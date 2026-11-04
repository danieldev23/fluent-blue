"""VideoPlayer: a themed player with transport controls, built on QtMultimedia."""
from __future__ import annotations

from pathlib import Path

from ...compatibility.qt import (
    MULTIMEDIA_AVAILABLE,
    QAudioOutput,
    QEvent,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QMediaPlayer,
    QSizePolicy,
    QStackedLayout,
    Qt,
    QUrl,
    QVBoxLayout,
    QVideoWidget,
    QWidget,
    Signal,
)
from ..base import ThemedMixin
from ..buttons.button import IconButton
from ..display.content import EmptyState
from ..display.text import Text
from ..selection.choice import Select
from ..selection.controls import Slider

SPEEDS = ((0.5, "0.5×"), (0.75, "0.75×"), (1.0, "1×"), (1.25, "1.25×"), (1.5, "1.5×"), (2.0, "2×"))
SEEK_STEP_MS = 5000


def format_time(milliseconds: int) -> str:
    """``m:ss``, or ``h:mm:ss`` from one hour up. Negative values read as zero."""
    seconds = max(0, int(milliseconds)) // 1000
    hours, rest = divmod(seconds, 3600)
    minutes, seconds = divmod(rest, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes}:{seconds:02d}"


class _SeekSlider(Slider):
    """A slider that jumps to the clicked position instead of paging towards it."""

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.button() == Qt.MouseButton.LeftButton and self.maximum() > self.minimum():
            fraction = min(1.0, max(0.0, event.position().x() / max(1, self.width())))
            self.setValue(self.minimum() + round(fraction * (self.maximum() - self.minimum())))
            self.sliderMoved.emit(self.value())
        super().mousePressEvent(event)


class VideoPlayer(ThemedMixin, QFrame):
    """A video player with play and pause, seeking, volume, speed and full screen.

    Keyboard, with the player focused: Space plays or pauses, Left and Right seek by five seconds, Up and
    Down change the volume, M mutes and F toggles full screen. Clicking the picture plays or pauses.

    Where QtMultimedia cannot be loaded, such as on a minimal Linux image without PulseAudio, the player
    shows an explanation and every method is a harmless no-op; check ``VideoPlayer.is_available()``.

    Args:
        source: A file path or URL to load.
        autoplay: Start playing as soon as the media is loaded.
        loop: Start again at the end.
        muted: Start muted.
        volume: Initial volume from 0 to 1.
        show_controls: Show the control bar.
        accessible_name: Name for assistive technology.

    Signals:
        position_changed(int): The playback position in milliseconds.
        duration_changed(int): The media length in milliseconds.
        state_changed(str): ``playing``, ``paused`` or ``stopped``.
        ended: Playback reached the end and did not loop.
        error_occurred(str): A readable description of why the media cannot play.
    """

    position_changed = Signal(int)
    duration_changed = Signal(int)
    state_changed = Signal(str)
    ended = Signal()
    error_occurred = Signal(str)

    def __init__(self, source: str | Path | QUrl | None = None, parent=None, *, autoplay: bool = False, loop: bool = False,
                 muted: bool = False, volume: float = 0.8, show_controls: bool = True, accessible_name: str = "Video player") -> None:
        super().__init__(parent)
        self._loop, self._autoplay = loop, autoplay
        self._source: QUrl | None = None
        self._error = ""
        self._seeking = False
        self._volume_before_mute = max(0.0, min(1.0, volume))
        self.setAccessibleName(accessible_name)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setProperty("fbComponent", "videoPlayer")
        self.setMinimumSize(320, 220)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        self.stage = QWidget()
        self.stage.setObjectName("videoStage")
        self._stack = QStackedLayout(self.stage)
        self._stack.setStackingMode(QStackedLayout.StackingMode.StackOne)
        self.empty = EmptyState("No video loaded", description="Choose a video file to start playing.", icon="play", action_text="Open video…")
        self.empty.action_clicked.connect(self.open_dialog)
        self._stack.addWidget(self.empty)
        column.addWidget(self.stage, 1)
        self.player = self.audio = self.video = None
        self.controls = self._build_controls()
        self.controls.setVisible(show_controls)
        column.addWidget(self.controls)
        self.bind_theme()
        if MULTIMEDIA_AVAILABLE:
            self._build_player(volume, muted)
        else:
            self._show_message("Video playback is unavailable", "QtMultimedia could not be loaded on this system.", "alert-triangle")
            for widget in self.controls.findChildren(QWidget):
                widget.setEnabled(False)
        if source is not None:
            self.set_source(source)

    # ---- availability -------------------------------------------------------------------------
    @staticmethod
    def is_available() -> bool:
        """Whether QtMultimedia loaded, so that media can actually play."""
        return MULTIMEDIA_AVAILABLE

    # ---- construction -------------------------------------------------------------------------
    def _build_player(self, volume: float, muted: bool) -> None:
        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.player.setAudioOutput(self.audio)
        self.video = QVideoWidget()
        self.video.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video.setMinimumHeight(120)
        self.video.installEventFilter(self)
        self.player.setVideoOutput(self.video)
        self._stack.addWidget(self.video)
        self.audio.setVolume(max(0.0, min(1.0, volume)))
        self.audio.setMuted(muted)
        # Use Qt's own looping. Restarting by hand inside the end-of-media callback re-enters the backend
        # and leaves it in a state where stop() blocks forever.
        self.set_loop(self._loop)
        self.player.positionChanged.connect(self._on_position)
        self.player.durationChanged.connect(self._on_duration)
        self.player.playbackStateChanged.connect(self._on_state)
        self.player.mediaStatusChanged.connect(self._on_status)
        self.player.errorOccurred.connect(self._on_error)
        self._sync_volume_controls()

    def _build_controls(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("videoControls")
        row = QHBoxLayout(bar)
        row.setContentsMargins(10, 6, 10, 6)
        row.setSpacing(8)
        self.play_button = IconButton("play", size="small", tooltip="Play", variant="primary")
        self.play_button.clicked.connect(self.toggle)
        self.time_label = Text("0:00", style="caption", color="text-secondary")
        self.time_label.setMinimumWidth(40)
        self.seek = _SeekSlider(0)
        self.seek.setRange(0, 0)
        self.seek.setAccessibleName("Seek")
        self.seek.sliderPressed.connect(lambda: setattr(self, "_seeking", True))
        self.seek.sliderReleased.connect(lambda: setattr(self, "_seeking", False))
        self.seek.sliderMoved.connect(self.seek_to)
        self.duration_label = Text("0:00", style="caption", color="text-secondary")
        self.duration_label.setMinimumWidth(40)
        self.mute_button = IconButton("volume", size="small", tooltip="Mute", variant="ghost")
        self.mute_button.clicked.connect(self.toggle_muted)
        self.volume_slider = Slider(80, minimum=0, maximum=100)
        self.volume_slider.setFixedWidth(72)
        self.volume_slider.setAccessibleName("Volume")
        self.volume_slider.valueChanged.connect(lambda value: self.set_volume(value / 100))
        self.speed = Select([(label, rate) for rate, label in SPEEDS], value=1.0, size="small")
        self.speed.setFixedWidth(84)
        self.speed.setAccessibleName("Playback speed")
        self.speed.value_changed.connect(self.set_speed)
        self.fullscreen_button = IconButton("maximize", size="small", tooltip="Full screen", variant="ghost")
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)
        for widget, stretch in ((self.play_button, 0), (self.time_label, 0), (self.seek, 1), (self.duration_label, 0),
                                (self.mute_button, 0), (self.volume_slider, 0), (self.speed, 0), (self.fullscreen_button, 0)):
            row.addWidget(widget, stretch)
        return bar

    # ---- public API ---------------------------------------------------------------------------
    def source(self) -> QUrl | None:
        return self._source

    def set_source(self, source: str | Path | QUrl) -> None:
        """Load a file path or URL. A path that does not exist reports ``error_occurred`` at once."""
        url = source if isinstance(source, QUrl) else (QUrl(str(source)) if "://" in str(source) else QUrl.fromLocalFile(str(Path(source).expanduser())))
        self._source = url
        self._error = ""
        self.seek.setRange(0, 0)
        self._update_times(0, 0)
        if self.player is None:
            return
        if url.isLocalFile() and not Path(url.toLocalFile()).is_file():
            self._fail(f"The file was not found: {url.toLocalFile()}")
            return
        self._stack.setCurrentWidget(self.video)
        self.player.setSource(url)
        if self._autoplay:
            self.player.play()

    def loop(self) -> bool:
        return self._loop

    def set_loop(self, loop: bool) -> None:
        """Start again at the end, or stop there."""
        self._loop = bool(loop)
        if self.player is not None:
            self.player.setLoops(QMediaPlayer.Loops.Infinite if self._loop else QMediaPlayer.Loops.Once)

    def open_dialog(self) -> None:
        """Ask for a video file with the native dialog and load it."""
        path, _ = QFileDialog.getOpenFileName(self, "Open video", "", "Video files (*.mp4 *.mov *.m4v *.mkv *.webm *.avi);;All files (*)")
        if path:
            self.set_source(path)

    def play(self) -> None:
        if self.player is not None and self._source is not None and not self._error:
            self.player.play()

    def pause(self) -> None:
        if self.player is not None:
            self.player.pause()

    def stop(self) -> None:
        if self.player is not None:
            self.player.stop()

    def toggle(self) -> None:
        """Play when paused or stopped, pause when playing."""
        if self.state() == "playing":
            self.pause()
        else:
            self.play()

    def state(self) -> str:
        """``playing``, ``paused`` or ``stopped``."""
        if self.player is None:
            return "stopped"
        return {QMediaPlayer.PlaybackState.PlayingState: "playing", QMediaPlayer.PlaybackState.PausedState: "paused"}.get(self.player.playbackState(), "stopped")

    def position(self) -> int:
        return int(self.player.position()) if self.player is not None else 0

    def duration(self) -> int:
        return int(self.player.duration()) if self.player is not None else 0

    def seek_to(self, milliseconds: int) -> None:
        """Move to a position in milliseconds, clamped to the media length."""
        if self.player is not None:
            self.player.setPosition(max(0, min(int(milliseconds), max(0, self.duration()))))

    def seek_by(self, milliseconds: int) -> None:
        self.seek_to(self.position() + milliseconds)

    def volume(self) -> float:
        return float(self.audio.volume()) if self.audio is not None else 0.0

    def set_volume(self, volume: float) -> None:
        """Set the volume from 0 to 1. Raising it above 0 unmutes."""
        if self.audio is None:
            return
        volume = max(0.0, min(1.0, float(volume)))
        self.audio.setVolume(volume)
        if volume > 0:
            self._volume_before_mute = volume
            self.audio.setMuted(False)
        self._sync_volume_controls()

    def is_muted(self) -> bool:
        return bool(self.audio is not None and (self.audio.isMuted() or self.audio.volume() == 0))

    def set_muted(self, muted: bool) -> None:
        if self.audio is None:
            return
        self.audio.setMuted(muted)
        if not muted and self.audio.volume() == 0:
            self.audio.setVolume(self._volume_before_mute or 0.5)
        self._sync_volume_controls()

    def toggle_muted(self) -> None:
        self.set_muted(not self.is_muted())

    def speed_rate(self) -> float:
        return float(self.player.playbackRate()) if self.player is not None else 1.0

    def set_speed(self, rate: float) -> None:
        """Set the playback rate, for example 1.5 for one and a half times speed."""
        if self.player is not None:
            self.player.setPlaybackRate(float(rate))

    def toggle_fullscreen(self) -> None:
        """Toggle native full screen on the picture. Esc or a double click leaves it."""
        if self.video is not None:
            self.video.setFullScreen(not self.video.isFullScreen())

    def error(self) -> str:
        """The last error message, or an empty string."""
        return self._error

    # ---- player events ------------------------------------------------------------------------
    def _on_position(self, position: int) -> None:
        self._update_times(int(position), self.duration())
        self.position_changed.emit(int(position))

    def _on_duration(self, duration: int) -> None:
        self.seek.setRange(0, max(0, int(duration)))
        self._update_times(self.position(), int(duration))
        self.duration_changed.emit(int(duration))

    def _on_state(self, _state) -> None:
        name = self.state()
        self.play_button.set_icon("pause" if name == "playing" else "play")
        self.play_button.setToolTip("Pause" if name == "playing" else "Play")
        self.play_button.setAccessibleName(self.play_button.toolTip())
        self.state_changed.emit(name)

    def _on_status(self, status) -> None:
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if not self._loop:
                self.ended.emit()
        elif status == QMediaPlayer.MediaStatus.InvalidMedia:
            self._fail("This file could not be played. The format may not be supported.")

    def _on_error(self, _error, message: str = "") -> None:
        if message:
            self._fail(message)

    def _fail(self, message: str) -> None:
        self._error = message
        self._show_message("This video cannot be played", message, "alert-circle")
        self.error_occurred.emit(message)

    def _show_message(self, title: str, description: str, icon: str) -> None:
        self.empty.title_label.setText(title)
        self.empty.description_label.setText(description)
        self.empty.description_label.setVisible(True)
        self.empty.action_button.setText("Choose another file…")
        self._stack.setCurrentWidget(self.empty)

    def _update_times(self, position: int, duration: int) -> None:
        self.time_label.setText(format_time(position))
        self.duration_label.setText(format_time(duration))
        if not self._seeking:
            self.seek.blockSignals(True)
            self.seek.setValue(min(max(0, position), self.seek.maximum()))
            self.seek.blockSignals(False)
        self.setAccessibleDescription(f"{format_time(position)} of {format_time(duration)}")

    def _sync_volume_controls(self) -> None:
        muted = self.is_muted()
        self.mute_button.set_icon("volume-off" if muted else "volume")
        self.mute_button.setToolTip("Unmute" if muted else "Mute")
        self.mute_button.setAccessibleName(self.mute_button.toolTip())
        self.volume_slider.blockSignals(True)
        self.volume_slider.setValue(0 if muted else round(self.volume() * 100))
        self.volume_slider.blockSignals(False)

    # ---- interaction --------------------------------------------------------------------------
    def eventFilter(self, watched, event) -> bool:  # noqa: N802 - Qt override
        if watched is self.video and event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
            self.setFocus()
            self.toggle()
        return False

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
        key = event.key()
        if key == Qt.Key.Key_Space:
            self.toggle()
        elif key == Qt.Key.Key_Left:
            self.seek_by(-SEEK_STEP_MS)
        elif key == Qt.Key.Key_Right:
            self.seek_by(SEEK_STEP_MS)
        elif key == Qt.Key.Key_Up:
            self.set_volume(self.volume() + 0.05)
        elif key == Qt.Key.Key_Down:
            self.set_volume(self.volume() - 0.05)
        elif key == Qt.Key.Key_M:
            self.toggle_muted()
        elif key == Qt.Key.Key_F:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)

    def release(self) -> None:
        """Pause and detach the media so that the backend lets go of the file and the audio device."""
        if self.player is not None:
            self.player.pause()
            self.player.setSource(QUrl())
            self._source = None

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt override
        self.release()
        super().closeEvent(event)

    def hideEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().hideEvent(event)
        self.pause()  # A hidden player must not keep playing sound.



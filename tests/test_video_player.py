"""VideoPlayer: the API and keyboard without media, and real playback when ffmpeg can make a clip."""
import shutil
import subprocess

import pytest

from fluent_blue import ThemeManager, VideoPlayer
from fluent_blue.compatibility.qt import MULTIMEDIA_AVAILABLE, Qt
from fluent_blue.components.advanced.video import format_time

needs_multimedia = pytest.mark.skipif(not MULTIMEDIA_AVAILABLE, reason="QtMultimedia is not available here")


@pytest.fixture(autouse=True)
def theme(qapp):
    ThemeManager.set_theme("light")


@pytest.fixture(scope="module")
def clip(tmp_path_factory):
    if shutil.which("ffmpeg") is None:
        pytest.skip("ffmpeg is needed to make a test clip")
    path = tmp_path_factory.mktemp("video") / "clip.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=duration=3:size=320x180:rate=15",
                    "-f", "lavfi", "-i", "sine=frequency=440:duration=3", "-pix_fmt", "yuv420p", "-shortest", str(path)], check=True)
    return path


@pytest.mark.parametrize(("milliseconds", "text"), [(0, "0:00"), (999, "0:00"), (65_000, "1:05"), (3_599_000, "59:59"), (3_600_000, "1:00:00"), (-5, "0:00")])
def test_format_time(milliseconds, text):
    assert format_time(milliseconds) == text


def test_player_builds_in_every_theme(qtbot):
    for theme in ("light", "dark", "high-contrast"):
        ThemeManager.set_theme(theme)
        player = VideoPlayer()
        qtbot.addWidget(player)
        player.show()
        assert not player.grab().isNull()


def test_availability_flag_matches_the_binding():
    assert VideoPlayer.is_available() is MULTIMEDIA_AVAILABLE


def test_empty_player_is_safe_to_drive(qtbot):
    player = VideoPlayer()
    qtbot.addWidget(player)
    player.show()
    for call in (player.play, player.pause, player.stop, player.toggle, player.toggle_muted):
        call()
    player.seek_to(5000)
    assert player.state() == "stopped" and player.position() == 0 and player.source() is None


@needs_multimedia
def test_missing_file_reports_an_error(qtbot, tmp_path):
    player = VideoPlayer()
    qtbot.addWidget(player)
    with qtbot.waitSignal(player.error_occurred, timeout=2000) as seen:
        player.set_source(tmp_path / "nope.mp4")
    assert "nope.mp4" in seen.args[0] and player.error() == seen.args[0]
    player.play()
    assert player.state() == "stopped"


@needs_multimedia
def test_volume_mute_and_speed(qtbot):
    player = VideoPlayer(volume=0.5)
    qtbot.addWidget(player)
    assert player.volume() == pytest.approx(0.5)
    player.set_volume(2)
    assert player.volume() == 1.0
    player.set_muted(True)
    assert player.is_muted() and player.mute_button.toolTip() == "Unmute"
    player.set_volume(0.3)
    assert not player.is_muted()
    player.set_volume(0)
    assert player.is_muted()
    player.set_muted(False)
    assert not player.is_muted() and player.volume() > 0
    player.set_speed(1.5)
    assert player.speed_rate() == pytest.approx(1.5)


@needs_multimedia
def test_keyboard_volume_and_mute(qtbot):
    player = VideoPlayer(volume=0.5)
    qtbot.addWidget(player)
    player.show()
    qtbot.keyClick(player, Qt.Key.Key_Up)
    assert player.volume() == pytest.approx(0.55)
    qtbot.keyClick(player, Qt.Key.Key_Down)
    qtbot.keyClick(player, Qt.Key.Key_Down)
    assert player.volume() == pytest.approx(0.45)
    qtbot.keyClick(player, Qt.Key.Key_M)
    assert player.is_muted()
    qtbot.keyClick(player, Qt.Key.Key_M)
    assert not player.is_muted()


@needs_multimedia
def test_plays_seeks_and_ends(qtbot, clip):
    player = VideoPlayer(clip)
    qtbot.addWidget(player)
    player.show()
    qtbot.waitUntil(lambda: player.duration() > 0, timeout=8000)
    assert 2500 <= player.duration() <= 3500 and player.duration_label.text() == "0:03"
    with qtbot.waitSignal(player.state_changed, timeout=3000):
        player.play()
    assert player.state() == "playing" and player.play_button.toolTip() == "Pause"
    qtbot.waitUntil(lambda: player.position() > 100, timeout=5000)
    player.pause()
    assert player.state() == "paused" and player.play_button.toolTip() == "Play"
    player.seek_to(1500)
    qtbot.waitUntil(lambda: abs(player.position() - 1500) < 300, timeout=3000)
    player.seek_to(10**9)
    assert player.position() <= player.duration()
    qtbot.keyClick(player, Qt.Key.Key_Space)
    assert player.state() == "playing"
    with qtbot.waitSignal(player.ended, timeout=8000):
        player.seek_to(player.duration() - 200)
    qtbot.keyClick(player, Qt.Key.Key_Left)  # Seeking after the end must not raise.


@needs_multimedia
def test_video_frames_are_decoded_at_the_right_size(qtbot, clip):
    """Screenshots cannot show video (the picture is drawn by a native sink), so check the decoded frames."""
    player = VideoPlayer(clip)
    qtbot.addWidget(player)
    player.show()
    frames = []
    player.video.videoSink().videoFrameChanged.connect(lambda frame: frames.append((frame.isValid(), frame.width(), frame.height())))
    qtbot.waitUntil(lambda: player.duration() > 0, timeout=8000)
    player.play()
    qtbot.waitUntil(lambda: any(valid for valid, _w, _h in frames), timeout=8000)
    assert (True, 320, 180) in frames
    player.pause()


@needs_multimedia
def test_hiding_pauses_playback(qtbot, clip):
    player = VideoPlayer(clip, autoplay=True)
    qtbot.addWidget(player)
    player.show()
    qtbot.waitUntil(lambda: player.state() == "playing", timeout=8000)
    player.hide()
    qtbot.waitUntil(lambda: player.state() == "paused", timeout=3000)


@needs_multimedia
def test_loop_restarts_at_the_end(qtbot, clip):
    player = VideoPlayer(clip, loop=True)
    qtbot.addWidget(player)
    player.show()
    qtbot.waitUntil(lambda: player.duration() > 0, timeout=8000)
    player.play()
    player.seek_to(player.duration() - 150)
    qtbot.waitUntil(lambda: player.state() == "playing" and player.position() < 1000 and player.position() >= 0, timeout=8000)
    assert player.state() == "playing"


def test_fallback_when_multimedia_cannot_load(qtbot, monkeypatch):
    """Forces the minimal-Linux path on every machine: no QtMultimedia, so no player, but a usable widget."""
    monkeypatch.setattr("fluent_blue.components.advanced.video.MULTIMEDIA_AVAILABLE", False)
    player = VideoPlayer("clip.mp4")
    qtbot.addWidget(player)
    player.show()
    assert player.player is None and player.video is None
    assert player.empty.title_label.text() == "Video playback is unavailable"
    assert not player.play_button.isEnabled() and not player.seek.isEnabled()
    for call in (player.play, player.pause, player.stop, player.toggle, player.toggle_fullscreen, player.release):
        call()
    player.seek_to(100)
    player.set_volume(0.2)
    player.set_loop(True)
    qtbot.keyClick(player, Qt.Key.Key_Space)
    assert player.state() == "stopped" and player.volume() == 0.0 and player.loop() is True

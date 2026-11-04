"""Behaviour, keyboard and signal tests for Rating, RangeSlider, Accordion, Carousel and Kbd."""
import pytest

from fluent_blue import Accordion, Carousel, Kbd, RangeSlider, Rating, Text, ThemeManager
from fluent_blue.compatibility.qt import QPoint, Qt


@pytest.fixture(autouse=True)
def theme(qapp):
    ThemeManager.set_theme("light")


def key(qtbot, widget, k):
    qtbot.keyClick(widget, k)


# ---- Rating -------------------------------------------------------------------------------------
def test_rating_set_value_clamps_snaps_and_signals(qtbot):
    rating = Rating(0, allow_half=True)
    qtbot.addWidget(rating)
    with qtbot.waitSignal(rating.value_changed) as seen:
        rating.set_value(3.3)
    assert seen.args == [3.5] and rating.value() == 3.5
    rating.set_value(99)
    assert rating.value() == 5
    rating.set_value(-4)
    assert rating.value() == 0


def test_rating_does_not_emit_when_unchanged(qtbot):
    rating = Rating(2)
    qtbot.addWidget(rating)
    with qtbot.assertNotEmitted(rating.value_changed):
        rating.set_value(2)


def test_rating_click_sets_and_second_click_clears(qtbot):
    rating = Rating(0)
    qtbot.addWidget(rating)
    rating.show()
    target = QPoint(2 + 2 * (rating._size + rating.GAP) + rating._size // 2, rating.height() // 2)
    qtbot.mouseClick(rating, Qt.MouseButton.LeftButton, pos=target)
    assert rating.value() == 3
    qtbot.mouseClick(rating, Qt.MouseButton.LeftButton, pos=target)
    assert rating.value() == 0


def test_rating_allow_clear_false_keeps_value(qtbot):
    rating = Rating(0, allow_clear=False)
    qtbot.addWidget(rating)
    rating.show()
    target = QPoint(2 + rating._size // 2, rating.height() // 2)
    qtbot.mouseClick(rating, Qt.MouseButton.LeftButton, pos=target)
    qtbot.mouseClick(rating, Qt.MouseButton.LeftButton, pos=target)
    assert rating.value() == 1


def test_rating_keyboard(qtbot):
    rating = Rating(2)
    qtbot.addWidget(rating)
    rating.show()
    key(qtbot, rating, Qt.Key.Key_Right)
    assert rating.value() == 3
    key(qtbot, rating, Qt.Key.Key_Left)
    key(qtbot, rating, Qt.Key.Key_Left)
    assert rating.value() == 1
    key(qtbot, rating, Qt.Key.Key_End)
    assert rating.value() == 5
    key(qtbot, rating, Qt.Key.Key_Home)
    assert rating.value() == 0


def test_rating_read_only_ignores_input_and_focus(qtbot):
    rating = Rating(4, read_only=True)
    qtbot.addWidget(rating)
    rating.show()
    qtbot.mouseClick(rating, Qt.MouseButton.LeftButton, pos=QPoint(5, 5))
    key(qtbot, rating, Qt.Key.Key_Right)
    assert rating.value() == 4
    assert rating.focusPolicy() == Qt.FocusPolicy.NoFocus


def test_rating_accessibility(qtbot):
    rating = Rating(3)
    qtbot.addWidget(rating)
    assert rating.accessibleName() == "Rating" and rating.accessibleDescription() == "3 of 5"


# ---- RangeSlider --------------------------------------------------------------------------------
def test_range_orders_and_snaps(qtbot):
    slider = RangeSlider(0, 100, minimum=0, maximum=100, step=10)
    qtbot.addWidget(slider)
    with qtbot.waitSignal(slider.range_changed) as seen:
        slider.set_range(87, 23)
    assert seen.args == [20, 90]


def test_range_validates_bounds():
    with pytest.raises(ValueError):
        RangeSlider(0, 1, minimum=5, maximum=5)


def test_range_keyboard_moves_the_active_handle_only(qtbot):
    slider = RangeSlider(20, 80)
    qtbot.addWidget(slider)
    slider.show()
    key(qtbot, slider, Qt.Key.Key_Right)  # The upper handle is active first.
    assert (slider.low(), slider.high()) == (20, 81)
    key(qtbot, slider, Qt.Key.Key_Down)
    key(qtbot, slider, Qt.Key.Key_Left)
    assert (slider.low(), slider.high()) == (19, 81)
    key(qtbot, slider, Qt.Key.Key_Home)
    assert slider.low() == 0
    key(qtbot, slider, Qt.Key.Key_Up)
    key(qtbot, slider, Qt.Key.Key_End)
    assert slider.high() == 100


def test_range_handles_cannot_cross(qtbot):
    slider = RangeSlider(40, 50)
    qtbot.addWidget(slider)
    slider.show()
    key(qtbot, slider, Qt.Key.Key_Down)
    for _ in range(30):
        key(qtbot, slider, Qt.Key.Key_Right)
    assert slider.low() == slider.high() == 50


def test_range_mouse_picks_nearer_handle(qtbot):
    slider = RangeSlider(20, 80)
    qtbot.addWidget(slider)
    slider.resize(300, 28)
    slider.show()
    qtbot.mouseClick(slider, Qt.MouseButton.LeftButton, pos=QPoint(int(slider._x(10)), 14))
    assert slider.low() == 10 and slider.high() == 80
    qtbot.mouseClick(slider, Qt.MouseButton.LeftButton, pos=QPoint(int(slider._x(95)), 14))
    assert slider.high() == 95


# ---- Accordion ----------------------------------------------------------------------------------
def build_accordion(qtbot, **kwargs):
    accordion = Accordion(**kwargs)
    qtbot.addWidget(accordion)
    for number in range(3):
        accordion.add_item(f"Item {number}", f"Body {number}")
    accordion.show()
    return accordion


def test_accordion_non_exclusive_allows_many_open(qtbot):
    accordion = build_accordion(qtbot)
    accordion.set_expanded(0, True)
    accordion.set_expanded(2, True)
    assert [accordion.is_expanded(i) for i in range(3)] == [True, False, True]
    accordion.collapse_all()
    assert not any(accordion.is_expanded(i) for i in range(3))
    accordion.expand_all()
    assert all(accordion.is_expanded(i) for i in range(3))


def test_accordion_exclusive_keeps_one_open_and_reports_both_changes(qtbot):
    accordion = build_accordion(qtbot, exclusive=True)
    events = []
    accordion.expanded_changed.connect(lambda index, on: events.append((index, on)))
    accordion.set_expanded(0, True)
    accordion.set_expanded(1, True)
    assert [accordion.is_expanded(i) for i in range(3)] == [False, True, False]
    assert (0, True) in events and (0, False) in events and (1, True) in events
    accordion.expand_all()  # Ignored in exclusive mode.
    assert sum(accordion.is_expanded(i) for i in range(3)) == 1


def test_accordion_initial_expanded_in_exclusive_mode(qtbot):
    accordion = Accordion(exclusive=True)
    qtbot.addWidget(accordion)
    accordion.add_item("A", "a", expanded=True)
    accordion.add_item("B", "b", expanded=True)
    assert [accordion.is_expanded(i) for i in range(2)] == [False, True]


def test_accordion_accepts_widgets(qtbot):
    accordion = Accordion()
    qtbot.addWidget(accordion)
    body = Text("custom")
    panel = accordion.add_item("Title", body)
    assert body.parentWidget() is not None and panel.is_expanded() is False


# ---- Carousel -----------------------------------------------------------------------------------
def build_carousel(qtbot, count=3, **kwargs):
    carousel = Carousel(**kwargs)
    qtbot.addWidget(carousel)
    for number in range(count):
        carousel.add_slide(Text(f"Slide {number}"))
    carousel.show()
    qtbot.waitExposed(carousel)
    return carousel


def test_carousel_navigation_wraps_with_loop(qtbot):
    carousel = build_carousel(qtbot)
    seen = []
    carousel.current_changed.connect(seen.append)
    carousel.next()
    carousel.next()
    carousel.next()
    assert carousel.current() == 0 and seen == [1, 2, 0]
    carousel.previous()
    assert carousel.current() == 2


def test_carousel_without_loop_stops_at_ends(qtbot):
    carousel = build_carousel(qtbot, loop=False)
    assert not carousel.previous_button.isEnabled() and carousel.next_button.isEnabled()
    carousel.set_current(99)
    assert carousel.current() == 2 and not carousel.next_button.isEnabled()
    carousel.next()
    assert carousel.current() == 2


def test_carousel_keyboard_and_dots(qtbot):
    carousel = build_carousel(qtbot)
    carousel.setFocus()
    key(qtbot, carousel, Qt.Key.Key_Right)
    assert carousel.current() == 1
    key(qtbot, carousel, Qt.Key.Key_Left)
    assert carousel.current() == 0
    carousel.dots.clicked.emit(2)
    assert carousel.current() == 2


def test_carousel_accessibility_text(qtbot):
    carousel = build_carousel(qtbot)
    assert carousel.accessibleDescription() == "Slide 1 of 3"
    carousel.next()
    assert carousel.accessibleDescription() == "Slide 2 of 3"


def pointer(carousel, inside: bool) -> None:
    """Simulate the pointer entering or leaving.

    The headless platform queues its own Enter event when a window is shown, and it arrives later, so
    pending events are flushed first. Qt 6 passes a ``QEnterEvent`` to ``enterEvent``.
    """
    from fluent_blue.compatibility.qt import QApplication, QEnterEvent, QEvent, QPointF

    QApplication.processEvents()
    if inside:
        centre = QPointF(carousel.rect().center())
        carousel.enterEvent(QEnterEvent(centre, centre, centre))
    else:
        carousel.leaveEvent(QEvent(QEvent.Type.Leave))


def test_carousel_autoplay_advances_when_the_pointer_is_away(qtbot):
    carousel = build_carousel(qtbot, autoplay_ms=40)
    pointer(carousel, inside=False)
    assert carousel.is_playing()
    qtbot.waitUntil(lambda: carousel.current() >= 1, timeout=3000)


def test_carousel_autoplay_pauses_on_hover_focus_and_hide(qtbot):
    carousel = build_carousel(qtbot, autoplay_ms=40)
    pointer(carousel, inside=False)
    assert carousel.is_playing()
    pointer(carousel, inside=True)
    assert not carousel.is_playing()
    pointer(carousel, inside=False)
    assert carousel.is_playing()
    carousel.setFocus()
    assert not carousel.is_playing()
    carousel.clearFocus()
    carousel.hide()
    assert not carousel.is_playing()
    carousel.show()
    pointer(carousel, inside=False)
    assert carousel.is_playing()


def test_carousel_autoplay_can_be_turned_off(qtbot):
    carousel = build_carousel(qtbot, autoplay_ms=40)
    pointer(carousel, inside=False)
    carousel.set_autoplay(0)
    assert not carousel.is_playing()


def test_carousel_single_slide_never_autoplays(qtbot):
    carousel = build_carousel(qtbot, count=1, autoplay_ms=50)
    assert not carousel.is_playing()
    assert not carousel.next_button.isEnabled()


def test_carousel_empty_is_safe(qtbot):
    carousel = Carousel()
    qtbot.addWidget(carousel)
    carousel.next()
    carousel.set_current(3)
    assert carousel.count() == 0


# ---- Kbd ----------------------------------------------------------------------------------------
def test_kbd_parses_and_names_keys(qtbot):
    kbd = Kbd("Ctrl + Shift+P")
    qtbot.addWidget(kbd)
    assert kbd.keys() == ["Ctrl", "Shift", "P"]
    assert kbd.accessibleName() == "Keyboard shortcut Ctrl Shift P"
    kbd.set_keys(["Cmd", "K"])
    assert kbd.keys() == ["Cmd", "K"]


def test_kbd_width_grows_with_keys(qtbot):
    one, three = Kbd("K"), Kbd("Ctrl+Shift+K")
    qtbot.addWidget(one)
    qtbot.addWidget(three)
    assert three.sizeHint().width() > one.sizeHint().width()


def test_kbd_rejects_unknown_size():
    with pytest.raises(ValueError):
        Kbd("K", size="huge")


@pytest.mark.parametrize("theme", ["light", "dark", "high-contrast"])
def test_new_components_render_in_every_theme(qtbot, theme):
    ThemeManager.set_theme(theme)
    widgets = [Rating(3.5, allow_half=True), RangeSlider(), Kbd("Ctrl+K"), Rating(2, disabled=True), RangeSlider(disabled=True)]
    for widget in widgets:
        qtbot.addWidget(widget)
        widget.show()
        assert not widget.grab().isNull()

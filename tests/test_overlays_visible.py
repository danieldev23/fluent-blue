"""Toasts, notifications and snackbars are painted where people look, and stack without clipping."""
import pytest

from fluent_blue import EmptyState, Notification, Result, Snackbar, ThemeManager, Toast
from fluent_blue.compatibility.qt import QLabel, QVBoxLayout, QWidget
from fluent_blue.studio.app import StudioWindow


@pytest.fixture(params=["plain", "studio"])
def window(qtbot, request):
    ThemeManager.set_theme("light")
    if request.param == "plain":
        win = QWidget()
        QVBoxLayout(win).addWidget(QLabel("content"))
    else:
        win = StudioWindow()
    qtbot.addWidget(win)
    win.resize(1100, 700)
    win.show()
    qtbot.waitExposed(win)
    return win


def _painted_colors(window, card) -> int:
    image = window.grab().toImage()
    origin = card.mapTo(window, card.rect().topLeft())
    colors = set()
    for y in range(origin.y() + 2, origin.y() + card.height() - 2, 2):
        for x in range(origin.x() + 2, origin.x() + card.width() - 2, 2):
            colors.add(image.pixelColor(x, y).name())
    return len(colors)


def _fully_visible(window, card) -> bool:
    if not card.isVisible() or card.height() < card.layout().totalHeightForWidth(card.width()):
        return False
    if card.visibleRegion().boundingRect().size() != card.size():
        return False
    center = card.mapTo(window, card.rect().center())
    hit = window.childAt(center)
    while hit is not None and hit is not card:
        hit = hit.parentWidget()
    return hit is card


def test_toast_is_painted_on_top(qtbot, window):
    card = Toast.show("Saved successfully", parent=window, variant="success", duration=0)
    qtbot.wait(250)
    assert _fully_visible(window, card)
    assert _painted_colors(window, card) >= 3  # surface, border or text, and the icon
    assert card.mapTo(window, card.rect().topRight()).x() <= window.width()


def test_three_messages_stack_without_clipping(qtbot, window):
    cards = [
        Toast.show("First", parent=window, duration=0),
        Toast.show("A second toast with a longer message that wraps onto two lines", parent=window, variant="warning", duration=0),
        Notification.show("Export finished", "Your report is ready.", parent=window, variant="success", action_text="Open"),
    ]
    qtbot.wait(300)
    for card in cards:
        assert _fully_visible(window, card), card.message_label.text()
    rects = [card.geometry() for card in cards]
    for index, rect in enumerate(rects):
        for other in rects[index + 1:]:
            assert not rect.intersects(other)
    cards[1].dismiss()
    qtbot.wait(300)
    assert _fully_visible(window, cards[0]) and _fully_visible(window, cards[2])


def test_snackbar_sits_at_bottom_center(qtbot, window):
    card = Snackbar.show("Item archived", parent=window, action_text="Undo", duration=0)
    qtbot.wait(250)
    assert _fully_visible(window, card)
    bottom = card.mapTo(window, card.rect().bottomLeft()).y()
    assert window.height() - 40 <= bottom <= window.height()
    center = card.mapTo(window, card.rect().center()).x()
    assert abs(center - window.width() // 2) <= 2


@pytest.mark.parametrize("width", [220, 300, 420, 700, 1000])
def test_empty_state_never_overlaps(qtbot, width):
    # A scroll area, because the offscreen platform clamps windows to its 800x600 screen.
    from fluent_blue import ScrollArea

    content = QWidget()
    host = ScrollArea(content)
    qtbot.addWidget(host)
    layout = QVBoxLayout(content)
    states = [
        EmptyState("No projects yet", description="Projects keep your palettes and tokens together. Create one to get started.", action_text="Create"),
        Result("error", "Sync failed", description="We could not reach the server, which may be offline.", action_text="Try again"),
    ]
    for state in states:
        layout.addWidget(state)
    host.resize(width, 500)
    host.show()
    qtbot.waitExposed(host)
    qtbot.wait(50)  # Minimum heights set during resize take one more layout pass.
    for state in states:
        order = [state.emblem, state.title_label, state.description_label, state.action_button]
        for above, below in zip(order, order[1:]):
            assert above.geometry().bottom() < below.geometry().top(), f"{width}px: {type(state).__name__}"
        assert state.description_label.height() >= state.description_label.heightForWidth(state.description_label.width())
        assert state.height() >= state.minimumHeight() >= state.action_button.geometry().bottom()

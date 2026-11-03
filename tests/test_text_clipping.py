"""Regression: wrapped text in feedback components must never be clipped."""
import pytest

from fluent_blue import Alert, ToastCard
from fluent_blue.compatibility.qt import QLabel, QVBoxLayout, QWidget

LONG = "Operation completed successfully and everything was saved to the server."


def _assert_fits(host, qtbot):
    host.show()
    qtbot.waitExposed(host)
    for label in host.findChildren(QLabel):
        if label.wordWrap() and label.isVisible() and label.text():
            needed = label.heightForWidth(label.width())
            assert label.height() >= needed, f"{label.text()!r}: {label.height()} < {needed}"


@pytest.mark.parametrize("width", [180, 240, 320, 600])
@pytest.mark.parametrize("dense", [False, True])
def test_alert_message_is_not_clipped(qtbot, width, dense):
    host = QWidget()
    qtbot.addWidget(host)
    layout = QVBoxLayout(host)
    for variant in ("info", "success", "warning", "error"):
        layout.addWidget(Alert(message=LONG, variant=variant, closable=True, dense=dense))
    layout.addStretch(1)
    host.resize(width, 640)
    _assert_fits(host, qtbot)


@pytest.mark.parametrize("width", [260, 400])
def test_toast_message_is_not_clipped(qtbot, width):
    host = QWidget()
    qtbot.addWidget(host)
    layout = QVBoxLayout(host)
    layout.addWidget(ToastCard(message=LONG, variant="success", duration=0))
    layout.addStretch(1)
    host.resize(width, 400)
    _assert_fits(host, qtbot)

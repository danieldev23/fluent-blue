"""Use the real Studio the way a person would, and fail on any exception or stuck overlay."""
import sys

import pytest

from fluent_blue import Tabs, ThemeManager
from fluent_blue.compatibility.qt import (
    QAbstractButton,
    QApplication,
    QFileDialog,
    QInputDialog,
    QLineEdit,
    Qt,
    QWidget,
    delete_now,
)
from fluent_blue.studio import catalog
from fluent_blue.studio.app import StudioWindow
from fluent_blue.studio.pages.components import ComponentGroupPage

PAGES = ("Overview", "Foundations", "Colors", "Typography", "Icons", *catalog.GROUPS, "Themes", "Playground", "About", "Changelog")


@pytest.fixture
def window(qtbot, monkeypatch):
    # Native dialogs block forever without a person, so answer them as "cancelled".
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: ("", ""))
    monkeypatch.setattr(QFileDialog, "getOpenFileNames", lambda *a, **k: ([], ""))
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: ("", ""))
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: "")
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("", False))
    ThemeManager.set_theme("light")
    errors = []
    previous, sys.excepthook = sys.excepthook, lambda kind, value, tb: errors.append(f"{kind.__name__}: {value}")
    win = StudioWindow()
    win.resize(1536, 1024)
    win.show()
    qtbot.waitExposed(win)
    win.errors = errors
    yield win
    sys.excepthook = previous
    ThemeManager.set_theme("light")
    for widget in QApplication.topLevelWidgets():
        if widget is not win and widget.isVisible():
            widget.close()
    win.close()
    delete_now(win)
    QApplication.processEvents()
    assert errors == []


def _close_transients(app, window):
    for widget in QApplication.topLevelWidgets():
        if widget is not window and widget.isVisible():
            widget.close()
    for widget in window.findChildren(QWidget):
        if type(widget).__name__ == "Drawer" and widget.is_open():
            widget.close_drawer()
    app.processEvents()


@pytest.mark.parametrize("name", PAGES)
def test_click_everything_on_page(window, qtbot, qapp, name):
    window.navigate(name)
    page = window.stack.currentWidget()
    if hasattr(page, "ensure_built"):
        page.ensure_built()
    qapp.processEvents()
    buttons = [b for b in page.findChildren(QAbstractButton) if b.isVisible() and b.isEnabled() and not isinstance(b.parentWidget(), QLineEdit)]
    assert buttons or name in ("Typography", "About", "Changelog", "Colors", "Icons")
    alive = list(buttons)
    for button in alive:
        try:
            if not button.isVisible():
                continue
        except RuntimeError:
            continue  # Removed by an earlier click, such as a dismissed alert.
        if button.text() in ("Back to light", "Apply custom theme", "Use theme"):
            continue
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        _close_transients(qapp, window)
    assert window.errors == []


@pytest.mark.parametrize("group", catalog.GROUPS)
def test_every_docs_tab_opens(window, qapp, group):
    window.navigate(group)
    page = window.stack.currentWidget()
    assert isinstance(page, ComponentGroupPage)
    page.ensure_built()
    for section in page.sections.values():
        tabs = section.findChildren(Tabs, options=Qt.FindChildOption.FindDirectChildrenOnly)[-1]
        for index in range(tabs.count()):
            tabs.setCurrentIndex(index)
            qapp.processEvents()
            assert tabs.currentWidget().layout().count() == 1
    assert window.errors == []


def test_theme_switch_with_overlays_open(window, qapp):
    from fluent_blue import Drawer, Modal, Notification, Snackbar, Toast

    Toast.show("Saved", parent=window, duration=0)
    Notification.show("Done", "Body", parent=window)
    Snackbar.show("Archived", parent=window, action_text="Undo", duration=0)
    drawer = Drawer(window, title="Edit")
    drawer.open_drawer()
    modal = Modal(window, title="Title", content="Body")
    modal.show()
    qapp.processEvents()
    for theme in ("dark", "high-contrast", "light"):
        ThemeManager.set_theme(theme)
        qapp.processEvents()
    modal.reject()
    drawer.close_drawer()
    qapp.processEvents()
    assert window.errors == []


def test_rapid_theme_switching_and_navigation(window, qapp):
    for index in range(12):
        ThemeManager.toggle()
        window.navigate(PAGES[index % len(PAGES)])
        qapp.processEvents()
    assert window.errors == []
    assert len(window.pages) <= 6


def test_command_palette_reaches_a_component(window, qapp):
    window.palette_widget.run("component:Inputs:TextArea")
    qapp.processEvents()
    assert window.sidebar.current() == "Inputs"
    assert "TextArea" in window.pages["Inputs"].sections


def test_theme_switch_is_fast_with_many_pages_visited(window, qapp):
    import time

    for name in catalog.GROUPS:
        window.navigate(name)
        window.stack.currentWidget().ensure_built()
    window.navigate("Overview")
    qapp.processEvents()
    start = time.perf_counter()
    ThemeManager.toggle()
    qapp.processEvents()
    assert (time.perf_counter() - start) < 1.0
    assert len(window.findChildren(QWidget)) < 4000




def test_repeated_dialogs_and_menus_do_not_accumulate(window, qapp):
    from fluent_blue import Button, Modal

    host = Button("Open", window)
    def live_modals():
        return len(window.findChildren(Modal))

    for _ in range(5):
        modal = Modal(host, title="T", content="Body")
        modal.finished.connect(modal.deleteLater)
        modal.show()
        qapp.processEvents()
        modal.reject()
        qapp.processEvents()
        QApplication.sendPostedEvents(None, 52)  # QEvent.DeferredDelete
    assert live_modals() == 0


def test_table_keeps_given_row_order_until_sorted(qtbot):
    from fluent_blue import DataTable

    rows = [{"id": n} for n in (2, 3, 1)]
    table = DataTable(["id"], rows, page_size=None)
    qtbot.addWidget(table)
    assert [table.model.index(i, 0).data() for i in range(3)] == ["2", "3", "1"]
    table.sort_by("id")
    assert [table.model.index(i, 0).data() for i in range(3)] == ["1", "2", "3"]

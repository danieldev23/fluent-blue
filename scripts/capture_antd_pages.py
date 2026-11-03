import sys
sys.path.insert(0, "/Users/dangquochuy/Documents/Projects/FluentBlue-PyQT6")

from fluent_blue.compatibility.qt import QApplication, QTimer
from fluent_blue.studio.app import StudioWindow
from fluent_blue.core.theme_manager import ThemeManager
from fluent_blue.components.feedback import MessageDialog

app = QApplication(sys.argv)
ThemeManager.set_theme("light")

win = StudioWindow()
win.resize(1300, 900)
win.show()

out_dir = "/Users/dangquochuy/.gemini/antigravity/brain/8a688404-0db4-4b19-bef0-38b1f35856af"

def step_buttons():
    win.navigate("Buttons")
    QTimer.singleShot(600, snap_buttons)

def snap_buttons():
    win.grab().save(f"{out_dir}/antd_buttons_light.png", "PNG")
    win.navigate("Colors")
    QTimer.singleShot(600, snap_colors)

def snap_colors():
    win.grab().save(f"{out_dir}/antd_colors_light.png", "PNG")
    ThemeManager.set_theme("dark")
    win.navigate("Buttons")
    QTimer.singleShot(600, snap_buttons_dark)

def snap_buttons_dark():
    win.grab().save(f"{out_dir}/antd_buttons_dark.png", "PNG")
    win.navigate("Overview")
    QTimer.singleShot(600, snap_overview_dark)

def snap_overview_dark():
    win.grab().save(f"{out_dir}/antd_overview_dark.png", "PNG")
    # Now snap dialogs
    ThemeManager.set_theme("light")
    dlg_light = MessageDialog(None, title="Update installed", message="Restart the app to finish.", variant="success", buttons=("Later", "Restart"))
    dlg_light.show()
    QTimer.singleShot(400, lambda: [dlg_light.grab().save(f"{out_dir}/antd_dialog_light.png", "PNG"), dlg_light.close(), snap_dlg_dark()])

def snap_dlg_dark():
    ThemeManager.set_theme("dark")
    dlg_dark = MessageDialog(None, title="Update installed", message="Restart the app to finish.", variant="success", buttons=("Later", "Restart"))
    dlg_dark.show()
    QTimer.singleShot(400, lambda: [dlg_dark.grab().save(f"{out_dir}/antd_dialog_dark.png", "PNG"), dlg_dark.close(), app.quit()])

QTimer.singleShot(800, step_buttons)
app.exec()
print("All Ant Design snapshots completed successfully!")


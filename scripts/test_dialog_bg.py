import sys
sys.path.insert(0, "/Users/dangquochuy/Documents/Projects/FluentBlue-PyQT6")

from fluent_blue.compatibility.qt import QApplication, QTimer, Qt
from fluent_blue.components.feedback import MessageDialog
from fluent_blue.core.theme_manager import ThemeManager

app = QApplication(sys.argv)
ThemeManager.set_theme("light")

dlg = MessageDialog(None, title="Update installed", message="Restart the app to finish.", variant="success", buttons=("Later", "Restart"))
dlg.show()

def snap():
    pixmap = dlg.grab()
    out = "/Users/dangquochuy/.gemini/antigravity/brain/8a688404-0db4-4b19-bef0-38b1f35856af/test_dialog_before.png"
    pixmap.save(out, "PNG")
    print(f"Margin: {dlg.MARGIN}, Dialog rect: {dlg.rect()}, Panel rect: {dlg.panel.rect()}")
    print("Saved snap:", out)
    app.quit()

QTimer.singleShot(500, snap)
app.exec()

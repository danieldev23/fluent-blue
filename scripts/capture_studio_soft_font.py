import sys
sys.path.insert(0, "/Users/dangquochuy/Documents/Projects/FluentBlue-PyQT6")

from fluent_blue.compatibility.qt import QApplication, QTimer
from fluent_blue.studio.app import StudioWindow
from fluent_blue.core.theme_manager import ThemeManager

app = QApplication(sys.argv)
ThemeManager.set_theme("light")
win = StudioWindow()
win.resize(1300, 850)
win.show()

win.navigate("Overview")

def snap():
    pixmap = win.grab()
    out = "/Users/dangquochuy/.gemini/antigravity/brain/8a688404-0db4-4b19-bef0-38b1f35856af/studio_soft_font.png"
    pixmap.save(out, "PNG")
    print("Saved snap:", out)
    app.quit()

QTimer.singleShot(800, snap)
app.exec()

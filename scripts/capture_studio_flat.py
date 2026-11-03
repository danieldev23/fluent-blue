import sys
import os

sys.path.insert(0, "/Users/dangquochuy/Documents/Projects/FluentBlue-PyQT6")

from fluent_blue.compatibility.qt import QApplication, QTimer
from fluent_blue.studio.app import StudioWindow
from fluent_blue.core.theme_manager import ThemeManager

app = QApplication(sys.argv)
ThemeManager.set_theme("light")
win = StudioWindow()
win.resize(1300, 850)
win.show()

# Switch to Overview
win.navigate("Overview")

def take_flat_overview():
    pixmap = win.grab()
    out_path = "/Users/dangquochuy/.gemini/antigravity/brain/8a688404-0db4-4b19-bef0-38b1f35856af/studio_flat_overview.png"
    pixmap.save(out_path, "PNG")
    print(f"[+] Saved flat overview: {out_path}")
    
    win.navigate("Buttons")
    QTimer.singleShot(600, take_flat_buttons)

def take_flat_buttons():
    pixmap = win.grab()
    out_path = "/Users/dangquochuy/.gemini/antigravity/brain/8a688404-0db4-4b19-bef0-38b1f35856af/studio_flat_buttons.png"
    pixmap.save(out_path, "PNG")
    print(f"[+] Saved flat buttons: {out_path}")
    app.quit()

QTimer.singleShot(800, take_flat_overview)
app.exec()

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

# Switch to Buttons page
win.navigate("Buttons")

def take_buttons():
    pixmap = win.grab()
    out_path = "/Users/dangquochuy/.gemini/antigravity/brain/8a688404-0db4-4b19-bef0-38b1f35856af/studio_buttons.png"
    pixmap.save(out_path, "PNG")
    print(f"[+] Saved buttons screenshot to: {out_path}")
    
    # Next switch to dark theme and Inputs
    ThemeManager.set_theme("dark")
    win.navigate("Inputs")
    QTimer.singleShot(600, take_dark_inputs)

def take_dark_inputs():
    pixmap = win.grab()
    out_path = "/Users/dangquochuy/.gemini/antigravity/brain/8a688404-0db4-4b19-bef0-38b1f35856af/studio_dark_inputs.png"
    pixmap.save(out_path, "PNG")
    print(f"[+] Saved dark inputs screenshot to: {out_path}")
    app.quit()

QTimer.singleShot(800, take_buttons)
app.exec()

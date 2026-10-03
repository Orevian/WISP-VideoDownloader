import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui_main import MainWindow

def main():
    # Support high resolution display configurations seamlessly
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Configure high-dpi attributes if Qt version is prior to modern automatic scalings
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
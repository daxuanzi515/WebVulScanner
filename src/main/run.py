import qdarkstyle
from PyQt5.QtWidgets import QApplication
from qdarkstyle import LightPalette

from startpage import MainWindow

if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=LightPalette()))
    window = MainWindow()
    window.show()
    app.exec_()
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
import sys

home_ui, _ = loadUiType('C:/Users/natal/Downloads/Dat-Back/ui/pages/home.ui')


#====================================================================
#                    HOME
#====================================================================

class MainHome(QMainWindow, home_ui):
    def __init__(self, parent=None):
        super(MainHome, self).__init__(parent)

        self.setupUi(self)
        
def main():
    app = QApplication(sys.argv)
    window = MainHome()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    

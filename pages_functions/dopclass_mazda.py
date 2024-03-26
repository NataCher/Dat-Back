from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
import sys

mazda_ui, _ = loadUiType('C:/Users/natal/Downloads/Dat-Back/ui/pages/mazda.ui')


#====================================================================
#                    MAZDA
#====================================================================

class MainMazda(QMainWindow, mazda_ui):
    def __init__(self, parent=None):
        super(MainMazda, self).__init__(parent)

        self.setupUi(self)
        
def main():
    app = QApplication(sys.argv)
    window = MainMazda()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    

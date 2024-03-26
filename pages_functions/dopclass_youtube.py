from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
import sys

youtube_ui, _ = loadUiType('C:/Users/natal/Downloads/Dat-Back/ui/pages/youtube.ui')


#====================================================================
#                        YOUTUBE
#====================================================================

class MainYoutube(QMainWindow, youtube_ui):
    def __init__(self, parent=None):
        super(MainYoutube, self).__init__(parent)

        self.setupUi(self)
        
def main():
    app = QApplication(sys.argv)
    window = MainYoutube()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    

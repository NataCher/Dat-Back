from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import sys
import pandas as pd
import psycopg2
from PyQt5.uic import loadUiType



menu_ui, _ = loadUiType('C:/Users/natal/Downloads/Dat-Back/ui/menu.ui')

class MainAppReportForm(QMainWindow, menu_ui):
    def __init__(self, parent=None):
        super(MainAppReportForm, self).__init__(parent)


        self.setupUi(self)

def main():
    app = QApplication(sys.argv)
    window = MainAppReportForm()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()




from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
import sys

home_ui, _ = loadUiType('C:/Users/natal/Downloads/Dat-Back/ui/pages/home.ui')

class MainHome(QMainWindow, home_ui):
    def __init__(self, parent=None):
        super(MainHome, self).__init__(parent)

        self.setupUi(self)

        self.selectedFiles = []    
        self.backupLocation = ""



        self.btn_files.clicked.connect(self.openFileExplorer)
        self.btn_files_save.clicked.connect(self.openBackupLocationDialog)






    
    
    
    
    
    def openFileExplorer(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "Выбрать файлы и каталоги", "", "All Files (*)", options=options)
        if files:
            self.selectedFiles = files
            QMessageBox.information(self, 'Выбранные файлы и каталоги', '\n'.join(self.selectedFiles), QMessageBox.Ok)


    def openBackupLocationDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        directory = QFileDialog.getExistingDirectory(self, "Выбрать место для сохранения резервной копии", options=options)
        if directory:
            self.backupLocation = directory
            QMessageBox.information(self, 'Место для сохранения резервной копии', self.backupLocation, QMessageBox.Ok)

















def main():
    app = QApplication(sys.argv)
    window = MainHome()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    

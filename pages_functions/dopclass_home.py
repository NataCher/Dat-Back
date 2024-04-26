from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QMessageBox
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
import sys
import shutil
import os

home_ui, _ = loadUiType('C:/Users/natal/Downloads/Dat-Back/ui/pages/home.ui')

class Home(QMainWindow, home_ui):
    def __init__(self, parent=None):
        super(Home, self).__init__(parent)

        self.setupUi(self)
        self.progressBar.hide()

        self.selectedFiles = []    
        self.backupLocation = ""

        self.btn_files.clicked.connect(self.openFileExplorer)
        self.btn_files_save.clicked.connect(self.openBackupLocationDialog)
        self.btn_create_backup.clicked.connect(self.backupData)












        

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

    def backupData(self):
        if not self.selectedFiles:
            QMessageBox.warning(self, 'Внимание', 'Выберите файлы и каталоги для резервного копирования!', QMessageBox.Ok)
            return
        if not self.backupLocation:
            QMessageBox.warning(self, 'Внимание', 'Выберите место для сохранения резервной копии!', QMessageBox.Ok)
            return
        self.progressBar.show()
        self.progressBar.setValue(0)
        total_files = len(self.selectedFiles)
        self.progressBar.setMaximum(total_files)

        for index, file_or_directory in enumerate(self.selectedFiles, 1):
            try:
                if os.path.isfile(file_or_directory):
                    shutil.copy(file_or_directory, self.backupLocation)
                elif os.path.isdir(file_or_directory):
                    shutil.copytree(file_or_directory, os.path.join(self.backupLocation, os.path.basename(file_or_directory)))
                self.progressBar.setValue(index) 
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Ошибка при копировании {file_or_directory}: {e}', QMessageBox.Ok)

        QMessageBox.information(self, 'Готово', 'Резервное копирование завершено успешно!', QMessageBox.Ok)
        self.progressBar.hide()


















































































def main():
    app = QApplication(sys.argv)
    window = Home()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

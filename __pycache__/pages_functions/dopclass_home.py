from PyQt5.QtCore import Qt, QDir, QStandardPaths, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtWidgets import QMainWindow, QApplication, QRadioButton, QVBoxLayout, QGroupBox, QTreeView, QFileSystemModel, QPushButton, QFileDialog, QLineEdit, QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QMessageBox, QPlainTextEdit
from PyQt5.uic import loadUiType
from datetime import datetime
import sys
import shutil
import os
import time
import zipfile
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon


home_ui, _ = loadUiType('C:/Users/natal/Downloads/Dat-Back/ui/pages/home.ui')

def LogMessage(message):
    with open("backup_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")


class CheckableDirModel(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checked_items = set()

    def flags(self, index):
        flags = super().flags(index)
        if index.isValid() and index.column() == 0:  # Флажки только для первой колонки (Name)
            flags |= Qt.ItemIsUserCheckable
        return flags

    def data(self, index, role):
        if role == Qt.CheckStateRole and index.isValid() and index.column() == 0:  # Состояние флажка только для первой колонки
            return Qt.Checked if index in self.checked_items else Qt.Unchecked
        return super().data(index, role)

    def setData(self, index, value, role):
        if role == Qt.CheckStateRole and index.isValid() and index.column() == 0:
            # Установка или удаление флажка
            self.UpdateCheck(index, value)
            return True
        return super().setData(index, value, role)

    def UpdateCheck(self, index, value):
        if value == Qt.Checked:
            self.checked_items.add(index)
        else:
            self.checked_items.discard(index)
        # Рекурсивное изменение состояния дочерних элементов
        self.ChangeChildrenFolder(index, value)
   
        self.dataChanged.emit(index, index)

    def ChangeChildrenFolder(self, index, value):
        num_children = self.rowCount(index)
        for row in range(num_children):
            child_index = self.index(row, 0, index)  # Только первая колонка
            if value == Qt.Checked:
                self.checked_items.add(child_index)
            else:
                self.checked_items.discard(child_index)
            self.dataChanged.emit(child_index, child_index)
            # Продолжить рекурсивно для вложенных элементов
            if self.hasChildren(child_index):
                self.ChangeChildrenFolder(child_index, value)


class Home(QMainWindow, home_ui):
    def __init__(self, parent=None):
        super(Home, self).__init__(parent)
        self.setupUi(self)
        self.compression_type = zipfile.ZIP_DEFLATED

        self.model = CheckableDirModel()

        special_folders = [
            QStandardPaths.standardLocations(QStandardPaths.DesktopLocation)[0],
            QStandardPaths.standardLocations(QStandardPaths.DownloadLocation)[0],
            QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)[0],
            QStandardPaths.standardLocations(QStandardPaths.PicturesLocation)[0],
            QStandardPaths.writableLocation(QStandardPaths.MoviesLocation),
            QStandardPaths.standardLocations(QStandardPaths.MusicLocation)[0]
        ]

        reordered_folders = [
            special_folders[4],  # Movies
            special_folders[0],  # Desktop
            special_folders[1],  # Downloads
            special_folders[2],  # Documents
            special_folders[3],  # Pictures
            special_folders[5]   # Music
        ]

        for folder in reordered_folders:
            self.AddRootFolder(folder)

        # Установка модели для QTreeView
        self.treeView.setModel(self.model)
        self.treeView.setRootIndex(self.model.index(""))

        self.NetworkDrives()

        self.treeView.header().show()

        self.treeView.setAnimated(False)
        self.treeView.setIndentation(20)
        self.treeView.setSortingEnabled(True)

        self.model.directoryLoaded.connect(self.ResizeColumns)
        self.textEdit = self.plainTextEdit
        self.textEdit.setReadOnly(True) 

        self.btn_copy.clicked.connect(self.CopyFiles)
        self.btn_increment.clicked.connect(self.ShowIncrementalCopyDialog)
        self.btn_different.clicked.connect(self.ShowDiffCopyDialog)
        self.btn_pause.clicked.connect(self.PauseBackup)
        self.btn_resume.clicked.connect(self.ResumeBackup)
        self.btn_cancel.clicked.connect(self.StopBackup)

        self.progressBar.setValue(0)  

        self.ResizeColumns()
        self.EnableControlButtons(False)

    def NetworkDrives(self):
        network_drives = []
        for drive in range(ord('A'), ord('Z') + 1):
            drive_letter = chr(drive) + ':\\'
            if os.path.exists(drive_letter) and not os.path.ismount(drive_letter):
                network_drives.append(drive_letter)
        return network_drives
    
    def ShowDiffCopyDialog(self):
        dialog = DifferentialCopyDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            print("Инкрементная копия запущена")

    def ShowIncrementalCopyDialog(self):        
        dialog = IncrementalCopyDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            print("Инкрементная копия запущена")

    def AddRootFolder(self, folder):
        # Получаем индекс для указанной папки
        index = self.model.setRootPath(folder)

    def ResizeColumns(self):
        # Получаем количество колонок в QTreeView
        column_count = self.model.columnCount()

        # Растягиваем каждую колонку для того, чтобы весь текст был виден
        for column in range(column_count):
            self.treeView.resizeColumnToContents(column)

    def GetBackupName(self):
        dialog = NameDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            backup_name = dialog.edit.text().strip()
            is_folder_copy = dialog.radio_folder.isChecked()
            return backup_name, is_folder_copy
        return None, None

    def set_compression_type(self, compression_type):
        self.compression_type = compression_type  # Обновляем тип сжатия
    
    def CopyFiles(self):
        self.ClearText()
        self.AppendText("Начало резервного копирования.\n")

        self.btn_pause.setEnabled(True)
        self.btn_resume.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        
        selected_files = [self.model.filePath(index) for index in self.model.checked_items]
        if not selected_files:
            QMessageBox.information(self, "Нет выбранных файлов", "Не выбраны файлы для резервного копирования.")
            self.plainTextEdit.clear()
            self.ClearCheckboxes()
            return

        total_size = self.CalculateTotalSize(selected_files)
        formatted_size = self.FormatSize(total_size)
        self.label_size.setText(f"{formatted_size}")

        backup_name, is_folder_copy = self.GetBackupName()
        if backup_name is None:
            self.plainTextEdit.clear()
            self.ClearCheckboxes()   
            self.label_size.clear()   
            return  

        if not backup_name:
            backup_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if not backup_name.startswith("Backup-"):
            backup_name = "Backup-" + backup_name

        destination_folder = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения", "/")
        if not destination_folder:
            self.ClearCheckboxes()    
            self.plainTextEdit.clear()    
            self.label_size.clear()   
            return

        try:
            if is_folder_copy:
                backup_path = os.path.join(destination_folder, backup_name)
                self.AppendText(f"Создание резервной копии в папке: {backup_path}\n")
                if not os.path.exists(backup_path):
                    os.makedirs(backup_path)

                self.backup_thread = BackupThread(selected_files, backup_path)
                self.backup_thread.updateProgress.connect(self.UpdateProgress)
                self.backup_thread.updateText.connect(self.AppendText)
                self.backup_thread.finished.connect(self.BackupFinished)
                self.backup_thread.start()
            else:
                backup_path = os.path.join(destination_folder, backup_name + ".zip")
                self.AppendText(f"Создание ZIP архива: {backup_path}\n")
                self.zip_thread = ZipThread(selected_files, backup_path, self.compression_type)
                self.zip_thread.updateProgress.connect(self.UpdateProgress)
                self.zip_thread.updateText.connect(self.AppendText)
                self.zip_thread.finished.connect(self.BackupFinished)
                self.zip_thread.start()

                self.btn_pause.clicked.connect(self.zip_thread.pause)
                self.btn_resume.clicked.connect(self.zip_thread.resume)
                self.btn_cancel.clicked.connect(self.zip_thread.cancel)
        except Exception as e:
            self.AppendText(f"Ошибка при создании резервной копии: {str(e)}\n")
            self.ShowMessageDialog(f"Ошибка при создании резервной копии: {str(e)}", success=False)


    def CalculateTotalSize(self, files):
        total_size = 0
        visited_folders = set()  # Множество для отслеживания посещённых папок

        for file in files:
            if os.path.isfile(file):
                # Если выбран файл, просто добавляем его размер
                total_size += os.path.getsize(file)
            elif os.path.isdir(file):
                # Если выбрана папка, рекурсивно считаем размер всех файлов внутри папки
                total_size += self.CalculateFolderSize(file, visited_folders)

        return total_size
    
    def CalculateFolderSize(self, folder, visited_folders):
        total_size = 0
        # Проверяем, что папка ещё не была посещена (для избежания бесконечной рекурсии)
        if folder in visited_folders:
            return 0

        visited_folders.add(folder)  # Добавляем папку в список посещённых

        # Рекурсивно обходим содержимое папки
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)

        return total_size

    def FormatSize(self, size_bytes):
        # Преобразуем размер из байт в килобайты, мегабайты, гигабайты и т.д.
        for unit in ['байт', 'КБ', 'МБ', 'ГБ']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} ТБ"  # Если размер слишком большой для ГБ, выводим в терабайтах

    def UpdateProgress(self, value):
        self.progressBar.setValue(value)

    def AppendText(self, text):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.textEdit.ensureCursorVisible()

    def ClearText(self):
        self.textEdit.clear()

    def GetBackupName(self):
        dialog = NameDialog(self)
        if dialog.exec_():
            backup_name = dialog.edit.text().strip()
            is_folder_copy = dialog.radio_folder.isChecked()
            return backup_name, is_folder_copy
        return None, None

    def PauseBackup(self):
        if hasattr(self, 'backup_thread') and self.backup_thread.isRunning():
            self.backup_thread.pause()
            self.AppendText("Процесс резервного копирования приостановлен.\n")
            self.btn_pause.setEnabled(False)
            self.btn_resume.setEnabled(True)
        elif hasattr(self, 'zip_thread') and self.zip_thread.isRunning():
            self.zip_thread.pause()
            self.AppendText("Процесс резервного копирования приостановлен.\n")
            self.btn_pause.setEnabled(False)
            self.btn_resume.setEnabled(True)

    def ResumeBackup(self):
        if hasattr(self, 'backup_thread') and self.backup_thread.isRunning():
            self.backup_thread.resume()
            self.AppendText("Процесс резервного копирования возобновлен.\n")
            self.btn_pause.setEnabled(True)
            self.btn_resume.setEnabled(False)
        elif hasattr(self, 'zip_thread') and self.zip_thread.isRunning():
            self.zip_thread.resume()
            self.AppendText("Процесс резервного копирования возобновлен.\n")
            self.btn_pause.setEnabled(True)
            self.btn_resume.setEnabled(False)

    def StopBackup(self):
        if hasattr(self, 'backup_thread') and self.backup_thread.isRunning():
            self.backup_thread.stop()
            self.AppendText("Процесс резервного копирования остановлен.\n")
            self.btn_pause.setEnabled(False)
            self.btn_resume.setEnabled(False)
            self.btn_cancel.setEnabled(False)
            self.setEnabled(True)
            self.plainTextEdit.clear()
        elif hasattr(self, 'zip_thread') and self.zip_thread.isRunning():
            self.zip_thread.cancel()
            self.AppendText("Процесс резервного копирования остановлен.\n")
            self.btn_pause.setEnabled(False)
            self.btn_resume.setEnabled(False)
            self.btn_cancel.setEnabled(False)
            self.setEnabled(True)
            self.progressBar.setValue(0)
            self.plainTextEdit.clear()

    def BackupFinished(self):
        self.progressBar.setValue(0) 
        self.label_size.setText("")

        self.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.ClearCheckboxes()

        if (hasattr(self, 'backup_thread') and not self.backup_thread.was_stopped) or \
           (hasattr(self, 'zip_thread') and not self.zip_thread._cancel):
            QMessageBox.information(self, "Завершено", "Резервное копирование успешно завершено.")
            self.progressBar.setValue(0) 

    def ShowMessageDialog(self, message, success=True):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information if success else QMessageBox.Critical)
        msg_box.setWindowTitle("Успешно" if success else "Ошибка")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def ClearCheckboxes(self):
        # Создание копии списка checked_items для предотвращения ошибки изменения размера набора во время итерации
        checked_items_copy = self.model.checked_items.copy()
        
        # Сброс всех флажков
        for index in checked_items_copy:
            self.model.setData(index, Qt.Unchecked, Qt.CheckStateRole)

        # Очистка списка выбранных элементов
        self.model.checked_items.clear()

    def EnableControlButtons(self, enable):
        self.btn_pause.setEnabled(enable)
        self.btn_resume.setEnabled(enable)
        self.btn_cancel.setEnabled(enable)


class NameDialog(QDialog):
    def __init__(self, parent=None):
        super(NameDialog, self).__init__(parent)
        self.setupUi(self)

        self.backup_name = None
        self.is_folder_copy = False
        self.compression_type = zipfile.ZIP_DEFLATED
        self.okButton.clicked.connect(self.Accept)
        self.cancelButton.clicked.connect(self.reject)

    def setupUi(self, NameDialog):
        NameDialog.setObjectName("NameDialog")
        NameDialog.setFixedSize(514, 439)
        NameDialog.setStyleSheet("QNameDialog {\n"
"                border-style: outset;\n"
"                border-width: 2px;\n"
"                border-radius: 10px;\n"
"                padding: 6px;\n"
"}")
        self.label = QtWidgets.QLabel(NameDialog)
        self.label.setGeometry(QtCore.QRect(40, 50, 461, 31))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.edit = QtWidgets.QLineEdit(NameDialog)
        self.edit.setEnabled(True)
        self.edit.setGeometry(QtCore.QRect(20, 90, 471, 51))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(11)
        self.edit.setFont(font)
        self.edit.setStyleSheet("QLineEdit {\n"
"                border-style: outset;\n"
"                border-width: 2px;\n"
"                border-radius: 10px;\n"
"                min-width: 10em;\n"
"                padding: 6px;\n"
"                border: 2px solid #1f3861;\n"
"}\n"
"\n"
"\n"
"")
        self.edit.setObjectName("edit")
        self.groupBox = QtWidgets.QGroupBox(NameDialog)
        self.groupBox.setGeometry(QtCore.QRect(120, 170, 291, 141))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setStyleSheet("QGroupBox {\n"
"    border: 2px solid #1f3861;\n"
"    border-radius: 10px;\n"
"    margin-top: 6px;\n"
"}\n"
"\n"
"QGroupBox::indicator:unchecked {\n"
"    background-color: #20232A;\n"
"}\n"
"\n"
"QGroupBox::indicator:checked {\n"
"    background-color: #1c4483;\n"
"}\n"
"\n"
"QComboBox {\n"
"    background-color: #20232A;\n"
"    color: #61dafb;\n"
"    border-style: outset;\n"
"    border-width: 2px;\n"
"    border-radius: 10px;\n"
"    padding: 6px;\n"
"}\n"
"\n"
"QComboBox:hover {\n"
"    background-color: #1f3861;\n"
"}\n"
"\n"
"QComboBox:pressed {\n"
"    background-color: #1c4483;\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    width: 20px;\n"
"    height: 20px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #20232A;\n"
"    color: #61dafb;\n"
"    border: 2px solid #1f3861;\n"
"    selection-background-color: #1c4483;\n"
"}\n"
"")
        self.groupBox.setObjectName("groupBox")
        self.radio_folder = QtWidgets.QRadioButton(self.groupBox)
        self.radio_folder.setGeometry(QtCore.QRect(20, 50, 95, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.radio_folder.setFont(font)
        self.radio_folder.setObjectName("radio_folder")
        self.radio_zip = QtWidgets.QRadioButton(self.groupBox)
        self.radio_zip.setGeometry(QtCore.QRect(20, 100, 111, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.radio_zip.setFont(font)
        self.radio_zip.setObjectName("radio_zip")
        self.cancelButton = QtWidgets.QPushButton(NameDialog)
        self.cancelButton.setGeometry(QtCore.QRect(260, 350, 176, 61))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.cancelButton.setFont(font)
        self.cancelButton.setStyleSheet("            QWidget {\n"
"                background-color: #20232A;\n"
"                color: #61dafb;\n"
"            }\n"
"QPushButton {\n"
"                border-style: outset;\n"
"                border-width: 2px;\n"
"                border-radius: 10px;\n"
"                padding: 6px;\n"
"}\n"
"QPushButton:hover {\n"
"background-color: #1f3861;\n"
"}\n"
"QPushButton:pressed {\n"
"background-color: #1c4483;\n"
"\n"
"}\n"
"            QLabel {\n"
"                color: #61dafb;\n"
"                font: bold 16px;\n"
"            }\n"
"\n"
"\n"
"\n"
"\n"
"")
        self.cancelButton.setObjectName("cancelButton")
        self.okButton = QtWidgets.QPushButton(NameDialog)
        self.okButton.setGeometry(QtCore.QRect(80, 350, 171, 61))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.okButton.setFont(font)
        self.okButton.setStyleSheet("            QWidget {\n"
"                background-color: #20232A;\n"
"                color: #61dafb;\n"
"            }\n"
"QPushButton {\n"
"                border-style: outset;\n"
"                border-width: 2px;\n"
"                border-radius: 10px;\n"
"                padding: 6px;\n"
"}\n"
"QPushButton:hover {\n"
"background-color: #1f3861;\n"
"}\n"
"QPushButton:pressed {\n"
"background-color: #1c4483;\n"
"\n"
"}\n"
"            QLabel {\n"
"                color: #61dafb;\n"
"                font: bold 16px;\n"
"            }\n"
"\n"
"\n"
"\n"
"\n"
"")
        self.okButton.setObjectName("okButton")

        self.retranslateUi(NameDialog)
        QtCore.QMetaObject.connectSlotsByName(NameDialog)

    def retranslateUi(self, NameDialog):
        _translate = QtCore.QCoreApplication.translate
        NameDialog.setWindowTitle(_translate("NameDialog", "Настройка создания бэкапа"))
        self.label.setText(_translate("NameDialog", "Введите имя для резервной копии"))
        self.groupBox.setTitle(_translate("NameDialog", "Выберите тип сохранения:"))
        self.radio_folder.setText(_translate("NameDialog", "Папка"))
        self.radio_zip.setText(_translate("NameDialog", "ZIP архив"))
        self.cancelButton.setText(_translate("NameDialog", "Отмена"))
        self.okButton.setText(_translate("NameDialog", "ОК"))

    def Accept(self):
        if not self.radio_folder.isChecked() and not self.radio_zip.isChecked():
            QMessageBox.warning(self, "Предупреждение", "Выберите тип сохранения: Папка или ZIP архив.")
        else:
            self.backup_name = self.edit.text().strip()
            self.is_folder_copy = self.radio_folder.isChecked()

            if self.radio_zip.isChecked():
                compression_dialog = CompressionDialog(self)
                if compression_dialog.exec_() == QDialog.Accepted:
                    self.compression_type = compression_dialog.GetCompressionType()
                    super().accept()
                else:
                    self.radio_folder.setChecked(True)
            else:
                super().accept()



class ZipThread(QThread):
    updateText = pyqtSignal(str)
    updateProgress = pyqtSignal(int)

    def __init__(self, files, backup_path, compression_type, parent=None):
        super(ZipThread, self).__init__(parent)
        self.files = files
        self.backup_path = backup_path
        self.compression_type = compression_type
        self._cancel = False
        self._pause = False
        self.zipf = None

    def run(self):
        total_files = self.CountTotalFilesPB(self.files)
        files_zipped = 0
        try:
            with zipfile.ZipFile(self.backup_path, 'w', self.compression_type) as zipf:
                self.zipf = zipf
                for file_path in self.files:
                    if self._cancel:
                        self.updateText.emit("Копирование отменено.\n")
                        break
                    while self._pause and not self._cancel:
                        time.sleep(0.1)
                    if self._cancel:
                        break
                    if os.path.isdir(file_path):
                        base_folder_name = os.path.basename(file_path)
                        for root, dirs, files in os.walk(file_path):
                            for file in files:
                                if self._cancel:
                                    self.updateText.emit("Копирование отменено.\n")
                                    break
                                while self._pause and not self._cancel:
                                    time.sleep(0.1)
                                if self._cancel:
                                    break
                                file_abs_path = os.path.join(root, file)
                                rel_path = os.path.relpath(file_abs_path, file_path)
                                zipf.write(file_abs_path, os.path.join(base_folder_name, rel_path))
                                self.updateText.emit(f"Скопировано: {file_abs_path}\n")
                                files_zipped += 1
                                progress = int((files_zipped / total_files) * 100)
                                self.updateProgress.emit(progress)
                    else:
                        zipf.write(file_path, os.path.basename(file_path))
                        self.updateText.emit(f"Скопировано: {file_path}\n")
                        files_zipped += 1
                        progress = int((files_zipped / total_files) * 100)
                        self.updateProgress.emit(progress)
        except Exception as e:
            self.updateText.emit(f"Ошибка при создании ZIP архива: {str(e)}\n")
        finally:
            if self.zipf is not None:
                self.zipf.close()
                self.zipf = None

    def CountTotalFilesPB(self, files):
        total_files = 0
        for file_path in files:
            if os.path.isdir(file_path):
                for _, _, file_list in os.walk(file_path):
                    total_files += len(file_list)
            else:
                total_files += 1
        return total_files

    def cancel(self):
        self._cancel = True
        self._pause = False
        self.wait()
        if os.path.exists(self.backup_path):
            os.remove(self.backup_path)

    def pause(self):
        self._pause = True

    def resume(self):
        self._pause = False
    
class BackupThread(QThread):
    updateText = pyqtSignal(str)
    updateProgress = pyqtSignal(int)

    def __init__(self, files, backup_path, parent=None):
        super(BackupThread, self).__init__(parent)
        self.files = files
        self.backup_path = backup_path
        self.stopped = False
        self._pause = False
        self.was_stopped = False

    def run(self):
        total_files = self.CountTotalFiles(self.files)
        files_copied = 0

        try:
            for file_path in self.files:
                if self.stopped:
                    self.updateText.emit("Копирование отменено.\n")
                    break
                while self._pause:
                    time.sleep(0.1)
                if os.path.isdir(file_path):
                    base_folder_name = os.path.basename(file_path)
                    for root, dirs, files in os.walk(file_path):
                        for file in files:
                            if self.stopped:
                                self.updateText.emit("Копирование отменено.\n")
                                break
                            while self._pause:
                                time.sleep(0.1)
                            file_abs_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_abs_path, file_path)
                            dest_path = os.path.join(self.backup_path, base_folder_name, rel_path)
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                            shutil.copy(file_abs_path, dest_path)
                            self.updateText.emit(f"Скопировано: {file_abs_path}\n")
                            files_copied += 1
                            progress = int((files_copied / total_files) * 100)
                            self.updateProgress.emit(progress)
                else:
                    dest_path = os.path.join(self.backup_path, os.path.basename(file_path))
                    shutil.copy(file_path, dest_path)
                    self.updateText.emit(f"Скопировано: {file_path}\n")
                    files_copied += 1
                    progress = int((files_copied / total_files) * 100)
                    self.updateProgress.emit(progress)
        except Exception as e:
            self.updateText.emit(f"Ошибка при копировании файлов: {str(e)}\n")

    def stop(self):
        self._cancel = True
        self._pause = False 
        self.stopped = True
        self.was_stopped = True
        try:
            self.wait()  
            if os.path.exists(self.backup_path):
                shutil.rmtree(self.backup_path)
                self.updateText.emit(f"Удалена папка: {self.backup_path}\n")
        except Exception as e:
            self.updateText.emit(f"Ошибка при удалении папки: {str(e)}\n")
            
    def CopyFolderr(self, source_folder, destination_folder):
        base_folder_name = os.path.basename(source_folder)
        dest_folder_path = os.path.join(destination_folder, base_folder_name)
        if not os.path.exists(dest_folder_path):
            os.makedirs(dest_folder_path)
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                if self._cancel:
                    self.updateText.emit("Копирование отменено.\н")
                    return
                while self._pause and not self._cancel:
                    time.sleep(0.1)
                if self._cancel:
                    return
                file_abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_abs_path, source_folder)
                dest_path = os.path.join(dest_folder_path, rel_path)
                dest_dir = os.path.dirname(dest_path)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                shutil.copy2(file_abs_path, dest_path)
                self.updateText.emit(f"Скопировано: {file_abs_path}\n")
    def pause(self):
        self._pause = True

    def resume(self):
        self._pause = False

    def CountTotalFiles(self, files):
        total_files = 0
        for file_path in files:
            if os.path.isdir(file_path):
                for root, dirs, files in os.walk(file_path):
                    total_files += len(files)
            else:
                total_files += 1
        return total_files
                

class IncrementalCopyDialog(QDialog):
    def __init__(self, parent=None):
        super(IncrementalCopyDialog, self).__init__(parent)
        self.setupUi(self)
        self.browse_button.clicked.connect(self.BrowseDirectory)
        self.start_button.clicked.connect(self.StartIncrementalCopy)
        self.line_edit.setReadOnly(True)

    def setupUi(self, IncrementalCopyDialog):
        IncrementalCopyDialog.setObjectName("IncrementalCopyDialog")
        IncrementalCopyDialog.setFixedSize(1005, 281)
        IncrementalCopyDialog.setStyleSheet("QNameDialog {\n"
"                border-style: outset;\n"
"                border-width: 2px;\n"
"                border-radius: 10px;\n"
"                padding: 6px;\n"
"}")
        self.path_layout = QtWidgets.QLabel(IncrementalCopyDialog)
        self.path_layout.setGeometry(QtCore.QRect(160, 30, 691, 41))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.path_layout.setFont(font)
        self.path_layout.setObjectName("path_layout")
        self.start_button = QtWidgets.QPushButton(IncrementalCopyDialog)
        self.start_button.setGeometry(QtCore.QRect(420, 200, 176, 61))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.start_button.setFont(font)
        self.start_button.setStyleSheet("            QWidget {\n"
"                background-color: #20232A;\n"
"                color: #61dafb;\n"
"            }\n"
"QPushButton {\n"
"                border-style: outset;\n"
"                border-width: 2px;\n"
"                border-radius: 10px;\n"
"                padding: 6px;\n"
"}\n"
"QPushButton:hover {\n"
"background-color: #1f3861;\n"
"}\n"
"QPushButton:pressed {\n"
"background-color: #1c4483;\n"
"\n"
"}\n"
"            QLabel {\n"
"                color: #61dafb;\n"
"                font: bold 16px;\n"
"            }\n"
"\n"
"\n"
"\n"
"\n"
"")
        self.start_button.setObjectName("start_button")
        self.frame = QtWidgets.QFrame(IncrementalCopyDialog)
        self.frame.setGeometry(QtCore.QRect(40, 100, 931, 51))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.line_edit = QtWidgets.QLineEdit(self.frame)
        self.line_edit.setEnabled(True)
        self.line_edit.setGeometry(QtCore.QRect(0, 0, 721, 51))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(11)
        self.line_edit.setFont(font)
        self.line_edit.setStyleSheet("QLineEdit {\n"
"                border-style: outset;\n"
"                border-width: 2px;\n"
"                border-radius: 10px;\n"
"                min-width: 10em;\n"
"                padding: 6px;\n"
"                border: 2px solid #1f3861;\n"
"}\n"
"\n"
"\n"
"")
        self.line_edit.setObjectName("line_edit")
        self.browse_button = QtWidgets.QPushButton(self.frame)
        self.browse_button.setGeometry(QtCore.QRect(750, 0, 176, 51))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.browse_button.setFont(font)
        self.browse_button.setStyleSheet("            QWidget {\n"
"                background-color: #20232A;\n"
"                color: #61dafb;\n"
"            }\n"
"QPushButton {\n"
"                border-style: outset;\n"
"                border-width: 2px;\n"
"                border-radius: 10px;\n"
"                padding: 6px;\n"
"}\n"
"QPushButton:hover {\n"
"background-color: #1f3861;\n"
"}\n"
"QPushButton:pressed {\n"
"background-color: #1c4483;\n"
"\n"
"}\n"
"            QLabel {\n"
"                color: #61dafb;\n"
"                font: bold 16px;\n"
"            }\n"
"\n"
"\n"
"\n"
"\n"
"")
        self.browse_button.setObjectName("browse_button")

        self.retranslateUi(IncrementalCopyDialog)
        QtCore.QMetaObject.connectSlotsByName(IncrementalCopyDialog)

    def retranslateUi(self, IncrementalCopyDialog):
        _translate = QtCore.QCoreApplication.translate
        IncrementalCopyDialog.setWindowTitle(_translate("IncrementalCopyDialog", "Инкрементная резервная копия"))
        self.path_layout.setText(_translate("IncrementalCopyDialog", "Укажите папку для создания инкрементной копии"))
        self.start_button.setText(_translate("IncrementalCopyDialog", "Запустить"))
        self.browse_button.setText(_translate("IncrementalCopyDialog", "Выбрать папку"))

    def BrowseDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку", "")
        if directory:
            self.line_edit.setText(directory)

    def StartIncrementalCopy(self):
        target_folder = self.line_edit.text().strip()
        if not target_folder:
            print("Выберите папку для инкрементной копии.")
            return

        copy_dir = os.path.join('C:\\', 'Increment Backup')
        short_bkpdir = time.strftime('%Y-%m-%d_%H-%M-%S')
        bkp_dir = os.path.join(copy_dir, os.path.basename(target_folder), short_bkpdir)

        try:
            os.makedirs(copy_dir, exist_ok=True)
            os.chdir(copy_dir)

            last_bkpsubdir = None
            for dr in os.listdir(copy_dir):
                if os.path.isdir(os.path.join(copy_dir, dr)):
                    last_bkpsubdir = dr
                    break

            last_bkptime = os.path.getmtime(os.path.join(copy_dir, last_bkpsubdir)) if last_bkpsubdir else 0

            if last_bkpsubdir != short_bkpdir:
                bkp_dir = os.path.join(copy_dir, os.path.basename(target_folder), short_bkpdir)
                os.makedirs(bkp_dir, exist_ok=True)

                for root, dirs, files in os.walk(target_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_time = os.path.getmtime(file_path)
                        if file_time > last_bkptime:
                            relative_path = os.path.relpath(file_path, target_folder)
                            dest_path = os.path.join(bkp_dir, relative_path)
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                            shutil.copy2(file_path, dest_path)
                            LogMessage(f"Скопировано: {file_path}")

                    for subdir in dirs:
                        dir_path = os.path.join(root, subdir)
                        dir_time = os.path.getmtime(dir_path)
                        if dir_time > last_bkptime:
                            relative_path = os.path.relpath(dir_path, target_folder)
                            dest_path = os.path.join(bkp_dir, relative_path)
                            os.makedirs(dest_path, exist_ok=True)
                            LogMessage(f"Создана папка: {dir_path}")

            QMessageBox.information(self, "Информация", "Инкрементная копия завершена успешно.")
            LogMessage("Инкрементная копия завершена успешно.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при инкрементной копии: {str(e)}")
            LogMessage(f"Ошибка при инкрементной копии: {str(e)}")



class DifferentialCopyDialog(QDialog):
    def __init__(self, parent=None):
        super(DifferentialCopyDialog, self).__init__(parent)

        self.setupUi(self)

        self.browsedif_button.clicked.connect(self.BrowseDirectory)
        self.startdif_button.clicked.connect(self.StartDifferentialCopy)
        self.line_edit_diff.setReadOnly(True)

    def setupUi(self, DifferentialCopyDialog):
        DifferentialCopyDialog.setObjectName("DifferentialCopyDialog")
        DifferentialCopyDialog.setFixedSize(1005, 281)

        DifferentialCopyDialog.setStyleSheet("QNameDialog {\n"
"                border-style: outset;\n"
"                border-width: 2px;\n"
"                border-radius: 10px;\n"
"                padding: 6px;\n"
"}")
        self.path_layout = QtWidgets.QLabel(DifferentialCopyDialog)
        self.path_layout.setGeometry(QtCore.QRect(140, 30, 701, 41))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.path_layout.setFont(font)
        self.path_layout.setObjectName("path_layout")
        self.startdif_button = QtWidgets.QPushButton(DifferentialCopyDialog)
        self.startdif_button.setGeometry(QtCore.QRect(420, 200, 176, 61))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.startdif_button.setFont(font)
        self.startdif_button.setStyleSheet("            QWidget {\n"
"                background-color: #20232A;\n"
"                color: #61dafb;\n"
"            }\n"
"QPushButton {\n"
"                border-style: outset;\n"
"                border-width: 2px;\n"
"                border-radius: 10px;\n"
"                padding: 6px;\n"
"}\n"
"QPushButton:hover {\n"
"background-color: #1f3861;\n"
"}\n"
"QPushButton:pressed {\n"
"background-color: #1c4483;\n"
"\n"
"}\n"
"            QLabel {\n"
"                color: #61dafb;\n"
"                font: bold 16px;\n"
"            }\n"
"\n"
"\n"
"\n"
"\n"
"")
        self.startdif_button.setObjectName("startdif_button")
        self.frame = QtWidgets.QFrame(DifferentialCopyDialog)
        self.frame.setGeometry(QtCore.QRect(40, 100, 931, 51))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.line_edit_diff = QtWidgets.QLineEdit(self.frame)
        self.line_edit_diff.setEnabled(True)
        self.line_edit_diff.setGeometry(QtCore.QRect(0, 0, 721, 51))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(11)
        self.line_edit_diff.setFont(font)
        self.line_edit_diff.setStyleSheet("QLineEdit {\n"
"                border-style: outset;\n"
"                border-width: 2px;\n"
"                border-radius: 10px;\n"
"                min-width: 10em;\n"
"                padding: 6px;\n"
"                border: 2px solid #1f3861;\n"
"}\n"
"\n"
"\n"
"")
        self.line_edit_diff.setObjectName("line_edit_diff")
        self.browsedif_button = QtWidgets.QPushButton(self.frame)
        self.browsedif_button.setGeometry(QtCore.QRect(750, 0, 176, 51))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.browsedif_button.setFont(font)
        self.browsedif_button.setStyleSheet("            QWidget {\n"
"                background-color: #20232A;\n"
"                color: #61dafb;\n"
"            }\n"
"QPushButton {\n"
"                border-style: outset;\n"
"                border-width: 2px;\n"
"                border-radius: 10px;\n"
"                padding: 6px;\n"
"}\n"
"QPushButton:hover {\n"
"background-color: #1f3861;\n"
"}\n"
"QPushButton:pressed {\n"
"background-color: #1c4483;\n"
"\n"
"}\n"
"            QLabel {\n"
"                color: #61dafb;\n"
"                font: bold 16px;\n"
"            }\n"
"\n"
"\n"
"\n"
"\n"
"")
        self.browsedif_button.setObjectName("browsedif_button")

        self.retranslateUi(DifferentialCopyDialog)
        QtCore.QMetaObject.connectSlotsByName(DifferentialCopyDialog)

    def retranslateUi(self, DifferentialCopyDialog):
        _translate = QtCore.QCoreApplication.translate
        DifferentialCopyDialog.setWindowTitle(_translate("DifferentialCopyDialog", "Диференциальная резервная копия"))
        self.path_layout.setText(_translate("DifferentialCopyDialog", "Укажите папку для создания диференциальной копии"))
        self.startdif_button.setText(_translate("DifferentialCopyDialog", "Запустить"))
        self.browsedif_button.setText(_translate("DifferentialCopyDialog", "Выбрать папку"))

    def BrowseDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку", "")
        if directory:
            self.line_edit_diff.setText(directory)

    def StartDifferentialCopy(self):
        target_folder = self.line_edit_diff.text().strip()
        if not target_folder:
            print("Выберите папку для дифференциальной копии.")
            return

        copy_dir = os.path.join('C:\\', 'Differential Backup')
        short_bkpdir = time.strftime('%Y-%m-%d_%H-%M-%S')
        bkp_dir = os.path.join(copy_dir, os.path.basename(target_folder), short_bkpdir)

        try:
            os.makedirs(copy_dir, exist_ok=True)
            os.chdir(copy_dir)

            for root, dirs, files in os.walk(target_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, target_folder)
                    dest_path = os.path.join(bkp_dir, relative_path)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(file_path, dest_path)
                    LogMessage(f"Скопировано: {file_path}")

                for subdir in dirs:
                    dir_path = os.path.join(root, subdir)
                    relative_path = os.path.relpath(dir_path, target_folder)
                    dest_path = os.path.join(bkp_dir, relative_path)
                    os.makedirs(dest_path, exist_ok=True)
                    LogMessage(f"Создана папка: {dir_path}")

            QMessageBox.information(self, "Информация", "Дифференциальная копия завершена успешно.")
            LogMessage("Дифференциальная копия завершена успешно.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при дифференциальной копии: {str(e)}")
            LogMessage(f"Ошибка при дифференциальной копии: {str(e)}")


class CompressionDialog(QDialog):
    def __init__(self, parent=None):
        super(CompressionDialog, self).__init__(parent)
        self.setupUi(self)

        self.compression_type = zipfile.ZIP_DEFLATED

        self.radio_deflated.setChecked(True)
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

    def setupUi(self, CompressionDialog):
        CompressionDialog.setObjectName("CompressionDialog")
        CompressionDialog.setFixedSize(514, 439)
        CompressionDialog.setStyleSheet("QNameDialog {\n"
"                border-style: outset;\n"
"                border-width: 2px;\n"
"                border-radius: 10px;\n"
"                padding: 6px;\n"
"}")
        self.cancelButton = QtWidgets.QPushButton(CompressionDialog)
        self.cancelButton.setGeometry(QtCore.QRect(260, 320, 176, 61))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.cancelButton.setFont(font)
        self.cancelButton.setStyleSheet("            QWidget {\n"
"                background-color: #20232A;\n"
"                color: #61dafb;\n"
"            }\n"
"QPushButton {\n"
"                border-style: outset;\n"
"                border-width: 2px;\n"
"                border-radius: 10px;\n"
"                padding: 6px;\n"
"}\n"
"QPushButton:hover {\n"
"background-color: #1f3861;\n"
"}\n"
"QPushButton:pressed {\n"
"background-color: #1c4483;\n"
"\n"
"}\n"
"            QLabel {\n"
"                color: #61dafb;\n"
"                font: bold 16px;\n"
"            }\n"
"\n"
"\n"
"\n"
"\n"
"")
        self.cancelButton.setObjectName("cancelButton")
        self.okButton = QtWidgets.QPushButton(CompressionDialog)
        self.okButton.setGeometry(QtCore.QRect(80, 320, 171, 61))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.okButton.setFont(font)
        self.okButton.setStyleSheet("            QWidget {\n"
"                background-color: #20232A;\n"
"                color: #61dafb;\n"
"            }\n"
"QPushButton {\n"
"                border-style: outset;\n"
"                border-width: 2px;\n"
"                border-radius: 10px;\n"
"                padding: 6px;\n"
"}\n"
"QPushButton:hover {\n"
"background-color: #1f3861;\n"
"}\n"
"QPushButton:pressed {\n"
"background-color: #1c4483;\n"
"\n"
"}\n"
"            QLabel {\n"
"                color: #61dafb;\n"
"                font: bold 16px;\n"
"            }\n"
"\n"
"\n"
"\n"
"\n"
"")
        self.okButton.setObjectName("okButton")
        self.radio_deflated = QtWidgets.QRadioButton(CompressionDialog)
        self.radio_deflated.setGeometry(QtCore.QRect(170, 130, 211, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.radio_deflated.setFont(font)
        self.radio_deflated.setObjectName("radio_deflated")
        self.radio_bzip2 = QtWidgets.QRadioButton(CompressionDialog)
        self.radio_bzip2.setGeometry(QtCore.QRect(170, 210, 161, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.radio_bzip2.setFont(font)
        self.radio_bzip2.setObjectName("radio_bzip2")
        self.radio_lzma = QtWidgets.QRadioButton(CompressionDialog)
        self.radio_lzma.setGeometry(QtCore.QRect(170, 250, 151, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.radio_lzma.setFont(font)
        self.radio_lzma.setObjectName("radio_lzma")
        self.radio_stored = QtWidgets.QRadioButton(CompressionDialog)
        self.radio_stored.setGeometry(QtCore.QRect(170, 170, 151, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.radio_stored.setFont(font)
        self.radio_stored.setObjectName("radio_stored")
        self.label = QtWidgets.QLabel(CompressionDialog)
        self.label.setGeometry(QtCore.QRect(100, 40, 321, 61))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(17)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")

        self.retranslateUi(CompressionDialog)
        QtCore.QMetaObject.connectSlotsByName(CompressionDialog)

    def retranslateUi(self, CompressionDialog):
        _translate = QtCore.QCoreApplication.translate
        CompressionDialog.setWindowTitle(_translate("CompressionDialog", "Выбор типа сжатия"))
        self.cancelButton.setText(_translate("CompressionDialog", "Отмена"))
        self.okButton.setText(_translate("CompressionDialog", "ОК"))
        self.radio_deflated.setText(_translate("CompressionDialog", "Обычное сжатие"))
        self.radio_bzip2.setText(_translate("CompressionDialog", "Сжатие BZIP2"))
        self.radio_lzma.setText(_translate("CompressionDialog", "Сжатие LZMA"))
        self.radio_stored.setText(_translate("CompressionDialog", "Без сжатия"))
        self.label.setText(_translate("CompressionDialog", "Выберите тип сжатия"))

        self.radio_deflated.toggled.connect(self.UpdateCompressionType)
        self.radio_stored.toggled.connect(self.UpdateCompressionType)
        self.radio_bzip2.toggled.connect(self.UpdateCompressionType)
        self.radio_lzma.toggled.connect(self.UpdateCompressionType)

    def UpdateCompressionType(self):
        if self.radio_deflated.isChecked():
            self.compression_type = zipfile.ZIP_DEFLATED
        elif self.radio_stored.isChecked():
            self.compression_type = zipfile.ZIP_STORED
        elif self.radio_bzip2.isChecked():
            self.compression_type = zipfile.ZIP_BZIP2
        elif self.radio_lzma.isChecked():
            self.compression_type = zipfile.ZIP_LZMA

    def GetCompressionType(self):
        return self.compression_type

        
def main():
    app = QApplication(sys.argv)
    window = Home()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

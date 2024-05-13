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
home_ui, _ = loadUiType('C:/Users/natal/Downloads/Dat-Back/ui/pages/home.ui')

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

        # Уведомить о изменении
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

        # Создание модели QFileSystemModel
        self.model = CheckableDirModel()

        # Список системных папок для отображения в QTreeView
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

        # Установка свойств QTreeView
        self.treeView.setAnimated(False)
        self.treeView.setIndentation(20)
        self.treeView.setSortingEnabled(True)
        self.model.directoryLoaded.connect(self.ResizeColumns)


        # Создание виджета для вывода текста
        self.textEdit = self.plainTextEdit
        self.textEdit.setReadOnly(True) 

        self.btn_copy.clicked.connect(self.CopyFiles)
        self.btn_increment.clicked.connect(self.ShowIncrementalCopyDialog)
        self.btn_different.clicked.connect(self.ShowDiffCopyDialog)

        self.progressBar.setValue(0)  

        self.ResizeColumns()

    def ShowDiffCopyDialog(self):
        dialog = DifferentialCopyDialog(self)
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

    def CopyFiles(self):
        self.ClearText() 
        self.AppendText("Начало резервного копирования...\n")

        selected_files = [self.model.filePath(index) for index in self.model.checked_items]
        if not selected_files:
            QMessageBox.information(self, "Нет выбранных файлов", "Не выбраны файлы для резервного копирования.")
            return

        # Вычисляем общий размер выбранных данных
        total_size = self.CalculateTotalSize(selected_files)

        # Отображаем размер в нужной единице измерения на QLabel
        formatted_size = self.FormatSize(total_size)
        self.label_size.setText(f"{formatted_size}")

        backup_name, is_folder_copy = self.GetBackupName()
        if not backup_name:
            backup_name = "Backup-" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        destination_folder = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения", "/")
        if not destination_folder:
            return

        try:
            if is_folder_copy:
                backup_path = os.path.join(destination_folder, backup_name)
                self.AppendText(f"Создание резервной копии в папке: {backup_path}\n")
                self.backup_thread = BackupThread(selected_files, backup_path)
                self.backup_thread.updateProgress.connect(self.UpdateProgress)
                self.backup_thread.updateText.connect(self.AppendText)
                self.backup_thread.finished.connect(self.BackupFinished)  
                self.backup_thread.start()
            else:
                backup_path = os.path.join(destination_folder, backup_name + ".zip")
                self.AppendText(f"Создание ZIP архива: {backup_path}\n")
                
                with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    total_files = len(selected_files)
                    for idx, file_path in enumerate(selected_files):
                        if os.path.isdir(file_path):
                            base_folder_name = os.path.basename(file_path)
                            for root, dirs, files in os.walk(file_path):
                                for file in files:
                                    file_abs_path = os.path.join(root, file)
                                    rel_path = os.path.relpath(file_abs_path, file_path)
                                    zipf.write(file_abs_path, os.path.join(base_folder_name, rel_path))
                                    self.AppendText(f"Скопировано: {file_abs_path}\n")
                                    QApplication.processEvents()  # Обновляем интерфейс
                        else:
                            zipf.write(file_path, os.path.basename(file_path))
                            self.AppendText(f"Скопировано: {file_path}\n")
                            QApplication.processEvents()  # Обновляем интерфейс
                     
                        current_progress = int((idx + 1) * 100 / total_files)
                        self.UpdateProgress(current_progress)

                self.AppendText("Резервная копия создана успешно.\n")
                self.ShowMessageDialog("Резервная копия создана успешно.")
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

    def BackupFinished(self):
        self.progressBar.setValue(0) 
        self.ShowMessageDialog("Резервная копия создана успешно.")

    def ShowMessageDialog(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Успешно")
        msg_box.setText(message)
        msg_box.exec_()


    def ShowIncrementalCopyDialog(self):
        dialog = IncrementalCopyDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            print("Инкрементная копия запущена")

class NameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.backup_name = None
        self.is_folder_copy = False
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.label = QLabel("Введите имя для резервной копии:")
        layout.addWidget(self.label)
        self.edit = QLineEdit()
        layout.addWidget(self.edit)

        self.radioGroupBox = QGroupBox("Тип резервной копии:")
        radioLayout = QVBoxLayout()

        self.radio_folder = QRadioButton("Папка")
        self.radio_zip = QRadioButton("ZIP архив")

        radioLayout.addWidget(self.radio_folder)
        radioLayout.addWidget(self.radio_zip)

        self.radioGroupBox.setLayout(radioLayout)
        layout.addWidget(self.radioGroupBox)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        buttons.accepted.connect(self.Accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def Accept(self):
        if not self.radio_folder.isChecked() and not self.radio_zip.isChecked():
            QMessageBox.warning(self, "Предупреждение", "Выберите тип сохранения: Папка или ZIP архив.")
        else:
            self.backup_name = self.edit.text().strip()
            self.is_folder_copy = self.radio_folder.isChecked()
            super().accept()

    def GetBackupName(self):
        return self.backup_name, self.is_folder_copy


class ZipThread(QThread):
    updateProgress = pyqtSignal(int)
    updateText = pyqtSignal(str)

    def __init__(self, files, backup_path):
        super().__init__()
        self.files = files
        self.backup_path = backup_path

    def run(self):
        total_files = len(self.files)
        current_progress = 0

        try:
            with zipfile.ZipFile(self.backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for idx, file_path in enumerate(self.files):
                    if os.path.isdir(file_path):
                        base_folder_name = os.path.basename(file_path)
                        for root, dirs, files in os.walk(file_path):
                            for file in files:
                                file_abs_path = os.path.join(root, file)
                                rel_path = os.path.relpath(file_abs_path, file_path)
                                zipf.write(file_abs_path, os.path.join(base_folder_name, rel_path))
                                self.updateText.emit(f"Скопировано: {file_abs_path}\n")
                    else:
                        zipf.write(file_path, os.path.basename(file_path))
                        self.updateText.emit(f"Скопировано: {file_path}\n")

                    current_progress = int((idx + 1) * 100 / total_files)
                    self.updateProgress.emit(current_progress)
                    self.msleep(100)
        
        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Ошибка при создании ZIP архива: {str(e)}")
            
class BackupThread(QThread):
    updateProgress = pyqtSignal(int)
    updateText = pyqtSignal(str)

    def __init__(self, files, backup_path):
        super().__init__()
        self.files = files
        self.backup_path = backup_path

    def run(self):
        total_files = len(self.files)
        current_progress = 0

        for idx, file_path in enumerate(self.files):
            if os.path.isfile(file_path):
                # Если начальный элемент - файл, копируем его непосредственно в корень целевой папки
                self.CopyFile(file_path, self.backup_path)
            else:
                # Если начальный элемент - папка, используем рекурсивное копирование
                self.CopyItem(file_path, self.backup_path)

            current_progress = int((idx + 1) * 100 / total_files)
            self.updateProgress.emit(current_progress)
            self.msleep(100)

    def CopyItem(self, source_path, target_root):
        if os.path.isdir(source_path):
            # Если исходный элемент - папка, создаем соответствующую папку в целевом каталоге
            source_folder_name = os.path.basename(source_path)
            target_folder_path = os.path.join(target_root, source_folder_name)
            os.makedirs(target_folder_path, exist_ok=True)
            for item in os.listdir(source_path):
                self.CopyItem(os.path.join(source_path, item), target_folder_path)
        else:
            # Если исходный элемент - файл, копируем его в целевую папку
            self.CopyFile(source_path, target_root)

    def CopyFile(self, source_file, target_folder):
        target_file_path = os.path.join(target_folder, os.path.basename(source_file))
        os.makedirs(target_folder, exist_ok=True)
        try:
            shutil.copy2(source_file, target_file_path)
            self.updateText.emit(f"Скопировано: {source_file}\n")
        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Ошибка при копировании файла {source_file}: {str(e)}")

                
class IncrementalCopyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Инкрементная копия")
        self.line_edit = QLineEdit()
        self.browse_button = QPushButton("Выбрать")
        self.start_button = QPushButton("Запуск")
        
        layout = QVBoxLayout(self)
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.line_edit)
        path_layout.addWidget(self.browse_button)
        layout.addLayout(path_layout)
        layout.addWidget(self.start_button)

        self.browse_button.clicked.connect(self.BrowseDirectory)
        self.start_button.clicked.connect(self.StartIncrementalCopy)

    def BrowseDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку", "")
        if directory:
            self.line_edit.setText(directory)

    def StartIncrementalCopy(self):
        target_folder = self.line_edit.text().strip()
        if not target_folder:
            print("Выберите папку для инкрементной копии.")
            return

        # Формируем путь для каталога копии
        copy_dir = os.path.join('C:\\', 'Increment Backup')
        short_bkpdir = time.strftime('%Y%m%d_%H%M')
        bkp_dir = os.path.join(copy_dir, os.path.basename(target_folder), short_bkpdir)

        try:
            os.makedirs(copy_dir, exist_ok=True)  # Создаем основную папку для копий
            os.chdir(copy_dir)

            # Находим время последнего бэкапа для выбранной папки
            last_bkpsubdir = None
            for dr in os.listdir(copy_dir):
                if os.path.isdir(os.path.join(copy_dir, dr)):
                    last_bkpsubdir = dr
                    break

            last_bkptime = os.path.getmtime(os.path.join(copy_dir, last_bkpsubdir)) if last_bkpsubdir else 0

            if last_bkpsubdir != short_bkpdir:
                bkp_dir = os.path.join(copy_dir, os.path.basename(target_folder), short_bkpdir)
                os.makedirs(bkp_dir, exist_ok=True)

                # Рекурсивно копируем только новые файлы и папки
                for root, dirs, files in os.walk(target_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_time = os.path.getmtime(file_path)
                        if file_time > last_bkptime:
                            relative_path = os.path.relpath(file_path, target_folder)
                            dest_path = os.path.join(bkp_dir, relative_path)
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                            shutil.copy2(file_path, dest_path)

                    for subdir in dirs:
                        dir_path = os.path.join(root, subdir)
                        dir_time = os.path.getmtime(dir_path)
                        if dir_time > last_bkptime:
                            relative_path = os.path.relpath(dir_path, target_folder)
                            dest_path = os.path.join(bkp_dir, relative_path)
                            os.makedirs(dest_path, exist_ok=True)

            QMessageBox.information(self, "Информация", "Инкрементная копия завершена успешно.")
        
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при инкрементной копии: {str(e)}")
         


class DifferentialCopyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Дифференциальная копия")
        self.line_edit_diff = QLineEdit()
        self.browsedif_button = QPushButton("Выбрать")
        self.startdif_button = QPushButton("Запуск")
        
        layout = QVBoxLayout(self)
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.line_edit_diff)
        path_layout.addWidget(self.browsedif_button)
        layout.addLayout(path_layout)
        layout.addWidget(self.startdif_button)

        self.browsedif_button.clicked.connect(self.BrowseDirectory)
        self.startdif_button.clicked.connect(self.StartDifferentialCopy)

    def BrowseDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку", "")
        if directory:
            self.line_edit_diff.setText(directory)

    def StartDifferentialCopy(self):
        target_folder = self.line_edit_diff.text().strip()
        if not target_folder:
            print("Выберите папку для дифференциальной копии.")
            return
        

        # Формируем путь для каталога копии
        copy_dir = os.path.join('C:\\', 'Differential Backup')
        bkp_dir = os.path.join(copy_dir, os.path.basename(target_folder))
        short_bkpdir = time.strftime('%Y-%m-%d_%H-%M-%S')
        bkp_dir_with_time = os.path.join(bkp_dir, short_bkpdir)

        try:
            os.makedirs(copy_dir, exist_ok=True)  # Создаем основную папку для копий
            os.makedirs(bkp_dir, exist_ok=True)   # Создаем папку для выбранной папки
            os.chdir(bkp_dir)

            # Находим время последнего бэкапа для выбранной папки
            last_bkp_dir = None
            for dr in os.listdir(bkp_dir):
                if os.path.isdir(os.path.join(bkp_dir, dr)):
                    last_bkp_dir = dr
                    break

            if last_bkp_dir:
                # Рекурсивно собираем информацию о файлах и папках в последнем бэкапе
                last_files = set()
                for root, dirs, files in os.walk(last_bkp_dir):
                    for f in files:
                        last_files.add(os.path.join(root, f))

                # Рекурсивно сравниваем текущую папку с последним бэкапом
                for root, dirs, files in os.walk(target_folder):
                    for f in files:
                        file_path = os.path.join(root, f)
                        if os.path.exists(file_path):
                            last_file_path = os.path.join(last_bkp_dir, os.path.relpath(file_path, target_folder))
                            
                            if last_file_path not in last_files:
                                # Файл был добавлен после последнего бэкапа
                                dest_path = os.path.join(bkp_dir_with_time, os.path.relpath(file_path, target_folder))
                                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                                shutil.copy2(file_path, dest_path)

            else:
                # Первая дифференциальная копия, копируем все файлы
                shutil.copytree(target_folder, bkp_dir_with_time)

            QMessageBox.information(self, "Dat-Back", "Дифференциальная копия завершена успешно.")
        
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при дифференциальной копии: {str(e)}")



def main():
    app = QApplication(sys.argv)
    window = Home()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

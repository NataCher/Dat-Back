from PyQt5.QtCore import Qt, QDir, QStandardPaths
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QTreeView, QFileSystemModel, QPushButton, QFileDialog, QLineEdit, QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QComboBox, QCheckBox, QMessageBox
from PyQt5.QtCore import QItemSelectionModel, QDateTime
from PyQt5.uic import loadUiType
from datetime import datetime
import sys
import shutil
import os
import zipfile

home_ui, _ = loadUiType('C:/Users/natal/Downloads/Dat-Back/ui/pages/home.ui')

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
            self.add_root_folder(folder)

        # Установка модели для QTreeView
        self.treeView.setModel(self.model)
        self.treeView.setRootIndex(self.model.index(""))

        # Установка свойств QTreeView
        self.treeView.setAnimated(False)
        self.treeView.setIndentation(20)
        self.treeView.setSortingEnabled(True)
        self.model.directoryLoaded.connect(self.resize_columns)

        # Подключение события нажатия на кнопку copy_button
        self.btn_copy.clicked.connect(self.copy_files)

    def add_root_folder(self, folder):
        # Получаем индекс для указанной папки
        index = self.model.setRootPath(folder)

    def resize_columns(self):
        for column in range(self.model.columnCount()):
            self.treeView.resizeColumnToContents(column)

    def copy_files(self):
        selected_files = [self.model.filePath(index) for index in self.model.checked_items]
        if not selected_files:
            QMessageBox.warning(self, "Предупреждение", "Не выбраны файлы для резервного копирования.")
            return

        # Запрос имени для резервной копии через диалоговое окно
        backup_name = self.get_backup_name()
        if not backup_name:
            # Используем текущую дату и время в качестве имени файла
            backup_name = "Backup-" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Выбор папки для сохранения резервной копии
        destination_folder = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения", "/")
        if not destination_folder:
            return

        backup_path = os.path.join(destination_folder, backup_name)

        try:
            if self.zip.isChecked():
                # Создание ZIP-архива и добавление выбранных файлов
                backup_path += ".zip"
                with zipfile.ZipFile(backup_path, 'w') as zipf:
                    for file_path in selected_files:
                        file_name = os.path.basename(file_path)
                        zipf.write(file_path, file_name)
                QMessageBox.information(self, "Успех", "Резервная копия успешно создана и упакована в ZIP архив.")
            else:
                # Простое копирование выбранных файлов в указанную папку
                for file_path in selected_files:
                    shutil.copy(file_path, backup_path)
                QMessageBox.information(self, "Успех", "Резервная копия успешно создана.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при создании резервной копии: {str(e)}")

    def get_backup_name(self):
        dialog = NameDialog(self)
        if dialog.exec_():
            backup_name = dialog.edit.text().strip()
            if backup_name:
                return "Backup-" + backup_name
            else:  
                return None
        return None

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
            self.update_check(index, value)
            return True
        return super().setData(index, value, role)

    def update_check(self, index, value):
        if value == Qt.Checked:
            self.checked_items.add(index)
        else:
            self.checked_items.discard(index)
        
        # Рекурсивное изменение состояния дочерних элементов
        self.change_children_folder(index, value)
        
        # Уведомить о изменении
        self.dataChanged.emit(index, index)

    def change_children_folder(self, index, value):
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
                self.change_children_folder(child_index, value)

class NameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.label = QLabel("Введите имя для резервной копии:")
        layout.addWidget(self.label)
        self.edit = QLineEdit()
        layout.addWidget(self.edit) 
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

def main():
    app = QApplication(sys.argv)
    window = Home()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

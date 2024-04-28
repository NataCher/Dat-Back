from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QFileDialog, QMessageBox
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
from datetime import datetime
from PyQt5.QtCore import Qt, QDir
import sys
import shutil
import os
import zipfile
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QFileSystemModel, QTreeView, QMainWindow, QPushButton, QFileDialog, \
    QLineEdit, QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QComboBox, QCheckBox
from PyQt5.QtWidgets import QTreeView, QFileSystemModel

home_ui, _ = loadUiType('C:/Users/natal/Downloads/Dat-Back/ui/pages/home.ui')

class Home(QMainWindow, home_ui):
    def __init__(self, parent=None):
        super(Home, self).__init__(parent)
        self.setupUi(self)

        # Установка модели для QTreeView
        self.model = CheckableDirModel()
        self.model.setRootPath("")
        self.treeView.setModel(self.model)
        self.treeView.setRootIndex(self.model.index(""))

        # Установка свойств QTreeView
        self.treeView.setAnimated(False)
        self.treeView.setIndentation(20)
        self.treeView.setSortingEnabled(True)
        self.model.directoryLoaded.connect(self.resize_columns)

        # Подключение события нажатия на кнопку copy_button
        self.btn_copy.clicked.connect(self.copy_files)

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
            backup_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

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
            return dialog.edit.text()
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
            self.UpdateCheck(index, value)
            return True
        return super().setData(index, value, role)

    def UpdateCheck(self, index, value):
        if value == Qt.Checked:
            self.checked_items.add(index)
        else:
            self.checked_items.discard(index)
        
        # Рекурсивное изменение состояния дочерних элементов
        self.ChangeСhildrenFolder(index, value)
        
        # Уведомить о изменении
        self.dataChanged.emit(index, index)

    def ChangeСhildrenFolder(self, index, value):
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
                self.ChangeСhildrenFolder(child_index, value)


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

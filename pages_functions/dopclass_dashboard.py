from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUiType
import sys
import os



shedule_ui, _ = loadUiType('C:/Users/natal/Downloads/Dat-Back/ui/pages/shedule.ui')
addSheduled_ui, _ = loadUiType('C:/Users/natal/Downloads/Dat-Back/ui/pages/dialog/addShedule.ui')

#====================================================================
#                       Shedule
#====================================================================

class MainShedule(QMainWindow, shedule_ui):
    def __init__(self, parent=None):
        super(MainShedule, self).__init__(parent)
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.addButton.clicked.connect(self.showAddSchedule)
        self.editButton.clicked.connect(self.editSchedule)
        self.deleteButton.clicked.connect(self.deleteSchedule)
        self.startButton.clicked.connect(self.startSchedule)
        self.taskTable.setColumnCount(5)
        self.taskTable.setHorizontalHeaderLabels(["Имя задачи", "Исходный путь", "Конечный путь", "Тип копирования", "Время"])
        self.tasks = []

    def showAddSchedule(self):
        self.scheduleWindow = AddSchedule(self)
        self.scheduleWindow.show()

    def editSchedule(self):
        row = self.taskTable.currentRow()
        if row != -1:
            self.scheduleWindow = AddSchedule(self, self.tasks[row], row)
            self.scheduleWindow.show()

    def deleteSchedule(self):
        row = self.taskTable.currentRow()
        if row != -1:
            self.taskTable.removeRow(row)
            del self.tasks[row]

    def startSchedule(self):
        for task in self.tasks:
            if task['timer'] is None:
                self.startTask(task)

    def startTask(self, task):
        interval = task['interval']
        if task['unit'] == 'Минуты':
            interval *= 60000
        elif task['unit'] == 'Час':
            interval *= 3600000
        elif task['unit'] == 'День':
            interval *= 86400000
        elif task['unit'] == 'Неделя':
            interval *= 604800000

        task['timer'] = QTimer(self)
        task['timer'].timeout.connect(lambda: self.performBackup(task))
        task['timer'].start(interval)

    def performBackup(self, task):
        source = task['source']
        dest = task['dest']
        if task['type'] == 'Полный':
            command = f'cp -r {source}/* {dest}/'
        else:
            command = f'rsync -av {source}/ {dest}/'
        os.system(command)

    def addTask(self, task, row=None):
        if row is None:
            self.tasks.append(task)
            row = self.taskTable.rowCount()
            self.taskTable.insertRow(row)
        else:
            self.tasks[row] = task

        self.taskTable.setItem(row, 0, QTableWidgetItem(task['name']))
        self.taskTable.setItem(row, 1, QTableWidgetItem(task['source']))
        self.taskTable.setItem(row, 2, QTableWidgetItem(task['dest']))
        self.taskTable.setItem(row, 3, QTableWidgetItem(task['type']))
        self.taskTable.setItem(row, 4, QTableWidgetItem(f"{task['interval']} {task['unit']}"))



class AddSchedule(QDialog, addSheduled_ui):
    def __init__(self, main_app, task=None, row=None):
        super(AddSchedule, self).__init__()

        self.main_app = main_app
        self.task = task
        self.row = row
        self.setupUi(self) 
        self.initUI()

    def initUI(self):
        self.sourcePathButton.clicked.connect(self.selectSourcePath)
        self.destPathButton.clicked.connect(self.selectDestPath)
        self.okButton.clicked.connect(self.saveSchedule)
        self.cancelButton.clicked.connect(self.close)
        if self.task:
            self.loadTask()

    def selectSourcePath(self):
        path = QFileDialog.getExistingDirectory(self, "Выберите исходный путь")
        if path:
            self.sourcePathEdit.setText(path)

    def selectDestPath(self):
        path = QFileDialog.getExistingDirectory(self, "Выберите конечный путь")
        if path:
            self.destPathEdit.setText(path)

    def loadTask(self):
        self.taskNameEdit.setText(self.task['name'])
        self.sourcePathEdit.setText(self.task['source'])
        self.destPathEdit.setText(self.task['dest'])
        self.backupTypeCombo.setCurrentText(self.task['type'])
        interval = self.task['interval']
        if self.task['unit'] == 'Минуты':
            self.minutesRadio.setChecked(True)
        elif self.task['unit'] == 'Час':
            self.hoursRadio.setChecked(True)
        elif self.task['unit'] == 'День':
            self.daysRadio.setChecked(True)
        elif self.task['unit'] == 'Неделя':
            self.weeksRadio.setChecked(True)
        self.timeSpinBox.setValue(interval)

    def saveSchedule(self):
        task_name = self.taskNameEdit.text()
        source_path = self.sourcePathEdit.text()
        dest_path = self.destPathEdit.text()
        backup_type = self.backupTypeCombo.currentText()
        interval = self.timeSpinBox.value()
        unit = None
        if self.minutesRadio.isChecked():
            unit = 'Минуты'
        elif self.hoursRadio.isChecked():
            unit = 'Час'
        elif self.daysRadio.isChecked():
            unit = 'День'
        elif self.weeksRadio.isChecked():
            unit = 'Неделя'

        if not task_name or not source_path or not dest_path:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        task = {
            'name': task_name,
            'source': source_path,
            'dest': dest_path,
            'type': backup_type,
            'interval': interval,
            'unit': unit,
            'timer': None
        }
        self.main_app.addTask(task, self.row)
        self.close()










def main():
    app = QApplication(sys.argv)
    window = MainShedule()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    

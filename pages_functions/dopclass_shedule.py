from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUiType
import sys
import os
import json
import shutil
from datetime import datetime
from PyQt5.QtCore import QRunnable, pyqtSignal, QObject

shedule_ui, _ = loadUiType('C:/Users/natal/Downloads/Dat-Back/ui/pages/shedule.ui')
addSheduled_ui, _ = loadUiType('C:/Users/natal/Downloads/Dat-Back/ui/pages/dialog/addShedule.ui')

 
def FormatInterval(interval, unit):
    if unit == 'минут':
        return f"{interval} минут"
    elif unit == 'час':
        interval = int(interval)
        if interval == 1:
            return "1 Час"
        elif 2 <= interval <= 4:
            return f"{interval} Часа"
        else:
            return f"{interval} Часов"
    elif unit == 'Ежедневно' or unit == 'Неделя':
        return interval
    else:
        return interval


class MainShedule(QMainWindow, shedule_ui):
    def __init__(self, parent=None):
        super(MainShedule, self).__init__(parent)

        self.setFixedSize(1038, 869) 

        self.setupUi(self)
        self.initUI()
        self.LoadTasksFromFile()
        self.initBackupSystem()

    def initBackupSystem(self):
        self.thread_pool = QThreadPool()
        self.backup_timer = QTimer(self)

    def initUI(self):
        self.addButton.clicked.connect(self.ShowAddSchedule)
        self.editButton.clicked.connect(self.EditSchedule)
        self.deleteButton.clicked.connect(self.DeleteTask)
        self.startButton.clicked.connect(self.StartScheduleTask)
        self.stopButton.clicked.connect(self.StopSchedule)
        self.taskTable.setColumnCount(6)  
        self.taskTable.setHorizontalHeaderLabels(["Имя задачи", "Исходный путь", "Конечный путь", "Тип бэкапа", "Интервал", "Дата создания"])  # Обновлены заголовки
        self.tasks = []
        self.taskTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.taskTable.resizeColumnsToContents()  

    def ShowSelectedWindow(self):
        button = self.sender()
        result = self.OpenTabFlag(button.text())
        self.SetBtnChecked(button)

        if result[0]:
            self.tabWidget.setCurrentIndex(result[1])
        else:
            tab_title = button.text()
            curIndex = self.tabWidget.addTab(self.menu_btns_dict[button](), tab_title)
            self.tabWidget.setCurrentIndex(curIndex)
            self.tabWidget.setVisible(True)
        
        # Обновление данных таблицы при переключении на вкладку MainShedule
        if isinstance(self.menu_btns_dict[button](), MainShedule):
            self.menu_btns_dict[button]().LoadTasksFromFile()

    def UpdateLog(self, message):
        """Запись сообщения в лог-файл с меткой времени"""
        log_file = 'backup_log.txt'
        with open(log_file, 'a') as log:
            log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
          
    def ShowAddSchedule(self):
        self.scheduleWindow = AddSchedule(self)
        self.scheduleWindow.show()

    def EditSchedule(self):
        if not self.tasks:
            QMessageBox.warning(self, "Предупреждение", "Нет задач для редактирования!")
            return
        selected_row = self.taskTable.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Предупреждение", "Выберите задачу для редактирования!")
            return
        
        self.EditScheduleDialog = AddSchedule(self, selected_row)
        task_data = self.tasks[selected_row] 
        self.EditScheduleDialog.loadTask(task_data)  
        self.EditScheduleDialog.show()

    def DeleteTask(self):
        if not self.tasks:
            QMessageBox.warning(self, "Предупреждение", "Нет задач для удаления!")
            return
        selected_row = self.taskTable.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Предупреждение", "Выберите задачу для удаления!")
            return
        self.taskTable.removeRow(selected_row)
        del self.tasks[selected_row]
        self.saveTasksToFile()

    def StartScheduleTask(self):
        if not self.tasks:
            QMessageBox.warning(self, "Предупреждение", "Нет задач для запуска!")
            return
        for task in self.tasks:
            self.StartTask(task)
        QMessageBox.information(self, "Dat-Back", "Процесс создания бэкапа запущен!")

    def StartTask(self, task):
        try:
            interval = 0  
            if task['unit'] in ['минут', 'час']:
                interval_str = task['interval'].split()[0]  
                interval = int(interval_str)

                if task['unit'] == 'минут':
                    interval *= 60000 
                elif task['unit'] == 'час':
                    interval *= 3600000  

            elif task['unit'] == 'Ежедневно':
                current_time = QTime.currentTime()
                scheduled_time = QTime.fromString(task['interval'], 'HH:mm:ss')
                interval = current_time.secsTo(scheduled_time) * 1000
                if interval < 0:
                    interval += 86400000  # добавить 24 часа в миллисекундах

            elif task['unit'] == 'Неделя':
                days, time_str = task['interval'].rsplit(' ', 1)
                day_names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
                current_day = QDate.currentDate().dayOfWeek() - 1  # 0 - понедельник, 6 - воскресенье
                scheduled_days = [day_names.index(day) for day in days.split(', ')]
                scheduled_time = QTime.fromString(time_str, 'HH:mm:ss')
                current_time = QTime.currentTime()

                interval = float('inf')
                for day in scheduled_days:
                    days_until_scheduled = (day - current_day + 7) % 7
                    time_interval = current_time.secsTo(scheduled_time) * 1000
                    if time_interval < 0 and days_until_scheduled == 0:
                        days_until_scheduled += 7  # следующая неделя
                    total_interval = days_until_scheduled * 86400000 + time_interval
                    if total_interval < interval:
                        interval = total_interval

            if interval <= 0:
                interval = 60000  # умолчание - 1 минута, чтобы избежать проблем

            task['timer'] = QTimer(self)
            task['timer'].timeout.connect(lambda: self.PerformBackup(task))
            task['timer'].start(interval)

        except ValueError as e:
            print(f"Ошибка при обработке интервала: {e}")

    def PerformBackup(self, task):
        source = task['source']
        dest = task['dest']
        backup_type = task['type']

        log_entry = f"Запуск бэкапа для задачи '{task['name']}' в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.UpdateLog(log_entry)  

        backup_task = BackupTask(source, dest, backup_type)
        backup_task.signals.progress.connect(self.UpdateStatus)
        backup_task.signals.progress.connect(self.UpdateLog)  
        backup_task.signals.finished.connect(self.OnBackupFinished)
        backup_task.signals.finished.connect(lambda: self.UpdateLog(f"Бэкап для задачи '{task['name']}' завершен в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"))
        self.thread_pool.start(backup_task)

    def GetBackupInterval(self):
        min_interval = float('inf')
        for task in self.tasks:
            task_interval = self.TimeStrToSeconds(task['interval'])
            if task_interval < min_interval:
                min_interval = task_interval
        return min_interval

    def TimeStrToSeconds(self, time_str):
        try:
            hours, minutes, seconds = map(int, time_str.split(':'))
            total_seconds = hours * 3600 + minutes * 60 + seconds
            return total_seconds
        except ValueError:
            return 0  

    def UpdateStatus(self, message):
        print(message)

    def OnBackupFinished(self):
        print("Бэкап завершен!")

    def addTask(self, task):
        if 'timer' not in task:
            task['timer'] = None

        self.tasks.append(task)
        row = self.taskTable.rowCount()
        self.taskTable.insertRow(row)

        self.taskTable.setItem(row, 0, QTableWidgetItem(task['name']))
        self.taskTable.setItem(row, 1, QTableWidgetItem(task['source']))
        self.taskTable.setItem(row, 2, QTableWidgetItem(task['dest']))
        self.taskTable.setItem(row, 3, QTableWidgetItem(task['type']))

        interval_display = FormatInterval(task['interval'], task['unit'])
        self.taskTable.setItem(row, 4, QTableWidgetItem(interval_display))
        self.taskTable.setItem(row, 5, QTableWidgetItem(task['creation_time']))

        self.taskTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.taskTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.taskTable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def CloseEvent(self, event):
        self.saveTasksToFile()

    def UpdateTask(self, row, task):
        self.tasks[row] = task
        self.taskTable.setItem(row, 0, QTableWidgetItem(task['name']))
        self.taskTable.setItem(row, 1, QTableWidgetItem(task['source']))
        self.taskTable.setItem(row, 2, QTableWidgetItem(task['dest']))
        self.taskTable.setItem(row, 3, QTableWidgetItem(task['type']))

        interval_display = FormatInterval(task['interval'], task['unit'])
        self.taskTable.setItem(row, 4, QTableWidgetItem(interval_display))
        self.taskTable.setItem(row, 5, QTableWidgetItem(task['creation_time']))

    def saveTasksToFile(self):
        tasks_data = []
        for task in self.tasks:
            tasks_data.append({
                'name': task['name'],
                'source': task['source'],
                'dest': task['dest'],
                'type': task['type'],
                'interval': task['interval'],
                'unit': task['unit'],
                'creation_time': task['creation_time']  
            })
        with open('tasks.json', 'w') as f:
            json.dump(tasks_data, f)

    def LoadTasksFromFile(self):
        try:
            with open('tasks.json', 'r') as f:
                tasks_data = json.load(f)
                for task_data in tasks_data:
                    task_data['timer'] = None
                    if 'creation_time' not in task_data:
                        task_data['creation_time'] = 'Нет времени'  
                    self.addTask(task_data)
        except FileNotFoundError:
            pass

    def StopSchedule(self):
        if not self.tasks:
            QMessageBox.warning(self, "Предупреждение", "Нет задач для остановки!")
            return

        for task in self.tasks:
            if task['timer']:
                task['timer'].stop()
                task['timer'] = None
        QMessageBox.information(self, "Dat-Back", "Процесс создания бэкапа остановлен!")


class AddSchedule(QDialog, addSheduled_ui):
    def __init__(self, main_app, row=None):
        super(AddSchedule, self).__init__()
        
        self.setFixedSize(955, 648) 
        self.main_app = main_app
        self.row = row

        self.setupUi(self)
        self.initUI()
       

    def initUI(self):
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())
        self.sourcePathButton.clicked.connect(self.selectSourcePath)
        self.destPathButton.clicked.connect(self.selectDestPath)
        self.okButton.clicked.connect(self.saveSchedule)
        self.cancelButton.clicked.connect(self.close)

        self.radioGroup = QButtonGroup(self)
        self.radioGroup.addButton(self.minutesRadio)
        self.radioGroup.addButton(self.hoursRadio)
        self.radioGroup.addButton(self.daysRadio)
        self.radioGroup.addButton(self.weeksRadio)
        self.radioGroup.buttonClicked.connect(self.updateScheduleOptions)

        self.mondayCheckBox.toggled.connect(lambda: self.singleCheckboxSelection(self.mondayCheckBox))
        self.tuesdayCheckBox.toggled.connect(lambda: self.singleCheckboxSelection(self.tuesdayCheckBox))
        self.wednesdayCheckBox.toggled.connect(lambda: self.singleCheckboxSelection(self.wednesdayCheckBox))
        self.thursdayCheckBox.toggled.connect(lambda: self.singleCheckboxSelection(self.thursdayCheckBox))
        self.fridayCheckBox.toggled.connect(lambda: self.singleCheckboxSelection(self.fridayCheckBox))
        self.saturdayCheckBox.toggled.connect(lambda: self.singleCheckboxSelection(self.saturdayCheckBox))
        self.sundayCheckBox.toggled.connect(lambda: self.singleCheckboxSelection(self.sundayCheckBox))

        self.updateScheduleOptions()

        self.sourcePathEdit.setReadOnly(True)
        self.destPathEdit.setReadOnly(True)

    def updateScheduleOptions(self):
        self.minutesComboBox.setVisible(self.minutesRadio.isChecked())
        self.hoursComboBox.setVisible(self.hoursRadio.isChecked())
        self.dayTimeEdit.setVisible(self.daysRadio.isChecked())
        self.weekDaysGroup.setVisible(self.weeksRadio.isChecked())
        self.weekTimeEdit.setVisible(self.weeksRadio.isChecked())

    def singleCheckboxSelection(self, selected_checkbox):
        checkboxes = [
            self.mondayCheckBox,
            self.tuesdayCheckBox,
            self.wednesdayCheckBox,
            self.thursdayCheckBox,
            self.fridayCheckBox,
            self.saturdayCheckBox,
            self.sundayCheckBox
        ]
        for checkbox in checkboxes:
            if checkbox != selected_checkbox:
                checkbox.setChecked(False)

    def selectSourcePath(self):
        path = QFileDialog.getExistingDirectory(self, "Выберите исходный путь")
        if path:
            self.sourcePathEdit.setText(path)

    def selectDestPath(self):
        path = QFileDialog.getExistingDirectory(self, "Выберите конечный путь")
        if path:
            self.destPathEdit.setText(path)

    def saveSchedule(self):
        task_name = self.taskNameEdit.text()
        source_path = self.sourcePathEdit.text()
        dest_path = self.destPathEdit.text()
        backup_type = self.backupTypeCombo.currentText()

        if self.minutesRadio.isChecked():
            interval = self.minutesComboBox.currentText()
            unit = ''
        elif self.hoursRadio.isChecked():
            interval = self.hoursComboBox.currentText()
            unit = 'Час'
        elif self.daysRadio.isChecked():
            interval = self.dayTimeEdit.time().toString()
            unit = 'Ежедневно'
        elif self.weeksRadio.isChecked():
            days = []
            if self.mondayCheckBox.isChecked():
                days.append('Пн')
            if self.tuesdayCheckBox.isChecked():
                days.append('Вт')
            if self.wednesdayCheckBox.isChecked():
                days.append('Ср')
            if self.thursdayCheckBox.isChecked():
                days.append('Чт')
            if self.fridayCheckBox.isChecked():
                days.append('Пт')
            if self.saturdayCheckBox.isChecked():
                days.append('Сб')
            if self.sundayCheckBox.isChecked():
                days.append('Вс')
            interval = ", ".join(days) + " " + self.weekTimeEdit.time().toString()
            unit = ''

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
            'timer': None,
            'creation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if self.row is None:
            self.main_app.addTask(task)
        else:
            self.main_app.UpdateTask(self.row, task)
        
        self.close()

    def loadTask(self, task):
        self.taskNameEdit.setText(task['name'])
        self.sourcePathEdit.setText(task['source'])
        self.destPathEdit.setText(task['dest'])
        index = self.backupTypeCombo.findText(task['type'])
        if index != -1:
            self.backupTypeCombo.setCurrentIndex(index)
        
        if task['unit'] == '':
            self.minutesRadio.setChecked(True)
            self.minutesComboBox.setCurrentText(task['interval'])
        elif task['unit'] == 'Час':
            self.hoursRadio.setChecked(True)
            self.hoursComboBox.setCurrentText(task['interval'])
        elif task['unit'] == 'Ежедневно':
            self.daysRadio.setChecked(True)
            self.dayTimeEdit.setTime(QTime.fromString(task['interval'], 'HH:mm:ss'))
        else: 
            self.weeksRadio.setChecked(True)
            interval_parts = task['interval'].rsplit(' ', 1)
            days = interval_parts[0].split(', ')
            time = interval_parts[1]
            for day in days:
                if day == 'Пн':
                    self.mondayCheckBox.setChecked(True)
                elif day == 'Вт':
                    self.tuesdayCheckBox.setChecked(True)
                elif day == 'Ср':
                    self.wednesdayCheckBox.setChecked(True)
                elif day == 'Чт':
                    self.thursdayCheckBox.setChecked(True)
                elif day == 'Пт':
                    self.fridayCheckBox.setChecked(True)
                elif day == 'Сб':
                    self.saturdayCheckBox.setChecked(True)
                elif day == 'Вс':
                    self.sundayCheckBox.setChecked(True)

            self.weekTimeEdit.setTime(QTime.fromString(time, 'HH:mm:ss'))


class BackupSignals(QObject):
    progress = pyqtSignal(str)
    finished = pyqtSignal()

class BackupTask(QRunnable):
    def __init__(self, source, dest, backup_type):
        super().__init__()
        self.source = source
        self.dest = dest
        self.backup_type = backup_type
        self.signals = BackupSignals()

    def run(self):
        try:
            self.LogMessage(f"Начало бэкапа: {self.backup_type}")
            if self.backup_type == 'Полный':
                self.FullBackup()
            elif self.backup_type == 'Инкрементальный':
                last_backup_time = self.getLastBackupTime()
                self.IncrementalBackup(last_backup_time)
            elif self.backup_type == 'Дифференциальный':
                last_FullBackup_time = self.getLastFullBackupTime()
                self.DifferentialBackup(last_FullBackup_time)
            
            self.updateBackupMetadata()
            self.signals.progress.emit(f"Бэкап {self.backup_type} завершен")
            self.LogMessage(f"Бэкап завершен: {self.backup_type}")
        except Exception as e:
            self.signals.progress.emit(f"Ошибка при выполнении бэкапа: {e}")
            self.LogMessage(f"Ошибка при выполнении бэкапа: {e}")
        finally:
            try:
                self.signals.finished.emit()
            except RuntimeError as e:
                self.LogMessage(f"Ошибка при завершении бэкапа: {e}")

    def LogMessage(self, message):
        """Запись сообщения в лог-файл с меткой времени"""
        with open('backup_log.txt', 'a') as log:
            log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")


    def FullBackup(self):
        main_dest_path = os.path.join(self.dest, os.path.basename(self.source))
        if not os.path.exists(main_dest_path):
            os.makedirs(main_dest_path)
        
        for item in os.listdir(self.source):
            src_path = os.path.join(self.source, item)
            dest_path = os.path.join(main_dest_path, item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dest_path)

    def IncrementalBackup(self, last_backup_time):
        main_dest_path = os.path.join(self.dest, os.path.basename(self.source))
        if not os.path.exists(main_dest_path):
            os.makedirs(main_dest_path)

        for root, _, files in os.walk(self.source):
            relative_path = os.path.relpath(root, self.source)
            dest_dir = os.path.join(main_dest_path, relative_path)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            for file in files:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest_dir, file)
                if os.path.getmtime(src_file) > last_backup_time:
                    shutil.copy2(src_file, dest_file)

    def DifferentialBackup(self, last_FullBackup_time):
        main_dest_path = os.path.join(self.dest, os.path.basename(self.source))
        if not os.path.exists(main_dest_path):
            os.makedirs(main_dest_path)

        for root, _, files in os.walk(self.source):
            relative_path = os.path.relpath(root, self.source)
            dest_dir = os.path.join(main_dest_path, relative_path)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            for file in files:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest_dir, file)
                if os.path.getmtime(src_file) > last_FullBackup_time:
                    shutil.copy2(src_file, dest_file)

    def updateBackupMetadata(self):
        main_dest_path = os.path.join(self.dest, os.path.basename(self.source))
        metadata_file = os.path.join(main_dest_path, 'backup_metadata.json')
        try:
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = {}

            metadata[self.backup_type] = datetime.now().isoformat()
            metadata['creation_time'] = datetime.now().isoformat() 

            with open(metadata_file, 'w') as f:
                json.dump(metadata, f)
        except Exception as e:
            self.signals.progress.emit(f"Ошибка при обновлении метаданных: {e}")

    def getLastBackupTime(self):
        return self.getBackupTime('incremental')

    def getLastFullBackupTime(self):
        return self.getBackupTime('full')

    def getBackupTime(self, backup_type):
        main_dest_path = os.path.join(self.dest, os.path.basename(self.source))
        metadata_file = os.path.join(main_dest_path, 'backup_metadata.json')
        if not os.path.exists(metadata_file):
            return 0  
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                if backup_type in metadata:
                    return datetime.fromisoformat(metadata[backup_type]).timestamp()
                else:
                    return 0  
        except Exception as e:
            self.signals.progress.emit(f"Ошибка при чтении метаданных: {e}")
            return 0


def main():
    app = QApplication(sys.argv)
    window = MainShedule()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
from PyQt5.uic import loadUiType
import resource_rc

from pages_functions.dopclass_shedule import MainShedule
from pages_functions.dopclass_home import Home

menu_ui, _ = loadUiType('C:/Users/natal/Downloads/Dat-Back/ui/menu.ui')

class MainWindow(QMainWindow, menu_ui):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupUi(self)    
        self.menu_widget.setFixedSize(205, 935)
        self.main_widget.setFixedSize(1044, 935)
        
        self.home_btn = self.pushButton
        self.dashboard_btn = self.pushButton_2

        self.menu_btns_dict = {  
                self.home_btn: Home, 
                self.dashboard_btn: MainShedule, 

        }
        self.ShowHome()

        self.home_btn.clicked.connect(self.ShowSelectedWindow)          
        self.dashboard_btn.clicked.connect(self.ShowSelectedWindow) 
        self.tabWidget.tabCloseRequested.connect(self.CloseTab)

    def onResize(self, event):
        self.menu_widget.setFixedSize(event.size())

    def ShowHome(self):
        result = self.OpenTabFlag(self.home_btn.text())
        self.SetBtnChecked(self.home_btn)

        if result[0]:
            self.tabWidget.setCurrentIndex(result[1])
        else:
            tab_title = self.home_btn.text()
            curIndex = self.tabWidget.addTab(Home(), tab_title)
            self.tabWidget.setCurrentIndex(curIndex)
            self.tabWidget.setVisible(True)

    def SetBtnChecked(self, btn):
        for button in self.menu_btns_dict.keys():
            if button != btn:
                button.setChecked(False)
            else:
                button.setChecked(True)

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

    def OpenTabFlag(self, btn_text):

        open_tab_count = self.tabWidget.count()

        for i in range(open_tab_count):
            tab_title = self.tabWidget.tabText(i)
            if tab_title == btn_text:
                return True, i
            else:
                continue
        return False, -1

    def CloseTab(self, index):
        widget = self.tabWidget.widget(index)
        if isinstance(widget, MainShedule):
            widget.saveTasksToFile()
        self.tabWidget.removeTab(index)

        if self.tabWidget.count() == 0:
            self.toolBox.setCurrentIndex(0)
            self.ShowHome()




def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setFixedSize(1255, 935)
    qr = window.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    window.move(qr.topLeft())

    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

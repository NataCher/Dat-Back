from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import sys
from PyQt5.uic import loadUiType

from pages_functions.dopclass_dashboard import MainDashboard
from pages_functions.dopclass_home import Home
from pages_functions.dopclass_lexus import MainLexus
from pages_functions.dopclass_mazda import MainMazda
from pages_functions.dopclass_toyota import MainToyota
from pages_functions.dopclass_tumbr import MainTumbr
from pages_functions.dopclass_youtube import MainYoutube

menu_ui, _ = loadUiType('C:/Users/natal/Downloads/Dat-Back/ui/menu.ui')

class MainAppReportForm(QMainWindow, menu_ui):
    def __init__(self, parent=None):
        super(MainAppReportForm, self).__init__(parent)
        self.setupUi(self)
        
        self.menu_widget.setFixedSize(138, 829)
        self.main_widget.setFixedSize(1100, 829)
        self.home_btn = self.pushButton
        self.dashboard_btn = self.pushButton_2
        self.toyota_btn = self.pushButton_3
        self.lexus_btn = self.pushButton_4
        self.mazda_btn = self.pushButton_5
        self.youtube_btn = self.pushButton_6
        self.tumbr_btn = self.pushButton_7 

        #====================================================================
        #         CREATE DICT FOR MENU BUTTONS AND TAB WINDOWS
        #====================================================================
        self.menu_btns_dict = {  
                self.home_btn: Home, 
                self.dashboard_btn: MainDashboard, 
                self.toyota_btn: MainToyota,
                self.lexus_btn: MainLexus,
                self.mazda_btn: MainMazda,
                self.youtube_btn: MainYoutube,
                self.tumbr_btn: MainTumbr,
        }


        self.ShowHome()

        self.home_btn.clicked.connect(self.ShowSelectedWindow)          
        self.dashboard_btn.clicked.connect(self.ShowSelectedWindow) 
        self.toyota_btn.clicked.connect(self.ShowSelectedWindow) #examples
        self.lexus_btn.clicked.connect(self.ShowSelectedWindow)  #examples
        self.mazda_btn.clicked.connect(self.ShowSelectedWindow) #examples
        self.toyota_btn.clicked.connect(self.ShowSelectedWindow) #examples
        self.tumbr_btn.clicked.connect(self.ShowSelectedWindow)  #examples


    def onResize(self, event):
        self.menu_widget.setFixedSize(event.size())

    def ShowHome(self):
    
    #function for showing home window
    #return:
      
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
        #set the status of selected button checked and set other buttons status uncheked
        # param btn: button object
        #return:
        for button in self.menu_btns_dict.keys():
            if button != btn:
                button.setChecked(False)
            else:
                button.setChecked(True)

    def ShowSelectedWindow(self):
        #function for showing selected window

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
        #check if selected window showed or not 
        #param btn_text: button text
        #return: bool and index

        open_tab_count = self.tabWidget.count()

        for i in range(open_tab_count):
            tab_title = self.tabWidget.tabText(i)
            if tab_title == btn_text:
                return True, i
            else:
                continue
        return False, -1









def main():
    app = QApplication(sys.argv)
    window = MainAppReportForm()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

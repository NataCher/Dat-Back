from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import sys
import pandas as pd
import psycopg2
from PyQt5.uic import loadUiType

from pages_functions.dopclass_dashboard import MainDashboard
from pages_functions.dopclass_home import MainHome
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



        self.menu_widget.setFixedSize(134, 629)
  





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
                self.home_btn: MainHome, 
                self.dashboard_btn: MainDashboard, 
                self.toyota_btn: MainToyota,
                self.lexus_btn: MainLexus,
                self.mazda_btn: MainMazda,
                self.youtube_btn: MainYoutube,
                self.tumbr_btn: MainTumbr,
        }


        self.show_home_window()


        self.home_btn.clicked.connect(self.show_selected_window)          
        self.dashboard_btn.clicked.connect(self.show_selected_window) 
        self.toyota_btn.clicked.connect(self.show_selected_window)
        self.lexus_btn.clicked.connect(self.show_selected_window)          
        self.mazda_btn.clicked.connect(self.show_selected_window) 
        self.toyota_btn.clicked.connect(self.show_selected_window)
        self.tumbr_btn.clicked.connect(self.show_selected_window)












    def onResize(self, event):
        # При изменении размера окна изменяем размер виджета
        self.menu_widget.setFixedSize(event.size())



    def show_home_window(self):
    
    #function for showing home window
    #return:
      
        result = self.open_tab_flag(self.home_btn.text())
        self.set_btn_checked(self.home_btn)

        if result[0]:
            self.tabWidget.setCurrentIndex(result[1])
        else:
            tab_title = self.home_btn.text()
            curIndex = self.tabWidget.addTab(MainHome(), tab_title)
            self.tabWidget.setCurrentIndex(curIndex)
            self.tabWidget.setVisible(True)

    def set_btn_checked(self, btn):
        #set the status of selected button checked and set other buttons status uncheked
        # param btn: button object
        #return:
        for button in self.menu_btns_dict.keys():
            if button != btn:
                button.setChecked(False)
            else:
                button.setChecked(True)

    def show_selected_window(self):
        #function for showing selected window

        button = self.sender()

        result = self.open_tab_flag(button.text())
        self.set_btn_checked(button)


        if result[0]:
            self.tabWidget.setCurrentIndex(result[1])
        else:
            tab_title = button.text()
            curIndex = self.tabWidget.addTab(self.menu_btns_dict[button](), tab_title)
            self.tabWidget.setCurrentIndex(curIndex)
            self.tabWidget.setVisible(True)  

    def open_tab_flag(self, btn_text):
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

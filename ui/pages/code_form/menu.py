# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\natal\Downloads\Dat-Back\ui\menu.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_menu(object):
    def setupUi(self, menu):
        menu.setObjectName("menu")
        menu.resize(904, 629)
        self.centralwidget = QtWidgets.QWidget(menu)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.menu_widget = QtWidgets.QWidget(self.splitter)
        self.menu_widget.setStyleSheet("background-color: #06162d;\n"
"color: #fff;\n"
"border: none;\n"
"")
        self.menu_widget.setObjectName("menu_widget")
        self.gridLayout = QtWidgets.QGridLayout(self.menu_widget)
        self.gridLayout.setContentsMargins(4, 4, 4, 15)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.toolBox = QtWidgets.QToolBox(self.menu_widget)
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.toolBox.setFont(font)
        self.toolBox.setStyleSheet("#toolBox {\n"
"color: #fff;\n"
"}\n"
"#toolBox::tab {\n"
"padding-left: 5px;\n"
"text-align: left;\n"
"border-radius: 2px;\n"
"}\n"
"\n"
"#toolBox:tab:selected {\n"
"background-color: #2d9cdb;\n"
"font-weight: bold;\n"
"}\n"
"\n"
"#toolBox QPushButton {\n"
"padding: 5px 0px 5px 20px;\n"
"text-align: left;\n"
"border-radius: 3px;\n"
"}\n"
"\n"
"#toolBox QPushButton:hover {\n"
"background-color: #85C1E9\n"
"}\n"
"\n"
"#toolBox QPushButton:checked {\n"
" background-color: #4398D8\n"
"}\n"
"\n"
"")
        self.toolBox.setObjectName("toolBox")
        self.page = QtWidgets.QWidget()
        self.page.setGeometry(QtCore.QRect(0, 0, 310, 507))
        self.page.setObjectName("page")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.page)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton = QtWidgets.QPushButton(self.page)
        self.pushButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton.setCheckable(True)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.page)
        self.pushButton_2.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_2.setCheckable(True)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout.addWidget(self.pushButton_2)
        spacerItem = QtWidgets.QSpacerItem(20, 411, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/Navigation-Menu.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolBox.addItem(self.page, icon, "")
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setGeometry(QtCore.QRect(0, 0, 310, 507))
        self.page_2.setObjectName("page_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.page_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.page_2)
        self.pushButton_3.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_3.setCheckable(True)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout_2.addWidget(self.pushButton_3)
        self.pushButton_4 = QtWidgets.QPushButton(self.page_2)
        self.pushButton_4.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_4.setCheckable(True)
        self.pushButton_4.setObjectName("pushButton_4")
        self.verticalLayout_2.addWidget(self.pushButton_4)
        self.pushButton_5 = QtWidgets.QPushButton(self.page_2)
        self.pushButton_5.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_5.setCheckable(True)
        self.pushButton_5.setObjectName("pushButton_5")
        self.verticalLayout_2.addWidget(self.pushButton_5)
        spacerItem1 = QtWidgets.QSpacerItem(20, 378, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.toolBox.addItem(self.page_2, "")
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setGeometry(QtCore.QRect(0, 0, 310, 507))
        self.page_3.setObjectName("page_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.page_3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.pushButton_6 = QtWidgets.QPushButton(self.page_3)
        self.pushButton_6.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_6.setCheckable(True)
        self.pushButton_6.setObjectName("pushButton_6")
        self.verticalLayout_3.addWidget(self.pushButton_6)
        self.pushButton_7 = QtWidgets.QPushButton(self.page_3)
        self.pushButton_7.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_7.setCheckable(True)
        self.pushButton_7.setObjectName("pushButton_7")
        self.verticalLayout_3.addWidget(self.pushButton_7)
        spacerItem2 = QtWidgets.QSpacerItem(20, 411, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.toolBox.addItem(self.page_3, "")
        self.gridLayout.addWidget(self.toolBox, 0, 0, 1, 1)
        self.main_widget = QtWidgets.QWidget(self.splitter)
        self.main_widget.setObjectName("main_widget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.main_widget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.search_widget = QtWidgets.QWidget(self.main_widget)
        self.search_widget.setStyleSheet("background-color: rgb(176, 176, 176);")
        self.search_widget.setObjectName("search_widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.search_widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_8 = QtWidgets.QPushButton(self.search_widget)
        self.pushButton_8.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.pushButton_8.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/arrow-left.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/arrow-right.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.pushButton_8.setIcon(icon1)
        self.pushButton_8.setCheckable(True)
        self.pushButton_8.setAutoRepeatDelay(300)
        self.pushButton_8.setObjectName("pushButton_8")
        self.horizontalLayout.addWidget(self.pushButton_8)
        spacerItem3 = QtWidgets.QSpacerItem(166, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.gridLayout_2.addWidget(self.search_widget, 0, 0, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(self.main_widget)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setObjectName("tabWidget")
        self.gridLayout_2.addWidget(self.tabWidget, 1, 0, 1, 1)
        self.gridLayout_3.addWidget(self.splitter, 0, 0, 1, 1)
        menu.setCentralWidget(self.centralwidget)

        self.retranslateUi(menu)
        self.toolBox.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(-1)
        self.pushButton_8.toggled['bool'].connect(self.menu_widget.setHidden) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(menu)

    def retranslateUi(self, menu):
        _translate = QtCore.QCoreApplication.translate
        menu.setWindowTitle(_translate("menu", "Dat-Back"))
        self.pushButton.setText(_translate("menu", "Бэкап файлов "))
        self.pushButton_2.setText(_translate("menu", "Расписание"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), _translate("menu", "Меню"))
        self.pushButton_3.setText(_translate("menu", "Toyota"))
        self.pushButton_4.setText(_translate("menu", "Lexus"))
        self.pushButton_5.setText(_translate("menu", "Mazda"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), _translate("menu", "Other_1"))
        self.pushButton_6.setText(_translate("menu", "YouTube"))
        self.pushButton_7.setText(_translate("menu", "Tumbr"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_3), _translate("menu", "Other_2"))
import resource_rc
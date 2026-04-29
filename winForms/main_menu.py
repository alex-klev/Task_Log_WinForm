# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_menu.ui'
#
# Created by: PyQt5 UI code generator 5.14.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(311, 141)
        MainWindow.setMinimumSize(QtCore.QSize(311, 141))
        MainWindow.setMaximumSize(QtCore.QSize(311, 141))
        font = QtGui.QFont()
        font.setPointSize(12)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 291, 121))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.btnEmployesCatalog = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btnEmployesCatalog.setObjectName("btnEmployesCatalog")
        self.gridLayout.addWidget(self.btnEmployesCatalog, 0, 1, 1, 1)
        self.btnBosesCatalog = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btnBosesCatalog.setObjectName("btnBosesCatalog")
        self.gridLayout.addWidget(self.btnBosesCatalog, 0, 0, 1, 1)
        self.btnTasksJournal = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btnTasksJournal.setObjectName("btnTasksJournal")
        self.gridLayout.addWidget(self.btnTasksJournal, 1, 0, 1, 1)
        self.btnDeadlineExpires = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btnDeadlineExpires.setObjectName("btnDeadlineExpires")
        self.gridLayout.addWidget(self.btnDeadlineExpires, 1, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Главное меню"))
        self.btnEmployesCatalog.setText(_translate("MainWindow", "Справочник\n"
"испонителей"))
        self.btnBosesCatalog.setText(_translate("MainWindow", "Справочник\n"
"руководителей"))
        self.btnTasksJournal.setText(_translate("MainWindow", "Журнал\n"
"задач"))
        self.btnDeadlineExpires.setText(_translate("MainWindow", "Истекает\n"
"срок выполнения"))

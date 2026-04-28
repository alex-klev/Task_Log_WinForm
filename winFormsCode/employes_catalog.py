# стандартные
import sys
import datetime as dt
import sqlite3 as sl

# сторонние
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QDesktopWidget, QLineEdit

# свои
from winForms import Ui_EmployesCatalogWindow
# from winForms.employes_catalog import Ui_EmployesCatalogWindow


class EmployesCatalog(QtWidgets.QMainWindow):
    def __init__(self, **kwargs):
        # QtWidgets.QMainWindow.__init__(self)  # Вызываем конструктор базового класса
        # super(EmployesCatalog, self).__init__()  # Вызываем конструктор базового класса
        super().__init__()  # Вызываем конструктор базового класса
        self.ui_employes_catalog = Ui_EmployesCatalogWindow()  # Создаем экземпляр Ui_EmployesCatalogWindow
        self.ui_employes_catalog.setupUi(self)  # Загружаем интерфейс из файла
        
        self.show_new_form = False  # проверка загрузки новой формы
        """
        self.ui_main_menu.btnBosesCatalog.clicked.connect(self.btn_boses_catalog)
        self.ui_main_menu.btnEmployesCatalog.clicked.connect(self.btn_employes_catalog)
        self.ui_main_menu.btnTasksJournal.clicked.connect(self.btn_tasks_journal)
        self.ui_main_menu.btnDeadlineExpires.clicked.connect(self.btn_deadline_expires)
        """
        
    ######################################################
        # Центрирование окна осуществляется с помощью метода center()
        self.center()
    
    def center(self):
        # Используйте метод frameGeometry(), чтобы получить местоположение и размер окна.
        qr = self.frameGeometry()
        # Узнайте центральное расположение экрана монитора, который вы используете.
        cp = QDesktopWidget().availableGeometry().center()
        # Переместите прямоугольное положение окна в центр экрана.
        qr.moveCenter(cp)
        # Переместите текущее окно в положение прямоугольника (qr),
        # которое вы переместили в центр экрана.
        # В результате центр текущего окна совпадает с центром экрана и окно появляется в центре.
        self.move(qr.topLeft())
    ######################################################
    
    def closeEvent(self, event):
        # Если нет процедуры входа в систему, то выходим в главное меню
        if not self.show_new_form:
            # import main # Для избежания циклического импорта
            from main import MainMenu  # Импортируем здесь
            self.start_form_main_menu = MainMenu()
            # self.start_form_main_menu = main.MainMenu()
            self.start_form_main_menu.show()
            # Закрытие формы
            event.accept()
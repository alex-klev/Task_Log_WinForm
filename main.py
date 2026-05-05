# стандартные
import sys
import datetime as dt
import sqlite3 as sl

# сторонние
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QDesktopWidget, QLineEdit

# свои
from winForms import Ui_MainWindow
# from winForms.main_menu import Ui_MainWindow

# from winFormsCode import boses_catalog_actions
from winFormsCode import BosesCatalog
# from winFormsCode import employes_catalog_actions
from winFormsCode import EmployesCatalog
# from winFormsCode import journal_actions
from winFormsCode import Journal

class MainMenu(QtWidgets.QMainWindow):
    def __init__(self, **kwargs):
        # QtWidgets.QMainWindow.__init__(self)  # Вызываем конструктор базового класса
        # super(MainMenu, self).__init__()  # Вызываем конструктор базового класса
        super().__init__() # Вызываем конструктор базового класса
        self.ui_main_menu = Ui_MainWindow()  # Создаем экземпляр Ui_GeneralWindow
        self.ui_main_menu.setupUi(self)  # Загружаем интерфейс из файла
        
        self.show_new_form = False  # проверка загрузки новой формы
        
        self.ui_main_menu.btnBosesCatalog.clicked.connect(self.btn_boses_catalog)
        self.ui_main_menu.btnEmployesCatalog.clicked.connect(self.btn_employes_catalog)
        self.ui_main_menu.btnTasksJournal.clicked.connect(self.btn_journal)
        self.ui_main_menu.btnDeadlineExpires.clicked.connect(self.btn_deadline_expires)
    
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
        # Если не открываем новую форму, то выводим сообщение
        if not self.show_new_form:
            # Создаем диалог вручную, а не через статический метод
            msg_box = QtWidgets.QMessageBox()
            
            msg_box.setWindowTitle("Выход из приложения")
            msg_box.setText("Вы уверены, что хотите выйти из приложения?")
            
            msg_box.setIcon(QtWidgets.QMessageBox.Question)
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            
            # Устанавливаем ту же иконку, что и у главного окна
            if self.windowIcon() and not self.windowIcon().isNull():
                msg_box.setWindowIcon(self.windowIcon())
            
            # Меняем текст кнопок ДО показа диалога
            msg_box.button(QtWidgets.QMessageBox.Yes).setText("Да")
            msg_box.button(QtWidgets.QMessageBox.No).setText("Нет")
            
            # Показываем диалог и получаем результат
            result = msg_box.exec_()
            
            if result == QtWidgets.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
    
    def btn_boses_catalog(self) -> None:
        """Запуск формы каталога начальников"""
        self.show_new_form = True  # Установка значения загрузки новой формы
        self.start_form_boses_catalog = BosesCatalog()  # Подключаемся к классу BossCatalog
        # self.start_form_boses_catalog = boses_catalog_actions.BosesCatalog()  # Подключаемся к классу BossCatalog
        # self.start_form_boses_catalog.load_all_data_persons()  # Загружаем данные
        self.start_form_boses_catalog.show()  # Запускаем форму boses_catalog
        self.close()  # Закрываем текущую форму
        
    def btn_employes_catalog(self) -> None:
        """Запуск формы каталога исполнителей"""
        self.show_new_form = True  # Установка значения загрузки новой формы
        self.start_form_employes_catalog = EmployesCatalog()  # Подключаемся к классу EmployesCatalog
        # self.start_form_boss_catalog = employes_catalog_actions.EmployesCatalog()  # Подключаемся к классу EmployesCatalog
        # self.start_form_employes_catalog.load_all_data_persons()  # Загружаем данные
        self.start_form_employes_catalog.show()  # Запускаем форму employes_catalog
        self.close()  # Закрываем текущую форму
    
    def btn_journal(self) -> None:
        """Запуск формы журнала задач"""
        self.show_new_form = True  # Установка значения загрузки новой формы
        self.start_form_journal = Journal()  # Подключаемся к классу TasksJournal
        # self.start_form_journal = journal_actions.Journal()  # Подключаемся к классу TasksJournal
        # self.start_form_journal.load_all_data_persons()  # Загружаем данные
        self.start_form_journal.show()  # Запускаем форму journal
        self.close()  # Закрываем текущую форму
    
    def btn_deadline_expires(self) -> None:
        """Запуск формы задач, где истекает срок выполнения"""
        #! self.show_new_form = True  # Установка значения загрузки новой формы
        # self.start_form_deadline_expires = DeadlineExpires()  # Подключаемся к классу DeadlineExpires
        #! self.start_form_deadline_expires = deadline_expires.DeadlineExpires()  # Подключаемся к классу DeadlineExpires
        # self.start_form_deadline_expires.load_all_data_persons()  # Загружаем данные
        #! self.start_form_deadline_expires.show()  # Запускаем форму persons
        #! self.close()  # Закрываем текущую форму


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())
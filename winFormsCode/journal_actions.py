# стандартные
import sys
import datetime as dt
import time

# сторонние
from PyQt5 import QtWidgets, QtGui # QtGui создает объект цвета в PyQt5 с использованием компонентов RGB 
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QMessageBox, QDesktopWidget, QLineEdit, QTableView, QAbstractItemView, QHeaderView
from PyQt5.QtGui import QStandardItemModel, QStandardItem

# свои
from winForms import Ui_JournalWindow
# from winForms.journal import Ui_JournalWindow

from dbCode import JournalDb
# import dbCode.db_actions as db_actions


class Journal(QtWidgets.QMainWindow):
    def __init__(self, **kwargs):
        # QtWidgets.QMainWindow.__init__(self)  # Вызываем конструктор базового класса
        # super(BosesCatalog, self).__init__()  # Вызываем конструктор базового класса
        super().__init__()  # Вызываем конструктор базового класса
        self.ui_journal = Ui_JournalWindow()  # Создаем экземпляр Ui_JournalWindow
        self.ui_journal.setupUi(self)  # Загружаем интерфейс из файла
        
        self.show_new_form = False  # проверка загрузки новой формы
        
        self.setSql = ""
        
        """
        self.ui_persons.btnFilterOn.clicked.connect(self.load_data_filter)  # Фильтрация
        self.ui_persons.btnFilterOff.clicked.connect(self.load_data_no_filter)  # Отключить фильтрацию
        """
        
        """
        self.ui_journal.btnInsert.clicked.connect(self.add_data_to_db)  # Добавить запись в таблицу
        self.ui_journal.btnUpdate.clicked.connect(self.update_data_in_db)  # Обновить запись в таблице
        self.ui_journal.btnDelete.clicked.connect(self.delete_data_from_db)  # Удалить запись из таблицы
        self.ui_journal.btnSave.clicked.connect(self.save_data_in_db)  # Сохранить запись в таблице
        self.ui_journal.btnCancel.clicked.connect(self.cancel)  # Отменить запись из таблицы
        
        self.ui_journal.tableView.clicked.connect(self.on_cell_clicked)  # Клик по ячейке
        self.ui_journal.tableView.activated.connect(self.on_cell_activated)  # Данные в выбранной строке таблицы
        # self.ui_journal.tableView.pressed.connect(self.on_cell_pressed)  # Данные в выбранной строке таблицы
        
        self.ui_journal.lineEdit.setEnabled(False)
        """
        
        # Создаём модель таблицы
        table_model = TableModel(
            ui=self.ui_journal, # Передаём ссылку на ui_journal
            parent_window=self  # Передаём ссылку на главное окно
        )
        table_model.create_model_table()  
        
        # Загружаем данные в таблицу
        self.load_data_db()
        
        # Для PyQt5/PyQt6
        #self.ui_journal.tableView.setStyleSheet("""
        #    QTableView::item:selected {
        #        background-color: #D3D3D3;  /* Светло-серый цвет */
        #   }
        #""")
        
        
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
    
    def get_current_datetime(self):
        # return dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def load_data_db(self):
        try:
            # TODO Загружаем данные теста исполнителя
            journal = JournalDb()
            data = journal.load_data()
        except Exception as e:
            QMessageBox.warning(self, 'Внимание', "Ошибка при загрузке данных {e}".format(e=e))
            print("Ошибка при загрузке данных {e}".format(e=e))
            return
        else:
            if not data or data == [('',)]:
                #! ###########################################
                #! ### Удаляем последнюю запись в таблице ####
                """
                model = self.ui_employes_catalog.tableView.model()
                if model and model.rowCount() > 0:
                    last_row = model.rowCount() - 1
                    model.removeRow(last_row)
                """
                
                model = self.ui_journal.tableView.model()
                if model and model.rowCount() > 0:
                    model.removeRow(model.rowCount() - 1)
                #! ###########################################
                #! ###########################################
            else:
                def transform_data(row):
                    """Функция для преобразования строки в словарь"""
                    return {
                        'data_id': row[0],
                        'task': row[1],
                        'note': row[2],
                        'date_start_task': row[3],
                        'date_end_task': row[4],
                        'time_end_task': row[5],
                        'boss_fio': row[6],
                        'employee_fio': row[7],
                        'days_difference': row[8],
                        'done': row[9],
                        "boss_id": row[10],
                        "employee_id": row[11]
                    }
                
                # Используем генераторное выражение
                # data_generator = (transform_data(row) for row in budget_data)
                
                # Или с использованием map (чуть быстрее)
                data_generator = map(transform_data, data)
                
                # print(list(data_generator))
                # print('data', data)
                
                self.load_table(list(data_generator))
                # return (list(data_generator))
    
    def load_table(self, data):
        # Если данных нет, очищаем таблицу и выходим
        if not data: 
            self.ui_journal.tableView.setModel(None)
            return
        
        # 1. Создаём модель: строки = кол-во записей, столбцы = 10
        model = QStandardItemModel(len(data), 10)
        model.setHorizontalHeaderLabels([
            "data_id", 
            "Задание", 
            "Примечание", 
            "Начало\nвыполнения", 
            "Завершение\nвыполнения",
            "Завершить к",
            "Руководитель", 
            "Исполнитель", 
            "days_difference",
            "done",
            "boss_id",
            "employee_id"
        ])
        
        # 2. Заполняем модель данными
        for row_idx, row_data in enumerate(data):
            # data_id (скрытый)
            model.setItem(row_idx, 0, QStandardItem(str(row_data.get('data_id', ''))))
            
            days_diff = str(row_data.get('days_difference', '0'))  # Берем значение Дни до завершения задачи (days_difference)
            done = str(row_data.get('done', '0'))  # Берем значение Отметка о завершении
            
            item_task = QStandardItem(str(row_data.get('task', '')))  # Задание
            item_note = QStandardItem(str(row_data.get('note', '')))  # Примечание
            item_date_start_task = QStandardItem(str(row_data.get('date_start_task', '')))  # Начало выполнения
            item_date_end_task = QStandardItem(str(row_data.get('date_end_task', '')))  # Завершение выполнения
            item_time_end_task = QStandardItem(str(row_data.get('time_end_task', '')))  # Завершить к
            item_boss_fio = QStandardItem(str(row_data.get('boss_fio', '')))  # Руководитель
            item_employee_fio = QStandardItem(str(row_data.get('employee_fio', '')))  # Исполнитель
            
            if 21.0 <= float(days_diff) <= 30.0:
                item_task.setForeground(QtGui.QColor("darkorange"))
                item_note.setForeground(QtGui.QColor("darkorange"))
                item_date_start_task.setForeground(QtGui.QColor("darkorange"))
                item_date_end_task.setForeground(QtGui.QColor("darkorange"))
                item_time_end_task.setForeground(QtGui.QColor("darkorange"))
                item_boss_fio.setForeground(QtGui.QColor("darkorange"))
                item_employee_fio.setForeground(QtGui.QColor("darkorange"))
            elif 10.0 <= float(days_diff) <= 20.0:
                item_task.setForeground(QtGui.QColor("red"))
                item_note.setForeground(QtGui.QColor("red"))
                item_date_start_task.setForeground(QtGui.QColor("red"))
                item_date_end_task.setForeground(QtGui.QColor("red"))
                item_time_end_task.setForeground(QtGui.QColor("red"))
                item_boss_fio.setForeground(QtGui.QColor("red"))
                item_employee_fio.setForeground(QtGui.QColor("red"))
            elif int(done) == 1:
                item_task.setForeground(QtGui.QColor("darkgreen"))
                item_note.setForeground(QtGui.QColor("darkgreen"))
                item_date_start_task.setForeground(QtGui.QColor("darkgreen"))
                item_date_end_task.setForeground(QtGui.QColor("darkgreen"))
                item_time_end_task.setForeground(QtGui.QColor("darkgreen"))
                item_boss_fio.setForeground(QtGui.QColor("darkgreen"))
                item_employee_fio.setForeground(QtGui.QColor("darkgreen"))
            
            
            # Задание
            # model.setItem(row_idx, 1, QStandardItem(str(row_data.get('task', ''))))
            model.setItem(row_idx, 1, item_task)
            
            # Примечание
            # model.setItem(row_idx, 2, QStandardItem(str(row_data.get('note', ''))))
            model.setItem(row_idx, 2, item_note)
            
            # Начало выполнения
            # model.setItem(row_idx, 3, QStandardItem(str(row_data.get('date_start_task', ''))))
            model.setItem(row_idx, 3, item_date_start_task)
            
            # Завершение выполнения
            # model.setItem(row_idx, 4, QStandardItem(str(row_data.get('date_end_task', ''))))
            model.setItem(row_idx, 4, item_date_end_task)
            
            # Завершить к
            # model.setItem(row_idx, 5, QStandardItem(str(row_data.get('time_end_task', ''))))
            model.setItem(row_idx, 5, item_time_end_task)
            
            # Руководитель
            # model.setItem(row_idx, 6, QStandardItem(str(row_data.get('boss_fio', ''))))
            model.setItem(row_idx, 6, item_boss_fio)
            
            # Исполнитель
            # model.setItem(row_idx, 7, QStandardItem(str(row_data.get('employee_fio', ''))))
            model.setItem(row_idx, 7, item_employee_fio)
            
            # Дни до завершения задачи (days_difference)
            # model.setItem(row_idx, 8, QStandardItem(str(row_data.get('days_difference', ''))))
            model.setItem(row_idx, 8, QStandardItem(days_diff))
            
            # Отметка о завершении
            # model.setItem(row_idx, 9, QStandardItem(str(row_data.get('done', ''))))
            model.setItem(row_idx, 9, QStandardItem(done))
            
            # boss_id
            model.setItem(row_idx, 10, QStandardItem(str(row_data.get('boss_id', ''))))
            
            # employee_id
            model.setItem(row_idx, 11, QStandardItem(str(row_data.get('employee_id', ''))))
            
            """
            # Сумма (с условным форматированием)
            amount = str(row_data.get('amount', '0'))
            item_amount = QStandardItem()
            row_type = row_data.get('type', '')
            
            if row_type == 'income':
                item_amount.setText('+{amount}'.format(amount=amount))
                item_amount.setForeground(QtGui.QColor("green"))
            elif row_type == 'expense':
                item_amount.setText('-{amount}'.format(amount=amount))
                item_amount.setForeground(QtGui.QColor("red"))
            else:
                item_amount.setText(amount)
            
            model.setItem(row_idx, 3, item_amount)
            """
            
            # Опционально: выравнивание по центру для красоты
            for col in range(12):
                model.item(row_idx, col).setTextAlignment(Qt.AlignCenter)
        
        # 3. Привязываем модель к tableView
        self.ui_journal.tableView.setModel(model)
        
        # 4. Скрываем столбцы data_id (индекс 0), days_difference (индекс 8), done (индекс 9), boss_id (индекс 10), employee_id (индекс 11)
        self.ui_journal.tableView.setColumnHidden(0, True)
        self.ui_journal.tableView.setColumnHidden(8, True)
        self.ui_journal.tableView.setColumnHidden(9, True)
        self.ui_journal.tableView.setColumnHidden(10, True)
        self.ui_journal.tableView.setColumnHidden(11, True)
        
        # 5. Запрещаем редактирование ячеек
        # self.ui_journal.tableViewO.setEditTriggers(QTableView.NoEditTriggers)  # QTableView наследуется от QAbstractItemView
        self.ui_journal.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # 6. Опционально: автоматическая подгонка ширины столбцов под содержимое
        header = self.ui_journal.tableView.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
    
    
    
    
    
    
    def cell_clicked_table_last_operations(self, row=None, column=None) -> None:
        """Данные в выбранной строке таблицы"""
        # row - принимает координаты строки
        # column - принимает координаты столбца
        # print("Row %d and Column %d was clicked" % (row, column))
        
        """
        # Пример
        comboBox.addItem("Красный", "red")    # данные = "red"
        comboBox.addItem("Зеленый", "green")  # данные = "green"
        comboBox.addItem("Синий", "blue")     # данные = "blue"
        
        # Поиск
        index = comboBox.findData("green")    # вернет 1
        index = comboBox.findData("yellow")   # вернет -1 (не найдено)
        
        # Поиск
        index = comboBox.findText("Зеленый")   # вернет 1
        index = comboBox.findText("зеленый")   # вернет -1 (регистр важен!)
        index = comboBox.findText("Зеленый", Qt.MatchFlag.MatchContains)  # частичное совпадение
        
        # Флаги для findText
        comboBox.findText("зел", Qt.MatchFlag.MatchStartsWith)     # начинается с "зел"
        comboBox.findText("ен", Qt.MatchFlag.MatchContains)        # содержит "ен"
        comboBox.findText("ЗЕЛЕНЫЙ", Qt.MatchFlag.MatchCaseSensitive)  # с учетом регистра
        
        # Флаги для findData (обычно используется только точное совпадение)
        comboBox.findData("green", Qt.MatchFlag.MatchExactly)      # точное совпадение
        """
        
        # TODO Тип цели
        # Получаем значение из таблицы ('income' или 'expense')
        if row is not None:
            value = self.ui_budget_by_categories.tableLastOperations.item(row, 4).text()
        else:
            value = self.ui_budget_by_categories.tableLastOperations.item(self.row, 4).text()
        
        # Находим индекс элемента с нужным значением data
        index = self.ui_budget_by_categories.comboBoxIncExpBudget.findData(value)
        
        # Устанавливаем найденный индекс (если найден)
        if index >= 0:
            # self.ui_budget_by_categories.comboBoxIncExpBudget.setCurrentIndex(index)
            self.data_IncExpBudget = index
        
        # TODO Сумма
        # self.ui_budget_by_categories.doubleSpinBoxSumBudget.setValue(abs(float(self.ui_budget_by_categories.tableLastOperations.item(row, 3).text().replace(' ', ''))))
        if row is not None:
            self.data_SumBudget = abs(float(self.ui_budget_by_categories.tableLastOperations.item(row, 3).text().replace(' ', '')))
        else:
            self.data_SumBudget = abs(float(self.ui_budget_by_categories.tableLastOperations.item(self.row, 3).text().replace(' ', '')))
        
        # TODO Категория
        # self.ui_budget_by_categories.lineEditCategoryBudget.setText(self.ui_budget_by_categories.tableLastOperations.item(row, 2).text())
        if row is not None:
            self.data_CategoryBudget = self.ui_budget_by_categories.tableLastOperations.item(row, 2).text()
        else:
            self.data_CategoryBudget = self.ui_budget_by_categories.tableLastOperations.item(self.row, 2).text()
        
        # TODO Дата
        if row is not None:
            slist = self.ui_budget_by_categories.tableLastOperations.item(row, 1).text().split(".")
        else:
            slist = self.ui_budget_by_categories.tableLastOperations.item(self.row, 1).text().split(".")
        sdate = dt.date(int(slist[2]), int(slist[1]), int(slist[0]))
        # self.ui_budget_by_categories.dateEditBudget.setDate(QDate(sdate))
        self.data_DateBudget = sdate
        # self.ui_budget_by_categories.dateEditBudget.setDate(QDate(2023, 7, 25))
        
        """
        print(self.ui_budget_by_categories.tableLastOperations.item(row, 0).text())
        print(self.ui_budget_by_categories.tableLastOperations.item(row, 1).text())
        print(self.ui_budget_by_categories.tableLastOperations.item(row, 2).text())
        print(self.ui_budget_by_categories.tableLastOperations.item(row, 3).text())
        print(self.ui_budget_by_categories.tableLastOperations.item(row, 4).text())
        """
    
    def cell_activated_table_last_operations(self, row=None, column=None) -> None:
        """Данные в выбранной строке таблицы"""
        # row - принимает координаты строки
        # column - принимает координаты столбца
        # print("Row %d and Column %d was clicked" % (row, column))
        
        # TODO Тип цели
        # Получаем значение из таблицы ('income' или 'expense')
        if row is not None:
            value = self.ui_budget_by_categories.tableLastOperations.item(row, 4).text()
        else:
            value = self.ui_budget_by_categories.tableLastOperations.item(self.row, 4).text()
        
        # Находим индекс элемента с нужным значением data
        index = self.ui_budget_by_categories.comboBoxIncExpBudget.findData(value)
        
        # Устанавливаем найденный индекс (если найден)
        if index >= 0:
            # self.ui_budget_by_categories.comboBoxIncExpBudget.setCurrentIndex(index)
            self.data_IncExpBudget = index
        
        # TODO Сумма
        # self.ui_budget_by_categories.doubleSpinBoxSumBudget.setValue(abs(float(self.ui_budget_by_categories.tableLastOperations.item(row, 3).text().replace(' ', ''))))
        if row is not None:
            self.data_SumBudget = abs(float(self.ui_budget_by_categories.tableLastOperations.item(row, 3).text().replace(' ', '')))
        else:
            self.data_SumBudget = abs(float(self.ui_budget_by_categories.tableLastOperations.item(self.row, 3).text().replace(' ', '')))
        
        # TODO Категория
        if row is not None:
            self.data_CategoryBudget = self.ui_budget_by_categories.tableLastOperations.item(row, 2).text()
        else:
            self.data_CategoryBudget = self.ui_budget_by_categories.tableLastOperations.item(self.row, 2).text()
        
        # TODO Дата
        if row is not None:
            slist = self.ui_budget_by_categories.tableLastOperations.item(row, 1).text().split(".")
        else:
            slist = self.ui_budget_by_categories.tableLastOperations.item(self.row, 1).text().split(".")
        sdate = dt.date(int(slist[2]), int(slist[1]), int(slist[0]))
        # self.ui_budget_by_categories.dateEditBudget.setDate(QDate(sdate))
        self.data_DateBudget = sdate
        # self.ui_budget_by_categories.dateEditBudget.setDate(QDate(2023, 7, 25))
    
    def cell_changed_table_last_operations(self, row=None, column=None) -> None:
        """Данные в выбранной строке таблицы"""
        # row - принимает координаты строки
        # column - принимает координаты столбца
        # print("Row %d and Column %d was clicked" % (row, column))
        
        # Без try возникает ошибка при удалении единственной (последней) записи из таблицы
        try:
            # TODO Тип цели
            # Получаем значение из таблицы ('income' или 'expense')
            if row is not None:
                value = self.ui_budget_by_categories.tableLastOperations.item(row, 4).text()
            else:
                value = self.ui_budget_by_categories.tableLastOperations.item(self.row, 4).text()
            
            # Находим индекс элемента с нужным значением data
            index = self.ui_budget_by_categories.comboBoxIncExpBudget.findData(value)
            
            # Устанавливаем найденный индекс (если найден)
            if index >= 0:
                # self.ui_budget_by_categories.comboBoxIncExpBudget.setCurrentIndex(index)
                self.data_IncExpBudget = index
            
            # TODO Сумма
            # self.ui_budget_by_categories.doubleSpinBoxSumBudget.setValue(abs(float(self.ui_budget_by_categories.tableLastOperations.item(row, 3).text().replace(' ', ''))))
            if row is not None:
                self.data_SumBudget = abs(float(self.ui_budget_by_categories.tableLastOperations.item(row, 3).text().replace(' ', '')))
            else:
                self.data_SumBudget = abs(float(self.ui_budget_by_categories.tableLastOperations.item(self.row, 3).text().replace(' ', '')))
            
            # TODO Категория
            # self.ui_budget_by_categories.lineEditCategoryBudget.setText(self.ui_budget_by_categories.tableLastOperations.item(row, 2).text())
            if row is not None:
                self.data_CategoryBudget = self.ui_budget_by_categories.tableLastOperations.item(row, 2).text()
            else:
                self.data_CategoryBudget = self.ui_budget_by_categories.tableLastOperations.item(self.row, 2).text()
            
            # TODO Дата
            if row is not None:
                slist = self.ui_budget_by_categories.tableLastOperations.item(row, 1).text().split(".")
            else:
                slist = self.ui_budget_by_categories.tableLastOperations.item(self.row, 1).text().split(".")
            sdate = dt.date(int(slist[2]), int(slist[1]), int(slist[0]))
            # self.ui_budget_by_categories.dateEditBudget.setDate(QDate(sdate))
            self.data_DateBudget = sdate
            # self.ui_budget_by_categories.dateEditBudget.setDate(QDate(2023, 7, 25))
        except Exception as e:
            return
    
    def cell_pressed_table_last_operations(self, row, column) -> None:
        """Данные в выбранной строке таблицы"""
        # row - принимает координаты строки
        # column - принимает координаты столбца
        # print("Row %d and Column %d was clicked" % (row, column))
        
        ## item = self.table.itemAt(row, column)        
        # print(self.ui_persons.tableWidget.item(row, column).text())  # значение в ячейке
        # print(self.ui_persons.tableWidget.item(row, 0).text())
        ## self.ID = item.text()
        #person_id = self.ui_persons.tableWidget.item(current_row, 0).text()
        pass
    
    


class TableModel:
    # Для Astra Linux 1.6 (Python 3.5.3)
    def __init__(self, ui, parent_window, **kwargs):
        self.ui_journal = ui  # передаём ссылку на UI (type: Ui_JournalWindow)
        self.parent_window = parent_window  # Сохраняем ссылку на родительское окно
    
    """
    def __init__(self, ui: Ui_JournalWindow, parent_window, **kwargs):  # Добавлена аннотация типа (аннотация - подсказки для разработчиков)
        self.ui_journal: Ui_JournalWindow = ui  # Аннотация типа для атрибута и передаём ссылку на UI (аннотация - подсказки для разработчиков)
        self.parent_window = parent_window  # Сохраняем ссылку на родительское окно
    """
    
    def create_model_table(self):
        """Создаём модель таблицы"""
        
        # 1. Уже есть модель, связанная с tableView
        model = self.ui_journal.tableView.model()
        
        # 2. Устанавливаем заголовки
        if model is not None:
            headers = [
                "data_id", 
                "Задание",
                "Примечание",
                "Начало\nвыполнения",
                "Завершение\nвыполнения",
                "Завершить к",
                "Руководитель",
                "Исполнитель",
                "days_difference",
                "done",
                "boss_id",
                "employee_id"
            ]
            model.setHorizontalHeaderLabels(headers)
        else:
            # 1. Создаем модель
            model = QStandardItemModel()
            
            # 2. Устанавливаем заголовки
            headers = [
                "data_id", 
                "Задание",
                "Примечание",
                "Начало\nвыполнения",
                "Завершение\nвыполнения",
                "Завершить к",
                "Руководитель",
                "Исполнитель",
                "days_difference",
                "done",
                "boss_id",
                "employee_id"
            ]
            model.setHorizontalHeaderLabels(headers)
            
            # 3. Присваиваем модель таблице
            self.ui_journal.tableView.setModel(model)
            
            # 3. Присваиваем модель таблице
            self.ui_journal.tableView.setModel(model)
            
            # 4. Скрываем столбцы data_id (индекс 0), days_difference (индекс 8), done (индекс 9), boss_id (индекс 10), employee_id (индекс 11)
            self.ui_journal.tableView.setColumnHidden(0, True)
            self.ui_journal.tableView.setColumnHidden(8, True)
            self.ui_journal.tableView.setColumnHidden(9, True)
            self.ui_journal.tableView.setColumnHidden(10, True)
            self.ui_journal.tableView.setColumnHidden(11, True)
            
            # 5. Запрещаем редактирование ячеек
            # self.ui_journal.tableView.setEditTriggers(QTableView.NoEditTriggers)  # QTableView наследуется от QAbstractItemView
            self.ui_journal.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
            
            # 6. Опционально: автоматическая подгонка ширины столбцов под содержимое
            header = self.ui_journal.tableView.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeToContents)
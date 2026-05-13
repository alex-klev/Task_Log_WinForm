# стандартные
import sys
import datetime as dt
import time
from dateutil.relativedelta import relativedelta

# сторонние
from PyQt5 import QtWidgets, QtGui # QtGui создает объект цвета в PyQt5 с использованием компонентов RGB 
from PyQt5.QtCore import Qt, QDate, QTime, QSortFilterProxyModel
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
        
        self.ui_journal.groupBoxElements.setEnabled(False)
        # self.ui_journal.groupBoxElements.enabled = False
        
        self.ui_journal.btnFilterOn.clicked.connect(self.load_data_db)
        
        self.ui_journal.lineEditFilterTask.textChanged.connect(self.on_filter_text_changed_task)  # Фильтрация
        self.ui_journal.lineEditFilterEmploye.textChanged.connect(self.on_filter_text_changed_employe)  # Фильтрация
        
        self.ui_journal.btnInsert.clicked.connect(self.add_data_to_db)  # Добавить запись в таблицу
        self.ui_journal.btnUpdate.clicked.connect(self.update_data_in_db)  # Обновить запись в таблице
        self.ui_journal.btnDelete.clicked.connect(self.delete_data_from_db)  # Удалить запись из таблицы
        self.ui_journal.btnSave.clicked.connect(self.save_data_in_db)  # Сохранить запись в таблице
        self.ui_journal.btnCancel.clicked.connect(self.cancel)  # Отменить запись из таблицы
        
        self.ui_journal.tableView.clicked.connect(self.on_cell_clicked)  # Клик по ячейке
        self.ui_journal.tableView.activated.connect(self.on_cell_activated)  # Данные в выбранной строке таблицы
        # self.ui_journal.tableView.pressed.connect(self.on_cell_pressed)  # Данные в выбранной строке таблицы
        """
        self.ui_journal.lineEdit.setEnabled(False)
        """
        
        self.ui_journal.plainTextEditTask.textChanged.connect(self.limit_text_edit_task)
        self.ui_journal.plainTextEditNote.textChanged.connect(self.limit_text_edit_note)
        
        self.ui_journal.checkBox_2.toggled.connect(self.check_time)
        # self.ui_journal.checkBox_2.clicked.connect(self.check_time)
        
        #! ### Ф.И.О. руководителя ###
        # Создаём объект BossFIO один раз (данные загрузятся внутри)
        self.boss_fio = BossFIO(ui=self.ui_journal, parent_window=self)
        # Подключаем сигнал к его методу
        self.ui_journal.lineEditFindBossFio.editingFinished.connect(self.boss_fio.id_person_show)
        self.ui_journal.comboBoxBoss.setCurrentText("нет данных")
        #! ###########################
        
        #! ### Ф.И.О. исполнителя ###
        # Создаём объект EmployeFIO один раз (данные загрузятся внутри)
        self.employe_fio = EmployeFIO(ui=self.ui_journal, parent_window=self)
        # Подключаем сигнал к его методу
        self.ui_journal.lineEditFindEmployeFio.editingFinished.connect(self.employe_fio.id_person_show)
        self.ui_journal.comboBoxEmploye.setCurrentText("нет данных")
        #! ###########################
        
        # Создаём модель таблицы
        table_model = TableModel(
            ui=self.ui_journal, # Передаём ссылку на ui_journal
            parent_window=self  # Передаём ссылку на главное окно
        )
        table_model.create_model_table()  
        
        # Установка диапазон дат 
        self.set_dates_dynamic()
        
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
    
    def set_dates(self):
        """Диапазон дат"""
        # Текущая дата
        today = QDate.currentDate()
        
        # Первое число текущего месяца
        first_day = QDate(today.year(), today.month(), 1)
        self.ui_journal.dateEditFrom.setDate(first_day)
        
        # Последнее число текущего месяца
        # Берём первый день следующего месяца и вычитаем один день
        if today.month() == 12:
            next_month_first = QDate(today.year() + 1, 1, 1)
        else:
            next_month_first = QDate(today.year(), today.month() + 1, 1)
        
        last_day = next_month_first.addDays(-1)
        self.ui_journal.dateEditTo.setDate(last_day)
    
    def set_dates_dynamic(self):
        """Диапазон дат"""
        # Текущая дата
        today = QDate.currentDate()
        
        # Текущая дата
        self.ui_journal.dateEditFrom.setDate(today)
        self.ui_journal.dateEditTo.setDate(self.check_date())
    
    @staticmethod
    def check_date() -> dt.date:
        """Прибавляем к текущей дате 1 месяц и вычитеаем 1 день"""
        today = dt.date.today()
        check_date = today + relativedelta(months=1, days=-1)
        
        # future_date = today + relativedelta(years=1, months=2, days=10)  # Добавление интервалов
        # past_date = today - relativedelta(weeks=3)  # Вычитание интервалов
        # previous_month_date = today + relativedelta(months=-1)  # Вычисление даты предыдущего месяца:
        
        # Определение последнего дня месяца
        # first_day = datetime(year, month, 1)
        # first_day + relativedelta(months=1, days=-1)
        
        # check_date = check_date - dt.timedelta(days=1)
        # print(check_date)
        return check_date
    
    def load_data_db(self):
        """Загрузка данных"""
        
        if self.ui_journal.dateEditFrom.date().toPyDate() > self.ui_journal.dateEditTo.date().toPyDate():
            QMessageBox.warning(self, "Внимание", "Дата начала не может быть позже даты завершения")
            self.ui_journal.dateEditFrom.setFocus()
            return
        
        try:
            # TODO Загружаем данные теста исполнителя
            journal = JournalDb(
                p10=self.ui_journal.dateEditFrom.date().toPyDate(),
                p11=self.ui_journal.dateEditTo.date().toPyDate()  
            )
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
                    model.removeRows(0, model.rowCount())  # при использовании фильтра between иначе удаляет по 1 строке
                    # model.removeRow(model.rowCount() - 1)
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
                        'employee_fio': row[6],
                        'boss_fio': row[7],
                        'days_difference': row[8],
                        'done': row[9],
                        "employee_id": row[10],
                        "boss_id": row[11]
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
        
        # 1. Создаём модель: строки = кол-во записей, столбцы = 12
        model = QStandardItemModel(len(data), 12)
        model.setHorizontalHeaderLabels([
            "data_id",
            "Задание",
            "Примечание",
            "Дата\nначала",
            "Дата\nзавершения",
            "Время\nзавершения",
            "Исполнитель",
            "Руководитель",
            "days_difference",
            "done",
            "employee_id",
            "boss_id"
        ])
        
        # 2. Заполняем модель данными
        for row_idx, row_data in enumerate(data):
            # data_id (скрытый)
            model.setItem(row_idx, 0, QStandardItem(str(row_data.get('data_id', ''))))
            
            days_diff = str(row_data.get('days_difference', '0.0'))  # Берем значение Дни до завершения задачи (days_difference)
            done = str(row_data.get('done', '0'))  # Берем значение Отметка о завершении
            
            item_task = QStandardItem(str(row_data.get('task', '')))  # Задание
            item_note = QStandardItem(str(row_data.get('note', '')))  # Примечание
            item_date_start_task = QStandardItem(str(row_data.get('date_start_task', '')))  # Дата начала
            item_date_end_task = QStandardItem(str(row_data.get('date_end_task', '')))  # Дата завершения
            item_time_end_task = QStandardItem(str(row_data.get('time_end_task', '')))  # Время завершения
            item_employee_fio = QStandardItem(str(row_data.get('employee_fio', '')))  # Исполнитель
            item_boss_fio = QStandardItem(str(row_data.get('boss_fio', '')))  # Руководитель
            
            if (8.0 <= float(days_diff) <= 14.0) and (int(done) == 0):
                item_task.setForeground(QtGui.QColor("darkorange"))
                item_note.setForeground(QtGui.QColor("darkorange"))
                item_date_start_task.setForeground(QtGui.QColor("darkorange"))
                item_date_end_task.setForeground(QtGui.QColor("darkorange"))
                item_time_end_task.setForeground(QtGui.QColor("darkorange"))
                item_boss_fio.setForeground(QtGui.QColor("darkorange"))
                item_employee_fio.setForeground(QtGui.QColor("darkorange"))
            
            elif (1.0 <= float(days_diff) <= 7.0) and (int(done) == 0):
                item_task.setForeground(QtGui.QColor("red"))
                item_note.setForeground(QtGui.QColor("red"))
                item_date_start_task.setForeground(QtGui.QColor("red"))
                item_date_end_task.setForeground(QtGui.QColor("red"))
                item_time_end_task.setForeground(QtGui.QColor("red"))
                item_boss_fio.setForeground(QtGui.QColor("red"))
                item_employee_fio.setForeground(QtGui.QColor("red"))
            
            elif (float(days_diff) <= 0.0) and (int(done) == 0):
                item_task.setForeground(QtGui.QColor("darkred"))
                item_note.setForeground(QtGui.QColor("darkred"))
                item_date_start_task.setForeground(QtGui.QColor("darkred"))
                item_date_end_task.setForeground(QtGui.QColor("darkred"))
                item_time_end_task.setForeground(QtGui.QColor("darkred"))
                item_boss_fio.setForeground(QtGui.QColor("darkred"))
                item_employee_fio.setForeground(QtGui.QColor("darkred"))
            
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
            
            # Дата начала
            # model.setItem(row_idx, 3, QStandardItem(str(row_data.get('date_start_task', ''))))
            model.setItem(row_idx, 3, item_date_start_task)
            
            # Дата завершения
            # model.setItem(row_idx, 4, QStandardItem(str(row_data.get('date_end_task', ''))))
            model.setItem(row_idx, 4, item_date_end_task)
            
            # Время завершения
            # model.setItem(row_idx, 5, QStandardItem(str(row_data.get('time_end_task', ''))))
            model.setItem(row_idx, 5, item_time_end_task)
            
            # Исполнитель
            # model.setItem(row_idx, 6, QStandardItem(str(row_data.get('employee_fio', ''))))
            model.setItem(row_idx, 6, item_employee_fio)
            
            # Руководитель
            # model.setItem(row_idx, 7, QStandardItem(str(row_data.get('boss_fio', ''))))
            model.setItem(row_idx, 7, item_boss_fio)
            
            # Дни до завершения задачи (days_difference)
            # model.setItem(row_idx, 8, QStandardItem(str(row_data.get('days_difference', ''))))
            model.setItem(row_idx, 8, QStandardItem(days_diff))
            
            # Отметка о завершении
            # model.setItem(row_idx, 9, QStandardItem(str(row_data.get('done', ''))))
            model.setItem(row_idx, 9, QStandardItem(done))
            
            # employee_id
            model.setItem(row_idx, 10, QStandardItem(str(row_data.get('employee_id', ''))))
            
            # boss_id
            model.setItem(row_idx, 11, QStandardItem(str(row_data.get('boss_id', ''))))
            
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
        
        # 3. Привязываем модель к tableView (если используем сортирвку - комментируем строку Привязываем модель в п. 10)
        # self.ui_journal.tableView.setModel(model)
        
        # 4. Скрываем столбцы data_id (индекс 0), days_difference (индекс 8), done (индекс 9), employee_id (индекс 10), boss_id (индекс 11)
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
        
        #! ### Фильтрация данных ###
        # 7. Создаём прокси-модель и связываем
        self.proxy_model = MultiColumnFilterProxyModel(self)
        self.proxy_model.setSourceModel(model)
        
        # 8. Настройка сортировки (по умолчанию сравнение строк, числа надо преобразовывать)
        # Можно указать роль, по которой сортировать (обычно Qt.DisplayRole)
        self.proxy_model.setSortRole(Qt.DisplayRole)
        
        # 9. Включаем динамическую сортировку (при изменении данных)
        self.proxy_model.setDynamicSortFilter(True)
        
        # 10. Таблица для отображения Привязываем модель к tableView (Вместо пункта 3)
        self.ui_journal.tableView.setModel(self.proxy_model)  # важно: подключаем прокси, а не исходную модель
        
        # 11. Включаем сортировку по клику на заголовок (может сбиваться сортировка)
        # self.ui_journal.tableView.setSortingEnabled(True)
        #! #########################
    
    def on_filter_text_changed_task(self, text):
        """Фильтрация по заданию"""
        model = self.ui_journal.tableView.model()
        if model and model.rowCount() == -1:
            return
        
        if text:
            self.proxy_model.setFilterForColumn(1, text)  # фильтр по заданию
        else:
            self.proxy_model.setFilterForColumn(1, "")  # фильтр по заданию
    
    def on_filter_text_changed_employe(self, text):
        """Фильтрация по исполнителю"""
        model = self.ui_journal.tableView.model()
        if model and model.rowCount() == -1:
            return
        
        if text:
            self.proxy_model.setFilterForColumn(6, text)  # фильтр по исполнителю
        else:
            self.proxy_model.setFilterForColumn(6, "")  # фильтр по исполнителю
    
    # TODO Добавление записи
    def add_data_to_db(self) -> None:
        """Добавление данных в базу данных"""
        # Установка фокуса на поле задание
        self.ui_journal.plainTextEditTask.setFocus(True)
        # Активация / деактивация элементов
        self.bool_enabled_elements(False)
        # Очистка полей
        self.clear_line_edit()
        # Выбор режима
        self.setSql = "Insert"
        # print(self.setSql)
    
    # TODO Изменение записи
    def update_data_in_db(self) -> None:
        """Изменение данных в базе данных"""
        # Выбранная строка
        current_row = self.ui_journal.tableView.currentIndex().row()
        
        # if current_row < 0:
        if current_row == -1:
            QMessageBox.warning(self, "Внимание", "Выберите запись для редактирования")
            return
        else:
            # Синхронизация значения полей со значением в таблице
            self.cell_clicked(current_row, 0)
            # Установка фокуса на поле задание
            self.ui_journal.plainTextEditTask.setFocus(True)
            # Активация / деактивация элементов
            self.bool_enabled_elements(False)
            # Выбор режима
            self.setSql = "Update"
            # print(self.setSql)
    
    # TODO Удаление записи
    def delete_data_from_db(self) -> None:
        """Удаление данных из базы данных"""
        # Выбранная строка
        current_row = self.ui_journal.tableView.currentIndex().row()
        
        # if current_row < 0:
        if current_row == -1:
            QMessageBox.warning(self, "Внимание", "Выберите запись для удаления")
            return
        
        # Синхронизация значения полей со значением в таблице
        self.cell_clicked(current_row, 0)
        
        """
        delete = QMessageBox.warning(self,
                                      "Удаление записи из таблицы",
                                      'Удаление записи приведёт к потере всех связанных данных.\n'
                                      'Вы хотите удалить запись "{0}" ?'.format(
                                          self.ui_personal_plan.tableAdditionalGoals.item(current_row, 1).text()),
                                      QMessageBox.Yes | QMessageBox.No)
        
        if delete == QMessageBox.Yes:
        """
        
        # Создаем диалог вручную, а не через статический метод
        msg_box = QtWidgets.QMessageBox()
        
        msg_box.setWindowTitle("Удаление записи")
        msg_box.setText("Вы уверены, что хотите удалить запись '{0}' ?".format(self.ui_journal.tableView.model().data(self.ui_journal.tableView.model().index(current_row, 1))))
        
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
            # Выбор режима
            self.setSql = "Delete"
            self.command_delete()
            # Заполнение таблицы
            self.load_data_db()
            # Очистка полей
            self.clear_line_edit()
            # Сброс режима SQL
            self.setSql = ""
    
    def command_delete(self):
        """команда на удаление записей"""
        current_row = self.ui_journal.tableView.currentIndex().row()
        
        # if current_row < 0:
        if current_row == -1:
            return
            
        data_id = self.ui_journal.tableView.model().index(current_row, 0).data()  # data.get('data_id') # id записи, присвоенная в таблице на стороне клиента (Date.now().toString() дата в виде текста)
        # print(data_id)
        
        if data_id:
            try:
                journal = JournalDb(
                    p0=data_id
                )
                journal.delete_data()
            except Exception as e:
                txt = self.ui_journal.plainTextEditTask.toPlainText().strip()
                QMessageBox.warning(self, 'Внимание', "Ошибка {e} при удалении записи {txt}".format(txt=txt, e=e))
                return
            else:
                pass
                # return jsonify({'status': 'success'})
        else:
            txt = self.ui_journal.plainTextEditTask.toPlainText().strip()
            QMessageBox.warning(self, 'Внимание', "Отсутсвует id для удалении записи {txt} {e}".format(txt=txt, e=e))
            return
    
    # TODO Сохранение записи
    def save_data_in_db(self) -> None:
        """Активация / деактивация кнопок"""
        # Установка фокуса на поле задание
        self.ui_journal.plainTextEditTask.setFocus(True)
        # Сохранение данных
        if self.setSql == "Insert":
            
            data_id = str(int(time.time() * 1000))  # data.get('data_id') # id записи, присвоенная в таблице на стороне клиента (Date.now().toString() дата в виде текста)
            boss_fio = self.ui_journal.comboBoxBoss.currentData()  # Ф.И.О. руководителя
            employe_fio = self.ui_journal.comboBoxEmploye.currentData()  # Ф.И.О. исполнителя
            task = self.ui_journal.plainTextEditTask.toPlainText().strip()  # задание
            note = self.ui_journal.plainTextEditNote.toPlainText().strip()  # примечание
            date_start = self.ui_journal.dateEditStart.date().toPyDate()  # дата начала задачи
            date_end = self.ui_journal.dateEditEnd.date().toPyDate()  # дата окончания задачи
            
            filter_from = self.ui_journal.dateEditFrom.date().toPyDate() # фильтр от
            filter_to = self.ui_journal.dateEditTo.date().toPyDate() # фильтр до
            
            if self.ui_journal.checkBox_2.isChecked():
                time_end = self.ui_journal.timeEdit.time().toString('hh:mm')  # время окончания задачи
            else:
                time_end = None
            
            if self.ui_journal.checkBox.isChecked():
                done = 1  # отметка о выполнении
            else:
                done = 0
            
            if employe_fio == 1:
                QMessageBox.warning(self, "Внимание", "Не указан исполнитель")
                self.ui_journal.lineEditFindEmployeFio.setFocus()
                return
            elif boss_fio == 1:
                QMessageBox.warning(self, "Внимание", "Не указан руководитель")
                self.ui_journal.lineEditFindBossFio.setFocus()
                return
            elif task.strip() == "":
                QMessageBox.warning(self, "Внимание", "Задание не указано")
                self.ui_journal.plainTextEditTask.setFocus()
                return
            elif date_start > date_end:
                QMessageBox.warning(self, "Внимание", "Дата начала не может быть позже даты завершения")
                self.ui_journal.dateEditStart.setFocus()
                return
            else:
                try:
                    journal = JournalDb(
                        p0=data_id, 
                        p1=boss_fio, 
                        p2=employe_fio,
                        p3=task,
                        p4=note,
                        p5=date_start,
                        p6=date_end,
                        p7=time_end,
                        p8=done,
                        p9=self.get_current_datetime(),
                        p10=filter_from,
                        p11=filter_to
                    )
                    journal.insert_data()
                except Exception as e:
                    QMessageBox.warning(self, 'Внимание', "Ошибка при добавлении данных {e}".format(e=e))
                    return
        
        if self.setSql == "Update":
            
            current_row = self.ui_journal.tableView.currentIndex().row()
            # if current_row < 0:
            if current_row == -1:
                return
            
            data_id = self.ui_journal.tableView.model().index(current_row, 0).data()  # data.get('data_id') # id записи, присвоенная в таблице на стороне клиента (Date.now().toString() дата в виде текста)
            boss_fio = self.ui_journal.comboBoxBoss.currentData()  # Ф.И.О. руководителя
            employe_fio = self.ui_journal.comboBoxEmploye.currentData()  # Ф.И.О. исполнителя
            task = self.ui_journal.plainTextEditTask.toPlainText().strip()  # задание
            note = self.ui_journal.plainTextEditNote.toPlainText().strip()  # примечание
            date_start = self.ui_journal.dateEditStart.date().toPyDate()  # дата начала задачи
            date_end = self.ui_journal.dateEditEnd.date().toPyDate()  # дата окончания задачи
            
            filter_from = self.ui_journal.dateEditFrom.date().toPyDate() # фильтр от
            filter_to = self.ui_journal.dateEditTo.date().toPyDate() # фильтр до
            
            if self.ui_journal.checkBox_2.isChecked():
                time_end = self.ui_journal.timeEdit.time().toString('hh:mm')  # время окончания задачи
            else:
                time_end = None
            
            if self.ui_journal.checkBox.isChecked():
                done = 1  # отметка о выполнении
            else:
                done = 0
            
            if employe_fio == 1:
                QMessageBox.warning(self, "Внимание", "Не указан исполнитель")
                self.ui_journal.lineEditFindEmployeFio.setFocus()
                return
            elif boss_fio == 1:
                QMessageBox.warning(self, "Внимание", "Не указан руководитель")
                self.ui_journal.lineEditFindBossFio.setFocus()
                return
            elif task.strip() == "":
                QMessageBox.warning(self, "Внимание", "Задание не указано")
                self.ui_journal.plainTextEditTask.setFocus()
                return
            elif date_start > date_end:
                QMessageBox.warning(self, "Внимание", "Дата начала не может быть позже даты завершения")
                self.ui_journal.dateEditStart.setFocus()
                return
            else:
                try:
                    journal = JournalDb(
                        p0=data_id, 
                        p1=boss_fio, 
                        p2=employe_fio,
                        p3=task,
                        p4=note,
                        p5=date_start,
                        p6=date_end,
                        p7=time_end,
                        p8=done,
                        p9=self.get_current_datetime(),
                        p10=filter_from,
                        p11=filter_to
                    )
                    journal.update_data()
                except Exception as e:
                    QMessageBox.warning(self, 'Внимание', "Ошибка при редактировании данных {e}".format(e=e))
                    return
        
        # Заполнение таблицы
        self.load_data_db()
        # Очистка полей
        self.cancel()
        # Сброс режима SQL
        self.setSql = ""
    
    # TODO Отмена
    def cancel(self) -> None:
        """Отмена действия"""
        # Очистка полей
        self.clear_line_edit()
        # Установка фокуса на поле задание
        self.ui_journal.plainTextEditTask.setFocus(True)
        # Активация / деактивация элементов
        self.bool_enabled_elements(True)
        
        # Выбранная строка
        current_row = self.ui_journal.tableView.currentIndex().row()
        # if current_row < 0:
        if current_row == -1:
            return
        
        self.value_elements(current_row)
        self.setSql = ""
    
    def limit_text_edit_task(self):
        """Установка ограничения количества символов"""
        text = self.ui_journal.plainTextEditTask.toPlainText()
        max_chars = 50
        if len(text) > max_chars:
            # Отключаем сигнал, чтобы избежать рекурсии при программной замене
            self.ui_journal.plainTextEditTask.blockSignals(True)
            self.ui_journal.plainTextEditTask.setPlainText(text[:max_chars])
            self.ui_journal.plainTextEditTask.blockSignals(False)
            
            # Перемещаем курсор в конец (иначе он останется в начале)
            cursor = self.ui_journal.plainTextEditTask.textCursor()
            cursor.movePosition(cursor.End)
            self.ui_journal.plainTextEditTask.setTextCursor(cursor)
    
    def limit_text_edit_note(self):
        """Установка ограничения количества символов"""
        text = self.ui_journal.plainTextEditNote.toPlainText()
        max_chars = 50
        if len(text) > max_chars:
            # Отключаем сигнал, чтобы избежать рекурсии при программной замене
            self.ui_journal.plainTextEditNote.blockSignals(True)
            self.ui_journal.plainTextEditNote.setPlainText(text[:max_chars])
            self.ui_journal.plainTextEditNote.blockSignals(False)
            
            # Перемещаем курсор в конец (иначе он останется в начале)
            cursor = self.ui_journal.plainTextEditNote.textCursor()
            cursor.movePosition(cursor.End)
            self.ui_journal.plainTextEditNote.setTextCursor(cursor)
    
    def cell_clicked(self, row, column) -> None:
        """Данные в выбранной строке таблицы (вызывается из других функций)"""
        # row - принимает координаты строки
        # column - принимает координаты столбца
        # print("Row %d and Column %d was clicked" % (row, column))
        
        self.value_elements(row)
    
    def on_cell_clicked(self, index):
        """Данные в выбранной строке таблицы"""
        if index.isValid():
            row = index.row()
            # column = index.column()
            # data = index.data()
            # print("Клик по строке {row}, столбцу {column}, данные: {data}".format(row=row, column=column, data=data))
            
            self.value_elements(row)
    
    def on_cell_activated(self, index):
        """Данные в выбранной строке таблицы"""
        row = index.row()
        # col = index.column()
        # print("Активирована ячейка: строка {row}, столбец {col}".format(row=row, col=col))
        # print("Данные: {index_data}".format(index_data=index.data()))
        # Данные: index.data() или модель.index(row, col).data()
        
        self.value_elements(row)
    
    def on_cell_pressed(index):
        """Slot для обработки нажатия"""
        # row = index.row()
        # column = index.column()
        # value = index.data()
        # print("Нажата ячейка: строка {row}, столбец {column}".format(row=row, column=column))
        # print("Данные: {data}".format(data=value))
        # Если нужно получить данные:
        # value = index.data()
        pass
    
    def value_elements(self, row):
        """Присваиваем значения элементам из таблицы"""
        # TODO Задание
        value1 = self.ui_journal.tableView.model().data(self.ui_journal.tableView.model().index(row, 1))
        self.ui_journal.plainTextEditTask.setPlainText(value1)
        
        # TODO Примечание
        value2 = self.ui_journal.tableView.model().data(self.ui_journal.tableView.model().index(row, 2))
        self.ui_journal.plainTextEditNote.setPlainText(value2)
        
        # TODO Дата начала
        slist1 = str(self.ui_journal.tableView.model().data(self.ui_journal.tableView.model().index(row, 3))).split(".")
        sdate1 = dt.date(int(slist1[2]), int(slist1[1]), int(slist1[0]))
        self.ui_journal.dateEditStart.setDate(QDate(sdate1))
        # self.ui_journal.dateEditStart.setDate(QDate(2023, 7, 25))
        
        # TODO Дата окончания
        slist2 = str(self.ui_journal.tableView.model().data(self.ui_journal.tableView.model().index(row, 4))).split(".")
        sdate2 = dt.date(int(slist2[2]), int(slist2[1]), int(slist2[0]))
        self.ui_journal.dateEditEnd.setDate(QDate(sdate2))
        # self.ui_journal.dateEditEnd.setDate(QDate(2023, 7, 25))
        
        # TODO Время окончания
        time_data = self.ui_journal.tableView.model().data(
            self.ui_journal.tableView.model().index(row, 5)
        )
        
        if time_data:
            if time_data != '-':
                self.ui_journal.checkBox_2.setChecked(True)
                try:
                    parts = str(time_data).split(":")
                    if len(parts) == 2:
                        hour, minute = int(parts[0]), int(parts[1])
                        if 0 <= hour <= 23 and 0 <= minute <= 59:
                            self.ui_journal.timeEdit.setTime(QTime(hour, minute))
                except (ValueError, IndexError):
                    pass  # логирование ошибки при необходимости
            else:
                self.ui_journal.checkBox_2.setChecked(False)
        else:
            self.ui_journal.checkBox_2.setChecked(False)
        
        # TODO Исполнитель
        self.ui_journal.comboBoxEmploye.setCurrentText(self.ui_journal.tableView.model().data(self.ui_journal.tableView.model().index(row, 6)))
        
        # TODO Руководитель
        self.ui_journal.comboBoxBoss.setCurrentText(self.ui_journal.tableView.model().data(self.ui_journal.tableView.model().index(row, 7)))
        
        # TODO Отметка о выполнении
        if int(self.ui_journal.tableView.model().data(self.ui_journal.tableView.model().index(row, 9))) == 0:
            self.ui_journal.checkBox.setChecked(False)
        else:
            self.ui_journal.checkBox.setChecked(True)
    
    def check_time(self, state):
        """Блокировка времени"""
        if state:
            self.ui_journal.timeEdit.setEnabled(True)
        else:
            self.ui_journal.timeEdit.setEnabled(False)
    
    def bool_enabled_elements(self, boolean) -> None:
        """Активация / деактивация элементов управления"""
        self.ui_journal.btnSave.setEnabled(not boolean)
        self.ui_journal.btnCancel.setEnabled(not boolean)
        self.ui_journal.btnInsert.setEnabled(boolean)
        self.ui_journal.btnUpdate.setEnabled(boolean)
        self.ui_journal.btnDelete.setEnabled(boolean)
        
        self.ui_journal.groupBoxFilter.setEnabled(boolean)
        self.ui_journal.groupBoxElements.setEnabled(not boolean)
        
        if (self.ui_journal.groupBoxElements.isEnabled()) and (not self.ui_journal.checkBox_2.isChecked()):
            self.ui_journal.timeEdit.setEnabled(False)
        else:
            self.ui_journal.timeEdit.setEnabled(True)
        
        self.ui_journal.tableView.setEnabled(boolean)
        
        # self.ui_persons.lineEditFilter.setEnabled(boolean)
        # self.ui_persons.lineEditFilter.setText("")
        
        # self.ui_persons.tableWidget.setEnabled(boolean)
    
    def clear_line_edit(self) -> None:
        """Очистка полей"""
        self.ui_journal.lineEditFindBossFio.setText("")
        
        # index0 = self.ui_journal.comboBoxBoss.findText("нет данных")
        # self.ui_journal.comboBoxBoss.setCurrentIndex(index0)
        self.ui_journal.comboBoxBoss.setCurrentText("нет данных")
        
        self.ui_journal.lineEditFindEmployeFio.setText("")
        
        # index1 = self.ui_journal.comboBoxEmploye.findText("нет данных")
        # self.ui_journal.comboBoxEmploye.setCurrentIndex(index1)
        self.ui_journal.comboBoxEmploye.setCurrentText("нет данных")
        
        self.ui_journal.plainTextEditTask.setPlainText("")
        self.ui_journal.plainTextEditNote.setPlainText("")
        
        self.ui_journal.dateEditStart.setDate(QDate.currentDate())
        self.ui_journal.dateEditEnd.setDate(QDate.currentDate())
        self.ui_journal.timeEdit.setTime(QTime(0, 0))  # 00:00
        
        self.ui_journal.checkBox_2.setChecked(False)
        self.ui_journal.checkBox.setChecked(False)


class EmployeFIO:
    # Для Astra Linux 1.6 (Python 3.5.3)
    def __init__(self, ui, parent_window, **kwargs):
        self.ui_journal = ui  # передаём ссылку на UI (type: Ui_JournalWindow)
        self.parent_window = parent_window  # Сохраняем ссылку на родительское окно
        
        self.list_employe_fio = []  # Список (массив) Ф.И.О. руководителя
        self.dict_employe_fio = {}  # Словарь (справочник) id, fio
        
        self.completer_lineEditEmployeFio = None  # Заполнение поле поиска
        
        # Загружаем данные сразу при создании объекта
        self.load_combo_box_employe_fio()
    
    """
    def __init__(self, ui: Ui_JournalWindow, parent_window, **kwargs):  # Добавлена аннотация типа (аннотация - подсказки для разработчиков)
        self.ui_journal: Ui_JournalWindow = ui  # Аннотация типа для атрибута и передаём ссылку на UI (аннотация - подсказки для разработчиков)
        self.parent_window = parent_window  # Сохраняем ссылку на родительское окно
    """
    
    ####################################################################################################################
    # Загрузка Ф.И.О. Исполнителя
    ####################################################################################################################
    def load_employes(self) -> list:
        """Загружаем данные из таблицы"""
        try:
            journal = JournalDb()
            data = journal.load_data_employes()
        except Exception as err:
            # print("Ошибка при работе с sqlite", err)
            # QMessageBox.critical(self, 'Внимание', 'Ошибка при работе с sqlite {0}'.format(err))
            QMessageBox.warning(self.parent_window, 'Внимание', 'Ошибка при работе с sqlite {0}'.format(err))
            return
        else:
            return data
    
    def load_combo_box_employe_fio(self) -> None:
        """Заполняем comboBoxEmploye данными"""
        for value_tuple in self.load_employes():
            _id = int(value_tuple[0])  # Присваиваем id записи
            fio = str(value_tuple[1])  # Указываем Ф.И.О.
            # fio = str(value_tuple[1]) + " " + str(value_tuple[2]) + " " + str(value_tuple[3])  # Указываем Ф.И.О.
            self.list_employe_fio.append(fio)  # Заполняем список (массив)
            # self.dict_employe_fio[fio] = _id   # Заполняем словарь (справочник)
            self.dict_employe_fio[fio.lower()] = _id   # Заполняем словарь (справочник) - ключи в нижнем регистре
            
            self.ui_journal.comboBoxEmploye.addItem(fio, _id)  # Добавляем Ф.И.О. и id
            
            """
            # совмещаем QLineEdit с данными
            ################################################
            from PyQt5.QtWidgets import QCompleter
            self.completer_lineEditEmployeFio = QCompleter(self.list_employe_fio)
            self.ui_journal.lineEditFindEmployeFio.setCompleter(self.completer_lineEditEmployeFio)
            ################################################
            
            # Выводим id сотрудника
            ################################################
            # self.ui_journal.lineEditFindEmployeFio.editingFinished.connect(self.id_person_show)
            """
            
            # совмещаем QLineEdit с данными
            ################################################
            from PyQt5.QtWidgets import QCompleter
            from PyQt5.QtCore import Qt
            
            self.completer_lineEditEmployeFio = QCompleter(self.list_employe_fio)
            # Включаем регистронезависимую фильтрацию через отдельный метод
            self.completer_lineEditEmployeFio.setCaseSensitivity(Qt.CaseInsensitive)
            # Устанавливаем режим поиска (содержит подстроку)
            self.completer_lineEditEmployeFio.setFilterMode(Qt.MatchContains)
            self.ui_journal.lineEditFindEmployeFio.setCompleter(self.completer_lineEditEmployeFio)
            ################################################
            
            # Установите режим завершения, который всегда показывает список
            # self.completer_lineEditEmployeFio.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
    
    def id_person_show(self) -> None:
        if self.ui_journal.lineEditFindEmployeFio.text().strip():
            search_text = self.ui_journal.lineEditFindEmployeFio.text().strip().lower()  # Приводим к нижнему регистру
            try:
                _id = self.dict_employe_fio[search_text]  # Ищем по ключу в нижнем регистре
            except KeyError as err:
                self.ui_journal.lineEditFindEmployeFio.setText("")
                QMessageBox.warning(self.parent_window, 'Внимание', 'Ошибочное значение {0}'.format(err))
                return 
            else:
                # Находим исходное написание ФИО для отображения
                original_fio = None
                for fio in self.list_employe_fio:
                    if fio.lower() == search_text:
                        original_fio = fio
                        break
                
                if original_fio:
                    self.ui_journal.comboBoxEmploye.setCurrentText(original_fio)
                    self.ui_journal.lineEditFindEmployeFio.setText("")
        else:
            return
    
    """
    def id_person_show(self) -> None:
        if self.ui_journal.lineEditFindEmployeFio.text().strip():
            try:
                _id = self.dict_employe_fio[self.ui_journal.lineEditFindEmployeFio.text().strip()]
            except KeyError as err:
                self.ui_journal.lineEditFindEmployeFio.setText("")
                # print("Ошибочное значение {0}".format(err))
                # QMessageBox.critical(self, 'Внимание', 'Ошибочное значение {0}'.format(err))
                QMessageBox.warning(self.parent_window, 'Внимание', 'Ошибочное значение {0}'.format(err))
                return 
            else:
                txt = self.ui_journal.lineEditFindEmployeFio.text().strip()
                # print(txt + " id = " + str(_id))
                self.ui_journal.comboBoxEmploye.setCurrentText(txt)
                self.ui_journal.lineEditFindEmployeFio.setText("")
        else:
            return
    """
    
    def id_data_current_employe_fio(self) -> None:
        # self.id_person = self.ui_journal.comboBoxEmploye.currentData()
        # _id = self.ui_journal.comboBoxEmploye.currentData()
        # txt = self.ui_journal.comboBoxEmploye.currentText()
        pass
    ####################################################################################################################


class BossFIO:
    # Для Astra Linux 1.6 (Python 3.5.3)
    def __init__(self, ui, parent_window, **kwargs):
        self.ui_journal = ui  # передаём ссылку на UI (type: Ui_JournalWindow)
        self.parent_window = parent_window  # Сохраняем ссылку на родительское окно
        
        self.list_boss_fio = []  # Список (массив) Ф.И.О. руководителя
        self.dict_boss_fio = {}  # Словарь (справочник) id, fio
        
        self.completer_lineEditBossFio = None  # Заполнение поле поиска
        
        # Загружаем данные сразу при создании объекта
        self.load_combo_box_boss_fio()
    
    """
    def __init__(self, ui: Ui_JournalWindow, parent_window, **kwargs):  # Добавлена аннотация типа (аннотация - подсказки для разработчиков)
        self.ui_journal: Ui_JournalWindow = ui  # Аннотация типа для атрибута и передаём ссылку на UI (аннотация - подсказки для разработчиков)
        self.parent_window = parent_window  # Сохраняем ссылку на родительское окно
    """
    
    ####################################################################################################################
    # Загрузка Ф.И.О. руководителя
    ####################################################################################################################
    def load_bosses(self) -> list:
        """Загружаем данные из таблицы"""
        try:
            journal = JournalDb()
            data = journal.load_data_bosses()
        except Exception as err:
            # print("Ошибка при работе с sqlite", err)
            # QMessageBox.critical(self, 'Внимание', 'Ошибка при работе с sqlite {0}'.format(err))
            QMessageBox.warning(self.parent_window, 'Внимание', 'Ошибка при работе с sqlite {0}'.format(err))
            return
        else:
            return data
    
    def load_combo_box_boss_fio(self) -> None:
        """Заполняем comboBoxBoss данными"""
        for value_tuple in self.load_bosses():
            _id = int(value_tuple[0])  # Присваиваем id записи
            fio = str(value_tuple[1])  # Указываем Ф.И.О.
            # fio = str(value_tuple[1]) + " " + str(value_tuple[2]) + " " + str(value_tuple[3])  # Указываем Ф.И.О.
            self.list_boss_fio.append(fio)  # Заполняем список (массив)
            # self.dict_boss_fio[fio] = _id   # Заполняем словарь (справочник)
            self.dict_boss_fio[fio.lower()] = _id   # Заполняем словарь (справочник) - ключи в нижнем регистре
            
            self.ui_journal.comboBoxBoss.addItem(fio, _id)  # Добавляем Ф.И.О. и id
            
            """
            # совмещаем QLineEdit с данными
            ################################################
            from PyQt5.QtWidgets import QCompleter
            
            self.completer_lineEditBossFio = QCompleter(self.list_boss_fio)
            self.ui_journal.lineEditFindBossFio.setCompleter(self.completer_lineEditBossFio)
            ################################################
            """
            
            # совмещаем QLineEdit с данными
            ################################################
            from PyQt5.QtWidgets import QCompleter
            from PyQt5.QtCore import Qt
            
            self.completer_lineEditBossFio = QCompleter(self.list_boss_fio)
            # Включаем регистронезависимую фильтрацию через отдельный метод
            self.completer_lineEditBossFio.setCaseSensitivity(Qt.CaseInsensitive)
            # Устанавливаем режим поиска (содержит подстроку)
            self.completer_lineEditBossFio.setFilterMode(Qt.MatchContains)
            self.ui_journal.lineEditFindBossFio.setCompleter(self.completer_lineEditBossFio)
            ################################################
            
            # Установите режим завершения, который всегда показывает список
            # self.completer_lineEditBossFio.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
    
    def id_person_show(self) -> None:
        if self.ui_journal.lineEditFindBossFio.text().strip():
            search_text = self.ui_journal.lineEditFindBossFio.text().strip().lower()  # Приводим к нижнему регистру
            try:
                _id = self.dict_boss_fio[search_text]  # Ищем по ключу в нижнем регистре
            except KeyError as err:
                self.ui_journal.lineEditFindBossFio.setText("")
                QMessageBox.warning(self.parent_window, 'Внимание', 'Ошибочное значение {0}'.format(err))
                return 
            else:
                # Находим исходное написание ФИО для отображения
                original_fio = None
                for fio in self.list_boss_fio:
                    if fio.lower() == search_text:
                        original_fio = fio
                        break
                
                if original_fio:
                    self.ui_journal.comboBoxBoss.setCurrentText(original_fio)
                    self.ui_journal.lineEditFindBossFio.setText("")
        else:
            return
    
    """
    def id_person_show(self) -> None:
        if self.ui_journal.lineEditFindBossFio.text().strip():
            try:
                _id = self.dict_boss_fio[self.ui_journal.lineEditFindBossFio.text().strip()]
            except KeyError as err:
                self.ui_journal.lineEditFindBossFio.setText("")
                # print("Ошибочное значение {0}".format(err))
                # QMessageBox.critical(self, 'Внимание', 'Ошибочное значение {0}'.format(err))
                QMessageBox.warning(self.parent_window, 'Внимание', 'Ошибочное значение {0}'.format(err))
                return 
            else:
                txt = self.ui_journal.lineEditFindBossFio.text().strip()
                # print(txt + " id = " + str(_id))
                self.ui_journal.comboBoxBoss.setCurrentText(txt)
                self.ui_journal.lineEditFindBossFio.setText("")
        else:
            return
    """
    
    def id_data_current_boss_fio(self) -> None:
        # self.id_person = self.ui_journal.comboBoxBoss.currentData()
        # _id = self.ui_journal.comboBoxBoss.currentData()
        # txt = self.ui_journal.comboBoxBoss.currentText()
        pass
    ####################################################################################################################


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
                "Дата\nначала", 
                "Дата\nзавершения",
                "Время\nзавершения",
                "Исполнитель",
                "Руководитель",
                "days_difference",
                "done",
                "employee_id",
                "boss_id"
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
                "Дата\nначала", 
                "Дата\nзавершения",
                "Время\nзавершения",
                "Исполнитель",
                "Руководитель",
                "days_difference",
                "done",
                "employee_id",
                "boss_id"
            ]
            model.setHorizontalHeaderLabels(headers)
            
            # 3. Присваиваем модель таблице
            self.ui_journal.tableView.setModel(model)
            
            # 3. Присваиваем модель таблице
            self.ui_journal.tableView.setModel(model)
            
            # 4. Скрываем столбцы data_id (индекс 0), days_difference (индекс 8), done (индекс 9), employee_id (индекс 10), boss_id (индекс 11)
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


class MultiColumnFilterProxyModel(QSortFilterProxyModel):
    """Прокси-модель для фильтрации по нескольким столбцам"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_columns = {}  # словарь: {column: filter_text}
    
    def setFilterForColumn(self, column, filter_text):
        """Установить фильтр для конкретного столбца"""
        if filter_text and filter_text.strip():
            self.filter_columns[column] = filter_text.strip().lower()
        else:
            if column in self.filter_columns:
                del self.filter_columns[column]
        self.invalidateFilter()
    
    def clearFilters(self):
        """Очистить все фильтры"""
        self.filter_columns.clear()
        self.invalidateFilter()
    
    def filterAcceptsRow(self, source_row, source_parent):
        """Переопределенный метод для фильтрации строк"""
        if not self.filter_columns:
            return True
        
        source_model = self.sourceModel()
        
        for column, filter_text in self.filter_columns.items():
            index = source_model.index(source_row, column, source_parent)
            data = source_model.data(index, Qt.DisplayRole)
            
            if data and filter_text not in str(data).lower():
                return False
        
        return True
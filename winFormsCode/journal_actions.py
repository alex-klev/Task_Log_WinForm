# стандартные
import sys
import datetime as dt
import time

# сторонние
from PyQt5 import QtWidgets, QtGui # QtGui создает объект цвета в PyQt5 с использованием компонентов RGB 
from PyQt5.QtCore import Qt, QDate, QTime
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
        
        """
        self.ui_persons.btnFilterOn.clicked.connect(self.load_data_filter)  # Фильтрация
        self.ui_persons.btnFilterOff.clicked.connect(self.load_data_no_filter)  # Отключить фильтрацию
        """
        
        
        self.ui_journal.btnInsert.clicked.connect(self.add_data_to_db)  # Добавить запись в таблицу
        self.ui_journal.btnUpdate.clicked.connect(self.update_data_in_db)  # Обновить запись в таблице
        
        #self.ui_journal.btnDelete.clicked.connect(self.delete_data_from_db)  # Удалить запись из таблицы
        self.ui_journal.btnSave.clicked.connect(self.save_data_in_db)  # Сохранить запись в таблице
        self.ui_journal.btnCancel.clicked.connect(self.cancel)  # Отменить запись из таблицы
        """
        self.ui_journal.tableView.clicked.connect(self.on_cell_clicked)  # Клик по ячейке
        self.ui_journal.tableView.activated.connect(self.on_cell_activated)  # Данные в выбранной строке таблицы
        # self.ui_journal.tableView.pressed.connect(self.on_cell_pressed)  # Данные в выбранной строке таблицы
        
        self.ui_journal.lineEdit.setEnabled(False)
        """
        
        self.ui_journal.plainTextEditTask.textChanged.connect(self.limit_text_edit_task)
        self.ui_journal.plainTextEditNote.textChanged.connect(self.limit_text_edit_note)
        
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
    
    
    
    
    
    # TODO Добавление данных ###
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
    
    # TODO Изменение данных ###
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
            # self.cell_clicked(current_row, 0)
            # Установка фокуса на поле задание
            self.ui_journal.plainTextEditTask.setFocus(True)
            # Активация / деактивация элементов
            self.bool_enabled_elements(False)
            # Выбор режима
            self.setSql = "Update"
            # print(self.setSql)
    
    
    
    
    
    
    def save_data_in_db(self) -> None:
        """Активация / деактивация кнопок"""
        # Установка фокуса на поле задание
        self.ui_journal.plainTextEditTask.setFocus(True)
        # Сохранение данных
        if self.setSql == "Insert":
            
            data_id = str(int(time.time() * 1000))  # data.get('data_id') # id записи, присвоенная в таблице на стороне клиента (Date.now().toString() дата в виде текста)
            boss_fio = self.ui_journal.comboBoxBoss.currentData()  # Ф.И.О. руководителя
            employe_fio = self.ui_journal.comboBoxEmploye.currentData()  # Ф.И.О. исполнителя
            task = self.ui_journal.plainTextEditTask.toPlainText()  # задание
            note = self.ui_journal.plainTextEditNote.toPlainText()  # примечание
            date_start = self.ui_journal.dateEditStart.date().toPyDate()  # дата начала задачи
            date_end = self.ui_journal.dateEditEnd.date().toPyDate()  # дата окончания задачи
            
            if self.ui_journal.checkBox_2.isChecked():
                time_end = self.ui_journal.timeEdit.time().toString('hh:mm')  # время окончания задачи
            else:
                time_end = None
            
            if self.ui_journal.checkBox.isChecked():
                done = 1  # отметка о выполнении
            else:
                done = 0
            
            if boss_fio == 1:
                QMessageBox.warning(self, "Внимание", "Не указан руководитель")
                self.ui_journal.comboBoxBoss.setFocus()
                return
            elif employe_fio == 1:
                QMessageBox.warning(self, "Внимание", "Не указан исполнитель")
                self.ui_journal.comboBoxEmploye.setFocus()
                return
            elif task.strip() == "":
                QMessageBox.warning(self, "Внимание", "Задание не указано")
                self.ui_journal.plainTextEditTask.setFocus()
                return
            elif date_start > date_end:
                QMessageBox.warning(self, "Внимание", "Дата начала не может быть позже даты окончания")
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
                        p9=self.get_current_datetime()
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
            task = self.ui_journal.plainTextEditTask.toPlainText()  # задание
            note = self.ui_journal.plainTextEditNote.toPlainText()  # примечание
            date_start = self.ui_journal.dateEditStart.date().toPyDate()  # дата начала задачи
            date_end = self.ui_journal.dateEditEnd.date().toPyDate()  # дата окончания задачи
            
            if self.ui_journal.checkBox_2.isChecked():
                time_end = self.ui_journal.timeEdit.time().toString('hh:mm')  # время окончания задачи
            else:
                time_end = None
            
            if self.ui_journal.checkBox.isChecked():
                done = 1  # отметка о выполнении
            else:
                done = 0
            
            if task.strip() == "":
                QMessageBox.warning(self, "Внимание", "Задание не указано")
                self.ui_journal.plainTextEditTask.setFocus()
                return
            elif date_start > date_end:
                QMessageBox.warning(self, "Внимание", "Дата начала не может быть позже даты окончания")
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
                        p9=self.get_current_datetime()
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
    
    # TODO Отмена ###
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
        
        # TODO Ф.И.О.
        # value1 = self.ui_journal.tableView.model().data(self.ui_journal.tableView.model().index(current_row, 1))
        # self.ui_journal.lineEdit.setText(value1)
        """
        # TODO Оценка цели
        value2 = self.ui_personal_plan.tableViewAdditionalGoals.model().data(self.ui_personal_plan.tableViewAdditionalGoals.model().index(current_row, 2)).replace(' ', '')
        self.ui_personal_plan.spinBoxGoalEvaluation.setValue(int(value2))
        # TODO Желаемый возраст достижения цели
        value3 = self.ui_personal_plan.tableViewAdditionalGoals.model().data(self.ui_personal_plan.tableViewAdditionalGoals.model().index(current_row, 3)).replace(' ', '')
        self.ui_personal_plan.spinBoxAgeGoal.setValue(int(value3))
        # TODO Имеющиеся накопления для достижения цели
        value4 = self.ui_personal_plan.tableViewAdditionalGoals.model().data(self.ui_personal_plan.tableViewAdditionalGoals.model().index(current_row, 4)).replace(' ', '')
        self.ui_personal_plan.spinBoxMoneyForGoal.setValue(int(value4))
        """
        self.setSql = ""
    
    
    def limit_text_edit_task(self):
        text = self.ui_journal.plainTextEditTask.toPlainText()
        max_chars = 50
        if len(text) > max_chars:
            self.ui_journal.plainTextEditTask.blockSignals(True)
            self.ui_journal.plainTextEditTask.setPlainText(text[:max_chars])
            self.ui_journal.plainTextEditTask.blockSignals(False)
    
    def limit_text_edit_note(self):
        text = self.ui_journal.plainTextEditNote.toPlainText()
        max_chars = 50
        if len(text) > max_chars:
            self.ui_journal.plainTextEditNote.blockSignals(True)
            self.ui_journal.plainTextEditNote.setPlainText(text[:max_chars])
            self.ui_journal.plainTextEditNote.blockSignals(False)
    
    
    
    def cell_clicked(self, row=None, column=None) -> None:
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
    
    def cell_activated(self, row=None, column=None) -> None:
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
    
    
    
    def cell_clicked(self, row, column) -> None:
        """Данные в выбранной строке таблицы (вызывается из других функций)"""
        # row - принимает координаты строки
        # column - принимает координаты столбца
        # print("Row %d and Column %d was clicked" % (row, column))
        
        # TODO Ф.И.О.
        value1 = self.ui_employes_catalog.tableView.model().data(self.ui_employes_catalog.tableView.model().index(row, 1))
        self.ui_employes_catalog.lineEdit.setText(value1)
        """
        # TODO Оценка цели
        value2 = self.ui_personal_plan.tableViewAdditionalGoals.model().data(self.ui_personal_plan.tableViewAdditionalGoals.model().index(row, 2)).replace(' ', '')
        self.ui_personal_plan.spinBoxGoalEvaluation.setValue(int(value2))
        # TODO Желаемый возраст достижения цели
        value3 = self.ui_personal_plan.tableViewAdditionalGoals.model().data(self.ui_personal_plan.tableViewAdditionalGoals.model().index(row, 3)).replace(' ', '')
        self.ui_personal_plan.spinBoxAgeGoal.setValue(int(value3))
        # TODO Имеющиеся накопления для достижения цели
        value4 = self.ui_personal_plan.tableViewAdditionalGoals.model().data(self.ui_personal_plan.tableViewAdditionalGoals.model().index(row, 4)).replace(' ', '')
        self.ui_personal_plan.spinBoxMoneyForGoal.setValue(int(value4))
        """
    
    def on_cell_clicked(self, index):
        if index.isValid():
            row = index.row()
            # column = index.column()
            # data = index.data()
            # print("Клик по строке {row}, столбцу {column}, данные: {data}".format(row=row, column=column, data=data))
            
            # TODO Ф.И.О.
            value1 = self.ui_employes_catalog.tableView.model().data(self.ui_employes_catalog.tableView.model().index(row, 1))
            self.ui_employes_catalog.lineEdit.setText(value1)
            """
            # TODO Оценка цели
            value2 = self.ui_personal_plan.tableViewAdditionalGoals.model().data(self.ui_personal_plan.tableViewAdditionalGoals.model().index(row, 2)).replace(' ', '')
            self.ui_personal_plan.spinBoxGoalEvaluation.setValue(int(value2))
            # TODO Желаемый возраст достижения цели
            value3 = self.ui_personal_plan.tableViewAdditionalGoals.model().data(self.ui_personal_plan.tableViewAdditionalGoals.model().index(row, 3)).replace(' ', '')
            self.ui_personal_plan.spinBoxAgeGoal.setValue(int(value3))
            # TODO Имеющиеся накопления для достижения цели
            value4 = self.ui_personal_plan.tableViewAdditionalGoals.model().data(self.ui_personal_plan.tableViewAdditionalGoals.model().index(row, 4)).replace(' ', '')
            self.ui_personal_plan.spinBoxMoneyForGoal.setValue(int(value4))
            """
    
    def on_cell_activated(self, index):
        """Данные в выбранной строке таблицы"""
        row = index.row()
        # col = index.column()
        # print("Активирована ячейка: строка {row}, столбец {col}".format(row=row, col=col))
        # print("Данные: {index_data}".format(index_data=index.data()))
        # Данные: index.data() или модель.index(row, col).data()
        
        # TODO Ф.И.О.
        value1 = self.ui_employes_catalog.tableView.model().data(self.ui_employes_catalog.tableView.model().index(row, 1))
        self.ui_employes_catalog.lineEdit.setText(value1)
        
        """
        # TODO Оценка цели
        value2 = self.ui_personal_plan.tableViewAdditionalGoals.model().data(self.ui_personal_plan.tableViewAdditionalGoals.model().index(row, 2)).replace(' ', '')
        self.ui_personal_plan.spinBoxGoalEvaluation.setValue(int(value2))
        # TODO Желаемый возраст достижения цели
        value3 = self.ui_personal_plan.tableViewAdditionalGoals.model().data(self.ui_personal_plan.tableViewAdditionalGoals.model().index(row, 3)).replace(' ', '')
        self.ui_personal_plan.spinBoxAgeGoal.setValue(int(value3))
        # TODO Имеющиеся накопления для достижения цели
        value4 = self.ui_personal_plan.tableViewAdditionalGoals.model().data(self.ui_personal_plan.tableViewAdditionalGoals.model().index(row, 4)).replace(' ', '')
        self.ui_personal_plan.spinBoxMoneyForGoal.setValue(int(value4))
        """
    
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    def bool_enabled_elements(self, boolean) -> None:
        """Активация / деактивация элементов управления"""
        self.ui_journal.btnSave.setEnabled(not boolean)
        self.ui_journal.btnCancel.setEnabled(not boolean)
        self.ui_journal.btnInsert.setEnabled(boolean)
        self.ui_journal.btnUpdate.setEnabled(boolean)
        self.ui_journal.btnDelete.setEnabled(boolean)
        
        self.ui_journal.groupBoxElements.setEnabled(not boolean)
        
        if (self.ui_journal.groupBoxElements.isEnabled()) and (not self.ui_journal.checkBox_2.isChecked()):
            self.ui_journal.timeEdit.setEnabled(False)
        else:
            self.ui_journal.timeEdit.setEnabled(True)
        
        """
        self.ui_journal.lineEditNameGoal.setEnabled(not boolean)
        self.ui_journal.spinBoxGoalEvaluation.setEnabled(not boolean)
        self.ui_journal.spinBoxAgeGoal.setEnabled(not boolean)
        self.ui_journal.spinBoxMoneyForGoal.setEnabled(not boolean)
        """
        
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
            self.dict_boss_fio[fio] = _id   # Заполняем словарь (справочник)
            
            self.ui_journal.comboBoxBoss.addItem(fio, _id)  # Добавляем Ф.И.О. и id
            
            # совмещаем QLineEdit с данными
            ################################################
            from PyQt5.QtWidgets import QCompleter
            self.completer_lineEditBossFio = QCompleter(self.list_boss_fio)
            self.ui_journal.lineEditFindBossFio.setCompleter(self.completer_lineEditBossFio)
            ################################################
            
            # Выводим id сотрудника
            ################################################
            # self.ui_journal.lineEditFindBossFio.editingFinished.connect(self.id_person_show)
    
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
    
    def id_data_current_boss_fio(self) -> None:
        # self.id_person = self.ui_journal.comboBoxBoss.currentData()
        # _id = self.ui_journal.comboBoxBoss.currentData()
        # txt = self.ui_journal.comboBoxBoss.currentText()
        pass
    ####################################################################################################################


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
            self.dict_employe_fio[fio] = _id   # Заполняем словарь (справочник)
            
            self.ui_journal.comboBoxEmploye.addItem(fio, _id)  # Добавляем Ф.И.О. и id
            
            # совмещаем QLineEdit с данными
            ################################################
            from PyQt5.QtWidgets import QCompleter
            self.completer_lineEditEmployeFio = QCompleter(self.list_employe_fio)
            self.ui_journal.lineEditFindEmployeFio.setCompleter(self.completer_lineEditEmployeFio)
            ################################################
            
            # Выводим id сотрудника
            ################################################
            # self.ui_journal.lineEditFindEmployeFio.editingFinished.connect(self.id_person_show)
    
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
    
    def id_data_current_employe_fio(self) -> None:
        # self.id_person = self.ui_journal.comboBoxEmploye.currentData()
        # _id = self.ui_journal.comboBoxEmploye.currentData()
        # txt = self.ui_journal.comboBoxEmploye.currentText()
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
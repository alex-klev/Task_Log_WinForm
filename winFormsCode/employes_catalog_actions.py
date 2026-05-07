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
from winForms import Ui_EmployesCatalogWindow
# from winForms.employes_catalog import Ui_EmployesCatalogWindow

from dbCode import EmployesCatalogDb
# import dbCode.db_actions as db_actions


class EmployesCatalog(QtWidgets.QMainWindow):
    def __init__(self, **kwargs):
        # QtWidgets.QMainWindow.__init__(self)  # Вызываем конструктор базового класса
        # super(EmployesCatalog, self).__init__()  # Вызываем конструктор базового класса
        super().__init__()  # Вызываем конструктор базового класса
        self.ui_employes_catalog = Ui_EmployesCatalogWindow()  # Создаем экземпляр Ui_EmployesCatalogWindow
        self.ui_employes_catalog.setupUi(self)  # Загружаем интерфейс из файла
        
        self.show_new_form = False  # проверка загрузки новой формы
        
        self.setSql = ""
        
        """
        self.ui_persons.btnFilterOn.clicked.connect(self.load_data_filter)  # Фильтрация
        self.ui_persons.btnFilterOff.clicked.connect(self.load_data_no_filter)  # Отключить фильтрацию
        """
        
        self.ui_employes_catalog.btnInsert.clicked.connect(self.add_data_to_db)  # Добавить запись в таблицу
        self.ui_employes_catalog.btnUpdate.clicked.connect(self.update_data_in_db)  # Обновить запись в таблице
        self.ui_employes_catalog.btnDelete.clicked.connect(self.delete_data_from_db)  # Удалить запись из таблицы
        self.ui_employes_catalog.btnSave.clicked.connect(self.save_data_in_db)  # Сохранить запись в таблице
        self.ui_employes_catalog.btnCancel.clicked.connect(self.cancel)  # Отменить запись из таблицы
        
        self.ui_employes_catalog.tableView.clicked.connect(self.on_cell_clicked)  # Клик по ячейке
        self.ui_employes_catalog.tableView.activated.connect(self.on_cell_activated)  # Данные в выбранной строке таблицы
        # self.ui_employes_catalog.tableView.pressed.connect(self.on_cell_pressed)  # Данные в выбранной строке таблицы
        
        self.ui_employes_catalog.lineEdit.setEnabled(False)
        
        # Создаём модель таблицы
        table_model = TableModel(
            ui=self.ui_employes_catalog, # Передаём ссылку на ui_employes_catalog
            parent_window=self  # Передаём ссылку на главное окно
        )
        table_model.create_model_table()  
        
        # Загружаем данные в таблицу
        self.load_data_db()
        
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
            employes_catalog = EmployesCatalogDb()
            data = employes_catalog.load_data()
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
                
                model = self.ui_employes_catalog.tableView.model()
                if model and model.rowCount() > 0:
                    model.removeRow(model.rowCount() - 1)
                #! ###########################################
                #! ###########################################
            else:
                def transform_data(row):
                    """Функция для преобразования строки в словарь"""
                    return {
                        'data_id': row[0],
                        'fio': row[1]
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
            self.ui_employes_catalog.tableView.setModel(None)
            return
        
        # 1. Создаём модель: строки = кол-во записей, столбцы = 2
        model = QStandardItemModel(len(data), 2)
        model.setHorizontalHeaderLabels(["data_id", "Ф.И.О.\nисполнителя"])
        
        # 2. Заполняем модель данными
        for row_idx, row_data in enumerate(data):
            # data_id (скрытый)
            model.setItem(row_idx, 0, QStandardItem(str(row_data.get('data_id', ''))))
            
            # Ф.И.О.
            model.setItem(row_idx, 1, QStandardItem(str(row_data.get('fio', ''))))
            
            # Опционально: выравнивание по центру для красоты
            # for col in range(2):
            #     model.item(row_idx, col).setTextAlignment(Qt.AlignCenter)
        
        # 3. Привязываем модель к tableView
        self.ui_employes_catalog.tableView.setModel(model)
        
        # 4. Скрываем столбец data_id (индекс 0)
        self.ui_employes_catalog.tableView.setColumnHidden(0, True)
        
        # 5. Запрещаем редактирование ячеек
        # self.ui_employes_catalog.tableView.setEditTriggers(QTableView.NoEditTriggers)  # QTableView наследуется от QAbstractItemView
        self.ui_employes_catalog.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # 6. Опционально: автоматическая подгонка ширины столбцов под содержимое
        header = self.ui_employes_catalog.tableView.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
    
    def add_data_to_db(self) -> None:
        """Добавление данных в базу данных"""
        # Установка фокуса на поле Ф.И.О.
        self.ui_employes_catalog.lineEdit.setFocus(True)
        # Активация / деактивация элементов
        self.bool_enabled_elements(False)
        # Очистка полей
        self.clear_line_edit()
        # Выбор режима
        self.setSql = "Insert"
        # print(self.setSql)
    
    def update_data_in_db(self) -> None:
        """Изменение данных в базе данных"""
        # Установка фокуса на поле Ф.И.О.
        self.ui_employes_catalog.lineEdit.setFocus(True)
        # Выбранная строка
        current_row = self.ui_employes_catalog.tableView.currentIndex().row()
        
        # if current_row < 0:
        if current_row == -1:
            QMessageBox.warning(self, "Внимание", "Выберите запись для редактирования")
            return
        else:
            # Синхронизация значения полей со значением в таблице
            self.cell_clicked(current_row, 0)
            # Установка фокуса на поле название цели
            self.ui_employes_catalog.lineEdit.setFocus(True)
            # Активация / деактивация элементов
            self.bool_enabled_elements(False)
            # Выбор режима
            self.setSql = "Update"
            # print(self.setSql)
    
    def delete_data_from_db(self) -> None:
        """Удаление данных из базы данных"""
        # Выбранная строка
        current_row = self.ui_employes_catalog.tableView.currentIndex().row()
        
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
                                          self.ui_employes_catalog.tableView.model().index(row, 1)),
                                          
                                      QMessageBox.Yes | QMessageBox.No)
        
        if delete == QMessageBox.Yes:
        """
        
        # Создаем диалог вручную, а не через статический метод
        msg_box = QtWidgets.QMessageBox()
        
        msg_box.setWindowTitle("Удаление записи")
        msg_box.setText("Вы уверены, что хотите удалить запись '{0}' ?".format(self.ui_employes_catalog.tableView.model().data(self.ui_employes_catalog.tableView.model().index(current_row, 1))))
            
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
            current_row = self.ui_employes_catalog.tableView.currentIndex().row()
            # if current_row < 0:
            if current_row == -1:
                return
            else:
                
                data_id = self.ui_employes_catalog.tableView.model().index(current_row, 0).data().strip()  # data.get('data_id') # id записи, присвоенная в таблице на стороне клиента (Date.now().toString() дата в виде текста)
                
                if data_id:
                    try:
                        employes_catalog = EmployesCatalogDb(
                            p0=data_id, 
                            p2=self.get_current_datetime()
                        )
                        employes_catalog.mark_to_deleted()
                        # employes_catalog.delete_data()  # Полное удаление данных
                    except Exception as e:
                        # QMessageBox.warning(self, 'Внимание', "Ошибка при удалении дополнительных целей для исполнителя {id_user}: {e}".format(id_user=self.id_user, e=e))
                        QMessageBox.warning(self, 'Внимание', "Ошибка при удалении {e}".format(e=e))
                        return
                    else:
                        pass
                else:
                    # QMessageBox.warning(self, 'Внимание', "Ошибка при удалении дополнительных целей для исполнителя {id_user}: {e}".format(id_user=self.id_user, e=e))
                    QMessageBox.warning(self, 'Внимание', "Ошибка при удалении {e}".format(e=e))
                    return
            
            # Заполнение таблицы
            self.load_data_db()
            # Очистка полей
            self.cancel()
            # Сброс режима SQL
            self.setSql = ""
    
    def save_data_in_db(self) -> None:
        """Активация / деактивация кнопок"""
        # Установка фокуса на поле Ф.И.О.
        self.ui_employes_catalog.lineEdit.setFocus(True)
        # Сохранение данных
        if self.setSql == "Insert":
            
            data_id = str(int(time.time() * 1000))  # data.get('data_id') # id записи, присвоенная в таблице на стороне клиента (Date.now().toString() дата в виде текста)
            fio = self.ui_employes_catalog.lineEdit.text().strip()  # Ф.И.О.
            
            if not fio or fio.strip() == "":
                QMessageBox.warning(self, "Внимание", "Ф.И.О. не указана")
                return
            else:
                # Проверка дублирования данных
                employes_catalog = EmployesCatalogDb(
                    p0=data_id, 
                    p1=fio
                )
                employes_catalog.double_data()
                
                if employes_catalog.double_data() != []:
                    QMessageBox.warning(self, 'Внимание', 'Запись исполнителя "{0}" уже существует'.format(fio))
                    return
                
                try:
                    employes_catalog = EmployesCatalogDb(
                        p0=data_id, 
                        p1=fio, 
                        p2=self.get_current_datetime()
                    )
                    employes_catalog.insert_data()
                except Exception as e:
                    QMessageBox.warning(self, 'Внимание', "Ошибка при добавлении данных {e}".format(e=e))
                    return
        
        if self.setSql == "Update":
            
            current_row = self.ui_employes_catalog.tableView.currentIndex().row()
            # if current_row < 0:
            if current_row == -1:
                return
            
            data_id = self.ui_employes_catalog.tableView.model().index(current_row, 0).data().strip()  # data.get('data_id') # id записи, присвоенная в таблице на стороне клиента (Date.now().toString() дата в виде текста)
            fio = self.ui_employes_catalog.lineEdit.text().strip()  # Ф.И.О.
            
            if not fio or fio.strip() == "":
                QMessageBox.warning(self, "Внимание", "Ф.И.О. не указана")
                return
            else:
                # Проверка дублирования данных
                employes_catalog = EmployesCatalogDb(
                    p0=data_id, 
                    p1=fio
                )
                employes_catalog.double_data()
                
                if employes_catalog.double_data() != []:
                    QMessageBox.warning(self, 'Внимание', 'Запись исполнителя "{0}" уже существует'.format(fio))
                    return
                
                try:
                    employes_catalog = EmployesCatalogDb(
                        p0=data_id, 
                        p1=fio, 
                        p2=self.get_current_datetime()
                    )
                    employes_catalog.update_data()
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
        # Установка фокуса на поле название цели
        self.ui_employes_catalog.lineEdit.setFocus(True)
        # Активация / деактивация элементов
        self.bool_enabled_elements(True)
        
        # Выбранная строка
        current_row = self.ui_employes_catalog.tableView.currentIndex().row()
        # if current_row < 0:
        if current_row == -1:
            return
        
        # TODO Ф.И.О.
        value1 = self.ui_employes_catalog.tableView.model().data(self.ui_employes_catalog.tableView.model().index(current_row, 1))
        self.ui_employes_catalog.lineEdit.setText(value1)
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
        self.ui_employes_catalog.btnSave.setEnabled(not boolean)
        self.ui_employes_catalog.btnCancel.setEnabled(not boolean)
        self.ui_employes_catalog.btnInsert.setEnabled(boolean)
        self.ui_employes_catalog.btnUpdate.setEnabled(boolean)
        self.ui_employes_catalog.btnDelete.setEnabled(boolean)
        
        self.ui_employes_catalog.lineEdit.setEnabled(not boolean)
        # self.ui_employes_catalog.lineEditName.setEnabled(not boolean)
        # self.ui_employes_catalog.lineEditPatronymic.setEnabled(not boolean)
        
        self.ui_employes_catalog.lineEditFilter.setEnabled(boolean)
        self.ui_employes_catalog.lineEditFilter.setText("")
        
        self.ui_employes_catalog.tableView.setEnabled(boolean)
    
    def clear_line_edit(self) -> None:
        """Очистка полей"""
        self.ui_employes_catalog.lineEdit.setText("")
        # self.ui_employes_catalog.spinBoxGoalEvaluation.setValue(0)
        # self.ui_employes_catalog.spinBoxAgeGoal.setValue(0)
        # self.ui_employes_catalog.spinBoxMoneyForGoal.setValue(0)


class TableModel:
    # Для Astra Linux 1.6 (Python 3.5.3)
    def __init__(self, ui, parent_window, **kwargs):
        self.ui_employes_catalog = ui  # передаём ссылку на UI (type: Ui_BosesCatalogWindow)
        self.parent_window = parent_window  # Сохраняем ссылку на родительское окно
    
    """
    def __init__(self, ui: Ui_BosesCatalogWindow, parent_window, **kwargs):  # Добавлена аннотация типа (аннотация - подсказки для разработчиков)
        self.ui_employes_catalog: Ui_BosesCatalogWindow = ui  # Аннотация типа для атрибута и передаём ссылку на UI (аннотация - подсказки для разработчиков)
        self.parent_window = parent_window  # Сохраняем ссылку на родительское окно
    """
    
    def create_model_table(self):
        """Создаём модель таблицы"""
        
        # 1. Уже есть модель, связанная с tableView
        model = self.ui_employes_catalog.tableView.model()
        
        # 2. Устанавливаем заголовки
        if model is not None:
            headers = [
                "data_id", 
                "Ф.И.О.\nисполнителя"
            ]
            model.setHorizontalHeaderLabels(headers)
        else:
            # 1. Создаем модель
            model = QStandardItemModel()
            
            # 2. Устанавливаем заголовки
            headers = [
                "data_id", 
                "Ф.И.О.\nисполнителя"
            ]
            model.setHorizontalHeaderLabels(headers)
            
            # 3. Присваиваем модель таблице
            self.ui_employes_catalog.tableView.setModel(model)
            
            # 3. Присваиваем модель таблице
            self.ui_employes_catalog.tableView.setModel(model)
            
            # 4. Скрываем столбец data_id (индекс 0)
            self.ui_employes_catalog.tableView.setColumnHidden(0, True)
            
            # 5. Запрещаем редактирование ячеек
            # self.ui_employes_catalog.tableView.setEditTriggers(QTableView.NoEditTriggers)  # QTableView наследуется от QAbstractItemView
            self.ui_employes_catalog.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
            
            # 6. Опционально: автоматическая подгонка ширины столбцов под содержимое
            header = self.ui_employes_catalog.tableView.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeToContents)
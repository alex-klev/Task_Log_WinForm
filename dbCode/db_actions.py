import sqlite3 as sl
import os

# conn = sl.connect("classnost_db_PyQt5.db") # Создаем подключение
# conn = sl.connect("db\TaskLogDb.db") # Создаем подключение
"""
# Создаем подключение (Объединение компонентов пути)
conn = sl.connect(os.path.join("db", "TaskLogDb.db"))
# Получаем курсор
cursor = conn.cursor()
# Включение поддержки внешних ключей
conn.execute("PRAGMA foreign_keys = ON;")
"""

#! ### Справочник руководителей ###
class BossesCatalogDb:
    """Справочник руководителей"""
    def __init__(self, **kwargs) -> None:
        self.data_id = kwargs.get('p0')  # id записи
        self.fio = kwargs.get('p1')  # Ф.И.О. руководителя
        self.current_datetime = kwargs.get('p2')  # Текущая дата и время
    
    #! #############################################################
    #! #############################################################
    #! #############################################################
    @staticmethod
    def lower_cyrillic(text):
        """
        if not text:
            return text
        cyrillic_upper = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        cyrillic_lower = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
        trans_table = str.maketrans(cyrillic_upper, cyrillic_lower)
        return text.translate(trans_table)
        """
        return text.lower()
    
    def double_data(self) -> list:
        """Проверка дублирования данных"""
        with sl.connect(os.path.join("db", "TaskLogDb.db")) as conn:
            # Получаем курсор
            cursor = conn.cursor()
            # Включение поддержки внешних ключей
            conn.execute("PRAGMA foreign_keys = ON;")
            
            # conn.create_function("lower_cyrillic", 1, self.lower_cyrillic)  #TODO Создаем пользовательскую функцию в SQLite
            
            try:
                """
                data = cursor.execute("SELECT 1 FROM bosses "
                                        "WHERE lower_cyrillic(fio) = lower_cyrillic(?)", 
                                        (self.fio,)).fetchall()
                """
                data = cursor.execute("SELECT 1 FROM bosses "
                                        "WHERE fio = ?", 
                                        (self.fio,)).fetchall()
            except sl.Error as err:
                print("Ошибка при работе с базой данных ", err)
                return [('',)]  # Возвращаем пустой список кортежа
            else:
                # print("Connect OK")
                return data
    #! #############################################################
    #! #############################################################
    #! #############################################################
    
    def load_data(self):
        """Загружаем данные из таблицы"""
        with sl.connect(os.path.join("db", "TaskLogDb.db")) as conn:
            # Получаем курсор
            cursor = conn.cursor()
            # Включение поддержки внешних ключей
            conn.execute("PRAGMA foreign_keys = ON;")
            
            try:
                # получаем все данные из таблицы bosses
                # execute принимает в качестве параметров кортеж. Запятая нужна после self.user_id
                """
                cursor.execute("SELECT opros_id, user_id, total_score, investment_term, result_type, description, current_datetime FROM opros "
                                "WHERE user_id = ?", (self.user_id,))
                """
                
                data = cursor.execute("SELECT data_id, fio FROM bosses "
                                      "WHERE fio <> 'нет данных' ").fetchall()
                
                # data = cursor.execute("SELECT data_id, fio FROM bosses ").fetchall()
                
                # print((cursor.fetchall()))
                # data = cursor.fetchall()
                # print(data)
            except sl.Error as err:
                print("Ошибка при работе с базой данных ", err)
                return [('',)]  # Возвращаем пустой список кортежа
            else:
                return data
    
    def insert_data(self) -> None:
        with sl.connect(os.path.join("db", "TaskLogDb.db")) as conn:
            # Получаем курсор
            cursor = conn.cursor()
            # Включение поддержки внешних ключей
            conn.execute("PRAGMA foreign_keys = ON;")
            
            try:
                # execute принимает в качестве параметров кортеж. Запятая нужна после data
                # cursor.execute("INSERT INTO table_name (abcd) VALUES(?)", (data,))       
                
                # Вставляем новую запись в таблицу bosses
                cursor.execute("INSERT INTO bosses (data_id, fio, create_datetime) VALUES (?, ?, ?)",
                                (self.data_id, self.fio, self.current_datetime))
            except sl.Error as err:
                print("Ошибка при работе с базой данных ", err)
            else:
                # Выполняем транзакцию
                conn.commit()
    
    def update_data(self) -> None:
        with sl.connect(os.path.join("db", "TaskLogDb.db")) as conn:
            # Получаем курсор
            cursor = conn.cursor()
            # Включение поддержки внешних ключей
            conn.execute("PRAGMA foreign_keys = ON;")
            
            try:
                # Обновляем запись в таблице bosses
                cursor.execute("UPDATE bosses SET fio = ?, create_datetime = ? "
                            "WHERE data_id = ?",
                            (self.fio, self.current_datetime, self.data_id))
            except sl.Error as err:
                print("Ошибка при работе с базой данных ", err)
            else:
                # Выполняем транзакцию
                conn.commit()
    
    def delete_data(self) -> None:
        with sl.connect(os.path.join("db", "TaskLogDb.db")) as conn:
            cursor = conn.cursor()
            conn.execute("PRAGMA foreign_keys = ON;")
            # print(self.user_id)
            # print(self.data_id)
            # print(self.current_datetime)
            try:
                # Удаляем запись в таблице 
                cursor.execute(
                    """DELETE FROM bosses 
                    WHERE data_id = ?""",
                    (self.data_id,))
            except sl.Error as err:
                print("Ошибка при работе с базой данных ", err)
            else:
                conn.commit()
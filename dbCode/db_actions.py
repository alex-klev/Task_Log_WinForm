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
        self.fio = kwargs.get('p1')  # Ф.И.О.
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
                data = cursor.execute("SELECT 1 FROM reference_bosses "
                                        "WHERE lower_cyrillic(fio) = lower_cyrillic(?)", 
                                        (self.fio,)).fetchall()
                """
                data = cursor.execute("SELECT 1 FROM reference_bosses "
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
                # получаем все данные из таблицы reference_bosses
                # execute принимает в качестве параметров кортеж. Запятая нужна после self.user_id
                data = cursor.execute("SELECT data_id, fio FROM reference_bosses "
                                      "WHERE deleted_flg = 0 AND fio <> 'нет данных' "
                                    ).fetchall()
                
                # data = cursor.execute("SELECT data_id, fio FROM reference_bosses ").fetchall()
                
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
                
                # Вставляем новую запись в таблицу reference_bosses
                cursor.execute("INSERT INTO reference_bosses (data_id, fio, current_datetime) VALUES (?, ?, ?)",
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
                # Обновляем запись в таблице reference_bosses
                cursor.execute("UPDATE reference_bosses SET fio = ?, current_datetime = ? "
                            "WHERE data_id = ? AND deleted_flg = 0",
                            (self.fio, self.current_datetime, self.data_id))
            except sl.Error as err:
                print("Ошибка при работе с базой данных ", err)
            else:
                # Выполняем транзакцию
                conn.commit()
    
    def mark_to_deleted(self) -> None:
        with sl.connect(os.path.join("db", "TaskLogDb.db")) as conn:
            cursor = conn.cursor()
            conn.execute("PRAGMA foreign_keys = ON;")
            # print(self.user_id)
            # print(self.data_id)
            # print(self.current_datetime)
            try:
                # Обновляем запись в таблице
                cursor.execute(
                    """UPDATE reference_bosses 
                    SET deleted_flg = 1, 
                        current_datetime = ?
                    WHERE data_id = ? AND deleted_flg = 0""",
                    (self.current_datetime, self.data_id))
            except sl.Error as err:
                print("Ошибка при работе с базой данных ", err)
            else:
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
                    """DELETE FROM reference_bosses 
                    WHERE data_id = ? AND deleted_flg = 0""",
                    (self.data_id,))
            except sl.Error as err:
                print("Ошибка при работе с базой данных ", err)
            else:
                conn.commit()


#! ### Справочник исполнителей ###
class EmployesCatalogDb:
    """Справочник исполнителей"""
    def __init__(self, **kwargs) -> None:
        self.data_id = kwargs.get('p0')  # id записи
        self.fio = kwargs.get('p1')  # Ф.И.О.
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
                data = cursor.execute("SELECT 1 FROM reference_employes "
                                        "WHERE lower_cyrillic(fio) = lower_cyrillic(?)", 
                                        (self.fio,)).fetchall()
                """
                data = cursor.execute("SELECT 1 FROM reference_employes "
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
                # получаем все данные из таблицы reference_employes
                # execute принимает в качестве параметров кортеж. Запятая нужна после self.user_id
                data = cursor.execute("SELECT data_id, fio FROM reference_employes "
                                      "WHERE deleted_flg = 0 AND fio <> 'нет данных' "
                                    ).fetchall()
                
                # data = cursor.execute("SELECT data_id, fio FROM employes ").fetchall()
                
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
                
                # Вставляем новую запись в таблицу reference_employes
                cursor.execute("INSERT INTO reference_employes (data_id, fio, current_datetime) VALUES (?, ?, ?)",
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
                # Обновляем запись в таблице reference_employes
                cursor.execute("UPDATE reference_employes SET fio = ?, current_datetime = ? "
                            "WHERE data_id = ? AND deleted_flg = 0",
                            (self.fio, self.current_datetime, self.data_id))
            except sl.Error as err:
                print("Ошибка при работе с базой данных ", err)
            else:
                # Выполняем транзакцию
                conn.commit()
    
    def mark_to_deleted(self) -> None:
        with sl.connect(os.path.join("db", "TaskLogDb.db")) as conn:
            cursor = conn.cursor()
            conn.execute("PRAGMA foreign_keys = ON;")
            # print(self.user_id)
            # print(self.data_id)
            # print(self.current_datetime)
            try:
                # Обновляем запись в таблице
                cursor.execute(
                    """UPDATE reference_employes 
                    SET deleted_flg = 1, 
                        current_datetime = ?
                    WHERE data_id = ? AND deleted_flg = 0""",
                    (self.current_datetime, self.data_id))
            except sl.Error as err:
                print("Ошибка при работе с базой данных ", err)
            else:
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
                    """DELETE FROM reference_employes 
                    WHERE data_id = ? AND deleted_flg = 0""",
                    (self.data_id,))
            except sl.Error as err:
                print("Ошибка при работе с базой данных ", err)
            else:
                conn.commit()


class JournalDb:
    """Справочник исполнителей"""
    def __init__(self, **kwargs) -> None:
        self.data_id = kwargs.get('p0')  # id записи
        self.boss_id = kwargs.get('p1')  # id руководителя
        self.employee_id = kwargs.get('p2')  # id исполнителя
        self.task = kwargs.get('p3')  # задание
        self.note = kwargs.get('p4', None)  # примечание
        self.date_start_task = kwargs.get('p5')  # дата начала задачи
        self.date_end_task = kwargs.get('p6')  # дата окончания задачи
        self.time_end_task = kwargs.get('p7', None)  # время окончания задачи
        self.done = kwargs.get('p8', 0)  # отметка о выполнении
        self.current_datetime = kwargs.get('p9')  # Текущая дата и время
        
        self.date_start_task_between = kwargs.get('p10')  # фильтр от
        self.date_end_task_between = kwargs.get('p11')  # фильтр до
        
        """
        print(self.data_id, 
                self.boss_id,
                self.employee_id, 
                self.task,
                self.note,
                self.date_start_task,
                self.date_end_task,
                self.time_end_task,
                self.done,
                self.current_datetime,
        )
        """
        
        # self.lang = kwargs.get("lang", 'ru')  # Язык приложения (Если значение is None, тогда значение = 'ru')
    
    def load_data(self):
        """Загружаем данные из таблицы"""
        with sl.connect(os.path.join("db", "TaskLogDb.db")) as conn:
            # Получаем курсор
            cursor = conn.cursor()
            # Включение поддержки внешних ключей
            conn.execute("PRAGMA foreign_keys = ON;")
            
            try:
                # получаем все данные из таблицы reference_employes
                # execute принимает в качестве параметров кортеж. Запятая нужна после self.user_id
                data = cursor.execute(
                    """SELECT 
                            j.data_id,
                            j.task,
                            -- j.note,
                            IFNULL(j.note, '-') AS note,
                            strftime('%d.%m.%Y', j.date_start_task) AS date_start_task,
                            strftime('%d.%m.%Y', j.date_end_task) AS date_end_task,
                            -- IIF(j.time_end_task = '00:00','нет данных', strftime('%H:%M', j.time_end_task)) AS time_end_task,
                            IFNULL(j.time_end_task, '-') AS time_end_task,
                            -- COALESCE(j.time_end_task, 'нет данных') AS time_end_task,
                            re.fio AS employee_fio,
                            rb.fio AS boss_fio,
                            CAST(ROUND(julianday(j.date_end_task) - julianday(date('now', 'localtime')), 0) AS INTEGER) AS days_difference,
                            -- CAST(CEIL(julianday(j.date_end_task) - julianday(date('now', 'localtime'))) AS INTEGER) AS days_difference,
                            j.done,
                            j.employee_id,
                            j.boss_id
                        FROM journal j
                        LEFT JOIN reference_bosses rb ON j.boss_id = rb.boss_id
                        LEFT JOIN reference_employes re ON j.employee_id = re.employee_id
                        WHERE j.date_end_task BETWEEN ? AND ?
                        ORDER BY done, days_difference
                    """,
                    (self.date_start_task_between, self.date_end_task_between)).fetchall()
                
                """
                data = cursor.execute("SELECT additional_goal_id, goal_name, goal_assessment, age, savings, years_left, capital, investing, investing_savings, ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY additional_goal_id) AS 'row_number' FROM additional_goals "
                                "WHERE user_id = ? "
                                "ORDER BY row_number", (self.user_id,)).fetchall()
                """
                
                # data = cursor.execute("SELECT data_id, fio FROM employes ").fetchall()
                
                # print((cursor.fetchall()))
                # data = cursor.fetchall()
                # print(data)
            except sl.Error as err:
                print("Ошибка при работе с базой данных ", err)
                return [('',)]  # Возвращаем пустой список кортежа
            else:
                return data
    
    def load_data_bosses(self):
        """Загружаем данные руководителей из таблицы"""
        with sl.connect(os.path.join("db", "TaskLogDb.db")) as conn:
            # Получаем курсор
            cursor = conn.cursor()
            # Включение поддержки внешних ключей
            conn.execute("PRAGMA foreign_keys = ON;")
            
            try:
                # получаем все данные из таблицы reference_bosses
                # execute принимает в качестве параметров кортеж. Запятая нужна после self.user_id
                data = cursor.execute("SELECT boss_id, fio FROM reference_bosses "
                                      "WHERE deleted_flg = 0 "
                                      "ORDER BY fio").fetchall()
                
                # data = cursor.execute("SELECT data_id, fio FROM reference_bosses ").fetchall()
                
                # print((cursor.fetchall()))
                # data = cursor.fetchall()
                # print(data)
            except sl.Error as err:
                print("Ошибка при работе с базой данных ", err)
                return [('',)]  # Возвращаем пустой список кортежа
            else:
                return data
    
    def load_data_employes(self):
        """Загружаем данные исполнителей из таблицы"""
        with sl.connect(os.path.join("db", "TaskLogDb.db")) as conn:
            # Получаем курсор
            cursor = conn.cursor()
            # Включение поддержки внешних ключей
            conn.execute("PRAGMA foreign_keys = ON;")
            
            try:
                # получаем все данные из таблицы reference_employes
                # execute принимает в качестве параметров кортеж. Запятая нужна после self.user_id
                data = cursor.execute("SELECT employee_id, fio FROM reference_employes "
                                      "WHERE deleted_flg = 0 "
                                      "ORDER BY fio").fetchall()
                
                # data = cursor.execute("SELECT data_id, fio FROM employes ").fetchall()
                
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
                
                # Вставляем новую запись в таблицу
                cursor.execute(
                    """INSERT INTO journal (
                        data_id, 
                        boss_id, 
                        employee_id, 
                        task, 
                        note, 
                        date_start_task, 
                        date_end_task, 
                        time_end_task, 
                        done, 
                        current_datetime
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        self.data_id, self.boss_id, self.employee_id, self.task, self.note, 
                        self.date_start_task, self.date_end_task, self.time_end_task, self.done, self.current_datetime
                    ))
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
                # Обновляем запись в таблице
                cursor.execute(
                    """UPDATE journal SET 
                            boss_id = ?, 
                            employee_id = ?, 
                            task = ?, 
                            note = ?, 
                            date_start_task = ?, 
                            date_end_task = ?, 
                            time_end_task = ?, 
                            done = ?, 
                            current_datetime = ?
                        WHERE data_id = ?""",
                        (
                            self.boss_id, self.employee_id, self.task, self.note, 
                            self.date_start_task, self.date_end_task, self.time_end_task, self.done, self.current_datetime,
                            self.data_id
                        ))
            except sl.Error as err:
                print("Ошибка при работе с базой данных ", err)
            else:
                # Выполняем транзакцию
                conn.commit()
    
    def delete_data(self) -> None:
        with sl.connect(os.path.join("db", "TaskLogDb.db")) as conn:
            # Получаем курсор
            cursor = conn.cursor()
            # Включение поддержки внешних ключей
            conn.execute("PRAGMA foreign_keys = ON;")
            
            try:
                # Удаляем запись в таблице
                cursor.execute("DELETE FROM Journal WHERE data_id = ?", (self.data_id,))
            except sl.Error as err:
                print("Ошибка при работе с базой данных ", err)
            else:
                # Выполняем транзакцию
                conn.commit()


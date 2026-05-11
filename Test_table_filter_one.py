import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout,
    QWidget, QLabel, QDateTimeEdit, QPushButton
)
from PyQt5.QtCore import QSortFilterProxyModel, QDateTime, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class DateFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._min_date = QDateTime()  # пустая дата означает "без нижней границы"
        self._max_date = QDateTime()

    def set_min_date(self, date):
        self._min_date = date
        self.invalidateFilter()  # перезапускаем фильтрацию

    def set_max_date(self, date):
        self._max_date = date
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        # Получаем индекс столбца с датой (например, столбец 1)
        date_index = self.sourceModel().index(source_row, 1, source_parent)
        date_value = date_index.data(Qt.UserRole)  # или Qt.DisplayRole, если дата хранится как QDateTime

        # Если данные не являются QDateTime, попробуем преобразовать
        if not isinstance(date_value, QDateTime):
            # Можно также хранить строку и парсить её, но лучше использовать UserRole с QDateTime
            return True  # или False в зависимости от требований

        # Проверка нижней границы
        if self._min_date.isValid() and date_value < self._min_date:
            return False
        # Проверка верхней границы
        if self._max_date.isValid() and date_value > self._max_date:
            return False
        return True

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Фильтр по диапазону дат")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Таблица
        self.table = QTableView()
        layout.addWidget(self.table)

        # Модель данных
        self.model = QStandardItemModel(0, 3)
        self.model.setHorizontalHeaderLabels(["Название", "Дата", "Комментарий"])
        self.table.setModel(self.model)

        # Прокси-модель
        self.proxy = DateFilterProxyModel()
        self.proxy.setSourceModel(self.model)
        self.table.setModel(self.proxy)

        # Заполним тестовыми данными
        self.fill_data()

        # Элементы управления фильтром
        layout.addWidget(QLabel("Дата с:"))
        self.start_date_edit = QDateTimeEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDateTime(QDateTime.currentDateTime().addDays(-7))
        layout.addWidget(self.start_date_edit)

        layout.addWidget(QLabel("Дата по:"))
        self.end_date_edit = QDateTimeEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDateTime(QDateTime.currentDateTime().addDays(7))
        layout.addWidget(self.end_date_edit)

        btn = QPushButton("Применить фильтр")
        btn.clicked.connect(self.apply_filter)
        layout.addWidget(btn)

    def fill_data(self):
        # Добавим несколько строк с датами
        data = [
            ("Событие А", QDateTime(2025, 5, 1, 12, 0)),
            ("Событие Б", QDateTime(2025, 5, 5, 9, 30)),
            ("Событие В", QDateTime(2025, 5, 10, 18, 45)),
            ("Событие Г", QDateTime(2025, 5, 15, 10, 0)),
            ("Событие Д", QDateTime(2025, 5, 20, 22, 15)),
        ]
        for name, dt in data:
            row = self.model.rowCount()
            self.model.insertRow(row)
            self.model.setItem(row, 0, QStandardItem(name))
            # Для даты создаём элемент и сохраняем QDateTime через UserRole
            item = QStandardItem()
            item.setData(dt, Qt.UserRole)
            item.setText(dt.toString("dd.MM.yyyy hh:mm"))
            self.model.setItem(row, 1, item)
            self.model.setItem(row, 2, QStandardItem("..."))

    def apply_filter(self):
        min_date = self.start_date_edit.dateTime()
        max_date = self.end_date_edit.dateTime()
        self.proxy.set_min_date(min_date)
        self.proxy.set_max_date(max_date)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 300)
    window.show()
    sys.exit(app.exec_())
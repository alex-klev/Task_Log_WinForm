import sys
from PyQt5.QtCore import QDate, QDateTime, Qt, QSortFilterProxyModel, QTime
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout, QWidget,
    QDateEdit, QHBoxLayout, QLabel
)


class DateRangeFilterProxyModel(QSortFilterProxyModel):
    """Прокси-модель для фильтрации по интервалу дат в двух столбцах."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_from = QDate()      # начальная граница (пустая - без ограничения)
        self.filter_to = QDate()        # конечная граница

    def setFilterDates(self, from_date: QDate, to_date: QDate):
        """Установить диапазон фильтрации."""
        self.filter_from = from_date
        self.filter_to = to_date
        self.invalidateFilter()  # принудительно перезапустить фильтрацию

    def filterAcceptsRow(self, source_row: int, source_parent) -> bool:
        # Получаем индексы столбцов с датами (0 и 1 для примера)
        idx_start = self.sourceModel().index(source_row, 0, source_parent)
        idx_end = self.sourceModel().index(source_row, 1, source_parent)

        # Извлекаем даты из модели (хранятся как QDateTime)
        start_date = self.sourceModel().data(idx_start, Qt.DisplayRole)
        end_date = self.sourceModel().data(idx_end, Qt.DisplayRole)

        # Преобразуем к QDate (если данные в виде QDateTime или строки)
        if isinstance(start_date, QDateTime):
            start_date = start_date.date()
        if isinstance(end_date, QDateTime):
            end_date = end_date.date()

        # Если даты не валидны – пропускаем строку
        if not start_date.isValid() or not end_date.isValid():
            return False

        # Проверка пересечения интервалов:
        # интервал [start_date, end_date] пересекается с [filter_from, filter_to]
        if self.filter_from.isValid() and self.filter_to.isValid():
            # Задан полный диапазон
            return not (end_date < self.filter_from or start_date > self.filter_to)
        elif self.filter_from.isValid():
            # Задана только нижняя граница
            return end_date >= self.filter_from
        elif self.filter_to.isValid():
            # Задана только верхняя граница
            return start_date <= self.filter_to
        else:
            # Границы не заданы – показываем всё
            return True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Фильтрация по диапазону дат (два столбца)")
        self.setGeometry(100, 100, 800, 400)

        # Центральный виджет и компоновка
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Панель с выбором дат
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Дата от:"))
        self.date_from_edit = QDateEdit()
        self.date_from_edit.setCalendarPopup(True)
        self.date_from_edit.setDate(QDate(2023, 1, 1))
        self.date_from_edit.setSpecialValueText("без ограничения")
        self.date_from_edit.setMinimumDate(QDate(2000, 1, 1))

        filter_layout.addWidget(self.date_from_edit)

        filter_layout.addWidget(QLabel("Дата до:"))
        self.date_to_edit = QDateEdit()
        self.date_to_edit.setCalendarPopup(True)
        self.date_to_edit.setDate(QDate(2023, 12, 31))
        self.date_to_edit.setSpecialValueText("без ограничения")
        self.date_to_edit.setMinimumDate(QDate(2000, 1, 1))

        filter_layout.addWidget(self.date_to_edit)
        layout.addLayout(filter_layout)

        # Таблица и модель
        self.table_view = QTableView()

        # Исходная модель
        self.source_model = QStandardItemModel(0, 2, self)
        self.source_model.setHorizontalHeaderLabels(["Дата начала", "Дата окончания"])

        # Заполним тестовыми данными
        self.fill_data()

        # Прокси-модель
        self.proxy_model = DateRangeFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.source_model)

        self.table_view.setModel(self.proxy_model)
        layout.addWidget(self.table_view)

        # Подключаем сигналы изменения дат
        self.date_from_edit.dateChanged.connect(self.on_filter_changed)
        self.date_to_edit.dateChanged.connect(self.on_filter_changed)

        # Применяем фильтр начально
        self.on_filter_changed()

    def fill_data(self):
        """Добавляем примеры строк с интервалами дат."""
        data = [
            (QDate(2023, 1, 10), QDate(2023, 1, 20)),
            (QDate(2023, 2, 1),  QDate(2023, 2, 28)),
            (QDate(2023, 3, 15), QDate(2023, 4, 10)),
            (QDate(2023, 5, 1),  QDate(2023, 5, 5)),
            (QDate(2022, 12, 1), QDate(2023, 1, 15)),   # переходящий через год
            (QDate(2023, 12, 20), QDate(2024, 1, 10)),  # в следующий год
        ]
        
        for start, end in data:
            item_start = QStandardItem()
            item_start.setData(QDateTime(start, QTime(0, 0, 0), Qt.UTC), Qt.DisplayRole)
            item_end = QStandardItem()
            item_end.setData(QDateTime(end, QTime(0, 0, 0), Qt.UTC), Qt.DisplayRole)
            self.source_model.appendRow([item_start, item_end])
        
        # Растягиваем столбцы по содержимому
        self.table_view.resizeColumnsToContents()
    
    def on_filter_changed(self):
        """Считываем выбранные даты и передаём их в прокси-модель."""
        from_date = self.date_from_edit.date()
        to_date = self.date_to_edit.date()
        # Если пользователь выбрал "без ограничения" (SpecialValueText),
        # то QDateEdit возвращает невалидную дату, что нам и нужно.
        self.proxy_model.setFilterDates(from_date, to_date)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
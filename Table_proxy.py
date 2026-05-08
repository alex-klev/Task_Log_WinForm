import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout, QWidget,
    QLineEdit, QLabel
)
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 1. Создаём исходную модель
        self.source_model = QStandardItemModel(0, 3, self)
        self.source_model.setHorizontalHeaderLabels(["Имя", "Возраст", "Город"])

        # Заполняем данными
        data = [
            ("Анна", 25, "Москва"),
            ("Борис", 32, "Санкт-Петербург"),
            ("Виктор", 28, "Москва"),
            ("Галина", 41, "Казань"),
            ("Дмитрий", 35, "Москва"),
        ]
        for row, (name, age, city) in enumerate(data):
            self.source_model.setItem(row, 0, QStandardItem(name))
            self.source_model.setItem(row, 1, QStandardItem(str(age)))
            self.source_model.setItem(row, 2, QStandardItem(city))

        # 2. Создаём прокси-модель и связываем
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.source_model)

        # Настройка сортировки (по умолчанию сравнение строк, числа надо преобразовывать)
        # Можно указать роль, по которой сортировать (обычно Qt.DisplayRole)
        self.proxy_model.setSortRole(Qt.DisplayRole)

        # Включаем динамическую сортировку (при изменении данных)
        self.proxy_model.setDynamicSortFilter(True)

        # 3. Настройка фильтрации (поиск по столбцу "Имя" - индекс 0)
        self.proxy_model.setFilterKeyColumn(0)  # 0 - первый столбец
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)  # регистронезависимо

        # UI: строка поиска
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Фильтр по имени...")
        self.filter_edit.textChanged.connect(self.on_filter_text_changed)

        # Таблица для отображения
        self.table_view = QTableView()
        self.table_view.setModel(self.proxy_model)  # важно: подключаем прокси, а не исходную модель

        # Включаем сортировку по клику на заголовок
        self.table_view.setSortingEnabled(True)

        # Компоновка
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(QLabel("Поиск:"))
        layout.addWidget(self.filter_edit)
        layout.addWidget(self.table_view)
        self.setCentralWidget(central_widget)

        # Дополнительная настройка внешнего вида
        self.table_view.resizeColumnsToContents()

    def on_filter_text_changed(self, text):
        # Устанавливаем регулярное выражение для фильтрации (можно и строку)
        self.proxy_model.setFilterRegExp(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
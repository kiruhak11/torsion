"""
Модальное окно с эталонными примерами для быстрого расчета.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class ExampleDialog(QDialog):
    """
    Модальное окно с выбором эталонных параметров.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_example = None
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        self.setWindowTitle('📚 Эталонные примеры для расчета')
        self.setModal(True)
        self.setFixedSize(900, 600)
        
        # Стиль окна
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel('📚 Выберите эталонный пример для расчета')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 15px;
                background: white;
                border-radius: 10px;
            }
        """)
        
        # Тень для заголовка
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 3)
        title.setGraphicsEffect(shadow)
        
        layout.addWidget(title)
        
        # Описание
        description = QLabel(
            'Эти примеры основаны на реальных экспериментальных данных.\n'
            'Выберите материал и параметры для автоматического заполнения формы.'
        )
        description.setFont(QFont('Arial', 11))
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet('color: #34495e; padding: 10px;')
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Таблица с примерами
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            '№', 'Материал', 'Диаметр D, мм', 'Длина L, мм', 
            'Макс. момент T, Н·м', 'G эталон, МПа'
        ])
        
        # Стиль таблицы
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                gridline-color: #ecf0f1;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Эталонные примеры
        self.examples = [
            {
                'material': 'Сталь',
                'diameter': 10.0,
                'length': 200.0,
                'max_moment': 100.0,
                'G_reference': 81000,
                'description': 'Стандартный стальной образец'
            },
            {
                'material': 'Сталь',
                'diameter': 15.0,
                'length': 250.0,
                'max_moment': 200.0,
                'G_reference': 81000,
                'description': 'Усиленный стальной образец'
            },
            {
                'material': 'Чугун',
                'diameter': 12.0,
                'length': 180.0,
                'max_moment': 80.0,
                'G_reference': 40000,
                'description': 'Стандартный чугунный образец'
            },
            {
                'material': 'Чугун',
                'diameter': 18.0,
                'length': 220.0,
                'max_moment': 150.0,
                'G_reference': 40000,
                'description': 'Усиленный чугунный образец'
            },
            {
                'material': 'Дерево',
                'diameter': 20.0,
                'length': 300.0,
                'max_moment': 50.0,
                'G_reference': 500,
                'description': 'Деревянный образец (сосна)'
            },
            {
                'material': 'Дерево',
                'diameter': 25.0,
                'length': 350.0,
                'max_moment': 70.0,
                'G_reference': 500,
                'description': 'Деревянный образец (дуб)'
            },
            {
                'material': 'Сталь',
                'diameter': 8.0,
                'length': 150.0,
                'max_moment': 60.0,
                'G_reference': 81000,
                'description': 'Тонкий стальной стержень'
            },
            {
                'material': 'Чугун',
                'diameter': 10.0,
                'length': 200.0,
                'max_moment': 90.0,
                'G_reference': 40000,
                'description': 'Стандартный чугунный вал'
            }
        ]
        
        # Заполнение таблицы
        self.table.setRowCount(len(self.examples))
        
        for i, example in enumerate(self.examples):
            # Номер
            item = QTableWidgetItem(str(i + 1))
            item.setTextAlignment(Qt.AlignCenter)
            item.setFont(QFont('Arial', 11, QFont.Bold))
            self.table.setItem(i, 0, item)
            
            # Материал
            material_item = QTableWidgetItem(example['material'])
            material_item.setFont(QFont('Arial', 11, QFont.Bold))
            if example['material'] == 'Сталь':
                material_item.setForeground(QColor('#3498db'))
            elif example['material'] == 'Чугун':
                material_item.setForeground(QColor('#95a5a6'))
            else:
                material_item.setForeground(QColor('#27ae60'))
            self.table.setItem(i, 1, material_item)
            
            # Параметры
            self.table.setItem(i, 2, QTableWidgetItem(f"{example['diameter']:.1f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{example['length']:.1f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{example['max_moment']:.1f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{example['G_reference']:,.0f}"))
            
            # Выравнивание
            for col in range(2, 6):
                self.table.item(i, col).setTextAlignment(Qt.AlignCenter)
        
        # Автоматическая ширина колонок
        header = self.table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Тень для таблицы
        table_shadow = QGraphicsDropShadowEffect()
        table_shadow.setBlurRadius(20)
        table_shadow.setColor(QColor(0, 0, 0, 40))
        table_shadow.setOffset(0, 5)
        self.table.setGraphicsEffect(table_shadow)
        
        layout.addWidget(self.table)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        select_btn = QPushButton('✅ Выбрать и применить')
        select_btn.setFont(QFont('Arial', 12, QFont.Bold))
        select_btn.setCursor(Qt.PointingHandCursor)
        select_btn.setMinimumHeight(50)
        select_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #2ecc71);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 30px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #229954, stop:1 #27ae60);
            }
            QPushButton:pressed {
                background: #1e8449;
            }
        """)
        select_btn.clicked.connect(self.select_example)
        
        cancel_btn = QPushButton('❌ Отмена')
        cancel_btn.setFont(QFont('Arial', 12, QFont.Bold))
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setMinimumHeight(50)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #95a5a6, stop:1 #bdc3c7);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 30px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7f8c8d, stop:1 #95a5a6);
            }
            QPushButton:pressed {
                background: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(select_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Двойной клик по строке
        self.table.doubleClicked.connect(self.select_example)
    
    def select_example(self):
        """Выбор примера."""
        selected_rows = self.table.selectedIndexes()
        
        if not selected_rows:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, 'Предупреждение', 
                              'Пожалуйста, выберите пример из таблицы!')
            return
        
        row = selected_rows[0].row()
        self.selected_example = self.examples[row]
        self.accept()
    
    def get_selected_example(self):
        """Получение выбранного примера."""
        return self.selected_example


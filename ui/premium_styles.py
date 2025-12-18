"""
Премиум-стили и улучшенный дизайн для приложения.
"""

# Глобальный стиль приложения
GLOBAL_STYLE = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f5f7fa, stop:1 #e8eef5);
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3498db, stop:1 #2980b9);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 13px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5dade2, stop:1 #3498db);
}

QPushButton:pressed {
    background: #2874a6;
}

QPushButton:disabled {
    background: #bdc3c7;
    color: #7f8c8d;
}

QLineEdit, QSpinBox, QDoubleSpinBox {
    padding: 10px;
    border: 2px solid #bdc3c7;
    border-radius: 6px;
    background: white;
    font-size: 12px;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #3498db;
}

QComboBox {
    padding: 10px;
    border: 2px solid #bdc3c7;
    border-radius: 6px;
    background: white;
    font-size: 12px;
}

QComboBox:hover {
    border: 2px solid #3498db;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

QComboBox::down-arrow {
    image: none;
    border: none;
}

QGroupBox {
    border: 2px solid #bdc3c7;
    border-radius: 10px;
    margin-top: 15px;
    padding-top: 20px;
    font-weight: bold;
    font-size: 13px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 5px 15px;
    background: white;
    border-radius: 5px;
}

QProgressBar {
    border: 2px solid #bdc3c7;
    border-radius: 8px;
    text-align: center;
    background: white;
    height: 25px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #27ae60, stop:0.5 #2ecc71, stop:1 #27ae60);
    border-radius: 6px;
}

QTextEdit {
    border: 2px solid #bdc3c7;
    border-radius: 8px;
    background: #f8f9fa;
    padding: 10px;
    font-family: 'Courier New';
    font-size: 11px;
}

QTableWidget {
    border: 2px solid #bdc3c7;
    border-radius: 8px;
    background: white;
    gridline-color: #ecf0f1;
}

QTableWidget::item:selected {
    background-color: #3498db;
    color: white;
}

QHeaderView::section {
    background: #34495e;
    color: white;
    padding: 10px;
    border: none;
    font-weight: bold;
}

QTabWidget::pane {
    border: 2px solid #bdc3c7;
    border-radius: 10px;
    background: white;
    padding: 10px;
}

QTabBar::tab {
    background: #ecf0f1;
    border: 2px solid #bdc3c7;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 12px 24px;
    margin-right: 4px;
    font-weight: bold;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #3498db, stop:1 #2980b9);
    color: white;
}

QTabBar::tab:hover:!selected {
    background: #d5dbdb;
}

QScrollBar:vertical {
    border: none;
    background: #ecf0f1;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #95a5a6;
    min-height: 20px;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background: #7f8c8d;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QStatusBar {
    background: #34495e;
    color: white;
    font-weight: bold;
}
"""

# Стиль для специальных кнопок
BUTTON_STYLES = {
    'primary': """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #27ae60, stop:1 #2ecc71);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 15px 30px;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #229954, stop:1 #27ae60);
        }
        QPushButton:pressed {
            background: #1e8449;
        }
        QPushButton:disabled {
            background: #95a5a6;
        }
    """,
    'secondary': """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3498db, stop:1 #2980b9);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 15px 30px;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #5dade2, stop:1 #3498db);
        }
        QPushButton:pressed {
            background: #2874a6;
        }
        QPushButton:disabled {
            background: #95a5a6;
        }
    """,
    'danger': """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #e74c3c, stop:1 #c0392b);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 15px 30px;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #ec7063, stop:1 #e74c3c);
        }
        QPushButton:pressed {
            background: #a93226;
        }
        QPushButton:disabled {
            background: #95a5a6;
        }
    """,
    'warning': """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #f39c12, stop:1 #e67e22);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 15px 30px;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #f8c471, stop:1 #f39c12);
        }
        QPushButton:pressed {
            background: #d68910;
        }
        QPushButton:disabled {
            background: #95a5a6;
        }
    """,
    'success': """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #27ae60, stop:1 #2ecc71);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 15px 30px;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #52be80, stop:1 #27ae60);
        }
        QPushButton:pressed {
            background: #1e8449;
        }
        QPushButton:disabled {
            background: #95a5a6;
        }
    """,
    'info': """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #9b59b6, stop:1 #8e44ad);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 15px 30px;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #af7ac5, stop:1 #9b59b6);
        }
        QPushButton:pressed {
            background: #7d3c98;
        }
        QPushButton:disabled {
            background: #95a5a6;
        }
    """
}

# Стиль для заголовков
TITLE_STYLE = """
    QLabel {
        color: #2c3e50;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #ecf0f1, stop:1 #bdc3c7);
        padding: 20px;
        border-radius: 10px;
        font-size: 18px;
        font-weight: bold;
    }
"""

# Стиль для информационных панелей
INFO_PANEL_STYLE = """
    QFrame {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #ffffff, stop:1 #f8f9fa);
        border: 2px solid #bdc3c7;
        border-radius: 12px;
        padding: 20px;
    }
"""

# Стиль для подсказок
TOOLTIP_STYLE = """
    QToolTip {
        background-color: #2c3e50;
        color: white;
        border: 2px solid #34495e;
        border-radius: 6px;
        padding: 8px;
        font-size: 11px;
    }
"""


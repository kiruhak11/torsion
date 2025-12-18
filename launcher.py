"""
🚀 ПРОФЕССИОНАЛЬНЫЙ ЛАУНЧЕР
Лабораторная работа №4: Определение модуля сдвига при кручении

Авторы: Коваленко К., Иокерс А.
Группа: ИН-31
"""

import sys
import subprocess
import webbrowser
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QFrame, 
                            QGraphicsDropShadowEffect, QDesktopWidget)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QPainter, QBrush


class FlaskServerThread(QThread):
    """Поток для запуска Flask сервера."""
    server_started = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.process = None
    
    def run(self):
        try:
            import os
            # Запуск Flask в фоновом режиме
            self.process = subprocess.Popen(
                [sys.executable, 'web_app.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            time.sleep(2)  # Даём время на запуск
            self.server_started.emit(True)
        except Exception as e:
            print(f"Ошибка запуска Flask: {e}")
            self.server_started.emit(False)
    
    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()


class GradientWidget(QWidget):
    """Виджет с градиентным фоном."""
    
    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(26, 188, 156))  # Бирюзовый
        gradient.setColorAt(0.5, QColor(52, 152, 219))  # Синий
        gradient.setColorAt(1.0, QColor(142, 68, 173))  # Фиолетовый
        painter.fillRect(self.rect(), QBrush(gradient))


class ModernButton(QPushButton):
    """Современная кнопка с эффектами."""
    
    def __init__(self, text, icon="", color="#3498db"):
        super().__init__(f"{icon}  {text}")
        self.color = color
        self.setup_style()
        self.setup_animation()
    
    def setup_style(self):
        self.setMinimumHeight(70)
        self.setFont(QFont('Arial', 14, QFont.Bold))
        self.setCursor(Qt.PointingHandCursor)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.color}, stop:1 {self.adjust_color(self.color, -20)});
                color: white;
                border: none;
                border-radius: 15px;
                padding: 20px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.adjust_color(self.color, 20)}, 
                    stop:1 {self.color});
            }}
            QPushButton:pressed {{
                background: {self.adjust_color(self.color, -30)};
            }}
        """)
        
        # Тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
    
    def setup_animation(self):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def adjust_color(self, color_str, adjustment):
        """Изменение яркости цвета."""
        color = QColor(color_str)
        h, s, l, a = color.getHsl()
        l = max(0, min(255, l + adjustment))
        color.setHsl(h, s, l, a)
        return color.name()
    
    def enterEvent(self, event):
        """Анимация при наведении."""
        geom = self.geometry()
        self.animation.setStartValue(geom)
        self.animation.setEndValue(geom.adjusted(-3, -3, 3, 3))
        self.animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Анимация при уходе курсора."""
        geom = self.geometry()
        adjusted = geom.adjusted(-3, -3, 3, 3)
        self.animation.setStartValue(adjusted)
        self.animation.setEndValue(geom)
        self.animation.start()
        super().leaveEvent(event)


class LauncherWindow(QMainWindow):
    """Главное окно лаунчера."""
    
    def __init__(self):
        super().__init__()
        self.flask_thread = None
        self.init_ui()
        self.center()
        
    def init_ui(self):
        """Инициализация интерфейса."""
        self.setWindowTitle('🚀 Лаунчер: Лабораторная работа по кручению')
        self.setFixedSize(800, 700)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Центральный виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Главный layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_widget.setLayout(main_layout)
        
        # Фон с градиентом
        background = GradientWidget()
        background_layout = QVBoxLayout()
        background.setLayout(background_layout)
        main_layout.addWidget(background)
        
        # Верхняя панель (закрытие)
        top_bar = QWidget()
        top_bar.setFixedHeight(40)
        top_bar.setStyleSheet("background: rgba(0, 0, 0, 0.3);")
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(10, 0, 10, 0)
        top_bar.setLayout(top_layout)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: none;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(231, 76, 60, 0.8);
                border-radius: 15px;
            }
        """)
        close_btn.clicked.connect(self.close_app)
        
        top_layout.addStretch()
        top_layout.addWidget(close_btn)
        
        background_layout.addWidget(top_bar)
        background_layout.addStretch()
        
        # Контент
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(50, 30, 50, 50)
        content_layout.setSpacing(30)
        content.setLayout(content_layout)
        
        # Заголовок
        title = QLabel("🔧 ЛАБОРАТОРНАЯ РАБОТА №4")
        title.setFont(QFont('Arial', 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: white; background: transparent;")
        content_layout.addWidget(title)
        
        subtitle = QLabel("Определение модуля сдвига при кручении")
        subtitle.setFont(QFont('Arial', 16))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9); background: transparent;")
        content_layout.addWidget(subtitle)
        
        content_layout.addSpacing(20)
        
        # Информационная панель
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        info_layout = QVBoxLayout()
        info_frame.setLayout(info_layout)
        
        info_items = [
            ("👨‍💻 Авторы:", "Коваленко Кирилл, Иокерс Артем"),
            ("🎓 Группа:", "ИН-31"),
            ("📅 Дата:", "15 декабря 2025 года"),
            ("🏛️ Университет:", "РУДН")
        ]
        
        for label, value in info_items:
            item_layout = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFont(QFont('Arial', 11, QFont.Bold))
            lbl.setStyleSheet("color: white; background: transparent;")
            
            val = QLabel(value)
            val.setFont(QFont('Arial', 11))
            val.setStyleSheet("color: rgba(255, 255, 255, 0.95); background: transparent;")
            
            item_layout.addWidget(lbl)
            item_layout.addWidget(val)
            item_layout.addStretch()
            
            info_layout.addLayout(item_layout)
        
        content_layout.addWidget(info_frame)
        content_layout.addSpacing(20)
        
        # Разделитель
        separator = QLabel("Выберите версию для запуска:")
        separator.setFont(QFont('Arial', 14, QFont.Bold))
        separator.setAlignment(Qt.AlignCenter)
        separator.setStyleSheet("color: white; background: transparent;")
        content_layout.addWidget(separator)
        
        content_layout.addSpacing(10)
        
        # Кнопки запуска
        self.desktop_btn = ModernButton("Десктоп-приложение", "🖥️", "#2ecc71")
        self.desktop_btn.clicked.connect(self.launch_desktop)
        content_layout.addWidget(self.desktop_btn)
        
        self.web_btn = ModernButton("Веб-приложение", "🌐", "#3498db")
        self.web_btn.clicked.connect(self.launch_web)
        content_layout.addWidget(self.web_btn)
        
        self.docs_btn = ModernButton("Документация", "📚", "#9b59b6")
        self.docs_btn.clicked.connect(self.open_docs)
        content_layout.addWidget(self.docs_btn)
        
        content_layout.addStretch()
        
        # Статус
        self.status_label = QLabel("Готов к запуску")
        self.status_label.setFont(QFont('Arial', 10))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); background: transparent;")
        content_layout.addWidget(self.status_label)
        
        background_layout.addWidget(content)
        background_layout.addStretch()
        
        # Анимация появления
        self.setWindowOpacity(0)
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(800)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        QTimer.singleShot(100, self.fade_animation.start)
    
    def center(self):
        """Центрирование окна."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def launch_desktop(self):
        """Запуск десктоп-версии."""
        self.status_label.setText("🚀 Запуск десктоп-приложения...")
        self.desktop_btn.setEnabled(False)
        
        try:
            subprocess.Popen([sys.executable, 'main.py'])
            QTimer.singleShot(1000, self.close)
        except Exception as e:
            self.status_label.setText(f"❌ Ошибка: {str(e)}")
            self.desktop_btn.setEnabled(True)
    
    def launch_web(self):
        """Запуск веб-версии."""
        self.status_label.setText("🌐 Запуск веб-сервера...")
        self.web_btn.setEnabled(False)
        
        # Запуск Flask в отдельном потоке
        self.flask_thread = FlaskServerThread()
        self.flask_thread.server_started.connect(self.on_server_started)
        self.flask_thread.start()
    
    def on_server_started(self, success):
        """Обработка запуска сервера."""
        if success:
            self.status_label.setText("✅ Сервер запущен! Открытие браузера...")
            QTimer.singleShot(500, lambda: webbrowser.open('http://localhost:5001'))
            QTimer.singleShot(1500, self.close)
        else:
            self.status_label.setText("❌ Ошибка запуска сервера")
            self.web_btn.setEnabled(True)
    
    def open_docs(self):
        """Открытие документации."""
        self.status_label.setText("📚 Открытие документации...")
        try:
            import os
            readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
            if sys.platform == 'darwin':  # macOS
                subprocess.Popen(['open', readme_path])
            elif sys.platform == 'win32':  # Windows
                os.startfile(readme_path)
            else:  # Linux
                subprocess.Popen(['xdg-open', readme_path])
            
            QTimer.singleShot(500, lambda: self.status_label.setText("Готов к запуску"))
        except Exception as e:
            self.status_label.setText(f"❌ Ошибка: {str(e)}")
    
    def close_app(self):
        """Закрытие приложения."""
        if self.flask_thread:
            self.flask_thread.stop()
        self.close()
    
    def closeEvent(self, event):
        """Обработка закрытия окна."""
        if self.flask_thread:
            self.flask_thread.stop()
        event.accept()


def main():
    """Главная функция."""
    app = QApplication(sys.argv)
    
    # Настройка стиля
    app.setStyle('Fusion')
    
    # Тёмная палитра
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)
    
    # Создание и отображение окна
    launcher = LauncherWindow()
    launcher.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    print("="*70)
    print("  🚀 ПРОФЕССИОНАЛЬНЫЙ ЛАУНЧЕР")
    print("  Лабораторная работа №4: Кручение")
    print("="*70)
    print("  Авторы: Коваленко К., Иокерс А.")
    print("  Группа: ИН-31")
    print("="*70)
    print("\n✨ Загрузка интерфейса...\n")
    
    main()


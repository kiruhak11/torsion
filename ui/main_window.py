"""
Главное окно PyQt5 приложения для лабораторной работы по кручению.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTabWidget, QLabel, QLineEdit, QPushButton, QComboBox,
                            QGroupBox, QFormLayout, QTableWidget, QTableWidgetItem,
                            QMessageBox, QProgressBar, QTextEdit, QRadioButton,
                            QButtonGroup, QScrollArea, QFileDialog, QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QMovie
import numpy as np
import sys
import os
import matplotlib.pyplot as plt

from core.calculator import TorsionCalculator, determine_failure_type
from core.database import DatabaseManager
from core.animator import TorsionAnimator
from core.report_generator import ReportGenerator
from ui.diagrams import DiagramWidget
from ui.premium_styles import GLOBAL_STYLE, TOOLTIP_STYLE


class AnimationThread(QThread):
    """Поток для выполнения анимации."""
    finished = pyqtSignal(str)
    
    def __init__(self, animator, save_path):
        super().__init__()
        self.animator = animator
        self.save_path = save_path
    
    def run(self):
        try:
            self.animator.create_torsion_animation(save_path=self.save_path, fps=20, duration=8)
            self.finished.emit(f"Анимация сохранена: {self.save_path}")
        except Exception as e:
            self.finished.emit(f"Ошибка: {str(e)}")


class TorsionLabWindow(QMainWindow):
    """
    Главное окно приложения.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Лабораторная работа: Определение модуля сдвига при кручении')
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet(GLOBAL_STYLE + TOOLTIP_STYLE)
        self.animation_movie = None
        self.animation_preview_label = None
        self.animation_status_label = None
        
        # Инициализация БД
        self.db = DatabaseManager()
        
        # Переменные
        self.calculator = None
        self.results = None
        self.current_user = "Коваленко К., Иокерс А."
        self.current_group = "ИН-31"
        
        # Создание UI
        self.init_ui()
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса."""
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Заголовок
        title_label = QLabel('🔧 ЛАБОРАТОРНАЯ РАБОТА №4: КРУЧЕНИЕ 🔧')
        title_font = QFont('Arial', 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('color: #2c3e50; padding: 15px; background-color: #ecf0f1; border-radius: 8px;')
        main_layout.addWidget(title_label)
        
        # Табы
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 2px solid #bdc3c7; border-radius: 5px; }
            QTabBar::tab { background: #ecf0f1; padding: 10px 20px; margin: 2px; }
            QTabBar::tab:selected { background: #3498db; color: white; font-weight: bold; }
        """)
        
        # Вкладки
        self.tabs.addTab(self.create_experiment_tab(), "📊 Эксперимент")
        self.tabs.addTab(self.create_results_tab(), "📈 Результаты и графики")
        self.tabs.addTab(self.create_animation_tab(), "🎬 Анимация")
        self.tabs.addTab(self.create_database_tab(), "💾 База данных")
        self.tabs.addTab(self.create_test_tab(), "📝 Контрольный тест")
        
        main_layout.addWidget(self.tabs)
        
        # Статус-бар
        self.statusBar().showMessage('Готов к работе')
    
    def create_experiment_tab(self):
        """Создание вкладки эксперимента."""
        tab = QWidget()
        layout = QHBoxLayout()
        
        # Левая панель - ввод данных
        input_group = QGroupBox("⚙️ Параметры эксперимента")
        input_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; }")
        input_layout = QFormLayout()
        
        # ФИО и группа
        self.user_input = QLineEdit(self.current_user)
        self.group_input = QLineEdit(self.current_group)
        input_layout.addRow("ФИО:", self.user_input)
        input_layout.addRow("Группа:", self.group_input)
        
        # Материал
        self.material_combo = QComboBox()
        self.material_combo.addItems(['Сталь', 'Чугун', 'Дерево'])
        input_layout.addRow("Материал:", self.material_combo)
        
        # Геометрия
        self.diameter_input = QDoubleSpinBox()
        self.diameter_input.setRange(1.0, 100.0)
        self.diameter_input.setValue(10.0)
        self.diameter_input.setSuffix(" мм")
        self.diameter_input.setDecimals(2)
        input_layout.addRow("Диаметр D:", self.diameter_input)
        
        self.length_input = QDoubleSpinBox()
        self.length_input.setRange(10.0, 1000.0)
        self.length_input.setValue(200.0)
        self.length_input.setSuffix(" мм")
        self.length_input.setDecimals(1)
        input_layout.addRow("Длина L:", self.length_input)
        
        # Параметры нагружения
        self.max_moment_input = QDoubleSpinBox()
        self.max_moment_input.setRange(1.0, 10000.0)
        self.max_moment_input.setValue(100.0)
        self.max_moment_input.setSuffix(" Н·м")
        self.max_moment_input.setDecimals(2)
        input_layout.addRow("Макс. момент T:", self.max_moment_input)
        
        self.num_points_input = QSpinBox()
        self.num_points_input.setRange(5, 200)
        self.num_points_input.setValue(50)
        input_layout.addRow("Точек измерения:", self.num_points_input)
        
        input_group.setLayout(input_layout)
        
        # Кнопки управления
        buttons_layout = QVBoxLayout()
        
        self.calc_button = QPushButton("🔬 Выполнить расчет")
        self.calc_button.setStyleSheet("QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 12px; font-size: 13px; border-radius: 6px; } QPushButton:hover { background-color: #229954; }")
        self.calc_button.clicked.connect(self.perform_calculation)
        buttons_layout.addWidget(self.calc_button)
        
        self.animate_button = QPushButton("🎬 Создать анимацию")
        self.animate_button.setEnabled(False)
        self.animate_button.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; font-weight: bold; padding: 12px; font-size: 13px; border-radius: 6px; } QPushButton:hover { background-color: #c0392b; } QPushButton:disabled { background-color: #95a5a6; }")
        self.animate_button.clicked.connect(self.create_animation)
        buttons_layout.addWidget(self.animate_button)
        
        self.save_button = QPushButton("💾 Сохранить в БД")
        self.save_button.setEnabled(False)
        self.save_button.setStyleSheet("QPushButton { background-color: #3498db; color: white; font-weight: bold; padding: 12px; font-size: 13px; border-radius: 6px; } QPushButton:hover { background-color: #2980b9; } QPushButton:disabled { background-color: #95a5a6; }")
        self.save_button.clicked.connect(self.save_to_database)
        buttons_layout.addWidget(self.save_button)
        
        self.report_button = QPushButton("📄 Сгенерировать отчет")
        self.report_button.setEnabled(False)
        self.report_button.setStyleSheet("QPushButton { background-color: #9b59b6; color: white; font-weight: bold; padding: 12px; font-size: 13px; border-radius: 6px; } QPushButton:hover { background-color: #8e44ad; } QPushButton:disabled { background-color: #95a5a6; }")
        self.report_button.clicked.connect(self.generate_report)
        buttons_layout.addWidget(self.report_button)
        
        buttons_layout.addStretch()
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        buttons_layout.addWidget(self.progress_bar)
        
        left_layout = QVBoxLayout()
        left_layout.addWidget(input_group)
        left_layout.addLayout(buttons_layout)
        
        # Блок методических данных (по Cherkanov_mex_lab)
        method_box = QGroupBox("📘 Методические ориентиры")
        method_box.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12px; }")
        method_layout = QVBoxLayout()
        method_label = QLabel(
            "E = 2.01·10⁵ МПа, μ = 0.26\n"
            "Gтеор (сталь) = E / [2(1+μ)] ≈ 7.98·10⁴ МПа\n"
            "φ = T·ℓ/(G·Jp),   γ = φ·D/(2ℓ)"
        )
        method_label.setWordWrap(True)
        method_label.setStyleSheet("color: #34495e;")
        method_layout.addWidget(method_label)
        method_box.setLayout(method_layout)
        left_layout.addWidget(method_box)
        
        # Правая панель - вывод результатов
        output_group = QGroupBox("📋 Результаты расчета")
        output_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; }")
        output_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont('Courier', 10))
        self.results_text.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6;")
        output_layout.addWidget(self.results_text)
        
        output_group.setLayout(output_layout)
        
        # Компоновка
        layout.addLayout(left_layout, 1)
        layout.addWidget(output_group, 2)
        
        tab.setLayout(layout)
        return tab
    
    def create_results_tab(self):
        """Создание вкладки с графиками."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Кнопки выбора графика
        buttons_layout = QHBoxLayout()
        
        self.diagram_btn = QPushButton("📊 Диаграмма T-φ")
        self.diagram_btn.clicked.connect(lambda: self.show_diagram('torsion'))
        buttons_layout.addWidget(self.diagram_btn)
        
        self.stress_btn = QPushButton("📉 Распределение τ")
        self.stress_btn.clicked.connect(lambda: self.show_diagram('stress'))
        buttons_layout.addWidget(self.stress_btn)
        
        self.comparison_btn = QPushButton("📊 Сравнение G")
        self.comparison_btn.clicked.connect(lambda: self.show_diagram('comparison'))
        buttons_layout.addWidget(self.comparison_btn)
        
        self.save_plot_btn = QPushButton("💾 Сохранить график")
        self.save_plot_btn.clicked.connect(self.save_current_plot)
        buttons_layout.addWidget(self.save_plot_btn)
        
        layout.addLayout(buttons_layout)
        
        # Виджет с графиком
        self.diagram_widget = DiagramWidget()
        layout.addWidget(self.diagram_widget)
        
        tab.setLayout(layout)
        return tab

    def create_animation_tab(self):
        """Отдельная вкладка для анимации."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        title = QLabel("🎬 Превью анимации процесса кручения")
        title.setFont(QFont('Arial', 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.animation_status_label = QLabel("Анимация появится после первого расчета.")
        self.animation_status_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        layout.addWidget(self.animation_status_label)
        
        self.animation_preview_label = QLabel("Запустите расчет, затем нажмите «Сгенерировать превью».")
        self.animation_preview_label.setAlignment(Qt.AlignCenter)
        self.animation_preview_label.setMinimumHeight(320)
        self.animation_preview_label.setStyleSheet(
            "border: 2px dashed #bdc3c7; border-radius: 10px; "
            "background: #f8f9fa; color: #7f8c8d; padding: 12px;"
        )
        layout.addWidget(self.animation_preview_label)
        
        controls = QHBoxLayout()
        refresh_btn = QPushButton("🎥 Сгенерировать превью")
        refresh_btn.clicked.connect(self.start_animation_preview)
        refresh_btn.setStyleSheet(
            "QPushButton { background-color: #8e44ad; color: white; font-weight: bold; padding: 12px; "
            "border-radius: 8px; } QPushButton:hover { background-color: #7d3c98; }"
        )
        controls.addWidget(refresh_btn)
        controls.addStretch()
        layout.addLayout(controls)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_database_tab(self):
        """Создание вкладки базы данных."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("💾 История экспериментов")
        title.setFont(QFont('Arial', 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.load_experiments)
        btn_layout.addWidget(refresh_btn)
        
        load_btn = QPushButton("📂 Загрузить выбранный")
        load_btn.clicked.connect(self.load_selected_experiment)
        btn_layout.addWidget(load_btn)
        
        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.clicked.connect(self.delete_experiment)
        btn_layout.addWidget(delete_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Таблица
        self.experiments_table = QTableWidget()
        self.experiments_table.setColumnCount(6)
        self.experiments_table.setHorizontalHeaderLabels(['ID', 'Дата', 'Пользователь', 'Материал', 'D (мм)', 'L (мм)'])
        self.experiments_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.experiments_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.experiments_table)
        
        tab.setLayout(layout)
        
        # Загрузка данных
        self.load_experiments()
        
        return tab
    
    def create_test_tab(self):
        """Создание вкладки с тестом."""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("📝 Контрольный тест по кручению (8 вопросов)")
        title.setFont(QFont('Arial', 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('color: #2c3e50; padding: 10px; background-color: #ecf0f1; border-radius: 5px;')
        layout.addWidget(title)
        
        # Вопросы и ответы
        self.test_questions = self.get_test_questions()
        self.answer_groups = []
        
        for i, question_data in enumerate(self.test_questions, 1):
            question_group = QGroupBox(f"Вопрос {i}")
            question_layout = QVBoxLayout()
            
            question_label = QLabel(question_data['question'])
            question_label.setWordWrap(True)
            question_label.setStyleSheet('font-weight: bold; font-size: 11px; padding: 5px;')
            question_layout.addWidget(question_label)
            
            button_group = QButtonGroup(content)
            
            for j, answer in enumerate(question_data['answers']):
                radio = QRadioButton(answer)
                button_group.addButton(radio, j)
                question_layout.addWidget(radio)
            
            question_group.setLayout(question_layout)
            layout.addWidget(question_group)
            
            self.answer_groups.append((button_group, question_data['correct']))
        
        # Кнопка проверки
        check_btn = QPushButton("✅ Проверить ответы")
        check_btn.setStyleSheet("QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 15px; font-size: 14px; border-radius: 6px; } QPushButton:hover { background-color: #229954; }")
        check_btn.clicked.connect(self.check_test_answers)
        layout.addWidget(check_btn)
        
        layout.addStretch()
        content.setLayout(layout)
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        tab.setLayout(main_layout)
        
        return tab
    
    def get_test_questions(self):
        """Получение вопросов для теста."""
        return [
            {
                'question': '1. Как формулируется закон Гука при кручении?',
                'answers': [
                    'φ = T·ℓ/(G·Jp)',
                    'σ = E·ε',
                    'τ = G·γ',
                    'F = k·Δl'
                ],
                'correct': 0
            },
            {
                'question': '2. В какой точке сечения наблюдаются максимальные касательные напряжения при кручении?',
                'answers': [
                    'В центре сечения',
                    'На расстоянии R/2 от центра',
                    'На поверхности вала (максимальный радиус)',
                    'Равномерно по всему сечению'
                ],
                'correct': 2
            },
            {
                'question': '3. Как вычисляется полярный момент инерции круглого сечения?',
                'answers': [
                    'Jp = π·D³/32',
                    'Jp = π·D⁴/32',
                    'Jp = π·D²/4',
                    'Jp = π·D⁴/64'
                ],
                'correct': 1
            },
            {
                'question': '4. Что такое модуль сдвига G?',
                'answers': [
                    'Коэффициент пропорциональности при растяжении',
                    'Характеристика упругих свойств материала при сдвиге',
                    'Отношение нормального напряжения к деформации',
                    'Предел прочности при кручении'
                ],
                'correct': 1
            },
            {
                'question': '5. В каких единицах измеряется модуль сдвига?',
                'answers': [
                    'Н',
                    'мм',
                    'МПа (Па)',
                    'рад'
                ],
                'correct': 2
            },
            {
                'question': '6. Каков приблизительный модуль сдвига для стали?',
                'answers': [
                    '8·10⁴ МПа',
                    '2·10⁵ МПа',
                    '4·10⁴ МПа',
                    '1·10³ МПа'
                ],
                'correct': 0
            },
            {
                'question': '7. Как распределяются касательные напряжения по сечению круглого вала?',
                'answers': [
                    'Равномерно',
                    'По параболическому закону',
                    'По линейному закону (от 0 в центре до максимума на поверхности)',
                    'Максимум в центре, минимум на поверхности'
                ],
                'correct': 2
            },
            {
                'question': '8. Какой характер разрушения при кручении у стали?',
                'answers': [
                    'Расслоение вдоль волокон',
                    'Разрушение по плоскости, перпендикулярной оси',
                    'Разрушение по винтовой поверхности под углом 45° (срез)',
                    'Хрупкое разрушение без деформации'
                ],
                'correct': 2
            }
        ]
    
    def perform_calculation(self):
        """Выполнение расчета."""
        try:
            # Получение данных
            material = self.material_combo.currentText()
            diameter = self.diameter_input.value() / 1000  # м
            length = self.length_input.value() / 1000  # м
            T_max = self.max_moment_input.value()
            num_points = self.num_points_input.value()
            
            # Создание калькулятора
            self.calculator = TorsionCalculator(diameter, length, material)
            
            # Генерация РЕАЛИСТИЧНЫХ экспериментальных данных с погрешностью
            self.progress_bar.setValue(25)
            diagram_data = self.calculator.generate_diagram_data(
                T_max, 
                num_points,
                add_experimental_noise=True,  # ✅ Добавляем погрешность как в реальном эксперименте!
                error_percent=2.5  # 2.5% погрешность измерений
            )
            
            # Обработка ЭКСПЕРИМЕНТАЛЬНЫХ данных (с учетом погрешности)
            self.progress_bar.setValue(50)
            self.results = self.calculator.process_experiment_data(
                diagram_data['T'], 
                diagram_data['phi']
            )
            
            # Вывод результатов
            self.progress_bar.setValue(75)
            self.display_results()
            
            # Активация кнопок
            self.animate_button.setEnabled(True)
            self.save_button.setEnabled(True)
            self.report_button.setEnabled(True)
            
            self.progress_bar.setValue(100)
            self.statusBar().showMessage('Расчет выполнен успешно!', 3000)
            
            # Автоматическое отображение диаграммы
            self.show_diagram('torsion')
            self.start_animation_preview()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при расчете:\n{str(e)}")
            self.progress_bar.setValue(0)
    
    def display_results(self):
        """Отображение результатов расчета."""
        text = f"""
{'='*70}
  РЕЗУЛЬТАТЫ ЭКСПЕРИМЕНТАЛЬНОГО ОПРЕДЕЛЕНИЯ МОДУЛЯ СДВИГА
{'='*70}

ИСХОДНЫЕ ДАННЫЕ:
  • Материал образца:           {self.calculator.material}
  • Диаметр D:                   {self.calculator.D * 1000:.2f} мм
  • Длина L:                     {self.calculator.L * 1000:.2f} мм
  • Полярный момент инерции Jp:  {self.results['Jp']:.6e} м⁴
  • Полярный момент сопротивления Wp: {self.results['Wp']:.6e} м³
  • Методичка: E = 2.01·10⁵ МПа, μ = 0.26 → Gтеор = {2.01e5/(2*(1+0.26)):.0f} МПа

РЕЗУЛЬТАТЫ РАСЧЕТА:
  • Модуль сдвига (эксп.):       G = {self.results['G_experimental']:.2f} МПа
  • Модуль сдвига (эталон):      G = {self.results['G_reference']:.2f} МПа
  • Относительная погрешность:   δ = {self.results['relative_error']:.2f} %
  
МЕХАНИЧЕСКИЕ ХАРАКТЕРИСТИКИ:
  • Максимальный момент:         T_max = {self.results['T_max']:.2f} Н·м
  • Угол при T_max:              φ_max = {self.results['phi_max']:.5f} рад
                                        ({self.results['phi_max'] * 180/np.pi:.3f}°)
  • Макс. касательное напряжение: τ_max = {self.results['tau_max']:.2f} МПа
  • Макс. остаточный сдвиг:      γ_max = {self.results['gamma_max']:.5f} рад

ХАРАКТЕР РАЗРУШЕНИЯ:
  {determine_failure_type(self.calculator.material)}

{'='*70}
        """
        self.results_text.setText(text)
    
    def show_diagram(self, diagram_type):
        """Отображение графика."""
        if not self.calculator or not self.results:
            QMessageBox.warning(self, "Предупреждение", "Сначала выполните расчет!")
            return
        
        try:
            if diagram_type == 'torsion':
                self.diagram_widget.plot_torsion_diagram(
                    self.results['moments'], 
                    self.results['angles'],
                    meta={
                        'length_m': self.calculator.L,
                        'Jp': self.results['Jp'],
                        'G_ref': self.results['G_reference'],
                        'G_exp': self.results['G_experimental'],
                        'material': self.calculator.material
                    }
                )
            elif diagram_type == 'stress':
                self.diagram_widget.plot_stress_distribution(
                    self.calculator, 
                    self.results['T_max']
                )
            elif diagram_type == 'comparison':
                self.diagram_widget.plot_comparison(self.calculator, self.results)
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при построении графика:\n{str(e)}")
    
    def save_current_plot(self):
        """Сохранение текущего графика."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить график", "", "PNG файлы (*.png);;Все файлы (*)"
        )
        if filename:
            try:
                self.diagram_widget.save_plot(filename)
                QMessageBox.information(self, "Успех", f"График сохранен: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения:\n{str(e)}")
    
    def create_animation(self):
        """Создание анимации."""
        if not self.calculator or not self.results:
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить анимацию", "torsion_animation.gif", 
            "GIF файлы (*.gif);;Все файлы (*)"
        )
        
        if filename:
            try:
                animator = TorsionAnimator(
                    self.calculator,
                    self.results['moments'],
                    self.results['angles']
                )
                
                self.animate_button.setEnabled(False)
                self.statusBar().showMessage('Создание анимации... Пожалуйста, подождите.')
                
                # Запуск в отдельном потоке
                self.anim_thread = AnimationThread(animator, filename)
                self.anim_thread.finished.connect(self.animation_finished)
                self.anim_thread.start()
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка создания анимации:\n{str(e)}")
                self.animate_button.setEnabled(True)
    
    def start_animation_preview(self):
        """Фоновая генерация GIF-превью и отображение прямо во вкладке с графиками."""
        if not self.calculator or not self.results:
            QMessageBox.information(self, "Напоминание", "Сначала выполните расчет.")
            return
        if not self.animation_preview_label:
            QMessageBox.information(self, "Напоминание", "Откройте вкладку «Анимация».")
            return
        
        preview_path = os.path.join(os.getcwd(), "temp_animation_preview.gif")
        animator = TorsionAnimator(
            self.calculator,
            self.results['moments'],
            self.results['angles']
        )
        
        # Безопасно перезапускаем поток, если он еще крутится
        if hasattr(self, 'preview_thread') and self.preview_thread.isRunning():
            self.preview_thread.quit()
            self.preview_thread.wait()
        
        self.animation_status_label.setText("Генерация превью анимации (8 c, 20 fps)...")
        self.preview_thread = AnimationThread(animator, preview_path)
        self.preview_thread.finished.connect(lambda msg, path=preview_path: self.animation_preview_ready(path, msg))
        self.preview_thread.start()
    
    def animation_preview_ready(self, path: str, message: str):
        """Загрузка и запуск GIF-превью после генерации."""
        if os.path.exists(path):
            movie = QMovie(path)
            movie.setCacheMode(QMovie.CacheAll)
            self.animation_movie = movie  # сохраняем, чтобы не собрать GC
            self.animation_preview_label.setMovie(movie)
            movie.start()
            self.animation_status_label.setText("Превью готово ✅")
        else:
            self.animation_preview_label.setText("Не удалось сгенерировать превью")
            self.animation_status_label.setText(message)
        
        if message:
            self.statusBar().showMessage(message, 5000)
    
    def animation_finished(self, message):
        """Обработка завершения анимации."""
        self.animate_button.setEnabled(True)
        self.statusBar().showMessage(message, 5000)
        QMessageBox.information(self, "Готово", message)
    
    def save_to_database(self):
        """Сохранение результатов в БД."""
        if not self.calculator or not self.results:
            return
        
        try:
            user_name = self.user_input.text()
            group = self.group_input.text()
            
            # Сохранение пользователя
            self.db.save_user(user_name, group)
            
            # Сохранение эксперимента
            input_params = {
                'material': self.calculator.material,
                'diameter': self.calculator.D,
                'length': self.calculator.L,
                'max_moment': self.max_moment_input.value(),
                'num_points': self.num_points_input.value()
            }
            
            exp_id = self.db.save_experiment(
                user_name, 
                self.calculator.material,
                self.calculator.D,
                self.calculator.L,
                input_params,
                self.results
            )
            
            QMessageBox.information(self, "Успех", f"Эксперимент сохранен в БД (ID: {exp_id})")
            self.load_experiments()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения в БД:\n{str(e)}")
    
    def load_experiments(self):
        """Загрузка списка экспериментов."""
        try:
            experiments = self.db.get_all_experiments()
            
            self.experiments_table.setRowCount(len(experiments))
            
            for i, exp in enumerate(experiments):
                self.experiments_table.setItem(i, 0, QTableWidgetItem(str(exp['id'])))
                self.experiments_table.setItem(i, 1, QTableWidgetItem(exp['timestamp']))
                self.experiments_table.setItem(i, 2, QTableWidgetItem(exp['user_name']))
                self.experiments_table.setItem(i, 3, QTableWidgetItem(exp['material']))
                self.experiments_table.setItem(i, 4, QTableWidgetItem(f"{exp['diameter']*1000:.2f}"))
                self.experiments_table.setItem(i, 5, QTableWidgetItem(f"{exp['length']*1000:.2f}"))
            
            self.experiments_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных:\n{str(e)}")
    
    def load_selected_experiment(self):
        """Загрузка выбранного эксперимента."""
        selected_row = self.experiments_table.currentRow()
        
        if selected_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите эксперимент!")
            return
        
        try:
            exp_id = int(self.experiments_table.item(selected_row, 0).text())
            exp_data = self.db.get_experiment(exp_id)
            
            if exp_data:
                # Восстановление параметров
                self.user_input.setText(exp_data['user_name'])
                self.material_combo.setCurrentText(exp_data['material'])
                self.diameter_input.setValue(exp_data['diameter'] * 1000)
                self.length_input.setValue(exp_data['length'] * 1000)
                
                # Восстановление калькулятора и результатов
                self.calculator = TorsionCalculator(
                    exp_data['diameter'],
                    exp_data['length'],
                    exp_data['material']
                )
                self.results = exp_data['results']
                
                # Отображение результатов
                self.display_results()
                self.show_diagram('torsion')
                self.start_animation_preview()
                
                # Активация кнопок
                self.animate_button.setEnabled(True)
                self.report_button.setEnabled(True)
                
                QMessageBox.information(self, "Успех", "Эксперимент загружен!")
                self.tabs.setCurrentIndex(0)
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки эксперимента:\n{str(e)}")
    
    def delete_experiment(self):
        """Удаление эксперимента."""
        selected_row = self.experiments_table.currentRow()
        
        if selected_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите эксперимент!")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Удалить выбранный эксперимент?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                exp_id = int(self.experiments_table.item(selected_row, 0).text())
                self.db.delete_experiment(exp_id)
                self.load_experiments()
                QMessageBox.information(self, "Успех", "Эксперимент удален!")
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления:\n{str(e)}")
    
    def check_test_answers(self):
        """Проверка ответов теста."""
        score = 0
        answers = {}
        
        for i, (button_group, correct_idx) in enumerate(self.answer_groups):
            selected_btn = button_group.checkedButton()
            if selected_btn:
                selected_idx = button_group.id(selected_btn)
                answers[i] = selected_idx
                if selected_idx == correct_idx:
                    score += 1
            else:
                answers[i] = None
        
        # Сохранение результата
        try:
            user_name = self.user_input.text()
            self.db.save_test_result(user_name, score, answers)
        except:
            pass
        
        # Вывод результата
        percentage = (score / 8) * 100
        
        if percentage >= 75:
            grade = "Отлично! ✅"
            color = "green"
        elif percentage >= 60:
            grade = "Хорошо! 👍"
            color = "blue"
        elif percentage >= 50:
            grade = "Удовлетворительно 😐"
            color = "orange"
        else:
            grade = "Неудовлетворительно ❌"
            color = "red"
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Результат теста")
        msg.setText(f"<h2 style='color:{color};'>{grade}</h2>")
        msg.setInformativeText(f"<p style='font-size:14px;'>Правильных ответов: <b>{score} из 8</b><br>Процент: <b>{percentage:.1f}%</b></p>")
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
    
    def generate_report(self):
        """Генерация отчета."""
        if not self.calculator or not self.results:
            QMessageBox.warning(self, "Предупреждение", "Сначала выполните расчет!")
            return
        
        try:
            # Сохранение графиков
            diagram_path = "temp_diagram.png"
            stress_path = "temp_stress.png"
            
            # Сохранение диаграммы T-φ
            fig, ax = plt.subplots(figsize=(8, 6))
            angles_deg = np.array(self.results['angles']) * 180 / np.pi
            ax.plot(angles_deg, self.results['moments'], 'b-', linewidth=2)
            ax.scatter(angles_deg, self.results['moments'], c='red', s=30, alpha=0.6)
            ax.set_xlabel('Угол закручивания φ, град', fontsize=12)
            ax.set_ylabel('Крутящий момент T, Н·м', fontsize=12)
            ax.set_title('Диаграмма кручения T-φ', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(diagram_path, dpi=150)
            plt.close()
            
            # Сохранение распределения напряжений
            fig, ax = plt.subplots(figsize=(8, 6))
            rho, tau = self.calculator.calc_shear_stress_distribution(self.results['T_max'], 50)
            rho_mm = rho * 1000
            tau_mpa = tau / 1e6
            ax.plot(tau_mpa, rho_mm, 'r-', linewidth=2)
            ax.fill_betweenx(rho_mm, 0, tau_mpa, alpha=0.3, color='red')
            ax.set_xlabel('Касательное напряжение τ, МПа', fontsize=12)
            ax.set_ylabel('Радиус ρ, мм', fontsize=12)
            ax.set_title('Распределение τ по сечению', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(stress_path, dpi=150)
            plt.close()
            
            # Генерация отчета
            report_gen = ReportGenerator()
            filename = report_gen.generate_experiment_report(
                user_name=self.user_input.text(),
                group=self.group_input.text(),
                calculator=self.calculator,
                results=self.results,
                diagram_path=diagram_path,
                stress_path=stress_path
            )
            
            # Удаление временных файлов
            try:
                os.remove(diagram_path)
                os.remove(stress_path)
            except:
                pass
            
            QMessageBox.information(self, "Успех", f"Отчет создан:\n{filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка генерации отчета:\n{str(e)}")


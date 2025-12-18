"""
Виджеты для отображения графиков и диаграмм с использованием Matplotlib.
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout


class DiagramWidget(QWidget):
    """
    Виджет для отображения диаграмм и графиков.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def clear(self):
        """Очистка графика."""
        self.figure.clear()
        self.canvas.draw()
    
    def plot_torsion_diagram(self, moments, angles, meta: dict = None):
        """
        Построение диаграммы кручения T-φ с отображением экспериментальной и теоретической кривых.
        
        Args:
            moments: Массив крутящих моментов (Н·м) - ЭКСПЕРИМЕНТАЛЬНЫЕ данные
            angles: Массив углов закручивания (рад) - ЭКСПЕРИМЕНТАЛЬНЫЕ данные
            meta: Дополнительные данные (Jp, L, G_ref, G_exp, material)
        """
        meta = meta or {}
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor("#fbfcff")
        
        # Перевод углов в градусы для удобства
        angles_deg = np.array(angles) * 180 / np.pi
        
        # ЭКСПЕРИМЕНТАЛЬНАЯ кривая (с погрешностями!)
        ax.plot(angles_deg, moments, color='#2471a3', linewidth=2.4, 
               label='Экспериментальная кривая', alpha=0.85)
        ax.scatter(angles_deg, moments, c='#e74c3c', s=38, alpha=0.7, zorder=5,
                  label='Измерения')
        
        # Теоретическая прямая (линейная зависимость по эталонному G)
        if meta.get('Jp') and meta.get('length_m') and meta.get('G_ref'):
            phi_theory = np.linspace(0, angles_deg.max() * np.pi/180, 100)
            g_ref_pa = meta['G_ref'] * 1e6
            T_theory = (g_ref_pa * meta['Jp'] * phi_theory) / meta['length_m']
            phi_theory_deg = phi_theory * 180 / np.pi
            
            # Показываем только линейный участок теории (до 70% от T_max)
            T_max_theory = max(moments)
            theory_mask = T_theory <= T_max_theory
            
            ax.plot(phi_theory_deg[theory_mask], T_theory[theory_mask], 
                   '--', color='#16a085', linewidth=2.5, alpha=0.9,
                   label=f'Теория (Gэтал = {meta["G_ref"]:.0f} МПа)')
        
        ax.set_xlabel('Угол закручивания φ, град', fontsize=12, fontweight='bold')
        ax.set_ylabel('Крутящий момент T, Н·м', fontsize=12, fontweight='bold')
        ax.set_title('Диаграмма кручения T-φ\n(сравнение эксперимента и теории)', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.35, linestyle='--')
        
        # Выделение упругой области
        linear_idx = int(len(moments) * 0.7)
        if linear_idx > 1:
            ax.axvspan(0, angles_deg[linear_idx], alpha=0.08, color='green')
            ax.axvline(x=angles_deg[linear_idx], color='orange', 
                      linestyle=':', linewidth=2, alpha=0.6)
            ax.text(angles_deg[linear_idx]/2, max(moments)*0.92,
                    'Упругая\nобласть', fontsize=10, ha='center',
                    bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
            ax.text(angles_deg[linear_idx]*1.1, max(moments)*0.5,
                    'Упруго-\nпластическая\nобласть', fontsize=9, ha='left',
                    bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
        
        # Информационная панель
        if meta.get('G_exp') and meta.get('G_ref'):
            error = abs(meta['G_exp'] - meta['G_ref']) / meta['G_ref'] * 100
            info_text = (f"📊 РЕЗУЛЬТАТЫ:\n"
                        f"Gэксп = {meta['G_exp']:.1f} МПа\n"
                        f"Gэтал = {meta['G_ref']:.1f} МПа\n"
                        f"Погрешность δ = {error:.2f}%\n"
                        f"Материал: {meta.get('material', '-')}")
            ax.text(0.97, 0.03, info_text,
                   transform=ax.transAxes,
                   fontsize=9, fontweight='bold',
                   verticalalignment='bottom',
                   horizontalalignment='right',
                   bbox=dict(boxstyle='round', facecolor='#fef5e7', alpha=0.95, 
                            edgecolor='#f39c12', linewidth=2))
        
        ax.legend(fontsize=10, loc='upper left', frameon=True, shadow=True)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_stress_distribution(self, calculator, moment):
        """
        Построение графика распределения касательных напряжений по сечению.
        
        Args:
            calculator: Экземпляр TorsionCalculator
            moment: Значение крутящего момента (Н·м)
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor("#fcfcfc")
        
        # Получение данных
        rho, tau = calculator.calc_shear_stress_distribution(moment, 50)
        rho_mm = rho * 1000
        tau_mpa = tau / 1e6
        
        # Построение графика
        ax.plot(tau_mpa, rho_mm, 'r-', linewidth=2.5, label='τ(ρ)')
        ax.fill_betweenx(rho_mm, 0, tau_mpa, alpha=0.25, color='#f1948a')
        
        # Отметка максимального значения
        max_tau = np.max(tau_mpa)
        max_rho = calculator.D * 1000 / 2
        ax.plot([max_tau], [max_rho], 'ro', markersize=10, 
               label=f'τmax = {max_tau:.2f} МПа')
        
        ax.set_xlabel('Касательное напряжение τ, МПа', fontsize=12, fontweight='bold')
        ax.set_ylabel('Радиус ρ, мм', fontsize=12, fontweight='bold')
        ax.set_title(f'Распределение τ по сечению при T = {moment:.2f} Н·м', 
                    fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.35, linestyle='--')
        ax.axhline(y=max_rho, color='k', linestyle='--', linewidth=1, 
                  label=f'R = {max_rho:.2f} мм')
        ax.legend(fontsize=10)
        
        # Текстовая аннотация
        ax.text(max_tau * 0.5, max_rho * 0.5, 
               'Линейное\nраспределение', 
               fontsize=11, ha='center', 
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_comparison(self, calculator, results):
        """
        Построение сравнительной диаграммы экспериментального и эталонного модуля сдвига.
        
        Args:
            calculator: Экземпляр TorsionCalculator
            results: Словарь с результатами
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor("#fbfbfb")
        
        materials = [calculator.material]
        g_exp = [results['G_experimental']]
        g_ref = [results['G_reference']]
        
        x = np.arange(len(materials))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, g_exp, width, label='Экспериментальный', 
                      color='steelblue', alpha=0.8, edgecolor='black')
        bars2 = ax.bar(x + width/2, g_ref, width, label='Эталонный', 
                      color='coral', alpha=0.8, edgecolor='black')
        
        ax.set_ylabel('Модуль сдвига G, МПа', fontsize=12, fontweight='bold')
        ax.set_title('Сравнение модуля сдвига', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(materials, fontsize=11)
        ax.legend(fontsize=11)
        ax.grid(True, axis='y', alpha=0.3)
        
        # Аннотации значений
        for bar in bars1 + bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.0f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Погрешность
        error_text = f'Погрешность: {results["relative_error"]:.2f}%'
        ax.text(0.5, 0.95, error_text, transform=ax.transAxes,
               fontsize=12, ha='center', va='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def save_plot(self, filename: str, dpi: int = 150):
        """
        Сохранение текущего графика в файл.
        
        Args:
            filename: Имя файла
            dpi: Разрешение
        """
        self.figure.savefig(filename, dpi=dpi, bbox_inches='tight')


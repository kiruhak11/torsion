"""
Модуль для создания анимации процесса кручения образца.
Визуализирует закручивание вала и распределение касательных напряжений.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle, FancyBboxPatch, Wedge
from matplotlib.collections import LineCollection
import matplotlib.patches as mpatches


class TorsionAnimator:
    """
    Класс для создания анимации процесса кручения.
    """
    
    def __init__(self, calculator, T_data, phi_data):
        """
        Инициализация аниматора.
        
        Args:
            calculator: Экземпляр TorsionCalculator
            T_data: Массив значений крутящего момента
            phi_data: Массив соответствующих углов закручивания
        """
        self.calculator = calculator
        self.T_data = np.array(T_data)
        self.phi_data = np.array(phi_data)
        self.fig = None
        self.anim = None
    
    def create_torsion_animation(self, save_path: str = None, fps: int = 30, duration: int = 10):
        """
        Создает анимацию процесса кручения с визуализацией деформации и напряжений.
        
        Args:
            save_path: Путь для сохранения анимации (если None - показывает интерактивно)
            fps: Кадров в секунду
            duration: Длительность анимации в секундах
        
        Returns:
            FuncAnimation объект
        """
        # Создаем фигуру с несколькими подграфиками
        self.fig = plt.figure(figsize=(14, 8))
        gs = self.fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        # 1. 3D визуализация закручивания вала
        ax_3d = self.fig.add_subplot(gs[:, 0])
        ax_3d.set_xlim(-1.2, 1.2)
        ax_3d.set_ylim(0, self.calculator.L * 1000 + 50)  # мм
        ax_3d.set_aspect('equal')
        ax_3d.set_title('Закручивание образца', fontsize=12, fontweight='bold')
        ax_3d.set_xlabel('Смещение, мм')
        ax_3d.set_ylabel('Длина образца, мм')
        
        # 2. Диаграмма T-φ
        ax_diagram = self.fig.add_subplot(gs[0, 1])
        ax_diagram.plot(self.phi_data * 180/np.pi, self.T_data, 'b-', linewidth=2, alpha=0.3)
        ax_diagram.set_xlabel('Угол закручивания φ, град', fontsize=10)
        ax_diagram.set_ylabel('Крутящий момент T, Н·м', fontsize=10)
        ax_diagram.set_title('Диаграмма кручения T-φ', fontsize=11, fontweight='bold')
        ax_diagram.grid(True, alpha=0.3)
        line_current, = ax_diagram.plot([], [], 'ro-', linewidth=2, markersize=8)
        
        # 3. Распределение касательных напряжений
        ax_stress = self.fig.add_subplot(gs[0, 2])
        ax_stress.set_xlabel('τ, МПа', fontsize=10)
        ax_stress.set_ylabel('Радиус ρ, мм', fontsize=10)
        ax_stress.set_title('Распределение τ по сечению', fontsize=11, fontweight='bold')
        ax_stress.grid(True, alpha=0.3)
        
        # 4. Информационная панель
        ax_info = self.fig.add_subplot(gs[1, 1:])
        ax_info.axis('off')
        info_text = ax_info.text(0.05, 0.9, '', transform=ax_info.transAxes, 
                                fontsize=11, verticalalignment='top', 
                                family='monospace',
                                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Количество кадров
        num_frames = fps * duration
        frame_indices = np.linspace(0, len(self.T_data) - 1, num_frames).astype(int)
        
        # Создаем сетку вала для визуализации
        num_sections = 20
        y_sections = np.linspace(0, self.calculator.L * 1000, num_sections)
        
        def init():
            """Инициализация анимации."""
            line_current.set_data([], [])
            return line_current, info_text
        
        def animate(frame_num):
            """Функция анимации для каждого кадра."""
            idx = frame_indices[frame_num]
            T_current = self.T_data[idx]
            phi_current = self.phi_data[idx]
            
            # Обновление диаграммы T-φ
            line_current.set_data(self.phi_data[:idx+1] * 180/np.pi, self.T_data[:idx+1])
            
            # Очистка и перерисовка 3D вала
            ax_3d.clear()
            ax_3d.set_xlim(-1.5, 1.5)
            ax_3d.set_ylim(0, self.calculator.L * 1000 + 50)
            ax_3d.set_aspect('equal')
            ax_3d.set_title('Закручивание образца', fontsize=12, fontweight='bold')
            ax_3d.set_xlabel('Смещение, мм')
            ax_3d.set_ylabel('Длина образца, мм')
            
            # Рисуем закрученный вал (проекция)
            radius_mm = self.calculator.D * 1000 / 2
            for i, y in enumerate(y_sections):
                # Угол поворота пропорционален расстоянию от основания
                angle = phi_current * (y / (self.calculator.L * 1000))
                
                # Координаты точек на окружности
                x1 = radius_mm * np.cos(angle)
                x2 = -radius_mm * np.cos(angle)
                
                # Рисуем вертикальные линии (образующие)
                if i == 0:
                    ax_3d.plot([x1, x1], [y, y], 'b-', linewidth=2)
                    ax_3d.plot([x2, x2], [y, y], 'b-', linewidth=2)
                else:
                    y_prev = y_sections[i-1]
                    angle_prev = phi_current * (y_prev / (self.calculator.L * 1000))
                    x1_prev = radius_mm * np.cos(angle_prev)
                    x2_prev = -radius_mm * np.cos(angle_prev)
                    
                    ax_3d.plot([x1_prev, x1], [y_prev, y], 'b-', linewidth=1.5, alpha=0.7)
                    ax_3d.plot([x2_prev, x2], [y_prev, y], 'r-', linewidth=1.5, alpha=0.7)
                
                # Горизонтальные сечения
                if i % 4 == 0:
                    ax_3d.plot([x1, x2], [y, y], 'k-', linewidth=0.5, alpha=0.5)
            
            # Стрелка момента
            arrow_y = self.calculator.L * 1000 + 20
            ax_3d.annotate('', xy=(0.8, arrow_y), xytext=(-0.8, arrow_y),
                          arrowprops=dict(arrowstyle='<->', color='red', lw=2))
            ax_3d.text(0, arrow_y + 10, f'M = {T_current:.2f} Н·м', 
                      ha='center', fontsize=10, color='red', fontweight='bold')
            
            # Обновление распределения напряжений
            ax_stress.clear()
            rho, tau = self.calculator.calc_shear_stress_distribution(T_current, 50)
            tau_mpa = tau / 1e6
            rho_mm = rho * 1000
            
            ax_stress.plot(tau_mpa, rho_mm, 'r-', linewidth=2)
            ax_stress.fill_betweenx(rho_mm, 0, tau_mpa, alpha=0.3, color='red')
            ax_stress.set_xlabel('τ, МПа', fontsize=10)
            ax_stress.set_ylabel('Радиус ρ, мм', fontsize=10)
            ax_stress.set_title('Распределение τ по сечению', fontsize=11, fontweight='bold')
            ax_stress.grid(True, alpha=0.3)
            ax_stress.axhline(y=self.calculator.D * 1000 / 2, color='k', 
                             linestyle='--', linewidth=1, label='R наруж')
            ax_stress.legend(fontsize=8)
            
            # Обновление информационной панели
            tau_max = self.calculator.calc_max_shear_stress(T_current) / 1e6
            gamma = self.calculator.calc_relative_shear(phi_current)
            G = self.calculator.calc_shear_modulus(T_current, phi_current) / 1e6 if phi_current > 0 else 0
            
            info_str = f"""
╔═══════════════════════════════════════════════════════════╗
║  ПАРАМЕТРЫ ЭКСПЕРИМЕНТА (Кадр {frame_num+1}/{num_frames})
╠═══════════════════════════════════════════════════════════╣
║  Материал: {self.calculator.material:<15}  D = {self.calculator.D*1000:.1f} мм
║  Длина: L = {self.calculator.L*1000:.1f} мм
╠═══════════════════════════════════════════════════════════╣
║  ТЕКУЩИЕ ЗНАЧЕНИЯ:
║  • Крутящий момент:        T = {T_current:8.2f} Н·м
║  • Угол закручивания:      φ = {phi_current:8.5f} рад ({phi_current*180/np.pi:6.2f}°)
║  • Касательное напряжение: τ = {tau_max:8.2f} МПа
║  • Относительный сдвиг:    γ = {gamma:8.5f}
║  • Модуль сдвига:          G = {G:8.0f} МПа
╚═══════════════════════════════════════════════════════════╝
            """
            info_text.set_text(info_str)
            
            return line_current, info_text
        
        # Создаем анимацию
        self.anim = FuncAnimation(self.fig, animate, init_func=init,
                                 frames=num_frames, interval=1000/fps,
                                 blit=False, repeat=True)
        
        # Сохранение или показ
        if save_path:
            try:
                self.anim.save(save_path, writer='pillow', fps=fps)
                print(f"Анимация сохранена: {save_path}")
            except Exception as e:
                print(f"Ошибка сохранения анимации: {e}")
        
        return self.anim
    
    def create_stress_distribution_frames(self, num_frames: int = 10) -> list:
        """
        Создает набор статичных кадров распределения напряжений для отчета.
        
        Args:
            num_frames: Количество кадров
            
        Returns:
            Список путей к сохраненным изображениям
        """
        saved_paths = []
        frame_indices = np.linspace(0, len(self.T_data) - 1, num_frames).astype(int)
        
        for i, idx in enumerate(frame_indices):
            fig, ax = plt.subplots(figsize=(6, 5))
            
            T = self.T_data[idx]
            rho, tau = self.calculator.calc_shear_stress_distribution(T, 50)
            tau_mpa = tau / 1e6
            rho_mm = rho * 1000
            
            ax.plot(tau_mpa, rho_mm, 'r-', linewidth=2)
            ax.fill_betweenx(rho_mm, 0, tau_mpa, alpha=0.3, color='red')
            ax.set_xlabel('Касательное напряжение τ, МПа', fontsize=11)
            ax.set_ylabel('Радиус ρ, мм', fontsize=11)
            ax.set_title(f'Распределение τ при T = {T:.2f} Н·м', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.axhline(y=self.calculator.D * 1000 / 2, color='k', 
                      linestyle='--', linewidth=1, label=f'R = {self.calculator.D*1000/2:.2f} мм')
            ax.legend()
            
            path = f'stress_distribution_frame_{i+1}.png'
            plt.tight_layout()
            plt.savefig(path, dpi=150, bbox_inches='tight')
            plt.close()
            saved_paths.append(path)
        
        return saved_paths


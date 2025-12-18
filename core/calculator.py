"""
Модуль расчетных функций для лабораторной работы по кручению.
Реализует все формулы из методички для определения модуля сдвига G и механических характеристик.
"""

import numpy as np
from typing import Dict, List, Tuple
import math


class TorsionCalculator:
    """
    Класс для расчета параметров кручения валов круглого сечения.
    """
    
    def __init__(self, diameter: float, length: float, material: str):
        """
        Инициализация калькулятора.
        
        Args:
            diameter: Диаметр образца, м
            length: Длина образца (база измерения), м
            material: Тип материала ('Сталь', 'Чугун', 'Дерево')
        """
        self.D = diameter  # м
        self.L = length    # м
        self.material = material
        
        # Эталонные значения модуля сдвига G (Па)
        self.G_reference = {
            'Сталь': 8.1e10,   # 81000 МПа
            'Чугун': 4.0e10,   # 40000 МПа
            'Дерево': 0.5e9    # 500 МПа
        }
    
    def calc_polar_moment_inertia(self) -> float:
        """
        Расчет полярного момента инерции круглого сечения.
        Jp = π·D⁴/32
        
        Returns:
            Полярный момент инерции, м⁴
        """
        return (math.pi * self.D**4) / 32
    
    def calc_polar_section_modulus(self) -> float:
        """
        Расчет полярного момента сопротивления.
        Wp = π·D³/16
        
        Returns:
            Полярный момент сопротивления, м³
        """
        return (math.pi * self.D**3) / 16
    
    def calc_relative_shear(self, phi: float) -> float:
        """
        Расчет относительного сдвига на поверхности вала.
        γ = (φ·D)/(2ℓ)
        
        Args:
            phi: Угол закручивания, рад
            
        Returns:
            Относительный сдвиг, безразмерный
        """
        return (phi * self.D) / (2 * self.L)
    
    def calc_shear_modulus(self, T: float, phi: float) -> float:
        """
        Расчет модуля сдвига по закону Гука при кручении.
        G = (T·ℓ)/(φ·Jp)
        
        Args:
            T: Крутящий момент, Н·м
            phi: Угол закручивания, рад
            
        Returns:
            Модуль сдвига, Па (для перевода в МПа делить на 1e6)
        """
        Jp = self.calc_polar_moment_inertia()
        if phi == 0:
            return 0
        return (T * self.L) / (phi * Jp)
    
    def calc_max_shear_stress(self, T: float) -> float:
        """
        Расчет максимального касательного напряжения на поверхности.
        τmax = T·(D/2)/Jp = T/Wp
        
        Args:
            T: Крутящий момент, Н·м
            
        Returns:
            Максимальное касательное напряжение, Па
        """
        Wp = self.calc_polar_section_modulus()
        return T / Wp
    
    def calc_shear_stress_distribution(self, T: float, num_points: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """
        Расчет распределения касательных напряжений по радиусу сечения.
        τ(ρ) = T·ρ/Jp (линейное распределение)
        
        Args:
            T: Крутящий момент, Н·м
            num_points: Количество точек для построения графика
            
        Returns:
            Кортеж (массив радиусов ρ, массив напряжений τ)
        """
        Jp = self.calc_polar_moment_inertia()
        rho = np.linspace(0, self.D/2, num_points)
        tau = (T * rho) / Jp
        return rho, tau
    
    def calc_yield_strength(self, T_f: float) -> float:
        """
        Расчет предела текучести при кручении.
        τ₀.₃ = Tf/Wp
        
        Args:
            T_f: Крутящий момент при пределе текучести, Н·м
            
        Returns:
            Предел текучести, Па
        """
        Wp = self.calc_polar_section_modulus()
        return T_f / Wp
    
    def calc_ultimate_strength(self, T_k: float) -> float:
        """
        Расчет предела прочности при кручении.
        τB = Tk/Wp
        
        Args:
            T_k: Максимальный крутящий момент перед разрушением, Н·м
            
        Returns:
            Предел прочности, Па
        """
        Wp = self.calc_polar_section_modulus()
        return T_k / Wp
    
    def calc_max_residual_shear(self, phi_max: float) -> float:
        """
        Расчет максимального остаточного сдвига при кручении.
        γmax = φmax·D/(2ℓ) если γ < 0.1 рад
        γmax = arctg(φmax·D/(2ℓ)) если γ >= 0.1 рад
        
        Args:
            phi_max: Угол закручивания в момент разрушения, рад
            
        Returns:
            Максимальный остаточный сдвиг, рад
        """
        gamma_temp = (phi_max * self.D) / (2 * self.L)
        
        if gamma_temp < 0.1:
            return gamma_temp
        else:
            return math.atan(gamma_temp)
    
    def load_custom_experiment_data(self, moments: List[float], angles: List[float]) -> bool:
        """
        Загрузка пользовательских экспериментальных данных T-φ.
        Используется для ввода РЕАЛЬНЫХ данных из лабораторного эксперимента.
        
        Args:
            moments: Список значений крутящего момента, Н·м (введенные пользователем)
            angles: Список соответствующих углов закручивания, рад (введенные пользователем)
            
        Returns:
            True если данные валидны, False иначе
        """
        if len(moments) != len(angles):
            return False
        if len(moments) < 3:
            return False
        if any(m < 0 for m in moments) or any(a < 0 for a in angles):
            return False
        
        return True
    
    def process_experiment_data(self, moments: List[float], angles: List[float]) -> Dict:
        """
        Обработка экспериментальных данных T-φ.
        Строит диаграмму, определяет модуль сдвига G на линейном участке.
        
        Args:
            moments: Список значений крутящего момента, Н·м
            angles: Список соответствующих углов закручивания, рад
            
        Returns:
            Словарь с результатами расчетов
        """
        moments = np.array(moments)
        angles = np.array(angles)
        
        # Находим линейный участок (первые 70% данных)
        linear_idx = int(len(moments) * 0.7)
        T_linear = moments[:linear_idx]
        phi_linear = angles[:linear_idx]
        
        # МНК для определения наклона (модуль жесткости)
        if len(phi_linear) > 1 and phi_linear[-1] != 0:
            k = np.polyfit(phi_linear, T_linear, 1)[0]  # T = k·φ
            
            # Модуль сдвига: G = k·ℓ/Jp
            Jp = self.calc_polar_moment_inertia()
            G_exp = (k * self.L) / Jp
        else:
            G_exp = 0
        
        # Максимальные значения
        T_max = np.max(moments)
        phi_max = angles[np.argmax(moments)]
        
        # Механические характеристики
        tau_max = self.calc_max_shear_stress(T_max)
        gamma_max = self.calc_max_residual_shear(phi_max)
        
        # Погрешность
        G_ref = self.G_reference.get(self.material, G_exp)
        relative_error = abs(G_exp - G_ref) / G_ref * 100 if G_ref != 0 else 0
        
        return {
            'Jp': self.calc_polar_moment_inertia(),
            'Wp': self.calc_polar_section_modulus(),
            'G_experimental': G_exp / 1e6,  # МПа
            'G_reference': G_ref / 1e6,  # МПа
            'relative_error': relative_error,
            'T_max': T_max,
            'phi_max': phi_max,
            'tau_max': tau_max / 1e6,  # МПа
            'gamma_max': gamma_max,
            'moments': moments.tolist(),
            'angles': angles.tolist(),
            'linear_slope': k if 'k' in locals() else 0
        }
    
    def generate_diagram_data(self, T_max: float, num_points: int = 100, 
                             add_experimental_noise: bool = True, error_percent: float = 2.0) -> Dict:
        """
        Генерация данных для построения диаграммы T-φ с учетом упругой и пластической стадий.
        ВАЖНО: Добавляет реалистичную погрешность для имитации реальных экспериментальных данных!
        
        Args:
            T_max: Максимальный момент, Н·м
            num_points: Количество точек
            add_experimental_noise: Добавлять ли экспериментальную погрешность
            error_percent: Процент погрешности (по умолчанию 2%)
            
        Returns:
            Словарь с массивами для построения графика
        """
        G_ref = self.G_reference.get(self.material, 8.1e10)  # Па (эталонное значение)
        Jp = self.calc_polar_moment_inertia()
        
        # Имитация реального экспериментального модуля сдвига с погрешностью
        if add_experimental_noise:
            # Случайное отклонение модуля сдвига (±error_percent%)
            G_experimental = G_ref * (1.0 + np.random.uniform(-error_percent/100, error_percent/100))
        else:
            G_experimental = G_ref
        
        # Упругая стадия (70% от T_max)
        T_elastic = T_max * 0.7
        phi_elastic = (T_elastic * self.L) / (G_experimental * Jp)
        
        # Упругий участок (используем ЭКСПЕРИМЕНТАЛЬНЫЙ G для реалистичности!)
        T_elastic_curve = np.linspace(0, T_elastic, int(num_points * 0.7))
        phi_elastic_curve = (T_elastic_curve * self.L) / (G_experimental * Jp)
        
        # Добавляем небольшой шум в упругую область
        if add_experimental_noise:
            noise_elastic = np.random.normal(0, phi_elastic * 0.01, len(phi_elastic_curve))
            phi_elastic_curve = phi_elastic_curve + noise_elastic
            phi_elastic_curve = np.maximum(phi_elastic_curve, 0)  # Убираем отрицательные значения
        
        # Упруго-пластический участок (70% - 100%)
        T_plastic_curve = np.linspace(T_elastic, T_max, int(num_points * 0.3))
        # Нелинейная зависимость (степенная функция)
        phi_plastic_curve = phi_elastic + (phi_elastic * 2) * ((T_plastic_curve - T_elastic) / (T_max - T_elastic))**2
        
        # Добавляем больший шум в пластическую область
        if add_experimental_noise:
            noise_plastic = np.random.normal(0, phi_elastic * 0.03, len(phi_plastic_curve))
            phi_plastic_curve = phi_plastic_curve + noise_plastic
        
        T_full = np.concatenate([T_elastic_curve, T_plastic_curve])
        phi_full = np.concatenate([phi_elastic_curve, phi_plastic_curve])
        
        return {
            'T': T_full,
            'phi': phi_full,
            'T_elastic': T_elastic,
            'phi_elastic': phi_elastic,
            'phi_max': phi_full[-1],
            'G_experimental_used': G_experimental  # Для отладки
        }


def calculate_safety_factor(tau_working: float, tau_ultimate: float) -> float:
    """
    Расчет коэффициента запаса прочности.
    n = τ_предельное / τ_рабочее
    
    Args:
        tau_working: Рабочее напряжение, Па
        tau_ultimate: Предельное напряжение, Па
        
    Returns:
        Коэффициент запаса
    """
    if tau_working == 0:
        return float('inf')
    return tau_ultimate / tau_working


def determine_failure_type(material: str) -> str:
    """
    Определение характера разрушения материала при кручении.
    
    Args:
        material: Тип материала
        
    Returns:
        Описание характера разрушения
    """
    failure_types = {
        'Сталь': 'Разрушение по винтовой поверхности под углом 45° (срез)',
        'Чугун': 'Разрушение по плоскости, перпендикулярной оси (отрыв)',
        'Дерево': 'Расслоение вдоль волокон'
    }
    return failure_types.get(material, 'Неизвестный тип разрушения')


import math

def polar_moment_inertia(diameter):
    """Полярный момент инерции круглого сечения (мм⁴)"""
    return (math.pi * (diameter ** 4)) / 32

def polar_resistance_moment(diameter):
    """Полярный момент сопротивления Wp (мм³)"""
    return (math.pi * (diameter ** 3)) / 16

def calculate_basic_G(moment, L, diameter, angle_deg):
    """Расчёт модуля сдвига (G) при кручении, угол в °"""
    try:
        theta = math.radians(angle_deg)
        J = polar_moment_inertia(diameter)
        G = (moment * L) / (J * theta)
        return round(G, 2)
    except ZeroDivisionError:
        return None

def calculate_tau(moment, diameter):
    """Расчёт касательных напряжений τ = M / Wp"""
    try:
        Wp = polar_resistance_moment(diameter)
        return round(moment / Wp, 2)
    except ZeroDivisionError:
        return None

def analyze_experiment(data, L, diameter):
    """
    Принимает список точек: [(T1, φ1), (T2, φ2), ...]
    Определяет:
      - Модуль G на линейном участке
      - Предел пропорциональности
      - Предел текучести (по 0.3% сдвигу)
      - Предел прочности
      - Максимальный сдвиг
    """
    J = polar_moment_inertia(diameter)
    Wp = polar_resistance_moment(diameter)
    analysis = {
        "G_linear": None,
        "τ_pcz": None,
        "τ_0_3": None,
        "τ_max": None,
        "γ_max": None
    }

    # Рассчёт G по линейной части (первая треть точек)
    linear_region = data[:max(3, len(data)//3)]
    G_values = []
    for T, phi in linear_region:
        if phi > 0:
            G = (T * L) / (J * phi)
            G_values.append(G)
    analysis["G_linear"] = round(sum(G_values) / len(G_values), 2) if G_values else None

    # Предел прочности
    max_T, max_

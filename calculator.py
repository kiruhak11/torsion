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
        return round(G, 2) if not math.isnan(G) else None
    except (ZeroDivisionError, ValueError):
        return None

def calculate_tau(moment, diameter):
    """Расчёт касательных напряжений τ = M / Wp"""
    try:
        Wp = polar_resistance_moment(diameter)
        return round(moment / Wp, 2) if Wp != 0 else None
    except (ZeroDivisionError, TypeError):
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
    if not data or L <= 0 or diameter <= 0:
        return {
            "G_linear": None,
            "τ_pcz": None,
            "τ_0_3": None,
            "τ_max": None,
            "γ_max": None
        }

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
    linear_region = data[:max(3, len(data)//3)] if data else []
    G_values = []
    tau_values = []
    
    for T, phi in linear_region:
        if phi > 0 and J != 0:
            try:
                G = (T * L) / (J * math.radians(phi))
                G_values.append(G)
                tau_values.append(calculate_tau(T, diameter))
            except (ZeroDivisionError, TypeError):
                continue

    if G_values:
        analysis["G_linear"] = round(sum(G_values)/len(G_values), 2)
        analysis["τ_pcz"] = max(tau_values) if tau_values else None

    # Поиск предела текучести (0.3% остаточной деформации)
    if analysis["G_linear"] and analysis["G_linear"] > 0:
        try:
            theta_yield = 0.003 * L / (diameter/2)  # γ = 0.3% = 0.003
            T_yield = (analysis["G_linear"] * J * theta_yield) / L
            analysis["τ_0_3"] = calculate_tau(T_yield, diameter)
        except ZeroDivisionError:
            analysis["τ_0_3"] = None

    # Предел прочности и максимальный сдвиг
    if data:
        T_max = max([T for T, phi in data])
        analysis["τ_max"] = calculate_tau(T_max, diameter)
        
        if analysis["G_linear"] and analysis["τ_max"]:
            analysis["γ_max"] = round(analysis["τ_max"] / analysis["G_linear"], 5)

    return analysis
# graph.py

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import math
from calculator import calculate_basic_G, calculate_tau

def plot_torsion_curve(L, diameter, moment, elastic_limit, failure_angle, k, display_angle, container):
    """
    Строит график зависимости эффективного модуля G от угла поворота
    """
    # Создание массива углов от 0 до display_angle
    angles = np.linspace(0.1, display_angle, 100)
    G_values = []
    
    for angle in angles:
        if angle <= elastic_limit:
            # В эластичной области
            G_baseline = calculate_basic_G(moment, L, diameter, angle)
            G_eff = k * G_baseline if G_baseline else 0
        elif angle <= failure_angle:
            # В пластической области - линейное снижение
            G0 = calculate_basic_G(moment, L, diameter, elastic_limit)
            if G0:
                G_baseline = G0 * ((failure_angle - angle) / (failure_angle - elastic_limit))
                G_eff = k * max(0, G_baseline)
            else:
                G_eff = 0
        else:
            G_eff = 0
        
        G_values.append(G_eff)
    
    # Очистка контейнера
    for widget in container.winfo_children():
        widget.destroy()
    
    # Создание графика
    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    ax.plot(angles, G_values, linewidth=2, color='darkblue', label='G_eff(θ)')
    ax.axvline(x=elastic_limit, color='orange', linestyle='--', alpha=0.7, label=f'Предел эластичности ({elastic_limit}°)')
    ax.axvline(x=failure_angle, color='red', linestyle='--', alpha=0.7, label=f'Угол разрушения ({failure_angle}°)')
    
    if display_angle <= failure_angle:
        current_G = G_values[np.argmin(np.abs(angles - display_angle))]
        ax.plot(display_angle, current_G, 'ro', markersize=8, label=f'Текущая точка ({display_angle:.1f}°, {current_G:.1f} МПа)')
    
    ax.set_xlabel('Угол поворота θ (градусы)')
    ax.set_ylabel('Эффективный модуль G_eff (МПа)')
    ax.set_title('Зависимость эффективного модуля упругости от угла поворота')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Интеграция в Tkinter
    canvas = FigureCanvasTkAgg(fig, master=container)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    
    return canvas

def save_torsion_curve(L, diameter, moment, elastic_limit, failure_angle, k, display_angle, filename):
    """
    Сохраняет график зависимости эффективного модуля G от угла поворота в файл
    """
    # Создание массива углов от 0 до display_angle
    angles = np.linspace(0.1, display_angle, 100)
    G_values = []
    
    for angle in angles:
        if angle <= elastic_limit:
            # В эластичной области
            G_baseline = calculate_basic_G(moment, L, diameter, angle)
            G_eff = k * G_baseline if G_baseline else 0
        elif angle <= failure_angle:
            # В пластической области - линейное снижение
            G0 = calculate_basic_G(moment, L, diameter, elastic_limit)
            if G0:
                G_baseline = G0 * ((failure_angle - angle) / (failure_angle - elastic_limit))
                G_eff = k * max(0, G_baseline)
            else:
                G_eff = 0
        else:
            G_eff = 0
        
        G_values.append(G_eff)
    
    # Создание графика
    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    ax.plot(angles, G_values, linewidth=2, color='darkblue', label='G_eff(θ)')
    ax.axvline(x=elastic_limit, color='orange', linestyle='--', alpha=0.7, label=f'Предел эластичности ({elastic_limit}°)')
    ax.axvline(x=failure_angle, color='red', linestyle='--', alpha=0.7, label=f'Угол разрушения ({failure_angle}°)')
    
    if display_angle <= failure_angle:
        current_G = G_values[np.argmin(np.abs(angles - display_angle))]
        ax.plot(display_angle, current_G, 'ro', markersize=8, label=f'Текущая точка ({display_angle:.1f}°, {current_G:.1f} МПа)')
    
    ax.set_xlabel('Угол поворота θ (градусы)')
    ax.set_ylabel('Эффективный модуль G_eff (МПа)')
    ax.set_title('Зависимость эффективного модуля упругости от угла поворота')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Сохранение графика
    fig.savefig(filename, bbox_inches='tight', dpi=300)
    plt.close(fig)

def plot_experiment_graph(data, L, diameter, container):
    """
    Строит график Момент (T, Н·мм) от Угла поворота (φ, рад)
    и график Касательных напряжений τ(φ)
    """
    angles = [x[1] for x in data]
    moments = [x[0] for x in data]
    taus = [calculate_tau(M, diameter) for M in moments]

    fig, axs = plt.subplots(1, 2, figsize=(10, 4), dpi=100)

    # График Момента
    axs[0].plot(angles, moments, marker='o', linestyle='-', color='teal')
    axs[0].set_title("График: Момент T vs Угол φ")
    axs[0].set_xlabel("Угол (рад)")
    axs[0].set_ylabel("Крутящий момент T (Н·мм)")
    axs[0].grid(True)

    # График Касательных напряжений
    axs[1].plot(angles, taus, marker='s', linestyle='-', color='darkred')
    axs[1].set_title("График: τ vs Угол φ")
    axs[1].set_xlabel("Угол (рад)")
    axs[1].set_ylabel("Касательное напряжение τ (МПа)")
    axs[1].grid(True)

    # Настройка макета
    fig.tight_layout()

    # Обновление контейнера с графиком в Tkinter
    for widget in container.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=container)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    return canvas

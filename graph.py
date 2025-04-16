# graph.py

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from calculator import calculate_tau

def plot_torsion_curve(data, L, diameter):
    """
    Строит график зависимости Момента от Угла
    для кривой кручения
    """
    # Извлечение данных
    angles = [x[1] for x in data]
    moments = [x[0] for x in data]
    
    # Построение графика
    plt.figure(figsize=(8, 4))
    plt.plot(angles, moments, marker='o', linestyle='-', color='teal')
    plt.title("Кривая кручения: Момент T vs Угол φ")
    plt.xlabel("Угол (рад)")
    plt.ylabel("Момент T (Н·мм)")
    plt.grid(True)
    plt.show()

def save_torsion_curve(data, L, diameter, filename):
    """
    Сохраняет график зависимости Момента от Угла в файл
    """
    angles = [x[1] for x in data]
    moments = [x[0] for x in data]
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(angles, moments, marker='o', linestyle='-', color='teal')
    ax.set_title("Кривая кручения: Момент T vs Угол φ")
    ax.set_xlabel("Угол (рад)")
    ax.set_ylabel("Момент T (Н·мм)")
    ax.grid(True)

    # Сохранение графика
    fig.savefig(filename)

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

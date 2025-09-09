import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import math

from calculator import calculate_basic_G, analyze_experiment  # и другие необходимые функции из calculator
from graph import plot_torsion_curve, save_torsion_curve, plot_experiment_graph
from report_docx import generate_docx
from db_manager import init_db, insert_result, get_results

material_properties = {
    "Сталь": {"k": 1.0, "elastic_limit": 15, "failure_angle": 30},
    "Чугун": {"k": 0.95, "elastic_limit": 10, "failure_angle": 20},
    "Дерево": {"k": 0.80, "elastic_limit": 8, "failure_angle": 16}
}

class TorsionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №4: Определение прочности при кручении")
        self.root.geometry("1000x900")
        self.root.resizable(False, False)
        self.create_widgets()
        init_db()
        self.last_result = None

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_main = ttk.Frame(self.notebook)
        self.tab_anim = ttk.Frame(self.notebook)
        self.tab_db = ttk.Frame(self.notebook)
        self.tab_report = ttk.Frame(self.notebook)
        self.tab_experiment = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_main, text="Главная")
        self.notebook.add(self.tab_anim, text="Анимация")
        self.notebook.add(self.tab_db, text="База данных")
        self.notebook.add(self.tab_report, text="Отчёт")
        self.notebook.add(self.tab_experiment, text="Эксперимент")

        self.build_main_tab()
        self.build_anim_tab()
        self.build_db_tab()
        self.build_report_tab()
        self.build_experiment_tab()

    def build_main_tab(self):
        frame_input = ttk.LabelFrame(self.tab_main, text="Ввод исходных данных", padding=10)
        frame_input.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_input, text="Материал:").grid(row=0, column=0, sticky="w", pady=5)
        self.material_var = tk.StringVar()
        self.material_combo = ttk.Combobox(frame_input, textvariable=self.material_var, state="readonly", width=20)
        self.material_combo["values"] = list(material_properties.keys())
        self.material_combo.current(0)
        self.material_combo.grid(row=0, column=1, pady=5)

        self.length_entry = self.add_entry(frame_input, "Длина образца (мм):", 1)
        self.diameter_entry = self.add_entry(frame_input, "Диаметр (мм):", 2)
        self.moment_entry = self.add_entry(frame_input, "Крутящий момент (Н·мм):", 3)
        self.angle_entry  = self.add_entry(frame_input, "Введённый угол (°):", 4)

        btn_calc = ttk.Button(frame_input, text="Рассчитать", command=self.calculate)
        btn_calc.grid(row=5, column=0, padx=5, pady=10)
        btn_reset = ttk.Button(frame_input, text="Сброс", command=self.reset_all)
        btn_reset.grid(row=5, column=1, padx=5, pady=10)

        self.result_label = ttk.Label(frame_input, text="", font=("Segoe UI", 12))
        self.result_label.grid(row=6, column=0, columnspan=2, pady=5)

        frame_expl = ttk.LabelFrame(self.tab_main, text="Пояснения", padding=10)
        frame_expl.pack(fill="x", padx=10, pady=10)
        expl_text = (
            "Расчет базового модуля по формуле:\n"
            "  G = (M * L) / ((π * d⁴)/32 * θ),  θ – угол в радианах.\n\n"
            "Учёт материала: G_eff = k*G в эластичной области (θ ≤ elastic_limit).\n"
            "В пластической области (elastic_limit < θ < failure_angle) G_eff линейно падает до 0.\n"
            "График показывает зависимость G_eff от угла скручивания."
        )
        ttk.Label(frame_expl, text=expl_text, wraplength=800, justify="left").pack()

        self.graph_frame = ttk.LabelFrame(self.tab_main, text="График зависимости", padding=10)
        self.graph_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def add_entry(self, parent, label, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5)
        entry = ttk.Entry(parent, width=25)
        entry.grid(row=row, column=1, pady=5, sticky="ew")
        return entry

    def reset_all(self):
        """
        Сбрасывает поля ввода, очищает результат и график.
        """
        # Сброс материала – установка на первый в списке
        self.material_combo.set(list(material_properties.keys())[0])
        # Очистка полей ввода
        self.length_entry.delete(0, tk.END)
        self.diameter_entry.delete(0, tk.END)
        self.moment_entry.delete(0, tk.END)
        self.angle_entry.delete(0, tk.END)
        # Очистка результата
        self.result_label.config(text="")
        # Очистка графика
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

    def build_anim_tab(self):
        frame_anim = ttk.LabelFrame(self.tab_anim, text="Анимация скручивания", padding=10)
        frame_anim.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas_anim = tk.Canvas(frame_anim, width=300, height=300, bg="white")
        self.canvas_anim.pack()
        self.anim_angle = 0
        self.animate()

    def animate(self):
        self.canvas_anim.delete("all")
        center = 150
        radius = 50
        end_x = center + radius * math.cos(math.radians(self.anim_angle))
        end_y = center + radius * math.sin(math.radians(self.anim_angle))
        self.canvas_anim.create_oval(center - radius, center - radius, center + radius, center + radius, outline="black")
        self.canvas_anim.create_line(center, center, end_x, end_y, fill="red", width=3)
        self.canvas_anim.create_text(center, center + radius + 20,
                                     text=f"Угол анимации: {self.anim_angle}°", font=("Arial", 12))
        self.anim_angle = (self.anim_angle + 5) % 360
        self.canvas_anim.after(100, self.animate)

    def build_db_tab(self):
        frame_db = ttk.LabelFrame(self.tab_db, text="Сохранённые результаты", padding=10)
        frame_db.pack(fill="both", expand=True, padx=10, pady=10)
        self.db_text = tk.Text(frame_db, height=15, font=("Segoe UI", 9))
        self.db_text.pack(fill="both", expand=True)
        btn_refresh = ttk.Button(self.tab_db, text="Обновить", command=self.refresh_db)
        btn_refresh.pack(pady=5)

    def refresh_db(self):
        results = get_results()
        self.db_text.delete("1.0", tk.END)
        header = f"{'ID':<4} | {'Материал':<10} | {'L':<6} | {'d':<6} | {'M':<8} | {'θ':<6} | {'G_eff':<8} | {'Время':<16}\n"
        self.db_text.insert(tk.END, header)
        self.db_text.insert(tk.END, "-" * 80 + "\n")
        for row in results:
            line = f"{row[0]:<4} | {row[1]:<10} | {row[2]:<6} | {row[3]:<6} | {row[4]:<8} | {row[5]:<6} | {row[6]:<8} | {row[7]:<16}\n"
            self.db_text.insert(tk.END, line)

    def build_report_tab(self):
        frame_report = ttk.LabelFrame(self.tab_report, text="Отчёт", padding=10)
        frame_report.pack(fill="x", padx=10, pady=10)
        btn_report = ttk.Button(frame_report, text="Сгенерировать отчёт", command=self.generate_report)
        btn_report.pack(pady=5)

    def build_experiment_tab(self):
        frame_experiment = ttk.LabelFrame(self.tab_experiment, text="Эксперимент", padding=10)
        frame_experiment.pack(fill="both", expand=True, padx=10, pady=10)
        # Пример: кнопка запуска эксперимента
        btn_experiment = ttk.Button(frame_experiment, text="Запустить эксперимент", command=self.run_experiment)
        btn_experiment.pack(pady=10)
        # Контейнер для графика эксперимента
        self.experiment_graph_frame = ttk.Frame(frame_experiment)
        self.experiment_graph_frame.pack(fill="both", expand=True)

    def run_experiment(self):
        # Пример: использование функции plot_experiment_graph с тестовыми данными
        data = [(100, 0.1), (150, 0.15), (200, 0.2)]  # (Момент, Угол)
        plot_experiment_graph(data, None, None, self.experiment_graph_frame)

    def calculate(self):
        try:
            material = self.material_var.get()
            L = float(self.length_entry.get())
            diameter = float(self.diameter_entry.get())
            moment = float(self.moment_entry.get())
            angle_input = float(self.angle_entry.get())
            if L <= 0 or diameter <= 0 or moment <= 0 or angle_input <= 0:
                raise ValueError("Все значения должны быть положительными и угол ≠ 0.")

            props = material_properties.get(material)
            k = props["k"]
            elastic_limit = props["elastic_limit"]
            failure_angle = props["failure_angle"]

            effective_angle = angle_input if angle_input <= failure_angle else failure_angle
            if angle_input > elastic_limit:
                messagebox.showwarning("Предупреждение",
                    f"Угол ({angle_input}°) превышает предел эластичности ({elastic_limit}°).\nПрименяется модель пластичности.")

            if effective_angle <= elastic_limit:
                G_baseline = calculate_basic_G(moment, L, diameter, effective_angle)
            else:
                G0 = calculate_basic_G(moment, L, diameter, elastic_limit)
                G_baseline = G0 * ((failure_angle - effective_angle) / (failure_angle - elastic_limit))
                if G_baseline < 0:
                    G_baseline = 0

            G_eff = round(k * G_baseline, 2)
            self.result_label.config(text=f"Эффективный модуль (G_eff): {G_eff} МПа")
            self.last_result = {
                "material": material,
                "L": L,
                "diameter": diameter,
                "moment": moment,
                "angle": angle_input,
                "G_baseline": G_baseline,
                "G_eff": G_eff,
                "elastic_limit": elastic_limit,
                "failure_angle": failure_angle
            }
            display_angle = min(angle_input, failure_angle)
            # Предполагается, что plot_torsion_curve принимает параметры:
            # (L, diameter, moment, elastic_limit, failure_angle, k, display_angle, container)
            plot_torsion_curve(L, diameter, moment, elastic_limit, failure_angle, k, display_angle, self.graph_frame)

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            insert_result(material, L, diameter, moment, angle_input, G_eff, current_time)
            messagebox.showinfo("Результат", "Расчёт выполнен успешно.")
        except Exception as e:
            messagebox.showerror("Ошибка ввода", f"Некорректный ввод данных: {str(e)}")

    def generate_report(self):
        if self.last_result:
            temp_graph = "temp_graph.png"
            display_angle = min(self.last_result["angle"], self.last_result["failure_angle"])
            # Предполагается, что save_torsion_curve принимает параметры:
            # (L, diameter, moment, elastic_limit, failure_angle, k, display_angle, filename)
            save_torsion_curve(self.last_result["L"], self.last_result["diameter"], self.last_result["moment"],
                               self.last_result["elastic_limit"], self.last_result["failure_angle"],
                               material_properties[self.last_result["material"]]["k"], display_angle, temp_graph)
            file_path = filedialog.asksaveasfilename(defaultextension=".docx",
                                                     filetypes=[("Документы Word", "*.docx")])
            if file_path:
                generate_docx(self.last_result["material"], self.last_result["L"], self.last_result["diameter"],
                              self.last_result["moment"], self.last_result["angle"], self.last_result["G_baseline"],
                              self.last_result["G_eff"], self.last_result["elastic_limit"], self.last_result["failure_angle"],
                              temp_graph, filename=file_path)
                messagebox.showinfo("Отчёт", "Отчёт успешно создан.")
        else:
            messagebox.showwarning("Отчёт", "Сначала выполните расчёт.")

if __name__ == "__main__":
    import sys
    import os
    
    print("=" * 80)
    print("ЛАБОРАТОРНАЯ РАБОТА №4")
    print("Определение модуля упругости второго рода при кручении")
    print("стали, чугуна, дерева")
    print()
    print("Авторы: Коваленко Кирилл, Артем Иокерс")
    print("Группа: ИН-31")
    print("=" * 80)
    print()
    
    # Проверка аргументов командной строки
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        print("Запуск в режиме GUI (Tkinter)...")
        root = tk.Tk()
        app = TorsionApp(root)
        root.mainloop()
    else:
        print("Выберите режим запуска:")
        print("1. Веб-приложение (рекомендуется)")
        print("2. GUI приложение (Tkinter)")
        print()
        
        try:
            choice = input("Введите номер (1 или 2) или нажмите Enter для веб-режима: ").strip()
            
            if choice == '2':
                print("\nЗапуск GUI приложения...")
                root = tk.Tk()
                app = TorsionApp(root)
                root.mainloop()
            else:
                print("\nЗапуск веб-приложения...")
                print("Проверка зависимостей...")
                
                # Проверка наличия Flask
                try:
                    import flask
                    print("✓ Flask найден")
                except ImportError:
                    print("✗ Flask не найден. Установите зависимости:")
                    print("  pip install -r requirements.txt")
                    sys.exit(1)
                
                # Запуск веб-приложения
                from web_app import app as web_app
                try:
                    web_app.run(debug=False, host='0.0.0.0', port=8080, threaded=True)
                except OSError as e:
                    if "Address already in use" in str(e):
                        print(f"\nПорт 8080 уже используется. Пробую порт 8081...")
                        web_app.run(debug=False, host='0.0.0.0', port=8081, threaded=True)
                    else:
                        raise e
                
        except KeyboardInterrupt:
            print("\nПрограмма завершена пользователем.")
        except Exception as e:
            print(f"\nОшибка: {e}")
            print("Запуск GUI по умолчанию...")
            root = tk.Tk()
            app = TorsionApp(root)
            root.mainloop()

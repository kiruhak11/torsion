"""
Flask веб-приложение для лабораторной работы по кручению.
Предоставляет веб-интерфейс и REST API для расчетов.

Авторы: Коваленко К., Иокерс А.
Группа: ИН-31
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import matplotlib
matplotlib.use('Agg')  # Для работы без GUI
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64

from core.calculator import TorsionCalculator, determine_failure_type
from core.database import DatabaseManager
from core.report_generator import ReportGenerator


app = Flask(__name__)
app.config['SECRET_KEY'] = 'torsion-lab-secret-key-2025'

# Инициализация БД
db = DatabaseManager()


@app.route('/')
def index():
    """Главная страница."""
    return render_template('index.html')


@app.route('/api/calculate', methods=['POST'])
def calculate():
    """
    API endpoint для выполнения расчета.
    Принимает JSON с параметрами эксперимента.
    """
    try:
        data = request.json
        
        # Извлечение параметров
        material = data.get('material', 'Сталь')
        diameter = float(data.get('diameter', 10.0)) / 1000  # мм -> м
        length = float(data.get('length', 200.0)) / 1000  # мм -> м
        max_moment = float(data.get('max_moment', 100.0))
        num_points = int(data.get('num_points', 50))
        
        # Создание калькулятора
        calculator = TorsionCalculator(diameter, length, material)
        
        # Генерация данных с реалистичной погрешностью
        diagram_data = calculator.generate_diagram_data(
            max_moment, 
            num_points,
            add_experimental_noise=True,  # Добавляем экспериментальную погрешность!
            error_percent=2.0  # 2% погрешность
        )
        
        # Обработка ЭКСПЕРИМЕНТАЛЬНЫХ данных (с погрешностью)
        results = calculator.process_experiment_data(
            diagram_data['T'],
            diagram_data['phi']
        )
        
        # Добавление дополнительной информации
        results['failure_type'] = determine_failure_type(material)
        results['Jp'] = float(calculator.calc_polar_moment_inertia())
        results['Wp'] = float(calculator.calc_polar_section_modulus())
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/plot/torsion', methods=['POST'])
def plot_torsion():
    """
    Генерация графика диаграммы T-φ.
    Возвращает изображение в формате base64.
    """
    try:
        data = request.json
        moments = data.get('moments', [])
        angles = data.get('angles', [])
        
        # Построение графика
        fig, ax = plt.subplots(figsize=(10, 6))
        
        angles_deg = np.array(angles) * 180 / np.pi
        ax.plot(angles_deg, moments, 'b-', linewidth=2.5, label='Экспериментальная кривая')
        ax.scatter(angles_deg, moments, c='red', s=40, alpha=0.6, zorder=5)
        
        ax.set_xlabel('Угол закручивания φ, град', fontsize=13, fontweight='bold')
        ax.set_ylabel('Крутящий момент T, Н·м', fontsize=13, fontweight='bold')
        ax.set_title('Диаграмма кручения T-φ', fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Выделение упругой области
        linear_idx = int(len(moments) * 0.7)
        if linear_idx > 1:
            ax.axvspan(0, angles_deg[linear_idx], alpha=0.15, color='green', label='Упругая область')
            ax.axvline(x=angles_deg[linear_idx], color='orange', linestyle='--', linewidth=2, label='Предел упругости')
        
        ax.legend(fontsize=11)
        plt.tight_layout()
        
        # Конвертация в base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{image_base64}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/plot/stress', methods=['POST'])
def plot_stress():
    """
    Генерация графика распределения касательных напряжений.
    """
    try:
        data = request.json
        
        material = data.get('material', 'Сталь')
        diameter = float(data.get('diameter', 10.0)) / 1000
        length = float(data.get('length', 200.0)) / 1000
        moment = float(data.get('moment', 50.0))
        
        calculator = TorsionCalculator(diameter, length, material)
        
        # Построение графика
        fig, ax = plt.subplots(figsize=(10, 6))
        
        rho, tau = calculator.calc_shear_stress_distribution(moment, 50)
        rho_mm = rho * 1000
        tau_mpa = tau / 1e6
        
        ax.plot(tau_mpa, rho_mm, 'r-', linewidth=3, label='τ(ρ)')
        ax.fill_betweenx(rho_mm, 0, tau_mpa, alpha=0.3, color='red')
        
        max_tau = np.max(tau_mpa)
        max_rho = diameter * 1000 / 2
        ax.plot([max_tau], [max_rho], 'ro', markersize=12, label=f'τmax = {max_tau:.2f} МПа')
        
        ax.set_xlabel('Касательное напряжение τ, МПа', fontsize=13, fontweight='bold')
        ax.set_ylabel('Радиус ρ, мм', fontsize=13, fontweight='bold')
        ax.set_title(f'Распределение τ по сечению при T = {moment:.2f} Н·м', fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.axhline(y=max_rho, color='k', linestyle='--', linewidth=1.5, label=f'R = {max_rho:.2f} мм')
        ax.legend(fontsize=11)
        
        ax.text(max_tau * 0.5, max_rho * 0.5, 'Линейное\nраспределение',
               fontsize=12, ha='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.6))
        
        plt.tight_layout()
        
        # Конвертация в base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{image_base64}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/experiments', methods=['GET'])
def get_experiments():
    """Получение списка всех экспериментов."""
    try:
        experiments = db.get_all_experiments()
        return jsonify({
            'success': True,
            'experiments': experiments
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/experiments/<int:exp_id>', methods=['GET'])
def get_experiment(exp_id):
    """Получение конкретного эксперимента."""
    try:
        experiment = db.get_experiment(exp_id)
        if experiment:
            return jsonify({
                'success': True,
                'experiment': experiment
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Эксперимент не найден'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/experiments', methods=['POST'])
def save_experiment():
    """Сохранение эксперимента в БД."""
    try:
        data = request.json
        
        user_name = data.get('user_name', 'Anonymous')
        material = data.get('material', 'Сталь')
        diameter = float(data.get('diameter', 10.0)) / 1000
        length = float(data.get('length', 200.0)) / 1000
        input_params = data.get('input_params', {})
        results = data.get('results', {})
        
        exp_id = db.save_experiment(
            user_name, material, diameter, length,
            input_params, results
        )
        
        return jsonify({
            'success': True,
            'experiment_id': exp_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/test', methods=['POST'])
def check_test():
    """Проверка ответов теста."""
    try:
        data = request.json
        answers = data.get('answers', {})
        user_name = data.get('user_name', 'Anonymous')
        
        # Правильные ответы
        correct_answers = [0, 2, 1, 1, 2, 0, 2, 2]
        
        score = 0
        for i, correct in enumerate(correct_answers):
            if str(i) in answers and answers[str(i)] == correct:
                score += 1
        
        # Сохранение результата
        db.save_test_result(user_name, score, answers)
        
        percentage = (score / 8) * 100
        
        if percentage >= 75:
            grade = "Отлично!"
        elif percentage >= 60:
            grade = "Хорошо!"
        elif percentage >= 50:
            grade = "Удовлетворительно"
        else:
            grade = "Неудовлетворительно"
        
        return jsonify({
            'success': True,
            'score': score,
            'total': 8,
            'percentage': percentage,
            'grade': grade
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/report/generate', methods=['POST'])
def generate_report():
    """Генерация отчета в формате .docx."""
    try:
        data = request.json
        
        user_name = data.get('user_name', 'Пользователь')
        group = data.get('group', 'ИН-31')
        material = data.get('material', 'Сталь')
        diameter = float(data.get('diameter', 10.0)) / 1000
        length = float(data.get('length', 200.0)) / 1000
        results = data.get('results', {})
        
        calculator = TorsionCalculator(diameter, length, material)
        
        # Генерация временных графиков
        diagram_path = 'temp_web_diagram.png'
        stress_path = 'temp_web_stress.png'
        
        # График T-φ
        if 'moments' in results and 'angles' in results:
            fig, ax = plt.subplots(figsize=(8, 6))
            angles_deg = np.array(results['angles']) * 180 / np.pi
            ax.plot(angles_deg, results['moments'], 'b-', linewidth=2)
            ax.scatter(angles_deg, results['moments'], c='red', s=30, alpha=0.6)
            ax.set_xlabel('Угол закручивания φ, град', fontsize=12)
            ax.set_ylabel('Крутящий момент T, Н·м', fontsize=12)
            ax.set_title('Диаграмма кручения T-φ', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(diagram_path, dpi=150)
            plt.close()
        
        # График распределения напряжений
        if 'T_max' in results:
            fig, ax = plt.subplots(figsize=(8, 6))
            rho, tau = calculator.calc_shear_stress_distribution(results['T_max'], 50)
            ax.plot(tau/1e6, rho*1000, 'r-', linewidth=2)
            ax.fill_betweenx(rho*1000, 0, tau/1e6, alpha=0.3, color='red')
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
            user_name, group, calculator, results,
            diagram_path if os.path.exists(diagram_path) else None,
            stress_path if os.path.exists(stress_path) else None
        )
        
        # Очистка временных файлов
        for path in [diagram_path, stress_path]:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except:
                pass
        
        return jsonify({
            'success': True,
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.errorhandler(404)
def not_found(error):
    """Обработка 404 ошибки."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработка 500 ошибки."""
    return jsonify({'error': 'Internal server error'}), 500


@app.route('/animation/sample', methods=['GET'])
def sample_animation():
    """Отдача базовой GIF-анимации для веб-интерфейса."""
    gif_path = os.path.join(app.root_path, 'torsion_animation.gif')
    if os.path.exists(gif_path):
        return send_file(gif_path, mimetype='image/gif')
    return jsonify({'error': 'Анимация не найдена'}), 404


if __name__ == '__main__':
    print("="*70)
    print("  FLASK ВЕБ-ПРИЛОЖЕНИЕ: ЛАБОРАТОРНАЯ РАБОТА ПО КРУЧЕНИЮ")
    print("="*70)
    print("  Авторы: Коваленко Кирилл, Иокерс Артем")
    print("  Группа: ИН-31")
    print("="*70)
    print("\n🌐 Запуск веб-сервера...")
    print("📍 Адрес: http://localhost:5001")
    print("\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)

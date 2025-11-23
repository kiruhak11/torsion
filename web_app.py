#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Веб-приложение для лабораторной работы №4
Определение модуля упругости второго рода при кручении
Авторы: Коваленко Кирилл, Артем Иокерс, группа ИН-31
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, send_from_directory
from flask_cors import CORS
import os
import json
import base64
import io
import webbrowser
import threading
import time
from datetime import datetime
import tempfile

from calculator import calculate_basic_G, analyze_experiment
from graph import save_torsion_curve
from report_docx import generate_docx
from db_manager import init_db, insert_result, get_results
from examples import get_all_examples, validate_result, EXPERIMENT_DATA_EXAMPLES

app = Flask(__name__)
CORS(app)

# Свойства материалов
material_properties = {
    "Сталь": {"k": 1.0, "elastic_limit": 15, "failure_angle": 30},
    "Чугун": {"k": 0.95, "elastic_limit": 10, "failure_angle": 20},
    "Дерево": {"k": 0.80, "elastic_limit": 8, "failure_angle": 16}
}

# Инициализация базы данных
init_db()

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html', 
                         materials=list(material_properties.keys()),
                         student_info="Коваленко Кирилл, Артем Иокерс, группа ИН-31")

@app.route('/static/<path:filename>')
def static_files(filename):
    """Обслуживание статических файлов"""
    return send_from_directory('static', filename)

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """API для расчета модуля упругости"""
    try:
        data = request.json
        material = data['material']
        L = float(data['length'])
        diameter = float(data['diameter'])
        moment = float(data['moment'])
        angle_input = float(data['angle'])
        
        # Валидация входных данных
        if L <= 0 or diameter <= 0 or moment <= 0 or angle_input <= 0:
            return jsonify({
                'success': False, 
                'error': 'Все значения должны быть положительными и угол ≠ 0.'
            })
        
        props = material_properties.get(material)
        if not props:
            return jsonify({
                'success': False, 
                'error': 'Неизвестный материал.'
            })
            
        k = props["k"]
        elastic_limit = props["elastic_limit"]
        failure_angle = props["failure_angle"]
        
        # Ограничение угла до угла разрушения
        effective_angle = min(angle_input, failure_angle)
        
        # Расчет модуля упругости
        if effective_angle <= elastic_limit:
            G_baseline = calculate_basic_G(moment, L, diameter, effective_angle)
        else:
            G0 = calculate_basic_G(moment, L, diameter, elastic_limit)
            if G0:
                G_baseline = G0 * ((failure_angle - effective_angle) / (failure_angle - elastic_limit))
                G_baseline = max(0, G_baseline)
            else:
                G_baseline = 0
        
        G_eff = round(k * G_baseline, 2) if G_baseline else 0
        
        # Создание графика и кодирование в base64
        graph_data = generate_graph_base64(L, diameter, moment, elastic_limit, failure_angle, k, effective_angle)
        
        # Сохранение в базу данных
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        insert_result(material, L, diameter, moment, angle_input, G_eff, current_time)
        
        result = {
            'success': True,
            'G_eff': G_eff,
            'G_baseline': round(G_baseline, 2),
            'effective_angle': effective_angle,
            'elastic_limit': elastic_limit,
            'failure_angle': failure_angle,
            'material': material,
            'graph': graph_data,
            'warning': f"Угол ({angle_input}°) превышает предел эластичности ({elastic_limit}°). Применяется модель пластичности." if angle_input > elastic_limit else None
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка при расчете: {str(e)}'
        })

def generate_graph_base64(L, diameter, moment, elastic_limit, failure_angle, k, display_angle):
    """Генерирует график и возвращает его в формате base64"""
    import matplotlib
    matplotlib.use('Agg')  # Backend без GUI
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Создание массива углов
    angles = np.linspace(0.1, min(display_angle * 1.2, failure_angle), 100)
    G_values = []
    
    for angle in angles:
        if angle <= elastic_limit:
            G_baseline = calculate_basic_G(moment, L, diameter, angle)
            G_eff = k * G_baseline if G_baseline else 0
        elif angle <= failure_angle:
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
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    ax.plot(angles, G_values, linewidth=3, color='darkblue', label='G_eff(θ)')
    ax.axvline(x=elastic_limit, color='orange', linestyle='--', alpha=0.8, linewidth=2, 
               label=f'Предел эластичности ({elastic_limit}°)')
    ax.axvline(x=failure_angle, color='red', linestyle='--', alpha=0.8, linewidth=2, 
               label=f'Угол разрушения ({failure_angle}°)')
    
    if display_angle <= failure_angle and len(G_values) > 0:
        current_G = G_values[np.argmin(np.abs(angles - display_angle))]
        ax.plot(display_angle, current_G, 'ro', markersize=10, 
                label=f'Текущая точка ({display_angle:.1f}°, {current_G:.1f} МПа)')
    
    ax.set_xlabel('Угол поворота θ (градусы)', fontsize=12)
    ax.set_ylabel('Эффективный модуль G_eff (МПа)', fontsize=12)
    ax.set_title('Зависимость эффективного модуля упругости от угла поворота', fontsize=14, pad=20)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    
    # Конвертация в base64
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close(fig)
    
    graphic = base64.b64encode(image_png).decode('utf-8')
    return graphic

@app.route('/api/database')
def get_database():
    """API для получения данных из базы"""
    try:
        results = get_results()
        data = []
        for row in results:
            data.append({
                'id': row[0],
                'material': row[1],
                'L': row[2],
                'diameter': row[3],
                'moment': row[4],
                'angle': row[5],
                'G': row[6],
                'timestamp': row[7]
            })
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/examples')
def get_examples():
    """API для получения примеров расчетов"""
    try:
        examples = get_all_examples()
        examples_list = []
        for name, example in examples.items():
            examples_list.append({
                'name': name,
                'material': example['material'],
                'length': example['length'],
                'diameter': example['diameter'],
                'moment': example['moment'],
                'angle': example['angle'],
                'description': example['description'],
                'expected_G_eff': example['expected_G_eff']
            })
        return jsonify({'success': True, 'examples': examples_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/validate', methods=['POST'])
def validate_calculation():
    """API для валидации результатов расчета"""
    try:
        data = request.json
        material = data['material']
        calculated_G = float(data['G_eff'])
        
        validation = validate_result(material, calculated_G)
        return jsonify({
            'success': True,
            'validation': validation
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/experiment', methods=['POST'])
def run_experiment():
    """API для анализа экспериментальных данных"""
    try:
        data = request.json
        experiment_data = data.get('data', [])  # [(T1, φ1), (T2, φ2), ...]
        L = float(data.get('L', 100))
        diameter = float(data.get('diameter', 10))
        
        if not experiment_data:
            return jsonify({'success': False, 'error': 'Нет экспериментальных данных'})
        
        # Анализ экспериментальных данных
        results = analyze_experiment(experiment_data, L, diameter)
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/report', methods=['POST'])
def generate_report():
    """API для генерации отчета"""
    try:
        data = request.json
        
        # Создание временного файла для графика
        temp_graph = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_graph.close()
        
        # Сохранение графика
        save_torsion_curve(
            data['L'], data['diameter'], data['moment'],
            data['elastic_limit'], data['failure_angle'],
            material_properties[data['material']]['k'],
            data['effective_angle'], temp_graph.name
        )
        
        # Создание временного файла для отчета
        temp_report = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
        temp_report.close()
        
        # Генерация отчета
        generate_docx(
            data['material'], data['L'], data['diameter'],
            data['moment'], data['angle'], data['G_baseline'],
            data['G_eff'], data['elastic_limit'], data['failure_angle'],
            temp_graph.name, filename=temp_report.name
        )
        
        # Удаление временного файла графика
        os.unlink(temp_graph.name)
        
        return send_file(
            temp_report.name,
            as_attachment=True,
            download_name=f"torsion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def open_browser():
    """Открывает браузер через 1.5 секунды после запуска сервера"""
    time.sleep(1.5)
    # Попробуем разные порты
    for port in [8080, 8081, 8082]:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result == 0:  # Порт открыт
                webbrowser.open(f'http://localhost:{port}')
                break
        except:
            continue
    else:
        webbrowser.open('http://localhost:8080')  # По умолчанию

if __name__ == '__main__':
    # Создание директории для шаблонов
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("=" * 60)
    print("Лабораторная работа №4")
    print("Определение модуля упругости второго рода при кручении")
    print("Авторы: Коваленко Кирилл, Артем Иокерс, группа ИН-31")
    print("=" * 60)
    print("\nЗапуск веб-приложения...")
    print("Адрес: http://localhost:8080")
    print("Для остановки нажмите Ctrl+C")
    print("=" * 60)
    
    # Запуск браузера в отдельном потоке
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Запуск Flask приложения
    try:
        app.run(debug=False, host='0.0.0.0', port=8080, threaded=True)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\nПорт 8080 уже используется. Пробую порт 8081...")
            app.run(debug=False, host='0.0.0.0', port=8081, threaded=True)
        else:
            raise e

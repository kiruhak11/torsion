#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Умный запуск лабораторной работы №4
Автоматически находит свободный порт и запускает приложение
Авторы: Коваленко Кирилл, Артем Иокерс, группа ИН-31
"""

import socket
import subprocess
import sys
import os
import webbrowser
import time
import threading

def find_free_port(start_port=8080, max_attempts=10):
    """Находит свободный порт начиная с start_port"""
    for port in range(start_port, start_port + max_attempts):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            continue
        finally:
            sock.close()
    return None

def check_dependencies():
    """Проверяет наличие необходимых зависимостей"""
    required_modules = ['flask', 'matplotlib', 'numpy', 'docx']
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    return missing

def open_browser_delayed(port):
    """Открывает браузер через задержку"""
    time.sleep(2)
    webbrowser.open(f'http://localhost:{port}')

def main():
    print("=" * 80)
    print("ЛАБОРАТОРНАЯ РАБОТА №4")
    print("Определение модуля упругости второго рода при кручении")
    print("стали, чугуна, дерева")
    print()
    print("Авторы: Коваленко Кирилл, Артем Иокерс")
    print("Группа: ИН-31")
    print("=" * 80)
    print()

    # Проверка зависимостей
    print("Проверка зависимостей...")
    missing = check_dependencies()
    
    if missing:
        print(f"✗ Отсутствуют модули: {', '.join(missing)}")
        print("Попытка автоматической установки...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("✓ Зависимости установлены")
        except subprocess.CalledProcessError:
            print("✗ Не удалось установить зависимости")
            print("Попробуйте вручную: pip install -r requirements.txt")
            return
    else:
        print("✓ Все зависимости найдены")

    # Поиск свободного порта
    print("\nПоиск свободного порта...")
    port = find_free_port()
    
    if not port:
        print("✗ Не удалось найти свободный порт")
        print("Попробуйте закрыть другие веб-приложения")
        return
    
    print(f"✓ Найден свободный порт: {port}")
    
    # Запуск веб-приложения
    print(f"\nЗапуск веб-приложения на порту {port}...")
    print(f"Адрес: http://localhost:{port}")
    print("Браузер откроется автоматически через 2 секунды")
    print("Для остановки нажмите Ctrl+C")
    print("=" * 80)
    
    # Запуск браузера в отдельном потоке
    threading.Thread(target=open_browser_delayed, args=(port,), daemon=True).start()
    
    # Запуск Flask приложения
    try:
        os.environ['FLASK_PORT'] = str(port)
        from web_app import app
        app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
    except KeyboardInterrupt:
        print("\n\nПрограмма завершена пользователем. До свидания!")
    except Exception as e:
        print(f"\nОшибка при запуске: {e}")
        print("Попробуйте запустить: python main.py")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт установки и проверки зависимостей
Лабораторная работа №4 - Кручение
Авторы: Коваленко Кирилл, Артем Иокерс, группа ИН-31
"""

import subprocess
import sys
import os

def print_header():
    print("=" * 80)
    print("ЛАБОРАТОРНАЯ РАБОТА №4")
    print("Определение модуля упругости второго рода при кручении")
    print("стали, чугуна, дерева")
    print()
    print("Авторы: Коваленко Кирилл, Артем Иокерс")
    print("Группа: ИН-31")
    print("=" * 80)
    print()

def check_python():
    """Проверка версии Python"""
    print("Проверка Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"✗ Python {version.major}.{version.minor} слишком старая версия")
        print("Требуется Python 3.7 или новее")
        return False
    else:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True

def install_requirements():
    """Установка зависимостей"""
    print("\nУстановка зависимостей...")
    
    requirements = [
        "matplotlib>=3.5.0",
        "python-docx>=0.8.11", 
        "Pillow>=9.0.0",
        "numpy>=1.21.0",
        "flask>=2.0.0",
        "flask-cors>=3.0.10",
        "waitress>=2.1.0"
    ]
    
    failed = []
    
    for req in requirements:
        try:
            print(f"Устанавливаю {req}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", req], 
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✓ {req}")
        except subprocess.CalledProcessError:
            print(f"✗ Ошибка установки {req}")
            failed.append(req)
    
    if failed:
        print(f"\nНе удалось установить: {', '.join(failed)}")
        print("Попробуйте выполнить вручную:")
        print(f"pip install {' '.join(failed)}")
        return False
    
    return True

def check_imports():
    """Проверка импорта модулей"""
    print("\nПроверка модулей...")
    
    modules = [
        ("matplotlib", "matplotlib"),
        ("numpy", "numpy"), 
        ("flask", "Flask"),
        ("docx", "python-docx"),
        ("PIL", "Pillow"),
        ("flask_cors", "flask-cors")
    ]
    
    failed = []
    
    for module, package in modules:
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package}")
            failed.append(package)
    
    return len(failed) == 0

def create_directories():
    """Создание необходимых директорий"""
    print("\nСоздание директорий...")
    
    dirs = ["data", "templates", "static"]
    
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✓ Создана директория {dir_name}")
        else:
            print(f"✓ Директория {dir_name} уже существует")

def main():
    print_header()
    
    success = True
    
    # Проверка Python
    if not check_python():
        success = False
    
    # Установка зависимостей
    if success and not install_requirements():
        success = False
    
    # Проверка импорта
    if success and not check_imports():
        success = False
    
    # Создание директорий
    if success:
        create_directories()
    
    print("\n" + "=" * 80)
    
    if success:
        print("✓ УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!")
        print("\nДля запуска используйте:")
        print("  python main.py          # Веб-приложение")
        print("  python main.py --gui    # GUI приложение")
        print("\nИли используйте готовые скрипты:")
        if os.name == 'nt':
            print("  start.bat               # Для Windows")
        else:
            print("  ./start.sh              # Для macOS/Linux")
    else:
        print("✗ ОШИБКИ ПРИ УСТАНОВКЕ!")
        print("\nПопробуйте установить зависимости вручную:")
        print("  pip install -r requirements.txt")
    
    print("=" * 80)

if __name__ == "__main__":
    main()

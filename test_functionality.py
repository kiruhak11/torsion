#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование функциональности приложения
Лабораторная работа №4 - Кручение
Авторы: Коваленко Кирилл, Артем Иокерс, группа ИН-31
"""

def test_calculator():
    """Тест расчетных функций"""
    print("Тестирование расчетных функций...")
    from calculator import calculate_basic_G, polar_moment_inertia, calculate_tau
    
    # Тест 1: Основной расчет
    G = calculate_basic_G(1000, 100, 10, 10)
    assert G is not None and G > 0, "Ошибка в расчете модуля упругости"
    print(f"✓ Расчет модуля упругости: G = {G} МПа")
    
    # Тест 2: Полярный момент инерции
    J = polar_moment_inertia(10)
    expected_J = 3.14159 * (10**4) / 32
    assert abs(J - expected_J) < 0.01, "Ошибка в расчете полярного момента"
    print(f"✓ Полярный момент инерции: J = {J:.2f} мм⁴")
    
    # Тест 3: Касательные напряжения
    tau = calculate_tau(1000, 10)
    assert tau is not None and tau > 0, "Ошибка в расчете касательных напряжений"
    print(f"✓ Касательные напряжения: τ = {tau} МПа")

def test_database():
    """Тест базы данных"""
    print("\nТестирование базы данных...")
    from db_manager import init_db, insert_result, get_results
    from datetime import datetime
    
    # Инициализация БД
    init_db()
    print("✓ Инициализация базы данных")
    
    # Вставка тестовой записи
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    insert_result("Сталь", 100.0, 10.0, 1000.0, 10.0, 583.61, timestamp)
    print("✓ Вставка тестовой записи")
    
    # Получение записей
    results = get_results()
    assert len(results) > 0, "Нет записей в базе данных"
    print(f"✓ Получение записей: найдено {len(results)} записей")

def test_materials():
    """Тест материалов"""
    print("\nТестирование материалов...")
    materials = {
        "Сталь": {"k": 1.0, "elastic_limit": 15, "failure_angle": 30},
        "Чугун": {"k": 0.95, "elastic_limit": 10, "failure_angle": 20},
        "Дерево": {"k": 0.80, "elastic_limit": 8, "failure_angle": 16}
    }
    
    for material, props in materials.items():
        assert 0 < props["k"] <= 1.0, f"Некорректный коэффициент для {material}"
        assert props["elastic_limit"] < props["failure_angle"], f"Некорректные пределы для {material}"
        print(f"✓ {material}: k={props['k']}, пределы={props['elastic_limit']}°-{props['failure_angle']}°")

def test_graph_functions():
    """Тест функций графиков"""
    print("\nТестирование функций графиков...")
    try:
        import matplotlib
        matplotlib.use('Agg')  # Backend без GUI
        from graph import save_torsion_curve
        import tempfile
        
        # Создание временного файла
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_file.close()
        
        # Тест сохранения графика
        save_torsion_curve(100, 10, 1000, 15, 30, 1.0, 10, temp_file.name)
        
        import os
        assert os.path.exists(temp_file.name), "График не создан"
        assert os.path.getsize(temp_file.name) > 0, "График пустой"
        
        # Очистка
        os.unlink(temp_file.name)
        print("✓ Сохранение графиков")
        
    except ImportError as e:
        print(f"⚠ Пропуск теста графиков: {e}")

def test_web_app_import():
    """Тест импорта веб-приложения"""
    print("\nТестирование импорта веб-приложения...")
    try:
        from web_app import app
        assert app is not None, "Flask приложение не создано"
        print("✓ Импорт веб-приложения")
    except ImportError as e:
        print(f"✗ Ошибка импорта веб-приложения: {e}")
        raise

def main():
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ ФУНКЦИОНАЛЬНОСТИ")
    print("Лабораторная работа №4 - Кручение")
    print("Авторы: Коваленко Кирилл, Артем Иокерс, группа ИН-31")
    print("=" * 70)
    
    tests = [
        test_calculator,
        test_database,
        test_materials,
        test_graph_functions,
        test_web_app_import
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ Тест {test.__name__} провален: {e}")
    
    print("\n" + "=" * 70)
    print(f"РЕЗУЛЬТАТ ТЕСТИРОВАНИЯ: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("\nПриложение готово к использованию:")
        print("  python main.py          # Основной запуск")
        print("  python launch.py        # Умный запуск")
        print("  ./start.sh              # Скрипт для macOS/Linux")
    else:
        print("❌ ЕСТЬ ПРОБЛЕМЫ В ФУНКЦИОНАЛЬНОСТИ")
        print("Рекомендуется исправить ошибки перед использованием")
    
    print("=" * 70)

if __name__ == "__main__":
    main()

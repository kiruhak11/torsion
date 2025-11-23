#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Примеры расчетов для лабораторной работы №4
Определение модуля упругости второго рода при кручении
Авторы: Коваленко Кирилл, Артем Иокерс, группа ИН-31
"""

# Примеры данных для демонстрации
EXAMPLE_CALCULATIONS = {
    "Сталь - упругая область": {
        "material": "Сталь",
        "length": 100.0,
        "diameter": 10.0,
        "moment": 140000.0,  # Н·мм (140 Н·м)
        "angle": 10.0,
        "description": "Расчет для стали в пределах упругости (угол < 15°)",
        "expected_G_eff": 81705.0  # Примерное значение (типично для стали)
    },
    
    "Сталь - пластическая область": {
        "material": "Сталь",
        "length": 120.0,
        "diameter": 12.0,
        "moment": 160000.0,  # Н·мм
        "angle": 20.0,
        "description": "Расчет для стали за пределом упругости (угол > 15°)",
        "expected_G_eff": 38000.0  # Снижается в пластической области
    },
    
    "Чугун - упругая область": {
        "material": "Чугун",
        "length": 100.0,
        "diameter": 10.0,
        "moment": 70000.0,  # Н·мм
        "angle": 8.0,
        "description": "Расчет для чугуна в пределах упругости (угол < 10°)",
        "expected_G_eff": 51000.0  # Примерное значение для чугуна
    },
    
    "Чугун - предел разрушения": {
        "material": "Чугун",
        "length": 150.0,
        "diameter": 12.0,
        "moment": 80000.0,  # Н·мм
        "angle": 15.0,
        "description": "Расчет для чугуна близко к пределу разрушения (угол > 10°)",
        "expected_G_eff": 15000.0  # Сильно снижен в пластической области
    },
    
    "Дерево - упругая область": {
        "material": "Дерево",
        "length": 100.0,
        "diameter": 10.0,
        "moment": 1400.0,  # Н·мм (малый момент для дерева)
        "angle": 5.0,
        "description": "Расчет для дерева в пределах упругости (угол < 8°)",
        "expected_G_eff": 1300.0  # Типично для дерева (800-2000 МПа)
    },
    
    "Дерево - пластическая область": {
        "material": "Дерево",
        "length": 100.0,
        "diameter": 10.0,
        "moment": 2000.0,  # Н·мм
        "angle": 12.0,
        "description": "Расчет для дерева за пределом упругости (угол > 8°)",
        "expected_G_eff": 600.0  # Снижен в пластической области
    }
}

# Типичные значения модулей упругости для справки
TYPICAL_G_VALUES = {
    "Сталь": {
        "min": 75000,  # МПа
        "max": 85000,
        "typical": 80000,
        "description": "Модуль сдвига стали обычно находится в диапазоне 75-85 ГПа"
    },
    "Чугун": {
        "min": 30000,
        "max": 50000,
        "typical": 40000,
        "description": "Модуль сдвига чугуна обычно находится в диапазоне 30-50 ГПа"
    },
    "Дерево": {
        "min": 500,
        "max": 2000,
        "typical": 1000,
        "description": "Модуль сдвига дерева сильно зависит от породы и направления волокон"
    }
}

# Экспериментальные данные для демонстрации анализа
EXPERIMENT_DATA_EXAMPLES = {
    "Сталь - линейная зависимость": [
        (100, 0.5),   # (Момент Н·мм, Угол °)
        (200, 1.0),
        (300, 1.5),
        (400, 2.0),
        (500, 2.5),
        (600, 3.0),
        (700, 3.5),
        (800, 4.0)
    ],
    
    "Чугун с пластичностью": [
        (50, 0.3),
        (100, 0.6),
        (150, 0.9),
        (200, 1.3),
        (250, 1.8),
        (300, 2.5),
        (320, 3.0),
        (330, 3.8)
    ],
    
    "Дерево до разрушения": [
        (50, 0.5),
        (100, 1.0),
        (150, 1.6),
        (200, 2.3),
        (250, 3.2),
        (280, 4.5),
        (290, 6.0),
        (285, 8.0)  # Начало разрушения
    ]
}

def get_example_by_name(name):
    """Получить пример расчета по имени"""
    return EXAMPLE_CALCULATIONS.get(name, None)

def get_all_examples():
    """Получить все примеры расчетов"""
    return EXAMPLE_CALCULATIONS

def get_typical_values(material):
    """Получить типичные значения модуля упругости для материала"""
    return TYPICAL_G_VALUES.get(material, None)

def get_experiment_example(name):
    """Получить экспериментальные данные по имени"""
    return EXPERIMENT_DATA_EXAMPLES.get(name, None)

def validate_result(material, calculated_G, tolerance=0.2):
    """
    Проверить, находится ли рассчитанное значение в разумных пределах
    
    Args:
        material: Материал образца
        calculated_G: Рассчитанное значение модуля упругости (МПа)
        tolerance: Допустимое отклонение от типичных значений (0.2 = ±20%)
    
    Returns:
        dict: {"valid": bool, "message": str, "typical_range": tuple}
    """
    typical = TYPICAL_G_VALUES.get(material)
    if not typical:
        return {
            "valid": None,
            "message": "Нет данных для проверки",
            "typical_range": None
        }
    
    min_allowed = typical["min"] * (1 - tolerance)
    max_allowed = typical["max"] * (1 + tolerance)
    
    is_valid = min_allowed <= calculated_G <= max_allowed
    
    if is_valid:
        message = f"✓ Результат в пределах нормы для {material}"
    else:
        if calculated_G < min_allowed:
            message = f"⚠ Результат слишком низкий для {material}"
        else:
            message = f"⚠ Результат слишком высокий для {material}"
    
    return {
        "valid": is_valid,
        "message": message,
        "typical_range": (typical["min"], typical["max"]),
        "calculated": calculated_G
    }

if __name__ == "__main__":
    # Демонстрация примеров
    print("=" * 60)
    print("ПРИМЕРЫ РАСЧЕТОВ ДЛЯ ЛАБОРАТОРНОЙ РАБОТЫ №4")
    print("=" * 60)
    print()
    
    for name, example in EXAMPLE_CALCULATIONS.items():
        print(f"Пример: {name}")
        print(f"  Описание: {example['description']}")
        print(f"  Материал: {example['material']}")
        print(f"  L = {example['length']} мм, d = {example['diameter']} мм")
        print(f"  M = {example['moment']} Н·мм, θ = {example['angle']}°")
        print(f"  Ожидаемый G_eff ≈ {example['expected_G_eff']} МПа")
        print()
    
    print("=" * 60)
    print("ТИПИЧНЫЕ ЗНАЧЕНИЯ МОДУЛЕЙ УПРУГОСТИ")
    print("=" * 60)
    print()
    
    for material, values in TYPICAL_G_VALUES.items():
        print(f"{material}:")
        print(f"  Диапазон: {values['min']} - {values['max']} МПа")
        print(f"  Типичное значение: {values['typical']} МПа")
        print(f"  Примечание: {values['description']}")
        print()


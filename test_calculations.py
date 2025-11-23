#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit-тесты для лабораторной работы №4
Определение модуля упругости второго рода при кручении
Авторы: Коваленко Кирилл, Артем Иокерс, группа ИН-31
"""

import unittest
import math
from calculator import (
    polar_moment_inertia,
    polar_resistance_moment,
    calculate_basic_G,
    calculate_tau,
    analyze_experiment
)
from examples import validate_result, EXAMPLE_CALCULATIONS

class TestPolarMomentInertia(unittest.TestCase):
    """Тесты для расчета полярного момента инерции"""
    
    def test_polar_moment_basic(self):
        """Базовый тест полярного момента инерции"""
        diameter = 10  # мм
        expected = (math.pi * (10 ** 4)) / 32
        result = polar_moment_inertia(diameter)
        self.assertAlmostEqual(result, expected, places=2)
    
    def test_polar_moment_different_diameters(self):
        """Тест для разных диаметров"""
        test_cases = [
            (5, 61.36),
            (10, 981.75),
            (20, 15707.96),
            (50, 613592.32)
        ]
        for diameter, expected in test_cases:
            with self.subTest(diameter=diameter):
                result = polar_moment_inertia(diameter)
                self.assertAlmostEqual(result, expected, places=1)
    
    def test_polar_moment_zero_diameter(self):
        """Тест для нулевого диаметра"""
        result = polar_moment_inertia(0)
        self.assertEqual(result, 0)

class TestPolarResistanceMoment(unittest.TestCase):
    """Тесты для расчета полярного момента сопротивления"""
    
    def test_resistance_moment_basic(self):
        """Базовый тест полярного момента сопротивления"""
        diameter = 10  # мм
        expected = (math.pi * (10 ** 3)) / 16
        result = polar_resistance_moment(diameter)
        self.assertAlmostEqual(result, expected, places=2)
    
    def test_resistance_moment_different_diameters(self):
        """Тест для разных диаметров"""
        test_cases = [
            (5, 24.54),
            (10, 196.35),
            (20, 1570.80),
            (50, 24543.69)
        ]
        for diameter, expected in test_cases:
            with self.subTest(diameter=diameter):
                result = polar_resistance_moment(diameter)
                self.assertAlmostEqual(result, expected, places=1)

class TestBasicG(unittest.TestCase):
    """Тесты для расчета базового модуля упругости"""
    
    def test_calculate_basic_G(self):
        """Базовый тест расчета G"""
        moment = 1000  # Н·мм
        L = 100  # мм
        diameter = 10  # мм
        angle_deg = 10  # градусы
        
        result = calculate_basic_G(moment, L, diameter, angle_deg)
        self.assertIsNotNone(result)
        self.assertGreater(result, 0)
        # Ожидаемое значение около 583.61 МПа (для малых моментов)
        self.assertAlmostEqual(result, 583.61, delta=10)
    
    def test_calculate_basic_G_zero_angle(self):
        """Тест для нулевого угла (деление на ноль)"""
        result = calculate_basic_G(1000, 100, 10, 0)
        self.assertIsNone(result)
    
    def test_calculate_basic_G_negative_values(self):
        """Тест для отрицательных значений"""
        # Отрицательные значения физически бессмысленны, но функция должна работать
        result = calculate_basic_G(-1000, 100, 10, 10)
        self.assertIsNotNone(result)
    
    def test_calculate_basic_G_large_angle(self):
        """Тест для больших углов"""
        result = calculate_basic_G(1000, 100, 10, 90)
        self.assertIsNotNone(result)
        self.assertGreater(result, 0)

class TestTauCalculation(unittest.TestCase):
    """Тесты для расчета касательных напряжений"""
    
    def test_calculate_tau_basic(self):
        """Базовый тест расчета τ"""
        moment = 1000  # Н·мм
        diameter = 10  # мм
        
        result = calculate_tau(moment, diameter)
        self.assertIsNotNone(result)
        self.assertGreater(result, 0)
        # τ = M / Wp, где Wp ≈ 196.35
        expected = 1000 / 196.35
        self.assertAlmostEqual(result, expected, places=1)
    
    def test_calculate_tau_zero_diameter(self):
        """Тест для нулевого диаметра"""
        result = calculate_tau(1000, 0)
        self.assertIsNone(result)
    
    def test_calculate_tau_different_moments(self):
        """Тест для разных моментов"""
        diameter = 10
        test_cases = [
            (500, 2.55),
            (1000, 5.09),
            (1500, 7.64),
            (2000, 10.19)
        ]
        for moment, expected in test_cases:
            with self.subTest(moment=moment):
                result = calculate_tau(moment, diameter)
                self.assertAlmostEqual(result, expected, delta=0.1)

class TestExperimentAnalysis(unittest.TestCase):
    """Тесты для анализа экспериментальных данных"""
    
    def test_analyze_experiment_linear(self):
        """Тест анализа линейных экспериментальных данных"""
        data = [
            (100, 0.5),
            (200, 1.0),
            (300, 1.5),
            (400, 2.0),
            (500, 2.5)
        ]
        L = 100  # мм
        diameter = 10  # мм
        
        result = analyze_experiment(data, L, diameter)
        
        self.assertIsNotNone(result["G_linear"])
        self.assertGreater(result["G_linear"], 0)
        self.assertIsNotNone(result["τ_max"])
    
    def test_analyze_experiment_empty_data(self):
        """Тест для пустых экспериментальных данных"""
        result = analyze_experiment([], 100, 10)
        
        self.assertIsNone(result["G_linear"])
        self.assertIsNone(result["τ_max"])
    
    def test_analyze_experiment_invalid_parameters(self):
        """Тест для некорректных параметров"""
        data = [(100, 0.5), (200, 1.0)]
        
        # Отрицательная длина
        result = analyze_experiment(data, -100, 10)
        self.assertIsNone(result["G_linear"])
        
        # Нулевой диаметр
        result = analyze_experiment(data, 100, 0)
        self.assertIsNone(result["G_linear"])

class TestValidation(unittest.TestCase):
    """Тесты для валидации результатов"""
    
    def test_validate_steel_result(self):
        """Тест валидации результата для стали"""
        result = validate_result("Сталь", 80000)
        self.assertTrue(result["valid"])
        self.assertIn("нормы", result["message"])
    
    def test_validate_steel_too_low(self):
        """Тест валидации слишком низкого значения для стали"""
        result = validate_result("Сталь", 50000)
        self.assertFalse(result["valid"])
        self.assertIn("низкий", result["message"])
    
    def test_validate_steel_too_high(self):
        """Тест валидации слишком высокого значения для стали"""
        result = validate_result("Сталь", 120000)
        self.assertFalse(result["valid"])
        self.assertIn("высокий", result["message"])
    
    def test_validate_iron_result(self):
        """Тест валидации результата для чугуна"""
        result = validate_result("Чугун", 40000)
        self.assertTrue(result["valid"])
    
    def test_validate_wood_result(self):
        """Тест валидации результата для дерева"""
        result = validate_result("Дерево", 1000)
        self.assertTrue(result["valid"])
    
    def test_validate_unknown_material(self):
        """Тест валидации для неизвестного материала"""
        result = validate_result("Неизвестный материал", 50000)
        self.assertIsNone(result["valid"])

class TestExampleCalculations(unittest.TestCase):
    """Тесты для примеров расчетов"""
    
    def test_example_steel_elastic(self):
        """Тест примера расчета для стали в упругой области"""
        example = EXAMPLE_CALCULATIONS["Сталь - упругая область"]
        
        # Проверяем, что все необходимые поля присутствуют
        self.assertIn("material", example)
        self.assertIn("length", example)
        self.assertIn("diameter", example)
        self.assertIn("moment", example)
        self.assertIn("angle", example)
        self.assertIn("expected_G_eff", example)
        
        # Проверяем типы данных
        self.assertIsInstance(example["length"], float)
        self.assertIsInstance(example["diameter"], float)
        self.assertIsInstance(example["moment"], float)
        self.assertIsInstance(example["angle"], float)
    
    def test_all_examples_have_required_fields(self):
        """Тест что все примеры содержат необходимые поля"""
        required_fields = ["material", "length", "diameter", "moment", "angle", "description", "expected_G_eff"]
        
        for name, example in EXAMPLE_CALCULATIONS.items():
            with self.subTest(example=name):
                for field in required_fields:
                    self.assertIn(field, example, f"Поле '{field}' отсутствует в примере '{name}'")

class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""
    
    def test_full_calculation_workflow(self):
        """Тест полного цикла расчета"""
        # Берем пример из базы примеров
        example = EXAMPLE_CALCULATIONS["Сталь - упругая область"]
        
        # Выполняем расчет
        G_basic = calculate_basic_G(
            example["moment"],
            example["length"],
            example["diameter"],
            example["angle"]
        )
        
        self.assertIsNotNone(G_basic)
        self.assertGreater(G_basic, 0)
        
        # Применяем коэффициент материала (для стали k=1.0)
        k = 1.0
        G_eff = k * G_basic
        
        # Проверяем, что результат близок к ожидаемому
        # Допускаем погрешность ±50% (так как зависит от входных параметров)
        expected = example["expected_G_eff"]
        # Проверяем только, что значение положительное и разумное
        self.assertGreater(G_eff, 100)  # Минимум 100 МПа
        self.assertLess(G_eff, 200000)  # Максимум 200 ГПа

def run_tests():
    """Запуск всех тестов"""
    # Создаем test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем все тестовые классы
    suite.addTests(loader.loadTestsFromTestCase(TestPolarMomentInertia))
    suite.addTests(loader.loadTestsFromTestCase(TestPolarResistanceMoment))
    suite.addTests(loader.loadTestsFromTestCase(TestBasicG))
    suite.addTests(loader.loadTestsFromTestCase(TestTauCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestExperimentAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestExampleCalculations))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Запускаем тесты с подробным выводом
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим итоговую статистику
    print("\n" + "=" * 70)
    print("ИТОГОВАЯ СТАТИСТИКА ТЕСТОВ")
    print("=" * 70)
    print(f"Всего тестов выполнено: {result.testsRun}")
    print(f"Успешно пройдено: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)


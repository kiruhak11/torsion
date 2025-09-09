#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления проблем с базой данных
Лабораторная работа №4 - Кручение
Авторы: Коваленко Кирилл, Артем Иокерс, группа ИН-31
"""

from db_manager import reset_database, init_db
import os

def main():
    print("=" * 60)
    print("ИСПРАВЛЕНИЕ БАЗЫ ДАННЫХ")
    print("Лабораторная работа №4")
    print("=" * 60)
    print()
    
    choice = input("Выберите действие:\n"
                  "1. Попробовать исправить существующую БД\n"
                  "2. Полностью пересоздать БД (данные будут потеряны)\n"
                  "Введите номер (1 или 2): ").strip()
    
    if choice == '2':
        confirm = input("\nВнимание! Все сохраненные результаты будут удалены.\n"
                       "Продолжить? (yes/no): ").lower()
        if confirm in ['yes', 'y', 'да', 'д']:
            reset_database()
            print("\n✓ База данных полностью пересоздана")
        else:
            print("Операция отменена")
            return
    else:
        print("\nПопытка исправления существующей базы данных...")
        try:
            init_db()
            print("✓ База данных обновлена")
            
            # Тест базы данных
            from db_manager import get_results
            results = get_results()
            print(f"✓ Тест пройден. Найдено записей: {len(results)}")
            
        except Exception as e:
            print(f"✗ Ошибка: {e}")
            print("Рекомендуется полная пересборка (вариант 2)")
            return
    
    print("\n" + "=" * 60)
    print("Готово! Теперь можно запустить приложение:")
    print("  python main.py")
    print("  или")
    print("  python launch.py")
    print("=" * 60)

if __name__ == "__main__":
    main()

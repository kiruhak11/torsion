@echo off
chcp 65001 >nul
title Лабораторная работа №4 - Кручение

echo ================================================================================
echo ЛАБОРАТОРНАЯ РАБОТА №4
echo Определение модуля упругости второго рода при кручении
echo стали, чугуна, дерева
echo.
echo Автор: Коваленко Кирилл
echo Группа: ИН-31
echo ================================================================================
echo.

echo Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден!
    echo Установите Python с https://python.org
    pause
    exit /b 1
)

echo Установка зависимостей...
pip install -r requirements.txt

echo.
echo Запуск веб-приложения...
echo Откроется браузер на http://localhost:5000
echo Для остановки нажмите Ctrl+C
echo.

python main.py

pause


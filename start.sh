#!/bin/bash

echo "================================================================================"
echo "ЛАБОРАТОРНАЯ РАБОТА №4"
echo "Определение модуля упругости второго рода при кручении"
echo "стали, чугуна, дерева"
echo ""
echo "Автор: Коваленко Кирилл"
echo "Группа: ИН-31"
echo "================================================================================"
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ОШИБКА: Python не найден!"
        echo "Установите Python с https://python.org"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Найден Python: $($PYTHON_CMD --version)"

# Установка зависимостей
echo "Установка зависимостей..."
$PYTHON_CMD -m pip install -r requirements.txt

echo ""
echo "Запуск веб-приложения..."
echo "Откроется браузер автоматически"
echo "Для остановки нажмите Ctrl+C"
echo ""

# Попробуем умный запуск
if [ -f "launch.py" ]; then
    echo "Использую умный запуск с автоматическим поиском порта..."
    $PYTHON_CMD launch.py
else
    echo "Использую стандартный запуск..."
    $PYTHON_CMD main.py
fi

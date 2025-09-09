import sqlite3
import os

DB_PATH = "data/results.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Проверяем существующую структуру таблицы
    cursor.execute("PRAGMA table_info(results)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if not columns:
        # Таблицы нет, создаем новую
        cursor.execute('''
            CREATE TABLE results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material TEXT,
                L REAL,
                diameter REAL,
                moment REAL,
                angle REAL,
                G REAL,
                timestamp TEXT
            )
        ''')
    else:
        # Таблица существует, проверяем и добавляем недостающие колонки
        required_columns = {
            'material': 'TEXT',
            'L': 'REAL', 
            'diameter': 'REAL',
            'moment': 'REAL',
            'angle': 'REAL',
            'G': 'REAL',
            'timestamp': 'TEXT'
        }
        
        for col_name, col_type in required_columns.items():
            if col_name not in columns:
                try:
                    cursor.execute(f'ALTER TABLE results ADD COLUMN {col_name} {col_type}')
                    print(f"✓ Добавлена колонка {col_name}")
                except sqlite3.OperationalError:
                    pass  # Колонка уже существует
    
    conn.commit()
    conn.close()

def insert_result(material, L, diameter, moment, angle, G_eff, timestamp):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO results (material, L, diameter, moment, angle, G, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (material, L, diameter, moment, angle, G_eff, timestamp))
    conn.commit()
    conn.close()

def get_results():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, material, L, diameter, moment, angle, G, timestamp FROM results ORDER BY id DESC')
        rows = cursor.fetchall()
    except sqlite3.OperationalError as e:
        # Если есть проблемы со структурой, пересоздаем таблицу
        print(f"Ошибка базы данных: {e}")
        print("Пересоздание таблицы...")
        cursor.execute('DROP TABLE IF EXISTS results')
        cursor.execute('''
            CREATE TABLE results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material TEXT,
                L REAL,
                diameter REAL,
                moment REAL,
                angle REAL,
                G REAL,
                timestamp TEXT
            )
        ''')
        rows = []
    conn.commit()
    conn.close()
    return rows

def reset_database():
    """Полная пересборка базы данных"""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("✓ Старая база данных удалена")
    init_db()
    print("✓ База данных пересоздана")

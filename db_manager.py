import sqlite3
import os

DB_PATH = "data/results.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
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
    cursor.execute('SELECT id, material, L, diameter, moment, angle, G, timestamp FROM results ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

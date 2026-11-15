import sqlite3, os
DB_PATH = os.path.join('database.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='autolike_targets';")
row = cursor.fetchone()
print(row[0] if row else 'No autolike_targets table')
conn.close()

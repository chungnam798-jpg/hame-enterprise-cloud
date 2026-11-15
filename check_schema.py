import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE name='autolike_targets'")
print(cursor.fetchone()[0])

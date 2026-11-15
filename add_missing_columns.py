import sqlite3, sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE affiliate_clicks ADD COLUMN estimated_commission REAL DEFAULT 0.0")
    conn.commit()
    print("Successfully added missing column estimated_commission!")
except Exception as e:
    print("Column addition result:", e)

conn.close()

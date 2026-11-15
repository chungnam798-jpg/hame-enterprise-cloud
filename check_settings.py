import sqlite3, json

db = 'database.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("SELECT key, value FROM settings WHERE key LIKE '%shopee%' OR key LIKE '%comment%'")
for row in c.fetchall():
    print(f"{row[0]}: {row[1]}")
conn.close()

import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute("PRAGMA table_info(insight_targets)")
print("Columns in insight_targets:")
for row in c.fetchall():
    print(row)

conn.close()

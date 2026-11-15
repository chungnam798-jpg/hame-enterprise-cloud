import sqlite3, sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(bulk_groups)")
print("=== BULK_GROUPS SCHEMA ===")
for col in cursor.fetchall():
    print(col)

conn.close()

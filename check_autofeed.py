import sqlite3, sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('SELECT id, name, status, platform FROM accounts')
accs = cursor.fetchall()
print("=== ACTIVE ACCOUNTS IN DB ===")
for a in accs:
    print(a)

cursor.execute("SELECT key, value FROM settings WHERE key LIKE '%autofeed%'")
stts = cursor.fetchall()
print("\n=== AUTOFEED SETTINGS IN DB ===")
for k, v in stts:
    print(f"{k} -> {v}")

conn.close()

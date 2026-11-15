import sqlite3, sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("UPDATE settings SET value = '' WHERE key = 'autofeed_account_id'")
cursor.execute("UPDATE settings SET value = '1' WHERE key = 'autofeed_engage_enabled'")
conn.commit()

cursor.execute("SELECT key, value FROM settings WHERE key LIKE '%autofeed%'")
print("=== UPDATED AUTOFEED SETTINGS ===")
for k, v in cursor.fetchall():
    print(f"{k} -> {v}")

conn.close()

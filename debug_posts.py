import sqlite3, sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("SELECT id, account_id, status, result_log, scheduled_at FROM posts")
posts = cursor.fetchall()
print(f"=== POSTS LOG CHECK ({len(posts)}) ===")
for p in posts:
    print(f"ID: {p[0]} | Account: {p[1]} | Status: {p[2]} | Sched: {p[4]}")
    if p[3]:
        print(f"   Log: {p[3]}")

cursor.execute("SELECT key, value FROM settings WHERE key LIKE '%autofeed%' OR key LIKE '%engage%'")
print("\n=== AUTOFEED SETTINGS ===")
for s in cursor.fetchall():
    print(f"- {s[0]}: {s[1]}")

conn.close()

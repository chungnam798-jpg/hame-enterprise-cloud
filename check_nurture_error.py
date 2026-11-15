import sqlite3, sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print("=== RECENT ENGAGEMENT LOGS IN DATABASE ===")
try:
    cursor.execute("SELECT id, post_url, commenter_name, comment_content, status, created_at FROM engagement_logs ORDER BY created_at DESC LIMIT 10")
    logs = cursor.fetchall()
    if not logs:
        print("No engagement logs found yet.")
    for l in logs:
        print(l)
except Exception as e:
    print("Error querying engagement_logs:", e)

print("\n=== RECENT SERVER LOGS / SETTINGS ===")
cursor.execute("SELECT key, value FROM settings WHERE key LIKE '%autofeed%'")
for k, v in cursor.fetchall():
    print(f"{k} -> {v}")

conn.close()

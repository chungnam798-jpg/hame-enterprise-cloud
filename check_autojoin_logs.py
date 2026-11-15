import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database.db')
cursor = conn.cursor()
try:
    cursor.execute("SELECT account_id, target_name_or_url, status, details, created_at FROM autojoin_logs ORDER BY created_at DESC LIMIT 50")
    rows = cursor.fetchall()
    print("Autojoin logs in DB:")
    for row in rows:
        print(f"Account: {row[0]} | Target: {row[1]} | Status: {row[2]} | Details: {row[3]} | Time: {row[4]}")
except Exception as e:
    print(f"Error checking logs: {e}")
conn.close()

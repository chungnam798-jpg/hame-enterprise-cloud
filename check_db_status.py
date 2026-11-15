import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database.db')

cursor = conn.cursor()

print("=== ACCOUNTS TABLE SUMMARY ===")
cursor.execute("SELECT id, name, platform, status, LENGTH(cookie) FROM accounts")
accounts = cursor.fetchall()
for acc in accounts:
    print(f"Account ID: {acc[0]} | Name: {acc[1]} | Status: {acc[3]} | Cookie Length: {acc[4]}")

print("\n=== POSTS TABLE STATUS BREAKDOWN ===")
cursor.execute("SELECT status, COUNT(*) FROM posts GROUP BY status")
print(cursor.fetchall())

print("\n=== UNASSIGNED POSTS (NULL / EMPTY ACCOUNT_ID) ===")
cursor.execute("SELECT COUNT(*) FROM posts WHERE account_id IS NULL OR account_id = ''")
print("Null Account ID Count:", cursor.fetchone()[0])

print("\n=== FAILED POSTS SAMPLE ===")
cursor.execute("SELECT id, account_id, content, status FROM posts WHERE status = 'failed' LIMIT 5")
failed_sample = cursor.fetchall()
for f in failed_sample:
    print(f)

conn.close()

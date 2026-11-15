import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("DELETE FROM posts WHERE id IN (SELECT id FROM posts ORDER BY created_at DESC LIMIT 10)")
deleted = cursor.rowcount

conn.commit()
conn.close()

print(f"Deleted {deleted} posts.")

import sqlite3
import json

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute("SELECT id, content, created_at, status FROM posts WHERE status IN ('posted', 'commented') ORDER BY created_at DESC LIMIT 5")
rows = c.fetchall()

if rows:
    print("Recent completed posts/comments:")
    for row in rows:
        print(f"- ID: {row[0]} | Time: {row[2]} | Status: {row[3]}\n  Content: {row[1][:100]}...\n")
else:
    print("No recent completed posts found in the DB.")
    
conn.close()

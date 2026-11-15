import sqlite3, json, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
posts = [dict(r) for r in conn.execute("SELECT id, status, type, target_id FROM posts WHERE status IN ('published', 'success') ORDER BY created_at DESC LIMIT 5").fetchall()]
print(json.dumps(posts, ensure_ascii=False, indent=2))

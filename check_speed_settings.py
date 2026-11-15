import sqlite3, json

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
settings = [dict(r) for r in conn.execute("SELECT key, value FROM settings WHERE key LIKE '%interval%' OR key LIKE '%max%' OR key LIKE '%speed%'").fetchall()]
print(json.dumps(settings, indent=2))

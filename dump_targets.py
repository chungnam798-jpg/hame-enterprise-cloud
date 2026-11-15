import sqlite3
import json

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
lists = [dict(r) for r in conn.execute('SELECT id, name FROM target_lists').fetchall()]

with open('temp_targets.txt', 'w', encoding='utf-8') as f:
    f.write(json.dumps(lists, ensure_ascii=False, indent=2))

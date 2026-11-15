import sqlite3
import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute("SELECT key, value FROM settings WHERE key LIKE '%insight%' OR key LIKE '%keyword%' OR key LIKE '%comment%'")
rows = c.fetchall()
print(json.dumps(rows, ensure_ascii=False, indent=2))
conn.close()

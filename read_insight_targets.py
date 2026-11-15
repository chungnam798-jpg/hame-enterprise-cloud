import sqlite3
import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute("SELECT * FROM insight_targets")
targets = c.fetchall()

print(json.dumps(targets, ensure_ascii=False, indent=2))
conn.close()

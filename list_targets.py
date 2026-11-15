import sqlite3
import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Xem toàn bộ các nhóm còn lại trong insight_targets
c.execute("SELECT id, target_name, niche_keywords, status FROM insight_targets")
rows = c.fetchall()
print(f"Total insight targets: {len(rows)}")
for r in rows:
    print(f"  [{r[3]}] {r[1]} | {r[2]}")

conn.close()

import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print("Tables:", [t[0] for t in tables])

if ('insight_targets',) in tables:
    c.execute("SELECT * FROM insight_targets")
    print("Insight Targets:", c.fetchall())

conn.close()

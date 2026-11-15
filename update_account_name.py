import sqlite3, json

db = 'database.db'
conn = sqlite3.connect(db)
c = conn.cursor()

c.execute("SELECT id, name FROM accounts")
accounts = c.fetchall()
print("Current accounts:", accounts)

# Update name
for acc in accounts:
    if "shope" in acc[1].lower():
        new_name = acc[1].replace("shope lite", "Lolishop").replace("shope", "Lolishop")
        c.execute("UPDATE accounts SET name=? WHERE id=?", (new_name, acc[0]))
        print(f"Updated {acc[1]} to {new_name}")

conn.commit()
conn.close()

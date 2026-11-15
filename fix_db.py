import sqlite3
import database

def fix_db():
    accs = database.get_accounts()
    if not accs:
        print("No accounts")
        return
    acc_id = accs[0]['id']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE autolike_targets SET account_id = ?", (acc_id,))
    cursor.execute("UPDATE posts SET account_id = ?", (acc_id,))
    conn.commit()
    conn.close()
    print("Migrated all to", acc_id)

if __name__ == "__main__":
    fix_db()

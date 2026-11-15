import sqlite3, uuid, sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

acc_id = 'acc_' + str(uuid.uuid4())[:8]
now_str = datetime.now().isoformat()
cursor.execute(
    "INSERT INTO accounts (id, name, cookie, status, team_role, platform, created_at, updated_at) VALUES (?, ?, '', 'active', 'team_poster', 'facebook', ?, ?)",
    (acc_id, 'Minh Thư - Sneaker Deals', now_str, now_str)
)
conn.commit()
print("SUCCESSFULLY REGISTERED ACCOUNT: Minh Thư - Sneaker Deals")

cursor.execute("SELECT id, name, team_role FROM accounts")
all_accs = cursor.fetchall()
print("\n=== TOTAL ACCOUNTS NOW IN SYSTEM:", len(all_accs), "===")
for idx, a in enumerate(all_accs, 1):
    print(f"{idx}. {a[1]} (Role: {a[2]})")

conn.close()

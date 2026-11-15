import sqlite3, uuid, sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Get all accounts currently in DB
cursor.execute("SELECT id, name, team_role FROM accounts")
accs = cursor.fetchall()
print(f"=== CURRENT ACCOUNTS IN DB ({len(accs)}) ===")
for a in accs:
    print(f"- {a[1]} | Current Role: {a[2]}")

# Restructure 10 accounts role assignment
squad_10_roles = {
    # Team 1: Profile VIP (2 Nicks)
    'Nguyễn Hồng Nhung': 'team_profile',
    'Trần Mai Anh': 'team_profile',
    
    # Team 2: Flash Sale Poster (5 Nicks)
    'LoliShop': 'team_poster',
    'Chung Nam': 'team_poster',
    'Thanh Hằng': 'team_poster',
    'Ngọc Trinh': 'team_poster',
    'Hoàng Yến': 'team_poster',
    
    # Team 3: Seeding Tương Tác (3 Nicks)
    'Minh Thư': 'team_seeding',
    'Phạm Khánh Linh': 'team_seeding',
    'Quỳnh Trang': 'team_seeding'
}

print("\n=== RESTRUCTURING 10-ACCOUNT SQUAD MATRIX ===")
for a_id, a_name, a_role in accs:
    new_role = 'team_poster'
    for key_name, target_role in squad_10_roles.items():
        if key_name.lower() in a_name.lower():
            new_role = target_role
            break
    cursor.execute("UPDATE accounts SET team_role = ? WHERE id = ?", (new_role, a_id))
    print(f"Updated: {a_name} ➔ New Squad Role: {new_role}")

# Enable AutoFeed / Nurturing for all 10 accounts
cursor.execute("UPDATE settings SET value = '1' WHERE key = 'autofeed_engage_enabled'")
cursor.execute("UPDATE settings SET value = '' WHERE key = 'autofeed_account_id'")
cursor.execute("UPDATE settings SET value = '3' WHERE key = 'autofeed_engage_interval_minutes'")

conn.commit()
print("\n=== 10-ACCOUNT CAMPAIGN SUCCESSFULLY CONFIGURED & ACTIVATED! ===")

conn.close()

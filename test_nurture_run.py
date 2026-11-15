import sys, sqlite3
sys.stdout.reconfigure(encoding='utf-8')

import database
from automation import auto_engage_feed_posts

print("=== STARTING DIRECT TEST OF AUTOFEED NURTURE ===")
accounts = [a for a in database.get_accounts() if a['status'] == 'active']

print(f"Found {len(accounts)} active accounts in DB:")
for a in accounts:
    print(f"- ID: {a['id']}, Name: {a['name']}, Cookie Length: {len(a.get('cookie','')) if a.get('cookie') else 0}")

if not accounts:
    print("NO ACTIVE ACCOUNTS FOUND!")
else:
    test_acc = accounts[0]
    print(f"\n--- Testing Auto-Engage for: {test_acc['name']} ---")
    res = auto_engage_feed_posts(
        account_cookie=test_acc['cookie'],
        account_name=test_acc['name'],
        source='groups',
        max_posts=2,
        comment_style='AI',
        comment_text=''
    )
    print("RESULT:", res)

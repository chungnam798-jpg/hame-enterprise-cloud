import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
import automation
import database
import random

def do_auto_fetch():
    accounts = [a for a in database.get_accounts() if a['status'] == 'active']
    if not accounts:
        print("No active accounts.")
        return
        
    acc = random.choice(accounts)
    print("Fetching joined groups...")
    res = automation.auto_fetch_joined_groups(acc['cookie'], limit=10)
    
    if res.get('success') and res.get('data'):
        groups = res['data']
        added = 0
        for g in groups:
            if database.save_insight_target(None, g['target_url'], g['target_name'], 'Sản phẩm/Dịch vụ phù hợp với chủ đề nhóm'):
                added += 1
        print(f"Added {added} groups automatically.")
    else:
        print("Failed:", res.get('log'))

if __name__ == '__main__':
    do_auto_fetch()

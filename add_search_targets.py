import sqlite3
import uuid
import datetime
import urllib.parse

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

account_id = 'acc_2ba0dc55' # shope lite

keywords = [
    "thanh lý quần áo",
    "review mỹ phẩm", 
    "săn sale shopee",
    "góc bóc phốt",
    "tâm sự mẹ bỉm sữa"
]

for kw in keywords:
    tid = 'tgt_' + str(uuid.uuid4())[:8]
    now = datetime.datetime.now().isoformat()
    encoded_kw = urllib.parse.quote(kw)
    target_url = f"https://www.facebook.com/search/posts/?q={encoded_kw}"
    
    cursor.execute("""
        INSERT INTO autolike_targets 
        (id, account_id, target_url, target_name, status, created_at, auto_comment, comment_style, comment_text) 
        VALUES (?, ?, ?, ?, 'active', ?, 1, 'AI', ?)
    """, (tid, account_id, target_url, f"Tìm kiếm: {kw}", now, 'Ghé shopee của mình nhé!'))

conn.commit()
conn.close()
print("Search targets added successfully.")

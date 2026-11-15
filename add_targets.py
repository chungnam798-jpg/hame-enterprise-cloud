import sqlite3
import uuid
import datetime

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

account_id = 'acc_2ba0dc55' # shope lite

targets = [
    {"url": "https://www.facebook.com/tranthanhne", "name": "Trấn Thành"},
    {"url": "https://www.facebook.com/MTP.Fan", "name": "Sơn Tùng M-TP"},
    {"url": "https://www.facebook.com/Theanh28", "name": "Theanh28 Entertainment"},
    {"url": "https://www.facebook.com/khongsocho.official", "name": "Không Sợ Chó"},
    {"url": "https://www.facebook.com/mytam.info", "name": "Mỹ Tâm"}
]

for t in targets:
    tid = 'tgt_' + str(uuid.uuid4())[:8]
    now = datetime.datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO autolike_targets 
        (id, account_id, target_url, target_name, status, created_at, auto_comment, comment_style, comment_text) 
        VALUES (?, ?, ?, ?, 'active', ?, 1, 'AI', ?)
    """, (tid, account_id, t['url'], t['name'], now, 'Nhớ ghé thăm shopee/trang cá nhân của mình nhé!'))

conn.commit()
conn.close()
print("Targets added successfully.")

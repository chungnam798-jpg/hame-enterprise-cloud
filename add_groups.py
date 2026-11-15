import sqlite3, uuid, datetime, os

groups = [
    "https://www.facebook.com/groups/5052276618187512"
]

db_path = 'database.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get the first active account to assign
c.execute("SELECT id FROM accounts WHERE status='active' LIMIT 1")
acc = c.fetchone()
account_id = acc[0] if acc else 'all'

now = datetime.datetime.now().isoformat()
comment_text = "💬 {emoji} {product_name} đang cực hot ở {group_name}! Xem ngay tại {link} Lolishop"

for url in set(groups):
    # Check if exists
    c.execute("SELECT id FROM autolike_targets WHERE target_url=?", (url,))
    if c.fetchone():
        print(f"Group already exists: {url}")
        continue
    
    target_id = f"target_{uuid.uuid4().hex[:8]}"
    name = url.split('/')[-1]
    
    try:
        c.execute("""
            INSERT INTO autolike_targets 
            (id, account_id, target_url, target_name, status, created_at, auto_comment, comment_style, comment_text, cross_comment_enabled)
            VALUES (?, ?, ?, ?, 'active', ?, 1, 'AI', ?, 1)
        """, (target_id, account_id, url, name, now, comment_text))
        print(f"Added group: {url}")
    except Exception as e:
        print(f"Error adding {url}: {e}")

conn.commit()
conn.close()
print("Done adding groups.")

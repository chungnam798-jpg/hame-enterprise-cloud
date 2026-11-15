import sqlite3
import sys

# Fix encoding issue
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Delete pending posts that have old shopee templates
c.execute("DELETE FROM posts WHERE status='pending' AND content LIKE '%Shopee%'")
c.execute("DELETE FROM posts WHERE status='pending' AND content LIKE '%shopee%'")
deleted = c.rowcount

c.execute("SELECT id, content, created_at, status FROM posts WHERE status IN ('posted', 'commented') ORDER BY created_at DESC LIMIT 5")
rows = c.fetchall()

if rows:
    print("Các bình luận/bài viết mới nhất vừa thực hiện:")
    for row in rows:
        print(f"✅ ID: {row[0]} | Lúc: {row[2]}\n   Nội dung: {row[1][:150]}...")
else:
    print("Chưa có bình luận mới nào hoàn thành.")
    
print(f"\nĐã dọn dẹp {deleted} bài đăng chờ cũ chứa từ Shopee.")
conn.commit()
conn.close()

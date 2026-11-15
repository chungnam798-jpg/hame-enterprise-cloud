import sqlite3
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Reset last_run for insight_targets to force it to scan again
c.execute("UPDATE insight_targets SET last_run = NULL")
print(f"Đã reset thời gian quét của {c.rowcount} nhóm.")

# Xóa bớt lịch sử đã quét để bot quét lại các bài gần đây
c.execute("DELETE FROM scanned_posts")
print(f"Đã xóa {c.rowcount} lịch sử bài viết đã quét.")

conn.commit()
conn.close()
print("Sẵn sàng! Bot sẽ lập tức quét lại các bài viết mới nhất trong nhóm.")

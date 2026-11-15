import sqlite3
import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Kiểm tra telegram settings
c.execute("SELECT key, value FROM settings WHERE key IN ('telegram_token', 'telegram_chat_id', 'bait_bio_link', 'gemini_api_key')")
rows = c.fetchall()
for r in rows:
    val = r[1][:30] + '...' if r[1] and len(r[1]) > 30 else r[1]
    print(f"{r[0]}: {val}")

print("\n--- XÓA CÁC NHÓM KHÔNG PHẢI THỜI TRANG TÚI XÁCH ---")

# Chỉ xóa các nhóm không liên quan đến thời trang
c.execute("""
    DELETE FROM insight_targets 
    WHERE niche_keywords NOT LIKE '%thời trang%' 
      AND niche_keywords NOT LIKE '%túi xách%' 
      AND niche_keywords NOT LIKE '%streetwear%'
      AND niche_keywords NOT LIKE '%phối đồ%'
""")
deleted = c.rowcount
print(f"Đã xóa {deleted} nhóm không liên quan")

# Cũng xóa bảng tin và tìm kiếm toàn cầu (quét lãng phí)
c.execute("DELETE FROM insight_targets WHERE target_name LIKE '%Bảng Tin%' OR target_name LIKE '%Newsfeed%' OR target_name LIKE '%Tìm kiếm Toàn Facebook%'")
deleted2 = c.rowcount
print(f"Đã xóa {deleted2} nhóm tìm kiếm toàn cầu")

conn.commit()

# Xem danh sách còn lại
c.execute("SELECT target_name, niche_keywords FROM insight_targets")
rows = c.fetchall()
print(f"\nCòn lại {len(rows)} nhóm thời trang túi xách:")
for r in rows:
    print(f"  ✅ {r[0]} | {r[1]}")

conn.close()

import sqlite3
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Bật auto_comment cho TẤT CẢ các nhóm chéo tương tác (cross-engagement groups)
# Nhận ra các nhóm chéo theo pattern tên
c.execute("""
    UPDATE autolike_targets
    SET auto_comment = 1, comment_style = 'AI'
    WHERE target_url LIKE '%cheofollowuytin05%'
       OR target_url LIKE '%cheofollowcheolike%'
       OR target_url LIKE '%3498824993681205%'
       OR target_url LIKE '%327670525543455%'
       OR target_url LIKE '%585963052781600%'
       OR target_url LIKE '%224626875310705%'
       OR target_url LIKE '%730185894673464%'
       OR target_url LIKE '%1167853450254147%'
       OR target_url LIKE '%158992923718361%'
       OR target_url LIKE '%5052276618187512%'
       OR target_name LIKE '%chéo%'
       OR target_name LIKE '%Chéo%'
       OR id LIKE 'cheo_%'
""")
updated = c.rowcount
print(f"Đã bật auto_comment cho {updated} nhóm chéo tương tác")

# Xóa duplicate trong insight_targets
c.execute("""
    DELETE FROM insight_targets
    WHERE id NOT IN (
        SELECT MIN(id) FROM insight_targets GROUP BY target_url
    )
""")
deleted = c.rowcount
print(f"Đã xóa {deleted} bản ghi insight_targets trùng lặp")

conn.commit()

# Tóm tắt
print("\n📊 PHÂN CHIA NHIỆM VỤ HAI BOT:")
print("=" * 60)
print("🤖 BOT 1 - TƯƠNG TÁC CHÉO (autolike_targets, auto_comment=1):")
c.execute("SELECT DISTINCT target_name, target_url FROM autolike_targets WHERE auto_comment=1 AND status='active' ORDER BY target_name")
rows = c.fetchall()
for r in rows[:15]:
    print(f"   💬 {r[0]}")
if len(rows) > 15:
    print(f"   ... và {len(rows)-15} nhóm khác")

print(f"\n🤖 BOT 2 - QUÉT TIỀM NĂNG TÚI XÁCH (insight_targets):")
c.execute("SELECT DISTINCT target_name, niche_keywords FROM insight_targets WHERE status='active'")
rows = c.fetchall()
for r in rows:
    print(f"   🎯 {r[0]} | [{r[1]}]")

conn.close()

import sqlite3
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Danh sách nhóm chéo tương tác (cross-engagement groups)
cross_groups = [
    # Chéo Follow/Like đã thêm trước đây
    ("cheo_1", "acc_2ba0dc55", "https://www.facebook.com/groups/cheofollowuytin05", "Chéo Follow Uy Tín 05", "active", 1, "AI", ""),
    ("cheo_2", "acc_2ba0dc55", "https://www.facebook.com/groups/cheofollowcheolike", "Chéo Follow Chéo Like", "active", 1, "AI", ""),
    ("cheo_3", "acc_2ba0dc55", "https://www.facebook.com/groups/3498824993681205", "Nhóm Chéo Tương Tác 1", "active", 1, "AI", ""),
    ("cheo_4", "acc_2ba0dc55", "https://www.facebook.com/groups/327670525543455", "Nhóm Chéo Tương Tác 2", "active", 1, "AI", ""),
    ("cheo_5", "acc_2ba0dc55", "https://www.facebook.com/groups/585963052781600", "Nhóm Chéo Tương Tác 3", "active", 1, "AI", ""),
    ("cheo_6", "acc_2ba0dc55", "https://www.facebook.com/groups/224626875310705", "Nhóm Chéo Tương Tác 4", "active", 1, "AI", ""),
    ("cheo_7", "acc_2ba0dc55", "https://www.facebook.com/groups/730185894673464", "Nhóm Chéo Tương Tác 5", "active", 1, "AI", ""),
    ("cheo_8", "acc_2ba0dc55", "https://www.facebook.com/groups/1167853450254147", "Nhóm Chéo Tương Tác 6", "active", 1, "AI", ""),
    ("cheo_9", "acc_2ba0dc55", "https://www.facebook.com/groups/158992923718361", "Nhóm Chéo Follow 158", "active", 1, "AI", ""),
    ("cheo_10", "acc_2ba0dc55", "https://www.facebook.com/groups/5052276618187512", "Nhóm Chéo Follow 505", "active", 1, "AI", ""),
]

for row in cross_groups:
    c.execute("""
        INSERT OR IGNORE INTO autolike_targets
        (id, account_id, target_url, target_name, status, auto_comment, comment_style, comment_text, cross_comment_enabled)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, row)

print(f"Đã đảm bảo {len(cross_groups)} nhóm chéo tương tác trong autolike_targets")

# Đảm bảo 3 nhóm thời trang túi xách trong insight_targets
fashion_groups = [
    ("ins_fashion_1", "https://www.facebook.com/groups/hoimepassdo", "Hội Mê Pass Đồ Thời Trang", "túi xách, thời trang, quần áo, váy", "active"),
    ("ins_fashion_2", "https://www.facebook.com/groups/macdepmoingay", "Mặc Đẹp Mỗi Ngày - Phối Đồ", "túi xách, phối đồ, thời trang, quần áo", "active"),
    ("ins_fashion_3", "https://www.facebook.com/groups/vssg.official", "Vietnam Street Style Group", "túi xách, streetwear, thời trang, phụ kiện", "active"),
    ("ins_fashion_4", "https://www.facebook.com/groups/hoiyeuphukien", "Hội Yêu Phụ Kiện Thời Trang", "túi xách, phụ kiện, đồng hồ, thời trang nữ", "active"),
]

for row in fashion_groups:
    c.execute("""
        INSERT OR IGNORE INTO insight_targets
        (id, target_url, target_name, niche_keywords, status, created_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, row)

# Xóa sạch các nhóm không liên quan túi xách khỏi insight_targets
c.execute("""
    DELETE FROM insight_targets 
    WHERE niche_keywords NOT LIKE '%túi xách%'
      AND niche_keywords NOT LIKE '%thời trang%'
      AND niche_keywords NOT LIKE '%streetwear%'
""")
deleted = c.rowcount

conn.commit()

# Kiểm tra kết quả
print("\n=== BOT 1: CHÉO TƯƠNG TÁC (autolike_targets) ===")
c.execute("SELECT target_name, auto_comment FROM autolike_targets WHERE status='active' ORDER BY target_name")
for r in c.fetchall():
    print(f"  💬 {r[0]} | auto_comment={r[1]}")

print("\n=== BOT 2: QUÉT TIỀM NĂNG (insight_targets) ===")
c.execute("SELECT target_name, niche_keywords FROM insight_targets WHERE status='active'")
for r in c.fetchall():
    print(f"  🎯 {r[0]} | {r[1]}")

conn.close()
print(f"\nĐã xóa {deleted} nhóm không liên quan khỏi insight_targets")

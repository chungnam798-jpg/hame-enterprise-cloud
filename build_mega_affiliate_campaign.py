import sqlite3, uuid, sys
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print("==================================================")
print("🚀 MEGA AFFILIATE REVENUE CAMPAIGN ENGINE (V29.0)")
print("==================================================")

# 1. Clean up old failed/draft posts from previous tests
cursor.execute("DELETE FROM posts WHERE status IN ('failed', 'draft', 'pending')")

# 2. Get active accounts by role
cursor.execute("SELECT id, name, team_role FROM accounts WHERE status = 'active'")
accounts = cursor.fetchall()

posters = [a for a in accounts if a[2] == 'team_poster']
seeders = [a for a in accounts if a[2] == 'team_seeding']
profiles = [a for a in accounts if a[2] == 'team_profile']

print(f"\n1. Active Squad Matrix Count: {len(accounts)} Accounts")
print(f"   • Team Posters: {len(posters)} Nicks")
print(f"   • Team Seeders: {len(seeders)} Nicks")
print(f"   • Team Profiles VIP: {len(profiles)} Nicks")

# 3. High-Converting Product Deal Matrix (Shopee & Lazada Dual Affiliate)
campaign_deals = [
    {
        'title': '🔥 [XẢ KHO FLASH SALE 60%] Balo Laptop Chống Nước Nam Nữ LoliShop Cao Cấp!\nChất liệu vải Oxford chống thấm nước tuyệt đối, ngăn chứa 15.6 inch rộng rãi.',
        'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F123456%2F789012&affiliate_id=783489745',
        'first_comment': '👉 Mọi người nhấp trực tiếp vào link ShopeeMall gian hàng chính hãng LoliShop ở đây nhé: https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F123456%2F789012&affiliate_id=783489745',
        'target_name': 'Hội Săn Sale Balo Túi Xách & Phụ Kiện'
    },
    {
        'title': '🎧 BALO LAPTOP GAMING NỮ & TAI NGHE BLUETOOTH GIẢM 50% HÔM NAY!\nThiết kế trẻ trung năng động, mút đệm lưng thoáng khí chống đau vai.',
        'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F234567%2F890123&affiliate_id=783489745',
        'first_comment': '👉 Anh em săn balo laptop/tai nghe gaming chính hãng giảm 50% ở đây nha: https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F234567%2F890123&affiliate_id=783489745',
        'target_name': 'Cộng Đồng Balo Phụ Kiện Nam & Công Nghệ'
    },
    {
        'title': '⚡ MÃ GIẢM SỐC 50K + FREESHIP 0Đ TOÀN SÀN SHOPEE/LAZADA THÁNG NÀY!\nTổng hợp toàn bộ voucher giảm sâu nhất hôm nay cho anh chị em mua sắm.',
        'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F345678%2F901234&affiliate_id=783489745',
        'first_comment': '👉 Link áp mã giảm 50k freeship nhanh kẻo hết lượt nha cả nhà: https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F345678%2F901234&affiliate_id=783489745',
        'target_name': 'Hội Săn Sale Deals Sốc Shopee Lazada 24/7'
    },
    {
        'title': '🛒 THỎA THÍCH SẮN PASS ĐỒ GIA DỤNG & ĐỒ DÙNG GIÁ GỐC THANH LÝ CƯ DÂN!\nBộ hộp thực phẩm giữ nhiệt & đồ tiện ích gia đình cao cấp.',
        'aff_url': 'https://s.lazada.vn/s.12345?custom_id=201037552823',
        'first_comment': '👉 Link mua bộ gia dụng chính hãng Lazada Mall thanh lý ở đây ạ: https://s.lazada.vn/s.12345?custom_id=201037552823',
        'target_name': 'Chợ Cư Dân Mua Bán Chung Cư Hà Nội - TP.HCM'
    },
    {
        'title': '👗 XẢ KHO LÔ ĐẦM THIẾT KẾ ĐẸP MÊ LY CHƯA TỚI 1XX MẶC TÔN DÁNG!\nForm dáng chuẩn, chất vải dày dặn mềm mịn không nhăn xù.',
        'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F456789%2F012345&affiliate_id=783489745',
        'first_comment': '👉 Chị em ghé gian hàng săn mã đầm đẹp ở đây nè: https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F456789%2F012345&affiliate_id=783489745',
        'target_name': 'Hội Mặc Đẹp Mỗi Ngày & Pass Đồ Thời Trang'
    }
]

# 4. Schedule Posts Spaced Every 15 Minutes across Posters
print("\n2. Launching Mega Campaign Posting Schedule:")
now = datetime.now()

for idx, deal in enumerate(campaign_deals):
    poster_acc = posters[idx % len(posters)]
    sched_time = (now + timedelta(minutes=15 * (idx + 1))).isoformat()
    now_str = now.isoformat()
    
    post_id = 'mega_' + str(uuid.uuid4())[:8]
    content = f"{deal['title']}\n\n🛒 Mua ngay tại: {deal['aff_url']}"
    
    cursor.execute(
        """INSERT INTO posts (
            id, account_id, type, target_id, content, media, scheduled_at, status, 
            created_at, updated_at, platform, first_comment, is_bait_post
        ) VALUES (?, ?, 'profile', 'me', ?, '[]', ?, 'pending', ?, ?, 'facebook', ?, 0)""",
        (post_id, poster_acc[0], content, sched_time, now_str, now_str, deal['first_comment'])
    )
    print(f"   ✅ [Lịch {sched_time[11:16]}] Poster: {poster_acc[1]} | Deal: {deal['target_name']}")

# 5. Enable AutoFeed Nurturing & Engagement Engine
cursor.execute("UPDATE settings SET value = '1' WHERE key = 'autofeed_engage_enabled'")
cursor.execute("UPDATE settings SET value = '' WHERE key = 'autofeed_account_id'")
cursor.execute("UPDATE settings SET value = '3' WHERE key = 'autofeed_engage_interval_minutes'")

conn.commit()
conn.close()

print("\n==================================================")
print("🚀 MEGA REVENUE CAMPAIGN FULLY SCHEDULED & RUNNING!")
print("==================================================")

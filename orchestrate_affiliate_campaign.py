import sqlite3, uuid, sys
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print("==================================================")
print("🔍 SYSTEM AUDIT & AFFILIATE REVENUE CAMPAIGN LAUNCH")
print("==================================================")

# 1. Inspect Accounts
cursor.execute("SELECT id, name, team_role, status FROM accounts WHERE status = 'active'")
active_accs = cursor.fetchall()
print(f"\n1. Active Accounts Count: {len(active_accs)}")
for idx, a in enumerate(active_accs, 1):
    print(f"   {idx}. [{a[2]}] {a[1]}")

# 2. Inspect Affiliate Cookies
cursor.execute("SELECT key, value FROM settings WHERE key IN ('shopee_affiliate_id', 'lazada_affiliate_id', 'autofeed_engage_enabled')")
settings = dict(cursor.fetchall())
print(f"\n2. Affiliate Settings Check:")
print(f"   • Shopee Affiliate ID: {settings.get('shopee_affiliate_id', 'MISSING')}")
print(f"   • Lazada Affiliate ID: {settings.get('lazada_affiliate_id', 'MISSING')}")
print(f"   • AutoFeed Nurturing Enabled: {settings.get('autofeed_engage_enabled', '0')}")

# 3. Sample High-Converting Affiliate Deals
deals = [
    {
        'title': '🔥 [FLASH SALE 60%] Balo Laptop Chống Nước Nam Nữ LoliShop Cao Cấp',
        'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F123456%2F789012&affiliate_id=783489745',
        'target_group': 'Hội Săn Sale Balo Túi Xách & Phụ Kiện',
        'poster': 'LoliShop',
        'first_comment': '👉 Mọi người nhấp trực tiếp vào link ShopeeMall gian hàng chính hãng LoliShop ở đây nha: https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F123456%2F789012&affiliate_id=783489745'
    },
    {
        'title': '🎧 Balo Chống Nước Laptop 15.6 Inch & Tai Nghe Gaming Nam Sale 50%',
        'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F234567%2F890123&affiliate_id=783489745',
        'target_group': 'Cộng Đồng Balo Phụ Kiện Nam & Công Nghệ',
        'poster': 'Chung Nam',
        'first_comment': '👉 Anh em săn deal balo laptop chống nước ở đây nha: https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F234567%2F890123&affiliate_id=783489745'
    },
    {
        'title': '⚡ MÃ GIẢM SỐC 50K + FREESHIP 0Đ TOÀN SÀN SHOPEE/LAZADA HÔM NAY',
        'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F345678%2F901234&affiliate_id=783489745',
        'target_group': 'Hội Săn Sale Deals Sốc Shopee Lazada 24/7',
        'poster': 'Thanh Hằng - Poster Shopee Deal Sốc',
        'first_comment': '👉 Link áp mã giảm 50k freeship nhanh không hết mã nha cả nhà: https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F345678%2F901234&affiliate_id=783489745'
    },
    {
        'title': '🛒 BỘ DỤNG CỤ THÔNG MINH GIA DỤNG THANH LÝ GIÁ GỐC DÀNH CHO CƯ DÂN',
        'aff_url': 'https://s.lazada.vn/s.12345?custom_id=201037552823',
        'target_group': 'Chợ Cư Dân Mua Bán Chung Cư Hà Nội - TP.HCM',
        'poster': 'Ngọc Trinh - Poster Chợ Cư Dân',
        'first_comment': '👉 Link mua bộ gia dụng chính hãng Lazada Mall ở đây ạ: https://s.lazada.vn/s.12345?custom_id=201037552823'
    },
    {
        'title': '👗 XẢ KHO LÔ ĐẦM THIẾT KẾ ĐẸP MÊ LY CHƯA TỚI 1XX MẶC TÔN DÁNG',
        'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F456789%2F012345&affiliate_id=783489745',
        'target_group': 'Hội Mặc Đẹp Mỗi Ngày & Pass Đồ Thời Trang',
        'poster': 'Hoàng Yến - Poster Fashion Sale',
        'first_comment': '👉 Chị em ghé gian hàng săn mã đầm đẹp ở đây nè: https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F456789%2F012345&affiliate_id=783489745'
    }
]

# 4. Schedule Automated Campaign Posts Across 24 Hours
cursor.execute("DELETE FROM posts WHERE status = 'pending'")

now = datetime.now()
print("\n3. Automated Campaign Schedule Dispatch:")

for idx, deal in enumerate(deals):
    post_time = (now + timedelta(minutes=20 * (idx + 1))).isoformat()
    now_str = now.isoformat()
    
    # Find account ID
    cursor.execute("SELECT id FROM accounts WHERE name LIKE ?", (f"%{deal['poster']}%",))
    acc_row = cursor.fetchone()
    account_id = acc_row[0] if acc_row else 'acc_a2c6d4d1'
    
    post_id = 'post_' + str(uuid.uuid4())[:8]
    content = deal['title']
    
    cursor.execute(
        """INSERT INTO posts (
            id, account_id, type, target_id, content, media, scheduled_at, status, 
            created_at, updated_at, platform, first_comment, is_bait_post
        ) VALUES (?, ?, 'group', ?, ?, '[]', ?, 'pending', ?, ?, 'facebook', ?, 0)""",
        (post_id, account_id, deal['target_group'], content, post_time, now_str, now_str, deal['first_comment'])
    )
    print(f"   ✅ [Lịch {post_time[:19]}] Poster: {deal['poster']} | Nhóm: {deal['target_group']}")

# 5. Ensure AutoFeed settings are optimal
cursor.execute("UPDATE settings SET value = '1' WHERE key = 'autofeed_engage_enabled'")
cursor.execute("UPDATE settings SET value = '' WHERE key = 'autofeed_account_id'")
cursor.execute("UPDATE settings SET value = '3' WHERE key = 'autofeed_engage_interval_minutes'")

conn.commit()
conn.close()

print("\n==================================================")
print("🚀 AFFILIATE REVENUE CAMPAIGN FULLY SCHEDULED & LIVE!")
print("==================================================")

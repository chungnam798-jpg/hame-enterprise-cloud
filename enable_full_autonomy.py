import sqlite3, sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print("=================================================================")
print("🤖 KÍCH HOẠT HỆ THỐNG TỰ ĐỘNG THỰC THI CHUYÊN SÂU 100% (FULL AUTONOMY)")
print("=================================================================")

# Enable all background auto-execution flags
settings_to_update = {
    'autofeed_engage_enabled': '1',
    'autofeed_account_id': '',  # All active accounts
    'autofeed_engage_interval_minutes': '15',
    'engage_speed_mode': 'turbo',
    'autofeed_max_posts_per_scan': '30',
    'autojoin_enabled': '1',
    'auto_reply_messenger_enabled': '1',
    'shopee_auto_post_enabled': '1',
    'shopee_poster_type': 'profile',
    'shopee_poster_target_id': 'me',
    'shopee_auto_comment_link': '1'
}

for key, val in settings_to_update.items():
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, val))

conn.commit()

print("✅ Đã bật chế độ TỰ ĐỘNG THỰC THI TOÀN DIỆN:")
print("   1. Tự động bật Trình duyệt ảo ngầm (Headless/Background Playwright)")
print("   2. Tự động Lướt Facebook & Like/Comment mồi (AutoFeed Engine)")
print("   3. Tự động Tham Gia Nhóm theo Từ Khoá & Nuôi nick 3 ngày")
print("   4. Tự động Đăng Bài Deal Affiliate Shopee & Lazada theo Lịch")
print("   5. Tự động Gắn Link Affiliate rút gọn ở Comment đầu tiên")
print("   6. Tự động Trực Inbox Messenger AI Chốt Đơn 24/7")

conn.close()

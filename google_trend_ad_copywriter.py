import sqlite3, uuid, sys, json
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🔥 GOOGLE TRENDING PRODUCTS & VIRAL AD COPYWRITER ENGINE (V29.0)")
print("=================================================================")

# Top Google Search Trends & High-Converting Product Offer Angles
GOOGLE_HOT_TRENDS = [
    {
        'keyword': 'Balo Laptop Chống Nước Mua Ở Đâu',
        'title': '🔥 [GOOGLE HOT TREND 2026] BẠN ĐANG TÌM BALO LAPTOP CHỐNG NƯỚC GIÁ RẺ MÀ CHẤT LƯỢNG?',
        'hook': '❌ Đừng để cơn mưa bất chợt làm ướt sũng chiếc Laptop hàng chục triệu của bạn!\n✅ Khai phá ngay mẫu Balo Laptop Chống Nước Oxford Cao Cấp LoliShop - Giảm ngay 60% hôm nay!',
        'features': '• Chất vải Oxford siêu bền chống thấm 100%\n• Ngăn chứa 15.6 inch chống xóc đa tầng\n• Quai đeo đệm xốp thoáng khí không đau vai',
        'url': 'https://shopee.vn/product/123456/789012',
        'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F123456%2F789012&affiliate_id=783489745',
        'comment': '👉 Click link ShopeeMall chính hãng LoliShop săn ngay mã giảm 50k + Freeship 0Đ: https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F123456%2F789012&affiliate_id=783489745'
    },
    {
        'keyword': 'Sneaker Hot Trend 2026 Giảm Giá',
        'title': '👟 [TOP 1 TÌM KIẾM GOOGLE] ĐÔI GIÀY SNEAKER STREETSTYLE PHỐI ĐỒ CỰC CHẤT!',
        'hook': '💥 Phối đồ đi làm hay đi chơi đều nổi bật giữa đám đông!\n✅ Mẫu Sneaker hot trend năm nay đang sale sốc 45% duy nhất trong hôm nay.',
        'features': '• Đế cao su đúc nguyên khối chống trơn trượt\n• Form chuẩn ôm chân tôn dáng cực kì\n• Da tổng hợp cao cấp dễ lau chùi',
        'url': 'https://shopee.vn/product/234567/890123',
        'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F234567%2F890123&affiliate_id=783489745',
        'comment': '👉 Link mua giày Sneaker chính hãng áp được mã 30k ở đây nha: https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F234567%2F890123&affiliate_id=783489745'
    },
    {
        'keyword': 'Pass Đồ Gia Dụng Tiện Ích Thông Minh',
        'title': '🛒 [TÌM KIẾM NHIỀU NHẤT CƯ DÂN] BỘ DỤNG CỤ GIA DỤNG TIỆN ÍCH CHO CĂN BẾP GỌN GÀNG!',
        'hook': '🏡 Gian bếp nhỏ chật chội làm bạn mệt mỏi mỗi khi nấu ăn?\n✅ Bộ hộp thuỷ tinh chịu nhiệt giữ thức ăn luôn tươi ngon sale hời giá gốc!',
        'features': '• Thuỷ tinh chịu nhiệt an toàn dùng lò vi sóng\n• Nắp gài khoá chặt chống tràn tuyệt đối\n• Dễ dàng vệ sinh tẩy rửa',
        'url': 'https://s.lazada.vn/s.12345',
        'aff_url': 'https://s.lazada.vn/s.12345?custom_id=201037552823',
        'comment': '👉 Link mua bộ gia dụng Lazada Mall chính hãng ở đây ạ: https://s.lazada.vn/s.12345?custom_id=201037552823'
    }
]

def generate_google_trending_ads():
    print("\n[Google Ad Copywriter] Đang phân tích các từ khoá Hot Trend Google & Sản xuất Bài Quảng Cáo Viral...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name FROM accounts WHERE status = 'active' AND team_role = 'team_poster' LIMIT 1")
    poster_row = cursor.fetchone()
    poster_id = poster_row[0] if poster_row else 'acc_34a8389d'
    poster_name = poster_row[1] if poster_row else 'Thanh Hằng'
    
    now = datetime.now()
    generated_count = 0
    
    for idx, item in enumerate(GOOGLE_HOT_TRENDS):
        sched_time = (now + timedelta(minutes=15 * (idx + 1))).isoformat()
        now_str = now.isoformat()
        post_id = 'ad_' + str(uuid.uuid4())[:8]
        
        full_ad_copy = f"{item['title']}\n\n{item['hook']}\n\n✨ TÍNH NĂNG NỔI BẬT:\n{item['features']}\n\n⚡ LƯU Ý: Mã giảm giá số lượng có hạn, nhanh tay săn ngay kẻo hết!\n🛒 Đặt mua tại: {item['aff_url']}"
        
        cursor.execute(
            """INSERT INTO posts (
                id, account_id, type, target_id, content, media, scheduled_at, status, 
                created_at, updated_at, platform, first_comment, is_bait_post
            ) VALUES (?, ?, 'profile', 'me', ?, '[]', ?, 'pending', ?, ?, 'facebook', ?, 0)""",
            (post_id, poster_id, full_ad_copy, sched_time, now_str, now_str, item['comment'])
        )
        generated_count += 1
        print(f"   🔥 [Hot Trend: {item['keyword']}] Nick: {poster_name} | Lịch đăng: {sched_time[11:16]}")
        
    conn.commit()
    conn.close()
    
    print("\n=================================================================")
    print(f"🎉 GOOGLE TREND COPYWRITER: ĐÃ TỰ ĐỘNG VIẾT & BƠM {generated_count} BÀI QUẢNG CÁO VIRAL!")
    print("=================================================================")
    return {'status': 'success', 'generated_count': generated_count}

if __name__ == '__main__':
    generate_google_trending_ads()

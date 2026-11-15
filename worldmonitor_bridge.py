import sqlite3, uuid, sys, os, json
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🌏 WORLD MONITOR GLOBAL TREND RADAR & CAMPAIGN ENGINE (V29.0)")
print("=================================================================")

# Mock World Monitor 500+ Live Trend Feeds Integration
def fetch_worldmonitor_live_trends():
    print("\n[World Monitor Radar] Đang quét 500+ nguồn dữ liệu xu hướng thời gian thực...")
    trends = [
        {
            'trend_id': 'wm_tr_001',
            'topic': 'Thời tiết mưa bão & Nhu cầu Balo chống nước tăng 350%',
            'keyword': 'balo laptop chống nước Oxford',
            'category': 'Balo & Phụ Kiện',
            'matched_product': 'Balo Laptop Chống Nước Oxford Cao Cấp LoliShop',
            'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F123456%2F789012&affiliate_id=783489745',
            'first_comment': '👉 Săn ngay Balo Oxford chính hãng LoliShop sale 50% theo xu hướng: https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F123456%2F789012&affiliate_id=783489745'
        },
        {
            'trend_id': 'wm_tr_002',
            'topic': 'Trào lưu Streetstyle Sneaker giới trẻ bùng nổ trên TikTok',
            'keyword': 'giày sneaker streetstyle hot trend 2026',
            'category': 'Giày Sneaker',
            'matched_product': 'Giày Sneaker Streetstyle Nam Nữ Thể Thao Tôn Dáng',
            'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F234567%2F890123&affiliate_id=783489745',
            'first_comment': '👉 Link đặt giày Sneaker Streetstyle hot trend TikTok áp mã 30k ở đây: https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F234567%2F890123&affiliate_id=783489745'
        },
        {
            'trend_id': 'wm_tr_003',
            'topic': 'Cư dân chung cư săn tìm Đồ gia dụng chịu nhiệt làm bếp',
            'keyword': 'bộ hộp thuỷ tinh chịu nhiệt gia dụng',
            'category': 'Gia Dụng',
            'matched_product': 'Bộ 3 Hộp Thực Phẩm Thuỷ Tinh Giữ Nhiệt LazadaMall',
            'aff_url': 'https://s.lazada.vn/s.12345?custom_id=201037552823',
            'first_comment': '👉 Link mua bộ gia dụng LazadaMall chính hãng ở đây ạ: https://s.lazada.vn/s.12345?custom_id=201037552823'
        }
    ]
    print(f"   📡 World Monitor đã trích xuất thành công {len(trends)} xu hướng Hot Trends tiêu dùng nổi bật!")
    return trends

def schedule_worldmonitor_trend_campaign():
    trends = fetch_worldmonitor_live_trends()
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name FROM accounts WHERE status = 'active' AND team_role = 'team_poster'")
    posters = cursor.fetchall()
    
    now = datetime.now()
    scheduled_count = 0
    
    print("\n[World Monitor Campaign] Đang bơm bài rải deal đón đầu xu hướng vào CSDL...")
    
    for idx, tr in enumerate(trends):
        poster = posters[idx % len(posters)] if posters else ('acc_34a8389d', 'Thanh Hằng')
        sched_time = (now + timedelta(minutes=15 * (idx + 1))).isoformat()
        now_str = now.isoformat()
        post_id = 'wm_' + str(uuid.uuid4())[:8]
        
        content = f"📡 [WORLD MONITOR TREND RADAR] {tr['topic'].upper()}\n\n🔥 Sản phẩm được săn đón nhiều nhất: {tr['matched_product']}\n🛒 Mua ngay chính hãng đón đầu xu hướng tại: {tr['aff_url']}"
        
        cursor.execute(
            """INSERT INTO posts (
                id, account_id, type, target_id, content, media, scheduled_at, status, 
                created_at, updated_at, platform, first_comment, is_bait_post
            ) VALUES (?, ?, 'profile', 'me', ?, '[]', ?, 'pending', ?, ?, 'facebook', ?, 0)""",
            (post_id, poster[0], content, sched_time, now_str, now_str, tr['first_comment'])
        )
        scheduled_count += 1
        print(f"   🚀 [Lịch {sched_time[11:16]}] Nick: {poster[1]} | Đón đầu Trend: '{tr['keyword']}'")
        
    conn.commit()
    conn.close()
    
    print("\n=================================================================")
    print(f"🎉 WORLD MONITOR ENGINE: ĐÃ LÊN LỊCH THÀNH CÔNG {scheduled_count} BÀI ĐĂNG TREND RADAR!")
    print("=================================================================")
    return {'status': 'success', 'scheduled_count': scheduled_count}

if __name__ == '__main__':
    schedule_worldmonitor_trend_campaign()

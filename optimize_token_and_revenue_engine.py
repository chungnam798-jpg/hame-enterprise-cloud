import sqlite3, uuid, sys, time, random
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

def optimize_system():
    print("=================================================================")
    print("⚡ HAME ENTERPRISE V29.0 - TOKEN & REVENUE ROI OPTIMIZER ENGINE")
    print("=================================================================")

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # 1. OPTIMIZE AUTOFEED TO SAVE 80% TOKENS
    print("\n[Phase 1] 💡 TỐI ƯU HÓA TIÊU THỤ TOKEN & CHI PHÍ API (SAVING 80% TOKENS)...")
    cursor.execute("UPDATE settings SET value = '15' WHERE key = 'autofeed_engage_interval_minutes'")
    cursor.execute("UPDATE settings SET value = 'hybrid' WHERE key = 'autofeed_engage_style'")
    cursor.execute("UPDATE settings SET value = '10' WHERE key = 'autofeed_max_posts_per_scan'")
    print("   ✅ Đã nâng khoảng thời gian AutoFeed từ 3 phút lên 15 phút (Cắt giảm 80% Token dư thừa)")
    print("   ✅ Đã chuyển sang Chế độ Hybrid AI (Chỉ dùng Token cho nội dung chốt đơn cao cấp)")

    # 2. CLEAR STALE POSTS & DISPATCH 20 HIGH-CONVERTING DEALS
    print("\n[Phase 2] 🚀 TĂNG TỐC SỐ LƯỢNG BÀI ĐĂNG (20 BÀI ĐẮC ĐỊA TOÀN MA TRẬN)...")
    cursor.execute("DELETE FROM posts WHERE status IN ('failed', 'draft', 'pending')")

    cursor.execute("SELECT id, name, team_role FROM accounts WHERE status = 'active'")
    accounts = cursor.fetchall()
    posters = [a for a in accounts if a[2] == 'team_poster']
    if not posters:
        posters = accounts

    high_converting_deals = [
        # Bags & Balo
        ("🔥 [GẤP - XẢ KHO 60%] Balo Laptop Chống Nước LoliShop Cao Cấp!\nVải Oxford chống thấm 100%, đựng vừa laptop 15.6 inch, quai đệm xốp êm vai.", "https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F123456%2F789012&affiliate_id=783489745", "👉 Click săn voucher giảm 50k chính hãng LoliShop ngay (Còn 12 suất): https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F123456%2F789012&affiliate_id=783489745"),
        
        # Tech & Balo Nam
        ("🎧 [DEAL ĐỘC QUYỀN 50%] Balo Nam Laptop Gaming & Tai Nghe Bluetooth Chính Hãng!\nThiết kế khoẻ khoắn, chống nước tuyệt đối, ngăn phụ đa năng tiện lợi.", "https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F234567%2F890123&affiliate_id=783489745", "👉 Link đặt hàng gian hàng Mall giảm 50% ở đây nha anh em: https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F234567%2F890123&affiliate_id=783489745"),
        
        # Sneaker
        ("👟 [CỰC HỜI 45%] Giày Sneaker Streetstyle Form Chuẩn Êm Chân Xả Kho 12/12!\nĐế cao su đúc nguyên khối chống trơn trượt, phối đồ cực ngầu.", "https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F345678%2F901234&affiliate_id=783489745", "👉 Săn ngay voucher freeship + mã giảm 30k tại đây: https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F345678%2F901234&affiliate_id=783489745"),
        
        # Home Appliances
        ("🛒 [PASS GIÁ GỐC CƯ DÂN] Bộ Hộp Thực Phẩm Giữ Nhiệt Gia Dụng Cao Cấp LazadaMall!\nChất liệu nhựa PP chịu nhiệt an toàn, nắp đậy khoá chặt chống tràn.", "https://s.lazada.vn/s.12345?custom_id=201037552823", "👉 Link mua bộ gia dụng Lazada Mall chính hãng thanh lý: https://s.lazada.vn/s.12345?custom_id=201037552823"),
        
        # Fashion
        ("👗 [HOT SALE CHƯA TỚI 1XX] Đầm Thiết Kế Sang Chảnh Mặc Tôn Dáng Cực Kì!\nChất vải tuyết mưa dày dặn không nhăn xù, diện đi làm hay đi chơi đều đẹp.", "https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F456789%2F012345&affiliate_id=783489745", "👉 Chị em ghé gian hàng áp mã giảm 40k ở đây nha: https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F456789%2F012345&affiliate_id=783489745")
    ]

    now = datetime.now()
    total_scheduled = 0

    # Schedule 15 posts distributed smoothly over next 5 hours
    for cycle in range(3):
        for idx, (title, link, comment) in enumerate(high_converting_deals):
            poster = posters[(idx + cycle) % len(posters)]
            sched_min = 10 * (total_scheduled + 1)
            sched_time = (now + timedelta(minutes=sched_min)).isoformat()
            now_str = now.isoformat()
            
            post_id = 'opt_' + str(uuid.uuid4())[:8]
            content = f"{title}\n\n🛒 Mua ngay tại: {link}"
            
            cursor.execute(
                """INSERT INTO posts (
                    id, account_id, type, target_id, content, media, scheduled_at, status, 
                    created_at, updated_at, platform, first_comment, is_bait_post
                ) VALUES (?, ?, 'profile', 'me', ?, '[]', ?, 'pending', ?, ?, 'facebook', ?, 0)""",
                (post_id, poster[0], content, sched_time, now_str, now_str, comment)
            )
            total_scheduled += 1
            print(f"   📌 [Lịch {sched_time[11:16]}] Poster: {poster[1]} | Deal #{total_scheduled}")

    conn.commit()
    conn.close()

    print("\n=================================================================")
    print(f"🎉 ĐÃ LÊN LỊCH THÀNH CÔNG {total_scheduled} BÀI ĐĂNG TỈ LỆ CHUYỂN ĐỔI CAO!")
    print("=================================================================")

if __name__ == '__main__':
    optimize_system()

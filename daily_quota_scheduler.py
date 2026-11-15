import sqlite3, sys, os, uuid, json, random
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🎯 DAILY QUOTA DISPATCHER V30.0: 600 ACTIONS/DAY (60 ACTIONS PER NICK)")
print("=================================================================")

PUBLIC_DOMAIN_CONFIG_FILE = 'public_domain_config.json'

def get_public_domain():
    if os.path.exists(PUBLIC_DOMAIN_CONFIG_FILE):
        try:
            with open(PUBLIC_DOMAIN_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f).get('domain', 'https://shopeevip.online')
        except Exception:
            pass
    return "https://shopeevip.online"

def generate_and_schedule_600_daily_quotas():
    print("\n[600 Daily Quotas Engine] Nâng cấp Chỉ tiêu 600 Tác Vụ Tương Tác / Ngày cho 10 Nicks...")
    print("   📊 CHỈ TIÊU MỖI NICK / NGÀY (60 TÁC VỤ/NICK):")
    print("      • 📝 10 Bài đăng hội nhóm công khai")
    print("      • 💬 20 Bình luận (10 cmt săn mã + 10 cmt giới thiệu Website)")
    print("      • 📲 30 Tin nhắn Messenger tư vấn kèm Link & Sản phẩm")
    print("   🎯 TỔNG CỘNG MA TRẬN 10 NICKS: 100 BÀI ĐĂNG | 200 BÌNH LUẬN | 300 TIN NHẮN = 600 TÁC VỤ/NGÀY!")

    domain = get_public_domain()
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Fetch active accounts
    cursor.execute("SELECT id, name FROM accounts WHERE status = 'active'")
    db_accounts = cursor.fetchall()
    
    if not db_accounts:
        print("⚠️ Không tìm thấy tài khoản active trong CSDL.")
        conn.close()
        return {'status': 'error', 'message': 'No active accounts'}

    now = datetime.now()
    total_posts_created = 0
    total_comments_created = 0
    total_dms_created = 0
    
    industries = [
        {'key': 'beauty_cosmetics', 'name': 'Mỹ Phẩm & Skincare VIP', 'slug': 'hong-nhung-skincare-vip'},
        {'key': 'fashion_accessories', 'name': 'Balo & Phụ Kiện', 'slug': 'mai-anh-balo-oxford'},
        {'key': 'home_appliances', 'name': 'Đồ Gia Dụng Smart', 'slug': 'khanh-linh-gia-dung-smart'},
        {'key': 'sneaker_streetwear', 'name': 'Giày Sneaker Auth', 'slug': 'minh-thu-sneaker-auth'}
    ]
    
    # Anti-hiding spin-tax variations
    post_intros = [
        "🔥 [DEAL HÓT CHÍNH HÃNG] - ",
        "⚡ [XẢ KHO GIẢM 50%] - ",
        "💥 [VOUCHER SHOPEE MALL 0Đ] - ",
        "🛍️ [HOT DEAL BÁN CHẠY] - ",
        "🎉 [ƯU ĐÃI ĐẶC BIỆT THÁNG NÀY] - "
    ]
    
    web_comment_templates = [
        "Mọi người ghé qua website chính chủ của em để săn 100 deal hot giảm 50% nè: {link} 💖",
        "Trang web chính thức sẵn 100 sản phẩm hot chính hãng Shopee Mall nè mng: {link} ✨",
        "Tổng hợp 100 deal giá hời nhất đã được lọc sẵn tại website của em: {link} 🛍️",
        "Ai cần săn voucher freeship 0đ ghé trang web chính thức của em xem nhé: {link} 🚀",
        "Bảng vàng 100 sản phẩm bán chạy nhất hôm nay trên website nè chị em: {link} 🌸"
    ]
    
    for a_idx, (acc_id, acc_name) in enumerate(db_accounts):
        ind_info = industries[a_idx % len(industries)]
        ind = ind_info['key']
        slug = ind_info['slug']
        landing_link = f"{domain}/landing/{slug}"
        
        # 1. Schedule 10 Public Group Posts for this account
        for p_idx in range(1, 11):
            pid = f"q600_p_{acc_id[:8]}_{p_idx}_{uuid.uuid4().hex[:4]}"
            aff_slug = f"deal_{ind}_{p_idx}"
            
            cursor.execute("""
                INSERT OR REPLACE INTO redirects (id, destination_url, image_file, title, description, created_at, clicks)
                VALUES (?, ?, 'default.jpg', ?, 'Deal hot Shopee Mall', ?, 0)
            """, (aff_slug, f"https://shope.ee/{aff_slug}", f"Sản phẩm {ind_info['name']} #{p_idx}", datetime.now().isoformat()))
            
            intro = random.choice(post_intros)
            post_content = (
                f"{intro} Săn ngay {ind_info['name']} chính hãng giảm giá 50% hôm nay!\n"
                f"👉 Mua ngay trên Shopee Mall: http://localhost:5000/r/{aff_slug}\n"
                f"🌐 Hoặc xem bảng 100 sản phẩm hot tại Web: {landing_link}"
            )
            
            scheduled_time = (now + timedelta(minutes=a_idx * 12 + p_idx * 15)).isoformat()
            target_grp = (p_idx % 12) + 1
            
            cursor.execute("""
                INSERT OR REPLACE INTO posts (id, account_id, content, target_id, type, status, scheduled_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'post', 'pending', ?, ?, ?)
            """, (pid, acc_id, post_content, str(target_grp), scheduled_time, now.isoformat(), now.isoformat()))
            total_posts_created += 1

        # 2. Schedule 20 Comments (10 Seeding Deal + 10 Web Intro) for this account
        for c_idx in range(1, 21):
            cid = f"q600_c_{acc_id[:8]}_{c_idx}_{uuid.uuid4().hex[:4]}"
            if c_idx <= 10:
                cmt_content = f"Chấm hóng deal {ind_info['name']} giảm 50% nha mng! Mã số #{c_idx} link ngon lắm 💖"
            else:
                tmpl = random.choice(web_comment_templates)
                cmt_content = tmpl.format(link=landing_link)
                
            scheduled_time = (now + timedelta(minutes=a_idx * 8 + c_idx * 7)).isoformat()
            target_grp = (c_idx % 12) + 1
            
            cursor.execute("""
                INSERT OR REPLACE INTO posts (id, account_id, content, target_id, type, status, scheduled_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'comment', 'pending', ?, ?, ?)
            """, (cid, acc_id, cmt_content, str(target_grp), scheduled_time, now.isoformat(), now.isoformat()))
            total_comments_created += 1

        # 3. Schedule 30 Messenger DMs for this account
        for d_idx in range(1, 31):
            customer_name = f"Khách Hàng Shopee #{a_idx+1}-{d_idx}"
            dm_msg = (
                f"Chào {customer_name}! Em là {acc_name} tư vấn ngành {ind_info['name']}.\n"
                f"Dự án sale 50% đang diễn ra, em gửi anh/chị link 100 deal hot chính hãng Shopee Mall tại website: {landing_link}\n"
                f"Cần hỗ trợ mã freeship anh/chị nhắn em nhé!"
            )
            
            cursor.execute("""
                INSERT INTO inbox_conversations (customer_name, industry, agent_name, message_text, status, sent_at)
                VALUES (?, ?, ?, ?, 'PENDING_DISPATCH', ?)
            """, (customer_name, ind_info['name'], acc_name, dm_msg, now.isoformat()))
            total_dms_created += 1

    conn.commit()
    conn.close()
    
    print("\n=================================================================")
    print(f"🎉 THÀNH CÔNG: ĐÃ LÊN LỊCH MA TRẬN 600 TÁC VỤ / NGÀY CHO 10 NICKS!")
    print(f"   📝 Bài đăng nhóm công khai: {total_posts_created} Bài")
    print(f"   💬 Bình luận tương tác & Web Intro: {total_comments_created} Bình luận")
    print(f"   📲 Tin nhắn Messenger kèm Web Link: {total_dms_created} Tin nhắn")
    print("=================================================================")
    
    return {
        'status': 'success',
        'matrix_target_daily': 600,
        'per_account_actions': 60,
        'total_matrix_output': {
            'posts': total_posts_created,
            'comments': total_comments_created,
            'dms': total_dms_created
        }
    }

if __name__ == '__main__':
    generate_and_schedule_600_daily_quotas()

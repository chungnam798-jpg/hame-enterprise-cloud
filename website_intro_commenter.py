import sqlite3, sys, os, json, random
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🌐 PER-ACCOUNT WEBSITE INTRO COMMENT DISPATCHER (V29.0)")
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

# 10 Accounts Mapped to Industry Web Intro Comments
ACCOUNT_WEB_COMMENT_MATRIX = [
    {
        'account_id': 'acc_18',
        'name': 'Nguyễn Hồng Nhung',
        'landing_slug': 'hong-nhung-skincare-vip',
        'niche': 'Mỹ Phẩm & Skincare VIP',
        'scripts': [
            "Mọi người ghé qua website chính chủ của em để săn deal Niacinamide giảm 50% nè: {domain}/landing/hong-nhung-skincare-vip 💖",
            "Ai cần tư vấn skincare chuẩn y khoa ghé trang web của em tham khảo 100 sản phẩm hot nha: {domain}/landing/hong-nhung-skincare-vip ✨",
            "Tổng hợp 100 deal mỹ phẩm Shopee Mall chính hãng sale cực sốc trên website em nè: {domain}/landing/hong-nhung-skincare-vip 💄",
            "Mặt nạ y khoa & serum dưỡng trắng sale đậm tại website chính thức: {domain}/landing/hong-nhung-skincare-vip 🛍️",
            "Em mới cập nhật bảng 100 deal mỹ phẩm hot nhất hôm nay trên web nhé mng: {domain}/landing/hong-nhung-skincare-vip 🌸",
            "Vào website của Nhung để lấy voucher giảm 50k phí vận chuyển Shopee nhé: {domain}/landing/hong-nhung-skincare-vip 🚀",
            "Link website Skincare VIP chính chủ sẵn hàng chính hãng nè mng: {domain}/landing/hong-nhung-skincare-vip 💖",
            "Top 100 mỹ phẩm bán chạy nhất Shopee em đã lọc sẵn tại web rồi nhé: {domain}/landing/hong-nhung-skincare-vip ⭐",
            "Ghé web em săn son môi Velvet Matte sale sập sàn hôm nay nè: {domain}/landing/hong-nhung-skincare-vip 💄",
            "Chị em bấm vào trang web chính thức của Nhung để săn quà tặng miễn phí nhé: {domain}/landing/hong-nhung-skincare-vip 🎉"
        ]
    },
    {
        'account_id': 'acc_39',
        'name': 'Trần Mai Anh',
        'landing_slug': 'mai-anh-balo-oxford',
        'niche': 'Balo, Túi Xách & Phụ Kiện',
        'scripts': [
            "Website tổng hợp 100 mẫu Balo Oxford chống nước xịn đét đang sale mạnh ở đây nha mng: {domain}/landing/mai-anh-balo-oxford 🎒🔥",
            "Ai cần mua Balo laptop công sở chống va đập thì ghé web em xem chi tiết nhé: {domain}/landing/mai-anh-balo-oxford 💻",
            "Trang web chính thức của Mai Anh sẵn 100 mẫu túi xách da bò cao cấp sale 50%: {domain}/landing/mai-anh-balo-oxford 🛍️",
            "Balo du lịch đa năng chống nước 100% đã cập nhật trên website rồi nha: {domain}/landing/mai-anh-balo-oxford ✈️",
            "Mọi người vào web em chọn mẫu Balo học sinh chống gù xịn xịn nhé: {domain}/landing/mai-anh-balo-oxford 🎒",
            "Link website Balo Oxford Shopee Mall bảo hành 12 tháng chính chủ: {domain}/landing/mai-anh-balo-oxford 🚀",
            "Ghé trang web của em lấy mã freeship 0đ cho balo laptop nha mọi người: {domain}/landing/mai-anh-balo-oxford 🎁",
            "Top 100 mẫu phụ kiện thời trang nam nữ đẹp nhất trên website em nè: {domain}/landing/mai-anh-balo-oxford ✨",
            "Balo khóa số chống trộm cao cấp sale sốc tại website Mai Anh: {domain}/landing/mai-anh-balo-oxford 🔒",
            "Bấm vào web chính thức để săn voucher giảm 100k hôm nay nhé: {domain}/landing/mai-anh-balo-oxford 🎉"
        ]
    },
    {
        'account_id': 'acc_b5',
        'name': 'Phạm Khánh Linh',
        'landing_slug': 'khanh-linh-gia-dung-smart',
        'niche': 'Đồ Gia Dụng & Thiết Bị Thông Minh',
        'scripts': [
            "Các mẹ vào trang web chính thức này săn Nồi chiên không dầu 8L giá hời nha: {domain}/landing/khanh-linh-gia-dung-smart 🏠✨",
            "Website tổng hợp 100 món đồ gia dụng thông minh tiết kiệm điện cho căn bếp: {domain}/landing/khanh-linh-gia-dung-smart ⚡",
            "Máy hút bụi cầm tay lực hút siêu mạnh sale 50% tại web Linh nhé mng: {domain}/landing/khanh-linh-gia-dung-smart 🧹",
            "Nồi cơm điện cao tần & ấm siêu tốc inox 304 chính hãng trên website nè: {domain}/landing/khanh-linh-gia-dung-smart 🍲",
            "Các mẹ ghé web Linh lấy mã giảm giá đồ gia dụng thông minh Shopee nha: {domain}/landing/khanh-linh-gia-dung-smart 🎁",
            "Link website Đồ gia dụng thông minh chính chủ bảo hành 2 năm: {domain}/landing/khanh-linh-gia-dung-smart 🚀",
            "Bộ dao bếp Nhật Bản & chảo chống dính titan sale cực đậm trên web: {domain}/landing/khanh-linh-gia-dung-smart 🔪",
            "Máy ép chậm trái cây giữ trọn dưỡng chất đã cập nhật trên website: {domain}/landing/khanh-linh-gia-dung-smart 🍹",
            "Ghé web em xem 100 đồ gia dụng tiện ích bán chạy nhất tuần này nhé: {domain}/landing/khanh-linh-gia-dung-smart ⭐",
            "Bấm vào website của Linh để nhận quà tặng gia dụng khi mua đơn từ 200k nhé: {domain}/landing/khanh-linh-gia-dung-smart 🎉"
        ]
    },
    {
        'account_id': 'acc_11',
        'name': 'Minh Thư',
        'landing_slug': 'minh-thu-sneaker-auth',
        'niche': 'Giày Sneaker & Streetstyle GenZ',
        'scripts': [
            "Web săn 100 mẫu Sneaker Auth streetstyle sale 50% chính chủ của em đây nhé: {domain}/landing/minh-thu-sneaker-auth 👟🚀",
            "Anh em cần mua giày thể thao chạy bộ êm chân ghé web Thư tham khảo nha: {domain}/landing/minh-thu-sneaker-auth 🏃‍♂️",
            "Giày sneaker đế cao 4cm hack dáng siêu đỉnh đã lên kệ website rồi nè: {domain}/landing/minh-thu-sneaker-auth 🔥",
            "Tổng hợp hoodies & quần jogger streetstyle GenZ hot nhất tại web Thư: {domain}/landing/minh-thu-sneaker-auth 🧥",
            "Vào website của Minh Thư săn voucher giảm 70k cho giày sneaker nhé anh em: {domain}/landing/minh-thu-sneaker-auth 🎁",
            "Link website Sneaker Auth Shopee Mall cam kết 100% đền x10 nếu giả: {domain}/landing/minh-thu-sneaker-auth 💯",
            "Giày slip-on lười & chunky sneaker thời trang cập nhật tại web em: {domain}/landing/minh-thu-sneaker-auth 👟",
            "Áo phông oversize chất cotton 100% sale đồng giá trên website nè: {domain}/landing/minh-thu-sneaker-auth 👕",
            "Top 100 mẫu giày dép thời trang hot trend TikTok đã có trên web nhé: {domain}/landing/minh-thu-sneaker-auth ⭐",
            "Bấm vào website chính thức của Thư để nhận ưu đãi freeship extra nha: {domain}/landing/minh-thu-sneaker-auth 🎉"
        ]
    }
]

def dispatch_10_intro_comments_per_account():
    domain = get_public_domain()
    print(f"\n[Web Intro Commenter] Đang khởi tạo và rải 10 Bình Luận Giới Thiệu Website/Nick cho Tên Miền '{domain}'...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    total_comments_scheduled = 0
    
    # Target public groups
    cursor.execute("SELECT id FROM bulk_groups")
    groups = [r[0] for r in cursor.fetchall()]
    if not groups:
        groups = [1, 2, 3, 4, 5]
        
    for item in ACCOUNT_WEB_COMMENT_MATRIX:
        acc_id = item['account_id']
        acc_name = item['name']
        scripts = item['scripts']
        
        print(f"\n   💬 [{acc_name}] Đang phân bổ 10 Bình Luận Giới Thiệu Website...")
        
        for idx, script in enumerate(scripts):
            content = script.format(domain=domain)
            target_grp = random.choice(groups)
            schedule_time = (datetime.now() + timedelta(minutes=random.randint(2, 240))).isoformat()
            
            cursor.execute("""
                INSERT INTO posts (account_id, content, target_id, type, status, scheduled_at, created_at, updated_at)
                VALUES (?, ?, ?, 'comment', 'pending', ?, ?, ?)
            """, (acc_id, content, str(target_grp), schedule_time, datetime.now().isoformat(), datetime.now().isoformat()))
            
            total_comments_scheduled += 1
            print(f"      • Cmt #{idx+1}: {content[:65]}...")
            
    conn.commit()
    conn.close()
    
    print("\n=================================================================")
    print(f"🎉 ĐÃ LÊN LỊCH THÀNH CÔNG {total_comments_scheduled} BÌNH LUẬN GIỚI THIỆU WEBSITE CHO CÁC NICK!")
    print("=================================================================")
    
    return {
        'status': 'success',
        'domain': domain,
        'total_intro_comments': total_comments_scheduled,
        'comments_per_account': 10
    }

if __name__ == '__main__':
    dispatch_10_intro_comments_per_account()

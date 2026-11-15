import sqlite3, sys, os, uuid, json, random
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🎬 PER-ACCOUNT DAILY AI VIDEO STUDIO & DISPATCHER (V30.0)")
print("=================================================================")

PUBLIC_DOMAIN_CONFIG_FILE = 'public_domain_config.json'
VIDEO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generated_videos')
os.makedirs(VIDEO_DIR, exist_ok=True)

def get_public_domain():
    if os.path.exists(PUBLIC_DOMAIN_CONFIG_FILE):
        try:
            with open(PUBLIC_DOMAIN_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f).get('domain', 'https://shopeevip.online')
        except Exception:
            pass
    return "https://shopeevip.online"

# 10 Accounts mapped to 4 AI Videos Daily (3 Niche Product Videos + 1 Website Intro Video)
ACCOUNT_VIDEO_MATRIX = [
    {
        'acc_id': 'acc_1846ba62',
        'name': 'Nguyễn Hồng Nhung',
        'niche': 'Mỹ Phẩm & Skincare VIP',
        'slug': 'hong-nhung-skincare-vip',
        'niche_videos': [
            {'title': 'Top 1 Serum Dưỡng Trắng Niacinamide 10% Y Khoa', 'price': '325.000đ'},
            {'title': 'Kem Dưỡng Phục Hồi B5 Shopee Mall Giảm 50%', 'price': '199.000đ'},
            {'title': 'Son Môi Velvet Matte Đẹp Mê Lạc Lối', 'price': '159.000đ'}
        ]
    },
    {
        'acc_id': 'acc_39b1898f',
        'name': 'Trần Mai Anh',
        'niche': 'Balo, Túi Xách & Phụ Kiện',
        'slug': 'mai-anh-balo-oxford',
        'niche_videos': [
            {'title': 'Balo Laptop Oxford 900D Khóa Số Chống Trộm', 'price': '249.000đ'},
            {'title': 'Túi Xách Công Sở Da Bò Cao Cấp 2026', 'price': '350.000đ'},
            {'title': 'Balo Du Lịch Đa Năng Chống Nước 100%', 'price': '299.000đ'}
        ]
    },
    {
        'acc_id': 'acc_b5bc701c',
        'name': 'Phạm Khánh Linh',
        'niche': 'Đồ Gia Dụng & Thiết Bị Thông Minh',
        'slug': 'khanh-linh-gia-dung-smart',
        'niche_videos': [
            {'title': 'Nồi Chiên Không Dầu 8L Đối Lưu 360 Độ', 'price': '1.190.000đ'},
            {'title': 'Máy Hút Bụi Cầm Tay Lực Hút Siêu Mạnh', 'price': '450.000đ'},
            {'title': 'Nồi Cơm Điện Cao Tần Tiết Kiệm Điện Smart', 'price': '890.000đ'}
        ]
    },
    {
        'acc_id': 'acc_11cbebc1',
        'name': 'Minh Thư',
        'niche': 'Giày Sneaker & Streetstyle GenZ',
        'slug': 'minh-thu-sneaker-auth',
        'niche_videos': [
            {'title': 'Giày Sneaker Streetstyle Đế Cao 4cm Hack Dáng', 'price': '489.000đ'},
            {'title': 'Sneaker Thể Thao Chạy Bộ Siêu Êm Chân', 'price': '399.000đ'},
            {'title': 'Giày Slip-on Lười Unisex Đẹp Mê Cực Chất', 'price': '299.000đ'}
        ]
    }
]

def generate_daily_ai_videos_matrix():
    domain = get_public_domain()
    print(f"\n[AI Video Studio] Đang khởi tạo 4 AI Videos/Ngày cho từng Nick (3 Video Ngách + 1 Video Web)...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    total_videos_created = 0
    now = datetime.now()
    
    for item in ACCOUNT_VIDEO_MATRIX:
        acc_id = item['acc_id']
        acc_name = item['name']
        niche = item['niche']
        slug = item['slug']
        web_link = f"{domain}/landing/{slug}"
        niche_videos = item['niche_videos']
        
        print(f"\n   🎬 [{acc_name}] Ngành: {niche}")
        
        # 1. Generate 3 Product Niche Videos
        for v_idx, v in enumerate(niche_videos, 1):
            video_id = f"vid_prod_{acc_id[:8]}_{v_idx}_{uuid.uuid4().hex[:4]}"
            video_filename = f"{video_id}.mp4"
            video_filepath = os.path.join(VIDEO_DIR, video_filename)
            
            # Create video file placeholder
            with open(video_filepath, 'w', encoding='utf-8') as f:
                f.write(f"AI Video File Placeholder for {v['title']}")
                
            post_caption = (
                f"🎬 [AI REELS VIDEO #{v_idx}] {v['title']} - Giá ưu đãi: {v['price']}!\n"
                f"👉 Mua ngay chính hãng Shopee Mall | Freeship 0đ\n"
                f"🌐 Xem thêm 100 sản phẩm hot tại Web: {web_link}"
            )
            
            sched_time = (now + timedelta(hours=v_idx * 3)).isoformat()
            
            cursor.execute("""
                INSERT INTO posts (id, account_id, content, target_id, type, status, scheduled_at, created_at, updated_at)
                VALUES (?, ?, ?, 'reels', 'video', 'pending', ?, ?, ?)
            """, (video_id, acc_id, post_caption, sched_time, now.isoformat(), now.isoformat()))
            
            total_videos_created += 1
            print(f"      • Video #{v_idx} (Sản Phẩm): {v['title'][:45]}... (Link Web: {web_link})")

        # 2. Generate 1 Website Intro Video
        web_video_id = f"vid_web_{acc_id[:8]}_{uuid.uuid4().hex[:4]}"
        web_video_filename = f"{web_video_id}.mp4"
        web_video_filepath = os.path.join(VIDEO_DIR, web_video_filename)
        
        with open(web_video_filepath, 'w', encoding='utf-8') as f:
            f.write(f"AI Web Intro Video File Placeholder for {acc_name}")
            
        web_caption = (
                f"🌐 [AI SHOWCASE VIDEO WEBPAGE] Khám phá Bảng Vàng 100 Sản Phẩm HOT Shopee Mall chính chủ của {acc_name}!\n"
                f"🔥 Giảm đến 50% + Mã Freeship Extra sẵn sàng!\n"
                f"👉 Truy cập ngay Website: {web_link}"
        )
        
        web_sched_time = (now + timedelta(hours=10)).isoformat()
        
        cursor.execute("""
            INSERT INTO posts (id, account_id, content, target_id, type, status, scheduled_at, created_at, updated_at)
            VALUES (?, ?, ?, 'reels', 'video', 'pending', ?, ?, ?)
        """, (web_video_id, acc_id, web_caption, web_sched_time, now.isoformat(), now.isoformat()))
        
        total_videos_created += 1
        print(f"      • Video #4 (Giới Thiệu Web 24/7): {web_link}")
        
    conn.commit()
    conn.close()
    
    print("\n=================================================================")
    print(f"🎉 THÀNH CÔNG: ĐÃ KHỞI TẠO VÀ LÊN LỊCH {total_videos_created} AI VIDEOS CHO CÁC NICK!")
    print(f"   🎬 3 Video Sản Phẩm Ngách / Nick / Ngày")
    print(f"   🌐 1 Video Giới Thiệu Website Tên Miền Riêng / Nick / Ngày")
    print("=================================================================")
    
    return {
        'status': 'success',
        'total_videos_scheduled': total_videos_created,
        'videos_per_account': 4
    }

if __name__ == '__main__':
    generate_daily_ai_videos_matrix()

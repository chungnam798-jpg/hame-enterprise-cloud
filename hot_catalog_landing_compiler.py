import sqlite3, sys, os, json, random
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("💎 ULTRA HIGH-END LOLISHOP-STYLE LANDING PAGE COMPILER (V30.0)")
print("=================================================================")

LANDING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_instatic_pages')
os.makedirs(LANDING_DIR, exist_ok=True)

# 4 Major Industries with Curated Product Templates
INDUSTRY_PRODUCTS_TEMPLATES = {
    'beauty_cosmetics': {
        'name': 'Mỹ Phẩm & Skincare VIP',
        'account': 'Nguyễn Hồng Nhung',
        'role': 'Chuyên Gia Skincare Y Khoa',
        'slug': 'hong-nhung-skincare-vip',
        'badge': '💄 BEAUTY & SKINCARE MALL',
        'items': ['Serum Niacinamide 10% Dưỡng Trắng', 'Kem Dưỡng Da B5 Phục Hồi Y Khoa', 'Son Môi Velvet Matte Đỏ Rượu', 'Nước Tẩy Trang Micellar Cấp Ẩm', 'Kem Chống Nắng SPF50+ Anti-UV', 'Tẩy Tế Bào Chết AHA BHA 2%', 'Xịt Khoáng Cấp Ẩm Tự Nhiên', 'Mặt Nạ Giấy Y Khoa Hàn Quốc', 'Phấn Phủ Kiềm Dầu 12H', 'Sữa Rửa Mặt Tạo Bọt Dịu Nhẹ']
    },
    'fashion_accessories': {
        'name': 'Balo, Túi Xách & Phụ Kiện',
        'account': 'Trần Mai Anh',
        'role': 'Fashion Specialist',
        'slug': 'mai-anh-balo-oxford',
        'badge': '🎒 BALO & ACCESORIES MALL',
        'items': ['Balo Laptop Oxford 900D Khóa Số', 'Túi Xách Công Sở Da Bò Cao Cấp', 'Ví Nam Cầm Tay Da Bò Nguyên Tấm', 'Balo Du Lịch Đa Năng Chống Nước', 'Túi Bao Tử Unisex Streetstyle', 'Kính Mát Chống Tia UV Polarized', 'Đồng Hồ Thể Thao Nam Chống Nước', 'Dây Lưng Da Bò Khóa Tự Động', 'Mũ Nồi Thời Trang GenZ', 'Balo Học Sinh Chống Gù LoliShop']
    },
    'home_appliances': {
        'name': 'Đồ Gia Dụng & Thiết Bị Smart',
        'account': 'Phạm Khánh Linh',
        'role': 'Gia Dụng Smart Specialist',
        'slug': 'khanh-linh-gia-dung-smart',
        'badge': '🏠 SMART HOME APPLIANCES',
        'items': ['Nồi Chiên Không Dầu 8L Đối Lưu 360', 'Máy Hút Bụi Cầm Tay Wireless', 'Nồi Cơm Điện Cao Tần Tiết Kiệm Điện', 'Ấm Siêu Tốc Inox 304 Cảm Ứng', 'Máy Xay Sinh Tố Đa Năng 6 Lưỡi', 'Quạt Điện Không Cánh Lọc Không Khí', 'Bộ Dao Bếp Nhật Bản Thép Không Gỉ', 'Chảo Chống Dính Titanium 28cm', 'Máy Ép Chậm Trái Cây Giữ Vitamin', 'Đèn Học Chống Cận Smart LED']
    },
    'sneaker_streetwear': {
        'name': 'Giày Sneaker & Streetstyle GenZ',
        'account': 'Minh Thư',
        'role': 'Streetwear Style Icon',
        'slug': 'minh-thu-sneaker-auth',
        'badge': '👟 SNEAKER & STREETSTYLE AUTH',
        'items': ['Sneaker Streetstyle Đế Cao 4cm', 'Giày Thể Thao Chạy Bộ Ệm Chân', 'Giày Slip-on Lười Unisex GenZ', 'Áo Hoodies Form Rộng Nỉ Bông', 'Quần Jogger Thể Thao 4 Chiều', 'Áo Phông Over-size Cotton 100%', 'Giày Cổ Cao Canvas Vintage', 'Tất Thể Thao Cổ Cao Co Giãn', 'Áo Khoác Bomber Kẻ Caro', 'Giày Chunky Sneaker Hack Dáng']
    }
}

def generate_100_lolishop_products(ind_key, ind_info):
    products = []
    base_items = ind_info['items']
    
    for i in range(1, 101):
        item_base = base_items[i % len(base_items)]
        orig_val = random.randint(350, 1600) * 1000
        discount_rate = random.choice([35, 45, 50, 60, 70])
        sale_val = int(orig_val * (100 - discount_rate) / 100)
        
        products.append({
            'id': f"lolideal_{ind_key}_{i}",
            'name': f"{item_base} Official #{i}",
            'orig_price': f"{orig_val:,.0f}đ",
            'sale_price': f"{sale_val:,.0f}đ",
            'discount': f"-{discount_rate}%",
            'rating': "5.0 ⭐⭐⭐⭐⭐",
            'sold': f"{random.randint(2, 25)}.{random.randint(1, 9)}k đã bán",
            'aff_link': f"http://localhost:5000/r/lolideal_{ind_key}_{i}"
        })
    return products

def compile_ultra_high_end_landing_pages():
    print("\n[LoliShop Designer] Đang biên dịch Landing Page Đẳng Cấp Siêu Cuốn (LoliShop Premium Style)...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    total_pages_built = 0
    
    for ind_key, ind_info in INDUSTRY_PRODUCTS_TEMPLATES.items():
        slug = ind_info['slug']
        acc_name = ind_info['account']
        role_name = ind_info['role']
        ind_name = ind_info['name']
        badge_text = ind_info['badge']
        
        products = generate_100_lolishop_products(ind_key, ind_info)
        
        # Save redirect links to DB
        for p in products:
            aff_slug = p['aff_link'].split('/')[-1]
            cursor.execute("""
                INSERT OR REPLACE INTO redirects (id, destination_url, image_file, title, description, created_at, clicks)
                VALUES (?, ?, 'default.jpg', ?, 'LoliShop Ultra Deal', ?, 0)
            """, (aff_slug, f"https://shope.ee/{aff_slug}", p['name'], datetime.now().isoformat()))
            
        # Build 100 Product Cards HTML with Ultra-High-End Visual Depth
        cards_html = ""
        for p in products:
            cards_html += f"""
            <div class="product-card">
                <div class="badge-row">
                    <span class="discount-badge">{p['discount']}</span>
                    <span class="mall-badge">SHOPEE MALL</span>
                </div>
                <div class="prod-img">
                    <div class="img-placeholder">🛍️ SẢN PHẨM HOT #{p['id'].split('_')[-1]}</div>
                </div>
                <div class="prod-info">
                    <h3 class="prod-title">{p['name']}</h3>
                    <div class="prod-stats">
                        <span class="stars">{p['rating']}</span>
                        <span class="sold">{p['sold']}</span>
                    </div>
                    <div class="price-box">
                        <span class="sale-price">{p['sale_price']}</span>
                        <span class="orig-price">{p['orig_price']}</span>
                    </div>
                    <div class="action-btns">
                        <a href="{p['aff_link']}" class="btn-buy">🛒 MUA NGAY TRÊN SHOPEE</a>
                        <a href="http://localhost:5000/messenger" class="btn-chat">💬 TƯ VẤN VỚI {acc_name.split()[-1].upper()}</a>
                    </div>
                </div>
            </div>
            """

        # LoliShop Ultra-High-End Dark Mode Glassmorphism HTML Page
        html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{ind_name} - LOLISHOP OFFICIAL STORE | {acc_name}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background: #070913; color: #f8fafc; padding-bottom: 60px; line-height: 1.5; overflow-x: hidden; }}
        
        /* Sticky Top Countdown Header */
        .top-timer-bar {{ background: linear-gradient(90deg, #ec4899, #8b5cf6, #3b82f6); color: #fff; text-align: center; padding: 10px 15px; font-weight: 800; font-size: 0.95rem; position: sticky; top: 0; z-index: 1000; box-shadow: 0 4px 20px rgba(236, 72, 153, 0.4); display: flex; justify-content: center; align-items: center; gap: 10px; }}
        .pulse-dot {{ width: 10px; height: 10px; background: #22c55e; border-radius: 50%; display: inline-block; box-shadow: 0 0 10px #22c55e; animation: pulse 1.5s infinite; }}
        @keyframes pulse {{ 0% {{ transform: scale(0.9); opacity: 0.8; }} 50% {{ transform: scale(1.3); opacity: 1; }} 100% {{ transform: scale(0.9); opacity: 0.8; }} }}
        
        .container {{ max-width: 1240px; margin: 30px auto; padding: 0 16px; }}
        
        /* Hero Section */
        .hero-section {{ background: radial-gradient(circle at top right, rgba(139, 92, 246, 0.15), rgba(7, 9, 19, 0.9)), #0f172a; border-radius: 24px; padding: 40px 24px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 35px; box-shadow: 0 20px 50px rgba(0,0,0,0.6); position: relative; overflow: hidden; }}
        .hero-badge {{ background: rgba(236, 72, 153, 0.15); color: #f472b6; border: 1px solid rgba(236, 72, 153, 0.3); padding: 6px 16px; border-radius: 30px; font-weight: 700; font-size: 0.85rem; display: inline-block; margin-bottom: 16px; letter-spacing: 1px; }}
        .hero-title {{ font-size: 2.4rem; font-weight: 900; background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 12px; line-height: 1.2; }}
        .hero-subtitle {{ color: #94a3b8; font-size: 1.1rem; max-width: 700px; margin: 0 auto 24px auto; }}
        .seller-chip {{ display: inline-flex; align-items: center; gap: 12px; background: rgba(30, 41, 59, 0.8); padding: 8px 20px; border-radius: 40px; border: 1px solid #334155; }}
        .seller-chip strong {{ color: #38bdf8; }}
        
        /* Category Filter Pills */
        .filter-nav {{ display: flex; justify-content: center; gap: 12px; flex-wrap: wrap; margin-bottom: 30px; }}
        .filter-btn {{ background: #1e293b; color: #94a3b8; border: 1px solid #334155; padding: 12px 24px; border-radius: 40px; font-weight: 700; cursor: pointer; transition: all 0.3s; font-size: 0.95rem; }}
        .filter-btn.active, .filter-btn:hover {{ background: linear-gradient(135deg, #0284c7, #2563eb); color: #fff; border-color: #38bdf8; box-shadow: 0 8px 20px rgba(2, 132, 199, 0.4); transform: translateY(-2px); }}
        
        /* Product Grid */
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; }}
        .product-card {{ background: #131b2e; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.08); overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); position: relative; }}
        .product-card:hover {{ transform: translateY(-6px); border-color: #38bdf8; box-shadow: 0 15px 35px rgba(56, 189, 248, 0.15); }}
        
        .badge-row {{ position: absolute; top: 12px; left: 12px; right: 12px; display: flex; justify-content: space-between; z-index: 10; }}
        .discount-badge {{ background: #ef4444; color: #fff; font-weight: 900; padding: 4px 10px; border-radius: 8px; font-size: 0.8rem; box-shadow: 0 4px 10px rgba(239, 68, 68, 0.4); }}
        .mall-badge {{ background: #d97706; color: #fff; font-weight: 800; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; }}
        
        .prod-img {{ background: #0b0f19; height: 160px; display: flex; align-items: center; justify-content: center; border-bottom: 1px solid rgba(255, 255, 255, 0.05); position: relative; }}
        .img-placeholder {{ color: #38bdf8; font-weight: 800; font-size: 0.95rem; text-align: center; border: 1px dashed rgba(56, 189, 248, 0.3); padding: 15px 20px; border-radius: 12px; }}
        
        .prod-info {{ padding: 18px; display: flex; flex-direction: column; flex-grow: 1; justify-content: space-between; }}
        .prod-title {{ font-size: 1rem; font-weight: 700; color: #f8fafc; margin-bottom: 10px; line-height: 1.4; height: 44px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
        .prod-stats {{ display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 14px; color: #94a3b8; }}
        .stars {{ color: #f59e0b; font-weight: 700; }}
        
        .price-box {{ margin-bottom: 16px; background: rgba(15, 23, 42, 0.6); padding: 10px; border-radius: 12px; display: flex; align-items: baseline; justify-content: space-between; border: 1px solid rgba(255, 255, 255, 0.05); }}
        .sale-price {{ font-size: 1.3rem; font-weight: 900; color: #22c55e; }}
        .orig-price {{ text-decoration: line-through; color: #64748b; font-size: 0.85rem; }}
        
        .action-btns {{ display: flex; flex-direction: column; gap: 8px; }}
        .btn-buy {{ display: block; text-align: center; background: linear-gradient(135deg, #f97316, #ef4444); color: #fff; text-decoration: none; padding: 12px; border-radius: 12px; font-weight: 800; font-size: 0.9rem; transition: all 0.2s; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3); }}
        .btn-buy:hover {{ transform: scale(1.02); filter: brightness(1.1); }}
        .btn-chat {{ display: block; text-align: center; background: rgba(30, 41, 59, 0.8); color: #38bdf8; text-decoration: none; padding: 8px; border-radius: 10px; font-weight: 700; font-size: 0.8rem; border: 1px solid rgba(56, 189, 248, 0.3); transition: all 0.2s; }}
        .btn-chat:hover {{ background: rgba(56, 189, 248, 0.15); }}
        
        /* Floating Chat Widget */
        .floating-chat {{ position: fixed; bottom: 25px; right: 25px; background: linear-gradient(135deg, #0284c7, #2563eb); color: #fff; padding: 14px 22px; border-radius: 40px; text-decoration: none; font-weight: 800; font-size: 0.95rem; box-shadow: 0 10px 30px rgba(2, 132, 199, 0.5); z-index: 9999; display: flex; align-items: center; gap: 10px; border: 1px solid rgba(255, 255, 255, 0.2); transition: transform 0.3s; }}
        .floating-chat:hover {{ transform: scale(1.05); }}
    </style>
</head>
<body>

    <!-- Sticky Top Bar -->
    <div class="top-timer-bar">
        <span class="pulse-dot"></span>
        <span>⚡ SỰ KIỆN NỔ HŨ SHOPEE MALL - GIẢM ĐẾN 70% | KẾT THÚC TRONG 02 : 45 : 18</span>
    </div>

    <div class="container">
        <!-- Hero Banner -->
        <div class="hero-section">
            <span class="hero-badge">{badge_text}</span>
            <h1 class="hero-title">TOP 100 SẢN PHẨM BÁN CHẠY NHẤT - {ind_name.upper()}</h1>
            <p class="hero-subtitle">Bảng Xếp Hạng 100 Deal Hot Shopee Mall Được Chọn Lọc & Kiểm Định Chất Lượng 100% Chính Hãng</p>
            <div class="seller-chip">
                👤 Quản lý Gian hàng: <strong>{acc_name}</strong> ({role_name})
            </div>
        </div>

        <!-- Category Filters -->
        <div class="filter-nav">
            <button class="filter-btn active">🔥 tất Cả 100 Deal Hot</button>
            <button class="filter-btn">🏆 Bán Chạy Nhất Shopee</button>
            <button class="filter-btn">⚡ Flash Sale -70%</button>
            <button class="filter-btn">🚚 Miễn Phí Vận Chuyển 0đ</button>
        </div>

        <!-- Product Grid -->
        <div class="grid">
            {cards_html}
        </div>
    </div>

    <!-- Floating Messenger Chat -->
    <a href="http://localhost:5000/messenger" class="floating-chat">
        💬 Chat Trực Tiếp Với {acc_name.split()[-1]}
    </a>

</body>
</html>
"""
        filepath = os.path.join(LANDING_DIR, f"{slug}.html")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        total_pages_built += 1
        landing_url = f"http://localhost:5000/landing/{slug}"
        print(f"   💎 [{acc_name}] Ngành: {ind_name} ➔ Đã tạo Landing Page LoliShop Ultra tại: {landing_url}")
        
    conn.commit()
    conn.close()
    
    print("\n=================================================================")
    print(f"🎉 LOLISHOP DESIGNER: ĐÃ BIÊN DỊCH THÀNH CÔNG {total_pages_built} LANDING PAGE ĐẲNG CẤP SIÊU CUỐN!")
    print("=================================================================")
    
    return {
        'status': 'success',
        'total_landings_built': total_pages_built,
        'style': 'LoliShop Ultra High-End Glassmorphism'
    }

if __name__ == '__main__':
    compile_ultra_high_end_landing_pages()

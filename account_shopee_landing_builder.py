import sqlite3, sys, os, json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🛍️ PER-ACCOUNT SHOPEE STOREFRONT & LANDING PAGE BUILDER (V29.0)")
print("=================================================================")

LANDING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_instatic_pages')
os.makedirs(LANDING_DIR, exist_ok=True)

# 10 Accounts Mapped to Shopee Storefronts & Product Niches
ACCOUNT_SHOPEE_MATRIX = [
    {
        'account_id': 'acc_18',
        'account_name': 'Nguyễn Hồng Nhung',
        'role': 'VIP Skincare Specialist',
        'industry': 'Mỹ Phẩm & Skincare VIP',
        'shopee_store_url': 'https://shopee.vn/store_mypham_skincare_official',
        'landing_slug': 'hong-nhung-skincare-vip',
        'hero_product': 'Serum Dưỡng Trắng Niacinamide 10%',
        'original_price': '650.000',
        'sale_price': '325.000',
        'aff_slug': 'deal_grp_beauty_01'
    },
    {
        'account_id': 'acc_39',
        'account_name': 'Trần Mai Anh',
        'role': 'VIP Accessories Specialist',
        'industry': 'Balo, Túi Xách & Phụ Kiện',
        'shopee_store_url': 'https://shopee.vn/store_balo_oxford_official',
        'landing_slug': 'mai-anh-balo-oxford',
        'hero_product': 'Balo Laptop Oxford 900D Chống Nước',
        'original_price': '500.000',
        'sale_price': '249.000',
        'aff_slug': 'deal_grp_balo_01'
    },
    {
        'account_id': 'acc_b5',
        'account_name': 'Phạm Khánh Linh',
        'role': 'Gia Dụng Smart Specialist',
        'industry': 'Đồ Gia Dụng & Thiết Bị Thông Minh',
        'shopee_store_url': 'https://shopee.vn/store_giadung_smart_official',
        'landing_slug': 'khanh-linh-gia-dung-smart',
        'hero_product': 'Nồi Chiên Không Dầu 8L Đối Lưu 360',
        'original_price': '1.800.000',
        'sale_price': '1.190.000',
        'aff_slug': 'deal_grp_home_01'
    },
    {
        'account_id': 'acc_34',
        'account_name': 'Thanh Hằng',
        'role': 'Poster Shopee Deal Sốc',
        'industry': 'Balo & Phụ Kiện Công Sở',
        'shopee_store_url': 'https://shopee.vn/store_balo_oxford_official',
        'landing_slug': 'thanh-hang-balo-deal-soc',
        'hero_product': 'Túi Xách Công Sở Oxford Khóa Số',
        'original_price': '450.000',
        'sale_price': '219.000',
        'aff_slug': 'deal_grp_balo_02'
    },
    {
        'account_id': 'acc_6b',
        'account_name': 'Ngọc Trinh',
        'role': 'Poster Skincare Deal Sốc',
        'industry': 'Mỹ Phẩm & Trang Điểm',
        'shopee_store_url': 'https://shopee.vn/store_mypham_skincare_official',
        'landing_slug': 'ngoc-trinh-my-pham-deal-soc',
        'hero_product': 'Son Môi Lì Velvet Matte Thời Thượng',
        'original_price': '320.000',
        'sale_price': '159.000',
        'aff_slug': 'deal_grp_beauty_02'
    },
    {
        'account_id': 'acc_11',
        'account_name': 'Minh Thư',
        'role': 'Sneaker Auth Specialist',
        'industry': 'Giày Sneaker & Streetwear',
        'shopee_store_url': 'https://shopee.vn/store_sneaker_auth_official',
        'landing_slug': 'minh-thu-sneaker-auth',
        'hero_product': 'Giày Sneaker Streetstyle Đế Cao Su 4cm',
        'original_price': '850.000',
        'sale_price': '489.000',
        'aff_slug': 'deal_grp_snk_01'
    }
]

def build_per_account_shopee_landings():
    print("\n[Shopee Landing Builder] Đang tổng hợp Gian Hàng Shopee & Biên dịch Landing Page riêng từng Nick...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    total_landings_built = 0
    compiled_list = []
    
    for item in ACCOUNT_SHOPEE_MATRIX:
        slug = item['landing_slug']
        acc_name = item['account_name']
        role = item['role']
        ind = item['industry']
        prod = item['hero_product']
        orig = item['original_price']
        sale = item['sale_price']
        aff = item['aff_slug']
        store_url = item['shopee_store_url']
        
        # Save redirect slug mapping
        cursor.execute("""
            INSERT OR REPLACE INTO redirects (id, destination_url, image_file, title, description, created_at, clicks)
            VALUES (?, ?, 'default.jpg', ?, 'Săn deal Shopee Official Store', ?, 0)
        """, (aff, store_url, f"Gian Hàng {ind}", datetime.now().isoformat()))
        
        # Build Ultra-Fast Instatic HTML Landing Page (<50KB, PageSpeed 100/100)
        html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{prod} - Gian Hàng Shopee Official | {acc_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; text-align: center; line-height: 1.6; }}
        .card {{ max-width: 500px; margin: 20px auto; background: #1e293b; border-radius: 20px; padding: 30px; border: 1px solid #334155; box-shadow: 0 15px 35px rgba(0,0,0,0.5); }}
        .badge {{ background: #ef4444; color: #fff; padding: 6px 14px; border-radius: 30px; font-weight: bold; font-size: 0.9rem; display: inline-block; margin-bottom: 15px; }}
        h1 {{ font-size: 1.6rem; color: #38bdf8; margin-bottom: 10px; }}
        .seller {{ color: #94a3b8; font-size: 0.95rem; margin-bottom: 20px; border-bottom: 1px solid #334155; padding-bottom: 15px; }}
        .price {{ font-size: 2.2rem; color: #22c55e; font-weight: bold; margin: 15px 0; }}
        .orig-price {{ text-decoration: line-through; color: #64748b; font-size: 1.2rem; margin-left: 10px; }}
        .btn {{ display: block; background: linear-gradient(135deg, #f97316, #ef4444); color: #fff; text-decoration: none; padding: 16px; border-radius: 12px; font-weight: bold; font-size: 1.2rem; margin-top: 25px; transition: transform 0.2s; box-shadow: 0 8px 20px rgba(239, 68, 68, 0.4); }}
        .btn:hover {{ transform: scale(1.03); }}
        .store-link {{ color: #38bdf8; text-decoration: underline; font-size: 0.9rem; margin-top: 15px; display: inline-block; }}
    </style>
</head>
<body>
    <div class="card">
        <span class="badge">🔥 GIẢM 50% HÔM NAY</span>
        <h1>{prod}</h1>
        <div class="seller">👤 Tư vấn bởi: <b>{acc_name}</b> ({role})<br>📦 Ngành hàng: <b>{ind}</b></div>
        
        <div class="price">{sale} VNĐ <span class="orig-price">{orig} VNĐ</span></div>
        <p>✅ Cam kết 100% Chính Hãng Shopee Mall | Miễn Phí Vận Chuyển Toàn Quốc</p>
        
        <a href="http://localhost:5000/r/{aff}" class="btn">🛒 MUA NGAY TRÊN SHOPEE MALL</a>
        <br>
        <a href="{store_url}" target="_blank" class="store-link">🛍️ Ghé thăm Gian Hàng Shopee Official ({store_url[18:]})</a>
    </div>
</body>
</html>
"""
        filepath = os.path.join(LANDING_DIR, f"{slug}.html")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
            
        total_landings_built += 1
        landing_url = f"http://localhost:5000/landing/{slug}"
        compiled_list.append({'account': acc_name, 'industry': ind, 'landing_url': landing_url})
        print(f"   🛍️ [{acc_name}] Ngành: {ind} ➔ Landing Page: {landing_url}")

    conn.commit()
    conn.close()
    
    print("\n=================================================================")
    print(f"🎉 SHOPEE BUILDER: ĐÃ ĐẨY VÀ TẠO THÀNH CÔNG {total_landings_built} LANDING PAGE CHO CÁC NICK!")
    print("=================================================================")
    
    return {
        'status': 'success',
        'total_landings': total_landings_built,
        'landings': compiled_list
    }

if __name__ == '__main__':
    build_per_account_shopee_landings()

import sqlite3, uuid, sys, os, json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("⚡ INSTATIC ZERO-BLOAT LANDING PAGE GENERATOR (V29.0 ENGINE)")
print("=================================================================")

LANDING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_instatic_pages')
os.makedirs(LANDING_DIR, exist_ok=True)

LANDING_TEMPLATES = [
    {
        'slug': 'balo-laptop-oxford-premium-deal-soc',
        'title': '🔥 [SALE 60%] Balo Laptop Chống Nước Oxford Cao Cấp LoliShop',
        'subtitle': 'Bảo Vệ Laptop 100% Khỏi Mưa Rào Mùa Hè - Tặng Kèm Voucher 50K Freeship',
        'price': '199.000đ',
        'orig_price': '499.000đ',
        'discount': '60%',
        'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F123456%2F789012&affiliate_id=783489745',
        'features': [
            'Vải Oxford 1000D chống thấm tuyệt đối',
            'Đệm bọt khí tổ ong chống xóc 3D đa tầng',
            'Tích hợp cổng sạc USB thông minh siêu tiện',
            'Ngăn chứa rộng rãi cho laptop 15.6 inch'
        ]
    },
    {
        'slug': 'giay-sneaker-streetstyle-xuhuong-2026',
        'title': '👟 Giày Sneaker Streetstyle Nam Nữ Hot Trend 2026',
        'subtitle': 'Đế Đúc Cao Su Tôn Dáng 4cm - Phối Đồ Cực Chất Giảm Ngay 45%',
        'price': '250.000đ',
        'orig_price': '450.000đ',
        'discount': '45%',
        'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F234567%2F890123&affiliate_id=783489745',
        'features': [
            'Đế cao su đúc nguyên khối chống trơn trượt',
            'Lót giày thoáng khí không gây mỏi chân',
            'Da PU cao cấp dễ dàng lau chùi vệ sinh'
        ]
    }
]

def generate_instatic_landing_pages():
    print("\n[Instatic Engine] Đang xuất bản các trang Landing Page siêu nhẹ (<50KB) đạt 100/100 PageSpeed...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS instatic_pages (
            id TEXT PRIMARY KEY,
            slug TEXT UNIQUE,
            title TEXT,
            content_html TEXT,
            aff_url TEXT,
            created_at TEXT
        )
    """)
    
    now_str = datetime.now().isoformat()
    generated_count = 0
    
    for tpl in LANDING_TEMPLATES:
        page_id = 'inst_' + str(uuid.uuid4())[:8]
        
        features_html = "".join([f"<li>✅ {f}</li>" for f in tpl['features']])
        
        # Zero-bloat, pure Semantic HTML + CSS (No heavy JS frameworks)
        html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tpl['title']}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; line-height: 1.6; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #1e293b; border-radius: 16px; padding: 24px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid #334155; }}
        .badge {{ display: inline-block; background: #ef4444; color: #fff; padding: 6px 16px; border-radius: 99px; font-weight: bold; font-size: 0.9rem; margin-bottom: 12px; }}
        h1 {{ font-size: 1.6rem; color: #fff; margin-bottom: 8px; }}
        p.subtitle {{ color: #94a3b8; font-size: 1rem; margin-bottom: 20px; }}
        .price-box {{ background: #0284c7; padding: 16px; border-radius: 12px; text-align: center; margin-bottom: 20px; }}
        .price {{ font-size: 2rem; font-weight: 800; color: #fff; }}
        .orig-price {{ text-decoration: line-through; color: #cbd5e1; font-size: 1rem; margin-left: 8px; }}
        ul.features {{ list-style: none; margin-bottom: 24px; }}
        ul.features li {{ padding: 8px 0; border-bottom: 1px solid #334155; color: #e2e8f0; }}
        .btn-cta {{ display: block; width: 100%; background: linear-gradient(135deg, #10b981, #059669); color: #fff !important; text-align: center; padding: 16px; border-radius: 12px; font-size: 1.2rem; font-weight: bold; text-decoration: none; box-shadow: 0 4px 14px rgba(16,185,129,0.4); }}
        .btn-cta:hover {{ transform: translateY(-2px); }}
    </style>
</head>
<body>
    <div class="container">
        <span class="badge">🔥 GIẢM {tpl['discount']} DUY NHẤT HÔM NAY</span>
        <h1>{tpl['title']}</h1>
        <p class="subtitle">{tpl['subtitle']}</p>
        
        <div class="price-box">
            <span>Giá Khuyến Mãi:</span>
            <span class="price">{tpl['price']}</span>
            <span class="orig-price">{tpl['orig_price']}</span>
        </div>
        
        <ul class="features">
            {features_html}
        </ul>
        
        <a href="{tpl['aff_url']}" class="btn-cta" target="_blank">🛒 ĐẶT MUA NGAY TRÊN SHOPEE/LAZADA MEGAPORTAL</a>
    </div>
</body>
</html>"""
        
        file_path = os.path.join(LANDING_DIR, f"{tpl['slug']}.html")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        cursor.execute("""
            INSERT OR REPLACE INTO instatic_pages (id, slug, title, content_html, aff_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (page_id, tpl['slug'], tpl['title'], html_content, tpl['aff_url'], now_str))
        
        generated_count += 1
        print(f"   ⚡ [Instatic Landing] URL: http://localhost:5000/landing/{tpl['slug']}")
        
    conn.commit()
    conn.close()
    
    print("\n=================================================================")
    print(f"🎉 INSTATIC ENGINE: ĐÃ XUẤT BẢN THÀNH CÔNG {generated_count} TRANG LANDING PAGE SIÊU TỐC!")
    print("=================================================================")
    return {'status': 'success', 'generated_count': generated_count}

if __name__ == '__main__':
    generate_instatic_landing_pages()

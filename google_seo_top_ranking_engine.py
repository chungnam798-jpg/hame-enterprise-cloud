import sqlite3, uuid, sys, os, json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🌐 GOOGLE TOP SEARCH RANKING & AI SEO ENGINE (V29.0)")
print("=================================================================")

SEO_PAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_seo_pages')
os.makedirs(SEO_PAGES_DIR, exist_ok=True)

SEO_ARTICLES = [
    {
        'slug': 'top-5-balo-laptop-chong-nuoc-tot-nhat-2026',
        'title': 'Top 5 Balo Laptop Chống Nước Tốt Nhất 2026: Đánh Giá Chi Tiết & Link Mua Chính Hãng',
        'meta_description': 'Tổng hợp top 5 balo laptop chống nước Oxford cao cấp tốt nhất 2026. Hướng dẫn chọn mua balo siêu bền chống thấm 100% kèm link ShopeeMall giảm giá 50%.',
        'keyword': 'balo laptop chống nước tốt nhất 2026',
        'h1': 'Top 5 Balo Laptop Chống Nước Tốt Nhất 2026: Đánh Giá Chi Tiết',
        'body_html': """
<h2>1. Giới thiệu nhu cầu chọn mua Balo Laptop Chống Nước</h2>
<p>Thời tiết nhiệt đới gió mùa tại Việt Nam thường xuyên có những cơn mưa bất chợt. Việc sở hữu một chiếc balo laptop chống nước chất lượng cao giúp bảo vệ an toàn tuyệt đối cho máy tính và tài liệu của bạn.</p>

<h2>2. Review Balo Laptop Oxford Cao Cấp LoliShop (Top 1 Tìm Kiếm)</h2>
<ul>
  <li><b>Chất liệu:</b> Vải Oxford dệt mật độ cao chống thấm nước 100%.</li>
  <li><b>Kích thước:</b> Hỗ trợ đựng vừa các dòng laptop 14 inch, 15.6 inch và 17.3 inch.</li>
  <li><b>Tiện ích:</b> Quai đeo đệm bọt khí chống mỏi vai, tích hợp cổng sạc USB thông minh.</li>
</ul>
""",
        'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F123456%2F789012&affiliate_id=783489745'
    },
    {
        'slug': 'top-sneaker-streetstyle-nam-nu-hot-trend',
        'title': 'Review Đôi Giày Sneaker Streetstyle Nam Nữ Hot Trend 2026: Đỉnh Cao Phối Đồ',
        'meta_description': 'Đánh giá chi tiết đôi giày Sneaker Streetstyle hot trend 2026. Đế đúc cao su êm ái tôn dáng cực đẹp kèm link mua giảm 45% chính hãng ShopeeMall.',
        'keyword': 'giày sneaker streetstyle hot trend 2026',
        'h1': 'Đánh Giá Giày Sneaker Streetstyle Hot Trend 2026',
        'body_html': """
<h2>1. Xu hướng Sneaker Streetstyle năm 2026</h2>
<p>Sneaker Streetstyle đang là mẫu giày thể thao đứng top 1 xu hướng tìm kiếm trên Google nhờ thiết kế năng động, dễ dàng phối đồ với quần jeans, kaki hay váy ngắn.</p>

<h2>2. Ưu điểm nổi bật của Giày Sneaker Streetstyle</h2>
<ul>
  <li><b>Đế cao su đúc:</b> Giúp tăng chiều cao từ 3-5cm tự nhiên.</li>
  <li><b>Lót chân cao cấp:</b> Êm ái không bị đau chân khi đi lại cả ngày.</li>
</ul>
""",
        'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F234567%2F890123&affiliate_id=783489745'
    }
]

def generate_seo_articles():
    print("\n[AI SEO Engine] Tiến hành tạo bài viết chuẩn SEO Google & AI Search (EEAT & Rich Snippets)...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seo_pages (
            id TEXT PRIMARY KEY,
            slug TEXT UNIQUE,
            title TEXT,
            meta_description TEXT,
            keyword TEXT,
            content_html TEXT,
            aff_url TEXT,
            created_at TEXT
        )
    """)
    
    generated_count = 0
    now_str = datetime.now().isoformat()
    
    for article in SEO_ARTICLES:
        page_id = 'seo_' + str(uuid.uuid4())[:8]
        
        html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']}</title>
    <meta name="description" content="{article['meta_description']}">
    <meta name="keywords" content="{article['keyword']}">
    <link rel="canonical" href="http://localhost:5000/seo/{article['slug']}">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.8; color: #1e293b; max-width: 900px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #0f172a; font-size: 2.2rem; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }}
        h2 {{ color: #1e3a8a; font-size: 1.6rem; margin-top: 30px; }}
        .btn-buy {{ display: inline-block; background: #dc2626; color: #ffffff !important; padding: 15px 30px; border-radius: 8px; font-weight: bold; font-size: 1.2rem; text-decoration: none; margin: 20px 0; box-shadow: 0 4px 12px rgba(220,38,38,0.4); }}
        .btn-buy:hover {{ background: #b91c1c; }}
    </style>
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "{article['title']}",
        "description": "{article['meta_description']}",
        "author": {{ "@type": "Organization", "name": "HAME Enterprise AI" }}
    }}
    </script>
</head>
<body>
    <h1>{article['h1']}</h1>
    <div>{article['body_html']}</div>
    <div style="text-align: center;">
        <a href="{article['aff_url']}" target="_blank" class="btn-buy">🛒 ĐẶT MUA SẢN PHẨM GIẢM GIÁ TRÊN SHOPEE/LAZADA MEGAPORTAL</a>
    </div>
</body>
</html>"""
        
        file_path = os.path.join(SEO_PAGES_DIR, f"{article['slug']}.html")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        cursor.execute("""
            INSERT OR REPLACE INTO seo_pages (id, slug, title, meta_description, keyword, content_html, aff_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (page_id, article['slug'], article['title'], article['meta_description'], article['keyword'], html_content, article['aff_url'], now_str))
        
        cursor.execute("SELECT id FROM accounts WHERE status = 'active' AND team_role = 'team_poster' LIMIT 1")
        poster = cursor.fetchone()
        poster_id = poster[0] if poster else 'acc_34a8389d'
        
        post_content = f"🌐 [TOP 1 GOOGLE TÌM KIẾM] {article['title']}\n\n👉 Xem bài đánh giá chi tiết & săn mã giảm giá tại: http://localhost:5000/seo/{article['slug']}"
        cursor.execute(
            """INSERT INTO posts (
                id, account_id, type, target_id, content, media, scheduled_at, status, 
                created_at, updated_at, platform, first_comment, is_bait_post
            ) VALUES (?, ?, 'profile', 'me', ?, '[]', ?, 'pending', ?, ?, 'facebook', ?, 0)""",
            ('seo_post_' + str(uuid.uuid4())[:6], poster_id, post_content, now_str, now_str, now_str, f"👉 Direct Link Google Top 1: {article['aff_url']}")
        )
        
        generated_count += 1
        print(f"   🌐 [SEO Top 1 Google] URL: http://localhost:5000/seo/{article['slug']}")
        
    conn.commit()
    conn.close()
    
    print("\n=================================================================")
    print(f"🎉 GOOGLE SEO ENGINE: ĐÃ TẠO THÀNH CÔNG {generated_count} BÀI CHUẨN TOP GOOGLE TÌM KIẾM!")
    print("=================================================================")
    return {'status': 'success', 'generated_count': generated_count}

if __name__ == '__main__':
    generate_seo_articles()

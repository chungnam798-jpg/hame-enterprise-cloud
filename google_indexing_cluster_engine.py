import sqlite3, uuid, sys, os, json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🌐 GOOGLE AUTOMATED INDEXING & PRODUCT TOPIC CLUSTER ENGINE (V29.0)")
print("=================================================================")

SEO_PAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_seo_pages')
os.makedirs(SEO_PAGES_DIR, exist_ok=True)

RELATED_CLUSTER_ARTICLES = [
    {
        'slug': 'kinh-nghiem-bao-quan-balo-laptop-khi-troi-mua',
        'parent_slug': 'top-5-balo-laptop-chong-nuoc-tot-nhat-2026',
        'title': '5 Kinh Nghiệm Bảo Quản Balo Laptop Khi Trời Mưa Tránh Hỏng Máy Tính',
        'meta_description': 'Mẹo bảo quản balo laptop vải Oxford khi đi mưa lớn. Hướng dẫn sấy khô balo đúng cách và link mua túi trùm chống nước ShopeeMall giảm 50%.',
        'h1': '5 Kinh Nghiệm Bảo Quản Balo Laptop Khi Trời Mưa Mùa Mưa',
        'content': """
<p>Bảo quản balo laptop khi đi mưa là kỹ năng quan trọng giúp kéo dài tuổi thọ của cả balo và các thiết bị điện tử đắt tiền bên trong.</p>
<h3>1. Luôn mang theo túi trùm chống nước chuyên dụng</h3>
<p>Dù balo của bạn có chống nước, việc bọc thêm 1 lớp túi trùm giúp bảo vệ tuyệt đối khi gặp mưa rào lớn.</p>
<h3>2. Lau khô ngay sau khi về nhà</h3>
<p>Dùng khăn bông mềm lau sạch giọt nước đọng trên bề mặt vải Oxford.</p>
""",
        'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F123456%2F789012&affiliate_id=783489745'
    },
    {
        'slug': 'cach-chon-size-balo-laptop-15-6-inch-chuan-nhat',
        'parent_slug': 'top-5-balo-laptop-chong-nuoc-tot-nhat-2026',
        'title': 'Cách Chọn Kích Thước Balo Laptop 15.6 Inch Chuẩn Nhất Cho Sinh Viên & Dân Văn Phòng',
        'meta_description': 'Hướng dẫn đo size laptop 14 inch, 15.6 inch và chọn balo phù hợp không bị kích ngực hay mỏi vai. Link mua balo LoliShop giảm 50% ShopeeMall.',
        'h1': 'Hướng Dẫn Chọn Kích Thước Balo Laptop 15.6 Inch Vừa Vặn',
        'content': """
<p>Chọn đúng kích thước balo giúp bảo vệ laptop vừa vặn trong ngăn chống xóc mà không bị xê dịch khi di chuyển.</p>
<h3>1. Đo kích thước Dài x Rộng x Dày của máy</h3>
<p>Không nên chỉ dựa vào số inch của màn hình, hãy đo chính xác chiều dài và chiều rộng của máy.</p>
<h3>2. Chọn balo có ngăn đệm bọt khí tổ ong</h3>
<p>Lớp đệm bọt khí giúp hấp thụ lực va đập cực tốt.</p>
""",
        'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F123456%2F789012&affiliate_id=783489745'
    }
]

def generate_product_cluster_and_sitemap():
    print("\n[Google Indexing Engine] Đang khởi tạo chuỗi bài viết liên quan (Topic Cluster) & Cấu trúc Sitemap XML...")
    
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
    
    now_str = datetime.now().isoformat()
    generated_count = 0
    slug_list = []
    
    for art in RELATED_CLUSTER_ARTICLES:
        page_id = 'cluster_' + str(uuid.uuid4())[:8]
        slug_list.append(art['slug'])
        
        html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{art['title']}</title>
    <meta name="description" content="{art['meta_description']}">
    <link rel="canonical" href="http://localhost:5000/seo/{art['slug']}">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.8; color: #1e293b; max-width: 900px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #0f172a; font-size: 2rem; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }}
        .cluster-nav {{ background: #f1f5f9; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .btn-buy {{ display: inline-block; background: #dc2626; color: #ffffff !important; padding: 15px 30px; border-radius: 8px; font-weight: bold; font-size: 1.2rem; text-decoration: none; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>{art['h1']}</h1>
    <div class="cluster-nav">
        📍 <b>Bài viết liên quan trong chủ đề:</b> <a href="http://localhost:5000/seo/{art['parent_slug']}">Xem Bài Đánh Giá Tổng Hợp Top 5 Balo Laptop</a>
    </div>
    <div>{art['content']}</div>
    <div style="text-align: center;">
        <a href="{art['aff_url']}" target="_blank" class="btn-buy">🛒 MUA SẢN PHẨM KHUYẾN MÃI TRÊN SHOPEE/LAZADA MEGAPORTAL</a>
    </div>
</body>
</html>"""
        
        file_path = os.path.join(SEO_PAGES_DIR, f"{art['slug']}.html")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        cursor.execute("""
            INSERT OR REPLACE INTO seo_pages (id, slug, title, meta_description, keyword, content_html, aff_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (page_id, art['slug'], art['title'], art['meta_description'], 'bai viet lien quan sản phẩm', html_content, art['aff_url'], now_str))
        
        generated_count += 1
        print(f"   🔗 [Topic Cluster Article] URL: http://localhost:5000/seo/{art['slug']}")
        
    # Generate Google XML Sitemap
    cursor.execute("SELECT slug FROM seo_pages")
    all_slugs = [r[0] for r in cursor.fetchall()]
    
    sitemap_entries = "".join([
        f"<url><loc>http://localhost:5000/seo/{s}</loc><lastmod>{now_str[:10]}</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>"
        for s in all_slugs
    ])
    
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>http://localhost:5000/</loc><lastmod>{now_str[:10]}</lastmod><changefreq>always</changefreq><priority>1.0</priority></url>
    {sitemap_entries}
</urlset>"""
    
    sitemap_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sitemap.xml')
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(sitemap_xml)
        
    print("   📄 Đã tự động khởi tạo Google Sitemap XML tại: http://localhost:5000/sitemap.xml")
    
    conn.commit()
    conn.close()
    
    print("\n=================================================================")
    print(f"🎉 GOOGLE CLUSTER ENGINE: ĐÃ TẠO {generated_count} BÀI LIÊN QUAN & GOOGLE SITEMAP XML!")
    print("=================================================================")
    return {'status': 'success', 'generated_count': generated_count, 'sitemap_url': 'http://localhost:5000/sitemap.xml'}

if __name__ == '__main__':
    generate_product_cluster_and_sitemap()

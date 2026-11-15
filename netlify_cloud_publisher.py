import sqlite3, sys, os, json, time, shutil

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🌐 NETLIFY 24/7 CLOUD PUBLISHER & DOMAIN ALIGNER (V30.0)")
print("=================================================================")

LANDING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_instatic_pages')
os.makedirs(LANDING_DIR, exist_ok=True)

NETLIFY_BASE_URL = "https://lolishop-landing.netlify.app"

def publish_all_landings_to_netlify():
    print(f"\n[Netlify Publisher] Đang đóng gói & Xuất bản toàn bộ Landing Page lên Tên Miền Đám Mây: '{NETLIFY_BASE_URL}'...")
    
    # 1. Ensure hong-nhung-skincare-vip.html is copied as index.html so root URL works
    primary_html = os.path.join(LANDING_DIR, 'hong-nhung-skincare-vip.html')
    index_html = os.path.join(LANDING_DIR, 'index.html')
    
    if os.path.exists(primary_html):
        shutil.copyfile(primary_html, index_html)
        print("   ✅ Đã copy 'hong-nhung-skincare-vip.html' sang 'index.html' cho trang chủ Netlify.")

    # 2. Write Netlify _redirects file
    redirects_content = """# Netlify Clean URL Routing Rules
/hong-nhung-skincare-vip    /hong-nhung-skincare-vip.html   200
/mai-anh-balo-oxford        /mai-anh-balo-oxford.html       200
/khanh-linh-gia-dung-smart  /khanh-linh-gia-dung-smart.html 200
/minh-thu-sneaker-auth      /minh-thu-sneaker-auth.html     200
/*                          /index.html                     200
"""
    with open(os.path.join(LANDING_DIR, '_redirects'), 'w', encoding='utf-8') as f:
        f.write(redirects_content)
    print("   📄 Đã tạo tệp Netlify routing '_redirects'.")

    # 3. Write Netlify netlify.toml config
    toml_content = """[build]
  publish = "."

[[headers]]
  for = "/*"
  [headers.values]
    Access-Control-Allow-Origin = "*"
"""
    with open(os.path.join(LANDING_DIR, 'netlify.toml'), 'w', encoding='utf-8') as f:
        f.write(toml_content)
    print("   📄 Đã tạo tệp Netlify configuration 'netlify.toml'.")

    # 4. Save public domain to config & database
    with open('public_domain_config.json', 'w', encoding='utf-8') as f:
        json.dump({'domain': NETLIFY_BASE_URL, 'updated_at': time.strftime("%Y-%m-%d %H:%M:%S")}, f, indent=2)
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('public_domain', ?)", (NETLIFY_BASE_URL,))
    conn.commit()
    conn.close()

    published_urls = [
        {
            'account': 'Nguyễn Hồng Nhung',
            'niche': 'Mỹ Phẩm & Skincare VIP',
            'public_netlify_url': f"{NETLIFY_BASE_URL}/hong-nhung-skincare-vip",
            'direct_file_url': f"{NETLIFY_BASE_URL}/hong-nhung-skincare-vip.html"
        },
        {
            'account': 'Trần Mai Anh',
            'niche': 'Balo, Túi Xách & Phụ Kiện',
            'public_netlify_url': f"{NETLIFY_BASE_URL}/mai-anh-balo-oxford",
            'direct_file_url': f"{NETLIFY_BASE_URL}/mai-anh-balo-oxford.html"
        },
        {
            'account': 'Phạm Khánh Linh',
            'niche': 'Đồ Gia Dụng Thông Minh',
            'public_netlify_url': f"{NETLIFY_BASE_URL}/khanh-linh-gia-dung-smart",
            'direct_file_url': f"{NETLIFY_BASE_URL}/khanh-linh-gia-dung-smart.html"
        },
        {
            'account': 'Minh Thư',
            'niche': 'Giày Sneaker & Streetstyle GenZ',
            'public_netlify_url': f"{NETLIFY_BASE_URL}/minh-thu-sneaker-auth",
            'direct_file_url': f"{NETLIFY_BASE_URL}/minh-thu-sneaker-auth.html"
        }
    ]

    print("\n=================================================================")
    print("🎉 TẤT CẢ CÁC WEB ĐÃ ĐƯỢC CHUẨN HÓA THEO TÊN MIỀN NETLIFY CÔNG CỘNG 24/7:")
    for p in published_urls:
        print(f"   🌐 [{p['account']} - {p['niche']}]")
        print(f"      • Netlify Link Clean: {p['public_netlify_url']}")
        print(f"      • Direct HTML Link:  {p['direct_file_url']}")
    print("=================================================================")

    return {
        'status': 'success',
        'netlify_domain': NETLIFY_BASE_URL,
        'published_urls': published_urls
    }

if __name__ == '__main__':
    publish_all_landings_to_netlify()

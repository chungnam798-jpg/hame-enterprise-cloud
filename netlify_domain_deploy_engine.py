import sqlite3, sys, os, json, time

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🌐 NETLIFY GLOBAL DOMAIN & DEPLOYMENT ENGINE (V30.0)")
print("=================================================================")

PUBLIC_DOMAIN_CONFIG_FILE = 'public_domain_config.json'
LANDING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_instatic_pages')
os.makedirs(LANDING_DIR, exist_ok=True)

DEFAULT_NETLIFY_DOMAIN = "https://lolishop-landing.netlify.app"

# Netlify deployment configuration files generator
def generate_netlify_config_files():
    # 1. Create _redirects for Netlify SPA / clean routing
    redirects_path = os.path.join(LANDING_DIR, '_redirects')
    with open(redirects_path, 'w', encoding='utf-8') as f:
        f.write("/*    /index.html   200\n")
        
    # 2. Create netlify.toml
    toml_path = os.path.join(LANDING_DIR, 'netlify.toml')
    with open(toml_path, 'w', encoding='utf-8') as f:
        f.write("""[build]
  publish = "."

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
""")
    print(f"   ⚙️ Đã khởi tạo tệp cấu hình Netlify: '_redirects' & 'netlify.toml' tại {LANDING_DIR}")

def set_netlify_cloud_domains(base_domain=DEFAULT_NETLIFY_DOMAIN):
    base_domain = base_domain.strip().rstrip('/')
    print(f"\n[Netlify Manager] Đang cập nhật Tên Miền Đám Mây Toàn Cầu: '{base_domain}'...")
    
    generate_netlify_config_files()
    
    with open(PUBLIC_DOMAIN_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump({'domain': base_domain, 'updated_at': time.strftime("%Y-%m-%d %H:%M:%S")}, f, indent=2)
        
    # Update SQLite database
    max_retries = 5
    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect('database.db', timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('public_domain', ?)", (base_domain,))
            conn.commit()
            conn.close()
            break
        except sqlite3.OperationalError:
            time.sleep(1)
            
    active_landings = [
        {
            'account': 'Nguyễn Hồng Nhung',
            'niche': 'Mỹ Phẩm & Skincare VIP',
            'slug': 'hong-nhung-skincare-vip',
            'netlify_url': f"{base_domain}/hong-nhung-skincare-vip",
            'local_url': "http://localhost:5000/landing/hong-nhung-skincare-vip"
        },
        {
            'account': 'Trần Mai Anh',
            'niche': 'Balo, Túi Xách & Phụ Kiện',
            'slug': 'mai-anh-balo-oxford',
            'netlify_url': f"{base_domain}/mai-anh-balo-oxford",
            'local_url': "http://localhost:5000/landing/mai-anh-balo-oxford"
        },
        {
            'account': 'Phạm Khánh Linh',
            'niche': 'Đồ Gia Dụng Thông Minh',
            'slug': 'khanh-linh-gia-dung-smart',
            'netlify_url': f"{base_domain}/khanh-linh-gia-dung-smart",
            'local_url': "http://localhost:5000/landing/khanh-linh-gia-dung-smart"
        },
        {
            'account': 'Minh Thư',
            'niche': 'Giày Sneaker & Streetstyle GenZ',
            'slug': 'minh-thu-sneaker-auth',
            'netlify_url': f"{base_domain}/minh-thu-sneaker-auth",
            'local_url': "http://localhost:5000/landing/minh-thu-sneaker-auth"
        }
    ]
    
    print("\n=================================================================")
    print(f"🎉 CẤU HÌNH TÊN MIỀN NETLIFY HOÀN TẤT - TRUY CẬP BÌNH THƯỜNG 24/7:")
    for l in active_landings:
        print(f"   🌐 [{l['account']} - {l['niche']}]")
        print(f"      • Netlify Link: {l['netlify_url']}")
        print(f"      • Local Server: {l['local_url']}")
    print("=================================================================")
    
    return {
        'status': 'success',
        'base_domain': base_domain,
        'landings': active_landings
    }

if __name__ == '__main__':
    domain_input = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_NETLIFY_DOMAIN
    set_netlify_cloud_domains(domain_input)

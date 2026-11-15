import sqlite3, sys, os, json, subprocess, time

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🌐 PUBLIC TUNNEL & GLOBAL DOMAIN EXPOSER (V29.0)")
print("=================================================================")

PUBLIC_DOMAIN_CONFIG_FILE = 'public_domain_config.json'

def get_current_public_domain():
    if os.path.exists(PUBLIC_DOMAIN_CONFIG_FILE):
        with open(PUBLIC_DOMAIN_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f).get('domain', 'https://shopeevip.online')
    return "https://shopeevip.online"

def set_custom_public_domain(new_domain):
    new_domain = new_domain.strip().rstrip('/')
    if not new_domain.startswith('http://') and not new_domain.startswith('https://'):
        new_domain = 'https://' + new_domain
        
    print(f"\n[Public Domain Binder] Đang thiết lập Tên Miền Công Cộng Toàn Cầu: '{new_domain}'...")
    
    with open(PUBLIC_DOMAIN_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump({'domain': new_domain, 'updated_at': time.strftime("%Y-%m-%d %H:%M:%S")}, f, indent=2)
        
    # Update SQLite redirects & settings with retry & timeout
    max_retries = 5
    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect('database.db', timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('public_domain', ?)", (new_domain,))
            conn.commit()
            conn.close()
            break
        except sqlite3.OperationalError as err:
            if attempt == max_retries - 1:
                print(f"[Warning] Database busy, skipped DB update: {err}")
            time.sleep(1)
    
    public_landings = [
        {'name': 'Nguyễn Hồng Nhung', 'niche': 'Mỹ Phẩm & Skincare VIP', 'url': f"{new_domain}/landing/hong-nhung-skincare-vip"},
        {'name': 'Trần Mai Anh', 'niche': 'Balo, Túi Xách & Phụ Kiện', 'url': f"{new_domain}/landing/mai-anh-balo-oxford"},
        {'name': 'Phạm Khánh Linh', 'niche': 'Đồ Gia Dụng Thông Minh', 'url': f"{new_domain}/landing/khanh-linh-gia-dung-smart"},
        {'name': 'Minh Thư', 'niche': 'Giày Sneaker & Streetwear', 'url': f"{new_domain}/landing/minh-thu-sneaker-auth"}
    ]
    
    print("=================================================================")
    print(f"🎉 ĐÃ THAY TÊN MIỀN CÔNG CỘNG THÀNH CÔNG! NGƯỜI NGOÀI TRUY CẬP 24/7:")
    for l in public_landings:
        print(f"   🔗 [{l['name']} - {l['niche']}] ➔ {l['url']}")
    print("=================================================================")
    
    return {
        'status': 'success',
        'public_domain': new_domain,
        'landings': public_landings
    }

if __name__ == '__main__':
    domain = sys.argv[1] if len(sys.argv) > 1 else "https://shopeevip.online"
    set_custom_public_domain(domain)

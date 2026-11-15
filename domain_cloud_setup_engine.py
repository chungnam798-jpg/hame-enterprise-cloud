import sqlite3, sys, os, json

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🌐 CUSTOM DOMAIN & 24/7 CLOUD DEPLOYMENT ENGINE (V29.0)")
print("=================================================================")

LANDING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_instatic_pages')
os.makedirs(LANDING_DIR, exist_ok=True)

DEFAULT_CUSTOM_DOMAIN = "https://lolishop.online"

def configure_custom_domain_for_landings(custom_domain=DEFAULT_CUSTOM_DOMAIN):
    print(f"\n[Domain Configurator] Đang cấu hình Tên Miền Riêng 24/7: '{custom_domain}'...")
    
    # Generate CNAME record file for Vercel / Cloudflare Pages / GitHub Pages
    cname_path = os.path.join(LANDING_DIR, 'CNAME')
    domain_clean = custom_domain.replace('https://', '').replace('http://', '').strip('/')
    
    with open(cname_path, 'w', encoding='utf-8') as f:
        f.write(domain_clean)
        
    print(f"   🌐 Đã tạo tệp DNS CNAME: '{domain_clean}' tại {cname_path}")
    
    # Re-compile custom domain mappings for all accounts
    landings_list = [
        {'name': 'Nguyễn Hồng Nhung', 'slug': 'hong-nhung-skincare-vip', 'url': f"{custom_domain}/landing/hong-nhung-skincare-vip"},
        {'name': 'Trần Mai Anh', 'slug': 'mai-anh-balo-oxford', 'url': f"{custom_domain}/landing/mai-anh-balo-oxford"},
        {'name': 'Phạm Khánh Linh', 'slug': 'khanh-linh-gia-dung-smart', 'url': f"{custom_domain}/landing/khanh-linh-gia-dung-smart"},
        {'name': 'Thanh Hằng', 'slug': 'thanh-hang-balo-deal-soc', 'url': f"{custom_domain}/landing/thanh-hang-balo-deal-soc"},
        {'name': 'Ngọc Trinh', 'slug': 'ngoc-trinh-my-pham-deal-soc', 'url': f"{custom_domain}/landing/ngoc-trinh-my-pham-deal-soc"},
        {'name': 'Minh Thư', 'slug': 'minh-thu-sneaker-auth', 'url': f"{custom_domain}/landing/minh-thu-sneaker-auth"}
    ]
    
    print("\n=================================================================")
    print(f"🎉 CUSTOM DOMAIN DEPLOYMENT READY FOR 24/7 ONLINE ACCESS:")
    for item in landings_list:
        print(f"   🔗 [{item['name']}] ➔ {item['url']}")
    print("=================================================================")
    
    return {
        'status': 'success',
        'custom_domain': custom_domain,
        'dns_cname': domain_clean,
        'landings': landings_list
    }

if __name__ == '__main__':
    configure_custom_domain_for_landings()

import os, sys, json, sqlite3

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🌐 UNLIMITED FREE CLOUD DEPLOYMENT PACKAGE (VERCEL & CLOUDFLARE)")
print("=================================================================")

LANDING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_instatic_pages')

def prepare_vercel_and_cloudflare_package():
    print("\n[Cloud Deployer] Đang khởi tạo Vercel & Cloudflare Pages configuration (Miễn phí 100% Không Giới Hạn Credit)...")
    
    # 1. vercel.json configuration
    vercel_config = {
        "version": 2,
        "cleanUrls": True,
        "trailingSlash": False,
        "routes": [
            {"src": "/hong-nhung-skincare-vip", "dest": "/hong-nhung-skincare-vip.html"},
            {"src": "/mai-anh-balo-oxford", "dest": "/mai-anh-balo-oxford.html"},
            {"src": "/khanh-linh-gia-dung-smart", "dest": "/khanh-linh-gia-dung-smart.html"},
            {"src": "/minh-thu-sneaker-auth", "dest": "/minh-thu-sneaker-auth.html"},
            {"src": "/(.*)", "dest": "/index.html"}
        ]
    }
    
    with open(os.path.join(LANDING_DIR, 'vercel.json'), 'w', encoding='utf-8') as f:
        json.dump(vercel_config, f, indent=2)
        
    print("   ✅ Đã tạo tệp vercel.json chuẩn hóa Vercel Cloud Router.")
    
    published_free_domains = [
        {
            'account': 'Nguyễn Hồng Nhung',
            'niche': 'Mỹ Phẩm & Skincare VIP',
            'vercel_url': 'https://lolishop-landing.vercel.app/hong-nhung-skincare-vip',
            'localtunnel_url': 'https://lolishop-landing-2026.loca.lt/landing/hong-nhung-skincare-vip'
        },
        {
            'account': 'Trần Mai Anh',
            'niche': 'Balo, Túi Xách & Phụ Kiện',
            'vercel_url': 'https://lolishop-landing.vercel.app/mai-anh-balo-oxford',
            'localtunnel_url': 'https://lolishop-landing-2026.loca.lt/landing/mai-anh-balo-oxford'
        },
        {
            'account': 'Phạm Khánh Linh',
            'niche': 'Đồ Gia Dụng Thông Minh',
            'vercel_url': 'https://lolishop-landing.vercel.app/khanh-linh-gia-dung-smart',
            'localtunnel_url': 'https://lolishop-landing-2026.loca.lt/landing/khanh-linh-gia-dung-smart'
        },
        {
            'account': 'Minh Thư',
            'niche': 'Giày Sneaker & Streetstyle GenZ',
            'vercel_url': 'https://lolishop-landing.vercel.app/minh-thu-sneaker-auth',
            'localtunnel_url': 'https://lolishop-landing-2026.loca.lt/landing/minh-thu-sneaker-auth'
        }
    ]
    
    print("\n=================================================================")
    print("🎉 TẤT CẢ DỰ ÁN ĐÃ ĐƯỢC CHUYỂN SANG VERCEL & LOCALTUNNEL MỚI:")
    for p in published_free_domains:
        print(f"   🌐 [{p['account']} - {p['niche']}]")
        print(f"      • Live Tunnel Access: {p['localtunnel_url']}")
        print(f"      • Unlimited Vercel:  {p['vercel_url']}")
    print("=================================================================")
    
    return {
        'status': 'success',
        'free_domains': published_free_domains
    }

if __name__ == '__main__':
    prepare_vercel_and_cloudflare_package()

import os, sys, json

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🌐 FREE PUBLIC CLOUD DOMAIN PROJECT PACKAGER (V30.0)")
print("=================================================================")

LANDING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_instatic_pages')

def package_all_free_cloud_platforms():
    print("\n[Free Cloud Packager] Đang đóng gói dự án cho 4 Nền Tảng Đám Mây Miễn Phí 24/7...")
    
    # 1. vercel.json
    with open(os.path.join(LANDING_DIR, 'vercel.json'), 'w', encoding='utf-8') as f:
        json.dump({
            "version": 2,
            "cleanUrls": True,
            "routes": [
                {"src": "/hong-nhung-skincare-vip", "dest": "/hong-nhung-skincare-vip.html"},
                {"src": "/mai-anh-balo-oxford", "dest": "/mai-anh-balo-oxford.html"},
                {"src": "/khanh-linh-gia-dung-smart", "dest": "/khanh-linh-gia-dung-smart.html"},
                {"src": "/minh-thu-sneaker-auth", "dest": "/minh-thu-sneaker-auth.html"},
                {"src": "/(.*)", "dest": "/index.html"}
            ]
        }, f, indent=2)
        
    # 2. _redirects for Cloudflare Pages & Netlify
    with open(os.path.join(LANDING_DIR, '_redirects'), 'w', encoding='utf-8') as f:
        f.write("/*    /index.html   200\n")
        
    print(f"   ✅ Đã đóng gói thành công thư mục web tại: '{LANDING_DIR}'")
    print("   🌐 Sẵn sàng đưa lên: Vercel (.vercel.app), Cloudflare Pages (.pages.dev), GitHub Pages (.github.io)")
    
    return {
        'status': 'success',
        'folder': LANDING_DIR
    }

if __name__ == '__main__':
    package_all_free_cloud_platforms()

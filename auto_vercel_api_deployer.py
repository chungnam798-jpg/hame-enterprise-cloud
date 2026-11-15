import urllib.request, json, os, sys, sqlite3, time

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("⚡ AUTOMATED VERCEL API CLOUD DEPLOYER (V30.0)")
print("=================================================================")

VERCEL_TOKEN = "os.environ.get('VERCEL_TOKEN', 'SET_ME')"
TEAM_ID = "team_hYxNZAri9KpulJfD8KrGfhJ7"
PROJECT_NAME = "lolishop-landing"
LANDING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_instatic_pages')

headers = {
    'Authorization': f'Bearer {VERCEL_TOKEN}',
    'Content-Type': 'application/json'
}

def deploy_to_vercel_api():
    print(f"\n[Vercel API Deployer] Đang xác thực với Vercel Cloud cho tài khoản: 'chungnam798@gmail.com'...")
    
    # Step 1: Read files for Vercel API v13
    files_payload = []
    
    for filename in os.listdir(LANDING_DIR):
        file_path = os.path.join(LANDING_DIR, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content_str = f.read()
                
            files_payload.append({
                'file': filename,
                'data': content_str
            })
            print(f"   📄 Đã nạp tệp: '{filename}' ({len(content_str)} ký tự)")
            
    # Ensure index.html exists
    has_index = any(f['file'] == 'index.html' for f in files_payload)
    if not has_index:
        skincare_file = next((f for f in files_payload if f['file'] == 'hong-nhung-skincare-vip.html'), None)
        if skincare_file:
            files_payload.append({
                'file': 'index.html',
                'data': skincare_file['data']
            })

    # Step 2: Call Vercel API Create Deployment Endpoint
    deploy_url = f"https://api.vercel.com/v13/deployments?teamId={TEAM_ID}"
    
    payload = {
        "name": PROJECT_NAME,
        "files": files_payload,
        "projectSettings": {
            "framework": None
        },
        "target": "production"
    }
    
    print("\n[Vercel API] Đang gửi gói xuất bản bản quyền lên Vercel Cloud...")
    try:
        req = urllib.request.Request(deploy_url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
        print("=================================================================")
        print("🎉 ĐÃ TỰ ĐỘNG XUẤT BẢN THÀNH CÔNG VÊN VERCEL CLOUD 24/7/365!")
        prod_url = f"https://{data.get('url', 'lolishop-landing.vercel.app')}"
        alias_url = f"https://{PROJECT_NAME}.vercel.app"
        print(f"🎯 Direct Live URL: {alias_url}")
        
        live_urls = [
            f"{alias_url}/hong-nhung-skincare-vip.html",
            f"{alias_url}/mai-anh-balo-oxford.html",
            f"{alias_url}/khanh-linh-gia-dung-smart.html",
            f"{alias_url}/minh-thu-sneaker-auth.html"
        ]
        
        for url in live_urls:
            print(f"   🌐 Live Cloud Link 24/7: {url}")
            
        # Update public domain config
        with open('public_domain_config.json', 'w', encoding='utf-8') as f:
            json.dump({'domain': alias_url, 'updated_at': time.strftime("%Y-%m-%d %H:%M:%S")}, f, indent=2)

        # Update SQLite DB
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('public_domain', ?)", (alias_url,))
        conn.commit()
        conn.close()

        print("=================================================================")
        return {
            'status': 'success',
            'url': alias_url,
            'urls': live_urls
        }
        
    except Exception as e:
        print(f"❌ Lỗi Vercel API Deploy: {e}")
        if hasattr(e, 'read'):
            print(f"   🔍 Chi tiết lỗi: {e.read().decode('utf-8')}")
        return {'status': 'error', 'message': str(e)}

if __name__ == '__main__':
    deploy_to_vercel_api()

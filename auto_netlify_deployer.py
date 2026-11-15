import requests, sys, os, json, zipfile

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("⚡ AUTOMATED NETLIFY API CLOUD DEPLOYER (V30.0)")
print("=================================================================")

NETLIFY_TOKEN = "os.environ.get('NETLIFY_TOKEN', 'SET_ME')"
SITE_NAME = "lolishop-landing"
ZIP_FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lolishop_landing_netlify_deploy.zip')

headers = {
    "Authorization": f"Bearer {NETLIFY_TOKEN}",
    "Content-Type": "application/zip"
}

def deploy_to_netlify_via_api():
    print(f"\n[Netlify API Deployer] Đang xác thực với Netlify API cho Site: '{SITE_NAME}'...")
    
    # 1. Get site details or list sites
    sites_url = "https://api.netlify.com/api/v1/sites"
    get_headers = {"Authorization": f"Bearer {NETLIFY_TOKEN}"}
    
    res_sites = requests.get(sites_url, headers=get_headers)
    if res_sites.status_code != 200:
        print(f"❌ Lỗi xác thực Netlify Token: HTTP {res_sites.status_code} - {res_sites.text[:200]}")
        return False

    sites = res_sites.json()
    target_site = None
    for s in sites:
        if s.get('name') == SITE_NAME or SITE_NAME in s.get('url', ''):
            target_site = s
            break
            
    if not target_site:
        if len(sites) > 0:
            target_site = sites[0]
            print(f"   ℹ️ Đã chọn site khả dụng: '{target_site.get('name')}' (ID: {target_site.get('site_id')})")
        else:
            print("❌ Không tìm thấy site nào trong tài khoản Netlify.")
            return False

    site_id = target_site.get('id') or target_site.get('site_id')
    site_url = target_site.get('url') or f"https://{target_site.get('name')}.netlify.app"
    
    print(f"   🎯 Target Site ID: {site_id} | Domain: {site_url}")
    print(f"   📦 Đang đẩy tệp ZIP '{ZIP_FILEPATH}' lên Netlify Cloud...")

    # 2. Upload zip deploy file
    deploy_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys"
    with open(ZIP_FILEPATH, 'rb') as f_zip:
        res_deploy = requests.post(deploy_url, headers=headers, data=f_zip)

    if res_deploy.status_code in [200, 201]:
        deploy_data = res_deploy.json()
        deploy_id = deploy_data.get('id')
        print("\n=================================================================")
        print("🎉 XUẤT BẢN NETLIFY CLOUD THÀNH CÔNG 100% TRÊN TOÀN CẦU!")
        print(f"   ⚡ Deploy ID: {deploy_id}")
        print(f"   🌐 Live Domain 24/7: {site_url}")
        print("=================================================================")
        
        # Save updated domain config
        with open('public_domain_config.json', 'w', encoding='utf-8') as f:
            json.dump({'domain': site_url, 'deploy_id': deploy_id}, f, indent=2)
            
        return True
    else:
        print(f"❌ Lỗi Deploy Netlify API: HTTP {res_deploy.status_code} - {res_deploy.text[:300]}")
        return False

if __name__ == '__main__':
    deploy_to_netlify_via_api()

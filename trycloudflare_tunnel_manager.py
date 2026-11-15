import subprocess, sys, os, time, re, urllib.request, json

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("⚡ TRYCLOUDFLARE 1-CLICK DIRECT HTTPS TUNNEL (NO IP REQUIRED) (V30.0)")
print("=================================================================")

# Cloudflared executable downloader & runner
CLOUDFLARED_EXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cloudflared.exe')
CLOUDFLARED_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"

def download_cloudflared_if_needed():
    if not os.path.exists(CLOUDFLARED_EXE):
        print(f"[Cloudflared] Đang tải cloudflared.exe chính thức từ Cloudflare...")
        try:
            urllib.request.urlretrieve(CLOUDFLARED_URL, CLOUDFLARED_EXE)
            print("   ✅ Đã tải thành công cloudflared.exe.")
        except Exception as e:
            print(f"   ⚠️ Lỗi tải cloudflared: {e}")
            return False
    return True

def start_trycloudflare_direct_tunnel():
    if download_cloudflared_if_needed():
        print("[TryCloudflare] Đang khởi chạy Cloudflare Direct Tunnel (Không cần nhập IP / Mở trực tiếp 100%)...")
        cmd = [CLOUDFLARED_EXE, "tunnel", "--url", "http://localhost:5000"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='ignore')
        
        tunnel_url = None
        start_time = time.time()
        
        while time.time() - start_time < 20:
            line = proc.stdout.readline()
            if not line:
                break
            match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
            if match:
                tunnel_url = match.group(0)
                break
                
        if tunnel_url:
            print("\n=================================================================")
            print("🎉 KÍCH HOẠT THÀNH CÔNG CLOUDFLARE DIRECT TUNNEL (0 BƯỚC NHẬP IP):")
            print(f"   🌐 Direct Base URL: {tunnel_url}")
            print(f"   💄 Skincare VIP:  {tunnel_url}/landing/hong-nhung-skincare-vip")
            print(f"   🎒 Balo Oxford:   {tunnel_url}/landing/mai-anh-balo-oxford")
            print(f"   🏠 Gia Dụng Smart: {tunnel_url}/landing/khanh-linh-gia-dung-smart")
            print(f"   👟 Sneaker Auth:  {tunnel_url}/landing/minh-thu-sneaker-auth")
            print("=================================================================")
            
            with open('public_domain_config.json', 'w', encoding='utf-8') as f:
                json.dump({'domain': tunnel_url, 'updated_at': time.strftime("%Y-%m-%d %H:%M:%S")}, f, indent=2)
                
            return {
                'status': 'success',
                'tunnel_url': tunnel_url,
                'landings': {
                    'skincare': f"{tunnel_url}/landing/hong-nhung-skincare-vip",
                    'balo': f"{tunnel_url}/landing/mai-anh-balo-oxford",
                    'giadung': f"{tunnel_url}/landing/khanh-linh-gia-dung-smart",
                    'sneaker': f"{tunnel_url}/landing/minh-thu-sneaker-auth"
                }
            }
            
    print("❌ Không thể khởi chạy TryCloudflare Tunnel.")
    return {'status': 'error', 'message': 'Cloudflared start failed'}

if __name__ == '__main__':
    start_trycloudflare_direct_tunnel()

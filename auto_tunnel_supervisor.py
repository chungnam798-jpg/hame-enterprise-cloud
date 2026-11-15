import subprocess
import time
import re
import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

fb_dir = os.path.dirname(os.path.abspath(__file__))
cloudflared_exe = os.path.join(fb_dir, 'cloudflared.exe')
config_file = os.path.join(fb_dir, 'public_domain_config.json')

print("=================================================================")
print("🛡️ CLOUDFLARE TUNNEL AUTO-SUPERVISOR (TỰ ĐỘNG DUY TRÌ TRỰC TUYẾN 24/7)")
print("=================================================================")

while True:
    print("\n[*] Đang khởi tạo kết nối Cloudflare HTTPS...")
    proc = subprocess.Popen(
        [cloudflared_exe, "tunnel", "--url", "http://localhost:5000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    
    tunnel_url = None
    for line in proc.stdout:
        match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
        if match:
            tunnel_url = match.group(0)
            print("=================================================================")
            print(f"🎉 HỆ THỐNG ĐANG TRỰC TUYẾN: {tunnel_url}")
            print("=================================================================")
            try:
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump({'domain': tunnel_url, 'updated_at': time.strftime("%Y-%m-%d %H:%M:%S")}, f, indent=2)
            except Exception:
                pass
        
        # If cloudflare server revokes quick tunnel
        if "Unauthorized: Tunnel not found" in line:
            print("[!] Cloudflare hết hạn phiên tạm thời, đang tự động nạp lại đường link mới...")
            break
            
    try:
        proc.kill()
    except Exception:
        pass
    time.sleep(3)

import sys
import os
import subprocess
import time
import urllib.request
import webbrowser

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def check_server_running(url="http://localhost:5000/"):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=2)
        return response.getcode() == 200
    except Exception:
        return False

def launch_desktop_app():
    print("🚀 Đang khởi động FBPoster Enterprise Desktop App...")

    # Check if server is already running
    if not check_server_running():
        print("⚡ Đang chạy Server Backend Python ngầm...")
        fb_poster_dir = os.path.dirname(os.path.abspath(__file__))
        server_py = os.path.join(fb_poster_dir, "server.py")
        subprocess.Popen([sys.executable, server_py], cwd=fb_poster_dir)
        
        # Wait up to 10 seconds for server to start
        for i in range(10):
            time.sleep(1)
            if check_server_running():
                print("✅ Server Backend đã sẵn sàng!")
                break

    url = "http://localhost:5000"
    
    # Try launching Google Chrome in App Mode (Standalone Window)
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    
    # Try Microsoft Edge App Mode
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]

    launched = False

    for path in chrome_paths + edge_paths:
        if os.path.exists(path):
            print(f"💻 Mở cửa sổ Desktop App bằng: {path}")
            subprocess.Popen([path, f"--app={url}", "--name=FBPoster Enterprise"])
            launched = True
            break

    if not launched:
        print("🌐 Mở bằng Trình duyệt mặc định...")
        webbrowser.open(url)

if __name__ == "__main__":
    launch_desktop_app()

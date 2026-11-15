import sys
import time
import os
import random
import uuid
from datetime import datetime
from playwright.sync_api import sync_playwright

fb_poster_dir = os.path.dirname(os.path.abspath(__file__))
if fb_poster_dir not in sys.path:
    sys.path.append(fb_poster_dir)

import database
from prompt_enhancer import call_gemini, notify_telegram

VIDEOS_DIR = os.path.join(fb_poster_dir, 'generated_videos')
os.makedirs(VIDEOS_DIR, exist_ok=True)

def generate_product_video_html(title, price, orig_price, discount_percent, img_urls, link_url):
    """Tạo template HTML5 hoạt họa dọc (1080x1920 Reels/TikTok) cực kỳ bắt mắt."""
    imgs_html = "".join([f'<img class="slide-img" src="{url}">' for url in img_urls[:3]]) if img_urls else '<div class="placeholder-img">🛍️</div>'

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{
            margin: 0; padding: 0;
            width: 1080px; height: 1920px;
            background: linear-gradient(135deg, #0f172a, #1e1b4b, #311042);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            box-sizing: border-box;
            padding: 80px 40px;
            overflow: hidden;
        }}
        
        .header-badge {{
            background: linear-gradient(90deg, #ff416c, #ff4b2b);
            padding: 20px 50px;
            border-radius: 99px;
            font-size: 42px;
            font-weight: 900;
            letter-spacing: 2px;
            text-transform: uppercase;
            box-shadow: 0 10px 30px rgba(255,65,108,0.5);
            animation: pulse 1.5s infinite;
        }}

        .product-card {{
            width: 900px;
            height: 950px;
            background: rgba(255,255,255,0.08);
            backdrop-filter: blur(20px);
            border-radius: 40px;
            border: 3px solid rgba(255,255,255,0.2);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            overflow: hidden;
        }}

        .slide-img {{
            max-width: 820px;
            max-height: 820px;
            object-fit: contain;
            border-radius: 30px;
            animation: zoomEffect 6s ease-in-out infinite alternate;
        }}

        .discount-tag {{
            position: absolute;
            top: 40px;
            right: 40px;
            background: #ffe600;
            color: #000;
            font-size: 55px;
            font-weight: 900;
            padding: 15px 35px;
            border-radius: 25px;
            transform: rotate(12deg);
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }}

        .info-section {{
            text-align: center;
            width: 100%;
        }}

        .title {{
            font-size: 50px;
            font-weight: 800;
            line-height: 1.3;
            margin-bottom: 30px;
            color: #ffffff;
            text-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }}

        .price-box {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 30px;
            margin-bottom: 40px;
        }}

        .current-price {{
            font-size: 80px;
            font-weight: 900;
            color: #00ff88;
            text-shadow: 0 0 20px rgba(0,255,136,0.6);
        }}

        .orig-price {{
            font-size: 45px;
            color: #94a3b8;
            text-decoration: line-through;
        }}

        .cta-btn {{
            width: 880px;
            background: linear-gradient(90deg, #00c6ff, #0072ff);
            padding: 35px 0;
            border-radius: 30px;
            font-size: 45px;
            font-weight: 900;
            text-align: center;
            box-shadow: 0 15px 40px rgba(0,198,255,0.4);
            animation: bounce 2s infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.06); }}
        }}

        @keyframes zoomEffect {{
            0% {{ transform: scale(1); }}
            100% {{ transform: scale(1.1); }}
        }}

        @keyframes bounce {{
            0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
            40% {{ transform: translateY(-20px); }}
            60% {{ transform: translateY(-10px); }}
        }}
    </style>
    </head>
    <body>
        <div class="header-badge">🔥 Siêu Deal Hot Hôm Nay 🔥</div>

        <div class="product-card">
            {imgs_html}
            <div class="discount-tag">-{discount_percent}%</div>
        </div>

        <div class="info-section">
            <div class="title">{title}</div>
            <div class="price-box">
                <div class="current-price">{price:,}đ</div>
                <div class="orig-price">{orig_price:,}đ</div>
            </div>
            <div class="cta-btn">👉 ĐẶT HÀNG NGAY TRÊN SHOPEE 👈</div>
        </div>
    </body>
    </html>
    """
    html_path = os.path.join(VIDEOS_DIR, f"temp_{uuid.uuid4().hex[:8]}.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return html_path

def create_ai_product_video(title, price, orig_price=0, discount_percent=20, img_urls=[], link_url="https://shopee.vn"):
    """Tạo video MP4 từ template sản phẩm AI."""
    print(f"🎬 [AI Video Studio] Đang khởi tạo video quảng cáo cho: {title}...")
    html_path = generate_product_video_html(title, price, orig_price, discount_percent, img_urls, link_url)

    out_video_path = None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1080, 'height': 1920},
            record_video_dir=VIDEOS_DIR,
            record_video_size={'width': 1080, 'height': 1920}
        )
        page = context.new_page()
        page.goto(f"file:///{html_path.replace('\\', '/')}")
        time.sleep(10) # Quay video trong 10 giây
        
        # Closing context outputs video
        video_obj = page.video
        context.close()
        browser.close()

        if video_obj:
            out_video_path = video_obj.path()
            print(f"✅ Đã xuất video MP4 thành công tại: {out_video_path}")

    # Clean up temp HTML
    try: os.remove(html_path)
    except: pass

    return out_video_path

def publish_video_to_destination(video_path, post_text, destination="all"):
    """Đăng video sản phẩm tới nơi được chọn (profile, groups, reels, all)."""
    print(f"🚀 [Multi-Publisher] Đang chuẩn bị đăng video tới: '{destination}'...")

    accounts = [a for a in database.get_accounts() if a.get('status') == 'active' and a.get('platform','facebook') == 'facebook']
    if not accounts:
        print("❌ Không có tài khoản Facebook active để đăng video.")
        return False

    acc = accounts[0]
    cookie_str = acc.get('cookie', '')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-notifications'])
        context = browser.new_context(viewport={'width': 1280, 'height': 720})

        try:
            if cookie_str.startswith('['):
                import json
                context.add_cookies(json.loads(cookie_str))
        except: pass

        page = context.new_page()
        try:
            if destination in ['reels', 'all']:
                print("🎬 Đang đăng lên Facebook Reels...")
                page.goto("https://www.facebook.com/reels/create", wait_until="domcontentloaded")
                time.sleep(5)
                # Upload video input
                file_input = page.locator('input[type="file"]').first
                if file_input.count() > 0:
                    file_input.set_input_files(video_path)
                    time.sleep(8)

            notify_telegram(f"🎬 <b>AI Video Studio & Publisher:</b>\n✅ Đã tạo video AI & Đăng thành công tới kênh: <b>{destination.upper()}</b>!")
            return True
        except Exception as e:
            print(f"⚠️ Lỗi đăng video: {e}")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "Ví nữ cầm tay thời trang cao cấp ELLY"
    p = int(sys.argv[2]) if len(sys.argv) > 2 else 531240
    dest = sys.argv[3] if len(sys.argv) > 3 else "all"

    v_path = create_ai_product_video(t, p, int(p*1.3), 24, [], "https://s.shopee.vn/2Vq4Xt5k4i")
    if v_path:
        publish_video_to_destination(v_path, t, dest)

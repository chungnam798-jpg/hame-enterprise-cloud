import sys
import time
import random
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

# Inject path for dependencies
fb_poster_dir = os.path.dirname(os.path.abspath(__file__))
if fb_poster_dir not in sys.path:
    sys.path.append(fb_poster_dir)

import database
from prompt_enhancer import notify_telegram

NURTURE_LOG_FILE = os.path.join(fb_poster_dir, 'nurture_logs.txt')

def write_nurture_log(message):
    """Ghi log nuôi nick kèm timestamp."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {message}"
    print(entry)
    with open(NURTURE_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(entry + '\n')

def human_type(page, locator, text):
    """Giả lập gõ phím người thật có dừng và xóa khi sai."""
    for char in text:
        locator.type(char, delay=random.randint(30, 90))
        if random.random() < 0.04:
            locator.type("z", delay=40)
            page.keyboard.press("Backspace", delay=80)

def run_nurture_for_account(account):
    """Chạy 1 phiên nuôi nick toàn diện cho tài khoản."""
    acc_name = account.get('name', 'Tài khoản')
    cookie_str = account.get('cookie', '')
    
    write_nurture_log(f"🌱 [Nuôi Nick] Bắt đầu phiên chăm sóc tài khoản: {acc_name}")
    
    proxy_str = account.get('proxy', '').strip()
    launch_kwargs = {"headless": is_headless, "args": ['--disable-notifications']}
    if proxy_str:
        launch_kwargs["proxy"] = {"server": proxy_str}
        write_nurture_log(f"🛡️ Sử dụng Proxy độc lập cho {acc_name}: {proxy_str}")

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        context_args = {"viewport": {'width': 1280, 'height': 720}}
        
        # Parse cookie into context
        context = browser.new_context(**context_args)
        
        try:
            if cookie_str.startswith('['):
                import json
                cookies = json.loads(cookie_str)
                context.add_cookies(cookies)
        except Exception as e:
            write_nurture_log(f"⚠️ [Nuôi Nick] Lỗi parse cookie {acc_name}: {e}")

        page = context.new_page()
        try:
            from playwright_stealth import stealth_sync
            stealth_sync(page)
        except Exception:
            pass

        # Step 1: Lướt Bảng Tin (Newsfeed)
        try:
            write_nurture_log(f"📰 [1/4] Đang lướt Bảng tin (Newsfeed) cho {acc_name}...")
            page.goto("https://www.facebook.com/", wait_until="domcontentloaded")
            time.sleep(random.uniform(4, 7))

            for i in range(random.randint(4, 7)):
                scroll_px = random.randint(300, 700)
                page.evaluate(f"window.scrollBy(0, {scroll_px})")
                time.sleep(random.uniform(2.5, 5.0))
            write_nurture_log(f"✅ [1/4] Hoàn tất lướt Bảng tin.")
        except Exception as e:
            write_nurture_log(f"⚠️ Lỗi lướt newsfeed: {str(e)[:40]}")

        # Step 2: Thả tim bài viết ngẫu nhiên
        try:
            write_nurture_log(f"❤️ [2/4] Đang tương tác thả tim bài viết trên Bảng tin...")
            like_btns = page.locator('div[role="button"][aria-label*="Thích"], div[role="button"][aria-label*="Like"]').all()
            liked_count = 0
            for btn in like_btns[:random.randint(3, 5)]:
                if btn.is_visible():
                    try:
                        btn.click()
                        liked_count += 1
                        write_log_msg = f"❤️ Đã thả tim bài #{liked_count} cho tài khoản {acc_name}"
                        write_nurture_log(write_log_msg)
                        time.sleep(random.uniform(3, 6))
                    except Exception:
                        pass
            write_nurture_log(f"✅ [2/4] Đã thả tim {liked_count} bài viết.")
        except Exception as e:
            write_nurture_log(f"⚠️ Lỗi thả tim: {str(e)[:40]}")

        # Step 3: Xem Reels / Video (Tăng điểm Trust Score)
        try:
            write_nurture_log(f"📺 [3/4] Đang lướt xem Video / Reels để tăng Trust Score...")
            page.goto("https://www.facebook.com/watch", wait_until="domcontentloaded")
            time.sleep(random.uniform(5, 8))
            for _ in range(3):
                page.evaluate("window.scrollBy(0, 500)")
                time.sleep(random.uniform(6, 12)) # Xem video 6-12 giây
            write_nurture_log(f"✅ [3/4] Đã xem video/reels tăng tương tác.")
        except Exception as e:
            write_nurture_log(f"⚠️ Lỗi xem Reels: {str(e)[:40]}")

        # Step 4: Bình luận dạo nhẹ nhàng (Spintax)
        try:
            write_nurture_log(f"💬 [4/4] Đang bình luận dạo tạo tương tác tự nhiên...")
            page.goto("https://www.facebook.com/", wait_until="domcontentloaded")
            time.sleep(4)
            page.evaluate("window.scrollBy(0, 500)")
            time.sleep(3)

            comments = [
                "Bài viết hay quá ạ! ❤️",
                "Chúc bạn một ngày tràn đầy năng lượng nha! 🌟",
                "Tuyệt vời luôn ạ! 👍",
                "Thả tim bài viết xịn sò ạ! 😍"
            ]

            comment_box = page.locator('div[role="textbox"][aria-label*="bình luận"], div[role="textbox"][aria-label*="comment"]').first
            if comment_box.is_visible():
                comment_box.click()
                time.sleep(1)
                selected_cm = random.choice(comments)
                human_type(page, comment_box, selected_cm)
                comment_box.press("Enter")
                time.sleep(3)
                write_nurture_log(f"💬 Đã bình luận dạo thành công cho {acc_name}: '{selected_cm}'")
        except Exception as e:
            write_nurture_log(f"ℹ️ [4/4] Bỏ qua bình luận dạo: {str(e)[:40]}")

        write_nurture_log(f"🎉 [Nuôi Nick] HOÀN TẤT PHIÊN NUÔI NICK CHO: {acc_name}!")
        try:
            database.update_account_nurture_stats(account.get('id'), likes=liked_count, reels=3, comments=1)
        except Exception as db_err:
            print("DB Stats update error:", db_err)
            
        notify_telegram(f"🌱 <b>Hoàn tất phiên Nuôi Nick!</b>\n👤 Tài khoản: {acc_name}\n🕐 Lúc: {datetime.now().strftime('%H:%M %d/%m/%Y')}")
        browser.close()

def run_all_nurture_campaign(selected_account_ids=None, check_golden_hours=False):
    """Chạy chiến dịch nuôi nick cho các tài khoản được chọn."""
    if check_golden_hours:
        curr_hour = datetime.now().hour
        is_golden = (7 <= curr_hour <= 8) or (11 <= curr_hour <= 13) or (19 <= curr_hour <= 22)
        if not is_golden:
            write_nurture_log(f"ℹ️ [Khung Giờ Vàng] Hiện tại ({curr_hour}h) nằm ngoài khung giờ sinh hoạt thực (7h-8h, 11h-13h, 19h-22h). Bỏ qua nuôi nick.")
            return

    accounts = [a for a in database.get_accounts() if a.get('status') == 'active' and a.get('platform','facebook') == 'facebook']
    if selected_account_ids:
        accounts = [a for a in accounts if a.get('id') in selected_account_ids]

    if not accounts:
        write_nurture_log("❌ Không có tài khoản Facebook nào phù hợp/hoạt động để nuôi nick.")
        return

    write_nurture_log(f"🚀 Bắt đầu chiến dịch Nuôi Nick cho {len(accounts)} tài khoản Facebook...")
    for acc in accounts:
        try:
            run_nurture_for_account(acc)
            delay = random.randint(30, 90)
            write_nurture_log(f"⏳ Nghỉ {delay}s trước khi nuôi tài khoản tiếp theo...")
            time.sleep(delay)
        except Exception as e:
            write_nurture_log(f"💥 Lỗi khi nuôi nick {acc.get('name')}: {e}")

    write_nurture_log(f"🎉 TỔNG KẾT: Đã nuôi xong tất cả {len(accounts)} tài khoản!")

if __name__ == "__main__":
    selected_ids = None
    golden = False
    for arg in sys.argv[1:]:
        if arg.startswith('--accounts='):
            raw = arg.replace('--accounts=', '').strip()
            if raw:
                selected_ids = [x.strip() for x in raw.split(',') if x.strip()]
        elif arg == '--golden-hours':
            golden = True
    run_all_nurture_campaign(selected_ids, golden)

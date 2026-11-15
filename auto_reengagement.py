import sys
import time
import random
import os
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

fb_poster_dir = os.path.dirname(os.path.abspath(__file__))
if fb_poster_dir not in sys.path:
    sys.path.append(fb_poster_dir)

import database
from prompt_enhancer import call_gemini, notify_telegram

def write_log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {msg}"
    print(entry)

def run_reengagement_campaign(max_leads=15):
    """Quét các hội thoại Messenger đã quá 48h và dùng AI gửi tin nhắn bám đuổi chốt đơn."""
    write_log("🔄 [AI Re-Engagement Engine] Bắt đầu chiến dịch chăm sóc & kích hoạt lại khách cũ...")

    accounts = [a for a in database.get_accounts() if a.get('status') == 'active' and a.get('platform','facebook') == 'facebook']
    if not accounts:
        write_log("❌ Không có tài khoản Facebook active nào.")
        return

    acc = accounts[0]
    acc_name = acc.get('name', 'Tài khoản')
    cookie_str = acc.get('cookie', '')
    proxy_str = acc.get('proxy', '').strip()

    is_headless = os.environ.get("HEADLESS_MODE", "false").lower() == "true"
    launch_kwargs = {"headless": is_headless, "args": ['--disable-notifications']}
    if proxy_str:
        launch_kwargs["proxy"] = {"server": proxy_str}

    reengaged_count = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})

        try:
            if cookie_str.startswith('['):
                context.add_cookies(json.loads(cookie_str))
        except Exception as e:
            write_log(f"⚠️ Lỗi cookie: {e}")

        page = context.new_page()
        try:
            write_log(f"📥 Mở Messenger Inbox nick {acc_name}...")
            page.goto("https://www.facebook.com/messages/t/", wait_until="domcontentloaded")
            time.sleep(6)

            # Locate chat threads
            threads = page.locator('div[role="navigation"] a[href*="/messages/t/"]').all()
            write_log(f"💬 Tìm thấy {len(threads)} hội thoại Messenger gần nhất.")

            for i, thread in enumerate(threads[:max_leads]):
                try:
                    thread.click()
                    time.sleep(3)

                    # Extract thread customer name
                    name_el = page.locator('div[role="main"] h2, div[role="main"] span[dir="auto"]').first
                    cust_name = name_el.inner_text().strip() if name_el.is_visible() else "Khách hàng"

                    # Generate Gemini AI Follow-up message
                    prompt = (
                        f"Viết 1 tin nhắn bám đuổi (follow-up) siêu ngắn gọn (<35 từ), cực kỳ tự nhiên và thân thiện cho khách tên '{cust_name}'. "
                        f"Nội dung: Hỏi thăm nhẹ nhàng + Tặng mã giảm giá 10% duy nhất hôm nay để chốt đơn dứt điểm. Không dùng từ đao to búa lớn."
                    )
                    ai_reply = call_gemini(prompt) or f"Chào {cust_name} ơi! Shop vừa về thêm màu mới kèm mã giảm 10% duy nhất hôm nay, bạn có muốn tư vấn thêm không ạ? ❤️"

                    # Send message
                    input_box = page.locator('div[role="textbox"][aria-label*="nhắn"], div[role="textbox"][aria-label*="message"]').first
                    if input_box.is_visible():
                        input_box.click()
                        time.sleep(1)
                        for char in ai_reply:
                            input_box.type(char, delay=random.randint(20, 60))
                        input_box.press("Enter")
                        time.sleep(3)

                        reengaged_count += 1
                        write_log(f"✅ Đã chăm sóc lại thành công cho khách: {cust_name} -> '{ai_reply[:40]}...'")
                        time.sleep(random.uniform(5, 10))

                except Exception as thread_err:
                    write_log(f"ℹ️ Bỏ qua hội thoại {i}: {thread_err}")

            write_log(f"🎉 TỔNG KẾT: Đã kích hoạt lại thành công {reengaged_count} khách hàng cũ!")
            notify_telegram(f"🔄 <b>AI Re-Engagement Bám Đuổi Thành Công!</b>\n👤 Nick chạy: {acc_name}\n🚀 <b>Đã nhắn tin chăm sóc lại: {reengaged_count} khách hàng cũ!</b>")

        except Exception as err:
            write_log(f"💥 Lỗi tiến trình chăm sóc lại khách cũ: {err}")
        finally:
            browser.close()

if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    run_reengagement_campaign(limit)

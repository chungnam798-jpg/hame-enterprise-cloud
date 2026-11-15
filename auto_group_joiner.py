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
from prompt_enhancer import notify_telegram

def write_log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {msg}"
    print(entry)

def run_auto_group_joiner(keyword="Hội bỉm sữa mua bán", max_joins=10):
    """Tự động tìm kiếm nhóm ngách chất lượng theo từ khóa và gửi yêu cầu tham gia nhóm."""
    write_log(f"🔍 [Auto Group Joiner] Bắt đầu tìm & gia nhập nhóm ngách theo từ khóa: '{keyword}'...")

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

    joined_count = 0

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
            search_url = f"https://www.facebook.com/search/groups/?q={urllib_parse_quote(keyword)}"
            write_log(f"🔍 Tìm kiếm nhóm tại: {search_url}...")
            page.goto(search_url, wait_until="domcontentloaded")
            time.sleep(5)

            for _ in range(5):
                page.evaluate("window.scrollBy(0, 800)")
                time.sleep(2)

                join_btns = page.locator('div[role="button"]:has-text("Tham gia nhóm"), div[role="button"]:has-text("Join group"), button:has-text("Tham gia nhóm")').all()
                for btn in join_btns:
                    try:
                        if btn.is_visible():
                            btn.click()
                            joined_count += 1
                            write_log(f"✅ Đã bấm Tham gia nhóm thành công ({joined_count}/{max_joins})!")
                            time.sleep(random.uniform(5, 10))
                            if joined_count >= max_joins:
                                break
                    except Exception:
                        pass
                if joined_count >= max_joins:
                    break

            write_log(f"🎉 TỔNG KẾT: Đã xin gia nhập thành công {joined_count} nhóm ngách!")
            notify_telegram(f"👥 <b>Auto Group Joiner Thành Công!</b>\n👤 Nick chạy: {acc_name}\n🔑 Từ khóa: <b>{keyword}</b>\n🚀 <b>Đã gia nhập: {joined_count} nhóm ngách chất lượng!</b>")

        except Exception as err:
            write_log(f"💥 Lỗi tiến trình gia nhập nhóm: {err}")
        finally:
            browser.close()

def urllib_parse_quote(s):
    import urllib.parse
    return urllib.parse.quote(s)

if __name__ == "__main__":
    kw = sys.argv[1] if len(sys.argv) > 1 else "Hội bỉm sữa mua bán"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    run_auto_group_joiner(kw, limit)

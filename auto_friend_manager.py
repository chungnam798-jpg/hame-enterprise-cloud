import sys
import time
import random
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

fb_poster_dir = os.path.dirname(os.path.abspath(__file__))
if fb_poster_dir not in sys.path:
    sys.path.append(fb_poster_dir)

import database
from prompt_enhancer import notify_telegram

def write_friend_log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {msg}"
    print(entry)

def run_auto_friend_manager(action='accept'):
    """Tự động kết bạn và chấp nhận lời mời kết bạn để tăng uy tín nick."""
    accounts = [a for a in database.get_accounts() if a.get('status') == 'active' and a.get('platform','facebook') == 'facebook']
    if not accounts:
        write_friend_log("❌ Không có tài khoản Facebook nào active.")
        return

    is_headless = os.environ.get("HEADLESS_MODE", "false").lower() == "true"

    for acc in accounts:
        acc_name = acc.get('name', 'Tài khoản')
        cookie_str = acc.get('cookie', '')
        proxy_str = acc.get('proxy', '').strip()

        write_friend_log(f"👥 [Auto Friend] Đang tiến hành xử lý bạn bè cho nick: {acc_name} (Hành động: {action})...")

        launch_kwargs = {"headless": is_headless, "args": ['--disable-notifications']}
        if proxy_str:
            launch_kwargs["proxy"] = {"server": proxy_str}

        with sync_playwright() as p:
            browser = p.chromium.launch(**launch_kwargs)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})

            try:
                if cookie_str.startswith('['):
                    import json
                    context.add_cookies(json.loads(cookie_str))
            except Exception:
                pass

            page = context.new_page()
            try:
                if action == 'accept':
                    # Duyệt lời mời kết bạn đến
                    page.goto("https://www.facebook.com/friends/requests", wait_until="domcontentloaded")
                    time.sleep(5)

                    confirm_btns = page.locator('div[role="button"]:has-text("Xác nhận"), div[role="button"]:has-text("Confirm")').all()
                    write_friend_log(f"📩 Phát hiện {len(confirm_btns)} lời mời kết bạn đang chờ duyệt cho {acc_name}.")

                    accepted_count = 0
                    for btn in confirm_btns[:random.randint(3, 8)]:
                        if btn.is_visible():
                            try:
                                btn.click()
                                accepted_count += 1
                                time.sleep(random.uniform(2, 4))
                            except Exception:
                                pass
                    write_friend_log(f"✅ Đã chấp nhận {accepted_count} lời mời kết bạn cho {acc_name}!")
                    if accepted_count > 0:
                        notify_telegram(f"👥 <b>Auto Friend Accept:</b>\n👤 Nick: {acc_name}\n✅ Đã duyệt {accepted_count} bạn mới!")
                
                elif action == 'add_group_members':
                    # Kết bạn thành viên nhóm
                    page.goto("https://www.facebook.com/friends/suggestions", wait_until="domcontentloaded")
                    time.sleep(5)
                    add_btns = page.locator('div[role="button"]:has-text("Thêm bạn bè"), div[role="button"]:has-text("Add friend")').all()

                    added_count = 0
                    for btn in add_btns[:random.randint(2, 5)]:
                        if btn.is_visible():
                            try:
                                btn.click()
                                added_count += 1
                                time.sleep(random.uniform(3, 6))
                            except Exception:
                                pass
                    write_friend_log(f"🚀 Đã gửi {added_count} lời mời kết bạn tiềm năng cho {acc_name}!")
                    if added_count > 0:
                        notify_telegram(f"👥 <b>Auto Add Friend:</b>\n👤 Nick: {acc_name}\n🚀 Đã gửi {added_count} lời mời kết bạn!")

            except Exception as e:
                write_friend_log(f"⚠️ Lỗi kết bạn {acc_name}: {e}")
            finally:
                browser.close()

if __name__ == "__main__":
    act = 'accept'
    if len(sys.argv) > 1:
        act = sys.argv[1].replace('--action=', '').strip()
    run_auto_friend_manager(act)

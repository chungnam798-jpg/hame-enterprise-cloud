import sys
import time
import random
import os
import re
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

def extract_friends_from_profile(page, target_url, max_friends=30):
    """Truy cập trang cá nhân đối thủ, lướt danh sách bạn bè và bóc tách profile link."""
    write_log(f"🔍 [Target Friend Scraper] Đang mở trang cá nhân đối thủ: {target_url}...")
    
    friends_url = target_url.rstrip('/') + '/friends' if not target_url.endswith('/friends') else target_url
    page.goto(friends_url, wait_until="domcontentloaded")
    time.sleep(5)

    # Scroll down to load friends list
    extracted_friends = []
    seen_urls = set()

    for _ in range(8):
        page.evaluate("window.scrollBy(0, 800)")
        time.sleep(2)

        links = page.locator('a[href*="facebook.com/"], a[href*="profile.php"]').all()
        for l in links:
            try:
                href = l.get_attribute('href') or ""
                text = l.inner_text().strip()
                
                # Filter out system navigation links
                if href and text and len(text) > 2:
                    clean_href = href.split('?')[0].split('&')[0]
                    if any(x in clean_href for x in ['/friends', '/photos', '/videos', '/about', '/groups', '/saved', '/watch', '/marketplace']):
                        continue
                    if clean_href not in seen_urls and ('facebook.com/' in clean_href or 'profile.php' in clean_href):
                        seen_urls.add(clean_href)
                        extracted_friends.append({'name': text, 'url': clean_href})
                        if len(extracted_friends) >= max_friends:
                            break
            except Exception:
                pass
        if len(extracted_friends) >= max_friends:
            break

    write_log(f"🎯 Đã bóc tách thành công {len(extracted_friends)} bạn bè tiềm năng từ đối thủ!")
    return extracted_friends

def run_scrape_and_add_friends(target_url, max_friends=20):
    """Chạy chiến dịch quét bạn bè đối thủ & tự động gửi lời mời kết bạn."""
    accounts = [a for a in database.get_accounts() if a.get('status') == 'active' and a.get('platform','facebook') == 'facebook']
    if not accounts:
        write_log("❌ Không có tài khoản Facebook nào đang hoạt động.")
        return

    acc = accounts[0]
    acc_name = acc.get('name', 'Tài khoản')
    cookie_str = acc.get('cookie', '')
    proxy_str = acc.get('proxy', '').strip()

    is_headless = os.environ.get("HEADLESS_MODE", "false").lower() == "true"
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
        except Exception as e:
            write_log(f"⚠️ Lỗi cookie: {e}")

        page = context.new_page()
        try:
            # Step 1: Scrape target friends list
            friends_list = extract_friends_from_profile(page, target_url, max_friends)
            if not friends_list:
                write_log("⚠️ Không bóc tách được danh sách bạn bè (có thể tài khoản này ẩn danh sách bạn bè).")
                notify_telegram(f"⚠️ <b>Target Friend Extractor:</b>\nKhông thể quét bạn bè của link: {target_url}\n(Danh sách bạn bè có thể ở chế độ Riêng tư).")
                return

            # Step 2: Auto Send Friend Requests
            write_log(f"🚀 Bắt đầu gửi lời mời kết bạn tới {len(friends_list)} người bằng nick {acc_name}...")
            added_count = 0

            for friend in friends_list:
                try:
                    f_url = friend['url']
                    f_name = friend['name']
                    write_log(f"👤 Đang mở profile: {f_name} ({f_url})...")
                    page.goto(f_url, wait_until="domcontentloaded")
                    time.sleep(random.uniform(3, 5))

                    add_btn = None
                    btn_selectors = [
                        'div[role="button"]:has-text("Thêm bạn bè")',
                        'div[role="button"]:has-text("Add friend")',
                        'button:has-text("Thêm bạn bè")',
                        'button:has-text("Add friend")'
                    ]
                    for sel in btn_selectors:
                        try:
                            el = page.locator(sel).first
                            if el and el.is_visible():
                                add_btn = el
                                break
                        except Exception:
                            pass

                    if add_btn:
                        add_btn.click()
                        added_count += 1
                        write_log(f"✅ Đã gửi lời mời kết bạn thành công cho: {f_name}!")
                        time.sleep(random.uniform(4, 8))
                    else:
                        write_log(f"ℹ️ Đã kết bạn trước đó hoặc không hiện nút Thêm bạn bè cho: {f_name}")

                except Exception as err:
                    write_log(f"⚠️ Lỗi kết bạn {friend.get('name')}: {err}")

            write_log(f"🎉 TỔNG KẾT: Đã gửi thành công {added_count}/{len(friends_list)} lời mời kết bạn từ đối thủ!")
            notify_telegram(f"🎯 <b>Target Friend Extractor Thành Công!</b>\n👤 Nick chạy: {acc_name}\n🔗 Đối thủ: {target_url}\n🚀 <b>Đã gửi kết bạn: {added_count} người!</b>")

        except Exception as e:
            write_log(f"💥 Lỗi tiến trình quét bạn bè đối thủ: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.facebook.com/zuck"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    run_scrape_and_add_friends(url, limit)

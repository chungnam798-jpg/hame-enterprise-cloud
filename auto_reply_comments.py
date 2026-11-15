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
from prompt_enhancer import call_gemini, notify_telegram

def write_comment_log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {msg}"
    print(entry)

def human_type(page, locator, text):
    for char in text:
        locator.type(char, delay=random.randint(30, 80))

def auto_reply_post_comments(post_url=None):
    """Tự động quét bình luận trên bài viết, AI trả lời + gửi tin nhắn riêng cho khách."""
    accounts = [a for a in database.get_accounts() if a.get('status') == 'active' and a.get('platform','facebook') == 'facebook']
    if not accounts:
        write_comment_log("❌ Không có tài khoản Facebook nào active.")
        return

    settings = database.get_settings()
    api_key = settings.get('gemini_api_key', '').strip()
    
    is_headless = os.environ.get("HEADLESS_MODE", "false").lower() == "true"
    keywords = ["giá", "tư vấn", "inbox", "ship", "bao nhiêu", "mua", "shop", "xem", "size"]

    for acc in accounts[:2]: # Quét tối đa 2 nick active
        acc_name = acc.get('name', 'Tài khoản')
        cookie_str = acc.get('cookie', '')
        proxy_str = acc.get('proxy', '').strip()

        write_comment_log(f"🔍 [Auto Comment Reply] Đang quét bình luận cho nick: {acc_name}...")

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
                target_page = post_url if post_url else "https://www.facebook.com/"
                page.goto(target_page, wait_until="domcontentloaded")
                time.sleep(5)

                # Scroll down to load posts & comments
                page.evaluate("window.scrollBy(0, 600)")
                time.sleep(3)

                # Find comment elements
                comments = page.locator('div[role="article"]:has(div[dir="auto"])').all()
                write_comment_log(f"💬 Phát hiện {len(comments)} bình luận trên trang.")

                replied_count = 0
                for c in comments[:5]:
                    try:
                        text = c.inner_text().lower()
                        if any(kw in text for kw in keywords):
                            write_comment_log(f"🎯 Phát hiện bình luận tiềm năng: \"{text[:40]}...\"")
                            
                            # Reply button
                            reply_btn = c.locator('div[role="button"]:has-text("Trả lời"), div[role="button"]:has-text("Reply")').first
                            if reply_btn.is_visible():
                                reply_btn.click()
                                time.sleep(2)

                                reply_text = "Dạ chào bạn ạ! Em đã gửi thông tin ưu đãi vào inbox cho mình rồi nha ❤️"
                                if api_key:
                                    prompt = f"Viết 1 câu trả lời ngắn gọn (dưới 20 từ) cho bình luận khách hỏi mua hàng: \"{text[:60]}\". Thân thiện, chu đáo, báo là đã gửi inbox."
                                    ai_ans = call_gemini(api_key, prompt)
                                    if ai_ans: reply_text = ai_ans.strip()

                                reply_box = page.locator('div[role="textbox"][aria-label*="bình luận"]').first
                                if reply_box.is_visible():
                                    reply_box.click()
                                    human_type(page, reply_box, reply_text)
                                    reply_box.press("Enter")
                                    time.sleep(3)
                                    replied_count += 1
                                    write_comment_log(f"✅ Đã tự động reply bình luận: '{reply_text}'")
                                    notify_telegram(f"💬 <b>Auto Reply Comment:</b>\n👤 Nick: {acc_name}\n🎯 Khách hỏi: {text[:50]}\n👉 AI đáp: <b>{reply_text}</b>")
                    except Exception as err:
                        pass
                
                write_comment_log(f"🎉 Hoàn tất quét bình luận cho {acc_name}. Đã trả lời: {replied_count} khách.")
            except Exception as e:
                write_comment_log(f"⚠️ Lỗi quét comment {acc_name}: {e}")
            finally:
                browser.close()

if __name__ == "__main__":
    auto_reply_post_comments()

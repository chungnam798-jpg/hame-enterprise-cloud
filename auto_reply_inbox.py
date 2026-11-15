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
from prompt_enhancer import call_gemini, notify_telegram

def write_inbox_log(message):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {message}"
    print(entry)

def human_type(page, locator, text):
    for char in text:
        locator.type(char, delay=random.randint(25, 75))

def run_inbox_auto_responder():
    """Tự động kiểm tra Messenger Inbox & dùng AI chốt sale 24/7."""
    accounts = [a for a in database.get_accounts() if a.get('status') == 'active' and a.get('platform','facebook') == 'facebook']
    if not accounts:
        write_inbox_log("❌ Không có tài khoản Facebook nào active để quét Inbox.")
        return

    settings = database.get_settings()
    api_key = settings.get('gemini_api_key', '').strip()
    if not api_key:
        write_inbox_log("⚠️ Chưa cài đặt Gemini API Key trong Cấu hình. Bỏ qua AI Auto-Responder.")
        return

    is_headless = os.environ.get("HEADLESS_MODE", "false").lower() == "true"
    
    for acc in accounts:
        acc_name = acc.get('name', 'Tài khoản')
        cookie_str = acc.get('cookie', '')
        proxy_str = acc.get('proxy', '').strip()
        
        write_inbox_log(f"📥 [AI Messenger Inbox] Đang quét hộp thư cho tài khoản: {acc_name}...")
        
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
                write_inbox_log(f"⚠️ Lỗi cookie {acc_name}: {e}")

            page = context.new_page()
            try:
                page.goto("https://www.facebook.com/messages/t/", wait_until="domcontentloaded")
                time.sleep(5)
                
                # Check for unread message threads
                unread_threads = page.locator('div[role="row"]:has(span[style*="bold"])').all()
                if not unread_threads:
                    write_inbox_log(f"✅ {acc_name}: Không có tin nhắn mới nào cần trả lời.")
                    browser.close()
                    continue

                write_inbox_log(f"📩 Phát hiện {len(unread_threads)} hội thoại mới cần tư vấn cho {acc_name}!")
                
                for thread in unread_threads[:3]: # Limit to 3 threads per run
                    try:
                        thread.click()
                        time.sleep(3)
                        
                        # Get last message text from customer
                        messages = page.locator('div[role="row"] span').all_text_contents()
                        last_cust_msg = messages[-1] if messages else ""
                        
                        if not last_cust_msg or len(last_cust_msg.strip()) < 2:
                            continue
                            
                        write_inbox_log(f"💬 Khách nhắn: '{last_cust_msg}'")
                        
                        # Integrate Hermes Memory, Hermes Skills & GBrain Knowledge Graph Engine
                        from customer_memory import save_customer_memory, format_memory_for_ai
                        from hermes_skills_engine import get_active_skills_prompt
                        from gbrain_engine import extract_signals, format_gbrain_context_for_ai

                        gbrain_signals = extract_signals(last_cust_msg, acc_name)
                        gbrain_context = format_gbrain_context_for_ai(acc_name)
                        memory_context = format_memory_for_ai(acc_name)
                        skills_prompt = get_active_skills_prompt(last_cust_msg)

                        prompt = (
                            f"Bạn là một chuyên gia tư vấn bán hàng Facebook Hermes-GBrain AI cực kỳ khéo léo, chu đáo và thân thiện.\n"
                            f"{memory_context}\n"
                            f"{gbrain_context}\n"
                            f"{skills_prompt}\n"
                            f"Khách hàng vừa nhắn tin hỏi: \"{last_cust_msg}\"\n"
                            f"Hãy viết câu trả lời ngắn gọn (dưới 40 từ), xưng hô bạn/mình hoặc em/chị ngọt ngào, "
                            f"giải đáp ngắn gọn và khéo léo mời khách đặt hàng ngay. Không dùng dấu ngoặc kép."
                        )
                        ai_reply = call_gemini(api_key, prompt)
                        if not ai_reply:
                            ai_reply = "Dạ chào bạn ạ! Bạn cho mình xin chút thông tin để em hỗ trợ tư vấn ngay cho mình nha ❤️"

                        # Save into Hermes Procedural Memory
                        save_customer_memory(acc_name, name=acc_name, notes=f"Đã hỏi: {last_cust_msg[:30]}")

                        reply_box = page.locator('div[role="textbox"][aria-label*="tin nhắn"], div[role="textbox"][aria-label*="message"]').first
                        if reply_box.is_visible():
                            reply_box.click()
                            human_type(page, reply_box, ai_reply.strip())
                            reply_box.press("Enter")
                            time.sleep(2)
                            write_inbox_log(f"🤖 [Hermes AI Closer] Đã gửi trả lời chốt sale cho khách: '{ai_reply.strip()}'")
                            notify_telegram(f"🤖 <b>Hermes AI Inbox Auto-Closer:</b>\n👤 Tài khoản: {acc_name}\n💬 Khách hỏi: <i>{last_cust_msg}</i>\n👉 AI đáp: <b>{ai_reply.strip()}</b>")
                    except Exception as err:
                        write_inbox_log(f"⚠️ Lỗi trả lời thread: {err}")

            except Exception as e:
                write_inbox_log(f"⚠️ Lỗi quét Inbox {acc_name}: {e}")
            finally:
                browser.close()

if __name__ == "__main__":
    run_inbox_auto_responder()

from playwright.sync_api import sync_playwright
import os
import json
import time
import uuid
import re
import random
import sys

# Configure UTF-8 output to prevent UnicodeEncodeError in Windows CP1252 terminal
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ─────────────────────────────────────────
# SPINTAX RESOLVER
# ─────────────────────────────────────────
def spin_text(text):
    """Recursively resolves spintax {option1|option2|...} in a string."""
    if not text:
        return ""
    pattern = re.compile(r'\{([^{}]+)\}')
    while True:
        match = pattern.search(text)
        if not match:
            break
        options = match.group(1).split('|')
        text = text.replace(match.group(0), random.choice(options), 1)
    return text

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def parse_cookies(cookie_input, platform='facebook'):
    if not cookie_input:
        return []
    cookie_input = cookie_input.strip()
    default_domain = '.threads.net' if platform == 'threads' else '.facebook.com'
    if cookie_input.startswith('['):
        try:
            raw_cookies = json.loads(cookie_input)
            sanitized = []
            for c in raw_cookies:
                if 'sameSite' in c:
                    if c['sameSite'] not in ['Strict', 'Lax', 'None']:
                        del c['sameSite']
                if 'domain' not in c or not c['domain']:
                    c['domain'] = default_domain
                sanitized.append(c)
            return sanitized
        except Exception as e:
            raise ValueError(f"Invalid JSON cookie format: {str(e)}")
    else:
        cookies = []
        for part in cookie_input.split(';'):
            part = part.strip()
            if '=' in part:
                name, val = part.split('=', 1)
                cookies.append({
                    'name': name.strip(),
                    'value': val.strip(),
                    'domain': default_domain,
                    'path': '/'
                })
        return cookies

def _launch_browser(p):
    """Try Playwright Chromium, fallback to Chrome, then Edge."""
    try:
        import database
        settings = database.get_settings()
        headless_setting = settings.get('browser_headless', '0')
        is_headless = (headless_setting == '1')
    except Exception:
        is_headless = False

    try:
        return p.chromium.launch(headless=is_headless, args=['--disable-notifications', '--no-sandbox', '--disable-blink-features=AutomationControlled'])
    except Exception:
        pass
    try:
        return p.chromium.launch(headless=is_headless, channel="chrome", args=['--disable-notifications', '--no-sandbox'])
    except Exception:
        pass
    return p.chromium.launch(headless=is_headless, channel="msedge", args=['--disable-notifications', '--no-sandbox'])

def _make_context(browser):
    return browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        viewport={'width': 1280, 'height': 900},
        locale='vi-VN'
    )

def _take_screenshot(page, name_prefix, ref_id):
    screenshot_dir = os.path.abspath(os.path.join('uploads', 'screenshots'))
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_name = f"{name_prefix}_{ref_id}.png"
    try:
        page.screenshot(path=os.path.join(screenshot_dir, screenshot_name))
    except Exception:
        pass
    return f"screenshots/{screenshot_name}"

def _check_logged_in(page):
    if page.query_selector('input[name="email"]') or page.query_selector('input[name="pass"]'):
        raise Exception("Cookie expired - redirected to login page.")

def _switch_to_all_comments(page, container=None):
    """
    Finds the comment sorting dropdown (e.g. 'Phù hợp nhất' or 'Most relevant')
    and switches it to 'Tất cả bình luận' or 'All comments' to ensure all comments are visible.
    """
    try:
        dropdown_selectors = [
            'div[role="button"]:has-text("Phù hợp nhất")',
            'div[role="button"]:has-text("Most relevant")',
            'div[role="button"]:has-text("Most Relevant")',
            'span:has-text("Phù hợp nhất")',
            'span:has-text("Most relevant")',
            'span:has-text("Most Relevant")'
        ]
        
        dropdown_btn = None
        locator_context = container if container else page
        
        for sel in dropdown_selectors:
            try:
                loc = locator_context.locator(sel)
                if loc.count() > 0 and loc.first.is_visible():
                    dropdown_btn = loc.first
                    break
            except Exception:
                pass
                
        if dropdown_btn:
            print("[Automation] Found comment sorting dropdown, clicking to switch...")
            dropdown_btn.click()
            time.sleep(1.5)
            
            option_selectors = [
                'span:has-text("Tất cả bình luận")',
                'span:has-text("All comments")',
                'div[role="menuitem"]:has-text("Tất cả bình luận")',
                'div[role="menuitem"]:has-text("All comments")'
            ]
            
            option_el = None
            for sel in option_selectors:
                try:
                    loc = page.locator(sel)
                    if loc.count() > 0 and loc.first.is_visible():
                        option_el = loc.first
                        break
                except Exception:
                    pass
            
            if option_el:
                option_el.click()
                print("[Automation] Switched comment sorting to 'All comments'.")
                time.sleep(2)
            else:
                try:
                    page.keyboard.press("Escape")
                except Exception:
                    pass
    except Exception as e:
        print(f"[Automation] Error switching comment sorting: {e}")

def _type_and_submit_comment(page, textbox_el, comment_text, type_delay, delay_focus, delay_type_end, delay_after_enter):
    """
    Inputs comment_text into textbox_el, and submits it by searching for the 'Post'/'Đăng' button,
    or pressing Enter. Then checks if the comment appears in the page DOM.
    """
    try:
        textbox_el.focus()
        time.sleep(delay_focus)
        
        # Clear existing text first
        try:
            page.keyboard.press("Control+A")
            time.sleep(0.1)
            page.keyboard.press("Backspace")
            time.sleep(0.1)
        except Exception:
            pass
            
        textbox_el.press_sequentially(comment_text, delay=type_delay)
        
        # Trigger Facebook's link parsing by typing a space and waiting
        try:
            textbox_el.press_sequentially(" ", delay=type_delay)
            time.sleep(2.0)
        except:
            pass
            
        time.sleep(delay_type_end)
        
        # Try to find a click-to-submit button first
        clicked = False
        try:
            # Look at ancestors up to 4 levels to find a container
            parent = textbox_el
            for _ in range(4):
                parent = parent.locator('xpath=..')
                if parent.count() == 0:
                    break
                # Search for send buttons inside this ancestor
                btn_selectors = [
                    'div[role="button"][aria-label="Đăng bình luận"]',
                    'div[role="button"][aria-label="Post comment"]',
                    'div[role="button"][aria-label="Đăng"]',
                    'div[role="button"][aria-label="Post"]',
                    'div[role="button"][aria-label="Gửi"]',
                    'div[role="button"][aria-label="Send"]',
                    'div[role="button"]:has(svg)'
                ]
                for sel in btn_selectors:
                    btn = parent.locator(sel)
                    if btn.count() > 0:
                        # Find the first visible one
                        for idx in range(btn.count()):
                            b = btn.nth(idx)
                            if b.is_visible() and b.is_enabled(timeout=1000):
                                print(f"[Automation] Found submit button: {sel}, clicking it...")
                                b.hover(timeout=2000, force=True)
                                time.sleep(0.2)
                                b.click(timeout=2000, force=True)
                                clicked = True
                                break
                    if clicked:
                        break
                if clicked:
                    break
        except Exception as click_err:
            print(f"[Automation] Error searching/clicking comment submit button: {click_err}")
            
        if not clicked:
            print("[Automation] Submit button not found or click failed, pressing Enter...")
            textbox_el.press("Enter", timeout=5000)
            
        time.sleep(delay_after_enter)
        
        # Verify if comment actually shows up
        try:
            for _ in range(3):
                body_text = page.locator('body').inner_text()
                if comment_text[:20] in body_text:
                    print("[Automation] Comment verified in page body.")
                    try:
                        from telegram_bot import notify_user
                        notify_user(f"✅ <b>Lolishop Bot:</b> Đã tự động bình luận mồi thành công trên Facebook!\n\n📝 <b>Nội dung:</b>\n<i>{comment_text}</i>")
                    except Exception:
                        pass
                    return True
                time.sleep(1.0)
            print("[Automation] Comment not verified in page body (it might still have posted, but could be filtered).")
        except Exception as check_err:
            print(f"[Automation] Error verifying comment: {check_err}")
            
        return True
    except Exception as e:
        print(f"[Automation] Failed to input and submit comment: {e}")
        return False

# ─────────────────────────────────────────
# PUBLISH POST
# ─────────────────────────────────────────
def _comment_on_first_post(page, comment_text):
    print(f"[Poster] Tiến hành bình luận tự động dưới bài đăng mới: {comment_text}")
    try:
        # 1. Check if comment box is already visible
        comment_box = None
        comment_box_selectors = [
            'div[role="textbox"]',
            'div[contenteditable="true"]',
            '[aria-label*="bình luận" i]',
            '[aria-label*="comment" i]'
        ]
        
        for sel in comment_box_selectors:
            try:
                el = page.locator(sel).first
                if el and el.count() > 0 and el.is_visible():
                    comment_box = el
                    break
            except:
                pass
                
        # 2. If not visible, try to click the Comment button
        if not comment_box:
            comment_btn = None
            comment_btn_selectors = [
                'div[role="button"]:has-text("Bình luận")',
                'div[role="button"]:has-text("Comment")',
                'span:has-text("Bình luận")',
                'span:has-text("Comment")',
                'div[aria-label*="Bình luận" i]',
                'div[aria-label*="Comment" i]'
            ]
            for btn_sel in comment_btn_selectors:
                try:
                    el = page.locator(btn_sel).first
                    if el and el.count() > 0 and el.is_visible():
                        comment_btn = el
                        break
                except:
                    pass
            
            if comment_btn:
                print("[Poster] Click nút Bình luận để mở hộp nhập...")
                comment_btn.click()
                time.sleep(3)
                
                # Re-check comment box
                for sel in comment_box_selectors:
                    try:
                        el = page.locator(sel).first
                        if el and el.count() > 0 and el.is_visible():
                            comment_box = el
                            break
                    except:
                        pass
        
        if comment_box:
            print("[Poster] Nhập nội dung bình luận...")
            try:
                comment_box.evaluate("el => el.scrollIntoView({block: 'center'})")
                time.sleep(0.5)
                comment_box.evaluate("el => el.focus()")
                time.sleep(0.5)
                comment_box.click(force=True)
            except Exception as e:
                print(f"[Poster] Lỗi focus hộp bình luận: {e}")
            time.sleep(0.5)
            
            # Use the existing type_and_submit logic
            success = _type_and_submit_comment(
                page=page,
                textbox_el=comment_box,
                comment_text=comment_text,
                type_delay=5,
                delay_focus=0.2,
                delay_type_end=0.3,
                delay_after_enter=2.0
            )
            if success:
                print("[Poster] Bình luận thành công.")
                return True
            else:
                print("[Poster] Gửi bình luận không thành công.")
        else:
            print("[Poster] Không tìm thấy hộp nhập bình luận.")
    except Exception as e:
        print(f"[Poster] Lỗi khi bình luận: {e}")
    return False

def publish_post(account_cookie, post_type, target_id, content, media_paths, post_id, first_comment=None):
    try:
        cookies = parse_cookies(account_cookie)
    except Exception as e:
        return {'success': False, 'log': f'Cookie error: {str(e)}', 'screenshot': ''}

    if not cookies:
        return {'success': False, 'log': 'No valid cookies found.', 'screenshot': ''}

    result = {'success': False, 'log': '', 'screenshot': '', 'status': 'failed'}
    content = spin_text(content)

    # Check if group is in nurture period (< 3 days since join)
    if post_type == 'group':
        try:
            import database
            from datetime import datetime, timedelta
            conn = database.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM accounts WHERE cookie=?", (account_cookie,))
            acc_row = cursor.fetchone()
            if acc_row:
                account_id = acc_row[0]
                clean_target = str(target_id).strip().rstrip('/')
                slug = clean_target.split('/')[-1]
                cursor.execute(
                    "SELECT created_at FROM autojoin_logs WHERE account_id=? AND (target_name_or_url LIKE ? OR target_name_or_url LIKE ?) AND status='success' ORDER BY created_at DESC LIMIT 1",
                    (account_id, f"%{clean_target}%", f"%{slug}%")
                )
                log_row = cursor.fetchone()
                if log_row:
                    join_time = datetime.fromisoformat(log_row[0])
                    settings = database.get_settings()
                    nurture_days = int(settings.get('group_nurture_days', 3))
                    elapsed = datetime.now() - join_time
                    if elapsed < timedelta(days=nurture_days):
                        remaining = timedelta(days=nurture_days) - elapsed
                        remaining_hours = int(remaining.total_seconds() / 3600)
                        conn.close()
                        return {
                            'success': False,
                            'log': f'Nhóm mới tham gia. Đang trong giai đoạn tương tác nuôi tài khoản (Còn {remaining_hours} giờ).',
                            'status': 'nurturing'
                        }
            conn.close()
        except Exception as e:
            print(f"[Poster] Lỗi kiểm tra thời gian nuôi nhóm: {e}")

    with sync_playwright() as p:
        browser = None
        try:
            print(f"[Poster] Launching browser for post {post_id}...")
            browser = _launch_browser(p)
            context = _make_context(browser)
            context.add_cookies(cookies)
            page = context.new_page()

            target_id_str = str(target_id).strip()
            if target_id_str.startswith('http://') or target_id_str.startswith('https://'):
                url = target_id_str
            elif 'facebook.com' in target_id_str or 'fb.com' in target_id_str:
                url = 'https://' + target_id_str if not target_id_str.startswith('http') else target_id_str
            else:
                if post_type == 'group' and (target_id_str.isdigit() or '/' in target_id_str):
                    url = f'https://www.facebook.com/groups/{target_id_str}'
                elif post_type == 'page' and (target_id_str.isalnum()):
                    url = f'https://www.facebook.com/{target_id_str}'
                else:
                    url = 'https://www.facebook.com'

            print(f"[Poster] Navigating to: {url}")
            page.goto(url, wait_until='domcontentloaded', timeout=60000)
            time.sleep(3)
            _check_logged_in(page)

            # Find composer
            print("[Poster] Waiting for composer to load...")
            composer_selectors = [
                'span:has-text("Bạn đang nghĩ gì")',
                'span:has-text("on your mind")',
                'span:has-text("Write something")',
                'span:has-text("Viết gì đó")',
                'span:has-text("Bạn viết gì đi")',
                'span:has-text("viết gì đi")',
                'span:has-text("Tạo bài viết")',
                'span:has-text("Create post")',
                'span:has-text("Tạo bài viết công khai")',
                'span:has-text("Create a public post")',
                'div[role="button"]:has-text("đang nghĩ gì")',
                'div[role="button"]:has-text("on your mind")',
                'div[role="button"]:has-text("Viết gì đó")',
                'div[role="button"]:has-text("Bạn viết gì đi")',
                'div[role="button"]:has-text("viết gì đi")',
                'div[role="button"]:has-text("Write something")',
                'div[role="button"]:has-text("Tạo bài viết công khai")',
                'div[role="button"]:has-text("Create a public post")',
                'div[role="button"]:has-text("Tạo bài viết")',
                'div[role="button"]:has-text("Create post")',
                'div:has-text("Bạn đang nghĩ gì")',
                'div:has-text("on your mind")',
                'div:has-text("Write something")',
                'div:has-text("Viết gì đó")',
                'div:has-text("Bạn viết gì đi")',
                'div:has-text("viết gì đi")',
            ]

            composer_trigger = None
            # Try waiting for up to 15 seconds, checking selectors
            for attempt in range(15):
                for sel in composer_selectors:
                    try:
                        el = page.query_selector(sel)
                        if el and el.is_visible():
                            composer_trigger = el
                            print(f"[Poster] Found composer: {sel}")
                            break
                    except Exception:
                        pass
                if composer_trigger:
                    break
                time.sleep(1)

            # If composer not found, check if we need to join the group
            if not composer_trigger and post_type == 'group':
                print("[Poster] Không tìm thấy khung soạn thảo. Đang kiểm tra xem tài khoản đã tham gia nhóm chưa...")
                
                # Check if already requested
                page_text = page.evaluate("document.body.innerText")
                if any(x in page_text for x in ["Đã gửi yêu cầu", "Requested", "Hủy yêu cầu", "Cancel Request"]):
                    msg = "Yêu cầu tham gia nhóm đang chờ duyệt. Chưa thể đăng bài."
                    return {'success': False, 'log': msg, 'status': 'failed', 'screenshot': _take_screenshot(page, 'join_pending', post_id)}
                
                join_btn = None
                btn_selectors = [
                    'div[role="button"]:has-text("Tham gia nhóm")',
                    'div[role="button"]:has-text("Join group")',
                    'div[role="button"]:has-text("Join Group")',
                    'div[role="button"]:has-text("Tham gia")',
                    'div[role="button"]:has-text("Join")',
                    'span:has-text("Tham gia nhóm")',
                    'span:has-text("Join group")'
                ]
                
                for sel in btn_selectors:
                    try:
                        btn = page.locator(sel).first
                        if btn and btn.is_visible():
                            join_btn = btn
                            break
                    except:
                        pass
                        
                if not join_btn:
                    try:
                        buttons = page.query_selector_all('div[role="button"], button')
                        for btn in buttons:
                            text = btn.inner_text() or ""
                            if "tham gia" in text.lower() or "join" in text.lower():
                                join_btn = btn
                                break
                    except:
                        pass
                        
                if join_btn:
                    print("[Poster] Phát hiện nút Tham gia nhóm. Tiến hành tự động tham gia...")
                    try:
                        import database
                        from database import save_autojoin_log
                        conn = database.get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT id FROM accounts WHERE cookie=?", (account_cookie,))
                        row = cursor.fetchone()
                        conn.close()
                        account_id = row[0] if row else "unknown"

                        join_btn.click()
                        time.sleep(4)
                        
                        dialog = page.query_selector('div[role="dialog"]')
                        details = ""
                        
                        if dialog:
                            print("[Poster] Phát hiện hộp thoại câu hỏi thành viên.")
                            dialog_text = dialog.inner_text()
                            
                            checkboxes = dialog.query_selector_all('input[type="checkbox"], div[role="checkbox"]')
                            for cb in checkboxes:
                                try:
                                    if cb.get_attribute('aria-checked') != 'true':
                                        cb.click()
                                        time.sleep(0.5)
                                except:
                                    pass
                            
                            text_inputs = dialog.query_selector_all('textarea, input[type="text"], div[role="textbox"]')
                            if text_inputs:
                                settings = database.get_settings()
                                api_key = settings.get('gemini_api_key', '').strip()
                                
                                for i, inp in enumerate(text_inputs):
                                    answer = "Tôi đồng ý tham gia nhóm và tuân thủ các nội quy."
                                    if api_key:
                                        try:
                                            prompt = (
                                                f"Dưới đây là nội dung câu hỏi xét duyệt tham gia nhóm Facebook:\n"
                                                f"\"\"\"\n{dialog_text}\n\"\"\"\n"
                                                f"Hãy đưa ra câu trả lời ngắn gọn, phù hợp nhất cho câu hỏi thứ {i+1}. "
                                                f"Yêu cầu:\n"
                                                f"- Chỉ trả lời đúng nội dung câu hỏi, không kèm giải thích.\n"
                                                f"- Trả lời ngắn gọn dưới 15 từ.\n"
                                                f"- Trả lời bằng tiếng Việt."
                                            )
                                            ai_ans = call_gemini(api_key, prompt)
                                            if ai_ans and len(ai_ans.strip()) > 0:
                                                answer = ai_ans.strip()
                                        except:
                                            pass
                                            
                                    try:
                                        inp.fill(answer)
                                        time.sleep(1)
                                    except:
                                        pass
                                    details += f"Q{i+1}: {answer}; "
                            
                            submit_btn = None
                            submit_selectors = [
                                'div[role="button"]:has-text("Gửi")',
                                'div[role="button"]:has-text("Submit")',
                                'div[role="button"]:has-text("Hoàn tất")',
                                'button:has-text("Gửi")',
                                'button:has-text("Submit")'
                            ]
                            for s_sel in submit_selectors:
                                try:
                                    s_btn = dialog.query_selector(s_sel)
                                    if s_btn:
                                        submit_btn = s_btn
                                        break
                                except:
                                    pass
                                    
                            if submit_btn:
                                submit_btn.click()
                                time.sleep(3)
                                status = "pending_approval"
                                details = "Đã gửi câu trả lời: " + details
                            else:
                                status = "failed"
                                details = "Không gửi được câu hỏi xét duyệt."
                        else:
                            status = "success"
                            details = "Đã tham gia thành công trực tiếp (Không có câu hỏi)."
                        
                        save_autojoin_log(account_id, url, status, f"[Auto-Join từ Đăng bài] {details}")
                        
                        if status == "success":
                            print("[Poster] Đã tự động tham gia nhóm thành công trực tiếp. Tiến hành kích hoạt tương tác nuôi tài khoản...")
                            try:
                                import database
                                target_id_db = 'tgt_' + str(uuid.uuid4())[:8]
                                target_name = url.rstrip('/').split('/')[-1]
                                database.save_autolike_target(
                                    target_id=target_id_db,
                                    account_id=account_id,
                                    target_url=url,
                                    target_name=target_name,
                                    status='active',
                                    auto_comment=1,
                                    comment_style='AI'
                                )
                                print(f"[Poster] Đã tự động thêm nhóm {target_name} vào mục tiêu tương tác nuôi tài khoản.")
                            except Exception as e:
                                print(f"[Poster] Lỗi khi thêm nhóm vào mục tiêu tương tác: {e}")
                                
                            return {
                                'success': False,
                                'log': 'Đã tự động tham gia nhóm thành công. Đang trong giai đoạn tương tác nuôi tài khoản 3 ngày.',
                                'status': 'nurturing',
                                'screenshot': _take_screenshot(page, 'join_success_nurturing', post_id)
                            }
                        else:
                            return {
                                'success': False,
                                'log': 'Tài khoản chưa tham gia nhóm. Hệ thống đã tự động gửi yêu cầu tham gia và câu trả lời AI, đang chờ duyệt.',
                                'status': 'failed',
                                'screenshot': _take_screenshot(page, 'join_pending', post_id)
                            }
                    except Exception as join_err:
                        print(f"[Poster] Lỗi khi tự động tham gia nhóm: {join_err}")
                        return {
                            'success': False,
                            'log': f'Chưa tham gia nhóm. Lỗi khi tự động tham gia: {str(join_err)}',
                            'status': 'failed',
                            'screenshot': _take_screenshot(page, 'join_error', post_id)
                        }

            if not composer_trigger:
                raise Exception("Cannot find post composer box. Facebook UI may have changed.")

            composer_trigger.click()
            time.sleep(3)

            # Wait for textbox
            textbox_selectors = [
                'div[role="dialog"] div[role="textbox"]',
                'div[role="textbox"]',
                'div[contenteditable="true"]',
                '[aria-label="Tạo bài viết công khai"]',
                '[aria-label="Create a public post"]',
                '[aria-label="Bạn đang nghĩ gì?"]',
                '[aria-label="What\'s on your mind?"]'
            ]
            
            textbox = None
            for sel in textbox_selectors:
                try:
                    page.wait_for_selector(sel, timeout=3000)
                    el = page.locator(sel).first
                    if el and el.count() > 0 and el.is_visible():
                        textbox = el
                        print(f"[Poster] Found textbox: {sel}")
                        break
                except Exception:
                    pass
            
            if not textbox:
                # Fallback to default selector
                textbox_sel = 'div[role="dialog"] div[role="textbox"]'
                page.wait_for_selector(textbox_sel, timeout=10000)
                textbox = page.locator(textbox_sel)

            textbox.focus()
            textbox.fill(content)
            try:
                page.keyboard.press("Space")
                time.sleep(0.2)
                page.keyboard.press("Backspace")
                time.sleep(0.5)
            except Exception as key_err:
                print(f"[Poster] Keyboard event trigger error: {key_err}")

            if "http://" in content or "https://" in content:
                print("[Poster] Content contains a link. Waiting 5 seconds for Facebook to generate link preview...")
                time.sleep(5)
            else:
                time.sleep(1)

            # Upload media
            if media_paths:
                file_input = page.locator('div[role="dialog"] input[type="file"]')
                if file_input.count() == 0:
                    file_input = page.locator('input[type="file"]')
                
                if file_input.count() == 0:
                    for sel in ['div[aria-label="Photo/video"]', 'div[aria-label="Ảnh/video"]',
                                'div[aria-label="Ảnh/Video"]',
                                'div[role="button"]:has-text("Photo/video")', 'div[role="button"]:has-text("Ảnh/video")',
                                'div[role="button"]:has-text("Ảnh/Video")']:
                        btn = page.locator(sel)
                        if btn.count() > 0:
                            btn.first.click()
                            time.sleep(2)
                            break
                    try:
                        page.wait_for_selector('input[type="file"]', timeout=5000)
                    except Exception:
                        pass
                    file_input = page.locator('input[type="file"]')

                resolved = [os.path.abspath(os.path.join('uploads', m)) if not os.path.isabs(m) else m
                            for m in media_paths if os.path.exists(os.path.abspath(os.path.join('uploads', m)) if not os.path.isabs(m) else m)]
                if resolved and file_input.count() > 0:
                    file_input.first.set_input_files(resolved)
                    time.sleep(6)

            # Click Post button
            time.sleep(2)
            post_btn = None
            post_selectors = [
                'div[role="dialog"] div[role="button"]:has-text("Đăng")',
                'div[role="dialog"] div[role="button"]:has-text("Post")',
                'div[role="dialog"] div[role="button"][aria-label="Đăng"]',
                'div[role="dialog"] div[role="button"][aria-label="Post"]',
                'div[role="button"]:has-text("Đăng")',
                'div[role="button"]:has-text("Post")',
                'div[role="button"][aria-label="Đăng"]',
                'div[role="button"][aria-label="Post"]'
            ]
            for sel in post_selectors:
                loc = page.locator(sel)
                cnt = loc.count()
                for idx in range(cnt):
                    try:
                        btn = loc.nth(idx)
                        if btn.is_visible():
                            post_btn = btn
                            print(f"[Poster] Found post button: {sel}")
                            break
                    except Exception:
                        pass
                if post_btn:
                    break

            if not post_btn:
                loc = page.locator('div[role="dialog"] div[role="button"]')
                if loc.count() > 0:
                    post_btn = loc.last
                else:
                    post_btn = page.locator('div[role="button"]').last

            post_btn.click()
            print("[Poster] Post button clicked. Waiting for dialog to close...")

            try:
                page.wait_for_selector('div[role="dialog"]', state='detached', timeout=30000)
            except Exception:
                time.sleep(6)

            # Check if post is pending admin approval
            time.sleep(4)
            page_url_lower = page.url.lower()
            page_text = ""
            try:
                page_text = page.locator('body').inner_text()
            except Exception:
                pass
                
            pending_keywords = [
                "chờ phê duyệt",
                "chờ quản trị",
                "chờ duyệt",
                "pending approval",
                "submitted for approval",
                "admin approval",
                "approval queue",
                "cám ơn bạn đã đăng",
                "đã gửi bài viết"
            ]
            
            is_pending = "pending" in page_url_lower
            if not is_pending:
                page_text_lower = page_text.lower()
                for kw in pending_keywords:
                    if kw in page_text_lower:
                        is_pending = True
                        break
                        
            if is_pending:
                result['log'] = 'Bài viết đã được gửi và đang chờ phê duyệt từ quản trị viên (Nhóm kiểm duyệt bài).'
                result['status'] = 'pending_approval'
            else:
                result['log'] = 'Đăng bài thành công.'
                result['status'] = 'posted'
                
                # Fetch Post URL via Activity Log
                try:
                    page.goto('https://www.facebook.com/me/allactivity/?category_key=GROUPPOSTS', timeout=15000)
                    time.sleep(3)
                    elements = page.query_selector_all('a[href*="/groups/"]')
                    for el in elements:
                        href = el.get_attribute('href')
                        if '/permalink/' in href or '/posts/' in href:
                            result['post_url'] = href
                            break
                except Exception as e:
                    print(f"Failed to extract post URL: {e}")
                # Tự động bình luận dưới bài đăng nếu cấu hình
                if first_comment and len(first_comment.strip()) > 0:
                    comment_success = _comment_on_first_post(page, first_comment)
                    if comment_success:
                        result['log'] += ' Đã gửi bình luận tự động thành công.'
                    else:
                        result['log'] += ' Gửi bình luận tự động thất bại.'

            result['success'] = True
            result['screenshot'] = _take_screenshot(page, 'success', post_id)
            print(f"[Poster] Post {post_id} completed successfully. Status: {result['status']}")

        except Exception as err:
            print(f"[Poster] Error: {str(err)}")
            result['success'] = False
            result['log'] = f'Lỗi: {str(err)}'
            try:
                result['screenshot'] = _take_screenshot(page, 'error', post_id)
            except Exception:
                pass
        finally:
            if browser:
                try: browser.close()
                except Exception: pass

    return result

# ─────────────────────────────────────────
# ENGAGEMENT: AUTO REPLY COMMENTS
# ─────────────────────────────────────────
def get_reply_text(comment_content, rules):
    comment_lower = comment_content.lower()
    default_reply = None
    for rule in rules:
        keywords = rule.get('keywords', '').strip().lower()
        if keywords == '*' or not keywords:
            default_reply = rule.get('reply_text')
            continue
        for kw in [k.strip() for k in keywords.split(',') if k.strip()]:
            if kw in comment_lower:
                return rule.get('reply_text')
    return default_reply

def _send_private_messenger_message(page, comment_el, commenter_name, message_text):
    """
    Attempts to send a private message to a commenter using Facebook Page's Message button
    or by hovering over the user's name to open their profile hovercard and clicking message.
    """
    print(f"[InboxBot] Attempting to send private message to {commenter_name}...")
    try:
        # 1. Search for direct Message / Nhắn tin / Gửi tin nhắn button in the comment block
        msg_btn_selectors = [
            'div[role="button"]:has-text("Nhắn tin")',
            'div[role="button"]:has-text("Message")',
            'div[role="button"]:has-text("Gửi tin nhắn")',
            'span:has-text("Nhắn tin")',
            'span:has-text("Message")'
        ]
        
        msg_btn = None
        for sel in msg_btn_selectors:
            btn = comment_el.locator(sel)
            if btn.count() > 0:
                msg_btn = btn.first
                break
                
        if msg_btn:
            print(f"[InboxBot] Found direct message button, clicking...")
            msg_btn.hover()
            time.sleep(0.5)
            msg_btn.click()
            time.sleep(3)
            
            # Find the chat input textbox
            chat_box = page.locator('div[role="textbox"][aria-label*="Tin nhắn"], div[role="textbox"][aria-label*="Message"], div[role="textbox"]')
            if chat_box.count() > 0:
                print("[InboxBot] Chat box found, typing message...")
                chat_box.first.fill(message_text)
                time.sleep(1)
                chat_box.first.press("Enter")
                time.sleep(3)
                
                # Check for close button on the chat box
                close_btn = page.locator('div[role="button"][aria-label*="Đóng"], div[role="button"][aria-label*="Close"], div[role="button"][aria-label*="Đóng cửa sổ"]')
                if close_btn.count() > 0:
                    close_btn.first.click()
                    time.sleep(1)
                return True
                
        # 2. Try profile hover method (e.g. for Groups)
        name_el = comment_el.locator('a[role="link"]').first
        if name_el.count() > 0:
            print(f"[InboxBot] Hovering commenter name to open profile hovercard...")
            name_el.hover()
            time.sleep(3) # Wait for hovercard to open
            
            # Search for message button inside the hovercard
            hover_msg_btn = page.locator('div[role="dialog"] div[role="button"]:has-text("Nhắn tin"), div[role="dialog"] div[role="button"]:has-text("Message"), div[role="dialog"] a[role="link"]:has-text("Nhắn tin"), div[role="dialog"] a[role="link"]:has-text("Message")')
            if hover_msg_btn.count() > 0:
                print(f"[InboxBot] Found message button in hovercard, clicking...")
                hover_msg_btn.first.click()
                time.sleep(3)
                
                # Find chat box and send message
                chat_box = page.locator('div[role="textbox"][aria-label*="Tin nhắn"], div[role="textbox"][aria-label*="Message"], div[role="textbox"]')
                if chat_box.count() > 0:
                    print("[InboxBot] Chat box found from hovercard, sending message...")
                    chat_box.first.fill(message_text)
                    time.sleep(1)
                    chat_box.first.press("Enter")
                    time.sleep(3)
                    
                    close_btn = page.locator('div[role="button"][aria-label*="Đóng"], div[role="button"][aria-label*="Close"]')
                    if close_btn.count() > 0:
                        close_btn.first.click()
                        time.sleep(1)
                    return True
                    
        print("[InboxBot] Could not find any message buttons for this commenter.")
        return False
    except Exception as e:
        print(f"[InboxBot] Error sending message: {e}")
        return False

def auto_reply_post_comments(account_cookie, post_url, page_name, rules, max_replies=5):
    try:
        import database
        db_settings = database.get_settings()
        speed_mode = db_settings.get('engage_speed_mode', 'turbo')
    except Exception:
        speed_mode = 'turbo'

    if speed_mode == 'turbo':
        type_delay = 1
        delay_hover = 0.05
        delay_click = 0.1
        delay_focus = 0.1
        delay_type_end = 0.1
        delay_after_enter = 0.5
    else:
        type_delay = 60
        delay_hover = 0.8
        delay_click = 1.5
        delay_focus = 0.8
        delay_type_end = 1.0
        delay_after_enter = 4.0

    try:
        cookies = parse_cookies(account_cookie)
    except Exception as e:
        print(f"[Engage] Cookie parse error: {e}")
        return []

    if not cookies:
        return []

    logs = []

    with sync_playwright() as p:
        browser = None
        try:
            print(f"[Engage] Scanning comments at: {post_url}")
            browser = _launch_browser(p)
            context = _make_context(browser)
            context.add_cookies(cookies)
            page = context.new_page()

            page.goto(post_url, wait_until='domcontentloaded', timeout=60000)
            time.sleep(5)
            _check_logged_in(page)

            # Switch sorting to All comments to ensure nothing is hidden
            _switch_to_all_comments(page)

            # Scroll to load more comments
            for _ in range(3):
                page.evaluate("window.scrollBy(0, 600)")
                time.sleep(1.5)

            comment_locators = page.locator('div[role="article"]')
            count = comment_locators.count()
            print(f"[Engage] Found {count} article elements")

            processed = 0
            for i in range(count):
                if processed >= max_replies:
                    break

                comment_el = comment_locators.nth(i)
                like_btn = comment_el.locator('div[role="button"]:has-text("Thích"), div[role="button"]:has-text("Like")')
                reply_btn = comment_el.locator('div[role="button"]:has-text("Phản hồi"), div[role="button"]:has-text("Reply")')

                if like_btn.count() == 0 or reply_btn.count() == 0:
                    continue

                name_el = comment_el.locator('a[role="link"]').first
                commenter_name = name_el.inner_text().strip() if name_el.count() > 0 else "Unknown"

                if page_name.lower() in commenter_name.lower():
                    continue

                text_el = comment_el.locator('span[dir="auto"]').first
                comment_text = text_el.inner_text().strip() if text_el.count() > 0 else ""

                if not comment_text:
                    continue

                # ---------------- HAME AI Messenger Inbox Bot ----------------
                is_inbox_sent = False
                inbox_enabled = db_settings.get('inbox_chatbot_enabled', '0') == '1'
                
                # Check keywords
                inbox_keywords_str = db_settings.get('inbox_keywords', 'ib,gia,inbox,tu van,link,shop,mua,size,ship')
                inbox_keywords = [kw.strip().lower() for kw in inbox_keywords_str.split(',') if kw.strip()]
                
                is_inbox_trigger = False
                comment_text_lower = comment_text.lower()
                for kw in inbox_keywords:
                    if kw in comment_text_lower:
                        is_inbox_trigger = True
                        break
                        
                if inbox_enabled and is_inbox_trigger:
                    # 1. Locate redirect link on the page
                    redirect_link = ""
                    try:
                        links = page.locator('a[href*="/r/"]')
                        for li in range(links.count()):
                            href = links.nth(li).get_attribute('href')
                            if href and '/r/' in href:
                                if 'l.facebook.com/l.php' in href:
                                    import urllib.parse
                                    parsed = urllib.parse.urlparse(href)
                                    queries = urllib.parse.parse_qs(parsed.query)
                                    if 'u' in queries:
                                        redirect_link = queries['u'][0]
                                        break
                                else:
                                    redirect_link = href
                                    break
                    except Exception as link_err:
                        print(f"[InboxBot] Error finding redirect link: {link_err}")
                        
                    if not redirect_link:
                        # Fallback to last redirect in database
                        try:
                            public_domain = db_settings.get('public_domain', 'http://localhost:5000').rstrip('/')
                            conn = database.get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("SELECT id FROM redirects ORDER BY created_at DESC LIMIT 1")
                            last_redir = cursor.fetchone()
                            conn.close()
                            if last_redir:
                                redirect_link = f"{public_domain}/r/{last_redir[0]}"
                        except Exception:
                            pass
                            
                    # 2. Format private message
                    inbox_msg_template = db_settings.get('inbox_message_template', 'Chào {name}! Cảm ơn bạn đã quan tâm sản phẩm bên mình. Đây là thông tin chi tiết và đường dẫn ưu đãi dành cho bạn: {link}')
                    inbox_msg = inbox_msg_template.replace('{name}', commenter_name).replace('{link}', redirect_link)
                    
                    # 3. Send private message
                    is_inbox_sent = _send_private_messenger_message(page, comment_el, commenter_name, inbox_msg)
                    
                    if is_inbox_sent:
                        # Format public comment reply
                        public_reply_template = db_settings.get('inbox_comment_reply_template', 'Chào {name}, mình đã gửi tin nhắn riêng thông tin chi tiết và ưu đãi cho bạn rồi nhé. Bạn check hộp thư Messenger giúp mình nha! {link}')
                        reply_content = public_reply_template.replace('{name}', commenter_name).replace('{link}', redirect_link)
                        
                        # Send Telegram notification
                        try:
                            from telegram_bot import notify_user
                            notify_user(f"💬 <b>HAME Sales Funnel:</b> Đã tự động inbox chốt đơn thành công cho khách hàng <b>{commenter_name}</b> trên Facebook!\n\n📝 <b>Nội dung tin nhắn:</b>\n<i>{inbox_msg}</i>")
                        except Exception:
                            pass
                    else:
                        # Fallback to rules if message sending failed
                        reply_content = get_reply_text(comment_text, rules)
                        if not reply_content:
                            continue
                        if reply_content.startswith('[AI]') or reply_content.startswith('[Gemini]'):
                            reply_content = get_gemini_reply(page_name, comment_text, reply_content)
                        else:
                            reply_content = spin_text(reply_content)
                else:
                    # Default rules behavior
                    reply_content = get_reply_text(comment_text, rules)
                    if not reply_content:
                        continue
                    if reply_content.startswith('[AI]') or reply_content.startswith('[Gemini]'):
                        reply_content = get_gemini_reply(page_name, comment_text, reply_content)
                    else:
                        reply_content = spin_text(reply_content)
                # -------------------------------------------------------------

                print(f"[Engage] Replying to: {commenter_name} - '{comment_text[:50]}'")

                try:
                    like_btn.first.hover()
                    time.sleep(delay_hover)
                    like_btn.first.click()
                    time.sleep(delay_click)

                    reply_btn.first.hover()
                    time.sleep(delay_hover)
                    reply_btn.first.click()
                    time.sleep(delay_click)

                    reply_textbox = comment_el.locator('div[role="textbox"]')
                    if reply_textbox.count() > 0:
                        _type_and_submit_comment(page, reply_textbox.first, reply_content, type_delay, delay_focus, delay_type_end, delay_after_enter)

                        log_id = 'eng_' + str(uuid.uuid4())[:8]
                        screenshot = _take_screenshot(page, 'engage', log_id)

                        logs.append({
                            'id': log_id,
                            'post_url': post_url,
                            'commenter_name': commenter_name,
                            'comment_content': comment_text,
                            'reply_content': reply_content,
                            'status': 'success',
                            'screenshot': screenshot
                        })
                        processed += 1
                        print(f"[Engage] Reply #{processed} sent.")

                except Exception as ex:
                    print(f"[Engage] Failed to reply: {ex}")

        except Exception as e:
            print(f"[Engage] Error: {e}")
        finally:
            if browser:
                try: browser.close()
                except Exception: pass

    return logs

# ─────────────────────────────────────────
# AUTO-LIKE: Auto like posts in target groups/pages
# ─────────────────────────────────────────
def auto_like_posts(account_cookie, target_url, max_likes=10, auto_comment=0, comment_style='AI', comment_text='', account_name=''):
    """Scroll through a group/page feed and like/comment on posts that aren't already liked."""
    try:
        import database
        db_settings = database.get_settings()
        speed_mode = db_settings.get('engage_speed_mode', 'turbo')
    except Exception:
        speed_mode = 'turbo'

    if speed_mode == 'turbo':
        type_delay = 1
        delay_like = 0.2
        delay_after_like = 0.2
        delay_focus = 0.1
        delay_type_end = 0.1
        delay_after_enter = 0.5
    else:
        type_delay = 60
        delay_like = 0.8
        delay_after_like = 1.5
        delay_focus = 0.5
        delay_type_end = 1.0
        delay_after_enter = 4.0

    try:
        cookies = parse_cookies(account_cookie)
    except Exception as e:
        print(f"[AutoLike] Cookie error: {e}")
        return []

    if not cookies:
        return []

    liked_posts = []

    with sync_playwright() as p:
        browser = None
        try:
            print(f"[AutoLike] Starting auto-like on: {target_url}")
            browser = _launch_browser(p)
            context = _make_context(browser)
            context.add_cookies(cookies)
            page = context.new_page()
            page.set_default_timeout(5000)

            page.goto(target_url, wait_until='domcontentloaded', timeout=60000)
            time.sleep(4)
            _check_logged_in(page)

            liked_count = 0

            for scroll_pass in range(5):  # Scroll through feed 5 times
                page.evaluate("window.scrollBy(0, 800)")
                time.sleep(2)

                print(f"[AutoLike] Pass {scroll_pass+1} scanning...")
                
                while True:
                    if liked_count >= max_likes:
                        break
                        
                    like_buttons = page.locator(
                        'div[role="button"][aria-label="Thích"]:not([aria-pressed="true"]):not([data-processed="1"]), '
                        'div[role="button"][aria-label="Like"]:not([aria-pressed="true"]):not([data-processed="1"])'
                    )
                    
                    if like_buttons.count() == 0:
                        break
                        
                    try:
                        btn = like_buttons.first
                        # Mark immediately to prevent infinite loop on skipped items
                        btn.evaluate("el => el.setAttribute('data-processed', '1')")
                        
                        has_article = btn.evaluate("el => el.closest('div[role=\"article\"]') !== null")
                        if not has_article:
                            continue
                            
                        post_el = btn.locator('xpath=ancestor::div[@role="article"]').first
                        post_link_el = post_el.locator('a[href*="/posts/"], a[href*="?story_fbid"]').first
                        try:
                            post_url_found = post_link_el.get_attribute('href', timeout=1000) if post_link_el.count() > 0 else target_url
                        except:
                            post_url_found = target_url

                        # Extract timeText and check if post is recent (max 10 days)
                        try:
                            time_text = post_el.evaluate(r'''el => {
                            let timeText = "";
                            let links = el.querySelectorAll('a[role="link"]');
                            for (let l of links) {
                                let txt = l.innerText.trim();
                                if (txt) {
                                    let txtLower = txt.toLowerCase();
                                    if (
                                        txtLower.includes("phút") || txtLower.includes("giờ") || 
                                        txtLower.includes("ngày") || txtLower.includes("tuần") || 
                                        txtLower.includes("tháng") || txtLower.includes("năm") ||
                                        txtLower.includes("hôm qua") || txtLower.includes("yesterday") ||
                                        txtLower.includes("min") || txtLower.includes("hr") || 
                                        txtLower.includes("day") || txtLower.includes("week") || 
                                        txtLower.includes("month") || txtLower.includes("year") ||
                                        /^\d+ [a-zA-Z]/.test(txtLower)
                                    ) {
                                        if (txt.length < 30 && !txtLower.includes("thích") && !txtLower.includes("comment") && !txtLower.includes("like") && !txtLower.includes("bày tỏ cảm xúc")) {
                                            timeText = txt;
                                            break;
                                        }
                                    }
                                }
                            }
                            return timeText;
                        }''')
                        except Exception:
                            time_text = ""
                        
                        if not is_post_recent(time_text, max_days=10):
                            print(f"[AutoLike] Bỏ qua bài viết quá 10 ngày.")
                            continue

                        btn.scroll_into_view_if_needed(timeout=2000)
                        time.sleep(delay_like)
                        btn.evaluate("el => el.click()") # Force click via JS to bypass overlays
                        time.sleep(delay_after_like)

                        log_id = 'like_' + str(uuid.uuid4())[:8]
                        liked_posts.append({
                            'id': log_id,
                            'post_url': post_url_found or target_url,
                            'status': 'success'
                        })
                        liked_count += 1
                        print(f"[AutoLike] Liked post #{liked_count}")

                        # Auto-comment if enabled
                        if auto_comment:
                            comment_box = post_el.locator('div[role="textbox"][aria-label*="Viết bình luận"], div[role="textbox"][aria-label*="Write a comment"], div[role="textbox"][aria-label*="bình luận"]')
                            if comment_box.count() == 0:
                                comment_trigger = post_el.locator('div[role="button"]:has-text("Bình luận"), div[role="button"]:has-text("Comment")').first
                                if comment_trigger.count() > 0:
                                    comment_trigger.evaluate("el => el.click()")
                                    time.sleep(delay_after_like)
                                    _switch_to_all_comments(page, container=post_el)
                                    comment_box = post_el.locator('div[role="textbox"][aria-label*="Viết bình luận"], div[role="textbox"][aria-label*="Write a comment"], div[role="textbox"][aria-label*="bình luận"]')
                            else:
                                _switch_to_all_comments(page, container=post_el)
                            
                            if comment_box.count() > 0:
                                comment_body = ""
                                if comment_style == 'AI':
                                    text_nodes = post_el.locator('div[dir="auto"]').all_inner_texts()
                                    post_text = " ".join([t.strip() for t in text_nodes if t.strip()])
                                    if not post_text:
                                        post_text = "Bài viết hay trên Facebook."
                                    comment_body = get_gemini_post_comment(account_name or "Tài khoản", post_text)
                                else:
                                    comment_body = spin_text(comment_text)

                                if comment_body:
                                    print(f"[AutoLike] Auto-commenting: '{comment_body[:40]}...'")
                                    box = comment_box.first
                                    box.hover(timeout=2000)
                                    time.sleep(delay_focus)
                                    _type_and_submit_comment(page, box, comment_body, type_delay, delay_focus, delay_type_end, delay_after_enter)
                                    print("[AutoLike] Comment posted.")

                    except Exception as ex:
                        print(f"[AutoLike] Could not engage post.")

                if liked_count >= max_likes:
                    break

            print(f"[AutoLike] Session complete. Total engaged: {liked_count}")

        except Exception as e:
            print(f"[AutoLike] Error: {e}")
        finally:
            if browser:
                try: browser.close()
                except Exception: pass

    return liked_posts

def get_gemini_post_comment(account_name, post_text):
    """Call Gemini to write a custom, natural comment on a post to interact with it."""
    import database
    settings = database.get_settings()
    api_key = settings.get('gemini_api_key', '').strip()
    if not api_key:
        print("[AutoLike-AI] No Gemini API key found. Falling back to default.")
        return "Bài viết chia sẻ rất hay và hữu ích ạ!"
        
    prompt = (
        f"Bạn là người dùng Facebook tên '{account_name}'. "
        f"Hãy viết một câu bình luận tương tác cực kỳ tự nhiên, thân thiện và ngắn gọn (dưới 25 từ) "
        f"để tương tác chéo với bài viết sau của người khác trên Facebook:\n"
        f"'{post_text}'\n"
        f"Yêu cầu:\n"
        f"- Viết một câu thật tích cực, khen ngợi, hoặc đồng tình mạnh mẽ với tác giả.\n"
        f"- Không quảng cáo sản phẩm của mình, không giới thiệu shop hay spam.\n"
        f"- Chèn biểu tượng cảm xúc phù hợp, viết tự nhiên bằng tiếng Việt.\n"
        f"Chỉ trả về nội dung câu bình luận, không có dấu ngoặc kép."
    )

    try:
        from automation import call_g4f
        reply = call_g4f(prompt).strip()
        if reply and len(reply) > 5 and len(reply) < 200:
            return reply
    except Exception as e_g4f:
        pass
        
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        import urllib.request
        import json
        req = urllib.request.Request(
            gemini_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"[AutoLike-AI] Error calling Gemini: {e}")
        return "Bài viết hay quá bạn ơi! 😍"

# ─────────────────────────────────────────
# SHOPEE SCRAPER
# ─────────────────────────────────────────
def scrape_shopee_product(url):
    """Access a Shopee product link and scrape basic text & title."""
    print(f"[ShopeeScraper] Scraping URL: {url}")
    result = {'title': '', 'description': '', 'price': ''}
    with sync_playwright() as p:
        browser = None
        try:
            browser = _launch_browser(p)
            context = _make_context(browser)
            page = context.new_page()
            page.goto(url, wait_until='domcontentloaded', timeout=60000)
            
            # Wait for redirect to complete (non-blocking sleep)
            for _ in range(25):
                if 's.shopee.vn' not in page.url and 'shope.ee' not in page.url and 'shp.ee' not in page.url:
                    break
                page.wait_for_timeout(500)
                
            try:
                page.wait_for_load_state('networkidle', timeout=15000)
            except Exception:
                try:
                    page.wait_for_load_state('load', timeout=10000)
                except Exception:
                    pass
            page.wait_for_timeout(3000)  # Wait for JS execution and DOM stabilization
            
            # If the page contains an iframe with product src, navigate to it directly
            try:
                iframe_el = None
                try:
                    iframe_el = page.wait_for_selector('iframe#main-iframe, iframe', timeout=10000)
                except Exception:
                    pass
                if iframe_el:
                    iframe_src = iframe_el.get_attribute('src')
                    if iframe_src and ('shopee.vn/' in iframe_src or 'shope.ee/' in iframe_src):
                        print(f"[ShopeeScraper] Found iframe container. Redirecting directly to: {iframe_src}")
                        page.goto(iframe_src, wait_until='domcontentloaded', timeout=60000)
                        try:
                            page.wait_for_load_state('networkidle', timeout=10000)
                        except Exception:
                            pass
                        page.wait_for_timeout(2000)
            except Exception as iframe_ex:
                print(f"[ShopeeScraper] Iframe redirect bypass failed: {iframe_ex}")
            
            # Safe query helper to catch and retry on navigation/destroyed context/document adoption issues
            def safe_query(selector):
                for _ in range(5):
                    try:
                        return page.query_selector(selector)
                    except Exception as e:
                        err_str = str(e).lower()
                        if any(x in err_str for x in ["destroyed", "navigation", "adopt", "context", "protocol", "node"]):
                            page.wait_for_timeout(1000)
                            continue
                        raise e
                return None

            def safe_query_all(selector):
                for _ in range(5):
                    try:
                        return page.query_selector_all(selector)
                    except Exception as e:
                        err_str = str(e).lower()
                        if any(x in err_str for x in ["destroyed", "navigation", "adopt", "context", "protocol", "node"]):
                            page.wait_for_timeout(1000)
                            continue
                        raise e
                return []

            def safe_attribute(selector, attr):
                for _ in range(5):
                    try:
                        el = page.query_selector(selector)
                        if el:
                            return el.get_attribute(attr)
                        return None
                    except Exception as e:
                        err_str = str(e).lower()
                        if any(x in err_str for x in ["destroyed", "navigation", "adopt", "context", "protocol", "node"]):
                            page.wait_for_timeout(1000)
                            continue
                        raise e
                return None

            def safe_inner_text(selector):
                for _ in range(5):
                    try:
                        el = page.query_selector(selector)
                        if el:
                            return el.inner_text()
                        return None
                    except Exception as e:
                        err_str = str(e).lower()
                        if any(x in err_str for x in ["destroyed", "navigation", "adopt", "context", "protocol", "node"]):
                            page.wait_for_timeout(1000)
                            continue
                        raise e
                return None

            # Fetch Title (wait for Javascript to update it from "Loading..." or "Shopee")
            title = page.title()
            for _ in range(15):
                if title and not title.lower().startswith('loading') and not title.lower().startswith('đang tải') and title.strip() != 'Shopee':
                    break
                page.wait_for_timeout(1000)
                title = page.title()
                
            if title:
                title = title.replace('| Shopee Việt Nam', '').replace('| Shopee.vn', '').strip()
            result['title'] = title or ''
            
            # Fetch Image
            og_img = safe_attribute('meta[property="og:image"]', 'content')
            image_urls = []
            if og_img:
                image_urls.append(og_img)
            
            # Find carousel or other product images
            try:
                img_els = safe_query_all('img')
                for img in img_els:
                    try:
                        src = img.get_attribute('src')
                        if src:
                            # Shopee images CDN domains
                            if 'susercontent.com/file/' in src or 'shopee.vn/file/' in src or 'cf.shopee.vn' in src:
                                # Clean thumbnail suffix if present
                                clean_src = src.split('_tn')[0].split('_xx')[0]
                                if clean_src not in image_urls:
                                    image_urls.append(clean_src)
                    except Exception:
                        continue # Skip elements that got destroyed mid-loop
            except Exception as img_err:
                print(f"[ShopeeScraper] Lỗi quét danh sách ảnh: {img_err}")
                
            result['image_url'] = image_urls[0] if image_urls else ''
            result['image_urls'] = image_urls[:5]
            
            # Fetch Description / Body content
            meta_d_val = safe_attribute('meta[property="og:description"]', 'content')
            if meta_d_val:
                result['description'] = meta_d_val
            else:
                body_text = safe_inner_text('body')
                if body_text:
                    result['description'] = body_text[:2500].strip()
                    
            print(f"[ShopeeScraper] Scraped title length: {len(result['title'])}")
        except Exception as e:
            print(f"[ShopeeScraper] Error scraping: {e}")
            result['error'] = str(e)
        finally:
            if browser:
                try: browser.close()
                except Exception: pass
    return result


# ─────────────────────────────────────────
# UNIFIED GEMINI HELPER WITH MODEL FALLBACKS
# ─────────────────────────────────────────
def call_claude(api_key, prompt, system_instruction=None):
    """Calls Claude API with fallbacks: 3.5-haiku -> 3.5-sonnet -> 3-haiku."""
    models = ["claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]
    import urllib.request
    import json
    
    url = "https://api.anthropic.com/v1/messages"
    payload = {
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }
    if system_instruction:
        payload["system"] = system_instruction
        
    for model in models:
        payload["model"] = model
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01'
                }
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                return res_data['content'][0]['text'].strip()
        except Exception as e:
            print(f"[Claude-Helper] Model {model} failed: {e}. Trying fallback...")
            continue
            
    raise Exception("All Claude models failed.")

def call_g4f(prompt, system_instruction=None):
    """Calls free AI models via g4f (GPT4Free) without API keys."""
    import g4f
    from g4f.client import Client
    
    try:
        print("[G4F-Helper] Sending request to free AI provider via g4f...")
        client = Client()
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=g4f.models.default,
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[G4F-Helper] Failed to get response from g4f: {e}")
        raise Exception(f"g4f failed: {e}")

def call_gemini(api_key, prompt, system_instruction=None):
    """Unified AI helper that routes to either Gemini or Claude based on DB settings."""
    import database
    try:
        settings = database.get_settings()
    except Exception:
        settings = {}
        
    ai_engine = settings.get('ai_engine', 'gemini')
    claude_key = settings.get('claude_api_key', '').strip()
    
    if ai_engine == 'g4f':
        print("[AI-Helper] Routing request to free AI (g4f)...")
        try:
            return call_g4f(prompt, system_instruction)
        except Exception as g4f_err:
            print(f"[AI-Helper] g4f failed: {g4f_err}. Falling back to Gemini...")
            
    if ai_engine == 'claude' and claude_key:
        print("[AI-Helper] Routing request to Claude...")
        try:
            return call_claude(claude_key, prompt, system_instruction)
        except Exception as claude_err:
            print(f"[AI-Helper] Claude failed: {claude_err}. Falling back to Gemini...")
            
    # Default Gemini actual call
    models = ["gemini-2.5-flash", "gemini-3.5-flash", "gemini-3.1-flash-lite", "gemini-flash-latest", "gemini-2.0-flash"]
    import urllib.request
    import json
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
        
    import time
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        retries = 3
        for attempt in range(retries):
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                with urllib.request.urlopen(req, timeout=40) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    return res_data['candidates'][0]['content']['parts'][0]['text'].strip()
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    wait_time = 5 * (attempt + 1)
                    print(f"[Gemini-Helper] Model {model} rate limited (429). Waiting {wait_time}s and retrying...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"[Gemini-Helper] Model {model} HTTP error: {e}. Trying next model...")
                    break
            except Exception as e:
                print(f"[Gemini-Helper] Model {model} failed: {e}. Trying next model...")
                break
            
    raise Exception("All Gemini models failed (rate limit or errors).")


# ─────────────────────────────────────────
# ENGAGEMENT: GEMINI COMMENT REPLY
# ─────────────────────────────────────────
def get_gemini_reply(page_name, comment_text, rule_instruction):
    """Call Gemini to write a custom, natural comment reply."""
    import database
    settings = database.get_settings()
    api_key = settings.get('gemini_api_key', '').strip()
    if not api_key:
        print("[Engage-AI] No Gemini API key found. Falling back to default.")
        return "Cảm ơn bạn đã quan tâm! Bạn check inbox shop nhé."
        
    prompt = (
        f"Bạn là đại diện của trang Facebook '{page_name}'. "
        f"Hãy viết một câu trả lời bình luận cực kỳ tự nhiên, thân thiện và ngắn gọn (dưới 30 từ) "
        f"để phản hồi bình luận sau của khách hàng: '{comment_text}'.\n"
    )
    if rule_instruction and rule_instruction != '[AI]' and rule_instruction != '[Gemini]':
        prompt += f"Yêu cầu về giọng điệu/nội dung: {rule_instruction.replace('[AI]', '').replace('[Gemini]', '').strip()}\n"
    else:
        prompt += "Giọng điệu: Thân thiện, chèn biểu tượng cảm xúc sinh động."

    try:
        return call_gemini(api_key, prompt)
    except Exception as e:
        print(f"[Engage-AI] Error calling Gemini: {e}")
        return "Dạ cảm ơn bạn nhiều ạ! Bạn inbox shop nhé."


# ─────────────────────────────────────────
# AUTO-BUMP: COMMENT ON ARTICLE
# ─────────────────────────────────────────
def post_article_comment(account_cookie, post_url, comment_text):
    """Navigate to a post URL and write a comment on it."""
    try:
        import database
        db_settings = database.get_settings()
        speed_mode = db_settings.get('engage_speed_mode', 'turbo')
    except Exception:
        speed_mode = 'turbo'

    if speed_mode == 'turbo':
        type_delay = 1
        delay_hover = 0.1
        delay_focus = 0.1
        delay_type_end = 0.1
        delay_after_enter = 0.5
    else:
        type_delay = 60
        delay_hover = 0.8
        delay_focus = 0.8
        delay_type_end = 1.0
        delay_after_enter = 4.0

    try:
        cookies = parse_cookies(account_cookie)
    except Exception as e:
        print(f"[AutoBump] Cookie parse error: {e}")
        return False
    if not cookies:
        return False

    success = False
    with sync_playwright() as p:
        browser = None
        try:
            print(f"[AutoBump] Posting bump comment on: {post_url}")
            browser = _launch_browser(p)
            context = _make_context(browser)
            context.add_cookies(cookies)
            page = context.new_page()
            page.goto(post_url, wait_until='domcontentloaded', timeout=60000)
            time.sleep(5)
            _check_logged_in(page)

            # Switch sorting to All comments to ensure nothing is hidden
            _switch_to_all_comments(page)

            # Find comment box
            comment_box = None
            comment_box_selectors = [
                'div[role="textbox"]',
                'div[contenteditable="true"]',
                '[aria-label*="bình luận" i]',
                '[aria-label*="comment" i]'
            ]
            for sel in comment_box_selectors:
                el = page.locator(sel).first
                if el.count() > 0 and el.is_visible():
                    comment_box = el
                    break

            if comment_box:
                comment_box.hover()
                time.sleep(delay_hover)
                comment_box.click() # Click to activate editor
                time.sleep(delay_focus)
                success = _type_and_submit_comment(page, comment_box, comment_text, type_delay, delay_focus, delay_type_end, delay_after_enter)
                print("[AutoBump] Bump comment posted successfully.")
            else:
                print("[AutoBump] Could not find comment textbox.")
        except Exception as e:
            print(f"[AutoBump] Error: {e}")
        finally:
            if browser:
                try: browser.close()
                except Exception: pass
    return success


# ─────────────────────────────────────────
# META THREADS POSTER
# ─────────────────────────────────────────
def publish_threads_post(account_cookie, content, media_paths, post_id, first_comment=None):
    """Publish a post to threads.net using Playwright web intent."""
    try:
        cookies = parse_cookies(account_cookie, platform='threads')
    except Exception as e:
        return {'success': False, 'log': f'Cookie error: {str(e)}', 'screenshot': ''}

    if not cookies:
        return {'success': False, 'log': 'No valid cookies found.', 'screenshot': ''}

    result = {'success': False, 'log': '', 'screenshot': ''}
    content = spin_text(content)

    with sync_playwright() as p:
        browser = None
        try:
            print(f"[ThreadsPoster] Launching browser for post {post_id}...")
            browser = _launch_browser(p)
            context = _make_context(browser)
            context.add_cookies(cookies)
            page = context.new_page()

            # Navigate to Threads intent post URL
            import urllib.parse
            encoded_text = urllib.parse.quote(content)
            intent_url = f"https://www.threads.net/intent/post?text={encoded_text}"
            
            print(f"[ThreadsPoster] Navigating to: {intent_url}")
            page.goto(intent_url, wait_until='domcontentloaded', timeout=60000)
            time.sleep(6)

            # Check if redirected to login page
            if "login" in page.url or page.query_selector('input[name="username"]') or page.query_selector('input[type="password"]'):
                raise Exception("Cookie expired - redirected to Threads login page.")

            # Check if composer textbox is visible
            textbox = None
            textbox_selectors = [
                'div[role="textbox"]',
                'div[aria-label="Start a thread..."]',
                'div[aria-label="Bắt đầu luồng..."]',
                'textarea[placeholder*="thread"]',
            ]
            for sel in textbox_selectors:
                el = page.query_selector(sel)
                if el:
                    textbox = el
                    break

            # Handle media upload
            if media_paths:
                print(f"[ThreadsPoster] Uploading media files: {media_paths}")
                file_input = page.locator('input[type="file"]')
                if file_input.count() > 0:
                    resolved = [os.path.abspath(os.path.join('uploads', m)) if not os.path.isabs(m) else m
                                for m in media_paths if os.path.exists(os.path.abspath(os.path.join('uploads', m)) if not os.path.isabs(m) else m)]
                    if resolved:
                        file_input.first.set_input_files(resolved)
                        time.sleep(5)
                else:
                    print("[ThreadsPoster] No file input found for media upload.")

            # Click the post button
            post_btn = None
            post_selectors = [
                'div[role="button"]:has-text("Post")',
                'div[role="button"]:has-text("Đăng")',
                'button:has-text("Post")',
                'button:has-text("Đăng")',
                'div[role="button"][aria-label="Post"]',
                'div[role="button"][aria-label="Đăng"]',
            ]
            for sel in post_selectors:
                locs = page.locator(sel)
                if locs.count() > 0:
                    post_btn = locs.first
                    print(f"[ThreadsPoster] Found post button using selector: {sel}")
                    break

            if not post_btn:
                try:
                    post_btn = page.get_by_role("button", name=re.compile("Post|Đăng", re.IGNORECASE)).first
                except Exception:
                    pass

            if not post_btn:
                raise Exception("Cannot find Post button on Threads composer.")

            post_btn.hover()
            time.sleep(random.uniform(0.5, 1.0))
            post_btn.click()
            print("[ThreadsPoster] Post button clicked. Waiting for post completion...")
            time.sleep(10) # Wait for upload and post completion

            result['log'] = 'Đăng bài Threads thành công.'
            
            # Auto-comment on Threads
            if first_comment and len(first_comment.strip()) > 0:
                print(f"[ThreadsPoster] Writing first comment: {first_comment}")
                try:
                    # Locate the reply button on the page
                    reply_btn = None
                    reply_selectors = [
                        'div[role="button"][aria-label="Reply"]',
                        'div[role="button"][aria-label="Phản hồi"]',
                        'svg[aria-label="Reply"]',
                        'svg[aria-label="Phản hồi"]',
                        'div[role="button"]:has(svg[aria-label="Reply"])',
                        'div[role="button"]:has(svg[aria-label="Phản hồi"])'
                    ]
                    for r_sel in reply_selectors:
                        try:
                            el = page.locator(r_sel).first
                            if el and el.count() > 0 and el.is_visible():
                                reply_btn = el
                                break
                        except:
                            pass
                    
                    if reply_btn:
                        reply_btn.click(force=True)
                        time.sleep(3)
                        
                        reply_textbox = None
                        reply_textbox_selectors = [
                            'div[role="textbox"]',
                            'div[aria-label="Reply to..."]',
                            'div[aria-label*="Phản hồi"]',
                            'div[contenteditable="true"]'
                        ]
                        for rt_sel in reply_textbox_selectors:
                            try:
                                el = page.locator(rt_sel).first
                                if el and el.count() > 0 and el.is_visible():
                                    reply_textbox = el
                                    break
                            except:
                                pass
                        
                        if reply_textbox:
                            reply_textbox.focus()
                            reply_textbox.fill(first_comment)
                            time.sleep(1)
                            
                            reply_post_btn = None
                            reply_post_selectors = [
                                'div[role="button"]:has-text("Post")',
                                'div[role="button"]:has-text("Đăng")',
                                'button:has-text("Post")',
                                'button:has-text("Đăng")',
                                'div[role="button"][aria-label="Post"]',
                                'div[role="button"][aria-label="Đăng"]',
                            ]
                            for rp_sel in reply_post_selectors:
                                try:
                                    el = page.locator(rp_sel).first
                                    if el and el.count() > 0 and el.is_visible():
                                        reply_post_btn = el
                                        break
                                except:
                                    pass
                            
                            if reply_post_btn:
                                reply_post_btn.click(force=True)
                                print("[ThreadsPoster] Reply submitted successfully.")
                                time.sleep(3)
                                result['log'] += ' Đã gửi bình luận tự động thành công.'
                            else:
                                print("[ThreadsPoster] Cannot find reply post button.")
                                result['log'] += ' Gửi bình luận tự động thất bại (Không tìm thấy nút đăng phản hồi).'
                        else:
                            print("[ThreadsPoster] Cannot find reply textbox.")
                            result['log'] += ' Gửi bình luận tự động thất bại (Không tìm thấy ô nhập phản hồi).'
                    else:
                        print("[ThreadsPoster] Cannot find reply button.")
                        result['log'] += ' Gửi bình luận tự động thất bại (Không tìm thấy nút Phản hồi bài viết).'
                except Exception as comm_err:
                    print(f"[ThreadsPoster] Error posting comment: {comm_err}")
                    result['log'] += f' Gửi bình luận tự động thất bại (Lỗi: {comm_err}).'

            result['success'] = True
            result['screenshot'] = _take_screenshot(page, 'success_threads', post_id)
            print(f"[ThreadsPoster] Post {post_id} completed successfully on Threads.")

        except Exception as err:
            print(f"[ThreadsPoster] Error: {str(err)}")
            result['success'] = False
            result['log'] = f'Lỗi: {str(err)}'
            try:
                result['screenshot'] = _take_screenshot(page, 'error_threads', post_id)
            except Exception:
                pass
        finally:
            if browser:
                try: browser.close()
                except Exception: pass

    return result


# ─────────────────────────────────────────
# AUTO-FEED ENGAGEMENT
# ─────────────────────────────────────────
def get_gemini_comment(account_name, post_author, post_content):
    """Call Gemini to write a custom, natural comment for a post on Facebook."""
    import database
    settings = database.get_settings()
    api_key = settings.get('gemini_api_key', '').strip()
    if not api_key:
        print("[Auto-Feed-AI] No Gemini API key found. Falling back to default.")
        return "Bài viết hay quá ạ!"
        
    prompt = (
        f"Bạn là người dùng Facebook tên '{account_name}'. "
        f"Hãy viết một câu bình luận tương tác cực kỳ tự nhiên, thân thiện và ngắn gọn (dưới 20 từ) "
        f"vào bài viết của '{post_author}' trên Facebook.\n"
        f"Nội dung bài viết: '{post_content}'\n"
        f"Lưu ý: Không dùng ngôn ngữ quá trang trọng, hãy giống người dùng bình thường chia sẻ/khen ngợi, thêm biểu tượng cảm xúc sinh động, không spam."
    )

    try:
        return call_gemini(api_key, prompt)
    except Exception as e:
        print(f"[Auto-Feed-AI] Error calling Gemini: {e}")
        return "Bài viết hay quá bạn ơi!"



def is_post_recent(time_text, max_days=10, now=None):
    if not time_text:
        return True # Fallback to True if we cannot extract

    text_lower = time_text.lower().strip()
    
    # 1. Just now / Just finished
    if any(w in text_lower for w in ["vừa xong", "vừa mới", "just now", "giây", "second", "sec"]):
        return True

    # 2. Hours and Minutes (recent)
    # Match strings containing "phút", "giờ", "min", "hr", "lúc", "at"
    # Ensure they don't have day/week/month/year words.
    if any(w in text_lower for w in ["phút", "giờ", "min", "hr", "lúc", "at"]):
        if not any(w in text_lower for w in ["ngày", "tuần", "tháng", "năm", "day", "week", "month", "year", "thg"]):
            return True

    # Check for short relative formats like "5m", "3h", "23h", "10m"
    # Match numbers followed by m, h, s (with optional spaces)
    if re.search(r'\b\d+\s*[mhs]\b', text_lower):
        if not any(w in text_lower for w in ["ngày", "tuần", "tháng", "năm", "day", "week", "month", "year", "thg"]):
            # Also ensure it's not a day/week indicator like "10d"
            if not re.search(r'\b\d+\s*[dwy]\b', text_lower):
                return True

    # 3. Yesterday / Hôm qua
    if "hôm qua" in text_lower or "yesterday" in text_lower:
        return True

    # 4. Check for X days / X ngày / X d
    day_match = re.search(r'\b(\d+)\s*(?:ngày|day|d)\b', text_lower)
    if day_match:
        days = int(day_match.group(1))
        return days <= max_days

    # 5. Check for X weeks / X tuần / X w
    week_match = re.search(r'\b(\d+)\s*(?:tuần|week|w)\b', text_lower)
    if week_match:
        weeks = int(week_match.group(1))
        return (weeks * 7) <= max_days

    # 6. Check for X years / X năm / X y (old)
    year_match = re.search(r'\b(\d+)\s*(?:năm|year|y)\b', text_lower)
    if year_match:
        return False

    # 7. Check for X months / X tháng / X thg / X month (old)
    # But distinguish between "2 tháng trước" (relative) and "18 tháng 6" (absolute)
    # Vietnamese calendar date
    date_vn_match = re.search(r'\b(\d{1,2})\s*(?:tháng|thg)\s*(\d{1,2})\b(?:\s*(?:năm|,)?\s*(\d{2,4})\b)?', text_lower)
    if date_vn_match:
        day = int(date_vn_match.group(1))
        month = int(date_vn_match.group(2))
        year = int(date_vn_match.group(3)) if date_vn_match.group(3) else None
        return check_absolute_date(day, month, year, max_days, now)

    # Date slash/dash format (e.g. 18/6, 18-6, 18/6/2026)
    date_slash_match = re.search(r'\b(\d{1,2})[\/\-](\d{1,2})\b(?:[\/\-](\d{2,4})\b)?', text_lower)
    if date_slash_match:
        day = int(date_slash_match.group(1))
        month = int(date_slash_match.group(2))
        year = int(date_slash_match.group(3)) if date_slash_match.group(3) else None
        return check_absolute_date(day, month, year, max_days, now)

    # Absolute dates in English: "June 18", "18 Jun", "18 June", "Jun 18"
    months_en = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    
    month_name_regex = '|'.join(months_en.keys())
    
    # Match "June 18" or "Jun 18"
    date_en_match1 = re.search(rf'\b({month_name_regex})\s+(\d{{1,2}})\b(?:\s*,?\s*(\d{{2,4}})\b)?', text_lower)
    if date_en_match1:
        month = months_en[date_en_match1.group(1)]
        day = int(date_en_match1.group(2))
        year = int(date_en_match1.group(3)) if date_en_match1.group(3) else None
        return check_absolute_date(day, month, year, max_days, now)

    # Match "18 June" or "18 Jun"
    date_en_match2 = re.search(rf'\b(\d{{1,2}})\s+({month_name_regex})\b(?:\s*,?\s*(\d{{2,4}})\b)?', text_lower)
    if date_en_match2:
        day = int(date_en_match2.group(1))
        month = months_en[date_en_match2.group(2)]
        year = int(date_en_match2.group(3)) if date_en_match2.group(3) else None
        return check_absolute_date(day, month, year, max_days, now)

    # Relative months: e.g. "2 tháng", "2 months" (definitely old)
    if any(w in text_lower for w in ["tháng", "month"]):
        return False

    return True

def check_absolute_date(day, month, year, max_days, now=None):
    from datetime import datetime
    if now is None:
        now = datetime.now()
        
    if not year:
        year = now.year
    elif year < 100:
        year += 2000
        
    try:
        post_date = datetime(year, month, day)
        if post_date > now:
            post_date = datetime(year - 1, month, day)
        delta = (now - post_date).days
        return delta <= max_days
    except Exception as e:
        print(f"Error parsing date {day}/{month}/{year}: {e}")
        return True


def auto_engage_feed_posts(account_cookie, account_name, source='groups', max_posts=5, comment_style='AI', comment_text=''):
    """
    Auto engage with posts on FB feed (News Feed or Groups Feed).
    Likes and comments on up to `max_posts` active posts by other users.
    """
    try:
        import database
        db_settings = database.get_settings()
        speed_mode = db_settings.get('engage_speed_mode', 'turbo')
    except Exception:
        speed_mode = 'turbo'

    if speed_mode == 'turbo':
        type_delay = 1
        delay_like = 0.2
        delay_after_like = 0.2
        delay_focus = 0.1
        delay_type_end = 0.1
        delay_after_enter = 0.5
        delay_between = 0.5
    else:
        type_delay = 60
        delay_like = 1.0
        delay_after_like = 2.0
        delay_focus = 0.5
        delay_type_end = 1.0
        delay_after_enter = 5.0
        delay_between = 7.0

    try:
        cookies = parse_cookies(account_cookie)
    except Exception as e:
        return {'success': False, 'log': f'Lỗi cookie: {str(e)}', 'logs': []}

    if not cookies:
        return {'success': False, 'log': 'Không tìm thấy cookie hợp lệ.', 'logs': []}

    feed_url = 'https://www.facebook.com/groups/feed/' if source == 'groups' else 'https://www.facebook.com/'
    logs = []
    success_count = 0
    processed_hashes = set()

    with sync_playwright() as p:
        browser = None
        try:
            print(f"[Auto-Feed] Bắt đầu tự động tương tác bảng tin cho tài khoản: {account_name}")
            browser = _launch_browser(p)
            context = _make_context(browser)
            context.add_cookies(cookies)
            page = context.new_page()
            
            target_groups = []
            if source == 'groups':
                try:
                    import database
                    all_accounts = database.get_accounts()
                    account_id = None
                    for acc in all_accounts:
                        if acc['name'] == account_name:
                            account_id = acc['id']
                            break
                    if account_id:
                        conn = database.get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT target_url FROM autolike_targets WHERE account_id=? AND status='active';", (account_id,))
                        target_groups = [row[0] for row in cursor.fetchall()]
                        conn.close()
                except Exception as e:
                    print(f"[Auto-Feed] Lỗi truy vấn nhóm mục tiêu: {e}")
                    target_groups = []

                # Limit to 10 target groups
                target_groups = target_groups[:10]

            urls_to_visit = target_groups if (source == 'groups' and target_groups) else [feed_url]
            is_direct_groups = (source == 'groups' and len(target_groups) > 0)

            for visit_url in urls_to_visit:
                if success_count >= max_posts:
                    break

                print(f"[Auto-Feed] Điều hướng tới: {visit_url}")
                try:
                    page.goto(visit_url, wait_until='domcontentloaded', timeout=60000)
                    time.sleep(4)
                    _check_logged_in(page)
                except Exception as goto_err:
                    print(f"[Auto-Feed] Lỗi truy cập {visit_url}: {goto_err}")
                    continue

                scrolled_times = 0
                max_scrolls_for_this = 2 if is_direct_groups else 15

                while success_count < max_posts and scrolled_times < max_scrolls_for_this:
                    # Find all unliked Like buttons (not already liked)
                    like_buttons = page.locator(
                        'div[role="button"]:has-text("Thích"):not([aria-pressed="true"]), '
                        'div[role="button"]:has-text("Like"):not([aria-pressed="true"]), '
                        'div[role="button"][aria-label*="Thích" i]:not([aria-pressed="true"]), '
                        'div[role="button"][aria-label*="Like" i]:not([aria-pressed="true"])'
                    )
                    count = like_buttons.count()
                    print(f"[Auto-Feed] Tìm thấy {count} nút Thích chưa bấm trên màn hình.")
                    
                    if count == 0:
                        page.evaluate("window.scrollBy(0, 800)")
                        time.sleep(random.uniform(2.5, 4.0))
                        scrolled_times += 1
                        continue

                    posts_to_interact = min(count, 1) if is_direct_groups else count

                    for i in range(posts_to_interact):
                        if success_count >= max_posts:
                            break
                        
                        try:
                            btn = like_buttons.nth(i)
                            if not btn.is_visible():
                                continue
                            
                            post_container = btn.locator('xpath=./ancestor::div[@role="article" or contains(@class, "x1y1aw1k") or contains(@class, "x1lq5wtb") or contains(@class, "userContentWrapper")][1]')
                            if post_container.count() == 0:
                                continue
                            
                            details = post_container.first.evaluate(r'''el => {
                                let author = "";
                                let authorLink = el.querySelector('h3 a[role="link"], h2 a[role="link"], a[role="link"][tabindex="0"]');
                                if (authorLink) {
                                    author = authorLink.innerText.trim();
                                }
                                if (!author) {
                                    let links = el.querySelectorAll('a[role="link"]');
                                    for (let l of links) {
                                        let txt = l.innerText.trim();
                                        if (txt && txt.length > 2 && !txt.includes('\\n') && isNaN(txt)) {
                                            author = txt;
                                            break;
                                        }
                                    }
                                }
                                
                                let content = "";
                                let contentEl = el.querySelector('div[data-ad-preview="message"], div[data-testid="post_message"], div.x1y1aw1k div.x11i5rnm, div.xzsf02u');
                                if (contentEl) {
                                    content = contentEl.innerText.trim();
                                } else {
                                    let textBlocks = el.querySelectorAll('div[dir="auto"]');
                                    let blocks = [];
                                    for (let tb of textBlocks) {
                                        let txt = tb.innerText.trim();
                                        if (txt && !tb.querySelector('a') && txt.length > 5) {
                                            blocks.push(txt);
                                        }
                                    }
                                    content = blocks.join("\\n").trim();
                                }
                                
                                let isSponsored = false;
                                let textLower = el.innerText.toLowerCase();
                                if (textLower.includes("được tài trợ") || textLower.includes("sponsored")) {
                                    isSponsored = true;
                                }
                                
                                let timeText = "";
                                let links = el.querySelectorAll('a[role="link"]');
                                for (let l of links) {
                                    let txt = l.innerText.trim();
                                    if (txt) {
                                        let txtLower = txt.toLowerCase();
                                        if (
                                            txtLower.includes("phút") || txtLower.includes("giờ") || 
                                            txtLower.includes("ngày") || txtLower.includes("tuần") || 
                                            txtLower.includes("tháng") || txtLower.includes("năm") ||
                                            txtLower.includes("hôm qua") || txtLower.includes("yesterday") ||
                                            txtLower.includes("min") || txtLower.includes("hr") || 
                                            txtLower.includes("day") || txtLower.includes("week") || 
                                            txtLower.includes("month") || txtLower.includes("year") ||
                                            /^\d+ [a-zA-Z]/.test(txtLower)
                                        ) {
                                            if (txt.length < 30 && !txtLower.includes("thích") && !txtLower.includes("comment") && !txtLower.includes("like") && !txtLower.includes("bày tỏ cảm xúc")) {
                                                timeText = txt;
                                                break;
                                            }
                                        }
                                    }
                                }
                                
                                return {
                                    author: author || "Người dùng Facebook",
                                    content: content || "",
                                    isSponsored: isSponsored,
                                    timeText: timeText
                                };
                            }''')
                            
                            author = details.get('author', 'Người dùng Facebook')
                            content = details.get('content', '')
                            is_sponsored = details.get('isSponsored', False)
                            time_text = details.get('timeText', '')
                            
                            post_hash = f"{author}_{content[:100]}"
                            if post_hash in processed_hashes:
                                continue
                            processed_hashes.add(post_hash)
    
                            if (is_sponsored):
                                print(f"[Auto-Feed] Bỏ qua bài viết được tài trợ của {author}.")
                                continue
    
                            # Filter by age (10 days limit)
                            if not is_post_recent(time_text, max_days=10):
                                try:
                                    time_text_safe = time_text.encode('ascii', 'ignore').decode('ascii')
                                except Exception:
                                    time_text_safe = "old"
                                print(f"[Auto-Feed] Bỏ qua bài viết quá 10 ngày của {author} ({time_text_safe}).")
                                continue
    
                            if author.lower() in account_name.lower() or account_name.lower() in author.lower():
                                print(f"[Auto-Feed] Bỏ qua bài viết của chính chủ: {author}.")
                                continue
    
                            print(f"[Auto-Feed] Đang tương tác bài viết của: {author} | Nội dung: {content[:80]}...")
                            
                            post_url = "https://www.facebook.com/feed_post"
                            try:
                                href = post_container.evaluate('''el => {
                                    let links = el.querySelectorAll('a[role="link"]');
                                    for (let l of links) {
                                        if (l.href && (l.href.includes("/posts/") || l.href.includes("/permalink/") || l.href.includes("/groups/"))) {
                                            return l.href;
                                        }
                                    }
                                    return "";
                                }''')
                                if href:
                                    post_url = href
                            except Exception:
                                pass
    
                            btn.scroll_into_view_if_needed()
                            time.sleep(delay_focus)
                            btn.hover(timeout=2000, force=True)
                            time.sleep(delay_focus)
                            btn.click(timeout=2000, force=True)
                            print(f"[Auto-Feed] Đã thả tim bài viết.")
                            time.sleep(delay_after_like)
    
                            final_comment = ""
                            if comment_style == 'AI':
                                final_comment = get_gemini_comment(account_name, author, content)
                            else:
                                final_comment = spin_text(comment_text)
                            
                            if not final_comment:
                                final_comment = "Tuyệt vời quá bạn ơi!"
    
                            comment_box = None
                            comment_box_selectors = [
                                'div[role="textbox"]',
                                'div[contenteditable="true"]',
                                '[aria-label*="bình luận" i]',
                                '[aria-label*="comment" i]'
                            ]
                            for sel in comment_box_selectors:
                                el = post_container.locator(sel).first
                                if el.count() > 0 and el.is_visible():
                                    comment_box = el
                                    break
    
                            if not comment_box:
                                comment_btn = None
                                comment_btn_selectors = [
                                    'div[role="button"]:has-text("Bình luận")',
                                    'div[role="button"]:has-text("Comment")',
                                    'div[role="button"][aria-label*="bình luận" i]',
                                    'div[role="button"][aria-label*="comment" i]'
                                ]
                                for sel in comment_btn_selectors:
                                    el = post_container.locator(sel).first
                                    if el.count() > 0 and el.is_visible():
                                        comment_btn = el
                                        break
    
                                if comment_btn:
                                    comment_btn.hover(timeout=2000, force=True)
                                    time.sleep(delay_focus)
                                    comment_btn.click(timeout=2000, force=True)
                                    time.sleep(delay_after_like)
                                    _switch_to_all_comments(page, container=post_container)
                                    for sel in comment_box_selectors:
                                        el = post_container.locator(sel).first
                                        if el.count() > 0 and el.is_visible():
                                            comment_box = el
                                            break
                            else:
                                _switch_to_all_comments(page, container=post_container)
    
                            comment_success = False
                            if comment_box:
                                comment_box.hover(timeout=2000, force=True)
                                time.sleep(delay_focus)
                                comment_box.click(timeout=2000, force=True) # Click to activate editor
                                time.sleep(delay_focus)
                                comment_success = _type_and_submit_comment(page, comment_box, final_comment, type_delay, delay_focus, delay_type_end, delay_after_enter)
                                print(f"[Auto-Feed] Đã bình luận: '{final_comment}'")
                            else:
                                print(f"[Auto-Feed] Không tìm thấy ô nhập bình luận cho bài viết của {author}.")
    
                            screenshot_path = _take_screenshot(page, 'autofeed', f"{success_count}_{int(time.time())}")
                            
                            logs.append({
                                'post_url': post_url,
                                'commenter_name': author,
                                'comment_content': content[:200],
                                'reply_content': final_comment,
                                'status': 'success' if comment_success else 'like_only',
                                'screenshot': screenshot_path
                            })
    
                            success_count += 1
                            time.sleep(delay_between)
                            
                        except Exception as single_err:
                            print(f"[Auto-Feed] Lỗi khi xử lý bài viết: {single_err}")
                            continue
                    
                    if success_count < max_posts:
                        page.evaluate("window.scrollBy(0, 1000)")
                        time.sleep(random.uniform(3.0, 5.5))
                        scrolled_times += 1

            return {
                'success': True,
                'log': f'Đã hoàn thành tương tác {success_count} bài viết trên bảng tin.',
                'logs': logs
            }

        except Exception as err:
            print(f"[Auto-Feed] Lỗi hệ thống: {err}")
            return {
                'success': False,
                'log': f'Lỗi hệ thống: {str(err)}',
                'logs': logs
            }
        finally:
            if browser:
                try: browser.close()
                except Exception: pass

# ─────────────────────────────────────────
# AUTO-JOIN GROUPS
# ─────────────────────────────────────────
def auto_join_facebook_groups(account_id, account_cookie, account_name, group_inputs, keyword=None, limit=5, delay=15, answer_questions=True):
    import database
    from database import save_autojoin_log
    import urllib.parse
    
    try:
        cookies = parse_cookies(account_cookie)
    except Exception as e:
        err_msg = f"Lỗi cookie: {str(e)}"
        save_autojoin_log(account_id, keyword or "Danh sách nhóm", "failed", err_msg)
        return {'success': False, 'log': err_msg}

    if not cookies:
        err_msg = "Không tìm thấy cookie hợp lệ."
        save_autojoin_log(account_id, keyword or "Danh sách nhóm", "failed", err_msg)
        return {'success': False, 'log': err_msg}

    groups_to_process = []
    joined_urls = []
    if group_inputs:
        for line in group_inputs.split('\n'):
            line = line.strip()
            if line:
                groups_to_process.append(line)

    with sync_playwright() as p:
        browser = None
        try:
            print(f"[Auto-Join] Khởi động trình duyệt cho tài khoản {account_name}...")
            browser = _launch_browser(p)
            context = _make_context(browser)
            context.add_cookies(cookies)
            page = context.new_page()
            
            page.goto('https://www.facebook.com', wait_until='domcontentloaded', timeout=60000)
            time.sleep(3)
            _check_logged_in(page)

            if keyword:
                print(f"[Auto-Join] Đang tìm kiếm nhóm với từ khóa: {keyword}...")
                search_url = f"https://www.facebook.com/search/groups/?q={urllib.parse.quote(keyword)}"
                page.goto(search_url, wait_until='domcontentloaded', timeout=60000)
                time.sleep(5)
                
                page.evaluate("window.scrollBy(0, 800)")
                time.sleep(3)
                
                hrefs = page.evaluate('''() => {
                    const links = Array.from(document.querySelectorAll('a[href*="/groups/"]'));
                    return links.map(a => a.href);
                }''')
                
                unique_groups = []
                for href in hrefs:
                    if any(x in href for x in ['/feed/', '/discover/', '/joins/', '/categories/', '/create/']):
                        continue
                    match = re.search(r'/groups/([^/?#]+)', href)
                    if match:
                        g_id = match.group(1)
                        g_url = f"https://www.facebook.com/groups/{g_id}/"
                        if g_url not in unique_groups:
                            unique_groups.append(g_url)
                
                print(f"[Auto-Join] Tìm thấy {len(unique_groups)} nhóm từ kết quả tìm kiếm.")
                groups_to_process = unique_groups[:limit]

            if not groups_to_process:
                msg = "Không tìm thấy nhóm nào để tham gia."
                save_autojoin_log(account_id, keyword or "Danh sách nhóm", "failed", msg)
                return {'success': False, 'log': msg}

            # Save target list immediately so user sees all found groups on UI
            import hashlib
            from datetime import datetime
            if keyword:
                target_list_name = f"Từ khóa: {keyword} - {account_name}"
                list_id = 'list_kw_' + hashlib.md5((account_id + keyword).encode('utf-8')).hexdigest()[:8]
            else:
                target_list_name = f"Tự động tham gia - {account_name}"
                list_id = 'list_aj_' + hashlib.md5((account_id + str(datetime.now().timestamp())).encode('utf-8')).hexdigest()[:8]
            
            targets_str = "\n".join(groups_to_process)
            database.save_target_list(list_id, target_list_name, targets_str)
            print(f"[Auto-Join] Đã lập danh sách mục tiêu '{target_list_name}' với {len(groups_to_process)} nhóm.")

            print(f"[Auto-Join] Bắt đầu xử lý {len(groups_to_process)} nhóm...")
            success_count = 0
            
            for index, group in enumerate(groups_to_process):
                if not group.startswith('http'):
                    group_url = f"https://www.facebook.com/groups/{group}/"
                else:
                    group_url = group
                
                print(f"[Auto-Join] [{index+1}/{len(groups_to_process)}] Đang truy cập: {group_url}")
                try:
                    page.goto(group_url, wait_until='domcontentloaded', timeout=60000)
                    time.sleep(4)
                    
                    page_text = page.evaluate("document.body.innerText")
                    
                    if any(x in page_text for x in ["Đã tham gia", "Joined", "Được quản lý", "Manage"]):
                        print(f"[Auto-Join] Đã là thành viên của nhóm: {group_url}")
                        save_autojoin_log(account_id, group_url, "already_member", "Đã là thành viên của nhóm.")
                        joined_urls.append(group_url)
                        continue
                        
                    if any(x in page_text for x in ["Đã gửi yêu cầu", "Requested", "Hủy yêu cầu", "Cancel Request"]):
                        print(f"[Auto-Join] Đang chờ phê duyệt trong nhóm này: {group_url}")
                        save_autojoin_log(account_id, group_url, "pending_approval", "Yêu cầu tham gia đang chờ duyệt.")
                        joined_urls.append(group_url)
                        continue
                    
                    join_btn = None
                    btn_selectors = [
                        'div[role="button"]:has-text("Tham gia nhóm")',
                        'div[role="button"]:has-text("Join group")',
                        'div[role="button"]:has-text("Join Group")',
                        'div[role="button"]:has-text("Tham gia")',
                        'div[role="button"]:has-text("Join")',
                        'div[role="button"][aria-label*="Tham gia nhóm" i]',
                        'div[role="button"][aria-label*="Join group" i]',
                        'span:has-text("Tham gia nhóm")',
                        'span:has-text("Join group")'
                    ]
                    
                    for sel in btn_selectors:
                        try:
                            btn = page.locator(sel).first
                            if btn and btn.is_visible():
                                join_btn = btn
                                break
                        except:
                            pass
                            
                    if not join_btn:
                        buttons = page.query_selector_all('div[role="button"], button')
                        for btn in buttons:
                            text = btn.inner_text() or ""
                            if "tham gia" in text.lower() or "join" in text.lower():
                                join_btn = btn
                                break
                                
                    if join_btn:
                        print(f"[Auto-Join] Click nút tham gia...")
                        join_btn.click()
                        time.sleep(4)
                        
                        dialog = page.query_selector('div[role="dialog"]')
                        details = ""
                        
                        if dialog:
                            print(f"[Auto-Join] Phát hiện hộp thoại câu hỏi thành viên.")
                            dialog_text = dialog.inner_text()
                            
                            checkboxes = dialog.query_selector_all('input[type="checkbox"], div[role="checkbox"]')
                            for cb in checkboxes:
                                try:
                                    if cb.get_attribute('aria-checked') != 'true':
                                        cb.click()
                                        time.sleep(0.5)
                                except:
                                    pass
                            
                            text_inputs = dialog.query_selector_all('textarea, input[type="text"], div[role="textbox"]')
                            
                            if text_inputs and answer_questions:
                                settings = database.get_settings()
                                api_key = settings.get('gemini_api_key', '').strip()
                                
                                for i, inp in enumerate(text_inputs):
                                    answer = "Tôi đồng ý tham gia nhóm và tuân thủ các nội quy."
                                    if api_key:
                                        try:
                                            prompt = (
                                                f"Dưới đây là nội dung câu hỏi xét duyệt tham gia nhóm Facebook:\n"
                                                f"\"\"\"\n{dialog_text}\n\"\"\"\n"
                                                f"Hãy đưa ra câu trả lời ngắn gọn, phù hợp nhất cho câu hỏi thứ {i+1} (hoặc ô nhập liệu thứ {i+1} trong biểu mẫu). "
                                                f"Yêu cầu:\n"
                                                f"- Chỉ trả lời đúng nội dung câu hỏi, không kèm theo giải thích hay dẫn nhập.\n"
                                                f"- Trả lời ngắn gọn dưới 15 từ.\n"
                                                f"- Nếu câu hỏi là đồng ý với nội quy nhóm, hãy trả lời 'Đồng ý' hoặc 'Tôi đồng ý'.\n"
                                                f"- Trả lời bằng tiếng Việt."
                                            )
                                            ai_ans = call_gemini(api_key, prompt)
                                            if ai_ans and len(ai_ans.strip()) > 0:
                                                answer = ai_ans.strip()
                                        except Exception as ai_err:
                                            print(f"[Auto-Join] Lỗi gọi Gemini: {ai_err}")
                                            
                                    print(f"[Auto-Join] Trả lời câu hỏi {i+1}: {answer}")
                                    try:
                                        inp.fill(answer)
                                        time.sleep(1)
                                    except:
                                        pass
                                    details += f"Q{i+1}: {answer}; "
                            
                            submit_btn = None
                            submit_selectors = [
                                'div[role="button"]:has-text("Gửi")',
                                'div[role="button"]:has-text("Submit")',
                                'div[role="button"]:has-text("Hoàn tất")',
                                'div[role="button"]:has-text("Confirm")',
                                'button:has-text("Gửi")',
                                'button:has-text("Submit")'
                            ]
                            for s_sel in submit_selectors:
                                try:
                                    s_btn = dialog.query_selector(s_sel)
                                    if s_btn:
                                        submit_btn = s_btn
                                        break
                                except:
                                    pass
                            
                            if submit_btn:
                                print(f"[Auto-Join] Click nút Gửi câu hỏi...")
                                submit_btn.click()
                                time.sleep(3)
                                status = "pending_approval"
                                details = "Đã gửi câu trả lời: " + details
                            else:
                                print(f"[Auto-Join] Không tìm thấy nút Gửi câu hỏi.")
                                status = "failed"
                                details = "Không gửi được câu hỏi xét duyệt."
                        else:
                            status = "success"
                            details = "Đã tham gia thành công trực tiếp (Không có câu hỏi)."
                        
                        save_autojoin_log(account_id, group_url, status, details)
                        if status in ["success", "pending_approval"]:
                            joined_urls.append(group_url)
                        success_count += 1
                    else:
                        print(f"[Auto-Join] Không tìm thấy nút Tham gia cho nhóm: {group_url}")
                        save_autojoin_log(account_id, group_url, "failed", "Không tìm thấy nút Tham gia nhóm trên giao diện.")
                except Exception as g_err:
                    print(f"[Auto-Join] Lỗi khi tham gia nhóm {group_url}: {g_err}")
                    save_autojoin_log(account_id, group_url, "failed", str(g_err))
                
                if index < len(groups_to_process) - 1:
                    sleep_time = delay + random.uniform(-3, 3)
                    sleep_time = max(5, sleep_time)
                    print(f"[Auto-Join] Chờ {sleep_time:.1f} giây trước khi tiếp tục...")
                    time.sleep(sleep_time)
            


            return {
                'success': True,
                'log': f'Đã xử lý xong danh sách tham gia nhóm ({success_count} thành công/gửi yêu cầu).'
            }
        except Exception as err:
            print(f"[Auto-Join] Lỗi hệ thống: {err}")
            try:
                save_autojoin_log(account_id, keyword or "Danh sách nhóm", "failed", f"Lỗi hệ thống: {str(err)}")
            except:
                pass
            return {'success': False, 'log': f'Lỗi hệ thống: {str(err)}'}
        finally:
            if browser:
                try: browser.close()
                except: pass

def scrape_and_save_public_groups(account_id, account_cookie, account_name, limit=30):
    import database
    from database import save_autojoin_log, save_target_list, get_target_lists
    import re
    import hashlib
    from datetime import datetime
    
    try:
        cookies = parse_cookies(account_cookie)
    except Exception as e:
        err_msg = f"Lỗi cookie: {str(e)}"
        save_autojoin_log(account_id, "Đồng bộ nhóm công khai", "failed", err_msg)
        return {'success': False, 'log': err_msg}

    if not cookies:
        err_msg = "Không tìm thấy cookie hợp lệ."
        save_autojoin_log(account_id, "Đồng bộ nhóm công khai", "failed", err_msg)
        return {'success': False, 'log': err_msg}

    save_autojoin_log(account_id, "Đồng bộ nhóm công khai", "pending", "Bắt đầu quét nhóm công khai từ tài khoản...")

    with sync_playwright() as p:
        browser = None
        try:
            print(f"[SyncGroups] Khởi động trình duyệt cho tài khoản {account_name}...")
            browser = _launch_browser(p)
            context = _make_context(browser)
            context.add_cookies(cookies)
            page = context.new_page()
            
            page.goto('https://www.facebook.com/groups/', wait_until='domcontentloaded', timeout=60000)
            time.sleep(5)
            _check_logged_in(page)

            # Scroll left panel or page a bit to load more groups
            try:
                page.evaluate('''() => {
                    const scrollableDivs = Array.from(document.querySelectorAll('div')).filter(
                        d => d.scrollHeight > d.clientHeight && window.getComputedStyle(d).overflowY !== 'hidden'
                    );
                    for (let d of scrollableDivs) {
                        d.scrollTop = d.scrollHeight;
                    }
                }''')
                time.sleep(3)
            except Exception as scroll_err:
                print(f"[SyncGroups] Scroll error (non-fatal): {scroll_err}")

            hrefs = page.evaluate('''() => {
                const links = Array.from(document.querySelectorAll('a[href*="/groups/"]'));
                return links.map(a => a.href);
            }''')

            raw_groups = []
            for href in hrefs:
                if any(x in href for x in ['/feed/', '/discover/', '/joins/', '/categories/', '/create/']):
                    continue
                match = re.search(r'/groups/([^/?#]+)', href)
                if match:
                    g_id = match.group(1)
                    g_url = f"https://www.facebook.com/groups/{g_id}/"
                    if g_url not in raw_groups:
                        raw_groups.append(g_url)

            print(f"[SyncGroups] Tìm thấy {len(raw_groups)} nhóm thô từ giao diện. Bắt đầu phân loại công khai...")
            
            public_groups = []
            checked_count = 0
            
            for index, g_url in enumerate(raw_groups[:limit]):
                print(f"[SyncGroups] Đang kiểm tra nhóm [{index+1}/{len(raw_groups[:limit])}]: {g_url}")
                try:
                    page.goto(g_url, wait_until='domcontentloaded', timeout=40000)
                    time.sleep(3)
                    
                    page_text = page.evaluate("document.body.innerText")
                    
                    is_public = False
                    has_public_keyword = any(kw in page_text for kw in ["Nhóm công khai", "Public group", "Công khai", "Public"])
                    has_private_keyword = any(kw in page_text for kw in ["Nhóm riêng tư", "Private group", "Riêng tư", "Private"])
                    
                    if has_public_keyword and not has_private_keyword:
                        is_public = True
                    
                    if is_public:
                        print(f"[SyncGroups] -> Nhóm CÔNG KHAI: {g_url}")
                        public_groups.append(g_url)
                    else:
                        print(f"[SyncGroups] -> Nhóm RIÊNG TƯ hoặc không rõ: {g_url}")
                    checked_count += 1
                except Exception as g_err:
                    print(f"[SyncGroups] Lỗi khi truy cập {g_url}: {g_err}")

            if not public_groups:
                msg = f"Đã quét {checked_count} nhóm nhưng không tìm thấy nhóm công khai nào."
                save_autojoin_log(account_id, "Đồng bộ nhóm công khai", "failed", msg)
                return {'success': False, 'log': msg}

            # Update target list in database
            target_list_name = f"Nhóm công khai - {account_name}"
            list_id = 'list_public_' + hashlib.md5(account_id.encode('utf-8')).hexdigest()[:8]
            
            targets_str = "\n".join(public_groups)
            database.save_target_list(list_id, target_list_name, targets_str)
            msg = f"Đã cập nhật danh sách '{target_list_name}' với {len(public_groups)} nhóm công khai (quét {checked_count} nhóm)."

            print(f"[SyncGroups] {msg}")
            save_autojoin_log(account_id, "Đồng bộ nhóm công khai", "success", msg)
            return {'success': True, 'log': msg}
            
        except Exception as err:
            err_msg = f"Lỗi hệ thống đồng bộ nhóm: {str(err)}"
            print(f"[SyncGroups] {err_msg}")
            save_autojoin_log(account_id, "Đồng bộ nhóm công khai", "failed", err_msg)
            return {'success': False, 'log': err_msg}
        finally:
            if browser:
                try: browser.close()
                except: pass

def auto_join_groups_by_topic(account_id, account_cookie, account_name, topic, target_limit=50, delay=15, answer_questions=True, prioritize=True):
    import database
    from database import save_autojoin_log, save_target_list
    import urllib.parse
    import re
    import hashlib
    
    def parse_member_count_str(num_str, suffix):
        num_str = num_str.strip()
        suffix = (suffix or "").lower().strip()
        if ',' in num_str and '.' in num_str:
            if num_str.find(',') < num_str.find('.'):
                num_str = num_str.replace(',', '')
            else:
                num_str = num_str.replace('.', '').replace(',', '.')
        elif ',' in num_str:
            parts = num_str.split(',')
            if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) == 3 and not suffix):
                num_str = num_str.replace(',', '')
            else:
                num_str = num_str.replace(',', '.')
        elif '.' in num_str:
            parts = num_str.split('.')
            if len(parts) == 2 and len(parts[1]) == 3 and not suffix:
                num_str = num_str.replace('.', '')
        try:
            num = float(num_str)
            if suffix in ['k', 'nghìn', 'tr']:
                num *= 1000
            elif suffix in ['m', 'triệu']:
                num *= 1000000
            return int(num)
        except:
            return 0

    try:
        cookies = parse_cookies(account_cookie)
    except Exception as e:
        err_msg = f"Lỗi cookie: {str(e)}"
        save_autojoin_log(account_id, f"Chủ đề: {topic}", "failed", err_msg)
        return {'success': False, 'log': err_msg}

    if not cookies:
        err_msg = "Không tìm thấy cookie hợp lệ."
        save_autojoin_log(account_id, f"Chủ đề: {topic}", "failed", err_msg)
        return {'success': False, 'log': err_msg}

    save_autojoin_log(account_id, f"Chủ đề: {topic}", "pending", f"Bắt đầu chiến dịch tìm kiếm và tham gia nhóm cho chủ đề: '{topic}'")

    joined_urls = []

    with sync_playwright() as p:
        browser = None
        try:
            print(f"[TopicCampaign] Khởi động trình duyệt cho {account_name}...")
            browser = _launch_browser(p)
            context = _make_context(browser)
            context.add_cookies(cookies)
            page = context.new_page()
            
            # 1. Search groups
            search_url = f"https://www.facebook.com/search/groups/?q={urllib.parse.quote(topic)}"
            print(f"[TopicCampaign] Đang tìm kiếm nhóm: {search_url}")
            page.goto(search_url, wait_until='domcontentloaded', timeout=60000)
            time.sleep(5)
            _check_logged_in(page)

            # Scroll multiple times to fetch a large list of groups
            scroll_count = max(6, min(25, int(target_limit * 0.5)))
            print(f"[TopicCampaign] Cuộn trang {scroll_count} lần để tải thêm các nhóm...")
            for s in range(scroll_count):
                page.evaluate("window.scrollBy(0, 1500)")
                time.sleep(1.5)

            # Evaluate page to get all groups cards with their metadata (privacy & member count)
            raw_candidates = page.evaluate('''() => {
                const results = [];
                const links = Array.from(document.querySelectorAll('a[href*="/groups/"]'));
                const seen = new Set();
                
                for (const a of links) {
                    const href = a.href;
                    if (href.includes('/feed/') || href.includes('/discover/') || href.includes('/joins/') || href.includes('/categories/') || href.includes('/create/')) {
                        continue;
                    }
                    
                    const match = href.match(/\/groups\/([^/?#]+)/);
                    if (!match) continue;
                    const gId = match[1];
                    const cleanUrl = `https://www.facebook.com/groups/${gId}/`;
                    
                    if (seen.has(cleanUrl)) continue;
                    seen.add(cleanUrl);
                    
                    let card = a;
                    // Go up parent elements until we find one that contains member/privacy metadata
                    for (let i = 0; i < 6; i++) {
                        if (!card.parentElement) break;
                        const parentText = card.parentElement.innerText || "";
                        if (parentText.includes('thành viên') || parentText.includes('members') || parentText.includes('member') || parentText.includes('công khai') || parentText.includes('public')) {
                            card = card.parentElement;
                            break;
                        }
                        card = card.parentElement;
                    }
                    
                    const text = card.innerText || "";
                    results.push({
                        url: cleanUrl,
                        text: text,
                        name: a.innerText || gId
                    });
                }
                return results;
            }''')

            print(f"[TopicCampaign] Đã tìm thấy {len(raw_candidates)} nhóm thô. Đang phân loại và sắp xếp...")
            
            parsed_candidates = []
            for item in raw_candidates:
                text = item['text']
                is_public = any(kw in text for kw in ["Nhóm công khai", "Public group", "Công khai", "Public"])
                
                member_count = 0
                member_match = re.search(r'([\d.,]+)\s*(K|M|triệu|nghìn|tr|k)?\s*(?:thành viên|members|member|người)', text, re.IGNORECASE)
                if member_match:
                    member_count = parse_member_count_str(member_match.group(1), member_match.group(2))
                
                # Parse post frequency to prioritize free posting (active groups)
                posts_per_day = 0.0
                freq_match = re.search(r'([\d.,]+)\s*\+?\s*(?:bài viết|posts?)\s*(?:một|a|mỗi|per|\/)?\s*(ngày|day|tuần|week|tháng|month)', text, re.IGNORECASE)
                if freq_match:
                    try:
                        val = float(freq_match.group(1).replace(',', ''))
                        unit = freq_match.group(2).lower()
                        if unit in ['ngày', 'day']:
                            posts_per_day = val
                        elif unit in ['tuần', 'week']:
                            posts_per_day = val / 7.0
                        elif unit in ['tháng', 'month']:
                            posts_per_day = val / 30.0
                    except:
                        pass
                
                parsed_candidates.append({
                    'url': item['url'],
                    'name': item['name'],
                    'is_public': is_public,
                    'member_count': member_count,
                    'posts_per_day': posts_per_day
                })

            if prioritize:
                # Sort: Public groups first (True > False), then posts_per_day descending, then member_count descending
                parsed_candidates.sort(key=lambda x: (x['is_public'], x['posts_per_day'], x['member_count']), reverse=True)
            else:
                # Sort: member_count descending
                parsed_candidates.sort(key=lambda x: x['member_count'], reverse=True)

            print(f"[TopicCampaign] Đã sắp xếp xong {len(parsed_candidates)} nhóm.")
            for idx, c in enumerate(parsed_candidates[:10]):
                print(f"  [{idx+1}] {c['name']} | Công khai: {c['is_public']} | Bài viết/ngày: {c['posts_per_day']:.2f} | Thành viên: {c['member_count']} | URL: {c['url']}")

            # Save target list immediately so user sees all found groups on UI
            target_candidates = parsed_candidates[:target_limit]
            if target_candidates:
                target_list_name = f"Chủ đề: {topic} - {account_name}"
                list_id = 'list_topic_' + hashlib.md5((account_id + topic).encode('utf-8')).hexdigest()[:8]
                targets_str = "\n".join([c['url'] for c in target_candidates])
                database.save_target_list(list_id, target_list_name, targets_str)
                print(f"[TopicCampaign] Đã lập danh sách mục tiêu '{target_list_name}' với {len(target_candidates)} nhóm.")

            success_count = 0
            
            for index, candidate in enumerate(parsed_candidates):
                if len(joined_urls) >= target_limit:
                    print(f"[TopicCampaign] Đã đạt giới hạn mục tiêu {target_limit} nhóm. Dừng chiến dịch.")
                    break
                    
                group_url = candidate['url']
                print(f"[TopicCampaign] Đang xử lý nhóm [{len(joined_urls)+1}/{target_limit}] (Quét qua danh sách vị trí {index+1}): {group_url}")
                
                try:
                    page.goto(group_url, wait_until='domcontentloaded', timeout=40000)
                    time.sleep(4)
                    
                    page_text = page.evaluate("document.body.innerText")
                    
                    if any(x in page_text for x in ["Đã tham gia", "Joined", "Được quản lý", "Manage"]):
                        print(f"[TopicCampaign] Đã là thành viên của nhóm: {group_url}")
                        save_autojoin_log(account_id, group_url, "already_member", "Đã là thành viên (thêm vào danh sách mục tiêu).")
                        joined_urls.append(group_url)
                        success_count += 1
                        continue
                        
                    if any(x in page_text for x in ["Đã gửi yêu cầu", "Requested", "Hủy yêu cầu", "Cancel Request"]):
                        print(f"[TopicCampaign] Đang chờ phê duyệt trong nhóm: {group_url}")
                        save_autojoin_log(account_id, group_url, "pending_approval", "Yêu cầu tham gia đang chờ duyệt (thêm vào danh sách).")
                        joined_urls.append(group_url)
                        success_count += 1
                        continue

                    join_btn = None
                    btn_selectors = [
                        'div[role="button"]:has-text("Tham gia nhóm")',
                        'div[role="button"]:has-text("Join group")',
                        'div[role="button"]:has-text("Join Group")',
                        'div[role="button"]:has-text("Tham gia")',
                        'div[role="button"]:has-text("Join")',
                        'div[role="button"][aria-label*="Tham gia nhóm" i]',
                        'div[role="button"][aria-label*="Join group" i]',
                        'span:has-text("Tham gia nhóm")',
                        'span:has-text("Join group")'
                    ]
                    for sel in btn_selectors:
                        try:
                            btn = page.locator(sel).first
                            if btn and btn.is_visible():
                                join_btn = btn
                                break
                        except:
                            pass
                            
                    if not join_btn:
                        buttons = page.query_selector_all('div[role="button"], button')
                        for btn in buttons:
                            text = btn.inner_text() or ""
                            if "tham gia" in text.lower() or "join" in text.lower():
                                join_btn = btn
                                break

                    if join_btn:
                        print(f"[TopicCampaign] Click nút Tham gia nhóm...")
                        join_btn.click()
                        time.sleep(4)
                        
                        dialog = page.query_selector('div[role="dialog"]')
                        details = ""
                        
                        if dialog:
                            print(f"[TopicCampaign] Phát hiện hộp thoại câu hỏi thành viên.")
                            dialog_text = dialog.inner_text()
                            
                            checkboxes = dialog.query_selector_all('input[type="checkbox"], div[role="checkbox"]')
                            for cb in checkboxes:
                                try:
                                    if cb.get_attribute('aria-checked') != 'true':
                                        cb.click()
                                        time.sleep(0.5)
                                except:
                                    pass
                            
                            text_inputs = dialog.query_selector_all('textarea, input[type="text"], div[role="textbox"]')
                            
                            if text_inputs and answer_questions:
                                settings = database.get_settings()
                                api_key = settings.get('gemini_api_key', '').strip()
                                
                                for i, inp in enumerate(text_inputs):
                                    answer = "Tôi đồng ý tham gia nhóm và tuân thủ các nội quy."
                                    if api_key:
                                        try:
                                            prompt = (
                                                f"Dưới đây là nội dung câu hỏi xét duyệt tham gia nhóm Facebook:\n"
                                                f"\"\"\"\n{dialog_text}\n\"\"\"\n"
                                                f"Hãy đưa ra câu trả lời ngắn gọn, phù hợp nhất cho câu hỏi thứ {i+1}. "
                                                f"Yêu cầu:\n"
                                                f"- Chỉ trả lời đúng nội dung câu hỏi, không giải thích.\n"
                                                f"- Trả lời ngắn gọn dưới 15 từ.\n"
                                                f"- Nếu là đồng ý nội quy, trả lời 'Tôi đồng ý'.\n"
                                                f"- Trả lời bằng tiếng Việt."
                                            )
                                            ai_ans = call_gemini(api_key, prompt)
                                            if ai_ans and len(ai_ans.strip()) > 0:
                                                answer = ai_ans.strip()
                                        except Exception as ai_err:
                                            print(f"[TopicCampaign] Lỗi AI: {ai_err}")
                                            
                                    print(f"[TopicCampaign] Trả lời câu hỏi {i+1}: {answer}")
                                    try:
                                        inp.fill(answer)
                                        time.sleep(1)
                                    except:
                                        pass
                                    details += f"Q{i+1}: {answer}; "
                            
                            submit_btn = None
                            submit_selectors = [
                                'div[role="button"]:has-text("Gửi")',
                                'div[role="button"]:has-text("Submit")',
                                'div[role="button"]:has-text("Hoàn tất")',
                                'div[role="button"]:has-text("Confirm")',
                                'button:has-text("Gửi")',
                                'button:has-text("Submit")'
                            ]
                            for s_sel in submit_selectors:
                                try:
                                    s_btn = dialog.query_selector(s_sel)
                                    if s_btn:
                                        submit_btn = s_btn
                                        break
                                except:
                                    pass
                                    
                            if submit_btn:
                                print(f"[TopicCampaign] Click nút Gửi câu trả lời...")
                                submit_btn.click()
                                time.sleep(3)
                                status = "pending_approval"
                                details = "Đã gửi câu trả lời: " + details
                            else:
                                print(f"[TopicCampaign] Không tìm thấy nút Gửi.")
                                status = "failed"
                                details = "Không gửi được câu hỏi xét duyệt."
                        else:
                            status = "success"
                            details = "Đã tham gia thành công trực tiếp (Không có câu hỏi)."
                        
                        save_autojoin_log(account_id, group_url, status, details)
                        joined_urls.append(group_url)
                        success_count += 1
                    else:
                        print(f"[TopicCampaign] Không tìm thấy nút Tham gia cho nhóm: {group_url}")
                except Exception as g_err:
                    print(f"[TopicCampaign] Lỗi khi xử lý nhóm {group_url}: {g_err}")
                
                time.sleep(delay)

            target_list_name = f"Chủ đề: {topic} - {account_name}"
            if target_candidates:
                msg = f"Đã xử lý xong chiến dịch chủ đề '{topic}' ({success_count} nhóm đã gia nhập/thành viên)."
                print(f"[TopicCampaign] {msg}")
                save_autojoin_log(account_id, f"Chủ đề: {topic}", "success", msg)
                return {'success': True, 'log': msg}
            else:
                msg = f"Không thu thập được nhóm nào cho chủ đề '{topic}'."
                print(f"[TopicCampaign] {msg}")
                save_autojoin_log(account_id, f"Chủ đề: {topic}", "failed", msg)
                return {'success': False, 'log': msg}
                
        except Exception as err:
            err_msg = f"Lỗi hệ thống chiến dịch: {str(err)}"
            print(f"[TopicCampaign] {err_msg}")
            save_autojoin_log(account_id, f"Chủ đề: {topic}", "failed", err_msg)
            return {'success': False, 'log': err_msg}
        finally:
            if browser:
                try: browser.close()
                except: pass


def auto_login_facebook(username, password, two_factor_key):
    """
    Logs into Facebook using username, password and 2FA TOTP key, 
    then extracts cookies.
    """
    if not username or not password:
        return {'success': False, 'log': 'Tài khoản hoặc mật khẩu trống.'}
    
    import pyotp
    import time
    import json
    from playwright.sync_api import sync_playwright
    
    print(f"[AutoLogin] Bắt đầu đăng nhập tự động cho {username}...")
    browser = None
    try:
        with sync_playwright() as p:
            browser = _launch_browser(p)
            context = _make_context(browser)
            page = context.new_page()
            
            page.goto('https://www.facebook.com/', wait_until='domcontentloaded')
            time.sleep(3)
            
            # Fill credentials
            if page.query_selector('input[name="email"]'):
                page.fill('input[name="email"]', username)
                page.fill('input[name="pass"]', password)
                
                # Click Login
                login_btn = page.query_selector('button[name="login"]') or page.query_selector('button[type="submit"]')
                if login_btn:
                    login_btn.click()
                else:
                    page.keyboard.press('Enter')
                
                time.sleep(5)
                
                # Check 2FA screen
                is_2fa = False
                code_input_selector = None
                for selector in ['input[name="approvals_code"]', 'input[id="approvals_code"]', 'input[autocomplete="one-time-code"]']:
                    if page.query_selector(selector):
                        is_2fa = True
                        code_input_selector = selector
                        break
                
                if is_2fa and code_input_selector:
                    print(f"[AutoLogin] Phát hiện màn hình bảo mật 2 lớp (2FA). Đang sinh mã OTP...")
                    if not two_factor_key:
                        return {'success': False, 'log': 'Phát hiện yêu cầu 2FA nhưng tài khoản không cấu hình khóa 2FA Key.'}
                    
                    try:
                        clean_key = two_factor_key.replace(" ", "").strip()
                        totp = pyotp.TOTP(clean_key)
                        otp_code = totp.now()
                        print(f"[AutoLogin] OTP sinh ra: {otp_code}")
                        
                        page.fill(code_input_selector, otp_code)
                        time.sleep(1)
                        
                        submit_btn = page.query_selector('button[id="checkpointSubmitButton"]') or page.query_selector('button[type="submit"]')
                        if submit_btn:
                            submit_btn.click()
                        else:
                            page.keyboard.press('Enter')
                            
                        time.sleep(5)
                        
                        # Handle next buttons (Lưu trình duyệt / Save browser / Confirm login)
                        for _ in range(3):
                            next_btn = page.query_selector('button[id="checkpointSubmitButton"]')
                            if next_btn and next_btn.is_visible():
                                print("[AutoLogin] Trình duyệt hiển thị màn hình tiếp theo, đang click Tiếp tục...")
                                next_btn.click()
                                time.sleep(3)
                    except Exception as o_err:
                        return {'success': False, 'log': f'Lỗi xác thực 2FA: {str(o_err)}'}
                
                # Verify login result
                time.sleep(3)
                try:
                    os.makedirs('uploads/screenshots', exist_ok=True)
                    page.screenshot(path='uploads/screenshots/last_login_attempt.png')
                    print("[AutoLogin] Saved screenshot to uploads/screenshots/last_login_attempt.png")
                except Exception as ss_err:
                    print(f"[AutoLogin] Error saving screenshot: {ss_err}")

                if page.query_selector('input[name="email"]') or page.query_selector('input[name="pass"]'):
                    err_msg = "Không đăng nhập được. Sai mật khẩu hoặc tài khoản bị khóa."
                    err_div = page.query_selector('div:has-text("không chính xác")') or page.query_selector('div:has-text("sai")')
                    if err_div:
                        err_msg = f"Đăng nhập thất bại: {err_div.inner_text().strip()}"
                    return {'success': False, 'log': err_msg}
                
                cookies = context.cookies()
                cookies_json = json.dumps(cookies)
                print("[AutoLogin] Đăng nhập thành công! Đã lấy được cookie mới.")
                return {'success': True, 'cookie': cookies_json}
            else:
                return {'success': False, 'log': 'Không tìm thấy các trường đăng nhập trên trang Facebook.'}
    except Exception as e:
        return {'success': False, 'log': f'Lỗi hệ thống đăng nhập tự động: {str(e)}'}
    finally:
        if browser:
            try: browser.close()
            except: pass

def scan_group_for_insights(account_cookie, group_url, limit=10):
    try:
        cookies = parse_cookies(account_cookie)
    except Exception as e:
        return {'success': False, 'log': f"Cookie error: {e}"}

    posts_data = []
    with sync_playwright() as p:
        browser = None
        try:
            print("[Insights Trace] Launching browser...")
            browser = _launch_browser(p)
            print("[Insights Trace] Creating context...")
            context = _make_context(browser)
            print("[Insights Trace] Adding cookies...")
            context.add_cookies(cookies)
            print("[Insights Trace] Opening new page...")
            page = context.new_page()

            if group_url == 'newsfeed':
                url = "https://www.facebook.com/"
            else:
                url = group_url
                if "?" not in url:
                    url += "?sorting_setting=CHRONOLOGICAL"
                elif "sorting_setting" not in url:
                    url += "&sorting_setting=CHRONOLOGICAL"

            print(f"[Insights] Scanning group: {url}")
            page.goto(url, wait_until='domcontentloaded', timeout=60000)
            time.sleep(4)
            _check_logged_in(page)

            scrolled = 0
            while len(posts_data) < limit and scrolled < 10:
                post_containers = page.locator('div[role="article"]').all()
                for container in post_containers:
                    if len(posts_data) >= limit:
                        break
                    try:
                        link_els = container.locator('a[role="link"]').all()
                        post_url = ""
                        author = ""
                        time_text = ""
                        for l in link_els:
                            href = l.get_attribute("href")
                            if href and "/groups/" in href and "/user/" not in href and "/posts/" in href:
                                post_url = href.split("?")[0]
                                time_text = l.inner_text().strip()
                        
                        author_link = container.locator('h3 a[role="link"], h2 a[role="link"], h4 a[role="link"]').first
                        if author_link.is_visible():
                            author = author_link.inner_text().strip()

                        content_div = container.locator('div[data-ad-comet-preview="message"]').first
                        content = ""
                        if content_div.is_visible():
                            content = content_div.inner_text().strip()

                        if post_url and content and post_url not in [p['url'] for p in posts_data]:
                            # Filter posts older than 6 hours
                            is_recent = False
                            t = time_text.lower()
                            if not t:
                                is_recent = True  # If cannot parse time, default to True
                            elif 'vừa' in t or 'phút' in t or 'giây' in t or 'mới đây' in t:
                                is_recent = True
                            else:
                                import re
                                match = re.search(r'(\d+)\s*(giờ|h\b)', t)
                                if match:
                                    if int(match.group(1)) <= 6:
                                        is_recent = True
                                
                            if is_recent:
                                posts_data.append({
                                    'author': author,
                                    'content': content,
                                    'url': post_url
                                })
                            else:
                                print(f"[Insights] Bỏ qua bài viết cũ: {time_text} - {post_url}")
                    except:
                        pass

                page.evaluate("window.scrollBy(0, 1000)")
                time.sleep(2)
                scrolled += 1

            return {'success': True, 'posts': posts_data}
        except Exception as e:
            return {'success': False, 'log': str(e)}
        finally:
            if browser:
                try: browser.close()
                except: pass

def analyze_customer_insights(posts, niche_keywords):
    import database
    import json
    import re
    settings = database.get_settings()
    api_key = settings.get('gemini_api_key', '')
    if not api_key:
        return {'success': False, 'log': 'Chưa cấu hình Gemini API Key.'}

    if niche_keywords.strip().lower() in ["tất cả", "all", "tất cả các lĩnh vực"]:
        prompt = f"""
Bạn là một chuyên gia thấu hiểu khách hàng (Customer Insight Analyst) và Copywriter tại thị trường Việt Nam. 
Dưới đây là một số bài viết mới từ Facebook.
Nhiệm vụ của bạn:
1. Đọc từng bài viết và xác định xem người viết có đang chia sẻ cuộc sống, đặt câu hỏi, tâm sự hoặc bày tỏ một nhu cầu nhỏ nào đó ở BẤT KỲ LĨNH VỰC NÀO hay không? (Chỉ cần không phải bài đăng bán hàng là có thể chọn).
2. Đối với MỖI bài tiềm năng, hãy phân tích:
   - Vấn đề cốt lõi (Pain point)
   - Mong muốn thực sự (Desire)
   - Insight (Sự thật ngầm hiểu)
3. Đề xuất 2-3 chủ đề nội dung (Content Topics) bạn có thể làm để thu hút người này.
4. Đề xuất cách lồng ghép sản phẩm TÚI XÁCH LOLISHOP để bán cho họ. QUAN TRỌNG: Dù khách nói về giày, quần áo, mỹ phẩm hay con cái, bạn PHẢI tìm cách dẫn dắt nhu cầu của họ về việc mua một chiếc TÚI XÁCH ĐẸP TẠI LOLISHOP.
5. Đưa ra một kết cấu bài viết/bình luận (Post Structure) ngắn gọn, thôi miên, để thu hút họ click vào link.
6. Gợi ý một ý tưởng hình ảnh (Image Idea) túi xách chân thực hoặc ấn tượng đi kèm bài viết.
7. Bài Viết Đề Xuất (Suggested Post): Dựa vào Cấu trúc trên, hãy VIẾT SẴN một bài viết/bình luận Facebook thực tế. BẮT BUỘC: Nội dung phải CHÀO BÁN TÚI XÁCH LOLISHOP và dẫn dắt khéo léo từ bài viết gốc của họ. Tuyệt đối không bán sản phẩm khác. Xưng 'mình/em', gọi 'bạn/chị'. Kèm theo Call to Action để sẵn [Link Shopee của bạn].
"""
    else:
        prompt = f"""
Bạn là một chuyên gia thấu hiểu khách hàng (Customer Insight Analyst) và Copywriter tại thị trường Việt Nam. 
Dưới đây là một số bài viết mới từ Facebook (Ngách: {niche_keywords}).
Nhiệm vụ của bạn:
1. Đọc từng bài viết và xác định xem bài viết này có tiềm năng tương tác không (kể cả chỉ chia sẻ cuộc sống, nuôi thú cưng, nấu ăn, hoặc hỏi đáp nhẹ nhàng). (Hãy MỞ RỘNG tiêu chí: chỉ cần không phải bài đăng bán hàng/quảng cáo chuyên nghiệp là chọn).
2. Đối với MỖI bài tiềm năng, hãy phân tích:
   - Vấn đề cốt lõi (Pain point)
   - Mong muốn thực sự (Desire)
   - Insight (Sự thật ngầm hiểu)
3. Đề xuất 2-3 chủ đề nội dung (Content Topics) bạn có thể làm để thu hút người này.
4. Đề xuất cách lồng ghép sản phẩm TÚI XÁCH LOLISHOP để bán cho họ. QUAN TRỌNG: Dù khách nói về giày, quần áo, mỹ phẩm hay con cái, bạn PHẢI tìm cách dẫn dắt nhu cầu của họ về việc mua một chiếc TÚI XÁCH ĐẸP TẠI LOLISHOP.
5. Đưa ra một kết cấu bài viết/bình luận (Post Structure) ngắn gọn, thôi miên, để thu hút họ click vào link.
6. Gợi ý một ý tưởng hình ảnh (Image Idea) túi xách chân thực hoặc ấn tượng đi kèm bài viết.
7. Bài Viết Đề Xuất (Suggested Post): Dựa vào Cấu trúc trên, hãy VIẾT SẴN một bài viết/bình luận Facebook thực tế. BẮT BUỘC: Nội dung phải CHÀO BÁN TÚI XÁCH LOLISHOP và dẫn dắt khéo léo từ bài viết gốc của họ. Tuyệt đối không bán sản phẩm khác. Xưng 'mình/em', gọi 'bạn/chị'. Kèm theo Call to Action để sẵn [Link Shopee của bạn].
"""

    prompt += f"""
Hãy trả về KẾT QUẢ DƯỚI DẠNG JSON MẢNG (JSON Array). Nếu không có bài nào tiềm năng, trả về [] (mảng rỗng).

Format JSON Yêu Cầu:
[
  {{
    "post_url": "URL của bài viết (lấy từ dữ liệu cung cấp)",
    "author": "Tên tác giả",
    "pain_point": "Vấn đề của họ",
    "desire": "Mong muốn của họ",
    "insight": "Insight phân tích được",
    "content_ideas": ["Ý tưởng 1", "Ý tưởng 2"],
    "suggested_products": ["Sản phẩm 1", "Sản phẩm 2"],
    "post_structure": "Ví dụ: Hook (Gây sốc) -> Story (Đồng cảm) -> Solution (Sản phẩm) -> CTA (Click link)",
    "image_idea": "Ví dụ: Ảnh thực tế Before/After hoặc ảnh review chân thực..."
  }}
]

Dữ liệu bài viết:
"""
    for p in posts:
        prompt += f"\n- Tác giả: {p['author']}\n- URL: {p['url']}\n- Nội dung: {p['content']}\n"

    try:
        raw_reply = ""
        # Thử sử dụng G4F (mô hình toàn cầu miễn phí) trước để tránh bị rate limit của Gemini
        try:
            from automation import call_g4f
            raw_reply = call_g4f(prompt).strip()
            if not raw_reply or len(raw_reply) < 50 or "```json" not in raw_reply:
                raise Exception("G4F trả về rỗng hoặc thiếu JSON")
        except Exception as e_g4f:
            print(f"[Insights] G4F lỗi: {e_g4f}, chuyển sang Gemini", flush=True)
            raw_reply = call_gemini(api_key, prompt).strip()
        
        
        # Xóa markdown json block nếu có
        if raw_reply.startswith("```json"):
            raw_reply = raw_reply[7:]
        elif raw_reply.startswith("```"):
            raw_reply = raw_reply[3:]
        if raw_reply.endswith("```"):
            raw_reply = raw_reply[:-3]
        raw_reply = raw_reply.strip()

        match = re.search(r'\[.*\]', raw_reply, re.DOTALL)
        if match:
            json_str = match.group(0)
            data = json.loads(json_str)
            return {'success': True, 'data': data}
        else:
            return {'success': False, 'log': 'Lỗi parse JSON từ AI.', 'raw': raw_reply}
    except Exception as e:
        return {'success': False, 'log': str(e)}

def auto_fetch_joined_groups(account_cookie, limit=10):
    try:
        cookies = parse_cookies(account_cookie)
    except Exception as e:
        return {'success': False, 'log': f"Cookie error: {e}"}

    groups = []
    with sync_playwright() as p:
        browser = None
        try:
            print("[Insights Trace] Launching browser...")
            browser = _launch_browser(p)
            print("[Insights Trace] Creating context...")
            context = _make_context(browser)
            print("[Insights Trace] Adding cookies...")
            context.add_cookies(cookies)
            print("[Insights Trace] Opening new page...")
            page = context.new_page()

            page.goto('https://www.facebook.com/groups/joins/', timeout=60000)
            # Wait for any group links to appear
            try:
                page.wait_for_selector('a[href*="/groups/"]', state='attached', timeout=20000)
            except:
                pass # Continue anyway
            
            import time
            time.sleep(3)
            
            group_elements = page.query_selector_all('a[href*="/groups/"]')
            seen = set()
            import re
            
            for el in group_elements:
                if len(groups) >= limit:
                    break
                href = el.get_attribute('href')
                if not href:
                    continue
                m = re.search(r'/groups/([^/?#]+)', href)
                if m:
                    g_id = m.group(1)
                    if g_id not in seen and g_id not in ('joins', 'discover', 'create', 'feed', 'search'):
                        # get text
                        name = el.inner_text().strip()
                        if name:
                            groups.append({
                                'target_url': f"https://www.facebook.com/groups/{g_id}",
                                'target_name': name
                            })
                            seen.add(g_id)
            
            if groups:
                return {'success': True, 'data': groups}
            else:
                return {'success': False, 'log': 'Không tìm thấy nhóm nào.'}
                
        except Exception as e:
            return {'success': False, 'log': f"Lỗi lấy nhóm: {e}"}
        finally:
            if browser:
                browser.close()

def seed_comment_on_post(account_cookie, post_url, comment_text):
    try:
        cookies = parse_cookies(account_cookie)
    except Exception as e:
        return {'success': False, 'log': f"Cookie error: {e}"}

    with sync_playwright() as p:
        browser = None
        try:
            browser = _launch_browser(p)
            context = _make_context(browser)
            context.add_cookies(cookies)
            page = context.new_page()

            page.goto(post_url, timeout=60000)
            time.sleep(5)
            
            # Find comment box
            comment_selectors = [
                'div[role="textbox"][aria-label="Viết bình luận"]',
                'div[role="textbox"][aria-label="Write a comment"]',
                'div[role="textbox"][aria-label*="bình luận"]',
                'div[role="textbox"][aria-label*="comment"]',
            ]
            
            comment_box = None
            for sel in comment_selectors:
                try:
                    el = page.locator(sel).first
                    if el and el.count() > 0 and el.is_visible():
                        comment_box = el
                        break
                except:
                    pass
                    
            if not comment_box:
                return {'success': False, 'log': 'Không tìm thấy ô bình luận.'}
                
            comment_box.focus()
            comment_box.fill(comment_text)
            time.sleep(1)
            page.keyboard.press('Enter')
            time.sleep(3)
            
            return {'success': True, 'log': 'Đã gửi bình luận seeding thành công.'}
        except Exception as e:
            return {'success': False, 'log': f"Lỗi seeding comment: {e}"}
        finally:
            if browser:
                browser.close()

def seed_reply_to_comment(account_cookie, post_url, reply_text):
    try:
        cookies = parse_cookies(account_cookie)
    except Exception as e:
        return {'success': False, 'log': f"Cookie error: {e}"}

    with sync_playwright() as p:
        browser = None
        try:
            browser = _launch_browser(p)
            context = _make_context(browser)
            context.add_cookies(cookies)
            page = context.new_page()

            page.goto(post_url, timeout=60000)
            time.sleep(5)
            
            # Find reply button
            reply_btn_selectors = [
                'div[role="button"]:has-text("Phản hồi")',
                'div[role="button"]:has-text("Reply")'
            ]
            
            reply_btn = None
            for sel in reply_btn_selectors:
                try:
                    # get the latest reply button if there are many comments
                    el = page.locator(sel).last
                    if el and el.count() > 0 and el.is_visible():
                        reply_btn = el
                        break
                except:
                    pass
                    
            if not reply_btn:
                return {'success': False, 'log': 'Không tìm thấy nút phản hồi.'}
                
            reply_btn.click()
            time.sleep(2)
            
            # Wait for reply textbox
            page.keyboard.type(reply_text)
            time.sleep(1)
            page.keyboard.press('Enter')
            time.sleep(3)
            
            return {'success': True, 'log': 'Đã phản hồi bình luận seeding thành công.'}
        except Exception as e:
            return {'success': False, 'log': f"Lỗi seeding reply: {e}"}
        finally:
            if browser:
                browser.close()

def search_global_posts_by_keyword(account_cookie, keyword, limit=15):
    import urllib.parse
    try:
        cookies = parse_cookies(account_cookie)
    except Exception as e:
        return {'success': False, 'log': f"Cookie error: {e}"}

    posts_data = []
    with sync_playwright() as p:
        browser = None
        try:
            browser = _launch_browser(p)
            context = _make_context(browser)
            context.add_cookies(cookies)
            page = context.new_page()

            encoded_kw = urllib.parse.quote(keyword)
            # Default search for posts with the keyword
            url = f"https://www.facebook.com/search/posts/?q={encoded_kw}"

            print(f"[Insights] Searching global posts for: {keyword}")
            page.goto(url, wait_until='domcontentloaded', timeout=60000)
            time.sleep(4)
            _check_logged_in(page)

            scrolled = 0
            while len(posts_data) < limit and scrolled < 10:
                post_containers = page.locator('div[role="article"]').all()
                for container in post_containers:
                    if len(posts_data) >= limit:
                        break
                    try:
                        link_els = container.locator('a[role="link"]').all()
                        post_url = ""
                        author = ""
                        for l in link_els:
                            href = l.get_attribute("href")
                            if href and ("/posts/" in href or "/permalink/" in href or "/videos/" in href):
                                post_url = href.split("?")[0]
                                break
                        
                        author_link = container.locator('h3 a[role="link"], h2 a[role="link"], h4 a[role="link"], span > a[role="link"]').first
                        if author_link.is_visible():
                            author = author_link.inner_text().strip()

                        content_div = container.locator('div[data-ad-comet-preview="message"]').first
                        content = ""
                        if content_div.is_visible():
                            content = content_div.inner_text().strip()

                        if post_url and content and post_url not in [p['url'] for p in posts_data]:
                            posts_data.append({
                                'author': author,
                                'content': content,
                                'url': post_url
                            })
                    except:
                        pass

                page.evaluate("window.scrollBy(0, 1000)")
                time.sleep(3)
                scrolled += 1

            return {'success': True, 'posts': posts_data}
        except Exception as e:
            return {'success': False, 'log': str(e)}
        finally:
            if browser:
                try: browser.close()
                except: pass

def discover_new_groups(account_cookie, search_keyword, limit=5):
    import urllib.parse
    import database
    
    try:
        cookies = parse_cookies(account_cookie)
    except Exception as e:
        return {'success': False, 'log': f"Cookie error: {e}"}
        
    with sync_playwright() as p:
        browser = None
        try:
            browser = _launch_browser(p)
            context = _make_context(browser)
            context.add_cookies(cookies)
            page = context.new_page()
            
            encoded_kw = urllib.parse.quote(search_keyword)
            url = f"https://www.facebook.com/search/groups/?q={encoded_kw}"
            print(f"[Auto-Discovery] Đang tìm kiếm nhóm mới với từ khóa: {search_keyword}")
            page.goto(url, wait_until='domcontentloaded', timeout=60000)
            
            time.sleep(5)
            
            # scroll down a bit
            page.evaluate("window.scrollBy(0, 1000)")
            time.sleep(3)
            
            groups_found = []
            # Find links that look like groups
            links = page.locator('a[role="presentation"]').all()
            if not links:
                links = page.locator('a').all()
                
            for link in links:
                try:
                    href = link.get_attribute('href')
                    if href and '/groups/' in href and not '/search/' in href:
                        # Clean href
                        clean_href = href.split('?')[0].rstrip('/')
                        if clean_href.startswith('https://www.facebook.com/groups/'):
                            name = link.inner_text().strip()
                            if name and len(name) > 3 and "\n" not in name:
                                groups_found.append({
                                    'url': clean_href,
                                    'name': name
                                })
                except:
                    pass
            
            # Deduplicate
            unique_groups = []
            seen = set()
            for g in groups_found:
                if g['url'] not in seen:
                    seen.add(g['url'])
                    unique_groups.append(g)
            
            unique_groups = unique_groups[:limit]
            added_count = 0
            for g in unique_groups:
                # check if exists
                existing = [t for t in database.get_insight_targets() if t['target_url'] == g['url']]
                if not existing:
                    database.save_insight_target(None, g['url'], g['name'], 'Tất cả')
                    added_count += 1
                    print(f"[Auto-Discovery] Đã thêm nhóm mới: {g['name']}")
                    
            return {'success': True, 'log': f'Đã tìm thấy và thêm {added_count} nhóm mới.'}
        except Exception as e:
            return {'success': False, 'log': str(e)}
        finally:
            if browser:
                try: browser.close()
                except: pass





def get_ai_bait_reply(comment_content):
    import database
    settings = database.get_settings()
    bio_link = settings.get('bait_bio_link', 'https://mycollection.shopee.vn/lucloi')
    prompt = f"""Bạn là người bán hàng nhiệt tình.
Người khác bình luận vào bài của bạn: "{comment_content}"
Hãy reply thân thiện kèm link Affiliate sau: {bio_link}
Ví dụ: "Dạ váy chị hỏi em để ở đây nha chị: {bio_link}"
BẮT BUỘC chèn link này vào câu trả lời, không bịa link khác.
Chỉ trả về câu reply, không thêm gì khác."""
    try:
        ai_engine = settings.get('ai_engine', 'g4f')
        if ai_engine == 'g4f':
            from automation import call_g4f
            return call_g4f(prompt)
        gemini_key = settings.get('gemini_api_key', '').strip()
        from automation import call_gemini
        return call_gemini(gemini_key, prompt)
    except Exception as e:
        print(f"[Bait] AI Error: {e}")
        return f"Dạ link đây bạn nhé, đang sale mạnh lắm ạ: {bio_link}"

def monitor_bait_posts_and_reply(account_cookie, post_url):
    import database
    import time
    import uuid
    from playwright.sync_api import sync_playwright
    import json
    
    try:
        from automation import parse_cookies, _launch_browser, _make_context, _check_logged_in
        cookies = parse_cookies(account_cookie)
    except Exception as e:
        return {'success': False, 'log': f"Cookie error: {e}"}

    with sync_playwright() as p:
        browser = None
        try:
            print(f"[BaitMonitor] Mở trình duyệt kiểm tra bài mồi: {post_url}")
            browser = _launch_browser(p)
            context = _make_context(browser)
            context.add_cookies(cookies)
            page = context.new_page()

            page.goto(post_url, wait_until='domcontentloaded', timeout=60000)
            time.sleep(5)
            _check_logged_in(page)

            comments = page.locator('div[role="article"]').all()
            for comment in comments:
                try:
                    author_el = comment.locator('span[dir="auto"]').first
                    if not author_el.is_visible():
                        continue
                    author_name = author_el.inner_text().strip()
                    
                    content_el = comment.locator('div[dir="auto"]').nth(1)
                    if not content_el.is_visible():
                        continue
                    comment_content = content_el.inner_text().strip()
                    
                    if database.is_bait_replied(post_url, author_name):
                        continue

                    keywords = ['link', 'ib', 'giá', 'inbox', 'xin', 'quan tâm', 'bao nhiêu', 'nhiêu', 'mua', 'đâu']
                    if any(k in comment_content.lower() for k in keywords):
                        print(f"[BaitMonitor] Khách {author_name} xin link: {comment_content}")
                        
                        reply_text = get_ai_bait_reply(comment_content)
                        
                        reply_btn = comment.locator('div[role="button"]:has-text("Phản hồi")').first
                        if not reply_btn.is_visible():
                            reply_btn = comment.locator('div[role="button"]:has-text("Reply")').first
                            
                        if reply_btn.is_visible():
                            reply_btn.click()
                            time.sleep(2)
                            
                            editor = comment.locator('div[role="textbox"]').first
                            if editor.is_visible():
                                editor.fill(reply_text)
                                time.sleep(1)
                                editor.press('Enter')
                                time.sleep(3)
                                
                                reply_id = 'bait_' + str(uuid.uuid4())[:8]
                                database.save_bait_reply(reply_id, post_url, author_name, comment_content, reply_text)
                                print(f"[BaitMonitor] Đã reply {author_name}: {reply_text}")
                                
                                try:
                                    import telegram_bot
                                    settings = database.get_settings()
                                    token = settings.get('telegram_token')
                                    chat_id = settings.get('telegram_chat_id')
                                    msg = f"🕸️ <b>ĐÃ CHỐT ĐƠN TỪ BÀI MỒI!</b>\\n\\n"
                                    msg += f"👤 <b>Khách:</b> {author_name}\\n"
                                    msg += f"💬 <b>Hỏi:</b> {comment_content}\\n"
                                    msg += f"🤖 <b>Bot trả lời:</b> {reply_text}\\n"
                                    msg += f"🔗 <a href='{post_url}'>Xem bài mồi</a>\\n"
                                    telegram_bot.send_telegram_message(token, chat_id, msg)
                                except: pass
                except Exception as ex:
                    continue

            return {'success': True, 'log': 'Hoàn tất quét bài mồi'}
        except Exception as e:
            return {'success': False, 'log': str(e)}
        finally:
            if browser:
                try: browser.close()
                except: pass


def get_ai_insight_comment(lead_content, bio_link):
    import database
    settings = database.get_settings()
    # LUÔN LUÔN lôi kéo về TÚI XÁCH LOLISHOP - không đi theo chủ đề của khách
    prompt = f"""Bạn là một tín đồ thời trang đang bình luận trên Facebook.
Khách hàng trong nhóm thời trang vừa đăng bài: "{lead_content[:200]}"

Nhiệm vụ của bạn: Viết một câu bình luận tự nhiên để kéo họ quan tâm đến TÚI XÁCH tại Lolishop.

QUY TẮC BẮT BUỘC:
1. Dù khách viết về bất kỳ chủ đề gì (quần áo, giày dép, make-up...), bạn vẫn phải khéo léo chuyển hướng sang TÚI XÁCH.
2. Tạo cầu nối tự nhiên: ví dụ nếu họ hỏi về outfit → "Ủa mà outfit này mà kết hợp thêm chiếc túi xách là hoàn hảo chị ơi!"
3. Xưng "em/mình" với "chị/bạn", KHÔNG xưng kiểu shop bán hàng.
4. Cuối bình luận BẮT BUỘC chèn link: {bio_link}
5. Dưới 220 ký tự.

Ví dụ tốt:
- "Outfit đẹp thế mà chị chưa có túi xách xịn để đi kèm thì phí lắm! Em mới tậu túi ở Lolishop da thật, vừa rẻ vừa đẹp, chị nghía thử nha: {bio_link} 👜"
- "Chị ơi phong cách này mà phối thêm túi tote/túi đeo chéo nữa là sang xịn hẳn! Mình hay sắm ở đây này: {bio_link}"

BẮT BUỘC có link {bio_link} ở cuối. Trả về ĐÚNG câu bình luận, không thêm gì khác."""
    try:
        ai_engine = settings.get('ai_engine', 'g4f')
        gemini_key = settings.get('gemini_api_key', '').strip()
        if ai_engine != 'g4f' and gemini_key:
            from automation import call_gemini
            return call_gemini(gemini_key, prompt)
        from automation import call_g4f
        return call_g4f(prompt)
    except Exception as e:
        print(f"[InsightsComment] AI Error: {e}")
        return f"Chị ơi outfit đẹp vậy phối thêm túi xách Lolishop nữa là chuẩn luôn nè 👜 {bio_link}"

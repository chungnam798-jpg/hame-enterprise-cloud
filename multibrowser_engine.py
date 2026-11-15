import os
import sys
import time
import json
import threading
from playwright.sync_api import sync_playwright
import database
import automation

open_browsers = {}
browser_lock = threading.Lock()

def calculate_window_position(index, total=15):
    cols = 5
    row = index // cols
    col = index % cols
    width = 380
    height = 450
    x = col * 380
    y = row * 460
    return x, y, width, height

def _run_single_browser(account_id, x, y, width, height):
    account = database.get_account(account_id)
    if not account:
        print('[MultiBrowser] Account not found')
        return
    acc_name = account.get('name', 'Account')
    print('[MultiBrowser] Launching browser for:', acc_name)
    profile_dir = os.path.abspath(os.path.join('profiles', f'acc_{account_id}'))
    os.makedirs(profile_dir, exist_ok=True)
    cookies = []
    if account.get('cookie'):
        try:
            cookies = automation.parse_cookies(account['cookie'])
        except Exception as e:
            print('[MultiBrowser] Cookie error:', e)
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=False,
                args=[
                    '--disable-notifications',
                    '--no-sandbox',
                    f'--window-position={x},{y}',
                    f'--window-size={width},{height}',
                    '--app=https://www.facebook.com'
                ],
                viewport={'width': width, 'height': height},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                locale='vi-VN'
            )
            if cookies:
                try:
                    browser.add_cookies(cookies)
                except Exception as ce:
                    print('[MultiBrowser] add_cookies error:', ce)
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto('https://www.facebook.com', wait_until='domcontentloaded')
            with browser_lock:
                open_browsers[account_id] = browser
            print('[MultiBrowser] Live window open for:', acc_name)
            while True:
                try:
                    if not page.is_closed():
                        time.sleep(1)
                    else:
                        break
                except Exception:
                    break
        except Exception as err:
            print('[MultiBrowser] Browser error:', err)
        finally:
            with browser_lock:
                open_browsers.pop(account_id, None)

def launch_account_browser(account_id, index=0, total=15):
    x, y, w, h = calculate_window_position(index, total)
    t = threading.Thread(target=_run_single_browser, args=(account_id, x, y, w, h), daemon=True)
    t.start()
    return {'success': True, 'message': f'Da mo trinh duyet cho account {account_id}'}

def launch_all_browsers(team_role=None):
    accounts = database.get_accounts()
    active_accs = [a for a in accounts if a.get('status') == 'active']
    if team_role:
        active_accs = [a for a in active_accs if a.get('team_role') == team_role]
    print(f'[MultiBrowser] Launching {len(active_accs)} browsers...')
    for idx, acc in enumerate(active_accs[:15]):
        launch_account_browser(acc['id'], idx, len(active_accs))
        time.sleep(0.8)
    return {
        'success': True,
        'count': len(active_accs),
        'message': f'Da kich hoat dong loat {len(active_accs)} trinh duyet!'
    }

def get_open_browsers():
    with browser_lock:
        return list(open_browsers.keys())

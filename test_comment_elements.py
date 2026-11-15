import os, sys, json, time, sqlite3
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Load cookie
conn = sqlite3.connect('database.db')
r = conn.execute("SELECT cookie FROM accounts WHERE id='acc_03c4c025'").fetchone()
cookie_input = r[0]
conn.close()

from automation import parse_cookies, _launch_browser, _make_context, _check_logged_in

cookies = parse_cookies(cookie_input)

with sync_playwright() as p:
    print("Launching browser...")
    browser = _launch_browser(p)
    context = _make_context(browser)
    context.add_cookies(cookies)
    page = context.new_page()
    
    url = 'https://www.facebook.com/groups/1016613779501681'
    print(f"Navigating to {url}")
    page.goto(url, wait_until='domcontentloaded', timeout=60000)
    time.sleep(5)
    _check_logged_in(page)
    
    # Locate first article container
    post_containers = page.locator('div[role="article"], div.x1y1aw1k')
    count = post_containers.count()
    print(f"Found {count} post containers.")
    
    # Inspect the first few post containers
    for idx in range(min(count, 3)):
        print(f"\n--- POST CONTAINER [{idx}] ---")
        pc = post_containers.nth(idx)
        
        # Print text of first 100 chars
        text = pc.text_content()[:120].strip().replace('\n', ' ')
        print(f"Post text preview: {repr(text)}")
        
        # 1. Look for comment buttons
        print("Searching for comment buttons:")
        comment_buttons = pc.locator('div[role="button"]:has-text("Bình luận"), div[role="button"]:has-text("Comment"), div[role="button"][aria-label*="Bình luận"], div[role="button"][aria-label*="Comment"]')
        btn_count = comment_buttons.count()
        print(f"  Found {btn_count} comment buttons in this post.")
        for b_idx in range(btn_count):
            btn = comment_buttons.nth(b_idx)
            print(f"  - Btn [{b_idx}] visible: {btn.is_visible()}, text: {repr(btn.text_content().strip())}, aria-label: {repr(btn.get_attribute('aria-label'))}")
            
        # 2. Look for comment textboxes
        print("Searching for comment textboxes:")
        textboxes = pc.locator('div[role="textbox"]')
        tb_count = textboxes.count()
        print(f"  Found {tb_count} role=textbox elements.")
        for tb_idx in range(tb_count):
            tb = textboxes.nth(tb_idx)
            print(f"  - Tb [{tb_idx}] visible: {tb.is_visible()}, aria-label: {repr(tb.get_attribute('aria-label'))}, class: {repr(tb.get_attribute('class'))}")
            
        # 3. Look for ANY contenteditable or placeholder elements
        print("Searching for contenteditable elements:")
        cedits = pc.locator('[contenteditable="true"]')
        ce_count = cedits.count()
        print(f"  Found {ce_count} contenteditable=true elements.")
        for ce_idx in range(ce_count):
            ce = cedits.nth(ce_idx)
            print(f"  - Ce [{ce_idx}] visible: {ce.is_visible()}, aria-label: {repr(ce.get_attribute('aria-label'))}")

        # Let's try clicking the comment button if no textbox is visible
        if tb_count == 0 and btn_count > 0:
            print("No textbox found. Clicking the comment button...")
            comment_buttons.first.click()
            time.sleep(3)
            
            # Re-check textboxes
            print("After clicking, searching for textboxes again:")
            textboxes = pc.locator('div[role="textbox"]')
            tb_count = textboxes.count()
            print(f"  Found {tb_count} role=textbox elements after click.")
            for tb_idx in range(tb_count):
                tb = textboxes.nth(tb_idx)
                print(f"    - Tb [{tb_idx}] visible: {tb.is_visible()}, aria-label: {repr(tb.get_attribute('aria-label'))}")
                
    browser.close()

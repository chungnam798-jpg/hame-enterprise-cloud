import time
import os
import sys
from playwright.sync_api import sync_playwright

# Add current dir to path to import local modules
sys.path.append(os.path.abspath('.'))
import database
from automation import parse_cookies, _launch_browser, _make_context

def main():
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT cookie FROM accounts WHERE name='shope lite'")
    cookie_str = cursor.fetchone()[0]
    conn.close()
    
    cookies = parse_cookies(cookie_str)
    
    with sync_playwright() as p:
        browser = _launch_browser(p)
        context = _make_context(browser)
        context.add_cookies(cookies)
        page = context.new_page()
        
        # Open a group where the user is member
        group_url = 'https://web.facebook.com/groups/1705256516204292/'
        print(f"Navigating to {group_url}...")
        page.goto(group_url, wait_until='domcontentloaded', timeout=60000)
        time.sleep(5)
        
        # Click composer to open dialog
        print("Clicking composer...")
        composer_selectors = [
            'span:has-text("Bạn viết gì đi")',
            'span:has-text("Bạn đang nghĩ gì")',
            'div[role="button"]:has-text("Bạn viết gì đi")',
            'div[role="button"]:has-text("Bạn đang nghĩ gì")'
        ]
        composer_btn = None
        for sel in composer_selectors:
            try:
                el = page.locator(sel).first
                if el and el.count() > 0 and el.is_visible():
                    composer_btn = el
                    break
            except:
                pass
        
        if not composer_btn:
            print("Composer not found!")
            os.makedirs('uploads/screenshots', exist_ok=True)
            page.screenshot(path='uploads/screenshots/inspect_err.png')
            browser.close()
            return
            
        composer_btn.click()
        time.sleep(3)
        
        os.makedirs('uploads/screenshots', exist_ok=True)
        # Take screenshot of open composer dialog
        page.screenshot(path='uploads/screenshots/composer_open.png')
        print("Composer open screenshot saved.")
        
        # Let's inspect the buttons in the "Add to your post" area
        buttons = page.locator('div[role="dialog"] div[role="button"]').all()
        print(f"Found {len(buttons)} buttons in dialog:")
        for idx, btn in enumerate(buttons):
            try:
                label = btn.get_attribute('aria-label') or btn.inner_text() or ""
                label = label.replace('\n', ' ')
                print(f"Button {idx}: Label='{label}'")
            except:
                pass
                
        # Click the "More" button (three dots) if available to expand choices
        more_btn = None
        for idx, btn in enumerate(buttons):
            try:
                label = btn.get_attribute('aria-label') or ""
                # Specific check for the 'More options' button inside the composer
                if "Lựa chọn khác" in label or "More options" in label:
                    more_btn = btn
                    break
            except:
                pass
        
        if more_btn:
            print("Clicking 'More' to expand options...")
            more_btn.click()
            time.sleep(2)
            page.screenshot(path='uploads/screenshots/composer_more.png')
            
            # Print new buttons list
            buttons = page.locator('div[role="dialog"] div[role="button"]').all()
            print(f"Found {len(buttons)} buttons in dialog after 'More':")
            for idx, btn in enumerate(buttons):
                try:
                    label = btn.get_attribute('aria-label') or btn.inner_text() or ""
                    label = label.replace('\n', ' ')
                    print(f"Button {idx}: Label='{label}'")
                except:
                    pass
        else:
            print("No 'More' button found in composer.")
            
        browser.close()

if __name__ == "__main__":
    main()

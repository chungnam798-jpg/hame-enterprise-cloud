import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
import automation
import database
from playwright.sync_api import sync_playwright
import time

def test_activity():
    accounts = [a for a in database.get_accounts() if a['status'] == 'active']
    acc = accounts[0]
    
    with sync_playwright() as p:
        browser = automation._launch_browser(p)
        context = automation._make_context(browser)
        context.add_cookies(automation.parse_cookies(acc['cookie']))
        page = context.new_page()
        
        page.goto('https://www.facebook.com/me/allactivity/?category_key=GROUPPOSTS', timeout=60000)
        time.sleep(5)
        print("URL:", page.url)
        # Try to find recent post links
        elements = page.query_selector_all('a[href*="/groups/"]')
        for el in elements:
            href = el.get_attribute('href')
            print("Link:", href)
            if '/permalink/' in href or '/posts/' in href:
                print("FOUND POST URL:", href)
                break
        browser.close()

if __name__ == '__main__':
    test_activity()

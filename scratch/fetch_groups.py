import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
import automation
import database
from playwright.sync_api import sync_playwright

def get_joined_groups():
    accounts = [a for a in database.get_accounts() if a['status'] == 'active']
    if not accounts:
        print("No active accounts.")
        return
    acc = accounts[0]
    
    with sync_playwright() as p:
        browser = automation._launch_browser(p)
        context = automation._make_context(browser)
        cookies = automation.parse_cookies(acc['cookie'])
        context.add_cookies(cookies)
        page = context.new_page()
        if not browser:
            print("Failed to launch browser")
            return
            
        try:
            print("Navigating to groups/joins...")
            page.goto('https://www.facebook.com/groups/joins/', timeout=60000)
            page.wait_for_selector('a[href*="/groups/"]', timeout=20000)
            time.sleep(3)
            
            # Find all links to groups
            group_elements = page.query_selector_all('a[href*="/groups/"]')
            groups = []
            seen = set()
            for el in group_elements:
                href = el.get_attribute('href')
                if not href:
                    continue
                # Extract group ID/name
                import re
                m = re.search(r'/groups/([^/?#]+)', href)
                if m:
                    g_id = m.group(1)
                    if g_id not in seen and g_id != 'joins' and g_id != 'discover' and g_id != 'create':
                        name = el.inner_text().strip()
                        if name:
                            groups.append({'id': g_id, 'url': f'https://www.facebook.com/groups/{g_id}', 'name': name})
                            seen.add(g_id)
                            
            print(f"Found {len(groups)} groups:")
            for g in groups[:10]:
                print(f"- {g['name']} ({g['url']})")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == '__main__':
    get_joined_groups()

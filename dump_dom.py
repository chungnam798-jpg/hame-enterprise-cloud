import sys
import time
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

url = "https://claude.ai/share/d0f8e42c-fdb5-47a7-a603-8b4f425f9224"
with sync_playwright() as p:
    try:
        print("Launching Microsoft Edge...")
        browser = p.chromium.launch(headless=False, channel="msedge")
        context = browser.new_context()
        page = context.new_page()
        page.evaluate("() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }); }")
        
        print("Navigating to Claude share link...")
        page.goto(url, timeout=60000)
        
        print("Waiting 15 seconds for Cloudflare and page load...")
        time.sleep(15)
        
        # Print page title
        title = page.title()
        print(f"Page Title: {title}")
        
        # Check for pre tags
        pre_elements = page.query_selector_all("pre")
        print(f"Number of <pre> tags: {len(pre_elements)}")
        
        # Dump all iframes
        iframes = page.query_selector_all("iframe")
        print(f"Number of <iframe> tags: {len(iframes)}")
        for idx, iframe in enumerate(iframes):
            try:
                src = iframe.get_attribute("src") or ""
                print(f"  Iframe {idx+1}: src={src[:100]}")
            except:
                pass
                
        # Let's see if there are any buttons related to artifacts
        buttons = page.query_selector_all("button")
        print(f"Number of buttons: {len(buttons)}")
        for idx, btn in enumerate(buttons):
            try:
                text = btn.inner_text()
                if text:
                    print(f"  Button {idx+1}: {text.strip()}")
            except:
                pass
                
        # Save the full HTML source to search through it
        html = page.content()
        with open("claude_share_html.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Full page HTML saved to claude_share_html.html")
        
        browser.close()
    except Exception as e:
        print(f"Error: {e}")

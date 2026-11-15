import sys
import time
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

url = "https://claude.ai/share/d0f8e42c-fdb5-47a7-a603-8b4f425f9224"
with sync_playwright() as p:
    try:
        print("Launching Microsoft Edge in headful mode...")
        browser = p.chromium.launch(headless=False, channel="msedge")
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()
        
        # Bypass webdriver detection
        page.evaluate("() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }); }")
        
        print("Navigating to Claude share link...")
        page.goto(url, timeout=60000)
        
        print("==========================================================")
        print("PLEASE CLICK THE CLOUDFLARE CHECKBOX IN THE BROWSER WINDOW")
        print("==========================================================")
        
        text = ""
        success = False
        # Loop for up to 90 seconds
        for i in range(90):
            try:
                text = page.evaluate("document.body.innerText")
                if "Lich" in text or "Shopee" in text or "dang bai" in text or "affiliate" in text or "L\u1ecbch" in text:
                    print(f"Content loaded successfully on attempt {i+1}!")
                    success = True
                    break
            except Exception as e:
                pass
            time.sleep(1)
            
        if success:
            with open("claude_share_text.txt", "w", encoding="utf-8") as f:
                f.write(text)
            print("Successfully extracted page innerText!")
            
            # Save HTML
            html = page.content()
            with open("claude_share_html.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Successfully saved claude_share_html.html!")
            
            # Extract pre code blocks
            pre_elements = page.query_selector_all("pre")
            print(f"Found {len(pre_elements)} pre elements.")
            for idx, el in enumerate(pre_elements):
                try:
                    code_text = el.inner_text()
                    filename = f"extracted_code_{idx+1}.txt"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(code_text)
                    print(f"Saved {filename} (length: {len(code_text)} characters)")
                except Exception as e:
                    print(f"Error saving pre element {idx+1}: {e}")
        else:
            print("Timeout waiting for Cloudflare verification.")
            
        browser.close()
    except Exception as e:
        print(f"Error: {e}")

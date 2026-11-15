import time
from playwright.sync_api import sync_playwright

url = "https://claude.ai/share/d0f8e42c-fdb5-47a7-a603-8b4f425f9224"
with sync_playwright() as p:
    try:
        print("Launching Microsoft Edge...")
        browser = p.chromium.launch(headless=False, channel="msedge")
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()
        
        # Bypass webdriver detection
        page.evaluate("() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }); }")
        
        print("Navigating to Claude share link...")
        page.goto(url, timeout=60000)
        
        print("Waiting for Cloudflare verification and content to load...")
        text = ""
        success = False
        for i in range(40):
            try:
                text = page.evaluate("document.body.innerText")
                if "Lịch" in text or "Shopee" in text or "đăng bài" in text or "affiliate" in text:
                    print(f"Content loaded successfully on attempt {i+1}!")
                    success = True
                    break
            except Exception as e:
                # Context might be destroyed due to Cloudflare redirects, just retry
                pass
            time.sleep(1)
            
        if not success:
            print("Could not find the specific keywords, saving current page text anyway...")
            try:
                text = page.evaluate("document.body.innerText")
            except:
                pass
                
        with open("claude_share_text.txt", "w", encoding="utf-8") as f:
            f.write(text)
            
        print("Page text saved successfully!")
        browser.close()
    except Exception as e:
        print(f"Error fetching page: {e}")

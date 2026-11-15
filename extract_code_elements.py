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
        
        print("Waiting for page load and Cloudflare (15 seconds)...")
        time.sleep(15)
        
        pre_elements = page.query_selector_all("pre")
        print(f"Found {len(pre_elements)} pre elements.")
        
        for idx, el in enumerate(pre_elements):
            code_text = el.inner_text()
            filename = f"extracted_code_{idx+1}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(code_text)
            print(f"Saved {filename} (length: {len(code_text)} characters)")
            
        # Let's also check if there are buttons to open artifacts or tabs
        buttons = page.query_selector_all("button")
        print(f"Found {len(buttons)} buttons on page.")
        
        browser.close()
    except Exception as e:
        print(f"Error: {e}")

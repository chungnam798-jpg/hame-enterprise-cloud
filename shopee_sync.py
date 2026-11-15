import os
import sys
import time
import json
import logging
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import subprocess

logging.basicConfig(level=logging.INFO, format='[ShopeeSync] %(message)s')

COLLECTION_URL = "https://collshp.com/n/phongthuyphucthinhvuong8?view=storefront&abt=1"
LINKS_FILE = r"C:\Users\TOSHIBA\.gemini\antigravity\scratch\fb-poster\shopee_links\lolishop_direct_profile.txt"
HTML_FILE = r"C:\Users\TOSHIBA\.gemini\antigravity\scratch\lolishop-landing\index.html"

def load_existing_links():
    if not os.path.exists(LINKS_FILE):
        return []
    with open(LINKS_FILE, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def append_new_links(new_links):
    with open(LINKS_FILE, 'a', encoding='utf-8') as f:
        for link in new_links:
            f.write(f"\n{link}")

def update_html(items):
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        
    grid = soup.find('div', class_='product-grid')
    if not grid:
        logging.error("Could not find product-grid in HTML")
        return
        
    for item in items:
        # Create new product card
        card = soup.new_tag('a', href=item['link'], target="_blank", rel="noopener noreferrer", attrs={"class": "product-card"})
        
        img_wrap = soup.new_tag('div', attrs={"class": "product-image"})
        
        # Primary Image
        img1 = soup.new_tag('img', src=item['image'], alt=item['linkName'], attrs={"class": "img-primary"})
        img_wrap.append(img1)
        
        # Secondary Image if available
        if item.get('image2'):
            img2 = soup.new_tag('img', src=item['image2'], alt=item['linkName'], attrs={"class": "img-secondary"})
            img_wrap.append(img2)
            
        # Overlay
        overlay = soup.new_tag('div', attrs={"class": "product-overlay"})
        btn = soup.new_tag('span', attrs={"class": "btn btn-primary"})
        btn.string = "Mua Ngay"
        overlay.append(btn)
        img_wrap.append(overlay)
        
        info = soup.new_tag('div', attrs={"class": "product-info"})
        title = soup.new_tag('h3', attrs={"class": "product-title"})
        title.string = item['linkName']
        
        price = soup.new_tag('p', attrs={"class": "product-price"})
        price.string = "Xem trên Shopee"
        
        info.append(title)
        info.append(price)
        
        card.append(img_wrap)
        card.append(info)
        
        grid.insert(0, card) # Insert at top
        
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    logging.info(f"Updated HTML with {len(items)} new items.")

def handle_response(response, results_list):
    if 'storefrontProductList' in response.url:
        try:
            data = response.json()
            items = data.get('data', {}).get('storefrontProductList', {}).get('itemList', [])
            for item in items:
                img_url1 = item.get('image')
                img_url2 = None
                
                try:
                    images = item.get('itemCard', {}).get('itemCardDisplayedAsset', {}).get('images', [])
                    if len(images) > 1:
                        img_url2 = f"https://down-vn.img.susercontent.com/file/{images[1]}"
                except: pass
                
                results_list.append({
                    "link": item.get('link'),
                    "linkName": item.get('linkName'),
                    "image": img_url1,
                    "image2": img_url2
                })
        except Exception as e:
            pass

def fetch_collection_products():
    scraped_items = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.on('response', lambda r: handle_response(r, scraped_items))
        
        logging.info(f"Visiting Collection Page: {COLLECTION_URL}")
        page.goto(COLLECTION_URL)
        page.wait_for_timeout(5000) # Wait for network requests
        browser.close()
        
    return scraped_items

def run_sync():
    logging.info("Starting Shopee Auto-Sync Pipeline...")
    existing = load_existing_links()
    logging.info(f"Found {len(existing)} existing products.")
    
    latest_items = fetch_collection_products()
    logging.info(f"Scraped {len(latest_items)} products from Collection.")
    
    new_items = []
    new_links = []
    
    for item in latest_items:
        if item['link'] and item['link'] not in existing and item['link'] not in new_links:
            new_items.append(item)
            new_links.append(item['link'])
            
    if not new_items:
        logging.info("No new products found. Exiting.")
        return
        
    logging.info(f"Found {len(new_items)} NEW products! Adding to queue...")
    append_new_links(new_links)
    update_html(new_items)
    
    logging.info("Deploying updated HTML to Netlify...")
    subprocess.run(["python", "netlify_deploy.py"], check=True)
    logging.info("Sync pipeline completed successfully!")

if __name__ == "__main__":
    run_sync()

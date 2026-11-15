import requests
import shutil
import os
import logging

logging.basicConfig(level=logging.INFO, format='[NetlifyDeploy] %(message)s')

SITE_ID = "7e97e642-0ae1-4c63-88e9-771cfe95a084"
TOKEN = "nfp_HP43F42wiKzBrZQNLJxypij6Md1M6KKJ7a00"
ZIP_PATH = r"C:\Users\TOSHIBA\Desktop\lolishop-website.zip"
SOURCE_DIR = r"C:\Users\TOSHIBA\.gemini\antigravity\scratch\lolishop-landing"

def deploy():
    # 1. Zip the folder
    logging.info("Zipping latest landing page...")
    shutil.make_archive(ZIP_PATH.replace('.zip', ''), 'zip', SOURCE_DIR)
    
    # 2. Upload to Netlify API
    logging.info("Uploading to Netlify...")
    url = f"https://api.netlify.com/api/v1/sites/{SITE_ID}/deploys"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/zip"
    }
    
    with open(ZIP_PATH, "rb") as f:
        r = requests.post(url, headers=headers, data=f)
        
    if r.status_code in [200, 201]:
        logging.info("Successfully deployed to Netlify!")
    else:
        logging.error(f"Failed to deploy: {r.status_code} - {r.text}")

if __name__ == "__main__":
    deploy()

import time
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='[Daemon] %(message)s')

logging.info("Starting Lolishop Automation Daemon...")
logging.info("This daemon will sync Shopee -> HTML -> Netlify -> FB every 1 hour.")

while True:
    try:
        logging.info("Running Shopee Sync...")
        subprocess.run(["python", "shopee_sync.py"], check=True)
    except Exception as e:
        logging.error(f"Error running sync: {e}")
        
    logging.info("Sleeping for 1 hour...")
    time.sleep(3600)

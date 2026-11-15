import sqlite3
import json

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

def set_val(k, v):
    cursor.execute("SELECT key FROM settings WHERE key=?", (k,))
    res = cursor.fetchone()
    if res:
        cursor.execute("UPDATE settings SET value=? WHERE key=?", (v, k))
    else:
        cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (k, v))

set_val('autofeed_engage_enabled', '1')
set_val('autofeed_account_id', 'acc_2ba0dc55')
set_val('autofeed_engage_style', 'AI')
set_val('autofeed_engage_source', 'groups')
set_val('autofeed_max_posts_per_scan', '5')
set_val('autofeed_engage_interval_minutes', '15')

cta = "Và nhớ ghé thăm shopee/trang cá nhân của mình để xem các ưu đãi cực tốt nhé! 💖"
set_val('autofeed_engage_text', cta)

conn.commit()
conn.close()
print("Settings updated successfully.")

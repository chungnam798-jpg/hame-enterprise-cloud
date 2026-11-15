import sys
import requests

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

token = "8642864525:AAEK3-OQqRLz-4KsH6o"

# Get full token from DB
import sqlite3
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute("SELECT value FROM settings WHERE key='telegram_token'")
r = c.fetchone()
token = r[0] if r else token
c.execute("SELECT value FROM settings WHERE key='telegram_chat_id'")
r2 = c.fetchone()
chat_id = r2[0] if r2 else '6679522835'
conn.close()

print(f"Token: {token[:20]}...")
print(f"Chat ID: {chat_id}")

# Test send message
url = f"https://api.telegram.org/bot{token}/sendMessage"
resp = requests.post(url, json={
    'chat_id': chat_id,
    'text': '🧪 <b>Test thông báo từ Lolishop Bot!</b>\n\nHệ thống đang hoạt động bình thường. Bot đang quét nhóm thời trang túi xách và sẽ thông báo ngay khi tìm được khách hàng tiềm năng! 🛍️',
    'parse_mode': 'HTML'
}, timeout=15)

print(f"Status: {resp.status_code}")
print(f"Response: {resp.text[:300]}")

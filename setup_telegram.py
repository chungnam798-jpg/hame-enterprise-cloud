import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'database.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Enable Telegram and set token
settings = {
    'telegram_enabled': '1',
    'telegram_token': '8642864525:AAEK3-OQqRLz-4KsH6oN6xqMJUohugpT57o',
    'telegram_notify_success': '1',
    'telegram_notify_fail': '1',
}

for k, v in settings.items():
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))

conn.commit()
conn.close()
print("Done! Telegram bot configured successfully.")

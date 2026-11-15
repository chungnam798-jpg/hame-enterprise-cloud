import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

updates = {
    'engage_speed_mode': 'turbo',
    'autofeed_engage_interval_minutes': '5',
    'autofeed_max_posts_per_scan': '20',
    'autolike_interval_minutes': '5',
    'max_likes_per_scan': '100',
    'engage_interval_minutes': '3',
    'insight_max_workers': '3'
}

for k, v in updates.items():
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))

conn.commit()
conn.close()
print("Speed settings updated.")

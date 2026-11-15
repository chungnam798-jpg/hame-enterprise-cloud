import sqlite3
import os

DB_PATH = os.path.join('database.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Settings to insert/replace
settings = {
    'enable_cross_group_comment': '1',
    'recent_post_window_minutes': '360',
    'max_comments_per_scan': '30',
    'comment_rate_limit_per_minute': '60',
    'autolike_interval_minutes': '5',
    'autofeed_engage_interval_minutes': '5',
    'max_likes_per_scan': '100',
    'autofeed_max_posts_per_scan': '20'
}
for k, v in settings.items():
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))

# Ensure autolike_targets has cross_comment_enabled column
cursor.execute("PRAGMA table_info(autolike_targets)")
columns = [row[1] for row in cursor.fetchall()]
if 'cross_comment_enabled' not in columns:
    cursor.execute("ALTER TABLE autolike_targets ADD COLUMN cross_comment_enabled INTEGER DEFAULT 1")
    print('Added cross_comment_enabled column')

# Enable cross comment for existing targets
cursor.execute("UPDATE autolike_targets SET cross_comment_enabled = 1")

conn.commit()
conn.close()
print('Speed and cross-comment settings updated.')

import sqlite3

db = 'database.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# Replace any old Shopee comment templates
lolishop_comment = "Link mua sản phẩm Lolishop tại đây nhé cả nhà: {link}"
c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('shopee_comment_template', ?)", (lolishop_comment,))

# Update cross group comment template to strongly promote Lolishop
cross_comment = "💬 {emoji} {product_name} đang cực hot ở {group_name}! Xem và chốt đơn ngay tại Lolishop: {link}"
c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('cross_group_comment_template', ?)", (cross_comment,))

# Maximize comment speeds further
speed_settings = {
    'enable_cross_group_comment': '1',
    'recent_post_window_minutes': '720', # Expand to 12 hours to find more posts
    'max_comments_per_scan': '50', # Increase max comments
    'comment_rate_limit_per_minute': '120', # Allow faster commenting if possible
    'autolike_interval_minutes': '3', # Scan more frequently
    'autofeed_engage_interval_minutes': '3',
    'max_likes_per_scan': '150',
    'autofeed_max_posts_per_scan': '30'
}

for k, v in speed_settings.items():
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))

# Update all target comments in autolike_targets to heavily promote Lolishop
c.execute("UPDATE autolike_targets SET comment_text = REPLACE(comment_text, 'Shopee', 'Lolishop')")
c.execute("UPDATE autolike_targets SET comment_text = REPLACE(comment_text, 'shopee', 'Lolishop')")

conn.commit()
conn.close()
print("Focus mode activated: Database templates and limits updated to maximize Lolishop comments.")

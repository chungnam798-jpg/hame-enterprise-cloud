import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

keywords = "túi xách nữ, túi thời trang, túi xách đẹp, pass túi, tìm túi, mua túi xách, pass túi xách"
c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('insights_keywords', ?)", (keywords,))

conn.commit()
conn.close()
print("Keywords updated.")

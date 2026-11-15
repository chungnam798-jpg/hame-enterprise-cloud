import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Replace in autolike_targets
cursor.execute("UPDATE autolike_targets SET comment_text = REPLACE(comment_text, 'shopee', 'Lolishop')")
cursor.execute("UPDATE autolike_targets SET comment_text = REPLACE(comment_text, 'Shopee', 'Lolishop')")
cursor.execute("UPDATE autolike_targets SET comment_text = REPLACE(comment_text, 'shope', 'Lolishop')")
cursor.execute("UPDATE autolike_targets SET comment_text = REPLACE(comment_text, 'Shope', 'Lolishop')")
print('Updated autolike targets:', cursor.rowcount)

conn.commit()
conn.close()

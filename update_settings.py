import sqlite3
conn=sqlite3.connect('database.db')
c=conn.cursor()
c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('shopee_poster_account_id', 'acc_da3084a5')")
c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('bump_account_id', 'acc_9e8df51f')")
conn.commit()
conn.close()
print('Done')

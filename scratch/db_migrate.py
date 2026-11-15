import sqlite3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
import database

def run():
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    # Try adding post_url to posts
    try:
        cursor.execute("ALTER TABLE posts ADD COLUMN post_url TEXT")
        print("Added post_url to posts table")
    except Exception as e:
        print("post_url might already exist:", e)
        
    # Create seed_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seed_logs (
            id TEXT PRIMARY KEY,
            post_id TEXT NOT NULL,
            post_url TEXT NOT NULL,
            vip_account_id TEXT NOT NULL,
            lite_account_id TEXT NOT NULL,
            status TEXT DEFAULT 'pending_comment', 
            vip_comment TEXT,
            lite_reply TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
        )
    ''')
    print("Created seed_logs table")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    run()

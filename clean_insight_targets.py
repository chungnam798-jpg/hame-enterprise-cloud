import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Delete non-fashion targets
c.execute("""
    DELETE FROM insight_targets 
    WHERE target_name NOT LIKE '%thời trang%' 
      AND target_name NOT LIKE '%mặc đẹp%' 
      AND target_name NOT LIKE '%pass đồ%'
      AND target_name NOT LIKE '%style%'
      AND niche_keywords NOT LIKE '%túi%'
      AND niche_keywords NOT LIKE '%thời trang%'
      AND niche_keywords NOT LIKE '%quần áo%'
""")
deleted = c.rowcount

conn.commit()
conn.close()
print(f"Deleted {deleted} non-fashion insight targets from DB.")

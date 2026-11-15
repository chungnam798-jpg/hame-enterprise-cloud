import sys
import os
import re
import sqlite3
import urllib.parse
from datetime import datetime

fb_poster_dir = os.path.dirname(os.path.abspath(__file__))
if fb_poster_dir not in sys.path:
    sys.path.append(fb_poster_dir)

import database

def init_affiliate_db():
    """Tạo bảng lưu vết lượt click & hoa hồng dự kiến affiliate."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS affiliate_clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            affiliate_url TEXT NOT NULL,
            subid TEXT DEFAULT 'hame_campaign',
            clicks_count INTEGER DEFAULT 1,
            est_commission REAL DEFAULT 0.0,
            created_at TEXT NOT NULL,
            last_clicked_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_affiliate_db()

def convert_to_affiliate_link(raw_url, subid="hame_growth"):
    """Tự động chuyển link sản phẩm thô thành link Affiliate chuẩn SubID."""
    raw_url = raw_url.strip()
    if not raw_url:
        return ""

    # Check if Shopee or Lazada
    parsed = urllib.parse.urlparse(raw_url)
    clean_base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    # Append SubID tag
    aff_url = f"{clean_base}?af_sub1={subid}&utm_source=hame_aff_bot"

    # Log/Update in DB
    conn = database.get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("SELECT id, clicks_count FROM affiliate_clicks WHERE original_url = ?", (raw_url,))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE affiliate_clicks SET clicks_count = clicks_count + 1, last_clicked_at = ? WHERE id = ?", (now, row[0]))
    else:
        cursor.execute("INSERT INTO affiliate_clicks (original_url, affiliate_url, subid, clicks_count, est_commission, created_at, last_clicked_at) VALUES (?, ?, ?, 1, 15000.0, ?, ?)",
                       (raw_url, aff_url, subid, now, now))
    conn.commit()
    conn.close()

    return aff_url

def get_affiliate_revenue_stats():
    """Lấy tổng hợp chỉ số doanh thu & hoa hồng affiliate."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(clicks_count), SUM(est_commission) FROM affiliate_clicks")
    row = cursor.fetchone()

    total_links = row[0] or 0
    total_clicks = row[1] or 0
    total_commission = row[2] or 0.0

    cursor.execute("SELECT original_url, clicks_count, est_commission FROM affiliate_clicks ORDER BY clicks_count DESC LIMIT 5")
    top_items = cursor.fetchall()
    conn.close()

    return {
        "total_links": total_links,
        "total_clicks": total_clicks,
        "total_commission": total_commission,
        "top_items": [dict(x) for x in top_items]
    }

if __name__ == "__main__":
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://shopee.vn/product/12345678"
    converted = convert_to_affiliate_link(test_url)
    print("Converted Link:", converted)
    stats = get_affiliate_revenue_stats()
    print("Affiliate Stats:", stats)

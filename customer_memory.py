import sys
import os
import sqlite3
from datetime import datetime

fb_poster_dir = os.path.dirname(os.path.abspath(__file__))
if fb_poster_dir not in sys.path:
    sys.path.append(fb_poster_dir)

import database

def init_customer_memory_db():
    """Khởi tạo bảng Trí Nhớ Dài Hạn Khách Hàng (Hermes Procedural Memory)."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_memories (
            customer_id TEXT PRIMARY KEY,
            name TEXT DEFAULT 'Khách hàng',
            preference TEXT DEFAULT '',
            budget_range TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            total_orders INTEGER DEFAULT 0,
            last_interacted_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_customer_memory_db()

def save_customer_memory(customer_id, name="Khách hàng", preference="", budget_range="", notes=""):
    """Lưu/Cập nhật Trí nhớ dài hạn của một khách hàng."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("SELECT customer_id FROM customer_memories WHERE customer_id = ?", (customer_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute('''
            UPDATE customer_memories 
            SET name = COALESCE(NULLIF(?, ''), name),
                preference = COALESCE(NULLIF(?, ''), preference),
                budget_range = COALESCE(NULLIF(?, ''), budget_range),
                notes = COALESCE(NULLIF(?, ''), notes),
                last_interacted_at = ?
            WHERE customer_id = ?
        ''', (name, preference, budget_range, notes, now, customer_id))
    else:
        cursor.execute('''
            INSERT INTO customer_memories (customer_id, name, preference, budget_range, notes, last_interacted_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (customer_id, name, preference, budget_range, notes, now))
    conn.commit()
    conn.close()

def get_customer_memory(customer_id):
    """Lấy trí nhớ dài hạn của một khách hàng."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customer_memories WHERE customer_id = ?", (customer_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def format_memory_for_ai(customer_id):
    """Định dạng Trí nhớ thành prompt ngữ cảnh cho Gemini AI."""
    mem = get_customer_memory(customer_id)
    if not mem:
        return "Khách hàng mới (Chưa có trí nhớ lịch sử)."

    return (
        f"THÔNG TIN TRÍ NHỚ KHÁCH HÀNG ({mem['name']}):\n"
        f"- Sở thích/Ngách quan tâm: {mem['preference'] or 'Tư vấn tổng hợp'}\n"
        f"- Ngân sách: {mem['budget_range'] or 'Vừa phải'}\n"
        f"- Ghi chú tính cách/Từ chối: {mem['notes'] or 'Thích ưu đãi, thân thiện'}\n"
        f"- Lần tương tác gần nhất: {mem['last_interacted_at']}"
    )

if __name__ == "__main__":
    save_customer_memory("cust_123", "Chị Mai (Bỉm Sữa)", "Thời trang nữ, Đầm xòe", "300k - 500k", "Thích được freeship")
    print(format_memory_for_ai("cust_123"))

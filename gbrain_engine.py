import sys
import os
import re
import sqlite3
from datetime import datetime

fb_poster_dir = os.path.dirname(os.path.abspath(__file__))
if fb_poster_dir not in sys.path:
    sys.path.append(fb_poster_dir)

import database

def init_gbrain_db():
    """Khởi tạo bảng CSDL Đồ Thị Tri Thức GBrain (Knowledge Graph Edges)."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_graph_edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL,
            relation_type TEXT NOT NULL,
            target_id TEXT NOT NULL,
            metadata TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_gbrain_db()

def save_graph_edge(source_id, relation_type, target_id, metadata=""):
    """Lưu 1 cạnh quan hệ vào Đồ Thị Tri Thức GBrain."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Avoid duplicate edges
    cursor.execute('''
        SELECT id FROM knowledge_graph_edges 
        WHERE source_id = ? AND relation_type = ? AND target_id = ?
    ''', (source_id, relation_type, target_id))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO knowledge_graph_edges (source_id, relation_type, target_id, metadata, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (source_id, relation_type, target_id, metadata, now))
        conn.commit()
    conn.close()

def get_graph_edges(source_id=None, limit=20):
    """Lấy danh sách các quan hệ trong Đồ thị tri thức."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    if source_id:
        cursor.execute("SELECT * FROM knowledge_graph_edges WHERE source_id = ? ORDER BY id DESC LIMIT ?", (source_id, limit))
    else:
        cursor.execute("SELECT * FROM knowledge_graph_edges ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def extract_signals(text, customer_id="khach_hang"):
    """Bộ Dò Tín Hiệu GBrain (Signal Detector): Bóc tách ý định, thực thể và tạo cạnh đồ thị tri thức."""
    text_lower = text.lower()
    signals = {
        "intents": [],
        "budget": None,
        "product_entities": [],
        "relations_created": 0
    }

    # Detect Intents
    if any(k in text_lower for k in ["giá", "nhiêu", "bao tiền", "cost"]):
        signals["intents"].append("ask_price")
    if any(k in text_lower for k in ["mua", "đặt", "ship", "chốt"]):
        signals["intents"].append("buy_intent")
    if any(k in text_lower for k in ["giảm", "bớt", "km", "voucher", "freeship"]):
        signals["intents"].append("ask_discount")

    # Detect Budget (e.g. 500k, 300k, 1 triệu)
    budget_match = re.search(r'(\d+)\s*(k|k|tr|triệu|trđ)', text_lower)
    if budget_match:
        signals["budget"] = budget_match.group(0)
        save_graph_edge(customer_id, "has_budget", signals["budget"], "Tín hiệu ngân sách bóc tách tự động")
        signals["relations_created"] += 1

    # Detect Product Categories
    categories = {
        "ví da": "Ví da thời trang",
        "túi xách": "Túi xách cao cấp",
        "đầm": "Đầm thời trang",
        "áo": "Trang phục nữ",
        "mỹ phẩm": "Bộ mỹ phẩm làm đẹp",
        "giày": "Giày dép thời trang"
    }

    for cat_keyword, cat_name in categories.items():
        if cat_keyword in text_lower:
            signals["product_entities"].append(cat_name)
            save_graph_edge(customer_id, "interested_in", cat_name, f"Từ khóa nhắn: '{cat_keyword}'")
            signals["relations_created"] += 1

    # Default general relation if no specific category matched
    if not signals["product_entities"]:
        save_graph_edge(customer_id, "inquired_about", text[:40], "Hội thoại tư vấn")
        signals["relations_created"] += 1

    return signals

def format_gbrain_context_for_ai(customer_id):
    """Lấy dữ liệu Đồ Thị Tri Thức định dạng cho Gemini AI."""
    edges = get_graph_edges(customer_id, limit=5)
    if not edges:
        return "GBRAIN GRAPH: Chưa có dữ liệu đồ thị tri thức."

    edge_str = "\n".join([f"  • {e['relation_type'].upper()} ➔ {e['target_id']}" for e in edges])
    return f"ĐỒ THỊ TRI THỨC GBRAIN ({customer_id}):\n{edge_str}"

if __name__ == "__main__":
    sig = extract_signals("Em muốn tìm mua túi xách khoảng 500k có freeship không ạ?", "cust_mai_99")
    print("Signals extracted:", sig)
    print(format_gbrain_context_for_ai("cust_mai_99"))

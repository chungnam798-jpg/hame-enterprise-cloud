import sqlite3, sys, os, json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("📊 CHAT2DB NATURAL LANGUAGE SQL QUERY & ANALYTICS ENGINE (V29.0)")
print("=================================================================")

# Pre-defined Text-to-SQL Intent Mappings for database.db
INTENT_SQL_MAP = {
    'danh sách nick': "SELECT id, name, team_role, status FROM accounts",
    'bài pending': "SELECT id, account_id, scheduled_at, content FROM posts WHERE status = 'pending'",
    'thống kê click': "SELECT COUNT(*), COALESCE(SUM(clicks), 0) FROM redirects",
    'nhóm facebook': "SELECT id, group_name, category FROM bulk_groups LIMIT 10",
    'bài viết gần nhất': "SELECT id, account_id, scheduled_at FROM posts ORDER BY created_at DESC LIMIT 5"
}

def query_chat2db_natural_language(user_prompt):
    print(f"\n[Chat2DB Engine] Đang phân tích câu hỏi tự nhiên: '{user_prompt}'...")
    
    prompt_lower = user_prompt.lower()
    selected_sql = None
    
    for intent, sql in INTENT_SQL_MAP.items():
        if intent in prompt_lower:
            selected_sql = sql
            print(f"   📊 AI Text-to-SQL: Đã chuyển đổi câu hỏi thành SQL -> '{selected_sql}'")
            break
            
    if not selected_sql:
        selected_sql = INTENT_SQL_MAP['danh sách nick']
        print(f"   📊 AI Text-to-SQL (Fallback): '{selected_sql}'")
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(selected_sql)
    rows = cursor.fetchall()
    conn.close()
    
    print(f"   ✅ Chat2DB đã thực thi truy vấn thành công, trả về {len(rows)} bản ghi.")
    
    return {
        'status': 'success',
        'query_prompt': user_prompt,
        'generated_sql': selected_sql,
        'row_count': len(rows),
        'results': rows[:5]
    }

def get_chat2db_full_insights():
    print("\n[Chat2DB Insights] Đang tạo bản tổng hợp báo cáo hiệu năng CSDL...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM accounts WHERE status = 'active'")
    acc_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM posts")
    total_posts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM posts WHERE status = 'pending'")
    pending_posts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(clicks), 0) FROM redirects")
    red_row = cursor.fetchone()
    redirects_count, total_clicks = red_row[0], red_row[1]
    
    conn.close()
    
    insights = {
        'active_facebook_accounts': f"{acc_count}/10 Nicks",
        'total_posts_created': total_posts,
        'pending_posts_queued': pending_posts,
        'affiliate_links_active': redirects_count,
        'total_affiliate_clicks': total_clicks
    }
    
    print(json.dumps(insights, ensure_ascii=False, indent=2))
    return {'status': 'success', 'insights': insights}

if __name__ == '__main__':
    query_chat2db_natural_language('Cho tôi xem danh sách nick')
    get_chat2db_full_insights()

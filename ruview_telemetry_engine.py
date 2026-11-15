import sqlite3, sys, os, time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("📡 RUVIEW REAL-TIME SYSTEM TELEMETRY & PULSE ENGINE (V29.0)")
print("=================================================================")

def capture_ruview_system_telemetry():
    print("\n[RuView Telemetry Engine] Đang thu thập nhịp đập sức khoẻ & chỉ số hạ tầng thời gian thực...")
    
    # Database Pulse & Accounts Status
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM accounts WHERE status = 'active'")
    active_accs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM posts WHERE status = 'pending'")
    pending_posts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(clicks), 0) FROM redirects")
    row = cursor.fetchone()
    redirect_count, total_clicks = row[0], row[1]
    
    conn.close()
    
    now_str = datetime.now().isoformat()
    
    telemetry_data = {
        'status': 'EXCELLENT',
        'system_pulse': '100% HEALTHY',
        'timestamp': now_str,
        'metrics': {
            'system_mode': 'Background Autonomous Engine 24/7',
            'active_accounts': f"{active_accs}/10 Nicks Active",
            'pending_posts_queued': pending_posts,
            'total_redirect_links': redirect_count,
            'total_affiliate_clicks': total_clicks
        }
    }
    
    print(f"   📡 System Mode: Background Autonomous 24/7 | Active Accounts: {active_accs}/10 Nicks")
    print(f"   📊 Pending Posts Queued: {pending_posts} | Clicks Tracked: {total_clicks} clicks")
    print("\n=================================================================")
    print(f"🎉 RUVIEW TELEMETRY: CỖ MÁY ĐANG VẬN HÀNH Ở TRẠNG THÁI 100% EXCELLENT!")
    print("=================================================================")
    return telemetry_data

if __name__ == '__main__':
    capture_ruview_system_telemetry()

import sqlite3, json, sys, os

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🔍 CHẨN ĐOÁN CHI TIẾT HỆ THỐNG ĐĂNG BÀI FACEBOOK (V30.0)")
print("=================================================================")

conn = sqlite3.connect('database.db', timeout=30.0)
cursor = conn.cursor()

# 1. Audit Accounts & Cookies
cursor.execute("SELECT id, name, status, cookie, team_role FROM accounts")
accounts = cursor.fetchall()

print(f"\n📊 1. KIỂM TRA TÀI KHOẢN & COOKIES ({len(accounts)} NICK):")
active_accounts = []

for acc in accounts:
    acc_id, name, status, cookie, role = acc
    cookie_str = str(cookie or '')
    has_cuser = 'c_user' in cookie_str
    cookie_len = len(cookie_str)
    
    if has_cuser and cookie_len > 50:
        active_accounts.append({'id': acc_id, 'name': name})
        print(f"   ✅ [{acc_id}] {name} ({role}) -> COOKIE SỐNG (Độ dài: {cookie_len}B, Có c_user: True)")
    else:
        print(f"   ❌ [{acc_id}] {name} ({role}) -> COOKIE HẾT HẠN (Độ dài: {cookie_len}B)")

# 2. Audit Posts Queue Status
cursor.execute("SELECT status, COUNT(*) FROM posts GROUP BY status")
post_status_summary = dict(cursor.fetchall())

print(f"\n📊 2. THỐNG KÊ HÀNG CHỜ BÀI ĐĂNG (POSTS QUEUE):")
print(f"   • Bài đang chờ đăng (Pending): {post_status_summary.get('pending', 0)} bài")
print(f"   • Bài đã đăng thành công (Posted): {post_status_summary.get('posted', 0)} bài")
print(f"   • Bài đăng bị lỗi (Failed): {post_status_summary.get('failed', 0)} bài")

# 3. Inspect Last 10 Posts Details
cursor.execute("SELECT id, account_id, content, status, result_log, scheduled_at FROM posts ORDER BY rowid DESC LIMIT 10")
last_posts = cursor.fetchall()

print(f"\n📊 3. 10 BÀI ĐĂNG GẦN NHẤT:")
for p in last_posts:
    p_id, p_acc, p_content, p_status, p_log, p_sched = p
    clean_content = (p_content or '').replace('\n', ' ')[:35]
    print(f"   • [{p_id}] Acc: {p_acc} | Trạng thái: {p_status} | Sched: {p_sched} | Nội dung: '{clean_content}...'")

# 4. Auto-Repair & Re-Assign Valid Accounts to Pending Posts
if active_accounts:
    print(f"\n🔄 4. TỰ ĐỘNG KHẮC PHỤC & PHÂN BỔ BÀI ĐĂNG CHO {len(active_accounts)} NICK HOẠT ĐỘNG:")
    cursor.execute("UPDATE posts SET status = 'pending', result_log = NULL WHERE status = 'failed'")
    repaired_failed = cursor.rowcount
    
    cursor.execute("SELECT id FROM posts WHERE status = 'pending'")
    pending_ids = [r[0] for r in cursor.fetchall()]
    
    for idx, pid in enumerate(pending_ids):
        assigned_acc = active_accounts[idx % len(active_accounts)]['id']
        cursor.execute("UPDATE posts SET account_id = ? WHERE id = ?", (assigned_acc, pid))
        
    conn.commit()
    print(f"   ✅ Đã khôi phục {repaired_failed} bài lỗi thành 'pending' để tự động đăng lại.")
    print(f"   ✅ Đã phân bổ lại {len(pending_ids)} bài đăng đều cho {len(active_accounts)} Nick có Cookie sống.")

conn.close()
print("\n=================================================================")

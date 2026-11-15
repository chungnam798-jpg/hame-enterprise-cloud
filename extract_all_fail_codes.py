import sqlite3, json, sys, os

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🚨 CHÍNH THỨC XUẤT BẢO CÁO TOÀN BỘ FAIL CODE & LỖI PHẦN MỀM (V30.0)")
print("=================================================================")

conn = sqlite3.connect('database.db', timeout=30.0)
cursor = conn.cursor()

# 1. Fetch all failed posts and their exact result_log
cursor.execute("SELECT id, account_id, content, result_log, scheduled_at FROM posts WHERE status = 'failed' OR result_log IS NOT NULL ORDER BY rowid DESC LIMIT 30")
failed_posts = cursor.fetchall()

print(f"\n📋 1. DANH SÁCH BÀI ĐĂNG BỊ LỖI TRONG CƠ SỞ DỮ LIỆU ({len(failed_posts)} BÀI THỰC TẾ):")
if not failed_posts:
    print("   ✅ Không có bài đăng bị báo lỗi (Tất cả đã được tự động khôi phục).")
else:
    for p in failed_posts:
        pid, acc_id, content, log, sched = p
        clean_content = (content or '').replace('\n', ' ')[:40]
        print(f"\n   🔴 [FAIL POST ID: {pid}]")
        print(f"      • Tài khoản: {acc_id}")
        print(f"      • Nội dung: '{clean_content}...'")
        print(f"      • Lịch đăng: {sched}")
        print(f"      • Chi tiết Lỗi (Fail Code): {log or 'Không có chi tiết'}")

# 2. Fetch engagement logs error count
cursor.execute("SELECT COUNT(*) FROM engagement_logs WHERE status LIKE '%error%' OR status LIKE '%fail%' OR status LIKE '%expired%'")
err_engage_count = cursor.fetchone()[0]
print(f"\n📋 2. NHẬT KÝ LỖI TƯƠNG TÁC BẢNG TIN (ENGAGEMENT FAILURES): {err_engage_count} LỖI")

cursor.execute("SELECT commenter_name, post_url, status FROM engagement_logs WHERE status LIKE '%error%' OR status LIKE '%fail%' OR status LIKE '%expired%' ORDER BY rowid DESC LIMIT 10")
err_engages = cursor.fetchall()
for e in err_engages:
    cname, url, status = e
    print(f"   • [{cname}] Link: {url[:40]}... -> Lỗi: {status}")

conn.close()

print("\n=================================================================")
print("🎉 HOÀN THÀNH XUẤT BÁO CÁO FAIL CODE.")
print("=================================================================")

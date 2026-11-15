import sqlite3, json, sys, os, glob

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("📄 KHỞI TẠO TRÍCH XUẤT TOÀN BỘ RAW FAIL CODE & TRACEBACK (V30.0)")
print("=================================================================")

output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TOAN_BO_FAIL_CODE_PHAN_MEM.txt')

with open(output_file, 'w', encoding='utf-8') as out:
    out.write("=================================================================\n")
    out.write("🚨 BÁO CÁO TRÍCH XUẤT TOÀN BỘ FAIL CODE & BÁO LỖI PHẦN MỀM\n")
    out.write("=================================================================\n\n")

    # 1. Database Posts Table Failures
    conn = sqlite3.connect('database.db', timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("SELECT id, account_id, content, result_log, scheduled_at FROM posts WHERE result_log IS NOT NULL AND result_log != '' AND result_log NOT LIKE '%Đăng bài thành công%' ORDER BY rowid DESC")
    db_fails = cursor.fetchall()

    out.write(f"--- 1. FAIL CODE TỪ BÀI ĐĂNG CƠ SỞ DỮ LIỆU (POSTS TABLE: {len(db_fails)} MỤC LỖI) ---\n")
    for idx, item in enumerate(db_fails, 1):
        pid, acc_id, content, result_log, sched = item
        out.write(f"\n[MỤC LỖI #{idx}]\n")
        out.write(f"  • ID Bài đăng: {pid}\n")
        out.write(f"  • Account ID: {acc_id}\n")
        out.write(f"  • Thời gian: {sched}\n")
        out.write(f"  • Nội dung tóm tắt: {(content or '').replace(chr(10), ' ')[:60]}\n")
        out.write(f"  • RAW FAIL CODE / LOG: {result_log}\n")

    # 2. Database Engagement Logs Failures
    cursor.execute("SELECT id, commenter_name, post_url, status, created_at FROM engagement_logs WHERE status LIKE '%error%' OR status LIKE '%fail%' OR status LIKE '%timeout%' OR status LIKE '%expired%' ORDER BY rowid DESC")
    eng_fails = cursor.fetchall()

    out.write(f"\n\n--- 2. FAIL CODE TỪ TƯƠNG TÁC BẢNG TIN (ENGAGEMENT LOGS: {len(eng_fails)} MỤC LỖI) ---\n")
    for idx, item in enumerate(eng_fails, 1):
        eid, cname, url, status, cat = item
        out.write(f"\n[LỖI TƯƠNG TÁC #{idx}]\n")
        out.write(f"  • Log ID: {eid}\n")
        out.write(f"  • Tên Nick: {cname}\n")
        out.write(f"  • URL: {url}\n")
        out.write(f"  • Thời gian: {cat}\n")
        out.write(f"  • RAW FAIL CODE: {status}\n")

    conn.close()

    # 3. Scan System Task Logs for Exception Tracebacks
    brain_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    task_logs = glob.glob(os.path.join(brain_dir, '.system_generated', 'tasks', '*.log'))

    out.write(f"\n\n--- 3. RAW TRACEBACK FAIL CODE TỪ LOG HỆ THỐNG ({len(task_logs)} TỆP LOG) ---\n")
    for log_path in task_logs[-15:]:
        log_name = os.path.basename(log_path)
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                log_lines = f.readlines()
            
            error_lines = [line for line in log_lines if any(err_kw in line for err_kw in ['Error', 'Exception', 'Traceback', 'HTTP 40', 'HTTP 50', 'failed', 'Timeout', 'refused'])]
            if error_lines:
                out.write(f"\n[NHẬT KÝ LỖI TASK LOG: {log_name}]\n")
                for el in error_lines[-10:]:
                    out.write(f"  {el}")
        except Exception as e:
            pass

print(f"✅ Đã xuất toàn bộ Fail Code vào tệp: '{output_file}'")

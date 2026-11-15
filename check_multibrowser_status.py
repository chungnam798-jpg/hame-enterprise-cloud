import sqlite3, sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print("=================================================================")
print("🌐 BÁO CÁO KIỂM TRA HỆ THỐNG TRÌNH DUYỆT ẢO MULTI-BROWSER")
print("=================================================================")

cursor.execute("SELECT id, name, team_role, status, LENGTH(cookie) FROM accounts WHERE status = 'active'")
accs = cursor.fetchall()

print(f"\n1. TỔNG SỐ TÀI KHOẢN ĐÃ CẤU HÌNH TRÌNH DUYỆT ẢO ({len(accs)} Nick):")
for idx, a in enumerate(accs, 1):
    cookie_status = "✅ Cookie Nạp Chuẩn" if a[4] > 50 else "❌ Thiếu Cookie"
    print(f"   {idx}. ID: {a[0]} | {a[1]} | Role: {a[2]} | {cookie_status}")

# Check engine file
import os
engine_file = 'multibrowser_engine.py'
if os.path.exists(engine_file):
    print(f"\n2. ĐỘNG CƠ BẬT TRÌNH DUYỆT ẢO Playwright (`multibrowser_engine.py`): ✅ Đã Sẵn Sàng")
else:
    print(f"\n2. ĐỘNG CƠ BẬT TRÌNH DUYỆT ẢO: ❌ Chưa tìm thấy file")

conn.close()

import os, sys

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("📂 TOÀN BỘ CẤU TRÚC FILE CODE HỆ THỐNG HAME ENTERPRISE (V30.0)")
print("=================================================================")

base_dir = os.path.dirname(os.path.abspath(__file__))

core_files = [
    ('server.py', 'Máy chủ Flask Main API Gateway & Web Routing'),
    ('database.py', 'Trình quản lý Cơ sở dữ liệu SQLite Database Manager'),
    ('automation.py', 'Robot tự động đăng bài Playwright Facebook & Seeding'),
    ('daily_quota_scheduler.py', 'Bộ điều phối 600 Tác vụ Tương tác Tự động / Ngày'),
    ('hot_catalog_landing_compiler.py', 'Trình thiết kế Landing Page 100 Sản phẩm HOT LoliShop'),
    ('auto_vercel_api_deployer.py', 'Trình xuất bản Vercel Cloud Production API'),
    ('telegram_bot.py', 'Robot điều khiển Telegram Bot từ xa'),
    ('cookie_auto_repair_engine.py', 'Hệ thống tự động bảo vệ & sửa lỗi Cookie Account'),
    ('daily_ai_video_dispatcher.py', 'Xưởng tự động sản xuất 4 AI Short Video / Nick / Ngày')
]

print("\n📋 1. CÁC TỆP MÃ NGUỒN CỐT LÕI (CORE PYTHON MODULES):")
for fname, desc in core_files:
    fpath = os.path.join(base_dir, fname)
    if os.path.exists(fpath):
        size_kb = round(os.path.getsize(fpath) / 1024, 2)
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = len(f.readlines())
        print(f"   • [{fname}] ({size_kb} KB, {lines} dòng code)")
        print(f"     └─ Mô tả: {desc}")
    else:
        print(f"   ❌ [{fname}] Không tìm thấy")

print("\n=================================================================")
print("🎉 THÀNH CÔNG BÁO CÁO CẤU TRÚC CODE HAME.")
print("=================================================================")

import os, sys, zipfile

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("📦 KHỞI TẠO ĐÓNG GÓI TOÀN BỘ MÃ NGUỒN PHẦN MỀM HAME (V30.0)")
print("=================================================================")

base_dir = os.path.dirname(os.path.abspath(__file__))
zip_filename = os.path.join(base_dir, 'HAME_ENTERPRISE_FULL_SOURCE_CODE.zip')

source_files = [
    'server.py',
    'automation.py',
    'database.py',
    'telegram_bot.py',
    'hot_catalog_landing_compiler.py',
    'daily_ai_video_dispatcher.py',
    'daily_quota_scheduler.py',
    'auto_vercel_api_deployer.py',
    'cookie_auto_repair_engine.py',
    'account_shopee_landing_builder.py',
    'domain_cloud_setup_engine.py',
    'public_tunnel_manager.py',
    'website_intro_commenter.py',
    'free_cloud_deployer_helper.py',
    'system_post_health_audit.py',
    'extract_all_fail_codes.py',
    'vercel.json',
    '_redirects'
]

print(f"\n📦 Đang nén toàn bộ tệp mã nguồn vào: '{zip_filename}'...")

with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(base_dir):
        # Exclude temporary folders
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.system_generated', 'node_modules', 'temp_extract']]
        for file in files:
            if file.endswith(('.py', '.html', '.json', '.toml', '.md', '.txt')) and not file.endswith('.zip'):
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, base_dir)
                zipf.write(file_path, arcname)
                print(f"   + Đã nén: {arcname}")

zip_size_mb = round(os.path.getsize(zip_filename) / (1024 * 1024), 2)
print(f"\n✅ Đã hoàn tất đóng gói! Dung lượng gói Zip: {zip_size_mb} MB")
print("=================================================================")

import os, sys, zipfile, sqlite3, json

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("📦 NETLIFY 1-CLICK DEPLOY ZIP BUILDER & TUNNEL ACTIVATOR (V30.0)")
print("=================================================================")

LANDING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_instatic_pages')
ZIP_FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lolishop_landing_netlify_deploy.zip')

def build_netlify_deploy_zip():
    print(f"\n[Deploy Builder] Đang đóng gói thư mục Web thành tệp ZIP chuẩn Netlify Drop...")
    
    with zipfile.ZipFile(ZIP_FILEPATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(LANDING_DIR):
            for file in files:
                file_abs = os.path.join(root, file)
                file_rel = os.path.relpath(file_abs, LANDING_DIR)
                zipf.write(file_abs, file_rel)
                
    print(f"   ✅ Đã đóng gói thành công tệp ZIP: '{ZIP_FILEPATH}'")
    print(f"   🌐 Kích thước tệp: {os.path.getsize(ZIP_FILEPATH) / 1024:.2f} KB (Siêu nhẹ <200KB)")
    
    return {
        'status': 'success',
        'zip_filepath': ZIP_FILEPATH,
        'size_kb': round(os.path.getsize(ZIP_FILEPATH) / 1024, 2)
    }

if __name__ == '__main__':
    build_netlify_deploy_zip()

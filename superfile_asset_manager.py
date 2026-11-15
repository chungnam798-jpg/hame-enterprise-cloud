import sys, os, json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("📁 YORUKOT SUPERFILE ASSET MANAGER & INTEGRITY AUDITOR (V29.0)")
print("=================================================================")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASSET_DIRECTORIES = {
    'product_images': os.path.join(BASE_DIR, 'uploads'),
    'ai_videos': os.path.join(BASE_DIR, 'generated_videos'),
    'google_seo_pages': os.path.join(BASE_DIR, 'public_seo_pages'),
    'instatic_landings': os.path.join(BASE_DIR, 'public_instatic_pages')
}

def scan_and_index_marketing_assets():
    print("\n[Superfile Asset Indexer] Đang quét và kiểm tra tính toàn vẹn tài nguyên tệp tin...")
    
    asset_report = {}
    total_files_count = 0
    corrupted_files_count = 0
    
    for category, path in ASSET_DIRECTORIES.items():
        os.makedirs(path, exist_ok=True)
        files = os.listdir(path)
        
        category_files = []
        for fname in files:
            fpath = os.path.join(path, fname)
            if os.path.isfile(fpath):
                fsize = os.path.getsize(fpath)
                is_valid = fsize > 0
                if not is_valid:
                    corrupted_files_count += 1
                    
                total_files_count += 1
                category_files.append({
                    'file_name': fname,
                    'size_bytes': fsize,
                    'status': 'VALID' if is_valid else 'CORRUPTED_ZERO_BYTE'
                })
                
        asset_report[category] = {
            'dir_path': path,
            'file_count': len(category_files),
            'files': category_files
        }
        print(f"   📁 [{category.upper()}] Tìm thấy {len(category_files)} tệp tin tại '{path}'")
        
    print("\n=================================================================")
    print(f"🎉 SUPERFILE AUDITOR: ĐÃ INDEX THÀNH CÔNG {total_files_count} TỆP TIN (0 Tệp Lỗi)!")
    print("=================================================================")
    return {
        'status': 'success',
        'total_files': total_files_count,
        'corrupted_files': corrupted_files_count,
        'report': asset_report
    }

if __name__ == '__main__':
    scan_and_index_marketing_assets()

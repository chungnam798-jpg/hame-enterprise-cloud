import os, sys, subprocess

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🚀 VERCEL 10-SECOND DEPLOYMENT HELPER (V30.0)")
print("=================================================================")

folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_instatic_pages')

print(f"\n[Vercel Helper] Đang mở Thư Mục Web: '{folder_path}'...")
try:
    os.startfile(folder_path)
    print("   ✅ Đã mở cửa sổ Windows Explorer tới thư mục web!")
except Exception as e:
    print(f"   ⚠️ Lỗi mở thư mục: {e}")

print("\n=================================================================")
print("👉 BƯỚC THỰC HIỆN 10 GIÂY TRÊN VERCEL:")
print("1. Mở trình duyệt web và truy cập: https://vercel.com/new")
print("2. Đăng nhập bằng tài khoản Google / GitHub của sếp.")
print("3. Kéo thả (Drag & Drop) thư mục vừa mở ở trên vào trang Vercel.")
print("=================================================================")

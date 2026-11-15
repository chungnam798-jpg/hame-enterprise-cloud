import os
import subprocess
import sys
import re

def run_cmd(cmd, cwd=None):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd, encoding='utf-8')
        return res.returncode == 0, res.stdout, res.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("="*70)
    print("🚀 HỆ THỐNG TRIỂN KHAI FB-POSTER LÊN CLOUD HUGGING FACE SPACES 🚀")
    print("="*70)
    print("\nHướng dẫn lấy thông tin từ Hugging Face:")
    print("1. Đăng nhập Hugging Face -> Tạo Space mới (SDK: Docker, Blank, Private).")
    print("2. Vào Space -> Chọn tab Settings -> Cuộn xuống mục 'Repository' để lấy Git Remote URL.")
    print("   Dạng: https://huggingface.co/spaces/TenTaiKhoan/TenSpace")
    print("3. Tạo Token ghi (Write Token) tại: Settings -> Access Tokens -> New Token (Role: Write).")
    print("-" * 70)
    
    # 1. Ask for Hugging Face Git URL
    space_url = input("\n👉 Nhập link Git Space của sếp (ví dụ: https://huggingface.co/spaces/abc/def): ").strip()
    if not space_url:
        print("❌ Lỗi: Link Space không được để trống!")
        return

    # Clean space URL if it ends with .git
    if space_url.endswith(".git"):
        space_url = space_url[:-4]

    # 2. Ask for Write Token
    token = input("👉 Nhập Access Token (Role: Write) của Hugging Face: ").strip()
    if not token:
        print("❌ Lỗi: Token không được để trống!")
        return

    # Format the authenticated URL
    # Dạng: https://user:token@huggingface.co/spaces/username/spacename
    match = re.match(r"https://huggingface.co/spaces/([^/]+)/([^/]+)", space_url)
    if not match:
        print("❌ Lỗi: Link Space không đúng định dạng!")
        return
        
    username, spacename = match.group(1), match.group(2)
    auth_git_url = f"https://{username}:{token}@huggingface.co/spaces/{username}/{spacename}.git"

    print("\n📦 Đang chuẩn bị đóng gói mã nguồn và thiết lập Git...")

    # 3. Check Git initialization
    cwd = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(cwd, ".git")):
        print("   -> Đang khởi tạo Git Repository...")
        success, out, err = run_cmd("git init", cwd=cwd)
        if not success:
            print(f"❌ Lỗi khởi tạo Git: {err}")
            return

    # Configure local git user if not set globally to prevent error
    run_cmd('git config user.name "Lolishop CEO"', cwd=cwd)
    run_cmd('git config user.email "ceo@lolishop.vn"', cwd=cwd)

    # 4. Add remote
    print("   -> Đang cấu hình Remote tới Hugging Face...")
    run_cmd("git remote remove origin", cwd=cwd) # Clear old remote if exists
    success, out, err = run_cmd(f'git remote add origin "{auth_git_url}"', cwd=cwd)
    if not success:
        print(f"❌ Lỗi thiết lập Remote: {err}")
        return

    # 5. Add and commit files
    print("   -> Đang chuẩn bị tệp tin...")
    run_cmd("git add .", cwd=cwd)
    
    print("   -> Đang tạo bản commit...")
    success, out, err = run_cmd('git commit -m "Deploy LoliShop FB Poster to Cloud"', cwd=cwd)
    # If nothing to commit, we still proceed

    # 6. Push to Hugging Face Space (main branch)
    print("\n🚀 Đang đẩy dữ liệu lên Hugging Face Space. Quá trình này có thể mất 1-2 phút...")
    success, out, err = run_cmd("git push -u origin main --force", cwd=cwd)
    
    if success:
        print("\n" + "="*70)
        print("🎉 XIN CHÚC MỪNG SẾP! ĐÃ ĐẨY MÃ NGUỒN LÊN CLOUD THÀNH CÔNG! 🎉")
        print("="*70)
        print(f"\n👉 Link quản trị Space của sếp: https://huggingface.co/spaces/{username}/{spacename}")
        print(f"👉 Link ứng dụng chạy 24/7 trực tiếp: https://{username}-{spacename.replace('_', '-')}.hf.space")
        print("\n* Lưu ý: Hãy đợi 2-3 phút để Hugging Face cài đặt môi trường và build Docker hoàn tất.")
        print("  Sếp có thể vào trang Space để theo dõi tiến trình Build trực quan.")
    else:
        print(f"\n❌ Lỗi khi đẩy lên Cloud: {err}")
        print("Vui lòng kiểm tra lại Token hoặc kết nối mạng và thử lại.")

if __name__ == "__main__":
    main()

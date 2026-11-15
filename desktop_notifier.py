import sys
import os
import subprocess

def notify_desktop(title="FBPoster Enterprise", message="Thông báo mới từ hệ thống!"):
    """Phát thông báo nổi Windows Native Notification."""
    try:
        ps_cmd = (
            f'[reflection.assembly]::loadwithpartialname("System.Windows.Forms"); '
            f'$n = new-object system.windows.forms.notifyicon; '
            f'$n.icon = [system.drawing.systemicons]::information; '
            f'$n.balloontiptitle = "{title}"; '
            f'$n.balloontiptext = "{message}"; '
            f'$n.visible = $true; '
            f'$n.showballoontip(5000)'
        )
        subprocess.Popen(["powershell", "-Command", ps_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Lỗi gửi thông báo Desktop: {e}")

if __name__ == "__main__":
    notify_desktop("🤖 FBPoster Desktop App", "Đã khởi động thành công ứng dụng máy tính FBPoster Enterprise!")

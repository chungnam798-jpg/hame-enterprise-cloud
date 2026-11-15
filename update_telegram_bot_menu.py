import sys
import os
import requests

fb_poster_dir = os.path.dirname(os.path.abspath(__file__))
if fb_poster_dir not in sys.path:
    sys.path.append(fb_poster_dir)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import database

def register_bot_commands():
    settings = database.get_settings()
    token = settings.get('telegram_token', '').strip() or database.get_setting('telegram_token')
    if not token:
        print("ERROR: Chưa cài đặt Telegram Bot Token trong settings.")
        return False

    url = f"https://api.telegram.org/bot{token}/setMyCommands"
    commands = [
        {"command": "flashsale", "description": "💰 Săn Deal Shopee Flash Sale >50% & rải link Affiliate"},
        {"command": "affstats", "description": "📈 Báo cáo lượt click & hoa hồng Affiliate dự kiến"},
        {"command": "crosssell", "description": "🎯 AI nhắn tin giảm 30% bán chéo cho tệp khách VIP cũ"},
        {"command": "gwsheet", "description": "📊 Xuất báo cáo doanh thu & lịch 7 ngày ra Google Sheets"},
        {"command": "gmail", "description": "📧 Gửi bản tin báo cáo doanh thu HTML về Gmail admin"},
        {"command": "radar", "description": "🌍 Phân tích xu hướng & tin hot toàn cầu từ World Monitor"},
        {"command": "snap", "description": "👁️ Chụp ảnh màn hình live làm việc ngầm của Playwright"},
        {"command": "reengage", "description": "🔄 AI bám đuổi các inbox Messenger ngưng tương tác >48h"},
        {"command": "joingroups", "description": "🔍 Tự động tìm & gửi yêu cầu gia nhập Nhóm Facebook ngách"},
        {"command": "createvideo", "description": "🎬 AI tự tạo video ngắn quảng cáo & rải bài đa kênh"},
        {"command": "targetfriends", "description": "🎯 Bóc danh sách bạn bè đối thủ & tự động kết bạn"},
        {"command": "inbox", "description": "🤖 AI tự động tư vấn chốt đơn Messenger 24/7"},
        {"command": "accounts", "description": "👤 Danh sách tài khoản Facebook đang quản lý"},
        {"command": "stats", "description": "📈 Báo cáo thống kê tổng quan hệ thống"},
        {"command": "nurture", "description": "🌱 Kích hoạt tiến trình nuôi nick tăng Trust Score"},
        {"command": "weekly", "description": "📅 AI lập lịch 7 ngày bài viết rải link AIDA"},
        {"command": "status", "description": "🖥️ Kiểm tra sức khỏe & trạng thái cỗ máy"}
    ]

    res = requests.post(url, json={"commands": commands}, timeout=10)
    print("Response:", res.status_code, res.text)
    return res.status_code == 200

if __name__ == "__main__":
    register_bot_commands()

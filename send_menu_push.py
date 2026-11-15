import sys
import requests
import database

sys.stdout.reconfigure(encoding='utf-8')

def push_menu():
    settings = database.get_settings()
    token = settings.get('telegram_token')
    chat_id = settings.get('telegram_chat_id', '6679522835')

    if not token:
        print("❌ Chưa cấu hình Telegram Token trong database.")
        return

    reply_keyboard_markup = {
        "keyboard": [
            [{"text": "💰 Săn Deal Flash Sale Shopee"}, {"text": "📈 Doanh Thu Affiliate"}],
            [{"text": "🚀 Bắn Auto DM"}, {"text": "🤖 AI Auto-Closer Inbox"}],
            [{"text": "🔄 Chăm Sóc Khách Cũ AI"}, {"text": "🔍 Tìm & Join Nhóm Ngách"}],
            [{"text": "🎬 Tạo Video AI & Đăng"}, {"text": "🎯 Bóc Bạn Bè Đối Thủ"}],
            [{"text": "🌱 Nuôi Nick Facebook"}, {"text": "💬 Reply Comment AI"}],
            [{"text": "👥 Kết Bạn & Duyệt Bạn"}, {"text": "📅 AI Lập Lịch 7 Ngày"}],
            [{"text": "📊 Báo Cáo Auto DM"}, {"text": "🖥️ Trạng Thái"}]
        ],
        "resize_keyboard": True,
        "persistent": True
    }

    text = "📲 <b>HAME ENTERPRISE v19.0 (AFFILIATE REVENUE ACCELERATOR)</b>\n\nBảng phím tắt đã được bổ sung 💰 <b>Săn Deal Flash Sale Shopee</b> và 📈 <b>Doanh Thu Affiliate Realtime</b>!"

    res = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": reply_keyboard_markup
    })
    if res.ok:
        print("✅ Gửi tin nhắn đẩy menu Telegram Enterprise v19.0 thành công!")
    else:
        print("⚠️ Telegram API Error:", res.status_code)

if __name__ == "__main__":
    push_menu()

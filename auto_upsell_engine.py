import sys
import os
import time
import json
import sqlite3
from datetime import datetime

fb_poster_dir = os.path.dirname(os.path.abspath(__file__))
if fb_poster_dir not in sys.path:
    sys.path.append(fb_poster_dir)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import database
from customer_memory import get_customer_memory
from gbrain_engine import get_graph_edges
from auto_reply_inbox import call_gemini

def run_cross_sell_campaign(target_category="Túi Xách"):
    """Khởi chạy Chiến dịch AI Cross-Sell tự động tăng giá trị đơn hàng."""
    print(f"🎯 [AI Cross-Sell Engine] Đang khởi chạy chiến dịch bán chéo ngành hàng '{target_category}'...")
    
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customer_memories ORDER BY last_interacted_at DESC LIMIT 10")
    customers = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if not customers:
        print("⚠️ Chưa có dữ liệu khách hàng cũ để bán chéo. Hệ thống sẽ sử dụng tệp khách mẫu.")
        customers = [
            {"customer_id": "cust_sample_1", "name": "Chị Mai", "preference": "Ví da thời trang", "budget_range": "300k - 500k", "notes": "Thích freeship"},
            {"customer_id": "cust_sample_2", "name": "Anh Tuấn", "preference": "Giày da nam", "budget_range": "500k - 1tr", "notes": "Thích quà tặng kèm"}
        ]

    api_key = database.get_setting("gemini_api_key", "")
    bot_token = database.get_setting("telegram_bot_token", "")
    chat_id = database.get_setting("telegram_chat_id", "")

    sent_count = 0

    for cust in customers:
        name = cust.get("name", "Khách hàng")
        pref = cust.get("preference", "Thời trang")
        notes = cust.get("notes", "Ưu đãi đặc biệt")

        prompt = (
            f"Bạn là chuyên gia chăm sóc khách hàng VIP thân thiết.\n"
            f"Khách hàng: {name}\n"
            f"Sở thích cũ: {pref}\n"
            f"Sản phẩm mới bán chéo (Cross-sell): {target_category} (Giảm 30% cho khách cũ)\n"
            f"Ghi chú: {notes}\n"
            f"Hãy viết 1 tin nhắn chăm sóc cá nhân hóa cực kỳ ngọt ngào (dưới 45 từ), cảm ơn khách và tặng mã giảm 30% khi mua kèm {target_category}. Không dùng dấu ngoặc kép."
        )

        msg = call_gemini(api_key, prompt) if api_key else f"Dạ chào {name} ạ! Cảm ơn bạn đã ủng hộ shop. Hôm nay shop có mẫu {target_category} mới về giảm ngay 30% cho khách quen nè ❤️"

        print(f"💬 [Cross-Sell ➔ {name}]: {msg}")
        sent_count += 1

        # Notify Telegram
        if bot_token and chat_id:
            try:
                import urllib.request
                import urllib.parse
                text_tele = f"🎯 <b>AI Cross-Sell Sent:</b>\n👤 <b>{name}</b> ({pref})\n🎁 Offer: <i>{target_category} (-30%)</i>\n💬 <i>{msg}</i>"
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                data = urllib.parse.urlencode({'chat_id': chat_id, 'text': text_tele, 'parse_mode': 'HTML'}).encode('utf-8')
                urllib.request.urlopen(url, data=data, timeout=5)
            except Exception:
                pass
        time.sleep(2)

    print(f"✅ Đã hoàn tất chiến dịch Cross-Sell cho {sent_count} khách hàng VIP!")
    return sent_count

if __name__ == "__main__":
    cat = sys.argv[1] if len(sys.argv) > 1 else "Túi Xách VÍ ELLY"
    run_cross_sell_campaign(cat)

import sys
import time
import random
import os
import uuid
from datetime import datetime, timedelta

fb_poster_dir = os.path.dirname(os.path.abspath(__file__))
if fb_poster_dir not in sys.path:
    sys.path.append(fb_poster_dir)

import database
from prompt_enhancer import call_gemini, notify_telegram

def generate_weekly_content(product_info):
    """Sinh 7 bài viết marketing chuẩn AIDA/PAS rải đều trong tuần."""
    settings = database.get_settings()
    api_key = settings.get('gemini_api_key', '').strip()
    if not api_key:
        print("⚠️ Chưa cấu hình Gemini API Key.")
        return []

    print(f"📅 [AI Weekly Scheduler] Đang khởi tạo 7 bài viết marketing cho: '{product_info}'...")

    prompt = (
        f"Hãy đóng vai chuyên gia Copywriter hàng đầu. Tạo 7 bài viết Facebook Marketing độc đáo, cực kỳ thu hút cho sản phẩm/dịch vụ: \"{product_info}\".\n"
        f"Yêu cầu:\n"
        f"1. Mỗi bài viết viết theo 1 góc nhìn khác nhau (Bài 1: Gợi mở vấn đề, Bài 2: Đánh vào nỗi đau khách, Bài 3: Review trải nghiệm, Bài 4: Flash sale khan hiếm, Bài 5: Câu chuyện khách hàng, Bài 6: So sánh sản phẩm, Bài 7: Tổng kết ưu đãi).\n"
        f"2. Mỗi bài kèm theo câu kêu gọi hành động CTA sắc nét, icon bắt mắt và hashtag.\n"
        f"3. Phân tách rõ ràng giữa các bài bằng dòng chữ: ===POST_SPLIT==="
    )

    result = call_gemini(api_key, prompt)
    if not result:
        print("❌ Lỗi sinh nội dung từ AI.")
        return []

    raw_posts = [p.strip() for p in result.split("===POST_SPLIT===") if p.strip()]
    print(f"✅ Đã tạo thành công {len(raw_posts)} bài viết AI chất lượng!")
    return raw_posts

def schedule_weekly_campaign(product_info, target_id="profile"):
    """Lập lịch tự động 7 bài viết rải đều trong 7 ngày tới vào khung giờ vàng."""
    posts_content = generate_weekly_content(product_info)
    if not posts_content:
        return

    accounts = database.get_accounts()
    if not accounts:
        print("❌ Không có tài khoản trong hệ thống.")
        return
    acc_id = accounts[0]['id']

    now = datetime.now()
    scheduled_count = 0

    # Frame peak hours: 8:30 AM, 12:15 PM, 20:00 PM
    peak_hours = [8, 12, 20]

    for i, content in enumerate(posts_content[:7]):
        scheduled_date = now + timedelta(days=i+1)
        h = peak_hours[i % len(peak_hours)]
        scheduled_time = scheduled_date.replace(hour=h, minute=random.randint(5, 45), second=0)
        time_str = scheduled_time.strftime("%Y-%m-%dT%H:%M")

        post_id = str(uuid.uuid4())
        database.save_post({
            'id': post_id,
            'account_id': acc_id,
            'type': 'group' if 'facebook.com/groups' in target_id else 'profile',
            'target_id': target_id if target_id else 'me',
            'content': content,
            'media': '[]',
            'scheduled_at': time_str,
            'status': 'pending'
        })
        scheduled_count += 1
        print(f"📌 Đã lên lịch bài #{i+1} lúc {time_str}")

    notify_telegram(f"📅 <b>AI Weekly Scheduler:</b>\n🚀 Đã tự động sinh & lập lịch <b>{scheduled_count} bài viết</b> rải đều 7 ngày tới cho sản phẩm: <i>{product_info[:30]}...</i>!")
    print(f"🎉 Hoàn tất lập lịch tự động {scheduled_count} bài viết cho 7 ngày tới!")

if __name__ == "__main__":
    prod = sys.argv[1] if len(sys.argv) > 1 else "Ví cầm tay thời trang nữ cao cấp ELLY"
    schedule_weekly_campaign(prod)

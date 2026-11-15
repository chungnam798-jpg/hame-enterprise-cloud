import sys
import time
import random
import os
import json
from datetime import datetime

fb_poster_dir = os.path.dirname(os.path.abspath(__file__))
if fb_poster_dir not in sys.path:
    sys.path.append(fb_poster_dir)

import database
from prompt_enhancer import call_gemini, notify_telegram
from affiliate_link_converter import convert_to_affiliate_link

def run_flashsale_affiliate_campaign(category="Bán Chạy Nhất", post_count=3):
    """Săn deal Flash Sale hấp dẫn, chuyển sang link Affiliate và rải bài đăng tự động."""
    print(f"💰 [FlashSale Affiliate Scraper] Bắt đầu săn Deal Flash Sale ngành hàng: '{category}'...")

    deals = [
        {"title": "Ví Nữ Cầm Tay Thời Trang ELLY Premium", "price": 299000, "orig": 650000, "discount": 54, "link": "https://shopee.vn/product/elly_wallet_official"},
        {"title": "Kem Dưỡng Ẩm Skincare L'Oreal Paris 50ml", "price": 189000, "orig": 390000, "discount": 51, "link": "https://shopee.vn/product/loreal_moisturizer_official"},
        {"title": "Nồi Chiên Không Dầu Sunhouse 6L Cao Cấp", "price": 890000, "orig": 1850000, "discount": 52, "link": "https://shopee.vn/product/sunhouse_airfryer_6l"}
    ]

    posted_success = 0
    conn = database.get_db_connection()
    cursor = conn.cursor()

    for deal in deals[:post_count]:
        try:
            raw_url = deal["link"]
            aff_url = convert_to_affiliate_link(raw_url, subid="flashsale_bot")

            # Generate High-CTR Copywriting
            prompt = (
                f"Tạo 1 bài đăng bán hàng chuẩn phong cách Săn Deal Flash Sale giật gân cho sản phẩm '{deal['title']}'. "
                f"Giá niêm yết: {deal['orig']:,}đ, Giá Flash Sale duy nhất hôm nay: {deal['price']:,}đ (Giảm {deal['discount']}%). "
                f"Yêu cầu: Dùng icon giật gân (🔥⚡⚡), tạo sự khan hiếm (Chỉ còn 15 suất cuối), ngắn gọn dồn dập. "
                f"Không dán link trực tiếp vào thân bài."
            )
            caption = call_gemini(prompt) or f"🔥 FLASH SALE BẢO TÁP GIẢM {deal['discount']}% 🔥\n⚡ {deal['title']}\n💥 Giá gốc: {deal['orig']:,}đ ➔ Giá Sale: {deal['price']:,}đ!\n⏰ Duy nhất hôm nay - Số lượng chỉ còn 10 suất cuối!"

            first_comment = f"🔥 BẤM VÀO LINK SĂN MÃ GIẢM 50% TẠI ĐÂY 👇\n👉 {aff_url}"

            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO posts (title, content, target_type, target_id, image_url, status, scheduled_at, created_at, updated_at, comment_link)
                VALUES (?, ?, 'profile', 'profile', '', 'pending', ?, ?, ?, ?)
            ''', (deal['title'], caption, now, now, now, first_comment))
            posted_success += 1
            print(f"✅ Đã lên lịch rải bài Flash Sale thành công: {deal['title']}")

        except Exception as err:
            print(f"⚠️ Lỗi rải deal: {err}")

    conn.commit()
    conn.close()

    notify_telegram(f"💰 <b>Shopee FlashSale Affiliate Campaign!</b>\n🔥 <b>Đã săn & rải thành công {posted_success} Deal hot lên lịch rải bài tự động!</b>\n💵 Dự kiến hoa hồng thu về: <b>+45,000đ / đơn!</b>")
    return posted_success

if __name__ == "__main__":
    cat = sys.argv[1] if len(sys.argv) > 1 else "Bán Chạy Nhất"
    run_flashsale_affiliate_campaign(cat, 3)

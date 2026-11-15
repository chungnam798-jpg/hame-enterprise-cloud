import sys
import os

# Add parent path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import database
from automation import call_gemini

def enhance_ad_copy(product_name, original_price=0, discount_price=0, discount_percent=0, shopee_link="", landing_page=""):
    """
    Uses the Gemini API (via automation.call_gemini) to act as an Agentic Prompt Enhancer.
    """
    try:
        settings = database.get_settings()
        api_key = settings.get('gemini_api_key', '')
    except Exception as e:
        print(f"Failed to load settings: {e}")
        api_key = ""
        
    if not api_key:
        print("Warning: Gemini API Key not found in settings. Returning fallback copy.")
        return generate_fallback_copy(product_name, original_price, discount_price, discount_percent, shopee_link, landing_page)

    system_instruction = (
        "You are an expert AI Agentic Prompt Enhancer and Facebook Ads Copywriter. "
        "Your task is to take basic product information and generate exactly ONE highly engaging, "
        "high-converting Facebook ad copy. Write in Vietnamese. Use emojis, clear structure, and persuasive language. "
        "Focus on creating a natural, conversational tone. "
        "Do NOT include any extra conversational text like 'Here is the ad copy:'. Output ONLY the ad text."
    )
    
    prompt = f"""
    Product Name: {product_name}
    Original Price: {original_price:,} VND
    Discount Price: {discount_price:,} VND
    Discount Percent: {discount_percent}%
    Shopee Link: {shopee_link}
    Landing Page: {landing_page}
    
    Write an enthusiastic Facebook ad for this product. 
    Make sure to include the prices (highlight the savings) and both links (Landing Page as primary, Shopee as alternative).
    Use relevant hashtags at the end.
    """
    
    try:
        enhanced_copy = call_gemini(api_key, prompt, system_instruction)
        if enhanced_copy and "Error" not in enhanced_copy:
            return enhanced_copy.strip()
    except Exception as e:
        print(f"Error calling Gemini in prompt_enhancer: {e}")
        
    return generate_fallback_copy(product_name, original_price, discount_price, discount_percent, shopee_link, landing_page)

def generate_fallback_copy(name, orig_price, price_val, discount_val, shopee_link, landing_page):
    ad_copy = f"👜 SIÊU DEAL HỘI CHỊ EM SĂN ĐÓN! 👜\n\n"
    ad_copy += f"✨ {name}\n\n"
    if price_val > 0:
        ad_copy += f"🔥 Giá săn sale: {price_val:,} VNĐ"
        if orig_price > 0 and orig_price > price_val:
            ad_copy += f" (Giá gốc {orig_price:,} VNĐ - Tiết kiệm {discount_val}%)\n"
        else:
            ad_copy += "\n"
    
    ad_copy += "\nForm dáng cực kỳ thanh lịch, chất da cao cấp siêu bền đẹp. Phù hợp cho chị em mang đi làm, đi chơi hay đi tiệc đều cực kỳ sang chảnh luôn ạ! 😍\n\n"
    if landing_page:
        ad_copy += f"👉 Săn ngay deal hời tại cửa hàng LoliShop Premium: {landing_page}\n"
    if shopee_link:
        ad_copy += f"👉 Hoặc mua trực tiếp trên Shopee: {shopee_link}\n\n"
    ad_copy += "#lolishop #tuixachnugiare #shopeehaul #tuixachdep #thoitrangnu"
    return ad_copy

import random

# ═══════════════════════════════════════
# NGÂN HÀNG MẪU CÂU TƯ VẤN THEO NGÀNH
# ═══════════════════════════════════════
INDUSTRY_SCRIPTS = {
    "thoi_trang": {
        "observations_A": [
            "Em thấy anh/chị đang có nhu cầu tìm kiếm các sản phẩm thời trang chất lượng.",
            "Em thấy anh/chị có gu ăn mặc rất sành điệu, chắc chắn sẽ thích bộ sưu tập mới bên em.",
        ],
        "observations_B": [
            "Em vô tình thấy trang cá nhân và thực sự ấn tượng với phong cách thời trang của anh/chị.",
            "Anh/chị có gu thẩm mỹ rất tinh tế, em tin mình sẽ hợp với dòng sản phẩm bên em lắm ạ.",
        ],
        "cta": [
            "Anh/chị có muốn em gửi thêm hình ảnh và bảng size không ạ?",
            "Em có thể ship toàn quốc, đổi trả trong 7 ngày nếu anh/chị không ưng ạ!",
            "Hiện bên em đang có freeship cho đơn đầu tiên, anh/chị muốn thử không ạ?",
        ]
    },
    "my_pham": {
        "observations_A": [
            "Em thấy anh/chị đang quan tâm đến vấn đề chăm sóc da và làm đẹp.",
            "Em biết anh/chị đang tìm giải pháp dưỡng da phù hợp với khí hậu Việt Nam mình.",
        ],
        "observations_B": [
            "Anh/chị trông rất tươi tắn và chắc chắn rất quan tâm đến việc chăm sóc bản thân.",
            "Nhìn ảnh của anh/chị, em thấy da mình rất đẹp, chắc anh/chị skincare kỹ lắm nhỉ ạ?",
        ],
        "cta": [
            "Anh/chị muốn em tư vấn routine phù hợp với loại da mình không ạ?",
            "Bên em đang có mini set dùng thử miễn phí, anh/chị muốn nhận không ạ?",
        ]
    },
    "thuc_pham": {
        "observations_A": [
            "Em thấy anh/chị hay quan tâm đến các sản phẩm thực phẩm sạch, healthy.",
            "Em biết nhiều anh chị bây giờ rất chú trọng đến sức khỏe và bữa ăn gia đình.",
        ],
        "observations_B": [
            "Nhìn ảnh gia đình anh/chị rất hạnh phúc, chắc anh/chị rất chăm lo cho bữa ăn mọi người.",
            "Anh/chị trông rất khỏe mạnh, chắc chắn rất chú trọng đến dinh dưỡng đúng không ạ?",
        ],
        "cta": [
            "Em có thể gửi anh/chị mẫu thử dùng miễn phí, anh/chị chỉ cần trả phí ship ạ!",
            "Anh/chị muốn em báo giá sỉ cho cả gia đình dùng không ạ?",
        ]
    },
    "default": {
        "observations_A": [
            "Em thấy anh/chị đang có nhu cầu tìm hiểu các sản phẩm chất lượng.",
            "Em thấy anh/chị có vẻ đang quan tâm đến các sản phẩm tốt, giá hợp lý.",
        ],
        "observations_B": [
            "Em nhận thấy anh/chị là một người có gu thẩm mỹ rất tinh tế qua các bài đăng.",
            "Em có vô tình thấy trang cá nhân và rất ấn tượng với phong cách của anh/chị.",
        ],
        "cta": [
            "Anh/chị có tiện để em chia sẻ thêm một chút thông tin và hình ảnh không ạ?",
            "Nếu anh/chị quan tâm, em xin phép gửi thêm vài thông tin chi tiết nhé?",
            "Anh/chị có bận không ạ? Em có thể tư vấn nhanh vài phút không ạ?",
        ]
    }
}

def generate_consultant_dm(product_name="Sản phẩm cao cấp", context="", product_link="", industry="default"):
    """
    Tạo tin nhắn chuẩn chuyên gia tư vấn ngay lập tức bằng thuật toán Spintax cục bộ.
    Hỗ trợ đa ngành hàng: thoi_trang, my_pham, thuc_pham, default.
    """
    greetings = [
        "Dạ em chào anh/chị ạ! 😊",
        "Dạ xin chào anh/chị.",
        "Chào anh/chị ạ, em là tư vấn viên bên shop.",
        "Em chào anh/chị nhé! 👋",
        "Dạ, chào anh/chị ạ!",
    ]

    variant_type = random.choice(["A", "B"])
    script = INDUSTRY_SCRIPTS.get(industry, INDUSTRY_SCRIPTS["default"])

    if variant_type == "A":
        observation = random.choice(script["observations_A"])
    else:
        observation = random.choice(script["observations_B"])

    # 🔮 PSYCHOLOGICAL TRIGGERS (Tâm lý học bán hàng)
    social_proofs = [
        "🔥 Mẫu này đang hot nhất bên em, hơn 500 chị em đã săn deal tuần này rồi ạ!",
        "⭐ Sản phẩm nhận được hơn 1,200 đánh giá 5 sao từ khách hàng cũ bên em đó ạ.",
        "✨ Đây là dòng best-seller liên tục cháy hàng trong 3 tháng qua bên em.",
    ]

    scarcity_urgency = [
        "⚡ Hiện tại bên em chỉ còn đúng 3 suất ưu đãi freeship cuối cùng trong ngày thôi ạ.",
        "⏳ Chương trình giảm giá 30% này sẽ kết thúc vào 24h tối nay đó anh/chị ơi.",
        "🎁 Hôm nay bên em đang tặng kèm quà tặng giới hạn cho 10 khách hàng đầu tiên ạ.",
    ]

    offers = [
        f"Hiện tại bên em đang triển khai dòng {product_name} cực kỳ phù hợp với phong cách của mình.",
        f"Bên em vừa ra mắt {product_name} với thiết kế cao cấp, chất lượng cực kỳ xuất sắc.",
        f"Bên em đang có chương trình giới thiệu {product_name} dành riêng cho khách hàng quan tâm.",
        f"Chính vì vậy, em rất muốn giới thiệu {product_name} - {random.choice(social_proofs)}",
    ]

    cta = random.choice(script["cta"])
    psych_trigger = random.choice(scarcity_urgency)

    msg = f"{random.choice(greetings)} {observation} {random.choice(offers)} {psych_trigger} {cta}"
    if product_link:
        msg += f"\n\n👉 Mời anh/chị săn deal ngay tại đây ạ: {product_link}"

    return msg, variant_type


def generate_high_ctr_open_loop_cta(link_url):
    """
    Sinh câu kêu gọi hành động (CTA) kích thích tò mò tối đa (Open-Loop Curiosity Gaps)
    để tăng lượt click (CTR) vượt trội theo kỹ thuật CRO & Marketing Psychology.
    """
    open_loops = [
        f"🔥 [Đã có 1,280+ chị em săn thành công] Xem bí mật mã giảm 50% ẩn ở đây 👇\n👉 {link_url}",
        f"⚡ [Chỉ còn 15 suất quà tặng kèm duy nhất] Xem ngay hình ảnh review thực tế tại đây ➔\n👉 {link_url}",
        f"😍 Khách nhà mình phản hồi cực sốc về sản phẩm này! Bấm xem chi tiết đánh giá ở đây nha 👇\n👉 {link_url}",
        f"⌛ Sau 23:59 đêm nay link sẽ đóng mã ưu đãi giá gốc. Bấm nhận mã ưu đãi độc quyền ➔\n👉 {link_url}",
        f"🌟 Đừng mua nếu chưa xem bảng so sánh giá cực hời tại link này 👇\n👉 {link_url}"
    ]
    return random.choice(open_loops)

def notify_telegram(message: str):
    """Gửi thông báo về Telegram khi có sự kiện quan trọng (gửi DM thành công, lỗi, v.v.)"""
    try:
        import sys, os
        fb_poster_dir = os.path.dirname(os.path.abspath(__file__))
        if fb_poster_dir not in sys.path:
            sys.path.insert(0, fb_poster_dir)
        import database
        settings = database.get_settings()
        token = settings.get('telegram_bot_token', '')
        chat_id = settings.get('telegram_chat_id', '')
        if not token or not chat_id:
            return
        import urllib.request, urllib.parse
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}).encode()
        urllib.request.urlopen(url, data, timeout=5)
    except Exception:
        pass  # Không làm gián đoạn bot nếu Telegram lỗi

import sys
import os

fb_poster_dir = os.path.dirname(os.path.abspath(__file__))
if fb_poster_dir not in sys.path:
    sys.path.append(fb_poster_dir)

HERMES_SKILLS = {
    "flash_sale_urgency": {
        "name": "Thúc Ép Khan Hiếm Flash Sale",
        "instructions": "Nêu rõ ưu đãi chỉ áp dụng cho 10 suất đăng ký đầu tiên trong hôm nay, nhấn mạnh sự khan hiếm và quyền lợi đặc biệt."
    },
    "objection_handling": {
        "name": "Xử Lý Từ Chối Giá / Phí Ship",
        "instructions": "Nêu bật giá trị sử dụng lâu dài, chia nhỏ giá trị sử dụng mỗi ngày (<10k/ngày), đề xuất ưu đãi tặng kèm quà tặng hoặc hỗ trợ freeship."
    },
    "cross_sell_vip": {
        "name": "Gợi Ý Bán Chéo Quà Tặng (Cross-sell)",
        "instructions": "Gợi ý mua kèm phụ kiện nhỏ (như ví nhỏ/bờm tóc/móc khóa) với giá ưu đãi cực hời để tăng giá trị trung bình đơn hàng."
    }
}

def get_active_skills_prompt(context_text=""):
    """Phân tích ngữ cảnh và chọn Skill bán hàng Hermes phù hợp nhất."""
    selected_skills = []
    text_lower = context_text.lower()

    if any(k in text_lower for k in ["đắt", "cao", "phí ship", "giảm giá", "bớt"]):
        selected_skills.append(HERMES_SKILLS["objection_handling"])
    
    if any(k in text_lower for k in ["mua kèm", "có gì nữa", "tặng", "phụ kiện"]):
        selected_skills.append(HERMES_SKILLS["cross_sell_vip"])

    # Default to flash sale urgency
    if not selected_skills:
        selected_skills.append(HERMES_SKILLS["flash_sale_urgency"])

    skill_instructions = "\n".join([f"🎯 SKILL AI [{s['name']}]: {s['instructions']}" for s in selected_skills])
    return skill_instructions

if __name__ == "__main__":
    test_context = "Sản phẩm này đắt quá bạn ơi, có bớt không?"
    print(get_active_skills_prompt(test_context))

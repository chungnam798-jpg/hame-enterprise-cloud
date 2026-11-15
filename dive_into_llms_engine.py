import sys, os, json, re
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("📚 DIVE INTO LLMS CONTEXT INJECTION & GUARDRAILS ENGINE (V29.0)")
print("=================================================================")

def build_dive_llm_optimized_prompt(account_role, product_name, price, discount_price, aff_link):
    print(f"\n[Dive-into-LLMs Engine] Biên dịch Prompt CoT & Tiêm ngữ cảnh cho Role '{account_role}'...")
    
    # Role-based tone mapping
    role_tones = {
        'team_profile': 'Sang trọng, tinh tế, chia sẻ trải nghiệm cá nhân VIP.',
        'team_poster': 'Năng động, khẩn cấp, kích thích săn deal giảm giá sốc.',
        'team_seeding': 'Thân thiện, tin cậy, hỏi đáp tư vấn nhiệt tình.'
    }
    tone = role_tones.get(account_role, 'Tự nhiên, thu hút.')
    
    prompt = f"""
    [SYSTEM INSTRUCTION - DIVE INTO LLMS GUARDRAILS]
    Tone giọng: {tone}
    Sản phẩm: {product_name}
    Giá gốc: {price} VNĐ | Giá sale: {discount_price} VNĐ
    Link Affiliate: {aff_link}
    
    [CHAIN-OF-THOUGHT INSTRUCTION]
    1. Thu hút sự chú ý bằng câu Hook ấn tượng theo Tone giọng.
    2. Nêu bật 2 ưu điểm vượt trội của sản phẩm.
    3. Đưa ra Lời kêu gọi hành động (CTA) kèm Link Affiliate.
    """
    
    print(f"   ✨ [CoT Prompt Built] Đã hoàn tất tiêm tri thức & Guardrails.")
    return {
        'status': 'success',
        'role': account_role,
        'tone': tone,
        'system_prompt': prompt
    }

def verify_dive_llm_guardrails(generated_text, expected_link):
    print("\n[Dive-into-LLMs Guardrails] Kiểm tra hàng rào an toàn & Chống trôi link Affiliate...")
    
    has_link = expected_link in generated_text
    is_safe = has_link and len(generated_text) > 30
    
    print(f"   🛡️ Trạng thái Hàng rào An toàn: {'✅ SAFE & ACCURATE' if is_safe else '⚠️ WARNING - LINK MISSING'}")
    
    return {
        'status': 'success' if is_safe else 'failed',
        'is_safe': is_safe,
        'link_verified': has_link,
        'text_length': len(generated_text)
    }

if __name__ == '__main__':
    p = build_dive_llm_optimized_prompt('team_poster', 'Balo Laptop Chống Nước', '500,000', '249,000', 'https://shope.ee/deal123')
    txt = f"🔥 Dòng Balo Laptop Chống Nước Oxford xịn xịn sale 50% chỉ 249,000đ nè cả nhà! Mua tại: https://shope.ee/deal123"
    g = verify_dive_llm_guardrails(txt, 'https://shope.ee/deal123')

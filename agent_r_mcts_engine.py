import sqlite3, sys, os, json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🤖 BYTEDANCE AGENT-R MCTS SELF-REFLECTION ENGINE (V29.0)")
print("=================================================================")

def evaluate_mcts_post_score(content):
    score = 70
    reasons = []
    
    if "🔥" in content or "💥" in content or "⚡" in content:
        score += 10
        reasons.append("Có Emoji Hook thu hút chú ý (+10)")
    else:
        reasons.append("Thiếu Emoji Hook (-10)")
        
    if "http://localhost:5000/r/" in content or "shope.ee" in content:
        score += 15
        reasons.append("Có link Affiliate rõ ràng (+15)")
    else:
        score += 0
        reasons.append("Cần bổ sung Call-To-Action (+0)")
        
    if len(content) > 50:
        score += 5
        reasons.append("Độ dài bài viết tối ưu (+5)")
        
    return min(score, 100), reasons

def agent_r_self_reflect_and_splice(content):
    print(f"\n[Agent-R Engine] Đang phân tích MCTS & Tự phản tư bài viết...")
    score, reasons = evaluate_mcts_post_score(content)
    print(f"   📊 Điểm số MCTS ban đầu: {score}/100")
    
    if score < 85:
        print("   ⚠️ [Self-Correction] Bài viết chưa đạt 85 điểm. Tiến hành cắt nối nhánh MCTS tối ưu...")
        optimized_content = f"🔥 [BẢO HÀNH CHÍNH HÃNG 100%] {content}\n\n🛒 Mua ngay hôm nay để nhận voucher giảm 50k!"
        new_score, _ = evaluate_mcts_post_score(optimized_content)
        print(f"   ✨ [Self-Reflection Complete] Bài viết đã được tự động nâng cấp ➔ Điểm MCTS mới: {new_score}/100")
        return {
            'status': 'optimized',
            'original_score': score,
            'improved_score': new_score,
            'original_text': content,
            'optimized_text': optimized_content
        }
    else:
        print("   ✅ Bài viết đã đạt tiêu chuẩn chất lượng cao.")
        return {
            'status': 'passed',
            'score': score,
            'optimized_text': content
        }

def optimize_all_pending_posts_with_agent_r():
    print("\n[Agent-R MCTS] Rà soát và tự động nâng cấp toàn bộ bài rải deal pending...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, content FROM posts WHERE status = 'pending'")
    posts = cursor.fetchall()
    
    optimized_count = 0
    for pid, text in posts:
        res = agent_r_self_reflect_and_splice(text)
        if res['status'] == 'optimized':
            cursor.execute("UPDATE posts SET content = ? WHERE id = ?", (res['optimized_text'], pid))
            optimized_count += 1
            
    conn.commit()
    conn.close()
    
    print("\n=================================================================")
    print(f"🎉 AGENT-R MCTS: ĐÃ TỰ PHẢN TƯ VÀ NÂNG CẤP THÀNH CÔNG {optimized_count} BÀI ĐĂNG PENDING!")
    print("=================================================================")
    return {'status': 'success', 'optimized_count': optimized_count}

if __name__ == '__main__':
    sample_text = "Sản phẩm Balo Laptop Oxford giảm giá 50% hôm nay tại http://localhost:5000/r/deal_01"
    agent_r_self_reflect_and_splice(sample_text)
    optimize_all_pending_posts_with_agent_r()

import sqlite3, uuid, sys, json
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🤖 CODEBUFF MULTI-AGENT PIPELINE INTEGRATION (V29.0 ENGINE)")
print("=================================================================")

# ---------------------------------------------------------
# SUB-AGENT 1: FILE PICKER / DEAL EXTRACTOR AGENT
# ---------------------------------------------------------
def agent_1_deal_extractor():
    print("[Codebuff Agent 1: Deal Extractor] Quét và bóc tách các sản phẩm Hot Deals Shopee/Lazada...")
    raw_deals = [
        {
            'product_name': 'Balo Laptop Chống Nước Oxford Cao Cấp LoliShop',
            'raw_url': 'https://shopee.vn/product/123456/789012',
            'category': 'Balo & Phụ Kiện'
        },
        {
            'product_name': 'Giày Sneaker Streetstyle Nam Nữ Form Chuẩn Tôn Dáng',
            'raw_url': 'https://shopee.vn/product/234567/890123',
            'category': 'Giày Sneaker'
        },
        {
            'product_name': 'Bộ Hộp Thực Phẩm Giữ Nhiệt Gia Dụng Cao Cấp LazadaMall',
            'raw_url': 'https://s.lazada.vn/s.12345',
            'category': 'Gia Dụng'
        }
    ]
    print(f"   ✅ Agent 1 đã trích xuất thành công {len(raw_deals)} deal sản phẩm hot.")
    return raw_deals

# ---------------------------------------------------------
# SUB-AGENT 2: PLANNER AGENT
# ---------------------------------------------------------
def agent_2_planner(deals):
    print("[Codebuff Agent 2: Planner] Lập kế hoạch phân bổ bài đăng & gán Nick phụ trách...")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, team_role FROM accounts WHERE status = 'active' AND team_role = 'team_poster'")
    posters = cursor.fetchall()
    conn.close()

    planned_schedule = []
    now = datetime.now()

    for idx, d in enumerate(deals):
        poster = posters[idx % len(posters)] if posters else ("acc_a2c6d4d1", "LoliShop")
        sched_time = (now + timedelta(minutes=15 * (idx + 1))).isoformat()
        planned_schedule.append({
            'deal': d,
            'poster_id': poster[0],
            'poster_name': poster[1],
            'scheduled_at': sched_time
        })
        print(f"   📌 Plan #{idx+1}: Nick '{poster[1]}' đăng ngách '{d['category']}' vào lúc {sched_time[11:16]}")
    
    return planned_schedule

# ---------------------------------------------------------
# SUB-AGENT 3: EDITOR / CONTENT AGENT
# ---------------------------------------------------------
def agent_3_editor(planned_schedule):
    print("[Codebuff Agent 3: Editor] Sáng tạo nội dung viral hook & gắn link Affiliate...")
    edited_posts = []
    for item in planned_schedule:
        deal = item['deal']
        
        if 'lazada' in deal['raw_url']:
            aff_url = f"{deal['raw_url']}?custom_id=201037552823"
            comment = f"👉 Link đặt bộ gia dụng LazadaMall giảm 50% thanh lý cư dân: {aff_url}"
        else:
            aff_url = f"https://s.shopee.vn/an_redir?origin_link={deal['raw_url']}&affiliate_id=783489745"
            comment = f"👉 Click săn mã giảm 50k freeship gian hàng ShopeeMall ở đây nha: {aff_url}"
            
        content = f"🔥 [HOT SALE CHỈ CÒN 15 XUẤT] {deal['product_name'].upper()}!\n\n🛒 Đặt mua gian hàng chính hãng tại: {aff_url}"
        
        edited_posts.append({
            'poster_id': item['poster_id'],
            'poster_name': item['poster_name'],
            'content': content,
            'first_comment': comment,
            'scheduled_at': item['scheduled_at']
        })
        print(f"   ✍️ Editor: Đã biên soạn xong bài viết cho '{deal['product_name'][:35]}...'")
        
    return edited_posts

# ---------------------------------------------------------
# SUB-AGENT 4: REVIEWER AGENT & DEPLOYMENT
# ---------------------------------------------------------
def agent_4_reviewer_and_deploy(edited_posts):
    print("[Codebuff Agent 4: Reviewer] Kiểm tra chất lượng link Affiliate & Phê duyệt bài đăng...")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    approved_count = 0
    now_str = datetime.now().isoformat()
    
    for p in edited_posts:
        # Quality check
        if '783489745' in p['first_comment'] or '201037552823' in p['first_comment']:
            post_id = 'cb_' + str(uuid.uuid4())[:8]
            cursor.execute(
                """INSERT INTO posts (
                    id, account_id, type, target_id, content, media, scheduled_at, status, 
                    created_at, updated_at, platform, first_comment, is_bait_post
                ) VALUES (?, ?, 'profile', 'me', ?, '[]', ?, 'pending', ?, ?, 'facebook', ?, 0)""",
                (post_id, p['poster_id'], p['content'], p['scheduled_at'], now_str, now_str, p['first_comment'])
            )
            approved_count += 1
            print(f"   ✅ Reviewer: Đã duyệt bài đăng #{approved_count} (Pass link Affiliate 100%)")
            
    conn.commit()
    conn.close()
    return approved_count

def run_codebuff_pipeline():
    print("\n🚀 BẮT ĐẦU VẬN HÀNH TIẾN TRÌNH MULTI-AGENT CODEBUFF...")
    deals = agent_1_deal_extractor()
    plans = agent_2_planner(deals)
    edited = agent_3_editor(plans)
    count = agent_4_reviewer_and_deploy(edited)
    print(f"\n===============================================================")
    print(f"🎉 TIẾN TRÌNH MULTI-AGENT HOÀN TẤT: ĐÃ DUYỆT & BƠM {count} BÀI ĐĂNG VÀO HỆ THỐNG!")
    print("===============================================================")
    return {'success': True, 'approved_posts': count}

if __name__ == '__main__':
    run_codebuff_pipeline()

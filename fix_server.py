import sys

def fix_server():
    with open('server.py', 'r', encoding='utf-8') as f:
        content = f.read()

    start_idx = content.find("def insight_worker():")
    if start_idx == -1:
        print("Cannot find insight_worker_func")
        return
        
    end_idx = content.find("def auto_seed_worker():", start_idx)
    if end_idx == -1:
        print("Cannot find auto_seed_worker")
        return
        
    new_worker_code = """
def process_target(target, active_accounts):
    try:
        import automation
        import database
        import telegram_bot
        import random
        from datetime import datetime
        import uuid
        import time
        import json

        last_run = target.get('last_run')
        if last_run:
            last_run_time = datetime.fromisoformat(last_run)
            if (datetime.now() - last_run_time).total_seconds() < 900: # 15 minutes
                return
        
        acc = random.choice(active_accounts)
        if target['target_url'] == 'global':
            print(f"[Insights] Bắt đầu tìm kiếm bài viết toàn Facebook với từ khóa: {target['niche_keywords']}", flush=True)
            scan_res = automation.search_global_posts_by_keyword(acc['cookie'], target['niche_keywords'], limit=15)
        elif target['target_url'] == 'newsfeed':
            print(f"[Insights] Bắt đầu quét Bảng Tin (Newsfeed) để tìm khách hàng đa ngách...", flush=True)
            scan_res = automation.scan_group_for_insights(acc['cookie'], 'newsfeed', limit=15)
        else:
            print(f"[Insights] Bắt đầu quét khách hàng cho nhóm/trang: {target['target_name']}", flush=True)
            scan_res = automation.scan_group_for_insights(acc['cookie'], target['target_url'], limit=15)
            
        if not scan_res.get('success'):
            print(f"[Insights] Lỗi quét {target['target_name']}: {scan_res.get('log')}", flush=True)
            database.update_insight_target_last_run(target['id'])
            return
        
        posts = scan_res.get('posts', [])
        if not posts:
            print(f"[Insights] Không tìm thấy bài viết mới ở {target['target_name']}", flush=True)
            database.update_insight_target_last_run(target['id'])
            return
        
        new_posts = []
        for p in posts:
            if not database.is_lead_exists(p['url']) and not database.is_scanned_post(p['url']):
                new_posts.append(p)
                database.save_scanned_post(p['url'])
        
        if not new_posts:
            print(f"[Insights] Không có bài viết nào mới ở {target['target_name']}", flush=True)
            database.update_insight_target_last_run(target['id'])
            return
        
        print(f"[Insights] Tìm thấy {len(new_posts)} bài viết chưa phân tích ở {target['target_name']}. Bắt đầu đẩy qua AI...", flush=True)
        analysis_res = automation.analyze_customer_insights(new_posts, target['niche_keywords'])
        if analysis_res.get('success'):
            leads = analysis_res.get('data', [])
            for lead in leads:
                post_url = lead.get('post_url')
                if post_url and not database.is_lead_exists(post_url):
                    import json
                    lead_id = 'lead_' + str(uuid.uuid4())[:8]
                    database.save_insight_lead(
                        lead_id=lead_id,
                        target_id=target['id'],
                        post_url=post_url,
                        author_name=lead.get('author'),
                        content="", 
                        analysis=json.dumps(lead, ensure_ascii=False)
                    )
                    telegram_bot.notify_insight_lead(lead, target['niche_keywords'])
                    print(f"[Insights] Đã lưu và thông báo lead mới: {lead.get('author')}", flush=True)
        else:
            print(f"[Insights] Lỗi phân tích AI: {analysis_res.get('log')}", flush=True)
        
        database.update_insight_target_last_run(target['id'])
    except Exception as e:
        print(f"[Insights] Lỗi process_target cho {target.get('target_name')}: {e}", flush=True)


def insight_worker():
    print("[Insights] Insight worker started.", flush=True)
    import time
    import random
    from datetime import datetime
    import database
    import automation
    import uuid
    import telegram_bot
    from concurrent.futures import ThreadPoolExecutor

    while True:
        try:
            active_targets = [t for t in database.get_insight_targets() if t['status'] == 'active']
            if not active_targets:
                database.save_insight_target(None, 'global', 'Tìm kiếm Toàn Facebook', 'thú cưng, chó mèo')
                active_targets = [t for t in database.get_insight_targets() if t['status'] == 'active']

            has_global = any(t['target_url'] == 'global' for t in active_targets)
            if not has_global:
                keywords = "thú cưng, chó mèo"
                if active_targets:
                    keywords = active_targets[0].get('niche_keywords', keywords)
                database.save_insight_target(None, 'global', 'Tìm kiếm Toàn Facebook', keywords)
                active_targets = [t for t in database.get_insight_targets() if t['status'] == 'active']

            has_newsfeed = any(t['target_url'] == 'newsfeed' for t in active_targets)
            if not has_newsfeed:
                database.save_insight_target(None, 'newsfeed', 'Bảng Tin Facebook (Newsfeed)', 'Tất cả')
                active_targets = [t for t in database.get_insight_targets() if t['status'] == 'active']
            
            accounts = database.get_accounts()
            active_accounts = [a for a in accounts if a['status'] == 'active' and a.get('cookie')]
            if not active_accounts:
                time.sleep(60)
                continue
                
            if random.random() < 0.10:
                global_target = next((t for t in active_targets if t['target_url'] == 'global'), None)
                if global_target:
                    keywords_list = [k.strip() for k in global_target['niche_keywords'].split(',') if k.strip()]
                    if keywords_list:
                        kw = random.choice(keywords_list)
                        if kw.lower() not in ['tất cả', 'all']:
                            acc = random.choice(active_accounts)
                            print(f"[Insights] Đang kích hoạt chế độ lân la tìm hội nhóm mới cho từ khóa: {kw}", flush=True)
                            automation.discover_new_groups(acc['cookie'], kw, limit=3)
            
            settings = database.get_settings()
            max_workers = int(settings.get('insight_max_workers', 3))
            
            targets_to_run = []
            for target in active_targets:
                last_run = target.get('last_run')
                if last_run:
                    last_run_time = datetime.fromisoformat(last_run)
                    if (datetime.now() - last_run_time).total_seconds() < 900:
                        continue
                targets_to_run.append(target)
            
            if targets_to_run:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    for target in targets_to_run:
                        executor.submit(process_target, target, active_accounts)
                
        except Exception as e:
            print(f"[Insights] Worker Error: {e}", flush=True)
        time.sleep(30)


"""
    
    new_content = content[:start_idx] + new_worker_code.strip() + "\\n\\n\\n" + content[end_idx:]
    
    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
        print("server.py updated successfully")

fix_server()

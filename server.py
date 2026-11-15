import os, csv, io, threading, time, uuid, json, sys
from datetime import datetime, timedelta

# Configure UTF-8 output to prevent UnicodeEncodeError in Windows CP1252 terminal
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import database
from automation import publish_post, auto_reply_post_comments, auto_like_posts, scrape_shopee_product, post_article_comment, publish_threads_post, auto_engage_feed_posts, call_gemini, auto_join_facebook_groups, scrape_and_save_public_groups, auto_join_groups_by_topic, auto_login_facebook

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(os.path.join(UPLOAD_FOLDER, 'screenshots'), exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

database.init_db()

import urllib.parse
def make_shopee_affiliate_link(url, settings):
    if not url:
        return url
    aff_id = settings.get('shopee_affiliate_id', '').strip()
    sub_id = settings.get('shopee_sub_id', '').strip()
    if not aff_id:
        return url
    
    # Only convert if it's a shopee domain
    if 'shopee.vn' in url or 'shope.ee' in url or 's.shopee.vn' in url:
        # Check if already affiliate redir
        if 'an_redir' in url:
            return url
        # Encode and wrap
        encoded_url = urllib.parse.quote(url, safe='')
        return f"https://s.shopee.vn/an_redir?origin_link={encoded_url}&affiliate_id={aff_id}&sub_id={sub_id}"
    return url

# ─────────────────────────────────────────
# BACKGROUND WORKERS
# ─────────────────────────────────────────
import subprocess

tunnel_status = "Offline"
tunnel_url = None

def try_serveo():
    global tunnel_status, tunnel_url
    tunnel_status = "Connecting"
    try:
        settings = database.get_settings()
        subdomain = settings.get('tunnel_subdomain', 'chungs-shopee')
        cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "-R", f"{subdomain}:80:localhost:5000", "serveo.net"]
        print(f"[Tunnel] Attempting Serveo: {' '.join(cmd)}")
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        start_time = time.time()
        url = None
        
        while True:
            if proc.poll() is not None:
                break
            
            line = proc.stdout.readline()
            if not line:
                break
            cleaned = line.strip()
            print(f"[Serveo] {cleaned}")
            if "https://" in cleaned and ".serveousercontent.com" in cleaned:
                for part in cleaned.split():
                    if part.startswith("https://") and ".serveousercontent.com" in part:
                        url = part.strip()
                        break
                if url:
                    database.save_setting('public_domain', url)
                    tunnel_url = url
                    tunnel_status = "Online"
                    print(f"[Serveo] Successfully configured public domain: {url}")
            if not url and (time.time() - start_time > 25):
                print("[Serveo] Timeout waiting for URL, killing process...")
                proc.terminate()
                break
                
        rc = proc.wait()
        return url is not None
    except Exception as e:
        print(f"[Serveo] Error: {e}")
        return False

def try_localhost_run():
    global tunnel_status, tunnel_url
    tunnel_status = "Connecting"
    try:
        cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "-R", "80:localhost:5000", "nokey@localhost.run"]
        print(f"[Tunnel] Attempting Localhost.run: {' '.join(cmd)}")
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        start_time = time.time()
        url = None
        
        while True:
            if proc.poll() is not None:
                break
            line = proc.stdout.readline()
            if not line:
                break
            cleaned = line.strip()
            print(f"[LocalhostRun] {cleaned}")
            if "https://" in cleaned and (".lhr.life" in cleaned or ".localhost.run" in cleaned):
                for part in cleaned.split():
                    if part.startswith("https://") and (".lhr.life" in part or ".localhost.run" in part):
                        url = part.strip().rstrip('.')
                        break
                if url:
                    database.save_setting('public_domain', url)
                    tunnel_url = url
                    tunnel_status = "Online"
                    print(f"[LocalhostRun] Successfully configured public domain: {url}")
            if not url and (time.time() - start_time > 25):
                print("[LocalhostRun] Timeout waiting for URL, killing process...")
                proc.terminate()
                break
                
        rc = proc.wait()
        return url is not None
    except Exception as e:
        print(f"[LocalhostRun] Error: {e}")
        return False

def tunnel_worker():
    global tunnel_status, tunnel_url
    while True:
        try:
            print("[Tunnel] Starting SSH Tunnel manager...")
            success = try_serveo()
            if not success:
                print("[Tunnel] Serveo failed, attempting Localhost.run...")
                success = try_localhost_run()
            if not success:
                tunnel_status = "Offline"
                tunnel_url = None
                print("[Tunnel] Both tunnel methods failed. Retrying in 30 seconds...")
                time.sleep(30)
            else:
                tunnel_status = "Offline"
                tunnel_url = None
                time.sleep(5)
        except Exception as e:
            tunnel_status = "Offline"
            tunnel_url = None
            print(f"[Tunnel] Error: {e}. Retrying in 15 seconds...")
            time.sleep(15)

def scheduler_worker():
    print("[Scheduler] Post scheduler started.")
    last_post_times = {}
    while True:
        try:
            now = datetime.now().isoformat()
            due = [p for p in database.get_posts_by_status('pending') if p['scheduled_at'] <= now]
            due.sort(key=lambda x: x['scheduled_at'])
            for post in due:
                account_id = post['account_id']
                last_time = last_post_times.get(account_id)
                if last_time:
                    elapsed = (datetime.now() - last_time).total_seconds()
                    delay = int(database.get_settings().get('delay_between_posts', 60))
                    if elapsed < delay:
                        sleep_time = delay - elapsed
                        print(f"[Scheduler] Giãn cách bài đăng cho tài khoản {account_id}. Chờ {sleep_time:.1f} giây...")
                        time.sleep(sleep_time)
                
                print(f"[Scheduler] Processing post {post['id']}")
                database.update_post_status(post['id'], 'posting', 'Đang đăng bài...')
                account = database.get_account(account_id)
                if not account:
                    database.update_post_status(post['id'], 'failed', 'Không tìm thấy tài khoản.')
                    continue
                if account.get('platform') == 'threads':
                    result = publish_threads_post(account['cookie'], post['content'], post['media'], post['id'], post.get('first_comment'))
                else:
                    result = publish_post(account['cookie'], post['type'], post['target_id'],
                                          post['content'], post['media'], post['id'],
                                          post.get('first_comment'))
                                          
                # Auto-retry with fresh cookie if failed due to cookie/composer errors
                if not result['success'] and account.get('username') and account.get('password'):
                    log_lower = (result.get('log') or '').lower()
                    if any(kw in log_lower for kw in ['cookie', 'composer', 'login', 'expired', 'checkpoint', 'session']):
                        print(f"[Scheduler] Đăng bài thất bại do Cookie lỗi. Đang tự đăng nhập lại cho {account['name']}...")
                        login_res = auto_login_facebook(account['username'], account['password'], account.get('two_factor_key'))
                        if login_res['success']:
                            new_cookie = login_res['cookie']
                            database.save_account(
                                account_id=account['id'],
                                name=account['name'],
                                cookie=new_cookie,
                                status='active',
                                platform=account['platform'],
                                username=account['username'],
                                password=account['password'],
                                two_factor_key=account.get('two_factor_key')
                            )
                            print(f"[Scheduler] Thử đăng bài lại sau khi gia hạn Cookie thành công...")
                            if account.get('platform') == 'threads':
                                result = publish_threads_post(new_cookie, post['content'], post['media'], post['id'], post.get('first_comment'))
                            else:
                                result = publish_post(new_cookie, post['type'], post['target_id'],
                                                      post['content'], post['media'], post['id'],
                                                      post.get('first_comment'))
                                                      
                if not result['success'] and result.get('status') == 'nurturing':
                    next_run = (datetime.now() + timedelta(days=1)).isoformat()[:16]
                    database.update_post_status_and_time(post['id'], 'pending', next_run, result['log'])
                else:
                    status = result.get('status', 'posted') if result['success'] else 'failed'
                    database.update_post_status(post['id'], status, result['log'], result['screenshot'], result.get('post_url'))
                    if status == 'pending_approval' and post['type'] == 'group':
                        database.increment_group_pending_count(post['target_id'])
                if post.get('bulk_group_id'):
                    database.update_bulk_group_stats(post['bulk_group_id'])
                
                last_post_times[account_id] = datetime.now()
        except Exception as e:
            print(f"[Scheduler] Error: {e}")
        time.sleep(10)

def engagement_worker():
    print("[Engage] Engagement worker started.")
    while True:
        try:
            settings = database.get_settings()
            interval = int(settings.get('engage_interval_minutes', 15)) * 60
            time.sleep(interval)

            rules = [r for r in database.get_engagement_rules() if r['status'] == 'active']
            if not rules:
                continue

            max_replies = int(settings.get('max_replies_per_scan', 5))
            posted = database.get_posts_by_status('posted')

            for post in posted[:3]:
                account = database.get_account(post['account_id'])
                if not account or account['status'] != 'active':
                    continue
                target_id_str = str(post['target_id']).strip()
                if target_id_str.startswith('http://') or target_id_str.startswith('https://'):
                    url = target_id_str
                elif 'facebook.com' in target_id_str or 'fb.com' in target_id_str:
                    url = 'https://' + target_id_str if not target_id_str.startswith('http') else target_id_str
                else:
                    if post['type'] == 'group':
                        url = f"https://www.facebook.com/groups/{target_id_str}"
                    elif post['type'] == 'page':
                        url = f"https://www.facebook.com/{target_id_str}"
                    else:
                        url = "https://www.facebook.com"

                print(f"[Engage] Auto-scanning: {url}")
                logs = auto_reply_post_comments(account['cookie'], url, account['name'], rules, max_replies)
                for log in logs:
                    database.save_engagement_log(
                        log['id'], log['post_url'], log['commenter_name'],
                        log['comment_content'], log['reply_content'],
                        log['status'], log.get('screenshot'))
        except Exception as e:
            print(f"[Engage] Error: {e}")

def autolike_worker():
    print("[AutoLike] Auto-like worker started.")
    while True:
        try:
            settings = database.get_settings()
            interval = int(settings.get('autolike_interval_minutes', 30)) * 60

            targets = [t for t in database.get_autolike_targets() if t['status'] == 'active']
            max_likes = int(settings.get('max_likes_per_scan', 10))

            for target in targets:
                account = database.get_account(target['account_id'])
                if not account or account['status'] != 'active':
                    continue
                # Safe print target name to prevent UnicodeEncodeError on Windows CP1252
                try:
                    target_name_safe = target['target_name'].encode('ascii', 'ignore').decode('ascii')
                except Exception:
                    target_name_safe = target['id']
                print(f"[AutoLike] Processing target: {target_name_safe}")
                liked = auto_like_posts(
                    account['cookie'], target['target_url'], max_likes,
                    auto_comment=target.get('auto_comment', 0),
                    comment_style=target.get('comment_style', 'AI'),
                    comment_text=target.get('comment_text', ''),
                    account_name=account['name']
                )
                for item in liked:
                    database.save_autolike_log(item['id'], target['id'], item['post_url'], item['status'])
                database.update_autolike_target_last_run(target['id'])
                
            print(f"[AutoLike] Scan complete. Sleeping for {interval} seconds.")
            time.sleep(interval)
        except Exception as e:
            print(f"[AutoLike] Error: {e}")

def autobump_worker():
    print("[AutoBump] Auto-bump worker started.")
    while True:
        try:
            # Chạy mỗi 4 tiếng
            time.sleep(4 * 60 * 60)
            
            posted_posts = database.get_posts_by_status('posted')
            if not posted_posts:
                continue
                
            posted_posts.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            bump_templates = [
                ".",
                "..",
                "up",
                "up bài ạ!",
                "🌸",
                "✨",
                "Chấm nhận tư vấn nhanh ạ! 👍",
                "Inbox ngay shop tư vấn nhiệt tình nha cả nhà 🌸"
            ]
            import random
            
            for post in posted_posts[:2]:
                settings = database.get_settings()
                bump_acc_id = settings.get('bump_account_id')
                
                if bump_acc_id:
                    account = database.get_account(bump_acc_id)
                else:
                    # Fallback to looking for an account named 'shope vip' or similar
                    all_accs = database.get_accounts()
                    vip_accs = [a for a in all_accs if 'vip' in a['name'].lower() and a['status'] == 'active']
                    if vip_accs:
                        account = vip_accs[0]
                    else:
                        account = database.get_account(post['account_id'])
                        
                if not account or account['status'] != 'active':
                    continue
                    
                target_id_str = str(post['target_id']).strip()
                if target_id_str.startswith('http://') or target_id_str.startswith('https://'):
                    url = target_id_str
                elif 'facebook.com' in target_id_str or 'fb.com' in target_id_str:
                    url = 'https://' + target_id_str if not target_id_str.startswith('http') else target_id_str
                else:
                    if post['type'] == 'group':
                        url = f"https://www.facebook.com/groups/{target_id_str}"
                    elif post['type'] == 'page':
                        url = f"https://www.facebook.com/{target_id_str}"
                    else:
                        continue
                    
                comment_text = random.choice(bump_templates)
                print(f"[AutoBump] Bumping post {post['id']} on {url} using account {account['name']}")
                post_article_comment(account['cookie'], url, comment_text)
                
        except Exception as e:
            print(f"[AutoBump] Error: {e}")

def run_single_account_autofeed(account, source, max_posts, comment_style, comment_text):
    try:
        print(f"[AutoFeed] Starting parallel thread for account: {account['name']}")
        result = auto_engage_feed_posts(
            account_cookie=account['cookie'],
            account_name=account['name'],
            source=source,
            max_posts=max_posts,
            comment_style=comment_style,
            comment_text=comment_text
        )
        
        # Save any returned logs to engagement_logs database
        if result.get('logs'):
            for log in result['logs']:
                log_id = 'log_' + str(uuid.uuid4())[:8]
                database.save_engagement_log(
                    log_id=log_id,
                    post_url=log['post_url'],
                    commenter_name=log['commenter_name'],
                    comment_content=log['comment_content'],
                    reply_content=log['reply_content'],
                    status=log['status'],
                    screenshot=log.get('screenshot')
                )
        print(f"[AutoFeed] Finished parallel thread for account: {account['name']}. Log: {result.get('log')}")
    except Exception as e:
        print(f"[AutoFeed] Error in parallel thread for account {account['name']}: {e}")

def autofeed_worker():
    print("[AutoFeed] Auto-feed engagement worker started.")
    while True:
        try:
            settings = database.get_settings()
            enabled = settings.get('autofeed_engage_enabled', '0') == '1'
            if not enabled:
                time.sleep(30)
                continue

            interval = int(settings.get('autofeed_engage_interval_minutes', 30)) * 60
            
            # Find all active Facebook accounts
            accounts = [a for a in database.get_accounts() if a['status'] == 'active' and a.get('platform', 'facebook') == 'facebook']
            
            target_account_id = settings.get('autofeed_account_id')
            if target_account_id and target_account_id.strip():
                filtered_accounts = [a for a in accounts if a['id'] == target_account_id]
                if filtered_accounts:
                    accounts = filtered_accounts

            if not accounts:
                time.sleep(30)
                continue

            source = settings.get('autofeed_engage_source', 'groups')
            max_posts = int(settings.get('autofeed_max_posts_per_scan', 5))
            comment_style = settings.get('autofeed_engage_style', 'spintax')
            comment_text = settings.get('autofeed_engage_text', '')

            threads = []
            for account in accounts:
                # Re-check settings in case they were disabled while launching
                settings = database.get_settings()
                if settings.get('autofeed_engage_enabled', '0') != '1':
                    break

                t = threading.Thread(
                    target=run_single_account_autofeed,
                    args=(account, source, max_posts, comment_style, comment_text),
                    daemon=True
                )
                threads.append(t)
                t.start()
                time.sleep(5) # Stagger launches by 5 seconds
            
            # Wait for all threads to finish
            for t in threads:
                t.join()
            
            print(f"[AutoFeed] All accounts finished scan. Sleeping for interval: {interval} seconds.")
            time.sleep(interval)
        except Exception as e:
            print(f"[AutoFeed] Error in worker: {e}")
            time.sleep(60)

def get_shopee_scheduler_details(topic_name):
    import unicodedata
    def norm(s):
        if not s: return ""
        s = s.lower().strip()
        s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        return s

    topic_norm = norm(topic_name)
    
    config_list = [
        {
            "account_type": "Lolishop",
            "account_keywords": ["lolishop"],
            "topics": ["lolishop_direct_profile"],
            "golden_hours": ["07:30", "11:30", "19:30", "20:30"]
        },
        {
            "account_type": "Shopee",
            "account_keywords": ["shope", "shopee"],
            "topics": ["Chợ", "Nội trợ", "Mẹ bỉm", "Nấu ăn", "cho", "noi tro", "bim sua", "nau an"],
            "golden_hours": ["07:30", "11:00", "19:00"]
        },
        {
            "account_type": "Shopee Lite",
            "account_keywords": ["shope lite chinh", "shopee lite chinh", "lite chinh"],
            "topics": ["Gym", "Chạy bộ", "Sinh viên", "gym", "tap gym", "chay bo", "sinh vien", "the thao"],
            "golden_hours": ["06:00", "16:00", "20:30"]
        },
        {
            "account_type": "Shopee VIP",
            "account_keywords": ["shope vip", "shopee vip", "vip"],
            "topics": ["Phụ nữ độc thân", "Thời trang", "Du lịch", "Thú cưng", "phu nu", "thoi trang", "du lich", "thu cung"],
            "golden_hours": ["12:00", "20:30", "21:30"]
        },
        {
            "account_type": "Shopee Lite 2",
            "account_keywords": ["shope  lite phu", "shopee lite phu", "lite phu"],
            "topics": ["Công nghệ", "Kinh doanh", "cong nghe", "kinh doanh", "mmo"],
            "golden_hours": ["09:00", "14:00", "21:00"]
        },
        {
            "account_type": "Shopee Sale",
            "account_keywords": ["shope sale", "shopee sale", "sale"],
            "topics": ["Mê xe", "Nhà đất", "Sinh viên", "xe", "xe co", "choi xe", "me xe", "nha dat", "sinh vien"],
            "golden_hours": ["11:00", "16:00", "20:00"]
        }
    ]
    
    for cfg in config_list:
        for t in cfg["topics"]:
            if norm(t) in topic_norm or topic_norm in norm(t):
                return cfg
                
    return config_list[0]

def get_next_golden_slot(account_id, golden_hours, current_scheduled_times, start_from=None):
    if not start_from:
        start_from = datetime.now()
        
    for day_offset in range(14):
        day = start_from + timedelta(days=day_offset)
        for hour_str in golden_hours:
            try:
                parts = hour_str.split(':')
                hour = int(parts[0])
                minute = int(parts[1])
                slot_time = datetime(day.year, day.month, day.day, hour, minute)
                
                if slot_time <= start_from:
                    continue
                    
                booked = False
                for t_str in current_scheduled_times:
                    if not t_str:
                        continue
                    try:
                        t = datetime.fromisoformat(t_str[:16])
                        if abs((t - slot_time).total_seconds()) < 300:
                            booked = True
                            break
                    except Exception:
                        pass
                
                if not booked:
                    return slot_time
            except Exception:
                pass
                
    return start_from + timedelta(hours=1)

def parse_target_line(line):
    line = line.strip()
    if not line:
        return None
    if line.lower().startswith('group:'):
        return {'type': 'group', 'target_id': line[6:].strip()}
    if line.lower().startswith('page:'):
        return {'type': 'page', 'target_id': line[5:].strip()}
    return {'type': 'profile', 'target_id': line}

def shopee_folder_worker():
    print("[ShopeePoster] Monitor folder worker started.")
    import shutil
    import glob
    import unicodedata
    
    def norm(s):
        if not s: return ""
        s = s.lower().strip()
        s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        return s
        
    shopee_dir = r"C:\Users\TOSHIBA\.gemini\antigravity\scratch\fb-poster\shopee_links"
    processed_dir = os.path.join(shopee_dir, "processed")
    os.makedirs(shopee_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    
    while True:
        try:
            active_accounts = [a for a in database.get_accounts() if a['status'] == 'active']
            if not active_accounts:
                time.sleep(30)
                continue
                
            settings = database.get_settings()
            poster_type = settings.get('shopee_poster_type', 'profile')
            poster_target_id = settings.get('shopee_poster_target_id', 'me')
            poster_format = settings.get('shopee_poster_format', 'clickable')
            api_key = settings.get('gemini_api_key', '').strip()
            
            txt_files = glob.glob(os.path.join(shopee_dir, "*.txt"))
            
            for file_path in txt_files:
                filename = os.path.basename(file_path)
                print(f"[ShopeePoster] Found file to import: {filename}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                except Exception as read_err:
                    print(f"[ShopeePoster] Error reading file {filename}: {read_err}")
                    continue
                    
                urls = []
                for line in lines:
                    line = line.strip()
                    if line and (line.startswith('http://') or line.startswith('https://')):
                        urls.append(line)
                        
                if not urls:
                    try:
                        shutil.move(file_path, os.path.join(processed_dir, filename))
                    except Exception:
                        pass
                    continue
                
                # Determine topic from filename
                topic_name = filename.replace('.txt', '')
                cfg = get_shopee_scheduler_details(topic_name)
                print(f"[ShopeePoster] Filename '{filename}' mapped to topic '{cfg['account_type']}' with hours {cfg['golden_hours']}")
                
                # Find matching account
                account_id = None
                for acc in active_accounts:
                    acc_name_norm = norm(acc['name'])
                    for kw in cfg["account_keywords"]:
                        if norm(kw) in acc_name_norm or acc_name_norm in norm(kw):
                            account_id = acc['id']
                            break
                    if account_id:
                        break
                
                if not account_id:
                    shopee_account_id = settings.get('shopee_poster_account_id', '').strip()
                    account_id = shopee_account_id if shopee_account_id else active_accounts[0]['id']
                    print(f"[ShopeePoster] No matching account found for keywords {cfg['account_keywords']}. Fallback to account ID: {account_id}")
                else:
                    print(f"[ShopeePoster] Matched account ID: {account_id}")
                    
                # Find matching target list
                conn = database.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, targets FROM target_lists")
                target_lists = cursor.fetchall()
                conn.close()
                
                matched_targets = None
                for tl_id, tl_name, tl_targets in target_lists:
                    tl_name_norm = norm(tl_name)
                    for t in cfg["topics"]:
                        if norm(t) in tl_name_norm or tl_name_norm in norm(t):
                            matched_targets = tl_targets
                            break
                    if matched_targets:
                        break
                        
                targets = []
                if matched_targets:
                    for line in matched_targets.split('\n'):
                        line = line.strip()
                        if not line:
                            continue
                        parsed = parse_target_line(line)
                        if parsed:
                            targets.append(parsed)
                    print(f"[ShopeePoster] Matched target list with {len(targets)} targets.")
                
                if not targets:
                    targets = [{"type": poster_type, "target_id": poster_target_id}]
                    print(f"[ShopeePoster] No matching target list. Fallback to default target: {poster_target_id}")
                
                # Retrieve existing scheduled times for this account
                conn = database.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT scheduled_at FROM posts WHERE account_id=? AND status='pending'", (account_id,))
                current_scheduled_times = [row[0] for row in cursor.fetchall()]
                conn.close()
                
                start_from = datetime.now()
                scheduled_count = 0
                
                for url in urls:
                    conn = database.get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM redirects WHERE destination_url=?", (url,))
                    dup_redir = cursor.fetchone()
                    cursor.execute("SELECT id FROM posts WHERE content LIKE ?", (f"%{url}%",))
                    dup_post = cursor.fetchone()
                    conn.close()
                    
                    if dup_redir or dup_post:
                        print(f"[ShopeePoster] Skipping duplicate Shopee URL: {url}")
                        continue
                        
                    print(f"[ShopeePoster] Processing URL: {url}")
                    product = scrape_shopee_product(url)
                    if 'error' in product or not product.get('title'):
                        print(f"[ShopeePoster] Failed to scrape {url}: {product.get('error', 'No title')}")
                        continue
                    
                    if api_key:
                        prompt = (
                            f"Hãy viết một bài viết quảng cáo giới thiệu sản phẩm hấp dẫn, hài hước, kích thích mua sắm dựa trên thông tin sản phẩm Shopee này:\n"
                            f"Tiêu đề: {product.get('title')}\n"
                            f"Mô tả: {product.get('description', '')[:1000]}\n\n"
                            f"Yêu cầu:\n"
                            f"- CHỈ trả về nội dung bài viết quảng cáo trực tiếp. KHÔNG viết lời mở đầu, KHÔNG viết lời chào hay bất kỳ câu giới thiệu nào khác (ví dụ: KHÔNG viết 'Dưới đây là...', 'Được thôi...', 'Đây là...').\n"
                            f"- Tập trung giới thiệu công dụng, tính năng nổi bật và lợi ích thực tế của sản phẩm.\n"
                            f"- KHÔNG quảng cáo hay nhắc đến 'kênh Shopee', 'gian hàng', 'shop của mình' hay 'kênh affiliate/tiếp thị liên kết'. Bán sản phẩm chứ không quảng cáo kênh.\n"
                            f"- Ngắn gọn dưới 150 từ, dùng nhiều emoji phù hợp.\n"
                            f"- Có lời kêu gọi hành động (Call to Action) bấm vào link/hình ảnh ở dưới để mua sản phẩm.\n"
                            f"- Không được kèm liên kết gốc Shopee trong nội dung bài viết."
                        )
                        try:
                            post_content = call_gemini(api_key, prompt)
                        except Exception as ai_err:
                            print(f"[ShopeePoster] Gemini AI error: {ai_err}")
                            post_content = f"🔥 {product.get('title')} 🔥\n\nSản phẩm cực chất, click ngay để mua với giá ưu đãi!"
                    else:
                        post_content = f"🔥 {product.get('title')} 🔥\n\nSản phẩm cực chất, click ngay để mua với giá ưu đãi!"
                    
                    scheduled_time = get_next_golden_slot(account_id, cfg["golden_hours"], current_scheduled_times, start_from)
                    scheduled_at_str = scheduled_time.isoformat()[:16]
                    current_scheduled_times.append(scheduled_at_str)
                    start_from = scheduled_time
                    
                    post_id = 'post_' + str(uuid.uuid4())[:8]
                    image_url = product.get('image_url')
                    media_list = []
                    
                    if poster_format == 'clickable' and image_url:
                        import urllib.request
                        local_image_name = f"shopee_{post_id}.jpg"
                        local_image_path = os.path.join(UPLOAD_FOLDER, local_image_name)
                        try:
                            req = urllib.request.Request(
                                image_url, 
                                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                            )
                            with urllib.request.urlopen(req, timeout=15) as response, open(local_image_path, 'wb') as out_file:
                                out_file.write(response.read())
                            
                            media_list = [f"uploads/{local_image_name}"]
                            
                            redir_id = 'r_' + str(uuid.uuid4())[:8]
                            conn = database.get_db_connection()
                            cursor = conn.cursor()
                            aff_url = make_shopee_affiliate_link(url, settings)
                            cursor.execute(
                                'INSERT INTO redirects (id, destination_url, image_file, title, description, created_at) VALUES (?,?,?,?,?,?)',
                                (redir_id, aff_url, f"uploads/{local_image_name}", product.get('title')[:100], "Click xem chi tiết sản phẩm và mua ngay!", datetime.now().isoformat())
                            )
                            conn.commit()
                            conn.close()
                            
                            public_domain = settings.get('public_domain', 'http://localhost:5000').rstrip('/')
                            redirect_link = f"{public_domain}/r/{redir_id}"
                            
                            shopee_auto_comment = settings.get('shopee_auto_comment_link', '1') == '1'
                            first_comment = None
                            if shopee_auto_comment:
                                comment_template = settings.get('shopee_comment_template', 'Link mua sản phẩm tại đây nhé cả nhà: {link}')
                                first_comment = comment_template.replace('{link}', redirect_link)
                                post_content = f"{post_content}\n\n👉 Chi tiết sản phẩm: {redirect_link}"
                            else:
                                post_content = f"{post_content}\n\n👉 Chi tiết sản phẩm: {redirect_link}"
                            
                        except Exception as img_err:
                            print(f"[ShopeePoster] Image download error, falling back to normal link: {img_err}")
                            shopee_auto_comment = settings.get('shopee_auto_comment_link', '1') == '1'
                            first_comment = None
                            aff_url = make_shopee_affiliate_link(url, settings)
                            if shopee_auto_comment:
                                comment_template = settings.get('shopee_comment_template', 'Link mua sản phẩm tại đây nhé cả nhà: {link}')
                                first_comment = comment_template.replace('{link}', aff_url)
                            else:
                                post_content = f"{post_content}\n\n👉 Mua ngay tại đây: {aff_url}"
                    else:
                        shopee_auto_comment = settings.get('shopee_auto_comment_link', '1') == '1'
                        first_comment = None
                        aff_url = make_shopee_affiliate_link(url, settings)
                        if shopee_auto_comment:
                            comment_template = settings.get('shopee_comment_template', 'Link mua sản phẩm tại đây nhé cả nhà: {link}')
                            first_comment = comment_template.replace('{link}', aff_url)
                        else:
                            post_content = f"{post_content}\n\n👉 Mua ngay tại đây: {aff_url}"
                    
                    for target in targets:
                        target_post_id = 'post_' + str(uuid.uuid4())[:8]
                        database.save_post(
                            post_id=target_post_id,
                            account_id=account_id,
                            type_=target['type'],
                            target_id=target['target_id'],
                            content=post_content,
                            media=media_list,
                            scheduled_at=scheduled_at_str,
                            status='pending',
                            first_comment=first_comment
                        )
                    
                    print(f"[ShopeePoster] Successfully scheduled Shopee posts at {scheduled_at_str}")
                    scheduled_count += 1
                
                dest_file_path = os.path.join(processed_dir, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}")
                try:
                    shutil.move(file_path, dest_file_path)
                except Exception as move_err:
                    print(f"[ShopeePoster] Error moving file: {move_err}")
                    
                if scheduled_count > 0:
                    print(f"[ShopeePoster] Monitored file {filename} import complete. Scheduled {scheduled_count} products.")
                    trigger_autojoin_for_targets(account_id, targets)
            
        except Exception as e:
            print(f"[ShopeePoster] Error in folder monitor: {e}")
            
        time.sleep(300)

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
            scan_res = automation.search_global_posts_by_keyword(acc['cookie'], target['niche_keywords'], limit=25)
        elif target['target_url'] == 'newsfeed':
            print(f"[Insights] Bắt đầu quét Bảng Tin (Newsfeed) để tìm khách hàng đa ngách...", flush=True)
            scan_res = automation.scan_group_for_insights(acc['cookie'], 'newsfeed', limit=25)
        else:
            print(f"[Insights] Bắt đầu quét khách hàng cho nhóm/trang: {target['target_name']}", flush=True)
            scan_res = automation.scan_group_for_insights(acc['cookie'], target['target_url'], limit=25)
            
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
                    # Find original content from new_posts
                    original_content = ""
                    for p in new_posts:
                        if p['url'] == post_url:
                            original_content = p.get('content', '')
                            break
                    
                    lead['content'] = original_content # Add to lead dict for Telegram
                    
                    lead_id = 'lead_' + str(uuid.uuid4())[:8]
                    database.save_insight_lead(
                        lead_id=lead_id,
                        target_id=target['id'],
                        post_url=post_url,
                        author_name=lead.get('author'),
                        content=original_content,
                        analysis=json.dumps(lead, ensure_ascii=False)
                    )
                    telegram_bot.notify_insight_lead(lead, target['niche_keywords'])
                    print(f"[Insights] Đã lưu và thông báo lead mới: {lead.get('author')}", flush=True)

                    # TỰ ĐỘNG BÌNH LUẬN DẠO RẢI LINK BIO
                    try:
                        # 1. Tìm tài khoản shope lite
                        lite_acc = None
                        for a in active_accounts:
                            if 'lite' in a['name'].lower():
                                lite_acc = a
                                break
                        if not lite_acc and active_accounts:
                            lite_acc = active_accounts[0] # Fallback to first active account
                        
                        if lite_acc:
                            print(f"[InsightsComment] Sử dụng tài khoản {lite_acc['name']} để bình luận dạo...")
                            settings = database.get_settings()
                            bio_link = settings.get('bait_bio_link', 'https://lolishop.vn')
                            
                            # 2. Sinh câu bình luận dạo bằng AI
                            from automation import get_ai_insight_comment, post_article_comment
                            comment_text = get_ai_insight_comment(original_content, bio_link)
                            
                            # 3. Tiến hành bình luận dạo rải link
                            res = post_article_comment(lite_acc['cookie'], post_url, comment_text)
                            # Handle both dict and bool return types
                            success = res.get('success') if isinstance(res, dict) else bool(res)
                            if success:
                                print(f"[InsightsComment] Đã bình luận dạo thành công lên bài: {post_url}")
                                # Gửi thông báo Telegram
                                try:
                                    token = settings.get('telegram_token')
                                    chat_id = settings.get('telegram_chat_id')
                                    msg = f"📣 <b>ĐÃ BÌNH LUẬN DẠO RẢI LINK!</b>\n\n"
                                    msg += f"👤 <b>Nick đi rải:</b> {lite_acc['name']}\n"
                                    msg += f"📝 <b>Nội dung bình luận:</b>\n<i>{comment_text}</i>\n\n"
                                    msg += f"🔗 <a href='{post_url}'>Xem bài viết gốc</a>"
                                    telegram_bot.send_telegram_message(token, chat_id, msg)
                                except Exception as tg_err:
                                    print(f"[InsightsComment] Lỗi gửi thông báo Telegram: {tg_err}")

                                # 4. ĐĂNG BÀI VỀ TÚI XÁCH LOLISHOP VÀO NHÓM - LUÔN LUÔN KÈM LINK
                                try:
                                    group_url = target.get('target_url', '')
                                    import re
                                    gid_match = re.search(r'groups/([^/?]+)', group_url)
                                    if gid_match:
                                        group_id = gid_match.group(1)
                                        api_key = settings.get('gemini_api_key', '').strip()

                                        # Dữ liệu phân tích lead - dùng để làm bài viết trúng tâm lý
                                        pain_point = lead.get('pain_point', 'tìm túi xách đẹp giá tốt')
                                        desire = lead.get('desire', 'muốn có túi xách sang chảnh')
                                        insight = lead.get('insight', '')
                                        post_structure = lead.get('post_structure', 'Hook -> Story -> Solution -> CTA')

                                        promo_prompt = (
                                            f"Bạn là copywriter chuyên viết bài đăng Facebook về TÚI XÁCH cho Lolishop.\n\n"
                                            f"=== BỐI CẢNH ===\n"
                                            f"Nhóm Facebook: {target.get('target_name')}\n"
                                            f"Tâm lý khách hàng trong nhóm: Pain point = '{pain_point}', Mong muốn = '{desire}'\n"
                                            f"Cấu trúc bài: {post_structure}\n\n"
                                            f"=== NHIỆM VỤ ===\n"
                                            f"Viết một bài đăng Facebook HẤP DẪN về TÚI XÁCH tại Lolishop theo cấu trúc:\n"
                                            f"• HOOK: Câu mở đầu chạm đúng tâm lý '{pain_point}' - phải gây tò mò, muốn đọc tiếp.\n"
                                            f"• STORY: 1-2 câu đồng cảm, kể trải nghiệm thật về việc sắm túi.\n"
                                            f"• SOLUTION: Giới thiệu túi xách Lolishop (da thật/canvas/da PU) là giải pháp hoàn hảo.\n"
                                            f"• CTA: Kêu gọi mạnh - click link xem ngay, số lượng có hạn, deal hôm nay.\n"
                                            f"• LINK BẮT BUỘC ở cuối: {bio_link}\n\n"
                                            f"QUY TẮC:\n"
                                            f"- Viết về TÚI XÁCH, không phải sản phẩm khác.\n"
                                            f"- Tone: Tự nhiên, thân thiện, xưng 'mình/chị', KHÔNG lộ liễu bán hàng.\n"
                                            f"- Có emoji hợp lý (👜 🛍️ ✨ 🔥).\n"
                                            f"- Dưới 400 ký tự.\n"
                                            f"- Link {bio_link} BẮT BUỘC xuất hiện ở cuối bài.\n"
                                            f"Chỉ trả về nội dung bài viết, không thêm gì khác."
                                        )

                                        if api_key:
                                            promo_content = call_gemini(api_key, promo_prompt)
                                        else:
                                            promo_content = (
                                                f"👜 Chị em ơi! Đang tìm túi xách đẹp mà không biết mua ở đâu uy tín?\n"
                                                f"Mình vừa sắm được chiếc túi tại Lolishop - da thật, form cứng cáp, giá siêu ổn 🥰\n"
                                                f"Còn nhiều mẫu hot đang sale nè, vào xem ngay trước khi hết:\n"
                                                f"👉 {bio_link}"
                                            )

                                        # Đảm bảo link luôn có trong bài
                                        if bio_link not in promo_content:
                                            promo_content += f"\n👉 {bio_link}"

                                        promo_post_id = 'post_promo_' + str(uuid.uuid4())[:8]
                                        database.save_post(
                                            post_id=promo_post_id,
                                            account_id=lite_acc['id'],
                                            type_='group',
                                            target_id=group_id,
                                            content=promo_content,
                                            media=[],
                                            scheduled_at=datetime.now().isoformat()
                                        )
                                        print(f"[InsightsPost] ✅ Đã lên lịch bài TÚI XÁCH vào nhóm {target.get('target_name')} | {promo_post_id}")
                                        try:
                                            token = settings.get('telegram_token')
                                            chat_id = settings.get('telegram_chat_id')
                                            msg2 = f"🚀 <b>ĐÃ LÊN LỊCH ĐĂNG BÀI TÚI XÁCH LOLISHOP!</b>\n\n"
                                            msg2 += f"👥 <b>Nhóm:</b> {target.get('target_name')}\n"
                                            msg2 += f"🎯 <b>Nhắm vào:</b> {pain_point}\n\n"
                                            msg2 += f"📝 <b>Nội dung bài:</b>\n<i>{promo_content[:300]}</i>"
                                            telegram_bot.send_telegram_message(token, chat_id, msg2)
                                        except Exception:
                                            pass
                                except Exception as post_err:
                                    print(f"[InsightsPost] Lỗi tạo bài quảng cáo: {post_err}")
                            else:
                                log_msg = res.get('log') if isinstance(res, dict) else str(res)
                                print(f"[InsightsComment] Lỗi bình luận: {log_msg}")
                    except Exception as e_comment:
                        print(f"[InsightsComment] Lỗi luồng tự động bình luận: {e_comment}")
            for p in new_posts:
                database.save_scanned_post(p['url'])
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
                
            # [DISABLED] Auto-Discovery: Tắt tự động tìm nhóm mới để tập trung vào nhóm túi xách đã chọn
            # if random.random() < 0.10:
            #     global_target = next((t for t in active_targets if t['target_url'] == 'global'), None)
            #     if global_target:
            #         keywords_list = [k.strip() for k in global_target['niche_keywords'].split(',') if k.strip()]
            #         if keywords_list:
            #             kw = random.choice(keywords_list)
            #             if kw.lower() not in ['tất cả', 'all']:
            #                 acc = random.choice(active_accounts)
            #                 automation.discover_new_groups(acc['cookie'], kw, limit=3)
            
            settings = database.get_settings()
            max_workers = int(settings.get('insight_max_workers', 3))
            max_workers = max(1, min(max_workers, len(active_accounts)))
            
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


def auto_seed_worker():
    print("[Seeder] Auto-seed worker started.")
    while True:
        try:
            import automation
            import telegram_bot
            import random
            
            # Step 1: Find unseeded posts to leave comments
            unseeded_posts = database.get_unseeded_posts()
            if unseeded_posts:
                accounts = [a for a in database.get_accounts() if a['status'] == 'active' and a.get('cookie')]
                if len(accounts) >= 1:
                    for post in unseeded_posts:
                        lite_account_id = post['account_id']
                        # Find a different account to be the VIP (seeder), fallback to self
                        possible_vips = [a for a in accounts if a['id'] != lite_account_id]
                        if not possible_vips:
                            possible_vips = accounts
                        if possible_vips:
                            vip_account = random.choice(possible_vips)
                            
                            # Generate a seeding comment using G4F
                            is_self = (vip_account['id'] == lite_account_id)
                            if is_self:
                                prompt = (
                                    f"Bài đăng của tôi:\n{post['content']}\n\n"
                                    f"Hãy viết một câu bình luận (comment) thật ngắn để tự đẩy (bump/chấm/up) bài viết của mình lên đầu trang. "
                                    f"Ví dụ: 'Sản phẩm vẫn còn nhé mọi người', 'Up cho ngày mới', hoặc các icon chấm. "
                                    f"Chỉ trả về nội dung câu bình luận, không cần giải thích gì thêm."
                                )
                            else:
                                prompt = (
                                    f"Bạn là một người chuyên săn sale (Gen Z). Đọc bài đăng sau:\n"
                                    f"Nội dung:\n{post['content']}\n\n"
                                    f"Hãy áp dụng kỹ năng **Marketing Psychology (Social Proof / Chim mồi)** để viết 1 câu bình luận (dưới 15 chữ), "
                                    f"khen ngợi một cách thực tế hoặc tạo hiệu ứng FOMO khiến người khác cũng muốn mua (ví dụ: 'ui xịn dã man', 'mã này đang hot chốt lẹ', 'ko mua tiếc lắm lắm nè'). "
                                    f"Giọng điệu tự nhiên, dùng 1-2 icon, KHÔNG hashtag, KHÔNG xưng hô trang trọng."
                                )
                            
                            try:
                                vip_comment = automation.call_g4f(prompt)
                            except Exception:
                                vip_comment = "Sản phẩm vẫn còn, ib nhé!" if is_self else "Sản phẩm này nhìn xịn quá, ib mình với nha!"
                            
                            if vip_comment:
                                print(f"[Seeder] {vip_account['name']} is seeding post {post['id']}...")
                                seed_id = database.create_seed_log(post['id'], post['post_url'], vip_account['id'], lite_account_id)
                                
                                res = automation.seed_comment_on_post(vip_account['cookie'], post['post_url'], vip_comment)
                                if res['success']:
                                    database.update_seed_log(seed_id, 'pending_reply', vip_comment=vip_comment)
                                    print(f"[Seeder] Successfully left comment: {vip_comment}")
                                    try:
                                        token = settings.get('telegram_token')
                                        chat_id = settings.get('telegram_chat_id')
                                        msg = f"🔥 <b>ĐÃ THẢ CHIM MỒI THÀNH CÔNG!</b>\n\n"
                                        msg += f"👤 <b>Nick mồi:</b> {vip_account['name']}\n"
                                        msg += f"💬 <b>Bình luận:</b> {vip_comment}\n"
                                        telegram_bot.send_telegram_message(token, chat_id, msg)
                                    except Exception:
                                        pass
                                else:
                                    database.update_seed_log(seed_id, 'failed')
                                    print(f"[Seeder] Failed to leave comment: {res['log']}")
                                time.sleep(10)
                                
            # Step 2: Find pending replies (so the original author replies to the VIP comment)
            pending_replies = database.get_pending_reply_seeds()
            if pending_replies:
                for seed in pending_replies:
                    if seed.get('vip_account_id') == seed['lite_account_id']:
                        database.update_seed_log(seed['id'], 'completed', lite_reply="Self-bumped")
                        continue
                        
                    lite_acc = database.get_account(seed['lite_account_id'])
                    if lite_acc and lite_acc.get('cookie'):
                        # Generate reply using Gemini
                        post = database.get_post(seed['post_id'])
                        post_content = post['content'] if post else ""
                        
                        prompt = (
                            f"Bạn là chủ shop đang chốt sale. Khách hàng vừa comment vào bài của bạn:\n"
                            f"Bài đăng:\n{post_content}\n\n"
                            f"Comment khách:\n{seed['vip_comment']}\n\n"
                            f"Hãy áp dụng **Copywriting & Scarcity (Khan hiếm)** để viết 1 câu trả lời cực ngắn (dưới 15 chữ) kèm Call To Action mạnh. "
                            f"Ví dụ: 'Dạ mẫu này em còn đúng 2 chiếc, check inbox em gửi ảnh nhen!', 'Giá sale áp dụng nốt hôm nay, check ib em chốt nha!' "
                            f"Chỉ trả về nội dung trả lời, không dùng hashtag."
                        )
                        try:
                            lite_reply = automation.call_g4f(prompt)
                        except Exception:
                            lite_reply = "Cảm ơn bạn đã quan tâm! Kiểm tra inbox nha bạn."
                        if lite_reply:
                            print(f"[Seeder] {lite_acc['name']} is replying to seed comment on post {seed['post_id']}...")
                            res = automation.seed_reply_to_comment(lite_acc['cookie'], seed['post_url'], lite_reply)
                            if res['success']:
                                database.update_seed_log(seed['id'], 'completed', lite_reply=lite_reply)
                                print(f"[Seeder] Successfully replied: {lite_reply}")
                                try:
                                    token = settings.get('telegram_token')
                                    chat_id = settings.get('telegram_chat_id')
                                    msg = f"💸 <b>ĐÃ CHỐT SALE THÀNH CÔNG!</b>\n\n"
                                    msg += f"👤 <b>Chủ shop:</b> {lite_acc['name']}\n"
                                    msg += f"💬 <b>Trả lời:</b> {lite_reply}\n"
                                    telegram_bot.send_telegram_message(token, chat_id, msg)
                                except Exception:
                                    pass
                            else:
                                # We can retry later or mark failed, let's mark failed to avoid infinite loop
                                database.update_seed_log(seed['id'], 'failed_reply', lite_reply=lite_reply)
                                print(f"[Seeder] Failed to reply: {res['log']}")
                            time.sleep(10)

        except Exception as e:
            print(f"[Seeder Worker] Error: {e}")
        time.sleep(180) # Check every 3 minutes

def auto_shopee_post_worker():
    print("[AutoShopee] Auto Shopee FB Poster worker started.")
    import sys
    sys.path.append(r'C:\Users\TOSHIBA\.gemini\antigravity\scratch')
    import time
    while True:
        try:
            import auto_fb_scheduler
            print("[AutoShopee] Running automated Shopee FB post queue check...")
            auto_fb_scheduler.run_scheduler()
        except Exception as e:
            print(f"[AutoShopee Worker] Error: {e}")
        # Wait 4 hours before checking next product
        time.sleep(14400)

threading.Thread(target=auto_shopee_post_worker, daemon=True).start()

threading.Thread(target=scheduler_worker, daemon=True).start()
threading.Thread(target=engagement_worker, daemon=True).start()
threading.Thread(target=autolike_worker, daemon=True).start()
threading.Thread(target=autobump_worker, daemon=True).start()
threading.Thread(target=autofeed_worker, daemon=True).start()
threading.Thread(target=shopee_folder_worker, daemon=True).start()
threading.Thread(target=tunnel_worker, daemon=True).start()
threading.Thread(target=insight_worker, daemon=True).start()
threading.Thread(target=auto_seed_worker, daemon=True).start()

# Start HAME Telegram Bot
try:
    from telegram_bot import start_telegram_bot
    start_telegram_bot()
except Exception as tele_init_err:
    print(f"[TeleBot] Failed to start Telegram bot: {tele_init_err}")

# ─────────────────────────────────────────
# STATIC & INDEX
# ─────────────────────────────────────────
@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/api/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ─────────────────────────────────────────
# ACCOUNTS
# ─────────────────────────────────────────
@app.route('/api/accounts', methods=['GET'])
def api_get_accounts():
    return jsonify(database.get_accounts())

@app.route('/api/accounts', methods=['POST'])
def api_save_account():
    data = request.json
    acc_id = data.get('id') or 'acc_' + str(uuid.uuid4())[:8]
    cookie_val = data.get('cookie', '').strip()
    username_val = data.get('username', '').strip()
    password_val = data.get('password', '').strip()
    two_factor_key_val = data.get('two_factor_key', '').strip()
    
    if not cookie_val and not (username_val and password_val):
        return jsonify({'error': 'Cookie hoặc thông tin đăng nhập (Tài khoản & Mật khẩu) không được để trống.'}), 400
        
    old_acc = database.get_account(acc_id)
    cookie_changed = False
    if old_acc and cookie_val and old_acc.get('cookie') != cookie_val:
        cookie_changed = True
        
    acc = database.save_account(
        account_id=acc_id,
        name=data.get('name', 'New Account'),
        cookie=cookie_val,
        status=data.get('status', 'active'),
        platform=data.get('platform', 'facebook'),
        username=username_val,
        password=password_val,
        two_factor_key=two_factor_key_val,
        team_role=data.get('team_role', 'team_poster')
    )
    
    if cookie_changed:
        reset_count = database.reset_failed_posts_due_to_cookie(acc_id)
        if reset_count > 0:
            print(f"[System] Resetted {reset_count} failed posts for account {acc_id} due to new cookie.")
            
    return jsonify(acc)

@app.route('/api/accounts/<acc_id>/auto-login', methods=['POST'])
def api_account_auto_login(acc_id):
    account = database.get_account(acc_id)
    if not account:
        return jsonify({'error': 'Không tìm thấy tài khoản.'}), 404
    
    username = account.get('username')
    password = account.get('password')
    two_factor_key = account.get('two_factor_key')
    
    if not username or not password:
        return jsonify({'error': 'Tài khoản chưa cấu hình thông tin đăng nhập (Email & Mật khẩu).'}), 400
        
    # Update status to 'logging_in'
    database.save_account(
        account_id=account['id'],
        name=account['name'],
        cookie=account['cookie'],
        status='logging_in',
        platform=account['platform'],
        username=username,
        password=password,
        two_factor_key=two_factor_key
    )
    
    res = auto_login_facebook(username, password, two_factor_key)
    if res['success']:
        new_cookie = res['cookie']
        database.save_account(
            account_id=account['id'],
            name=account['name'],
            cookie=new_cookie,
            status='active',
            platform=account['platform'],
            username=username,
            password=password,
            two_factor_key=two_factor_key
        )
        return jsonify({'success': True, 'message': 'Đăng nhập thành công và cập nhật Cookie mới.'})
    else:
        database.save_account(
            account_id=account['id'],
            name=account['name'],
            cookie=account['cookie'],
            status='expired',
            platform=account['platform'],
            username=username,
            password=password,
            two_factor_key=two_factor_key
        )
        return jsonify({'error': f"Đăng nhập thất bại: {res.get('log')}"}), 500

@app.route('/api/accounts/<acc_id>', methods=['DELETE'])
def api_delete_account(acc_id):
    database.delete_account(acc_id)
    return jsonify({'success': True})

# ─────────────────────────────────────────
# MULTI-BROWSER LAUNCHER
# ─────────────────────────────────────────
@app.route('/api/browser/launch/<acc_id>', methods=['POST'])
def api_launch_single_browser(acc_id):
    import multibrowser_engine
    res = multibrowser_engine.launch_account_browser(acc_id)
    return jsonify(res)

@app.route('/api/browser/launch-all', methods=['POST'])
def api_launch_all_browsers():
    import multibrowser_engine
    team_role = request.args.get('team_role')
    res = multibrowser_engine.launch_all_browsers(team_role=team_role)
    return jsonify(res)

# ─────────────────────────────────────────
# LINK ANALYZER
# ─────────────────────────────────────────
@app.route('/api/analyze-link', methods=['POST'])
def api_analyze_link():
    import re
    data = request.json or {}
    url = data.get('url', '').strip()
    account_id = data.get('account_id', '')
    
    if not url:
        return jsonify({'error': 'Vui lòng cung cấp đường link Facebook.'}), 400
        
    settings = database.get_settings()
    api_key = settings.get('gemini_api_key', '').strip()
    if not api_key:
        return jsonify({'error': 'Vui lòng cấu hình Gemini API Key trước trong phần Cấu hình.'}), 400
        
    # Get account name to customize the response
    account_name = "Tài khoản của tôi"
    if account_id:
        acc = database.get_account(account_id)
        if acc:
            account_name = acc.get('name', 'Tài khoản của tôi')
            
    # Simple regex to classify the URL
    link_type = "unknown"
    link_type_vi = "Liên kết Facebook"
    target_id = ""
    
    # 1. Check Group
    if "groups/" in url:
        link_type = "group"
        link_type_vi = "Nhóm Facebook"
        match = re.search(r'groups/([^/?#\s]+)', url)
        if match:
            target_id = match.group(1)
    # 2. Check Post/Permalink
    elif "/posts/" in url or "permalink" in url or "story_fbid" in url:
        link_type = "post"
        link_type_vi = "Bài viết Facebook"
    # 3. Check Profile/Page
    elif "facebook.com/" in url:
        link_type = "page_or_profile"
        link_type_vi = "Trang cá nhân / Fanpage"
        clean_url = url.split('?')[0].split('#')[0].rstrip('/')
        parts = clean_url.split('/')
        if parts:
            last = parts[-1]
            if last not in ["facebook.com", "fb.com", ""]:
                target_id = last
                if "profile.php" in last:
                    try:
                        from urllib.parse import urlparse, parse_qs
                        parsed = urlparse(url)
                        q = parse_qs(parsed.query)
                        if 'id' in q:
                            target_id = q['id'][0]
                    except:
                        pass
                        
    prompt = (
        f"Hãy phân tích đường link Facebook sau đây:\n"
        f"URL: {url}\n"
        f"Loại link hệ thống nhận diện sơ bộ: {link_type_vi} (Mã: {link_type}, Target ID gợi ý: '{target_id}')\n\n"
        f"Tên tài khoản hoặc thương hiệu của chúng tôi: '{account_name}'\n\n"
        f"Hãy thực hiện bóc tách các TÁC NHÂN (Actors) trên trang/liên kết này và ĐỀ XUẤT các hành động tự động hóa cụ thể để phát triển trang của chúng tôi. "
        f"Hãy trả về kết quả dưới dạng cấu trúc JSON thô duy nhất (KHÔNG ĐƯỢC CHÈN MARKDOWN ```json hay ```, KHÔNG CHỨA BẤT KỲ VĂN BẢN NÀO NGOÀI JSON) theo cấu trúc mẫu sau:\n"
        f"{{\n"
        f"  \"link_type_vi\": \"Nhóm Facebook / Trang đối thủ...\",\n"
        f"  \"actors\": [\n"
        f"    {{\"name\": \"Tên tác nhân\", \"description\": \"Mô tả chi tiết tác nhân này làm gì trên trang\", \"role\": \"target hoặc lead\"}}\n"
        f"  ],\n"
        f"  \"proposals\": [\n"
        f"    {{\n"
        f"      \"title\": \"Tiêu đề hành động đề xuất\",\n"
        f"      \"description\": \"Mô tả cách hành động này giúp phát triển trang của chúng tôi\",\n"
        f"      \"action_type\": \"autolike hoặc post hoặc auto_reply\",\n"
        f"      \"action_data\": {{}},\n"
        f"      \"btn_text\": \"Nhãn nút bấm hành động (ví dụ: Kích hoạt Auto-Like ngay)\"\n"
        f"    }}\n"
        f"  ]\n"
        f"}}\n\n"
        f"LƯU Ý QUAN TRỌNG VỀ PHẦN ACTION_DATA CHO TỪNG LOẠI ACTION_TYPE:\n"
        f"1. Nếu action_type là \"autolike\": action_data PHẢI chứa: \n"
        f"   - \"target_url\": link trang/nhóm đối thủ.\n"
        f"   - \"target_name\": tên trang/nhóm gợi nhớ.\n"
        f"   - \"auto_comment\": 1 (nếu khuyên bình luận chéo) hoặc 0.\n"
        f"   - \"comment_style\": \"AI\" hoặc \"spintax\".\n"
        f"   - \"comment_text\": mẫu câu nếu style là spintax.\n"
        f"2. Nếu action_type là \"post\": action_data PHẢI chứa: \n"
        f"   - \"type\": \"group\" (nếu là nhóm) hoặc \"page\" (nếu là page) hoặc \"profile\".\n"
        f"   - \"target_id\": ID/username đích.\n"
        f"   - \"content\": nội dung nháp gợi ý viết bằng AI để thu hút tương tác ở đó.\n"
        f"3. Nếu action_type là \"auto_reply\": action_data PHẢI chứa:\n"
        f"   - \"post_url\": link bài viết cụ thể để quét bình luận.\n"
        f"Hãy đảm bảo tất cả các trường dữ liệu đều đúng cấu trúc để giao diện có thể tự động điền form cho người dùng. Phản hồi thô JSON hoàn chỉnh bằng tiếng Việt."
    )
    
    system_instruction = (
        "Bạn là chuyên gia tự động hóa tiếp thị và tối ưu hóa Facebook. Nhiệm vụ của bạn là nhận đường link Facebook từ người dùng, "
        "phân tích các đối tượng/tác nhân trên liên kết đó (ví dụ: Admin nhóm, thành viên đăng bài, người bình luận) và đề xuất các hành động "
        "tương tác tự động hóa tối ưu nhất (Auto-Like, Auto-Comment, Auto-Reply, Posting) để giúp trang/profile của người dùng phát triển nhanh nhất. "
        "Hãy phản hồi cấu trúc JSON chuẩn."
    )
    
    try:
        raw_res = call_gemini(api_key, prompt, system_instruction=system_instruction)
        raw_res = raw_res.strip()
        if raw_res.startswith("```json"):
            raw_res = raw_res[7:]
        if raw_res.startswith("```"):
            raw_res = raw_res[3:]
        if raw_res.endswith("```"):
            raw_res = raw_res[:-3]
        raw_res = raw_res.strip()
        
        parsed = json.loads(raw_res)
        return jsonify(parsed)
    except Exception as e:
        print(f"[LinkAnalyzer] Error running link analysis: {e}")
        fallback = {
            "link_type_vi": link_type_vi,
            "actors": [
                {"name": "Đối tượng trên trang", "description": "Không thể phân tích sâu do lỗi kết nối AI hoặc lỗi cú pháp.", "role": "target"}
            ],
            "proposals": []
        }
        
        if link_type == "group" and target_id:
            fallback["proposals"].append({
                "title": "Tự động thả tim & bình luận nhóm",
                "description": f"Chạy chiến dịch tương tác tự động trên nhóm ID {target_id}.",
                "action_type": "autolike",
                "action_data": {
                    "target_url": url,
                    "target_name": f"Nhóm {target_id}",
                    "auto_comment": 1,
                    "comment_style": "AI"
                },
                "btn_text": "Kích hoạt Auto-Like ngay"
            })
            fallback["proposals"].append({
                "title": "Soạn bài viết vào nhóm",
                "description": f"Lên lịch bài viết nháp đăng trực tiếp vào nhóm ID {target_id}.",
                "action_type": "post",
                "action_data": {
                    "type": "group",
                    "target_id": target_id,
                    "content": "Bài viết chia sẻ kiến thức..."
                },
                "btn_text": "Soạn bài đăng nhóm"
            })
        elif link_type == "page_or_profile" and target_id:
            fallback["proposals"].append({
                "title": "Tương tác với Fanpage",
                "description": f"Tự động thả tim và bình luận chéo trên trang {target_id}.",
                "action_type": "autolike",
                "action_data": {
                    "target_url": url,
                    "target_name": f"Trang {target_id}",
                    "auto_comment": 1,
                    "comment_style": "AI"
                },
                "btn_text": "Kích hoạt Auto-Like ngay"
            })
        elif link_type == "post":
            fallback["proposals"].append({
                "title": "Tự động phản hồi bình luận bài viết",
                "description": "Quét và phản hồi tự động tất cả bình luận trên bài viết này.",
                "action_type": "auto_reply",
                "action_data": {
                    "post_url": url
                },
                "btn_text": "Cài đặt Auto-Reply ngay"
            })
            
        return jsonify(fallback)

# ─────────────────────────────────────────
# POSTS
# ─────────────────────────────────────────
@app.route('/api/posts', methods=['GET'])
def api_get_posts():
    return jsonify(database.get_posts())

def parse_target_line(line):
    line = line.strip()
    if not line:
        return None
    
    # Prefix check
    if line.lower().startswith('group:'):
        return {'type': 'group', 'target_id': line[6:].strip()}
    if line.lower().startswith('page:'):
        return {'type': 'page', 'target_id': line[5:].strip()}
        
    # URL check
    if 'facebook.com' in line or 'fb.com' in line:
        if '/groups/' in line:
            import re
            match = re.search(r'groups/([^/?#\s]+)', line)
            if match:
                return {'type': 'group', 'target_id': match.group(1)}
        else:
            clean_url = line.split('?')[0].split('#')[0].rstrip('/')
            parts = clean_url.split('/')
            if parts:
                last = parts[-1]
                if last not in ["facebook.com", "fb.com", ""]:
                    target_id = last
                    if "profile.php" in last:
                        try:
                            from urllib.parse import urlparse, parse_qs
                            parsed = urlparse(line)
                            q = parse_qs(parsed.query)
                            if 'id' in q:
                                target_id = q['id'][0]
                        except:
                            pass
                    return {'type': 'page', 'target_id': target_id}
                    
    # Raw digits vs string
    if line.isdigit():
        return {'type': 'group', 'target_id': line}
    else:
        return {'type': 'page', 'target_id': line}

def trigger_autojoin_for_targets(account_id, targets_input):
    """
    Tự động khởi chạy luồng chạy ngầm để tham gia các nhóm mục tiêu nếu tài khoản chưa tham gia.
    """
    account = database.get_account(account_id)
    if not account or account.get('platform') == 'threads':
        return
        
    group_urls = []
    
    def add_group_target(t_id):
        if not t_id or t_id == 'me':
            return
        t_id = str(t_id).strip()
        if t_id.startswith('http://') or t_id.startswith('https://'):
            if '/groups/' in t_id:
                if t_id not in group_urls:
                    group_urls.append(t_id)
        else:
            url = f"https://www.facebook.com/groups/{t_id}/"
            if url not in group_urls:
                group_urls.append(url)

    if isinstance(targets_input, list):
        for t in targets_input:
            if isinstance(t, dict):
                t_type = t.get('type', 'group')
                t_id = t.get('target_id', '')
                if t_type == 'group':
                    add_group_target(t_id)
            elif isinstance(t, str):
                parsed = parse_target_line(t)
                if parsed and parsed.get('type') == 'group':
                    add_group_target(parsed.get('target_id'))
    elif isinstance(targets_input, str):
        if targets_input.startswith('list_'):
            target_list = database.get_target_list(targets_input)
            if target_list:
                raw_targets = target_list.get('targets', '')
                for line in raw_targets.split('\n'):
                    parsed = parse_target_line(line)
                    if parsed and parsed.get('type') == 'group':
                        add_group_target(parsed.get('target_id'))
        else:
            parsed = parse_target_line(targets_input)
            if parsed and parsed.get('type') == 'group':
                add_group_target(parsed.get('target_id'))
                
    if not group_urls:
        return
        
    def run_autojoin():
        print(f"[AutoJoin-Trigger] Khởi động tham gia ngầm {len(group_urls)} nhóm cho tài khoản {account['name']}...")
        try:
            urls_str = "\n".join(group_urls)
            auto_join_facebook_groups(
                account_id=account['id'],
                account_cookie=account['cookie'],
                account_name=account['name'],
                group_inputs=urls_str,
                keyword=None,
                limit=len(group_urls),
                delay=10,
                answer_questions=True
            )
            print(f"[AutoJoin-Trigger] Hoàn thành tiến trình tham gia ngầm cho tài khoản {account['name']}.")
        except Exception as e:
            print(f"[AutoJoin-Trigger] Lỗi khi tự động tham gia nhóm chạy ngầm: {e}")
            
    threading.Thread(target=run_autojoin, daemon=True).start()

@app.route('/api/posts', methods=['POST'])
def api_save_post():
    post_id = request.form.get('id') or 'post_' + str(uuid.uuid4())[:8]
    account_id = request.form.get('account_id')
    if not account_id:
        return jsonify({'error': 'Vui lòng chọn tài khoản.'}), 400

    media_list = []
    existing = request.form.get('existing_media')
    if existing:
        try: media_list = json.loads(existing)
        except: pass
    for f in request.files.getlist('media'):
        if f and f.filename:
            fname = str(uuid.uuid4())[:8] + "_" + f.filename
            f.save(os.path.join(UPLOAD_FOLDER, fname))
            media_list.append(fname)

    scheduled_at = request.form.get('scheduled_at') or datetime.now().isoformat()
    first_comment = request.form.get('first_comment')
    
    target_list_id = request.form.get('target_list_id')
    redirect_url = request.form.get('redirect_url')
    
    # Process redirect link if provided
    if redirect_url:
        if not media_list:
            return jsonify({'error': 'Vui lòng chọn 1 hình ảnh để làm ảnh bìa clickable.'}), 400
            
        settings = database.get_settings()
        public_domain = settings.get('public_domain', '').strip()
        if not public_domain:
            return jsonify({'error': 'Bạn cần cấu hình "Tên miền công khai" trong tab Cấu hình trước khi đăng ảnh clickable.'}), 400
            
        redirect_id = 'r_' + str(uuid.uuid4())[:8]
        image_file = media_list[0]
        title = request.form.get('redirect_title') or 'Xem chi tiết sản phẩm'
        description = request.form.get('redirect_desc') or 'Click để truy cập liên kết'
        
        # Save redirect link to database
        database.save_redirect(redirect_id, redirect_url, image_file, title, description)
        
        # Format the new content
        orig_content = request.form.get('content', '')
        redirect_link = f"{public_domain}/r/{redirect_id}"
        content_to_save = f"{orig_content}\n\n{redirect_link}" if orig_content else redirect_link
        
        # Empty the media list so the posting worker does not upload the image file to FB
        media_list = []
    else:
        content_to_save = request.form.get('content', '')

    if target_list_id:
        target_list = database.get_target_list(target_list_id)
        if not target_list:
            return jsonify({'error': 'Không tìm thấy danh sách mục tiêu.'}), 404
            
        raw_targets = target_list.get('targets', '')
        parsed_targets = []
        for line in raw_targets.split('\n'):
            parsed = parse_target_line(line)
            if parsed:
                parsed_targets.append(parsed)
                
        if not parsed_targets:
            return jsonify({'error': 'Danh sách mục tiêu rỗng hoặc không hợp lệ.'}), 400
            
        created_posts = []
        bulk_group_id = 'bulk_' + str(uuid.uuid4())[:8] if len(parsed_targets) > 1 else None
        
        for idx, t in enumerate(parsed_targets):
            cur_post_id = post_id if idx == 0 else 'post_' + str(uuid.uuid4())[:8]
            post = database.save_post(
                cur_post_id, account_id, t['type'],
                t['target_id'], content_to_save,
                media_list, scheduled_at, bulk_group_id=bulk_group_id,
                platform=request.form.get('platform', 'facebook'),
                first_comment=first_comment
            )
            created_posts.append(post)
            
        trigger_autojoin_for_targets(account_id, parsed_targets)
        return jsonify(created_posts[0])

    post = database.save_post(
        post_id, account_id, request.form.get('type', 'profile'),
        request.form.get('target_id', 'me'), content_to_save,
        media_list, scheduled_at, bulk_group_id=request.form.get('bulk_group_id'),
        platform=request.form.get('platform', 'facebook'),
        first_comment=first_comment
    )
    trigger_autojoin_for_targets(account_id, [{'type': request.form.get('type', 'profile'), 'target_id': request.form.get('target_id', 'me')}])
    return jsonify(post)

@app.route('/api/posts/<post_id>/publish', methods=['POST'])
def api_publish_now(post_id):
    post = database.get_post(post_id)
    if not post: return jsonify({'error': 'Không tìm thấy bài viết.'}), 404
    account = database.get_account(post['account_id'])
    if not account: return jsonify({'error': 'Không tìm thấy tài khoản.'}), 400
    database.update_post_status(post_id, 'posting', 'Đang đăng ngay...')
    def run():
        if account.get('platform') == 'threads':
            res = publish_threads_post(account['cookie'], post['content'], post['media'], post['id'], post.get('first_comment'))
        else:
            res = publish_post(account['cookie'], post['type'], post['target_id'], post['content'], post['media'], post['id'], post.get('first_comment'))
        status = res.get('status', 'posted') if res['success'] else 'failed'
        database.update_post_status(post_id, status, res['log'], res['screenshot'], res.get('post_url'))
        if status == 'pending_approval' and post['type'] == 'group':
            database.increment_group_pending_count(post['target_id'])
    threading.Thread(target=run).start()
    return jsonify({'success': True})

@app.route('/api/posts/<post_id>', methods=['PUT'])
def api_update_post_details(post_id):
    """
    Updates details of a post, with optional cascading update to similar pending posts.
    """
    data = request.json or {}
    content = data.get('content', '').strip()
    scheduled_at = data.get('scheduled_at', '').strip()
    post_type = data.get('type', 'profile').strip()
    target_id = data.get('target_id', 'me').strip()
    first_comment = data.get('first_comment', '').strip()
    update_similar = data.get('apply_to_similar', False)
    
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM posts WHERE id=?", (post_id,))
    orig_row = cursor.fetchone()
    if not orig_row:
        conn.close()
        return jsonify({'error': 'Post not found'}), 404
        
    orig_content = orig_row[0]
    
    # Update current post
    cursor.execute(
        "UPDATE posts SET content=?, scheduled_at=?, type=?, target_id=?, first_comment=? WHERE id=?",
        (content, scheduled_at, post_type, target_id, first_comment, post_id)
    )
    
    updated_count = 1
    
    # Cascade to similar pending posts if requested
    if update_similar and orig_content:
        cursor.execute(
            "UPDATE posts SET content=?, first_comment=? WHERE content=? AND status='pending' AND id != ?",
            (content, first_comment, orig_content, post_id)
        )
        updated_count += cursor.rowcount
        
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': f'Cập nhật thành công {updated_count} bài đăng.'
    })

@app.route('/api/posts/<post_id>', methods=['DELETE'])
def api_delete_post(post_id):
    database.delete_post(post_id)
    return jsonify({'success': True})

@app.route('/api/posts/deleted', methods=['GET'])
def api_get_deleted_posts():
    posts = database.get_deleted_posts()
    return jsonify(posts)

@app.route('/api/posts/<post_id>/restore', methods=['POST'])
def api_restore_post(post_id):
    database.restore_post(post_id)
    return jsonify({'success': True})

@app.route('/api/posts/<post_id>/permanent', methods=['DELETE'])
def api_delete_post_permanent(post_id):
    post = database.get_post(post_id)
    if post:
        all_posts = database.get_posts()
        for mf in post.get('media', []):
            other_uses = any(p['id'] != post_id and mf in p.get('media', []) for p in all_posts)
            if not other_uses:
                try: os.remove(os.path.join(UPLOAD_FOLDER, mf))
                except: pass
        if post.get('screenshot'):
            other_ss_uses = any(p['id'] != post_id and p.get('screenshot') == post['screenshot'] for p in all_posts)
            if not other_ss_uses:
                try: os.remove(os.path.join(UPLOAD_FOLDER, post['screenshot']))
                except: pass
    database.delete_post_permanently(post_id)
    return jsonify({'success': True})

@app.route('/api/posts/bulk-delete', methods=['POST'])
def api_bulk_delete_posts():
    data = request.get_json() or {}
    ids = data.get('ids', [])
    for post_id in ids:
        database.delete_post(post_id)
    return jsonify({'success': True})

@app.route('/api/posts/bulk-restore', methods=['POST'])
def api_bulk_restore_posts():
    data = request.get_json() or {}
    ids = data.get('ids', [])
    for post_id in ids:
        database.restore_post(post_id)
    return jsonify({'success': True})

@app.route('/api/posts/bulk-permanent', methods=['POST'])
def api_bulk_permanent_posts():
    data = request.get_json() or {}
    ids = data.get('ids', [])
    all_posts = database.get_posts()
    for post_id in ids:
        post = database.get_post(post_id)
        if post:
            for mf in post.get('media', []):
                other_uses = any(p['id'] not in ids and mf in p.get('media', []) for p in all_posts)
                if not other_uses:
                    try: os.remove(os.path.join(UPLOAD_FOLDER, mf))
                    except: pass
            if post.get('screenshot'):
                other_ss_uses = any(p['id'] not in ids and p.get('screenshot') == post['screenshot'] for p in all_posts)
                if not other_ss_uses:
                    try: os.remove(os.path.join(UPLOAD_FOLDER, post['screenshot']))
                    except: pass
        database.delete_post_permanently(post_id)
    return jsonify({'success': True})

# ─────────────────────────────────────────
# BULK POSTING
# ─────────────────────────────────────────
@app.route('/api/bulk', methods=['GET'])
def api_get_bulk_groups():
    return jsonify(database.get_bulk_groups())

@app.route('/api/bulk', methods=['POST'])
def api_create_bulk():
    """Create a bulk campaign: one content sent to multiple targets."""
    data = request.json
    name = data.get('name', 'Bulk Campaign')
    account_id = data.get('account_id')
    targets = data.get('targets', [])  # List of {type, target_id}
    content = data.get('content', '')
    scheduled_at = data.get('scheduled_at') or datetime.now().isoformat()

    if not account_id or not targets or not content:
        return jsonify({'error': 'Thiếu thông tin: account_id, targets hoặc content.'}), 400

    group_id = 'bulk_' + str(uuid.uuid4())[:8]
    database.save_bulk_group(group_id, name, len(targets))

    created_posts = []
    for t in targets:
        post_id = 'post_' + str(uuid.uuid4())[:8]
        post = database.save_post(post_id, account_id, t.get('type', 'group'),
                                   t.get('target_id', ''), content, [],
                                   scheduled_at, bulk_group_id=group_id)
        created_posts.append(post)

    trigger_autojoin_for_targets(account_id, targets)
    return jsonify({'group_id': group_id, 'posts_created': len(created_posts)})

@app.route('/api/bulk/<group_id>', methods=['DELETE'])
def api_delete_bulk_group(group_id):
    database.delete_bulk_group(group_id)
    return jsonify({'success': True})


# ─────────────────────────────────────────
# TEMPLATES
# ─────────────────────────────────────────
@app.route('/api/templates', methods=['GET'])
def api_get_templates():
    return jsonify(database.get_templates())

@app.route('/api/templates', methods=['POST'])
def api_save_template():
    data = request.json
    tid = data.get('id') or 'tpl_' + str(uuid.uuid4())[:8]
    if not data.get('name') or not data.get('content'):
        return jsonify({'error': 'Tên và nội dung không được để trống.'}), 400
    database.save_template(tid, data['name'], data['content'], data.get('tags', ''))
    return jsonify({'success': True, 'id': tid})

@app.route('/api/templates/<tid>', methods=['DELETE'])
def api_delete_template(tid):
    database.delete_template(tid)
    return jsonify({'success': True})

# ─────────────────────────────────────────
# ENGAGEMENT
# ─────────────────────────────────────────
@app.route('/api/engagement/rules', methods=['GET'])
def api_get_rules():
    return jsonify(database.get_engagement_rules())

@app.route('/api/engagement/rules', methods=['POST'])
def api_save_rule():
    data = request.json
    rid = data.get('id') or 'rule_' + str(uuid.uuid4())[:8]
    if not data.get('reply_text'):
        return jsonify({'error': 'Nội dung phản hồi không được để trống.'}), 400
    rule = database.save_engagement_rule(rid, data.get('keywords', '*'), data['reply_text'], data.get('status', 'active'))
    return jsonify(rule)

@app.route('/api/engagement/rules/<rid>', methods=['DELETE'])
def api_delete_rule(rid):
    database.delete_engagement_rule(rid)
    return jsonify({'success': True})

@app.route('/api/engagement/logs', methods=['GET'])
def api_get_engage_logs():
    return jsonify(database.get_engagement_logs())

@app.route('/api/engagement/scan', methods=['POST'])
def api_manual_scan():
    data = request.json
    account_id = data.get('account_id')
    post_url = data.get('post_url')
    if not account_id or not post_url:
        return jsonify({'error': 'Cần account_id và post_url.'}), 400
    account = database.get_account(account_id)
    if not account: return jsonify({'error': 'Không tìm thấy tài khoản.'}), 404
    rules = [r for r in database.get_engagement_rules() if r['status'] == 'active']
    if not rules: return jsonify({'error': 'Chưa có luật phản hồi nào hoạt động.'}), 400

    def run():
        settings = database.get_settings()
        max_r = int(settings.get('max_replies_per_scan', 5))
        logs = auto_reply_post_comments(account['cookie'], post_url, account['name'], rules, max_r)
        for log in logs:
            database.save_engagement_log(log['id'], log['post_url'], log['commenter_name'],
                                         log['comment_content'], log['reply_content'],
                                         log['status'], log['screenshot'])
    threading.Thread(target=run).start()
    return jsonify({'success': True, 'message': 'Đã kích hoạt quét bình luận trong nền.'})


@app.route('/api/engagement/autofeed', methods=['POST'])
def api_manual_autofeed():
    data = request.json
    account_id = data.get('account_id')
    source = data.get('source', 'groups')
    
    if not account_id:
        return jsonify({'error': 'Thiếu account_id.'}), 400
        
    account = database.get_account(account_id)
    if not account:
        return jsonify({'error': 'Không tìm thấy tài khoản.'}), 404
        
    def run():
        settings = database.get_settings()
        max_posts = int(settings.get('autofeed_max_posts_per_scan', 5))
        comment_style = settings.get('autofeed_engage_style', 'spintax')
        comment_text = settings.get('autofeed_engage_text', '')
        
        print(f"[Manual-AutoFeed] Running auto-feed interaction for account: {account['name']}")
        result = auto_engage_feed_posts(
            account_cookie=account['cookie'],
            account_name=account['name'],
            source=source,
            max_posts=max_posts,
            comment_style=comment_style,
            comment_text=comment_text
        )
        
        if result.get('logs'):
            for log in result['logs']:
                log_id = 'log_' + str(uuid.uuid4())[:8]
                database.save_engagement_log(
                    log_id=log_id,
                    post_url=log['post_url'],
                    commenter_name=log['commenter_name'],
                    comment_content=log['comment_content'],
                    reply_content=log['reply_content'],
                    status=log['status'],
                    screenshot=log.get('screenshot')
                )
        print(f"[Manual-AutoFeed] Finished manual interaction. Log: {result.get('log')}")
        
    threading.Thread(target=run).start()
    return jsonify({'success': True, 'message': 'Đã kích hoạt bình luận dạo bằng chatbot AI trong nền.'})

# ─────────────────────────────────────────
# TARGET LISTS
# ─────────────────────────────────────────
@app.route('/api/target-lists', methods=['GET'])
def api_get_target_lists():
    return jsonify(database.get_target_lists())

@app.route('/api/target-lists', methods=['POST'])
def api_save_target_list():
    data = request.json
    lid = data.get('id') or ('list_' + str(uuid.uuid4())[:8])
    name = data.get('name')
    targets = data.get('targets')
    
    if not name or not targets:
        return jsonify({'error': 'Thiếu tên danh sách hoặc danh sách mục tiêu.'}), 400
        
    result = database.save_target_list(lid, name, targets)
    return jsonify(result)

@app.route('/api/target-lists/<lid>', methods=['DELETE'])
def api_delete_target_list(lid):
    database.delete_target_list(lid)
    return jsonify({'success': True})

def extract_fb_name(url):
    url = url.strip()
    if not url:
        return "Mục tiêu"
    if url.endswith('/'):
        url = url[:-1]
    
    parts = url.split('/')
    if len(parts) > 0:
        last = parts[-1]
        if '?' in last:
            last = last.split('?')[0]
        if last.lower() == 'feed' and len(parts) > 1:
            last = parts[-2]
        
        if 'groups' in url.lower() and 'groups' in parts:
            try:
                idx = parts.index('groups')
                if len(parts) > idx + 1:
                    group_id = parts[idx + 1]
                    if '?' in group_id:
                        group_id = group_id.split('?')[0]
                    return f"Nhóm {group_id}"
            except Exception:
                pass
            
        return last
    return url

# ─────────────────────────────────────────
# AUTO-LIKE
# ─────────────────────────────────────────
@app.route('/api/autolike/targets', methods=['GET'])
def api_get_autolike_targets():
    return jsonify(database.get_autolike_targets())

@app.route('/api/autolike/targets', methods=['POST'])
def api_save_autolike_target():
    data = request.json
    if not data.get('account_id') or not data.get('target_url'):
        return jsonify({'error': 'Thiếu thông tin tài khoản hoặc đường dẫn mục tiêu.'}), 400
        
    urls_input = data.get('target_url', '')
    account_id = data['account_id']
    auto_comment = int(data.get('auto_comment', 0))
    comment_style = data.get('comment_style', 'AI')
    comment_text = data.get('comment_text', '')
    
    raw_urls = []
    for line in urls_input.split('\n'):
        u = line.strip()
        if u:
            raw_urls.append(u)
            
    if not raw_urls:
        return jsonify({'error': 'Không có đường dẫn mục tiêu hợp lệ.'}), 400
        
    added_count = 0
    for u in raw_urls:
        if not u.startswith('http://') and not u.startswith('https://'):
            if u.isdigit():
                u = f"https://www.facebook.com/groups/{u}"
            else:
                u = f"https://www.facebook.com/{u}"
        
        tid = 'alt_' + str(uuid.uuid4())[:8]
        if len(raw_urls) == 1 and data.get('target_name') and data.get('target_name').strip():
            t_name = data['target_name'].strip()
        else:
            t_name = extract_fb_name(u)
            
        database.save_autolike_target(
            tid, account_id, u, t_name,
            status='active', auto_comment=auto_comment, comment_style=comment_style, comment_text=comment_text
        )
        added_count += 1
        
    return jsonify({'success': True, 'added_count': added_count})

@app.route('/api/autolike/targets/<tid>', methods=['DELETE'])
def api_delete_autolike_target(tid):
    database.delete_autolike_target(tid)
    return jsonify({'success': True})

@app.route('/api/autolike/logs', methods=['GET'])
def api_get_autolike_logs():
    return jsonify(database.get_autolike_logs())

@app.route('/api/autolike/run', methods=['POST'])
def api_run_autolike_now():
    """Trigger auto-like immediately for a specific target."""
    data = request.json
    target_id = data.get('target_id')
    targets = database.get_autolike_targets()
    target = next((t for t in targets if t['id'] == target_id), None)
    if not target: return jsonify({'error': 'Không tìm thấy mục tiêu.'}), 404
    account = database.get_account(target['account_id'])
    if not account: return jsonify({'error': 'Không tìm thấy tài khoản.'}), 400

    def run():
        settings = database.get_settings()
        max_l = int(settings.get('max_likes_per_scan', 10))
        liked = auto_like_posts(
            account['cookie'], target['target_url'], max_l,
            auto_comment=target.get('auto_comment', 0),
            comment_style=target.get('comment_style', 'AI'),
            comment_text=target.get('comment_text', ''),
            account_name=account['name']
        )
        for item in liked:
            database.save_autolike_log(item['id'], target['id'], item['post_url'], item['status'])
        database.update_autolike_target_last_run(target['id'])
    threading.Thread(target=run).start()
    return jsonify({'success': True, 'message': 'Đã kích hoạt Auto-Like trong nền.'})

# ─────────────────────────────────────────
# ANALYTICS & EXPORT
# ─────────────────────────────────────────
@app.route('/api/dashboard', methods=['GET'])
@app.route('/api/analytics', methods=['GET'])
def api_analytics():
    return jsonify(database.get_analytics())

@app.route('/api/export/posts', methods=['GET'])
def api_export_posts():
    posts = database.get_posts()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Tai khoan', 'Loai', 'Muc tieu', 'Noi dung', 'Lich dang', 'Trang thai', 'Ket qua', 'Cap nhat'])
    for p in posts:
        cw.writerow([p['id'], p.get('account_name', ''), p['type'], p['target_id'],
                     p['content'][:100], p['scheduled_at'], p['status'],
                     p.get('result_log', ''), p['updated_at']])
    output = si.getvalue()
    return Response(output, mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=posts_export.csv'})

@app.route('/api/export/logs', methods=['GET'])
def api_export_logs():
    logs = database.get_engagement_logs()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'URL bai viet', 'Nguoi binh luan', 'Noi dung BL', 'Phan hoi', 'Trang thai', 'Thoi gian'])
    for l in logs:
        cw.writerow([l['id'], l['post_url'], l['commenter_name'],
                     l['comment_content'], l['reply_content'], l['status'], l['created_at']])
    output = si.getvalue()
    return Response(output, mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=engagement_logs.csv'})

# ─────────────────────────────────────────
# AI ASSISTANT (GEMINI & IMAGEN)
# ─────────────────────────────────────────
import urllib.parse
import urllib.request
import urllib.error

@app.route('/api/ai/generate-text', methods=['POST'])
def api_ai_generate_text():
    data = request.json or {}
    prompt_addon = data.get('prompt', '')
    shopee_url = data.get('shopee_url', '')

    settings = database.get_settings()
    api_key = settings.get('gemini_api_key', '').strip()
    if not api_key:
        return jsonify({'error': 'Vui lòng cấu hình Gemini API Key trong phần Cấu hình hệ thống.'}), 400

    product_context = ""
    shopee_image = None
    product_title = ""
    if shopee_url:
        try:
            print(f"[AI] Scraping Shopee link: {shopee_url}")
            product_data = scrape_shopee_product(shopee_url)
            if product_data.get('title'):
                product_title = product_data['title']
                product_context = f"\nThông tin sản phẩm từ link Shopee:\nTiêu đề: {product_data['title']}\nChi tiết: {product_data.get('description', '')[:1200]}\n"
                
                # Download product image if present
                image_url = product_data.get('image_url')
                if image_url:
                    try:
                        print(f"[AI] Downloading Shopee image: {image_url}")
                        req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=15) as img_res:
                            img_data = img_res.read()
                            filename = f"shopee_img_{str(uuid.uuid4())[:8]}.png"
                            filepath = os.path.join(UPLOAD_FOLDER, filename)
                            with open(filepath, 'wb') as f:
                                f.write(img_data)
                            shopee_image = filename
                            print(f"[AI] Shopee image saved: {filename}")
                    except Exception as img_err:
                        print(f"[AI] Failed to download Shopee image: {img_err}")
        except Exception as ex:
            print(f"[AI] Failed to scrape Shopee context: {ex}")

    system_instruction = (
        "Bạn là một người dùng Facebook bình thường, có sở thích mua sắm và săn sale, đang muốn chia sẻ review về một sản phẩm cực kỳ ưng ý mà bạn vừa mua.\n"
        "Nhiệm vụ của bạn là viết một bài đăng (Post) Facebook dạng CHIA SẺ/REVIEW CHÂN THỰC dựa trên thông tin sản phẩm dưới đây.\n"
        "Yêu cầu chung:\n"
        "- Giọng điệu thân thiện, tự nhiên, gần gũi như đang tâm sự với bạn bè trong hội nhóm.\n"
        "- Chèn các biểu tượng cảm xúc (emojis) vừa phải, không lạm dụng như bài quảng cáo.\n"
        "- Cách hành văn KHÔNG ĐƯỢC giống quảng cáo (Tuyệt đối không dùng cấu trúc Tiêu đề giật gân -> Nỗi đau -> Lợi ích -> CTA).\n"
        "- Viết dưới góc độ người đã trải nghiệm sản phẩm: Khen điểm tốt, nói sơ qua lý do mua, và khuyên mọi người nên dùng thử.\n"
        "- KHÔNG quảng cáo hay nhắc đến 'kênh Shopee', 'gian hàng', 'shop của mình' hay 'kênh affiliate'. Chỉ nói là 'mình săn được ở đây'.\n"
        "- Khéo léo chèn link sản phẩm vào bài viết một cách tự nhiên (VD: 'Mình để link chỗ mình mua cho mng tham khảo nha: [Link]').\n"
        "- Độ dài vừa phải, súc tích, đọc giống một bài đăng seeding trong các hội nhóm review.\n"
    )

    full_prompt = system_instruction
    if product_context:
        full_prompt += product_context
        if shopee_url:
            full_prompt += f"Link mua hàng shopee để gắn vào bài: {shopee_url}\n"
    
    if prompt_addon:
        full_prompt += f"\nYêu cầu bổ sung của khách hàng:\n{prompt_addon}\n"
    else:
        full_prompt += "\nHãy viết bài đăng giới thiệu chi tiết sản phẩm này."

    try:
        text_result = call_gemini(api_key, full_prompt)
        return jsonify({
            'text': text_result,
            'shopee_image': shopee_image,
            'product_title': product_title
        })
    except Exception as e:
        print(f"[AI] Gemini API error: {e}")
        return jsonify({'error': f'Lỗi hệ thống khi gọi Gemini: {str(e)}'}), 500

@app.route('/api/ai/generate-image', methods=['POST'])
def api_ai_generate_image():
    data = request.json or {}
    prompt = data.get('prompt', '').strip()
    if not prompt:
        return jsonify({'error': 'Vui lòng cung cấp mô tả hình ảnh.'}), 400

    try:
        encoded_prompt = urllib.parse.quote(prompt)
        pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"
        
        print(f"[AI] Requesting image from Pollinations: {pollinations_url}")
        req = urllib.request.Request(pollinations_url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=40) as response:
            image_data = response.read()
            filename = f"ai_gen_{str(uuid.uuid4())[:8]}.png"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, 'wb') as f:
                f.write(image_data)
                
            print(f"[AI] Image saved to {filepath}")
            return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        print(f"[AI] Image generation error: {e}")
        return jsonify({'error': f'Lỗi khi tạo ảnh AI: {str(e)}'}), 500

# ─────────────────────────────────────────
@app.route('/api/telegram/test', methods=['POST'])
def api_test_telegram():
    data = request.json or {}
    token = data.get('token', '').strip()
    chat_id = data.get('chat_id', '').strip()
    
    if not token or not chat_id:
        return jsonify({'error': 'Vui lòng cung cấp đầy đủ Token và Chat ID.'}), 400
        
    from telegram_bot import send_telegram_message
    res = send_telegram_message(token, chat_id, "🔔 <b>Thông báo từ HAME:</b> Kết nối thành công! Hệ thống của bạn đã được liên kết chính xác.")
    
    if res and res.get('ok'):
        return jsonify({'success': True, 'message': 'Đã gửi tin nhắn thử nghiệm thành công.'})
    else:
        desc = res.get('description', 'Không rõ nguyên nhân') if res else 'Lỗi kết nối API Telegram'
        return jsonify({'error': f'Lỗi gửi tin nhắn: {desc}'}), 400

@app.route('/api/settings', methods=['GET'])
def api_get_settings():
    return jsonify(database.get_settings())

@app.route('/api/settings', methods=['POST'])
def api_save_settings():
    data = request.json or {}
    for k, v in data.items():
        database.save_setting(k, v)
        
    shopee_target = data.get('shopee_poster_target_id')
    shopee_account = data.get('shopee_poster_account_id')
    if shopee_target or shopee_account:
        settings = database.get_settings()
        target_id = shopee_target or settings.get('shopee_poster_target_id')
        account_id = shopee_account or settings.get('shopee_poster_account_id')
        if account_id and target_id:
            trigger_autojoin_for_targets(account_id, target_id)
            
    return jsonify(database.get_settings())

@app.route('/api/shopee/auto-post-trigger', methods=['POST'])
def api_shopee_auto_post_trigger():
    import sys
    sys.path.append(r'C:\Users\TOSHIBA\.gemini\antigravity\scratch')
    import auto_fb_scheduler
    
    def run_post():
        try:
            auto_fb_scheduler.run_scheduler()
        except Exception as e:
            print("Manual auto-post thread error:", e)
            
    threading.Thread(target=run_post, daemon=True).start()
    return jsonify({"status": "success", "message": "Đã kích hoạt robot đăng bài Shopee tự động trong nền."})

@app.route('/r/<redirect_id>')
def serve_redirect_page(redirect_id):
    try:
        redirect_info = database.get_redirect(redirect_id)
        if not redirect_info:
            return Response("<h1>404 - Link Not Found</h1>", status=404, mimetype='text/html')
            
        # Count click for non-bots
        try:
            user_agent = request.headers.get('User-Agent', '').lower()
            is_bot = any(bot in user_agent for bot in ['facebookexternalhit', 'facebot', 'bot', 'spider', 'crawler', 'scrap'])
            if not is_bot:
                database.increment_redirect_clicks(redirect_id)
        except Exception as e:
            print(f"[Redirect] Click tracking error: {e}")
            
        destination_url = redirect_info.get('destination_url') or '/'
        image_file = redirect_info.get('image_file') or ''
        title = redirect_info.get('title') or 'Xem chi tiết sản phẩm'
        description = redirect_info.get('description') or 'Click để truy cập liên kết'
        
        settings = database.get_settings()
        public_domain = settings.get('public_domain', '').strip()
        if not public_domain:
            public_domain = request.host_url.rstrip('/')
            
        image_url = f"{public_domain}/api/uploads/{image_file}" if image_file else ""
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{image_url}">
    <meta property="og:url" content="{public_domain}/r/{redirect_id}">
    <meta property="og:type" content="website">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta http-equiv="refresh" content="0; url={destination_url}">
</head>
<body>
    <p>Redirecting to <a href="{destination_url}">{destination_url}</a>...</p>
    <script>
        window.location.href = {json.dumps(destination_url)};
    </script>
</body>
</html>"""
        return Response(html_content, status=200, mimetype='text/html')
    except Exception as err:
        print(f"[Redirect] Fatal handler error: {err}")
        return Response(f"<h1>Redirect Error</h1><p>{str(err)}</p>", status=500, mimetype='text/html')

# ─────────────────────────────────────────
# AUTO-JOIN GROUPS API
# ─────────────────────────────────────────
@app.route('/api/autojoin/run', methods=['POST'])
def api_autojoin_run():
    data = request.json or {}
    account_id = data.get('account_id')
    if not account_id:
        return jsonify({'error': 'Vui lòng chọn tài khoản.'}), 400
        
    account = database.get_account(account_id)
    if not account:
        return jsonify({'error': 'Tài khoản không tồn tại.'}), 404
        
    source_type = data.get('source_type', 'urls')
    urls = data.get('urls', '')
    keyword = data.get('keyword', '') if source_type == 'keyword' else None
    limit = int(data.get('limit', 5))
    delay = int(data.get('delay', 15))
    answer_questions = bool(data.get('answer_questions', True))
    
    def run_autojoin_thread():
        print(f"[Auto-Join] Bắt đầu luồng chạy ngầm tham gia nhóm cho tài khoản: {account['name']}")
        try:
            auto_join_facebook_groups(
                account_id=account['id'],
                account_cookie=account['cookie'],
                account_name=account['name'],
                group_inputs=urls,
                keyword=keyword,
                limit=limit,
                delay=delay,
                answer_questions=answer_questions
            )
            print(f"[Auto-Join] Luồng chạy ngầm đã hoàn thành.")
        except Exception as th_err:
            print(f"[Auto-Join] Lỗi trong luồng chạy ngầm: {th_err}")
            
    threading.Thread(target=run_autojoin_thread, daemon=True).start()
    return jsonify({'success': True, 'message': 'Tiến trình tự động tham gia nhóm đã bắt đầu chạy ngầm.'})

@app.route('/api/autojoin/sync-public-groups', methods=['POST'])
def api_autojoin_sync_public_groups():
    data = request.json or {}
    account_id = data.get('account_id')
    if not account_id:
        return jsonify({'error': 'Vui lòng chọn tài khoản.'}), 400
        
    account = database.get_account(account_id)
    if not account:
        return jsonify({'error': 'Tài khoản không tồn tại.'}), 404
        
    limit = int(data.get('limit', 30))
    
    def run_sync_thread():
        print(f"[SyncGroups] Khởi động đồng bộ nhóm công khai cho {account['name']}...")
        try:
            scrape_and_save_public_groups(
                account_id=account['id'],
                account_cookie=account['cookie'],
                account_name=account['name'],
                limit=limit
            )
        except Exception as th_err:
            print(f"[SyncGroups] Lỗi đồng bộ: {th_err}")
            
    threading.Thread(target=run_sync_thread, daemon=True).start()
    return jsonify({'success': True, 'message': 'Đang tiến hành đồng bộ nhóm công khai chạy ngầm. Vui lòng theo dõi tiến trình trong nhật ký.'})

@app.route('/api/autojoin/topic-campaign', methods=['POST'])
def api_autojoin_topic_campaign():
    import re
    data = request.json or {}
    account_id = data.get('account_id')
    if not account_id:
        return jsonify({'error': 'Vui lòng chọn tài khoản.'}), 400
        
    account = database.get_account(account_id)
    if not account:
        return jsonify({'error': 'Tài khoản không tồn tại.'}), 404
        
    topics_raw = data.get('topics', '').strip()
    if not topics_raw:
        return jsonify({'error': 'Vui lòng nhập ít nhất một chủ đề.'}), 400
        
    topics = []
    for part in re.split(r'[\n,]', topics_raw):
        part = part.strip()
        if part:
            topics.append(part)
            
    if not topics:
        return jsonify({'error': 'Vui lòng nhập chủ đề hợp lệ.'}), 400
        
    limit_per_topic = int(data.get('limit_per_topic', 50))
    delay = int(data.get('delay', 15))
    answer_questions = bool(data.get('answer_questions', True))
    prioritize = bool(data.get('prioritize', True))
    
    def run_campaign_thread():
        print(f"[TopicCampaign] Bắt đầu chiến dịch nhóm theo chủ đề cho tài khoản {account['name']}...")
        for topic in topics:
            try:
                auto_join_groups_by_topic(
                    account_id=account['id'],
                    account_cookie=account['cookie'],
                    account_name=account['name'],
                    topic=topic,
                    target_limit=limit_per_topic,
                    delay=delay,
                    answer_questions=answer_questions,
                    prioritize=prioritize
                )
                time.sleep(5)
            except Exception as cam_err:
                print(f"[TopicCampaign] Lỗi chiến dịch cho chủ đề {topic}: {cam_err}")
        print("[TopicCampaign] Tất cả chiến dịch theo chủ đề hoàn tất.")
        
    threading.Thread(target=run_campaign_thread, daemon=True).start()
    return jsonify({'success': True, 'message': f'Đã khởi chạy chiến dịch tham gia nhóm theo {len(topics)} chủ đề trong nền.'})

@app.route('/api/autojoin/logs', methods=['GET'])
def api_autojoin_get_logs():
    return jsonify(database.get_autojoin_logs())
    
@app.route('/api/autojoin/logs', methods=['DELETE'])
def api_autojoin_clear_logs():
    database.clear_autojoin_logs()
    return jsonify({'success': True})

@app.route('/api/shopee/bulk-import', methods=['POST'])
def api_shopee_bulk_import():
    data = request.json or {}
    urls_str = data.get('urls', '').strip()
    topic = data.get('topic', '').strip()
    
    if not urls_str:
        return jsonify({'error': 'Vui lòng nhập ít nhất một link Shopee.'}), 400
        
    urls = []
    for line in urls_str.split('\n'):
        line = line.strip()
        if line and (line.startswith('http://') or line.startswith('https://')):
            urls.append(line)
            
    if not urls:
        return jsonify({'error': 'Không tìm thấy đường dẫn (link) hợp lệ.'}), 400
        
    active_accounts = [a for a in database.get_accounts() if a['status'] == 'active']
    if not active_accounts:
        return jsonify({'error': 'Không tìm thấy tài khoản Facebook nào đang hoạt động.'}), 400
        
    settings = database.get_settings()
    poster_type = settings.get('shopee_poster_type', 'profile')
    poster_target_id = settings.get('shopee_poster_target_id', 'me')
    poster_format = settings.get('shopee_poster_format', 'clickable')
    api_key = settings.get('gemini_api_key', '').strip()
    
    # Map topic to scheduler config
    cfg = get_shopee_scheduler_details(topic)
    
    # Match account
    import unicodedata
    def norm(s):
        if not s: return ""
        s = s.lower().strip()
        s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        return s

    account_id = None
    for acc in active_accounts:
        acc_name_norm = norm(acc['name'])
        for kw in cfg["account_keywords"]:
            if norm(kw) in acc_name_norm or acc_name_norm in norm(kw):
                account_id = acc['id']
                break
        if account_id:
            break
            
    if not account_id:
        shopee_account_id = settings.get('shopee_poster_account_id', '').strip()
        account_id = shopee_account_id if shopee_account_id else active_accounts[0]['id']
        
    # Match target list
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, targets FROM target_lists")
    target_lists = cursor.fetchall()
    conn.close()
    
    matched_targets = None
    for tl_id, tl_name, tl_targets in target_lists:
        tl_name_norm = norm(tl_name)
        for t in cfg["topics"]:
            if norm(t) in tl_name_norm or tl_name_norm in norm(t):
                matched_targets = tl_targets
                break
        if matched_targets:
            break
            
    targets = []
    if matched_targets:
        for line in matched_targets.split('\n'):
            line = line.strip()
            if not line:
                continue
            parsed = parse_target_line(line)
            if parsed:
                targets.append(parsed)
                
    if not targets:
        targets = [{"type": poster_type, "target_id": poster_target_id}]
        
    def run_import_thread():
        print(f"[BulkShopee] Starting UI bulk import for {len(urls)} URLs under topic '{topic}'...")
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT scheduled_at FROM posts WHERE account_id=? AND status='pending'", (account_id,))
        current_scheduled_times = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        start_from = datetime.now()
        post_count = 0
        for url in urls:
            conn = database.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM redirects WHERE destination_url=?", (url,))
            dup_redir = cursor.fetchone()
            cursor.execute("SELECT id FROM posts WHERE content LIKE ?", (f"%{url}%",))
            dup_post = cursor.fetchone()
            conn.close()
            
            if dup_redir or dup_post:
                print(f"[BulkShopee] Skipping duplicate URL: {url}")
                continue
                
            print(f"[BulkShopee] Processing URL: {url}")
            product = scrape_shopee_product(url)
            if 'error' in product or not product.get('title'):
                print(f"[BulkShopee] Error scraping product: {product.get('error', 'No title')}")
                continue
                
            if api_key:
                prompt = (
                    f"Hãy viết một bài viết quảng cáo giới thiệu sản phẩm hấp dẫn, hài hước, kích thích mua sắm dựa trên thông tin sản phẩm Shopee này:\n"
                    f"Tiêu đề: {product.get('title')}\n"
                    f"Mô tả: {product.get('description', '')[:1000]}\n\n"
                    f"Yêu cầu:\n"
                    f"- CHỈ trả về nội dung bài viết quảng cáo trực tiếp. KHÔNG viết lời mở đầu, KHÔNG viết lời chào hay bất kỳ câu giới thiệu nào khác (ví dụ: KHÔNG viết 'Dưới đây là...', 'Được thôi...', 'Đây là...').\n"
                    f"- BẮT BUỘC phải giới thiệu thương hiệu 'Lolishop' một cách tự nhiên trong bài viết (ví dụ: 'Lolishop giới thiệu...', 'Sản phẩm cực hot tại Lolishop...').\n"
                    f"- Tập trung giới thiệu công dụng, tính năng nổi bật và lợi ích thực tế của sản phẩm.\n"
                    f"- Ngắn gọn dưới 150 từ, dùng nhiều emoji phù hợp.\n"
                    f"- Có lời kêu gọi hành động (Call to Action) bấm vào link/hình ảnh ở dưới để mua sản phẩm từ Lolishop.\n"
                    f"- Không được kèm liên kết gốc Shopee trong nội dung bài viết."
                )
                try:
                    post_content = call_gemini(api_key, prompt)
                except Exception as ai_err:
                    post_content = f"🔥 {product.get('title')} 🔥\n\nSản phẩm cực chất, click ngay để mua với giá ưu đãi!"
            else:
                post_content = f"🔥 {product.get('title')} 🔥\n\nSản phẩm cực chất, click ngay để mua với giá ưu đãi!"

            scheduled_time = get_next_golden_slot(account_id, cfg["golden_hours"], current_scheduled_times, start_from)
            scheduled_at_str = scheduled_time.isoformat()[:16]
            current_scheduled_times.append(scheduled_at_str)
            start_from = scheduled_time
            
            post_id = 'post_' + str(uuid.uuid4())[:8]
            image_url = product.get('image_url')
            media_list = []
            
            if poster_format == 'clickable' and image_url:
                import urllib.request
                local_image_name = f"shopee_{post_id}.jpg"
                local_image_path = os.path.join(UPLOAD_FOLDER, local_image_name)
                try:
                    req = urllib.request.Request(
                        image_url, 
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    )
                    with urllib.request.urlopen(req, timeout=15) as response, open(local_image_path, 'wb') as out_file:
                        out_file.write(response.read())
                    
                    media_list = [f"uploads/{local_image_name}"]
                    
                    redir_id = 'r_' + str(uuid.uuid4())[:8]
                    conn = database.get_db_connection()
                    cursor = conn.cursor()
                    aff_url = make_shopee_affiliate_link(url, settings)
                    cursor.execute(
                        'INSERT INTO redirects (id, destination_url, image_file, title, description, created_at) VALUES (?,?,?,?,?,?)',
                        (redir_id, aff_url, f"uploads/{local_image_name}", product.get('title')[:100], "Click xem chi tiết sản phẩm và mua ngay!", datetime.now().isoformat())
                    )
                    conn.commit()
                    conn.close()
                    
                    public_domain = settings.get('public_domain', 'http://localhost:5000').rstrip('/')
                    redirect_link = f"{public_domain}/r/{redir_id}"
                    
                    shopee_auto_comment = settings.get('shopee_auto_comment_link', '1') == '1'
                    first_comment = None
                    if shopee_auto_comment:
                        comment_template = settings.get('shopee_comment_template', 'Link mua sản phẩm tại đây nhé cả nhà: {link}')
                        first_comment = comment_template.replace('{link}', redirect_link)
                    else:
                        post_content = f"{post_content}\n\n👉 Chi tiết sản phẩm: {redirect_link}"
                    
                except Exception as img_err:
                    shopee_auto_comment = settings.get('shopee_auto_comment_link', '1') == '1'
                    first_comment = None
                    aff_url = make_shopee_affiliate_link(url, settings)
                    if shopee_auto_comment:
                        comment_template = settings.get('shopee_comment_template', 'Link mua sản phẩm tại đây nhé cả nhà: {link}')
                        first_comment = comment_template.replace('{link}', aff_url)
                    else:
                        post_content = f"{post_content}\n\n👉 Mua ngay tại đây: {aff_url}"
            else:
                shopee_auto_comment = settings.get('shopee_auto_comment_link', '1') == '1'
                first_comment = None
                aff_url = make_shopee_affiliate_link(url, settings)
                if shopee_auto_comment:
                    comment_template = settings.get('shopee_comment_template', 'Link mua sản phẩm tại đây nhé cả nhà: {link}')
                    first_comment = comment_template.replace('{link}', aff_url)
                else:
                    post_content = f"{post_content}\n\n👉 Mua ngay tại đây: {aff_url}"
                
            for target in targets:
                target_post_id = 'post_' + str(uuid.uuid4())[:8]
                database.save_post(
                    post_id=target_post_id,
                    account_id=account_id,
                    type_=target['type'],
                    target_id=target['target_id'],
                    content=post_content,
                    media=media_list,
                    scheduled_at=scheduled_at_str,
                    status='pending',
                    first_comment=first_comment
                )
            post_count += 1
            
        print(f"[BulkShopee] Import thread completed. Scheduled {post_count} products successfully.")
        if post_count > 0:
            trigger_autojoin_for_targets(account_id, targets)

    threading.Thread(target=run_import_thread, daemon=True).start()
    return jsonify({'success': True, 'message': 'Đã bắt đầu tiến trình cào và lên lịch đăng Shopee tự động chạy ngầm.'})

def find_account_for_topic(item_name, item_target, active_accounts):
    """Phân luồng tài khoản dựa trên tên chủ đề/nhóm mục tiêu của bài đăng."""
    name_lower = (item_name or '').lower()
    target_lower = (item_target or '').lower()
    full_text = name_lower + " " + target_lower

    # Ánh xạ từ các từ khóa chủ đề đến từ khóa của tài khoản
    topic_map = {
        'shope lite 2': ['công nghệ', 'kinh doanh', 'cong nghe'],
        'shope lite': ['gym', 'chạy bộ', 'sinh viên', 'chay bo', 'sinh vien'],
        'shope vip': ['phụ nữ', 'thời trang', 'du lịch', 'thú cưng', 'phu nu', 'thoi trang', 'du lich', 'thu cung'],
        'shope sale': ['mê xe', 'nhà đất', 'me xe', 'nha dat'],
        'shope': ['chợ', 'nội trợ', 'mẹ bỉm', 'nấu ăn', 'cho', 'noi tro', 'me bim', 'nau an']
    }

    for canonical, keywords in topic_map.items():
        for kw in keywords:
            if kw in full_text:
                for acc in active_accounts:
                    acc_name = acc['name'].lower()
                    if canonical == 'shope lite 2' and 'shope lite 2' in acc_name:
                        return acc['id']
                    elif canonical == 'shope lite' and 'shope lite' in acc_name and 'shope lite 2' not in acc_name:
                        return acc['id']
                    elif canonical == 'shope sale' and 'shope sale' in acc_name:
                        return acc['id']
                    elif canonical == 'shope vip' and 'shope vip' in acc_name:
                        return acc['id']
                    elif canonical == 'shope' and 'shope' in acc_name and not any(k in acc_name for k in ['lite', 'sale', 'vip']):
                        return acc['id']
    
    # Nếu không khớp từ khóa nào, chọn tài khoản đầu tiên
    if active_accounts:
        return active_accounts[0]['id']
    return None

@app.route('/api/import-claude-schedule', methods=['POST'])
def api_import_claude_schedule():
    """
    Import lịch đăng bài từ Claude share link.
    Nhận: { items: [{content, scheduled_at, target_id, type, name}], shopee_link, account_id }
    Mỗi item sẽ tạo 1 bài đăng pending với link Shopee tự động bình luận ở comment đầu tiên.
    """
    data = request.json or {}
    items = data.get('items', [])
    shopee_link = data.get('shopee_link', '').strip()
    account_id = data.get('account_id', '').strip()

    if not items:
        return jsonify({'error': 'Danh sách bài đăng trống.'}), 400

    settings = database.get_settings()
    active_accounts = [a for a in database.get_accounts() if a['status'] == 'active']
    if not active_accounts:
        return jsonify({'error': 'Không có tài khoản Facebook nào đang hoạt động.'}), 400

    if not account_id:
        return jsonify({'error': 'Vui lòng chọn tài khoản đăng bài từ danh sách của bạn.'}), 400

    comment_template = settings.get('shopee_comment_template', 'Link mua sản phẩm tại đây nhé cả nhà: {link}')
    created = 0
    errors = []

    for item in items:
        try:
            content = item.get('content', '').strip()
            scheduled_at = item.get('scheduled_at', '').strip()
            target_id = item.get('target_id', 'me').strip()
            post_type = item.get('type', 'profile')
            item_name = item.get('name', '')

            if not content or not scheduled_at:
                errors.append(f"Bỏ qua item thiếu nội dung hoặc thời gian: {item.get('name','?')}")
                continue

            # Thực hiện phân luồng tài khoản nếu người dùng chọn auto_route
            item_account_id = account_id
            if account_id == 'auto_route':
                item_account_id = find_account_for_topic(item_name, target_id, active_accounts)
                if not item_account_id:
                    errors.append(f"Bỏ qua '{item_name}': Không tìm thấy tài khoản tương ứng.")
                    continue

            post_id = 'post_' + str(uuid.uuid4())[:8]

            # Gắn link Shopee vào first_comment nếu có
            first_comment = None
            if shopee_link:
                aff_link = make_shopee_affiliate_link(shopee_link, settings)
                first_comment = comment_template.replace('{link}', aff_link)

            database.save_post(
                post_id=post_id,
                account_id=item_account_id,
                type_=post_type,
                target_id=target_id,
                content=content,
                media=item.get('media', []),
                scheduled_at=scheduled_at,
                status='pending',
                first_comment=first_comment
            )
            created += 1
        except Exception as e:
            errors.append(f"Lỗi tạo bài '{item.get('name','?')}': {str(e)}")

    # Trigger auto-join cho các target nhóm
    if created > 0:
        all_targets = ' '.join([item.get('target_id','') for item in items if item.get('target_id')])
        try:
            trigger_autojoin_for_targets(active_accounts[0]['id'], all_targets)
        except Exception:
            pass

    return jsonify({
        'success': True,
        'created': created,
        'errors': errors,
        'message': f'Đã lên lịch {created}/{len(items)} bài đăng thành công.'
    })


# ─────────────────────────────────────────
# INSIGHT TARGETS & LEADS
# ─────────────────────────────────────────
@app.route('/api/insights/targets', methods=['GET'])
def api_get_insight_targets():
    return jsonify(database.get_insight_targets())

@app.route('/api/insights/targets', methods=['POST'])
def api_save_insight_target():
    data = request.json
    tid = data.get('id') or 'ins_' + str(uuid.uuid4())[:8]
    t = database.save_insight_target(
        target_id=tid,
        target_url=data.get('target_url', '').strip(),
        target_name=data.get('target_name', 'Unknown'),
        niche_keywords=data.get('niche_keywords', '').strip(),
        status=data.get('status', 'active')
    )
    return jsonify(t)

@app.route('/api/insights/targets/<tid>', methods=['DELETE'])
def api_delete_insight_target(tid):
    database.delete_insight_target(tid)
    return jsonify({'success': True})

@app.route('/api/insights/leads', methods=['GET'])
def api_get_insight_leads():
    limit = int(request.args.get('limit', 100))
    return jsonify(database.get_insight_leads(limit))

@app.route('/api/accounts/check-health', methods=['GET'])
def api_check_accounts_health():
    accounts = database.get_accounts()
    health_results = []
    
    # Query last failed reason for each account from posts table
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    import time
    now = time.time()
    
    for acc in accounts:
        # 1. Parse cookie timestamp
        expired = False
        try:
            cookies = json.loads(acc['cookie'])
            for c in cookies:
                if c.get('name') in ['xs', 'c_user']:
                    exp = c.get('expirationDate')
                    if exp and exp < now:
                        expired = True
                        break
        except Exception:
            expired = True
            
        # 2. Check last post failure log
        last_failed_log = ""
        if not expired:
            try:
                cursor.execute(
                    "SELECT result_log FROM posts WHERE account_id=? AND status='failed' ORDER BY updated_at DESC LIMIT 1;",
                    (acc['id'],)
                )
                row = cursor.fetchone()
                if row and row[0]:
                    last_log = row[0].lower()
                    if "cookie expired" in last_log or "login page" in last_log or "hết hạn" in last_log or "cookie" in last_log:
                        expired = True
                        last_failed_log = row[0]
            except Exception as db_err:
                print(f"[Health] DB Error: {db_err}")
                
        health_results.append({
            'id': acc['id'],
            'name': acc['name'],
            'status': acc['status'],
            'cookie_expired': expired,
            'last_failed_log': last_failed_log
        })
        
    conn.close()
    return jsonify(health_results)

@app.route('/api/tunnel/status', methods=['GET'])
def api_get_tunnel_status():
    global tunnel_status, tunnel_url
    return jsonify({
        'status': tunnel_status,
        'url': tunnel_url,
        'subdomain': database.get_settings().get('tunnel_subdomain', 'chungs-shopee')
    })

@app.route('/api/generate-video', methods=['POST'])
def api_generate_video():
    try:
        data = request.json or {}
        image_urls = data.get('images', [])
        product_name = data.get('product_name', 'Sản Phẩm Mới')
        price = data.get('price', 'Liên hệ')
        
        if not image_urls:
            return jsonify({'success': False, 'error': 'No images provided'})
            
        import video_generator
        # generate a unique filename
        import uuid
        filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        res = video_generator.create_video(image_urls, product_name, price, output_path)
        
        if isinstance(res, tuple) and res[0] is None:
            return jsonify({'success': False, 'error': res[1]})
        elif res:
            video_url = f"/api/uploads/{filename}"
            return jsonify({'success': True, 'video_url': video_url})
        else:
            return jsonify({'success': False, 'error': 'Failed to generate video'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


def monitor_bait_worker():
    import database
    import automation
    print("[Bait] Bắt đầu luồng theo dõi bài mồi...")
    while True:
        try:
            posts = database.get_bait_posts()
            if posts:
                # Get first active account cookie
                accounts = database.get_accounts()
                active_accounts = [a for a in accounts if a['status'] == 'active']
                if active_accounts:
                    cookie = active_accounts[0]['cookie']
                    for post in posts:
                        url = post.get('target_id') # Assuming target_id holds the post_url if not saved elsewhere
                        if 'facebook.com' in url:
                            automation.monitor_bait_posts_and_reply(cookie, url)
                            time.sleep(10)
        except Exception as e:
            print(f"[Bait] Lỗi luồng bait: {e}")
        time.sleep(900) # Quét mỗi 15 phút

@app.route('/api/autodm/run', methods=['POST'])
def api_autodm_run():
    data = request.json
    group_url = data.get('group_url')
    product_url = data.get('product_url', '')
    industry = data.get('industry', 'thoi_trang')
    high_risk = data.get('high_risk', False)
    
    if not group_url:
        return jsonify({"error": "Missing group_url"}), 400
        
    cmd = ["py", "trigger_autodm.py", "--group_url", group_url]
    if product_url:
        cmd.extend(["--product_url", product_url])
    if industry:
        cmd.extend(["--industry", industry])
    if high_risk:
        cmd.append("--high_risk")
        
    # Chạy dưới nền
    subprocess.Popen(cmd)
    
    return jsonify({"message": f"Chiến dịch Auto DM ({industry}) đang chạy ngầm cho: {group_url}"}), 200

# Đường dẫn file log cố định trong thư mục fb-poster
AB_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ab_test_logs.txt')

@app.route('/api/autodm/stats', methods=['GET'])
def api_autodm_stats():
    stats = {
        "total": 0,
        "variant_a_success": 0,
        "variant_b_success": 0,
        "failed": 0,
        "recent_logs": []
    }
    
    if os.path.exists(AB_LOG_FILE):
        try:
            with open(AB_LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    stats["total"] += 1
                    if "SUCCESS" in line:
                        if "Variant A" in line:
                            stats["variant_a_success"] += 1
                        elif "Variant B" in line:
                            stats["variant_b_success"] += 1
                    else:
                        stats["failed"] += 1
                
                # Get last 20 logs
                stats["recent_logs"] = [l.strip() for l in lines[-20:]]
        except Exception as e:
            print("Error reading ab_test_logs:", e)
            
    return jsonify(stats), 200

@app.route('/api/autodm/stream')
def api_autodm_stream():
    """Server-Sent Events: stream log file realtime to browser."""
    def generate():
        last_pos = 0
        while True:
            if os.path.exists(AB_LOG_FILE):
                with open(AB_LOG_FILE, 'r', encoding='utf-8') as f:
                    f.seek(last_pos)
                    new_lines = f.readlines()
                    last_pos = f.tell()
                for line in new_lines:
                    line = line.strip()
                    if line:
                        yield f"data: {line}\n\n"
            time.sleep(2)
    from flask import Response
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/autodm/leads', methods=['GET'])
def api_autodm_leads():
    try:
        leads = database.get_all_dm_leads(limit=100)
        return jsonify(leads), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/autodm/export-leads', methods=['GET'])
def api_autodm_export_leads():
    try:
        leads = database.get_all_dm_leads(limit=1000)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Customer_URL', 'Group_URL', 'Variant', 'Status', 'First_Sent_At', 'Last_Followup_At', 'Notes'])
        for lead in leads:
            writer.writerow([
                lead.get('id', ''),
                lead.get('customer_url', ''),
                lead.get('group_url', ''),
                lead.get('variant', 'A'),
                lead.get('status', ''),
                lead.get('first_sent_at', ''),
                lead.get('last_follow_up_at', ''),
                lead.get('notes', '')
            ])
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename=dm_leads_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/autodm/followup', methods=['POST'])
def api_autodm_followup():
    cmd = ["py", "..\\auto_dm_playwright.py", "--followup"]
    subprocess.Popen(cmd)
    return jsonify({"message": "Chiến dịch Chăm sóc lại (Follow-up) đang chạy ngầm!"}), 200

@app.route('/api/inbox/run', methods=['POST'])
def api_inbox_run():
    cmd = ["py", "auto_reply_inbox.py"]
    subprocess.Popen(cmd)
    return jsonify({"message": "Robot AI Messenger Auto-Closer đang tự động quét hộp thư và chốt đơn!"}), 200

@app.route('/api/automation/comments', methods=['POST'])
def api_auto_comments():
    data = request.json or {}
    post_url = data.get('post_url', '')
    cmd = ["py", "auto_reply_comments.py"]
    if post_url:
        cmd.append(post_url)
    subprocess.Popen(cmd)
    return jsonify({"message": "Robot Auto-Reply Comment đang quét bài viết và trả lời khách!"}), 200

@app.route('/api/automation/friends', methods=['POST'])
def api_auto_friends():
    data = request.json or {}
    action = data.get('action', 'accept')
    cmd = ["py", "auto_friend_manager.py", f"--action={action}"]
    subprocess.Popen(cmd)
    return jsonify({"message": f"Robot Auto Friend đang thực hiện: {action}!"}), 200

@app.route('/api/friends/target-add', methods=['POST'])
def api_target_friends_add():
    data = request.json or {}
    target_url = data.get('target_url', '').strip()
    limit = int(data.get('limit', 20))
    if not target_url:
        return jsonify({"error": "Vui lòng cung cấp URL trang cá nhân đối thủ/KOL!"}), 400
    cmd = ["py", "scrape_and_add_friends.py", target_url, str(limit)]
    subprocess.Popen(cmd)
    return jsonify({"message": f"Robot Target Friend Extractor đang bóc tách bạn bè đối thủ & gửi kết bạn ngầm!"}), 200

@app.route('/api/video/create', methods=['POST'])
def api_video_create():
    data = request.json or {}
    title = data.get('title', 'Ví nữ cầm tay cao cấp ELLY').strip()
    price = int(data.get('price', 500000))
    destination = data.get('destination', 'all').strip()
    cmd = ["py", "video_generator.py", title, str(price), destination]
    subprocess.Popen(cmd)
    return jsonify({"message": f"🤖 AI Video Studio đang quay video ngắn & chuẩn bị đăng lên kênh: {destination.upper()}!"}), 200

@app.route('/api/automation/reengage', methods=['POST'])
def api_auto_reengage():
    data = request.json or {}
    limit = int(data.get('limit', 10))
    cmd = ["py", "auto_reengagement.py", str(limit)]
    subprocess.Popen(cmd)
    return jsonify({"message": f"AI Re-Engagement đang quét hội thoại & nhắn tin chăm sóc lại {limit} khách hàng cũ!"}), 200

@app.route('/api/automation/join-groups', methods=['POST'])
def api_auto_join_groups():
    data = request.json or {}
    kw = data.get('keyword', 'Hội bỉm sữa mua bán').strip()
    limit = int(data.get('limit', 10))
    cmd = ["py", "auto_group_joiner.py", kw, str(limit)]
    subprocess.Popen(cmd)
    return jsonify({"message": f"Auto Group Joiner đang tìm & gửi yêu cầu tham gia nhóm ngách cho từ khóa: '{kw}'!"}), 200

@app.route('/api/affiliate/revenue-stats', methods=['GET'])
def api_affiliate_revenue_stats():
    from affiliate_link_converter import get_affiliate_revenue_stats
    stats = get_affiliate_revenue_stats()
    return jsonify(stats), 200

@app.route('/api/affiliate/convert', methods=['POST'])
def api_affiliate_convert():
    data = request.json or {}
    raw_url = data.get('url', '').strip()
    subid = data.get('subid', 'hame_growth').strip()
    if not raw_url:
        return jsonify({"error": "Vui lòng dán URL sản phẩm Shopee/Lazada!"}), 400
    from affiliate_link_converter import convert_to_affiliate_link
    aff_url = convert_to_affiliate_link(raw_url, subid)
    return jsonify({"original_url": raw_url, "affiliate_url": aff_url}), 200

@app.route('/api/affiliate/flashsale', methods=['POST'])
def api_affiliate_flashsale():
    data = request.json or {}
    category = data.get('category', 'Bán Chạy Nhất').strip()
    cmd = ["py", "shopee_flashsale_scraper.py", category]
    subprocess.Popen(cmd)
    return jsonify({"message": f"🤖 Robot đang ngầm săn Deal Flash Sale ngành hàng '{category}' & rải link Affiliate tự động!"}), 200

@app.route('/api/hermes/memories', methods=['GET'])
def api_hermes_memories():
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customer_memories ORDER BY last_interacted_at DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200

@app.route('/api/gbrain/graph', methods=['GET'])
def api_gbrain_graph():
    from gbrain_engine import get_graph_edges
    edges = get_graph_edges(limit=25)
    return jsonify(edges), 200

@app.route('/api/affiliate/cross-sell', methods=['POST'])
def api_affiliate_cross_sell():
    data = request.json or {}
    category = data.get('category', 'Túi Xách').strip()
    cmd = ["py", "auto_upsell_engine.py", category]
    subprocess.Popen(cmd)
    return jsonify({"message": f"🎯 Robot AI đang ngầm chạy chiến dịch Cross-Sell bán chéo sản phẩm '{category}' cho tệp khách VIP!"}), 200

@app.route('/api/affiliate/export-csv', methods=['GET'])
def api_affiliate_export_csv():
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM affiliate_clicks ORDER BY last_clicked_at DESC")
    rows = cursor.fetchall()
    conn.close()

    output = "ID,Original_URL,SubID,Clicks_Count,Estimated_Commission,Last_Clicked_At\n"
    for r in rows:
        d = dict(r)
        output += f"{d.get('id')},{d.get('original_url')},{d.get('subid')},{d.get('clicks_count')},{d.get('est_commission')},{d.get('last_clicked_at')}\n"

    from flask import Response
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=affiliate_revenue_report.csv"}
    )

@app.route('/api/hermes-studio/dashboard', methods=['GET'])
def api_hermes_studio_dashboard():
    from hermes_studio_engine import get_hermes_studio_dashboard_payload
    payload = get_hermes_studio_dashboard_payload()
    return jsonify(payload), 200

@app.route('/api/gws/sync-sheets', methods=['POST'])
def api_gws_sync_sheets():
    from gws_engine import export_leads_to_google_sheets, sync_calendar_events
    f_csv = export_leads_to_google_sheets()
    f_ics = sync_calendar_events()
    return jsonify({"message": "📊 Đã đồng bộ toàn bộ Báo cáo Doanh Thu & Lịch Đăng Bài sang định dạng Google Workspace (GWS) thành công!"}), 200

@app.route('/api/gws/send-digest', methods=['POST'])
def api_gws_send_digest():
    data = request.json or {}
    email = data.get('email', 'admin@hame.enterprise')
    from gws_engine import send_gmail_daily_digest
    send_gmail_daily_digest(email)
    return jsonify({"message": f"📧 Đã tạo & gửi Email Báo Cáo Gmail Digest thành công tới '{email}'!"}), 200

@app.route('/api/worldmonitor/brief', methods=['GET'])
def api_worldmonitor_brief():
    from worldmonitor_engine import get_worldmonitor_brief
    brief = get_worldmonitor_brief()
    return jsonify(brief), 200

@app.route('/api/mano/capture', methods=['GET'])
def api_mano_capture():
    from mano_visual_engine import analyze_gui_vision
    analysis = analyze_gui_vision()
    return jsonify(analysis), 200

@app.route('/api/mano/screenshot.jpg', methods=['GET'])
def api_mano_screenshot():
    from mano_visual_engine import get_latest_screenshot_path
    from flask import send_file
    shot_path = get_latest_screenshot_path()
    return send_file(shot_path, mimetype='image/png')

@app.route('/api/squad/matrix', methods=['GET'])
def api_squad_matrix():
    from squad_coordinator import get_squad_matrix
    return jsonify(get_squad_matrix()), 200

@app.route('/api/squad/assign', methods=['POST'])
def api_squad_assign():
    from squad_coordinator import auto_assign_squad_roles
    res = auto_assign_squad_roles()
    return jsonify(res), 200

@app.route('/api/squad/execute', methods=['POST'])
def api_squad_execute():
    data = request.json or {}
    niche = data.get('niche', 'Thời Trang Nữ')
    from squad_coordinator import trigger_coordinated_squad_workflow
    res = trigger_coordinated_squad_workflow(niche)
    return jsonify(res), 200

@app.route('/api/automation/weekly', methods=['POST'])
def api_auto_weekly():
    data = request.json or {}
    product_info = data.get('product_info', 'Ví nữ cầm tay thời trang cao cấp')
    target_id = data.get('target_id', 'profile')
    cmd = ["py", "ai_weekly_scheduler.py", product_info]
    subprocess.Popen(cmd)
    return jsonify({"message": f"AI Weekly Scheduler đang tự động sinh & rải 7 ngày bài viết cho: '{product_info}'!"}), 200

@app.route('/api/automation/health', methods=['POST'])
def api_auto_health():
    cmd = ["py", "health_backup_worker.py"]
    subprocess.Popen(cmd)
    return jsonify({"message": "Đã kích hoạt kiểm tra sức khỏe tài khoản & sao lưu CSDL!"}), 200

NURTURE_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nurture_logs.txt')

@app.route('/api/nurture/run', methods=['POST'])
def api_nurture_run():
    data = request.json or {}
    account_ids = data.get('account_ids', [])
    cmd = ["py", "nurture_engine.py"]
    if account_ids and isinstance(account_ids, list):
        ids_str = ",".join(account_ids)
        cmd.append(f"--accounts={ids_str}")
    subprocess.Popen(cmd)
    return jsonify({"message": f"Chiến dịch Nuôi Nick cho {len(account_ids) if account_ids else 'tất cả'} tài khoản đang chạy ngầm!"}), 200

@app.route('/api/nurture/stream')
def api_nurture_stream():
    """Server-Sent Events: stream log nuôi nick realtime."""
    def generate():
        last_pos = 0
        while True:
            if os.path.exists(NURTURE_LOG_FILE):
                with open(NURTURE_LOG_FILE, 'r', encoding='utf-8') as f:
                    f.seek(last_pos)
                    new_lines = f.readlines()
                    last_pos = f.tell()
                for line in new_lines:
                    line = line.strip()
                    if line:
                        yield f"data: {line}\n\n"
            time.sleep(2)
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/analytics/clicks', methods=['GET'])
def api_analytics_clicks():
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, destination_url, clicks, created_at FROM redirects ORDER BY clicks DESC LIMIT 20")
        rows = cursor.fetchall()
        redirects = [dict(r) for r in rows]
        total_clicks = sum(r['clicks'] for r in redirects) if redirects else 0
        conn.close()
        return jsonify({
            "total_clicks": total_clicks,
            "top_links": redirects
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/r/<short_id>')
def redirect_shortener(short_id):
    """Rút gọn link Affiliate & đếm lượt click theo thời gian thực."""
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT destination_url, clicks FROM redirects WHERE id = ?", (short_id,))
        row = cursor.fetchone()
        if row:
            dest = row['destination_url']
            cursor.execute("UPDATE redirects SET clicks = clicks + 1 WHERE id = ?", (short_id,))
            conn.commit()
            conn.close()
            return redirect(dest)
        conn.close()
    except Exception as e:
        print("Error in redirect link:", e)
    return redirect("https://shopee.vn")

@app.route('/api/openall', methods=['GET', 'POST'])
def api_openall():
    """Bật toàn bộ Trình Duyệt Ảo Chromium cho tất cả 10 nick trong cơ sở dữ liệu."""
    try:
        import multibrowser_engine
        res = multibrowser_engine.launch_all_browsers()
        return jsonify({'success': True, 'message': 'Đã bật thành công Trình duyệt ảo cho tất cả tài khoản active!', 'details': res})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/openbrowser/<account_id>', methods=['GET', 'POST'])
def api_openbrowser(account_id):
    """Bật Trình Duyệt Ảo Chromium cho 1 tài khoản cụ thể."""
    try:
        import multibrowser_engine
        res = multibrowser_engine.launch_single_account_browser(account_id)
        return jsonify({'success': True, 'message': f'Đã bật Trình duyệt ảo cho tài khoản {account_id}!', 'details': res})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ruview/pulse', methods=['GET'])
def api_ruview_pulse():
    """Thu thập nhịp đập sức khoẻ & chỉ số hạ tầng thời gian thực theo công nghệ RuView."""
    try:
        import ruview_telemetry_engine
        res = ruview_telemetry_engine.capture_ruview_system_telemetry()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/ruview/telemetry-report', methods=['GET'])
def api_ruview_telemetry_report():
    """Xem báo cáo đo lường chỉ số vận hành chi tiết RuView."""
    try:
        import ruview_telemetry_engine
        res = ruview_telemetry_engine.capture_ruview_system_telemetry()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/videos/schedule-daily', methods=['POST', 'GET'])
def api_videos_schedule_daily():
    """Tự động tạo & lên lịch 4 AI Videos/ngày cho từng nick (3 Video Ngách + 1 Video Web)."""
    try:
        import daily_ai_video_dispatcher
        res = daily_ai_video_dispatcher.generate_daily_ai_videos_matrix()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/comments/schedule-web-intro', methods=['POST', 'GET'])
def api_comments_schedule_web_intro():
    """Tự động lên lịch 10 bình luận/nick giới thiệu trang web tên miền riêng cho từng tài khoản."""
    try:
        import website_intro_commenter
        res = website_intro_commenter.dispatch_10_intro_comments_per_account()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/domain/publish-netlify-cloud', methods=['POST', 'GET'])
def api_domain_publish_netlify_cloud():
    """Đóng gói & Đồng bộ 100% đường link Landing Page lên miền đám mây Netlify 24/7."""
    try:
        import netlify_cloud_publisher
        res = netlify_cloud_publisher.publish_all_landings_to_netlify()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/domain/set-netlify', methods=['POST', 'GET'])
def api_domain_set_netlify():
    """Cấu hình miền đám mây Netlify miễn phí 24/7 (ví dụ https://lolishop-landing.netlify.app)."""
    try:
        data = request.json if request.is_json else request.args
        domain = data.get('domain', 'https://lolishop-landing.netlify.app')
        import netlify_domain_deploy_engine
        res = netlify_domain_deploy_engine.set_netlify_cloud_domains(domain)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/domain/bind-public', methods=['POST', 'GET'])
def api_domain_bind_public():
    """Thay đổi Tên Miền Công Cộng Toàn Cầu để khách ngoài Internet (4G/Wi-Fi) truy cập 24/7."""
    try:
        data = request.json if request.is_json else request.args
        domain = data.get('domain', 'https://lolishop-landing.netlify.app')
        import public_tunnel_manager
        res = public_tunnel_manager.set_custom_public_domain(domain)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/shopee/compile-100-hot-landings', methods=['POST', 'GET'])
def api_shopee_compile_100_hot_landings():
    """Tự động biên dịch Landing Page thu hút siêu sắc nét với 100 sản phẩm HOT/trang theo ngạch."""
    try:
        import hot_catalog_landing_compiler
        res = hot_catalog_landing_compiler.compile_100_hot_landing_pages()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/domain/configure-custom', methods=['POST', 'GET'])
def api_domain_configure_custom():
    """Tự động đổi tên miền riêng (Custom Domain) cho Landing Page giúp khách truy cập 24/7 khi tắt máy."""
    try:
        data = request.json if request.is_json else request.args
        domain = data.get('domain', 'https://lolishop.online')
        import domain_cloud_setup_engine
        res = domain_cloud_setup_engine.configure_custom_domain_for_landings(domain)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/shopee/build-account-landings', methods=['POST', 'GET'])
def api_shopee_build_account_landings():
    """Tự động cào gian hàng Shopee & biên dịch Landing Page riêng từng nick theo ngạch sản phẩm."""
    try:
        import account_shopee_landing_builder
        res = account_shopee_landing_builder.build_per_account_shopee_landings()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/quota/schedule-daily', methods=['POST', 'GET'])
def api_quota_schedule_daily():
    """Khởi tạo & Lên lịch chỉ tiêu Hàng Ngày cho 10 Nick (10 Bài/Nick, 10 Cmt/Nick, 30 DMs/Nick)."""
    try:
        import daily_quota_scheduler
        res = daily_quota_scheduler.generate_and_schedule_daily_quotas()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/messenger/auto-consult', methods=['POST', 'GET'])
def api_messenger_auto_consult():
    """Tự động nhắn tin tư vấn khách hàng theo từng ngành hàng và từng nhóm sản phẩm."""
    try:
        import messenger_auto_consultant
        res = messenger_auto_consultant.auto_consult_and_send_messages()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/agent-r/reflect-and-optimize', methods=['POST', 'GET'])
def api_agent_r_reflect_and_optimize():
    """Tự động phân tích MCTS & tự sửa lỗi bài rải deal theo công nghệ ByteDance Agent-R."""
    try:
        data = request.json if request.is_json else request.args
        text = data.get('text', 'Sản phẩm Balo Laptop Oxford giảm giá 50%')
        import agent_r_mcts_engine
        res = agent_r_mcts_engine.agent_r_self_reflect_and_splice(text)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/niche/dispatch-groups', methods=['POST', 'GET'])
def api_niche_dispatch_groups():
    """Phân loại và tự động rải bài tới 12 Hội Nhóm Công Khai theo 4 Ngành hàng chủ lực."""
    try:
        import niche_group_dispatcher
        res = niche_group_dispatcher.seed_niche_groups_and_dispatch_posts()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/dive/optimize-prompt', methods=['POST', 'GET'])
def api_dive_optimize_prompt():
    """Biên dịch Prompt CoT & Tiêm tri thức sản phẩm theo công nghệ Dive-into-LLMs."""
    try:
        data = request.json if request.is_json else request.args
        role = data.get('role', 'team_poster')
        product_name = data.get('product_name', 'Balo Laptop Chống Nước')
        price = data.get('price', '500000')
        discount_price = data.get('discount_price', '249000')
        aff_link = data.get('aff_link', 'https://shope.ee/deal123')
        import dive_into_llms_engine
        res = dive_into_llms_engine.build_dive_llm_optimized_prompt(role, product_name, price, discount_price, aff_link)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/dive/verify-guardrails', methods=['POST', 'GET'])
def api_dive_verify_guardrails():
    """Kiểm tra hàng rào an toàn & chống trôi link Affiliate từ Dive-into-LLMs."""
    try:
        data = request.json if request.is_json else request.args
        text = data.get('text', '')
        expected_link = data.get('expected_link', '')
        import dive_into_llms_engine
        res = dive_into_llms_engine.verify_dive_llm_guardrails(text, expected_link)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/apollo11/mission-status', methods=['GET'])
def api_apollo11_mission_status():
    """Kiểm tra độ ưu tiên nhiệm vụ & tính toàn vẹn CSDL theo chuẩn Apollo 11."""
    try:
        import apollo11_mission_executive
        res = apollo11_mission_executive.apollo_priority_task_executive()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/apollo11/self-heal', methods=['POST', 'GET'])
def api_apollo11_self_heal():
    """Kích hoạt quy trình tự dọn dẹp bộ nhớ & phục hồi lỗi tự động (Alarm 1202 Clear)."""
    try:
        import apollo11_mission_executive
        res = apollo11_mission_executive.apollo_self_healing_recovery()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/chat2db/query', methods=['POST', 'GET'])
def api_chat2db_query():
    """Chuyển đổi câu hỏi tự nhiên bằng tiếng Việt thành lệnh SQL truy vấn CSDL theo công nghệ Chat2DB."""
    try:
        data = request.json if request.is_json else request.args
        prompt = data.get('prompt', 'Cho tôi xem danh sách nick')
        import chat2db_sql_engine
        res = chat2db_sql_engine.query_chat2db_natural_language(prompt)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/chat2db/db-summary', methods=['GET'])
def api_chat2db_db_summary():
    """Xem tổng hợp báo cáo chỉ số kinh doanh & hiệu năng CSDL từ Chat2DB."""
    try:
        import chat2db_sql_engine
        res = chat2db_sql_engine.get_chat2db_full_insights()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/omniroute/gateway-status', methods=['GET'])
def api_omniroute_gateway_status():
    """Xem trạng thái 4 Cổng AI Providers & Auto-Fallback theo công nghệ OmniRoute."""
    try:
        import omniroute_ai_gateway
        res = omniroute_ai_gateway.get_omniroute_gateway_status()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/omniroute/generate-smart-copy', methods=['POST', 'GET'])
def api_omniroute_generate_smart_copy():
    """Biên soạn bài viết rải deal với khả năng tự động chuyển mô hình AI dự phòng tức thì."""
    try:
        data = request.json if request.is_json else request.args
        topic = data.get('topic', 'Balo Laptop Chống Nước')
        import omniroute_ai_gateway
        res = omniroute_ai_gateway.generate_copy_with_omniroute_fallback(topic)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/superfile/scan-assets', methods=['GET'])
def api_superfile_scan_assets():
    """Kiểm tra tính toàn vẹn & phân loại 43+ tệp tin tài nguyên marketing theo công nghệ Superfile."""
    try:
        import superfile_asset_manager
        res = superfile_asset_manager.scan_and_index_marketing_assets()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/ego/check-sessions', methods=['GET'])
def api_ego_check_sessions():
    """Rà soát phiên đăng nhập & Cookie bảo lưu cho 10 nick Facebook theo công nghệ Ego Lite."""
    try:
        import ego_lite_session_manager
        res = ego_lite_session_manager.audit_ego_lite_account_sessions()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/ego/keepalive-all', methods=['POST', 'GET'])
def api_ego_keepalive_all():
    """Gia hạn & duy trì phiên đăng nhập ngầm cho tất cả tài khoản Facebook."""
    try:
        import ego_lite_session_manager
        res = ego_lite_session_manager.trigger_ego_session_keepalive()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/kronos/predict-peak-hours', methods=['GET'])
def api_kronos_predict_peak_hours():
    """Dự báo Khung Giờ Vàng Chốt Đơn Affiliate dựa trên mô hình chuỗi thời gian Kronos."""
    try:
        import kronos_time_series_engine
        res = kronos_time_series_engine.predict_peak_shopping_hours()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/kronos/optimize-schedule', methods=['POST', 'GET'])
def api_kronos_optimize_schedule():
    """Tự động điều chỉnh toàn bộ bài rải deal pending vào đúng Khung Giờ Vàng mua sắm."""
    try:
        import kronos_time_series_engine
        res = kronos_time_series_engine.optimize_posts_schedule_with_kronos()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/harper/lint-post', methods=['POST', 'GET'])
def api_harper_lint_post():
    """Kiểm tra chính tả, khoảng trắng thừa & chuẩn CRO cho 1 đoạn bài viết theo công nghệ Automattic Harper."""
    try:
        data = request.json if request.is_json else request.args
        content = data.get('content', '')
        first_comment = data.get('first_comment', '')
        import harper_copy_linter
        res = harper_copy_linter.lint_and_fix_post_content(content, first_comment)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/harper/auto-fix-all', methods=['POST', 'GET'])
def api_harper_auto_fix_all():
    """Tự động rà soát & sửa lỗi chính tả/khoảng trắng thừa trọn bộ bài viết pending trong CSDL."""
    try:
        import harper_copy_linter
        res = harper_copy_linter.lint_all_pending_posts()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/architecture', methods=['GET'])
def render_likec4_architecture_page():
    """Phục vụ trang Sơ đồ kiến trúc C4 tương tác LikeC4 trực quan hoá toàn bộ hệ thống."""
    try:
        import os
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_architecture', 'architecture.html')
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}
        return "<h1>404 - Trang sơ đồ kiến trúc chưa khởi tạo</h1>", 404
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>", 500

@app.route('/api/likec4/export-dsl', methods=['POST', 'GET'])
def api_likec4_export_dsl():
    """Tự động biên dịch đặc tả kiến trúc LikeC4 DSL & cập nhật sơ đồ C4 tương tác."""
    try:
        import likec4_system_architecture
        res = likec4_system_architecture.generate_likec4_architecture()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/landing/<path:filename>', methods=['GET'])
def render_instatic_landing_page(filename):
    """Phục vụ trang Landing Page bán hàng siêu tốc Instatic (<50KB)."""
    try:
        if not filename.endswith('.html'):
            filename = f"{filename}.html"
        dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_instatic_pages')
        return send_from_directory(dir_path, filename)
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>", 500


@app.route('/api/instatic/generate-landing', methods=['POST', 'GET'])
def api_instatic_generate_landing():
    """Tự động xuất bản trọn bộ các trang Landing Page bán hàng siêu nhẹ chuẩn Instatic."""
    try:
        import instatic_landing_generator
        res = instatic_landing_generator.generate_instatic_landing_pages()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/worldmonitor/trends', methods=['GET'])
def api_worldmonitor_trends():
    """Xem trọn bộ danh sách xu hướng Hot Trends tiêu dùng từ rada World Monitor."""
    try:
        import worldmonitor_bridge
        trends = worldmonitor_bridge.fetch_worldmonitor_live_trends()
        return jsonify({'status': 'success', 'count': len(trends), 'trends': trends}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/worldmonitor/trigger-campaign', methods=['POST', 'GET'])
def api_worldmonitor_trigger_campaign():
    """Tự động bơm bài rải deal Affiliate đón đầu xu hướng World Monitor."""
    try:
        import worldmonitor_bridge
        res = worldmonitor_bridge.schedule_worldmonitor_trend_campaign()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/buzz/hivemind-status', methods=['GET'])
def api_buzz_hivemind_status():
    """Xem trạng thái mạng lưới kết nối 10 AI Agents theo công nghệ Block Buzz."""
    try:
        import block_buzz_hivemind
        res = block_buzz_hivemind.get_hivemind_agent_network()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/buzz/broadcast-event', methods=['POST', 'GET'])
def api_buzz_broadcast_event():
    """Phát sóng tín hiệu phối hợp thời gian thực giữa các AI Agents."""
    try:
        data = request.json if request.is_json else request.args
        event_type = data.get('event_type', 'NEW_DEAL_POSTED')
        payload = data.get('payload', {'post_title': 'Hot Deal ShopeeMall'})
        import block_buzz_hivemind
        res = block_buzz_hivemind.broadcast_hivemind_event(event_type, payload)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/superpowers/verify-pipeline', methods=['POST', 'GET'])
def api_superpowers_verify_pipeline():
    """Kích hoạt tiến trình Rà Soát Kỷ Luật Obra Superpowers (Quality Assurance 100%)."""
    try:
        import obra_superpowers_engine
        res = obra_superpowers_engine.run_obra_superpowers_qa()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/sitemap.xml', methods=['GET'])
def serve_sitemap_xml():
    """Phục vụ file Google Sitemap XML cho Google Bot & Bing Bot quét lập chỉ mục."""
    try:
        import os
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sitemap.xml')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read(), 200, {'Content-Type': 'application/xml; charset=utf-8'}
        return "<error>Sitemap not generated</error>", 404
    except Exception as e:
        return f"<error>{str(e)}</error>", 500

@app.route('/robots.txt', methods=['GET'])
def serve_robots_txt():
    """Phục vụ file robots.txt chỉ dẫn Google Bot cào sitemap."""
    robots_content = "User-agent: *\nAllow: /\nSitemap: http://localhost:5000/sitemap.xml\n"
    return robots_content, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/api/seo/generate-product-cluster', methods=['POST', 'GET'])
def api_seo_generate_product_cluster():
    """Tự động tạo cụm bài viết liên quan sản phẩm (Topic Cluster) & cập nhật Google Sitemap XML."""
    try:
        import google_indexing_cluster_engine
        res = google_indexing_cluster_engine.generate_product_cluster_and_sitemap()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/seo/<slug>', methods=['GET'])
def render_seo_page(slug):
    """Phục vụ trang bài viết chuẩn SEO Google công khai cho người đọc & Google Bot lập chỉ mục."""
    try:
        import sqlite3, os
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_seo_pages', f"{slug}.html")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}
        return "<h1>404 - Trang SEO Google không tồn tại</h1>", 404
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>", 500

@app.route('/api/seo/generate-top-ranking-articles', methods=['POST', 'GET'])
def api_seo_generate_top_ranking_articles():
    """Tự động viết bài chuẩn SEO Top 1 Google & AI Search kèm link Affiliate Shopee & Lazada."""
    try:
        import google_seo_top_ranking_engine
        res = google_seo_top_ranking_engine.generate_seo_articles()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/ad-copywriter/generate-trending', methods=['POST', 'GET'])
def api_ad_copywriter_generate_trending():
    """Tự động phân tích từ khoá tìm kiếm hot trên Google & viết bài quảng cáo viral thu hút người đọc."""
    try:
        import google_trend_ad_copywriter
        res = google_trend_ad_copywriter.generate_google_trending_ads()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/markitdown/import', methods=['POST', 'GET'])
def api_markitdown_import():
    """Tự động bóc tách tài liệu Excel/Word/CSV theo công nghệ Microsoft MarkItDown thành bài rải Affiliate."""
    try:
        import markitdown_importer
        res = markitdown_importer.parse_and_import_document('imported_catalog.xlsx', 'xlsx')
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/addy/webperf', methods=['POST', 'GET'])
def api_addy_webperf():
    """Slash Command /webperf: Tối ưu hoá index CSDL & Tốc độ phản hồi Web."""
    import addy_skills_engine
    return jsonify(addy_skills_engine.execute_webperf_audit()), 200

@app.route('/api/addy/code-simplify', methods=['POST', 'GET'])
def api_addy_code_simplify():
    """Slash Command /code-simplify: Dọn dẹp bản ghi rác & Nhật ký cũ."""
    import addy_skills_engine
    return jsonify(addy_skills_engine.execute_code_simplify()), 200

@app.route('/api/addy/ship', methods=['POST', 'GET'])
def api_addy_ship():
    """Slash Command /ship: Kiểm tra điều kiện triển khai Production 100%."""
    import addy_skills_engine
    return jsonify(addy_skills_engine.execute_ship_check()), 200

@app.route('/api/video/auto-generate-and-post', methods=['POST', 'GET'])
def api_video_auto_generate_and_post():
    """Tự động sáng tạo Video sản phẩm AI Reels/TikTok & Lên lịch rải bài Affiliate tự động."""
    try:
        import ai_video_marketing_pipeline
        res = ai_video_marketing_pipeline.generate_video_and_schedule_campaign()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/codebuff/run-multiagent', methods=['POST', 'GET'])
def api_codebuff_run_multiagent():
    """Kích hoạt tiến trình Đa Tác Nhân Codebuff (4 Sub-Agents: Extractor, Planner, Editor, Reviewer)."""
    try:
        import codebuff_orchestrator
        res = codebuff_orchestrator.run_codebuff_pipeline()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/recommendations', methods=['GET', 'POST'])
def api_recommendations():
    """Tự động phân tích sản phẩm & gợi ý các sản phẩm bán chéo (Cross-Sell) Affiliate tăng doanh thu."""
    try:
        data = request.json if request.is_json else request.args
        query = data.get('query', 'balo laptop').strip()
        import ai_recommendation_engine
        res = ai_recommendation_engine.get_smart_recommendations(query)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    import sys
    port = int(os.environ.get("PORT", 5000))
    if len(sys.argv) > 2 and sys.argv[1] == '--port':
        port = int(sys.argv[2])
    print(f"Launching FBPoster v1.1 at http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)


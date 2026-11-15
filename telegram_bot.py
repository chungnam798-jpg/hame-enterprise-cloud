import time
import threading
import requests
import json
import uuid
import os
import re
from datetime import datetime

# Import database module from the current folder
import database
# Import automation modules
from automation import scrape_shopee_product

def make_shopee_affiliate_link(url, settings):
    if not url:
        return url
    aff_id = settings.get('shopee_affiliate_id', '').strip()
    sub_id = settings.get('shopee_sub_id', '').strip()
    if not aff_id:
        return url
    
    if 'shopee.vn' in url or 'shope.ee' in url or 's.shopee.vn' in url:
        if 'an_redir' in url:
            return url
        import urllib.parse
        encoded_url = urllib.parse.quote(url, safe='')
        return f"https://s.shopee.vn/an_redir?origin_link={encoded_url}&affiliate_id={aff_id}&sub_id={sub_id}"
    return url

def call_claude(api_key, prompt):
    """Calls Claude API with requests and model fallbacks."""
    models = ["claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key,
        'anthropic-version': '2023-06-01'
    }
    for model in models:
        payload = {
            "model": model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data['content'][0]['text'].strip()
            else:
                print(f"[Claude-Helper] Model {model} failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[Claude-Helper] Model {model} error: {e}")
            
    raise Exception("All Claude models failed.")

def call_gemini(api_key, prompt):
    """Unified AI helper routing to Gemini or Claude in Telegram Bot."""
    try:
        settings = database.get_settings()
    except Exception:
        settings = {}
        
    ai_engine = settings.get('ai_engine', 'gemini')
    claude_key = settings.get('claude_api_key', '').strip()
    
    if ai_engine == 'claude' and claude_key:
        print("[TeleBot-AI] Routing to Claude...")
        try:
            return call_claude(claude_key, prompt)
        except Exception as err:
            print(f"[TeleBot-AI] Claude failed: {err}. Falling back to Gemini...")

    # Gemini call actual
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if response.status_code == 200:
        data = response.json()
        try:
            return data['candidates'][0]['content']['parts'][0]['text'].strip()
        except:
            raise Exception("Failed to parse Gemini response.")
    else:
        raise Exception(f"Gemini API returned status code {response.status_code}: {response.text}")

def send_telegram_message(token, chat_id, text, parse_mode='HTML', reply_markup=None):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        res = requests.post(url, json=payload, timeout=10)
        return res.json()
    except Exception as e:
        print(f"[TeleBot] Error sending message: {e}")
        return None

def send_telegram_photo(token, chat_id, photo_path, caption=None, parse_mode='HTML', reply_markup=None):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    if not os.path.exists(photo_path):
        return send_telegram_message(token, chat_id, caption or "", reply_markup=reply_markup)
        
    try:
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id, 'parse_mode': parse_mode}
            if caption:
                data['caption'] = caption
            if reply_markup:
                data['reply_markup'] = json.dumps(reply_markup)
            res = requests.post(url, data=data, files=files, timeout=15)
            return res.json()
    except Exception as e:
        print(f"[TeleBot] Error sending photo: {e}")
        # Fallback to message
        if caption:
            send_telegram_message(token, chat_id, caption)
        return None

def notify_user(msg, photo_path=None):
    """Sends notification to Telegram if enabled and credentials are set"""
    try:
        settings = database.get_settings()
        enabled = settings.get('telegram_enabled', '0') == '1'
        token = settings.get('telegram_token', '').strip()
        chat_id = settings.get('telegram_chat_id', '').strip()
        
        if enabled and token and chat_id:
            if photo_path and os.path.exists(photo_path):
                send_telegram_photo(token, chat_id, photo_path, msg)
            else:
                send_telegram_message(token, chat_id, msg)
    except Exception as e:
        print(f"[TeleBot] Notification error: {e}")

def process_shopee_import_via_bot(url, token, chat_id, target_platform='facebook'):
    try:
        settings = database.get_settings()
        api_key = settings.get('gemini_api_key', '').strip()
        
        # Check duplicate
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM redirects WHERE destination_url=?", (url,))
        dup_redir = cursor.fetchone()
        cursor.execute("SELECT id FROM posts WHERE content LIKE ?", (f"%{url}%",))
        dup_post = cursor.fetchone()
        conn.close()
        
        if dup_redir or dup_post:
            send_telegram_message(token, chat_id, "⚠️ Liên kết này đã tồn tại trong hệ thống. Bỏ qua trùng lặp.")
            return

        # Scrape
        product = scrape_shopee_product(url)
        if 'error' in product or not product.get('title'):
            send_telegram_message(token, chat_id, f"❌ Cào dữ liệu thất bại: {product.get('error', 'Không lấy được tiêu đề sản phẩm')}")
            return
            
        title = product.get('title')
        description = product.get('description', '')
        
        # Gemini write
        if api_key:
            prompt = (
                f"Hãy viết một bài viết quảng cáo giới thiệu sản phẩm cực kỳ thu hút, kích thích tò mò để đạt TỶ LỆ CLICK VÀO LINK CAO NHẤT dựa trên thông tin sản phẩm này:\n"
                f"Tiêu đề: {product.get('title')}\n"
                f"Mô tả: {product.get('description', '')[:1000]}\n\n"
                f"Yêu cầu:\n"
                f"- CHỈ trả về nội dung bài viết quảng cáo trực tiếp. KHÔNG viết lời mở đầu, KHÔNG viết lời chào hay bất kỳ câu giới thiệu nào khác.\n"
                f"- BẮT BUỘC phải giới thiệu thương hiệu 'Lolishop' một cách tự nhiên trong bài viết (ví dụ: 'Lolishop giới thiệu...', 'Sản phẩm cực hot tại Lolishop...').\n"
                f"- Tập trung 100% vào việc bán sản phẩm, mô tả công dụng, tính năng nổi bật.\n"
                f"- Ngắn gọn, có dùng emoji phù hợp.\n"
                f"- Có lời kêu gọi hành động (Call to Action) bấm vào link/hình ảnh ở dưới để mua sản phẩm từ Lolishop.\n"
                f"- Không được kèm liên kết gốc trong nội dung bài viết."
            )
            try:
                post_content = call_gemini(api_key, prompt)
            except Exception as ai_err:
                post_content = f"🔥 {title} 🔥\n\nSản phẩm cực chất, click ngay để mua với giá ưu đãi!"
        else:
            post_content = f"🔥 {title} 🔥\n\nSản phẩm cực chất, click ngay để mua với giá ưu đãi!"
            
        # Media setup
        post_id = 'post_' + str(uuid.uuid4())[:8]
        media_list = []
        
        # Extract images
        scraped_images = product.get('image_urls', [])
        if not scraped_images and product.get('image_url'):
            scraped_images = [product.get('image_url')]
            
        tele_auto_video = settings.get('tele_auto_video', '1') == '1'
        local_first_image = None
        upload_dir = 'static/uploads'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
            
        if tele_auto_video and len(scraped_images) > 0:
            send_telegram_message(token, chat_id, f"🎬 Đang tự động tạo Video 30s cho sản phẩm: {title[:30]}...")
            import video_generator
            video_filename = f"video_{post_id}.mp4"
            video_output_path = os.path.join(upload_dir, video_filename)
            res = video_generator.create_video(scraped_images, title, "", video_output_path)
            
            if isinstance(res, tuple) and res[0] is None:
                send_telegram_message(token, chat_id, f"⚠️ Lỗi tạo Video: {res[1]}. Hệ thống sẽ chuyển sang dùng ảnh tĩnh.")
                tele_auto_video = False # Fallback
            elif res:
                media_list.append(f"uploads/{video_filename}")
                local_first_image = video_output_path
            else:
                tele_auto_video = False

        if not tele_auto_video:
            # Download up to 2 images
            import urllib.request
            for idx, img_u in enumerate(scraped_images[:2]):
                local_image_name = f"shopee_{post_id}_{idx}.jpg"
                local_image_path = os.path.join(upload_dir, local_image_name)
                try:
                    req = urllib.request.Request(
                        img_u, 
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    )
                    with urllib.request.urlopen(req, timeout=15) as response, open(local_image_path, 'wb') as out_file:
                        out_file.write(response.read())
                    media_list.append(f"uploads/{local_image_name}")
                    if idx == 0:
                        local_first_image = local_image_path
                except Exception as img_err:
                    print(f"[TeleBot] Error downloading image {idx}: {img_err}")

        # Link in comment setup
        shopee_auto_comment = settings.get('shopee_auto_comment_link', '1') == '1'
        first_comment = None
        aff_url = make_shopee_affiliate_link(url, settings)
        if shopee_auto_comment:
            comment_template = settings.get('shopee_comment_template', 'Link mua sản phẩm tại đây nhé cả nhà: {link}')
            first_comment = comment_template.replace('{link}', aff_url)
        else:
            post_content = f"{post_content}\n\n👉 Mua ngay tại đây: {aff_url}"

        # Setup scheduling parameters
        from datetime import timedelta
        import random
        delay_minutes = int(settings.get('shopee_poster_delay_minutes', 15))
        
        conn = database.get_db_connection()
        cursor = conn.cursor()
        # Setup scheduling parameters
        from datetime import timedelta
        import random
        
        golden_hours = [(7, 9), (11, 13), (19, 22)]
        
        def generate_slots(start_time, count):
            slots = []
            curr = start_time
            while len(slots) < count:
                segments = []
                for day_offset in [0, 1, 2]:
                    base_day = (curr + timedelta(days=day_offset)).replace(minute=0, second=0, microsecond=0)
                    segments.append((base_day.replace(hour=7), base_day.replace(hour=9)))
                    segments.append((base_day.replace(hour=11), base_day.replace(hour=13)))
                    segments.append((base_day.replace(hour=19), base_day.replace(hour=22)))
                
                valid_segments = []
                for start, end in segments:
                    if end > curr:
                        act_start = max(start, curr)
                        if act_start < end:
                            valid_segments.append((act_start, end))
                
                valid_segments.sort()
                
                day_segments = []
                limit = curr + timedelta(hours=24)
                for start, end in valid_segments:
                    if start < limit:
                        day_segments.append((start, min(end, limit)))
                
                if not day_segments:
                    day_segments = [(curr, curr + timedelta(hours=24))]
                
                total_min = sum((end - start).total_seconds() / 60 for start, end in day_segments)
                
                if count > 1:
                    step = total_min / count
                else:
                    step = total_min / 2
                
                for i in range(count):
                    target_min = step * (i + 0.5)
                    temp_acc = 0
                    slot_time = None
                    for start, end in day_segments:
                        seg_len = (end - start).total_seconds() / 60
                        if temp_acc + seg_len >= target_min:
                            diff = target_min - temp_acc
                            slot_time = start + timedelta(minutes=diff)
                            break
                        temp_acc += seg_len
                    if not slot_time:
                        slot_time = day_segments[-1][1] - timedelta(minutes=5)
                    slots.append(slot_time)
                break
            
            slots.sort()
            return slots

        # Batch setup
        batch_id = 'batch_' + str(uuid.uuid4())[:8]
        total_scheduled = 0
        platforms_target = []

        # Platform 1: Facebook
        if target_platform in ['facebook', 'both']:
            active_accounts = [a for a in database.get_accounts() if a['status'] == 'active' and a.get('platform', 'facebook') == 'facebook']
            if active_accounts:
                shopee_account_id = settings.get('shopee_poster_account_id', '').strip()
                fb_account_id = shopee_account_id if shopee_account_id else active_accounts[0]['id']
                fb_account_name = next((a['name'] for a in active_accounts if a['id'] == fb_account_id), "Unknown")
                
                # Fetch all target lists and their names to classify groups by product niche
                conn = database.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT name, targets FROM target_lists")
                target_lists_raw = cursor.fetchall()
                conn.close()
                
                target_lists_dict = {}
                for name, targets_str in target_lists_raw:
                    groups = []
                    seen = set()
                    for line in targets_str.split('\n'):
                        line = line.strip()
                        if line.startswith('http') and 'facebook.com/groups/' in line:
                            if line not in seen:
                                seen.add(line)
                                slug = line.rstrip('/').split('/')[-1]
                                groups.append({"url": line, "slug": slug})
                    if groups:
                        target_lists_dict[name] = groups
                        
                matched_category = None
                if api_key and target_lists_dict:
                    categories_list = list(target_lists_dict.keys())
                    categories_text = "\n".join([f"{i+1}. {cat}" for i, cat in enumerate(categories_list)])
                    ai_prompt = (
                        f"Hãy phân loại sản phẩm dưới đây vào một trong các danh mục có sẵn của người dùng để chọn nhóm đăng bài phù hợp.\n\n"
                        f"SẢN PHẨM:\n"
                        f"- Tên: {title}\n"
                        f"- Mô tả: {description[:500]}\n\n"
                        f"DANH SÁCH DANH MỤC CÓ SẴN:\n{categories_text}\n\n"
                        f"Yêu cầu:\n"
                        f"- Chọn duy nhất một danh mục phù hợp nhất với ngạch sản phẩm này.\n"
                        f"- Chỉ phản hồi TÊN CHÍNH XÁC của danh mục được chọn (ví dụ: 'Gia dụng'). Không viết thêm lời giải thích nào khác."
                    )
                    try:
                        ai_res = call_gemini(api_key, ai_prompt).strip()
                        for cat in categories_list:
                            if cat.lower() in ai_res.lower() or ai_res.lower() in cat.lower():
                                matched_category = cat
                                print(f"[TeleBot] AI matched product '{title[:30]}' to category niche: '{matched_category}'")
                                break
                    except Exception as ai_err:
                        print(f"[TeleBot] AI category classification error: {ai_err}")
                
                # Filter groups by matched category niche
                all_groups = []
                if matched_category and matched_category in target_lists_dict:
                    all_groups = target_lists_dict[matched_category]
                    print(f"[TeleBot] Selected {len(all_groups)} groups from category: '{matched_category}'")
                else:
                    # Fallback to combining all categories if classification failed or matched nothing
                    seen_urls = set()
                    for cat, groups in target_lists_dict.items():
                        for g in groups:
                            if g['url'] not in seen_urls:
                                seen_urls.add(g['url'])
                                all_groups.append(g)
                    print(f"[TeleBot] Fallback: selected all {len(all_groups)} combined groups across all target lists")
                                    
                # Automatically select exactly 10 joined groups from the selected niche list (rotated randomly to avoid spam)
                selected_fb_targets = []
                if all_groups:
                    import random
                    sample_size = min(10, len(all_groups))
                    chosen_groups = random.sample(all_groups, sample_size)
                    selected_fb_targets = [{"type": "group", "target_id": g['url']} for g in chosen_groups]
                else:
                    selected_fb_targets = [{"type": "profile", "target_id": "me"}]
                
                # Assign schedule times for FB (strictly within 24 hours)
                fb_slots = generate_slots(datetime.now(), len(selected_fb_targets))
                
                for i, target in enumerate(selected_fb_targets):
                    target_post_id = 'post_' + str(uuid.uuid4())[:8]
                    scheduled_at = fb_slots[i].isoformat()[:16]
                    
                    database.save_post(
                        post_id=target_post_id,
                        account_id=fb_account_id,
                        type_=target['type'],
                        target_id=target['target_id'],
                        content=post_content,
                        media=media_list,
                        scheduled_at=scheduled_at,
                        status='draft',
                        bulk_group_id=batch_id,
                        platform='facebook',
                        first_comment=first_comment
                    )
                    total_scheduled += 1
                
                platforms_target.append(f"📱 <b>Facebook</b> ({fb_account_name}): {len(selected_fb_targets)} nhóm")
            else:
                if target_platform == 'facebook':
                    send_telegram_message(token, chat_id, "❌ Không tìm thấy tài khoản Facebook nào đang hoạt động.")
                    return

        # Platform 2: Threads
        if target_platform in ['threads', 'both']:
            active_threads_accounts = [a for a in database.get_accounts() if a['status'] == 'active' and a.get('platform') == 'threads']
            if active_threads_accounts:
                threads_account = active_threads_accounts[0]
                threads_account_name = threads_account['name']
                
                threads_slots = generate_slots(datetime.now(), 1)
                scheduled_at = threads_slots[0].isoformat()[:16]
                target_post_id = 'post_' + str(uuid.uuid4())[:8]
                
                database.save_post(
                    post_id=target_post_id,
                    account_id=threads_account['id'],
                    type_='profile',
                    target_id='me',
                    content=post_content,
                    media=media_list,
                    scheduled_at=scheduled_at,
                    status='draft',
                    bulk_group_id=batch_id,
                    platform='threads',
                    first_comment=first_comment
                )
                total_scheduled += 1
                platforms_target.append(f"🧵 <b>Threads</b> ({threads_account_name}): 1 bài đăng (Trang cá nhân)")
            else:
                if target_platform == 'threads':
                    send_telegram_message(token, chat_id, "❌ Không tìm thấy tài khoản Threads nào đang hoạt động.")
                    return

        if total_scheduled == 0:
            send_telegram_message(token, chat_id, "❌ <b>HAME:</b> Đã có lỗi xảy ra. Không bài đăng nào được lên lịch.")
            return

        # Send unified Telegram notification
        platform_list_display = "\n".join([f"- {p}" for p in platforms_target])
        reply_msg = (
            f"✅ <b>AI đã soạn bài viết & lên lịch xong!</b>\n\n"
            f"📦 <b>Sản phẩm:</b> {title[:80]}...\n"
            f"🎯 <b>Nền tảng phân phối:</b>\n{platform_list_display}\n"
            f"⏰ <b>Lịch đăng:</b> Khung giờ vàng (7-9h, 11-13h, 19-22h)\n"
            f"🔗 <b>Link Affiliate:</b> Tự động bình luận dưới bài đăng\n"
            f"📊 <b>Tổng số bài chờ duyệt:</b> {total_scheduled} bài\n\n"
            f"📝 <b>Xem trước nội dung:</b>\n<i>{post_content[:150]}...</i>\n\n"
            f"⚠️ <b>VUI LÒNG PHÊ DUYỆT ĐỂ BẮT ĐẦU ĐĂNG!</b>"
        )
        
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "✅ Phê duyệt Đăng", "callback_data": f"approve_{batch_id}"},
                    {"text": "❌ Hủy bỏ", "callback_data": f"cancel_{batch_id}"}
                ]
            ]
        }
        
        if local_first_image and os.path.exists(local_first_image):
            send_telegram_photo(token, chat_id, local_first_image, reply_msg, reply_markup=reply_markup)
        else:
            send_telegram_message(token, chat_id, reply_msg, reply_markup=reply_markup)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        send_telegram_message(token, chat_id, f"❌ <b>Lỗi hệ thống HAME:</b> {e}")
            
    except Exception as e:
        send_telegram_message(token, chat_id, f"❌ <b>Lỗi hệ thống HAME:</b> {e}")

def register_telegram_bot_commands(token):
    if not token:
        return
    url = f"https://api.telegram.org/bot{token}/setMyCommands"
    commands = [
        {"command": "auto500", "description": "⚡ Kích hoạt Đăng Tự Động 500 Tác vụ/Ngày (100 Bài, 100 Cmt, 300 DMs)"},
        {"command": "flashsale", "description": "💰 Săn Deal Shopee Flash Sale >50% & rải link Affiliate"},
        {"command": "affstats", "description": "📈 Báo cáo lượt click & hoa hồng Affiliate dự kiến"},

        {"command": "crosssell", "description": "🎯 AI nhắn tin giảm 30% bán chéo cho tệp khách VIP cũ"},
        {"command": "gwsheet", "description": "📊 Xuất báo cáo doanh thu & lịch 7 ngày ra Google Sheets"},
        {"command": "gmail", "description": "📧 Gửi bản tin báo cáo doanh thu HTML về Gmail admin"},
        {"command": "radar", "description": "🌍 Phân tích xu hướng & tin hot toàn cầu từ World Monitor"},
        {"command": "snap", "description": "👁️ Chụp ảnh màn hình live làm việc ngầm của Playwright"},
        {"command": "reengage", "description": "🔄 AI bám đuổi các inbox Messenger ngưng tương tác >48h"},
        {"command": "joingroups", "description": "🔍 Tự động tìm & gửi yêu cầu gia nhập Nhóm Facebook ngách"},
        {"command": "createvideo", "description": "🎬 AI tự tạo video ngắn quảng cáo & rải bài đa kênh"},
        {"command": "targetfriends", "description": "🎯 Bóc danh sách bạn bè đối thủ & tự động kết bạn"},
        {"command": "inbox", "description": "🤖 AI tự động tư vấn chốt đơn Messenger 24/7"},
        {"command": "accounts", "description": "👤 Danh sách tài khoản Facebook đang quản lý"},
        {"command": "stats", "description": "📈 Báo cáo thống kê tổng quan hệ thống"},
        {"command": "nurture", "description": "🌱 Kích hoạt tiến trình nuôi nick tăng Trust Score"},
        {"command": "weekly", "description": "📅 AI lập lịch 7 ngày bài viết rải link AIDA"},
        {"command": "status", "description": "🖥️ Kiểm tra sức khỏe & trạng thái cỗ máy"}
    ]
    try:
        import requests
        requests.post(url, json={"commands": commands}, timeout=10)
    except Exception as e:
        pass

def run_telegram_polling():
    print("[TeleBot] Telegram Bot Polling Thread started.")
    offset = 0
    sent_initial_menu = False
    
    while True:
        try:
            settings = database.get_settings()
            enabled = settings.get('telegram_enabled', '0') == '1'
            token = settings.get('telegram_token', '').strip()
            allowed_chat_id = settings.get('telegram_chat_id', '').strip()
            
            if not enabled or not token:
                time.sleep(5)
                continue

            if not sent_initial_menu:
                register_telegram_bot_commands(token)

            # Tự động gửi bàn phím phím tắt lên điện thoại sếp ngay khi bot kết nối
            reply_keyboard_markup = {
                "keyboard": [
                    [{"text": "💰 Săn Deal Flash Sale"}, {"text": "📈 Doanh Thu Affiliate"}],
                    [{"text": "🎯 AI Cross-Sell"}, {"text": "📊 Google Sheets Sync"}],
                    [{"text": "📧 Gmail Digest Report"}, {"text": "🌍 World Monitor Radar"}],
                    [{"text": "👁️ Chụp Màn Hình Live"}, {"text": "🔄 Chăm Sóc Khách Cũ AI"}],
                    [{"text": "🔍 Tìm & Join Nhóm Ngách"}, {"text": "🎬 Tạo Video AI & Đăng"}],
                    [{"text": "🎯 Bóc Bạn Bè Đối Thủ"}, {"text": "🤖 AI Auto-Closer Inbox"}],
                    [{"text": "🌱 Nuôi Nick Facebook"}, {"text": "📅 AI Lập Lịch 7 Ngày"}],
                    [{"text": "👤 Tài Khoản"}, {"text": "🖥️ Trạng Thái"}]
                ],
                "resize_keyboard": True,
                "persistent": True
            }
            if not sent_initial_menu and allowed_chat_id:
                send_telegram_message(token, allowed_chat_id, "📲 <b>Bàn phím điều hành HAME v28.0 Enterprise đã được kích hoạt!</b>\nToàn bộ 16 phím tắt công cụ đã hiển thị trực tiếp ở khung chat bên dưới trên điện thoại sếp.", reply_markup=reply_keyboard_markup)
                sent_initial_menu = True
                
            # Request updates
            url = f"https://api.telegram.org/bot{token}/getUpdates?offset={offset}&timeout=5"
            try:
                res = requests.get(url, timeout=10)
            except Exception as conn_err:
                print(f"[TeleBot] Network error (Timeout). Retrying in 10s...")
                time.sleep(10)
                continue
                
            if res.status_code != 200:
                if res.status_code == 409:
                    print(f"[TeleBot] 409 Conflict: Another bot instance is running. Retrying in 15s...")
                    time.sleep(15)
                else:
                    print(f"[TeleBot] Bad status code: {res.status_code}")
                    time.sleep(10)
                continue
                
            data = res.json()
            if not data.get('ok'):
                print(f"[TeleBot] API error: {data.get('description')}")
                time.sleep(10)
                continue
                
            updates = data.get('result', [])
            for update in updates:
                offset = update['update_id'] + 1
                
                # Handle callback query
                callback_query = update.get('callback_query')
                if callback_query:
                    offset = update['update_id'] + 1
                    data_str = callback_query.get('data', '')
                    cb_chat_id = callback_query['message']['chat']['id']
                    cb_msg_id = callback_query['message']['message_id']
                    
                    # Answer to stop loading indicator
                    try:
                        requests.post(f"https://api.telegram.org/bot{token}/answerCallbackQuery", json={"callback_query_id": callback_query['id']}, timeout=5)
                    except: pass

                    if data_str.startswith('approve_'):
                        batch_id = data_str.replace('approve_', '')
                        conn = database.get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE posts SET status='pending' WHERE bulk_group_id=? AND status='draft'", (batch_id,))
                        rows_affected = cursor.rowcount
                        conn.commit()
                        conn.close()
                        
                        # Remove inline keyboard
                        edit_url = f"https://api.telegram.org/bot{token}/editMessageReplyMarkup"
                        requests.post(edit_url, json={"chat_id": cb_chat_id, "message_id": cb_msg_id, "reply_markup": {"inline_keyboard": []}})
                        
                        send_telegram_message(token, cb_chat_id, f"✅ Đã phê duyệt! Hệ thống sẽ bắt đầu đăng {rows_affected} bài vào danh sách đăng.")
                        
                    elif data_str.startswith('cancel_'):
                        batch_id = data_str.replace('cancel_', '')
                        conn = database.get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM posts WHERE bulk_group_id=? AND status='draft'", (batch_id,))
                        conn.commit()
                        conn.close()
                        
                        # Remove inline keyboard
                        edit_url = f"https://api.telegram.org/bot{token}/editMessageReplyMarkup"
                        requests.post(edit_url, json={"chat_id": cb_chat_id, "message_id": cb_msg_id, "reply_markup": {"inline_keyboard": []}})
                        
                        send_telegram_message(token, cb_chat_id, f"❌ Đã hủy đăng bài.")
                        
                    elif data_str.startswith('plat_'):
                        # Format: plat_{platform}_{import_id}
                        parts = data_str.split('_', 2)
                        platform = parts[1]
                        import_id = parts[2]
                        
                        settings = database.get_settings()
                        shopee_url = settings.get(f'temp_url_{import_id}')
                        if not shopee_url:
                            send_telegram_message(token, cb_chat_id, "❌ Yêu cầu nhập đã hết hạn hoặc không tồn tại. Vui lòng gửi lại link.")
                            continue
                            
                        # Delete to prevent double clicking
                        database.delete_setting(f'temp_url_{import_id}')
                        
                        # Edit message to remove markup and show status
                        edit_url = f"https://api.telegram.org/bot{token}/editMessageText"
                        platform_name = {
                            'facebook': 'Facebook',
                            'threads': 'Threads',
                            'both': 'Facebook & Threads'
                        }.get(platform, platform)
                        
                        requests.post(edit_url, json={
                            "chat_id": cb_chat_id,
                            "message_id": cb_msg_id,
                            "text": f"📥 <b>HAME:</b> Đã chọn {platform_name}. Đang cào dữ liệu Shopee và chuẩn bị bài đăng...",
                            "parse_mode": "HTML"
                        })
                        
                        # Start background thread to import
                        threading.Thread(
                            target=process_shopee_import_via_bot, 
                            args=(shopee_url, token, cb_chat_id, platform), 
                            daemon=True
                        ).start()
                    continue
                
                # Check message
                message = update.get('message')
                if not message:
                    continue
                    
                chat = message.get('chat', {})
                chat_id = chat.get('id')
                user = message.get('from', {})
                username = user.get('username') or user.get('first_name') or "User"
                text = (message.get('text') or '').strip()
                
                if not text:
                    continue
                    
                # Auto-bind chat ID if not configured
                if not allowed_chat_id:
                    # Save to DB settings
                    database.save_setting('telegram_chat_id', str(chat_id))
                    allowed_chat_id = str(chat_id)
                    send_telegram_message(token, chat_id, f"🎯 <b>Kết nối HAME thành công!</b>\nChat ID của bạn <code>{chat_id}</code> đã được tự động liên kết với cỗ máy kiếm tiền HAME.")
                    
                # Authorize chat
                if str(chat_id) != allowed_chat_id:
                    send_telegram_message(token, chat_id, "⚠️ <b>HAME Security:</b> Bạn không có quyền truy cập cỗ máy này.")
                    continue
                    
                print(f"[TeleBot] Received message from {username}: {text}")
                
                # Menu Keyboard (Nút bấm phím tắt)
                reply_keyboard_markup = {
                    "keyboard": [
                        [{"text": "⚡ Đăng Tự Động 600 Tác Vụ"}, {"text": "💰 Săn Deal Flash Sale Shopee"}],
                        [{"text": "📈 Doanh Thu Affiliate"}, {"text": "🌐 Rada Trend Cầu"}],
                        [{"text": "🚀 Mở 15 Trình Duyệt"}, {"text": "🚀 Bắn Auto DM"}],
                        [{"text": "🤖 AI Auto-Closer Inbox"}, {"text": "🔄 Chăm Sóc Khách Cũ AI"}],
                        [{"text": "🔍 Tìm & Join Nhóm Nhách"}, {"text": "🎬 Tạo Video AI & Đăng"}],
                        [{"text": "🎯 Bóc Bạn Bè Đối Thủ"}, {"text": "🌱 Nuôi Nick Facebook"}],
                        [{"text": "💬 Reply Comment AI"}, {"text": "👥 Kết Bạn & Duyệt Bạn"}],
                        [{"text": "📅 AI Lập Lịch 7 Ngày"}, {"text": "🖥️ Trạng Thái"}]
                    ],
                    "resize_keyboard": True,
                    "persistent": True
                }

                # Command handler
                if text.startswith('/') or text in ["⚡ Đăng Tự Động 600 Tác Vụ", "💰 Săn Deal Flash Sale Shopee", "📈 Doanh Thu Affiliate", "🌐 Rada Trend Cầu", "🚀 Mở 15 Trình Duyệt", "🚀 Bắn Auto DM", "🤖 AI Auto-Closer Inbox", "🔄 Chăm Sóc Khách Cũ AI", "🔍 Tìm & Join Nhóm Nhách", "🎬 Tạo Video AI & Đăng", "🎯 Bóc Bạn Bè Đối Thủ", "🌱 Nuôi Nick Facebook", "💬 Reply Comment AI", "👥 Kết Bạn & Duyệt Bạn", "📅 AI Lập Lịch 7 Ngày", "📊 Báo Cáo Auto DM", "📈 Thống Kê Chung", "👤 Tài Khoản", "🖥️ Trạng Thái"]:
                    cmd = text.split()[0].lower() if text.startswith('/') else text

                    if cmd in ['/auto600', '/auto500', '/schedule600', '⚡ Đăng Tự Động 600 Tác Vụ']:
                        try:
                            import daily_quota_scheduler
                            res = daily_quota_scheduler.generate_and_schedule_600_daily_quotas()
                            msg = (
                                f"⚡ <b>ĐÃ KÍCH HOẠT MA TRẬN 600 TÁC VỤ / NGÀY THÀNH CÔNG!</b>\n\n"
                                f"👥 <b>Chi Tiết Chỉ Tiêu Ma Trận 10 Nick Active:</b>\n"
                                f"• 📝 <b>Bài đăng nhóm công khai:</b> {res['total_matrix_output']['posts']} bài (10 bài/nick)\n"
                                f"• 💬 <b>Bình luận săn mã & giới thiệu Web:</b> {res['total_matrix_output']['comments']} bình luận (20 cmt/nick: 10 cmt săn mã + 10 cmt giới thiệu Web)\n"
                                f"• 📲 <b>Tin nhắn tư vấn Messenger:</b> {res['total_matrix_output']['dms']} tin nhắn (30 tin/nick)\n\n"
                                f"🛡️ <i>Tất cả bài viết & bình luận đều được dùng thuật toán chống ẩn Spintax 100%!</i>"
                            )
                            send_telegram_message(token, chat_id, msg, reply_markup=reply_keyboard_markup)
                        except Exception as ex:
                            send_telegram_message(token, chat_id, f"❌ Lỗi kích hoạt 600 tác vụ: {ex}")


                    elif cmd in ['/start', '/help', '/menu']:

                        help_text = (
                            f"🤖 <b>HAME Telegram Command Center (v19.0 Enterprise Edition)</b>\n\n"
                            f"Xin chào <b>{username}</b>! Bạn có thể điều hành toàn bộ cỗ máy bằng các phím tắt bên dưới hoặc gõ câu lệnh:\n\n"
                            f"🌐 <code>/trend</code> : Xem Rada tin tức & xu hướng hot nhất toàn cầu (World Monitor Integration)\n"
                            f"🚀 <code>/openall</code> : Mở đồng loạt 15 nick Facebook trình duyệt\n"
                            f"💰 <code>/flashsale &lt;Ngành_Hàng&gt;</code> : Tự động săn Deal Flash Sale giảm >50% & rải link Affiliate\n"
                            f"📈 <code>/affstats</code> : Xem báo cáo tổng doanh thu & hoa hồng Affiliate Shopee/Lazada\n"
                            f"🔄 <code>/reengage</code> : AI quét hội thoại Messenger cũ & nhắn tin bám đuổi chốt đơn\n"
                            f"🔍 <code>/joingroups &lt;Từ_Khóa&gt;</code> : Tự động tìm & xin gia nhập nhóm ngách\n"
                            f"🎬 <code>/createvideo &lt;Tên_SP&gt; [reels/groups/profile/all]</code> : Tạo Video AI sản phẩm & Đăng tự động\n"
                            f"🎯 <code>/targetfriends &lt;URL_Đối_Thủ&gt;</code> : Bóc tách danh sách bạn bè đối thủ & tự động gửi kết bạn\n"
                            f"🤖 <code>/inbox</code> : Bật Robot AI quét Messenger Inbox & tự động chốt đơn 24/7\n"
                            f"💬 <code>/comments</code> : Tự động trả lời bình luận hỏi hàng & nhắn tin mồi"
                        )
                        send_telegram_message(token, chat_id, help_text, reply_markup=reply_keyboard_markup)

                    elif cmd in ['/flashsale', '💰 Săn Deal Flash Sale', '💰 Săn Deal Flash Sale Shopee']:
                        parts = text.split(maxsplit=1)
                        cat = parts[1] if len(parts) > 1 else "Bán Chạy Nhất"
                        import subprocess
                        subprocess.Popen(["py", "shopee_flashsale_scraper.py", cat])
                        send_telegram_message(token, chat_id, f"💰 <b>Đã kích hoạt Flash Sale Affiliate Scraper!</b>\nRobot đang tự động quét các Deal Flash Sale giảm > 50% cho ngành <b>'{cat}'</b> và tự động rải bài chứa link Affiliate SubID...")

                    elif cmd in ['/affstats', '📈 Doanh Thu Affiliate']:
                        from affiliate_link_converter import get_affiliate_revenue_stats
                        st = get_affiliate_revenue_stats()
                        msg = (
                            f"📈 <b>BÁO CÁO DOANH THU & HOA HỒNG AFFILIATE REALTIME</b>\n\n"
                            f"🔗 <b>Tổng số Link Affiliate đã tạo:</b> {st['total_links']} link\n"
                            f"👆 <b>Tổng số Lượt Click thu về:</b> {st['total_clicks']} clicks\n"
                            f"💰 <b>Tổng Hoa Hồng Dự Kiến:</b> {st['total_commission']:,.0f} VNĐ\n\n"
                            f"🔥 <i>Cỗ máy đang rải bài liên tục để đẩy mạnh doanh số cho bạn!</i>"
                        )
                        send_telegram_message(token, chat_id, msg)

                    elif cmd in ['/squad', '🛡️ Đội Hình 15 Nick']:
                        from squad_coordinator import get_squad_matrix, auto_assign_squad_roles
                        auto_assign_squad_roles()
                        sm = get_squad_matrix()
                        teams = sm['teams']
                        squad_msg = (
                            f"🛡️ <b>HAME 15-ACCOUNT SQUAD MATRIX</b>\n"
                            f"📊 <b>Tổng số tài khoản:</b> {sm['total_accounts']} Nick\n\n"
                            f"🥇 <b>Team Profile (Chốt Đơn):</b> {len(teams['team_profile']['accounts'])}/3 Nick (Mục tiêu 5.000 bạn bè)\n"
                            f"🥈 <b>Team Poster (Flash Sale):</b> {len(teams['team_poster']['accounts'])}/7 Nick (Mục tiêu 200 Nhóm)\n"
                            f"🥉 <b>Team Seeding (Tương Tác):</b> {len(teams['team_seeding']['accounts'])}/5 Nick (Nurture 30p/ngày)\n\n"
                            f"✅ Đã tự động phân bổ và kích hoạt kịch bản tác chiến phối hợp!"
                        )
                        send_telegram_message(token, chat_id, squad_msg)

                    elif cmd in ['/reengage', '🔄 Chăm Sóc Khách Cũ AI']:
                        import subprocess
                        subprocess.Popen(["py", "auto_reengagement.py", "15"])
                        send_telegram_message(token, chat_id, "🔄 <b>Đã kích hoạt AI Re-Engagement Engine!</b>\nRobot đang ngầm quét hội thoại Messenger cũ quá 48h và dùng AI gửi tin nhắn bám đuổi chốt đơn...")

                    elif cmd in ['/gwsheet', '📊 Google Sheets Sync']:
                        from gws_engine import export_leads_to_google_sheets, sync_calendar_events
                        f_csv = export_leads_to_google_sheets()
                        f_ics = sync_calendar_events()
                        send_telegram_message(token, chat_id, "📊 <b>Đồng Bộ Google Workspace Thành Công!</b>\nDữ liệu báo cáo Leads & Lịch Đăng Bài đã được xuất sang định dạng Google Sheets & Google Calendar thành công!")

                    elif cmd in ['/gmail', '📧 Gmail Digest Report']:
                        from gws_engine import send_gmail_daily_digest
                        send_gmail_daily_digest()
                        send_telegram_message(token, chat_id, "📧 <b>Gmail Digest Created!</b>\nEmail HTML báo cáo tổng quan doanh thu đã được khởi tạo thành công!")

                    elif cmd in ['/radar', '/trend', '🌐 Rada Trend Cầu', '🌍 World Monitor Radar']:
                        try:
                            import worldmonitor_bridge
                            trends = worldmonitor_bridge.get_cached_trends()
                            lines = []
                            for idx, t in enumerate(trends[:7]):
                                lines.append(f"{idx+1}. <b>{t['source']}:</b> {t['title']}")
                            
                            radar_text = (
                                f"🌐 <b>WORLD MONITOR REAL-TIME TREND RADAR</b>\n\n"
                                f"🔥 <b>CÁC XU HƯỚNG BỎNG NGÔ TRÊN TOÀN CẦU & VIỆT NAM:</b>\n\n"
                                + "\n".join(lines) + "\n\n"
                                f"💡 <i>AI HAME tự động lấy các trend này làm Hook để rải bài bán hàng Shopee thu hút triệu view!</i>"
                            )
                            send_telegram_message(token, chat_id, radar_text)
                        except Exception as e:
                            send_telegram_message(token, chat_id, f"🌐 <b>World Monitor Trend Radar:</b> {e}")

                    elif cmd in ['/snap', '👁️ Chụp Màn Hình Live']:
                        from mano_visual_engine import get_latest_screenshot_path
                        shot_file = get_latest_screenshot_path()
                        if os.path.exists(shot_file):
                            try:
                                import requests
                                url_photo = f"https://api.telegram.org/bot{token}/sendPhoto"
                                with open(shot_file, 'rb') as f_img:
                                    requests.post(url_photo, data={'chat_id': chat_id, 'caption': '👁️ <b>Mano-P Live Screenshot Snapshot</b>'}, files={'photo': f_img}, timeout=10)
                            except Exception as e:
                                send_telegram_message(token, chat_id, f"👁️ <b>Mano-P Live Screenshot:</b> {shot_file}")
                        else:
                            send_telegram_message(token, chat_id, "⚠️ Chưa có ảnh chụp màn hình live.")

                    elif cmd in ['/joingroups', '🔍 Tìm & Join Nhóm Ngách']:
                        parts = text.split(maxsplit=1)
                        kw = parts[1] if len(parts) > 1 else "Hội bỉm sữa mua bán"
                        import subprocess
                        subprocess.Popen(["py", "auto_group_joiner.py", kw, "10"])
                        send_telegram_message(token, chat_id, f"🔍 <b>Đã kích hoạt Auto Group Joiner!</b>\nRobot đang tìm kiếm các nhóm Facebook chất lượng theo từ khóa <b>'{kw}'</b> và gửi yêu cầu gia nhập...")

                    elif cmd in ['/createvideo', '🎬 Tạo Video AI & Đăng']:
                        parts = text.split(maxsplit=2)
                        prod_title = parts[1] if len(parts) > 1 else "Ví nữ cầm tay thời trang cao cấp ELLY"
                        dest = parts[2] if len(parts) > 2 else "all"
                        import subprocess
                        subprocess.Popen(["py", "video_generator.py", prod_title, "500000", dest])
                        send_telegram_message(token, chat_id, f"🎬 <b>Đã kích hoạt AI Video Studio!</b>\nRobot đang tự động dựng video ngắn quảng cáo cho sản phẩm: <b>{prod_title}</b> và sẽ đăng lên kênh: <b>{dest.upper()}</b>...")

                    elif cmd in ['/targetfriends', '🎯 Bóc Bạn Bè Đối Thủ']:
                        parts = text.split(maxsplit=1)
                        if len(parts) < 2 and text.startswith('/'):
                            send_telegram_message(token, chat_id, "⚠️ <b>Cú pháp sai:</b>\nVui lòng dán link trang cá nhân đối thủ theo dạng:\n<code>/targetfriends https://facebook.com/profile_url</code>")
                        else:
                            target_url = parts[1] if len(parts) > 1 else "https://www.facebook.com/zuck"
                            import subprocess
                            subprocess.Popen(["py", "scrape_and_add_friends.py", target_url, "25"])
                            send_telegram_message(token, chat_id, f"🎯 <b>Đã kích hoạt Target Friend Extractor!</b>\nRobot đang ngầm bóc tách danh sách bạn bè từ đối thủ: <i>{target_url}</i> và gửi lời mời kết bạn...")

                    elif cmd in ['/comments', '💬 Reply Comment AI']:
                        import subprocess
                        subprocess.Popen(["py", "auto_reply_comments.py"])
                        send_telegram_message(token, chat_id, "💬 <b>Đã kích hoạt Auto-Reply Comment AI!</b>\nRobot đang quét bình luận bài viết và tự động trả lời kèm nhắn tin mồi cho khách...")

                    elif cmd in ['/friends', '👥 Kết Bạn & Duyệt Bạn']:
                        import subprocess
                        subprocess.Popen(["py", "auto_friend_manager.py"])
                        send_telegram_message(token, chat_id, "👥 <b>Đã kích hoạt Auto Friend Manager!</b>\nRobot đang tự động duyệt lời mời kết bạn & kết bạn với khách hàng tiềm năng...")

                    elif cmd in ['/weekly', '📅 AI Lập Lịch 7 Ngày']:
                        parts = text.split(maxsplit=1)
                        prod_name = parts[1] if len(parts) > 1 else "Ví nữ cầm tay thời trang cao cấp"
                        import subprocess
                        subprocess.Popen(["py", "ai_weekly_scheduler.py", prod_name])
                        send_telegram_message(token, chat_id, f"📅 <b>Đã kích hoạt AI Weekly Scheduler!</b>\nAI đang sinh 7 bài viết marketing chuẩn AIDA và lập lịch rải đều 7 ngày tới cho: <b>{prod_name}</b>...")

                    elif cmd in ['/inbox', '🤖 AI Auto-Closer Inbox']:
                        import subprocess
                        inbox_cmd = ["py", "auto_reply_inbox.py"]
                        subprocess.Popen(inbox_cmd)
                        send_telegram_message(token, chat_id, "🤖 <b>Đã kích hoạt AI Messenger Auto-Closer!</b>\nRobot AI đang đọc các tin nhắn phản hồi của khách trong Inbox và tự động nhắn tư vấn chốt đơn 24/7...")

                    elif cmd in ['/nurture', '🌱 Nuôi Nick Facebook']:
                        import subprocess
                        nurture_cmd = ["py", "nurture_engine.py"]
                        subprocess.Popen(nurture_cmd)
                        send_telegram_message(token, chat_id, "🌱 <b>Đã kích hoạt chiến dịch Nuôi Nick Facebook!</b>\n🤖 Bot đang ngầm lướt Bảng tin, thả tim bài viết & xem Reels tăng độ uy tín cho các nick...")

                    elif cmd in ['/autodm', '🚀 Bắn Auto DM']:
                        parts = text.split(maxsplit=2)
                        if len(parts) < 2 and text.startswith('/'):
                            send_telegram_message(token, chat_id, "⚠️ Cú pháp: <code>/autodm &lt;Link_Nhóm_FB&gt; [Link_Sản_Phẩm]</code>\nVí dụ: <code>/autodm https://www.facebook.com/groups/123456 https://shopee.vn/sp1</code>")
                            continue
                        elif not text.startswith('/'):
                            send_telegram_message(token, chat_id, "💡 Để bắn Auto DM từ Telegram, sếp hãy gõ:\n<code>/autodm &lt;Link_Nhóm_FB&gt; [Link_SP]</code>")
                            continue

                        group_url = parts[1].strip()
                        product_url = parts[2].strip() if len(parts) > 2 else ""

                        import subprocess
                        autodm_cmd = ["py", "trigger_autodm.py", "--group_url", group_url]
                        if product_url:
                            autodm_cmd.extend(["--product_url", product_url])
                        
                        subprocess.Popen(autodm_cmd)
                        send_telegram_message(token, chat_id, f"🚀 <b>Đã kích hoạt chiến dịch Auto DM!</b>\n👥 Group: {group_url}\n🛒 SP: {product_url if product_url else 'Mặc định'}\n🤖 Bot đang chạy ngầm...")

                    elif cmd in ['/followup', '🔄 Chăm Sóc Lại (Follow-up)']:
                        import subprocess
                        followup_cmd = ["py", "auto_dm_playwright.py", "--followup"]
                        subprocess.Popen(followup_cmd)
                        send_telegram_message(token, chat_id, "🔄 <b>Đã kích hoạt chiến dịch Chăm sóc lại (Follow-up)!</b>\n🤖 Bot đang kiểm tra các lead cũ và gửi tin nhắn nhắc nhở ngầm...")

                    elif cmd in ['/autodm_stats', '📊 Báo Cáo Auto DM']:
                        try:
                            leads = database.get_all_dm_leads(limit=100)
                            total_leads = len(leads)
                            success_leads = len([l for l in leads if l.get('status') == 'SUCCESS'])
                            followup_leads = len([l for l in leads if l.get('status') == 'FOLLOW_UP_SENT'])
                            var_a = len([l for l in leads if l.get('variant') == 'A'])
                            var_b = len([l for l in leads if l.get('variant') == 'B'])
                            
                            rate = round((success_leads / total_leads * 100)) if total_leads > 0 else 0
                            
                            stats_msg = (
                                f"📊 <b>BÁO CÁO AUTO DM & CRM LEADS:</b>\n\n"
                                f"👥 <b>Tổng số Lead trong Database:</b> {total_leads}\n"
                                f"✅ <b>Gửi tin nhắn thành công:</b> {success_leads}\n"
                                f"🔄 <b>Đã Follow-up chăm sóc lại:</b> {followup_leads}\n"
                                f"📈 <b>Tỷ lệ thành công:</b> {rate}%\n\n"
                                f"⚖️ <b>Phân bổ A/B Test:</b>\n"
                                f"- Variant A (Đi thẳng vấn đề): {var_a}\n"
                                f"- Variant B (Khen ngợi nịnh nọt): {var_b}"
                            )
                            send_telegram_message(token, chat_id, stats_msg)
                        except Exception as e:
                            send_telegram_message(token, chat_id, f"❌ Lỗi lấy báo cáo Auto DM: {e}")

                    elif cmd in ['/status', '🖥️ Trạng Thái']:
                        active_accounts = [a for a in database.get_accounts() if a['status'] == 'active']
                        pending_count = len(database.get_posts_by_status('pending'))
                        
                        conn = database.get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT SUM(clicks) FROM redirects")
                        res_clicks = cursor.fetchone()
                        total_clicks = res_clicks[0] if res_clicks and res_clicks[0] is not None else 0
                        conn.close()
                        
                        status_text = (
                            f"🖥️ <b>Trạng thái hệ thống HAME:</b>\n"
                            f"● <b>Máy chủ chính:</b> 🟢 Đang hoạt động tốt\n"
                            f"● <b>Tài khoản Facebook:</b> 🟢 {len(active_accounts)} hoạt động\n"
                            f"● <b>Hàng đợi Scheduler:</b> ⏰ {pending_count} bài đăng đang chờ\n"
                            f"● <b>Tổng lượt Click hôm nay:</b> 📈 {total_clicks} clicks"
                        )
                        send_telegram_message(token, chat_id, status_text, reply_markup=reply_keyboard_markup)

                    elif cmd.startswith('/auto_groups'):
                        niche = text.replace('/auto_groups', '').strip()
                        if not niche:
                            send_telegram_message(token, chat_id, "⚠️ Vui lòng nhập ngách sản phẩm. Ví dụ: <code>/auto_groups Sữa non cho bé</code>")
                            continue
                            
                        accounts = [a for a in database.get_accounts() if a['status'] == 'active']
                        if not accounts:
                            send_telegram_message(token, chat_id, "⚠️ Hệ thống chưa có tài khoản Facebook nào đang hoạt động để quét nhóm.")
                            continue
                            
                        send_telegram_message(token, chat_id, "⏳ Đang tải danh sách nhóm bạn đã tham gia (Mất khoảng 15-30 giây)...")
                        
                        def fetch_and_save():
                            import automation
                            import random
                            acc = random.choice(accounts)
                            res = automation.auto_fetch_joined_groups(acc['cookie'], limit=10)
                            if res.get('success') and res.get('data'):
                                groups = res['data']
                                added = 0
                                for g in groups:
                                    if database.save_insight_target(None, g['target_url'], g['target_name'], niche):
                                        added += 1
                                send_telegram_message(token, chat_id, f"✅ Đã tải và tự động thêm <b>{added} nhóm</b> vào danh sách Quét Leads với ngách <b>{niche}</b>.\nHệ thống AI sẽ tự động phân tích và gửi báo cáo mỗi 15 phút!")
                            else:
                                send_telegram_message(token, chat_id, f"❌ Lỗi: {res.get('log', 'Không tìm thấy nhóm.')}")
                        
                        threading.Thread(target=fetch_and_save, daemon=True).start()
                        
                    elif cmd in ['/accounts', '👤 Tài Khoản']:
                        accounts = database.get_accounts()
                        if not accounts:
                            send_telegram_message(token, chat_id, "⚠️ Hệ thống HAME chưa được cấu hình tài khoản nào.")
                            continue
                            
                        acc_lines = []
                        for i, acc in enumerate(accounts):
                            status_emoji = "🟢" if acc['status'] == 'active' else "🔴"
                            acc_lines.append(f"{i+1}. {status_emoji} <b>{acc['name']}</b> ({acc['platform']}) - Trạng thái: {acc['status']}")
                        
                        acc_text = "👤 <b>Danh sách tài khoản HAME:</b>\n\n" + "\n".join(acc_lines)
                        send_telegram_message(token, chat_id, acc_text, reply_markup=reply_keyboard_markup)
                        
                    elif cmd in ['/stats', '📈 Thống Kê Chung']:
                        conn = database.get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT status, count(*) FROM posts GROUP BY status")
                        stats_rows = cursor.fetchall()
                        cursor.execute("SELECT COUNT(*), SUM(clicks) FROM redirects")
                        redir_stats = cursor.fetchone()
                        conn.close()
                        
                        stats_map = dict(stats_rows)
                        success = stats_map.get('success', 0)
                        posted = stats_map.get('posted', 0)
                        failed = stats_map.get('failed', 0)
                        pending = stats_map.get('pending', 0)
                        
                        total_redirs = redir_stats[0] if redir_stats else 0
                        total_clicks = redir_stats[1] if redir_stats and redir_stats[1] is not None else 0
                        
                        stats_text = (
                            f"📈 <b>Báo cáo thống kê HAME:</b>\n\n"
                            f"● <b>Đã đăng thành công:</b> {success + posted} bài\n"
                            f"● <b>Bài đăng thất bại:</b> {failed} bài\n"
                            f"● <b>Đang chờ lên lịch:</b> {pending} bài\n"
                            f"● <b>Tổng số Link click-through:</b> {total_redirs} link\n"
                            f"● <b>Tổng lượt click người dùng thực:</b> 🔗 {total_clicks} click"
                        )
                        send_telegram_message(token, chat_id, stats_text, reply_markup=reply_keyboard_markup)

                    elif cmd in ['/bio', '/set_bio']:
                        parts = text.split(maxsplit=1)
                        if len(parts) < 2:
                            send_telegram_message(token, chat_id, "⚠️ Vui lòng nhập link Bio. Ví dụ: <code>/bio https://mycollection.shopee.vn/username</code>")
                            continue
                        bio_url = parts[1].strip()
                        database.save_setting('bait_bio_link', bio_url)
                        send_telegram_message(token, chat_id, f"✅ <b>Đã lưu Link Bio thành công!</b>\nLink của sếp: {bio_url}\n\nTừ giờ, khi có khách xin link ở bài viết mồi, Bot sẽ tự động trả lời kèm link này!")
                    elif cmd in ['/openall', '/openbrowser', '🚀 Mở 15 Trình Duyệt']:
                        import multibrowser_engine
                        res = multibrowser_engine.launch_all_browsers()
                        send_telegram_message(token, chat_id, f"🚀 <b>ĐÃ KÍCH HOẠT ĐỒNG LOẠT TRÌNH DUYỆT!</b>\n💻 {res.get('message')}\n🌐 15 cửa sổ Chrome đã tự động nạp Cookie Facebook độc lập và xếp lưới trên màn hình máy tính của sếp.")

                    else:
                        send_telegram_message(token, chat_id, "❓ Lệnh không hợp lệ. Gửi <code>/help</code> để xem hướng dẫn.")
                
                # Check Shopee product link
                elif 'shopee.vn' in text.lower() or 'shp.ee' in text.lower():
                    # Extract URL
                    url_match = re.search(r'(https?://[^\s]+)', text)
                    if url_match:
                        shopee_url = url_match.group(1)
                        import_id = 'imp_' + str(uuid.uuid4())[:8]
                        database.save_setting(f'temp_url_{import_id}', shopee_url)
                        
                        choose_msg = (
                            f"📥 <b>HAME:</b> Đã nhận liên kết Shopee.\n"
                            f"Bạn muốn đăng bài tiếp thị này lên nền tảng nào?"
                        )
                        reply_markup = {
                            "inline_keyboard": [
                                [
                                    {"text": "📱 Facebook", "callback_data": f"plat_facebook_{import_id}"},
                                    {"text": "🧵 Threads", "callback_data": f"plat_threads_{import_id}"}
                                ],
                                [
                                    {"text": "🚀 Đăng cả hai nền tảng", "callback_data": f"plat_both_{import_id}"}
                                ]
                            ]
                        }
                        send_telegram_message(token, chat_id, choose_msg, reply_markup=reply_markup)
                    else:
                        send_telegram_message(token, chat_id, "❌ Không tìm thấy đường dẫn liên kết hợp lệ trong nội dung tin nhắn.")
                else:
                    send_telegram_message(token, chat_id, "💡 <b>HAME:</b> Gửi một liên kết sản phẩm Shopee (e.g., https://shope.ee/...) để cào và tự động tạo bài viết.")
                    
            time.sleep(2)
        except Exception as bot_loop_err:
            print(f"[TeleBot] Bot loop error: {bot_loop_err}")
            time.sleep(10)

_bot_started = False
def start_telegram_bot():
    """Trigger the bot loop inside a daemon thread"""
    global _bot_started
    if _bot_started: return None
    _bot_started = True
    t = threading.Thread(target=run_telegram_polling, daemon=True)
    t.start()
    return t

def notify_insight_lead(lead_data, niche_keywords):
    import database
    settings = database.get_settings()
    if str(settings.get('telegram_enabled', '0')) != '1':
        return
    token = settings.get('telegram_token')
    chat_id = settings.get('telegram_chat_id')
    if not token or not chat_id:
        return
    
    import html
    def escape(text):
        return html.escape(str(text)) if text else ""
        
    msg = f"🚨 <b>LEAD MỚI PHÁT HIỆN!</b>\n\n"
    msg += f"🔍 <b>Ngách:</b> {escape(niche_keywords)}\n"
    msg += f"👤 <b>Tác giả:</b> {escape(lead_data.get('author', 'Không rõ'))}\n"
    msg += f"🔗 <b>Link bài:</b> <a href='{lead_data.get('post_url', '')}'>Bấm vào đây để xem/chat</a>\n\n"
    
    content = lead_data.get('content', '')
    if content:
        msg += f"📝 <b>Nội dung gốc:</b>\n<i>{escape(content[:300])}{'...' if len(content) > 300 else ''}</i>\n\n"
    msg += f"💔 <b>Vấn đề (Pain Point):</b>\n{escape(lead_data.get('pain_point', ''))}\n\n"
    msg += f"✨ <b>Mong muốn (Desire):</b>\n{escape(lead_data.get('desire', ''))}\n\n"
    msg += f"🧠 <b>Insight:</b>\n{escape(lead_data.get('insight', ''))}\n\n"
    
    ideas = lead_data.get('content_ideas', [])
    if ideas:
        msg += f"💡 <b>Gợi ý Content tiếp cận:</b>\n"
        for i, idea in enumerate(ideas, 1):
            msg += f"{i}. {escape(idea)}\n"
            
    products = lead_data.get('suggested_products', [])
    if products:
        msg += f"\n🛍️ <b>Sản phẩm Gợi ý (Nhu cầu khách):</b>\n"
        for i, prod in enumerate(products, 1):
            msg += f"• {escape(prod)}\n"
            
    structure = lead_data.get('post_structure')
    if structure:
        msg += f"\n📝 <b>Cấu trúc Content chốt sale:</b>\n{escape(structure)}\n"
        
    image_idea = lead_data.get('image_idea')
    if image_idea:
        msg += f"\n📸 <b>Ý tưởng Hình ảnh:</b>\n{image_idea}\n"

    suggested_post = lead_data.get('suggested_post')
    if suggested_post:
        msg += f"\n✍️ <b>BÀI VIẾT COPY & PASTE (Shopee Affiliate):</b>\n<blockquote>{escape(suggested_post)}</blockquote>\n"

    send_telegram_message(token, chat_id, msg)

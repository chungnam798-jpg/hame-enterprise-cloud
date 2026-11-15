import sqlite3
import json
import os
import uuid
from datetime import datetime

DB_FILE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            cookie TEXT NOT NULL,
            platform TEXT DEFAULT 'facebook',
            status TEXT DEFAULT 'active',
            team_role TEXT DEFAULT 'team_poster',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    try:
        cursor.execute("ALTER TABLE accounts ADD COLUMN team_role TEXT DEFAULT 'team_poster'")
    except Exception:
        pass
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            type TEXT NOT NULL,
            target_id TEXT NOT NULL,
            content TEXT NOT NULL,
            media TEXT DEFAULT '[]',
            platform TEXT DEFAULT 'facebook',
            scheduled_at TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            result_log TEXT,
            screenshot TEXT,
            bulk_group_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS target_lists (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            targets TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS redirects (
            id TEXT PRIMARY KEY,
            destination_url TEXT NOT NULL,
            image_file TEXT NOT NULL,
            title TEXT,
            description TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS engagement_rules (
            id TEXT PRIMARY KEY,
            keywords TEXT NOT NULL,
            reply_text TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS engagement_logs (
            id TEXT PRIMARY KEY,
            post_url TEXT NOT NULL,
            commenter_name TEXT NOT NULL,
            comment_content TEXT NOT NULL,
            reply_content TEXT NOT NULL,
            status TEXT NOT NULL,
            screenshot TEXT,
            created_at TEXT NOT NULL
        )
    ''')

    # Post templates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            tags TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    # Bulk post groups - group multiple posts into one campaign
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bulk_groups (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            total_posts INTEGER DEFAULT 0,
            success_count INTEGER DEFAULT 0,
            fail_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    # Auto-like targets (groups/pages to auto-like posts in)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS autolike_targets (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            target_url TEXT NOT NULL,
            target_name TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            last_run TEXT,
            auto_comment INTEGER DEFAULT 0,
            comment_style TEXT DEFAULT 'AI',
            comment_text TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE CASCADE
        )
    ''')

    # Group stats (for tracking pending approval rates)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_stats (
            group_id TEXT PRIMARY KEY,
            group_name TEXT,
            pending_count INTEGER DEFAULT 0,
            is_moderated INTEGER DEFAULT 0,
            last_posted TEXT
        )
    ''')

    # DM Leads CRM table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dm_leads (
            id TEXT PRIMARY KEY,
            customer_url TEXT NOT NULL UNIQUE,
            group_url TEXT DEFAULT '',
            account_id TEXT DEFAULT '',
            variant TEXT DEFAULT 'A',
            status TEXT DEFAULT 'SUCCESS',
            first_sent_at TEXT NOT NULL,
            last_follow_up_at TEXT DEFAULT '',
            notes TEXT DEFAULT ''
        )
    ''')

    try:
        cursor.execute("ALTER TABLE accounts ADD COLUMN proxy TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE accounts ADD COLUMN nurture_likes INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE accounts ADD COLUMN nurture_reels INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE accounts ADD COLUMN nurture_comments INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE accounts ADD COLUMN trust_score INTEGER DEFAULT 95")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE accounts ADD COLUMN last_nurtured_at TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE autolike_targets ADD COLUMN auto_comment INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE autolike_targets ADD COLUMN comment_style TEXT DEFAULT 'AI'")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE autolike_targets ADD COLUMN comment_text TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE autolike_targets ADD COLUMN is_moderated INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE autolike_targets ADD COLUMN pending_count INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    # Auto-like logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS autolike_logs (
            id TEXT PRIMARY KEY,
            target_id TEXT NOT NULL,
            post_url TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')

    # Auto-join logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS autojoin_logs (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            target_name_or_url TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )
    ''')
    
    # Insight targets (Lead generation)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS insight_targets (
            id TEXT PRIMARY KEY,
            target_url TEXT NOT NULL,
            target_name TEXT NOT NULL,
            niche_keywords TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            last_run TEXT,
            created_at TEXT NOT NULL
        )
    ''')

    # Insight leads (Stored analyzed leads)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS insight_leads (
            id TEXT PRIMARY KEY,
            target_id TEXT,
            post_url TEXT,
            author_name TEXT,
            content TEXT,
            analysis TEXT,
            created_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scanned_posts (
            post_url TEXT PRIMARY KEY
        )
    ''')
    
    # Default settings
    defaults = {
        'delay_between_posts': '60',
        'engage_interval_minutes': '15',
        'autolike_interval_minutes': '30',
        'max_replies_per_scan': '5',
        'max_likes_per_scan': '10',
        'autofeed_engage_enabled': '0',
        'autofeed_engage_interval_minutes': '30',
        'autofeed_engage_source': 'groups',
        'autofeed_engage_style': 'spintax',
        'autofeed_engage_text': '{Hay quá|Tuyệt vời|Đỉnh quá}! Chúc bạn {ngày mới tốt lành|buôn may bán đắt}!',
        'autofeed_max_posts_per_scan': '5',
        'browser_headless': '0',
        'engage_speed_mode': 'turbo',
        'shopee_auto_comment_link': '1',
        'shopee_comment_template': 'Link mua sản phẩm tại đây nhé cả nhà: {link}',
        'shopee_affiliate_id': '',
        'shopee_sub_id': 'fbposter',
        'telegram_enabled': '0',
        'telegram_token': '',
        'telegram_chat_id': '',
        'telegram_notify_success': '1',
        'telegram_notify_fail': '1',
        'inbox_chatbot_enabled': '0',
        'inbox_keywords': 'ib,gia,inbox,tu van,link,shop,mua,size,ship',
        'inbox_comment_reply_template': 'Chào {name}, mình đã gửi tin nhắn riêng thông tin chi tiết và ưu đãi cho bạn rồi nhé. Bạn check hộp thư Messenger giúp mình nha! {link}',
        'inbox_message_template': 'Chào {name}! Cảm ơn bạn đã quan tâm sản phẩm bên mình. Đây là thông tin chi tiết và đường dẫn ưu đãi dành cho bạn: {link}',
        'tunnel_subdomain': 'chungs-shopee-' + str(uuid.uuid4())[:8],
    }
    for k, v in defaults.items():
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

        
    # Migrations for version 1.4: platform support & legacy migrations
    try:
        cursor.execute("ALTER TABLE accounts ADD COLUMN platform TEXT DEFAULT 'facebook'")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE accounts ADD COLUMN username TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE accounts ADD COLUMN password TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE accounts ADD COLUMN two_factor_key TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE posts ADD COLUMN is_deleted INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE posts ADD COLUMN platform TEXT DEFAULT 'facebook'")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE posts ADD COLUMN bulk_group_id TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE posts ADD COLUMN first_comment TEXT DEFAULT NULL")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE posts ADD COLUMN post_url TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE redirects ADD COLUMN clicks INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seed_logs (
            id TEXT PRIMARY KEY,
            post_id TEXT,
            post_url TEXT,
            vip_account_id TEXT,
            lite_account_id TEXT,
            vip_comment TEXT,
            lite_reply TEXT,
            status TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# ACCOUNTS
# ─────────────────────────────────────────
def get_accounts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM accounts ORDER BY created_at DESC')
    rows = cursor.fetchall()
    accounts = [dict(row) for row in rows]
    conn.close()
    return accounts

def get_account(account_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM accounts WHERE id = ?', (account_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_account(account_id, name, cookie, status='active', platform='facebook', username=None, password=None, two_factor_key=None, proxy=None, team_role='team_poster'):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('SELECT id FROM accounts WHERE id = ?', (account_id,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute('UPDATE accounts SET name=?, cookie=?, status=?, platform=?, username=?, password=?, two_factor_key=?, proxy=?, team_role=?, updated_at=? WHERE id=?',
                       (name, cookie, status, platform, username, password, two_factor_key, proxy, team_role, now, account_id))
    else:
        cursor.execute('INSERT INTO accounts (id, name, cookie, status, platform, username, password, two_factor_key, proxy, team_role, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                       (account_id, name, cookie, status, platform, username, password, two_factor_key, proxy, team_role, now, now))
    conn.commit()
    conn.close()
    return get_account(account_id)
def update_account_nurture_stats(account_id, likes=0, reels=0, comments=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        UPDATE accounts 
        SET nurture_likes = COALESCE(nurture_likes, 0) + ?,
            nurture_reels = COALESCE(nurture_reels, 0) + ?,
            nurture_comments = COALESCE(nurture_comments, 0) + ?,
            last_nurtured_at = ?
        WHERE id = ?
    ''', (likes, reels, comments, now, account_id))
    conn.commit()
    conn.close()

def delete_account(account_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM accounts WHERE id=?', (account_id,))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# POSTS
# ─────────────────────────────────────────
def get_posts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, a.name as account_name 
        FROM posts p 
        LEFT JOIN accounts a ON p.account_id = a.id 
        WHERE p.is_deleted = 0
        ORDER BY p.scheduled_at DESC
    ''')
    rows = cursor.fetchall()
    posts = []
    for row in rows:
        d = dict(row)
        try: d['media'] = json.loads(d['media'])
        except: d['media'] = []
        posts.append(d)
    conn.close()
    return posts

def get_post(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts WHERE id=?', (post_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        d = dict(row)
        try: d['media'] = json.loads(d['media'])
        except: d['media'] = []
        return d
    return None

def get_posts_by_status(status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts WHERE status=? AND is_deleted=0 ORDER BY scheduled_at ASC', (status,))
    rows = cursor.fetchall()
    posts = []
    for row in rows:
        d = dict(row)
        try: d['media'] = json.loads(d['media'])
        except: d['media'] = []
        posts.append(d)
    conn.close()
    return posts

def save_post(post_id, account_id, type_, target_id, content, media, scheduled_at,
              status='pending', result_log=None, screenshot=None, bulk_group_id=None, platform='facebook', first_comment=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    media_json = json.dumps(media)
    cursor.execute('SELECT id FROM posts WHERE id=?', (post_id,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute('''
            UPDATE posts SET account_id=?, type=?, target_id=?, content=?, media=?, platform=?,
            scheduled_at=?, status=?, result_log=?, screenshot=?, bulk_group_id=?, first_comment=?, updated_at=?
            WHERE id=?
        ''', (account_id, type_, target_id, content, media_json, platform, scheduled_at,
              status, result_log, screenshot, bulk_group_id, first_comment, now, post_id))
    else:
        cursor.execute('''
            INSERT INTO posts (id, account_id, type, target_id, content, media, platform, scheduled_at,
            status, result_log, screenshot, bulk_group_id, first_comment, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (post_id, account_id, type_, target_id, content, media_json, platform, scheduled_at,
              status, result_log, screenshot, bulk_group_id, first_comment, now, now))
    conn.commit()
    conn.close()
    return get_post(post_id)

def update_post_status(post_id, status, result_log=None, screenshot=None, post_url=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    if post_url:
        cursor.execute('UPDATE posts SET status=?, result_log=?, screenshot=?, post_url=?, updated_at=? WHERE id=?',
                       (status, result_log, screenshot, post_url, now, post_id))
    else:
        cursor.execute('UPDATE posts SET status=?, result_log=?, screenshot=?, updated_at=? WHERE id=?',
                       (status, result_log, screenshot, now, post_id))
    conn.commit()
    conn.close()

def update_post_status_and_time(post_id, status, scheduled_at, result_log=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('UPDATE posts SET status=?, scheduled_at=?, result_log=?, updated_at=? WHERE id=?',
                   (status, scheduled_at, result_log, now, post_id))
    conn.commit()
    conn.close()

    # Telegram notification hook
    if status in ['success', 'posted', 'failed', 'pending_approval']:
        try:
            post = get_post(post_id)
            if post:
                account = get_account(post['account_id'])
                acc_name = account['name'] if account else "Unknown"
                
                status_txt = {
                    'success': '🟢 Đăng thành công',
                    'posted': '🟢 Đăng thành công',
                    'failed': '🔴 Thất bại',
                    'pending_approval': '🟠 Chờ duyệt (Admin approval)'
                }.get(status, status)
                
                settings = get_settings()
                notify_success = settings.get('telegram_notify_success', '1') == '1'
                notify_fail = settings.get('telegram_notify_fail', '1') == '1'
                
                should_notify = False
                if status in ['success', 'posted', 'pending_approval'] and notify_success:
                    should_notify = True
                elif status == 'failed' and notify_fail:
                    should_notify = True
                    
                if should_notify:
                    msg = (
                        f"📢 <b>Báo cáo đăng bài HAME:</b> {status_txt}\n\n"
                        f"👤 <b>Tài khoản:</b> {acc_name}\n"
                        f"🎯 <b>Nơi đăng:</b> {post['type']} ({post['target_id']})\n"
                        f"📝 <b>Nội dung:</b>\n<i>{post['content'][:150]}...</i>"
                    )
                    if result_log:
                        clean_log = result_log[:200]
                        msg += f"\n\n⚙️ <b>Chi tiết:</b> {clean_log}"
                        
                    from telegram_bot import notify_user
                    photo_path = None
                    if screenshot:
                        photo_path = os.path.join('static', screenshot)
                        
                    notify_user(msg, photo_path)
        except Exception as notify_err:
            print(f"[TeleBot] Notification hook error: {notify_err}")

def delete_post(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE posts SET is_deleted=1, updated_at=? WHERE id=?', (datetime.now().isoformat(), post_id))
    conn.commit()
    conn.close()

def reset_failed_posts_due_to_cookie(account_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE posts 
        SET status='pending', result_log = COALESCE(result_log, '') || '\n[System] Đã reset trạng thái về pending do tài khoản được cập nhật Cookie mới.'
        WHERE account_id=? AND status='failed' AND is_deleted=0 AND (
            LOWER(COALESCE(result_log, '')) LIKE '%cookie%' OR 
            LOWER(COALESCE(result_log, '')) LIKE '%checkpoint%' OR 
            LOWER(COALESCE(result_log, '')) LIKE '%login%' OR 
            LOWER(COALESCE(result_log, '')) LIKE '%expired%' OR 
            LOWER(COALESCE(result_log, '')) LIKE '%session%' OR
            LOWER(COALESCE(result_log, '')) LIKE '%đăng nhập%'
        )
    ''', (account_id,))
    updated_count = cursor.rowcount
    conn.commit()
    conn.close()
    return updated_count

def restore_post(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE posts SET is_deleted=0, updated_at=? WHERE id=?', (datetime.now().isoformat(), post_id))
    conn.commit()
    conn.close()

def delete_post_permanently(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE id=?', (post_id,))
    conn.commit()
    conn.close()

def get_deleted_posts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, a.name as account_name 
        FROM posts p 
        LEFT JOIN accounts a ON p.account_id = a.id 
        WHERE p.is_deleted = 1
        ORDER BY p.updated_at DESC
    ''')
    rows = cursor.fetchall()
    posts = []
    for row in rows:
        d = dict(row)
        try: d['media'] = json.loads(d['media'])
        except: d['media'] = []
        posts.append(d)
    conn.close()
    return posts

def get_analytics():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total counts
    cursor.execute("SELECT COUNT(*) as total, status FROM posts WHERE is_deleted=0 GROUP BY status")
    post_stats = {row['status']: row['total'] for row in cursor.fetchall()}
    
    # Posts per day (last 7 days)
    cursor.execute("""
        SELECT substr(created_at, 1, 10) as day, COUNT(*) as count, status
        FROM posts 
        WHERE is_deleted=0 AND created_at >= date('now', '-7 days')
        GROUP BY day, status
        ORDER BY day
    """)
    daily = cursor.fetchall()
    
    # Engagement stats
    cursor.execute("SELECT COUNT(*) as total FROM engagement_logs WHERE status='success'")
    engage_success = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM engagement_logs")
    engage_total = cursor.fetchone()['total']

    # Auto-like stats
    cursor.execute("SELECT COUNT(*) as total FROM autolike_logs WHERE status='success'")
    like_success = cursor.fetchone()['total']
    
    conn.close()
    return {
        'post_stats': post_stats,
        'daily': [dict(r) for r in daily],
        'engage_total': engage_total,
        'engage_success': engage_success,
        'like_success': like_success,
    }

# ─────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────
def get_settings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM settings')
    rows = cursor.fetchall()
    settings = {row['key']: row['value'] for row in rows}
    conn.close()
    return settings

def save_setting(key, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO settings (key, value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',
                   (key, str(value)))
    conn.commit()
    conn.close()

def delete_setting(key):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM settings WHERE key=?', (key,))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# ENGAGEMENT RULES
# ─────────────────────────────────────────
def get_engagement_rules():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM engagement_rules ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_engagement_rule(rule_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM engagement_rules WHERE id=?', (rule_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_engagement_rule(rule_id, keywords, reply_text, status='active'):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('SELECT id FROM engagement_rules WHERE id=?', (rule_id,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute('UPDATE engagement_rules SET keywords=?, reply_text=?, status=?, updated_at=? WHERE id=?',
                       (keywords, reply_text, status, now, rule_id))
    else:
        cursor.execute('INSERT INTO engagement_rules (id, keywords, reply_text, status, created_at, updated_at) VALUES (?,?,?,?,?,?)',
                       (rule_id, keywords, reply_text, status, now, now))
    conn.commit()
    conn.close()
    return get_engagement_rule(rule_id)

def delete_engagement_rule(rule_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM engagement_rules WHERE id=?', (rule_id,))
    conn.commit()
    conn.close()

def get_engagement_logs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM engagement_logs ORDER BY created_at DESC LIMIT 100')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_engagement_log(log_id, post_url, commenter_name, comment_content, reply_content, status, screenshot=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO engagement_logs (id, post_url, commenter_name, comment_content, reply_content, status, screenshot, created_at)
        VALUES (?,?,?,?,?,?,?,?)
    ''', (log_id, post_url, commenter_name, comment_content, reply_content, status, screenshot, now))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# TEMPLATES
# ─────────────────────────────────────────
def get_templates():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM templates ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_template(template_id, name, content, tags=''):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('SELECT id FROM templates WHERE id=?', (template_id,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute('UPDATE templates SET name=?, content=?, tags=?, updated_at=? WHERE id=?',
                       (name, content, tags, now, template_id))
    else:
        cursor.execute('INSERT INTO templates (id, name, content, tags, created_at, updated_at) VALUES (?,?,?,?,?,?)',
                       (template_id, name, content, tags, now, now))
    conn.commit()
    conn.close()

def delete_template(template_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM templates WHERE id=?', (template_id,))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# BULK GROUPS
# ─────────────────────────────────────────
def get_bulk_groups():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bulk_groups ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_bulk_group(group_id, name, total_posts=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('SELECT id FROM bulk_groups WHERE id=?', (group_id,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute('UPDATE bulk_groups SET name=?, total_posts=?, updated_at=? WHERE id=?',
                       (name, total_posts, now, group_id))
    else:
        cursor.execute('INSERT INTO bulk_groups (id, name, total_posts, created_at, updated_at) VALUES (?,?,?,?,?)',
                       (group_id, name, total_posts, now, now))
    conn.commit()
    conn.close()

def update_bulk_group_stats(group_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("SELECT COUNT(*) as c FROM posts WHERE bulk_group_id=? AND status='posted'", (group_id,))
    success = cursor.fetchone()['c']
    cursor.execute("SELECT COUNT(*) as c FROM posts WHERE bulk_group_id=? AND status='failed'", (group_id,))
    fail = cursor.fetchone()['c']
    cursor.execute("SELECT COUNT(*) as c FROM posts WHERE bulk_group_id=?", (group_id,))
    total = cursor.fetchone()['c']
    
    status = 'running'
    if success + fail == total and total > 0:
        status = 'completed'
    
    cursor.execute('UPDATE bulk_groups SET success_count=?, fail_count=?, status=?, updated_at=? WHERE id=?',
                   (success, fail, status, now, group_id))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# AUTO-LIKE TARGETS
# ─────────────────────────────────────────
def get_autolike_targets():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.*, a.name as account_name
        FROM autolike_targets t
        LEFT JOIN accounts a ON t.account_id = a.id
        ORDER BY t.created_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_autolike_target(target_id, account_id, target_url, target_name, status='active', auto_comment=0, comment_style='AI', comment_text=''):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('SELECT id FROM autolike_targets WHERE id=?', (target_id,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute('''
            UPDATE autolike_targets 
            SET account_id=?, target_url=?, target_name=?, status=?, last_run=?, auto_comment=?, comment_style=?, comment_text=?
            WHERE id=?
        ''', (account_id, target_url, target_name, status, now, auto_comment, comment_style, comment_text, target_id))
    else:
        cursor.execute('''
            INSERT INTO autolike_targets (id, account_id, target_url, target_name, status, auto_comment, comment_style, comment_text, created_at)
            VALUES (?,?,?,?,?,?,?,?,?)
        ''', (target_id, account_id, target_url, target_name, status, auto_comment, comment_style, comment_text, now))
    conn.commit()
    conn.close()

def delete_autolike_target(target_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM autolike_targets WHERE id=?', (target_id,))
    conn.commit()
    conn.close()

def update_autolike_target_last_run(target_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('UPDATE autolike_targets SET last_run=? WHERE id=?', (now, target_id))
    conn.commit()
    conn.close()

def get_autolike_logs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM autolike_logs ORDER BY created_at DESC LIMIT 100')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_autolike_log(log_id, target_id, post_url, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('INSERT INTO autolike_logs (id, target_id, post_url, status, created_at) VALUES (?,?,?,?,?)',
                   (log_id, target_id, post_url, status, now))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# TARGET LISTS
# ─────────────────────────────────────────
def get_target_lists():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM target_lists ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_target_list(list_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM target_lists WHERE id=?', (list_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_target_list(list_id, name, targets):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('SELECT id FROM target_lists WHERE id=?', (list_id,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute('''
            UPDATE target_lists SET name=?, targets=?, updated_at=? WHERE id=?
        ''', (name, targets, now, list_id))
    else:
        cursor.execute('''
            INSERT INTO target_lists (id, name, targets, created_at, updated_at)
            VALUES (?,?,?,?,?)
        ''', (list_id, name, targets, now, now))
    conn.commit()
    conn.close()
    return get_target_list(list_id)

def delete_target_list(list_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM target_lists WHERE id=?', (list_id,))
    conn.commit()
    conn.close()

def save_redirect(redirect_id, destination_url, image_file, title, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('SELECT id FROM redirects WHERE id=?', (redirect_id,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute('''
            UPDATE redirects SET destination_url=?, image_file=?, title=?, description=? WHERE id=?
        ''', (destination_url, image_file, title, description, redirect_id))
    else:
        cursor.execute('''
            INSERT INTO redirects (id, destination_url, image_file, title, description, created_at)
            VALUES (?,?,?,?,?,?)
        ''', (redirect_id, destination_url, image_file, title, description, now))
    conn.commit()
    conn.close()
    return get_redirect(redirect_id)

def get_redirect(redirect_id):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM redirects WHERE id=?', (redirect_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_redirect(redirect_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM redirects WHERE id=?', (redirect_id,))
    conn.commit()
    conn.close()

def increment_redirect_clicks(redirect_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE redirects SET clicks = clicks + 1 WHERE id = ?', (redirect_id,))
    conn.commit()
    conn.close()

def delete_bulk_group(group_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    # Move all posts in this bulk campaign to trash
    cursor.execute('UPDATE posts SET is_deleted=1, updated_at=? WHERE bulk_group_id=?', (now, group_id))
    # Delete the bulk group metadata
    cursor.execute('DELETE FROM bulk_groups WHERE id=?', (group_id,))
    conn.commit()
    conn.close()

# GROUP STATS (Moderation tracking)

def increment_group_pending_count(group_id, group_name=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    cursor.execute("SELECT pending_count FROM group_stats WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    
    if row:
        new_count = row['pending_count'] + 1
        is_mod = 1 if new_count >= 3 else 0
        cursor.execute("""
            UPDATE group_stats 
            SET pending_count=?, is_moderated=?, last_posted=?, group_name=COALESCE(NULLIF(?,''), group_name)
            WHERE group_id=?
        """, (new_count, is_mod, now, group_name, group_id))
    else:
        cursor.execute("""
            INSERT INTO group_stats (group_id, group_name, pending_count, is_moderated, last_posted)
            VALUES (?, ?, 1, 0, ?)
        """, (group_id, group_name, now))
        
    conn.commit()
    conn.close()

def get_moderated_groups():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM group_stats WHERE is_moderated=1 ORDER BY pending_count DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_group_stats(group_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM group_stats WHERE group_id=?", (group_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# ─────────────────────────────────────────
# AUTO-JOIN GROUPS LOGS
# ─────────────────────────────────────────
def get_autojoin_logs():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT l.*, a.name as account_name 
        FROM autojoin_logs l
        LEFT JOIN accounts a ON l.account_id = a.id
        ORDER BY l.created_at DESC LIMIT 100
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_autojoin_log(account_id, target_name_or_url, status, details=''):
    conn = get_db_connection()
    cursor = conn.cursor()
    log_id = 'aj_' + str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    cursor.execute('INSERT INTO autojoin_logs (id, account_id, target_name_or_url, status, details, created_at) VALUES (?,?,?,?,?,?)',
                   (log_id, account_id, target_name_or_url, status, details, now))
    conn.commit()
    conn.close()

def clear_autojoin_logs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM autojoin_logs')
    conn.commit()
    conn.close()



# ─────────────────────────────────────────
# INSIGHT TARGETS & LEADS
# ─────────────────────────────────────────
def get_insight_targets():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM insight_targets ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_insight_target(target_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM insight_targets WHERE id = ?', (target_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def is_lead_exists(post_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM insight_leads WHERE post_url = ?", (post_url,))
    res = cursor.fetchone()
    conn.close()
    return bool(res)

def save_insight_lead(lead_id, target_id, post_url, author_name, content, analysis):
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO insight_leads (id, target_id, post_url, author_name, content, analysis, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (lead_id, target_id, post_url, author_name, content, analysis, created_at))
    conn.commit()
    conn.close()

def is_scanned_post(post_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM scanned_posts WHERE post_url = ?", (post_url,))
    res = cursor.fetchone()
    conn.close()
    return bool(res)

def save_scanned_post(post_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO scanned_posts (post_url) VALUES (?)", (post_url,))
        conn.commit()
    except:
        pass
    finally:
        conn.close()

def save_insight_target(target_id, target_url, target_name, niche_keywords, status='active'):
    if not target_id:
        import uuid
        target_id = f"ins_{uuid.uuid4().hex[:8]}"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('SELECT id FROM insight_targets WHERE id = ?', (target_id,))
    if cursor.fetchone():
        cursor.execute('''
            UPDATE insight_targets SET target_url=?, target_name=?, niche_keywords=?, status=? 
            WHERE id=?
        ''', (target_url, target_name, niche_keywords, status, target_id))
    else:
        cursor.execute('''
            INSERT INTO insight_targets (id, target_url, target_name, niche_keywords, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (target_id, target_url, target_name, niche_keywords, status, now))
    conn.commit()
    conn.close()
    return get_insight_target(target_id)

def delete_insight_target(target_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM insight_targets WHERE id=?', (target_id,))
    conn.commit()
    conn.close()

def update_insight_target_last_run(target_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('UPDATE insight_targets SET last_run=? WHERE id=?', (now, target_id))
    conn.commit()
    conn.close()

def get_insight_leads(limit=100):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM insight_leads ORDER BY created_at DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def is_lead_exists(post_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM insight_leads WHERE post_url = ?', (post_url,))
    row = cursor.fetchone()
    conn.close()
    return bool(row)

def save_insight_lead(lead_id, target_id, post_url, author_name, content, analysis):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO insight_leads (id, target_id, post_url, author_name, content, analysis, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (lead_id, target_id, post_url, author_name, content, analysis, now))
    conn.commit()
    conn.close()

def get_unseeded_posts():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Get posts that have post_url, status 'posted' or 'success'
    # and don't exist in seed_logs
    cursor.execute('''
        SELECT p.* FROM posts p
        LEFT JOIN seed_logs s ON p.id = s.post_id
        WHERE p.post_url IS NOT NULL 
          AND p.status IN ('posted', 'success')
          AND s.id IS NULL
        ORDER BY p.created_at DESC LIMIT 10
    ''')
    posts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return posts

def get_pending_reply_seeds():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.* FROM seed_logs s
        WHERE s.status = 'pending_reply'
        ORDER BY s.updated_at ASC LIMIT 10
    ''')
    seeds = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return seeds

def create_seed_log(post_id, post_url, vip_account_id, lite_account_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    seed_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO seed_logs (id, post_id, post_url, vip_account_id, lite_account_id, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (seed_id, post_id, post_url, vip_account_id, lite_account_id, 'pending_comment', now, now))
    conn.commit()
    conn.close()
    return seed_id

def update_seed_log(seed_id, status, vip_comment=None, lite_reply=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    updates = ["status=?", "updated_at=?"]
    params = [status, now]
    if vip_comment is not None:
        updates.append("vip_comment=?")
        params.append(vip_comment)
    if lite_reply is not None:
        updates.append("lite_reply=?")
        params.append(lite_reply)
        
    params.append(seed_id)
    
    query = f"UPDATE seed_logs SET {', '.join(updates)} WHERE id=?"
    cursor.execute(query, tuple(params))
    conn.commit()
    conn.close()

# ═══════════════════════════════════════
# DM LEADS CRM FUNCTIONS
# ═══════════════════════════════════════
def save_dm_lead(customer_url, group_url='', variant='A', status='SUCCESS', account_id='', notes=''):
    conn = get_db_connection()
    cursor = conn.cursor()
    lead_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    try:
        cursor.execute('''
            INSERT INTO dm_leads (id, customer_url, group_url, account_id, variant, status, first_sent_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(customer_url) DO UPDATE SET
                status=excluded.status,
                variant=excluded.variant,
                notes=excluded.notes
        ''', (lead_id, customer_url, group_url, account_id, variant, status, now, notes))
        conn.commit()
    except Exception as e:
        print(f"Error saving DM lead: {e}")
    finally:
        conn.close()

def get_all_dm_leads(limit=100):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
def get_setting(key, default=''):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE key=?', (key,))
    row = cursor.fetchone()
    conn.close()
    return row['value'] if row else default

def save_setting(key, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value', (key, str(value)))
    conn.commit()
    conn.close()


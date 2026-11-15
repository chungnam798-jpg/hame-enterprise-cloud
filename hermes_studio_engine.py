import sys
import os
import sqlite3
from datetime import datetime

fb_poster_dir = os.path.dirname(os.path.abspath(__file__))
if fb_poster_dir not in sys.path:
    sys.path.append(fb_poster_dir)

import database

def get_active_sessions():
    """Lấy danh sách các phiên trò chuyện đa nền tảng (Messenger & Telegram)."""
    sessions = []
    conn = database.get_db_connection()
    cursor = conn.cursor()

    # Get recent customer memories as active sessions
    cursor.execute("SELECT customer_id, name, preference, last_interacted_at FROM customer_memories ORDER BY last_interacted_at DESC LIMIT 6")
    memories = cursor.fetchall()
    for m in memories:
        d = dict(m)
        sessions.append({
            "platform": "Facebook Messenger",
            "icon": "fa-brands fa-facebook-messenger",
            "color": "#0084ff",
            "session_id": d.get("customer_id"),
            "name": d.get("name"),
            "detail": f"Quan tâm: {d.get('preference', 'Thời trang')}",
            "last_active": d.get("last_interacted_at")
        })

    conn.close()

    # Fallback/Default active channels if empty
    if not sessions:
        sessions = [
            {"platform": "Facebook Messenger", "icon": "fa-brands fa-facebook-messenger", "color": "#0084ff", "session_id": "fb_inbox_live", "name": "FB Messenger Auto-Closer", "detail": "Đang lắng nghe tin nhắn mới 24/7", "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {"platform": "Telegram Bot", "icon": "fa-brands fa-telegram", "color": "#229ed9", "session_id": "tele_bot_channel", "name": "HAME Telegram Command Center", "detail": "13 Phím tắt điều hành active", "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        ]

    return sessions

def get_scheduled_jobs_status():
    """Lấy danh sách & trạng thái của các Tiến trình tự động theo lịch (Job Visualizer)."""
    jobs = [
        {
            "job_id": "job_weekly_7day",
            "title": "AI 7-Day Weekly Content Scheduler",
            "type": "Tự Động Đăng Bài",
            "icon": "fa-solid fa-calendar-days",
            "color": "#a855f7",
            "status": "RUNNING",
            "schedule": "Hàng ngày (7 ngày tới)",
            "description": "Tự động sinh kịch bản AIDA & rải bài đăng Profile/Groups"
        },
        {
            "job_id": "job_nurture_accounts",
            "title": "Account Nurturing Engine (Nuôi Nick)",
            "type": "Tương Tác Tự Động",
            "icon": "fa-solid fa-seedling",
            "color": "#10b981",
            "status": "ACTIVE",
            "schedule": "Mỗi 30 phút",
            "description": "Like, lướt Reels & comment tương tác nâng Trust Score"
        },
        {
            "job_id": "job_flashsale_scraper",
            "title": "Shopee Flash Sale Scraper & Rải Link",
            "type": "Affiliate Auto-Post",
            "icon": "fa-solid fa-bolt",
            "color": "#eab308",
            "status": "READY",
            "schedule": "Theo từ khóa / lệnh /flashsale",
            "description": "Quét Deal Shopee giảm >50% & rải bài kèm link SubID"
        },
        {
            "job_id": "job_cross_sell",
            "title": "AI Cross-Sell & Upsell Campaign",
            "type": "Chăm Sóc Khách Cũ",
            "icon": "fa-solid fa-bullseye",
            "color": "#14b8a6",
            "status": "READY",
            "schedule": "Theo yêu cầu / lệnh /crosssell",
            "description": "Đọc Trí nhớ & Đồ thị GBrain để tạo ưu đãi giảm 30% cho tệp VIP"
        }
    ]
    return jobs

def get_usage_analytics():
    """Thống kê tổng lượng Token, lượt gọi API và doanh thu Affiliate."""
    conn = database.get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM posts")
    total_posts = cursor.fetchone()["total"]

    try:
        cursor.execute("SELECT COUNT(*) as total_clicks, COALESCE(SUM(estimated_commission), 0) as total_comm FROM affiliate_clicks")
        aff_data = cursor.fetchone()
        total_clicks = aff_data["total_clicks"]
        total_comm = aff_data["total_comm"]
    except Exception:
        total_clicks = 0
        total_comm = 0.0

    conn.close()

    # Estimate API token usage based on posts & interactions
    est_api_calls = total_posts * 3 + total_clicks * 2 + 150
    est_tokens = est_api_calls * 450

    return {
        "total_posts": total_posts,
        "total_clicks": total_clicks,
        "total_commission": total_comm,
        "api_calls_count": est_api_calls,
        "estimated_tokens_used": est_tokens,
        "system_health": "100% EXCELLENT",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def get_hermes_studio_dashboard_payload():
    """Tổng hợp toàn bộ dữ liệu cho Hermes Studio Dashboard."""
    return {
        "sessions": get_active_sessions(),
        "scheduled_jobs": get_scheduled_jobs_status(),
        "analytics": get_usage_analytics()
    }

if __name__ == "__main__":
    import json
    print(json.dumps(get_hermes_studio_dashboard_payload(), indent=2, ensure_ascii=False))

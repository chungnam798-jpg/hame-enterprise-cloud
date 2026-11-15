import sys
import os
import csv
import json
import sqlite3
from datetime import datetime

fb_poster_dir = os.path.dirname(os.path.abspath(__file__))
if fb_poster_dir not in sys.path:
    sys.path.append(fb_poster_dir)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import database
from affiliate_link_converter import get_affiliate_revenue_stats, init_affiliate_db
from customer_memory import init_customer_memory_db

init_affiliate_db()
init_customer_memory_db()

def export_leads_to_google_sheets():
    """Tự động đóng gói và xuất file báo cáo tương thích Google Sheets (GWS format)."""
    conn = database.get_db_connection()
    cursor = conn.cursor()

    # Fetch Affiliate Clicks
    cursor.execute("SELECT * FROM affiliate_clicks ORDER BY last_clicked_at DESC")
    clicks = [dict(r) for r in cursor.fetchall()]

    # Fetch Customer Memories
    cursor.execute("SELECT * FROM customer_memories ORDER BY last_interacted_at DESC")
    memories = [dict(r) for r in cursor.fetchall()]

    conn.close()

    output_dir = os.path.join(fb_poster_dir, "gws_exports")
    os.makedirs(output_dir, exist_ok=True)

    sheet_file = os.path.join(output_dir, "gws_master_report.csv")
    with open(sheet_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["BÁO CÁO TỔNG QUAN GOOGLE WORKSPACE (GWS SYNC)", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow([])
        writer.writerow(["--- DANH SÁCH LƯỢT CLICK AFFILIATE ---"])
        writer.writerow(["ID", "Link Gốc", "SubID", "Số Lượt Click", "Hoa Hồng Dự Kiến (VNĐ)", "Tương Tác Lần Cuối"])
        for c in clicks:
            writer.writerow([c.get("id"), c.get("original_url"), c.get("subid"), c.get("clicks_count"), c.get("est_commission"), c.get("last_clicked_at")])

        writer.writerow([])
        writer.writerow(["--- DỮ LIỆU KHÁCH HÀNG & TRÍ NHỚ HERMES ---"])
        writer.writerow(["Customer ID", "Họ Tên", "Sở Thích Quan Tâm", "Khung Ngân Sách", "Ghi Chú", "Tương Tác Gần Nhất"])
        for m in memories:
            writer.writerow([m.get("customer_id"), m.get("name"), m.get("preference"), m.get("budget_range"), m.get("notes"), m.get("last_interacted_at")])

    print(f"📊 [GWS Engine] Đã xuất file Google Sheets Master: {sheet_file}")
    return sheet_file

def send_gmail_daily_digest(recipient_email="admin@hame.enterprise"):
    """Tự động tạo HTML Email Digest báo cáo gửi qua Gmail."""
    st = get_affiliate_revenue_stats()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
      <h2 style="color: #4285f4; text-align: center;">📊 Báo Cáo Doanh Thu Google Workspace (Gmail Digest)</h2>
      <p style="text-align: center; color: #666;">Thời gian báo cáo: {now_str}</p>
      <hr>
      <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
        <h3 style="margin-top: 0; color: #34a853;">💰 Chỉ Số Doanh Thu Affiliate:</h3>
        <ul>
          <li><b>Hoa Hồng Dự Kiến:</b> <span style="color: #ea4335; font-size: 1.1em;">{st['total_commission']:,.0f} VNĐ</span></li>
          <li><b>Tổng Lượt Click:</b> {st['total_clicks']} clicks</li>
          <li><b>Số Link Đang Active:</b> {st['total_links']} links</li>
        </ul>
      </div>
      <p style="font-size: 0.9em; color: #555;">Cỗ máy HAME Enterprise đang vận hành tự động 24/7. Bạn có thể mở ứng dụng Desktop hoặc Web UI để xem chi tiết.</p>
    </div>
    """

    output_dir = os.path.join(fb_poster_dir, "gws_exports")
    os.makedirs(output_dir, exist_ok=True)
    digest_file = os.path.join(output_dir, "gmail_daily_digest.html")
    with open(digest_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"📧 [GWS Engine] Đã khởi tạo Gmail Digest HTML report gửi tới {recipient_email}: {digest_file}")
    return digest_file

def sync_calendar_events():
    """Đồng bộ lịch 7 ngày AI Content sang định dạng Google Calendar (ICS / JSON)."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE status='pending' ORDER BY scheduled_at ASC LIMIT 10")
    posts = [dict(r) for r in cursor.fetchall()]
    conn.close()

    output_dir = os.path.join(fb_poster_dir, "gws_exports")
    os.makedirs(output_dir, exist_ok=True)

    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//HAME Enterprise//Google Workspace Sync//EN\n"
    for p in posts:
        sch_str = p.get("scheduled_at", "").replace("-", "").replace(":", "").replace(" ", "T")
        ics_content += f"BEGIN:VEVENT\nSUMMARY:HAME Post: {p.get('name', 'Bài Đăng FB')}\nDESCRIPTION:{p.get('content', '')[:100]}\nDTSTART:{sch_str}\nEND:VEVENT\n"
    ics_content += "END:VCALENDAR\n"

    ics_file = os.path.join(output_dir, "hame_calendar_schedule.ics")
    with open(ics_file, "w", encoding="utf-8") as f:
        f.write(ics_content)

    print(f"📅 [GWS Engine] Đã tạo file Google Calendar ICS: {ics_file}")
    return ics_file

if __name__ == "__main__":
    export_leads_to_google_sheets()
    send_gmail_daily_digest()
    sync_calendar_events()

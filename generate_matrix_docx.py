import os
import sys
import docx
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

desktop_path = r"C:\Users\TOSHIBA\Desktop"
docx_file_path = os.path.join(desktop_path, "HAME_Enterprise_v28_Account_Matrix_Guide.docx")

doc = Document()

style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(13)
font.color.rgb = RGBColor(0x1e, 0x29, 0x3b)

def format_run(run, size=13, bold=False, italic=False, color_rgb=(0x1e, 0x29, 0x3b)):
    run.font.name = 'Times New Roman'
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)

def add_custom_heading(doc, text, level):
    h = doc.add_heading(level=level)
    run = h.add_run(text)
    if level == 1:
        format_run(run, size=22, bold=True, color_rgb=(0x4f, 0x46, 0xe5))
    elif level == 2:
        format_run(run, size=17, bold=True, color_rgb=(0x02, 0x84, 0xc7))
    elif level == 3:
        format_run(run, size=14, bold=True, color_rgb=(0x7c, 0x3a, 0xed))
    return h

# Title
title_p = doc.add_paragraph()
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r1 = title_p.add_run("👥 KIẾN TRÚC PHÂN BỔ NICK & QUY TRÌNH ĐIỀU PHỐI VẬN HÀNH\n")
format_run(r1, size=24, bold=True, color_rgb=(0x4f, 0x46, 0xe5))

r2 = title_p.add_run("Hệ Thống HAME Enterprise Suite v28.0 (15 Nick Matrix)\n")
format_run(r2, size=14, bold=True, color_rgb=(0x1e, 0x1b, 0x4b))

r3 = title_p.add_run("Mục tiêu: Vận hành tự động hóa 15 Nick Facebook để đạt 20 - 50 Triệu VNĐ / Tháng")
format_run(r3, size=12, italic=True, color_rgb=(0x22, 0xc5, 0x5e))

doc.add_paragraph().add_run("―" * 50)

# Section 1
add_custom_heading(doc, "1. SỐ LƯỢNG NICK CẦN THIẾT & BẢNG PHÂN BỔ VAI TRÒ (15 NICK MATRIX)", level=1)
p = doc.add_paragraph()
r = p.add_run("Để cỗ máy vận hành mượt mà và không bị gián đoạn, sếp cần chuẩn bị 10 - 15 Nick Facebook được chia thành 3 Đội ngũ chuyên biệt:")
format_run(r, size=12)

table1 = doc.add_table(rows=1, cols=4)
table1.alignment = WD_TABLE_ALIGNMENT.CENTER
hdr_cells = table1.rows[0].cells
hdr_cells[0].text = 'Đội Ngũ Nick'
hdr_cells[1].text = 'Số Lượng'
hdr_cells[2].text = 'Nhiệm Vụ & Vai Trò Chính'
hdr_cells[3].text = 'Cấu Hình Trust Score'

for cell in hdr_cells:
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            format_run(run, size=11, bold=True, color_rgb=(0xff, 0xff, 0xff))

acc_data = [
    ("Đội 1: Nick Profile Vệ Tinh (Chốt Đơn)", "3 Nick", "Bóc bạn bè đối thủ (/targetfriends), kết bạn 5.000 người, AI tự chat chốt đơn Messenger (/inbox) & nhắn bán chéo (/crosssell).", "Trust Score > 90 điểm. Avatar chuyên nghiệp."),
    ("Đội 2: Nick Rải Bài Mồi (Flash Sale)", "7 Nick", "Gia nhập các Nhóm ngách (/joingroups), tự động cào bài Flash Sale Shopee (/flashsale), thả link Affiliate ở Bình luận 1.", "Trust Score > 85 điểm. Mỗi nick join 20-30 nhóm."),
    ("Đội 3: Nick Seeding (Tạo Hiệu Ứng)", "5 Nick", "Tự nhảy vào bài rải của Đội 2 để comment mồi ('Ib em với', 'Check inbox nha shop') tăng tương tác đám đông.", "Nuôi tự động (/nurture) 30p/ngày. Trust > 80.")
]

for team, qty, task, trust in acc_data:
    row_cells = table1.add_row().cells
    row_cells[0].text = team
    row_cells[1].text = qty
    row_cells[2].text = task
    row_cells[3].text = trust

for row in table1.rows:
    for cell in row.cells:
        for p in cell.paragraphs:
            for r in p.runs:
                format_run(r, size=11)

# Section 2
add_custom_heading(doc, "2. QUY TRÌNH ĐIỀU PHỐI VẬN HÀNH THEO KHUNG GIỜ GIỮA CÁC ĐỘI NICK", level=1)

matrix_steps = [
    ("⏰ 08:00 AM - BUỔI SÁNG: Kích Hoạt Đội 2 Rải Bài & Đội 3 Seeding",
     "• Sếp mở Telegram trên iPhone, bấm phím '/radar' xem ngành hàng hot -> Bấm phím '💰 Săn Deal Flash Sale' (/flashsale Thời Trang Nữ).\n• 7 Nick Đội 2 tự động chia nhau rải bài mồi lên 200 Nhóm Facebook ngách (khoảng cách 15 phút/bài để tránh checkpoint).\n• Ngay sau khi bài lên, 5 Nick Đội 3 tự động nhảy vào thả tim và comment mồi dưới bài viết để tạo hiệu ứng đám đông."),

    ("⏰ 12:00 PM - BUỔI TRƯA: Kích Hoạt Đội 1 Chốt Đơn & Kiểm Tra Màn Hình",
     "• Sếp mở Telegram trên iPhone, bấm phím '🤖 AI Auto-Closer Inbox' (/inbox).\n• 3 Nick Đội 1 tự động quét Messenger Inbox, dùng Trí nhớ Hermes đọc lịch sử mua sắm của khách và tư vấn chốt đơn 24/7.\n• Sếp bấm phím '👁️ Chụp Màn Hình Live' (/snap) để kiểm tra bức ảnh thao tác của Robot."),

    ("⏰ 16:00 PM - BUỔI CHIỀU: Đội 1 Bóc Bạn Bè Đối Thủ & Nuôi Tự Động",
     "• Sếp bấm phím '🎯 Bóc Bạn Bè Đối Thủ' (/targetfriends <URL_FB>).\n• 3 Nick Đội 1 tự động gửi lời mời kết bạn với khách hàng của đối thủ (mỗi nick gửi 20 bạn/ngày).\n• Sếp bấm phím '🌱 Nuôi Nick Facebook' (/nurture) để toàn bộ 15 Nick tự động lướt Reels & Like để tăng uy tín."),

    ("⏰ 20:00 PM - BUỔI TỐI: Kích Hoạt Đội 1 Bán Chéo Khách Cũ & Xuất Báo Cáo Data",
     "• Sếp bấm phím '🎯 AI Cross-Sell' (/crosssell Túi Xách VÍ ELLY).\n• 3 Nick Đội 1 tự động nhắn tin cá nhân hóa tặng mã giảm giá 30% cho khách cũ đã mua hàng 7 ngày trước.\n• Sếp bấm phím '📊 Google Sheets Sync' (/gwsheet) để xuất toàn bộ số liệu lượt click và hoa hồng ra Google Sheets.")
]

for time_title, detail in matrix_steps:
    add_custom_heading(doc, time_title, level=2)
    p = doc.add_paragraph()
    r = p.add_run(detail)
    format_run(r, size=12)

# Section 3
add_custom_heading(doc, "3. BÍ QUYẾT PHÒNG TRÁNH KHÓA NICK (ANTI-CHECKPOINT PROTOCOL)", level=1)

rules = [
    "Quy Tắc Xoay Vòng IP (Proxy/Dcom): Nếu chạy trên 5 nick, bật 4G Dcom tự động đổi IP sau mỗi lượt rải bài.",
    "Giới Hạn Tần Suất Đăng Bài: Đội 2 đăng bài cách nhau 15 - 25 phút/lần. Mỗi nick không đăng quá 15 nhóm/ngày.",
    "Nuôi Nick Đều Đặn: Luôn bật tiến trình nuôi nick (/nurture) mỗi ngày để giữ Trust Score luôn đạt trên 85 - 90 điểm."
]
for rule in rules:
    p = doc.add_paragraph(style='List Bullet')
    r = p.add_run(rule)
    format_run(r, size=12)

doc.add_paragraph().add_run("―" * 50)
final_p = doc.add_paragraph()
final_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = final_p.add_run("🎉 HOÀN THÀNH BẢN THIẾT KẾ PHÂN BỔ 15 NICK & ĐIỀU PHỐI CỖ MÁY HAME ENTERPRISE v28.0!")
format_run(r, size=14, bold=True, color_rgb=(0x4f, 0x46, 0xe5))

doc.save(docx_file_path)
print(f"SUCCESS_MATRIX_DOCX: {docx_file_path}")

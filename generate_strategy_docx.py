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
docx_file_path = os.path.join(desktop_path, "HAME_Enterprise_v28_30Days_Strategy.docx")

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
r1 = title_p.add_run("🚀 CHIẾN LƯỢC 30 NGÀY BỨT PHÁ THU NHẬP THỤ ĐỘNG (X5 - X10)\n")
format_run(r1, size=24, bold=True, color_rgb=(0x4f, 0x46, 0xe5))

r2 = title_p.add_run("Cùng Cỗ Máy HAME Enterprise v28.0 (ReactBits Motion Edition)\n")
format_run(r2, size=14, bold=True, color_rgb=(0x1e, 0x1b, 0x4b))

r3 = title_p.add_run("Mục tiêu: Đạt 20.000.000 - 50.000.000 VNĐ / Tháng dòng tiền thụ động từ Affiliate & Bán lẻ")
format_run(r3, size=12, italic=True, color_rgb=(0x22, 0xc5, 0x5e))

doc.add_paragraph().add_run("―" * 50)

# 5 Pillars
add_custom_heading(doc, "📌 5 TRỤ CỘT TĂNG TRƯỞNG DOANH THU TOÀN DIỆN", level=1)

pillars = [
    ("💎 CHIẾN DỊCH 1: THẢ LINK BÌNH LUẬN 1 (BẮT TREND FLASH SALE 50%)",
     "Mục tiêu: Tạo 1.000 - 3.000 lượt Click Link Affiliate mỗi ngày mà KHÔNG bị Facebook bóp tương tác.\nThao tác: Mỗi sáng lúc 08:00 AM bấm nút '🌍 World Monitor Radar' (/radar) -> Bấm nút '💰 Săn Deal Flash Sale' (/flashsale). Robot tự cào deal hot >50%, gắn link Affiliate SubID & thả link ở Bình Luận 1 để bài đăng đạt Reach cao nhất!"),
    
    ("💎 CHIẾN DỊCH 2: BÓC TỆP KHÁCH HÀNG CAO CẤP CỦA ĐỐI THỦ",
     "Mục tiêu: Xây dựng 5 tài khoản Facebook cá nhân đạt 5.000 bạn bè chuẩn ngách mua sắm.\nThao tác: Bấm nút '🎯 Bóc Bạn Bè Đối Thủ' (/targetfriends <URL_FB_Đối_Thủ>) -> Bấm nút '🌱 Nuôi Nick Facebook' (/nurture) 30 phút/ngày để giữ Trust Score >90 điểm an toàn 100%."),
    
    ("💎 CHIẾN DỊCH 3: VÒNG XOÁY BÁN CHÉO TỰ ĐỘNG GBRAIN (AI CROSS-SELL FLYWHEEL)",
     "Mục tiêu: Tăng giá trị vòng đời khách hàng (CLV) và tạo thêm 40% doanh thu thụ động từ tệp khách cũ.\nThao tác: Khi khách mua Ví da (Sản phẩm A) -> GBrain Graph ghi nhớ -> Sau 7 ngày bấm nút '🎯 AI Cross-Sell' (/crosssell Túi Xách VÍ ELLY) để AI nhắn tin ưu đãi giảm 30% bán kèm sản phẩm B!"),
    
    ("💎 CHIẾN DỊCH 4: SÁNG TẠO VIDEO AI NGẮN MULTI-CHANNEL (REELS VIRALITY)",
     "Mục tiêu: Phủ sóng Video ngắn quảng cáo sản phẩm trên Facebook Reels & Groups.\nThao tác: Bấm nút '🎬 Tạo Video AI & Đăng' (/createvideo Ví Da ELLY 500k all) -> AI tự viết kịch bản AIDA, ghép video & rải lên Reels để kéo triệu view tự nhiên."),
    
    ("💎 CHIẾN DỊCH 5: DỮ LIỆU TỐI ƯU VỚI GOOGLE WORKSPACE (DATA-DRIVEN SCALE)",
     "Mục tiêu: Lọc ra Top 20% sản phẩm ra tiền nhiều nhất để nhân bản doanh số x10.\nThao tác: Buổi tối bấm nút '📊 Google Sheets Sync' (/gwsheet) -> Mở file Google Sheets lọc ra nhóm 20% sản phẩm hoa hồng cao nhất để nhân bản quy mô!")
]

for title, desc in pillars:
    add_custom_heading(doc, title, level=2)
    p = doc.add_paragraph()
    r = p.add_run(desc)
    format_run(r, size=12)

# Action Plan Table
add_custom_heading(doc, "📅 LỊCH VẬN HÀNH 30 NGÀY TỪNG TUẦN (ACTION PLAN)", level=1)

table = doc.add_table(rows=1, cols=3)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
hdr_cells = table.rows[0].cells
hdr_cells[0].text = 'Tuần'
hdr_cells[1].text = 'Mục Tiêu & Hành Động Trọng Tâm'
hdr_cells[2].text = 'Sản Phẩm Đầu Ra'

for cell in hdr_cells:
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            format_run(run, size=11, bold=True, color_rgb=(0xff, 0xff, 0xff))

plan_data = [
    ("Tuần 1", "Chuẩn hóa 5 nick Facebook -> Bật /nurture nuôi nick -> Gõ /targetfriends bóc bạn bè đối thủ.", "5 Nick đạt Trust Score >90, 2.000 bạn bè chuẩn ngách."),
    ("Tuần 2", "Bật /radar quét Trend -> Bật /flashsale rải bài mồi link ở Bình luận 1 -> Bật /inbox tự chốt đơn.", "Thu về 500 - 1.000 clicks/ngày, bắt đầu có hoa hồng đều đặn."),
    ("Tuần 3", "Kích hoạt /createvideo rải bài Facebook Reels -> Bật /crosssell nhắn tin tặng mã -30% cho khách cũ.", "Doanh thu bùng nổ từ cả khách mới lẫn khách cũ tái mua."),
    ("Tuần 4", "Bấm /gwsheet xuất báo cáo Google Sheets -> Lọc Top 20% SP bán chạy -> Nhân bản quy mô x5.", "Cán mốc 20 - 50 triệu VNĐ/tháng dòng tiền thụ động.")
]

for week, act, out in plan_data:
    row_cells = table.add_row().cells
    row_cells[0].text = week
    row_cells[1].text = act
    row_cells[2].text = out

for row in table.rows:
    for cell in row.cells:
        for p in cell.paragraphs:
            for r in p.runs:
                format_run(r, size=11)

doc.save(docx_file_path)
print(f"SUCCESS_STRATEGY_DOCX: {docx_file_path}")

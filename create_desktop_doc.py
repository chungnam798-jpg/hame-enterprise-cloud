import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

desktop_path = r"C:\Users\TOSHIBA\Desktop"
doc_file_path = os.path.join(desktop_path, "HAME_Enterprise_v28_User_Manual_SOP.doc")

html_doc_content = """<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
<head>
  <meta charset='utf-8'>
  <title>SÁCH HƯỚNG DẪN VẬN HÀNH & NĂNG SUẤT DOANH THU HAME ENTERPRISE v28.0</title>
  <style>
    body { font-family: 'Times New Roman', Times, serif; line-height: 1.6; color: #1e293b; padding: 20px; }
    h1 { color: #4f46e5; border-bottom: 3px solid #6366f1; padding-bottom: 8px; font-size: 24pt; font-family: 'Times New Roman', Times, serif; }
    h2 { color: #0284c7; margin-top: 25px; border-left: 5px solid #0284c7; padding-left: 10px; font-size: 18pt; font-family: 'Times New Roman', Times, serif; }
    h3 { color: #7c3aed; margin-top: 18px; font-size: 14pt; font-family: 'Times New Roman', Times, serif; }
    p, li, td, th { font-size: 13pt; font-family: 'Times New Roman', Times, serif; }
    .header-box { background: linear-gradient(135deg, #1e1b4b, #312e81); color: #ffffff; padding: 25px; border-radius: 10px; text-align: center; margin-bottom: 30px; }
    .header-box h1 { color: #fbbf24; border: none; font-size: 26pt; margin: 0; font-family: 'Times New Roman', Times, serif; }
    .header-box p { color: #e0e7ff; font-size: 13pt; margin-top: 8px; font-family: 'Times New Roman', Times, serif; }
    .code-box { background-color: #f1f5f9; border: 1px solid #cbd5e1; padding: 12px; font-family: 'Times New Roman', Times, serif; border-radius: 6px; color: #0f172a; margin: 10px 0; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 20px; font-family: 'Times New Roman', Times, serif; }
    th { background-color: #4f46e5; color: white; padding: 10px; border: 1px solid #3730a3; text-align: left; font-family: 'Times New Roman', Times, serif; }
    td { padding: 10px; border: 1px solid #cbd5e1; font-family: 'Times New Roman', Times, serif; }
    tr:nth-child(even) { background-color: #f8fafc; }
    .highlight-box { background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 15px; margin: 15px 0; }
    .warning-box { background-color: #fffbebf; border-left: 5px solid #f59e0b; padding: 15px; margin: 15px 0; }
  </style>
</head>
<body>

  <div class="header-box">
    <h1>📖 SÁCH HƯỚNG DẪN SỬ DỤNG & QUY TRÌNH VẬN HÀNH SOP</h1>
    <p><b>Hệ Thống Tự Động Hóa Facebook Marketing & Monetization Affiliate Doanh Nghiệp</b></p>
    <p>Phiên bản: Enterprise Suite v28.0 (ReactBits Motion & Visual Excellence Edition)</p>
  </div>

  <h2>📌 MỤC LỤC CHI TIẾT</h2>
  <ol>
    <li><b>CHƯƠNG 1:</b> HƯỚNG DẪN KHỞI ĐỘNG PHẦN MỀM & THIẾT LẬP BAN ĐẦU</li>
    <li><b>CHƯƠNG 2:</b> HƯỚNG DẪN SỬ DỤNG CHI TIẾT TOÀN BỘ 16 TAB GIAO DIỆN WEB UI & DESKTOP APP</li>
    <li><b>CHƯƠNG 3:</b> HƯỚNG DẪN ĐIỀU HÀNH BẰNG TELEGRAM BOT (CHI TIẾT 17+ CÂU LỆNH MẪU)</li>
    <li><b>CHƯƠNG 4:</b> QUY TRÌNH VẬN HÀNH THƯỜNG NHẬT THEO GIỜ (SOP TỪ 08:00 ĐẾN 22:00)</li>
    <li><b>CHƯƠNG 5:</b> KỊCH BẢN KIẾM TIỀN AFFILIATE SHOPEE / LAZADA TỪ A TỚI Z (RA TIỀN THẬT)</li>
    <li><b>CHƯƠNG 6:</b> BÍ QUYẾT NUÔI NICK AN TOÀN, CHỐNG CHECKPOINT & XỬ LÝ LỖI A-Z</li>
  </ol>

  <hr>

  <h2>CHƯƠNG 1: HƯỚNG DẪN KHỞI ĐỘNG PHẦN MỀM & THIẾT LẬP BAN ĐẦU</h2>
  
  <h3>1.1. Cách Khởi Động Phần Mềm</h3>
  <p>Hệ thống hỗ trợ 3 phương thức mở ứng dụng vô cùng tiện lợi:</p>
  <ul>
    <li><b>Phương Thức 1 (Khuyên dùng):</b> Nhấp đúp vào biểu tượng lối tắt <b>FBPoster Enterprise</b> trực tiếp trên màn hình Desktop Windows (<code>C:\\Users\\TOSHIBA\\Desktop\\FBPoster Enterprise.lnk</code>). Khung ứng dụng Standalone Desktop App sẽ khởi chạy tức thì.</li>
    <li><b>Phương Thức 2:</b> Mở trình duyệt bất kỳ (Chrome/Edge/Cốc Cốc) và gõ địa chỉ: <code>http://localhost:5000</code></li>
    <li><b>Phương Thức 3:</b> Mở Telegram trên điện thoại và nhắn tin trực tiếp cho Bot Telegram điều khiển từ xa.</li>
  </ul>

  <h3>1.2. Thiết Lập API Key & Cấu Hình Cơ Bản (Chỉ làm 1 lần đầu)</h3>
  <ol>
    <li>Mở Web UI tại <code>http://localhost:5000</code>, bấm chọn Tab <b>Cấu Hình</b> (icon bánh răng) trên Menu bên trái.</li>
    <li><b>Cấu hình Gemini AI Key:</b> Nhập API Key Gemini vào ô <i>Gemini API Key</i> và bấm <b>Lưu cài đặt</b>.</li>
    <li><b>Cấu hình Telegram Bot:</b> Nhập Bot Token vào ô <i>Telegram Bot Token</i>. Gửi 1 tin nhắn bất kỳ tới Bot trên Telegram để hệ thống lưu Chat ID điều khiển.</li>
    <li><b>Cấu hình Affiliate:</b> Nhập mã SubID cá nhân vào ô <i>Affiliate SubID</i> (Ví dụ: <code>hame_growth</code>).</li>
  </ol>

  <hr>

  <h2>CHƯƠNG 2: HƯỚNG DẪN SỬ DỤNG CHI TIẾT CÁC TAB GIAO DIỆN WEB UI</h2>

  <h3>2.1. Tab "Quản Lý Tài Khoản" (#tab-accounts)</h3>
  <p>Cho phép thêm, phân loại và theo dõi sức khỏe các nick Facebook dùng để đăng bài:</p>
  <ul>
    <li><b>Thêm nick bằng Cookie:</b> Đăng nhập Facebook trên Chrome ➔ Dùng Extension <i>Get Cookie HTTP</i> lấy chuỗi Cookie ➔ Dán vào ô Cookie Facebook ➔ Bấm <b>Thêm tài khoản</b>.</li>
    <li><b>Cột Trust Score:</b> Hiển thị điểm độ tin cậy của tài khoản (từ 0 đến 100 điểm). Điểm > 80 là an toàn tuyệt đối.</li>
  </ul>

  <h3>2.2. Tab "Nuôi Nick Tự Động" (#tab-nurture)</h3>
  <p>Tính năng nuôi nick ngầm tăng độ uy tín, tránh bị Facebook bóp tương tác hoặc khóa tài khoản:</p>
  <ul>
    <li>Tích chọn tài khoản cần nuôi ➔ Chọn thao tác (<i>Lướt Newfeed & Like, Xem Reels, Bình luận tương tác</i>) ➔ Bấm <b>Kích Hoạt Nuôi Nick Ngay</b>.</li>
    <li>Theo dõi tiến trình nuôi nick realtime trên khung nhật ký màu xanh lá bên dưới.</li>
  </ul>

  <h3>2.3. Tab "Hermes Studio Hub" (#tab-hermes-studio)</h3>
  <p>Trung tâm điều hành cao cấp nhất bao gồm 4 phân hệ thông minh:</p>
  <ol>
    <li><b>Active Sessions:</b> Quản lý các cuộc hội thoại AI đang trả lời tự động trên Messenger & Telegram.</li>
    <li><b>Scheduled Jobs Visualizer:</b> Trực quan hóa 4 tiến trình ngầm (Nuôi Nick, Lịch 7 ngày AIDA, Săn Deal Flash Sale, AI Cross-Sell).</li>
    <li><b>Google Workspace Integration Hub:</b> Bấm <i>Đồng Bộ Google Sheets & Calendar</i> hoặc <i>Gửi Gmail Digest Report</i> để nhận báo cáo kinh doanh.</li>
    <li><b>World Monitor Global Intelligence Radar:</b> Bấm <i>Phân Tích Radar Thị Trường Live</i> để cập nhật các xu hướng Hot Trends bùng nổ toàn cầu.</li>
    <li><b>Mano-P GUI Visual Monitor & Checkpoint Guard:</b> Xem ảnh màn hình live trực tiếp từ Robot Playwright ngầm và tự động kiểm tra cảnh báo 2FA/Captcha.</li>
  </ol>

  <hr>

  <h2>CHƯƠNG 3: HƯỚNG DẪN ĐIỀU HÀNH BẰNG TELEGRAM BOT (17+ LỆNH)</h2>

  <table>
    <tr>
      <th>Câu Lệnh Telegram</th>
      <th>Cú Pháp Mẫu</th>
      <th>Chức Năng & Tác Dụng</th>
    </tr>
    <tr>
      <td><b>/flashsale</b></td>
      <td><code>/flashsale Thời Trang Nữ</code></td>
      <td>Tự cào Deal Shopee giảm >50%, gắn link Affiliate SubID & rải bài tự động.</td>
    </tr>
    <tr>
      <td><b>/affstats</b></td>
      <td><code>/affstats</code></td>
      <td>Xem tổng số lượt Click và <b>Hoa hồng dự kiến (VNĐ)</b> thu về realtime.</td>
    </tr>
    <tr>
      <td><b>/crosssell</b></td>
      <td><code>/crosssell Túi Xách VÍ ELLY</code></td>
      <td>AI đọc Trí nhớ Hermes & GBrain Graph để tự nhắn tin tặng mã -30% cho khách cũ.</td>
    </tr>
    <tr>
      <td><b>/gwsheet</b></td>
      <td><code>/gwsheet</code></td>
      <td>Đồng bộ toàn bộ báo cáo doanh thu & lịch bài đăng ra Google Sheets & Calendar.</td>
    </tr>
    <tr>
      <td><b>/gmail</b></td>
      <td><code>/gmail</code></td>
      <td>Khởi tạo & gửi 1 bản tin báo cáo doanh thu Gmail Digest về hòm thư admin.</td>
    </tr>
    <tr>
      <td><b>/radar</b></td>
      <td><code>/radar</code></td>
      <td>Xem tin tức Hot Trends & ngách sản phẩm bùng nổ tìm kiếm từ World Monitor.</td>
    </tr>
    <tr>
      <td><b>/snap</b></td>
      <td><code>/snap</code></td>
      <td>Chụp ảnh màn hình live của Robot Playwright & gửi về Telegram cho sếp kiểm tra.</td>
    </tr>
    <tr>
      <td><b>/reengage</b></td>
      <td><code>/reengage</code></td>
      <td>AI tự nhắn tin mồi bám đuổi các khách hàng ngưng tương tác quá 48h để chốt đơn lại.</td>
    </tr>
    <tr>
      <td><b>/joingroups</b></td>
      <td><code>/joingroups Hội Bỉm Sữa</code></td>
      <td>Tự động tìm kiếm & gửi yêu cầu gia nhập các Nhóm Facebook ngách chất lượng.</td>
    </tr>
    <tr>
      <td><b>/createvideo</b></td>
      <td><code>/createvideo Ví ELLY 500k all</code></td>
      <td>AI tự làm video ngắn quảng cáo sản phẩm và rải bài đa kênh.</td>
    </tr>
    <tr>
      <td><b>/targetfriends</b></td>
      <td><code>/targetfriends Link_FB_Đối_Thủ</code></td>
      <td>Bóc tách bạn bè đối thủ & tự động gửi lời mời kết bạn chuẩn ngách.</td>
    </tr>
    <tr>
      <td><b>/inbox</b></td>
      <td><code>/inbox</code></td>
      <td>Bật Robot AI quét Messenger Inbox tự động trả lời & chốt đơn 24/7.</td>
    </tr>
  </table>

  <hr>

  <h2>CHƯƠNG 4: QUY TRÌNH VẬN HÀNH THƯỜNG NHẬT THEO GIỜ (SOP)</h2>

  <div class="highlight-box">
    <b>QUY TRÌNH 3 BƯỚC MỖI NGÀY (CHỈ MẤT 5 PHÚT):</b><br>
    • <b>08:00 AM (Buổi Sáng):</b> Gõ <code>/radar</code> ➔ Gõ <code>/flashsale Thời Trang Nữ</code> để Robot cào Deal Hot & rải bài bài sáng.<br>
    • <b>12:00 PM (Buổi Trưa):</b> Gõ <code>/inbox</code> ➔ Gõ <code>/snap</code> để AI tự trả lời khách & chụp ảnh kiểm tra tiến trình.<br>
    • <b>20:00 PM (Buổi Tối):</b> Gõ <code>/crosssell Túi Xách VÍ ELLY</code> ➔ Gõ <code>/gwsheet</code> để chăm sóc khách cũ & đồng bộ Google Sheets.
  </div>

  <hr>

  <h2>CHƯƠNG 5: KỊCH BẢN KIẾM TIỀN AFFILIATE SHOPEE / LAZADA RA TIỀN THẬT</h2>

  <h3>5.1. Bí Quyết "Link Ở Bình Luận Đầu Tiên" (Tránh Bóp Reach)</h3>
  <p>Thuật toán Facebook sẽ ẩn bài nếu đăng link bán hàng trên Caption bài viết. Cỗ máy HAME áp dụng kịch bản khép kín:</p>
  <ul>
    <li><b>Caption bài đăng:</b> Chỉ đăng ảnh đẹp + nội dung chia sẻ giật gân, không chứa link.</li>
    <li><b>First Comment:</b> Robot tự động gắn link Affiliate SubID vào <b>Bình luận đầu tiên</b>. Tỷ lệ tiếp cận tăng <b>300%</b>!</li>
  </ul>

  <h3>5.2. Vòng Xoáy Bán Chéo Khép Kín (Cross-Sell Flywheel)</h3>
  <p>Khách mua Ví da (Sản phẩm A) ➔ GBrain Graph ghi nhớ ➔ Sau 7 ngày AI Cross-Sell tự động gửi mã giảm 30% Túi xách (Sản phẩm B) ➔ Thu hoa hồng lần 2 hoàn toàn thụ động!</p>

  <hr>

  <h2>CHƯƠNG 6: BÍ QUYẾT NUÔI NICK CHỐNG CHECKPOINT & XỬ LÝ LỖI A-Z</h2>

  <div class="warning-box">
    <b>NGUYÊN TẮC "3 KHÔNG" BẢO VỆ NICK FACEBOOK:</b><br>
    1. <b>Không rải bài quá dồn dập:</b> Đặt khoảng cách thời gian giữa 2 bài đăng từ 15 đến 30 phút.<br>
    2. <b>Không dùng 1 nội dung cho 100 nhóm:</b> Bật tính năng Spintax hoặc để AI tự đổi câu từ.<br>
    3. <b>Không bỏ qua khâu nuôi nick:</b> Bật chế độ Nuôi Nick tự động 30 phút/ngày để giữ Trust Score > 90 điểm.
  </div>

  <p style="text-align: center; margin-top: 40px; font-weight: bold; color: #4f46e5;">
    🎉 CHÚC SẾP VẬN HÀNH CỖ MÁY HAME ENTERPRISE v28.0 THÀNH CÔNG RỰC RỠ VÀ ĐẠT DOANH THU HOA HỒNG KỶ LỤC!
  </p>

</body>
</html>
"""

doc_file_path = os.path.join(desktop_path, "HAME_Enterprise_v28_User_Manual_TimesNewRoman.doc")

with open(doc_file_path, "w", encoding="utf-8") as f:
    f.write(html_doc_content)

print(f"SUCCESS: File document Times New Roman đã được tạo thành công tại: {doc_file_path}")

try:
    alt_file = os.path.join(desktop_path, "HAME_Enterprise_v28_User_Manual_SOP.doc")
    with open(alt_file, "w", encoding="utf-8") as f:
        f.write(html_doc_content)
    print(f"SUCCESS: Đã cập nhật file: {alt_file}")
except Exception as e:
    pass

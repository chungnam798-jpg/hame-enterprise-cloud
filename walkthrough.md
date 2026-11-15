# Hướng dẫn chi tiết & Nhật ký phát triển (FBPoster v1.5)

Chúng tôi đã hoàn thành phát triển và nâng cấp toàn diện phiên bản **FBPoster v1.5** - tích hợp module **Tương tác Bảng tin & Nhóm tự động (Auto-Feed Engagement)**. Hệ thống hiện có khả năng quét ngầm thông minh trên bảng tin nhóm hoặc trang cá nhân, tự động thả tim và để lại bình luận tự nhiên bằng Gemini AI (hoặc theo cấu trúc mẫu Spintax xoay vòng) giúp tăng độ tương tác chéo tối đa và tự động tiếp cận khách hàng.

---

## Tính năng tương tác bảng tin/nhóm mới (v1.5)

1. **Auto-Feed Engagement (Tương tác bảng tin chéo)**:
   - Tự động quét bảng tin nhóm đã tham gia (`https://www.facebook.com/groups/feed/`) hoặc bảng tin chính (`https://www.facebook.com/`).
   - Tự động bỏ qua các bài viết tự quảng cáo (sponsored), bài viết của chính chủ hoặc bài viết đã tương tác rồi (thông qua kiểm tra thuộc tính `aria-pressed` của nút Like).
   - Thả tim và viết bình luận tương thích mô phỏng hành vi gõ bàn phím, di chuyển chuột của người dùng thực tế.

2. **Tích hợp Gemini 2.5 Flash thông minh**:
   - Sử dụng mô hình **Gemini 2.5 Flash** phân tích ngữ cảnh, nội dung bài viết và tên tác giả để sinh bình luận tự nhiên dưới 20 từ (ví dụ: khen ngợi sản phẩm, chúc mừng, hỏi han...).
   - Đảm bảo bình luận phong phú, tránh rủi ro spam và bị khóa tài khoản.

3. **Cấu hình Spintax linh hoạt**:
   - Bên cạnh AI, người dùng có thể cấu hình các câu mẫu Spintax ngẫu nhiên chống trùng lặp: `{Hay quá|Tuyệt vời|Đỉnh quá}! Chúc bạn {ngày mới tốt lành|buôn may bán đắt}!`.

4. **Chạy ngầm (Background Worker Thread)**:
   - Tiến trình `autofeed_worker` chạy định kỳ trong nền theo số phút cài đặt, duyệt qua toàn bộ các tài khoản đang hoạt động để chạy quét và tự động lưu báo cáo.

---

## Chi tiết các tệp tin đã phát triển & nâng cấp

Tất cả mã nguồn được lưu trữ tại thư mục [C:\Users\TOSHIBA\.gemini\antigravity\scratch\fb-poster](file:///C:/Users/TOSHIBA/.gemini/antigravity/scratch/fb-poster).

- **Database Layer**:
  - [database.py](file:///C:/Users/TOSHIBA/.gemini/antigravity/scratch/fb-poster/database.py): Tích hợp 6 trường cấu hình Auto-Feed vào hệ thống cài đặt mặc định (`autofeed_engage_enabled`, `autofeed_engage_source`, `autofeed_max_posts_per_scan`, v.v.).
- **Browser Automation**:
  - [automation.py](file:///C:/Users/TOSHIBA/.gemini/antigravity/scratch/fb-poster/automation.py): Triển khai hàm `auto_engage_feed_posts()` sử dụng Playwright điều hướng và thực hiện Like + Comment chéo tự động. Thêm helper `get_gemini_comment()` gọi API Gemini 2.5 Flash để sinh nội dung bình luận chéo.
- **Backend API & Workers**:
  - [server.py](file:///C:/Users/TOSHIBA/.gemini/antigravity/scratch/fb-poster/server.py): Tạo worker daemon `autofeed_worker()` chạy ngầm và ghi nhận kết quả vào nhật ký tương tác thành công để hiển thị lên dashboard.
- **Frontend UI**:
  - [index.html](file:///C:/Users/TOSHIBA/.gemini/antigravity/scratch/fb-poster/static/index.html): Bổ sung giao diện thiết lập Auto-Feed tại tab Cấu hình hệ thống (bật/tắt chạy ngầm, chọn nguồn, chọn kiểu AI/Spintax, chu kỳ quét...).
  - [app.js](file:///C:/Users/TOSHIBA/.gemini/antigravity/scratch/fb-poster/static/app.js): Đồng bộ hóa settings Auto-Feed với Backend khi tải trang/lưu form và lập trình các hàm ẩn/hiện động `toggleAutofeedSettingsDisplay()` và `toggleAutofeedSpintaxDisplay()`.

---

## Hướng dẫn cấu hình tính năng Auto-Feed Engagement

### Bước 1: Kích hoạt Auto-Feed
1. Truy cập: 👉 **[http://localhost:5000](http://localhost:5000)**.
2. Di chuyển sang tab **Cấu hình hệ thống**.
3. Tick chọn **Tự động thả tim & bình luận Bảng tin/Nhóm (Auto-Feed)**. Giao diện mở rộng sẽ xuất hiện.

### Bước 2: Tùy chỉnh thông số
- **Nguồn tương tác**: Chọn quét trên **Nhóm đã tham gia** hoặc **Bảng tin chính**.
- **Chu kỳ quét bảng tin**: Khoảng thời gian giãn cách giữa các đợt quét (mặc định là 30 phút để an toàn tài khoản).
- **Số bài viết tương tác tối đa**: Giới hạn tương tác (mặc định là 5 bài/lần quét).
- **Phương thức bình luận**: 
  - **Gemini AI**: Hệ thống sẽ tự động bình luận thông minh. Hãy chắc chắn bạn đã điền **Gemini API Key** ở phía trên.
  - **Mẫu Spintax**: Nhập mẫu văn bản của bạn dưới dạng spintax (ví dụ: `{Cảm ơn bạn|Bài viết rất hay|Rất hữu ích}`).
- Bấm **Lưu cấu hình**.

### Bước 3: Kích hoạt thủ công bình luận dạo (Tùy chọn)
Nếu không muốn đợi chu kỳ chạy tự động, bạn có thể chạy bình luận dạo ngay lập tức:
1. Chuyển sang tab **Tương tác tự động**.
2. Tại phần **Kích hoạt bình luận dạo bằng chatbot AI**:
   - Chọn tài khoản thực hiện.
   - Chọn nguồn tương tác (**Nhóm đã tham gia** hoặc **Bảng tin chính**).
3. Bấm nút **Chạy bình luận dạo ngay**. Trình duyệt Playwright sẽ khởi động ngầm để đi bình luận dạo ngay lập tức.

### Bước 4: Xem kết quả tương tác
- Lịch sử tương tác (bao gồm bài viết được like, bình luận AI đã đăng và ảnh chụp màn hình) sẽ xuất hiện tại phần **Nhật ký tương tác** trong tab **Tương tác tự động**.
- Các chỉ số tương tác sẽ được đồng bộ lên biểu đồ thống kê tại màn hình **Dashboard** chính.

---

## Bản sửa lỗi JSON Parse Error (v1.6)

### Lỗi xảy ra:
Lỗi `Unexpected token '<', "<!doctype "... is not valid JSON` xuất hiện ở frontend khi máy chủ trả về một trang HTML thay vì JSON. Điều này thường do:
1. Gặp mã lỗi **HTTP 405 (Method Not Allowed)** hoặc **HTTP 500 (Internal Server Error)** trên endpoint `/api/analyze-link` do server phiên bản cũ bị kẹt trong nền chưa được tải lại tuyến đường mới.
2. Việc gọi `response.json()` hoặc `error.json()` trực tiếp trên phản hồi HTML dẫn đến lỗi phân tích cú pháp nghiêm trọng trong Javascript của trình duyệt.

### Các cải tiến đã áp dụng:
1. **Quản lý Cổng và Tiến trình**: Đã đóng các tiến trình server cũ chạy nền bị kẹt bằng script `kill_port.py` trên cổng 5000, sau đó khởi động lại server mới với định tuyến `/api/analyze-link` hoạt động hoàn chỉnh (trả về JSON chuẩn mã 200).
2. **Cơ chế Phân tích JSON An toàn (`safeJson`)**:
   - Nâng cấp hàm `post()` trong [app.js](file:///C:/Users/TOSHIBA/.gemini/antigravity/scratch/fb-poster/static/app.js) để kiểm tra tính hợp lệ của JSON trước khi phân tích. Nếu máy chủ trả về lỗi HTML hoặc văn bản thông thường, hàm sẽ dịch sang mã lỗi và nội dung thân thiện thay vì gây crash giao diện.
   - Nâng cấp logic bắt lỗi trong `handleLinkAnalysis()` để bắt và hiển thị thông tin lỗi máy chủ chi tiết (Ví dụ: `Lỗi máy chủ (Mã HTTP: 405)` hoặc lỗi định dạng) thay vì hiển thị thông báo cú pháp JSON bí ẩn.
   - Cải tiến xử lý phản hồi lỗi ở chức năng tải lên bài đăng (`handleCreatePost`) để đảm bảo không bị gián đoạn hoạt động của UI khi upload file thất bại.

---

## Bản sửa lỗi Tìm hộp soạn bài viết (v1.7)

### Lỗi xảy ra:
Lỗi `Cannot find post composer box. Facebook UI may have changed.` xảy ra khi Playwright định hướng tới Nhóm/Trang/Bảng tin Facebook nhưng không thể tìm thấy nút kích hoạt khung soạn bài viết. Điều này do:
1. Giao diện Facebook của tài khoản thay đổi (ví dụ: giao diện dạng cột mới, giao diện ngôn ngữ tiếng Việt/tiếng Anh khác nhau).
2. Tốc độ tải trang chậm khiến nút soạn bài viết chưa xuất hiện kịp thời trước khi quét (vấn đề độ trễ bất đồng bộ).
3. Hộp soạn bài viết đôi khi hiển thị dưới dạng trình soạn thảo nội tuyến (inline editor) thay vì hộp thoại bật lên (dialog modal) mặc định.

### Các cải tiến đã áp dụng:
1. **Tìm kiếm Trình soạn thảo Đa dạng hơn**:
   - Thêm danh sách hơn 20 bộ chọn (selectors) khác nhau bao gồm cả tiếng Anh, tiếng Việt, viết hoa, viết thường, các thẻ `span`, `div`, `button` và thuộc tính `role="button"`.
2. **Vòng lặp Chờ Động (Retry Loop)**:
   - Thay thế việc chờ cứng bằng cơ chế chờ động lên tới 15 giây. Định kỳ 1 giây quét lại toàn bộ danh sách bộ chọn cho đến khi tìm thấy nút soạn bài hiển thị thực tế trên màn hình.
3. **Thích ứng với Trình soạn thảo Nội tuyến & Hộp thoại**:
   - Nâng cấp bộ chọn hộp văn bản (`textbox`) hỗ trợ cả `div[role="textbox"]`, `div[contenteditable="true"]`, và bộ chọn dựa trên thuộc tính `aria-label` đa ngôn ngữ.
   - Nâng cấp bộ chọn tải phương tiện (`input[type="file"]`) hỗ trợ tìm kiếm toàn bộ trang chứ không giới hạn trong hộp thoại.
   - Nâng cấp bộ chọn nút **Đăng (Post)** để tìm kiếm mọi nút có nhãn Đăng/Post hiển thị trên màn hình.
4. **Khởi động lại máy chủ**:
    - Đã dừng tiến trình máy chủ cũ và khởi động lại tiến trình mới để cập nhật hoàn chỉnh các thay đổi logic này vào hệ thống lập lịch chạy ngầm (`Scheduler`).

### Kết quả xác thực (Verification Results):
- **Tình trạng kiểm tra**: Thành công rực rỡ (Success).
- **Quy trình thực hiện**:
  1. Đã đặt lại trạng thái của bài viết lỗi `post_baeca307` (nhắm mục tiêu vào ID nhóm `1016613779501681`) về trạng thái `pending` trong cơ sở dữ liệu.
  2. Khởi chạy máy chủ backend `server.py` và tiến trình lập lịch chạy ngầm `Scheduler`.
  3. Tiến trình lập lịch tự động phát hiện và thực hiện đăng bài viết.
  4. Trình duyệt Playwright đã truy cập nhóm Facebook, nhận diện thành công nút soạn thảo thông qua bộ chọn bổ sung:
     `div[role="button"]:has-text("Bạn viết gì đi")`
  5. Điền nội dung vào ô soạn thảo, nhấn nút **Đăng** thành công.
  6. Nhật ký hệ thống ghi nhận: `[Poster] Post post_baeca307 completed successfully.`
  7. Trạng thái bài viết trong `database.db` được cập nhật thành: `posted` với nhật ký kết quả `Đăng bài thành công.`

---

## Bản sửa lỗi Tự động Like & Bình luận dạo Bảng tin (v1.8)

### Lỗi xảy ra:
1. **Chỉ Like mà không bình luận**: Playwright quét qua các bài viết và nhấn Thích được nhưng không thể nhập bình luận chéo (không hiển thị bình luận trên bài viết).
2. **Không nhận diện được nút Like trên một số phiên bản giao diện**: Hệ thống log liên tục ghi nhận `Tìm thấy 0 nút Thích chưa bấm trên màn hình` mặc dù có nhiều bài viết trên bảng tin.
3. **Cấu hình mặc định chọn AI**: Người dùng muốn mặc định tắt tính năng AI (Gemini) để ưu tiên nhập mẫu bình luận Spintax thủ công nhằm kiểm soát nội dung tốt hơn.

### Các cải tiến đã áp dụng:
1. **Nhận diện nút Like linh hoạt hơn**:
   - Thay thế bộ chọn bắt buộc `aria-pressed="false"` bằng `:not([aria-pressed="true"])` trong hàm `auto_engage_feed_posts()`. Điều này giúp hệ thống tìm được các nút Like chưa bấm ngay cả khi Facebook không hiển thị thuộc tính `aria-pressed="false"`.
2. **Nâng cấp nhận diện ô nhập bình luận**:
   - Sử dụng danh sách các bộ chọn rộng hơn: `div[role="textbox"]`, `div[contenteditable="true"]`, và bộ chọn `aria-label` không phân biệt hoa thường (`i` flag: `[aria-label*="bình luận" i]`).
   - Sửa lỗi tương tác: Thêm thao tác **`.click()`** trước khi `.focus()` vào ô bình luận chéo. Điều này cực kỳ quan trọng đối với các trình soạn thảo phong phú (Rich Editor) của React trên Facebook để kích hoạt khung soạn thảo trước khi gõ phím.
3. **Cấu hình mặc định tắt AI**:
   - Thay đổi cài đặt mặc định trên cả Frontend (`app.js`), cơ sở dữ liệu (`database.py`) và Backend (`server.py`) từ phương thức `'AI'` sang `'spintax'` (Mẫu Spintax soạn sẵn). Khi khởi tạo hoặc khi không có cấu hình trước đó, hệ thống sẽ sử dụng phần nhập bình luận thủ công làm mặc định.
4. **Kiểm tra trạng thái Cookie**:
   - Nhật ký hệ thống ghi nhận tài khoản `lolishop` đã bị hết hạn Cookie (`Cookie expired - redirected to login page.`). Cần dán lại Cookie mới cập nhật từ trình duyệt để kích hoạt lại tính năng tương tác tự động.

---

## Tính năng Quản lý & Lưu danh sách mục tiêu (v1.9)

### Nhu cầu sử dụng:
Trước đây, ở tab **Đăng hàng loạt**, mỗi khi tạo một chiến dịch mới, người dùng phải sao chép và dán thủ công toàn bộ các liên kết/ID nhóm/trang vào ô nhập liệu. Việc này rất mất thời gian nếu phải đăng đồng loạt nhiều lần cho cùng một tập hợp mục tiêu.

### Giải pháp nâng cấp:
Chúng tôi đã xây dựng hoàn chỉnh tính năng **Quản lý danh sách mục tiêu (Target Lists)**:
1. **Cơ sở dữ liệu (Database)**:
   - Thêm bảng `target_lists` lưu trữ các danh sách mục tiêu đã được đặt tên.
   - Triển khai các API chẩn đoán và thao tác dữ liệu chuẩn REST tại [server.py](file:///C:/Users/TOSHIBA/.gemini/antigravity/scratch/fb-poster/server.py): `GET /api/target-lists`, `POST /api/target-lists`, và `DELETE /api/target-lists/<id>`.
2. **Giao diện người dùng (Frontend HTML/JS)**:
   - **Tích hợp dropdown chọn nhanh**: Bổ sung hộp chọn *"Áp dụng danh sách mục tiêu đã lưu"* phía trên ô nhập liệu ở tab **Đăng hàng loạt**. Khi chọn, toàn bộ danh sách sẽ tự động điền vào ô mục tiêu.
   - **Lưu trực tiếp từ ô nhập**: Bổ sung nút bấm *"Lưu ô nhập này làm danh sách mới"* ngay dưới ô nhập mục tiêu. Khi click, hệ thống sẽ hỏi tên danh sách và tự động lưu lại vào cơ sở dữ liệu.
   - **Quản lý danh sách**: Bổ sung một Glass-Card mới *"Quản lý danh sách mục tiêu"* ở cột bên trái của tab **Đăng hàng loạt**, hiển thị danh sách các nhóm đã lưu kèm theo số lượng mục tiêu và nút xóa nhanh.

### Hướng dẫn sử dụng:
1. Chuyển sang tab **Đăng hàng loạt**.
2. Nhập các liên kết nhóm hoặc trang của bạn vào ô **Danh sách mục tiêu** (mỗi mục tiêu một dòng).
3. Nhấp vào nút **Lưu ô nhập này làm danh sách mới**, nhập tên gợi nhớ (VD: `Nhóm Thời Trang Cần Thơ`) và nhấn **OK**.
4. Danh sách mới sẽ ngay lập tức xuất hiện ở bảng **Quản lý danh sách mục tiêu** bên dưới và trong dropdown **Áp dụng danh sách mục tiêu đã lưu**.
5. Lần sau, bạn chỉ cần chọn tên danh sách từ dropdown để tự động điền tất cả các liên kết và tạo chiến dịch đăng đồng loạt.

---

## Xuất phần mềm thành bộ cài đặt di động (v2.0)

### Tối ưu hóa tệp khởi chạy:
1. **Lập trình `run.bat` di động**:
   - Thay thế các đường dẫn cứng tuyệt đối bằng ký hiệu thư mục tương đối `%~dp0`. Nhờ đó, người dùng có thể giải nén thư mục phần mềm ở bất kỳ vị trí nào trên máy tính (như Desktop, ổ D, ổ E...) và click đúp là có thể chạy ngay.
   - Thêm tính năng **Tự động cai đặt thư viện (Auto-Dependency Installation)**: Khi khởi chạy lần đầu tiên trên một máy tính mới, `run.bat` sẽ tự động tải các gói thư viện Python cần thiết từ tệp `requirements.txt`.
   - Thêm tính năng **Tự động tải trình duyệt Playwright**: Tự động tải xuống nhân trình duyệt Chromium tương thích mà không cần người dùng phải gõ lệnh thủ công trong Terminal.
2. **Nén đóng gói sẵn sàng tải về**:
   - Toàn bộ mã nguồn, cấu hình giao diện, tệp khởi chạy và cơ sở dữ liệu `database.db` đã được nén đóng gói sạch sẽ (loại bỏ các file cache như `__pycache__` và các file rác) thành tệp **[fb-poster.zip](file:///C:/Users/TOSHIBA/.gemini/antigravity/brain/8eeaa6e1-8a1b-4909-a91b-74d2974efac3/fb-poster.zip)**.

### Hướng dẫn tải về và cài đặt:
1. Click vào liên kết này để tải về: 👉 **[Tải bộ cài fb-poster.zip](file:///C:/Users/TOSHIBA/.gemini/antigravity/brain/8eeaa6e1-8a1b-4909-a91b-74d2974efac3/fb-poster.zip)**.
2. Giải nén thư mục `fb-poster` ra bất kỳ nơi nào trên máy tính của bạn (VD: ngoài Desktop).
3. Nhấp đúp chuột vào tệp **`run.bat`** để khởi chạy phần mềm. Giao diện quản trị trên trình duyệt sẽ tự động mở ra ở địa chỉ `http://localhost:5000` và hệ thống sẽ bắt đầu tự động vận hành trong nền!

---

## Bản nâng cấp Đa luồng Tương tác Song song (v2.1)

### Nhu cầu nâng cấp:
Trước đây, tiến trình tương tác bảng tin nhóm (`autofeed_worker`) duyệt qua từng tài khoản một cách tuần tự (hết tài khoản này mới chuyển sang tài khoản tiếp theo). Điều này làm chậm tốc độ quét đáng kể khi người dùng thêm nhiều tài khoản Facebook vào hệ thống.

### Giải pháp nâng cấp song song:
1. **Lập trình Đa luồng (Multi-threading)**:
   - Tái cấu trúc hàm `autofeed_worker` trong [server.py](file:///C:/Users/TOSHIBA/.gemini/antigravity/scratch/fb-poster/server.py).
   - Khi chu kỳ quét bảng tin bắt đầu, hệ thống sẽ tạo các tiểu trình (`threading.Thread`) chạy song song độc lập cho từng tài khoản hoạt động.
   - Thêm cơ chế **Giãn cách khởi chạy (Staggering)**: Giãn cách 5 giây giữa các lượt bắt đầu luồng để tránh việc khởi động quá nhiều nhân Chromium cùng một phần triệu giây gây quá tải CPU của máy tính.
   - Sử dụng lệnh `t.join()` để đảm bảo toàn bộ tài khoản hoàn thành chu kỳ tương tác của mình trước khi hệ thống bắt đầu đếm ngược thời gian giãn cách tiếp theo.
2. **Cơ chế an toàn Cơ sở dữ liệu (SQLite Thread Safety)**:
   - SQLite mặc định có thể gặp lỗi `database is locked` nếu nhiều luồng ghi dữ liệu cùng lúc.
   - Đã nâng cấp hàm kết nối `get_db_connection()` trong [database.py](file:///C:/Users/TOSHIBA/.gemini/antigravity/scratch/fb-poster/database.py) bổ sung thuộc tính **`timeout=30.0`**. Khi có xung đột ghi, luồng sẽ kiên nhẫn chờ đến khi cơ sở dữ liệu mở khóa thay vì crash tiến trình.

---

## Bản sửa lỗi & Nâng cấp Lọc Thời gian 10 Ngày (v2.2)

### Nhu cầu nâng cấp:
Yêu cầu của người dùng là hệ thống tương tác **chỉ thả tim và bình luận trên các bài viết được đăng trong vòng 10 ngày trở lại**. Phiên bản trước đây có bộ phân tích thời gian tương đối thô sơ, dẫn đến việc nhận diện sai (ví dụ: chữ `h` trong `tháng` bị nhận diện nhầm thành giờ `h` khiến các bài viết cũ nhiều tháng vẫn bị coi là mới và tương tác).

### Giải pháp nâng cấp & Kiểm thử:
1. **Thiết kế lại Bộ phân tích Thời gian (`is_post_recent`)**:
   - Viết lại hàm `is_post_recent()` và `check_absolute_date()` trong [automation.py](file:///C:/Users/TOSHIBA/.gemini/antigravity/scratch/fb-poster/automation.py) với thiết kế an toàn, không sử dụng substring đơn ký tự.
   - Sử dụng các biểu thức chính quy (regular expressions) có giới hạn từ `\b` rõ ràng để khớp chính xác các từ chỉ đơn vị thời gian: `ngày/day/d`, `tuần/week/w`, `giờ/hr/h`, `phút/min/m`, tránh xung đột chéo giữa các định dạng.
   - Hỗ trợ đầy đủ các định dạng ngày tháng lịch tuyệt đối cả tiếng Việt (ví dụ: `18 tháng 6`, `18 thg 6`, `18/6`) và tiếng Anh (ví dụ: `June 18`, `18 Jun`) bằng cách tự động đối chiếu với ngày hiện tại (máy tính).
2. **Kiểm thử Độc lập (Unit Testing)**:
   - Viết tệp kiểm thử tự động [test_date_parser.py](file:///C:/Users/TOSHIBA/.gemini/antigravity/brain/8eeaa6e1-8a1b-4909-a91b-74d2974efac3/scratch/test_date_parser.py) chứa **41 kịch bản kiểm thử** đại diện cho mọi cách viết thời gian trên Facebook (từ thời gian tương đối đến ngày tháng tuyệt đối, viết tắt tiếng Anh/Việt).
   - Kiểm tra và sửa lỗi biên đặc biệt: Tránh nhận diện sai `'9 June 2026'` thành `'June 20'` bằng cách kiểm tra ranh giới số.
   - Chạy kiểm thử thành công: Đạt tỉ lệ **41/41 test case vượt qua (Passed 100%)**.
3. **Áp dụng Bộ lọc 10 ngày cho tất cả các Luồng Tương tác**:
   - Tích hợp bộ lọc thời gian vào **cả 2 luồng tương tác**: Luồng bình luận dạo Bảng tin (`auto_engage_feed_posts`) và Luồng tương tác theo Nhóm/Trang cụ thể (`auto_like_posts`). Cả hai luồng hiện nay đều quét hộp thông tin thời gian của bài viết và bỏ qua ngay nếu bài đăng cũ quá 10 ngày.
4. **Khởi chạy lại máy chủ**:
   - Dừng tiến trình cũ và khởi chạy lại máy chủ Flask server để cập nhật mã nguồn mới vào luồng vận hành thực tế.

---

## Bản nâng cấp v2.3 - Hiện cửa sổ trình duyệt tương tác trực tiếp & Cỗ máy bình luận (Turbo Mode) siêu tốc

### Nhu cầu nâng cấp:
Theo yêu cầu của người dùng, hệ thống cần:
1. Cho phép người dùng theo dõi trực tiếp quá trình tự động bình luận, thả tim bằng cách hiển thị cửa sổ trình duyệt (Headed Mode/Không ẩn trình duyệt).
2. Tối ưu hóa tính năng bình luận thành "cỗ máy bình luận" siêu tốc, loại bỏ độ trễ gõ phím và giảm thiểu tối đa các khoảng thời gian chờ không cần thiết trên toàn bộ hệ thống (gồm cả trả lời bình luận và bình luận bài đăng).

### Các cải tiến đã áp dụng:
1. **Mặc định hiển thị cửa sổ trình duyệt (Headed Mode)**:
   - Cập nhật cấu hình cơ sở dữ liệu mặc định: Thiết lập `'browser_headless': '0'` trong [database.py](file:///C:/Users/TOSHIBA/.gemini/antigravity/scratch/fb-poster/database.py). 
   - Khi chạy, Playwright sẽ tự động mở cửa sổ Chrome/Edge hiển thị trực tiếp các thao tác like/comment dạo cho người dùng xem ("ko cần ẩn bình luận đi").
   - Người dùng có thể chủ động chuyển đổi lại chế độ chạy ẩn (Headless Mode) tại tab **Cấu hình hệ thống**.

2. **Đồng bộ hóa Cỗ máy bình luận (Turbo Mode) siêu tốc**:
   - Nâng cấp đồng bộ cài đặt tốc độ tương tác trên toàn hệ thống trong [automation.py](file:///C:/Users/TOSHIBA/.gemini/antigravity/scratch/fb-poster/automation.py).
   - Ở phiên bản trước, chế độ Turbo Mode chỉ áp dụng cho tự động tương tác bảng tin. Hiện tại, chúng tôi đã tích hợp chế độ này vào **tất cả** các hàm bình luận/phản hồi:
     - **Tự động trả lời bình luận (`auto_reply_post_comments`)**
     - **Bình luận bài viết chỉ định (`post_article_comment`)**
     - **Tự động tương tác bảng tin (`auto_engage_feed_posts`)**
     - **Tự động tương tác nhóm/trang cụ thể (`auto_like_posts`)**
   - Khi chọn **Cỗ máy tương tác (Turbo Mode)**, các thông số được tối ưu như sau:
     - Tốc độ gõ phím bình luận: Giảm từ **60ms/ký tự** xuống còn **5ms/ký tự** (gần như gõ tức thì).
     - Thời gian di chuột và click nút Thích/Phản hồi: Giảm từ **0.8s - 1.5s** xuống còn **0.1s - 0.2s**.
     - Thời gian chờ tải và gửi bình luận sau khi nhấn Enter: Giảm từ **4.0s - 5.0s** xuống còn **1.5s**.

3. **Cập nhật & Đóng gói phiên bản v2.3**:
   - Đóng gói toàn bộ mã nguồn sạch của dự án thành tệp tin nén mới **[fb-poster.zip](file:///C:/Users/TOSHIBA/.gemini/antigravity/brain/8eeaa6e1-8a1b-4909-a91b-74d2974efac3/fb-poster.zip)**.
   - Sao chép tệp nén trực tiếp vào thư mục [static/fb-poster.zip](file:///C:/Users/TOSHIBA/.gemini/antigravity/scratch/fb-poster/static/fb-poster.zip) để người dùng tải trực tiếp qua giao diện web.

---

## Bản nâng cấp v2.5 - Hỗ trợ Thêm hàng loạt Mục tiêu Auto-Like từ Danh sách đã lưu

### Nhu cầu nâng cấp:
Trước đây, ở tab **Auto-Like (Tương tác tự động)**, người dùng chỉ có thể thêm từng link mục tiêu một cách thủ công (nhập từng Tên và từng URL). Điều này rất bất tiện nếu người dùng muốn thêm danh sách hàng chục nhóm/trang Facebook để chạy tương tác.

### Giải pháp nâng cấp:
Chúng tôi đã tích hợp tính năng quản lý danh sách mục tiêu ("tệp mục tiêu") vào tab Auto-Like:
1. **Dropdown áp dụng danh sách mục tiêu**: Bổ sung bộ chọn *“Áp dụng danh sách mục tiêu đã lưu (Tùy chọn)”* ở tab Auto-Like. Khi người dùng chọn danh sách đã lưu (được tạo ở tab Đăng hàng loạt), tất cả các link trong danh sách đó sẽ tự động được điền vào ô nhập liệu.
2. **Hộp nhập liệu đa dòng (Textarea)**: Thay đổi ô nhập link từ dạng dòng đơn (`input url`) sang dạng nhiều dòng (`textarea`). Người dùng có thể tự do copy-paste hàng loạt link nhóm/trang (mỗi dòng một link) để thêm cùng lúc.
3. **Tự động bóc tách tên mục tiêu (Auto-naming)**:
   - Viết lại hàm xử lý API `POST /api/autolike/targets` trong [server.py](file:///C:/Users/TOSHIBA/.gemini/antigravity/scratch/fb-poster/server.py).
   - Backend sẽ tự động tách danh sách liên kết nhập vào theo dòng, tự động làm sạch liên kết.
   - Nếu người dùng thêm hàng loạt link, backend sẽ tự động phân tích đường dẫn (đường dẫn nhóm hoặc trang cá nhân) để trích xuất ra tên gợi nhớ tương ứng (ví dụ: `https://www.facebook.com/groups/123456/` -> `Nhóm 123456`, `https://www.facebook.com/VinhRau.FAP` -> `VinhRau.FAP`).
4. **Cập nhật giao diện Frontend**:
   - Cập nhật [index.html](file:///C:/Users/TOSHIBA/.gemini/antigravity/scratch/fb-poster/static/index.html) và [app.js](file:///C:/Users/TOSHIBA/.gemini/antigravity/scratch/fb-poster/static/app.js) để đồng bộ tải danh sách mục tiêu khi vào tab Auto-Like và xử lý sự kiện điền nhanh link.

---

## Bản nâng cấp v3.0 - Nhận diện bài đăng chờ phê duyệt (Moderation Queue Detection) & Trạng thái "Chờ duyệt"

### Nhu cầu nâng cấp:
Facebook cho phép quản trị viên (admin) của các Nhóm thiết lập chế độ kiểm duyệt bài viết. Khi đăng bài vào các nhóm này, bài viết không được xuất bản công khai ngay lập tức mà bị đưa vào hàng đợi chờ duyệt (Moderation Queue).
Để giúp người dùng quản lý hiệu quả và nhận biết nhóm nào yêu cầu phê duyệt từ quản trị viên nhằm tối ưu hóa danh sách đăng bài, hệ thống cần:
1. Tự động nhận diện xem bài viết sau khi gửi lên có bị đưa vào danh sách chờ duyệt hay không.
2. Cập nhật trạng thái bài viết tương ứng thành "Chờ duyệt" thay vì hiển thị "Đã đăng" hoặc "Thất bại".
3. Hiển thị nhãn cảnh báo màu vàng cam "Chờ duyệt" nổi bật trong giao diện lịch sử bài đăng.

### Giải pháp nâng cấp & Logic hoạt động:
1. **Phát hiện hàng đợi duyệt trong Trình duyệt (`automation.py`)**:
   - Sau khi nhấn nút **Đăng** (Post) và hộp thoại soạn thảo đóng lại, Playwright sẽ đợi 3 giây và trích xuất toàn bộ văn bản của trang (`body` inner text).
   - Tiến hành so khớp với các từ khóa kiểm duyệt phổ biến (cả tiếng Anh và tiếng Việt): `chờ phê duyệt`, `chờ quản trị`, `chờ duyệt`, `pending approval`, `submitted for approval`, `admin approval`, `approval queue`.
   - Nếu phát hiện thấy các từ khóa này, bài đăng sẽ được lưu với trạng thái `pending_approval` kèm mô tả chi tiết: *"Bài viết đã được gửi và đang chờ phê duyệt từ quản trị viên (Nhóm kiểm duyệt bài)."*
   - Nếu không có từ khóa kiểm duyệt nào, bài đăng được ghi nhận là `posted` (Đã đăng thành công).

2. **Cập nhật Backend API & Scheduler (`server.py`)**:
   - Cải tiến luồng lập lịch chạy ngầm (`scheduler_worker`) và endpoint đăng bài ngay lập tức (`/api/posts/<post_id>/publish`).
   - Lưu trữ trực tiếp mã trạng thái thực tế từ hàm tự động hóa trả về (`posted` hoặc `pending_approval`) thay vì gán cứng trạng thái `posted`.

3. **Cập nhật Giao diện người dùng (`static/app.js`)**:
   - Bổ sung định nghĩa hiển thị trạng thái `pending_approval` vào hàm `statusBadge()`:
     - Map key: `pending_approval`
     - Class CSS sử dụng: `badge-pending` (sử dụng tông màu cảnh báo cam/vàng có sẵn trong `style.css`).
     - Nội dung hiển thị: `<i class="fa-solid fa-hourglass-half"></i> Chờ duyệt`.
   - Trạng thái này sẽ xuất hiện đồng bộ trên bảng Dashboard thống kê và Lịch sử bài viết.

4. **Đóng gói dự án**:
   - Chạy script đóng gói tự động `zip_project.py` và đồng bộ hóa bản lưu trữ tại `static/fb-poster.zip` để người dùng dễ dàng nâng cấp.

---

## Bản nâng cấp v3.5 - Cơ chế Gửi Bình luận Đa tầng & Xác thực Bình luận trên Trang

### Nhu cầu nâng cấp:
Facebook áp dụng các bộ lọc chống spam rất mạnh mẽ. Trong nhiều trường hợp:
1. Việc chỉ nhấn nút "Enter" trên ô nhập văn bản có thể không kích hoạt hành động gửi bình luận (ví dụ: do ô nhập mất tiêu điểm focus hoặc giao diện Facebook yêu cầu tương tác click).
2. Bình luận có chứa nội dung quảng cáo, link hoặc spintax trùng lặp có thể bị Facebook ẩn ngay lập tức (không xuất hiện trên bài viết công khai) mà công cụ tự động hóa không hề hay biết.
Người dùng muốn bình luận **phải luôn hiển thị trực tiếp** trên bài viết để tiếp cận người xem khác hiệu quả.

### Các cải tiến đã áp dụng:
1. **Phát triển Hàm Gửi Bình luận Đa tầng (`_type_and_submit_comment`)**:
   - Tích hợp một quy trình gửi bình luận cực kỳ bền bỉ trong `automation.py`.
   - Sau khi nhập xong văn bản bình luận, Playwright sẽ tìm kiếm các nút **Đăng / Post / Send / Gửi** trong phạm vi container của bài viết (tìm kiếm lên tới 4 tầng thẻ cha).
   - Nếu tìm thấy nút gửi (ví dụ: nút có nhãn `Đăng`, biểu tượng SVG máy bay giấy, hoặc `Post comment`), hệ thống sẽ di chuột và thực hiện thao tác **click trực tiếp** vào nút đó.
   - Nếu không tìm thấy nút gửi, hệ thống sẽ tự động hạ cấp xuống phương án nhấn phím **Enter** trên bàn phím để gửi bài.

2. **Cơ chế Xác thực Bình luận Thực tế**:
   - Sau khi gửi bình luận, Playwright sẽ đợi và quét nội dung trang (`body` text) trong vòng tối đa 3 giây để xác minh xem chuỗi bình luận vừa đăng có thực sự hiển thị công khai trên giao diện người dùng hay không.
   - Ghi nhận thông báo xác thực vào nhật ký log hệ thống giúp người dùng dễ dàng theo dõi hiệu quả tương tác thực tế của tài khoản.

3. **Tối ưu hóa Tiến trình đóng gói (`zip_project.py`)**:
   - Loại bỏ các file nén `.zip` tự động ra khỏi bộ lọc nén của dự án để tránh hiện tượng nén đệ quy tệp tin cũ gây nặng bộ nhớ hệ thống.

---

## Bản nâng cấp v4.0 - Hệ thống Thùng rác Bài viết (Trash Bin System)

### Nhu cầu nâng cấp:
Trước đây, khi người dùng xóa bài viết (ở tab Lịch sử & Hẹn giờ), bài viết sẽ bị xóa vĩnh viễn ngay lập tức khỏi cơ sở dữ liệu và các tệp hình ảnh/ảnh chụp đi kèm cũng bị xóa mất. Điều này dễ dẫn đến việc xóa nhầm các bài viết quan trọng hoặc bài viết đã lên lịch công phu.
Người dùng yêu cầu **tích hợp một Thùng rác (Trash Bin)** để lưu tạm các bài đăng đã xóa, cho phép khôi phục hoặc xóa vĩnh viễn khi cần.

### Giải pháp nâng cấp & Logic hoạt động:
1. **Soft-delete (Xóa tạm thời) trong Database (`database.py`)**:
   - Thêm cột `is_deleted INTEGER DEFAULT 0` vào bảng `posts`.
   - Hàm `delete_post(post_id)` thay vì chạy truy vấn `DELETE` thì chuyển sang chạy truy vấn `UPDATE posts SET is_deleted=1, updated_at=?` để đánh dấu bài viết đã xóa.
   - Cập nhật các hàm truy vấn danh sách bài viết đang hoạt động (`get_posts`, `get_posts_by_status`, và thống kê analytics `get_analytics`) để loại trừ các bài viết đã bị đánh dấu xóa (`WHERE is_deleted = 0`).
   - Thêm các hàm nghiệp vụ mới: `get_deleted_posts()` (lấy danh sách bài viết trong thùng rác), `restore_post(post_id)` (khôi phục bài đăng về trạng thái hoạt động) và `delete_post_permanently(post_id)` (xóa thực sự khỏi database).

2. **Cung cấp API mới (`server.py`)**:
   - `DELETE /api/posts/<post_id>`: Chỉ soft-delete (xóa tạm thời) bài viết, không xóa tệp tin đính kèm.
   - `GET /api/posts/deleted`: Trả về danh sách bài viết đang nằm trong thùng rác.
   - `POST /api/posts/<post_id>/restore`: Khôi phục lại bài viết về danh sách chính.
   - `DELETE /api/posts/<post_id>/permanent`: Thực hiện xóa vĩnh viễn bài viết khỏi cơ sở dữ liệu và **xóa các tệp ảnh/media/screenshot đính kèm vật lý** trên ổ cứng để giải phóng bộ nhớ.

3. **Cập nhật Giao diện người dùng (`static/index.html` và `static/app.js`)**:
   - **Giao diện sidebar**: Bổ sung tab **Thùng rác** với biểu tượng thùng rác để quản lý tập trung.
   - **Bảng quản lý Thùng rác**: Hiển thị danh sách các bài viết đã xóa, thời gian xóa (dựa vào cột `updated_at`), tài khoản và nội dung.
   - **Hai nút tương tác**:
     - *Nút Khôi phục (Màu xanh)*: Click để khôi phục bài viết về Lịch sử & Hẹn giờ.
     - *Nút Xóa vĩnh viễn (Màu đỏ)*: Click để xóa hoàn toàn bài viết và giải phóng ổ cứng (có cảnh báo xác nhận trước khi thực hiện).
   - Tích hợp đồng bộ hóa và refresh tự động danh sách thùng rác mỗi khi chuyển tab hoặc định kỳ.

---

## Bản nâng cấp v4.5 - Quản lý Chọn và Xóa/Khôi phục Hàng loạt (Bulk Actions Support)

### Nhu cầu nâng cấp:
Khi số lượng bài viết tăng lên đến hàng chục, hàng trăm bài đăng, việc nhấp chuột xóa từng bài đăng một cách thủ công ở danh sách Lịch sử hoặc Thùng rác cực kỳ tốn thời gian.
Người dùng yêu cầu **tích hợp tính năng chọn nhiều (checkboxes) và thực hiện các hành động hàng loạt (Bulk Actions)**: Xóa hàng loạt, Khôi phục hàng loạt và Xóa vĩnh viễn hàng loạt.

### Các cải tiến đã áp dụng:
1. **API Xử lý hàng loạt hiệu năng cao (`server.py`)**:
   - Bổ sung 3 định tuyến API chấp nhận danh sách ID bài viết dưới dạng JSON `{"ids": [...]}` để xử lý đồng thời trong một vòng lặp tối ưu:
     - `POST /api/posts/bulk-delete`: Di chuyển hàng loạt bài viết vào thùng rác.
     - `POST /api/posts/bulk-restore`: Khôi phục hàng loạt bài viết về danh sách hoạt động.
     - `POST /api/posts/bulk-permanent`: Quét và xóa hoàn toàn hàng loạt bài viết khỏi cơ sở dữ liệu cùng toàn bộ tệp đính kèm vật lý tương ứng.

2. **Cập nhật Giao diện Bảng chọn (`static/index.html`)**:
   - Thêm cột Checkbox chọn ở đầu mỗi hàng của cả 2 bảng: bảng **Lịch sử bài đăng** và bảng **Thùng rác**.
   - Bổ sung Checkbox tổng (`select-all`) trên tiêu đề cột (`thead`) giúp bật/tắt chọn tất cả bài đăng trên trang chỉ với 1 click.
   - Thêm hai thanh điều khiển tác vụ hàng loạt (`bulk-actions-panel`) có khả năng hiển thị động khi người dùng bắt đầu tích chọn ít nhất 1 bài viết.

3. **Lập trình logic tương tác thông minh (`static/app.js`)**:
   - Viết các hàm lắng nghe sự thay đổi trạng thái của các ô checkbox (`onPostItemCheckboxChange`, `onTrashItemCheckboxChange`).
   - Tự động đếm và cập nhật số lượng dòng đã chọn: *"Đã chọn N bài viết"*.
   - Triển khai các hàm điều phối API hàng loạt (`bulkDeletePosts`, `bulkRestoreTrash`, `bulkDeletePermanentTrash`) có xác nhận cảnh báo an toàn từ trình duyệt trước khi gửi yêu cầu lên máy chủ.
   - Tự động tắt bảng điều khiển hàng loạt và bỏ tích chọn sau khi thực thi tác vụ thành công để tránh lỗi thao tác lặp lại.

## Bản nâng cấp v5.0 - Ảnh Clickable & Trình Soạn Bài Tiếp Thị Shopee Affiliate Tự Động
### Nhu cầu nâng cấp:
Facebook không hỗ trợ đính kèm hình ảnh tùy chỉnh khi đăng bài dạng Liên Kết (Link Card). Người dùng muốn đăng một bài đăng trên Facebook chứa ảnh đẹp đại diện cho sản phẩm, và khi người đọc nhấp vào hình ảnh đó, trình duyệt sẽ tự động chuyển hướng họ tới link tiếp thị Shopee Affiliate của người dùng. Đồng thời, người dùng muốn quy trình này phải hoàn toàn tự động: khi họ dán một liên kết Shopee vào ô trợ lý AI, hệ thống sẽ tự động cào dữ liệu sản phẩm, tải ảnh sản phẩm, viết bài quảng cáo, và tự động điền đầy đủ các thông tin của ảnh clickable chuyển hướng.

### Các cải tiến đã áp dụng:
1. **Trang chuyển hướng động với Meta Tags Open Graph (`server.py`)**:
   - Thêm định tuyến `GET /r/<redirect_id>` phục vụ cho Facebook Scraper/Crawler. Khi Facebook quét link này, hệ thống sẽ trả về mã HTML động có chứa các thẻ meta Open Graph (`og:image`, `og:title`, `og:description`) trỏ tới ảnh sản phẩm tùy chỉnh và tiêu đề/mô tả của sản phẩm.
   - Khi người dùng thực tế nhấp vào liên kết này, hệ thống sẽ tự động chuyển hướng (Redirect 302 và JavaScript fallback) đưa họ đến liên kết Shopee Affiliate thực tế.

2. **Tải ảnh Shopee tự động (`server.py`)**:
   - Khi cào liên kết Shopee trong API soạn bài, hệ thống sẽ tự động tải hình ảnh sản phẩm (`og:image`) về máy chủ và lưu trữ dưới dạng tệp tin cục bộ trong thư mục `uploads/` để làm ảnh clickable.

3. **Tích hợp Tự Động Hóa UI Trợ Lý AI (`static/app.js`)**:
   - Cải tiến hàm `generateAIText()`: Khi nhận được kết quả soạn bài từ Gemini AI chứa ảnh sản phẩm Shopee và tiêu đề sản phẩm, giao diện sẽ:
     - Tự động kích hoạt tính năng đăng ảnh chuyển hướng (`#post-redirect-toggle`).
     - Tự động điền URL Shopee vào ô link chuyển hướng.
     - Điền tiêu đề và mô tả kêu gọi hành động gợi ý.
     - Đưa ảnh Shopee đã tải về vào khay phương tiện xem trước (`media-preview-container`) và cập nhật số lượng tệp.
   - Cải tiến logic validate trong `handleCreatePost()`: Chấp nhận tổng số lượng hình ảnh (tải lên từ ổ cứng + ảnh tải về từ AI Shopee) bằng 1 để thỏa mãn yêu cầu tạo bài đăng chuyển hướng ảnh clickable.

---

## Bản nâng cấp v5.5 - Tự động tham gia nhóm & Trả lời câu hỏi bằng Gemini AI (Giai đoạn 14)
### Nhu cầu nâng cấp:
Việc tham gia các nhóm Facebook theo cách thủ công tốn nhiều thời gian và công sức, đặc biệt khi các nhóm yêu cầu trả lời câu hỏi xét duyệt của quản trị viên. Người dùng muốn có một công cụ tự động hóa toàn bộ quy trình này.

### Các cải tiến đã áp dụng:
1. **Lưu trữ nhật ký tham gia (`database.py`)**:
   - Thêm bảng `autojoin_logs` lưu thông tin tài khoản, nhóm mục tiêu, trạng thái và chi tiết.
2. **Tự động trả lời câu hỏi bằng Gemini AI (`automation.py`)**:
   - Khi Playwright click nút "Tham gia nhóm" và phát hiện dialog câu hỏi xét duyệt, hệ thống sẽ tự động điền các checkbox nội quy.
   - Sử dụng Gemini AI để phân tích câu hỏi trong dialog và đưa ra câu trả lời ngắn gọn (dưới 15 từ, tiếng Việt) để gửi duyệt tự động.
3. **Tiến trình chạy ngầm & Quản lý logs (`server.py`, `static/app.js`)**:
   - Thêm tab "Tự động tham gia nhóm" trên UI.
   - Thêm API endpoints để chạy tác vụ ngầm và quản lý danh sách nhật ký trên giao diện dashboard.

---

## Bản nâng cấp v6.0 - Quét Nhóm Công Khai & Auto Shopee Poster từ thư mục (Giai đoạn 15)
### Nhu cầu nâng cấp:
1. Người dùng muốn tự động quét và phân loại các nhóm Facebook mà tài khoản của họ đã tham gia để chỉ chọn ra các **nhóm công khai (public groups)** để đăng bài quảng cáo, tăng tỷ lệ bài đăng được duyệt ngay.
2. Người dùng muốn có một thư mục (folder) trên máy tính để dán các link Shopee sản phẩm. Hệ thống sẽ tự động lấy các link này, cào thông tin, sinh bài viết marketing và đăng bài tự động mà không cần điền form thủ công trên web.

### Các cải tiến đã áp dụng:
1. **Đồng bộ & Phân loại Nhóm Công Khai (`automation.py`, `server.py`)**:
   - Viết hàm `scrape_and_save_public_groups` điều hướng đến trang quản lý nhóm, thu thập các liên kết nhóm của tài khoản, truy cập từng nhóm để phân tích xem có phải là nhóm công khai hay không.
   - Lưu hoặc cập nhật danh sách các nhóm công khai tìm thấy vào bảng `target_lists` dưới tên `"Nhóm công khai - <Tên tài khoản>"`.
   - Bổ sung nút **"Quét & Đồng bộ Nhóm Công Khai"** trên giao diện tab Auto-Join của dashboard.

2. **Giám sát Thư mục Đăng bài Shopee Tự động (`server.py`)**:
   - Tạo thư mục `shopee_links` và thư mục con `processed` trong project.
   - Triển khai tiến trình chạy ngầm `shopee_folder_worker` quét thư mục `shopee_links/` mỗi 5 phút một lần để tìm các tệp tin văn bản `.txt`.
   - Với mỗi liên kết Shopee tìm thấy trong file:
     - Tự động cào dữ liệu tiêu đề, mô tả và hình ảnh sản phẩm.
     - Dùng Gemini AI sinh bài viết bán hàng thu hút.
     - Hỗ trợ cả định dạng **Ảnh Clickable (Chuyển hướng)** bằng cách tự động tải ảnh về máy, tạo bản ghi chuyển hướng trong bảng `redirects` thông qua tên miền công khai.
     - Tạo bản ghi bài viết ở trạng thái `pending` trong bảng `posts`, tự động tính toán giãn cách thời gian đặt lịch (mặc định 15 phút) để Scheduler tự động đăng bài theo hàng đợi.
     - Di chuyển tệp tin đã xử lý vào thư mục `processed/` để quản lý.

3. **Cấu hình Trực quan trên Dashboard (`static/index.html`, `static/app.js`)**:
   - Bổ sung khối cấu hình trong tab Cấu hình hệ thống để tùy chỉnh: tài khoản đăng bài Shopee mặc định, nơi đăng mặc định, ID mục tiêu mặc định, định dạng đăng bài và giãn cách đặt lịch.

## Bản nâng cấp v6.5 - Tự động tham gia nhóm khi lựa chọn mục tiêu (Giai đoạn 16)
### Nhu cầu nâng cấp:
1. Khi người dùng lên lịch bài đăng đơn lẻ, đăng bài hàng loạt hoặc import các link sản phẩm Shopee, họ thường chọn mục tiêu là một danh sách nhóm Facebook (hoặc các nhóm đơn lẻ).
2. Nếu tài khoản Facebook được chọn chưa tham gia (chưa là thành viên) của các nhóm mục tiêu này, bài đăng sẽ thất bại. Người dùng muốn hệ thống tự động nhận diện và gửi yêu cầu tham gia các nhóm này ngay khi họ thiết lập mục tiêu mà không cần phải thực hiện thủ công.

### Các cải tiến đã áp dụng:
1. **Bộ kích hoạt tự động tham gia ngầm (`server.py`)**:
   - Viết hàm `trigger_autojoin_for_targets(account_id, targets_input)` để phân tích mục tiêu đăng bài (ID nhóm, danh sách mục tiêu).
   - Tự động lọc ra tất cả các nhóm mục tiêu dạng `group` mà tài khoản được chọn cần đăng bài.
   - Khởi chạy một luồng chạy ngầm gọi hàm `auto_join_facebook_groups` để duyệt qua danh sách các nhóm đó.
   - Nếu tài khoản chưa gia nhập, Playwright sẽ tự động nhấn nút tham gia, tích chọn các quy định, gọi Gemini AI trả lời các câu hỏi xét duyệt của nhóm và lưu nhật ký.
2. **Tích hợp toàn diện vào các điểm chạm mục tiêu**:
   - **Tạo/Lưu bài viết đơn lẻ (`/api/posts`)**: Tự động kích hoạt khi người dùng lên lịch đăng bài cho một mục tiêu nhóm hoặc danh sách mục tiêu.
   - **Tạo chiến dịch hàng loạt (`/api/bulk`)**: Tự động kích hoạt cho tất cả các nhóm đích trong chiến dịch.
   - **Giám sát Shopee Folder & Shopee UI Import**: Tự động kích hoạt cho tài khoản và mục tiêu đăng Shopee mặc định ngay sau khi hoàn tất xếp lịch các bài đăng Shopee.
   - **Lưu cấu hình hệ thống (`/api/settings`)**: Tự động kích hoạt cho cấu hình Shopee mặc định khi người dùng thay đổi tài khoản hoặc nhóm đăng bài Shopee mặc định.

---

## Bản nâng cấp v7.0 - Chiến dịch tham gia nhóm theo chủ đề & Lập danh sách mục tiêu (Giai đoạn 17)

### Nhu cầu nâng cấp:
1. Người dùng muốn có khả năng nhập các từ khóa hoặc chủ đề khác nhau để tự động tìm kiếm, lọc, và tham gia các nhóm Facebook theo chủ đề đó.
2. Hệ thống cần lập danh sách mục tiêu (Target Lists) chứa 50 nhóm tốt nhất cho mỗi chủ đề để có thể dễ dàng chọn và đăng bài hàng loạt sau này.
3. Cần ưu tiên các nhóm đăng bài tự do (không bị kiểm duyệt gắt gao hoặc có lượng hoạt động cao) và có nhiều thành viên tham gia nhất.

### Các cải tiến đã áp dụng:
1. **Quét thông tin & Ưu tiên đăng bài tự do (`automation.py`)**:
   - Sử dụng **Tần suất bài đăng (posts per day)** trích xuất trực tiếp từ thẻ nhóm kết quả tìm kiếm làm thước đo gián tiếp cho khả năng cho phép đăng bài tự do (nhóm có hoạt động đăng bài sôi nổi, nhiều bài đăng mới/ngày).
   - Tích hợp hàm **`parse_member_count_str`** thông minh để chuẩn hóa việc đếm và quy đổi số lượng thành viên (hỗ trợ cả dấu chấm, phẩy, chữ K, M, triệu, nghìn của định dạng tiếng Anh lẫn tiếng Việt).
   - Sắp xếp danh sách nhóm theo thứ tự ưu tiên: `Nhóm công khai (Public) -> Tần suất bài viết giảm dần -> Số lượng thành viên giảm dần`.

2. **Cuộn trang động & Lưu danh sách mục tiêu (`automation.py`)**:
   - Tự động tính toán số lần cuộn trang (`scroll_count`) dựa vào số lượng nhóm đích yêu cầu (mục tiêu 50 nhóm sẽ tự động cuộn trang từ 15-25 lần để đảm bảo thu được lượng nhóm phong phú và lọc ra các nhóm chất lượng nhất).
   - Sau khi kết thúc quá trình tham gia nhóm thành công, hệ thống tự động tạo một danh sách mục tiêu mới đặt tên: `Chủ đề: <Chủ đề> - <Tên tài khoản>` để người dùng sử dụng trực tiếp trong giao diện đăng bài hàng loạt.

3. **Giao diện & Cấu hình API đồng bộ (`server.py`, `static/app.js`, `static/index.html`)**:
   - Bổ sung cụm điều khiển **"Chiến dịch tham gia theo chủ đề"** trong tab Tự động tham gia nhóm với các trường cấu hình: chọn tài khoản, nhập nhiều chủ đề (mỗi dòng một chủ đề), đặt số lượng nhóm tối đa, đặt giãn cách, và checkbox cấu hình ưu tiên nhóm công khai & đông thành viên.
   - Đồng bộ hóa checkbox ưu tiên (`prioritize`) từ UI thông qua API POST `/api/autojoin/topic-campaign` xuống worker chạy ngầm của máy chủ.

---

## Bản nâng cấp v7.5 - Tự động bình luận link sản phẩm dưới bài đăng (Giai đoạn 18)

### Nhu cầu nâng cấp:
1. Facebook thường bóp tương tác (giảm reach) rất nặng các bài viết chứa liên kết ngoài ở phần nội dung chính. Người dùng muốn đăng bài quảng cáo (text + hình ảnh) thông thường, sau đó hệ thống sẽ tự động đăng bình luận chứa link tiếp thị (link sản phẩm Shopee Affiliate) ở phần bình luận đầu tiên dưới bài viết đó.
2. Cần cung cấp khả năng nhập nội dung bình luận tùy chỉnh cho từng bài viết đơn lẻ từ giao diện soạn thảo.
3. Cần tích hợp cài đặt tự động bình luận link Shopee cho các bài đăng import hàng loạt từ thư mục giám sát và UI bulk import.

### Các cải tiến đã áp dụng:
1. **Lưu trữ & Di chuyển cấu trúc dữ liệu (`database.py`)**:
   - Chạy migration tự động bổ sung trường `first_comment TEXT` vào bảng `posts`.
   - Bổ sung cấu hình mặc định: `shopee_auto_comment_link` và `shopee_comment_template` để tự động hóa mẫu bình luận Shopee.

2. **Cơ chế bình luận tức thời không tải lại trang (`automation.py`)**:
   - Viết hàm `_comment_on_first_post(page, comment_text)` thực thi trực tiếp trong phiên trình duyệt Playwright đang đăng bài.
   - Thay vì tắt trình duyệt và mở lại theo link bài viết, hệ thống sẽ chờ bài đăng xuất hiện trên bảng tin hiện tại, tự động click nút "Bình luận" (Comment) trên thẻ bài đăng trên cùng, nhập nội dung bình luận và gửi đi. Điều này tăng tốc độ thực thi lên gấp nhiều lần và giảm tỷ lệ bị bot Facebook chặn.
   - Cập nhật hàm `publish_post` để hỗ trợ tham số và kích hoạt tự động bình luận ngay khi bài đăng được tải lên thành công.

3. **Cấu hình & Tự động hóa tiến trình Shopee (`server.py`, `static/app.js`, `static/index.html`)**:
   - Thêm ô nhập "Bình luận đầu tiên" trên form soạn thảo bài viết đơn lẻ.
   - Thêm cụm cấu hình **"Tự động bình luận link Shopee"** và **"Mẫu bình luận"** vào tab Cấu hình hệ thống để tùy chỉnh tự động hóa tiếp thị liên kết Shopee.
   - Tối ưu hóa `shopee_folder_worker` và `api_shopee_bulk_import`: Nếu kích hoạt tự động bình luận Shopee và định dạng đăng bài là bình thường (normal), link Shopee sẽ được lọc bỏ khỏi nội dung chính để tránh bóp reach và chỉ đẩy xuống bình luận đầu tiên. Nếu định dạng là Clickable, link vẫn được giữ ở nội dung chính và gửi bình luận song song.


---

## Bản nâng cấp v8.0 - Tự động lập và hiển thị danh sách mục tiêu khi tham gia nhóm (Giai đoạn 19)

### Nhu cầu nâng cấp:
1. Khi người dùng chạy tính năng tự động tham gia nhóm (bằng cách nhập danh sách URL/ID hoặc nhập từ khóa tìm kiếm), hệ thống chưa có cơ chế lưu lại danh sách các nhóm đã xử lý (đã tham gia thành công, đã là thành viên, hoặc đang chờ phê duyệt) thành một danh sách mục tiêu để sử dụng lại.
2. Khi các chiến dịch quét hoặc tự động tham gia nhóm chạy ngầm hoàn tất và lưu danh sách mục tiêu vào cơ sở dữ liệu, danh sách này không hiển thị trên giao diện người dùng nếu họ đang ở tab Soạn bài viết mới hoặc Tự động tham gia, do giao diện không tự động tải lại và nạp dữ liệu.

### Các cải tiến đã áp dụng:
1. **Lập danh sách mục tiêu tự động cho luồng tham gia thường & Quét chủ đề (`automation.py`)**:
   - Thay đổi thời điểm lưu danh sách mục tiêu: Hệ thống sẽ lập và lưu danh sách mục tiêu vào cơ sở dữ liệu **ngay lập tức** sau khi quét xong các nhóm ứng viên (trước khi bắt đầu vòng lặp tham gia).
   - Danh sách mục tiêu được lập sẽ chứa **tất cả các nhóm được tìm thấy** theo chủ đề hoặc từ khóa, đảm bảo 100% các nhóm quét được sẽ xuất hiện đầy đủ trong phần "Đăng hàng loạt" (Bulk posting).
   - Khắc phục hoàn toàn lỗi mất nhóm: Các nhóm sẽ không bị loại bỏ khỏi danh sách mục tiêu nếu luồng tham gia gặp lỗi ngẫu nhiên (ví dụ: lỗi mạng, timeout, hoặc không gửi được câu hỏi xét duyệt).
   - Đặt tên danh sách mục tiêu nhất quán:
     - Luồng chiến dịch theo chủ đề: `Chủ đề: {topic} - {account_name}` (list_id dạng `list_topic_<hash>`).
     - Luồng tham gia theo từ khóa: `Từ khóa: {keyword} - {account_name}` (list_id dạng `list_kw_<hash>`).
     - Luồng tham gia theo danh sách URL: `Tự động tham gia - {account_name}` (list_id dạng `list_aj_<hash>`).
2. **Cập nhật dữ liệu tức thời và nạp ban đầu trên UI (`static/app.js`)**:
   - Bổ sung `fetchTargetLists()` vào luồng khởi tạo trang `loadAll()` để đảm bảo nạp sẵn danh sách mục tiêu cho tất cả các dropdown ngay khi mở ứng dụng.
   - Gọi `fetchTargetLists()` khi người dùng chuyển sang các tab `create-post` (Soạn bài viết mới) và `autojoin` (Tự động tham gia nhóm) để cập nhật ngay lập tức các thay đổi.
   - Nâng cấp hàm `refreshDynamic()` chạy ngầm mỗi 6 giây: nếu tab hiện tại là `create-post`, `autojoin`, `bulk`, hoặc `autolike`, hệ thống tự động gọi `fetchTargetLists()` để đồng bộ hóa danh sách mục tiêu mới từ database mà không cần người dùng phải bấm tải lại trang thủ công.

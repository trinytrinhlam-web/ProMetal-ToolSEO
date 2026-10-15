# Yêu cầu phần mềm ProMetal-ToolSEO

Cập nhật: 07/10/2026 (thu gọn theo phạm vi mới)
Dùng làm đầu vào để xây dựng bằng Claude Code trong repo `trinytrinhlam-web/ProMetal-ToolSEO`.

---

## 1. Phạm vi

**Phần mềm làm 4 việc:**
1. Viết bài
2. Đăng bài lên website (WordPress)
3. Tối ưu onpage: bài mới và bài đang có
4. Internal link

**Phần mềm không làm:** lên kế hoạch, nghiên cứu từ khóa, chọn chủ đề, lập lịch biên tập, theo dõi thứ hạng, báo cáo, Google Business Profile. Các việc này do kế hoạch SEO đảm nhận. Phần mềm nhận đầu vào là **phiếu giao bài** đã được duyệt.

Ký hiệu ưu tiên: **GĐ1** = phải có để bắt đầu viết · **GĐ2** = bổ sung sau khi GĐ1 chạy ổn

---

## 2. Nguyên tắc bắt buộc (chặn bằng code)

| # | Nguyên tắc | Lỗi mà nó ngăn |
|---|---|---|
| N1 | Chỉ viết theo phiếu giao bài, không tự chọn chủ đề | Viết lan man, lệch kế hoạch |
| N2 | Mọi bài lưu **nháp**. Chỉ đăng khi người dùng bấm duyệt | Đăng bài lỗi |
| N3 | Mọi con số, khẳng định về doanh nghiệp chỉ lấy từ file thông tin đã điền | “8 năm”, “1000+ khách” tự đặt |
| N4 | Địa chỉ chi nhánh chỉ lấy từ file thông tin; địa danh phải có trong danh sách hành chính | Long Biên, Cái Răng… |
| N5 | Không đăng bài có tiêu đề hoặc nội dung trùng với bài đang có trên site | Hai trang cùng nhắm một từ khóa |

---

## 3. Đầu vào

### 3.1. Phiếu giao bài (từ kế hoạch)
Mỗi phiếu là một dòng trong file Excel hoặc một file YAML. Thiếu trường bắt buộc thì phần mềm không cho bắt đầu viết.

| Trường | Bắt buộc | Ghi chú |
|---|---|---|
| Mã bài | Có | Ví dụ `B-024` |
| Loại trang | Có | Dịch vụ / Khu vực / Hướng dẫn / Công trình thực tế / Cập nhật bài cũ |
| Từ khóa chính | Có | |
| Từ khóa phụ, ý cần có | Không | |
| Tiêu đề dự kiến | Có | |
| Slug | Có | Không dấu, theo kiểu URL đang có (`/sua-cua-keo-tphcm/`) |
| Trang dịch vụ đích | Có (trừ trang dịch vụ) | Link bắt buộc trong bài |
| Link bắt buộc khác | Không | |
| Khu vực | Có nếu là trang khu vực | Lấy từ sheet “Khu vực” |
| Ghi chú của thợ | Có với bài hướng dẫn, công trình | Nguyên nhân hay gặp, mẹo, lỗi khách hay mắc |
| Thư mục ảnh | Không | USB, thư mục máy hoặc Google Drive |
| Ngày giờ đăng | Không | Giờ Việt Nam |
| URL bài cũ | Có nếu là “Cập nhật bài cũ” | |

### 3.2. File thông tin doanh nghiệp
`thong_tin_can_dien.xlsx`, gồm sheet Thông tin chung, Dịch vụ & giá, Khu vực. Phần mềm nhập trực tiếp file này:
- Chỉ dùng ô đã điền; ô trống thì nội dung liên quan bị bỏ, không được tự bịa.
- Không đổi tên cột; dòng “VD” được bỏ qua.
- Đổi dữ liệu (hotline, giá, địa chỉ) → phần mềm liệt kê các bài đang dùng dữ liệu cũ để cập nhật.

### 3.3. Danh sách đơn vị hành chính
Phần mềm kèm sẵn danh sách 168 phường/xã/đặc khu của TP.HCM theo Nghị quyết 1685/NQ-UBTVQH15 (hiệu lực 01/7/2025), cùng tên quận/huyện cũ, dùng để kiểm tra địa danh.

---

## 4. Yêu cầu chức năng

### M0. Nền tảng — GĐ1
| Mã | Yêu cầu | Đạt khi |
|---|---|---|
| YC-001 | Chạy trên Windows 10/11 và macOS, Python 3.11+, khởi động bằng một lệnh, giao diện tiếng Việt chạy trên trình duyệt ở localhost | Cài trên máy thứ hai trong dưới 15 phút theo README |
| YC-002 | Đăng nhập bằng mật khẩu (băm argon2 hoặc bcrypt), tự khóa khi không dùng | Không lưu mật khẩu dạng chữ thường |
| YC-003 | Khóa API, Application Password lưu trong keyring hệ điều hành hoặc `.env` nằm trong `.gitignore` | Quét repo không thấy khóa nào |
| YC-004 | Bài viết, phiếu giao bài, cấu hình lưu dạng file văn bản trong repo để đồng bộ 2 máy qua Git; ảnh gốc để ngoài Git | Mở trên máy kia thấy đủ bài |
| YC-005 | Khi mở ứng dụng, cảnh báo nếu repo chưa kéo bản mới từ GitHub | Có cảnh báo khi máy kia vừa đẩy thay đổi |
| YC-006 | Nhật ký mọi thao tác ghi lên WordPress, lưu bản trước khi sửa để hoàn tác | Hoàn tác được một lần cập nhật bài |

### M1. Nhập dữ liệu — GĐ1
| Mã | Yêu cầu |
|---|---|
| YC-101 | Nhập phiếu giao bài từ Excel/YAML, báo trường thiếu |
| YC-102 | Nhập file thông tin doanh nghiệp, báo ô bắt buộc còn trống theo từng khu vực, dịch vụ |
| YC-103 | Kéo danh sách bài/trang đang có trên site (WordPress REST API) làm kho kiểm tra trùng và nguồn internal link |

### M2. Viết bài — GĐ1
| Mã | Yêu cầu |
|---|---|
| YC-201 | Mẫu theo loại trang (dịch vụ, khu vực, hướng dẫn, công trình thực tế), có mục bắt buộc và mục tùy chọn, **không cố định số từ** |
| YC-202 | Đổi được nhà cung cấp AI (Claude, GPT, Gemini…) qua một lớp chung; ghi chi phí từng bài; đặt trần ngân sách tháng |
| YC-203 | Câu lệnh gửi AI chỉ chứa dữ liệu từ phiếu giao bài và file thông tin; yêu cầu AI không thêm số liệu ngoài dữ liệu được cấp |
| YC-204 | Văn phong tiếng Việt tự nhiên, có dấu đầy đủ, xưng hô thống nhất, không văn mẫu quảng cáo, không ép chèn từ khóa |
| YC-205 | Bài hướng dẫn, công trình phải dùng ghi chú của thợ làm phần cốt lõi |
| YC-206 | Phần hỏi đáp lấy từ câu khách hay hỏi (sheet Khu vực, ghi chú thợ) |
| YC-207 | **Trang khu vực**: dùng địa chỉ chi nhánh, loại địa điểm, thời gian có mặt, công trình tiêu biểu, ảnh của đúng khu vực đó. Thiếu địa chỉ hoặc chưa có công trình nào → không cho tạo. Độ giống giữa hai trang khu vực vượt ngưỡng → chặn |
| YC-208 | Viết lại từng đoạn theo yêu cầu, không phải viết lại cả bài |
| YC-209 | Nhập ghi chú thợ bằng giọng nói (GĐ2) |

### M3. Ảnh — GĐ1
| Mã | Yêu cầu |
|---|---|
| YC-301 | Nhập ảnh từ USB/thư mục máy và Google Drive (API) |
| YC-302 | Gắn thẻ: hạng mục, khu vực, trước/sau, mã công trình |
| YC-303 | Tự xoay đúng chiều, thu kích thước (ví dụ cạnh dài 1600px), nén WebP, đặt tên file không dấu theo nội dung |
| YC-304 | **Xóa tọa độ GPS và thông tin máy trong EXIF** (bảo vệ địa chỉ nhà khách) |
| YC-305 | AI gợi ý alt mô tả đúng ảnh, người dùng duyệt |
| YC-306 | Ảnh do AI tạo chỉ dùng minh họa, có đánh dấu, không được gắn thẻ công trình thật |
| YC-307 | Cảnh báo ảnh đã dùng ở bài khác (GĐ2) |
| YC-308 | Làm mờ số nhà, biển số xe, mặt người (GĐ2) |

### M4. Tối ưu onpage bài mới — GĐ1
| Mã | Yêu cầu |
|---|---|
| YC-401 | Title (hiển thị khoảng 60 ký tự), meta description (khoảng 150 ký tự), slug, một H1, cấu trúc H2/H3 |
| YC-402 | Kiểm tra title, meta description không trùng với bài khác trên site |
| YC-403 | Schema JSON-LD theo loại trang (bảng dưới); kiểm tra hợp lệ trước khi đăng |
| YC-404 | Tránh hai nguồn schema chồng nhau (plugin SEO và phần mềm): chọn một nguồn, tắt nguồn kia cho loại schema tương ứng |
| YC-405 | Canonical, thẻ robots đúng |
| YC-406 | Ảnh có alt, kích thước hợp lý, ảnh đầu bài làm ảnh đại diện |

| Loại trang | Schema |
|---|---|
| Trang chủ | Organization + LocalBusiness (trụ sở) |
| Trang liên hệ | LocalBusiness cho từng địa chỉ đã điền |
| Trang khu vực | LocalBusiness với **địa chỉ chi nhánh của khu vực đó** (cùng tên thương hiệu, hotline) + Service có `areaServed` + BreadcrumbList |
| Trang dịch vụ | Service + BreadcrumbList |
| Bài hướng dẫn, công trình | Article (có tác giả) + BreadcrumbList; FAQPage tùy chọn |
| Không dùng | HowTo (Google bỏ hiển thị từ 9/2023). FAQ không còn hiển thị nổi bật từ 07/5/2026, chỉ giữ nếu có ích |

### M5. Rà soát onpage bài đang có
| Mã | Yêu cầu | Ưu tiên |
|---|---|---|
| YC-501 | Quét toàn bộ trang/bài đang có (hiện 29 URL), lập báo cáo lỗi từng URL: title thiếu, quá dài hoặc trùng; thiếu meta description; nhiều H1; ảnh thiếu alt hoặc quá nặng; thiếu schema; link hỏng; nội dung quá mỏng; hotline/địa chỉ sai so với file thông tin | GĐ1 |
| YC-502 | Đề xuất sửa cho từng lỗi, người dùng duyệt từng mục rồi phần mềm cập nhật lên WordPress, giữ nguyên URL | GĐ2 |
| YC-503 | Khi phiếu giao bài yêu cầu gộp hai bài: chuyển nội dung sang bài giữ lại, tạo chuyển hướng 301 cho bài bỏ, sửa các link nội bộ đang trỏ tới bài bỏ | GĐ2 |

### M6. Internal link
| Mã | Yêu cầu | Ưu tiên |
|---|---|---|
| YC-601 | Chèn link bắt buộc theo phiếu giao bài (trang dịch vụ đích + link khác) | GĐ1 |
| YC-602 | Quy tắc mặc định theo loại trang: bài hướng dẫn → trang dịch vụ đích + 2–3 bài cùng nhóm; trang khu vực → trang dịch vụ chính + trang tổng “Khu vực phục vụ”; trang dịch vụ → 2–3 bài hướng dẫn liên quan | GĐ1 |
| YC-603 | Không cho link tới bài chưa đăng hoặc đang nháp | GĐ1 |
| YC-604 | Kiểm tra link hỏng trong bài trước khi đăng | GĐ1 |
| YC-605 | Bản đồ liên kết toàn site: số link vào/ra từng URL, trang không có link trỏ tới, số lần bấm từ trang chủ | GĐ2 |
| YC-606 | Khi bài mới đăng: đề xuất 3–5 bài cũ nên chèn link tới bài mới, kèm câu chèn; người dùng duyệt rồi phần mềm cập nhật | GĐ2 |
| YC-607 | Cảnh báo một anchor giống hệt nhau dùng quá nhiều lần cho cùng một URL | GĐ2 |
| YC-608 | Cập nhật trang tổng “Khu vực phục vụ” mỗi khi có trang khu vực mới đăng | GĐ2 |

### M7. Kiểm tra trước khi đăng — GĐ1
Mỗi mục cho kết quả **Chặn** (không cho đăng) hoặc **Cảnh báo** (đăng được nếu người dùng xác nhận).

| # | Kiểm tra | Mức |
|---|---|---|
| 1 | Chính tả tiếng Việt có dấu; danh sách lỗi cấm (“sửa cua”, từ thiếu dấu trong tiêu đề) | Chặn |
| 2 | Mọi con số đi kèm “năm, khách, %, giờ, phút, sao, đánh giá, đồng, triệu, nghìn” phải khớp file thông tin | Chặn |
| 3 | Địa danh có trong danh sách hành chính; địa danh thuộc tỉnh khác → chặn | Chặn |
| 4 | Địa chỉ, hotline, Zalo khớp file thông tin | Chặn |
| 5 | Độ giống với bài khác trên site dưới ngưỡng (nhất là giữa các trang khu vực) | Chặn |
| 6 | Title, meta description không trùng bài khác | Chặn |
| 7 | Dễ đọc: câu trung bình ngắn (ví dụ ≤ 25 từ), đoạn ≤ 4 câu, có tiêu đề phụ. Không dùng Flesch, không đo mật độ từ khóa | Cảnh báo |
| 8 | Ảnh đã nén, có alt, không còn GPS | Chặn nếu còn GPS |
| 9 | Title, meta, slug đúng độ dài; một H1 | Cảnh báo |
| 10 | Schema hợp lệ | Chặn |
| 11 | Có link tới trang dịch vụ đích; không có link hỏng hay link tới bài chưa đăng | Chặn |
| 12 | Lời kêu gọi liên hệ ở 2–3 vị trí, không dày đặc | Cảnh báo |
| 13 | Người dùng xác nhận đã đọc toàn bài | Chặn |

### M8. Đăng lên WordPress
| Mã | Yêu cầu | Ưu tiên |
|---|---|---|
| YC-801 | Kết nối REST API bằng Application Password của tài khoản Biên tập viên riêng, không dùng tài khoản quản trị | GĐ1 |
| YC-802 | Tạo nháp: nội dung, ảnh, ảnh đại diện, danh mục, thẻ, title/meta SEO, schema | GĐ1 |
| YC-803 | Hẹn giờ đăng theo ngày giờ trong phiếu (giờ Việt Nam); thứ trong tuần do máy tự tính | GĐ1 |
| YC-804 | Cập nhật bài đang có, giữ nguyên URL | GĐ1 |
| YC-805 | Đăng thử lên site staging trước khi lên site chính | GĐ2 |
| YC-806 | Tạo chuyển hướng 301 khi đổi URL hoặc gộp bài | GĐ2 |

---

## 5. Đối chiếu với 6 module đã định

| Module đã định | Trong bản này |
|---|---|
| 1. Content Intelligence | **Ngoài phạm vi** (thuộc kế hoạch). Phần mềm chỉ nhận từ khóa, ý cần có từ phiếu giao bài |
| 2. Writing Quality | M2, M7 |
| 3. SEO Optimization | M4, M5, M6 |
| 4. User Value | M2 (ghi chú thợ, câu khách hay hỏi) |
| 5. Content Management | Giữ: đăng, hẹn giờ, cập nhật bài (M8). Bỏ: A/B testing, nhắc làm mới bài |
| 6. QA Checklist | M7 (13 mục, có mức Chặn) |

---

## 6. Việc cần làm phía website trước khi phần mềm chạy

1. Cài một plugin SEO (Rank Math hoặc Yoast). Site hiện dùng sitemap mặc định WordPress, nhiều khả năng chưa có plugin SEO.
2. Thêm một plugin nhỏ (mu-plugin) đăng ký các trường meta của plugin SEO (title, mô tả, từ khóa chính) để ghi được qua REST API.
3. Tạo tài khoản Biên tập viên riêng + Application Password cho phần mềm.
4. Cài plugin Redirection (có REST API) hoặc bật module chuyển hướng của Rank Math.
5. Chặn lập chỉ mục site staging `staging-m.suachuacuasat.com`.
6. Tạo trang tổng “Khu vực phục vụ”.
7. Sao lưu toàn bộ site trước khi phần mềm được quyền ghi.

---

## 7. Lộ trình xây dựng

| Giai đoạn | Module | Kết quả |
|---|---|---|
| GĐ1 | M0, M1, M2 (trừ YC-209), M3 (trừ YC-307, 308), M4, M5 (YC-501), M6 (YC-601–604), M7, M8 (YC-801–804) | Viết, kiểm tra, đăng nháp, hẹn giờ được bài mới; có báo cáo onpage của 29 URL đang có |
| GĐ2 | YC-209, 307, 308, 502, 503, 605–608, 805, 806 | Sửa bài cũ hàng loạt, tự bổ sung link ngược, gộp bài, đăng thử staging |

---

## 8. Bài kiểm tra nghiệm thu GĐ1

Chạy trên site staging:

1. Nhập file `thong_tin_can_dien.xlsx` → phần mềm báo các khu vực còn thiếu địa chỉ.
2. Nhập ảnh từ USB → ra WebP, không còn GPS, có alt đã duyệt.
3. Nhập phiếu giao bài “Cửa kéo bị kẹt ray” (loại Hướng dẫn, trang đích `/sua-cua-keo-tphcm/`) → tạo dàn ý → nháp.
4. Cố tình thêm “Pro-Metal có 8 năm kinh nghiệm” khi file thông tin chưa điền năm → bị **chặn**.
5. Cố tình thêm “phường Long Biên” → bị **chặn**.
6. Gõ “sửa cua” trong tiêu đề → bị **chặn**.
7. Tạo trang khu vực cho một quận chưa điền địa chỉ → **không cho tạo**.
8. Bài đạt kiểm tra → đăng nháp với title, meta, schema Article + BreadcrumbList, link tới `/sua-cua-keo-tphcm/`.
9. Hẹn giờ thứ Ba tuần sau 8:00 → WordPress hiển thị đúng ngày giờ.
10. Chạy rà soát onpage → ra báo cáo lỗi cho 29 URL đang có.

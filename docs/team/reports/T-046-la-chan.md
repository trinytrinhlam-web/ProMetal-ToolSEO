# Biên bản bảo mật T-046 · Thiết kế Giai đoạn 3 (ảnh)

> **Model:** chạy tạm Claude Opus 5.5 vì tài khoản không dùng được Fable (chủ dự án đã duyệt). **Sau 01/11 phải kiểm lại bằng Fable.**

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm) |
| Phiếu được kiểm | [T-046](../tickets/T-046-thiet-ke-giai-doan-3.md) |
| Phạm vi | Kiểm rút gọn (phiếu chỉ sửa tài liệu): diff `a23f764..96385ed` trên `team/T-046` (3 commit `23647dc`, `392e4ab`, `96385ed`) |
| Ngày | 2026-10-17 |
| **Kết luận** | **ĐẠT** |

## Tóm tắt (cho chủ dự án)

Phiếu chỉ thêm một file báo cáo thiết kế. Không có khóa, mật khẩu, đường dẫn file bí mật hay thông tin khách trong file và trong cả 3 commit. Thiết kế khớp chính sách bảo mật và quyết định "giữ GPS"; bên dưới là các góp ý để các phiếu code Giai đoạn 3 làm cho chặt.

## Bằng chứng

| Kiểm | Lệnh | Kết quả |
|---|---|---|
| Chỉ đúng 1 file | `git diff --stat origin/main...HEAD` | `docs/team/reports/T-046-tho-may.md`, 262 dòng thêm, không file nào khác. 3 commit đều chỉ đụng file này |
| Quét bí mật file hiện tại | `uvx detect-secrets scan docs/team/reports/T-046-tho-may.md` | `"results": {}` |
| Quét bí mật từng bản trong lịch sử | `git show <commit>:<file>` → `detect-secrets scan`, cho cả 3 commit | 0 phát hiện ở cả 3 bản |
| Quét toàn bộ patch của nhánh | `git log -p origin/main..HEAD` → `detect-secrets scan` | `"results": {}` |
| Grep khóa/mật khẩu/đường dẫn/dữ liệu cá nhân | `grep -Ei 'api_key\|secret\|password\|token\|sk-\|AIza\|BEGIN PRIVATE\|\.json\|\.env\|C:\\Users\|số điện thoại\|email'` trên patch và file | Chỉ khớp tên định dạng và tên file thiết kế (`_seo_tags.json`), bảng giá mô hình, và email tác giả commit (tài khoản GitHub của dự án, đã có trong toàn bộ lịch sử, không phải dữ liệu khách). Không có Application Password, không có đường dẫn tới JSON service account, không có nội dung `.env` |
| Đường dẫn máy | grep `scratchpad`, `C:/`, `D:` | Chỉ `scratchpad\t046\` (tương đối, không tên người dùng) và các ví dụ đường dẫn tấn công trong thử 14 |
| Dữ liệu cá nhân khách | đọc toàn văn | Tọa độ GPS N 16.0544 / E 108.2022 là **giả** (báo cáo ghi rõ ảnh và GPS do Pillow tạo; là vùng trung tâm thành phố, không phải một nhà). Ví dụ "Nha anh Tuan 12 Le Loi" là ví dụ minh họa rủi ro, không gắn với khách thật. Không có ảnh nào được commit |

## Lỗi phát hiện

Không phát hiện lỗi (không lộ bí mật, không lộ dữ liệu cá nhân).

## Đối chiếu chính sách (soát nhanh nội dung thiết kế)

| Điểm | Kết quả |
|---|---|
| Giữ GPS (sổ rủi ro mục 6, 2.6, F2) | Khớp: chép EXIF khi nén WebP, kiểm sau nén, test bắt buộc. Câu hỏi 2 (bỏ số seri, MakerNote) không đụng tới GPS, là đề xuất giảm lộ thông tin máy nhân viên: hợp lệ, chủ dự án quyết |
| A3 (không gửi dữ liệu khách cho AI) | Khớp: bản gửi AI bỏ EXIF/XMP, không gửi tên file gốc, đường dẫn; không dùng Files API/URL |
| 2.2 / W2 (không đăng, không xóa, không ghi đè) | Khớp: chỉ tải ảnh khi người dùng bấm "Gửi nháp"; lỗi giữa chừng không xóa media |
| 2.7 / W4 (SSL) | Khớp: giữ https, timeout, SSL như hiện tại; không đề xuất tắt kiểm tra chứng chỉ |
| D1 / 2.8 (thư viện mới) | Khớp: `pillow-heif` đưa thành câu hỏi 1 cho chủ dự án, có ghi Lá Chắn quét. Pillow đã duyệt (2026-10-16) |
| 2.3 (`sanitize_html`) | Khớp: việc mở `class` được ghi rõ là phải qua Lá Chắn (G3-8) |
| F1 (thư mục ảnh) | Khớp: chỉ đọc, chặn `..`/ổ đĩa/UNC/symlink/junction, nháp chỉ lưu đường dẫn tương đối |
| 2.9 (ảnh khách không commit) | Khớp: ảnh mẫu thật không commit |

## Góp ý cho các phiếu code Giai đoạn 3

Không chặn phiếu này. Chỉ Huy chép các điểm liên quan vào phiếu G3 tương ứng.

1. **G3-3 · Bản gửi AI phải sạch thật, không chỉ "không truyền `exif=`".** Pillow có thể tự lấy lại một số metadata từ `im.info` khi lưu JPEG (ví dụ đoạn chú thích COM; XMP tùy phiên bản). Cách chắc: dựng bản gửi AI từ điểm ảnh (xóa sạch `im.info` hoặc tạo ảnh mới rồi dán điểm ảnh vào). Test phải dùng ảnh gốc có **đủ** EXIF + GPS + XMP + chú thích COM (và chunk chữ `tEXt/iTXt` với PNG), rồi khẳng định bytes gửi đi không còn đoạn APP1/COM/XMP nào.
2. **G3-3 · Kiểm GPS sau nén:** so sánh giá trị GPS (không chỉ "có thẻ GPS"). Nếu câu 2 chọn A thì test thêm: số seri, `CameraOwnerName`, MakerNote, ảnh nhỏ IFD1 đã bị bỏ; ảnh AI (G3-7) không có GPS.
3. **G3-2/G3-6 · Tên thư mục là dữ liệu chưa tin cậy và có thể chứa tên/địa chỉ khách.** Thẻ "khu vực" đọc từ tên thư mục (câu 3A) phải đối chiếu với **danh sách quận/huyện cố định**, không khớp thì để trống. Áp dụng trước khi (a) đưa vào prompt AI (A3, bọc khung "dữ liệu tham khảo" theo 2.4) và (b) dùng làm tên file `.webp`, tiêu đề, caption media, vì những thứ này **công khai trên web**. Mã công trình chỉ nhận mẫu cố định (ví dụ `CT\d+`).
4. **G3-1 · `pillow-heif` (nếu chủ dự án chọn 1A):** gói kèm thư viện C giải mã HEIC (libheif, libde265) từng có lỗ hổng; Lá Chắn phải chạy `pip-audit` và kiểm bản libheif đi kèm. Giới hạn số điểm ảnh, dung lượng file và bắt lỗi phải áp dụng cho cả đường mở HEIC, có test riêng. Khi khai báo `pillow>=12.3`, chạy `pip-audit` và cân nhắc nâng lên bản mới nhất nếu có bản vá.
5. **G3-4/G3-7 · Đổi SDK Gemini:** nếu dùng Interactions API mà phải nâng `google-genai` thì đó là thay đổi `uv.lock` → D1 + `pip-audit`. Không đổi địa chỉ máy chủ chính thức đã cố định (T-026), không đọc lại `*_CUSTOM_HEADERS` (T-028/T-034).
6. **G3-7 · Ảnh AI trả về:** chỉ nhận base64 trong phản hồi; **không tải ảnh theo URL** do máy chủ AI đưa về. Giới hạn kích thước trước khi giải base64 (chiều dài chuỗi), rồi mới mở bằng Pillow có giới hạn điểm ảnh. Ảnh AI không được mang thẻ công trình thật (đã có trong thiết kế, giữ test).
7. **G3-8 · Mở `class` trong `sanitize_html`:** chỉ trên `img`/`figure`, mỗi lớp phải khớp **toàn bộ** mẫu `wp-image-\d+` hoặc `wp-block-image`, bỏ lớp lạ thay vì giữ cả thuộc tính. HTML `<figure>` dựng bằng code, alt/caption đã escape, và vẫn chạy qua `sanitize_html` lần cuối. Lá Chắn soát riêng thay đổi này.
8. **G3-8/G3-10 · Ảnh công khai ngay khi tải lên:** giao diện nên nói rõ trước nút "Gửi nháp" rằng ảnh (có GPS) sẽ xem được công khai qua đường dẫn kể cả khi bài là nháp. Lỗi giữa chừng: liệt kê media đã tải để người dùng tự xử lý (app không xóa, đúng W2).
9. **G3-2/G3-3 · Cache ảnh xem trước:** thư mục cache phải nằm trong `.gitignore` (kiểm lại trong code, đừng chỉ dựa vào báo cáo). Ảnh xem trước nên bỏ EXIF (chỉ dùng trong máy, không cần GPS). Câu báo lỗi và giao diện không hiện đường dẫn tuyệt đối (U1/U2).
10. **G3-6 · Nếu chọn câu 3B (ghi file thẻ vào Drive):** đây là lần đầu app ghi vào thư mục ảnh. Chỉ ghi đúng một tên file cố định, ghi file tạm rồi đổi tên, chặn symlink/junction ở đích ghi, đọc file thẻ bằng `json` (không `pickle`/`eval`), giới hạn dung lượng file thẻ. Lá Chắn soát kỹ F1 ở phiếu đó.
11. **G3-9 · Nháp:** đọc nháp cũ phải kiểm lại đường dẫn tương đối qua đúng hàm chặn của G3-2 (nháp là dữ liệu có thể bị sửa tay), không tin số thứ tự gốc vượt phạm vi.

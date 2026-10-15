# Bảng việc

Chủ dự án xem file này để biết agent nào đang làm gì. Chỉ Huy cập nhật mỗi khi giao, nhận hoặc đóng phiếu.

_Cập nhật: 2026-10-15_

## Đang làm

> 2026-10-15: 4 phiên (Ngòi Bút · T-022, Soi Lỗi · T-018/T-023/T-024) dừng lúc 22:05 ngày 14/10 vì chạm giới hạn sử dụng của tài khoản; đã chạy lại theo đợt, tối đa 3 phiên cùng lúc.

Mỗi agent chạy ở một **phiên con** dưới phiên "Điều phối" (thanh bên app Claude), tên phiên = tên agent + số phiếu. Mỗi phiếu làm trên nhánh tạm `team/T-xxx`, gộp vào `main` khi Lá Chắn ĐẠT.

| Phiếu | Việc | Agent (tên phiên) | Nhánh | Trạng thái | Báo cáo |
|---|---|---|---|---|---|
| [T-018](tickets/T-018-them-openai-gemini.md) | Thêm AI ChatGPT (OpenAI) và Gemini, thư viện chính hãng (chủ dự án duyệt 2026-10-14) | Thợ Máy (`Thợ Máy · T-018 ChatGPT/Gemini`) → Soi Lỗi (`Soi Lỗi · T-018 ChatGPT/Gemini`) | `team/T-018` | Soi Lỗi lượt 2 **đạt** (654cdb7; còn SL-3, SL-4 mức Thấp). Đã gộp vào `team/T-023` (2.169 test qua). **Lá Chắn đang kiểm** (`Lá Chắn · T-018 + T-023 ChatGPT/Gemini`) | [Thợ Máy](reports/T-018-tho-may.md) · [Soi Lỗi](reports/T-018-soi-loi.md) |
| [T-023](tickets/T-023-nut-kiem-tra-khoa-openai-gemini.md) | Bật nút Kiểm tra khóa ChatGPT/Gemini trong Cài đặt → Kết nối | Họa Sĩ (`Họa Sĩ · T-023 Nút Kiểm tra khóa`) → Soi Lỗi (`Soi Lỗi · T-023 Nút Kiểm tra khóa`) | `team/T-023` | Soi Lỗi **đạt**; Họa Sĩ đã sửa 2 lỗi Thấp (67c0be3). **Lá Chắn đang kiểm** chung với T-018 trên `team/T-023`. Lá Chắn kiểm chung T-018 + T-023 | [Họa Sĩ](reports/T-023-hoa-si.md) · [Soi Lỗi](reports/T-023-soi-loi.md) |
| [T-025](tickets/T-025-on-dinh-test-do-toc-do.md) | Ổn định các test đo tốc độ chập chờn | Soi Lỗi (`Soi Lỗi · T-025 Test đo tốc độ`) | `team/T-025` | Đang làm | |
| [T-022](tickets/T-022-sua-ho-so-doanh-nghiep.md) | Soát, sửa hồ sơ doanh nghiệp (PR #3 đã gộp vào `main`) | Ngòi Bút (`Ngòi Bút · T-022 Hồ sơ doanh nghiệp`) → Soi Lỗi (`Soi Lỗi · T-022 Hồ sơ doanh nghiệp`) | `team/T-022` | Ngòi Bút xong lượt 2 (dfdffc5), Soi Lỗi lượt 1 **đạt**. Chờ Lá Chắn kiểm chung với T-024 | [Ngòi Bút](reports/T-022-ngoi-but.md) · [Soi Lỗi](reports/T-022-soi-loi.md) |
| [T-024](tickets/T-024-loc-ho-so-theo-khoi.md) | Bộ lọc hồ sơ doanh nghiệp lọc theo cả ý (Ngòi Bút phát hiện ở T-022) | Thợ Máy (`Thợ Máy · T-024 Bộ lọc hồ sơ`) → Soi Lỗi (`Soi Lỗi · T-024 Bộ lọc hồ sơ`) | `team/T-024` | Thợ Máy sửa xong SL-024-1, SL-024-2 (ea1a7be, 2.014 test qua). Soi Lỗi kiểm lại lượt 2. Nhánh đã gộp T-022; Lá Chắn kiểm chung T-022 + T-024 | [Thợ Máy](reports/T-024-tho-may.md) · [Soi Lỗi](reports/T-024-soi-loi.md) |

## Chờ

| Phiếu | Việc | Agent | Chờ gì |
|---|---|---|---|
| T-019 | Thử mù mô hình trong Cài đặt | Họa Sĩ, Thợ Máy | T-018 |
| Giai đoạn 3 | Ảnh: khai báo thư viện Pillow | Thợ Máy | Chủ dự án chọn "để sau" (2026-10-14), hỏi lại khi tới Giai đoạn 3 |

## Việc đang làm ngoài hệ thống phiếu

Các việc này bắt đầu trước khi có đội agent. Khi xong, Chỉ Huy lập phiếu kiểm định cho Lá Chắn.

| Việc | Ở đâu |
|---|---|
| _(không còn)_ | Hồ sơ doanh nghiệp (PR #3) đã gộp vào `main` 2026-10-14, kiểm định qua T-022 |

## Xong

| Phiếu | Việc | Agent | Ngày xong | Kết quả |
|---|---|---|---|---|
| [T-021](tickets/T-021-sua-loi-kho-nhap-va-env.md) | Sửa lỗi kho nháp và ghi `.env` (2 lượt Thợ Máy) | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-021-tho-may.md) · [Soi Lỗi](reports/T-016-020-soi-loi.md) lần 2: đạt · Lá Chắn: [**ĐẠT**](reports/T-016-020-la-chan.md) lần 2 (chạy tạm Opus) |
| [T-020](tickets/T-020-nhap-khoa-api-trong-app.md) | Nhập khóa API Claude/ChatGPT/Gemini trong Cài đặt | Thợ Máy, Họa Sĩ | 2026-10-14 | [Thợ Máy](reports/T-020-tho-may.md) · [Họa Sĩ](reports/T-020-hoa-si.md) · Lá Chắn: **ĐẠT** |
| [T-017](tickets/T-017-giao-dien-luu-nhap.md) | Tự lưu, mở lại, xóa bài đang soạn | Họa Sĩ | 2026-10-14 | [Báo cáo](reports/T-017-hoa-si.md) · Soi Lỗi: đạt · Lá Chắn: **ĐẠT** |
| [T-016](tickets/T-016-luu-nhap-bai-dang-soan.md) | Kho lưu nháp bài đang soạn | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-016-tho-may.md) · Soi Lỗi: đạt · Lá Chắn: **ĐẠT** |
| [T-015](tickets/T-015-loi-thap-con-lai.md) | Lỗi Thấp còn lại, test tốc độ ổn định (2 lần) | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-015-tho-may.md) · [Soi Lỗi](reports/T-015-soi-loi.md): đạt · Lá Chắn: [**ĐẠT**](reports/T-015-la-chan.md) lần 2 (chạy tạm bằng Opus) |
| [T-014](tickets/T-014-loi-thap-escape.md) | Lỗi Thấp của bộ escape link | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-014-tho-may.md) · [Soi Lỗi](reports/T-013-014-soi-loi.md): đạt, còn R5-1 → T-015 · Lá Chắn: [**ĐẠT**](reports/T-013-014-la-chan.md) (chạy tạm bằng Opus, kiểm lại bằng Fable sau 01/11) |
| [T-013](tickets/T-013-escape-cau-can-xem-lai.md) | Hiển thị an toàn câu «Cần xem lại» | Họa Sĩ | 2026-10-14 | [Báo cáo](reports/T-012-hoa-si.md) · Soi Lỗi: đạt · Lá Chắn: [**ĐẠT**](reports/T-013-014-la-chan.md) |
| [T-012](tickets/T-012-an-dau-escape-o-o-sua.md) | Ô sửa chữ không hiện dấu `\` | Họa Sĩ | 2026-10-14 | [Báo cáo](reports/T-012-hoa-si.md) · Lá Chắn: [**ĐẠT**](reports/T-008r3-012-la-chan.md) |
| [T-008](tickets/T-008-gia-co-bo-loc.md) | Chặn link Markdown tận gốc (3 lần) | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-008-tho-may.md) · Lá Chắn: **ĐẠT** · [Soi Lỗi](reports/T-008r3-012-soi-loi.md): đạt, còn R4-1 → T-013 |
| [T-011](tickets/T-011-sua-cum-cam-bat-nham.md) | Sửa cụm từ cấm bắt nhầm | Ngòi Bút | 2026-10-14 | Lá Chắn: [**ĐẠT**](reports/T-008r-010-011-la-chan.md) |
| [T-010](tickets/T-010-cau-hinh-chiu-loi-va-loi-thap.md) | File cấu hình chịu lỗi, lỗi Thấp | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-010-tho-may.md) · Lá Chắn: **ĐẠT** |
| [T-009](tickets/T-009-dua-loi-dan-moi-vao-code.md) | Đưa lời dặn AI mới vào code | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-009-tho-may.md) · Lá Chắn: [**ĐẠT**](reports/T-003-006-008-009-la-chan.md) |
| [T-006](tickets/T-006-sua-loi-nho-giai-doan-2.md) | Sửa lỗi Trung bình/Thấp Giai đoạn 2 | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-006-tho-may.md) · Lá Chắn: **ĐẠT** |
| [T-003](tickets/T-003-ra-soat-prompt-noi-dung.md) | Rà soát prompt, quy tắc văn phong | Ngòi Bút | 2026-10-14 | [Báo cáo](reports/T-003-ngoi-but.md) · Lá Chắn: **ĐẠT** |
| [T-004](tickets/T-004-loc-html-ket-qua-ai.md) | Lọc HTML/link trong kết quả AI | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-004-tho-may.md) · Soi Lỗi: [3 lỗ hở nhỏ](reports/T-004-T-005-soi-loi.md) → T-008 · Lá Chắn: [**ĐẠT**](reports/T-004-T-005-la-chan.md) |
| [T-005](tickets/T-005-escape-hien-thi-bai.md) | Hiển thị bài AI an toàn | Họa Sĩ | 2026-10-14 | [Báo cáo](reports/T-005-hoa-si.md) · Soi Lỗi: xác nhận · Lá Chắn: **ĐẠT** |
| [T-001](tickets/T-001-kiem-dinh-bao-mat-nen.md) | Kiểm định bảo mật toàn bộ code | Lá Chắn | 2026-10-14 | [Biên bản](reports/T-001-la-chan.md): KHÔNG ĐẠT (1 Cao). Nay **ĐẠT** (sau T-004, T-005, T-006, T-009). |
| [T-007](tickets/T-007-xoa-gps-anh-dai-dien.md) | Xóa GPS trong ảnh | Thợ Máy | 2026-10-14 | **Hủy**: chủ dự án muốn giữ vị trí trong ảnh (sổ rủi ro, `security.md` mục 6) |
| [T-002](tickets/T-002-kiem-thu-giai-doan-2.md) | Kiểm thử Giai đoạn 2 phần 1 | Soi Lỗi | 2026-10-14 | [Báo cáo](reports/T-002-soi-loi.md): 69 test mới, 8 lỗi (đánh dấu `xfail`), test chặn mạng thật. Chỉ Huy soát: test chỉ dùng khóa giả. |

## Việc bắt buộc khi làm Giai đoạn 5 (đăng lên WordPress)

Lá Chắn yêu cầu, xem các biên bản trong `reports/`:

- Chuyển Markdown sang HTML bằng code có escape, hiểu dấu `\` escape, chuẩn hóa xuống dòng, không xử lý link kiểu tham chiếu.
- `sanitize_html` áp cho toàn bộ HTML cuối, kể cả phần người dùng tự gõ.
- Màn hình xác nhận liệt kê mọi link (`href`), đánh dấu địa chỉ lạ hoặc có `@` ở phần tên máy. **Bắt buộc**, vì `sanitize_html` vẫn cho qua `<a href="https://…">`, nên link ẩn chỉ bị phát hiện ở bước này ([T-015-la-chan.md](reports/T-015-la-chan.md)).
- Đúng một đường đi tới `publish`/`future`, có bước xác nhận và có test.
- Từ khóa lấy từ Google Sheets phải được vô hiệu thẻ khung (SL-7).
- URL trần `https://…` trong thân bài có thể bị Markdown kiểu GFM tự biến thành link: bộ chuyển Markdown sang HTML không bật autolink, hoặc màn hình xác nhận liệt kê cả các URL này ([T-015-soi-loi.md](reports/T-015-soi-loi.md)).

## Số phiếu tiếp theo: T-026

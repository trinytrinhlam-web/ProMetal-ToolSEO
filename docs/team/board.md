# Bảng việc

Chủ dự án xem file này để biết agent nào đang làm gì. Chỉ Huy cập nhật mỗi khi giao, nhận hoặc đóng phiếu.

_Cập nhật: 2026-10-15 14:10 (Chỉ Huy B, đang bàn giao cho Chỉ Huy A: xem mục "Đang làm dở" của dong-bo.md). Hai Chỉ Huy phối hợp qua [dong-bo.md](dong-bo.md): đọc file đó trước._

> 2026-10-15 13:20: Chỉ Huy B nhận quyền, làm tiếp 3 việc dở của A (T-026, T-029, T-025). Phát hiện `main` đỏ trên Linux (9 test của T-027), lập T-030.
>
> 2026-10-15 13:50 (A): chủ dự án yêu cầu Chỉ Huy A dừng để Chỉ Huy B làm tiếp.

## Đang làm

> 2026-10-15: Fable 5.1 vẫn bị giới hạn tới 01/11, nên Lá Chắn chạy tạm bằng Opus 5.5 (chủ dự án đã duyệt). Sau 01/11 Lá Chắn kiểm lại bằng Fable: T-013 → T-021, T-018, T-022, T-023, T-024, T-026, T-027, T-028, T-029, T-030.
>
> 2026-10-15 12:35: tài khoản của Chỉ Huy A gọi Fable 5.1 bị từ chối ("cần mua thêm lượt dùng"), nên Lá Chắn T-027 chạy lại bằng Opus 5.5.
>
> 2026-10-15: 4 phiên (Ngòi Bút · T-022, Soi Lỗi · T-018/T-023/T-024) dừng lúc 22:05 ngày 14/10 vì chạm giới hạn sử dụng của tài khoản; đã chạy lại theo đợt, tối đa 3 phiên cùng lúc.

> 2026-10-15 11:30: Chỉ Huy A (Claude Desktop trên máy chủ dự án) đã xóa các nhánh tạm gộp xong: `team/T-018`, `team/T-022`, `team/T-023`, `team/T-024`.

Mỗi agent chạy ở một **phiên con** dưới phiên Chỉ Huy đang giữ quyền (xem [dong-bo.md](dong-bo.md)), tên phiên = tên agent + số phiếu. Mỗi phiếu làm trên nhánh tạm `team/T-xxx`, gộp vào `main` khi Lá Chắn ĐẠT.

| Phiếu | Việc | Agent (tên phiên) | Nhánh | Trạng thái | Báo cáo |
|---|---|---|---|---|---|
| [T-019](tickets/T-019-thu-mu-mo-hinh.md) | Thử mù mô hình AI trong Cài đặt (việc cuối của Giai đoạn 2) | Thợ Máy (`Thợ Máy · T-019 Thử mù mô hình`) → Họa Sĩ (`Họa Sĩ · T-019 Thử mù mô hình`) | `team/T-019` | Thợ Máy xong logic (`d2bfa8c`, 39 test). Họa Sĩ xong giao diện (`0d09f4d`, 14 test; Linux chỉ 9 test đỏ sẵn của T-027). Soi Lỗi **đạt có điều kiện** (`e3cee76`): SL-T019-1 AI tự xưng tên lọt lớp che (`_Claude_`, `Opus`…), SL-T019-2 tên mô hình quá ngắn làm hỏng bài mọi ứng viên. **Thợ Máy đang sửa lượt 2** (phiên Chỉ Huy A), rồi Soi Lỗi kiểm lại, rồi Lá Chắn | [Thợ Máy](reports/T-019-tho-may.md) · [Họa Sĩ](reports/T-019-hoa-si.md) · [Soi Lỗi](reports/T-019-soi-loi.md) |
| [T-025](tickets/T-025-on-dinh-test-do-toc-do.md) | Ổn định các test đo tốc độ chập chờn | Soi Lỗi (`Soi Lỗi · T-025 Test đo tốc độ (tiếp)`) | `team/T-025` | Chỉ Huy B đã gộp `main` vào nhánh (`ce1a79c`). Soi Lỗi làm tiếp và nộp báo cáo | |

## Chờ

| Phiếu | Việc | Agent | Chờ gì |
|---|---|---|---|
| [T-031](tickets/T-031-dia-chi-tran-thanh-link.md) | Địa chỉ trần, `www.`, email trong chữ AI không thành link bấm được (Soi Lỗi phát hiện ở T-019; có ở cả trang Soạn bài) | Thợ Máy | T-019 gộp vào `main` |
| _(chưa lập phiếu)_ | Lỗi Thấp #1, #2 của bộ lọc hồ sơ: nhãn gõ sai (`[CẦNXÁC NHẬN]`, không dấu, ngoặc tròn), nhãn trên tiêu đề | Thợ Máy (#1), Ngòi Bút (#2) | Lá Chắn đề nghị ([biên bản](reports/T-022-024-la-chan.md)); lập phiếu sau T-026 |
| _(gộp vào phiếu lớp AI tiếp theo)_ | Lỗi Thấp của Lá Chắn T-028: LC-T028-1 đổi khóa gỡ biến môi trường sang `RLock` (gọi lồng sẽ treo; hiện không có chỗ gọi lồng); LC-T028-3 gzip hỏng ra "Không kết nối được" (có từ trước). LC-T028-2 chấp nhận | Thợ Máy | Khi có phiếu lớp AI tiếp theo |
| _(chưa lập phiếu)_ | Ghim cùng một bản Python cho mọi máy (`.python-version` hiện là `3.12`: cloud chạy 3.12.3, Windows 3.12.15; độ lệch này gây 9 test đỏ ở T-030) | Thợ Máy | Soi Lỗi đề xuất ở T-029; lập phiếu sau khi T-029 + T-030 gộp |
| _(ghi nhận, không lập phiếu)_ | Bộ chặn mạng của test chỉ xét socket AF_INET/AF_INET6; họ khác (AF_UNIX…) không bị chặn nhưng không có đường vô tình ra mạng | — | Lá Chắn T-029 + T-030, lỗi Thấp #2 |
| Giai đoạn 3 | Ảnh: khai báo thư viện Pillow | Thợ Máy | Chủ dự án chọn "để sau" (2026-10-14), hỏi lại khi tới Giai đoạn 3 |

## Việc đang làm ngoài hệ thống phiếu

Các việc này bắt đầu trước khi có đội agent. Khi xong, Chỉ Huy lập phiếu kiểm định cho Lá Chắn.

| Việc | Ở đâu |
|---|---|
| _(không còn)_ | Hồ sơ doanh nghiệp (PR #3) đã gộp vào `main` 2026-10-14, kiểm định qua T-022 |

## Xong

| Phiếu | Việc | Agent | Ngày xong | Kết quả |
|---|---|---|---|---|
| [T-029](tickets/T-029-bo-chan-mang-udp-va-dns.md) + [T-030](tickets/T-030-test-t027-chay-tren-linux-mac.md) | Bộ chặn mạng chặn thêm UDP, tra tên; test T-027 chạy được trên Linux/Mac | Soi Lỗi | 2026-10-15 | [Soi Lỗi](reports/T-029-soi-loi.md) · Lá Chắn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-029-030-la-chan.md) (Opus tạm). Điều kiện chạy trên Windows: Chỉ Huy A chạy 2 lượt, 2.758 qua, 0 hỏng; test IPv6, Proactor, `vong-lap-mac-dinh` đều qua. Gộp vào `main` `7c8604e` |
| [T-028](tickets/T-028-noi-dung-hong-tu-may-chu-ai.md) | Máy chủ AI trả 200 nhưng nội dung hỏng → câu lỗi tiếng Việt; bỏ qua `*_CUSTOM_HEADERS` | Thợ Máy | 2026-10-15 | [Thợ Máy](reports/T-028-tho-may.md) (2 lượt) · [Soi Lỗi](reports/T-028-soi-loi.md): đạt · Lá Chắn: [**ĐẠT**](reports/T-028-la-chan.md) (Opus tạm), 3 lỗi Thấp ghi sổ. Gộp vào `main` `d08f8ca`: Windows 3.110 qua, 0 hỏng |
| [T-026](tickets/T-026-loi-thap-lop-ai.md) | 4 lỗi Thấp lớp AI: thư viện lệch phiên bản, câu lỗi 400 cố định, `base_url` chính thức | Thợ Máy | 2026-10-15 | [Thợ Máy](reports/T-026-tho-may.md) (2 lượt) · [Soi Lỗi](reports/T-026-soi-loi.md): đạt lượt 2 · Lá Chắn: [**ĐẠT**](reports/T-026-la-chan.md) (Opus tạm, Chỉ Huy B giao lại) |
| [T-027](tickets/T-027-test-chay-tren-windows.md) | Bộ test chạy xanh trên Windows | Soi Lỗi | 2026-10-15 | [Soi Lỗi](reports/T-027-soi-loi.md) · Lá Chắn: [**ĐẠT**](reports/T-027-la-chan.md) (Opus tạm), 2 lỗi Thấp → T-029. Gộp vào `main` `e4107f2`: Windows 2.358 qua, 0 hỏng |
| [T-024](tickets/T-024-loc-ho-so-theo-khoi.md) | Bộ lọc hồ sơ lọc theo cả ý | Thợ Máy | 2026-10-15 | [Thợ Máy](reports/T-024-tho-may.md) (2 lượt) · [Soi Lỗi](reports/T-024-soi-loi.md): đạt lượt 2 · Lá Chắn: [**ĐẠT**](reports/T-022-024-la-chan.md) (Opus tạm), 4 lỗi Thấp ghi sổ. Gộp vào `main` `958a93e` |
| [T-022](tickets/T-022-sua-ho-so-doanh-nghiep.md) | Soát, sửa hồ sơ doanh nghiệp theo trả lời của chủ dự án | Ngòi Bút | 2026-10-15 | [Ngòi Bút](reports/T-022-ngoi-but.md) (2 lượt) · [Soi Lỗi](reports/T-022-soi-loi.md): đạt · Lá Chắn: [**ĐẠT**](reports/T-022-024-la-chan.md) (Opus tạm). Gộp vào `main` `958a93e` |
| [T-023](tickets/T-023-nut-kiem-tra-khoa-openai-gemini.md) | Nút Kiểm tra khóa ChatGPT/Gemini trong Cài đặt → Kết nối | Họa Sĩ | 2026-10-15 | [Họa Sĩ](reports/T-023-hoa-si.md) (2 lượt) · [Soi Lỗi](reports/T-023-soi-loi.md): đạt · Lá Chắn: [**ĐẠT**](reports/T-018-023-la-chan.md) (Opus tạm) |
| [T-018](tickets/T-018-them-openai-gemini.md) | Thêm ChatGPT (`openai`) và Gemini (`google-genai`) vào lớp AI | Thợ Máy | 2026-10-15 | [Thợ Máy](reports/T-018-tho-may.md) (2 lượt) · [Soi Lỗi](reports/T-018-soi-loi.md): đạt lượt 2 · Lá Chắn: [**ĐẠT**](reports/T-018-023-la-chan.md) (Opus tạm), 4 lỗi Thấp → T-026 |
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

## Số phiếu tiếp theo: T-032

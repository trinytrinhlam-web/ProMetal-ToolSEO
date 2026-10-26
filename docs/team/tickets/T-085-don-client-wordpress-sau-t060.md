# T-085 · Dọn lỗi Thấp client WordPress sau T-060 (LC-T060-1, -2, -3, SL-T060-1)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-24 |
| Giai đoạn | Giai đoạn 4 |
| Mức ưu tiên | Thấp (trước khi hết Giai đoạn 4; LC-T060-1, -2 bắt buộc trước phiếu nào đưa khóa JSON hay giá trị tham số lấy từ dữ liệu ngoài vào `_request`) |
| Phụ thuộc | T-060 đã gộp |
| Trạng thái | Xong |

## Mục tiêu

Đóng các chốt chặn còn thiếu của `_request` (khóa thân JSON, giá trị `_fields`) và câu báo của `upload_media` khi ảnh đã lên mà ghi mô tả hỏng.

## Bối cảnh

Biên bản Lá Chắn T-060 (`docs/team/reports/T-060-la-chan.md`, bảng lỗi và mục Điều kiện 1–3, mục «Thử bản sửa mẫu», «Đối chiếu mã nguồn WordPress») và báo cáo Soi Lỗi T-060 (`docs/team/reports/T-060-soi-loi.md`, SL-T060-1):

- **LC-T060-1:** thân JSON chưa có danh sách khóa theo đường; WordPress cho khóa trong thân JSON thắng tham số trên đường (`id`, `name`), `status` khác `draft` đi ra được.
- **LC-T060-2:** `_fields` chỉ kiểm kiểu, không kiểm giá trị; hỏi `content`, `description`… làm WordPress chạy `the_content` (shortcode) ngay trong lệnh của app.
- **LC-T060-3 + SL-T060-1:** `upload_media` ảnh đã lên (201) mà lệnh ghi đè hỏng, hay trả lời mang mã ảnh khác, thì câu báo không nói ảnh đã nằm trong thư viện Media.

## Phạm vi

- **Được sửa:** `seo_app/wordpress/client.py`, test mới; gỡ `xfail` trong `tests/test_la_chan_t060.py` (12 ca) và `tests/test_soi_loi_t060.py` (SL-T060-1) khi XPASS (chỉ xóa dấu).
- **Không được sửa:** `app/**`, `config/**`; tên, chữ ký, hành vi `_has_shortcode`, `_SHORTCODE_OPEN`, `_drop_invisible` (dùng chung với `seo_app/wordpress/shortcodes.py` của T-056).
- Nếu chọn danh sách giá trị `_fields` tuyệt đối (phải sửa 9 ca test cũ đang gửi `_fields` khác hằng) thì hỏi Chỉ Huy trước (R5).

## Yêu cầu

1. **LC-T060-1:** danh sách khóa thân JSON cấp trên cùng theo từng đường (cùng kiểu `ALLOWED_PARAMS`, thiếu đường thì lỗi khi nạp module); không bao giờ nhận `id`, `name`; có `status` thì chỉ `"draft"`.
2. **LC-T060-2:** với `_fields`, tách theo dấu phẩy và khoảng trắng; tên trường (phần trước dấu chấm) thuộc `content`, `excerpt`, `description`, `caption`, `_embedded`, `_links` thì chặn.
3. **LC-T060-3 + SL-T060-1:** `upload_media` bọc lệnh ghi đè; hỏng, hay trả lời không đúng mã ảnh vừa tạo, thì báo câu cố định có «thư viện Media», mã ảnh (số đã kiểm) và dặn vào Media → Thư viện kiểm hoặc xóa.
4. Không chặn oan mọi lệnh thật app đang gửi (ca đối chứng của Lá Chắn T-060 phải qua).
5. Gỡ `xfail` khi XPASS.

## Yêu cầu bảo mật riêng

W1, W2, W3, S2.

## Tiêu chí xong

- [ ] Yêu cầu 1–5
- [ ] Test liên quan (các file test WordPress, `tests/test_la_chan_t060.py`, `tests/test_soi_loi_t060.py`, `tests/test_wordpress_t060.py`, `tests/test_app_pages.py`) qua, `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo nộp tại `docs/team/reports/T-085-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (W1–W3, S2).

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 1–3 của Lá Chắn T-060; chủ dự án duyệt 2026-10-24. Nhánh `team/T-085` từ `main` sau khi gộp T-060.
- 2026-10-24 10:13 (Chỉ Huy B): Thợ Máy xong phần 1 (`8226ed7`: LC-T060-1, -2, gỡ 9 `xfail`). Hỏi sửa 1 test cũ `tests/test_wordpress_round2_t042.py::test_upload_media_odd_fields_are_safe` (dòng 89-90) cho yêu cầu 3: **Chỉ Huy đồng ý** (đòi `WordPressError` có «thư viện Media», «mã ảnh 5»; phần trường sai kiểu chuyển sang ca mới), commit riêng, bảng trước/sau cho R5.
- 2026-10-26 08:18 (Chỉ Huy B): **Thợ Máy xong** (`8d0eb56`, 5/5; sửa 1 test cũ đã duyệt). Chủ dự án duyệt giao **Soi Lỗi rút gọn** (nhắn phiên Soi Lỗi T-060).
- 2026-10-26 09:18 (Chỉ Huy B): **Soi Lỗi rút gọn ĐẠT CÓ ĐIỀU KIỆN** (`c63eb09`): 5/5 yêu cầu đạt; R5 đạt; gộp thử với `main` và T-056 không xung đột. 3 Thấp: SL-T085-1 (`_fields` vòng qua bằng ký tự NUL sát tên trường), SL-T085-2 (trả lời lồng quá sâu → lỗi đỏ Python ở trang Kết nối WordPress), SL-T085-3 (lỗi ngay lúc nhận ảnh: ảnh có thể đã lên mà câu báo chỉ «thử lại sau»). Chờ Lá Chắn rút gọn.
- 2026-10-26 09:59 (Chỉ Huy B): chủ dự án duyệt; giao **Lá Chắn rút gọn** (nhắn phiên Lá Chắn T-060).
- 2026-10-26 10:33 (Chỉ Huy B): **Lá Chắn rút gọn ĐẠT CÓ ĐIỀU KIỆN** (`0d453d9`): LC-T060-1, -3, SL-T060-1 đóng; 4 Thấp (SL-T085-1 NUL sát tên trường `_fields`; SL-T085-2 + LC-T085-1 `response.json()` để lọt `RecursionError`/lỗi giải mã lạ; SL-T085-3 lỗi ở lệnh tải ảnh của `upload_media` chưa dặn ảnh có thể đã lên) → **phiếu dọn lỗi Thấp client WordPress sau T-085** (chờ chủ dự án duyệt lập; hạn trước khi hết GĐ4). Gộp `main` trên máy (`86a391c`), đang chạy toàn bộ test.
- 2026-10-26 13:07 (Chỉ Huy B): **đã gộp vào `main`** (Windows 13.961 test qua, 0 hỏng, 45 phút); xóa nhánh `team/T-085`, worktree `wt-T-085`. Còn: 4 Thấp (SL-T085-1..3, LC-T085-1) → phiếu dọn mới, chờ chủ dự án duyệt lập.
- 2026-10-26 13:20 (Chỉ Huy B): chủ dự án duyệt lập **T-088** cho 4 Thấp còn lại.

# T-041 · Bước 4 "SEO" của Soạn bài chạy thật

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`), Thợ Máy hỗ trợ phần lưu nháp |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 4 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-036, T-037, T-038, T-039 đã gộp (T-040 nên gộp trước) |
| Trạng thái | Chờ |

## Mục tiêu

Thay phần demo bước 4 trong trang Soạn bài bằng chức năng thật. **Giữ bố cục chủ dự án đã duyệt.**

## Phạm vi

- **Được sửa:**
  - `app/views/write.py`: chỉ bước SEO và trạng thái liên quan;
  - `seo_app/demo.py`: xóa `META_TITLES`, `META_DESCRIPTIONS`, `SLUG`, `INTERNAL_LINKS`, `SCHEMA` khi không còn dùng;
  - `seo_app/storage/drafts.py`: thêm trường meta/link/schema vào nháp, giữ `extra="forbid"`. Phần này Thợ Máy làm trước, cùng nhánh;
  - test giao diện.
- **Không được sửa:** logic `seo_app/onpage/**` (báo Thợ Máy nếu cần đổi).

## Yêu cầu (tóm tắt)

1. **Meta:**
   - ô title/description có nút 🔄 viết lại riêng từng ô, quay lại bản trước được;
   - đếm ký tự NFC; màu Nên / Cảnh báo / Chặn;
   - xem trước kiểu Google (`ui.serp_preview` đã có, kiểm lại escape).
2. **Slug:** gợi ý, sửa được, kiểm trùng.
3. **Liên kết nội bộ:** bảng tick "Dùng", "Cụm từ trong bài", "Trỏ tới bài"; nút "Tải lại danh sách bài".
4. **Schema:** xem FAQPage đã dựng (nếu bài có mục Hỏi đáp), hiện chữ thuần, không HTML.
5. Lưu mọi lựa chọn vào nháp cục bộ (tự lưu như bước 1–3).
6. Bỏ nhãn "Bản demo" của bước này. `tests/test_app_pages.py` vẫn qua.

## Yêu cầu bảo mật riêng

U1 (chữ từ site và AI phải escape; không `unsafe_allow_html` với chữ chưa escape), U2, D3.

## Tiêu chí xong

- [ ] Bước SEO chạy thật, giữ bố cục
- [ ] Test giao diện bằng `AppTest`, hàm giả
- [ ] Báo cáo `docs/team/reports/T-041-hoa-si.md` (và `T-041-tho-may.md` cho phần nháp), kèm hướng dẫn chủ dự án tự mở app xem

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (U1).

## Ghi chú của Chỉ Huy

- Phiên **"Thợ Máy · T-041 Lưu SEO vào nháp"** rồi **"Họa Sĩ · T-041 Bước SEO thật"**, nhánh `team/T-041`.
- 2026-10-16: chủ dự án chưa trả lời câu 1, 2 (cách ghi SEO lên SiteSEO). Bước SEO phải chạy trọn vẹn **không cần** ghi lên site:
  - có nút chép (copy) title, description, slug để chủ dự án dán tay vào hộp SiteSEO;
  - không hiện lỗi hay nút hỏng khi chưa cấu hình ghi SEO;
  - không có kết nối WordPress thì danh sách bài (liên kết nội bộ, kiểm trùng) báo nhẹ "chưa kết nối", các phần còn lại vẫn dùng được.
- 2026-10-16 (Chỉ Huy B), điều kiện của Soi Lỗi T-038, `docs/team/reports/T-038-soi-loi.md`: phần Thợ Máy của phiếu này **được sửa thêm `seo_app/onpage/schema.py`** trước khi Họa Sĩ làm giao diện.
  - SL-T038-2 (Trung bình): bỏ Markdown nội dòng (`**đậm**`, link, `` `mã` ``) ở **cả** bài lẫn câu trả lời trước khi so nguyên văn. JSON-LD không được mang dấu Markdown.
  - SL-T038-1 (Thấp): chặn ký tự surrogate lẻ (loại Cs).
  - Bỏ `xfail` tương ứng trong `tests/test_soi_loi_t038.py`.
- 2026-10-16: **Điều kiện bắt buộc của Lá Chắn T-038** (`docs/team/reports/T-038-la-chan.md`). Phải xong trước khi giao diện dùng `json_ld`, hạn chót trước khi hết Giai đoạn 4:
  1. `schema.py` chặn thêm ký tự loại Cs, Co, Cn.
  2. Bỏ Markdown nội dòng ở cả bài lẫn câu trả lời:
     - link chỉ giữ chữ, không giữ địa chỉ, nên `[x](javascript:…)` không còn trong JSON-LD;
     - ảnh: bỏ, hoặc chỉ giữ alt;
     - **không bao giờ** đổi sang HTML.
  3. Giao diện hiện `json_ld` bằng `st.code`, không dùng `unsafe_allow_html`.
- 2026-10-17 (Chỉ Huy A): **Điều kiện của Lá Chắn T-036** (`docs/team/reports/T-036-la-chan.md`, ĐẠT CÓ ĐIỀU KIỆN). Phải xong trước khi T-042 gửi meta lên site, hạn chót cuối Giai đoạn 4. Phiếu này **được thêm ngoại lệ**: phần Thợ Máy được sửa `seo_app/onpage/meta.py` cho các điểm 1–3.
  1. LC-T036-1: `normalize_meta` (`meta.py:74-85`) bỏ hoặc Chặn ký tự Cc (NUL, ESC…), Cs, Co, Cn, ở cả chữ AI lẫn chữ người dùng gõ; có test.
  2. SL-T036-10: chỉ loại trừ đúng chữ "xu hướng", không nới các đơn vị khác.
  3. SL-T036-12: giao diện không gọi `has_link` / `mentions_price` với chữ chưa cắt độ dài, hoặc cắt độ dài ngay trong hai hàm này.
  4. SL-T036-11, LC-T036-2 (bộ dò link sót vài dạng tên miền lạ): ghi nhận, không bắt buộc.
  5. Phần Họa Sĩ: hiện `FieldCheck.messages` (có tên bài lấy từ site) bằng chữ thuần hoặc đã escape, không dùng `unsafe_allow_html`.

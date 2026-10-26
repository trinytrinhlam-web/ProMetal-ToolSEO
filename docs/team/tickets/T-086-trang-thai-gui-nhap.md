# T-086 · Trạng thái gửi nháp không chỉ nằm trong phiên (SL-T056-8 → -11, LC-T056-1)

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`); được sửa thêm phần trạng thái gửi trong `seo_app/storage/drafts.py` (việc Thợ Máy, Chỉ Huy duyệt cho Họa Sĩ làm để khỏi chia hai nhánh) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-26 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Trung bình (nên xong trước khi dùng nút «Gửi nháp» thường xuyên; trước khi hết Giai đoạn 3) |
| Phụ thuộc | T-056 đã gộp |
| Trạng thái | Họa Sĩ xong, chờ Soi Lỗi rút gọn |

## Mục tiêu

Trong mọi tình huống (tải lại trang, đóng tab, mở bài khác rồi mở lại, bấm liên tục khi đang gửi), app nhớ một bài đã gửi hay đang gửi dở, không cho gửi lại khi chưa xác nhận, và không tải lên ảnh đã bị thay sau khi duyệt.

## Bối cảnh

Biên bản Lá Chắn T-056 (`docs/team/reports/T-056-la-chan.md`, điều kiện 2, LC-T056-1, Ghi nhận 1–3) và báo cáo Soi Lỗi T-056 lượt 2 (`docs/team/reports/T-056-soi-loi.md`, SL-T056-8 → -11): cùng gốc «trạng thái gửi chỉ nằm trong phiên Streamlit».

- **SL-T056-8:** mở bài khác rồi mở lại bài vừa gửi: mất khóa «đã gửi»/«gửi dở».
- **SL-T056-9:** bấm gì đó trong lúc gửi: bài đã lên nhưng app báo «gửi dở», mất kết quả.
- **SL-T056-10:** file ảnh bị thay đúng lúc đang gửi vẫn lên.
- **SL-T056-11:** F5/đóng tab giữa lúc gửi, mở lại nháp: gửi lại không cần xác nhận.
- **LC-T056-1:** khóa chống gửi trùng có khe: bỏ dấu trước, làm việc bảo vệ sau (`mark_send_interrupted`, `draft_panel`).

## Phạm vi

- **Được sửa:** `app/views/write.py`, `seo_app/storage/drafts.py` (chỉ phần lưu/đọc trạng thái gửi của nháp, giữ tương thích nháp cũ), test; gỡ `xfail` trong `tests/test_soi_loi_t056.py` (5 ca) và `tests/test_la_chan_t056.py` (2 ca) khi XPASS (chỉ xóa dấu).
- **Không được sửa:** `seo_app/wordpress/**`, `seo_app/images/**`, `config/**`.

## Yêu cầu

1. (a) Ghi «đang gửi / đã gửi (mã bài)» vào nháp **trước** khi gửi; đọc lại khi mở nháp (SL-T056-8, -11). Nháp có dấu «đang gửi» mà không có kết quả thì coi như «gửi dở»: khóa nút, nhắc kiểm Bài viết → Nháp và Media trước khi xác nhận gửi lại.
2. (b) Đối tượng giữ kết quả, sửa tại chỗ, để lần chạy bị ngắt vẫn giữ kết quả đã có (SL-T056-9).
3. (c) Thứ tự ghi khóa đơn điệu: làm việc bảo vệ trước, bỏ dấu sau (LC-T056-1 (a), (b)).
4. (d) Băm nội dung ảnh lúc duyệt và ngay trước khi tải; khác thì dừng, bắt duyệt lại (SL-T056-10, Ghi nhận 1).
5. Nên gom Ghi nhận 2, 3 của biên bản Lá Chắn nếu nhỏ.
6. Nháp cũ (không có trường trạng thái gửi) vẫn mở được như trước.

## Yêu cầu bảo mật riêng

W1, W2, U1, F2.

## Tiêu chí xong

- [ ] Yêu cầu 1–6, có test (gồm ngắt lần chạy thật, phiên mới cùng kho nháp)
- [ ] Test liên quan (`tests/test_app_images.py`, `tests/test_soi_loi_t056.py`, `tests/test_la_chan_t056.py`, `tests/test_storage_drafts.py`, `tests/test_drafts_images.py`, `tests/test_soi_loi_t055.py`, `tests/test_app_pages.py`) qua, `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo nộp tại `docs/team/reports/T-086-hoa-si.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (W1, W2, U1).

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 2 của Lá Chắn T-056; chủ dự án duyệt 2026-10-26. Nhánh `team/T-086` từ `main` sau khi gộp T-056.
- Nếu chủ dự án chọn không sửa thì phải ghi sổ rủi ro (`security.md` mục 6).
- 2026-10-26 09:55 (Chỉ Huy B): **Họa Sĩ xong** (`e2e345f`, code `1eb96f9`): yêu cầu 1–6; gỡ 7 `xfail` (5 Soi Lỗi, 2 Lá Chắn) đều XPASS trước khi gỡ; thử gỡ chỗ sửa 10/10 đột biến bị bắt; 48 file test liên quan 4.866 qua, 6 file gửi nháp trên code cuối 147 qua. Chờ Soi Lỗi rút gọn.
- 2026-10-26 09:59 (Chỉ Huy B): chủ dự án duyệt; giao **Soi Lỗi rút gọn** (nhắn phiên Soi Lỗi T-056).

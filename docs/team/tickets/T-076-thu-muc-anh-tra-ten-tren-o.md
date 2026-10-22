# T-076 · Thư mục ảnh trả tên theo tên trên ổ (sau T-055)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-21 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Trung bình (Lá Chắn T-055, LC-T055-1); nên gộp trước T-056 |
| Phụ thuộc | T-055 đã gộp |
| Trạng thái | Đang làm |

## Mục tiêu

Ảnh AI không bao giờ thành "ảnh công trình thật" chỉ vì nháp hay người dùng gõ tên thư mục khác chữ hoa/thường với tên trên ổ; bỏ được ràng buộc 2a của T-056.

## Bối cảnh

Biên bản Lá Chắn T-055 (`docs/team/reports/T-055-la-chan.md`, điều kiện 3): `ImageLibrary.list_folder` và `stat_image` nhận `rel_dir` khác hoa thường rồi dựng `ImageRef` theo chữ người gọi gõ, nên `scanned` quét theo đường dẫn trong nháp làm SL-T055-1 quay lại (LC-T055-1, Trung bình). Hai lỗi Thấp đi kèm: LC-T055-2 (= SL-T055-4, `ref` đổi sang file chưa `stat_image` lại; danh sách bị cắt), LC-T055-3 (= SL-T055-5, thư mục cha hơn 5.000 mục thì ảnh "chưa kiểm được").

## Phạm vi

- **Được sửa:** `seo_app/images/folders.py`, `seo_app/storage/drafts.py`, test của hai module này (`tests/test_images_folders.py`, `tests/test_drafts_images.py`), gỡ `xfail` liên quan trong `tests/test_soi_loi_t055.py`.
- **Không được sửa:** `app/**`, `config/**`, `seo_app/images/tags.py`.

## Yêu cầu

1. **LC-T055-1:** `list_folder` và `stat_image` trả `ImageRef` theo tên trên ổ (Windows: từ đường đã `resolve`; Mac: xác nhận từng tầng bằng tên trùng hẳn trong thư mục cha), hoặc từ chối `rel_dir` không trùng hẳn tên trên ổ. Ghi rõ điều kiện của `scanned` trong docstring `check_draft_images`; sửa câu `_MSG_FOLDER_NAME` thành "mở lại từ thư mục ảnh gốc". Có test: nháp ghi `…/congai/cong.png`, trên ổ là `CongAI` → ảnh AI, alt có «Minh họa», cả khi `scanned` quét theo đường dẫn trong nháp.
2. **LC-T055-2:** sau khi đổi sang tên thật, `stat_image` lại và dùng `entry` mới; khác cỡ hay giờ sửa thì báo không dùng được. Danh sách `truncated` mà không có tên trùng hẳn thì không nhận trùng không phân biệt hoa thường.
3. **LC-T055-3:** có tên thật từ `stat_image` thì không cần xem thư mục cha (ảnh ở thư mục con của gốc hơn 5.000 mục vẫn kiểm được). Nếu không làm được gọn, ghi lại trong báo cáo để Chỉ Huy hỏi chủ dự án ghi sổ rủi ro.
4. Gỡ `xfail` SL-T055-4, SL-T055-5 khi XPASS, không đổi điều kiện kiểm.

## Yêu cầu bảo mật riêng

F1, F3.

## Tiêu chí xong

- [ ] Đạt các yêu cầu trên, có test
- [ ] Test liên quan (`uv run pytest tests/test_images_folders.py tests/test_drafts_images.py tests/test_soi_loi_t055.py tests/test_storage_drafts.py tests/test_images_tags.py tests/test_app_pages.py`) qua và `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy trên Windows khi gộp
- [ ] Báo cáo nộp tại `docs/team/reports/T-076-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Rút gọn (F1).

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 3 của Lá Chắn T-055. Làm trên nhánh tạm `team/T-076`, tạo từ `main` sau khi T-055 gộp. Hạn: trước khi hết Giai đoạn 3; nên gộp trước T-056.
- 2026-10-21 13:58 (Chỉ Huy B): chủ dự án cho giao. Nhánh `team/T-076` tạo từ `main` sau khi gộp T-055.
- 2026-10-22 (Chỉ Huy B): **Lá Chắn ĐẠT CÓ ĐIỀU KIỆN** (`docs/team/reports/T-076-la-chan.md`): **lượt 2 trước khi gộp**: sửa **LC-T076-1** (Trung bình: trên Google Drive for Desktop của Windows, `resolve` trả đúng chữ đã gõ nên LC-T055-1 chưa đóng; Windows lấy tên từ danh sách thư mục, không từ `resolve`; sửa chú thích, docstring; thêm kiểu ổ "resolve trả chữ đã gõ" vào test; gỡ `xfail` ở `tests/test_la_chan_t076.py`), nên sửa luôn **LC-T076-2** (= SL-T076-1, cách (a) của Soi Lỗi, gỡ `xfail`). Sau đó Soi Lỗi rút gọn, Lá Chắn rút gọn (F1).

# T-107 · HEIC: không giải mã song song (tránh lỗ hổng libheif 1.23.6, LC-T093-3)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-30 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | **Cao** (chặn đóng Giai đoạn 3) |
| Phụ thuộc | Không |
| Trạng thái | Đang làm |

## Mục tiêu

Ảnh HEIC (iPhone) không đi qua đường giải mã có lỗ hổng đã biết của libheif 1.23.6 (mang sẵn trong pillow-heif 1.8.1), trong khi chưa có bản pillow-heif mang libheif ≥ 1.23.7.

## Bối cảnh

- Lá Chắn T-093 (`docs/team/reports/T-093-la-chan.md`, mục 3), **LC-T093-3 (Cao)**: libheif 1.23.7 (26/10) vá **GHSA-35mc-3887-rr37** (CVSS 7.5, chỉ 1.23.6): dùng vùng nhớ đã giải phóng khi **giải mã song song** các ô ảnh lưới có chung một mục mã hóa, với tùy chọn mặc định; hậu quả sập, hỏng heap. Cùng các lỗi «làm treo CPU» mức cao (file vài kB giải mã hàng chục giây). `pip-audit` không thấy vì lỗi ở thư viện C trong wheel.
- Gợi ý của Lá Chắn: `DECODE_THREADS = 0` (giải mã một luồng) hoặc tạm tắt HEIF; theo dõi bản pillow-heif mang libheif ≥ 1.23.7 để nâng (**nâng thư viện cần chủ dự án duyệt**).
- Test `xfail(strict=True)`: `tests/test_la_chan_t093.py::test_lc_t093_3_heic_decoding_not_exposed_to_libheif_1_23_6` (nhánh `team/T-093`, sẽ vào `main` khi T-093 gộp).

## Phạm vi

- **Được sửa:** `seo_app/images/process.py` (`_register_heif` và chỗ liên quan), test; gỡ `xfail` LC-T093-3 khi XPASS (chỉ xóa dấu, R5).
- **Không được sửa:** `pyproject.toml`, `uv.lock` (không đổi phiên bản thư viện ở phiếu này), `app/**`.

## Yêu cầu

1. Đặt pillow-heif giải mã một luồng (`DECODE_THREADS = 0` hoặc cách tương đương có trong 1.8.1) ở đúng chỗ đăng ký HEIF, trước mọi lần mở ảnh; giữ các tùy chọn tắt ảnh nhỏ, ảnh độ sâu, ảnh phụ hiện có.
2. Xét thêm giới hạn thời gian/kích thước giải mã HEIC (ô lưới, số ô) để giảm lỗi «treo CPU» nếu làm được trong phạm vi; nếu không, ghi rõ trong báo cáo.
3. Ảnh HEIC thật (thư mục ảnh mẫu, ảnh iPhone) vẫn đọc đúng, giữ GPS, xoay đúng; tốc độ chấp nhận được (ghi số đo).
4. Mọi test ảnh, HEIF, T-047, T-058, T-080 cũ vẫn qua.
5. Báo cáo ghi rõ: phiên bản pillow-heif, libheif hiện tại; cách kiểm khi có bản mới để nâng (cho chủ dự án duyệt sau).

## Yêu cầu bảo mật riêng

F1, F2, S1 (thư viện).

## Tiêu chí xong

- [ ] Yêu cầu 1–5
- [ ] Test liên quan + `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-107-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (F1, F2, S1).

## Ghi chú của Chỉ Huy

- Lập 2026-10-30 theo đề xuất Lá Chắn T-093 (việc 1 để đóng Giai đoạn 3) và chỉ đạo «vấn đề nào có đề xuất thì làm theo đề xuất».
- 2026-10-30 17:23 (Chỉ Huy B): Soi Lỗi ĐẠT CÓ ĐIỀU KIỆN (`f68a206`); lượt 2 (`28f4a4d`, SL-T107-1, -2); Lá Chắn ĐẠT CÓ ĐIỀU KIỆN (`a9d381e`): LC-T093-3 đóng, gộp `main` được. Còn 2 Trung bình có từ trước: LC-T107-1 (HEIC có ảnh phụ alpha lớn) → lượt 3 cách (a), Chỉ Huy duyệt đổi ca `test_soi_loi_t049.py::…[heic-trong-suot]`; LC-T107-2 (libheif 1.23.6 còn 5 lỗi làm treo, vá ở 1.23.7) → **chủ dự án chọn tạm không nhận HEIC** (30/10 14:15): lượt 3 làm công tắc tắt HEIC, giữ mã để bật lại khi nâng.

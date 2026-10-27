# T-082 · Sửa câu báo đọc ảnh khi bị tráo thư mục (SL-T080-1, -2, -L-1)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-23 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Thấp (làm sau T-056; không chặn T-056) |
| Phụ thuộc | T-080 đã gộp vào `main`; T-056 xong |
| Trạng thái | Xong |

## Mục tiêu

Khi thư mục ảnh bị dời hay tráo đúng lúc app đọc, app báo "vừa bị thay đổi, hãy thử lại" thay vì các câu sai nghĩa ("Không đọc được… không có quyền hoặc ổ đĩa vừa bị ngắt", "nằm ngoài thư mục ảnh"). Chỉ sửa câu chữ; các lớp chặn giữ nguyên.

## Bối cảnh

- Báo cáo Soi Lỗi T-080 phần Windows (`docs/team/reports/T-080-soi-loi.md`, mục Lỗi mới): **SL-T080-1**, **SL-T080-2** (Thấp, có từ trước T-080, chỉ sai câu báo; SL-T080-2 nên làm cùng LC-T048-2, -3 nếu có phiếu đó).
- Báo cáo Soi Lỗi T-080 phần Linux (`docs/team/reports/T-080-soi-loi-linux.md`): **SL-T080-L-1** (Thấp: câu "nằm ngoài thư mục ảnh" thay "vừa bị thay đổi"); Soi Lỗi Windows xác nhận lỗi này cũng có trên Windows.
- Biên bản Lá Chắn T-080 (`docs/team/reports/T-080-la-chan.md`): mức và điều kiện cho các lỗi trên, ghi chú `_resolve_inside` nếu có.
- Chủ dự án duyệt 2026-10-23: lập phiếu dọn riêng, làm sau màn hình chọn ảnh T-056.

## Phạm vi

- **Được sửa:** `seo_app/images/folders.py`, `tests/test_images_folders.py`; gỡ `xfail` trong `tests/test_soi_loi_t080.py`, `tests/test_soi_loi_t080_linux.py` (chỉ xóa dấu).
- **Không được sửa:** `app/**`, `config/**`, `seo_app/storage/**`.

## Yêu cầu

1. Sửa SL-T080-1, SL-T080-2, SL-T080-L-1 theo cách gợi ý trong các báo cáo trên (và điều kiện của Lá Chắn T-080 nếu có).
2. Không nới lớp chặn nào của T-048, T-076, T-079, T-080; ép thắng và tráo thật vẫn 0 lọt.
3. Gỡ `xfail` khi XPASS; ca chỉ chạy trên Linux/Mac cần một lượt cloud Linux (hoặc ghi rõ chưa kiểm được).

## Yêu cầu bảo mật riêng

F1.

## Tiêu chí xong

- [ ] Yêu cầu 1–3
- [ ] Test liên quan (`uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_images_folders_t063.py tests/test_soi_loi_t079.py tests/test_la_chan_t079.py tests/test_soi_loi_t080.py`) qua và `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy trên Windows khi gộp
- [ ] Có test cho phần logic mới
- [ ] Báo cáo nộp tại `docs/team/reports/T-082-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn (Windows + cloud Linux nếu có ca chỉ chạy trên Linux). Lá Chắn: Rút gọn (F1).

## Ghi chú của Chỉ Huy

- Lập theo đề xuất của Soi Lỗi T-080 (Windows và Linux); chủ dự án chọn phiếu dọn sau thay vì chỉ ghi nhận (2026-10-23).
- 2026-10-23 14:32 (Chỉ Huy B): thêm điều kiện 2 của Lá Chắn T-080: ghi chú/làm chặt `_resolve_inside`, `_checked_file` (Việc 4 (a) bắt buộc, (b) nên làm, xem `docs/team/reports/T-080-la-chan.md`); chỉ đổi câu báo, mọi ca vẫn từ chối (`_ChangedError` là `_LinkError`); Windows giữ `_MSG_ALIAS` cho tên ngắn 8.3 thật; ép thắng (ổ máy và `\\localhost\C$`) vẫn 0 lọt.
- 2026-10-27 17:35 (Chỉ Huy B): chủ dự án duyệt làm ngay. Nhánh `team/T-082` từ `main` `b60054f`, worktree `wt-T-082`; giao Thợ Máy (phiên mới). Chạy song song T-082, T-083, T-084 (khác file). Ca chỉ chạy trên Linux: không chạy cloud (chủ dự án chưa đồng ý), ghi rõ chưa kiểm được.
- 2026-10-28 02:40 (Chỉ Huy B): Thợ Máy 2 lượt (`453208b`), Soi Lỗi ĐẠT CÓ ĐIỀU KIỆN (SL-T082-1, -2 sửa ở lượt 2), Lá Chắn rút gọn ĐẠT (`38006d4`). **Đã gộp `main`** (Windows 15.352 test qua, 0 hỏng); xóa nhánh `team/T-082`, worktree `wt-T-082`. 6 ca `tests/test_soi_loi_t080_linux.py` (chỉ chạy Linux/Mac) dự đoán XPASS, chưa chạy vì chưa được chạy cloud: lượt Linux/Mac đầu tiên phải gỡ 6 dấu đó.

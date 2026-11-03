# T-119 · Tài liệu sau rà soát Fable: cách chạy `pip-audit`, sổ rủi ro, README mục Google, chú thích `uvx`

| Mục | Nội dung |
|---|---|
| Giao cho | Thư Ký (`thu-ky`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-02 |
| Giai đoạn | Chung (tài liệu bảo mật) |
| Mức ưu tiên | Thấp |
| Phụ thuộc | T-116 nhóm 1, 3, 4 đã gộp `main` |
| Trạng thái | Xong (gộp `main` 2026-11-03) |

## Mục tiêu

Ghi vào tài liệu các việc hành chính Lá Chắn (Fable, T-116) và Lá Chắn T-078 nêu, không đổi code.

## Việc

1. `docs/team/security.md` §5: cách chạy `pip-audit` khi `pillow` bị ép bản 13 (`uvx pip-audit -r` thường hỏng vì xung đột `pillow<13` ↔ 13.0.0 có chủ đích): `uv export --no-hashes > tạm.txt` (hoặc như biên bản T-116 nhóm 1) rồi `uvx pip-audit -r tạm.txt --no-deps --disable-pip`; nhắc kiểm `uv --version` ≥ 0.13.4 trước khi dùng `uvx` (LC-T078-1).
2. `docs/team/security.md` §6 (sổ rủi ro): hai đề nghị «ghi sổ» của lớp AI mà biên bản T-116 nhóm 3 nêu (T-016-020 #5 `parse_stream`, T-022-024 #3) — đọc biên bản để ghi đúng nội dung, mức, lý do chấp nhận.
3. `README.md` mục Google: đối chiếu với code hiện tại (LC-T094-43, biên bản T-116 nhóm 4): cách tạo tài khoản dịch vụ, chia sẻ Sheet, chỗ khai báo file khóa, nút «Kiểm tra kết nối», «Chuẩn bị trang tính», «Cập nhật trạng thái từ website» (T-113); sửa chỗ lệch.
4. `pyproject.toml`: chú thích ở `[tool.uv] required-version` nói rõ không áp cho `uvx` / `uv tool run` (LC-T078-1); chỉ sửa chú thích.

## Phạm vi

- **Được sửa:** `docs/team/security.md`, `README.md`, chú thích trong `pyproject.toml`.
- **Không được sửa:** code, `uv.lock`, giá trị trong `pyproject.toml`.

## Tiêu chí xong

- [ ] Việc 1–4
- [ ] `detect-secrets` (`PYTHONUTF8=1`) sạch; `uv run ruff check .` (nếu đụng `pyproject.toml`)
- [ ] Báo cáo `docs/team/reports/T-119-thu-ky.md`

## Kiểm thử và kiểm định

- Soi Lỗi: không. Lá Chắn: xem nhanh mục 1, 2 (đúng cách chạy, đúng mức) khi rảnh.

## Ghi chú của Chỉ Huy

- Lập 2026-11-02 theo biên bản T-116 nhóm 1, 3, 4 và T-078. Hai giới hạn `modified_gmt` của T-115 ghi sổ sau khi Lá Chắn T-115 kết luận.
- 2026-11-03 12:33 (Chỉ Huy B): Thư Ký (`6f707a9`, `5f695a5`): 4 việc xong; README chưa từng có mục Google nên viết mục 14 mới; 2 dòng sổ rủi ro chủ dự án đồng ý 02/11. Gộp `main` (`33dd87f`), Windows 22.300 test qua, 0 hỏng.

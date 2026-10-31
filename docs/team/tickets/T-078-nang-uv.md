# T-078 · Nâng công cụ `uv` lên 0.13.4 trở lên (GHSA-hq85-5cpj-mr62)

| Mục | Nội dung |
|---|---|
| Giao cho | Chủ dự án + Chỉ Huy (nâng `uv` trên 2 máy); Thợ Máy (`required-version`); Thư Ký (README) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-21 |
| Giai đoạn | Chung (bảo mật toàn máy) |
| Mức ưu tiên | **Cao** (Lá Chắn T-075, LC-T075-1) |
| Phụ thuộc | Chủ dự án duyệt nâng `uv` 2026-10-21 13:39 |
| Trạng thái | Xong (gộp `main` 2026-10-31; máy Mac: khi có máy) |

## Mục tiêu

Công cụ `uv` trên cả 2 máy không còn tin gốc chứng chỉ «emSign ECC Root CA - G3», nên không ai giả được kho gói Python để cài mã độc khi agent chạy `uvx`, `uv run --with`, `uv lock --upgrade-package`.

## Bối cảnh

Biên bản Lá Chắn T-075 (`docs/team/reports/T-075-la-chan.md`, mục «Phát hiện toàn repo», LC-T075-1, mức **Cao**, có từ trước): `uv` dưới 0.13.4 mang bộ chứng chỉ riêng còn gốc G3 (GHSA-hq85-5cpj-mr62, vá ở 0.13.4). Máy Windows của chủ dự án đang chạy `uv 0.12.23`; máy Mac chưa biết bản nào. Mở app hằng ngày không bị vì `uv sync` kiểm mã băm theo `uv.lock`.

## Phạm vi

- **Trên máy:** `uv self update` trên máy Windows và máy Mac (làm ở mạng nhà hoặc công ty), rồi `uv --version` ≥ 0.13.4.
- **Được sửa (Thợ Máy):** `pyproject.toml` (chỉ thêm `[tool.uv] required-version = ">=0.13.4"`), test nhỏ nếu cần.
- **Được sửa (Thư Ký):** `README.md` mục cài đặt và «Xử lý sự cố»: cách nâng `uv`, câu báo khi `uv` quá cũ.
- **Không được sửa:** `uv.lock`, code ứng dụng.

## Yêu cầu

1. Cả 2 máy: `uv --version` ≥ 0.13.4 (ghi kết quả vào báo cáo).
2. `required-version` trong `pyproject.toml`; `uv sync` với `uv` cũ báo lỗi rõ ràng (thử bằng tài liệu hoặc máy đã biết bản cũ, không hạ cấp máy thật).
3. README hướng dẫn nâng `uv` bằng tiếng Việt.

## Yêu cầu bảo mật riêng

D1, D3.

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (D1); đối chiếu 8 chứng chỉ trung gian bị lộ với danh sách chặn của Windows và macOS (đề xuất của Lá Chắn T-075).

## Ghi chú của Chỉ Huy

- Lập theo đề xuất của Lá Chắn T-075. Lời dặn «không dùng Wi-Fi công cộng» bỏ được khi đủ 3 việc: T-075 gộp và cả 2 máy mở lại app; cả 2 máy nâng `uv` ≥ 0.13.4; Windows và macOS đã cập nhật như thường lệ.
- 2026-10-21 13:39 (Chỉ Huy B): chủ dự án duyệt. Máy Windows: `uv self update` từ 0.12.23 lên **0.13.4** (Chỉ Huy chạy). Máy Mac: chủ dự án tự chạy `uv self update`. Phần `required-version` (Thợ Máy) và README (Thư Ký) chưa giao.
- 2026-10-22 09:01 (Chỉ Huy B): Chủ dự án báo 2026-10-22: **hiện chưa có máy Mac**. Bỏ bước nâng `uv` trên Mac cho tới khi có máy Mac. Máy Windows đã xong (0.13.4). Phần `required-version` (Thợ Máy) và README (Thư Ký) vẫn chưa giao.
- 2026-10-30 22:24 (Chỉ Huy B): thêm vào phần Thư Ký: README và danh sách đuôi ảnh vẫn ghi nhận AVIF nhưng app không mở được AVIF (Thợ Máy, Soi Lỗi T-107 lượt 3 xác nhận, có từ trước): bỏ câu AVIF khỏi README (phần bỏ AVIF khỏi danh sách đuôi giao Thợ Máy cùng `required-version`).
- 2026-10-31 13:32 (Chỉ Huy B): Thợ Máy (`1ebf679`), Thư Ký 2 lượt (`10d33f4`, `12c2a3d`), Soi Lỗi ĐẠT (`517f178`), Lá Chắn ĐẠT CÓ ĐIỀU KIỆN (`09a5569`): LC-T075-1 đóng trên Windows; LC-T078-1 (`required-version` không chặn `uvx` → quy tắc kiểm `uv --version` trong `security.md`, `la-chan.md`, README), LC-T078-2 (nâng `uv` ở mạng tin cậy) đã sửa; LC-T078-3 (`pyasn1`) → T-114. Gộp `main`, Windows 21.819 test qua. Còn: máy Mac nâng `uv` khi có máy.

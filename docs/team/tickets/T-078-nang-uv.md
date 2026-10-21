# T-078 · Nâng công cụ `uv` lên 0.13.4 trở lên (GHSA-hq85-5cpj-mr62)

| Mục | Nội dung |
|---|---|
| Giao cho | Chủ dự án + Chỉ Huy (nâng `uv` trên 2 máy); Thợ Máy (`required-version`); Thư Ký (README) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-21 |
| Giai đoạn | Chung (bảo mật toàn máy) |
| Mức ưu tiên | **Cao** (Lá Chắn T-075, LC-T075-1) |
| Phụ thuộc | Nâng công cụ: chờ chủ dự án duyệt (`rules.md` mục 4) |
| Trạng thái | Chờ chủ dự án duyệt |

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

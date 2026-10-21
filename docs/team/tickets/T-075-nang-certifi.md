# T-075 · Nâng `certifi` lên 2026.10.19 (lỗ hổng GHSA-6q48-6c7w-9gw2)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-21 |
| Giai đoạn | Chung (bảo mật toàn repo) |
| Mức ưu tiên | **Cao, gấp** (Lá Chắn T-061, LC-T061-1) |
| Phụ thuộc | Không. Nâng thư viện: chờ chủ dự án duyệt (`rules.md` mục 4) |
| Trạng thái | Chờ chủ dự án duyệt |

## Mục tiêu

App không còn tin các chứng chỉ do khóa bị lộ của eMudhra ký, nên không ai giả được suachuacuasat.com hay máy chủ Gemini để lấy mật khẩu ứng dụng WordPress, khóa Gemini.

## Bối cảnh

Lá Chắn T-061 (`docs/team/reports/T-061-la-chan.md`, mục «Phát hiện toàn repo», LC-T061-1, mức **Cao**, có sẵn trên `main`, không do T-061):

- `uv.lock` đang khóa `certifi` 2026.7.22. Bộ chứng chỉ này còn gốc «emSign ECC Root CA - G3»; 8 chứng chỉ trung gian dưới gốc này bị lộ khóa riêng (GHSA-6q48-6c7w-9gw2 = PYSEC-2026-4320, công bố 2026-10-20; ảnh hưởng `>= 2019.03.09, < 2026.10.19`; vá ở **2026.10.19**).
- Client WordPress (`requests`) và Gemini (`google-genai`) dùng `certifi.where()`; mỗi lệnh WordPress gửi Application Password, mỗi lệnh Gemini gửi khóa API.
- Lá Chắn đã thử trên bản sao: `uv lock --upgrade-package certifi` chỉ đổi đúng thư viện này; `pip-audit` (PyPI và OSV) sạch.

## Phạm vi

- **Được sửa:** `uv.lock` (chỉ `certifi`), test mới nhỏ chốt phiên bản (ví dụ `tests/test_certifi_version.py`).
- **Không được sửa:** `pyproject.toml` (trừ khi `uv` bắt buộc; ghi lý do), code ứng dụng, thư viện khác.

## Yêu cầu

1. `uv lock --upgrade-package certifi` → `certifi` ≥ 2026.10.19; `git diff uv.lock` chỉ đổi khối `certifi`.
2. Test chốt: `certifi` ≥ 2026.10.19 và `certifi.where()` không còn nhãn «emSign ECC Root CA - G3».
3. `uvx pip-audit` (hoặc tương đương) trên toàn `uv.lock`: dán kết quả vào báo cáo.

## Yêu cầu bảo mật riêng

D1, D3.

## Tiêu chí xong

- [ ] Đạt yêu cầu 1–3, có test
- [ ] Test liên quan (test mới, test client WordPress và lớp AI) qua và `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy trên Windows khi gộp
- [ ] Báo cáo nộp tại `docs/team/reports/T-075-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (D1).

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 1 của Lá Chắn T-061. **Hạn:** trước T-059 (thử thật) và trước khi gộp T-056. Sau khi gộp: cả 2 máy mở app bằng `run.bat` / `run.command` (tự `uv sync`). Trong lúc chờ: không dùng app trên Wi-Fi công cộng.

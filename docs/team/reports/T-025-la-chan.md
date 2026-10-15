# Biên bản bảo mật T-025 · Ổn định các test đo tốc độ chập chờn

> **Model:** lần này Lá Chắn chạy **tạm bằng Claude Opus 5.5** ("Opus tạm"), không phải Fable 5.1 như hồ sơ vai yêu cầu (Fable bị giới hạn tới 01/11; chủ dự án đã duyệt). Đề nghị kiểm lại bằng Fable sau 01/11 cùng đợt với các phiếu Opus tạm khác.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (Opus tạm, xem trên) |
| Phiếu được kiểm | [T-025](../tickets/T-025-on-dinh-test-do-toc-do.md) |
| Phạm vi | Mức **rút gọn**. `git diff origin/main...team/T-025` (gốc chung `e6d5b69`, nhánh `a36a943`). Code: `5ff60f3`, `a1d48d4`, `ee41ccb`; báo cáo Soi Lỗi `a36a943` |
| Ngày | 2026-10-15 |
| **Kết luận** | **ĐẠT** |

## Tóm tắt (cho chủ dự án)

Phiếu này chỉ sửa công cụ đo tốc độ dùng trong test, **không đụng code của app**. Không có khóa, mật khẩu hay đường dẫn máy cá nhân; test mới dùng "đồng hồ giả" nên không gọi mạng, AI, WordPress hay Google. Kiểm tra không bị nới lỏng: ngưỡng 9 lần giữ nguyên, không bỏ qua test nào, code chạy chậm kiểu bình phương vẫn bị bắt, thậm chí chặt hơn trước.

## Xác nhận phạm vi

```
$ git diff origin/main...HEAD --stat
 docs/team/reports/T-025-soi-loi.md | 116 +++++
 tests/test_soi_loi_t025.py         | 115 +++++
 tests/timing.py                    |  24 ++++--
```

Không có `seo_app/`, `app/`, `scripts/`, `config/`, `pyproject.toml`, `uv.lock` hay `.claude/` bị sửa.

## Lỗi phát hiện

Không phát hiện lỗi.

## Soát theo yêu cầu rút gọn

| Mục | Kết quả | Bằng chứng |
|---|---|---|
| Bí mật | Đạt | Tìm `sk-`, `api_key`, `password`, `secret`, `token`, `/home/`, `/Users/`, `C:\` trong diff và trong toàn bộ patch của các commit nhánh: không có. `detect-secrets` trên 3 file: `"results": {}`. Báo cáo Soi Lỗi chỉ có số đo, tên test và lệnh chạy, không có đường dẫn máy |
| D3 / R4 (không gọi mạng thật) | Đạt | `tests/timing.py` chỉ dùng `gc`, `time`. `tests/test_soi_loi_t025.py` chỉ dùng `pytest`, `timing`; thay `timing.time` bằng đồng hồ giả qua `monkeypatch` (`tests/test_soi_loi_t025.py:31-32`), hàm đo là hàm giả cộng giờ ảo. Không có `socket`, `requests`, `httpx`, `urllib`, không gọi `seo_app`. Bộ chặn mạng trong `tests/conftest.py` vẫn áp dụng |
| R5 (không nới lỏng) | Đạt | `MAX_RATIO = 9.0` giữ nguyên (`tests/timing.py:33`), có test khóa cứng (`tests/test_soi_loi_t025.py:112-115`, gồm cả `MIN_MEASURE >= 0.1`). Không có `skip`, `xfail`, `rerun`, `flaky` trong diff. Phép so cuối `ratio <= MAX_RATIO` và mốc `MAX_SECONDS` vẫn giữ (`tests/timing.py:78-79`). Xem phân tích dưới |
| Tiến trình con / file tạm | Không áp dụng | Diff không tạo tiến trình con, không dùng `tempfile`/`tmp_path`, không ghi file. Script đo nhiều tiến trình mà Soi Lỗi dùng để lấy số liệu nằm ngoài repo, không thuộc diff |

**Phân tích R5 (đã đọc code, không chỉ dựa vào báo cáo):** thời gian CPU chỉ bị đo dài ra khi máy bận, không ngắn đi. Bản mới đo cỡ nhỏ tới 4 lần (trước 2) và lấy lần nhanh nhất: `t_small` chỉ có thể nhỏ hơn hoặc bằng trước, nên tỉ lệ chỉ tăng, tức là bắt hàm chậm **chặt hơn**. Cỡ lớn vẫn đo tối đa 3 lần như code cũ, không thêm cơ hội "đo may" cho hàm chậm. Vòng 1 dừng sớm ở `CLEAR_RATIO = 6` (trước là 9), cũng chặt hơn. Việc đo thêm xảy ra **trong một lần gọi helper**, kết quả cuối vẫn phải ≤ 9 nếu không thì báo lỗi; đây không phải "hỏng thì chạy lại". Bản bình phương bị bắt có test: `test_burst_*_quadratic`, `test_ratio_just_above_max_is_caught` (tỉ lệ 9,2), `test_windows_clock_resolution_quadratic_caught`.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Không có bí mật trong diff, báo cáo hay lịch sử nhánh (xem trên) |
| S2 | Không áp dụng | Không in log hay giao diện |
| S3 | Không áp dụng | Không đụng `.env`, `.env.example`, `.gitignore` |
| W1 | Không áp dụng | Không đụng WordPress |
| W2 | Không áp dụng | |
| W3 | Không áp dụng | |
| W4 | Không áp dụng | |
| A1 | Không áp dụng | Không đụng prompt hay lớp AI |
| A2 | Không áp dụng | |
| A3 | Không áp dụng | |
| U1 | Không áp dụng | Không đụng giao diện, đăng nhập |
| U2 | Không áp dụng | |
| U3 | Không áp dụng | |
| F1 | Không áp dụng | Không đọc/ghi file |
| F2 | Không áp dụng | |
| F3 | Không áp dụng | |
| D1 | Không áp dụng | Không thêm thư viện, `uv.lock` không đổi |
| D2 | Không áp dụng | Không có HTTP client |
| D3 | Đạt | Test dùng đồng hồ giả, không socket, không gọi dịch vụ thật |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | Không chạy: phiếu không đổi thư viện (`uv.lock` không nằm trong diff) | Có |
| bandit | 6 cảnh báo B101 (dùng `assert`), mức Low | Có, báo nhầm (xem dưới) |
| detect-secrets | 0 kết quả trên 3 file của diff | Có |
| Soát lịch sử git | `git log origin/main..HEAD -p`: không có `sk-ant`, `AIza`, `password=`, khóa riêng | Có |
| pytest / ruff | `uv run pytest tests/test_soi_loi_t025.py tests/test_soi_loi_round6.py tests/test_soi_loi_round7.py`: **121 passed in 21.23s**. `uv run ruff check .`: **All checks passed!** | Có, tự chạy |

## Báo nhầm đã loại

- **bandit B101** (`tests/timing.py:62,78,79`, `tests/test_soi_loi_t025.py:113-115`): `assert` là cách báo lỗi chuẩn của pytest, chỉ chạy trong test, không phải code ứng dụng.

## Ghi chú (không phải điều kiện)

- Phần đồng hồ Windows mới kiểm bằng đồng hồ giả; Soi Lỗi đã đề nghị chạy 100 lần trên máy Windows của chủ dự án. Đây là việc về độ ổn định của test, không ảnh hưởng bảo mật, nên không đặt làm điều kiện.
- `origin/main` đã tiến tới `f013a27` sau gốc chung `e6d5b69`. Khi gộp, Chỉ Huy nên gộp `main` vào nhánh và chạy lại `uv run pytest` một lượt.

## Điều kiện (nếu ĐẠT CÓ ĐIỀU KIỆN)

Không có.

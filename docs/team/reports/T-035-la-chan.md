# Biên bản bảo mật T-035 · README và chú thích `config/ai.toml`: 3 hãng AI, thử mù

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **Opus tạm** (Claude Opus 5.5; Fable bị giới hạn tới 01/11, chủ dự án duyệt chạy tạm) |
| Phiếu được kiểm | [T-035](../tickets/T-035-readme-ai-3-hang-thu-mu.md) |
| Phạm vi | Kiểm định **rút gọn**: diff `git diff main...team/T-035` = `cbfe37a..8cc4781` (3 commit: `44a565d`, `21cf502`, `8cc4781`). File: `README.md`, `config/ai.toml`, `docs/team/reports/T-035-thu-ky.md` |
| Ngày | 2026-10-16 |
| **Kết luận** | **ĐẠT** |

## Tóm tắt (cho chủ dự án)

Phiếu chỉ sửa tài liệu và dòng chú thích, an toàn. Không có khóa thật hay khóa mẫu, không có đường dẫn máy cá nhân. File `config/ai.toml` chỉ đổi dòng `#`, giá trị cấu hình giữ nguyên. README chỉ dẫn tới trang chính thức của 3 hãng, chỉ dạy nhập khóa trong **Cài đặt → 🔌 Kết nối**, không dạy làm gì mất an toàn và không nêu giá tiền.

## Lỗi phát hiện

Không phát hiện lỗi.

## Soát theo yêu cầu của phiếu

| Mục soát | Kết quả | Bằng chứng |
|---|---|---|
| Chỉ 3 file trong phạm vi bị đổi | Đạt | `git diff --name-only main...HEAD`: chỉ `README.md`, `config/ai.toml`, `docs/team/reports/T-035-thu-ky.md`. Không đụng code, test, `.env.example` |
| `config/ai.toml` chỉ đổi dòng `#` | Đạt | `git diff -U0` lọc bỏ dòng `#`: không còn dòng `+`/`-` nào |
| `tomllib` đọc như `main` | Đạt | So `tomllib.loads(main:config/ai.toml) == tomllib.load(config/ai.toml)` → `True`; đủ 5 việc `outline, research, review, rewrite, write` |
| Link trong README | Đạt | Link mới chỉ có `https://console.anthropic.com`, `https://platform.openai.com/api-keys`, `https://aistudio.google.com/apikey`; trùng với `API_KEY_FIELDS` ở `app/views/settings.py:15-21`. Không có tên miền lạ |
| Không dạy tắt SSL | Đạt | Không có `verify`, `ssl`, `SSL` trong dòng thêm |
| Không dạy đổi `*_BASE_URL` | Đạt | Không có `BASE_URL` trong dòng thêm. Câu lỗi Gemini về khu vực khuyên "tắt VPN hoặc proxy … hoặc đổi sang hãng khác" (README mục 7.6), không khuyên đổi máy chủ |
| Không dạy đặt `*_CUSTOM_HEADERS` | Đạt | Không có trong dòng thêm |
| Khóa chỉ nhập ở Cài đặt → 🔌 Kết nối / `.env` | Đạt | README mục 5 và 7.1, bảng lỗi 7.6 đều hướng về **Cài đặt → 🔌 Kết nối**; ghi rõ "Khóa nằm trong `.env` của từng máy, nên máy thứ hai cần nhập lại một lần" (không bảo gửi `.env` sang máy khác hay cho người khác) |
| Không nêu giá tiền | Đạt | Không có con số giá; README mục 7.1 hướng xem trang giá của hãng |

## Danh sách kiểm tra

Kiểm định rút gọn: chỉ S1, S3 là trọng tâm; các dòng khác không áp dụng vì diff không có code.

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Quét dòng thêm trong cả 3 commit (`git log -p main..HEAD`) với mẫu `sk-…`, `sk-ant-…`, `AIza…`, `private_key`, `BEGIN … PRIVATE`: không có. Không có `/home/`, `/Users/`, `C:\` trong dòng thêm. `detect-secrets` trên 3 file: `results: {}` |
| S2 | Không áp dụng | Không có code in lỗi/log |
| S3 | Đạt | Không có biến cấu hình mới; `.env.example` không đổi. Ví dụ trong README chỉ là tên biến (`ANTHROPIC_API_KEY`…), không có giá trị |
| W1 | Không áp dụng | Không đụng `seo_app/wordpress/` |
| W2 | Không áp dụng | |
| W3 | Không áp dụng | |
| W4 | Đạt | Tài liệu không dạy tắt SSL hay đổi URL máy chủ (xem bảng trên) |
| A1 | Không áp dụng | Không đổi prompt |
| A2 | Không áp dụng | |
| A3 | Không áp dụng | |
| U1 | Không áp dụng | Không đổi giao diện |
| U2 | Không áp dụng | |
| U3 | Không áp dụng | |
| F1 | Không áp dụng | |
| F2 | Không áp dụng | |
| F3 | Không áp dụng | |
| D1 | Không áp dụng | `pyproject.toml`, `uv.lock` không đổi |
| D2 | Không áp dụng | `.gitignore` không đổi |
| D3 | Không áp dụng | Không có test mới |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | Không chạy: phiếu không đổi thư viện | Có (`uv.lock` không trong diff) |
| bandit | Không chạy: không có code Python trong diff | Có |
| detect-secrets | 0 kết quả trên `README.md`, `config/ai.toml`, `docs/team/reports/T-035-thu-ky.md` | Có |
| Soát lịch sử git | 3 commit trên nhánh: không có mẫu khóa, không có đường dẫn máy cá nhân | Có |
| pytest / ruff | `uv run pytest tests/test_app_pages.py tests/test_config_tolerance.py`: 62 passed. `uv run ruff check .`: All checks passed! | Có |

## Báo nhầm đã loại

Không có.

## Điều kiện (nếu ĐẠT CÓ ĐIỀU KIỆN)

Không có.

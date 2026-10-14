# Báo cáo T-020 · Nhập khóa API AI ngay trong app (phần Họa Sĩ)

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | [T-020](../tickets/T-020-nhap-khoa-api-trong-app.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Trong **Cài đặt → 🔌 Kết nối** giờ có 3 thẻ: Claude, ChatGPT, Gemini. Mỗi thẻ cho biết khóa đã khai báo hay chưa, có link tới trang lấy khóa, một ô để dán khóa (hiện dấu chấm), và các nút **Lưu**, **Kiểm tra** (chỉ Claude), **Xóa** (hỏi lại một lần). Lưu xong ô nhập tự trống và trạng thái đổi ngay. Khóa đã lưu không bao giờ hiện lại, kể cả vài ký tự cuối. Các kết nối khác (WordPress, Google…) vẫn hiện bên dưới như cũ.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `app/views/settings.py` | Tab "🔌 Kết nối": 3 thẻ khóa API dùng `seo_app/env_file.py`; danh sách kết nối khác giữ nguyên (bỏ 3 dòng AI vì đã có thẻ riêng) |
| `tests/test_settings_keys.py` | Mới: 12 test giao diện, `.env` trỏ sang `tmp_path` riêng từng test, `check_api_key` được giả |

Không sửa `seo_app/env_file.py`, `app/views/write.py`, `tests/conftest.py`. Không thêm thư viện.

## Bằng chứng

```
$ uv run pytest tests/test_settings_keys.py -q
12 passed in 4.04s

$ uv run pytest -q
1711 passed, 3 xfailed in 92.59s

$ uv run ruff check .
All checks passed!
```

Tự kiểm tra trên app: bấm đúp `run.bat` / `run.command` → đăng nhập → **Cài đặt** → tab **🔌 Kết nối**. Dán khóa Claude → **Lưu** → thấy "Đã lưu khóa Claude vào file .env.", nhãn đổi thành "✅ Đã khai báo", ô nhập trống → bấm **Kiểm tra** (chờ tối đa 15 giây).

## Đối chiếu tiêu chí xong

1. [x] Ba ô nhập `type="password"`, kèm link lấy khóa như `.env.example` (`app/views/settings.py:84-92`, `:76`). Test: `test_initial_state_shows_three_cards_not_configured` (kiểm tra kiểu PASSWORD và đủ 3 link).
2. [x] Không bao giờ hiện lại khóa: ô nhập luôn bắt đầu trống (không có `value`), trạng thái chỉ là huy hiệu "Đã khai báo / Chưa khai báo", thông báo là câu cố định hoặc lỗi của `EnvFileError` (đã không chứa khóa), kết quả kiểm tra lưu trong `session_state` chỉ là `(status, message)`. Hàm kiểm tra được gọi **không truyền khóa** (`:112`). Test `assert_key_nowhere` dò toàn bộ chữ trên trang và toàn bộ `session_state`, tìm cả khóa đầy đủ lẫn 4 và 6 ký tự cuối: dùng trong `test_save_writes_env_clears_input_and_never_shows_key`, `test_save_keeps_other_lines`, `test_clear_asks_once_then_clears`, `test_os_environ_override_warning`, `test_check_shows_result`, `test_saving_new_key_resets_old_check_result`; `test_invalid_value_rejected_and_cleared` kiểm tra cả giá trị cố chèn `APP_PASSWORD_HASH`.
3. [x] Nút Lưu; Xóa hỏi lại một lần ("Xóa thật" / "Thôi"); Kiểm tra chỉ bật cho Claude khi đã có khóa, ChatGPT/Gemini tắt kèm chú thích "chờ cài thư viện của hãng". Kết quả: `ok` → xanh, `invalid` → đỏ, còn lại (`unknown`, …) → vàng. Test: `test_clear_asks_once_then_clears`, `test_check_only_for_claude`, `test_check_shows_result[ok|invalid|unknown]`.
4. [x] Lưu bằng callback `on_click` (`:31`): đọc giá trị, **xóa ngay** khỏi ô nhập/`session_state` (`:35`) rồi mới ghi, dù lưu được hay lỗi. Cấu hình được đọc lại sau callback (`settings = load_settings()` ở `:154`), nên trạng thái đổi trong cùng lần bấm. Lưu/xóa khóa cũng bỏ kết quả kiểm tra cũ. Test: `test_save_writes_env_clears_input_and_never_shows_key`, `test_invalid_value_rejected_and_cleared`, `test_saving_new_key_resets_old_check_result`.
5. [x] Nếu biến có trong biến môi trường của máy thì thẻ đó hiện cảnh báo "khóa nhập ở đây sẽ không có hiệu lực" (`:77`). Test: `test_os_environ_override_warning`.
6. [x] Bố cục giữ nguyên (4 tab, link sang trang WordPress); `tests/test_app_pages.py` vẫn qua.

## Rủi ro và điểm cần chú ý

- **Khóa nằm trong `session_state` trong lúc đang gõ** (từ khi dán tới khi bấm Lưu): Streamlit bắt buộc vậy để đọc được ô nhập. Nếu dán xong rồi chuyển trang không bấm Lưu, Streamlit tự bỏ giá trị của ô không còn hiện; đăng xuất thì `S.clear()`. Không bao giờ hiện ra màn hình.
- Ô dùng `autocomplete="off"` để trình duyệt không gợi ý lưu như mật khẩu; một số trình quản lý mật khẩu vẫn có thể hỏi. Không ảnh hưởng an toàn của `.env`.
- Trang Cài đặt vẫn mang nhãn "Bản demo" ở đầu trang vì 3 tab kia còn là demo; tab Kết nối có ghi rõ "Phần này là thật".
- Khóa chỉ lưu vào `.env` của máy đang dùng; máy kia phải nhập lại một lần (đã ghi chú dưới các thẻ). Đúng quyết định đã chốt (bí mật không đồng bộ).

## Đề xuất

- Thư Ký: README mục khóa API có thể thêm "Có thể nhập khóa trong Cài đặt → Kết nối thay vì sửa `.env`".
- Khi T-018 duyệt thư viện OpenAI/Gemini: chỉ cần thêm tên biến vào `CHECKABLE_KEYS` trong `app/views/settings.py` sau khi Thợ Máy thêm nhánh kiểm tra.
- Không cần đổi `seo_app/env_file.py`.

## Câu hỏi cho chủ dự án

Không có.

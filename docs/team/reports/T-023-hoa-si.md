# Báo cáo T-023 · Bật nút Kiểm tra khóa ChatGPT và Gemini trong Cài đặt

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | [T-023](../tickets/T-023-nut-kiem-tra-khoa-openai-gemini.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Ở **Cài đặt → 🔌 Kết nối**, nút **Kiểm tra** giờ bấm được cho cả ba khóa Claude, ChatGPT và Gemini (khi khóa đã lưu). Kết quả hiện ngay dưới thẻ khóa: xanh là dùng được, đỏ là khóa sai, vàng là chưa kiểm được (mất mạng, hãng đang bận...). Khóa không bao giờ hiện ra, kể cả vài ký tự cuối.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `app/views/settings.py` | Bỏ `CHECKABLE_KEYS`; nút Kiểm tra bật khi khóa đã khai báo (`:100-108`). Bỏ câu "chờ cài thư viện của hãng"; chú thích nút mới: chưa lưu khóa thì "Lưu khóa trước rồi mới kiểm tra được." |
| `tests/test_settings_keys.py` | Đổi `test_check_only_for_claude` thành `test_check_buttons_disabled_until_key_saved`; thêm `test_check_enabled_for_all_three_keys` và `test_check_openai_gemini` (2 khóa × 4 trạng thái). |

Không sửa `seo_app/**`, `config/**` hay tab khác. Phần hiện kết quả (`settings.py:146-150`: `ok` → `st.success`, `invalid` → `st.error`, còn lại → `st.warning`) đã đúng từ trước nên giữ nguyên; câu thông báo lấy nguyên từ `check_api_key`, không qua HTML.

## Bằng chứng

```
$ uv run pytest
1996 passed, 3 xfailed in 121.36s (0:02:01)

$ uv run ruff check .
All checks passed!
```

Test mới (`tests/test_settings_keys.py`):
- `test_check_buttons_disabled_until_key_saved`: chưa có khóa thì cả 3 nút Kiểm tra tắt.
- `test_check_enabled_for_all_three_keys`: có đủ 3 khóa thì cả 3 nút bật; câu "chờ cài thư viện" không còn; không khóa nào hiện trên trang hay trong `session_state`.
- `test_check_openai_gemini` (8 trường hợp): bấm Kiểm tra ở thẻ ChatGPT/Gemini gọi `check_api_key` giả **đúng một lần, đúng tên biến, không truyền khóa**; thông báo hiện đúng màu (`ok` xanh, `invalid` đỏ, `unknown`/`missing` vàng), chỉ hiện ở một thẻ; không khóa giả nào lộ ra.
- Test cũ của Claude (`test_check_shows_result`, `test_saving_new_key_resets_old_check_result`) vẫn qua. `tests/test_app_pages.py` vẫn qua.

### Chủ dự án tự kiểm tra trên app

1. Windows: bấm đúp `run.bat` (Mac: `run.command`), đăng nhập.
2. Vào **Cài đặt** → tab **🔌 Kết nối**.
3. Thẻ nào chưa có khóa: nút **Kiểm tra** mờ. Dán khóa vào ô, bấm **Lưu**, nút Kiểm tra sáng lên.
4. Bấm **Kiểm tra** ở thẻ ChatGPT và Gemini: đợi vài giây, thấy khung xanh "Khóa ... dùng được." (hoặc đỏ nếu khóa sai, vàng nếu mất mạng).
5. Thử dán một khóa sai, Lưu, bấm Kiểm tra: phải ra khung đỏ. Nhớ lưu lại khóa đúng sau đó.

## Đối chiếu tiêu chí xong

- [x] Ba nút Kiểm tra hoạt động, có test (`settings.py:100-108`; `test_check_enabled_for_all_three_keys`, `test_check_openai_gemini`, `test_check_shows_result`)
- [x] `uv run pytest` và `uv run ruff check .` sạch (kết quả ở trên)
- [x] Báo cáo nộp tại `docs/team/reports/T-023-hoa-si.md`, kèm hướng dẫn tự kiểm tra

Bảo mật: S2 (không hiện khóa: `assert_key_nowhere` cho cả 3 khóa), U1 (chỉ `st.success`/`st.error`/`st.warning`, không `unsafe_allow_html`), D3 (`check_api_key` được thay bằng hàm giả trong mọi test bấm nút).

## Rủi ro và điểm cần chú ý

- Chú thích nút ghi "không tốn tiền": dựa trên báo cáo T-018 (gọi lấy danh sách mô hình, không tốn token). Nếu Thợ Máy đổi cách kiểm tra sang lệnh có tính phí thì phải sửa câu này.
- Trạng thái `unsupported` (nếu sau này hàm trả lại) sẽ hiện màu vàng, không làm sập trang.

## Đề xuất

Không có.

## Câu hỏi cho chủ dự án

Không có.

## Lượt 2 (2026-10-15) · sửa 2 lỗi mức Thấp của Soi Lỗi

Soi Lỗi kết luận ĐẠT (`docs/team/reports/T-023-soi-loi.md`); Chỉ Huy yêu cầu sửa luôn 2 lỗi Thấp.

| Lỗi | Sửa |
|---|---|
| T023-01: `check_api_key` ném ngoại lệ lạ thì trang sập, có thể hiện nguyên thông điệp (chứa khóa) | `app/views/settings.py`: bọc lời gọi trong `try/except Exception`; lỗi bất ngờ hiện câu cố định màu vàng "Không kiểm tra được khóa (<tên loại lỗi>). Thử lại sau." Không hiện `str(exc)`, không dùng `st.exception`. |
| T023-02: câu kết quả hiện nguyên, chỉ dựa vào `check_api_key` tự che | Cho câu kết quả qua `redact_secrets` (`seo_app.ai.base`) thêm một lần trước khi lưu vào `session_state` và hiện lên trang. |

Test:
- Bỏ dấu `xfail(strict=True)` của đúng 2 test (nay qua): `tests/test_soi_loi_t023.py::test_message_containing_key_is_not_shown` (T023-02) và `tests/test_soi_loi_t023.py::test_unexpected_exception_does_not_crash_or_leak` (T023-01). Không đụng test khác của Soi Lỗi.
- Sửa câu giả trong test của chính tôi, `tests/test_settings_keys.py::test_check_openai_gemini`: câu cũ "Kết quả giả OPENAI_API_KEY: ok." bị `redact_secrets` che đúng luật (chuỗi `api_key:` + giá trị), nên đổi thành "Kết quả giả OPENAI: ok.". Câu thật của `check_api_key` (ví dụ "Khóa Claude dùng được.") không chứa mẫu này nên không bị che nhầm. Kiểm tra trong test giữ nguyên.

Bằng chứng:

```
$ uv run pytest
2040 passed, 3 xfailed in 110.26s (0:01:50)

$ uv run ruff check .
All checks passed!
```

(3 xfailed còn lại là test có sẵn ở chỗ khác, không thuộc T-023: `tests/test_soi_loi_t023.py` không còn `xfail` nào.)

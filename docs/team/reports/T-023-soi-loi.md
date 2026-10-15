# Báo cáo T-023 · Kiểm thử nút Kiểm tra khóa ChatGPT và Gemini

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-023](../tickets/T-023-nut-kiem-tra-khoa-openai-gemini.md) |
| Ngày nộp | 2026-10-15 |
| Kết quả | Hoàn thành · **ĐẠT** (mọi yêu cầu của phiếu), kèm 2 lỗi mức Thấp nên sửa |

## Tóm tắt (cho chủ dự án)

Nút **Kiểm tra** của cả 3 khóa (Claude, ChatGPT, Gemini) chạy đúng: chỉ sáng khi khóa đã lưu, báo đúng màu, kết quả nằm đúng thẻ, lưu khóa mới thì kết quả cũ biến mất, khóa không hiện ra ở bất kỳ đâu. Tìm thấy 2 chỗ chưa phòng thủ đủ: nếu phần kiểm tra gặp lỗi lạ chưa lường trước thì trang Cài đặt hiện khung lỗi kỹ thuật (thay vì khung vàng), và giao diện không tự che khóa lần hai. Hiện chưa tìm được tình huống thật nào gây ra hai lỗi này.

Chỉ kiểm phần giao diện T-023; logic T-018 có Soi Lỗi khác kiểm.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t023.py` | Mới: 44 test (38 qua, 6 `xfail(strict=True)` cho 2 lỗi dưới). Không sửa code ứng dụng, không đụng test cũ. |

## Bằng chứng

```
$ uv run pytest            (trước khi thêm test, commit 565040d)
1 failed, 1661 passed, 2 xfailed   (dừng ở lỗi đầu, -x)
  -> tests/test_soi_loi_round7.py::test_many_lookup_inputs_catch_naive_scan[_title_end-...]
     chạy riêng thì qua (3 passed). Test đo tốc độ, chập chờn khi máy bận; không liên quan T-023.

$ uv run pytest            (sau khi thêm test, commit 15f23db)
2034 passed, 9 xfailed in 90.93s

$ uv run ruff check .
All checks passed!
```

Đối chiếu từng yêu cầu Chỉ Huy giao (tên test trong `tests/test_soi_loi_t023.py`):

| Yêu cầu | Test | Kết quả |
|---|---|---|
| Nút bật/tắt theo từng khóa | `test_button_enabled_only_for_configured_key` (3 trường hợp: chỉ 1 khóa có thì chỉ nút đó sáng), `test_help_text_matches_state`, `test_os_environ_key_also_enables_check`, `test_clear_key_disables_check_and_drops_result` | Qua |
| Gọi đúng tên biến, đúng màu | `test_click_calls_right_name_and_color` (3 khóa × 6 trạng thái: `ok` xanh, `invalid` đỏ, `unknown`/`missing`/`unsupported`/trạng thái lạ vàng; gọi đúng 1 lần, không truyền khóa) | Qua |
| Không lộ khóa | Mọi test gọi `assert_no_key`: dò **toàn bộ cây phần tử** (cả nhãn, `help`, chú thích, lỗi) và `session_state`, tìm cả khóa đủ và 4/8 ký tự cuối. `test_end_to_end_real_check_api_key_with_leaky_library`: dùng `check_api_key` thật, giả thư viện 3 hãng ném lỗi chứa khóa → trang hiện khung vàng, không lộ khóa | Qua |
| Kết quả không lạc thẻ | `test_results_stay_in_their_own_card` (bấm cả 3, mỗi thẻ đúng 1 thông báo đúng màu; chạy lại trang không gọi lại máy chủ), `test_check_one_card_does_not_call_others` | Qua |
| Lưu khóa mới xóa kết quả cũ | `test_saving_new_key_drops_only_that_cards_result` (ChatGPT, Gemini: chỉ thẻ vừa lưu mất kết quả, thẻ khác giữ nguyên), `test_failed_save_still_drops_old_result` | Qua |
| `test_app_pages.py` | Chạy cùng: `77 passed, 6 xfailed` (settings_keys + app_pages + file mới) | Qua |
| Ngoại lệ bất ngờ | `test_unexpected_exception_does_not_crash_or_leak` | **Lỗi T023-01** (xfail) |
| | `test_unexpected_exception_after_crash_page_recovers`: lượt sau trang mở lại bình thường | Qua |
| Thông báo dài / Markdown / HTML / rỗng / tiếng Việt | `test_odd_messages_shown_as_plain_alert` (5 trường hợp): hiện bằng khung cảnh báo, không qua `unsafe_allow_html` | Qua |
| Khóa nằm trong câu thông báo | `test_message_containing_key_is_not_shown` | **Lỗi T023-02** (xfail) |

## Lỗi tìm thấy

### T023-01 · Lỗi lạ khi kiểm tra làm trang Cài đặt sập · mức Thấp

- **Tái hiện:** giả `env_file.check_api_key` ném `RuntimeError("lỗi lạ, khóa <khóa>")`, mở Cài đặt → Kết nối, bấm Kiểm tra ở thẻ bất kỳ (`test_unexpected_exception_does_not_crash_or_leak`, chạy với `--runxfail`).
- **Mong đợi:** trang không sập; thẻ hiện khung vàng kiểu "Chưa kiểm tra được khóa (RuntimeError)", không chứa khóa.
- **Thực tế:** trang dừng giữa chừng, hiện khung lỗi kỹ thuật với nguyên thông điệp và traceback: `Exception(message='lỗi lạ, khóa sk-ant-api03-…')`. Nút bấm ở `app/views/settings.py:100-113` không có `try/except`.
- **Đánh giá:** `_check_openai`/`_check_gemini` đã bắt mọi `Exception`; `_check_anthropic` chỉ bắt `AnthropicError`, và phần trước `try` (`_check_name`, `load_settings`, `import`) có thể ném ra ngoài. Tôi đã thử khóa có ký tự tiếng Việt với client Anthropic giả tầng mạng: không ném lỗi. Nên **chưa thấy đường thật** nào gây lỗi; đây là phòng thủ lớp hai. Streamlit mặc định hiện chi tiết lỗi cho người dùng (suy luận từ cấu hình `.streamlit/config.toml` không đặt `client.showErrorDetails`), nên nếu xảy ra thì có thể lộ khóa.
- **Đề xuất (Họa Sĩ):** bọc lời gọi `check_api_key` trong `try/except Exception as exc` và lưu `("unknown", f"Chưa kiểm tra được khóa ({type(exc).__name__}).")`.

### T023-02 · Giao diện không tự che khóa trong câu thông báo · mức Thấp

- **Tái hiện:** giả `check_api_key` trả `KeyCheckResult("invalid", "Khóa <khóa> không đúng.")`, bấm Kiểm tra (`test_message_containing_key_is_not_shown`).
- **Mong đợi:** khóa không hiện trên trang (yêu cầu 3 của phiếu: "không bao giờ hiện giá trị khóa").
- **Thực tế:** câu hiện nguyên, kể cả khóa (`settings.py:150`, `show(message)`).
- **Đánh giá:** đúng như thiết kế của phiếu ("câu thông báo lấy nguyên từ `check_api_key`, đã che khóa"); `check_api_key` thật đã qua `redact_secrets` và chỉ dùng câu cố định, test đầu-cuối ở trên xác nhận không lộ. Ghi lại để Chỉ Huy/Lá Chắn quyết có cần lớp che thứ hai không. Sửa rẻ: ở giao diện, thay chuỗi khóa đang có hiệu lực bằng "[đã ẩn]" trước khi hiện (hoặc gọi `redact_secrets`, lưu ý hàm này che theo mẫu nên có thể không bắt mọi dạng khóa).

## Đối chiếu tiêu chí xong

- [x] Ba nút Kiểm tra hoạt động, có test (bảng trên)
- [x] `uv run pytest` và `uv run ruff check .` sạch (`2034 passed, 9 xfailed`; `All checks passed!`)
- [x] Báo cáo của Họa Sĩ có hướng dẫn chủ dự án tự kiểm tra

## Rủi ro và điểm cần chú ý

- `tests/test_soi_loi_round7.py::test_many_lookup_inputs_catch_naive_scan` hỏng 1 lần khi chạy cả bộ, qua khi chạy riêng và ở lượt chạy cả bộ thứ hai. Test đo tốc độ, dễ chập chờn khi máy bận (không liên quan T-023).
- Streamlit tự bỏ khoảng trắng ở cuối câu thông báo; không phải lỗi.
- Không đọc được vị trí thẻ qua giao diện thật; "đúng thẻ" kiểm bằng cây phần tử của AppTest (cột chứa 3 nút của khóa đó).

## Đề xuất

- Họa Sĩ sửa T023-01 (vài dòng `try/except`), bỏ dấu `xfail` tương ứng. T023-02 để Lá Chắn quyết.
- Chỉ Huy cân nhắc phiếu làm test tốc độ ở round7 bền hơn.

## Câu hỏi cho chủ dự án

Không có.

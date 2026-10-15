# Báo cáo T-019 · Thử mù mô hình AI (phần giao diện)

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | [T-019](../tickets/T-019-thu-mu-mo-hinh.md) |
| Ngày nộp | 2026-10-15 |
| Kết quả | Hoàn thành (phần Họa Sĩ) |

## Tóm tắt (cho chủ dự án)

Tab **🤖 Mô hình AI** trong Cài đặt giờ là thật. Bảng "việc nào dùng mô hình nào" đọc thẳng từ `config/ai.toml`. Khu thử mù: bạn gõ từ khóa, chọn 2–3 mô hình (chỉ trong các hãng đã có khóa), app báo trước "sẽ gọi AI N lần, có tốn tiền", bấm chạy thì các bài hiện dưới tên A/B/C. Chấm điểm, bấm "Chấm xong — hiện tên mô hình" mới biết bài nào của ai, kèm hướng dẫn sửa `config/ai.toml` để dùng mô hình thắng cuộc.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `app/views/settings.py` | Tab "🤖 Mô hình AI": bảng việc–mô hình thật, khu thử mù gọi `seo_app.content.blind_test`; sửa chú thích `ai_models.toml` → `ai.toml`. Các tab khác không đổi |
| `seo_app/demo.py` | Xóa `AI_TASKS`, `BLIND_OUTPUTS`, `BLIND_MODELS` (không còn dùng) |
| `tests/test_settings_blind.py` (mới) | 14 test `AppTest`, `run_blind_test` giả, không gọi mạng |
| `tests/test_app_pages.py` | Thay test thử mù cũ (dựa trên dữ liệu mẫu) bằng test "chưa có khóa thì khóa thử mù" |

## Cách hoạt động trên giao diện

1. **Bảng việc–mô hình**: `blind_test.task_models()` → cột Việc, Hãng, Mô hình, Mức nghĩ (effort). File sai → `st.error` câu tiếng Việt.
2. **Hãng**: dòng huy hiệu "✅ đã có khóa / ⚪ chưa có khóa" (chỉ đúng/sai, không hiện khóa). Chưa có khóa nào → câu nhắc sang tab 🔌 Kết nối, không hiện ô chọn, không có nút chạy.
3. **Ứng viên**: chọn số lượng bằng `segmented_control` (nhãn cố định "2 mô hình" / "3 mô hình"). Mỗi ứng viên: hãng (chỉ hãng có khóa; mặc định mỗi ứng viên một hãng khác nhau nếu đủ), tên mô hình (gợi ý sẵn từ `config/ai.toml`; đổi hãng thì gợi ý đổi theo; hãng chưa có trong file thì để trống, nhắc gõ theo tài liệu hãng), mức nghĩ. Mới có khóa một hãng vẫn thử được giữa các mô hình cùng hãng.
4. **Trước khi chạy**: luôn hiện cảnh báo vàng "Bấm chạy sẽ gọi AI N lần … có tốn tiền"; nhãn nút cũng ghi số lần gọi. Nút chỉ bật khi `validate_request` qua (có từ khóa, 2–3 ứng viên, tên mô hình hợp lệ); nếu chưa qua, hiện lý do dưới cảnh báo.
5. **Kết quả**: mỗi bài một ô "Bài A/B/C", chữ AI hiện bằng `st.markdown` thường (không `unsafe_allow_html`), mỗi bài một thanh điểm 1–10. Ứng viên lỗi chỉ hiện câu cố định `HIDDEN_ERROR`, không có thanh điểm.
6. **Hiện tên**: bấm "Chấm xong — hiện tên mô hình" thì chốt điểm (thanh điểm thành chữ "Điểm: 9/10", không chấm lại), hiện bảng xếp hạng (Bài, Điểm, Tình trạng, Hãng, Mô hình, Mức nghĩ), câu lỗi thật của ứng viên lỗi, và hướng dẫn 4 bước sửa `config/ai.toml` kèm khối `provider` / `model` / `effort` của bài điểm cao nhất. Chạy lượt mới thì tên lại ẩn; nút "🔄 Xóa kết quả" xóa lượt thử.

Giữ kín trước khi chấm: `reveal` chỉ nằm trong `st.session_state`, không vào nhãn, `help=`, `key=`, bảng hay chữ nào trên trang; khóa widget chỉ dùng nhãn A/B/C.

## Bằng chứng

```
$ uv run pytest tests/test_settings_blind.py tests/test_app_pages.py tests/test_settings_keys.py
53 passed

$ uv run pytest
9 failed, 2770 passed, 2 skipped, 9 xfailed in 171.25s
# 9 test đỏ đều là tests/test_soi_loi_t027.py (đỏ sẵn trên Linux, phiếu khác đang sửa)

$ uv run ruff check .
All checks passed!
```

Test chính:
- `test_names_hidden_until_scored_then_revealed`: trước khi chấm không chữ nào trên trang (markdown, chú thích, thông báo, nhãn/help/key widget, bảng) chứa tên mô hình; sau khi chấm bảng xếp hạng đúng thứ tự điểm và hướng dẫn đúng mô hình thắng.
- `test_failed_candidate_shows_fixed_message_then_real_error`: ứng viên lỗi chỉ hiện câu cố định; câu lỗi thật chỉ hiện sau khi chấm.
- `test_ai_text_is_plain_markdown_not_html`: ô Markdown chứa chữ AI có `allow_html = False`.
- `test_only_providers_with_key_can_be_chosen`, `test_no_key_locks_blind_test`, `test_run_disabled_until_inputs_valid_and_cost_warning_shown`, `test_three_candidates`, `test_single_vendor_can_compare_its_own_models`, `test_run_passes_inputs`, `test_run_error_shown`, `test_model_table_reads_config_ai_toml`, `test_bad_config_shows_vietnamese_error`, `test_model_name_suggested_from_config_and_follows_provider`, `test_new_run_hides_names_again_and_clear_button`.

### Chủ dự án tự kiểm tra

1. Windows: bấm đúp `run.bat` (Mac: `run.command`), đăng nhập.
2. Menu **Cài đặt** → tab **🤖 Mô hình AI**.
3. Xem bảng trên cùng có khớp `config/ai.toml` không.
4. Nếu đã nhập khóa (tab 🔌 Kết nối): gõ một từ khóa thật, chọn 2 mô hình, đọc cảnh báo tốn tiền, bấm **▶️ Chạy thử mù**. Mỗi lượt gọi AI 2–3 lần, mỗi bài ngắn.
5. Kéo điểm từng bài, bấm **Chấm xong — hiện tên mô hình**, xem bảng xếp hạng và hướng dẫn sửa `config/ai.toml`.

## Đối chiếu tiêu chí xong (phần Họa Sĩ)

- [x] Mục 1 · bảng đọc thật `config/ai.toml`, sửa chú thích (`test_model_table_reads_config_ai_toml`)
- [x] Mục 2 · từ khóa + ghi chú; 2–3 ứng viên chỉ trong hãng có khóa, gợi ý mô hình từ config; cảnh báo N lần trước khi chạy; A/B/C không HTML; thanh điểm và nút hiện tên (các test ở trên)
- [x] Mục 3 · hướng dẫn sửa `provider`/`model` sau khi hiện tên
- [x] Mục 4 · xóa `AI_TASKS`, `BLIND_OUTPUTS`, `BLIND_MODELS`; tab có chú thích "Phần này là thật"
- [x] Mục 5 · test `AppTest` với hàm giả; `tests/test_app_pages.py` vẫn mở được trang Cài đặt
- [x] Không lộ tên mô hình trước khi chấm

## Rủi ro và điểm cần chú ý

- **Nhãn "Bản demo" đầu trang Cài đặt vẫn còn** (vì tab Văn phong và Ảnh vẫn là demo, phiếu không cho sửa). Như tab 🔌 Kết nối, tab này có chú thích riêng "Phần này là thật". Câu demo ghi "chưa gọi AI thật" nên hơi lệch với tab này; muốn sửa thì cần cho phép đổi `ui.page_header` hoặc chuyển nhãn demo xuống từng tab.
- `config/ai.toml` hiện chỉ có mô hình Anthropic, nên với OpenAI/Gemini ô tên mô hình để trống, người dùng phải tự gõ đúng tên. Gõ sai thì ứng viên đó lỗi (vẫn tốn lượt gọi các ứng viên khác), câu lỗi hiện sau khi chấm.
- Danh sách ứng viên người dùng nhập vẫn hiện phía trên kết quả (đó là bản chất thử mù: biết những ai dự thi, không biết ai là A/B/C). Không có chữ nào nối "Ứng viên 1" với nhãn.
- Câu lỗi `bad_request_error` nhắc mục `blind_test` trong `config/ai.toml` (Thợ Máy đã ghi, thuộc T-028).
- Chú thích đầu file `config/ai.toml` vẫn ghi "openai và gemini sẽ thêm sau" (đã lỗi thời từ T-018); không sửa vì ngoài phạm vi (`config/**`).

## Đề xuất

- Thư Ký / Ngòi Bút: cập nhật chú thích đầu `config/ai.toml` (đã có đủ 3 hãng) và thêm vào README mục "Thử mù mô hình".
- Sau khi các tab Cài đặt còn lại làm thật: bỏ `demo=True` ở đầu trang.

## Câu hỏi cho chủ dự án

Không có.

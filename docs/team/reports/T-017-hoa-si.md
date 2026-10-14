# Báo cáo T-017 · Tự lưu nháp và mở lại bài đang soạn (giao diện)

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | [T-017](../tickets/T-017-giao-dien-luu-nhap.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Trang Soạn bài giờ tự lưu bài đang soạn vào máy sau mỗi thay đổi (AI chạy xong, sửa dàn ý, viết lại, áp dụng/bỏ qua gợi ý, sửa tay, chuyển bước), không cần bấm nút. Dưới tiêu đề trang có dòng nhỏ "💾 Đã lưu lúc HH:MM". Ở bước 1 có khung "📂 Bài đang soạn dở": mỗi bài có tên, từ khóa, giờ lưu, nút **Mở** và nút **🗑️ Xóa** (bấm Xóa thì hỏi lại "Xóa hẳn nháp này?"). Mở một bài sẽ quay về đúng bước, đủ các phiên bản của từng phần (nút ↶ ↷ vẫn dùng được).

Trong lúc làm, tôi gặp và sửa luôn một lỗi có sẵn: sau khi rời bước 1 vài lần bấm, **từ khóa, chất liệu thật và tiêu đề các mục dàn ý bị mất** (Streamlit tự xóa giá trị của ô không còn hiện trên màn hình). Không sửa thì nháp sẽ lưu thiếu những thứ này.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `app/views/write.py` | Tự lưu, khung Bài đang soạn dở (Mở/Xóa), mở nháp, dòng "Đã lưu lúc", báo file nháp hỏng; giữ giá trị ô `keyword`, `outline_title`, `real-…`, `h-…` khi chuyển bước. |
| `tests/conftest.py` | Fixture tự động `_never_touch_real_drafts`: mọi test trỏ kho nháp sang thư mục tạm riêng. |
| `tests/test_app_drafts.py` (mới) | 14 hàm test (18 trường hợp) cho tự lưu, mở, xóa, lỗi. |

Không sửa `seo_app/storage/`, `seo_app/env_file.py`, `app/views/settings.py`. Không thêm thư viện, không commit.

## Chi tiết

- **Kho nháp** (`write.py:194–202`): `draft_store()` đọc `seo_app.storage.drafts.DEFAULT_DRAFTS_FILE` *lúc chạy* và dùng `st.cache_resource` theo đường dẫn, nên test trỏ được sang thư mục tạm và mỗi test có kho riêng.
- **Mở nháp** (`write.py:235–276`, gọi ở `init_state` dòng 52–53, trước khi vẽ ô nào): nút Mở chỉ đặt `S._open_draft`. Làm đúng ba lưu ý của Thợ Máy: chạy trước widget; không dùng `set_outline` (test `test_open_sample_draft_restores_step_and_versions` kiểm tiêu đề mục có `\[` giữ nguyên); `clear_compose()` (dòng 93) xóa các ô `real-` cũ, chỉ nhận nhãn chất liệu đang có trên trang. Mở xong không lưu lại ngay (giữ nguyên giờ lưu), chỉ ghi nhận làm mốc so sánh.
- **Tự lưu** (`autosave`, cuối trang): dựng `snapshot()`, so JSON (bỏ `saved_at`) với lần lưu trước, khác thì `save`. Trang trống (chưa có từ khóa, chưa nghiên cứu) thì không lưu. Lỗi (`DraftError`, dữ liệu sai khuôn) chỉ hiện `⚠️ Chưa lưu được nháp: …`, trang không sập. Lưu ý: khi AI chạy xong trang gọi `st.rerun()`, nên bản lưu diễn ra ở lần chạy liền sau (tức thì với người dùng).
- **Bài mới từ trang Bài viết** (`_start_keyword`): bỏ `draft_id` để tạo nháp mới, không ghi đè bài đang mở. Theo quyết định của Chỉ Huy, bài mới cũng xóa luôn chất liệu thật (`clear_compose()` thay cho `reset_compose()`); bài cũ vẫn giữ chất liệu trong nháp riêng (test `test_new_article_clears_material_but_old_draft_keeps_it`).
- **Xóa**: popover hỏi lại, nút "Xóa hẳn". Xóa đúng bài đang mở thì trang được xóa trắng (nếu không, lần tự lưu sau sẽ tạo lại nháp vừa xóa). Bài đang mở hiện nút "Đang mở" (khóa).
- **Hiển thị chữ từ nháp**: tên và từ khóa trong danh sách hiện bằng `st.text` (không diễn giải Markdown/HTML, `write.py:340–344`); nhãn nút, popover và thông báo xóa là chữ cố định. Nội dung khác (nghiên cứu, dàn ý, các phần, rà soát) đi qua đúng các đường hiển thị sẵn có như khi AI vừa trả về. Không thêm `unsafe_allow_html` nào (`git diff app/views/write.py | grep unsafe_allow_html` không ra dòng nào).
- **File nháp hỏng**: nếu `recovered_from` có giá trị, báo một lần mỗi phiên: "File nháp cũ bị hỏng nên đã được cất sang một bên (tên «…», cùng thư mục). App bắt đầu file nháp mới." Chỉ hiện tên file, không hiện đường dẫn đầy đủ.
- **Lỗi mất giá trị ô** (`write.py:36–41, 54–55`): mỗi lần chạy gán lại `S[k] = S[k]` cho `keyword`, `outline_title`, `real-…`, `h-…`, cách Streamlit khuyên dùng để giữ giá trị ô không hiện. Đã kiểm chứng lỗi trước khi sửa: sau `go_to_article` và hai lần chạy, `keyword`, `real-…`, `h-…` biến mất khỏi session. Test `test_keyword_and_material_survive_moving_between_steps`.

## Bằng chứng

```
$ uv run pytest tests/test_app_drafts.py tests/test_app_pages.py -q
35 passed in 15.74s

$ uv run pytest -q   (toàn bộ, lần chạy cuối, sau khi thêm phần xóa chất liệu khi viết bài mới)
1712 passed, 3 xfailed in 99.29s

$ uv run pytest -q   (toàn bộ, một lần chạy trước đó)
FAILED tests/test_soi_loi_round6.py::test_helper_catches_quadratic_function

$ uv run pytest -q tests/test_soi_loi_round6.py tests/test_soi_loi_round7.py tests/test_app_drafts.py tests/test_app_pages.py tests/test_storage_drafts.py
169 passed in 30.23s

$ uv run ruff check .
Found 3 errors.   (cả 3 nằm trong tests/test_soi_loi_t016_t020.py: file Soi Lỗi đang viết song song, tôi không sửa)

$ uv run ruff check . --exclude tests/test_soi_loi_t016_t020.py
All checks passed!
```

Lỗi trong lần chạy toàn bộ là test đo thời gian (`round6`/`round7`), lúc qua lúc trượt khi máy bận (có agent khác chạy song song); chạy riêng thì qua. Một lần chạy trước đó còn có lỗi ở `tests/test_settings_keys.py`: file đó thuộc việc Thợ Máy đang làm song song (`settings.py`, `env_file.py`), không liên quan T-017; lần chạy sau thì qua.

`ruff format --check .` báo 7 file chưa định dạng, trong đó có `app/views/settings.py` (của agent khác); 3 file tôi sửa đã định dạng đúng.

**Tự kiểm tra trên app:** mở app, vào Soạn bài, nhập từ khóa, bấm Phân tích → thấy "💾 Đã lưu lúc …". Bấm F5 (hoặc đóng tab mở lại), đăng nhập, vào Soạn bài → khung "📂 Bài đang soạn dở" mở sẵn, bấm **Mở** để quay lại đúng bước. Thử 🗑️ Xóa → hỏi lại → Xóa hẳn.

## Đối chiếu tiêu chí xong

- [x] Tự lưu sau AI và sau thay đổi của người dùng: `test_autosave_after_ai_and_shows_saved_time`, `test_user_edits_are_saved_without_a_button`
- [x] Khung Bài đang soạn dở, Mở, Xóa hỏi lại: `test_draft_list_shows_text_without_markdown`, `test_delete_asks_first_then_removes`, `test_deleting_open_draft_clears_page_and_does_not_recreate`
- [x] Mở dựng lại đúng bước, đúng phiên bản: `test_open_sample_draft_restores_step_and_versions`, `test_open_draft_then_outline_step_keeps_text`, `test_every_step_renders_with_open_draft` (5 bước)
- [x] "Đã lưu lúc HH:MM" theo giờ Việt Nam: `test_saved_time_uses_vietnam_time`
- [x] Chữ từ nháp không đi qua `unsafe_allow_html`; tên có link Markdown hiện nguyên chữ: `test_draft_list_shows_text_without_markdown`
- [x] File hỏng được báo một lần: `test_corrupt_drafts_file_is_reported`; nháp không mở được báo lỗi: `test_opening_missing_draft_shows_error`
- [x] `tests/test_app_pages.py` vẫn qua hết (mọi trang, mọi bước)
- [x] Test không ghi vào `data/` thật: fixture `_never_touch_real_drafts` trong `tests/conftest.py`; sau khi chạy toàn bộ, `data/` không có file nháp nào
- [x] `uv run pytest` qua hết ở lần chạy cuối (1712 passed); `uv run ruff check .` sạch với mọi file của T-017 (3 lỗi còn lại nằm trong file Soi Lỗi đang viết)

## Rủi ro và điểm cần chú ý

- **Kho nháp thật từng bị test ghi vào**: lúc 10:23:02–10:23:32 (sau khi tôi sửa `write.py`, trước khi thêm fixture) có ai đó chạy pytest, các test trang Soạn bài đã ghi 4 nháp rác vào `data/drafts.sqlite` (từ khóa "sửa cửa cuốn", tiêu đề `<script>…`). Tôi đã kiểm tra cả 4 đều là dữ liệu test rồi xóa file đó (thư mục `data/` không đưa lên git). Từ giờ fixture chặn việc này.
- Tự lưu khi từ khóa vừa được gõ: mỗi phiên mới gõ từ khóa sẽ tạo một nháp (tối đa 30, tự bỏ nháp cũ nhất). Có thể làm đầy danh sách nếu người dùng thử nhiều từ khóa.
- Hai tab cùng sửa một nháp: bản lưu sau ghi đè (như Thợ Máy đã nêu).
- Meta title/description (bước SEO, còn demo) chưa được lưu.

## Đề xuất

- Thợ Máy (khi làm Giai đoạn 4): thêm trường meta vào `DraftSnapshot` (giá trị mặc định), như đã đề xuất ở T-016.
- Soi Lỗi: test đo thời gian `test_soi_loi_round6/7` chập chờn khi máy bận, nên nới ngưỡng hoặc đo nhiều lần lấy số nhỏ nhất.
- Lá Chắn: xác nhận các đường hiển thị nội dung nháp (nghiên cứu, rà soát, dàn ý) như Thợ Máy đề nghị ở T-016; tên/từ khóa trong danh sách hiện bằng `st.text`.

## Câu hỏi cho chủ dự án

Không có.

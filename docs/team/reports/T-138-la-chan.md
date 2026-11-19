# Biên bản bảo mật T-138 · Tạm dùng Gemini Flash cho mọi việc AI; test ghim cấu hình; nghiên cứu tắt tìm web; test không ghi `data/` thật · rút gọn

> **Model:** **Fable 5.1** (dòng «You are powered by»: Fable 5.1, kiểm đầu lượt). Chỉ Huy B giao 19/11.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **Fable 5.1** · dưới Chỉ Huy B |
| Phiếu được kiểm | T-138 (phiếu trên `main`; quyết định chủ dự án 18/11: tạm Gemini Flash miễn phí, tắt tìm Google; sổ rủi ro `security.md` mục 6 dòng 2026-11-18 trên `main` `756941c`). Nhánh `team/T-138` từ `main` `3202035`: Thợ Máy `7bbe500`, `6309116`, `2bdee5f`, `d82ad6d` (lượt 1, R5 22 ca); Soi Lỗi rút gọn `c1b6674` (ĐẠT CÓ ĐIỀU KIỆN, 3 Thấp chữ, G-1 → G-4); Thợ Máy lượt 2 `8203c06`, `df517a3` (SL-T138-1, -2, -3; gỡ 3 `xfail`). Đầu nhánh **`df517a3`**, đã push |
| Phạm vi | **Rút gọn**, theo 4 trọng tâm Chỉ Huy giao: diff `3202035..df517a3` (`config/ai.toml`, `seo_app/content/prompts.py` +25, `workflow.py` +12, `app/views/write.py` +49, `README.md` +16, `tests/conftest.py` +19, `tests/ai_config_samples.py` mới, 10 file test cũ sửa, 3 file test mới), bảng R5 của Thợ Máy và bảng đột biến R5 của Soi Lỗi; đọc cùng `ContentWriter._run`, nơi gọi `DEFAULT_…_FILE` ở các trang, `PREVIEW_CACHE_DIR`. Không sửa mã; không gọi AI, Google, website thật; chỉ chạy test trong `wt-T-138` |
| Ngày | 2026-11-19 (giao ≈ 13:30, xong 13:59, +07, giờ máy) |
| Máy | Windows 11 Pro 10.0.26300, Python 3.12.15, uv 0.13.4. Chỉ chạy test liên quan, không chạy toàn bộ; lô test chạy nền trong worktree |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được ngay** (`main` `ddcd23c`: `git merge-tree` không xung đột; từ `3202035` `main` chỉ đổi tài liệu): 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp mới. Cả 4 trọng tâm **đạt**: 22 ca R5 vẫn giữ điều bảo vệ đã qua Lá Chắn (T-051, T-062, T-103, T-010/T-118…), ca `[bat-du]` nay rỗng một phần nhưng điều «không lộ khóa» vẫn có ca khác giữ; tắt tìm web thì bài đối thủ bị bỏ **ở code**, bật lại thì lời dặn và trang như cũ; fixture cách ly ba kho lưu tạm đủ cho mọi kho trong `seo_app/storage`; `config/ai.toml`, README 7 và 7.2 đúng hiện trạng và cách quay lại Claude. Điều kiện chỉ là dọn test và một thư mục `data/` ngoài phạm vi phiếu (ảnh xem trước), không chặn |

## Tóm tắt (cho chủ dự án)

Phiếu này chuyển mọi việc AI sang Gemini Flash miễn phí theo quyết định của anh/chị ngày 18/11, và sửa bộ kiểm thử cho khớp. **Gộp được.**

- **Dữ liệu gửi đi không đổi loại:** app vẫn chỉ gửi cho AI những gì trước đây gửi cho Claude (từ khóa, chất liệu thật, hồ sơ doanh nghiệp, ảnh công trình đã bỏ GPS khi bấm «AI viết alt»). Khác là nay gửi cho **Gemini gói miễn phí**, Google có thể dùng để cải tiến sản phẩm. Anh/chị đã chấp nhận điều này ngày 18/11 (đã ghi sổ rủi ro); README mục 7.2 nay nói đúng như vậy và dặn **không bấm «AI viết alt» cho ảnh có mặt người, số nhà, biển hiệu của khách**.
- **Tắt tìm Google:** AI không đọc được trang nào, nên app **bỏ hẳn** phần «bài đối thủ» ngay trong code dù AI có bịa ra. Trang Soạn bài ghi rõ «Đang tắt tìm Google». Bật lại (quay về Claude, hay bật thanh toán Gemini) thì mọi thứ như trước, lời dặn AI giống hệt bản cũ.
- **Bộ kiểm thử:** các ca từng «ghim» Claude nay kiểm đúng điều cần bảo vệ (app chỉ đòi khóa của hãng đang dùng, không lộ khóa, file cấu hình hỏng thì trang vẫn chạy, chỉ bước nghiên cứu mới được tìm web) mà không phụ thuộc hãng nào. Tôi đọc từng ca: không ca nào bị làm yếu.
- **Kiểm thử không còn ghi vào thư mục `data` của phần mềm** (danh sách bài, kế hoạch, số liệu Google), nên chạy test không còn làm lệch dữ liệu app đang dùng.
- **Việc của anh/chị:** không có.

## Kết quả theo trọng tâm Chỉ Huy giao

### 1. Bảng R5: ca cũ đổi kỳ vọng vẫn giữ điều bảo vệ — **đạt**

Tôi đọc diff của 10 file test cũ (`git diff 3202035..df517a3 -- tests/`) và bảng đột biến của Soi Lỗi (23 đột biến, ca mới trên nhánh so ca cũ trên `main`):

| Điều bảo vệ đã qua Lá Chắn | Ca giữ nó sau T-138 | Đánh giá |
|---|---|---|
| Trang Soạn bài **chỉ đòi khóa của hãng đang được cấu hình**, không đòi cả ba (T-051 SL-T051-1) | `test_write_page_with_committed_config_needs_only_configured_keys` (`set_configured_keys`, có chặn rỗng `names and len(names) < 3`), `test_app_pages::test_without_api_key_ai_buttons_are_locked` (câu báo nêu đúng biến khóa của hãng đang dùng, nút khóa) | Giữ; ca mới còn bắt thêm đột biến P1 |
| **Việc ảnh bật thì khóa Gemini chỉ bị đòi khi gọi việc ảnh**; trang Soạn bài, Cài đặt không đòi; viết bài không dựng Gemini (T-051, T-062) | 6 ca dùng bản mẫu `ai_text_on("anthropic")` («viết bằng Claude, ảnh bằng Gemini») trong `tmp_path` | Giữ, nay **không phụ thuộc** hãng trong file đã commit (với file toàn Gemini thì không thử được điều này: Thợ Máy chọn đúng) |
| **Không lộ khóa** trong câu báo | `test_t062_image_config::test_write_page_with_image_enabled_and_only_claude_key` (đột biến P6 bị bắt trên nhánh) | Giữ. Ca `[bat-du]` của `test_write_page_with_image_block_touched_never_crashes_or_shows_key` **không đổi** nhưng nay đặt khóa Claude trên file toàn Gemini nên không dựng hãng nào: phần «không lộ khóa» của ca đó rỗng (Soi Lỗi G-3). Không phải lỗi: điều bảo vệ còn ở ca trên; **điều kiện B.1** đặt khóa theo `set_configured_keys` |
| **`config/*.toml` hỏng thì trang vẫn chạy, báo câu tiếng Việt**, không lọt lỗi thô (T-010, T-118) | `test_real_ai_toml_broken_on_disk_is_handled_like_t010[cut]` (chỗ cắt theo `[tasks.alt]`, hãng nào cũng vậy), `test_write_page_survives_broken_real_content_toml`, `test_bad_alt_and_images_do_not_lock_write_page` | Giữ (khóa đặt theo hãng đang cấu hình chỉ là điều kiện để trang chạy) |
| **Chỉ việc nghiên cứu được tìm web**; `links`, `plan` không bao giờ (Lá Chắn T-039, T-094, T-103) | `test_old_tasks_still_load_next_to_alt`, `test_ai::test_project_ai_config_is_valid`, `test_t103_plan_prompt::…never_searches_web`: tập việc có tìm web ⊆ {`research`} | Giữ (đột biến C1–C3, L3 bị bắt). Phần «research bật» đổi thành ghim quyết định 18/11 (tắt), đúng phiếu |
| **Tiêu đề bài đối thủ hiện đã thoát Markdown** (U1) | `test_config_tolerance::test_research_page_shows_competitor_title_escaped` với bản mẫu **bật** tìm web (`research_web_search_toml`) | Giữ; cần bản mẫu vì tắt thì code bỏ hết đối thủ |
| Lỗi AI viết alt hiện bằng `st.error`, nêu khóa thiếu, không `st.exception` | `test_app_images::test_alt_ai_errors_shown_as_message` (biến khóa theo hãng của việc `alt`) | Giữ |
| Ô tên mô hình thử mù lấy từ cấu hình, đổi theo hãng | `test_settings_blind::…follows_provider` | Mất phần «điền sẵn lúc mở trang» (Soi Lỗi G-1), Soi Lỗi đã bù bằng ca riêng; cả hai trong lô test |
| Bộ đọc không bỏ qua `web_search` | 4 ca R5 so với `False` (= mặc định) không bắt được L2 (Soi Lỗi G-2); 3 ca khác trên nhánh và ca bù của Soi Lỗi bắt | Giữ |

Hai ca ghim **quyết định** (alt = Claude Sonnet 4A; nghiên cứu có tìm web) đổi thành ghim cấu hình 18/11 kèm chú thích: đúng yêu cầu 2 của phiếu. Không ca nào bị xóa, không `skip`/`xfail` thêm; 3 `xfail` của Soi Lỗi gỡ ở lượt 2 chỉ xóa dấu (thân test không đổi, kiểm diff `c1b6674..8203c06`).

### 2. Nghiên cứu tắt tìm web: đối thủ bị bỏ ở code, không lên trang, dàn ý, nháp; bật lại như cũ — **đạt**

- `ContentWriter.research` (`workflow.py:236-247`): lấy `TaskConfig` của việc `research`, dựng lời dặn theo `config.web_search`, gọi `provider.generate(config, system=self.system, prompt=…, schema=Research)` **y như** `_run` (`:231-233`, tôi so từng tham số: không bỏ lớp nào), rồi `clean_research`, rồi **`competitors = []` khi tắt** (không tin lời dặn). Chỉ `workflow.py` dựng `Research` từ AI; `drafts.py` chỉ đọc lại nháp đã lưu. Soi Lỗi thử cả luồng với AI giả cố tình bịa đối thủ có dấu nhận: tắt thì không có ở trang, `research` của phiên, lời dặn dàn ý, viết bài, file nháp; bật thì có ở cả bốn chỗ (đối chứng); 9/9 đột biến bị bắt.
- **Không gọi công cụ tìm web khi tắt:** hãng AI chỉ gắn công cụ khi `config.web_search` (Soi Lỗi dẫn `anthropic_provider.py:95`, `openai_provider.py:121`, `gemini_provider.py:179`; lớp provider không đổi trong phiếu). Vì vậy tắt tìm web còn là một lớp **giảm dữ liệu gửi ra ngoài**: không có truy vấn Google mang từ khóa.
- **Lời dặn khi tắt** (`prompts.py:166-182`): từ khóa qua cùng lớp lọc `_keyword` như cũ, bảo để TRỐNG đối thủ, không bịa tên bài, đường dẫn; không gửi thêm dữ liệu gì mới. **Bật:** `research_prompt(k, web_search=True)` giống hệt bản `main` từng chữ (Soi Lỗi 7/7 từ khóa).
- **Trang** (`write.py:2085-2090`, `:2188-2242`): `research_searches_web()` chỉ đọc `config/ai.toml` (không cần khóa, không tạo AI; lỗi cấu hình → coi như bật, chỉ mất dòng nhắc, không sập); dòng `MSG_NO_WEB_SEARCH` hằng; khung đối thủ ẩn khi tắt **và** danh sách trống (kết quả cũ có đối thủ thật vẫn hiện: đúng, dàn ý vẫn dùng); bật thì không đổi. Tên bài đối thủ vẫn qua `markdown_link` như cũ.

### 3. Fixture cách ly `data/` — **đạt** (đủ cho mọi kho trong `seo_app/storage`)

- `tests/conftest.py:231-247`: fixture tự chạy `_never_touch_real_caches` trỏ `site_index.DEFAULT_SITE_INDEX_FILE`, `plan_cache.DEFAULT_PLAN_CACHE_FILE`, `search_cache.DEFAULT_SEARCH_CACHE_FILE` sang thư mục tạm riêng từng test, cùng hai fixture có sẵn cho kho nháp, kho thẻ ảnh. **Ăn thật** vì kho đọc mặc định **lúc tạo** (`default_factory`) và các trang đọc **thuộc tính module lúc chạy** (`plan.py:174,181`, `write.py:2532`, `home.py`, `tracking.py`); `seo_app/storage/__init__.py` chỉ xuất lại `DEFAULT_DRAFTS_FILE` và không chỗ nào dùng bản đó (grep).
- `tests/test_t138_khong_ghi_data_that.py`: mọi `DEFAULT_…_FILE` của **mọi** module trong `seo_app/storage` phải trỏ ra ngoài dự án lúc test (kho thêm sau mà quên trỏ thì hỏng); luồng WordPress giả không tạo, không đổi gì trong `data/` thật; ca đối chứng tắt trỏ thì ghi vào `data/`; 3 fixture đều `autouse`. Soi Lỗi: 98 file có WordPress giả chạy trong worktree với móc `sys.addaudithook`, **0** lần đụng `data/`; 4/4 đột biến fixture bị bắt.
- **Còn ngoài `seo_app/storage`:** cache ảnh xem trước `PREVIEW_CACHE_DIR = data/image_previews` (`seo_app/images/process.py:103`, `write.py:1142` đọc lúc chạy) **không** có fixture tự chạy; các file test ảnh tự trỏ qua fixture `previews` của `test_app_images.py` (conftest `:222` ghi rõ). Ngoài phạm vi phiếu (phiếu nêu ba kho lưu tạm); hôm nay không test nào ghi (móc kiểm của Soi Lỗi 0 lần), nhưng test mới sau này mở trang Soạn bài có ảnh mà không nhập fixture đó thì ghi được vào `data/image_previews/`. **Điều kiện B.2** (một dòng conftest + thêm vào ca «trỏ ra ngoài dự án»).
- Sau lô test của tôi: worktree không có thư mục `data/` (kiểm bằng `ls`).

### 4. `config/ai.toml`, README 7 và 7.2 — **đạt**

- `config/ai.toml`: 9 việc `provider = "gemini"`, `model = "gemini-3.8-flash"`; `[tasks.research]` `web_search = false` (chú thích «đang tắt tìm web từ 18/11»); `links`, `plan` giữ chú thích «KHÔNG thêm web_search» (Lá Chắn T-039, T-094); `[tasks.alt]` ghi quyết định 4A, tạm Gemini từ 18/11 và trỏ sổ rủi ro; ghi chú quay lại Claude (`:36-40`) có đủ ba bước: `provider`/`model` từng việc (alt: Sonnet), `web_search = true` ở research, nhập khóa Claude ở Cài đặt; ví dụ tên mô hình Gemini còn dùng được. File không chứa khóa, mật khẩu (grep `key|secret|token|password`: chỉ `max_tokens`); UTF-8, NFC, không CR; `load_ai_config()` nạp được (test `test_project_ai_config_is_valid`).
- README mục 7: khung «Đang dùng Gemini Flash miễn phí (từ 18/11/2026)» nêu hai giới hạn (không tìm Google, 503) và hai cách quay lại (Claude với `web_search = true`; bật thanh toán Gemini dùng Pro). Mục 7.2: alt đang dùng Gemini Flash khóa miễn phí, Google có thể dùng ảnh, chủ dự án chấp nhận 18/11 (dẫn sổ rủi ro), **tránh ảnh có mặt người, số nhà, biển hiệu**, quay lại Claude hay bật thanh toán thì hết. Khớp sổ rủi ro mục 6 dòng 2026-11-18 trên `main` và CLAUDE.md «Quyết định đã chốt» 18/11. Test của Thợ Máy và Soi Lỗi đối chiếu README với chữ trên trang và với cấu hình.
- Soi Lỗi G-4 (quay lại Claude thì 2–4 ca ghim quyết định hiện tại phải sửa cùng): đúng bản chất của «ca ghim quyết định» mà phiếu yêu cầu; ghi ở điều kiện B.3 để Chỉ Huy nhớ khi đổi cấu hình.

## Lỗi phát hiện

Không có lỗi mới.

## Đánh giá lỗi, ghi nhận của Soi Lỗi; R5

| Mục | Lá Chắn |
|---|---|
| SL-T138-1 (README 7.2 còn ghi Claude Sonnet, dặn báo Chỉ Huy) · Thấp | Đồng ý; **đã đóng** ở `8203c06` (mục 4). Đây là chỗ bảo mật đáng kể nhất của phiếu: tài liệu phải nói đúng việc ảnh công trình đi tới khóa miễn phí; nay đúng và có lời dặn tránh ảnh nhạy cảm |
| SL-T138-2 (ghi chú quay lại Claude thiếu `web_search = true`) · Thấp | Đồng ý; đã đóng (ai.toml `:36-40`, README) |
| SL-T138-3 (chữ bước 1 khi tắt tìm web) · Thấp | Đồng ý; đã đóng; cách ẩn khung khi danh sách trống nhưng giữ kết quả cũ có đối thủ thật là đúng |
| G-1, G-2 (hai ca R5 kiểm ít hơn ca cũ) | Đồng ý; Soi Lỗi đã bù bằng 3 ca; không cần Thợ Máy sửa thêm |
| G-3 (`[bat-du]` rỗng phần «không lộ khóa») | Đồng ý; điều bảo vệ còn ở ca khác; điều kiện B.1 |
| G-4 (quay lại Claude phải sửa 2–4 ca ghim) | Đồng ý; điều kiện B.3 |
| R5 lượt 2 (`test_soi_loi_t138.py` gỡ 3 `xfail`) | `git diff c1b6674..8203c06 -- tests/test_soi_loi_t138.py`: chỉ xóa 3 dấu; đúng |

## Thử độc lập (Fable)

Phiếu không thêm đường mạng hay lệnh ghi mới, nên tôi không viết probe riêng; thay vào đó đọc đối chiếu:

- `research()` mới so với `_run` (cùng `provider.generate(config, system=self.system, prompt, schema)`): không bỏ lớp nào;
- mọi chỗ gọi `provider.generate` trong `workflow.py` (`:233`, `:243`, `:422`): chỉ hai chỗ ngoài `_run`, đều truyền đúng `TaskConfig` của việc;
- nơi đọc `DEFAULT_…_FILE` ở các trang: đều qua thuộc tính module lúc chạy (fixture trỏ được);
- `PREVIEW_CACHE_DIR` chưa có fixture tự chạy (mục 3).

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pytest 44 file liên quan trên `df517a3`, trong `wt-T-138` (T-138 ×3; 10 file test cũ sửa; mọi file test nhắc `research_prompt`, `clean_research`, `competitors`, `web_search`; trang Cài đặt `test_soi_loi_t084`, `test_t101_settings_google`; kho `plan_cache`, `search_cache`, T-122, trang Theo dõi; T-103 ×3) | **3.968 qua, 8 bỏ qua** (đều symlink, quyền POSIX trên Windows), **2 xfail có từ trước** (SL-T026-3), **0 hỏng**, 20 phút 54 giây; sau lô: worktree **không có** thư mục `data/` | ✔ |
| `ruff check .`; `ruff format --check` 8 file | sạch; đúng khuôn | ✔ |
| bandit `prompts.py`, `workflow.py`, `write.py` (`PYTHONUTF8=1`), so bản gốc `3202035` và `df517a3` | 0 → 0 | ✔ |
| detect-secrets (`PYTHONUTF8=1`) `config/ai.toml`, README, 4 file mã, 9 file test, 2 báo cáo; biên bản này | 2 báo nhầm có từ trước: mật khẩu thử `PASSWORD` ở `test_settings_blind.py:19` (commit cũ) và báo cáo Thợ Máy dòng 142 chép lại mẫu địa chỉ web kèm tên đăng nhập, mật khẩu giả của docstring `write.py`; biên bản này: 0 | ✔ |
| Ký tự ẩn (Cf, Cc, CR), NFC trong 10 file | 0; đều NFC | ✔ |
| D1 | `uv.lock`, `pyproject.toml` không đổi; `config/ai.toml` đổi đúng phiếu, không khóa | ✔ |
| Gộp thử | `git merge-tree --write-tree main HEAD` (`main` `ddcd23c`) không xung đột; từ `3202035` `main` chỉ đổi tài liệu | ✔ |

## Ghi nhận (không xếp lỗi)

1. **Rủi ro dữ liệu gửi tới Gemini gói miễn phí** (chữ của bài, hồ sơ doanh nghiệp, chất liệu thật, ảnh công trình khi viết alt): là quyết định của chủ dự án, đã ghi sổ rủi ro và README; T-138 không gửi thêm loại dữ liệu nào so với trước. Khi quay lại Claude hay bật thanh toán, Chỉ Huy đánh dấu dòng sổ rủi ro hết hiệu lực.
2. `research_searches_web()` đọc `config/ai.toml` ở mỗi lần vẽ bước 1: rẻ; cấu hình lỗi thì thiếu dòng nhắc (câu báo lỗi cấu hình đã hiện chỗ khác).
3. Khuôn `Research` gửi AI vẫn tả `competitors` là «bài đứng đầu Google» cả khi tắt (Soi Lỗi đã nêu): vô hại vì code bỏ hết; Ngòi Bút gọn lại khi tiện.
4. Nháp cũ soạn lúc còn tìm Google giữ đối thủ thật (Thợ Máy chọn 1): đúng.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

**A. Gộp `main`: được ngay.** Chỉ Huy chạy toàn bộ test khi gộp, **trong worktree** (nay test không ghi `data/` thật, nhưng vẫn không chạy trong thư mục app đang dùng).

**B. Cho việc sau** (không chặn):

1. **Phiếu dọn test (Thấp):** `test_soi_loi_t051.py::test_write_page_with_image_block_touched_never_crashes_or_shows_key[bat-du]` đặt khóa bằng `set_configured_keys` để phần «không lộ khóa» chạy thật trên hãng đang cấu hình (Soi Lỗi G-3).
2. **Phiếu dọn test (Thấp):** thêm `seo_app.images.process.PREVIEW_CACHE_DIR` vào fixture tự chạy của `tests/conftest.py` (như ba kho lưu tạm) và vào ca «trỏ ra ngoài dự án» của `test_t138_khong_ghi_data_that.py`, để test ảnh sau này không ghi `data/image_previews/`.
3. **Khi quay lại Claude hay bật thanh toán Gemini:** sửa `config/ai.toml` theo ghi chú đầu file **và** 4 ca ghim quyết định hiện tại (`test_soi_loi_t051.py::test_alt_task_follows_owner_decision_with_small_budget`, `::test_old_tasks_still_load_next_to_alt`, `test_t138_gemini_flash.py::test_every_task_uses_gemini_flash_and_research_does_not_search`, `::test_write_page_with_committed_config_shows_the_note`), đồng thời Chỉ Huy cập nhật dòng sổ rủi ro 2026-11-18. Lá Chắn rút gọn.

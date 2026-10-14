# Biên bản bảo mật T-016 + T-020 · Kho nháp bài đang soạn · Nhập khóa API trong app

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **Claude Opus 5.5 (chạy tạm)**. Model chuẩn của vai này là Claude Fable 5.1, đang bị giới hạn tới 01/11/2026 nên lần này dùng Opus. Có thể cho Fable soát lại khi hết giới hạn. |
| Phiếu được kiểm | [T-016](../tickets/T-016-luu-nhap-bai-dang-soan.md), [T-020](../tickets/T-020-nhap-khoa-api-trong-app.md) |
| Phạm vi | Thay đổi **chưa commit** trên `HEAD = 4a0b6c3`: `seo_app/storage/` (mới), `seo_app/env_file.py` (mới), `app/views/settings.py`, `tests/conftest.py`, `tests/test_storage_drafts.py`, `tests/test_env_file.py`, `tests/test_settings_keys.py`. **Không** gồm `app/views/write.py` (T-017, Họa Sĩ đang sửa) |
| Ngày | 2026-10-14 |
| **Kết luận** | Lần 1: **ĐẠT CÓ ĐIỀU KIỆN**. **Lần 2 (sau T-021, kèm T-017): ĐẠT**. Xem mục "Lần 2" cuối biên bản |

## Tóm tắt (cho chủ dự án)

Khóa API nhập trong app không lộ ra màn hình, log hay thông báo lỗi. Không ai chèn được biến khác vào `.env` qua ô nhập. File `.env` được ghi với quyền chỉ chủ máy đọc được (600). Kho nháp không có chỗ nào chứa khóa hay mật khẩu. Không có lỗi Nghiêm trọng hay Cao.

Có hai lỗi mức Trung bình, phải sửa trước khi đóng T-017:
1. Nghiên cứu, rà soát, tiêu đề phần, tiêu đề bài và ghi chú ảnh đọc từ file nháp được hiện ra mà không lọc lại như khi AI vừa trả về.
2. Nếu dòng khóa trong `.env` bị lỡ một dấu nháy (thường do sửa tay), bấm Lưu sẽ xóa luôn mọi dòng phía sau, kể cả mật khẩu WordPress và mã băm mật khẩu đăng nhập.

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| 1 | **Trung bình** | Chữ do AI tạo, đọc lại từ nháp, không được lọc lại. Chỉ thân bài được chạy lại `escape_link_syntax`. Phần còn lại chỉ được kiểm khuôn: `research` (mọi trường), `review.summary/reason/replacement`, `DraftPart.heading`, `DraftPart.image`, `article_title`, `outline[*].heading/points/image`. **Tiền đề "an toàn nhờ đường hiển thị đã escape" là sai.** Khi AI vừa trả về, an toàn đến từ `clean_research`/`clean_review`/`clean_outline`/`clean_draft` lúc nhận dữ liệu (`seo_app/content/workflow.py:52-111`). Còn lúc hiển thị, trang chỉ ghép thẳng vào `st.markdown` | `seo_app/storage/drafts.py:95-113`. Chỗ hiển thị không escape: `app/views/write.py` (HEAD) `:302-315` (nghiên cứu), `:397` (ảnh), `:497` (`review.summary`), `:517-520` (tiêu đề phần, câu gợi ý), `:551` (`html.escape` chặn được thẻ HTML nhưng không chặn link Markdown) | Bước 1: sửa một dòng trong `data/drafts.sqlite` để `research.intent` chứa `[bấm đây](https://evil.example) ![](https://track.example/p.gif)`. Bước 2: `DraftSnapshot.model_validate_json` vẫn nhận nguyên văn (đã chạy thử). Bước 3: mở nháp, trang Soạn bài hiện link bấm được và tự tải ảnh từ máy chủ lạ (lộ IP, biết lúc mở bài). Thẻ HTML không chạy vì `st.markdown` không bật `unsafe_allow_html`. Muốn làm vậy phải ghi được file trên máy, nên **không khai thác từ xa được**. Nhưng có hai lý do vẫn phải sửa. (a) Phiếu T-016 yêu cầu coi dữ liệu từ file là chưa tin cậy. (b) Sau này siết bộ lọc `clean_*` thì nháp cũ vẫn đi vòng qua bộ lọc mới. Thân bài cũng chỉ được escape link, không bỏ thẻ (`<b>`, `<script>` nằm nguyên trong nháp). Trên giao diện thẻ đã được `ui.highlight` escape, nhưng khi gửi WordPress vẫn phải qua `sanitize_html` (W3) | Lọc lại khi **đọc nháp** (trong validator của `DraftSnapshot` hoặc trong `DraftStore.load`), dùng **đúng** các hàm `clean_*` của luồng AI: `research = clean_research(research)`, `review = clean_review(review)`, `article_title`/`DraftPart.heading` qua `clean_ai_line`, `DraftPart.image` qua `clean_ai_text`. Thân bài nên chạy `escape_link_syntax(strip_tags(...))`, giống `apply_flag`. Dàn ý lưu ở dạng ô sửa (chưa escape), nên dùng `unescape_link_syntax(clean_ai_line(x))` cho tiêu đề và `clean_ai_text` cho ý, ảnh. Thêm test: (i) nháp sạch đọc lại không đổi (đã chạy thử: `clean_research` và `clean_review` idempotent trên dữ liệu đã sạch); (ii) nháp có link hoặc ảnh Markdown và thẻ HTML ở **mọi** trường trên đều bị vô hiệu |
| 2 | **Trung bình** | Ghi khóa khi dòng cũ trong `.env` mở dấu nháy mà không đóng làm mất mọi dòng phía sau. `_unclosed_quote` thấy nháy mở, rồi vòng `while` bỏ các dòng tiếp theo cho tới khi gặp dấu nháy đóng. Nếu không có dấu đóng thì bỏ tới hết file. python-dotenv xử lý khác: nó chỉ bỏ qua dòng hỏng (*"could not parse statement starting at line 1"*), và các biến phía sau vẫn có hiệu lực | `seo_app/env_file.py:160-169` (dùng cho cả `set_api_key` và `clear_api_key`) | Đã chạy thử. `.env` gồm `ANTHROPIC_API_KEY="sk-old` (quên đóng nháy), `WORDPRESS_APP_PASSWORD=wp`, `APP_PASSWORD_HASH=pbkdf2$x`. Trước khi lưu, dotenv đọc được cả `WORDPRESS_APP_PASSWORD` và `APP_PASSWORD_HASH`. Bấm Lưu khóa mới thì file chỉ còn `ANTHROPIC_API_KEY=sk-ant-new…`. Mã băm mật khẩu và Application Password WordPress mất hẳn, không có bản sao. Lần mở app sau, chủ dự án bị khóa ngoài, phải tạo lại mã băm và Application Password. Trường hợp khóa cũ kết thúc bằng `\"` (nháy bị escape) cũng vậy. Không lộ bí mật, nhưng đây là lỗi làm hỏng chính file chứa bí mật, và người dùng ít dùng dòng lệnh rất dễ gõ thiếu nháy khi sửa tay | Chỉ bỏ các dòng tiếp theo khi **thật sự có** dấu nháy đóng ở dòng sau, tức là khớp cách dotenv đọc. Không tìm thấy dấu đóng thì chỉ thay đúng một dòng đó. Cách an toàn hơn: báo `EnvFileError` ("Dòng ANTHROPIC_API_KEY trong .env đang thiếu dấu nháy, hãy sửa tay trước") và không ghi gì. Thêm test: nháy không đóng, và `\"` ở cuối; sau khi ghi, mọi biến khác dotenv đọc được trước đó vẫn còn nguyên |
| 3 | Thấp | `.env` là liên kết tắt (symlink): `os.replace` thay chính liên kết bằng một file thường. Nội dung file đích bị **chép** vào `.env` mới (quyền 600), còn file đích không đổi | `seo_app/env_file.py:127-132`, `:197` | Đã chạy thử: liên kết tới `/tmp/…/real.env`. Sau khi lưu, `.env` không còn là liên kết, file đích còn nguyên, và không có gì bị ghi ra ngoài thư mục app. Liên kết gãy (trỏ tới file không tồn tại) thì tạo file mới tại chỗ, không tạo file ở đích. **Không khai thác được.** Chỉ có điều cách làm của người dùng bị phá ngầm (ví dụ họ trỏ `.env` sang một thư mục riêng) | Nên từ chối bằng `EnvFileError` khi `path.is_symlink()` ("File .env là liên kết tắt, hãy sửa tay"), kèm test. Không bắt buộc trong giai đoạn này |

## Trả lời các điểm Chỉ Huy hỏi

1. **Khóa nằm trong `session_state` từ lúc dán tới lúc bấm Lưu: CHẤP NHẬN.**
   - Streamlit bắt buộc vậy mới đọc được ô nhập.
   - Ô dùng `type="password"` (`app/views/settings.py:84-91`).
   - Callback `_save_key` xóa giá trị **trước** khi ghi, dù ghi được hay lỗi (`:34-35`). Nút Xóa cũng xóa ô nhập (`:56`).
   - Đăng xuất gọi `S.clear()` (`:159-160`). Chuyển trang thì Streamlit tự bỏ trạng thái của ô không còn hiện.
   - Nút Kiểm tra không truyền khóa: `check_api_key` tự đọc từ `load_settings()` (`:112`, `seo_app/env_file.py:280-282`). Kết quả lưu vào session chỉ là `(status, message)`.
   - Kho nháp có `extra="forbid"` và chỉ lấy các khóa `real-`, `h-`, `texts-`…, nên `api-key-input-*` không thể lọt vào nháp.
   - Khóa vẫn nằm trong bộ nhớ của tiến trình app, nhưng tiến trình đó vốn đã giữ khóa trong `Settings`. Rủi ro không tăng.
2. **Danh sách ký tự cho phép `[A-Za-z0-9_\-.:+/~]+` (`seo_app/env_file.py:33`): ĐỦ CHẶT.**
   - Không có `=`, `$` (nên không có `${…}` để dotenv thay giá trị), nháy, `#`, `\`, dấu cách, ký tự ngoài ASCII, ký tự vô hình.
   - Đã chạy thử, mọi giá trị sau đều bị chặn và file không đổi: `a\nAPP_PASSWORD_HASH=x`, ` `, `\x85`, `a=b`, `${HOME}`, `​`, chữ toàn khổ (`ａｂｃ`). Thông báo lỗi không chứa giá trị.
   - Giá trị hợp lệ được dotenv đọc lại đúng nguyên văn: `sk-ant-api03-a_b-c`, `AIza+/~:.x`, `~/x`, `-x`, `x:y`.
   - Có thể bỏ thêm `:`, `+`, `~` vì khóa của cả ba hãng hiện không dùng. Không bắt buộc.
3. **T-016: chữ trong nghiên cứu, rà soát, dàn ý chỉ được kiểm khuôn: CHƯA ĐỦ.** Xem lỗi #1. Trang Soạn bài không escape các trường này khi hiển thị. Chúng an toàn khi AI vừa trả về là nhờ các hàm `clean_*` chạy lúc nhận dữ liệu, và đọc nháp đã đi vòng qua bước đó. Danh sách thực tế còn rộng hơn câu hỏi: tiêu đề phần, tiêu đề bài, ghi chú ảnh cũng chưa được lọc. Thân bài thì đúng là được escape link, nhưng thẻ HTML không bị bỏ. Cần sửa trong T-016 (lọc lại khi đọc) trước khi T-017 nối nút "Mở nháp" vào giao diện.

## Các điểm T-020 được yêu cầu soi riêng

| Điểm | Kết quả | Bằng chứng |
|---|---|---|
| Khóa lộ ra giao diện | Không | Ô nhập luôn trống (không có `value=`). Trạng thái chỉ là huy hiệu cố định (`settings.py:72-75`). Thông báo là câu cố định hoặc lỗi `EnvFileError`. `test_settings_keys.py` (`assert_key_nowhere`) dò toàn bộ chữ trên trang và `session_state`, tìm cả khóa đầy đủ lẫn 4 và 6 ký tự cuối |
| Khóa lộ ra log | Không | Không có `logging`, `print`, `st.exception`, `st.json` trong `env_file.py`, `storage/`, `settings.py` (đã grep) |
| Khóa lộ ra thông báo lỗi | Không | Mọi `EnvFileError` là câu cố định, cùng lắm kèm `type(exc).__name__` (`env_file.py:51-79`, `:134-138`, `:201-203`). Đã chạy thử: khóa có chữ có dấu, `\n`, `\x00` khi kiểm tra đều bị thư viện gói thành `APIConnectionError`, và app trả câu cố định. Không có ngoại lệ thô nào lọt ra trang |
| Khóa lộ qua `repr` | Không | `Settings` đặt `repr=False` cho khóa (`config.py:52-54`). `KeyCheckResult` chỉ có `status` và `message`. Không đối tượng mới nào giữ khóa |
| Khóa lộ qua file tạm | Không | `mkstemp` tạo file quyền 600 ngay từ đầu, đặt cùng thư mục, tên `.env.*.tmp`. Tên này nằm trong `.gitignore` (`.env.*`). Lỗi thì xóa file tạm (`env_file.py:204-207`). `test_failed_replace_keeps_old_file_and_cleans_temp` qua |
| Chèn biến khác vào `.env` | Không chèn được | Xem trả lời điểm 2. Tên biến chỉ nhận đúng ba biến (`env_file.py:29`, `:48-51`) |
| Quyền 600 | Đạt | Đã chạy thử: file cũ quyền 644, sau khi ghi thành `0o600`. Không còn file tạm. Windows bỏ qua `chmod` (`:195`) |
| `os.replace` khi `.env` là symlink | Không ghi ra ngoài thư mục app | Xem lỗi #3 (Thấp) |
| Kiểm tra khóa Anthropic: timeout | Có | Client tạo với `timeout=15`, `max_retries=0` (`env_file.py:302`). Lời gọi `models.list(limit=1, timeout=…)` (`:304`). Địa chỉ mặc định của SDK là https, SDK kiểm tra chứng chỉ |
| Kiểm tra khóa Anthropic: `redact_secrets` | Có | Mọi nhánh trả kết quả đều qua `result()`, tức là qua `redact_secrets` (`:296-297`). Thêm vào đó, không nhánh nào chép thông điệp thô của thư viện (`:317-319`) |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Diff không có bí mật. detect-secrets báo 11 chỗ trong file mới, đã xem từng dòng và đều là chuỗi giả (`sk-ant-api03-ThuNghiemKhongPhaiKhoaThat…`, `mat-khau-thu-123`, `sk-ant-giả`…). Lịch sử git không có khóa thật và không có `.env`, `.sqlite`, file service account nào từng được thêm (`git log --all --diff-filter=A`) |
| S2 | Đạt | Xem bảng "Các điểm T-020" ở trên. `DraftError` chỉ nêu vị trí trường, không chép dữ liệu (`drafts.py:327-336`, `errors(include_input=False)`) |
| S3 | Không áp dụng | Không có biến `.env` mới. `ENV_VARS` và `.env.example` không đổi |
| W1 | Không áp dụng | Không đụng code WordPress hay `status` |
| W2 | Không áp dụng | Không đụng code WordPress |
| W3 | Không áp dụng (ghi chú) | Chưa có đường gửi bài. Ghi chú cho Giai đoạn 4: thân bài trong nháp có thể còn thẻ HTML (lỗi #1), nên khi gửi WordPress bắt buộc qua `sanitize_html` |
| W4 | Đạt | Lời gọi kiểm tra Anthropic có timeout 15 giây, không thử lại, dùng https của SDK, SSL bật mặc định (`env_file.py:302-304`) |
| A1 | Không áp dụng | Không đổi prompt |
| A2 | **Không đạt (Trung bình, lỗi #1)** | Kết quả AI đọc lại từ nháp chỉ được kiểm khuôn, chưa qua `clean_*` như lúc AI vừa trả về. AI không được thêm công cụ nào |
| A3 | Đạt | Khuôn nháp không có trường bí mật, `extra="forbid"` (`drafts.py:65-66`). Test `test_wrong_shape_draft_gives_friendly_error` có trường `api_key`. Khóa không bao giờ đi vào prompt |
| U1 | Đạt | Code mới trong `settings.py` không có `unsafe_allow_html`. Link "Lấy khóa ở" là hằng số (`settings.py:11-18`, `:76`) |
| U2 | Đạt | Trang Cài đặt nằm trong `PAGES` và chỉ hiện sau khi đăng nhập (`app/main.py:25-29`, `:72-78`). `server.address = "localhost"` (`.streamlit/config.toml`) |
| U3 | Đạt | Không đổi cách đăng nhập. `env_file` không ghi được `APP_PASSWORD_HASH` (`test_other_names_rejected`) |
| F1 | Đạt (ghi chú lỗi #3) | Đường dẫn `.env` cố định (`config.DEFAULT_ENV_FILE`). File tạm nằm cùng thư mục. Symlink không gây ghi ra ngoài thư mục app (đã chạy thử). Kho nháp dùng đường dẫn cố định `PROJECT_ROOT/data/drafts.sqlite`. File hỏng được đổi tên trong cùng thư mục (`drafts.py:297-305`). Mã nháp chỉ nhận đúng 32 ký tự hex (`:43`, `:56-59`) |
| F2 | Không áp dụng | Không đụng ảnh |
| F3 | Đạt | Đọc/ghi `.env` bằng `encoding="utf-8"` (`env_file.py:131`, `:191`). JSON nháp đọc bằng `model_validate_json`, có giới hạn 5 MB đo **trước khi** đọc (`drafts.py:216-222`). Không `pickle`, `eval`, `yaml.load`. SQL luôn dùng `?` (`test_storage_module_does_not_use_pickle_or_string_sql`) |
| D1 | Đạt | `pyproject.toml` và `uv.lock` không đổi. pip-audit trên 155 gói xuất từ `uv.lock`: 0 lỗ hổng |
| D2 | Đạt | `.gitignore` không đổi, vẫn chặn `.env`, `.env.*` (gồm cả file tạm `.env.*.tmp`), `data/`, `*.sqlite`, `*service-account*.json` |
| D3 | Đạt | `conftest.py` thêm `_never_touch_real_drafts`, trỏ kho nháp sang thư mục tạm. `_never_read_real_env` vẫn trỏ `.env` sang file tạm. Bộ chặn mạng `_block_real_network` vẫn còn. Test `test_check_with_real_client_class_hits_network_guard` chứng minh client thật bị chặn |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uvx pip-audit` (môi trường của công cụ): "No known vulnerabilities found". Chạy thêm `uvx pip-audit --no-deps --disable-pip -r <uv export --frozen>` (155 gói của dự án): "No known vulnerabilities found" | Có. Lần chạy thứ hai mới là kết quả cho thư viện của dự án |
| bandit | 1 cảnh báo Thấp: B101 `assert` ở `seo_app/storage/drafts.py:191` | Báo nhầm (xem dưới) |
| detect-secrets | Có kết quả trong `docs/team/reports/`, `tests/` và `seo_app/ai/base.py:22`. Riêng file mới: `tests/test_env_file.py:91,142,154,258,262`, `tests/test_settings_keys.py:17,18,19,180`, `tests/test_storage_drafts.py:273,327` | Đã xem từng dòng trong file mới: toàn bộ là chuỗi giả hoặc tên biến. Các kết quả cũ đã được xác minh ở biên bản trước |
| Soát lịch sử git | `git log -p` có chuỗi giống khóa, nhưng không có khóa thật (dạng `sk-ant-` hoặc `AIza` dài) ngoài test. Không file `.env`, `.sqlite` hay service account nào từng được thêm vào git | Có |
| pytest / ruff | `1804 passed, 13 xfailed in 97.97s` (đã gồm test đang làm của Soi Lỗi). `ruff check .`: All checks passed! | Có |

Chạy thử riêng (script trong thư mục nháp của phiên, không thêm vào repo, không gọi mạng thật):
- Symlink, symlink gãy, quyền 600, nháy không đóng, 9 giá trị cố chèn, 5 giá trị hợp lệ đọc lại bằng dotenv.
- `_check_anthropic` với khóa lạ, trỏ `ANTHROPIC_BASE_URL` về `127.0.0.1:9`.
- `DraftSnapshot.model_validate_json` với link, ảnh Markdown và thẻ HTML ở mọi trường.

## Báo nhầm đã loại

- **bandit B101** (`drafts.py:191`): `assert saved.saved_at is not None` chỉ để báo kiểu cho trình kiểm tra. Dòng 178 vừa đặt `saved_at` và dòng 181 đã kiểm khuôn lại. Bỏ `assert` khi chạy `-O` cũng không đổi hành vi.
- **detect-secrets "Basic Auth Credentials" ở `seo_app/ai/base.py:22`**: đây là chú thích mô tả mẫu `https://admin:matkhau@site` của `redact_secrets`, không phải mật khẩu.
- **detect-secrets ở các file test mới**: khóa giả cố ý để test chứng minh khóa không bị lộ.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

| Lỗi | Phải sửa ở | Hạn |
|---|---|---|
| #1 (Trung bình): lọc lại mọi chữ AI khi đọc nháp | Mở lại T-016 hoặc mở phiếu mới cho Thợ Máy | **Trước khi đóng T-017** (lúc nút Mở nháp xuất hiện trên giao diện), muộn nhất trước khi hết Giai đoạn 2 |
| #2 (Trung bình): nháy không đóng làm mất dòng trong `.env` | Phiếu sửa cho Thợ Máy (`seo_app/env_file.py`) | **Trước khi đóng T-017**, muộn nhất trước khi hết Giai đoạn 2. Trong lúc chờ: README hoặc trang Kết nối nên nhắc "đừng sửa tay `.env` khi đang dùng ô nhập khóa" |
| #3 (Thấp): symlink | Ghi vào sổ rủi ro nếu chủ dự án không muốn sửa | Không bắt buộc |

Sau khi sửa #1 và #2, Lá Chắn cần kiểm lại phần diff sửa.

---

## Lần 2 · Kiểm lại sau T-021, và kiểm T-017

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **Claude Opus 5.5 (chạy tạm)**. Model chuẩn Fable 5.1 vẫn bị giới hạn tới 01/11/2026 |
| Phiếu được kiểm | [T-021](../tickets/T-021-sua-loi-kho-nhap-va-env.md) (sửa lỗi #1, #2, #3 của lần 1), [T-017](../tickets/T-017-giao-dien-luu-nhap.md) (tự lưu, mở, xóa nháp trên trang Soạn bài) |
| Phạm vi | Thay đổi chưa commit trên `HEAD = 7f34728`: `seo_app/storage/drafts.py`, `seo_app/env_file.py`, `app/views/write.py`, `tests/conftest.py`, `tests/test_app_drafts.py`, `tests/test_env_file.py`, `tests/test_storage_drafts.py`. Đọc kèm `docs/team/reports/T-021-tho-may.md`, `T-017-hoa-si.md` |
| Ngày | 2026-10-14 |
| **Kết luận lần 2** | **ĐẠT**. Ba lỗi của lần 1 đã sửa đúng. Chỉ còn 2 lỗi Thấp, ghi vào sổ rủi ro hoặc sửa khi tiện, không chặn phiếu |

### Tóm tắt (cho chủ dự án)

Ba lỗi lần trước đã được sửa.
- Mở lại nháp thì mọi chữ do AI viết được lọc lại như lúc AI vừa trả về. Link lạ, ảnh từ máy chủ lạ hay mã HTML cài vào file nháp đều bị vô hiệu.
- Dòng khóa trong `.env` bị thiếu dấu nháy thì app báo lỗi và không đụng vào file. Mật khẩu WordPress và mật khẩu đăng nhập không thể bị xóa mất nữa.
- `.env` là liên kết tắt (symlink) thì app từ chối ghi.

Phần tự lưu, mở và xóa nháp trên trang Soạn bài cũng an toàn: không có đường nào để nháp hiện mã HTML, và test không ghi vào kho nháp thật. Còn hai điểm nhỏ, không nguy hiểm, có thể sửa sau.

### Kết luận theo phiếu

| Phiếu | Kết luận | Ghi chú |
|---|---|---|
| T-016 (kho nháp) | **ĐẠT** | Lỗi #1 đã sửa qua T-021 phần A |
| T-020 (nhập khóa API) | **ĐẠT** | Lỗi #2, #3 đã sửa qua T-021 phần B |
| T-021 (sửa lỗi) | **ĐẠT** | Về bảo mật đã đủ. Riêng để phiếu được tính **Xong** (`rules.md` mục 6), `uv run pytest` phải qua hết: hiện còn `test_round_trip_tricky_text_every_version` đỏ. Test này đòi đọc lại nguyên văn chữ chưa lọc, trái với yêu cầu lọc lại của lần 1. Chỉ Huy đã chốt giữ việc lọc, Soi Lỗi sửa test. Lá Chắn đồng ý: **không được** nới bộ lọc để test này qua |
| T-017 (giao diện nháp) | **ĐẠT** | Còn lỗi Thấp #4 |

### Lỗi đã sửa (xác minh lại)

| # lần 1 | Kết quả | Bằng chứng |
|---|---|---|
| #1 Chữ AI đọc từ nháp không được lọc lại | **Đã sửa** | `clean_loaded` (`seo_app/storage/drafts.py:326-367`) được gọi ở cuối `load` (`:249`). Lọc nghiên cứu bằng `clean_research`, rà soát bằng `clean_review`, tiêu đề bài và tiêu đề phần bằng `clean_ai_line`, ghi chú ảnh và ý dàn ý bằng `clean_ai_text`. Dàn ý dùng `unescape_link_syntax(clean_ai_line(...))`, khớp dạng ô sửa. Thân bài dùng `escape_link_syntax(strip_tags(...))`. **Đã chạy thử**: cài `[bấm](https://evil…)`, `![](https://t…/p.gif)`, `<img onerror>`, `<script>` vào mọi trường chữ, và URL đối thủ `javascript:`. Sau `clean_loaded`, các mẫu này chỉ còn ở những trường đã có lý do: `keyword`, `material` (chữ người dùng, hiện trong ô nhập), `research_keyword` (xem #4), `competitors[].title` (chỉ bỏ thẻ theo thiết kế, hiện qua `markdown_link` có escape), `review.flags[].sentence` (chỉ hiện khi là đoạn con của thân bài đã lọc, `write.py:176`, qua `quote_ai_text`), `ignored_flags` (chỉ dùng để so khớp). URL `javascript:` bị bỏ. Lọc chạy lúc **đọc**, nên khi siết bộ lọc thì nháp cũ cũng tự được lọc theo |
| #2 Nháy không đóng làm mất dòng `.env` | **Đã sửa** | `_build_content` tách file bằng chính bộ đọc của python-dotenv. Dòng của khóa đang ghi mà hỏng thì báo `EnvFileError` và không ghi (`env_file.py:134-141`). **Đã chạy thử** với `ANTHROPIC_API_KEY="sk-old` và 2 dòng bí mật phía sau. Cả Lưu và Xóa đều bị từ chối, file giữ nguyên từng byte, không còn file tạm. Dòng hỏng của **biến khác** không chặn việc ghi, và mọi biến khác dotenv đọc được vẫn giữ nguyên. Thêm hai lớp kiểm: so bằng `dotenv_values` trước khi ghi (`:186-189`) và sau khi ghi (`:193-204`); sai thì trả lại bản cũ. Quyền vẫn 600 |
| #3 `.env` là symlink | **Đã sửa** | `_read_env_text` từ chối mọi symlink, kể cả symlink gãy (`env_file.py:99-104`). Áp dụng cho cả Lưu và Xóa. **Đã chạy thử**: liên kết giữ nguyên, file đích không đổi, thông báo không chứa đường dẫn |

### Lỗi còn lại (lần 2)

| # | Mức | Mô tả | Vị trí | Đường đi thật | Cách sửa đề xuất |
|---|---|---|---|---|---|
| 4 | Thấp | `research_keyword` đọc từ nháp không được lọc. Trang hiện nó qua `st.warning`, tức là Markdown | `app/views/write.py:497-501`, `seo_app/storage/drafts.py:326-367` (`clean_loaded` không đụng trường này) | Sửa tay `data/drafts.sqlite` để `research_keyword` chứa link hoặc ảnh Markdown, mở nháp, rồi đổi từ khóa. Ô cảnh báo "Kết quả dưới đây là của từ khóa «…»" sẽ hiện link bấm được hoặc ảnh từ máy chủ lạ. Thẻ HTML không chạy. Muốn làm vậy phải ghi được file trên máy, và chỉ ảnh hưởng một dòng cảnh báo. Trước khi có nháp, giá trị này luôn là chữ người dùng tự gõ | Trong `clean_loaded`, xử lý `research_keyword` như `keyword`: chuẩn hóa về một dòng và bỏ thẻ. Hoặc hiện nó bằng `escape_markdown` (`seo_app/text.py`). Một dòng code, kèm một test |
| 5 | Thấp | `env_file.py` dùng `dotenv.parser.parse_stream`, một module con không ghi trong tài liệu chính thức của python-dotenv | `seo_app/env_file.py:29`, `:134` | Không phải đường tấn công, đây là rủi ro bảo trì. **Đánh giá:** (a) Phiên bản được cố định trong `uv.lock` (1.2.4). `uv sync` không tự nâng; `pyproject.toml` chỉ ghi `>=1.0`. (b) `parse_stream` là bộ đọc mà chính `dotenv_values` dùng bên trong, có từ bản 0.10 (2018) tới nay. (c) Nếu một bản sau đổi cách đọc, bước so bằng `dotenv_values` (API công khai) trước khi ghi sẽ thấy khác và **từ chối ghi**, nên lỗi an toàn: không làm hỏng `.env`, không lộ gì. (d) Nếu module bị xóa hẳn, `import` lỗi và trang Cài đặt không mở được: chỉ mất tính năng, test bắt ngay. **Kết luận: chấp nhận được, không cần sửa** | Khi nâng python-dotenv, chạy lại `tests/test_env_file.py` trước khi commit `uv.lock` mới. Lá Chắn sẽ soát điểm này mỗi lần `uv.lock` đổi |

### T-017: các điểm Chỉ Huy yêu cầu soát

| Điểm | Kết quả | Bằng chứng |
|---|---|---|
| Mọi chỗ hiển thị dữ liệu nháp | An toàn (trừ #4) | Danh sách nháp: tên và từ khóa lấy thẳng từ cột trong file (chưa lọc) nhưng hiện bằng `st.text`, không diễn giải Markdown hay HTML (`write.py:340-344`). Nhãn nút, popover, thông báo là chữ cố định. `recovered_from.name` do code tự đặt tên. Lỗi `DraftError` không chép dữ liệu từ file (`_short` chỉ nêu tên trường có trong khuôn, `drafts.py:389-410`). Nội dung đã mở đi qua các đường hiển thị sẵn có, và giờ dữ liệu đã được `clean_loaded` lọc trước. `keyword` hiện trong `ui.page_header` qua `html.escape` |
| `unsafe_allow_html` | Đạt | T-017 không thêm chỗ nào. Năm chỗ có sẵn trong `write.py` (`:612`, `:674`, `:698`, `:754`, `:791`) đều dùng `html.escape`, `ui.highlight` (escape toàn bộ, chỉ chèn `<mark>`), số nguyên đã kiểm khuôn, hoặc dữ liệu demo không đến từ nháp |
| Nháp độc có thể làm gì khi mở | Rất hạn chế | Kiểm khuôn chặt: `extra="forbid"`, `step` từ 0 đến 4, `current` nằm trong danh sách, mã nháp đúng 32 ký tự hex, tối đa 5 MB đo trước khi đọc. Sau đó lọc lại bằng `clean_loaded`. Chất liệu thật chỉ nhận nhãn đang có trên trang (`write.py:247-249`). Còn lại: (a) #4; (b) `keyword` và chất liệu thật bị sửa sẽ đi vào prompt AI. Đây là prompt injection, nhưng AI không có công cụ hành động thật (A2) và kết quả AI lại qua `clean_*`; (c) `flag.section` âm chỉ làm tô sai phần, không gây hại. Không có đường nào gửi lên WordPress (bước Xuất bản còn demo); khi làm thật vẫn bắt buộc qua `sanitize_html` (W3) |
| Test có thể lỡ ghi `data/` thật không | Không | Có ba lớp chặn: (1) fixture tự động `_never_touch_real_drafts` (`tests/conftest.py:52-61`) trỏ `seo_app.storage.drafts.DEFAULT_DRAFTS_FILE` sang thư mục tạm riêng từng test; (2) `write.py` đọc đường dẫn **lúc chạy** (`:200-202`), và `DraftStore()` cũng đọc lúc tạo (`default_factory`, `drafts.py:170`, sửa R8-4); (3) `st.cache_resource` lưu theo đường dẫn nên mỗi test có kho riêng. Không file nào dùng bản sao `seo_app.storage.DEFAULT_DRAFTS_FILE` (đã grep). Sau khi chạy toàn bộ test, `data/` rỗng (`ls -la data`). Theo báo cáo T-017, lúc 10:23 kho thật từng bị test ghi 4 nháp rác, xảy ra trước khi có fixture; Họa Sĩ đã xác minh là dữ liệu test và xóa. Không có bí mật nào trong đó, vì khuôn nháp không có chỗ cho bí mật |

### Danh sách kiểm tra (lần 2)

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets trên các file đổi: chỉ có chuỗi giả trong `tests/test_env_file.py` (`:479`, `:487`, `:498`, `:522` là `pbkdf2$x`, `sk-old`, đã xem từng dòng). `.gitignore` không đổi |
| S2 | Đạt | Mọi `EnvFileError` mới là câu cố định, không chứa giá trị hay đường dẫn. Cảnh báo của dotenv ("could not parse statement starting at line N") chỉ nêu số dòng, không nêu nội dung. Tự lưu nháp chỉ hiện chữ cố định hoặc `DraftError` |
| S3 | Không áp dụng | Không có biến `.env` mới |
| W1 | Không áp dụng | Không đụng WordPress |
| W2 | Không áp dụng | Không đụng WordPress |
| W3 | Không áp dụng (ghi chú) | Thân bài trong nháp đã được bỏ thẻ và escape link khi đọc. Khi làm bước Xuất bản vẫn bắt buộc qua `sanitize_html` |
| W4 | Đạt | Không đổi phần kiểm tra khóa Anthropic (timeout 15 giây, `max_retries=0`) |
| A1 | Không áp dụng | Không đổi prompt |
| A2 | Đạt | Lỗi #1 đã sửa: kết quả AI đọc lại từ nháp được lọc như lúc AI vừa trả về |
| A3 | Đạt | Khuôn nháp không có chỗ cho bí mật. Chất liệu thật có thể chứa thông tin khách, nhưng chỉ nằm trong `data/drafts.sqlite` trên máy (`.gitignore` chặn `data/`, `*.sqlite`) và đi vào prompt như trước đây |
| U1 | Đạt | Xem bảng T-017 ở trên |
| U2 | Đạt | Không đổi cách đăng nhập. Trang Soạn bài vẫn sau màn hình đăng nhập |
| U3 | Không áp dụng | Không đổi |
| F1 | Đạt | `.env` là symlink thì bị từ chối. Kho nháp dùng đường dẫn cố định. File hỏng đổi tên trong cùng thư mục. Xóa `data/` khi đang chạy thì kho tạo lại đúng chỗ cũ (`drafts.py:282-284`) |
| F2 | Không áp dụng | Không đụng ảnh |
| F3 | Đạt | Mọi chỗ đọc/ghi đều dùng UTF-8. Lỗi mã hóa khi lưu thành `DraftError` (`drafts.py:188-196`). Không `pickle`, `eval`. SQL luôn dùng `?`. Lệnh dọn nháp vẫn dùng tham số (`:220-224`) |
| D1 | Đạt | `pyproject.toml` và `uv.lock` không đổi so với lần 1; pip-audit lần 1 trên 155 gói của `uv.lock` vẫn còn hiệu lực: 0 lỗ hổng. `dotenv.parser` thuộc thư viện đã có, không phải thư viện mới (xem #5) |
| D2 | Đạt | `.gitignore` không đổi |
| D3 | Đạt | Xem "Test có thể lỡ ghi `data/` thật không" ở trên. Bộ chặn mạng trong `conftest.py` vẫn còn |

### Kết quả công cụ quét (lần 2)

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | Không chạy lại vì `uv.lock` không đổi so với lần 1 (`git diff HEAD -- uv.lock pyproject.toml` rỗng). Kết quả lần 1: 0 lỗ hổng | Có |
| bandit | 1 cảnh báo Thấp: B101 `assert` ở `seo_app/storage/drafts.py:203` | Báo nhầm như lần 1 (dòng chỉ dời chỗ) |
| detect-secrets | Chạy trên `seo_app/env_file.py`, `seo_app/storage/drafts.py`, `app/views/write.py`, `app/views/settings.py`, `tests/test_app_drafts.py`, `tests/test_env_file.py`: chỉ có chuỗi giả trong `tests/test_env_file.py` | Có, đã xem từng dòng |
| Soát lịch sử git | Không có commit mới chứa code (HEAD `7f34728` chỉ lập phiếu) | Có |
| pytest / ruff | `1 failed, 1833 passed, 3 xfailed in 78.83s`. Lỗi duy nhất là `test_round_trip_tricky_text_every_version`, bàn ở bảng kết luận T-021. `ruff check .`: All checks passed! | Có |

Chạy thử riêng (script trong thư mục nháp của phiên, không thêm vào repo, không gọi mạng):
- `clean_loaded` với link, ảnh Markdown, `<img onerror>`, `<script>`, `javascript:` ở mọi trường.
- `.env` có nháy không đóng (Lưu và Xóa).
- Dòng hỏng của biến khác.
- `.env` là symlink.
- Một dòng `ANTHROPIC_API_KEY=` nằm trong giá trị nhiều dòng của biến khác: được giữ nguyên, chỉ dòng thật bị thay.

### Điều kiện

Không có điều kiện bảo mật. Hai lỗi Thấp còn lại:
- **#4**: nên sửa cùng lần Thợ Máy chạm `clean_loaded` lần tới. Nếu không sửa thì Chỉ Huy hỏi chủ dự án để ghi vào sổ rủi ro.
- **#5**: đề nghị ghi vào sổ rủi ro (`security.md` mục 6) sau khi chủ dự án đồng ý: "Dùng `dotenv.parser.parse_stream` (module con không ghi trong tài liệu); lỗi an toàn nhờ bước so bằng `dotenv_values`; soát lại mỗi lần nâng python-dotenv."

Riêng việc đóng T-021 còn chờ Soi Lỗi sửa test `test_round_trip_tricky_text_every_version` để `uv run pytest` qua hết. Đây không phải điều kiện bảo mật.

# Biên bản bảo mật T-086 · Trạng thái gửi nháp không chỉ nằm trong phiên · rút gọn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem dòng trên) |
| Phiếu được kiểm | [T-086](../tickets/T-086-trang-thai-gui-nhap.md) · kiểm **rút gọn** (W1, W2, U1, F2) |
| Phạm vi | Diff `504ab15..801fbdf` (Họa Sĩ 6 commit, Soi Lỗi 2): `app/views/write.py`, `seo_app/storage/drafts.py` (chỉ phần trạng thái gửi), test mới `tests/test_t086_send_state.py`, `tests/test_storage_send_state.py`, `tests/test_soi_loi_t086.py`; gỡ `xfail` ở `tests/test_soi_loi_t056.py` (5 ca), `tests/test_la_chan_t056.py` (2 ca); `tests/test_app_images.py` (1 test so chữ đã escape); 2 báo cáo. Không đổi `seo_app/wordpress/**`, `seo_app/images/**`, `config/**`, `uv.lock`. Đọc thêm: `seo_app/wordpress/client.py` (`_positive_id` `:1718-1720`, `edit_link`), Streamlit 1.65.0 (`runtime/app_session.py:566-586`: `runner.fastReruns` mặc định bật, dừng lần chạy cũ và chạy lần mới ngay). Lá Chắn thêm `tests/test_la_chan_t086.py` (`7bed4a4`). Thử gộp với `origin/main` `9a1308d` rồi `1d37a07` (mới nhất, đã có T-085, T-087), `origin/team/T-085`, `origin/team/T-041`, `origin/team/T-087`. Số dòng theo `7bed4a4` (code ứng dụng như `801fbdf`) |
| Báo cáo đã đọc | [Họa Sĩ](T-086-hoa-si.md) (gồm Quyết định 1–7, fastReruns), [Soi Lỗi](T-086-soi-loi.md) (SL-T086-1, -2); điều kiện 2, LC-T056-1, Ghi nhận 1–3 của [Lá Chắn T-056](T-056-la-chan.md) |
| Ngày | 2026-10-26 (bắt đầu 10:53; làm tiếp 13:07 → 13:28 +07, giờ máy; phiên bị ngắt giữa chừng vì hết lượt dùng) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **3 Thấp** (1 mới: LC-T086-1; 2 của Soi Lỗi giữ Thấp: SL-T086-1, -2). LC-T056-1 và SL-T056-8, -9, -10, -11 **đã đóng** đúng điều kiện 2 (a)–(d) của biên bản Lá Chắn T-056. W1, W2, U1, F2 đạt. **Gộp `main` được ngay**: thử gộp với `origin/main` mới nhất `1d37a07` (đã có T-085, T-087) và `origin/team/T-041` không xung đột; 16 file test liên quan trên cây gộp 1.718 qua, 0 hỏng; ruff sạch |

## Tóm tắt (cho chủ dự án)

- Bản sửa làm đúng việc: app ghi «đang gửi» vào nháp trên máy **trước** khi gửi, và ghi «đã gửi, bài nháp mã …» ngay khi website trả lời. Tải lại trang, đóng tab, mở bài khác rồi mở lại, bấm liên tục hay bấm đúp lúc đang gửi: nút «Gửi nháp» luôn khóa, phải tick xác nhận mới gửi thêm. Cả 5 lỗi cũ (4 của Soi Lỗi, 1 của tôi) đã đóng. File ảnh bị thay bằng ảnh khác sau khi bạn duyệt (kể cả đúng lúc đang gửi) thì app dừng, chưa gửi gì, bắt xem lại.
- Chỗ ghi «đã gửi» trong nháp an toàn: bị sửa tay, hỏng thì app khóa nút và nhắc kiểm trang quản trị, không đoán. Mã bài ghi trong nháp chỉ dùng để hiện và mở link, **không bao giờ** dùng để sửa bài trên website: tôi thử ghi vào nháp mã của một bài khác rồi gửi lại, app không gửi lệnh nào tới bài đó. Nháp cũ vẫn mở bình thường.
- 1 lỗi nhỏ mới (Thấp): nếu website trả về một mã bài số cực lớn (chỉ xảy ra khi website hỏng hay bị chiếm) thì trang Soạn bài báo lỗi kỹ thuật và kẹt lỗi tới khi tải lại trang. Không gửi trùng, nút vẫn khóa. Sửa khoảng 2 dòng.
- 2 lỗi nhỏ Soi Lỗi tìm ra giữ mức Thấp: mở **cùng một bài ở hai tab** rồi bấm gửi ở cả hai cách nhau vài giây thì vẫn ra hai bài nháp; file ảnh bị thay **cố ý** (cùng dung lượng, cùng giờ sửa) trước khi chọn thì khung xem trước hiện ảnh cũ.
- Gộp vào `main` được ngay. Ba lỗi nhỏ sửa ở một phiếu sau. Lần gửi thật đầu tiên vẫn nên: một bài, một ảnh, **một tab**.

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T086-1 | Thấp | **Mã bài website trả từ 2⁶³ trở lên làm `record_outcome` ném lỗi ngoài khối bắt.** `record_outcome` dựng `SendState.now(pending, post_id)` **trước** `try` (`app/views/write.py:2169-2171`), mà `SendState.post_id` chỉ nhận `1 … 2⁶³−1` (`seo_app/storage/drafts.py:473-492`), còn client nhận mọi số nguyên dương của website (`_positive_id`, `client.py:1718-1720`). `ValidationError` thoát khỏi `send_and_record` (sau `finally` bật `done`), thoát khỏi `send_draft`; dấu `_wp_sending` còn, và `finish_send` (đầu `init_state`, `:2203`) gọi lại `record_outcome` ở **mọi** lần chạy sau | `app/views/write.py:2165-2178`, `:2233-2234` | Website (hỏng, bị chiếm, hay plugin lạ; WordPress lưu mã bài kiểu số không dấu 64 bit nên 2⁶³ vẫn là mã hợp lệ của site) trả `{"id": 9223372036854775808, "status": "draft"}` cho lệnh tạo nháp. Bài đã lên (1 bài), nháp giữ «đang gửi» (khóa vẫn đúng: mở lại là «gửi dở»). Nhưng trang Soạn bài hiện lỗi kỹ thuật kèm dấu vết lỗi (mặc định `client.showErrorDetails = "full"`, có đường dẫn file mã nguồn trên máy), và mọi lần chạy sau của phiên đều lỗi lại tới khi tải lại trang. Thử (test, WordPress giả): lần 1 lỗi; 3 lần chạy sau đều lỗi, `_wp_sending` còn; WordPress giả nhận đúng 1 bài. Xếp **Thấp**: cần website trả dữ liệu bất thường; không gửi trùng, không lộ bí mật; dấu vết lỗi chỉ hiện trên máy. Test `tests/test_la_chan_t086.py::test_lc_t086_1_huge_post_id_from_site_does_not_break_page` (`xfail(strict=True)`; `--runxfail` hỏng đúng câu kiểm «trang in dấu vết lỗi», sau khi đã kiểm 1 bài và nháp còn «đang gửi») | Trong `record_outcome`, dựng `SendState` **bên trong** `try` (lỗi dựng hay lỗi ghi đều thành `holder["note"]`, nháp giữ «đang gửi», trang hiện kết quả và khóa «gửi dở»). Thêm (không bắt buộc, phòng nhiều lớp): giới hạn trên cho `_positive_id` của client (phần T-085). Gỡ `xfail` khi XPASS |

Không phát hiện lỗi Nghiêm trọng, Cao hay Trung bình.

## Đối chiếu điều kiện 2 của biên bản Lá Chắn T-056 và các lỗi cũ

| Điều kiện / lỗi | Kết quả | Bằng chứng |
|---|---|---|
| **(a)** ghi «đang gửi / đã gửi (mã bài)» vào nháp **trước** khi gửi, đọc lại khi mở nháp (SL-T056-8, -11) | **Đạt** | `send_and_record` ghi `SendState(pending=True)` trước `create_draft_with_images` (`write.py:2123`, `:2137`); không ghi được thì **không gửi** (`:2122-2134`). Ghi kết quả ngay sau (`record_outcome` `:2172`). `draft_panel` đọc trạng thái trong nháp **mỗi lần vẽ** (`saved_send_state` `:2342`): `pending`, dòng hỏng → khóa «gửi dở»; có `post_id` → khóa «đã gửi» (`:2375-2384`). Bảng riêng `send_states` (`drafts.py:699`): lần tự lưu nháp không ghi đè, nháp cũ không có dòng nào thì như «chưa gửi». Test qua: `SL: test_switch_draft_and_back_keeps_send_lock[gui-xong, gui-do]`, `SL: test_new_session_after_send_needs_confirmation`, `T: test_pending_written_before_first_request`, `T: test_reopened_*`, `T: test_cannot_write_pending_does_not_send`; Soi Lỗi trình duyệt thật (F5 lúc đang gửi: phiên mới khóa «đã gửi», bài 505) |
| **(b)** đối tượng giữ kết quả, sửa tại chỗ (SL-T056-9) | **Đạt** | `holder` (dict) đặt vào phiên ở chỗ dừng cuối cùng trước khi gửi (`:2082`); `send_and_record`, `record_outcome` không đọc/ghi `st.session_state`, không gọi `st.*` (đọc mã `:2105-2178`); `done` bật trong `finally` (`:2086`). fastReruns: lần chạy mới chạy song song nên `finish_send` **đợi** `done` (tối đa 60 giây) rồi mới đọc kết quả (`:2203-2236`). Test qua: `SL: test_real_interruption_keeps_result`, `T: test_new_run_waits_for_send_still_running`, `SL: test_interrupt_at_each_write_after_send` (5 vị trí) |
| **(c)** thứ tự ghi khóa đơn điệu (LC-T056-1 a, b) | **Đạt** | (a) `finish_send` dựng khóa «gửi dở» và câu báo trước (`:2217-2218`), `apply_send` bỏ dấu `_wp_sending` sau cùng (`:2200`). (b) `draft_panel` bỏ tick hai ô rồi mới bỏ cờ `_wp_reset_guards` (`:2337-2340`). 2 test LC-T056-1 của tôi đã gỡ `xfail`, qua; `SL: test_double_interrupt_each_write` (ngắt lần hai ở từng lần ghi 1–7) qua |
| **(d)** băm nội dung ảnh lúc duyệt và ngay trước khi tải (SL-T056-10, Ghi nhận 1) | **Đạt trong phiên** (giới hạn: Ghi nhận 1, SL-T086-2) | `web_info` băm SHA-256 đúng byte đã đọc để ra dòng GPS (`:830-856`); lần duyệt gắn băm đó (`altsha-<id>`, `alt_editor` `:1176-1180`), bỏ duyệt, chọn ảnh khác, bỏ ảnh thì bỏ băm. `send_draft` băm **đúng byte đem nén và tải** (`:2040-2052`), khác thì dừng, chưa gửi gì, bỏ duyệt (`replaced_after_approval` `:2090-2103`): không còn khe giữa lúc so và lúc tải. Ảnh bị thay tại chỗ: ảnh xem trước dựng lại bằng `make_preview` (được phép theo LC-T058-2). Test qua: `SL: test_file_replaced_while_sending_stops`, `T: test_file_replaced_in_place_stops_and_shows_new_file`, `T: test_approval_bound_to_shown_version` |
| Ghi nhận 2 (lỗi lạ ở lần kiểm lại ảnh) | **Đóng** | `check_in_pool` bắt `Exception` → `MSG_CHECK_FAILED` (`:739-762`); `choose_image` cũng vậy (`:928-947`). `restore_images` cố ý không bọc (Họa Sĩ Quyết định 6): đồng ý, chưa có đường đi thật |
| Ghi nhận 3 (câu chưa escape) | **Đóng** | `row.error(escape_markdown(error))`, `st.warning(escape_markdown(listing.notice))` |

## Còn khe gửi trùng nào không

| Tình huống | Kết quả | Bằng chứng |
|---|---|---|
| Tải lại trang (F5), đóng tab lúc đang gửi | **Không trùng** | Lần gửi cũ chạy nốt (không chỗ dừng giữa ghi «đang gửi» và ghi kết quả), ghi kết quả vào nháp; phiên mới đọc từ nháp. Soi Lỗi, Họa Sĩ thử trình duyệt thật |
| App bị tắt hẳn (đóng cửa sổ chạy app, mất điện) lúc đang gửi | **Không trùng** | Nháp còn `pending=True` (ghi trước khi gửi) → mở lại: «gửi dở», khóa tới khi tick «Tôi đã kiểm tra…». `T: test_reopened_pending_draft_is_unsure` |
| Mở bài khác rồi mở lại | **Không trùng** | Khóa theo trạng thái của từng nháp, không theo phiên |
| Bấm liên tục, bấm đúp (fastReruns) | **Không trùng** | Đọc mã: lần chạy cũ bị `request_stop` chỉ dừng ở chỗ dừng kế tiếp. Từ lúc bấm tới `S._wp_sending = holder` (`:2082`, chỗ dừng cuối) luôn còn chỗ dừng (`S.get("altsha-…")` trong vòng nén ảnh, `sent_title()`), nên lần cũ bị dừng **trước** khi gửi nếu lần mới đã bắt đầu; nếu lần cũ đã qua `:2082` thì lần mới thấy dấu, đợi, rồi khóa «gửi dở». Soi Lỗi bấm 3 lần liên tiếp trên trình duyệt thật: 1 bài |
| Lần chạy bị ngắt hai lần liên tiếp | **Không trùng** | Thứ tự đơn điệu (điều kiện c); `SL: test_double_interrupt_each_write` × 7, 2 test LC-T056-1 |
| Hai tab cùng một nháp, bấm gửi cách nhau vài giây | **Còn trùng** | SL-T086-1 (Thấp, giữ mức) |

## Trạng thái gửi trong nháp đọc an toàn

- **Khuôn chặt:** `SendState(_Strict)` (`extra="forbid"`), `pending` bool chặt, `post_id` số nguyên chặt `1 … 2⁶³−1`, `updated_at` phải có múi giờ; **không có trường chữ** nên không có chữ thô nào từ file hiện ra giao diện (U1). `DraftSnapshot` không đổi khuôn (vẫn `extra="forbid"`).
- **Đọc phòng thủ:** `load_send_state` đo cỡ dòng trước khi đọc (≤ 4 KB), dữ liệu `NULL`, số, `blob` lạ, JSON sai đều thành `DraftError` câu cố định (`drafts.py:626-651`); giao diện coi là «chưa rõ» và **khóa** (`saved_error`), câu báo cố định. Soi Lỗi thử 14 kiểu sửa tay (kiểu sai, `post_id` 0/âm/thập phân/chuỗi/2⁶³, giờ không múi, trường lạ, thiếu trường, 5.000 byte, kiểu cột số…): khóa, không request nào.
- **Nháp cũ:** bảng mới tạo thêm khi mở (`CREATE TABLE IF NOT EXISTS`), file cũ không bị cất sang một bên; Soi Lỗi tạo file bằng chính mã `main` `504ab15` rồi mở bằng mã mới: đọc được. `_is_healthy` kiểm thêm cột bảng `send_states`: bảng bị sửa sai cột thì cả file bị cất sang một bên như mọi file hỏng (không còn nháp để gửi lại, nên không mở khóa nhầm).
- **Ngoài phạm vi phòng:** ai sửa được `data/drafts.sqlite` (xóa dòng, ghi «chưa gửi») thì mở được khóa. Khóa này chống bấm nhầm, không chống người đã có quyền ghi file trên máy (cùng loại các rủi ro đã ghi sổ ở `security.md` mục 6).

## Mã bài, link (U1, W2)

- Mã bài hiện ra là số nguyên (từ `SendState` hay từ client), qua `escape_markdown` (`sent_message` `:2267-2279`, `send_result`). Link «Mở bài nháp trong WordPress» của nháp mở lại dựng bằng `client.edit_link(post_id)` (`:2382`): địa chỉ từ `WORDPRESS_URL` cộng số, không lấy chữ nào từ file nháp.
- Mã bài trong nháp chỉ dùng để hiện, dựng link và ghi lại vào «đang gửi» lần sau (`previous_post`); **không** đi vào lệnh ghi nào lên website (soát mọi chỗ dùng `post_id`, `previous_post` trong `write.py`). Thử (`tests/test_la_chan_t086.py::test_saved_post_id_never_used_to_write_to_wordpress`, đang qua): nháp ghi «đã gửi, bài 777», mở lại ở phiên mới: khóa «đã gửi», link `…/post.php?post=777&action=edit`; tick «Tạo thêm…», gửi: chỉ `POST /wp/v2/posts` tạo bài mới và tải ảnh, không lệnh nào tới bài 777; nháp ghi bài mới 501.
- W1: vẫn chỉ `create_draft_with_images` (bài luôn `draft`); không thêm đường `publish`/`future`.

## Mức SL-T086-1, -2

| Mã | Mức Lá Chắn | Lý do |
|---|---|---|
| SL-T086-1 (hai tab cùng nháp, bấm gửi cách nhau vài giây: hai bài) | **Thấp** (giữ) | Cần mở cùng một bài ở hai tab và bấm gửi ở cả hai trong lúc tab kia còn kiểm lại, nén ảnh. Hậu quả như các lỗi trùng cũ: bài nháp thứ hai, cùng ảnh tải lần hai (ảnh đã công khai từ lần đầu, không lộ thêm), không đăng công khai, không ghi đè. Cách sửa «so rồi đặt» trong một giao dịch SQLite của Soi Lỗi là đúng và đủ (mọi tab trên một máy cùng đi qua một file) |
| SL-T086-2 (file bị thay tại chỗ, cùng cỡ, cùng giờ sửa **trước** khi chọn: khung xem trước hiện ảnh cũ từ cache, băm và dòng GPS của ảnh mới) | **Thấp** (giữ) | Phải **cố ý** đặt lại giờ sửa và giữ đúng dung lượng, tức là đã có quyền ghi thư mục ảnh (làm được nhiều hơn mà không cần khe này). Dòng GPS vẫn đúng ảnh sẽ tải. Cách sửa của Soi Lỗi (ảnh xem trước dựng từ đúng byte đã băm) là đúng |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `PYTHONUTF8=1 uvx detect-secrets scan` 11 file đổi và test của Lá Chắn: `{}`; dòng thêm trong `git log -p 504ab15..HEAD` không có khóa |
| S2 | Đạt (kèm LC-T086-1) | Câu lỗi mới cố định (`MSG_*`, `DraftError`); LC-T086-1 để lộ dấu vết lỗi (đường dẫn mã nguồn, không bí mật) |
| S3 | Không áp dụng | Không biến cấu hình mới |
| W1 | Đạt | Mục «Mã bài, link» |
| W2 | Đạt | Không lệnh sửa, xóa nào mới; mã bài trong nháp không dùng để ghi (có test) |
| W3 | Không áp dụng | Nội dung gửi đi không đổi cách dựng (`article_parts`) |
| W4 | Không áp dụng | Không đổi client |
| A1, A2 | Không áp dụng | Không đổi phần AI |
| A3 | Đạt (không đổi) | AI vẫn chỉ nhận byte `make_ai_image` khi bấm |
| U1 | Đạt | Không thêm `unsafe_allow_html`; chữ mới là câu cố định, số, giờ, qua `escape_markdown`; thêm escape cho 2 chỗ cũ (Ghi nhận 3) |
| U2 | Đạt (kèm LC-T086-1) | Trang vẫn sau đăng nhập; không đường dẫn ảnh, không nội dung `.env` |
| U3 | Không áp dụng | — |
| F1 | Đạt | Mọi lần đọc ảnh mới (`web_info`, băm lúc gửi, `make_preview` cho ảnh bị thay) đều qua `ImageLibrary.read_image_bytes` |
| F2 | Đạt | Băm đúng byte đem nén, tải; giới hạn cỡ, điểm ảnh của `ImageLibrary`, `process.py` không đổi; ảnh web vẫn giữ GPS |
| F3 | Đạt | `SendState` đọc bằng `model_validate_json` khuôn chặt; không `eval`, `pickle` |
| D1 | Đạt | Không thư viện mới (`hashlib`, `threading` có sẵn); `uv.lock` không đổi |
| D2 | Đạt | `.gitignore` không đổi; test dùng kho nháp tạm |
| D3 | Đạt | Test dùng WordPress giả, AI giả; WordPress giả của phần thử trình duyệt chỉ nghe `127.0.0.1` |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| detect-secrets | `{}` (11 file đổi, `tests/test_la_chan_t086.py`, biên bản này), `PYTHONUTF8=1` | — |
| bandit | `uvx bandit -r app/views/write.py seo_app/storage/drafts.py`: 1 Low B101 (`assert`) ở `drafts.py:535` | Có từ trước (`504ab15` dòng 505), không thuộc phiếu |
| pip-audit | Không chạy lại: `uv.lock` không đổi, cả trên `main` mới nhất `1d37a07` (lần quét gần nhất 2026-10-26 sáng, 0 lỗ hổng, biên bản T-056) | `git diff 504ab15 origin/main -- uv.lock`: rỗng |
| ruff | `uv run ruff check .`: All checks passed! | — |
| pytest (nhánh, `7bed4a4`) | 11 file (7 file tiêu chí xong của phiếu + `tests/test_t086_send_state.py`, `tests/test_storage_send_state.py`, `tests/test_soi_loi_t086.py`, `tests/test_la_chan_t086.py`), `PYTHONUTF8=1`: **542 passed, 1 skipped, 3 xfailed, 0 failed** (646,6 s). 3 xfail: SL-T086-1, SL-T086-2, LC-T086-1. `tests/test_la_chan_t086.py` riêng: 1 passed, 1 xfailed; `--runxfail -k lc_t086_1`: hỏng đúng câu kiểm «trang in dấu vết lỗi» | Test nháp (không commit, đã xóa): sau lỗi đầu, 3 lần chạy sau đều lỗi, `_wp_sending` còn, WordPress giả nhận 1 bài |
| pytest (cây gộp) | Mục «Thử gộp» | — |

## Thử gộp

Làm trên worktree tạm (detached, thư mục nháp của Lá Chắn), không đụng repo chính; xong đã gỡ (`git worktree remove`).

| Việc | Kết quả |
|---|---|
| `git merge-tree --write-tree` của `team/T-086` với `origin/main` (`9a1308d`), `origin/team/T-041`, `origin/team/T-087`, `origin/team/T-085` | Không xung đột chữ. T-041 sửa `drafts.py` ở phần SEO (`DraftSeo`, `DraftLink`…), không đụng bảng `send_states`, `save`, `delete`, `_is_healthy`: Git tự gộp |
| Lần 1: `7bed4a4` + `origin/main` `9a1308d` + `origin/team/T-085` (`0d453d9`) + `origin/team/T-041` (`5cf42bc`); 15 file test (11 file ở trên, `test_t041_drafts_seo`, `test_wordpress_t085`, `test_wordpress_client`, `test_wordpress_images`) | **1.013 passed, 1 skipped, 3 xfailed, 0 failed** (672,5 s); 3 xfail như trên nhánh. `ruff`: All checks passed! |
| Lần 2: `7bed4a4` + `origin/main` mới nhất `1d37a07` (đã gộp T-085, T-087) + `origin/team/T-041` (`c059b41`); 16 file test (như lần 1, thêm `test_soi_loi_t085`) | **1.718 passed, 1 skipped, 39 xfailed, 0 failed** (1.123,3 s). 39 xfail đều có sẵn: 3 của T-086 (SL-T086-1, -2, LC-T086-1), 36 của T-085 (SL-T085-1 × 30, SL-T085-2 × 3, SL-T085-3 × 6). `ruff`: All checks passed! Không xung đột |

`_positive_id` của client trên `main` mới nhất vẫn không có giới hạn trên (`client.py:1802-1804`), nên LC-T086-1 vẫn còn sau khi gộp T-085.

## Báo nhầm đã loại

- bandit B101 `assert saved.saved_at is not None` (`drafts.py:535`): có từ trước phiếu, chỉ là kiểm nội bộ, không phải đường bảo mật.

## Ghi nhận (không phải lỗi)

1. **Băm chỉ nhớ trong phiên** (Họa Sĩ Quyết định 4): nháp mở lại ở phiên khác mà không xem lại khung ảnh ở bước Viết & kiểm tra thì lần gửi chỉ so cỡ, giờ sửa, định danh như T-056; ảnh bị thay giữa hai phiên không bị bắt (phần còn lại của SL-T056-2). Đồng ý đề xuất phiếu Thợ Máy lưu băm đã duyệt trong `DraftImage`. Cách tạm nếu muốn sớm: khi mở lại nháp, ảnh chưa có băm duyệt trong phiên thì bỏ «Đã duyệt» (bắt xem lại khung ảnh).
2. **Phiếu sau dùng mã bài (T-041, Giai đoạn 5):** không được dùng `SendState.post_id` để ghi gì lên website (SEO, ảnh đại diện, đăng); chỉ ghi vào bài chính client vừa tạo trong lần làm việc này (`_created_post_ids` của client, giữ như hiện nay).
3. Lần chạy mới đợi lần gửi song song tối đa 60 giây (`SEND_WAIT_SECONDS`); website chậm hơn thì trang báo «vẫn đang chạy», giữ dấu. Chỉ ảnh hưởng tính sẵn sàng.
4. `tests/test_la_chan_t056.py`: docstring đầu file còn nói hai ca LC-T056-1 «đánh dấu `xfail`» sau khi đã gỡ dấu. Không ảnh hưởng gì; sửa khi tiện.
5. Hai máy: nháp chỉ nằm trên máy đang dùng (không đồng bộ), nên khóa «đã gửi» không sang máy kia; viết cùng một bài trên hai máy là hai nháp khác nhau (đúng thiết kế).

## Điều kiện

1. **Gộp `main`:** được ngay, không lỗi nào phải sửa trước. Chỉ Huy chạy toàn bộ pytest trên Windows khi gộp như thường lệ. Nếu gộp sau T-085 hay T-041: đã thử gộp cả hai, không xung đột (mục «Thử gộp»).
2. **Phiếu sửa sau (Chỉ Huy lập; Họa Sĩ `write.py`, phần trạng thái gửi `drafts.py`), trước khi hết Giai đoạn 3:**
   - **LC-T086-1** (Thấp): dựng `SendState` trong `try` của `record_outcome` (cột «Cách sửa»); gỡ `xfail` của `tests/test_la_chan_t086.py` khi XPASS.
   - **SL-T086-1** (Thấp): ghi «đang gửi» kiểu «so rồi đặt» trong một giao dịch SQLite (gợi ý của Soi Lỗi).
   - **SL-T086-2** (Thấp): ảnh xem trước dựng từ đúng byte đã băm (gợi ý của Soi Lỗi).
   - Giữ các test mới của T-086 (ngắt ở từng lần ghi, ngắt hai lần, trạng thái sửa tay, mã bài trong nháp không dùng để ghi). Soi Lỗi, Lá Chắn rút gọn.
3. **Thợ Máy (phiếu nhỏ, cần chủ dự án duyệt):** lưu băm ảnh đã duyệt trong `DraftImage` (Ghi nhận 1; phần còn lại của SL-T056-2). Thêm, không bắt buộc: giới hạn trên cho `_positive_id` của client (phòng nhiều lớp cho LC-T086-1).
4. **T-041 và các phiếu Giai đoạn 5:** giữ Ghi nhận 2 (không dùng mã bài trong nháp để ghi lên website).
5. **Lần gửi thật đầu tiên (T-059):** một bài, một ảnh, **một tab** (tới khi SL-T086-1 xong).
6. **Thư Ký, sau khi gộp T-086:** viết lại khối «Lời dặn tạm thời» của README (điều kiện 3 biên bản Lá Chắn T-087): nay app nhớ việc gửi qua tải lại trang, mở bài khác; vẫn dặn đừng mở cùng một bài ở hai tab rồi bấm gửi ở cả hai (SL-T086-1).
7. **Lá Chắn:** kiểm lại biên bản này bằng Claude Fable sau 01/11.

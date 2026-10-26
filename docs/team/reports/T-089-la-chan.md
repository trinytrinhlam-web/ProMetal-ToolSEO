# Biên bản bảo mật T-089 · Dọn lỗi Thấp gửi nháp sau T-086, băm ảnh đã duyệt trong nháp · rút gọn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem dòng trên) |
| Phiếu được kiểm | [T-089](../tickets/T-089-gui-nhap-loi-thap-sau-t086.md) · kiểm **rút gọn** (W1, W2, U1, F2) |
| Phạm vi | Diff `3d7f4b7..66131e5` (Họa Sĩ 7 commit, Soi Lỗi 4): `app/views/write.py`, `seo_app/storage/drafts.py` (phần trạng thái gửi và `DraftImage`), test mới `tests/test_t089_send_draft.py`, `tests/test_soi_loi_t089.py`; gỡ `xfail` ở `tests/test_la_chan_t086.py` (1 ca), `tests/test_soi_loi_t086.py` (2 ca); `tests/test_t086_send_state.py`, `tests/test_app_images.py` (sửa nhỏ, mục «Soát R5»); 2 báo cáo. Không đổi `seo_app/wordpress/**`, `seo_app/onpage/**`, `config/**`, khối SEO của `drafts.py`, `uv.lock`. Python 3.12.15, SQLite 3.53.1. Thử gộp với `origin/main` `e295f0e`, `origin/team/T-088` `7e1fdae`, `origin/team/T-041` `a88c6e5` (và đầu mới `ee1de90`). Số dòng theo `66131e5` |
| Báo cáo đã đọc | [Họa Sĩ](T-089-hoa-si.md) (Quyết định 1–9, Rủi ro 1–5), [Soi Lỗi](T-089-soi-loi.md) (SL-T089-1); điều kiện 2, 3 của [Lá Chắn T-086](T-086-la-chan.md) |
| Ngày | 2026-10-26 (19:22 → 19:51 +07, giờ máy) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (SL-T089-1 của Soi Lỗi, giữ Thấp); Lá Chắn không có lỗi mới. LC-T086-1, SL-T086-1, SL-T086-2 **đã đóng** đúng điều kiện 2 biên bản Lá Chắn T-086; băm ảnh đã duyệt trong nháp đạt điều kiện 3 (phần băm). Ghi nhận 2 (mã bài trong nháp không dùng để ghi lên website) vẫn giữ. W1, W2, U1, F2 đạt. **Gộp `main` được ngay**: thử gộp với `origin/main` `e295f0e`, `team/T-088`, `team/T-041` không xung đột; 15 file test liên quan trên cây gộp 1.210 qua, 0 hỏng; T-041 lên `ee1de90` thử lại: 17 file 1.394 qua, 0 hỏng; ruff sạch |

## Tóm tắt (cho chủ dự án)

- Bản sửa an toàn để gộp. Ba lỗi nhỏ còn lại của lần trước đã đóng: mở **cùng một bài ở hai tab** rồi bấm gửi gần nhau nay chỉ ra **một** bài nháp (tab bấm sau báo rõ và khóa nút); website trả mã bài lạ thì trang không còn lỗi kỹ thuật, nút vẫn khóa; khung ảnh luôn hiện đúng bản ảnh app đã kiểm và bạn đã duyệt.
- App nay nhớ «dấu vân tay» của ảnh lúc bạn duyệt alt **ngay trong nháp**: mở lại bài hôm khác mà ảnh trên máy đã bị thay bằng ảnh khác cùng tên thì app bỏ «Đã duyệt», bắt xem lại; bấm gửi thẳng thì app dừng, chưa gửi gì. Bài lưu từ bản cũ: phải tick «Đã duyệt» lại một lần. Dấu vân tay này chỉ nằm trên máy, không gửi lên website hay hãng AI.
- Còn 1 lỗi nhỏ (Thấp, Soi Lỗi tìm ra): hai tab cùng gửi một bài, tab bị từ chối mà **đúng lúc đó** lại bị bấm thêm (trong vài phần nghìn giây) thì app xóa mất ghi chú «đã gửi» của tab kia; mở lại bài thì không còn bị khóa. Rất khó gặp, sửa nhỏ; nên sửa ở lượt sau. Tới lúc đó vẫn nên gửi ở **một tab**.

## Lỗi phát hiện

Không phát hiện lỗi mới (Lá Chắn). Lỗi của Soi Lỗi: mục «Mức SL-T089-1».

## Đối chiếu điều kiện 2, 3 của biên bản Lá Chắn T-086

| Điều kiện / lỗi | Kết quả | Bằng chứng |
|---|---|---|
| **LC-T086-1** (mã bài website từ 2⁶³ làm `record_outcome` ném lỗi ngoài khối bắt, trang lỗi lặp lại) | **Đóng** | `SendState.now(...)` nay nằm trong `try` (`write.py:2248-2249`); `ValidationError` (dạng `ValueError`) → `note` câu cố định `MSG_POST_ID_OUT_OF_RANGE` (`:176`, `:2253-2254`); nháp giữ «đang gửi» nên nút vẫn khóa «gửi dở» (mở lại cũng vậy); `finish_send` thử ghi lại một lần cũng chỉ ra câu đó rồi `apply_send` bỏ dấu, không lặp lỗi. Test của tôi `tests/test_la_chan_t086.py::test_lc_t086_1_huge_post_id_from_site_does_not_break_page` gỡ `xfail` (chỉ xóa dấu), qua; Soi Lỗi thêm 2⁶⁴, 10³⁰, ngắt ở từng lần ghi, mã âm/0/chữ/số thực; Họa Sĩ thử trình duyệt thật (mã 9223372036854775808: trang không lỗi, log app, console không lỗi) |
| **SL-T086-1** (hai tab cùng bài ra hai bài) | **Đóng** (còn SL-T089-1, Thấp) | `save_send_state(…, expected=…)` (`drafts.py:658-692`): `BEGIN IMMEDIATE` giữ khóa ghi từ lúc đọc tới lúc ghi (`:677`), đọc bằng `_read_send_state` (`:747`), khác trạng thái người dùng thấy thì **không ghi, trả `False`** (`:683`); `with conn` của `_connect` (`:697-709`) commit, lỗi khóa quá 5 giây thành `DraftError`. `send_and_record` ghi «đang gửi» với `expected=seen` (`write.py:2190-2192`); không ghi được thì **không gửi**, báo `MSG_SENT_ELSEWHERE` (`:186`, `:2205-2208`). `seen` là trạng thái ở **lần vẽ người dùng đã thấy** (`_wp_seen`, `:2427-2428`): ô «Tạo thêm…» hay «Tôi đã kiểm tra…» tick sẵn cho trạng thái cũ không được dùng cho lần gửi tab kia vừa mở ra (đọc mã: `allowed` theo lần đọc lúc bấm, CAS theo lần vẽ trước, hai khóa khác nhau thì không gửi). Test qua: Soi Lỗi `test_other_tab_starts_sending_while_this_tab_prepares` (gỡ `xfail`), `test_two_sessions_take_turns_one_post_per_round`, `test_other_session_completes_send_while_this_one_prepares`; Họa Sĩ `test_only_one_tab_wins` (4 luồng, đọc chậm lại: đúng 1 luồng ghi được); trình duyệt thật (Họa Sĩ, Soi Lỗi): hai tab bấm gần nhau, 1 bài |
| **SL-T086-2** (khung xem trước từ cache theo cỡ, giờ sửa, khác bản đã băm) | **Đóng** | `web_info` đọc file **một lần**: băm, `make_preview` trên đúng byte đó (`write.py:871-903`, `:890`), rồi nén thử để ra dòng GPS; `slot_preview` hiện ảnh xem trước của `web_info` (`:1063-1066`). `st.image` vẫn chỉ nhận ảnh JPEG do app tạo (`make_preview` được phép theo LC-T058-2); lưới chọn ảnh vẫn dùng `PreviewCache`. Test qua: Soi Lỗi `test_preview_shown_matches_approved_content` (gỡ `xfail`), `test_file_replaced_between_view_and_approval`; Họa Sĩ `test_chosen_preview_built_from_hashed_bytes` |
| **Điều kiện 3, phần băm** (lưu băm ảnh đã duyệt trong `DraftImage`) | **Đạt** | Trường tùy chọn `approved_sha256` (`drafts.py:238`), chỉ nhận đúng 64 chữ số hex thường (`:100`, `:273-277`), chỉ đi cùng lần duyệt của ảnh trong thư mục ảnh (`:291-292`), trống thì không ghi vào JSON (nháp giữ khuôn cũ). Mở nháp: `set_pick` khôi phục băm (`write.py:731-734`); nháp không có băm thì bỏ «Đã duyệt», báo một lần (`:487-491`); khung ảnh khác băm thì bỏ duyệt trước khi vẽ ô (`:1217-1223`); lần gửi so byte sắp tải với băm (`:2108-2109`), kể cả khi gửi thẳng ở bước Xuất bản sau khi mở lại nháp (đóng Ghi nhận 1 của biên bản T-086). Test qua: Họa Sĩ 11 ca khuôn băm, mở lại nháp (cùng file, file bị thay, nháp cũ); Soi Lỗi 9 kiểu băm sửa tay (chữ hoa, 63 ký tự, không phải hex, số, `null`, list, dict, xuống dòng, 100.000 ký tự: ảnh giữ, bỏ duyệt), băm đúng dạng nhưng sai file (gửi thẳng: dừng, 0 request) |
| **Ghi nhận 2** (mã bài trong nháp không dùng để ghi lên website) | **Giữ** | Mã bài trong nháp vẫn chỉ để hiện, dựng link `client.edit_link`, ghi lại vào «đang gửi» lần sau; mã bài lạ chỉ hiện ra (số), không ghi vào nháp. Test của tôi `test_saved_post_id_never_used_to_write_to_wordpress` qua |

## Mức SL-T089-1

| Mã | Mức Lá Chắn | Lý do |
|---|---|---|
| SL-T089-1 (tab thua «so rồi đặt» mà lần chạy bị ngắt ngay sau đó: `finish_send` ghi trạng thái của tab này, xóa hay ghi đè «đang gửi»/«đã gửi» của tab kia) | **Thấp** (giữ) | Đúng như Soi Lỗi tả, tôi đọc lại mã: `send_and_record` không gọi `record_outcome` khi thua (`write.py:2205-2208`), nhưng `finish_send` gọi lại cho mọi `holder` có `result` mà chưa `saved` (`:2315-2316`), với `state = (False, previous_post)` → xóa dòng (hay ghi mã cũ). Cần đủ: cùng một bài ở hai tab, tab này thua, **và** một cú bấm nữa tới đúng khe vài mili giây giữa lúc thua và lúc `apply_send` bỏ dấu (tới 5 giây nếu file nháp bận). Hậu quả như các lỗi trùng cũ: mất khóa, bấm gửi tiếp là bài nháp thứ hai, cùng ảnh tải lần hai (ảnh đã công khai từ lần đầu, không lộ thêm); không đăng công khai, không ghi đè bài có sẵn. Cách sửa của Soi Lỗi (`holder["claimed"]`, `finish_send` chỉ ghi lại khi `claimed`; nên thêm ghi kết quả kiểu so rồi đặt) là đúng và đủ |

## Băm trong nháp đọc an toàn; nháp cũ

- Băm từ file nháp là dữ liệu chưa tin cậy: chỉ nhận đúng dạng hex, sai dạng thì **bỏ băm, giữ ảnh, bỏ duyệt** (không đoán, không bỏ cả bài); chỉ dùng để **so**, không bao giờ thay cho lần đọc file thật. Băm không hiện ra giao diện (U1), không gửi lên WordPress hay hãng AI (soát mọi chỗ dùng `approved_sha256`, `altsha-` trong `write.py`; `seo_app/wordpress/**`, `seo_app/images/alt.py` không có).
- Nháp cũ (không có trường): mở bình thường, ảnh có alt đã duyệt bị bỏ duyệt một lần (không so được với lúc duyệt): hướng an toàn. `extra="forbid"` của `DraftImage`, `DraftSnapshot` giữ nguyên. Bản app **cũ** mở nháp có băm thì bỏ ảnh đó như ảnh hỏng (phần chữ giữ): chỉ khi quay về bản cũ, chấp nhận.
- Ngoài phạm vi phòng: ai sửa được cả thư mục ảnh lẫn `data/drafts.sqlite` (ghi băm đúng của ảnh đã tráo) thì qua được lớp so này; người đó đã có quyền ghi trên máy (cùng loại các rủi ro trong sổ `security.md` mục 6).

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `PYTHONUTF8=1 uvx detect-secrets scan` 10 file đổi: `{}`; biên bản này: `{}` |
| S2 | Đạt | Câu mới đều cố định (`MSG_POST_ID_OUT_OF_RANGE`, `MSG_SENT_ELSEWHERE`, `MSG_APPROVED_OTHER_VERSION`, `MSG_OLD_APPROVAL` với số ảnh); LC-T086-1 (dấu vết lỗi) đã đóng |
| S3 | Không áp dụng | Không biến cấu hình mới |
| W1 | Đạt | Vẫn chỉ `create_draft_with_images` (bài luôn `draft`); so rồi đặt chỉ chặn thêm (không ghi được «đang gửi» thì không gửi) |
| W2 | Đạt | Không thêm lệnh sửa, xóa nào lên website; Ghi nhận 2 giữ (có test) |
| W3, W4 | Không áp dụng | Không đổi nội dung gửi, không đổi client |
| A1, A2 | Không áp dụng | Không đổi phần AI |
| A3 | Đạt (không đổi) | Băm không gửi AI; AI vẫn chỉ nhận byte `make_ai_image` khi bấm |
| U1 | Đạt | 7 chỗ `unsafe_allow_html` như `main` `3d7f4b7`, không thêm chỗ nào; chữ mới là câu cố định, số |
| U2 | Đạt | Không đường dẫn, không nội dung `.env` |
| U3 | Không áp dụng | — |
| F1 | Đạt | Mọi lần đọc ảnh mới (`web_info`) qua `ImageLibrary.read_image_bytes` |
| F2 | Đạt | Ảnh xem trước, băm, dòng GPS cùng một lần đọc; giới hạn cỡ, điểm ảnh không đổi; ảnh web vẫn giữ GPS |
| F3 | Đạt | Băm đọc bằng khuôn pydantic chặt; không `eval`, `pickle` |
| D1 | Đạt | Không thư viện mới (`Field(exclude_if=…)` của pydantic đã có trong `uv.lock`); `uv.lock` không đổi |
| D2 | Đạt | `.gitignore` không đổi |
| D3 | Đạt | Test dùng WordPress giả, AI giả, kho nháp tạm |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| detect-secrets | `{}` (10 file đổi, biên bản này), `PYTHONUTF8=1` | — |
| bandit | `uvx bandit -r app/views/write.py seo_app/storage/drafts.py`: 1 Low B101 `assert` ở `drafts.py:557` | Có từ trước (biên bản T-086 đã loại), không thuộc phiếu |
| pip-audit | Không chạy lại: `uv.lock` không đổi (`git diff 3d7f4b7..66131e5 -- uv.lock` rỗng) | — |
| ruff | `uv run ruff check .`: All checks passed! (nhánh và cây gộp) | — |
| pytest (nhánh, `66131e5`) | 12 file (8 file tiêu chí xong của phiếu + `tests/test_t086_send_state.py`, `tests/test_storage_send_state.py`, `tests/test_t089_send_draft.py`, `tests/test_soi_loi_t089.py`), `PYTHONUTF8=1`: **474 passed, 1 skipped, 2 xfailed, 0 failed** (773,1 s); 2 xfail = SL-T089-1. Khớp số của Soi Lỗi | — |
| pytest (cây gộp) | Mục «Thử gộp»: 1.210 passed (T-041 `a88c6e5`), 1.394 passed (T-041 `ee1de90`), 0 failed | — |
| Soát R5 | `tests/test_la_chan_t086.py`: chỉ xóa dấu `xfail` LC-T086-1 và `import pytest` thừa; `tests/test_soi_loi_t086.py`: chỉ xóa 2 dấu `xfail`; `tests/test_t086_send_state.py`: 2 hàm giả nhận và chuyển tiếp `**kwargs` (cho `expected=`), câu kiểm giữ nguyên; `tests/test_app_images.py::test_open_draft_uses_checked_image_not_draft_fields`: nháp mẫu thêm băm đúng của file, câu kiểm giữ nguyên (nháp không băm có test riêng). Không `skip`, không xóa test | Đạt (khớp soát R5 của Soi Lỗi) |

## Thử gộp

Làm trên hai worktree tạm (detached, thư mục nháp của Lá Chắn), không đụng repo chính; xong đã gỡ (`git worktree remove`).

| Việc | Kết quả |
|---|---|
| `git merge-tree --write-tree` của `team/T-089` với `origin/main` `e295f0e` (từ gốc nhánh chỉ đổi tài liệu), `origin/team/T-088` `7e1fdae` (sửa `client.py`), `origin/team/T-041` `a88c6e5` (cùng sửa `write.py`, `drafts.py` ở chỗ khác) | Không xung đột |
| Gộp lần lượt `66131e5` → `main` → `T-088` → `T-041` (Git tự gộp `write.py`, `drafts.py`); 15 file test: gửi nháp T-086, T-089 (`test_t089_send_draft`, `test_soi_loi_t089`, `test_t086_send_state`, `test_soi_loi_t086`, `test_la_chan_t086`, `test_storage_send_state`), kho nháp (`test_storage_drafts`, `test_drafts_images`), `test_app_pages`, T-041 (`test_t041_seo_ui`, `test_t041_drafts_seo`, `test_soi_loi_t041`), client sau T-088 (`test_wordpress_t088`, `test_soi_loi_t088`, `test_la_chan_t085`) | **1.210 passed, 1 skipped, 10 xfailed, 0 failed** (630,3 s, `PYTHONUTF8=1`). 10 xfail đều có sẵn: 2 SL-T089-1, 8 SL-T088-1. `ruff`: All checks passed! |
| `team/T-041` lên `ee1de90` sau lần trên (Thợ Máy lượt 3: `_seo_text` ở `drafts.py`, `client.py`; `meta.py`, `schema.py`; không chạm phần T-089). `merge-tree` với T-089 sạch; gộp lần lượt `89c7179` → `main` → `T-088` → `T-041` `ee1de90` không xung đột (`drafts.py` gộp còn đủ `approved_sha256`, `save_send_state`, `_drop_surrogates`); 15 file trên + `test_t041_meta`, `test_t041_schema` | **1.394 passed, 1 skipped, 10 xfailed, 0 failed** (554,3 s, `PYTHONUTF8=1`); 10 xfail như trên (2 SL-T089-1, 8 SL-T088-1). `ruff`: All checks passed! |

## Báo nhầm đã loại

- bandit B101 `assert` (`drafts.py:557`): có từ trước, không phải đường bảo mật.

## Ghi nhận (không phải lỗi)

1. **Rủi ro 1 của Họa Sĩ** (tab 2 **cố ý** tick «Tôi đã kiểm tra…» khi tab 1 đang gửi rồi gửi tiếp: hai bài, kết quả tab này ghi đè «đang gửi» tab kia): người dùng đã xác nhận có chủ ý; nháp vẫn khóa «đã gửi». Cách sửa thêm của Soi Lỗi (ghi kết quả kiểu so rồi đặt) đóng luôn ca này; gom vào lượt sửa SL-T089-1.
2. **Soi Lỗi Ghi nhận 3** (mã bài sai dạng: câu của client «Thử lại sau…» đứng dưới khóa «gửi dở»): thuộc `client.py` (T-088), chữ có thể làm người dùng tick xác nhận vội; nút vẫn khóa tới khi tick. Thợ Máy cân nhắc khi dọn câu báo của client.
3. Lần duyệt mà `web_info` không đọc được ảnh (ổ chậm) không có băm: trong phiên chỉ so cỡ, giờ sửa, định danh; mở lại nháp thì phải duyệt lại. Hiếm, hướng an toàn.
4. Giới hạn trên cho `_positive_id` của client (phần không bắt buộc của biên bản T-086) vẫn chưa làm; để sau T-088 như phiếu ghi. Không còn cần cho an toàn của trang (LC-T086-1 đã đóng ở `write.py`).

## Điều kiện

1. **Gộp `main`:** được ngay, không lỗi nào phải sửa trước. Chỉ Huy chạy toàn bộ pytest trên Windows khi gộp như thường lệ.
2. **SL-T089-1 (Thấp) → Họa Sĩ**, lượt sửa nhỏ (hoặc phiếu dọn sau, trước khi hết Giai đoạn 3): `holder["claimed"]`, `finish_send` chỉ ghi lại kết quả khi lần này đã ghi được «đang gửi»; nên ghi kết quả kiểu so rồi đặt (đóng cả Ghi nhận 1). Gỡ 2 `xfail` của `tests/test_soi_loi_t089.py` khi XPASS. Soi Lỗi, Lá Chắn rút gọn.
3. **Thư Ký, sau khi gộp T-089:** sửa khối «Lời dặn tạm thời» của README: hai tab cùng bài nay không còn ra hai bài nháp, nhưng tới khi SL-T089-1 xong vẫn nên gửi ở **một tab**; lần gửi thật đầu tiên (T-059) giữ «một bài, một ảnh, một tab»; thêm một câu: nháp lưu trước bản này phải tick «Đã duyệt» lại một lần.
4. **Lá Chắn:** kiểm lại biên bản này bằng Claude Fable sau 01/11.

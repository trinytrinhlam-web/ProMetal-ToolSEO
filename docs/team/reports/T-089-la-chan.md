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
| **Kết luận README sau T-089** (2026-10-27) | **ĐẠT** · 0 lỗi: README mục 9, 10 sau T-089 (nhánh `team/T-089-readme`, `e009792`) đủ 4 điều kiện của mục «Xem lại lượt 4» (việc theo sau số 2), câu trích khớp `app/views/write.py` lượt 4, D1 đạt, không hứa quá. Gộp sau T-089 lượt 4. Xem mục [README sau T-089](#readme-sau-t-089-2026-10-27) |
| **Kết luận xem lại lượt 2 + 3** (2026-10-27) | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp mới** (LC-T089-1: có từ trước, không phải lỗi lùi). SL-T089-1, SL-T089-2 **đã đóng**; Ghi nhận 1 đóng phần ghi đè; không lùi LC-T086-1, SL-T086-1, SL-T086-2, băm ảnh đã duyệt, Ghi nhận 2; câu báo mới đạt U1; R5 đạt. **Gộp `main` được ngay** (đầu nhánh `58100eb`; thử gộp với `main` `828da87`, T-041 `f21bc3a` và `a735c7e` không xung đột, 18 file test trên cây gộp 1.511 qua, 0 hỏng). Xem mục [Xem lại lượt 2 + 3](#xem-lại-lượt-2--3-2026-10-27) |
| **Kết luận xem lại lượt 4** (2026-10-27) | **ĐẠT** · 0 lỗi mới; LC-T089-1 **đã đóng** (lần gửi không tạo được bài nào trả nháp về đúng trạng thái cũ, so rồi đặt); không lùi SL-T089-1, SL-T089-2, Ghi nhận 1, LC-T086-1, SL-T086-1, SL-T086-2, băm ảnh đã duyệt, Ghi nhận 2; R5 đạt. **Gộp `main` được ngay** (đầu nhánh `3b48502`; thử gộp với `main` `641a837`, T-041 `33d0655` không xung đột, 20 file trên cây gộp 1.554 qua, 0 hỏng). Xem mục [Xem lại lượt 4](#xem-lại-lượt-4-2026-10-27) |

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

## README sau T-089 (2026-10-27)

Theo tin giao việc của Chỉ Huy B (2026-10-27): điều kiện Thư Ký của biên bản này (mục «Xem lại lượt 4», việc theo sau số 2). Nhánh `team/T-089-readme` (`e009792`, từ `main` `641a837`). Đọc báo cáo Thư Ký (`docs/team/reports/T-089-thu-ky.md`) và `git diff 641a837..e009792 -- README.md`: mục 9 thêm một đoạn; mục 10 bỏ khối «Lời dặn tạm thời», thêm hai ý vào «App nhớ việc đã gửi», «Lần gửi thật đầu tiên» thành khối riêng. Đối chiếu `app/views/write.py` của `origin/team/T-089` (`d0a34d5`, mã lượt 4 `e7549ea`). Chỉ đọc. 15:12 → 15:16 +07, giờ máy. Mục này đặt trước mục «Xem lại lượt 2 + 3» để nhánh gộp vào `main` (đã có mục «Xem lại lượt 4» ở cuối file) không xung đột.

**Tóm tắt (cho chủ dự án):** README nay nói đúng app sau T-089: hai tab cùng gửi một bài chỉ ra một bài nháp (bỏ lời dặn «một tab»); đã tick xác nhận mà lần gửi hỏng trước khi tạo được bài thì bài giữ khóa như cũ; app nhớ «dấu vân tay» của ảnh lúc duyệt, ảnh bị thay thì bắt duyệt lại, bài soạn bằng bản app cũ phải tick duyệt ảnh lại một lần; lần gửi thật đầu tiên vẫn một bài, một ảnh, một tab. Không có khóa, mật khẩu hay đường dẫn máy. Không có lỗi.

| Điểm kiểm | Kết quả | Bằng chứng |
|---|---|---|
| Bỏ dặn một tab | **Đạt** | Khối «Lời dặn tạm thời» bỏ hẳn. Ý mới «Cùng một bài mở ở hai tab (hay hai cửa sổ), bấm 📤 Gửi nháp ở cả hai: chỉ ra **một** bài nháp. Tab bấm sau không gửi gì, báo «Chưa gửi gì lên website: trạng thái gửi của bài này vừa thay đổi (…)…», và nút gửi khóa theo lời nhắc phía trên nút» đúng code: `send_and_record` ghi «đang gửi» so rồi đặt với trạng thái người dùng thấy, không ghi được thì không gửi, báo `MSG_SENT_ELSEWHERE` (câu trích có nguyên văn); `draft_panel` đọc trạng thái trong nháp mỗi lần vẽ nên khóa theo tab kia. Hai tab cùng tick «Tạo thêm» rồi bấm cũng chỉ ra một bài (test hai phiên của Họa Sĩ, Soi Lỗi). Chữ «tab bấm sau»: Ghi nhận README số 1 |
| Gửi hỏng trước khi tạo bài vẫn khóa | **Đạt** (đúng khi đã gộp lượt 4) | Ý mới «Đã tick xác nhận rồi gửi, mà lần gửi đó hỏng trước khi tạo được bài (ví dụ mất mạng lúc tải ảnh): bài giữ nguyên khóa như trước lúc gửi (vẫn «chưa có kết quả», hay vẫn «đã gửi» bài cũ). Muốn gửi tiếp thì kiểm trang quản trị rồi tick lại.» đúng `record_outcome` lượt 4 (lần gửi không tạo được bài nào trả nháp về `holder["replaced"]`). Ví dụ «mất mạng lúc tải ảnh» đúng là nhánh «chưa tạo gì» (lỗi ở bước tải ảnh: `maybe_draft` tắt). Ô xác nhận bị bỏ tick trước mỗi lần gửi (`_wp_reset_guards`) nên phải tick lại. Không hứa quá: mất mạng đúng lúc tạo bài thì app báo «bài nháp có thể đã có», khóa «chưa có kết quả»; README không nói khác. `origin/main` `641a837` mới có lượt 1–3 (ở đó gửi hỏng sau khi tick ở «chưa có kết quả» thì mở khóa): gộp nhánh này **sau** T-089 lượt 4 (`main` trên máy `bd5a1f8` đã gộp `d0a34d5`) |
| Nháp cũ tick duyệt ảnh lại một lần | **Đạt** | Mục 9: «Bài soạn dở lưu bằng bản app cũ (trước khi app có dấu vân tay này) thì các ảnh đã duyệt phải tick **Đã duyệt** lại một lần; app báo «… nháp không có «dấu vân tay» của ảnh lúc duyệt …»» đúng `restore_images` (nháp có alt đã duyệt mà không có băm thì bỏ duyệt, báo `MSG_OLD_APPROVAL`; câu trích có nguyên văn). Ảnh bị thay bằng ảnh khác cùng tên: «Ảnh này khác bản bạn đã duyệt trước đó…» nguyên văn `MSG_APPROVED_OTHER_VERSION`, bỏ duyệt ở khung ảnh (`alt_editor`); gửi thẳng ở Xuất bản thì dừng, «Chưa gửi gì lên website.» (`send_draft` so băm). «Lúc bạn tick **Đã duyệt**, app nhớ «dấu vân tay» của đúng bản ảnh đang hiện»: `altsha-<id>` lấy băm của bản ảnh đang hiện, ghi khi ô được tick; «lưu trong nháp trên máy, không gửi đi đâu»: `approved_sha256` trong nháp, băm không gửi WordPress hay hãng AI (mục «Băm trong nháp đọc an toàn; nháp cũ» của biên bản này) |
| Lần gửi thật đầu tiên | **Đạt** | Khối riêng «Lần gửi thật đầu tiên»: một bài, một ảnh, một tab; ảnh có GPS chụp ở nơi đã công khai (xưởng, cửa hàng), không dùng ảnh nhà khách; 3 bước tải ảnh về kiểm GPS rồi xóa bài và ảnh thử. Giữ nguyên nội dung đã duyệt ở T-087 (LC-T087-2), chỉ bỏ chữ «tạm thời» |
| Tên nút, câu nhắc khớp code | **Đạt** | 11 chuỗi README trích (nút, ô, câu báo) đều có nguyên văn trong `write.py` `d0a34d5` (đọc hằng bằng `ast`, gồm hằng nhiều dòng): «📤 Gửi nháp», «Tôi đã kiểm tra trang quản trị, vẫn muốn gửi», «Tạo thêm một bài nháp mới», «Mở bài nháp trong WordPress», «… bài nháp có thể đã có trên website», «Chưa gửi gì lên website.», `MSG_SENT_ELSEWHERE`, `MSG_APPROVED_OTHER_VERSION`, `MSG_OLD_APPROVAL`. Ô duyệt: Ghi nhận README số 2 |
| D1 (không bí mật, không đường dẫn máy) | **Đạt** | `PYTHONUTF8=1 uvx detect-secrets scan README.md docs/team/reports/T-089-thu-ky.md`: `{}`; các dòng thêm trong diff không có khóa, mật khẩu, email, đường dẫn máy, địa chỉ website (chỉ chữ `https://` trong cách lấy địa chỉ ảnh, có từ trước) |
| Không hứa điều app chưa làm | **Đạt** | Không nói app chặn được mọi lần gửi trùng: vẫn dặn tick xác nhận, kiểm trang quản trị, đang gửi ở tab khác thì đợi tab đó xong rồi hãy xem. Không nói app tự so ảnh khi mở lại bài: nói đúng hai chỗ app so (khung ảnh, lần gửi) |
| ruff | **Đạt** | `uv run ruff check .`: All checks passed! (nhánh chỉ đổi README và báo cáo) |

**Ghi nhận README (không phải lỗi):**

1. «Tab bấm sau không gửi gì»: chính xác là tab ghi «đang gửi» sau (kiểm lại ảnh, nén ảnh xong sau), thường là tab bấm sau; kết quả README nói (một bài, tab kia báo «Chưa gửi gì…», khóa) đúng. Thư Ký đã ghi trong báo cáo. Nếu muốn: «một trong hai tab (thường là tab bấm sau)».
2. Ô trong app là «✅ Đã duyệt»; README viết **Đã duyệt** như các chỗ đã có từ T-087. Người dùng nhận ra được.

**Kết luận README sau T-089: ĐẠT** · 0 lỗi. Đủ 4 điều kiện (bỏ dặn một tab; gửi hỏng trước khi tạo bài vẫn khóa; nháp cũ tick duyệt ảnh lại một lần; lần gửi thật đầu tiên một bài, một ảnh, một tab); câu trích khớp `write.py` lượt 4; D1 đạt; không hứa quá. **Điều kiện gộp:** gộp sau (hay cùng lúc) T-089 lượt 4 (`d0a34d5`). Lá Chắn kiểm lại bằng Claude Fable sau 01/11.

## Xem lại lượt 2 + 3 (2026-10-27)

Theo tin giao việc của Chỉ Huy B (2026-10-27). Đầu nhánh `58100eb` (mã lượt 2 `f2a72f5`, lượt 3 `8a1ba02`; sau đó chỉ báo cáo). Đọc mục «Lượt 2», «Lượt 3» báo cáo Họa Sĩ, mục «Lượt 2» báo cáo Soi Lỗi; `git diff d5d0e69..58100eb`: phần app chỉ đổi `app/views/write.py` (luồng gửi nháp: `send_and_record`, `record_outcome`, `apply_send`, `finish_send`, câu báo); không đổi `seo_app/**`, `config/**`, `pyproject.toml`, `uv.lock`. Số dòng theo `58100eb`. 09:29 → 13:42 +07, giờ máy (có quãng ngắt vì hết lượt dùng, làm tiếp từ 13:07).

**Tóm tắt (cho chủ dự án):**

- Hai lỗi nhỏ còn lại của «Gửi nháp» đã sửa đúng: tab bị từ chối không còn xóa ghi chú «đang gửi/đã gửi» của tab kia (SL-T089-1); bài bị xóa ở tab khác, hay lần gửi ở tab khác hỏng ngay, thì bài vừa tạo vẫn được nhớ (SL-T089-2). Câu báo mới nói đúng, không lộ gì. Bản này an toàn để gộp.
- Lá Chắn tìm thêm **1 lỗi nhỏ (LC-T089-1, Thấp)**, có từ trước (bản đang dùng cũng vậy, không do lần sửa này): cùng một bài mở ở hai tab, tab đầu đang gửi; ở tab hai bạn **cố ý** tick «Tôi đã kiểm tra trang quản trị, vẫn muốn gửi» rồi gửi; tab đầu tạo xong bài trước, sau đó lần gửi ở tab hai hỏng (ví dụ website quá tải lúc tải ảnh). Khi đó app quên bài tab đầu vừa tạo: nút «Gửi nháp» mở lại, bấm là ra bài nháp thứ hai (vẫn là nháp, không đăng; tab đầu có báo rõ mã bài). Cách tránh tới khi sửa: thấy câu «bài nháp có thể đã có…» trong lúc tab khác đang gửi thì **đợi tab đó gửi xong**, đừng tick ô xác nhận.

| Điểm kiểm | Kết quả | Bằng chứng |
|---|---|---|
| **SL-T089-1** (tab thua so rồi đặt bị ngắt, `finish_send` ghi đè trạng thái tab kia) | **Đóng** | `send_and_record` dựng «đang gửi» một lần (`write.py:2196`), ghi so rồi đặt (`:2198`); chỉ khi ghi được mới đặt `holder["claimed"]` (`:2214`). `record_outcome` không có dấu thì không ghi gì (`:2261-2263`); `finish_send` chỉ thử ghi lại khi có dấu (`:2347-2352`). `holder` là `dict` thường: giữa lần ghi được «đang gửi» và lúc đặt dấu không có lần đọc/ghi `st.session_state` hay lệnh `st.*` nào (không có chỗ dừng); lần chạy mới chỉ đọc `holder` sau `done` (`:2333-2343`), không tranh nhau. Test qua: Soi Lỗi `test_lost_tab_interrupted_keeps_other_tab_sending`, `…_sent` (gỡ `xfail`), 6 biến thể `test_lost_or_busy_tab_interrupted_keeps_other_tab_sent` (thua, file nháp bận, ngắt một và hai lần); Họa Sĩ `test_pending_not_written_then_interrupted_writes_nothing` |
| **Ghi nhận 1** của biên bản này (tab 2 cố ý tick «Tôi đã kiểm tra…» khi tab 1 đang gửi, kết quả tab 1 ghi đè «đang gửi» tab 2) | **Đóng phần ghi đè**; còn LC-T089-1 | Kết quả ghi so rồi đặt với đúng dấu của lần này (`expected=(claimed, False)`, `:2267`): tab khác đã ghi trạng thái mới thì không ghi đè, `kept_other` (`:2282`), nháp giữ khóa của tab kia. Test qua: Họa Sĩ `test_outcome_does_not_overwrite_other_tab_new_send`, `test_retry_in_finish_send_also_compares`; Soi Lỗi hai phiên thật `test_confirmed_send_in_other_tab_keeps_its_record`. Đính chính lượt đầu: câu «nháp vẫn khóa «đã gửi»» của Ghi nhận 1 chỉ đúng khi lần gửi của tab 2 có bài hay chưa rõ; tab 2 hỏng mà chưa tạo gì **sau khi** tab 1 đã tạo bài thì nháp mất khóa (mục «Lỗi mới»: LC-T089-1; mã lượt 1 và `main` cũng vậy) |
| **SL-T089-2** (nháp mất dòng trạng thái gửi lúc đang gửi thì kết quả bị bỏ) | **Đóng** | So với dấu của mình hỏng mà kết quả có bài hay chưa rõ (`state` khác `None`) thì ghi thêm một lần với `expected=(None, False)` (`:2268-2269`). `save_send_state` đọc và ghi trong một giao dịch `BEGIN IMMEDIATE` (`drafts.py:675-692`, `BEGIN IMMEDIATE` `:677`, không ghi `:684`): chỉ ghi khi nháp **không có dòng nào** và không hỏng; dòng «đang gửi», «đã gửi» của tab khác không bao giờ bị ghi đè hay xóa; lần ghi thêm chỉ **thêm khóa**. Lần này chưa tạo gì (`state` là `None`) mà dòng đã đổi thì coi là xong, không báo (`:2277`). Giữ chốt `claimed` (lớp chặn chính cho tab thua). Test qua: Soi Lỗi `test_confirmed_send_in_other_tab_failing_first_keeps_this_post`, `test_draft_deleted_elsewhere_while_sending_comes_back_locked` (gỡ `xfail`); Họa Sĩ `test_outcome_recorded_when_send_state_row_gone`, `test_nothing_created_and_other_tab_wrote_no_note` |
| Câu báo mới (U1) | **Đạt** | `kept_other_message` (`:2399-2410`): câu cố định `MSG_STATE_CHANGED_ELSEWHERE` (`:187`) ghép mã bài của chính lần gửi này; mã bài là số nguyên thật (`_positive_id` của client: `type(value) is int`), hiện bằng `st.warning` (`:2447-2448`). Không đường dẫn, không địa chỉ website, không chữ từ website. `git diff d5d0e69..58100eb` không thêm `unsafe_allow_html` (vẫn 7 chỗ như `main` `3d7f4b7`). Nói đúng ở cả hai ca tab kia còn đang gửi và đã gửi xong (Ghi nhận L2-1 của Soi Lỗi); ca nháp bị xóa ở tab khác không còn hiện câu này (lần ghi thêm ghi được) |
| Không lùi LC-T086-1 | **Đạt** | `SendState.now(...)` vẫn trong `try` (`:2266`); mã bài từ 2⁶³ → `ValueError` → câu cố định `MSG_POST_ID_OUT_OF_RANGE`, không ghi gì, nháp giữ «đang gửi» của chính lần này (khóa «gửi dở»); `finish_send` thử lại cũng chỉ ra câu đó. Test qua: `tests/test_la_chan_t086.py::test_lc_t086_1_huge_post_id_from_site_does_not_break_page`, Họa Sĩ, Soi Lỗi (2⁶³, 2⁶⁴, 10³⁰, ngắt ở từng lần ghi) |
| Không lùi SL-T086-1, SL-T086-2, băm ảnh đã duyệt, Ghi nhận 2 | **Đạt** | Lần ghi «đang gửi» so rồi đặt với `seen` không đổi (`:2198`, `_wp_seen` ở `draft_panel`); `web_info`, `approved_sha256`, `set_pick`, lần so băm lúc gửi không nằm trong diff. Mã bài trong nháp vẫn chỉ để hiện và dựng link `client.edit_link`; câu báo mới dùng mã bài website vừa trả, không dùng mã trong nháp. Test qua: `test_saved_post_id_never_used_to_write_to_wordpress`, bộ test T-056, T-086, T-089 (mục dưới) |
| W1, W2 | **Đạt** | Không thêm lệnh nào lên website; chỉ đổi cách ghi trạng thái gửi trong nháp trên máy; so rồi đặt chỉ bớt lần ghi, lần ghi thêm chỉ thêm khóa |
| Gỡ `xfail` đúng R5 | **Đạt** | Lượt 2 (`d5d0e69..f2a72f5`): `tests/test_soi_loi_t089.py` chỉ xóa 2 dấu SL-T089-1 (8 dòng), không thêm dòng nào; lượt 3 (`c636e9b..8a1ba02`): chỉ xóa 2 dấu SL-T089-2 (8 dòng). `tests/test_t089_send_draft.py`: chỉ thêm test, dòng nhập thêm `DraftError`. Commit của Soi Lỗi lượt 2 chỉ đổi file test và báo cáo của Soi Lỗi. Không `skip`, không xóa test |
| Thử gộp | **Không xung đột** | Mục «Thử gộp lượt 2 + 3» dưới |

**Lỗi mới** (test `xfail(strict=True)` trong `tests/test_la_chan_t089.py`, commit `3bdf1f9`):

| Mã | Mức | Lỗi | Tái hiện | Mong đợi | Thực tế | Gợi ý sửa |
|---|---|---|---|---|---|---|
| LC-T089-1 | **Thấp** (có từ trước: mã lượt 1 `d5d0e69` và `main` cũng vậy; không phải lỗi lùi; không chặn gộp) | Tab 2 ghi «chưa gửi» (xóa dòng) bằng so rồi đặt với chính «đang gửi» của nó, **sau khi** tab 1 đã tạo bài mà không ghi được vào nháp (`kept_other`, đúng thiết kế): nháp mất dấu vết bài của tab 1. Thứ tự ngược lại (tab 2 hỏng trước) là SL-T089-2, đã sửa | `test_lc_t089_1_confirmed_send_elsewhere_creating_nothing_keeps_this_post`: tab 1 (phiên AppTest thật) đang chờ website tạo bài 501; tab 2 chạy đúng `send_and_record` của trang trên luồng riêng, với `seen` = «gửi dở» của tab 1 và mã bài như `draft_panel` tính khi người dùng tick «Tôi đã kiểm tra…»: ghi được «đang gửi» của nó, đang tải ảnh. Tab 1 tạo xong bài 501, báo «nháp giữ trạng thái gửi của tab kia». Sau đó tải ảnh của tab 2 hỏng (website quá tải, 503): lỗi ở bước tải ảnh nên `maybe_draft` tắt (`client.py:1242`, `:1272`, `:1293`), chưa có bài nào | Bài 501 có trên website thì nháp vẫn khóa («đã gửi 501», hay «gửi dở» để người dùng kiểm trang quản trị) | `record_outcome` của tab 2: `state` là `None`, so với `claimed` của nó khớp (tab 1 không ghi đè) nên xóa dòng. Nháp không còn dòng trạng thái gửi: tab 2 ngay sau câu lỗi và phiên mới mở nháp đều thấy nút «Gửi nháp» bật, không nhắc; bấm là bài nháp thứ hai, ảnh tải lần nữa (ảnh đã công khai từ lần đầu, không lộ thêm). `--runxfail`: hỏng đúng câu kiểm `load_send_state(draft) is not None`; mọi bước trước đó đúng như tả (tab 2 có `claimed`, `state == (False, None)`, 1 bài, câu báo của tab 1). Đối chứng trên bản sao `git archive d5d0e69` (mã lượt 1, ghi không so): hỏng cùng chỗ. Cần: người dùng cố ý xác nhận ở tab 2 trong lúc tab 1 đang gửi, và lần gửi của tab 2 hỏng mà chưa tạo bài (lỗi ở bước tải ảnh: mất mạng, hết giờ, 4xx, 5xx) sau khi tab 1 xong. Mất khóa hẳn khi đó là lần gửi đầu của nháp; nháp đã có bài từ trước thì tab 2 ghi lại «đã gửi» bài cũ (vẫn khóa, chỉ thiếu mã bài 501) | Lần gửi chưa tạo được bài nào (lỗi mà không `maybe_draft`: kết quả không `ok`, `pending` tắt) thì trả nháp về **đúng trạng thái mà «đang gửi» của nó đã thay** (`seen`, so rồi đặt với `claimed`), thay vì «chưa gửi»/`(False, previous_post)`: dấu «gửi dở» của tab 1 còn nên nháp vẫn khóa, người dùng kiểm trang quản trị thấy bài 501. Thử sửa giả trên bản sao (`holder` nhớ `seen`; khoảng 6 dòng trong `send_and_record`, `record_outcome`): test LC-T089-1 qua (`[XPASS(strict)]`), 5 file gửi nháp còn lại (`test_t089_send_draft`, `test_soi_loi_t089`, `test_t086_send_state`, `test_soi_loi_t086`, `test_la_chan_t086`) 130 qua, 0 hỏng. Lưu ý cho người sửa: nhận ra «chưa tạo bài nào» theo nhánh kết quả (lỗi mà không `maybe_draft`), **không** so mã bài với `previous_post`: bản thử đầu so mã bài thì 2 test hai phiên «Tạo thêm» (`test_two_sessions_create_more_only_once`, `test_two_sessions_take_turns_one_post_per_round`) ra bài thứ ba (WordPress giả trả cùng mã 501 cho mọi bài: lần gửi có bài bị coi là chưa tạo gì, nháp được trả lại đúng trạng thái cũ, tab kia so rồi đặt khớp lại). Ảnh hưởng: một tab gửi lại sau «gửi dở» (đã tick) mà hỏng trước khi tạo gì thì nháp vẫn «gửi dở», phải tick lại (hướng an toàn). Cách khác: tab 1 khi `kept_other` mà dòng đang là «đang gửi» của tab khác thì ghi gộp «đang gửi» kèm mã bài 501 |

**Ghi nhận xem lại (không phải lỗi):**

1. Câu `kept_other_message` khi lần này chưa tạo gì mà nháp đã có bài từ trước (`(False, previous_post)` khác `None`) nói bài của lần này «có thể cũng đã có»: thừa thận trọng, đúng hướng an toàn. Có thể chỉnh chữ khi sửa LC-T089-1.
2. Lần ghi thêm `expected=(None, False)` cho nháp vừa bị xóa ở tab khác tạo một dòng `send_states` không có nháp đi kèm: rất nhỏ, theo mã nháp ngẫu nhiên, chỉ có tác dụng khi chính nháp đó được lưu lại (đúng ý: nháp tạo lại vẫn khóa). Không rủi ro.
3. Cho người gộp T-041: trong cây gộp, `send_and_record` gọi `write_seo(client, holder)` ngay sau `record_outcome`, chú thích «sau khi đã ghi «đã gửi» vào nháp» không còn đúng hẳn khi `kept_other`; `write_seo` vẫn chỉ ghi lên bài vừa tạo của chính lần gửi này (`result["ok"]`, cùng client), tab thua trả về trước đó: đúng W2, không phải lỗi.

### Thử gộp lượt 2 + 3

| Việc | Kết quả |
|---|---|
| `git merge-tree --write-tree` của `58100eb` với `origin/main` `828da87` (đã gộp T-088), `origin/team/T-041` `f21bc3a` (tin giao việc) và đầu mới `a735c7e` (Họa Sĩ T-041 lượt 3, cũng sửa `write.py`) | Không xung đột (cả T-041 với `main`) |
| Cây gộp lần lượt `58100eb` → `main` `828da87` → `T-041` `a735c7e` (dựng bằng `git merge-tree`, xuất `git archive` ra thư mục nháp, chạy bằng venv của `wt-T-089`: `pyproject.toml`, `uv.lock` không đổi) + `tests/test_la_chan_t089.py`; 18 file: gửi nháp T-086, T-089 (7 file), kho nháp (2), `test_app_pages`, `test_app_images`, T-041 (`test_t041_seo_ui`, `test_t041_drafts_seo`, `test_soi_loi_t041`, `test_t041_meta`, `test_t041_schema`), client sau T-088 (`test_wordpress_t088`, `test_soi_loi_t088`) | **1.511 passed, 1 skipped, 10 xfailed, 0 failed** (1.351,2 s, `PYTHONUTF8=1`; chạy song song với lượt khác). 10 xfail đều đã biết: 1 LC-T089-1, 1 SL-T041-8 (có sẵn trên `team/T-041`), 8 SL-T088-1 (có sẵn trên `main`). `ruff check .` trên cây gộp: All checks passed! |

### Kết quả công cụ quét lượt 2 + 3

| Công cụ | Kết quả |
|---|---|
| detect-secrets (`PYTHONUTF8=1`) | `{}`: 6 file đổi từ `d5d0e69` (`write.py`, 3 file test, 2 báo cáo) và biên bản này |
| bandit | `uvx bandit -r app/views/write.py`: 0 vấn đề |
| pip-audit | Không chạy lại: `uv.lock` không đổi |
| ruff | `uv run ruff check .`: All checks passed! (nhánh `3bdf1f9` và cây gộp) |
| pytest (nhánh, `58100eb` + `tests/test_la_chan_t089.py`) | 13 file (8 file tiêu chí xong của phiếu + `tests/test_t086_send_state.py`, `tests/test_storage_send_state.py`, `tests/test_t089_send_draft.py`, `tests/test_soi_loi_t089.py`, `tests/test_la_chan_t089.py`), `PYTHONUTF8=1`: **493 passed, 1 skipped, 1 xfailed, 0 failed** (1.289,6 s; máy chạy song song hai lượt test khác của Lá Chắn); 1 xfail = LC-T089-1. 493 qua khớp số Họa Sĩ lượt 3 |

**Kết luận xem lại lượt 2 + 3: ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp mới** (LC-T089-1, có từ trước, không phải lỗi lùi). SL-T089-1, SL-T089-2 **đóng**; Ghi nhận 1 đóng phần ghi đè (phần còn lại là LC-T089-1). Không lùi LC-T086-1, SL-T086-1, SL-T086-2, băm ảnh đã duyệt, Ghi nhận 2; câu báo mới đạt U1; R5 đạt. **Gộp `main` được ngay**: LC-T089-1 chỉ ra thêm bài nháp, cần người dùng cố ý xác nhận ở tab thứ hai đúng lúc tab đầu đang gửi; bản này không kém `main` ở ca nào và tốt hơn hẳn ở ca hai tab bấm gửi bình thường (`main` ra hai bài).

**Điều kiện xem lại lượt 2 + 3:**

1. **Gộp `main`:** được ngay. Chỉ Huy chạy toàn bộ pytest trên Windows khi gộp như thường lệ.
2. **LC-T089-1 (Thấp) → Họa Sĩ**, phiếu dọn sau (hoặc lượt 4 nếu Chỉ Huy muốn đóng trọn trong T-089); gỡ `xfail` của `tests/test_la_chan_t089.py` khi XPASS (chỉ xóa dấu). Soi Lỗi, Lá Chắn rút gọn.
3. **Thư Ký, sau khi gộp T-089** (thay điều kiện 3 lượt đầu): viết lại khối «Lời dặn tạm thời» của README: mở cùng một bài ở hai tab rồi bấm gửi nay không còn ra hai bài nháp; giữ một câu tới khi LC-T089-1 xong: thấy «bài nháp có thể đã có…» trong lúc tab khác đang gửi thì đợi tab đó gửi xong, đừng tick «Tôi đã kiểm tra…»; nháp lưu trước bản này phải tick «Đã duyệt» ảnh lại một lần; lần gửi thật đầu tiên (T-059) giữ «một bài, một ảnh, một tab».
4. **Lá Chắn:** kiểm lại phần xem lại này bằng Claude Fable sau 01/11.

## Xem lại lượt 4 (2026-10-27)

Theo tin giao việc của Chỉ Huy B (2026-10-27). Đầu nhánh `3b48502` (mã `e7549ea`). Đọc mục «Lượt 4» báo cáo Họa Sĩ; `git diff 6f67bb2..3b48502`: phần app chỉ đổi `app/views/write.py` (`send_and_record`, `record_outcome`; không câu báo mới); test: gỡ `xfail` LC-T089-1, thêm 4 test của Họa Sĩ. Số dòng theo `3b48502`. 14:28 → 14:55 +07, giờ máy.

**Tóm tắt (cho chủ dự án):**

- Lỗi nhỏ LC-T089-1 đã sửa đúng: lần gửi nào hỏng mà chưa tạo được bài thì app trả ghi chú gửi của bài về **đúng như trước lúc nó bắt đầu gửi**. Ca hai tab ở lượt trước: bài vẫn khóa, mở trang quản trị là thấy bài của tab đầu.
- Thay đổi nhỏ bạn có thể gặp (hướng an toàn): bài đang «gửi dở», bạn tick «Tôi đã kiểm tra…» rồi gửi mà lần đó hỏng trước khi tạo bài (ví dụ mất mạng lúc tải ảnh) thì bài vẫn «gửi dở», muốn gửi tiếp phải tick lại.
- Không có lỗi mới. Bản này an toàn để gộp.

| Điểm kiểm | Kết quả | Bằng chứng |
|---|---|---|
| **LC-T089-1** | **Đóng** | `send_and_record` nhớ trạng thái mà «đang gửi» của lần này thay (`holder["replaced"]`, `write.py:2217`; dòng hỏng thì chính «đang gửi» của lần này), ngay sau `claimed` (`:2215`), trước khi gửi. `record_outcome`: lần gửi không tạo được bài nào (`nothing_created`, `:2273`) thì ghi `replaced` (`:2276`) kiểu so rồi đặt với `claimed` (`:2279`); không ghi thêm khi nháp trống (`:2280`); không ghi được (tab khác đã ghi trạng thái mới) thì coi là xong, không báo (`:2289`). Ca LC-T089-1: tab 2 trả lại đúng «đang gửi» của tab 1 → nháp «gửi dở», khóa. `tests/test_la_chan_t089.py` (đã gỡ `xfail`) qua. Đọc mã thêm ca nhiều tab cố ý gửi chồng nhau (A, B, C, mỗi tab thay «đang gửi» của tab trước): lần chưa tạo gì trả lại từng nấc, dòng còn lại luôn là «đang gửi» của một lần có thể đã tạo bài hay kết quả thật của nó → không mở khóa |
| «Chưa tạo gì» không sai theo hướng mở khóa khi website đã có bài | **Đạt** (một giả định có từ T-054: Ghi nhận lượt 4 số 1) | `nothing_created = not ok and not pending` chỉ đúng ở hai nhánh: (a) `WordPressError` thường: chỉ ném ở bước kiểm trước khi gửi (tiêu đề, phần bài, ảnh); trong khối gửi mọi lỗi đổi thành `DraftImagesError`; sau khi tạo bài, lỗi đặt ảnh đại diện thành `message`, kết quả vẫn `ok` (`client.py:1308-1317`). (b) `DraftImagesError` không `maybe_draft`: lỗi ở bước tải ảnh (chưa tới lệnh tạo bài: `creating` tắt, `client.py:1242`, `:1272`) hoặc lệnh tạo bài bị từ chối 4xx (`:1281-1293`). Hết giờ, mất mạng, lỗi SSL: `WordPressError` không mã (`client.py:1446-1466`); chuyển hướng 3xx, 5xx: mã không phải 4xx (`:1467-1475`) → `maybe_draft` → «gửi dở». Câu trả lời 2xx hỏng (không JSON, sai khuôn: `_json`, `_post_from`) → lỗi không mã → `maybe_draft`. Lỗi lạ (không phải `WordPressError`) ở mọi bước, kể cả sau khi tạo bài → `except Exception` giữ `pending` (`write.py:2232`) → «gửi dở». Lỗi thoát ra sau khi website đã trả kết quả (lúc dựng `holder["result"]`): `result` còn `None`, `finish_send` không ghi gì, nháp giữ «đang gửi» → khóa. Lần trả lại chỉ về **đúng** trạng thái trước lúc bấm gửi: không bao giờ mở khóa hơn trước lúc gửi |
| Không lùi SL-T089-1 | **Đạt** | Chốt `claimed` giữ nguyên (`:2215`, `:2270`, guard của `finish_send`); tab thua không có `claimed`, `replaced`, không ghi gì |
| Không lùi SL-T089-2 | **Đạt** | Lần gửi có bài hay chưa rõ vẫn ghi thêm khi nháp trống (`:2280-2281`); hai test SL-T089-2 của Soi Lỗi qua. Riêng lần gửi **chưa tạo gì** mà nháp bị xóa ở tab khác: không ghi (Ghi nhận lượt 4 số 2) |
| Không lùi Ghi nhận 1 (lượt đầu) | **Đạt** | Kết quả có bài vẫn so rồi đặt với `claimed` (`:2279`), không ghi đè trạng thái mới của tab khác (`kept_other`, `:2294`); lần trả lại cũng so rồi đặt, không ghi đè, không xóa dòng của tab khác |
| Không lùi LC-T086-1, SL-T086-1, SL-T086-2, băm ảnh đã duyệt, Ghi nhận 2 | **Đạt** | `SendState.now` cho kết quả có bài vẫn trong `try`; lần ghi «đang gửi» với `seen` không đổi; phần ảnh, băm, mã bài trong nháp không nằm trong diff. Test qua (bộ test dưới) |
| U1, W1, W2 | **Đạt** | Không câu báo mới, không thêm `unsafe_allow_html` (vẫn 7 chỗ `=True`), không lệnh mới lên website; chỉ đổi trạng thái gửi trong nháp trên máy |
| Thay đổi người dùng thấy | **Đạt** (hướng an toàn) | Nháp «gửi dở», tick «Tôi đã kiểm tra…», gửi hỏng trước khi tạo bài: vẫn «gửi dở», phải tick lại (trước đây mở khóa). Nháp «đã gửi X», tick «Tạo thêm», gửi hỏng trước khi tạo gì: giữ đúng dòng «đã gửi X» cũ. Lần gửi đầu hỏng trước khi tạo gì: vẫn «chưa gửi», nút bật như cũ (T-086 `test_error_before_any_draft_clears_pending` qua). Nên ghi vào README (điều kiện Thư Ký) |
| Gỡ `xfail` đúng R5 | **Đạt** | `git diff 6f67bb2..3b48502 -- tests/`: `tests/test_la_chan_t089.py` chỉ xóa dấu `@pytest.mark.xfail(...)` LC-T089-1 và dòng `import pytest` không còn dùng (6 dòng; ruff F401, như `tests/test_la_chan_t086.py` ở lượt 1), thân test không đổi; `tests/test_t089_send_draft.py` chỉ thêm 4 test và hàm phụ `media_rejected`. Không `skip`, không xóa test |
| Thử gộp | **Không xung đột** | Mục «Thử gộp lượt 4» dưới |

**Ghi nhận lượt 4 (không phải lỗi):**

1. Giả định «website trả 4xx cho lệnh tạo bài = chưa tạo bài» (có từ T-054, LC-T054-2) nay quyết định cả việc trả nháp về trạng thái cũ. WordPress lõi, với đúng các trường app gửi lúc tạo bài (`status`, `title`, `content`; không `categories`, `tags`, `meta`, `featured_media`, `template`), không trả 4xx sau khi đã thêm bài; chỉ plugin hay tường lửa làm sai (ví dụ `wp_die(…, 403)` trong `save_post`, `rest_after_insert_post`, lọc `rest_post_dispatch`, luật tường lửa xét câu trả lời) mới tạo được ca «bài đã có mà lệnh báo 4xx». Khi đó nháp về đúng trạng thái trước lúc gửi (lần gửi đầu: «chưa gửi»), y như `main` và các lượt trước; câu của client nói «chưa tạo bài nháp». Không lùi. Muốn chặn hẳn: phiếu client sau coi 4xx ở lệnh tạo bài là «có thể đã có» (đổi lại: lỗi cấu hình 4xx cũng khóa «gửi dở»).
2. Lần gửi chưa tạo gì mà nháp bị xóa ở tab khác trong lúc gửi: không ghi gì (lượt 3 ghi lại «đã gửi» bài cũ vào dòng mồ côi nên nháp được tự lưu tạo lại vẫn khóa). Không phải lỗi: xóa nháp ở một tab trong khi tab khác còn mở rồi tự lưu tạo lại thì trạng thái gửi mất theo nháp, kể cả khi không gửi gì (có từ T-055/T-086, ngoài phiếu này). Có thể gom vào phiếu dọn sau: tự lưu không tạo lại nháp vừa bị xóa ở tab khác, hay giữ trạng thái gửi của nháp đã gửi.
3. Trả lại đúng đối tượng trạng thái cũ (cùng giờ ghi) làm lần so rồi đặt của tab khác thấy trạng thái đó khớp lại: đúng ý (lần này không tạo gì, nháp đúng như lúc tab kia thấy). An toàn vì «chưa tạo gì» xét theo nhánh kết quả, không so mã bài (bẫy đã nêu ở lượt 2 + 3; Họa Sĩ có test `test_created_post_with_same_id_is_a_new_record`, cùng hai test hai phiên «Tạo thêm»).

### Thử gộp lượt 4

| Việc | Kết quả |
|---|---|
| `git merge-tree --write-tree` của `3b48502` với `origin/main` `828da87`, `main` trên máy `4e81776` (Chỉ Huy đã gộp T-089 tới `6f67bb2`, chưa push) và `origin/team/T-041` `33d0655` | Không xung đột |
| Cây gộp lần lượt `3b48502` → `main` `4e81776` → T-041 `33d0655` (xuất `git archive` ra thư mục nháp, chạy bằng venv của `wt-T-089`: `pyproject.toml`, `uv.lock` không đổi); 20 file: 7 file luồng gửi nháp (grep), 6 file tiêu chí xong còn lại, T-041 (`test_t041_seo_ui`, `test_t041_drafts_seo`, `test_soi_loi_t041`, `test_t041_meta`, `test_t041_schema`), client sau T-088 (`test_wordpress_t088`, `test_soi_loi_t088`) | **1.554 passed, 1 skipped, 9 xfailed, 0 failed** (1.293,8 s, `PYTHONUTF8=1`; chạy song song với lượt nhánh). 9 xfail đều có sẵn ở nhánh khác: 1 SL-T041-8 (`team/T-041`), 8 SL-T088-1 (`main`). `ruff check .` trên cây gộp: All checks passed! Sau đó `origin/main` lên `641a837` (Chỉ Huy push; so với `4e81776` chỉ thêm `CLAUDE.md`, `docs/team/board.md`, phiếu T-089): `merge-tree` với nhánh, và lần lượt với T-041 `33d0655`, vẫn sạch |

### Kết quả công cụ quét lượt 4

| Công cụ | Kết quả |
|---|---|
| detect-secrets (`PYTHONUTF8=1`) | `{}`: 4 file đổi từ `6f67bb2` và biên bản này |
| bandit | `uvx bandit -r app/views/write.py`: 0 vấn đề |
| pip-audit | Không chạy lại: `uv.lock` không đổi |
| ruff | `uv run ruff check .`: All checks passed! (nhánh `3b48502` và cây gộp) |
| pytest (nhánh `3b48502`) | 13 file: 7 file luồng gửi nháp (`grep -l "send_and_record\|finish_send\|record_outcome\|save_send_state" tests/`) + 6 file tiêu chí xong còn lại (`test_app_images`, `test_soi_loi_t056`, `test_la_chan_t056`, `test_storage_drafts`, `test_drafts_images`, `test_app_pages`), `PYTHONUTF8=1`: **498 passed, 1 skipped, 0 failed**, không còn xfail nào (1.004,5 s; chạy song song với lượt cây gộp). Khớp số Họa Sĩ lượt 4; `tests/test_la_chan_t089.py` (đã gỡ `xfail`) qua |

**Kết luận xem lại lượt 4: ĐẠT** · 0 lỗi mới; LC-T089-1 **đóng**; không lùi SL-T089-1, SL-T089-2, Ghi nhận 1, LC-T086-1, SL-T086-1, SL-T086-2, băm ảnh đã duyệt, Ghi nhận 2; «chưa tạo gì» không mở khóa khi website đã có bài, trừ ca plugin/tường lửa trả 4xx sau khi đã thêm bài (Ghi nhận lượt 4 số 1, có từ T-054, như `main`); R5 đạt. Phiếu T-089 không còn lỗi mở nào của Soi Lỗi hay Lá Chắn. **Gộp `main` được ngay.**

**Việc theo sau (không chặn gộp):**

1. **Gộp `main`:** được ngay. Chỉ Huy chạy toàn bộ pytest trên Windows khi gộp như thường lệ.
2. **Thư Ký, sau khi gộp** (thay điều kiện 3 của lượt 2 + 3): viết lại khối «Lời dặn tạm thời» của README: hai tab cùng gửi một bài nay chỉ ra một bài nháp, lời dặn «một tab» bỏ được; thêm: bài «gửi dở», tick xác nhận rồi gửi mà hỏng trước khi tạo bài thì vẫn «gửi dở», phải tick lại; nháp lưu trước bản này phải tick «Đã duyệt» ảnh lại một lần; lần gửi thật đầu tiên (T-059) giữ «một bài, một ảnh, một tab».
3. Ghi nhận lượt 4 số 1, 2: phiếu dọn sau nếu Chỉ Huy muốn (không bắt buộc).
4. **Lá Chắn:** kiểm lại phần xem lại này bằng Claude Fable sau 01/11.

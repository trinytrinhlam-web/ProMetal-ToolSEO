# Biên bản bảo mật T-098 · Kế hoạch: khuôn dữ liệu, đọc CSV/TSV/chữ dán, đề xuất có AI, SL-7

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-098](../tickets/T-098-ke-hoach-khuon-doc-de-xuat.md) (Thợ Máy 2 lượt, Soi Lỗi 2 lượt) · điều kiện [Lá Chắn T-094](T-094-la-chan.md): chung LC-T094-1, -2, -3 (phần dữ liệu); riêng LC-T094-18, -19, -20, -21 |
| Phạm vi | **Rút gọn** (dữ liệu chưa tin cậy, lời dặn AI). Diff `15bfaca..9e7cea6` (đầu nhánh lúc kiểm, chỉ có trên máy): `seo_app/plan/model.py`, `parse.py`, `propose.py` (3 file mới, tổng 1.593 dòng), `seo_app/content/models.py` (+30), `prompts.py` (+67/−6), `workflow.py` (+78); test mới `tests/test_plan_*.py` (4 file), `tests/test_soi_loi_t098.py`; 2 test cũ đổi (`test_soi_loi_t003_t009.py` gỡ 5 dòng `xfail`, `test_t040_prompts.py` 1 dòng). Đọc thêm: `prompts._neutralize`, `_block`, `DATA_RULES`, `system_prompt`; `seo_app/onpage/meta.py` (`has_html`, `compare_key`); `seo_app/wordpress/client.py` (`is_site_link`); `AIRouter.get`. Thử gộp với `main` trên máy `1b45f5d` (có T-096, chưa lên `origin`) |
| Ngày | 2026-10-28 (14:12–14:53 +07, giờ máy) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: tôi **không tìm thấy lỗi mới** (0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp). Còn **6 Thấp** của Soi Lỗi (SL-T098-12 → -17), tôi xét **không lỗi nào cần nâng mức**. Mọi điều kiện LC-T094 của phiếu đạt. **Không lỗi nào bắt buộc sửa trước khi gộp**; SL-T098-17 phải sửa trước khi T-101 nối giao diện (điều kiện 1). Gộp `main` được: không xung đột, test liên quan qua trên cây gộp |

## Tóm tắt (cho chủ dự án)

Phần «máy» đọc kế hoạch (file, chữ dán, đề xuất của AI) **an toàn để gộp**. Tôi thử ba kiểu tấn công. (1) Gài lệnh giả, thẻ khung giả, ký tự vô hình vào kế hoạch dán và vào từ khóa của kế hoạch đang có: phần lời dặn của phần mềm không đổi một chữ, chữ độc luôn nằm trong khung «dữ liệu». (2) Cho AI giả trả về hơn 26.000 đề xuất bậy (thẻ HTML ngụy trang, mã bài không có, đổi trạng thái, link, chữ khổng lồ): không đề xuất nào lọt qua được bộ kiểm; AI không xóa được dòng nào, không đổi được trạng thái bài (ngoài đề xuất «Bỏ», mà «Bỏ» không bao giờ tick sẵn), không đưa được link vào ô trang đích. (3) File, chữ dán dị dạng cỡ lớn sát giới hạn: không treo, chậm nhất khoảng 2 giây. Việc đọc kế hoạch **không bao giờ tìm web**; chữ có số điện thoại, email thì dừng lại hỏi trước khi gửi AI. 6 lỗi nhỏ Soi Lỗi tìm ra đều không phải lỗi bảo mật; một lỗi (kế hoạch có mã bài «B-99999» làm phần so bảng báo lỗi lạ) phải sửa trước khi làm giao diện trang Kế hoạch.

## Lỗi phát hiện

Không phát hiện lỗi mới.

## Đối chiếu điều kiện Lá Chắn T-094 của phiếu

| Mã | Đạt? | Bằng chứng |
|---|---|---|
| **LC-T094-1** Test không gọi Google, WordPress, AI thật | **Đạt** | AI giả (`PlanProvider`, `make_provider` giả), danh sách bài dựng trong bộ nhớ; Soi Lỗi thử «không tìm web» bằng chính lớp provider 3 hãng với client giả. Test mới không nhập `requests`, `socket`, `urllib.request`, `http.client` (`grep`); bộ chặn mạng `autouse` của `tests/conftest.py` vẫn bật |
| **LC-T094-2** Câu báo cố định | **Đạt** | Lỗi đọc nguồn là hằng (`parse.py` `FILE_TOO_BIG`, `FILE_BAD_TYPE`, `FILE_BAD_ENCODING`, `BAD_TABLE`, `TOO_MANY_*`, `PASTE_TOO_LONG`, `TEXT_TOO_LONG`, `EMPTY`), không chép tên file, chữ trong ô; câu báo ô sai chỉ có **tên cột chuẩn** và số dòng (`_Notes`); cảnh báo đề xuất chỉ có mã bài dạng `B-001` hay số mã bài đã đăng (`propose.py` `WARN_*`); mục AI sai chỉ đếm (`NOTE_AI_DROPPED`); `PersonalInfoError` chỉ có số lượng (`workflow.py:56`, `PERSONAL_INFO`). Lỗi `csv`, giải mã đổi thành câu cố định `from None`. Riêng `ValueError("hết mã bài")`: SL-T098-17 (điều kiện 1) |
| **LC-T094-3** (phần dữ liệu) Chữ thuần, bỏ ký tự đảo hướng và vô hình | **Đạt** | `clean_text` (`model.py:158`) bỏ Cc (trừ khoảng trắng), Cf (gồm U+202A–U+202E, U+2066–U+2069), Cs, Co, Cn và ký tự «mặc định bỏ qua»; mọi trường chữ của `PlanRow` và lý do AI đều qua đây. Thử độc lập: không trường nào của đề xuất AI còn ký tự loại Cc/Cf/Cs/Co/Cn (trừ xuống dòng ở ghi chú), mục «AI ngẫu nhiên» dưới. Hiện lên giao diện là việc T-101 (LC-T094-32) |
| **LC-T094-18** Một bộ làm sạch `PlanRow`, giới hạn | **Đạt** | `PlanRow` (`model.py:411`, `extra="forbid"`, `frozen`) là đường duy nhất cho file, chữ dán, AI. File: kiểm **byte trước khi giải mã** ≤ 1 MB (`parse.py:151`), chỉ `.csv/.tsv/.txt/.md`, chỉ `utf-8`/`utf-8-sig` không đoán (`:154-160`); ≤ 1.000 dòng, ≤ 26 cột kiểm **trong lúc** đọc (`_limited_rows`, `:253`; bảng Markdown `:279-283`), ô ≤ 2.000 ký tự cắt và báo (`_cell`, `:427`), chữ dán ≤ 20.000 kiểm trước khi đọc (`read_paste`, `:176`); `csv` chuẩn ở chế độ `strict` (`:241`), không `eval`, `pandas`; ngày không nhận `mm/dd`, năm 2020–2035 cả với số ngày kiểu Sheets (`model.py` `_in_range`, `_serial_date`). Thời gian: mục «Dữ liệu dị dạng» dưới |
| **LC-T094-19** SL-7 mọi lời dặn; khung `plan`; không tìm web | **Đạt** | `_keyword` (`prompts.py:56`: gộp một dòng, `_neutralize`, «» → ‹›) ở 5 lời dặn có từ khóa trong câu chỉ thị; `meta_prompt`, `blind_test_prompt` vốn để từ khóa trong khung. `plan_prompt` (`:512`): kế hoạch hiện tại trong `<ke_hoach_hien_tai>`, chữ dán trong `<ke_hoach_moi>`, cả hai qua `_block` (đã thêm vào `DATA_TAGS`, `:17-20`), lời dặn hệ thống có `DATA_RULES`; dòng kế hoạch gửi AI chỉ có mã, từ khóa, ngày, trạng thái, ưu tiên (`_plan_line`, `:504`: **không** gửi ghi chú của thợ). `_plan_task` (`workflow.py:417-427`) luôn `web_search=False`, kể cả khi dùng tạm cấu hình `outline` hay `[tasks.plan]` ghi `web_search = true`. Thử độc lập: mục «Lời dặn AI» dưới |
| **LC-T094-20** Kết quả AI chưa tin cậy | **Đạt** | `from_ai` (`propose.py:296`): ≤ 100 mục (`MAX_AI_ITEMS`), thừa thì đếm bỏ; mục sai bỏ và chỉ đếm; thẻ HTML kiểm trên **chữ đã làm sạch và cả bản NFKC** (`_has_html_text`, `:338`; SL-T098-1 đã sửa) ở từ khóa, từ khóa phụ, tiêu đề, ghi chú, lý do; lý do ≤ 300 ký tự; nhãn, ngày, giờ qua `PlanRow`; «Thêm» không được có mã, mã do code cấp; «Cập nhật»/«Bỏ» phải đúng mã có thật, mỗi mã một lần; khuôn `PlanSuggestion` không có slug, trang đích, trạng thái, mã bài WordPress (AI không đặt được); «Bỏ» chỉ đổi Trạng thái, không tick sẵn (`preselected`, `:130`), không hàm nào xóa dòng. AI đề xuất quá 20 thay đổi thì không tick sẵn cái nào (`AI_MANY`). Trang đích chỉ nhận **mã bài** có trong danh sách bài đã đăng (`resolve_target`, `parse.py:537`, có `is_site_link`), không giữ địa chỉ; chữ dạng địa chỉ ở lý do, ghi chú, tiêu đề chỉ là chữ |
| **LC-T094-21** A3 số điện thoại, email | **Đạt** (phần T-098) | `plan_changes` (`workflow.py:377`) dò trên chữ dán và từ khóa kế hoạch hiện tại (`:406`), chữ đã làm sạch và NFKC như chữ AI nhận (`model.py` `_visible_for_ai`); có thì `PersonalInfoError`, **không gọi AI** trừ khi người dùng đồng ý (`allow_personal`) hoặc che bằng `mask_personal_info` («[đã ẩn]»). Ghi chú của thợ không gửi AI. Chữ AI trả về có số điện thoại/email thì thêm cảnh báo (`WARN_PERSONAL`). Biểu thức dò có neo, giới hạn độ dài từng phần: 20.000 ký tự xấu nhất chạy dưới 15 ms (đo dưới). Nửa sau của điều kiện (khi điền ghi chú vào Soạn bài) thuộc T-102 |

## Thử tấn công (không gọi AI, website, mạng)

Script ở thư mục nháp của phiên, bản sao trong thư mục ghi chú chung `T-098-la-chan-scripts/`. Chạy trong worktree: `PYTHONUTF8=1 uv run python <script>`.

**Lời dặn AI (`lc_a1_plan.py`).** 81 mảnh độc: thẻ mở/đóng của **mọi** khung trong `DATA_TAGS` (hoa, có cách, tab), toàn khổ `＜／ke_hoach_moi＞`, `﹤…﹥`, chen 11 loại ký tự vô hình/đảo hướng giữa «<» và tên khung hay giữa tên khung; 7 kiểu xuống dòng kèm dòng kế hoạch giả «- B-999 | … »; «Bỏ qua mọi chỉ dẫn… SYSTEM: …»; dấu «» giả đóng câu chỉ thị rồi viết lệnh («» + xuống dòng + «Hôm nay là 01/01/2030.»); khối mã bọc `</ke_hoach_moi>`. Mỗi mảnh đặt **cùng lúc** vào chữ dán và vào từ khóa của một dòng kế hoạch hiện tại (qua `PlanRow` như mọi nguồn), và vào từ khóa của 5 lời dặn có từ khóa trong câu chỉ thị (`research`, `outline`, `write`, `review`, `rewrite`). 486 lời dặn. Kiểm: phần ngoài khung của `plan_prompt` **giống hệt** bản nhập chữ thường; số thẻ khung AI thấy (sau NFKC, bỏ ký tự vô hình) không tăng; đúng 2 khung, đúng thứ tự; khung kế hoạch hiện tại chỉ có dòng `- B-nnn | …` do code viết; dòng «Từ khóa…: «…»» của 5 lời dặn chỉ một dòng, không có «» bên trong, không có thẻ khung. **0 vi phạm.** Đối chứng (`lc_a1_plan_control.py`): tắt `_neutralize` → 782 vi phạm; `_keyword` không đổi «» → 405 vi phạm.

**AI trả lời độc (`lc_ai_parse.py`).** 400 lượt, mỗi lượt 1–130 mục ngẫu nhiên (26.092 mục) ghép từ: thẻ HTML ngụy trang (U+200B, U+00AD, U+FEFF, U+2060, U+034F, NUL chen sau «<»; `＜script＞`; `<svg/onload>`; chú thích HTML; `<?php`), `&lt;script&gt;`, link Markdown `javascript:`, địa chỉ web, chữ công thức (`=HYPERLINK(…)`, `+cmd`, `@SUM`), ký tự đảo hướng, số điện thoại, email, thẻ khung, dòng kế hoạch giả, nhãn/ngày/giờ đúng và sai, lý do 301 ký tự; hành động «them», «THÊM», «xoa», «delete»…; mã `B-1`, `b-001`, `B-0001`, `B-001`+U+200B (cùng một mã), mã không có, `B-99999`, mã ghép. Bất biến trên mọi kết quả: ≤ 100 đề xuất; không chữ nào còn thẻ HTML (cả sau NFKC) hay ký tự Cc/Cf/Cs/Co/Cn; lý do ≤ 300; «Bỏ» không tick sẵn; «Thêm» trạng thái «Chưa viết», không có trường app (slug, trang đích, mã bài WordPress, ngày đăng); «Cập nhật»/«Bỏ» chỉ trên mã có thật, không đổi trường app, không đổi trạng thái ngoài «Bỏ». **0 vi phạm.** Chữ dạng địa chỉ, link Markdown, công thức được giữ **là chữ** đúng thiết kế (LC-T094-20); trung hòa công thức khi ghi Sheet là LC-T094-28 của T-100 (điều kiện 2). Một mục có 3 trường 1.000.000 ký tự: 0,30 s (bị bỏ); 100.000 mục: 0,012 s (chỉ xét 100 mục đầu).

**Dữ liệu dị dạng sát giới hạn (`lc_ai_parse.py`).**

| Đầu vào | Thời gian | Kết quả |
|---|---|---|
| `.md` 1 MB một dòng `\|----…x` (dò dòng phân cách) | 0,40 s | Câu cố định (chữ tự do quá dài) |
| `.md` 1 MB một dòng toàn «\|» | 0,75 s | «Bảng có hơn 26 cột…» |
| `.md` ô 1 MB `**aaa…` / ô lặp `` `*_ `` / ô lặp `\\|` | 0,04–0,06 s | Đọc được |
| `.csv` 1 MB toàn dấu `"` | 0,09 s | «Không đọc được bảng…» |
| `.csv` 1 MB một dòng toàn dấu phẩy | 0,44 s | Câu cố định |
| `.csv` 500 dòng, ô «Ngày giờ đăng» ~2.000 ký tự `1 1h 1h…` | 1,27 s | Đọc được, ô sai bỏ trống |
| `.txt` 1 MB toàn tab; `.md` 1.000 dòng × 26 cột | 0,004 / 0,10 s | Câu cố định / đọc được |
| Chữ dán 20.000 ký tự `0 0 0…`, `aaaa…@b.vn`, `0.0.0…`, `(+84)(…`, 10.000 dòng «\|»; cả dò và che dữ liệu cá nhân | ≤ 0,017 s mỗi việc | Đọc được / «Bảng có hơn 1.000 dòng» |
| So bảng 1.000 dòng hiện tại + 1.000 dòng mới + 1.000 bài đã đăng | 1,95 s (lần đo riêng 1,12 s) | Quan sát 2 |

Không có biểu thức nào chạy bậc hai: các biểu thức giờ, ngày giờ chạy trên chữ đã gộp khoảng trắng (`clean_text`), dò số điện thoại có số lần lặp giới hạn, dò email có neo và giới hạn độ dài (SL-T098-7 đã sửa).

## Xếp mức 6 lỗi Thấp của Soi Lỗi (lượt 2)

| Mã | Ý kiến Lá Chắn |
|---|---|
| SL-T098-12 (một ô mở bằng chữ trong ngoặc kép làm hỏng cả bảng) | **Giữ Thấp**, không phải lỗi bảo mật: chỉ làm từ chối nhầm (hướng an toàn), câu báo cố định |
| SL-T098-13 (bảng «mục – nội dung» bị đọc nhầm thành kế hoạch, dòng giả tick sẵn) | **Giữ Thấp**: dòng giả chỉ là đề xuất «Thêm» người dùng còn duyệt; chữ đã qua `PlanRow`, không chạy được gì. Nên sửa trước khi gộp (Soi Lỗi đề xuất) vì dễ làm bẩn kế hoạch |
| SL-T098-14 (mất cảnh báo trang cửa ngõ với «P. Tân Định») | **Giữ Thấp**: chất lượng SEO, không phải bảo mật |
| SL-T098-15 (cảnh báo «AI có số điện thoại» thừa vì xét cả ghi chú cũ) | **Giữ Thấp**: báo thừa, theo hướng thận trọng; chữ cũ không gửi AI |
| SL-T098-16 (`46337.0` thành giờ 00:00) | **Giữ Thấp**: sai dữ liệu người dùng còn duyệt, không phải bảo mật |
| SL-T098-17 (mã «B-99999» trong kế hoạch làm so bảng, đề xuất AI ném `ValueError`) | **Giữ Thấp** hôm nay (chưa có giao diện), nhưng dữ liệu Sheet là chưa tin cậy và `ValueError` không phải `AIError`: khi T-101 nối giao diện, lỗi lạ có thể hiện thành khung lỗi kèm đường dẫn máy (security.md 2.1). **Điều kiện 1** |

Góp ý G9–G12 của Soi Lỗi: không phải bảo mật. G12 (mã bài chuẩn hóa) là việc của T-100.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` (đặt `PYTHONUTF8=1`) trên 15 file đổi và bản vá nhánh, kèm file mồi tiếng Việt: mồi bắt 2/2; chỉ báo khóa **giả** có từ trước trong `tests/test_soi_loi_t003_t009.py:229-256` (mục Báo nhầm). Lịch sử nhánh `15bfaca..9e7cea6`: 0 dạng khóa thật |
| S2 | Đạt (điều kiện 1 cho T-101) | Câu báo cố định (LC-T094-2); không log |
| S3 | Không áp dụng | Không biến `.env` mới; `config/` không đổi |
| W1–W4 | Không áp dụng | Không gọi WordPress, không lệnh mạng mới |
| A1 | Đạt | LC-T094-19 và mục «Lời dặn AI» |
| A2 | Đạt | LC-T094-20 và mục «AI trả lời độc»; việc `plan` không có công cụ (tắt tìm web trong code) |
| A3 | Đạt | LC-T094-21; ghi chú của thợ không gửi AI |
| U1–U3 | Không áp dụng | Không đổi `app/` (giao diện ở T-101) |
| F1 | Đạt | Không đọc file theo đường dẫn: `read_file` nhận byte và tên file chỉ để lấy đuôi; không ghi file |
| F2 | Không áp dụng | Không xử lý ảnh |
| F3 | Đạt | `csv` chuẩn, không `eval`, `pickle`, `pandas`; chỉ UTF-8 |
| D1 | Đạt | `pyproject.toml`, `uv.lock` không đổi (`git diff --quiet 15bfaca HEAD`); không thư viện mới |
| D2 | Không áp dụng | `.gitignore` không đổi |
| D3 | Đạt | LC-T094-1 |

## Kết quả công cụ quét

Máy chủ dự án, Windows 11, Python 3.12.15, worktree `wt-T-098` tại `9e7cea6`; có phiên khác chạy song song.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| detect-secrets 1.5.0 | **Đặt `PYTHONUTF8=1`**, `--all-files` trên bản sao 15 file đổi, bản vá nhánh và **file mồi tiếng Việt**: mồi bắt **2/2**; file thật: 4 mục ở `tests/test_soi_loi_t003_t009.py` (khóa giả có từ trước). Quét lại chính biên bản này cùng file mồi mới: biên bản 0 mục, mồi 2/2 | Có. Đã xóa cả hai file mồi |
| bandit 1.9.4 | `seo_app/plan`, `seo_app/content`: không có mục nào | Có |
| pip-audit | Không chạy: `uv.lock` không đổi | — |
| Soát lịch sử git | `git log -p 15bfaca..9e7cea6`: 0 dạng khóa thật (`sk-ant-…`, `AIza…`, `ghp_`, `PRIVATE KEY`, `xox`, `AKIA…`) | Có |
| pytest (nhánh) | 9 file (`test_plan_model`, `_parse`, `_propose`, `_ai`, `test_soi_loi_t098`, `test_soi_loi_t003_t009`, `test_t040_prompts`, `test_prompt_data_frames`, `test_content_workflow`): **696 passed, 11 xfailed** (11 = SL-T098-12 → -17) | Có |
| ruff | `uv run ruff check .`: `All checks passed!` | Có |
| Thử gộp | `main` trên máy `1b45f5d` (có T-096, chưa lên `origin`) + `9e7cea6`: `git merge-tree --write-tree` **không xung đột** (cây `326fe54`); hai bên không sửa chung file nào (`main` đổi `seo_app/images/alt.py`, `images/html.py`, `onpage/links.py`, `publish/*`, `wordpress/client.py`; `seo_app/publish/*` không nhập `content`, `plan`). Commit tạm trong worktree riêng (`git commit-tree`, không nhánh, đã gỡ): `ruff` sạch; 21 file test nhập module của **cả hai** phía, cộng test riêng của T-098, T-096 và `test_app_pages.py` (mở mọi trang): **3.506 passed, 16 xfailed** (gồm 11 của SL-T098-12 → -17), 0 hỏng, 16 phút 54 giây (máy đang chạy song song test toàn bộ của phiên khác; lượt đầu 91 file tôi dừng sau 8 phút vì quá chậm) | Có |

## Quan sát (không tính là lỗi)

1. Lời dặn `plan` đặt câu chỉ thị **sau** khung `<ke_hoach_moi>` (khung không phải khối cuối). Không phải lỗi: chữ dán vẫn nằm trọn trong khung đã vô hiệu thẻ, và câu chỉ thị cuối cùng do code viết; T-103 (Ngòi Bút) viết lại chữ thì giữ nguyên hai khung và `DATA_RULES` (LC-T094-42, góp ý G6).
2. So trùng với bài đã đăng (`_duplicate_post`, `propose.py:482`) xét từng cặp (đề xuất × bài đã đăng): 1.000 dòng mới × 1.000 bài 1–2 s; ở mức tối đa client đọc (10.000 bài × 1.000 dòng) khoảng 12 s. Site thật ít bài hơn nhiều; danh sách bài lấy từ chính website, không phải dữ liệu người lạ đưa vào. Nếu website lớn lên: dựng chỉ mục (slug, từ) một lần, hoặc T-101 hiện vòng chờ.
3. Chữ đề xuất (từ bảng hay AI) có thể bắt đầu bằng `=`, `+`, `-`, `@`, và có thể chứa địa chỉ web, link Markdown, chữ dạng shortcode: đúng thiết kế là **chữ**. Lớp chặn nằm ở chỗ dùng: T-100 ghi Sheet (LC-T094-28), T-101 hiện chữ thuần (LC-T094-32), các đường gửi WordPress đã có (T-061, T-096).

## Báo nhầm đã loại

- detect-secrets «Base64 High Entropy String», «Secret Keyword» ở `tests/test_soi_loi_t003_t009.py:229-232`, `:256`: chuỗi khóa **giả** (`sk-ant-api03-AbC_dEf-…`, `AIzaSyA1234…`, `Authorization: Basic bGFt…`) của test lọc bí mật có từ trước (đã có ở gốc `15bfaca`); T-098 chỉ xóa 5 dòng `xfail` trong file này.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

Không điều kiện nào bắt buộc trước khi gộp T-098 vào `main` (phần này chưa nối vào giao diện).

| # | Điều kiện | Phiếu nhận | Hạn |
|---|---|---|---|
| 1 | **SL-T098-17:** kế hoạch có mã gần giới hạn («B-99999») không được làm so bảng, đề xuất AI ném `ValueError`; chỉ báo «hết mã bài» (câu cố định, lớp lỗi app hiện được) khi thật sự cần cấp mã mới. Gỡ `xfail` khi XPASS (R5). Nếu chưa sửa: T-101 phải bắt mọi lỗi của `parse.*`, `propose.*`, `plan_changes` (cả `ValueError`) và hiện câu cố định, không bao giờ để Streamlit hiện khung lỗi kèm đường dẫn máy | Thợ Máy (lượt sửa nhỏ của T-098, cùng SL-T098-13, -12 Soi Lỗi khuyên) hoặc T-101 | Trước khi T-101 nối trang Kế hoạch |
| 2 | **T-100:** LC-T094-28 (ô `RAW`, trung hòa chữ mở đầu `=` `+` `-` `@` tab CR) áp cho **mọi** ô ghi Sheet, kể cả chữ từ đề xuất của AI (chữ dán có thể dụ AI viết công thức như `=IMPORTXML(…)`); tìm dòng theo mã đã chuẩn hóa (G12) | T-100 | Khi làm T-100 |
| 3 | **T-101:** hiện lý do AI, tiêu đề, ghi chú, cảnh báo bằng chữ thuần (LC-T094-3, -32: có thể chứa link Markdown, địa chỉ); `PersonalInfoError` → cảnh báo kèm «Che số điện thoại, email» / «Vẫn gửi» (số có thể nằm ở từ khóa kế hoạch hiện tại chứ không chỉ chữ dán: «Che» phải che cả hai, hoặc báo rõ chỗ nào còn số); tải file kiểm kích thước trước khi đọc (LC-T094-33) | T-101 | Khi làm T-101 |
| 4 | T-102 dùng `personal_info`/`mask_personal_info` khi điền «Ghi chú của thợ» vào Soạn bài (nửa sau LC-T094-21); T-103 thêm 2 khung kế hoạch vào `DATA_RULES` (G6, LC-T094-42), `[tasks.plan]` không có `web_search` | T-102, T-103 | Khi làm các phiếu đó |
| 5 | Kiểm lại biên bản này bằng Claude Fable sau 01/11 | Chỉ Huy | Sau 01/11 |

Không có rủi ro nào cần chủ dự án quyết định chấp nhận; không thêm dòng vào sổ rủi ro (`security.md` mục 6).

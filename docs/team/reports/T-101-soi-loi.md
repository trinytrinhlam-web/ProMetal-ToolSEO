# Báo cáo T-101 · Giao diện Giai đoạn 5: trang Kế hoạch, Cài đặt → Google, trang Bài viết · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-101](../tickets/T-101-giao-dien-ke-hoach-cai-dat-google.md), Họa Sĩ `6b0c785` (gốc `main` `fd28bbc`) |
| Ngày nộp | 2026-10-30 (19:21 +07:00) |
| **Kết luận** | **ĐẠT**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp; 3 góp ý nhỏ (không chặn). Cả 7 việc Chỉ Huy giao đều đạt; R5 đúng (chỉ 1 ca đã duyệt); gộp được với `main` `17b2a31` (không xung đột) |

## Tóm tắt (cho chủ dự án)

- **Trang Kế hoạch, Cài đặt → Google, trang Bài viết chạy đúng và an toàn.** Tôi thử chữ cố tình làm hỏng (link giả, thẻ HTML, ký tự đảo chữ, ký tự vô hình) ở Sheet, file tải lên, ghi chú của AI và cả **tên Sheet** do Google trả: mọi chỗ đều hiện thành chữ thường, không thành link hay định dạng; không in đường dẫn file khóa, mã Sheet đầy đủ, nội dung file khóa.
- **«Áp dụng thay đổi» không bao giờ ghi trùng hay ghi đè.** Hai tab cùng thêm một bài: chỉ một dòng. Bấm xong thì nút biến mất, tải lại trang không ghi thêm. Mất mạng đúng lúc thêm dòng: trang báo «chưa rõ», bảo bấm «Tải lại», đọc lại cùng bảng thì không đề xuất thêm lần hai. Dòng bị xóa trên Sheet giữa chừng: không ghi, không thêm lại, bảng «trước / bây giờ / đề xuất» ghi «(không thấy)».
- **Chỉ mở trang thì không tốn gì:** trang Bài viết (trang mở đầu) không gọi Google, WordPress; trang Kế hoạch chỉ đọc Google Sheets khi bản lưu trên máy đã cũ hơn 5 phút (đúng thiết kế); tick, xem, đổi tab không gọi mạng, không gọi AI. Chạy hết bộ test, không file nào bị ghi vào thư mục `data/` thật.
- **Không có lỗi. Không có gì phải anh/chị quyết.**

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t101.py` | Mới: **7 ca, đều qua**. Không gọi Google, WordPress, AI thật (cùng bộ giả với test của Họa Sĩ) |
| `docs/team/reports/T-101-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, test của Họa Sĩ, phiếu hay file khác.

## Kiểm từng mục (7 việc Chỉ Huy giao)

### 1. Dữ liệu chưa tin cậy: không chữ chạy được, không lộ đường dẫn, mã Sheet, email, khóa

Soát mọi chỗ hiện chữ của 3 trang (`app/views/plan.py`, `home.py`, `settings.py` phần T-101):

| Chữ từ đâu | Hiện bằng | Kết quả |
|---|---|---|
| Dòng kế hoạch (Sheet, cache), đề xuất, lý do của AI, `Conflict.now` | `st.dataframe`, `st.text`; câu báo qua `escape_markdown` (`plain`/`show`) | An toàn (test của Họa Sĩ: link `javascript:`, `<b>`, U+202E, U+200B) |
| Từ khóa trong ô chọn «Chọn bài để viết», «Từ kế hoạch» | `st.selectbox` + `format_func` | An toàn: ô chọn của Streamlit 1.65 hiện chữ thuần (khác `st.radio`, không đọc Markdown); từ khóa đã qua `PlanRow` |
| Nhãn ô tick đề xuất | `pick_label`: số dòng, loại, Mã bài dạng `B-001` | Không có chữ dữ liệu |
| Tiêu đề nháp, từ khóa ở trang Bài viết | `escape_markdown` (đã escape cả `$`, `:`, `[`, `]`); tiêu đề nháp qua `clean_text` trước | An toàn |
| **Tên Sheet** Google trả khi «Kiểm tra kết nối» | client bỏ ký tự điều khiển, vô hình (`_clean_text`), trang `visible` + `escape_markdown` | **Tôi thêm ca**: tên Sheet có link Markdown, `<b>`, U+202E, U+200B → câu báo chữ thuần, không còn U+202E (`test_sheet_title_from_google_is_plain`) |
| Tên file khóa, email, cảnh báo của file khóa | `folder_name_md`, `st.code(visible(email))`, `escape_markdown` | Không đường dẫn, không mảnh khóa (test của Họa Sĩ) |
| Mã Sheet | `mask_sheet_id` (4 ký tự cuối) | Không hiện đầy đủ ở đâu |

- Không `unsafe_allow_html` mới (chỗ duy nhất là khung «Đang viết» bản demo có từ trước, chữ hằng đã `html.escape`), không `st.table`, không `st.exception`, không `st.cache_*`.
- Câu lỗi là câu cố định của lớp lỗi app; `ValueError` lạ thành câu cố định (test chuỗi mồi của Họa Sĩ: lời máy chủ Google, file khóa).

### 2. «Áp dụng» chỉ ghi qua đường T-100

`apply_chosen` gọi đúng `sync.apply_proposals(client, plan_base, các dòng đã tick)` (bản người dùng đã xem, `RAW`, so ô, «chưa rõ» đọc lại Mã bài, không xóa dòng); xong (dù kết quả nào) thì bỏ bộ đề xuất. Tôi thêm 4 ca:

| Tình huống | Kết quả |
|---|---|
| **Hai tab** cùng dán một bài mới (cùng Mã bài B-004), lần lượt «Áp dụng» | Tab đầu thêm dòng; tab sau: xung đột «đã có», bảng xung đột hiện B-004; Sheet có **đúng một** dòng |
| **Bấm lại** / chạy lại trang sau «Áp dụng» | Nút «Áp dụng» không còn; chạy lại 2 lần: không lệnh ghi nào thêm |
| Lệnh thêm dòng **đứt mạng sau khi Google đã thêm**, đọc lại cũng lỗi (mã 500 có chuỗi mồi) | Câu báo «chưa rõ … Tải lại», không chuỗi mồi; bộ đề xuất bị bỏ (không áp dụng lại được); dán lại đúng bảng đó: «Không có thay đổi…», không đề xuất «Thêm»; Sheet có đúng một dòng |
| Sau khi xem đề xuất, dòng B-001 bị **xóa** trên Sheet | Không ghi ô, không thêm lại dòng; bảng xung đột: «Bây giờ trên Sheet» = «(không thấy)» |
| Ô bị sửa ở nơi khác (test của Họa Sĩ) | Không ghi; «trước / bây giờ / đề xuất» |

### 3. Không gọi mạng, AI khi chỉ mở trang hay chạy lại trang; không tạo file

| Kiểm | Kết quả |
|---|---|
| Trang Kế hoạch đã mở (đã đọc Sheet một lần), rồi tick, bỏ tick, «Xem đủ một đề xuất», đổi tab nguồn, chạy lại trang (WordPress, AI giả đều đã khai báo) | **0** lệnh Google, **0** lệnh WordPress mới, **0** lần gọi AI, không ghi Sheet (`test_reruns_with_fresh_cache_call_nothing`) |
| Trang **Bài viết** (trang mở đầu), đã khai báo Google và WordPress, chưa có bản lưu | **0** lệnh Google, **0** lệnh WordPress; không tạo file cache kế hoạch, cache bài, kho nháp (`test_home_page_opens_without_network_or_new_files`) |
| Cài đặt → 📗 Google khi mở | 0 lệnh (test của Họa Sĩ); «Kiểm tra kết nối», «Chuẩn bị trang tính» chỉ khi bấm |
| Thư mục `data/` thật của worktree sau 21 file test (gồm mọi test mở 3 trang) | **Không có** thư mục `data/` (không test nào ghi cache thật) |

Ghi rõ (đúng thiết kế 2.6, không phải lỗi): mở trang **Kế hoạch** khi bản lưu đã cũ hơn 5 phút thì đọc lại Google Sheets một lệnh (chỉ đọc); trong 5 phút thì không gọi. Các nút gọi mạng khác (đọc kế hoạch, AI, áp dụng, hỏi website, thử ghi lại) chỉ chạy khi bấm.

### 4. «Viết bài», hợp đồng `_start_plan_key`

- `write.py` **không đổi** (diff `fd28bbc..6b0c785` không có file này).
- «Viết bài» (trang Kế hoạch) và «Bắt đầu» (trang Bài viết) đúng hợp đồng của báo cáo Họa Sĩ: đã có nháp của Mã bài (Sheet đang dùng) thì `_open_draft`, bỏ `_start_plan_key` cũ; chưa có thì `open_row` đọc lại (chỉ `GET`), dựng lại qua `PlanRow`, Mã bài qua `parse_key` hai lần, đặt `_start_keyword`, `_start_plan_key`; 0 lệnh WordPress (test của Họa Sĩ chạy lại trên nhánh và bản gộp: qua).
- Góp ý G1 (dưới): đường «Viết bài mới» gõ tay chưa bỏ `_start_plan_key` còn sót.

### 5. Hai lỗi Họa Sĩ tự sửa

| Lỗi | Kiểm | Kết quả |
|---|---|---|
| Trang Bài viết (trang mở đầu) mở kho nháp hỏng nên cất file lặng lẽ, trang Soạn bài không còn báo | `tests/test_app_drafts.py::test_corrupt_drafts_file_is_reported` (qua), test của Họa Sĩ: file hỏng để lại cho Soạn bài, chưa có file thì không tạo | **Đóng** |
| Tạo `data/plan_cache.sqlite` thật khi chỉ mở trang | Trang chỉ mở kho khi file đã có; ca của tôi ở mục 3; sau 21 file test không có `data/` | **Đóng** |

### 6. R5 và các tab Cài đặt

- Diff test cũ (`fd28bbc..6b0c785`): chỉ `tests/test_app_pages.py::test_plan_reading_shows_proposed_changes` đổi kỳ vọng, đúng phương án A Chỉ Huy duyệt (giữ tên ca; nay: chưa khai báo Google, dán chữ, bấm đọc → báo «Chưa đọc được kế hoạch hiện tại», không đề xuất, không gọi AI). Không ca cũ nào khác bị đổi, xóa, `skip`, `xfail`.
- Tab «📗 Google» đặt cuối, 4 tab cũ giữ vị trí: `test_soi_loi_t019.py`, `test_soi_loi_t023.py`, `test_soi_loi_t084.py`, `test_settings_blind.py`, `test_settings_keys.py`, `test_settings_images.py` đều qua (không lùi T-019, T-023, T-084).

### 7. Mở mọi trang; gộp thử với `main` mới nhất

- `tests/test_app_pages.py` (mở mọi trang, mọi bước Soạn bài): qua trên nhánh và trên bản gộp.
- Gộp thử `team/T-101` vào `main` **`17b2a31`** (có T-099 lượt 2, T-107 lượt 1–2) trong worktree tạm (không nhánh, không push, đã gỡ): **không xung đột**. `main` mới chỉ đổi `seo_app/wordpress/client.py` (phần `release_draft`, không đụng `post_statuses`, `from_settings` mà T-101 dùng) và phần ảnh HEIC. Chạy trên bản gộp 11 file (đăng nhập, mọi trang, kho nháp, 3 file T-101 của Họa Sĩ, file của tôi, T-019, T-023, T-084, `test_wordpress_release.py` của T-099): **457 passed, 0 failed**.

## Lỗi và góp ý

Không có lỗi mới.

**Góp ý (không xếp lỗi):**

- **G1 (phòng xa cho T-102):** ô «Viết bài mới» của trang Bài viết (gõ từ khóa) chỉ đặt `_start_keyword`, không bỏ `_start_plan_key` còn sót. Trước T-102, `write.py` chưa đọc khóa này nên sau một lần «Viết bài» theo dòng kế hoạch, Mã bài cũ nằm yên trong phiên; nếu T-102 đọc `_start_plan_key` mỗi khi có `_start_keyword` thì bài gõ tay sau đó sẽ bị gắn nhầm dòng kế hoạch cũ. Khi T-102 đã chạy, mỗi lần «Viết bài» đều được `write.py` lấy và bỏ ngay nên không còn khóa sót (và app khởi động lại thì phiên mới). Gợi ý: đường gõ tay `S.pop("_start_plan_key", None)`; T-102 chỉ dùng `_start_plan_key` khi nó đi cùng đúng lần đặt `_start_keyword` của nút kế hoạch (hay kiểm từ khóa của dòng đọc lại khớp `_start_keyword`).
- **G2:** sau «Thử ghi lại» (việc ghi trạng thái còn nợ), trang đặt `_plan_reload` nhưng không chạy lại, nên bảng danh sách vẫn hiện trạng thái cũ tới lần bấm kế tiếp (câu báo kết quả thì hiện ngay). Gợi ý: `st.rerun()` sau khi thử ghi xong, như «Áp dụng».
- **G3 (ghi nhận):** mở trang Kế hoạch khi đã khai báo cả Google lẫn WordPress thì `cached_index()` mở kho cache bài đã đăng, tạo file `data/site_index.sqlite` rỗng nếu chưa có (là cache theo thiết kế T-037, xóa vẫn tạo lại). Test của Họa Sĩ đều trỏ cache sang thư mục tạm; góp ý fixture chung trong `tests/conftest.py` của Họa Sĩ (mục «Đề xuất» báo cáo T-101) sẽ chặn hẳn chuyện test nào quên.

## Cách tái hiện

```bash
uv run pytest -q tests/test_soi_loi_t101.py
```

## Bằng chứng

- `tests/test_soi_loi_t101.py`: **7 passed**.
- 21 file test chọn lọc trên nhánh `6b0c785` (20 file Họa Sĩ đã dùng: mọi file mở trang Kế hoạch, Cài đặt, Bài viết, kho nháp, cùng file của tôi): **698 passed, 6 skipped, 0 failed** (23 phút; máy đang chạy toàn bộ test của Chỉ Huy; 6 ca bỏ qua có từ trước: symlink cần quyền trên Windows, quyền kiểu POSIX). Sau lượt chạy, worktree **không có** thư mục `data/`.
- Bản gộp thử với `main` `17b2a31` (commit gộp tạm `c63683c`, không xung đột): 11 file `test_app`, `test_app_pages`, `test_app_drafts`, `test_t101_home_page`, `test_t101_plan_page`, `test_t101_settings_google`, `test_soi_loi_t101`, `test_soi_loi_t019`, `test_soi_loi_t023`, `test_soi_loi_t084`, `test_wordpress_release`: **457 passed, 0 failed** (7 phút); bản gộp cũng không có thư mục `data/` sau khi chạy.
- `uv run ruff check .` sạch; `ruff format --check` file test của tôi sạch; quét ký tự ẩn: file của tôi và 3 trang sạch; `PYTHONUTF8=1 uvx detect-secrets scan` file của tôi: 0 phát hiện (mồi «AKIA…» trong file tiếng Việt tạm: bắt được, đã xóa).
- Không mở app thật (đủ bằng AppTest; Họa Sĩ đã mở app ở cổng 8509 và trả `launch.json` nguyên bản).

## Đối chiếu tiêu chí xong (phần việc Soi Lỗi)

| Việc Chỉ Huy giao | Kết quả |
|---|---|
| 1. Dữ liệu Sheet, file, chữ AI chưa tin cậy; câu lỗi cố định | Đạt (mục 1) |
| 2. «Áp dụng» chỉ qua đường T-100; Sheet đổi giữa chừng; bấm hai lần, hai tab | Đạt (mục 2) |
| 3. Không gọi mạng, AI khi chỉ mở trang, chạy lại; Bài viết không gọi Google; không tạo file `data/` | Đạt (mục 3; trang Kế hoạch đọc Sheet khi bản lưu cũ hơn 5 phút là đúng thiết kế) |
| 4. «Viết bài», `_start_plan_key`; không chạm `write.py` | Đạt (mục 4; góp ý G1) |
| 5. Hai lỗi Họa Sĩ tự sửa đóng hẳn | Đạt (mục 5) |
| 6. R5; không lùi T-019, T-023, T-084 | Đạt (mục 6) |
| 7. `test_app_pages.py`; gộp thử `main` `17b2a31` | Đạt (mục 7) |

## Đề xuất

- Gửi T-101 sang Lá Chắn rút gọn.
- Chuyển G1 vào phiếu T-102 (cách đọc `_start_plan_key`).

## Câu hỏi cho chủ dự án

Không có.

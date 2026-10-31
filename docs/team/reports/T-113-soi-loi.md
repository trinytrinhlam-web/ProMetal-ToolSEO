# Báo cáo T-113 · Nút «Cập nhật trạng thái từ website» ở trang Kế hoạch; ô công thức trang Kết nối · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | T-113 (file phiếu chưa có trên `main`, đọc bản ở thư mục tạm của Chỉ Huy), Họa Sĩ đầu nhánh `7b93af1` (gốc `main` cục bộ `bb25dde`: có T-101, T-102, T-109); điều kiện lượt nối nút của Lá Chắn T-109 (cả «Xem lại lượt 2»), G1, G2 Soi Lỗi T-109 |
| Ngày nộp | 2026-10-31 (13:45 +07:00) |
| **Kết luận** | **ĐẠT**: 0 lỗi mới. Điều kiện (a)–(f) của Lá Chắn T-109, G1, G2 làm đúng; chỉ chạy khi bấm, chạy lại trang không gọi mạng; hai tab, bấm ghi lại, Sheet đổi giữa chừng, lần kiểm cũ, giờ máy lùi, website lỗi: không ghi sai, câu cố định; chữ Sheet / website hiện thuần, không lộ mã Sheet, đường dẫn. Không lùi T-101, T-102, T-109, trang Kết nối, T-084 (ca T-084 Họa Sĩ báo là **oan thật**: quá giờ chờ AppTest khi máy bận). Test T-113 không ghi vào `data/` (file `data/site_index.sqlite` gặp khi chạy là của `tests/test_soi_loi_t102.py` có sẵn trên `main`). 4 góp ý nhỏ |

## Tóm tắt (cho chủ dự án)

- **Nút «🌐 Cập nhật trạng thái từ website» làm đúng như thiết kế.** Bấm thì phần mềm chỉ **hỏi** website (không sửa bài nào), so với Google Sheet rồi hiện bảng đề xuất. Không dòng nào được tick sẵn; chỉ dòng anh/chị tick mới được ghi, và mỗi dòng chỉ đổi 3 ô: Trạng thái, Ngày đăng thực tế, Cập nhật lúc.
- **Ghi an toàn khi có chuyện bất thường.** Tôi thử: hai cửa sổ cùng bấm ghi, bấm ghi lại lần nữa, xóa / đảo thứ tự / chép trùng dòng trên Sheet sau khi kiểm, đổi mã bài website của một dòng, đồng hồ máy chạy lùi, website lỗi giữa chừng khi hỏi hơn 100 bài, Google lỗi lúc ghi. Không lần nào ghi nhầm dòng hay ghi hai lần; dòng đã đổi thì phần mềm dừng và nói rõ vì sao.
- **Chỉ chạy khi bấm.** Mở trang, chuyển trang, chạy lại trang không hỏi website, không đọc hay ghi Google Sheet thêm.
- **Chữ lạ trên Sheet hay từ website** (link, thẻ HTML, ký tự đảo chiều chữ) hiện như chữ thường; câu báo không chép chữ trong ô; trang không bao giờ hiện mã Google Sheet hay đường dẫn file khóa.
- **Bảng chuyên mục, thẻ ở trang Kết nối WordPress** tải về mở bằng Excel không còn thành công thức.
- Một bài kiểm tra cũ (T-084) từng báo đỏ khi Họa Sĩ chạy: tôi chạy lại, nó chỉ đỏ khi máy quá bận (quá 30 giây chờ), không phải lỗi phần mềm.
- **Không có lỗi mới. Không có gì phải anh/chị quyết.**

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t113.py` | Mới: **11 ca, đều qua**. Không gọi Google, WordPress thật (Google Sheets giả qua `SheetsClient` thật, WordPress giả đếm request; cache ở thư mục tạm) |
| `docs/team/reports/T-113-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, test của Họa Sĩ, phiếu hay file khác.

## Kiểm từng mục

### 1. Điều kiện lượt nối nút của Lá Chắn T-109 (lượt 1 và «Xem lại lượt 2»), G1, G2

| Điều kiện | Cách làm (đọc mã) | Kiểm |
|---|---|---|
| (a) chỉ chạy khi bấm; nút đọc, nút ghi riêng; chỉ ghi thay đổi người dùng tick, không tick sẵn | Đọc: `plan-web` → `ask_website` (`plan.py:661`). Ghi: `plan-web-write` trong khung riêng, `disabled` khi chưa tick hay lần kiểm cũ; ô tick `value=False`, khóa theo lần kiểm (`plan_webround`) | Test Họa Sĩ (không tick sẵn, «Chọn tất cả» là một lần bấm, chỉ ghi dòng đã tick) và `test_reruns_with_check_and_result_call_nothing`: có lần kiểm, rồi có kết quả ghi, chạy lại trang 2 lần mỗi lúc: **0** lệnh WordPress, **0** lệnh Google Sheets mới, không tạo lần kiểm mới |
| (b) truyền thẳng `post_statuses`, đúng mã đã hỏi, `sheet_id`, `now=settings.now()`; không dùng `S.plan_web`; `website.LATE_AFTER` | `check_website(plan, states, ids, sheet_id=settings.google_sheet_id, now=settings.now())`; `S.plan_web` (bộ đôi chữ) chỉ cho cột «Trên website» | Test Họa Sĩ (gián điệp ghi lại tham số: `PostState`, mã 501–503, mã Sheet, giờ có múi giờ; hằng dùng chung) |
| (c) bắt `MSG_STALE`, `MSG_OTHER_SHEET`, `MSG_NO_COLUMNS`, hiện chữ thuần, mời kiểm lại; không ghi bằng lần kiểm cũ | Giao diện khóa nút ghi khi quá `CHECK_MAX_AGE`; `apply_web` bắt `SheetPlanError`, hiện câu của lõi, bỏ lần kiểm | Test Họa Sĩ (cũ 6 phút, lõi từ chối) và `test_clock_moved_back_is_refused_with_fixed_text`: giờ máy lùi 3 phút (giao diện không khóa vì chỉ xét «quá 5 phút»), lõi từ chối **trước khi đọc Sheet**, trang hiện đúng câu `MSG_STALE`, bỏ lần kiểm, 0 lệnh ghi |
| (d) client Google, WordPress mới mỗi lần bấm | `wordpress_client()`, `sheets_client()` tạo mới trong hàm bấm; phiên chỉ giữ `WebCheck`, `WebApplyResult` (dữ liệu, không có link bài) | Đọc mã |
| (e) lý do, cảnh báo (cả `ODD_CELL`, `UNSURE_ROW`), xung đột chữ thuần; bảng qua `safe_text` | Cảnh báo qua `show()` (`escape_markdown`); bảng thay đổi, bảng xung đột qua `safe_rows` | `test_odd_sheet_and_website_data_stay_plain_and_fixed`: ô có link Markdown, `<b>`, U+202E, ô Trạng thái «Xong rồi…», ô Ngày «hôm qua…», Mã bài trùng «b-3», một bài ở hai dòng, website trả trạng thái lạ / giờ hỏng: mọi cảnh báo trên trang **đúng từng chữ** câu của lõi, không mồi, trang thuần |
| (f) bắt `SheetsError`, `SheetPlanError`, `ValueError`, `WordPressError` | `ask_website`, `apply_web` | `test_website_error_in_a_later_chunk_keeps_no_check`, `test_sheet_id_and_paths_never_shown` (lỗi Google khi ghi), test Họa Sĩ (lỗi 500 website, lỗi đọc Sheet) |
| G1 | `plan.py:636`, `home.py:211` dùng `website.LATE_AFTER`, giờ `settings.now()` | Test Họa Sĩ (đổi hằng lõi thì nhãn đổi); `test_t101_home_page` (nhãn «Lỡ lịch» trang Bài viết) qua |
| G2 | Như (b) | Như (b) |

### 2. Ghi: hai tab, bấm ghi lại, Sheet đổi giữa chừng, website lỗi

| Tình huống | Kết quả |
|---|---|
| Hai tab cùng kiểm; tab đầu ghi B-003; tab sau tick B-003, B-004 rồi ghi | Lệnh ghi thứ nhất chỉ dòng 4 (B-003), lệnh thứ hai chỉ dòng 5 (B-004); tab sau báo «Đã cập nhật 1 dòng… 1 dòng đã đúng sẵn» |
| Bấm ghi lần nữa với đúng lần kiểm đó (như bấm đúp, tab cũ còn giữ lần kiểm) | Lõi đọc lại, thấy đã đúng: không có lệnh ghi thứ hai, báo «đã đúng sẵn». Trên giao diện thật, ghi xong khung kiểm đóng nên nút ghi không còn để bấm lần hai |
| Sau lần kiểm: xóa dòng B-003 / đảo ngược thứ tự dòng / đổi Mã bài WordPress của B-003 / chép trùng dòng B-003 | Ghi theo Mã bài: đảo thứ tự thì ghi đúng cả hai dòng ở chỗ mới; ba trường hợp kia B-003 vào bảng «Vì sao chưa ghi» (chữ thuần), không ghi B-003; B-004 vẫn ghi đúng; chỉ 3 cột của app, không thêm dòng |
| 150 bài: website trả được lệnh hỏi đầu (100 bài), lệnh thứ hai lỗi 500 có mồi | Câu cố định, không mồi; lần kiểm trước đó cũng bị bỏ (không còn bảng cũ để ghi); không lệnh ghi Sheet; mọi lệnh tới WordPress là GET |
| Lần kiểm cũ quá 5 phút, Sheet khác, Sheet thiếu cột, dòng vừa bị sửa, lỗi đọc Sheet khi ghi, website lỗi 500 | Test Họa Sĩ, chạy lại qua |

### 3. Không lộ mã Sheet, đường dẫn

`test_sheet_id_and_paths_never_shown`: đọc, tick, ghi (một dòng xung đột), kiểm lại, rồi Google lỗi khi ghi (mồi trong lời Google). Quét **mọi chuỗi** của mọi phần tử trên trang (`page_strings`, như T-084): không có mã Sheet, đường dẫn file khóa, tên thư mục khóa, thư mục tạm, thư mục dự án, mồi.

### 4. Không lùi; `test_app_pages`; không ghi `data/`

- R5: Họa Sĩ không đổi test cũ (đã đối chiếu `git diff bb25dde 7b93af1 -- tests/`: chỉ thêm `test_t113_website_status.py`).
- 21 file chọn lọc (T-113, T-109 ×2, T-101 ×5, `test_app_pages`, trang Kết nối: `test_app_wordpress`, `test_app_t044_safe_text`, `test_soi_loi_t044`, `test_soi_loi_t031`, `test_soi_loi_t085`, `test_soi_loi_t088`, `test_la_chan_t093`, `test_t106_trang_ket_noi`, `test_soi_loi_t106`; `test_soi_loi_t084`, `test_app_drafts`, `test_plan_sync`): **2.474 qua, 3 xfail** có sẵn (SL-T106-1 ×2, SL-T108-1), 0 hỏng (lượt này ca T-084 qua). 4 file T-102 (`test_t102_publish`, `test_t102_formula_cells`, `test_soi_loi_t102`, `test_la_chan_t102`): **66 qua, 4 xfail** có sẵn (SL-T102-1 ×3, LC-T102-1), 0 hỏng.
- **Ca T-084 «hỏng oan»** (`test_soi_loi_t084.py::test_whole_settings_page_never_shows_env_values_or_paths`): chạy riêng 3 lần lúc máy đang chạy bộ test khác: lần 1 hỏng với `RuntimeError: AppTest script run timed out after 30(s)` (quá giờ chờ một lượt chạy trang, không phải câu kiểm sai), lần 2, 3 qua (26 giây, 23 giây cả lượt); chạy ngay sau 25 ca T-113 trong cùng một lượt: qua. T-113 không đổi `app/main.py`, `app/views/settings.py`, `seo_app/`, `config/` (`git diff --stat` rỗng). Kết luận: **oan thật**, do máy bận.
- **Không ghi `data/`:** sau 21 file trên (và chạy riêng test T-113 cùng ca T-084), worktree không có `data/`. Sau 4 file T-102 thì có `data/site_index.sqlite`: chạy riêng từng file, file này do `tests/test_soi_loi_t102.py` tạo (có sẵn trên `main`; Họa Sĩ ghi nhận thêm `test_la_chan_t102.py`; tôi đã báo ở Soi Lỗi T-109 lượt 2), không phải T-113. Trang Kế hoạch không còn tạo file này khi chỉ mở trang (test Họa Sĩ `test_opening_plan_page_does_not_create_site_index`). Đã xóa file thử sinh ra trong worktree.

### 5. Gộp thử với `main` cục bộ

`main` vẫn là `bb25dde`, tổ tiên của nhánh: gộp là tiến thẳng. `git merge-tree --write-tree main 7b93af1` cho cây `a0bb753`, **trùng** cây của nhánh, nên kết quả test trên nhánh chính là của bản gộp.

## Góp ý (không xếp lỗi)

- **G1.** Nhiều cảnh báo thì mỗi câu một khung vàng: Sheet 300 dòng mà tài khoản WordPress mất quyền xem nháp sẽ hiện 300 khung «Không thấy bài…». Có thể gộp theo loại (đếm, hiện vài dòng đầu, phần còn lại trong mục thu gọn). Bảng thay đổi lớn cũng tạo từng ấy ô tick (đã có «Chọn tất cả»).
- **G2.** Câu viết cứng số phút: `MSG_WEB_NOTE` «15 phút», `MSG_WEB_STALE` «quá 5 phút» (cùng loại G8 của T-109 ở lõi). Đổi `website.LATE_AFTER` / `CHECK_MAX_AGE` mà quên câu thì câu sai; khi giờ máy lùi, câu của lõi vẫn nói «quá 5 phút». Có thể dựng câu từ hằng.
- **G3.** Hỏi website lần sau bị lỗi thì khung kiểm bị bỏ (đúng), nhưng cột «Trên website» vẫn giữ trạng thái của lần hỏi trước, không còn giờ kiểm đi kèm (cách cũ của T-101). Có thể bỏ cả `S.plan_web` khi bắt đầu hỏi lại.
- **G4.** Trang Kết nối WordPress nhập `seo_app.plan.sync` (kéo theo client Google) chỉ để dùng `safe_text`. Nên chuyển `safe_text` sang một mô-đun chữ dùng chung (ví dụ `seo_app/text.py`) để trang WordPress không phụ thuộc phần kế hoạch.

## Lệnh đã chạy

```
uv run pytest tests/test_soi_loi_t113.py -q                                        # 11 qua
uv run pytest <21 file: T-113, T-109, T-101, trang, trang Kết nối, T-084, kho nháp, sync> -q   # 2.474 qua, 3 xfail (SL-T106-1 ×2, SL-T108-1)
uv run pytest <4 file T-102> -q                                                    # 66 qua, 4 xfail (SL-T102-1 ×3, LC-T102-1)
uv run pytest <ca T-084> -q  (×3; rồi sau test T-113)                              # 1 quá giờ chờ, 2 qua; qua
git merge-tree --write-tree main 7b93af1                                            # a0bb753 = cây nhánh
uv run ruff check tests/test_soi_loi_t113.py; uv run ruff format --check tests/test_soi_loi_t113.py
PYTHONUTF8=1 uvx detect-secrets scan --all-files <bản chép file đổi + file mồi>     # chỉ file mồi bị bắt
```

Quét ký tự ẩn trên các file đổi và file test mới: sạch. Không gọi Google, WordPress thật; không chạy cloud; không mở app.

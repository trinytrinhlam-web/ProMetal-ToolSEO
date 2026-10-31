# Biên bản bảo mật T-113 · Nút «Cập nhật trạng thái từ website» ở trang Kế hoạch; ô công thức trang Kết nối

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-113](../tickets/T-113-noi-nut-cap-nhat-trang-thai-website.md) (Họa Sĩ `7b93af1`, Soi Lỗi `44d2a8a`, gốc `main` `bb25dde`) · điều kiện 1 (a)–(f) cho lượt nối nút của biên bản [Lá Chắn T-109](T-109-la-chan.md) (cả «Xem lại lượt 2») · [Lá Chắn T-094](T-094-la-chan.md): chung LC-T094-1, -2, -3; LC-T094-26, -28, -29, -32, -35 · LC-T101-1 ([T-101](T-101-la-chan.md)) · Ghi nhận 3 [Lá Chắn T-102](T-102-la-chan.md) |
| Phạm vi | **Rút gọn**. Diff `bb25dde..44d2a8a`: `app/views/plan.py` (+201/−13), `app/views/home.py` (+4/−4), `app/views/wordpress.py` (+13/−1), 2 file test mới (`test_t113_website_status.py`, `test_soi_loi_t113.py`), 2 báo cáo. Đọc thêm: lõi `seo_app/plan/website.py` (T-109, đã trên `main`), `WordPressClient.post_statuses`, `_state_from`, `_is_date_gmt`, `model.parse_plan_date`, `parse_plan_datetime`, `sync.safe_text`, `app/main.py`, `.streamlit/config.toml`. Nhánh không đổi `seo_app/**`, `config/`, `pyproject.toml`, `uv.lock`, test cũ |
| Ngày | 2026-10-31 (13:53–14:15 +07, giờ máy) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp mới (LC-T113-1)**. Điều kiện (a)–(f) của T-109 làm đúng; không gọi mạng hay ghi Sheet ngoài ý người dùng; dữ liệu website, Sheet hiện thuần; LC-T101-1 đóng cả ở trang Kết nối (và ở mọi bảng của app có chữ từ ngoài). LC-T113-1: website trả ngày ở cuối năm 9999 thì nút đọc hiện lỗi Python có traceback thay vì câu cố định; không ghi gì; gốc ở lõi T-109 (`_due_of`). **Không lỗi nào bắt buộc sửa trước khi gộp**; LC-T113-1 nên sửa trước khi thử thật Giai đoạn 5. Góp ý G1–G4 của Soi Lỗi không cần làm trước khi gộp. Gộp được: `origin/main` `731a46e` (chỉ tài liệu) và `main` cục bộ `4ee27d8` (T-110 lượt 2–3) đều không xung đột, không sửa chung file; trên cây gộp với `4ee27d8`: `ruff` sạch, 17 file test chọn lọc **756 passed**, 7 xfailed (4 ca LC-T113-1, 3 ca có sẵn), **0 failed** |

## Tóm tắt (cho chủ dự án)

Nút «🌐 Cập nhật trạng thái từ website» ở trang Kế hoạch **an toàn để gộp**:
- Chỉ chạy khi anh/chị bấm. Bấm thì phần mềm chỉ **hỏi** website (không sửa bài nào), rồi hiện các dòng nên đổi. Không dòng nào được tick sẵn; chỉ dòng anh/chị tick mới được ghi, mỗi dòng đúng 3 ô: Trạng thái, Ngày đăng thực tế, Cập nhật lúc.
- Lần kiểm đã quá 5 phút, Sheet đã đổi, dòng vừa bị sửa ở nơi khác: phần mềm không ghi và nói rõ vì sao. Chữ lạ trên Sheet hay từ website hiện như chữ thường.
- Bảng chuyên mục, thẻ ở trang Kết nối WordPress khi tải về mở bằng Excel không còn thành công thức.

Tôi tìm thấy một lỗi nhỏ: nếu một bài trên website có ngày ở **cuối năm 9999** (ngày vô lý, phải có người cố tình đặt; website đặt giờ Việt Nam thì không chọn được ngày đó từ trang quản trị thông thường), bấm nút sẽ hiện lỗi kỹ thuật thay vì câu báo dễ hiểu. Không ghi gì, không lộ mật khẩu hay khóa. Sửa chỉ vài dòng; không cần chờ sửa mới gộp.

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Hạn |
|---|---|---|---|---|
| LC-T113-1 | **Thấp** | Website trả `date_gmt` đúng khuôn nhưng ở cuối năm 9999: lõi ném `OverflowError` (không phải `ValueError`), lọt qua các khối `except` của nút đọc; trang hiện lỗi Python kèm traceback, có đường dẫn đầy đủ file app, thay vì câu cố định (trái LC-T094-2). Không ghi gì | `seo_app/plan/website.py:590` (`_due_of`); lộ ra ở `app/views/plan.py:685-693` | Trước khi thử thật Giai đoạn 5 (không bắt buộc trước khi gộp) |

### LC-T113-1 chi tiết

- **Đường đi thật.** Website trả mục `{"id": 501, "status": "publish", "date_gmt": "9999-12-31T23:59:59"}` cho một bài có Mã bài WordPress trong Sheet. Client chỉ kiểm khuôn `[0-9]{4}-[0-9]{2}-…` (`client.py:192`, `_is_date_gmt` `:2486`), nên giữ nguyên chuỗi. Bấm «🌐 Cập nhật trạng thái từ website» → `check_website` → `_known_states` → `_due_of` (`website.py:579`): `strptime` qua, rồi `moment.astimezone(model.TIMEZONE)` để xét năm; sang +07 là năm 10000 → `OverflowError: date value out of range`. `_due_of` chỉ bắt `ValueError`, `ask_website` chỉ bắt `SheetPlanError`, `ValueError` (`plan.py:688`, `:691`), `app/main.py` không bọc `navigation.run()`, `.streamlit/config.toml` không đặt `client.showErrorDetails` → khung lỗi Streamlit có traceback.
- **Hậu quả.** Cả lần kiểm hỏng: mọi dòng khác cũng không cập nhật được, tới khi bài đó đổi ngày hay bỏ khỏi Sheet. Lỗi chỉ hiện ở lần bấm: thử bằng AppTest, lần chạy trang kế tiếp trở lại bình thường (danh sách, cột «Trên website» còn, không có lần kiểm), bấm lại thì lỗi lại hiện; traceback 8 dòng, có đường dẫn đầy đủ. **Không** ghi Sheet, không ghi website (lỗi xảy ra trước khi có lần kiểm, nút ghi không có). Traceback chỉ có tên file, số dòng, dòng code của app (cả đường dẫn thư mục cài app trên máy), không có khóa, mật khẩu, mã Sheet.
- **Ngưỡng.** Từ `9999-12-31T17:00:00` giờ UTC. `9999-12-31T16:59:59` vẫn đúng: cảnh báo «giờ không đọc được» (`ODD_DATE`), vẫn đề xuất đổi Trạng thái. Các ngày lạ khác đã có test (năm 2050, `0000-00-00…`, ngày 29/02 năm thường, chuỗi 100.000 chữ số) đều đúng.
- **Ai tạo được.** Người sửa được ngày bài trên website: site đặt múi giờ từ +06:59 trở xuống (kể cả UTC) thì có thể đặt ngày cuối năm 9999 từ trang quản trị (suy từ giới hạn ngày giờ của WordPress, chưa thử trên site thật); hoặc sửa thẳng cơ sở dữ liệu, công cụ nhập bài, plugin đổi dữ liệu REST. Site giờ Việt Nam (+07) thì giờ UTC lớn nhất là `16:59:59`, không tràn. Ngoài ra, mã bài trong Sheet do người sửa Sheet đặt, nên ai sửa được Sheet có thể trỏ một dòng tới bài có ngày như vậy.
- **Vì sao Thấp.** Chỉ hỏng một chức năng, theo hướng an toàn (không ghi); đầu vào phải cố tình dựng; không lộ bí mật. Gốc ở lõi T-109: tôi đã bỏ sót khi kiểm T-109 (hai lượt). Lúc đó lõi chưa nối giao diện; T-113 nối nút nên đường này mới tới được từ trang.
- **Cách sửa.** Ở lõi: `_due_of` xét năm trên giờ UTC trước khi đổi múi giờ, hoặc bắt thêm `OverflowError` như `ValueError` → `(None, True)`. Kết quả: cảnh báo `ODD_DATE`, vẫn đề xuất đổi Trạng thái, không đổi ngày, đúng hợp đồng test T-109 `test_odd_website_date_changes_status_but_not_date`. Sửa `seo_app/plan/website.py` nằm ngoài phạm vi T-113, nên cần Chỉ Huy cho phép. Lớp chặn thêm ở giao diện là tùy chọn: `ask_website` bắt `OverflowError` → `MSG_WEB_ODD`.
- **Test.** `tests/test_la_chan_t113.py`: 4 ca `xfail(strict=True)` (2 ở lõi `check_website`, 2 qua trang Kế hoạch bằng AppTest, ngày `17:00:00` và `23:59:59`) và 2 ca đối chứng mốc `16:59:59` (qua). Đã chạy `--runxfail`: cả 4 hỏng đúng vì `OverflowError: date value out of range` ở `website.py:590`. Ca qua trang không gắn với cách sửa: sửa ở lõi hay ở giao diện đều qua. Sửa xong thì gỡ 4 dấu `xfail` (R5).

## Các câu Chỉ Huy hỏi

| Câu hỏi | Trả lời |
|---|---|
| Điều kiện (a)–(f) đạt? | **Đạt** (bảng «Đối chiếu điều kiện»). Riêng (f): giao diện bắt đúng các loại lỗi đã đặt; LC-T113-1 là một loại lỗi khác (`OverflowError`) lọt ra từ lõi |
| Không gọi mạng, không ghi Sheet ngoài ý người dùng? | **Đạt.** Lệnh WordPress duy nhất là `post_statuses` (GET, chỉ đọc), chỉ trong `ask_website` (`plan.py:661`, `:677`), chỉ gọi từ nút `plan-web` (`:967`). Lệnh ghi Sheet duy nhất là `apply_website_changes` trong `apply_web` (`:802`, `:812`), chỉ gọi từ nút `plan-web-write` (`:791`); nút khóa khi chưa tick hay lần kiểm quá 5 phút (`:794`). Khung kiểm, khung kết quả vẽ lại từ `session_state`, không gọi mạng. Ghi xong, `_plan_reload` (`:827`) chỉ **đọc** lại Sheet, là hệ quả của lần bấm. «Chọn tất cả» chỉ tick, không ghi. Soi Lỗi đếm: chạy lại trang khi đang có lần kiểm hay kết quả: 0 lệnh WordPress, 0 lệnh Google mới. Trang Kế hoạch không còn tạo `data/site_index.sqlite` khi chỉ mở (`:175`) |
| Dữ liệu website, Sheet hiện thuần? | **Đạt.** Bảng thay đổi, bảng xung đột qua `safe_rows` (`:761`, `:839`) trong `st.dataframe` (không đọc Markdown). Cảnh báo, câu kết quả qua `show()` → `escape_markdown`. Nhãn ô tick (có đọc Markdown) chỉ có số dòng, Mã bài (khuôn `[A-Z]{1,3}-[0-9]{1,5}`, `model.py:132`) và mã bài là số (`plan.py:768`, `WebUpdate.label`). Ô Trạng thái là nhãn chuẩn của `PlanRow`; giờ do app định dạng; lý do, cảnh báo là câu cố định của lõi. Hai tiêu đề `st.markdown` mới là chữ hằng; không `unsafe_allow_html`. Soi Lỗi gài link Markdown, `<b>`, U+202E vào ô Sheet và lời website: hiện thuần, đúng từng chữ câu của lõi |
| LC-T101-1 (loại công thức) đóng cả ở trang Kết nối? | **Đóng.** Bảng chuyên mục, thẻ: Tên, Slug qua `cell()` → `safe_text` (`wordpress.py:34`, `:160`); ID, Số bài là số. Tôi rà mọi `st.dataframe`, `st.data_editor` của `app/`: `plan.py` 6 bảng, đều qua `safe_rows`; `write.py` đều qua `safe_text` hay `cell_text` (T-102); `wordpress.py` bảng này; `settings.py` 2 bảng chỉ có tên việc, hãng, mô hình từ `config/ai.toml` và nhãn do code dựng, không có chữ từ website, Sheet, AI. Không còn bảng nào đưa chữ từ ngoài vào CSV mà chưa trung hòa |
| Góp ý Soi Lỗi cần làm trước khi gộp? | **Không.** G1 (nhiều cảnh báo, nhiều ô tick): tối đa theo 1.000 dòng Sheet, chỉ chậm, không phải bảo mật. G2 (câu viết cứng «15 phút», «quá 5 phút»): chỉ lệch chữ khi đổi hằng. G3 (cột «Trên website» giữ trạng thái lần hỏi trước khi lần hỏi sau lỗi): chỉ để xem; đường ghi dùng lần kiểm, mà lần kiểm đã bị bỏ, nên không ghi theo dữ liệu cũ. G4 (`wordpress.py` nhập `seo_app.plan.sync`): `sync.py` chỉ có `import`, `def`, hằng, không chạy gì lúc nạp; chỉ là chuyện gọn phụ thuộc, nên chuyển `safe_text` sang mô-đun chữ dùng chung khi tiện |

## Đối chiếu điều kiện

| Điều kiện | Đạt? | Bằng chứng |
|---|---|---|
| T-109 đk 1 (a): chỉ khi bấm; nút đọc, nút ghi riêng; không tick sẵn | **Đạt** | Đọc: `plan-web` → `ask_website`. Ghi: `plan-web-write` trong khung riêng, chỉ có khi đã có lần kiểm. Ô tick `value=False` (`:769`), khóa theo lần kiểm (`plan_webround`); «Chọn tất cả» là một lần bấm riêng. Test Họa Sĩ, Soi Lỗi (chạy lại trang 0 lệnh mạng) |
| (b): truyền thẳng `post_statuses`, đúng mã đã hỏi, `sheet_id`, `now`, `LATE_AFTER` | **Đạt** | `plan.py:685`: `check_website(plan, states, ids, sheet_id=settings.google_sheet_id, now=settings.now())`, `states` là đúng kết quả `post_statuses(ids)` (`:677`). `S.plan_web` (bộ đôi chữ) chỉ cho cột «Trên website». `website.LATE_AFTER` ở `plan.py:636`, `home.py:211` |
| (c): lần kiểm cũ | **Đạt** | Giao diện khóa nút ghi khi quá `CHECK_MAX_AGE` (`:777`, `:794`). Lõi tự từ chối (quá 5 phút, giờ lùi quá 1 phút, Sheet khác, thiếu cột) → `SheetPlanError` → `apply_web` bỏ lần kiểm, hiện câu của lõi (`:815`–`:818`). Soi Lỗi thử giờ máy lùi 3 phút: lõi từ chối trước khi đọc Sheet |
| (d): client mới mỗi lần bấm | **Đạt** | `wordpress_client()` (`:133`), `sheets_client()` (`:122`) dựng mới mỗi lần gọi. Phiên chỉ giữ `WebCheck`, `WebApplyResult`, `plan_web` (dữ liệu; không khóa, không link bài) |
| (e): chữ thuần, bảng qua `safe_text` | **Đạt** | Câu hỏi 3 ở trên |
| (f): bắt lỗi thành câu cố định | **Đạt, trừ LC-T113-1** | `ask_website`: `WordPressError` (`:678`), `SheetPlanError` (`:688`), `ValueError` (`:691`). `apply_web`: `SheetPlanError`, `SheetsError`, `ValueError` (`:815`–`:823`). `sheets_client()` bắt `SheetsError`, `ServiceAccountError`, `ConfigError`. Câu của `SheetsError`, `WordPressError` là câu cố định (T-097, T-060); `post_statuses` chỉ ném `WordPressError`; `PlanKeyError` là `ValueError` |
| LC-T094-1 | **Đạt** | Test dùng `FakePlanSheet` qua `SheetsClient` thật, `FakeWordPress`; bộ chặn mạng không đổi |
| LC-T094-2 | **Đạt, trừ LC-T113-1** | Câu báo mới là hằng (`MSG_WEB_*`); lỗi Google, WordPress là câu cố định; Soi Lỗi gài mồi vào lời máy chủ: không hiện. LC-T113-1 hiện traceback có đường dẫn đầy đủ |
| LC-T094-3, LC-T094-32 | **Đạt** | Câu hỏi 3 |
| LC-T094-26 | **Đạt** | Giao diện chỉ gọi `post_statuses` (client kiểm mã, `include` ≤ 100 mã, `status`, `_fields` hằng); kết quả chỉ dùng để ghi 3 ô Sheet, không dẫn tới lệnh ghi WordPress (test Họa Sĩ, Soi Lỗi: mọi request là GET) |
| LC-T094-28, LC-T094-29 | **Đạt** (lõi T-109) | Giao diện chỉ đưa đúng các `WebUpdate` của lần kiểm đang hiện (lõi kiểm lại, khác thì `ValueError`, chưa ghi); lõi đọc lại Sheet trước khi ghi, so từng ô với bản đã xem, chỉ ghi 3 ô, `RAW` (test Họa Sĩ kiểm cột đã ghi và `RAW`) |
| LC-T094-35 | **Đạt** | Nút mới không gửi gì lên WordPress |
| LC-T101-1, Ghi nhận 3 T-102 | **Đạt** | Câu hỏi 4 |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets (`PYTHONUTF8=1`) trên file đổi, test mới, báo cáo, bản vá nhánh, kèm file mồi tiếng Việt: mồi bắt 2/2, file thật 0 mục. Lịch sử `bb25dde..44d2a8a` (2 commit): 0 dạng khóa |
| S2 | Đạt (không bí mật) | Câu báo mới là hằng; lỗi Google, WordPress là câu cố định. LC-T113-1 làm hiện traceback có đường dẫn file app, không có bí mật |
| S3 | Không áp dụng | Không biến `.env` mới |
| W1 | Không áp dụng | Không hẹn giờ, không đăng |
| W2 | Đạt | Chỉ GET `post_statuses`; không ghi, không xóa gì trên site |
| W3 | Không áp dụng | Không gửi HTML |
| W4 | Đạt | Dùng client sẵn có (`WordPressClient.from_settings`: `https`, SSL, timeout), không đổi |
| A1–A3 | Không áp dụng | Không AI |
| U1 | Đạt | Không `unsafe_allow_html`; 2 tiêu đề `st.markdown` mới là chữ hằng |
| U2 | Đạt | Không thêm trang; trang Kế hoạch, Kết nối vẫn qua cổng đăng nhập (`test_app_pages.py` qua) |
| U3 | Không áp dụng | Không đổi đăng nhập |
| F1 | Đạt | Không đọc, ghi file mới; trang Kế hoạch thôi tạo `data/site_index.sqlite` khi chỉ mở (`plan.py:175`) |
| F2, F3 | Không áp dụng | Không ảnh, không đọc file |
| D1 | Đạt | Không thư viện mới; `pyproject.toml`, `uv.lock` không đổi |
| D2 | Đạt | `.gitignore` không đổi |
| D3 | Đạt | LC-T094-1 |

## Kết quả công cụ quét

Máy chủ dự án, Windows 11, Python 3.12.15, `uv` 0.13.4, worktree `wt-T-113` tại `44d2a8a`; máy đang chạy toàn bộ test của Chỉ Huy.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| detect-secrets 1.5.0 | **Đặt `PYTHONUTF8=1`**, `--all-files` trên bản sao 6 file code, test đổi (cả `test_la_chan_t113.py`), 2 báo cáo, bản vá nhánh và **file mồi tiếng Việt**: mồi bắt **2/2**; file thật 0 mục | Có. Đã xóa file mồi |
| bandit 1.9.4 | `PYTHONUTF8=1`, `plan.py`, `home.py`, `wordpress.py` (1.404 dòng): không có mục nào | Có |
| pip-audit | Không chạy: `uv.lock` không đổi | — |
| Soát lịch sử git | `git log -p bb25dde..44d2a8a`: 0 dạng khóa | Có |
| ruff | `ruff check`, `ruff format --check` trên `tests/test_la_chan_t113.py`: sạch. `ruff check .` trên cây gộp (dòng «Thử gộp», kèm bản cuối của file test này): sạch | Có |
| pytest | `tests/test_la_chan_t113.py` trên nhánh: **2 passed, 4 xfailed** (17 giây); `--runxfail`: 4 ca hỏng đúng vì `OverflowError` ở `website.py:590`. Soi Lỗi đã chạy 21 file trên nhánh (2.474 qua) và 4 file T-102; tôi không chạy lại trên nhánh mà chạy trên cây gộp (dòng dưới) | Có |
| Thử gộp | `origin/main` `731a46e` + `44d2a8a`: `git merge-tree --write-tree` **không xung đột** (cây `be3bb00`); từ gốc chung `bb25dde`, `731a46e` chỉ đổi `CLAUDE.md` và tài liệu, nên code cây gộp trùng nhánh. `main` cục bộ `4ee27d8` (có `731a46e` và T-110 lượt 2–3: `seo_app/wordpress/client.py`, `app/views/write.py`) + `44d2a8a`: **không xung đột** (cây `890d485`), hai bên không sửa chung file; T-110 chỉ đổi đường tải ảnh (`_post_media`, `create_draft_with_images`, `_draft_images_error`), không đụng `post_statuses`, chuyên mục, thẻ. Commit tạm `733cf62` (`git commit-tree`, không nhánh) trong worktree tạm `wt-T113-lc-gop` (đã gỡ). Trên cây gộp: `ruff check .` sạch; 17 file (T-113: `test_la_chan_t113`, `test_t113_website_status`, `test_soi_loi_t113`; T-109: `test_t109_website_status`, `test_soi_loi_t109`; T-101: `test_t101_plan_page`, `test_t101_home_page`, `test_la_chan_t101`, `test_soi_loi_t101`; `test_app_pages`; trang Kết nối: `test_app_wordpress`, `test_t106_trang_ket_noi`, `test_soi_loi_t106`, `test_app_t044_safe_text`; T-110: `test_t110_gan_anh_vao_bai_nhap`, `test_la_chan_t110`, `test_soi_loi_t110`): **756 passed, 7 xfailed** (4 ca LC-T113-1; 3 ca có sẵn SL-T106-1 ×2, SL-T108-1), **0 failed**, 5 phút 6 giây. Không sinh thư mục `data/` | Có |

## Quan sát (không tính là lỗi)

1. **Nút ghi chỉ khóa theo «quá 5 phút».** Giờ máy lùi thì nút không khóa, nhưng lõi từ chối trước khi đọc Sheet (lùi quá 1 phút), trang hiện câu cố định. Không ghi sai.
2. **Ngày website giữ nguyên chuỗi trong `S.plan_web`.** `web_label` (`plan.py:633`) và `web_badge` (`home.py:207`) chỉ trừ hai mốc giờ, không đổi múi giờ, nên không tràn với ngày năm 9999; ngày sai khuôn thì `strptime` ném `ValueError`, đã bắt.
3. **G3 Soi Lỗi.** Cột «Trên website» có thể hiện trạng thái của lần hỏi trước, không ghi giờ. Chỉ để xem; đường ghi không dùng nó.
4. Họa Sĩ ghi nhận 8 ca test T-102 ghi `data/site_index.sqlite` vào thư mục chạy test (qua `write.py`). Đây là chuyện cách ly test, không phải lỗi của app; nên làm fixture trong `tests/conftest.py` như Họa Sĩ đề xuất.

## Báo nhầm đã loại

Không có: detect-secrets, bandit không báo mục nào ở file thật.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

Không điều kiện nào bắt buộc trước khi gộp T-113 vào `main`.

| # | Điều kiện | Phiếu nhận | Hạn |
|---|---|---|---|
| 0 | **LC-T113-1** sửa ở lõi: `_due_of` không để lọt `OverflowError` (xét năm trên giờ UTC trước khi đổi múi giờ, hay bắt như `ValueError`). Cần Chỉ Huy cho phép sửa `seo_app/plan/website.py`. Gỡ 4 `xfail` khi XPASS (R5); chạy test T-109, T-113 | Thợ Máy (phiếu nhỏ hay T-113 lượt 2) | Trước khi thử thật Giai đoạn 5 |
| 1 | Kiểm lại biên bản này bằng Claude Fable sau 01/11 | Chỉ Huy | Sau 01/11 |

LC-T113-1 có lượt sửa, không cần chủ dự án chấp nhận rủi ro; không thêm dòng vào sổ rủi ro (`security.md` mục 6).

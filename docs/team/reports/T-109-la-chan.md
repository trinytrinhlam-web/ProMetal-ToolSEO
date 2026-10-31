# Biên bản bảo mật T-109 · Lõi đưa trạng thái bài trên website về Google Sheets

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-109](../tickets/T-109-dong-bo-trang-thai-website-ve-sheet.md) (Thợ Máy `b511036`, Soi Lỗi `09870bd`, gốc `main` `eef13b5`) · điều kiện [Lá Chắn T-094](T-094-la-chan.md): chung LC-T094-1, -2, -3; đồng bộ LC-T094-28 (T-100); điều kiện biên bản [T-100](T-100-la-chan.md) (LC-T100-1, -3, SL-T100-4), [T-101](T-101-la-chan.md) (LC-T101-1) |
| Phạm vi | **Rút gọn**. Diff `eef13b5..09870bd`: `seo_app/plan/website.py` (mới, 601 dòng: `check_website`, `apply_website_changes`), `tests/test_t109_website_status.py`, `tests/test_soi_loi_t109.py`. Đọc thêm: `seo_app/plan/sync.py` (`_connected_hash`, `read_sheet`, `_key_of`, `_post_id_of`, `to_cell`, `_moment_text`), `WordPressClient.post_statuses`. Không đổi `sync.py`, `app/`, `config/`, client Google, WordPress |
| Ngày | 2026-10-30 (23:13–23:20 +07, giờ máy) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: Lá Chắn **0 lỗi mới**; 3 Thấp của Soi Lỗi (SL-T109-1 → -3) **giữ Thấp, không nâng**. Không có lối nào ghi ra ngoài 3 ô, ghi công thức, ghi sang Sheet khác hay thêm/xóa dòng. **Không lỗi nào bắt buộc sửa trước khi gộp** (chưa nối giao diện); **SL-T109-1 → -3 phải sửa trước khi nối nút**. Gộp `origin/main` `a416e74` được: không xung đột, code của cây gộp trùng nhánh, 10 file test chọn lọc qua, 0 hỏng |

## Tóm tắt (cho chủ dự án)

Phần lõi «Cập nhật trạng thái từ website» **an toàn để gộp**. Nó chỉ đọc trạng thái bài trên website rồi đề xuất sửa cột Trạng thái, Ngày đăng thực tế trên Google Sheet:
- Mỗi lần ghi chỉ đụng **3 ô**: Trạng thái, Ngày đăng thực tế, Cập nhật lúc. Giá trị là chữ của phần mềm, nên không thể thành công thức.
- App không thêm, không xóa dòng, không đổi ô Mã bài WordPress, không ghi sang Sheet khác Sheet đã kiểm.
- Trạng thái chỉ đi tới, không lùi. Dữ liệu lạ từ website (trạng thái lạ, giờ hỏng, mã lạ) bị bỏ qua hay chỉ cảnh báo.

Soi Lỗi tìm 3 lỗi nhỏ, chỉ xảy ra khi ô trên Sheet gõ rất lạ (ví dụ 30 dấu cách trước Mã bài). Lỗi đáng chú ý nhất có thể ghi trạng thái vào một dòng trùng của **cùng bài**, thay vì dòng anh/chị đang xem. Không mất dữ liệu, không ảnh hưởng website. Cần sửa trước khi gắn nút vào trang Kế hoạch.

## Lỗi phát hiện

Lá Chắn không phát hiện lỗi mới.

## Xếp mức 3 lỗi Thấp của Soi Lỗi

| Mã | Ý kiến Lá Chắn | Hạn |
|---|---|---|
| SL-T109-1 (Mã bài có ≥ 30 ký tự trắng hay vô hình đầu ô + một dòng trùng mã: bộ đọc giữ dòng đầu, lúc ghi lại ghi vào dòng sau) | **Giữ Thấp, không nâng**, dù trái LC-T094-28 («Mã bài trùng → không ghi»). Lý do: (1) `_cells_for` chỉ ghi khi dòng tìm được có **cùng** Mã bài WordPress với dòng người dùng đã xem (`website.py:429-445`), nên dòng bị ghi nhầm luôn là một dòng trùng của **cùng bài, cùng mã**; (2) giá trị ghi là nhãn và giờ của code (không phải chữ do người sửa Sheet đặt), chỉ 3 ô; (3) muốn dựng được ô như vậy thì đã có quyền sửa Sheet, sửa thẳng còn dễ hơn, nên không ai có thêm quyền gì. Gốc lỗi: `sync._key_of` cắt 30 ký tự **trước** khi làm sạch, còn `PlanRow` làm sạch cả ô (cùng gốc với SL-T109-2, `_post_id_of`). Đường T-100 không bị: `_update` so cả ô Mã bài với bản gốc nên ra xung đột; `open_row` chặn trước khi «Viết bài» | Trước khi nối nút |
| SL-T109-2 (Mã bài WordPress có ≥ 30 ký tự trắng đầu ô: một bài nối hai dòng không bị nhận ra) | **Giữ Thấp.** Cùng gốc. Kết quả: đề xuất cho cả hai dòng của **cùng một bài**, ghi được một; không ghi sang bài khác | Trước khi nối nút |
| SL-T109-3 (ô Trạng thái / Ngày đăng gõ chữ tự do: đề xuất được, ghi luôn bị từ chối với lý do «vừa bị sửa ở nơi khác») | **Giữ Thấp**, không phải bảo mật: hỏng theo hướng an toàn (không ghi), chỉ sai câu báo | Trước khi nối nút |

**Cách sửa gợi ý.**
- Chỉ trong `website.py` (Soi Lỗi đã thử bản nháp: 6 `xfail` qua, 114 ca khác vẫn qua): `_cells_for` đòi `fresh.find(key).number == key_rows[key][0]` như `open_row`; đếm bài trên chữ đã làm sạch; tách câu báo «ô không đọc được».
- Nếu sửa tận gốc `sync._key_of` / `_post_id_of` (làm sạch rồi mới giới hạn độ dài), phải chạy test mọi nơi gọi: `parse_sheet`, `apply_proposals`, `write_status`, `open_row`, `_key_present`, `website.py`.

## Các câu Chỉ Huy hỏi

| Câu hỏi | Trả lời |
|---|---|
| Có lối nào ghi ra ngoài 3 ô? | **Không.** `apply_website_changes` chỉ gọi `client.update_cells` (`website.py:414`), không `append_row`, `batch_update`. `_cells_for` chỉ dựng `CellUpdate` cho cột Trạng thái, Ngày đăng thực tế, Cập nhật lúc (`:458`, `:462`, `:468`), vị trí cột lấy theo tên trên bản vừa đọc lại. Ô Mã bài WordPress không bao giờ được ghi. Dòng tìm theo Mã bài, đúng một dòng (trùng → không ghi; Sheet đầy mà không thấy → không ghi). Client T-097 còn chặn lại: ô đơn A–Z, dòng ≤ 1.001, `RAW` |
| Ghi công thức? | **Không.** Trạng thái là nhãn của code (`to_cell` → `safe_text`, nhãn không mở đầu bằng `=` `+` `-` `@`); hai ô ngày giờ do app dựng (`2026-11-05 09:00+07:00`). `WebUpdate` không mang chữ ô Sheet hay lời website. Lệnh ghi luôn `RAW` (client chặn ở lớp kiểm). Test kiểm từng ô đã ghi |
| Ghi Sheet khác? | **Không.** `check_website` lưu mã băm Sheet đã kiểm; `apply_website_changes` so bằng `_connected_hash` (`:384`): luôn `client.sheet_hash`, `sheet_id` nơi gọi đưa thì phải khớp (bản đã sửa SL-T100-4). Khác → `SheetPlanError`, chưa đọc, chưa ghi. `updates` phải là thay đổi của chính lần kiểm (không tự dựng được, trùng thì từ chối) |
| Dữ liệu website chưa tin cậy? | **Đạt.** `_known_states` (`:494`): mã là số nguyên dương thật, đúng mã đã hỏi, `id` của mục trùng khóa; trạng thái phải thuộc `POST_STATUSES` và bảng nhãn (lạ như `trash`, `inherit`, `PUBLISH` → coi như không thấy). `_due_of` (`:518`): `date_gmt` đúng khuôn 19 ký tự, đọc theo UTC, năm 2020–2035; sai → không ghi ngày, cảnh báo «giờ không đọc được». «Lỡ lịch» so bằng giờ có múi giờ. `private`, về nháp, đã đăng mà website còn hẹn giờ, dòng «Bỏ»: chỉ cảnh báo, không ghi. Trạng thái chỉ đi tới |
| Dữ liệu Sheet chưa tin cậy? | **Đạt, trừ SL-T109-1 → -3.** Dòng qua `parse_sheet` / `PlanRow` (T-100); mã lạ ở cột Mã bài WordPress làm dòng không nối; một bài nối nhiều dòng, Mã bài trùng, dòng chưa có mã → chỉ cảnh báo. Lúc ghi so Mã bài WordPress, Trạng thái, Ngày đăng của dòng vừa đọc với bản đã xem: khác → không ghi |
| Câu báo cố định? | **Đạt.** Lý do, cảnh báo, xung đột chỉ chứa Mã bài chuẩn hóa, mã bài WordPress (số), số dòng, nhãn trạng thái chuẩn, giờ do app định dạng (`_notice`, `_compare`). Lỗi Google là `str(SheetsError)` (câu cố định T-097). Test gài chuỗi mồi vào ô và lời Google |

## Đối chiếu điều kiện

| Điều kiện | Đạt? | Bằng chứng |
|---|---|---|
| **LC-T094-1** Test không gọi Google, WordPress thật | **Đạt** | Sheet giả `FakePlanSheet` qua `SheetsClient` thật, trạng thái website dựng tay (`PostState`); bộ chặn mạng không đổi |
| **LC-T094-2** | **Đạt** | Mục trên |
| **LC-T094-3** (phần dữ liệu) | **Đạt** | `WebUpdate`, `WebNotice` chỉ mang nhãn, số, giờ của code; hiện chữ thuần là việc của lượt nối nút |
| **LC-T094-28** | **Đạt, trừ SL-T109-1** | Mục trên; chỉ 3 ô, `RAW`, so từng ô với bản đã xem, không xóa, không thêm |
| LC-T100-1 (Sheet đầy) | **Đạt** | Dòng không thấy trên Sheet đầy → `WebConflict` câu `CONFLICT_FULL`; không thêm dòng |
| LC-T100-3, SL-T100-4 (đúng Sheet) | **Đạt** | `_connected_hash` như trên |
| LC-T101-1 (bảng tải về CSV) | **Đạt cho lõi** | Mọi giá trị lõi trả lên giao diện là nhãn, số, giờ của code. Lượt nối nút vẫn phải đưa ô chữ qua `safe_text` như các bảng khác (điều kiện 1 biên bản T-101) |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` (`PYTHONUTF8=1`) trên 5 file đổi, bản vá nhánh, kèm file mồi tiếng Việt: mồi bắt 2/2, file thật 0 mục. Lịch sử `eef13b5..09870bd`: 0 dạng khóa thật |
| S2 | Đạt | LC-T094-2 |
| S3 | Không áp dụng | Không biến `.env` mới |
| W1–W4 | Không áp dụng | Lõi không gọi WordPress (nhận kết quả `post_statuses` từ nơi gọi) |
| A1–A3 | Không áp dụng | Không AI |
| U1–U3 | Không áp dụng | Chưa nối giao diện (điều kiện 1) |
| F1–F3 | Không áp dụng | Không đọc, ghi file |
| D1, D2 | Đạt | `pyproject.toml`, `uv.lock`, `.gitignore` không đổi |
| D3 | Đạt | LC-T094-1 |

## Kết quả công cụ quét

Máy chủ dự án, Windows 11, Python 3.12.15, worktree `wt-T-109` tại `09870bd`; máy đang chạy toàn bộ test của Chỉ Huy.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| detect-secrets 1.5.0 | **Đặt `PYTHONUTF8=1`**, `--all-files` trên bản sao 5 file đổi, bản vá nhánh và **file mồi tiếng Việt**: mồi bắt **2/2**; file thật 0 mục | Có. Đã xóa file mồi |
| bandit 1.9.4 | `PYTHONUTF8=1`, `seo_app/plan/website.py` (531 dòng): không có mục nào | Có |
| pip-audit | Không chạy: `uv.lock` không đổi | — |
| Soát lịch sử git | `git log -p eef13b5..09870bd`: 0 dạng khóa thật | Có |
| ruff, pytest | Trên đầu nhánh `09870bd`: `ruff check .` sạch. 10 file (`test_t109_website_status.py`, `test_soi_loi_t109.py`, `test_plan_sync.py`, `test_soi_loi_t100.py`, `test_la_chan_t100.py`, `test_t101_plan_page.py`, `test_la_chan_t101.py`, `test_google_sheets.py`, `test_wordpress_release.py`, `test_plan_model.py`): **982 passed, 8 xfailed** (6 ca SL-T109-1 → -3, 2 ca LC-T101-1 có sẵn), 0 failed, 2 phút 30 giây | Có |
| Thử gộp | `origin/main` `a416e74` + `09870bd`: `git merge-tree --write-tree` **không xung đột** (cây `b099c5c`). Từ gốc chung `eef13b5`, `main` chỉ đổi `CLAUDE.md` và tài liệu; `git diff` cho thấy `seo_app/`, `tests/`, `app/`, `config/`, `pyproject.toml`, `uv.lock` của cây gộp trùng nhánh, nên lượt test trên nhánh (dòng trên) chính là lượt test của cây gộp | Có |

## Quan sát (không tính là lỗi)

1. **Lần kiểm không có hạn (G4 của Soi Lỗi):** kiểm lúc bài còn hẹn giờ, sau đó bài bị chuyển về nháp trong trang quản trị, rồi mới bấm ghi → Sheet ghi «Đã hẹn giờ» theo dữ liệu cũ (lần sau chỉ cảnh báo, vì không lùi). Không ghi sai Sheet khác hay sai dòng, chỉ cũ. Điều kiện 1 (c).
2. **`states` sai kiểu (G2):** truyền dict có giá trị là tuple (như `S.plan_web` của T-101) thì mọi bài thành «Không thấy». Không ghi gì sai (chỉ cảnh báo thừa), nhưng dễ nối nhầm. Điều kiện 1 (b).
3. Khe «hai máy ghi cùng một ô trong 1–2 giây» và khe «dòng dời chỗ giữa đọc lại và lệnh ghi» của T-100 vẫn áp dụng (T-094 Ghi nhận 2; Quan sát 1 biên bản T-100). Ở đây chỉ 3 ô trạng thái, ngày.

## Báo nhầm đã loại

Không có: detect-secrets, bandit không báo mục nào ở file thật.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

Không điều kiện nào bắt buộc trước khi gộp T-109 vào `main`.

| # | Điều kiện | Phiếu nhận | Hạn |
|---|---|---|---|
| 0 | **SL-T109-1 → -3** sửa (cách ở trên), gỡ 6 `xfail` khi XPASS (R5); sửa tận gốc ở `sync.py` thì chạy test mọi nơi gọi | Thợ Máy (lượt sửa T-109) | Trước khi nối nút |
| 1 | **Lượt nối nút «Cập nhật trạng thái từ website»** (T-101 lượt sau hay T-102): (a) chỉ chạy khi bấm: một nút **đọc** (`post_statuses` rồi `check_website`), một nút **ghi** riêng (`apply_website_changes` với các thay đổi người dùng tick, không tick sẵn hàng loạt mà không xem); (b) truyền **đúng** kết quả `post_statuses` (`dict[int, PostState]`) và đúng danh sách mã đã hỏi, `sheet_id=settings.google_sheet_id`, `now=settings.now()`, dùng `website.LATE_AFTER` / cảnh báo «Lỡ lịch» của lõi (G1, G2); (c) kiểm lại website ngay trước khi ghi, hay từ chối lần kiểm cũ hơn vài phút (G4); (d) client Google tạo mới mỗi lần bấm, không giữ trong phiên; (e) hiện lý do, cảnh báo, xung đột bằng chữ thuần, bảng qua `safe_text` (LC-T094-3, LC-T101-1); (f) bắt `SheetsError`, `SheetPlanError`, `ValueError`, `WordPressError` thành câu cố định | Họa Sĩ (T-101 lượt sau / T-102) | Khi nối nút |
| 2 | Kiểm lại biên bản này bằng Claude Fable sau 01/11 | Chỉ Huy | Sau 01/11 |

3 lỗi Thấp đều có lượt sửa, không cần chủ dự án chấp nhận rủi ro; không thêm dòng vào sổ rủi ro (`security.md` mục 6).

## Xem lại lượt 2

| Mục | Nội dung |
|---|---|
| Phạm vi | Thợ Máy `82464d4`, `088b1e1`: `seo_app/plan/sync.py` (+18/−7: `_key_of`, `_post_id_of`, `_status_of` đọc ô qua `_reader_text` mới), `seo_app/plan/website.py` (+80/−11), test; gỡ 3 dấu `xfail` SL-T109. Soi Lỗi `635e95f` (ĐẠT, 0 lỗi mới, thêm 53 ca) |
| Ngày | 2026-10-31 (08:20–08:57 +07, giờ máy) |
| **Kết luận lượt 2** | **ĐẠT**: SL-T109-1, -2, -3 **đóng thật**. Đổi ba hàm dùng chung trong `sync.py` **không** mở lối ghi nhầm hay ghi rộng nào ở T-100, T-101, T-102: các hàm nay đọc ô đúng như bộ đọc bảng, nên chỉ làm khớp hơn, và nhận ra dòng trùng Mã bài nhiều hơn (dừng ghi). Lá Chắn **0 lỗi mới**. Giới hạn 2.000 ký tự **chấp nhận được** (có câu báo). G7, G8 **không cần làm trước khi gộp**. Gộp `main` được: với `main` trên máy `3cdd096` (có T-102) không xung đột; 18 file test T-100, T-101, T-102, T-109 qua trên cây gộp (1 ca hỏng oan vì quá giờ khi máy bận, chạy lại qua) |

### Tóm tắt (cho chủ dự án)

Ba lỗi nhỏ lượt trước đã sửa tận gốc: phần mềm nay đọc ô Mã bài, Mã bài WordPress, Trạng thái **giống hệt** bảng anh/chị thấy, nên không còn trường hợp xem một dòng mà ghi vào dòng khác. Ô gõ lạ chỉ có cảnh báo, không đề xuất. Một lần kiểm cũ hơn 5 phút thì phải kiểm lại mới ghi. Phần ghi trạng thái sau khi gửi bài (T-100, T-102) cũng được lợi: dòng trùng Mã bài nay luôn bị dừng. Còn một giới hạn đã biết, chỉ xảy ra khi ô bị gõ gần 2.000 dấu cách; khi đó phần mềm có hiện cảnh báo.

### SL-T109-1 → -3

| Mã | Kết quả | Bằng chứng |
|---|---|---|
| SL-T109-1 | **Đóng** | `_key_of` (`sync.py:1113`) đọc qua `_reader_text` (`:1123`: cắt đúng 2.000 ký tự như `parse._cell`, rồi mới làm sạch), nên `key_rows` và bộ đọc thấy cùng Mã bài. Thêm hai lớp chặn trong `website.py`: lúc kiểm, dòng mà `key_rows` không trỏ đúng thì chỉ cảnh báo `UNSURE_ROW` (`:275`); lúc ghi, đòi `fresh.find(key).number` trùng dòng tìm được, như `open_row` (`:495`). 3 ca `xfail` cũ qua, Soi Lỗi thêm ca biến thể |
| SL-T109-2 | **Đóng** | `_post_id_of` (`sync.py:892`) đọc như bộ đọc; `_post_counts` nhận ra một bài nối hai dòng → `SHARED_POST`, không đề xuất |
| SL-T109-3 | **Đóng** | Trạng thái, Ngày đăng thực tế đọc bằng đúng hàm lúc ghi (`_status_of`, `_moment_of`); ô không đọc được → cảnh báo `ODD_CELL`, không đề xuất |

### Đổi hàm dùng chung: ảnh hưởng tới T-100, T-101, T-102

Nơi gọi `_key_of`, `_post_id_of`, `_status_of`: `parse_sheet` (`key_rows`), `apply_proposals` (`_fresh_row`), `write_status`, `open_row`, `_key_present`, `website.py`.
- **Trước:** cắt 30 (hay 100) ký tự rồi mới làm sạch, nên ô có ký tự trắng, vô hình ở đầu bị đọc khác bộ đọc.
- **Nay:** đọc khớp bộ đọc. Hệ quả:
  - (1) Ô Mã bài có ký tự trắng đầu ô nay vào `key_rows`: dòng trùng Mã bài (một dòng gõ thẳng, một dòng có dấu cách) nay bị nhận là **trùng**, nên `apply_proposals`, `write_status`, `open_row` đều **dừng** (trước đây có thể ghi vào một trong hai). Hướng an toàn hơn.
  - (2) `write_status` tìm được dòng có Mã bài gõ sau nhiều dấu cách. Đó đúng là dòng bộ đọc nhận và người dùng đã mở bài từ đó (`open_row`), nên ghi vào đó là đúng.
  - (3) `_status_of` đọc 2.000 ký tự thay vì 100: chữ dài hơn mới thành «không đọc được». Không đổi đường ghi.
  - (4) Không hàm nào ghi thêm ô hay dòng mới.
- **Kiểm:** test T-100, T-101, T-102, T-109 trên cây gộp với `main` có T-102 (dưới) đều qua. `parse_sheet` đọc tối đa 1.001 × 26 ô, mỗi ô ≤ 2.000 ký tự, làm sạch tuyến tính.

### Giới hạn 2.000 ký tự: chấp nhận được

Tự thử: ô Mã bài 1.996 dấu cách + «B-070» được đọc thành `B-007`; ô Mã bài WordPress 1.996 dấu cách + «12345» được đọc thành `1234` (một bài khác).

Chấp nhận, vì:
1. Bộ đọc và đường ghi thấy **cùng** giá trị đó: bảng trên app hiện `B-007`, `1234`, nên thay đổi đề xuất khớp với cái người dùng thấy.
2. Trang có câu báo cố định «Ô «Mã bài» dài quá 2.000 ký tự, đã cắt (dòng …)».
3. Trùng với một dòng `B-007` thật hay một dòng nối bài 1234 thật thì bị nhận là trùng, dừng ghi.
4. Gõ được gần 2.000 dấu cách vào ô thì đã sửa được ô đó thành bất kỳ mã nào; không ai có thêm quyền.

Cách làm chắc hơn, nếu sau này muốn (không bắt buộc): ô Mã bài, Mã bài WordPress dài quá giới hạn thì coi là **không đọc được** (như ô sai dạng), thay vì cắt rồi đọc. Phải sửa ở cả bộ đọc `parse._cell` / `parse._row` và `_reader_text` để hai bên vẫn khớp.

### G7, G8 của Soi Lỗi

| Góp ý | Ý kiến |
|---|---|
| G7 (dòng «Bỏ» có ô ngày gõ lạ: mất câu «Bỏ mà bài vẫn còn», thay bằng câu «ô không đọc được») | Không phải bảo mật; vẫn có cảnh báo, không ghi gì. Không cần trước khi gộp |
| G8 (`MSG_STALE` viết cứng «quá 5 phút», tách khỏi `CHECK_MAX_AGE`) | Không phải bảo mật (chỉ lệch chữ nếu sau này đổi hằng). Không cần trước khi gộp; nên dựng câu từ hằng khi tiện |

### Gỡ `xfail` (R5)

Đúng R5. `git diff a40a107 088b1e1 -- tests/test_soi_loi_t109.py`: xóa 3 dấu `xfail` (12 dòng). Một dòng `assert` đổi `range(401, 407)` → `range(401, 408)` (ca bài 407 «giờ lạ», G6), có ghi chú Chỉ Huy duyệt 31/10 00:45.

### Thử gộp

`main` trên máy `3cdd096` (có T-102: `app/views/plan.py`, `home.py`, `write.py`) + `635e95f`: `git merge-tree --write-tree` **không xung đột** (cây `ce09950`); từ gốc chung `eef13b5`, hai bên không sửa chung file nào. T-102 không đổi `sync.py`, nhưng trang Kế hoạch, Bài viết, Soạn bài của T-101, T-102 gọi các hàm vừa đổi, nên tôi chạy test của cả hai phiếu. Commit tạm `9d5804b` trong worktree riêng (`git commit-tree`, không nhánh, đã gỡ).

Trên cây gộp: `ruff check .` sạch. 18 file (T-109: 2; T-100: `test_plan_sync`, `test_soi_loi_t100`, `test_la_chan_t100`, `test_t100_drafts_plan`; T-101: `test_t101_plan_page`, `test_t101_home_page`, `test_la_chan_t101`, `test_soi_loi_t101`; T-102: `test_t102_publish`, `test_soi_loi_t102`, `test_la_chan_t102`, `test_t102_formula_cells`; `test_plan_model`, `test_plan_parse`, `test_google_sheets`, `test_app_pages`): **1.044 passed, 4 xfailed** (lỗi còn mở có sẵn của T-102: LC-T102-1, 3 ca Soi Lỗi T-102), **1 failed**, 26 phút 56 giây. Ca hỏng là `test_t101_plan_page.py::test_list_reads_sheet_and_shows_plain_text`, vì AppTest chạy trang quá 30 giây (`AppTest script run timed out after 30(s)`) khi máy đang chạy toàn bộ test của Chỉ Huy. Chạy lại trên cùng cây gộp: ca đó **qua** (20 giây), cả file **30 passed**. Hỏng oan vì máy bận, không phải lỗi.

### Điều kiện còn lại cho lượt nối nút (phiếu T-113)

Điều kiện 1 lượt 1 vẫn giữ. Riêng (c) nay lõi đã làm (`CHECK_MAX_AGE` 5 phút, giờ máy lùi, `website.py:441`, chạy trước khi đọc, ghi Sheet), giao diện chỉ phải xử lý lỗi đó. Cụ thể:
- (a) chỉ chạy khi bấm: một nút **đọc** (`post_statuses` rồi `check_website`), một nút **ghi** riêng với các thay đổi người dùng tick;
- (b) truyền **thẳng** kết quả `post_statuses` (`dict[int, PostState]`), đúng danh sách mã đã hỏi, `sheet_id=settings.google_sheet_id`, `now=settings.now()`, dùng `website.LATE_AFTER`. **Không** dùng `S.plan_web` (bộ đôi chữ) của cột «Trên website» T-101 (G2);
- (c) bắt `SheetPlanError` câu `MSG_STALE`, `MSG_OTHER_SHEET`, `MSG_NO_COLUMNS` và hiện bằng chữ thuần, mời bấm kiểm lại; không giữ `WebCheck` qua lần tải trang sau đó lâu;
- (d) client Google, WordPress tạo mới mỗi lần bấm, không giữ trong phiên;
- (e) lý do, cảnh báo (cả `ODD_CELL`, `UNSURE_ROW`), xung đột hiện bằng chữ thuần; bảng qua `safe_text` (LC-T101-1);
- (f) bắt `SheetsError`, `SheetPlanError`, `ValueError`, `WordPressError` thành câu cố định.

Kiểm lại biên bản bằng Claude Fable sau 01/11 (điều kiện 2 lượt 1) vẫn giữ.

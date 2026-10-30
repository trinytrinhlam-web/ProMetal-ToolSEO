# Báo cáo T-109 · Đưa trạng thái bài trên website về Google Sheets · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-109](../tickets/T-109-dong-bo-trang-thai-website-ve-sheet.md), Thợ Máy đầu nhánh `b511036` (gốc `main` `eef13b5`, có T-100, T-101); thiết kế T-094 mục 1.7, 2.5 |
| Ngày nộp | 2026-10-30 (23:10 +07:00) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **3 Thấp** (SL-T109-1 → -3, đều cần ô Sheet gõ lạ: không mất dữ liệu, không lùi trạng thái, không ghi ngoài 3 ô). Trạng thái chỉ đi tới, «Lỡ lịch», ghi khi Sheet đổi giữa chừng, hai tab, lỗi giữa lô, ăn khớp T-100 / T-102: **không lỗi**. Không lùi T-097, T-098, T-100, T-101, T-103; gộp thử `origin/main` `a416e74` sạch. Điều kiện: Chỉ Huy chọn sửa 3 lỗi Thấp ngay (lượt 2 ngắn, chỉ trong `website.py`) hay ghi nhận để sau; không chặn Lá Chắn |

## Tóm tắt (cho chủ dự án)

- **Nút «Cập nhật trạng thái từ website» (phần lõi) làm đúng việc chính.** Bài đã lên thì dòng thành «Đã đăng», bài anh/chị tự hẹn giờ trong trang quản trị thì thành «Đã hẹn giờ» kèm giờ, bài mới có nháp thì thành «Đã gửi nháp». Phần mềm **không bao giờ lùi** trạng thái: tôi thử đủ 6 trạng thái trên Sheet × 5 trạng thái trên website, không đề xuất nào đi lùi; dòng «Bỏ», bài riêng tư, bài bị xóa, bài về nháp chỉ hiện cảnh báo.
- **«Lỡ lịch»** hiện đúng khi bài hẹn giờ quá giờ **hơn 15 phút** mà chưa lên (đúng 15 phút chưa báo, 15 phút và một phần triệu giây thì báo), giờ trong câu là giờ Việt Nam, máy đặt múi giờ nào cũng như nhau.
- **Ghi lên Sheet an toàn:** chỉ 3 ô (Trạng thái, Ngày đăng thực tế, Cập nhật lúc), ở dạng giữ nguyên, không thành công thức. Tôi thử chèn dòng, xếp lại dòng, đổi chỗ cột, hai tab cùng bấm ghi, mất mạng ở lệnh ghi thứ hai, máy khác vừa sửa dòng, bài gửi từ app ghi trạng thái xen giữa: không lần nào ghi nhầm dòng, đè ô người khác vừa sửa, hay thêm/xóa dòng.
- **Còn 3 lỗi nhỏ**, chỉ xảy ra khi ô trên Sheet gõ lạ: Mã bài hay Mã bài WordPress có **30 dấu cách** (hoặc ký tự vô hình) ở đầu ô, ô Trạng thái gõ chữ tự do («Xong rồi»), ô Ngày đăng thực tế gõ chữ («hôm qua»). Khi đó phần mềm có thể ghi vào một dòng trùng Mã bài, hay đề xuất một thay đổi mà bấm ghi lần nào cũng bị từ chối. Không mất dữ liệu, không lùi trạng thái.
- **Không có gì phải anh/chị quyết.**

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t109.py` | Mới: **52 ca: 46 qua, 6 `xfail(strict=True)`** của 3 lỗi mới. Không gọi Google, WordPress thật (Sheet giả có trạng thái trên `FakeGoogle`, đi qua `SheetsClient` thật) |
| `docs/team/reports/T-109-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, test của Thợ Máy, phiếu hay file khác.

## Kiểm từng mục

### 1. Dữ liệu website và Sheet là dữ liệu chưa tin cậy

**Website (`post_statuses`):**

| Tình huống | Kết quả |
|---|---|
| `date_gmt` chữ số toàn chiều rộng («２０２６-…»), có surrogate lẻ, 29/02/2026, giây 60, `0000-00-00T00:00:00`, 100.000 chữ số | Không lỗi, không treo (< 2 giây); đổi trạng thái nhưng **không** ghi ngày, cảnh báo «giờ đăng … không đọc được»; không «Lỡ lịch» |
| `date_gmt` là `None` | Coi như không có ngày, đổi trạng thái không kèm ngày |
| Trạng thái `publish` + U+202E, chuỗi giả dạng (lớp con của `str`), `id` là chữ «410» | Coi như không thấy bài (cảnh báo «Không thấy bài»), không đề xuất |
| Biên năm theo **giờ Việt Nam**: `2035-12-31T16:59:59` (23:59 ngày 31/12/2035), `2019-12-31T17:00:00` (00:00 ngày 01/01/2020) | Nhận, ghi «2035-12-31 23:59+07:00», «2020-01-01 00:00+07:00»; đọc lại từ Sheet được, kiểm lại không còn đề xuất |
| `2035-12-31T17:00:00` (sang 2036 giờ Việt Nam), `2019-12-31T16:59:59` | Ngoài khoảng năm kế hoạch: đổi trạng thái, không ghi ngày, cảnh báo |

**Sheet:**

| Tình huống | Kết quả |
|---|---|
| Mọi ô chữ (từ khóa, từ khóa phụ, tiêu đề, ghi chú, ý định, slug) có U+202E, `=IMPORTXML(1)`, `[x](javascript:1)`, `<b>`, chuỗi mồi; từ khóa 5.000 ký tự, ghi chú 50.000 ký tự | Mọi lý do, cảnh báo (cả 10 loại), câu kết quả ghi, lý do xung đột: **không** chép chữ ô (LC-T094-2); Mã bài trong câu là mã đã chuẩn hóa («B-001», không phải «b-1») |
| Mã bài gõ khác dạng giữa lúc kiểm và lúc ghi («b-70» → « B-070 », «KV-0012» → «kv-12») | Tìm đúng dòng, ghi đúng dòng, ô Mã bài giữ nguyên chữ người dùng gõ |
| Hai dòng cùng Mã bài gõ khác dạng («b-70», «B-0070», 20 dấu cách + «B-070», U+200B + «B-070») | Cảnh báo «Mã bài … có ở nhiều dòng», không ghi |
| Hai dòng cùng bài WordPress gõ khác dạng («0170», « 170 », số `170.0`, U+200B + «170», «１７０») | Cảnh báo «một bài ở nhiều dòng», không đề xuất |
| Ô Trạng thái, Ngày đăng thực tế gõ dạng khác đọc được («da dang bai», «ĐÃ HẸN GIỜ», «03/11/2026 08:00», ô ngày giờ kiểu số của Sheets, ISO có «Z») | Đề xuất ghi được ngay, không xung đột; kiểm lại không còn đề xuất |
| Mã bài / Mã bài WordPress có **30 ký tự trắng hay vô hình ở đầu ô** | **Lỗi SL-T109-1, SL-T109-2** (dưới) |
| Ô Trạng thái / Ngày đăng thực tế **không đọc được** | **Lỗi SL-T109-3** (dưới) |

### 2. Chỉ đi tới; không đề xuất cho dòng không nối được; «Lỡ lịch»

| Tình huống | Kết quả |
|---|---|
| 60 dòng: 6 trạng thái Sheet × 5 trạng thái website (`draft`, `pending`, `future`, `publish`, `private`), có và không có «Ngày đăng thực tế» | Không đề xuất nào lùi; không đề xuất cho dòng «Bỏ», bài riêng tư; đề xuất «chỉ đổi ngày» khi và chỉ khi trạng thái giữ nguyên. Ghi xong kiểm lại: **0** đề xuất; mọi ô ghi thuộc 3 cột app, là chữ không mở đầu bằng `=`, `+`, `-`, `@`, tab, CR; ô ghi chú giữ nguyên; không thêm, không xóa dòng |
| Áp dụng lần kiểm **cũ** («→ Đã hẹn giờ») sau lần kiểm mới đã ghi «Đã đăng» | Xung đột, dòng giữ «Đã đăng», không lệnh ghi thứ hai |
| «Lỡ lịch»: quá giờ hẹn 14 phút 59 giây / đúng 15 phút / 15 phút + 1 micro giây / 15 phút 1 giây / còn 30 phút nữa; `now` ở múi giờ Việt Nam, UTC, New York | Chỉ báo khi quá **hơn** 15 phút; kết quả như nhau ở cả 3 múi giờ; câu báo «hẹn giờ lúc 03/11/2026 09:00» (giờ Việt Nam); không ghi Sheet |
| Đồng hồ máy lệch | «Lỡ lịch» tính theo đồng hồ máy (như cột «Trên website» của T-101): lệch thì báo sớm hay muộn. Chỉ là cảnh báo; ghi ở «Giới hạn đã biết» |

Dòng không nối được (ô Mã bài WordPress lạ, bài không được hỏi, bài không có trong kết quả website): không có đề xuất (test của Thợ Máy và test mục 1 ở trên).

### 3. Ghi: Sheet đổi giữa chừng, hai tab, «chưa rõ», lỗi giữa lô

| Tình huống | Kết quả |
|---|---|
| Sau lúc kiểm: chèn một dòng mới ở đầu, đảo ngược thứ tự 3 dòng | Ghi đúng 3 dòng theo Mã bài (số dòng mới), dòng mới chèn không bị chạm, không thêm dòng |
| Sau lúc kiểm: đổi chỗ cột «Trạng thái» với «Ghi chú của thợ» | Ghi theo tên cột của bản đọc lại; ô ghi chú không bị đè |
| Hai tab cùng giữ một lần kiểm, lần lượt bấm ghi | Tab đầu ghi 2 dòng, tab sau «2 dòng đã đúng sẵn», chỉ **một** lệnh ghi |
| Hai tab: tab sau **đọc trước** khi tab đầu ghi (khe hở thiết kế 2.5) | Hai lệnh ghi đúng các giá trị đó: Sheet cuối như chỉ ghi một lần, không chạm cột khác |
| 4 dòng, mỗi lệnh một dòng; **lệnh thứ hai** đứt mạng (Google chưa ghi) | Dòng 1 «đã cập nhật», dòng 2 «chưa rõ», dòng 3, 4 «chưa ghi» (không gửi thêm lệnh nào); câu báo đủ ba phần; kiểm lại đề xuất đúng dòng 2, 3, 4 |
| `unsure` (Google đã ghi), lỗi 403, lỗi đọc lại, thiếu cột, Sheet khác, thay đổi không thuộc lần kiểm | Đúng như báo cáo Thợ Máy (test của Thợ Máy, chạy lại qua) |

### 4. Ăn khớp với T-100 (`record_status`, mã băm) và T-102

| Tình huống | Kết quả |
|---|---|
| Mã băm Sheet | `WebCheck.sheet_hash` = `plan_ref(...).sheet_hash` = `sheet_hash(SHEET_ID)`: cùng một cách băm với kho nháp, cache |
| Lần kiểm website (bài hẹn 05/11) ghi trước; việc ghi còn nợ của app (gửi lại, hẹn 06/11) chạy sau | `write_status` thấy dòng đã «Đã hẹn giờ» → «đã đúng», không lùi, không ghi thêm; lần kiểm sau đề xuất sửa «Ngày đăng thực tế» theo website (06/11) |
| App ghi trạng thái sau khi gửi trước; lần kiểm website **cũ** ghi sau | Xung đột, giờ app vừa ghi giữ nguyên; sau đó app ghi «Đang viết» (mở lại bài) → «ở bước sau», không lùi |
| Ô ghi | Website chỉ ghi 3 ô, không bao giờ ghi «Mã bài WordPress» (ô đó chỉ app ghi sau khi gửi) |

Hằng «Lỡ lịch» 15 phút hiện ở 3 nơi (`app/views/plan.py`, `app/views/home.py`, `seo_app/plan/website.py`): cùng giá trị, cùng phép so «quá hơn». Xem góp ý G1.

### 5. Không lùi; gộp thử

- T-109 chỉ **thêm** `seo_app/plan/website.py`, test, báo cáo (đã đối chiếu `git diff eef13b5 b511036`): không sửa code cũ, không sửa test cũ.
- R5: 26 file chọn lọc (T-097, T-098, T-100, T-101, T-103, T-109, kế hoạch, Google Sheets, kho nháp): **2.111 qua, 3 bỏ qua, 8 xfail** (6 của báo cáo này, 2 có sẵn của Lá Chắn T-101 LC-T101-1); không tạo thư mục `data/`.
- Gộp thử với `origin/main` `a416e74` (worktree tạm, đã xóa): không xung đột (`main` chỉ thêm sổ sách: `git diff eef13b5 a416e74 -- seo_app app tests` rỗng); 11 file chọn lọc trên bản gộp: **1.210 qua, 6 xfail**.

## Lỗi mới

### SL-T109-1 · Thấp · Mã bài có 30 ký tự trắng đầu ô: kiểm không thấy trùng, ghi vào dòng trùng

- **Tái hiện** (`test_key_with_leading_blanks_never_writes_a_duplicate_row`): dòng 2 Mã bài «(30 dấu cách)B-070», dòng 3 «B-070», cả hai «Đã hẹn giờ», bài 170 (ô dòng 2 cũng có 30 dấu cách đầu). Bộ đọc nhận dòng 2 là B-070, **bỏ dòng 3** và báo «Mã bài trùng»; nhưng `SheetPlan.key_rows` (dựng bằng `sync._key_of`, cắt 30 ký tự **trước** khi làm sạch) chỉ thấy dòng 3, nên `duplicate_keys` rỗng. Kiểm đề xuất «B-070 (dòng 2) → Đã đăng»; ghi thì `_cells_for` lấy `key_rows["B-070"]` = dòng 3, so ô khớp, ghi 3 ô vào **dòng 3**.
- **Hậu quả:** ghi vào dòng mà bảng của app không hiện (bị bỏ vì trùng), trái LC-T094-28 / thiết kế 2.5 «Mã bài trùng → không ghi»; dòng 2 người dùng thấy vẫn «Đã hẹn giờ», lần sau ghi lại báo «đã đúng sẵn». Không mất dữ liệu (dòng 3 mang cùng bài, cùng trạng thái cũ).
- **Gợi ý sửa:** như `sync.open_row` đã làm: trong `_cells_for`, `fresh.find(update.key)` phải có và trùng số dòng với `key_rows` (khác thì xung đột «trùng»); lúc kiểm, dòng có `plan.key_rows.get(key) != (số dòng,)` thì cảnh báo, không đề xuất. Gốc ở `sync._key_of` / `_post_id_of` (cắt rồi mới làm sạch); sửa ở đó thì hợp hơn nhưng chạm T-100.

### SL-T109-2 · Thấp · Mã bài WordPress có 30 ký tự trắng đầu ô: một bài nối hai dòng vẫn được đề xuất

- **Tái hiện** (`test_post_on_two_rows_is_never_proposed_whatever_the_blanks`, 2 ca: dấu cách, U+200B): B-001 bài 170; B-002 ô Mã bài WordPress «(30 ký tự trắng)170». Bộ đọc nối **cả hai** dòng với bài 170; `_post_counts` đọc ô bằng `sync._post_id_of` (cắt 30 ký tự trước khi làm sạch) nên chỉ đếm một dòng. Kiểm đề xuất cho cả hai dòng; ghi được B-001 (B-002 xung đột).
- **Hậu quả:** trái quy tắc «một bài nối nhiều dòng: chỉ cảnh báo» của phiếu. Biến thể 29 dấu cách + «170»: `_post_id_of` đọc ra bài **1** (đếm nhầm sang bài khác, chỉ thêm cảnh báo thừa).
- **Gợi ý sửa:** `_post_counts` đếm theo **cùng** cách đọc với bộ đọc bảng (`parse._post_id` trên chữ đã làm sạch, giới hạn như `_cell`), hay đếm cả hai cách. Bản sửa nháp (worktree tạm) làm test này qua, không hỏng test nào khác.

### SL-T109-3 · Thấp · Ô Trạng thái / Ngày đăng thực tế không đọc được: đề xuất không bao giờ ghi được

- **Tái hiện** (`test_what_check_proposes_is_writable_while_sheet_is_unchanged`, 3 ca): ô Trạng thái «Xong rồi»; ô Ngày đăng thực tế «hôm qua» với dòng «Đã hẹn giờ» và «Đã đăng»; website `publish`. Bộ đọc coi ô không đọc được là trống («Chưa viết», không ngày) nên kiểm đề xuất «Chưa viết → Đã đăng» hay «sửa ngày»; lúc ghi, `_status_of` / `_moment_of` thấy ô «không đọc được» nên **luôn** xung đột với lý do «Dòng vừa bị sửa ở nơi khác («Trạng thái» / «Ngày đăng thực tế»)», dù Sheet không đổi. Kiểm lại: đề xuất y hệt, vòng lặp không ra.
- **Hậu quả:** đề xuất sai (bảng hiện «trước: Chưa viết» trong khi ô ghi «Xong rồi»), lý do xung đột sai, người dùng không biết phải sửa ô nào. Không ghi gì sai.
- **Gợi ý sửa:** lúc kiểm, đọc ô bằng đúng hàm lúc ghi (`_status_of`, `_moment_of` trên `sheet_row.cells`); không đọc được thì cảnh báo cố định («ô … dòng B-001 không đọc được») thay vì đề xuất. Test viết theo bất biến «Sheet không đổi thì không xung đột», không ép một cách sửa.

Đã thử bản sửa nháp cho cả 3 lỗi trong `website.py` (worktree tạm, đã xóa): 6 ca `xfail` thành XPASS, 114 ca còn lại của `test_soi_loi_t109.py` + `test_t109_website_status.py` vẫn qua.

## Góp ý (không xếp lỗi)

- **G1.** Khi nối nút vào trang Kế hoạch: dùng `website.LATE_AFTER` thay hai hằng riêng ở `plan.py`, `home.py`, và truyền `now=settings.now()` (như cột «Trên website») để nhãn và cảnh báo «Lỡ lịch» luôn khớp.
- **G2.** `check_website` nhận `states` sai kiểu (`None`, list, hay dict mà giá trị là tuple như `S.plan_web` của T-101 đang lưu `(status, date_gmt)`) thì im lặng coi **mọi** bài là «Không thấy… đã bị xóa». Dễ nối nhầm ở giao diện: nên truyền thẳng kết quả `post_statuses`, và hàm nên ném lỗi lập trình khi `states` không phải `Mapping`.
- **G3.** Dòng «Bỏ» mà bài đã xóa hay vào thùng rác: mỗi lần kiểm vẫn cảnh báo «Không thấy bài…». Có thể bỏ cảnh báo này cho dòng «Bỏ».
- **G4.** Lần kiểm không có hạn: kiểm lúc bài còn hẹn giờ, sau đó chủ dự án chuyển bài về nháp trong trang quản trị, rồi mới bấm ghi → Sheet «Đã hẹn giờ» (và không bao giờ tự lùi). Giao diện nên kiểm lại ngay trước khi ghi, hoặc từ chối `WebCheck.checked_at` quá vài phút.
- **G5.** Thiếu cột «Trạng thái» (bị đổi tên): kiểm đề xuất «Chưa viết → …» cho mọi dòng nối bài, ghi mới báo thiếu cột (câu rõ). Có thể báo ngay lúc kiểm (`plan.missing`).
- **G6.** «Đăng ngay» của T-102 ghi «Ngày đăng thực tế» bằng giờ máy lúc nhận trả lời; nút này so tới phút với `date_gmt` của WordPress nên đôi khi đề xuất sửa lệch một phút (đúng, nhưng thừa). `post_statuses` (T-099) đổi `date_gmt` sai khuôn thành chuỗi rỗng nên bài hẹn giờ có ngày hỏng hiện như «không có ngày», không có cảnh báo «giờ không đọc được»; có thể coi `future` / `publish` rỗng ngày là ngày lạ.

## Giới hạn đã biết (không xếp lỗi)

- Khe hở thiết kế 2.5: hai máy ghi **khác** giá trị vào cùng ô trong 1–2 giây giữa đọc lại và ghi thì bản sau thắng (không có lệnh ghi có điều kiện). Cùng một lần kiểm thì vô hại (test hai tab đọc trước).
- Chỉ đọc 1.000 dòng đầu (LC-T100-1): dòng sau đó không được kiểm, bài nối dòng sau 1.000 không được đếm vào «một bài nhiều dòng».
- Ô «Trạng thái» là **công thức thật** (`=IF(…)`): Sheets trả giá trị đã tính, app ghi `RAW` nên công thức bị thay bằng chữ (như ghi trạng thái của T-100).
- «Lỡ lịch» tính theo đồng hồ máy.

## Lệnh đã chạy

```
uv run pytest tests/test_soi_loi_t109.py tests/test_t109_website_status.py -q            # 114 qua, 6 xfail
uv run pytest <26 file chọn lọc> -q                                                      # 2.111 qua, 3 bỏ qua, 8 xfail
uv run ruff check tests/test_soi_loi_t109.py seo_app/plan/website.py tests/test_t109_website_status.py
uv run ruff format --check tests/test_soi_loi_t109.py
PYTHONUTF8=1 uvx detect-secrets scan --all-files <bản chép 3 file + file mồi>                # chỉ file mồi bị bắt
```

Quét ký tự ẩn (Cc, Cf, Cn, Co, Cs) trên `website.py`, 2 file test, báo cáo Thợ Máy: sạch. Không gọi Google, WordPress thật; không chạy cloud; không mở app.

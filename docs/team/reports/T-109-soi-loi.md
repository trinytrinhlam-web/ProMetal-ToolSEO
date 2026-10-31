# Báo cáo T-109 · Đưa trạng thái bài trên website về Google Sheets · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-109](../tickets/T-109-dong-bo-trang-thai-website-ve-sheet.md), Thợ Máy đầu nhánh `b511036` (gốc `main` `eef13b5`, có T-100, T-101); thiết kế T-094 mục 1.7, 2.5 |
| Ngày nộp | 2026-10-30 (23:10 +07:00) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **3 Thấp** (SL-T109-1 → -3, đều cần ô Sheet gõ lạ: không mất dữ liệu, không lùi trạng thái, không ghi ngoài 3 ô). Trạng thái chỉ đi tới, «Lỡ lịch», ghi khi Sheet đổi giữa chừng, hai tab, lỗi giữa lô, ăn khớp T-100 / T-102: **không lỗi**. Không lùi T-097, T-098, T-100, T-101, T-103; gộp thử `origin/main` `a416e74` sạch. Điều kiện: Chỉ Huy chọn sửa 3 lỗi Thấp ngay (lượt 2 ngắn, chỉ trong `website.py`) hay ghi nhận để sau; không chặn Lá Chắn |
| **Kết luận lượt 2** (đầu nhánh `088b1e1`, 2026-10-31) | **ĐẠT**: SL-T109-1 → -3 **đóng** (6 ca qua, thân test không đổi; 23 ký tự trắng / vô hình × 6 độ dài × 3 vị trí: hai cách đọc ô khớp nhau, bản lượt 1 lệch 231 / 297); đổi `_key_of`, `_post_id_of`, `_status_of` trong `sync.py` không làm hỏng nơi gọi nào (T-100, T-101, T-102 trên bản gộp `main` `3cdd096`); G3 → G6 đúng biên; R5 đúng phạm vi duyệt. **0 lỗi mới**, 2 góp ý câu báo (G7, G8). Chi tiết: mục [«Lượt 2»](#lượt-2-2026-10-31-0759-0700--soát-lượt-sửa-của-thợ-máy-088b1e1) |

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

## Lượt 2 (2026-10-31 07:59 +07:00) · soát lượt sửa của Thợ Máy `088b1e1`

Phạm vi theo tin Chỉ Huy B (31/10 01:10, nhắc lại 07:40): 6 ca của SL-T109-1 → -3 qua thật và biến thể gần; đổi hàm dùng chung `_key_of`, `_post_id_of`, `_status_of` trong `sync.py` (mọi nơi gọi, test ghim hành vi cũ); G4, G6, R5; gộp thử với `main` cục bộ `3cdd096` (đã có T-102).

### Tóm tắt (cho chủ dự án)

- **Ba lỗi nhỏ lượt trước đã sửa tận gốc.** Phần mềm nay đọc lại một ô Google Sheet **giống hệt** bảng anh/chị đang xem. Tôi thử 23 loại ký tự trắng hay vô hình (dấu cách cứng, ký tự rộng 0, dấu đảo chiều chữ, ký tự thẻ…) ở đầu, cuối và giữa ô, với 1 tới 1.500 ký tự: không còn chỗ nào hai cách đọc khác nhau (bản trước lệch ở 231 trên 297 trường hợp).
- **Ô gõ chữ tự do** («Xong rồi», «hôm qua») nay chỉ được nhắc «ô … không đọc được, sửa ô đó», không còn đề xuất rồi bị từ chối mãi.
- Sửa này cũng giúp nút **«Viết bài»** và **«Áp dụng»** đề xuất kế hoạch: dòng có Mã bài gõ sau nhiều dấu cách nay mở được, sửa được; hai dòng trùng Mã bài (một dòng gõ lệch) thì mọi nút đều dừng, không ghi nhầm dòng.
- **Bốn góp ý lượt trước đã làm đúng:** lần kiểm cũ quá 5 phút phải kiểm lại (đúng tới phần triệu giây); dòng «Bỏ» mà bài đã xóa không còn nhắc; thiếu cột báo ngay khi kiểm; giờ đăng lệch website không quá 2 phút coi như đúng, lệch hơn thì sửa một lần rồi thôi.
- **Bước Xuất bản (T-102) vừa lên `main` vẫn chạy đúng** khi gộp với phiếu này: test của T-102 (ghi «Đang viết», «Đã gửi nháp» sau khi gửi) qua hết.
- **Không có lỗi mới.** Hai góp ý nhỏ về câu báo.
- Ghi nhận ngoài phiếu này: trên `main` hiện có **một bài kiểm tra cũ của T-103 báo đỏ** sau khi gộp T-102. Bài kiểm tra đó dò chữ quá rộng nên bắt nhầm, phần mềm không hỏng; Chỉ Huy sẽ thấy khi chạy toàn bộ test.
- **Không có gì phải anh/chị quyết.**

### Kết luận lượt 2

**ĐẠT**: SL-T109-1, -2, -3 **đóng**; G3, G4, G5, G6 đúng biên; đổi hàm dùng chung không làm hỏng nơi gọi nào (T-100, T-101, T-102); R5 đúng phạm vi Chỉ Huy duyệt; gộp thử `3cdd096` sạch. **0 lỗi mới**, 2 góp ý (G7, G8), 1 giới hạn đã biết (ô quá 2.000 ký tự).

### Đã thay đổi (lượt 2)

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t109.py` | Thêm **53 ca lượt 2** (mục cuối file). Tổng 105 ca, **105 qua**. Không sửa ca cũ |
| `docs/team/reports/T-109-soi-loi.md` | Mục này, dòng kết luận lượt 2 ở bảng đầu |

### 1. SL-T109-1 → -3 qua thật; biến thể gần

- **Test của tôi chỉ đổi đúng phần được duyệt** (`git diff 09870bd 088b1e1 -- tests/test_soi_loi_t109.py`): gỡ 3 dấu `xfail` (chỉ dòng dấu), đổi một kỳ vọng ở `test_odd_website_values_never_crash_late_or_leak` (bài 407 nay có «giờ lạ», Chỉ Huy duyệt 31/10 00:45). Thân 6 ca giữ nguyên, nay qua.
- **Bộ test lượt 2 bắt được bản cũ:** chạy 53 ca mới trên mã lượt 1 (`09870bd`, worktree tạm): **41 hỏng** (đúng các chỗ đã sửa), 12 qua (các ca giữ hành vi không đổi). Trên `088b1e1`: 53 qua.

| Biến thể | Kết quả |
|---|---|
| 23 ký tự: dấu cách, NBSP U+00A0, U+202F, U+3000, tab, xuống dòng, U+0085, U+2028, U+200B, U+200C, U+200D, U+2060, BOM U+FEFF, gạch mềm U+00AD, U+180E, U+200E, U+202E, U+2066, U+3164, U+034F, U+FE0F, ký tự thẻ U+E0020, ký tự riêng U+E000; 1, 29, 30, 31, 40, 1.500 ký tự; ở **đầu, cuối, giữa** các ô Mã bài, Mã bài WordPress, Trạng thái, Ngày đăng thực tế | Bộ đọc bảng và `_key_of` / `key_rows` / `_post_id_of` / `_status_of` / `_moment_of` cho **cùng** kết quả ở mọi trường hợp (phép dò rộng hơn, 33 ký tự × 9 độ dài: bản mới 0 / 297 lệch, bản lượt 1 231 / 297) |
| Qua `SheetsClient` thật với 7 ký tự (NBSP, BOM, U+2060, U+00AD, U+3000, U+200E, U+E0020) × 40: Mã bài «(40 ký tự)b-70» và «B-070»; bài 172 ở «B-001» và «(40 ký tự)172»; ô Trạng thái, Ngày có 40 ký tự đầu | Trùng Mã bài: cảnh báo, không ghi; một bài hai dòng: cảnh báo; dòng còn lại đề xuất đúng, ghi không xung đột, chỉ chạm dòng đó |
| Mã bài khác hoa / thường («b-70», «B-0070») | Cùng mã B-070 ở mọi đường |
| NBSP **giữa** chữ («Đã␣đăng», «03/11/2026␣08:00», «B-␣072», «1␣72») | Hai cách đọc khớp: trạng thái, ngày đọc được; Mã bài, mã bài WordPress có khoảng trắng giữa là sai ở cả hai |
| Ô Trạng thái «=Đã đăng» (dạng công thức) | Cả hai cách đọc ra «Đã đăng»; chỉ ghi ô ngày, ô trạng thái giữ nguyên chữ người dùng |
| Ô **quá 2.000 ký tự** (1.995, 1.996, 1.997, 2.100 dấu cách rồi mới tới mã) | Hai cách đọc khớp (cùng cắt ở 2.000 ký tự như bộ đọc bảng), bảng có câu báo «dài quá 2.000 ký tự, đã cắt». Cắt đúng giữa mã thì đọc ra mã khác: xem «Giới hạn đã biết» |

### 2. Đổi hàm dùng chung trong `sync.py` (bài học T-041, T-091)

**Nơi gọi** (`git grep` trên nhánh và trên `main` `3cdd096`):

| Hàm | Nơi gọi | Đã chạy test |
|---|---|---|
| `_key_of` | `parse_sheet` → `key_rows`, `duplicate_keys`: dùng ở `open_row` (T-101 `plan.py:694`, `home.py:129`; T-102 `write.py:657`), `write_status` / `record_status` / `retry_pending` (T-102 `write.py:671`, `:3617`; T-101 `plan.py:757`), `_update` (mã mới đã có), `_key_present` (thêm dòng «chưa rõ»); `_fresh_row` (dòng chưa có mã) | `test_plan_sync`, `test_soi_loi_t100`, `test_la_chan_t100`, `test_t100_drafts_plan`, `test_t101_*`, `test_soi_loi_t101`, `test_la_chan_t101`, `test_t102_*`, `test_soi_loi_t102`, `test_la_chan_t102`, T-109 |
| `_post_id_of`, `_status_of` | `write_status` (T-100, T-102 qua `record_status`); `website.py` (kiểm, ghi, đếm bài) | như trên |
| `_moment_of` (`website.py`) | chỉ `website.py` | T-109 |

`app/` không gọi thẳng các hàm `_…` này. **Test ghim hành vi cũ:** `git grep` cả `tests/` (nhánh và `3cdd096`) theo `[:30]`, `[:100]`, «30 ký tự», «Không còn thấy dòng», `MSG_ROW_MISSING`, `CONFLICT_MISSING`, `key_rows`, `_key_of(`, `_post_id_of(`, `_status_of(`: không ca nào ngoài T-109 ghim cách cắt cũ (các chỗ trùng chữ là test alt, meta không liên quan; `test_plan_sync` dùng `key_rows` với mã gõ thường).

Hành vi đổi (theo hướng khớp bảng), có test mới:

| Tình huống | Trước (lượt 1) | Nay |
|---|---|---|
| «Viết bài» (`open_row`) dòng Mã bài «(40 dấu cách)B-080» | «Không còn thấy dòng» dù bảng hiện dòng đó | Mở được đúng dòng 2 |
| «Áp dụng» đề xuất sửa «Ưu tiên» dòng đó (`_fresh_row`) | Xung đột «Không còn thấy dòng» | Ghi đúng ô «Ưu tiên», ô Mã bài giữ nguyên chữ người dùng gõ |
| Dòng «(40 dấu cách)B-081» và dòng «B-081» | `key_rows` chỉ thấy dòng 3: `write_status` (việc ghi sau khi gửi của T-102) **ghi vào dòng 3** (dòng bảng đã bỏ vì trùng), ghi cả Mã bài WordPress | Mọi đường thấy trùng: `open_row` từ chối, `write_status` xung đột, không ghi ô nào |

**Tốc độ** (1.000 dòng, nhanh nhất của 3 lần, đo xen kẽ hai bản lúc máy đang chạy test khác): ô thường: đọc Sheet 0,38–0,40 → 0,39–0,47 giây, kiểm trạng thái 0,05 → 0,19–0,26 giây; ô dài cố tình (4 ô mỗi dòng gần 2.000 ký tự): đọc 3,07–3,16 → 3,22–3,44 giây, kiểm 0,05 → 1,20–1,25 giây. Tăng vì nay đọc lại đúng cả ô như bộ đọc bảng; vẫn tuyến tính, không đáng lo.

### 3. G4, G6, R5

| Mục | Tình huống | Kết quả |
|---|---|---|
| G4 | Ghi lúc kiểm + 5 phút / + 5 phút 1 micro giây / − 1 phút (giờ máy lùi) / − 1 phút 1 micro giây; `now` theo giờ Việt Nam và New York | Nhận / từ chối `MSG_STALE` / nhận / từ chối; múi giờ không đổi kết quả; từ chối **trước khi đọc** Sheet (không lệnh đọc, không lệnh ghi) |
| G4 | Lần kiểm cũ mà không chọn thay đổi nào; lần kiểm cũ + Sheet đang nối đã khác | «Không có thay đổi nào để ghi.» (vô hại); báo Sheet khác trước (kiểm mã băm đứng trước) |
| G6 | Ô «08:00», website 08:02:00 / 07:58:00 (lệch đúng 2 phút) | Không đề xuất |
| G6 | Website 08:02:01 / 07:57:59 / 08:02:59 | Một đề xuất sửa ngày; ghi xong kiểm lại **không còn đề xuất** (ô ghi tới phút, lệch còn dưới 1 phút, không lặp) |
| G6 | Bài hẹn giờ / đã đăng mà website không trả giờ, dòng «Bỏ» hay Sheet «Đã đăng» mà website còn hẹn giờ | Đúng một câu báo cho dòng («Bỏ…» / «đang hẹn giờ…»), không thêm «giờ lạ» |
| G3, G5 | Dòng «Bỏ» + bài không thấy; thiếu cột Mã bài / Trạng thái / Mã bài WordPress | Không cảnh báo; báo thiếu cột ngay lúc kiểm (test Thợ Máy, chạy lại qua) |
| R5 | `git diff 09870bd 088b1e1 --numstat -- tests/` | `test_soi_loi_t109.py` 3 thêm / 13 bớt (3 dấu `xfail` + 1 kỳ vọng được duyệt, có ghi chú); `test_t109_website_status.py` chỉ thêm (147 dòng); không file test nào khác đổi |

### 4. Gộp thử với `main` cục bộ `3cdd096` (có T-102)

Worktree tạm (đã xóa), `git merge --no-commit 3cdd096` vào `088b1e1`: **không xung đột**. `main` không đổi gì trong `seo_app/plan/` (chỉ `app/views/home.py`, `plan.py`, `write.py`, `seo_app/demo.py`, test, sổ sách), nên `sync.py` / `website.py` của nhánh vào nguyên. Trên bản gộp: 28 file chọn lọc (T-097 → T-103, T-109; gồm `test_t102_publish`, `test_t102_formula_cells`, `test_soi_loi_t102`, `test_la_chan_t102`, `test_wordpress_release`, `test_t101_*`): **2.373 qua, 4 xfail** có sẵn của T-102 (SL-T102-1, LC-T102-1), **1 hỏng có sẵn trên `main`** (test canh của T-103, không do T-109: mục «Ghi nhận ngoài phạm vi» dưới). Test của T-102 ghi «Đang viết», «Đã gửi nháp» qua `record_status` sau khi gửi, mở Soạn bài từ dòng kế hoạch (`open_row`): **qua hết**. File test Soi Lỗi mới (105 ca) chạy trên bản gộp: 105 qua.

### Góp ý lượt 2 (không xếp lỗi)

- **G7.** Dòng «Bỏ» có ô «Ngày đăng thực tế» gõ lạ: câu báo là «Ô «Ngày đăng thực tế» … không đọc được … Sửa ô đó» (cả khi website trả bản nháp hay riêng tư), thay vì «Dòng … ghi «Bỏ» nhưng bài … vẫn còn trên website». Dòng «Bỏ» không bao giờ được ghi nên ô ngày không quan trọng; có thể xét «Bỏ» trước ô ngày. Không ghi sai gì.
- **G8.** `MSG_STALE` viết cứng «quá 5 phút» trong câu, tách khỏi hằng `CHECK_MAX_AGE`: đổi hằng mà quên câu thì câu báo sai. Có thể dựng câu từ hằng.
- G2 (`states` sai kiểu → mọi bài «Không thấy») Chỉ Huy để lượt nối nút: nhắc lại khi nối.

### Giới hạn đã biết (lượt 2)

- Ô Mã bài / Mã bài WordPress **dài quá 2.000 ký tự**: bộ đọc bảng (T-098) cắt ở 2.000 ký tự rồi mới làm sạch, nên mã nằm vắt qua chỗ cắt có thể đọc thành mã khác: «(1.996 dấu cách)B-070» thành B-007, «(1.998 dấu cách)1700» thành bài 17. Nay mọi đường đọc giống nhau và bảng có câu báo «dài quá 2.000 ký tự, đã cắt»; cần gần 2.000 ký tự trắng trước mã nên không xảy ra khi gõ tay. Nếu muốn chặn hẳn: ô mã dài quá giới hạn coi là không đọc được thay vì cắt.

### Ghi nhận ngoài phạm vi (có sẵn trên `main` `3cdd096`, không do T-109)

- `tests/test_t103_plan_prompt.py::test_plan_section_note_says_not_used_yet_and_is_true` **hỏng** trên bản gộp: test canh của T-103 dò chuỗi `["plan"]` trong `app/`, `seo_app/` để chắc chưa code nào đọc mục `[plan]` của `config/content.toml`, nay bắt nhầm `holder["plan"]`, `result["plan"]` trong `app/views/write.py` của T-102 (dòng 3441–3443, 3622, 3624). `git grep` trên `3cdd096` cho cùng kết quả, nhánh T-109 không có chuỗi đó: hỏng cả trên `main`. Mục `[plan]` vẫn chưa được đọc; cần thu hẹp mẫu dò của test (sửa test có duyệt R5), không phải sửa code.
- `tests/test_soi_loi_t102.py` (trên `main`) tạo `data/site_index.sqlite` trong thư mục dự án khi chạy (thử từng file trên bản gộp: `test_t102_publish.py` không tạo, `test_soi_loi_t102.py` tạo). `data/` có trong `.gitignore` nên không lọt vào commit, nhưng test không nên ghi vào thư mục dự án.

### Lệnh đã chạy (lượt 2)

```
uv run pytest tests/test_soi_loi_t109.py tests/test_t109_website_status.py -q                    # 088b1e1: 146 qua
uv run pytest tests/test_soi_loi_t109.py -k round2 -q        # 088b1e1: 53 qua; 09870bd (tạm): 41 hỏng, 12 qua
uv run pytest <8 file: T-109, T-100, đọc bảng> -q                                                # 712 qua
uv run pytest <28 file: T-097 → T-103, T-109> -q    # bản gộp 3cdd096: 2.373 qua, 4 xfail (T-102), 1 hỏng có sẵn trên main (test canh T-103)
uv run python <phép dò 297 biến thể, đo tốc độ>                                                  # 0 lệch (lượt 1: 231)
uv run ruff check tests/test_soi_loi_t109.py; uv run ruff format --check tests/test_soi_loi_t109.py
```

Quét ký tự ẩn trên `sync.py`, `website.py`, 2 file test, báo cáo Thợ Máy: sạch. Không gọi Google, WordPress thật; không chạy cloud; không mở app.

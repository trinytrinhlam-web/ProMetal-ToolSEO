# Báo cáo T-015 · Kiểm thử: lỗi Thấp còn lại, test tốc độ ổn định

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-015](../tickets/T-015-loi-thap-con-lai.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành. **Đạt có điều kiện**: không có lỗi Cao, còn 3 lỗi (R6-1 Thấp, R6-2 Thấp, R6-3 Trung bình) |

## Tóm tắt (cho chủ dự án)

Ba phần sửa của Thợ Máy chạy đúng.

- Câu AI gợi ý không còn mang thẻ HTML vào bài.
- Câu kiểu «Cửa [A](dày "mỏng" 1mm)» không còn bị mất chữ.
- Không có link nào lọt qua.

Còn 3 điểm nhỏ:

- **R6-1:** chữ bị mất khi trong ngoặc có dấu "<", ví dụ «(<0,5 mm)». Lỗi này có từ trước T-015.
- **R6-2:** khi thay câu, chỗ nối vẫn có thể ghép thành thẻ HTML. Thợ Máy đã nêu điểm này; tôi tái hiện được qua đúng đường đi thật. Thẻ này không chạy được, vì giao diện đã escape và bài gửi WordPress còn qua bộ lọc.
- **R6-3:** test tốc độ mới vẫn chập chờn khi máy đang bận. Mục tiêu của phiếu là test không đỏ oan trên máy chậm, nên mục tiêu này chưa đạt trọn.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_round6.py` (mới) | 59 test: 53 qua, 6 `xfail(strict=True)` cho R6-1, R6-2, R6-3. |
| `docs/team/reports/T-015-soi-loi.md` | Báo cáo này. |

Tôi không sửa code ứng dụng, không chạy `stash`/`reset`/`checkout`/`clean`, không commit.

## Kết quả kiểm thử theo phần

**1. `apply_flag` bỏ thẻ trong câu thay thế: đạt.**
- 7 mẫu thẻ độc đều bị bỏ: thẻ lồng `<scr<script>ipt>`, `<<b>img …>`, comment, `<svg/onload>`, `<a href=javascript:>`, `<STYLE>`, thẻ chưa đóng.
- 7 kiểu chỗ nối có thể ghép thành link đều bị vô hiệu: `]`+`(`, `\` bị bỏ, `[b]`+`(x)`, `[b][ref]`, `[b]:` đầu dòng, `\\`. Thử cả hai trường hợp: thay câu và bỏ câu.
- Thử ngẫu nhiên 20 000 bộ (thân bài, câu, câu thay thế): không có link nào sống.
- Đường đi thật (`clean_review` rồi `apply_replacements`): không còn thẻ, không còn `alert`, không còn địa chỉ.

**2. R5-1 trong `looks_like_destination`: đạt.**
- Chữ không còn bị mất ở 9 dạng: chữ dính sau dấu nháy đóng, hai tiêu đề, `'nó's'`, nháy đóng bị escape, `(mỏng)1mm`, nháy cong tiếng Việt, dòng trống ở giữa, hai link trên một dòng.
- Link thật vẫn bị bỏ địa chỉ ở 15 dạng: có tiêu đề `"…"`, `'…'` hoặc `(…)`; nháy escape bên trong; `\\` rồi mới tới nháy; ngoặc trong tiêu đề; `<…>`; ảnh; tiêu đề rỗng; khoảng trắng hoặc xuống dòng trước `)`.
- Ca `[a](url "a)b")` là link thật theo CommonMark, nhưng nay được giữ nguyên chữ. Ca này vẫn an toàn, vì `]\(` đã bị escape nên không thành link.
- Tính nghịch đảo vẫn giữ: chạy 20 000 chuỗi ngẫu nhiên nhiều dấu nháy. Phần escape/unescape không bị sửa trong phiếu này.
- Thời gian chạy vẫn tuyến tính với 6 đầu vào xấu: nháy không đóng, nháy escape, ngoặc tiêu đề lồng 24 000 tầng, 40 000 dấu nháy đứng trước link. Đo riêng ngoài pytest ở 5 cỡ, mỗi lần gấp đôi cỡ thì thời gian tăng khoảng 2 lần.

**3. Helper `tests/timing.py`.**
- Bắt được hàm bình phương thật: có test `test_helper_catches_quadratic_function`.
- Hàm tuyến tính qua.
- Khi máy rảnh, chạy riêng 54 test tốc độ 5 lần: lần nào cũng qua. Tỉ lệ đo được cao nhất là 8,11, rất sát ngưỡng 9 (`_clean_and_sanitize` với `<script…`). Rất hiếm khi phải đo lại.
- Khi máy bận (6 chương trình chạy hết CPU trên máy 4 nhân), chạy 2 lần thì cả 2 lần có **2 test đỏ**. Xem R6-3.
- Có 7 đầu vào của `sanitize_html` chạy dưới 0,1 ms ở cỡ nhỏ. Helper làm tròn các lần đo này lên 0,1 ms, nên ở đó gần như không đo được tỉ lệ. Tôi cho rằng việc này chưa gây hại: hàm bình phương trên 50 000 ký tự không thể chạy nhanh tới vậy. Xem phần Đề xuất.

## Lỗi tìm thấy

### R6-1 · Thấp · Ngoặc mở bằng "<" mà không có địa chỉ `<…>` hợp lệ thì mất chữ
- **Tái hiện:** `clean_ai_text("Sai số [cho phép](<0,5 mm) thôi.")`. Thêm hai ca `(< 5 mm)` và `(<0,5 mm> là chuẩn)`.
- **Mong đợi:** giữ nguyên chữ, chỉ escape. Theo CommonMark, đây không phải link: không có `>` đóng, hoặc sau `>` còn chữ không phải tiêu đề.
- **Thực tế:** `"Sai số cho phép thôi."`, mất «<0,5 mm».
- **Nguyên nhân:** `looks_like_destination` gặp `text[dest] == "<"` là trả `True` ngay, không kiểm tra có `>` đóng và phần sau `>` có đúng dạng không. Lỗi có từ trước T-015.
- **Test:** `test_r6_1_angle_bracket_without_valid_destination_keeps_text` (×3).

### R6-2 · Thấp · Chỗ nối trong `apply_flag` vẫn ghép được thẻ HTML
- **Tái hiện:** thân bài «Nhiệt độ <5 độ là tốt.». Thân bài này đã sạch: `clean_ai_text` giữ nguyên vì sau "<" là chữ số. AI gợi ý câu «5 độ là tốt.», thay bằng «img src=x onerror=alert(1)>». Câu thay thế này qua `clean_review` mà không đổi gì, vì không có dấu "<". Sau `apply_replacements`, kết quả là `Nhiệt độ <img src=x onerror=alert(1)>`. Bỏ câu (không có câu thay thế) cũng ghép ra thẻ tương tự.
- **Mong đợi:** bài sau khi áp gợi ý không có thẻ HTML.
- **Thực tế:** có thẻ `<img onerror>`.
- **Mức độ:** Thấp. Thẻ không chạy được, vì `ui.highlight` đã escape và bài gửi WordPress còn qua `sanitize_html`. Muốn ghép ra thẻ, AI phải chọn đúng câu bắt đầu ngay sau "<", tức phải bị chèn lệnh (prompt injection).
- **Hướng sửa gợi ý:** sau khi ghép, chạy `_TAG_OPEN.sub("< ", …)` hoặc `strip_tags` trên đúng vùng quanh chỗ nối. Cách khác là tách "<" ở cuối phần trước câu. Chỉ Huy quyết; Thợ Máy cũng đã nêu điểm này.
- **Test:** `test_r6_2_seam_with_lt_in_body_makes_tag` (×2).

### R6-3 · Trung bình · Test tốc độ theo tỉ lệ vẫn đỏ oan khi máy bận
- **Tái hiện:** chạy 6 vòng lặp bận CPU (`python3 -c "while True: pass"`) trên máy 4 nhân, rồi chạy 4 file test tốc độ. Cả 2 lần chạy đều có 2 test đỏ:
  - lần 1: `ngoac-vuong-roi-dong` với tỉ lệ 10,8, và `[a]: u\r` với 9,7;
  - lần 2: `nhan-dai-nhieu-dong` với 9,6.
- **Mong đợi:** hàm tuyến tính qua dù máy bận. Đây chính là mục tiêu của phiếu: «dễ hỏng trên máy Windows chậm».
- **Thực tế:** đỏ.
- **Nguyên nhân:** cỡ nhỏ chạy khoảng 20 ms. Lấy lần nhanh nhất trong 3 lần thì gần như luôn có một lần may mắn không bị ngắt. Cỡ lớn chạy khoảng 200 ms nên lần nào cũng bị chia CPU. Kết quả là máy bận làm chậm lần đo lớn nhiều hơn lần đo nhỏ. Đáng chú ý: cũng lúc máy bận đó, lần đo lớn chỉ mất khoảng 0,5 giây, nên mốc cũ "dưới 1 giây" vẫn qua.
- **Test:** `test_r6_3_helper_stable_on_busy_machine`. Test dùng đồng hồ giả mô phỏng máy bận, nên kết quả xác định và không chập chờn.
- **Hướng sửa gợi ý:** đo bằng thời gian CPU (`time.process_time` hoặc `thread_time`) thay cho `perf_counter`, vì thời gian CPU không tính lúc chờ máy. Tôi đã thử thay riêng `_time_once` bằng `process_time` trong một plugin tạm ngoài repo: R6-3 qua, 2 test helper khác vẫn qua. Lưu ý: trên Windows, thời gian CPU chỉ chính xác tới khoảng 15,6 ms, nên cỡ nhỏ cần chạy từ khoảng 100 ms trở lên, nghĩa là phải tăng cỡ đầu vào. Cách khác là đo xen kẽ nhỏ và lớn, rồi nới ngưỡng có kiểm soát. Thợ Máy chọn cách.

## Bằng chứng

```
$ uv run pytest
1512 passed, 9 xfailed in 53.34s
# 9 xfail: R4-3 ×2, SL-7 (đã có từ trước) + R6-1 ×3, R6-2 ×2, R6-3 (mới)

$ uv run ruff check .
All checks passed!

$ uv run pytest -q tests/test_soi_loi_round6.py   (chạy 3 lần)
53 passed, 6 xfailed  (cả 3 lần)
```

Đã chạy `--runxfail` để chắc 6 test `xfail` đỏ đúng ở dòng `assert` mong đợi, không phải vì lỗi khác.

## Đối chiếu tiêu chí xong của phiếu

- [x] Mục 1, `apply_flag` bỏ thẻ: đạt. Còn chỗ nối (R6-2, Thấp).
- [x] Mục 2, R5-1: đạt. Test R5-1 đã qua, không còn `xfail`.
- [ ] Mục 3, test tốc độ ổn định: đạt khi máy rảnh, chưa đạt khi máy bận (R6-3).
- [x] Mục 4, PEP 8: đạt, `ruff` sạch.

## Rủi ro và điểm cần chú ý

- Cả bộ test nay mất khoảng 53–58 giây, trước đây 43 giây (Thợ Máy đo).
- Câu thay thế chỉ có thẻ (ví dụ `<b></b>`) bị bỏ hết thẻ thành chuỗi rỗng, nên câu gốc bị xóa và để lại dấu cách thừa ở đầu: `' Câu C.'`. Chỉ ảnh hưởng chữ, không ảnh hưởng an toàn. Không xếp thành lỗi.

## Đề xuất

- Thợ Máy: sửa R6-3, đổi helper sang đo thời gian CPU. Nên kèm một kiểm tra: nếu cỡ nhỏ chạy dưới mức đo tin được thì báo lỗi (hoặc tự tăng cỡ), thay vì làm tròn lên 0,1 ms rồi cho qua.
- Thợ Máy: R6-1 và R6-2 (Thấp), làm cùng lượt nếu tiện.

## Câu hỏi cho chủ dự án

Không có.

---

## Lần 2 (2026-10-14, kiểm lại sau khi Thợ Máy sửa R6-1, R6-2, R6-3 và Lá Chắn #2)

**Kết quả: Đạt.** Không còn lỗi R6 nào. Không phát hiện lỗi mới.

### Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_round7.py` (mới) | 39 test, tất cả qua. |
| `docs/team/reports/T-015-soi-loi.md` | Thêm mục này. |

Tôi không sửa `tests/test_soi_loi_round6.py` (Thợ Máy đã gỡ đúng 6 `xfail`, tôi đối chiếu bằng `git diff`). Không chạy stash/reset/checkout/clean, không commit.

### Kết quả theo mục Chỉ Huy giao

**1. `apply_flag` không còn ghép ra thẻ hay autolink ở chỗ nối: đạt.**
- Thử ngẫu nhiên 30 000 bộ (thân bài, câu, câu thay thế). Bộ chữ dùng để thử gồm `<`, `>`, `[ ] ( )`, `\`, `!--`, `img … onerror …>`, `https://…>`, `a@b.c>`. Không lần nào ra thẻ, comment, khai báo `<?`, autolink, hay link Markdown sống.
- 7 ca viết tay: autolink chỗ nối trái và phải, autolink email, comment `<!--`, `<?php`, và nhánh bỏ câu với `</textarea><img>`, `<<script>`. Tất cả sạch.
- Áp gợi ý lần hai lên kết quả đã lọc: chữ không đổi thêm (không chồng thêm `\` hay `< `).

**2. R6-1 (địa chỉ `<…>`): đạt.**
- Link thật vẫn bị bỏ địa chỉ ở 10 dạng `<…>`: có hoặc không có tiêu đề, tiêu đề xuống dòng, `\>` bên trong, có dấu cách trong `<…>`, `<>`, ảnh.
- 7 dạng lạ (thiếu khoảng trắng trước tiêu đề, xuống dòng trong `<…>`, `<` lồng, `)` trong `<…>` …) không còn link sống, không còn thẻ.
- Chữ không còn mất ở 6 câu kiểu «(<0,5 mm)», «(< 5 mm)», «(<0,5 mm> là chuẩn)», kể cả hai chỗ trên cùng một dòng.
- Thử ngẫu nhiên 20 000 chuỗi nhiều `<`, `>`: không còn link, và `escape(unescape(x)) == x` đúng. Với chữ gốc không có `\` thì `unescape(escape(t)) == t` đúng.
- Ca `[a](<u)v>)` là link thật theo CommonMark, nhưng nay được giữ nguyên chữ. Ca này an toàn vì đã escape `]\(`.

**3. `tests/timing.py` đo bằng `process_time`: đạt.**
- Máy bận, tái hiện như lần 1 (6 vòng lặp chiếm hết CPU trên máy 4 nhân): chạy 3 lần 6 file test tốc độ, cả 3 lần `509 passed`. Lần 1 thì 2 lần chạy đều có 2 test đỏ.
- Thử thêm 12 tiến trình chép bộ nhớ liên tục (làm chậm bộ nhớ, thứ mà thời gian CPU không loại bỏ được): `509 passed`.
- Chạy `test_soi_loi_round6.py` và `test_soi_loi_round7.py` khi máy bận: `98 passed`.
- Vẫn bắt được hàm bình phương: `test_helper_catches_quadratic_function` và 3 test ở mục 4 đều đỏ đúng như mong đợi.

**4. Đầu vào tra tiêu đề nhiều lần (ý của Lá Chắn): đã thêm.**
- Nguyên tắc: mỗi tầng là một link có tiêu đề (hoặc dấu `>`) nằm rất xa, và sau đó còn chữ nên không phải link. Nhờ vậy bộ đọc phải đi tiếp vào tầng trong và tra lại.
- Ba đầu vào:
  - `"[a](x (" * N + ") y)" * N`: tiêu đề ngoặc khớp ở xa;
  - `"[a](<5 " * N + ")" * N + ">"`: `<` không có `>` hợp lệ;
  - `"[a](<5 <" * N + ")" * N + ">"`: có `<` chen giữa.
- Code thật: chạy tuyến tính (`test_many_title_and_angle_lookups_scale_linearly`, đo cả `strip_markdown_links` và `clean_ai_text`).
- Kiểm chứng sức mạnh của đầu vào: thay `_title_end` và `_angle_destination_end` bằng bản lỗi cố ý quét thẳng (vòng lặp Python), helper **bắt được** cả 3 (`test_many_lookup_inputs_catch_naive_scan`).
- Ghi chú: bản lỗi dùng `str.find` (chạy bằng C) thì ở cỡ đầu vào hợp lý chỉ chậm gấp khoảng 4–9 lần, chưa vượt ngưỡng một cách chắc chắn. Vì vậy tôi kiểm chứng bằng bản quét bằng vòng lặp Python. Bản `str.find` vẫn chạy nhanh (dưới 0,3 giây với 64 000 tầng), nên không gây treo app.

### Bằng chứng

```
$ uv run pytest
1564 passed, 3 xfailed in 74.99s
# 3 xfail: R4-3 ×2 (đã chấp nhận), SL-7 (Giai đoạn 5)

$ uv run ruff check .
All checks passed!

$ uv run pytest -q tests/test_soi_loi_round7.py   (3 lần)
39 passed (cả 3 lần, khoảng 8 giây)
```

### Rủi ro và điểm cần chú ý

- Cả bộ test nay mất khoảng 75 giây. Tăng thêm do mỗi lần đo chạy ít nhất 0,1 giây CPU, cộng thêm 39 test mới.
- Như Thợ Máy và Lá Chắn đã nêu, HTML người dùng tự gõ trong một phần sẽ bị bỏ khi áp gợi ý ở phần đó. Đây là đánh đổi đã biết, không phải lỗi.
- URL trần (`https://…` không có `< >`) vẫn có thể được bộ hiển thị GFM tự biến thành link. Điểm này nằm ngoài phạm vi T-015, và trước giờ `clean_ai_text` cũng chưa xử lý. Nếu chưa có trong sổ rủi ro thì Chỉ Huy cân nhắc ghi vào.

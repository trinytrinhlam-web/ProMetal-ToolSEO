# Báo cáo T-015 · Lỗi Thấp còn lại sau T-013/T-014, test tốc độ ổn định

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-015](../tickets/T-015-loi-thap-con-lai.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Bốn việc trong phiếu đã xong.

1. Câu AI gợi ý thay thế giờ được bỏ thẻ HTML trước khi ghép vào bài.
2. Câu như «Cửa [A](dày "mỏng" 1mm)» không còn bị cắt mất chữ.
3. Các test tốc độ không còn so với mốc "dưới 1 giây", vốn dễ đỏ oan trên máy Windows chậm. Nay test so tỉ lệ: đầu vào dài gấp 4 thì thời gian không được tăng quá 9 lần. Code chạy tuyến tính chỉ chậm gấp khoảng 4 lần; code chậm theo kiểu bình phương sẽ chậm gấp khoảng 16 lần và bị bắt.
4. Sửa dòng trống theo PEP 8 trong `sanitize.py`.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/content/workflow.py` | `apply_flag`: câu thay thế qua `strip_tags` trước khi ghép, tức `escape_link_syntax(body.replace(câu, strip_tags(thay_thế)))`. |
| `seo_app/sanitize.py` | R5-1: `looks_like_destination` kiểm tra tiêu đề có đóng hay không và sau tiêu đề chỉ còn khoảng trắng rồi tới `)`. Thêm 2 dòng trống trước `clean_ai_text` (PEP 8). |
| `tests/timing.py` (mới) | Hàm `assert_scales_linearly(fn, make)`, chi tiết ở mục bên dưới. |
| `tests/test_link_escape.py` | 2 test tốc độ đổi sang so tỉ lệ. Thêm 12 trường hợp: `apply_flag` bỏ thẻ, R5-1, tốc độ tra tiêu đề. |
| `tests/test_sanitize_hardening.py` | 2 test tốc độ đổi sang so tỉ lệ (18 trường hợp). |
| `tests/test_soi_loi_round3.py` | `test_filter_stays_fast_on_round3_inputs` đổi sang so tỉ lệ (12 trường hợp). |
| `tests/test_soi_loi_t003_t009.py` | `test_filters_stay_fast_on_more_adversarial_inputs` đổi sang so tỉ lệ (9 trường hợp × 2 hàm). |
| `tests/test_soi_loi_round5.py` | Gỡ `xfail` R5-1 (3 trường hợp), không sửa gì khác. |

Ba file test của Soi Lỗi chỉ được sửa phần đo tốc độ, đúng như phiếu cho phép, kèm hai dòng import mà ruff tự sắp lại. Tôi không chạy `stash`, `reset` hay `checkout` (R11) và không commit.

## Chi tiết

**1. `apply_flag`**
- Câu thay thế thường đã qua `clean_review` rồi, nhưng `apply_flag` không dựa vào điều đó nữa: nó tự bỏ thẻ ngay tại chỗ ghép.
- Test `test_apply_flag_strips_tags_from_replacement` dùng 4 mẫu (`<script>`, `<img onerror>`, `<b>`, `<a href>`): kết quả không còn thẻ, không còn `alert`, không còn link.

**2. R5-1**
- Sau địa chỉ, nếu có tiêu đề thì tìm ký tự đóng của tiêu đề:
  - với `"` và `'`: dấu nháy cùng loại, chưa escape, đứng sau gần nhất;
  - với `(`: ngoặc khớp, lấy từ bảng ghép ngoặc sẵn có.
- Chỉ coi là link khi tiêu đề đóng trước `)`, và giữa hai chỗ đó chỉ có khoảng trắng. Nếu tiêu đề không đóng, hoặc còn chữ sau tiêu đề, thì không phải link: giữ chữ, chỉ thêm `\` sau `]`.
- Vị trí các dấu nháy được lập một lần rồi tra bằng `bisect`, nên vẫn chạy tuyến tính. Có test `test_title_lookup_stays_linear` với ngoặc lồng 20 000 tầng.
- Ghi chú `\f`/`\v` của Soi Lỗi không đổi, vì AI hầu như không viết các ký tự này.

**3. Test tốc độ**
- Mỗi đầu vào cũ được viết lại thành hàm theo cỡ `k`: `k = 4` cho đúng đầu vào cũ, `k = 1` cho đầu vào cỡ 1/4. Không đầu vào nào bị bỏ hay làm nhỏ đi.
- `assert_scales_linearly` đo hai cỡ:
  - cỡ nhỏ lấy lần nhanh nhất trong 3 lần, có chạy nháp trước;
  - cỡ lớn đo tối đa 3 lần, lấy lần nhanh nhất, dừng sớm khi đã đạt;
  - tắt dọn rác bộ nhớ (`gc`) trong lúc đo;
  - đòi tỉ lệ thời gian không quá 9.
- Thời gian cỡ nhỏ dưới 0,1 ms được tính là 0,1 ms. Lý do: đo dưới mức này rất nhiễu, và Soi Lỗi cũng dùng mức này ở `test_soi_loi_round5.py`.
- Kiểm tra lại hàm đo bằng một hàm cố ý chậm theo kiểu bình phương: bị bắt với tỉ lệ 16,1.
- Các kiểm tra khác trong test (không còn thẻ, không còn link, đầu vào ≥ 190 000 ký tự) giữ nguyên, chạy trên đầu vào cỡ đầy đủ.

## Bằng chứng

```
$ uv run pytest
1459 passed, 3 xfailed in 42.93s
# 3 xfail: R4-3 ×2 (Chỉ Huy đã chấp nhận), SL-7 (Giai đoạn 5)

$ uv run ruff check .
All checks passed!
```

Chạy lại riêng 54 test tốc độ 3 lần liên tiếp: lần nào cũng `54 passed`, khoảng 18 giây.

## Đối chiếu tiêu chí xong

- [x] `uv run pytest` qua hết, R5-1 hết `xfail` (`test_r5_1_parenthesis_with_quote_then_more_words_keeps_text` ×3).
- [x] `uv run ruff check .` sạch.
- [x] Báo cáo này.

## Rủi ro và điểm cần chú ý

- Cả bộ test chậm hơn khoảng 12 giây, từ 31 lên 43 giây, vì mỗi đầu vào giờ được đo ở hai cỡ và đo lặp lại.
- Chỗ nối khi thay câu vẫn có thể ghép ra thẻ, ví dụ thân bài kết thúc bằng `<` và câu thay thế mở đầu bằng chữ cái. Thân bài do người dùng tự sửa vốn đã có thể chứa HTML. Cả hai đều không chạy được, vì chỗ hiển thị đã escape (`ui.highlight`) và chữ gửi WordPress sẽ qua `sanitize_html`. Nếu muốn chặn cả ở đây thì phải bỏ thẻ trên toàn bộ phần bài, kể cả HTML người dùng tự gõ. Việc đó cần Chỉ Huy quyết.

## Câu hỏi cho chủ dự án

Không có.

## Lần 2 (2026-10-14, sau [Lá Chắn](T-015-la-chan.md) KHÔNG ĐẠT và [Soi Lỗi](T-015-soi-loi.md) đạt có điều kiện)

### Đã sửa

| Mục | Sửa |
|---|---|
| **Lá Chắn #1 / R6-2** (chặn phiếu) | `apply_flag` (`seo_app/content/workflow.py`) nay lọc trên **kết quả sau khi ghép**, ở **cả hai nhánh**: `escape_link_syntax(strip_tags(ghép))`. Nhánh thay câu vẫn bỏ thẻ ở câu thay thế trước khi ghép. Như Lá Chắn đã nêu, cái giá là HTML người dùng tự gõ trong phần đó cũng bị bỏ khi áp gợi ý. |
| **R6-3** (Trung bình) | `tests/timing.py` đo bằng **thời gian CPU** (`time.process_time`) thay vì `perf_counter`. Mỗi lần đo chạy lặp hàm tới khi đủ 0,1 giây CPU rồi chia đều cho số lần chạy, nên vượt độ phân giải khoảng 15,6 ms trên Windows mà không phải tăng cỡ đầu vào. Bỏ luôn mức sàn 0,1 ms vì không còn cần: các đầu vào rất nhanh của `sanitize_html` nay cũng đo được tỉ lệ thật (Soi Lỗi ghi ở mục Đề xuất). |
| **Lá Chắn #2** (Thấp) | Thêm mốc tuyệt đối rộng `MAX_SECONDS = 5` giây CPU cho lần đo cỡ đầy đủ. Hiện các lần đo chỉ khoảng 0,2 giây. Có test `test_timing_helper_has_absolute_limit`. |
| **R6-1** (Thấp) | Trong `looks_like_destination`, địa chỉ dạng `<…>` phải có `>` đóng (chưa escape), giữa hai dấu không có `<` hay xuống dòng, và sau `>` chỉ được là khoảng trắng hoặc `)`. Nếu không đạt thì đó là chữ thường, giữ nguyên, ví dụ `(<0,5 mm)`, `(< 5 mm)`, `(<0,5 mm> là chuẩn)`. Vị trí `<`, `>`, xuống dòng và dấu nháy chưa escape được lập một lần rồi tra bằng `bisect`, nên vẫn tuyến tính. Round-trip `unescape`/`escape` không đổi, vì phần này chỉ ảnh hưởng bước bỏ link, không ảnh hưởng bước escape. |

### Test

- Gỡ `xfail` R6-1 (3 trường hợp), R6-2 (2) và R6-3 (1) trong `tests/test_soi_loi_round6.py`. Không sửa gì khác trong file đó.
- Thêm `test_apply_flag_seam_cannot_make_tag_or_autolink` (6 trường hợp) theo 4 dạng Lá Chắn nêu:
  - chỗ nối phải: câu gợi ý kết thúc bằng `<`;
  - chỗ nối trái: `<"foo"`, `<5 độ`;
  - nhánh bỏ câu;
  - autolink `<https://…>`, ở cả hai nhánh.
- Đã đối chứng: với `apply_flag` cũ, cả 6 trường hợp đều ra `<a href="https://evil.example">` hoặc `<https://…>`. Với bản mới thì không còn.

### Bằng chứng

```
$ uv run pytest
1525 passed, 3 xfailed in 67.51s
# 3 xfail: R4-3 ×2 (đã chấp nhận), SL-7 (Giai đoạn 5)

$ uv run ruff check .
All checks passed!
```

**Thử khi máy bận** (máy 4 nhân, 6 vòng lặp chiếm hết CPU, giống cách Soi Lỗi tái hiện R6-3): chạy 61 test tốc độ 2 lần, cả 2 lần đều `61 passed`.

### Rủi ro

- Cả bộ test chậm thêm khoảng 14 giây so với lần trước (khoảng 53 giây lên 67 giây), vì mỗi lần đo kéo dài ít nhất 0,1 giây CPU.
- `process_time` tính thời gian CPU của **cả tiến trình**. Nếu sau này test chạy song song nhiều luồng trong cùng tiến trình, số đo sẽ lẫn; hiện pytest chạy một luồng.
- HTML người dùng tự gõ trong một phần sẽ bị bỏ khi bấm Áp dụng gợi ý ở phần đó (đã nêu ở mục Lá Chắn #1).

# Báo cáo T-068 · Dọn lỗi Thấp bước code tự sửa alt (sau T-062)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-068](../tickets/T-068-don-loi-thap-alt-anh-ai.md) · lỗi từ [T-062-soi-loi](T-062-soi-loi.md), điều kiện 2 của [T-062-la-chan](T-062-la-chan.md) |
| Nhánh | `team/T-068` (worktree `D:\ProMetal-ToolSEO\wt-T-068`, tạo từ `main` `af7ac41`) |
| Ngày nộp | 2026-10-20 |
| Máy chạy | Windows 11 Pro 10.0.26300, Python 3.12 (uv) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Đã sửa 3 lỗi nhỏ ở bước phần mềm tự chỉnh alt mà AI gợi ý. (1) AI trả về alt chỉ có dấu câu hay biểu tượng («???», «!!!», «🔥🔥») thì nay báo «AI không viết được alt», như khi AI để trống. (2) AI tự viết «Minh họa» trong ngoặc («Minh họa», “Minh họa”, **Minh họa**) hay dính dấu câu («Minh họa!», «Minh họa…»): phần mềm bỏ đi rồi ghi đúng **một** tiền tố, không còn «Minh họa «Minh họa» cửa cuốn». (3) Phần mềm bỏ tiền tố AI tự viết **trước** rồi mới cắt cho vừa độ dài, nên không còn mất chữ cuối hay báo lỗi oan khi giới hạn alt nhỏ. Ảnh AI vẫn **luôn** có chữ «Minh họa» / «Ảnh minh họa (AI)» do phần mềm tự thêm (C6).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/images/alt.py` | `_one_line` (lọc, gộp một dòng, chưa cắt; `clean_alt_text` dùng lại); `_strip_ai_prefix` nhận tiền tố trong ngoặc, dính dấu câu, lặp lại, bọc cả câu; `_meaningful` (có chữ cái hay chữ số); `clean_suggestion` đổi thứ tự: bỏ tiền tố → cắt phần thân theo chỗ còn lại → ghép tiền tố chuẩn |
| `tests/test_t062_alt_prompt.py` | Thêm 145 test (11 hàm) cho SL-T062-1 → 3 và C6 |
| `tests/test_soi_loi_t062.py` | Gỡ 3 dấu `xfail` (SL-T062-1, -2, -3), thân test không đổi; test C6 đổi cách kiểm riêng 2 đầu vào «???», «🔥🔥» (xem Rủi ro, mục 1) |
| `docs/team/reports/T-068-tho-may.md` | Báo cáo này |

Không sửa `seo_app/ai/**`, `seo_app/content/**`, `app/**`, `config/**`.

## Cách sửa

| Mã | Cách sửa | Code |
|---|---|---|
| SL-T062-1 | Sau khi lọc và cắt, alt không có chữ cái hay chữ số nào (`str.isalnum`) thì báo `AIError` «AI không viết được alt…», cả ảnh AI lẫn ảnh thật. Chú thích như vậy coi như để trống (ảnh AI còn đúng tiền tố «Ảnh minh họa (AI)»). Kiểm cả **sau khi cắt**: cắt theo ranh giới từ có thể chỉ còn phần dấu câu ở đầu («?????????? cửacuốn…» → «??????????») | `alt.py:389-392` (`_meaningful`), `:439-442` |
| SL-T062-2 | `_strip_ai_prefix`: tối đa 3 ký tự ngoặc mở `« “ ‘ ‹ " ' ( [ *` trước tiền tố; ngay sau tiền tố có ngoặc đóng tương ứng thì bỏ; không có mà cuối câu có ngoặc đóng (và giữa câu không còn ngoặc đóng ấy) thì là ngoặc bọc cả câu, bỏ ngoặc cuối. Dấu dính sau tiền tố: `: , . ; ! ? … - – — \| / · •`. Lặp tới khi hết tiền tố. Không có tiền tố thì giữ nguyên chữ, kể cả ngoặc («Minh họa «cửa cuốn» nhà phố», «(2 cánh) cửa cuốn» giữ ngoặc) | `alt.py:347-386` |
| SL-T062-3 | `clean_suggestion`: lọc, gộp một dòng nhưng **chưa cắt** (`_one_line`); ảnh AI thì bỏ tiền tố AI tự viết; cắt phần thân theo chỗ còn lại (`max_chars` − «Minh họa » = 9 ký tự; `caption_max_chars` − «Ảnh minh họa (AI): » = 19); rồi mới ghép tiền tố (`_with_prefix`, như cũ). Bỏ chấm cuối alt trước khi cắt, nên câu vừa đúng giới hạn không mất chữ cuối vì dấu chấm (cũng áp cho ảnh thật) | `alt.py:433-446` |

C6 giữ nguyên: tiền tố vẫn do `_with_prefix` ghép **trước**, chỉ phần thân bị cắt (`alt.py:404-410`, không đổi); alt ảnh AI không bao giờ được trả về thiếu tiền tố, chỉ có thể là có tiền tố hoặc báo lỗi.

## Bằng chứng

```
$ git log --oneline -3      # nhánh team/T-068
ed328f0 T-068: test cho SL-T062-1 → 3 và C6 (tiền tố ảnh AI đúng một lần)
5022558 T-068: sửa SL-T062-1 → 3 ở bước code tự sửa alt; gỡ 3 dấu xfail
af7ac41 Thêm tiến độ phần trăm vào bảng việc; …                       # main lúc tạo nhánh

$ uv run pytest tests/test_soi_loi_t062.py -k "sl_t062 or prefix" --runxfail   # trước khi gỡ xfail
4 failed, 34 passed        # 18/18 test SL-T062 đã qua; 4 hỏng = test C6 với alt «???», «🔥🔥» (Rủi ro, mục 1)

$ uv run pytest tests/test_t062_alt_prompt.py      # test mới chạy trên alt.py CŨ (af7ac41), nạp thay module
111 failed, 87 passed      # test mới bắt đúng lỗi; mọi test cũ của file vẫn qua trên bản cũ
$ uv run pytest tests/test_t062_alt_prompt.py      # trên bản đã sửa
198 passed in 2.58s

$ uv run pytest tests/test_t062_alt_prompt.py tests/test_soi_loi_t062.py tests/test_ai_images.py \
    tests/test_soi_loi_t050.py tests/test_soi_loi_t051.py -q -p no:cacheprovider -rfEX
813 passed, 15 xfailed in 119.95s (0:01:59)        # 16:36 → 16:38; 0 hỏng, 0 XPASS
                                                    # 15 xfail = dấu cũ của tests/test_soi_loi_t050.py

$ uv run python <script thử ngẫu nhiên C6, ngoài repo>     # như lượt Lá Chắn T-062
42313 kết quả đúng tiền tố, 17687 lần báo «AI không viết được alt»
# 60.000 cặp alt/chú thích: 0–3 tiền tố đủ kiểu (NFD, NBSP, «(AI)», hoa thường) trong đủ loại ngoặc,
# dính dấu câu; thân có HTML, link Markdown, </du_lieu_tham_khao>, ký tự rộng 0, \u202e, NUL, ESC,
# emoji, chữ rất dài; giới hạn 20–200. Mọi kết quả: alt bắt đầu «Minh họa », chú thích «Ảnh minh
# họa (AI)», không quá giới hạn, một dòng, NFC, không «<», thân có chữ, không còn tiền tố lặp,
# chạy lại không đổi. Mọi lỗi là đúng câu «AI không viết được alt…».

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check seo_app/images/alt.py tests/test_soi_loi_t062.py tests/test_t062_alt_prompt.py
3 files already formatted
```

Theo quy tắc mới, toàn bộ `uv run pytest` do Chỉ Huy chạy trên Windows khi gộp.

## Đối chiếu tiêu chí xong

- [x] YC1 · SL-T062-1: `test_alt_without_any_letter_or_digit_is_refused` (18 trường hợp, ảnh AI và ảnh thật), `test_alt_cut_down_to_punctuation_only_is_refused`, `test_caption_without_any_letter_is_left_empty`, `test_ai_caption_with_only_prefix_and_symbols_is_just_the_prefix`; `test_alt_with_a_letter_or_digit_is_kept` («2 cánh», «LED», «x» vẫn được nhận). Soi Lỗi: `test_sl_t062_1_…` 9/9 qua.
- [x] YC2 · SL-T062-2: `test_ai_prefix_in_quotes_or_with_odd_punctuation_is_written_once` (21 kiểu, gồm «Minh họa «Minh họa» cửa cuốn», «Ảnh minh họa (AI): «Ảnh minh họa (AI)» …», «Minh họa!», «Minh họa…», bọc cả câu), `test_quotes_that_are_not_around_the_prefix_are_kept` (7), `test_real_photo_alt_keeps_quotes_and_words`. Soi Lỗi: `test_sl_t062_2_…` 5/5 qua.
- [x] YC3 · SL-T062-3: `test_ai_prefix_is_removed_before_cutting_alt` (4, có `max_chars = 20`), `test_ai_prefix_is_removed_before_cutting_caption`, `test_final_period_does_not_cost_the_last_word`, `test_suggest_alt_with_project_rules_keeps_whole_body_after_ai_written_prefix` (qua `suggest_alt`, quy tắc thật, mặc định 125). Soi Lỗi: `test_sl_t062_3_…` 4/4 qua.
- [x] YC4 · C6: mọi test C6 cũ qua (`test_t062_alt_prompt.py` nhóm YC5/C6; `test_soi_loi_t062.py::test_ai_image_alt_and_caption_always_start_with_prefix` 19/19, xem Rủi ro mục 1); thêm `test_c6_prefix_written_exactly_once_whatever_ai_writes` (26 kiểu × giới hạn 20, 29, 125: đúng **một** «minh họa» ở alt và chú thích); thử ngẫu nhiên 60.000 lần. 3 dấu `xfail` đã gỡ, thân test không đổi.
- [x] Test liên quan qua (813), ruff sạch.
- [x] Báo cáo nộp tại `docs/team/reports/T-068-tho-may.md`.

## Rủi ro và điểm cần chú ý

1. **Hai test của Soi Lỗi mâu thuẫn nhau, tôi đã chỉnh test C6 (ngoài phần «gỡ xfail» phiếu cho phép), cần Chỉ Huy / Lá Chắn xác nhận.** `test_sl_t062_1_alt_without_any_letter_is_refused` đòi alt «???», «🔥🔥» của ảnh AI phải báo lỗi; còn `test_ai_image_alt_and_caption_always_start_with_prefix` (C6) lại đưa đúng hai alt đó vào và đòi ra alt có tiền tố. Không code nào qua được cả hai. Tôi theo yêu cầu 1 của phiếu và sửa test C6 tối thiểu (`tests/test_soi_loi_t062.py:480-488`): với đầu vào không có chữ hay số, test đòi `AIError` «không viết được alt», rồi kiểm chú thích kỳ lạ đó cùng một alt có chữ, đủ mọi điều kiện cũ (tiền tố, giới hạn, NFC, một dòng). 15 trường hợp còn lại của test C6 giữ nguyên điều kiện. Bảo đảm C6 (không bao giờ có alt ảnh AI thiếu tiền tố) không yếu đi: báo lỗi nghĩa là không có alt nào được dùng. Nếu Chỉ Huy muốn cách khác (ví dụ Soi Lỗi tự sửa test), chỉ cần đổi khối 7 dòng đó.
2. **Đổi hành vi nhỏ cho ảnh thật** (do đổi thứ tự cắt, không phải yêu cầu riêng): alt dài đúng giới hạn + 1 dấu chấm trước đây mất chữ cuối, nay giữ («Cổng sắt hai cánh đỏ.» ở giới hạn 20). Alt ảnh thật chỉ có dấu câu hay biểu tượng nay báo lỗi, chú thích như vậy để trống. Mọi test cũ của ảnh thật vẫn qua.
3. Chú thích ảnh AI ở `caption_max_chars = 20` (mức thấp nhất bộ đọc cho phép) chỉ còn 1 ký tự cho phần thân, nên ra «Ảnh minh họa (AI): c» (cắt giữa chữ). Có từ trước T-068 (Soi Lỗi T-062 và Lá Chắn đều đã thấy với giới hạn 20), không thuộc 3 lỗi của phiếu; xem Đề xuất.
4. Tiền tố viết dính chữ số («Minh họa2 cánh») không được nhận là tiền tố (giữ ranh giới từ như code cũ, tránh bỏ nhầm). Đây là AI gõ sai; người dùng vẫn duyệt từng alt ở T-056.
5. Không gọi mạng, không dùng khóa thật; script thử ngẫu nhiên nằm ngoài repo, không thêm vào test.

## Đề xuất

- **Chỉ Huy:** xác nhận cách chỉnh test C6 ở Rủi ro mục 1 khi giao Soi Lỗi / Lá Chắn rút gọn. Sau đó T-056 gộp được về mặt điều kiện 2 của Lá Chắn T-062.
- **Ngòi Bút (khi có phiếu):** cân nhắc nâng mức thấp nhất của `caption_max_chars` (ví dụ 40) hoặc ghi chú trong `config/content.toml` rằng chú thích ảnh AI tốn 19 ký tự cho tiền tố (Rủi ro mục 3). Cùng G5 của Soi Lỗi T-062 (câu cấm mở đầu «Ảnh» chỉ áp cho alt).
- **Soi Lỗi (rút gọn):** điểm nên xem: `alt.py:363-386` (`_strip_ai_prefix`: ngoặc, ngoặc bọc cả câu), `:433-446` (thứ tự bỏ tiền tố → cắt → ghép).

## Câu hỏi cho chủ dự án

Không có.

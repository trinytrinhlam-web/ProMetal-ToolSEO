# Báo cáo T-036 · Soi Lỗi: kiểm thử meta title, meta description, slug, AI gợi ý meta

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-036](../tickets/T-036-meta-title-description-slug.md) |
| Ngày nộp | 2026-10-16 |
| Kết quả | Hoàn thành. Kết luận: **ĐẠT CÓ ĐIỀU KIỆN** (phải sửa SL-T036-1 trước khi gộp) |

## Tóm tắt (cho chủ dự án)

Phần đếm độ dài, slug, kiểm trùng và lọc gợi ý AI chạy đúng ở hầu hết trường hợp: chữ dán từ Mac đếm đúng, đuôi "| Pro-Metal" chỉ gắn khi còn chỗ, bài trùng hệt bị chặn, gợi ý AI có link/giá/cụm sáo bị bỏ.

Tìm thấy **1 lỗi cần sửa ngay**: một thẻ HTML giấu ký tự vô hình (ví dụ `<` + ký tự rộng 0 + `script>`) qua được bước kiểm meta người dùng gõ, và chữ đem gửi đi lại thành thẻ thật. Còn 7 lỗi nhỏ (giá viết bằng chữ như "năm trăm nghìn" lọt bộ lọc, đuôi thương hiệu lặp 2 lần chỉ gỡ 1 lần…) và 1 điểm cần chủ dự án quyết: tiêu đề ngắn kiểu "Sửa cửa cuốn quận 7" và "…quận 8" bị báo "rất giống".

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t036.py` | Mới: 167 test (144 qua, 23 `xfail(strict=True)` cho SL-T036-1…6 và 9; SL-T036-8 ghi hành vi hiện tại). Provider giả, không gọi mạng |
| `docs/team/reports/T-036-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng.

## Bằng chứng

```
$ uv run pytest tests/test_soi_loi_t036.py
144 passed, 23 xfailed in 10.94s

$ uv run pytest
1 failed, 4574 passed, 4 skipped, 40 xfailed, 1 warning in 216.75s
FAILED tests/test_soi_loi_t028.py::test_other_threads_reading_environment_never_fail
(chạy riêng 3 lần: cả 3 lần qua)

$ uv run ruff check .
All checks passed!
```

## Đối chiếu yêu cầu kiểm thử

| # | Hạng mục | Kết quả | Test |
|---|---|---|---|
| 1 | Đếm NFC (NFD từ Mac, ký tự vô hình, xuống dòng, tab) | Đạt | `test_invisible_chars_not_counted`, `test_nfd_*`, `test_*_thresholds_with_accented_letters` |
| 1 | Ngưỡng Nên / Cảnh báo / Chặn (biên 29/30/65/66, 69/70/160/161) | Đạt | như trên |
| 1 | Chặn `%%`, thẻ HTML | **Lỗi SL-T036-1** (thẻ chen ký tự vô hình) | `test_html_hidden_by_invisible_char_blocked` |
| 1 | Slug: không dấu, ≤ 60, bỏ từ nối cuối, chữ `đ` | Đạt | `test_slug_*`, `test_check_slug_cases` |
| 2 | Đuôi thương hiệu: thêm khi còn chỗ, không hai lần, gỡ biến thể, cấu hình sai → mặc định, rỗng → tắt | Đạt phần chính; **SL-T036-2, 3, 4** | `test_brand_*`, `test_bad_brand_config_uses_default_no_error` |
| 3 | Trùng hệt Chặn, giống Cảnh báo, slug trùng Chặn, bỏ bài đang sửa, hoa/thường, có/không dấu | Đạt | `test_exact_duplicate_title_blocked`, `test_current_post_skipped_everywhere`, `test_slug_duplicate_blocked_variants` |
| 3 | Tiêu đề rất ngắn (Dice 0,8) | Cần quyết: **SL-T036-8** | `test_short_titles_*` |
| 4 | Gợi ý AI có link, URL, email, `javascript:`, tên miền trần, chữ toàn khổ, giá, cụm cấm, `%%`, thiếu từ khóa → bỏ | Đạt phần chính; **SL-T036-5, 6, 7** | `test_bad_title_part_dropped`, `test_bad_description_part_dropped` (18 mẫu, cả NFD) |
| 4 | Hỏng hết → `AIError` tiếng Việt | Đạt | `test_all_bad_*_raise_vietnamese`, `test_empty_keyword_raises_vietnamese` |
| 4 | Viết lại riêng title / description không đụng phần kia | Đạt | `test_rewrite_*_only_*` |
| 4 | Thẻ khung giả (`</bai_viet>`, `</de_bai>`, `</ho_so_doanh_nghiep>`, toàn khổ) trong từ khóa, tiêu đề, bài, meta đang có | Đạt | `test_fake_frames_in_user_data_neutralized` |
| 5 | Tốc độ: danh sách bài lớn, chữ dài | Đạt với dữ liệu người dùng; **SL-T036-9** với gợi ý AI chuỗi dài | `test_*_linear_*` |
| 6 | Trang Soạn bài, `tests/test_app_pages.py` | Đạt (không đổi `app/**`) | bộ test toàn repo |

## Lỗi tìm thấy

### SL-T036-1 · Cao · Thẻ HTML giấu ký tự vô hình qua được `check_title` / `check_description`

- Tái hiện: `check_title("Cửa sắt bị xệ <​script>alert(1) cho nhà phố bền đẹp")` (cũng vậy với U+00AD, U+2060, U+FEFF).
- Mong đợi: `level == Chặn`.
- Thực tế: `level == Nên`, `value == "Cửa sắt bị xệ <script>alert(1) cho nhà phố bền đẹp"`. Báo cáo Thợ Máy dặn T-042 "gửi đi đúng `value`", nên thẻ thật sẽ đi tới WordPress.
- Nguyên nhân: `_check_text` gọi `has_html(raw)` trên chữ **gốc**, còn `value` là chữ **đã bỏ ký tự vô hình**. Sửa: kiểm `has_html(value)` (hoặc cả hai). Đường AI không dính lỗi này vì `_final` gọi lại `check_title` trên chữ đã chuẩn hóa (`test_hidden_tag_in_ai_title_dropped`).
- Test: `test_html_hidden_by_invisible_char_blocked` (4 trường hợp).

### SL-T036-2 · Thấp · Đuôi thương hiệu lặp hai lần chỉ gỡ một lần

- Tái hiện: `with_brand("Cửa sắt bị xệ: dấu hiệu sớm | Pro-Metal | Pro Metal")`.
- Mong đợi: còn một " | Pro-Metal". Thực tế: "… | Pro-Metal | Pro-Metal" (`_BRAND_TAIL` chỉ ăn một lần). Tiêu đề cũ trên site có thể đã bị gắn đuôi hai lần.
- Test: `test_brand_repeated_twice_collapsed`.

### SL-T036-3 · Thấp · Hậu tố tùy chỉnh bị gắn thêm lần nữa

- Tái hiện: `with_brand("Cửa sắt bị xệ · Cơ khí ABC", suffix="· Cơ khí ABC")` → "… · Cơ khí ABC · Cơ khí ABC". `strip_brand` chỉ biết dạng "Pro-Metal", nên khi đổi `BRAND_SUFFIX` hoặc truyền hậu tố khác, bấm gắn lại sẽ lặp. Tương tự `suffix="Pro-Metal"` (không dấu phân cách) → "… Pro-Metal Pro-Metal".
- Test: `test_custom_brand_not_twice`.

### SL-T036-4 · Thấp · Hậu tố lạ

- `suffix="​"` (chỉ ký tự vô hình): `value.strip()` không coi là rỗng, ra hậu tố " " → title có dấu cách cuối. Test `test_invisible_only_brand_no_trailing_space`.
- Biến thể "| Pro‑Metal" (U+2011), "| Pro–Metal" (gạch ngang giữa tên), "| Pro-Metal." không được gỡ. Test `test_brand_odd_hyphen_variants_stripped`.

### SL-T036-5 · Trung bình · Giá viết bằng chữ, viết tắt, toàn khổ lọt bộ lọc gợi ý AI

- Tái hiện: `mentions_price("Cửa sắt bị xệ sửa chỉ năm trăm nghìn tại nhà", "cửa sắt bị xệ")` → `False`. Cũng lọt: "hai triệu đồng", "vài trăm ngàn", "1tr5", "５００ｋ" (chữ số và chữ toàn khổ: không NFKC trước khi soát giá, khác `has_link`), "500 đô".
- Mong đợi: `True` (BAN-GIAO 7.4: không nêu giá dưới mọi dạng).
- Test: `test_price_in_words_dropped` (6 trường hợp).

### SL-T036-6 · Thấp · Tên miền trần đuôi ngoài danh sách lọt

- "bit.ly/abc", "pro-metal.shop", "abc.store/x", "abc.asia" không bị coi là link (danh sách đuôi cố định). Meta là chữ thuần, không thành link bấm được, nên rủi ro chỉ là quảng cáo trang khác trong meta.
- Test: `test_bare_domain_other_tld_dropped`.

### SL-T036-7 · Thấp · Thực thể HTML và «％％» toàn khổ được nhận

- `accept_ai_title("Cửa sắt bị xệ &amp; cách sửa tại nhà nhanh", …)` được nhận nguyên "&amp;". Nếu SiteSEO/WordPress escape lại khi in, người tìm thấy chữ "&amp;" trên Google. "％％post_title％％" (toàn khổ) cũng được nhận; SiteSEO chỉ hiểu `%%` ASCII nên không thành biến, nhưng là chữ rác. Không viết xfail (chờ T-042 xác minh SiteSEO in meta thế nào).

### SL-T036-8 · Cần quyết · Dice 0,8 với tiêu đề ngắn

- "Sửa cửa cuốn quận 8" so với bài "Sửa cửa cuốn quận 7" → **Cảnh báo** "rất giống" (5 từ, chung 4, Dice = 0,8). "Cửa sắt đẹp" so với "Cửa sắt" → Cảnh báo. Không báo nhầm với: "Cửa cuốn bị kêu"/"…kẹt" (0,75), "Bản lề cửa sắt"/"Khóa cửa sắt", "Cửa kéo Đài Loan"/"Cửa kéo".
- Chỉ là Cảnh báo, không chặn. Nếu site có nhiều trang theo quận, người dùng sẽ thấy cảnh báo ở mọi trang. Đề xuất: giữ (2 trang chỉ khác số quận đúng là dễ tranh nhau trên Google), hoặc cho tiêu đề ≤ 5 từ dùng ngưỡng cao hơn. Test `test_short_titles_dice_edge_cases_documented` ghi hành vi hiện tại.

### SL-T036-9 · Trung bình · Lọc gợi ý AI chạy bình phương với chuỗi dài không có dấu cách

- Tái hiện: `accept_ai_description("1" * 16000, "a")` mất khoảng 4,6 giây CPU; "a." × 8000 khoảng 0,8 giây; "a" × 16000 khoảng 1,5 giây. Gấp 4 độ dài thì chậm khoảng 15 lần.
- Nguyên nhân: `_PRICE` (`\d[\d.,]*\s*…`) và `_LINK` (`[a-z][a-z0-9+.\-]*://`, `\b[\w-]+\.(?:com|…)`) quay lui ở mỗi vị trí; `_ai_text` chạy các biểu thức này **trước** khi kiểm độ dài (`_final`).
- Chỉ xảy ra khi AI bị lừa trả chuỗi dài (tối đa khoảng 8.000 ký tự với `max_tokens = 2000`), nên vài giây treo, không treo hẳn. Sửa đơn giản: bỏ gợi ý dài quá `warn_max` ngay đầu `_ai_text`.
- Test: `test_ai_filter_linear_on_long_runs` (3 dạng chuỗi). Dữ liệu người dùng (`check_*`, `make_slug`, kiểm trùng với 2.000 bài và chữ dài) đều tuyến tính.

## Rủi ro và điểm cần chú ý

- Test hỏng ở lần chạy toàn bộ là test chập chờn đã biết của T-028 (chạy đua nhiều luồng trong `seo_app/ai`, đã ghi ở T-032 và đưa vào T-034). T-036 không đụng `seo_app/ai`; chạy riêng 3 lần đều qua.

- Lá Chắn: SL-T036-1 thuộc A2/U1 (chữ gửi WordPress có thẻ). Khung dữ liệu (A1) đạt: thẻ khung giả ở cả 5 chỗ người dùng nhập (từ khóa, tiêu đề, bài, meta title đang có, meta description đang có) đều bị vô hiệu, kể cả dạng toàn khổ.
- T-041: câu báo trùng chứa tên bài từ site (có thể có thẻ), giao diện phải escape (`test_duplicate_name_from_site_is_kept_as_data`).

## Đề xuất

- Thợ Máy sửa SL-T036-1 (bắt buộc), SL-T036-5 và SL-T036-9 (nên làm trong phiếu này, vài dòng); SL-T036-2, 3, 4, 6 có thể để phiếu lỗi Thấp sau.
- Khi sửa xong, đổi `xfail` tương ứng thành test thường (strict nên sẽ báo XPASS).

## Câu hỏi cho chủ dự án

- SL-T036-8: hai tiêu đề chỉ khác số quận ("…quận 7" / "…quận 8") có nên bị **Cảnh báo** "rất giống" không? Đề xuất: **Có** (giữ như hiện tại).

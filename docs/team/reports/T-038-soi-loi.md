# Báo cáo T-038 · Soi Lỗi: kiểm thử schema FAQPage

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Opus 5.5 |
| Phiếu | [T-038](../tickets/T-038-schema-faqpage-kiem-hop-le.md) |
| Ngày nộp | 2026-10-16 |
| Kết quả | **Đạt có điều kiện** |

## Tóm tắt (cho chủ dự án)

Phần dựng và kiểm schema hỏi đáp chạy đúng phiếu: không dữ liệu nào đóng được thẻ `</script>`, các loại schema bị cấm đều bị chặn, địa chỉ giả mạo tên miền đều bị chặn, tốc độ tăng tuyến tính theo độ dài bài. Tìm thấy 2 lỗi, đều không chặn việc gộp: một lỗi hiếm gặp (ký tự hỏng lọt qua bộ kiểm), và một điểm sẽ gây khó dùng khi làm bước SEO (T-041): câu trả lời trong bài có chữ **in đậm** thì phải bỏ dấu Markdown ở cả hai phía trước khi so.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t038.py` | Mới: 132 test (127 qua, 5 `xfail(strict=True)` cho SL-T038-1, SL-T038-2) |

Không sửa code ứng dụng.

## Bằng chứng

```
$ uv run pytest tests/test_soi_loi_t038.py tests/test_onpage_schema.py -q -W error
209 passed, 5 xfailed in 1.19s

$ uv run pytest -q
4867 passed, 4 skipped, 21 xfailed, 1 warning in 245.42s (Linux)
(cảnh báo pydantic có sẵn từ trước, không đến từ T-038: chạy riêng 2 file T-038 với -W error vẫn sạch)

$ uv run ruff check .
All checks passed!
```

## Đối chiếu tiêu chí phiếu

- [x] `@context` đúng `https://schema.org`; `http://`, có `/` cuối, dạng mảng, `None` đều bị chặn (`test_bad_context_blocked`).
- [x] `@type`: `HowTo` bị chặn mọi dạng (`" HowTo "`, `howto`, `HowToStep`, URL schema.org), vì code dùng danh sách **cho phép**. `@type` dạng mảng, dict, rỗng, số, có khoảng trắng thừa đều bị chặn (`test_howto_variants_never_allowed`, `test_odd_top_type_values_blocked`).
- [x] Từ chối loại site đã tự xuất ở cả 3 tầng (FAQPage, Question, Answer) (`test_site_owned_types_refused_at_top_and_nested`).
- [x] `extra=forbid`: khóa lạ (`@id`, `name`, `url` trong Question, `author` trong Answer) bị chặn (`test_extra_keys_forbidden_anywhere`).
- [x] `mainEntity`: 0 câu chặn, 20 câu qua, 21 câu chặn; bộ sinh vô hạn vẫn dừng (`test_question_count_bounds`, `test_infinite_pairs_generator_terminates`).
- [x] Không HTML: `</script>`, `<img onerror>`, `<!--`, thực thể `&lt;…&gt;`, `&#60;…`, `&#x3c;…`, ký tự rộng 0 chen trong thẻ, thẻ lồng `<scr<script>ipt>` đều chặn. `a < b`, `<3`, `x <= 3`, `Tom & Jerry`, chữ toàn khổ `＜b＞` vẫn qua đúng.
- [x] Ký tự điều khiển NUL, BEL, ESC, DEL, C1 bị chặn. `\x1f`, `\x0b`, `\x85`, U+2028/2029 Python coi là khoảng trắng nên bị gộp thành dấu cách, không lọt ra JSON (chấp nhận được).
- [x] Giới hạn độ dài đúng biên: câu hỏi 300, trả lời 2.000, bài 500.000 (`test_length_limits`).
- [x] URL `https` và đúng tên miền (mục 4 dưới).
- [x] Khớp nguyên văn (mục 3 dưới).
- [x] Câu báo lỗi không chép lại dữ liệu hoặc URL đầu vào (`test_messages_do_not_echo_url_or_text`).

## Kết quả thử phá

### 2. JSON xuất ra

Dựng thẳng khuôn `FAQPage` (bỏ qua bộ kiểm) với `</script>`, `<!--`, `-->`, `]]>`, `<![CDATA[`, U+2028/2029, `<`/`>`/`&` viết sẵn, `&amp;`, chữ toàn khổ `＜／script＞`, ngoặc kép, gạch ngược; cả trong `url`. Chuỗi ra **không có** `<`, `>`, `&`, U+2028/2029; `json.loads` đọc lại **đúng nguyên** nội dung (`test_payload_never_escapes_script_and_roundtrips`). Qua `build_faq_page` cũng vậy.

Ghi chú (không phải lỗi): `&amp;lt;script&amp;gt;` (thực thể mã hóa hai lần) được qua vì chỉ giải mã một lần. Bỏ mã một lần ra chữ `&lt;script&gt;`, vẫn là chữ thường, không thành thẻ. Chấp nhận được.

### 3. Khớp nguyên văn

- NFD ↔ NFC cả hai chiều: khớp, chữ xuất ra là NFC.
- Khoảng trắng lạ (NBSP, em space, U+3000, tab, xuống dòng, 2 dấu cách): khớp.
- Ký tự vô hình (U+200B, FEFF, 2060, soft hyphen, ZWJ): bỏ đi khi so và **không** có trong JSON.
- Câu hỏi trong tiêu đề `###`, trong đoạn văn, hay trong dòng `**…**`: đều khớp.
- Đổi chữ hoa/thường hoặc diễn đạt lại: bị chặn (đúng "nguyên văn").
- **Bài có định dạng Markdown trong câu trả lời: xem SL-T038-2.**

Nhận xét thêm (đề xuất, không đánh lỗi): so là **chuỗi con**, không theo ranh giới từ. Câu trả lời cụt giữa chữ (ví dụ `"Thường 8–10 nă"`, hay chỉ `"ó"`) vẫn qua. Nguồn cặp hỏi-đáp là code T-041 cắt từ bài nên rủi ro thấp; nếu muốn chắc thì thêm Cảnh báo khi chuỗi khớp không nằm trọn ranh giới từ.

### 4. URL

Qua: `https://suachuacuasat.com/…`, chữ hoa, dấu `.` cuối tên máy, cổng `:443`.
Chặn: `http://`, `www.` khi site không `www` (và ngược lại), `suachuacuasat.com.evil.tld`, `evilsuachuacuasat.com`, có `@` (cả hai phía, kể cả `\@`), `user:pass@`, punycode `xn--…`, chữ có dấu `suachuacuasát.com`, dấu chấm toàn khổ `。`, `%2e`, gạch ngược, `https:` thiếu `//`, `https:///`, `//…`, `javascript:`, cổng lạ, cổng sai dạng, IPv6, khoảng trắng, ký tự đảo chiều U+202E, quá 2.000 ký tự, chưa khai báo `WORDPRESS_URL`.

Ghi chú: `www.` và không `www.` bị coi là khác nhau (đúng thiết kế). Vì `page_url` lấy từ chính WordPress mà `WORDPRESS_URL` trỏ tới, thực tế hai bên sẽ cùng dạng; không gây khó dùng.

Ghi chú: đường dẫn URL có `<script>` (`https://suachuacuasat.com/<script>`) vẫn qua `check_url`. Không nguy hiểm vì JSON đã đổi `<` thành `<`; nêu để Lá Chắn biết.

### 5. Tốc độ

- 20 câu × trả lời ~1.600 ký tự, bài 87k → 437k ký tự: 0,06 s → 0,16 s, tuyến tính. Có test tỉ lệ bằng `tests/timing.py` (`test_build_scales_linearly_with_article_length`).
- Trường hợp xấu nhất cho tìm chuỗi con (bài 499k chữ `a`, 20 câu gần khớp): ~0,17 s.
- Câu hỏi 5 triệu khoảng trắng: ~0,9 s, tuyến tính (chuẩn hóa chạy trước bước đo độ dài; chấp nhận được, dữ liệu này không đến từ người dùng thật).

## Lỗi tìm thấy

### SL-T038-1 · Ký tự thay thế lẻ (surrogate) lọt qua bộ kiểm · Mức: Thấp

- **Tái hiện:** `build_faq_page([(q, "Trả lời \ud800 lỗi.")], article_text=<bài có cùng chuỗi>, site_url=SITE)`.
- **Mong đợi:** bị chặn ("có ký tự lạ"), như ký tự điều khiển.
- **Thực tế:** qua, `json_ld` có `\ud800` nguyên dạng; `json_ld.encode("utf-8")` ném `UnicodeEncodeError`, nên khi T-041 hiện lên Streamlit hoặc gửi đi sẽ lỗi.
- **Gợi ý sửa:** `_has_control` chặn thêm loại `Cs` (có thể cả `Co`, `Cn`). Test: `test_lone_surrogate_blocked` (xfail strict).
- Hiếm: chuỗi Python chỉ có surrogate lẻ khi đọc file sai mã hóa (`surrogateescape`) hoặc lỗi thư viện.

### SL-T038-2 · Câu trả lời chữ thường không khớp bài có `**đậm**`, link, `` `mã` `` · Mức: Trung bình (khó dùng, không phải lỗi an toàn)

- **Tái hiện:** bài viết `Thường **8–10 năm** nếu…`; truyền câu trả lời `Thường 8–10 năm nếu…`.
- **Mong đợi:** khớp (người đọc thấy đúng câu đó trên trang), JSON-LD chứa chữ sạch.
- **Thực tế:** bị chặn "không có nguyên văn trong bài". Muốn qua phải truyền chữ thô có `**`, khi đó JSON-LD chứa luôn `**8–10 năm**`, Google hiển thị dấu sao (`test_bold_answer_raw_markdown_passes_and_leaks_asterisks`).
- **Đánh giá:** prompt viết bài (`seo_app/content/prompts.py`) không cấm in đậm, và các mô hình hay in đậm ý chính trong mục Hỏi đáp (ví dụ `**Có.**`). Nghĩa là nhiều bài sẽ hoặc bị chặn, hoặc ra schema có dấu sao: người dùng sẽ khó dùng nếu T-041 không xử lý.
- **Gợi ý sửa (chọn một):**
  1. Trong T-038: so trên bản đã bỏ định dạng Markdown nội dòng (`**`, `*`, `_`, `` ` ``, `[chữ](url)` → `chữ`) ở **cả** bài lẫn câu trả lời, và xuất chữ đã bỏ định dạng; hoặc
  2. Ghi rõ vào phiếu T-041: bên gọi phải bỏ Markdown nội dòng ở cả hai phía trước khi gọi `build_faq_page`.
  Soi Lỗi nghiêng về cách 1 (một chỗ, có test), nhưng phải giữ được: chữ sau khi bỏ định dạng vẫn qua bộ kiểm HTML.
- Test: `test_plain_answer_matches_markdown_formatted_article` (4 trường hợp, xfail strict).

## Điều kiện để "đạt"

- SL-T038-2 phải được giải quyết **trước hoặc trong T-041** (theo cách 1 hoặc 2 ở trên). Không chặn việc gộp T-038 vì T-038 chưa có chỗ nào dùng.
- SL-T038-1 sửa khi tiện (có thể gộp vào T-041 hoặc phiếu dọn lỗi).

## Rủi ro và điểm cần chú ý

- So chuỗi con không theo ranh giới từ (đề xuất ở mục 3).
- Không kiểm câu trả lời có đúng là của câu hỏi đó trong bài hay không (chỉ kiểm có mặt). Chấp nhận được khi T-041 cắt cặp từ bài bằng code.

## Đề xuất

- Chỉ Huy giao SL-T038-1 (và SL-T038-2 nếu chọn cách 1) cho Thợ Máy; nếu chọn cách 2 thì ghi vào phiếu T-041.

## Câu hỏi cho chủ dự án

Không có.

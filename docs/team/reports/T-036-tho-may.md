# Báo cáo T-036 · Meta title, meta description, slug: kiểm độ dài, kiểm trùng, AI gợi ý

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-036](../tickets/T-036-meta-title-description-slug.md) |
| Ngày nộp | 2026-10-16 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Đã có phần "bộ não" cho bước 4 SEO của trang Soạn bài (chưa có giao diện, chưa ghi lên WordPress):
- Đếm độ dài meta title, meta description đúng kiểu Google thấy (chữ Việt dán từ Mac không còn bị đếm gấp đôi), xếp loại **Nên / Cảnh báo / Chặn**, kèm câu giải thích tiếng Việt.
- Tạo slug không dấu, tối đa 60 ký tự, bỏ từ nối thừa ở cuối ("…-cho", "…-và"); slug anh tự gõ luôn được giữ.
- So với các bài đã có trên site: trùng hệt thì Chặn, rất giống thì Cảnh báo và nêu tên bài bị giống; slug trùng thì Chặn.
- AI gợi ý 3 title, 2 description. Phần mềm tự kiểm từng gợi ý (không link, không giá, không cụm sáo, có từ khóa…) và bỏ gợi ý hỏng. Viết lại riêng title hoặc riêng description được.
- Đuôi "| Pro-Metal" (câu 3 anh chưa trả lời): mặc định **thêm khi còn chỗ** (tổng ≤ 60 ký tự). Muốn bỏ: đổi một hằng số `BRAND_SUFFIX` thành `""`.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/onpage/__init__.py` | Mới, đúng một dòng như phiếu yêu cầu |
| `seo_app/onpage/meta.py` | Mới: chuẩn hóa, đếm, kiểm ngưỡng, hậu tố thương hiệu, slug, kiểm trùng, kiểm gợi ý AI |
| `seo_app/content/prompts.py` | Chỉ thêm: khuôn `MetaSuggestions`, `META_PARTS`, `meta_prompt` |
| `seo_app/content/workflow.py` | Chỉ thêm: import `seo_app.onpage.meta`, hàm `ContentWriter.meta` |
| `config/ai.toml` | Chỉ thêm `[tasks.meta]`: cùng hãng/mô hình với `review`, `effort = "low"`, `max_tokens = 2000` |
| `tests/test_onpage_meta.py` | Mới: 130 test, provider giả, không gọi mạng |

### Cách dùng (cho T-041 giao diện, T-042 ghi WordPress)

- `check_title(s)`, `check_description(s)`, `check_slug(s)` → `FieldCheck(field, value, length, level, messages)`. `value` là chữ đã chuẩn hóa: **gửi đi đúng `value`**, đếm hiện trên giao diện là `length`.
- `make_slug(text, given=None)`; `with_brand(title, suffix=None)`; `strip_brand(title)`.
- `check_title_duplicates(title, posts, current_id)`, `check_description_duplicates(...)`, `check_slug_duplicates(...)`, với `posts` là danh sách `SitePost(id, title, meta_title, meta_description, slug)`. T-037 chỉ cần đổi dữ liệu cache sang `SitePost`.
- `worst([c.level for c in checks])` cho mức chung.
- `ContentWriter.meta(keyword, title, parts, which="both"|"title"|"description", current_title, current_description, brand_suffix)` → `MetaSuggestions(titles, descriptions)`; phần không yêu cầu trả về `[]`.

## Bằng chứng

```
$ uv run pytest
4431 passed, 4 skipped, 17 xfailed, 1 warning in 194.10s (0:03:14)

$ uv run pytest tests/test_onpage_meta.py
130 passed in 0.90s

$ uv run ruff check .
All checks passed!
```

Commit trên `team/T-036`: `817cfcf` (phần 1), `bc244c0` (phần 2), `f6eeaed` (phần 3), cộng commit báo cáo này.

## Đối chiếu tiêu chí xong

- [x] Kiểm độ dài, slug, trùng: có test (`test_nfd_*`, `test_title_thresholds`, `test_description_thresholds`, `test_html_is_blocked`, `test_double_percent_is_blocked`, `test_make_slug_*`, `test_check_slug`, `test_exact_duplicate_*`, `test_similar_title_warns_with_post_name`, `test_slug_duplicate_blocked`, `test_current_post_is_skipped`, `test_duplicate_check_is_linear_in_post_count`)
- [x] AI gợi ý meta, kiểm từng gợi ý: có test với provider giả (`test_ai_meta_*`, `test_bad_ai_title_dropped`, `test_bad_ai_description_dropped`, `test_ai_title_keyword_without_accents_accepted`, `test_injection_in_article_is_framed`, `test_injection_in_keyword_is_framed`, `test_ai_returns_fake_frames_and_commands`)
- [x] `uv run pytest`, `uv run ruff check .` sạch
- [x] Báo cáo này

## Quyết định đã đưa ra (trong phạm vi phiếu)

1. **Ngưỡng ba mức.** Đúng bảng mục 5.1. Khoảng giữa (title 30–49 hoặc 61–65; description 70–119 hoặc 156–160) vẫn là **Nên**, kèm lời nhắc "hơi ngắn / hơi dài", vì bảng chỉ định nghĩa Cảnh báo ngoài 30/65 và 70/160.
2. **"Trong ngưỡng Chặn" với gợi ý AI** hiểu là: không bị Chặn **và** độ dài nằm trong ngưỡng Cảnh báo (title 30–65 sau khi gắn hậu tố, description 70–160). AI viết lệch độ dài thì gợi ý bị bỏ; người dùng tự gõ thì chỉ Cảnh báo.
3. **Gợi ý AI chỉ được nhận khi `clean_ai_text` không đổi chữ** (U1), để chữ được đếm chính là chữ được gửi đi. Gợi ý đã được kiểm không link, không thẻ nên thực tế không bao giờ khác.
4. **Hậu tố thương hiệu**: `BRAND_SUFFIX = " | Pro-Metal"` (đổi 1 chỗ). Tham số `suffix`/`brand_suffix`: `None` hoặc cấu hình sai (không phải chữ, có thẻ, có `%%`, dài > 25) → dùng mặc định, không báo lỗi; chữ rỗng → không gắn. Mọi dạng cũ (" | Pro Metal", " - Pro-Metal", "– ProMetal"…) được bỏ rồi gắn lại một dạng thống nhất. AI được dặn **không** tự gắn thương hiệu.
5. **Kiểm trùng**: chuẩn hóa NFC, chữ thường, bỏ hậu tố thương hiệu, bỏ dấu câu, **giữ dấu** khi so trùng hệt ("cửa" ≠ "của"); "giống nhiều" = hệ số Dice trên tập từ **không dấu** ≥ `SIMILARITY_WARN = 0.8`. Meta title so với cả meta title lẫn tiêu đề bài của bài khác (SiteSEO dùng tiêu đề bài khi meta trống). Description chỉ so với description (bài để trống thì bỏ qua). Slug so sau khi giải mã `%` và bỏ `/`.
6. **Slug**: từ nối cuối xét trên chữ **có dấu** (danh sách `SLUG_TRAILING_STOPWORDS`), vì bỏ dấu thì "của" và "cửa" đều là "cua". Slug người dùng đưa vào chỉ được chuyển không dấu, không cắt, không bỏ từ.
7. **`ContentWriter.meta`**: phần được yêu cầu mà mọi gợi ý đều hỏng → `AIError` tiếng Việt (chế độ "both": một trong hai phần hỏng hết cũng báo lỗi, để giao diện luôn nhận đủ phần đã yêu cầu).
8. **Không nêu giá**: chặn số tiền (`200.000đ`, `500k`, `3 triệu`…), ký hiệu tiền, "giá rẻ/tốt/chỉ/từ…", "rẻ", "đắt", "bảng giá", "giảm giá", "khuyến mãi", "miễn phí", "ưu đãi", "trọn gói". "Báo giá" thì cho phép (BAN-GIAO 7.4: hướng khách gửi ảnh qua Zalo để báo giá). Từ khóa chính được bỏ ra trước khi soát giá, để từ khóa kiểu "báo giá cửa sắt" không làm hỏng mọi gợi ý.

## Rủi ro và điểm cần chú ý

- **Soi Lỗi**: bộ dò link/giá là danh sách mẫu, có thể bắt nhầm hoặc sót (ví dụ tên miền đuôi lạ, giá viết bằng chữ "hai trăm nghìn"). Bắt nhầm chỉ làm bỏ một gợi ý; nên thử thêm cách viết giá/link lạ. Ngưỡng Dice 0,8 nên thử với tiêu đề ngắn (3–4 từ dễ chạm 0,8).
- **Soi Lỗi**: test tốc độ kiểm trùng dùng `tests/timing.py` với 400 / 1.600 bài.
- **Lá Chắn (A1)**: từ khóa và meta đang có nằm trong khung `<de_bai>`, bài trong `<bai_viet>`, hồ sơ trong `<ho_so_doanh_nghiep>` (system prompt), đều qua `_block` / `_neutralize`. `DATA_RULES` vẫn nằm trong system prompt; `<de_bai>` không có trong câu liệt kê của `DATA_RULES` nên lời dặn meta tự ghi rõ khung đó là dữ liệu.
- **Lá Chắn (A2)**: AI không có công cụ; mọi gợi ý qua `strip_tags`-check, NFC, link, `%%`, cụm cấm, giá, từ khóa, ngưỡng, `clean_ai_text`.
- **U1 cho giao diện (T-041)**: câu báo trùng có chứa **tiêu đề bài lấy từ site** (dữ liệu chưa tin cậy). Giao diện phải escape khi hiện.
- **Giai đoạn 5 / T-042**: `normalize_meta` bỏ mọi ký tự loại Cf, kể cả U+200B mà `break_autolinks` chèn, nên meta gửi đi không mang ký tự ngắt.
- Vòng import: `workflow.py` → `seo_app.onpage.meta` → `seo_app.content.rules`. Dùng `from seo_app.onpage import meta as onpage_meta` (truy cập thuộc tính lúc chạy) nên import theo thứ tự nào cũng chạy; đã thử cả hai thứ tự.

## Đề xuất

- T-038 (Ngòi Bút): rà lời dặn `meta_prompt` cho tự nhiên; nếu đưa ngưỡng và hậu tố vào `config/content.toml` mục `[meta]`, đọc bằng `resolve_brand_suffix` (đã chịu được cấu hình sai).
- T-041: dùng `FieldCheck.length` thay `len(S.meta_title)` thô ở `app/views/write.py`.

## Câu hỏi cho chủ dự án

Không có câu mới. Câu 3 (đuôi "| Pro-Metal") vẫn chờ; phần mềm đang chạy theo phương án A và đổi được bằng một hằng số.

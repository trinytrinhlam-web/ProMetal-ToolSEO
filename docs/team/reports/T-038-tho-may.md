# Báo cáo T-038 · Schema: dựng và kiểm FAQPage không cần mạng

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Opus 5.5 |
| Phiếu | [T-038](../tickets/T-038-schema-faqpage-kiem-hop-le.md) |
| Ngày nộp | 2026-10-16 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Phần mềm đã tự dựng được dữ liệu cấu trúc **FAQPage** (hỏi đáp) từ mục Hỏi đáp của bài, và tự kiểm nó hợp lệ mà không cần mạng. Câu hỏi/trả lời phải có nguyên văn trong bài, không được chứa thẻ HTML, và chuỗi JSON xuất ra không thể "thoát" khỏi thẻ `<script>`. Chưa đưa gì lên website; giao diện chưa đổi (bước SEO dùng ở T-041).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/onpage/__init__.py` | Mới, đúng một dòng, y hệt T-036 (đã `diff` với `origin/team/T-036`) |
| `seo_app/onpage/schema.py` | Mới: khuôn pydantic `FAQPage`/`Question`/`Answer` (`extra="forbid"`, `strict`), `build_faq_page`, `validate_faq_page`, `check_schema_type`, `check_url`, `normalize_text`, `to_json_ld` |
| `tests/test_onpage_schema.py` | Mới: 82 test, chỉ dữ liệu giả, không gọi mạng |

## Cách dùng

```python
result = build_faq_page(
    [(cau_hoi, tra_loi), ...],
    article_text=bai_markdown,
    site_url=settings.wordpress_url,   # truyền vào, hàm không đọc .env
    page_url=None,                     # tùy chọn
)
result.blocked      # True nếu có lỗi mức Chặn → page, json_ld = None
result.issues       # tuple[Issue(level=Level.WARN|BLOCK, message="…tiếng Việt…")]
result.json_ld      # chuỗi JSON an toàn để đặt trong <script type="application/ld+json">
```

## Bằng chứng

```
$ uv run pytest tests/test_onpage_schema.py -q
82 passed

$ uv run pytest -q
4740 passed, 4 skipped, 16 xfailed, 1 warning in 207.27s (Linux)

$ uv run ruff check .
All checks passed!
```

## Đối chiếu tiêu chí xong

- [x] Khuôn pydantic `extra="forbid"`; AI không viết JSON, code dựng từ cặp hỏi-đáp (`schema.py` lớp `FAQPage`, `build_faq_page`; test `test_pydantic_models_forbid_extra`, `test_validate_rejects_extra_keys`)
- [x] `@context` đúng `https://schema.org` (`test_validate_rejects_bad_context`)
- [x] Chặn `HowTo`; từ chối loại site đã lo: Article, BlogPosting, NewsArticle, BreadcrumbList, LocalBusiness, HomeAndConstructionBusiness, Organization — hằng số `SITE_OWNED_TYPES` (`test_site_owned_types_refused`, `test_howto_refused`, `test_validate_rejects_bad_top_type`, `test_validate_rejects_howto_nested`)
- [x] `mainEntity` ≥ 1, mỗi câu có `name` và `acceptedAnswer.text` không rỗng (`test_validate_rejects_bad_main_entity`, `test_empty_question_or_answer_blocked`)
- [x] Không thẻ HTML, kể cả dạng thực thể `&lt;script&gt;` (`test_html_in_question_or_answer_is_blocked`); ký tự điều khiển bị chặn (`test_control_characters_are_blocked`)
- [x] Giới hạn: tối đa 20 câu, câu hỏi 300, trả lời 2.000, URL 2.000 ký tự (`test_too_many_questions_blocked`, `test_too_long_answer_blocked`)
- [x] URL: `https://`, đúng tên máy của `WORDPRESS_URL` (tham số), không `@`/tài khoản, không cổng lạ (`test_url_bad_blocked`, `test_build_with_foreign_url_blocked`)
- [x] Khớp nguyên văn với bài sau NFC + gộp khoảng trắng (`test_question_not_in_article_is_blocked`, `test_answer_paraphrased_is_blocked`, `test_whitespace_and_nfd_are_normalized_for_matching`)
- [x] Không thể đóng `</script>`: `<`, `>`, `&` (và U+2028/2029) thành `<`, `>`, `&`; `json.loads` đọc lại đúng nội dung (`test_json_output_cannot_close_script_tag`, `test_to_json_ld_escapes_even_if_model_built_directly`, `test_build_ok_and_json_roundtrip`)
- [x] Kết quả dạng Chặn / Cảnh báo, câu tiếng Việt, không chép lại dữ liệu đầu vào (`test_messages_never_echo_input`). Không import code T-036
- [x] Chỉ `json` + `pydantic` (và code sẵn có: `strip_tags`, `IGNORABLE_NOT_CF`); không thư viện mới (D1); test không gọi mạng (D3)

## Rủi ro và điểm cần chú ý

- **Khớp nguyên văn là so chuỗi con trên bài thô** (Markdown). Nếu câu trả lời trong bài có định dạng (`**đậm**`, link, gạch đầu dòng) thì phải truyền đúng chữ đó, hoặc bên gọi (T-041) bỏ định dạng Markdown của cả bài lẫn câu trả lời trước khi gọi. Hiện **không** tự bỏ Markdown để giữ đúng "nguyên văn".
- Bộ dò HTML dùng `strip_tags` sẵn có nên **chặt**: `</ x`, `<!` cũng bị coi là thẻ (có test). `a < b`, `x <= 3` vẫn qua.
- `www.suachuacuasat.com` **khác** `suachuacuasat.com` (so đúng tên máy, như thiết kế 4.1). Nếu site dùng `www` thì `WORDPRESS_URL` phải ghi có `www`.
- Cảnh báo (không chặn): câu hỏi trùng nhau, câu hỏi không kết thúc bằng "?".
- Kiểu `Level` của T-038 chỉ có `WARN`/`BLOCK`, giá trị chuỗi (`"canh_bao"`, `"chan"`) trùng T-036 nhưng là lớp riêng (phiếu yêu cầu không phụ thuộc T-036). Khi gộp cả hai, có thể gom về một chỗ trong phiếu sau.

## Đề xuất

- T-041 (bước SEO): hiện `json_ld` trong `st.code(..., language="json")` (không dùng `unsafe_allow_html`), và hiện `issues` bằng chữ thường.
- Khi chủ dự án muốn đưa FAQPage lên site: theo cách "d" (gửi dữ liệu hỏi-đáp, site tự dựng), phiếu riêng qua Lá Chắn.

## Câu hỏi cho chủ dự án

Không có.

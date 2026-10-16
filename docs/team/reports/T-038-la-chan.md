# Biên bản bảo mật T-038 · Schema: dựng và kiểm FAQPage không cần mạng

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **Opus 5.5 (Opus tạm**, chủ dự án duyệt vì Fable bị giới hạn tới 01/11; kiểm lại bằng Fable sau 01/11) |
| Phiếu được kiểm | [T-038](../tickets/T-038-schema-faqpage-kiem-hop-le.md) |
| Phạm vi | `git diff origin/main...team/T-038` tại `365251c`: `seo_app/onpage/__init__.py`, `seo_app/onpage/schema.py`, `tests/test_onpage_schema.py`, `tests/test_soi_loi_t038.py`, 2 báo cáo. Đọc thêm code dùng chung: `seo_app/sanitize.py` (`strip_tags`), `seo_app/content/rules.py` (`IGNORABLE_NOT_CF`) |
| Ngày | 2026-10-16 |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** |

## Tóm tắt (cho chủ dự án)

Phần dựng schema hỏi đáp an toàn: tôi thử hơn 30 kiểu dữ liệu độc (thẻ `</script>`, chú thích HTML, chữ toàn khổ, thực thể HTML, ký tự xuống dòng lạ…) và không kiểu nào thoát được khỏi khối JSON để chèn mã vào trang; địa chỉ giả mạo tên miền đều bị chặn. Chưa có chỗ nào trong app dùng phần này, và nó không gửi gì lên website. Còn 2 lỗi nhỏ (Soi Lỗi đã nêu) cùng 1 lưu ý của tôi; tôi đồng ý chuyển sang phiếu T-041, với điều kiện sửa xong **trước khi** giao diện dùng tới schema.

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| 1 (= SL-T038-1) | Thấp | Ký tự surrogate lẻ (`Cs`) lọt bộ kiểm. Tôi xác nhận thêm: ký tự riêng (`Co`, ví dụ U+E000) và ký tự chưa gán (`Cn`, ví dụ U+0378) cũng lọt vào `json_ld` | `seo_app/onpage/schema.py:137-139` | Bài đọc từ file sai mã hóa có `\ud800` → `build_faq_page` cho qua → `json_ld.encode("utf-8")` ném `UnicodeEncodeError` khi T-041 hiện lên Streamlit. Hậu quả: trang lỗi (không chèn được mã, không lộ gì). `Co`/`Cn` chỉ là chữ rác, không chạy được | `_has_control` chặn thêm `Cs`, `Co`, `Cn` (giữ câu báo "có ký tự lạ", không chép ký tự) |
| 2 (= SL-T038-2) | Thấp về bảo mật (Trung bình về dễ dùng, theo Soi Lỗi) | Khớp nguyên văn so trên Markdown thô: câu trả lời có `**đậm**` thì hoặc bị chặn, hoặc JSON-LD mang dấu `**` | `schema.py:245`, `:255` | Bài AI viết `**Có.** …` → T-041 truyền chữ sạch → Chặn; truyền chữ thô → Google hiện dấu sao. Không có đường chèn mã: JSON-LD là chữ, `<>&` đã đổi | Theo cách 1 của Soi Lỗi (bỏ Markdown nội dòng ở **cả** bài lẫn câu trả lời trong `schema.py`), kèm điều kiện ở dòng 3 |
| 3 (mới) | Thấp | Link Markdown trong câu trả lời đi nguyên vào JSON-LD, kể cả địa chỉ `javascript:` hay tên miền lạ | `schema.py:229-247` | Bài có `Xem [bảng giá](javascript:alert(1)) ![x](https://e.vil/a.png)` → câu trả lời nguyên văn qua kiểm (tôi chạy thử: không Chặn, không Cảnh báo) → JSON-LD chứa chuỗi đó **dạng chữ**. Hiện không chạy được (không phải HTML, không phải thuộc tính `href`). Nguy cơ thật chỉ xuất hiện nếu ai sửa lỗi 2 bằng cách **đổi Markdown thành HTML** `<a href>` | Khi sửa lỗi 2: `[chữ](url)` → chỉ giữ `chữ`, `![alt](url)` → bỏ hẳn hoặc giữ `alt`; **không bao giờ** đổi sang HTML; chữ sau khi bỏ định dạng vẫn đi qua `_has_html` và `to_json_ld`. Có test cho `javascript:`/tên miền lạ |
| 4 (ghi nhận) | Thấp | `_host` bỏ **mọi** dấu chấm cuối, nên `https://suachuacuasat.com..` được coi là cùng tên miền | `schema.py:193` | Không có hậu quả: trình duyệt không thể đưa địa chỉ này tới máy chủ khác; tên máy vẫn là site của mình | Không bắt buộc. Nếu tiện khi sửa ở T-041: chỉ bỏ **một** dấu chấm cuối |

Không có lỗi Nghiêm trọng, Cao hay Trung bình (về bảo mật).

## Kiểm độc lập (trọng tâm phiếu)

**Không đóng được `</script>` (W3, U1).** `to_json_ld` (`schema.py:391-410`) chạy `json.dumps(ensure_ascii=False)` rồi đổi `<`, `>`, `&`, U+2028, U+2029 thành `<`, `>`, `&`, ` `, ` ` (đã kiểm byte thô dòng 396–397 là đúng U+2028/U+2029). Vì `json.dumps` luôn viết `\` thành `\\`, không có cách nào để một `<` đứng sau số lẻ dấu `\` → phép đổi sau cùng luôn ra JSON hợp lệ. Tôi dựng thẳng khuôn (bỏ qua bộ kiểm) với `</script><script>…`, `<!--`, `]]>`, U+2028/2029, `＜／script＞`, `&lt;/script&gt;`, `&#x3c;…`, `\</script>`, `</SCRIPT >`, `</script>` viết sẵn, `a\`, `x"y`, cả trong `url`: chuỗi ra **không** còn `<`, `>`, `&`, U+2028/2029; `json.loads` đọc lại đúng nguyên văn. Không có `<` thì không tạo được `</script>` hay `<!--`. Chữ toàn khổ `＜` không được trình duyệt hiểu là thẻ. Hiện chưa có `unsafe_allow_html` nào dùng kết quả này.

**URL.** `check_url` (`schema.py:196-223`): chặn ký tự trắng/`Cc`/`Cf`, chỉ `https`, chặn mọi `@` trong netloc (kể cả `\@`), so **đúng** tên máy với `WORDPRESS_URL`, chặn cổng khác 443. Tôi thử: `evil.com\@site`, `site\.evil.com`, `site%2eevil.com`, punycode `xn--…`, chữ toàn khổ `ｓuachuacuasat.com`, `[::1]`, `:8443`, `https:site` (thiếu `//`), NUL → đều Chặn. `#@evil.com`, `?@evil.com` qua nhưng tên máy vẫn là site (đúng). Câu báo không chép URL.

**AI không viết JSON.** `build_faq_page` dựng dict từ cặp chữ (`schema.py:357-386`), rồi qua `validate_faq_page` và `FAQPage.model_validate`. Khuôn `extra="forbid"`, `strict=True`, `frozen=True` (`schema.py:82-83`); `@context`/`@type` là `Literal`. Loại bị cấm hoặc site đã xuất bị chặn bằng danh sách **cho phép** (`schema.py:149-163`); câu báo chỉ chèn tên loại khi tên đó nằm trong hằng số của code.

**SL-T038-1, SL-T038-2: có chấp nhận chuyển sang T-041 không?** **Chấp nhận**, vì: (1) T-038 chưa có nơi gọi, gộp vào `main` không đổi hành vi app; (2) cả hai không mở đường chèn mã hay lộ dữ liệu; lỗi 1 chỉ làm trang lỗi, lỗi 2 chỉ khó dùng/xấu. Không lỗi nào phải sửa trước khi gộp. Điều kiện ở mục cuối.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Không bí mật trong diff/lịch sử nhánh; detect-secrets báo 3 chỗ đều là dữ liệu giả của test (xem Báo nhầm) |
| S2 | Đạt | Câu báo là chữ cố định, không chép đầu vào (`schema.py:70-76`, test `test_messages_never_echo_input`, `test_messages_do_not_echo_url_or_text`). Không log |
| S3 | Không áp dụng | Không biến cấu hình mới; `site_url` truyền vào dạng tham số, hàm không đọc `.env` |
| W1 | Không áp dụng | Không gọi WordPress, không có `publish`/`future` |
| W2 | Không áp dụng | Không ghi gì lên site |
| W3 | Đạt | Không có HTML trong chữ (`_has_html` dùng `strip_tags` cả bản gốc lẫn bản giải thực thể, `schema.py:142-144`); JSON ra không đóng được `</script>` (`schema.py:391-410`, kiểm độc lập ở trên). Lưu ý lỗi 3 cho T-041 |
| W4 | Không áp dụng | Không gọi mạng. URL trong schema bắt buộc `https` (`schema.py:209`) |
| A1 | Không áp dụng | Không có prompt |
| A2 | Đạt | AI không viết JSON; code dựng và kiểm bằng khuôn `extra=forbid` |
| A3 | Không áp dụng | Không gửi gì cho AI |
| U1 | Đạt | Không dùng `unsafe_allow_html`; chuỗi ra an toàn kể cả khi sau này đặt trong `<script type="application/ld+json">` |
| U2 | Không áp dụng | Không có trang mới |
| U3 | Không áp dụng | |
| F1 | Không áp dụng | Không đọc/ghi file |
| F2 | Không áp dụng | |
| F3 | Đạt | Không `eval`/`pickle`/`yaml.load`; chỉ `json.dumps` |
| D1 | Đạt | Chỉ `json`, `re`, `html`, `unicodedata`, `urllib.parse` (thư viện chuẩn) + `pydantic` có sẵn; `pyproject.toml`, `uv.lock` không đổi |
| D2 | Đạt | `.gitignore` không đổi |
| D3 | Đạt | Test chỉ dữ liệu giả, không `requests`/`socket`; bộ chặn mạng chung ở `tests/conftest.py` vẫn bật; toàn bộ test qua |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | No known vulnerabilities found | Có |
| bandit (`seo_app/onpage`) | No issues identified | Có |
| detect-secrets (file của phiếu) | 3 cảnh báo trong test | Có: đều là dữ liệu giả, xem dưới |
| Soát lịch sử git (`origin/main..HEAD`) | Chỉ khớp chữ `secret = "MA-BI-MAT-123"` (dữ liệu giả của test) và `parts.password` (code kiểm URL) | Có |
| pytest / ruff | `4867 passed, 4 skipped, 21 xfailed` (Linux; 5 xfail strict là SL-T038-1/2) · `All checks passed!` | Có |

## Báo nhầm đã loại

- detect-secrets "Basic Auth Credentials" `tests/test_onpage_schema.py:368` (`https://user:pw@suachuacuasat.com/bai`) và `tests/test_soi_loi_t038.py:355` (`user:pass@`): URL giả để test việc **chặn** tài khoản trong URL.
- detect-secrets "Secret Keyword" `tests/test_soi_loi_t038.py:398` (`MA-BI-MAT-123`): chuỗi mồi để test câu báo không chép dữ liệu.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

Ghi vào phiếu **T-041**, Thợ Máy sửa `schema.py` **trước** khi Họa Sĩ cho giao diện hiện hoặc dùng `json_ld`; T-041 phải qua Lá Chắn:

1. **Lỗi 1 (SL-T038-1):** chặn `Cs`, `Co`, `Cn` cùng chỗ với ký tự điều khiển; bỏ `xfail` của `test_lone_surrogate_blocked`.
2. **Lỗi 2 (SL-T038-2) + lỗi 3:** bỏ Markdown nội dòng ở cả bài lẫn câu trả lời; link chỉ giữ chữ, ảnh bỏ hoặc giữ alt; **không đổi sang HTML**; chữ sau khi bỏ vẫn qua `_has_html` và `to_json_ld`. Test có `**đậm**`, `` `mã` ``, `[chữ](javascript:…)`, `![x](https://tên-miền-lạ/…)`, và `<`/`</script>` nằm giữa dấu Markdown.
3. Giao diện T-041 hiện `json_ld` bằng `st.code(..., language="json")`, không dùng `unsafe_allow_html`.
4. Hạn chót: trước khi hết Giai đoạn 4 (sớm hơn nếu T-041 làm giao diện trước).

Lỗi 4: không bắt buộc.

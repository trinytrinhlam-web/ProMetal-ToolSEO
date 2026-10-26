# Biên bản bảo mật T-088 · Dọn lỗi Thấp client WordPress sau T-085 · rút gọn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

> **BẢN ĐANG LÀM** (18:14 +07): phần kiểm code và thử độc lập đã xong; các lượt pytest còn đang chạy. Chưa phải kết luận cuối.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-088](../tickets/T-088-don-client-wordpress-sau-t085.md): SL-T085-1, -2, -3 của [Soi Lỗi T-085](T-085-soi-loi.md) và LC-T085-1 của [Lá Chắn T-085](T-085-la-chan.md) (điều kiện 1–3) |
| Phạm vi | Rút gọn: **W2, W3, S2** (yêu cầu bảo mật riêng của phiếu), kèm đủ 19 dòng danh sách kiểm tra. Diff `dd5ea2d..team/T-088` (gốc `main` `dd5ea2d`, đầu nhánh lúc kiểm `b008dc8`). Code ứng dụng chỉ có `seo_app/wordpress/client.py` (+55/−14); test: `tests/test_wordpress_t088.py` (mới, Thợ Máy), `tests/test_soi_loi_t088.py` (mới, Soi Lỗi), `tests/test_soi_loi_t085.py` (−20: gỡ 4 khối dấu `xfail`), `tests/test_la_chan_t085.py` (−10: gỡ 2 khối dấu `xfail` của tôi); 2 báo cáo. Kèm code xung quanh: `_request`, `_post_media`, `_describe_draft_media`, `create_draft_with_images`, `is_site_link`, `_plain`, `check_connection`, `app/views/wordpress.py`. `origin/main` lúc kiểm: `0735c5d` (có T-086; sau `8eac87c` chỉ thêm tài liệu); `origin/team/T-041`: `13a554c` |
| Ngày | 2026-10-26 (15:19–15:30 và 18:09–(đang chạy, điền ở bản cuối) +07, giờ máy đo bằng `date`; dừng giữa chừng vì hết lượt dùng) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (SL-T088-1 của Soi Lỗi, đồng ý **Thấp**, có từ trước, không do T-088). Lá Chắn không có lỗi mới. **SL-T085-1, -2, -3 và LC-T085-1 đóng; LC-T060-2 nay đóng hẳn** (cả lối vòng NUL). 4 `xfail` LC-T085-1 của tôi gỡ đúng. **Gộp `main` được ngay**: (đang chạy, điền ở bản cuối) |

## Tóm tắt (cho chủ dự án)

- **Phần sửa của T-088 an toàn và đóng đúng 4 lỗi nhỏ còn lại của lần kiểm trước.** Mẹo chèn ký tự vô hình (mã 0) để xin website trả nội dung bài nay bị chặn: tôi thử 60.000 giá trị ngẫu nhiên, không giá trị nào lọt. Website trả dữ liệu lạ, lồng quá sâu (kể cả trong câu báo lỗi) thì trang hiện một câu tiếng Việt cố định kèm mã lỗi, không còn khung lỗi đỏ của Python. Tải ảnh ở trang Kết nối WordPress mà website lỗi giữa chừng thì câu báo dặn kiểm thư viện Media trước khi tải lại; website từ chối rõ ràng thì giữ câu cũ.
- Câu báo mới đều cố định: không chép chữ website trả về, không chép địa chỉ, không lộ mật khẩu. Mọi việc thật của phần mềm vẫn gửi đúng.
- **Còn 1 điểm nhỏ (Thấp) có từ trước:** nếu website (hay plugin, proxy hỏng) trả chữ có một loại ký tự hỏng đặc biệt, trang vẫn hiện lỗi đỏ. WordPress bình thường không trả loại ký tự này. Nên sửa ở một phiếu dọn sau, tốt nhất trước hoặc cùng lúc bước SEO (T-041), chậm nhất trước khi hết Giai đoạn 4.

## Lỗi phát hiện

Không phát hiện lỗi mới (ngoài SL-T088-1 của Soi Lỗi, đánh giá ở mục dưới).

## Kiểm lại lỗi cũ

Số dòng theo `b008dc8`.

| Mã | Kết quả | Bằng chứng |
|---|---|---|
| SL-T085-1 · NUL sát tên trường `_fields` (lối vòng LC-T060-2) | **Đóng** (LC-T060-2 đóng hẳn) | Đúng cách tôi đề xuất ở T-085: `_asks_rendered_fields` cắt hai đầu mỗi phần bằng đúng bộ ký tự `trim()` của PHP `" \t\n\r\0\x0b"` (`_PHP_TRIM`, `client.py:125`, `:249-263`), sau khi tách như `wp_parse_list`; cắt thêm hai đầu tên trước dấu chấm (chặn thừa an toàn); phần chỉ còn rỗng không tính là tên, nên `_fields` chỉ có NUL bị chặn như `_fields` rỗng. NUL ở **giữa** tên vẫn đi ra (WordPress không cắt, vô hại). Đối chiếu mã WordPress (đọc ở T-085): `wp_parse_list` = `preg_split('/[\s,]+/', …)` (khoảng trắng ASCII, không có NUL), `get_fields_for_response` = `array_map('trim', …)` (bộ mặc định, có NUL). Thử độc lập (script T-085 chạy lại trên nhánh): 27 ca NUL của tôi (3 cách đặt × 9 đường): **0 lọt** (trên T-085: 27/27 lọt); 171 ca `_fields` khác và 9 hằng của app như cũ; 60.000 giá trị ngẫu nhiên (ghép tên trường, dấu phẩy, mọi khoảng trắng ASCII, NUL, U+00A0, U+200B, `\x1c`, U+0085, U+3000, `%00`, `+`, `;`): 38.838 được cho đi, **0** làm WordPress dựng trường chạy shortcode (trên T-085: 2.486). Bản Python của tôi: tách byte theo `[ \t\n\x0b\x0c\r,]+`, `trim()` từng phần, tên trước dấu chấm, so đúng chữ hoa thường; danh sách rỗng thì coi như mọi trường |
| SL-T085-2 · JSON lồng quá sâu → `RecursionError` (`_json`) | **Đóng** | `_json` (`client.py:1517-1527`) bắt mọi lỗi lúc giải mã thành câu cố định kèm «(mã N)», chỉ bọc đúng `response.json()`. Thử: `check_connection` với thân 200 lồng 100.000 tầng, chữ UTF-8 hỏng, rỗng, HTML, JSON cụt: `WordPressError` câu cố định (thân UTF-8 hỏng được `requests` giải mã thay ký tự rồi đi tiếp, ra câu «không có REST API» cố định) |
| LC-T085-1 · thân **lỗi** 4xx/5xx lồng quá sâu (`_error_from`) | **Đóng** | `_error_from` (`client.py:1535-1538`) bắt mọi lỗi giải mã thân lỗi, coi như thân rỗng, vẫn ra câu cố định theo mã HTTP. Thử 10 mã (400, 401, 403, 404, 409, 413, 429, 500, 502, 503) với thân lồng sâu: câu cố định có «mã N». Lệnh ghi đè ảnh trả 500 hay 200 lồng sâu, hay lỗi lạ `RuntimeError` mang mật khẩu: câu «thư viện Media», «mã ảnh 9», «Media → Thư viện» (`client.py:1162-1181`; lỗi lạ `:1178-1179`). 4 `xfail` LC-T085-1 của tôi gỡ đúng (chỉ xóa 2 khối dấu), qua |
| SL-T085-3 · lệnh tải ảnh lỗi giữa chừng | **Đóng** | `upload_media` bọc `_post_media` (`client.py:1144-1158`): lỗi có mã 4xx là lời từ chối rõ ràng, ném lại nguyên lỗi cũ; còn lại (hết giờ, mất kết nối, SSL, 3xx, 5xx, câu trả lời hỏng kể cả `201`, mã khác `201`) thêm câu cố định `_MEDIA_MAYBE_UPLOADED` (`client.py:386-389`), giữ `status_code`, `code`; lỗi lạ: `_MEDIA_UPLOAD_UNEXPECTED` (chỉ tên lớp lỗi, `:390`) cộng câu đó. Thử: 8 mã 4xx (thân có lời máy chủ và mật khẩu): giữ câu cũ kèm «(mã N)», **không** nhắc thư viện Media; 301 sang site lạ, 500, 504 trang HTML, mất kết nối và SSL mang địa chỉ + mật khẩu, `201` lồng sâu, `200`: có «thư viện Media», «Media → Thư viện», đúng 1 lệnh; 4 lỗi lạ của thư viện (`RuntimeError`, `ValueError`, `UnicodeError`, `OSError` mang mật khẩu và địa chỉ): câu chỉ có tên lớp lỗi và lời dặn, không chép chữ của lỗi |

Gỡ `xfail`: `git diff dd5ea2d..team/T-088 -- tests/test_soi_loi_t085.py tests/test_la_chan_t085.py`: chỉ xóa 4 + 2 khối dấu (`@pytest.mark.xfail(strict=True, reason=…)`), thân test không đổi chữ nào; 40 ca qua. Ca đối chứng của tôi ở T-060, T-085 qua. Không test cũ nào bị sửa.

## Đánh giá lỗi của Soi Lỗi

| Lỗi | Đánh giá của Lá Chắn | Chặn gộp? Phiếu nhận |
|---|---|---|
| SL-T088-1 · chữ website trả có ký tự surrogate lẻ (U+D800–U+DFFF) đi qua client nguyên vẹn | **Đồng ý Thấp.** Tự tái hiện gốc lỗi: `GET /wp-json/` trả `"name": "Cửa \ud800 sắt"` (JSON hợp lệ) → `check_connection()` trả `site_name` còn surrogate lẻ, không mã hóa UTF-8 được (Streamlit gửi chữ ra trình duyệt, SQLite ghi chữ đều mã hóa UTF-8 nên vỡ). Cùng họ LC-T044-1, SL-T085-2: dữ liệu lạ từ chính website làm trang hiện khung lỗi Python (mặc định kèm đường dẫn thư mục trên máy), chỉ người đang mở app ở localhost thấy. WordPress lõi không tự sinh surrogate lẻ (`wp_json_encode` sửa chữ UTF-8 hỏng), nên cần website, plugin hay proxy lỗi hoặc cố ý. Không lộ khóa, không ghi gì lên website: địa chỉ ảnh có surrogate lẻ mà lọt vào nội dung nháp thì `requests` gửi đi dạng `\ud800` và WordPress từ chối JSON đó (thân hỏng), không tạo gì. Có từ trước, không do T-088 | **Không chặn gộp T-088.** Phiếu dọn sau (Chỉ Huy lập): một chỗ làm sạch chung cho chữ website trả (thay hay bỏ surrogate lẻ, ví dụ ngay sau `response.json()` hay ở `_plain`, `_clean_text`, vai trò), `is_site_link` từ chối địa chỉ có surrogate. Không bắt buộc trước T-041 về bảo mật; **nên** làm trước hoặc cùng lúc T-041 vì T-041 đưa danh sách bài đã đăng vào bước SEO của Soạn bài (`site_listing()` chỉ bắt `WordPressError`, `SiteIndexError`, nên `UnicodeEncodeError` khi ghi bộ nhớ tạm lọt ra; Soi Lỗi đã nêu, Lá Chắn T-041 nên xét). Hạn chót: trước khi hết GĐ4 |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Không bí mật trong diff, file mới, lịch sử 3 commit của nhánh (mục Công cụ). Mật khẩu trong test là chuỗi giả |
| S2 | Đạt | Câu mới đều cố định: `_MEDIA_MAYBE_UPLOADED` (hằng), `_MEDIA_UPLOAD_UNEXPECTED` (chỉ ghép tên lớp lỗi Python, máy chủ không đặt được), câu `_json` chỉ ghép mã HTTP (số). Lỗi 4xx ở lệnh tải ném lại nguyên lỗi cũ (câu cố định của `_error_from`); lỗi khác chỉ ghép thêm câu dặn vào câu cố định cũ (`str(exc)` của `WordPressError`, vốn cố định). Thử 38 ca (thân lỗi có mật khẩu và địa chỉ, lỗi mạng mang mật khẩu, lỗi lạ của thư viện mang mật khẩu): không câu nào có mật khẩu (có và không dấu cách), tên đăng nhập, tên máy, lời máy chủ, «<». Lỗi lạ: `from exc`/`from None`, app chỉ hiện `plain(exc)` (không in `__cause__`, không traceback) |
| S3 | Không áp dụng | Không biến cấu hình mới; `.env.example` không đổi |
| W1 | Không áp dụng | Không đổi đường tạo bài; `_is_plain_request` (chốt `status` chỉ `"draft"` của T-085) giống hệt (so cây cú pháp) |
| W2 | Đạt | `upload_media` vẫn chỉ ghi vào ảnh website vừa xác nhận tạo (`201`); lệnh tải lỗi thì không gửi lệnh ghi đè nào (đúng 1 lệnh trong mọi ca thử); câu báo dặn người dùng tự kiểm, xóa (phần mềm không có hàm xóa). Mã `200`/`202` (có thể là ảnh đã có): vẫn dừng, không ghi gì, nay thêm lời dặn kiểm thư viện |
| W3 | Đạt | Lối vòng NUL của `_fields` đóng (0/60.000); mọi chốt chặn khác của `_request` (tham số, header, thân JSON, phiên kết nối, chuyển hướng) giống hệt T-085 (so cây cú pháp `_request`, `_is_plain_request`, `ALLOWED_ROUTES`, `ALLOWED_PARAMS`, `ALLOWED_JSON_KEYS`: giống). Script T-085 chạy lại: khóa JSON 689 ca, `status` 19 ca, `_fields` 171 ca: 0 lọt, 0 chặn oan. Lọc HTML nội dung bài (mục 2.3) không đổi |
| W4 | Đạt | `_request` không đổi: vẫn `timeout`, `allow_redirects=False`, không `verify=False` (`grep` rỗng), `WORDPRESS_URL` bắt buộc `https://` |
| A1 | Không áp dụng | Không dựng prompt, không gọi AI |
| A2 | Không áp dụng | Không đổi lớp AI; `_seo_text` (T-041 dùng lại trong `seo_app/onpage/meta.py`) giống hệt |
| A3 | Không áp dụng | Không gửi gì cho AI |
| U1 | Không áp dụng | Không sửa `app/**` (`git diff --quiet`); trang Kết nối WordPress hiện câu báo qua `plain()` |
| U2 | Không áp dụng | Không trang mới; `.streamlit/` không đổi |
| U3 | Không áp dụng | Không đụng mật khẩu đăng nhập app |
| F1 | Không áp dụng | Không mở file mới |
| F2 | Không áp dụng | Không đổi xử lý ảnh |
| F3 | Đạt | Phần thêm không `eval`, `pickle`, `yaml.load`, `subprocess`; JSON đọc bằng `response.json()` như cũ (chỉ bọc lỗi rộng hơn) |
| D1 | Đạt | Không thư viện mới; `uv.lock`, `pyproject.toml` giống gốc. pip-audit: 0 lỗ hổng (`uv export --frozen --no-hashes --no-emit-project`, 69 gói → `uvx pip-audit -r … --no-deps --disable-pip`, 18:13: **No known vulnerabilities found**) |
| D2 | Đạt | `.gitignore` không đổi; diff không có `.env`, `.sqlite`, `.json`, `.pem` |
| D3 | Đạt | Test mới chỉ dùng `FakeWordPress`; bộ chặn mạng tự bật (`tests/conftest.py:18`). Thử độc lập của tôi cũng chỉ dùng site giả |

## Không chặn oan

- Không đổi: so cây cú pháp giữa `dd5ea2d` và nhánh, chỉ khác `_asks_rendered_fields`, `_json`, `_error_from`, `upload_media` (và 3 hằng mới); `_has_shortcode`, `_SHORTCODE_OPEN`, `_drop_invisible`, `_ignorable_not_cf`, `_seo_text`, `_request`, `_is_plain_request`, `_post_media`, `create_draft_with_images`, `_describe_draft_media`, `ALLOWED_ROUTES`, `ALLOWED_PARAMS`, `ALLOWED_JSON_KEYS`, `is_site_link`, `_plain`, `_RENDERED_FIELDS` **giống hệt**.
- 9 hằng `_fields` của app vẫn đi ra trên đúng đường; khóa JSON app thật gửi vẫn đi ra (script T-085).
- (đang chạy, điền ở bản cuối)

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | 0 lỗ hổng (`uv export --frozen --no-hashes --no-emit-project`, 69 gói → `uvx pip-audit -r … --no-deps --disable-pip`, 18:13: **No known vulnerabilities found**) | Có. `uv.lock` không đổi so với gốc |
| bandit | `seo_app/wordpress/client.py`: **No issues identified** (1.593 dòng) | Có |
| detect-secrets (`PYTHONUTF8=1`) | 8 file (`client.py`, 4 file test có đổi, 3 báo cáo kể cả biên bản này): 6 phát hiện, đều là chuỗi giả hay chữ mẫu: `client.py:682` dòng chú thích ví dụ dạng «tên:mật-khẩu@site» (có từ T-060); «Secret Keyword» ở `tests/test_soi_loi_t085.py:45`, `:46`, `tests/test_soi_loi_t088.py:41`, `:42`, `tests/test_wordpress_t088.py:30` là mật khẩu giả của test. Biên bản này: 0 | Có, từng dòng |
| Soát lịch sử git | `git log -p dd5ea2d..HEAD` (3 commit): không có `sk-ant-`, `AIza…`, `ghp_…`, `-----BEGIN`; không file `.env`, `.sqlite`, `.json`, `.pem` | Có |
| pytest (nhánh) | (đang chạy, điền ở bản cuối) | Có |
| pytest (cây gộp) | (đang chạy, điền ở bản cuối) | Có |
| ruff | `uv run ruff check .`: **All checks passed!** | Có |

## Ghi nhận (không xếp lỗi)

1. **Mã `200`/`202` ở lệnh tải** (`_MEDIA_NOT_CREATED`) nay cũng dặn «ảnh có thể đã lên»; mã 3xx cũng vậy (Ghi nhận 1 của Soi Lỗi): đồng ý, dọa thừa nhưng an toàn, khớp `maybe_uploaded` của nhánh gửi nháp kèm ảnh.
2. **Bắt mọi lỗi lúc giải mã JSON** (`except Exception` chỉ bọc `response.json()`): không giấu lỗi của code khác; đồng ý.
3. Đề xuất còn mở từ T-060, T-085 (Thợ Máy nhắc lại): lớp chặn phụ `id`/`name` cho tham số truy vấn; bắt buộc `_fields` trên đường bài, ảnh; `verify=True` tường minh; `html.escape` tiêu đề, chú thích trong `upload_media`. Vẫn tùy chọn, không có đường tới.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

| # | Việc | Ai làm | Hạn |
|---|---|---|---|
| 1 | **SL-T088-1:** chữ website trả không còn surrogate lẻ (làm sạch chung, `is_site_link` từ chối); gỡ 8 `xfail` của Soi Lỗi | Thợ Máy, **phiếu dọn lỗi Thấp client WordPress sau T-088** (Chỉ Huy lập) | Nên trước hoặc cùng lúc gộp T-041; chậm nhất trước khi hết GĐ4. Không chặn gộp T-088 |

**Kết luận: ĐẠT CÓ ĐIỀU KIỆN.** (đang chạy, điền ở bản cuối)

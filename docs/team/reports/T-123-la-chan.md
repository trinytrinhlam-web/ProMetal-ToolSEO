# Biên bản bảo mật T-123 · Lõi tính toán theo dõi bài (Giai đoạn 6, đợt 1) · rút gọn

> **Model:** Claude Opus 5.5. Chủ dự án quyết ngày 04/11: hết hạn mức Fable thì dùng Opus.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-123](../tickets/T-123-loi-tinh-toan-theo-doi.md) · mức **rút gọn** (hàm thuần) · báo cáo [Thợ Máy](T-123-tho-may.md) (lượt 1, 2), [Soi Lỗi](T-123-soi-loi.md) |
| Phạm vi | Nhánh `team/T-123` tại `d71c9ad`, diff `a499a13..d71c9ad` (16 file: 7 file mã `seo_app/tracking/`, 7 file test, 2 báo cáo). Trọng tâm: lượt 2 `d8fe3f7` (`site_base`, CTR) và 5 điều kiện LC-T120-6, -10, -11, -15, -19. Đối chiếu client Search Console `origin/team/T-121` `eb05747` (chỉ đọc, chạy thử trên bản chép). Không gọi Google hay website thật, không sửa mã |
| Ngày | 2026-11-04 (08:40–09:25, giờ máy +07) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: gộp `main` được ngay. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp mới** (LC-T123-1: link bài WordPress viết hoa tên máy thì bài không nhận số liệu; sửa hay báo ở T-124, T-125). SL-T123-1, SL-T123-2 **đóng đúng**. `site_base` **không nới lọc**: 0 lệch so với bản cũ, kể cả trên 60.000 địa chỉ dò ngẫu nhiên. 5 điều kiện LC-T120 **đạt phần T-123**. T-121 **không có** lỗi chữ hoa. 3 điều kiện chuyển cho T-124, T-125, T-127 (mục 7) |

## Tóm tắt (cho chủ dự án)

- **Phần tính toán cho trang theo dõi Google an toàn để gộp.** Nó chỉ tính toán: không gọi mạng, không đọc ghi file, không tạo link.
- **Hai lỗi Soi Lỗi tìm ra đã sửa đúng.**
  - Địa chỉ website trong `.env` gõ chữ hoa không còn làm bảng trống.
  - Tỉ lệ click đúng «x,x5%» nay luôn làm tròn lên. Tôi thử 721.800 cặp số, không sai cặp nào.
- **Bản sửa không mở cửa cho địa chỉ lạ.** Bản staging, `www.`, `http://`, cổng khác, địa chỉ có tên người dùng, tên miền giống (`evilsuachuacuasat.com`) vẫn bị loại, dù `.env` viết kiểu nào.
- **Chữ lạ từ Google không lọt ra màn hình.** Tôi thử đủ mọi ký tự Unicode (hơn 1,1 triệu ký tự) trong đường dẫn và từ khóa, kể cả ký tự đảo chiều chữ và ký tự vô hình: tất cả đều được làm sạch. Ngày lạ (năm 1, năm 9999) không làm phần mềm lỗi.
- **Một lỗi nhỏ mới (Thấp).** Nếu ô «Địa chỉ trang» trong cài đặt WordPress có chữ hoa (ví dụ `https://SuaChuaCuaSat.com`), bài sẽ không nhận được số liệu. Website hiện viết chữ thường nên chưa ảnh hưởng. Sẽ sửa, hoặc báo rõ trên màn hình, ở phiếu sau.
- **Không có gì anh/chị phải quyết.**

## 1. Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T123-1 | Thấp | Cùng loại với SL-T123-2, nhưng ở phía WordPress. Link bài từ WordPress vẫn được so **nguyên văn** với tiền tố đã viết thường. Link có tên máy viết hoa vì vậy bị bỏ | `seo_app/tracking/match.py:182-187` (`page_key(item.link, site)` trong `build_tracking`) | <ul><li>**Đầu vào:** ô «Địa chỉ trang» (`home`) của WordPress gõ có chữ hoa. WordPress giữ nguyên chữ hoa khi lưu: `sanitize_option` gọi `sanitize_url` rồi `esc_url`, không đổi tên máy (`wp-includes/formatting.php:5000-5011`, bản 6.9.4 trong máy). Link bài thành `https://SuaChuaCuaSat.com/bai-1/`.</li><li>**Trong app:** client WordPress vẫn nhận link vì `is_site_link` so tên máy không phân biệt hoa thường. Nhưng `build_tracking` bỏ bài (`skipped_items = 1`).</li><li>**Số liệu Google:** tên máy luôn viết thường, vì bộ lọc RE2 và `_page` của T-121 phân biệt hoa thường. Số liệu của bài rơi vào «Trang khác», bài hiện 👻 «Chưa có lượt hiển thị».</li><li>**Đã chạy:** `pages = 0`, `skipped_items = 1`, `others = ['/bai-1']`.</li><li>**Mức độ:** không lộ gì, không nới lọc. Khả năng xảy ra thấp: mọi link thật của website trong các lượt thử trước đều viết thường.</li></ul> | Một trong hai cách: <ul><li>**T-124:** trong `build_tracking`, viết thường scheme và tên máy của `item.link` (như `site_base`) trước khi dựng khóa. An toàn vì `is_site_link` đã chứng minh cùng tên máy, cùng cổng.</li><li>**T-125:** khi `skipped_items > 0`, hiện câu cố định «N bài, trang không khớp địa chỉ website trong cài đặt», không im lặng.</li></ul> |

Không có lỗi Nghiêm trọng, Cao, Trung bình.

## 2. Sáu việc Chỉ Huy giao

| # | Việc | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | Điều kiện LC-T120-6, -10, -11, -15, -19 | **Đạt cả 5** (phần T-123) | Mục 3 |
| 2 | SL-T123-1, -2 đã đóng đúng | **Đóng đúng.** Chi tiết ngay dưới bảng | `probe_t123.py` mục 1, 4; `git diff 10b6fd5 d71c9ad -- tests/` |
| 3 | `site_base` có nới lọc không | **Không nới.** Chi tiết ngay dưới bảng | `probe_t123.py` mục 1 |
| 4 | Chữ từ Google sau khi giải mã `%` có được làm sạch không | **Có**, ở mọi đường hiện. Chi tiết ngay dưới bảng | `probe_t123.py` mục 2 |
| 5 | Năm 1 và 9999 | **Không lỗi Python nào lọt ra.** Sai thì trả `None` hay `PeriodError` câu cố định. Chi tiết ngay dưới bảng | `probe_t123.py` mục 3 |
| 6 | T-121 có cùng lỗi chữ hoa không | **Không.** Chi tiết ngay dưới bảng | `cross_t121.py` |

**Việc 2: SL-T123-1, -2 đã đóng đúng**

- **SL-T123-2:**
  - Với `https://SuaChuaCuaSat.com`, bản cũ `2548d1f` cho `None`, bản mới cho `PageKey('/bai-1')`.
  - Thử 7 cách viết `WORDPRESS_URL`: chữ hoa, `/` cuối, `//`, `:443`. Trên 52 địa chỉ và 60.000 địa chỉ dò ngẫu nhiên, `page_key` mới cho **đúng kết quả** của bản cũ với cách viết chuẩn: 0 lệch.
  - Đường dẫn con giữ chữ hoa: `/Blog` khác `/blog`.
- **SL-T123-1:**
  - So với phép làm tròn 5 lên chính xác (`Fraction`) trên **mọi** cặp click ≤ hiển thị ≤ 1.200: 721.800 cặp, trong đó 1.560 cặp đúng nửa.
  - `shown_ctr_percent` và `percent_text` sai **0** cặp; bản cũ sai 69 cặp đúng nửa.
  - `Decimal` dùng ngữ cảnh mặc định 28 chữ số; không chỗ nào trong `seo_app/`, `app/` đổi ngữ cảnh. Làm tròn hai lần chỉ xảy ra khi lượt hiển thị trên 5×10²⁴, xa trần 10⁹ một dòng.
- **R5:** lượt 2 chỉ gỡ 3 dấu `xfail` (9 dòng) sau khi XPASS, thêm 70 dòng test, không sửa kỳ vọng nào.

**Việc 3: `site_base` không nới lọc**

- **42 địa chỉ ngoài website** bị loại ở cả 7 cách viết `WORDPRESS_URL`:
  - tên máy khác: staging, `www.`, `evilsuachuacuasat.com`, `….com.evil.com`, dấu chấm cuối, chữ Kirin giống chữ Latin, `xn--`, địa chỉ IP;
  - scheme sai: `http://`, `ftp://`, `javascript://`, `//…`, `https:/…`;
  - cổng: `8443`, `80`, `0`, `0443`, `443` viết rõ, cổng rỗng;
  - tên người dùng trong địa chỉ: `user@…`, kèm mật khẩu, `…com@evil.com`, `%40`, `\`;
  - tên máy viết hoa trong địa chỉ Google;
  - ký tự lạ: dấu cách, `<>`, `"`, ký tự đảo chiều, ký tự vô hình, tab, xuống dòng;
  - quá 2.000 ký tự, UTF-8 hỏng.
- **Dò ngẫu nhiên:** 60.000 địa chỉ (sửa 1–3 ký tự từ mẫu) × 7 cách viết, có 8.785 lượt nhận. Mọi lượt nhận đều bắt đầu **đúng** `https://suachuacuasat.com/`, đúng tên máy, không cổng, không tên người dùng.
- **Ba cách viết `WORDPRESS_URL` lạ** (`user@…`, `?x=1`, `#x`): `site_base` bỏ phần lạ, nên vẫn nhận địa chỉ của chính website. Không ảnh hưởng, vì client WordPress (`_is_plain_site_url`) và T-121 (`site_prefix`) đều từ chối các cách viết này: app không có bài, không có số liệu.

**Việc 4: chữ từ Google sau khi giải mã `%` được làm sạch**

- **Mọi điểm mã Unicode** (1.112.064, trừ surrogate), đặt giữa đường dẫn, trong phần `?…` và trong từ khóa:
  - nhãn (`page_label`) và từ khóa (`query_text`) có **0** ký tự loại Cc, Cf, Cs, Co, Cn, ký tự mặc định bỏ qua, khoảng trắng lạ;
  - nhãn ≤ 120 ký tự, từ khóa ≤ 200 ký tự.
- **28 ký tự nguy hiểm mã hóa `%`** (NUL, tab, xuống dòng, ESC, U+202E, U+2066, U+200B, BOM, ký tự thẻ U+E0001…):
  - giải mã vào `PageKey` còn nguyên vẹn. Đây là cố ý, để không gộp nhầm hai địa chỉ;
  - nhãn sạch 28/28.
- **Câu giải thích nhãn** chỉ chèn số, ngày và chữ cố định. Đã soát mọi chỗ chèn trong `flags.py`.
- Lưu ý cho T-125 ở mục 7.

**Việc 5: năm 1 và 9999**

- 792 lệnh gọi với các giá trị: năm 1, 9999, 1999, 2201; `date.min`, `date.max`; `datetime.min`/`max` có múi giờ ±23:59; giờ không múi giờ; chữ; `None`; `bool`; số.
- Các hàm đã gọi: `Period`, `last_days`, `custom_period`, `previous_period`, `year_before`, `week_blocks`, `google_day`, `google_today`, `published_day`, `page_flags`, `aggregate`, `build_tracking`, `page_queries`.

**Việc 6: T-121 không có lỗi chữ hoa**

- Đã chạy `site_prefix`, `_page`, `parse_property`, `covers_site` của `eb05747` trên bản chép.
- **Tiền tố:** với 8 cách viết `WORDPRESS_URL` mà T-121 nhận (chữ hoa, `:443`, thư mục con có chữ hoa), tiền tố của T-121 **trùng** `site_base + "/"` của T-123.
- **Dòng số liệu:** dòng T-121 nhận mà T-123 bỏ: **0**. Dòng T-123 nhận mà T-121 bỏ: 0.
- **`GSC_SITE_URL` viết hoa** (`sc-domain:SUACHUACUASAT.com`, `https://SuaChuaCuaSat.com/`): T-121 từ chối kèm câu cố định «Thuộc tính … sai dạng. Chọn lại ở Cài đặt → Google», không im lặng. LC-T120-17 cho phép từ chối.
- `sc-domain:evilsuachuacuasat.com` và `https://www.suachuacuasat.com/` không phủ website.

## 3. Điều kiện LC-T120 (phần T-123)

| Mã | Kết quả | Bằng chứng |
|---|---|---|
| LC-T120-6 | Đạt | <ul><li>`page_key` đòi cả `is_site_link` lẫn tiền tố website (mục 2, việc 3).</li><li>Test: `test_page_key_rejects_rows_outside_website`, `test_rows_outside_website_are_dropped_even_if_google_returns_them`, `test_google_url_spelling_is_still_compared_verbatim`, 12 ca canh của Soi Lỗi.</li><li>Đột biến M2, M4, M5 (mục 4) đều bị bắt.</li><li>Phần «thuộc tính phủ website» là của T-121 (đã thử ở việc 6).</li></ul> |
| LC-T120-10 | Đạt | <ul><li>Năm được kiểm trước khi đổi múi giờ hay trừ ngày: `is_day`, `_checked`, `google_day`, `published_day`, `_post_age`.</li><li>`google_day` bắt `OverflowError`, `ValueError`, `TypeError`.</li><li>Không có phép cộng ngày. Phép trừ ngày (`last_days`, `previous_period`, `year_before`, `week_blocks`) và đổi múi giờ chỉ chạy trên ngày đã kiểm trong khoảng 2000–2200; kết quả lại qua `Period`.</li><li>Mục 2, việc 5. Đột biến M10, M11, M12c bị bắt.</li></ul> |
| LC-T120-11 | Đạt phần T-123 | <ul><li>Gói chỉ trả chữ thuần: không nhập Streamlit, không HTML, không Markdown, không link (đã `grep`).</li><li>Câu giải thích nhãn chỉ có số, ngày.</li><li>`safe_rows` và «không `LinkColumn`» là việc của T-125 (mục 7).</li></ul> |
| LC-T120-15 | Đạt | <ul><li>Plugin `sys.addaudithook` khi chạy 7 file test: 0 kết nối, 0 tra tên, 0 tiến trình con, 0 lần mở `.env`.</li><li>Sự kiện duy nhất là `bind(('::1', 0))` lúc nhập urllib3, để thử máy có IPv6 không (`urllib3/util/connection.py:127`). Lệnh này không gửi gì.</li><li>File `.env` mồi đặt ở gốc worktree: mã băm trước và sau như nhau.</li><li>Ca biên mục 2.4 thuộc lớp này đều có test: đường dẫn > 2.000 ký tự, từ khóa > 2.048 ký tự, từ khóa rỗng sau làm sạch, `bool`, số thực, `NaN`, `inf`, click > hiển thị, hiển thị 0 hay > 10⁹, vị trí < 1 hay > 10.000. Đột biến M7–M9, M15, M16 bị bắt.</li><li>Không có trang mới, nên không áp dụng phần `PAGES`.</li></ul> |
| LC-T120-19 | Đạt phần T-123 | <ul><li>`page_label` chạy `clean_text` sau khi giải mã `%`, rồi cắt 120 ký tự (mục 2, việc 4).</li><li>Đột biến M6, M7 bị bắt.</li><li>Phần tên máy ở «Kiểm tra» là của T-121 (`HostCheck`) và T-125.</li></ul> |

## 4. Thử đột biến

Plugin pytest đổi đúng một chỗ trước khi nạp test, rồi chạy lại 7 file test. Bản gốc: 317 qua.

| Mã | Đột biến | Kết quả |
|---|---|---|
| M1 | `site_base` viết thường cả đường dẫn | Bắt (1 hỏng) |
| M2 | `site_base` quay về bản cũ (không chuẩn hóa) | Bắt (10) |
| M3 | Viết thường nhưng giữ `:443` | Bắt (2) |
| M4 | Bỏ `is_site_link` trong `page_key` | Bắt (4) |
| M5 | Bỏ kiểm tiền tố trong `page_key` | Bắt (5) |
| M6 | Nhãn không qua `clean_text` | Bắt (1) |
| M7 | Nhãn không cắt 120 ký tự | Bắt (1) |
| M8 | Từ khóa không qua `clean_text` | Bắt (5) |
| M9 | Bỏ trần 2.048 ký tự của từ khóa | Bắt (2) |
| M10 | `is_day` bỏ khoảng năm | Bắt (3) |
| M11 | `Period` bỏ khoảng năm | Bắt (9) |
| M12a | `google_day` bỏ kiểm năm, còn bắt lỗi | Sống: lớp bắt lỗi và `is_day` phía sau vẫn chặn |
| M12b | `google_day` bỏ bắt lỗi, còn kiểm năm | Sống: kiểm năm phía trước đã chặn |
| M12c | `google_day` bỏ cả hai lớp | Bắt (6) |
| M13 | CTR quay về số thực (SL-T123-1) | Bắt (7) |
| M14 | `percent_text` nhân 100 bằng số thực | Bắt (5) |
| M15 | Nhận `final` không phải `bool` | Bắt (1) |
| M16 | Cho `NaN`, `inf` qua `numbers_ok` | Bắt (4) |
| M17 | Bỏ trần 2.000 ký tự trong `page_key` | Sống: `is_site_link` có cùng trần 2.000 |

16/19 bị bắt. Ba đột biến sống đều chỉ bỏ **một** trong hai lớp chặn trùng nhau; lớp còn lại vẫn đủ. Có thể thêm một ca ghim quy tắc «kiểm năm trước khi đổi múi giờ» (góp ý G2).

## 5. Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets 16 file: 0 kết quả, mồi bị bắt. `git log -p a499a13..d71c9ad` chỉ có câu nhắc lệnh quét trong báo cáo |
| S2 | Đạt | Gói không ghi log, không in. Câu lỗi `PeriodError` cố định, không chép giá trị vào |
| S3 | Không áp dụng | Không có biến cấu hình mới; `.env.example` không đổi |
| W1 | Không áp dụng | Không gọi WordPress |
| W2 | Không áp dụng | Không ghi gì |
| W3 | Không áp dụng | Không gửi HTML |
| W4 | Không áp dụng | Không gọi mạng. Chỉ dùng `is_site_link` để kiểm địa chỉ (đòi `https://`) |
| A1 | Không áp dụng | Không có prompt. Từ khóa và nhãn «Trang khác» là chữ người lạ (kể cả `?s=` khách gõ vào ô tìm kiếm): không đưa vào lời dặn AI hay Sheets (LC-T120-13; mục 7) |
| A2 | Không áp dụng | Không dùng AI |
| A3 | Không áp dụng | Không gửi gì ra ngoài |
| U1 | Đạt (phần T-123) | Không HTML, không `unsafe_allow_html`. Chữ trả ra là chữ thuần đã làm sạch |
| U2 | Không áp dụng | Không có trang |
| U3 | Không áp dụng | |
| F1 | Không áp dụng | Không đọc ghi file (`test_package_is_pure_functions`) |
| F2 | Không áp dụng | |
| F3 | Đạt | Không `eval`, `exec`, `pickle`. bandit 0 lỗi |
| D1 | Đạt | Không thư viện mới. `pyproject.toml`, `uv.lock` không đổi (`zoneinfo` dùng `tzdata` sẵn có) |
| D2 | Đạt | `.gitignore` không đổi, vẫn chặn `.env` |
| D3 | Đạt | Plugin audit hook: 0 kết nối, 0 tra tên (LC-T120-15) |

## 6. Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | Không chạy, vì không đổi thư viện | `git diff a499a13 d71c9ad -- pyproject.toml uv.lock` trống |
| bandit | 0 lỗi, 1.094 dòng (`seo_app/tracking`) | Có `PYTHONUTF8=1` |
| detect-secrets | 16 file đổi: `{}`. Mồi (bản chép `flags.py` tiếng Việt, thêm 2 khóa giả): bị bắt | <ul><li>Cách chạy: trên bản chép, đứng tại thư mục chép, `--all-files`, `PYTHONUTF8=1`.</li><li>Lần đầu đưa mồi bằng đường dẫn tuyệt đối nằm ngoài thư mục đang đứng thì ra `{}` giả. Đã chạy lại đúng cách.</li></ul> |
| Soát lịch sử git | Sạch | Chỉ có câu nhắc lệnh detect-secrets trong 2 báo cáo |
| pytest | 7 file liên quan: **317 qua** | <ul><li>Trên `d71c9ad`.</li><li>Trên bản gộp thử với `main` máy `33bac10`: `git merge-tree` không xung đột; 7 file mã T-123 giống hệt sau gộp; `seo_app` nạp từ bản gộp.</li><li>Không chạy toàn bộ pytest, theo tin giao.</li></ul> |
| ruff | `ruff check .` sạch; `ruff format --check` 14 file sạch | |

## 7. Điều kiện

**Gộp `main` được ngay.** Các điều kiện sau thuộc phiếu sau; Chỉ Huy chép vào phiếu:

1. **LC-T123-1 (Thấp) → T-124, hay T-125.** Chọn một trong hai:
   - viết thường scheme và tên máy của `item.link` trước khi dựng khóa;
   - T-125 báo `skipped_items` bằng câu cố định.

   Không chặn gộp.
2. **T-125, phần hiện chữ:**
   - **Chỉ hiện** `TrackedPage.label`, `KeywordGroup.text`, `KeywordVariant.text`.
   - **Không hiện, không xuất** `PageKey` (`str(key)`, `key.path`, `key.query`): đây là chữ đã giải mã nhưng **chưa làm sạch**.
   - **Không hiện, không xuất** `KeywordGroup.key`: đây là khóa nội bộ, có thể bắt đầu bằng `=`.
   - **Không dựng link** từ `key` hay `label`. Link tới bài chỉ lấy từ `item.link`.
   - **Mọi bảng** có các chữ trên đi qua `safe_rows` (LC-T120-11). Từ khóa như `=HYPERLINK(1)` vẫn giữ dấu `=` ở đầu sau khi làm sạch.
3. **T-125, T-127 (A1):** nhãn «Trang khác» có thể chứa chữ khách gõ (`/?s=…`), cùng loại với từ khóa. Không đưa vào lời dặn AI hay Google Sheets (LC-T120-13, -24).

## 8. Góp ý (không xếp lỗi)

- **G1. Nhãn «Trang khác» có thể trùng nhãn trang chủ.**
  - `HOME_LABEL` là «/ (trang chủ)», bắt đầu bằng «/» như mọi nhãn đường dẫn. Vì vậy địa chỉ `/%20(trang%20ch%E1%BB%A7)` có nhãn trùng hệt (đã chạy).
  - Gần như không xảy ra: muốn có số liệu, địa chỉ đó phải được Google lập chỉ mục, mà WordPress trả 404.
  - Muốn chặn hẳn: đổi `HOME_LABEL` thành chữ không bắt đầu bằng «/», ví dụ «(trang chủ)». Nhãn đường dẫn sau `clean_text` luôn bắt đầu bằng «/», nên sẽ không trùng được nữa.
- **G2. Thêm một ca ghim quy tắc «kiểm năm trước khi đổi múi giờ».** Hiện đột biến M12a sống.
  - Ca đề xuất: `datetime(1999, 12, 31, 23, 0, tzinfo=UTC−23:00)` phải cho `None`.
  - Nếu bỏ kiểm năm, mốc này đổi sang giờ PT thành ngày 01/01/2000, là ngày hợp lệ, nên lọt.
- **G3. Về các góp ý của Soi Lỗi.**
  - Đồng ý G1 (đếm riêng dòng sai khuôn) và G3.
  - G5 (`round_half_up` hỏng từ 10²⁷) không tới được: phần trăm chênh click lớn nhất chỉ cỡ 10¹⁷. Đã chạy `change_text` với 486 ngày × 10⁹ × 50 dòng một ngày.

## 9. Lệnh đã chạy

```
# Script dò (thư mục nháp; .venv của wt-T-123; old_match.py, old_stats.py = bản 2548d1f)
python -X utf8 probe_t123.py
  1. 7 cách viết × 52 địa chỉ: lệch 0; 42/42 ngoài website bị loại; 10/10 đúng website nhận
     dò ngẫu nhiên 60.000 × 7: nhận 8.785, sai 0; link WordPress viết hoa: pages=0, skipped_items=1
  2. mọi điểm mã: nhãn bẩn 0, từ khóa bẩn 0; 28 ký tự nguy hiểm: khóa giữ 28/28, nhãn sạch 28/28
  3. 792 lệnh năm biên: lỗi Python lọt ra 0
  4. 721.800 cặp CTR: sai 0 (bản cũ sai 69/1.560 ca đúng nửa)
python -X utf8 cross_t121.py t121 <bản chép seo_app của eb05747> …; … t123 …   # trùng 8/8, lệch 0/0

uv run pytest -p lc_audit_plugin <7 file> -q             # 317 passed; audit: 1 bind ::1 của urllib3
LC_MUT=<M1…M17> uv run pytest -p lc_mut_t123 <7 file> -q  # 16/19 bị bắt (mục 4)
git merge-tree --write-tree 33bac10 d71c9ad               # không xung đột → commit thử 915125b (không đẩy)
PYTHONPATH=<bản gộp> python -m pytest <7 file> -q         # 317 passed, seo_app nạp từ bản gộp
uv run ruff check .; uv run ruff format --check …          # sạch
PYTHONUTF8=1 uvx detect-secrets scan --all-files …        # 16 file {}; mồi bị bắt
PYTHONUTF8=1 uvx bandit -r seo_app/tracking               # No issues identified
uv --version                                               # 0.13.4
```

- Không gọi Google, WordPress thật; không chạy cloud; không chạy toàn bộ pytest; không sửa mã hay test.
- Script, plugin, bản chép, bản gộp thử để ở thư mục nháp, không commit.

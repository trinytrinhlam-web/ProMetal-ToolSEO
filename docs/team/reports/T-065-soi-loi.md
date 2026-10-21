# Báo cáo T-065 · Quy tắc alt: chữ trong ảnh không chép vào alt lẫn chú thích · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-065](../tickets/T-065-quy-tac-alt-chu-trong-anh.md) |
| Ngày nộp | 2026-10-21 |
| Kết quả | Hoàn thành (kiểm rút gọn). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn rút gọn được |

## Tóm tắt (cho chủ dự án)

Ngòi Bút sửa đúng cả 4 yêu cầu và ghi chú của Lá Chắn: quy tắc viết alt nay cấm chép chữ đọc được trong ảnh (biển hiệu, tên cửa hàng, số điện thoại…) vào **cả alt lẫn chú thích**; hai ví dụ tự mâu thuẫn đã sửa; trong file có dòng nhắc «quy tắc và ví dụ được gửi nguyên văn cho hãng AI, chỉ dùng thông tin bịa». File đọc được, vẫn 16 quy tắc và 6 ví dụ, độ dài còn xa giới hạn. Lời dặn gửi AI vẫn sạch, ảnh AI vẫn luôn ra «Minh họa». 18 file test liên quan qua hết.

Tôi thấy **1 lỗi Thấp, không chặn**: một ví dụ «alt xấu» ghi «đường Cộng Hòa». Đây là tên đường thật ở Tân Bình, trùng con đường có chi nhánh Pro-Metal (theo hồ sơ doanh nghiệp). Chính dòng nhắc mới trong file lại nói địa chỉ trong ví dụ phải là bịa. Không phải thông tin khách và không có số nhà, nên không nguy hiểm. Chỉ cần thay bằng tên đường bịa. Ngoài ra có 2 góp ý câu chữ, không bắt buộc.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t065.py` | Mới: 17 ca (16 qua, 1 `xfail(strict=True)` SL-T065-1). Kiểm yêu cầu 1–4, ghi chú LC-T062-1, chốt chặn số điện thoại đủ số, số nhà, email, địa chỉ web trong ví dụ (đề xuất 1 của Ngòi Bút), lời dặn sạch, ảnh AI ra «Minh họa» |
| `docs/team/reports/T-065-soi-loi.md` | Báo cáo này |

Không sửa `config/`, code ứng dụng hay test của agent khác.

## Kiểm từng mục

| Mục | Kết quả | Bằng chứng |
|---|---|---|
| Phạm vi diff | **ĐẠT** | `git diff --stat 998d626..team/T-065`: chỉ `config/content.toml` (19 dòng) và báo cáo Ngòi Bút. Trong `content.toml`, chỉ các dòng của `[alt]`, `[[alt.examples]]` và khối `#` ngay trên `[alt]` đổi; không đụng `seo_app/`, `app/`, `tests/` |
| Đọc được, đủ số lượng, trong giới hạn | **ĐẠT** | `load_alt_rules()`: 16 quy tắc, 6 ví dụ, 125/200. Đo bằng `format_rules`/`format_examples`: quy tắc 2.302 ký tự (file lưu kiểu Mac NFD: 2.828), ví dụ 2.455 (NFD: 3.035), giới hạn 4.000. Alt tốt dài nhất 93/125. Khớp số Ngòi Bút báo |
| YC1 chữ trong ảnh | **ĐẠT** | `config/content.toml:116` đúng nguyên văn phiếu; bản cũ «không chép vào alt» không còn. Test `test_yc1_text_in_image_rule_is_verbatim_and_covers_caption` |
| YC2 quy tắc chú thích | **ĐẠT** (góp ý SL-T065-2) | `:121`, quy tắc cuối, bắt đầu «Chú thích (caption)», có câu phiếu. Phần thêm «hỏng chỗ nào, vì sao hỏng nếu ảnh cho thấy rõ» hợp lý, không trái quy tắc 1. Test `test_yc2_caption_rule_is_last_and_forbids_what_alt_forbids` |
| YC3 bỏ «phường» | **ĐẠT** | `:114`; cả mục `[alt]` (quy tắc lẫn 5 trường ví dụ) không còn chữ «phường». Test `test_yc3_no_ward_level_in_alt_section` |
| YC4 (SL-T051-7) | **ĐẠT** (góp ý SL-T065-3) | Ví dụ 1 `:135` không còn «làm» (đoán nguyên nhân); ví dụ 4 `:156` «sau khi sơn lại» khớp hạng mục «sơn». Máy dò T-051: 6 bản tốt sạch, 6 bản xấu đều sai thật. Test mới: không alt tốt nào có từ nối nguyên nhân (làm, do, vì, nên, khiến, bởi); động từ sau «trước khi/sau khi» là việc ở thẻ hạng mục (kiểm 3 ví dụ) |
| LC-T062-1 | **ĐẠT** | Khối `#` trên `[alt]` (`:87-90`) và trên `[[alt.examples]]` đầu tiên (`:129-131`) nói rõ gửi nguyên văn cho hãng AI, chỉ dùng tên, số điện thoại, địa chỉ bịa, không chép khách thật. Đúng với code: `format_rules`/`format_examples` (`seo_app/images/alt.py:207-234`) đưa nguyên `rules` và 5 trường ví dụ vào lời dặn; `bad_starts` không gửi. Dòng `#` không tới AI. Test `test_lc_t062_1_notes_above_alt_and_examples_say_text_goes_to_ai_verbatim`, `test_comment_lines_never_reach_the_ai` |
| Không có thông tin trông như thật | **Có lỗi Thấp** (SL-T065-1) | Không có số điện thoại đủ số (chỉ «0909 xxx xxx»), số nhà, email, địa chỉ web. Tên người, tên cửa hàng («anh Tuấn», «chị Lan», «Minh Phát») là tên bịa thông dụng, Lá Chắn T-062 đã chấp nhận. Riêng «đường Cộng Hòa» là tên đường thật (xem SL-T065-1) |
| Lời dặn qua bộ lọc khung dữ liệu | **ĐẠT** | Phần lấy từ `config/` không có `<`, `>`, `du_lieu`, `` ``` ``, `\`, không có ký tự điều khiển hay vô hình, đã ở dạng NFC. Khung cố định `ALT_SYSTEM` đứng trước, quy tắc rồi ví dụ đứng sau; số lần xuất hiện nhãn khung trong lời dặn đúng bằng trong `ALT_SYSTEM` |
| Ảnh AI vẫn ra «Minh họa» | **ĐẠT** | Test của T-051, T-062, T-068 qua. Thêm 3 ca với quy tắc thật: AI quên tiền tố, tự viết «Hình minh họa…», viết «Minh họa: …» ở chú thích. Cả 3 ra alt «Minh họa …» đúng một lần, chú thích bắt đầu «Ảnh minh họa (AI)»; ảnh AI không gửi thẻ |

## Lỗi và góp ý

| Mã | Mức | Mô tả | Ai sửa |
|---|---|---|---|
| SL-T065-1 | Thấp | Ví dụ 3, bản xấu (`config/content.toml:150`) ghi «cửa hàng Minh Phát, 0909 xxx xxx, **đường Cộng Hòa**», thẻ khu vực Tân Bình. Cộng Hòa là đường thật ở Tân Bình và là địa chỉ chi nhánh thật của Pro-Metal (`config/business_profile.md:54`, «249 Cộng Hòa, P.13, Tân Bình»). Trái dòng nhắc mới ngay trong file (`:129-131` «địa chỉ trong ví dụ phải là bịa») và gợi ý LC-T062-1 («không chép … tên đường thật»). Không phải dữ liệu khách, không có số nhà, nên chỉ là Thấp. Sửa: thay bằng tên đường bịa có chữ hoa sau «đường» (ví dụ «đường Hoa Sứ»), để máy dò T-051 vẫn nhận ra «tên đường». Không cần sửa `vi_sao` | Ngòi Bút, trước khi gộp T-065 hoặc cùng phiếu dọn trước T-056; không chặn |
| SL-T065-2 | Góp ý | Câu YC2 «Không ghi vào chú thích điều mà các quy tắc trên cấm ghi trong alt» rộng hơn ý phiếu: đọc theo chữ thì kéo cả quy tắc **hình thức** của alt sang chú thích. Quy tắc 5 cấm mở đầu bằng «Ảnh», nên chú thích cũng không được mở đầu bằng «Ảnh». Nhưng quy tắc 15 lại đòi chú thích ảnh AI mở đầu «Ảnh minh họa (AI)». Quy tắc 4 («không quá max_chars», «không chấm câu ở cuối») cũng lệch với giới hạn riêng của chú thích. Không gây hại: code luôn tự ghi tiền tố cho ảnh AI (`clean_suggestion`), và câu chữ đúng nguyên văn phiếu. Nếu muốn rõ hơn, có thể viết «Không ghi vào chú thích **thông tin** mà các quy tắc trên cấm ghi trong alt (tên, số, địa chỉ, khu vực, trước/sau, quảng cáo…)» | Ngòi Bút / Chỉ Huy, nếu muốn; không chặn, không có test |
| SL-T065-3 | Góp ý | Ví dụ 3, bản tốt «Cửa cuốn **kẹt** lưng chừng…»: ô `anh` chỉ nói «kéo lên lưng chừng, lá cửa bên trái lệch khỏi ray». «Kẹt» là suy ra, cùng loại với điều SL-T051-7 nêu, nhưng nhẹ hơn vì trật ray thường đi kèm kẹt. Có thể đổi thành «Cửa cuốn dừng lưng chừng…» | Ngòi Bút, nếu muốn; không chặn |

### Cách tái hiện SL-T065-1

`uv run pytest tests/test_soi_loi_t065.py --runxfail -k sl_t065_1`. Mong đợi: không tên đường nào trong ví dụ trùng địa chỉ thật trong hồ sơ doanh nghiệp. Thực tế: `['Cộng Hòa']`. Giới hạn của test: chỉ so với địa chỉ trong `config/business_profile.md`; tên đường thật khác (không có trong hồ sơ) thì máy không biết, vẫn cần người đọc.

## Bằng chứng

```
$ git pull                       # wt-T-065, đầu phiên
Already up to date.              # HEAD bded957, cha 998d626

$ uv run pytest tests/test_soi_loi_t051.py tests/test_t062_content_config.py \
    tests/test_t062_alt_prompt.py tests/test_t062_image_config.py tests/test_soi_loi_t062.py \
    tests/test_soi_loi_t068.py tests/test_ai_images.py tests/test_config_tolerance.py \
    tests/test_soi_loi_round3.py tests/test_soi_loi_t003_t009.py tests/test_soi_loi_t019.py \
    tests/test_soi_loi_t024.py tests/test_drafts_images.py tests/test_images_tags.py \
    tests/test_soi_loi_t050.py tests/test_soi_loi_t052.py tests/test_soi_loi_t054.py \
    tests/test_soi_loi_t055.py -q
2403 passed, 3 skipped, 47 xfailed in 240.91s (0:04:00)

$ uv run pytest tests/test_app_pages.py tests/test_soi_loi_t065.py tests/test_soi_loi_t051.py -q -rxX
XFAIL tests/test_soi_loi_t065.py::test_sl_t065_1_example_street_names_are_not_real_addresses_from_profile - SL-T065-1: …
75 passed, 1 xfailed in 32.68s

$ uv run pytest tests/test_soi_loi_t065.py --runxfail -k sl_t065
E       AssertionError: assert ['Cộng Hòa'] == []
1 failed, 16 deselected

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan tests/test_soi_loi_t065.py docs/team/reports/T-065-soi-loi.md
"results": {}
```

Chọn file test: mọi file trong `tests/` có `content.toml` hoặc `load_alt_rules` (10 file), mọi file nhập `seo_app.images.alt` (thêm 7 file), `tests/test_t062_image_config.py`, `tests/test_app_pages.py` và file mới. 47 `xfailed` là lỗi cũ đã ghi của các phiếu khác, không file nào thuộc T-065.

**Test mới có bắt được lỗi thật không:** tôi sửa thử một bản tạm của `content.toml` (12 cách) và chạy lại từng test. Cả 12 cách đều bị bắt: số điện thoại «0909.123.456», «+84 909 123 456»; «12 Lê Lợi», «số 12 đường …»; email; tên đường trong hồ sơ («đường Lê Lai»); «gỉ sét làm cánh xệ»; «sau khi sửa» với hạng mục sơn; trả lại «(quận, phường)»; trả lại «không chép vào alt»; bỏ câu YC2. Tên đường bịa («đường Hoa Sứ Bịa») thì qua, đúng ý.

## Đối chiếu tiêu chí xong

- [x] YC1–YC3 đúng nguyên văn phiếu (bảng trên, test `test_yc1…`, `test_yc2…`, `test_yc3…`).
- [x] YC4: ví dụ 1 và 4 đã sửa, không còn tự mâu thuẫn (máy dò T-051 và 2 test mới).
- [x] LC-T062-1: ghi chú có ở cả hai chỗ, không tới AI.
- [x] TOML đọc được, 16 quy tắc, 6 ví dụ, trong giới hạn kể cả bản NFD.
- [x] Lời dặn sạch, ảnh AI vẫn «Minh họa» (test T-051, T-062, T-068 và 4 ca mới).
- [ ] Ví dụ không còn địa chỉ trông như thật: còn «đường Cộng Hòa» (SL-T065-1, Thấp).
- [ ] Toàn bộ `uv run pytest` trên Windows: Chỉ Huy chạy khi gộp.

## Rủi ro và điểm cần chú ý

- Chưa có máy dò nào cho **chú thích** AI viết (ví dụ không có trường chú thích). Bảo vệ chính vẫn là `PRIVATE_INFO_RULE` trong code và bước duyệt tay ở T-056. Đồng ý với đề xuất 2 của Ngòi Bút: T-056 nên hiện chú thích cạnh alt khi duyệt.
- Chốt chặn số điện thoại và số nhà nay là test thật, nhưng tên người và tên đường thật thì máy không phân biệt được với tên bịa. Người sửa file vẫn phải đọc dòng nhắc.
- `suggest_alt` chưa được trang nào gọi (chờ T-056), nên thay đổi này chưa hiện trên giao diện.

## Đề xuất

1. **SL-T065-1 → Ngòi Bút:** thay «đường Cộng Hòa» ở ví dụ 3 bằng tên đường bịa. Sửa xong, test `test_sl_t065_1_…` báo XPASS: gỡ dấu `xfail` (Soi Lỗi hoặc Thợ Máy).
2. SL-T065-2, SL-T065-3: Chỉ Huy quyết có sửa câu chữ hay không; không ảnh hưởng an toàn.

## Câu hỏi cho chủ dự án

Không có.

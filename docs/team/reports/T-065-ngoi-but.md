# Báo cáo T-065 · Quy tắc alt: chữ trong ảnh không chép vào alt lẫn chú thích

| Mục | Nội dung |
|---|---|
| Agent | Ngòi Bút (`ngoi-but`) · model: Claude Opus 5.5 |
| Phiếu | [T-065](../tickets/T-065-quy-tac-alt-chu-trong-anh.md) |
| Ngày nộp | 2026-10-21 (lượt 1), 2026-10-22 (lượt 2, mục cuối báo cáo) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Quy tắc viết alt trong `config/content.toml` nay cấm chép chữ đọc được trong ảnh (biển hiệu, **tên cửa hàng, số điện thoại**, số nhà, biển số xe, tên người) vào **cả alt lẫn chú thích**. Trước đây chỉ cấm alt, nên AI có thể đưa tên cửa hàng của khách vào chú thích dưới ảnh.
- Quy tắc chú thích thêm một câu: điều gì cấm ghi trong alt thì cũng không ghi vào chú thích. Chú thích chỉ nói nguyên nhân hỏng khi ảnh cho thấy rõ, không đoán.
- Sửa 2 ví dụ alt cho đúng quy tắc của chính nó (ví dụ cổng gỉ không còn đoán nguyên nhân; ví dụ cửa kéo sơn lại ghi «sau khi sơn lại» thay vì «sau khi sửa»), bỏ chữ «phường» ở quy tắc khu vực cho khỏi lẫn.
- Thêm dòng nhắc ngay trong file: quy tắc và ví dụ được gửi nguyên văn cho hãng AI mỗi lần viết alt, nên chỉ dùng tên, số điện thoại, địa chỉ bịa, không bao giờ chép thông tin khách thật.
- Anh/chị không thấy gì khác trên giao diện; khác biệt nằm ở lời dặn gửi AI khi viết alt (màn hình chọn ảnh T-056).
- Lượt 2 (2026-10-22): sửa theo Soi Lỗi, xem mục [Lượt 2](#lượt-2-2026-10-22-sửa-theo-soi-lỗi) cuối báo cáo.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `config/content.toml` | Chỉ mục `[alt]`: 3 dòng quy tắc, 3 trường ví dụ, 2 khối chú thích (dòng `#`). Vẫn 16 quy tắc, 6 ví dụ |
| `docs/team/reports/T-065-ngoi-but.md` | Báo cáo này |

Không sửa `seo_app/**`, `app/**`, `tests/**`. `git diff --stat main`: `config/content.toml | 19 +++++++++++++------` (13 thêm, 6 bỏ).

## Trước / sau từng dòng

### Quy tắc (`[alt].rules`)

| Yêu cầu | Trước | Sau | Lý do |
|---|---|---|---|
| YC1 (`config/content.toml:116`) | Chữ đọc được trong ảnh (biển hiệu, số nhà, biển số xe, tên người) không chép vào alt | Chữ đọc được trong ảnh (biển hiệu, **tên cửa hàng, số điện thoại**, số nhà, biển số xe, tên người) không chép vào alt **hay chú thích** | Đúng nguyên văn phiếu và điều kiện C10 của Lá Chắn T-051 (LC-T051-1 a): đóng khe tên cửa hàng lọt vào chú thích |
| YC2 (`config/content.toml:121`) | Chú thích (caption) bổ sung điều alt chưa nói và có ích cho người đọc bài (đang sửa gì, vì sao hỏng), không lặp lại nguyên alt, không quá caption_max_chars ký tự | Chú thích (caption) bổ sung điều alt chưa nói và có ích cho người đọc bài (đang sửa gì, **hỏng chỗ nào, vì sao hỏng nếu ảnh cho thấy rõ**), không lặp lại nguyên alt, không quá caption_max_chars ký tự. **Không ghi vào chú thích điều mà các quy tắc trên cấm ghi trong alt** | Câu in đậm cuối là nguyên văn phiếu. Phần trong ngoặc là thêm của tôi (xem dưới) |
| YC3 (`config/content.toml:114`) | Khu vực **(quận, phường)** chỉ được nêu khi có trong thẻ ảnh, ảnh là ảnh thật, và chỉ ghi cấp quận/huyện. Không bao giờ ghi tên khách hay địa chỉ dù thẻ hoặc tên thư mục có chứa | Khu vực chỉ được nêu khi có trong thẻ ảnh, ảnh là ảnh thật, và chỉ ghi cấp quận/huyện. Không bao giờ ghi tên khách hay địa chỉ dù thẻ hoặc tên thư mục có chứa | Bỏ cả ngoặc «(quận, phường)» thay vì chỉ chữ «phường»: còn lại «(quận)» thì lặp ý với «chỉ ghi cấp quận/huyện» ngay sau. Câu không còn chữ nào cho phép ghi phường |

**Phần thêm ở YC2, vì sao.** Câu mới «không ghi vào chú thích điều mà các quy tắc trên cấm ghi trong alt» kéo quy tắc 1 («Không đoán điều ảnh không cho thấy») sang chú thích. Nếu giữ nguyên «vì sao hỏng», hai câu trong cùng một quy tắc lại ngược chiều: một bên bảo nêu nguyên nhân, một bên cấm đoán. Đây cũng chính là điều Soi Lỗi chỉ ra ở SL-T051-7 («gỉ sét làm cánh cổng xệ» là đoán nguyên nhân). Tôi giữ ý cũ (chú thích nói được nguyên nhân, có ích cho người đọc) và thêm điều kiện «nếu ảnh cho thấy rõ», cộng «hỏng chỗ nào» là điều luôn thấy được. Nếu Chỉ Huy muốn đúng chữ phiếu, chỉ cần trả phần trong ngoặc về «(đang sửa gì, vì sao hỏng)»: không test nào phụ thuộc.

### Ví dụ (`[[alt.examples]]`, góp ý SL-T051-7)

| Ví dụ | Trường | Trước | Sau | Lý do |
|---|---|---|---|---|
| 1 (cổng sắt gỉ, `:135`) | `tot` | Bản lề cửa cổng sắt gỉ sét **làm** cánh cổng xệ, chạm nền, trước khi sửa ở Bình Tân | Bản lề cửa cổng sắt **hai cánh gỉ sét nặng, một cánh xệ** chạm nền gạch, trước khi sửa ở Bình Tân | «làm cánh cổng xệ» nói gỉ là nguyên nhân, ảnh chỉ cho thấy hai việc cùng lúc. Bản mới tả đúng ô `anh` (hai cánh, gỉ nặng, một cánh xệ, chạm nền gạch). 93/125 ký tự |
| 3 (cửa cuốn có biển hiệu, `:151`) | `vi_sao` | Bản xấu mở đầu bằng «Hình ảnh», chép tên cửa hàng, số điện thoại, tên đường trong ảnh | … tên đường trong ảnh. **Chú thích cũng không được chép các chữ này** | Ví dụ này đúng là tình huống Lá Chắn nêu ở LC-T051-1 (biển «Minh Phát»): nhắc ngay trong ví dụ để AI không chuyển tên cửa hàng từ alt sang chú thích. Không thêm trường chú thích vào ví dụ vì bộ đọc và test chỉ nhận 5 trường `anh`, `the`, `tot`, `xau`, `vi_sao` |
| 4 (cửa kéo sơn lại, `:156`) | `tot` | Cửa kéo sắt sơn xanh vừa sơn lại, đóng kín, **sau khi sửa** ở Quận 3 | Cửa kéo sắt **sau khi sơn lại màu xanh**, đóng kín, ở Quận 3 | Hạng mục là sơn nên «sau khi sửa» lệch việc; câu cũ còn lặp «sơn… sơn». Thẻ vẫn là «sau» nên «sau khi sơn lại» đúng thẻ. 56/125 ký tự |

Ví dụ 2, 5, 6 và mọi bản «xau» giữ nguyên (đã đúng quy tắc, tên trong ví dụ là tên bịa, số điện thoại đã che).

### Chú thích trong file (dòng `#`, LC-T062-1)

Thêm ngay trên `[alt]` (`config/content.toml:87-90`):

```toml
# LƯU Ý: quy tắc (rules) và ví dụ ([[alt.examples]], kể cả bản «xau») của mục [alt] được gửi
# NGUYÊN VĂN cho hãng AI (hãng ghi ở [tasks.alt] trong config/ai.toml) mỗi lần viết alt.
# Chỉ dùng tên người, tên cửa hàng, số điện thoại, địa chỉ bịa; không bao giờ chép thông tin của
# khách thật vào đây. Dòng bắt đầu bằng # chỉ là ghi chú cho người sửa file, không gửi đi.
```

Thêm ngay trên `[[alt.examples]]` đầu tiên (`config/content.toml:129-131`):

```toml
# Mọi ví dụ, kể cả bản xau, được gửi nguyên văn cho hãng AI mỗi lần viết alt: tên người, tên cửa
# hàng, số điện thoại, địa chỉ trong ví dụ phải là bịa (số điện thoại che kiểu «0909 xxx xxx»),
# không bao giờ lấy từ công trình hay khách thật.
```

Đã đối chiếu với code: `format_rules` và `format_examples` (`seo_app/images/alt.py`) đưa nguyên chữ `rules` và cả 5 trường ví dụ vào lời dặn hệ thống; `bad_starts` không gửi đi, nên chú thích chỉ nói «quy tắc và ví dụ». Dòng `#` bị `tomllib` bỏ qua khi đọc, nên ghi chú không tới AI.

## Kiểm bằng ví dụ (đầu vào → đầu ra mong muốn)

| Ảnh | Thẻ | Alt mong muốn | Chú thích mong muốn | Chú thích không được viết |
|---|---|---|---|---|
| Ảnh thật: cửa cuốn kẹt lưng chừng, lá trái lệch ray, biển hiệu ghi tên cửa hàng và số điện thoại | sửa cửa cuốn · Tân Bình · trước | Cửa cuốn kẹt lưng chừng, lá cửa bên trái trật khỏi ray, trước khi sửa ở Tân Bình | Lá cửa bên trái đã trật khỏi ray nên cửa không kéo lên hết được | Cửa cuốn của cửa hàng Minh Phát bị trật ray, gọi 0909 xxx xxx (chép chữ biển hiệu: YC1, YC2) |
| Ảnh thật: bản lề cổng gỉ nặng, một cánh xệ chạm nền | sửa cửa cổng · Bình Tân · trước | Bản lề cửa cổng sắt hai cánh gỉ sét nặng, một cánh xệ chạm nền gạch, trước khi sửa ở Bình Tân | Cánh xệ thấp hơn cánh còn lại, mép dưới chạm hẳn nền gạch | Cổng xệ do nhà để lâu không bảo dưỡng, nước mưa đọng (đoán nguyên nhân ảnh không cho thấy) |
| Ảnh thật: cửa kéo vừa sơn xanh | sơn cửa kéo · Quận 3 · sau | Cửa kéo sắt sau khi sơn lại màu xanh, đóng kín, ở Quận 3 | Cửa kéo đã sơn lại toàn bộ một màu xanh | Cửa kéo nhà số 12, đường <tên đường thật> sau khi sơn (số nhà, tên đường: quy tắc «Không bịa…», «Không bao giờ ghi… địa chỉ») |

Lời dặn đầy đủ sau khi sửa đã in ra và đọc lại từng dòng: 16 quy tắc đúng thứ tự, quy tắc chú thích vẫn đứng cuối, 6 ví dụ đều có nhãn «Không nên viết … Vì sao».

## Bằng chứng

```
$ uv run pytest tests/test_soi_loi_t051.py tests/test_t062_content_config.py tests/test_t062_alt_prompt.py \
    tests/test_soi_loi_t062.py tests/test_ai_images.py tests/test_config_tolerance.py \
    tests/test_soi_loi_round3.py tests/test_soi_loi_t003_t009.py tests/test_soi_loi_t019.py \
    tests/test_soi_loi_t024.py tests/test_drafts_images.py tests/test_images_tags.py \
    tests/test_soi_loi_t050.py tests/test_soi_loi_t052.py tests/test_soi_loi_t054.py \
    tests/test_soi_loi_t055.py tests/test_soi_loi_t068.py tests/test_app_pages.py
1 failed, 2401 passed, 3 skipped, 47 xfailed in 702.87s (0:11:42)
FAILED tests/test_soi_loi_t062.py::test_models_tab_with_image_enabled_and_only_claude_key
  RuntimeError: AppTest script run timed out after 30(s)

$ uv run pytest "tests/test_soi_loi_t062.py::test_models_tab_with_image_enabled_and_only_claude_key"
1 passed in 19.48s

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan config/content.toml
"results": {}
```

Kết quả: **2.402 qua, 0 hỏng thật**. Test duy nhất báo hỏng là hỏng oan vì quá giờ: AppTest mở trang Cài đặt quá 30 giây trong lúc máy đang chạy song song một lượt pytest toàn bộ và 2 agent khác. Chạy riêng thì qua (19,5 giây). Test này dùng một `config/ai.toml` tạm và trang Cài đặt, không đọc mục `[alt]`, nên không liên quan tới thay đổi của phiếu.

Chọn file test: mọi file trong `tests/` có `content.toml`, `load_alt_rules` hoặc `[alt]` (10 file), mọi file nhập `seo_app.images.alt` (thêm 7 file), và `tests/test_app_pages.py`. Không có test nào so nguyên chữ các dòng đã đổi (`grep` «gỉ sét làm», «vừa sơn lại, đóng kín», «quận, phường», «vì sao hỏng» ngoài `docs/`: chỉ còn `config/content.toml` và ô `anh` không đổi của ví dụ 4).

Các giới hạn code kiểm khi nạp (đo bằng `format_rules`, `format_examples` trên file thật, cả bản lưu kiểu Mac NFD như `test_content_toml_saved_as_nfd_on_mac_reads_the_same`):

| Phần | Trước | Sau | Giới hạn |
|---|---|---|---|
| Quy tắc, NFC | 2.172 | 2.302 | 4.000 (`GUIDANCE_MAX_LENGTH`) |
| Quy tắc, NFD (Mac) | 2.669 | 2.828 | 4.000 |
| Ví dụ, NFC | 2.405 | 2.455 | 4.000 (`EXAMPLES_MAX_LENGTH`) |
| Ví dụ, NFD (Mac) | 2.974 | 3.035 | 4.000 |
| Số quy tắc / ví dụ | 16 / 6 | 16 / 6 | test đòi đúng 16 và 6, quy tắc cuối bắt đầu «Chú thích (caption)» |
| Alt dài nhất trong ví dụ | 80 | 93 | 125 (`max_chars`) |

Tên khóa dạng `a_b` trong quy tắc vẫn chỉ có `max_chars`, `caption_max_chars` (`test_limits_named_in_rules_exist_in_alt_section`).

## Đối chiếu tiêu chí xong

- [x] YC1: `config/content.toml:116`, đúng nguyên văn phiếu; test `test_alt_rules_cover_ticket_requirements`, trường hợp «chữ trong ảnh không chép».
- [x] YC2: `config/content.toml:121`, câu phiếu nằm cuối quy tắc chú thích; quy tắc này vẫn là quy tắc cuối (`test_project_content_toml_images_and_alt`, `test_project_rules_and_examples_reach_ai_whole`).
- [x] YC3: `config/content.toml:114`, không còn chữ «phường» trong `[alt]`.
- [x] YC4 (SL-T051-7): ví dụ 1 và 4 đã sửa; máy dò vi phạm của Soi Lỗi vẫn thấy cả 6 bản tốt sạch, cả 6 bản xấu sai thật (`test_good_examples_follow_their_own_rules`, `test_bad_examples_really_break_a_rule`).
- [x] LC-T062-1: chú thích trên `[alt]` (`:87-90`) và trên `[[alt.examples]]` (`:129-131`).
- [x] File TOML đọc được, giới hạn độ dài và số ví dụ vẫn thỏa (bảng trên); test liên quan qua, `ruff` sạch.
- [x] Báo cáo nộp tại `docs/team/reports/T-065-ngoi-but.md`.
- [ ] Toàn bộ `uv run pytest` trên Windows: Chỉ Huy chạy khi gộp (chủ dự án chốt 2026-10-20).

## Rủi ro và điểm cần chú ý

- Quy tắc trong `config/` chỉ là phần **bổ sung**. Bảo vệ chính nằm trong code từ T-062: `PRIVATE_INFO_RULE` trong `seo_app/images/alt.py` đã cấm tên cửa hàng, chữ trên biển hiệu, số điện thoại… cho **cả alt lẫn chú thích**, sửa `config/` không gỡ được. Phiếu này làm cho quy tắc cấu hình nói cùng chiều với code, không thay nó.
- Chưa có máy dò nào cho **chú thích**: test của Soi Lỗi chỉ dò alt trong ví dụ, ví dụ không có trường chú thích. Chú thích AI viết vẫn dựa vào lời dặn và bước anh/chị duyệt từng ảnh ở T-056.
- Lời nhắc «chỉ dùng thông tin bịa» chỉ là ghi chú, không có gì chặn ai lỡ chép số điện thoại thật vào ví dụ (xem Đề xuất 1).
- Quy tắc 12 vẫn chỉ nêu «trước/sau khi sửa». Ví dụ 4 nay dùng «sau khi sơn lại» theo đúng thẻ «sau» và hạng mục sơn; tôi không đổi quy tắc 12 vì phiếu chỉ cho sửa ví dụ ở YC4.

## Đề xuất

1. **Soi Lỗi / Thợ Máy (nhỏ, không gấp):** thêm test cho `config/content.toml` thật: không ví dụ nào trong `[[alt.examples]]` chứa số điện thoại đủ chữ số (ví dụ mẫu `0\d{8,10}` sau khi bỏ dấu cách, dấu chấm), chỉ chấp nhận số đã che kiểu «0909 xxx xxx». Biến lời nhắc LC-T062-1 thành chốt chặn thật.
2. **T-056 (giao diện duyệt alt):** nên hiện chú thích cạnh alt khi duyệt, để người duyệt thấy cả hai trước khi gửi bài (chú thích là nơi LC-T051-1 có thể lọt).

## Câu hỏi cho chủ dự án

Không có.

## Lượt 2 (2026-10-22): sửa theo Soi Lỗi

Chỉ Huy B giao, chủ dự án đã duyệt. Sửa theo biên bản [Soi Lỗi T-065](T-065-soi-loi.md) (đầu nhánh trước khi sửa `8f41ba0`): lỗi Thấp SL-T065-1 và 2 góp ý câu chữ SL-T065-2, SL-T065-3. Chỉ sửa `config/content.toml` mục `[alt]` và gỡ dấu `xfail` SL-T065-1 trong `tests/test_soi_loi_t065.py`.

### Tóm tắt lượt 2 (cho chủ dự án)

- Một ví dụ «alt không nên viết» ghi «đường Cộng Hòa». Đó là tên đường thật, trùng con đường có chi nhánh Pro-Metal ở Tân Bình. Nay đổi thành «đường Mây Trắng», tên tôi tự đặt: tra trên mạng không thấy đường nào ở TP.HCM mang tên này, hồ sơ doanh nghiệp cũng không có. Tên Soi Lỗi gợi ý («Hoa Sứ») là đường có thật ở Phú Nhuận nên tôi không dùng.
- Đã soát lại mọi tên, số, địa chỉ còn lại trong mục alt. Tất cả đều là tên bịa thông dụng, số điện thoại đã che, hoặc tên quận dùng làm thẻ khu vực.
- Câu «không ghi vào chú thích điều mà các quy tắc trên cấm ghi trong alt» giữ đúng chữ phiếu. Tôi thêm phần nói rõ đó là những loại thông tin nào. Phần thêm cũng nói rõ độ dài, dấu câu, chữ mở đầu của chú thích không theo quy tắc của alt, nên chú thích ảnh AI vẫn mở đầu bằng «Ảnh minh họa (AI)» mà không trái quy tắc nào.
- Ví dụ cửa cuốn đổi «kẹt lưng chừng» thành «kéo lên lưng chừng»: ảnh chỉ cho thấy cửa đang ở lưng chừng, không cho thấy cửa bị kẹt.

### Trước / sau

| Mã | Chỗ | Trước | Sau |
|---|---|---|---|
| SL-T065-1 | Ví dụ 3, `xau` (`config/content.toml:150`) | Hình ảnh cửa cuốn của cửa hàng Minh Phát, 0909 xxx xxx, đường **Cộng Hòa** | Hình ảnh cửa cuốn của cửa hàng Minh Phát, 0909 xxx xxx, đường **Mây Trắng** |
| SL-T065-1 (kèm) | Ví dụ 3, `anh` (`:147`) | Ảnh thật: … có biển hiệu cửa hàng ghi tên và số điện thoại | Ảnh thật: … có biển hiệu cửa hàng ghi tên, số điện thoại **và tên đường** |
| SL-T065-3 | Ví dụ 3, `tot` (`:149`) | Cửa cuốn **kẹt** lưng chừng, lá cửa bên trái trật khỏi ray, trước khi sửa ở Tân Bình | Cửa cuốn **kéo lên** lưng chừng, lá cửa bên trái trật khỏi ray, trước khi sửa ở Tân Bình |
| SL-T065-2 | Quy tắc 16, chú thích (`:121`) | … không quá caption_max_chars ký tự. Không ghi vào chú thích điều mà các quy tắc trên cấm ghi trong alt | … không quá caption_max_chars ký tự. Không ghi vào chú thích điều mà các quy tắc trên cấm ghi trong alt **(thông tin cá nhân, chữ trong ảnh, khu vực hay trước/sau không có trong thẻ, quảng cáo, điều ảnh không cho thấy, tả ảnh AI như công trình thật…); riêng độ dài, dấu câu và chữ mở đầu thì chú thích theo quy tắc này và quy tắc ảnh AI, không theo quy tắc của alt** |
| Gỡ dấu | `tests/test_soi_loi_t065.py:173` | `@pytest.mark.xfail(strict=True, reason="SL-T065-1: …")` | `# SL-T065-1: đã sửa ở T-065 lượt 2 (…), gỡ xfail.` Thân test giữ nguyên, không đổi điều kiện kiểm |

`git diff --stat 8f41ba0`: `config/content.toml` đổi 4 dòng; `tests/test_soi_loi_t065.py` bỏ 9 dòng decorator, thêm 1 dòng chú thích.

### SL-T065-1: chọn tên đường bịa

- **«Mây Trắng»:** không có trong `config/business_profile.md` (so chữ thường, đã chuẩn hóa NFC, như test SL-T065-1). Tìm trên web `"đường Mây Trắng" TP.HCM` không ra đường nào, chỉ ra bài báo và danh bạ không liên quan. Trong các tên đường TP.HCM tôi biết cũng không có. Đường ở TP.HCM phần lớn đặt theo tên người, địa danh, sự kiện, nên một cụm tả cảnh như «Mây Trắng» khó trùng.
- **Không dùng «Hoa Sứ» (gợi ý của Soi Lỗi):** đây là đường có thật ở Phú Nhuận, nhiều tin cho thuê nhà ghi «đường Hoa Sứ, Phú Nhuận» (ví dụ [guland.vn](https://guland.vn/cho-thue-bat-dong-san-duong-hoa-su-quan-phu-nhuan-tp-ho-chi-minh), [muaban.net](https://muaban.net/bat-dong-san/cho-thue-can-ho-duong-hoa-su-quan-phu-nhuan-ho-chi-minh)). Test SL-T065-1 chỉ so với hồ sơ doanh nghiệp nên tên này vẫn qua test: ở chỗ này máy không thay được người đọc.
- **Giữ dạng «đường» + chữ hoa:** máy dò của T-051 (`_STREET`) vẫn nhận ra bản xấu có tên đường, và test SL-T065-1 vẫn có tên đường để kiểm (test đòi tìm thấy ít nhất một tên).
- **Sửa kèm ô `anh`:** lý do của bản xấu ghi «chép … tên đường trong ảnh», nhưng ô `anh` trước đây chỉ nói biển hiệu ghi tên và số điện thoại. Nay thêm «và tên đường» cho khớp: AI thấy rõ tên đường nằm trên biển hiệu, tức là chữ đọc được trong ảnh (quy tắc 13).
- **Nhận lỗi lượt 1:** ở lượt 1 tôi ghi «tên trong ví dụ là tên bịa» nhưng sót «Cộng Hòa». Bản xấu này có từ T-051, và lượt 1 tôi không đọc lại nó theo dòng nhắc vừa thêm.

### Soát lại mọi tên, số, địa chỉ trong `[alt]`

Dò bằng máy trên mọi chữ sẽ tới AI (16 quy tắc và 5 trường của 6 ví dụ: chữ viết hoa giữa câu, chữ số), rồi đọc lại từng chỗ:

| Loại | Có trong `[alt]` | Kết luận |
|---|---|---|
| Tên người | «anh Tuấn» (ví dụ 2, bản xấu), «chị Lan» (ví dụ 6, bản xấu) | Tên bịa thông dụng, không kèm địa chỉ hay số |
| Tên cửa hàng | «Minh Phát» (ví dụ 3, bản xấu) | Tên bịa, rất thông dụng. Nay đi cùng tên đường bịa và số đã che, nên không chỉ tới cửa hàng thật nào |
| Tên đường | «Mây Trắng» (ví dụ 3, bản xấu) | Bịa (mục trên). Không còn tên đường nào khác |
| Số điện thoại | «0909 xxx xxx» (ví dụ 3, bản xấu) | Đã che. Test `test_rules_and_examples_have_no_real_looking_phone_number` qua |
| Số nhà, email, địa chỉ web | Không có | Test `test_rules_and_examples_have_no_house_number_email_or_web_address` qua |
| Số khác | «30 phút» (ví dụ 2), «10 năm» (ví dụ 4), đều ở bản xấu | Là lỗi «bịa số liệu» mà bản xấu cố ý mắc, không phải thông tin của ai |
| Khu vực | Bình Tân, Tân Bình, Quận 3 (thẻ và alt tốt); Quận 7, Gò Vấp (bản xấu) | Tên quận, đúng thiết kế thẻ khu vực (chỉ cấp quận/huyện), không phải địa chỉ |
| Tên doanh nghiệp | «Pro-Metal» (quy tắc 9, 14; bản xấu ví dụ 2, 5, 6) | Chính doanh nghiệp, không phải thông tin khách |

### SL-T065-2: câu về chú thích

- Soi Lỗi đúng: đọc theo chữ, «điều mà các quy tắc trên cấm ghi trong alt» kéo cả quy tắc **hình thức** của alt sang chú thích. Quy tắc 5 cấm mở đầu bằng «Ảnh», trong khi quy tắc 15 đòi chú thích ảnh AI mở đầu «Ảnh minh họa (AI)». Quy tắc 4 thì có «không quá max_chars», «không chấm câu ở cuối».
- **Không đổi «điều» thành «thông tin» như gợi ý:** câu này là nguyên văn phiếu (YC2), và test `test_yc2_caption_rule_is_last_and_forbids_what_alt_forbids` kiểm đúng nguyên văn đó; Chỉ Huy dặn không đổi điều kiện kiểm. Thay vào đó tôi thêm phần giải thích ngay sau câu. Trong ngoặc là các loại thông tin bị cấm, danh sách mở (có «…»), nên không làm hẹp câu gốc. Sau dấu chấm phẩy: độ dài, dấu câu, chữ mở đầu của chú thích theo quy tắc chú thích và quy tắc ảnh AI, không theo quy tắc của alt.
- **Khớp với code:** `clean_suggestion` (`seo_app/images/alt.py:413-446`) chỉ bỏ dấu câu cuối của alt, giữ dấu câu của chú thích, và tự ghi tiền tố «Ảnh minh họa (AI)» cho chú thích ảnh AI.
- **Thêm «tả ảnh AI như công trình thật» vào danh sách** vì đây là lỗi chú thích ảnh AI dễ mắc nhất: code chỉ bảo đảm tiền tố, phần sau tiền tố vẫn có thể là «Pro-Metal vừa thi công…».
- Quy tắc chú thích nay dài 522 ký tự, vẫn là một quy tắc và vẫn đứng cuối. Tổng quy tắc 2.561/4.000 ký tự (bảng dưới).

### SL-T065-3: «kẹt» ở ví dụ 3

Đồng ý: ô `anh` chỉ nói cửa «kéo lên lưng chừng» và lá trái lệch ray, «kẹt» là suy ra. Tôi chọn «kéo lên lưng chừng» (đúng chữ của ô `anh`) thay vì «dừng lưng chừng» như Soi Lỗi gợi ý, vì «dừng» cũng ngầm ý cửa đang chạy thì tự dừng. «Trật khỏi ray» giữ nguyên: nhìn thấy được, và là từ thợ hay dùng (quy tắc 1, 3).

Bảng «Kiểm bằng ví dụ» ở lượt 1 mắc cùng lỗi. Dòng đầu dùng alt «Cửa cuốn kẹt lưng chừng…», còn chú thích mong muốn «Lá cửa bên trái đã trật khỏi ray nên cửa không kéo lên hết được» cũng là suy ra: ảnh không cho thấy cửa còn kéo được hay không. Dòng đó nay đọc là:

| Ảnh | Thẻ | Alt mong muốn | Chú thích mong muốn | Chú thích không được viết |
|---|---|---|---|---|
| Ảnh thật: cửa cuốn kéo lên lưng chừng, lá trái lệch ray, biển hiệu ghi tên cửa hàng, số điện thoại, tên đường | sửa cửa cuốn · Tân Bình · trước | Cửa cuốn kéo lên lưng chừng, lá cửa bên trái trật khỏi ray, trước khi sửa ở Tân Bình | Lá cửa bên trái lệch hẳn ra ngoài ray, lúc này không nên cố kéo cửa lên xuống | Cửa cuốn của cửa hàng Minh Phát trên đường Mây Trắng bị trật ray (chép chữ biển hiệu: quy tắc 13, câu cuối quy tắc 16) |

### Bằng chứng lượt 2

```
$ uv run pytest tests/test_soi_loi_t065.py -rxX          # cấu hình mới, trước khi gỡ xfail
[XPASS(strict)] SL-T065-1: ví dụ 3 (bản xấu) ghi «đường Cộng Hòa», …
1 failed, 16 passed in 1.60s

$ uv run pytest -rxX tests/test_soi_loi_t065.py tests/test_soi_loi_t051.py \
    tests/test_t062_content_config.py tests/test_t062_alt_prompt.py tests/test_t062_image_config.py \
    tests/test_soi_loi_t062.py tests/test_ai_images.py tests/test_config_tolerance.py \
    tests/test_soi_loi_round3.py tests/test_soi_loi_t003_t009.py tests/test_soi_loi_t019.py \
    tests/test_soi_loi_t024.py tests/test_drafts_images.py tests/test_images_tags.py \
    tests/test_soi_loi_t050.py tests/test_soi_loi_t052.py tests/test_soi_loi_t054.py \
    tests/test_soi_loi_t055.py tests/test_soi_loi_t068.py tests/test_app_pages.py
2438 passed, 3 skipped, 47 xfailed in 276.62s (0:04:36)
# 47 xfail đều là lỗi cũ đã ghi của phiếu khác (t003_t009: 1, t050: 15, t054: 4, t055: 4,
# t068: 23); không còn xfail nào trong tests/test_soi_loi_t065.py

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan config/content.toml tests/test_soi_loi_t065.py
"results": {}
```

Độ dài sau lượt 2 (đo như lượt 1, cả bản lưu kiểu Mac NFD):

| Phần | Lượt 1 | Lượt 2 | Giới hạn |
|---|---|---|---|
| Quy tắc, NFC | 2.302 | 2.561 | 4.000 (`GUIDANCE_MAX_LENGTH`) |
| Quy tắc, NFD (Mac) | 2.828 | 3.144 | 4.000; test Soi Lỗi đòi dưới 4.000 |
| Ví dụ, NFC | 2.455 | 2.471 | 4.000 (`EXAMPLES_MAX_LENGTH`) |
| Ví dụ, NFD (Mac) | 3.035 | 3.056 | 4.000 |
| Số quy tắc / ví dụ | 16 / 6 | 16 / 6 | đúng 16 và 6 |
| Alt tốt dài nhất | 93 | 93 (ví dụ 3: 80 → 84) | 125 |

### Đối chiếu lượt 2

- [x] SL-T065-1: ví dụ 3 dùng tên đường bịa «Mây Trắng» (`config/content.toml:150`); test SL-T065-1 qua khi không còn `xfail`. Mọi tên, số, địa chỉ khác đã soát (bảng trên).
- [x] Gỡ `xfail` SL-T065-1, không đổi thân test (`tests/test_soi_loi_t065.py:173`).
- [x] SL-T065-2: đã làm, giữ nguyên văn phiếu, thêm phần giải thích (`:121`).
- [x] SL-T065-3: đã làm (`:149`); dòng ví dụ lượt 1 đã thay ở trên.
- [x] Chỉ sửa mục `[alt]` và dấu `xfail`; test liên quan qua, `ruff` sạch.

### Rủi ro lượt 2

- Không chứng minh tuyệt đối được «Mây Trắng» không trùng đường nào: TP.HCM có hàng nghìn tên đường, cộng thêm đường nội bộ ở các khu dân cư mới. Tôi đã tra web và hồ sơ doanh nghiệp. Nếu sau này phát hiện trùng thì chỉ cần đổi hai chữ ở `config/content.toml:150`.
- Test SL-T065-1 chỉ so tên đường với hồ sơ doanh nghiệp, nên chưa bắt được tên đường thật nằm ngoài hồ sơ (trường hợp «Hoa Sứ»). Người sửa file vẫn phải đọc dòng nhắc ở `:129-131`.

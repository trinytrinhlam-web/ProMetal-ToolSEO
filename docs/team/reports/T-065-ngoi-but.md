# Báo cáo T-065 · Quy tắc alt: chữ trong ảnh không chép vào alt lẫn chú thích

| Mục | Nội dung |
|---|---|
| Agent | Ngòi Bút (`ngoi-but`) · model: Claude Opus 5.5 |
| Phiếu | [T-065](../tickets/T-065-quy-tac-alt-chu-trong-anh.md) |
| Ngày nộp | 2026-10-21 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Quy tắc viết alt trong `config/content.toml` nay cấm chép chữ đọc được trong ảnh (biển hiệu, **tên cửa hàng, số điện thoại**, số nhà, biển số xe, tên người) vào **cả alt lẫn chú thích**. Trước đây chỉ cấm alt, nên AI có thể đưa tên cửa hàng của khách vào chú thích dưới ảnh.
- Quy tắc chú thích thêm một câu: điều gì cấm ghi trong alt thì cũng không ghi vào chú thích. Chú thích chỉ nói nguyên nhân hỏng khi ảnh cho thấy rõ, không đoán.
- Sửa 2 ví dụ alt cho đúng quy tắc của chính nó (ví dụ cổng gỉ không còn đoán nguyên nhân; ví dụ cửa kéo sơn lại ghi «sau khi sơn lại» thay vì «sau khi sửa»), bỏ chữ «phường» ở quy tắc khu vực cho khỏi lẫn.
- Thêm dòng nhắc ngay trong file: quy tắc và ví dụ được gửi nguyên văn cho hãng AI mỗi lần viết alt, nên chỉ dùng tên, số điện thoại, địa chỉ bịa, không bao giờ chép thông tin khách thật.
- Anh/chị không thấy gì khác trên giao diện; khác biệt nằm ở lời dặn gửi AI khi viết alt (màn hình chọn ảnh T-056).

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

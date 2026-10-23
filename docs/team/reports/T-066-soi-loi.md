# Báo cáo T-066 · Dọn lỗi Thấp lớp ảnh gửi AI · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-066](../tickets/T-066-don-loi-thap-anh-gui-ai.md) |
| Ngày nộp | 2026-10-23 |
| Kết quả | Hoàn thành (kiểm rút gọn). **Kết luận: ĐẠT**, chuyển Lá Chắn rút gọn được |

## Tóm tắt (cho chủ dự án)

- Bộ kiểm cuối cùng trước khi ảnh tới hãng AI giờ từ chối mọi "hồ sơ màu" và các khối kỹ thuật bị lặp hay dài hơn bình thường, đúng như phiếu yêu cầu. 15 lỗi cũ còn treo từ T-050 nay bị chặn thật, đúng chỗ.
- **Ảnh thật không bị chặn oan.** Tôi cho phần mềm chuẩn bị bản gửi AI từ 446 ảnh gốc: ảnh điện thoại có GPS, hồ sơ màu, ghi chú; PNG, WebP, HEIC của iPhone; ảnh xoay đủ 8 hướng, ảnh xám, ảnh trong suốt, ảnh nhiều khung; từ 1×1 tới 6000×4000 điểm ảnh; 400 ảnh trong số đó sinh ngẫu nhiên. Cả 892 bản (bản gửi AI và ảnh xem trước) đều qua, không bản nào còn GPS, hồ sơ màu hay chữ của ảnh gốc.
- Tôi thử thêm 2 triệu tệp bị sửa hỏng hay dựng cố ý. Không tệp nào lọt qua mà thư viện ảnh vẫn đọc ra hồ sơ màu, EXIF, XMP hay chữ; bộ kiểm không lần nào gặp lỗi lạ; không tệp nào bản mới nhận mà bản cũ chặn. Ảnh thật 4–5 MB kiểm mất dưới 0,05 giây.
- **Không có lỗi mới.** Thêm 27 test.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t066.py` | Mới, 27 ca, đều qua. (1) Bản gửi AI thật từ 5 nguồn chưa có test (MPO 3 khung, PNG động, WebP động, PNG RGB 16 bit có `iCCP`, JPEG 1×1) và đủ 8 hướng xoay EXIF. (2) 12 cách giấu hồ sơ màu ở khối khác loại: đều bị từ chối. (3) "Trọng tài Pillow": 4.000 ảnh đột biến (hạt giống cố định); ảnh nào lớp kiểm nhận thì Pillow không đọc ra metadata; có đối chứng để trọng tài không "mù" |
| `docs/team/reports/T-066-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác.

## Kiểm từng yêu cầu

| Yêu cầu | Kết quả | Bằng chứng |
|---|---|---|
| YC1 · mọi hồ sơ màu bị từ chối | **ĐẠT** | APP2 không còn trong danh sách APPn (`seo_app/ai/base.py:580`), `iCCP` không còn trong `_PNG_ALLOWED` (`:681`), `ICCP` không còn trong `_WEBP_ALLOWED` (`:753`). `git grep` không còn `_icc_ok`, `_jpeg_icc_ok`, `_check_png_icc`, `_ICC_MIN_LENGTH`, `zlib` trong `seo_app/ai/`. Thử hồ sơ sRGB thật (LittleCMS) trong JPEG, PNG, WebP: "còn thông tin kèm theo" (bản `main`: qua). Hồ sơ màu đặt ở chỗ khác cũng bị từ chối: chú thích, APP15, APP2 tên viết thường, APP2 giữa hai lượt quét, sau EOI, chunk riêng, `ICCP` viết hoa trong PNG, `iCCP` sau IDAT, `cICP`, `iccp` viết thường và `ICCP` sau chunk ảnh trong WebP (test mục 2) |
| YC2 · khối theo SL-T050-6 | **ĐẠT** | APP0/APP14 lặp → metadata; SOF, SOS, DRI, DNL sai độ dài → hỏng; DAC, SOF3 → metadata; PLTE của ảnh RGB hay ảnh xám có alpha → metadata; tRNS sai độ dài → hỏng; cHRM, sBIT, bKGD → metadata. Đối chiếu mã nguồn Pillow 13.0.0 (`PngImagePlugin._save`, dòng 1451–1540): cHRM, sBIT, bKGD, gAMA, sRGB chỉ được ghi khi truyền `pnginfo`, pHYs chỉ khi truyền `dpi`; PLTE luôn có tối đa 2^(độ sâu bit) màu, tRNS không dài hơn số màu. Luật mới không chặn ảnh nào Pillow tự ghi |
| YC3 · chú thích đúng khả năng thật | **ĐẠT** (một ghi nhận nhỏ) | `base.py:551–560` và `:670–679` nói rõ "Không chống được ảnh dựng cố ý … lớp này chỉ là lưới cuối", bảo đảm thật là T-049 dựng lại từ điểm ảnh. Câu "Pillow chỉ ghi các chunk này khi được yêu cầu (`dpi`, `pnginfo`)" đúng với mã Pillow 13. Hai cụm từ trong câu chung chưa chính xác tuyệt đối, xem Ghi nhận 1 |
| YC4 · gỡ 15 `xfail` | **ĐẠT** | `git diff 9b41e6a^..team/T-066 -- tests/test_soi_loi_t050.py`: chỉ bỏ 2 hằng `SL5`, `SL6` và 2 dòng `@SL5`, `@SL6`; dữ liệu thử và `assert not accepted(...)` của 15 ca giữ nguyên. Từng ca bị chặn đúng khối: 6 ca SL-T050-5 → "còn thông tin kèm theo" (khối hồ sơ màu); SL-T050-6: APP0 lặp, APP14 lặp, PLTE ảnh RGB, cHRM → metadata; SOF, DRI, DNL, SOS dài, tRNS dài → hỏng. Các ca hồ sơ màu đổi theo thiết kế mới vẫn kiểm đúng ý: kèm hồ sơ màu thì bị từ chối (đúng câu `IMAGE_METADATA_MESSAGE`), cùng ảnh không kèm thì qua. Không còn `xfail` nào trong `test_soi_loi_t050.py` |

## Không chặn oan ảnh thật

Mỗi ảnh gốc đi qua `make_ai_image` và `make_preview` (T-049), rồi `prepare_images`. Sau đó tìm trong bản ra các chuỗi `ICC_PROFILE`, `Exif`, `xmpmeta`, tên khách, `GPS`.

| Nhóm | Nguồn | Kết quả |
|---|---|---|
| Cố định (33) | JPEG điện thoại có hồ sơ màu + EXIF/GPS + XMP + chú thích, xoay 6; JPEG progressive 4:4:4 có dpi, xoay 8; JPEG restart marker + optimize; JPEG CMYK, xám, `keep_rgb`; PNG RGBA có `iCCP` + `tEXt` + `iTXt` + `eXIf`; PNG có gAMA/cHRM/bKGD/sBIT/tIME/pHYs; PNG xám 16 bit, bảng màu trong suốt, bảng màu 4 bit, 1 bit, LA, RGB có tRNS; WebP nén có mất dữ liệu kèm hồ sơ màu + EXIF + XMP, WebP RGBA nén không mất và có mất dữ liệu, WebP xám; HEIC có hồ sơ màu + EXIF + XMP, HEIC RGBA, HEIC xám; 16×16, 3000×40, 6000×4000; JPEG xoay đủ 8 hướng | 66/66 bản qua |
| Ngẫu nhiên (400) | Định dạng JPEG/PNG/WebP/HEIC, 11 chế độ màu (RGB, RGBA, L, LA, P, 1, CMYK, I;16, I, YCbCr, PA), cỡ 1–1800 điểm ảnh, ngẫu nhiên kèm hồ sơ màu, EXIF/GPS, XMP, chú thích, chunk chữ, dpi, progressive, optimize, subsampling, restart, độ trong suốt, `bits` (117 tổ hợp Pillow không lưu được, bỏ qua và sinh ảnh khác) | 800/800 bản qua |
| Nguồn lạ (13) | MPO 3 khung có EXIF lớn, PNG động 3 khung, WebP động 3 khung, PNG RGB 16 bit có `iCCP` + `tEXt`, JPEG có MakerNote 30 KB xoay 6, JPEG CMYK progressive có hồ sơ màu, WebP xám có alpha, PNG từ bảng màu có alpha, HEIC 4032×3024, JPEG 4:2:0 chất lượng 100, ảnh 1×1 ba định dạng | 26/26 bản qua |

**Tổng: 892/892 bản qua, 0 bị chặn oan, 0 ảnh gốc bị app từ chối.** Các chuỗi dài (`ICC_PROFILE`, `Exif`, `xmpmeta`, tên khách, `SAMSUNG`) không xuất hiện trong bản nào. Có đúng một lần gặp 3 byte `GPS`, ở bản gửi AI của một ảnh HEIC xám ngẫu nhiên (234.374 byte). Chạy lại đúng thứ tự cũ (nhiễu của Pillow lặp lại giống hệt) thì xác định được vị trí: byte 35.503, nằm **trong dữ liệu ảnh nén** (đoạn 623–234.372). File chỉ có các khối SOI, JFIF, 2 DQT, SOF0, 4 DHT, SOS, EOI. Đây là trùng ngẫu nhiên (xác suất cỡ 1/16 triệu mỗi vị trí), không phải metadata: `GPS` chỉ có đúng một lần trong file, `Le Loi` và các chuỗi dấu khác không có (`t066_real_images_where.py`).

## Tìm lỗi mới

### Tệp dựng cố ý (63 ca, so với bản `main` `a9338f7`)

- 10 ca bản mới chặt hơn bản cũ (hồ sơ màu JPEG/PNG/WebP, `iCCP` sau IDAT, APP14 lặp, JFIF lặp sau lượt quét, DAC, SOF3, SOS dài hơn số thành phần, PLTE ảnh xám có alpha). **0 ca bản mới nhận mà bản cũ chặn.**
- Vẫn bị chặn như cũ: JFXX, TEM, EXP, JPGn, APP15, chú thích, sau EOI, `Exif\0\0` nằm trong DQT (bộ dò chuỗi), chunk tên có số, chunk trước IHDR, IHDR lặp, sau IEND, WebP chỉ có VP8X, ALPH trong dạng đơn giản.
- Còn qua, đúng giới hạn đã chấp nhận ở LC-T050-2 (Thợ Máy ghi ở mục Rủi ro 3, chú thích `base.py:554–555` cũng nói): hồ sơ màu, EXIF thô hay XMP không dấu nhét trong DQT, DHT, dữ liệu nén; PLTE và tRNS của ảnh bảng màu; dữ liệu sau dòng nén IDAT, IDAT riêng, CRC của IDAT rỗng, CRC sai; ALPH, đuôi VP8L, byte của VP8X; trường cố định (sRGB = 200, đơn vị pHYs = 7, giá trị tRNS ngoài phạm vi độ sâu bit); JPEG không có SOF; DRI, DNL lặp; SOS khai 4 thành phần trong ảnh 1 thành phần (đúng 12 byte theo số của chính nó) (xem Ghi nhận 1).

### Trọng tài Pillow (2 triệu tệp đột biến)

Kho 63 ảnh Pillow sạch (JPEG RGB/L/CMYK thường, progressive, restart + optimize; PNG 8 kiểu; WebP 4 kiểu; 3 cỡ). Mỗi tệp đột biến 1–3 lần: chèn khối metadata (APP1 EXIF, APP2 hồ sơ màu, XMP, chú thích, APP13; `iCCP`, `eXIf`, `tEXt`, `zTXt`, `iTXt`; `ICCP`, `EXIF`, `XMP `) ở chỗ bất kỳ hay đúng ranh giới khối, lặp, xóa, đổi chỗ khối, sửa trường độ dài, lật byte, cắt cụt, chèn dữ liệu metadata trần. Tệp nào `prepare_images` nhận thì mở bằng Pillow (gồm `load()`, để đọc cả chunk sau IDAT, và libwebp demux) xem có khóa `info` lạ hay EXIF không.

```
1000000 ảnh đột biến: nhận 142329, từ chối 857671, ngoại lệ lạ 0, nhận mà Pillow đọc ra metadata 0, mới nhận mà cũ chặn 0 (137 s)
1000000 ảnh đột biến: nhận 142809, từ chối 857191, ngoại lệ lạ 0, nhận mà Pillow đọc ra metadata 0, mới nhận mà cũ chặn 0 (188 s)
```

Lớp kiểm đọc chặt hơn Pillow ở mọi chỗ tôi xem: đòi `FF` ở đầu mỗi khối (Pillow bỏ qua byte rác), đi hết mọi lượt quét tới EOI (Pillow dừng ở SOS đầu), không nhận dữ liệu sau EOI, IEND hay khối RIFF.

### Tốc độ (ảnh 5 MB, lấy lần nhanh nhất trong 3 lần, máy đang chạy song song agent khác)

Số trong bảng là lần đo lúc 09:10 (`t066_speed_out.txt`).

| Ca | `main` (s) | nhánh (s) |
|---|---|---|
| JPEG thật 1800×1500 chất lượng 100, 4,3 MB | 0,029 | 0,030 |
| JPEG thật 2400×1800 chất lượng 95, 4,5 MB | 0,017 | 0,015 |
| Dựng cố ý: dữ liệu nén toàn `FF FF` | 2,765 | 3,293 |
| Dựng cố ý: toàn `FF 00` / toàn mã RST | 0,979 / 1,526 | 1,082 / 1,668 |
| Dựng cố ý: 1,3 triệu khối DHT rỗng / DQT rỗng | 1,957 / 1,928 | 2,325 / 2,658 |
| Dựng cố ý: 870 nghìn khối DRI / 480 nghìn lượt quét | 1,238 / 1,065 | 1,610 / 1,628 |
| Dựng cố ý: PNG 437 nghìn IDAT rỗng | 0,644 | 0,683 |

Không chậm bất thường. Thời gian tăng tuyến tính theo dung lượng; ảnh thật chỉ mất vài chục mili giây như bản cũ. Với tệp dựng toàn khối nhỏ, bản mới chậm hơn khoảng 1,2–1,5 lần vì kiểm thêm độ dài từng khối. Ca chậm nhất ở cả hai bản là dữ liệu nén toàn `FF FF`: khoảng 3,3 giây mỗi ảnh 5 MB. Đo hai lần, bản mới 3,47 và 3,29 giây, bản cũ 4,15 và 2,77 giây: chênh nhau trong mức dao động của máy đang bận. Một lần gửi tối đa (2 ảnh × 5 MB DHT rỗng) đo được 4,9 giây. Với 2 ảnh `FF FF`, ước tính khoảng 6,6 giây.

## Lỗi tìm thấy

Không có.

## Ghi nhận (không phải lỗi, không viết test `xfail`)

1. **Câu chung của chú thích `base.py:553–554` hơi rộng.** Câu nói "khối được nhận phải đúng độ dài theo khuôn, khối chỉ cần một lần thì không được lặp". Thực tế lệch ở mấy chỗ sau. DQT, DHT không được kiểm độ dài; chú thích phần JPEG ở `:566` đã nói đúng điều này. DRI và DNL lặp được không giới hạn, mỗi khối chở 2 byte tùy ý: 294 khối DRI chở trọn một hồ sơ sRGB 588 byte vẫn qua. DNL được nhận cả trước lượt quét đầu, dù theo chuẩn chỉ có một khối và chỉ sau lượt quét đầu. Đầu lượt quét SOS chỉ được so với số thành phần do chính nó khai, không so với khung ảnh: SOS khai 4 thành phần trong ảnh 1 thành phần (đúng 12 byte) vẫn qua, dư 6 byte tùy ý mỗi lượt quét, mà lượt quét thì lặp được. Các kênh này cùng loại với "DQT, DHT được phép lặp" đã chấp nhận ở LC-T050-2: không mở thêm khả năng gì. Chú thích cũng đã nói rõ lớp kiểm không chống được ảnh dựng cố ý, nên không gây hiểu sai như LC-T050-3. Nếu muốn sửa khi tiện: viết lại thành "…đúng độ dài theo khuôn (trừ bảng DQT, DHT); khung ảnh, APP0, APP14 và các chunk PNG không được lặp", hoặc chặn rẻ: DNL tối đa một lần, chỉ sau lượt quét đầu; số thành phần của SOS không quá số của khung ảnh.
2. Các chỗ Thợ Máy đề xuất siết thêm (byte dành riêng của VP8X, giá trị sRGB 0–3, đơn vị pHYs 0/1, giá trị tRNS trong phạm vi độ sâu bit, bắt buộc có SOF trước SOS) vẫn nhận như Thợ Máy mô tả. Mỗi chỗ chỉ vài bit tới vài byte, cùng loại với mục 1. Không bắt buộc.

## Bằng chứng

Máy Windows 11 Pro (10.0.26300) của chủ dự án, Python 3.12, Pillow 13.0.0, pillow-heif 1.8.1, worktree `wt-T-066`, nhánh `team/T-066`, đầu nhánh lúc kiểm `66f58dd` (gốc `main` `a9338f7`). Máy đang chạy song song 2 agent khác và một lượt pytest toàn bộ.

```
$ uv run pytest tests/test_ai_images.py tests/test_soi_loi_t050.py tests/test_soi_loi_t049.py \
    tests/test_images_process.py tests/test_app_pages.py -q -p no:cacheprovider -rfEsxX
(08:23–08:27, trước khi có file của tôi)
893 passed in 217.29s (0:03:37)

$ uv run pytest tests/test_ai_images.py tests/test_soi_loi_t050.py tests/test_soi_loi_t049.py \
    tests/test_soi_loi_t066.py tests/test_images_process.py tests/test_app_pages.py tests/test_ai.py \
    tests/test_ai_openai_gemini.py tests/test_ai_openai_gemini_soi_loi.py tests/test_ai_t026.py \
    tests/test_ai_t028.py tests/test_ai_t034.py tests/test_soi_loi_t052.py tests/test_soi_loi_t062.py \
    tests/test_soi_loi_t065.py tests/test_t062_alt_prompt.py -q -p no:cacheprovider -rfEsxX
(09:04–09:07)
SKIPPED [1] tests\test_soi_loi_t052.py:538: máy không cho tạo symlink (Windows chưa bật Developer Mode)
1903 passed, 1 skipped in 153.60s (0:02:33)

$ uv run pytest tests/test_soi_loi_t066.py -q -p no:cacheprovider
(09:23, bản cuối của file)
27 passed in 23.85s

$ uv run ruff check .
All checks passed!
```

- 0 hỏng, 0 `xfail`. Bỏ qua 1: test symlink của T-052 (Windows chưa bật Developer Mode), có từ trước, Thợ Máy cũng gặp. Sau lượt 2, tôi chỉ sửa cách viết trong file mới (tách một dòng quá dài, viết lại docstring), không đổi ý; file mới được chạy lại riêng trên bản cuối.
- Các file test trên gồm: mọi file có `prepare_images` (`grep -l "prepare_images" tests/`: `test_ai_images.py`, `test_soi_loi_t049.py`, `test_soi_loi_t050.py`, và file mới của tôi), các file test lớp AI (`test_ai*.py`), các file gửi ảnh qua `suggest_alt` (`test_soi_loi_t052.py`, `test_soi_loi_t062.py`, `test_soi_loi_t065.py`, `test_t062_alt_prompt.py`), xử lý ảnh T-049 (`test_images_process.py`) và các trang app (`test_app_pages.py`).
- **Test mới trên code cũ:** chép `seo_app`, `tests`, `config`, `app` vào thư mục nháp, thay `base.py` bằng `git show a9338f7:seo_app/ai/base.py`, chạy với `PYTHONPATH` trỏ vào đó (in `__file__` xác nhận nạp đúng bản cũ, có `_icc_ok`). Kết quả **4 hỏng, 23 qua**. Bốn ca hỏng đúng là chỗ T-066 sửa: APP2 hồ sơ màu giữa hai lượt quét, `iCCP` sau IDAT, `ICCP` sau chunk ảnh WebP, và trọng tài Pillow (bản cũ nhận hồ sơ màu nên Pillow đọc ra `icc_profile`). 23 ca còn lại (ảnh thật qua, hồ sơ màu ở khối lạ bị chặn) qua trên cả hai bản.
- **Quét chuỗi giống bí mật:** `PYTHONUTF8=1 uvx detect-secrets scan --all-files` trong thư mục riêng chứa file test của tôi và một file mồi có chữ tiếng Việt (khóa AWS giả, `password = …`). File mồi bắt đủ 2/2 (`AWS Access Key`, `Secret Keyword`); file của tôi 0 mục. Đã xóa thư mục mồi.
- `ruff format --check tests/test_soi_loi_t066.py`: "already formatted".
- Script thử và kết quả: thư mục ghi chú chung của nhóm phiên, `T-066-soi-loi-scripts/`: `t066_real_images.py` (ảnh thật cố định + ngẫu nhiên), `t066_real_images_where.py` (vị trí 3 byte `GPS`), `t066_exotic.py` (nguồn lạ), `t066_crafted.py` (63 tệp dựng cố ý, so `main`; phần đo tốc độ ở cuối là bản nháp đầu, số trong báo cáo lấy từ `t066_speed.py`), `t066_speed.py` (tốc độ), `t066_oracle_fuzz.py` và `t066_oracle_fuzz_vs_old.py` (trọng tài Pillow, có so `main`), `reasons.py` (lý do chặn 15 ca cũ), kèm các file `*_out.txt`. Chạy trong worktree bằng `PYTHONUTF8=1 PYTHONPATH=. uv run python <script> [<old_base.py>]`, bản cũ lấy bằng `git show a9338f7:seo_app/ai/base.py`.

## Đối chiếu việc được giao

- [x] 1. YC1–4 đạt (bảng "Kiểm từng yêu cầu"); 15 ca cũ bị chặn đúng khối; các ca hồ sơ màu đổi theo thiết kế mới vẫn khẳng định "ảnh có hồ sơ màu bị từ chối"
- [x] 2. Không chặn oan: 446 ảnh gốc (JPEG điện thoại có hồ sơ màu/EXIF, PNG có `iCCP`, WebP, HEIC, ảnh xoay, xám, có alpha, nhiều khung; 400 ảnh ngẫu nhiên) → 892/892 bản qua
- [x] 3. Tìm lỗi mới: 63 tệp dựng cố ý, 2 triệu tệp đột biến có trọng tài Pillow, đo tốc độ 12 kiểu ảnh 5 MB: không có lỗi
- [x] 4. Không có lỗi mới nên không có test `xfail`; `tests/test_soi_loi_t066.py` gồm 27 ca qua, giữ các đối chứng trên
- [x] Test liên quan qua, `uv run ruff check .` sạch

## Rủi ro và điểm cần chú ý

- Số đo thời gian lấy trên máy đang chạy song song agent khác và một lượt pytest toàn bộ, nên con số tuyệt đối chậm hơn máy rảnh và dao động giữa các lần đo (ca `FF FF` ở trên). Bản cũ và bản mới chạy kế nhau ở từng ca, lấy lần nhanh nhất trong 3 lần, nên phép so chỉ đáng tin ở mức "cùng cỡ" hay "chậm hơn 1,2–1,5 lần".
- Trọng tài là Pillow. Máy chủ hãng AI có thể dùng bộ đọc khác, nhưng lớp kiểm đọc chặt hơn bộ đọc thông thường ở mọi chỗ tôi thấy (xem mục Trọng tài Pillow). Đây là suy luận, không thử được bộ đọc của hãng.
- `test_real_ai_copy_from_more_sources_passes` dựa vào việc Pillow 13 ghi được hồ sơ màu vào MPO, PNG động, WebP động. Nếu sau này nâng Pillow mà Pillow thôi ghi, test hỏng ở bước tiền đề (kiểm ảnh gốc có hồ sơ màu), không phải lỗi bảo mật: sửa test cho khớp.
- Chưa chạy trên Mac/Linux. Lớp kiểm chỉ đọc byte bằng Python thuần, không phụ thuộc hệ điều hành; test mới không dùng đường dẫn.

## Đề xuất

- **Lá Chắn (rút gọn):** soát `base.py:544–790`; xem Ghi nhận 1 (câu chung của chú thích, DRI/DNL lặp) để quyết có cần sửa chữ hay không.
- **T-056:** như Thợ Máy đề xuất, chỉ gọi `suggest_alt` với byte của `make_ai_image`. Ảnh gốc của điện thoại (có hồ sơ màu) và ảnh đăng web (WebP giữ GPS, hồ sơ màu) giờ đều bị chặn ở lớp này.

## Câu hỏi cho chủ dự án

Không có.

## Kết luận

**ĐẠT**, chuyển Lá Chắn rút gọn được. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp. Cả 4 yêu cầu đạt. 892 bản gửi AI thật qua, không bản nào bị chặn oan. 2 triệu tệp đột biến và 63 tệp dựng cố ý không làm lớp kiểm lỏng hơn bản cũ ở chỗ nào, và không tệp nào lọt kèm metadata mà Pillow đọc được. Ghi nhận 1 (câu chung của chú thích hơi rộng, DRI/DNL lặp được) cùng loại giới hạn đã chấp nhận ở LC-T050-2.

# Báo cáo T-066 · Dọn lỗi Thấp lớp ảnh gửi AI · Thợ Máy

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-066](../tickets/T-066-don-loi-thap-anh-gui-ai.md) |
| Ngày nộp | 2026-10-23 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Bộ kiểm cuối cùng trước khi ảnh rời máy tới hãng AI giờ **từ chối mọi "hồ sơ màu"** gắn trong ảnh (phần dữ liệu màu có thể chở tên, đời màn hình hay chữ tùy ý), và chặt hơn với các khối kỹ thuật bị lặp lại hoặc dài hơn bình thường (chỗ có thể nhét chữ, tọa độ). Bộ kiểm cũng không còn phải giải nén gì.
- Ảnh do chính phần mềm chuẩn bị để gửi AI (bản thu nhỏ của T-049) **vẫn qua**: đã thử với ảnh gốc JPEG, PNG, WebP và HEIC của iPhone có đủ GPS, ghi chú, XMP và hồ sơ màu chở chữ. 476 kiểu ảnh sạch do thư viện ảnh tạo: không ảnh nào bị chặn nhầm.
- Người dùng không thấy gì khác. Chỉ khi có ai cố tình dựng ảnh lạ thì app báo "ảnh còn thông tin kèm theo… (EXIF, XMP, chú thích, hồ sơ màu…)" và không gửi.
- Chú thích trong code giờ nói đúng giới hạn: bộ kiểm chỉ là lưới cuối; bảo vệ thật là bước dựng lại ảnh từ điểm ảnh (T-049).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/ai/base.py` | Từ chối mọi hồ sơ màu (JPEG APP2, PNG `iCCP`, WebP `ICCP`); bỏ `_icc_ok`, `_jpeg_icc_ok`, `_check_png_icc`, lần giải nén zlib và `import zlib`; siết khối JPEG/PNG theo SL-T050-6 (APP0/APP14 một lần, SOF/SOS/DRI/DNL đúng độ dài, bỏ DAC, chỉ SOF0/1/2; PNG kiểm IHDR, `PLTE`/`tRNS` theo loại màu, bỏ `cHRM`/`sBIT`/`bKGD`, chunk phụ phải trước IDAT); viết lại chú thích (LC-T050-3); câu báo metadata thêm "hồ sơ màu" |
| `tests/test_ai_images.py` | Đổi các ca hồ sơ màu sang "bị từ chối"; thêm ca đúng/sai khuôn cho từng luật mới; thêm test bản gửi AI thật (`make_ai_image`, `make_preview`) từ 8 loại ảnh gốc phải qua |
| `tests/test_soi_loi_t050.py` | Gỡ 15 dấu `xfail(strict=True)` (SL-T050-5: 6 ca, SL-T050-6: 9 ca); đổi các ca hồ sơ màu theo thiết kế mới (phiếu cho phép) |
| `docs/team/reports/T-066-tho-may.md` | Báo cáo này |

Không sửa `seo_app/images/**`, `app/**`, `config/**`; không thêm thư viện (`git diff --stat a9338f7..HEAD` chỉ có 4 file trên).

Commit trên `team/T-066` (tách từ `main` `a9338f7`): `9b41e6a` (phần lớn code và test, việc dở hôm 22/10, Chỉ Huy B commit giùm khi chủ dự án bảo dừng), `48dad2a` (sửa chú thích pHYs, ca HEIC của test Soi Lỗi), và commit báo cáo này.

## Cách sửa từng yêu cầu

**YC1 · Từ chối mọi hồ sơ màu** (`seo_app/ai/base.py:551–560`)

- JPEG: chỉ còn APP0 `JFIF` và APP14 `Adobe` trong danh sách APPn (`_JPEG_APP`, `base.py:580`); mọi APP2 (`ICC_PROFILE`, FlashPix…) rơi vào nhánh "ngoài danh sách cho phép" → `metadata` (`base.py:636–637`).
- PNG: `iCCP` không còn trong `_PNG_ALLOWED` (`base.py:681`) → `metadata` ngay khi gặp, **không giải nén**. Bom giải nén `iCCP` 64 MB bị từ chối ngay (`test_png_iccp_decompression_bomb_is_rejected`); `test_png_iccp_is_rejected_without_decompressing` thay `zlib.decompress`/`decompressobj` bằng hàm báo lỗi để chắc không còn lần giải nén nào, và kiểm `base.py` không còn `import zlib`.
- WebP: `ICCP` không còn trong `_WEBP_ALLOWED` (`base.py:753`).
- Đã xóa: `_ICC_MIN_LENGTH`, `_icc_ok`, `_JPEG_ICC`, `_jpeg_icc_ok`, `_PNG_ICC_HEADER`, `_check_png_icc`, `import zlib`.
- Câu báo `IMAGE_METADATA_MESSAGE` (`base.py:464`) thêm "hồ sơ màu" để ai gặp lỗi biết vì sao. Không file nào khác so nguyên văn câu này (đã tìm trong `app/`, `seo_app/`, `tests/`).

**YC2 · Siết khối theo SL-T050-6**

| Luật | Ở đâu | Test |
|---|---|---|
| APP0 `JFIF`, APP14 `Adobe` tối đa một lần | `seen_app`, `base.py:614`, `:632–635` | `jfif-lap`, `adobe-lap`; SL6 `jpeg-app0-lap`, `jpeg-app14-lap` |
| Khung ảnh chỉ SOF0/1/2, đúng 6 + 3·N byte, N = 1–4 | `_JPEG_FRAME` `:567`, `_jpeg_decode_ok` `:592–602` | `sof0`, `sof1`, `sof2-3-thanh-phan` (qua); `sof-ngan`, `sof-dai`, `sof-thieu-thanh-phan`, `sof-0-thanh-phan`, `sof-5-thanh-phan`, `sof-cut` (hỏng); `sof3`, `sof5`, `sof9`, `sof15` (metadata); SL6 `jpeg-sof-dai` |
| SOS đúng 4 + 2·N byte; DRI, DNL đúng 2 byte | `_jpeg_decode_ok` | `sos-*`, `dri-*`, `dnl-ngan`; SL6 `jpeg-sos-dai`, `jpeg-dri-dai`, `jpeg-dnl-dai` |
| Bỏ DAC (bảng mã số học) | `_JPEG_DECODE` `:570` | `dac` |
| PNG IHDR: độ sâu bit hợp loại màu, nén/lọc 0, xen dòng 0/1 | `_png_ihdr_ok` `:688–695` | `ihdr-rgb-4-bit`, `ihdr-loai-mau-5`, `ihdr-nen-1`, `ihdr-xen-dong-2` |
| `PLTE` chỉ với ảnh bảng màu (loại 3), 3 byte mỗi màu, ≤ 2^độ sâu màu | `:725–730` | `plte-anh-rgb`, `plte-anh-xam` (metadata); `plte-le`, `plte-rong`, `plte-qua-so-mau`, `plte-lap`, `bang-mau-thieu-plte` (hỏng); SL6 `png-plte-anh-rgb` |
| `tRNS` đúng độ dài theo loại màu: xám 2, RGB 6, bảng màu 1–số màu (sau PLTE); ảnh có alpha không có `tRNS` | `:731–736` | `trns-*`; SL6 `png-trns-dai` |
| Bỏ `cHRM`, `sBIT`, `bKGD` (bản gửi AI của T-049 là JPEG, không cần; Pillow chỉ ghi khi được truyền `pnginfo`) | `_PNG_ALLOWED` `:681` | `chrm`, `sbit`, `bkgd`; SL6 `png-chrm-chu` |
| `gAMA` 4, `sRGB` 1, `pHYs` 9 byte **đúng** (trước đây: tối đa) | `_PNG_FIXED_LENGTH` `:680` | `gama-dai`, `phys-ngan` |
| Chunk phụ phải đứng trước IDAT, các IDAT liền nhau (đúng chuẩn PNG: `PLTE`, `tRNS`, `gAMA`, `sRGB`, `pHYs` đều phải trước IDAT) | `:716–717` | `gama-sau-idat`, `png-nhieu-idat` (qua) |

Không kiểm độ dài DQT/DHT: giá trị bảng vốn là dữ liệu tùy ý và được phép lặp, nên kiểm khuôn không đóng được gì (theo LC-T050-2).

**YC3 · Chú thích đúng khả năng thật** (mẫu LC-T050-3)

- `base.py:551–560` (thay `:552–556` cũ): "chặn metadata do phần mềm thật ghi … và mọi loại khối chưa biết; khối được nhận phải đúng độ dài theo khuôn… **Không** chống được ảnh dựng cố ý: dữ liệu vẫn giấu được trong phần ảnh nén, bảng giải mã (DQT, DHT được phép lặp) và các trường cố định (mật độ điểm ảnh, cờ…). Bảo đảm thật là bản gửi AI được dựng lại từ điểm ảnh, không kèm hồ sơ màu (T-049); lớp này chỉ là lưới cuối."
- `base.py:670–679` (thay `:683–689` cũ): bỏ vế "không chứa chữ tự do"; ghi "Pillow chỉ ghi các chunk này khi được yêu cầu (`dpi`, `pnginfo`); giữ để không từ chối nhầm". Câu cũ "pHYs: Pillow tự ghi khi ảnh nguồn có dpi" sai (thử: mở PNG có dpi rồi lưu lại không truyền `dpi` → không có `pHYs`), đã sửa.
- Docstring `prepare_images` (`base.py:494–499`): "chỉ đọc cấu trúc khối, không giải nén gì".

**YC4 · Gỡ 15 `xfail`, đổi ca hồ sơ màu, ảnh sạch của T-049 vẫn qua**

- `tests/test_soi_loi_t050.py`: bỏ `SL5`, `SL6`; `test_icc_profile_with_data_outside_tag_table_is_rejected` (6 ca) và `test_allowed_blocks_repeated_or_longer_than_shape_are_rejected` (9 ca) nay **qua thật** (trước khi gỡ dấu: 15/15 báo XPASS). Không đổi dữ liệu thử hay điều kiện kiểm của 15 ca này.
- Ca hồ sơ màu đổi theo thiết kế mới (Chỉ Huy B duyệt ở phiếu, LC-T050-1 mục "Khuyến nghị" điểm 2):

| File | Test cũ → mới | Đổi gì |
|---|---|---|
| `test_soi_loi_t050.py` | `test_clean_pillow_images_with_icc_pass` → `test_clean_pillow_images_pass_and_icc_is_rejected` | Kèm hồ sơ sRGB: bị từ chối (metadata); cùng ảnh không kèm: qua |
| `test_soi_loi_t050.py` | `test_icc_builders_without_tail_pass` → `test_icc_builders_without_tail_are_rejected_too` | Hồ sơ không đuôi cũng bị từ chối |
| `test_soi_loi_t050.py` | `test_more_clean_pillow_images_pass` (3 ca có `icc_profile`) | Kèm hồ sơ: bị từ chối; cùng ảnh, cùng cách lưu không kèm: qua |
| `test_soi_loi_t050.py` | `test_heic_photo_read_with_pillow_heif_makes_clean_ai_copy` | Bản sạch dựng lại từ điểm ảnh như T-049 (lưu thẳng ảnh đọc từ HEIC thành PNG thì Pillow tự chép hồ sơ màu, đúng đường P10 của Lá Chắn); lỡ chép hồ sơ màu hay EXIF: bị từ chối |
| `test_soi_loi_t050.py` | `test_png_iccp_decompression_bomb_is_rejected` | Câu báo: "hỏng" → "còn thông tin kèm theo" (từ chối ngay, không giải nén) |
| `test_ai_images.py` | `test_prepare_accepts_clean_images`, `test_allowed_blocks_in_right_shape_pass`, `test_pillow_images_of_every_kind_pass` | Bỏ ca có hồ sơ màu; chuyển sang `test_icc_profiles_are_always_rejected` (8 ca), `test_pillow_images_with_icc_profile_are_rejected` (8 ca) |
| `test_ai_images.py` | `test_extra_frames_duplicates_and_animation_are_broken` | `iccp-hong`, `iccp-cut` chuyển sang ca hồ sơ màu; `webp-don-gian-them-chunk`, `webp-khong-anh` dùng `ALPH` thay `ICCP` để vẫn kiểm đúng đường "hỏng" |

- Ảnh sạch thật của T-049: `test_real_ai_copy_from_make_ai_image_passes` (`tests/test_ai_images.py`), 8 loại ảnh gốc 600×400 có nhiễu: JPEG (EXIF + GPS + hồ sơ màu chở chữ + chú thích + XMP), JPEG CMYK progressive, PNG RGBA (`iCCP` chở chữ + `tEXt` + `iTXt` XMP + `eXIf`), PNG bảng màu trong suốt, PNG xám 16 bit, WebP (EXIF + XMP + `ICCP`), WebP RGBA lossless, HEIC (EXIF + GPS + XMP + hồ sơ màu). Mỗi loại: ảnh gốc mang đúng hồ sơ màu chở chữ; gửi thẳng thì bị từ chối (trừ HEIC: MIME không được nhận); `make_ai_image` và `make_preview` ra JPEG **qua** `prepare_images`, không còn `ICC_PROFILE`, `Exif\0\0`, `<x:xmpmeta`, chữ GPS, tên khách. Test cũ của T-049 cũng vẫn qua (`tests/test_soi_loi_t049.py::test_ban_ai_moi_loai_nguon_qua_prepare_images`, 11 loại nguồn, và `tests/test_images_process.py`).

## Bằng chứng

Máy Windows 11 của chủ dự án, worktree `wt-T-066`, Pillow 13.0.0, ngày 2026-10-23 (chạy từ 07:41 tới 07:44, trên đúng code của commit `48dad2a`).

```
$ uv run pytest tests/test_ai_images.py tests/test_soi_loi_t050.py tests/test_soi_loi_t049.py \
    tests/test_images_process.py tests/test_soi_loi_t052.py tests/test_soi_loi_t062.py \
    tests/test_soi_loi_t065.py tests/test_t062_alt_prompt.py tests/test_ai.py tests/test_app_pages.py \
    -q -p no:cacheprovider -rfEsxX
SKIPPED [1] tests\test_soi_loi_t052.py:538: máy không cho tạo symlink (Windows chưa bật Developer Mode)
1266 passed, 1 skipped in 177.16s (0:02:57)
(0 hỏng, 0 xfail. Bỏ qua 1: test symlink của T-052, có từ trước, không liên quan.
 tests/test_ai_providers.py không có trong repo nên không chạy.)

$ uv run pytest tests/test_ai_images.py tests/test_soi_loi_t050.py --collect-only -q
578 tests collected        (trên main a9338f7: 505 test, trong đó 15 xfail; nay 578, không còn xfail)

$ uv run ruff check .
All checks passed!
```

Các file test trên gồm: mọi file có `prepare_images` (`grep -l "prepare_images" tests/`: `test_ai_images.py`, `test_soi_loi_t049.py`, `test_soi_loi_t050.py`), các file gửi ảnh qua `suggest_alt` (`test_soi_loi_t052.py`, `test_soi_loi_t062.py`, `test_soi_loi_t065.py`, `test_t062_alt_prompt.py`), xử lý ảnh T-049 (`test_images_process.py`), lớp AI chung (`test_ai.py`) và các trang app (`test_app_pages.py`).

`detect-secrets scan` (chạy với `PYTHONUTF8=1`) trên 3 file code/test của phiếu và báo cáo này: 4 mục, đúng 4 mục có sẵn trên `main` (dòng ví dụ `https://admin:matkhau@site…` trong chú thích `base.py:28`, 3 khóa giả `…KhoaGia…` của T-050 ở `tests/test_ai_images.py:70–72`); 0 mục mới.

`ruff format --check tests/test_soi_loi_t050.py` báo "would reformat" ở các dòng của Soi Lỗi; trên `main` file này cũng vậy (dự án chỉ dùng `ruff check`), nên không định dạng lại file của Soi Lỗi. `base.py` và `test_ai_images.py`: "already formatted".

**Chỉ chặt hơn, không lỏng hơn** (script tạm trong scratchpad, không commit; so `prepare_images` của nhánh với bản của `main` `a9338f7` nạp từ `git show a9338f7:seo_app/ai/base.py`): 60.000 ảnh dựng từ 14 ảnh Pillow hợp lệ (JPEG, PNG, WebP; có và không hồ sơ màu), đột biến bằng cách chèn/lặp/bỏ/đổi chỗ khối từ một kho 52 khối (APP0 chở chữ, APP2 hồ sơ màu, SOF/SOS/DRI dài, DAC, SOF3, PLTE, tRNS, cHRM, iCCP, ICCP, EXIF, IHDR đủ loại màu…) và sửa ngẫu nhiên 1–6 byte. Lần chạy trên code cuối:

```
(cũ nhận, mới nhận): {(False, False): 27765, (True, True): 22692, (True, False): 9543}
bản mới nhận mà bản cũ từ chối: 0
```

Chạy 2 lần (ảnh gốc có nhiễu ngẫu nhiên nên số ca mỗi lần lệch chút): cả 2 lần đều **0** ca bản mới nhận mà bản cũ từ chối. Đọc code cũng thấy vậy: mỗi danh sách cho phép mới là tập con của danh sách cũ, mỗi giới hạn độ dài mới chặt hơn hoặc bằng giới hạn cũ, các bước từ chối cũ đều giữ nguyên.

**Không chặn nhầm ảnh sạch** (cùng script): ma trận 476 ảnh Pillow 13.0.0 không hồ sơ màu (JPEG: RGB, L, CMYK, YCbCr × 12 kiểu lưu gồm progressive, optimize, restart marker, `qtables`, subsampling, `keep_rgb`, dpi; PNG: RGB, RGBA, L, LA, P, 1, I;16, I × 9 kiểu gồm `bits` 1/2/4, `transparency`, `optimize`, dpi; WebP: RGB, RGBA, L, LA, P × 7 kiểu; 4 cỡ từ 1×1 tới 333×257): **0 bị từ chối** (28 tổ hợp Pillow không lưu được, bỏ qua).

**Test mới bắt được lỗi cũ** (chạy `tests/test_ai_images.py` mới trên code `base.py` của `main`, bản sao trong scratchpad): 63 ca hỏng, đúng là các ca của luật mới (APP0/APP14 lặp, DAC, SOF3/5/9/15, SOF/SOS/DRI/DNL sai độ dài, IHDR sai, PLTE/tRNS sai, cHRM/sBIT/bKGD, chunk sau IDAT, 8 ca hồ sơ màu, 8 ảnh Pillow có hồ sơ màu, Pillow tự chép `iCCP`, không giải nén, và đối chứng "ảnh gốc gửi thẳng bị chặn" của 2 loại ảnh chỉ có hồ sơ màu).

## Đối chiếu tiêu chí xong

- [x] YC1 từ chối mọi hồ sơ màu, bỏ `_icc_ok`, `_jpeg_icc_ok`, `_check_png_icc` và lần giải nén zlib (`test_icc_profiles_are_always_rejected`, `test_pillow_images_with_icc_profile_are_rejected`, `test_pillow_resaved_png_copies_icc_profile_and_is_rejected`, `test_png_iccp_is_rejected_without_decompressing`; 6 ca SL-T050-5)
- [x] YC2 APP0/APP14 một lần, khối giải mã đúng độ dài theo số thành phần, bỏ DAC, chỉ SOF0/1/2, `PLTE` chỉ loại màu 3, `tRNS` đúng độ dài, bỏ `cHRM`/`sBIT`/`bKGD` (bảng YC2; 9 ca SL-T050-6)
- [x] YC3 chú thích viết lại theo mẫu LC-T050-3 (`base.py:551–560`, `:670–679`)
- [x] YC4 gỡ 15 `xfail` (15 XPASS → qua); ảnh sạch của T-049 vẫn qua (`test_real_ai_copy_from_make_ai_image_passes` 8 loại, `test_soi_loi_t049.py`, `test_images_process.py`)
- [x] Lớp kiểm chỉ chặt hơn (so với `main`: 0/60.000 ca lỏng hơn, 2 lần chạy)
- [x] Test liên quan qua, `uv run ruff check .` sạch (mục Bằng chứng). Toàn bộ `uv run pytest` do Chỉ Huy chạy khi gộp
- [x] Báo cáo tại `docs/team/reports/T-066-tho-may.md`

## Rủi ro và điểm cần chú ý

1. **Bản gửi AI không còn hồ sơ màu** (đổi thiết kế T-046 mục 3, Chỉ Huy B duyệt): ảnh iPhone Display P3 tới AI hơi nhạt màu; đủ để viết alt (LC-T050-1). Bản đăng web (WebP 1600 px) vẫn giữ hồ sơ màu như cũ.
2. **Ai gọi `suggest_alt` bằng byte khác bản của `make_ai_image`** (ví dụ ảnh gốc từ điện thoại, có hồ sơ màu) sẽ bị từ chối với câu "còn thông tin kèm theo… hồ sơ màu". Đúng thiết kế; hiện chưa có chỗ nào trong `app/` gọi `suggest_alt` (giao diện là T-056).
3. **Vẫn giấu được dữ liệu trong ảnh dựng cố ý** (chấp nhận theo LC-T050-2, đã ghi trong chú thích): dữ liệu nén JPEG/IDAT/VP8L/ALPH, dữ liệu sau dòng zlib trong IDAT, CRC của chunk PNG, giá trị bảng DQT/DHT (được lặp), và các trường cố định: phiên bản, đơn vị, mật độ điểm ảnh của khối JFIF (7 byte), cờ của khối Adobe (7 byte), `pHYs` (9), `gAMA` (4), `sRGB` (1), giá trị `tRNS`, cờ và 3 byte dành riêng của `VP8X`, các byte trong SOF/SOS. Không đóng được nếu không giải mã ảnh; bảo vệ thật là T-049 dựng lại ảnh từ điểm ảnh.
4. **Phân loại câu báo** với ảnh dựng cố ý: khối lạ, DAC, SOF3/5–7/9–15, `PLTE` của ảnh không dùng bảng màu → "còn thông tin kèm theo"; khối được nhận nhưng sai độ dài, IHDR sai, chunk sau IDAT → "bị hỏng". Ảnh thật của phần mềm không gặp các câu này.
5. `test_pillow_resaved_png_copies_icc_profile_and_is_rejected` khẳng định Pillow 13.0.0 (bản trong `uv.lock`) tự chép hồ sơ màu khi lưu lại PNG. Nếu sau này nâng Pillow mà Pillow thôi chép, test đó báo hỏng ở bước tiền đề (không phải lỗi bảo mật): sửa test cho khớp.
6. Chưa chạy trên Mac/Linux (code chỉ là đọc byte bằng Python thuần, không phụ thuộc hệ điều hành; chủ dự án chưa có máy Mac).

## Đề xuất

- **T-056 (giao diện chọn ảnh):** chỉ gọi `suggest_alt` với `ImageInput(data=make_ai_image(ảnh).data, mime="image/jpeg")`; không đưa byte ảnh gốc hay ảnh đăng web (WebP giữ GPS, hồ sơ màu sẽ bị chặn).
- **Soi Lỗi, Lá Chắn (rút gọn):** soát `base.py:544–790`. Nếu muốn chặt thêm (rẻ, không bắt buộc): cờ và 3 byte dành riêng của `VP8X`, giá trị `sRGB` 0–3, đơn vị `pHYs` 0/1, giá trị `tRNS` trong phạm vi độ sâu bit, bắt buộc có SOF trước SOS. Mỗi chỗ chỉ vài bit đến vài byte, cùng loại với mục Rủi ro 3.
- Báo cáo Soi Lỗi T-050 nhắc tên test cũ `test_clean_pillow_images_with_icc_pass`, `test_icc_builders_without_tail_pass`: nay đổi tên như bảng YC4.

## Câu hỏi cho chủ dự án

Không có.

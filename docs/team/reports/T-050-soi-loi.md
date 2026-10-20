# Báo cáo T-050 · Lớp AI đọc ảnh và gợi ý alt · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-050](../tickets/T-050-lop-ai-doc-anh-goi-y-alt.md) |
| Ngày nộp | 2026-10-20 |
| Kết quả | Hoàn thành · Kết luận: **ĐẠT CÓ ĐIỀU KIỆN** |

## Tóm tắt (cho chủ dự án)

Phần lớn làm đúng: ảnh gửi thẳng trong lời gọi, luôn tới đúng máy chủ chính thức của hãng, không qua kho file hay đường dẫn; ảnh có EXIF/GPS, XMP hay chú thích ở các vị trí quen thuộc (kể cả giấu giữa các lượt quét hay nối sau ảnh) đều bị từ chối; chữ AI trả về không còn HTML/link và không vượt độ dài. Tìm ra **2 lỗi Trung bình** làm thông tin riêng có thể tới AI: (1) thẻ ảnh viết bằng ký tự "toàn chiều rộng" (`C：＼Users＼…`) lách được bộ lọc đường dẫn và tới AI thành đường dẫn thật; (2) bộ kiểm metadata chỉ chặn một số loại khối, khối lạ chứa GPS hay đường dẫn vẫn qua. Thêm 2 lỗi Thấp. Điều kiện: sửa 2 lỗi Trung bình (hoặc Chỉ Huy chấp nhận lỗi số 2 nếu T-049 bảo đảm ảnh gửi AI được nén lại từ đầu).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t050.py` (mới) | 42 hàm test (135 qua + 39 `xfail(strict=True)` cho 4 lỗi). Dùng lại ảnh giả và fixture mạng giả `network` của `tests/test_ai_images.py` |
| `docs/team/reports/T-050-soi-loi.md` (mới) | Báo cáo này |

Không sửa code ứng dụng. Commit trên `team/T-050`: `787c66f`, `ad01548` và commit báo cáo.

## Bằng chứng

```
$ uv run pytest            (Windows 11, worktree wt-T-050)
6072 passed, 11 skipped, 71 xfailed, 1 warning in 687.96s (0:11:27)
(= 5.937 qua của Thợ Máy + 135 test mới; 71 xfail = 32 cũ + 39 mới của phiếu này)

$ uv run pytest tests/test_soi_loi_t050.py tests/test_ai_images.py
281 passed, 39 xfailed in 27.70s

$ uv run ruff check .
All checks passed!
```

## Lỗi tìm thấy

### SL-T050-1 · Trung bình · Thẻ ảnh "toàn chiều rộng" lách bộ lọc đường dẫn, tới AI thành đường dẫn thật (A3)

- **Tái hiện:** `alt_prompt({"Thư mục": "C：＼Users＼Lam＼Nha anh Tuan"})` (hoặc `suggest_alt(..., tags=...)`).
- **Mong đợi:** thẻ bị bỏ như `C:\Users\…` (giá trị trông như đường dẫn không được gửi AI).
- **Thực tế:** `_short_text` (`seo_app/images/alt.py`) chỉ chuẩn hóa NFC rồi so `_PATH_LIKE`, nên `＼ ／ ： ．` không khớp. Sau đó khung dữ liệu `_block` chạy **NFKC**, đổi chúng về ASCII: yêu cầu gửi Anthropic chứa đúng dòng `Thư mục: C:\Users\Lam\Nha anh Tuan`. Cùng lỗi với `D：／Anh／…`, `＼＼may-chu＼…`, `IMG_0001．jpg`, `https：／／…`, `﹨` (U+FE68), và dấu gạch giống `/` không đổi qua NFKC: `∕` (U+2215), `⁄` (U+2044). Từ khóa (`keyword`) cũng vậy.
- **Gợi ý sửa:** chuẩn hóa NFKC (và bỏ ký tự vô hình) trước khi so; thêm `∕ ⁄` vào nhóm ký tự gạch chéo. Ký tự vô hình chen giữa (`D:\u200b/`, `.j\u200bpg`, U+034F, BOM, gạch nối mềm) đã bị bắt đúng.
- **Test:** `test_fullwidth_or_lookalike_path_tags_are_dropped` (8 trường hợp), `test_fullwidth_path_keyword_is_dropped`, `test_fullwidth_path_tag_never_reaches_ai_as_ascii_path` (thư viện anthropic thật, mạng giả).

### SL-T050-2 · Trung bình · Bộ kiểm metadata là "danh sách chặn": khối/chunk lạ chứa GPS, đường dẫn vẫn tới AI (A3, lớp kiểm thứ hai)

- **Tái hiện:** `prepare_images([ImageInput(data=make_jpeg(jpeg_segment(0xE3, b"Meta\0\0" + TIFF_có_GPS)), mime="image/jpeg")])`.
- **Mong đợi:** từ chối, như APP1/APP13/COM (báo cáo Thợ Máy: "từ chối gửi nếu ảnh còn sót thông tin kèm theo").
- **Thực tế:** qua, bytes được gửi nguyên cho hãng. Cùng kết quả với:
  - JPEG: APP3–APP12, APP15 chứa chữ tùy ý (ExifTool đọc nhiều khối loại này: Kodak "Meta" APP3, Ricoh "RMETA" APP5, GoPro APP6, "PictureInfo"/"Ducky" APP12). APP0 và APP2 không bắt đầu bằng `JFIF`/`ICC_PROFILE` cũng qua (không viết test xfail, ghi để cân nhắc).
  - PNG: chunk riêng/không chuẩn (`zxIf`, `exIf`, `prVt`…) chứa EXIF thô dạng TIFF (không có `Exif\0\0` nên bộ dò chuỗi không thấy); `iCCP` có tên hồ sơ là chữ tùy ý.
  - WebP: chunk `exif`, `xmp `, `XMP\0`, `META`… (chỉ đúng `EXIF`, `XMP ` bị chặn).
- **Đánh giá:** T-049 nếu nén lại ảnh bằng Pillow thì không chép các khối này, nên rủi ro thực tế hiện thấp; nhưng đây là lớp kiểm cuối trước khi bytes rời máy, và cách chặn theo danh sách đen sẽ lọt mọi khối chưa biết.
- **Gợi ý sửa:** chuyển sang **danh sách cho phép**: JPEG chỉ nhận APP0 `JFIF`/`JFXX`, APP2 `ICC_PROFILE`, APP14 `Adobe` cùng các khối ảnh (SOF, DHT, DQT, DRI, SOS, RST, DNL); PNG nhận chunk chính và các chunk phụ đã biết vô hại (`PLTE`, `tRNS`, `gAMA`, `cHRM`, `sRGB`, `iCCP`, `pHYs`, `sBIT`, `bKGD`); WebP nhận `VP8 `, `VP8L`, `VP8X`, `ALPH`, `ICCP`, `ANIM`, `ANMF`.
- **Test:** `test_jpeg_other_app_segments_with_private_data_are_rejected` (11 khối APPn), `test_png_unknown_chunks_with_raw_exif_are_rejected` (4), `test_webp_unknown_chunks_with_private_data_are_rejected` (4). Có sẵn test ảnh Pillow sạch kèm ICC phải qua (`test_clean_pillow_images_with_icc_pass`) để bản sửa không chặn nhầm.

### SL-T050-3 · Thấp · Ký tự điều khiển (NUL, BEL, ESC, DEL) còn trong alt/caption và trong thẻ

- **Tái hiện:** `clean_alt_text("Cổng\x00inox", 125)` → `'Cổng\x00inox'`; `reference_lines({"Hạng mục": "Cổng\x00inox\x1b[31m"})` giữ nguyên.
- **Mong đợi:** bỏ ký tự loại Cc (schema T-038 coi Cc là lỗi chặn; client WordPress có `_CONTROL_CHARS`). AI trả JSON `"\u0000"` là chuyện có thể xảy ra.
- **Thực tế:** `normalize_meta` chỉ bỏ Cf, `str.split()` không coi NUL/BEL/ESC/DEL là khoảng trắng.
- **Test:** `test_control_characters_are_removed_from_alt` (4), `test_control_characters_are_removed_from_tags`.

### SL-T050-4 · Thấp · Thẻ hoặc từ khóa có dấu "/" bị bỏ âm thầm

- **Tái hiện:** `reference_lines({}, keyword="sửa cửa cuốn 24/7")` → `[]`; thẻ `"Cổng/hàng rào inox"` cũng bị bỏ.
- **Mong đợi:** chữ thường có "/" (giờ, phân số, "A/B") vẫn được gửi; chỉ bỏ thứ thật sự trông như đường dẫn.
- **Thực tế:** `_PATH_LIKE` khớp bất kỳ `/` hoặc `\`. AI mất từ khóa chính mà người dùng không biết.
- **Gợi ý:** coi là đường dẫn khi có ổ đĩa, `~/`, `://`, hai đoạn trở lên kiểu `a/b/c`, hoặc đuôi file; hay ít nhất giữ từ khóa (người dùng tự gõ) và chỉ lọc thẻ.
- **Test:** `test_ordinary_text_with_slash_is_kept` (3).

## Đã thử, chạy đúng (có test)

- **Metadata giấu chỗ lạ:** APP1 EXIF/XMP và COM giữa hai lượt quét progressive, APP13, chuỗi `Exif\0\0` trong dữ liệu nén, XMP trong APP15, PNG `tEXt` sau IDAT, XMP trong chunk riêng: đều bị từ chối với câu metadata. Bất cứ gì sau EOI/IEND/khối RIFF (1 byte, `FF`, EOI lặp, ảnh thứ hai, MPO của Pillow), chunk khai dài quá, RIFF khai sai kích thước: từ chối. `Exif\0\0` tách đôi qua hai khối APP15 không bị dò chuỗi bắt (ghi nhận; sẽ bị chặn khi sửa SL-T050-2).
- **Giới hạn:** ảnh đúng 5 MB qua, 5 MB + 1 byte bị từ chối; tổng đúng 10 MB (2 × 5 MB, 4 × 2,5 MB) qua, vượt 1 byte bị từ chối; 4 ảnh qua, 5 ảnh bị từ chối trước khi đọc ảnh nào; generator/set bị từ chối. Ảnh 5 MB tới đúng máy chủ chính thức của cả 3 hãng, không qua đường `upload`/`files`.
- **`bytearray` bị sửa sau khi kiểm:** chèn EXIF vào `bytearray` ngay sau `prepare_images` (giả lập bằng monkeypatch trong provider Anthropic): yêu cầu gửi đi vẫn là bản đã kiểm; `suggest_alt` truyền `bytes` bất biến.
- **MIME:** `image/jpeg; name=IMG_0001.jpg`, MIME có xuống dòng kiểu header, SVG, HTML, HEIC, GIF, rỗng: từ chối, câu báo không chép giá trị. `" IMAGE/JPG "` gửi đi thành `image/jpeg`.
- **Thẻ:** ký tự vô hình chen vào đường dẫn bị bắt; xuống dòng trong nhãn/giá trị bị gộp một dòng; độ dài đếm theo NFC; thẻ rác không chiếm chỗ 8 thẻ; thẻ không phải chữ bị bỏ; `ai_generated=True` bỏ hết thẻ (kể cả thẻ độc), giữ từ khóa và câu "ảnh minh họa do AI tạo".
- **Khung dữ liệu:** thẻ/nhãn/từ khóa chứa `＜／du_lieu_tham_khao＞`, `< du_lieu_tham_khao >`, chữ hoa, chen U+200B/U+3164, `<ho_so_doanh_nghiep>`, `<de_bai>…</de_bai>`: khung vẫn đúng một cặp, không mở được khung khác.
- **Chữ AI trả về** (16 mẫu × 2 giới hạn): toàn dấu `\`, `\[\]\(` lặp, `[](` lặp, link lồng 3 tầng, ảnh Markdown, link tham chiếu, `<https://…>`, `www.`, email, `<img onerror>`, `<script>` lồng nhau, `<[](x)script>`, xuống dòng đủ kiểu (`\r`, U+2028/2029, `\x0b`, `\x0c`, `\x85`), NFD dài, ký tự đảo chiều: luôn ≤ giới hạn, một dòng, không thẻ, không `://`, không `](` chưa escape, chạy lại không đổi. Alt rỗng sau lọc → câu tiếng Việt; caption rỗng sau lọc được chấp nhận; provider trả sai khuôn → câu tiếng Việt.
- **Đầu-cuối 3 hãng** (thư viện thật, mạng giả, biến môi trường `*_BASE_URL` và `*_CUSTOM_HEADERS` độc): `suggest_alt` với việc bật `web_search` → mỗi hãng đúng 1 yêu cầu tới máy chủ chính thức, không `tools`/`google_search`, không `file_id`/`fileUri`, thẻ dạng đường dẫn không có trong yêu cầu, alt trả về đã lọc HTML/link.
- **Lỗi máy chủ kèm ảnh:** 400/413/422/500 × 3 hãng có câu máy chủ chứa khóa giả và base64 ảnh: câu báo không chép gì trong số đó, mọi yêu cầu tới đúng máy chủ. Gemini lỗi 400 "thinking" gọi lại lần 2: vẫn `inlineData`, đúng máy chủ, `:generateContent`. `OPENAI_ORG_ID`/`OPENAI_PROJECT_ID` không thành header khi kèm ảnh.

## Rủi ro và điểm cần chú ý

1. **Câu báo khi ảnh quá lớn với máy chủ:** 413 ra "…báo lỗi 413. Thử lại sau ít phút." (thử lại không giúp gì); 400 vì ảnh ra gợi ý "Kiểm tra tên mô hình và các thông số…". Nên thêm câu gợi ý riêng khi yêu cầu có ảnh (ví dụ "ảnh quá lớn hoặc hãng không đọc được ảnh").
2. **Giới hạn ảnh của Anthropic:** T-046 ghi 10 MB/ảnh (base64). Theo tài liệu tôi biết trước đây, API ghi 5 MB/ảnh; nếu 5 MB tính trên chuỗi base64 thì ảnh thô trên khoảng 3,75 MB bị từ chối. Chưa kiểm được khi không gọi mạng thật; bản gửi AI chỉ vài trăm KB nên ít ảnh hưởng. Đề nghị Thợ Máy/Lá Chắn xác nhận lại trên trang Vision, hoặc hạ `MAX_IMAGE_BYTES` về 3,75 MB cho chắc.
3. **Không kiểm kích thước điểm ảnh** (Anthropic tối đa 8000 px, OpenAI giới hạn số ô): dựa vào T-049 thu nhỏ về 1024 px. Đọc chiều rộng/cao từ IHDR/SOF/VP8X rất rẻ nếu muốn chặn sớm.
4. **Dữ liệu giấu trong phần ảnh nén** (giữa dữ liệu quét JPEG, trong IDAT sau dòng zlib, trong mô tả ICC) không thể phát hiện nếu không giải nén: T-049 phải **nén lại ảnh từ điểm ảnh**, không chép khối từ file gốc. Nên có test ở T-049 rằng bản gửi AI chỉ chứa các khối trong danh sách cho phép.
5. **Chữ trong ảnh (biển hiệu, giấy tờ) là đường chèn lệnh** (Ngòi Bút T-051 lưu ý). Đánh giá: lời dặn hệ thống nói rõ chữ trong ảnh là dữ liệu; AI không có công cụ nào (tìm web bị tắt); kết quả chỉ là 2 trường chữ, đã lọc, ≤ 125/200 ký tự, và người dùng duyệt trước khi dùng. Rủi ro còn lại: AI chép số điện thoại, tên người, chữ quảng cáo từ biển hiệu vào alt; code không lọc những thứ này. Giao diện T-056 phải hiện alt để duyệt; có thể thêm cảnh báo khi alt có dãy số giống số điện thoại.
6. **Thẻ chứa tên khách** (ví dụ thư mục "Nhà anh Tuấn - 12 Lê Lợi") không trông như đường dẫn nên vẫn được gửi: bộ lọc của T-050 không thể biết; T-052 (chuẩn hóa thẻ) phải chịu trách nhiệm.
7. **Escape Markdown còn trong alt:** khi AI viết `](`, alt chứa `]\(`. T-054 ngoài `unbreak_autolinks` còn phải gỡ escape link trước khi ghi alt vào thuộc tính HTML (rồi escape HTML).
8. Alt chỉ gồm dấu `\` dưới giới hạn (ví dụ 50 dấu) được nhận làm alt, còn 400 dấu thì báo lỗi rỗng: không nhất quán, ảnh hưởng nhỏ.

## Đề xuất

- Giao Thợ Máy sửa SL-T050-1 và SL-T050-2 (trọng tâm), kèm SL-T050-3, SL-T050-4 nếu tiện; gỡ dấu `xfail` khi test báo XPASS.
- Lá Chắn soát lại A3 sau khi sửa, và xem điểm 2 (giới hạn Anthropic).
- T-049: thêm test bản gửi AI chỉ có khối trong danh sách cho phép (điểm 4). T-054: gỡ escape link trước khi ghi alt (điểm 7). T-056: hiện alt để duyệt, cân nhắc cảnh báo số điện thoại (điểm 5).

## Câu hỏi cho chủ dự án

Không có.

---

## Lượt 2 (2026-10-20, kiểm lại sau Thợ Máy lượt 2)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Việc | Xác nhận SL-T050-1 → -4 đã sửa; tìm cách lách bản sửa mới (`seo_app/ai/base.py:552–790`, `seo_app/images/alt.py:96–143`) |
| Kết quả | Hoàn thành · Kết luận: **ĐẠT** (chuyển Lá Chắn được). 4 lỗi lượt 1 đã sửa thật; 2 lỗi mới đều mức **Thấp** |

### Tóm tắt (cho chủ dự án)

Bốn lỗi lượt trước đã được sửa thật: thẻ ảnh viết bằng ký tự "toàn chiều rộng" không còn tới AI thành đường dẫn, ảnh có khối lạ chứa GPS bị từ chối, từ khóa "24/7" không còn bị bỏ, ký tự điều khiển bị bỏ. Ảnh sạch thật không bị chặn nhầm (thử 965 ảnh do Pillow tạo và ảnh iPhone HEIC), chữ tiếng Việt đủ dấu và thẻ kiểu `CT012 - Cổng inox - Tân Phú/truoc` được giữ nguyên. Tìm ra 2 chỗ hở nhỏ (Thấp): ai **cố tình dựng** ảnh vẫn giấu được chữ hay tọa độ GPS trong hồ sơ màu của ảnh, hoặc trong vài khối kỹ thuật được phép lặp lại. Ảnh bình thường (kể cả ảnh gốc từ điện thoại) không tự sinh ra những khối này, nên không cần chặn việc chuyển sang Lá Chắn.

### Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t050.py` | Thêm mục 6 "lượt 2" (dòng 692 tới hết): 72 test qua + 15 `xfail(strict=True)` cho SL-T050-5 (6 ca) và SL-T050-6 (9 ca). Dùng lại ảnh giả của `tests/test_ai_images.py` và fixture `heif_registry_restored` của `tests/test_pillow_heif_setup.py` (trả nguyên bảng định dạng của Pillow sau test) |
| `docs/team/reports/T-050-soi-loi.md` | Mục "Lượt 2" này |

Không sửa code ứng dụng. Commit trên `team/T-050`: `c43a321` (test) và commit báo cáo này.

### Xác nhận 4 mã lượt 1

`git diff 8ea45df..HEAD -- tests/test_soi_loi_t050.py`: Thợ Máy chỉ bỏ các dấu `xfail` (`SL1`, `SL2`, 2 dấu SL-T050-3, 1 dấu SL-T050-4) và thêm dòng chú thích "Thợ Máy lượt 2 đã sửa"; không đổi điều kiện kiểm hay dữ liệu thử nào. 39 test trước đây `xfail` nay qua:

| Mã | Test (số ca) | Kết quả |
|---|---|---|
| SL-T050-1 | `test_fullwidth_or_lookalike_path_tags_are_dropped` (8), `test_fullwidth_path_keyword_is_dropped` (3), `test_fullwidth_path_tag_never_reaches_ai_as_ascii_path` (1, thư viện anthropic thật, mạng giả) | qua |
| SL-T050-2 | `test_jpeg_other_app_segments_with_private_data_are_rejected` (11), `test_png_unknown_chunks_with_raw_exif_are_rejected` (4), `test_webp_unknown_chunks_with_private_data_are_rejected` (4) | qua |
| SL-T050-3 | `test_control_characters_are_removed_from_alt` (4), `test_control_characters_are_removed_from_tags` (1) | qua |
| SL-T050-4 | `test_ordinary_text_with_slash_is_kept` (3) | qua |

### Bằng chứng

```
$ git pull --ff-only        (đầu phiên, worktree wt-T-050, HEAD c3910e0)
Already up to date.

$ uv run pytest tests/test_soi_loi_t050.py tests/test_ai_images.py      (tại c3910e0, trước khi thêm test)
418 passed in 90.67s (0:01:30)

$ uv run pytest            (tại c3910e0, chạy song song với các script thử nên chậm)
7588 passed, 11 skipped, 27 xfailed, 1 warning in 1227.08s (0:20:27)

$ uv run pytest            (tại c43a321, có test lượt 2)
7660 passed, 11 skipped, 42 xfailed, 1 warning in 783.03s (0:13:03)
(= 7.588 + 72 test mới; 42 xfail = 27 của phiếu khác + 15 mới; 0 hỏng, 0 lỗi. Cảnh báo là của
 test cũ tests/test_soi_loi_t028.py (pydantic), như các lượt trước)

$ uv run pytest tests/test_soi_loi_t050.py tests/test_ai_images.py      (tại c43a321)
490 passed, 15 xfailed in 29.65s
(= 418 cũ + 72 test mới qua; 15 xfail = SL-T050-5 (6) + SL-T050-6 (9))

$ uv run pytest tests/test_soi_loi_t050.py --runxfail -k "outside_tag_table or longer_than_shape"
15 failed  (cả 15 hỏng đúng ở "assert not accepted(data, mime)": ảnh độc được nhận)

$ uv run ruff check .
All checks passed!
```

### Lỗi mới

#### SL-T050-5 · Thấp · Hồ sơ màu ICC chỉ được kiểm phần đầu: chở được EXIF có GPS, XMP, chữ tùy ý (A3, lớp kiểm cuối)

- **Tái hiện:** hồ sơ màu = 132 byte đầu hợp lệ (khai đúng độ dài, chữ ký `acsp`, bảng thẻ rỗng) + EXIF thô `MM\0*…GPS 16.0544N 108.2022E; D:/Anh/Nha anh Tuan 12 Le Loi/IMG_0001.jpg`. Đặt vào JPEG APP2 `ICC_PROFILE`, PNG `iCCP` tên `ICC Profile`, hay WebP `ICCP`, rồi gọi `prepare_images`.
- **Mong đợi:** từ chối như các khối metadata khác; chú thích `seo_app/ai/base.py:552–553` hứa "khối được nhận phải đúng khuôn của nó (không còn chỗ nhét chữ tự do)".
- **Thực tế:** qua ở cả 3 định dạng. `_icc_ok` (`base.py:563–569`) chỉ so độ dài khai báo và chữ ký, không đọc bảng thẻ, nên mọi byte sau phần đầu đều được nhận. Ở PNG còn tệ hơn: hồ sơ được nén zlib nên cả gói `Exif\0\0…` hay XMP đầy đủ cũng qua mắt bộ dò chuỗi `_has_metadata_marker` (`base.py:545–549`). Ở JPEG, tách `Ex|if\0\0` qua 2 khối APP2 cũng qua.
- **Đánh giá:** Pillow chỉ chép hồ sơ màu có sẵn của ảnh gốc; hồ sơ của máy ảnh, điện thoại là hồ sơ chuẩn (sRGB, Display P3), không chứa GPS. Rủi ro còn lại là suy luận, chưa thử với file thật: ảnh đã qua phần mềm chỉnh sửa có thể mang hồ sơ màu của màn hình đã cân màu, loại này có thể có thẻ riêng ghi tên, đời hay số seri màn hình. Vì vậy mức Thấp.
- **Gợi ý sửa (Chỉ Huy chọn):**
  - (a) Đơn giản nhất: T-049 đổi bản gửi AI về sRGB và **không** kèm hồ sơ màu (AI viết alt không cần); `prepare_images` từ chối mọi hồ sơ màu. Khi đó phải đổi các test đang yêu cầu ảnh có ICC được qua (`test_clean_pillow_images_with_icc_pass`, `test_pillow_images_of_every_kind_pass`, `test_allowed_blocks_in_right_shape_pass`…), cần Chỉ Huy duyệt vì đổi thiết kế T-046.
  - (b) Kiểm bảng thẻ: số thẻ hợp lý, mỗi thẻ nằm trong hồ sơ, **mọi byte sau bảng thẻ thuộc một thẻ** (chỉ cho tối đa 3 byte đệm 0), chỉ nhận thẻ màu chuẩn (`desc cprt wtpt bkpt rXYZ gXYZ bXYZ rTRC gTRC bTRC kTRC chad chrm lumi meas tech dmnd dmdd view A2B* B2A*`…), thẻ chữ ngắn. Cách này làm 6 test xfail qua, nhưng vẫn để lọt khoảng một câu chữ trong thẻ mô tả `desc`.
- **Test:** `test_icc_profile_with_data_outside_tag_table_is_rejected` (6 ca, `tests/test_soi_loi_t050.py:767`). Đối chứng `test_icc_builders_without_tail_pass` (3 ca): cùng cách dựng, hồ sơ không có đuôi thì qua, tức test xfail hỏng vì đuôi chứ không vì khuôn ảnh.

#### SL-T050-6 · Thấp · Khối được nhận lặp lại hoặc dài hơn khuôn, chở được chữ tùy ý

- **Tái hiện:** JPEG có 9 khối APP0 `JFIF\0` + 7 byte chữ + `\0\0` (mỗi khối đúng 14 byte, phần mật độ điểm ảnh là chữ: ghép lại được cả câu `SECRET`); tương tự 9 khối APP14 `Adobe`; khung ảnh SOF, DRI, DNL, đầu lượt quét SOS có chữ nối sau phần khuôn. PNG ảnh RGB có `PLTE` 63 byte chữ, `tRNS` 60 byte chữ, `cHRM` đúng 32 byte `GPS 16.0544N 108.2022E Le Loi 12`.
- **Mong đợi:** từ chối. Pillow ghi mỗi khối một lần, đúng độ dài, không ghi PLTE cho ảnh RGB, không ghi cHRM.
- **Thực tế:** qua. `_jpeg_app_ok` (`base.py:593–606`) kiểm khuôn từng khối APP0/APP14 nhưng không đếm số lần; khối giải mã (`base.py:651–656`) không kiểm độ dài; PNG chỉ kiểm độ dài **tối đa** (`_PNG_ALLOWED`, `base.py:690–693`), không theo loại màu. Chú thích `base.py:686–687` ("độ dài cố định và nhỏ, không chứa chữ tự do") chưa đúng: `cHRM` 32 byte đủ chứa một tọa độ GPS.
- **Đánh giá:** chỉ ảnh dựng cố ý mới có; không phần mềm nào tự sinh. Thấp; sửa rẻ.
- **Gợi ý sửa:** APP0 và APP14 tối đa một lần; SOF đúng 6 + 3·(số thành phần) byte, SOS đúng 4 + 2·(số thành phần), DRI và DNL đúng 2 byte; PNG: `PLTE` chỉ khi loại màu 3 (độ dài chia hết cho 3), `tRNS` đúng độ dài theo loại màu (2 / 6 byte, hoặc ≤ số màu), bỏ `cHRM`, `sBIT`, `bKGD` khỏi danh sách (khi lưu bản gửi AI, Pillow 12.3 chỉ ghi chúng nếu được truyền `pnginfo`: `PngImagePlugin._save`). Sửa lại 2 chú thích trên cho đúng.
- **Test:** `test_allowed_blocks_repeated_or_longer_than_shape_are_rejected` (9 ca, `:817`). Đối chứng `test_decode_segments_in_right_shape_pass` (2 ca: SOF, DRI đúng khuôn phải qua, để bản sửa không chặn nhầm).

### Đã thử, chạy đúng (có test) hoặc chỉ ghi nhận

**Khối ảnh**

- **Bị từ chối đúng:** JFIF có ảnh nhỏ 1×1, `JFXX`; PNG `iCCP` tên khác `ICC Profile`, `iCCP` lặp; hồ sơ màu chứa nguyên chuỗi `Exif\0\0` ở JPEG và WebP (bộ dò chuỗi bắt).
- **Bom giải nén, ảnh to:** `iCCP` bom 1 GB bị từ chối sau 0,03 giây (giải nén dừng ở 5 MB); hồ sơ giải nén đúng 5 MB qua, 5 MB + 1 byte bị từ chối; `IDAT` bom 1 GB không bị giải nén (0,00 giây). Đo một lần gửi 2 ảnh × 5 MB (đúng mức tổng tối đa 10 MB), máy rảnh, trường hợp chậm nhất: dữ liệu nén toàn byte `FF FF…` 5,0 giây; `FF 00` 2,0 giây; mã RST 2,3 giây; khoảng 1,3 triệu khối DHT rỗng mỗi ảnh 3,2 giây; khoảng 480 nghìn lượt quét mỗi ảnh 1,9 giây; khoảng 290 nghìn khối JFIF mỗi ảnh 1,2 giây. Không treo, không tràn đệ quy; bản gửi AI thật chỉ vài trăm KB. Test: `test_png_iccp_decompression_bomb_is_rejected` (bom 64 MB).
- **Ảnh sạch thật không bị chặn nhầm:** Pillow 12.3.0 (bản trong `uv.lock`, giống `main`): ma trận 965 ảnh (5 cỡ từ 1×1 tới 1024×768, 8 chế độ màu, 17 kiểu lưu JPEG gồm progressive, optimize, restart marker, `qtables`, subsampling, ICC, dpi, `keep_rgb`; 8 kiểu PNG; 9 kiểu WebP) → 0 ảnh bị từ chối. 22 kiểu chưa có trong test của Thợ Máy đưa vào `test_more_clean_pillow_images_pass` (ảnh có nhiễu để dữ liệu nén có đủ loại byte).
- **Ảnh HEIC qua pillow-heif 1.8.1** (libheif 1.23.6): HEIC có EXIF + GPS, XMP, hồ sơ màu (và loại không có ICC, chỉ `nclx`), mở bằng Pillow, thu nhỏ, lưu JPEG/PNG/WebP chỉ kèm `icc_profile` → qua; lưu mặc định với `info` của HEIC → qua (Pillow 12.3 không tự chép `exif`/`xmp` sang 3 định dạng này); lỡ kèm `exif=` → từ chối "còn thông tin kèm theo". Test: `test_heic_photo_read_with_pillow_heif_makes_clean_ai_copy` (3).
- **Ghi nhận cho T-049** (Pillow 12.3): lưu lại một JPEG gốc có chú thích (COM) thành JPEG mà **không** truyền `comment` thì Pillow vẫn tự chép chú thích (lớp kiểm từ chối, đúng); lưu PNG thì Pillow tự chép hồ sơ màu từ `im.info`. T-049 nên xóa `info` của ảnh trước khi lưu bản gửi AI và chỉ truyền đúng thứ cần. Test: `test_pillow_resaved_jpeg_with_comment_is_rejected_if_comment_is_copied` (đúng với mọi bản Pillow: còn chú thích thì phải bị từ chối).
- **Chỉ ghi nhận, không viết test xfail** (dữ liệu nằm trong phần ảnh nén hay bảng giải mã, không kiểm được nếu không giải mã, Thợ Máy đã nêu): giá trị bảng lượng tử DQT, bảng mã DHT; dữ liệu nén JPEG; dữ liệu thừa sau dòng zlib trong `IDAT` (kể cả EXIF nén trong `IDAT`); CRC chunk PNG không được kiểm (4 byte mỗi chunk); WebP: 3 byte dành riêng của `VP8X`, nội dung `ALPH`, dữ liệu thừa trong `VP8L`, byte đệm khác 0. WebP `VP8X` bật cờ EXIF/XMP/ảnh động mà không có chunk: qua, vô hại (chỉ là cờ 1 bit). JPEG không có khung ảnh SOF, PNG không có `IDAT`: qua (ảnh không giải mã được, không lộ gì).

**Thẻ và từ khóa**

- **Chữ kiểm = chữ gửi:** chèn lần lượt cả 1.112.064 ký tự Unicode vào giữa một thẻ: không ký tự nào làm chữ được nhận khác chữ tới AI (`_neutralize` không đổi gì, chạy lại không đổi); 200.000 chuỗi ngẫu nhiên: 0 lệch. Test: `test_random_tags_reach_ai_exactly_as_checked` (3.000 chuỗi trộn chữ tách dấu, ký tự toàn chiều rộng, vô hình, điều khiển, `/`, `:`; hạt giống cố định).
- **Ký tự giả còn lọt:** 1.124 ký tự ngoài ASCII qua danh sách cho phép, đều là chữ Latin. Vài chữ trông như dấu câu: `ǀ ǁ ǃ` (chữ "click" Latin, trông như `|`, `||`, `!`), `ꞏ` (trông như `·`), `ʔ`. Không chữ nào trông như `/`, `\` hay `:`, nên không ghép được thành đường dẫn thật (`ǀǀmay-chuǀchia-se` được giữ nhưng không phải đường dẫn nào trên máy). Ghi nhận.
- **Không chặn nhầm tiếng Việt:** 23 thẻ/từ khóa (đủ dấu, chữ hoa, `Đ/đ`, chữ tách dấu kiểu Mac, `TP.HCM`, `P.12, Q.Gò Vấp`, `5×20 m`, `90°`, `Bước 1: tháo lò xo`, thẻ 3A `CT012 - Cổng inox - Tân Phú/truoc` và `/trước`) đều giữ nguyên, ở cả vị trí thẻ lẫn từ khóa. Test: `test_common_vietnamese_tags_and_keywords_are_kept` (23).
- **Đường dẫn thật bị bỏ:** Google Drive for Desktop trên Windows (`G:/My Drive/…`, `G:\My Drive\…`) và Mac (`/Users/…/CloudStorage/GoogleDrive-…@gmail.com/…`), OneDrive, NAS `\\NAS\…`, `~/Pictures`, USB `/Volumes/…`, thẻ nhớ `E:/DCIM/…`, `file:///`, bản toàn chiều rộng `Ｇ：／My Drive／…`, 3 cấp `My Drive/CT012…/truoc`, tên file `IMG_0001 (1).jpg`, `.jpg.webp`, `.HEIC`, tên ảnh chụp màn hình tiếng Việt và tiếng Anh; ở nhãn, giá trị lẫn từ khóa. Test: `test_real_paths_and_file_names_are_dropped` (16).
- **Được giữ theo thiết kế SL-T050-4** (một dấu `/`; ghi nhận cho T-052): `Users/Lam`, `Lam/Desktop`, `My Drive/CT012`, `OneDrive - Personal/Anh`, `Anh/IMG_0001` (tên file đã bỏ đuôi), `%USERPROFILE%/Anh`, `facebook.com/nhaanhtuan`. Không có ổ đĩa hay gốc thư mục, nhưng `Users/Lam` lộ tên tài khoản máy. T-052 nên chỉ đưa vào thẻ phần tên thư mục **bên dưới** thư mục ảnh đã khai báo (đúng như 3A), không đưa phần đầu đường dẫn.
- **Bị bỏ âm thầm (chặn nhầm nhẹ, ghi nhận):** ngày `15/10/2026` và `Cổng/cửa/hàng rào` (từ 2 dấu `/` liền chữ: đúng như gợi ý lượt 1 của chính Soi Lỗi), `A: cổng chính` (giống ổ đĩa), `Giá 1.500.000₫` (`₫`), `Cửa 1½ cánh` (NFKC đổi thành `1⁄2`), `Cổng • Hàng rào`, `Cổng · inox`, `Cửa cuốn ~2m`, `Bảo hành 12 tháng*`, `Cửa «Đài Loan»`, `Cổng /hàng rào` (dấu cách trước `/`). Thẻ từ tên thư mục khó gặp các dạng này (Windows cấm `* : |` trong tên thư mục), từ khóa chính hiếm khi có. Nếu muốn nới: coi `số/số/số` là ngày, thêm `₫ • · « »` vào danh sách.

### Rủi ro và điểm cần chú ý

1. Lớp kiểm này chỉ là **lớp cuối**: dữ liệu giấu trong phần ảnh nén (JPEG, `IDAT`, `VP8L`, `ALPH`) và trong bảng giải mã không thể thấy nếu không giải mã. T-049 vẫn phải dựng bản gửi AI lại từ điểm ảnh, và xóa `info` (chú thích JPEG, hồ sơ màu PNG được Pillow tự chép) trước khi lưu.
2. Số đo thời gian ở trên chỉ để thấy "không treo" (ảnh dựng cố ý, chậm nhất 5 giây cho 10 MB); không viết test đo tốc độ (dễ đỏ oan, xem T-025).
3. Các điểm "Rủi ro" lượt 1 không thuộc 4 mã lỗi (số 1, 2, 3, 5, 7, 8) chưa đổi; Thợ Máy đã ghi chưa làm.

### Kết luận

**ĐẠT**: chuyển Lá Chắn được. 4 lỗi lượt 1 đã sửa thật (39 test qua, không đổi điều kiện); không còn lỗi Trung bình trở lên. 2 lỗi mới SL-T050-5 và SL-T050-6 đều **Thấp** (chỉ ảnh dựng cố ý mới lợi dụng được; bản gửi AI của T-049 dựng lại từ điểm ảnh). Chỉ Huy chọn sửa luôn ở một lượt nhỏ hoặc gom vào phiếu dọn lỗi Thấp; 15 test `xfail(strict=True)` sẽ báo XPASS khi sửa xong để gỡ dấu.

### Đề xuất

- Lá Chắn soát A3 sau lượt 2: xem SL-T050-5 (chọn cách a hay b) và 2 chú thích `base.py:552–556`, `:686–687` đang nói quá khả năng của lớp kiểm.
- T-049: bản gửi AI không mang `info` của ảnh gốc (chú thích JPEG, hồ sơ màu PNG được Pillow tự chép); nếu chọn cách (a) của SL-T050-5 thì đổi màu về sRGB và không kèm hồ sơ màu.
- T-052: chỉ đưa vào thẻ phần tên thư mục bên dưới thư mục ảnh đã khai báo (thẻ một dấu `/` như `Users/Lam` giờ được gửi AI).

### Câu hỏi cho chủ dự án

Không có.

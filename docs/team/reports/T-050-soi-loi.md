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

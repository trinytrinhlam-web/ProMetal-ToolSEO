# Biên bản bảo mật T-067 · Dọn lỗi Thấp xử lý ảnh (sau T-049), kiểm rút gọn

> **Model:** chạy tạm Claude Opus 5.5 vì tài khoản không dùng được Fable (chủ dự án đã duyệt). **Sau 01/11 phải kiểm lại bằng Fable.**

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-067](../tickets/T-067-don-loi-thap-xu-ly-anh.md) |
| Phạm vi | Kiểm **rút gọn**: diff `origin/main...team/T-067` tại `46f1bf7` (gốc chung `6ed41e2`): `seo_app/images/process.py` (+66 −18), `tests/test_images_process.py` (+199, Thợ Máy), `tests/test_soi_loi_t049.py` (gỡ 3 `xfail`), `tests/test_soi_loi_t067.py` (+471, Soi Lỗi), 2 báo cáo. Đọc thêm code xung quanh trong `process.py` (`_open`, `_KeptExif`, `_verify_web_image`, `make_web_image`, `PreviewCache`) và chỗ Pillow 13.0.0 đã cài gọi `_decompression_bomb_check` |
| Ngày | 2026-10-20 |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** (0 Nghiêm trọng, 0 Cao, 0 Trung bình; 1 Thấp: LC-T067-1 = SL-T067-1). Gộp vào `main` được ngay; điều kiện ở mục cuối |

## Tóm tắt (cho chủ dự án)

- **An toàn để gộp.** Ba lỗi nhỏ còn lại của phần xử lý ảnh (T-049) đã được sửa đúng: (1) ảnh có GPS ghi sai chuẩn không còn lên web với vị trí sai bán cầu, app bỏ vị trí của ảnh đó và báo một câu cố định; (2) ảnh xem trước luôn kiểm phiên bản thư viện ảnh, kể cả ảnh đã lưu sẵn; (3) nhiều tab mở ảnh cùng lúc không còn làm rối lớp chặn "ảnh bom". Ảnh chụp bình thường vẫn **giữ đúng vị trí GPS từng con số** (quyết định 2A), bản gửi AI vẫn **sạch hoàn toàn** thông tin kèm theo.
- **1 lỗi nhỏ (Thấp), không chặn gộp:** ảnh **không có vị trí** mà có một thẻ GPS phụ ghi sai chuẩn bị báo nhầm "GPS bị hỏng". Không lộ gì, không sai vị trí, chỉ là câu báo gây hiểu lầm. Lá Chắn khuyên sửa trước khi làm màn hình chọn ảnh (T-056), cùng lúc nới cách xử lý để thẻ phụ sai chỉ bỏ riêng thẻ đó, **giữ vị trí** cho SEO địa phương.
- Sau khi gộp phiếu này: T-054 (chèn ảnh vào bài nháp) hết bị chặn bởi lỗi T-049; T-056 cần thêm bản sửa nhỏ nói trên.

## Lỗi phát hiện

Không có lỗi Nghiêm trọng, Cao hay Trung bình. Bản sửa không mở lỗ mới nào. 1 lỗi Thấp (Soi Lỗi đã tìm, Lá Chắn đồng ý mức).

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T067-1 (= SL-T067-1) | Thấp | Kiểm thẻ Ref mới chạy **trước** nhánh "không có tọa độ" và không xét ảnh có tọa độ hay không: ảnh không có vĩ độ, kinh độ mà có một thẻ Ref **phụ** sai khuôn bị báo `_NOTICE_GPS_BROKEN`. Cùng gốc: thẻ Ref phụ sai (kể cả `GPSAltitudeRef` = 2, 3 mà Exif 3.0 có thể coi là hợp lệ) làm **mất cả vị trí** của ảnh có tọa độ đúng | `process.py:496-501` (chạy trước `:502-507`), `:340-351` (`_GPS_REF_TAGS` gồm 8 thẻ Ref phụ), `:400-401` (`byte01`) | Máy tắt định vị nhưng vẫn ghi `GPSSpeedRef = "k"` (hoặc độ cao `\x04`) → `make_web_image` → `web.gps is None` (đúng), `notice` = "Thông tin GPS của ảnh gốc bị hỏng…" (sai sự thật) → khi T-056 hiện câu này, chủ dự án tưởng máy ảnh hỏng định vị. Lá Chắn tái hiện được (T1 ở dưới). **Không lộ** thông tin nào, **không đăng** giá trị sai nghĩa. Mất vị trí vì Ref phụ sai là hướng an toàn (ít thông tin hơn), chỉ hại SEO địa phương | **Phương án (b) của Soi Lỗi** (Lá Chắn chọn): Ref vĩ độ, kinh độ sai khuôn → giữ như nay (bỏ cả khối GPS, báo). Ref **phụ** sai khuôn → bỏ **cả cặp** (Ref và giá trị đi kèm: `GPSAltitude`, `GPSSpeed`, `GPSTrack`, `GPSImgDirection`, `GPSDestLatitude`, `GPSDestLongitude`, `GPSDestBearing`, `GPSDestDistance`), giữ vị trí, không báo. **Không** nhận thêm `GPSAltitudeRef` = 2, 3 (trình đọc cũ có thể hiểu 3 là "trên mặt biển"). Ảnh không có tọa độ thì đi tiếp nhánh `:502-507` như T-049. Chi tiết và cách đổi test ở mục "Đánh giá SL-T067-1" |

## Kiểm các lỗi của T-049

| Mục | Kết quả | Bằng chứng |
|---|---|---|
| **LC-T049-1** Ref GPS sai khuôn | **Đã sửa** | `process.py:496-501`: thẻ Ref **có trong ảnh gốc** (`tag in gps_ifd`) mà không qua `_valid` (`tag not in kept.gps`) → `_KeptExif` giữ hãng, đời máy, ngày chụp nhưng GPS rỗng, `notice = _NOTICE_GPS_BROKEN` (câu cố định `:104`). `_verify_web_image` (`:740-766`) so file ra với GPS rỗng, nên file ra chắc chắn **không còn thẻ GPS nào**; `web.gps = _coordinates({}) = None` (`:803`). Không còn nhánh nào chuẩn hóa hay đoán lại bán cầu. **GPS đúng khuôn giữ đúng giá trị (2A):** `_verify_web_image` không đổi, vẫn so từng giá trị; test `tests/test_images_process.py:924` (Nam/Tây, dưới mặt biển, `K`, vĩ độ đích `S`), `tests/test_soi_loi_t067.py:173` (đủ 10 thẻ Ref × 2 bán cầu × 4 định dạng: khối GPS đọc lại bằng gốc), ma trận 32 + 24 ca của Soi Lỗi T-049 vẫn qua. Thử T1 của Lá Chắn: khớp |
| **LC-T049-2** cache xem trước kiểm Pillow 13 | **Đã sửa** | `process.py:944`: `_require_pillow_13()` là dòng đầu của `PreviewCache.get`, trước `stat_image` (`:945`) và trước `_read` cache (`:948`). Các đường còn lại (`make_web_image`, `make_ai_image`, `make_preview`, `open_image`) đều qua `_open` (`:207`). Test `tests/test_images_process.py:1322` (cache có sẵn, Pillow "12.3.0": câu cố định, không gọi `stat_image`/`read_image_bytes`, file cache không đổi), `tests/test_soi_loi_t067.py:249` (5 phiên bản < 13 × cache bật/tắt), `:269` (≥ 13 vẫn trả ảnh), test cũ `tests/test_soi_loi_t049.py:719` nay qua |
| **LC-T049-3** khóa quanh mở ảnh | **Đã sửa** | `process.py:85` khóa `threading.Lock` của module; `:191-200` `_pillow_open`: `with _WARNINGS_LOCK, warnings.catch_warnings():` (lấy khóa trước, trả bộ lọc trước rồi mới nhả khóa) bọc **đúng** lời gọi `Image.open`; `:213-236` kiểm 80 triệu điểm ảnh, `draft`, `load` nằm ngoài khóa nhưng vẫn trong khối `try` bắt lỗi như cũ. **Khóa luôn được nhả:** câu `with` nhả khóa với mọi ngoại lệ kể cả `BaseException`; khóa không gọi lồng (trong `Image.open` không có đường quay lại code của app), nên không tự khóa chết. **Đủ phạm vi:** Lá Chắn soát Pillow 13.0.0 đã cài: với JPEG/PNG/WebP/HEIF, `_decompression_bomb_check` chỉ được gọi trong `Image.open` (`PIL/Image.py:3693`, `PIL/WebPImagePlugin.py:77`); `MpoImagePlugin.py:165` nằm trong `seek` (module không gọi); `Image._crop` (`PIL/Image.py:1410`) chỉ chạy trên ảnh đã ≤ 80 triệu điểm ảnh nên không thể chạm ngưỡng cảnh báo 89,5 triệu; pillow-heif không gọi hàm này. Có test giữ điều này nếu Pillow đổi (`tests/test_images_process.py:619`). Test `:583`, `:639`, `tests/test_soi_loi_t067.py:332`, `:359`, `:397`, test cũ `tests/test_soi_loi_t049.py:729` nay qua; Soi Lỗi thay khóa giả thì 2 test nhiều luồng hỏng 3/3 lần. Thử T2, T3 của Lá Chắn: khớp. Vẫn giữ "cảnh báo bom thành lỗi" (Lá Chắn T-047 điều kiện 2) |
| **N1** (không bắt buộc) | Làm, không mở lỗ | `process.py:283-286`, `:390-393`, `:315`, `:325`: `GPSMapDatum` chỉ nhận `[A-Za-z0-9 -]{1,16}`, `GPSSatellites` chỉ nhận `[0-9,]{1,64}`, `fullmatch` (không lọt ký tự xuống dòng). Sai dạng thì chỉ bỏ thẻ đó, vị trí vẫn giữ (2 thẻ này không đổi nghĩa thẻ khác). Chặt hơn trước, không nới gì. Giới hạn còn lại: ghi nhận N4 dưới |
| **N4** (không bắt buộc) | Làm, không mở lỗ | `process.py:157`: `memoryview` đo bằng `nbytes`, kiểu khác vẫn `len`. Chỉ chặt hơn (đếm đủ byte). Test `tests/test_images_process.py:489`, `tests/test_soi_loi_t067.py:454`, `:468` |
| Bản gửi AI sạch metadata | Không đổi, vẫn đạt | `make_ai_image`, `_encode_clean_jpeg`, `jpeg_layout` không bị sửa (diff chỉ đụng các dòng trên). `tests/test_ai_images.py` và test A3 của T-049 vẫn qua. Thử T1: bản AI của 10 kiểu GPS × JPEG/PNG/WebP không có `Exif`, `GPS`, số seri |
| `WebImage.notice` | Không lộ gì | Chỉ nhận một trong 3 giá trị: `""`, `_NOTICE_EXIF_UNREADABLE` (`:101-103`), `_NOTICE_GPS_BROKEN` (`:104`), đều là câu cố định do code viết, không ghép đường dẫn, tên file hay dữ liệu ảnh (`:485`, `:495`, `:501`, `:507`, `:804`). `WebImage.data` vẫn `repr=False` (`:728`). Thử T1: mọi `notice` thuộc tập 2 câu trên, không có `/`, `\` |

## Đánh giá SL-T067-1 (= LC-T067-1)

- **Mức Thấp: đồng ý.** Không lộ metadata, không đăng vị trí sai, không đọc ngoài thư mục, không mở được ảnh "bom". Hậu quả chỉ là câu báo sai sự thật (ảnh vốn không có vị trí) và, cùng gốc, mất vị trí của ảnh có thẻ Ref phụ sai. Theo bảng mức ở `security.md` mục 3, đây là "cách viết chưa tốt nhất nhưng chưa khai thác được".
- **Sửa ở đâu: gom vào một lượt dọn nhỏ (phiếu dọn mới hoặc lượt nhỏ trên nhánh riêng), không sửa trong T-067.** Lý do: T-067 đang chặn T-054 (LC-T049-1 phải vào `main` trước T-054), còn lỗi này chỉ có hại khi câu báo hiện lên màn hình (T-056). Sửa ngay trên T-067 thì phải qua lại Soi Lỗi và Lá Chắn, làm T-054 chờ thêm mà không được thêm gì về an toàn. **Mốc: trước khi gộp T-056.** Không chặn gộp T-067, không chặn T-054.
- **Cách sửa Lá Chắn chọn: phương án (b) của Soi Lỗi** (Ghi nhận 1 trong báo cáo Soi Lỗi):
  1. `GPSLatitudeRef`, `GPSLongitudeRef` có trong ảnh gốc mà sai khuôn → giữ như nay: bỏ cả khối GPS, `notice = _NOTICE_GPS_BROKEN`.
  2. Ref **phụ** có trong ảnh gốc mà sai khuôn → bỏ **cả cặp** Ref và giá trị đi kèm (độ cao, tốc độ, hướng đi, hướng ảnh, vĩ độ đích, kinh độ đích, góc đích, khoảng cách đích), giữ phần còn lại, **không báo**. Không đăng giá trị nào có thể sai nghĩa, mà vẫn giữ vị trí cho SEO địa phương (2A).
  3. Sau bước 2, ảnh không có tọa độ thì đi nhánh `:502-507` như T-049 (chỉ báo khi ảnh gốc có thẻ tọa độ). SL-T067-1 hết theo.
  4. **Không** thêm 2, 3 vào tập hợp lệ của `GPSAltitudeRef`: Lá Chắn chưa đối chiếu tài liệu CIPA của Exif 3.0, và trình đọc chỉ biết Exif 2.x có thể hiểu 3 thành "trên mặt biển" (đổi dấu độ cao). Với (b), ảnh ghi 2, 3 chỉ mất độ cao, giữ vị trí.
  5. **Test:** ca Ref vĩ độ, kinh độ giữ nguyên kỳ vọng. Các ca Ref **phụ** trong `tests/test_images_process.py:947` (`GPSAltitudeRef` = `\x02`, kiểu SHORT, `GPSSpeedRef = "k"`, `GPSDestLatitudeRef = "s"`) và trong `tests/test_soi_loi_t067.py:122`, `:130`, `:163` (các ca Ref phụ, Ref độ cao sai kiểu) **đổi kỳ vọng** thành: vị trí giữ đúng từng giá trị, file ra không còn cả Ref lẫn giá trị đi kèm, `notice == ""`. Đây là đổi điều kiện theo quyết định bảo mật ghi trong biên bản này, không phải "sửa test cho qua" (R5); người sửa ghi rõ trong báo cáo, Soi Lỗi soát lại. Thêm test: `GPSAltitudeRef` = 3 thì file ra không còn `GPSAltitude`. Gỡ 4 `xfail` SL-T067-1 khi XPASS.
- **Phương án tối thiểu (cũng đạt về bảo mật)** nếu Chỉ Huy muốn ít đổi test: giữ (a) "bỏ cả khối", chỉ chuyển điều kiện báo sang "ảnh gốc có thẻ tọa độ" (gộp với `had_location` ở `:506`). SL-T067-1 hết, nhưng ảnh có Ref phụ sai vẫn mất vị trí.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets (`PYTHONUTF8=1`) trên patch diff và patch lịch sử nhánh: 0; trên 6 file của diff: 0; mồi trong file có tiếng Việt bắt đủ. grep `security.md` mục 5 trên `git log -p origin/main..team/T-067`: 0 dòng. Không file nhị phân, không ảnh nào được commit (`git diff --numstat`: 6 file chữ) |
| S2 | Đạt | Module không ghi log. Câu báo mới là câu cố định (`process.py:104`), không đường dẫn hay câu lỗi gốc; lỗi mở ảnh vẫn `from None` (`:230`, `:232`, `:235`). `WebImage.data` `repr=False` (`:728`) |
| S3 | Không áp dụng | Không có biến `.env` mới; khóa và mẫu chữ mới là hằng số trong code (`:85`, `:283-286`, `:340-351`) |
| W1 | Không áp dụng | Không gọi WordPress (`process.py` không nhập module `wordpress`); tải ảnh lên là T-054 |
| W2 | Không áp dụng | Không đụng dữ liệu trên site |
| W3 | Không áp dụng | Không dựng HTML |
| W4 | Không áp dụng | Không gọi mạng |
| A1 | Không áp dụng | Không dựng prompt |
| A2 | Không áp dụng | Không gọi AI |
| A3 | Đạt | Đường bản gửi AI không bị sửa (`make_ai_image`, `_encode_clean_jpeg`, `jpeg_layout`); `tests/test_ai_images.py` qua; thử T1: bản AI không còn `Exif`, `GPS`, số seri ở JPEG, PNG, WebP |
| U1 | Không áp dụng | Không sửa `app/`, không có `unsafe_allow_html` |
| U2 | Không áp dụng | Không thêm trang; `.streamlit/config.toml:5` vẫn `address = "localhost"` (không đổi) |
| U3 | Không áp dụng | Không đụng đăng nhập |
| F1 | Đạt | Không đổi cách đọc ghi file: module chỉ nhận byte; `PreviewCache.get` vẫn đọc qua `ImageLibrary.stat_image`/`read_image_bytes` (`:945`, `:951`), nay còn kiểm Pillow trước khi đụng thư mục ảnh (`:944`). Cache vẫn ở `data/image_previews`, tên là mã băm |
| F2 | Đạt | **Giới hạn:** không nới: 40 MB (nay đo đúng byte với `memoryview`, `:157`), 80 triệu điểm ảnh kiểm sau `Image.open` (`:216-218`), WebP kiểm trước `Image.open` (`:209-211`), cảnh báo bom vẫn thành lỗi trong khóa (`:198-200`; thử T2). **GPS (sổ rủi ro mục 6, 2A):** ảnh đúng khuôn giữ GPS đúng từng giá trị, so sau nén không đổi (`:740-766`); ảnh Ref sai khuôn không còn lên web với vị trí có thể sai bán cầu (`:496-501`). Ngoại lệ: LC-T067-1 (Thấp, chỉ mất vị trí hoặc báo nhầm, hướng an toàn) |
| F3 | Đạt | Không `eval`, `exec`, `pickle`, `yaml.load` (bandit 0). Vẫn bắt đủ lỗi quanh cả `open` lẫn `load` trong cùng khối `try` (`:213-236`); `formats` cố định; HEIF đăng ký trước khi lấy khóa (`:212`). Đa luồng: khóa luôn nhả, bộ lọc trả đúng (`tests/test_images_process.py:639`, `tests/test_soi_loi_t067.py:397`; thử T2, T3). Ghi nhận N1, N2 |
| D1 | Đạt | Không thư viện mới; `uv.lock`, `pyproject.toml` không đổi so với `main`. Chỉ thêm `threading` (thư viện chuẩn). pip-audit: 0 lỗ hổng (69 gói ghim, `pillow==13.0.0`, `pillow-heif==1.8.1`) |
| D2 | Đạt | `.gitignore` không đổi: `.env` (dòng 2), `*service-account*.json` (5), `data/` (22, phủ cache xem trước), `*.sqlite` (23) |
| D3 | Đạt | `tests/conftest.py` chặn mạng cho mọi test; test mới tạo ảnh giả bằng Pillow trong bộ nhớ hoặc `tmp_path`, không tải gì; luồng nền có hạn chờ (`join(cho)`), không treo. Lượt 650 test không có lỗi mạng |

## Kết quả công cụ quét

Chạy trên máy Windows của chủ dự án, trong worktree `wt-T-067`, tại `46f1bf7`, ngày 2026-10-20 16:54–17:05.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit 2.10.1 | `uv export --frozen --no-hashes --no-emit-project` → 69 gói ghim; `pip-audit -r … --no-deps --disable-pip`: **No known vulnerabilities found** | Có. `uv.lock`, `pyproject.toml` không đổi (`git diff --quiet` đúng), nên kết quả như `main`. Lưu ý LC-T058-4 vẫn còn (cơ sở dữ liệu có thể chưa có khuyến cáo Pillow mới nhất) |
| bandit 1.9.4 | `process.py`: **No issues identified** (759 dòng). Toàn bộ `seo_app app scripts`: 9.669 dòng, 1 mục Thấp B101 (`seo_app/storage/drafts.py:203`, có từ trước). File test của phiếu (bỏ B101): B404/B603 (`tests/test_images_process.py:14`, `:1270`), B311 (`tests/test_images_process.py:855`, `tests/test_soi_loi_t049.py:605`) | Có. Đều có từ T-049 (chỉ dời số dòng), là báo nhầm (mục dưới) |
| detect-secrets 1.5.0 | **Đặt `PYTHONUTF8=1`** (`security.md` mục 5). Patch diff (`git diff origin/main...team/T-067`, 75 KB) + patch lịch sử nhánh (`git log -p origin/main..team/T-067`, 9 commit, 83 KB): **0**. 6 file của diff: **0**. Mồi: bản sao patch lịch sử (có tiếng Việt) thêm khóa AWS giả và `password = "…"` → bắt **đủ 2 mồi** | Có. Cùng file mồi **không** đặt `PYTHONUTF8=1`: 0 mục (bỏ qua lặng lẽ, đúng LC-T049-4). Chuỗi mồi chỉ nằm trong bản sao ở thư mục tạm của phiên, không vào repo |
| Soát lịch sử git | `git log -p origin/main..team/T-067 \| grep -inE "api[_-]?key\|password\|secret\|token"`: **0 dòng**. 9 commit riêng (`496d518` → `46f1bf7`), chỉ đụng 6 file của diff | Có |
| pytest (test liên quan) | `uv run pytest tests/test_images_process.py tests/test_soi_loi_t049.py tests/test_soi_loi_t067.py tests/test_ai_images.py -q -rsxX`: **646 passed, 4 xfailed in 142.31s**, mã thoát 0 | Có. 4 xfail đúng là SL-T067-1 (`strict=True`), 0 XPASS, 0 bỏ qua. Toàn bộ pytest do Chỉ Huy chạy khi gộp |
| ruff | `uv run ruff check .`: **All checks passed!** | Có |
| Thử gộp | `git merge-tree --write-tree origin/main team/T-067` với `main` `af7ac41` (sau `git fetch`): **sạch**, cây `b16e6bf`, mã thoát 0 | Có |

## Thử độc lập của Lá Chắn

Script trong thư mục tạm của phiên (không commit), ảnh giả 64 × 48 tạo bằng Pillow (hãng, đời máy, số seri giả, GPS giả ở 10°46' B, 106°41' Đ), không mạng, gọi thẳng `seo_app.images.process` của nhánh, chạy `python -I`.

**T1 · GPS (LC-T049-1, LC-T067-1, N1), kết quả với JPEG** (bản AI kiểm cả JPEG, PNG, WebP)

| Ảnh gốc | `web.gps` | `notice` | Thẻ GPS trong file ra |
|---|---|---|---|
| Ref `s`, `w` (sai) | None | GPS hỏng | 0 |
| Ref `S`, `W` (đúng, Nam/Tây) | (−10,7762667; −106,6867611) | rỗng | 5 |
| `GPSAltitudeRef` `\x01` + độ cao (đúng) | giữ | rỗng | 7 |
| `GPSAltitudeRef` `\x03` | None | GPS hỏng | 0 (LC-T067-1: mất vị trí) |
| `GPSSpeedRef` `k` (Ref phụ sai) | None | GPS hỏng | 0 (LC-T067-1: mất vị trí) |
| Thiếu hẳn `GPSLatitudeRef` | giữ, hiểu là Bắc | rỗng | 4 (ghi nhận N3) |
| Không tọa độ, `GPSSpeedRef` `k` | None | **GPS hỏng** | 0 (**LC-T067-1 tái hiện**) |
| Không tọa độ, chỉ `GPSVersionID` | None | rỗng | 0 |
| `GPSMapDatum` `Nguyen Van An` | giữ | rỗng | 6 (thẻ còn, ghi nhận N4) |
| `GPSMapDatum` `12 Le Loi, Q1` | giữ | rỗng | 5 (thẻ bị bỏ) |

Bản AI của cả 30 trường hợp (10 kiểu × 3 định dạng) không có `Exif`, `GPS`, số seri; ảnh web không có số seri; `notice` chỉ là rỗng hoặc câu cố định.

**T2 · Khóa (LC-T049-3).** File rác, PNG cụt, JPEG cụt: câu lỗi cố định, sau mỗi lần khóa không bị giữ, `warnings.filters` bằng trước. Hạ giới hạn Pillow để ảnh 3.072 điểm ảnh rơi vào **vùng cảnh báo** (giới hạn 2.000) và **vùng lỗi** (giới hạn 1.000): cả hai báo "Ảnh có quá nhiều điểm ảnh…", khóa nhả, bộ lọc bằng trước.

**T3 · Nhiều luồng.** 6 luồng × 20 lượt `make_web_image`, xen kẽ JPEG Nam/Tây đúng khuôn, PNG Ref sai khuôn, WebP Bắc/Đông: 0 lỗi, mỗi ảnh ra đúng kết quả của nó (Nam/Tây âm, sai khuôn bỏ và báo, Bắc/Đông dương), không luồng nào treo, khóa nhả, bộ lọc bằng trước.

## Báo nhầm đã loại

- **bandit B404/B603** (`tests/test_images_process.py:14`, `:1270`): test gọi `git check-ignore` bằng danh sách tham số cố định, không qua shell, có timeout, không có dữ liệu ngoài (như biên bản T-049).
- **bandit B311** (`tests/test_images_process.py:855`, `tests/test_soi_loi_t049.py:605`): `random` có hạt giống cố định để sinh file hỏng trong test thử ngẫu nhiên, không dùng cho mật mã.
- **bandit B101** (`seo_app/storage/drafts.py:203`): code cũ, ngoài phạm vi.

## Ghi nhận (không lập lỗi)

- **N1 · Khe còn lại của LC-T049-3** (Rủi ro 1 Thợ Máy, Ghi nhận 4 Soi Lỗi). Khóa chỉ xếp hàng code của app; Streamlit (`dataframe_util.py:753`, `data_editor.py:461`) và pandas cũng dùng `warnings.catch_warnings()` trong luồng của phiên. Trùng đúng lúc thì: (a) bộ lọc "cảnh báo bom thành lỗi" bị để lại cho cả app → chỉ chặt hơn; `st.image` theo điều kiện 3 của T-049 chỉ nhận ảnh xem trước nhỏ nên không bị ảnh hưởng; (b) bộ lọc mất trong chốc lát → **không mở lỗ**, vì phép so 80 triệu điểm ảnh của app (`:216-218`) luôn quyết định trước ngưỡng cảnh báo 89,5 triệu của Pillow, WebP được so trước khi mở, và trên 179 triệu Pillow luôn báo lỗi bất kể bộ lọc. **Quyết định: giữ khóa như phiếu**, không chuyển sang bộ lọc vĩnh viễn: cách đó cũng không đóng hẳn khe (thư viện khác vẫn có thể tạm `simplefilter("ignore")` trong `catch_warnings`) và đổi hành vi Pillow của cả app. Đóng hẳn khi dự án lên Python 3.14 (cảnh báo theo ngữ cảnh).
- **N2 · Khóa giữ trong lúc `Image.open`.** Nếu có file làm Pillow treo ngay ở bước mở thì mọi phiên khác cũng phải chờ (trước T-067 chỉ phiên đó treo). Chưa có đường đi: không biết lỗi treo nào của Pillow 13 / pillow-heif 1.8.1 ở bước mở; Thợ Máy và Soi Lỗi T-049 đã thử ngẫu nhiên 16.800 lượt không treo; file tối đa 40 MB; app chạy cục bộ một người dùng, tắt mở lại là hết. Không cần sửa.
- **N3 · Thẻ Ref thiếu hẳn, hoặc ghi kiểu TIFF lạ mà Pillow bỏ lúc đọc** (Rủi ro 4 Thợ Máy, Ghi nhận 2 Soi Lỗi). Có tọa độ mà không có Ref thì hiểu là Bắc/Đông, không báo (thử T1). File ra có cùng nghĩa với file gốc khi đọc bằng Pillow (mọi trình đọc mặc định Bắc/Đông khi thiếu Ref), không chi tiết hơn tọa độ vốn được công khai có chủ đích; ảnh chụp ở Việt Nam luôn là Bắc/Đông. Muốn nhận ra kiểu TIFF lạ phải tự đọc khối IFD thô, không đáng so với rủi ro. **Không bắt buộc sửa.** Gợi ý cho T-056 (không bắt buộc): hiện tọa độ `web.gps` để chủ dự án liếc qua trước khi chèn ảnh.
- **N4 · Giới hạn của mẫu `GPSMapDatum`** (Ghi nhận 3 Soi Lỗi). Mẫu `[A-Za-z0-9 -]{1,16}` vẫn chở được 16 ký tự kiểu `Nguyen Van An`, `0903 123 456` (thử T1). Thẻ này chỉ có khi phần mềm ghi nó; máy thật ghi `WGS-84`, `WGS 84`, `TOKYO`. Rủi ro thêm so với chính tọa độ (vốn công khai có chủ đích) không đáng kể, như đánh giá N1 ở T-049. Chấp nhận; nếu sau này muốn chặt hơn thì dùng danh sách tên hệ tọa độ đã biết.
- **N5 · `memoryview` đã `release()`** ném `ValueError` thô (Soi Lỗi đã thử), có từ trước T-067. Không có đường đi: `read_image_bytes` trả `bytes`. T-053 truyền `bytes` giải từ base64 cho ảnh AI là đủ.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

Không chặn gộp T-067. Sau khi gộp: điều kiện 1 của biên bản T-049 xong; T-054 không còn bị chặn bởi LC-T049-1; LC-T049-2, -3 (điều kiện của T-056) đã xong.

| # | Việc | Phiếu nhận | Mốc |
|---|---|---|---|
| 1 | Sửa LC-T067-1 theo phương án (b) ở mục "Đánh giá SL-T067-1" (Ref vĩ độ, kinh độ sai → bỏ cả khối và báo; Ref phụ sai → bỏ cả cặp, giữ vị trí, không báo; không nhận `GPSAltitudeRef` 2, 3); đổi kỳ vọng các ca Ref phụ trong test của Thợ Máy và Soi Lỗi như đã ghi, thêm test `GPSAltitudeRef` = 3; gỡ 4 `xfail` SL-T067-1 khi XPASS. Hoặc phương án tối thiểu nếu Chỉ Huy chọn | **Phiếu dọn nhỏ mới** cho `process.py` (Thợ Máy; Soi Lỗi rút gọn; Lá Chắn soát diff) | Trước khi gộp **T-056** |
| 2 | T-056 hiện `WebImage.notice` khi có (điều kiện 3 của T-049, nay câu báo còn gặp ở ảnh GPS ghi sai chuẩn) | **T-056** | Khi làm T-056 |
| 3 | Khi thử 3–5 ảnh thật trên máy (điều kiện 7 của T-049): xem có ảnh nào bị báo "GPS hỏng" bất ngờ hay mất vị trí không; **không commit ảnh** | **Chỉ Huy** | Trước khi gộp T-054 |
| 4 | Kiểm lại phiếu này bằng Fable | **Lá Chắn** | Sau 01/11 |

_Hết biên bản. Lá Chắn T-067 · 2026-10-20._

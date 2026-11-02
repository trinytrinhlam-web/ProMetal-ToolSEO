# Biên bản bảo mật T-116 · nhóm 1: đọc ảnh từ thư mục, xử lý ảnh, HEIC (kiểm lại bằng Fable)

> Kiểm lại độc lập các biên bản Lá Chắn chạy tạm bằng Opus 5.5 từ 15/10 (T-048, T-049, T-052, T-055, T-066, T-067, T-070, T-074, T-076, T-077, T-079, T-080, T-082, T-093 phần ảnh, T-107, T-078 mục AVIF). Quy trình và mức độ lỗi: `docs/team/security.md`.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **chạy Fable 5.1** |
| Ghi chú model | Lượt 07:41–08:05 ngày 02/11 phiên này báo Opus (Chỉ Huy B dừng, kết quả nửa chừng bỏ). Từ 08:05 chủ dự án tự chuyển phiên sang Fable trong menu model của ứng dụng; lời nhắc hệ thống của lượt này báo «Fable 5.1». **Mọi kết luận dưới đây do lượt Fable này đưa ra**; chỉ dùng lại phần đọc mã còn trong ngữ cảnh. |
| Phiếu được kiểm | [T-116](../tickets/T-116-la-chan-fable-kiem-lai.md) (phiếu chưa commit; Chỉ Huy giữ) |
| Phạm vi | `main` `731a46e`: `seo_app/images/**` (folders, process, tags, alt, html, naming), `seo_app/storage/image_tags.py`, lớp kiểm ảnh gửi AI `seo_app/ai/base.py` (`prepare_images`, `_check_jpeg/_png/_webp`), nơi gọi `app/views/write.py` (phần ảnh), `app/views/settings.py` (tab Ảnh), `seo_app/storage/drafts.py` (`check_chosen_image`) |
| Ngày | 2026-11-02 |
| Máy | Windows 11, Python 3.12.15, uv 0.13.4 (đạt ngưỡng chạy `uvx`), Pillow 13.0.0, pillow-heif 1.8.1 (libheif 1.23.6, bản còn lỗi → công tắc `HEIC_ENABLED = False`) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** (0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp mới** LC-T116-1) |

## Tóm tắt (cho chủ dự án)

Phần đọc ảnh từ thư mục, xử lý ảnh và HEIC **an toàn** như các biên bản Opus đã kết luận: tôi tự thử lại từ đầu (không chỉ đọc biên bản cũ) và không cách nào làm app đọc file ngoài thư mục ảnh (qua `..`, junction, tên ngắn 8.3), không lối nào tới thư viện HEIC đang tắt (kể cả file HEIC đổi đuôi `.png`), ảnh dựng cố ý cỡ khổng lồ bị chặn trước khi cấp bộ nhớ, bản ảnh gửi AI sạch hoàn toàn metadata còn bản đăng web giữ đúng GPS như chủ dự án muốn. Câu báo lỗi không lộ đường dẫn máy.

Tìm thêm **một lỗi nhỏ (Thấp)**: nếu ai đó ghi được vào thư mục cài app và đặt thư mục `data/` thành một liên kết tắt (junction) trỏ đi nơi khác, app sẽ ghi cache ảnh xem trước và file thẻ ảnh sửa tay vào nơi đó mà không biết. Muốn làm được phải có quyền ghi trên máy bạn từ trước (cùng loại với vài dòng đã ghi trong sổ rủi ro), nên không nguy hiểm ngay; đề xuất một phiếu dọn nhỏ hoặc ghi sổ rủi ro.

Không có phát hiện nào của Opus bị xếp là **sai**; một ghi nhận của T-049 (N2) được **nâng mức** thành lỗi Thấp nói trên.

## Lỗi phát hiện (mới)

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T116-1 | **Thấp** | Liên kết (junction/symlink) ở **tầng thư mục** `data/` (hay `data/image_previews`) không được kiểm trước khi app ghi file. `_cache_dir_is_ignored` `resolve` thư mục cache: trỏ ra ngoài gốc dự án thì trả `True` («git không thấy») nên cache **bật**; `ImageTagStore._remove_links` chỉ gỡ liên kết ở đúng tên file `.sqlite` và file nhật ký, không kiểm thư mục cha. Opus T-049 ghi nhận N2 coi "cache ngoài dự án là an toàn" — đúng với git, nhưng trái F1 khi "ngoài dự án" là do bị tráo bằng liên kết | `seo_app/images/process.py:984-985` (`_cache_dir_is_ignored`), `:1043-1048` (`_write` mkdir + ghi); `seo_app/storage/image_tags.py:444-448` (`_prepare` mkdir), `:479-486`, `:512-521` (`_remove_links`, `_is_link` chỉ xét file) | Kẻ có quyền ghi vào thư mục cài app đặt `data` → junction tới thư mục ngoài (test: `tests/test_la_chan_t116_nhom1.py`, 2 ca XFAIL). Người dùng mở khung chọn ảnh → `PreviewCache.get` ghi `<băm>.jpg` (JPEG 320 px, không metadata) vào thư mục đó; bấm «Đây là ảnh AI» → `image_tags.sqlite` được tạo và ghi ở đó. Ngược lại, `_read` tin file trong cache (chỉ kiểm khuôn JPEG sạch): ảnh xem trước ở lưới chọn có thể bị thay (khung ảnh đã chọn và byte tải lên vẫn dựng từ file thật, `write.py:1183-1198`). Hậu quả: ghi/đọc dữ liệu phụ qua nơi kẻ đặt liên kết chọn; không lộ ảnh gốc, không ảnh hưởng ảnh gửi web | Một hàm dùng chung (ví dụ `seo_app/storage/_links.py`): `lstat` từng tầng từ `PROJECT_ROOT` xuống `data/…`, từ chối symlink/junction (như `_is_link_stat` của `folders.py`); `PreviewCache.__init__` đặt `enabled = False` và `ImageTagStore._prepare` báo `ImageTagStoreError` khi gặp liên kết; hoặc đòi `(PROJECT_ROOT / "data").resolve(strict=True) == PROJECT_ROOT.resolve() / "data"` đúng từng chữ. Gỡ 2 `xfail` khi XPASS |

## Đối chiếu từng phát hiện của biên bản Opus cũ

Kết luận Fable: **giữ** (đúng mức, trạng thái đúng), **đổi mức**, hoặc **sai**. Bằng chứng theo mã tại `731a46e`.

| Biên bản | Mã | Mức Opus | Kết luận Fable | Bằng chứng / ghi chú |
|---|---|---|---|---|
| T-048 | LC-T048-1 | Trung bình | giữ | Nhánh Mac/Linux đã chạy thật trên Linux (T-063, T-079, T-080-linux); **Mac vẫn chờ** (chủ dự án chưa có Mac, không chạy cloud). Lượt này không chạy lại Linux |
| T-048 | LC-T048-2, -3 | Thấp | giữ | Còn mở (T-064 hoãn). Nay `_scan_held` (`folders.py:1192-1212`) giữ handle không chia sẻ xóa, kiểm `_win_handle_is_link` + `_same_win_path` trước và sau khi đọc; nhánh dự phòng (`:1205-1212`) so định danh trước/sau. Lọt tối đa tên/cỡ, không bao giờ nội dung (đọc đi `_open_image`). Thấp là đúng |
| T-048 | LC-T048-4 | Thấp | giữ | (a) `tags.py:397` bỏ Cf/Cs/Co/Cn/Zl/Zp; (b) `write.py:954-964`, `settings.py:455-460` hiện «�» + cô lập hướng chữ; (c) `_is_safe_name` `folders.py:128-143` vẫn cho Cf (U+200B…) đi qua — còn mở T-064, chỉ ảnh hưởng hiển thị |
| T-048 | LC-T048-5 | Thấp | giữ | Không phải bảo mật |
| T-048 | LC-T048-6 | Thấp | giữ | Sổ rủi ro 20/10; `_same_file` `folders.py:219-223` vẫn coi `st_ino = 0` là "cùng file" |
| T-049 | LC-T049-1, -2, -3 | Thấp | giữ (đã đóng T-067) | `process.py:615-620` Ref sai → bỏ cả khối GPS + báo; `:1063` `_require_pillow_13` đầu `PreviewCache.get`; `:109`, `:307` khóa bọc đúng `Image.open` |
| T-049 | LC-T049-4 | Thấp (quy trình) | giữ | `security.md` §5 đã ghi; lượt này gặp lại đúng hiện tượng (probe in tiếng Việt lỗi cp1252 khi thiếu `PYTHONUTF8=1`) |
| T-049 | N2 (cache ngoài dự án coi là an toàn) | ghi nhận | **đổi mức → Thấp** | Thành LC-T116-1 ở trên |
| T-049 | N3 (web giữ nguyên byte hồ sơ màu) | ghi nhận | giữ | `_rgb_icc_profile` `process.py:684-697` chỉ kiểm phần đầu (cỡ, `acsp`, `RGB `, ≤ 1 MB) rồi chép nguyên sang `ICCP`; không phân tích nên không có lỗi bộ nhớ; chữ trong hồ sơ (tên, bản quyền) lên web là có chủ đích (màu Display P3). Bản AI bỏ hồ sơ màu (A3) |
| T-049 | N7 (điểm ảnh vẫn tới AI) | ghi nhận | giữ | Sổ rủi ro 23/10 (ảnh dựng cố ý) |
| T-052 | LC-T052-1 | Trung bình | giữ (đã đóng T-070, T-077) | `tags.py:206-300`, `:867` đọc dấu hiệu AI hai cách tách; `is_ai_name` `:973-986`; `write.py:930-947` kiểm cả tên gốc khai báo lẫn tên sau `resolve` |
| T-052 | LC-T052-2 | Thấp | giữ (đã đóng T-070, T-074) | `_app_tables` `image_tags.py:593-616` so đúng từng dòng `sqlite_master` (danh sách, trùng → `None`), `_guard` `:544-563` (`trusted_schema = OFF`, giới hạn độ dài, 50 triệu bước), `_begin` trước kiểm `:419`, `:462`, `:635` |
| T-052 | LC-T052-3 | Thấp | giữ (đã đóng) | `_keep_ai` áp từng `ref` ở `get_many` `:283-287`, `_row_to_tag` `:408`, `set` `:307-308` |
| T-052 | LC-T052-4 | Thấp | giữ | README; không kiểm bằng mã (như Opus ghi) |
| T-052 | LC-T052-5 | Thấp | giữ | Sổ rủi ro 30/10 (N5); khe `-journal` vẫn còn về nguyên tắc |
| T-055 | LC-T055-1, -2, -3 | Trung bình / Thấp / Thấp | giữ (đã đóng T-076, T-079) | `stat_image` `folders.py:951-975` trả tên trên ổ + `file_id`; `drafts.py:1504-1538` hỏi lại tên cũ, so cỡ/giờ/định danh trước khi nhận tên mới |
| T-055 | LC-T055-4 | Thấp | giữ (đã đóng) | — |
| T-066 | (không lỗi; sổ rủi ro 23/10) | — | giữ | Probe lượt này: `prepare_images` (`base.py:491-538`) chặn ảnh gốc còn EXIF (`IMAGE_METADATA_MESSAGE`), nhận bản `make_ai_image`; danh sách cho phép JPEG/PNG/WebP `:605-787` |
| T-067 | LC-T067-1 | Thấp | giữ | T-072 hoãn. `process.py:615-620`: Ref phụ sai → bỏ cả khối GPS, báo `_NOTICE_GPS_BROKEN`. Hướng an toàn (không đăng tọa độ sai bán cầu), chỉ mất GPS oan |
| T-070 | LC-T070-1, -2 | Thấp | giữ (đã đóng T-074) | `image_tags.py:607-608` đọc danh sách + bắt trùng; giao dịch mở trước kiểm `:419`, `:462`, `:635` |
| T-070 | SL-T070-4 | Thấp | giữ | Sổ rủi ro 30/10 (N5); `xfail` `tests/test_soi_loi_t070.py:481` còn |
| T-074 | LC-T074-1, SL-T074-1 | Thấp | giữ (đã đóng T-077) | `tags.py:246-249`, `:867`; `get_many` `:269-277` chỉ `SELECT` trong giao dịch |
| T-076 | LC-T076-1, -2, -3 | Trung bình / Thấp / Thấp | giữ (đã đóng T-076 lượt 2, T-079) | `_found_names` `folders.py:784-795` hỏi `FindFirstFileW` từng tầng (`_win_listed_name` `:380-398`); `drafts.py:1527-1538` so `file_id` |
| T-077 | (không lỗi) | — | giữ | — |
| T-079 | LC-T079-1 | Thấp (T-080 xét lại: lẽ ra Cao trên `main` cũ) | giữ (đã đóng T-080; xét lại Cao đúng) | `_same_win_path` `folders.py:401-419` so **từng chữ** (không gộp hoa thường, NFC/NFD, Kelvin), dùng ở `_opened_stat` `:1020`, `_open_image` `:1062`, `_scan_held` `:1199`. `is_relative_to` `:729` vẫn so chữ thường nhưng chỉ để so chuỗi (docstring `:676-691`), không mở/đọc theo đường dẫn `resolve` trả |
| T-079 | LC-T079-2 | Thấp | giữ (đã đóng T-080) | `_checked_file` `:909-934`: kiểm hỏng thì báo theo mục mở lại trong thư mục ảnh, không tả `lstat` theo chuỗi |
| T-079 | LC-T079-3 | Thấp | giữ (đã đóng T-080) | `_changed_while_resolving` `:457-475` |
| T-079 | ghi nhận "thư mục dời vào gốc" | — | giữ | Sổ rủi ro 23/10 |
| T-080 | SL-T080-1, -2, -L-1 | Thấp | giữ (đã đóng T-082) | `:1010-1018` lấy mã lỗi Windows 2/3; `:1219-1222`; `:712-713`, `:743-745` `_still_same_entry` |
| T-082 | (không lỗi; 6 `xfail` Linux treo) | — | giữ | Không chạy lại Linux lượt này (chủ dự án: không cloud) |
| T-093 | LC-T093-3 | Cao | giữ (đã đóng T-107) | `HEIF_DECODE_THREADS = 0` `process.py:83`, đặt lại mỗi lần `:170`; công tắc `folders.py:57`; `_allowed_formats` `process.py:70-72` |
| T-093 | LC-T093-1, LC-T093-2 | Trung bình / Thấp | **ngoài nhóm 1** | `app/views/wordpress.py`, gắn ảnh vào bài (T-106, T-110): kiểm ở nhóm 2 |
| T-093 | N2, N3, N5 | Thấp | giữ | Sổ rủi ro 30/10; libheif vẫn 1.23.6 → công tắc tắt là đúng |
| T-107 | LC-T107-1 | Trung bình | giữ (đã đóng lượt 3) | `_check_heif_alpha` `process.py:224-232` chạy trước `load()` `:335-340` |
| T-107 | LC-T107-2 | Trung bình | giữ (đã đóng bằng công tắc) | Probe lượt này: 4 hàm dựng ảnh × HEIC thật (bộ mã hóa pillow-heif) → đều `_MSG_HEIC_OFF`, **0** lời gọi `_pillow_heif.load_file`, **0** `register_heif_opener`, `"HEIF" not in Image.OPEN`; HEIC đội lốt `.png` trong thư mục ảnh bị từ chối theo nội dung (`_is_heic_container` `:288-297`). Chốt bật lại: `tests/test_la_chan_t107.py::test_lc_t107_2_…` đòi libheif ≥ 1.23.7 |
| T-107 | LC-T107-3 | Thấp (khi tắt) | giữ | `xfail` `tests/test_la_chan_t107.py:233`; chỉ có nghĩa khi bật lại; điều kiện 3 của T-107 lượt 3 |
| T-107 | SL-T107-3 | Thấp | giữ | Không bảo mật |
| T-078 | mục AVIF | không lỗi | giữ | `_BASE_FORMATS` `process.py:67` không AVIF; `IMAGE_EXTENSIONS` `folders.py:62` không `.avif`; `test_avif_still_gets_not_image_message` qua |

**Sai:** không có. **Đổi mức:** 1 (T-049 N2 → LC-T116-1 Thấp).

## Kiểm lại độc lập (lượt Fable): probe trong thư mục tạm, không ghi vào repo

Script nằm ngoài repo (`scratchpad/probe_*.py`), mỗi probe tự dọn. Kết quả:

| Probe | Nội dung thử | Kết quả |
|---|---|---|
| Lớp kiểm dạng chữ (`ImageRef`) | 22 đường dẫn xấu (`..`, tuyệt đối, ổ đĩa, UNC, gạch ngược, `:` dòng dữ liệu NTFS, tên thiết bị, tên ẩn, chấm/cách cuối, phần rỗng, RLO, surrogate lẻ, đuôi lạ, `.heic` khi tắt), 4 tên tốt, 4 `root_index` xấu | 21/22 xấu bị từ chối; 1 ca "lọt" là **tôi phân loại sai** (`a/trailing .jpg`: khoảng trắng giữa tên, kết thúc bằng `g`, là tên hợp lệ không bị Windows cắt); 4/4 tốt nhận; 4/4 `root_index` chặn |
| Hệ thống tệp (Windows) | Junction trong gốc trỏ ra thư mục ngoài có file "bí mật"; junction khi liệt kê; tên ngắn 8.3 `THUMUC~1`; `repr(ImageLibrary)` | Junction → `_MSG_LINK`, **không trả nội dung ngoài**; liệt kê bỏ qua (`skipped.links = 1`); 8.3 → từ chối; câu báo và `repr` **không chứa đường dẫn**. Symlink không tạo được trên máy này (thiếu quyền Developer Mode) → dựa vào junction (lối không cần quyền) và test Linux T-079/T-080 |
| HEIC tắt | HEIC thật 447 byte (tạo bằng bộ mã hóa, tiến trình riêng) qua 4 hàm dựng ảnh ×3; đội lốt `.png` trong thư mục ảnh | Xem LC-T107-2 ở trên: 0 lời gọi libheif |
| EXIF/GPS | JPEG có GPS 10°46′30,12″N 106°41′23,99″E, Make/Model, số seri thân máy | Bản web: `has_gps`, đọc lại WebP đúng tọa độ (10,7750333 / 106,6899972), **không còn số seri**; bản AI: `getexif()` rỗng, không dấu `Exif`; ảnh xem trước sạch; `prepare_images` chặn gốc, nhận bản AI |
| Bom giải nén | WebP VP8L khai 10000×8500 = **85 triệu** (trên ngưỡng app 80 tr, **dưới** ngưỡng Pillow 89,5 tr → chỉ tiền kiểm app bắt); WebP 16384² = 268 tr; PNG IHDR 20000² = 400 tr | Cả ba bị chặn trước khi cấp bộ nhớ: `_webp_canvas_pixels` `process.py:259-280` bắt 85 tr; PNG báo "không phải ảnh đọc được" (Pillow từ chối ở `open`) |
| Liên kết ở tầng `data/` | `data` → junction ra ngoài; `PreviewCache.get`, `ImageTagStore.set` | **Lọt** → LC-T116-1 (2 test XFAIL strict) |

Test chọn lọc hiện có (chạy lại lượt này, máy đang chạy toàn bộ test trên `main` nên chỉ chạy nhóm liên quan): `tests/test_t107_heic_tat.py`, `test_la_chan_t107.py`, `test_images_process.py`, `test_images_folders.py`, `test_la_chan_t079.py`, `test_soi_loi_t080.py`, `test_images_tags.py`, `test_soi_loi_t070.py`, `test_la_chan_t074.py`, `test_la_chan_t093.py` — kết quả ở bảng công cụ.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Không có bí mật trong phạm vi; soát lịch sử git (bảng công cụ) |
| S2 | Đạt | Mọi câu báo là chuỗi cố định tiếng Việt: `folders.py:100-110`, `process.py:111-139`, `image_tags.py:141-146`, `:689-699` (`strerror` không có đường dẫn); giao diện bắt `Exception` → câu cố định `write.py:1097-1098`, `:1158-1159`, `:1194-1195`, `:1332-1333`; `settings.py:481-486` |
| S3 | Không áp dụng | Không có biến cấu hình mới |
| W1–W3 | Không áp dụng | Nhóm 2 |
| W4 | Không áp dụng | Nhóm 1 không gọi mạng |
| A1 | Đạt | Thẻ/từ khóa trong khung `<du_lieu_tham_khao>` `alt.py:295-303`; `DATA_RULE` `:103-108` nằm trong mã, không ở `config/` |
| A2 | Đạt | `suggest_alt` tắt `web_search` `alt.py:589-591`; kết quả AI qua `clean_suggestion` `:511-559` |
| A3 | Đạt | Bản gửi AI dựng lại từ điểm ảnh `process.py:724`, `jpeg_layout` `:778-822`; `prepare_images` `base.py:491-538` + `_has_metadata_marker` `:547-548`; thẻ qua `_short_text` `alt.py:176-189` (danh sách ký tự, `_looks_like_path`); `ImageTags` chỉ giá trị cố định `tags.py:659-676`. Probe EXIF/GPS xác nhận |
| U1 | Đạt | `unsafe_allow_html` trong phần ảnh chỉ với HTML cố định `write.py:1385`, `:1821`; tên file/thư mục qua `shown_name`/`escape_markdown` `:954-973`, `:1823`; `settings.py:455-460` |
| U2 | Đạt | Không in đường dẫn: `ImageLibrary.__repr__` `folders.py:631-633`; `RootInfo.label` chỉ tên cuối `:644`; `settings.py:443-507`; `note_tag_store` chỉ `.name` `write.py:1005`. Probe: câu báo junction/8.3 sạch |
| U3 | Không áp dụng | Nhóm 3 |
| F1 | **Đạt có ghi chú** | Đọc ảnh: `_parse_rel` `folders.py:146-167`, `_resolve_inside` `:675-746`, `_open_image`/`_win_handle_at` `:1029-1065`, `_posix_open_dir` `:422-440`, `_scan_held` `:1192-1212` — probe junction/8.3 giữ. **Ghi chú:** ghi cache/kho thẻ qua liên kết ở tầng `data/` → LC-T116-1 (Thấp) |
| F2 | Đạt | `MAX_IMAGE_BYTES` 40 MB `folders.py:65`, `_check_source_size` `process.py:245-256`; `MAX_IMAGE_PIXELS` 80 tr `:78`, tiền kiểm WebP `:259-280`, so sau `open` trước `load` `:331-333`, `DecompressionBombWarning` → lỗi `:307-308`; chỉ `ALLOWED_FORMATS` `:67-75`; GPS giữ ở web, so từng giá trị sau nén `_verify_web_image` `:859-885`, mất là dừng `:882-883` |
| F3 | Đạt | Không `eval`/`pickle`; SQLite chỉ tham số `?`, `trusted_schema = OFF` `image_tags.py:553`; `.gitignore` đọc `encoding="utf-8"` `process.py:967` |
| D1 | Đạt | Không thư viện mới; `uv.lock` không đổi; pip-audit 69 gói sạch (bảng công cụ); libheif 1.23.6 đã có công tắc tắt và dòng sổ rủi ro, chốt chặn bật lại `test_lc_t107_2_…` |
| D2 | Đạt | `.gitignore` chặn `.env`, `*service-account*.json`, `data/`, `*.sqlite` |
| D3 | Đạt | Probe và test mới không gọi mạng; `conftest` chặn mạng (T-027) |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| `uv --version` | 0.13.4 ≥ 0.13.4 → được phép chạy `uvx` (T-078) | ✔ |
| pip-audit (`uv export` 69 gói ghim → `uvx pip-audit -r … --no-deps --disable-pip`) | **No known vulnerabilities found** (pillow 13.0.0, pillow-heif 1.8.1, certifi 2026.10.19, pyasn1 0.6.5, streamlit 1.65.0). Không thấy khuyến cáo của thư viện C libheif 1.23.6 trong wheel (như T-093 ghi) → vẫn là dòng sổ rủi ro 30/10 + công tắc `HEIC_ENABLED = False` | ✔ |
| bandit 1.9.4 (`PYTHONUTF8=1`, `seo_app/images` + `image_tags.py`, 3.983 dòng) | 1 mục B608 (Medium, độ tin Low) `seo_app/storage/image_tags.py:128` `_oversized_sql`: SQL ghép từ **tên bảng, tên cột hằng** (`_COLUMNS`, `("key", "value")`), giá trị đi qua tham số `?1` — báo nhầm, cùng mục T-074/T-077 đã loại. 0 mục khác | ✔ |
| detect-secrets 1.5.0 (`PYTHONUTF8=1`; `seo_app/images/*`, `image_tags.py`, `write.py`, `settings.py`) | 1 mục «Basic Auth Credentials» `app/views/write.py:2452`: docstring mẫu ``https://tên:mật-khẩu@…`` (chữ chỗ trống minh họa LC-T041-1), không phải khóa — báo nhầm. 6 file còn lại: 0 | ✔ |
| Soát lịch sử git (`git log -p --all` 2 đường dẫn, lọc `api_key\|password\|secret\|token`) | Chỉ khớp tên hàm `_tokens` trong `tags.py` — không có bí mật | ✔ |
| pytest test mới | `tests/test_la_chan_t116_nhom1.py`: **2 xfailed** (strict) — LC-T116-1 thật | ✔ |
| pytest chọn lọc (10 file liệt kê ở mục kiểm lại độc lập) | **1223 passed, 12 skipped, 11 xfailed, 0 failed** (4′28″; 12 bỏ qua là ca Mac/Linux, 11 xfail là lỗi treo đã biết: LC-T107-3, SL-T070-4, 6 ca Linux T-082…) | ✔ |
| ruff | `tests/test_la_chan_t116_nhom1.py`: sạch, đã format | ✔ |

## Báo nhầm đã loại

- bandit B608 `image_tags.py:128`: chuỗi SQL chỉ ghép tên bảng/cột hằng của app, mọi giá trị qua `?` (xem bảng công cụ).
- detect-secrets `write.py:2452`: chữ chỗ trống ``https://tên:mật-khẩu@…`` trong docstring, không có giá trị thật.
- `uvx pip-audit -r req.txt` (kể cả `--no-deps`) hỏng vì pip cố giải xung đột `pillow<13` của Streamlit với `pillow==13.0.0` ép có chủ đích (T-058): lỗi công cụ, không phải lỗ hổng; chạy được với `--no-deps --disable-pip` (tra khuyến cáo thẳng theo phiên bản ghim).
- Probe dạng chữ: `a/trailing .jpg` — tôi liệt kê nhầm vào nhóm xấu; app nhận đúng (tên hợp lệ, không bị Windows cắt vì không kết thúc bằng `.`/khoảng trắng).
- Symlink file/thư mục không tạo được trên máy này (OSError, thiếu quyền) — không phải lỗi app; lớp chặn symlink có `_is_link_stat` `folders.py:202-209` và test Linux T-079/T-080.

## Chưa làm được trong lượt này

- Không chạy nhánh Mac/Linux (chủ dự án chưa có Mac; không chạy cloud): LC-T048-1 phần Mac và 6 `xfail` Linux của T-082 vẫn treo như cũ. Kết luận cho Mac/Linux dựa trên đọc mã (`_posix_open_dir`, `_scan_by_fd`, `_opened_stat`/`_open_image` nhánh `dir_fd`) và các lượt Linux đã chạy (T-063, T-079, T-080).
- Không thử ổ mạng/Google Drive thật lượt này (T-080 đã thử).

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

1. **LC-T116-1 (Thấp):** mở một phiếu dọn nhỏ (sửa cả `PreviewCache` và `ImageTagStore` bằng một hàm kiểm liên kết từng tầng dưới `PROJECT_ROOT`) trước khi đóng Giai đoạn 3, **hoặc** chủ dự án ghi sổ rủi ro mục 6 (cùng lớp "phải chiếm máy trước" như LC-T048-6, T-079). Gỡ 2 `xfail` trong `tests/test_la_chan_t116_nhom1.py` khi XPASS.
2. Giữ nguyên các điều kiện cũ còn mở: Mac chạy test thật trước khi dùng app trên Mac; **chỉ bật lại HEIC** khi đủ 8 điều kiện của T-107 lượt 3 (LC-T107-3 sửa trước, libheif ≥ 1.23.7, Lá Chắn quét D1).
3. LC-T093-1, LC-T093-2 (đường WordPress) kiểm ở nhóm 2.

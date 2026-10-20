# Báo cáo T-049 · Xử lý ảnh: xoay, thu nhỏ, WebP giữ GPS, bản gửi AI sạch, tên file (G3-3)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-049](../tickets/T-049-xu-ly-anh-webp-giu-gps.md) |
| Ngày nộp | 2026-10-20 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- App đã có phần xử lý ảnh thật: ảnh được xoay đúng chiều, thu cạnh dài về 1600 px, nén WebP chất lượng 80, và **giữ nguyên vị trí GPS**. Sau khi nén, app mở lại file và so từng con số GPS với ảnh gốc; lệch một chữ số là dừng, không bao giờ trả ảnh mất GPS.
- Thông tin máy trong ảnh theo đúng lựa chọn 2A: giữ ngày chụp, hãng, đời máy; bỏ số seri máy và ống kính, tên chủ máy, khối dữ liệu riêng của hãng, ảnh nhỏ nhúng bên trong.
- Bản gửi AI viết alt (1024 px, JPEG) được vẽ lại từ điểm ảnh, không còn chút thông tin kèm theo nào (không GPS, không chú thích, không hồ sơ màu). Đã thử: qua được bộ kiểm "danh sách cho phép" của T-050.
- Ảnh HEIC của iPhone, ảnh chụp màn hình không có EXIF, ảnh hỏng, ảnh quá lớn đều được xử lý hoặc báo lỗi tiếng Việt rõ ràng. Tên file ảnh không dấu theo hạng mục, khu vực, mã công trình (ví dụ `cong-inox-tan-phu-ct012.webp`), không lấy tên thư mục.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/images/process.py` | Mới: mở ảnh an toàn, `make_web_image` (WebP giữ GPS), `make_ai_image` (bản gửi AI sạch), `make_preview` + `PreviewCache` (ảnh xem trước, cache trong `data/`), `jpeg_layout`/`webp_chunks` (kiểm khối của file ra) |
| `seo_app/images/naming.py` | Mới: `image_file_name` (tên file không dấu theo thẻ hoặc alt, tối đa 60 ký tự, tránh trùng, tiền tố ảnh AI) |
| `tests/test_images_process.py` | Mới: 61 hàm test, 107 trường hợp (ảnh giả tạo trong bộ nhớ/thư mục tạm, không mạng) |
| `docs/team/reports/T-049-tho-may.md` | Báo cáo này |

Không sửa `seo_app/images/__init__.py`, `folders.py`, `app/**`, `config/**`, `seo_app/ai/**`, test của phiếu khác, không thêm thư viện (`git diff --stat c1b21dc..HEAD` chỉ có 4 file trên).

Commit trên `team/T-049`: `a293a1c` (naming), `9aa6596` (process lõi), `98096e7` (test + chặn WebP khai khung lớn), `d015789` (chỉnh nhỏ), và commit báo cáo này.

## Bằng chứng

```
$ uv run pytest tests/test_images_process.py -q            (tại d015789)
107 passed in 21.94s

$ uv run pytest tests/test_images_process.py tests/test_pillow_heif_setup.py tests/test_soi_loi_t047.py \
    tests/test_soi_loi_t058.py tests/test_pillow_version_t058.py tests/test_images_folders.py -q -rs
331 passed, 6 skipped in 65.46s
(6 skip đều của test_images_folders.py: symlink/Mac-Linux, có từ trước. Test "chưa đăng ký" HEIF
 của T-047 KHÔNG bị bỏ qua: test của phiếu này trả nguyên bảng định dạng Pillow sau mỗi test.)

$ uv run pytest                                             (toàn bộ, Windows)
<<PYTEST_FULL>>

$ uv run ruff check .
All checks passed!
```

**Bản gửi AI qua bộ kiểm của T-050** (code `seo_app/ai/` lấy từ `origin/team/T-050` `2327c75` bằng `git archive` vào thư mục tạm, không đụng worktree `wt-T-050`): ảnh nhiễu 1600×1200 lưu dưới dạng JPEG (có EXIF + GPS + ICC + COM + XMP), PNG RGBA (EXIF + ICC), WebP (EXIF + ICC + XMP), PNG xám 16 bit, HEIC (EXIF + GPS) → `make_ai_image` và `make_preview` → `prepare_images([ImageInput(data, "image/jpeg")])`: **10/10 QUA** (bản AI ~374 KB với ảnh nhiễu, trường hợp nặng nhất; giới hạn T-050 là 5 MB).

**EXIF hỏng ngẫu nhiên** (thử ngoài test, 3 × 3.000 file JPEG có EXIF bị sửa 1–8 byte hoặc cắt cụt): 9.000/9.000 xử lý xong, 0 lỗi thô lọt ra. Lần đầu có 114/3.000 ca báo "Không nén được" vì hãng/đời máy có ký tự ngoài ASCII (Pillow ghi thành `?`, lớp kiểm sau nén bắt lệch) → đã sửa: chỉ giữ chữ ASCII in được, ký tự lạ thì bỏ thẻ đó. Trong test có bản thu nhỏ (150 ca, hạt giống cố định): `test_exif_hong_ngau_nhien_khong_lam_sap`.

## Cách làm chính

| Bước | Làm gì | Ở đâu |
|---|---|---|
| Mở ảnh | Kiểm Pillow ≥ 13 → kiểm dung lượng (≤ 40 MB, lấy từ `folders.MAX_IMAGE_BYTES`) → (WebP) đọc kích thước khung từ phần đầu file → đăng ký HEIF → `Image.open(..., formats=["JPEG","PNG","WEBP","HEIF"])` trong khối đổi `DecompressionBombWarning` thành lỗi → so `rộng × cao` với `MAX_IMAGE_PIXELS` (80 triệu) → (JPEG) `draft` → `load()` | `process.py:184-219` |
| Đọc EXIF | `getexif()` trong khối bắt lỗi; hỏng thì coi như không có EXIF và báo người dùng | `:363-371` |
| Lọc EXIF (2A) | **Danh sách cho phép**: IFD0 `Make`, `Model`, `DateTime`; Exif IFD `DateTimeOriginal`, `DateTimeDigitized`, `OffsetTime*`; GPS: 30 thẻ chuẩn, mỗi thẻ kiểm đúng kiểu. Mọi thẻ khác bị bỏ | `:270-318`, `:339-360`, `:429-480` |
| Điểm ảnh | Xám 16 bit chia 256 về 8 bit; có trong suốt → RGBA (ảnh web) hoặc lót nền trắng (AI, xem trước); còn lại RGB. Xoay theo Orientation (cùng bảng với `ImageOps.exif_transpose`), `thumbnail(LANCZOS)` (chỉ thu nhỏ), rồi **`Image.frombytes`**: ảnh mới hoàn toàn, không `info` | `:497-558` |
| Ảnh web | WebP `quality=80`, `method=6`, `exif=` EXIF dựng mới (Orientation = 1), hồ sơ màu chỉ khi là RGB hợp lệ. Mở lại: chunk chỉ `VP8X/VP8 /VP8L/ALPH/ICCP/EXIF`, đúng cỡ, **GPS đúng từng giá trị** (so phân số), EXIF còn lại đúng y danh sách giữ, không IFD1 | `:688-756` |
| Bản AI | JPEG q85, chỉ truyền `quality`; kiểm danh sách khối (`jpeg_layout`): SOI, 1 APP0 JFIF 14 byte, DQT, DHT, DRI, 1 SOF0/1, 1 SOS, dữ liệu ảnh chỉ có `FF 00`/RST, EOI ở cuối | `:607-670`, `:760-781` |
| Xem trước | JPEG q80 320 px, cùng lớp kiểm khối; `PreviewCache` lưu theo mã băm của (`ImageRef`, dung lượng, thời điểm sửa) trong `data/image_previews/` | `:784-905` |

## Đối chiếu tiêu chí xong

**7 yêu cầu của phiếu**

- [x] YC1 mở ảnh an toàn, giới hạn điểm ảnh cả HEIC, chỉ định dạng cho phép, không `"MPO"` trong `formats` (`test_qua_so_diem_anh_bi_chan_truoc_khi_giai_ma[HEIF]`, `test_mo_anh_chi_voi_bon_dinh_dang`, `test_dinh_dang_khac_bi_tu_choi_theo_noi_dung`, `test_ma_nguon_..._khong_arrow_khong_alignment`)
- [x] YC2 xoay → Orientation = 1 → cạnh dài 1600 → WebP kèm EXIF lọc 2A (`test_xoay_dung_chieu_ca_8_huong` ×8, `test_thu_canh_dai_khong_phong_to` ×5, `test_2a_giu_ngay_hang_doi_may_bo_seri_chu_may_makernote_ifd1`: ảnh gốc có IFD1 thật, có số seri thân máy/ống kính, `CameraOwnerName`, `Artist`, `Software`, MakerNote)
- [x] YC3 kiểm GPS **sau nén theo giá trị** (`test_f2_webp_con_gps_dung_tung_gia_tri`, `test_kiem_gps_sau_nen_bat_duoc_khi_quen_chep_exif` (giả lập quên `exif=`), `test_kiem_gps_sau_nen_so_gia_tri_khong_chi_co_the` (lệch 0,01 giây vĩ độ))
- [x] YC4 bản AI dựng từ điểm ảnh, không APP1/COM/XMP/chunk chữ (`test_f2_ban_ai_tu_jpeg_day_du_khong_con_metadata`: gốc có EXIF + GPS + XMP + COM + APP13 + APP15 + ICC + IFD1; `test_f2_ban_ai_tu_png_co_chunk_chu`: tEXt, iTXt, zTXt, eXIf, iCCP; `test_f2_ban_ai_tu_heic_co_gps`; `test_ban_ai_bi_chan_neu_pillow_lo_chep_metadata`)
- [x] YC5 ảnh xem trước bỏ EXIF, cache trong `.gitignore` kiểm bằng code (`_cache_dir_is_ignored` `:802-820`; `test_cache_mac_dinh_nam_trong_data_da_gitignore` chạy cả `git check-ignore`; `test_cache_trong_du_an_ngoai_data_thi_khong_ghi`; `test_cache_bi_go_khoi_gitignore_thi_khong_ghi`)
- [x] YC6 tên file không dấu theo nội dung, tránh trùng, không lấy tên thư mục (12 test `test_ten_file_*`, `test_tranh_trung_*`, `test_ham_dat_ten_khong_nhan_ten_thu_muc_hay_ten_file_goc`)
- [x] YC7 ảnh chụp màn hình không EXIF (`test_anh_chup_man_hinh_khong_exif_van_chay`: PNG trong suốt 1920×1080 → WebP 1600×900, không chunk EXIF, giữ trong suốt)

**Lưu ý của Soi Lỗi T-047**

- [x] 1. `open` lẫn `load` trong cùng khối, bắt `(OSError, ValueError)` (`:194-218`; `test_heic_cut_chi_hong_luc_load_van_bat_duoc`, `test_jpeg_png_cut_bao_anh_hong`)
- [x] 2. HEIC hỏng giữa dữ liệu ra ảnh rác: ghi nhận; giao diện (T-056) cho xem trước trước khi dùng
- [x] 3. Đăng ký HEIF một chỗ (`_register_heif` `:122-134`). Đăng ký **lúc mở ảnh lần đầu**, không lúc import; test của phiếu này trả nguyên bảng định dạng sau mỗi test nên test "chưa đăng ký" của T-047 vẫn chạy (xem Đề xuất)

**Điều kiện Lá Chắn T-047 (mục 7), giữ nguyên theo Lá Chắn T-058**

- [x] Đ1 bắt `(OSError, ValueError, Image.DecompressionBombError)` quanh `open` + `load`, câu tiếng Việt cố định, không chép lỗi gốc (`:210-218`; mọi test lỗi dùng `_loi()` kiểm `__cause__ is None`)
- [x] Đ2 kiểm dung lượng **trước khi mở** (`test_kiem_dung_luong_truoc_khi_mo`: `Image.open` không được gọi); `MAX_IMAGE_PIXELS` rõ ràng + tự so `rộng × cao` trước `load()` + `DecompressionBombWarning` thành lỗi (`test_canh_bao_bom_giai_nen_cua_pillow_thanh_loi[PNG/HEIF]`); áp cho HEIC; không bật `DISABLE_SECURITY_LIMITS` (đặt `False` mỗi lần mở)
- [x] Đ3 `register_heif_opener(thumbnails=False, depth_images=False, aux_images=False)` một chỗ duy nhất trong `seo_app/` (test dò mã nguồn); không `load_libheif_plugin`, không ghi HEIC
- [x] Đ4 luôn `formats=["JPEG","PNG","WEBP","HEIF"]`; không thêm AVIF (lý do ở `:57-58`; `test_avif_bi_tu_choi`)
- [x] Đ5 không còn bắt buộc trên Pillow 13 (dùng `draft`/`thumbnail`, ghi JPEG cho bản AI); vẫn chỉ khung đầu MPO (`test_mpo_chi_dung_khung_dau`: `seek` sang khung 2 là hỏng test)
- [ ] Đ6 thay `pytest.skip` trong test "chưa đăng ký" của T-047: **không thuộc phạm vi phiếu này** (không sửa test của T-047), chuyển Soi Lỗi (Đề xuất)
- [x] Đ7 F1: chỉ nhận byte (`test_khong_nhan_duong_dan_chi_nhan_byte`), đọc qua `ImageLibrary.read_image_bytes` (`PreviewCache.get` `:884-905`; test đếm lần gọi); EXIF giữ GPS theo 2A

**Điều kiện Lá Chắn T-048**: [x] kiểm nội dung bằng `formats=…`, không tin đuôi (nhận byte, không có đuôi nào); [x] cache trong `.gitignore` (YC5); [x] đọc qua `read_image_bytes`; khóa cache lấy `ImageRef` của kết quả quét (ghi trong docstring `PreviewCache`).

**Điều kiện Lá Chắn T-058**

- [x] LC-T058-1 không Arrow, không `PILLOW_ALIGNMENT` (test dò mã nguồn đã bỏ chú thích)
- [x] LC-T058-2 `st.image` chỉ nhận `make_preview`/`PreviewCache.get` (JPEG do app tạo, luôn mã hóa lại kể cả khi ảnh gốc đã là JPEG nhỏ sạch): `test_anh_xem_truoc_jpeg_khong_metadata_xoay_dung`, `test_st_image_nhan_anh_xem_truoc` (AppTest, ảnh HEIC). `open_image` trả ảnh còn metadata trong `info`: docstring ghi rõ không đưa thẳng vào `st.image`
- [x] LC-T058-3 từ chối khi Pillow < 13, câu cố định, một dòng kiểm (`:116-119`; `test_tu_choi_khi_pillow_duoi_13` ×4 hàm)
- [x] SL-T058-1 ảnh 16 bit về 8 bit đúng độ sáng (40000 → 156, không thành 255): `test_anh_16_bit_doi_ve_8_bit_dung_do_sang`
- [x] Không đổi `Image.MAX_IMAGE_PIXELS` chung của Pillow (giữ đúng test `test_gioi_han_bom_giai_nen_mac_dinh_khong_doi` của Soi Lỗi T-058): `test_khong_doi_gioi_han_chung_cua_pillow`

**Góp ý Lá Chắn T-046**: [x] số 1 (bản AI dựng lại từ điểm ảnh, test đủ loại metadata); [x] số 2 (so giá trị GPS; số seri, `CameraOwnerName`, MakerNote, IFD1 bị bỏ); [x] số 3 (tên file không nhận tên thư mục, mã công trình chỉ mẫu `CT\d{1,6}`); [x] số 9 (cache, ảnh xem trước không EXIF, câu lỗi không có đường dẫn).

**SL-T050-5 / Lá Chắn T-050**: bản gửi AI không kèm hồ sơ màu, không đổi màu bằng ImageCms (cách (a)); test bản AI chỉ có khối trong danh sách cho phép (đề xuất điểm 4 của Soi Lỗi T-050).

- [x] `uv run pytest` và `uv run ruff check .`: xem Bằng chứng
- [x] Báo cáo tại `docs/team/reports/T-049-tho-may.md`

## Rủi ro và điểm cần chú ý

1. **Khác thiết kế T-046, có lý do:**
   - Giới hạn **80 triệu** điểm ảnh, không phải 100 triệu: Pillow tự cảnh báo từ 89,5 triệu (và phiếu đổi cảnh báo thành lỗi), nên 100 triệu sẽ là con số "trên giấy". Đủ cho máy 48–64 MP. Không đổi giới hạn chung của Pillow (test T-058 kiểm).
   - **Không gọi thẳng `ImageOps.exif_transpose`**: hàm này ghi lại toàn bộ EXIF gốc vào ảnh trả về và nổ `struct.error`/`TypeError`/`AttributeError` với EXIF hỏng (24/4.000 ca khi thử). Dùng đúng bảng xoay của nó (`process.py:249-260`), có test so khớp 8 hướng với `ImageOps.exif_transpose`.
   - **Bỏ 2 thẻ GPS chữ tự do** (`GPSProcessingMethod`, `GPSAreaInformation`): chở được chữ bất kỳ (kể cả địa chỉ gõ tay), điện thoại hầu như không ghi. Vị trí (vĩ độ, kinh độ, độ cao, giờ GPS…) giữ đủ.
   - Thêm bước **đọc kích thước khung WebP trước `Image.open`** (`:160-181`): bộ mở WebP của Pillow cấp bộ nhớ cả khung ngay lúc mở và chỉ chặn khi vượt gấp đôi giới hạn chung (tới ~179 triệu điểm ảnh, ~700 MB RAM). Test bằng 3 kiểu đầu WebP (`VP8X`, `VP8L`, `VP8 `) khai 90 triệu điểm ảnh.
2. **Ảnh web giữ hồ sơ màu ICC** (chỉ hồ sơ RGB, đúng khuôn phần đầu, ≤ 1 MB) để màu ảnh iPhone (Display P3) không nhạt đi trên web, đúng thiết kế T-046 bước 4. SL-T050-5 cho thấy hồ sơ màu chở được chữ tùy ý; ở đây là ảnh của chính doanh nghiệp, công khai trên web. Nhờ Lá Chắn quyết: giữ (như hiện tại) hay bỏ cả ở ảnh web.
3. `warnings.catch_warnings()` không an toàn khi nhiều luồng (Streamlit chạy mỗi phiên một luồng): hai phiên mở ảnh cùng lúc có thể để lại bộ lọc "cảnh báo bom giải nén thành lỗi" cho cả chương trình (chặt hơn, vô hại) hoặc làm mất nó trong chốc lát. Lớp chặn thật là phép so `rộng × cao` của module (không phụ thuộc bộ lọc); đây là suy luận, chưa thử với 2 phiên thật.
4. **Chưa thử với ảnh thật** (iPhone HEIC thật, ảnh Android, MakerNote thật, ảnh MPO của iPhone). Mọi test dùng ảnh giả. Dung lượng WebP thật (mục tiêu 150–400 KB) chưa đo. Nén WebP `method=6` mất khoảng 2 giây với ảnh nhiễu 1600×1200 (trường hợp nặng nhất); ảnh thật nhanh hơn.
5. HEIC chỉ có `nclx` (không ICC) thì ảnh web không có hồ sơ màu: màu rộng có thể hơi nhạt. Chấp nhận.
6. Cache ảnh xem trước không tự dọn; xóa thư mục `data/image_previews/` lúc nào cũng được (tự tạo lại).
7. `folders.IMAGE_EXTENSIONS` (T-048) nhận đuôi `.avif`, nhưng phiếu này **không mở AVIF** (theo Đ4): ảnh `.avif` hiện trong danh sách nhưng bấm vào sẽ báo "không phải ảnh JPEG, PNG, WebP hoặc HEIC".

## Đề xuất

- **Soi Lỗi:** (a) điều kiện 6 Lá Chắn T-047: thay `pytest.skip` ở `tests/test_pillow_heif_setup.py:46-47` bằng fixture tự gỡ `HEIF` khỏi bảng định dạng. Phiếu này đăng ký HEIF lúc mở ảnh lần đầu (không lúc import) và test của phiếu tự trả nguyên bảng, nên hiện test đó vẫn chạy; nhưng phiếu giao diện (T-056) mở ảnh trong AppTest sẽ để HEIF đăng ký sẵn. (b) Thử thêm: ảnh có EXIF cả ở PNG `eXIf` lẫn chunk `Raw profile type exif`, ảnh WebP động, JPEG CMYK đảo màu (Adobe), JPEG có nhiều khối APP1 EXIF, ảnh rất dẹt (1 × 10000).
- **Lá Chắn:** quyết điểm 2 (ICC ở ảnh web); soát `_webp_canvas_pixels`, `jpeg_layout`, `_cache_dir_is_ignored`, `_KeptExif` (danh sách cho phép 2A).
- **T-064 (dọn thư mục ảnh) hoặc Chỉ Huy:** bỏ `.avif` khỏi `folders.IMAGE_EXTENSIONS`, hoặc mở phiếu thêm AVIF vào `ALLOWED_FORMATS` (Lá Chắn xét thư viện libavif/dav1d).
- **T-053 (ảnh AI):** dùng `make_web_image` cho ảnh AI trả về (không có GPS); phần đánh dấu EXIF `ImageDescription`/`Software` của ảnh AI (thiết kế T-046 mục 4) chưa có: phiếu đó cần thêm tham số vào `make_web_image` (sửa `process.py`). Tên file: `image_file_name(..., ai_generated=True)`.
- **T-054 (chèn ảnh vào nháp):** tải lên đúng `WebImage.data` (không sửa byte) để GPS tới WordPress; tên file từ `naming.image_file_name`.
- **T-056 (giao diện):** `st.image` chỉ nhận `PreviewCache.get(library, ref)` hoặc `make_preview(...)`; hiện `WebImage.notice` khi có, và "Ảnh không có vị trí GPS" khi `WebImage.gps is None`; bắt cả `ImageFolderError` lẫn `ImageProcessError`.
- **T-062 (đọc cấu hình ảnh):** truyền `[images] webp_quality`, `max_edge_px` vào `make_web_image(webp_quality=…, max_edge_px=…)`; giá trị sai đã có câu báo tiếng Việt nêu tên khóa.
- **Chỉ Huy/chủ dự án:** sau khi gộp, thử 3–5 ảnh thật trên máy (không commit ảnh): mở bằng app, xem GPS còn (ví dụ bằng thuộc tính file trên Windows) và dung lượng WebP.

## Câu hỏi cho chủ dự án

Không có.

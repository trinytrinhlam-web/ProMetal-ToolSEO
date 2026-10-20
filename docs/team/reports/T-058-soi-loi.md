# Báo cáo T-058 · Soi Lỗi kiểm rút gọn: nâng lên Pillow 13

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-058](../tickets/T-058-nang-pillow-13.md) |
| Ngày nộp | 2026-10-20 |
| Kết quả | Hoàn thành · Kết luận: **ĐẠT**, chuyển sang Lá Chắn |

## Tóm tắt (cho chủ dự án)

Đã thử Pillow 13 với mọi chỗ Streamlit dùng Pillow để vẽ ảnh, với bộ nhớ tạm của Streamlit, và với đúng các bước xử lý ảnh mà phiếu T-049 sắp làm (xoay ảnh, lọc EXIF, thu nhỏ 1600 px, lưu WebP còn nguyên GPS). Không tìm thấy lỗi nào do việc nâng cấp: 60 test mới đều qua, toàn bộ 7.232 test qua (0 hỏng) trên Windows, kiểm code sạch. Có một giới hạn cũ của Streamlit (ảnh xám 16 bit) đã có từ Pillow 12.3.0, không do phiếu này, ghi lại để T-049 tránh. Việc còn lại trước khi gộp: Lá Chắn kiểm bảo mật, Chỉ Huy mở app thật xem mọi trang.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t058.py` | Hoàn thiện bản dở của phiên Soi Lỗi trước (commit `042a626`, 49 test, chưa từng chạy) thành 60 test; chi tiết ở mục "Đã thử gì" |
| `docs/team/reports/T-058-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, `pyproject.toml`, `uv.lock`.

**Sửa trong bản dở** (lỗi của test, không phải của ứng dụng):

- `test_st_image_bytes_rac_bao_loi_ro_rang`: khẳng định cũ `"UnidentifiedImageError" in ... or at.exception[0].message` luôn đúng khi có bất kỳ lỗi nào. Nay kiểm đúng loại lỗi `PIL.UnidentifiedImageError` và câu "cannot identify image file".
- `test_cache_data_bam_duoc_anh_pillow`: AppTest đặt tên tệp trang theo mã nguồn, nên cache của hàm trong trang còn lại giữa các lần chạy cùng tiến trình; chạy test hai lần là hỏng (không có `so_lan_tinh`). Nay xóa cache của hàm đó đầu trang. Thêm ảnh khác một điểm màu và ảnh bảng màu (`P`) cùng điểm ảnh nhưng khác bảng màu để chắc Streamlit băm theo nội dung (`tobytes()` + `getpalette()`), không chỉ theo cỡ.
- Fixture `canh_bao_la_loi` (đổi cảnh báo "sắp bỏ" thành lỗi) chưa có gì chứng minh nó có hiệu lực trong luồng riêng mà AppTest chạy trang. Thêm test chứng minh và test đối chứng.
- `test_gioi_han_bom_giai_nen_van_bat` chỉ kiểm một hằng số. Nay kiểm thật hành vi (xem dưới).

## Đã thử gì

Phiên bản đang chạy: Pillow **13.0.0**, pillow-heif **1.8.1**, Streamlit **1.65.0**, Python 3.12.15, uv 0.12.23, Windows 11.

| Nhóm | Test | Kết quả |
|---|---|---|
| Fixture | Cảnh báo "sắp bỏ" trong trang AppTest thành lỗi (`test_canh_bao_sap_bo_trong_app_thanh_loi`), đối chứng không đổi thì trang chạy bình thường | Qua |
| `st.image` ảnh Pillow | 6 chế độ màu (RGB, L, RGBA, LA, P, CMYK); RGBA giữ đúng độ trong suốt; RGBA ép JPEG bỏ alpha; ảnh 1×1, 1×500, 500×1; ảnh rộng 3000 px thu về 1460 px (đúng màu); `width=100`; ảnh 4032×3024; ảnh mở từ file JPEG; 3 ảnh một lúc | Qua. Bắt byte Streamlit thật gửi ra trình duyệt, mở lại bằng Pillow để kiểm định dạng, cỡ, kênh alpha, màu |
| `st.image` bytes/BytesIO/file | PNG có alpha, JPEG, WEBP (có/không alpha), BMP, TIFF, GIF động (giữ nguyên 4 khung khi nhỏ, thu nhỏ khi quá rộng); đường dẫn file tên có dấu và khoảng trắng; logo SVG của app (không qua Pillow); bytes rác báo `UnidentifiedImageError` rõ ràng | Qua |
| `st.image` numpy | Xám 2 chiều và 1 kênh, RGB, RGBA, float32, float64 có `clamp`, BGR (đảo kênh đúng), ép PNG | Qua |
| Chỗ khác dùng ảnh Pillow | `st.set_page_config(page_icon=ảnh)`, `st.logo(ảnh)`, `st.chat_message(avatar=ảnh)`, `st.write(ảnh)` | Qua (app hiện chỉ dùng logo SVG và emoji, nhưng phiếu sau có thể dùng) |
| `st.cache_data` | Băm ảnh Pillow: trùng thì lấy cache, khác 1 điểm màu thì tính lại, ảnh `P` khác bảng màu thì tính lại | Qua (đúng 4 lần tính) |
| Đường T-049 | JPEG có GPS đọc lại đúng; WebP kèm `exif=` (cả `getexif()` lẫn `info["exif"]`) giữ GPS, hãng, hướng; không truyền `exif=` thì mất GPS; xóa thẻ GPS thì chỉ mất GPS; sau `exif_transpose` vẫn giữ GPS | Qua |
| Đường T-049 đủ bước | JPEG 4032×3024 có EXIF như điện thoại (GPS, hãng, đời máy, ngày chụp, số seri, tên chủ máy, MakerNote, hướng 6) → mở với `formats=` → `exif_transpose` → Orientation = 1 → bỏ số seri, tên chủ máy, MakerNote → `thumbnail(1600)` → WebP. Ra 1200×1600, **giá trị** GPS khớp ảnh gốc, giữ hãng/đời máy/ngày chụp, không còn chuỗi số seri và MakerNote trong byte EXIF | Qua |
| JPEG `thumbnail()`/`draft()` | Đường có lỗ hổng GHSA-8g5g ở 12.3.0: JPEG 4000×3000, `draft` giảm cỡ lúc giải mã còn 1000×750, `thumbnail(400)` ra 400×300 đúng màu | Qua |
| MPO | Ảnh nhiều khung mở qua `formats=["JPEG",...]` ra format `MPO`, `seek(1)` đọc đúng khung 2; `formats=["MPO"]` vẫn `KeyError` trên Pillow 13 (đúng như phiếu T-049 ghi) | Qua |
| HEIC | HEIC có GPS sang WebP giữ GPS; `st.image` vẽ được ảnh HEIC | Qua |
| Bom giải nén | Giới hạn mặc định vẫn 89.478.485 điểm ảnh; `DecompressionBombError` vẫn không phải con của `OSError`; với PNG **và HEIC**: vượt giới hạn thì cảnh báo, vượt gấp đôi thì lỗi, đổi cảnh báo thành lỗi thì `Image.open` báo lỗi | Qua |

Mọi ảnh tạo trong bộ nhớ hoặc thư mục tạm (`tmp_path`); không gọi mạng (bộ chặn mạng của `tests/conftest.py` vẫn bật).

## Bằng chứng

```
$ git pull --ff-only            # đầu phiên, nhánh team/T-058 tại 042a626
Already up to date.

$ uv run pytest tests/test_soi_loi_t058.py -q      # bản dở, trước khi sửa
49 passed in 41.71s

$ uv run pytest tests/test_soi_loi_t058.py -q      # sau khi hoàn thiện (commit 86dc99b)
60 passed in 50.54s

$ uv run python -c "import PIL, pillow_heif, streamlit; print(PIL.__version__, pillow_heif.__version__, streamlit.__version__)"
13.0.0 1.8.1 1.65.0

$ uv lock --check
Resolved 70 packages in 11ms

$ uv sync --locked --dry-run
Would make no changes                               # môi trường đang chạy khớp uv.lock

$ uv pip check
Found 1 incompatibility
The package `streamlit` requires `pillow>=7.1.0,<13`, but `13.0.0` is installed   # cố ý (override)

$ git diff 5e5c02b..HEAD -- uv.lock                 # so với trước T-058
chỉ đổi: thêm [manifest] overrides = [{ name = "pillow", specifier = ">=13.0.0,<14" }];
pillow 12.3.0 -> 13.0.0 (1 sdist + 68 wheel, có đủ cp312 Windows/Mac Intel/Mac M/Linux);
requires-dist của seo-app: pillow >=12.3 -> >=13.0.0. Không gói nào khác đổi.

$ grep pyproject.toml
15: "pillow>=13.0.0",
35: [tool.uv]
38: override-dependencies = ["pillow>=13.0.0,<14"]

$ uv run pytest -q -rfEs              # toàn bộ, Windows 11, tại commit 86dc99b
7232 passed, 11 skipped, 27 xfailed, 1 warning in 699.60s (0:11:39)
(= 7.172 của Thợ Máy + 60 test mới; 0 hỏng, 0 lỗi. 11 bỏ qua đều do Windows: quyền 600 kiểu
Mac/Linux, tạo symlink cần quyền đặc biệt; giống hệt lần chạy của Thợ Máy. Cảnh báo duy nhất:
Pydantic trong tests/test_soi_loi_t028.py, có từ trước, không liên quan Pillow.)

$ uv run ruff check .
All checks passed!
```

`run.bat` (dòng 25) và `run.command` (dòng 26) chạy `uv sync`, nên máy chủ dự án sẽ nhận Pillow 13 theo `uv.lock` khi bấm chạy app.

Kiểm lại giới hạn ảnh 16 bit trên bản cũ (môi trường riêng, không đụng `.venv`):

```
$ uvx --offline --from "pillow==12.3.0" python -c "...Image.new('I;16',(4,4),3000).save(buf,'JPEG')..."
12.3.0
OSError cannot write mode I;16 as JPEG
$ uv run python -c "...cùng lệnh trên Pillow 13..."
OSError cannot write mode I;16 as JPEG
```

## Lỗi tìm được

Không có lỗi nào do việc nâng lên Pillow 13.

| Mã | Mức | Nội dung |
|---|---|---|
| SL-T058-1 | Thấp (ghi nhận, có từ trước, không chặn) | `st.image` với ảnh xám 16 bit (`I;16`) ở chế độ tự động: Streamlit chọn JPEG, Pillow báo `OSError: cannot write mode I;16 as JPEG`. |

**SL-T058-1, cách tái hiện:** trong trang Streamlit, `st.image(Image.new("I;16", (40, 30), 3000))`.
Mong đợi: hiện ảnh. Thực tế: trang báo lỗi `OSError`. Y hệt trên Pillow 12.3.0 (bằng chứng ở trên), nên đây là giới hạn của Streamlit, không phải do T-058. Truyền `output_format="PNG"` thì chạy (`test_st_image_anh_16_bit_phai_chon_png`). App hiện không hiển thị ảnh 16 bit; ghi lại để T-049 biết (xem Đề xuất).

## Kết luận

**ĐẠT**: chuyển sang Lá Chắn. Không có lỗi nào phải trả Thợ Máy sửa; SL-T058-1 có từ trước, không do T-058, không chặn. Việc mở app thật kiểm mọi trang vẫn là bước của Chỉ Huy trước khi gộp.

## Đối chiếu tiêu chí xong

- [x] Pillow thật đang chạy là 13.0.0, pillow-heif 1.8.1, Streamlit 1.65.0, khớp báo cáo Thợ Máy (lệnh `uv run python -c ...` ở trên)
- [x] `pyproject.toml` và `uv.lock` khai đúng như báo cáo Thợ Máy: `pillow>=13.0.0`, `override-dependencies = ["pillow>=13.0.0,<14"]`, chỉ gói Pillow đổi, `uv lock --check` và `uv sync --locked --dry-run` khớp
- [x] Mọi nhánh Streamlit dùng Pillow (`image_to_url`, `_pil_to_bytes`, `_np_array_to_bytes`, `_ensure_image_size_and_format` có `resize`, băm ảnh của `cache_data`) có test và qua, không có cảnh báo "sắp bỏ"
- [x] Đường T-049 (WebP giữ GPS, lọc EXIF, `thumbnail`, MPO, HEIC, bom giải nén) chạy trên Pillow 13
- [x] `uv run pytest` 0 hỏng trên Windows; `uv run ruff check .` sạch
- [ ] Mở app thật kiểm mọi trang: việc của Chỉ Huy (phiếu, yêu cầu 3); Soi Lỗi chỉ có `tests/test_app_pages.py` (qua trong bộ test toàn phần)

## Rủi ro và điểm cần chú ý

- `uv pip check` sẽ luôn báo 1 xung đột (Streamlit đòi `pillow<13`) chừng nào còn override. Đó là cố ý; đừng "sửa" bằng cách hạ Pillow.
- Test chỉ thay được một phần việc mở app thật: Streamlit chưa được thử chính thức với Pillow 13. Mọi hàm Pillow mà Streamlit 1.65 gọi đã được chạy qua với cảnh báo "sắp bỏ" bị đổi thành lỗi.
- Nếu phải quay về Pillow 12.3.0 (mục "Cách quay về" của báo cáo Thợ Máy): `tests/test_soi_loi_t058.py` không ghim bản 13 và **đã chạy qua cả trên 12.3.0** (bằng chứng dưới), nên không cần xóa; chỉ xóa `tests/test_pillow_version_t058.py` như Thợ Máy ghi. Mặt trái: 60 test này là test chống hỏng chức năng, không phân biệt được 12.3.0 với 13 (không dựng file ảnh khai thác lỗ hổng); chỉ `test_pillow_la_ban_13` của Thợ Máy giữ phiên bản.

```
$ uv run --offline --with "pillow==12.3.0" pytest tests/test_soi_loi_t058.py tests/test_pillow_version_t058.py -q
FAILED tests/test_pillow_version_t058.py::test_pillow_la_ban_13 - assert <Version('12.3.0')> >= <Version('13.0.0')>
1 failed, 61 passed in 37.27s        # đúng như dự tính: chỉ test ghim bản 13 hỏng
```
- Lệch số khuyến cáo (Lá Chắn T-047 ghi 53, Thợ Máy đếm 40 hôm nay) và GHSA-654x-cwwv-5j9c (chưa có bản vá ở 13.0.0) là phần của Lá Chắn; Soi Lỗi không kiểm lại.

## Đề xuất

- **Lá Chắn:** kiểm D1 cho phiếu này; đối chiếu 53 → 40 khuyến cáo.
- **Chỉ Huy:** mở app thật (`uv run streamlit run app/main.py`) xem mọi trang trước khi gộp, theo yêu cầu 3 của phiếu.
- **T-049 (Thợ Máy):** (1) `formats=["MPO"]` vẫn `KeyError` trên Pillow 13 và ảnh MPO mở qua `"JPEG"` ra format `MPO` (nhiều khung): chỉ lấy khung đầu, không `seek()` qua các khung. (2) `DecompressionBombError` vẫn không phải con của `OSError`; giới hạn điểm ảnh có áp cho HEIC (đã thử). (3) Nếu có bước xem trước bằng `st.image`, đổi ảnh về RGB/8 bit trước (hoặc `output_format="PNG"`) để tránh SL-T058-1 với ảnh PNG 16 bit. (4) Thứ tự xoay → Orientation = 1 → lọc EXIF → `thumbnail` → WebP đã chạy được trên Pillow 13 (`test_duong_t049_xoay_loc_exif_thu_nho_webp`); Soi Lỗi T-049 sẽ kiểm lại trên code thật.

## Câu hỏi cho chủ dự án

Không có.

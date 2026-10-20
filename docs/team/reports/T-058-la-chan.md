# Biên bản bảo mật T-058 · Nâng Pillow 13

> **Model:** chạy tạm **Claude Opus 5.5** vì tài khoản này không dùng được Claude Fable (chủ dự án đã duyệt). Cần kiểm lại bằng Fable sau 01/11.
>
> **BẢN NHÁP (phần 1/3):** đã có nguồn gốc gói, đối chiếu khuyến cáo, lỗi phát hiện. Danh sách kiểm, kết quả công cụ và kết luận đang viết tiếp.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, thay Fable) |
| Phiếu được kiểm | [T-058](../tickets/T-058-nang-pillow-13.md) (chặn [T-049](../tickets/T-049-xu-ly-anh-webp-giu-gps.md)) |
| Phạm vi | diff `origin/main...team/T-058` (gốc chung với `main` → `bda4dfc`): `pyproject.toml`, `uv.lock`, `tests/test_pillow_version_t058.py`, `tests/test_soi_loi_t058.py`, 2 báo cáo. Đọc thêm: `streamlit/elements/lib/image_utils.py`, `streamlit/dataframe_util.py`, mã Pillow 12.3.0 và 13.0.0 |
| Máy kiểm | Windows 11, Python 3.12.15, uv 0.12.23, worktree `wt-T-058` |
| Ngày | 2026-10-20 |
| **Kết luận** | _(đang viết, xem phần 3)_ |

## 1. Bản Pillow được cài có đúng là bản thật từ PyPI không (D1)

| Kiểm gì | Bằng chứng | Kết quả |
|---|---|---|
| Bản đang chạy | `uv run python -c "import PIL, pillow_heif, streamlit; ..."` → `13.0.0 1.8.1 1.65.0`, nạp từ `wt-T-058\.venv\Lib\site-packages\PIL` | Đúng 13.0.0 |
| Lock khớp `pyproject.toml` | `uv lock --check` → `Resolved 70 packages`; `uv sync --locked` → `Checked 69 packages`, không đổi gì | Khớp |
| Nguồn tải | `uv.lock:1001-1004`: `source = { registry = "https://pypi.org/simple" }`; mọi wheel và sdist của 70 gói đều ở `https://files.pythonhosted.org/packages/` (script so 2 file lock, không có URL lạ) | PyPI chính thức |
| Mã băm trong lock = mã băm PyPI | Lấy `https://pypi.org/pypi/pillow/13.0.0/json`, so từng file: **69/69 khớp** (68 wheel + 1 sdist), 0 lệch. 14 file PyPI không có trong lock đều là bản cp311/pp311, đúng vì dự án đòi `requires-python >= 3.12` (`pyproject.toml:6`). PyPI ghi `yanked: false`, trường `vulnerabilities: []` | Khớp |
| Ai đóng gói wheel | API chứng thực của PyPI (`/integrity/pillow/13.0.0/pillow-13.0.0-cp312-cp312-win_amd64.whl/provenance`): người đăng là **GitHub `python-pillow/Pillow`, workflow `wheels.yml`, môi trường `release-pypi`** (Trusted Publishing); câu khai ghi sha256 `ff3fe9eb…961b`, trùng `uv.lock` cho wheel Windows đang cài. Thẻ `13.0.0` trên GitHub trỏ commit `293218a`, phát hành 2026-10-16 22:37 UTC | Đúng kho gốc. **Chưa** tự kiểm chữ ký Sigstore (chỉ đọc nội dung câu khai) |
| File đã cài còn nguyên | So sha256 từng file với `RECORD`: `pillow-13.0.0.dist-info` 121/121 khớp, `pillow_heif-1.8.1.dist-info` 27/27 khớp. `INSTALLER` = `uv`, thẻ wheel `cp312-cp312-win_amd64`. uv kiểm mã băm theo `uv.lock` khi cài | Nguyên vẹn |
| Thư viện kéo theo | So `uv.lock` của `main` và nhánh: 70 gói cả hai bên, **không thêm, không bớt**; chỉ `pillow` đổi `12.3.0 → 13.0.0`, `seo-app` đổi khai báo `pillow>=12.3 → >=13.0.0` (`uv.lock:1604`). METADATA của Pillow 13 không có `Requires-Dist` bắt buộc nào (26 dòng đều là `extra`). `olefile` không được cài, nên bộ đọc FPX/MIC không được bật (`Image.OPEN` không có `FPX`, `MIC`) | Không có gói lạ |
| `override-dependencies` đè đúng một gói | `pyproject.toml:35-38` và `uv.lock:13-14`: `overrides = [{ name = "pillow", specifier = ">=13.0.0,<14" }]`, duy nhất một mục. Ba gói đòi Pillow (`streamlit` `<13`, `pillow-heif` `>=11.1.0`, `seo-app`) đều nhận 13.0.0 (`uv.lock:1081,1584,1663`). `uv pip check` → đúng 1 xung đột cố ý: `streamlit requires pillow>=7.1.0,<13` | Chỉ đè Pillow |
| Có bản mới hơn không | PyPI (API simple): bản 13.x/14.x duy nhất là `13.0.0`. Streamlit mới nhất `1.66.0` vẫn khai `pillow<13,>=9.2.0` | 13.0.0 là mới nhất |

Thư viện C đóng sẵn trong wheel Pillow 13.0.0 (theo SBOM `pillow-13.0.0.dist-info/sboms/pillow-13.0.0.cdx.json` và `PIL.features`): libjpeg-turbo 3.2.0, libwebp 1.6.0, zlib-ng 2.3.3, Little CMS 2.19.1, libavif 1.4.2, OpenJPEG 2.5.4, libtiff 4.7.2, FreeType 2.14.3, HarfBuzz 14.5.0. Bản phát hành mới nhất trên GitHub của libjpeg-turbo, zlib-ng, Little-CMS, libavif, OpenJPEG, libwebp đều trùng bản trong wheel; kho của họ không có khuyến cáo GitHub nào. OpenJPEG 2.5.4 là bản có lỗi OSV-2025-219 (GHSA-78g4-xqwv-q3g8), nhưng ghi chú phát hành 13.0.0 ghi Pillow đã vá thêm (`Apply uclouvain/openjpeg#1621 to address OSV-2025-219 #10156`). **Chưa tra NVD** cho các thư viện C này; libtiff (GitLab) chưa tra.

## 2. Khuyến cáo của Pillow: 12.3.0 → 13.0.0

Nguồn: `gh api --paginate repos/python-pillow/Pillow/security-advisories`, tra 2026-10-20 09:31 giờ VN (02:31 UTC).

| Nhóm | Số lượng |
|---|---|
| Khuyến cáo đã công bố của kho | 61 (không mục nào bị rút: `withdrawn_at` đều rỗng) |
| **Ảnh hưởng 12.3.0** | **41**: 2 nghiêm trọng, 13 cao, 23 trung bình, 3 thấp. Đều công bố 17/10, trừ GHSA-654x (19/10) |
| Trong đó **vá ở 13.0.0** | **40** |
| **Còn ảnh hưởng 13.0.0, chưa có bản vá** | **1**: GHSA-654x-cwwv-5j9c (trung bình, khoảng `11.2.1 - 13.0.0`): xuất ảnh sang Arrow lộ vùng nhớ cũ khi đặt `PILLOW_ALIGNMENT` > 1 (lỗi LC-T058-1) |
| Cũ hơn, đã vá trước 12.3.0 | 20 |
| Kho khuyến cáo chung GitHub (`/advisories?ecosystem=pip&affects=pillow@12.3.0` và `@13.0.0`) | 0 và 0 (chưa nhận các mục tháng 10) |
| OSV (`/v1/query`, PyPI) cho `pillow 12.3.0`, `pillow 13.0.0`, `pillow-heif 1.8.1`, `streamlit 1.65.0` | `{}` cả bốn |

**Đính chính con số 53 của Lá Chắn T-047.** Hôm nay tôi đếm lại được 41 mục chạm 12.3.0 (40 vá ở 13.0.0 + GHSA-654x), khớp con số của Thợ Máy. Số mức cao trở lên vẫn là 15 (T-047 ghi 1 nghiêm trọng + 14 cao, nay 2 + 13: một mục được nâng mức), nên 13 mục biến mất đều thuộc mức trung bình/thấp. Không mục nào ở trạng thái "rút"; mục bị nhóm Pillow đưa về nháp hoặc đóng (thường vì trùng) thì người ngoài không xem được, nên tôi **không xác minh được** 13 mục đó là gì. Nếu chúng còn hiệu lực mà chưa vá thì sẽ hiện với `patched_versions` rỗng như GHSA-654x; hiện không có mục nào như vậy ngoài GHSA-654x. Năm mục T-047 nêu tên (GHSA-8g5g, GHSA-g7cr, GHSA-g4qv, GHSA-p8hx, GHSA-4rm8) vẫn còn, đều vá ở 13.0.0.

**Bản vá có thật trong 13.0.0 không** (không chỉ tin nhãn của khuyến cáo). So mã nguồn 12.3.0 (bộ nhớ đệm uv) với 13.0.0 (đã cài) và mã C trên GitHub ở hai thẻ:

| Khuyến cáo | Đường app/T-049 có thể đi | Bằng chứng bản vá |
|---|---|---|
| GHSA-8g5g-8vmr-9782 (cao, JPEG `draft()`/`thumbnail()`) | T-049 thu nhỏ ảnh 1600 px | `src/libImaging/JpegDecode.c` thẻ 13.0.0 thêm kiểm `cinfo.output_width > state->xsize` và `output_components * output_width`, sai thì `IMAGING_CODEC_BROKEN` |
| GHSA-g7cr-3p24-7wf7 (cao, ghi JPEG có ICC + chú thích) | Streamlit lưu ảnh Pillow thành JPEG trong `st.image` | `src/libImaging/JpegEncode.c:330-334` thẻ 13.0.0 thêm kiểm `comment_size + 5 > free_in_buffer` |
| GHSA-g4qv-2jxx-769h (cao, PNG eXIf chạy bậc hai) | Đọc EXIF ảnh PNG | `PIL/Image.py:4152` (13.0.0): `re.sub(b"^(Exif\x00\x00){1,2}", b"", data)` thay vòng `while data.startswith(...)` cắt từng lần (`Image.py:4148` bản 12.3.0) |
| GHSA-p8hx-v2p6-rp84 (trung bình, MPO/DCX `seek()` vượt chặn bom) | Ảnh MPO từ điện thoại | `PIL/MpoImagePlugin.py` và `DcxImagePlugin.py` (13.0.0) thêm `Image._decompression_bomb_check(self.size)` trong `seek()` |
| GHSA-g842-9rc4-69pw, GHSA-xgh8-jp6q-p5x8, GHSA-3j72-p6qg-6xp7, GHSA-74r2-7ff9-mjj2 | Spider, XBM, TarIO, chú thích GIF | Có thay đổi tương ứng trong `SpiderImagePlugin.py` (kiểm bom), `XbmImagePlugin.py` (bỏ biểu thức chính quy, đọc từng dòng tối đa 75 byte), `TarIO.py` (chặn cỡ âm), `GifImagePlugin.py` (gom chú thích vào danh sách) |

Các mục còn lại phần lớn nằm ở định dạng app không cần (TIFF, PDF, FPX, EPS, WMF, BMP, MSP, Spider, XBM, font PIL); không kiểm từng bản vá của các mục này.

## Lỗi phát hiện

Không có lỗi Nghiêm trọng, Cao hay Trung bình. Bốn lỗi Thấp, đều **chưa có đường đi** trong code hiện tại; ba lỗi đầu chuyển thành điều kiện cho T-049.

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T058-1 | Thấp | Pillow 13.0.0 còn **GHSA-654x-cwwv-5j9c** chưa vá: xuất ảnh sang Arrow (`Image.__arrow_c_array__`, `__arrow_c_schema__`) trả kèm vùng nhớ chưa xóa (có thể chứa điểm ảnh của ảnh khác đã giải phóng) khi biến môi trường `PILLOW_ALIGNMENT` > 1. Pillow 12.3.0 cũng bị, nên nâng không làm xấu đi | thư viện (`PIL/Image.py:822-826, 3384`; Pillow đọc biến ở `Image.py:4017`) | **Hiện không có đường đi:** máy không đặt biến `PILLOW_*` (`env`), `.env` chỉ đọc bằng `dotenv_values` (`seo_app/config.py:112`, `seo_app/env_file.py:94`) nên không ghi được biến vào môi trường; `grep` `PILLOW_`, `fromarrow`, `__arrow_c_` trong `app/`, `seo_app/`, `scripts/`, `config/`, `tests/`, `.env.example`, `run.*`: 0 dòng. Streamlit chỉ nhận dữ liệu Arrow qua `__arrow_c_stream__` (`streamlit/dataframe_util.py:731`), ảnh Pillow không có hàm này (0 dòng trong `PIL/`). Kẻ muốn đặt biến môi trường phải chiếm máy trước | Điều kiện T-049: không xuất ảnh sang Arrow (`__arrow_c_array__`, `fromarrow`, `pyarrow` với ảnh), không đặt `PILLOW_ALIGNMENT`. Lượt quét cuối Giai đoạn 3: xem có Pillow 13.0.1 vá mục này chưa, có thì nâng |
| LC-T058-2 | Thấp (có từ trước, không do T-058) | `st.image` của Streamlit tự mở ảnh bằng `Image.open(io.BytesIO(...))` **không có `formats=`** cho mọi đầu vào dạng đường dẫn, bytes, BytesIO; Pillow nhận 43 định dạng (có EPS, WMF, TIFF, PDF…). Danh sách định dạng an toàn của T-049 (`formats=["JPEG","PNG","WEBP","HEIF"]`, điều kiện 4 của T-047) **không áp** cho đường này | `streamlit/elements/lib/image_utils.py:115, 194, 307-309` | **Hiện không có đường đi:** `st.image` duy nhất là logo SVG (`app/main.py:38`), Streamlit đọc như chữ, không qua Pillow. **Từ T-049 hoặc phiếu giao diện xem trước ảnh:** nếu đưa thẳng đường dẫn/byte của file trong `IMAGE_FOLDERS` vào `st.image` → file mang đuôi `.jpg` nhưng nội dung là định dạng khác (Pillow nhận theo nội dung) → bộ giải mã ngoài danh sách chạy trên dữ liệu lạ. Với 13.0.0 các lỗi đã biết đều đã vá, nên đây là lớp phòng thủ thêm cho lỗ hổng tương lai | Điều kiện T-049 và mọi phiếu có xem trước ảnh: chỉ đưa vào `st.image` **ảnh đã mở qua hàm mở an toàn của module ảnh** (có `formats=`, giới hạn điểm ảnh) hoặc **byte WebP/JPEG do chính app tạo ra**; không đưa đường dẫn hay byte gốc của file người dùng |
| LC-T058-3 | Thấp | Đường **quay về Pillow 12.3.0** (báo cáo Thợ Máy mục "Cách quay về", chú thích `pyproject.toml:37`) bảo xóa `tests/test_pillow_version_t058.py`, tức bỏ chốt chặn duy nhất giữ phiên bản. Sau khi T-049 gộp mà không còn điều kiện 5 (Chỉ Huy A ghi trên `main`: "Nếu T-058 đã gộp thì điều kiện 5 … không còn bắt buộc") | `docs/team/reports/T-058-tho-may.md:104-110`; `pyproject.toml:37` | App hỏng với Pillow 13 → quay về theo hướng dẫn, xóa test ghim bản → code T-049 gọi `thumbnail()` trên JPEG chạy trên 12.3.0 → JPEG dựng riêng trong thư mục Drive dùng chung → tràn heap GHSA-8g5g (có thể chạy mã trên máy chứa `.env`). Hướng dẫn có câu "phải theo lựa chọn B" nhưng không có gì tự chặn | (a) Quay về 12.x thì phải **mở lại kiểm định Lá Chắn** và áp lại điều kiện 5 của T-049 trước khi chạy app với ảnh thật. (b) Khuyên T-049: module ảnh từ chối xử lý ảnh khi `PIL.__version__` < 13 (một dòng kiểm lúc mở ảnh, có test), để quay về sai cách thì app báo lỗi thay vì chạy âm thầm |
| LC-T058-4 | Thấp | Ép phiên bản để lại 3 điểm cần nhớ: (1) `<14` sẽ chặn Pillow 14 dù sau này 14 mới có bản vá; (2) `uv pip check` luôn báo 1 xung đột nên dễ quen mắt, bỏ sót xung đột Pillow thật về sau; (3) pip-audit, OSV và kho khuyến cáo chung GitHub **chưa có** khuyến cáo Pillow tháng 10 (mục 2), nên "pip-audit sạch" chưa đủ làm bằng chứng | `pyproject.toml:38` | Không phải lỗ hổng; là rủi ro bảo trì: bản vá mới ra mà không ai nâng | Lượt quét cuối Giai đoạn 3 và mỗi lần đổi `uv.lock`: tra thẳng `gh api repos/python-pillow/Pillow/security-advisories`, xem Streamlit đã cho Pillow 13 chưa (cho rồi thì bỏ override, giữ `pillow>=13.0.0`), xem có Pillow 14 chưa. `uv pip check` chỉ được phép báo đúng dòng `streamlit … <13` |

Câu hỏi của Chỉ Huy "Streamlit gặp Pillow ngoài dải nó khai báo có mở ra lỗ bảo mật nào không": **không thấy lỗ mới.** Streamlit 1.65 chỉ dùng Pillow ở `image_utils.py` (`Image.open`, `fromarray`, `resize(BILINEAR)`, `save`) và ở băm `st.cache_data` (`runtime/caching/hashing.py:48`, `tobytes()` + `getpalette()`). Soi Lỗi đã chạy mọi nhánh này trên 13.0.0 với cảnh báo "sắp bỏ" đổi thành lỗi (60 test), kể cả hai ảnh khác bảng màu ra hai mã băm khác nhau (cache không nhầm ảnh). Ảnh rác vẫn ra `UnidentifiedImageError`, không treo. Chỗ đáng lưu ý duy nhất là LC-T058-2, có từ trước và không phụ thuộc phiên bản.

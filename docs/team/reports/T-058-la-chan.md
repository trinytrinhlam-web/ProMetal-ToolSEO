# Biên bản bảo mật T-058 · Nâng Pillow 13

> **Model:** chạy tạm **Claude Opus 5.5** vì tài khoản này không dùng được Claude Fable (chủ dự án đã duyệt). Cần kiểm lại bằng Fable sau 01/11.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, thay Fable) |
| Phiếu được kiểm | [T-058](../tickets/T-058-nang-pillow-13.md) (chặn [T-049](../tickets/T-049-xu-ly-anh-webp-giu-gps.md)) |
| Phạm vi | diff `origin/main...team/T-058` (gốc chung với `main` → `bda4dfc`): `pyproject.toml`, `uv.lock`, `tests/test_pillow_version_t058.py`, `tests/test_soi_loi_t058.py`, 2 báo cáo. Đọc thêm: `streamlit/elements/lib/image_utils.py`, `streamlit/dataframe_util.py`, mã Pillow 12.3.0 và 13.0.0 |
| Máy kiểm | Windows 11, Python 3.12.15, uv 0.12.23, worktree `wt-T-058` |
| Ngày | 2026-10-20 |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: không lỗi Nghiêm trọng/Cao/Trung bình; 4 lỗi Thấp (LC-T058-1…4). Gộp được sau khi Chỉ Huy mở app thật xem mọi trang (yêu cầu 3 của phiếu). Điều kiện còn lại ràng buộc T-049 và lượt quét cuối Giai đoạn 3 (mục **Điều kiện**) |

## Tóm tắt (cho chủ dự án)

- **Nâng lên Pillow 13.0.0 là an toàn và nên gộp.** Gói được tải đúng từ kho chính thức (mã kiểm tra khớp từng file, do chính nhóm làm Pillow đóng gói), không kéo thêm thư viện nào, và **40 trong 41** lỗ hổng của bản cũ đã được vá. Tôi đã mở tận mã nguồn để thấy bản vá của các lỗ hổng chạm tới việc xử lý ảnh sắp làm (thu nhỏ JPEG, đọc EXIF, ảnh nhiều khung).
- **Còn 1 lỗ hổng mức trung bình chưa có bản vá**, nhưng nó chỉ xảy ra khi máy đặt một biến cấu hình đặc biệt của Pillow **và** phần mềm xuất ảnh sang dạng dữ liệu Arrow. Phần mềm không làm cả hai, nên hiện không bị ảnh hưởng. Bản cũ 12.3.0 cũng có lỗi này.
- Không có lỗi phải sửa trong phiếu này. Có 4 điểm ghi nhận mức Thấp, chủ yếu là những việc phiếu xử lý ảnh T-049 phải giữ (ví dụ: chỉ đưa lên màn hình ảnh mà app đã kiểm). Con số "53 lỗ hổng" tôi báo hôm 19/10, hôm nay trang của nhóm Pillow chỉ còn 41 (có thể họ gộp các báo cáo trùng); kết luận không đổi.
- Việc còn lại trước khi gộp: Chỉ Huy mở app thật xem mọi trang như phiếu yêu cầu. Nếu phải quay về Pillow 12.3.0 thì phải gọi lại Lá Chắn.

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

Thư viện C đóng sẵn trong wheel Pillow 13.0.0 (theo SBOM `pillow-13.0.0.dist-info/sboms/pillow-13.0.0.cdx.json` và `PIL.features`): libjpeg-turbo 3.2.0, libwebp 1.6.0, zlib-ng 2.3.3, Little CMS 2.19.1, libavif 1.4.2, OpenJPEG 2.5.4, libtiff 4.7.2, FreeType 2.14.3, HarfBuzz 14.5.0. Bản phát hành mới nhất trên GitHub của libjpeg-turbo, zlib-ng, Little-CMS, libavif, OpenJPEG (với libwebp: thẻ mới nhất `v1.6.0`) đều trùng bản trong wheel; các kho này không có khuyến cáo GitHub nào (libwebp, FreeType chỉ là bản sao trên GitHub, nơi công bố lỗi của họ chưa tra). OpenJPEG 2.5.4 là bản có lỗi OSV-2025-219 (GHSA-78g4-xqwv-q3g8), nhưng ghi chú phát hành 13.0.0 ghi Pillow đã vá thêm (`Apply uclouvain/openjpeg#1621 to address OSV-2025-219 #10156`). **Chưa tra NVD** cho các thư viện C này; libtiff (GitLab) chưa tra.

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
| GHSA-g7cr-3p24-7wf7 (cao, ghi JPEG có ICC + chú thích) | Ghi JPEG có kèm ICC. T-049 xuất WebP; `st.image` có ghi lại JPEG và tự chép chú thích, nhưng không chép ICC (`PIL/JpegImagePlugin.py:771` chỉ lấy ICC từ tham số lưu), nên đường này hầu như không chạy tới | `src/libImaging/JpegEncode.c:330-334` thẻ 13.0.0 thêm kiểm `comment_size + 5 > free_in_buffer` |
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
| LC-T058-3 | Thấp | Đường **quay về Pillow 12.3.0** (báo cáo Thợ Máy mục "Cách quay về", chú thích `pyproject.toml:37`) bảo xóa `tests/test_pillow_version_t058.py`, tức bỏ chốt chặn duy nhất giữ phiên bản. Khi T-058 đã gộp, T-049 được dùng `thumbnail()` vì điều kiện 5 không còn bắt buộc (Chỉ Huy A ghi trên `main`: "Nếu T-058 đã gộp thì điều kiện 5 … không còn bắt buộc"), nên quay về 12.x sau T-049 sẽ mở lại đường GHSA-8g5g | `docs/team/reports/T-058-tho-may.md:104-110`; `pyproject.toml:37` | App hỏng với Pillow 13 → quay về theo hướng dẫn, xóa test ghim bản → code T-049 gọi `thumbnail()` trên JPEG chạy trên 12.3.0 → JPEG dựng riêng trong thư mục Drive dùng chung → tràn heap GHSA-8g5g (có thể chạy mã trên máy chứa `.env`). Hướng dẫn có câu "phải theo lựa chọn B" nhưng không có gì tự chặn | (a) Quay về 12.x thì phải **mở lại kiểm định Lá Chắn** và áp lại điều kiện 5 của T-049 trước khi chạy app với ảnh thật. (b) Khuyên T-049: module ảnh từ chối xử lý ảnh khi `PIL.__version__` < 13 (một dòng kiểm lúc mở ảnh, có test), để quay về sai cách thì app báo lỗi thay vì chạy âm thầm |
| LC-T058-4 | Thấp | Ép phiên bản để lại 3 điểm cần nhớ: (1) `<14` sẽ chặn Pillow 14 dù sau này 14 mới có bản vá; (2) `uv pip check` luôn báo 1 xung đột nên dễ quen mắt, bỏ sót xung đột Pillow thật về sau; (3) pip-audit, OSV và kho khuyến cáo chung GitHub **chưa có** khuyến cáo Pillow tháng 10 (mục 2), nên "pip-audit sạch" chưa đủ làm bằng chứng | `pyproject.toml:38` | Không phải lỗ hổng; là rủi ro bảo trì: bản vá mới ra mà không ai nâng | Lượt quét cuối Giai đoạn 3 và mỗi lần đổi `uv.lock`: tra thẳng `gh api repos/python-pillow/Pillow/security-advisories`, xem Streamlit đã cho Pillow 13 chưa (cho rồi thì bỏ override, giữ `pillow>=13.0.0`), xem có Pillow 14 chưa. `uv pip check` chỉ được phép báo đúng dòng `streamlit … <13` |

Câu hỏi của Chỉ Huy "Streamlit gặp Pillow ngoài dải nó khai báo có mở ra lỗ bảo mật nào không": **không thấy lỗ mới.** Streamlit 1.65 chỉ dùng Pillow ở `image_utils.py` (`Image.open`, `fromarray`, `resize(BILINEAR)`, `save`) và ở băm `st.cache_data` (`runtime/caching/hashing.py:48`, `tobytes()` + `getpalette()`). Soi Lỗi đã chạy mọi nhánh này trên 13.0.0 với cảnh báo "sắp bỏ" đổi thành lỗi (60 test), kể cả hai ảnh khác bảng màu ra hai mã băm khác nhau (cache không nhầm ảnh). Ảnh rác vẫn ra `UnidentifiedImageError`, không treo. Chỗ đáng lưu ý duy nhất là LC-T058-2, có từ trước và không phụ thuộc phiên bản.

## Danh sách kiểm tra

Phiếu chỉ đổi `pyproject.toml`, `uv.lock`, thêm 2 file test và 2 báo cáo; **không đổi** `app/`, `seo_app/`, `scripts/`, `config/`, `.env.example`, `.gitignore`, `.streamlit/`, `run.*`, `tests/conftest.py`, `.claude/` (`git diff --stat origin/main...team/T-058 -- <các đường đó>` rỗng). Các dòng về WordPress, AI, đăng nhập vì vậy không áp dụng.

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets trên 6 file của diff (kể cả `uv.lock`): 0 kết quả. `git log -p origin/main..team/T-058` lọc `api[_-]?key\|password\|secret\|token`: 0 dòng. Quét mọi file git đang theo dõi: 1 kết quả ở `tests/test_config.py:34` (`"abcd efgh"`, mật khẩu giả có từ trước, ngoài diff) |
| S2 | Không áp dụng | Không đổi code ứng dụng, không thêm chỗ in lỗi. Ghi chú cho T-049: câu lỗi của Pillow 13 vẫn chứa đường dẫn file (`cannot identify image file '<đường dẫn>'`, như 12.3.0), nên điều kiện 1 của T-047 (báo một câu tiếng Việt cố định, không in đường dẫn hay câu lỗi gốc) vẫn giữ |
| S3 | Không áp dụng | Không có biến cấu hình mới; `.env.example` không đổi. `PILLOW_ALIGNMENT` là biến của Pillow, **không được** thêm vào `.env.example` hay cấu hình (LC-T058-1) |
| W1 | Không áp dụng | Không đổi code WordPress |
| W2 | Không áp dụng | Như trên |
| W3 | Không áp dụng | Như trên |
| W4 | Không áp dụng | Như trên |
| A1 | Không áp dụng | Không đổi prompt hay lớp AI |
| A2 | Không áp dụng | Như trên |
| A3 | Không áp dụng | Như trên. Bản ảnh gửi AI (không metadata) là việc của T-049 |
| U1 | Không áp dụng | Diff không có `unsafe_allow_html`, `st.markdown`, `st.html` (grep phần thêm của `tests/`: 0 dòng) |
| U2 | Đạt (không đổi) | `.streamlit/config.toml:5` vẫn `address = "localhost"`; không thêm trang. Test mới dựng trang tạm bằng `AppTest.from_function`, chạy trong tiến trình test, không mở cổng |
| U3 | Không áp dụng | Không đổi đăng nhập |
| F1 | Đạt (test) | Test mới chỉ ghi vào `tmp_path` (`tests/test_soi_loi_t058.py:285-287, 580-593, 617-628`); còn lại tạo ảnh trong bộ nhớ (`io.BytesIO`). Fixture `media_ra` (`:53-56`) chỉ đọc lại đúng file mà test đưa cho Streamlit. `ASSETS` (`:35`) là thư mục `app/assets` của repo. Code mở ảnh thật thuộc T-049 |
| F2 | Đạt (đã thử trên 13.0.0) | `Image.MAX_IMAGE_PIXELS` mặc định không đổi (89.478.485, `:610-613`); vượt giới hạn thì cảnh báo, vượt gấp đôi thì lỗi, áp cả PNG lẫn HEIC (`:616-641`); `DecompressionBombError` vẫn **không** là con của `OSError` (`:613`). Pillow 13 thêm kiểm bom ở `seek()` của MPO/DCX/Spider (mục 2). WebP kèm `exif=` giữ đúng **giá trị** GPS, lọc được số seri, tên chủ máy, MakerNote theo 2A (`:449-530`) |
| F3 | Đạt | Test mới không có `eval`, `exec`, `pickle`, `yaml.load`, `subprocess`; bandit chỉ báo `B101 assert`. File ảnh đọc/ghi dạng nhị phân (không cần `encoding`). Fixture `heif_dang_ky` (`:564-577`) trả lại bảng định dạng của Pillow sau mỗi test, không để HEIF đăng ký lọt sang test khác |
| D1 | Đạt | Không có gói mới (70 gói, chỉ Pillow đổi bản); nâng Pillow 13 bằng override do chủ dự án chốt 2026-10-20 (`CLAUDE.md`, Quyết định đã chốt). Nguồn PyPI chính thức, mã băm 69/69 khớp, wheel do kho `python-pillow/Pillow` đăng qua Trusted Publishing, file cài nguyên vẹn (mục 1). 40/41 khuyến cáo của 12.3.0 vá ở 13.0.0, đã thấy bản vá trong mã cho các mục chạm đường T-049 (mục 2). pip-audit 0 lỗ hổng, nhưng cơ sở dữ liệu của nó chưa có khuyến cáo tháng 10 (LC-T058-4). Còn GHSA-654x chưa vá, không có đường đi (LC-T058-1) |
| D2 | Đạt (không đổi) | `.gitignore` không đổi: `.env` (dòng 2), `.env.*` (3), `*service-account*.json` (5), `secrets/` (6), `.pytest_cache/`, `.ruff_cache/` (18-19), `*.sqlite`, `*.sqlite3` (23-24) |
| D3 | Đạt | Bộ chặn mạng `autouse` (`tests/conftest.py:18-19`) áp cho mọi test, kể cả 62 test mới; grep `requests`, `urllib`, `http`, `socket` trong 2 file test mới: 0 dòng. AppTest chạy trang trong tiến trình test. (Các lệnh tra PyPI, GitHub, OSV ở mục 1–2 là Lá Chắn tự chạy để kiểm, không nằm trong test) |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit 2.10.1 | `uv export --frozen --no-hashes --no-emit-project` → 69 gói ghim (có `pillow==13.0.0`, `pillow-heif==1.8.1`). Nguồn PyPI: `No known vulnerabilities found`. Nguồn OSV (`-s osv`): `No known vulnerabilities found`. Quét thẳng môi trường đã cài (`--path .venv/Lib/site-packages`): `No known vulnerabilities found` (bỏ qua `seo-app` vì là chính dự án) | Có. **Nhưng** cả ba nguồn đều chưa có khuyến cáo Pillow tháng 10 (cũng không báo gì cho 12.3.0), nên bằng chứng chính là tra thẳng kho Pillow (mục 2) |
| bandit 1.9.4 | `seo_app app scripts` (7.504 dòng): 1 mức Thấp, `B101 assert` ở `seo_app/storage/drafts.py:203` (có từ trước, ngoài diff). 2 file test mới (492 dòng): 94 `B101 assert`, không gì khác | Báo nhầm, xem dưới |
| detect-secrets 1.5.0 | 6 file của diff: 0. Mọi file git theo dõi: 1 (`tests/test_config.py:34`, giả, có từ trước). Lệnh `--all-files` đúng như `security.md` quét cả `.venv/` (không thuộc repo) và báo 126 file thư viện; đã chạy lại chỉ trên file git theo dõi | Có |
| Soát lịch sử git | 9 commit của nhánh (`origin/main..HEAD`): 0 dòng khớp. Toàn lịch sử (`git log -p --all`) lọc dạng khóa thật (`sk-ant-`, `sk-proj-`, `AIza…`, `BEGIN … PRIVATE KEY`, `ghp_`, `gho_`): 82 dòng, đều là khóa giả có chữ `khoa-gia`/`KhoaGia` của các phiếu trước (đã xác minh ở các biên bản trước), không dòng nào thuộc T-058. File từng được thêm khớp `.env`/`.json`/`.sqlite`/`.pem`/`.key`: chỉ `.claude/settings.json` (cấu hình, không bí mật) | Có |
| pytest (Windows) | **Lượt 1** (09:30–09:52, `uv run pytest -q`): `1 failed, 7231 passed, 11 skipped, 27 xfailed, 1 warning in 1334.73s (0:22:14)`. Hỏng: `tests/test_app.py::test_correct_password_opens_home_and_logout_works` → `RuntimeError: AppTest script run timed out after 30(s)` khi chuyển sang trang Cài đặt. Cùng lúc agent khác chạy pytest toàn bộ ở `wt-T-051` (thấy tiến trình khi kiểm), lượt chạy dài gần gấp đôi thường lệ (Soi Lỗi: 11 phút 39 giây). Chạy lại riêng test đó: `1 passed in 7.65s` (phần gọi mất 3,08 giây); cả `tests/test_app.py`: `5 passed in 25.75s`. Test Pillow/HEIC (`test_pillow_version_t058.py`, `test_soi_loi_t058.py`, `test_pillow_heif_setup.py`, `test_soi_loi_t047.py`): `81 passed in 45.28s`. **Lượt 2:** đang chạy | Có. Hỏng do máy quá tải (quá giới hạn 30 giây), không do Pillow: trang Cài đặt không dùng ảnh, chạy riêng qua ngay |
| ruff 0.16.10 | `uv run ruff check .` → `All checks passed!` | Có |
| Kiểm thêm (D1) | `uv lock --check` khớp; `uv sync --locked` không đổi gì; `uv pip check` đúng 1 xung đột cố ý (Streamlit `<13`); so mã băm lock với PyPI 69/69; chứng thực PyPI của wheel Windows; `RECORD` 121/121 (Pillow) và 27/27 (pillow-heif) | Có |

## Báo nhầm đã loại

- **bandit B101** (`assert`): cách viết test của pytest. Cảnh báo ở `seo_app/storage/drafts.py:203` có từ trước, không thuộc diff.
- **detect-secrets `--all-files`**: 126 file báo đều nằm trong `.venv/` hoặc thư mục cache (`.pytest_cache`, `.ruff_cache`, đều bị `.gitignore` chặn), là mã của thư viện (ví dụ một chuỗi bị nhận nhầm là khóa AWS trong `PIL/ImageFont.py`), không thuộc repo.
- **detect-secrets `tests/test_config.py:34`**: `"abcd efgh"` là mật khẩu giả trong test cấu hình, có từ trước.
- **`uv pip check` báo `streamlit requires pillow<13`**: cố ý, đúng quyết định của chủ dự án (override).
- **pytest lượt 1 hỏng `test_correct_password_opens_home_and_logout_works`**: quá giới hạn 30 giây của AppTest khi máy đang chạy song song bộ test của agent khác; chạy lại riêng qua trong 3 giây. Không liên quan Pillow (xem dòng pytest).

## Pillow-heif và thư viện HEIC (kiểm lại sau T-047)

`pillow-heif` 1.8.1 không đổi bản, vẫn nhận Pillow 13 (`Requires-Dist: pillow>=11.1.0`, thư viện C libheif 1.23.6, libde265 1.1.3 không đổi). Tra lại 2026-10-20: kho `bigcat88/pillow_heif` vẫn 2 khuyến cáo (đã vá ở < 1.7.0 và < 1.2.1), `strukturag/libheif` vẫn 74 (mới nhất 2026-10-05, vá ở 1.23.6), `strukturag/libde265` vẫn 13 (mới nhất 2026-09-14, vá ở 1.1.3); bản phát hành mới nhất của cả ba trùng bản đang dùng. Không có gì mới so với biên bản T-047. Test HEIC chạy trên Pillow 13: `tests/test_pillow_heif_setup.py`, `tests/test_soi_loi_t047.py`, phần HEIC của `tests/test_soi_loi_t058.py` đều qua.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

**1. Trước khi gộp T-058 vào `main` (Chỉ Huy):**
- Mở app thật (`uv run streamlit run app/main.py`) xem mọi trang, theo yêu cầu 3 của phiếu. Đây là điều kiện của phiếu, không phải lỗi bảo mật.
- Chạy `uv run pytest` trên Windows sau khi gộp; nếu lại có test AppTest quá 30 giây thì chạy lại khi máy rảnh (không agent nào khác đang chạy test) trước khi kết luận hỏng.

**2. Chép vào phiếu T-049 (Chỉ Huy), Lá Chắn sẽ kiểm khi kiểm định T-049:**
- **Điều kiện 5 của T-047** (tránh `thumbnail()`/`draft()`, `seek()`, ghi JPEG) **không còn bắt buộc** khi T-049 chạy trên Pillow 13.0.0: đã thấy bản vá trong mã (mục 2). Xác nhận ghi chú của Chỉ Huy A trên `main` (`docs/team/tickets/T-049-xu-ly-anh-webp-giu-gps.md:66`). Vẫn khuyên chỉ xử lý khung đầu của ảnh MPO (app không cần khung khác).
- **Điều kiện 1–4, 6, 7 của T-047 giữ nguyên, không nới vì đã lên 13**: bắt lỗi quanh cả `open` lẫn `load` gồm `(OSError, ValueError, Image.DecompressionBombError)`; kiểm dung lượng trước khi mở, đặt `MAX_IMAGE_PIXELS` rõ ràng, đổi `DecompressionBombWarning` thành lỗi; đăng ký HEIF một chỗ; luôn mở với `formats=["JPEG","PNG","WEBP","HEIF"]`. Lý do: các lớp này chặn cả những lỗ hổng chưa ai biết.
- **LC-T058-1 (GHSA-654x):** không xuất ảnh sang Arrow (`__arrow_c_array__`, `__arrow_c_schema__`, `Image.fromarrow`, đưa ảnh vào `pyarrow`), không đặt và không đọc `PILLOW_ALIGNMENT`. Đã có trong ghi chú Chỉ Huy A (`T-049…:66`).
- **LC-T058-2:** chỉ đưa vào `st.image` ảnh Pillow **đã mở qua hàm mở an toàn** của module ảnh, hoặc byte WebP/JPEG **do app tạo ra**; không bao giờ đưa đường dẫn hay byte gốc của file trong `IMAGE_FOLDERS` (Streamlit sẽ tự mở bằng Pillow không giới hạn định dạng). Áp cho cả phiếu giao diện xem trước ảnh của Giai đoạn 3. Có test.
- **LC-T058-3:** module ảnh từ chối xử lý ảnh khi Pillow < 13 (một dòng kiểm phiên bản, câu lỗi tiếng Việt cố định, có test), để nếu ai quay về 12.x mà quên điều kiện 5 thì app báo lỗi chứ không chạy âm thầm.
- (Từ Soi Lỗi, không phải bảo mật) ảnh 16 bit đưa vào `st.image` phải đổi về 8 bit hoặc `output_format="PNG"` (SL-T058-1).

**3. Nếu quay về Pillow 12.3.0** (báo cáo Thợ Máy mục "Cách quay về"): phải gọi lại Lá Chắn và chủ dự án ký chấp nhận rủi ro (lựa chọn B của phiếu), áp lại điều kiện 5 cho T-049 trước khi app mở ảnh thật (LC-T058-3).

**4. Lượt quét cuối Giai đoạn 3 (Lá Chắn), LC-T058-1 và LC-T058-4:**
- Tra thẳng `gh api repos/python-pillow/Pillow/security-advisories` (pip-audit/OSV có thể vẫn chưa có các mục tháng 10); có Pillow 13.0.1 (vá GHSA-654x hoặc mục mới) thì nâng.
- Xem Streamlit đã cho Pillow 13 chưa: cho rồi thì bỏ `override-dependencies`, giữ `pillow>=13.0.0`. Có Pillow 14 có bản vá thì xét nới `<14`.
- `uv pip check` chỉ được báo đúng một dòng `streamlit … pillow<13`.
- Tra NVD cho thư viện C trong wheel Pillow (libjpeg-turbo 3.2.0, libwebp 1.6.0, zlib-ng 2.3.3, Little CMS 2.19.1, libtiff 4.7.2), phiếu này chưa tra.

**5. Kiểm lại bằng Claude Fable sau 01/11** (biên bản này chạy tạm Opus 5.5).

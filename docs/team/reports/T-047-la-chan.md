# Biên bản bảo mật T-047 · Khai báo Pillow và pillow-heif

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **Claude Opus 5.5** (chạy tạm vì tài khoản không dùng được Fable, chủ dự án đã duyệt). **Sau 01/11 phải kiểm lại bằng Fable.** |
| Phiếu được kiểm | [T-047](../tickets/T-047-khai-bao-pillow-va-pillow-heif.md) |
| Phạm vi | diff `origin/main...team/T-047` tại `82b37ce` (6 file: `pyproject.toml`, `uv.lock`, 2 file test, 2 báo cáo) và wheel `pillow-heif 1.8.1` đã cài trong `.venv` |
| Ngày | 2026-10-19 (tra cứu trực tuyến 13:45–14:10 giờ Việt Nam, tức 06:45–07:10 UTC) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** |

## Tóm tắt (cho chủ dự án)

- **Phiếu này đạt.** Đúng 2 thư viện anh đã duyệt được thêm, tải từ kho chính thức PyPI, mã kiểm tra (mã băm) khớp từng file. Không thêm gói phụ nào khác. Thư viện C đi kèm để đọc ảnh iPhone (libheif, libde265) đều là bản mới nhất, mọi lỗ hổng đã công bố đều đã được vá ở các bản này. 5.643 test qua, không hỏng.
- **Có một việc phải xử lý trước khi app bắt đầu mở ảnh thật (phiếu T-049).** Hai ngày trước (17/10), nhóm làm Pillow công bố **53 lỗ hổng** của Pillow 12.3.0, trong đó có lỗi tràn bộ nhớ khi thu nhỏ ảnh JPEG. Bản vá chỉ có ở Pillow 13.0.0, mà Streamlit hiện chưa cho dùng bản 13. Công cụ quét tự động (pip-audit) **chưa thấy** các lỗi này vì cơ sở dữ liệu của nó chưa cập nhật. Hiện app chưa mở ảnh nào bằng Pillow, nên hôm nay chưa có nguy cơ thật; Pillow 12.3.0 cũng đã nằm sẵn trong máy từ trước (Streamlit tự kéo về), phiếu này không làm tình hình xấu đi. Nhưng T-049 không được gộp khi chưa xử lý xong việc này (xem mục Điều kiện).
- **Giấy phép:** bản cài sẵn của pillow-heif chịu giấy phép **GPLv2** (vì có kèm bộ nén x265). Anh chỉ dùng app trong nội bộ, không bán, không phát cho người ngoài, nên **không phát sinh nghĩa vụ gì**. Nếu sau này muốn phát hoặc bán phần mềm cho người khác thì phải xem lại (chi tiết ở mục Giấy phép).

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| 1 | **Trung bình** (thành **Cao, chặn** ở phiếu đầu tiên giải mã ảnh nếu vẫn dùng Pillow 12.x) | Pillow 12.3.0 bị 53 khuyến cáo bảo mật của chính kho `python-pillow/Pillow`, công bố 2026-10-17, khoảng ảnh hưởng `<= 12.3.0`, bản vá `13.0.0` (phát hành PyPI 2026-10-16 22:15 UTC). Gồm 1 mức nghiêm trọng, 14 mức cao. pip-audit (cả nguồn PyPI lẫn OSV) và kho khuyến cáo chung của GitHub (`/advisories?affects=pillow@12.3.0` trả 0) **chưa có** các khuyến cáo này. Streamlit 1.65.0 (trong lock) và 1.66.0 (mới nhất) đều khai báo `pillow<13,>=9.2.0`, nên `uv` không nâng được. Báo cáo Thợ Máy ghi "Pillow không có bản vá mới hơn" chỉ đúng trong giới hạn của Streamlit | `uv.lock:998` (`pillow 12.3.0`, có từ trước trên `main`); `pyproject.toml:14` | **Hiện tại không có đường đi:** app chưa gọi Pillow; `st.image` duy nhất (`app/main.py:38`) mở `logo.svg`, Streamlit đi nhánh SVG đọc chữ, không qua Pillow (`streamlit/elements/lib/image_utils.py:285`). **Từ T-049:** ảnh trong thư mục khai báo (USB, Drive dùng chung) → `Image.open(..., formats=["JPEG"])` → `thumbnail()` (tự gọi `draft()`) → JPEG "lossless" SOF3 hợp chuẩn làm libjpeg-turbo ghi quá bộ đệm heap (GHSA-8g5g-8vmr-9782, mức cao; khuyến cáo nói rõ `formats=["JPEG"]` **không** chặn được) → sập app hoặc có thể chạy mã trên máy đang chứa `.env` (khóa AI, mật khẩu WordPress). Các khuyến cáo khác chạm đường app: PNG eXIf chạy thời gian bậc hai (GHSA-g4qv-2jxx-769h), MPO `seek()` vượt chặn bom giải nén (GHSA-p8hx-v2p6-rp84) | Xem mục **Điều kiện**: nâng Pillow 13.0.0 (ép bằng `[tool.uv] override-dependencies` sau khi thử Streamlit, hoặc chờ Streamlit nới), hoặc chủ dự án chấp nhận rủi ro ghi sổ, kèm biện pháp tạm bắt buộc |
| 2 | Thấp | OSV (truy vấn theo commit `f81f28a` của thẻ `v1.23.6`) còn 2 mục OSS-Fuzz **chưa ghi commit sửa**: OSV-2020-2308 (đọc quá heap 1 byte trong `derive_collocated_motion_vectors`, mã libde265 chạy trong bài fuzz của libheif) và OSV-2023-1129 (đọc lỗi trong `HeifPixelImage::overlay`). Không có CVE/GHSA tương ứng còn mở. Trang báo lỗi OSS-Fuzz không tra được | thư viện C trong wheel | ảnh HEIC dựng riêng → giải mã → đọc quá bộ nhớ → có thể sập tiến trình. Lỗi overlay cùng loại với CVE-2026-32882 (vá ở 1.22.0) và đã được gia cố thêm ở 1.23.6; có khả năng mục OSV đã cũ nhưng **chưa xác minh** | Ghi nhận. T-049 bắt lỗi và giới hạn kích thước như mục 7; kiểm lại ở lượt quét cuối Giai đoạn 3 |
| 3 | Thấp | Bản cài sẵn (wheel) của pillow-heif chịu **GPLv2** do kèm x265; libheif, libde265 là LGPLv3; mã nguồn pillow-heif BSD-3 | `pillow_heif-1.8.1.dist-info/licenses/LICENSES_bundled.txt` dòng 1–26 | Không phải lỗ hổng. Rủi ro pháp lý chỉ phát sinh khi phát hoặc bán phần mềm kèm thư viện này cho người ngoài | Ghi vào sổ rủi ro như một lưu ý; xem mục Giấy phép |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `uvx detect-secrets scan` trên `pyproject.toml`, 2 file test, 2 báo cáo: `"results": {}`. `git log -p origin/main..team/T-047 \| grep -inE "api[_-]?key\|password\|secret\|token\|sk-\|AIza"`: không có dòng nào. `uv.lock` không chạy detect-secrets (toàn mã băm sha256 hợp lệ, báo nhầm hàng loạt); đã đọc diff bằng mắt: chỉ URL `files.pythonhosted.org` và mã băm |
| S2 | Không áp dụng | Không có code in lỗi hay log mới |
| S3 | Không áp dụng | Không có biến cấu hình mới |
| W1 | Không áp dụng | Không đụng WordPress |
| W2 | Không áp dụng | |
| W3 | Không áp dụng | |
| W4 | Không áp dụng | |
| A1 | Không áp dụng | Không đụng prompt |
| A2 | Không áp dụng | |
| A3 | Không áp dụng | |
| U1 | Không áp dụng | Không đụng giao diện |
| U2 | Không áp dụng | |
| U3 | Không áp dụng | |
| F1 | Không áp dụng | Test chỉ ghi vào `tmp_path` (`tests/test_pillow_heif_setup.py:45,57`, `tests/test_soi_loi_t047.py:186-189`). Code mở ảnh thật ở T-049 |
| F2 | Không áp dụng (điều kiện cho T-049) | Đã xác minh: `Image.MAX_IMAGE_PIXELS` của Pillow **có** áp cho ảnh HEIF: ảnh 400×300 với giới hạn 50.000 → `DecompressionBombError`; giới hạn 100.000 → chỉ `DecompressionBombWarning` (Pillow chỉ báo lỗi khi vượt gấp đôi). libheif có giới hạn riêng, `pillow_heif.options.DISABLE_SECURITY_LIMITS = False` (mặc định). Yêu cầu cho T-049 ở mục 7 |
| F3 | Đạt | Test dùng `write_bytes`, `json.loads`; tiến trình con chạy `[sys.executable, "-I", "-c", <script cố định>, <thư mục tạm>]`, không `shell=True`, có `timeout=120` (`tests/test_soi_loi_t047.py:191-195`). Không có `eval`, `pickle`, `yaml.load` |
| D1 | **Đạt có điều kiện** | Chủ dự án duyệt `pillow` (2026-10-16) và `pillow-heif` (2026-10-19), ghi trong `CLAUDE.md` và chú thích `pyproject.toml:12-16`. Lock chỉ thêm **một** khối `[[package]]` mới (`pillow-heif 1.8.1`, phụ thuộc duy nhất `pillow`); `pillow` không đổi bản. Mã băm khớp PyPI, pip-audit sạch, thư viện C đã đối chiếu (mục 4–5). Điều kiện: lỗi số 1 (Pillow 12.3.0) |
| D2 | Đạt | `.gitignore` không đổi trong diff; vẫn chặn `.env` (dòng 2), `.env.*` (3), `*service-account*.json` (5), `__pycache__/` (11), `.pytest_cache/` (18), `*.sqlite` (23) |
| D3 | Đạt | Bộ chặn mạng `autouse` (`tests/conftest.py:18-19`) áp cho mọi test; ảnh HEIC giả tạo trong `tmp_path`. Tiến trình con trong `test_heic_hong_khong_lam_sap_hay_treo_tien_trinh` nằm ngoài bộ chặn, nhưng script cố định chỉ đọc file `*.heic` trong thư mục tạm (`tests/test_soi_loi_t047.py:153-169`), không có lời gọi mạng |

## 1. Thư viện thêm vào (D1)

| Gói | Bản | Nguồn | Giấy phép (PyPI) | Mã băm trong `uv.lock` so với PyPI JSON API |
|---|---|---|---|---|
| `pillow-heif` | 1.8.1 (bản mới nhất, 2026-10-11) | `registry = "https://pypi.org/simple"`, trang dự án `github.com/bigcat88/pillow_heif` | BSD-3-Clause (mã nguồn) | **49/49 khớp**, 0 lệch (PyPI có 70 file; lock bỏ các wheel cp310/cp311/pypy vì dự án cần Python ≥ 3.12) |
| `pillow` | 12.3.0 (không đổi, có sẵn trên `main`) | PyPI, `github.com/python-pillow/Pillow` | MIT-CMU | **64/64 khớp**, 0 lệch |

- Toàn bộ `uv.lock`: 69 gói nguồn `pypi.org/simple`, 1 gói `editable = "."` (chính dự án); 1.141 URL đều ở `files.pythonhosted.org`.
- `uv lock --check`: `Resolved 70 packages`; `uv sync --locked --dry-run`: `Would make no changes` (môi trường đúng như lock).
- Phụ thuộc bắt buộc của `pillow-heif` theo PyPI: chỉ `pillow>=11.1.0`. Các gói khác chỉ thuộc nhóm tùy chọn `docs`, `tests`, `dev`, không cài.
- Wheel đã cài trên Windows: `INSTALLER = uv`; gồm `_pillow_heif.cp312-win_amd64.pyd`, `libheif`, `libde265`, `libx265`, `libgcc_s_seh`, `libstdc++`, `libwinpthread` (DLL có hậu tố băm của công cụ đóng gói).

## 2. Quét lỗ hổng gói Python (pip-audit)

```
$ uv export --format requirements-txt --frozen --no-hashes --no-emit-project -o <scratchpad>/t047-req.txt
(69 dòng ghim phiên bản)
$ uvx pip-audit --version
pip-audit 2.10.1
$ uvx pip-audit -r <scratchpad>/t047-req.txt --no-deps --desc off
No known vulnerabilities found
$ uvx pip-audit -r <scratchpad>/t047-req.txt --no-deps -s osv
No known vulnerabilities found
```

Đối chiếu thêm bằng tay (vì pip-audit chỉ thấy những gì cơ sở dữ liệu đã nhận):

| Nguồn | `pillow 12.3.0` | `pillow-heif 1.8.1` |
|---|---|---|
| OSV API `/v1/query` (PyPI) | `{}` | `{}` |
| Kho khuyến cáo chung GitHub (`ecosystem=pip`) | 0 | (không tra riêng) |
| **Khuyến cáo của chính kho dự án** (`gh api repos/<kho>/security-advisories`) | **53 khuyến cáo ảnh hưởng `<= 12.3.0`, vá ở 13.0.0** (lỗi số 1) | 2 khuyến cáo, đều đã vá: GHSA-ccw6-q225-c975 (`< 1.7.0`), GHSA-5gjj-6r7v-ph3x / CVE-2026-28231 (`< 1.2.1`) |

Các khuyến cáo Pillow chạm tới đường app sẽ dùng ở Giai đoạn 3: GHSA-8g5g-8vmr-9782 (tràn heap khi giải mã JPEG thu nhỏ qua `draft()`/`thumbnail()`, cao), GHSA-g7cr-3p24-7wf7 / CVE-2026-96778 (tràn heap khi **ghi** JPEG có ICC và chú thích, cao; app xuất WebP nên tránh được nếu không ghi JPEG), GHSA-g4qv-2jxx-769h / CVE-2026-96643 (PNG eXIf, cao, từ chối dịch vụ), GHSA-p8hx-v2p6-rp84 / CVE-2026-96636 (MPO/DCX `seek()` vượt chặn bom giải nén, trung bình), GHSA-4rm8-3hmm-39fg / CVE-2026-96641 (hành vi không xác định trong phép tính số nguyên, trung bình). Phần lớn các khuyến cáo còn lại nằm ở định dạng app không cần (TIFF, PDF, FPX, EPS, WMF, BMP, GIF, XBM, MSP, Spider…), loại được bằng cách giới hạn `formats`.

## 3. Thư viện C đi kèm wheel (pip-audit không quét)

Phiên bản thật lấy từ `pillow_heif.libheif_info()` trên máy Windows: libheif `1.23.6`, libde265 `1.1.3`, x265 `4.3+1-e9b8812`. Mã nguồn tương ứng theo `LICENSES_bundled.txt`: `strukturag/libheif` thẻ `v1.23.6` (commit `f81f28a`), `strukturag/libde265` thẻ `v1.1.3` (commit `ba62bf4`), `Multicorewareinc/x265` thẻ `4.3` (trỏ tới commit `e9b8812`, trùng chuỗi phiên bản).

| Thư viện | Bản mới nhất? | Nguồn đã tra (2026-10-19) | Kết quả |
|---|---|---|---|
| **libheif 1.23.6** | Có (phát hành 2026-10-05; GitHub Releases) | (a) 74 khuyến cáo của kho `strukturag/libheif`; (b) NVD, từ khóa `libheif`: 48 CVE; (c) OSV theo commit `f81f28a`; (d) OSV hệ Debian; (e) ghi chú phát hành v1.23.6 | Mọi khuyến cáo có khoảng ảnh hưởng kết thúc ở ≤ 1.23.5 và bản vá ≤ 1.23.6; 12 khuyến cáo mới nhất (2026-10-05, 4 mức cao) vá đúng ở 1.23.6. CVE mới nhất của NVD (CVE-2026-84444 … 84451, công bố 2026-09-18) vá ở ≤ 1.23.3. Các mục còn lại xử lý riêng ở bảng dưới. OSV Debian khớp 32 mục chỉ vì nhánh Debian cũ chưa vá; mọi mục đều đã vá ở bản Debian ≤ 1.23.4 (báo nhầm). OSV theo commit: 2 mục OSS-Fuzz chưa đóng (lỗi số 2) |
| **libde265 1.1.3** | Có (phát hành 2026-09-14) | (a) 13 khuyến cáo của kho `strukturag/libde265`; (b) NVD, từ khóa `libde265`: 67 CVE; (c) OSV theo commit `ba62bf4`: `{}` | Mọi khuyến cáo vá ở ≤ 1.1.3. CVE-2026-49346 (cao) và GHSA-x27c-jp65-g395 không ghi bản vá trên GitHub, nhưng ghi chú phát hành v1.1.0 liệt kê cả hai là đã vá. CVE mới nhất CVE-2026-88373 (NVD 2026-09-24, mô tả nêu commit `4d45a6b`): commit sửa `f8d3249` (2026-08-26, issue #534 đã đóng) **nằm trong** v1.1.3 (GitHub compare: v1.1.3 đi trước 29 commit, sau 0) |
| **x265 4.3** | Có (thẻ mới nhất trên bản sao GitHub) | (a) NVD, từ khóa `x265`: 3 CVE (2017, ảnh hưởng ≤ 2.5); (b) OSV theo commit `e9b8812`: `{}`; (c) khuyến cáo kho GitHub: 0 | Không có lỗ hổng đã biết cho 4.3. **Chưa xác minh** trên kho gốc của x265 (Bitbucket) và trình theo dõi lỗi của họ. x265 chỉ là **bộ nén**; app chỉ đọc HEIC, không ghi, nên đường này không chạy |
| MinGW runtime (`libgcc_s_seh`, `libstdc++`, `libwinpthread`) | — | Không tra | **Chưa xác minh** (thư viện chạy nền của trình biên dịch, không xử lý dữ liệu ảnh) |

Các khuyến cáo libheif không ghi rõ bản vá, đã xem từng mục:

| Khuyến cáo | Nội dung | Kết luận |
|---|---|---|
| GHSA-h27h-4hc4-5vf5 (khoảng ghi "none") | Con trỏ rỗng `m_iloc_box` khi hộp `hdlr` khác `pict` | **Đã vá ở 1.23.6**: đọc mã nguồn thẻ `v1.23.6`, `libheif/file.cc:619-623` luôn gán `m_iloc_box` hoặc trả lỗi `No_iloc_box`, không còn lối thoát sớm trước đó |
| GHSA-5hqq-636x-r3cr ("fixed version unknown") | Ghi quá heap trong API vùng mặt nạ `heif_region_*` | **Không chạm tới**: danh sách 116 hàm libheif trong `_pillow_heif.cp312-win_amd64.pyd` không có hàm `heif_region_*` nào. Lỗi cùng chỗ CVE-2026-84448 đã vá ở 1.23.2 |
| GHSA-wjj2-gjqj-5gr4 ("current master") | Tràn số khi đọc TIFF lát gạch trong `heif-enc` | **Không chạm tới**: là công cụ dòng lệnh, không có trong wheel |
| GHSA-vr5j-9r89-725x (`<= 1.23.4`, không ghi bản vá) | Tốn CPU ở bộ giải mã `unci` | Ngoài khoảng ảnh hưởng; ghi chú v1.23.6 mục Hardening ghi đã sửa |
| CVE-2025-29482 (NVD ghi "libheif 1.19.7", qua lỗi SAO của libde265) | Tràn bộ đệm SAO | libde265 đã vá lỗi SAO ở 1.1.1 (CVE-2026-54241); việc hai mã này cùng một lỗi **chưa xác minh** bằng commit |

Điểm cộng đã xác minh:
- File DLL libheif **không** chứa chuỗi `LIBHEIF_PLUGIN_PATH`: libheif không tự nạp plugin theo biến môi trường; plugin chỉ nạp khi code gọi `pillow_heif.load_libheif_plugin()`.
- `pillow_heif` gọi `heif_context_set_security_limits`; tùy chọn `DISABLE_SECURITY_LIMITS` mặc định `False`.

## 4. Giấy phép

| Thành phần | Giấy phép |
|---|---|
| Mã nguồn pillow-heif | BSD-3-Clause |
| libheif, libde265 | LGPLv3 |
| x265 | GPLv2 |
| MinGW runtime (chỉ Windows) | GPL-3.0 kèm ngoại lệ GCC, MIT, BSD |
| **Bản cài sẵn (wheel) nói chung** | **GPLv2** ("due to base library licenses", `LICENSES_bundled.txt` dòng 2) |

Đánh giá: GPL chỉ đặt nghĩa vụ khi **phân phối** phần mềm (phát, bán, cho tải về). App chạy nội bộ trên 2 máy của chủ dự án, không phân phối, nên **không có nghĩa vụ nào**. Ảnh WebP app tạo ra và bài đăng lên website không bị GPL ràng buộc.

Khuyến nghị cho chủ dự án nếu sau này phát phần mềm cho người khác (kể cả cho đối tác dùng thử):
1. Hoặc phát toàn bộ app theo GPLv2 và kèm mã nguồn (gồm mã nguồn libheif, libde265, x265 đúng bản);
2. Hoặc dựng bản pillow-heif **không có x265** (app chỉ cần đọc HEIC, không cần nén HEIC). Khi đó còn LGPLv3: được phát kèm nếu giữ thư viện ở dạng file riêng thay được, kèm văn bản giấy phép và nơi lấy mã nguồn;
3. Hỏi người có chuyên môn pháp lý trước khi phát. Lá Chắn không thay được tư vấn pháp lý.

## 5. `uv.lock` đổi `revision = 3` → `5`

- Do uv 0.12.23 (`46b84fd0b 2026-10-03`) ghi. Soi Lỗi đã thử uv 0.9.5 và 0.11.0: `uv lock --check` qua, uv 0.9.5 không ghi đè lại file.
- `run.bat:12` và `run.command:15` cài uv bản mới nhất từ `astral.sh` khi máy chưa có uv, nên máy mới không gặp vấn đề. Máy đang có uv cũ vẫn đọc được.
- Không phải vấn đề bảo mật. Khuyên Chỉ Huy dặn máy kia chạy `uv self update` để hai máy ghi lock giống nhau, tránh diff `revision` qua lại.

## 6. Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit 2.10.1 | 0 lỗ hổng (nguồn PyPI và OSV), 69 gói | Có. **Nhưng** pip-audit bỏ sót 53 khuyến cáo Pillow mới công bố (lỗi số 1) và không quét thư viện C (mục 3) |
| bandit | 18 cảnh báo mức Thấp: 16 `B101 assert` trong test và 1 ở `seo_app/storage/drafts.py:203` (có từ trước, ngoài diff); `B404`/`B603` ở tiến trình con của test | Báo nhầm, xem mục dưới |
| detect-secrets | `"results": {}` trên 5 file mới/sửa (trừ `uv.lock`) | Có |
| Soát lịch sử git | Không có dòng khớp trong 6 commit của nhánh | Có |
| pytest | `5643 passed, 11 skipped, 35 xfailed, 1 warning in 828.53s` (cảnh báo Pydantic ở `tests/test_soi_loi_t028.py`, có từ trước) | Có, chạy lại trên Windows |
| ruff | `All checks passed!` | Có |

## Báo nhầm đã loại

- **bandit B101** (`assert` trong test): `assert` là cách viết test của pytest. Cảnh báo ở `seo_app/storage/drafts.py:203` có từ trước, không thuộc diff phiếu này.
- **bandit B404/B603** (`tests/test_soi_loi_t047.py:191`): danh sách lệnh cố định (`sys.executable -I -c <script trong code>`), đối số duy nhất là thư mục tạm, không `shell=True`, có timeout.
- **OSV hệ Debian** khớp 32 CVE libheif và 2 CVE libde265: do nhánh Debian cũ chưa vá; mọi mục đều đã vá ở bản Debian ≤ 1.23.4 (libheif) và ≤ 1.1.2 (libde265), thấp hơn bản app dùng.
- **`uv.lock` với detect-secrets**: chuỗi sha256 hợp lệ, không chạy.

## 7. Những điểm phiếu T-049 (code mở ảnh) phải làm

Lá Chắn sẽ kiểm các điểm này khi kiểm định T-049:

1. **Bắt lỗi quanh cả `open` lẫn `load`:** gọi `Image.open(...)` **và** `image.load()` (hoặc thao tác giải mã đầu tiên) trong cùng một khối `try`, bắt ít nhất `(OSError, ValueError, Image.DecompressionBombError)`. `UnidentifiedImageError` là con của `OSError`; HEIC cắt cụt ném `ValueError` và chỉ nổ ở `load()` (Soi Lỗi đã tái hiện); **`DecompressionBombError` không phải con của `OSError`** nên phải ghi riêng. Báo người dùng một câu tiếng Việt cố định, không in đường dẫn đầy đủ hay câu lỗi gốc. Có test cho từng loại.
2. **Giới hạn dung lượng và số điểm ảnh, áp cho cả HEIC:** kiểm dung lượng file (`stat().st_size`) **trước** khi mở; đặt `Image.MAX_IMAGE_PIXELS` rõ ràng trong code và biến `DecompressionBombWarning` thành lỗi (Pillow chỉ báo lỗi khi vượt **gấp đôi** giới hạn), hoặc tự so `width * height` với giới hạn trước `load()`. Không bật `DISABLE_SECURITY_LIMITS` của pillow-heif. Có test với HEIC vượt giới hạn.
3. **Đăng ký HEIF một chỗ cố định:** gọi `pillow_heif.register_heif_opener()` đúng một lần trong module ảnh (ví dụ `seo_app/images/`), không gọi rải rác. Khuyên tắt phần không cần: `register_heif_opener(thumbnails=False, depth_images=False, aux_images=False)`. Không bao giờ gọi `load_libheif_plugin()`. Không ghi file HEIC (không cần bộ nén x265).
4. **Giới hạn định dạng:** luôn mở bằng `formats=["JPEG", "PNG", "WEBP", "HEIF"]` (hoặc danh sách chủ dự án duyệt). Cách này loại phần lớn 53 khuyến cáo Pillow.
5. **Khi còn dùng Pillow 12.x** (nếu chủ dự án chấp nhận rủi ro): không gọi `draft()` hay `thumbnail()` trên ảnh JPEG (đường GHSA-8g5g-8vmr-9782); không `seek()` sang khung thứ hai (đường MPO, GHSA-p8hx-v2p6-rp84); không ghi JPEG (GHSA-g7cr-3p24-7wf7), chỉ xuất WebP.
6. **Test "chưa đăng ký":** thay `pytest.skip` ở `tests/test_pillow_heif_setup.py:46-47` bằng fixture tự gỡ `HEIF` khỏi bảng định dạng (góp ý Soi Lỗi mục 3), để test không lặng lẽ bị bỏ qua khi module ảnh đăng ký HEIF lúc import.
7. Đường dẫn ảnh vẫn theo F1 (chỉ trong `IMAGE_FOLDERS`, chặn `..` và symlink); EXIF giữ GPS theo sổ rủi ro mục 6 và quyết định 2A.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

1. **Lỗi số 1 (Pillow 12.3.0), hạn: trước khi gộp phiếu đầu tiên giải mã ảnh bằng Pillow (T-049) vào `main`.** Chỉ Huy mở phiếu riêng (Thợ Máy) để chọn một trong hai đường:
   - **(a) Nâng Pillow lên 13.0.0** bằng `[tool.uv] override-dependencies = ["pillow>=13.0.0"]` (vượt ràng buộc `pillow<13` của Streamlit), sau đó chạy toàn bộ test và mở app thật thử các trang có `st.image`; Soi Lỗi và Lá Chắn kiểm. Không phải thêm thư viện mới, nhưng ép phiên bản trái khai báo của Streamlit nên Chỉ Huy cần báo chủ dự án. Hoặc chờ bản Streamlit cho phép Pillow 13 rồi nâng cả hai.
   - **(b) Chủ dự án chấp nhận rủi ro**, ghi vào `security.md` mục 6, kèm đủ biện pháp tạm ở mục 7 điểm 4–5.
   Nếu T-049 tới tay Lá Chắn mà chưa có (a) hoặc (b), T-049 sẽ **KHÔNG ĐẠT** (mức Cao: thư viện có lỗ hổng đã biết đang bị dùng tới).
2. **T-049 làm đủ mục 7 điểm 1–4 và 6**, có test.
3. **Lượt quét cuối Giai đoạn 3:** chạy lại pip-audit (lúc đó cơ sở dữ liệu đã có khuyến cáo Pillow), xem lại khuyến cáo mới của libheif/libde265/pillow-heif và 2 mục OSS-Fuzz ở lỗi số 2.
4. **Sau 01/11:** kiểm lại phiếu này bằng Fable.

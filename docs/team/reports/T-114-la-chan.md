# Biên bản bảo mật T-114 · Nâng `pyasn1` 0.6.4 → 0.6.5 (4 khuyến cáo mức High, LC-T078-3)

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem dòng trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | T-114 `T-114-nang-pyasn1.md` (bản trong thư mục nháp của Chỉ Huy, chưa lên `main`) · kiểm **rút gọn** (D1, D3, S1). Phiếu sinh từ LC-T078-3 ([Lá Chắn T-078](T-078-la-chan.md), nhánh `team/T-078`) |
| Phạm vi | diff `a416e74..1d29e60` (nhánh `team/T-114`, 3 file): `uv.lock` (chỉ khối `pyasn1`), `tests/test_pyasn1_version.py` (mới), báo cáo Thợ Máy. Kèm mã nguồn `pyasn1` 0.6.4 và 0.6.5, `pyasn1-modules`, `google-auth`, đường app dựng thông tin xác thực Google |
| Báo cáo đã đọc | [Thợ Máy](T-114-tho-may.md). Phiếu không cần Soi Lỗi |
| Ngày | 2026-10-31 (09:14–09:40, giờ máy +07) |
| **Kết luận** | **ĐẠT** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp. **LC-T078-3 đóng** (có hiệu lực trên máy sau khi gộp và mở app bằng `run.bat`). **Gộp vào `main` được ngay**: gộp thử với `main` cục bộ `3cdd096` không xung đột, test chọn lọc trên cây gộp 0 hỏng |

## Tóm tắt (cho chủ dự án)

- **Bản nâng an toàn, gộp được ngay.** File khóa thư viện chỉ đổi đúng `pyasn1`. Mã băm trỏ đúng file chính thức trên PyPI, tôi đối chiếu qua hai đường mạng độc lập.
- **Bản 0.6.5 vá đủ 4 lỗi và không có lỗi mới.** Ba nguồn dữ liệu lỗ hổng (PyPI, OSV, GitHub) đều sạch với bản mới; với bản cũ thì cả ba báo đủ 4 lỗi.
- **Tôi thử thật:** với bản cũ, dữ liệu dựng cố ý làm thời gian giải mã tăng theo bình phương (gấp đôi dữ liệu thì chậm gần gấp 4); với bản mới thì chỉ chậm gấp 2. Bản mới chỉ đổi đúng phần sửa lỗi, không thêm gì lạ.
- **Không ảnh hưởng chức năng Google.** Thư viện Google vẫn đọc khóa và chứng chỉ đúng từng byte. App vẫn không dùng tới `pyasn1` khi kết nối Google Sheets.

## Trả lời câu hỏi của Chỉ Huy

| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | `uv.lock` chỉ đổi `pyasn1`, mã băm và nguồn PyPI đúng? | **Đúng.** Mục «`uv.lock` và nguồn PyPI» |
| 2 | 0.6.5 vá đủ 4 khuyến cáo, không mang khuyến cáo mới? | **Đúng.** Cả 4 GHSA ghi bản vá 0.6.5; `affects=pyasn1@0.6.5`: 0; quét 69 gói bằng 3 nguồn: 0. Đo thời gian: 3/4 lỗi tái hiện được trên 0.6.4, hết trên 0.6.5 (mục «Bản 0.6.5 vá đủ») |
| 3 | `pyasn1-modules` / `google-auth` vẫn tương thích? | **Có.** `pyasn1-modules` 0.4.2 đòi `pyasn1<0.7.0,>=0.6.1`; giải mã rồi mã hóa lại PKCS#8, PKCS#1, X.509 trùng từng byte; test Google trên nhánh và cây gộp qua |
| 4 | Test mới không gọi mạng? | **Đúng.** Audit hook: 0 lần nối, 0 lần tra tên (D3) |
| 5 | LC-T078-3 đóng? | **Đóng** khi gộp; mỗi máy nhận bản mới khi mở app bằng `run.bat` / `run.command` |
| 6 | Gộp thử với `main` `3cdd096`? | Không xung đột; 273 qua, 0 hỏng (mục «Thử gộp») |

Trước khi dùng `uvx`, tôi đã kiểm `uv --version`: `uv 0.13.4` (LC-T078-1).

## Lỗi phát hiện

Không phát hiện lỗi.

## `uv.lock` và nguồn PyPI (D1)

| Kiểm | Kết quả | Bằng chứng |
|---|---|---|
| Chỉ đổi khối `pyasn1` | Đạt | `git diff a416e74..1d29e60 -- uv.lock`: 1 khối (`uv.lock:1196-1202`), 6 dòng (3 bớt, 3 thêm): `version`, `sdist`, `wheels`. Vẫn 70 gói. `pyproject.toml` không đổi |
| Khóa nhất quán | Đạt | `uv lock --check`: `Resolved 70 packages`, mã 0; `uv sync --locked`: `Checked 69 packages`, mã 0 |
| Mã băm, địa chỉ, cỡ khớp PyPI | Đạt | `pypi.org/pypi/pyasn1/0.6.5/json` qua **2 đường độc lập**: `curl` trên máy này, và công cụ đọc web chạy trên máy chủ khác (không qua mạng máy này). Cả hai trả giống hệt và khớp `uv.lock`. Wheel: `sha256:4017b0fce125096b8573b39c989fdb1a4b19cf761e683398184550fea0e66587`, 84807 byte, `files.pythonhosted.org/packages/19/1f/…`. Sdist: `sha256:6b11616a6bcf3a40e635f082bb232fa57b5e0dd7f517bd7ddd69ec3794508a47`, 155152 byte, `…/88/7e/…`. Tải lên 2026-10-27 06:32 UTC; không bị rút (`yanked: false`); `info.version` 0.6.5 là bản mới nhất |
| Bản đã cài đúng file | Đạt | `.venv` của nhánh: `pyasn1` 0.6.5 (cả `__version__` lẫn metadata); 39 file có mã băm trong RECORD, sai lệch 0 |
| Nguồn gói | Đúng | Chủ gói «pyasn1 maintenance organization», mã nguồn `github.com/pyasn1/pyasn1` (theo PyPI); chính 4 khuyến cáo GitHub ghi 0.6.5 là bản vá |
| Gói khác | Không đổi | `uv tree --invert --package pyasn1`: `pyasn1` ← `pyasn1-modules` 0.4.2 ← `google-auth` 2.62.0 ← app và `google-genai[requests]` 2.30.1; không gói nào đổi phiên bản theo |
| Không ghim trong `pyproject.toml` | Đồng ý với Thợ Máy | `uv.lock` đã ghim kèm mã băm; 2 test chốt bắt lùi bản (thử ngược ở mục D3). Cùng cách đã làm với `certifi` ở T-075. Đồng ý **không** dùng `override-dependencies`: cách này bỏ qua giới hạn `<0.7.0` của `pyasn1-modules`. Nếu sau này muốn ghim thì dùng `constraint-dependencies` |

## Bản 0.6.5 vá đủ, không mang khuyến cáo mới

**4 khuyến cáo** (kho GitHub, đọc 31/10; công bố 2026-10-30 23:03–23:07 UTC; chưa bị rút):

| GHSA | CVE | Mức | Bản bị ảnh hưởng → bản vá | Nội dung |
|---|---|---|---|---|
| GHSA-fm9c-5rcf-2q5p | CVE-2026-119194 | High | `>= 0.3.3, < 0.6.5` → 0.6.5 | Giải mã không khuôn, khối chứa nhiều thẻ dài khác nhau: CPU bậc hai |
| GHSA-9m75-vc3g-4x39 | CVE-2026-119195 | High | `<= 0.6.4` → 0.6.5 | OCTET STRING / chuỗi ký tự dựng từ nhiều mảnh, `ANY` độ dài bất định: chép lại bậc hai |
| GHSA-mm57-4v3p-rchx | CVE-2026-119197 | High | `<= 0.6.4` → 0.6.5 | REAL nhị phân phần định trị dài: CPU bậc hai |
| GHSA-2qm8-x737-gmw5 | CVE-2026-119196 | High | `<= 0.6.4` → 0.6.5 | BIT STRING dựng từ nhiều mảnh: dịch và chép lại bậc hai |

**Quét lại** (`pip-audit` 2.10.1 chạy bằng `uvx`, `uv` 0.13.4):

| Nguồn | `uv.lock` của nhánh (69 gói, bỏ điều kiện hệ điều hành) | Môi trường đã cài (`--path .venv\Lib\site-packages`) | Đối chứng 0.6.4 |
|---|---|---|---|
| PyPI | `No known vulnerabilities found`, mã 0; JSON: 69 gói, 0 bỏ qua, 0 lỗ hổng | 0, mã 0 (69 mục; `seo-app` bỏ qua vì không có trên PyPI) | Lá Chắn T-078: 4 (cùng 4 mã trên) |
| OSV | 0, mã 0; 69 gói, 0 bỏ qua | 0, mã 0 | Lá Chắn T-078: 4 |
| Kho khuyến cáo GitHub (`affects` = 69 `tên@phiên bản`) | reviewed 0, unreviewed 0, malware 0 | | `affects=pyasn1@0.6.4`: đúng 4 GHSA trên; `affects=pyasn1@0.6.5`: 0 |

Nghĩa là từ sáng nay tới lúc kiểm (09:20) không có khuyến cáo mới nào cho 69 gói của `uv.lock`.

**Mã nguồn 0.6.4 → 0.6.5** (so thư mục gói đã cài, bỏ `__pycache__`): chỉ 2 file đổi.
- `__init__.py`: số phiên bản.
- `codec/ber/decoder.py` (diff 224 dòng): đúng 4 chỗ vá.
  - BIT STRING: ghép mảnh vào `bytearray` (hàm `_appendFragment` mới), thay cho dựng lại cả chuỗi sau mỗi mảnh.
  - OCTET STRING, chuỗi ký tự, `ANY` độ dài bất định: gom mảnh vào danh sách rồi `b''.join`.
  - REAL: `int.from_bytes` thay vòng cắt từng byte.
  - Tập loại thẻ khi đoán SEQUENCE / SEQUENCE OF: giới hạn 2 phần tử.

Phần thêm vào không có lệnh nhập mới, không có `exec`, `eval`, `subprocess`, `socket`, `urllib`, `base64`, `pickle`, `open(`, `os.environ` (tìm trên các dòng `+` của diff: 0). Thay đổi hành vi duy nhất: OCTET STRING dựng từ mảnh lồng nhau nay ghép theo giá trị từng mảnh. Chỉ dạng BER mới có kiểu này; DER (khóa, chứng chỉ) không dùng nên không ảnh hưởng (mục tương thích).

**Đo thời gian giải mã dữ liệu dựng cố ý** (script nháp, dữ liệu trong bộ nhớ, `uv run --no-project --isolated --with pyasn1==…`; nhân đôi cỡ dữ liệu tới khi một lần đo quá 1 giây; máy đang chạy toàn bộ test nên số tuyệt đối chỉ để so):

| Ca | 0.6.4 | 0.6.5 |
|---|---|---|
| BIT STRING nhiều mảnh (GHSA-2qm8) | 16.000 mảnh (172 KB): 1,56 s; hệ số khi nhân đôi 2,2 → 2,9 → **3,4** | 128.000 mảnh (1,4 MB): 1,33 s; hệ số 2,2 → 2,0 → **1,9** |
| OCTET STRING nhiều mảnh (GHSA-9m75) | 64.000 mảnh (625 KB): 2,80 s; hệ số 2,4 → 2,5 → **5,5** | cùng cỡ: 1,16 s; hệ số 2,4 → 1,8 → **2,1** |
| REAL định trị 64 KB (GHSA-mm57) | 1,12 s; hệ số 2,6 → 3,8 → **3,5** | định trị 250 KB: **0,00 s** |
| Khối nhiều thẻ khác nhau (GHSA-fm9c) | Không tái hiện được: dữ liệu tôi dựng bị cả hai bản từ chối ngay (`PyAsn1Error`) | Dựa vào diff (tập loại thẻ giới hạn 2 phần tử) và khuyến cáo |

Hệ số gần 4 là bậc hai (lỗi), gần 2 là tuyến tính (đã vá). Ba lỗi tái hiện được đều hết trên 0.6.5.

## Tương thích `pyasn1-modules`, `google-auth`

| Kiểm | Kết quả |
|---|---|
| Ràng buộc | `pyasn1-modules` 0.4.2 khai `pyasn1<0.7.0,>=0.6.1`; `google-auth` 2.62.0 khai `pyasn1-modules>=0.2.1` (đọc metadata đã cài) |
| Giải mã và mã hóa lại (`pyasn1` 0.6.5 + `pyasn1-modules` 0.4.2, khóa RSA 2048 và chứng chỉ tự ký giả tạo trong bộ nhớ) | `rfc5208.PrivateKeyInfo` (PKCS#8), `rfc2437.RSAPrivateKey` (PKCS#1), `rfc2459.Certificate` (X.509): dư 0 byte, mã hóa lại **trùng từng byte**; thuật toán khóa `1.2.840.113549.1.1.1`. Đây là các khuôn `google-auth` dùng trong `_python_rsa.py` |
| Đường app (tiến trình riêng): dựng `Credentials.from_service_account_info` với khóa giả, nhập `seo_app.google.service_account`, `seo_app.google.sheets`, ký thử | Bộ ký `google.auth.crypt._cryptography_rsa`; **`pyasn1` không được nạp** (như Lá Chắn T-078). Gói `rsa` vẫn không có trong `uv.lock` |
| Test Google | Nhánh: `tests/test_pyasn1_version.py`, `tests/test_google_service_account.py`, `tests/test_certifi_version.py`: 65 qua, 3 bỏ qua. Cây gộp: thêm `tests/test_google_sheets.py`, `tests/test_t101_settings_google.py`: 273 qua, 3 bỏ qua. Thợ Máy: 25 file (Sheets, kế hoạch, cấu hình, trang app), 1637 qua |

## Test mới (D3)

| Kiểm | Kết quả |
|---|---|
| Không gọi mạng | `tests/test_pyasn1_version.py` chỉ đọc `uv.lock` (`tomllib`) và metadata gói đã cài. Chạy 3 file trên dưới audit hook (plugin pytest nháp, không commit): đúng 1 sự kiện, `socket.bind` vào `('::1', 0)` (cặp socket nội bộ trên Windows); **0** lần nối, **0** lần tra tên, 0 sự kiện ngoài `127.0.0.1`/`::1`. Bộ chặn mạng chung `tests/conftest.py` vẫn bật |
| Bắt được lùi bản | (a) bản cài 0.6.4 qua lớp phủ `--with pyasn1==0.6.4`, `uv.lock` vẫn 0.6.5: **1 hỏng** (`test_pyasn1_da_cai_tu_ban_da_va`), 1 qua. (b) `uv.lock` cũ (`git show a416e74:uv.lock`) cạnh bản sao file test, bản cài 0.6.5: **1 hỏng** (`test_uv_lock_khoa_pyasn1_tu_ban_da_va`), 1 qua. Mỗi test bắt đúng một kiểu lùi; `.venv` sau đó vẫn 0.6.5 |
| Mac/Linux | Chỉ dùng `pathlib`, `tomllib`, `importlib.metadata`, `packaging` (phụ thuộc của `pytest` trong `uv.lock`), đọc file `encoding="utf-8"`; không có gì riêng Windows (suy luận từ mã) |
| Thiết kế | Hai test coi như đạt khi `pyasn1` biến mất khỏi khóa hay khỏi máy (khi `google-auth` bỏ gói này): hợp lý, vì khi đó không còn bản lỗi nào để chặn |

## Thử gộp với `main`

- `main` cục bộ `3cdd096` (đã có T-102): `git merge-tree --write-tree main team/T-114` → **không xung đột** (cây `81af34c`). Từ `a416e74`, `main` không đổi `uv.lock`, `pyproject.toml`, `tests/conftest.py`, `seo_app/google/` hay test Google.
- Chạy thật: worktree tạm trong thư mục nháp (commit treo `c74e3f2`, không đẩy, đã gỡ), `uv sync --frozen`; kiểm `pyasn1` 0.6.5 và `seo_app` nạp từ chính worktree tạm.
  - Chạy 5 file: `tests/test_pyasn1_version.py`, `tests/test_google_service_account.py`, `tests/test_google_sheets.py`, `tests/test_t101_settings_google.py`, `tests/test_certifi_version.py`.
  - Kết quả: **273 passed, 3 skipped, 0 hỏng** (116,6 s, 09:32–09:35). 3 ca bỏ qua có từ trước, do Windows: symlink cần Developer Mode, không có quyền kiểu `chmod`.
  - `ruff`: sạch.
- `origin/main` vẫn ở `a416e74` (gốc nhánh). **Gộp được ngay.**

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` (đặt `PYTHONUTF8=1`) trên 3 file của diff: `results: {}`. Mồi khóa giả trong bản sao file test (có chữ tiếng Việt): bắt được 1; cùng file không đặt `PYTHONUTF8`: 0; đã xóa mồi. Soát 2 commit `a416e74..1d29e60`: chỉ có chữ «detect-secrets» trong báo cáo, không có khóa |
| S2 | Không áp dụng | Không đổi code |
| S3 | Không áp dụng | Không có biến cấu hình mới |
| W1 | Không áp dụng | Không đụng `seo_app/wordpress/` |
| W2 | Không áp dụng | Như W1 |
| W3 | Không áp dụng | Như W1 |
| W4 | Không áp dụng | Không đụng client mạng |
| A1 | Không áp dụng | Không đụng prompt |
| A2 | Không áp dụng | Như A1 |
| A3 | Không áp dụng | Như A1 |
| U1 | Không áp dụng | Không đụng `app/` |
| U2 | Không áp dụng | Như U1 |
| U3 | Không áp dụng | Như U1 |
| F1 | Không áp dụng | Không đọc/ghi file của người dùng |
| F2 | Không áp dụng | Không đụng ảnh |
| F3 | Đạt | Test đọc `uv.lock` bằng `tomllib`, `encoding="utf-8"`; không `eval`, `pickle` |
| D1 | Đạt | Không thư viện mới; chỉ nâng `pyasn1` (chủ dự án duyệt 31/10 «nâng ngay»); mã băm khớp PyPI; quét 3 nguồn sạch; mã nguồn bản mới chỉ có phần vá |
| D2 | Không áp dụng | `.gitignore` không đổi |
| D3 | Đạt | Mục «Test mới (D3)» |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit 2.10.1 (PyPI, OSV) | 0 trên `uv.lock` (69 gói) và trên `.venv` đã cài | Có: JSON đọc đúng 69 gói, `pyasn1` 0.6.5; đối chứng 0.6.4 ở T-078 ra 4 |
| Kho khuyến cáo GitHub | 0 (reviewed, unreviewed, malware); `pyasn1@0.6.5`: 0; `pyasn1@0.6.4`: 4 | Có |
| bandit | Không chạy | Phiếu không đổi mã Python của app (kiểm rút gọn D1, D3, S1) |
| detect-secrets (`PYTHONUTF8=1`) | 0 trên 3 file | Có (mồi) |
| Soát lịch sử git | Sạch (S1) | Có |
| pytest | Nhánh: 65 qua, 3 bỏ qua; cây gộp: 273 qua, 3 bỏ qua; thử ngược: mỗi test bắt một kiểu lùi bản. Máy đang chạy toàn bộ test trên `main` nên chỉ chạy chọn lọc; không có lần «timed out» | Có |
| ruff 0.16.10 | `All checks passed!` trên nhánh và trên cây gộp | Có |

## Báo nhầm đã loại

- Audit hook ghi `socket.bind(('::1', 0))`: cặp socket nội bộ Windows (asyncio), bộ chặn chung cho qua; không có lần nối.
- `pip-audit --path` ghi `seo-app` «bỏ qua»: đó là chính dự án, không có trên PyPI.
- Thời gian tuyệt đối trong bảng đo dao động vì máy bận; kết luận dựa vào hệ số khi nhân đôi cỡ dữ liệu.

## Điều kiện

Không có.

Việc sau khi gộp (không chặn gộp): mỗi máy mở app bằng `run.bat` / `run.command` để `uv sync` cài `pyasn1` 0.6.5. `.venv` của repo chính trên máy Windows hiện vẫn là 0.6.4 cho tới lúc đó; app không nạp gói này nên không có rủi ro trong lúc chờ.

## Đề xuất

- Gộp T-114 trước phiếu kế tiếp có đổi `uv.lock` (ví dụ T-111, `pillow-heif`), để biên bản của phiếu đó quét sạch (đồng ý với Thợ Máy).

## Nguồn đã đọc (chỉ đọc, không gọi WordPress, AI, Google)

- `pypi.org/pypi/pyasn1/0.6.5/json` (qua `curl` và qua công cụ đọc web chạy ngoài máy)
- Kho khuyến cáo GitHub qua `gh api` (`advisories/GHSA-…`; `affects` = 69 gói, `pyasn1@0.6.4`, `pyasn1@0.6.5`)

Script thử (đo thời gian, tương thích và đường nạp `pyasn1`, plugin audit hook) và diff mã nguồn 0.6.4 → 0.6.5 để ngoài repo, không commit; bản sao ở thư mục ghi chú chung `T-114-la-chan-scripts/`.

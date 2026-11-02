# Báo cáo T-114 · Nâng `pyasn1` 0.6.4 → 0.6.5 (4 khuyến cáo mức High, LC-T078-3)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-114](../tickets/T-114-nang-pyasn1.md) (LC-T078-3 của Lá Chắn T-078, nhánh `team/T-078`) |
| Ngày nộp | 2026-10-31 (giờ máy, +07) |
| Nhánh | `team/T-114`, tạo từ `origin/main` `a416e74`; commit thay đổi chính `134c9ab` |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Thư viện phụ `pyasn1` (đi kèm thư viện Google, dùng để đọc dữ liệu mã hóa dạng ASN.1) đã lên **bản 0.6.5**, vá 4 lỗi mức High công bố sáng 31/10. Với bản cũ, dữ liệu dựng cố ý có thể làm máy chạy rất lâu (treo app), nhưng không làm lộ gì. Lá Chắn đã thử: app hiện không đi tới phần bị lỗi. Nâng để các lần quét sau sạch và phòng khi sau này có đường dùng tới.
- Chỉ đúng thư viện này đổi: không sửa code của app, không đổi thư viện nào khác, giao diện không có gì khác. **Không cần sửa `pyproject.toml`** (lý do ở mục riêng bên dưới).
- Công cụ quét lỗ hổng (2 nguồn dữ liệu): bản cũ có 4 lỗi, bản mới **sạch**. Có thêm 2 test tự động: nếu sau này ai lỡ hạ về bản cũ, test sẽ báo hỏng.
- Sau khi Chỉ Huy gộp vào `main`: mở app bằng `run.bat` như mọi ngày, app tự cài bản mới trước khi mở.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `uv.lock` | Khối `pyasn1`: 0.6.4 → 0.6.5 (3 dòng: phiên bản, địa chỉ và mã băm của sdist, của wheel). Không gói nào khác đổi, vẫn 70 gói |
| `tests/test_pyasn1_version.py` | Mới, 2 test, không gọi mạng: (1) `uv.lock` khóa `pyasn1` từ 0.6.5 trở lên; (2) bản đang cài từ 0.6.5 trở lên. Nếu sau này `google-auth` bỏ hẳn `pyasn1` thì cả hai coi như đạt (không còn gì để vá) |
| `docs/team/reports/T-114-tho-may.md` | Báo cáo này |

Không đụng `pyproject.toml`, `seo_app/`, `app/`, `config/`, test cũ.

```
$ git diff --stat a416e74 -- uv.lock tests/ pyproject.toml
 tests/test_pyasn1_version.py | 33 +++++++++++++++++++++++++++++++++
 uv.lock                      |  6 +++---
 2 files changed, 36 insertions(+), 3 deletions(-)

$ git diff a416e74 -- uv.lock
@@ -1194,11 +1194,11 @@ wheels = [

 [[package]]
 name = "pyasn1"
-version = "0.6.4"
+version = "0.6.5"
 source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/a4/9a/23310166d960def5897e91fe20e5b724601b02a22e84ba1f94232c0b7f67/pyasn1-0.6.4.tar.gz", hash = "sha256:9c447d8431c947fe4c8febc4ed9e760bc29011a5b01e5c74b67025bd9fb8ce81", size = 151262, upload-time = "2026-07-09T01:12:33.988Z" }
+sdist = { url = "https://files.pythonhosted.org/packages/88/7e/3c0da41061a2021cac7cd524fd57092adbe5b515e8bf9005702e366802e2/pyasn1-0.6.5.tar.gz", hash = "sha256:6b11616a6bcf3a40e635f082bb232fa57b5e0dd7f517bd7ddd69ec3794508a47", size = 155152, upload-time = "2026-10-27T06:32:49.125Z" }
 wheels = [
-    { url = "https://files.pythonhosted.org/packages/9a/3b/6163796d69c3977d1e4287bea4a6979161cbbdd170ebb430511e8e1999ce/pyasn1-0.6.4-py3-none-any.whl", hash = "sha256:deda9277cfd454080ec40b207fb6df82206a3a2688735233cdcd8d3d565f088b", size = 84410, upload-time = "2026-07-09T01:12:32.92Z" },
+    { url = "https://files.pythonhosted.org/packages/19/1f/3eefd5c84c35cae44549ce1c7f7e58f7945b34f5a6bce07a135438522073/pyasn1-0.6.5-py3-none-any.whl", hash = "sha256:4017b0fce125096b8573b39c989fdb1a4b19cf761e683398184550fea0e66587", size = 84807, upload-time = "2026-10-27T06:32:48.045Z" },
 ]
```

## Thông tin phiên bản

| Gói | Trước | Sau | Ghi chú |
|---|---|---|---|
| `pyasn1` | 0.6.4 (PyPI 2026-07-09) | **0.6.5** (PyPI, tải lên 2026-10-27 06:32 UTC) | Bản mới nhất: `uv lock --upgrade-package pyasn1 --dry-run` → `No lockfile changes detected` |
| `pyasn1-modules` | 0.4.2 | 0.4.2 | Khai báo `pyasn1<0.7.0,>=0.6.1`, nên 0.6.5 hợp lệ |
| `google-auth` | 2.62.0 | 2.62.0 | Đòi `pyasn1-modules>=0.2.1` |

Chuỗi phụ thuộc (`uv tree --invert --package pyasn1`): `pyasn1` ← `pyasn1-modules` 0.4.2 ← `google-auth` 2.62.0 ← `seo-app` và `google-genai[requests]` 2.30.1. App không nhập `pyasn1` (`grep` trong `seo_app/`, `app/`, `scripts/`, `config/`, `tests/` trước phiếu: 0 kết quả). Trong cả `.venv`, chỉ `google/auth/crypt/_python_rsa.py` nhập nó, và file này cần gói `rsa`, mà gói này không có trong `uv.lock` (khớp Lá Chắn T-078).

## Mã khuyến cáo

| GHSA | CVE | Bản bị ảnh hưởng đang khóa | Bản vá |
|---|---|---|---|
| GHSA-fm9c-5rcf-2q5p | CVE-2026-119194 | 0.6.4 | 0.6.5 |
| GHSA-9m75-vc3g-4x39 | CVE-2026-119195 | 0.6.4 | 0.6.5 |
| GHSA-2qm8-x737-gmw5 | CVE-2026-119196 | 0.6.4 | 0.6.5 |
| GHSA-mm57-4v3p-rchx | CVE-2026-119197 | 0.6.4 | 0.6.5 |

Ghép mã CVE ↔ GHSA lấy từ trường `aliases` trong `pip-audit -f json`; nguồn PyPI và nguồn OSV cho đúng 4 cặp này. Nội dung lỗi theo Lá Chắn T-078: giải mã ASN.1 (BER/CER/DER) dựng cố ý làm CPU chạy lâu theo bình phương cỡ dữ liệu (treo, không lộ dữ liệu); GitHub xếp High.

## Có cần ghim bản tối thiểu trong `pyproject.toml` không?

**Đề xuất: không ghim** (không sửa `pyproject.toml`). Lý do:

1. **`uv.lock` đã khóa đúng 0.6.5, kèm mã băm.** `uv sync` (chạy trong `run.bat`) cài đúng bản này. `uv lock` không có `--upgrade` thì giữ nguyên bản đã khóa (`uv lock --check` đạt), và không gói nào đòi `pyasn1<0.6.5`. Chỉ khi có người cố ý ra lệnh hạ bản thì mới lùi về bản lỗi.
2. **Mọi cách ghim đều làm `uv.lock` đổi thêm ngoài khối `pyasn1`**, trái yêu cầu 1. Tôi thử từng cách trên **bản sao** `pyproject.toml` + `uv.lock` trong thư mục nháp, không đụng repo:

| Cách ghim | `uv.lock` đổi thêm | Nhược điểm |
|---|---|---|
| `[tool.uv] constraint-dependencies = ["pyasn1>=0.6.5"]` | 1 dòng `constraints = [...]` trong `[manifest]` | Nhẹ nhất; vẫn tôn trọng giới hạn của gói khác (thử ép `==0.6.0`: uv tự hạ `pyasn1-modules` về 0.4.1 cho khớp) |
| Khai báo `"pyasn1>=0.6.5"` trong `dependencies` | 2 dòng (phụ thuộc và `requires-dist` của `seo-app`) | Trái quy ước của `pyproject.toml` là chỉ ghi gói app dùng trực tiếp (app không nhập `pyasn1`); nếu `google-auth` bỏ `pyasn1` thì gói vẫn bị cài thừa |
| Thêm `"pyasn1>=0.6.5"` vào `override-dependencies` | Mục override mới trong `[manifest]` | **Bỏ qua giới hạn của gói khác**: thử ép `==0.6.0` thì uv nhận 0.6.0 dù `pyasn1-modules` 0.4.2 đòi `>=0.6.1`. Sau này nó cũng bỏ qua `<0.7.0`, có thể kéo bản 0.7 không tương thích. Không nên dùng |

3. **Test mới chặn lùi bản.** Lượt toàn bộ test của Chỉ Huy sẽ hỏng nếu `uv.lock` hay `.venv` về dưới 0.6.5. Đây là cùng cách làm với `certifi` ở T-075 (không ghim, có test chốt; Lá Chắn ĐẠT).

Nếu Chỉ Huy hay Lá Chắn vẫn muốn ghim: dùng `constraint-dependencies` (dòng đầu bảng), kèm chú thích tiếng Việt; không dùng `override`.

## Kết quả quét khuyến cáo (`pip-audit`)

`pip-audit` 2.10.1 chạy bằng `uvx` trong thư mục nháp của phiên (không thêm vào thư viện của dự án), quét theo hai cách, mỗi cách qua cả nguồn PyPI và nguồn OSV:

- **(a) Trên `uv.lock`:** đủ **69 gói ghim** (`uv export --frozen --no-hashes --no-emit-project --format requirements-txt`, rồi `--disable-pip --no-deps`). Đối chứng: `uv.lock` gốc lấy bằng `git show a416e74:uv.lock` (cùng `pyproject.toml`). Hai danh sách ghim chỉ khác đúng một dòng: `pyasn1==0.6.4` → `pyasn1==0.6.5`.
- **(b) Trên môi trường đã cài** (`--path .venv/Lib/site-packages`), đúng chữ «trên môi trường mới» của phiếu. Đối chứng: `.venv` của repo chính (còn 0.6.4). Đã kiểm bằng `-f json` rằng lượt này đọc đúng `.venv` được chỉ: liệt kê `pyasn1` 0.6.5 ở worktree, 0.6.4 ở repo chính. Kết quả gồm 69 mục = 68 gói + `seo-app` (chính dự án; nguồn PyPI ghi «bỏ qua» vì không có trên PyPI). Gói còn lại của lock, `httpx2-jsfetch`, chỉ cài cho Python chạy trong trình duyệt (`sys_platform == 'emscripten'`), nên không có trên Windows. Mọi gói đã cài khớp phiên bản trong `uv.lock`.

```
# (a) uv.lock
$ uvx pip-audit -r req.txt --disable-pip --no-deps -s pypi        # uv.lock MỚI
No known vulnerabilities found                                      (mã thoát 0)
$ uvx pip-audit -r req.txt --disable-pip --no-deps -s osv         # uv.lock MỚI
No known vulnerabilities found                                      (mã thoát 0)

$ uvx pip-audit -r req-old.txt --disable-pip --no-deps -s pypi    # uv.lock CŨ (đối chứng)
Found 4 known vulnerabilities in 1 package
Name   Version ID              Fix Versions
------ ------- --------------- ------------
pyasn1 0.6.4   CVE-2026-119196 0.6.5
pyasn1 0.6.4   CVE-2026-119194 0.6.5
pyasn1 0.6.4   CVE-2026-119197 0.6.5
pyasn1 0.6.4   CVE-2026-119195 0.6.5                               (mã thoát 1)
$ uvx pip-audit -r req-old.txt --disable-pip --no-deps -s osv     # uv.lock CŨ (đối chứng)
Found 4 known vulnerabilities in 1 package
Name   Version ID              Fix Versions
------ ------- --------------- ------------
pyasn1 0.6.4   CVE-2026-119196 0.6.5
pyasn1 0.6.4   CVE-2026-119195 0.6.5
pyasn1 0.6.4   CVE-2026-119194 0.6.5
pyasn1 0.6.4   CVE-2026-119197 0.6.5                               (mã thoát 1)

# (b) môi trường đã cài
$ uvx pip-audit --path D:/ProMetal-ToolSEO/wt-T-114/.venv/Lib/site-packages -s osv     # MỚI
No known vulnerabilities found                                      (mã thoát 0; nguồn PyPI: cũng 0, mã 0)
$ uvx pip-audit --path <.venv của repo chính> -s pypi | -s osv                        # CŨ (đối chứng)
4 lỗ hổng, đều ở pyasn1 0.6.4, cùng 4 mã trên                       (mã thoát 1, cả hai nguồn)
```

- Mã thoát lấy bằng `${PIPESTATUS[0]}` (Git Bash), là mã của chính `pip-audit`.
- Cảnh báo duy nhất của công cụ (đã lọc khỏi khối trên): khuyên dùng mã băm khi chạy `--no-deps`. Không ảnh hưởng kết quả; `uv.lock` vẫn giữ mã băm và `uv sync` kiểm mã băm khi cài.

## Bằng chứng

```
$ uv lock --upgrade-package pyasn1          # máy Windows 11, uv 0.13.4
Using CPython 3.12.15
Resolved 70 packages in 2.67s
Updated pyasn1 v0.6.4 -> v0.6.5

$ uv lock --check
Resolved 70 packages in 2ms
$ uv sync
 + pyasn1==0.6.5
 + pyasn1-modules==0.4.2
(worktree mới nên cài đủ 69 gói; cảnh báo duy nhất: không tạo được hardlink, uv chép file thay thế)
$ uv run python -c "…"                      # pyasn1.__version__, metadata
pyasn1 0.6.5 0.6.5 | pyasn1-modules 0.4.2 | google-auth 2.62.0

$ uv run pytest tests/test_pyasn1_version.py -v
2 passed
# Đối chứng: cùng file test + tests/conftest.py chép vào thư mục nháp, cạnh uv.lock gốc
# (git show a416e74:uv.lock), chạy bằng Python của .venv repo chính (pyasn1 0.6.4),
# PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider (không ghi gì vào repo chính):
2 failed   (AssertionError: [<Version('0.6.4')>] và assert <Version('0.6.4')> >= <Version('0.6.5')>)

$ uv run pytest <25 file dưới đây> -q -rfEs
1637 passed, 3 skipped, 2 xfailed in 619.21s (0:10:19)
(0 hỏng. Máy đang chạy song song toàn bộ test trên main. Mã băm uv.lock (22149b8a…) và file
 test (262acee5…) trùng nhau lúc đầu, lúc cuối lượt chạy và trùng bản đã commit 134c9ab)

$ uv run ruff check .                       # ruff 0.16.10
All checks passed!

$ uv pip check
Found 1 incompatibility
The package `streamlit` requires `pillow>=7.1.0,<13`, but `13.0.0` is installed
(có từ T-058, cố ý; không có gì về pyasn1)

$ PYTHONUTF8=1 uvx detect-secrets scan tests/test_pyasn1_version.py uv.lock
results: {}                                 (uv.lock gốc, cùng lệnh: cũng {})
```

**25 file test chọn lọc**, gồm nhóm T-097, T-100, T-101 (T-109 chưa có test trên `main`):

| Nhóm | File |
|---|---|
| Thư viện | `test_pyasn1_version.py` (mới), `test_certifi_version.py` |
| Google Sheets | `test_google_service_account.py`, `test_google_sheets.py`, `test_la_chan_t097.py`, `test_soi_loi_t097.py` |
| Kế hoạch | `test_plan_ai.py`, `test_plan_cache.py`, `test_plan_model.py`, `test_plan_parse.py`, `test_plan_propose.py`, `test_plan_sync.py`, `test_t100_drafts_plan.py`, `test_t100_google_identity.py`, `test_la_chan_t100.py`, `test_soi_loi_t100.py`, `test_t103_plan_prompt.py` |
| Cấu hình | `test_config.py`, `test_config_tolerance.py` |
| Trang app | `test_app_pages.py`, `test_t101_home_page.py`, `test_t101_plan_page.py`, `test_t101_settings_google.py`, `test_la_chan_t101.py`, `test_soi_loi_t101.py` |

- 3 mục bỏ qua có từ trước, do Windows: `test_google_service_account.py:180` (×2, tạo symlink cần Developer Mode), `:299` (Windows không có quyền kiểu `chmod`).
- 2 `xfail` có từ trước, đều ở `test_la_chan_t101.py` (LC-T101-1, `strict=True`, sửa ở T-102).

**Kiểm nhanh thêm (một lần, không commit):** `pyasn1` 0.6.5 cùng `pyasn1-modules` 0.4.2 giải mã được khóa PKCS#8 (qua `pem.readPemBlocksFromFile` với 2 dấu PKCS#1/PKCS#8) và chứng chỉ X.509, đúng các lệnh `google-auth` gọi (`_python_rsa.py:179-188`, `:118`): thuật toán `1.2.840.113549.1.1.1`, 0 byte dư. Khóa và chứng chỉ là đồ giả tạo trong bộ nhớ bằng `cryptography`, không ghi ra file.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: `uv lock --upgrade-package pyasn1` trên Windows, `uv` 0.13.4; `uv.lock` chỉ đổi khối `pyasn1` (diff ở mục Đã thay đổi); `pyproject.toml` không đổi (đề xuất và lý do ở mục riêng) (commit `134c9ab`)
- [x] Yêu cầu 2: `uv sync`; 25 file test chọn lọc 1637 passed, 0 hỏng; `uv run ruff check .` sạch
- [x] Yêu cầu 3: `pip-audit` trên `uv.lock` và trên môi trường đã cài, nguồn PyPI và OSV: không còn mục `pyasn1` (bản cũ: 4 mục)
- [x] Yêu cầu 4: báo cáo ghi cũ → mới, mã khuyến cáo, cách kiểm
- [x] D1: không thêm thư viện, chỉ nâng `pyasn1` (chủ dự án duyệt 31/10). D3: test mới chỉ đọc file trên máy, chạy dưới bộ chặn mạng tự động (`tests/conftest.py`). S1: diff không có bí mật (`detect-secrets` với `PYTHONUTF8=1`: 0)
- [x] Báo cáo nộp tại `docs/team/reports/T-114-tho-may.md`
- [ ] Toàn bộ `uv run pytest` trên Windows: việc của Chỉ Huy khi gộp

## Cách quay về nếu hỏng

**Dấu hiệu hỏng:** sau khi gộp, trang Kế hoạch hay Cài đặt → Google báo lỗi khi đọc khóa tài khoản dịch vụ hoặc kết nối Google Sheets, mà trước đó thì không. Khả năng rất thấp (suy luận): app dựng xác thực Google bằng `cryptography`, không nạp `pyasn1` (Lá Chắn T-078); 0.6.5 là bản vá nhỏ cùng dòng 0.6.x và vẫn giải mã được khóa, chứng chỉ (kiểm nhanh ở trên).

**Quay về nghĩa là mở lại 4 lỗ hổng**: chỉ làm khi app hỏng thật, và báo Lá Chắn ngay.

1. `git revert 134c9ab` (bỏ commit đổi `uv.lock` và test chốt; báo cáo giữ lại), rồi `uv sync` hoặc mở lại `run.bat`.
2. Hoặc làm tay: `uv lock --upgrade-package "pyasn1==0.6.4"` (đã thử `--dry-run`: `Update pyasn1 v0.6.5 -> v0.6.4`), `uv sync`, xóa `tests/test_pyasn1_version.py`, chạy `uv run pytest`.

## Rủi ro và điểm cần chú ý

- **Mỗi máy chỉ có bản mới sau `uv sync`.** `run.bat` (dòng 25) và `run.command` (dòng 26) chạy `uv sync` trước khi mở app.
- **Hai test chốt coi như đạt khi không còn `pyasn1`** (nếu `google-auth` sau này bỏ hẳn gói này). Cố ý, để test không hỏng oan khi nâng `google-auth`. Lượt đối chứng cho thấy cả hai đều bắt được bản 0.6.4.
- `pip-audit` chỉ biết các khuyến cáo đã có trong cơ sở dữ liệu lúc quét (31/10, khoảng 08:55).
- Kiểm gộp: `origin/main` vẫn ở `a416e74` (gốc nhánh); `git merge-tree --write-tree origin/main team/T-114`: không xung đột.

## Đề xuất

- Lá Chắn rút gọn (D1, S1): quét lại `pip-audit` trên nhánh `team/T-114`.
- Nên gộp T-114 **trước** phiếu kế tiếp có đổi `uv.lock` (ví dụ T-111, `pillow-heif`) để biên bản của phiếu đó quét sạch, như Lá Chắn T-078 khuyên.

## Câu hỏi cho chủ dự án

Không có.

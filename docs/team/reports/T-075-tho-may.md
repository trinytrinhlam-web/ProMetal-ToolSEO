# Báo cáo T-075 · Nâng `certifi` lên 2026.10.19 (GHSA-6q48-6c7w-9gw2)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-075](../tickets/T-075-nang-certifi.md) (LC-T061-1 của [Lá Chắn T-061](T-061-la-chan.md), mức Cao) |
| Ngày nộp | 2026-10-21 (giờ máy, +07) |
| Nhánh | `team/T-075`, tạo từ `main` `ddb9beb`; commit thay đổi chính `ca112a0` |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Thư viện `certifi` (danh sách «cơ quan cấp chứng chỉ» mà app tin khi kết nối website suachuacuasat.com và Gemini) đã lên **bản 2026.10.19**. Bản mới bỏ đúng **một** cơ quan bị lộ khóa (emSign ECC Root CA - G3); không thêm, không bỏ cơ quan nào khác, nên các kết nối đang chạy được vẫn chạy như cũ.
- Chỉ đúng thư viện này đổi: không sửa code của app, không đổi thư viện nào khác, giao diện không có gì khác.
- Công cụ quét lỗ hổng (2 nguồn dữ liệu): bản cũ bị báo 1 lỗ hổng, bản mới **sạch**. Có thêm 4 test tự động: nếu sau này ai lỡ hạ về bản cũ, test sẽ báo hỏng.
- Sau khi Chỉ Huy gộp vào `main`: mỗi máy chỉ cần mở app bằng `run.bat` (Windows) hoặc `run.command` (Mac) như mọi ngày, app tự cài bản mới trước khi mở. Lời dặn «không dùng Wi-Fi công cộng» chỉ bỏ khi cả 2 máy đã mở app lại và Lá Chắn xác nhận.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `uv.lock` | Khối `certifi`: 2026.7.22 → 2026.10.19 (3 dòng: phiên bản, địa chỉ và mã băm của sdist, của wheel). Không gói nào khác đổi, vẫn 70 gói |
| `tests/test_certifi_version.py` | Mới, 4 test, không gọi mạng: (1) `certifi` đã cài ≥ 2026.10.19 (so bằng `Version`, `__version__` khớp metadata); (2) file `certifi.where()` không còn nhãn «emSign ECC Root CA - G3»; (3) nạp bộ chứng chỉ vào `ssl.SSLContext` như thư viện mạng làm: không còn chứng chỉ nào có dấu vân tay SHA-256 của gốc đó (bắt được cả khi nhãn bị đổi tên); (4) `requests` (client WordPress) mặc định dùng đúng file `certifi.where()` |
| `docs/team/reports/T-075-tho-may.md` | Báo cáo này |

Không đụng `pyproject.toml`, `seo_app/`, `app/`, `config/`, test cũ.

```
$ git diff --stat ddb9beb -- uv.lock tests/
 tests/test_certifi_version.py | 54 +++++++++++++++++++++++++++++++++++++++++++
 uv.lock                       |  6 ++---
 2 files changed, 57 insertions(+), 3 deletions(-)
```

## Thông tin phiên bản

| Mục | Trước | Sau |
|---|---|---|
| `certifi` | 2026.7.22 | **2026.10.19** (PyPI, tải lên 2026-10-20 02:24 UTC). Là bản mới nhất: `uv lock --upgrade-package certifi --dry-run` → `No lockfile changes detected` |
| Số gốc trong `cacert.pem` | 121 | 120 |
| Gốc bị bỏ | | `emSign ECC Root CA - G3` (SHA-256 `86:a1:ec:ba:…:a3:6b:be:6b`) |
| Gốc được thêm | | Không có |

So hai bộ chứng chỉ theo dấu vân tay SHA-256 của từng gốc: bản cũ đọc từ `.venv` của repo chính (chỉ đọc), bản mới từ `.venv` của worktree. Các gốc của Google Trust Services (GTS Root R1, R3, R4) và Let's Encrypt (ISRG Root X1, X2) vẫn còn.

Gói dùng `certifi` (`uv tree --invert --package certifi`): `requests` 2.34.2 (client WordPress; kéo theo `streamlit`, `google-auth`, `google-genai`), `httpx` 0.28.1 và `httpcore` 1.0.9 (`google-genai`). Không gói nào đổi phiên bản theo.

## Kết quả `pip-audit`

`pip-audit` 2.10.1 chạy bằng `uvx` trong thư mục nháp của phiên (không thêm vào thư viện của dự án), trên đủ **69 gói ghim** của `uv.lock` (`uv export --frozen --no-hashes --no-emit-project --format requirements-txt`, rồi `--disable-pip --no-deps`). Đối chứng: `uv.lock` gốc lấy bằng `git show ddb9beb:uv.lock` (cùng `pyproject.toml`) vào thư mục nháp. Hai danh sách ghim chỉ khác đúng một dòng: `certifi==2026.7.22` → `certifi==2026.10.19`.

```
$ uvx pip-audit -r req.txt --disable-pip --no-deps -s pypi        # uv.lock MỚI
No known vulnerabilities found                                      (mã thoát 0)
$ uvx pip-audit -r req.txt --disable-pip --no-deps -s osv         # uv.lock MỚI
No known vulnerabilities found                                      (mã thoát 0)

$ uvx pip-audit -r req-old.txt --disable-pip --no-deps -s pypi    # uv.lock CŨ (đối chứng)
Found 1 known vulnerability in 1 package
Name    Version   ID              Fix Versions
------- --------- --------------- ------------
certifi 2026.7.22 PYSEC-2026-4320 2026.10.19                        (mã thoát 1)
$ uvx pip-audit -r req-old.txt --disable-pip --no-deps -s osv     # uv.lock CŨ (đối chứng)
Found 2 known vulnerabilities in 1 package
Name    Version   ID              Fix Versions
------- --------- --------------- ------------
certifi 2026.7.22 PYSEC-2026-4320 2026.10.19
certifi 2026.7.22 PYSEC-2026-4320 2026.10.19                        (mã thoát 1)
```

- Mã thoát lấy bằng `${PIPESTATUS[0]}` (Git Bash), là mã của chính `pip-audit`.
- OSV in hai dòng giống hệt nhau; xem bằng `-f json` thì cả hai đều là `PYSEC-2026-4320`, bí danh `GHSA-6q48-6c7w-9gw2`: một lỗ hổng được trả về hai lần, không phải hai lỗ hổng.
- Cảnh báo duy nhất của công cụ (đã lọc khỏi khối trên): khuyên dùng mã băm khi chạy `--no-deps`. Không ảnh hưởng kết quả; `uv.lock` vẫn giữ mã băm và `uv sync` kiểm mã băm khi cài.

## Bằng chứng

```
$ uv lock --upgrade-package certifi
Using CPython 3.12.15
Resolved 70 packages in 1.94s
Updated certifi v2026.7.22 -> v2026.10.19

$ git diff --stat                     # trước commit: chỉ uv.lock, chỉ khối certifi (xem mục Đã thay đổi)
 uv.lock | 6 +++---
$ uv lock --check
Resolved 70 packages in 3ms
$ uv sync --frozen
Checked 69 packages in 20ms
$ uv run python -c "import certifi, importlib.metadata as m; print(certifi.__version__, m.version('certifi'))"
2026.10.19 2026.10.19

$ uv run pytest tests/test_certifi_version.py -v
4 passed
# Đối chứng: cùng file test, chạy bằng Python của .venv repo chính (certifi 2026.7.22),
# PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider (không ghi gì vào repo chính):
3 failed, 1 passed     (hỏng đúng 3 test chốt: 2026.7.22 < 2026.10.19, còn nhãn, còn dấu vân tay;
                        test (4) không phụ thuộc phiên bản nên qua)

$ uv run pytest tests/test_certifi_version.py tests/test_wordpress_client.py tests/test_app_pages.py \
    tests/test_ai.py tests/test_ai_images.py tests/test_ai_openai_gemini.py \
    tests/test_ai_openai_gemini_soi_loi.py tests/test_ai_t026.py tests/test_ai_t028.py tests/test_ai_t034.py -q -rfEs
927 passed in 88.63s (0:01:28)
(0 hỏng, 0 bỏ qua; Windows 11, máy đang chạy song song phiên khác. Mã băm của uv.lock và file test
 trùng nhau lúc đầu và lúc cuối lượt chạy, và trùng bản đã commit ca112a0)

$ uv run ruff check .                 # ruff 0.16.10
All checks passed!

$ uv pip check
Found 1 incompatibility
The package `streamlit` requires `pillow>=7.1.0,<13`, but `13.0.0` is installed
(có từ T-058, cố ý; không có gì về certifi)

$ PYTHONUTF8=1 uvx detect-secrets scan tests/test_certifi_version.py
results: {}
```

Số test theo file (927 = tổng): `test_ai.py` 18, `test_ai_images.py` 244, `test_ai_openai_gemini.py` 130, `test_ai_openai_gemini_soi_loi.py` 117, `test_ai_t026.py` 100, `test_ai_t028.py` 230, `test_ai_t034.py` 33, `test_app_pages.py` 18, `test_certifi_version.py` 4, `test_wordpress_client.py` 33.

Hai chỗ tự soát được trong lúc làm (đều trước commit):

- Lượt đối chứng với bản cũ cho thấy bản đầu của test (1) so chuỗi `certifi.__version__ == version("certifi")`: `certifi` viết số 0 đầu («2026.07.22») còn metadata thì không («2026.7.22»), nên test sẽ hỏng oan ở các bản sau như 2027.02.xx. Đã đổi sang so bằng `Version`.
- `detect-secrets` báo nhầm «Hex High Entropy String» khi dấu vân tay viết liền 64 ký tự hex. Đã chép lại đúng dạng có dấu `:` như dòng «SHA256 Fingerprint» trong file `certifi` (dễ so bằng mắt; đã kiểm giá trị sau khi bỏ dấu `:` trùng giá trị tính được), không dùng lệnh bỏ qua `pragma: allowlist secret`. Quét lại: 0.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: `certifi` 2026.10.19; `git diff uv.lock` chỉ đổi khối `certifi`, `uv` không đòi đổi gói khác hay `pyproject.toml` (commit `ca112a0`)
- [x] Yêu cầu 2: test chốt `tests/test_certifi_version.py` (phiên bản, nhãn, thêm dấu vân tay và đường `requests`); đối chứng bản cũ: hỏng đúng 3 test
- [x] Yêu cầu 3: `pip-audit` nguồn PyPI và OSV trên 69 gói của `uv.lock`: 0 lỗ hổng (bản cũ: 1, PYSEC-2026-4320)
- [x] Test liên quan qua (927 passed), `uv run ruff check .` sạch
- [x] D1: không thêm thư viện; chỉ nâng `certifi` (chủ dự án duyệt 2026-10-21 10:05). D3: test mới chỉ đọc file trên máy, chạy dưới bộ chặn mạng tự động (`tests/conftest.py`)
- [x] Báo cáo nộp tại `docs/team/reports/T-075-tho-may.md`
- [ ] Toàn bộ `uv run pytest` trên Windows: việc của Chỉ Huy khi gộp

## Cách quay về nếu hỏng

**Dấu hiệu hỏng:** sau khi gộp, trang Kết nối WordPress báo «Lỗi chứng chỉ bảo mật (SSL) của website…», hoặc Gemini báo lỗi SSL, mà trước đó thì không. Khả năng này rất thấp (suy luận): bản mới chỉ bỏ một gốc emSign, mọi gốc khác giữ nguyên như bản cũ đang chạy tốt; chỉ website nào có chứng chỉ do đúng gốc bị bỏ cấp mới hỏng, và đó chính là thứ cần chặn.

**Quay về nghĩa là mở lại lỗ hổng**: chỉ làm khi app hỏng thật, và báo Lá Chắn ngay.

1. `git revert ca112a0` (bỏ commit đổi `uv.lock` và test chốt; báo cáo giữ lại), rồi `uv sync` hoặc mở lại `run.bat` / `run.command`.
2. Hoặc làm tay: `uv lock --upgrade-package "certifi==2026.7.22"` (đã thử `--dry-run`: `Update certifi v2026.10.19 -> v2026.7.22`), `uv sync`, xóa `tests/test_certifi_version.py`, chạy `uv run pytest`.

## Rủi ro và điểm cần chú ý

- **Mỗi máy chỉ an toàn sau `uv sync`.** `run.bat` (dòng 25) và `run.command` (dòng 26) chạy `uv sync` trước khi mở app; máy nào chưa mở lại app bằng hai file này thì vẫn dùng bản cũ.
- **Biến môi trường của máy vẫn thắng `certifi`:** `google-genai` dùng `SSL_CERT_FILE` nếu có đặt (`google/genai/_api_client.py:1188`), `requests` dùng `REQUESTS_CA_BUNDLE` / `CURL_CA_BUNDLE` (`requests/sessions.py:857-858`). Đây là rủi ro đã ghi sổ 2026-10-15 (`security.md` mục 6); test (4) chỉ kiểm đường mặc định.
- **Claude, ChatGPT không đi qua `certifi`** (theo Lá Chắn T-061: `httpx2` + `truststore`, dùng kho chứng chỉ của hệ điều hành), nên phiếu này không đổi gì với hai hãng đó. Chúng phụ thuộc Windows, macOS đã gỡ hay chặn gốc này chưa: tôi chưa kiểm, ngoài phạm vi phiếu.
- **Test (4) sẽ hỏng nếu sau này `requests` đổi sang kho của hệ điều hành.** Khi đó không phải lỗi của app: đọc chú thích trong test và xem lại phiếu này.
- `origin/main` trên GitHub đang ở `6a58617`, còn `main` cục bộ ở `ddb9beb`; nhánh này dựng trên `ddb9beb` đúng như phiếu giao (ghi để Chỉ Huy biết khi gộp).

## Đề xuất

- Lá Chắn rút gọn (D1, D3): quét lại `pip-audit` trên nhánh `team/T-075`; xác nhận bỏ lời dặn «không dùng Wi-Fi công cộng» sau khi cả 2 máy đã `uv sync`.
- Lá Chắn (ngoài phạm vi phiếu, chưa kiểm): xem kho chứng chỉ của Windows và macOS còn tin gốc «emSign ECC Root CA - G3» không, cho đường Claude, ChatGPT qua `truststore`.

## Câu hỏi cho chủ dự án

Không có.

# Báo cáo T-075 · Soi Lỗi · Nâng `certifi` lên 2026.10.19, kiểm rút gọn

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-075](../tickets/T-075-nang-certifi.md) · báo cáo Thợ Máy: [T-075-tho-may](T-075-tho-may.md) |
| Ngày nộp | 2026-10-21 (giờ máy, +07) |
| Nhánh kiểm | `team/T-075`, đầu nhánh lúc nhận `f6a8220`, gốc `main` `ddb9beb` |
| Kết quả | Hoàn thành |
| **Kết luận** | **ĐẠT**: chuyển Lá Chắn rút gọn được. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp. Không có test `xfail` |

## Tóm tắt (cho chủ dự án)

- **Bản nâng cấp đúng và sạch.** File khóa thư viện chỉ đổi đúng `certifi`, trỏ đúng file chính thức trên PyPI (mã băm khớp từng ký tự). Sau khi cài, danh sách «cơ quan cấp chứng chỉ» mà app tin **chỉ mất đúng một** cơ quan bị lộ khóa (emSign ECC Root CA - G3), không thêm, không bớt cơ quan nào khác. Vì vậy website nào app vào được trước đây thì nay vẫn vào được.
- **Tôi thử đúng đường app đi khi kết nối**, không gọi mạng thật: cho client WordPress và Gemini của app chạy tới đúng lúc «bắt tay» bảo mật với máy chủ, rồi xem danh sách cơ quan mà thư viện thật sự dùng. Cả hai đều dùng **đúng** danh sách mới, bắt buộc kiểm chứng chỉ, không còn cơ quan bị lộ. Khi chứng chỉ bị từ chối, trang WordPress báo câu lỗi SSL quen thuộc và không lộ mật khẩu.
- **Test mới bắt được lỗi thật:** tôi cố tình làm hỏng theo 5 cách (quay về bản cũ, tắt kiểm chứng chỉ, cho WordPress hoặc Gemini dùng kho của Windows, cài đè bộ kiểm chứng chỉ của hệ điều hành): lần nào cũng có test báo đỏ.
- **Không tìm thấy lỗi nào.** Lời dặn «không dùng Wi-Fi công cộng» vẫn giữ tới khi Chỉ Huy gộp, cả 2 máy mở app lại bằng `run.bat` / `run.command`, và Lá Chắn xác nhận.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t075.py` | Mới, 2 test, không gọi mạng: client WordPress và provider Gemini của app bắt tay TLS bằng đúng bộ `certifi` đã vá (mục Bằng chứng, bước 4) |
| `docs/team/reports/T-075-soi-loi.md` | Báo cáo này |

Không sửa `uv.lock`, `pyproject.toml`, code ứng dụng hay test của người khác.

## Bằng chứng

### 1. `uv.lock` và `pyproject.toml`

```
$ git diff ddb9beb..team/T-075 --stat
 docs/team/reports/T-075-tho-may.md | 159 +++++
 tests/test_certifi_version.py      |  54 +++
 uv.lock                            |   6 +-
$ git diff ddb9beb..team/T-075 -- pyproject.toml          # trống: không đổi
$ git diff ddb9beb..team/T-075 -- uv.lock                 # 1 khối duy nhất (dòng 80–88), chỉ [[package]] name = "certifi":
-version = "2026.7.22"            +version = "2026.10.19"
 sdist: 1 dòng đổi                 wheels: 1 dòng đổi       (source, wheels = [ ... ] giữ nguyên)
$ uv lock --check                 → Resolved 70 packages in 3ms   (mã thoát 0)
$ uv sync --locked                → mã thoát 0
```

Đối chiếu với PyPI (`https://pypi.org/pypi/certifi/2026.10.19/json`, chỉ đọc):

| File | Mục | `uv.lock` | PyPI | Khớp |
|---|---|---|---|---|
| `certifi-2026.10.19-py3-none-any.whl` | sha256 | `42d35340…5fa8670e1b` | `42d35340cc5b9ba78e818ddbff0c5b1c2b779de448a340fd1b989f5fa8670e1b` | Có |
| | địa chỉ | `files.pythonhosted.org/packages/c4/51/29046e48…/certifi-2026.10.19-py3-none-any.whl` | giống hệt | Có |
| | cỡ, giờ tải lên | 136464, `2026-10-20T02:24:15.072Z` | 136464, `2026-10-20T02:24:15.072385Z` | Có |
| `certifi-2026.10.19.tar.gz` | sha256 | `035c1e85…fea780a1ae` | `035c1e85572b141bf1c3a3eff0e33a8eb74917522f2559075ff8d2fea780a1ae` | Có |
| | địa chỉ | `files.pythonhosted.org/packages/a6/bd/1436c50c…/certifi-2026.10.19.tar.gz` | giống hệt | Có |
| | cỡ, giờ tải lên | 137598, `2026-10-20T02:24:16.604Z` | 137598, `2026-10-20T02:24:16.604828Z` | Có |

Cả hai file `yanked = False`. Bản mới nhất trên PyPI là 2026.10.19 (các bản gần nhất: 2026.6.17, 2026.7.22, 2026.10.18, 2026.10.19).

### 2. Cài trong worktree

```
$ uv sync                         → Resolved 70 packages / Checked 69 packages
$ uv run python -c "…"
version 2026.10.19 2026.10.19                               (certifi.__version__, metadata)
where   D:\ProMetal-ToolSEO\wt-T-075\.venv\Lib\site-packages\certifi\cacert.pem
"emSign ECC Root CA - G3" có trong file: False
số chứng chỉ gốc trong file: 120; nạp vào SSLContext: 120
mã băm cacert.pem đã cài = mã băm trong RECORD của wheel: True
```

So bộ gốc giữa các bản (nạp từng bản vào môi trường tạm bằng `uv run --no-project --isolated --with certifi==…`, tính SHA-256 của từng gốc):

| So | Kết quả |
|---|---|
| 2026.7.22 (cũ, 121 gốc) trừ 2026.10.19 (mới, 120 gốc) | đúng 1: `emSign ECC Root CA - G3` (`86a1ecba…a36bbe6b`) |
| 2026.10.19 trừ 2026.7.22 | không có |
| 2026.7.22 trừ 2026.10.18 (117 gốc) | 4 gốc emSign: G3, Root CA - G1, Root CA - C1, ECC Root CA - C3 |

Dấu vân tay trong test của Thợ Máy đúng là của gốc G3: file `cacert.pem` bản 2026.7.22 có `# Label: "emSign ECC Root CA - G3"` (dòng 2010) và `# SHA256 Fingerprint: 86:a1:ec:ba:…:a3:6b:be:6b` (dòng 2014), trùng từng ký tự với `_VAN_TAY_BI_LO`.

Cả `.venv` chỉ có đúng một bộ chứng chỉ (`certifi/cacert.pem`); không file nào khác (kể cả file nhị phân) chứa chuỗi «emSign ECC Root CA - G3» (`grep -r` trên `.venv`). Không thư viện nào gọi `truststore.inject_into_ssl()`; app không dùng đường gọi bất đồng bộ của Gemini (`.aio`), và `aiohttp` không được cài.

### 3. Soát test mới của Thợ Máy (`tests/test_certifi_version.py`)

| Thử | Kết quả |
|---|---|
| Bản đang khóa (2026.10.19) | 4 passed |
| Quay về 2026.7.22 (`uv run --with certifi==2026.7.22 pytest …`, không đổi `uv.lock`) | **3 failed, 1 passed**: hỏng đúng 3 test chốt (phiên bản `2026.7.22 < 2026.10.19`, còn nhãn, còn dấu vân tay); test (4) không phụ thuộc phiên bản nên qua, đúng thiết kế |
| Bản 2026.10.18 (không còn G3 nhưng nằm trong khoảng bị ảnh hưởng của khuyến cáo) | 1 failed (test phiên bản), 3 passed: đúng ngưỡng của khuyến cáo (`< 2026.10.19`) |

- **Không gọi mạng:** chỉ đọc file `cacert.pem` và nạp vào `ssl.SSLContext` trong bộ nhớ; chạy dưới bộ chặn mạng tự động (`tests/conftest.py`).
- **Chạy được trên Mac/Linux** (suy luận từ mã, máy này chỉ có Windows): chỉ dùng `pathlib`, `ssl`, `hashlib`, `importlib.metadata`, đọc file bằng `encoding="utf-8"`; không có đường dẫn hay lệnh riêng Windows. `get_ca_certs(binary_form=True)` có trên mọi bản Python dùng OpenSSL (Python của uv trên cả 3 hệ điều hành).
- Không phụ thuộc thứ tự chạy, không cần `.env`. `detect-secrets` sạch (Thợ Máy đã quét).

### 4. Thử thêm: kết nối thật của app (`tests/test_soi_loi_t075.py`)

Cả 2 test đi đúng đường app dùng, chỉ thay hai bước chạm mạng: nối TCP (trả socket chưa nối) và bắt tay TLS (`SSLContext.wrap_socket` ghi lại ngữ cảnh rồi báo «chứng chỉ không hợp lệ»). Biến `REQUESTS_CA_BUNDLE`, `CURL_CA_BUNDLE`, `SSL_CERT_FILE`, `SSL_CERT_DIR` và proxy được gỡ trong lúc test, để kiểm đường mặc định giống nhau trên mọi máy.

| Test | Đường đi | Kiểm |
|---|---|---|
| `test_client_wordpress_bat_tay_bang_bo_certifi_da_va` | `WordPressClient("https://suachuacuasat.com", …).check_connection()` → `requests` → `urllib3` | ngữ cảnh TLS: `CERT_REQUIRED`, tên máy `suachuacuasat.com`, bộ gốc **bằng đúng** bộ `certifi.where()` (120 gốc, không thêm kho Windows), không có G3; app báo «Lỗi chứng chỉ bảo mật (SSL)…», câu lỗi không chứa mật khẩu ứng dụng; đúng 1 lần bắt tay |
| `test_gemini_bat_tay_bang_bo_certifi_da_va` | `GeminiProvider(khóa giả)._client.models.generate_content(…)` → `google-genai` → `httpx` → `httpcore` | như trên với tên máy `generativelanguage.googleapis.com`; số lần bắt tay bằng `RETRY.attempts` của app (3), lần thử lại nào cũng dùng cùng bộ chứng chỉ (chỉ bỏ thời gian chờ giữa các lần) |

**Thử ngược** (plugin pytest nháp trong thư mục tạm của phiên, không commit): mỗi kiểu hỏng đều có test báo đỏ.

| Giả lập hỏng | Test WordPress | Test Gemini |
|---|---|---|
| `certifi` 2026.7.22 | hỏng | hỏng |
| `requests.Session` đặt `verify = False` | hỏng (`CERT_NONE`) | qua (đúng: Gemini không dùng `requests`) |
| `requests` bỏ `certifi`, `urllib3` nạp kho Windows | hỏng (thừa gốc của Windows) | qua |
| `google-genai` gọi `ssl.create_default_context(cafile=None)` (kho Windows) | qua | hỏng (thừa gốc của Windows) |
| `truststore.inject_into_ssl()` (thay `ssl` toàn cục bằng kho hệ điều hành) | hỏng | hỏng |

### 5. Test liên quan và `ruff`

```
$ uv run pytest tests/test_certifi_version.py tests/test_wordpress_client.py tests/test_app_pages.py tests/test_ai*.py -q -rfEsxX
                                                       (Windows, tại f6a8220, 2026-10-21 11:25:43–11:28:00 +07)
927 passed in 131.23s (0:02:11)
(0 hỏng, 0 bỏ qua; 7 file test_ai*: test_ai.py, test_ai_images.py, test_ai_openai_gemini.py,
 test_ai_openai_gemini_soi_loi.py, test_ai_t026.py, test_ai_t028.py, test_ai_t034.py)

$ uv run pytest tests/test_soi_loi_t075.py tests/test_certifi_version.py tests/test_wordpress_client.py tests/test_app_pages.py -q -rfEsxX
57 passed in 26.04s                                    (2026-10-21 11:35:29 +07)
$ uv run pytest tests/test_app_pages.py tests/test_wordpress_client.py tests/test_soi_loi_t075.py -q
53 passed in 25.79s                                    (thứ tự ngược, không phụ thuộc thứ tự)

$ uv run ruff check .
All checks passed!
$ PYTHONUTF8=1 uvx detect-secrets scan tests/test_soi_loi_t075.py
"results": {}
```

Toàn bộ `uv run pytest` không chạy (quy tắc 2026-10-20: Chỉ Huy chạy khi gộp).

## Đối chiếu việc được giao

- [x] **Việc 1:** `uv.lock` chỉ đổi khối `certifi` (6 dòng, 1 khối); mã băm, địa chỉ, cỡ, giờ tải lên của cả wheel và sdist khớp PyPI; `pyproject.toml` không đổi; `uv lock --check`, `uv sync --locked` qua (mục 1).
- [x] **Việc 2:** `uv sync` xong, `certifi` 2026.10.19; `certifi.where()` không còn gốc G3 (theo nhãn và theo dấu vân tay); so với bản cũ chỉ mất đúng gốc này (mục 2).
- [x] **Việc 3:** test của Thợ Máy kiểm đúng ý, hỏng 3/4 khi quay về 2026.7.22, không gọi mạng, không có gì riêng Windows (mục 3).
- [x] **Việc 4:** `requests` (client WordPress) và `google-genai` (Gemini) bắt tay TLS bằng đúng bộ mới, có test và thử ngược; mọi trang app mở được (`test_app_pages.py` 18 passed trong 927) (mục 4, 5).
- [x] **Việc 5:** không có lỗi mới nên không có `xfail`; không sửa `uv.lock` hay code ứng dụng.

## Lỗi tìm được

Không có.

## Ghi nhận (không phải lỗi, để Lá Chắn và Chỉ Huy biết)

1. **Bản 2026.10.18 bỏ cả 4 gốc emSign, bản 2026.10.19 thêm lại 3 gốc** (Root CA - G1, Root CA - C1, ECC Root CA - C3). Khuyến cáo GHSA-6q48-6c7w-9gw2 (đọc qua `api.github.com/advisories`, 2026-10-21) nói rõ 2026.10.19 «khôi phục các gốc emSign không bị ảnh hưởng» và chỉ G3 có chứng chỉ trung gian bị lộ khóa. Nên việc 3 gốc emSign còn trong bộ mới là cố ý của nhà phát hành. Nếu sau này eMudhra có sự cố với các gốc đó, bản `certifi` mới sẽ xử lý; test hiện tại chỉ chốt G3.
2. **Test (4) của Thợ Máy chỉ so hằng số `DEFAULT_CA_BUNDLE_PATH`.** `requests` 2.34.2 không nạp sẵn kho chứng chỉ lúc import mà gán đường dẫn này cho từng kết nối (`requests/adapters.py:307-346`, `cert_verify`), nên kiểm hằng số là đủ cho phiên bản này. Test mới của Soi Lỗi kiểm thêm ngữ cảnh TLS thật của cả hai client, nên nếu thư viện đổi cách làm thì vẫn bắt được.
3. **Biến môi trường của máy vẫn thắng `certifi`** (`SSL_CERT_FILE`, `SSL_CERT_DIR` với Gemini: `google/genai/_api_client.py:1187-1190`; `REQUESTS_CA_BUNDLE`, `CURL_CA_BUNDLE` với WordPress). Đã ghi sổ (`security.md` mục 6), Thợ Máy cũng nêu. Trên máy Windows này không có biến nào trong 4 biến trên (kiểm trong phiên, chỉ xem có đặt hay không).
4. **`run.bat` (dòng 25–31) và `run.command` (dòng 26–30) dừng hẳn khi `uv sync` lỗi**, không mở app với thư viện cũ. Máy nào mở app bằng hai file này sau khi gộp thì chắc chắn dùng bản mới.

## Rủi ro và điểm cần chú ý

- Test mới chạm vào vài chỗ bên trong thư viện (`provider._client._api_client._retry`, `httpcore._backends.sync.SyncBackend.connect_tcp`, `urllib3.util.connection.create_connection`). Khi nâng `google-genai`, `httpx`/`httpcore` hay `urllib3`, test có thể hỏng vì thư viện đổi cấu trúc chứ không phải vì app sai: khi đó đọc chú thích đầu file và sửa chỗ thay thế, đừng bỏ test.
- Chưa chạy trên Mac/Linux (máy này chỉ có Windows); kết luận «chạy được» là suy luận từ mã (mục 3). Proxy hệ thống trên Windows (registry) và macOS bị vô hiệu trong test bằng `NO_PROXY=*`, nên test không phụ thuộc cài đặt mạng của máy.
- Claude và ChatGPT không đi qua `certifi` (dùng kho chứng chỉ của hệ điều hành qua `truststore`): ngoài phạm vi phiếu, chưa kiểm (giữ như Đề xuất 2 của Thợ Máy).

## Đề xuất

- Lá Chắn rút gọn: quét lại `pip-audit` trên `team/T-075`; xác nhận bỏ lời dặn «không dùng Wi-Fi công cộng» sau khi cả 2 máy đã mở app bằng `run.bat` / `run.command`.
- Lá Chắn (ngoài phạm vi, như Thợ Máy đề xuất): xem kho chứng chỉ của Windows và macOS cho đường Claude, ChatGPT.

## Câu hỏi cho chủ dự án

Không có.

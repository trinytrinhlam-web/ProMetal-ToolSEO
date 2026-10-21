# Biên bản bảo mật T-075 · Nâng `certifi` lên 2026.10.19 (GHSA-6q48-6c7w-9gw2)

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

> **Phát hiện mới, mức Cao, ngoài phạm vi phiếu, không do T-075 (LC-T075-1):** chính công cụ `uv` 0.12.23 trên máy Windows này (máy Mac chưa biết bản nào) mang sẵn gốc «emSign ECC Root CA - G3» trong bộ chứng chỉ riêng của nó (GHSA-hq85-5cpj-mr62, vá ở uv **0.13.4**). Lúc mở app không bị ảnh hưởng vì `uv sync` kiểm mã băm từng gói, nhưng các lệnh tải công cụ không ghim mã băm (`uvx`, `uv run --with`, `uv lock --upgrade-package`) thì bị. Cần nâng uv trên cả 2 máy. Chi tiết ở mục «Phát hiện toàn repo».

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem dòng trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-075](../tickets/T-075-nang-certifi.md) · kiểm **rút gọn** (D1, D3), xác nhận đóng LC-T061-1 của [Lá Chắn T-061](T-061-la-chan.md) |
| Phạm vi | diff `ddb9beb..f5f2bb6` (nhánh `team/T-075`, 5 file): `uv.lock`, `tests/test_certifi_version.py`, `tests/test_soi_loi_t075.py`, 2 báo cáo. Kèm đường TLS của client WordPress (`requests` → `urllib3`) và Gemini (`google-genai` → `httpx` → `httpcore`), `run.bat`, `run.command`; ngoài phiếu: công cụ `uv`, đường Claude/ChatGPT qua `truststore` |
| Báo cáo đã đọc | [Thợ Máy](T-075-tho-may.md), [Soi Lỗi](T-075-soi-loi.md) (ĐẠT, 0 lỗi), [Lá Chắn T-061](T-061-la-chan.md) mục «Phát hiện toàn repo» |
| Ngày | 2026-10-21 (12:00–12:30, giờ máy +07) |
| **Kết luận** | **ĐẠT** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp trong thay đổi của T-075. **LC-T061-1 đã đóng.** **Gộp vào `main` được ngay** (thử gộp với `origin/main` `9e6254f`: không xung đột; test liên quan trên cây gộp 0 hỏng). LC-T075-1 (Cao, toàn máy, có từ trước) không tính vào kết luận này, cần phiếu riêng |

## Tóm tắt (cho chủ dự án)

- **Bản vá đúng và đủ.** File khóa thư viện chỉ đổi `certifi`, mã băm khớp PyPI (tôi đối chiếu qua 3 đường mạng khác nhau). Bộ «cơ quan cấp chứng chỉ» đã cài bỏ đúng một cơ quan bị lộ khóa (emSign ECC Root CA - G3), không thêm cơ quan nào. Client WordPress và Gemini của app dùng đúng bộ mới và luôn kiểm chứng chỉ. Phiếu **đạt**, gộp được ngay.
- **Quét lại cả 69 thư viện** bằng 3 nguồn dữ liệu lỗ hổng (PyPI, OSV, GitHub): **sạch**. Bản cũ thì cả 3 nguồn đều báo lỗ hổng `certifi`, nên công cụ chạy đúng.
- **Việc mới cần làm (không do phiếu này):** công cụ `uv` (cài thư viện, mở app) cũng mang cùng cơ quan bị lộ trong bộ chứng chỉ riêng của nó. Mở app hằng ngày vẫn an toàn vì `uv` kiểm «dấu vân tay» từng gói trước khi cài; chỗ hở nằm ở lúc các agent tải công cụ kiểm tra. Sửa bằng **một lệnh trên mỗi máy** (`uv self update`, làm ở mạng nhà hoặc công ty). Chỉ Huy sẽ lập phiếu.
- **Lời dặn «không dùng Wi-Fi công cộng»** bỏ được khi đủ 3 việc: (1) Chỉ Huy gộp phiếu này và cả 2 máy mở app lại bằng `run.bat` / `run.command`; (2) cả 2 máy đã nâng `uv` lên 0.13.4 trở lên; (3) Windows và macOS đã cập nhật như thường lệ (Claude, ChatGPT dùng kho chứng chỉ của hệ điều hành; theo tin công bố, Microsoft và Apple đã chặn các chứng chỉ bị lộ ngày 19–20/10).

## Lỗi phát hiện (thay đổi của T-075)

Không phát hiện lỗi.

## LC-T061-1: đã đóng

| # | Kiểm | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | `uv.lock` chỉ đổi khối `certifi` | Đạt | `git diff ddb9beb..f5f2bb6 -- uv.lock`: một khối (`uv.lock:82-88`), 3 dòng đổi: `version` 2026.7.22 → 2026.10.19, `sdist`, `wheels`. `pyproject.toml` không đổi (diff trống). Vẫn 70 gói. `uv lock --check` (uv 0.12.23): `Resolved 70 packages`, mã thoát 0; `uv sync --locked`: `Checked 69 packages`, mã thoát 0. Gói phụ thuộc `certifi` không đổi phiên bản: `httpcore` (`:458`), `httpx` (`:521`), `requests` (`:1433`) |
| 2 | Mã băm khớp PyPI | Đạt | So `uv.lock:85`, `:87` với `pypi.org/pypi/certifi/2026.10.19/json` lấy qua **2 đường độc lập**: `curl` trên máy này (Schannel, kho Windows) và công cụ đọc web chạy trên máy chủ khác (không đi qua mạng của máy này). Cả hai trả giống hệt: wheel `sha256:42d35340cc5b9ba78e818ddbff0c5b1c2b779de448a340fd1b989f5fa8670e1b`, 136464 byte, tải lên `2026-10-20T02:24:15.072385Z`; sdist `sha256:035c1e85572b141bf1c3a3eff0e33a8eb74917522f2559075ff8d2fea780a1ae`, 137598 byte; địa chỉ `files.pythonhosted.org/packages/c4/51/…` và `…/a6/bd/…` trùng từng ký tự; cả hai `yanked = false`; `info.version` = 2026.10.19 (bản mới nhất). Cùng giá trị Soi Lỗi đã đối chiếu |
| 3 | Bộ chứng chỉ đã cài không còn G3 | Đạt | Trong `.venv` của worktree: `certifi.__version__` = metadata = 2026.10.19; `certifi.where()` = `.venv\Lib\site-packages\certifi\cacert.pem`; 120 nhãn, nạp vào `ssl.SSLContext` được 120 gốc; nhãn «emSign ECC Root CA - G3»: không có; dấu vân tay SHA-256 `86a1ecba…a36bbe6b`: không có; mã băm `cacert.pem` khớp `RECORD` của wheel. Còn 3 gốc emSign (Root CA - G1, Root CA - C1, ECC Root CA - C3): đúng khuyến cáo («2026.10.19 restored the emSign roots that are not affected») |
| 4 | So bộ gốc giữa các bản | Đạt | Tự tính SHA-256 từng gốc (bản cũ nạp bằng `uv run --no-project --isolated --with certifi==…`): 2026.7.22 (121) → bản đã cài (120): **bỏ đúng G3, thêm 0**. 2026.7.22 → 2026.10.18 (117): bỏ 4 gốc emSign; 2026.10.18 → 2026.10.19: thêm lại G1, C1, ECC C3. Trùng kết quả của Thợ Máy và Soi Lỗi |
| 5 | Không còn bộ chứng chỉ nào khác mang G3 | Đạt | Đọc cả 12.338 file trong `.venv`: không file nào chứa G3 dạng DER (so byte) hay PEM (so base64 sau khi bỏ xuống dòng); đối chứng: tìm thấy trong `cacert.pem` của 2026.7.22. Nhãn G3 (`grep -r`): 0 file. `.venv` không có `pip` (pip mang `certifi` riêng) |
| 6 | Client WordPress (`requests`) dùng đúng bộ này | Đạt | `requests/utils.py:82` (`DEFAULT_CA_BUNDLE_PATH = certs.where()`), `requests/adapters.py:328-340` (`cert_verify` gán đường này cho từng kết nối khi `verify=True`). App không đặt `verify` riêng: `seo_app/wordpress/client.py:492` (`requests.Session()`); `grep` `verify=` trong `seo_app/`, `app/`, `scripts/`: chỉ có tham số không liên quan ở `seo_app/images/folders.py:559`. Test `test_client_wordpress_bat_tay_bang_bo_certifi_da_va` qua: ngữ cảnh TLS lúc bắt tay `CERT_REQUIRED`, bộ gốc **bằng đúng** bộ `certifi` |
| 7 | Gemini (`google-genai`) dùng đúng bộ này | Đạt | `google/genai/_api_client.py:1187-1190` (`ssl.create_default_context(cafile=os.environ.get('SSL_CERT_FILE', certifi.where()))`); provider của app chỉ truyền `base_url`, `timeout`, `retry_options` (`seo_app/ai/gemini_provider.py:117-125`), không truyền ngữ cảnh SSL riêng. Test `test_gemini_bat_tay_bang_bo_certifi_da_va` qua: cả 3 lần bắt tay (`RETRY.attempts`) cùng bộ `certifi`, `CERT_REQUIRED` |
| 8 | Biến môi trường làm thư viện bỏ `certifi` | Không đặt | `SSL_CERT_FILE`, `SSL_CERT_DIR`, `REQUESTS_CA_BUNDLE`, `CURL_CA_BUNDLE`: không đặt trên máy này (chỉ xem có đặt hay không). Rủi ro đã ghi sổ (`security.md` mục 6, 2026-10-15) |
| 9 | Mỗi máy nhận bản vá khi mở app | Đạt | `run.bat:25` và `run.command:26` chạy `uv sync` trước khi mở app, lỗi thì dừng hẳn; `uv sync` kiểm mã băm theo `uv.lock` (thử ở mục LC-T075-1: mã băm sai thì từ chối cài) |

**Kết luận: LC-T061-1 đóng.** Có hiệu lực trên từng máy sau khi Chỉ Huy gộp và máy đó mở app lại bằng `run.bat` / `run.command`.

## Quét lỗ hổng toàn `uv.lock` (D1)

Danh sách: `uv export --frozen --no-hashes --no-emit-project --format requirements-txt` → **69 gói ghim**. Tôi bỏ phần điều kiện hệ điều hành (7 gói có, ví dụ `colorama ; sys_platform == 'win32'`, `watchdog ; sys_platform != 'darwin'`) để quét cả gói chỉ dùng trên Mac.

| Nguồn | `uv.lock` của nhánh | Đối chứng (`certifi==2026.7.22`, còn lại giữ nguyên) |
|---|---|---|
| `pip-audit` 2.10.1, `-s pypi --disable-pip --no-deps` | `No known vulnerabilities found`, mã thoát 0; JSON: 69 gói, 0 bỏ qua, 0 lỗ hổng | `certifi 2026.7.22 PYSEC-2026-4320 → 2026.10.19`, mã thoát 1 |
| `pip-audit` 2.10.1, `-s osv` | `No known vulnerabilities found`, mã thoát 0; JSON: 69 gói, 0 bỏ qua, 0 lỗ hổng | 2 dòng cùng `PYSEC-2026-4320` (một lỗ hổng, hai bản ghi), mã thoát 1 |
| Kho khuyến cáo GitHub (`gh api advisories`, `ecosystem=pip`, `affects=` đủ 69 `tên@phiên bản`, cả 3 loại `reviewed`, `unreviewed`, `malware`) | 0 / 0 / 0 | `GHSA-6q48-6c7w-9gw2 critical certifi >= 2019.03.09, < 2026.10.19` |

- Thử bộ lọc phiên bản của GitHub trước khi tin số 0: `pillow@12.3.0` → 2 khuyến cáo, `pillow@13.0.0` → 0; `requests` (mọi bản) → 8, `requests@2.34.2` → 0.
- Môi trường công cụ `uvx pip-audit` dùng `certifi` 2026.10.19, nên chính lần quét này đi qua bộ chứng chỉ đã vá.
- Khuyến cáo GHSA-6q48-6c7w-9gw2 (đọc qua `api.github.com`): mức critical, CVSS 4.0 9.1, công bố 2026-10-20 19:35 UTC, ảnh hưởng `>= 2019.03.09, < 2026.10.19`, vá ở 2026.10.19; chưa bị rút lại.
- **D1:** không thư viện mới (vẫn 70 gói), chỉ nâng `certifi` (chủ dự án duyệt 2026-10-21 10:05). Ngoài `uv.lock` không quét bằng 3 nguồn trên được; công cụ `uv` có khuyến cáo riêng: LC-T075-1.

## Soát test mới (D3, Mac/Linux)

| Kiểm | Kết quả |
|---|---|
| Không gọi mạng | `tests/test_certifi_version.py` chỉ đọc `cacert.pem`, nạp vào `SSLContext` trong bộ nhớ. `tests/test_soi_loi_t075.py` thay `urllib3.util.connection.create_connection`, `SyncBackend.connect_tcp` (trả socket **chưa nối**) và `SSLContext.wrap_socket` (báo lỗi chứng chỉ); bộ chặn mạng chung `tests/conftest.py` vẫn bật; gỡ biến chứng chỉ, proxy, đặt `NO_PROXY=*`. **Thử độc lập:** gắn `sys.addaudithook` (plugin pytest nháp, không commit) khi chạy 6 test: **0** `socket.connect`, **0** `socket.getaddrinfo`, **0** `socket.sendto`. Chỉ có 1 `socket.bind` vào `('::1', 0)` (cặp socket nội bộ trên Windows) và 1 sự kiện `http.client.connect` mà `urllib3` tự phát **sau** khi `create_connection` giả đã trả socket chưa nối (`urllib3/connection.py:239`, `:258`) |
| Bắt được bản hỏng | Tự thử lại: `uv run --with certifi==2026.7.22 pytest` hai file: **5 hỏng, 1 qua** (test (4) của Thợ Máy không phụ thuộc phiên bản, đúng thiết kế); `certifi==2026.10.18`: 1 hỏng (test phiên bản, đúng ngưỡng khuyến cáo). Sau đó `.venv` vẫn 2026.10.19 |
| Chạy được trên Mac/Linux | Suy luận từ mã, **chưa chạy thật** (máy này không có WSL, Docker). Không có mã riêng hệ điều hành (`grep` `os.name`, `sys.platform`, `winreg`, `msvcrt`, đường dẫn Windows: 0). Chỉ dùng `ssl`, `hashlib`, socket `AF_INET` chưa nối, `monkeypatch` lớp Python. `ssl.create_default_context(cafile=…)` và `load_verify_locations` không nạp kho hệ điều hành trên cả 3 hệ, nên phép so «bằng đúng bộ `certifi`» giữ nguyên. `NO_PROXY=*` làm `urllib` đọc biến môi trường trước registry (Windows) hay cài đặt hệ thống (macOS). `packaging` (test (1) dùng) là phụ thuộc của `pytest` trong `uv.lock` |
| Không làm yếu test cũ (R5) | Không test cũ nào bị sửa, bỏ qua hay đánh `xfail` |

## Thử gộp với `main`

| Gộp với | Kết quả |
|---|---|
| `origin/main` `95ece3b` (lúc bắt đầu; so với gốc `ddb9beb` chỉ khác tài liệu) | `git merge-tree --write-tree`: không xung đột (cây `8841cce`) |
| `main` cục bộ `378f710` (đã có code T-074: `seo_app/images/tags.py`, `seo_app/storage/image_tags.py`) | Không xung đột (cây `eac599b`). Dựng worktree tạm trong thư mục nháp trên cây này (đã xóa), `uv sync --frozen` → `certifi` 2026.10.19. Test liên quan + 3 file test của T-074: **1552 passed, 1 skipped, 39 xfailed, 0 hỏng** (140,82 s; bỏ qua: tạo symlink cần Developer Mode; xfail: 20 `test_la_chan_t074.py` + 19 `test_soi_loi_t074.py`, có sẵn của T-074). `ruff`: sạch |
| `origin/main` = `main` `9e6254f` (lúc nộp) | Không xung đột (cây `4fd3d51`). Cây này khác cây đã chạy test **chỉ ở 3 file tài liệu** (`CLAUDE.md`, `docs/team/board.md`, `docs/team/dong-bo.md`), nên kết quả test trên áp dụng nguyên |

Từ `ddb9beb` tới `9e6254f`, `main` không đổi file nào trong `uv.lock`, `pyproject.toml`, `tests/conftest.py`, `seo_app/wordpress/`, `seo_app/ai/` hay các test liên quan. **Gộp được ngay.**

## Phát hiện toàn repo (ngoài phạm vi phiếu, không tính vào kết luận T-075)

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T075-1 | **Cao** (toàn máy, có từ trước, không do T-075; khuyến cáo xếp High) | Công cụ `uv` **dưới 0.13.4** dùng bộ chứng chỉ gói sẵn trong tệp chạy (theo `webpki-root-certs`), còn gốc «emSign ECC Root CA - G3» (GHSA-hq85-5cpj-mr62, công bố 2026-10-20, vá ở **0.13.4**, phát hành 2026-10-20 15:24 UTC). Máy Windows này: `uv 0.12.23`; tìm byte DER trong `C:\Users\ADMIN\.local\bin\uv.exe`: **có G3** (cùng 3 gốc emSign khác; đối chứng ISRG Root X1 cũng có). Máy Mac: chưa biết bản nào | Tệp chạy `uv` trên từng máy; được gọi từ `run.bat:25`, `run.command:26`, `security.md` mục 5 (`uvx pip-audit`, `uvx bandit`, `uvx detect-secrets`) và các lệnh nâng thư viện (`uv lock --upgrade-package`) | Agent chạy `uvx <công cụ>`, `uv run --with <gói>` hay `uv lock --upgrade-package` trên máy của chủ dự án (máy có `.env` thật) khi máy đang ở mạng có kẻ chen giữa → kẻ đó đưa chứng chỉ giả cho `pypi.org` / `files.pythonhosted.org`, ký bằng một trong 8 khóa trung gian bị lộ → `uv` cũ chấp nhận → nhận gói giả kèm mã băm giả (các lệnh này **không có mã băm ghim sẵn**) → mã độc chạy dưới quyền chủ dự án, đọc `.env` (mật khẩu ứng dụng WordPress, khóa AI) → sửa bài trên site thật. Điều kiện «có khóa» gần như không còn: theo Christian Heimes (discuss.python.org; tiêu đề một bài trên dev.to nói cùng điều này), cả 8 khóa riêng là số nhỏ hơn 256, ai cũng tính lại được; chỉ còn điều kiện «ở giữa đường mạng». **Không bị:** mở app hằng ngày, vì `uv sync` / `uv run` kiểm mã băm theo `uv.lock`: tôi thử trên dự án nháp, sửa 1 ký tự mã băm wheel `certifi` → `uv sync --frozen` báo `Hash mismatch` và dừng, cả khi tải mới (bộ nhớ đệm rỗng) lẫn khi lấy từ bộ nhớ đệm; `uv` không gửi mật khẩu nào (không khai báo kho gói riêng). Mã băm `certifi` của phiếu này đã được đối chiếu qua 2 đường khác (`curl` dùng kho Windows; máy chủ ngoài), nên `uv.lock` của T-075 không bị ảnh hưởng | 1) **Nâng `uv` ≥ 0.13.4 trên cả 2 máy** (Chỉ Huy báo chủ dự án; làm ở mạng nhà hoặc công ty): `uv self update`, rồi `uv --version`. Lệnh cập nhật vẫn đi qua bộ chứng chỉ cũ của `uv`, nên chỉ chạy ở mạng tin cậy (một lần, rủi ro không đáng kể). 2) **Phiếu nhỏ** (Thợ Máy, `pyproject.toml`): thêm `required-version = ">=0.13.4"` vào `[tool.uv]` để `uv` cũ từ chối chạy. Đã thử trên dự án nháp với uv 0.12.23: `uv sync` và `uv run` đều dừng, mã thoát 2, câu báo «Required uv version `>=0.13.4` does not match the running version `0.12.23`. Update `uv` by running `uv self update`.»; khi đó `run.bat` hiện «Cai thu vien bi loi…», nên Thư Ký thêm vào README mục «Xử lý sự cố»: gặp câu này thì chạy `uv self update` (hoặc Thợ Máy cho `run.bat` / `run.command` tự cập nhật uv). Lá Chắn rút gọn kiểm. 3) **Trong lúc chờ:** agent không chạy `uvx`, `uv run --with`, `uv lock --upgrade-package` khi máy ở mạng lạ. **Hạn:** gấp (mỗi máy một lệnh); muộn nhất trước T-059 (thử thật) |

### Ghi nhận (không thành lỗi)

1. **Claude, ChatGPT đi qua kho chứng chỉ của hệ điều hành** (`httpx2/_config.py:40-41` → `truststore`), không qua `certifi`. Trên Windows, `truststore` mặc định **không kiểm thu hồi** (`truststore/_windows.py:366-371`: `chain_flags = 0` khi không bật `VERIFY_CRL_CHECK_*`), nên an toàn dựa vào danh sách chặn của Microsoft. Máy này: kho `ROOT`, `CA`, `AuthRoot` cục bộ không có gốc emSign nào; danh sách chặn tự động của Windows đồng bộ lần cuối **2026-10-21 11:27 (+07)** (registry `AuthRoot\AutoUpdate\DisallowedCertLastSyncTime`), sau ngày Microsoft được báo là đã chặn (20/10, theo InfoSec Today); không có chính sách tắt tự cập nhật. Tôi **chưa đối chiếu** từng chứng chỉ trong danh sách đó; Mac chưa kiểm (Apple được báo đã chặn 19/10). Vì vậy điều kiện (3) ở phần Tóm tắt là «Windows, macOS đã cập nhật». Lá Chắn đối chiếu 8 chứng chỉ khi kiểm phiếu của LC-T075-1.
2. Git (`http.sslBackend = schannel`) và `curl` (Schannel) trên máy này dùng kho Windows, không mang bộ chứng chỉ riêng.
3. Test của Soi Lỗi chạm vài thuộc tính bên trong thư viện (`_api_client._retry`, `httpcore._backends.sync`); khi nâng `google-genai`, `httpx`, `httpcore`, `urllib3` mà test hỏng vì cấu trúc thư viện đổi thì sửa chỗ thay thế, không bỏ test (R5). Soi Lỗi đã ghi ở đầu file.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` (đặt `PYTHONUTF8=1`) trên 5 file của diff: `results: {}`. Soát 3 commit `ddb9beb..f5f2bb6` (`git log -p`, mẫu `api_key|password|secret|token|AIza|sk-`): chỉ khóa giả `AIzaSy-khoa-gia-cua-soi-loi-T075` và mật khẩu giả `abcd EFGH …` trong `tests/test_soi_loi_t075.py` |
| S2 | Đạt | Không đổi code. Test Soi Lỗi: lỗi chứng chỉ ra câu cố định «Lỗi chứng chỉ bảo mật (SSL)…», không chứa mật khẩu ứng dụng |
| S3 | Không áp dụng | Không có biến cấu hình mới |
| W1 | Không áp dụng | Không đụng `seo_app/wordpress/` |
| W2 | Không áp dụng | Như W1 |
| W3 | Không áp dụng | Như W1 |
| W4 | Đạt | Kiểm chứng chỉ vẫn bật, `CERT_REQUIRED` trên cả 2 client (test Soi Lỗi); bộ gốc đã vá; timeout, URL không đổi |
| A1 | Không áp dụng | Không đụng prompt |
| A2 | Không áp dụng | Như A1 |
| A3 | Không áp dụng | Như A1 |
| U1 | Không áp dụng | Không đụng `app/` |
| U2 | Không áp dụng | Như U1 |
| U3 | Không áp dụng | Như U1 |
| F1 | Không áp dụng | Không đọc/ghi file của người dùng |
| F2 | Không áp dụng | Không đụng ảnh |
| F3 | Đạt | Test đọc `cacert.pem` bằng `encoding="utf-8"`; không `eval`, `pickle`, `yaml.load` |
| D1 | Đạt | Mục «Quét lỗ hổng toàn `uv.lock`»: 3 nguồn sạch, không thư viện mới. Công cụ `uv`: LC-T075-1 (ngoài phiếu) |
| D2 | Không áp dụng | `.gitignore` không đổi |
| D3 | Đạt | Mục «Soát test mới»: bộ chặn mạng chung bật; audit hook ghi 0 lần nối, tra tên, gửi gói ra mạng |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit (PyPI, OSV) | 0 lỗ hổng trên 69 gói | Có: đối chứng với `certifi` cũ báo đúng PYSEC-2026-4320 |
| Kho khuyến cáo GitHub | 0 (reviewed, unreviewed, malware) | Có: đối chứng lock cũ ra GHSA-6q48-6c7w-9gw2; thử bộ lọc phiên bản (pillow, requests) |
| bandit | Không chạy | Phiếu không đổi mã Python trong `seo_app/`, `app/`, `scripts/` (kiểm rút gọn D1, D3); cũng tránh tải thêm công cụ qua `uv` 0.12.23 (LC-T075-1) |
| detect-secrets (`PYTHONUTF8=1`) | 0 trên 5 file của diff | Có: chép `tests/test_soi_loi_t075.py` (có chữ tiếng Việt) ra thư mục nháp, thêm khóa mồi → bắt được `AWS Access Key`; cùng file **không** đặt `PYTHONUTF8` → 0 (đúng cảnh báo `security.md` mục 5); đã xóa file mồi |
| Soát lịch sử git | Sạch (mục S1) | Có |
| pytest (nhánh, `f5f2bb6`) | `tests/test_certifi_version.py`, `tests/test_soi_loi_t075.py`, `tests/test_wordpress_client.py`, `tests/test_app_pages.py`, 7 file `tests/test_ai*.py`: **929 passed** in 133,24 s (12:10:18–12:12:37), 0 hỏng, 0 bỏ qua | Không có lần «timed out» nào nên không phải chạy lại |
| pytest (cây gộp với `main`) | 1552 passed, 1 skipped, 39 xfailed, 0 hỏng (mục «Thử gộp») | Có |
| ruff 0.16.10 | `All checks passed!` trên nhánh và trên cây gộp | Có |

## Báo nhầm đã loại

- `pip-audit -s osv` (chỉ ở lượt đối chứng) in 2 dòng `PYSEC-2026-4320`: một lỗ hổng, hai bản ghi trùng.
- `pip-audit` cảnh báo nên dùng mã băm khi chạy `--no-deps`: không ảnh hưởng kết quả; `uv.lock` vẫn giữ mã băm và `uv sync` kiểm.
- Audit hook: `socket.bind(('::1', 0))` là cặp socket nội bộ của Windows; `http.client.connect` do `urllib3` phát sau khi đã nhận socket chưa nối từ hàm giả. Không có lần nối ra ngoài.
- Tìm chuỗi `BEGIN CERTIFICATE` trong `.venv` ra 11 file: mã đọc PEM (`google/auth/…`, `pyasn1_modules/pem.py`) và chuỗi hằng trong `arrow.dll`, `_rust.pyd`; không phải bộ chứng chỉ, và không file nào chứa G3 (mục LC-T061-1, dòng 5).

## Điều kiện

Không có điều kiện cho T-075.

Việc sau khi gộp (không chặn gộp): cả 2 máy mở app bằng `run.bat` / `run.command` để `uv sync` cài `certifi` 2026.10.19. Lời dặn «không dùng Wi-Fi công cộng» giữ tới khi đủ 3 việc ở phần Tóm tắt.

## Đề xuất

- **Chỉ Huy:** lập phiếu cho LC-T075-1 (nâng `uv` cả 2 máy; Thợ Máy thêm `required-version`; Thư Ký cập nhật README «Xử lý sự cố»), báo chủ dự án vì là nâng công cụ.
- **T-063** (chạy test trên Mac/Linux): thêm `tests/test_certifi_version.py`, `tests/test_soi_loi_t075.py` vào lượt chạy, để thay suy luận «chạy được trên Mac/Linux» bằng kết quả thật.
- **Lá Chắn (phiếu LC-T075-1):** đối chiếu 8 chứng chỉ trung gian bị lộ với danh sách chặn của Windows và macOS, để bỏ điều kiện (3) bằng bằng chứng thay vì tin công bố.

## Nguồn đã đọc (chỉ đọc, không gọi WordPress, AI, Google)

- `api.github.com/advisories/GHSA-6q48-6c7w-9gw2`; `github.com/astral-sh/uv/security/advisories/GHSA-hq85-5cpj-mr62`; `api.github.com/repos/astral-sh/uv/releases`
- `pypi.org/pypi/certifi/2026.10.19/json`
- `discuss.python.org/t/information-for-python-users-regarding-emudhra-emsign-ca-certificate-security-incident/109576`
- `infosectoday.io/eight-emudhra-ca-keys-compromised-triggering-emergency-fixes-across-browsers-and-software` (ngày chặn của Apple, Microsoft); tiêu đề bài `dev.to/frankchu/eight-ca-private-keys-were-integers-under-256-…` (chỉ đọc tiêu đề trong kết quả tìm kiếm)

Script thử (kiểm bộ chứng chỉ, so bộ gốc, tìm G3 trong `.venv` và trong `uv.exe`, kho Windows, plugin audit hook) để ngoài repo, không commit.

# Biên bản bảo mật T-078 (phần còn lại) · `uv` tối thiểu 0.13.4, bỏ AVIF, README nâng `uv`

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem dòng trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | `T-078-nang-uv.md` (đọc ở repo chính) · kiểm **rút gọn** (D1, D3), kèm việc phiếu ghi cho Lá Chắn: đối chiếu chứng chỉ trung gian bị lộ với danh sách chặn của Windows. Phiếu sinh từ LC-T075-1 ([Lá Chắn T-075](T-075-la-chan.md)) |
| Phạm vi | diff `a416e74..517f178` (nhánh `team/T-078`, 8 file): `pyproject.toml`, `seo_app/images/folders.py`, `tests/test_images_folders.py`, `tests/test_t078_avif_uv.py`, `README.md`, 3 báo cáo. Kèm `run.bat`, `run.command`, `.claude/hooks/session-start.sh`, công cụ `uv` trên máy, kho chứng chỉ Windows |
| Báo cáo đã đọc | [Thợ Máy](T-078-tho-may.md), [Thư Ký](T-078-thu-ky.md), [Soi Lỗi](T-078-soi-loi.md) (ĐẠT, 0 lỗi; GN-1 chuyển Lá Chắn) |
| Ngày | 2026-10-31 (07:50–08:30, giờ máy +07) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **2 Thấp** (LC-T078-1 = GN-1 của Soi Lỗi; LC-T078-2 câu README). **LC-T075-1 đóng trên máy Windows.** **Gộp vào `main` được ngay**: 2 điều kiện là sửa chữ trong tài liệu, không chặn gộp. Ngoài phiếu: LC-T078-3 (Thấp, toàn repo, có từ trước): `pyasn1` 0.6.4 có 4 khuyến cáo mới công bố sáng nay, app không có đường dùng tới |

## Tóm tắt (cho chủ dự án)

- **Phiếu an toàn, gộp được.** Phần mềm từ chối chạy với công cụ `uv` cũ hơn 0.13.4 (bản còn tin chứng chỉ bị lộ), ảnh AVIF không còn hiện trong khung chọn ảnh, README hướng dẫn nâng `uv` bằng tiếng Việt. Không có thư viện mới.
- **Máy Windows của anh/chị đã sạch lỗ hổng này.** Máy chỉ có một bản `uv` (0.13.4), và bộ chứng chỉ bên trong nó không còn cơ quan bị lộ. Tôi cũng đối chiếu xong với danh sách của chính Windows (Claude, ChatGPT, Git dùng danh sách này). Windows không còn tin cơ quan nào dẫn tới các khóa bị lộ, kể cả một đường «ký chéo» qua cơ quan khác mà tôi mới tìm ra hôm nay.
- **Lời dặn «không dùng Wi-Fi công cộng» bỏ được cho máy Windows**, vì đã đủ cả 3 việc đặt ra ngày 21/10. Máy Mac (khi có) làm lại các bước như README ghi.
- **Hai điểm nhỏ nên sửa chữ (không chặn gộp):**
  1. README nên dặn nâng `uv` ở mạng nhà hoặc công ty: bản `uv` cũ tải bản mới qua đúng kênh chứng chỉ bị lộ.
  2. Lớp chặn `uv` cũ không áp dụng cho lệnh `uvx` mà các agent dùng để chạy công cụ kiểm tra, nên cần một dòng quy tắc cho agent.
- **Việc ngoài phiếu (không gấp):** thư viện `pyasn1` (đi kèm thư viện Google) có lỗi mới công bố sáng nay. App không dùng tới phần bị lỗi (tôi đã thử). Nên nâng lên bản 0.6.5 ở một phiếu nhỏ; tôi đã thử trên bản sao: chỉ đổi đúng thư viện này, quét lại sạch.

## Trả lời 5 câu của Chỉ Huy

| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | LC-T075-1 đóng được trên máy Windows chưa? | **Đóng.** Mục «LC-T075-1 trên máy Windows» |
| 2 | Xử lý GN-1 thế nào? | **Quy tắc cho agent trong `docs/team/security.md` mục 5** (chỗ duy nhất bảo agent chạy `uvx`) và `.claude/agents/la-chan.md` bước 3; thêm nửa câu vào README phần người phát triển. **Không sửa hook**, **không cần ghi sổ rủi ro**. Chi tiết: LC-T078-1 |
| 3 | Đối chiếu 8 chứng chỉ trung gian bị lộ với danh sách chặn Windows còn cần không? | **Đã làm xong trong biên bản này**, không cần phiếu riêng. Kết quả: trên máy Windows không còn đường nào tới gốc được tin (mục «Đối chiếu với danh sách của Windows»). Máy Mac: làm khi có máy |
| 4 | README có dẫn người dùng làm gì nguy hiểm không? | **Không có bước nguy hiểm.** Đường dẫn `%USERPROFILE%\.local\bin\uv.exe`, `~/.local/bin/uv` đúng chỗ bộ cài chính thức đặt `uv`. Thiếu một câu dặn làm ở mạng tin cậy cho `uv self update` và `pip install --upgrade uv`: LC-T078-2 |
| 5 | Gộp thử với `main` cục bộ `3cdd096`? | **Không xung đột**; test chọn lọc trên cây gộp 366 qua, 0 hỏng (mục «Thử gộp») |

## Lỗi phát hiện (thay đổi của T-078)

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T078-1 | Thấp (= GN-1 của Soi Lỗi, **giữ mức ghi nhận → Thấp**) | `required-version` chỉ chặn lệnh dự án (`uv sync`, `uv run`, `uv run --with`, `uv lock`, `uv pip`), **không** chặn `uvx` / `uv tool run`: đúng lối LC-T075-1 nêu (tải công cụ không ghim mã băm). README phần người phát triển («bản cũ hơn bị từ chối») và chú thích `pyproject.toml` có thể khiến người đọc tưởng đã phủ cả `uvx` | `pyproject.toml:43`; `README.md:507`; quy định chạy `uvx`: `docs/team/security.md:127-140`, `.claude/agents/la-chan.md:25` | Tự thử lại (dự án nháp khai `>=0.13.5`, chạy bằng `uv 0.13.4`, `--offline`): `uv sync`, `uv run` dừng, mã 2, không tạo `.venv`; `uvx detect-secrets --version` và `uv tool run detect-secrets --version` **chạy**, in `1.5.0`, mã 0. Máy có `uv` cũ (phiên cloud có `uv` cũ hơn 0.13.4, máy Mac sau này chưa mở app) + agent chạy `uvx` theo `security.md` mục 5 + kẻ chen giữa đường mạng dùng khóa trung gian bị lộ → gói công cụ giả → mã chạy trên máy đó. **Hôm nay không có máy nào ở trường hợp này**: máy Windows đã 0.13.4 (mục dưới); chưa có máy Mac; phiên cloud thì hook `uv sync` tự dừng với câu `Required uv version` (`set -euo pipefail`), và cloud không có `.env` | **Chỉ Huy** (tài liệu đội): thêm vào `security.md` mục 5, ngay trên khối lệnh: «Trước khi chạy `uvx` / `uv tool run`: `uv --version` phải từ 0.13.4 (T-078, GHSA-hq85-5cpj-mr62). Thấp hơn thì không chạy, báo Chỉ Huy. `required-version` của dự án không chặn `uvx`.» Chép một dòng tương tự vào `.claude/agents/la-chan.md` bước 3. Không cần sửa `AGENTS.md` (không có lệnh `uvx`). **Thư Ký:** `README.md:507` thêm «(không áp dụng cho `uvx`: kiểm `uv --version` trước khi dùng)». **Không sửa hook:** hook đã dừng an toàn nhờ `required-version`; cho hook tự `uv self update` thì lại tải qua đúng kênh chứng chỉ cũ, không người trông. **Không cần ghi sổ rủi ro** khi đã có quy tắc. Hạn: trước phiên cloud tiếp theo (T-063 lượt Linux) hoặc trước khi có máy Mac |
| LC-T078-2 | Thấp | README bảo người có `uv` cũ chạy `uv self update` (hoặc `pip install --upgrade uv` / `pip3 install --upgrade uv`) mà không dặn làm ở mạng tin cậy. Với `uv` cũ, chính lệnh `uv self update` tải bản mới qua bộ chứng chỉ cũ còn gốc G3; `pip` dưới 26.2.2 cũng mang `certifi` cũ (discuss.python.org, 20/10). Cả hai không ghim mã băm | `README.md:33`, `:37` (Windows); `:53`, `:57` (Mac) | Máy còn `uv` cũ + người dùng nâng `uv` ở Wi-Fi công cộng có kẻ chen giữa đường → kẻ đó dùng khóa trung gian bị lộ giả `github.com` (`uv self update`) hay `pypi.org` (`pip`) → cài bản `uv` giả → mã chạy trên máy có `.env`. Hôm nay không có máy nào ở trường hợp này (Windows đã 0.13.4, chưa có Mac). Đây là lời dặn đã có ở T-075 («làm ở mạng nhà hoặc công ty») và trong phạm vi phiếu, nhưng chưa vào README | **Thư Ký:** thêm vào bước 3 của cả hai khối (và dòng `pip`): «Làm bước này ở mạng nhà hoặc công ty, không dùng Wi-Fi công cộng.» Không cần nêu bản `pip`. Sửa được ngay trên nhánh trước khi gộp, hoặc ở phiếu tài liệu nhỏ sau; không chặn gộp |

Không có lỗi Nghiêm trọng, Cao hay Trung bình. Phần `pyproject.toml` và bỏ AVIF không có lỗi bảo mật: bỏ một định dạng app vốn không mở được chỉ thu hẹp bề mặt, không mở đường mới (Soi Lỗi đã thử mọi đường: liệt kê, quét đệ quy, `ImageRef`, 5 hàm dựng ảnh, trang Soạn bài, nháp, kho thẻ).

## LC-T075-1 trên máy Windows: đóng

| Kiểm | Kết quả | Bằng chứng |
|---|---|---|
| Phiên bản | `uv 0.13.4 (7456b60bc 2026-10-20)`; `uvx 0.13.4` | `uv --version`, `uvx --version`, `uv self version`; biên lai cài đặt `%LOCALAPPDATA%\uv\uv-receipt.json`: `"version":"0.13.4"`, cài bằng bộ cài chính thức (cargo-dist) vào `C:\Users\ADMIN\.local\bin` |
| Chỉ một bản `uv` | Có | `where uv`, `Get-Command uv -All`: chỉ `C:\Users\ADMIN\.local\bin\uv.exe`. Tìm `uv.exe` trong các chỗ hay cài (Python, pipx, cargo, WinGet, scoop, Program Files, `%APPDATA%\uv\tools`): không có bản nào khác. `uv tool list`: «No tools installed». `uv.lock` không có gói `uv`; `.venv` của repo chính không có `uv.exe` |
| Bộ chứng chỉ trong `uv.exe` không còn G3 | Đạt | So byte DER (script T-075 chạy lại): `emSign ECC Root CA - G3` **không có** (bản 0.12.23 ngày 21/10: có); 3 gốc emSign không bị ảnh hưởng (G1, C1, ECC C3) còn, như `certifi` 2026.10.19; đối chứng ISRG Root X1: có. `uvx.exe` (345 KB) không mang chứng chỉ nào: nó gọi `uv.exe` cùng thư mục |
| Không còn đường ký chéo | Đạt | `uv.exe` không chứa gốc `AAA Certificate Services` lẫn `emSign Root TLS CA - G3` (mục dưới) |
| Khuyến cáo mới cho `uv` 0.13.4 | Không có | Kho khuyến cáo GitHub, `affects=uv@0.13.4`: 0. Đối chứng `affects=uv`: 8 khuyến cáo, có GHSA-hq85-5cpj-mr62 (`< 0.13.4`). Bản mới nhất 0.13.6 (27/10), không có khuyến cáo nào bắt buộc nâng |
| App thật đã nhận `certifi` đã vá | Có | `.venv` của repo chính: `certifi` 2026.10.19 (cài 2026-10-21 13:38), không còn nhãn G3 |

**Công cụ tải bằng `uv` cũ trước 21/10** (bộ nhớ đệm của `uvx`: `detect-secrets`, `pip-audit`…): không cần làm lại. Muốn bị tráo thì phải có kẻ chen giữa mạng nhà hoặc công ty trong vài ngày đó; gói của dự án thì luôn được `uv sync` kiểm mã băm (đã thử ở T-075).

## Đối chiếu với danh sách của Windows (việc phiếu ghi cho Lá Chắn)

**8 chứng chỉ bị lộ** gồm 6 chứng chỉ trung gian TLS và 2 chứng chỉ ký mã. Hai chứng chỉ ký mã không dùng cho kết nối HTTPS nên ngoài phạm vi. Danh sách 6 chứng chỉ TLS lấy từ dữ liệu chặn công khai OneCRL của Mozilla (bug 2083382):
- 17/10: chặn 6 chứng chỉ theo người cấp và số seri, người cấp `emSign Root TLS CA - G3`;
- 21/10: chặn thêm theo chủ thể và khóa: `EM DV/EV/OV TLS CA - G3B` (eMudhra BV), `EM DV/EV/OV TLS CA - G3C` (eMudhra Inc).

Tra crt.sh theo dấu khóa (SHA-256 của khóa công khai): **mỗi khóa có 2 chứng chỉ**, tổng 12:

| Bản | Người cấp | Hạn | Đi tới gốc nào |
|---|---|---|---|
| 6 chứng chỉ | `emSign Root TLS CA - G3` | 2040 | `emSign Root TLS CA - G3` có 2 bản: tự ký (gốc riêng), và một bản do `emSign ECC Root CA - G3` cấp. crt.sh không có bản nào khác, nên **không** đi tới 3 gốc emSign còn lại (G1, C1, ECC C3) |
| 6 chứng chỉ **ký chéo** | `AAA Certificate Services` (Comodo/Sectigo) | 31/12/2028 | Gốc `AAA Certificate Services`. Đây là đường mới, Mozilla chặn thêm ngày 21/10 |

Một nơi chỉ an toàn khi **không tin cả 3 gốc** `emSign ECC Root CA - G3`, `emSign Root TLS CA - G3`, `AAA Certificate Services`:

| Nơi | `emSign ECC Root CA - G3` | `emSign Root TLS CA - G3` | `AAA Certificate Services` | Kết luận |
|---|---|---|---|---|
| `certifi` 2026.10.19 (client WordPress, Gemini) | Không | Không | Không (cả bản cũ 2026.7.22 cũng không) | An toàn: đường ký chéo **không** vượt được bản vá T-075 |
| `uv.exe` 0.13.4 | Không | Không | Không | An toàn |
| Windows: danh sách gốc tự động của Microsoft (registry `AuthRoot\AutoUpdate\EncodedCtl`, 555 gốc, mốc thời gian trong danh sách 2026-10-23 23:18 UTC, máy đồng bộ lần cuối 2026-10-31 07:31 +07) | Không | Không | Không | An toàn |
| Windows: kho gốc trên máy (`ROOT`, `CA`, `AuthRoot`) | Không | Không | Không | An toàn |

- **Bộ đọc danh sách đã được thử** trên các gốc chắc chắn có trong danh sách: ISRG Root X1, DigiCert Global Root G2, GTS Root R1, USERTrust RSA, COMODO RSA, và emSign G1, C1, ECC C3. Cả 8 đều có, chỉ riêng `emSign ECC Root CA - G3` vắng. Nghĩa là Microsoft đã gỡ G3 (hoặc chưa từng nhận), còn 3 gốc emSign không bị ảnh hưởng thì vẫn tin, đúng như `certifi` và `uv`.
- **Danh sách chặn tự động của Windows** (`DisallowedCertEncodedCtl`, 96 mục): mã định danh dài 16 và 48 byte, không phải dấu SHA-1 như tôi giả định. Tôi chưa đọc được cách Windows ghi mục chặn nên không kết luận từ danh sách này. Không cần: chuỗi chứng chỉ đã không tới được gốc nào Windows tin.
- **Hệ quả:** trên máy Windows này, kết nối của Claude, ChatGPT (`truststore`, dùng bộ kiểm của Windows; Windows mặc định không kiểm thu hồi, `truststore/_windows.py:366-371`), Git (`schannel`), `curl`, PowerShell đều không nhận chứng chỉ giả ký bằng 6 khóa bị lộ. **Điều kiện (3) của lời dặn Wi-Fi đạt cho Windows**, bằng bằng chứng chứ không còn dựa vào tin công bố.
- Điều kiện (1) và (2) cũng đạt cho Windows: `certifi` 2026.10.19 trong app thật (bảng trên); `uv` 0.13.4. Mac: chưa có máy, làm khi có: README mục 3, `required-version`, và đối chiếu kho macOS.

## Thử gộp với `main`

| Gộp với | Kết quả |
|---|---|
| `main` cục bộ `3cdd096` (đã có T-102) | `git merge-tree --write-tree`: không xung đột (cây `24d988d`). Từ `a416e74`, `main` sửa `tests/test_app_images.py` (28 dòng) mà test mới `tests/test_t078_avif_uv.py` nhập hàm từ đó, nên chạy thật: worktree tạm trong thư mục nháp (commit treo `a851b30`, không đẩy, đã gỡ), `uv sync --frozen`, kiểm `seo_app` nạp từ chính worktree tạm, `IMAGE_EXTENSIONS` = `.jpeg .jpg .png .webp`. `tests/test_t078_avif_uv.py`, `tests/test_images_folders.py`, `tests/test_t107_heic_tat.py`, `tests/test_app_images.py`: **366 passed, 11 skipped, 0 hỏng** (6 phút 8 giây, 07:55–08:02, máy đang chạy toàn bộ test trên `main`). 11 bỏ qua là ca chỉ chạy trên Mac/Linux hoặc cần quyền tạo symlink. `ruff`: sạch |
| `origin/main` `a416e74` (gốc nhánh) | Không xung đột (cây `67b4a2f`) |

`main` không đổi `pyproject.toml`, `uv.lock`, `README.md`, `seo_app/images/`, `.claude/` kể từ `a416e74`. **Gộp được ngay.**

## Phát hiện toàn repo (ngoài phạm vi phiếu, không tính vào kết luận)

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T078-3 | Thấp (toàn repo, có từ trước, không do T-078; GitHub xếp High) | `pyasn1` 0.6.4 có 4 khuyến cáo mới: GHSA-fm9c-5rcf-2q5p, GHSA-9m75-vc3g-4x39, GHSA-mm57-4v3p-rchx, GHSA-2qm8-x737-gmw5 (CVE-2026-119194 → 119197). Kho GitHub công bố 2026-10-30 23:03–23:07 UTC, tức sáng nay giờ Việt Nam. Giải mã dữ liệu ASN.1 (BER/CER/DER) dựng cố ý làm CPU chạy lâu theo bình phương cỡ dữ liệu (treo, không lộ gì). Vá ở 0.6.5 (PyPI 27/10) | `uv.lock` (`pyasn1` 0.6.4, có trên `main`); chuỗi phụ thuộc: `pyasn1` ← `pyasn1-modules` 0.4.2 ← `google-auth` 2.62.0 ← app và `google-genai` | **Hôm nay không có đường đi.** Trong cả `.venv`, chỉ `google/auth/crypt/_python_rsa.py` nhập `pyasn1`. File này chỉ được dùng khi khóa là đối tượng của gói `rsa`, mà gói `rsa` **không có** trong `uv.lock`. `google-auth` 2.62 dựng khóa từ chuỗi luôn bằng `cryptography` (`google/auth/crypt/rsa.py:73`, `:129`). Tự thử: dựng `Credentials.from_service_account_info` với khóa RSA giả tạo tại chỗ, nhập `seo_app.google.service_account`, `seo_app.google.sheets`, ký thử một chuỗi → bộ ký là `_cryptography_rsa`, **`pyasn1` không được nạp**. Khóa tài khoản dịch vụ do chính người dùng chọn, không phải dữ liệu từ ngoài | Phiếu nhỏ (Thợ Máy; Chỉ Huy quyết có hỏi chủ dự án không, vì là nâng thư viện phụ, bản vá nhỏ): `uv lock --upgrade-package pyasn1`. Đã thử trên bản sao `pyproject.toml` + `uv.lock` trong thư mục nháp: `Updated pyasn1 v0.6.4 -> v0.6.5`, chỉ khối `pyasn1` đổi (3 dòng), vẫn 70 gói; `pip-audit` PyPI và OSV trên bản sao: `No known vulnerabilities found`, mã 0. Không gấp; nên làm trước lượt gộp tiếp theo có đổi `uv.lock` (ví dụ T-111), để các biên bản sau quét sạch |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` (đặt `PYTHONUTF8=1`) trên 8 file của diff: `results: {}`. Mồi khóa giả trong bản sao README (chữ tiếng Việt): bắt được 1; cùng file không đặt `PYTHONUTF8`: 0, đúng cảnh báo `security.md` mục 5; đã xóa mồi. Soát 3 commit `a416e74..517f178`: chỉ có chữ `set_password`, `detect-secrets`, không có khóa |
| S2 | Không áp dụng | Câu báo mới (`folders.py:523`, `:525`) là chữ cố định, không chứa đường dẫn hay bí mật |
| S3 | Không áp dụng | Không có biến cấu hình mới |
| W1 | Không áp dụng | Không đụng `seo_app/wordpress/` |
| W2 | Không áp dụng | Như W1 |
| W3 | Không áp dụng | Như W1 |
| W4 | Không áp dụng | Không đụng client mạng của app; phần TLS của công cụ `uv`: mục LC-T075-1 |
| A1 | Không áp dụng | Không đụng prompt |
| A2 | Không áp dụng | Như A1 |
| A3 | Không áp dụng | Như A1 |
| U1 | Không áp dụng | Không đụng `app/` |
| U2 | Không áp dụng | Như U1 |
| U3 | Không áp dụng | Như U1 |
| F1 | Đạt | Bỏ `.avif` khỏi `IMAGE_EXTENSIONS` (`folders.py:62`) chỉ thu hẹp danh sách; lớp chặn `..`, symlink, junction không đổi; `tests/test_images_folders.py` 285 qua cùng test mới |
| F2 | Đạt | Giới hạn 40 MB không đổi; AVIF đổi đuôi bị từ chối theo nội dung ở cả 4 hàm dựng ảnh (test mới) |
| F3 | Đạt | Test đọc `pyproject.toml` bằng `tomllib`, `encoding="utf-8"`; không `eval`, `pickle` |
| D1 | Đạt (đã xác minh) | `uv.lock` không đổi (cả nhánh lẫn `main` so với `a416e74`); `uv lock --check` đạt; `required-version` không phải thư viện. Quét 69 gói: chỉ `pyasn1` (LC-T078-3, không do phiếu, không có đường đi) |
| D2 | Không áp dụng | `.gitignore` không đổi |
| D3 | Đạt | `tests/test_t078_avif_uv.py` + `tests/test_images_folders.py` chạy dưới audit hook (plugin pytest nháp, không commit): 15 sự kiện mạng, **cả 15 là 127.0.0.1** (cặp socket nội bộ của asyncio trong AppTest, bộ chặn chung cho qua); 0 `getaddrinfo`, 0 nối ra ngoài. Ảnh AVIF dựng trong bộ nhớ; chạy được trên Mac/Linux (không có mã riêng Windows; ca riêng hệ điều hành dùng `skip` có sẵn) |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit 2.10.1 (PyPI, OSV) | 69 gói, 0 bỏ qua: 4 lỗ hổng, đều ở `pyasn1` 0.6.4 (LC-T078-3) | Có: đọc mã, thử đường nạp; bản sao nâng 0.6.5 thì 0 |
| Kho khuyến cáo GitHub | reviewed: 4 (cùng `pyasn1`); unreviewed 0; malware 0. `uv@0.13.4`: 0 | Có |
| bandit | Không chạy | Phần mã đổi chỉ là hằng số và chuỗi báo (`folders.py`); kiểm rút gọn D1, D3 |
| detect-secrets (`PYTHONUTF8=1`) | 0 trên 8 file | Có (mồi) |
| Soát lịch sử git | Sạch (S1) | Có |
| pytest (nhánh `517f178`) | `tests/test_t078_avif_uv.py`, `tests/test_images_folders.py`: **285 passed, 11 skipped** (29,6 s, 08:00–08:01). Máy đang chạy toàn bộ test trên `main` nên chỉ chạy chọn lọc; Soi Lỗi đã chạy 11 file (1324 qua) | Có |
| pytest (cây gộp với `main` `3cdd096`) | 366 passed, 11 skipped, 0 hỏng | Có |
| ruff 0.16.10 | `All checks passed!` trên nhánh và trên cây gộp | Có |

## Báo nhầm đã loại

- Audit hook ghi `socket.bind` / `socket.connect` tới `127.0.0.1`: cặp socket nội bộ Windows tạo cho vòng lặp asyncio (Streamlit AppTest); `tests/conftest.py` chỉ cho qua đúng cặp này.
- Soát lịch sử khớp chữ `set_password` (tên file), `detect-secrets` (tên công cụ): không phải bí mật.
- `seo_app/wordpress/client.py:626` còn `".avif": "image/avif"`: danh sách loại file **tải lên** WordPress. App chỉ tải WebP do `make_web_image` dựng; trang Kết nối không còn ô tải nguyên ảnh (T-106). Không có đường đưa AVIF lên.

## Điều kiện

| # | Việc | Ai | Hạn |
|---|---|---|---|
| 1 | LC-T078-1: quy tắc kiểm `uv --version` trước `uvx` trong `security.md` mục 5 và `.claude/agents/la-chan.md`; nửa câu ở `README.md:507` | Chỉ Huy (tài liệu đội), Thư Ký (README) | Trước phiên cloud tiếp theo hoặc trước khi có máy Mac |
| 2 | LC-T078-2: câu «làm ở mạng nhà hoặc công ty» ở bước nâng `uv` (`README.md:33`, `:37`, `:53`, `:57`) | Thư Ký | Cùng lúc với điều kiện 1; có thể làm ngay trên nhánh trước khi gộp |

Không điều kiện nào chặn gộp. Lá Chắn kiểm rút gọn khi sửa (chỉ đọc chữ).

## Đề xuất

- **Chỉ Huy:** lập phiếu nhỏ cho LC-T078-3 (`pyasn1` 0.6.5), gom với lượt đổi `uv.lock` gần nhất.
- **Chỉ Huy:** ghi vào `docs/team/dong-bo.md` hoặc bảng tiến độ rằng lời dặn «không dùng Wi-Fi công cộng» đã bỏ được cho máy Windows (đủ 3 điều kiện có bằng chứng ở biên bản này).
- **Khi có máy Mac** (phần Mac của T-078): `uv --version` ≥ 0.13.4 trước khi chạy `uvx`; mở app bằng `run.command` (`required-version` chặn `uv` cũ); Lá Chắn đối chiếu kho chứng chỉ macOS với 3 gốc ở bảng trên. Lưu ý thêm: `curl` có sẵn của macOS có bộ chứng chỉ riêng, nên đối chiếu cả bộ đó.
- **Về sau (không gấp):** nếu muốn bỏ hẳn lối tải công cụ không ghim mã băm, có thể đưa `pip-audit`, `detect-secrets`, `bandit` vào nhóm `dev` của `pyproject.toml` (khi đó `uv.lock` ghim mã băm và `required-version` chặn được). Đây là thêm thư viện vào dự án, trái với ghi chú «chạy tạm, không thêm vào thư viện của dự án» ở `security.md` mục 5, nên phải hỏi chủ dự án. Hiện quy tắc ở điều kiện 1 là đủ.

## Nguồn đã đọc (chỉ đọc, không gọi WordPress, AI, Google)

- Kho khuyến cáo GitHub qua `gh api advisories` (`affects` = 69 gói của `uv.lock`, `uv@0.13.4`, `uv`); `api.github.com/repos/astral-sh/uv/releases`
- `pypi.org/pypi/pyasn1/json`
- Dữ liệu chặn OneCRL của Mozilla: `firefox.settings.services.mozilla.com/v1/buckets/security-state/collections/onecrl/changeset` (bug 2083382)
- `crt.sh` (tra theo dấu khóa, theo tên `emSign Root TLS CA - G3`, `AAA Certificate Services`; tải 15 chứng chỉ công khai)
- Registry của máy (chỉ đọc): `HKLM\SOFTWARE\Microsoft\SystemCertificates\AuthRoot\AutoUpdate`

Script thử (đối chiếu danh sách Windows, đọc danh sách tự động, tìm gốc trong `uv.exe` và `certifi`, đường nạp `pyasn1`, plugin audit hook) để ngoài repo, không commit; bản sao ở thư mục ghi chú chung `T-078-la-chan-scripts/`.

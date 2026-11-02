# Biên bản bảo mật T-105 · `set_password`: câu báo đúng nguyên nhân khi đọc lại lỗi, dừng khi biến môi trường đè `.env`

> **Model:** chạy bằng Claude Opus 5.5 (phiên này chưa chuyển sang Fable). Hồ sơ vai khuyên Claude Fable 5.1; mốc 01/11 đã qua nên cần kiểm lại bằng Fable.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (xem dòng trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-105](../tickets/T-105-set-password-cau-bao-bien-moi-truong.md) (đọc ở repo chính) · kiểm **rút gọn** (U3, F3). Đóng SL-T104-1, SL-T104-2 ([Soi Lỗi T-104](T-104-soi-loi.md), [Lá Chắn T-104](T-104-la-chan.md)) |
| Phạm vi | diff `731a46e..4771521` (nhánh `team/T-105`, 7 file): `seo_app/env_file.py`, `scripts/hash_password.py`, `tests/test_t105_set_password.py` (mới), `tests/test_soi_loi_t105.py` (mới), `tests/test_soi_loi_t104.py` (gỡ 2 dấu `xfail`), 2 báo cáo. Kèm code xung quanh: `_read_env_text`, `_atomic_write`, `load_settings` (`seo_app/config.py`), trang Cài đặt (`app/views/settings.py`, nơi bắt `EnvFileError`), `set_password.bat`, `set_password.command`, `tests/conftest.py` |
| Báo cáo đã đọc | [Thợ Máy](T-105-tho-may.md), [Soi Lỗi](T-105-soi-loi.md) (ĐẠT CÓ ĐIỀU KIỆN, 1 Thấp mới SL-T105-1) |
| Ngày | 2026-11-02 (07:28–07:50, giờ máy +07) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (SL-T105-1, có từ T-104, đồng ý mức). **SL-T104-1, SL-T104-2 đóng.** **Gộp vào `main` được ngay**: SL-T105-1 không cần sửa trước khi gộp, làm ở phiếu nhỏ sau. Không có lỗi mới của Lá Chắn |

## Tóm tắt (cho chủ dự án)

- **An toàn, gộp được.** Công cụ đặt mật khẩu nay nói đúng sự thật trong hai tình huống hiếm.
  - Phần mềm khác giữ file `.env` đúng lúc lưu: công cụ báo đúng là không đọc lại được để kiểm, file cũ còn nguyên. Nếu cả việc trả bản cũ cũng không được, công cụ báo «chưa chắc đã lưu».
  - Máy có đặt biến môi trường `APP_PASSWORD_HASH`: công cụ dừng ngay, chưa hỏi mật khẩu, và chỉ cách gỡ biến. Không còn chuyện báo «Đã lưu» trong khi mật khẩu cũ vẫn dùng được.
- **Không lộ gì:** tôi thử 5 tình huống. Không câu nào in mã băm, giá trị biến môi trường hay đường dẫn thư mục, không câu nào hiện lỗi kỹ thuật dài. Tôi cũng kiểm riêng là chạy test không đụng tới file `.env` thật của anh/chị.
- **Còn một điểm nhỏ (mức Thấp, có từ trước):** nếu một chương trình khác sửa `.env` đúng phần nghìn giây công cụ vừa lưu, công cụ báo nhầm nguyên nhân là «dòng sai định dạng». Tôi thấy thêm: lúc đó công cụ trả file về bản cũ, nên thay đổi của chương trình kia cũng bị bỏ. Rất hiếm (phải hai việc lưu trùng nhau gần như cùng lúc), không làm lộ hay hỏng mật khẩu. Nên sửa ở một phiếu nhỏ sau, không cần chờ.

## Trả lời câu hỏi của Chỉ Huy

| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | SL-T104-1, -2 đóng? | **Đóng.** Hai test của Soi Lỗi T-104 bỏ dấu `xfail` nay qua thật (diff chỉ xóa 2 khối dấu, R5). Tôi tự thử lại độc lập (bảng «Thử độc lập», ca a, b, c) |
| 2 | Câu báo không in giá trị `APP_PASSWORD_HASH`, đường dẫn, traceback? | **Đúng** với mọi câu báo lỗi. Các câu là hằng; chỗ chèn duy nhất là **tên loại lỗi** (`PermissionError`…), lấy từ `type(exc).__name__` hay `error_name` (`env_file.py:284-291`). Thử 5 ca, dò từng câu: 0 lần lộ giá trị biến (giá trị dấu riêng), mã băm, đường dẫn thư mục, `Traceback`. Hai chỗ in có chủ đích, có từ trước: `--print` in mã băm (chính là việc của chế độ này) và câu thành công «Đã lưu mật khẩu mới vào <đường dẫn .env>» (file của chính người dùng; Soi Lỗi GN-2) |
| 3 | `.env` vẫn ghi nguyên tử, không lộ mã băm qua câu báo hay log? | **Đúng.** `_atomic_write` không đổi (file tạm cùng thư mục, `fsync`, `os.replace`). Bước bỏ bản vừa ghi cũng dùng nó, hoặc `unlink` khi trước đó chưa có `.env`. Không sót `.env.*.tmp` ở mọi ca. Không có `logging` trong `env_file.py` lẫn `hash_password.py` |
| 4 | Mức SL-T105-1, có cần sửa trước khi gộp không? | **Thấp, đồng ý; không cần sửa trước khi gộp.** Kèm một hệ quả tôi thấy thêm và cách sửa đề xuất (mục «Đánh giá SL-T105-1») |
| 5 | Gộp thử với `origin/main`? | `origin/main` = `731a46e` = gốc nhánh, nên gộp không có gì đổi. Gộp với `main` cục bộ mới hơn (`4ee27d8`, có T-110 lượt 2–3): **không xung đột**; test chọn lọc trên cây gộp 297 qua, 0 hỏng (mục «Thử gộp») |

Trước khi dùng `uvx` tôi đã kiểm `uv --version`: `uv 0.13.4` (LC-T078-1).

## Lỗi phát hiện

Không có lỗi mới của Lá Chắn. Đánh giá lỗi Soi Lỗi ở mục dưới.

## Đánh giá SL-T105-1

| Mục | Ý kiến Lá Chắn |
|---|---|
| Mức | **Thấp, đồng ý** (có từ T-104, không do T-105) |
| Tái hiện | Thử độc lập ca d: chương trình khác ghi thêm một dòng vào `.env` ngay sau khi bộ ghi thay file. Kết quả: mã thoát 1; câu «Chưa lưu mật khẩu mới. File .env có dòng sai định dạng…»; `.env` trở về **đúng từng byte** bản trước khi lưu; mật khẩu cũ vẫn là mật khẩu có hiệu lực |
| Thấy thêm | Bước «trả bản cũ» viết đè luôn thay đổi của chương trình kia: dòng nó vừa thêm **mất** (`False` ở ca d). Đây là hệ quả của Quan sát 2 ở Lá Chắn T-104 (hai bộ ghi không khóa lẫn nhau, lần thay sau thắng). Ca thật: trang Cài đặt lưu khóa AI đúng lúc `set_password` đọc lại; trang báo đã lưu khóa nhưng khóa bị bước trả bản cũ xóa |
| Vì sao vẫn Thấp | Không lộ mã băm hay khóa; không có câu «Đã lưu» sai (công cụ báo thất bại, người dùng chạy lại); file luôn ở một trạng thái hợp lệ; cần hai việc ghi trùng nhau trong vài phần nghìn giây, do cùng một người làm |
| Sửa trước khi gộp? | **Không.** Phiếu nhỏ sau (Thợ Máy). Gỡ 2 `xfail(strict=True)` trong `tests/test_soi_loi_t105.py` khi XPASS (R5) |
| Cách sửa đề xuất | Bổ sung gợi ý của Soi Lỗi. Trong `_write_value`, khi đọc lại **được** mà khác, so chữ đọc lại với `content` vừa ghi. **Khác chữ** nghĩa là có chương trình khác vừa ghi sau mình: **không trả bản cũ** (để khỏi xóa thay đổi của chương trình kia) và báo câu riêng, kiểu «File .env vừa bị chương trình khác thay đổi đúng lúc lưu; chưa chắc đã lưu được giá trị mới. Đóng chương trình đó rồi lưu lại». `set_password` dùng nhánh «Chưa chắc đã lưu…» (`UnsureSaveError`). **Giống chữ mà đọc ra khác** mới là lỗi định dạng: giữ câu và bước trả bản cũ như cũ. Thêm test: thay đổi của chương trình kia còn nguyên |

## Thử độc lập (script nháp, `.env` giả trong thư mục nháp, mã thật của nhánh)

Gọi `main` của `scripts/hash_password.py` và `set_api_key` của bộ ghi dùng chung. Mỗi ca dò câu báo (stdout và stderr) tìm: giá trị biến môi trường (dấu riêng `…DAU-RIENG-BIEN-MOI-TRUONG…`), chuỗi `pbkdf2_sha256:`, mã băm vừa tạo, đường dẫn thư mục `.env`, chữ `Traceback`. Đối chiếu bằng `load_settings` xem mật khẩu nào đang có hiệu lực.

| Ca | Mã thoát | `.env` sau đó | Mật khẩu có hiệu lực | File tạm sót | Lộ | Câu báo (đầu câu) |
|---|---|---|---|---|---|---|
| a. Biến `APP_PASSWORD_HASH` (giá trị dấu riêng) | 1 | Giữ nguyên từng byte | Cũ | Không | Không | «Chưa đặt được mật khẩu. Máy này đang có biến môi trường APP_PASSWORD_HASH…» (kèm 3 bước gỡ biến). **Không hỏi mật khẩu lần nào** |
| a2. Như a, chạy `--print` | 0 | Giữ nguyên | Cũ | Không | Không lộ giá trị biến (mã băm mới in ra là việc của `--print`) | Dòng mã băm + «Lưu ý: máy này đang có biến môi trường…» |
| b. Đọc lại lỗi (`PermissionError`) ngay sau khi thay | 1 | Giữ nguyên từng byte | Cũ | Không | Không | «Chưa lưu mật khẩu mới. Không đọc lại được file .env để kiểm sau khi ghi (PermissionError) nên đã bỏ bản vừa ghi. File .env cũ vẫn còn nguyên…» |
| c. Như b, trả bản cũ cũng lỗi | 1 | **Đã đổi** | **Mới** | Không | Không | «Chưa chắc đã lưu được mật khẩu mới… file .env có thể đã mang mật khẩu mới nhưng chưa được kiểm…»: **đúng sự thật** (không nói «còn nguyên») |
| d. SL-T105-1: chương trình khác sửa `.env` đúng lúc | 1 | Giữ nguyên từng byte (thay đổi của chương trình kia mất) | Cũ | Không | Không | «Chưa lưu mật khẩu mới. File .env có dòng sai định dạng…» (sai nguyên nhân: SL-T105-1) |
| e. Trang Cài đặt (`set_api_key`, khóa giả), đọc lại lỗi | (ngoại lệ `EnvFileReadBackError`) | Giữ nguyên | | | Không lộ khóa, không lộ đường dẫn | «Không đọc lại được file .env để kiểm sau khi ghi (PermissionError) nên đã bỏ bản vừa ghi, file .env vẫn như trước khi lưu…» |

Trang Cài đặt bắt lỗi mới qua `except env_file.EnvFileError` có sẵn (`app/views/settings.py:52`, `:72`, `:557`; lớp mới là lớp con), hiện `str(exc)` là câu cố định: không traceback trên giao diện. Soi Lỗi đã thử khóa file thật của Windows (4 kiểu chia sẻ) và chạy thật `set_password.bat` với 5 dạng biến; tôi không lặp lại.

## U3 · Mật khẩu

- **Cách băm, cách so không đổi:** `git diff 731a46e..4771521 -- seo_app/auth.py seo_app/config.py app/` trống.
- **SL-T104-2 đóng đúng ý U3.**
  - `password_hash_overridden` (`env_file.py:421-431`) dùng đúng điều kiện của `load_settings`: biến **có mặt** là đè, kể cả rỗng. Hàm chỉ trả đúng/sai.
  - `main` kiểm điều kiện này **trước** khi đọc `.env` và trước khi hỏi mật khẩu (`hash_password.py:173-178`).
  - Vì vậy không còn đường nào để công cụ báo «Đã lưu» trong khi app vẫn nhận mật khẩu cũ.
  - Chọn «từ chối» thay vì «lưu rồi nhắc» là cách an toàn hơn: `.env` không mang một mật khẩu chưa dùng tới, mà nhiều tháng sau tự có hiệu lực khi ai đó gỡ biến.
- **Biến rỗng:** app dùng mã băm rỗng, tức chưa đặt mật khẩu, nên không vào được chức năng nào (`security.md` 2.5). Công cụ báo «bị đè» cho ca này là đúng.
- **Không lộ:** không chỗ nào đọc giá trị biến ra; câu dặn gỡ biến là hằng, test ghim không có `{}`.
- **Câu «Đã lưu» chỉ in khi** bộ ghi đã đọc lại và parse ra đúng giá trị mới (`_write_value`).

## F3 · Đọc/ghi file

- Đọc, ghi `.env` vẫn `encoding="utf-8"`, `newline=""` (`env_file.py:166`, `:317`); không `eval`, `pickle`.
- `_read_env_text` vẫn từ chối liên kết tắt (symlink).
- Đọc lại mà gặp liên kết tắt (bị tráo sau khi thay) nay ra `EnvFileReadBackError` với tên loại lỗi `EnvFileError`, không chép câu gốc (test `[lien-ket-tat]`; Soi Lỗi đột biến N8 bị bắt).
- Ca lỗi kép «chưa có `.env`, đọc lại thấy khác, xóa file vừa tạo cũng lỗi» trước đây bị bỏ qua lặng lẽ rồi báo «đã giữ nguyên file cũ». Nay báo `_RESTORE_FAILED`, đúng hơn, có test.

## D3 · Test không gọi mạng, không đụng `.env` thật

- Test mới chỉ dùng `.env` trong `tmp_path`.
  - `scripts/hash_password.py`: test thay `DEFAULT_ENV_FILE` của module script (`tests/test_t105_set_password.py:57`, `tests/test_soi_loi_t105.py:61`).
  - Trang Cài đặt: test thay `config.DEFAULT_ENV_FILE` (`tests/test_soi_loi_t105.py:83`).
  - `tests/conftest.py:191-202` (tự chạy) gỡ mọi biến trong `config.ENV_VARS`, kể cả `APP_PASSWORD_HASH`, trước mỗi test.
- **Kiểm thật:** trên cây gộp, đặt một `.env` canh (giả) ở gốc dự án, giống repo chính có `.env` thật khi Chỉ Huy chạy toàn bộ test. Chạy 11 file test (mục «Thử gộp»): `.env` canh **không đổi** (SHA-256 `ce8a36d4…`, giờ sửa giữ nguyên); không có `.env.*.tmp` ở gốc.
- Audit hook (plugin pytest nháp, không commit) trên cùng lượt chạy: 197 sự kiện, **cả 197 là `127.0.0.1`** (cặp socket nội bộ của asyncio trong test trang Cài đặt và app). 0 lần tra tên, 0 lần nối ra ngoài.
- 2 ca khóa file thật của Windows (`msvcrt`) có chạy trên máy này: `tests/test_t105_set_password.py` + `tests/test_soi_loi_t104.py` 53 qua, 0 bỏ qua.

## Thử gộp

| Gộp với | Kết quả |
|---|---|
| `origin/main` `731a46e` | Là gốc nhánh: `git merge-tree` cho cây `3aa1e9c` (= cây nhánh), không xung đột |
| `main` cục bộ `4ee27d8` (có T-110 lượt 2–3: `seo_app/wordpress/client.py`, `app/views/write.py`, test WordPress, ảnh) | Không xung đột (cây `5480f30`); `main` không đụng file nào T-105 sửa hay dùng. Chạy thật trên worktree tạm (commit treo `fa701f4`, không đẩy, đã gỡ), `uv sync --frozen`, 11 file: `tests/test_t105_set_password.py`, `tests/test_soi_loi_t105.py`, `tests/test_soi_loi_t104.py`, `tests/test_t104_set_password.py`, `tests/test_hash_password_script.py`, `tests/test_env_file.py`, `tests/test_settings_keys.py`, `tests/test_auth.py`, `tests/test_la_chan_t090.py`, `tests/test_soi_loi_t090.py`, `tests/test_t090_env_bang_ma.py`. Kết quả: **297 passed, 4 skipped, 2 xfailed, 0 hỏng** (334 s, 07:33–07:39). 4 bỏ qua là ca riêng Mac/Linux (quyền 600, symlink) có từ trước; 2 `xfail` đúng là SL-T105-1 (`strict`). `ruff`: sạch |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` (đặt `PYTHONUTF8=1`) trên 7 file của diff: 1 mục `Secret Keyword` ở `seo_app/env_file.py:58`. Đó là dòng khai hằng `PASSWORD_HASH_VAR`, giá trị chỉ là tên biến môi trường; không phải bí mật, có từ trước (`main` dòng 54) (mục Báo nhầm). Mồi khóa giả trong bản sao file test (có chữ tiếng Việt): bắt được 1; không đặt `PYTHONUTF8`: 0; đã xóa mồi. Soát 3 commit `731a46e..4771521` (dòng thêm vào, mẫu mã băm `pbkdf2_sha256:<số>:<chuỗi>`, khóa `sk-ant-`, `AIza`, khóa riêng PEM): 0. Mã băm trong test được tạo lúc chạy, không ghi cứng |
| S2 | Đạt | Mục «Trả lời» câu 2 và bảng «Thử độc lập» |
| S3 | Không áp dụng | Không có biến cấu hình mới |
| W1 | Không áp dụng | Không đụng `seo_app/wordpress/` |
| W2 | Không áp dụng | Như W1 |
| W3 | Không áp dụng | Như W1 |
| W4 | Không áp dụng | Không có lời gọi mạng mới |
| A1 | Không áp dụng | Không đụng prompt |
| A2 | Không áp dụng | Như A1 |
| A3 | Không áp dụng | Như A1 |
| U1 | Không áp dụng | Không đụng HTML; trang Cài đặt hiện câu qua đường có sẵn |
| U2 | Không áp dụng | Không đụng đăng nhập trang, `.streamlit/config.toml` |
| U3 | Đạt | Mục «U3 · Mật khẩu» |
| F1 | Đạt | Chỉ ghi `.env` của dự án (hay file test chỉ định); vẫn từ chối liên kết tắt |
| F2 | Không áp dụng | Không đụng ảnh |
| F3 | Đạt | Mục «F3» |
| D1 | Đạt | Không thư viện mới; `uv.lock`, `pyproject.toml` không đổi |
| D2 | Không áp dụng | `.gitignore` không đổi |
| D3 | Đạt | Mục «D3» |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | Không chạy | `uv.lock` không đổi (đã quét sạch ở T-114, 31/10) |
| bandit | Không chạy | Kiểm rút gọn U3, F3; thay đổi là câu báo và nhánh xử lý lỗi, đã đọc tay và thử độc lập |
| detect-secrets (`PYTHONUTF8=1`) | 1 báo nhầm có từ trước | Có (mồi) |
| Soát lịch sử git | Sạch | Có |
| pytest | Cây gộp 297 qua, 0 hỏng; 2 ca khóa file thật chạy được; `.env` canh không đổi. Máy đang chạy toàn bộ test trên `main` nên chỉ chạy chọn lọc; không có lần «timed out» | Có |
| ruff 0.16.10 | `All checks passed!` trên nhánh và trên cây gộp | Có |

## Báo nhầm đã loại

- `detect-secrets` «Secret Keyword» ở `seo_app/env_file.py:58`: dòng khai hằng `PASSWORD_HASH_VAR` (giá trị chỉ là tên biến môi trường), không có giá trị bí mật. Có từ trước (`main` dòng 54), chỉ dời dòng do docstring dài thêm.
- Audit hook ghi `socket.bind` / `socket.connect` tới `127.0.0.1`: cặp socket nội bộ của asyncio (Streamlit AppTest); bộ chặn chung chỉ cho qua đúng cặp này.

## Ghi nhận (không thành lỗi)

1. **Câu thành công in đường dẫn `.env`** («Đã lưu mật khẩu mới vào …»): có từ trước, là file của chính người dùng trên máy của họ, không phải câu lỗi. Đồng ý với Soi Lỗi GN-2: không phải lỗi.
2. **Cửa sổ lệnh đang mở giữ biến cũ** (Soi Lỗi GN-4): gỡ biến rồi chạy lại từ cửa sổ cũ vẫn bị báo. Không phải lỗi bảo mật (công cụ dừng, không ghi sai). Có thể thêm «mở cửa sổ mới» vào bước 3 của câu dặn, cùng phiếu sửa SL-T105-1.
3. **Đề xuất của Thợ Máy cho bộ ghi thử đọc lại vài lần** trước khi bỏ bản vừa ghi: không có vấn đề bảo mật, miễn câu báo vẫn đúng sự thật như bảng trên.
4. **Đề xuất của Thợ Máy về `app/views/settings.py:609`** (cảnh báo mã Google Sheet theo `.strip()`, lệch `load_settings` khi biến rỗng): đồng ý là lệch nhỏ của lời cảnh báo trên giao diện, không lộ gì. Gom vào phiếu dọn giao diện sau nếu Chỉ Huy muốn.

## Điều kiện

| # | Việc | Ai | Hạn |
|---|---|---|---|
| 1 | SL-T105-1: câu báo đúng nguyên nhân khi chương trình khác sửa `.env` đúng lúc lưu. Nên không trả bản cũ khi chữ đọc lại khác chữ vừa ghi (mục «Đánh giá SL-T105-1»); gỡ 2 `xfail` khi XPASS | Chỉ Huy lập phiếu nhỏ (Thợ Máy) | Phiếu dọn lỗi Thấp kế tiếp; không chặn gộp |

## Đề xuất

- Gộp T-105 được ngay; sau khi gộp không có việc gì riêng cho máy (không đổi thư viện, không đổi mật khẩu).

Script thử độc lập (`p1_tinh_huong.py`) và plugin audit hook để ngoài repo, không commit; bản sao ở thư mục ghi chú chung `T-105-la-chan-scripts/`.

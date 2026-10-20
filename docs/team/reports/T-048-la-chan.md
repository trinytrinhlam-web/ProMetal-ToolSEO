# Biên bản bảo mật T-048 · Đọc thư mục ảnh an toàn

> **Model:** chạy tạm Claude Opus 5.5 vì tài khoản không dùng được Fable (chủ dự án đã duyệt). **Sau 01/11 phải kiểm lại bằng Fable.**

> **BẢN DỞ** (đang kiểm định, chưa có kết luận). Đã có: phạm vi, công cụ quét, 19 dòng kiểm tra, ghi chú gộp. Còn: pytest, thử thật, lỗi, kết luận. Lá Chắn phiên trước (dưới Chỉ Huy A) chỉ kịp tạo khung lúc 08:02; phiên này kiểm định lại từ đầu.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm thay Fable) |
| Phiếu được kiểm | [T-048](../tickets/T-048-doc-thu-muc-anh-an-toan.md) |
| Phạm vi | diff `origin/main...team/T-048` (gốc chung `5e38bb8`, code tới `882dc18`, test Soi Lỗi tới `e366dc5`, HEAD lúc kiểm `5993812`) và code xung quanh (`seo_app/config.py`, `app/views/settings.py`, `.gitignore`, `.streamlit/config.toml`, `tests/conftest.py`) |
| Ngày | 2026-10-20 |
| Máy kiểm | Windows 11 Pro 10.0.26300, Python 3.12.15 (junction, tên 8.3, `\\localhost\C$` chạy thật). Không có WSL, Docker, máy Mac: nhánh Mac/Linux **chưa chạy** |
| **Kết luận** | _đang kiểm_ |

## Phạm vi diff

`git diff --stat origin/main...team/T-048`: 7 file, 3.423 dòng thêm, 0 dòng xóa.

| File | Dòng | Ghi chú |
|---|---|---|
| `seo_app/images/__init__.py` | 6 | Mới, chỉ docstring |
| `seo_app/images/folders.py` | 847 | Mới: `ImageRef`, `ImageLibrary`, `_Scan`, gọi Windows API qua `ctypes` |
| `tests/test_images_folders.py` | 962 | Mới (Thợ Máy) |
| `tests/test_images_folders_soi_loi.py` | 1.193 | Mới (Soi Lỗi) |
| `docs/team/reports/T-048-*.md` | 415 | Báo cáo |

Không đổi: `pyproject.toml`, `uv.lock`, `.gitignore`, `.env.example`, `.streamlit/`, `config/`, `app/` (`git diff origin/main...team/T-048 -- uv.lock pyproject.toml .gitignore .env.example .streamlit config app` rỗng). Chưa trang nào gọi `ImageLibrary` (grep `seo_app.images` trong `app/`: không có).

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uv export --format requirements-txt --no-hashes --frozen` (68 gói ghim, đúng `uv.lock` của nhánh, `pillow==12.3.0`) → `uvx pip-audit --no-deps --disable-pip -r …`: **No known vulnerabilities found**. Gói `-e .` (`seo-app`) bị bỏ qua vì không có trên PyPI, bình thường. Nhánh không đổi `uv.lock`; `main` đã đổi `uv.lock` (T-058, Pillow 13.0.0) sau gốc chung, kết quả quét bản gộp ở mục "Ghi chú cho Chỉ Huy khi gộp" | Có |
| bandit | `uvx bandit -r seo_app app scripts`: 1 Low (B101 `assert` ở `seo_app/storage/drafts.py:203`, có từ T-016, không thuộc phiếu). Riêng `seo_app/images/folders.py` + `__init__.py` (702 dòng): **No issues identified** | Có |
| detect-secrets | `uvx detect-secrets scan` trên 7 file của diff: `"results": {}`. Toàn bộ patch `git log -p origin/main..team/T-048` (4.120 dòng) quét riêng: `"results": {}` | Có |
| Soát lịch sử git | Patch của nhánh lọc `api[_-]?key\|password\|secret\|token`: 18 dòng, đều là dữ liệu test (`b"SECRET"`, `SECRET~1`, `.secret`, `os.link(secret, …)`) và chữ trong báo cáo. Toàn lịch sử (`git log -p --all`) lọc dạng khóa thật (`sk-ant-…`, `sk-proj-…`, `AIza…`, `BEGIN PRIVATE KEY`): chỉ có khóa giả có từ trước (`…KhoaGia…`, `ThuNghiemKhongPhaiKhoaThat`, `BIMAT_KHONG_DUOC_IN`, `AAAA…`), không dòng nào thuộc T-048 | Có |
| ruff | `uv run ruff check .`: **All checks passed!** `ruff format --check` 4 file Python của diff: đã đúng định dạng | Có |
| pytest | _đang chạy (toàn bộ, nền)_ | |

## Danh sách kiểm tra

Số dòng theo `seo_app/images/folders.py` tại `882dc18` (giống HEAD). `test:` = `tests/test_images_folders.py`, `sl:` = `tests/test_images_folders_soi_loi.py`.

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | **Đạt** | detect-secrets trên 7 file và toàn patch của nhánh: `"results": {}`. Lọc lịch sử: 18 dòng khớp đều là dữ liệu test (`b"SECRET"`, `SECRET~1`). Không có `.env`, khóa, mật khẩu, đường dẫn máy thật trong file mới (test chỉ dùng `tmp_path`) |
| S2 | **Đạt** | Module không ghi log, không `print`. Mọi câu lỗi là chữ cố định, không ghép đường dẫn (`folders.py:67-75`, `:90`, `:332`, `:335`, `:460`, `:466-477`, `:539-548`, `:605-616`, `:638-645`, `:780-782`); lỗi hệ điều hành bị cắt xích bằng `from None` (`:475`, `:489-491`, `:505-507`, `:640`, `:650`, `:743-747`, `:782`). `repr(ImageLibrary)` chỉ in số thư mục (`:436-438`). Có test: `raises_safely` (`test:84`) kiểm mọi câu lỗi không chứa `tmp_path` và không xích lỗi OS; `sl:636` (`repr`/`str` mọi đối tượng trả về), `sl:670` (mọi loại hỏng, cả gốc UNC). Một chỗ có thể ném `OSError` thô: `os.fstat(fd)` ở `:268` (chỉ khi `GetFileInformationByHandleEx` lỗi); lỗi này không có tên file nên không lộ đường dẫn (ghi nhận, không phải lỗi) |
| S3 | **Không áp dụng** | Không có biến cấu hình mới. `IMAGE_FOLDERS` có từ trước: `.env.example:47-51` (có chú thích, ví dụ Windows/Mac, không giá trị thật), đọc ở `seo_app/config.py:142`, tách bằng `;` ở `:146-148` |
| W1 | **Không áp dụng** | Module không import `seo_app.wordpress`, không gọi HTTP (`folders.py:25-38` chỉ thư viện chuẩn) |
| W2 | **Không áp dụng** | Như W1. Riêng thư mục ảnh: module **chỉ đọc** (xem F1) |
| W3 | **Không áp dụng** | Không tạo HTML |
| W4 | **Không áp dụng** | Không gọi mạng |
| A1 | **Không áp dụng** | Không có prompt. Tên file/thư mục trả về là dữ liệu chưa tin cậy (docstring `folders.py:21-22`); việc bọc khung dữ liệu và đối chiếu danh sách cố định thuộc T-052 (góp ý Lá Chắn T-046 số 3). Xem LC-T048-4 |
| A2 | **Không áp dụng** | AI không gọi được module này; module không nhận lệnh từ AI |
| A3 | **Không áp dụng** | Module không gửi gì cho AI. Kết quả chỉ có tên và đường dẫn tương đối, không có đường dẫn tuyệt đối (`ImageRef` `:318-343`, `RootInfo.label` chỉ là tên thư mục cuối `:449`) |
| U1 | **Không áp dụng** | Phiếu không có giao diện. Điều kiện cho T-056/G3-10: hiện tên bằng chữ thường (escape), cô lập hướng chữ (xem LC-T048-4) |
| U2 | **Đạt** | Không thêm trang (`git diff origin/main...team/T-048 -- app` rỗng); `.streamlit/config.toml:5` `address = "localhost"` không đổi; module không mở cổng mạng. Ghi nhận ngoài phạm vi: trang Cài đặt hiện có in đường dẫn tuyệt đối của `IMAGE_FOLDERS` (`app/views/settings.py:474-477`, có từ trước); khi làm G3-10 nên đổi sang `ImageLibrary.roots()` (góp ý T-046 số 9) |
| U3 | **Không áp dụng** | Không đụng đăng nhập |
| F1 | **Đạt** (còn lỗi Thấp LC-T048-2, -3, -6; nhánh Mac chưa chạy: LC-T048-1) | Ba lớp chặn, tôi đọc từng dòng: (1) dạng chữ `_parse_rel` `:111-132` + `_is_safe_name` `:93-108` (từ chối `..`, `.`, rỗng, `/…`, ổ đĩa, UNC, `\`, `:`, `<>"\|?*`, Cc, Cs, 9 ký tự hướng chữ, tên thiết bị, tên kết thúc bằng dấu chấm/khoảng trắng); (2) `lstat` từng phần, từ chối liên kết và mục ẩn/hệ thống `:484-499`, `_is_link_stat` `:144-151` dùng bit name surrogate (bắt junction `0xA0000003`, symlink `0xA000000C`, symlink WSL `0xA000001D`); (3) `resolve(strict=True)` + `is_relative_to(gốc)` `:500-509`, tên thật phải trùng tên gõ (chặn 8.3) `:513-517`. Khi quét: `_visit` bỏ symlink/junction `:809`, `:816`; giữ handle thư mục không cho chia sẻ quyền xóa `:231-256`, hỏi đường dẫn thật từ handle `:757-760`, kiểm lại reparse tag sau khi quét `:762`; Mac/Linux mở từng tầng bằng `openat(…, O_NOFOLLOW)` `:297-311`. Khi đọc: `O_NOFOLLOW` (Mac/Linux) `:630-634`, so `(st_dev, st_ino)` file đã mở với file đã kiểm `:642-645`. **Chỉ đọc:** handle chỉ xin `FILE_LIST_DIRECTORY \| FILE_READ_ATTRIBUTES` `:239`, `os.open` chỉ `O_RDONLY` `:630`; `test:662` dò mã nguồn không có lệnh ghi/xóa; `test:649` so cây thư mục trước/sau. Test junction **chạy thật** trên máy này (xem pytest). Thử tấn công thật của tôi: mục "Thử thật" |
| F2 | **Đạt** (phần thuộc phiếu) | Giới hạn 40 MB (`:42`) kiểm khi quét `:842`, trước khi mở `:608` → `:614`, sau khi mở `:646`, và chỉ đọc tối đa giới hạn + 1 byte `:648` (`test:587` file to ra giữa chừng). File 0 byte bị loại `:839`, `:613`. Module trả nguyên bytes, không đụng EXIF/GPS. Giới hạn số điểm ảnh và kiểm nội dung đúng là ảnh (`Image.open(formats=…)`) thuộc G3-3/T-049 (docstring `:627`) |
| F3 | **Đạt** | Không đọc file văn bản; ảnh đọc nhị phân `"rb"` `:641`. Không `eval`, `exec`, `pickle`, `yaml`, `subprocess` trong module (`test:662` dò cả `pickle`, `eval(`). `ctypes` chỉ gọi 4 hàm đọc của `kernel32` với kiểu tham số khai báo đủ `:197-228` |
| D1 | **Đạt** | Không thêm thư viện (`pyproject.toml`, `uv.lock` không đổi); chỉ dùng thư viện chuẩn. pip-audit: 0 lỗ hổng |
| D2 | **Đạt** | `.gitignore` không đổi: `.env` `:2-4`, `*service-account*.json` `:5`, `secrets/` `:6`, cache `data/`, `*.sqlite` `:22-24`. Không commit ảnh: diff không có file nhị phân, test tạo ảnh giả trong `tmp_path` (`test:36-39`). Thư mục cache ảnh xem trước (góp ý T-046 số 9) chưa có ở phiếu này, kiểm ở G3-3 |
| D3 | **Đạt** | Hai file test không import `requests`, `socket`, thư viện AI (`test:7-17`, `sl:8-18`); bộ chặn mạng `tests/conftest.py:18-19` (autouse) không đổi. Một test đọc ổ chia sẻ `\\localhost\C$` (`sl:185-216`): đi qua bộ chuyển hướng SMB của Windows tới **chính máy này**, không phải WordPress/AI/Google, tự bỏ qua nếu không mở được; tôi chấp nhận. Test junction tới cả ổ đĩa (`sl:124-142`) gỡ junction bằng `os.rmdir` trong `finally`; nếu test bị ngắt giữa chừng thì pytest dọn bằng `shutil.rmtree`, mà Python 3.12.15 coi junction là file (`os.walk(..., followlinks=_walk_symlinks_as_files)`, `os.py:387-388`) nên không xóa xuyên vào ổ đĩa (tôi đã đọc mã nguồn bản Python đang dùng) |

## Ghi chú cho Chỉ Huy khi gộp

- **`seo_app/images/__init__.py` cũng được T-050 tạo** (file rỗng, blob `e69de29`). T-048 tạo cùng file, có docstring. Tôi thử gộp không đụng thư mục làm việc (`git merge-tree --write-tree`):
  - `origin/main` + `team/T-048`: **sạch**, không xung đột (cây `ff133e4`).
  - `team/T-048` + `team/T-050`: **sạch**; bản gộp lấy đúng docstring của T-048 (blob `04c33dd`), đúng như bảng việc đã chốt. Lý do: git gộp "cùng thêm một file" mà một bên rỗng thì lấy bên có nội dung. Thứ tự gộp nào cũng ra cùng kết quả.
  - Docstring T-048 ghi "chỉ phiếu T-048 tạo nó" là chưa đúng hẳn (T-050 cũng tạo), không ảnh hưởng bảo mật.
- `main` đã đi xa gốc chung `5e38bb8` (49 file, có `uv.lock` của T-058). Code T-048 chỉ dùng thư viện chuẩn (`ctypes`, `msvcrt`, `os`, `stat`, `unicodedata`), không phụ thuộc phần `main` mới đổi.

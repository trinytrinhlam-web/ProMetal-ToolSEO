# Biên bản bảo mật T-048 · Đọc thư mục ảnh an toàn

> **Model:** chạy tạm Claude Opus 5.5 vì tài khoản không dùng được Fable (chủ dự án đã duyệt). **Sau 01/11 phải kiểm lại bằng Fable.**

> Lá Chắn phiên trước (dưới Chỉ Huy A) chỉ kịp tạo khung lúc 08:02 rồi dừng; phiên này (dưới Chỉ Huy B) kiểm định lại từ đầu.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm thay Fable) |
| Phiếu được kiểm | [T-048](../tickets/T-048-doc-thu-muc-anh-an-toan.md) |
| Phạm vi | diff `origin/main...team/T-048` (gốc chung `5e38bb8`, code tới `882dc18`, test Soi Lỗi tới `e366dc5`, HEAD lúc kiểm `5993812`) và code xung quanh (`seo_app/config.py`, `app/views/settings.py`, `.gitignore`, `.streamlit/config.toml`, `tests/conftest.py`) |
| Ngày | 2026-10-20 |
| Máy kiểm | Windows 11 Pro 10.0.26300, Python 3.12.15 (junction, tên 8.3, `\\localhost\C$` chạy thật). Không có WSL, Docker, máy Mac: nhánh Mac/Linux **chưa chạy** |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** (0 Nghiêm trọng, 0 Cao, 1 Trung bình, 5 Thấp) |

## Tóm tắt (cho chủ dự án)

Phần đọc thư mục ảnh **an toàn để gộp**. Tôi đã cho một chương trình khác liên tục biến thư mục ảnh thành "lối tắt" trỏ ra chỗ khác trên máy, trong lúc app đọc ảnh hơn 11.000 lần: **không lần nào app đọc được nội dung file nằm ngoài thư mục ảnh**. App không ghi, không xóa gì trong thư mục ảnh; câu báo lỗi không lộ đường dẫn trên máy; không có khóa hay mật khẩu trong code.

Còn một khe nhỏ: nếu máy **đã bị cài sẵn chương trình độc** đang chạy, app có thể hiện **tên** (không phải nội dung) của vài file ở chỗ khác trên chính máy đó. Kẻ đã chạy được chương trình trên máy thì vốn tự xem được các file đó, nên không mất thêm gì; tôi xếp mức Thấp và đề nghị anh/chị quyết định ghi vào sổ rủi ro hoặc cho sửa sau.

Điều kiện chính: phần code chạy trên **máy Mac chưa được chạy thử lần nào** (cả đội chỉ có máy Windows). Cần chạy bộ test trên Mac (hoặc Linux) trước khi trang chọn ảnh được gộp và trước khi xong Giai đoạn 3.

## Lỗi phát hiện

Số dòng theo `seo_app/images/folders.py` tại `882dc18`. `test:` = `tests/test_images_folders.py`, `sl:` = `tests/test_images_folders_soi_loi.py`.

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T048-1 | **Trung bình** | Đường chặn liên kết trên **Mac/Linux chưa chạy lần nào** trên bất kỳ máy nào: quét bằng `openat(…, O_NOFOLLOW)` + `os.scandir(fd)`, `O_NOFOLLOW` khi đọc, cờ ẩn `UF_HIDDEN`, tên sai UTF-8. Thợ Máy, Soi Lỗi và tôi đều chỉ có Windows (máy này không có WSL, Docker) | `folders.py:182`, `:297-311`, `:739-751`, `:630-634`, `:158`; 6 test chỉ chạy trên Mac/Linux bị bỏ qua: `test:62` (4 symlink), `test:368`, `test:381` | App chạy cả trên Mac (`run.command`, `CLAUDE.md`). Trên Mac mọi lần xem thư mục đi nhánh `_scan_by_fd`, không đi nhánh Windows đã thử. Tôi đọc từng dòng và **không thấy lỗi** (mở từng tầng từ gốc đã `resolve` với `O_DIRECTORY \| O_NOFOLLOW`, ELOOP thành `_ChangedError`), nhưng chưa có bằng chứng chạy. Lỗi ẩn có thể làm Mac không xem được thư mục, xấu nhất là lọt symlink (F1). Bảng mức ở `security.md` mục 3: thiếu test cho đường an toàn là Trung bình | Chạy `uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py -rs` trên Mac (hoặc phiên cloud Ubuntu, nhánh `team/T-048` đã có trên GitHub). Kết quả phải cho thấy 6 test Mac/Linux **chạy**, không bỏ qua; dán vào báo cáo. Hạn: trước khi gộp phiếu giao diện đầu tiên gọi `ImageLibrary` (G3-10/T-056) và trước khi hết GĐ3 |
| LC-T048-2 | Thấp | (= R2-1 của Soi Lỗi) Đặt rồi gỡ junction **tại chỗ** quanh `os.scandir`: app kiểm thư mục qua handle đang giữ nhưng liệt kê theo **tên**, nên junction đặt vào đúng lúc đó bị đi xuyên | Kiểm qua handle `:757-760`, liệt kê theo tên `:761` → `:778`, kiểm lại `:762` | Chương trình chạy trên máy, có quyền ghi vào thư mục ảnh, tạo thư mục rỗng `x` rồi bật/tắt junction tại chỗ liên tục → người dùng mở thư mục ảnh → kết quả có **tên, cỡ, ngày sửa** file của thư mục đích ngoài gốc. **Thử thật** (mục bên dưới): lọt 74/6.715 lần xem `x` (1,1%) và 367/6.715 lần quét cả cây (5,5%), tức là lọt trong chưa tới 1 giây; **đọc nội dung lọt 0/6.715**. Khe này không hẹp như báo cáo Thợ Máy/Soi Lỗi ước lượng, nhưng vẫn Thấp vì: (a) phải có chương trình đang chạy trên máy (Drive không đồng bộ junction, USB FAT/exFAT không có junction, junction đặt sẵn thì bị chặn); (b) chương trình chạy với quyền của chủ máy thì tự đọc thẳng được thư mục đích, còn tài khoản khác trên máy dùng chung thì không thấy màn hình app; (c) tên lọt không đi tiếp ra ngoài: không đọc được nội dung nên không chọn được ảnh đó, tên file gốc không gửi AI (thiết kế T-046), thẻ phải khớp danh sách cố định (T-052) | Khuyên sửa ở phiếu dọn (không bắt buộc ở phiếu này): liệt kê qua **chính handle đang giữ** (`GetFileInformationByHandleEx`, lớp `FileIdBothDirectoryInfo` hoặc `FileFullDirectoryInfo`) thay cho `os.scandir(tên)`; khi đó cả việc chặn đổi tên cũng không còn cần. Sửa xong thì bỏ `xfail` R2-1 (`sl:903`). Không sửa thì chủ dự án quyết ghi sổ rủi ro |
| LC-T048-3 | Thấp | Nhánh dự phòng **ép được** từ bên ngoài, và nhánh này còn khe "tráo rồi tráo lại" (Soi Lỗi đã ghi) | `:185` (không chia sẻ quyền xóa), `:765-772`; `sl:1004` | Bất kỳ chương trình nào giữ một handle thư mục có quyền DELETE (chia sẻ đủ) làm `CreateFileW` của app lỗi 32, app tự sang nhánh dự phòng, trong khi `os.scandir` vẫn chạy bình thường (tôi đã thử thật). Ở nhánh dự phòng, bật/tắt junction tại chỗ 20 giây: lọt 5/3.312 lần xem, 17/3.312 lần quét cả cây; đọc nội dung lọt 0/3.312. Hậu quả và lý do Thấp như LC-T048-2 | Cùng cách sửa LC-T048-2. Ở nhánh dự phòng có thể mở lại handle **có** chia sẻ quyền xóa: không khóa được đường đi nhưng vẫn liệt kê qua handle và hỏi đường dẫn thật được. Hoặc ghi sổ rủi ro chung với LC-T048-2 |
| LC-T048-4 | Thấp | Tên có ký tự **vô hình hoặc ngắt dòng** vẫn được trả về: `_is_safe_name` chỉ chặn Cc, Cs và 9 ký tự hướng chữ. Tôi gọi thử: nhận U+2028, U+2029 (Zl, Zp: ngắt dòng), U+200B, U+200F (RLM), U+061C, U+FEFF, U+FFF9 và **ký tự thẻ U+E0000–E007F** (Cf, vô hình), Co, Cn | `:51-57`, `:101-107` | Người có quyền sửa thư mục Drive dùng chung đặt tên thư mục hay file chứa các ký tự này (Drive cho phép, đồng bộ về máy) → `list_folder` trả nguyên tên → nếu phiếu sau dùng thẳng: chữ ẩn đi vào prompt AI (ký tự thẻ là kiểu "giấu chữ" mà nhiều mô hình vẫn đọc được), hoặc giao diện hiện tên đánh lừa. Phiếu này làm đúng phạm vi (chỉ trả tên, `:21-22`) nên Thấp | (a) T-052: thẻ chỉ nhận khi khớp danh sách cố định (góp ý T-046 số 3), bỏ ký tự Cf/Zl/Zp trước khi so. (b) T-056/G3-10: hiện tên bằng chữ thường đã escape, cô lập hướng chữ. (c) Phiếu dọn (khuyên): `_is_safe_name` từ chối thêm Zl, Zp, khối U+E0000–E007F, U+FFF9–FFFB; giữ ZWJ/ZWNJ cho emoji và chữ ghép (test `sl:1093-1110` đang cho qua U+200B, sửa thì cập nhật test) |
| LC-T048-5 | Thấp | (= R2-2 của Soi Lỗi) Quét cả cây: vừa đủ `max_entries` mục mà còn thư mục con rỗng chờ quét thì vẫn báo "còn nữa" | `:703` | Thư mục có đúng 5.000 mục kèm thư mục con rỗng → câu "còn nữa chưa xem" thừa. **Không có hậu quả bảo mật** (không đọc thêm, không lộ gì); chỉ là câu báo sai | Như Soi Lỗi đề xuất (để `_read_entries` tự báo khi gặp mục thứ `max_entries + 1`), phiếu dọn lỗi Thấp, bỏ `xfail` (`sl:1041`) |
| LC-T048-6 | Thấp | Hard link và ổ không có số inode (Thợ Máy, Soi Lỗi đã ghi) | `:161-165`, `:644`; `sl:420` | Hard link: chương trình chạy trên máy tạo trong thư mục ảnh một hard link tới file cùng ổ → app đọc được nội dung file đó (bản chất của hard link, `sl:420` ghi hành vi). Cần chạy được chương trình trên máy (Drive không đồng bộ hard link). `st_ino = 0` (ổ ảo, một số ổ FAT): tắt phép so "cùng file" ở `:163` và `:644`; FAT không có junction, symlink nên không tráo được | Ghi sổ rủi ro (chủ dự án quyết). Tùy chọn từ chối `st_nlink > 1` có thể từ chối nhầm ảnh do phần mềm sao lưu tạo, nên không khuyên |

### Đánh giá R2-1, R2-2 của Soi Lỗi

- **R2-1 (LC-T048-2): đồng ý mức Thấp, nhưng lý do khác.** Báo cáo Soi Lỗi và Thợ Máy cho rằng khe chỉ vài chục micro giây nên "chỉ là lý thuyết". Thử thật với một tiến trình riêng bật/tắt junction liên tục: lọt 1–6% số lần quét, nghĩa là lọt gần như chắc chắn trong vài giây. Mức Thấp đứng được vì kẻ tấn công không thu thêm được gì (nội dung vẫn bị chặn, tên không đi ra ngoài), **không phải** vì khe hẹp. Nếu sau này tên file được gửi ra ngoài máy (AI, log, WordPress) thì phải xét lại mức.
- **R2-2 (LC-T048-5): đồng ý Thấp.** Không phải lỗi bảo mật.

## Thử thật (Windows, máy kiểm định)

Script nằm trong thư mục tạm của phiên (không commit): một tiến trình "kẻ tấn công" riêng gọi `FSCTL_SET_REPARSE_POINT` / `FSCTL_DELETE_REPARSE_POINT` liên tục, tiến trình app gọi `list_folder(0, "x")`, `list_folder(0, recursive=True)`, `read_image_bytes(ImageRef(0, "x/bi-mat.jpg"))` liên tục trong 20 giây. Thư mục ngoài gốc chứa `bi-mat.jpg` (nội dung `SECRET`) và `chi-ngoai.jpg`. Dữ liệu tạo trong thư mục tạm và đã xóa sau khi thử.

| # | Cách tấn công | Liệt kê lọt (xem `x` / quét cả cây) | Đọc nội dung lọt | Ghi chú |
|---|---|---|---|---|
| 1 | Bật/tắt junction tại chỗ trên `x` rỗng, app giữ được handle (lần 1) | 47/2.805 · 176/2.805 | **0**/2.805 | Còn lại: lỗi gọn "liên kết tắt", "ngoài thư mục", "vừa bị thay đổi" |
| 2 | Như 1 (lần 2) | 27/3.910 · 191/3.910 | **0**/3.910 | |
| 3 | Như 1, thêm handle có quyền DELETE để ép nhánh dự phòng | 5/3.312 · 17/3.312 | **0**/3.312 | |
| 4 | Đổi tên `x` → `x-2`, tạo junction `x` ra ngoài, gỡ, trả tên; `x` có ảnh mồi cùng tên `bi-mat.jpg` (thử đường đọc: kiểm xong rồi mới tráo) | 0/1.165 · 0/1.165 | **0**/1.165 | 995 lần đọc ra ảnh mồi, 170 lỗi gọn. Đổi tên bị Windows từ chối khi app đang giữ handle |
| 5 | Ép nhánh dự phòng: giữ handle `DELETE \| READ_ATTRIBUTES`, chia sẻ đủ | | | `_win_hold_dir` trả `None` (lỗi 32); `os.scandir` vẫn chạy |
| 6 | Gọi `_is_safe_name` với từng ký tự Unicode lạ | | | Xem LC-T048-4 |

Tổng: **11.192 lần đọc trong lúc bị tấn công, 0 lần đọc được nội dung file ngoài gốc.** Lớp chặn nội dung (`lstat` từng phần, `resolve` + `is_relative_to`, so `(st_dev, st_ino)` sau khi mở) chịu được; riêng tấn công kiểu 1–3 thì thư mục phải rỗng mới đặt được junction, nên đường đọc luôn gặp "không thấy" hoặc "ngoài thư mục".

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
| pip-audit | `uv export --format requirements-txt --no-hashes --frozen` (68 gói ghim, đúng `uv.lock` của nhánh, `pillow==12.3.0`) → `uvx pip-audit --no-deps --disable-pip -r …`: **No known vulnerabilities found**. Gói `-e .` (`seo-app`) bị bỏ qua vì không có trên PyPI, bình thường. Nhánh không đổi `uv.lock`. `main` đã đổi `uv.lock` sau gốc chung (T-047 `b9e4b64`: `pillow>=12.3`, `pillow-heif>=1.8.1`); quét bản gộp `main` + T-048 (`pillow==12.3.0`, `pillow-heif==1.8.1`): **No known vulnerabilities found** | Có |
| bandit | `uvx bandit -r seo_app app scripts`: 1 Low (B101 `assert` ở `seo_app/storage/drafts.py:203`, có từ T-016, không thuộc phiếu). Riêng `seo_app/images/folders.py` + `__init__.py` (702 dòng): **No issues identified** | Có |
| detect-secrets | `uvx detect-secrets scan` trên 7 file của diff: `"results": {}`. Toàn bộ patch `git log -p origin/main..team/T-048` (4.120 dòng) quét riêng: `"results": {}` | Có |
| Soát lịch sử git | Patch của nhánh lọc `api[_-]?key\|password\|secret\|token`: 18 dòng, đều là dữ liệu test (`b"SECRET"`, `SECRET~1`, `.secret`, `os.link(secret, …)`) và chữ trong báo cáo. Toàn lịch sử (`git log -p --all`) lọc dạng khóa thật (`sk-ant-…`, `sk-proj-…`, `AIza…`, `BEGIN PRIVATE KEY`): chỉ có khóa giả có từ trước (`…KhoaGia…`, `ThuNghiemKhongPhaiKhoaThat`, `BIMAT_KHONG_DUOC_IN`, `AAAA…`), không dòng nào thuộc T-048 | Có |
| ruff | `uv run ruff check .`: **All checks passed!** `ruff format --check` 4 file Python của diff: đã đúng định dạng | Có |
| pytest (toàn bộ) | Nhánh tại `5993812` (code giống `882dc18`): `uv run pytest -q -p no:cacheprovider` → **5875 passed, 17 skipped, 38 xfailed, 1 warning in 717.47s**, 0 hỏng, 0 lỗi. 17 bỏ qua = 6 của T-048 (bên dưới) + 11 có từ trước; 38 xfail = 35 có từ trước + 3 của Soi Lỗi (R2-1 ×2, R2-2). Cảnh báo duy nhất là Pydantic trong `test_soi_loi_t028.py`, có từ trước | Có |
| pytest (T-048) | `uv run pytest tests/test_images_folders.py tests/test_images_folders_soi_loi.py -rsx` → **251 passed, 6 skipped, 3 xfailed in 16.98s**. 6 bỏ qua đúng lý do: 4 symlink (Windows này không cho tạo, lỗi 1314), tên lạ và FIFO (chỉ tạo được trên Mac/Linux). **Mọi test Windows đều chạy thật**: junction, junction tới cả ổ đĩa, `\\localhost\C$`, tên 8.3, đặt junction tại chỗ bằng `FSCTL_SET_REPARSE_POINT`, giữ handle. 3 xfail hỏng đúng lý do R2-1, R2-2 | Có |
| pytest (bản gộp) | Cây gộp thử `origin/main` + `team/T-048` (`ff133e4`, giải nén ra thư mục tạm bằng `git archive`, không đụng repo): test T-048 **251 passed, 6 skipped, 3 xfailed**; `ruff check .` sạch. Toàn bộ test trên bản gộp: xem mục "Ghi chú cho Chỉ Huy khi gộp" | Có |

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

## Báo nhầm đã loại

- bandit B101 (`assert`) ở `seo_app/storage/drafts.py:203`: có từ T-016, không thuộc phiếu này.
- Soát lịch sử khớp chữ `secret`/`SECRET` trong test T-048: là nội dung giả của file ngoài gốc dùng để thử (`b"SECRET"`), không phải bí mật.
- Khóa dạng `sk-ant-…`, `AIza…` trong lịch sử: khóa giả có chữ `KhoaGia`, `ThuNghiemKhongPhaiKhoaThat` từ các phiếu trước, đã được các biên bản trước xác minh.

## Ghi nhận (không phải lỗi, chuyển cho phiếu sau)

- **Gốc khai báo là junction được phép** (thiết kế, `test:776`). Nếu `IMAGE_FOLDERS` trỏ vào một thư mục con trên USB định dạng NTFS do người khác chuẩn bị, thư mục đó có thể là junction trỏ vào máy (ví dụ thư mục Ảnh của người dùng) và app coi đó là gốc. Hậu quả: thấy ảnh lạ trong danh sách; chỉ tải lên khi người dùng tự chọn. Khai báo gốc là ký tự ổ (`E:/`) thì không bị. Đề xuất cho G3-10: trang Cài đặt báo "thư mục gốc đi qua lối tắt" (không hiện đường dẫn).
- **Một file có thể có nhiều `ImageRef`** (khác hoa thường, NFC/NFD), vì `_resolve_inside` so tên không phân biệt hoa thường (`:513-517`). Không phải lỗi bảo mật; G3-9 (nháp) và G3-3 (cache ảnh xem trước) nên lấy `ImageRef` từ kết quả quét làm khóa, không lấy chuỗi người dùng gõ.
- `_path_key` (`:288-294`) so đường dẫn bằng NFC + `casefold`, lỏng hơn cách Windows so tên. Muốn lợi dụng phải tạo thư mục "anh em" ngoài gốc có tên gần giống và chạy chương trình trên máy; không thu thêm gì. Tùy chọn: trên Windows chỉ so không phân biệt hoa thường, bỏ NFC.
- `os.fstat(fd)` ở `:268` có thể ném `OSError` thô (không có đường dẫn) khi `GetFileInformationByHandleEx` lỗi; nên bọc vào `ImageFolderError` ở phiếu dọn.
- App giữ handle thư mục không chia sẻ quyền xóa trong lúc quét (tối đa 10 giây): Google Drive hay Explorer có thể báo "đang dùng" trong chốc lát. Soi Lỗi đã phân tích, tôi đồng ý ảnh hưởng thấp.
- Trang Cài đặt đang in đường dẫn tuyệt đối của `IMAGE_FOLDERS` (`app/views/settings.py:474-477`, có từ trước, ngoài phạm vi).

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

Gộp được ngay. Các việc sau phải có phiếu (Chỉ Huy lập):

1. **LC-T048-1 (Trung bình):** Soi Lỗi chạy test T-048 trên Mac hoặc Linux, dán kết quả có 6 test Mac/Linux chạy thật. Hạn: trước khi gộp phiếu giao diện đầu tiên gọi `ImageLibrary` (G3-10/T-056) và trước khi hết GĐ3. Có lỗi thì Thợ Máy sửa và Lá Chắn kiểm lại phần đó.
2. **Sổ rủi ro hoặc sửa (chủ dự án quyết, Chỉ Huy hỏi):** LC-T048-2 và LC-T048-3 (liệt kê được tên file ngoài gốc khi có chương trình độc đang chạy trên máy), LC-T048-6 (hard link, ổ không có số inode). Lá Chắn khuyên **sửa** LC-T048-2/-3 theo cách liệt kê qua handle ở phiếu dọn GĐ3; nếu chủ dự án chọn chấp nhận thì ghi vào `security.md` mục 6.
3. **Phiếu dọn lỗi Thấp GĐ3:** LC-T048-5 (R2-2), LC-T048-4 mục (c), bọc `os.fstat` ở `:268`; sửa xong thì bỏ `xfail` tương ứng.
4. **Chép vào phiếu sau:**
   - T-052 (thẻ ảnh): LC-T048-4 mục (a); tên thư mục là dữ liệu chưa tin cậy.
   - T-056/G3-10 (giao diện chọn ảnh): escape tên, cô lập hướng chữ (LC-T048-4 mục (b)); không dùng `ImageLibrary._folders`; không hiện đường dẫn tuyệt đối (dùng `roots()`); chỉ quét khi người dùng mở thư mục hoặc bấm quét lại; báo "gốc đi qua lối tắt" (mục Ghi nhận).
   - G3-9 (nháp): `ImageRef` đọc từ nháp phải tạo lại bằng `ImageRef(...)` rồi đi qua `stat_image`/`read_image_bytes`, không tin số thứ tự gốc (góp ý T-046 số 11); khóa theo `ImageRef` của kết quả quét.
   - G3-3/T-049 (xử lý ảnh): kiểm nội dung bằng Pillow `formats=…`, không tin đuôi file; thư mục cache ảnh xem trước nằm trong `.gitignore` (góp ý T-046 số 9).

## Ghi chú cho Chỉ Huy khi gộp

- **`seo_app/images/__init__.py` cũng được T-050 tạo** (file rỗng, blob `e69de29`). T-048 tạo cùng file, có docstring. Tôi thử gộp không đụng thư mục làm việc (`git merge-tree --write-tree`):
  - `origin/main` + `team/T-048`: **sạch**, không xung đột (cây `ff133e4`).
  - `team/T-048` + `team/T-050`: **sạch**; bản gộp lấy đúng docstring của T-048 (blob `04c33dd`), đúng như bảng việc đã chốt. Lý do: git gộp "cùng thêm một file" mà một bên rỗng thì lấy bên có nội dung. Thứ tự gộp nào cũng ra cùng kết quả.
  - Docstring T-048 ghi "chỉ phiếu T-048 tạo nó" là chưa đúng hẳn (T-050 cũng tạo), không ảnh hưởng bảo mật.
- `main` đã đi xa gốc chung `5e38bb8` (49 file, có `uv.lock` của T-058). Code T-048 chỉ dùng thư viện chuẩn (`ctypes`, `msvcrt`, `os`, `stat`, `unicodedata`), không phụ thuộc phần `main` mới đổi.

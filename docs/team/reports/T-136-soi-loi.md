# Báo cáo T-136 · Gom kiểm file 5 kho SQLite, LC-T131-1, câu báo kho nháp · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-136](../tickets/T-136-gom-kiem-file-5-kho.md) · Lá Chắn T-131 B.1, B.2, B.4, LC-T131-1 · Soi Lỗi T-131 GN-1 → GN-3 |
| Nhánh | `team/T-136` tại `81a3016` (mã và test `c48aedd`, báo cáo `81a3016`; gốc `main` `71322c4`). Gộp thử `main` cục bộ `01fc45c`: **không xung đột**, cây `481f3ed`; từ gốc nhánh, `main` chỉ đổi tài liệu, nên cây gộp cùng mã với nhánh |
| Ngày nộp | 2026-11-12 (soi từ 2026-11-10; hai lần ngắt do phiên dừng) |
| **Kết luận** | **ĐẠT**: 0 lỗi mới (0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp). Module chung `sqlite_file` giữ nguyên hành vi đã qua Lá Chắn ở 5 kho: so bản cũ và bản mới trên 15 kiểu file hỏng, lạ × 5 kho, **62/71 ca y hệt**; 6 ca khác đúng như phiếu đòi, 3 ca chỉ khác câu báo khi chỗ đặt file lưu tạm là **thư mục** (G1). LC-T131-1 (a), (b) đóng; cất file nháp mà dấu «đã gửi» còn nguyên trong file cất đi, câu báo nhắc đúng; câu báo lối tắt, chỉ đọc đúng; GN-1, GN-2, GN-3 đóng; R5 đúng. 107 file mọi nơi gọi tới 5 kho và quét cả gói: 10.137 qua, 0 hỏng. 3 ghi nhận, không chặn |

## Tóm tắt (cho chủ dự án)

- **Năm kho dữ liệu trong máy nay dùng chung một bộ kiểm file. Phần này đúng.** Tôi đem 15 kiểu file hỏng hay bị sửa tay thử trên cả 5 kho, ở bản cũ và bản mới:
  - 62/71 ca chạy y hệt bản cũ;
  - 6 ca khác đúng như phiếu muốn: file ghi «phiên bản» lạ không còn làm kẹt; ô chữ hỏng trong file nháp chỉ làm vắng đúng nháp đó; file nháp chỉ đọc nay báo «chỉ đọc»;
  - 3 ca còn lại chỉ khác **câu báo** khi chỗ đặt file lưu tạm là một thư mục (rất hiếm, ghi lại để sửa câu sau).
- **Dấu «đã gửi» chống gửi trùng:**
  - ô chữ hỏng: nháp đó vắng khỏi danh sách, nhưng khóa gửi trùng vẫn còn; lần tự lưu kế của tab đang mở bài làm nháp hiện lại;
  - file nháp ghi «phiên bản» lạ: file được cất sang một bên, dấu «đã gửi» nằm nguyên trong file cất đi; câu báo nhắc xem WordPress trước khi gửi lại.
- **Câu báo** khi chỗ đặt file nháp là lối tắt, và khi file nháp chỉ đọc: đúng.
- **Việc của bạn:** không có.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t136.py` | Mới: 2 ca, qua cả 2 (byte 18 lạ ở kho nháp: file cất đi còn dấu «đã gửi», câu báo; ô tiêu đề UTF-8 hỏng: chỉ vắng khỏi danh sách, khóa còn, lưu lại thì hiện) |
| `docs/team/reports/T-136-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của Thợ Máy, Lá Chắn, không commit file phiếu.

## Kiểm theo trọng tâm

### 1. Module chung không đổi hành vi đã qua Lá Chắn ở 5 kho

**Đọc mã từng lớp mỏng** (`git diff 71322c4..c48aedd`): mỗi kho truyền vào `sqlite_file` đúng hằng số của bản cũ:

| Kho | So cấu trúc | Bước kiểm file | Đối chiếu |
|---|---|---|---|
| `search_cache` | đủ bộ dòng (`app_rows`), file trống thì được | `_HEALTH_TIMEOUT`, `MAX_FILE_BYTES`, chữ UTF-8 chặt | Như bản cũ; thêm byte 18–19, mã 13 (GN-3) |
| `site_index`, `plan_cache` | đủ bộ dòng | `_HEALTH_TIMEOUT`, chữ chặt | Như bản cũ; thêm byte 18–19; `plan_cache` tạo bảng một giao dịch (GN-2) |
| `drafts` | từng bảng (`app_table_names`), bảng thiếu thì được | `_SQLITE_TIMEOUT`, không chặt chữ (đọc `sqlite_master` thành byte), `extra` = ô quá dài | Như bản cũ; thêm byte 18–19 |
| `image_tags` | từng bảng | giữ `_is_healthy` riêng (quy tắc lỗi riêng, bảng `info`), thêm byte 18–19 | Như bản cũ; liên kết theo định nghĩa chung (thêm reparse point trỏ đi chỗ khác) |

Câu dựng cấu trúc mẫu đọc tới 64 dòng thay cho 16 hay 32: chỉ là trần lúc dựng mẫu trong bộ nhớ (mỗi kho vài dòng), không đổi kết quả. Lớp bọc `_Checked` và so rồi đặt của kho nháp không đổi.

**So hành vi bản cũ và bản mới** (`probe_diff.py`, chạy cùng một script trên cây `71322c4` và cây `81a3016`). Mỗi ca: dựng file hợp lệ có dữ liệu bằng chính kho (kho nháp có «đã gửi 501»), làm hỏng, mở kho mới, rồi đọc, ghi, đọc lại; ghi kết quả từng bước, câu lỗi, các file còn trong `data/`. 15 kiểu: không hỏng, «unsupported file format», cỡ trang sai, file cụt, rác, file trống, UTF-8 hỏng trong `sqlite_master`, trigger, khung nhìn, bảng lạ, byte 18 = 3, byte 19 = 3, chỗ đặt file là thư mục, file chỉ đọc, ô chữ UTF-8 hỏng (chỉ kho nháp). Tổng 71 ca:

| Kết quả | Ca |
|---|---|
| **Y hệt bản cũ** | 62/71 |
| Khác đúng như phiếu (LC-T131-1, GN-1, B.4) | 6: byte 18 = 3 ở kho nháp, kho thẻ (cất sang một bên, dùng file mới; bản cũ kẹt câu lỗi), ở `site_index`, `plan_cache` (bỏ file, ghi lại được; bản cũ đọc được nhưng ghi kẹt); ô UTF-8 hỏng ở kho nháp (bỏ đúng dòng đó, khóa «đã gửi 501» còn đọc được; bản cũ kẹt); file nháp chỉ đọc (câu «chỉ đọc» thay cho «bị lỗi») |
| Khác ngoài dự định | 3: chỗ đặt file của `site_index`, `plan_cache`, `search_cache` là **thư mục** → câu báo đổi (G1). Hành vi giữ nguyên: không xóa, không ghi |

Byte 19 = 3 ở cả 5 kho: y hệt bản cũ (SQLite đã báo «not a database», file lạ từ trước).

### 2. LC-T131-1 (a): dòng hỏng UTF-8 bị bỏ khi liệt kê

`_Checked.keep_bad_text()` chỉ đổi cách đọc chữ trong đúng thao tác liệt kê (`list_drafts`, `find_plan_draft`, `list_plan_writes`); cấu trúc vẫn đọc thành byte. Ca của tôi: ô tiêu đề hỏng mã → danh sách bỏ đúng nháp đó (`skipped = 1`), không cất cả file; `load_send_state`, `send_state_if_exists` vẫn trả «đã gửi 501» (tab đang mở bài không thấy «nháp không còn», bước Xuất bản vẫn khóa); lần tự lưu kế (so rồi đặt) ghi lại dòng, nháp hiện lại. Ca của Thợ Máy và ca Lá Chắn `[utf8-hong-trong-o]` (gỡ dấu `xfail`) qua.

### 3. LC-T131-1 (b): byte 18–19 lớn hơn 2 là file lạ

`newer_file_format` đọc 20 byte đầu trước khi SQLite mở; chạy trong `is_healthy` của 4 kho và `_is_healthy` riêng của kho thẻ. So hành vi ở mục 1: cả 5 kho thoát được (cất hay bỏ file). Ca Thợ Máy (5 kho × 2 byte), ca Lá Chắn `[byte-18-la-3]` qua.

### 4. Cất file nháp hỏng mà vẫn giữ dấu «đã gửi»

Thợ Máy chọn cách câu báo (phiếu cho chọn), không chép dòng trạng thái gửi từ file lạ sang file mới. Ca của tôi: file nháp có byte 18 lạ, có «đã gửi 501» → kho dùng file mới; file cất đi (`drafts.hong-…`, mở chỉ đọc) **còn nguyên** dòng «đã gửi 501»; câu `MSG_RECOVERED` có tên file, nói lối tắt, dấu «đã gửi» và nhắc xem WordPress. Không đường nào của phiếu xóa dòng trạng thái gửi (đọc mã: chỉ hai đường cũ của T-089, T-130).

### 5. Câu báo lối tắt, chỉ đọc

- `MSG_RECOVERED` (dùng chung ba trang Bài viết, Kế hoạch, Soạn bài; trang Soạn bài nay thoát Markdown tên file như hai trang kia): thêm «Nếu chỗ đặt file nháp là một lối tắt thì chỉ lối tắt được cất đi, nơi nó trỏ tới không bị đụng», và câu về dấu «đã gửi». `test_app_drafts.py::test_corrupt_drafts_file_is_reported` vẫn qua (câu mới giữ đoạn cũ).
- Mã 8 (`SQLITE_READONLY`) ở kho nháp → «File nháp đang ở chế độ chỉ đọc…» (so hành vi: ca file chỉ đọc).

### 6. GN-1, GN-2, GN-3 (Soi Lỗi T-131)

- **GN-1:** byte 18–19 ở cả 5 kho (mục 3).
- **GN-2:** `plan_cache` tạo cả hai bảng trong một giao dịch ghi, kiểm lại cấu trúc trong giao dịch đó (`sqlite_file.create_tables`, như `site_index`, `search_cache`); ca vết câu SQL của Thợ Máy qua.
- **GN-3:** bộ mã giữ file chung có 13 (đầy ổ); ca Thợ Máy (4 kho × 4 mã) qua.

### 7. R5

`tests/test_la_chan_t131.py`: chỉ xóa dấu `xfail` (7 dòng) của ca LC-T131-1; thân, tham số, kỳ vọng không đổi. Không ca cũ nào khác đổi.

### 8. Chạy chọn lọc

Cây `81a3016` (cùng mã với cây gộp `481f3ed`), qua `run_list.sh` (kiểm danh sách, thiếu file thì dừng; dòng đầu mỗi lô đã xem), 7 lô nối tiếp, mỗi lúc một tiến trình. Danh sách: mọi file test nhắc kho nháp, kho thẻ ảnh, `site_index`, `plan_cache`, `search_cache`, `sqlite_file` (87 file), cộng mọi test quét cả cây mã nguồn `seo_app` (`glob`, `rglob`, `iterdir`; phiếu thêm file mới `sqlite_file.py`) và ba trang Bài viết, Kế hoạch, Soạn bài: 106 file, cộng file của tôi.

| Lô | Số file | Kết quả |
|---|---|---|
| 0 | 16 | 1.306 passed, 20 skipped, 3 xfailed |
| 1 | 16 | 1.827 passed, 8 skipped |
| 2 | 15 | 1.942 passed, 1 skipped, 7 xfailed |
| 3 | 16 | 1.597 passed, 1 xfailed |
| 4 | 16 | 1.755 passed |
| 5 | 14 | 766 passed |
| 6 | 14 (có file của tôi) | 944 passed, 4 skipped |

Cộng: **10.137 passed, 33 skipped, 11 xfailed, 0 failed, 0 XPASS**. Ca bỏ qua đều do Windows (tạo symlink cần Developer Mode, quyền kiểu POSIX, `os.environb`, ổ không phân biệt hoa thường). Xfail đều có từ trước (`test_images_folders_soi_loi` r2, SL-T070-4, SL-T107-3). Hai lần ngắt giữa chừng (phiên dừng): kiểm lại bản sao (`tar --compare` với `git archive`), không còn tiến trình cũ, chạy lại lô dở.

## Lỗi mới

Không có.

## Ghi nhận (không tính lỗi, không chặn)

- **G1 · Chỗ đặt file lưu tạm là thư mục: câu báo đổi.** `newer_file_format` mở thẳng đường dẫn bằng `open()` trước SQLite; với thư mục, Windows báo `PermissionError`, nên ba kho lưu tạm nay báo «Không tạo được file lưu tạm danh sách bài (Permission denied).», «Không ghi được file lưu tạm kế hoạch (Permission denied).», «Không đọc, ghi được file lưu tạm số liệu Search Console (Permission denied).» thay cho «Không mở được … (có thể chương trình khác đang giữ file, hoặc không có quyền…)». Hành vi không đổi (giữ thư mục, không ghi). Câu mới nói sai nguyên nhân (không phải thiếu quyền). Gợi ý phiếu chữ sau: `newer_file_format` trả `False` khi chỗ đó không phải file thường (để SQLite báo như cũ), hay câu riêng như kho nháp («Chỗ đặt file … đang là một thư mục»).
- **G2 · «Bài trùng vẫn chỉ là bài nháp»** (báo cáo Thợ Máy, mục chọn 3): đúng khi công tắc Hẹn giờ/Đăng ngay tắt (mặc định); khi đã bật, lần gửi lại sau khi file nháp bị cất có thể hẹn giờ hay đăng. Câu `MSG_RECOVERED` đã nhắc xem WordPress trước khi gửi lại, và việc cất file chỉ xảy ra khi chương trình khác sửa file; không đổi kết luận.
- **G3 · Ca symlink** của T-131, T-136 vẫn bỏ qua trên máy này (Windows chưa bật Developer Mode): chạy trên Mac/Linux cùng B.3.

## Lệnh đã chạy

- `pytest tests/test_soi_loi_t136.py` (cây nhánh): 2 passed.
- So hành vi bản cũ, bản mới (`probe_diff.py`, `python -I -X utf8`, chạy với thư mục làm việc là từng cây): 71 ca, 62 y hệt (mục 1).
- 7 lô chọn lọc, 107 file: 10.137 passed, 33 skipped, 11 xfailed, 0 failed (mục 8).
- `uv run ruff check .`: sạch.
- `detect-secrets` (`PYTHONUTF8=1`), quét bản sao trong thư mục ngoài git cùng file mồi tiếng Việt: sạch (chỉ file mồi bị báo; file test và báo cáo không có gì).
- Script: thư mục ghi chú chung `T-136-soi-loi-scripts/` (`probe_diff.py`, `run_list.sh`).

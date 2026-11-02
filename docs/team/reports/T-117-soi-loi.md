# Báo cáo T-117 · `data/` là liên kết: cache ảnh xem trước, kho thẻ ảnh không ghi ra ngoài (LC-T116-1) · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | T-117 `docs/team/tickets/T-117-data-junction-cache-the-anh.md` (đọc ở bản trên `main`) · mức kiểm **rút gọn**, Windows. Không chạy cloud, không đụng website |
| Ngày nộp | 2026-11-02 |
| Máy kiểm | Windows 11 Pro 10.0.26300, Python 3.12.15. Tài khoản thường: tạo được junction, **không** tạo được symlink (WinError 1314). Ổ D: tắt tên 8.3, ổ C: bật. Máy đang chạy toàn bộ test trên `main` |
| Mã nguồn | `team/T-117` tại `f397466` (mã + test `0cef836`; = `origin/main` `731a46e` + T-116 nhóm 1). Gộp thử với `main` `935d381` (= `origin/main`) |
| Kết quả | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp có từ trước** (SL-T117-1: kho nháp, cache kế hoạch, danh sách bài đã đăng vẫn ghi xuyên khi `data/` là liên kết; Thợ Máy đã đề xuất; không chặn Lá Chắn với T-117). LC-T116-1 đóng đúng ý: junction thật trỏ sang ổ khác, junction treo, tên 8.3, mọi tầng `data/…`; câu báo cố định, không đường dẫn; app vẫn chạy. Khe «đặt liên kết giữa lần kiểm và lần ghi» có thật, đúng như Thợ Máy ghi (cùng lớp «phải chiếm máy trước»). Không lùi T-048, T-052, T-074, T-079, T-080, T-107, T-078. R5 chỉ gỡ đúng 2 dấu `xfail`. Thử đột biến: thêm 1 test (qua) cho nhánh «kiểm không được thì không dùng cache». Gộp `main` `935d381` sạch |

## Tóm tắt (cho chủ dự án)

- **Lỗi của phiếu đã sửa đúng.** Nếu thư mục `data` của phần mềm bị thay bằng lối tắt trỏ ra chỗ khác:
  - ảnh xem trước vẫn hiện, nhưng không ghi gì ra chỗ đó;
  - lưu thẻ ảnh báo một câu cố định, không đường dẫn; app vẫn chạy.

  Đã thử lối tắt thật trỏ sang ổ đĩa khác, lối tắt «treo», tên thư mục kiểu rút gọn của Windows: đều chặn đúng.
- **Ba chỗ khác cũng ghi vào `data` chưa có lớp chặn này** (lỗi nhỏ có từ trước, mức Thấp như lỗi gốc): bài nháp, bản lưu tạm kế hoạch, danh sách bài đã đăng. Thợ Máy đã đề xuất sửa ở phiếu sau. Tôi đồng ý nên làm, kho bài nháp trước. Đã viết sẵn test cho phiếu đó.
- Còn một khe rất hẹp đã biết: lối tắt đặt vào đúng phần nghìn giây giữa lúc kiểm và lúc ghi thì không chặn được. Muốn lợi dụng phải chiếm được máy trước.
- Không ảnh hưởng chức năng khác.

## Việc 1 · Junction thật ở mọi tầng, ổ khác, 8.3, reparse point khác — **đạt**

Test của Thợ Máy (`tests/test_t117_data_dir_links.py`, 24 ca) đã phủ:
- junction thật ở `data` và `data/image_previews`;
- liên kết đặt vào khi cache đang chạy;
- file cache là liên kết (giả lập);
- giả lập Mac/Linux (symlink);
- giả lập các loại reparse point: symlink Windows, junction, symlink WSL, OneDrive «chỉ trực tuyến».

Tôi thử thêm bằng junction thật (`sl117_real.py`, `sl117_83.py`):

| Ca | Kết quả |
|---|---|
| **Ổ khác.** Dự án giả trên D:, `data` → junction tới thư mục trên C: | Cache ép bật: ảnh xem trước vẫn trả về, **0 file** ở C:. Kho thẻ: `ImageTagStoreError` câu cố định `MSG_DATA_DIR_LINK`, 0 file ở C: |
| Ổ khác, `data/image_previews` → junction tới C: (`data` thường) | Cache: 0 file ở C:. Kho thẻ ghi bình thường vào `data/` thật (đúng, liên kết không nằm trên đường của nó) |
| **Junction treo** (thư mục đích đã xóa) | `dir_has_link` = `True`. Cache không tạo lại thư mục đích. Kho thẻ từ chối câu cố định |
| **8.3** trên C: (dạng ngắn `SL117-~1\THU-MU~1`): `PROJECT_ROOT` dài + thư mục cache ngắn; `PROJECT_ROOT` ngắn + cache dài; cả hai ngắn | Cả 3 cách: `dir_has_link` = `True`, 0 file qua junction. Kho thẻ (`PROJECT_ROOT` dài, đường dẫn kho ngắn): từ chối. Nhánh «ngoài gốc» xét chính thư mục và thư mục cha nên vẫn bắt được. App thật luôn dựng đường dẫn từ `PROJECT_ROOT` đã `resolve()`, nên không trộn hai dạng |
| **Hardlink** ở chính file cache, trỏ tới file ngoài cùng ổ | Ghi: `_write` dùng file tạm rồi `os.replace`, nên file ngoài **không** bị ghi đè. Đọc: cache trả nội dung file ngoài (nếu là JPEG sạch). Ghi nhận GN-2 |
| Reparse point khác junction | Không tạo được symlink thật (thiếu quyền), mount point tới volume cần quyền quản trị. Giả lập của Thợ Máy đã phủ symlink Windows, symlink WSL, junction, OneDrive. Định nghĩa dùng chung `_is_link_stat` (cờ «name surrogate» của reparse tag), cùng định nghĩa lớp đọc ảnh T-048/T-079 |

Mac/Linux: chỉ giả lập. Test của Thợ Máy giả `lstat` trả `S_IFLNK` cho `data` và cho chính file cache: không tạo thư mục, không đọc, không ghi qua. App không dùng `O_NOFOLLOW`; trên Mac/Linux, `is_link` + `lstat` từng tầng và ghi bằng `mkstemp` + `os.replace` đủ cho ca liên kết **có sẵn**. Ca đặt vào giữa chừng là khe ở Việc 2.

Câu báo: `MSG_DATA_DIR_LINK` là câu cố định, không đường dẫn. `repr(PreviewCache)` không in đường dẫn. Cache bỏ qua lặng lẽ, ảnh xem trước vẫn dựng.

## Việc 2 · Liên kết đặt vào giữa chừng (sau lần kiểm, trước lần ghi) — **khe đã ghi nhận, giữ mức**

Thử thật bằng cách chèn junction đúng sau lần kiểm:

| Ca | Kết quả |
|---|---|
| Cache ảnh: `data/image_previews` (chưa có) thành junction ngay trước `_write` (sau lần kiểm thứ hai) | **Ghi xuyên**: 1 file `<băm>.jpg` ở thư mục đích |
| Kho thẻ: `data` (chưa có) thành junction ngay sau `dir_has_link` trong `_prepare`, trước `mkdir` + `sqlite3.connect` | **Ghi xuyên**: `image_tags.sqlite` tạo ở thư mục đích |
| Liên kết đặt **giữa hai lần dùng** (test của Thợ Máy) | Lần dùng sau bị chặn, vì mỗi lần đọc/ghi/mở đều kiểm lại |

Đúng như docstring `data_dir.py` và báo cáo Thợ Máy («Rủi ro»):
- SQLite chỉ mở được theo đường dẫn, nên không làm được kiểu mở từng tầng bằng handle như T-079;
- muốn lợi dụng phải chạy được chương trình trên máy và ghi được vào thư mục cài app.

Cùng lớp «phải chiếm máy trước» trong sổ rủi ro, không tính là lỗi mới. Đề nghị Lá Chắn ghi một dòng sổ rủi ro nếu chưa có.

## Việc 3 · Chỗ khác ghi vào `data/` → **SL-T117-1 (Thấp, có từ trước)**: đồng ý Đề xuất 1 của Thợ Máy

Thử thật với `data` là junction ra ngoài (`tests/test_soi_loi_t117.py`, `xfail(strict=True)`):

| Kho | File ghi ra ngoài | Mã |
|---|---|---|
| Nháp bài viết `DraftStore.save` | `drafts.sqlite` | `seo_app/storage/drafts.py` `_prepare`: không kiểm liên kết ở tầng nào |
| Cache kế hoạch `PlanCacheStore.save` | `plan_cache.sqlite` | `seo_app/storage/plan_cache.py` `_prepare`: chỉ `self.path.is_symlink()` ở chính file (không bắt junction, không xét thư mục cha) |
| Danh sách bài đã đăng `SiteIndexStore.save` | `site_index.sqlite` | `seo_app/storage/site_index.py` `_prepare`: như trên |

Cùng loại và cùng điều kiện với LC-T116-1, nên cùng mức Thấp. Có từ trước, ngoài phạm vi T-117: phiếu chỉ sửa hai chỗ dùng chung đường dẫn.

**Có cần làm không:** có, ở một phiếu nhỏ như Đề xuất 1 của Thợ Máy:
- thêm `dir_has_link(self.path.parent, PROJECT_ROOT)` đầu `_prepare` của ba kho;
- hai kho sau đổi `is_symlink()` thành `is_link()`, để bắt cả junction.

Làm kho nháp trước, vì nó giữ bài chưa gửi. Test đỏ sẵn có: khi sửa xong, 3 ca XPASS thì gỡ dấu `xfail` (R5). Test không ràng cách sửa: chỉ đòi không có file ở nơi liên kết trỏ tới; kho được báo lỗi riêng.

Đề xuất 2 (giao diện báo một lần khi cache bị bỏ qua) và Đề xuất 3 (README) là tùy chọn. Tôi thấy không cần cho an toàn.

## Việc 4 · Không lùi T-048, T-052, T-074, T-079, T-080, T-107, T-078; R5 — **đạt**

- Test chọn lọc trên nhánh, 23 file: `test_t117_data_dir_links`, `test_la_chan_t116_nhom1`, `test_soi_loi_t117`, `test_images_folders`, `test_images_folders_soi_loi`, `test_images_tags`, `test_soi_loi_t052`, `test_la_chan_t074`, `test_soi_loi_t074`, `test_la_chan_t079`, `test_soi_loi_t079`, `test_soi_loi_t080`, `test_t107_heic_tat`, `test_t107_heif_mot_luong`, `test_soi_loi_t107`, `test_la_chan_t107`, `test_t078_avif_uv`, `test_images_process`, `test_app_images`, `test_drafts_images`, `test_soi_loi_t070`, `test_soi_loi_t077`, `test_soi_loi_t055`.
  - Kết quả: **2093 qua, 16 bỏ qua, 18 xfail, 0 hỏng, không XPASS** (13 phút, máy bận).
  - 18 xfail gồm 3 ca SL-T117-1 mới và 15 ca có từ trước của phiếu khác.
- R5: `tests/test_la_chan_t116_nhom1.py` chỉ xóa đúng 2 khối `@pytest.mark.xfail(strict=True, …)` của LC-T116-1 (10 dòng). Thân test giữ nguyên, nay qua. Không test cũ nào khác bị đổi.
- `ruff check`, `ruff format --check` file test mới: sạch.

## Việc 5 · Gộp thử với `main` `935d381` — **sạch**

- `main` cục bộ = `origin/main` = `935d381`, chứa `731a46e`.
- `git merge-tree --write-tree 935d381 team/T-117`: **không xung đột** (cây `085cc6e`).
- Từ `731a46e`, `main` có sửa `app/views/write.py` (nơi dùng cache ảnh, kho thẻ) và `tests/test_app_images.py`. Vì vậy đã gộp thật ở worktree tạm tách rời (commit treo `6e15f76`, không đẩy; đã kiểm `seo_app` nạp từ chính worktree tạm) rồi chạy 10 file: `test_t117_data_dir_links`, `test_la_chan_t116_nhom1`, `test_soi_loi_t117`, `test_app_images`, `test_drafts_images`, `test_images_process`, `test_images_tags`, `test_soi_loi_t052`, `test_soi_loi_t074`, `test_t110_gan_anh_vao_bai_nhap`. Kết quả: **1241 qua, 3 bỏ qua, 3 xfail (SL-T117-1), 0 hỏng, không XPASS** (15 phút).
- Worktree tạm đã gỡ.

## Thử đột biến (`sl117_mutate.py`)

Mỗi đột biến chạy trên một bản sao `git archive` riêng, với 3 file `test_t117_data_dir_links`, `test_la_chan_t116_nhom1`, `test_soi_loi_t117`.

| Đột biến | Test hỏng |
|---|---|
| D1 `dir_has_link` không bao giờ thấy liên kết | 17 |
| D2 bỏ tầng cuối | 8 |
| D3 chỉ xét tầng cuối | 10 |
| D4 bỏ kiểm chính file cache | 1 |
| D5 chỉ kiểm trước khi đọc, không kiểm lại trước khi ghi | 6, gồm LC-T116-1 |
| D6 chỉ kiểm trước khi ghi | 2 |
| D7 `lstat` lỗi lạ thì coi như không có liên kết (mở thay vì đóng) | **0 lúc đầu: lọt.** Soi Lỗi thêm `test_preview_cache_check_error_means_no_cache` (**qua** trên nhánh). Chạy lại: **1 hỏng** |
| D8 kho thẻ bỏ kiểm | 5, gồm LC-T116-1 |
| D9 nhánh «ngoài gốc» chỉ xét chính thư mục | 1 |
| D10 xét cả gốc dự án (gốc nằm dưới lối tắt hợp lệ bị chặn oan) | 1 |
| D11 chỉ bắt symlink, bỏ junction | 14 |

Kết luận: sau test bổ sung, test bắt được mọi đột biến làm đổi hành vi.

## Lỗi mới

| Mã | Mức | Mô tả | Test |
|---|---|---|---|
| **SL-T117-1** | Thấp (có từ trước, cùng loại LC-T116-1) | `data/` là liên kết thì kho nháp, cache kế hoạch, danh sách bài đã đăng tạo và ghi file SQLite ở nơi liên kết trỏ tới, ngoài thư mục dự án. Thợ Máy đã nêu ở Đề xuất 1; Soi Lỗi xác nhận bằng junction thật và viết test | `tests/test_soi_loi_t117.py::test_sl_t117_1_other_data_stores_never_write_through_link` (3 ca, `xfail(strict=True)`; `--runxfail`: hỏng đúng chỗ, mỗi kho 1 file ở ngoài) |

Không chặn Lá Chắn với T-117.

## Ghi nhận (không phải lỗi)

- **GN-1:** khe giữa lần kiểm và lần ghi (Việc 2), như docstring và báo cáo Thợ Máy.
- **GN-2:** `data_dir.is_link` không coi hardlink là liên kết; kho thẻ (`image_tags._is_link`) thì có coi (`st_nlink > 1`). Với cache ảnh, hardlink ở file cache chỉ làm cache **đọc** nội dung file kia nếu là JPEG sạch; ghi thì thay chỗ, không ghi xuyên. Ai đặt được hardlink trong `data/` thì cũng ghi thẳng file vào đó được, nên không thêm quyền gì. Hai định nghĩa «liên kết» khác nhau ở hai nơi, nên ghi chú để khỏi nhầm khi dùng chung `data_dir` cho các kho khác (SL-T117-1): kho SQLite nên giữ phép kiểm hardlink ở chính file như kho thẻ.
- **GN-3:** người dùng cố ý dời `data` sang ổ khác bằng lối tắt thì mất cache lặng lẽ và không lưu được thẻ (có câu báo). Đúng chủ ý F1. README chưa nói (Đề xuất 3 của Thợ Máy).

## Tệp và cách chạy lại

- Test: `tests/test_soi_loi_t117.py`:
  - 3 `xfail(strict=True)` cho SL-T117-1;
  - 1 test bổ sung (qua): `test_preview_cache_check_error_means_no_cache`.

  Chạy: `uv run pytest tests/test_soi_loi_t117.py -rxX`.
- Script (thư mục ghi chú chung, `T-117-soi-loi-scripts/`, chạy từ worktree bằng `.venv/Scripts/python.exe -X utf8 <script>`):
  - `sl117_real.py`: junction thật trỏ sang ổ khác, junction treo, hardlink, chèn junction giữa chừng;
  - `sl117_83.py`: tên 8.3 trên C:;
  - `sl117_mutate.py`: 11 đột biến.

  Dự án giả nằm ở `D:\ProMetal-ToolSEO\_sl117_tam`, xóa ngay khi script chạy xong.
- detect-secrets (`PYTHONUTF8=1`, có file mồi trong thư mục tạm): file test và báo cáo **0** phát hiện; file mồi 2 phát hiện.

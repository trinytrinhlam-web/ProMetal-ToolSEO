# Báo cáo T-117 · Thư mục `data/` là liên kết: cache ảnh xem trước và kho thẻ ảnh không ghi ra ngoài dự án (LC-T116-1)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-117](../tickets/T-117-data-junction-cache-the-anh.md) (LC-T116-1 của Lá Chắn T-116 nhóm 1, kiểm bằng Fable) |
| Nhánh | `team/T-117`, từ `origin/main` `731a46e` cộng nhánh T-116 `3669046`; commit thay đổi chính `0cef836` |
| Ngày nộp | 2026-11-02 (giờ máy, +07) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Phần mềm lưu hai loại dữ liệu phụ trong thư mục `data` cạnh phần mềm: **ảnh xem trước** (để khung chọn ảnh mở nhanh hơn) và **thẻ ảnh bạn sửa tay**. Lá Chắn phát hiện: nếu ai đó đã vào được máy đổi thư mục `data` thành một «lối tắt» trỏ sang chỗ khác, phần mềm sẽ ghi hai loại dữ liệu đó sang chỗ kia. Mức thấp, vì muốn làm vậy phải có quyền ghi vào thư mục phần mềm trước.
- Nay phần mềm kiểm từng tầng thư mục trước **mỗi lần** đọc, ghi. Gặp lối tắt:
  - Ảnh xem trước vẫn hiện bình thường, chỉ không lưu lại để lần sau mở nhanh.
  - Thẻ ảnh sửa tay không được lưu, phần mềm báo câu «Thư mục dữ liệu của phần mềm (…) là lối tắt trỏ ra chỗ khác nên phần mềm không ghi vào đó. Hãy thay lối tắt đó bằng một thư mục thường.». Câu báo không lộ đường dẫn. Thẻ đọc từ tên thư mục ảnh vẫn dùng được.
  - Thay lối tắt bằng thư mục thường thì mọi thứ chạy lại ngay, không cần mở lại phần mềm.
- Máy bình thường (không ai tạo lối tắt) không thấy gì khác.
- Ba kho khác cũng ghi vào `data` (bài nháp, cache kế hoạch, danh sách bài đã đăng) chưa có lớp kiểm này. Theo phiếu, tôi chỉ ghi đề xuất, chưa sửa (mục Đề xuất).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/images/data_dir.py` | **Mới.** Hàm dùng chung `dir_has_link(directory, root)`: `lstat` từng tầng từ ngay dưới gốc dự án xuống tới thư mục; không đi theo liên kết, không `resolve`; tầng chưa có trên ổ thì dừng (app sẽ tự tạo nó là thư mục thường). `is_link(path)`: xét một tầng. Câu cố định `MSG_DATA_DIR_LINK`. «Liên kết» dùng đúng định nghĩa của lớp đọc ảnh, `folders._is_link_stat` (T-048, T-079): symlink; trên Windows thêm junction và mọi reparse point có bit «name surrogate»; thư mục «chỉ trực tuyến» của OneDrive, Google Drive không tính |
| `seo_app/images/process.py` | `PreviewCache._no_link(path)`: **trước mỗi lần đọc và mỗi lần ghi** cache (trong `get`), kiểm thư mục cache từ ngay dưới `PROJECT_ROOT` và chính file cache. Có liên kết, hay không kiểm được, thì lần đó không dùng cache; ảnh xem trước vẫn được dựng và trả về. Kiểm mỗi lần vì đối tượng cache sống suốt phiên app (`st.cache_resource`, `app/views/write.py:893-900`), liên kết có thể được đặt vào sau. `enabled`, `_cache_dir_is_ignored`, cách dựng ảnh không đổi |
| `seo_app/storage/image_tags.py` | `ImageTagStore._prepare` (chạy ở **mỗi lần mở**): thư mục chứa file là liên kết thì báo `ImageTagStoreError(MSG_DATA_DIR_LINK)` **trước** khi tạo thư mục hay mở SQLite. Không tự gỡ liên kết thư mục (có thể là của người dùng, ví dụ cố ý dời `data` sang ổ khác). Phần gỡ liên kết ở chính file `.sqlite` và file nhật ký (SL-T052-7, -8) giữ nguyên |
| `tests/test_t117_data_dir_links.py` | **Mới**, 15 hàm test, 22 ca (mục Bằng chứng) |
| `tests/test_la_chan_t116_nhom1.py` | Gỡ 2 dấu `xfail(strict=True)` LC-T116-1 sau khi cả hai XPASS. Chỉ xóa 2 khối trang trí, không đổi thân test (R5) |
| `docs/team/reports/T-117-tho-may.md` | Báo cáo này |

Không đụng `app/**`, phần đọc ảnh của `folders.py` (chỉ dùng lại `_is_link_stat`), cách băm, cách dựng thẻ.

**Vì sao hàm dùng chung nằm ở `seo_app/images/` chứ không ở `seo_app/storage/`** (Lá Chắn gợi ý `storage`): nhập bất kỳ module nào trong `seo_app.storage` là chạy `storage/__init__.py`, file này nạp kho nháp (kéo theo lớp AI, quy trình nội dung). Đo bằng `python -X importtime` khi đặt ở `storage`: `process.py` nạp thêm khoảng 1,86 trên tổng 3,06 giây (máy đang bận). Đặt cạnh `folders.py` thì module mới nạp mất khoảng 3 ms, và `process.py` không còn kéo `seo_app.storage`. `image_tags.py` vốn đã nhập từ `seo_app.images` nên không thêm chiều phụ thuộc mới. Đã thử nạp theo 6 thứ tự (`process`, `image_tags`, `drafts`, `data_dir`, `storage`, `wordpress.client` trước): không vòng nhập.

```
$ git diff --stat 3669046..0cef836
 seo_app/images/data_dir.py        |  67 +++++++++
 seo_app/images/process.py         |  16 +-
 seo_app/storage/image_tags.py     |  12 +-
 tests/test_la_chan_t116_nhom1.py  |  10 --
 tests/test_t117_data_dir_links.py | 305 ++++++++++++++++++++++++++++++++++++++
 5 files changed, 396 insertions(+), 14 deletions(-)
```

Cộng thêm báo cáo này (commit sau). Gộp thử (`git merge-tree --write-tree`): với `origin/main` mới nhất `c7a8df9` (đã gộp T-110 lượt 2–3) không xung đột, `main` không đổi file nào của phiếu kể từ `731a46e`; với `origin/team/T-116` mới nhất `c73fc21` (thêm biên bản nhóm 3) không xung đột.

## Chỗ khác ghi vào `data/` (yêu cầu 2)

| Kho | Đường dẫn dựng ở | Đang chặn liên kết thế nào | Áp dụng hàm mới? |
|---|---|---|---|
| Nháp bài viết | `seo_app/storage/drafts.py:107` (`DEFAULT_DRAFTS_FILE`), `_prepare` `:1136-1145` | **Không kiểm** liên kết ở tầng nào: `mkdir` rồi `sqlite3.connect` thẳng | Nên. Hàm dựng đường dẫn riêng (không chung với 2 nơi của phiếu) nên **chưa sửa**, theo phiếu → Đề xuất 1 |
| Cache kế hoạch | `seo_app/storage/plan_cache.py:39` (`DEFAULT_PLAN_CACHE_FILE`), `_prepare` `:234-241` | Chỉ `self.path.is_symlink()` ở chính file: không bắt junction, không xét thư mục cha | Nên, cùng lý do → Đề xuất 1 |
| Danh sách bài đã đăng | `seo_app/storage/site_index.py:37` (`DEFAULT_SITE_INDEX_FILE`), `_prepare` `:283-290` | Như cache kế hoạch | Nên, cùng lý do → Đề xuất 1 |
| `.env` | `seo_app/env_file.py:261` (file tạm cạnh `.env`, ở gốc dự án, không ở `data/`) | `_read_env_text` từ chối `.env` là liên kết tắt | Không thuộc `data/`, ngoài phạm vi |

Tìm bằng `grep` mọi `PROJECT_ROOT / "data"`, `mkdir(`, `mkstemp`, `write_bytes(`, `write_text(` trong `seo_app/`, `app/`, `scripts/`: ngoài các chỗ trên không còn chỗ nào ghi vào `data/`.

## Bằng chứng

```
# 1. Gốc 3669046, trước khi sửa: 2 ca của Lá Chắn còn xfail
$ uv run pytest tests/test_la_chan_t116_nhom1.py -q -rxX
XFAIL …::test_lc_t116_1_preview_cache_khong_ghi_xuyen_lien_ket - LC-T116-1: …
XFAIL …::test_lc_t116_1_kho_the_khong_ghi_xuyen_lien_ket - LC-T116-1: …
2 xfailed in 15.11s

# 2. Đối chứng: file test mới chạy trên mã CŨ (chưa sửa process.py, image_tags.py)
$ uv run pytest tests/test_t117_data_dir_links.py -q
9 failed, 13 passed      (hỏng đúng 9 ca cache và kho thẻ gặp liên kết; 13 ca qua là ca của hàm
                          dùng chung mới và ca canh «thư mục thường vẫn dùng cache»)

# 3. Đã sửa mã, dấu xfail còn nguyên
$ uv run pytest tests/test_t117_data_dir_links.py tests/test_la_chan_t116_nhom1.py -q -rfEsxX
[XPASS(strict)] LC-T116-1: … PreviewCache …
[XPASS(strict)] LC-T116-1: … ImageTagStore …
2 failed, 22 passed in 3.05s

# 4. Gỡ 2 dấu, chạy 26 file test liên quan (danh sách dưới), bản đúng commit 0cef836
#    (mã băm 5 file trùng nhau lúc đầu, lúc cuối lượt chạy và lúc commit)
$ uv run pytest <26 file> -q -rfEsxX
2431 passed, 51 skipped, 14 xfailed in 1014.11s (0:16:54)

$ uv run ruff check .                     # ruff 0.16.10
All checks passed!

# 5. Không vòng nhập: nạp từng module trước trong trình thông dịch mới, rồi nạp cả ba
seo_app.images.process / seo_app.storage.image_tags / seo_app.storage.drafts /
seo_app.images.data_dir / seo_app.storage / seo_app.wordpress.client  → OK cả 6
$ uv run python -X importtime -c "import seo_app.images.process"
      3252 |       3252 |   seo_app.images.data_dir      (không còn seo_app.storage trong chuỗi nạp)

# 6. Quét bí mật, PYTHONUTF8=1, 5 file đổi + báo cáo
$ PYTHONUTF8=1 uvx detect-secrets scan …
results: {}
```

**26 file test liên quan:**

| Nhóm | File |
|---|---|
| Phiếu này | `test_t117_data_dir_links.py` (mới), `test_la_chan_t116_nhom1.py` (đã gỡ 2 dấu) |
| Dùng `PreviewCache`, `ImageTagStore`, xử lý ảnh | `test_app_images.py`, `test_drafts_images.py`, `test_images_process.py`, `test_images_tags.py`, `test_la_chan_t096.py`, `test_publish_render.py`, `test_soi_loi_t049.py`, `test_soi_loi_t052.py`, `test_soi_loi_t055.py`, `test_soi_loi_t056.py`, `test_soi_loi_t067.py`, `test_soi_loi_t070.py`, `test_soi_loi_t074.py`, `test_soi_loi_t077.py` |
| Đọc thư mục ảnh (không lùi T-048, T-079, T-080) | `test_images_folders.py`, `test_images_folders_soi_loi.py`, `test_images_folders_t063.py`, `test_la_chan_t074.py`, `test_la_chan_t079.py`, `test_soi_loi_t079.py`, `test_soi_loi_t079_linux.py`, `test_soi_loi_t080.py`, `test_soi_loi_t080_linux.py` |
| Mọi trang app | `test_app_pages.py` |

- **51 mục bỏ qua**, đều có từ trước và đều do máy là Windows: ca chỉ chạy trên Mac/Linux (symlink thật, quyền POSIX, `renameat2`, mở thư mục theo fd), hay cần quyền tạo symlink (Developer Mode). Gồm `test_images_folders.py` ×11, `test_images_folders_t063.py` ×11, `test_soi_loi_t079.py` ×2, `test_soi_loi_t079_linux.py` ×12, `test_soi_loi_t080_linux.py` ×12, `test_drafts_images.py:645`, `test_images_tags.py:1780`, `test_soi_loi_t052.py:538`. Ba mục cuối lấy từ một lượt chạy riêng các file đó (1277 passed, 3 skipped, 3 xfailed), vì bản tóm tắt của lượt chính bị cắt mất phần đầu. Không ca nào của `test_t117_data_dir_links.py` bị bỏ qua: các ca liên kết thật chạy bằng junction.
- **14 `xfail`**, đều đã biết và có từ trước: SL-T067-1 ×4, SL-T070-4 ×7, R2-1 ×2, R2-2 ×1. Không ca nào mới.

**Các ca test mới:**

| Ca | Kiểm gì |
|---|---|
| `test_real_dirs_have_no_link`, `test_missing_levels_stop_without_error` | Thư mục thường, tầng chưa có trên ổ: không phải liên kết, không lỗi |
| `test_real_link_at_any_level_is_found` ×2 | Liên kết thật ở `data` hay ở `data/image_previews` đều bị bắt |
| `test_root_reached_through_a_link_is_not_flagged` | Thư mục cài app nằm dưới một lối tắt hợp lệ: không chặn nhầm (gốc và tầng trên không xét) |
| `test_outside_root_checks_dir_and_its_parent` | Thư mục ngoài gốc (test): xét chính nó và thư mục cha |
| `test_simulated_link_kinds` ×6 | Giả lập `lstat`: symlink Mac/Linux, symlink Windows, junction, symlink WSL là liên kết; thư mục «chỉ trực tuyến» OneDrive và thư mục thường thì không |
| `test_preview_cache_normal_dirs_still_cache` | Canh: thư mục thường thì cache vẫn ghi, vẫn dùng lại |
| `test_preview_cache_never_writes_through_link` ×2 | Liên kết ở `data` hay tầng con: ảnh xem trước vẫn có, 0 file ghi ra ngoài (3 lần gọi, 2 ảnh) |
| `test_preview_cache_link_put_in_while_running` | Cache đang chạy, `data` bị thay bằng liên kết: không ghi ra ngoài, **không đọc** file JPEG đặt sẵn ở nơi liên kết trỏ tới |
| `test_preview_cache_file_link_not_read`, `test_preview_cache_simulated_posix_link_at_data` | Chính file cache là liên kết (giả lập): không đọc, không ghi đè qua nó. `data` là symlink (giả lập Mac/Linux): không tạo thư mục, không ghi |
| `test_tag_store_refuses_link_with_fixed_message` | Đúng câu cố định, không đường dẫn; đọc thẻ vẫn trả thẻ theo tên thư mục kèm câu báo; 0 file ra ngoài |
| `test_tag_store_link_put_in_after_first_use` | Kho đã dùng rồi `data` bị thay: lần mở sau báo câu cố định; file thật cũ không bị đụng |
| `test_tag_store_simulated_posix_link_at_data` | Giả lập Mac/Linux: báo trước khi tạo file SQLite |
| `test_tag_store_works_again_after_link_replaced_by_folder` | Làm theo câu báo (thay lối tắt bằng thư mục thường): dùng lại được ngay, không cần mở lại app |

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: kiểm từng tầng từ `PROJECT_ROOT` tới file (junction, symlink, reparse point trỏ đi chỗ khác trên Windows; `lstat` không đi theo liên kết trên Mac/Linux). Có liên kết thì không ghi, câu cố định không lộ đường dẫn. Cache ảnh xem trước gặp liên kết thì app vẫn chạy, chỉ không lưu cache (`seo_app/images/data_dir.py`, `PreviewCache._no_link`, `ImageTagStore._prepare`; test ở mục Bằng chứng)
- [x] Yêu cầu 2: một hàm dùng chung cho cả hai nơi. Đã tìm mọi chỗ khác ghi vào `data/` (kho nháp, cache kế hoạch, danh sách bài đã đăng); các chỗ đó không dùng chung hàm dựng đường dẫn nên chưa sửa, ghi vào Đề xuất 1 (mục «Chỗ khác ghi vào `data/`»)
- [x] Yêu cầu 3: test với junction thật trên Windows và giả lập Mac/Linux; không lùi T-048, T-052, T-074, T-079, T-080 (các file test của các phiếu đó qua hết, mục Bằng chứng). 2 ca `xfail` LC-T116-1 XPASS rồi gỡ dấu (chỉ xóa dấu, R5)
- [x] Test liên quan (26 file): 2431 passed, 51 skipped, 14 xfailed, 0 hỏng; `uv run ruff check .` sạch
- [x] F1: hai nơi ghi không còn ghi hay đọc qua liên kết ở tầng thư mục; phần đọc ảnh của `folders.py` không đổi. F2: không đổi giới hạn ảnh, EXIF, GPS
- [x] Báo cáo nộp tại `docs/team/reports/T-117-tho-may.md`
- [ ] Toàn bộ `uv run pytest` trên Windows: việc của Chỉ Huy khi gộp

## Rủi ro và điểm cần chú ý

- **Khoảnh khắc giữa lúc kiểm và lúc ghi.** Kiểm bằng `lstat` theo đường dẫn, nên liên kết đặt vào đúng khoảnh khắc sau lúc kiểm, trước lúc ghi thì không bị chặn. Cache ảnh kiểm lại ngay trước khi ghi, sau bước dựng ảnh tốn thời gian. SQLite chỉ mở được theo đường dẫn, nên không làm được kiểu mở từng tầng bằng handle như T-079. Muốn lợi dụng khe này phải chạy được chương trình trên máy và ghi được vào thư mục cài app, cùng lớp «phải chiếm máy trước» trong sổ rủi ro.
- **Ai cố ý dời `data/` sang ổ khác bằng lối tắt** thì nay mất cache ảnh xem trước (lặng lẽ) và không lưu được thẻ sửa tay (có câu báo). Đây là chủ ý (F1). README chưa nói điều này (Đề xuất 3).
- **Thư mục nằm ngoài gốc dự án** (chỉ có trong test, khi trỏ kho sang thư mục tạm): hàm chỉ xét chính thư mục và thư mục cha của nó, không xét các tầng trên nữa. App thật luôn dùng `PROJECT_ROOT / "data" / …`, nên được xét đủ mọi tầng từ ngay dưới gốc.
- **Gốc dự án và các tầng trên nó không bị xét**, có chủ ý: thư mục cài app có thể nằm dưới một lối tắt hợp lệ của máy (có test `test_root_reached_through_a_link_is_not_flagged`).
- **Mac/Linux:** máy này là Windows nên các ca dùng liên kết thật chạy bằng junction. Trên Mac/Linux, cùng các ca đó tạo symlink thật (`os.symlink`), nhưng chưa chạy ở đây (chủ dự án chưa có Mac; lượt Linux bằng cloud chỉ chạy khi được duyệt). Nhánh symlink kiểu Mac/Linux được phủ bằng ca giả lập kết quả `lstat`.
- `_cache_dir_is_ignored` vẫn `resolve` thư mục cache (không đổi). Ca `data/` là liên kết nay bị chặn trước, ở bước kiểm từng tầng mỗi lần đọc, ghi.

## Đề xuất

1. **Thợ Máy, phiếu nhỏ (Thấp).** Thêm một dòng `dir_has_link(self.path.parent, PROJECT_ROOT)` ở đầu `_prepare` của kho nháp, cache kế hoạch, danh sách bài đã đăng, kèm test như `tests/test_t117_data_dir_links.py`. Với hai kho sau, đổi luôn `self.path.is_symlink()` thành `is_link(self.path)` để bắt cả junction. Nên làm kho nháp trước vì nó giữ bài chưa gửi.
2. **Họa Sĩ (tùy chọn, Thấp).** Khi cache ảnh xem trước bị bỏ qua vì gặp lối tắt, giao diện chưa báo gì (ảnh vẫn hiện, chỉ chậm hơn). Có thể hiện câu `MSG_DATA_DIR_LINK` một lần ở khung chọn ảnh.
3. **Thư Ký (tùy chọn).** README thêm một dòng: không thay thư mục `data` bằng lối tắt; muốn dời thì chép cả thư mục phần mềm.

## Câu hỏi cho chủ dự án

Không có.

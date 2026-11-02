# Biên bản bảo mật T-117 · Thư mục `data/` là liên kết: cache ảnh xem trước và kho thẻ ảnh không ghi ra ngoài dự án (đóng LC-T116-1)

> **Model:** lượt này **chạy Fable 5.1** (dòng «You are powered by» của lời nhắc hệ thống: Fable 5.1, kiểm theo luật 08:05 của Chỉ Huy B). Quy trình và mức độ lỗi: `docs/team/security.md`.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **chạy Fable 5.1** · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-117](../tickets/T-117-data-junction-cache-the-anh.md) (phiếu chưa commit, đọc ở repo chính) · sửa **LC-T116-1** (Thấp, [biên bản T-116 nhóm 1](T-116-la-chan-nhom-1.md), tìm ra ở lượt kiểm Fable) |
| Phạm vi | diff `3669046..8c0190d` trên `team/T-117` (gốc `731a46e` + T-116 nhóm 1): `seo_app/images/data_dir.py` (**mới**, 67 dòng: `dir_has_link`, `is_link`, `MSG_DATA_DIR_LINK`), `seo_app/images/process.py` (`PreviewCache._no_link`, `get`), `seo_app/storage/image_tags.py` (`ImageTagStore._prepare`), `tests/test_t117_data_dir_links.py` (mới, 22 ca), `tests/test_soi_loi_t117.py` (mới, 1 ca + 3 `xfail`), `tests/test_la_chan_t116_nhom1.py` (gỡ 2 dấu `xfail`), 2 báo cáo. Kèm code xung quanh: `folders._is_link_stat`, `_cache_dir_is_ignored`, `PreviewCache._read/_write`, `image_tags._is_link/_remove_links`, nơi giữ hai đối tượng suốt phiên `app/views/write.py:883-897` và nơi hiện câu báo `:1255-1261`, `_prepare` của `seo_app/storage/drafts.py`, `plan_cache.py`, `site_index.py` |
| Báo cáo đã đọc | [Thợ Máy](T-117-tho-may.md) (`f397466`, Opus 5.5), [Soi Lỗi](T-117-soi-loi.md) (`8c0190d`, Opus 5.5: ĐẠT CÓ ĐIỀU KIỆN, 1 Thấp có từ trước SL-T117-1) |
| Máy | Windows 11 Pro 10.0.26300, Python 3.12.15, uv 0.13.4 (đạt ngưỡng `uvx`, LC-T078-1). Tài khoản thường: tạo được junction và hard link, **không** tạo được symlink (như nhóm 1). Ổ C: có tên 8.3, ổ D: không. Máy đang chạy toàn bộ test trên `main` nên chỉ chạy test chọn lọc |
| Ngày | 2026-11-02 (18:05–18:23, giờ máy +07) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **0 Thấp mới** của Lá Chắn. **LC-T116-1 đóng.** SL-T117-1 (Thấp, có từ trước, của Soi Lỗi): đồng ý mức, **không chặn**. **Gộp vào `main` được ngay**; điều kiện chỉ là lập phiếu dọn nhỏ và một dòng sổ rủi ro |

## Tóm tắt (cho chủ dự án)

- **An toàn, gộp được.** Lỗi nhỏ tôi tìm ra ở lượt kiểm Fable sáng nay (nếu thư mục `data` cạnh phần mềm bị ai đó đổi thành «lối tắt» trỏ đi nơi khác thì ảnh xem trước và thẻ ảnh sửa tay bị ghi sang nơi đó) **đã được sửa đúng ý**: nay phần mềm kiểm từng tầng thư mục trước **mỗi lần** đọc hay ghi. Gặp lối tắt thì ảnh xem trước vẫn hiện (chỉ không lưu lại), thẻ sửa tay không được lưu và phần mềm báo một câu cố định, không in đường dẫn máy.
- **Tôi tự thử lại từ đầu**, không chỉ đọc báo cáo của Thợ Máy và Soi Lỗi: lối tắt trỏ sang **ổ đĩa khác** theo cả hai chiều (D: → C: và C: → D:), lối tắt **treo** (nơi nó trỏ tới đã bị xóa), đường dẫn viết bằng **tên ngắn 8.3** của Windows, **hard link** ở chính file cache, **tráo đúng khoảnh khắc** giữa lúc kiểm và lúc ghi, lỗi quyền khi kiểm. Trong mọi ca phần mềm **không ghi gì ra ngoài** thư mục của nó, không bị lỗi trang, câu báo không lộ đường dẫn. (Một chi tiết: tôi đo được khe «tráo đúng khoảnh khắc» là có thật nhưng cực hẹp và chỉ ai đã có quyền chạy chương trình trên máy bạn mới dùng được; người đó sửa thẳng được phần mềm nên khe này không cho thêm quyền gì. Không tính là lỗi, chỉ ghi sổ rủi ro.)
- **Còn một việc nhỏ, có từ trước (mức Thấp, Soi Lỗi ghi SL-T117-1):** ba kho khác cũng nằm trong `data` (bài nháp, cache kế hoạch, danh sách bài đã đăng) chưa có lớp kiểm này. Nên làm ở một phiếu dọn nhỏ sau khi gộp T-117, không cần chờ.

## Trả lời câu hỏi của Chỉ Huy (18:05)

| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | LC-T116-1 đóng? | **Đóng.** Hai test `xfail(strict=True)` tôi viết ở T-116 nhóm 1 nay qua thật; Thợ Máy chỉ xóa 2 khối dấu, không đổi thân test (R5, tôi đối chiếu diff). Tự thử lại độc lập bằng junction thật ở `data` và ở `data/image_previews`: 0 file đi qua liên kết, kho thẻ từ chối đúng câu cố định (bảng «Thử độc lập», ca A–D) |
| 2 | Còn khe nào? | **Junction tạo giữa chừng:** còn, đúng như Thợ Máy và Soi Lỗi ghi; tôi đo thêm độ rộng khe và kết luận **không phải lỗi mới** (mục «Khe còn lại»). **Hard link:** ở tầng thư mục không có khe (NTFS lẫn POSIX không cho hard link thư mục); ở chính file cache: ghi **không xuyên** (file tạm rồi `os.replace` thay chỗ, file ngoài nguyên vẹn), đọc **có xuyên** (cache trả nội dung file ngoài nếu là JPEG sạch) nhưng không thêm quyền gì cho kẻ đặt (ghi nhận GN-2, đồng ý Soi Lỗi). **Ổ khác:** chặn cả hai chiều; `lstat` không đi theo liên kết nên ổ đích không liên quan. **8.3:** chặn với gốc ngắn, thư mục ngắn, hay trộn hai dạng. **Junction treo:** chặn, app không tạo lại thư mục đích, không nổ. **Không kiểm được** (`lstat` lỗi quyền): cache không dùng, kho thẻ báo câu không có đường dẫn |
| 3 | Câu báo không lộ đường dẫn? | **Đúng.** `MSG_DATA_DIR_LINK` là hằng, không có ký tự `\`, không có ổ đĩa, không chèn gì (`data_dir.py`); nơi hiện ghép vào câu «Chưa lưu được dấu «ảnh AI» trên máy này: … Trong lần làm việc này app vẫn coi ảnh là ảnh AI.» (`write.py:1257-1261`). Nhánh lỗi hệ thống của `_prepare` chỉ chèn `exc.strerror` (chữ lỗi của hệ điều hành, không có tên file): thử ép `lstat` lỗi quyền → «Không tạo được file lưu thẻ ảnh (Permission denied).». `repr(PreviewCache)` không in đường dẫn. `resolve()` trả `error` kèm thẻ theo tên thư mục, trang không lỗi |
| 4 | Mở rộng hàm cho `plan_cache`/`site_index` ở phiếu nào? | **Một phiếu dọn nhỏ riêng, lập sau khi T-117 gộp `main`** (gợi ý tên «Dọn kho dữ liệu phụ», như tôi đề ở T-116 nhóm 4), Thợ Máy, mức Thấp: cả **ba** kho (nháp trước, vì giữ bài chưa gửi), dùng chung `dir_has_link(self.path.parent, PROJECT_ROOT)` ở đầu `_prepare` và **giữ** phép kiểm hard link ở chính file như kho thẻ; gỡ 3 `xfail` SL-T117-1 khi XPASS; gom luôn Đề xuất 2–3 của Thợ Máy (giao diện báo khi cache bị bỏ qua, README) và dòng sổ rủi ro mục «Khe còn lại». **Không gom vào T-118** đang chạy: nhánh `team/T-118` rẽ từ `935d381`, chưa có `data_dir.py`, và Thợ Máy đã làm từ 13:20; nếu Chỉ Huy vẫn muốn gom thì phải gộp `main` (sau T-117) vào `team/T-118` trước, vì T-118 cũng đang sửa `plan_cache.py`, `site_index.py` (LC-T113-2) |
| 5 | Gộp thử với `origin/main` `7485b94`? | `git merge-tree --write-tree 7485b94 HEAD`: **không xung đột** (cây `b51b52b`). Từ `731a46e`, `main` đổi 9 file mã (`app/views/write.py`, `plan.py`, `wordpress.py`, `home.py`, `scripts/hash_password.py`, `seo_app/env_file.py`, `plan/sync.py`, `plan/website.py`, `wordpress/client.py`) — không file nào của T-117, không đụng `folders.py`, `config.py` mà `data_dir` nhập; `uv.lock`, `pyproject.toml` không đổi ở cả hai phía. Vì `write.py` (nơi dùng cache và kho thẻ) có đổi, tôi gộp thật trên cây tạm (commit treo `c042320`, worktree tạm ngoài repo, không đẩy; test `test_zz_la_chan_where` xác nhận `seo_app` và `app` nạp từ chính cây tạm) và chạy 8 file test: **845 qua, 1 bỏ qua (Windows, có từ trước), 3 xfail (= SL-T117-1), 0 hỏng, 0 XPASS**, 5 phút 10. (Ca kiểm vị trí nạp mã của tôi hỏng ở lượt đầu vì `app` là gói không có `__init__.py` nên `__file__` là `None` — lỗi của test phụ; sửa rồi chạy riêng: qua, in đúng đường dẫn cây tạm cho `seo_app`, `data_dir`, `app/views/write.py`.) Worktree tạm đã gỡ |

Trước khi dùng `uvx` tôi đã kiểm `uv --version`: `uv 0.13.4` (LC-T078-1).

## Lỗi phát hiện

Không có lỗi mới của Lá Chắn. Đánh giá lỗi và ghi nhận của Soi Lỗi ở hai mục dưới.

## Đối chiếu với báo cáo Soi Lỗi và Thợ Máy (Opus 5.5)

| Mã | Mức Opus | Kết luận Fable | Bằng chứng |
|---|---|---|---|
| SL-T117-1 (3 kho khác ghi xuyên khi `data/` là liên kết) | Thấp, có từ trước | **giữ** | Tự thử: junction `data` → thư mục ngoài, `DraftStore.save`, `PlanCacheStore.save`, `SiteIndexStore.save` mỗi kho tạo đúng 1 file `.sqlite` ở thư mục ngoài (ca H). Đọc mã: `drafts._prepare` không kiểm liên kết ở tầng nào; `plan_cache`/`site_index._prepare` chỉ `self.path.is_symlink()` ở chính file (bắt được symlink file nếu kẻ tạo được; junction không thể là file; **không xét thư mục cha, không bắt hard link ở file**). Điều kiện như LC-T116-1 (phải ghi được vào thư mục cài app) nên Thấp là đúng. 3 `xfail(strict=True)` XFAIL trên nhánh và trên cây gộp. Ngoài phạm vi T-117 (phiếu chỉ cho sửa hai nơi), không chặn |
| GN-1 (khe giữa lần kiểm và lần ghi) | ghi nhận | **giữ** (ghi nhận, không lập lỗi) | Mục «Khe còn lại» |
| GN-2 (`data_dir.is_link` không coi hard link là liên kết; kho thẻ thì có) | ghi nhận | **giữ** | Ca E: ghi không xuyên, đọc xuyên; không thêm quyền. Nhắc ở phiếu mở rộng: kho SQLite giữ phép kiểm hard link ở chính file |
| GN-3 (người dùng cố ý dời `data` bằng lối tắt thì mất cache lặng lẽ, thẻ có câu báo) | ghi nhận | **giữ** | Đúng chủ ý F1; README chưa nói (Đề xuất 3 Thợ Máy → phiếu dọn) |
| Thợ Máy: đặt hàm chung ở `seo_app/images/` thay vì `storage/` | quyết định thiết kế | **đồng ý** | `data_dir` chỉ nhập `folders._is_link_stat` (cùng định nghĩa «liên kết» với lớp đọc ảnh T-048/T-079: symlink; trên Windows mọi reparse point có bit «name surrogate» `0x20000000`); `process.py` không kéo `seo_app.storage` (Thợ Máy đo ~1,9 s); `image_tags.py` vốn đã nhập từ `seo_app.images`; không vòng nhập |

## Khe còn lại (không phải lỗi mới)

| Khe | Thực tế đo được | Vì sao không lập lỗi |
|---|---|---|
| **Liên kết đặt vào đúng khoảnh khắc** sau lần kiểm, trước lần ghi (GN-1) | Ca F: tráo `data` thành junction ngay trong khe (sau `_no_link`, trước `_write`) → **1 file** `<băm>.jpg` đi qua; lần gọi kế tiếp kiểm lại và bị chặn. Với kho thẻ, khe tương tự giữa `dir_has_link` và `mkdir` + `sqlite3.connect` (Soi Lỗi đã thử). **Trên Windows khe hẹp hơn nữa:** tôi thử đổi tên thư mục đang có file mở bên trong → `PermissionError` (WinError 5); nghĩa là từ lúc `mkstemp` mở file tạm tới lúc đóng, không tráo được `data`; sau khi đóng mà tráo thì `os.replace` không tìm thấy file tạm qua liên kết → `OSError` được nuốt, app **không** ghi gì ra ngoài. Khe thật chỉ là vài micro-giây giữa `_no_link` và `mkdir`/`mkstemp` (cache) hay giữa `dir_has_link` và `mkdir`/`connect` (kho thẻ) | Muốn lợi dụng phải **chạy được chương trình trên máy** và **ghi được vào thư mục cài app** đúng khoảnh khắc; kẻ đó sửa thẳng được mã `.py` của app, nên khe này không cho thêm quyền gì. Hậu quả tối đa nếu lọt: một ảnh xem trước 320 px không metadata, hoặc file thẻ sửa tay (tên thư mục, thẻ) nằm ở nơi kẻ đó chọn. Cùng lớp «phải chiếm máy trước» đã có trong sổ rủi ro; SQLite chỉ mở theo đường dẫn nên không đóng được khe bằng handle như T-079. **Đề nghị:** một dòng ở sổ rủi ro (`security.md` §6), không sửa mã |
| **Hard link ở chính file cache** (GN-2) | Ca E: hard link `<băm>.jpg` → file JPEG ngoài: cache **đọc** và trả nội dung file ngoài (chỉ khi là JPEG sạch, ≤ cỡ và ≤ cạnh tối đa); hard link → file chữ: cache dựng lại ảnh thật và **ghi thay chỗ** (tmp + `os.replace`), file ngoài nguyên vẹn, `st_nlink` về 1 | Hard link cần quyền ghi vào `data/image_previews` **và** (Windows từ 10 1709, Linux `protected_hardlinks`) quyền ghi file đích; ai có vậy thì chép thẳng một JPEG vào cache cũng được. Ảnh xem trước chỉ hiện ở lưới chọn; ảnh đã chọn và byte gửi web dựng từ file thật (`write.py`, T-089). Kho thẻ vẫn gỡ hard link ở chính file (`image_tags._is_link`, `st_nlink > 1`) |
| **Gốc dự án và các tầng trên gốc không xét** | Có chủ ý (test `test_root_reached_through_a_link_is_not_flagged`): app cài dưới một lối tắt hợp lệ của máy vẫn chạy | Kẻ tráo được cả thư mục cài app thì đã đổi được mã app. `PROJECT_ROOT` là `Path(__file__).resolve()` nên mọi đường dẫn `data/…` dựng từ đường thật |
| **Nhánh «thư mục ngoài gốc»** của `dir_has_link` chỉ xét thư mục và thư mục cha | Chỉ xảy ra trong test (kho trỏ sang thư mục tạm) | App luôn dùng `PROJECT_ROOT / "data" / …`. Lưu ý cho phiếu mở rộng: `os.path.abspath` rút gọn `..` theo chữ, nên chỉ truyền đường dẫn hằng từ `PROJECT_ROOT` (không `..`), như hiện nay |
| `_cache_dir_is_ignored` vẫn `resolve()` thư mục cache (không đổi) | Với `data` là liên kết ra ngoài: `enabled = True` (git không thấy) nhưng `_no_link` chặn mỗi lần → ca A–D đều `enabled=True`, 0 file | Không còn đường ghi; có thể dọn cùng phiếu mở rộng (tùy chọn) |

## Thử độc lập (`probe_t117.py`, thư mục tạm, không mạng)

Chạy bằng `uv run python -X utf8` từ worktree (`seo_app` nạp từ `wt-T-117`). Thư mục tạm: scratchpad trên C: và `build/probe-t117` trên D: (bị `.gitignore`), tự dọn; `git status` sạch sau khi chạy.

| Ca | Tình huống | Kết quả |
|---|---|---|
| A | Dự án trên D:, junction `data` (và riêng `data/image_previews`) → thư mục trên **C:** | `dir_has_link` = True; 3 lần `get` (2 ảnh) đều trả JPEG; 0 file ở đích (`enabled=True`); kho thẻ từ chối đúng `MSG_DATA_DIR_LINK`, câu không chứa đường dẫn; `resolve` trả câu cố định; thư mục đích không bị gỡ |
| B | Dự án trên C:, junction → thư mục trên **D:** | Như A |
| C | Junction **treo** (xóa thư mục đích sau khi tạo) | `is_link` = True, `dir_has_link` = True; dựng `PreviewCache` sau khi treo không nổ; ảnh có; kho thẻ từ chối; **không tạo lại** thư mục đích |
| D | **8.3** trên C: (`GetShortPathNameW` của thư mục dự án tên dài có dấu) | Gốc ngắn + thư mục ngắn, gốc dài + thư mục ngắn, gốc ngắn + thư mục dài: đều bắt được; cache và kho thẻ qua gốc 8.3: 0 file ở đích, kho từ chối |
| E | **Hard link** ở chính file cache | Xem «Khe còn lại» (ghi không xuyên; đọc xuyên: ghi nhận) |
| F | **Tráo đúng khe** kiểm→ghi | 1 file đi qua (giới hạn thiết kế); lần sau bị chặn |
| G | Câu báo; `lstat` lỗi quyền | `MSG_DATA_DIR_LINK` không có `\`, ổ đĩa; kho thẻ báo «Không tạo được file lưu thẻ ảnh (Permission denied).», không tạo file; cache không ghi, ảnh vẫn có |
| H | 3 kho khác với junction `data` | Mỗi kho ghi 1 file `.sqlite` ra ngoài → xác nhận SL-T117-1 |

Tổng: **56 PASS / 0 FAIL thật / 5 INFO** (E.read, F.window, H ×3). Probe báo 4 «FAIL» ở ca A, B tầng `data/image_previews` là **lỗi của probe**: junction ở `data/image_previews` không nằm trên đường tới `data/image_tags.sqlite`, nên kho thẻ **đúng** là không từ chối (kiểm «0 file ở đích» vẫn qua) — tôi đặt kỳ vọng sai cho ca đó, không phải lỗi app.

## Đọc mã (ngoài probe)

- `dir_has_link`: đi từ ngay dưới gốc xuống, `os.lstat` từng tầng, dùng `_is_link_stat` của lớp đọc ảnh; tầng chưa có thì dừng (app sẽ tạo thư mục thường); dùng `abspath` chứ không `resolve` (đúng: `resolve` đi theo liên kết và làm mất dấu). `is_link` bắt `FileNotFoundError`/`NotADirectoryError` → `False`; lỗi khác để caller quyết.
- `PreviewCache._no_link` kiểm **hai lần** mỗi `get` (trước đọc, trước ghi, vì `make_preview` tốn thời gian) và `except OSError → False` (đóng an toàn); Soi Lỗi đã thêm test ghim nhánh này. Đối tượng sống suốt phiên (`st.cache_resource`, `write.py:893-897`) nên kiểm mỗi lần là bắt buộc — đã làm.
- `ImageTagStore._prepare` kiểm **trước** `_remove_links`, `mkdir`, `sqlite3.connect`; đặt `_ready = False` để lần sau kiểm lại từ đầu; **không tự gỡ** liên kết thư mục (có thể là của người dùng) — đúng F1 (chỉ gỡ ở chính file như trước, SL-T052-7/-8 giữ nguyên). Thay lối tắt bằng thư mục thường thì dùng lại ngay (test Thợ Máy).
- Không đổi: cách băm tên file cache, kiểm khuôn JPEG khi đọc, giới hạn cỡ, EXIF/GPS, phần đọc ảnh của `folders.py`, `app/**`.
- Mac/Linux: nhánh symlink chỉ **giả lập** (`lstat` trả `S_IFLNK`), như Thợ Máy/Soi Lỗi ghi; máy này không tạo được symlink. Điều kiện cũ «chạy test trên Mac thật» vẫn mở.

## Danh sách kiểm tra (rút gọn theo phiếu: F1, F3; thêm U2, D1–D3)

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| F1 | Đạt | Hai nơi ghi không còn ghi/đọc qua liên kết ở tầng thư mục hay ở chính file (ca A–D, G); khe GN-1 ghi sổ rủi ro |
| F2 | Không áp dụng | Không đổi giới hạn ảnh, EXIF, GPS |
| F3 | Đạt | Không `eval`/`pickle`; `.gitignore` đọc như cũ; test ghi file bằng `encoding="utf-8"` |
| U2 | Đạt | Câu báo cố định, không đường dẫn; `strerror` không có tên file; `repr` không in đường dẫn |
| D1 | Đạt | Không thư viện mới; `uv.lock`/`pyproject.toml` không đổi (so `731a46e` và so `7485b94`) → kết quả pip-audit sáng 02/11 (69 gói, 0 lỗ hổng) còn hiệu lực |
| D2 | Đạt | `.gitignore:22` vẫn `data/`; `build/` (`:14`) che thư mục probe |
| D3 | Đạt | Test mới chỉ dùng `tmp_path`, junction (`_winapi.CreateJunction`), `lstat` giả; bộ chặn mạng của `conftest` vẫn chạy |
| S1–S3, W1–W4, A1–A3, U1, U3 | Không áp dụng | Phiếu không đụng bí mật, WordPress, AI, đăng nhập |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | Dùng lại kết quả sáng 02/11 (nhóm 1): 69 gói, **0 lỗ hổng** (`uv export` → `uvx pip-audit -r … --no-deps --disable-pip`); lock không đổi | ✔ |
| bandit (`PYTHONUTF8=1`) | 1 Medium **B608** `seo_app/storage/image_tags.py:129` — báo nhầm (SQL hằng, đã loại ở nhóm 1); `data_dir.py`, `process.py`: 0 | ✔ |
| detect-secrets (`PYTHONUTF8=1`) | 0 trên 5 file mã/test + 2 báo cáo | ✔ |
| Soát lịch sử git `3669046..8c0190d` | 0 khóa, 0 mã băm thật | ✔ |
| ruff | `ruff check` + `ruff format --check`: sạch | ✔ |
| pytest chọn lọc trên `team/T-117` (10 file: `test_t117_data_dir_links`, `test_la_chan_t116_nhom1`, `test_soi_loi_t117`, `test_images_process`, `test_images_tags`, `test_soi_loi_t052`, `test_la_chan_t074`, `test_soi_loi_t074`, `test_app_images`, `test_drafts_images`) | **1194 qua / 3 bỏ qua (Windows, có từ trước) / 3 xfail (= SL-T117-1) / 0 hỏng / 0 XPASS**, 9 phút 55 | ✔ |
| pytest trên cây gộp `team/T-117` + `origin/main` `7485b94` (`test_t117_data_dir_links`, `test_soi_loi_t117`, `test_la_chan_t116_nhom1`, `test_app_images`, `test_t110_gan_anh_vao_bai_nhap`, `test_images_process`, `test_images_tags` + ca kiểm vị trí nạp mã) | **845 qua / 1 bỏ qua / 3 xfail (= SL-T117-1) / 0 hỏng / 0 XPASS**, 5 phút 10; `seo_app`, `app` nạp từ chính cây tạm | ✔ |

## Báo nhầm đã loại

- bandit B608 `image_tags.py:129`: câu SQL ghép từ hằng trong module, không có dữ liệu ngoài (đã loại ở T-116 nhóm 1).
- Probe ca A/B tầng `data/image_previews` báo «kho thẻ không từ chối»: kỳ vọng của probe sai (xem «Thử độc lập»).
- Ca kiểm vị trí nạp mã trên cây gộp hỏng lần đầu (`TypeError` vì `app.__file__` là `None`, gói namespace): lỗi của test phụ tôi viết, không phải của app; sửa và chạy lại: qua.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

Không điều kiện nào chặn gộp `main`.

1. **Lập phiếu dọn nhỏ «Dọn kho dữ liệu phụ»** (Thợ Máy, Thấp) **sau khi T-117 gộp**: SL-T117-1 cho cả ba kho (`drafts.py` trước, rồi `plan_cache.py`, `site_index.py`) dùng `dir_has_link(self.path.parent, PROJECT_ROOT)` ở đầu `_prepare`, giữ phép kiểm hard link ở chính file; gỡ 3 `xfail` khi XPASS (chỉ xóa dấu, R5); gom Đề xuất 2 (Họa Sĩ, tùy chọn) và 3 (README, Thư Ký) của Thợ Máy. Nếu Chỉ Huy gom vào T-118 thì gộp `main` (có T-117) vào `team/T-118` trước.
2. **Sổ rủi ro** (`docs/team/security.md` §6, Thư Ký hoặc Chỉ Huy): một dòng cho khe «liên kết đặt vào đúng khoảnh khắc giữa lần kiểm và lần ghi vào `data/`» (lớp «phải chiếm máy trước»).
3. Điều kiện cũ còn mở, không thuộc phiếu này: chạy test trên Mac thật (ca symlink thật của `test_t117_data_dir_links.py` khi đó tự chạy bằng `os.symlink`).

## Tệp và cách chạy lại

- Probe: `C:\Users\ADMIN\AppData\Local\Temp\claude\D--ProMetal-ToolSEO\42f61352-e440-426b-832a-72b79f8aff54\scratchpad\probe_t117.py` (thư mục tạm của phiên, không commit). Chạy từ worktree: `PYTHONUTF8=1 uv run python -X utf8 <đường dẫn probe>`; tự dọn thư mục tạm và `build/probe-t117`.
- Ghi chú bàn giao: thư mục ghi chú chung của phiên, file `T-116-la-chan-nhom-1.md` (mục T-117).

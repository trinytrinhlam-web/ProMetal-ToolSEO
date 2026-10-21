# Biên bản bảo mật T-077 · Dọn thẻ ảnh nhỏ (sau T-074): tên công cụ AI gõ khác dạng chuẩn · rút gọn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) |
| Phiếu được kiểm | [T-077](../tickets/T-077-don-the-anh-ten-cong-cu-ai.md) |
| Phạm vi | Rút gọn (A3; yêu cầu bảo mật riêng A3, F1, F3). Diff `378f710...team/T-077` (gốc `378f710`, đầu nhánh lúc kiểm `0cbd4f3`; code ứng dụng đổi ở `c8c6351`, sau đó chỉ có test và báo cáo): `seo_app/images/tags.py` (+21/−8), `seo_app/storage/image_tags.py` (+25/−18), `tests/test_images_tags.py` (+192), `tests/test_soi_loi_t077.py` (mới, +173), `tests/test_soi_loi_t074.py` (−23, chỉ gỡ `xfail`), `tests/test_la_chan_t074.py` (−8, chỉ gỡ `xfail`), 2 báo cáo. `origin/main` lúc kiểm `d9e279f` (đã có T-055, T-075) |
| Ngày | 2026-10-21 (13:58–14:42 +07) |
| **Kết luận** | **ĐẠT**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp. **LC-T074-1 (gồm SL-T074-2) đóng**, SL-T074-1 đóng; LC-T070-2 vẫn giữ. Gộp `main` được ngay |

## Tóm tắt (cho chủ dự án)

Lỗi nhỏ tôi tìm ra ở T-074 đã được vá đúng cách tôi đề xuất: thư mục hay file ảnh AI đặt tên công cụ kiểu "MidJourney", "Mid Journey", "Co-Pilot", "See Dream" nay là **ảnh AI** (không còn mang mã công trình, khu vực của công trình thật). Tôi so bản sửa với bản cũ trên gần 300.000 tên: **không tên nào** đang là ảnh AI bị chuyển thành ảnh thật, và tên ảnh thật nào vẫn là ảnh thật thì thẻ giữ y nguyên.

Phần đọc thẻ sửa tay đổi thứ tự (đọc file xong mới kiểm từng thẻ) để tab khác lưu thẻ không phải chờ lâu. Tôi thử cho một chương trình lạ chen vào **giữa** lúc app đang đọc: app vẫn đọc trọn một bản đã kiểm, không lẫn dữ liệu chen vào; thay đổi lạ bị bắt ở lần sau và file lạ được cất sang một bên. Sau khi đọc xong, app không đụng thêm vào file.

Không có lỗi mới. Gộp vào `main` không xung đột, test liên quan chạy qua trên bản gộp. Hôm nay giao diện chưa thấy gì khác (màn hình chọn ảnh T-056 chưa làm).

## Lỗi phát hiện

Không phát hiện lỗi.

## Kiểm lại lỗi cũ và các mục phiếu giao

Số dòng theo `0cbd4f3`.

| Mã / việc | Kết quả | Bằng chứng |
|---|---|---|
| LC-T074-1 (gồm SL-T074-2) · tên công cụ gõ khác dạng chuẩn | **Đóng** | Đúng cách sửa tôi đề xuất ở T-074: `_parse_dir_name` đọc dấu hiệu theo cả hai cách (`seo_app/images/tags.py:867`), thêm đúng 4 tên tách đôi (`:246-249`). **E1:** bản nhánh tương đương bản sửa thử T6 của tôi: cùng `_AI_MARKERS`, cùng từ điển, các hàm liên quan cùng thân (chỉ khác `_parse_dir_name` đặt biến `ai` trước). **T5a dựng lại trên nhánh:** 12 tên viết hoa giữa chữ ("MidJourney", "FireFly", "CoPilot", "SeeDream", "ReCraft", "RunWay", "IdeoGram", "DreamIna", "HaiLuo", "JiMeng"…) và 6 tên tách đôi ("Mid Journey", "Mid-Journey", "Fire Fly", "Co Pilot", "Co-Pilot", "See Dream") đều là ảnh AI ở thư mục (CT, khu vực rỗng), thư mục gốc (`is_ai_name`) và tên file; bản `378f710` là ảnh thật. **T6 dựng lại:** 60.336 tên, nhánh so bản sửa thử: **0** tên đổi; nhánh so `378f710`: 40 tên thư mục, 25 tên file đổi (đúng số của T6 ở T-074), mọi tên đổi đều có cặp chữ tiếng Anh tương ứng, trừ "SoRa"; 112 tên thật kiểu Pro-Metal: 0 đổi |
| Không kéo lùi chiều ảnh AI → ảnh thật | **Đạt** | **E1 (chứng minh theo cấu trúc):** `_AI_MARKERS` cũ ⊆ mới (thêm đúng 4: "co pilot", "fire fly", "mid journey", "see dream"); từ điển: không khóa cũ nào đổi hay mất, chỉ thêm 4 khóa, cả 4 là mục AI và là dấu hiệu AI. `ai` chỉ được bật, không bao giờ tắt (`_DirTags.add`), nên cách đọc mới chỉ thêm ảnh AI. **E1 (thử vi phân)** 299.856 phép so (60.000 tên ngẫu nhiên có/không dấu, viết liền, hoa lẫn, chèn dấu hiệu AI, × thư mục cuối, thư mục đầu, tên file, thư mục gốc, ô "Nguồn ảnh" `match_source`): cũ AI → mới thật **0**; tên mới vẫn là ảnh thật mà thẻ khác bản cũ **0**; thật → AI 2.574 (hướng an toàn). **T5b:** 2.324 tên dựng từ mọi dấu hiệu trong 18 ngữ cảnh: AI → thật 0 |
| SL-T074-1 · `get_many` kiểm dòng sau khi đóng giao dịch | **Đóng** | `get_many` (`seo_app/storage/image_tags.py:255-288`): trong `with self._connect()` (`:269-277`) chỉ còn các câu `SELECT` và `fetchall()`; `_row_to_tag`, `tags_for_image` chạy ở `:278-287`. Đúng cách E3b của Soi Lỗi. E2: kẻ tấn công chờ khóa ở nhật ký thường vào được sau 0,37–0,42 s (bản `378f710`: 1,38–2,13 s) |
| LC-T070-2 vẫn giữ sau khi đổi `get_many` | **Giữ** | **T2 dựng lại** (script T-074, chép nguyên; 2 kiểu chen: sửa thẳng `sqlite_master` và `CREATE TRIGGER` thật) × 8 lối vào (`set`, `clear`, `clear_all`, `get`, `resolve_many`, `list_manual`, kho mới qua `set`/`get`) × nhật ký thường/WAL × không chờ/chờ khóa: nhánh **giống hệt** `378f710` ở cả 2 × 32 dòng (so sau khi bỏ số giây), không lần nào khu vực thành "Quận 1". **E2 (biến thể mới, nhắm đúng chỗ đổi):** 900 ảnh, 2 thư mục gốc, 4 câu `IN`; chương trình lạ chen vào ngay lúc câu đọc thứ hai bắt đầu (nhóm 1 đã đọc xong), (A) sửa mọi khu vực thành "Quận 1", (B) bỏ bảng `manual_tags` và dựng khung nhìn cùng tên trả "Quận 1"; `get_many` và `resolve_many` × nhật ký thường/WAL × không chờ/chờ: nhánh và `378f710` **cả 32 lần đọc ra đúng 900/900 "Quận 7"** (bản đã kiểm). Nhật ký thường không chờ: chen bị chặn ("locked"); chờ khóa: chỉ ghi được sau khi app xong; WAL: ghi được nhưng app vẫn đọc bản đã kiểm. Khi kiểu (B) ghi được (chờ khóa, WAL), nó bị bắt ở lần sau ("File lưu thẻ ảnh bị lỗi…"), lần sau nữa file lạ đổi tên, app dùng thẻ đọc từ tên thư mục. Đối chứng `da87dbf` (trước T-074, mỗi câu đọc một giao dịch): **16/16 lần đọc lẫn 400 "Quận 7" + 500 "Quận 1"**, kiểu (B) đọc cả từ khung nhìn lạ: phép thử nhạy, bắt được đúng lỗ cũ |
| Phần Python sau commit không đọc thêm gì từ file | **Đạt** | **E3:** ghi mọi sự kiện kiểm toán của Python (`open`, `sqlite3.connect`, `os.*`) và mọi lần gọi `os.stat`, `os.lstat`, `os.open`, `os.scandir`, `os.listdir`, theo dõi câu SQL bằng `set_trace_callback` (thấy cả `BEGIN`, `COMMIT`). `get_many(900)` + `resolve_many(200)`: trong `_connect` bộ ghi thấy 18 `os.stat`, 8 `os.lstat`, 2 `sqlite3.connect` (gỡ liên kết ở `_prepare` và mở file, như cũ); **sau khi đóng kết nối: 0** truy cập file/ổ đĩa, 0 câu SQL; 2 kết nối đều đã đóng; mọi câu `SELECT` (7) và `COMMIT` (2) chạy với `in_transaction = True`; `_row_to_tag` chạy khi giao dịch còn mở: nhánh **0** lần, `378f710` 1.100 lần. Dòng giữ trong bộ nhớ chỉ có `bytes` và `int` (đã đọc hết, không còn con trỏ tới file). `tags_for_image` chỉ xử lý chữ ("Không đọc ổ đĩa", `tags.py:942-954`) |
| Docstring chế độ WAL (`image_tags.py:14-25`, `_begin` `:566-572`) | **Đúng** | Khớp hành vi đo được ở T2, E2: nhật ký thường, chương trình khác phải chờ giao dịch của app xong mới ghi được; WAL, nó ghi được lúc app **đọc** nhưng lần đọc chỉ thấy bản đã kiểm, lần **ghi** của app giữ quyền ghi từ đầu; thay đổi chen vào bị bắt ở lần kiểm sau. Phần Thợ Máy sửa thêm ở `_begin` (ngoài dòng 19-21) chỉ là lời, đúng ý, đồng ý |
| Gỡ `xfail` | **Đúng** | `git diff 378f710 team/T-077 -- tests/test_la_chan_t074.py tests/test_soi_loi_t074.py`: chỉ có dòng xóa (3 dấu `xfail` + hằng `_REASON`; 3 khối `xfail`), không đổi `assert` hay tham số. 20 ca LC-T074-1 của tôi nay qua thật (trong 1.367 ca qua) |
| Gộp với `origin/main` (`d9e279f`, có T-055, T-075) | **Được ngay** | Xem mục công cụ: không xung đột; test liên quan + test nháp ảnh T-055 qua trên cây gộp. `drafts.py` mới của T-055 gọi `tags_for_image`, `resolve_many` (`_check_images`); vì thẻ đọc từ tên thư mục phân biệt hoa thường, nó lấy tên thật trên ổ trước khi đọc thẻ (`_FolderNames`, SL-T055-1), nên không phụ thuộc cặp tên khác hoa thường nào. T-077 thêm một cách đọc **không** phân biệt hoa thường (tên thư mục ít phụ thuộc hoa thường hơn trước); cặp thử của T-055 vẫn đúng: "CongAI" là ảnh AI, "congai" là ảnh thật |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets (`PYTHONUTF8=1`, `--all-files`, thư mục riêng có 8 file của diff lấy bằng `git show team/T-077:…`, patch nhánh `git log -p 378f710..team/T-077`, và 1 file mồi có chữ tiếng Việt): bắt **đủ 2/2 mồi**, **0 mục** ở file thật; đã xóa mồi. grep `security.md` mục 5 trên patch nhánh: 4 dòng (chữ "password = …", "Secret Keyword" trong 3 câu báo cáo tả cách quét mồi; `_tokens`). Không file nhị phân (`git diff --numstat`) |
| S2 | Đạt | Không câu lỗi mới; `get_many` vẫn chỉ ném `ImageTagStoreError` câu cố định từ `_connect` (`:411-436`); lỗi sau khi đóng kết nối (về lý thuyết, `_row_to_tag` chỉ xử lý chữ) không mang đường dẫn |
| S3 | Không áp dụng | Không biến cấu hình mới |
| W1 | Không áp dụng | Diff không có code WordPress |
| W2 | Không áp dụng | Như W1 |
| W3 | Không áp dụng | Không tạo HTML |
| W4 | Không áp dụng | Không gọi mạng |
| A1 | Không áp dụng | Diff không dựng prompt |
| A2 | Không áp dụng | Không gọi AI; ảnh thật/AI do code quyết (`tags.py:910-939`) |
| A3 | Đạt | Dấu hiệu mới chỉ bật `ai = True`; `is_ai_name` chỉ trả `bool` (`tags.py:973-986`); giá trị thẻ chỉ từ danh sách cố định (T5d: 20.000 đường dẫn ngẫu nhiên có chữ số lạ, đạt); ảnh AI không mang mã công trình, khu vực, trước/sau (`:933-937`). LC-T074-1 đóng (bảng trên) |
| U1 | Không áp dụng | Không có giao diện |
| U2 | Không áp dụng | Không có trang mới |
| U3 | Không áp dụng | Không đụng mật khẩu |
| F1 | Đạt | Không thêm đường dẫn mới; `get_many` không mở file nào ngoài kết nối đã có (E3: 0 truy cập sau khi đóng); gỡ liên kết ở mỗi lần mở không đổi (`_prepare`, `:438`). Test mới trỏ file thẻ sang thư mục tạm (`tests/test_soi_loi_t077.py:29-33` tự động, `:105` `tmp_path`; ca mới ở `tests/test_images_tags.py:2455` dùng fixture `store` như ca cũ) |
| F2 | Không áp dụng | Không đọc nội dung ảnh, không đụng EXIF/GPS |
| F3 | Đạt | Không `pickle`, `eval`, `exec`, `yaml`; SQL vẫn dùng tham số `?`, chuỗi f chỉ ghép hằng (`_SELECT`, dãy `?`). Mọi câu SQL vẫn chạy trong giao dịch đã kiểm cấu trúc (T2, E2, E3); `trusted_schema = OFF`, giới hạn số bước và độ dài không đổi (`_guard`, `:544-563`). Không đọc/ghi file chữ nên không cần `encoding=` |
| D1 | Đạt | `uv.lock`, `pyproject.toml` không đổi so với gốc; không import mới. pip-audit trên khóa của nhánh: 1 lỗ hổng `certifi 2026.7.22` (PYSEC-2026-4320) **có từ gốc `378f710`**, đã vá trên `main` ở T-075; T-077 không đụng `uv.lock` nên bản gộp dùng `certifi 2026.10.19` (cây gộp: pip-audit sạch, `certifi.__version__` = 2026.10.19) |
| D2 | Đạt | `.gitignore` không đổi (`data/`, `*.sqlite`) |
| D3 | Đạt | Bộ chặn mạng tự bật (`tests/conftest.py`); test mới không có `requests`, `urllib`, `socket`, `http` |

## Kết quả công cụ quét

Máy Windows 11 Pro (10.0.26300) của chủ dự án, Python 3.12.15, SQLite 3.53.1, `uv` 0.13.4, worktree `wt-T-077`, nhánh `team/T-077` tại `0cbd4f3`. Máy đang chạy song song các agent khác.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit 2.10.1 | `uv export --frozen --no-hashes --no-emit-project` (69 gói) → `uvx pip-audit -r … --no-deps --disable-pip`. Nhánh: 1 lỗ hổng `certifi 2026.7.22` PYSEC-2026-4320 (sửa ở 2026.10.19). Khóa của `origin/main` `d9e279f`: **không có lỗ hổng** | Có. Có từ gốc, không do T-077 (D1) |
| bandit 1.9.4 | `tags.py` + `image_tags.py` (1.426 dòng): 1 mục B608 (Medium, độ tin Low) ở `image_tags.py:128`, như T-074 (lệch 4 dòng). 4 file test của phiếu (bỏ B101): B608 ×11, B311 ×2, đều là mục cũ lệch dòng; `tests/test_soi_loi_t077.py`, `tests/test_la_chan_t074.py`: 0 | Có. Báo nhầm (mục dưới) |
| detect-secrets 1.5.0 | **`PYTHONUTF8=1`**, `--all-files` trong thư mục riêng (8 file diff, patch nhánh, 1 file mồi có chữ tiếng Việt: khóa AWS giả, `password = …`): bắt **đủ 2 mồi, 0 mục khác**. Đã xóa mồi | Có. Mồi bị bắt nên file tiếng Việt thật sự được đọc (LC-T049-4) |
| Soát lịch sử git | `git log -p 378f710..team/T-077 \| grep -inE "api[_-]?key\|password\|secret\|token"`: 4 dòng (3 câu báo cáo tả cách quét mồi, 1 `_tokens`) | Có, đọc từng dòng |
| ruff | `uv run ruff check .`: **All checks passed!** | Có |
| pytest (nhánh) | `uv run pytest tests/test_images_tags.py tests/test_soi_loi_t052.py tests/test_soi_loi_t070.py tests/test_soi_loi_t074.py tests/test_la_chan_t074.py tests/test_soi_loi_t077.py tests/test_images_folders.py tests/test_ai_images.py -q -p no:cacheprovider -rsx` (14:02–14:04): **1367 passed, 8 skipped, 7 xfailed, 0 hỏng** | Có. Khớp số của Soi Lỗi. 8 bỏ qua: 2 ca symlink của T-052 (Windows chưa bật Developer Mode), 6 ca T-048 (chỉ Mac/Linux hay cần symlink). 7 xfail: SL-T070-4 (đã hoãn, ngoài phiếu) |
| Gộp với `main` | `git merge-tree --write-tree origin/main team/T-077` (`origin/main` = `d9e279f`) → cây `75dfd9d`, **không xung đột** (exit 0). Dựng cây gộp bằng `git archive` vào thư mục nháp, `uv sync --frozen` theo `uv.lock` của cây gộp; 8 file test trên + `tests/test_drafts_images.py`, `tests/test_soi_loi_t055.py`, `tests/test_storage_drafts.py`, `tests/test_app_drafts.py` (T-055 dùng thẻ ảnh), 14:35–14:39: **1725 passed, 9 skipped, 11 xfailed, 0 hỏng** (= 1367 của 8 file trên + 358 của 4 file nháp; thêm 1 bỏ qua symlink chỉ Mac/Linux `tests/test_drafts_images.py:633`, 4 xfail SL-T055-4, -5 đã có từ T-055) | Có: `seo_app` và `drafts.py` nạp từ đúng thư mục cây gộp (in `__file__`), `certifi` 2026.10.19. `main` đổi từ gốc không trùng file nào của T-077 |

**Chưa chạy được (không ghi là đạt):** ca symlink (Windows này lỗi 1314; điều kiện T-063 vẫn giữ). Không chạy toàn bộ pytest (theo `rules.md`, Chỉ Huy chạy khi gộp). Chưa thử trên Mac (thay đổi chỉ ở phần xử lý chữ và thứ tự đọc/xử lý trong `get_many`, không đụng đường dẫn hay file).

## Báo nhầm đã loại

- **bandit B608 `image_tags.py:128`** (`_oversized_sql`): chỉ gọi lúc nạp module với tên bảng, tên cột hằng; giá trị so dùng tham số `?1`. Không đổi từ T-074.
- **bandit B608 trong test** (`tests/test_images_tags.py:1924`, `:1934`, `:1938`, `:1943`, `:1946`, `:1950`, `:1954`, `:2177`; `tests/test_soi_loi_t074.py:96`, `:100`, `:107`): đúng các mục T-074 đã loại (lệch dòng vì thêm test), dựng file SQLite độc bằng chuỗi f ghép hằng trong test.
- **bandit B311** (`tests/test_images_tags.py:1333`, `:1355`): `random.Random(hạt giống cố định)` sinh tên thử, không dùng cho mật mã.
- **detect-secrets**: 2 mục duy nhất là chuỗi mồi tôi tự đặt.

## Thử độc lập của Lá Chắn

Script nằm ngoài repo (thư mục nháp của phiên, bản sao ở thư mục ghi chú chung `T-077-la-chan-scripts/`), không sửa code ứng dụng; chạy bằng `.venv` của worktree (`PYTHONUTF8=1 uv run python <script> <đối số>`), mọi file SQLite trong thư mục nháp. Bản cũ nạp từ `git show 378f710:…`, `git show da87dbf:…`; bản sửa thử T6 dựng lại từ `T6_ban-sua-thu_LC-T074-1.diff` (T-074) áp lên `tags.py` bản `378f710`.

| # | Thử gì | Kết quả |
|---|---|---|
| E1 | Nhánh có tương đương bản sửa thử T6 của tôi không; chỉ thêm không bớt; thử vi phân 299.856 phép so với `378f710` | Tương đương; `_AI_MARKERS` cũ ⊆ mới (+4), từ điển chỉ thêm 4 khóa AI; AI → thật 0; ảnh thật đổi thẻ 0 |
| T5 | Dựng lại T5 (a)–(d) của T-074 trên nhánh, đối chứng `378f710` | (a) 18 tên LC-T074-1 là ảnh AI ở thư mục, gốc, tên file; (b) AI → thật 0 / 2.324; (c) 112 tên thật: 0 đổi; (d) A3 đạt |
| T6 | Dựng lại T6 của T-074: 60.336 tên, nhánh so bản sửa thử và so `378f710` | So bản sửa thử: 0 đổi. So `378f710`: 40 thư mục, 25 tên file đổi sang AI, chỉ tên có cặp chữ tiếng Anh tương ứng và "SoRa" |
| T2 | Dựng lại T2 của T-074 (2 kiểu chen × 8 lối vào × 2 chế độ nhật ký × chờ/không chờ) trên nhánh, đối chứng `378f710` | Giống hệt bản `378f710` ở 2 × 32 dòng; không lần nào trigger chạy trong thao tác |
| E2 | **Mới:** chen giữa các câu đọc của một lần `get_many`/`resolve_many` 4 nhóm: sửa dữ liệu, thay bảng bằng khung nhìn; nhánh, `378f710`, `da87dbf` | Nhánh và `378f710`: 32/32 lần đọc ra đúng bản đã kiểm (900 "Quận 7"), thay đổi cấu trúc bị bắt lần sau, file lạ đổi tên. `da87dbf`: 16/16 lần đọc lẫn hai bản |
| E3 | **Mới:** sau khi đóng kết nối, `get_many` có đọc file, chạy SQL không; dòng giữ lại kiểu gì; giới hạn số dòng | 0 truy cập file, 0 câu SQL sau khi đóng; dòng chỉ `bytes`, `int`; 30 bước máy ảo mỗi dòng → tối đa ≈ 1,66 triệu dòng mỗi kết nối (mục Ghi nhận) |

## Ghi nhận (không thành lỗi)

- **Kiểu gõ tách khác vẫn là ảnh thật** (Thợ Máy đã ghi): "Run Way", "Re Craft", "Ideo Gram", "Hai Luo", "Ji Meng", "Dream Ina", "Leo Nardo" ở thư mục, tên file, thư mục gốc (tôi thử lại: đúng vậy). Hướng không an toàn nhưng hiếm (tên hãng vốn viết liền, ít ai gõ tách; các tên này không nằm trong kiểu gõ tách tôi tìm ra ở T-074). Không thành lỗi vì: dạng chuẩn và dạng viết hoa giữa chữ đều đúng; lớp chặn cuối là người duyệt ở T-056 (hiện "Ảnh thật / Ảnh AI" từng ảnh trước khi viết alt, một bấm đổi sang AI, điều kiện 2b Lá Chắn T-052); README (T-069) đã có điều kiện hướng dẫn gõ tên công cụ viết liền chuẩn. Nếu Chỉ Huy muốn bịt thêm, thêm "Run Way", "Re Craft" vào `_AI_TOOLS` như 4 tên của phiếu này (hai chữ tiếng Anh, không trùng chữ tiếng Việt không dấu) ở một phiếu dọn sau; không cần trước T-056.
- **"AnHai", "SoRa" là ảnh AI** (Soi Lỗi, T6): tên thật gõ liền không dấu trùng dạng liền của dấu hiệu ("anhai" = "ảnh AI", "sora"). Đồng ý đây là đánh đổi chấp nhận được, cùng loại "SoRa" tôi đã chấp nhận ở T6 T-074: hướng an toàn, ảnh chỉ mất thẻ công trình, không chữ nào đi ra; "An Hai", "An Hải", "So Ra" vẫn là ảnh thật. Tên **file** "AnHai…", "SoRa…" đã là ảnh AI từ trước T-077 (tên file vốn không tách chữ hoa); T-077 chỉ làm tên thư mục nhất quán với tên file.
- **`get_many` giữ mọi dòng của một lần gọi** (trước là từng nhóm 400): với file đúng cấu trúc, số dòng không quá số ảnh được hỏi (khóa chính), mỗi ô bị `substr` cắt (tối đa 13.384 byte mỗi dòng). Với file bị sửa ở mức từng byte (chỉ mục có mục trùng), giới hạn vẫn là bộ đếm bước của `_guard`, **đếm chung cho mọi câu của một kết nối** (`:556-563`): ≈ 1,66 triệu dòng mỗi lần gọi (E3). Bản cũ cũng vậy, vì một nhóm đã có thể chứa ngần ấy dòng; T-077 không nới giới hạn nào. Muốn khai thác phải chạy được chương trình trên máy (cùng mô hình đe dọa LC-T048-6 trong sổ rủi ro). T-056 gọi `resolve_many` theo trang ≤ 200 ảnh (điều kiện 3i Lá Chắn T-074).
- **Ghi nhận công cụ của Thợ Máy** (`detect-secrets scan <file…>` không `--all-files` bỏ qua file git chưa theo dõi, ra "0" giả): đồng ý, đúng với cách `security.md` mục 5 đã ghi (`--all-files`); Thư Ký có thể thêm một dòng nhắc khi sửa `security.md` lần tới.

## Điều kiện

Không có điều kiện mới (kết luận ĐẠT). Gộp T-077 vào `main` được ngay; Chỉ Huy chạy toàn bộ test trên Windows khi gộp. Các điều kiện cũ vẫn giữ, không do phiếu này:

- **T-056:** mọi điều kiện đã có (gồm 3i `resolve_many` theo trang ≤ 200 ảnh, 3j đổi sang ảnh AI lỗi lưu thì trong phiên vẫn coi là ảnh AI, của Lá Chắn T-074). Điều kiện "phiếu dọn nhỏ phải gộp trước T-056" của T-074 nay là T-077: gộp T-077 là xong điều kiện đó.
- **T-069 (README):** điều kiện 3 Lá Chắn T-074 giữ nguyên; nên thêm hai ý của Thợ Máy và Soi Lỗi: để chữ "AI" trong tên thư mục ảnh AI ("Ảnh AI - Runway"); tên thư mục ảnh thật trùng chữ gần giống "ảnh AI" thì viết có dấu hay tách chữ ("An Hải", không "AnHai").

## Kết luận

**ĐẠT.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp. LC-T074-1 (gồm SL-T074-2) đóng: bản nhánh tương đương bản sửa thử của tôi, dựng lại T5a, T6 trên nhánh đúng kết quả mong đợi, chiều ảnh AI → ảnh thật không bị kéo lùi (chứng minh theo cấu trúc và thử vi phân gần 300.000 phép so). SL-T074-1 đóng; LC-T070-2 vẫn giữ: T2 giống hệt bản `378f710`, biến thể mới chen giữa các câu đọc không làm lẫn dữ liệu (bản `da87dbf` thì lẫn), phần Python sau commit không đụng file. A3, F1, F3 đạt. Gộp `main` được ngay: không xung đột, test liên quan và test nháp ảnh T-055 qua trên cây gộp.

Chưa chạy: ca symlink trên Windows này (điều kiện T-063), thử trên Mac. Biên bản chạy tạm bằng Claude Opus 5.5; **kiểm lại bằng Claude Fable sau 01/11**.

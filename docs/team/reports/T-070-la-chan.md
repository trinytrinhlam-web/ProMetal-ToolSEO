# Biên bản bảo mật T-070 · Dọn lỗi thẻ ảnh (sau T-052) · rút gọn

> **Model:** chạy tạm **Claude Opus 5.5** vì tài khoản này không dùng được Fable (chủ dự án đã duyệt). Cần **kiểm lại bằng Claude Fable sau 01/11**.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) |
| Phiếu được kiểm | [T-070](../tickets/T-070-don-loi-the-anh.md) |
| Phạm vi | Rút gọn (A3, F1, F3). Diff `origin/main...team/T-070` (gốc chung `881548f`, HEAD `95c0f70`; `main` lúc kiểm `8d15244`): `seo_app/images/tags.py` (+79/−9), `seo_app/storage/image_tags.py` (+116/−30), `tests/test_images_tags.py` (+442), `tests/test_soi_loi_t052.py` (chỉ gỡ 3 khối `xfail`), `tests/test_soi_loi_t070.py` (mới), 2 báo cáo. Code ứng dụng tại `0da01d6`, không đổi tới `95c0f70` |
| Ngày | 2026-10-20 (19:10–19:40 +07) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 2 Thấp (LC-T070-1, LC-T070-2). LC-T052-1 (Trung bình) **đã đóng** phần nhận tên; LC-T052-3 đóng; LC-T052-2 đóng phần lớn, phần còn lại là LC-T070-1, -2. Gộp `main` được ngay; điều kiện → phiếu dọn trước T-056, T-056, T-069 |

## Tóm tắt (cho chủ dự án)

Phiếu này làm đúng việc quan trọng nhất: thư mục hay file tên "Ảnh minh họa", "trí tuệ nhân tạo", "genai", hay tên các công cụ tạo ảnh (Copilot, Designer, Leonardo, Ideogram, Flux…) nay đều làm ảnh thành **ảnh AI**, nên không bị giới thiệu như công trình thật. Tôi thử 45 tên thư mục ảnh thật kiểu Pro-Metal hay đặt (có dấu và không dấu): chỉ 2 tên gõ **không dấu** bị coi nhầm là ảnh AI ("Phoi canh cong", "Nha anh Minh Hoa"), đúng như Thợ Máy đã báo trước; ảnh nhận nhầm chỉ mất mã công trình, khu vực, trước/sau, không lộ chữ nào. File nhớ thẻ sửa tay nay được kiểm cấu trúc trước khi đọc, chặn được hầu hết file bị làm độc.

Còn **2 lỗi nhỏ** ở file nhớ thẻ (đều cần một chương trình lạ đã chạy được trên máy): một cách khéo để giấu đoạn lệnh qua lớp kiểm (Soi Lỗi đã tìm ra, tôi dựng lại được bằng cách khác), và một khe rất ngắn giữa lúc app kiểm file và lúc app ghi. Hậu quả tệ nhất là phần thẻ sửa tay chạy chậm hoặc ghi sai thẻ, không lộ dữ liệu, không đụng website. Hôm nay chưa có màn hình nào dùng phần này, nên gộp vào `main` được ngay; hai lỗi phải sửa **trước khi gộp màn hình chọn ảnh T-056**.

## Lỗi phát hiện

0 Nghiêm trọng, 0 Cao, 0 Trung bình, **2 Thấp**. Không lỗi nào làm lộ chữ của tên thư mục, lộ bí mật, đọc/ghi ngoài `data/` hay đụng WordPress. Số dòng theo `95c0f70`.

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T070-1 (= SL-T070-1) | Thấp | **Lớp kiểm `sqlite_master` bị lách bằng một dòng lặp.** `_app_tables` đọc tối đa (số dòng mong đợi + 1) = 5 dòng và so theo **tập hợp** từng bảng; một dòng chỉ mục tự sinh lặp lại bị gộp vào dòng cũ, nên dòng thứ 6 (trigger) không bao giờ được đọc. Tôi dựng lại bằng **cách khác** Soi Lỗi (lặp `sqlite_autoindex_info_1` thay vì `…manual_tags_1`; thử T1): SQLite nhận file, `quick_check` ra `ok`, `_is_healthy` = `True`, trigger chạy ở lần `set`: lưu "Tân Phú" đọc lại ra **"Quận 1"**, file không bị đổi tên. Lặp dòng **bảng** thì SQLite tự từ chối ("table info already exists"), nên chỉ dòng chỉ mục lặp được. Không có dòng lặp thì trigger bị bắt đúng (T1b) | `seo_app/storage/image_tags.py:539-544` (`_app_tables`), dùng ở `:383`, `:564` | Chương trình lạ chạy trên máy ghi một file SQLite dựng sẵn (đúng 2 bảng + 1 dòng chỉ mục lặp + trigger) vào `data/image_tags.sqlite` → mỗi lần người dùng lưu thẻ (T-056), trigger chạy trong app: sửa thẻ vừa lưu, hoặc làm mỗi lần lưu bị dừng sau vài giây (trigger đệ quy, kẹt mãi vì file không bị đổi tên), hoặc chạy hàng giây/giờ với hàm nặng (SL-T070-2). Thấp: phải chạy được chương trình trên máy (kẻ đó vốn sửa thẳng được dữ liệu trong file); trigger chỉ chạy SQL thuần (`trusted_schema = OFF`, Python tắt nạp extension), không đọc/ghi ngoài file; thẻ đọc ra vẫn qua `ImageTags` (chỉ giá trị trong danh sách) và `_keep_ai` (ảnh có tên AI vẫn là AI). Nhưng đây là lách **đúng lớp kiểm YC2 phiếu yêu cầu** | Đọc vào **danh sách**, không phải tập hợp: có hơn số dòng mong đợi, hoặc có dòng trùng `(type, name)`, thì trả `None` (giữ `LIMIT` để không đọc vô hạn). Gỡ `xfail` 3 test SL-T070-1 của Soi Lỗi khi qua |
| LC-T070-2 | Thấp | **Kiểm cấu trúc và dùng file không nằm trong cùng một giao dịch.** `_connect` kiểm `_app_tables` bằng một câu `SELECT` chạy ngoài giao dịch (Python chỉ tự `BEGIN` trước `INSERT/UPDATE/DELETE`), nên khóa đọc được nhả ngay; lệnh ghi sau đó chạy trên cấu trúc **lúc ghi**, không phải lúc kiểm. Tương tự, `_prepare` chạy `INSERT OR IGNORE INTO info` mà không kiểm lại cấu trúc trong kết nối đó. Thợ Máy đã ghi khe này ở "Rủi ro" và tin vào giới hạn số bước; SL-T070-2 cho thấy giới hạn đó không đủ. Thử T2 (giả lập chương trình khác thêm trigger **ngay sau** bước kiểm): `set` chạy trigger, khu vực trong file thành "Quận 1"; lần `set` sau mới bắt được | `image_tags.py:379-386` (`_connect`), `:414-423` (`_prepare`: kiểm ở kết nối khác, rồi `INSERT` vào `info`) | Chương trình lạ trên máy chạy vòng lặp thêm/bỏ trigger trên `data/image_tags.sqlite` → lần lưu thẻ nào rơi đúng khe giữa kiểm và ghi thì trigger chạy một lần (cùng hậu quả LC-T070-1). Khe tính bằng micro giây, phải canh thời điểm. Thấp: như LC-T070-1, lại khó hơn | Đặt bước kiểm **trong** giao dịch, trước mọi truy vấn khác: `conn.execute("BEGIN IMMEDIATE")` cho thao tác ghi (`BEGIN` cho thao tác đọc) rồi mới `_app_tables`; khóa giữ tới khi commit nên chương trình khác không đổi được cấu trúc giữa chừng (thử T2b: chương trình khác bị chặn, "database is locked"). Trong `_prepare`: `BEGIN IMMEDIATE`, kiểm `_app_tables`, rồi mới `CREATE TABLE`/`INSERT`. Có test giả lập như T2 |

## Kiểm lại các lỗi của Lá Chắn T-052

| Mã | Kết quả | Bằng chứng |
|---|---|---|
| LC-T052-1 (Trung bình) · ảnh AI bị coi là ảnh thật vì tên | **Đóng** (phần nhận theo tên). Còn phụ thuộc T-056 (điều kiện 2b, 2c của T-052) | (a) `minh họa`, `minh hoạ` (`tags.py:259-268`, dạng không dấu và viết liền tự sinh ở `_build_ai_markers` `:444-454`); (b) `trí tuệ nhân tạo`; (c) `GenAI` ở mọi kiểu hoa/thường (`_AI_JOINED` `:271`); (d) đủ 16 công cụ phiếu yêu cầu cộng 7 công cụ thêm (`_AI_TOOLS` `:203-240`); Canva coi là AI (đồng ý: hướng an toàn); (e) `is_ai_name` (`:933-946`) chỉ trả `bool`, chỉ xét tên cuối. Test: Thợ Máy 33 tên thư mục ×2 tầng, 23 tên file; Soi Lỗi thêm 66 tên thư mục, 27 tên file. Tôi thử thêm (T5): tên thật 45 tên → 2 nhầm sang AI (đều gõ không dấu, đã ghi trước); tên AI còn sót: "Ảnh mô phỏng" (SL-T070-5), "AI01.png", "dalle3.png" (SL-T070-3), "AIgen", "Ảnh Whisk", "Freepik"; tên file mặc định không chứa tên công cụ ("Untitled design.png" của Canva, "Default_…" của Leonardo cũ, "00001-…" của A1111) vẫn là ảnh thật: giới hạn của cách nhận theo tên, lớp chặn cuối là người duyệt ở T-056 |
| LC-T052-1 · mặt ngược (ảnh thật nhận nhầm là AI) | Chấp nhận được, **không phải lỗi bảo mật** | Ảnh nhầm chỉ mất mã công trình, khu vực, trước/sau (`tags.py:893-897`), alt/tên file ghi «Minh họa»: nói **ít** hơn sự thật, không nói quá. Không lộ chữ (Thợ Máy `test_t070_ambiguous_names_lean_to_ai_and_leak_nothing`). Phiền: người dùng không đổi lại được trong app (`image_tags.py:271`), phải đổi tên thư mục trên Drive (SL-T070-4) |
| LC-T052-2 (Thấp) · file thẻ độc làm treo/hỏng | **Đóng phần lớn**; còn LC-T070-1, LC-T070-2 | `_app_tables` đọc `sqlite_master` (chỉ phân tích, không chạy khung nhìn/trigger) và so cả loại, tên, bảng, nguyên câu `CREATE` với bản dựng từ chính `_CREATE_TABLES` (`:514-528`, `:531-546`), **trước** `quick_check` và mọi truy vấn khác (`:564`), ở cả `_is_healthy` và mỗi lần `_connect` (`:383`). 14 kiểu file độc của Thợ Máy + 7 kiểu của Soi Lỗi đều bị bắt, mỗi kiểu thử cả "có sẵn" và "thay khi đang chạy". `trusted_schema = OFF` ở cả 3 chỗ mở qua `_guard` (`:501`; `_expected_schema` chỉ mở `:memory:` với câu của app). Giới hạn 50 triệu bước (`:70`, `:497-510`): việc nặng nhất của file thật dưới 2,1 triệu bước (dư hơn 20 lần), đệ quy vô hạn dừng sau vài giây; nhưng không giới hạn được bước nặng (SL-T070-2). `_ready` đặt lại với mọi lỗi trừ bận/khóa (`:387-392`). File T-052 tạo vẫn được nhận (`test_t070_file_made_by_t052_is_still_accepted`) |
| LC-T052-3 (Thấp) · `get` không ép ảnh AI theo ảnh được hỏi | **Đóng** | `get_many` áp `_keep_ai(…, tags_for_image(ref).tags)` cho **từng** `ref` được hỏi (`:247-251`); `_row_to_tag` vẫn ép theo đường dẫn đã lưu (`:372`): AI nếu một trong hai là AI. Test `test_t070_get_applies_ai_rule_to_the_ref_asked`, Soi Lỗi `test_get_many_and_resolve_many_force_ai_per_ref_asked` (`khoai`/`KhoAI`/`KHOAI`) |
| LC-T052-5 (Thấp) · khe file `-journal` | **Để nguyên** đúng phiếu: chủ dự án chưa quyết | `grep journal_mode` trong `image_tags.py`: không có. Vẫn ở điều kiện 6 của biên bản T-052 |

## Đánh giá 5 lỗi của Soi Lỗi (SL-T070-1 → -5)

Hôm nay **không có code nào ngoài hai module này gọi** `ImageTagStore`, `tags_for_image` hay `is_ai_name` (`git grep` trên `origin/main` và `team/T-070`, thư mục `app`, `seo_app`: 0 chỗ). Lỗi chỉ thành thật khi T-056 dùng tới. T-070 chặt hơn hẳn bản T-052 đang ở `main` (bản đó không kiểm khung nhìn, trigger), nên giữ T-070 lại chỉ làm `main` kém an toàn lâu hơn.

| Mã | Soi Lỗi xếp | Lá Chắn | Sửa ngay hay gom |
|---|---|---|---|
| SL-T070-1 (dòng lặp che trigger) | Thấp | **Thấp, đúng mức** (= LC-T070-1; tôi dựng lại bằng biến thể khác) | **Gom phiếu dọn, phải gộp trước T-056**, cùng LC-T070-2. Không chặn gộp T-070. Nếu Chỉ Huy còn lượt Thợ Máy ngay thì sửa trong T-070 cũng được (sửa nhỏ, chỉ `_app_tables`) |
| SL-T070-2 (giới hạn số bước không phải giới hạn thời gian) | Thấp | **Thấp, đúng mức.** Chỉ tới được khi lớp kiểm cấu trúc bị lách (LC-T070-1) hoặc qua khe LC-T070-2. Tôi thử (T3): `printf('%.*c', 300000000, 'x')` chạy 1,4–3,2 giây mà không bị dừng | Gom cùng phiếu. Sửa: trong `_guard` thêm `conn.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 1_000_000)` (thử T3b: `randomblob`, `zeroblob`, `hex` báo `SQLITE_TOOBIG` ngay, `printf` trả rỗng; dòng dài nhất app ghi vẫn đọc được, T3c); **bắt buộc** coi `SQLITE_TOOBIG` (mã 18, `sqlite3.DataError`) là "hỏng" trong `_is_healthy` như `_is_interrupted`, nếu không file sẽ kẹt ở câu "Không mở được…" và không bao giờ bị đổi tên. Sửa lời "file dựng sẵn không làm treo app" ở docstring `image_tags.py:18-19` cho đúng mức |
| SL-T070-3 (tên file "AI01.png", "dalle3_…" là ảnh thật) | Thấp | **Thấp, đúng mức.** Hướng **không** an toàn (ảnh AI mang thẻ công trình thật) nhưng kiểu tên này ít gặp hơn "Ảnh minh họa" của LC-T052-1, và T-056 phải hiện "Ảnh thật / Ảnh AI" cho người duyệt (điều kiện 2b của T-052). Tôi thấy thêm "AIgen" (tên thư mục) cũng là ảnh thật | Gom cùng phiếu, **nên** gộp trước T-056 (sửa nhỏ: tên file tách thêm ở chỗ chữ ↔ số, không tách theo chữ hoa; đối chứng "xAI3kQ" đã có) |
| SL-T070-4 (tên riêng thật trùng tên công cụ thành ảnh AI) | Thấp | **Thấp, và không phải lỗi bảo mật**: hướng an toàn (nói ít hơn sự thật), đánh đổi khả dụng | **Hoãn**, chủ dự án quyết. Nếu sửa: chỉ nới cho **tên thư mục** với tên công cụ là chữ thông dụng/tên riêng, giữ nguyên nhận theo **tên file** (`Designer (3).png`, `Leonardo_…`); không thêm nút "đổi ảnh AI thành ảnh thật" trong app khi chưa có quyết định của chủ dự án. Trước mắt: T-056 hiện lý do, T-069 README dặn đặt tên |
| SL-T070-5 ("Ảnh mô phỏng" là ảnh thật) | Thấp | **Thấp, đúng mức** (hướng không an toàn, ít gặp; tôi dựng lại ở T5) | Gom cùng phiếu, nên trước T-056: thêm `mô phỏng` vào `_AI_PHRASES` (đồng ý không thêm "ảnh dựng") |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets (`PYTHONUTF8=1`, mồi trong file tiếng Việt bị bắt đủ 2/2): **0 mục** ở 7 file của diff và ở toàn bộ patch nhánh (`git log -p origin/main..team/T-070`, 110 KB). grep `security.md` mục 5 trên patch nhánh: 3 dòng, đều là tên hàm `_tokens` và biến `secret` (chữ riêng giả để kiểm không lọt). Không file nhị phân (`git diff --numstat`) |
| S2 | Đạt | Câu lỗi mới `_MSG_BROKEN` cố định, không đường dẫn (`image_tags.py:113`); `_db_message` chỉ chọn câu cố định (`:603-614`); `recovered_from` không đổi (điều kiện 2d của T-052 cho T-056 vẫn giữ) |
| S3 | Không áp dụng | Không biến cấu hình mới; `_MAX_VM_STEPS` là hằng trong code (`:70`) |
| W1 | Không áp dụng | Diff không có code WordPress (chỉ `tags.py`, `image_tags.py`, test, báo cáo) |
| W2 | Không áp dụng | Như W1 |
| W3 | Không áp dụng | Không tạo HTML |
| W4 | Không áp dụng | Không gọi mạng |
| A1 | Không áp dụng | Diff không dựng prompt; giá trị thẻ vẫn chỉ là chữ trong danh sách (A3), đường tới AI qua `reference()` không đổi. Test trên cây gộp với `alt.py` mới của `main` qua |
| A2 | Không áp dụng | Không gọi AI; nguồn ảnh thật/AI do code quyết (`tags.py:893-898`) |
| A3 | Đạt | `is_ai_name` chỉ trả `bool` (`tags.py:933-946`); dấu hiệu mới chỉ bật `ai = True`, không sinh chữ nào ra ngoài; giá trị thẻ vẫn chỉ từ `_Item.value` do code viết. Thử ngẫu nhiên 40.000 đường dẫn của T-052 vẫn chạy và qua (`tests/test_images_tags.py:1096`, `:1118`). YC4: LC-T052-1 đóng phần tên, còn SL-T070-3, -5 (Thấp) và giới hạn nhận theo tên → T-056 |
| U1 | Không áp dụng | Không có giao diện |
| U2 | Không áp dụng | Không có trang mới |
| U3 | Không áp dụng | Không đụng mật khẩu |
| F1 | Đạt | Không thêm đường dẫn mới; file lạ chỉ được đổi tên **trong** `data/` (`_move_aside`, `self.path.with_name`, `:445-462`); gỡ liên kết ở mỗi lần mở không đổi (`:404`, `:432-439`). Test trỏ file thẻ sang thư mục tạm bằng fixture tự động (`tests/test_images_tags.py:93`, `tests/test_soi_loi_t070.py:41-45`). LC-T052-4, -5 không đổi (chờ T-069, chủ dự án) |
| F2 | Không áp dụng | Không đọc nội dung ảnh, không đụng EXIF/GPS |
| F3 | Đạt, có LC-T070-1, -2 (Thấp) | Không `pickle`, `eval`, `exec`, `yaml` (grep 2 file: 0); SQL dùng tham số `?`, kể cả `_MASTER_SQL` (`:81`); `trusted_schema = OFF` ở cả 3 chỗ mở (`:501`); cấu trúc file kiểm trước mọi truy vấn khác (`:564`, `:383`); giới hạn số bước (`:497-510`). Không đọc/ghi file chữ nên không cần `encoding=`. Còn: lách bằng dòng lặp (LC-T070-1), kiểm và dùng không cùng giao dịch (LC-T070-2), bước nặng không bị giới hạn (SL-T070-2) |
| D1 | Đạt | `uv.lock`, `pyproject.toml` không đổi so với `main`; import mới chỉ thư viện chuẩn (`os`, `functools.cache`). pip-audit: 0 lỗ hổng |
| D2 | Đạt | `.gitignore:22-24` (`data/`, `*.sqlite`, `*.sqlite3`; gồm cả bản `hong-…`) không đổi |
| D3 | Đạt | Bộ chặn mạng tự bật (`tests/conftest.py:18-19`); `test_soi_loi_t070.py` không có `requests`, `urllib`, `socket`, `http`; file thẻ trỏ sang thư mục tạm (F1) |

## Kết quả công cụ quét

Máy Windows 11 Pro (10.0.26300), Python 3.12.15, SQLite 3.53.1, worktree `wt-T-070`, nhánh `team/T-070` tại `95c0f70`.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uv export --frozen --no-hashes --no-emit-project` → 69 gói ghim (`pillow==13.0.0`, `pillow-heif==1.8.1`, `streamlit==1.65.0`), `uvx pip-audit -r … --no-deps --disable-pip`: **No known vulnerabilities found** | Có. `uv.lock` không đổi so với `main`, nên kết quả như `main`. LC-T058-4 còn đó (cơ sở dữ liệu của pip-audit có thể chậm hơn khuyến cáo mới nhất) |
| bandit 1.9.x | `tags.py` + `image_tags.py` (1.336 dòng): **No issues identified**. File test của phiếu (bỏ B101, chạy với `PYTHONUTF8=1` vì bản không đặt biến này vỡ khi in chữ tiếng Việt): B311 ×2, B608 ×10 | Có. Mục ở file test là báo nhầm (mục dưới) |
| detect-secrets 1.5.0 | **Chạy với `PYTHONUTF8=1`**, `--all-files` trong thư mục riêng chứa 7 file của diff (lấy bằng `git show team/T-070:…`), patch nhánh và **1 file mồi có chữ tiếng Việt** (khóa AWS giả, `password = …`): bắt **đủ 2 mồi, 0 mục khác**. Đã xóa file mồi sau khi chạy | Có. Mồi bị bắt nên file tiếng Việt thật sự được đọc (LC-T049-4) |
| Soát lịch sử git | `git log -p origin/main..team/T-070 \| grep -inE "api[_-]?key\|password\|secret\|token"`: 3 dòng (`_tokens` ×2, `fold(secret)` trong test) | Có, đọc từng dòng |
| ruff | `uv run ruff check .`: **All checks passed!** | Có |
| pytest (test liên quan, `rules.md`) | `uv run pytest tests/test_images_tags.py tests/test_soi_loi_t052.py tests/test_soi_loi_t070.py tests/test_images_folders.py tests/test_ai_images.py -q -p no:cacheprovider -rsx` (19:28–19:31): **1003 passed, 8 skipped, 22 xfailed, 0 hỏng** | Có. 8 bỏ qua: 2 ca symlink của T-052 (`tests/test_images_tags.py:1540`, `tests/test_soi_loi_t052.py:538`, Windows chưa bật Developer Mode) + 6 ca T-048. 22 xfail đều là SL-T070-1 → -5 (`strict=True`: sửa xong mà quên gỡ thì test đỏ) |
| Gộp với `main` | `git merge-tree --write-tree origin/main team/T-070` → cây `3c7ad5d`, **không xung đột** (exit 0). Dựng cây gộp bằng `git archive` vào thư mục tạm, chạy lại 5 file test trên (19:32–19:33): **1003 passed, 8 skipped, 22 xfailed, 0 hỏng** | Có: `seo_app` nạp từ đúng thư mục cây gộp (in `seo_app.__file__`, `seo_app.images.alt.__file__`); cây gộp có `alt.py`, `process.py` mới của T-054, T-067, T-068 |

**Chưa chạy được (không ghi là đạt):** ca symlink (Windows này lỗi 1314, như T-052; điều kiện 5 của T-052 cho T-063 vẫn giữ). Không chạy toàn bộ pytest (theo `rules.md`, Chỉ Huy chạy khi gộp).

## Thử độc lập của Lá Chắn

Script nằm ngoài repo (thư mục tạm của phiên), không sửa code hay test; chạy bằng `.venv` của worktree, mọi file SQLite trong thư mục tạm.

| # | Thử gì | Kết quả |
|---|---|---|
| T1 | SL-T070-1, **biến thể khác** Soi Lỗi: file app tạo + lặp dòng `sqlite_autoindex_info_1` + trigger `AFTER INSERT ON manual_tags` sửa khu vực | `sqlite_master` 6 dòng; `_is_healthy` = **True**; `set` xong, đọc lại khu vực **"Quận 1"** (lưu "Tân Phú"), `recovered_from` = `None`. Lặp dòng **bảng** `info`: SQLite từ chối ("malformed database schema … already exists") |
| T1b | Trigger như T1 nhưng **không** có dòng lặp | `_is_healthy` = False (bắt đúng) |
| T2 | LC-T070-2: bọc `_app_tables`, ngay sau bước kiểm cho "chương trình khác" thêm trigger (`writable_schema`) | `set` chạy trigger: khu vực trong file "Quận 1". Lần `set` sau báo "File lưu thẻ ảnh bị lỗi…" (bắt được, nhưng trễ một lần) |
| T2b | Cách sửa đề xuất: `BEGIN` rồi mới `_app_tables`, giữ giao dịch; kết nối khác (timeout 0) cố thêm trigger | Kết nối khác bị chặn: **"database is locked"** |
| T3 | SL-T070-2: `_guard` (giới hạn thật 50 triệu bước) + `SELECT length(printf('%.*c', 300000000, 'x'))` | Chạy xong sau 1,4–3,2 giây, không bị dừng, cấp phát 300 MB |
| T3b | Thử `setlimit(SQLITE_LIMIT_LENGTH, 1_000_000)` | `printf` trả rỗng ngay; `randomblob`, `zeroblob`, `hex(zeroblob)` báo `DataError` "string or blob too big", mã 18 (`SQLITE_TOOBIG`); `_is_corrupt`, `_is_interrupted`, `_is_busy` đều **False** với lỗi này (vì vậy cách sửa phải thêm nhận `SQLITE_TOOBIG`) |
| T3c | Dòng dài nhất app ghi (đường dẫn ~900 ký tự có dấu) đọc lại dưới giới hạn 1 MB | Đọc được 1 dòng, `quick_check` = `ok` |
| T4 | `is_ai_name` với 11 dạng đường dẫn | Đúng: `G:/My Drive/Ảnh AI` (có/không gạch cuối, kiểu `\`), có ký tự vô hình, `Path(…/Ảnh AI/.)` → True; `G:/AI/Ảnh công trình`, `""`, `G:` → False. **Chuỗi** kết thúc bằng `/.` → False (pathlib thì bỏ `.`); `RootInfo.label` lấy từ `Path.name` nên không dính (ghi vào điều kiện T-056) |
| T5 | 45 tên thư mục ảnh thật kiểu Pro-Metal (23 có dấu, 22 không dấu: "Cong tu dong", "Che tao cong sat", "Mai ton Binh Duong", "Nha anh Thai", "Anh Hai Quan 7"…); 19 tên ảnh AI/không phải ảnh chụp; 10 tên file | Ảnh thật nhầm sang AI: **2/45** ("Phoi canh cong", "Nha anh Minh Hoa", đều đã ghi là đánh đổi). Còn là ảnh thật: "Ảnh mô phỏng", "AIgen", "Ảnh Whisk", "Freepik", "Ảnh tham khảo", "Ảnh mạng"; file "AI01.png", "dalle3.png", "Untitled design.png", "Default_cong_sat.jpg", "00001-1234567890.png". "ai_01.png", "AI-01.png", "anh-ai-01.png" là ảnh AI (đúng) |

## Báo nhầm đã loại

- **bandit B311** (`tests/test_images_tags.py:1096`, `:1118`): `random.Random(hạt giống cố định)` sinh tên thư mục thử ngẫu nhiên, không dùng cho mật mã.
- **bandit B608** (`tests/test_images_tags.py:1687`, `:1697`, `:1701`, `:1706`, `:1709`, `:1713`, `:1717`; `tests/test_soi_loi_t052.py:580`; `tests/test_soi_loi_t070.py:299`, `:377`): test dựng file SQLite độc bằng chuỗi f ghép **hằng trong test** (câu `CREATE`, tên cột, truy vấn đệ quy có giới hạn); không có dữ liệu ngoài.
- **Chuỗi f trong SQL của `image_tags.py`** (bandit không báo): đọc lại từng chỗ, chỉ ghép hằng (`_SELECT`, `_COLUMNS`) và dãy `?`; `_MASTER_SQL` dùng tham số cho cả độ dài và `LIMIT`.
- **detect-secrets**: 2 mục duy nhất là chuỗi mồi tôi tự đặt.

## Ghi nhận (không thành lỗi)

- **Ngưỡng `_MAX_VM_STEPS` = 50 triệu**: dư hơn 20 lần so với việc nặng nhất của file thật Thợ Máy đo; bộ đếm tính theo kết nối (mỗi thao tác một kết nối) nên không cộng dồn giữa các lần. Máy chậm hơn (Mac đời cũ) thì truy vấn đệ quy dừng sau lâu hơn vài giây, chấp nhận được.
- **Canva, Designer coi là ảnh AI**: đồng ý (hướng an toàn; ảnh thiết kế không phải ảnh chụp công trình).
- **Ảnh không phải ảnh công trình mà cũng không phải ảnh AI** ("Ảnh tham khảo", "Ảnh mạng", "Freepik"): app coi là ảnh thật. Ngoài phạm vi YC4 (chỉ nói về ảnh AI) nhưng cùng hậu quả (ảnh không phải của Pro-Metal được tả như công trình thật, thêm rủi ro bản quyền). Đưa vào README (T-069): không để ảnh lấy từ mạng trong thư mục ảnh đã khai báo.
- **Đua nhẹ khi hai tab cùng tạo file lần đầu**: `CREATE TABLE` chạy từng câu một nên tab kia có thể thấy file mới có một bảng và báo lỗi một lần; `_is_healthy` cho phép bảng chưa có nên **không** đổi tên file thật, không mất thẻ.
- `is_ai_name` không giới hạn độ dài (Soi Lỗi: 1 triệu ký tự mất 7,5 giây); T-056 chỉ đưa tên một thư mục (tối đa 255 ký tự) nên không thành lỗi.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

Gộp T-070 vào `main` được ngay (Chỉ Huy chạy toàn bộ test khi gộp). Các điều kiện sau Chỉ Huy chép vào phiếu nhận:

1. **Phiếu dọn thẻ ảnh lượt 2** (Chỉ Huy lập số; Thợ Máy; phạm vi `seo_app/storage/image_tags.py`, `seo_app/images/tags.py`, `tests/test_images_tags.py`, gỡ `xfail` ở `tests/test_soi_loi_t070.py`). **Phải gộp trước T-056.** Soi Lỗi rút gọn, Lá Chắn rút gọn.
   - LC-T070-1 (SL-T070-1): `_app_tables` đọc vào danh sách, hơn số dòng mong đợi hoặc có dòng trùng thì `None`.
   - LC-T070-2: kiểm cấu trúc trong cùng giao dịch với thao tác (`BEGIN IMMEDIATE` cho ghi, `BEGIN` cho đọc, trước `_app_tables`); `_prepare` kiểm trong giao dịch trước `CREATE`/`INSERT`. Test giả lập như T2.
   - SL-T070-2: `setlimit(SQLITE_LIMIT_LENGTH, …)` trong `_guard`; coi `SQLITE_TOOBIG` là hỏng ở `_is_healthy` (và đặt lại `_ready`); sửa lời "không làm treo app" ở docstring `image_tags.py:18-19`.
   - SL-T070-3: tên file tách thêm ở chỗ chữ ↔ số (giữ "xAI3kQ" là ảnh thật); xét thêm "AIgen".
   - SL-T070-5: thêm `mô phỏng` vào `_AI_PHRASES`.
   - Nếu Chỉ Huy còn lượt Thợ Máy ngay trong T-070 thì làm các mục trên ở T-070 cũng được; khi đó Lá Chắn kiểm lại rút gọn trước khi gộp.
2. **T-056** (giao diện chọn ảnh): giữ nguyên điều kiện 2(a)–(f) của Lá Chắn T-052, thêm:
   - (g) Gọi `is_ai_name` với `RootInfo.label` (tên lấy từ `Path`, không tự cắt chuỗi đường dẫn: chuỗi kết thúc bằng `/.` cho kết quả sai, T4) **và** với tên thư mục gốc sau `resolve()` (gốc là junction/symlink thì tên thật có thể khác); một trong hai đúng thì mọi ảnh trong gốc là ảnh AI. Chỉ dùng `is_ai_name` cho tên thư mục gốc.
   - (h) Hiện lý do một ảnh bị coi là ảnh AI ("tên thư mục hoặc tên file có chữ AI / tên công cụ tạo ảnh"), vì người dùng không đổi lại được trong app (SL-T070-4).
3. **T-069** (README): liệt kê các chữ làm ảnh thành ảnh AI; gõ tên thư mục ảnh thật **có dấu**; tránh tên công cụ đứng riêng (Sora, Flux, Designer, Canva, Bing…); không để ảnh lấy từ mạng/ảnh tham khảo trong thư mục ảnh.
4. **Chủ dự án quyết** (Chỉ Huy hỏi): SL-T070-4 (sửa hay giữ, xem đề xuất ở bảng trên); LC-T052-5 (ghi sổ rủi ro hay `journal_mode = MEMORY`, điều kiện 6 của T-052, vẫn mở).

## Kết luận

**ĐẠT CÓ ĐIỀU KIỆN.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình; 2 Thấp (LC-T070-1 = SL-T070-1, LC-T070-2). Lỗi Trung bình duy nhất còn mở từ T-052 (LC-T052-1, ảnh AI bị coi là ảnh thật vì tên) đã được sửa ở phần nhận tên, có test cả hai chiều; LC-T052-3 đóng; LC-T052-2 đóng phần lớn. Trọng tâm A3 giữ nguyên: không chữ nào của tên thư mục đi ra ngoài module. 5 lỗi của Soi Lỗi đều đúng mức Thấp: SL-T070-1, -2, -3, -5 gom vào phiếu dọn lượt 2 phải gộp trước T-056; SL-T070-4 hoãn chờ chủ dự án.

Chưa chạy: ca symlink trên Windows này (điều kiện T-063). Biên bản chạy tạm bằng Claude Opus 5.5; **kiểm lại bằng Claude Fable sau 01/11**.

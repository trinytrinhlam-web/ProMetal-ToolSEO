# Biên bản bảo mật T-074 · Dọn thẻ ảnh lượt 2 (sau T-070) · rút gọn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) |
| Phiếu được kiểm | [T-074](../tickets/T-074-don-the-anh-luot-2.md) |
| Phạm vi | Rút gọn (A3, F1; yêu cầu bảo mật riêng A3, F1, F3). Diff `da87dbf...team/T-074` (gốc `da87dbf`, đầu nhánh lúc kiểm `eec8fc7`; code ứng dụng đổi lần cuối ở `f4069ec`, sau đó chỉ có test và báo cáo): `seo_app/storage/image_tags.py` (+102/−23), `seo_app/images/tags.py` (+46/−19), `tests/test_images_tags.py` (+400/−4), `tests/test_soi_loi_t070.py` (chỉ gỡ 6 khối `xfail`, −44), `tests/test_soi_loi_t074.py` (mới), 2 báo cáo. `origin/main` lúc kiểm `b5eecc9`. Lá Chắn thêm `tests/test_la_chan_t074.py` (mới: chỉ `xfail(strict=True)` cho LC-T074-1 và ca đối chứng) |
| Ngày | 2026-10-21 (11:23–12:00 +07) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 1 Thấp (LC-T074-1, gồm SL-T074-2 của Soi Lỗi; có từ trước T-074). **LC-T070-1 và LC-T070-2 đã đóng.** Đồng ý SL-T074-1 Thấp (hiệu năng, không phải lỗ bảo mật). Gộp `main` được ngay; điều kiện → phiếu dọn nhỏ phải gộp trước T-056, T-056, T-069 |

## Tóm tắt (cho chủ dự án)

Hai lỗ nhỏ ở file nhớ thẻ ảnh sửa tay mà tôi tìm ra ở T-070 đã được vá thật. Tôi dựng lại đúng hai cách lách cũ và thêm nhiều biến thể khó hơn (chương trình lạ chen vào đúng lúc app vừa kiểm file, kiên nhẫn chờ tới lượt, file ở chế độ ghi khác): đoạn lệnh giấu trong file không chạy lần nào; bản cũ thì lần nào cũng chạy. Khi gặp lỗi giữa chừng, app không để file bị khóa; file lạ được đổi tên sang một bên, giữ nguyên, app tạo file mới.

Còn **1 lỗi nhỏ có từ trước** (không do phiếu này): thư mục hay file ảnh AI đặt tên công cụ theo kiểu "MidJourney", "Mid Journey", "Co-Pilot" vẫn bị coi là **ảnh thật** (giữ mã công trình, khu vực). Cách viết chuẩn "Midjourney", "Copilot" thì đúng. Sửa rất nhỏ (tôi đã thử trên bản sao: hết lỗi, không tên ảnh thật nào bị ảnh hưởng), nên phải xong **trước màn hình chọn ảnh T-056**. Trong lúc chờ: đặt tên thư mục ảnh AI theo cách viết liền chuẩn. Hôm nay chưa màn hình nào dùng phần này, nên gộp phiếu vào `main` được ngay.

## Lỗi phát hiện

0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp**. Không lỗi nào làm lộ chữ của tên thư mục, lộ bí mật, đọc/ghi ngoài `data/` hay đụng WordPress. Số dòng theo `eec8fc7`.

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T074-1 (gồm SL-T074-2) | Thấp | **Tên công cụ tạo ảnh AI một từ bị gõ khác dạng chuẩn thì ảnh AI bị coi là ảnh thật.** (a) Viết hoa giữa chữ ở **tên thư mục** và thư mục gốc: "MidJourney", "FireFly", "CoPilot", "SeeDream", "ReCraft", "RunWay"… (SL-T074-2, tôi dựng lại 12 tên). (b) **Mới, Soi Lỗi chưa ghi:** gõ **tách đôi** bằng dấu cách hay gạch nối ở **cả tên thư mục, tên file và thư mục gốc**: "Mid Journey", "Mid-Journey", "Fire Fly", "Co Pilot", "Co-Pilot", "See Dream" (T5a); cách sửa một dòng của Soi Lỗi không gỡ được kiểu này (T6). Dạng chuẩn ("Midjourney", "midjourney", "MIDJOURNEY") và dấu hiệu nhiều chữ ("Chat GPT", "Comfy UI", "Stable-Diffusion", "DALL·E") đều đúng. **Có từ trước:** `main` `da87dbf` cho kết quả y như nhánh (T5a) | `seo_app/images/tags.py:855` (`_parse_dir_name` chỉ đọc kiểu tách chữ hoa), `:204-241` (`_AI_TOOLS` chỉ có dạng một từ); đi qua `:939` (tên file), `:973` (`is_ai_name`) | Người dùng tạo ảnh bằng Midjourney, lưu vào thư mục Drive `CT012 - Cổng inox - Quận 7/truoc/MidJourney/` (hay `Mid Journey/`, hay file `Mid Journey 0001.png`) → `tags_for_image` trả ảnh **thật**, giữ CT012, Quận 7, trước → khi T-056 dùng: alt không có «Minh họa», tên file và chú thích như ảnh chụp công trình → bài đăng giới thiệu ảnh AI như công trình thật của Pro-Metal. **Thấp** vì: không lộ chữ nào (A3 giữ); cách viết chuẩn, phổ biến nhất vẫn đúng; T-056 phải hiện "Ảnh thật / Ảnh AI" từng ảnh **trước** khi viết alt và có nút đổi sang ảnh AI (điều kiện 2b Lá Chắn T-052); hôm nay chưa màn hình nào gọi. Cùng loại SL-T070-3, -5 đã xếp Thấp ở T-070. Nhưng là hướng **không** an toàn, nên phải sửa trước T-056 | (1) `_parse_dir_name`: `ai = _has_ai_marker(cleaned, split_case=True) or _has_ai_marker(cleaned, split_case=False)` (đề xuất của Soi Lỗi, đọc thêm kiểu tên file); (2) thêm vào `_AI_TOOLS` 4 dạng tách: `"Mid Journey"`, `"Fire Fly"`, `"Co Pilot"`, `"See Dream"` (dạng gạch nối tự khớp vì gạch nối tách chữ). **Không** ghép bừa mọi cặp chữ liền nhau: "Cua so ra ban cong" (cửa sổ ra ban công) sẽ thành "sora". Đã thử đúng cách (1)+(2) trên bản sao (T6): 38 ca `xfail` thành `XPASS(strict)` (18 SL-T074-2 + 20 LC-T074-1), 836 test khác qua, ca đối chứng qua; 0/112 tên thư mục thật kiểu Pro-Metal đổi kết quả; trong 60.336 tên ghép ngẫu nhiên chỉ tên có đúng cặp chữ tiếng Anh đó, và tên trơ trọi "SoRa", đổi sang ảnh AI (hướng an toàn). Gỡ `xfail` ở `tests/test_soi_loi_t074.py` và `tests/test_la_chan_t074.py` khi XPASS |

## Kiểm lại lỗi của Lá Chắn T-070 và các mục phiếu yêu cầu

| Mã | Kết quả | Bằng chứng |
|---|---|---|
| LC-T070-1 (= SL-T070-1) · dòng lặp trong `sqlite_master` | **Đóng** | `_app_tables` đọc vào danh sách, quá 4 dòng hay trùng `(loại, tên)` thì `None` (`image_tags.py:598-602`). **T1 dựng lại trên nhánh** (lặp `sqlite_autoindex_info_1` + trigger sửa khu vực): `quick_check` "ok" nhưng `_is_healthy` = False; lưu "Tân Phú" đọc lại "Tân Phú" qua 2 lần tạo kho; file lạ đổi tên `image_tags.hong-<giờ>.sqlite` **cùng thư mục**, giữ nguyên từng byte (vẫn còn trigger); file mới đúng 4 dòng. Đối chứng bản cũ `da87dbf` trên bản sao cùng file: `_is_healthy` = True, trigger chạy, trong file thành **"Quận 1"**. 4 biến thể mới của tôi (T1): lặp với loại viết hoa, trigger nằm trong câu của dòng chỉ mục tự sinh, trigger ghi `tbl_name = info`: đều bị bắt (hai kiểu sau SQLite tự báo "malformed"); kiểu "câu `CREATE` đúng + ký tự NUL + trigger phía sau" qua được lớp kiểm nhưng **vô hại**: SQLite chỉ đọc câu tới NUL khi dựng cấu trúc, `substr` của lớp kiểm cũng dừng ở NUL; sau 2 lần lưu khu vực vẫn đúng, SQLite nhận 0 trigger, `integrity_check` "ok" (T1b). Cộng 7 biến thể Soi Lỗi đã thử (E1) |
| LC-T070-2 · kiểm và dùng không cùng giao dịch | **Đóng** | `_begin` mở giao dịch **trước** `_app_tables` ở `_connect` (`:412`), `_prepare` (`:455`, trước `CREATE`/`INSERT`), `_is_healthy` (`:628`); `set`, `clear`, `clear_all` mở giao dịch ghi (`BEGIN IMMEDIATE`, `:304`, `:336`, `:345`), đọc mở `BEGIN`. **T2 dựng lại** với kẻ tấn công dùng câu `CREATE TRIGGER` thật, chen ngay sau **mỗi** lần kiểm, ở 8 lối vào (`set`, `clear`, `clear_all`, `get`, `resolve_many`, `list_manual`, và kho mới qua `set`/`get`: `_is_healthy` → `_prepare` → `_connect`), 2 chế độ nhật ký × kẻ tấn công không chờ/chờ khóa: nhật ký thường, không chờ: **12/12** lần chen nhận "database is locked"; chờ khóa: chỉ vào được sau khi giao dịch của app xong (≈ 0,33 s), trigger không chạy trong thao tác, thao tác kế tiếp bắt được (báo lỗi một lần), lần sau nữa đổi tên file và lưu đúng; **WAL**: thao tác ghi chặn được, thao tác đọc thì WAL cho chương trình khác ghi song song nhưng app vẫn đọc trên bản đã kiểm, thao tác kế tiếp bắt được. **Không lần nào** khu vực thành "Quận 1". Đối chứng bản cũ `da87dbf` cùng kịch bản: **40/40** lần chen vào được, `set` chạy trigger ngay trong lần lưu (khu vực "Quận 1") ở cả 4 kiểu. Lần chạy với kẻ tấn công sửa thẳng `sqlite_master` (không đổi số phiên bản cấu trúc): bản mới cũng chặn 12/12 |
| Lỗi giữa giao dịch có để khóa treo không (phiếu giao thêm) | **Không treo** | T4, 8 kiểu lỗi: lỗi Python và `KeyboardInterrupt` khi đang xử lý dòng đọc được; câu thứ hai của `set` bị dừng vì quá số bước (ghi dở được hoàn tác, khu vực vẫn "Quận 7"); `BEGIN IMMEDIATE` chờ quyền ghi quá 5 s; commit bị khóa đọc của chương trình khác chặn quá 5 s (báo "đang bận" sau 5,5 s, không ghi dở); cấu trúc lạ bắt ở `_connect` và ở `_prepare`; ô quá dài (`SQLITE_TOOBIG`) giữa giao dịch đọc. Sau **mỗi** lỗi: kết nối khác (không chờ) lấy ngay được `BEGIN EXCLUSIVE`, không còn file nhật ký, thao tác kế tiếp chạy được. Mỗi thao tác một kết nối, đóng bằng `closing` (`:409`, `:449`, `:622`) |
| File lạ có được đổi tên đúng và giữ lại không (phiếu giao thêm) | **Đúng** | `_move_aside` chỉ đổi tên trong cùng thư mục (`self.path.with_name`, `:485-502`), kèm file nhật ký. T1, T3, T4: file lạ nằm cạnh file mới trong `data/`, giữ nguyên từng byte. File lạ đang bị chương trình khác mở (Windows không cho đổi tên): báo "Không tạo được file lưu thẻ ảnh (…being used by another process)", **không** có đường dẫn, không xóa; chương trình kia đóng thì lần sau đổi tên được |
| SL-T070-2 · giới hạn độ dài, `SQLITE_TOOBIG` | **Đóng** | `setlimit(SQLITE_LIMIT_LENGTH, 1_000_000)` trong `_guard` (`:547`), có ở **cả 4 loại kết nối** (`_is_healthy`, `_prepare`, `_connect` đọc, `_connect` ghi): `randomblob`, `zeroblob`, `replace` phình → `SQLITE_TOOBIG` (18), `printf('%.*c', 3000000, …)` → NULL (T3). 5 kiểu ô 1,2 MB (chữ, chữ nhiều byte, khối byte ở cột số, khối byte ở khóa chính, giá trị bảng `info`): `quick_check` "ok" nhưng `_is_healthy` = False nhờ bước đọc thử mọi ô (`_OVERSIZED_SQL`, `:122-135`, `:636-638`), file đổi tên, giữ nguyên, kho dùng lại được. `_is_too_big` (`:673-679`) ở `_is_healthy` (`:645`) và `_db_message` (`:687`) |
| SL-T070-3, SL-T070-5 · tên file dính số, "AIgen", "mô phỏng" | **Đóng**, không kéo lùi | Test `xfail` cũ của Soi Lỗi nay qua với đúng điều kiện cũ. T5b: 2.180 tên dựng từ mọi dấu hiệu AI trong nhiều ngữ cảnh (dính số, gạch, viết liền, hoa/thường): **0** tên bản gốc nhận AI mà nhánh nhận thật (thư mục và tên file); 66 tên thư mục, 480 tên file thêm thành AI (đúng mục đích: tách chữ dính số, dấu hiệu mới) |

## Đánh giá 2 lỗi của Soi Lỗi

| Mã | Soi Lỗi xếp | Lá Chắn | Sửa ở đâu, khi nào |
|---|---|---|---|
| SL-T074-1 (`get_many` giữ khóa đọc suốt phần xử lý dòng) | Thấp (hiệu năng) | **Thấp, đúng mức; không phải lỗ bảo mật.** Hậu quả chỉ là lần lưu ở tab/cửa sổ khác chờ, quá 5 s thì báo "đang bận" (có câu báo, không ghi dở, không mất dữ liệu); chương trình lạ trên máy vốn giữ được khóa lâu hơn nhiều. Chỉ xảy ra khi một lần đọc có hàng nghìn ảnh đã sửa thẻ tay. Cách sửa thử E3b của Soi Lỗi (đọc hết dòng trong giao dịch, xử lý sau) **giữ nguyên LC-T070-2**: mọi câu SQL vẫn chạy trong giao dịch đã kiểm, chỉ dời phần Python ra sau commit (tôi đọc diff) | **Nên** sửa cùng phiếu dọn nhỏ ở điều kiện 2 (khoảng 10 dòng, đã thử); về bảo mật **không bắt buộc** trước T-056. T-056 phải gọi `resolve_many` theo trang (điều kiện 3i) |
| SL-T074-2 ("MidJourney" ở tên thư mục) | Thấp | **Giữ Thấp**, gộp vào **LC-T074-1** và mở rộng (kiểu tách đôi, cả tên file). Không nâng lên Trung bình vì: dạng chuẩn đúng, lớp chặn cuối là người duyệt ở T-056 (hiện "Ảnh thật / Ảnh AI" trước khi viết alt, một bấm đổi sang AI), không lộ chữ; cùng mức với SL-T070-3, -5. Hướng không an toàn nên **phải** gộp trước T-056 | Phiếu dọn nhỏ ở điều kiện 2 (Thợ Máy), **trước T-056**. Không gộp vào T-056: phạm vi T-056 không được sửa `seo_app/**` |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets (`PYTHONUTF8=1`, mồi trong file có chữ tiếng Việt bị bắt đủ 2/2, đã xóa mồi): **0 mục** ở 7 file của diff (lấy bằng `git show team/T-074:…`) và patch nhánh (`git log -p da87dbf..team/T-074`, 154 KB). grep `security.md` mục 5 trên patch nhánh: 14 dòng, đều là tên hàm `_tokens` và chữ "detect-secrets" trong báo cáo. Không file nhị phân (`git diff --numstat`) |
| S2 | Đạt | Câu lỗi cố định, không đường dẫn: `_MSG_BROKEN` (`image_tags.py:142`), `_db_message` (`:682-692`, `SQLITE_TOOBIG` → `_MSG_BROKEN`); lỗi `OSError` chỉ ghép `strerror` (`:426-429`, `:466-469`), T4 thử thật: câu không có đường dẫn. `recovered_from` không đổi (điều kiện 2d của T-052 cho T-056 vẫn giữ) |
| S3 | Không áp dụng | Không biến cấu hình mới; `_MAX_SQLITE_LENGTH` là hằng (`:84`) |
| W1 | Không áp dụng | Diff không có code WordPress |
| W2 | Không áp dụng | Như W1 |
| W3 | Không áp dụng | Không tạo HTML |
| W4 | Không áp dụng | Không gọi mạng |
| A1 | Không áp dụng | Diff không dựng prompt; giá trị thẻ tới AI vẫn qua `reference()` không đổi |
| A2 | Không áp dụng | Không gọi AI; ảnh thật/AI do code quyết (`tags.py:920-925`) |
| A3 | Đạt, có LC-T074-1 (Thấp) | Dấu hiệu mới chỉ bật `ai = True`, không sinh chữ nào ra ngoài; `is_ai_name` chỉ trả `bool` (`tags.py:960-973`). T5d: 20.000 đường dẫn ngẫu nhiên (có chữ số lạ: ², ①, ٣, chữ toàn chiều rộng "ＡＩ０１"): mọi giá trị thẻ đều trong danh sách cố định, `is_ai_name` chỉ ra `bool`. Ảnh AI vẫn không mang mã công trình, khu vực, trước/sau (`:920-924`). Còn LC-T074-1: một số kiểu gõ tên công cụ làm ảnh AI thành ảnh thật |
| U1 | Không áp dụng | Không có giao diện |
| U2 | Không áp dụng | Không có trang mới |
| U3 | Không áp dụng | Không đụng mật khẩu |
| F1 | Đạt | Không thêm đường dẫn mới; file lạ chỉ đổi tên **trong** thư mục của file thẻ (`:485-502`), đã thử T1, T3, T4; gỡ liên kết ở mỗi lần mở không đổi (`:437`, `:472-479`). Test trỏ file thẻ sang thư mục tạm bằng fixture tự động (`tests/test_soi_loi_t074.py:41-45`, `tests/test_images_tags.py:96`); `tests/test_la_chan_t074.py` chỉ xử lý chữ, không mở file. Ca symlink vẫn bỏ qua trên Windows này (điều kiện T-063, như T-070) |
| F2 | Không áp dụng | Không đọc nội dung ảnh, không đụng EXIF/GPS |
| F3 | Đạt | Không `pickle`, `eval`, `exec`, `yaml` (grep 2 file: chỉ có chữ trong docstring); SQL dùng tham số `?`; chuỗi f trong SQL chỉ ghép hằng (`:124` tên bảng/cột hằng, `:269` dãy `?`, `:307` `_COLUMNS`, `:360` `where` hằng). `trusted_schema = OFF`, giới hạn số bước và độ dài ở cả 4 loại kết nối (T3); kiểm cấu trúc trong cùng giao dịch với thao tác (LC-T070-2 đóng). Không đọc/ghi file chữ nên không cần `encoding=` |
| D1 | Đạt (cho phiếu này) | `uv.lock`, `pyproject.toml` không đổi so với gốc; không import mới. pip-audit: **1 lỗ hổng `certifi 2026.7.22` (PYSEC-2026-4320)**: có từ trước, toàn repo, là LC-T061-1 (Cao) đang sửa ở T-075 (Lá Chắn T-055 cũng ghi vậy); không do T-074, gộp T-074 không làm nặng thêm. T-056 đã có điều kiện "T-075 phải gộp trước" |
| D2 | Đạt | `.gitignore:22-24` (`data/`, `*.sqlite`, `*.sqlite3`; gồm bản `hong-…`) không đổi |
| D3 | Đạt | Bộ chặn mạng tự bật (`tests/conftest.py:18-19`); `tests/test_soi_loi_t074.py`, `tests/test_la_chan_t074.py` không có `requests`, `urllib`, `socket`, `http` |

## Kết quả công cụ quét

Máy Windows 11 Pro (10.0.26300) của chủ dự án, Python 3.12.15, SQLite 3.53.1, worktree `wt-T-074`, nhánh `team/T-074` tại `eec8fc7`. Máy đang chạy song song các agent khác.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit 2.10.1 | `uv export --frozen --no-hashes --no-emit-project` → 69 gói ghim, `uvx pip-audit -r … --no-deps --disable-pip`: **1 lỗ hổng**: `certifi 2026.7.22` PYSEC-2026-4320, sửa ở 2026.10.19 | Có. Có từ trước, không do T-074 (D1); xử lý ở T-075 |
| bandit 1.9.4 | `tags.py` + `image_tags.py` (1.413 dòng): 1 mục B608 (Medium, độ tin Low) ở `image_tags.py:124`. File test của phiếu (bỏ B101, `PYTHONUTF8=1`): B608 ×13, B311 ×2 | Có. Đều là báo nhầm (mục dưới) |
| detect-secrets 1.5.0 | **Chạy với `PYTHONUTF8=1`**, `--all-files` trong thư mục riêng chứa 7 file của diff, patch nhánh và **1 file mồi có chữ tiếng Việt** (khóa AWS giả, `password = …`): bắt **đủ 2 mồi, 0 mục khác**. Đã xóa file mồi | Có. Mồi bị bắt nên file tiếng Việt thật sự được đọc (LC-T049-4) |
| Soát lịch sử git | `git log -p da87dbf..team/T-074 \| grep -inE "api[_-]?key\|password\|secret\|token"`: 14 dòng (`_tokens`, chữ "detect-secrets") | Có, đọc từng dòng |
| ruff | `uv run ruff check .`: **All checks passed!** (cả sau khi thêm `tests/test_la_chan_t074.py`) | Có |
| pytest (test liên quan, `rules.md`) | `uv run pytest tests/test_images_tags.py tests/test_soi_loi_t052.py tests/test_soi_loi_t070.py tests/test_soi_loi_t074.py tests/test_images_folders.py tests/test_ai_images.py -q -p no:cacheprovider -rsx` (11:40–11:44): **1215 passed, 8 skipped, 26 xfailed, 0 hỏng**. Thêm `tests/test_la_chan_t074.py` (11:54–11:55): **1223 passed, 8 skipped, 46 xfailed, 0 hỏng** | Có. 8 bỏ qua: 2 ca symlink của T-052 (`tests/test_images_tags.py:1641`, `tests/test_soi_loi_t052.py:538`, Windows chưa bật Developer Mode) + 6 ca T-048. 46 xfail = 7 SL-T070-4 (hoãn, đúng phiếu) + 1 SL-T074-1 + 18 SL-T074-2 + 20 LC-T074-1, đều `strict=True` |
| Gộp với `main` | `git merge-tree --write-tree origin/main team/T-074` (`origin/main` = `b5eecc9`) → cây `5e92bbb`, **không xung đột** (exit 0). Dựng cây gộp bằng `git archive` vào thư mục tạm, chạy 6 file test trên (11:45–11:46): **1215 passed, 8 skipped, 26 xfailed, 0 hỏng**; `tests/test_la_chan_t074.py` trên cây gộp: 8 passed, 20 xfailed | Có: `seo_app` nạp từ đúng thư mục cây gộp (in `__file__`), cây gộp có `sanitize.py`, `html.py`, `wordpress/client.py` mới của T-061. File `main` đổi từ gốc không trùng file nào của T-074 |

**Chưa chạy được (không ghi là đạt):** ca symlink (Windows này lỗi 1314; điều kiện T-063 vẫn giữ). Không chạy toàn bộ pytest (theo `rules.md`, Chỉ Huy chạy khi gộp). Chưa thử trên Mac.

## Báo nhầm đã loại

- **bandit B608 `image_tags.py:124`** (`_oversized_sql`): chỉ gọi lúc nạp module với tên bảng, tên cột hằng (`:132-135`: `"manual_tags"` + `_COLUMNS`, `"info"` + `("key", "value")`); giá trị so dùng tham số `?1`.
- **bandit B608 trong test** (`tests/test_soi_loi_t074.py:96`, `:100`, `:107`; `tests/test_images_tags.py:1788`, `:1798`, `:1802`, `:1807`, `:1810`, `:1814`, `:1818`, `:2041`; `tests/test_soi_loi_t070.py:299`, `:377`): test dựng file SQLite độc bằng chuỗi f ghép **hằng trong test** (câu trigger, tên chỉ mục); không có dữ liệu ngoài.
- **bandit B311** (`tests/test_images_tags.py:1197`, `:1219`): `random.Random(hạt giống cố định)` sinh tên thư mục thử ngẫu nhiên, không dùng cho mật mã.
- **detect-secrets**: 2 mục duy nhất là chuỗi mồi tôi tự đặt.

## Thử độc lập của Lá Chắn

Script nằm ngoài repo (thư mục nháp của phiên), không sửa code ứng dụng; chạy bằng `.venv` của worktree (`PYTHONUTF8=1 uv run python <script>`), mọi file SQLite trong thư mục nháp. Bản cũ nạp từ `git show da87dbf:…`.

| # | Thử gì | Kết quả |
|---|---|---|
| T1 | LC-T070-1: T1 nguyên bản + 4 biến thể mới, bản mới và bản cũ trên cùng file | Như bảng "Kiểm lại" ở trên: bản mới bắt cả 5 (kiểu NUL vô hại), file lạ giữ nguyên từng byte; bản cũ để trigger chạy ("Quận 1") ở T1 |
| T1b | Kiểu "câu `CREATE` đúng + NUL + trigger" có thật sự chứa trigger không | Câu 398 byte, có NUL, phần sau NUL là `CREATE TRIGGER…`; lớp kiểm đọc được đúng câu của app; sau 2 lần lưu khu vực đúng, SQLite nhận 0 trigger, `integrity_check` "ok" |
| T2 | LC-T070-2: chen `CREATE TRIGGER` ngay sau mỗi lần kiểm, 8 lối vào × nhật ký thường/WAL × không chờ/chờ khóa; bản mới và bản cũ | Bản mới: không lần nào trigger chạy trong thao tác; nhật ký thường không chờ: 12/12 bị chặn; còn lại bắt được ở thao tác kế. Bản cũ: 40/40 lần chen vào được, `set` chạy trigger ngay ("Quận 1") |
| T3 | Giới hạn độ dài ở từng loại kết nối; 5 kiểu ô 1,2 MB | Giới hạn 1.000.000 ở cả 4 loại kết nối; 5/5 file đổi tên, giữ nguyên, kho dùng lại được |
| T4 | 8 kiểu lỗi giữa giao dịch + file lạ đang bị mở | Khóa luôn được nhả, ghi dở hoàn tác, thao tác kế tiếp chạy; câu lỗi không có đường dẫn |
| T5 | Tên ảnh AI: (a) "MidJourney" và kiểu tách đôi, nhánh và gốc; (b) AI → thật giữa gốc và nhánh; (c) cách sửa của Soi Lỗi trên 112 tên thư mục thật kiểu Pro-Metal; (d) A3 | (a) 12 tên viết hoa giữa chữ (thư mục, gốc) và 6 tên tách đôi (thư mục, file, gốc) là ảnh thật, nhánh và gốc như nhau (LC-T074-1); (b) 0 / 2.180; (c) 0 / 112 đổi; (d) đạt |
| T6 | Cách sửa thử LC-T074-1 (cách của Soi Lỗi + 4 dạng tách đôi) trên bản sao cây nhánh | 5 file test (`test_la_chan_t074`, `test_soi_loi_t074`, `test_images_tags`, `test_soi_loi_t070`, `test_soi_loi_t052`): 38 `XPASS(strict)` đúng các ca LC-T074-1 và SL-T074-2, 836 passed, 8 xfailed (SL-T070-4 ×7, SL-T074-1), 0 hỏng khác. 60.336 tên (20.112 tên × gõ thường/không dấu/viết liền CamelCase): chỉ tên có cặp chữ tiếng Anh tương ứng và "SoRa" đổi sang AI; 112 tên thật: 0 |
| T7 | Suy luận "chỉ mục không khớp bảng" của Thợ Máy, kiểu Soi Lỗi chưa thử: sửa byte đổi `rowid` 2 → 3 trong bảng, chỉ mục vẫn trỏ 2 | `quick_check` "ok", `integrity_check` báo "row 2 missing from index"; `_is_healthy` = True. `get` ảnh đó báo "bị lỗi"; `resolve_many` trang có ảnh đó trả thẻ đọc từ tên thư mục kèm câu lỗi cho **cả trang**; ảnh khác, `list_manual`, `set` ảnh khác vẫn chạy. Lần **lưu lại** ảnh đó gỡ được lỗi (`list_manual` thấy thêm một dòng cũ mồ côi); `clear_all` gỡ hẳn (`integrity_check` "ok"). **Không kẹt mãi**, không chạy SQL lạ, không lộ chữ |
| T8 | Cờ trong phần đầu file: định dạng cấu trúc 5 (byte 44); "chỉ bản mới hơn được ghi" (byte 18 = 3); "… được đọc" (byte 19 = 3) | Byte 44: "unsupported file format" (mã 1), `_is_healthy` ném lại; byte 18: file chỉ đọc, `_is_healthy` = True: cả hai báo "Không mở được file lưu thẻ ảnh…" ở mọi lần, **không** đổi tên file, ảnh vẫn dùng thẻ từ tên thư mục. Byte 19: "không phải cơ sở dữ liệu" → đổi tên, kho dùng lại được |

## Ghi nhận (không thành lỗi)

- **Chỉ mục không khớp bảng (T7)**: có từ trước T-074, phải sửa file ở mức từng byte (chương trình lạ đã chạy được trên máy). Hậu quả chỉ là phần thẻ sửa tay của trang có ảnh đó báo lỗi (ảnh vẫn dùng thẻ đọc từ tên thư mục) tới khi lưu lại ảnh đó hoặc "bỏ mọi thẻ sửa tay"; không kẹt mãi, không chạy SQL lạ. Không cần sửa bây giờ. Nếu muốn chặt hơn (đưa vào nhóm hoãn): khi một thao tác gặp `SQLITE_CORRUPT`, lần kiểm lại dùng `PRAGMA integrity_check` thay cho `quick_check` (chỉ trong trường hợp đó, khỏi chậm lúc thường).
- **Cờ lạ trong phần đầu file (T8)**: kho báo "Không mở được…" mãi, như file có thuộc tính chỉ đọc hay bị chương trình khác giữ khóa; đúng thiết kế "không mở được thì báo lỗi, không xóa" (`image_tags.py:26-28`), cùng mô hình đe dọa. Đưa vào README (T-069) cách gỡ: đóng chương trình khác, hoặc xóa `data/image_tags.sqlite` (chỉ mất thẻ sửa tay).
- **Lời docstring module ở chế độ WAL** (Soi Lỗi đã ghi): `image_tags.py:19-21` nói "chương trình khác không đổi được cấu trúc giữa lúc kiểm và lúc dùng"; ở WAL, chương trình khác **ghi được** trong lúc app đọc, nhưng app vẫn dùng đúng bản đã kiểm (T2). Hệ quả an toàn như nhau; nên sửa lời cho sát ("cấu trúc app dùng luôn là cấu trúc đã kiểm").
- **Giới hạn số bước và độ dài không phải giới hạn thời gian** (Thợ Máy E5): docstring đã ghi đúng mức. Sau T-074 chỉ tới được khi lớp kiểm cấu trúc bị lách; tôi không tìm ra cách lách nào (T1, T1b, T2). Đề xuất hạn giờ thật của Thợ Máy là tùy chọn, không cần ngay.
- **`_is_healthy` đọc thử mọi ô**: chậm gấp đôi trên file lớn nhất (0,64 s, Thợ Máy E4), chỉ khi kho kiểm lại file; đáng đổi vì nếu thiếu, file có một ô quá dài làm kho kẹt mãi.
- **Đánh đổi tên ảnh thật thành ảnh AI** ("mo phong" gõ không dấu, tên file ngẫu nhiên có "ai" kẹp giữa số, 0,03–0,2 %): hướng an toàn, cùng loại đánh đổi "Nha anh Minh Hoa" đã chấp nhận ở T-070.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

Gộp T-074 vào `main` được ngay (Chỉ Huy chạy toàn bộ test khi gộp). Các điều kiện sau Chỉ Huy chép vào phiếu nhận:

1. **Phiếu dọn thẻ ảnh nhỏ** (Chỉ Huy lập số; Thợ Máy; phạm vi `seo_app/images/tags.py`, `seo_app/storage/image_tags.py`, `tests/test_images_tags.py`, gỡ `xfail` ở `tests/test_soi_loi_t074.py` và `tests/test_la_chan_t074.py`). **Phải gộp trước T-056.** Soi Lỗi rút gọn, Lá Chắn rút gọn.
   - **LC-T074-1 (gồm SL-T074-2), bắt buộc:** `_parse_dir_name` đọc thêm kiểu không tách chữ hoa (`… or _has_ai_marker(cleaned, split_case=False)`); thêm `"Mid Journey"`, `"Fire Fly"`, `"Co Pilot"`, `"See Dream"` vào `_AI_TOOLS`. Không ghép bừa mọi cặp chữ liền nhau; giữ ca đối chứng của `tests/test_la_chan_t074.py`.
   - **SL-T074-1, nên làm cùng:** `get_many` đọc hết các dòng trong giao dịch, xử lý sau (như E3b của Soi Lỗi); mọi câu SQL vẫn nằm trong giao dịch đã kiểm.
   - Nên: sửa lời docstring `image_tags.py:19-21` cho đúng với chế độ WAL.
2. **T-056** (giao diện chọn ảnh): giữ mọi điều kiện đã có, thêm:
   - (i) Gọi `resolve_many` theo từng trang (tối đa 200 ảnh), không gọi cho cả lần quét (SL-T074-1).
   - (j) Nút đổi sang ảnh AI: nếu `ImageTagStore.set(…)` báo lỗi (đang bận, file hỏng) thì **trong phiên vẫn coi ảnh đó là ảnh AI** (hướng an toàn) và hiện câu lỗi; không viết alt hay gửi nháp như ảnh thật vì lần lưu hỏng; có test.
   - Trước khi gộp T-056: phiếu dọn ở điều kiện 1 phải gộp.
3. **T-069** (README): gõ tên công cụ tạo ảnh theo cách viết liền chuẩn (Midjourney, Firefly, Copilot, Seedream); nếu app báo mãi "Không mở được file lưu thẻ ảnh…" thì đóng chương trình khác đang mở file, hoặc xóa `data/image_tags.sqlite` (chỉ mất thẻ sửa tay).
4. **D1 (không do T-074):** `certifi` (LC-T061-1, Cao) vẫn đang trên `main`; T-075 cần gộp sớm (đã là điều kiện trước T-056).

## Kết luận

**ĐẠT CÓ ĐIỀU KIỆN.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình; 1 Thấp (LC-T074-1, gồm SL-T074-2 và kiểu tách đôi tôi tìm thêm; có từ trước T-074, `main` y như vậy). Trọng tâm của phiếu đạt: LC-T070-1 và LC-T070-2 đã đóng, có thử lại bằng chính T1, T2 của biên bản T-070 cộng biến thể mới, có đối chứng bản cũ; lỗi giữa giao dịch không để khóa treo; file lạ đổi tên đúng chỗ, giữ nguyên. SL-T070-2, -3, -5 đóng, không kéo lùi chiều ảnh AI → ảnh thật. A3, F1, F3 đạt. SL-T074-1 đồng ý Thấp (hiệu năng). Gộp `main` được ngay: không xung đột, test liên quan qua trên cây gộp; LC-T074-1 phải sửa ở phiếu dọn nhỏ trước T-056.

Chưa chạy: ca symlink trên Windows này (điều kiện T-063), thử trên Mac. Biên bản chạy tạm bằng Claude Opus 5.5; **kiểm lại bằng Claude Fable sau 01/11**.

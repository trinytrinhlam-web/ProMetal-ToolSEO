# Báo cáo T-074 · Dọn thẻ ảnh lượt 2 (sau T-070) · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-074](../tickets/T-074-don-the-anh-luot-2.md) |
| Ngày nộp | 2026-10-21 |
| Kết quả | Hoàn thành (kiểm rút gọn). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn rút gọn được |

## Tóm tắt (cho chủ dự án)

Bản sửa của Thợ Máy làm đúng cả 6 yêu cầu của phiếu. Tôi thử lại đúng các cách lách mà tôi và Lá Chắn tìm ra ở T-070, cộng thêm các kiểu khó hơn (chương trình lạ kiên nhẫn chờ tới lượt để chen vào, file ở chế độ ghi "WAL", sửa mục lục file theo 7 kiểu khác nhau): đoạn lệnh giấu trong file không chạy lần nào, file lạ được đổi tên sang một bên (giữ lại) và app tạo file mới. Tên ảnh của máy ảnh, điện thoại, Zalo, Facebook, Viber… và tên tự đặt có số dính liền vẫn là ảnh thật; file thẻ cũ do bản T-070 ghi vẫn mở được, mở ra đọc không làm đổi file.

Tôi ghi **2 lỗi, đều mức Thấp**, cả hai sửa nhỏ (tôi đã thử từng cách sửa trên bản sao: hết lỗi, mọi test khác vẫn qua), nên sửa trước hoặc cùng màn hình chọn ảnh T-056:

- **SL-T074-1:** khi một tab (hay một cửa sổ app khác) đang đọc thẻ của **rất nhiều** ảnh đã sửa thẻ tay cùng lúc, lần lưu thẻ ở tab kia phải chờ tới khi đọc xong; đọc lâu quá 5 giây thì lần lưu báo "đang bận, thử lại sau". Bản cũ không bị. Chỉ gặp khi một lần đọc có hàng nghìn ảnh đã sửa thẻ tay (một trang chọn ảnh tối đa 200 ảnh thì chỉ chờ thêm dưới 1 giây); không mất dữ liệu.
- **SL-T074-2** (Lá Chắn T-055 thấy trên `main`, Chỉ Huy giao tôi kiểm thêm; có từ trước T-074, nhánh này chưa sửa): thư mục ảnh AI đặt tên công cụ viết hoa giữa chữ, như "MidJourney", "FireFly", "CoPilot", "SeeDream", vẫn bị coi là **ảnh thật**, giữ mã công trình, khu vực, trước/sau. Viết "Midjourney", "midjourney", "MIDJOURNEY" thì đúng; tên **file** viết kiểu nào cũng đúng.

Hôm nay chưa màn hình nào dùng phần này, nên không chặn.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t074.py` | Mới: 147 ca (128 qua, 19 `xfail(strict=True)`: 1 ca SL-T074-1, 18 ca SL-T074-2) |
| `docs/team/reports/T-074-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của người khác.

## Bằng chứng

Máy Windows 11 Pro của chủ dự án, Python 3.12.15, SQLite 3.53.1, worktree `wt-T-074`, nhánh `team/T-074` (code của Thợ Máy tại `8ce0117`, không đổi). Máy đang chạy song song các agent khác.

```
$ uv run pytest tests/test_images_tags.py tests/test_soi_loi_t052.py tests/test_soi_loi_t070.py \
    tests/test_images_folders.py tests/test_ai_images.py -q -p no:cacheprovider -rsx
(2026-10-21 10:23–10:25 +07, trước khi thêm file của tôi)
1087 passed, 8 skipped, 7 xfailed in 98.15s

$ uv run pytest <5 file trên> tests/test_soi_loi_t074.py -q -p no:cacheprovider -rsx
(2026-10-21 10:59–11:02 +07, có file của tôi)
1203 passed, 8 skipped, 8 xfailed in 184.48s (0:03:04)

$ uv run pytest tests/test_soi_loi_t074.py -q -p no:cacheprovider
(11:04, sau khi đổi một tên hex để detect-secrets không báo nhầm)
116 passed, 1 xfailed in 6.21s

$ uv run pytest <5 file trên> tests/test_soi_loi_t074.py -q -p no:cacheprovider -rsx
(11:13–11:14, sau khi thêm test SL-T074-2)
1215 passed, 8 skipped, 26 xfailed in 65.61s (0:01:05)

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan tests/test_soi_loi_t074.py docs/team/reports/T-074-soi-loi.md
0 mục   (file mồi có chữ tiếng Việt trong thư mục nháp: bắt đủ 2/2, đã xóa)
```

- 0 hỏng. Lượt đầu khớp số của Thợ Máy (1087 qua, 8 bỏ qua, 7 xfail); lượt cuối thêm đúng 128 qua và 19 xfail của tôi. 8 bỏ qua như cũ (2 ca symlink của T-052, 6 ca của T-048: Windows chưa bật Developer Mode, hoặc chỉ chạy trên Mac/Linux). 26 xfail = 7 ca SL-T070-4 (đã hoãn, đúng phiếu) + 1 ca SL-T074-1 + 18 ca SL-T074-2.
- **Đối chứng trên code cũ:** chạy file test của tôi trên `seo_app` của `da87dbf` (dựng bằng `git archive`, `PYTHONPATH` trỏ vào đó): 3 test thử T2 mới **hỏng** (trigger chạy, khu vực đọc lại ra "Quận 1"), test SL-T074-1 **qua** (bản cũ không giữ khóa khi xử lý). Nghĩa là test bắt được đúng lỗi LC-T070-2 cũ và SL-T074-1 đúng là do T-074 gây ra. (2 test khác hỏng chỉ vì bản cũ chưa có tham số `write=` của `_connect`.)
- **Thử cách sửa SL-T074-1** trên bản sao (thư mục nháp, không đụng worktree): `get_many` đọc hết các dòng trong giao dịch rồi mới xử lý sau. Chạy `test_soi_loi_t074.py`, `test_images_tags.py`, `test_soi_loi_t070.py`, `test_soi_loi_t052.py`: **816 passed, 2 skipped, 7 xfailed**, test SL-T074-1 thành `XPASS(strict)`.
- **Thử cách sửa SL-T074-2** trên bản sao riêng: tên thư mục đọc thêm kiểu không tách chữ hoa (như tên file). Cùng 4 file test: **828 passed, 2 skipped, 8 xfailed**, chỉ đúng 18 ca SL-T074-2 thành `XPASS(strict)`; 20.000 tên thư mục tiếng Việt ngẫu nhiên và 42 tên viết liền kiểu "CongSatQuan7", "NhaChiMai", "CuaSoRaBanCong", "QuanCafeFlux": **0** tên đổi kết quả (E11).

## Kiểm từng yêu cầu của phiếu

| YC | Kết quả | Bằng chứng |
|---|---|---|
| 1 · LC-T070-1 (= SL-T070-1): dòng lặp trong `sqlite_master` | **ĐẠT** | `_app_tables` đọc vào danh sách, quá 4 dòng hay trùng `(loại, tên)` thì `None` (`seo_app/storage/image_tags.py:598-602`). Thử T1 của Lá Chắn (lặp `sqlite_autoindex_info_1` + trigger) và kiểu của tôi ở T-070 (lặp `…manual_tags_1` + trigger): `_is_healthy` = False, lưu "Tân Phú" đọc lại đúng "Tân Phú" (2 lần tạo kho), file lạ đổi tên, giữ nguyên từng byte (E1). 3 test SL-T070-1 nay qua. Thêm 5 biến thể (E1, 4 thành test `test_master_row_tricks_are_strange_files_and_trigger_never_runs`): lặp viết khác hoa/thường, thay dòng chỉ mục bằng trigger để giữ đúng 4 dòng, trigger mang đúng tên chỉ mục, bỏ bảng `info` lấy chỗ cho dòng lặp và trigger, lặp cả 4 dòng: đều bị bắt |
| 2 · LC-T070-2: kiểm trong cùng giao dịch | **ĐẠT**, có SL-T074-1 (Thấp, hiệu năng) | `_begin` (`:559-565`) trước `_app_tables` ở `_connect` (`:412-417`), `_prepare` (`:455-457`, trước `CREATE`/`INSERT`), `_is_healthy` (`:628-631`). Thử T2 như Lá Chắn (kẻ tấn công không chờ): 4/4 lần "database is locked" (E2). **Biến thể mới** (E2, thành 3 test): kẻ tấn công **chờ khóa** (busy timeout 10 giây) chỉ thêm được trigger sau khi lần lưu xong, trigger không chạy trong lần lưu, lần sau app bắt được (chế độ nhật ký thường và WAL); file ở chế độ **WAL**: lần lưu chặn được kẻ tấn công, lần đọc thì WAL cho người khác ghi song song nhưng app vẫn đọc đúng bản đã kiểm, lần lưu sau bắt được. Chỉ thử bằng script (E2): đổi câu `CREATE` (thêm `CHECK`) ngay giữa `_app_tables` và `quick_check` trong `_is_healthy` (WAL): `quick_check` vẫn chạy trên bản đã kiểm (0,03 s), lần kiểm sau bắt được. File lạ thay vào ngay sau `_is_healthy`: `_prepare` bắt trước khi ghi (`test_file_swapped_right_after_health_check_is_caught_before_create`). Trên code cũ, 3 test T2 mới hỏng (trigger chạy) |
| 3 · SL-T070-2: giới hạn độ dài, `SQLITE_TOOBIG` | **ĐẠT** | `setlimit(SQLITE_LIMIT_LENGTH, 1_000_000)` trong `_guard` (`:547`); `_is_too_big` (`:673-679`) ở `_is_healthy` (`:645`) và `_db_message` (`:687`); `_connect` đặt lại `_ready` với mọi lỗi trừ bận (`:419-425`). Test SL-T070-2 của tôi nay qua. Thêm: câu `CREATE` 1,2 MB thay vào khi app đang chạy: lần đọc báo câu lỗi cố định, đặt lại `_ready`, không để khóa, lần sau đổi tên file (`test_huge_create_statement_swapped_in_while_running_resets_then_recovers`). Docstring đã sửa đúng mức (`:22-25`, `:543-545`: "không phải giới hạn thời gian") |
| 4 · SL-T070-3: tên file tách chỗ chữ ↔ số; "AIgen" | **ĐẠT** (ngoài chữ phiếu còn SL-T074-2, có từ trước) | `split_digits` (`seo_app/images/tags.py:423-451`), tên file gọi `_has_ai_marker(…, split_case=False)` (`:939`), "AIgen" (`:278`). 8 ca SL-T070-3 của tôi nay qua; "xAI3kQ" vẫn là ảnh thật. Ảnh thật không bị kéo theo: xem mục "Ảnh thật bị nhận nhầm" dưới. Tên công cụ viết hoa giữa chữ ở **tên thư mục** ("MidJourney"): SL-T074-2 |
| 5 · SL-T070-5: "mô phỏng" | **ĐẠT** | `_AI_PHRASES` (`:270`); 3 ca SL-T070-5 nay qua; 12 tên thư mục gần nghĩa ("Cửa phòng ngủ", "Mô tơ cổng cuốn", "Mô hình cổng", "Nhà chị Mơ", "Ảnh dựng khung", có dấu và không dấu) vẫn là ảnh thật (`test_folders_near_simulated_stay_real`) |
| 6 · Gỡ `xfail` khi XPASS, không đổi điều kiện | **ĐẠT** | Mục "Soát test" dưới |

### Soát test (`git diff da87dbf..team/T-074 -- tests/`)

- `tests/test_soi_loi_t070.py`: `0 dòng thêm, 44 dòng xóa` (`git diff --numstat`); lọc các dòng xóa trừ dòng thuộc khối `@pytest.mark.xfail(…)` (`xfail`, `strict=True`, `reason=(`, chuỗi lý do, `raises=AssertionError`, dấu đóng): **không còn dòng nào**. Đúng 6 khối: SL-T070-1 ×3, -2, -3, -5. Khối của SL-T070-4 (7 ca) giữ nguyên, vẫn XFAIL.
- `tests/test_images_tags.py`: 400 dòng thêm, 4 dòng xóa: 1 dòng import (viết lại thành nhiều dòng để thêm `MAX_REL_PATH_CHARS`; thêm `import threading`), 3 dòng của `test_t070_schema_is_read_before_any_other_query`. Không test cũ nào khác bị sửa hay xóa. **Không làm yếu điều kiện:** bản cũ kiểm câu đầu tiên sau giới hạn số bước là `[master, CREATE, master, master]`; bản mới kiểm câu đầu là `[BEGIN, BEGIN IMMEDIATE, BEGIN, BEGIN IMMEDIATE]` (đúng loại giao dịch cho từng kết nối: kiểm file đọc, tạo bảng ghi, `get` đọc, `set` ghi), câu kế là `sqlite_master` ở cả 4 kết nối, và ở kết nối tạo bảng `CREATE` đứng **sau** câu kiểm. `BEGIN` không đọc gì của file (SQLite chỉ nạp cấu trúc khi chạy câu đọc đầu tiên), nên `sqlite_master` vẫn là câu đọc đầu tiên: chặt hơn bản cũ (thêm kiểm `_prepare` và loại giao dịch).

### Tìm lỗi mới do thay đổi gây ra

**Giao dịch, khóa, nhiều tab** (E3, E6; bản cũ `da87dbf` nạp từ `git show`, chạy xen kẽ với bản mới):

| Thử | Bản cũ | Bản mới |
|---|---|---|
| `get_many` N ảnh đều có thẻ sửa tay (thời gian, máy đang tải) | N = 100: 0,17 s; 500: 0,79 s; 2.000: 3,3 s; 5.000: 8,4 s | như bản cũ (0,16 / 0,92 / 3,2 / 8,5 s) |
| 1 luồng đọc `get_many(N)` liên tục + 1 luồng lưu 10 thẻ | N = 500 / 2.000 / 5.000 / 10.000: chờ lâu nhất 0,96 / 1,59 / 1,28 / 4,71 s, **0 lỗi** | chờ lâu nhất 1,65 / 5,47 / 11,3 / 7,6 s; **N = 5.000: 4/10 lần lưu báo "đang bận"; N = 10.000: 7/10** |
| 2 tiến trình đọc `resolve_many(N)` + 1 tiến trình lưu, 20 giây (như 3 cửa sổ app) | N = 2.000: lưu 48 lần, chờ lâu nhất 2,5 s, 0 lỗi; N = 5.000: lưu 50 lần, 0 lỗi | N = 2.000: lưu chỉ 9 lần, chờ lâu nhất 6,3 s, 1 lần lưu và 1 lần đọc "đang bận"; N = 5.000: lưu 5 lần, **3/5 báo "đang bận"**, 1 lần đọc ra thẻ từ tên thư mục kèm câu lỗi |
| Như dòng 2, chạy lại so bản mới với **bản sửa thử** SL-T074-1 (E3b) | | bản mới N = 2.000 / 5.000: chờ lâu nhất 5,56 / 6,64 s, 0 / 2 lỗi; **bản sửa thử: 1,03 / 2,44 s, 0 lỗi** |
| Thử T-074 (Thợ Máy, E7): 4 luồng × 15 vòng, trang 2 ảnh | không lỗi | không lỗi (chạy lại trong bộ test: qua) |

Kết luận: không kẹt vĩnh viễn, không khóa chết (giao dịch đọc không bao giờ xin quyền ghi; giao dịch ghi xin quyền ghi ngay từ `BEGIN IMMEDIATE`), nhưng giao dịch đọc nay giữ khóa suốt phần xử lý Python của `get_many`, nên lần lưu ở tab khác phải chờ hết: **SL-T074-1**. `list_manual` không bị (xử lý dòng sau khi đóng kết nối, `image_tags.py:358-371`).

**Lỗi giữa thao tác có để giao dịch mở không** (E4; 7 ca test): lỗi Python và lỗi kiểu dừng ngang (`BaseException`, như Ctrl+C) khi đang xử lý dòng đọc được; lỗi giữa giao dịch ghi; chạy quá số bước trong giao dịch ghi; cấu trúc lạ bắt được ở `_connect`; cấu trúc lạ bắt được ở `_prepare`; câu `CREATE` khổng lồ: sau mỗi lỗi, kết nối khác (không chờ) lấy ngay được khóa ghi độc quyền (`BEGIN EXCLUSIVE`), lần ghi dở bị hoàn tác (khu vực vẫn "Quận 7"). Chỉ thử bằng script: commit bị chặn bởi khóa đọc của chương trình khác giữ quá 5 giây: lần lưu báo "đang bận" (sau 7,6 giây trên máy đang tải), không ghi dở, khóa được nhả. Mỗi thao tác dùng kết nối riêng và luôn đóng (`closing`), nên giao dịch không thể sống quá thao tác.

**Ảnh thật bị nhận nhầm là ảnh AI** (E5, E9; so bản cũ và bản mới trên cùng tên):

| Loại tên (20.000 tên mỗi loại, tạo ngẫu nhiên theo mẫu) | Nay là ảnh AI | Đổi thật → AI so với bản cũ |
|---|---|---|
| 83 mẫu tên máy ảnh, điện thoại, ứng dụng chat, phần mềm sửa ảnh (IMG_…, PXL_…, DSC…, DJI_…, Screenshot_…_Zalo, z…_<hex>, FB_IMG_…, received_…, viber_image_…, mmexport…, Ảnh chụp màn hình…, UUID, hex…) | **0** | 0 |
| Tên công trình tiếng Việt ghép ngẫu nhiên, có/không dấu, có số dính liền | 1.092 | 657, **đều do cụm không dấu "mo phong"** mà tôi cố tình cài vào bộ tên ("Cua mo phong", "Anh mo phong khach", tên "Mơ" đứng trước "Phong Phú"); kiểm lại trên bộ 20.000 tên khác (E5b): 648 tên file, 670 tên thư mục đổi, **0** tên đổi vì lý do khác; xem Ghi nhận |
| Chuỗi ngẫu nhiên chữ hoa/thường/số (base62) dài 6–32 | 0,03–0,12 % | như cột trái (bản cũ 0) |
| Chuỗi ngẫu nhiên chữ thường/số (base36) dài 8–20 | 0,03–0,2 % | như cột trái |

95 tên file và 18 tên thư mục cụ thể (máy ảnh, điện thoại, Zalo, tên người đặt dính số như "nha-chi-Mai2", "Hai3", "TRAI2", "cong2canh", "Cổng2cánh", "Mộ Phong") đều là ảnh thật ở cả hai bản; 89 tên file và 12 tên thư mục đưa vào test (`test_real_photo_file_names_stay_real_after_digit_split`, `test_folders_near_simulated_stay_real`). Đánh đổi với tên ngẫu nhiên khớp số Thợ Máy đã báo (0,05–0,1 %); hướng an toàn (ảnh chỉ mất thẻ công trình).

**File thẻ cũ của T-070** (E4, thành test): file do bản `da87dbf` tạo (4 thẻ: có dấu, ảnh AI, đường dẫn dài, thẻ xóa rồi lưu lại) mở bằng bản mới: `_is_healthy` = True, đọc đủ 4 thẻ đúng giá trị, liệt kê 4, không đổi tên, mở và đọc **không đổi một byte** của file, lưu thẻ mới được. Chiều ngược lại (file bản mới, mở bằng bản cũ) cũng vậy. Test `test_file_written_by_t070_is_accepted_and_reads_do_not_rewrite_it` dựng file bằng câu `CREATE` chép nguyên văn từ `da87dbf`. File chỉ đọc (thuộc tính read-only): bản cũ và bản mới như nhau (không mở được để ghi, ảnh dùng thẻ từ tên thư mục kèm câu báo).

## Lỗi mới

| Mã | Mức | Chỗ | Tóm tắt |
|---|---|---|---|
| SL-T074-1 | Thấp (YC2, hiệu năng) | `seo_app/storage/image_tags.py:263-280` (`get_many`) | Giao dịch đọc giữ khóa suốt phần xử lý Python từng dòng; lần lưu ở tab khác chờ hết, đọc quá 5 giây thì lần lưu (và cả lần đọc mới) báo "đang bận" |
| SL-T074-2 | Thấp (LC-T052-1 còn sót; có từ trước T-074) | `seo_app/images/tags.py:855` (`_parse_dir_name`), dùng ở `is_ai_name` (`:973`) | Tên công cụ AI một từ viết hoa giữa chữ trong **tên thư mục** ("MidJourney", "FireFly", "CoPilot") không nhận là ảnh AI |

#### SL-T074-1 · Thấp · `get_many` giữ khóa đọc suốt phần xử lý từng dòng

- **Tái hiện:** kho có N ảnh đã sửa thẻ tay; luồng (hay tiến trình) A gọi `get_many`/`resolve_many` cho N ảnh đó; trong lúc A đang chạy, luồng B gọi `set` cho một ảnh khác. Script `e3_lock_hold.py`, `e6_two_processes.py` (thư mục ghi chú chung, mục Đề xuất).
- **Mong đợi:** như bản cũ: B chỉ phải chờ phần đọc file (vài chục mili giây), không chờ phần xử lý Python của A; không báo "đang bận".
- **Thực tế:** từ T-074, `_connect` mở `BEGIN` và giữ giao dịch tới hết khối `with self._connect() as conn:`; `get_many` gọi `_row_to_tag` và `tags_for_image` (khoảng 1,6 ms mỗi dòng trên máy đang tải) **bên trong** khối đó (`:263-280`). Khóa đọc giữ suốt thời gian này, nên lần commit của B (cần khóa độc quyền) phải chờ hết; trong lúc B chờ, SQLite chặn luôn các lần đọc mới. Đọc quá 5 giây (`_SQLITE_TIMEOUT`) thì B nhận "File lưu thẻ ảnh đang bận…" (số đo ở bảng trên: N = 5.000, 4/10 lần lưu; 2 tiến trình đọc + 1 tiến trình lưu, 3/5 lần lưu và 1 lần đọc). Bản cũ chạy cùng kịch bản: 0 lỗi.
- **Vì sao Thấp:** không mất dữ liệu, không ghi dở, câu báo đúng ("thử lại sau"), lớp an toàn không bị ảnh hưởng; chỉ xảy ra khi một lần đọc có hàng nghìn ảnh đã sửa thẻ tay **và** có lần lưu cùng lúc ở tab/cửa sổ khác. Trang ảnh của T-048 tối đa 200 mục (`MAX_PAGE_SIZE`, `folders.py:46`): đọc 200 ảnh đều có thẻ tay mất khoảng 0,35 s, lần lưu chỉ chờ thêm chừng đó. Hôm nay chưa màn hình nào gọi phần này.
- **Gợi ý sửa (Thợ Máy):** trong `get_many`, chỉ đọc các dòng (`fetchall` từng nhóm) trong khối `with self._connect()`, ra khỏi khối rồi mới `_row_to_tag` và `tags_for_image`, giống `list_manual` đang làm. Kiểm và đọc vẫn nằm trong cùng giao dịch (LC-T070-2 giữ nguyên), sau đó không còn câu SQL nào chạy. Tôi đã thử đúng cách này trên bản sao (khoảng 10 dòng): test SL-T074-1 XPASS, 816 test liên quan khác qua; cùng kịch bản 1 luồng đọc + 1 luồng lưu, N = 5.000: lần lưu chờ lâu nhất 2,44 s, 0 lỗi (bản hiện tại 6,64 s, 2/10 lỗi).
- **Test:** `test_sl_t074_1_save_in_other_tab_does_not_wait_for_row_processing` (`tests/test_soi_loi_t074.py:531`): lúc `get_many` bắt đầu xử lý dòng đã đọc, "tab khác" (kết nối riêng, không chờ) lưu một thẻ thật và commit. Bản mới: "database is locked" (XFAIL); bản cũ và bản sửa thử: lưu được. Không phụ thuộc thời gian, chạy dưới 1 giây.

#### SL-T074-2 · Thấp · Tên công cụ AI viết hoa giữa chữ trong tên thư mục là ảnh thật

- **Nguồn:** Lá Chắn T-055 thấy trên `main` ("MidJourney" ra ảnh thật, "midjourney" ra ảnh AI); Chỉ Huy B giao kiểm trên nhánh này.
- **Tái hiện:** `tags_for_image(ImageRef(0, "CT012 - Cổng inox - Quận 7/truoc/MidJourney/IMG_0001.jpg"))`; tương tự "Ảnh MidJourney", "MidJourney V6", "FireFly", "Adobe FireFly", "SeeDream", "HaiLuo", "JiMeng", "CoPilot", "IdeoGram", "ReCraft", "RunWay"; `is_ai_name("G:/My Drive/MidJourney")`.
- **Mong đợi:** ảnh AI, chỉ giữ hạng mục (như "Midjourney", "midjourney", "MIDJOURNEY" đang đúng); `is_ai_name` = True.
- **Thực tế:** ảnh **thật**, giữ CT012, Quận 7, trước; `is_ai_name` = False. Tên thư mục chỉ đọc kiểu **tách theo chữ hoa** (`_parse_dir_name`, `tags.py:855`: `split_case=True`, để nhận "ẢnhAI", "GenAI"), nên "MidJourney" thành hai từ "mid journey", không khớp dấu hiệu một từ "midjourney". Dấu hiệu **nhiều từ** thì không bị ("ChatGpt", "NightCafe", "StableDiffusion", "ComfyUi", "NanoBanana" đều đúng, vì dấu hiệu có sẵn dạng tách). Thử hệ thống (E10): mọi dấu hiệu một từ dài từ 4 chữ, viết hoa thêm **một** chữ ở mọi vị trí: **118/155 kiểu sai ở tên thư mục, 0/155 sai ở tên file** (tên file không tách theo chữ hoa). Viết thường, VIẾT HOA, Hoa đầu, như danh sách: không kiểu nào sai. Trên `main` (`da87dbf`) y như vậy: T-074 không gây ra, cũng không chạm phần này.
- **Vì sao Thấp:** hướng **không** an toàn (ảnh AI mang thẻ công trình thật, có thể bị giới thiệu như ảnh chụp công trình), cùng loại SL-T070-3 ("AI01.png") và SL-T070-5 ("Ảnh mô phỏng") mà Soi Lỗi và Lá Chắn T-070 xếp Thấp: chỉ một số kiểu gõ tên, và T-056 phải hiện "Ảnh thật / Ảnh AI" cho người duyệt (điều kiện 2b của Lá Chắn T-052). "MidJourney" là kiểu gõ sai khá phổ biến, nên nên sửa **trước T-056**. Không lộ chữ nào (A3 giữ).
- **Gợi ý sửa (Thợ Máy):** trong `_parse_dir_name`, coi là ảnh AI khi **một trong hai** cách đọc có dấu hiệu: `_has_ai_marker(cleaned, split_case=True) or _has_ai_marker(cleaned, split_case=False)` (cách thứ hai chính là cách đọc tên file, vẫn tách chỗ chữ dính số). `is_ai_name` dùng `_parse_dir_name` nên tự đúng theo. Tôi thử đúng cách này trên bản sao (E11): 18 ca SL-T074-2 XPASS, 828 test khác qua, 0 tên thư mục thật đổi kết quả.
- **Test:** `test_sl_t074_2_camel_case_tool_name_in_folder_is_ai` (13 ca), `test_sl_t074_2_camel_case_tool_name_as_root_folder_is_ai` (5 ca, `is_ai_name`), XFAIL (`tests/test_soi_loi_t074.py:576-598`). Đối chứng đang qua: cùng các tên ở tên file (`test_camel_case_tool_name_in_file_name_is_ai`, 5 ca) và ở kiểu viết thường gặp (`test_tool_name_in_usual_case_in_folder_is_ai`, 7 ca).

## Ghi nhận (không thành lỗi)

- **"mo phong" gõ không dấu thành ảnh AI.** Như mọi dấu hiệu khác, "mô phỏng" tự có dạng không dấu, nên tên **gõ không dấu** có hai chữ "mo" rồi "phong" liền nhau là ảnh AI: "Cua mo phong ngu" (cửa mở phòng ngủ), "Anh mo phong khach" (ảnh mờ phòng khách), "Nha chi Mo - Phong Phu" (chị Mơ, xã Phong Phú). Cùng loại đánh đổi Lá Chắn T-070 đã chấp nhận cho "Nha anh Minh Hoa" (hướng an toàn: ảnh chỉ mất thẻ công trình). Gõ có dấu thì không sao ("Cửa mở phòng ngủ", "Nhà chị Mơ" là ảnh thật, có test). Đưa vào README (T-069): gõ tên thư mục ảnh thật có dấu.
- **Tên file ngẫu nhiên** (chữ và số trộn, như ảnh tải từ web) bị coi là ảnh AI 0,03–0,2 % (có "ai", "gpt", "oig", "krea" kẹp giữa số). Khớp đánh đổi Thợ Máy đã báo; tên của máy ảnh, điện thoại, Zalo không bị.
- **`get_many` vốn đã chậm** với rất nhiều ảnh có thẻ tay (khoảng 1,6 ms mỗi ảnh trên máy đang tải, như nhau ở bản cũ và bản mới). T-056 nên gọi `resolve_many` theo từng trang (tối đa 200 ảnh), không gọi cho cả lần quét (tới 5.000 ảnh).
- **Suy luận "chỉ mục không khớp bảng" của Thợ Máy** (ngoài phạm vi, có từ trước T-074, cho Lá Chắn cân nhắc): tôi thử tráo `rootpage` hai chỉ mục tự sinh (`writable_schema`). Số mục hai chỉ mục khác nhau thì `quick_check` bắt được ("wrong # of entries"), file bị đổi tên. Số mục bằng nhau (mỗi bảng 1 dòng) thì `quick_check` ra "ok", `_is_healthy` = True; hậu quả: một thẻ sửa tay đọc không ra, lần lưu sau tạo dòng trùng khóa; kho **không kẹt**, không báo lỗi, không chạy SQL lạ (E8). Cùng mô hình đe dọa (chương trình lạ trên máy), mức Thấp hoặc thấp hơn; `integrity_check` bắt được nhưng chậm hơn.
- **Lời docstring module** (`image_tags.py:19-20`): "chương trình khác không đổi được cấu trúc giữa lúc kiểm và lúc dùng" đúng với chế độ nhật ký thường app dùng; ở chế độ WAL, chương trình khác **ghi được** trong lúc app đọc nhưng app vẫn đọc trên bản đã kiểm (docstring `_begin` đã nói "ảnh chụp ở chế độ WAL"). Hệ quả an toàn như nhau; nếu sửa SL-T074-1 thì tiện sửa lời cho sát.

## Đối chiếu tiêu chí xong (phần Soi Lỗi kiểm)

- [x] YC1: thử T1 của Lá Chắn và kiểu của Soi Lỗi T-070, thêm 5 biến thể (E1; 4 ca test mới); 3 test SL-T070-1 qua
- [x] YC2: thử T2 của Lá Chắn, kẻ tấn công chờ khóa, file WAL, đổi cấu trúc giữa hai bước kiểm (E2; 4 ca test mới); còn SL-T074-1 (Thấp, hiệu năng, không phải lỗ an toàn)
- [x] YC3: giới hạn độ dài, `SQLITE_TOOBIG` là hỏng, đặt lại `_ready`, docstring; thêm ca câu `CREATE` khổng lồ thay vào khi đang chạy
- [x] YC4, YC5: tên file tách chữ ↔ số, "AIgen", "mô phỏng"; ảnh thật không bị kéo theo (E5, E9; 101 ca test mới)
- [x] Ca Chỉ Huy giao thêm ("MidJourney", Lá Chắn T-055): còn ở tên thư mục và `is_ai_name`, không còn ở tên file → SL-T074-2 (E10; 18 ca `xfail`, 12 ca đối chứng)
- [x] YC6: `test_soi_loi_t070.py` chỉ gỡ 6 khối `xfail`; test T-070 của Thợ Máy sửa kỳ vọng không làm yếu điều kiện
- [x] Lỗi giữa thao tác không để giao dịch mở (7 ca test mới); file thẻ T-070 mở được (1 test mới)
- [x] Test liên quan qua, `ruff check .` sạch

## Rủi ro và điểm cần chú ý

- Số đo thời gian (E3, E6) lấy trên máy đang chạy song song các agent khác và một lượt pytest toàn bộ: con số tuyệt đối chậm hơn máy rảnh, nhưng bản cũ và bản mới chạy xen kẽ trong cùng điều kiện nên phép so vẫn đúng. Test SL-T074-1 không dựa vào thời gian.
- Test thử T2 "kẻ tấn công chờ khóa" có một lần ngủ 0,3 giây trong lúc app giữ giao dịch (để kẻ tấn công kịp chen vào); máy chậm đến mấy thì kết quả vẫn đúng (kẻ tấn công vào sau, trigger không chạy trong lần lưu), chỉ có thể chậm thêm.
- Ca symlink vẫn bỏ qua trên máy này (điều kiện T-063, như T-070). Chưa thử hai tiến trình trên Mac.

## Đề xuất

- **Thợ Máy (Chỉ Huy chọn: phiếu nhỏ trước T-056, hoặc gộp vào T-056):** sửa SL-T074-1 như gợi ý (đọc dòng trong giao dịch, xử lý sau) và SL-T074-2 (tên thư mục đọc thêm kiểu không tách chữ hoa, 1 dòng); gỡ `xfail` khi XPASS. Hai cách sửa độc lập, mỗi cách đã thử riêng trên bản sao.
- **T-056:** gọi `resolve_many` theo trang (tối đa 200 ảnh), không cho cả lần quét.
- **T-069 (README):** gõ tên thư mục ảnh thật có dấu (thêm "mô phỏng" vào danh sách chữ làm ảnh thành ảnh AI, như Thợ Máy đề xuất).
- **Lá Chắn (rút gọn):** cân nhắc mục "chỉ mục không khớp bảng" ở Ghi nhận (có từ trước, ngoài phiếu). Script tái hiện (E1–E6, E8–E11, kèm E3b, E5b, E8b) và kết quả: thư mục ghi chú chung của nhóm phiên, `T-074-soi-loi-scripts/` (chạy bằng `PYTHONUTF8=1 uv run python <script>` trong worktree; E3, E4, E6 cần tham số là `image_tags.py` bản cũ, E5, E5b, E9, E10 cần `tags.py` bản cũ, lấy bằng `git show da87dbf:…`; E3b, E11 cần bản sửa thử, có sẵn dạng diff cạnh script).

## Câu hỏi cho chủ dự án

Không có.

## Kết luận

**ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn rút gọn được. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **2 Thấp** (SL-T074-1 do T-074 gây ra; SL-T074-2 có từ trước, Lá Chắn T-055 tìm ra). Cả 6 yêu cầu của phiếu đạt; LC-T070-1, LC-T070-2, SL-T070-1, -2, -3, -5 đã sửa thật (test cũ gỡ `xfail` qua bằng chính điều kiện cũ, test mới của tôi trên code cũ hỏng đúng chỗ).

Điều kiện: SL-T074-1 và SL-T074-2 sửa trước hoặc cùng T-056 (cả hai sửa nhỏ, đã thử được); trong lúc chờ, T-056 chỉ gọi `resolve_many` theo trang. Lá Chắn có thể cân lại mức SL-T074-2 (hướng không an toàn, kiểu gõ "MidJourney" khá phổ biến).

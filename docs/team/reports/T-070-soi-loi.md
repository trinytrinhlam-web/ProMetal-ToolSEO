# Báo cáo T-070 · Dọn lỗi thẻ ảnh (sau T-052) · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-070](../tickets/T-070-don-loi-the-anh.md) |
| Ngày nộp | 2026-10-20 |
| Kết quả | Hoàn thành (kiểm rút gọn). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN** chuyển sang Lá Chắn rút gọn |

## Tóm tắt (cho chủ dự án)

Bản sửa của Thợ Máy làm đúng phần lớn việc: các cách gọi ảnh AI hay gặp ("Ảnh minh họa", "trí tuệ nhân tạo", "genai", tên các công cụ tạo ảnh) nay đều được nhận ở mọi kiểu viết (hoa/thường, không dấu, dính số, dính gạch, kiểu Mac); tên khách có dấu ("Minh Hòa", "chị Ái") vẫn là ảnh thật; ba lỗi cũ của tôi ở T-052 nay qua mà không ai đổi điều kiện kiểm.

Tôi tìm thấy **5 lỗi mới, đều mức Thấp**. Đáng sửa nhất: một file thẻ bị làm độc theo một cách khéo (lặp một dòng trong bảng mục lục của file) vẫn **lách qua được lớp kiểm mới**, nên đoạn lệnh giấu trong file vẫn chạy được: sửa thẻ đã lưu, hoặc làm mỗi lần lưu thẻ đứng hơn 10 giây. Muốn làm vậy phải có chương trình lạ chạy trên máy, nên mức Thấp. Bốn lỗi còn lại về tên: một số tên file AI có số dính liền chưa nhận ("AI01.png"); một số tên riêng thật trùng tên công cụ ("Sora Gardens", "Quán Night Cafe") bị coi là ảnh AI mà trong app không sửa lại được.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t070.py` | Mới: 164 ca (142 qua, 22 `xfail` cho 5 lỗi mới SL-T070-1 → -5) |
| `docs/team/reports/T-070-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của người khác.

## Bằng chứng

Máy Windows 11 Pro, Python 3.12.15, SQLite 3.53.1, worktree `wt-T-070`, nhánh `team/T-070` (code của Thợ Máy tại `0d92ff1`). Chỉ chạy test liên quan theo `rules.md`; toàn bộ test do Chỉ Huy chạy khi gộp.

```
$ git diff origin/main...HEAD -- tests/test_soi_loi_t052.py
(chỉ xóa 3 khối @pytest.mark.xfail(...) của SL-T052-9, -10, -11; 24 dòng xóa, 0 dòng thêm,
 không đổi dòng assert, parametrize hay thân test nào)

$ uv run pytest tests/test_soi_loi_t052.py -q -p no:cacheprovider -rsx
56 passed, 1 skipped in 104.81s            (1 bỏ qua: symlink, Windows chưa bật Developer Mode)

$ uv run pytest tests/test_images_tags.py tests/test_soi_loi_t052.py tests/test_soi_loi_t070.py \
    tests/test_images_folders.py tests/test_ai_images.py -q -p no:cacheprovider -rs
(2026-10-20 18:33–18:36 +07, tại 6cfbb91)
1003 passed, 8 skipped, 22 xfailed in 145.51s

$ uv run ruff check .
All checks passed!
```

- **0 hỏng.** So với lượt Thợ Máy (861 qua, 8 bỏ qua): thêm đúng 142 ca qua và 22 `xfail` của tôi. 8 bỏ qua y như cũ (2 symlink T-052, 6 của T-048).
- Lượt chạy chậm hơn lượt Thợ Máy (145 s so với 54 s cho 4 file cũ cộng file mới 18 s). Suy luận: máy đang chạy song song phiên Thợ Máy T-061; không có ca nào hỏng vì thời gian.

## Kết quả theo việc được giao

### 1. Ba `xfail` cũ (SL-T052-9, -10, -11): ĐẠT

Nay qua bằng chính điều kiện cũ (diff ở trên chỉ gỡ dòng `xfail`).

### 2. LC-T052-1 · Tên ảnh AI: đạt phần phiếu yêu cầu, còn 3 lỗi Thấp

Thử thêm, **đúng** (giữ thành test hồi quy trong `tests/test_soi_loi_t070.py`):

- **66 tên thư mục ảnh AI** ngoài danh sách của Thợ Máy, mỗi tên thử ở hai tầng (`test_more_ai_folder_names_are_ai_at_any_depth`): "Hình minh họa", "Minh Hoạ", "anh-minh-hoa", "anh_minh_hoa", "minhhoa01", "Ảnh-minh-họa", NFD; "TRI TUE NHAN TAO", "tri-tue-nhan-tao", "TriTueNhanTao", NFD; "Gen AI", "Gen-AI", "gen_ai", "genai2024", "GenAI-01"; "COPILOT", "designer", "bing", "BingImageCreator", "Leonardo.Ai", "FLUX.1", "flux1", "Flux1-dev", "KLING AI", "Kling2.1", "Comfy UI", "RunwayML", "krea.ai", "seedream4", "Seedream 4.0", "Midjourney6", "NanoBanana", "Imagen3", "DALLE3", "DALL·E", "gpt4o", "StableDiffusion", "sdxl1.0", "Sora", "NightCafe", "SeaArt", "Meta AI", "render 3D", chữ toàn chiều rộng "ＡＩ", chữ toán học "𝐀𝐈"…
- **27 tên file mặc định** (`test_more_default_ai_file_names_are_ai`): "designer (1).jpeg", "OIG1/2/4.jpg", "flux-dev_00001_.png", "FLUX.1-schnell.png", "grok-image-1234.jpg", "ComfyUI_temp_abc_00001_.png", "Gemini_Generated_Image_….png", "ChatGPT Image Mar 15, 2025….png", "DALL·E 2024-03-15 ….webp", "Firefly 2024….png", "GenAI_001.png", "anh-minh-hoa.jpg"…
- **Đối chứng ảnh thật:** 13 tên gần giống ("Imagine Coffee", "Kreative Space", "Fluxion", "Chị Kréa", "AIA Building", "khoai", "Nhà anh Hoà"…) và 9 tên file máy ảnh/Zalo ("PXL_…", "IMG-…-WA0001", "z5432…", "xAI3kQ") vẫn là ảnh thật, giữ đủ thẻ.
- **Không từ nào trong danh sách thẻ** (160 từ: khu vực, hạng mục, trước/sau), có dấu, không dấu hay kèm số, bị coi là dấu hiệu AI (`test_no_word_of_the_tag_lists_is_ever_an_ai_marker`).
- **`is_ai_name`:** chỉ xét tên cuối với đường dẫn Windows, Mac, UNC, dấu gạch cuối; bỏ ký tự vô hình; `None`, `bytes`, số, `ImageRef` → `TypeError`.

Lỗi: SL-T070-3, -4, -5 (bảng dưới).

### 3. LC-T052-2 · File SQLite độc: còn 1 cách lách (SL-T070-1) và 1 khe ở lớp phòng thứ hai (SL-T070-2)

Thử thêm 7 kiểu file lạ ngoài 14 kiểu của Thợ Máy (`test_more_strange_files_are_moved_aside_and_store_recovers`): dòng bảng lặp trong `sqlite_master`, `rootpage` trùng bảng `info` / trỏ trang 1 / bằng 0 / ra ngoài file, có `sqlite_stat1` (sau `ANALYZE`), trigger nằm trong file `-wal` dựng sẵn chưa ghi vào file chính. Tất cả bị nhận là file lạ, đổi tên sang một bên (giữ lại), kho tự tạo file mới và lưu được ngay. File hợp lệ mã UTF-16 hay ở chế độ WAL được giữ, dùng bình thường. File 70 MB chứa 70.000 khung nhìn: `_is_healthy` mất khoảng 7 giây (phân tích cấu trúc không tính vào giới hạn số bước) rồi trả "hỏng"; chỉ một lần, và kho đổi tên file trên 64 MB trước cả bước này.

### 4. LC-T052-3 · `get_many`: ĐẠT

`test_get_many_and_resolve_many_force_ai_per_ref_asked`: thẻ thật (CT012, Quận 7, trước) lưu cho `…/khoai/x.png`; hỏi cùng lúc `khoai`, `KhoAI`, `KHOAI` (cùng khóa): chỉ `KhoAI` ra ảnh AI (chỉ giữ hạng mục), hai ảnh kia giữ thẻ thật; `resolve_many` như vậy; `set(KhoAI, ảnh thật)` bị từ chối.

## Lỗi mới

| Mã | Mức | Chỗ | Tóm tắt |
|---|---|---|---|
| SL-T070-1 | Thấp (F3, YC2) | `image_tags.py:539–544` (`_app_tables`) | Lặp một dòng trong `sqlite_master` đẩy trigger ra ngoài `LIMIT`: file độc qua kiểm, trigger chạy |
| SL-T070-2 | Thấp (F3) | `image_tags.py:497–510` (`_guard`) | Giới hạn số bước không chặn được bước nặng: truy vấn ít bước mà chạy hàng giây/giờ không bị dừng |
| SL-T070-3 | Thấp (YC4) | `tags.py:912` (tên file, `split_case=False`) | Tên file có "AI"/tên công cụ dính số ("AI01.png", "dalle3_…", "Gemini2_…") là ảnh thật |
| SL-T070-4 | Thấp (YC1 "không chặn nhầm") | `tags.py:203–240` (`_AI_TOOLS`), `image_tags.py:271` | Tên riêng thật trùng tên công cụ một từ ("Sora Gardens", "Quán Night Cafe", "Flux Coffee") thành ảnh AI, không sửa lại được trong app |
| SL-T070-5 | Thấp (YC4) | `tags.py:259` (`_AI_PHRASES`) | "Ảnh mô phỏng", "Hình mô phỏng 3D" không nhận là ảnh AI |

#### SL-T070-1 · Thấp · Lách lớp kiểm `sqlite_master` bằng một dòng lặp

- **Tái hiện:** tạo file đúng như app (chính `_CREATE_TABLES`), bật `PRAGMA writable_schema = ON`, chép lại dòng `sqlite_autoindex_manual_tags_1` (thành dòng thứ 5) rồi thêm một trigger `AFTER INSERT ON manual_tags` (dòng thứ 6). Gọi `_is_healthy`, rồi `ImageTagStore.set` và `get`.
- **Mong đợi:** file có trigger là file app không bao giờ tạo, nên `_is_healthy` trả `False`, file bị đổi tên, trigger không bao giờ chạy (YC2: "không VIEW/TRIGGER").
- **Thực tế:** `_app_tables` đọc `LIMIT` = số dòng mong đợi + 1 = 5 dòng và so theo **tập hợp**; dòng lặp gộp vào dòng cũ, trigger ở dòng 6 không được đọc. SQLite chấp nhận dòng lặp, `quick_check` ra `ok`. Kết quả `_is_healthy` = `True`, file giữ nguyên, kể cả khi tạo kho mới (như khởi động lại app):
  - trigger sửa dữ liệu: lưu "Tân Phú" xong đọc lại ra **"Quận 1"**;
  - trigger đệ quy: mỗi lần `set` bị giới hạn số bước dừng (theo số đo của Thợ Máy, khoảng 2 giây với giới hạn thật) rồi báo lỗi, file **không bao giờ** bị đổi tên: kẹt mãi (đúng triệu chứng LC-T052-2 c, d mà phiếu muốn sửa);
  - trigger gọi hàm nặng (40 lần `randomblob` 50 MB): **mỗi lần `set` chạy 11 giây** và không bị dừng (xem SL-T070-2); tăng số lần thì treo hàng giờ.
- **Vì sao Thấp:** cùng mô hình đe dọa với LC-T052-2: phải có chương trình chạy trên máy ghi được vào `data/`. Không lộ dữ liệu, không ghi ra ngoài `data/`, trigger chỉ ghi được giá trị trong danh sách. Nhưng đây là lách **đúng lớp kiểm YC2 yêu cầu**, nên nên sửa trong phiếu này.
- **Gợi ý sửa:** `_app_tables` đọc vào danh sách (không phải tập hợp) và coi là hỏng khi số dòng đọc được lớn hơn số dòng mong đợi, hoặc có dòng trùng (giữ `LIMIT` để không đọc vô hạn).
- **Test:** `test_sl_t070_1_duplicate_master_row_cannot_hide_a_trigger`, `test_sl_t070_1_hidden_trigger_never_changes_saved_tags`, `test_sl_t070_1_hidden_recursive_trigger_does_not_jam_store`. XFAIL.

#### SL-T070-2 · Thấp · Giới hạn số bước không phải giới hạn thời gian

- **Tái hiện:** mở kết nối, gọi `_guard(conn)` (giới hạn thật 50 triệu bước), chạy `SELECT sum(length(randomblob(25000000)))` trên 32 dòng.
- **Mong đợi:** bị dừng hoặc bị từ chối. Docstring module và báo cáo Thợ Máy nói file dựng sẵn "không làm treo app", truy vấn đệ quy "bị dừng sau khoảng 2 giây", và khe "file bị thay giữa lúc kiểm và lúc đọc" thì "chỉ còn lớp giới hạn số bước chặn (không treo)".
- **Thực tế:** chạy xong sau khoảng 4,5 giây với chỉ vài trăm bước. Một bước có thể tốn tùy ý: `randomblob`, `zeroblob`/`hex`, `printf('%.*c', N, 'x')` tới 1 tỷ byte (giới hạn độ dài mặc định của SQLite), vừa tốn giờ vừa tốn bộ nhớ. `trusted_schema = OFF` không chặn các hàm này (SQLite coi chúng là vô hại).
- **Đường tới:** SL-T070-1 (tới khi sửa), hoặc file bị thay đúng giữa lúc kiểm và lúc đọc (khe Thợ Máy đã ghi).
- **Vì sao Thấp:** chỉ tới được khi lớp kiểm cấu trúc đã bị lách; vẫn phải có chương trình lạ trên máy.
- **Gợi ý sửa:** trong `_guard`, thêm `conn.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, …)` nhỏ (ô lớn nhất app đọc chỉ vài KB; Python 3.11 trở lên có `setlimit`) để mỗi bước có giới hạn; và/hoặc cho bộ đếm dừng theo giờ thật (`time.monotonic()`), không chỉ theo số bước.
- **Test:** `test_sl_t070_2_guard_also_stops_few_but_heavy_steps` (ca này tốn khoảng 4,5 giây khi lỗi còn). XFAIL.

#### SL-T070-3 · Thấp · Tên file AI có số dính liền không nhận là ảnh AI

- **Tái hiện:** `tags_for_image(ImageRef(0, "CT012 - Cổng inox - Quận 7/truoc/AI01.png"))`; tương tự `AI2.jpg`, `dalle3_cong-sat.png`, `flux1-dev_00001_.png`, `gpt4o_cong-sat.png`, `seedream4_cong-sat.png`, `imagen3_cong-sat.png`, `Gemini2_cong-sat.png`.
- **Mong đợi:** ảnh AI, chỉ giữ hạng mục. Thư mục cùng tên ("AI01", "dalle3", "flux1", "gpt4o") đã được nhận.
- **Thực tế:** ảnh thật, giữ CT012, Quận 7, trước. Tên file chỉ tách ở dấu cách, dấu câu, gạch dưới (`split_case=False`, để chuỗi ngẫu nhiên "xAI3kQ" không thành AI), nên "ai01", "dalle3", "gemini2" là một từ, không khớp. Người dùng hay đặt "AI01", "AI02" cho ảnh vừa tạo.
- **Gợi ý sửa:** với tên file, tách thêm ở chỗ chữ ↔ số (không tách theo chữ hoa): "xAI3kQ" thành "xai 3 kq", vẫn là ảnh thật; đối chứng đã có trong `test_camera_and_chat_file_names_stay_real`.
- **Test:** `test_sl_t070_3_ai_file_name_with_digits_stuck_is_ai` (8 ca). XFAIL.
- **Ghi thêm:** `is_ai_name` đọc tên kiểu tên thư mục (có tách chữ hoa), nên với tên file nó trả khác `tags_for_image` ("xAI3kQ.jpg", "AI01.png": `is_ai_name` = `True`, `tags_for_image` = ảnh thật). Hướng an toàn; T-056 chỉ nên dùng `is_ai_name` cho tên thư mục gốc như docstring hướng dẫn.

#### SL-T070-4 · Thấp · Tên riêng thật trùng tên công cụ thành ảnh AI, không sửa lại được trong app

- **Tái hiện:** `tags_for_folder("CT015 - Sora Gardens - Q7/truoc")`; tương tự "Quán Night Cafe", "Flux Coffee", "Nhà anh Leonardo", "Nhà anh Krea", "Shop Runway", "Quán Sea Art".
- **Mong đợi:** phiếu YC1 "không chặn nhầm ảnh thật": ảnh thật, giữ CT015, Quận 7, trước.
- **Thực tế:** ảnh AI, mất mã công trình, khu vực, trước/sau. Tên công cụ một từ là chữ thường gặp hay tên riêng (Sora: khu căn hộ, quán Nhật; Flux: tên công ty, thuốc hàn trong nghề hàn; "Night Cafe", "Sea Art" có dấu cách vẫn khớp NightCafe, SeaArt). Thử thêm cũng thành AI: "Interior Designer", "Copilot Logistics", "Cty Canva Decor", "Render Studio", "Bing Tea", "Quán Grok", "Hailuo Trading", "Nhà hàng Jimeng"; tên file "Sora_Gardens_cong.jpg", "flux-coffee-cong.jpg".
- **Không có đường sửa trong app:** `ImageTagStore.set` từ chối đổi ảnh trong thư mục AI thành ảnh thật (`image_tags.py:271`), nên phải đổi tên thư mục trên Drive. Với tên riêng thì khó: "SoraGardens", "Sora-Gardens", "Sora Garden" vẫn là AI; chỉ "Soragardens" hay "S0ra Gardens" mới thoát.
- **Vì sao Thấp:** hướng an toàn (Lá Chắn T-052): ảnh chỉ mất thẻ công trình, không lộ chữ (A3 giữ). Thợ Máy đã ghi một phần là đánh đổi có chủ ý ("Cty Home Designer", "Thuốc hàn Flux"), nhưng chưa ghi các tên ở trên.
- **Gợi ý sửa (Chỉ Huy quyết):** tên công cụ là chữ thông dụng hay tên riêng (Sora, Flux, Krea, Leonardo, Runway, Designer, Bing, Grok, Kling, Canva, Render, Night Cafe, Sea Art, Image Creator) chỉ tính khi đứng riêng trong một phần tên (có thể kèm "ảnh/hình", "AI", số phiên bản), hoặc trong tên file; tên chỉ có nghĩa là công cụ AI (Midjourney, ChatGPT, DALL-E, Stable Diffusion, ComfyUI, Ideogram, Dreamina, Seedream…) giữ như nay. Nếu sửa, Thợ Máy cần xem lại test của mình `test_t070_ambiguous_names_lean_to_ai_and_leak_nothing` (đang khóa "Cty Home Designer", "Thuốc hàn Flux" là ảnh AI). Tôi tránh đưa hai tên đó vào test của tôi để hai test không mâu thuẫn.
- **Test:** `test_sl_t070_4_real_proper_names_are_not_ai` (7 ca). XFAIL.

#### SL-T070-5 · Thấp · "Ảnh mô phỏng" không nhận là ảnh AI

- **Tái hiện:** `tags_for_image(ImageRef(0, "CT012 - Cổng inox - Quận 7/truoc/Ảnh mô phỏng/x.png"))`; tương tự "Hình mô phỏng 3D", "mo phong".
- **Mong đợi:** ảnh AI (ảnh dựng, không phải ảnh chụp công trình), như "phối cảnh", "render" Thợ Máy đã thêm.
- **Thực tế:** ảnh thật, giữ CT012, Quận 7, trước. "Mô phỏng" là cách gọi ảnh dựng hay gặp ("hình ảnh mô phỏng").
- **Gợi ý sửa:** thêm "mô phỏng" vào `_AI_PHRASES`. Không đề xuất "ảnh dựng": "Ảnh dựng khung" là ảnh thật lúc dựng khung.
- **Test:** `test_sl_t070_5_simulated_image_phrase_is_ai` (3 ca). XFAIL.

## Đối chiếu tiêu chí xong (của phiếu, phần Soi Lỗi kiểm)

- [x] YC1 phần danh sách (a)–(e): đủ dấu hiệu phiếu yêu cầu, có `is_ai_name`, có đối chứng (`test_more_ai_folder_names_are_ai_at_any_depth`, `test_more_default_ai_file_names_are_ai`, `test_names_close_to_ai_markers_stay_real`, `test_is_ai_name_*`). Còn SL-T070-3, -4, -5 (Thấp)
- [ ] YC2 chưa trọn: lách được bằng dòng lặp (SL-T070-1); lớp phòng thứ hai có khe (SL-T070-2). 21 kiểu file độc khác (14 của Thợ Máy + 7 của tôi) đều bị bắt
- [x] YC3: `test_get_many_and_resolve_many_force_ai_per_ref_asked`
- [x] YC4: để nguyên đúng phiếu (chờ chủ dự án)
- [x] YC5: diff `tests/test_soi_loi_t052.py` chỉ gỡ 3 khối `xfail`; 56 qua
- [x] Test liên quan qua (1003 qua, 0 hỏng), `ruff check .` sạch

## Rủi ro và điểm cần chú ý

- **Nhận ảnh AI vẫn chỉ dựa vào tên** (như Thợ Máy ghi): file mặc định không có tên công cụ (Midjourney, Bing tải về "_<mã>.jpeg", Leonardo "Default_…", "AlbedoBase_XL_…", A1111 "00001-…", Canva "Untitled design.png") vẫn là ảnh thật nếu nằm trong thư mục công trình. Lớp chặn cuối vẫn là người duyệt ở T-056.
- `is_ai_name` không giới hạn độ dài: chuỗi 1 triệu ký tự mất khoảng 7,5 giây. T-056 chỉ đưa tên thư mục gốc (tối đa 255 ký tự) nên không thành lỗi; ghi lại để không ai đưa chuỗi tùy ý vào.
- File thẻ cỡ gần 64 MB mà toàn khung nhìn: lần mở đầu chờ khoảng 6–7 giây rồi tự đổi tên (một lần).
- Ca symlink và tên NFD thật trên ổ vẫn chưa chạy trên máy này (điều kiện T-063, Mac/Linux).

## Đề xuất

- **Thợ Máy (lượt sửa trong T-070, trước khi gộp):** SL-T070-1 (`_app_tables` đếm dòng, chặn dòng trùng); nên làm cùng SL-T070-2 (`setlimit` độ dài trong `_guard`). Cả hai đều nhỏ, trong `image_tags.py`.
- **Thợ Máy (cùng lượt hay phiếu sau, Chỉ Huy chọn):** SL-T070-3 (tách chữ ↔ số trong tên file), SL-T070-5 ("mô phỏng"); SL-T070-4 theo quyết định của Chỉ Huy/chủ dự án.
- **Cân nhắc thêm dấu hiệu (không phải lỗi, ngoài phiếu):** Google Whisk, Freepik (ảnh AI và ảnh mẫu đều không phải ảnh công trình), Doubao, Qwen, Craiyon, Playground, Tensor Art; "runwayml" viết liền chữ thường; tên mặc định của Canva nếu chủ dự án giữ "Canva là ảnh AI".
- **Lá Chắn (rút gọn):** cân mức SL-T070-1, -2 (lách đúng lớp YC2 yêu cầu); soát lại lời "không làm treo app" trong docstring `image_tags.py` sau khi sửa.
- **T-056 (Họa Sĩ/Thợ Máy):** hiện lý do một ảnh bị coi là AI ("tên thư mục có chữ …"), vì với SL-T070-4 người dùng không sửa được trong app; dùng `resolve`/`resolve_many` (không dùng `get`, `list_manual`) để lấy thẻ dùng cho ảnh; chỉ dùng `is_ai_name` cho tên thư mục gốc.
- **T-069 (README):** dặn tên thư mục ảnh thật tránh tên công cụ AI đứng riêng (Sora, Flux, Designer, Canva, Bing…).

## Câu hỏi cho chủ dự án

1. Ảnh thật trong thư mục có tên riêng trùng tên công cụ AI (ví dụ khu căn hộ "Sora Gardens", "Quán Night Cafe") đang bị coi là ảnh AI và không sửa lại được trong app. **Sửa** (chỉ coi là ảnh AI khi tên công cụ đứng riêng hay kèm chữ "ảnh/AI") hay **giữ** (người dùng đổi tên thư mục)? Đề xuất: **Sửa**.

## Kết luận

**ĐẠT CÓ ĐIỀU KIỆN** chuyển sang Lá Chắn rút gọn. 0 Nghiêm trọng, 0 Cao, 0 Trung bình; 5 Thấp (SL-T070-1 → -5). LC-T052-1 phần phiếu yêu cầu và LC-T052-3 đạt; ba `xfail` cũ gỡ đúng.

Điều kiện:
1. **SL-T070-1** sửa trước khi gộp `main` (lách đúng lớp kiểm YC2 của phiếu; sửa nhỏ). Lá Chắn cân mức; nên sửa cùng SL-T070-2.
2. **SL-T070-4**: Chỉ Huy hỏi chủ dự án (câu hỏi trên); chưa quyết thì giữ `xfail`.
3. **SL-T070-3, -5**: dọn trong lượt sửa này hoặc phiếu sau, trước T-056 nếu kịp.

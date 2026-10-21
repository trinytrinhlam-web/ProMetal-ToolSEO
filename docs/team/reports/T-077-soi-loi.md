# Báo cáo T-077 · Dọn thẻ ảnh nhỏ (sau T-074): tên công cụ AI gõ khác dạng chuẩn · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-077](../tickets/T-077-don-the-anh-ten-cong-cu-ai.md) |
| Ngày nộp | 2026-10-21 |
| Kết quả | Hoàn thành (kiểm rút gọn). **Kết luận: ĐẠT**, chuyển Lá Chắn rút gọn được |

## Tóm tắt (cho chủ dự án)

Bản sửa của Thợ Máy làm đúng cả 4 yêu cầu. Tôi thử 231 cách gõ tên công cụ tạo ảnh ("MidJourney", "Mid Journey", "Co-Pilot", "See Dream", kèm gạch ngang dài, chữ toàn chiều rộng, ký tự vô hình chen giữa, số phiên bản, tên hãng) ở 5 chỗ (thư mục cuối, thư mục đầu, hai kiểu tên file, thư mục gốc): **cả 231 tên đều là ảnh AI ở cả 5 chỗ**. Bản cũ chỉ đúng 11 tên.

Ảnh thật không bị kéo theo: tôi thử 74.458 tên ghép từ tên người, tên đường, khu căn hộ, chữ tiếng Việt có dấu và không dấu, viết liền, gõ hoa nhầm giữa chữ. Chỉ 4 tên đổi sang ảnh AI và đều là tên vô nghĩa hay tên công cụ ("BiNg"). Trong tên thật, tôi chỉ thấy thêm một trường hợp hiếm: "AnHai" (gõ liền "An Hải", không dấu) nay là ảnh AI. Cùng loại với "SoRa" mà Lá Chắn đã chấp nhận: ảnh chỉ mất mã công trình, không chữ nào lộ ra ngoài. "Anhai" viết thường thì bản cũ cũng đã coi là ảnh AI.

Khi một tab đang đọc thẻ của rất nhiều ảnh, lần lưu ở tab khác nay chờ ít hơn hẳn. Tôi đo với 5.000 ảnh: chờ lâu nhất còn 2,2 giây (bản cũ 6,5 giây). **Không có lỗi mới.**

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t077.py` | Mới: 44 ca, đều qua. Đối chứng ảnh thật (nửa tên công cụ đứng riêng; tên người, tên đường, khu căn hộ viết liền) và thứ tự câu SQL của `get_many` (cả `COMMIT`) |
| `docs/team/reports/T-077-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác.

## Kiểm từng yêu cầu

| Yêu cầu | Kết quả | Bằng chứng |
|---|---|---|
| YC1 · LC-T074-1 (gồm SL-T074-2) | **ĐẠT** | `_parse_dir_name` đọc cả hai kiểu (`seo_app/images/tags.py:867`), 4 tên tách đôi ở `:246-249`. S5: 21 kiểu gõ ("MidJourney", "FireFly", "CoPilot", "SeeDream", "Mid Journey", "Mid-Journey", "Co-Pilot", "Fire Fly", "co_pilot", "midJourney", "MIDjourney", "SEE DREAM"…) × 11 biến thể (nguyên, gạch ngang dài " – ", dấu cách không ngắt, chữ toàn chiều rộng, ký tự rộng 0 chen giữa, hai dấu cách, "v6", kèm hãng, "Ảnh … 2025", dính số, trong ngoặc) = 231 tên. Bản mới: cả 231 là ảnh AI, không mang mã công trình, khu vực hay trước/sau, ở thư mục cuối, thư mục đầu, tên file `_0001`, tên file ` (2)`, thư mục gốc. Bản `378f710`: chỉ 11/231 tên đúng cả 5 chỗ. Ca đối chứng của `tests/test_la_chan_t074.py` ("Cua so ra ban cong", "Cửa sổ ra ban công", "Nha co Phuong", "Mai che san thuong") qua |
| YC2 · SL-T074-1 | **ĐẠT** | `get_many` (`seo_app/storage/image_tags.py:255-288`). S2 theo dõi bằng `set_trace_callback`, thấy cả câu Python tự chạy. 1.209 ảnh ở 3 thư mục gốc: `PRAGMA`, `BEGIN`, câu kiểm `sqlite_master`, 6 câu đọc, `COMMIT`. Mọi câu sau `BEGIN` có `in_transaction = True`, kết nối đóng rồi mới kiểm dòng đầu tiên, sau đó không còn câu SQL nào. Bản cũ: 5/6 câu đọc và `COMMIT` chạy sau khi đã kiểm dòng. **Thử lại T2 của Lá Chắn** (S1, script `t2_giao_dich.py` của Lá Chắn T-074, chép nguyên): 6 thao tác (`set`, `clear`, `clear_all`, `get`, `resolve_many`, `list_manual`; `set`, `get` thêm lần chạy trên kho mới) × nhật ký thường/WAL × kẻ tấn công chờ/không chờ. Kết quả bản T-077 **giống hệt** bản `378f710` ở cả 32 dòng (so sau khi bỏ số giây). Trigger không chạy trong thao tác nào (khu vực không lần nào thành "Quận 1"); ở chế độ nhật ký thường, kẻ tấn công không chờ bị chặn ("locked"); thay đổi chen vào bị bắt ở lần sau, file lạ được đổi tên. **Thời gian chờ lưu** (S3, script `k1` của Thợ Máy, 13:43–13:46): N = 5.000, lần lưu chờ lâu nhất 6,50 → **2,19 s**, trung bình 6,14 → 1,74 s; N = 2.000: 2,37 → 1,32 s. Thời gian `get_many` không đổi (5,6 / 6,1 s, máy đang tải). Test mới `test_get_many_runs_every_statement_inside_the_checked_transaction_before_row_checks` |
| YC3 · docstring WAL | **ĐẠT** | Docstring module (`image_tags.py:19-25`) và `_begin` (`:566-571`) khớp hành vi S1 đo được. Nhật ký thường: chương trình khác không ghi xong được trong lúc app giữ giao dịch (bị chặn). WAL: chương trình khác ghi được trong lúc app **đọc**, nhưng lần đọc vẫn chỉ thấy bản đã kiểm, còn lần **ghi** của app thì chặn được nó. Thay đổi chen vào bị bắt ở lần kiểm sau. Phần sửa thêm ở `_begin` (ngoài đúng dòng 19-21 phiếu ghi) chỉ là lời, đúng ý, không mâu thuẫn với docstring module |
| YC4 · gỡ `xfail`, không đổi điều kiện | **ĐẠT** | `git diff --numstat 378f710..team/T-077 -- tests/`: `test_soi_loi_t074.py` 0 dòng thêm, 23 dòng xóa (đúng 3 khối `@pytest.mark.xfail(...)`); `test_la_chan_t074.py` 0 thêm, 8 xóa (3 dấu `xfail` và hằng `_REASON` chỉ dùng cho chúng); `test_images_tags.py` 192 dòng thêm, 0 dòng xóa. Đọc diff: không đổi `assert`, tham số hay hàm phụ nào |

## Tìm lỗi mới (ảnh thật bị coi nhầm là ảnh AI)

Script S4 so bản `378f710` với bản T-077 (13:45–13:49):

- **A. Mọi dấu hiệu AI một chữ** (54 dấu hiệu ASCII trong `_AI_MARKERS`), tách thành âm tiết tiếng Việt không dấu hay chữ tiếng Anh rồi viết CamelCase, đứng riêng hay kèm chữ khác. Có 154 tên đổi sang ảnh AI. Gần hết là tên công cụ viết hoa giữa chữ, đúng yêu cầu ("CoPilot", "RunWay", "ReCraft", "IdeoGram", "GeMini", "HaiLuo"…). Một số là cụm chỉ ảnh AI gõ hoa lạ, cũng đúng là ảnh AI ("MinhHoA" là "minh hoạ", "MopHong" là "mô phỏng", "PhoICanh" là "phối cảnh"). Phần còn lại là chuỗi vô nghĩa ("AiimAge", "TaoBanGai"). Tên thật đọc được thì chỉ có **"SoRa"** (đã biết, Thợ Máy có test, Lá Chắn T-074 chấp nhận ở T6) và **"AnHai"** ("An Hải" gõ liền không dấu, trùng dạng liền "anhai" của "ảnh AI"). Tôi ghi "AnHai" ở mục Ghi nhận.
- **B. 74.458 tên thật**: họ tên người viết liền (21 họ × 16 tên đệm × 58 tên, gồm cả tên gần giống tên công cụ như "Ra", "Va", "Can", "Bình"; có dấu và không dấu; đủ họ tên, tên đệm + tên, tên riêng, "Nha …", "Nha anh …"), 20 tên đường và 25 tên khu căn hộ, cửa hàng (viết liền, tách từng chữ, "So 45 …"), cùng 40.000 tên ghép ngẫu nhiên 1–4 âm tiết từ 1.346 âm tiết lấy trong repo (viết liền, tách chữ, gõ hoa nhầm một chữ giữa, kèm "Q7", "2024", "_01"). So cả 4 chỗ: thư mục là ảnh AI hay không; mã công trình, khu vực, trước/sau; `is_ai_name`; tên file. **4 tên đổi**: "BiNg", "BinG" (tên công cụ Bing), "AnhaI", "ẢnHai" (vô nghĩa, dạng liền của "ảnh AI"). Không tên người, tên đường hay khu căn hộ nào đổi.
- **C. Nửa tên công cụ tách đôi**: "See", "Fire", "Co", "Mid", "Fly", "Dream", "Pilot", "Journey" (cả "SEE", "co") trong 13 ngữ cảnh ("Nha co …", "Sweet …", "… Home", "… Station", "… Phuong", dính số). Không tên nào là ảnh AI, trừ tên có đủ cả hai nửa ("Nha co Pilot", "See Dream", "Fire - Fly Shop"). Tên thật có một nửa ("Co.op Mart", "Co-op", "See You Cafe", "Fire Station", "Firefighter", "Dream Home", "Sweet Dream", "Mid Valley", "Pilot Pen", "Journey Coffee", "Mid - Town"): đều là ảnh thật.

Kết luận: không có lỗi mới. Các kiểu nhận nhầm còn lại đều thuộc loại đánh đổi Lá Chắn đã chấp nhận: hướng an toàn, ảnh chỉ mất thẻ công trình, không chữ nào đi ra.

## Lỗi tìm thấy

Không có.

## Ghi nhận (không phải lỗi, không cần sửa)

- **"AnHai" là ảnh AI** (mới ở T-077). Thư mục tên đúng một chữ "AnHai", hay "Nha AnHai", "CT012 - Cong - AnHai" (gõ liền không dấu), bị đọc kiểu không tách thành "anhai", tức dạng liền của "ảnh AI". Bản cũ: ảnh thật. "Anhai" viết thường thì bản cũ đã là ảnh AI. "An Hai", "An Hải", "AnHải", "NguyenAnHai", "AnhHai" đều vẫn là ảnh thật. Cùng loại "SoRa": tên thật trùng dạng liền của một dấu hiệu, hướng an toàn, hiếm (Lá Chắn T6 dò 60.336 tên không gặp; tôi dò 74.458 tên cũng không gặp, chỉ thấy khi dò ngược từ dấu hiệu). Tôi không viết test `xfail`: muốn "AnHai" là ảnh thật thì phải bỏ dạng liền của "ảnh AI", và như thế làm sai "Anhai" vốn đúng từ trước. Lớp chặn cuối vẫn là người duyệt ở T-056.
- **Phần khớp danh sách so không dấu**: thư mục chỉ có "Có Pilot" hay "Cổ Pilot", và ô "Nguồn ảnh" sửa tay gõ "Có Pilot", đều được nhận là ảnh AI (`match_source("Có Pilot") == "ai"`). Đây là cách so có từ trước cho mọi dấu hiệu nhiều chữ trong `_AI_WORDS`. Tên ghép như vậy khó gặp ngoài đời; hướng an toàn.
- Thư mục chỉ có một chữ trùng tên công cụ (`"Firefly Coffee"`, `"Sora Gardens"`) là ảnh AI: SL-T070-4, đã hoãn, ngoài phiếu (7 ca `xfail` còn lại).

## Bằng chứng

Máy Windows 11 Pro (10.0.26300) của chủ dự án, Python 3.12.15, SQLite 3.53.1, worktree `wt-T-077`, nhánh `team/T-077` (đầu nhánh lúc kiểm `36d6470`, gốc `378f710`). Máy đang chạy song song các agent khác.

```
$ uv run pytest tests/test_images_tags.py tests/test_soi_loi_t052.py tests/test_soi_loi_t070.py \
    tests/test_soi_loi_t074.py tests/test_la_chan_t074.py tests/test_images_folders.py \
    tests/test_ai_images.py -q -p no:cacheprovider -rsx
(13:40–13:42, trước khi thêm file của tôi)
1323 passed, 8 skipped, 7 xfailed in 81.86s (0:01:21)

(thêm tests/test_soi_loi_t077.py, 13:52–13:53)
1367 passed, 8 skipped, 7 xfailed in 66.80s (0:01:06)

$ uv run ruff check .
All checks passed!
```

- 0 hỏng. Lượt đầu khớp số của Thợ Máy (1323 qua, 8 bỏ qua, 7 xfail); lượt sau thêm đúng 44 ca của tôi. 8 bỏ qua như cũ: 2 ca symlink của T-052 (Windows chưa bật Developer Mode), 6 ca của T-048 (chỉ chạy được trên Mac/Linux hay cần symlink). 7 xfail đều là SL-T070-4 (đã hoãn).
- **Test mới trên code cũ:** dựng `seo_app` của `378f710` bằng `git archive` vào thư mục nháp, chép `tests/test_soi_loi_t077.py` vào, chạy với `PYTHONPATH` trỏ vào đó (in `__file__` xác nhận nạp đúng bản cũ). Kết quả **1 hỏng, 43 qua**. Ca hỏng đúng là ca `get_many` (bản cũ còn chạy câu SQL sau khi kiểm dòng đầu tiên). 43 ca đối chứng ảnh thật qua trên cả hai bản: T-077 không kéo ảnh thật nào trong danh sách sang ảnh AI.
- **Quét chuỗi giống bí mật:** `PYTHONUTF8=1 uvx detect-secrets scan --all-files` trong thư mục riêng chứa 2 file của tôi và 1 file mồi có chữ tiếng Việt (khóa AWS giả, `password = …`). Chỉ file mồi có mục, bắt đủ 2/2 (`AWS Access Key`, `Secret Keyword`); 0 mục ở file của tôi. Đã xóa thư mục mồi.
- Script thử và kết quả: thư mục ghi chú chung của nhóm phiên, `T-077-soi-loi-scripts/`. S1 `s1_t2_giao_dich.py` (T2 của Lá Chắn T-074, chép nguyên), S2 `s2_trace.py`, S3 `s3_k1_lock_compare.py` (`k1` của Thợ Máy), S4 `s4_names.py`, S5 `s5_tool_variants.py`, mỗi script kèm file `*_out.txt`. Chạy bằng `PYTHONUTF8=1 uv run python <script> <file bản cũ>` trong worktree. Bản cũ lấy bằng `git show 378f710:seo_app/images/tags.py` (S4, S5) hay `git show 378f710:seo_app/storage/image_tags.py` (S1, S2, S3).

## Đối chiếu việc được giao

- [x] 1. YC1–4 làm thật: 231 kiểu gõ tên công cụ là ảnh AI ở mọi chỗ (S5); tên ảnh thật và ca đối chứng của Lá Chắn vẫn là ảnh thật (S4, test); `get_many` đọc hết trong giao dịch rồi mới xử lý, mọi câu SQL trong giao dịch đã kiểm (S2), thử T2 giống hệt bản cũ (S1); lần lưu chờ ít hơn (S3)
- [x] 2. Soát test: hai file `xfail` chỉ gỡ dấu, không thêm dòng nào; `test_images_tags.py` chỉ thêm
- [x] 3. Tìm lỗi mới: 74.458 tên thật, 54 dấu hiệu một chữ, nửa tên công cụ trong 13 ngữ cảnh: không có lỗi; "AnHai" ghi nhận (hướng an toàn)
- [x] 4. Không có lỗi mới nên không có test `xfail`. `tests/test_soi_loi_t077.py` gồm 44 ca qua, giữ các đối chứng trên
- [x] Test liên quan qua, `uv run ruff check .` sạch

## Rủi ro và điểm cần chú ý

- Số đo thời gian (S3) lấy trên máy đang chạy song song agent khác: con số tuyệt đối chậm hơn máy rảnh. Bản cũ và bản mới chạy xen kẽ trong cùng điều kiện nên phép so vẫn đúng. Lần đo này bản cũ chờ tới 6,5 s mà vẫn không báo "đang bận" (lần chờ khóa SQLite riêng lẻ chưa quá 5 s; phần còn lại là hai luồng chia nhau một tiến trình Python).
- Chưa thử trên Mac (thay đổi chỉ ở phần xử lý chữ và thứ tự đọc/xử lý trong `get_many`, không đụng đường dẫn hay file).
- Danh sách tên thật tôi dựng (S4) là tên giả theo mẫu tên Việt Nam và tên đường TP.HCM, không phải thư mục Drive thật của Pro-Metal.

## Đề xuất

- **Lá Chắn (rút gọn):** cân nhắc ghi "AnHai" cùng dòng "SoRa" trong phần đánh đổi đã chấp nhận (T6 của T-074).
- **T-069 (README):** như Thợ Máy đề xuất, khuyên để chữ "AI" trong tên thư mục ảnh AI; thêm: tên thư mục ảnh thật nên viết có dấu hay tách chữ ("An Hải", không "AnHai") nếu trùng chữ gần giống "ảnh AI".

## Kết luận

**ĐẠT**, chuyển Lá Chắn rút gọn được. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp. Cả 4 yêu cầu đạt, có thử lại bằng chính T2 của Lá Chắn, cách đo `k1` của Thợ Máy và cách đọc SQL bằng `set_trace_callback`, đều có đối chứng bản cũ. Không có ảnh thật nào trong 74.458 tên thật bị coi nhầm là ảnh AI. Riêng "AnHai" (dò ngược từ dấu hiệu mới ra) là đánh đổi cùng loại "SoRa".

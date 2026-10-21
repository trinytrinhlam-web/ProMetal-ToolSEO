# Báo cáo T-077 · Dọn thẻ ảnh nhỏ (sau T-074): tên công cụ AI gõ khác dạng chuẩn

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-077](../tickets/T-077-don-the-anh-ten-cong-cu-ai.md) |
| Ngày nộp | 2026-10-21 |
| Kết quả | Hoàn thành (yêu cầu 1–4) |

## Tóm tắt (cho chủ dự án)

Thư mục hay file ảnh AI đặt tên công cụ tạo ảnh theo kiểu viết hoa giữa chữ ("MidJourney", "FireFly", "CoPilot") hoặc gõ tách đôi ("Mid Journey", "Fire Fly", "Co-Pilot", "See Dream") nay được nhận là **ảnh AI**; trước đây chúng bị coi là ảnh thật và mang mã công trình, khu vực của công trình thật. Tên thư mục ảnh thật gõ liền hay không dấu ("CongSatQuan7", "Cua so ra ban cong") vẫn là ảnh thật.

Khi một tab đang đọc thẻ của rất nhiều ảnh, lần lưu thẻ ở tab khác nay chỉ chờ phần đọc file, không chờ phần app kiểm từng thẻ: thời gian chờ còn khoảng một nửa (đo với 5.000 ảnh đã sửa thẻ tay), nên khó chạm mốc 5 giây báo "đang bận" như Soi Lỗi đo được ở bản cũ.

Hôm nay giao diện chưa thấy gì khác vì màn hình chọn ảnh (T-056) chưa làm; phiếu này dọn đường cho T-056. Còn sót vài kiểu gõ tách hiếm gặp ("Run Way", "Re Craft"), ngoài 4 tên phiếu giao (mục Rủi ro).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/images/tags.py` | Tên thư mục tìm dấu hiệu ảnh AI theo cả hai cách đọc (tách và không tách chữ hoa); thêm 4 tên công cụ dạng tách đôi vào `_AI_TOOLS`; sửa docstring cho khớp |
| `seo_app/storage/image_tags.py` | `get_many` đọc mọi dòng trong giao dịch đã kiểm, kiểm từng dòng sau khi giao dịch đóng; sửa lời docstring (module, `_begin`) cho đúng chế độ WAL |
| `tests/test_images_tags.py` | Thêm 61 ca test T-077 (chỉ thêm, không sửa test cũ) |
| `tests/test_soi_loi_t074.py` | Gỡ 3 khối `xfail` (19 ca SL-T074-1, SL-T074-2), không đổi gì khác |
| `tests/test_la_chan_t074.py` | Gỡ 3 dấu `xfail` (20 ca LC-T074-1) và hằng `_REASON` chỉ dùng cho chúng, không đổi gì khác |
| `docs/team/reports/T-077-tho-may.md` | Báo cáo này |

Không đụng file ngoài phạm vi phiếu (`drafts.py`, `folders.py`, `app/**`, `config/**` không đổi). Không thêm thư viện.

## Cách sửa từng yêu cầu

### YC1 · LC-T074-1 (gồm SL-T074-2), bắt buộc

- **Đọc thêm kiểu không tách chữ hoa:** `_parse_dir_name` (`seo_app/images/tags.py:863-868`) nay là `ai = _has_ai_marker(cleaned, split_case=True) or _has_ai_marker(cleaned, split_case=False)`, đúng câu phiếu. Cách đọc thứ hai chính là cách đọc tên file (chỉ tách ở dấu cách, dấu câu, gạch dưới, chỗ chữ dính số), nên "MidJourney" là một chữ "midjourney", "HaiLuo" là "hailuo". `is_ai_name` dùng `_parse_dir_name` nên thư mục gốc tự đúng theo. Phần đọc thẻ (mã công trình, hạng mục, khu vực, trước/sau) không đổi: vẫn chỉ tách kiểu cũ.
- **4 tên tách đôi:** thêm đúng `"Mid Journey"`, `"Fire Fly"`, `"Co Pilot"`, `"See Dream"` vào `_AI_TOOLS` (`tags.py:243-249`), kèm chú thích "không ghép mọi cặp chữ liền nhau". Gạch nối, gạch dưới, dấu chấm đều tách chữ nên "Mid-Journey", "co_pilot", "Mid.Journey" tự khớp; "MidJourney" khớp ở cả hai cách đọc. Vì `_AI_TOOLS` nằm trong `_AI_WORDS`, 4 tên này cũng vào danh sách khớp trọn như mọi tên công cụ khác: một phần tên thư mục chỉ có "Co Pilot" được đọc là dấu hiệu AI (không bị đếm là phần lạ), và ô "Nguồn ảnh" khi sửa tay nhận "Co Pilot" là ảnh AI. Không trùng cách viết trong từ điển (`_build_vocabulary` báo lỗi lúc nạp module nếu trùng; module nạp bình thường).
- **Không ghép bừa:** chỉ 4 cặp chữ cụ thể. Ca đối chứng của Lá Chắn ("Cua so ra ban cong", "Cửa sổ ra ban công", "Nha co Phuong", "Mai che san thuong") vẫn qua.
- Docstring module (`tags.py:42-46`) và `_has_ai_marker` (`:496-501`) ghi cách đọc mới.

### YC2 · SL-T074-1, nên làm cùng

`get_many` (`seo_app/storage/image_tags.py:266-288`): khối `with self._connect() as conn:` chỉ còn các câu `SELECT` (gộp `fetchall()` của mọi nhóm vào `rows`); `_row_to_tag` và `tags_for_image` chạy **sau** khi ra khỏi khối (giao dịch đã commit, kết nối đã đóng), giống `list_manual` đang làm. Mọi câu SQL vẫn chạy trong giao dịch `_connect` mở bằng `BEGIN` và đã kiểm `sqlite_master` ở câu đọc đầu tiên (LC-T070-2 giữ nguyên); sau khối không còn câu SQL nào. Đúng cách sửa thử E3b của Soi Lỗi, giữ chú thích LC-T052-3.

### YC3 · lời docstring cho đúng chế độ WAL

- Docstring module (`image_tags.py:19-25`): bỏ câu "chương trình khác không đổi được cấu trúc giữa lúc kiểm và lúc dùng" (sai khi app **đọc** file ở chế độ WAL). Nay ghi: cấu trúc app dùng luôn là cấu trúc vừa kiểm; chế độ nhật ký thường (app không đổi chế độ của file) thì chương trình khác mở file qua SQLite phải chờ giao dịch xong mới ghi được; chế độ WAL thì nó ghi được trong lúc app đọc, nhưng lần đọc đó vẫn chỉ thấy bản đã kiểm, còn lần ghi của app giữ quyền ghi từ đầu; thay đổi chen vào bị bắt ở lần kiểm sau. Các ý này đã có test: `test_wal_attacker_blocked_on_save_and_read_keeps_checked_snapshot`, `test_patient_attacker_cannot_slip_a_trigger_into_a_save` (`tests/test_soi_loi_t074.py`).
- **Ngoài đúng dòng 19-21:** docstring `_begin` (`image_tags.py:566-571`) có cùng câu sai ("chương trình khác không đổi được cấu trúc… (nó nhận "database is locked")"). Tôi sửa luôn cho khỏi mâu thuẫn với docstring module: chỉ còn nói chương trình khác phải chờ hay nhận "database is locked" ở lần **ghi** của app. Cùng file trong phạm vi, chỉ là lời; Soi Lỗi, Lá Chắn xem giúp.

### YC4 · gỡ `xfail` khi XPASS, không đổi điều kiện

`git diff --numstat 378f710 -- tests/test_soi_loi_t074.py tests/test_la_chan_t074.py`: **0 dòng thêm**; `test_soi_loi_t074.py` xóa 23 dòng (đúng 3 khối `@pytest.mark.xfail(strict=True, reason=(…))`), `test_la_chan_t074.py` xóa 8 dòng (3 dòng `@pytest.mark.xfail(strict=True, reason=_REASON)` và hằng `_REASON` 5 dòng, chỉ dùng cho 3 dấu đó). Không đổi `assert`, tham số hay hàm phụ nào. Hai file test bản `378f710` (còn `xfail`) chạy trên code đã sửa cho đúng 39 XPASS(strict) (mục Bằng chứng).

## Test mới (`tests/test_images_tags.py`, 61 ca)

| Test | Kiểm gì |
|---|---|
| `test_t077_one_word_tool_name_with_a_capital_inside_is_ai` (28 ca, `:926`) | Cả 28 tên công cụ một chữ trong `_AI_TOOLS`, viết hoa thêm **một** chữ ở **mọi** vị trí (144 kiểu, như thử E10 của Soi Lỗi): thư mục dưới gốc ở mọi tầng, kèm chữ khác ("Ảnh MidJourney v6"), dính số ("MidJourney2"), thư mục gốc (`is_ai_name`), tên file |
| `test_t077_tool_name_typed_as_two_words_is_ai` (16 ca, `:964`) | 4 tên tách đôi với dấu cách, gạch nối, gạch dưới, dấu chấm, hoa/thường, kèm hãng hay phiên bản: thư mục, thư mục gốc, tên file |
| `test_t077_real_names_stay_real_when_read_both_ways` (15 ca, `:999`) | Đối chứng: tên ảnh thật gõ liền hay không dấu ("CongSatQuan7", "CuaSoRaBanCong", "NhaCoPhuong", "CongTyDesignHome", "Dream Home", "Mid Town"…) vẫn là ảnh thật, giữ mã công trình, khu vực, trước/sau; cả tên file |
| `test_t077_lone_word_equal_to_a_tool_name_leans_to_ai_and_leaks_nothing` (`:1007`) | Đánh đổi có chủ ý Lá Chắn đã nêu (T6): thư mục chỉ có chữ "SoRa" là ảnh AI (công cụ Sora); không chữ nào của tên đi ra |
| `test_t077_get_many_reads_all_chunks_in_checked_transaction_then_releases_lock` (`:2455`) | 802 ảnh ở 2 thư mục gốc (4 câu `IN`): trên kết nối chỉ có đúng `PRAGMA`, `BEGIN`, câu kiểm `sqlite_master`, rồi 4 câu đọc; lúc kiểm dòng đầu tiên, mọi câu SQL đã chạy xong và kết nối khác lấy ngay được `BEGIN EXCLUSIVE` (khóa đã nhả) |

## Bằng chứng

Máy Windows 11 Pro (10.0.26300) của chủ dự án, Python 3.12.15, SQLite 3.53.1, worktree `wt-T-077`, nhánh `team/T-077` (gốc `378f710`). Máy đang chạy song song các agent khác.

```
$ uv run pytest tests/test_images_tags.py tests/test_soi_loi_t052.py tests/test_soi_loi_t070.py \
    tests/test_soi_loi_t074.py tests/test_la_chan_t074.py tests/test_images_folders.py \
    tests/test_ai_images.py -q -p no:cacheprovider -rsx
(trước khi sửa, 378f710, 12:16–12:19)
1223 passed, 8 skipped, 46 xfailed in 106.20s (0:01:46)
(sau khi sửa, mã cuối của nhánh, 12:33–12:34)
1323 passed, 8 skipped, 7 xfailed in 63.17s (0:01:03)
(chạy lại cùng mã sau khi phiên tạm dừng, 13:33–13:34)
1323 passed, 8 skipped, 7 xfailed in 72.02s (0:01:12)

$ uv run ruff check .
All checks passed!
```

- 1323 = 1223 cũ + 39 ca gỡ `xfail` + 61 ca mới. 0 hỏng. 7 xfail còn lại là SL-T070-4 (đã hoãn, ngoài phiếu). 8 bỏ qua như cũ (2 ca symlink của T-052: Windows chưa bật Developer Mode; 6 ca của T-048 chỉ chạy được trên Mac/Linux hay cần symlink).
- **Test mới bắt đúng lỗi cũ:** dựng `seo_app` của `378f710` bằng `git archive` vào thư mục nháp, chép 3 file test của nhánh vào, chạy với `PYTHONPATH` trỏ vào đó (in `__file__` xác nhận nạp đúng bản cũ): **85 ca hỏng, 15 qua**. Hỏng: 28 + 16 + 1 ca tên mới, ca `get_many` (`assert [(4, False)] == [(7, True)]`: bản cũ kiểm dòng đầu khi mới chạy 4/7 câu SQL và khóa còn giữ), cùng 39 ca vừa gỡ `xfail`. Qua: đúng 15 ca đối chứng ảnh thật.
- **39 ca `xfail` thật sự XPASS:** chạy đúng 2 file test bản `378f710` (còn dấu `xfail`) trên code đã sửa (thư mục nháp, kèm `tests/conftest.py`): **39 XPASS(strict)** (20 LC-T074-1, 18 SL-T074-2, 1 SL-T074-1), 136 qua, không hỏng gì khác.
- **Thử lại T5, T6 của Lá Chắn** (`t5_ten_anh.py`, `t6_ban_sua_thu.py` chép nguyên, đối số là `tags.py` bản `378f710`; 12:27–12:29):
  - T5 (a): 12 tên viết hoa giữa chữ ("MidJourney", "FireFly", "CoPilot", "ReCraft", "RunWay", "HaiLuo"…) và 6 tên gõ tách đôi ("Mid Journey", "Co-Pilot", "See Dream"…) nay là ảnh AI ở thư mục, thư mục gốc và tên file; bản cũ: ảnh thật.
  - T5 (b): 2.324 tên dựng từ mọi dấu hiệu AI trong 18 ngữ cảnh (dính số, gạch, viết liền, hoa/thường): **0** tên bản cũ nhận AI mà bản mới nhận thật.
  - T5 (c): 112 tên thư mục ảnh thật kiểu Pro-Metal ("CongSatQuan7", "NhaChiMai", "CuaSoRaBanCong", "VinHomes", "Inox304"…): **0** đổi kết quả.
  - T5 (d): A3 đạt trên 20.000 đường dẫn ngẫu nhiên (giá trị thẻ chỉ từ danh sách, `is_ai_name` chỉ trả `bool`).
  - T6: 60.336 tên (20.112 tên × gõ thường / không dấu / viết liền CamelCase): đổi kết quả 40 tên thư mục, 25 tên file, **trùng đúng số bản sửa thử của Lá Chắn**. Mọi tên đổi đều có cặp chữ tiếng Anh tương ứng ("co pilot", "fire fly", "mid journey", "see dream"), trừ đúng một tên chỉ có chữ tiếng Việt: "SoRa" (thành ảnh AI, hướng an toàn). 112 tên thật: 0 đổi.
- **Thử lại E10 của Soi Lỗi** (`e10_camel_case.py`, đối số `tags.py` bản cũ): 155 kiểu viết hoa thêm một chữ ở mọi vị trí (mọi dấu hiệu một chữ dài từ 4 chữ cái): sai ở tên thư mục **0** (bản cũ 118), sai ở tên file 0. 37 kiểu viết hay gặp ("MidJourney V6", "Microsoft CoPilot", "LeoNardo", "SeeDream 4.0"…): đều là ảnh AI ở thư mục, tên file và `is_ai_name`.
- **Thời gian chờ lưu (SL-T074-1)**, script `k1_lock_compare.py` (cùng kịch bản E3 của Soi Lỗi: một luồng gọi `get_many(N)` liên tục, luồng khác lưu 10 thẻ; N ảnh đều có thẻ sửa tay; hai bản chạy xen kẽ; 12:30–12:32):

  ```
  N=  200 378f710: get_many 0.16 s | luu: cho lau nhat 0.35 s, trung binh 0.31 s, bao ban 0/10 [] | doc 23 lan, loi doc 0
  N=  200 T-077  : get_many 0.15 s | luu: cho lau nhat 0.23 s, trung binh 0.17 s, bao ban 0/10 [] | doc 16 lan, loi doc 0
  N= 2000 378f710: get_many 1.59 s | luu: cho lau nhat 1.87 s, trung binh 1.64 s, bao ban 0/10 [] | doc 11 lan, loi doc 0
  N= 2000 T-077  : get_many 1.59 s | luu: cho lau nhat 1.41 s, trung binh 0.97 s, bao ban 0/10 [] | doc 6 lan, loi doc 0
  N= 5000 378f710: get_many 4.20 s | luu: cho lau nhat 4.73 s, trung binh 4.23 s, bao ban 0/10 [] | doc 11 lan, loi doc 0
  N= 5000 T-077  : get_many 4.01 s | luu: cho lau nhat 2.58 s, trung binh 1.91 s, bao ban 0/10 [] | doc 5 lan, loi doc 0
  ```

  Lần đo này bản cũ chưa chạm mốc 5 giây (`_SQLITE_TIMEOUT`) nên cả hai bản đều 0 lần "đang bận"; Soi Lỗi đo bản cũ lúc máy tải nặng hơn: N = 5.000, 4/10 lần lưu báo bận. Thời gian chờ trung bình còn khoảng một nửa, thời gian `get_many` không đổi. Suy luận: phần chờ còn lại là lúc giao dịch đọc chạy các câu `SELECT`, cộng việc hai luồng chia nhau một tiến trình Python; bản sửa thử E3b của Soi Lỗi đo được tương tự (chờ lâu nhất 1,03 / 2,44 s ở N = 2.000 / 5.000).
- **Tốc độ đọc thẻ** (đọc thêm một kiểu cho tên thư mục), script `k2_tag_speed.py` (lần nhanh nhất trong 7, xen kẽ hai bản; 12:30): `tags_for_image` một trang 200 ảnh (4 tầng thư mục) 84,6 → 93,7 ms; `is_ai_name` 200 tên 63,2 → 67,2 ms.
- **Quét chuỗi giống bí mật:** `PYTHONUTF8=1 uvx detect-secrets scan --all-files` trong thư mục riêng chứa 6 file của phiếu, patch nhánh (`git diff 378f710`) và 1 file mồi có chữ tiếng Việt (khóa AWS giả, `password = …`): chỉ file mồi có mục, bắt đủ 2/2 (`AWS Access Key`, `Secret Keyword`); 0 mục ở file thật. Quét lại lúc 13:35 với bản báo cáo cuối: như vậy. Đã xóa thư mục mồi sau mỗi lần quét.
- **Gộp với `main`:** `git merge-tree --write-tree main HEAD` không xung đột (`main` đã sang `9e6254f`, chỉ đổi `CLAUDE.md`, `docs/team/board.md`, `docs/team/dong-bo.md`). `git diff --check` sạch.

## Đối chiếu tiêu chí xong

- [x] YC1 LC-T074-1 (gồm SL-T074-2): `tags.py:243-249`, `:863-868`; 18 ca SL-T074-2 và 20 ca LC-T074-1 gỡ `xfail` qua; 60 ca mới về tên (28 + 16 + 15 đối chứng + 1); ca đối chứng của Lá Chắn qua
- [x] YC2 SL-T074-1: `image_tags.py:266-288`; `test_sl_t074_1_save_in_other_tab_does_not_wait_for_row_processing` gỡ `xfail` qua; `test_t077_get_many_reads_all_chunks_in_checked_transaction_then_releases_lock`
- [x] YC3 docstring WAL: `image_tags.py:19-25` (và `_begin`, `:566-571`)
- [x] YC4 gỡ `xfail`, không đổi điều kiện: 0 dòng thêm ở 2 file test; 39 XPASS(strict) trước khi gỡ
- [x] Test liên quan qua, `uv run ruff check .` sạch (mục Bằng chứng)
- [x] Báo cáo tại `docs/team/reports/T-077-tho-may.md`

## Rủi ro và điểm cần chú ý

- **Kiểu gõ tách khác vẫn là ảnh thật** (hướng không an toàn, ngoài 4 tên phiếu giao): "Run Way", "Re Craft", "Ideo Gram", "Hai Luo", "Ji Meng", "Dream Ina", "Leo Nardo" ở thư mục, tên file và thư mục gốc (tôi đã thử). Hiếm gặp: tên hãng viết liền, ít ai gõ tách. Các tên nhiều chữ có sẵn trong danh sách thì gõ tách vẫn đúng: "Night Cafe", "Sea Art", "Comfy UI", "Chat GPT", "Dall E", "Stable Diffusion", "Nano Banana", "Image Creator" đều là ảnh AI. Lớp chặn cuối vẫn là người duyệt ở T-056 (hiện "Ảnh thật / Ảnh AI" từng ảnh, điều kiện 2b Lá Chắn T-052).
- **Ảnh thật thành ảnh AI** (hướng an toàn, ảnh chỉ mất thẻ công trình, không chữ nào đi ra): thư mục chỉ có chữ "SoRa" (gõ liền "so ra", trùng công cụ Sora, có test), và tên có đúng cặp chữ tiếng Anh "mid journey", "fire fly", "co pilot", "see dream". Đúng đánh đổi Lá Chắn đã chấp nhận ở thử T6.
- **Bộ nhớ của `get_many`:** nay giữ mọi dòng của một lần gọi rồi mới kiểm (trước là từng nhóm 400 dòng). Mỗi ô đã bị cắt độ dài khi đọc (`substr`), số dòng không quá số ảnh được hỏi; `list_manual` vốn đã đọc tới 20.000 dòng một lần như vậy. T-056 gọi theo trang tối đa 200 ảnh (điều kiện 2i của Lá Chắn T-074).
- **Lỗi không phải của SQLite khi kiểm dòng** (về lý thuyết; `_row_to_tag` chỉ xử lý chữ) nay xảy ra sau khi kết nối đã đóng, giống `list_manual`: không thể để giao dịch mở (`test_error_while_reading_rows_leaves_no_lock` vẫn qua).
- Đọc thêm một kiểu cho tên thư mục làm việc đọc thẻ chậm thêm khoảng 10 % (một trang 200 ảnh thêm chừng 9 ms).
- Số đo thời gian lấy trên máy đang chạy song song agent khác: con số tuyệt đối chậm hơn máy rảnh; bản cũ và bản mới chạy xen kẽ nên phép so vẫn đúng. Chưa thử trên Mac (thay đổi chỉ ở phần xử lý chữ và thứ tự đọc/xử lý trong `get_many`, không đụng đường dẫn hay file).

## Đề xuất

- **T-069 (README):** đã có điều kiện 3 của Lá Chắn T-074 (gõ tên công cụ theo cách viết liền chuẩn). Nên thêm: muốn chắc chắn thì để chữ "AI" trong tên thư mục ảnh AI ("Ảnh AI - Runway").
- **Chỉ Huy cân nhắc:** nếu muốn bịt thêm "Run Way", "Re Craft" thì chỉ cần thêm 2 dòng vào `_AI_TOOLS` như 4 tên phiếu này (hai chữ tiếng Anh, không trùng chữ tiếng Việt gõ không dấu). Tôi không thêm vì ngoài phiếu.
- **Soi Lỗi, Lá Chắn (rút gọn):** xem thêm docstring `_begin` (sửa ngoài đúng dòng 19-21, lý do ở YC3). Script thử và kết quả: thư mục ghi chú chung của nhóm phiên, `T-077-tho-may-scripts/` (chạy bằng `PYTHONUTF8=1 uv run python <script> <file bản cũ>` trong worktree; bản cũ lấy bằng `git show 378f710:seo_app/images/tags.py`, `git show 378f710:seo_app/storage/image_tags.py`).
- **Lá Chắn, Thư Ký (ghi nhận công cụ):** `detect-secrets scan <file…>` không có `--all-files` lặng lẽ bỏ qua file git chưa theo dõi (kể cả file mồi), ra "0" giả; tôi gặp lần đầu rồi chạy lại đúng cách `security.md` mục 5 (`--all-files` trong thư mục riêng). Có thể thêm một dòng nhắc vào mục 5.

## Câu hỏi cho chủ dự án

Không có.

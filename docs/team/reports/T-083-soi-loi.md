# Báo cáo T-083 · Dọn lỗi chữ nhỏ trong alt, chú thích ảnh AI · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-083](../tickets/T-083-don-loi-chu-mo-ta-anh.md) |
| Nhánh | `team/T-083` (Thợ Máy `eff4f12`, mã `372c265`, gốc `b60054f`) |
| Ngày nộp | 2026-10-27 |
| Kết quả | Hoàn thành (kiểm rút gọn). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn rút gọn được ngay. Yêu cầu 1–4 đạt. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (SL-T083-1: dấu đầu dòng «+ », dấu trích dẫn «> » trước tiền tố vẫn lặp; cùng loại SL-T068-2, có từ trước). Điều kiện: SL-T083-1 được ghi theo dõi (sửa ở lượt 2 hay phiếu dọn sau, Chỉ Huy chọn). **Không lỗi nào phải sửa trước Lá Chắn** |

## Tóm tắt (cho chủ dự án)

- Bản sửa của Thợ Máy làm đúng việc: AI tự viết chữ «Minh họa» theo kiểu lạ (không dấu, có gạch nối, trong dấu `` ` `` hay `_`, sau gạch đầu dòng «- », «1. », hay để «(AI)» tách riêng) thì alt và chú thích nay chỉ còn **đúng một** «Minh họa» / «Ảnh minh họa (AI)». Chú thích không còn bị cụt giữa chữ khi giới hạn ký tự nhỏ. Tôi tự thử 99 câu viết tay, 760 câu alt, chú thích hợp lý ở 4 mức giới hạn và 60.000 cặp câu ngẫu nhiên: tiền tố luôn còn, không quá giới hạn, lọc lại lần nữa không đổi chữ (bản cũ đổi 8.715 lần).
- Chặn «lệnh WordPress» (shortcode), link, thẻ HTML giữ nguyên với mọi kiểu tiền tố mới; ảnh thật không đổi gì (0 khác biệt trên 60.000 cặp).
- Câu alt, chú thích hợp lý không bị từ chối oan: 0 câu báo «AI không viết được alt» mới ở cả giới hạn mặc định lẫn mức thấp nhất được phép. Báo lỗi mới chỉ gặp khi alt AI viết chỉ có tiền tố (đúng quy định cũ), hay chữ đầu là địa chỉ web, mã dính liền quá dài.
- Còn 1 lỗi nhỏ cùng loại (Thấp, có từ trước): AI viết gạch đầu dòng bằng dấu «+ » hay dấu trích dẫn «> » trước «Minh họa» thì vẫn lặp chữ («Minh họa + Minh họa: …»). Sửa nhanh, không ảnh hưởng an toàn; không cần chờ để chuyển sang kiểm bảo mật.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t083.py` | Mới: 759 ca (755 qua, 4 `xfail(strict=True)` của SL-T083-1). Dữ liệu, site giả riêng; không dùng lại dữ liệu của Thợ Máy |
| `docs/team/reports/T-083-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác.

## Kiểm từng yêu cầu

| Việc | Kết quả | Bằng chứng |
|---|---|---|
| **SL-T068-1** tiền tố không dấu, gạch nối, «AI» không ngoặc, gọi khác | **ĐẠT** | `_AI_PREFIX` (`alt.py:362-368`). Test `test_tien_to_kieu_la_chi_con_mot_tien_to_chuan` (18 dạng, thân khác của Thợ Máy: «MINH HOA -», «minh-hoạ:», «Hình‐minh‑họa (ai)», «Buc tranh minh hoa:», «Hinh ve minh hoa AI –», «Tranh vẽ minh hoạ!», khoảng trắng thừa trong cả «( AI )»…): alt, chú thích lưu và gửi đi đúng từng chữ. Alt chỉ có tiền tố như vậy: `test_alt_chi_co_tien_to_kieu_la_bi_tu_choi` báo đúng «AI không viết được alt…», chú thích chỉ còn tiền tố. 23 ca `xfail` cũ của Soi Lỗi T-068 qua |
| **SL-T068-2** Markdown khác `*`, dấu đầu dòng, số thứ tự | **ĐẠT** cho mọi dạng đã nêu; còn **SL-T083-1** (Thấp) với «+ », «> » | `_WRAPPERS` thêm `` ` ``, `_` (`alt.py:380-383`), `_NUMBERED` (`:376`), bỏ dấu câu đầu mỗi vòng (`:427`). Test trên cùng có «- **Minh họa**:», «1. `Minh họa`:», «• Ảnh minh họa (AI) –», «2) _Minh hoạ_», «10. __Minh họa__:», «- [Minh họa]:» (ngoặc vuông + «\» của T-081). Số thứ tự chỉ bỏ khi ngay sau là tiền tố: «3.5 mét…», «Minh họa: 2) lá cửa» giữ nguyên (`test_chu_that_dau_alt_anh_ai_duoc_giu`) |
| **SL-T068-3** chú thích ảnh AI cụt giữa chữ ở 20–21 | **ĐẠT** | Chú thích ảnh AI cắt trọn chữ (`whole_words`, `alt.py:309-324`, `:543-545`). `test_chu_thich_anh_ai_khong_bao_gio_cut_giua_chu`: mọi giới hạn 17–74 × 2 câu dài (một câu có dấu phẩy, một câu «Ở cửacuốnnhàphố…» chữ ngắn rồi chữ rất dài, chỗ cách cắt của alt sẽ cụt): mỗi chữ trong phần thân là một chữ trọn của câu gốc, đúng thứ tự, không quá giới hạn. Thử tay giới hạn 15–23: ở 20–21 «ray dưới bị mòn» ra «Ảnh minh họa (AI)» (bản cũ «…: r», «…: ra»), chữ một ký tự «ở» vẫn vừa. Alt (không được rỗng) giữ cách cắt cũ, chữ đầu dài hơn chỗ còn lại thì báo lỗi (`test_alt_chu_dau_qua_dai_bi_tu_choi_khong_ra_mau_cut`, 3 ca) |
| **LC-T068-1** giới hạn nhỏ hơn tiền tố | **ĐẠT** (ngưỡng 10 / 17, không phải 20: xem dưới bảng) | `_check_ai_limits` (`alt.py:497-506`). `test_gioi_han_alt_duoi_10_bao_loi_khong_cat_tien_to` (1–9), `test_gioi_han_chu_thich_duoi_17_bao_loi_khong_cat_tien_to` (1–16): `ValueError`, câu báo không chép chữ AI. `test_c6_moi_gioi_han_nho_tien_to_con_nguyen`: 8 chuỗi × giới hạn alt 10, 11, 12, 15, 19, 20, 24, 33 × chú thích 17, 18, 19, 20, 21, 25, 31: tiền tố luôn trọn, không quá giới hạn, chạy lại không đổi |
| **SL-T081-1** «(AI)» tách khỏi tiền tố | **ĐẠT** | `_AI_TAG` (`alt.py:372`, `:428-431`). Test trên cùng có «(AI) Minh họa:», «Minh họa – (AI)», «[Ảnh minh họa] ( AI ) :», «Minh họa (AI) (AI)», «AI: «Ảnh minh họa»». 5 ca `xfail` cũ của tôi (T-081) qua. «Ai» viết thường hoa đầu («Ai cũng…») và «AIR», «AIRBLADE» giữ nguyên |
| C6 (tiền tố luôn còn, alt chỉ có tiền tố thì từ chối) | **ĐẠT** | Test trên; thử ngẫu nhiên 60.000 cặp: thiếu tiền tố 0, quá giới hạn 0 |
| Chặn link, shortcode T-061, T-062, T-081 (W3, mục 2.3) | **ĐẠT** | Mục «W3» bên dưới |
| Kết quả bất động | **ĐẠT** | `test_chay_lai_khong_doi_chu` (12 chuỗi lạ × 6 cặp giới hạn, có ngưỡng 10/17, 11/18, có ca cắt lộ tiền tố mới «2) Minh-hoaXYZ…»), `test_c6_moi_gioi_han_nho_…` (448 tổ hợp); thử ngẫu nhiên 0/60.000 (bản cũ 8.715); tập hợp lý 0/3.040 (bản cũ 76 mỗi mức giới hạn) |
| Không chặn oan alt ảnh thật | **ĐẠT** | Đường ảnh thật đi đúng hai dòng cũ (`alt.py:547-548`, `_cut` mặc định như cũ; `drafts._one_line` gọi `clean_alt_text` không đổi). `test_anh_that_nhu_truoc` (4 ca: không bỏ tiền tố, giữ escape, giới hạn 5/6 không báo lỗi, vẫn cắt giữa chữ như trước). Thử ngẫu nhiên 60.000 cặp × giới hạn ngẫu nhiên: ảnh thật khác bản `main` **0** (so cả chữ lẫn kiểu lỗi) |
| Gỡ `xfail` đúng R5 | **ĐẠT** | `git diff --numstat b60054f..HEAD`: `tests/test_soi_loi_t068.py` 0 thêm / 5 xóa, `tests/test_soi_loi_t081.py` 0 / 5; 10 dòng xóa đều là dòng `@pytest.mark.xfail(…)`, thân test và tham số giữ nguyên |

**Ngưỡng LC-T068-1 là 10 / 17 thay cho 20 (Lá Chắn T-068 gợi ý 20):** đạt đúng ý của Lá Chắn: tiền tố **không bao giờ** bị cắt, và bảo đảm nằm ngay trong `alt.py`, không dựa vào mức sàn 20 của `seo_app/content/rules.py`. Lý do Thợ Máy nêu đúng: `tests/test_soi_loi_t081.py::test_cat_do_dai_sau_khi_bo_gach_cheo` (test của tôi ở T-081) gọi ảnh AI với `max_chars=18`. Với 10–19, alt là «Minh họa …» trọn tiền tố (thử tay và test C6 ở trên); với 17–19, chú thích là đúng «Ảnh minh họa (AI)». `ValueError` không tới được từ app: `suggest_alt` lấy giới hạn từ `load_alt_rules()` (sàn 20, `rules.py:89`, `:485-490`), `drafts._ai_prefixed` dùng 500 / 1000; và `app/views/write.py:1046-1047` bắt mọi lỗi lạ bằng câu cố định. Lá Chắn xác nhận lựa chọn này.

### W3 / mục 2.3

- **Chữ lưu trong nháp** (hiện trên Streamlit): `test_chu_luu_va_html_anh_khong_mo_lai_link_the_shortcode` (5 kiểu tiền tố mới × 8 đuôi: `[code_snippet id=1]`, `[[…]]`, `[embed]…[/embed]`, `[gallery ids=1,2]`, link Markdown, thẻ `<a>`, `<img onerror>`, «\[code_snippet…\]» AI tự escape): alt, chú thích lưu là điểm bất động của `escape_link_syntax`, không có `<`, `href`, `javascript`. `figure_html` không còn «[» «]», chỉ thẻ `figure`, `img`, `figcaption`, không «\» khi đầu vào không có.
- **Gửi site giả**: `test_gui_site_gia_tien_to_kieu_moi_van_vo_hieu_shortcode` (3 cặp tiền tố kiểu mới + shortcode, link, thẻ, qua `DraftImage(…, tags=ImageTags(source=SOURCE_AI))`): người đọc thấy đúng chữ, đúng một «Minh họa»; mọi chuỗi JSON gửi đi không có «[», «]», «\», `<a `, `href`.
- **Thử ngẫu nhiên 60.000 cặp** (`fuzz.py`): chữ lưu còn cú pháp link sống 0; HTML ảnh còn «[» «]» hay thẻ lạ 0; 3 ô Media còn «[» «]» 0; chữ gửi đi có «\» mà đầu vào không có 0.
- Lớp vô hiệu «[» «]» khi in ra (`html.py`, `client.py`) không có trong diff; phần thân vẫn qua `clean_alt_text` trước và sau khi ghép tiền tố.

## Thử độc lập (không dùng lại dữ liệu của Thợ Máy)

Script ở thư mục ghi chú chung của các phiên, `T-083-soi-loi-scripts/` (không commit). Chạy trong worktree: `PYTHONUTF8=1 uv run python <script>`; bản `main` của `alt.py` lấy bằng `git show b60054f:seo_app/images/alt.py > old_alt.py` cạnh script.

| Thử | Kết quả |
|---|---|
| `probe.py`: 99 ca viết tay (9 dạng SL-T068-1, 5 alt chỉ có tiền tố, 12 dạng SL-T068-2 gồm «+ », «> », «●», «1 - », «a) », 6 alt chỉ có tiền tố, 5 dạng SL-T081-1, 11 chữ không phải tiền tố, 45 ca chú thích giới hạn 15–23, 6 ca shortcode/link/thẻ sau tiền tố kiểu mới) | 0 cờ (thiếu tiền tố, quá giới hạn, chạy lại đổi chữ, cú pháp link, «\», cụt chữ). Còn lặp: «+ », «> » (SL-T083-1), «●», «▪», «1 - », «a) » (Ghi nhận 2). Giữ đúng «Minh Hòa», «Minh Hóa», «Minh Hoàng», «Minh hoạt», «Hoa văn», «Tranh vẽ cổng», «Hình vẽ kỹ thuật», «AIR», «Ai cũng», «1. Cửa cuốn», «3.5 mét» |
| `fuzz.py`: 60.000 cặp ngẫu nhiên (hạt giống 83083): 0–3 tiền tố từ 27 kiểu (có «Minh Hòa», «Minh hoạt», «Bản vẽ minh họa», «Sơ đồ minh họa», «Ảnh AI») × 26 kiểu mở đầu (không có, ngoặc, `` ` ``, `_`, «- », «• », «* », «+ », «> », «1. », «2) », «10. », `<b>`, ký tự rộng 0) × 21 kiểu nối (có «\:», «\[», «(AI)», «AI:», NBSP, xuống dòng) rồi 0–7 mảnh (shortcode, link, thẻ, email, `www.`, «\», chữ Hán, emoji, «İ», chữ rất dài, «AI», «Ai», «AIR»); giới hạn alt 10–500, chú thích 17–1000 | Ảnh AI, bản mới: thiếu tiền tố **0**, quá giới hạn **0**, chạy lại đổi chữ **0** (bản `main`: 8.715), cú pháp link sống **0**, «\» mới **0**, HTML/ô Media còn «[» «]» **0**, chú thích cụt giữa chữ **0**, lỗi lạ (ngoài `AIError`, `ValueError` dưới ngưỡng) **0**. Ảnh thật khác bản `main` **0**. 3 lần chạy quá 0,5 giây: chạy lại từng ca dưới 1 ms (máy đang chạy song song phiên khác) |
| `fuzz_newerr.py`, `fuzz_newerr_20.py`: xếp mọi ca bản mới báo «AI không viết được alt» mà bản `main` ra alt (11.357/60.000, bộ sinh cố ý dày tiền tố và giới hạn nhỏ) | Giới hạn alt dưới 20 (dưới sàn cấu hình): 6.558. Từ 20 trở lên: 4.306 alt chỉ có tiền tố, dấu (đúng C6), 482 chữ đầu dài hơn chỗ còn lại (giới hạn 20: 170, 21: 155, 25: 82, 29: 52, 30: 22, 40: 1, 125: 0; chữ đầu đều là địa chỉ web, `[code_snippet`, `javascript:alert(1)`, chữ dính liền; bản `main` ra mẩu cụt «Minh họa [code_snippe», «Minh họa javascript:a»), 11 khác (đọc hết: 5 thân là dòng khai báo link «[nhãn]: chữ» mà `clean_ai_text` vốn xóa, như Ghi nhận 1 của Soi Lỗi T-081; 6 thân chỉ còn dấu câu sau khi cắt theo giới hạn 20–21) |
| `corpus.py`: 38 thân alt + 20 thân chú thích viết theo quy tắc `[alt]` × 20 cách mở đầu (có «Minh hoa», «Minh họa AI:», «- », «1. », `` ` ``, «[Minh họa] (AI):», «Tranh minh họa», «Hình vẽ minh họa», «+ », «AI: ») × 4 cặp giới hạn (125/200, 20/20, 30/40, 60/80) | Mỗi cặp giới hạn: AIError mới **0**; thiếu tiền tố 0; chạy lại đổi chữ 0 (bản `main` 76); còn lặp «minh họa» 38 (bản `main` 266 ở 125/200), **cả 38 đều mở đầu «+ »** (SL-T083-1) |
| `mutations.py`: đột biến 9 chỗ sửa trên bản sao `git archive HEAD` + file test mới, chạy `tests/test_soi_loi_t083.py` bằng Python của worktree (`seo_app` nạp từ bản sao ở cả 10 lượt) | Không đổi: 755 qua, 4 xfail. Bỏ bước bỏ «(AI)»/«AI» (SL-T081-1): 110 hỏng. Tiền tố chỉ nhận dạng cũ (SL-T068-1): 17. Bỏ `` ` ``, `_` khỏi ngoặc (SL-T068-2): 6. Không bỏ số thứ tự: 6. Chú thích ảnh AI cắt như alt (SL-T068-3): 19. Bỏ kiểm giới hạn nhỏ (LC-T068-1): 25. Bỏ vòng bỏ tiếp khi cắt lộ tiền tố (bất động): 1. Bỏ bước bỏ dấu câu đầu mỗi vòng (G1): 96. Bỏ quy tắc chữ đầu dài hơn chỗ còn lại: 3. **Bắt cả 9.** (Lượt đầu, 23:38–23:45, lọt 3 chỗ: cắt chú thích như alt, vòng bỏ tiếp, quy tắc chữ đầu; tôi thêm câu chú thích «chữ ngắn rồi chữ rất dài», ca «2) Minh-hoaXYZ…», test chữ đầu quá dài, rồi chạy lại 23:47–23:59) |

## Lỗi tìm thấy

### SL-T083-1 · Thấp · có từ trước · Dấu đầu dòng «+ », dấu trích dẫn «> » trước tiền tố AI tự viết vẫn lặp

- **Cách tái hiện:** `clean_suggestion(AltSuggestion(alt="+ Minh họa: cửa cuốn khe thoáng", caption="> Ảnh minh họa (AI): ray mòn"), ai_generated=True)`; cũng vậy với «>> », «+ **Minh họa**:». Alt chỉ «+ Minh họa» hay «> Minh họa».
- **Mong đợi:** như «- Minh họa: …», «* Minh họa …» (đã sửa): alt «Minh họa cửa cuốn khe thoáng», chú thích «Ảnh minh họa (AI): ray mòn»; alt chỉ có tiền tố thì báo «AI không viết được alt».
- **Thực tế:** alt «Minh họa + Minh họa: cửa cuốn khe thoáng», chú thích «Ảnh minh họa (AI): > Ảnh minh họa (AI): ray mòn»; alt «+ Minh họa» thành «Minh họa + Minh họa», được nhận dù không tả gì. Ở giới hạn 20/20, «+ Minh họa: Cấu tạo ray…» ra đúng alt «Minh họa + Minh họa». Bản `main` y hệt (có từ trước).
- **Nguyên nhân:** `_strip_ai_prefix` bỏ dấu đầu dòng nhờ `_AFTER_PREFIX` («- », «• », `alt.py:388`) và `_WRAPPERS` («* », `:380`), số thứ tự nhờ `_NUMBERED`; «+» (dấu đầu dòng thứ ba của Markdown, cùng «-», «*») và «>» (trích dẫn) không thuộc nhóm nào. `seo_app/sanitize.py:115` coi đúng bộ `>*+-.)` là dấu đầu dòng khi dò dòng khai báo link, nên hai dấu này nên được xử lý như «- », «* ».
- **Hậu quả:** chữ lặp trên alt, chú thích công khai; alt chỉ có tiền tố lọt qua (cùng triệu chứng SL-T068-2, trái ý C6 «alt chỉ có tiền tố thì từ chối» ở dạng này). Không có hệ quả bảo mật. Khả năng gặp thấp hơn «- », «* », «1. » (AI ít dùng «+», «>» trong một ô JSON một dòng).
- **Test:** `tests/test_soi_loi_t083.py::test_sl_t083_1_dau_dau_dong_cong_va_trich_dan_truoc_tien_to` (4 ca: «+ », «> », «>> », «+ **», `xfail(strict=True)`).
- **Gợi ý sửa (Thợ Máy):** thêm «+», «>» vào nhóm dấu bỏ ở đầu mỗi vòng của `_strip_ai_prefix` (ví dụ thêm vào `_AFTER_PREFIX`, hoặc một nhóm riêng chỉ bỏ ở đầu chữ), giữ «ngay sau là tiền tố» nếu muốn không đụng chữ thật như «> 5 mét». Có thể làm kèm các dấu đầu dòng Unicode hay gặp («●», «◦», «▪», Ghi nhận 2). **Không bắt buộc trước Lá Chắn**; Chỉ Huy chọn sửa ở T-083 lượt 2 hay phiếu dọn sau.

## Ghi nhận (không phải lỗi của T-083)

1. **«AI» viết hoa đứng đầu phần thân bị bỏ** (Rủi ro 1, 2 của Thợ Máy, đúng như mô tả): «AI robot hàn cổng sắt» ra «Minh họa robot hàn cổng sắt». Phần còn lại có khi xấu: «AI's cổng sắt» ra «Ảnh minh họa (AI): 's cổng sắt», «AI_tạo cổng» ra «… _tạo cổng», «AI-generated cổng» ra «Minh họa generated cổng». Chỉ ảnh AI, chữ tiếng Anh ít gặp trong alt tiếng Việt; tiền tố chuẩn vẫn nói ảnh do AI làm.
2. **Dấu đầu dòng Unicode khác và đánh số kiểu khác** («● », «▪ », «◦ », «1 - », «a) ») trước tiền tố vẫn lặp như bản `main`. Nhóm này không có giới hạn rõ, tôi không ghi thành lỗi; nếu sửa SL-T083-1 thì có thể thêm vài dấu hay gặp.
3. **Cách gọi khác chưa nhận**: «Bản vẽ minh họa…», «Sơ đồ minh họa…», «Hình ảnh mô phỏng…» ra «Minh họa sơ đồ minh họa cấu tạo…» (lặp «minh họa», như bản `main`). Bỏ luôn «Sơ đồ», «Bản vẽ» thì mất ý ảnh là sơ đồ; nên để nguyên, hoặc Ngòi Bút dặn AI viết «Minh họa sơ đồ…». Hệ quả nhỏ kèm theo: chú thích cắt trọn chữ có thể dừng ở «… sơ đồ minh» (đúng chữ trọn, đọc hơi cụt ý).
4. **Quy tắc «chữ đầu dài hơn chỗ còn lại» ở mức sàn 20** (chỗ còn 11 ký tự): chữ đầu là địa chỉ web, `[code_snippet`, chữ dính liền dài thì alt báo «AI không viết được alt» (bản `main` ra mẩu cụt). Ở mặc định 125: 0 ca trong thử ngẫu nhiên, 0 trong tập hợp lý. Chữ đầu được đếm cả ký tự rộng 0 mà `clean_ai_text` chèn vào địa chỉ, email (T-031), nên «a@e.test» (8 ký tự nhìn thấy) tính 9.
5. **«Minh hoa» không dấu luôn được coi là tiền tố**: «Minh hoa sen trên cổng» ra «Minh họa sen trên cổng». Câu không tự nhiên (AI viết có dấu thì là «Minh họa hoa sen…», vẫn đúng); đổi lại «Minh Hòa», «Minh Hóa», «Minh Hoàng», «Minh hoạt» được giữ đúng.
6. Dòng khai báo link «[nhãn]: chữ» lộ ra đầu phần thân sau khi bỏ tiền tố («_Minh họa_:\n[Minh Hòa]: 2)») bị `clean_ai_text` xóa như mọi alt ảnh thật (Ghi nhận 1 của Soi Lỗi T-081); 5 ca ở giới hạn alt từ 20 trong 60.000 cặp ngẫu nhiên, toàn chuỗi dựng.
7. `main` đã đi tiếp tới `2d22c7b` (tài liệu, `app/views/settings.py` và test cài đặt của T-084, 3 gói rỗng của Giai đoạn 5; không đụng `alt.py` hay nơi gọi nó): `git merge-tree --write-tree origin/main HEAD` không xung đột.

## Bằng chứng

Máy Windows 11 Pro (10.0.26300) của chủ dự án, Python 3.12.15 (uv), worktree `wt-T-083`, nhánh `team/T-083` (`eff4f12`). Máy chạy song song các phiên khác nên test chạy lâu.

Test liên quan: 9 file trong tiêu chí xong của phiếu, cộng **mọi file test** gọi tới `clean_suggestion`, `clean_alt_text`, `suggest_alt`, `clean_loaded`, `seo_app.images.alt`, `seo_app.storage.drafts` hay `app/views/write.py` (lấy bằng `grep` trên `tests/test_*.py`, gồm cả test mới của Thợ Máy và của tôi): 53 file, danh sách ở `T-083-soi-loi-scripts/related_files.txt`.

```
$ uv run pytest -q -p no:cacheprovider -rxXfs <53 file>
(2026-10-27 23:30:53 → 2026-10-28 00:32:56 +0700)
7026 passed, 20 skipped, 8 xfailed in 3706.05s (1:01:46)

$ uv run pytest -q -p no:cacheprovider tests/test_soi_loi_t083.py     # bản cuối của file test mới
755 passed, 4 xfailed in 45.19s

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check tests/test_soi_loi_t083.py
1 file already formatted
```

- 0 hỏng, 0 XPASS. 8 `xfailed`: SL-T083-1 (4 ca, lỗi mới); còn lại có từ trước, không liên quan: `tests/test_soi_loi_round4.py::test_r4_3_code_span_is_not_escaped` (2), `tests/test_soi_loi_t003_t009.py::test_keyword_cannot_fake_a_frame` (1), SL-T041-8 `tests/test_soi_loi_t041.py::test_sl_t041_8_new_emoji_is_not_blocked` (1). 20 bỏ qua đều do máy: symlink, quyền POSIX chỉ thử trên Mac/Linux, Windows chưa bật Developer Mode, ổ không phân biệt hoa thường.
- Lượt 53 file chạy với file test mới khi còn 692 ca; sau đó tôi chỉ thêm ca vào chính file đó (để thử đột biến bắt đủ 9 chỗ) và chạy lại riêng file đó (dòng thứ hai ở trên). Code ứng dụng không đổi giữa hai lượt.
- 28 ca `xfail` cũ (23 SL-T068 trong `tests/test_soi_loi_t068.py`, 5 SL-T081-1 trong `tests/test_soi_loi_t081.py`) nay qua trong lượt trên.
- Quét bí mật: chép `tests/test_soi_loi_t083.py` và 6 script thử vào thư mục nháp, thêm một file mồi có chữ tiếng Việt (một khóa AWS giả, một dòng `password = …` giả), chạy `PYTHONUTF8=1 uvx --offline detect-secrets scan --all-files .`: mồi **bắt đủ 2/2**, file của Soi Lỗi: **0**.
- Không gọi WordPress, AI hay Google thật: test dùng `FakeWordPress` (fixture `fake_wp`, `wp_client`); bộ chặn mạng của `tests/conftest.py` bật cho mọi test.

## Đối chiếu việc được giao

- [x] 5 lỗi đóng đúng ý: tiền tố AI tự viết kiểu lạ không lặp, không cụt; chú thích ảnh AI ở giới hạn nhỏ; «(AI)» tách rời (mục «Kiểm từng yêu cầu»); còn SL-T083-1 cùng loại SL-T068-2
- [x] Giữ C6 (tiền tố AI luôn còn, alt chỉ có tiền tố thì từ chối) và lớp chặn link, shortcode của T-061, T-062, T-081 (mục «W3»)
- [x] Kết quả bất động: chạy lại `clean_suggestion` không đổi chữ
- [x] Không chặn oan alt ảnh thật (0 khác biệt với bản `main`); alt ảnh AI hợp lý không bị từ chối oan (0 AIError mới trong tập hợp lý)
- [x] Gỡ `xfail` đúng R5 (chỉ xóa 10 dòng dấu)
- [x] Không sửa code ứng dụng; lỗi mới ghi thành test `xfail(strict=True)` SL-T083-1 trong `tests/test_soi_loi_t083.py`
- [x] Test liên quan (lệnh trong tiêu chí xong của phiếu + mọi file test gọi `clean_suggestion`, `clean_alt_text`, `suggest_alt`, `clean_loaded`, `seo_app.storage.drafts`, `app/views/write.py`) và `uv run ruff check .` (mục «Bằng chứng»)

## Rủi ro và điểm cần chú ý

- Thử ngẫu nhiên và tập câu hợp lý là chữ dựng sẵn, không phải chữ AI thật trả về (test không được gọi AI thật).
- 4 test `xfail(strict=True)` của SL-T083-1: sửa xong thì thành XPASS và báo hỏng, chỉ cần xóa dòng `@pytest.mark.xfail`. Nếu chỉ sửa «+» mà không sửa «>», hai ca «> », «>> » vẫn `xfail` (không báo hỏng); khi đó nên tách lại dấu `xfail` cho rõ.
- Máy chạy song song các phiên khác: thời gian chạy test dài, 3 lần chạy chậm trong thử ngẫu nhiên là do máy (chạy lại dưới 1 ms).

## Đề xuất

1. **Chỉ Huy:** chuyển T-083 sang Lá Chắn rút gọn ngay. **SL-T083-1** (Thấp): sửa ở T-083 lượt 2 (một nhóm dấu trong `_strip_ai_prefix`, gỡ 4 `xfail`) hoặc gom phiếu dọn sau; không chặn Lá Chắn, không chặn gộp.
2. **Lá Chắn (rút gọn, W3):** xác nhận ngưỡng 10 / 17 thay cho 20 (mục «Kiểm từng yêu cầu»); lớp vô hiệu «[» «]» khi in ra không đổi; chữ gửi AI không đổi (`alt_system`, `alt_prompt` không có trong diff). Script và log thử ở `T-083-soi-loi-scripts/` (thư mục ghi chú chung).
3. **Ngòi Bút (tùy chọn):** Ghi nhận 3 («Sơ đồ minh họa…», «Bản vẽ minh họa…»): dặn AI đặt «Minh họa» lên đầu rồi mới tả loại hình.

## Câu hỏi cho chủ dự án

Không có.

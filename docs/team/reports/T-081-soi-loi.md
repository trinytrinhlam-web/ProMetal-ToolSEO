# Báo cáo T-081 · Bỏ dấu «\» sót ở alt, chú thích ảnh AI (SL-T071-1) · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-081](../tickets/T-081-dau-gach-cheo-alt-anh-ai.md) |
| Ngày nộp | 2026-10-23 |
| Kết quả | Hoàn thành (kiểm rút gọn). **Kết luận: ĐẠT**, chuyển Lá Chắn rút gọn được ngay. Yêu cầu 1–4 đạt. 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp có từ trước** (SL-T081-1: có từ T-062, ngoài phạm vi phiếu, T-081 không gây ra; **không phải điều kiện gộp T-081**, không chặn T-056) |

## Tóm tắt (cho chủ dự án)

- Bản sửa của Thợ Máy làm đúng việc: AI viết mô tả ảnh minh họa kiểu «[Minh họa]: Cổng inox…» thì alt và chú thích lên website nay là «Minh họa cổng inox…», «Ảnh minh họa (AI): cổng…», hết dấu «\» thừa. Tôi tự thử 7 dạng của phiếu và hơn 150.000 câu viết lạ (ngoặc lồng nhiều lớp, ký tự vô hình, khoảng trắng lạ, viết hoa, bị cắt ngắn…): **không câu nào** còn dấu «\» do phần mềm tự thêm (bản cũ: hơn 25.000 câu còn).
- Lớp chặn «lệnh WordPress» giữ nguyên: mọi dấu «[» «]» vẫn đổi thành mã ký tự trước khi gửi, kể cả khi ngay sau tiền tố là đoạn trông như lệnh (`[code_snippet id=1]`, `[embed]…[/embed]`) hay link, thẻ HTML. Ảnh thật không đổi gì. Mở lại bài nháp có ảnh AI cũng được sửa theo.
- Điểm mới cần biết (đúng như Thợ Máy nêu): câu kỳ lạ kiểu «[Minh họa]: [Lưu ý]: Cửa» (nhãn thứ hai rồi đúng một chữ) nay báo «AI không viết được alt, bấm thử lại», giống cách phần mềm đã xử lý «Minh họa: [Lưu ý]: Cửa» từ trước. Trên 3.840 câu alt, chú thích hợp lý: chỉ 40 câu báo lỗi mới, đều đúng dạng một chữ đó; câu nhiều chữ không bị.
- Tìm thêm 1 lỗi nhỏ **có từ trước** (không do phiếu này): AI viết «(AI)» tách khỏi tiền tố, như «[Minh họa] (AI): Cổng inox», thì chú thích ra «Ảnh minh họa (AI): (AI): Cổng inox» (lặp chữ). Nên gom vào lần dọn lỗi nhỏ phần alt sau này; không cần làm trước màn hình chọn ảnh.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t081.py` | Mới: 126 ca (121 qua, 5 `xfail(strict=True)` của SL-T081-1). Dữ liệu, site giả riêng; không dùng lại dữ liệu của Thợ Máy |
| `docs/team/reports/T-081-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác.

## Kiểm từng yêu cầu

| Yêu cầu | Kết quả | Bằng chứng |
|---|---|---|
| 1. Bỏ ngoặc đóng của tiền tố thì bỏ luôn «\» do `escape_link_syntax` thêm | **ĐẠT** | `git diff 1d1e53e..team/T-081 -- seo_app`: chỉ `seo_app/images/alt.py`, hằng `_LINK_ESCAPES` (`alt.py:363`) và 2 dòng (`alt.py:391-392`), còn lại là chú thích. Điều kiện «ngoặc đóng tận cùng bằng «]» và ngay sau là `\:`, `\[`, `\(`» đúng bằng 3 chỗ `escape_link_syntax` thêm «\» (`sanitize.py:507`, «]» rồi «(», «[», hay «:» khi nhãn đứng đầu dòng); ngoặc đóng của tiền tố luôn mở ở đầu chữ nên «:» sau nó luôn được escape. Lý do chọn cách 1 (báo cáo Thợ Máy) hợp lý: cách 2 phải gỡ escape cả câu, mở lại link đã bị vô hiệu ở giữa câu. Thử đột biến 6 kiểu trên bản sao: test mới bắt cả 6 (mục «Thử đột biến») |
| 2. Đủ biến thể ra «Minh họa …», «Ảnh minh họa (AI): …», không «\» (qua `clean_suggestion` và `DraftImage(…, tags=ImageTags(source=SOURCE_AI))` gửi site giả) | **ĐẠT** | Test: `test_bien_the_cua_phieu_ra_dung_chu_khong_gach_cheo` (6 dạng «:» của phiếu, thân khác của Thợ Máy), `test_bien_the_ngoac_mo_cua_phieu_…` (dạng «[»), `test_tien_to_ngoac_vuong_bien_the_la_giong_khong_ngoac` (20 dạng: ký tự vô hình U+200B, U+200C, U+200D, U+2060, BOM, gạch nối mềm ở trước, trong, sau ngoặc; NBSP, U+3000, U+2003, tab, xuống dòng, dấu cách trong ngoặc, viết hoa/thường, «Minh hoạ», chữ NFD, ngoặc lồng `[[…]]`, `[**…**]`, `[“…”]`, `[(Ảnh minh họa (AI))]`, `[Minh họa…]`, tiền tố lặp: kết quả bằng đúng khi AI viết «Minh họa: …»), `…_roi_ngoac_tron_hay_vuong_…` (8 dạng «(», «[», ngoặc lồng, thiếu ngoặc đóng), `…_nhan_thu_hai_nhieu_chu_…`, `test_cat_do_dai_sau_khi_bo_gach_cheo` (3 cỡ cắt). Gửi site giả: `test_gui_site_gia_alt_chu_thich_dung_chu_khong_gach_cheo` (6 dạng): `alt` của `<img>`, `<figcaption>` như trình duyệt đọc, `alt_text`, tiêu đề `[AI] …`, `caption` gửi REST đúng chữ; mọi chuỗi JSON gửi đi không có «\», «[», «]» |
| 3. Không nới chặn link, shortcode (T-061, T-062); «\» ở chỗ khác giữ nguyên; ảnh thật không đổi | **ĐẠT** | Mục «W3 / 2.3» bên dưới. «\» AI gõ ở chỗ khác: `test_gach_cheo_ai_go_o_cho_khac_giu_nguyen` (6 ca, có «\» sau ngoặc đóng không phải «]»). Ảnh thật: `test_anh_that_khong_bo_tien_to_va_giu_escape_nhu_truoc` (3 ca); so bản `main` trên 150.000 chuỗi thử ngẫu nhiên, 3.840 câu hợp lý, 80 chuỗi thử tay: ảnh thật khác nhau **0** (về cấu trúc cũng không thể khác: `_strip_ai_prefix` chỉ chạy khi `ai_generated`, `alt.py:445`) |
| 4. Gỡ `xfail` 2 ca SL-T071-1 | **ĐẠT** | `git diff 1d1e53e..team/T-081 -- tests/test_soi_loi_t071.py`: xóa đúng 5 dòng `@pytest.mark.xfail(strict=True, reason=…)`, 0 dòng thêm; tham số và thân test giữ nguyên (R5). 2 ca qua |

### W3 / mục 2.3: bỏ «\» không mở lại link, thẻ, shortcode

- **Chữ gửi WordPress**: dấu «\» bị bỏ chỉ nằm trong chữ đã lưu của ảnh AI; bước vô hiệu «[» «]» (`escape_shortcodes` trong `sanitize_html` cho nội dung, `client.py:1205-1209` cho ô Media) và `plain_image_text` (`html.py:66`) không đổi. `test_gui_site_gia_shortcode_link_the_sau_tien_to_van_bi_vo_hieu` (18 chuỗi đặt ngay sau tiền tố: `[code_snippet id=1]` sau «]» và sau «:», `[[code_snippet id=1]]` sau «]» và sau «: », `[embed]https://…[/embed]`, `[/code_snippet]`, `([code_snippet id=1])`, `[caption]…[/caption]`, `[gallery ids=1,2]`, tên shortcode chen ký tự rộng 0 hay thẻ `<b>`, link Markdown, link lồng trong ngoặc, `javascript:`, thẻ `<a>`, `<img onerror>`, «\» AI gõ trước «(»): người đọc thấy đúng chữ, không «\»; trang chỉ có thẻ `figure`, `img`, `figcaption`; mọi chuỗi JSON gửi đi không có «[», «]», «\», `<a `, `onerror`, `javascript:`.
- **Chữ lưu trong nháp, hiện trên Streamlit**: bỏ «\» làm «[», «(» của phần thân đứng trần, nhưng phần thân được lọc lại (`clean_alt_text` → `clean_ai_text`) rồi mới ghép tiền tố. `test_chu_da_luu_khong_con_cu_phap_link_hay_the_song` (18 chuỗi trên): alt, chú thích đã lưu là điểm bất động của `escape_link_syntax` (không còn «](», «][», «]:» đầu dòng chưa escape), không có `<`, `href`, `javascript`; chạy lại không đổi. `test_html_anh_khong_con_ngoac_vuong_tran_hay_the_la`: `figure_html` không còn «[» «]» «\».
- **Thử ngẫu nhiên 150.000 chuỗi** (`fuzz.py`, mục «Thử độc lập»): 0 chuỗi còn «[» «]» trần hay thẻ lạ trong HTML ảnh, 0 chuỗi trong 3 ô Media, 0 chữ đã lưu còn cú pháp link sống.

## Thử độc lập (không dùng lại dữ liệu của Thợ Máy)

Script ở thư mục ghi chú chung của các phiên, `T-081-soi-loi-scripts/` (không commit). Chạy trong worktree: `PYTHONUTF8=1 uv run python <script>`; bản `main` của `alt.py` lấy bằng `git show 1d1e53e:seo_app/images/alt.py > old_alt.py` cạnh script.

| Thử | Kết quả |
|---|---|
| `probe.py`: 80 cặp alt/chú thích viết tay (7 dạng của phiếu, ngoặc lồng 1–4 lớp, `[_…_]`, `` [`…`] ``, «[Minh họa](…)» 7 kiểu, 9 loại ký tự vô hình, 7 kiểu khoảng trắng lạ, hoa/thường, NFD, «Minh hoa» không dấu, nhãn thứ hai, «\» AI gõ, 9 dạng shortcode, HTML, link, địa chỉ, chuỗi rỗng) | Bản mới: chỉ 4 cặp còn «\», đều là «\» AI tự gõ ở chỗ khác (`\\:`, `\[cổng]` trong thân, `C:\Users`, `] \:` có dấu cách), đúng yêu cầu 3. 0 chữ đã lưu còn cú pháp link sống, 0 chạy lại đổi chữ. Ảnh thật khác bản `main`: 0 |
| `fuzz.py`: 150.000 chuỗi ngẫu nhiên (hạt giống cố định 81081): 85% mở đầu bằng 18 kiểu ngoặc mở × 9 tiền tố × 23 kiểu nối (có `\:`, `\[`, `\(`, ký tự rộng 0, NBSP, xuống dòng), 15% lặp tiền tố, rồi 0–9 mảnh (chữ, ngoặc, «\», shortcode, URL, email, thẻ, ký tự vô hình, `&#91;`) | Chuỗi vào không có «\» mà alt/chú thích gửi đi còn «\»: **0** (bản `main`: **25.426**). HTML ảnh còn «[» «]» hay thẻ lạ: 0. 3 ô Media còn «[» «]»: 0. Chữ đã lưu còn cú pháp link: 0. Ảnh thật khác bản `main`: 0. Xếp loại ảnh AI: giống 109.874 · chỉ bỏ «\» 30.471 · bỏ «\» kèm bỏ thêm tiền tố lặp, ngoặc, dấu 7.820 · lỗi mới 1.799 (`fuzz_newerr.py` xét hết: 1.793 ca alt bản `main` chỉ có tiền tố, ngoặc, dấu câu, `_`, `` ` ``, không có chữ mô tả nào; 6 ca thân «[nhãn]: một-chữ») · khác 36 (35 là «(AI)» còn lại: SL-T081-1; 1 là chú thích «[nhãn]:» bị bỏ: Ghi nhận 1) · hết lỗi 0 |
| `fuzz_changed.py`: cùng 150.000 chuỗi, mọi chuỗi bản mới khác bản `main` | **40.126/40.126** chuỗi đổi đều là chuỗi bản `main` để lại «\» trong alt hay chú thích gửi đi. Khớp nhận định của Thợ Máy «chỉ đổi đúng những câu từng dính dấu «\» thừa» |
| `fuzz_i4.py`: chạy lại `clean_suggestion` trên kết quả (bất động) | 221 chuỗi bản mới không bất động mà bản `main` bất động: **cả 221** có alt mở đầu «Minh họa (AI)» (SL-T081-1). 2.823 chuỗi không bất động ở cả hai bản (thân mở đầu bằng dấu câu, có từ trước) |
| `corpus.py`: 40 thân alt + 30 thân chú thích viết tay theo quy tắc `[alt]` × 16 cách AI hay mở đầu × 6 kiểu nhãn thứ hai = 3.840 cặp | Bản mới còn «\»: 0 (bản `main`: 1.190). AIError mới (bản `main` ra alt): **40**, đều dạng «[tiền tố]: [nhãn]: một-chữ» với 2 thân một chữ cố ý đưa vào («Cửa», «Inox»); 38 thân nhiều chữ: 0. Chú thích chỉ còn tiền tố (bản `main` còn thân): 85, đều thân «[nhãn]: một-chữ» hay thân chỉ là «minh họa» (Ghi nhận 1). Ảnh thật khác nhau: 0 |
| `consistency.py`: «[nhãn]: một-chữ» ở bản `main` | «Minh họa: [Lưu ý]: cổng», «[Minh họa] [Lưu ý]: cổng», ««Minh họa»: [Lưu ý]: cổng» và ảnh thật «[Lưu ý]: cổng» đều đã báo AIError (alt), chú thích đều chỉ còn tiền tố (hay rỗng ở ảnh thật). Bản mới đưa «[Minh họa]: [Lưu ý]: cổng» về đúng cách đó |

### Hành vi mới «[Minh họa]: [nhãn]: một-chữ» → AIError (việc 4)

Đúng như Thợ Máy mô tả (mục Rủi ro của báo cáo Thợ Máy): sau khi bỏ tiền tố và «\», phần thân «[Lưu ý]: Cửa» đứng đầu dòng, `clean_ai_text` coi là dòng khai báo link Markdown (`_MD_LINK_DEF`, `sanitize.py:104`) và xóa, alt rỗng → `AIError(EMPTY_ALT_MESSAGE)`. Không làm hỏng câu thường gặp: 38/38 thân nhiều chữ trong tập hợp lý vẫn ra alt; dạng «[Minh họa]: Cửa» (không có nhãn thứ hai) đã báo lỗi từ trước, không đổi. Hướng an toàn (không gửi gì lên website). Test: `test_nhan_roi_dung_mot_chu_bao_loi_nhu_dang_khong_ngoac` (6 ca, có 3 dạng đã báo lỗi từ trước), `test_nhan_mot_chu_o_anh_that_cung_bao_loi_tu_truoc`, `test_cau_thuong_gap_van_ra_alt` (4 ca), `test_chu_thich_nhan_roi_mot_chu_chi_con_tien_to_nhu_dang_khong_ngoac`.

### Soát test của Thợ Máy (việc 5)

- `tests/test_soi_loi_t071.py`: chỉ gỡ dấu `xfail` (5 dòng), đúng R5 (yêu cầu 4 ở trên).
- `tests/test_t081_alt_gach_cheo.py` (48 ca) kiểm đúng ý: so chữ chính xác của alt, chú thích; so với dạng không ngoặc vuông; chạy lại không đổi; tổ hợp 552 chuỗi kiểm sau `plain_image_text`; «\» chỗ khác giữ; ảnh thật; site giả kiểm mọi chuỗi JSON không có «\», «[», «]»; 8 chuỗi shortcode, link, thẻ ngay sau tiền tố. Thiếu (tôi bổ sung trong file của mình): ký tự vô hình, khoảng trắng lạ, chữ NFD trong test (Thợ Máy chỉ thử bằng script); đường mở lại nháp (`clean_loaded` → `_ai_wording` → `_ai_prefixed`, `drafts.py:177`, `:308`, `:635`, dùng chính `clean_suggestion`); điều kiện tổng quát «chữ đã lưu không còn cú pháp link sống».

### Mở lại nháp (đường thứ hai dùng `clean_suggestion`)

`_ai_prefixed` (`drafts.py:177`) ghép tiền tố cho ảnh AI có alt chưa mở đầu «Minh họa» bằng chính `clean_suggestion`, nên T-081 sửa luôn đường này: ảnh AI lưu alt «[Minh họa]: Cửa cuốn…» mở lại thành «Minh họa cửa cuốn…», không «\». Test `test_mo_lai_nhap_anh_ai_tien_to_ngoac_vuong_khong_gach_cheo`.

### Thử đột biến (test mới có bắt được không)

`mutations.py`: chép `git archive HEAD` + file test mới vào thư mục nháp, sửa dòng sửa của T-081 trong bản sao, chạy `tests/test_soi_loi_t081.py` bằng Python của worktree; mỗi lượt kiểm `seo_app` nạp từ bản sao (lượt cuối: mục «Bằng chứng»).

| Đột biến | Kết quả |
|---|---|
| M0 không đổi | 121 qua, 5 xfail |
| M1 bỏ hẳn bước gỡ «\» | 83 hỏng |
| M2 chỉ gỡ trước «:» | 35 hỏng |
| M3 không gỡ trước «[» | 27 hỏng |
| M4 không gỡ trước «(» | 8 hỏng |
| M5 gỡ mọi «\» đứng sau «]» (cả «\\») | 1 hỏng |
| M6 gỡ cả khi ngoặc đóng không phải «]» | 2 hỏng |

## Lỗi tìm thấy

### SL-T081-1 · Thấp · có từ trước (T-062), ngoài phạm vi T-081 · «(AI)» viết tách khỏi tiền tố bị lặp trong alt, chú thích ảnh AI

- **Cách tái hiện:** `clean_suggestion(AltSuggestion(alt=t, caption=t), ai_generated=True)` với `t` là «[Minh họa] (AI): Cổng inox 2 cánh», «**Ảnh minh họa** (AI): Cổng inox 2 cánh», ««Minh họa» (AI) Cổng inox 2 cánh», «Minh họa: (AI) Cổng inox 2 cánh», «[Minh họa]: (AI) Cổng inox 2 cánh».
- **Mong đợi:** như khi AI viết liền «Minh họa (AI): Cổng inox 2 cánh» (`_AI_PREFIX` nhận «(AI)» đứng ngay sau): alt «Minh họa cổng inox 2 cánh», chú thích «Ảnh minh họa (AI): cổng inox 2 cánh».
- **Thực tế:** alt «Minh họa (AI): Cổng inox 2 cánh» (hay «Minh họa (AI) Cổng inox 2 cánh»), chú thích «Ảnh minh họa (AI): (AI): Cổng inox 2 cánh»; chạy lại `clean_suggestion` thì đổi chữ (không bất động). Bốn dạng đầu ra y vậy ở bản `main`; dạng thứ năm ở bản `main` ra «Minh họa \: (AI) Cổng inox 2 cánh» (còn «\»), T-081 bỏ «\» nên nó về cùng nhóm.
- **Nguyên nhân:** `_AI_PREFIX` (`alt.py:347-350`) chỉ nhận «(AI)» khi đứng ngay sau «minh họa»; có ngoặc đóng hay dấu câu xen giữa thì vòng lặp của `_strip_ai_prefix` (`alt.py:379-395`) thấy phần còn lại «(AI): …» mở đầu bằng ngoặc «(» rồi chữ «AI)» (không phải tiền tố), nên giữ nguyên.
- **Hậu quả:** chữ lặp «(AI): (AI)» trên chú thích công khai, alt có «(AI):» thừa. Không có hệ quả bảo mật. Ít gặp hơn SL-T071-1 (AI được dặn viết liền «Ảnh minh họa (AI)», `alt.py:138-140`), nhưng AI hay in đậm, đóng ngoặc phần chữ rồi để «(AI)» ngoài.
- **Test:** `tests/test_soi_loi_t081.py::test_sl_t081_1_ai_tach_khoi_tien_to_khong_bi_lap` (5 ca, `xfail(strict=True)`).
- **Gợi ý sửa (Thợ Máy):** trong vòng lặp của `_strip_ai_prefix`, sau khi bỏ tiền tố, ngoặc đóng và dấu câu, nếu phần còn lại mở đầu bằng «(AI)» (không phân biệt hoa thường, cho phép khoảng trắng trong ngoặc) thì bỏ luôn rồi lại bỏ dấu câu. Gom vào phiếu dọn lỗi Thấp phần alt cùng SL-T068-1 → -3. **Không bắt buộc trước T-056.**

## Ghi nhận (không phải lỗi của T-081)

1. **Chú thích «[Minh họa]: [nhãn]: một-chữ» chỉ còn tiền tố**: chú thích không báo lỗi như alt, phần thân bị bỏ, chú thích thành «Ảnh minh họa (AI)». Báo cáo Thợ Máy mới nêu phía alt. Giống hệt cách bản `main` xử lý «Minh họa: [Lưu ý]: cổng» (`consistency.py`). Test `test_chu_thich_nhan_roi_mot_chu_chi_con_tien_to_nhu_dang_khong_ngoac`. Cùng gốc với Đề xuất 1 của Thợ Máy (`clean_ai_text` xóa dòng «[nhãn]: một-chữ»).
2. **Chuỗi chỉ có tiền tố lặp** («[Minh họa]: [Minh họa]», «[Ảnh minh họa][[Hình ảnh minh họa]][_») nay báo AIError thay vì ra alt rác «Minh họa \: [Minh họa]» (1.793/150.000 chuỗi thử ngẫu nhiên): đúng thiết kế SL-T062-1 (alt chỉ có tiền tố bị từ chối).
3. **«\» AI tự gõ sát sau «]» của tiền tố** (kể cả bị ký tự vô hình che: `[Minh họa]\u2063\: …`) cũng bị bỏ, đã nêu ở báo cáo Thợ Máy; trong Markdown `\:`, `\[`, `\(` vẫn là «:», «[», «(», ảnh thật cũng gỡ như vậy.
4. **Ngoặc vuông mở dư** («[[Minh họa] cửa», «[minh hoạ][[MINH HỌA]: …») để lại «]» lẻ trong alt: có từ trước (cách đếm ngoặc mở của `_strip_ai_prefix`), không có «\», không mở được gì. Cùng nhóm với «[Minh họa cổng inox][x]» Thợ Máy đã nêu.
5. **Thân mở đầu bằng dấu câu** («Minh họa: :cổng», 2.823/150.000 chuỗi) không bất động khi chạy lại `clean_suggestion` ở cả bản `main` lẫn bản mới. Đường mở lại nháp chỉ ghép lại tiền tố khi alt chưa mở đầu «Minh họa» (`drafts.py:318`), nên không gặp.
6. `main` đã đi tiếp tới `367c3bf` (chỉ tài liệu); `git merge-tree --write-tree origin/main HEAD`: không xung đột.

## Bằng chứng

Máy Windows 11 Pro (10.0.26300) của chủ dự án, Python 3.12.15, worktree `wt-T-081`, nhánh `team/T-081` (Thợ Máy `96e9e11`, gốc `1d1e53e`). Máy đang chạy song song các agent khác.

```
$ uv run pytest -q -p no:cacheprovider -rxXfs tests/test_soi_loi_t071.py tests/test_t081_alt_gach_cheo.py \
    tests/test_t062_alt_prompt.py tests/test_soi_loi_t062.py tests/test_soi_loi_t054.py \
    tests/test_soi_loi_t068.py tests/test_shortcode_t061.py tests/test_soi_loi_t061.py \
    tests/test_wordpress_images.py tests/test_ai_images.py tests/test_soi_loi_t081.py
(2026-10-23 14:21:13 → 14:22:07)
1479 passed, 34 xfailed in 48.58s

$ uv run ruff check .
All checks passed!
```

- 11 file: 10 file lời giao và file mới của Soi Lỗi. 0 hỏng, 0 XPASS. 34 `xfailed`: SL-T081-1 (5 ca, lỗi mới, có từ trước); còn lại là lỗi cũ không liên quan: SL-T068-1 (8), SL-T068-2 (11), SL-T068-3 (4) trong `tests/test_soi_loi_t068.py`; SL-T061-1 (4), SL-T061-2 (2) trong `tests/test_soi_loi_t061.py` (thuộc T-060). Lượt trước đó (14:19:36 → 14:20:53) cùng kết quả.
- Thêm các file đụng đường mở lại nháp (dùng `clean_suggestion` qua `_ai_prefixed`): `tests/test_drafts_images.py tests/test_soi_loi_t055.py tests/test_storage_drafts.py tests/test_soi_loi_t076.py tests/test_la_chan_t076.py tests/test_app_drafts.py tests/test_soi_loi_t016_t020.py tests/test_soi_loi_t021_t017.py tests/test_images_folders_t063.py` (14:14:12 → 14:15:31): `604 passed, 18 skipped`; 18 bỏ qua đều do máy (symlink, quyền POSIX chỉ thử trên Mac/Linux; ổ không phân biệt hoa thường).
- `uv run ruff format --check tests/test_soi_loi_t081.py`: đã đúng định dạng.
- Thử đột biến lượt cuối (14:22–14:23): kết quả như bảng ở mục «Thử đột biến», `seo_app` nạp từ bản sao ở cả 7 lượt (log `T-081-soi-loi-scripts/related_tests.log`).
- Quét bí mật: chép `tests/test_soi_loi_t081.py` và các script thử vào thư mục nháp, thêm một file mồi có chữ tiếng Việt (một khóa AWS giả, một dòng `password = …` giả), chạy `PYTHONUTF8=1 uvx --offline detect-secrets scan --all-files .`: mồi **bắt đủ 2/2**, file của Soi Lỗi: **0**.
- Không gọi WordPress, AI hay Google thật: test dùng `FakeWordPress` (fixture `fake_wp`, `wp_client`); bộ chặn mạng của `tests/conftest.py` bật cho mọi test.

## Đối chiếu việc được giao

- [x] 1. Đọc diff, xác nhận yêu cầu 1–4 (mục «Kiểm từng yêu cầu»)
- [x] 2. Thử độc lập 7 biến thể và các biến thể khác qua `clean_suggestion` rồi `DraftImage(…, tags=ImageTags(source=SOURCE_AI))` gửi site giả: alt, `<figcaption>`, `alt_text`, `title`, `caption` không còn «\» mồ côi
- [x] 3. W3 / 2.3: mọi «[» «]» trần vẫn thành `&#91;` `&#93;`; shortcode `[code_snippet id=1]`, `[[…]]`, `[embed]…[/embed]` ngay sau tiền tố; ảnh thật không đổi so với `main`
- [x] 4. Soát «[Minh họa]: [nhãn]: một-chữ» → `AIError` trên tập câu hợp lý (3.840 cặp)
- [x] 5. Soát test: `tests/test_soi_loi_t071.py` chỉ gỡ dấu; `tests/test_t081_alt_gach_cheo.py` kiểm đúng ý
- [x] 6. Lỗi mới ghi thành test `xfail(strict=True)` SL-T081-1 trong `tests/test_soi_loi_t081.py`; không sửa code ứng dụng

## Rủi ro và điểm cần chú ý

- Thử ngẫu nhiên và tập câu hợp lý là chữ dựng sẵn, không phải chữ AI thật trả về (test không được gọi AI thật). Tập hợp lý viết theo quy tắc `[alt]` và các kiểu mở đầu đã thấy ở T-062, T-068, T-071.
- 5 test `xfail(strict=True)` của SL-T081-1: khi sửa xong thì thành XPASS và báo hỏng, chỉ cần xóa dòng `@pytest.mark.xfail`.

## Đề xuất

1. **SL-T081-1** (Thấp, có từ trước): Chỉ Huy gom vào phiếu dọn lỗi Thấp phần alt (cùng SL-T068-1 → -3 và Đề xuất 1 của Thợ Máy về «[nhãn]: một-chữ»); không chặn T-056.
2. **Lá Chắn rút gọn (W3)** nên soát: bước bỏ «\» chỉ đụng chữ đã lưu của ảnh AI (`alt.py:391-392`); lớp vô hiệu «[» «]» ở bước in ra không đổi; phần thân luôn được lọc lại trước khi ghép tiền tố. Script và log thử ở `T-081-soi-loi-scripts/` (thư mục ghi chú chung).

## Câu hỏi cho chủ dự án

Không có.

# Báo cáo T-098 · Kế hoạch: khuôn dữ liệu, đọc CSV/TSV/chữ dán, đề xuất có AI, SL-7 · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-098](../tickets/T-098-ke-hoach-khuon-doc-de-xuat.md), Thợ Máy đầu nhánh `ff8f542` (gốc `main` `15bfaca`) |
| Ngày nộp | 2026-10-28 |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, **2 Trung bình** (SL-T098-1, -2), **9 Thấp** (SL-T098-3 → -11), 8 góp ý. Test `xfail(strict=True)` cho cả 11 lỗi |
| **Phải sửa trước Lá Chắn** | **SL-T098-1** (bộ kiểm «AI không đưa HTML vào kế hoạch» bị lách bằng một ký tự vô hình; sửa 2–3 dòng). **Nên sửa cùng lượt**: SL-T098-2 (file kế hoạch nhiều bảng chỉ đọc bảng đầu: kế hoạch 6 tháng thật mất 104/112 dòng, không báo). Các lỗi Thấp không chặn; rẻ nên sửa trước khi gộp: SL-T098-3, -7, -11 |
| **Kết luận lượt 2** (đầu nhánh `d52f162`, 2026-10-28) | **ĐẠT CÓ ĐIỀU KIỆN**: SL-T098-1 → -11 **đóng cả 11** (thử lại cả biến thể gần); 12 dấu `xfail` gỡ đúng R5; 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **6 Thấp mới** (SL-T098-12 → -17, đều do phần sửa lượt 2, có `xfail(strict=True)`). **Không lỗi nào phải sửa trước Lá Chắn.** Không lùi `main`: bản gộp thử với `main` `1b45f5d` (có T-096) sạch, 3.797 test qua. Chi tiết: mục [«Lượt 2»](#lượt-2-2026-10-28-1358-0700--soát-lượt-sửa-của-thợ-máy-d52f162) |
| **Kết luận lượt 3** (đầu nhánh `34302fa`, 2026-10-28) | **ĐẠT CÓ ĐIỀU KIỆN**: SL-T098-12 → -17 **đóng cả 6** (thử cả biến thể gần); 6 dấu `xfail` gỡ đúng R5; 11 lỗi lượt 1 không lùi; 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **3 Thấp mới** (SL-T098-18 do lượt 3, -19 biến thể của -13, -20 có từ lượt 1; có `xfail(strict=True)`). **Không lỗi nào chặn gộp**, lượt 3 không đụng chỗ bảo mật. Chạy được với `main` mới nhất `d1506cb` (T-096, T-090, T-097): bản gộp thử 26 file test, 4.586 qua, 0 hỏng. Chi tiết: mục [«Lượt 3»](#lượt-3-2026-10-28-1733-0700--soát-lượt-sửa-của-thợ-máy-34302fa) |

## Tóm tắt (cho chủ dự án)

- Phần «máy» của trang Kế hoạch (đọc file, đọc chữ dán, so với kế hoạch đang có, nhận đề xuất của AI) làm đúng phần lớn các điều kiện bảo mật. Tôi thử bằng chính các file kế hoạch trong `docs/plan/` và bằng dữ liệu cố tình làm hỏng: file sai bảng mã, dòng thiếu/thừa ô, ô cực dài, chữ có công thức Excel (`=…`), ký tự đảo chiều chữ, lệnh giấu trong ghi chú, AI trả lời bậy (khoảng 2.500 mục ngẫu nhiên).
- Điều tốt: lệnh giấu trong ghi chú không tới được AI (ghi chú của thợ không được gửi đi); chữ người dùng dán không «thoát» khỏi khung dữ liệu; việc đọc kế hoạch **không bao giờ tìm web**, tôi kiểm tới tận lệnh gửi của cả 3 hãng AI; AI không xóa được dòng nào, không đổi được trạng thái bài, không đưa được link vào ô trang đích; đề xuất «Bỏ» không bao giờ tick sẵn; chữ có số điện thoại, email khách thì dừng lại hỏi trước khi gửi AI.
- Có 2 lỗi mức Trung bình:
  1. Phần mềm định chặn chữ HTML do AI viết vào kế hoạch, nhưng chỉ cần chen một ký tự vô hình sau dấu «<» là lọt qua, rồi bước làm sạch xóa ký tự đó, để lại thẻ HTML thật trong kế hoạch. Chưa gây hại ngay (chưa có chỗ nào hiện HTML), nhưng là lỗ hổng của một lớp bảo vệ. **Phải sửa trước Lá Chắn** (sửa nhỏ).
  2. File kế hoạch Markdown có nhiều bảng (như file kế hoạch 6 tháng của anh/chị: 12 bảng, 112 bài) chỉ đọc **bảng đầu tiên** (8 bài), các bảng sau bị bỏ mà không báo gì. Nên sửa cùng lượt.
- 9 lỗi nhỏ (Thấp): file CSV hỏng dấu ngoặc kép thì các dòng sau bị «nuốt» vào một ô; bảng Markdown có ô chứa dấu `|` làm lệch cột; vài cách viết số điện thoại chưa nhận ra (có ngoặc như «(028) 3812 3456»); số viết kiểu chữ toàn chiều rộng lọt qua bộ dò; một chuỗi 20.000 ký tự liền làm bộ dò email chạy ~5 giây; cảnh báo «trang cửa ngõ» nhầm với từ khóa không có địa danh (ví dụ «phụ kiện cửa cuốn», «phí lắp cửa cuốn»); một ca hiếm mất cảnh báo trùng; bảng chép từ Google Sheets có ô nhiều dòng bị coi là chữ tự do; kế hoạch 1.000 dòng so mất 30–60 giây.
- Không có gì phải anh/chị quyết. Nếu sau này anh/chị tải kế hoạch có cột ngày kiểu «Publish: T3 10/8» (tháng/ngày, không năm), phần mềm sẽ không đọc ngày (đúng chủ ý: không đoán tháng/ngày kiểu Mỹ); nên ghi ngày dạng «08/10/2026».

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t098.py` | Mới: 193 ca, **160 qua, 33 `xfail(strict=True)`** cho SL-T098-1 → -11. Không gọi AI, mạng thật (AI giả; client giả của thư viện Anthropic, OpenAI, Gemini) |
| `docs/team/reports/T-098-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, `config/`, test của Thợ Máy. Commit test: `0d23e62`, `d4e8298`.

## Kiểm từng mục

### 1. Hai dòng test cũ đổi (R5)

| Test | Thay đổi | Kết luận |
|---|---|---|
| `tests/test_soi_loi_t003_t009.py::test_keyword_cannot_fake_a_frame` | Chỉ gỡ 5 dòng `@pytest.mark.xfail(strict=True, reason="SL-7 (Thấp)…")`; thân test giữ nguyên | **Đúng R5**: lỗi SL-7 đã sửa nên test chuyển thành test thường (chặt hơn), như LC-T094-19 yêu cầu |
| `tests/test_t040_prompts.py::test_data_rules_and_tags_unchanged` (dòng 329) | Bộ `DATA_TAGS` mong đợi thêm đúng 2 khung `ke_hoach_hien_tai`, `ke_hoach_moi` | **Đúng R5** (Chỉ Huy đã duyệt): vẫn so trọn bộ khung (đúng thứ tự, không thừa, không thiếu), không nới; 2 dòng kiểm `DATA_RULES` giữ nguyên |

### 2. Điều kiện Lá Chắn (LC-T094) của phiếu

| Mã | Kết quả | Bằng chứng (test của tôi) |
|---|---|---|
| LC-T094-1 Test không gọi mạng thật | **ĐẠT** | Mọi test dùng AI giả; test «không tìm web» dùng chính lớp `AnthropicProvider`, `OpenAIProvider`, `GeminiProvider` với client giả; bộ chặn mạng của `tests/conftest.py` vẫn bật |
| LC-T094-2 Câu báo cố định | **ĐẠT** | Lỗi file: đúng hằng số, không chép tên file có chèn khung/đường dẫn (`test_file_errors_…`, 5 ca); câu báo của 11 file thật không chép chữ trong ô; câu «AI không hợp lệ» chỉ có số đếm; `PersonalInfoError` chỉ có số lượng, không chép số, email (7 ca) |
| LC-T094-3 Chữ thuần, bỏ ký tự đảo hướng | **ĐẠT** phần dữ liệu (hiển thị là việc T-101) | U+202A–202E, U+2066–2069, U+200E/F, U+061C, 6 ký tự vô hình, 5 ký tự điều khiển rời khỏi **mọi** trường chữ và nhãn (`test_bidi_invisible_…`). Lưu ý cho T-101: lý do AI, tiêu đề, ghi chú có thể chứa link Markdown hay địa chỉ web (LC-T094-20 cho phép là chữ): phải hiện chữ thuần (LC-T094-32) |
| LC-T094-18 Một bộ làm sạch, giới hạn, bảng mã, CSV chuẩn, ngày | **ĐẠT**, kèm SL-T098-3, -4, -10 | 1 MB kiểm theo byte trước khi giải mã; 20.000 ký tự dán; ô 200.000 ký tự → câu cố định; ô > 2.000 cắt và báo; 7 bảng mã khác (cp1258, UTF-16 có/không BOM, UTF-32, latin-1, surrogate, UTF-8 dạng dài) đều bị từ chối, không đoán; công thức `=1+1`, `=HYPERLINK(…)`, `=cmd…`, `@SUM(A1)` giữ là chữ, không tính; 13 dạng ngày (ngày/tháng luôn trước, `11/25/2026` bị từ chối, thiếu năm không đoán, năm ngoài 2020–2035 bị từ chối); thử ngẫu nhiên 400 lần × 2 cách đọc chỉ ra dòng sạch hoặc câu lỗi cố định |
| LC-T094-19 SL-7 mọi lời dặn, khung `plan`, không tìm web | **ĐẠT** | Test canh: mọi hàm `…_prompt` có tham số `keyword` (8 hàm, gồm `alt_prompt`) phải nằm trong danh sách thử; 4 kiểu từ khóa độc (đóng/mở khung, chữ toàn chiều rộng, ký tự vô hình, chữ hoa) không thêm thẻ khung nào, đếm trên chữ «như AI đọc» (NFKC, bỏ ký tự vô hình); chữ dán (5 kiểu tấn công) và từ khóa dòng hiện tại (cả dòng dựng thẳng không qua kiểm) không thoát khung; `DATA_RULES` có trong lời dặn hệ thống. **Không tìm web tới tận lệnh gửi**: 3 hãng × (có `[tasks.plan]` / dùng tạm `outline`), cả hai đều ghi `web_search = true`: không lệnh nào mang công cụ tìm web |
| LC-T094-20 Kết quả AI chưa tin cậy | **ĐẠT CÓ ĐIỀU KIỆN**: SL-T098-1 | 24 mục (21 phải bỏ: hành động lạ «add», «xoa», «delete»; mã ghép, mã không có; «Thêm» có mã; thẻ khung, HTML; lý do rỗng/vô hình/301 ký tự; nhãn, ngày, giờ sai; quá dài. 3 phải giữ: «THÊM», «Cập Nhật» viết hoa, lý do đúng 300 ký tự) đều đúng, câu báo cố định; lý do và chữ được làm sạch; AI không đổi được trạng thái, mã bài WordPress, slug, trang đích; 120 «Bỏ» → 3 đề xuất, không cái nào tick sẵn; thử ngẫu nhiên 80 lượt (≤ 130 mục/lượt) giữ mọi bất biến; **AI trả lời hỏng** (chữ không phải JSON, sai kiểu, thiếu trường, thư viện không dựng được khuôn) qua cả 3 thư viện thật với client giả: một câu lỗi cố định «… Bấm thử lại.», không chép chữ AI (6 ca). **Lách được** bộ kiểm HTML (SL-T098-1) |
| LC-T094-21 Dữ liệu cá nhân khách (A3) | **ĐẠT CÓ ĐIỀU KIỆN**: SL-T098-5, -6, -7 | Ví dụ của điều kiện (`0909 123 456`, `+84 909…`, email dạng `a.b@khach.vn`) đã có ở test Thợ Máy; tôi thử thêm 7 dạng hay gặp (`0912.345.678`, `SĐT:0909123456`, `090 912 3456`, `+84 909 123 456`, `84909123456`, email có `+`, số bị chèn ký tự vô hình): chặn trước khi gửi, câu báo chỉ đếm, che xong gửi được; số điện thoại nằm trong **từ khóa** dòng hiện tại cũng bị chặn; ghi chú của thợ (có số, email, lệnh) đọc từ file **không** tới AI. Nửa sau của điều kiện (khi điền ghi chú vào Soạn bài) thuộc T-101/T-102: hàm `personal_info`, `mask_personal_info` đã dùng được |

### 3. Dữ liệu thật trong `docs/plan/`

| File | Kết quả đọc | Nhận xét |
|---|---|---|
| `ke_hoach_6_thang_chi_tiet.md` | 12 bảng có cột «Từ khóa», 113 dòng (112 hợp lệ, 1 từ khóa dài quá 120 ký tự) → **đọc 8** | **SL-T098-2**. Cột «Publish» (`T3 10/8`: thứ + tháng/ngày, không năm) không nhận ra nên không đọc ngày và không báo (góp ý G1; giá trị kiểu này đúng là phải từ chối). «Loại» `Service`, `Guide` nhận đúng; đọc riêng từng bảng sau thì `Ward`, `Case Study`… báo «không đọc được», bỏ trống (đúng) |
| `seo_local_hcm_20_bai_thang_vi.md` | 2 bảng, 15 dòng → **đọc 8** | SL-T098-2. «Search Intent» `Local service` không thuộc 3 nhãn → báo, bỏ trống (đúng). 8 trang «sửa cửa quận N» đều có cảnh báo **trang cửa ngõ** và không tick sẵn (đúng ý `review_ke_hoach_v1.md` L5) |
| `bang_dieu_khien_theo_doi_vi.md` | Bảng theo dõi thứ hạng có cột «Từ Khóa» → 4 dòng kế hoạch | Đúng luật «có cột từ khóa là bảng»; người dùng bỏ tick được |
| 8 file còn lại `.md` | Chữ tự do 3.200–15.900 ký tự (dưới 20.000) → gửi AI | Đúng thiết kế 1.2 |
| `thong_tin_can_dien.xlsx` | Từ chối, câu khuyên chép vùng ô rồi dán | Đúng câu 2A |

Trong kế hoạch 6 tháng, khuôn cửa ngõ «sua cua» gom đúng 28 từ khóa quận/phường.

### 4. Gỡ chỗ bảo vệ trên bản sao (đột biến)

Bản sao: `git worktree` tạm ở `ff8f542` (không đụng `wt-T-098`), mỗi lần thay đúng một đoạn code (đoạn phải có đúng một lần), chạy `tests/test_soi_loi_t098.py` với `-x`, trả file về. Script: `T-098-soi-loi-scripts/mutate.py` (thư mục ghi chú chung).

| Chỗ bảo vệ (điều kiện) | Gỡ thế nào | Test của tôi bắt |
|---|---|---|
| `plan` luôn tắt tìm web (LC-T094-19) | `_plan_task` trả cấu hình gốc | `test_plan_request_never_carries_a_search_tool` |
| Khung `<ke_hoach_moi>` (LC-T094-19) | Bọc chữ dán bằng thẻ trần, không `_neutralize` | `test_pasted_text_cannot_leave_its_frame` |
| Khung `<ke_hoach_hien_tai>` | Như trên, cho kế hoạch hiện tại | `test_keyword_of_current_rows_cannot_leave_its_frame` |
| SL-7: `_neutralize` từ khóa | Bỏ `_neutralize` trong `_keyword` | `test_keyword_cannot_open_or_close_any_frame` |
| SL-7: đổi «» thành ‹› | Bỏ bước đổi | `test_keyword_in_instruction_line_stays_one_line_…` |
| Không gửi ghi chú của thợ (A3) | `_plan_line` thêm ghi chú | `test_notes_with_injection_and_phone_read_from_file_…` |
| AI: hai mục một Mã bài | Bỏ kiểm `touched` | `test_many_junk_drops_are_never_preselected` |
| AI: «Thêm» có mã | Bỏ kiểm mã | `test_hostile_ai_items_are_dropped_…` |
| AI: trường có HTML | Bỏ kiểm `has_html` | `test_hostile_ai_items_are_dropped_…` |
| AI: lý do làm sạch | Dùng lý do thô | `test_hostile_ai_items_are_dropped_…` (lý do toàn ký tự vô hình) |
| AI: tối đa 100 mục | Bỏ giới hạn | `test_ai_fuzz_invariants_hold_for_any_answer` |
| «Bỏ» không tick sẵn | `preselected` chỉ xét cảnh báo | `test_table_fuzz_never_drops_or_touches_app_columns` |
| Bảng không đặt trạng thái app | `_new_row` giữ trạng thái bảng | `test_table_fuzz_never_drops_or_touches_app_columns` |
| Cảnh báo bài đã hẹn giờ/đăng | Bỏ cảnh báo | `test_ai_cannot_change_status_or_app_fields_…` |
| Bỏ ký tự Cf (LC-T094-18) | Bỏ «Cf» khỏi bộ lọc | `test_bidi_invisible_and_control_characters_…` |
| Dò số điện thoại (LC-T094-21) | Đòi 11–12 chữ số | `test_personal_info_blocks_sending_…` |
| Dò email | Đòi «@@» | `test_personal_info_blocks_sending_…` |
| Chặn gửi khi có dữ liệu cá nhân | Không bao giờ chặn | `test_personal_info_blocks_sending_…` |
| Dò cả từ khóa kế hoạch hiện tại | Chỉ dò chữ dán | `test_personal_info_in_a_current_keyword_also_blocks` |
| Chỉ UTF-8 (LC-T094-18) | Giải mã `errors="replace"` | `test_other_encodings_are_refused_…` |
| Giới hạn 1 MB theo byte (LC-T094-18) | Bỏ kiểm kích thước | `test_file_errors_are_fixed_and_never_echo_the_file_name[too-big]` |
| Câu báo không chép tên file (LC-T094-2) | Nối tên file vào câu báo | `test_real_xlsx_is_refused_with_paste_advice` |

**22/22 lần gỡ đều bị test của tôi bắt.** Các file trả về giống hệt bản gốc (so bỏ qua kiểu xuống dòng); bản sao đã gỡ. Kết quả thô: `T-098-soi-loi-scripts/mutate_out.txt`.

## Lỗi và góp ý

| # | Mức | Mô tả | Vị trí | Trước Lá Chắn? | Test |
|---|---|---|---|---|---|
| SL-T098-1 | **Trung bình** | Bộ kiểm «chữ AI có HTML thì bỏ mục» chạy trên **chữ thô**, rồi mới làm sạch. Chen một ký tự vô hình (U+200B, U+00AD, U+2060) sau «<» là `has_html` không thấy thẻ; bước làm sạch xóa ký tự đó nên kế hoạch giữ thẻ thật: `<img src=x onerror=alert(1)>`, `<script>`, `<a href=…>` ở từ khóa, tiêu đề dự kiến, từ khóa phụ, ghi chú **và lý do**. Trái LC-T094-20 («khuôn chặt», «lý do chữ thường») và docstring `from_ai`. Chưa khai thác được ngay (chưa chỗ nào hiện HTML; đường bảng vốn nhận chữ có `<` như chữ thường), nhưng là lớp bảo vệ của đường AI (dữ liệu bị dụ được) mà T-101/T-102 sẽ dựa vào | `seo_app/plan/propose.py:280` (`has_html(raw)` trước `PlanRow`), `:298` (`has_html(item.reason)` trên chữ thô, `reason` đã làm sạch) | **Có** | `test_sl_t098_1_…` (15 ca) |
| SL-T098-2 | **Trung bình** | Markdown nhiều bảng: `_read_text` trả về ngay **bảng đầu tiên** có cột từ khóa, các bảng sau bị bỏ, không câu báo nào (câu «Chỉ đọc bảng; phần chữ ngoài bảng không được đọc» còn làm người dùng tưởng mọi bảng đã đọc). File thật: kế hoạch 6 tháng 112 → 8 dòng, SEO local 15 → 8 | `seo_app/plan/parse.py:182-188` | Nên (cùng lượt) | `test_sl_t098_2_…` (2 ca: chữ dán + file, file thật) |
| SL-T098-3 | Thấp | CSV có dấu ngoặc kép không đóng: `csv.reader` (mặc định `strict=False`) gộp mọi dòng sau vào một ô, không báo; câu `BAD_TABLE` nói có kiểm «dấu ngoặc kép không đóng» nhưng không bao giờ xảy ra. Có thể dùng `strict=True` (đã thử: CSV chuẩn của Excel vẫn đọc được) hoặc dò riêng ca hết file trong ngoặc | `parse.py:208` | Không (rẻ, nên sửa trước khi gộp) | `test_sl_t098_3_…` |
| SL-T098-4 | Thấp | Ô Markdown có dấu gạch đứng đã escape (gạch chéo ngược + gạch đứng, cách GFM ghi tiêu đề «Sửa cửa cuốn \| Pro-Metal») bị tách thành 2 ô → lệch cột (ưu tiên, ngày mất, có báo); dòng mở đầu bằng hai dấu gạch đứng liền nhau (ô đầu trống không dấu cách) bị `strip` ăn mất ô → **từ khóa thành «12/11/2026»**, không báo | `parse.py:244` | Không | `test_sl_t098_4_…` (2 ca) |
| SL-T098-5 | Thấp | Dò số điện thoại sót dạng hay gặp: `(+84) 909 123 456`, `+84 (0) 909 123 456`, `(028) 3812 3456` (bàn), `0909 - 123 - 456`. Dạng dính chữ `sđt0909123456` cũng sót (chưa xếp lỗi: sửa dễ nhầm mã hàng) | `model.py:340` | Không | `test_sl_t098_5_…` (4 ca) |
| SL-T098-6 | Thấp | Dò dữ liệu cá nhân trên chữ NFC, nhưng `_neutralize` của lời dặn đổi chữ sang NFKC: số toàn chiều rộng `０９０９ １２３ ４５６`, `lan＠mail.vn` lọt bộ dò rồi tới AI thành `0909 123 456`, `lan@mail.vn`. Hiếm gặp (gõ bằng bộ gõ Nhật/Trung) | `model.py:347` so với `prompts.py:44` | Không | `test_sl_t098_6_…` (2 ca) |
| SL-T098-7 | Thấp | `_EMAIL_RE` (`[\w.+\-]+@…`, không neo đầu) chạy theo **bình phương** độ dài một chuỗi liền: 20.000 ký tự `a` (chữ dán tối đa) mất 4,5–5,2 s mỗi lần dò; `mask_personal_info` dò 2 lượt. Sửa: neo đầu (`(?<![\w.+\-])`) và giới hạn phần trước «@» (≤ 64 ký tự) | `model.py:341` | Không (rẻ) | `test_sl_t098_7_…` (đo xen kẽ nhỏ/lớn) |
| SL-T098-8 | Thấp | `_LOCATION` cho nhánh chữ (`[a-z]+(?:\s+[a-z]+)?`) đi ngay sau `q`, `p`, `xa` **không cần dấu cách hay dấu chấm**, nên mọi từ bắt đầu bằng p, q, xa (và từ kế tiếp) bị coi là địa danh: «phụ kiện / phụ tùng / phí lắp cửa cuốn», «cửa cuốn quay chậm / quá nóng / quên mã», «cửa cuốn xài lâu / xanh lá / xám» bị cảnh báo «trang cửa ngõ», bỏ tick | `propose.py:421-424` | Không | `test_sl_t098_8_…` (3 ca) |
| SL-T098-9 | Thấp | Kế hoạch có dòng chưa có Mã bài: khi một dòng như thế được «Cập nhật» (khớp theo từ khóa), `replaced = {""}` loại **mọi** dòng chưa có mã khỏi bộ so trùng → đề xuất trùng từ khóa với dòng chưa mã khác mất cảnh báo. Đề xuất «Cập nhật» đó còn mang `key = ""` (T-100 không ghi theo mã được) | `propose.py:339-340` | Không | `test_sl_t098_9_…` |
| SL-T098-10 | Thấp | Bảng chép từ Google Sheets/Excel có ô nhiều dòng (ô ghi chú xuống dòng được chép trong ngoặc kép): `_read_text` đếm dấu tab theo **dòng vật lý** (≥ 60%) nên coi cả bảng là chữ tự do → phải gửi AI (có thể quá 20.000 ký tự) thay vì đọc thẳng | `parse.py:177-180` | Không | `test_sl_t098_10_…` |
| SL-T098-11 | Thấp | `check_proposals` tính lại `keyword_key` cho **từng cặp** (đề xuất × dòng kế hoạch); mỗi lần ~140 µs (làm sạch từng ký tự). Đo: 100 dòng 0,3–0,6 s; 300 dòng 3–5 s; **1.000 dòng 31–59 s** (giới hạn cho phép là 1.000); đường AI: 100 đề xuất × kế hoạch 1.000 dòng 8,1 s. Sửa: tính khóa một lần cho mỗi dòng | `propose.py:349-358` | Không (rẻ) | `test_sl_t098_11_…` (đo xen kẽ nhỏ/lớn) |

Góp ý (không xếp lỗi, không test xfail):

- **G1** Tên cột: chưa nhận «Ngày đăng dự kiến», «Ngày xuất bản», «Ngày đăng bài», «Publish» (file thật), «Deadline», «Từ khóa SEO», «Keyword chính», «Từ khóa mục tiêu». Cột không nhận ra bị bỏ qua lặng lẽ (cột ngày bị bỏ thì người dùng không biết): nên báo «N cột không nhận ra nên không đọc» (chỉ số đếm, LC-T094-2).
- **G2** Giờ có giây `08:00:00`, `8:00 SA`/`8:00 AM`, ngày giờ ISO `2026-06-12T08:00:00`, số ngày có phần lẻ `46337.5` bị bỏ trống kèm câu báo. Google Sheets (tiếng Việt) hiện giờ dạng `08:00:00`, Excel xuất `12/06/2026 08:00:00`; T-100 đọc Sheet cũng sẽ gặp. Test của Thợ Máy cố ý từ chối `08:00:00`: Chỉ Huy quyết có nhận giây `:00` không.
- **G3** «Ngày dự kiến đã qua» gắn cả khi đề xuất **không đổi ngày** (bài đăng tháng trước, bảng chỉ sửa ghi chú) → bỏ tick oan. Nên chỉ cảnh báo với «Thêm» hoặc khi ngày đổi.
- **G4** Dòng «Đã hẹn giờ»/«Đã đăng»: AI hay bảng đổi **từ khóa, tiêu đề** thì không cảnh báo, vẫn tick sẵn (thiết kế 1.4 chỉ nói đổi ngày và «Bỏ»). Nên gắn `WARN_RELEASED` cho mọi thay đổi ở dòng đã hẹn giờ/đăng.
- **G5** AI có thể chép số điện thoại, email vào ghi chú, tiêu đề (lời dặn cấm, code chưa kiểm; ví dụ khi người dùng đã đồng ý gửi): nên chạy `personal_info` trên chữ AI và thêm cảnh báo.
- **G6** `DATA_RULES` chỉ nêu 4 khung cũ, chưa nêu `<ke_hoach_hien_tai>`, `<ke_hoach_moi>` (lời dặn `plan` tự nói đó là dữ liệu). Việc của T-103 (LC-T094-42: giữ `DATA_RULES`).
- **G7** CSV có dòng tên bảng phía trên dòng tiêu đề → cả bảng thành chữ tự do (nên dò dòng tiêu đề trong vài dòng đầu); Markdown in đậm `**sửa cửa**` giữ dấu `*` trong từ khóa; «B-1» và «B-001» là hai mã khác nhau; dấu phân cách CSV đoán theo dòng đầu (tiêu đề có dấu phẩy trong ngoặc kép dễ đoán sai).
- **G8** Ghi cho phiếu sau: T-100 trung hòa chữ bắt đầu `=` `+` `-` `@` khi ghi Sheet (LC-T094-28; T-098 giữ nguyên chữ là đúng phạm vi); T-101 hiện lý do, tiêu đề, ghi chú bằng chữ thuần; T-101/T-102 gọi `personal_info` khi điền ghi chú vào Soạn bài; AI đề xuất 100 «Thêm» rác thì cả 100 đều tick sẵn (thiết kế chấp nhận, người dùng duyệt): có thể cân nhắc không tick sẵn khi AI đề xuất quá nhiều.

Ghi nhận (không phải lỗi): ký tự điều khiển mà Python coi là khoảng trắng (U+000B, U+000C, U+001C–U+001F, U+0085) thành một dấu cách thường, không bị giữ lại: hợp ý «bỏ Cc trừ khoảng trắng».

## Cách tái hiện

```bash
uv run pytest tests/test_soi_loi_t098.py -k sl_t098 --runxfail --tb=line
```

Ví dụ nhanh SL-T098-1 (Python):

```python
from seo_app.content.models import PlanSuggestion, PlanSuggestions
from seo_app.plan import propose
item = PlanSuggestion.model_validate({n: "" for n in PlanSuggestion.model_fields} | {
    "action": "them", "keyword": "cửa sắt", "reason": "x",
    "title_hint": "<" + chr(0x200B) + "img src=x onerror=alert(1)>"})
print(propose.from_ai(PlanSuggestions(items=[item]), []).items[0].after.title_hint)
# <img src=x onerror=alert(1)>
```

SL-T098-2: `parse.read_file(open("docs/plan/ke_hoach_6_thang_chi_tiet.md","rb").read(), "k.md").rows` → 8 dòng.

## Bằng chứng

- `uv run pytest tests/test_soi_loi_t098.py`: **160 passed, 33 xfailed**. Chạy `--runxfail -k sl_t098`: 33 hỏng, đúng câu khẳng định của từng lỗi (không hỏng vì lỗi viết test). Biên độ 2 test đo giờ: SL-T098-7 0,63 s so với ngưỡng 0,19 s; SL-T098-11 0,44 s so với 0,11 s.
- Test liên quan (70 file: 4 file test kế hoạch, `test_soi_loi_t003_t009.py`, `test_t040_prompts.py`, mọi file test lời dặn, AI, nội dung, Soi Lỗi/Lá Chắn cũ, trang app): **7166 passed, 11 skipped, 23 xfailed, 0 failed** (27 phút, chạy trước khi thêm file của tôi). Chạy lại chung sau cùng 4 file test kế hoạch, `test_soi_loi_t003_t009.py`, `test_t040_prompts.py`, `test_prompt_data_frames.py` và file của tôi: **510 passed, 33 xfailed**.
- `uv run ruff check .`: sạch; `ruff format --check` file test: sạch.
- `PYTHONUTF8=1 uvx detect-secrets scan` (file test + mồi thử): chỉ bắt mồi, file test không có gì.

## Đối chiếu tiêu chí xong

- [x] Thử đọc kế hoạch với dữ liệu thật `docs/plan/` (mục 3) và dữ liệu độc: CSV bẩn, mã hóa lạ, dòng thiếu/thừa cột, tên cột đồng nghĩa, ngày nhiều dạng, chữ `=`/`+`/`-`/`@`, ký tự đảo hướng, chữ cực dài, lệnh giấu trong ghi chú
- [x] Đề xuất đúng (so bảng: thử ngẫu nhiên 150 lượt giữ bất biến; dữ liệu thật) — kèm SL-T098-8, -9, -11
- [x] AI trả lời hỏng/độc vẫn an toàn — kèm SL-T098-1
- [x] SL-7 ở mọi lời dặn (có test canh hàm mới), không tìm web (tới lệnh gửi của 3 hãng)
- [x] Nhắc khi có số điện thoại/email khách — kèm SL-T098-5, -6, -7
- [x] Không sửa code ứng dụng; lỗi ở `tests/test_soi_loi_t098.py`, `xfail(strict=True)`, mã SL-T098-n; không gọi AI thật
- [x] Test liên quan + `uv run ruff check .`; báo cáo này

## Rủi ro

- Test đo giờ (SL-T098-7, -11) dựa vào tỉ lệ nhỏ/lớn đo xen kẽ, lấy lần nhanh nhất (như T-025), biên độ 3–4 lần: máy rất bận vẫn có thể làm lệch; nếu XPASS bất ngờ mà code chưa đổi thì chạy lại.
- Thử ngẫu nhiên dùng hạt giống cố định (lặp lại được), không phủ hết mọi tổ hợp.
- Chưa thử giao diện (T-101 chưa làm) và Google Sheets (T-097, T-100).

## Đề xuất

1. Thợ Máy sửa **SL-T098-1** trước Lá Chắn: kiểm HTML trên chữ **đã làm sạch** (sau `clean_text` / sau `PlanRow`), cả `reason`. Cùng lượt nên sửa **SL-T098-2** (đọc mọi bảng có cột từ khóa, hoặc ít nhất báo số bảng bị bỏ) và 3 lỗi rẻ SL-T098-3, -7, -11.
2. Soi Lỗi soát lại lượt sửa (rút gọn): các test `xfail` sẽ XPASS và phải được gỡ dấu `xfail` theo R5.
3. Chỉ Huy quyết G2 (nhận giờ có giây `08:00:00`) trước T-100.

## Câu hỏi cho chủ dự án

Không có.

---

## Lượt 2 (2026-10-28 13:58 +07:00) · soát lượt sửa của Thợ Máy (`d52f162`)

| Mục | Nội dung |
|---|---|
| Phiếu giao | Chỉ Huy B, 28/10 13:50: xác nhận SL-T098-1 → -11 đóng thật (thêm biến thể gần), soát R5 12 dấu `xfail` được gỡ, tìm lỗi mới do phần sửa (ngày giờ nhiều dạng, so trùng theo dòng, mã «B-1» = «B-001», AI hơn 20 đề xuất không tick sẵn), không lùi `main` (vừa gộp T-096) |
| Đầu nhánh soát | `d52f162` (Thợ Máy lượt 2, sau báo cáo `84f32ec`); Thợ Máy chỉ sửa 3 file `seo_app/plan/` và test |
| **Kết luận lượt 2** | **ĐẠT CÓ ĐIỀU KIỆN**: 11/11 lỗi cũ đóng; **6 Thấp mới** (SL-T098-12 → -17); 0 Nghiêm trọng, 0 Cao, 0 Trung bình. **Không lỗi nào phải sửa trước Lá Chắn.** Nên sửa trước khi gộp (đều nhỏ): SL-T098-13 (dòng kế hoạch giả, tick sẵn), -17 (sập khi có mã «B-99999»), -12 (cả bảng dán hỏng vì một ô mở đầu bằng ngoặc kép) |

### Tóm tắt (cho chủ dự án)

- Các lỗi lần trước đã được sửa thật. Tôi thử lại đúng các ca cũ, thêm nhiều cách «lách» gần giống: không còn lọt chữ HTML do AI viết; file kế hoạch 6 tháng nay đọc đủ 112 bài; dò số điện thoại, email nhận thêm nhiều cách viết và chạy rất nhanh; kế hoạch 1.000 dòng so trong chưa tới nửa giây (trước gần một phút).
- Phần sửa sinh 6 lỗi nhỏ mới, không lỗi nào nguy hiểm:
  1. Một ô bắt đầu bằng chữ trong ngoặc kép (ví dụ `"Đức" là hãng tốt`) làm cả bảng dán bị từ chối.
  2. Bảng dạng «tên mục – nội dung» có một dòng «Từ khóa» bị đọc nhầm thành kế hoạch: các dòng «Ngày», «Ghi chú»… thành bài giả, tick sẵn (file yêu cầu phần mềm trong `docs/plan/` cho ra 10 bài giả).
  3. Từ khóa viết tắt «P. Tân Định», «P. Đa Kao»… không còn được cảnh báo «trang cửa ngõ».
  4. AI chỉ đổi mức ưu tiên một bài mà ghi chú cũ có số khách cũng bị cảnh báo «AI có số điện thoại», bỏ tick.
  5. Ô ngày dạng `46337.0` nay thành giờ đăng 0 giờ đêm.
  6. Kế hoạch có mã bài «B-99999» thì phần so bảng và đề xuất AI báo lỗi, không chạy được.
- Không có gì phải anh/chị quyết.

### R5

| Test | Thay đổi | Kết luận |
|---|---|---|
| `tests/test_soi_loi_t098.py` (của tôi) | 55 dòng xóa, 0 dòng thêm; mọi dòng xóa thuộc 12 dấu `@pytest.mark.xfail(...)` (11 dấu nhiều dòng của SL-T098-1 → -11, 1 dấu một dòng của ca file thật SL-T098-2); thân test, điều kiện khẳng định không đổi | **Đúng R5** |
| `tests/test_plan_model.py`, `test_plan_parse.py`, `test_plan_propose.py` (của Thợ Máy) | Đổi theo hành vi mới có chủ đích (G2, G7): `test_key_format` («b-1» → «B-001»), `test_times` thêm giờ có giây, SA/CH/AM/PM; `test_times_rejected` bỏ `08:00:00` (nay nhận) nhưng thêm 5 ca phải từ chối («08:00:61», «13 PM», «0 AM», «8:00 sáng», «8 chiều»); thêm 15 test lượt 2 | **Đúng R5**: không ca nào bị nới mà không có hành vi mới đi kèm |

### Từng lỗi cũ

| Lỗi | Ca cũ | Biến thể gần (mới, đều qua) | Kết quả |
|---|---|---|---|
| SL-T098-1 | 15 ca qua | 14 ký tự chen sau «<» (U+200B, U+00AD, U+2060, U+FEFF, U+034F, U+180E, U+FFA0, U+3164, U+FE0F, U+E0100, NUL, U+E0041, U+200E, U+202E) × 5 trường (70 ca): mục bị bỏ; dạng NFKC và đánh dấu khác (`＜script＞`, `﹤b﹥`, chú thích HTML, `<?php`, `<!doctype`, NUL chen giữa thẻ, chữ hoa): bị bỏ; chữ «<» thường («giá < 5 triệu», «cửa <3m», «a <- b», `⟨b⟩`, `&lt;b&gt;`): vẫn giữ | **Đóng** |
| SL-T098-2 | 2 ca qua | File thật: kế hoạch 6 tháng 112 dòng + 1 bỏ (từ khóa dài quá 120 ký tự), SEO local 15; nhiều bảng chung mã (`B-1`/`B-001` giữ dòng đầu, câu báo «Bảng 2: …»), bảng không có cột từ khóa được đếm; giới hạn 1.000 dòng tính chung (3 bảng × 400 → câu cố định) | **Đóng** |
| SL-T098-3 | Qua (ngoặc không đóng → câu cố định) | — | **Đóng**; xem SL-T098-12 |
| SL-T098-4 | 2 ca qua | Ô in đậm, nghiêng, mã bỏ dấu bọc. Ghi nhận (không xếp lỗi): gạch chéo ngược thật đứng trước gạch đứng (đường dẫn Windows cuối ô) vẫn bị coi là gạch đứng escape, rất hiếm | **Đóng** |
| SL-T098-5 | 4 ca qua | `(+84)909123456`, `+84-909-123-456`, `84 909 123 456` | **Đóng** |
| SL-T098-6 | 2 ca qua | Số toàn chiều rộng có dấu cách, U+FFA0 chen giữa số, ký tự vô hình + dấu cách | **Đóng** |
| SL-T098-7 | Qua | 9 chuỗi độc khác cho cả số điện thoại và email (`0`, `0 `, `(0)`, `0-(-`, `+84`, `(+84) `, `a.@`, `@a.`, `a-`), đo cả `mask_personal_info`: tuyến tính (20.000 ký tự ~15 ms, trước 4,5–5,2 s) | **Đóng** |
| SL-T098-8 | 3 ca qua | — | **Đóng**; xem SL-T098-14 |
| SL-T098-9 | Qua | 2 dòng chưa mã cùng đổi được cấp `B-001`, `B-002` khác nhau; «Bỏ» dòng chưa mã cũng được cấp mã; `changes` có `key` | **Đóng** |
| SL-T098-10 | Qua | Dán 600 dòng có ô nhiều dòng: đọc thẳng thành bảng (0,03 s) | **Đóng** |
| SL-T098-11 | Qua | Đo: so bảng 1.000 + 1.000 dòng 0,23 s (trước 31–59 s); đề xuất AI 100 mục × kế hoạch 1.000 dòng 0,06 s (trước 8,1 s); thêm test tỉ lệ cho đường AI | **Đóng** |
| Góp ý | — | G1, G3, G4 đúng; G2 đúng (xem SL-T098-16); G5 đúng (xem SL-T098-15); G7 đúng (xem SL-T098-13, -17); G8: 20 đề xuất tick sẵn, 21 (lẫn «Cập nhật»; mục sai không tính) thì không; G6 để T-103 (đúng phạm vi) | — |

### Lỗi mới (lượt 2)

| # | Mức | Mô tả | Vị trí | Do phần sửa | Test |
|---|---|---|---|---|---|
| SL-T098-12 | Thấp | `csv` chạy `strict=True` nên ô **mở đầu** bằng chữ trong ngoặc kép rồi có chữ sau (`"Đức" là hãng tốt`) làm hỏng **cả bảng**, câu báo nói «dấu ngoặc kép không đóng» dù ngoặc đã đóng. Excel, Google Sheets chép ô không xuống dòng ra nguyên chữ (không bọc ngoặc), CSV gõ tay cũng hay gặp. Lượt 1 đọc được (chỉ mất dấu ngoặc). Gợi ý: chỉ coi «hết file khi còn trong ngoặc» là lỗi; lỗi `strict` khác thì đọc lại không `strict` | `seo_app/plan/parse.py:241` | SL-T098-3 | `test_sl_t098_12_…` (dán, CSV) |
| SL-T098-13 | Thấp | Tìm dòng tiêu đề trong 5 dòng đầu bắt nhầm **dòng dữ liệu** có ô «Từ khóa»/«Từ khóa chính»: bảng dạng «Mục – Nội dung» thành kế hoạch, các dòng sau («Ngày», «Ghi chú»…) thành bài giả, **tick sẵn**. File thật `docs/plan/yeu_cau_phan_mem_ProMetal_ToolSEO.md` (lượt 1: chữ tự do) nay cho 10 bài giả («Slug», «Tiêu đề dự kiến», «Từ khóa phụ, ý cần có»…). Gợi ý: Markdown thì dòng tiêu đề luôn là dòng ngay trước dòng phân cách «\|---\|» (không dò); CSV chỉ bỏ qua dòng phía trên có tối đa một ô không trống (dòng tên bảng) | `parse.py:132`, `:381` (`_find_header`) | G7 | `test_sl_t098_13_…` (Markdown, CSV, file thật) |
| SL-T098-14 | Thấp | Nhánh viết tắt «p.»/«q.» + tên của `_LOCATION` không bao giờ khớp: `_location_template` nhận chữ đã `keyword_key` (dấu chấm thành dấu cách). «sửa cửa P. Tân Định / P. Đa Kao / P. Bến Nghé» mất cảnh báo trang cửa ngõ (lượt 1 có). Gợi ý: trên chữ đã bỏ dấu, nhận «p»/«q» **đứng riêng** rồi tên: «phụ kiện» không bị bắt vì «phu» không phải «p» đứng riêng | `propose.py:513` | SL-T098-8 | `test_sl_t098_14_…` |
| SL-T098-15 | Thấp | `_has_personal` xét mọi trường chữ của dòng **sau khi đổi**, gồm chữ cũ: AI chỉ đổi ưu tiên (hay «Bỏ») một dòng mà ghi chú cũ có số khách cũng bị cảnh báo «Đề xuất của AI có số điện thoại hoặc email», bỏ tick. Ghi chú có số khách là chuyện thường (vì vậy ghi chú không gửi AI). Gợi ý: chỉ xét các trường AI gửi (đã đổi) và lý do | `propose.py:345` | G5 | `test_sl_t098_15_…` («Cập nhật», «Bỏ») |
| SL-T098-16 | Thấp | `_SERIAL_TIME_RE` nhận cả phần lẻ toàn chữ số 0: ô ngày `46337.0` (lượt 1 là ngày trần như `46337`) nay đặt giờ đăng **00:00** (nửa đêm), đè giờ mặc định. Gợi ý: phần lẻ toàn 0 là ngày trần | `model.py:139`, `:284` | G2 | `test_sl_t098_16_…` (2 ca) |
| SL-T098-17 | Thấp | `_Keys.__init__` gọi `model.next_key` ngay khi dựng: kế hoạch có mã «B-99999» (gõ tay trên Sheet: dữ liệu chưa tin cậy) làm **mọi** lần so bảng, đề xuất AI báo `ValueError` «hết mã bài», kể cả khi chỉ «Cập nhật» (lượt 1 chỉ lỗi khi thật sự cần cấp mã mới). `ValueError` không phải `AIError` nên `plan_changes` để lọt ra giao diện như lỗi lạ. Gợi ý: tính số lớn nhất trực tiếp, chỉ báo «hết mã» (câu cố định) khi cần cấp mã mới | `propose.py:158` | SL-T098-11 | `test_sl_t098_17_…` |

Góp ý lượt 2 (không xếp lỗi, không test `xfail`):

- **G9** Ô «ngày giờ» có giờ không có dấu «:» (`12/06/2026 8 PM`) mất **cả ngày** (`_DATE_TIME_RE` đòi dấu giờ), trong khi `8 PM` đứng riêng nay đọc được; ISO có múi giờ (`2026-06-12T08:00:00+07:00`) mất giờ (có câu báo). Sheets, Excel không xuất hai dạng này.
- **G10** Dòng trùng là dòng cũ chưa có mã thì câu cảnh báo ghi «Từ khóa trùng dòng **mới** trong kế hoạch»: dễ hiểu nhầm là dòng vừa thêm; nên ghi «dòng chưa có mã».
- **G11** Dò số điện thoại nay cho cách tới 3 ký tự (cả xuống dòng, ngoặc) nên có thêm vài dương tính giả kiểu «Lô 0 - 1 - 2 - … - 9» (hiếm; chỉ là cảnh báo, người dùng vẫn gửi được). Từ khóa có «quán» (bỏ dấu thành «quan») vẫn bị coi là địa danh («lắp cửa kính quán cà phê / quán trà sữa / quán ăn» → cảnh báo cửa ngõ), có từ lượt 1.
- **G12** Cho T-100: mã bài nay chuẩn hóa («B-1» → «B-001»): khi ghi Sheet theo mã phải so mã trên Sheet sau chuẩn hóa (ô Sheet có thể còn «B-1»); đề xuất «Cấp mã bài» cho dòng cũ chưa có mã: T-100 phải tìm dòng đó không qua mã.

### Không lùi `main`

- `main` cục bộ `1b45f5d` (đã gộp T-096, chưa lên GitHub) và nhánh không sửa chung file nào (gốc chung `15bfaca`).
- Bản gộp thử trong `git worktree` tạm (không nhánh, không push, đã gỡ): gộp không xung đột; 22 file test (kế hoạch, lời dặn, nội dung, liên kết nội bộ, T-096, T-083, T-062, trang app): **3797 passed, 4 xfailed, 0 failed**; file test của tôi bản lượt 2 trên bản gộp: **296 passed, 11 xfailed**. Test canh SL-7 (mọi hàm `…_prompt` có `keyword`) vẫn qua sau khi `main` đổi `seo_app/images/alt.py` (T-083); T-096 không thêm lời dặn có từ khóa.

### Bằng chứng (lượt 2)

- `uv run pytest tests/test_soi_loi_t098.py`: **296 passed, 11 xfailed**; `--runxfail` với SL-T098-12 → -17: 11 hỏng, đúng câu khẳng định (`BAD_TABLE`, bài giả, thiếu cảnh báo cửa ngõ, cảnh báo số điện thoại thừa, giờ `00:00`, `ValueError`).
- 10 file test liên quan trên nhánh (4 file kế hoạch, file của tôi, `test_soi_loi_t003_t009.py`, `test_t040_prompts.py`, `test_content_workflow.py`, `test_prompt_data_frames.py`, `test_content_edge_cases.py`): **728 passed, 11 xfailed**.
- `uv run ruff check .` sạch; `ruff format --check` file test sạch; `PYTHONUTF8=1 uvx detect-secrets scan` (file test + mồi thử): chỉ bắt mồi; quét ký tự ẩn: sạch.
- Script thử lượt 2: `T-098-soi-loi-scripts/round2.py` (thư mục ghi chú chung).

### Đề xuất (lượt 2)

1. Chuyển Lá Chắn rút gọn được ngay (không lỗi Trung bình trở lên).
2. Thợ Máy sửa trong một lượt nhỏ trước khi gộp: SL-T098-13, -17, -12 (mỗi lỗi vài dòng); -14, -15, -16 sửa cùng lúc nếu tiện (đều nhỏ). Gỡ dấu `xfail` khi XPASS (R5).

---

## Lượt 3 (2026-10-28 17:33 +07:00) · soát lượt sửa của Thợ Máy (`34302fa`)

| Mục | Nội dung |
|---|---|
| Phiếu giao | Chỉ Huy B, 28/10 16:00 (làm tiếp 17:30): xác nhận SL-T098-12 → -17 đóng (thêm biến thể gần, nhất là -13, -17, -12), soát R5, tìm lỗi mới do lượt 3, không lùi 11 lỗi lượt 1, chạy được với `main` mới nhất `d1506cb` (có T-096, T-090, T-097) |
| Đầu nhánh soát | `34302fa` (Thợ Máy lượt 3; Lá Chắn rút gọn `b520623` ĐẠT CÓ ĐIỀU KIỆN) |
| **Kết luận lượt 3** | **ĐẠT CÓ ĐIỀU KIỆN**: SL-T098-12 → -17 **đóng cả 6** (SL-T098-13 đóng đủ các ca đã nêu; một biến thể gần còn lỗi, ghi thành SL-T098-19); 11 lỗi lượt 1 **không lùi**; 0 Nghiêm trọng, 0 Cao, 0 Trung bình; **3 Thấp mới**: SL-T098-18 (do lượt 3), -19 (biến thể của -13, do G7 lượt 2), -20 (có từ lượt 1). **Không lỗi nào chặn gộp**; nên sửa trước T-100, T-101 (đều nhỏ) |
| Bảo mật | Lượt 3 **không** đụng bộ kiểm thẻ HTML, bộ làm sạch ký tự vô hình, biểu thức dò số điện thoại, email. Chỗ gần bảo mật: (1) cảnh báo «AI có số điện thoại hoặc email» nay chỉ xét chữ do AI đưa: đúng ý, không bỏ sót chữ mới nào của AI (đã thử «Thêm», «Cập nhật», «Bỏ», lý do); (2) biểu thức mới (`_SERIAL_TIME_RE`, nhánh «p/q đứng riêng» của `_LOCATION`) và đọc CSV hai lượt chạy tuyến tính (chuỗi độc 20.000 ký tự ≤ 3 ms; CSV 1.000 dòng đọc hai lượt 0,09 s; giới hạn 1.000 dòng, 26 cột vẫn dừng ngay); (3) lượt đọc lại không `strict` ảnh hưởng **toàn vẹn dữ liệu** (SL-T098-18), không phải bảo mật. Theo tôi không cần Lá Chắn xem lại |

### Tóm tắt (cho chủ dự án)

- 6 lỗi nhỏ lần trước đã sửa thật: ô bắt đầu bằng ngoặc kép không còn làm hỏng cả bảng; bảng dạng «mục – nội dung» (cả file yêu cầu phần mềm) không còn ra bài giả; «P. Tân Định» lại có cảnh báo trang cửa ngõ; cảnh báo «AI có số điện thoại» chỉ hiện khi chính AI viết số; ô ngày `46337.0` là ngày, không thành 0 giờ đêm; kế hoạch có mã «B-99999» chạy bình thường.
- Còn 3 lỗi nhỏ, không nguy hiểm, không chặn:
  1. File CSV có một dấu ngoặc kép quên đóng, mà phía dưới còn ô có ngoặc kép, thì các dòng ở giữa bị gộp vào một ô, không báo (lần 2 đã chặn đúng; lần sửa này làm lộ lại).
  2. Bảng «brief» xuất CSV có dòng tên phía trên rồi các dòng «Từ khóa, …», «Ngày, …» vẫn ra bài giả.
  3. Bảng có dòng mới tự ghi Mã bài (ví dụ «B-004») đứng sau một dòng mới chưa có mã thì mã bị đổi sang số khác, không báo (có từ lần đầu).
- Không có gì phải anh/chị quyết.

### R5

| Test | Thay đổi | Kết luận |
|---|---|---|
| `tests/test_soi_loi_t098.py` (của tôi) | 35 dòng xóa, 0 dòng thêm: đúng 6 dấu `@pytest.mark.xfail(...)` của SL-T098-12 → -17; thân test, điều kiện khẳng định không đổi | **Đúng R5** |
| `tests/test_plan_ai.py`, `test_plan_parse.py`, `test_plan_propose.py` (của Thợ Máy) | Chỉ thêm 6 test lượt 3; không xóa, không sửa dòng cũ | **Đúng R5** |

### Từng lỗi lượt 2

| Lỗi | Ca cũ | Biến thể gần (mới, đều qua) | Kết quả |
|---|---|---|---|
| SL-T098-12 | 2 ca qua | Dán và CSV ô «"Đức" là hãng tốt» đọc đủ 2 dòng; ngoặc giữa chữ («anh nói "gấp"») giữ nguyên; ô ngoặc rỗng; CSV chuẩn Excel (`"""Đức"" là hãng, tốt"`) đúng chữ; ngoặc không đóng tới hết file vẫn `BAD_TABLE` | **Đóng**; xem SL-T098-18 |
| SL-T098-13 | 3 ca qua | Markdown «Mục – Nội dung» có và không có dòng phân cách, tiêu đề gần giống («Từ khóa phụ – Ghi chú») → chữ tự do; tiêu đề ở dòng 2 của bảng (dòng tên phía trên), dòng phân cách đứng đầu → đọc đúng; file thật `yeu_cau_phan_mem_ProMetal_ToolSEO.md` lại là chữ tự do; CSV có dòng tên hai ô → chữ tự do (thận trọng) | **Đóng** các ca đã nêu; biến thể «dòng tên một ô + bảng khóa–giá trị không tiêu đề» còn lỗi: SL-T098-19 |
| SL-T098-14 | 1 ca qua | «P. Tân Định / P. Đa Kao / P. Bến Nghé», «Q. Bình Thạnh / Q. Gò Vấp / Q. Tân Phú», «p tân định / p đa kao / q bình thạnh» → cảnh báo cửa ngõ; «loại P / Q / X», «phụ kiện / phụ tùng / phí lắp» → không | **Đóng** |
| SL-T098-15 | 2 ca qua | 5 đề xuất một lượt: AI đổi ưu tiên dòng có số khách cũ → không cảnh báo, tick sẵn; «Bỏ» dòng có số trong tiêu đề cũ → không; AI đổi ghi chú thành chữ có số → có; «Thêm» có số trong tiêu đề → có; lý do có email → có | **Đóng** |
| SL-T098-16 | 2 ca qua | `46337.000` → ngày trần; `.5` → 12:00; `.25` → 06:00; 1.900 chữ số 0 → ngày trần; 1.500 số 0 rồi «1» → 00:00 (phần lẻ thật, đúng); ≤ 2 ms | **Đóng** |
| SL-T098-17 | 1 ca qua | Sau «B-99999»: so bảng cấp B-003, B-004 (số trống), AI «Thêm» B-003; 1.000 mã liền + «B-99999» → B-1001, B-1002 (0,02 s); `next_key` hết mã ra câu cố định; `plan_changes` đổi `PlanKeyError` thành `AIError` câu cố định (test Thợ Máy) | **Đóng** |
| 11 lỗi lượt 1 | 307 ca của lượt 1 và lượt 2 (gồm 44 ca từng là `xfail`) vẫn qua | — | **Không lùi** |

### Lỗi mới (lượt 3)

| # | Mức | Mô tả | Vị trí | Do | Test |
|---|---|---|---|---|---|
| SL-T098-18 | Thấp | Lượt đọc lại không `strict` (sửa SL-T098-12) làm SL-T098-3 sống lại ở dạng gần: ngoặc kép **không đóng** mà phía dưới còn một ô có ngoặc kép (ô chuẩn `"có, phẩy"` hay `"Đức" là hãng`) thì `csv` «đóng» ngoặc ở đó; lỗi `strict` không phải «hết file» nên đọc lại không `strict`: mọi dòng ở giữa bị gộp vào ô ghi chú, **không báo** (CSV và bảng dán). Lượt 2 chặn đúng (`BAD_TABLE`). Gợi ý: sau lượt không `strict`, ô nào có xuống dòng thì coi là lỗi (`BAD_TABLE`) hay báo; hoặc trước khi đọc chỉ bọc lại đúng dạng ô mở đầu bằng chữ trong ngoặc rồi có chữ sau trên **cùng một dòng**, rồi đọc `strict` | `seo_app/plan/parse.py:250` (`_csv_rows`) | SL-T098-12 (lượt 3) | `test_sl_t098_18_…` (CSV ×2, dán) |
| SL-T098-19 | Thấp | Biến thể gần của SL-T098-13 chưa đóng: CSV có **dòng tên một ô** phía trên một bảng «Mục – Nội dung» **không có dòng tiêu đề** (kiểu brief bài viết xuất từ Sheet: «BRIEF BÀI VIẾT», rồi «Từ khóa, sửa cửa cuốn», «Ngày, 12/11/2026»…): `_find_header` bỏ dòng tên rồi lấy dòng dữ liệu «Từ khóa, …» làm tiêu đề → «Ngày», «Ghi chú» thành bài giả, tick sẵn. Lượt 1 là chữ tự do. Gợi ý: đã bỏ qua dòng tên thì dòng tiêu đề phải nhận ra ít nhất hai cột | `parse.py:404` (`_find_header`) | G7 (lượt 2) | `test_sl_t098_19_…` |
| SL-T098-20 | Thấp (có từ lượt 1) | Bảng đưa vào có dòng mới **tự ghi Mã bài** (ví dụ «B-004», nối số kế tiếp) đứng **sau** một dòng mới chưa có mã: dòng chưa mã được cấp B-004 trước, dòng ghi B-004 bị đổi sang B-005, không báo. Đưa lại file đó: cùng thứ tự thì dòng «B-004» bị bỏ vì «trùng»; đổi thứ tự thì đề xuất đổi từ khóa của bài B-004 (bài khác) thành từ khóa dòng đó (có cảnh báo trùng, không tick sẵn). Gợi ý: giữ trước mọi mã mới ghi trong bảng (`take`), rồi mới cấp mã cho dòng chưa có mã | `propose.py:192` (`compare_rows`) | lượt 1 | `test_sl_t098_20_…` |

Ghi cho phiếu sau (không xếp lỗi): `compare_rows` có thể báo `PlanKeyError` (chỉ khi hết thật 99.999 mã): đường AI đã đổi thành `AIError`; đường bảng (T-101 gọi `compare_rows`) cần bắt `PlanKeyError` và hiện câu cố định của nó.

### Chạy được với `main` mới nhất

- `main` cục bộ `d1506cb` (T-096, T-090, T-097) và nhánh không sửa chung file nào (gốc chung `15bfaca`). T-097 có `PLAN_TAB = "KeHoach"` trùng tên với `model.SHEET_TAB`; chưa gọi `seo_app.plan` (T-100 nối).
- Bản gộp thử trong `git worktree` tạm (không nhánh, không push, đã gỡ), kèm file test lượt 3 của tôi: gộp không xung đột; 26 file test (kế hoạch, lời dặn, nội dung, liên kết nội bộ, T-096, T-083, T-062, T-097 Google Sheets, cấu hình, `.env`, trang app): **4586 passed, 4 skipped, 25 xfailed, 0 failed** (5 xfail là SL-T098-18 → -20 của tôi, còn lại của phiếu khác).
- 10 file test liên quan trên nhánh (4 file kế hoạch, file của tôi, `test_soi_loi_t003_t009.py`, `test_t040_prompts.py`, `test_content_workflow.py`, `test_prompt_data_frames.py`, `test_content_edge_cases.py`): **766 passed, 5 xfailed**.

### Bằng chứng (lượt 3)

- `uv run pytest tests/test_soi_loi_t098.py`: **328 passed, 5 xfailed**; `--runxfail` với SL-T098-18 → -20: 5 hỏng, đúng câu khẳng định (dòng bị gộp, bài giả, `B-005` thay vì `B-004`).
- `uv run ruff check .` sạch; `ruff format --check` file test sạch; quét ký tự ẩn và `PYTHONUTF8=1 uvx detect-secrets scan` (file test + mồi thử): sạch.
- Script thử lượt 3: `T-098-soi-loi-scripts/round3.py`, `round3_speed.py` (thư mục ghi chú chung).

### Đề xuất (lượt 3)

1. Gộp `main` được (không lỗi Trung bình trở lên, không đụng chỗ bảo mật).
2. Sửa SL-T098-18, -19, -20 trong một phiếu dọn nhỏ trước T-100 (T-100 dùng `compare_rows` và đọc bảng từ Sheet khác); gỡ dấu `xfail` khi XPASS (R5).

# Báo cáo T-098 · Kế hoạch: khuôn dữ liệu, đọc CSV/TSV/chữ dán, đề xuất có AI, SL-7 · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-098](../tickets/T-098-ke-hoach-khuon-doc-de-xuat.md), Thợ Máy đầu nhánh `ff8f542` (gốc `main` `15bfaca`) |
| Ngày nộp | 2026-10-28 |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, **2 Trung bình** (SL-T098-1, -2), **9 Thấp** (SL-T098-3 → -11), 8 góp ý. Test `xfail(strict=True)` cho cả 11 lỗi |
| **Phải sửa trước Lá Chắn** | **SL-T098-1** (bộ kiểm «AI không đưa HTML vào kế hoạch» bị lách bằng một ký tự vô hình; sửa 2–3 dòng). **Nên sửa cùng lượt**: SL-T098-2 (file kế hoạch nhiều bảng chỉ đọc bảng đầu: kế hoạch 6 tháng thật mất 104/112 dòng, không báo). Các lỗi Thấp không chặn; rẻ nên sửa trước khi gộp: SL-T098-3, -7, -11 |

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

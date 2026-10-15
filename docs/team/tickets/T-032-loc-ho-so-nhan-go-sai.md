# T-032 · Bộ lọc hồ sơ nhận cả nhãn gõ sai và nhãn trên tiêu đề

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Trung bình (nên xong trước khi chủ dự án tự điền mục 7 "chất liệu thật" của hồ sơ) |
| Phụ thuộc | Không. Không đụng file với T-019, T-025, T-031 |
| Trạng thái | Đã giao |

## Mục tiêu

Chủ dự án sửa `config/business_profile.md` bằng Notepad. Gõ nhãn `[CẦN XÁC NHẬN]` hơi sai (dính chữ, quên bật bộ gõ tiếng Việt, dùng ngoặc tròn) hay gắn nhãn lên tiêu đề của cả mục thì ý chưa chắc chắn vẫn **không** tới AI. Hướng "an toàn khi nghi ngờ": thà giấu thừa còn hơn để lọt.

## Bối cảnh

Lá Chắn kết luận T-022 + T-024 **ĐẠT**, kèm 4 lỗi Thấp (`docs/team/reports/T-022-024-la-chan.md`). Phiếu này sửa lỗi #1, #2 và #4. Lỗi #3 (lọc thừa đoạn thụt lề kiểu Word) **giữ nguyên**, vì cách sửa sẽ mở chiều ngược lại.

- **#1:** `seo_app/content/rules.py` (`_UNCONFIRMED_PATTERN = r"\[\s*CẦN\s+XÁC\s+NHẬN"`) không nhận các nhãn gõ sai sau:
  - `[CẦNXÁC NHẬN]`, `[CẦN XÁCNHẬN]` (dính chữ);
  - `[CAN XAC NHAN]` (không dấu);
  - `(CẦN XÁC NHẬN)` (ngoặc tròn);
  - nhãn bị xuống dòng giữa chừng (`[CẦN XÁC` ở cuối dòng này, `NHẬN]` ở đầu dòng sau, cùng một ý).
- **#2:** nhãn đặt trên tiêu đề (`## 7. Chất liệu thật [CẦN XÁC NHẬN]`) chỉ giấu dòng tiêu đề, các ý bên dưới vẫn tới AI. Chủ dự án dễ nghĩ "gắn nhãn lên tiêu đề là giấu cả mục".
- **#4:** `prompts.py` nhập tên "riêng" `_IGNORABLE_NOT_CF` từ `rules.py`.

## Phạm vi

- **Được sửa:**
  - `seo_app/content/rules.py`;
  - `seo_app/content/prompts.py` (chỉ dòng nhập tên ở lỗi #4);
  - test của bộ lọc (`tests/test_profile_blocks.py`, `tests/test_soi_loi_t024.py` và test mới);
  - trong `config/business_profile.md`, **chỉ các dòng ghi chú `>`** ở phần "CÁCH ĐỌC FILE NÀY" đầu file, để hướng dẫn khớp hành vi mới. Không sửa dòng nào AI thấy.
- **Không được sửa:** `app/**`, `seo_app/ai/**`, `seo_app/sanitize.py`, phần nội dung hồ sơ.
- **Ngoài phạm vi:** lỗi #3. Muốn đổi thì báo Chỉ Huy, không tự làm.

## Yêu cầu

1. **Nhận nhãn gõ sai (#1).** Coi là có nhãn khi gặp **ngoặc mở** (`[` hoặc `(`; dạng toàn khổ `［`, `（` đã qua NFKC), rồi tới cụm `CẦN XÁC NHẬN`, chấp nhận các biến thể sau:
   - dấu cách giữa các chữ có hay không đều được (`\s*`);
   - **không dấu**: so thêm trên chữ đã bỏ dấu (tách bằng NFD, bỏ dấu kết hợp, đổi `Đ` thành `D`), nên `[CAN XAC NHAN]`, `[CẦN XAC NHẬN]` cũng tính;
   - thêm cụm `CHƯA XÁC NHẬN` (gõ nhầm chữ đầu, ý vẫn là "chưa chắc"), có dấu hoặc không dấu.
   - **Vẫn bắt buộc có ngoặc mở.** Câu thường trong hồ sơ như "khách cần xác nhận lịch trước khi thợ tới" không được bị giấu. Viết test cho câu này.
   - Giữ nguyên mọi thứ đang đúng: ký tự vô hình chen trong nhãn, viết thường, tab, dấu cách không ngắt, ngoặc toàn khổ.
2. **Nhãn bị xuống dòng (#1).** Xét nhãn trên **cả khối** (các dòng trong khối nối nhau bằng dấu cách), không chỉ từng dòng. Nhãn nằm vắt qua hai dòng của cùng một ý thì bỏ cả ý.
3. **Nhãn trên tiêu đề (#2).** Tiêu đề có nhãn thì giấu tiêu đề đó **và mọi dòng bên dưới**, tới tiêu đề kế tiếp **cùng cấp hoặc cao hơn** (số dấu `#` bằng hoặc ít hơn). Ví dụ `## 7. … [CẦN XÁC NHẬN]` giấu tới `## 8.` hoặc `# …`, không dừng ở `### 7.1`. Dòng `>` vẫn luôn bị bỏ như cũ.
4. **Tên công khai (#4).** Đổi `_IGNORABLE_NOT_CF` thành tên công khai (ví dụ `IGNORABLE_NOT_CF`), sửa chỗ nhập trong `prompts.py`. Hành vi không đổi.
5. **Hướng dẫn đầu hồ sơ.** Cập nhật dòng `>` ở phần "CÁCH ĐỌC FILE NÀY" cho khớp: nhãn viết hoa/thường, có dấu/không dấu, ngoặc vuông hay tròn đều được; gắn nhãn lên tiêu đề thì giấu cả mục tới tiêu đề cùng cấp kế tiếp. Viết ngắn, tiếng Việt dễ hiểu. Sau khi sửa, chạy bộ lọc trên hồ sơ thật: phần AI thấy **không đổi** so với trước (so chuỗi), vì hồ sơ hiện tại gõ nhãn đúng hết.
6. **Test**, không gọi mạng:
   - mỗi kiểu gõ sai ở #1 bị lọc, kể cả viết thường và có ký tự vô hình chen vào;
   - câu "cần xác nhận" không có ngoặc **không** bị lọc;
   - nhãn vắt qua hai dòng của một gạch đầu dòng;
   - nhãn trên tiêu đề `##` giấu cả mục, kể cả mục con `###`; dừng đúng ở `##` hoặc `#` kế tiếp; nhãn trên tiêu đề `###` không giấu mục `##` kế sau;
   - đổi `test_misspelled_tags_are_not_recognised` và `test_glued_tag_still_not_recognised_but_invisible_separator_is` theo hành vi mới (đổi tên cho đúng nghĩa). Không xóa trường hợp nào: mỗi trường hợp cũ phải được kiểm theo hành vi mới;
   - hồ sơ thật: phần AI thấy không đổi.
7. Tốc độ: bộ lọc vẫn tuyến tính (đã có test tốc độ của T-015, T-024). Không thêm vòng lặp lồng theo số dòng.

## Yêu cầu bảo mật riêng

A1, A3 (thông tin chưa xác nhận không tới AI), D3 (test không gọi mạng). Hướng an toàn khi nghi ngờ: trường hợp không rõ thì giấu.

## Tiêu chí xong

- [ ] Các kiểu gõ sai ở #1 và nhãn trên tiêu đề ở #2 đều bị lọc, có test
- [ ] Câu thường có chữ "cần xác nhận" không bị lọc
- [ ] Phần hồ sơ thật AI thấy không đổi
- [ ] `uv run pytest` và `uv run ruff check .` sạch trên Linux
- [ ] Báo cáo `docs/team/reports/T-032-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có.
- Lá Chắn: Có (A1, A3).

## Ghi chú của Chỉ Huy

- Làm trong phiên con **"Thợ Máy · T-032 Bộ lọc hồ sơ nhận nhãn gõ sai"**, trên nhánh tạm `team/T-032` (tạo từ `main`). Commit và đẩy lên `team/T-032`; không đẩy `main`.
- Chỉ Huy B cho phép Thợ Máy sửa các dòng `>` đầu `config/business_profile.md` (thường là việc của Ngòi Bút), vì đó chỉ là hướng dẫn cho chủ dự án và phải khớp với code.

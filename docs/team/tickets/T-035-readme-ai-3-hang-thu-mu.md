# T-035 · README và chú thích `config/ai.toml`: 3 hãng AI, thử mù

| Mục | Nội dung |
|---|---|
| Giao cho | Thư Ký (`thu-ky`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 2 (đóng giai đoạn) |
| Mức ưu tiên | Trung bình (README đang chỉ nói tới Claude, chủ dự án đọc sẽ hiểu sai) |
| Phụ thuộc | T-032 đã gộp vào `main`, vì README nói về nhãn `[CẦN XÁC NHẬN]` mà T-032 đổi cách nhận |
| Trạng thái | Chờ T-032 |

## Mục tiêu

Chủ dự án đọc README và chú thích đầu `config/ai.toml`, rồi tự làm được 4 việc mà không phải hỏi:
1. lấy khóa của cả 3 hãng;
2. đổi hãng hoặc mô hình cho từng việc;
3. dùng thử mù để chọn mô hình;
4. hiểu các câu lỗi thường gặp.

## Bối cảnh

- Giai đoạn 2 đã có:
  - 3 hãng: Claude (`anthropic`), ChatGPT (`openai`), Gemini (`gemini`), T-018;
  - nút Kiểm tra khóa cả 3 hãng, T-023;
  - **thử mù mô hình** ở **Cài đặt → 🤖 Mô hình AI**, T-019;
  - bộ lọc hồ sơ nhận cả nhãn gõ sai và nhãn trên tiêu đề, T-032.
- Chủ dự án chốt 2026-10-15: **không có hãng mặc định**. Đủ 3 hãng, tự đổi khi cần.
- README mục 7 ("Viết bài bằng AI") còn viết như lúc chỉ có Claude: chỉ hướng dẫn `console.anthropic.com`, bảng lỗi chỉ có `ANTHROPIC_API_KEY`.
- `config/ai.toml` dòng đầu ghi `Hiện có "anthropic". "openai" và "gemini" sẽ thêm sau.`: sai.

## Phạm vi

- **Được sửa:**
  - `README.md`: mục 7, và mục khác nếu nhắc tới AI hay `.env`;
  - `config/ai.toml`: **chỉ các dòng chú thích `#`**, không đổi giá trị nào;
  - `.env.example`: chỉ chú thích, nếu thiếu hướng dẫn lấy khóa ChatGPT hoặc Gemini.
- **Không được sửa:** code, test, giá trị trong `config/`.

## Yêu cầu

1. **README mục 7:**
   - Lấy khóa ở đâu cho từng hãng: Anthropic Console, OpenAI Platform, Google AI Studio. Cần nạp tiền hay không. Nhập khóa trong **Cài đặt → 🔌 Kết nối**, rồi bấm **Kiểm tra**.
   - Đổi hãng/mô hình cho một việc: sửa `provider` và `model` trong `config/ai.toml`, kèm một ví dụ ngắn. Nói rõ không có hãng mặc định.
   - **Thử mù:** vào đâu, chọn 2–3 ứng viên, app báo trước số lần gọi AI (tốn tiền), chấm điểm rồi mới hiện tên, sau đó sửa `config/ai.toml` theo kết quả.
   - Bảng lỗi thường gặp: dùng **đúng** câu app hiện ra (đọc trong `seo_app/ai/`, `seo_app/content/blind_test.py`, `seo_app/env_file.py`) cho cả 3 hãng: thiếu khóa, khóa sai, hết tiền, bài dài quá giới hạn, máy chủ bận. Không bịa câu.
   - Dòng về `config/business_profile.md`: ý có nhãn `[CẦN XÁC NHẬN]` bị bỏ qua (viết hoa/thường, có dấu/không dấu, ngoặc vuông/tròn đều được); nhãn trên tiêu đề giấu cả mục. Lấy đúng theo phần ghi chú đầu `config/business_profile.md` sau T-032.
2. **Chú thích đầu `config/ai.toml`:**
   - `provider` nhận `"anthropic"`, `"openai"`, `"gemini"`. Mỗi hãng một ví dụ tên mô hình: lấy từ code và test hiện có, không bịa tên.
   - `effort` có ý nghĩa thế nào với từng hãng (nếu code ánh xạ khác nhau).
   - Có việc `blind_test` không. Nếu thử mù không đọc mục nào trong file này thì nói rõ.
3. Viết theo `docs/team/README.md`: tiếng Việt, ngắn gọn, cho người ít dùng kỹ thuật. Không nêu giá tiền cụ thể (giá đổi theo thời gian; hướng chủ dự án xem trang giá của hãng).
4. Đổi xong chạy `uv run pytest tests/test_app_pages.py` và các test đọc `config/ai.toml` (`grep -rl "ai.toml" tests/`). Chú thích không được làm hỏng file TOML.

## Yêu cầu bảo mật riêng

- S1, S3: không có khóa thật hay khóa mẫu giống thật. Ví dụ dùng dạng `sk-...` rút gọn hoặc mô tả bằng chữ.
- Không hướng dẫn tắt kiểm tra SSL hay đổi địa chỉ máy chủ AI.

## Tiêu chí xong

- [ ] README mục 7 đúng với app hiện tại, đủ 3 hãng và thử mù
- [ ] Chú thích `config/ai.toml` đúng, giá trị không đổi (so `git diff`: chỉ dòng `#`)
- [ ] Báo cáo `docs/team/reports/T-035-thu-ky.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Không (không có code). Chỉ Huy soát câu lỗi trong bảng đối chiếu với code.
- Lá Chắn: Rút gọn (S1, S3; file cấu hình chỉ đổi chú thích).

## Ghi chú của Chỉ Huy

- Làm trong phiên con **"Thư Ký · T-035 README 3 hãng AI, thử mù"**, trên nhánh tạm `team/T-035` (tạo từ `main` sau khi T-032 gộp).

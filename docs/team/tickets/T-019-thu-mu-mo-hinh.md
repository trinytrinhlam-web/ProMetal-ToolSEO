# T-019 · Thử mù mô hình AI trong Cài đặt

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`): phần logic. Sau đó Họa Sĩ (`hoa-si`): giao diện |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 2 (việc cuối cùng của giai đoạn, cùng T-028) |
| Mức ưu tiên | Cao |
| Phụ thuộc | T-018 (đã lên `main`). Không đụng file với T-028 (T-028 sửa `seo_app/ai/**`, phiếu này **không** sửa thư mục đó) |
| Trạng thái | Đã giao (Thợ Máy) |

## Mục tiêu

Chủ dự án muốn tự chọn hãng và mô hình cho từng việc; app không có hãng mặc định (chốt 2026-10-15). Thử mù giúp chọn dựa trên chất lượng thật:
1. Cùng một đề, gửi cho 2–3 mô hình (khác hãng hoặc cùng hãng).
2. Hiện bài viết dưới tên A/B/C, không lộ tên mô hình.
3. Chủ dự án chấm điểm xong mới hiện tên.

Giao diện demo đã được duyệt nằm ở tab **🤖 Mô hình AI** của trang Cài đặt (`app/views/settings.py`, dữ liệu mẫu `seo_app/demo.py`: `AI_TASKS`, `BLIND_OUTPUTS`, `BLIND_MODELS`).

## Phạm vi

- **Thợ Máy được sửa:** file mới `seo_app/content/blind_test.py`, thêm hàm lời dặn trong `seo_app/content/prompts.py`, test mới.
- **Họa Sĩ được sửa (lượt sau):** `app/views/settings.py` (chỉ tab "🤖 Mô hình AI"), `seo_app/demo.py` (xóa mẫu không còn dùng), test giao diện.
- **Không được sửa:** `seo_app/ai/**` (T-028 đang sửa), `config/**`, các tab khác của Cài đặt.
- **Ngoài phạm vi:** ghi lựa chọn mô hình ngược vào `config/ai.toml` từ giao diện. Trang chỉ hướng dẫn cách sửa file.

## Yêu cầu: Thợ Máy

1. `blind_test.py` có một hàm chạy thử mù. Đầu vào:
   - từ khóa, kèm ghi chú ngắn nếu có;
   - danh sách 2–3 ứng viên (`provider`, `model`, `effort`);
   - `Settings`.

   Mọi ứng viên nhận **cùng** system prompt và **cùng** lời dặn. Việc giao cho AI: viết mở bài và một mục ngắn cho từ khóa, theo quy tắc nội dung hiện có (`ContentRules`, hồ sơ doanh nghiệp). Gọi qua `make_provider(...).generate(...)` với khuôn có sẵn hoặc khuôn mới nhỏ.
2. Lời dặn mới (`prompts.py`): từ khóa và ghi chú của người dùng phải nằm trong khung dữ liệu, có vô hiệu thẻ khung (`security.md` 2.4), như các lời dặn khác.
3. Kết quả:
   - xáo thứ tự ngẫu nhiên rồi gắn nhãn A/B/C;
   - phần "nhãn → mô hình" trả **riêng**, để giao diện chỉ hiện sau khi chấm;
   - chữ AI qua `clean_ai_text`.
4. Một ứng viên lỗi (thiếu khóa, sai tên mô hình, hết tiền…) thì ứng viên đó mang câu lỗi tiếng Việt của `AIError`; các ứng viên khác vẫn có kết quả. Không chép lỗi thô.
5. Giới hạn chi phí:
   - tối đa 3 ứng viên;
   - `max_tokens` nhỏ (khoảng 2.000), không tìm web;
   - hàm có tham số ước tính số lần gọi để giao diện cảnh báo trước khi chạy.
6. Hàm phụ cho giao diện:
   - liệt kê hãng đã khai báo khóa (chỉ đúng/sai, không bao giờ trả khóa);
   - đọc bảng việc–mô hình từ `config/ai.toml` (dùng `load_ai_config`).
7. Test bằng provider giả, không gọi mạng:
   - xáo nhãn;
   - không lộ tên mô hình trong phần kết quả hiển thị;
   - một ứng viên lỗi;
   - dữ liệu người dùng có thẻ khung giả;
   - quá 3 ứng viên;
   - kết quả có HTML hoặc link bị lọc.

## Yêu cầu: Họa Sĩ (làm sau Thợ Máy, cùng nhánh)

1. Bảng việc–mô hình đọc thật từ `config/ai.toml`. Sửa chú thích sai: hiện ghi `config/ai_models.toml`, đúng là `config/ai.toml`.
2. Khu thử mù:
   - nhập từ khóa và ghi chú;
   - chọn 2–3 ứng viên: hãng chỉ trong số đã khai báo khóa, tên mô hình gợi ý sẵn từ `config/ai.toml`;
   - cảnh báo "sẽ gọi AI N lần, tốn tiền" rồi mới chạy;
   - hiện A/B/C an toàn (không `unsafe_allow_html` với chữ AI);
   - thanh điểm, nút "Chấm xong — hiện tên mô hình".
3. Sau khi hiện tên: hướng dẫn ngắn cách đổi `provider`/`model` trong `config/ai.toml`.
4. Xóa `AI_TASKS`, `BLIND_OUTPUTS`, `BLIND_MODELS` khỏi `seo_app/demo.py` nếu không còn dùng. Bỏ nhãn demo của tab này. Giữ bố cục đã duyệt.
5. Test giao diện bằng `AppTest` và hàm giả; trang vẫn qua `tests/test_app_pages.py`.

## Yêu cầu bảo mật riêng

A1 (dữ liệu người dùng trong khung), A2, S2 (lỗi không lộ khóa), U1 (chữ AI không qua HTML), D3.

## Tiêu chí xong

- [ ] Thử mù chạy được với 2–3 ứng viên khác hãng (chứng minh bằng test với provider giả)
- [ ] Không lộ tên mô hình trước khi chấm
- [ ] `uv run pytest` và `uv run ruff check .` sạch (trên Linux chỉ chấp nhận 9 test đỏ sẵn của T-027 nếu T-030 chưa gộp)
- [ ] Báo cáo `docs/team/reports/T-019-tho-may.md` và `docs/team/reports/T-019-hoa-si.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (A1, U1, S2).

## Ghi chú của Chỉ Huy

- Nhánh tạm `team/T-019` (tạo từ `main`). Phiên **"Thợ Máy · T-019 Thử mù mô hình"**, sau đó **"Họa Sĩ · T-019 Thử mù mô hình"**.

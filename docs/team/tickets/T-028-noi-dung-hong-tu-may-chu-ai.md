# T-028 · Máy chủ AI trả mã 200 nhưng nội dung hỏng: báo lỗi tiếng Việt, không hiện traceback

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Thấp (phải xong trước khi hết Giai đoạn 2) |
| Phụ thuộc | T-026 đã gộp vào `main` (cùng sửa `seo_app/ai/**`) |
| Trạng thái | Mới |

## Mục tiêu

Khi máy chủ AI trả về nội dung hỏng, trang Soạn bài và nút Kiểm tra khóa hiện câu tiếng Việt dễ hiểu, không bao giờ hiện traceback hay lỗi thô của Python.

## Bối cảnh

Soi Lỗi phát hiện khi kiểm T-026 (SL-T026-4, `docs/team/reports/T-026-soi-loi.md`). Lỗi có sẵn trên `main` từ trước T-026:

- Anthropic nhận mã 200 kèm HTML, JSON thường thay vì luồng SSE, hoặc SSE hỏng → `AssertionError` / `JSONDecodeError` thô lọt ra, Streamlit hiện traceback.
- OpenAI nhận mã 200 kèm JSON hỏng → `JSONDecodeError` thô.
- Tình huống thật: proxy hoặc cổng mạng công ty chen trang HTML, máy chủ trục trặc giữa chừng.

Soi Lỗi đã viết sẵn test `xfail(strict=True)` cho SL-T026-4 trong `tests/test_soi_loi_t026.py`.

## Phạm vi

- **Được sửa:** `seo_app/ai/**`, `seo_app/env_file.py` (phần kiểm tra khóa), test mới cho phần mình làm. Bỏ dấu `xfail` của đúng các test SL-T026-4 khi đã sửa xong, ghi tên vào báo cáo.
- **Không được sửa:** `app/**`, `config/**`, `tests/conftest.py`.
- **Ngoài phạm vi:** SL-T026-3 (Gemini nhận JSON sai kiểu ra câu "uv sync" thay vì "dữ liệu lạ"), Chỉ Huy đã chấp nhận ở T-026.

## Yêu cầu

1. Cả 3 hãng, cả lúc viết bài (`generate`) lẫn lúc kiểm tra khóa: nội dung trả về không đọc được (HTML, JSON hỏng, luồng SSE hỏng, thiếu trường) thì ra `AIError` tiếng Việt kiểu "máy chủ AI trả về dữ liệu lạ, thử lại sau". Câu báo không chép nội dung máy chủ.
2. Không bắt nhầm thành câu "uv sync" của T-026.
3. Test cho mọi nhánh mới, dùng mạng giả (`MockTransport` hoặc `tests/fake_ai.py`), không gọi mạng thật.

## Yêu cầu bảo mật riêng

S2 (không lộ khóa, không chép nội dung máy chủ vào thông báo lỗi), A2.

## Tiêu chí xong

- [ ] Các test SL-T026-4 bỏ `xfail` và qua; có test mới cho cả 3 hãng
- [ ] `uv run pytest` (0 hỏng, 0 lỗi trên Windows) và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-028-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có.
- Lá Chắn: Có (S2).

## Ghi chú của Chỉ Huy

- Làm trên nhánh tạm `team/T-028`, tạo từ `main` sau khi T-026 đã gộp.

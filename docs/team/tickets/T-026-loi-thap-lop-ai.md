# T-026 · Sửa 4 lỗi mức Thấp của lớp AI (sau T-018)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Thấp (phải xong trước khi hết Giai đoạn 2) |
| Phụ thuộc | T-018 (đã lên `main`) |
| Trạng thái | Đã giao |

## Mục tiêu

Lớp AI chịu được thư viện lệch phiên bản. Thông báo lỗi không bao giờ hiện câu thô của máy chủ. Không biến môi trường nào lái được app gọi sang máy chủ AI khác.

## Bối cảnh

Lá Chắn kết luận T-018 + T-023 **ĐẠT** và đề nghị gom 4 lỗi Thấp vào một phiếu, xem `docs/team/reports/T-018-023-la-chan.md`:

- **LC-1 = SL-3:** `seo_app/ai/openai_provider.py` khoảng dòng 52. `text_format()` nằm ngoài `try`. Nếu `openai.pydantic_function_tool` đổi cách dùng thì lỗi `AttributeError` thô lọt ra.
- **LC-2 = SL-4:** `seo_app/ai/registry.py` khoảng dòng 103. `make_provider` chỉ bắt `ImportError`, chưa bắt `AttributeError` lúc nhập thư viện (ví dụ google-genai bỏ hằng `types.ThinkingLevel`).
- **LC-3:** lỗi 400 hiện nguyên câu của máy chủ. Câu này đã che khóa nhưng vẫn còn Markdown. Khóa không có tiền tố, viết dạng ` key=…` (sau dấu cách), thì không bị che. Lá Chắn đề nghị: chỉ hiện câu cố định tiếng Việt kèm mã lỗi.
- **LC-4:** các biến môi trường `OPENAI_BASE_URL`, `GOOGLE_GEMINI_BASE_URL` và biến tương tự của Anthropic đổi được địa chỉ máy chủ mà thư viện gọi tới. Lá Chắn đề nghị: truyền `base_url` cố định (địa chỉ chính thức) khi tạo client.

Soi Lỗi đã viết sẵn test `xfail(strict=True)` cho SL-3 và SL-4 trong `tests/test_ai_openai_gemini_soi_loi.py`.

## Phạm vi

- **Được sửa:** `seo_app/ai/**`, `seo_app/env_file.py` (client kiểm tra khóa cũng phải dùng `base_url` cố định), test mới cho phần mình làm.
- **Không được sửa:** `app/**`, `config/**`. Test của Soi Lỗi chỉ được bỏ dấu `xfail` của đúng các test SL-3, SL-4 khi đã sửa xong, ghi tên vào báo cáo; phần còn lại để Soi Lỗi tự bỏ.
- **Ngoài phạm vi:** đổi mô hình mặc định.

## Yêu cầu

1. LC-1, LC-2: mọi lỗi do thư viện lệch phiên bản đều thành `AIError` tiếng Việt nhắc chạy `uv sync`. Áp dụng cho cả 3 hãng, lúc nhập thư viện lẫn lúc gọi.
2. LC-3: lỗi 400 của cả 3 hãng chỉ hiện câu cố định tiếng Việt kèm mã lỗi và tên mô hình. Có thể giữ một gợi ý ngắn đã lọc (chỉ chữ, số, dấu câu thường), nhưng không bao giờ chép câu thô.
3. LC-4: client của 3 hãng, cả trong `env_file.check_api_key`, dùng địa chỉ chính thức cố định. Biến môi trường đổi địa chỉ không có tác dụng. Có test chứng minh: đặt biến môi trường giả thì client vẫn trỏ đúng địa chỉ chính thức.
4. Test cho mọi nhánh mới, không gọi mạng.

## Yêu cầu bảo mật riêng

S2 (không lộ khóa trong lỗi), W4 / mục 2.7 (chỉ gọi máy chủ chính thức), D1, D3.

## Tiêu chí xong

- [ ] 4 lỗi LC-1 → LC-4 đã sửa, có test
- [ ] `uv run pytest` và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-026-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có.
- Lá Chắn: Có (S2, W4).

## Ghi chú của Chỉ Huy

- Làm trong phiên con **"Thợ Máy · T-026 Lỗi Thấp lớp AI"**, trên nhánh tạm `team/T-026` (tạo từ `main`). Mở khi còn chỗ (tối đa 3 phiên cùng lúc).
- 2026-10-15 (Chỉ Huy A): giao cho Thợ Máy chạy dưới phiên Chỉ Huy A trên máy chủ dự án (Windows), trong worktree riêng `D:\ProMetal-ToolSEO\wt-T-026`. Nhánh `team/T-026` tạo lại từ `main` `d91a80d`.
- Trên Windows, `main` đang có 152 test đỏ do bộ test (phiếu T-027 sửa song song). Tiêu chí "pytest sạch" của phiếu này tính là: **không có test hỏng nào ngoài danh sách đỏ sẵn đó**, và mọi test mới của phiếu đều qua. Ghi rõ trong báo cáo.

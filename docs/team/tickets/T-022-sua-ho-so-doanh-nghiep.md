# T-022 · Soát và sửa hồ sơ doanh nghiệp trước khi AI dùng

| Mục | Nội dung |
|---|---|
| Giao cho | Ngòi Bút (`ngoi-but`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Cao |
| Phụ thuộc | Không |
| Trạng thái | Đã giao |

## Mục tiêu

`config/business_profile.md` (từ PR #3, chủ dự án đồng ý gộp vào `main` ngày 2026-10-14) được đưa vào **mọi** prompt viết bài. Sau phiếu này, phần AI thấy phải đúng và đủ: không mất dòng quy tắc nào, không lọt dòng chưa xác nhận, không trái quyết định của chủ dự án.

## Bối cảnh

- `seo_app/content/rules.py`, hàm `confirmed_profile`: bỏ **mọi dòng chứa** chữ `[CẦN XÁC NHẬN` và mọi dòng bắt đầu bằng `>`. Phần còn lại vào khung `<ho_so_doanh_nghiep>` của prompt (`seo_app/content/prompts.py`).
- Lỗi đã biết: dòng 112 ("Chỉ nêu địa chỉ đã ghi ở mục 3; không dùng dòng nào mang nhãn [CẦN XÁC NHẬN]") là quy tắc nhưng chứa nhãn, nên bị bỏ mất.
- Quyết định của chủ dự án về doanh nghiệp: `BAN-GIAO.md` mục 7.4. Tóm tắt:
  - Không dùng năm thành lập, tên người phụ trách hay tác giả, bảng giá. Khách gửi ảnh qua Zalo để được báo giá.
  - Có thợ ở mọi khu vực TP.HCM. Địa chỉ cụ thể chỉ dùng 9 địa chỉ trên trang Liên hệ.
  - Câu chuyện khách thật và câu khách hay hỏi để sau; app sẽ hỏi chủ dự án theo từng bài.

## Phạm vi

- **Được sửa:** `config/business_profile.md`.
- **Không được sửa:** code Python, `config/content.toml`, `config/ai.toml`, `CLAUDE.md`.
- **Ngoài phạm vi:** đổi cách `confirmed_profile` lọc dòng (nếu thấy nên đổi, ghi vào mục Đề xuất).

## Yêu cầu

1. Viết lại dòng 112 để quy tắc vẫn còn sau khi lọc (không chứa chuỗi `[CẦN XÁC NHẬN`).
2. Soát cả file: không còn dòng quy tắc hay thông tin dùng được nào bị lọc nhầm, và không còn dòng chưa xác nhận nào lọt qua lọc.
3. Mục 7 (chất liệu thật, đang để trống): quyết định AI có nên thấy các gạch đầu dòng trống không. Nếu không, đổi sang dạng bị lọc (ví dụ dòng bắt đầu bằng `>`). Hướng dẫn cho chủ dự án cách điền phải còn rõ khi mở file bằng Notepad.
4. Đối chiếu với `BAN-GIAO.md` mục 7.4. Chỗ nào trái quyết định thì sửa. Chỗ tự mâu thuẫn hoặc cần chủ dự án quyết thì **không tự quyết**, ghi vào báo cáo để Chỉ Huy hỏi. Ví dụ dòng 69–70: báo giá "khoảng 15 phút", nhưng trang Bảng giá ghi "30 phút".
5. Báo cáo có phần "AI sẽ thấy gì": dán nguyên văn kết quả của `confirmed_profile` trên file sau khi sửa (chạy `uv run python -c "from seo_app.content.rules import load_rules; print(load_rules().business_profile)"`), kèm danh sách các dòng bị lọc.

## Yêu cầu bảo mật riêng

- A1: hồ sơ nằm trong khung dữ liệu. Không được viết câu nào có thể bị hiểu là chỉ thị vượt quyền, ví dụ "bỏ qua quy tắc…".
- A3: không có dữ liệu cá nhân khách hàng. Hotline, địa chỉ cửa hàng là thông tin công khai của doanh nghiệp, được phép.
- S1: không có khóa hay mật khẩu.

## Tiêu chí xong

- [ ] Quy tắc ở dòng 112 còn nguyên sau `confirmed_profile`
- [ ] Không còn dòng nào chứa `[CẦN XÁC NHẬN` trong phần AI thấy
- [ ] `uv run pytest` và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-022-ngoi-but.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có (sau Ngòi Bút). Thêm test trên file thật `config/business_profile.md`:
  - Mọi dòng của mục 8 (quy tắc) vẫn còn sau `confirmed_profile`.
  - Không dòng nào chứa nhãn lọt qua.
  - Hồ sơ đi vào đúng khung `<ho_so_doanh_nghiep>` của system prompt.
- Lá Chắn: Có (nội dung đi vào prompt AI: A1, A3, S1).

## Ghi chú của Chỉ Huy

- 2026-10-14: Chỉ Huy đã gộp nhánh `claude/project-thread-bcuk2m` (PR #3) vào `main`. Xung đột ở `CLAUDE.md` đã sửa bằng cách giữ cả hai bên.
- Làm trong phiên con **"Ngòi Bút · T-022 Hồ sơ doanh nghiệp"**, trên nhánh tạm `team/T-022`. Commit và đẩy lên `team/T-022`; không đẩy `main`. Chỉ Huy gộp vào `main` sau khi Lá Chắn ĐẠT.

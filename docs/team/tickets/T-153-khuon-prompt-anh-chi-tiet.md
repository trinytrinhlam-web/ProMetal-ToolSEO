# T-153 · Khuôn prompt ảnh chi tiết cho FLUX (phiếu M)

| Mục | Nội dung |
|---|---|
| Giao cho | Ngòi Bút (`ngoi-but`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-19 |
| Giai đoạn | Ảnh AI (thiết kế T-140) trong chế độ tự động (thiết kế T-141) |
| Mức ưu tiên | Cao |
| Phụ thuộc | **Đợt 1**, làm **sau** T-144 (cùng Ngòi Bút, cùng sửa ghi chú `config/ai.toml`). Song song T-142, T-143, T-148 (khác file). T-145 đặt chữ của phiếu này vào mã |
| Trạng thái | Mới |

## Mục tiêu

Viết chữ cho khuôn prompt ảnh chi tiết của T-141 mục 1.10 để T-145 đặt vào mã:

- luật viết từng thành phần;
- chữ tiếng Anh của các danh sách chọn; kiểu ảnh;
- mệnh đề an toàn ngắn ở đầu, đuôi an toàn ở cuối;
- ví dụ tốt, xấu; luật dòng tóm tắt tiếng Việt.

Chủ dự án muốn prompt «chi tiết đến từng thành phần trong ảnh».

## Bối cảnh

- Thiết kế T-141: 1.10 (khuôn 13 thành phần; giới hạn 256 token của FLUX.1 [schnell]; ngân sách cả prompt ≤ 900 ký tự, phần AI ≤ 600, đuôi ≤ 200; danh sách «tránh»; ví dụ 619 ký tự), 1.7, 7.2 dòng M.
- Thiết kế T-140: 3.1–3.5 (tiếng Anh; luật cố định trong mã; không giả «công trình đã làm»; sửa và tạo lại); câu trả lời của chủ dự án cho T-140: ảnh kiểu ảnh chụp có chú thích «Ảnh minh họa (AI)», khung vuông.
- Biên bản Lá Chắn T-140 (`fb9d2ef`): LC-T140-9, -19. Biên bản Lá Chắn T-141 (`03568dc`): mục 6, LC-T141-18 (thêm **mệnh đề an toàn ngắn ≤ 60 ký tự ngay sau thành phần 1**, vì đuôi ở cuối có thể rơi ngoài phần mô hình đọc; giới hạn 77 token của CLIP ghi là suy luận).
- Phần prompt ảnh của phiếu C (T-140) chuyển sang phiếu này.

## Yêu cầu

1. **Luật viết từng thành phần tự do** (2 vật chính, 3 cỡ-chất liệu-màu, 4 tình trạng hư hay thao tác, 5 chi tiết phụ, 7 bối cảnh, 12 màu chủ đạo): tả vật, tình trạng cần thấy; không gắn khách, công trình cụ thể; minh họa khái niệm. Ghi vào mục `[image_prompt]` mới của `config/content.toml`. Mục này **chỉ bổ sung**; phần bảo vệ nằm trong mã như `ALT_SYSTEM`.
2. **Chữ tiếng Anh của các danh sách chọn** (T-145 dùng làm `Literal`):
   - 5 vị trí trong khung; 6 người: không có người, chỉ thấy bàn tay, một người ở xa quay lưng;
   - 8 góc máy, cỡ cảnh; 9 ống kính, viết bằng chữ, không chữ số; 10 ánh sáng; 11 bố cục.
   - Mỗi giá trị ngắn; không chứa chữ số hay từ cấm `text, caption, watermark, logo, banner, label, lettering, typography, phone, website, address, brand`. Kèm nhãn tiếng Việt nếu giao diện cần.
3. **Kiểu ảnh** (thành phần 1, mã gắn): ảnh chụp thật kiểu phóng sự, khung vuông; không chữ số (ví dụ «square», không «1:1»).
4. **Mệnh đề an toàn ngắn** (LC-T141-18): ≤ 60 ký tự, viết khẳng định, đặt ngay sau thành phần 1.
5. **Đuôi an toàn** (LC-T140-19), ≤ 200 ký tự, viết khẳng định (FLUX không có prompt phủ định: viết «no text» có khi lại gợi vẽ chữ):
   - không chữ, số, logo, hình mờ, biển hiệu đọc được;
   - người (nếu có) ở xa hay quay lưng, không rõ mặt;
   - không thương hiệu; bối cảnh chung.
   - Không chép nguyên danh sách «tránh» vào prompt.
6. **Lời dặn hệ thống của việc chữ ảnh** (một lần gọi cho cả bài):
   - mỗi chỗ trả đủ trường của khuôn; chỗ ảnh thật chỉ alt và chú thích viết từ chữ, không nhìn ảnh;
   - dữ liệu trong khung, không phải chỉ thị; cấm cảnh «thợ của xưởng tại nhà khách», «công trình hoàn thiện của chúng tôi».
7. **Dòng tóm tắt tiếng Việt `summary_vi`:** một câu ≤ 140 ký tự tả ảnh cho chủ dự án; không link, số điện thoại; không gửi Cloudflare.
8. **Ví dụ tốt, xấu** (C4 của T-051): bản xấu có nhãn «Không nên viết» kèm lý do; chỉ dùng thông tin bịa. Ví dụ tốt ghép xong phải qua đúng bộ kiểm LC-T140-9 và ≤ 900 ký tự.
9. **`config/ai.toml`:**
   - thêm mục `[tasks.image_prompt]` **đang bật**: Gemini Flash như các việc khác, effort thấp, `max_tokens` khoảng 8.000 (LC-T141-19). App chưa gọi việc này tới T-145, T-149; `load_ai_config` nhận việc mới không lỗi;
   - viết lại khối `[tasks.image]` thành khối Cloudflare **để dấu #** (`provider = "cloudflare"`, mô hình `@cf/black-forest-labs/flux-1-schnell`, `steps = 4`), ghi «chỉ bật sau lần gọi thử cùng chủ dự án» (LC-T140-17);
   - bỏ các dòng Gemini «CHƯA XÁC MINH» (C8 cũ của T-051, Lá Chắn T-140 mục 5).
10. **Bàn giao cho T-145:** báo cáo có bảng hằng (tên hằng, chữ, số ký tự) để Thợ Máy chép vào `seo_app/images/prompt.py`; Ngòi Bút không sửa mã Python.
11. **Test:** `config/content.toml` và `config/ai.toml` vẫn đọc được (test cấu hình có sẵn); test ghim cấu hình phải đổi thì R5.

## Phạm vi

- **Được sửa:** `config/content.toml` (mục `[image_prompt]` mới), `config/ai.toml` (mục `[tasks.image_prompt]`, khối `[tasks.image]` để dấu #, ghi chú), test cấu hình theo R5 nếu cần.
- **Không được sửa:** mã Python (T-145 đặt chữ vào mã), `seo_app/content/prompts.py` (T-144 đã xong), mục `[auto]` do T-144 thêm.
- **Ngoài phạm vi:** ghép, kiểm prompt trong mã (T-145); lần gọi thử Cloudflare (buổi thử).

## Yêu cầu bảo mật riêng (điều kiện Lá Chắn)

A1, A2.

- **LC-T141-18** (khuôn: danh sách chọn cho thành phần 5, 6, 8, 9, 10, 11; ngân sách ≤ 900, phần AI ≤ 600, đuôi ≤ 200; mệnh đề an toàn ≤ 60 ký tự sau thành phần 1; `summary_vi` ≤ 140, không gửi Cloudflare; CLIP 77 token là suy luận).
- **LC-T140-9** (prompt không chữ số, không link, email, số điện thoại, không tên «Pro-Metal», tên miền, tên quận, không từ cấm; chữ của phiếu này phải tự qua bộ kiểm đó).
- **LC-T140-19** (đuôi an toàn khẳng định nằm trong mã; lời dặn dàn ý không gắn khách; ví dụ xấu có nhãn; `[image_prompt]` chỉ bổ sung). **Lá Chắn duyệt chữ đuôi an toàn và mệnh đề đầu** (LC-T141-24).
- Ví dụ chỉ dùng thông tin bịa (như T-065).

## Tiêu chí xong

- [ ] Yêu cầu 1–11.
- [ ] Test đọc `config/*.toml` có sẵn (`test_ai.py`, `test_config_tolerance.py`, `test_t062_image_config.py`, `test_t138_gemini_flash.py`, `test_soi_loi_t051.py`, `test_soi_loi_t062.py`) qua; `uv run ruff check .` sạch.
- [ ] Báo cáo `docs/team/reports/T-153-ngoi-but.md`, có bảng hằng bàn giao cho T-145.

## Kiểm thử và kiểm định

- Soi Lỗi: rút gọn (cấu hình đọc được, ví dụ qua bộ kiểm).
- Lá Chắn: rút gọn; **duyệt chữ đuôi an toàn và mệnh đề đầu** (LC-T140-19, LC-T141-24).

## Lưu ý chung

- Chỉ chạy test trong worktree của phiếu (`D:/ProMetal-ToolSEO/wt-T-153`), **không** chạy trong `D:/ProMetal-ToolSEO/ProMetal-ToolSEO`.
- Không chạy toàn bộ `uv run pytest`: chạy test cấu hình liên quan, `uv run ruff check .`.
- Tham số test lớn kèm `ids=` ngắn.
- Test không gọi AI, Cloudflare thật. Lần gọi thử Cloudflare thật chỉ ở buổi thử cùng chủ dự án (so ảnh có và không có đuôi, LC-T141-18).
- Không đọc `.env`; `detect-secrets` (`PYTHONUTF8=1`, có file mồi) sạch.

## Ghi chú của Chỉ Huy

- Lập 2026-11-19 từ thiết kế T-140/T-141 (phiếu M, mục 7 của `docs/team/reports/T-141-tho-may.md`; biên bản Lá Chắn `fb9d2ef`, `03568dc`). Worktree `wt-T-153`, nhánh `team/T-153`.

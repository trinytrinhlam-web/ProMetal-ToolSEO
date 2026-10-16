# T-046 · Thiết kế Giai đoạn 3 (ảnh): tìm hiểu kỹ thuật, chia phiếu

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-16 |
| Giai đoạn | Giai đoạn 3 (chuẩn bị) |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | Không. Phiếu này **không sửa code**, chỉ viết tài liệu thiết kế |
| Trạng thái | Đã giao |

## Mục tiêu

Trước khi viết code Giai đoạn 3, cần một thiết kế rõ ràng gồm:
- cách xử lý ảnh an toàn và đúng quyết định của chủ dự án;
- cách chia phiếu nhỏ;
- câu hỏi cho chủ dự án, nếu có.

## Quyết định đã chốt (thắng mọi tài liệu cũ hơn)

- **Giữ nguyên vị trí GPS trong ảnh.** Chủ dự án chốt 2026-10-14, có chủ đích, để làm SEO địa phương. Khi nén sang WebP phải **chép lại EXIF**. Phiếu T-007 (xóa GPS) đã hủy. `docs/plan/yeu_cau_phan_mem_ProMetal_ToolSEO.md` YC-304 ghi "xóa GPS" là **cũ**, không theo. Xem sổ rủi ro `docs/team/security.md` mục 6.
- **Thư viện Pillow được duyệt** (2026-10-16).
- Ảnh thật lấy từ **thư mục trên máy** do người dùng khai báo (`IMAGE_FOLDERS` trong `.env`: USB, thư mục Google Drive for Desktop). Không dùng Google Drive API.
- Mỗi chỗ cần ảnh trong bài chọn ảnh thật (từ thư mục) hoặc ảnh AI. Ảnh AI luôn kèm prompt xem, sửa, sao chép được (`CLAUDE.md`, mục "Quyết định đã chốt").
- AI có 3 hãng. Mô hình cho từng việc (alt ảnh, tạo ảnh) khai báo trong `config/ai.toml`, không có hãng mặc định.
- Mặc định mọi thứ gửi lên WordPress đều là **nháp**. Không có site thử nghiệm.

## Bối cảnh

- Yêu cầu của chủ dự án: `docs/plan/yeu_cau_phan_mem_ProMetal_ToolSEO.md`, mục M3 (YC-301 → YC-308). Đọc kèm `docs/plan/README.md` để biết phần nào đã lệch.
- Đã có:
  - `seo_app/wordpress/client.py`: `upload_media`, `upload_media_file`, `set_featured_image`;
  - `seo_app/config.py`: đọc `IMAGE_FOLDERS`;
  - lớp AI `seo_app/ai/` cho 3 hãng (hiện chỉ gửi chữ);
  - giao diện demo "chỗ cần ảnh" trong trang Soạn bài (`app/views/write.py`, `seo_app/demo.py`). Bố cục này chủ dự án **đã duyệt**.
- Chính sách bảo mật: `docs/team/security.md`, mục 2.6 (ảnh và file), dòng F1–F3.

## Phạm vi

- **Được làm:**
  - đọc code và tài liệu;
  - tìm hiểu tài liệu chính thức của Pillow, WordPress REST (media), API ảnh của 3 hãng AI (đọc ảnh để viết alt; tạo ảnh);
  - thử Pillow trong thư mục tạm, **ngoài repo**, bằng `uv run --with pillow`. Không thêm vào `pyproject.toml` ở phiếu này.
- **Không được làm:** sửa code, cấu hình, test; gọi API AI thật hay WordPress thật.
- **Được viết:** báo cáo `docs/team/reports/T-046-tho-may.md`.

## Yêu cầu: nội dung báo cáo

1. **Đọc ảnh từ thư mục**:
   - chỉ trong các thư mục đã khai báo; chặn `..`, symlink ra ngoài, đường dẫn tuyệt đối lạ (F1);
   - danh sách đuôi file được nhận;
   - giới hạn kích thước file và số điểm ảnh (chống "bom giải nén");
   - ảnh iPhone HEIC: Pillow có đọc được không. Nếu cần thêm thư viện thì nêu tên, lý do, phương án khác, và đưa thành câu hỏi cho chủ dự án;
   - quét thư mục lớn (hàng nghìn ảnh, ổ Google Drive chậm) mà không treo app.
2. **Xử lý ảnh** (YC-303):
   - tự xoay đúng chiều theo EXIF Orientation, rồi đặt lại Orientation = 1;
   - thu nhỏ cạnh dài (ví dụ 1600 px), nén WebP, chọn chất lượng;
   - **chép lại EXIF, có GPS, vào file WebP**. Chứng minh bằng thử nghiệm nhỏ (đọc lại GPS sau khi nén) và ghi kết quả;
   - EXIF có thông tin máy (hãng máy, số seri…) và ảnh chụp màn hình không có EXIF: xử lý thế nào. Nếu cần thì đưa thành câu hỏi cho chủ dự án, vì chủ dự án chỉ chốt "giữ GPS";
   - đặt tên file không dấu theo nội dung (dùng `slugify` có sẵn), tránh trùng tên.
3. **Alt ảnh bằng AI** (YC-305):
   - hãng nào đọc được ảnh, dữ liệu gửi đi ra sao, giới hạn kích thước;
   - lớp provider cần mở rộng gì (thêm việc `alt` trong `config/ai.toml`);
   - **ảnh gửi cho AI có nên bỏ EXIF/GPS không** (A3: không gửi dữ liệu thừa ra ngoài). Đề xuất: bỏ EXIF trong bản gửi AI, giữ trong bản tải lên web;
   - alt qua bộ lọc chữ AI (`clean_ai_text`), có độ dài giới hạn; người dùng duyệt (YC-305).
4. **Ảnh AI** (YC-306):
   - hãng nào tạo được ảnh, cách gọi, chi phí ước tính mỗi ảnh (lấy từ trang giá chính thức, ghi "chưa xác minh" nếu không chắc);
   - prompt xem, sửa, sao chép được;
   - đánh dấu ảnh AI (tên file, metadata, alt), không bao giờ gắn thẻ "công trình thật";
   - kiểm định dạng và kích thước ảnh trả về trước khi dùng.
5. **Gắn thẻ ảnh** (YC-302: hạng mục, khu vực, trước/sau, mã công trình):
   - lưu ở đâu để **2 máy cùng thấy**. Có các cách: file kèm ảnh trong thư mục Drive, cache SQLite cục bộ, WordPress media. Nêu ưu nhược từng cách;
   - đưa cách chọn thành câu hỏi cho chủ dự án nếu cần.
6. **Tải lên WordPress:** dùng `upload_media` có sẵn, đặt alt/caption, ảnh đại diện, chèn vào bài. Giữ W1–W4: chỉ nháp, chỉ bài do app tạo.
7. **Chia phiếu:** danh sách phiếu cho Giai đoạn 3. Mỗi phiếu ghi: mục tiêu, agent, file được sửa (không đụng nhau khi chạy song song), phụ thuộc, yêu cầu bảo mật. Phiếu logic thuần, test bằng ảnh giả tạo trong test, đặt trước. Phiếu đầu tiên là thêm Pillow vào `pyproject.toml` (đã duyệt).
8. **Câu hỏi cho chủ dự án:** không quá 5 câu, có lựa chọn kèm hệ quả, xếp theo mức cần thiết.

Viết tiếng Việt, ngắn gọn, có bảng. Điều gì chưa chắc thì ghi "chưa xác minh".

## Yêu cầu bảo mật riêng

F1, F2 (giữ GPS theo quyết định chủ dự án), F3, A1, A2, A3, W1–W4, D1 (chỉ Pillow đã duyệt; thư viện khác phải hỏi).

## Tiêu chí xong

- [ ] Báo cáo đủ 8 mục, có thử nghiệm EXIF/GPS sau khi nén WebP
- [ ] Không thay đổi code, cấu hình, test
- [ ] Đẩy báo cáo lên `team/T-046`

## Ghi chú của Chỉ Huy

- Phiên **"Thợ Máy · T-046 Thiết kế Giai đoạn 3"**, nhánh `team/T-046` (từ `main`).

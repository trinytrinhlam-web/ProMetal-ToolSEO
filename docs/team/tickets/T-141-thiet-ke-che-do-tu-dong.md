# T-141 · Thiết kế chế độ tự động: từ khóa hay kế hoạch → bài hoàn chỉnh → duyệt một lần ở bước Xuất bản

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) — thiết kế, chưa viết mã; Họa Sĩ góp phần giao diện |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-19 |
| Giai đoạn | Mới (sau bản 1.0 về tính năng, nhưng chủ dự án cần sớm) |
| Mức ưu tiên | Cao |
| Phụ thuộc | Thiết kế T-140 (ảnh tự chọn + ảnh AI Cloudflare; Lá Chắn `fb9d2ef` ĐẠT CÓ ĐIỀU KIỆN), T-137, T-138 (sắp gộp) |
| Trạng thái | Đang làm (thiết kế) |

## Quyết định của chủ dự án (2026-11-19)

Chủ dự án: «vấn đề của phần mềm này là thủ công cần quá nhiều… Muốn duyệt thì tôi chỉ cần xem ở bước cuối cùng. Nếu cần chỉnh sửa ở bước nào thì tôi sẽ chọn tới bước đó để chỉnh.»

1. **Soạn theo từ khóa:** nhập từ khóa → app **tự chạy hết** (ý định, nghiên cứu, dàn ý, viết, rà soát văn phong và tự sửa, SEO meta/slug/liên kết nội bộ/schema, chọn ảnh thư mục hay tạo ảnh AI, viết alt, chú thích) → **dừng ở bước 5 · Xuất bản**. Không bắt duyệt dàn ý, không bắt duyệt từng ảnh, không bắt nhập alt.
2. **Duyệt một lần ở bước Xuất bản** (chọn «Dừng ở bước Xuất bản»): màn hình cuối hiện đủ bài, ảnh, alt, SEO, cảnh báo; mỗi phần có nút **«Sửa»** nhảy về đúng bước; sửa xong quay lại bước cuối. **Không gì lên website khi chủ dự án chưa bấm** Gửi nháp / Hẹn giờ / Đăng ngay (giữ màn hình xác nhận, khóa gửi trùng T-086 → T-137).
3. **Theo kế hoạch:** nút **«Viết các bài tới hạn»** ở trang Kế hoạch: app tự viết các dòng có Ngày dự kiến trong **7 ngày tới**, **tối đa 5 bài mỗi lần bấm**, mỗi bài vào danh sách **«Chờ duyệt»**; chủ dự án mở từng bài ở bước Xuất bản, bấm Hẹn giờ theo ngày, giờ của dòng kế hoạch.
4. **Chất liệu thật:** lấy từ cột **«Ghi chú của thợ»** của dòng kế hoạch + **hồ sơ doanh nghiệp**. Thiếu thì AI **không bịa**, viết chung và **đánh dấu vàng** ở bước cuối để chủ dự án bổ sung nếu muốn.
5. Câu hỏi T-140 (chủ dự án chưa trả lời riêng; Chỉ Huy theo khuyến nghị, chủ dự án đổi được): ảnh AI kiểu ảnh chụp có chú thích «Ảnh minh họa (AI)»; ảnh tự tạo trong luồng tự động (không cần bấm riêng); ảnh vuông 1024×1024; không giới hạn số ảnh thật mỗi bài (chỉ lấy khi khớp rõ).

Quyết định này **thay** các quyết định cũ: duyệt dàn ý trước khi viết (quy trình nội dung bước 4), duyệt alt từng ảnh, «không sản xuất nội dung hàng loạt» (nay: tối đa 5 bài/lần, duyệt từng bài trước khi gửi).

## Việc (thiết kế, báo cáo `docs/team/reports/T-141-tho-may.md`)

1. **Luồng tự động một bài:** thứ tự bước, việc AI nào, chỗ nào code làm; dàn ý tự duyệt; viết; rà soát + tự áp dụng sửa (luật nào tự áp, luật nào chỉ cảnh báo); SEO tự điền (meta, slug, liên kết nội bộ, schema FAQ); ảnh: T-140 (tự chọn thư mục, không có thì tạo AI qua Cloudflare); alt, chú thích tự viết (ảnh thật: Gemini miễn phí đã chấp nhận ở sổ rủi ro; ảnh AI: alt từ prompt, không gửi ảnh); lưu nháp sau từng bước để F5/mất mạng không mất.
2. **Chạy lâu trong Streamlit:** mỗi bài nhiều lần gọi AI (vài phút); hiển thị tiến độ từng bước; dừng giữa chừng, chạy tiếp; lỗi 503/hạn mức Gemini miễn phí (thử lại có giới hạn, báo rõ); hai tab, hai máy; không chạy nền khi tắt app (giữ «app không chạy nền»).
3. **Màn hình duyệt cuối (bước 5):** những gì phải hiện; nút «Sửa» từng phần; các dấu vàng (thiếu chất liệu thật, câu cần xem lại, ảnh AI, ảnh thật tự chọn có thể có nhà khách); điều gì **chặn** gửi, điều gì chỉ **cảnh báo**; khóa gửi trùng; công tắc Hẹn giờ/Đăng ngay giữ nguyên luật.
4. **«Viết các bài tới hạn»:** chọn dòng (7 ngày, tối đa 5, bỏ dòng đã có nháp/đã gửi, trạng thái Sheet «Đang viết»), chạy lần lượt, danh sách «Chờ duyệt» (ở đâu: trang Bài viết hay Kế hoạch), ngày giờ hẹn lấy từ dòng; ghi trạng thái về Sheet khi gửi (đã có T-100).
5. **Đối chiếu với điều kiện cũ của Lá Chắn** bị đụng: duyệt alt (T-050, T-056), băm ảnh đã duyệt (T-086, T-089), ảnh tự chọn tick duyệt từng ảnh (LC-T140), ảnh gửi AI, dữ liệu kế hoạch là dữ liệu chưa tin cậy vào lời dặn AI (T-094, LC-T120-24) — đề xuất thay mỗi điều kiện bằng chốt ở bước cuối.
6. **Hạn mức:** ước số lần gọi AI mỗi bài; 5 bài có vượt hạn mức Gemini Flash miễn phí hay Cloudflare không; cách chia.
7. **Chia phiếu code** (Thợ Máy, Họa Sĩ, Ngòi Bút, Thư Ký), thứ tự gộp cùng các phiếu T-140 (A–F), câu hỏi còn mở cho chủ dự án (mỗi câu có khuyến nghị).

## Phạm vi

- Chỉ viết báo cáo thiết kế; đọc mã, tài liệu. Không sửa mã, không gọi AI hay website thật.

## Kiểm định

- Lá Chắn đọc thiết kế (đầy đủ) trước khi lập phiếu code.

## Ghi chú của Chỉ Huy

- Lập 2026-11-19 theo 3 câu trả lời của chủ dự án. Buổi thử thật Hẹn giờ/Đăng ngay đang dừng ở Ca 3 (làm tiếp khi chủ dự án rảnh). Worktree `wt-T-141`, nhánh `team/T-141` từ `main`.
- 2026-11-19 (Chỉ Huy B): thiết kế Thợ Máy 5f5c38e (luồng 1 bài, chạy lâu, màn hình duyệt cuối, «Viết các bài tới hạn», hạn mức, phiếu A–F sửa + G, H, J, K, L). Chủ dự án thêm: không nhúng trình duyệt chạy Flow, không làm đường Flow tay; Cloudflare tự tạo ảnh; prompt ảnh rất chi tiết từng thành phần. 6 câu mục 8: chọn cả 6 khuyến nghị A (alt ảnh thật không gửi ảnh; dòng quá hạn viết trước, hẹn ngày mai; 5 bài chờ duyệt thì khóa nút; Ghi SEO bật sẵn — Lá Chắn xét; dùng Tiêu đề dự kiến khi hợp lệ; đo hạn mức Gemini trước rồi quyết).

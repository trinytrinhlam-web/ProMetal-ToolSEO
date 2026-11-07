# T-129 · Lá Chắn rà soát đóng Giai đoạn 4 (tối ưu on-page)

| Mục | Nội dung |
|---|---|
| Giao cho | Lá Chắn (`la-chan`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-05 |
| Giai đoạn | Giai đoạn 4 |
| Mức ưu tiên | Trung bình (cần trước bản 1.0) |
| Phụ thuộc | Các phiếu Giai đoạn 4 đã gộp `main`; T-116 (kiểm lại bằng Fable) xong |
| Trạng thái | Xong (2026-11-07; Giai đoạn 4 đóng có điều kiện) |

## Mục tiêu

Kết luận Giai đoạn 4 (meta, schema JSON-LD, liên kết nội bộ, ghi SEO vào nháp qua SiteSEO, bước 4 «SEO» của Soạn bài) đóng được hay còn gì, giống T-093 đã làm cho Giai đoạn 3.

## Việc

1. Đối chiếu Lộ trình Giai đoạn 4 trong `CLAUDE.md` và thiết kế T-033 với `main` hiện tại: hạng mục nào đã có, hạng mục nào còn thiếu hay đổi theo quyết định chủ dự án (FAQ giữ như hiện tại, 04/11; không xuất Article/Breadcrumb/LocalBusiness vì site đã tự có).
2. Gom mọi điều kiện Lá Chắn còn mở của các phiếu Giai đoạn 4 (T-036 → T-042, T-059, T-091, T-095, T-106 và các phiếu dọn sau): cái nào đã đóng ở phiếu sau, cái nào còn mở, cái nào nên ghi sổ rủi ro. Dùng biên bản T-116 nhóm 2, 5 (đã kiểm lại bằng Fable) làm nền, không kiểm lại từ đầu.
3. Rủi ro còn lại khi người dùng thật dùng bước SEO: chữ SEO ghi lên website, link nội bộ, schema hiện trong app.
4. Kết luận: **đóng được** / **đóng có điều kiện** (liệt kê) / **chưa đóng**; đề xuất phiếu nếu cần.

## Phạm vi

- Chỉ đọc mã, tài liệu, chạy test liên quan. Không sửa code. Không gọi website thật.

## Tiêu chí xong

- [ ] Biên bản `docs/team/reports/T-129-la-chan.md` có «Tóm tắt (cho chủ dự án)» lời thường
- [ ] `detect-secrets` (`PYTHONUTF8=1`) sạch

## Ghi chú của Chỉ Huy

- Lập 2026-11-05 khi chủ dự án hỏi «khi nào đóng gói phần mềm»: đóng Giai đoạn 4 là một bước trước bản 1.0. Chạy Opus 5.5 (Fable để dành cho phiếu nhạy cảm Giai đoạn 6), ghi rõ model.
- 2026-11-07 07:52 (Chỉ Huy B): biên bản `50005d7`: ĐÓNG CÓ ĐIỀU KIỆN. Lập T-131 (Phiếu A), T-132 (Phiếu B). Đánh dấu Giai đoạn 4 xong khi T-131, T-132 gộp và tài liệu cập nhật.

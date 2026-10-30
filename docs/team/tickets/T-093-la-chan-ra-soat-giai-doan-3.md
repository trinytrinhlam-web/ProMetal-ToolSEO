# T-093 · Lá Chắn rà soát toàn bộ Giai đoạn 3 (ảnh) trước khi đóng giai đoạn

| Mục | Nội dung |
|---|---|
| Giao cho | Lá Chắn (`la-chan`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-27 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-082, T-083, T-084 đã gộp |
| Trạng thái | Lá Chắn xong; chờ T-107, T-110, T-078 phần còn lại |

## Mục tiêu

Một biên bản rà soát cả Giai đoạn 3 trên `main` (không chỉ từng phiếu): đọc thư mục ảnh, xử lý ảnh, thẻ ảnh, alt AI, chọn ảnh trên Soạn bài, gửi nháp kèm ảnh, trạng thái gửi; tìm lỗ hổng ở chỗ các phiếu nối với nhau, xác nhận sổ rủi ro (`docs/team/security.md` mục 6) còn đúng, liệt kê điều kiện còn mở.

## Bối cảnh

- Các biên bản Lá Chắn từ T-047 tới T-089 trong `docs/team/reports/`; sổ rủi ro `docs/team/security.md` mục 6.
- Thử thật T-059 (27/10): ảnh lên site giữ GPS, WordPress tự thêm `srcset` (bản thu nhỏ mất GPS; ảnh trong bài sửa ở T-059 bước 7, ảnh đại diện của theme chủ dự án chấp nhận).

## Phạm vi

- Chỉ đọc code, chạy test, viết test `xfail(strict=True)` trong `tests/test_la_chan_t093.py` khi có lỗi (mã LC-T093-n). Không sửa code ứng dụng. Không gọi website thật.

## Yêu cầu

1. Danh sách điều kiện Lá Chắn còn mở của Giai đoạn 3: đóng hay chưa, phiếu nào giữ.
2. Rà chéo các chỗ nối: đường ảnh từ thư mục → xử lý → AI alt → nháp → WordPress (F1, F2, A3, W2, W3, U1, U2).
3. Sổ rủi ro mục 6 còn đúng không; đề xuất dòng mới nếu có (chủ dự án quyết ghi sổ).
4. Kết luận giai đoạn: đóng được không, cần gì trước.

## Tiêu chí xong

- [ ] Yêu cầu 1–4
- [ ] Biên bản `docs/team/reports/T-093-la-chan.md` (ghi «chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11»)

## Ghi chú của Chỉ Huy

- Lập 2026-10-27 theo chỉ đạo «cứ làm liên tục, không cần hỏi»; việc đã có trong kế hoạch («Lá Chắn rà cả Giai đoạn 3»).
- 2026-10-29 01:50 (Chỉ Huy B): T-082, T-083 đã gộp. Nhánh `team/T-093` từ `main` `209615a`, worktree `wt-T-093`; giao Lá Chắn (phiên Lá Chắn T-056). Máy dừng khoảng 02:00 ngày 29/10; 30/10 07:35 cho làm tiếp.
- 2026-10-30 11:00 (Chỉ Huy B): Lá Chắn xong (`c51fe4f`): **chưa đóng được Giai đoạn 3**. Làm theo đề xuất: LC-T093-3 (Cao) → T-107 (Thợ Máy, làm ngay); LC-T093-1 (Trung bình) → T-108 (Họa Sĩ, cùng nhánh T-106); LC-T093-2, N1 → N5, câu sổ rủi ro dòng `unfiltered_html`, các việc hoãn mang sang: chủ dự án quyết (`TIEN-DO.md` mục 4); T-078 phần còn lại giao khi máy rảnh. Biên bản, test `xfail` của T-093 vào `main` qua nhánh T-107, T-106.
- 2026-10-30 12:52 (Chỉ Huy B): biên bản, test của T-093 vào `main` cùng T-106. LC-T093-1 đóng. Còn: T-107 (LC-T093-3), quyết định của chủ dự án, T-078 phần còn lại.
- 2026-10-30 17:23 (Chỉ Huy B): chủ dự án trả lời 30/10 13:50: 1A (gắn ảnh vào bài nháp → T-110), 2 đồng ý (N1, N2, N3, N5 ghi sổ rủi ro), 3 đồng ý (sửa câu dòng `unfiltered_html`), 4 đồng ý (nâng pillow-heif khi có bản vá), 5 OK (mang sang việc hoãn). Đã ghi `docs/team/security.md` mục 6, CLAUDE.md «Quyết định đã chốt».

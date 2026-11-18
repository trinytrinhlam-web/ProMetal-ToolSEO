# T-139 · Lá Chắn đọc kết quả buổi thử thật Google (T-133), cho dùng trang 📈 Theo dõi

| Mục | Nội dung |
|---|---|
| Giao cho | Lá Chắn (`la-chan`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-18 |
| Giai đoạn | Giai đoạn 6 (điều kiện còn lại: buổi thử thật Google) |
| Mức ưu tiên | Trung bình (cần trước bản 1.0) |
| Phụ thuộc | Buổi thử 18/11 xong; báo cáo `docs/team/reports/T-139-thu-that-google.md` |
| Trạng thái | Chờ Lá Chắn |

## Mục tiêu

Theo kịch bản T-133 mục 8: Lá Chắn đọc bảng mục 7 của buổi thử, kết luận có cho dùng trang 📈 Theo dõi không (Lá Chắn T-121 B4), và xem lại Giai đoạn 6 (T-120 mục 6 «Đi kèm», biên bản T-135).

## Việc

1. Đọc `docs/team/reports/T-139-thu-that-google.md`. Xét từng dòng «Chưa làm», «Không gặp», ghi nhận nhỏ:
   - CTR «−0,6 điểm» trong khi số suy ra là −0,51 (làm tròn hai lần?);
   - «0,8% ngoài website» ở ca 2 so với ~1,5% đếm từ bảng Trang (khoảng ngày, cách đếm?);
   - bảng đề xuất không có cột «Nguồn» như kịch bản ghi;
   - không ⚠️ khi từ khóa gần trùng ý một bài đã đăng (so trùng theo từ khóa/slug).
2. Kết luận: **cho dùng** / **cho dùng có điều kiện** / **chưa cho dùng**; đề xuất phiếu nếu cần (Thợ Máy, Thư Ký: kịch bản, README mục 15).
3. Cập nhật điều kiện Giai đoạn 6 trong biên bản (đóng hẳn hay còn gì).

## Phạm vi

- Chỉ đọc, chạy test liên quan **trong worktree**, không trong thư mục app của chủ dự án. Không gọi Google thật (buổi thử đã gọi).

## Tiêu chí xong

- [ ] Biên bản `docs/team/reports/T-139-la-chan.md` có «Tóm tắt (cho chủ dự án)», ghi rõ model; `detect-secrets` (`PYTHONUTF8=1`) sạch

## Ghi chú của Chỉ Huy

- Lập 2026-11-18 sau buổi thử (11:09–13:25). Giao sau khi Lá Chắn xong T-137 (cùng phiên, Fable).

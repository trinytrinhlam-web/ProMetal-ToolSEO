# T-112 · Chuẩn bị bật Hẹn giờ / Đăng ngay: sửa SL-T102-1, LC-T102-1, nút công tắc trong Cài đặt

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`); Thư Ký (README) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-31 |
| Giai đoạn | Giai đoạn 5 |
| Mức ưu tiên | Trung bình (bắt buộc trước khi bật công tắc) |
| Phụ thuộc | T-102 đã gộp `main` |
| Trạng thái | Đang làm (chờ T-115) |

## Mục tiêu

Đủ mọi điều kiện Lá Chắn đặt ra để **có thể** bật Hẹn giờ / Đăng ngay sau lần thử thật với chủ dự án (LC-T094-44). Phiếu này **không** bật công tắc: mặc định vẫn tắt.

## Bối cảnh

- Lá Chắn đầy đủ T-102 (`docs/team/reports/T-102-la-chan.md`): ĐẠT CÓ ĐIỀU KIỆN, gộp được khi công tắc tắt. Trước khi bật (bắt buộc): (1) sửa chung SL-T102-1 và LC-T102-1; (2) nút công tắc trong Cài đặt (LC-T094-41), Lá Chắn xét cách lưu; (3) thử thật LC-T094-44 với chủ dự án; (4) Lá Chắn rà soát lại Giai đoạn 5.
- **SL-T102-1 (Trung bình):** Đăng ngay + bật «Ghi SEO lên website» mà lệnh ghi SEO lỗi (500, không ghi được, SiteSEO chưa cho) thì bài vẫn đăng với SEO mặc định (trái LC-T094-39).
- **LC-T102-1 (Thấp):** Đăng ngay mà đặt ảnh đại diện trả 500 thì bài vẫn đăng, thiếu ảnh đại diện.
- Nên làm cùng lúc (Lá Chắn T-102): so `modified_gmt` trước lệnh chuyển (LC-T094-23); lệnh chuyển không rõ kết quả thì không ghi trạng thái vào dòng kế hoạch (G1); ô «Tạo thêm một bài nháp mới» khi đang chọn Đăng ngay phải nói rõ sẽ đăng bài mới; README phần Hẹn giờ và Đăng ngay.

## Phạm vi

- **Được sửa (Họa Sĩ):** `app/views/write.py` (bước Xuất bản), `app/views/settings.py` (nút công tắc), test.
- **Được sửa (Thư Ký):** `README.md` (Hẹn giờ, Đăng ngay, nút công tắc; ghi rõ mặc định tắt).
- **Không được sửa:** `seo_app/wordpress/**` (cần đổi client thì hỏi Chỉ Huy, giao Thợ Máy), `config/**` trừ khi Lá Chắn chọn lưu công tắc ở đó.

## Yêu cầu

1. Một luật chung: **Đăng ngay** chỉ gửi `release_draft` khi ảnh đại diện (nếu có) và SEO (nếu bật ghi) đã lên website thành công; hỏng thì bài giữ là nháp, câu báo cố định nói rõ phần nào chưa lên. **Hẹn giờ**: cảnh báo rõ, người dùng quyết (ghi lý do chọn trong báo cáo). 3 ca `xfail` SL-T102-1 và ca LC-T102-1 phải XPASS rồi gỡ dấu.
2. Nút công tắc Hẹn giờ/Đăng ngay trong Cài đặt: mặc định tắt; cách lưu (`.env`, `config/`, kho trên máy…) đề xuất trong báo cáo và **chờ Lá Chắn duyệt trước khi làm** (hỏi Chỉ Huy); không đặt được qua tham số địa chỉ, file nháp, ô nhập khác; bật/tắt có câu giải thích.
3. So `modified_gmt` ngay trước lệnh chuyển (LC-T094-23): bài trên website đổi sau lần xác nhận thì không chuyển.
4. Lệnh chuyển không rõ kết quả: không ghi trạng thái vào dòng kế hoạch (G1 Lá Chắn T-102).
5. Nhãn ô «Tạo thêm một bài nháp mới» đúng nghĩa khi đang chọn Đăng ngay / Hẹn giờ.
6. Không lùi T-099, T-102, T-110, «Gửi nháp», khóa gửi trùng; R5 như thường lệ.

## Yêu cầu bảo mật riêng

LC-T094-23, -39, -41, -44; điều kiện trong `docs/team/reports/T-102-la-chan.md`.

## Tiêu chí xong

- [ ] Yêu cầu 1–6
- [ ] Test liên quan + `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-112-hoa-si.md`, `T-112-thu-ky.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Đầy đủ.

## Ghi chú của Chỉ Huy

- Lập 2026-10-31 theo biên bản Lá Chắn đầy đủ T-102. Sau phiếu này: thử thật LC-T094-44 với chủ dự án (cần chủ dự án đồng ý và có mặt), rồi Lá Chắn rà soát Giai đoạn 5.
- 2026-10-31 13:32 (Chỉ Huy B): giao Họa Sĩ 09:40 (nhánh từ `d6df633`). Chỉ Huy chọn **A** cho công tắc: chỉ trong phiên (`st.session_state`), tick «Tôi hiểu…», tắt khi tải lại/tắt app, không ghi file; Lá Chắn đầy đủ T-112 xác nhận. Yêu cầu 3 (`modified_gmt`) tách sang T-115. Họa Sĩ xong (`f598cef`: Đăng ngay chỉ khi ảnh đại diện và SEO đã lên; Hẹn giờ cảnh báo; tab «📅 Hẹn giờ, đăng»; G1; nhãn gửi lại), Thư Ký README mục 11 (`245e199`).

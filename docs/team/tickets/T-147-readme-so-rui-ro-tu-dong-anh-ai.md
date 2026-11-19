# T-147 · README, sổ rủi ro: chế độ tự động, ảnh AI Cloudflare (phiếu F)

| Mục | Nội dung |
|---|---|
| Giao cho | Thư Ký (`thu-ky`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-19 |
| Giai đoạn | Chế độ tự động (thiết kế T-141) và ảnh AI (thiết kế T-140) |
| Mức ưu tiên | Trung bình (bắt buộc trước khi dùng với bài thật) |
| Phụ thuộc | **Đợt 5**, cùng lúc T-150, T-152: viết theo giao diện thật (tên nút, câu báo) của T-146, T-150, T-152 |
| Trạng thái | Mới |

## Mục tiêu

Chủ dự án đọc README là:

- tự tạo được tài khoản và token Cloudflare tối thiểu;
- dùng được chế độ tự động, «Viết các bài tới hạn»;
- hiểu dấu vàng, ô duyệt chung, giới hạn hạn mức.

Sổ rủi ro ghi đủ các rủi ro mới của hai thiết kế.

## Bối cảnh

- Thiết kế T-140: 2.5 (biến `.env`, token tối thiểu), mục 5 (bảo mật), mục 6 phiếu F.
- Thiết kế T-141: 1.11 (vì sao không chạy Flow trong app), mục 2 (chạy lâu, dừng, chạy tiếp), mục 3 (màn hình duyệt cuối, dấu vàng, ô duyệt chung), mục 4 (bài tới hạn), mục 6 (hạn mức), câu trả lời của chủ dự án (mục 8, cả 6 câu chọn A).
- Biên bản Lá Chắn T-140 (`fb9d2ef`): LC-T140-16. Biên bản Lá Chắn T-141 (`03568dc`): LC-T141-17, -22.

## Yêu cầu

1. **README, Cloudflare** (LC-T140-16 a–d):
   - tạo **token người dùng** (My Profile → API Tokens), phạm vi Account, một tài khoản, chỉ quyền **Workers AI Read**; lần gọi thử báo 403 mới thêm «Workers AI Edit» (trên trang có chỗ ghi «Write»);
   - không quyền nào khác; đặt ngày hết hạn (1 năm); token chỉ hiện một lần; dán mã tài khoản, token vào `.env`;
   - **giữ gói Workers Free, không gắn thẻ**: quá hạn mức chỉ bị từ chối. Nâng gói là tính tiền, và bộ đếm của app chỉ là lời khuyên;
   - dữ liệu gửi đi và chính sách của Cloudflare, có nguồn và ngày đọc; app không dùng AI Gateway;
   - FLUX.1 [schnell]: giấy phép Apache 2.0, dùng thương mại được; ảnh AI luôn ghi nhãn (đúng điều khoản hãng mô hình); điều 1.2(e) của điều khoản bfl.ai không áp khi dùng qua Cloudflare.
2. **README, chế độ tự động** (LC-T141-22, LC-T141-17):
   - **Chạy:** cách bấm «Soạn tự động»; giữ cửa sổ app mở, tắt chế độ ngủ của máy khi chạy lô; không tắt app giữa lúc đang gọi AI; tắt app thì lượt chạy dừng, mở lại bấm «Chạy tiếp».
   - **Hạn mức Gemini:** xem trong AI Studio; đặt lại lúc nửa đêm giờ Thái Bình Dương, khoảng 15:00 giờ Việt Nam mùa đông.
   - **Duyệt:** cách đọc dấu vàng; **ô duyệt chung bắt buộc cả khi gửi Nháp**.
   - **«Ghi SEO lên website»:** bật sẵn chỉ cho bài tự động, tắt được ở bước cuối; bài soạn tay vẫn tắt như cũ.
   - **«Viết các bài tới hạn»:** dòng có ngày trong 7 ngày tới, cả dòng quá hạn; tối đa 5 bài mỗi lần; không bao giờ quá 5 bài chờ duyệt.
   - **Vì sao app không chạy Flow** (T-141 1.11).
3. **`docs/team/security.md` §6, sổ rủi ro:**
   - (LC-T141-22) luồng nền chạy trong tiến trình app;
   - (LC-T141-22) chữ Google Sheet vào AI không qua duyệt dàn ý; chốt là mã kiểm và duyệt cả bài;
   - (LC-T141-22) ảnh tự chọn chỉ được người nhìn ở bước cuối, qua ô duyệt chung;
   - (LC-T141-22) «Ghi SEO» bật sẵn cho bài tự động;
   - (LC-T140-16 e) hạn mức ngày của Cloudflare chung cho hai máy, bộ đếm mỗi máy riêng; prompt mang chữ của bài tới Cloudflare (không dữ liệu khách); ảnh có thể có chữ lạ nếu lọt bộ kiểm, người dùng duyệt trước khi gửi.
4. **Cách viết:** lời thường, tiếng Việt; không bí mật, không đường dẫn đầy đủ trên máy, không mã tài khoản thật. Tên nút, câu báo đúng như giao diện đã gộp.
5. **Kiểm:** chạy các test có đọc README (test đọc `README.md` của T-087, T-095, T-126, T-138, nếu có).

## Phạm vi

- **Được sửa:** `README.md`, `docs/team/security.md` (§6).
- **Không được sửa:** mã, cấu hình, test.
- **Ngoài phạm vi:** `.env.example` (T-142 đã viết chú thích).

## Yêu cầu bảo mật riêng (điều kiện Lá Chắn)

S1, S3 (tài liệu biến `.env` có chú thích, không giá trị thật).

- **LC-T140-16** (a–e như yêu cầu 1, 3).
- **LC-T141-17** (README ghi «Ghi SEO» bật sẵn chỉ cho bài tự động, tắt được).
- **LC-T141-22** (4 dòng sổ rủi ro; README: giữ app mở, tắt chế độ ngủ, không tắt app giữa lần gọi, hạn mức xem trong AI Studio, cách đọc dấu vàng, ô duyệt chung bắt buộc cả Nháp, vì sao không chạy Flow).

## Tiêu chí xong

- [ ] Yêu cầu 1–5.
- [ ] Test có đọc README qua.
- [ ] Báo cáo `docs/team/reports/T-147-thu-ky.md`.

## Kiểm thử và kiểm định

- Soi Lỗi: Không (tài liệu); chạy test có đọc README.
- Lá Chắn: rút gọn.

## Lưu ý chung

- Chỉ chạy test trong worktree của phiếu (`D:/ProMetal-ToolSEO/wt-T-147`), **không** chạy trong `D:/ProMetal-ToolSEO/ProMetal-ToolSEO`.
- Không chạy toàn bộ `uv run pytest`.
- Không đọc `.env`, không chép khóa hay mã tài khoản thật; `detect-secrets` (`PYTHONUTF8=1`, bản sao có file mồi) sạch. Ví dụ dạng `tên:mật-khẩu@` hay tên khóa trong dấu backtick dễ bị báo nhầm: viết bằng lời.

## Ghi chú của Chỉ Huy

- Lập 2026-11-19 từ thiết kế T-140/T-141 (phiếu F, mục 7 của `docs/team/reports/T-141-tho-may.md`; biên bản Lá Chắn `fb9d2ef`, `03568dc`). Worktree `wt-T-147`, nhánh `team/T-147`.

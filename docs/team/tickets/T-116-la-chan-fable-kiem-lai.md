# T-116 · Lá Chắn kiểm lại bằng Fable các phần nhạy cảm (thay cho các lần kiểm tạm bằng Opus từ 15/10)

| Mục | Nội dung |
|---|---|
| Giao cho | Lá Chắn (`la-chan`), chạy Fable 5.1 |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-02 |
| Giai đoạn | Chung (bảo mật) |
| Mức ưu tiên | Cao |
| Phụ thuộc | Chủ dự án chọn 02/11: «Phần nhạy cảm trước» |
| Trạng thái | Xong (2026-11-04, 5 nhóm) |

## Mục tiêu

Từ 2026-10-15 Fable 5.1 bị giới hạn tới 01/11, nên mọi biên bản Lá Chắn chạy tạm bằng Opus 5.5 (chủ dự án duyệt; ghi ở `docs/team/board.md` mục «Đang làm»). Nay kiểm lại bằng Fable, theo nhóm, ưu tiên chỗ rủi ro cao. Phần còn lại làm sau nếu còn hạn mức.

## Các nhóm (làm lần lượt, mỗi nhóm một biên bản)

1. **Đọc ảnh từ thư mục, xử lý ảnh, HEIC:** `seo_app/images/**` (T-048, T-049, T-052, T-055, T-066, T-067, T-070, T-074, T-076, T-077, T-079, T-080, T-082, T-107; nay thêm T-078 bỏ AVIF). Rủi ro: đọc ngoài thư mục, tráo thư mục, symlink/junction, file ảnh dựng cố ý, GPS/EXIF lộ khi gửi AI, libheif.
2. **Client WordPress và đăng bài:** `seo_app/wordpress/**`, `seo_app/publish/**`, `app/views/write.py` phần gửi (T-054, T-060, T-061, T-071, T-085, T-086, T-088, T-089, T-091, T-096, T-099, T-102, T-106, T-108, T-110, T-112, T-115). Rủi ro: đăng ngoài ý người dùng, shortcode/HTML chạy được, ghi vào bài/ảnh không phải của app, lộ `WORDPRESS_URL`/mật khẩu ứng dụng.
3. **Đăng nhập, `.env`, bí mật, lớp AI:** `seo_app/auth.py`, `seo_app/config.py`, `seo_app/env_file.py`, `scripts/`, `seo_app/ai/**` (T-013 → T-034, T-090, T-104, T-105). Rủi ro: lộ khóa, mã băm, `*_CUSTOM_HEADERS`, lời dặn AI bị chèn lệnh.
4. **Google Sheets, kế hoạch:** `seo_app/google/**`, `seo_app/plan/**`, `app/views/plan.py`, `home.py` (T-097, T-098, T-100, T-101, T-103, T-109, T-113). Rủi ro: file khóa tài khoản dịch vụ, ghi Sheet sai chỗ, công thức, dữ liệu chưa tin cậy vào lời dặn AI.

## Cách làm

- Làm trên `main` mới nhất đã đẩy GitHub, trong worktree `wt-T-116` (nhánh `team/T-116`, chỉ chứa biên bản + test `xfail` mới).
- Mỗi nhóm: đọc biên bản Opus cũ, kiểm lại độc lập, thử khai thác; ghi rõ cái nào **giữ**, cái nào **khác Opus** (lỗi mới, đổi mức).
- Lỗi mới có test `xfail(strict=True)`; Nghiêm trọng/Cao báo Chỉ Huy ngay, không chờ hết nhóm.
- Không sửa code ứng dụng.

## Tiêu chí xong

- [ ] Biên bản `docs/team/reports/T-116-la-chan-nhom-<n>.md` cho từng nhóm đã làm
- [ ] Danh sách lỗi mới kèm mức, đề xuất phiếu sửa

## Ghi chú của Chỉ Huy

- Lập 2026-11-02 theo quyết định của chủ dự án («Phần nhạy cảm trước»). Bắt đầu nhóm 1 vì không có phiếu nào đang sửa phần ảnh; nhóm 2, 4 làm sau khi T-110, T-112, T-113, T-115 gộp.
- 2026-11-02 12:44 (Chỉ Huy B): `start_session` không chọn được Fable (rơi về Opus) → dừng, `set_session_model` Fable, chủ dự án tự chuyển trong menu model 08:05; lượt Opus 07:41–08:05 bỏ. Nhóm 1 xong (`3669046`, Fable 5.1): ĐẠT CÓ ĐIỀU KIỆN, 14 biên bản Opus không sai, 1 đổi mức (T-049 N2 → LC-T116-1 Thấp) → T-117 (Chỉ Huy chọn phiếu dọn, không ghi sổ rủi ro). Ghi nhận quy trình: `uvx pip-audit -r` hỏng vì xung đột `pillow<13` ↔ 13.0.0 ép có chủ đích → chạy `uv export` rồi `uvx pip-audit -r … --no-deps --disable-pip` (Thư Ký ghi vào `security.md` §5). Giao nhóm 3.
- 2026-11-02 17:23 (Chỉ Huy B): nhóm 3 xong (`c73fc21`, Fable 5.1): ĐẠT CÓ ĐIỀU KIỆN, 0 lỗi mới, 20 biên bản Opus (42 phát hiện) không sai; LC-T090-1 lẽ ra Trung bình (đã đóng ở T-104). Điều kiện hành chính: Thấp cũ lớp AI (LC-T034-1..3) → T-118; hai đề nghị «ghi sổ» (T-016-020 #5 `parse_stream`, T-022-024 #3) → Thư Ký `security.md` §6; `client.showErrorDetails` → chủ dự án chọn 02/11 «chỉ hiện loại lỗi» (T-118). Giao nhóm 4.
- 2026-11-03 12:33 (Chỉ Huy B): nhóm 4 xong (`5fe5c4d`): ĐẠT CÓ ĐIỀU KIỆN, 0 lỗi mới, 13 biên bản Opus không sai; LC-T113-2 → T-118. Biên bản nhóm 1, 3, 4 đã gộp `main` (`33dd87f`). Nhóm 2 (WordPress, đăng bài) giao cùng Lá Chắn đầy đủ T-112 (nhánh T-112 chứa T-102, T-110, T-115).
- 2026-11-03 23:10 (Chỉ Huy B): nhóm 2 xong cùng Lá Chắn đầy đủ T-112 (`7e8af87`, nhánh `team/T-112`): ĐẠT CÓ ĐIỀU KIỆN, 0 lỗi mới, Opus không sai. Giao **nhóm 5** (phần «còn lại»: `seo_app/content/**`, `seo_app/onpage/**`, `text.py`, `ui.py`, kho nháp ngoài `SendState`, `write.py` bước 1–4, `config/*.toml`, bộ chặn mạng của test). Biên bản gần xong (chưa thấy lỗi mới) thì hết hạn mức Fable tuần (18:15); chạy tiếp sau 04/11 10:00, không đổi model giữa biên bản.
- 2026-11-04 13:05 (Chỉ Huy B): nhóm 5 xong (`0989d36`): ĐẠT CÓ ĐIỀU KIỆN, 0 lỗi mới, 30 biên bản Opus (36 LC, 44 SL) giữ cả. Phần đọc mã, probe, bộ chặn mạng chạy Fable 03/11; phần đối chiếu, test, kết luận chạy **Opus 5.5** theo chủ dự án 04/11 08:20 («Sử dụng opus 5.5 đi»). Việc cũ còn mở (đã có chỗ theo dõi): SL-T045-1, -2 (T-057 hoãn), T-059 ĐK3 srcset (buổi thử thật), Mac (T-063, uv), T-053, schema FAQ lên website (T-041 ĐK3). Gộp `main`.

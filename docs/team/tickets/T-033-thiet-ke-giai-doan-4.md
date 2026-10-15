# T-033 · Thiết kế Giai đoạn 4 (tối ưu on-page): tìm hiểu SiteSEO, chia phiếu

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 4 (chuẩn bị) |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | Không. Phiếu này **không sửa code**, chỉ viết tài liệu thiết kế, nên chạy song song với T-019, T-032 được |
| Trạng thái | Đã giao |

## Mục tiêu

Trước khi viết code Giai đoạn 4, cần biết chắc ba điều:
1. Phần mềm ghi meta title, meta description, schema, canonical, robots vào **SiteSEO** bằng cách nào.
2. Cần làm gì phía website (việc cho chủ dự án).
3. Giai đoạn 4 chia thành những phiếu nhỏ nào, ai làm, theo thứ tự nào.

Kết quả là một tài liệu thiết kế để Chỉ Huy lập phiếu và hỏi chủ dự án đúng câu cần hỏi.

## Bối cảnh

- Lộ trình trong `CLAUDE.md`: "Giai đoạn 4 — Tối ưu on-page: meta, schema JSON-LD, liên kết nội bộ dựa trên danh sách bài trên WordPress."
- Chủ dự án chốt 2026-10-14: plugin SEO là **SiteSEO** (ghi meta/schema theo SiteSEO). Tên miền suachuacuasat.com. **Không có staging**: mọi thứ ghi lên site phải là nháp.
- Yêu cầu chi tiết của chủ dự án: `docs/plan/yeu_cau_phan_mem_ProMetal_ToolSEO.md`
  - M4: YC-401 → YC-406, có bảng schema theo loại trang;
  - M6: YC-601 → YC-604;
  - M7: các mục 6, 9, 10, 11;
  - mục 6: việc phía website.
  - File này viết trước khi chốt SiteSEO, nên còn nhắc Rank Math/Yoast và site staging; theo `docs/plan/README.md`, quyết định sau thắng.
- **Lệch cần lưu ý:** bảng schema ghi "Article (có tác giả)", nhưng chủ dự án chốt **không** dùng tên tác giả (`BAN-GIAO.md` 7.4). Đề xuất cách giải quyết, ví dụ `author` là tổ chức Pro-Metal.
- Đã có sẵn:
  - `seo_app/wordpress/client.py`: client REST, chỉ tạo `draft`;
  - `seo_app/content/`: quy trình viết, lời dặn có khung dữ liệu;
  - `seo_app/sanitize.py`: lọc HTML/link;
  - trang Soạn bài bước 4 "SEO" còn là **demo**. Xem `app/views/write.py` và dữ liệu mẫu `META_TITLES`, `META_DESCRIPTIONS`, `SLUG`, `INTERNAL_LINKS`, `SCHEMA` trong `seo_app/demo.py`. Bố cục này chủ dự án **đã duyệt**.
- Việc bắt buộc của Lá Chắn cho Giai đoạn 5 (cuối `docs/team/board.md`) liên quan tới link trong bài: thiết kế liên kết nội bộ phải tính tới.

## Phạm vi

- **Được làm:**
  - đọc code và tài liệu trong repo;
  - tìm hiểu SiteSEO qua mã nguồn công khai (wordpress.org, GitHub) và tài liệu chính thức;
  - xem trang **công khai** của suachuacuasat.com bằng GET **không đăng nhập**: mã HTML trang chủ, một bài viết, `/wp-json/` để biết namespace REST nào đang bật, schema SiteSEO đang xuất.
- **Không được làm:**
  - gọi REST có xác thực, ghi bất cứ thứ gì lên site;
  - đăng nhập;
  - dò quét nhiều trang (tối đa khoảng 10 lần GET, ghi rõ đã gọi URL nào);
  - sửa code, cấu hình hay test.
- **Được viết:** báo cáo `docs/team/reports/T-033-tho-may.md`, chứa toàn bộ thiết kế.

## Yêu cầu: nội dung báo cáo

1. **SiteSEO lưu dữ liệu ở đâu.** Tên khóa post meta cho meta title, meta description, canonical, robots (noindex/nofollow), từ khóa chính, dữ liệu schema (nếu có). Có ghi được qua REST API của WordPress không:
   - meta có đăng ký `show_in_rest` không;
   - SiteSEO có endpoint REST riêng không (namespace, quyền cần có).

   Dẫn nguồn: file và dòng trong mã nguồn SiteSEO, phiên bản.
2. **Nếu không ghi được qua REST:** các cách làm và đánh giá rủi ro. Ví dụ: mu-plugin nhỏ đăng ký meta với `show_in_rest` và `auth_callback` kiểm quyền `edit_post` (soạn sẵn mã mu-plugin trong báo cáo). Ghi rõ đây là việc chủ dự án phải tự cài lên site.
3. **Schema (YC-403, YC-404).**
   - SiteSEO đang tự xuất loại schema nào (đọc từ trang công khai)?
   - Đề xuất nguồn schema cho từng loại trang trong bảng YC-403 để không chồng nhau.
   - Cách đưa JSON-LD của phần mềm lên trang: qua trường của SiteSEO, hay chèn vào nội dung bài? Nêu ưu, nhược.
   - Cách kiểm hợp lệ trước khi đăng mà không gọi mạng: kiểm cấu trúc trong code, không dùng công cụ trực tuyến của Google.
4. **Liên kết nội bộ (YC-601 → YC-604).**
   - Lấy danh sách bài/trang đã đăng (chỉ `publish`) qua REST, có lưu tạm trong cache SQLite không;
   - cách AI gợi ý chỗ chèn và anchor;
   - chặn link tới bài nháp;
   - kiểm link hỏng mà không gọi mạng thật trong test;
   - link chèn vào phải đi qua `sanitize` thế nào để không phá các lớp bảo vệ đã có (T-004 → T-015).
5. **Meta (YC-401, YC-402).**
   - độ dài title và meta description theo ký tự tiếng Việt có dấu;
   - slug không dấu;
   - AI tạo meta theo lời dặn có khung dữ liệu (`security.md` 2.4);
   - kiểm trùng title/meta với bài khác trên site.
6. **Chia phiếu.** Danh sách phiếu đề xuất cho Giai đoạn 4, mỗi phiếu gồm:
   - mục tiêu;
   - agent làm (Thợ Máy, Họa Sĩ, Ngòi Bút);
   - file được sửa, sao cho không đụng nhau nếu chạy song song;
   - phụ thuộc;
   - yêu cầu bảo mật theo `security.md`.

   Phần chạy được mà không cần website (logic thuần + test giả) xếp trước. Phần cần chủ dự án làm trên site xếp sau.
7. **Câu hỏi cho chủ dự án.** Ví dụ: có cài được mu-plugin không; tài khoản Biên tập viên riêng; nguồn schema nào được ưu tiên. Mỗi câu viết sao cho người ít dùng kỹ thuật trả lời được (có lựa chọn kèm hệ quả). Không quá 5 câu, xếp theo mức cần thiết.
8. **Thư viện.** Nếu cần thư viện mới, nêu tên, lý do, phương án không cần thư viện. Không tự thêm (chủ dự án phải duyệt).

Viết tiếng Việt, ngắn gọn, có bảng. Thông tin nào **không chắc** (chưa tìm được nguồn) thì đánh dấu rõ "chưa xác minh".

## Yêu cầu bảo mật riêng

- Không in, không ghi vào báo cáo bất kỳ khóa, mật khẩu, Application Password nào.
- Chỉ GET công khai, không đăng nhập. Không ghi lên site.
- W1–W4 và mục 2.7 (`security.md`): thiết kế phải giữ "mặc định nháp", "không ghi đè dữ liệu đã có", "chỉ gọi đúng tên miền đã khai báo".

## Tiêu chí xong

- [ ] Báo cáo có đủ 8 mục trên, nguồn rõ ràng
- [ ] Không có thay đổi code, cấu hình hay test
- [ ] Đẩy báo cáo lên nhánh `team/T-033`

## Kiểm thử và kiểm định

- Soi Lỗi: Không (không có code).
- Lá Chắn: đọc thiết kế khi lập các phiếu code Giai đoạn 4 (mỗi phiếu code vẫn qua Lá Chắn như thường). Riêng mã mu-plugin soạn sẵn (nếu có) phải qua Lá Chắn trước khi đưa chủ dự án cài.

## Ghi chú của Chỉ Huy

- Làm trong phiên con **"Thợ Máy · T-033 Thiết kế Giai đoạn 4"**, trên nhánh tạm `team/T-033` (tạo từ `main`). Chỉ đẩy lên `team/T-033`.
- Chỉ Huy gộp báo cáo vào `main` sau khi đọc. Chưa lập phiếu code Giai đoạn 4 trước khi T-019 (việc cuối Giai đoạn 2) lên `main`.

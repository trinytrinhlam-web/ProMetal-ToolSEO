# Bảng việc

Chủ dự án xem file này để biết agent nào đang làm gì. Chỉ Huy cập nhật mỗi khi giao, nhận hoặc đóng phiếu.

_Cập nhật: 2026-10-21 09:07 (Chỉ Huy B)._

## Tiến độ dự án (cho chủ dự án)

**Cả dự án: khoảng 60% khối lượng việc** (ước tính theo số phiếu đã xong trong từng giai đoạn, cân theo độ lớn giai đoạn; giai đoạn 5, 6 chưa thiết kế nên con số còn đổi).

| Giai đoạn | Hoàn thành | Đã làm được gì |
|---|---|---|
| 0 · Bộ khung | **100%** | App mở bằng `run.bat`, đăng nhập bằng mật khẩu |
| 1 · Kết nối WordPress | **100%** | Kiểm tra kết nối, chuyên mục, thẻ, tạo bài nháp, tải ảnh |
| 2 · AI viết bài | **100%** | 3 hãng AI; ý định tìm kiếm, nghiên cứu, dàn ý, viết, tự rà soát; viết lại từng phần; kiểm tra văn phong; thử mù mô hình |
| 3 · Ảnh | **khoảng 75%** | Đọc thư mục ảnh an toàn, HEIC iPhone, xoay, 1600 px, WebP giữ GPS, AI gợi ý alt, thẻ ảnh từ tên thư mục (nhận ảnh AI theo tên: "minh họa", tên công cụ AI…), chèn ảnh vào nháp, nháp nhớ ảnh đã chọn (đang kiểm). Còn: **màn hình chọn ảnh** và các phiếu an toàn trước nó. Tạo ảnh AI: hoãn (chủ dự án chốt 20/10) |
| 4 · SEO trên trang | **khoảng 45%** | Meta title, mô tả, slug, schema FAQ, ghi SEO vào nháp qua SiteSEO. Còn: liên kết nội bộ, **màn hình bước SEO** |
| 5 · Kế hoạch, lịch, đăng bài | 0% | Chưa làm |
| 6 · Theo dõi thứ hạng Google | 0% | Chưa làm |

Trên app hôm nay chủ dự án dùng thật được phần **viết bài bằng AI** (Soạn bài bước 1–3, cần khóa API). Phần ảnh, SEO, gửi bài và kế hoạch đã có xử lý bên trong nhưng chưa có màn hình, nên vẫn hiện "Bản demo".

## Đang làm

> 2026-10-15: Fable 5.1 vẫn bị giới hạn tới 01/11, nên Lá Chắn chạy tạm bằng Opus 5.5 (chủ dự án đã duyệt). Sau 01/11 Lá Chắn kiểm lại bằng Fable: T-013 → T-021, T-018, T-022, T-023, T-024, T-019, T-025, T-026, T-027, T-028, T-029, T-030, T-031, T-032, T-034, T-035, T-038, T-043, T-036, T-037, T-044, T-045, T-046, T-047, T-042, T-048, T-058, T-051, T-050, T-049, T-062, T-052, T-067, T-054, T-068 (Chỉ Huy B bổ sung 20/10 các phiếu gộp từ 17/10).
>
> 2026-10-15 12:35: tài khoản của Chỉ Huy A gọi Fable 5.1 bị từ chối ("cần mua thêm lượt dùng"), nên Lá Chắn T-027 chạy lại bằng Opus 5.5.
>
> 2026-10-15: 4 phiên (Ngòi Bút · T-022, Soi Lỗi · T-018/T-023/T-024) dừng lúc 22:05 ngày 14/10 vì chạm giới hạn sử dụng của tài khoản; đã chạy lại theo đợt, tối đa 3 phiên cùng lúc.

> 2026-10-15 11:30: Chỉ Huy A (Claude Desktop trên máy chủ dự án) đã xóa các nhánh tạm gộp xong: `team/T-018`, `team/T-022`, `team/T-023`, `team/T-024`.

Mỗi agent chạy ở một **phiên con** dưới phiên Chỉ Huy đang giữ quyền (xem [dong-bo.md](dong-bo.md)), tên phiên = tên agent + số phiếu. Mỗi phiếu làm trên nhánh tạm `team/T-xxx`, gộp vào `main` khi Lá Chắn ĐẠT.

| Phiếu | Việc | Agent (tên phiên) | Nhánh | Trạng thái | Báo cáo |
|---|---|---|---|---|---|
| [T-055](tickets/T-055-nhap-luu-lua-chon-anh.md) | GĐ3 · G3-9: nháp lưu lựa chọn ảnh | Soi Lỗi · T-055 kiểm lại lượt 2 | `team/T-055` | 18:32 Soi Lỗi **ĐẠT CÓ ĐIỀU KIỆN** (2 Trung bình SL-T055-1, -2; 1 Thấp). 19:46 Thợ Máy lượt 2 **xong** (`2c95844`: sửa SL-T055-1 → -3, gỡ 7 `xfail`; test liên quan 936 qua). ⏳ **21/10 Soi Lỗi đang kiểm lại**; rồi Lá Chắn | [Thợ Máy](reports/T-055-tho-may.md) · [Soi Lỗi](reports/T-055-soi-loi.md) |
| [T-061](tickets/T-061-shortcode-trong-bai-ai.md) | Chặn shortcode WordPress trong chữ AI, meta SEO, alt và chú thích ảnh (LC-T042-3, LC-T054-1 Trung bình) | Lá Chắn · T-061 kiểm chặn shortcode | `team/T-061` | 19:06 Thợ Máy **xong** (`7c5a405`). 19:47 Soi Lỗi **ĐẠT CÓ ĐIỀU KIỆN** (`64525d3`; 45.000 chuỗi ngẫu nhiên không lọt; 7 file test cũ không bị làm yếu; 2 Thấp SL-T061-1 chữ SEO `[<>…]`, SL-T061-2 chữ có sẵn trong file ảnh tải tay). ⏳ **21/10 Lá Chắn đang kiểm** | [Thợ Máy](reports/T-061-tho-may.md) · [Soi Lỗi](reports/T-061-soi-loi.md) |
| [T-074](tickets/T-074-don-the-anh-luot-2.md) | Dọn thẻ ảnh lượt 2 (LC-T070-1, -2; SL-T070-2, -3, -5). **Phải gộp trước T-056** | Thợ Máy · T-074 dọn thẻ ảnh lượt 2 | `team/T-074` | ⏳ **21/10 Thợ Máy đang làm** (nhánh từ `main` sau khi gộp T-070) | |

## Chờ

| Phiếu | Việc | Agent | Chờ gì |
|---|---|---|---|
| [T-059](tickets/T-059-thu-that-ghi-seo-mot-bai-nhap.md) | Thử thật một bài nháp, ghi SEO lên site (có chủ dự án) | Chỉ Huy, Thợ Máy | T-042 gộp; chủ dự án bật Abilities, tạo tài khoản Biên tập viên |
| [T-060](tickets/T-060-don-loi-thap-client-wordpress.md) | Dọn lỗi Thấp client WordPress (LC-T042-1/4/5) | Thợ Máy | T-042 gộp; trước khi hết GĐ4 |
| [T-057](tickets/T-057-loc-ho-so-nhan-tieu-de-vat-dong.md) | Bộ lọc hồ sơ: nhãn tiêu đề vắt nhiều dòng (SL-T045-1/2, có từ trước) | Thợ Máy | **Hoãn** (chủ dự án chốt 20/10: rút gọn, lỗi nhỏ không chặn) |
| [T-063](tickets/T-063-chay-test-t048-tren-mac-linux.md) | Chạy test đọc thư mục ảnh trên Mac/Linux (LC-T048-1, Trung bình). **Chặn gộp T-056** | Soi Lỗi | Cần máy Linux/Mac: phiên Claude Code cloud |
| [T-064](tickets/T-064-don-loi-thap-doc-thu-muc-anh.md) | Dọn lỗi Thấp đọc thư mục ảnh (LC-T048-2/-3/-4c/-5, `os.fstat`) | Thợ Máy | **Hoãn** (chủ dự án chốt 20/10: lỗi nhỏ không chặn) |
| [T-065](tickets/T-065-quy-tac-alt-chu-trong-anh.md) | Quy tắc alt: chữ trong ảnh không chép vào alt lẫn chú thích (C10 của Lá Chắn T-051) | Ngòi Bút | Còn chỗ (T-051 đã gộp); trước khi gộp T-056 |
| [T-066](tickets/T-066-don-loi-thap-anh-gui-ai.md) | Dọn lỗi Thấp lớp ảnh gửi AI (LC-T050-1/-2/-3, SL-T050-5/-6): từ chối mọi hồ sơ màu, khối dựng cố ý | Thợ Máy | Còn chỗ (T-049, T-050 đã gộp); trước khi gộp T-056 |
| [T-069](tickets/T-069-readme-anh-gui-ai.md) | README: ảnh gửi hãng AI khi viết alt (LC-T050-4), cách đặt thư mục ảnh | Thư Ký | Còn chỗ (T-062 đã gộp); nên sau T-052; trước khi gộp T-056 |
| [T-071](tickets/T-071-don-loi-thap-chen-anh-nhap.md) | Dọn lỗi Thấp chèn ảnh vào nháp (LC-T054-2/-3/-5/-6, phần code LC-T054-4) | Thợ Máy | Còn chỗ (T-054, T-070 đã gộp); trước khi gộp T-056 |
| [T-072](tickets/T-072-gps-ref-phu-sai-khuon.md) | GPS: thẻ Ref phụ sai khuôn không làm mất vị trí (LC-T067-1) | Thợ Máy | **Hoãn** (chủ dự án chốt 20/10: ảnh Zalo mất GPS) |
| [T-073](tickets/T-073-on-dinh-test-khoa-cho-t037.md) | Ổn định test khóa chờ của kho danh sách bài (hỏng oan khi máy bận) | Soi Lỗi | Còn chỗ |
| [T-053](tickets/T-053-tao-anh-ai.md) | GĐ3 · G3-7: tạo ảnh AI (Gemini), đánh dấu ảnh AI | Thợ Máy | **Hoãn** (chủ dự án chốt 20/10: chưa cần tạo ảnh AI) |
| [T-056](tickets/T-056-giao-dien-cho-can-anh.md) | GĐ3 · G3-10: giao diện chỗ cần ảnh | Họa Sĩ | T-055, T-061, T-074, T-065, T-066, T-069, T-071; **T-063** (điều kiện Lá Chắn T-048) |
| _(ghi nhận, không lập phiếu)_ | Lá Chắn T-034: LC-T034-2 `os.environb`/`getenvb` không được lọc (thư viện hiện không dùng); LC-T034-3 vòng trỏ `os` nằm trước `try` (lệch về phía an toàn). LC-T034-1 gộp vào T-044 | — | Xem lại khi thư viện AI đổi phiên bản |
| [T-039](tickets/T-039-lien-ket-noi-bo.md) | GĐ4: liên kết nội bộ (ứng viên, AI gợi ý anchor, chèn link bằng code) | Thợ Máy | Hết chờ (T-036, T-037 đã gộp); chủ dự án chốt chuyển sớm sang GĐ4 |
| [T-040](tickets/T-040-loi-dan-meta-anchor.md) | GĐ4: lời dặn AI cho meta và anchor, mục `[meta]` trong `config/content.toml` | Ngòi Bút | T-036, T-039 |
| [T-041](tickets/T-041-buoc-seo-that.md) | GĐ4: bước 4 "SEO" của Soạn bài chạy thật | Thợ Máy → Họa Sĩ | T-036 → T-039 |
| _(chưa lập phiếu)_ | Ghim cùng một bản Python cho mọi máy (`.python-version` hiện là `3.12`: cloud chạy 3.12.3, Windows 3.12.15; độ lệch này gây 9 test đỏ ở T-030) | Thợ Máy | Soi Lỗi đề xuất ở T-029; lập phiếu sau khi T-029 + T-030 gộp |
| _(ghi nhận, không lập phiếu)_ | Bộ chặn mạng của test chỉ xét socket AF_INET/AF_INET6; họ khác (AF_UNIX…) không bị chặn nhưng không có đường vô tình ra mạng | — | Lá Chắn T-029 + T-030, lỗi Thấp #2 |

## Việc đang làm ngoài hệ thống phiếu

Các việc này bắt đầu trước khi có đội agent. Khi xong, Chỉ Huy lập phiếu kiểm định cho Lá Chắn.

| Việc | Ở đâu |
|---|---|
| _(không còn)_ | Hồ sơ doanh nghiệp (PR #3) đã gộp vào `main` 2026-10-14, kiểm định qua T-022 |

## Xong

| Phiếu | Việc | Agent | Ngày xong | Kết quả |
|---|---|---|---|---|
| [T-070](tickets/T-070-don-loi-the-anh.md) | Dọn lỗi thẻ ảnh: nhận ảnh AI theo tên ("minh họa", "trí tuệ nhân tạo", genai, Copilot, Designer…; `is_ai_name`), kho thẻ sửa tay kiểm cấu trúc trước khi đọc, `get_many` giữ ảnh AI | Thợ Máy | 2026-10-20 | [Thợ Máy](reports/T-070-tho-may.md) · [Soi Lỗi](reports/T-070-soi-loi.md) rút gọn: đạt có điều kiện (5 Thấp) · Lá Chắn rút gọn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-070-la-chan.md) (Opus tạm), 2 Thấp LC-T070-1, -2 → T-074 (trước T-056); điều kiện → T-056 (g), (h), T-069. Gộp vào `main` `588c76f`: Windows đang chạy toàn bộ test (21/10) |
| [T-054](tickets/T-054-chen-anh-vao-nhap-wordpress.md) | GĐ3 · G3-8: tải ảnh lên WordPress, chèn `<figure>` vào nháp (`seo_app/images/html.py`, gửi nháp kèm ảnh) | Thợ Máy | 2026-10-20 | [Thợ Máy](reports/T-054-tho-may.md) · [Soi Lỗi](reports/T-054-soi-loi.md): đạt có điều kiện · Lá Chắn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-054-la-chan.md) (Opus tạm): LC-T054-1 Trung bình → T-061; 5 Thấp → T-071. Thử 8 ảnh thật trên website (99 ảnh gốc, 0 ảnh còn GPS): xử lý tốt. Gộp vào `main` `43d6c4a` (cùng T-068): Windows 9.477 qua, 1 hỏng oan (`test_soi_loi_t037.py` khóa chờ → T-073) |
| [T-068](tickets/T-068-don-loi-thap-alt-anh-ai.md) | Dọn lỗi Thấp bước code tự sửa alt ảnh AI (SL-T062-1 → -3) | Thợ Máy | 2026-10-20 | [Thợ Máy](reports/T-068-tho-may.md) · [Soi Lỗi](reports/T-068-soi-loi.md) rút gọn: đạt (xác nhận test C6 chỉnh) · Lá Chắn rút gọn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-068-la-chan.md) (Opus tạm). Gộp vào `main` `4bc61b9` |
| [T-067](tickets/T-067-don-loi-thap-xu-ly-anh.md) | Dọn lỗi Thấp xử lý ảnh (LC-T049-1 GPS sai khuôn, LC-T049-2 cache xem trước kiểm Pillow, LC-T049-3 khóa luồng) | Thợ Máy | 2026-10-20 | [Thợ Máy](reports/T-067-tho-may.md) · [Soi Lỗi](reports/T-067-soi-loi.md) rút gọn: đạt có điều kiện · Lá Chắn rút gọn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-067-la-chan.md) (Opus tạm), LC-T067-1 → T-072. Gộp vào `main` `e5c0ce8`: Windows 8.974 qua, 1 hỏng vì máy bận (`test_link_escape.py` đo tốc độ; chạy riêng lại 3 lần, 119/119 qua) |
| [T-052](tickets/T-052-the-anh-theo-ten-thu-muc.md) | GĐ3 · G3-6: thẻ ảnh từ tên thư mục Drive (mã công trình, hạng mục, khu vực, trước/sau, nguồn thật/AI); thẻ sửa tay lưu SQLite trong `data/` (`tags.py`, `storage/image_tags.py`) | Thợ Máy | 2026-10-20 | [Thợ Máy](reports/T-052-tho-may.md) (2 lượt) · [Soi Lỗi](reports/T-052-soi-loi.md) (2 lượt): đạt có điều kiện · Lá Chắn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-052-la-chan.md) (Opus tạm), 1 Trung bình + 4 Thấp → T-070; điều kiện → T-055, T-056, T-063, T-069. Gộp vào `main` `1c7bd9a`: Windows 8.840 qua, 1 hỏng vì máy bận (`test_soi_loi_t037.py` khóa chờ; chạy riêng lại 3 lần, 139/139 qua; T-052 không đụng phần này) |
| [T-062](tickets/T-062-doc-cau-hinh-viec-anh.md) | Đọc cấu hình việc ảnh: provider lười (bật được `[tasks.image]` mà Soạn bài không đòi khóa Gemini), đọc `[images]`/`[alt]` chịu lỗi, nhãn, tiền tố ảnh AI do code bảo đảm | Thợ Máy | 2026-10-20 | [Thợ Máy](reports/T-062-tho-may.md) · [Soi Lỗi](reports/T-062-soi-loi.md): đạt có điều kiện (3 Thấp → T-068) · Lá Chắn rút gọn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-062-la-chan.md) (Opus tạm), C1–C6 đạt, LC-T062-1 → T-065; README → T-069. Gộp vào `main` `f96775a`: Windows 8.487 qua, 0 hỏng |
| [T-049](tickets/T-049-xu-ly-anh-webp-giu-gps.md) | GĐ3 · G3-3: xoay, cạnh dài 1600 px, WebP **giữ GPS** (danh sách thẻ 2A), bản gửi AI dựng lại từ điểm ảnh (không metadata, không hồ sơ màu), ảnh xem trước, tên file chuẩn SEO (`process.py`, `naming.py`) | Thợ Máy | 2026-10-20 | [Thợ Máy](reports/T-049-tho-may.md) · [Soi Lỗi](reports/T-049-soi-loi.md): đạt có điều kiện (3 Thấp) · Lá Chắn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-049-la-chan.md) (Opus tạm), 4 Thấp; điều kiện → T-053, T-054, T-056, T-062, `security.md` mục 5; dọn → T-067. Gộp vào `main` `3f90489`: Windows 8.278 qua, 0 hỏng. Chưa thử ảnh thật (trước khi gộp T-054) |
| [T-050](tickets/T-050-lop-ai-doc-anh-goi-y-alt.md) | GĐ3 · G3-4: lớp AI đọc ảnh (Claude, ChatGPT, Gemini), gợi ý alt; ảnh gửi AI qua bộ kiểm "danh sách cho phép" (không metadata), thẻ/từ khóa qua lớp lọc ký tự | Thợ Máy | 2026-10-20 | [Thợ Máy](reports/T-050-tho-may.md) (2 lượt) · [Soi Lỗi](reports/T-050-soi-loi.md) (2 lượt): đạt · Lá Chắn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-050-la-chan.md) (Opus tạm), 4 lỗi Thấp; điều kiện → T-049, T-052, T-054, T-056, T-062; dọn → T-066. Gộp vào `main` `c1aa0ce` (`seo_app/images/__init__.py` giữ bản T-048): Windows 8.009 qua, 0 hỏng |
| [T-051](tickets/T-051-prompt-alt-va-cau-hinh-anh.md) | GĐ3 · G3-5: quy tắc alt và 6 ví dụ (`[alt]`), `[images]` (WebP 80, 1600 px), `[tasks.alt]` Claude Sonnet, `[tasks.image]` Gemini (ghi sẵn, đang tắt chờ T-062) | Ngòi Bút | 2026-10-20 | [Ngòi Bút](reports/T-051-ngoi-but.md) · [Soi Lỗi](reports/T-051-soi-loi.md) rút gọn: đạt (36 test mới) · Lá Chắn rút gọn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-051-la-chan.md) (Opus tạm), 2 lỗi Thấp; điều kiện C1–C6 → T-062, C7–C9 → T-053, C10 → T-065. Gộp vào `main` `57fc6b9`: Windows 7.519 qua, 0 hỏng |
| [T-058](tickets/T-058-nang-pillow-13.md) | Nâng Pillow 13.0.0 bằng `override-dependencies` (vá 53 khuyến cáo của 12.3.0; Streamlit khai báo `pillow<13`) | Thợ Máy | 2026-10-20 | [Thợ Máy](reports/T-058-tho-may.md) · [Soi Lỗi](reports/T-058-soi-loi.md) rút gọn: đạt (60 test mới) · Lá Chắn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-058-la-chan.md) (Opus tạm), 4 lỗi Thấp; điều kiện ghi vào T-049, T-056. Chỉ Huy B và chủ dự án mở app thật xem mọi trang (Bài viết, Soạn bài 5 bước, Kế hoạch, Cài đặt 4 thẻ, Kết nối WordPress): không lỗi. Gộp vào `main` `0481f7e`: Windows 7.483 qua, 0 hỏng |
| [T-048](tickets/T-048-doc-thu-muc-anh-an-toan.md) | GĐ3 · G3-2: đọc thư mục ảnh an toàn (chặn `..`, symlink, junction) | Thợ Máy | 2026-10-20 | [Thợ Máy](reports/T-048-tho-may.md) (2 lượt) · [Soi Lỗi](reports/T-048-soi-loi.md) (2 lượt): đạt có điều kiện · Lá Chắn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-048-la-chan.md) (Opus tạm): LC-T048-1 Trung bình → T-063 (chặn gộp T-056); lỗi Thấp → T-064; điều kiện ghi vào T-049, T-052, T-055, T-056; LC-T048-6 chờ chủ dự án (sổ rủi ro). Gộp vào `main` `f37ffd6`: Windows 7.420 qua, 1 hỏng vì quá tải (`test_app.py` quá 30 giây khi 4 bộ test chạy cùng lúc; chạy riêng lại 5/5 qua). Lá Chắn chạy đúng bản gộp: 7.421 qua, 0 hỏng |
| [T-042](tickets/T-042-ghi-meta-seo-len-nhap.md) | Ghi meta SEO (SiteSEO) lên bài nháp (GĐ4) | Thợ Máy | 2026-10-20 | [Thợ Máy](reports/T-042-tho-may.md) (3 lượt) · [Soi Lỗi](reports/T-042-soi-loi.md) (2 lượt) · Lá Chắn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-042-la-chan.md) (Opus tạm); lỗi Thấp → T-060, T-061; giao diện → T-041; thử thật → T-059. Gộp vào `main` `81381c5`: Windows 7.170 qua, 0 hỏng |
| [T-047](tickets/T-047-khai-bao-pillow-va-pillow-heif.md) | Khai báo Pillow 12.3.0, pillow-heif 1.8.1 (GĐ3) | Thợ Máy | 2026-10-19 | [Thợ Máy](reports/T-047-tho-may.md) · [Soi Lỗi](reports/T-047-soi-loi.md) rút gọn: đạt · Lá Chắn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-047-la-chan.md) (Opus tạm): Pillow 12.3.0 có 53 khuyến cáo mới, vá ở 13 → T-058; điều kiện mở ảnh ghi vào T-049. Gộp vào `main` `d350aec`: Windows 5.810 qua, 0 hỏng |
| [T-045](tickets/T-045-loc-ho-so-theo-doi-sau-t043.md) | Bộ lọc hồ sơ: 3 lỗi Thấp sau T-043 | Thợ Máy | 2026-10-19 | [Thợ Máy](reports/T-045-tho-may.md) · [Soi Lỗi](reports/T-045-soi-loi.md): đạt (fuzz 300.000 tài liệu, 0 dòng có nhãn tới AI) · Lá Chắn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-045-la-chan.md) (Opus tạm); SL-T045-1/2 → T-057. Gộp vào `main` `cc3099f`: Windows 5.791 qua, 0 hỏng |
| [T-044](tickets/T-044-ten-site-tu-wordpress-hien-an-toan.md) | Chữ lấy từ WordPress và tên mô hình hiện an toàn | Họa Sĩ | 2026-10-19 | [Họa Sĩ](reports/T-044-hoa-si.md) (2 lượt) · [Soi Lỗi](reports/T-044-soi-loi.md) rút gọn: đạt có điều kiện (SL-T044-1/2 đã sửa) · Lá Chắn rút gọn: [**ĐẠT**](reports/T-044-la-chan.md) (Opus tạm); LC-T044-1 → T-042. Gộp vào `main` `cb9cd47`: Windows 5.624 qua, 0 hỏng |
| [T-037](tickets/T-037-danh-sach-bai-da-dang-cache.md) | Danh sách bài/trang đã đăng + cache SQLite (GĐ4) | Thợ Máy | 2026-10-17 | [Thợ Máy](reports/T-037-tho-may.md) (2 lượt) · [Soi Lỗi](reports/T-037-soi-loi.md): đạt lượt 2 · Lá Chắn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-037-la-chan.md) (Opus tạm); điều kiện ghi vào T-042 (SL-T037-3/4/5, LC-T037-1, danh sách đường gọi cố định) và T-039, T-041. Gộp vào `main` `914ac68`: Windows 5.537 qua, 0 hỏng |
| [T-036](tickets/T-036-meta-title-description-slug.md) | Meta title, description, slug (GĐ4, phần logic) | Thợ Máy | 2026-10-17 | [Thợ Máy](reports/T-036-tho-may.md) (2 lượt) · [Soi Lỗi](reports/T-036-soi-loi.md): đạt lượt 2 · Lá Chắn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-036-la-chan.md) (Opus tạm); điều kiện ghi vào T-041 (LC-T036-1, SL-T036-10/11/12) và T-042 (chặn thực thể HTML). Gộp vào `main` `f11ba28`: Windows 5.291 qua, 0 hỏng |
| [T-046](tickets/T-046-thiet-ke-giai-doan-3.md) | Thiết kế Giai đoạn 3 (ảnh), chỉ tài liệu | Thợ Máy | 2026-10-17 | [Thợ Máy](reports/T-046-tho-may.md): nén WebP kèm `exif=` giữ được GPS (đã thử); Pillow không đọc HEIC; 10 phiếu G3-1 → G3-10; 5 câu hỏi chủ dự án · Lá Chắn rút gọn: [**ĐẠT**](reports/T-046-la-chan.md) (Opus tạm), 11 góp ý cho phiếu code. Gộp vào `main` `de65bdb` |
| [T-038](tickets/T-038-schema-faqpage-kiem-hop-le.md) | GĐ4: dựng và kiểm schema FAQPage không cần mạng (`seo_app/onpage/schema.py`) | Thợ Máy | 2026-10-16 | [Thợ Máy](reports/T-038-tho-may.md) · [Soi Lỗi](reports/T-038-soi-loi.md): đạt có điều kiện · Lá Chắn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-038-la-chan.md) (Opus tạm): 3 điều kiện chuyển T-041. Gộp vào `main`: Linux 4.867 qua, 0 hỏng |
| [T-034](tickets/T-034-loi-thap-lop-ai-sau-t019.md) | 7 lỗi Thấp lớp AI và thử mù: che số phiên bản và biến thể, Claude bị cắt, `_OsWithoutIgnored` thay gỡ biến môi trường, `RLock`, gzip hỏng, tên mô hình lạ, đường dẫn trong câu lỗi | Thợ Máy | 2026-10-16 | [Thợ Máy](reports/T-034-tho-may.md) (2 lượt) · [Soi Lỗi](reports/T-034-soi-loi.md): đạt lượt 2 · Lá Chắn: [**ĐẠT**](reports/T-034-la-chan.md) (Opus tạm), 3 lỗi Thấp ghi sổ. Gộp vào `main` `49f57c9`: Linux 4.658 qua, 0 hỏng |
| [T-043](tickets/T-043-loc-ho-so-loi-thap-sau-t032.md) | Bộ lọc hồ sơ: nhãn có ký tự lạ chen vào, nửa nhãn qua dòng trống, tiêu đề thụt lề có nửa nhãn | Thợ Máy | 2026-10-16 | [Thợ Máy](reports/T-043-tho-may.md) · [Soi Lỗi](reports/T-043-soi-loi.md): đạt có điều kiện · Lá Chắn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-043-la-chan.md) (Opus tạm): gộp được ngay, mở phiếu theo dõi T-045. Gộp vào `main`: Linux 4.403 qua, 0 hỏng |
| [T-031](tickets/T-031-dia-chi-tran-thanh-link.md) | Địa chỉ trần, `www.`, email trong chữ AI và chữ ngoài không thành link (chèn ký tự rộng 0); sửa thêm `clean_flags` và lỗi có sẵn ở `markdown_link` | Thợ Máy | 2026-10-16 | [Thợ Máy](reports/T-031-tho-may.md) · [Soi Lỗi](reports/T-031-soi-loi.md): đạt · Lá Chắn: [**ĐẠT**](reports/T-031-la-chan.md) (Opus tạm; 48.977 ca, 0 link). Gộp vào `main`: Linux 4.301 qua, 0 hỏng. Cần chạy lại trên Windows |
| [T-035](tickets/T-035-readme-ai-3-hang-thu-mu.md) | README mục 7 và chú thích `config/ai.toml`: 3 hãng AI, thử mù, bảng lỗi | Thư Ký | 2026-10-16 | [Thư Ký](reports/T-035-thu-ky.md) · Chỉ Huy B soát câu lỗi: khớp code · Lá Chắn rút gọn: [**ĐẠT**](reports/T-035-la-chan.md) (Opus tạm). Gộp vào `main` `4a5480b` |
| [T-032](tickets/T-032-loc-ho-so-nhan-go-sai.md) | Bộ lọc hồ sơ nhận nhãn gõ sai (dính chữ, không dấu, ngoặc tròn, vắt dòng) và nhãn trên tiêu đề | Thợ Máy | 2026-10-16 | [Thợ Máy](reports/T-032-tho-may.md) (2 lượt) · [Soi Lỗi](reports/T-032-soi-loi.md): đạt lượt 2 · Lá Chắn: [**ĐẠT**](reports/T-032-la-chan.md) (Opus tạm), 3 lỗi Thấp → T-043. Gộp vào `main` `cbfe37a`: Linux 3.558 qua, 0 hỏng |
| [T-033](tickets/T-033-thiet-ke-giai-doan-4.md) | Thiết kế Giai đoạn 4: SiteSEO lưu meta ở đâu, ghi qua REST (Abilities / meta đã mở), schema site đang có, chia phiếu | Thợ Máy | 2026-10-15 | [Báo cáo](reports/T-033-tho-may.md) (chỉ tài liệu, 8 lần GET công khai). Gộp vào `main`. Lập T-036 → T-042; 4 câu hỏi chờ chủ dự án |
| [T-019](tickets/T-019-thu-mu-mo-hinh.md) | Thử mù mô hình AI trong Cài đặt (việc cuối của Giai đoạn 2) | Thợ Máy, Họa Sĩ | 2026-10-15 | [Thợ Máy](reports/T-019-tho-may.md) (2 lượt) · [Họa Sĩ](reports/T-019-hoa-si.md) · [Soi Lỗi](reports/T-019-soi-loi.md): đạt lượt 2 · Lá Chắn: [**ĐẠT**](reports/T-019-la-chan.md) (Opus tạm), 5 lỗi Thấp → T-034. Gộp vào `main` `7d8f6f3`: Linux 3.344 qua, 0 hỏng |
| [T-025](tickets/T-025-on-dinh-test-do-toc-do.md) | Ổn định các test đo tốc độ chập chờn | Soi Lỗi | 2026-10-15 | [Soi Lỗi](reports/T-025-soi-loi.md): 1.000 lần đo, trước sửa hỏng 25, sau sửa 0; ngưỡng 9 giữ nguyên · Lá Chắn rút gọn: [**ĐẠT**](reports/T-025-la-chan.md) (Opus tạm). Gộp vào `main` `39065cd`: Linux 3.133 qua, 0 hỏng. Nên chạy lại trên Windows (6 test đồng hồ kiểu Windows mới kiểm bằng đồng hồ giả) |
| [T-029](tickets/T-029-bo-chan-mang-udp-va-dns.md) + [T-030](tickets/T-030-test-t027-chay-tren-linux-mac.md) | Bộ chặn mạng chặn thêm UDP, tra tên; test T-027 chạy được trên Linux/Mac | Soi Lỗi | 2026-10-15 | [Soi Lỗi](reports/T-029-soi-loi.md) · Lá Chắn: [**ĐẠT CÓ ĐIỀU KIỆN**](reports/T-029-030-la-chan.md) (Opus tạm). Điều kiện chạy trên Windows: Chỉ Huy A chạy 2 lượt, 2.758 qua, 0 hỏng; test IPv6, Proactor, `vong-lap-mac-dinh` đều qua. Gộp vào `main` `7c8604e` |
| [T-028](tickets/T-028-noi-dung-hong-tu-may-chu-ai.md) | Máy chủ AI trả 200 nhưng nội dung hỏng → câu lỗi tiếng Việt; bỏ qua `*_CUSTOM_HEADERS` | Thợ Máy | 2026-10-15 | [Thợ Máy](reports/T-028-tho-may.md) (2 lượt) · [Soi Lỗi](reports/T-028-soi-loi.md): đạt · Lá Chắn: [**ĐẠT**](reports/T-028-la-chan.md) (Opus tạm), 3 lỗi Thấp ghi sổ. Gộp vào `main` `d08f8ca`: Windows 3.110 qua, 0 hỏng |
| [T-026](tickets/T-026-loi-thap-lop-ai.md) | 4 lỗi Thấp lớp AI: thư viện lệch phiên bản, câu lỗi 400 cố định, `base_url` chính thức | Thợ Máy | 2026-10-15 | [Thợ Máy](reports/T-026-tho-may.md) (2 lượt) · [Soi Lỗi](reports/T-026-soi-loi.md): đạt lượt 2 · Lá Chắn: [**ĐẠT**](reports/T-026-la-chan.md) (Opus tạm, Chỉ Huy B giao lại) |
| [T-027](tickets/T-027-test-chay-tren-windows.md) | Bộ test chạy xanh trên Windows | Soi Lỗi | 2026-10-15 | [Soi Lỗi](reports/T-027-soi-loi.md) · Lá Chắn: [**ĐẠT**](reports/T-027-la-chan.md) (Opus tạm), 2 lỗi Thấp → T-029. Gộp vào `main` `e4107f2`: Windows 2.358 qua, 0 hỏng |
| [T-024](tickets/T-024-loc-ho-so-theo-khoi.md) | Bộ lọc hồ sơ lọc theo cả ý | Thợ Máy | 2026-10-15 | [Thợ Máy](reports/T-024-tho-may.md) (2 lượt) · [Soi Lỗi](reports/T-024-soi-loi.md): đạt lượt 2 · Lá Chắn: [**ĐẠT**](reports/T-022-024-la-chan.md) (Opus tạm), 4 lỗi Thấp ghi sổ. Gộp vào `main` `958a93e` |
| [T-022](tickets/T-022-sua-ho-so-doanh-nghiep.md) | Soát, sửa hồ sơ doanh nghiệp theo trả lời của chủ dự án | Ngòi Bút | 2026-10-15 | [Ngòi Bút](reports/T-022-ngoi-but.md) (2 lượt) · [Soi Lỗi](reports/T-022-soi-loi.md): đạt · Lá Chắn: [**ĐẠT**](reports/T-022-024-la-chan.md) (Opus tạm). Gộp vào `main` `958a93e` |
| [T-023](tickets/T-023-nut-kiem-tra-khoa-openai-gemini.md) | Nút Kiểm tra khóa ChatGPT/Gemini trong Cài đặt → Kết nối | Họa Sĩ | 2026-10-15 | [Họa Sĩ](reports/T-023-hoa-si.md) (2 lượt) · [Soi Lỗi](reports/T-023-soi-loi.md): đạt · Lá Chắn: [**ĐẠT**](reports/T-018-023-la-chan.md) (Opus tạm) |
| [T-018](tickets/T-018-them-openai-gemini.md) | Thêm ChatGPT (`openai`) và Gemini (`google-genai`) vào lớp AI | Thợ Máy | 2026-10-15 | [Thợ Máy](reports/T-018-tho-may.md) (2 lượt) · [Soi Lỗi](reports/T-018-soi-loi.md): đạt lượt 2 · Lá Chắn: [**ĐẠT**](reports/T-018-023-la-chan.md) (Opus tạm), 4 lỗi Thấp → T-026 |
| [T-021](tickets/T-021-sua-loi-kho-nhap-va-env.md) | Sửa lỗi kho nháp và ghi `.env` (2 lượt Thợ Máy) | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-021-tho-may.md) · [Soi Lỗi](reports/T-016-020-soi-loi.md) lần 2: đạt · Lá Chắn: [**ĐẠT**](reports/T-016-020-la-chan.md) lần 2 (chạy tạm Opus) |
| [T-020](tickets/T-020-nhap-khoa-api-trong-app.md) | Nhập khóa API Claude/ChatGPT/Gemini trong Cài đặt | Thợ Máy, Họa Sĩ | 2026-10-14 | [Thợ Máy](reports/T-020-tho-may.md) · [Họa Sĩ](reports/T-020-hoa-si.md) · Lá Chắn: **ĐẠT** |
| [T-017](tickets/T-017-giao-dien-luu-nhap.md) | Tự lưu, mở lại, xóa bài đang soạn | Họa Sĩ | 2026-10-14 | [Báo cáo](reports/T-017-hoa-si.md) · Soi Lỗi: đạt · Lá Chắn: **ĐẠT** |
| [T-016](tickets/T-016-luu-nhap-bai-dang-soan.md) | Kho lưu nháp bài đang soạn | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-016-tho-may.md) · Soi Lỗi: đạt · Lá Chắn: **ĐẠT** |
| [T-015](tickets/T-015-loi-thap-con-lai.md) | Lỗi Thấp còn lại, test tốc độ ổn định (2 lần) | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-015-tho-may.md) · [Soi Lỗi](reports/T-015-soi-loi.md): đạt · Lá Chắn: [**ĐẠT**](reports/T-015-la-chan.md) lần 2 (chạy tạm bằng Opus) |
| [T-014](tickets/T-014-loi-thap-escape.md) | Lỗi Thấp của bộ escape link | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-014-tho-may.md) · [Soi Lỗi](reports/T-013-014-soi-loi.md): đạt, còn R5-1 → T-015 · Lá Chắn: [**ĐẠT**](reports/T-013-014-la-chan.md) (chạy tạm bằng Opus, kiểm lại bằng Fable sau 01/11) |
| [T-013](tickets/T-013-escape-cau-can-xem-lai.md) | Hiển thị an toàn câu «Cần xem lại» | Họa Sĩ | 2026-10-14 | [Báo cáo](reports/T-012-hoa-si.md) · Soi Lỗi: đạt · Lá Chắn: [**ĐẠT**](reports/T-013-014-la-chan.md) |
| [T-012](tickets/T-012-an-dau-escape-o-o-sua.md) | Ô sửa chữ không hiện dấu `\` | Họa Sĩ | 2026-10-14 | [Báo cáo](reports/T-012-hoa-si.md) · Lá Chắn: [**ĐẠT**](reports/T-008r3-012-la-chan.md) |
| [T-008](tickets/T-008-gia-co-bo-loc.md) | Chặn link Markdown tận gốc (3 lần) | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-008-tho-may.md) · Lá Chắn: **ĐẠT** · [Soi Lỗi](reports/T-008r3-012-soi-loi.md): đạt, còn R4-1 → T-013 |
| [T-011](tickets/T-011-sua-cum-cam-bat-nham.md) | Sửa cụm từ cấm bắt nhầm | Ngòi Bút | 2026-10-14 | Lá Chắn: [**ĐẠT**](reports/T-008r-010-011-la-chan.md) |
| [T-010](tickets/T-010-cau-hinh-chiu-loi-va-loi-thap.md) | File cấu hình chịu lỗi, lỗi Thấp | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-010-tho-may.md) · Lá Chắn: **ĐẠT** |
| [T-009](tickets/T-009-dua-loi-dan-moi-vao-code.md) | Đưa lời dặn AI mới vào code | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-009-tho-may.md) · Lá Chắn: [**ĐẠT**](reports/T-003-006-008-009-la-chan.md) |
| [T-006](tickets/T-006-sua-loi-nho-giai-doan-2.md) | Sửa lỗi Trung bình/Thấp Giai đoạn 2 | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-006-tho-may.md) · Lá Chắn: **ĐẠT** |
| [T-003](tickets/T-003-ra-soat-prompt-noi-dung.md) | Rà soát prompt, quy tắc văn phong | Ngòi Bút | 2026-10-14 | [Báo cáo](reports/T-003-ngoi-but.md) · Lá Chắn: **ĐẠT** |
| [T-004](tickets/T-004-loc-html-ket-qua-ai.md) | Lọc HTML/link trong kết quả AI | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-004-tho-may.md) · Soi Lỗi: [3 lỗ hở nhỏ](reports/T-004-T-005-soi-loi.md) → T-008 · Lá Chắn: [**ĐẠT**](reports/T-004-T-005-la-chan.md) |
| [T-005](tickets/T-005-escape-hien-thi-bai.md) | Hiển thị bài AI an toàn | Họa Sĩ | 2026-10-14 | [Báo cáo](reports/T-005-hoa-si.md) · Soi Lỗi: xác nhận · Lá Chắn: **ĐẠT** |
| [T-001](tickets/T-001-kiem-dinh-bao-mat-nen.md) | Kiểm định bảo mật toàn bộ code | Lá Chắn | 2026-10-14 | [Biên bản](reports/T-001-la-chan.md): KHÔNG ĐẠT (1 Cao). Nay **ĐẠT** (sau T-004, T-005, T-006, T-009). |
| [T-007](tickets/T-007-xoa-gps-anh-dai-dien.md) | Xóa GPS trong ảnh | Thợ Máy | 2026-10-14 | **Hủy**: chủ dự án muốn giữ vị trí trong ảnh (sổ rủi ro, `security.md` mục 6) |
| [T-002](tickets/T-002-kiem-thu-giai-doan-2.md) | Kiểm thử Giai đoạn 2 phần 1 | Soi Lỗi | 2026-10-14 | [Báo cáo](reports/T-002-soi-loi.md): 69 test mới, 8 lỗi (đánh dấu `xfail`), test chặn mạng thật. Chỉ Huy soát: test chỉ dùng khóa giả. |

## Việc bắt buộc khi làm Giai đoạn 5 (đăng lên WordPress)

Lá Chắn yêu cầu, xem các biên bản trong `reports/`:

- Chuyển Markdown sang HTML bằng code có escape, hiểu dấu `\` escape, chuẩn hóa xuống dòng, không xử lý link kiểu tham chiếu.
- `sanitize_html` áp cho toàn bộ HTML cuối, kể cả phần người dùng tự gõ.
- Màn hình xác nhận liệt kê mọi link (`href`), đánh dấu địa chỉ lạ hoặc có `@` ở phần tên máy. **Bắt buộc**, vì `sanitize_html` vẫn cho qua `<a href="https://…">`, nên link ẩn chỉ bị phát hiện ở bước này ([T-015-la-chan.md](reports/T-015-la-chan.md)).
- Đúng một đường đi tới `publish`/`future`, có bước xác nhận và có test.
- Từ khóa lấy từ Google Sheets phải được vô hiệu thẻ khung (SL-7).
- URL trần `https://…` trong thân bài có thể bị Markdown kiểu GFM tự biến thành link: bộ chuyển Markdown sang HTML không bật autolink, hoặc màn hình xác nhận liệt kê cả các URL này ([T-015-soi-loi.md](reports/T-015-soi-loi.md)).
- Gỡ ký tự rộng 0 (U+200B) mà T-031 chèn vào địa chỉ (`unbreak_autolinks`) trước khi gửi WordPress, cho cả thân bài, tiêu đề, meta. Sau khi gỡ thì bộ chuyển Markdown → HTML **không** bật autolink, hoặc màn hình xác nhận liệt kê cả địa chỉ trần. Chữ đã gỡ không được coi là an toàn ([T-031-la-chan.md](reports/T-031-la-chan.md)).
- Bất biến: kết quả `unescape_link_syntax` / `unbreak_autolinks` không bao giờ được đưa vào `st.markdown`.

## Số phiếu tiếp theo: T-075

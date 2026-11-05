# Báo cáo T-128 · Sổ rủi ro 3 giới hạn `modified_gmt` và kịch bản buổi thử thật Hẹn giờ / Đăng ngay

| Mục | Nội dung |
|---|---|
| Agent | Thư Ký (`thu-ky`) · model: Claude Opus 5.5 |
| Phiếu | [T-128](../tickets/T-128-so-rui-ro-va-kich-ban-thu-that.md) (Chỉ Huy B giao 04/11; làm 04/11, nghỉ vì hết hạn mức, làm tiếp 05/11) |
| Nhánh | `team/T-128` (từ `main` cục bộ `2a7b408`) |
| Ngày nộp | 2026-11-05 10:19 (+07:00, theo lệnh `date`) |
| Kết quả | Hoàn thành yêu cầu 1–3. Sửa `docs/team/security.md` mục 6; thêm `docs/team/reports/T-128-kich-ban-thu-that.md` và báo cáo này. Không sửa code, README |

## Tóm tắt (cho chủ dự án)

- **Sổ rủi ro** có thêm 3 dòng anh/chị đồng ý ngày 04/11. Đó là ba khe rất hẹp của cách phần mềm kiểm «bài nháp có bị ai sửa không» ngay trước khi hẹn giờ hay đăng:
  1. ai đó sửa bài đúng trong cùng một giây;
  2. sửa đúng lúc giữa hai lệnh của phần mềm;
  3. chỉ đổi ảnh đại diện bằng trình soạn cổ điển.

  Cả ba cần người có tài khoản sửa bài đang sửa đúng bài nháp vừa tạo, trong vài giây.
- **Kịch bản buổi thử thật** đã soạn sẵn từng bước, anh/chị báo rảnh là làm được. File `docs/team/reports/T-128-kich-ban-thu-that.md`, gồm:
  - chuẩn bị: việc anh/chị quyết phía website, bài thử, Sheet bản sao;
  - 6 ca thử (0 tới 5), thêm ca Sheet;
  - cách dọn sau buổi thử;
  - bảng ghi kết quả cho Lá Chắn.
- Buổi thử có **hai bài thử hiện công khai vài phút** (một bài hẹn giờ 15 phút, một bài Đăng ngay) rồi gỡ ngay. Anh/chị đọc nội dung trước khi bấm. Khoảng 1 giờ 30.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `docs/team/security.md` mục 6, `:178-180` (3 dòng mới, ngày 2026-11-04) | Giới hạn 1 «cùng giây»; giới hạn 2 «khe giữa lệnh đọc kiểm và lệnh ghi của app»; giới hạn 3 «sửa chỉ phần meta». Mỗi dòng có rủi ro (dẫn `release_draft` `client.py:1545-1550`), lý do chấp nhận (WordPress không có khóa lạc quan `If-Match`; cần người đang sửa đúng bài nháp vừa tạo trong vài giây của một cú bấm; nội dung đã xác nhận bằng mã băm T-102), người quyết định «Chủ dự án (04/11)». Dòng 3 thêm: trình soạn khối luôn đổi giờ sửa nên khe hẹp; cách thu hẹp không bắt buộc (xin thêm `featured_media`, Lá Chắn T-115) |
| `docs/team/reports/T-128-kich-ban-thu-that.md` (mới, 266 dòng) | Kịch bản cho Chỉ Huy, chủ dự án ngồi cùng. Mục 0 tóm tắt; 1 quy tắc (không bí mật, chủ dự án tự đăng nhập và tự xóa hẳn, một tab, không mở trình soạn khi app đang gửi, điểm dừng); 2 bảng việc → ca; 3 chuẩn bị (việc phía website chủ dự án quyết, máy, bài thử, Sheet bản sao, ca 0); 4 các ca 1–5, xem bài hiển thị thật, ca S, (f) suốt buổi; 5 khi có sự cố; 6 dọn (10 dòng); 7 bảng kết quả cho Lá Chắn; 8 sau buổi thử |

## Đối chiếu

### Yêu cầu 1: ba giới hạn (`docs/team/reports/T-115-la-chan.md`, mục 4 «Tự tái hiện cả ba», điều kiện 3)

| Giới hạn (biên bản) | Dòng sổ |
|---|---|
| 1. Cùng giây: `modified_gmt` tính tới giây; sửa cùng giây với lệnh ghi cuối của app thì giờ không đổi | `:178` |
| 2. Khe giữa lệnh đọc kiểm và lệnh ghi (vài trăm mili giây): lệnh ghi của app đặt giờ sửa mới, client nhớ giờ đó nên lần sửa kia bị «rửa» | `:179` |
| 3. Sửa chỉ meta (ảnh đại diện qua trình soạn cổ điển, plugin ghi khóa meta riêng): giờ sửa không đổi | `:180` |
| Lý do chấp nhận: không khóa lạc quan; cần người đang sửa đúng nháp vừa tạo, vài giây; nội dung xác nhận bằng mã băm (T-102); trình soạn khối luôn đổi giờ sửa | cả 3 dòng; ý trình soạn khối ở `:180` |
| Mức Thấp; Lá Chắn T-112 (Fable) đồng ý (`T-112-la-chan.md` mục 2) | ghi trong cột rủi ro |
| Chủ dự án đồng ý 04/11 (phiếu T-128, tin Chỉ Huy B) | cột người quyết định «Chủ dự án (04/11)» |

Số dòng code `client.py:1545-1550` kiểm trên nhánh (`known = self._modified.get(post_id)` … `raise ReleaseError(_RELEASE_CHANGED, **fail)`).

### Yêu cầu 2: đủ mục (a)–(g) (`T-112-la-chan.md` «Điều kiện» B4; bảng lượt 3 mục 5 và lượt 3 Fable mục 4)

| Mục | Ca trong kịch bản |
|---|---|
| (a) `publish_posts` | Ca 0 bước 1 («Đăng bài: ✅») |
| (b) Abilities có đổi `modified_gmt` không | Ca 2 (đối chứng: không ghi SEO) + ca 3 (ghi SEO); kết quả CÓ ĐỔI thì bỏ ca 5, cần phiếu client |
| (c) múi giờ, giờ hẹn trong trang quản trị | Ca 0 bước 2; ca 2 bước 2, 5 |
| (d) trình soạn khối hay cổ điển | Ca 0 bước 3 |
| (e) WP-Cron đăng đúng giờ | Ca 4 (hẹn 15 phút, xem tự đăng; lỡ lịch thì mở trang chủ, đợi thêm) |
| (f) câu báo không lộ gì lạ | Quy tắc 8 (điểm dừng), mục «Suốt buổi · (f)» |
| (g) `srcset`/GPS (T-059 ghi nhận 2); «< 5 triệu» (T-091 điều kiện 4) | Ca 1 bước 1, 4, 5 |

Các ý khác của LC-T094-44 (`T-094-la-chan.md:138`), và các việc Fable T-116 nhóm 2 gom vào buổi thử:

| Ý | Ca trong kịch bản |
|---|---|
| Thử trên Sheet bản sao | Mục 3.4, ca S |
| Không ghi bí mật vào báo cáo | Quy tắc 1, dọn bước 10 |
| Hẹn giờ, đăng chỉ bài chủ dự án duyệt | Quy tắc 2, mục 3.1 |
| Header `Date` | Ca 0 bước 4, ca 2 bước 4 |
| Biên tập viên hẹn giờ được qua REST | Ca 2 |
| Xem bài hiển thị thật | Mục 4.1 |
| T-110 điều kiện 3 (Media ẩn danh, gắn ảnh không 403) | Ca 1 bước 3, 6 |
| T-097 điều kiện 5 (tùy chọn) | Mục 3.4 |
| Nguồn T-112 B4 «cuối cùng chuyển về nháp/xóa» | Ca 2, ca 3 bước chuyển về nháp; mục 6 |

**Câu chữ trong kịch bản.** 73 câu báo, tên nút, nhãn ô trích trong kịch bản đều có trong `app/`, `seo_app/` trên nhánh. Kiểm bằng script Python đọc UTF-8, có nối chuỗi viết tách dòng: «tổng: 73 thiếu: 0».

**Luật dòng kế hoạch.** Ca S ghi đúng luật đọc từ code:
- `seo_app/plan/sync.py` `write_status`: trạng thái chỉ đi tới, câu `STATUS_LATER`.
- `seo_app/plan/website.py`: chỉ đi tới. Bài về nháp thì cảnh báo `NOTICE_BACK_TO_DRAFT`, không ghi; `NOTICE_LATE` «Lỡ lịch»; `NOTICE_MISSING` sau khi xóa.

Bản nháp đầu của tôi viết «Cập nhật trạng thái từ website ghi lại về nháp»; đọc code thấy sai nên đã sửa trước khi nộp.

## Kiểm tra

```
$ uv --version                 # trước khi chạy uvx (T-078)
uv 0.13.4 (7456b60bc 2026-10-20 x86_64-pc-windows-msvc)
$ PYTHONUTF8=1 uvx detect-secrets scan docs/team/security.md docs/team/reports/T-128-kich-ban-thu-that.md docs/team/reports/T-128-thu-ky.md
  "results": {}
$ (script đối chiếu câu trích)  tổng: 73 thiếu: 0
```

Kịch bản không chứa mật khẩu ứng dụng, mật khẩu, tên hay nội dung file khóa, mã hay link Sheet, email tài khoản dịch vụ, tên tài khoản WordPress. Địa chỉ website viết `<tên-miền>`. Không chạy pytest, ruff (chỉ đổi tài liệu).

## Rủi ro và điểm cần chú ý

- **Nhãn trang quản trị WordPress, Google Sheets** (bộ lọc «đã lên lịch», «Sửa nhanh», «Tệp → Tạo bản sao»…) viết theo nghĩa, kèm tên tiếng Anh. Tôi chưa đối chiếu trên trang thật.
- **Google có thể chưa nối.** Theo `TIEN-DO.md`, tạo tài khoản dịch vụ là việc của chủ dự án «khi tới bước thử thật». Chưa nối thì mục 3.4 và ca S ghi «chưa làm»; Lá Chắn xét có cần làm trước khi dùng không.
- **(b) suy ra từ đối chứng**, không đọc thẳng `modified_gmt`, để không phải dùng mật khẩu ứng dụng ngoài app. Ca 2 không ghi SEO mà hẹn giờ được, còn ca 3 ghi SEO thì bị chặn ⇒ Abilities đổi giờ sửa. Điều kiện: không ai mở bài trong trình soạn lúc đang gửi (quy tắc 5).
- **Ca 4, ca 5 đăng bài công khai** trên website thật (không có website thử). Kịch bản giảm rủi ro bằng: chủ dự án duyệt nội dung, quyết trước về plugin tự báo bài mới, gỡ ngay, xóa cache, kiểm địa chỉ ra «không tìm thấy». Chủ dự án vẫn nên biết là vài phút đó khách có thể thấy bài.
- **Bước kiểm tên máy chủ Google** (T-097 đk 5) bằng `Get-DnsClientCache` chỉ để tham khảo: bộ nhớ tên miền của Windows có cả tên do trình duyệt tra.

## Câu hỏi cho chủ dự án

Không có câu mới. Các việc phía website (sao lưu, plugin tự báo bài mới, duyệt bài thử) đã ghi ở mục 3.1 của kịch bản để anh/chị quyết khi bắt đầu buổi thử.

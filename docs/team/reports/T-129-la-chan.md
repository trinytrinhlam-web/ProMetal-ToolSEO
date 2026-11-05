# Biên bản bảo mật T-129 · Rà soát đóng Giai đoạn 4 (tối ưu on-page)

> **Model:** Claude Opus 5.5. Chỉ Huy B giao (Fable để dành cho phiếu nhạy cảm Giai đoạn 6); chủ dự án quyết ngày 04/11: hết hạn mức Fable thì Lá Chắn chạy Opus.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-129](../tickets/T-129-la-chan-ra-soat-giai-doan-4.md) · rà soát cả giai đoạn (việc 1–4), như T-093 đã làm cho Giai đoạn 3 |
| Phạm vi | <ul><li>**Mã:** `main` máy `9952ba1`, checkout `D:\ProMetal-ToolSEO\ProMetal-ToolSEO` (chỉ đọc); nhánh `team/T-129` tạo từ `main`, cùng commit.</li><li>**Nền, không kiểm lại từ đầu:** biên bản Fable [T-116 nhóm 5](T-116-la-chan-nhom-5.md) (on-page, bước SEO: T-036 → T-042, T-059, T-095) và [nhóm 2](T-116-la-chan-nhom-2.md) (WordPress, đăng bài: T-060, T-061, T-085, T-088, T-091, T-106, T-108).</li><li>**Đối chiếu thêm:** thiết kế [T-033](T-033-tho-may.md); Lộ trình trong `CLAUDE.md`; biên bản Lá Chắn T-112, T-092, T-117, T-118, T-122; sổ rủi ro `docs/team/security.md` mục 6; `TIEN-DO.md` mục 4; `docs/team/board.md`.</li><li>**Đổi từ mốc nhóm 5 (`29499dd`):** mã lõi Giai đoạn 4 (`seo_app/onpage/`, `site_index.py`, client WordPress, lời dặn, `config/`) **không đổi dòng nào**. Chỉ `write.py`, `drafts.py`, README, `.env.example` đổi (T-112, T-092, đã có Lá Chắn riêng); tôi đọc lại các đoạn chạm bước SEO.</li><li>Không gọi website thật, không sửa mã.</li></ul> |
| Ngày | 2026-11-05 (12:38–13:08, giờ máy +07) |
| **Kết luận** | **ĐÓNG CÓ ĐIỀU KIỆN.** <ul><li>Mọi hạng mục của thiết kế T-033 đã có trên `main` (riêng schema FAQ chỉ hiện trong app, đúng thiết kế và quyết định 04/11); đã thử thật trên website 27–28/10.</li><li>0 Nghiêm trọng, 0 Cao, 0 Trung bình. **1 Thấp mới**: LC-T129-1, cache danh sách bài kiểm cấu trúc file theo kiểu cũ.</li><li>Còn mở từ trước: SL-T106-1 (Thấp: trang Kết nối còn khuyên «Quản trị viên»), SL-T117-1 (Thấp, chưa có phiếu), vài mục «sửa khi tiện».</li><li>**3 điều kiện để đánh dấu xong** (mục 5): sửa SL-T106-1; lập phiếu dọn kho dữ liệu phụ; cập nhật tài liệu. Việc thử thật còn nợ và việc phía website đã có chỗ theo dõi, không chặn.</li></ul> |

## Tóm tắt (cho chủ dự án)

- **Phần «SEO trên trang» của phần mềm đã làm đủ theo thiết kế và an toàn để dùng.**
  - Gồm: tiêu đề và mô tả hiện trên Google, đường dẫn bài, liên kết nội bộ, schema hỏi đáp, ghi SEO vào bài nháp trên website.
  - Đã thử thật trên website ngày 27–28/10.
- **Phần mềm không tự đưa gì lạ lên website.**
  - Chữ SEO có mã, shortcode hay ký tự lạ bị chặn.
  - Chỉ ghi vào bài nháp chính nó vừa tạo; công tắc «Ghi SEO lên website» mặc định tắt.
  - Link nội bộ chỉ trỏ tới bài đã đăng trên chính website.
  - Schema chỉ hiện trong phần mềm để xem, chưa gửi lên website.
- **Không có lỗi nặng. Còn 2 việc nhỏ trước khi đánh dấu xong:**
  1. Trang «Kết nối WordPress» còn một câu khuyên dùng tài khoản «Quản trị viên» khi tài khoản thiếu quyền. Câu này trái với việc anh đã chọn tài khoản Biên tập viên riêng. Sửa một câu.
  2. File lưu tạm danh sách bài trên máy được kiểm theo kiểu cũ. Nếu một chương trình lạ trên máy sửa file này, nút tải lại danh sách bài có thể chạy rất lâu. Không lộ gì, và không có link sai nào lên website, vì phần mềm kiểm lại từng link. Sửa trong một phiếu dọn nhỏ, làm chung cho file bài nháp và file kế hoạch.
- **Mang sang, đã có chỗ theo dõi:**
  - Buổi thử thật chung: tiêu đề SEO có dấu «<», ghi SEO có làm đổi giờ sửa bài không, ảnh trên điện thoại.
  - Việc anh làm trên website từ 16/10 (chưa xác nhận xong): tắt khối thông tin doanh nghiệp rỗng của SiteSEO, bỏ đoạn «3 chi nhánh…» ở trang chủ, cân nhắc bỏ mức giá «$$», nhờ người làm web xác nhận 3 đường nhạy cảm của website.
- **Không có gì anh phải quyết ngay.**

## 1. Đối chiếu Lộ trình và thiết kế T-033 với `main` (việc 1)

Thiết kế T-033 dùng số phiếu tạm; bảng dưới ghi số phiếu thật.

| Hạng mục (thiết kế T-033) | Phiếu | Trên `main` | Ghi chú |
|---|---|---|---|
| Meta tiêu đề, mô tả: đếm ký tự như Google (NFC), nhãn Nên/Cảnh báo/Chặn, kiểm trùng bài đã đăng, AI gợi ý, viết lại, quay lại bản trước | T-036, T-041 | Có | `seo_app/onpage/meta.py`, bước 4 «SEO» |
| Đuôi « \| Pro-Metal» khi tiêu đề còn chỗ (câu 3A) | T-036, T-041 | Có | `brand_suffix` |
| Slug không dấu | T-036, T-041 | Có | Gửi kèm bài từ T-102 |
| Danh sách bài đã đăng và cache | T-037, T-042 | Có | `seo_app/storage/site_index.py` (xem LC-T129-1) |
| Liên kết nội bộ | T-039 | Có | Link do code chèn, AI chỉ chọn cụm từ có sẵn; bảng tick «Dùng» |
| Lời dặn AI cho meta, anchor | T-040 | Có | `config/content.toml` mục `[meta]` |
| Schema FAQPage: dựng, kiểm, xem trước | T-038, T-041 | Có, **chỉ hiện trong app** | Thiết kế 3.3: Giai đoạn 4 chưa đưa lên website. Chủ dự án 04/11: giữ như hiện tại. README mục 10 nói rõ «app chưa gửi schema lên website» |
| Không xuất Article, Breadcrumb, LocalBusiness; chặn HowTo | T-038 | Có | Website tự xuất các loại đó |
| Ghi tiêu đề, mô tả, từ khóa chính vào SiteSEO qua Abilities, chỉ nháp app tạo (câu 1A, 2A) | T-042, T-041 | Có | Công tắc mặc định tắt; hỏi lại website «bài còn là nháp» sau khi ghi |
| Thử thật trên website | T-059 | Xong 27–28/10 | Còn việc thử lại trong buổi thử thật chung (mục 2) |
| mu-plugin dự phòng | — | Không cần | Abilities ghi được |
| Việc chủ dự án trên website (câu 4A): khối Organization rỗng của SiteSEO, đoạn mô tả thừa ở trang chủ, mức giá «$$» | Chủ dự án | **Chưa xác nhận** | `TIEN-DO.md` mục 4, việc 6 (ghi từ 16/10) |
| Để ngoài Giai đoạn 4 theo thiết kế (cuối mục 6): schema Service cho trang dịch vụ, LocalBusiness trang khu vực, FAQPage lên website (cách d mục 3.3), YC-501 rà 29 URL | — | Chưa làm | Đúng thiết kế, mang sang |
| Tài liệu | — | **Cũ** | <ul><li>`CLAUDE.md`, Lộ trình: dòng Giai đoạn 4 còn ghi «Đang kiểm: meta (T-036), danh sách bài đã đăng + cache (T-037)».</li><li>`TIEN-DO.md` dòng 19 («phần meta… chờ kiểm») và dòng 188 («Meta… chưa được lưu vào nháp»).</li><li>Bảng tiến độ ghi «khoảng 98%» mà không nói còn gì.</li></ul> |

## 2. Điều kiện, lỗi Lá Chắn còn mở (việc 2)

Nền: nhóm 5 và nhóm 2 của T-116 đã đối chiếu từng mã của các phiếu Giai đoạn 4 (giữ cả, 0 đổi mức, 0 sai). Tôi đối chiếu lại các mục còn mở trên `9952ba1`.

**Đã đóng sau mốc của nhóm 2, nhóm 5:**

| Mục | Bằng chứng |
|---|---|
| SL-T108-1 (README) | `746ba9d` (T-112, Thư Ký lượt 2); README dòng 7 nay ghi «tạo thử bài nháp chữ» |
| T-095 QS 1 (`.env.example`) | `.env.example:23-24` nay ghi rõ tài khoản Biên tập viên riêng, không dùng tài khoản quản trị |
| SL-T112-1 (phần Chặn của LC-T094-39) | T-112 lượt 3 (`58d5326`): «Đăng ngay» bị Chặn khi bật «Ghi SEO» mà tiêu đề, mô tả trống hay đang «Chặn» (`seo_notices`) |
| LC-T113-2 (phần `site_index._parse_time`) | T-118: `site_index.py:391-396` bắt `OverflowError`, `ValueError` thành «file hỏng» |

**Còn mở:**

| Mục | Mức | Ở đâu | Việc |
|---|---|---|---|
| **SL-T106-1** | Thấp | `app/views/wordpress.py:131-134` | <ul><li>Khi tài khoản thiếu quyền viết bài hay tải ảnh, trang khuyên «Biên tập viên (Editor) **hoặc Quản trị viên (Administrator)**».</li><li>Câu này trái quyết định 2A và ngược câu ở dòng 78 («không nên nâng lên Quản trị viên»).</li><li>Ca `xfail(strict=True)` còn ở `tests/test_soi_loi_t106.py:296`.</li><li>**Sửa trước khi đánh dấu xong** (điều kiện 1).</li></ul> |
| **LC-T129-1** (mới) | Thấp | `seo_app/storage/site_index.py` | Mục 3d, mục 4. Phiếu dọn (điều kiện 2) |
| **SL-T117-1** | Thấp, cũ | `site_index.py`, `drafts.py`, `plan_cache.py` | Ba kho chưa kiểm `data/` là lối tắt (`dir_has_link`). Biên bản T-117 đề xuất phiếu «dọn kho dữ liệu phụ», **chưa có phiếu**. Gộp vào điều kiện 2 |
| LC-T036-2 | Thấp, ghi nhận | `seo_app/onpage/meta.py` (`has_link`) | Bộ dò link trong gợi ý meta sót vài dạng tên miền lạ (`evil。com`, `evil[.]com`…). Lá Chắn T-036 xếp «sửa khi tiện» |
| SL-T036-11, SL-T036-10 | Thấp | Bộ dò giá trong gợi ý meta; 5 ca `xfail` | Vài cách nói giá («5 trăm», «triệu rưỡi») lọt. SL-T036-10 phần «đô vật» lệch về phía an toàn. «Sửa khi tiện» |
| T-091 ĐK 4; T-059 ĐK 2, 3; LC-T094-44 (b) | Thử thật | Buổi thử thật chung (kịch bản ở phiếu T-128) | <ul><li>Nội dung thử: tiêu đề SEO có «<» hiện đúng trong SiteSEO; `srcset` trên điện thoại; ghi SEO qua Abilities có đổi `modified_gmt` không.</li><li>**Không chặn đóng**: «Ghi SEO» mặc định tắt, và nếu sai thì app báo «chưa ghi được» (đóng an toàn).</li></ul> |
| T-041 ĐK 3 | Chưa áp dụng | — | Chỉ áp khi có phiếu đưa schema lên website (cách d mục 3.3 của T-033, qua Lá Chắn) |
| T-038 lỗi 4; T-039 QS 2, 3; T-040 QS 2 | Ghi nhận | — | Giữ như nhóm 5 (không chạm được, hay chỉ là ghi nhận) |
| `write_seo` gọi hàm riêng `client._own_draft` | Gọn mã | `app/views/write.py` (hàm `write_seo`) | Chú thích trong mã đề nghị mở hàm công khai. Không phải lỗi; gộp phiếu dọn nếu tiện |

**Sổ rủi ro (mục 6).**
- Hai dòng có sẵn đã phủ rủi ro dùng thật của Giai đoạn 4:
  - 28/10: tài khoản Biên tập viên có quyền `unfiltered_html`;
  - 30/10: shortcode chạy lại khi chủ dự án tự sửa bài trên website.
- Không cần dòng mới nếu phiếu dọn làm LC-T129-1 và SL-T117-1.
- LC-T036-2, SL-T036-11 không cần ghi sổ, vì không phải đường tấn công: meta là chữ thuần trên trang kết quả Google, người dùng duyệt từng ô; «không nêu giá» là quy tắc nội dung.

## 3. Rủi ro khi người dùng thật dùng bước SEO (việc 3)

**a. Chữ SEO ghi lên website** (tiêu đề, mô tả, từ khóa chính vào SiteSEO qua Abilities)

- **Lớp chặn:**
  - công tắc «Ghi SEO lên website» mặc định tắt;
  - chỉ ghi vào bài nháp app vừa tạo trong chính lần gửi;
  - sau khi ghi, hỏi lại website bài còn là nháp;
  - chữ có thẻ HTML, mã ký tự, shortcode, ký tự điều khiển hay ký tự lạ bị Chặn ở bước SEO và ở client;
  - so dạng đã lưu theo `sanitize_text_field` (T-091).
  - Đã thử thật 27–28/10 bằng tài khoản Biên tập viên.
- **Còn lại:**
  - Gợi ý AI có thể còn một cách nói giá (SL-T036-11), một số điện thoại của xưởng (T-040 QS 2, số công khai), hay một dạng tên miền lạ (LC-T036-2). Người dùng phải đọc lại từng ô trước khi lưu: đó là chữ hiện công khai trên Google.
  - Abilities là tính năng của cả website: lộ mật khẩu ứng dụng thì người có nó sửa được SEO mọi bài. App tự giới hạn mình vào nháp; phần còn lại cùng lớp với dòng sổ rủi ro 28/10.
  - Tiêu đề có «<» chưa thử thật (buổi thử thật chung).

**b. Link nội bộ**

- **Lớp chặn:**
  - địa chỉ link chỉ lấy từ danh sách bài đã đăng, và kiểm lại đúng website ngay lúc chèn;
  - AI chỉ chọn cụm từ có sẵn trong bài;
  - code chèn link (`html.escape`), không chèn trong tiêu đề, mã, chú thích;
  - mọi link qua bộ kiểm trước khi gửi;
  - người dùng tick «Dùng» từng link.
- **Còn lại:**
  - Danh sách bài cũ (bài vừa chuyển về nháp hay bị xóa) có thể cho một link hỏng: bấm tải lại danh sách bài trước khi gửi.
  - Cache danh sách bài trên máy: LC-T129-1 (mục d).

**c. Schema trong app**

- **Lớp chặn:**
  - chỉ hiện bằng `st.code`; JSON đổi `<`, `>`, `&` thành `\u003c`… nên không đóng được thẻ `<script>`;
  - câu hỏi có thẻ HTML bị Chặn;
  - địa chỉ không bao giờ vào schema;
  - app không gửi schema lên website.
- **Còn lại:**
  - Ô «Dùng schema Hỏi đáp (FAQ) này cho bài» chỉ ghi nhớ lựa chọn trong nháp. README mục 10 nói rõ, nhưng giao diện chưa nói ngay dưới ô; người dùng có thể tưởng schema đã lên website. Góp ý: thêm một dòng chú thích.
  - Nếu chủ dự án tự dán đoạn mã lên website thì đoạn mã an toàn để đặt trong thẻ `<script type="application/ld+json">`. Cách đưa lên chuẩn vẫn là cách d (phiếu riêng, qua Lá Chắn).

**d. Cache danh sách bài trên máy** (`data/site_index.sqlite`): LC-T129-1, chi tiết ở mục 4.

## 4. Lỗi tìm thấy

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T129-1 | Thấp | Cache danh sách bài (làm từ T-037, trước khi có mẫu kiểm file của `plan_cache`, `image_tags`, `search_cache`) kiểm cấu trúc file theo kiểu cũ. `_is_healthy` chỉ so cột hai bảng `pages`, `info` (`site_index.py:399-416`). Thiếu bốn lớp: so trọn `sqlite_master` (bảng lạ, trigger, khung nhìn bị từ chối), `trusted_schema = OFF`, giới hạn số bước, giới hạn độ dài giá trị | `seo_app/storage/site_index.py:283-300` (`_prepare`), `:399-416` (`_is_healthy`) | <ul><li>**Đầu vào:** chương trình lạ có quyền ghi vào `data/` cài vào file một bảng phụ và một trigger tính nặng chạy sau mỗi lần chèn dòng.</li><li>**Đã chạy:** `_is_healthy` trả `True`, file không bị bỏ (`reset_count` 0). Mỗi lần ghi danh sách bài, trigger chạy trên từng dòng: 2 bài mất 0,61 giây với trigger thử (nhân chéo 10⁷ dòng).</li><li>**Hậu quả:** danh sách tối đa 10.000 dòng, trigger lại có thể nặng hơn, và không có giới hạn số bước để dừng. Vì vậy bấm tải lại danh sách bài có thể treo rất lâu.</li><li>**Mức độ:** đọc ra vẫn đúng 2 bài: mỗi dòng dựng lại `PublishedItem` và kiểm `is_site_link`, nên không có link lạ (T-037 đã thử trigger chèn link lạ: bị bỏ). Không lộ gì; chỉ làm chậm hay treo. Muốn làm phải ghi được vào `data/` (cùng lớp «phải chiếm máy trước»).</li><li>**Đối chứng:** cùng kiểu sửa trên `search_cache` thì `_is_healthy` trả `False`, bỏ file ngay.</li><li>**Kho khác (đọc mã, chưa thử riêng):** kho nháp `drafts.py` cũng thiếu cả bốn lớp; `plan_cache` có đủ, chỉ thiếu `dir_has_link`.</li></ul> | Trong phiếu «dọn kho dữ liệu phụ» (điều kiện 2): <ul><li>`site_index` kiểm như `search_cache`: so trọn `sqlite_master` (trước khi mở và trong cùng giao dịch), `trusted_schema = OFF`, giới hạn số bước, độ dài.</li><li>Đọc `sqlite_master` bằng bộ giải mã có bắt lỗi, để không lặp LC-T122-1.</li><li>Rà `drafts` cùng kiểu.</li><li>Thêm ca test: trigger, bảng lạ, khung nhìn thì bỏ file.</li></ul> |

Không có lỗi Nghiêm trọng, Cao, Trung bình.

## 5. Kết luận giai đoạn và đề xuất phiếu (việc 4)

**ĐÓNG CÓ ĐIỀU KIỆN.**

Phần mềm làm đủ các hạng mục Giai đoạn 4 của thiết kế, an toàn để dùng thật. Ba điều kiện trước khi đánh dấu `[x]` trong Lộ trình:

1. **Sửa SL-T106-1** (một câu, Họa Sĩ):
   - `wordpress.py:131-134` chỉ khuyên tài khoản Biên tập viên;
   - gỡ `xfail` trong `tests/test_soi_loi_t106.py` (R5: chỉ xóa dấu).

   Làm chung được với phiếu dọn chữ ở bảng dưới.
2. **Lập phiếu «dọn kho dữ liệu phụ»** cho LC-T129-1 và SL-T117-1, làm trước bản 1.0. Theo `security.md`, «đóng có điều kiện» cần lỗi Thấp còn lại có phiếu sửa.
3. **Cập nhật tài liệu khi đánh dấu** (Chỉ Huy, Thư Ký):
   - dòng Giai đoạn 4 trong Lộ trình `CLAUDE.md`;
   - `TIEN-DO.md` dòng 19, 188;
   - bảng tiến độ;
   - ghi rõ những gì mang sang (dưới).

**Không chặn đánh dấu, đã có chỗ theo dõi:**
- Buổi thử thật chung (kịch bản ở phiếu T-128): LC-T094-44 mục (b) và (g). Lá Chắn đọc báo cáo buổi thử.
- Việc chủ dự án làm trên website: `TIEN-DO.md` mục 4, việc 6.

**Mang sang, ngoài Giai đoạn 4 theo thiết kế:**
- schema Service cho trang dịch vụ;
- LocalBusiness cho trang khu vực;
- FAQPage lên website (cách d, qua Lá Chắn; áp T-041 ĐK 3);
- YC-501 rà 29 URL.

**Đề xuất phiếu** (số tạm, Chỉ Huy đánh lại):

| Phiếu | Việc | Agent | Lá Chắn |
|---|---|---|---|
| T-130 · Dọn kho dữ liệu phụ | <ul><li>(1) `site_index`, `drafts`: kiểm file như `search_cache` (LC-T129-1).</li><li>(2) `site_index`, `drafts`, `plan_cache`: `dir_has_link` ngay từ đầu (SL-T117-1).</li><li>(3) `plan_cache._is_healthy`: lỗi giải mã, «unsupported file format» là file lạ (cùng mẫu LC-T122-1).</li><li>Test ghim từng phần; chạy test mọi nơi gọi.</li></ul> | Thợ Máy | Rút gọn; **đầy đủ** nếu đụng `drafts.py` (kho giữ khóa chống gửi trùng) |
| T-131 · Dọn chữ Giai đoạn 4 | <ul><li>**Bắt buộc:** SL-T106-1.</li><li>**Tùy chọn:** LC-T036-2, SL-T036-11 (`meta.py`); một dòng chú thích dưới ô «Dùng schema FAQ» («app chưa gửi schema lên website»); mở hàm công khai thay `client._own_draft`.</li></ul> | Họa Sĩ (Thợ Máy cho `meta.py`, client) | Rút gọn |

## 6. Kết quả công cụ quét, test

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pytest | 41 file liên quan (meta, liên kết, schema, danh sách bài, bước SEO, ghi SEO, trang Kết nối, luật «Đăng ngay» của T-112): **4.126 qua**, 1 bỏ qua (symlink trên Windows), 7 `xfail` đã biết (SL-T036-11 ×4, SL-T036-10 ×1, SL-T106-1 ×2), **0 hỏng**; 19 phút 58 giây | <ul><li>Chỉ test liên quan, không chạy toàn bộ pytest (theo tin giao).</li><li>Móc kiểm `sys.addaudithook`, 3.164 sự kiện:<ul><li>1.473 lần `connect` và 749 lần `bind` đều tới `127.0.0.1` hay `::1`: cặp socket nội bộ của asyncio trong test giao diện (ngoại lệ T-027 của `conftest`);</li><li>60 lần mở `.env` đều trong thư mục tạm của pytest, không đụng `.env` thật;</li><li>1 tiến trình con Python khóa một file SQLite tạm (ca «file đang bận»).</li></ul></li><li>**0 kết nối ra ngoài máy.**</li></ul> |
| pip-audit | Chạy lại hôm nay (`uv export` rồi `uvx pip-audit -r … --no-deps --disable-pip`): 69 gói; nguồn PyPI và OSV: **No known vulnerabilities found** | `uv.lock`, `pyproject.toml` không đổi từ `29499dd` |
| detect-secrets (`PYTHONUTF8=1`) | <ul><li>13 file Giai đoạn 4 (`onpage/*`, `site_index.py`, `client.py`, `prompts.py`, `write.py`, `wordpress.py`, `config/*.toml`, README, `.env.example`): **0 bí mật thật**.</li><li>2 báo nhầm (mục 7).</li><li>Mồi bị bắt.</li><li>Biên bản này: 0.</li></ul> | Chạy trên bản chép, đứng tại thư mục chép, đường dẫn tương đối, `--all-files` |
| bandit, ruff | Không chạy lại | Phiếu không sửa mã; mã lõi Giai đoạn 4 không đổi từ lượt quét của nhóm 5 (bandit 0 lỗi thật, ruff sạch) |
| Thử riêng | `probe_site_index.py` (thư mục nháp): LC-T129-1, có đối chứng `search_cache` | |

**Danh sách kiểm tra** (vùng Giai đoạn 4):

| Mã | Kết quả | Ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets 0 bí mật thật |
| S2 | Đạt | Câu báo cố định; nhóm 2, 5 |
| S3 | Đạt | `.env.example` đủ biến, có chú thích tài khoản Biên tập viên |
| W1 | Đạt | Ghi SEO chỉ vào nháp app vừa tạo; không đổi `status` |
| W2 | Đạt | Không ghi vào bài, ảnh có sẵn; hỏi lại còn nháp |
| W3 | Đạt | Chữ SEO chặn thẻ, mã ký tự, shortcode; link do code chèn, `html.escape` |
| W4 | Đạt | Client chung (https, timeout, không đi theo chuyển hướng; nhóm 2) |
| A1 | Đạt | Danh sách bài, tiêu đề, bài viết đều trong khung dữ liệu (nhóm 5) |
| A2 | Đạt | Gợi ý meta, link được kiểm trước khi dùng; AI không viết JSON, không viết địa chỉ |
| A3 | Đạt | Không gửi bí mật vào lời dặn |
| U1 | Đạt | Chữ ngoài qua `escape_markdown`; schema qua `st.code` |
| U2 | Đạt, trừ SL-T106-1 | Trang có đăng nhập; còn câu khuyên «Quản trị viên» |
| U3 | Không áp dụng | |
| F1 | Đạt có điều kiện | `site_index` chưa kiểm `data/` là lối tắt (SL-T117-1) |
| F2 | Không áp dụng | |
| F3 | Đạt có điều kiện | Không `eval`, `pickle`; file cache kiểm theo kiểu cũ (LC-T129-1) |
| D1 | Đạt | pip-audit hôm nay 0 lỗ hổng |
| D2 | Đạt | `.gitignore` giữ `data/`, `.env` |
| D3 | Đạt | Móc kiểm: 0 kết nối ra ngoài máy (mục 6) |

## 7. Báo nhầm đã loại

- **detect-secrets «Basic Auth Credentials»** ở `app/views/write.py:2645` và `seo_app/wordpress/client.py:1023`:
  - cả hai là chữ mẫu «tên:mật-khẩu@» trong chú thích, giải thích vì sao app không chép `WORDPRESS_URL` ra màn hình;
  - cùng một mã băm (`be5b7743…`);
  - không phải bí mật; các biên bản T-038, T-041 đã gặp cùng chữ mẫu.
- **Đếm `xfail` bằng `grep` lần đầu:** lẫn cả câu chú thích có chữ «xfail». Danh sách đúng (chỉ dấu đang hiệu lực) dùng ở mục 2.

## Ghi nhận (không phải lỗi)

1. **`write_seo` gọi hàm riêng `client._own_draft`.** Chú thích trong mã đã ghi phải mở hàm công khai ở phiếu sửa client sau. Không đổi hành vi; gom vào T-131 nếu tiện.
2. **Bảng tiến độ ghi Giai đoạn 4 «khoảng 98%».** Phần còn lại đúng bằng 3 điều kiện ở mục 5.

## Phụ lục · Kiểm kê biên bản Lá Chắn các phiếu Giai đoạn 4

| Phiếu | Việc | Lá Chắn | Kiểm lại bằng Fable | Còn mở |
|---|---|---|---|---|
| T-033 | Thiết kế | — (báo cáo Thợ Máy) | — | Việc phía website câu 4A |
| T-036 | Meta, slug | ĐẠT CÓ ĐIỀU KIỆN | Nhóm 5: giữ | LC-T036-2, SL-T036-10, -11 (sửa khi tiện) |
| T-037 | Danh sách bài, cache | ĐẠT CÓ ĐIỀU KIỆN | Nhóm 5: giữ | LC-T129-1, SL-T117-1 (mới gom) |
| T-038 | Schema FAQ | ĐẠT CÓ ĐIỀU KIỆN | Nhóm 5: giữ | Lỗi 4 không chạm được |
| T-039 | Liên kết nội bộ | ĐẠT CÓ ĐIỀU KIỆN | Nhóm 5: giữ | QS ghi nhận |
| T-040 | Lời dặn meta, anchor | ĐẠT CÓ ĐIỀU KIỆN | Nhóm 5: giữ | QS 2 ghi nhận |
| T-041 | Bước SEO | ĐẠT CÓ ĐIỀU KIỆN | Nhóm 5: giữ | ĐK 3 chưa áp dụng |
| T-042 | Ghi SEO lên nháp | ĐẠT CÓ ĐIỀU KIỆN | Nhóm 5: giữ | Không |
| T-059 | Thử thật | ĐẠT CÓ ĐIỀU KIỆN | Nhóm 5: giữ | ĐK 2, 3 trong buổi thử thật chung |
| T-091 | Dọn client WordPress | ĐẠT CÓ ĐIỀU KIỆN | Nhóm 2: giữ | ĐK 4 trong buổi thử thật chung |
| T-095 | README bước SEO | ĐẠT | Nhóm 5: giữ | Không (QS 1 đã đóng) |
| T-106, T-108 | Trang Kết nối WordPress | ĐẠT CÓ ĐIỀU KIỆN | Nhóm 2: giữ | SL-T106-1 |
| T-112 | Đăng ngay chỉ khi SEO đã lên | ĐẠT CÓ ĐIỀU KIỆN (Fable + Opus) | — | LC-T094-44 (buổi thử thật) |

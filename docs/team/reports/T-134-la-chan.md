# Biên bản bảo mật T-134 · Rà soát đóng Giai đoạn 5 (kế hoạch, lịch, đăng bài)

> **Model:** Claude Opus 5.5 (Chỉ Huy B giao; chủ dự án quyết 04/11: hết hạn mức Fable thì Lá Chắn chạy Opus).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-134](../tickets/T-134-la-chan-ra-soat-giai-doan-5.md) · rà soát cả giai đoạn (việc 1–4), như T-093 (Giai đoạn 3) và [T-129](T-129-la-chan.md) (Giai đoạn 4) |
| Phạm vi | <ul><li>**Mã:** nhánh `team/T-134` tại `d4a015e`. Đây là `main` máy: nhánh tạo từ `00261e8`, tiến nhanh lên `d4a015e`, không có thay đổi riêng.</li><li>**Nền, không kiểm lại từ đầu:** biên bản Fable [T-116 nhóm 2](T-116-la-chan-nhom-2.md) (cùng lượt với [T-112](T-112-la-chan.md): WordPress, bộ dựng bài, bước Xuất bản) và [nhóm 4](T-116-la-chan-nhom-4.md) (Google Sheets, kế hoạch).</li><li>**Đối chiếu thêm:** thiết kế [T-094](T-094-tho-may.md); bảng «Việc bắt buộc khi làm Giai đoạn 5» trong `docs/team/board.md`; bảng «trước khi bật công tắc» của T-112; [kịch bản thử thật T-128](T-128-kich-ban-thu-that.md); biên bản Lá Chắn T-092, T-113, T-115, T-127, T-128, T-130, T-132; sổ rủi ro `security.md` mục 6; `TIEN-DO.md` mục 4.</li><li>**Đổi từ mốc Fable:** mã đổi trong vùng Giai đoạn 5 (`write.py`, `drafts.py`, `settings.py`, `plan.py`, `propose.py`, `client.py`, `sheets.py`, `service_account.py`) đều đã có Lá Chắn riêng ở T-112, T-092, T-130, T-132, T-127, T-121, T-124. `seo_app/publish/` không đổi dòng nào.</li><li>Không gọi website thật hay Google thật, không sửa mã.</li></ul> |
| Ngày | 2026-11-10 13:43–13:46 (dừng vì hết hạn mức); 16:03–16:20 (giờ máy +07) |
| **Kết luận** | **ĐÓNG CÓ ĐIỀU KIỆN.** <ul><li>Đủ 8 phiếu của thiết kế T-094, cùng các phiếu thêm sau (T-109, T-112, T-113, T-115, T-130).</li><li>0 Nghiêm trọng, 0 Cao, 0 Trung bình, **0 Thấp mới**.</li><li>Điều kiện của Fable nhóm 2, nhóm 4 và bảng «Việc bắt buộc» đã đóng hết, trừ buổi thử thật.</li><li>**2 điều kiện để đánh dấu xong:** T-131 (dọn kho dữ liệu phụ, đang làm) gộp `main`; cập nhật tài liệu.</li><li>**Buổi thử thật** (kịch bản T-128, kể cả Sheet bản sao) chưa làm. Nó **bắt buộc trước khi bật công tắc** Hẹn giờ/Đăng ngay và trước khi nối Sheet kế hoạch thật, nhưng không chặn đóng giai đoạn.</li></ul> |

## Tóm tắt (cho chủ dự án)

- **Phần «Kế hoạch, lịch, đăng bài» đã làm đủ theo thiết kế và an toàn để dùng.**
  - Gồm: nhận kế hoạch (tải file, dán chữ, Google Sheets), AI đề xuất để anh tick duyệt, đồng bộ Google Sheets, gửi nháp kèm ảnh lên website, màn hình xác nhận trước khi gửi.
  - Hẹn giờ và Đăng ngay đã có nhưng **đang tắt**.
- **Các lớp bảo vệ chính đều có và đã được kiểm lại:**
  - Phần mềm chỉ chuyển bài sang «hẹn giờ» hay «đăng» bằng một đường duy nhất, cho đúng bài nó vừa tạo, sau khi anh xác nhận đúng bản đã xem.
  - Bài bị sửa ngoài phần mềm thì không chuyển.
  - Không gửi trùng bài.
  - Mã lạ, shortcode trong bài bị lọc hết.
  - Tài khoản Google của phần mềm chỉ được sửa đúng một Sheet anh chia sẻ.
- **Còn 2 việc trước khi đánh dấu xong:**
  1. Phiếu dọn kho dữ liệu phụ (T-131, đang làm): siết cách kiểm file bài nháp, file kế hoạch lưu tạm trên máy. Đây là lỗi nhỏ, cùng phiếu với điều kiện đóng Giai đoạn 4.
  2. Cập nhật tài liệu tiến độ.
- **Trước khi bật Hẹn giờ/Đăng ngay:** làm buổi thử thật cùng Chỉ Huy theo kịch bản đã soạn (gồm cả thử trên một bản sao của Sheet kế hoạch). Tôi sẽ đọc báo cáo buổi thử trước khi bật.
- **Không có lỗi mới. Không có gì anh phải quyết ngay.**

## 1. Đối chiếu thiết kế T-094 và Lộ trình với `main` (việc 1)

| Hạng mục (thiết kế T-094, mục 6) | Phiếu | Trên `main` | Ghi chú |
|---|---|---|---|
| Bộ dựng bài cuối: Markdown → HTML an toàn, kiểm link, chặn nhúng | T-096 | Có | `seo_app/publish/`; không đổi từ mốc Fable |
| Client Google Sheets, kiểm file khóa tài khoản dịch vụ | T-097 | Có | Đường gọi cố định, ghi `RAW`; thêm phạm vi Search Console ở T-121 |
| Kế hoạch: khuôn, đọc CSV/TSV/chữ dán, đề xuất có AI | T-098 | Có | `seo_app/plan/`; thêm nguồn «Search Console» ở T-127 |
| Client hẹn giờ, đăng ngay, đọc trạng thái | T-099 | Có | `release_draft` là đường duy nhất tới `future`/`publish` |
| Đồng bộ kế hoạch, cache, nối nháp | T-100 | Có | `plan_cache.py`, `plan/sync.py` (xem T-131) |
| Lời dặn AI đọc kế hoạch | T-103 | Có | `[tasks.plan]` không tìm web |
| Trang Kế hoạch, Cài đặt → Google, trang Bài viết | T-101 | Có | Thay demo, giữ bố cục |
| Bước Xuất bản thật, màn hình xác nhận | T-102 | Có | Hẹn giờ/Đăng ngay **mặc định tắt**; công tắc ở Cài đặt, chỉ trong phiên (T-112) |
| README Kế hoạch, Google Sheets, Hẹn giờ/Đăng ngay | Thư Ký | Có | T-119; README mục 11 (T-112 lượt 4) |
| Thêm ngoài thiết kế | T-109, T-113, T-115, T-112, T-092, T-130, T-128 | Có | Trạng thái website về Sheet; nút cập nhật trạng thái; so `modified_gmt`; luật «Đăng ngay chỉ khi SEO, ảnh đại diện đã lên»; nháp bị xóa ở tab khác; sổ rủi ro `modified_gmt`, kịch bản thử thật |
| **Thử thật** (thiết kế mục 6, «Đi kèm»): Sheet bản sao, hẹn giờ một bài thật, Đăng ngay bài chủ dự án duyệt | Chỉ Huy, chủ dự án | **Chưa làm** | Kịch bản T-128 đã sẵn, gồm mục 3.4 «Sheet bản sao». Điều kiện trước khi bật (mục 5) |
| 6 câu hỏi thiết kế | — | Theo khuyến nghị A | Chủ dự án «có đề xuất thì làm theo đề xuất» (`TIEN-DO.md` mục 4, việc 7) |
| Ngoài phạm vi (thiết kế mục 8) | — | Chưa làm, đúng thiết kế | Cập nhật bài cũ, gộp bài, 301; hủy, đổi giờ hẹn từ app; vài dòng M7; FAQ lên website |
| Tài liệu | — | **Cũ** | <ul><li>Dòng Giai đoạn 5 trong Lộ trình `CLAUDE.md` chưa đánh dấu.</li><li>Bảng tiến độ ghi «khoảng 97%… Còn: thử thật…, Lá Chắn rà soát cả giai đoạn».</li></ul> |

## 2. Điều kiện Lá Chắn còn mở (việc 2)

**Đã đóng:**

| Mục | Bằng chứng |
|---|---|
| 8 dòng «Việc bắt buộc khi làm Giai đoạn 5» (`board.md`) | Fable nhóm 2 đối chiếu trên bộ dựng và bước Xuất bản (giữ cả 44 điều kiện LC-T094). `seo_app/publish/` không đổi từ đó |
| SL-T112-1 (phần Chặn của LC-T094-39) | T-112 lượt 3 |
| T-112 mục B2 (README: SL-T112-2, -3, -4, G1) | Thư Ký lượt 4 (`97d0bc4`) |
| T-112 mục B5 (sổ rủi ro: ba giới hạn `modified_gmt`) | T-128 (gộp `09ac0ab`; chủ dự án đồng ý 04/11) |
| SL-T106-1, SL-T108-1 (trang Kết nối, README) | T-132; T-112 Thư Ký lượt 2 |
| LC-T113-2 (`plan_cache._parse_time`) | T-118 |
| LC-T094-43 (README mục Google) | README dòng 575: chỉ chia sẻ đúng Sheet cho email tài khoản dịch vụ, quyền Người chỉnh sửa, không bật «Bất kỳ ai có đường liên kết» |
| T-092 điều kiện B1, B3 (giữ trạng thái gửi khi xóa nháp đã gửi; nhắc khi xóa) | T-130 (Lá Chắn ĐẠT) |
| T-092 điều kiện B2 (duyệt R5) | Chỉ Huy duyệt khi gộp (`9952ba1`) |
| T-127 điều kiện B2, B3 (README, sổ rủi ro LC-T120-24) | T-126; `03b5881` (chủ dự án đồng ý 10/11) |

**Còn mở:**

| Mục | Mức | Việc |
|---|---|---|
| **LC-T094-44, T-097 ĐK 5:** buổi thử thật | Thử thật | <ul><li>Kịch bản T-128: mục (a)–(g) (quyền `publish_posts`, `modified_gmt` sau ghi SEO, múi giờ, trình soạn, WP-Cron, câu báo, `srcset` và «<» trong SiteSEO), cùng mục 3.4 «Sheet bản sao».</li><li>**Bắt buộc trước khi bật công tắc** Hẹn giờ/Đăng ngay, và trước khi nối Sheet kế hoạch thật. Lá Chắn đọc báo cáo buổi thử trước khi bật.</li></ul> |
| **SL-T117-1** (`xfail` còn ở `tests/test_soi_loi_t117.py`); **LC-T129-1** (kho nháp kiểm file theo kiểu cũ); cùng mẫu **LC-T122-1** ở `plan_cache` | Thấp | Phiếu **T-131** (dọn kho dữ liệu phụ) đang làm lượt 2, sau đó Lá Chắn đầy đủ. Điều kiện 1 (mục 5) |
| T-112 mục B3: ghi dấu «SEO chưa lên» (`SendState.seo_missing`) | Khuyến nghị | Chưa làm; không chặn. Nên làm cùng phiếu đầu tiên đụng trạng thái gửi |
| T-127 điều kiện B1 (thử «Đưa vào kế hoạch» với Google thật) | Thử thật | Thuộc Giai đoạn 6 (kịch bản T-133) |

**Việc phía website** (chủ dự án quyết 28/10 để nguyên, `TIEN-DO.md` mục 4): 2 mật khẩu ứng dụng cũ trên tài khoản quản trị, các snippet tạm trong Code Snippets, xác nhận các đường `/prometal/v1/*`, `/code-snippets/*`.
- Không thuộc phần mềm, vì app chỉ dùng tài khoản Biên tập viên riêng.
- Nhưng mỗi mật khẩu ứng dụng của tài khoản quản trị có toàn quyền website. **Khuyến nghị** chủ dự án xem lại trước khi bật Đăng ngay.

**Sổ rủi ro:** các dòng có sẵn đã phủ rủi ro dùng thật của Giai đoạn 5:
- 28/10: proxy/chứng chỉ cho `requests`, `google-auth`; quyền `unfiltered_html` của Biên tập viên;
- 30/10: shortcode khi tự sửa trên website;
- 04/11: ba giới hạn `modified_gmt`;
- 10/11: LC-T120-24.

Không cần dòng mới.

## 3. Rủi ro khi người dùng thật dùng (việc 3)

**a. Trang Kế hoạch, Google Sheets**

- **Lớp chặn:**
  - tài khoản dịch vụ chỉ được chia sẻ đúng một Sheet, file khóa để ngoài dự án;
  - client chỉ gọi đường cố định, ghi `RAW` nên ô công thức không chạy;
  - kiểm xung đột khi hai máy cùng sửa;
  - từ khóa từ Sheet bị vô hiệu thẻ khung trong lời dặn AI (SL-7);
  - đề xuất AI phải tick rồi bấm «Áp dụng» mới ghi.
- **Còn lại:**
  - Lộ file khóa thì người có nó sửa được đúng Sheet đó (phạm vi nhỏ nhất có thể).
  - Cache kế hoạch trên máy còn chờ T-131 siết cách kiểm file.
  - Chưa thử với Sheet thật (mục 3.4 kịch bản).

**b. Gửi nháp**

- **Lớp chặn:**
  - mặc định nháp;
  - khóa «đang gửi» ghi trong file nháp kiểu «so rồi đặt», hai tab không cùng qua (T-086, T-089, T-092, T-130);
  - ảnh dựng lại, chỉ giữ GPS, ngày chụp, hãng, đời máy;
  - `sanitize_html` cho toàn bộ HTML; shortcode thành mã ký tự;
  - màn hình xác nhận liệt kê mọi link.
- **Còn lại:** quyền `unfiltered_html` của tài khoản Biên tập viên (sổ rủi ro 28/10); kho nháp chờ T-131.

**c. Hẹn giờ, Đăng ngay** (sau buổi thử thật)

- **Lớp chặn:**
  - một đường `release_draft`, chỉ cho nháp client vừa tạo trong lần gửi;
  - xác nhận đúng bản đã xem (mã băm);
  - so `modified_gmt` ngay trước lệnh: bài bị sửa ngoài thì không chuyển;
  - «Đăng ngay» chỉ khi SEO và ảnh đại diện đã lên;
  - công tắc ở Cài đặt mặc định tắt, chỉ giữ trong phiên.
- **Còn lại:** WP-Cron có chạy đúng giờ không, trình soạn website, ghi SEO có đổi `modified_gmt` không. Đều là mục của buổi thử thật.

## 4. Lỗi tìm thấy

Không phát hiện lỗi mới.

## 5. Kết luận giai đoạn và đề xuất (việc 4)

**ĐÓNG CÓ ĐIỀU KIỆN.**

Phần mềm làm đủ Giai đoạn 5 theo thiết kế. Hai điều kiện trước khi đánh dấu `[x]` trong Lộ trình:

1. **T-131 gộp `main`**, sau Lá Chắn đầy đủ. Phiếu đóng SL-T117-1, LC-T129-1 và mẫu LC-T122-1 ở `plan_cache`. Đã có phiếu, đang làm lượt 2; cùng là điều kiện 2 của Giai đoạn 4.
2. **Cập nhật tài liệu khi đánh dấu:**
   - dòng Giai đoạn 5 trong Lộ trình `CLAUDE.md`;
   - bảng tiến độ trong `board.md`, `TIEN-DO.md`;
   - ghi rõ việc mang sang.

**Không chặn đóng, nhưng bắt buộc trước khi bật công tắc Hẹn giờ/Đăng ngay:** buổi thử thật theo kịch bản T-128, mục (a)–(g) và mục 3.4 «Sheet bản sao». Lá Chắn đọc báo cáo buổi thử trước khi bật.

**Không bắt buộc:**
- `SendState.seo_missing` (T-112 mục B3);
- việc phía website ở mục 2.

**Mang sang** (thiết kế mục 8):
- cập nhật bài cũ, gộp bài, 301;
- hủy, đổi giờ hẹn từ app;
- vài dòng M7;
- FAQ lên website.

Không cần phiếu mới.

## 6. Kết quả công cụ quét, test

| Công cụ | Kết quả | Ghi chú |
|---|---|---|
| pytest | 21 file liên quan (8 file test Lá Chắn T-096 → T-113, bộ dựng, Markdown, hẹn giờ/đăng, Google Sheets, đồng bộ kế hoạch, cache kế hoạch, trạng thái gửi, T-102, T-112, T-115, T-127, T-130): **1.066 qua, 0 hỏng**; 11 phút 7 giây | <ul><li>Chỉ test liên quan, theo tin giao.</li><li>Toàn bộ 24.204 ca đã qua trên đúng `d4a015e` (Chỉ Huy chạy khi gộp T-127, T-126).</li><li>Móc kiểm `sys.addaudithook`: 0 kết nối ra ngoài máy, 0 lần mở `.env` ngoài thư mục tạm của pytest.</li></ul> |
| pip-audit | Chạy lại hôm nay: 69 gói; nguồn PyPI và OSV: **No known vulnerabilities found** | `uv.lock`, `pyproject.toml` không đổi từ lần quét 05/11 |
| detect-secrets (`PYTHONUTF8=1`) | 21 file vùng Giai đoạn 5 (`plan/*`, `sheets.py`, `service_account.py`, `publish/*`, `plan_cache.py`, `drafts.py`, `client.py`, `plan.py`, `home.py`, `write.py`, `settings.py`, `.env.example`, README): **0 bí mật thật**; 2 báo nhầm (chữ mẫu «tên:mật-khẩu@» trong chú thích, như T-129, T-132); mồi bị bắt | Chạy trên bản chép, đường dẫn tương đối, `--all-files` |

**Danh sách kiểm tra** (vùng Giai đoạn 5):

| Mã | Kết quả | Ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets 0 bí mật thật |
| S2 | Đạt | Câu lỗi cố định ở client WordPress, Sheets (nhóm 2, 4) |
| S3 | Đạt | `.env.example` có đủ biến Google, chú thích |
| W1 | Đạt | Mặc định nháp; một đường tới `future`/`publish`, có xác nhận, có test; công tắc tắt |
| W2 | Đạt | Chỉ ghi vào bài, ảnh app vừa tạo; so `modified_gmt` |
| W3 | Đạt | `sanitize_html` toàn bộ; shortcode thành mã ký tự; không autolink |
| W4 | Đạt | https, timeout, không đi theo chuyển hướng |
| A1 | Đạt | Kế hoạch, từ khóa từ Sheet trong khung dữ liệu (SL-7) |
| A2 | Đạt | Đề xuất AI phải tick, «Áp dụng»; `[tasks.plan]` không tìm web |
| A3 | Đạt | Chữ kế hoạch dò số điện thoại, email trước khi gửi AI |
| U1 | Đạt | Chữ ngoài qua escape; bảng qua `safe_rows` khi xuất CSV |
| U2 | Đạt | Mọi trang kiểm đăng nhập |
| U3 | Không áp dụng | |
| F1 | Đạt có điều kiện | Kho nháp, cache kế hoạch chưa kiểm `data/` là lối tắt (SL-T117-1 → T-131) |
| F2 | Đạt | Ảnh qua đường xử lý của Giai đoạn 3 |
| F3 | Đạt có điều kiện | Không `eval`, `pickle`; kho nháp kiểm file theo kiểu cũ (LC-T129-1 → T-131) |
| D1 | Đạt | pip-audit hôm nay 0 lỗ hổng |
| D2 | Đạt | `.gitignore` giữ `data/`, `.env`, file khóa ngoài dự án |
| D3 | Đạt | Móc kiểm: 0 kết nối ra ngoài máy |

## Báo nhầm đã loại

**detect-secrets «Basic Auth Credentials»** ở `app/views/write.py:2692` và `seo_app/wordpress/client.py:1030`:
- là chữ mẫu «tên:mật-khẩu@» trong chú thích;
- dòng có từ trước, chỉ dời số dòng;
- đã ghi ở biên bản T-129 mục 7 và T-132.

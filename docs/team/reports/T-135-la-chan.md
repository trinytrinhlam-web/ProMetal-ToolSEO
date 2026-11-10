# Biên bản bảo mật T-135 · Rà soát đóng Giai đoạn 6 (theo dõi bài qua Google Search Console)

> **Model:** Claude **Opus 5.5** (dòng «You are powered by»: Opus 5.5). Chỉ Huy B giao chạy Opus 5.5; chủ dự án quyết ngày 04/11: hết hạn mức Fable thì Lá Chắn chạy Opus 5.5, ghi rõ model.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-135](../tickets/T-135-la-chan-ra-soat-giai-doan-6.md) · rà soát cả giai đoạn (việc 1–4), như T-093 (Giai đoạn 3), T-129 (Giai đoạn 4) |
| Phạm vi | <ul><li>**Mã:** nhánh `team/T-135` tạo từ `main` `d4a015e` (đã có T-120 → T-127, T-133). Chỉ đọc, không sửa mã, không gọi Google hay website thật.</li><li>**Nền, không kiểm lại từ đầu:** biên bản Lá Chắn T-120 (thiết kế), T-121, T-124, T-125, T-127 (Fable), T-122, T-123, T-126, T-133 (Opus).</li><li>**Đối chiếu:** thiết kế [T-120](T-120-tho-may.md); 7 câu trả lời của chủ dự án ngày 04/11 (`CLAUDE.md`); Lộ trình `CLAUDE.md`, `TIEN-DO.md`; sổ rủi ro `docs/team/security.md`; README mục 15; kịch bản thử thật [T-133](T-133-kich-ban-thu-that-google.md).</li><li>**Mã Giai đoạn 6:** `seo_app/google/search_console.py`, `service_account.py` (phạm vi), `seo_app/storage/search_cache.py`, gói `seo_app/tracking/` (`model`, `periods`, `match`, `stats`, `flags`, `keywords`, `refresh`), `app/views/tracking.py`, mục Search Console của `app/views/settings.py`, `seo_app/env_file.py` (`GSC_SITE_URL`), `seo_app/plan/propose.py` (`google_keyword`, `from_google_keywords`)</li></ul> |
| Ngày | 2026-11-10 (16:03–16:20, giờ máy +07) |
| **Kết luận** | **ĐÓNG CÓ ĐIỀU KIỆN.** <ul><li>Mọi hạng mục của thiết kế T-120 và cả 7 câu trả lời ngày 04/11 đã có trên `main`. Cả **24 điều kiện LC-T120** đều đã có biên bản Lá Chắn kiểm đạt, có test chứng minh.</li><li>0 Nghiêm trọng, 0 Cao, 0 Trung bình, **0 Thấp mới**. Không còn lỗi Lá Chắn nào mở trong vùng Giai đoạn 6.</li><li>**Điều kiện để đánh dấu xong** (mục 5): cập nhật tài liệu Lộ trình, `TIEN-DO.md`. Còn lại, đã có chỗ theo dõi, không chặn đóng: buổi thử thật với Google (kịch bản T-133), ca Mac của T-125, phần `plan_cache` trong phiếu dọn T-131.</li></ul> |

## Tóm tắt (cho chủ dự án)

- **Phần theo dõi bài trên Google đã làm đủ theo thiết kế và an toàn để dùng.** Gồm:
  - trang **📈 Theo dõi**: lượt hiển thị, lượt click, vị trí, từ khóa từng bài, so hai kỳ, nhãn «Tụt hạng»…;
  - mục **Search Console** ở Cài đặt (tìm và lưu thuộc tính, kiểm tra kết nối);
  - nút **«Đưa vào kế hoạch»**.
- **Phần mềm chỉ đọc số liệu Google**, không sửa gì trên Search Console:
  - quyền xin Google chỉ là «đọc Search Console», và anh chỉ cấp quyền «Hạn chế»;
  - phần mềm chỉ gọi Google khi anh bấm nút, không tự gọi khi mở trang, không chạy ngầm;
  - mỗi lần bấm gửi tối đa 20 lệnh, mỗi lúc chỉ một lần lấy số chạy.
- **Chữ từ Google được coi là chữ lạ:**
  - từ khóa người khác gõ hiện như chữ thường, không bao giờ thành link;
  - từ khóa không gửi cho AI, không ghi lên Google Sheets, trừ khi anh tự chọn «Đưa vào kế hoạch» rồi «Áp dụng». Rủi ro nhỏ còn lại của đường này anh đã đồng ý ghi sổ ngày 10/11.
- **Đúng 7 câu anh trả lời ngày 04/11**: trang mới giữa Kế hoạch và Cài đặt; chọn thuộc tính bằng nút; không hiện số tạm; không ghi số lên Google Sheets; ngưỡng nhãn mặc định; kiểm lập chỉ mục bằng tay trong Search Console; có nút «Đưa vào kế hoạch».
- **Không có lỗi mới.** Còn lại, đã có chỗ theo dõi:
  1. buổi thử với Search Console thật (kịch bản T-133). Tới khi Lá Chắn đọc kết quả buổi thử, số trên trang chỉ để xem làm quen, như README đã ghi;
  2. một ca test chỉ chạy được trên Mac;
  3. một chỗ dọn nhỏ ở file kế hoạch lưu tạm (phiếu T-131 đang làm).
- **Việc của anh:** khi rảnh, làm README mục 15 bước 1–3 phía Google, rồi ngồi cùng Chỉ Huy buổi thử thật.

## 1. Đối chiếu Lộ trình, thiết kế T-120 và 7 câu trả lời với `main` (việc 1)

| Hạng mục (thiết kế T-120) | Phiếu | Trên `main` | Ghi chú |
|---|---|---|---|
| Client Search Console chỉ đọc: phạm vi `webmasters.readonly`, 2 lệnh cố định (`sites`, `searchAnalytics/query`), kiểm từng dòng, câu lỗi cố định | T-121 | Có | `search_console.py`; `service_account.py:50` |
| Cache số liệu (16 tháng, kiểm khi đọc, mã băm phạm vi, chặn `data/` là liên kết) | T-122 | Có | `search_cache.py` |
| Lõi tính toán: kỳ ngày, khớp địa chỉ với bài và dòng kế hoạch, cộng dồn, nhãn, từ khóa | T-123 | Có | gói `seo_app/tracking/` |
| Lấy số liệu (chia đoạn, số tạm, chặn bấm lại, một lần chạy), «Kiểm tra», tìm và lưu `GSC_SITE_URL` | T-124 | Có | `refresh.py`, `env_file.py` |
| Trang «📈 Theo dõi», mục Search Console trong Cài đặt | T-125 | Có | `app/views/tracking.py`, `settings.py` |
| README «Theo dõi trên Google», chú thích `.env.example` | T-126 | Có | README mục 15 |
| «Đưa vào kế hoạch» (câu 7 = B) | T-127 | Có | `propose.py` (`google_keyword`), `tracking.py`, `plan.py` |
| Thử thật | Kịch bản T-133 | **Chưa làm** | Điều kiện còn lại (mục 5) |
| Lá Chắn rà cả Giai đoạn 6 | T-135 | Biên bản này | |
| Không thư viện mới (thiết kế 2.2) | — | Đúng | `uv.lock`, `pyproject.toml` không đổi từ `29499dd` (trước Giai đoạn 6) |

**7 câu trả lời của chủ dự án ngày 04/11:**

| Câu | Trả lời | Trên `main` |
|---|---|---|
| 1 · Đặt ở đâu | A: trang mới giữa Kế hoạch và Cài đặt | `app/main.py:28-30`: Kế hoạch → Theo dõi → Cài đặt |
| 2 · Chọn thuộc tính | A: tìm rồi bấm chọn, app ghi `.env` | «🔎 Tìm thuộc tính», «Lưu thuộc tính đã chọn»; `set_gsc_site_url` chỉ nhận mục vừa nhận từ `sites` (`env_file.py:450-465`, LC-T120-12) |
| 3 · Số tạm | A: không hiện | Chỉ tính số đã chốt; câu «… ngày gần nhất còn là số tạm, chưa tính.» |
| 4 · Ghi Sheets | A: không | `seo_app/tracking/`, `app/views/tracking.py` không có lệnh ghi Sheets nào (grep) |
| 5 · Ngưỡng nhãn | A: mặc định | `flags.py:32-41`: 30 lượt hiển thị, 3 bậc, trang 1 (≤ 10), 10 click, 14 ngày, 200 lượt hiển thị, CTR 1%, 100 lượt hiển thị |
| 6 · Kiểm lập chỉ mục | A: để sau, kiểm bằng tay | Không có lệnh URL Inspection (LC-T120-7); README nhãn 👻 hướng dẫn chủ dự án tự kiểm trong Search Console |
| 7 · Đưa vào kế hoạch | B: có nút | T-127; sổ rủi ro LC-T120-24 (chủ dự án đồng ý 10/11, `03b5881`) |

**Tài liệu cũ** (sửa khi đánh dấu xong, điều kiện 1):
- `CLAUDE.md`, Lộ trình (dòng 102): Giai đoạn 6 còn ghi «Giao diện demo hiện chưa có trang này; khi làm thì hỏi chủ dự án đặt ở đâu trong menu».
- `TIEN-DO.md` dòng 33: «| 6 | Theo dõi thứ hạng qua Search Console | ⚪ Chưa làm».

## 2. Điều kiện Lá Chắn (việc 2)

### 2.1 24 điều kiện LC-T120: **đủ cả**

| Mã | Nội dung ngắn | Kiểm đạt ở biên bản |
|---|---|---|
| LC-T120-1 | Một phạm vi `webmasters.readonly`, phạm vi chỉ từ hằng | T-121 (Fable) |
| LC-T120-2 | Danh sách lệnh cố định, thân đủ khóa và đủ giá trị | T-121 |
| LC-T120-3 | Chỉ máy chủ Google cố định; không theo chuyển hướng; giờ chờ, cỡ câu trả lời | T-121 |
| LC-T120-4 | Câu lỗi cố định, mã lý do từ danh sách ASCII | T-121 |
| LC-T120-5 | Kiểm từng dòng, chặn `NaN` ở bộ đọc JSON | T-121 |
| LC-T120-6 | Thuộc tính phủ website; từ chối `http://`, staging; bỏ dòng ngoài tiền tố | T-121, T-123 |
| LC-T120-7 | Không lệnh ghi, không URL Inspection | T-121 |
| LC-T120-8 | ≤ 20 lệnh mỗi lần bấm, thử lại 429 một lần | T-121, T-124 |
| LC-T120-9 | Cache kiểm như `plan_cache`; `dir_has_link` từ đầu | T-122 (LC-T122-1 sửa ở T-124) |
| LC-T120-10 | Mốc giờ kiểm năm, bắt `OverflowError`, `ValueError` | T-122, T-123, T-124 |
| LC-T120-11 | Chữ Google chỉ hiện chữ thuần, qua `safe_rows` | T-123 (phần lõi), T-125 |
| LC-T120-12 | `GSC_SITE_URL` chỉ nhận mục vừa nhận từ `sites`, ghi nguyên tử | T-124, T-125 |
| LC-T120-13 | Từ khóa không vào AI, không ghi Sheets (trừ đường LC-T120-24) | T-124, T-125, T-127 |
| LC-T120-14 | Trang kiểm đăng nhập, không gọi mạng khi mở, client mới mỗi lần bấm | T-125 |
| LC-T120-15 | Test không gọi mạng; trang mới trong `PAGES` | mọi phiếu; lại ở mục 6 |
| LC-T120-16 | Không mạo danh (`with_subject`), không phạm vi rộng | T-121 |
| LC-T120-17 | «Phủ website» so theo từng phần tên miền | T-121 (lại ở Lá Chắn T-126 phần 1: 21 ca, 0 sai) |
| LC-T120-18 | Test chứng minh từng lớp vận chuyển được nối đúng | T-121 |
| LC-T120-19 | Đường dẫn đã giải mã, tên máy qua `clean_text`, không thành link | T-123 (phần lõi), T-125 |
| LC-T120-20 | Biểu đồ dựng từ khuôn cố định, chỉ số và ngày | T-125 |
| LC-T120-21 | Không gọi mạng khi mở trang Theo dõi và Cài đặt | T-124, T-125 |
| LC-T120-22 | Mỗi lúc một lần lấy số liệu (khóa cấp module) | T-124 |
| LC-T120-23 | Báo biến môi trường `GSC_SITE_URL` đè `.env`, kể cả rỗng | T-124, T-125 (lại ở T-126 phần 3: `config.py:125`) |
| LC-T120-24 | Từ khóa sang Kế hoạch: lọc chặt, ≤ 10, không AI, chỉ ghi khi «Áp dụng» | T-127 (Fable); sổ rủi ro, chủ dự án đồng ý 10/11 |

### 2.2 Điều kiện riêng từng biên bản

**Đã đóng:**

| Mục | Đóng ở |
|---|---|
| T-121 B.1 (một client mỗi lần bấm, khóa cấp module, giữ phần đã ghi khi đủ 20 lệnh, ngày theo `today_pacific`, câu lỗi qua `escape_markdown`), B.2 (gom 3 hàm chuẩn hóa `WORDPRESS_URL`) | T-124 (Fable) |
| T-121 B.3 (hiện chữ thuần, cảnh báo quyền cao hơn «Hạn chế», thuộc tính không phủ website hay chưa xác minh không chọn được) | T-125 (Fable) |
| T-121 B.5 (sửa lớp vận chuyển thì chạy test cả hai client) | Ghi trong docstring `search_console.py`; lô test mục 6 chạy cả `test_google_sheets.py` |
| LC-T122-1, LC-T122-2 (Thấp), góp ý G1, G2, mục 8.3 của T-122 | T-124 (Fable) |
| T-122 mục 8.2 (câu `SearchCacheError`, nút «Xóa bản lưu tạm», không `st.cache_data`) | T-125 |
| LC-T123-1 (Thấp, link bài viết hoa tên máy), T-123 mục 7.2, 7.3 (chỉ hiện nhãn đã làm sạch, không dựng link từ khóa) | T-124, T-125 |
| T-124 B.1 (giao diện), B.2 (README) | T-125; T-126 phần 3 |
| T-124 B.4, phần docstring `set_gsc_site_url` | Docstring nay ghi rõ chỉ nhận mục vừa nhận từ `sites` và qua `validate_gsc_site_url` (`env_file.py:453-458`) |
| T-125 B.1 (T-127 theo LC-T120-24), B.4 (câu U1 trong `security.md`) | T-127 (Fable); T-126 lượt cuối |
| T-126 điều kiện 1 (chủ dự án xác nhận dòng sổ rủi ro LC-T120-24), điều kiện 2 (thứ tự gộp) | `03b5881` (chủ dự án đồng ý 10/11); gộp T-127 (`e96202a`) trước T-126 (`09a480f`) |
| T-127 B.2 (README), B.3 (sổ rủi ro) | T-126 lượt cuối; `03b5881` |
| T-133 G1 (đoạn lệnh ca 7 chỉ in câu lỗi của phần mềm), G2 (tên nút theo `main`) | T-126 lượt cuối |

**Còn mở, đã có chỗ theo dõi:**

| Mục | Loại | Ở đâu |
|---|---|---|
| T-121 B.4 (a)–(d), T-124 B.3, T-125 B.2, T-127 B.1: quyền «Hạn chế» đọc được `sites`, `query`; `metadata` thật của đoạn mới và đoạn cũ; mã lý do 403; dòng bị bỏ; số lệnh mỗi nút; chữ thật hiện chữ thuần; cảnh báo quyền cao; «Đưa vào kế hoạch» chỉ ghi Sheet sau «Áp dụng» | Chờ buổi thử thật Google | Kịch bản T-133 (Lá Chắn duyệt 07/11, thêm ca 6b 10/11). Lá Chắn đọc bảng kết quả trước khi dùng số để quyết việc |
| T-125 B.3: `test_t125_tho_may.py::test_stamp_of_a_folder_or_link_is_none`, phần symlink | Chờ Mac | Cùng các ca Mac đang treo (T-063 ĐK 3); chủ dự án chưa có Mac |
| T-122 mục 8.4, T-124 B.4: `plan_cache._is_healthy` cùng mẫu LC-T122-1 | Thấp, phiếu dọn | Phiếu T-131 mục 3 (đang làm, Lá Chắn T-129 phiếu A) |
| T-133 G3 (mã lý do 403 «hết hạn mức» không nên cố tạo ra), G4 (số lệnh lần đầu chỉ suy ra, màn hình không hiện) | Ghi nhận | Chấp nhận như kịch bản ghi; muốn số chính xác thì phiếu giao diện sau hiện `RefreshReport.requests` |
| T-123 G1 (nhãn «Trang khác» có thể trùng nhãn trang chủ), các ca test ghim G2 của T-122, T-123 | Góp ý | Không phải lỗi; gom vào phiếu dọn nếu tiện |

## 3. Rủi ro khi người dùng thật dùng (việc 3)

**a. Tài khoản dịch vụ, file khóa.**
- **Lớp chặn:**
  - client Search Console xin đúng một phạm vi chỉ đọc, từ chối mọi phạm vi khác và ủy quyền toàn miền (LC-T120-1, -16);
  - phía Google, README chỉ bảo cấp quyền «Hạn chế», chỉ thêm email vào đúng thuộc tính của website, gặp 403 thì không nâng quyền;
  - Cài đặt cảnh báo khi quyền cao hơn «Hạn chế».
- **Còn lại:**
  - Lộ file khóa thì người có nó đọc được số liệu Search Console (và Sheet kế hoạch) của các thuộc tính đã thêm email. Cách giảm: README mục 14 (cất file khóa, đổi khóa khi lộ), mục 15 (chỉ một thuộc tính, quyền «Hạn chế»).
  - «Hạn chế» có đủ để đọc số không: chờ buổi thử. Hỏng thì theo hướng an toàn (lỗi 403, phần mềm dừng).

**b. Chữ từ Google** (từ khóa người lạ gõ, đường dẫn, tên máy).
- **Lớp chặn:**
  - làm sạch (`clean_text`, `page_label`) rồi mới `escape_markdown`;
  - bảng qua `safe_rows`, biểu đồ chỉ có số và ngày;
  - không bao giờ thành link, không vào AI, không ghi Sheets (LC-T120-11, -13, -19, -20).
  - `security.md` U1 nay ghi luật «làm sạch trước `escape_markdown`» cho mọi chữ ngoài mới.
- **Còn lại:** không thấy.

**c. «Đưa vào kế hoạch»** (từ khóa thành dòng kế hoạch, rồi vào lời dặn AI khi viết bài từ dòng đó).
- **Lớp chặn:**
  - bộ lọc chặt `google_keyword` (chỉ chữ tiếng Việt hoặc a–z, số, khoảng trắng, «-», ≤ 80 ký tự; không số điện thoại, email, chữ web);
  - người dùng tick tối đa 10, duyệt đề xuất, bấm «Áp dụng» mới ghi Sheet;
  - khi viết bài, từ khóa nằm trong khung dữ liệu của lời dặn, dàn ý và bài đều qua người duyệt.
- **Còn lại:** một câu lệnh viết toàn chữ thường, ngắn vẫn lọt bộ lọc. Mức Thấp; chủ dự án đã đồng ý ghi sổ (`security.md` §6, 10/11).

**d. Gọi Google, hạn mức.**
- **Lớp chặn:**
  - không gọi khi mở trang (LC-T120-21);
  - ≤ 20 lệnh mỗi lần bấm, thử lại 429 một lần;
  - mỗi lúc một lần lấy số (LC-T120-8, -22);
  - bấm lại trong 10 phút không hỏi Google.
- **Còn lại:** không thấy.

**e. Bản lưu tạm trên máy** (`data/`, có từ khóa người khác gõ).
- **Lớp chặn:**
  - kiểm cấu trúc file khi đọc, mã băm phạm vi, chặn `data/` là liên kết (LC-T120-9);
  - giữ tối đa 16 tháng;
  - nút «Xóa bản lưu tạm»;
  - không rời máy (câu 4 = A).
- **Còn lại:** người dùng chung máy hay chương trình lạ trên máy đọc được file này, cùng lớp với các bản lưu tạm khác («phải chiếm máy trước»). Google đã ẩn từ khóa hiếm và từ khóa có thông tin cá nhân.

**f. Thuộc tính, `.env`.**
- **Lớp chặn:**
  - chỉ lưu mục vừa tìm thấy và dùng được, kiểm chặt, ghi nguyên tử;
  - báo khi biến môi trường đè, kể cả rỗng (LC-T120-12, -23);
  - thuộc tính staging, `http://`, tên miền na ná bị từ chối (LC-T120-6, -17).
- **Còn lại:** không thấy.

## 4. Lỗi tìm thấy

Không có lỗi mới (0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp). Không còn lỗi Lá Chắn nào mở trong vùng Giai đoạn 6.

## 5. Kết luận giai đoạn (việc 4)

**ĐÓNG CÓ ĐIỀU KIỆN.**

Phần mềm làm đủ các hạng mục Giai đoạn 6 của thiết kế T-120, đúng 7 câu trả lời ngày 04/11, an toàn để dùng. Điều kiện trước khi đánh dấu `[x]` trong Lộ trình:

1. **Cập nhật tài liệu khi đánh dấu** (Chỉ Huy, Thư Ký):
   - dòng Giai đoạn 6 trong Lộ trình `CLAUDE.md` (bỏ câu «Giao diện demo hiện chưa có trang này…»);
   - `TIEN-DO.md` dòng 33;
   - bảng tiến độ;
   - ghi rõ những gì còn chờ (dưới).

**Không chặn đánh dấu, đã có chỗ theo dõi:**
- **Buổi thử thật với Google** (kịch bản T-133, cả ca 6b). Tới khi Lá Chắn đọc bảng kết quả, số trên trang chỉ để làm quen, không dùng để quyết việc; README mục 15 đã nói vậy.
- **Ca Mac** của T-125 (B.3), cùng các ca Mac đang treo.
- **`plan_cache._is_healthy`** trong phiếu T-131.

**Đề xuất phiếu:** không cần phiếu mới. Góp ý nhỏ (T-123 G1, các ca test ghim) gom vào phiếu dọn sau nếu tiện. Phần ngoài phạm vi theo thiết kế T-120 mục 7 (Google Analytics 4, loại tìm kiếm khác, kiểm lập chỉ mục trong app, ghi tab «TheoDoi») vẫn mang sang. Mỗi phần cần hỏi chủ dự án và qua Lá Chắn riêng nếu làm.

## 6. Kết quả công cụ quét, test

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pytest | 27 file liên quan: client Search Console, file khóa, client Sheets (lớp vận chuyển dùng chung, LC-T120-18), cache, lõi theo dõi (7 file), lấy số liệu, `GSC_SITE_URL`, trang Theo dõi, Cài đặt → Google, «Đưa vào kế hoạch», bộ đề xuất kế hoạch, bộ Soi Lỗi T-121 → T-127, `test_app_pages.py` (mở mọi trang). Kết quả: **1.914 qua, 5 bỏ qua, 0 hỏng**; 6 phút 56 (16:08–16:15). 5 ca bỏ qua là ca cần quyền tạo symlink trên Windows (Developer Mode) hay ca chỉ dành cho Mac/Linux, đúng ý T-125 B.3 | Chỉ test liên quan, không chạy toàn bộ pytest (theo giao việc); máy mới tạo `.venv` bằng `uv sync --frozen` |
| Móc kiểm mạng (`sys.addaudithook`, plugin riêng trong thư mục nháp, ghi lại khi chạy cùng lô test) | 1.246 sự kiện:<ul><li>430 lần `connect` và 430 lần `bind` đều tới `127.0.0.1`: cặp socket nội bộ của asyncio trong test giao diện (ngoại lệ T-027 của `conftest`);</li><li>1 lần `bind(('::1', 0))` lúc nhập urllib3, để thử máy có IPv6 không;</li><li>384 lần mở `.env`, tất cả trong thư mục tạm của pytest, không đụng `.env` thật;</li><li>1 tiến trình con: ca «nhật ký nóng» của Soi Lỗi T-122 (Python chỉ chạy SQLite trên file tạm), như biên bản T-122 đã ghi.</li></ul>**0 kết nối ra ngoài máy, 0 lần tra tên** | ✔ |
| pip-audit | Chạy hôm nay (`uv export` rồi `uvx pip-audit -r … --no-deps --disable-pip`): 69 gói, **No known vulnerabilities found** | `uv.lock`, `pyproject.toml` không đổi từ `29499dd` |
| bandit (`PYTHONUTF8=1`; `search_console.py`, `service_account.py`, `search_cache.py`, `seo_app/tracking/`, `app/views/tracking.py`, `propose.py`, `env_file.py`; 6.257 dòng) | 0 High, 0 Medium, 9 Low báo nhầm (mục 7) | ✔ |
| detect-secrets (`PYTHONUTF8=1`; chép 15 file mã Giai đoạn 6, README, `.env.example`, `security.md`, kịch bản T-133 ra thư mục ngoài git cùng file mồi) | 0 bí mật thật; 1 báo nhầm (mục 7); file mồi bị bắt | ✔ |

**Danh sách kiểm tra** (vùng Giai đoạn 6):

| Mã | Kết quả | Ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets 0 bí mật thật |
| S2 | Đạt | Câu lỗi cố định, không chép lời Google, thuộc tính, đường dẫn, từ khóa (LC-T120-4); email tài khoản dịch vụ chỉ hiện ở Cài đặt |
| S3 | Đạt | `.env.example` có `GSC_SITE_URL` kèm chú thích (T-126) |
| W1–W4 | Không áp dụng | Giai đoạn 6 không gửi gì lên WordPress; chỉ đọc danh sách bài, trạng thái qua client có sẵn |
| A1, A2 | Đạt | Từ khóa chỉ vào lời dặn AI qua dòng kế hoạch đã duyệt, trong khung dữ liệu (LC-T120-24) |
| A3 | Đạt | Không gửi số liệu, từ khóa cho AI ở trang Theo dõi |
| U1 | Đạt | Làm sạch trước `escape_markdown`, `safe_rows`, không `unsafe_allow_html` với chữ Google |
| U2 | Đạt | Trang Theo dõi kiểm đăng nhập như mọi trang (LC-T120-14) |
| U3 | Không áp dụng | |
| F1 | Đạt | Bản lưu tạm chặn `data/` là liên kết từ đầu |
| F2 | Không áp dụng | |
| F3 | Đạt | Không `eval`, `pickle`; cache kiểm cấu trúc theo mẫu mới |
| D1 | Đạt | Không thư viện mới; pip-audit hôm nay 0 lỗ hổng |
| D2 | Đạt | `.gitignore` giữ `data/`, `.env` |
| D3 | Đạt | Mục 6: móc kiểm mạng |

## 7. Báo nhầm đã loại

- **bandit B101** (5 chỗ `assert` ở `refresh.py:361, 382, 433, 515`, `tracking.py:551`): chỉ để báo kiểu cho bộ kiểm kiểu (`… is not None`), không phải lớp kiểm bảo mật.
- **bandit B105** (`env_file.py:70` tên biến `APP_PASSWORD_HASH`; `service_account.py:52` địa chỉ lấy mã của Google; `:117` câu báo): không phải mật khẩu.
- **bandit B311** (`search_console.py:678`): `random.uniform` chỉ để giãn giờ thử lại khi Google báo 429, không dùng cho mã hóa.
- **detect-secrets «Secret Keyword»** `env_file.py:70`: cùng tên biến `APP_PASSWORD_HASH` như trên.

## Phụ lục · Kiểm kê biên bản Lá Chắn các phiếu Giai đoạn 6

| Phiếu | Việc | Lá Chắn | Model | Còn mở |
|---|---|---|---|---|
| T-120 | Thiết kế | ĐẠT (24 điều kiện LC-T120) | Opus tạm | Không (mọi điều kiện đã kiểm ở phiếu code) |
| T-121 | Client Search Console | ĐẠT CÓ ĐIỀU KIỆN | Fable | B.4 → buổi thử |
| T-122 | Cache số liệu | ĐẠT CÓ ĐIỀU KIỆN | Opus | Mục 8.4 → T-131 |
| T-123 | Lõi tính toán | ĐẠT CÓ ĐIỀU KIỆN | Opus | Góp ý G1, G2 |
| T-124 | Lấy số liệu, lưu thuộc tính | ĐẠT CÓ ĐIỀU KIỆN | Fable | B.3 → buổi thử; B.4 → T-131 |
| T-125 | Trang Theo dõi, Cài đặt | ĐẠT CÓ ĐIỀU KIỆN | Fable | B.2 → buổi thử; B.3 → Mac |
| T-126 | README «Theo dõi trên Google» (3 phần) | ĐẠT, ĐẠT CÓ ĐIỀU KIỆN (lượt cuối) | Opus | Không (cả hai điều kiện đã xong) |
| T-127 | «Đưa vào kế hoạch» | ĐẠT CÓ ĐIỀU KIỆN | Fable | B.1 → buổi thử |
| T-133 | Kịch bản thử thật Google | ĐẠT | Opus | Buổi thử chưa làm |

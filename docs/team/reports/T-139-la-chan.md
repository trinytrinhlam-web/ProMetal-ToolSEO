# Biên bản bảo mật T-139 · Đọc kết quả buổi thử thật Google (kịch bản T-133), cho dùng trang 📈 Theo dõi

> **Model:** Claude **Fable 5.1** (dòng «You are powered by» của lời nhắc hệ thống, kiểm trước khi viết theo luật 02/11 08:05).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Fable 5.1 · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-139](../tickets/T-139-la-chan-doc-thu-that-google.md) · đọc [kết quả buổi thử 18/11](T-139-thu-that-google.md) theo [kịch bản T-133](T-133-kich-ban-thu-that-google.md) mục 7, 8 · xem lại điều kiện Giai đoạn 6 của [T-135](T-135-la-chan.md) |
| Phạm vi | <ul><li>**Chỉ đọc:** báo cáo buổi thử (Chỉ Huy B, Opus 5.5, cùng chủ dự án, 11:09–13:25), kịch bản, biên bản T-135, T-121, T-124, T-125, T-127, README mục 15.</li><li>**Mã** trên `origin/main` `c5d1fd2` (nhánh `team/T-139` tạo từ đó) để trả lời 4 ghi nhận: `seo_app/tracking/stats.py`, `refresh.py`, `periods.py`, `seo_app/plan/propose.py`, `app/views/plan.py`.</li><li>Tái hiện 4 ghi nhận bằng hàm thuần trong worktree `wt-T-139` (không trong thư mục app của chủ dự án); không gọi Google thật.</li><li>App trong buổi thử là `main` `3202035`; từ đó tới `c5d1fd2` vùng Giai đoạn 6 không đổi hành vi (chỉ tài liệu, bảng việc).</li></ul> |
| Ngày | 2026-11-18 (14:19–14:40, giờ máy +07) |
| **Kết luận** | **CHO DÙNG trang 📈 Theo dõi, và nút «Đưa vào kế hoạch».** <ul><li>Mọi ca của kịch bản đạt; 17 trang và 5 từ khóa khớp Search Console từng số; `metadata` đoạn mới nhất `ok`; 0 dòng bị bỏ; 3 lệnh; quyền «Hạn chế» đủ; quyền trên Search Console không đổi; câu báo không lộ gì.</li><li>Không ngưỡng nào ở mục 8 kịch bản bị chạm, nên **không cần phiếu sửa mã**.</li><li>4 ghi nhận của buổi thử: đều **không phải lỗi**, đều giải thích được từ mã (mục 2). 2 việc chữ nhỏ cho Thư Ký (mục 4).</li><li>**Giai đoạn 6:** điều kiện «buổi thử thật» của T-135 **đã đóng**. Còn lại chỉ tài liệu và hai mục đã có chỗ theo dõi (mục 3).</li></ul> |

## Tóm tắt (cho chủ dự án)

- **Trang 📈 Theo dõi dùng được, số trên đó tin được.** Trong buổi thử 18/11, cả 17 bài, trang và 5 từ khóa của một bài đều khớp Search Console từng con số; tổng 11 click, 259 hiển thị cũng khớp.
- **Phần mềm chỉ đọc, và chỉ với quyền thấp nhất.** Tài khoản dịch vụ ở quyền «Hạn chế» là đủ; sau buổi thử, danh sách người dùng và quyền trên Search Console không đổi. Không có câu báo nào lộ email, đường dẫn máy hay lời máy chủ.
- **Nút «Đưa vào kế hoạch» cũng dùng được:** chỉ ghi vào Google Sheet đúng một dòng, và chỉ sau khi anh bấm «Áp dụng».
- **Bốn chỗ ghi nhận trong buổi thử không phải lỗi:**
  - «−0,6 điểm» là hiệu của hai số CTR đã làm tròn (4,2% − 4,8%), cố ý để chữ khớp số anh thấy trên màn hình.
  - «0,8% ngoài website» và «1,5%» đếm tay là hai khoảng ngày khác nhau (phần mềm đếm 28 ngày tính tới hôm nay theo giờ Google, kể cả 2 ngày chưa chốt).
  - Cột «Nguồn» có trong bảng đề xuất; bảng rộng nên cột cuối bị cuộn ngang trên ảnh.
  - Phần mềm cảnh báo trùng khi từ khóa trùng đường dẫn hay tiêu đề bài đã đăng, không so «cùng ý». Từ khóa thử chỉ chung 2 từ với bài cũ nên không cảnh báo. Anh vẫn nên tự xem bài cũ trước khi viết bài mới cùng chủ đề.
- **Không có gì anh phải quyết.** Dòng B-001 trên Sheet anh giữ hay xóa tùy ý.

## 1. Đọc bảng mục 7 của buổi thử

| Mã (kịch bản) | Kết quả buổi thử | Lá Chắn đối chiếu |
|---|---|---|
| (1) Chuẩn bị | Đạt | API bật, email quyền «Hạn chế» trước khi bấm; người dùng Search Console: 1 chủ sở hữu, 1 Hạn chế, 1 Toàn quyền (email khác của chính chủ dự án) → mục 2.5 |
| (2) Tìm, Lưu, Kiểm tra | Đạt | Một thuộc tính tên miền, «Hạn chế», «dùng được (tự lọc phần ngoài website)»; không cảnh báo quyền cao, không mục bị bỏ, không biến môi trường đè. Đóng T-121 B.4 (a) «Hạn chế» đọc được `sites` |
| (3) Lấy lần đầu | Đạt | Khung xanh, ngày chốt 15/11, 2 ngày tạm, không câu phụ. Đóng T-121 B.4 (a) phần `query` |
| (8) Số lệnh | Đạt | Không chạm trần 20 lệnh; ca 7 đếm 3 lệnh cho 3 lần gọi. Đóng T-124 B.3 phần số lệnh |
| (5) Bấm lại | Đạt | Chặn trong 10 phút, câu cố định, dòng «lấy lúc 11:16» giữ nguyên |
| (3) Bài A, bài B, tổng | Đạt | 17/17 dòng khớp click, hiển thị, vị trí (lệch 0); tổng khớp các dòng không `www.`. Vị trí trung bình theo lượt hiển thị (thiết kế T-120 1.5, ghi «suy luận, kiểm ở lượt thử thật») **nay đã xác nhận bằng số thật**. Ngưỡng mục 8 («lệch quá 0,1 → phiếu Thợ Máy») không chạm |
| (10) Từ khóa | Đạt | 5/5 khớp; «Google ẩn từ khóa hiếm» đúng như ghi chú cố định của app; bài không có từ khóa ra câu cố định. Đóng T-125 B.2 (chữ thật hiện chữ thuần) |
| (11) Đưa vào kế hoạch | Đạt | Ô chọn đủ 5 từ khóa sạch; 1 dòng «Thêm» B-001, nguồn «Search Console» trong Lý do; Sheet chưa có dòng trước «Áp dụng», đúng 1 dòng sau. Đóng T-127 B.1 |
| (4) `metadata` | `ok` (mới nhất), `missing` (cũ) | Đúng kỳ vọng thiết kế 2.4: đoạn mới có `first_incomplete_date` 16/11 khớp «2 ngày tạm»; đoạn đã chốt không có trường này. Ngưỡng mục 8 (`missing`/`bad` ở đoạn mới → phiếu T-124 B.3) **không chạm** |
| (7) Dòng bị bỏ | 0 / 169, 0 / 6, 0 / 23 | Luật 10% dòng lạ không bị kích; không cần xét lại (Soi Lỗi T-124 GN-2) |
| (9) 403, 429 | Không gặp | Mã lý do 403 thật chưa thấy. Đúng ghi nhận T-133 G3: không cố tạo ra. Lớp xử lý 403 đã có test giả ở T-121; giữ nguyên |
| (6) Người dùng và quyền | Đạt | Không đổi sau buổi: phần mềm không ghi gì phía Google (LC-T120-7, -16) |
| Câu báo | Đạt | Mọi câu là chữ cố định; ảnh không có email, đường dẫn (LC-T120-4, S2) |
| Dọn | Đạt | 1 dòng chờ chủ dự án (B-001 trên Sheet, tùy ý) |
| Tab thứ hai, «Hủy» | Chưa làm (tùy chọn) | Hai ca tùy chọn: khóa cấp module (LC-T120-22) và nút «Hủy» đã có test ở T-124, T-127; không cần làm thêm |

## 2. Bốn ghi nhận Chỉ Huy hỏi (việc 1)

### 2.1 CTR «−0,6 điểm» trong khi số suy ra là −0,51

- **Mã:** `stats.ctr_change_text` (`stats.py:201-208`) lấy hiệu của `shown_ctr_percent` hai kỳ, tức hai số **đã làm tròn 1 chữ số** như khi hiện; chú thích đầu file ghi rõ «chênh CTR, vị trí tính trên số đã làm tròn như khi hiện, để chữ khớp số người dùng thấy».
- **Tái hiện:** `PageStats(11, 259)` và `PageStats(3, 63)` cho 4,2 và 4,8 → «−0,6 điểm»; chênh thô −0,51.
- **Kết luận:** cố ý từ T-123 (chỗ #8 Thợ Máy tự chọn, Soi Lỗi T-123 đồng ý, Lá Chắn T-123 không phản đối). Nếu hiện −0,5 thì người dùng tự trừ 4,8 − 4,2 lại ra 0,6 và nghi số sai. **Không sửa.** Thư Ký thêm một câu ở README mục 15 (mục 4).

### 2.2 «0,8% ngoài website» ở ca 2 so với ~1,5% đếm từ bảng Trang

- **Mã:** `refresh._outside` (`refresh.py:731`) hỏi Google khuôn `hosts` cho cửa sổ `HOSTS_DAYS = 28` ngày tính tới **hôm nay theo giờ Google** (`google_today`), không phải tới ngày chốt. Lúc 11:15 +07 ngày 18/11, hôm nay PT là 17/11 → cửa sổ 21/10–17/11, **gồm 2 ngày tạm**.
- Bảng Trang chủ dự án so là 19/10–15/11 (theo hướng dẫn ca 5, tới ngày chốt). Hai cửa sổ lệch 2 ngày ở mỗi đầu; mẫu chỉ 4 hiển thị `www.` trên ~260, nên 0,8% và 1,5% là hai cách đếm trên hai khoảng, không mâu thuẫn.
- **Mục đích của số này** chỉ là cảnh báo «gần hết lượt hiển thị ngoài website» (`OUTSIDE_WARN_SHARE = 0.9`, `WORDPRESS_URL` có thể sai); độ chính xác tới phần trăm không quan trọng. **Không sửa.** Thư Ký ghi một câu ở README (mục 4).

### 2.3 Bảng đề xuất không có cột «Nguồn»

- **Mã:** `plan.proposal_rows` (`plan.py:475-489`) có đủ 8 cột, cột cuối là «Nguồn»; bảng hiện bằng `st.dataframe(safe_rows(...))` (`plan.py:526`), không ẩn cột. Tái hiện: `from_google_keywords` → cột `['Dòng', 'Loại', 'Mã bài', 'Từ khóa chính', 'Thay đổi', 'Lý do', 'Cảnh báo', 'Nguồn']`, Nguồn = «Search Console».
- Hai cột «Lý do», «Cảnh báo» đặt `width="large"`, nên trên màn hình thường cột «Nguồn» nằm ngoài khung, phải cuộn ngang; ảnh chụp không thấy là vì vậy.
- **Kết luận:** kịch bản đúng, mã đúng, ảnh thiếu. Không sửa mã. Thư Ký thêm chữ «(cuộn ngang nếu không thấy)» ở kịch bản và README nếu tiện.

### 2.4 Không ⚠️ khi từ khóa gần trùng ý bài đã đăng

- **Mã:** `propose._duplicate_post` (`propose.py:825-843`) cảnh báo khi: slug của từ khóa bằng slug bài; hệ số Dice ≥ 0,8 giữa tập từ không dấu của từ khóa và tiêu đề; hay từ khóa có ≥ 3 từ và mọi từ nằm trong tiêu đề. Đây là luật kiểm trùng của T-036 (bước SEO) dùng lại, có test.
- **Tái hiện:** «sửa cửa kéo sắt tphcm» với bài «Cửa sắt bị kẹt, khó đóng mở, cong vênh…»: chung 2 từ («cửa», «sắt») → không ⚠️. Đối chứng với bài slug `sua-cua-keo-sat-tphcm` → ⚠️ «Có thể trùng bài đã đăng (mã bài 13)…».
- **Kết luận:** đúng thiết kế; so «cùng ý» cần AI, mà LC-T120-13, -24 cấm đưa từ khóa Google vào AI ở bước này. Người dùng duyệt đề xuất rồi mới ghi, và còn duyệt dàn ý khi viết. **Không sửa.** Chủ dự án tự xem bài cũ trước khi viết bài mới cùng chủ đề (ghi ở tóm tắt).

### 2.5 Thêm: người dùng «Toàn quyền» trên Search Console

- Buổi thử đếm 1 Toàn quyền, là email khác của chính chủ dự án, có từ trước. Không liên quan phần mềm (phần mềm chỉ dùng email tài khoản dịch vụ ở «Hạn chế»). Không phải lỗi; không thuộc phạm vi phiếu. Ghi để chủ dự án biết tài khoản đó sửa được cài đặt Search Console.

## 3. Điều kiện Giai đoạn 6 sau buổi thử (việc 3)

Bảng «Còn mở, đã có chỗ theo dõi» của T-135 mục 2.2, cập nhật:

| Mục T-135 | Nay |
|---|---|
| T-121 B.4 (a)–(d), T-124 B.3, T-125 B.2, T-127 B.1: chờ buổi thử | **Đóng** (mục 1): «Hạn chế» đọc được `sites`, `query`; `metadata` thật `ok`/`missing` đúng kỳ vọng; 0 dòng bị bỏ; 3 lệnh; chữ thật hiện chữ thuần; không có cảnh báo quyền cao vì quyền đúng; «Đưa vào kế hoạch» chỉ ghi sau «Áp dụng». Riêng (c) mã lý do 403 thật: chưa gặp, giữ test giả của T-121, không cố tạo ra (T-133 G3) |
| T-125 B.3: ca symlink, chờ Mac | Còn, cùng các ca Mac đang treo (chủ dự án chưa có Mac) |
| T-122 8.4, T-124 B.4: `plan_cache._is_healthy` | Còn, phiếu T-131 (lượt 2, Thợ Máy), gộp cùng T-136 |
| T-133 G3, G4 | Giữ như ghi nhận |
| T-123 G1, các ca test ghim | Góp ý, gom phiếu dọn |
| Tài liệu (điều kiện 1 của T-135) | Lộ trình `CLAUDE.md` đã đánh dấu Giai đoạn 6 xong (10/11), còn ghi «Còn buổi thử thật với Google»: Chỉ Huy bỏ vế đó. **Còn**: README mục 15 bỏ khung «Chưa thử với Search Console thật» (dòng 608) và thêm 3 câu ở mục 4 |

**Kết luận Giai đoạn 6:** điều kiện «buổi thử thật» của T-135 đã đóng; Lộ trình đã đánh dấu xong từ 10/11. Còn lại chỉ tài liệu (README, kịch bản, vế «còn buổi thử» trong Lộ trình) và hai mục đã có chỗ theo dõi (Mac, T-131). Số trên trang 📈 Theo dõi **được dùng để quyết việc** từ hôm nay (hết hiệu lực câu «chỉ để làm quen» của T-135 mục 5).

## 4. Đề xuất phiếu (việc 2)

Không cần phiếu cho Thợ Máy. **Một phiếu nhỏ cho Thư Ký** (hay gộp vào lượt tài liệu đóng Giai đoạn 6), chỉ chữ, Lá Chắn rút gọn:

1. README mục 15: bỏ khung «Chưa thử với Search Console thật…» (dòng 608), thay bằng một dòng «Đã so với Search Console ngày 18/11/2026: khớp từng bài».
2. README mục 15, ba câu ngắn:
   - chênh CTR, vị trí là hiệu của hai số đã làm tròn như hiện trên màn hình;
   - «% ngoài website» ở Kiểm tra đếm 28 ngày tính tới hôm nay theo giờ Google (kể cả ngày chưa chốt), nên khác bảng Trang so tới ngày chốt;
   - cảnh báo trùng chỉ so đường dẫn, tiêu đề bài đã đăng, không so chủ đề; tự xem bài cũ trước khi viết.
3. Kịch bản T-133 ca 6b: «cột Nguồn (cuộn ngang nếu không thấy)». Kịch bản cũng nên ghi cửa sổ ngày của ca 2 để lần sau không so nhầm.

## 5. Công cụ quét

| Công cụ | Kết quả |
|---|---|
| detect-secrets (`PYTHONUTF8=1`) | Bản chép biên bản này, báo cáo buổi thử và kịch bản T-133, đứng tại thư mục chép, `--all-files`: **0**; file mồi (2 khóa giả) bị bắt |
| pytest | Không chạy lô test: phiếu chỉ đọc, mã Giai đoạn 6 không đổi từ T-135 (lô 27 file: 1.914 qua). Chỉ tái hiện 4 ghi nhận bằng hàm thuần trong worktree |
| pip-audit, bandit | Không chạy lại (không đổi mã, thư viện; T-135 ngày 10/11: 0 lỗ hổng) |

**Danh sách kiểm tra:** như T-135 (vùng Giai đoạn 6), không đổi. Buổi thử xác nhận thêm S2 (câu báo không lộ gì trên ảnh thật), W1–W4 không áp dụng (phía Google chỉ đọc, quyền không đổi), U1 (chữ Google thật hiện chữ thuần).

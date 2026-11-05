# Biên bản bảo mật T-126 · README «Theo dõi trên Google» và chú thích `GSC_SITE_URL` · rút gọn

> **Model:** Claude **Opus 5.5** (dòng «You are powered by»: Opus 5.5). Chỉ Huy B giao chạy Opus 5.5; chủ dự án 04/11: hết hạn mức Fable thì Lá Chắn chạy Opus 5.5, ghi rõ model.

## Phần 1 (README mục 15, `.env.example`)

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-126](../tickets/T-126-readme-theo-doi-google.md) phần 1 · [báo cáo Thư Ký](T-126-thu-ky.md) |
| Phạm vi | Rút gọn, chỉ đọc: `team/T-126` tại `cbe3114` (từ `main` cục bộ `8caab2f`), 3 file tài liệu: `README.md` (mục 15 mới `:604-659`; mục 14 `:556`, `:561`), `.env.example` (chú thích `GSC_SITE_URL` `:53-59`), báo cáo Thư Ký. Đối chiếu: `seo_app/google/search_console.py` (`parse_property`, `covers_site`, câu báo), `seo_app/google/service_account.py` (phạm vi), `app/views/settings.py` (khung tài khoản dịch vụ), thiết kế T-120 (`T-120-tho-may.md`), biên bản Lá Chắn T-120, T-121 |
| Máy | Windows 11 Pro, uv 0.13.4 (đạt ngưỡng `uvx`, T-078). Không gọi Google, không gọi website |
| Ngày | 2026-11-05 (11:12–11:25, giờ máy +07) |
| **Kết luận** | **ĐẠT** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp. Cả 4 điểm Chỉ Huy hỏi đều đạt. 4 ghi nhận nhỏ về chữ, không bắt buộc (mục 5), có thể làm cùng phần 2. **Gộp `main` được ngay** |

### Tóm tắt (cho chủ dự án)

- **Hướng dẫn phía Google an toàn, đúng với phần mềm.** README chỉ bảo cấp cho tài khoản phần mềm quyền **«Hạn chế»** (chỉ xem). README dặn rõ: không «Toàn quyền», không chủ sở hữu, không cấp thêm vai trò trong Google Cloud, gặp lỗi 403 cũng không nâng quyền mà báo Chỉ Huy.
- **Không chọn thuộc tính staging**, và nên chọn loại «Tiền tố URL» để tài khoản phần mềm chỉ thấy đúng website. Tôi tự thử bằng chính hàm của phần mềm: chọn nhầm thuộc tính staging, `http://`, sai `www.` đều bị từ chối, đúng như README viết.
- **Không lộ gì:** README và `.env.example` không có email tài khoản dịch vụ, mã project, đường dẫn file khóa hay tên miền thật; công cụ quét bí mật sạch.
- **Việc của anh/chị:** làm bước 1–3 ở README mục 15 khi rảnh. Đây là việc phía Google, không đụng website.

### 1. Quyền «Hạn chế», không bảo nâng quyền: **đạt**

| README | Đối chiếu |
|---|---|
| Bước 1.3 (`:621`): không cấp thêm vai trò (role) nào trong project Google Cloud | Đúng thiết kế T-120 mục 1.2; quyền đọc số liệu chỉ cấp trong Search Console |
| Bước 3.3 (`:632`): quyền **Hạn chế**; **không** Toàn quyền, **không** chủ sở hữu | Đúng T-120 (`T-120-la-chan.md:16`, `:124`). Phía app, phạm vi chỉ có `webmasters.readonly` (`service_account.py:50`), client từ chối mọi phạm vi khác hay ủy quyền toàn miền (`_search_console_only`, `search_console.py:830-839`). Nên dù quyền phía Google có cao hơn, phần mềm vẫn không sửa được gì: hai lớp «chỉ đọc» độc lập |
| Bước 3.3 (`:633`): Search Console không nhận email, hay chỉ cho thêm làm chủ sở hữu thì dừng, báo Chỉ Huy, «đừng thử cách khác» | Đúng T-120 (`:123-124`): không tự chọn «Toàn quyền» |
| Bước 3.4 (`:634`): lỡ chọn quyền cao hơn thì đổi về **Hạn chế** | Đúng; T-125 sẽ cảnh báo khi quyền cao hơn «Hạn chế» (T-121 phần B mục 3) |
| Dòng 403 (`:651`): «**Đừng nâng lên «Toàn quyền» hay chủ sở hữu** để thử… báo Chỉ Huy» | Đúng T-120 `:124`; câu app trích khớp `_MSG_BY_STATUS[403]` (câu đó cũng ghi «quyền «Hạn chế»») |
| «Giữ an toàn» (`:657-659`): xem lại quyền; đổi khóa không đổi email; «Xoá quyền truy cập» khi thôi dùng | Đúng (đổi khóa của tài khoản dịch vụ không đổi email) |

### 2. Không chọn thuộc tính staging: **đạt**

- README (`:629`, `:641`, `:643`) và `.env.example` (`:59`): chọn thuộc tính của website chính; không thêm email vào thuộc tính staging; nên dùng «Tiền tố URL» (tài khoản dịch vụ chỉ thấy đúng website). Loại «Tên miền» có cả tên miền con và staging; khi đó app chỉ lấy số liệu của đúng `WORDPRESS_URL`.
- Mã: `covers_site` (`search_console.py:355-366`) so theo từng phần tên miền; bộ lọc trang `^<WORDPRESS_URL>/` gửi Google cùng lớp kiểm từng dòng trong máy (T-121 mục 4). Câu «… (ví dụ thuộc tính staging)…» là `_MSG_NOT_SITE`.
- **Tự thử** (`probe_t126.py`, chỉ gọi hàm thuần, không mạng): **21 ca, 0 sai**:
  - `parse_property` nhận `https://example.com/`, `sc-domain:example.com`, `sc-domain:xn--…`;
  - `parse_property` từ chối `http://`, thiếu `/` cuối, chữ hoa, đường con, cổng, địa chỉ IP, dấu chấm cuối, chữ có dấu, dấu cách đầu;
  - `covers_site`: tiền tố phải cùng tên máy, `www.` sai lệch là từ chối, cả hai chiều; tên miền phủ cả `www.`;
  - `covers_site`: `staging.` (cả hai loại) và `evilexample.com` không phủ website.

  Cả 21 ca khớp đúng các câu ở README và `.env.example`.

### 3. Không lộ email, mã project, đường dẫn file khóa: **đạt**

- Ví dụ trong README chỉ dùng `ten-mien-cua-ban`, `example.com`; email chỉ nêu đuôi chung `.iam.gserviceaccount.com`. Không có mã project hay đường dẫn file khóa. Bước 2 bảo chép email **từ app** (`settings.py:594-595`, `st.code`), không ghi email vào tài liệu.
- Grep diff `cbe3114`: không email, không tên miền thật, không đường dẫn máy, không chuỗi khóa.
- detect-secrets (mục 4): 0 kết quả.

### 4. Khớp code và các biên bản T-120, T-121: **đạt**

| README / `.env.example` | Mã / biên bản |
|---|---|
| Chỉ 2 dạng `https://…/` và `sc-domain:…`, chữ thường không dấu, có `/` cuối, không đường con, `http://` bị từ chối | `parse_property` (`:291-313`); thiết kế T-120 `:104` (tên miền tiếng Việt ở dạng `xn--`) |
| Tiền tố: tên miền giống hệt `WORDPRESS_URL`, kể cả `www.` | `covers_site` (`:366`); T-121 mục 4, ca C |
| Tên miền: app chỉ lấy số liệu của `WORDPRESS_URL` | bộ lọc `includingRegex` + kiểm dòng trong máy (docstring `:12-15`; T-121 `:50`) |
| Chỉ đọc danh sách thuộc tính và báo cáo Hiệu suất | hai lệnh cố định `GET …/sites`, `POST …/searchAnalytics/query` (docstring `:6-11`; LC-T120-7) |
| Dùng lại tài khoản dịch vụ, file khóa của mục 14, không khóa mới | thiết kế T-120 mục 2.1 |
| 4 câu báo trong bảng «Khi app báo lỗi» | `_MSG_API_OFF`, `_MSG_BY_STATUS[403]`, `_MSG_NOT_SITE`, `_MSG_BAD_PROPERTY`: khớp đầu câu |
| `.env.example`: chọn ở Cài đặt, app tự ghi dòng này (đang làm) | thiết kế T-120 `:122` (lựa chọn A), Đ12 → T-124 (ghi qua `env_file`, bộ kiểm chặt) |
| Mục 14 sửa hai câu cho khỏi mâu thuẫn với mục 15 | Đúng |

### 5. Ghi nhận (không tính lỗi, không bắt buộc)

- **N1 · `:651` «Hạn chế» là đủ:** theo tài liệu Google thì đúng, nhưng T-120 (`T-120-la-chan.md:123`) và T-121 (phần B mục 4a) ghi đây là việc **chưa xác minh**, sẽ kiểm ở buổi thử với Google. Nên viết: «Theo Google, «Hạn chế» đủ để xem số liệu; buổi thử sẽ xác nhận». Hướng xử lý (không nâng quyền, báo Chỉ Huy) vẫn giữ nguyên.
- **N2 · Bước 3:** nên thêm nửa câu «chỉ thêm email vào đúng thuộc tính của website này, không thêm vào thuộc tính website khác của bạn». File khóa thấy được thuộc tính nào thì người có file khóa đọc được số liệu của thuộc tính đó; app thì chỉ dùng thuộc tính phủ `WORDPRESS_URL`.
- **N3 · Bảng «Chọn thuộc tính nào» (`:640`):** `.env.example` có ghi «không đường con», bảng README thì chưa. Thuộc tính tiền tố có đường con (ví dụ `https://ten-mien-cua-ban/blog/`) bị app từ chối bằng câu sai dạng.
- **N4 · Cho T-125 (Họa Sĩ), không phải README:** chú thích trong app «Email của tài khoản dịch vụ, để chia sẻ Sheet kế hoạch (quyền Người chỉnh sửa):» (`settings.py:594`) chỉ nói về Sheet. README đã giải thích, nhưng khi làm phần Search Console trong Cài đặt nên ghi luôn «Search Console: quyền Hạn chế» ngay cạnh email. Ngoài ra, buổi thử với Google của T-121 (phần B mục 4) chưa có trong kịch bản T-128; khi xong T-124, T-125 thì Chỉ Huy thêm vào.

### 6. Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| `uv --version` trước `uvx` | 0.13.4 | ✔ |
| detect-secrets (`PYTHONUTF8=1`; chép `README.md`, `.env.example`, báo cáo Thư Ký ra thư mục ngoài git cùng file mồi tiếng Việt, `scan --all-files .`) | 3 file: 0 kết quả; file mồi: bị bắt | ✔ |
| Grep diff `cbe3114` (email, tên miền thật, đường dẫn máy, `.json`, khóa) | 0 (chỉ chữ «project» và đuôi `.iam.gserviceaccount.com`) | ✔ |
| `probe_t126.py` (hàm thuần, không mạng) | 21 ca, 0 sai | ✔ |
| pytest file đọc `.env.example` (`test_config.py`, `test_t090_env_bang_ma.py`, `test_la_chan_t090.py`) | 58 qua, 15 giây | ✔ |
| Gộp thử: `main` cục bộ `8caab2f` (nhánh nằm ngay trên), `team/T-128` `952aaca` | `git merge-tree`: không xung đột cả hai | ✔ |

### 7. Kết luận phần 1

**ĐẠT.** Gộp `main` được ngay. N1–N3 có thể sửa cùng phần 2 (sau T-125); N4 chuyển cho T-125 và kịch bản buổi thử. Phần 2 (cách đọc số, nút «Đưa vào kế hoạch») Lá Chắn kiểm khi giao.

# Biên bản bảo mật T-127 · Nút «Đưa vào kế hoạch» (từ khóa Google thành đề xuất «Thêm» chờ duyệt) · đầy đủ

> **Model:** **Fable 5.1** (dòng «You are powered by»: Fable 5.1, kiểm đầu lượt). Chỉ Huy B giao 10/11 sau lượt 2 của Thợ Máy; Soi Lỗi chưa kiểm lại lượt 2 nên biên bản này xác nhận thay việc SL-T127-1 đã đóng. Đúng trọng tâm Chỉ Huy giao, không lan rộng.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **Fable 5.1** · dưới Chỉ Huy B |
| Phiếu được kiểm | T-127 (phiếu trên `main`: `docs/team/tickets/T-127-dua-tu-khoa-vao-ke-hoach.md`; LC-T120-13, -15, -24; điều kiện B.1 của Lá Chắn T-125). Nhánh `team/T-127` từ `09fdad2`: Thợ Máy `523b0ce`, `0505f31`, báo cáo `0c1f286`; Soi Lỗi rút gọn `8e2cd5a` (ĐẠT CÓ ĐIỀU KIỆN, SL-T127-1 Thấp); Thợ Máy lượt 2 `8ce3383`, báo cáo `6a4aeea`. Đầu nhánh **`6a4aeea`**, đã push |
| Phạm vi | **Đầy đủ**: toàn bộ diff của phiếu `523b0ce~1..6a4aeea` (`seo_app/plan/propose.py` +112: `google_keyword`, `from_google_keywords`; `app/views/tracking.py` +44/−6: `plan_box`; `app/views/plan.py` +42: `take_google_keywords`; 2 file test mới), đọc cùng code không đổi mà đường này dựa vào: `check_proposals`, `_new_row`, `PlanRow` (`_keyword`, `KEYWORD_MIN`), `personal_info` (`_PHONE_RE`, `_EMAIL_RE`), `fold_key`, `keep_proposals`, `proposals_box`, `proposal_rows`, `pick_label`, `proposal_detail`, `safe_rows`, `apply_chosen`, `fresh_index`, `site_listing`, `run_ai`. Không gọi Google, website thật; không chạy cloud |
| Ngày | 2026-11-10 (giao ≈ 12:00, xong 12:21, +07, giờ máy) |
| Máy | Windows 11 Pro 10.0.26300, Python 3.12.15, uv 0.13.4. Chỉ chạy test liên quan, không chạy toàn bộ; không vòng chờ dài |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được ngay** (`main` `7153f0a`: `git merge-tree` không xung đột; `main` không sửa file nào của phiếu từ `09fdad2`): 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **0 Thấp mới**. LC-T120-13, -15, **-24** và điều kiện B.1 của Lá Chắn T-125 **đạt**. **SL-T127-1 đã đóng** ở `8ce3383` (đọc mã, thử riêng, test). Điều kiện chỉ cho lượt thử thật và tài liệu, không chặn gộp |

## Tóm tắt (cho chủ dự án)

Nút «➕ Đưa vào kế hoạch» ở trang «📈 Theo dõi» **an toàn để gộp**. Tôi đọc lại từ đầu và thử riêng, không dựa vào kết quả của Thợ Máy và Soi Lỗi:

- **Chỉ từ khóa «sạch» mới vào được ô chọn:** chữ tiếng Việt hoặc a–z, số, dấu cách, dấu «-», tối đa 80 ký tự, không số điện thoại, email, địa chỉ web. Tôi thử hơn 50 kiểu chữ lạ (ký tự vô hình, chữ Nga trông giống chữ Việt, chữ toàn khổ, công thức bảng tính, link giấu, số điện thoại nhiều dạng, chữ ghép kiểu Unicode): không kiểu nào lọt. Từ khóa bị bỏ chỉ được **đếm**, không chép lại nội dung lên màn hình.
- **Mỗi lần tối đa 10 từ khóa**, cắt ở cả hai trang.
- **Chỉ thành đề xuất chờ anh/chị duyệt** ở trang Kế hoạch, giống đề xuất từ file hay AI; phần mềm **không ghi thẳng vào Google Sheet**, **không gọi AI** ở bước này. Ghi Sheet vẫn chỉ qua nút «Áp dụng» có sẵn.
- **Lọc hai lần:** trang Kế hoạch lọc lại danh sách nhận được, nên dù danh sách trong phiên có bị sai (tôi cố tình đặt thẳng chữ xấu vào), vẫn chỉ ra đề xuất sạch, không gọi mạng.
- **Lỗi nhỏ Soi Lỗi tìm ra đã sửa đúng:** khi so với bài đã đăng, nút này nay tải lại danh sách bài khi bản trên máy cũ hơn 6 giờ và báo khi không tải được, giống cách nạp kế hoạch cũ.
- **Việc của anh/chị lúc này:** không có.

## Kết quả theo trọng tâm Chỉ Huy giao

### 1. Bộ lọc chặt (LC-T120-24) — **đạt**

- `google_keyword` (`propose.py:901-923`): không phải chuỗi → bỏ; **NFC** rồi gộp dấu cách thường (chỉ tách theo dấu cách U+0020: tab, xuống dòng, NBSP, U+3000 nằm lại trong chữ và bị bảng trắng loại); `0 < độ dài ≤ 80` (đếm sau NFC); **mọi ký tự** phải thuộc bảng trắng 186 chữ (`_KEYWORD_LETTERS`: a–z, đ, 12 nguyên âm với 5 dấu thanh, hoa và thường) hoặc `0-9`, dấu cách, `-`; phải có ít nhất một chữ; `personal_info` = (0, 0); không có từ `www`, `http`, `https` (tách theo dấu cách và `-`, so chữ thường). Trả về **đúng chuỗi đã chuẩn hóa**, nên kết quả không bao giờ chứa ký tự ngoài bảng trắng (probe F: quét 15.000 mã điểm, 0 ký tự lọt).
- Vì bảng trắng là danh sách **ký tự cụ thể**, không phải loại Unicode, nên mọi lớp Soi Lỗi và tôi thử đều bị bỏ: ký tự vô hình (ZWSP, word joiner, BOM, soft hyphen, U+3164), đảo hướng (RLO), chữ toàn khổ (chữ, số, gạch U+FF0D), chữ Nga, Hy Lạp, Hebrew, Thổ (ı), chữ có dấu ngoài tiếng Việt (ö, ñ, ç, ś), chữ ghép (ﬁ), dấu tổ hợp lạ (U+0336), gạch dài (U+2013, U+2011), dấu câu, `=`, `+`, `@`, `[`, `(`, `<`, `*`, `#`, `_`, `&`, `/`, `"`, `'`. **NFC không mở lối**: các ký tự đơn có phân rã chuẩn (U+1FEF → `` ` ``, U+037E → `;`, U+2126 → Ω, U+212B → Å) ra chữ ngoài bảng trắng → bị bỏ; chỉ U+212A KELVIN → `K` được nhận và kết quả là chữ `K` thường (ghi nhận 3). Dấu tổ hợp tiếng Việt viết tách (NFD) được gộp đúng (ắ, ợ, ề).
- **Số điện thoại, email, web:** email và địa chỉ web không thể tồn tại (không có `@`, `.`, `:`, `/`); `personal_info` chặn mọi dạng số Việt Nam có đầu `0`/`84` (liền, cách, gạch, từng cặp, **từng chữ số một**, số bàn `028`). Dãy số không đầu `0`/`84` (hotline `1900 1234`, `1800 1234`, dãy 12 số) không bị coi là số điện thoại: đúng thiết kế `_PHONE_RE` (LC-T094-21), ghi nhận 1. Từ `www`/`http` dính liền chữ khác (`wwwsuachuacuasat`) hay `ftp`, `mailto`, `com` không bị chặn: chỉ là chữ, không thành link ở đâu.
- **Từ khóa chỉ toàn chữ (Soi Lỗi GN-2, mục 9 sổ T-120):** câu lệnh không dấu câu, ≤ 80 ký tự, vẫn qua bộ lọc. Đây là rủi ro LC-T120-24 **đã chấp nhận**; tôi xem lại và giữ nguyên mức Thấp vì (a) kẻ xấu phải làm nhiều người gõ đúng câu đó rồi bấm vào website này trong 2–3 tháng (Google ẩn từ khóa hiếm), (b) người dùng tự tick từng từ khóa, bấm «Áp dụng», rồi mới chọn viết bài, (c) khi viết bài, từ khóa nằm trong khung dữ liệu của lời dặn (T-098, T-103 đã qua Lá Chắn), và dàn ý, bài đều qua người duyệt. Không cần thêm điều kiện.

### 2. Tối đa 10 từ khóa mỗi lần — **đạt**

`st.multiselect(max_selections=MAX_GOOGLE_KEYWORDS)` (`tracking.py:833-835`), cắt `[:10]` khi đặt vào phiên (`:839`), và `from_google_keywords` cắt `keywords[:MAX_GOOGLE_KEYWORDS]` lần nữa (`propose.py:948`), câu báo chỉ đếm số (`NOTE_GOOGLE_TOO_MANY`). Probe D: 12 phần tử → 10 xét, câu báo «2 từ khóa sau bị bỏ»; ca trang của tôi: 14 phần tử đặt thẳng vào phiên → câu báo «4 từ khóa sau bị bỏ».

### 3. Chỉ thành đề xuất chờ duyệt, không ghi thẳng Sheet (LC-T120-13) — **đạt**

- Trang Theo dõi chỉ đặt `S["plan_google_keywords"] = tuple(...)` rồi `st.switch_page` (`tracking.py:838-840`). Trang Kế hoạch lấy ra (`pop`) ngay sau khi đọc kế hoạch (`plan.py:1077-1078`), chỉ nhận `tuple`, dựng đề xuất bằng `from_google_keywords` → `keep_proposals` (`plan.py:414-442`): chỉ ghi `S.plan_proposals`, `S.plan_base`, `S.plan_index`, `S.plan_notes`; **không lệnh ghi** nào. Ghi Sheet chỉ qua «✅ Áp dụng thay đổi» (`apply_chosen`, `plan.py:571-593` → `sync.apply_proposals`, đọc lại Sheet và so với `plan_base` trước khi ghi, T-100). Đề xuất có cảnh báo không tick sẵn (`preselected` False, probe D).
- Mỗi dòng mới qua `PlanRow.model_validate` (mọi bộ kiểm dòng kế hoạch; «x» 1 ký tự bị `KEYWORD_MIN` loại), `_new_row` (chỉ trường được đề xuất, trạng thái «Chưa viết»), `check_proposals` (trùng dòng kế hoạch, trùng bài đã đăng, trang cửa ngõ, như T-098), `source="Search Console"`, `before=None`, `Action.ADD` (probe D).

### 4. Từ khóa không vào lời dặn AI (LC-T120-13) — **đạt**

Đường đi `plan_box` → `take_google_keywords` → `from_google_keywords` → `check_proposals` không nhập `seo_app.ai`, không dựng lời dặn (Thợ Máy có ca AST). `run_ai` (`plan.py:445-472`) chỉ nhận `S.plan_base.plan_rows()` (kế hoạch đã đọc từ Sheet), chữ người dùng gõ và danh sách bài: **đề xuất đang chờ không vào đó**; `keep_proposals` còn bỏ `plan_ai` đang dở. Sau «Áp dụng», từ khóa là một dòng kế hoạch như mọi dòng khác, vào lời dặn AI trong khung dữ liệu khi đọc kế hoạch lần sau và khi viết bài: đúng chữ LC-T120-24.

### 5. Chữ hiện chữ thuần — **đạt**

Ô chọn `st.multiselect` hiện lựa chọn là chữ thuần (không Markdown), và chỉ chứa chuỗi đã qua bộ lọc (chỉ chữ, số, dấu cách, `-`), **hiện nguyên văn** như trong bảng (chữ chuẩn hóa chỉ dùng cho đề xuất). Nhãn, `help`, câu đếm là hằng (`MSG_PLAN_PICK`, `MSG_PLAN_HELP`, `MSG_PLAN_NONE`, `MSG_PLAN_LEFT_OUT` chỉ có số). Trang Kế hoạch: bảng đề xuất `st.dataframe(safe_rows(proposal_rows(...)))` (`plan.py:529-537`) và `proposal_detail` (`safe_rows`, `st.text`); nhãn ô tick `pick_label` **không có chữ dữ liệu**; ghi chú và cảnh báo qua `show` → `plain` = `escape_markdown`. Từ khóa mở đầu bằng `-` (bộ lọc cho phép, probe B) được `safe_text` thêm dấu cách ở bảng và khi ghi Sheet (LC-T094-28, LC-T101-1), nên CSV tải về và ô Sheet không thành công thức. Không `unsafe_allow_html`, không `LinkColumn` (grep).

### 6. SL-T127-1 đã đóng (lượt 2) — **đạt**

`take_google_keywords` dùng `index, notice = fresh_index()` (`plan.py:426`) như `read_source`, `read_sheet_link` (T-098): `site_listing(store, client)` → `store.get` tải lại khi bản trên máy cũ hơn `DEFAULT_MAX_AGE_HOURS` = 6 giờ, lỗi WordPress hay file cache → `index=None` kèm câu cố định «Chưa tải được danh sách bài đã đăng…», chưa khai báo WordPress → `MSG_NOT_CONNECTED`; câu vào `plan_notes` sau `MSG_GOOGLE_FROM`. Lời gọi website chỉ chạy **sau khi người dùng bấm nút** (khóa phiên được `pop` trước khi tải, tải lại trang không chạy lại), mở trang như thường không thêm lời gọi nào: không đụng LC-T120-21 (ghi nhận 2). R5: `git diff 8e2cd5a..6a4aeea -- tests/test_soi_loi_t127.py` chỉ gỡ khối `@pytest.mark.xfail(strict=True)`; thân test không đổi. Ca của Soi Lỗi và ca mới của Thợ Máy (`loads == 1`, cảnh báo trùng bài 99) qua trong lô test.

### 7. LC-T120-15, không lùi — **đạt**

Không thêm trang (`PAGES` không đổi). Bộ chặn mạng chung của `conftest` **đang hoạt động** (ca thử tạm của tôi mở trang Kế hoạch mà quên mồi bản lưu kế hoạch: bị chặn ngay ở `oauth2.googleapis.com`); mọi ca trang dùng client giả đếm lệnh. 13 file test liên quan (T-127, `propose`, `model`, T-098, trang Kế hoạch T-101, trang Theo dõi T-125, `test_app_pages`, T-103, T-113) qua hết; ca giữ chỗ cũ `test_t125_tracking_page.py:541` vẫn đúng (nút khóa khi chưa chọn).

## Lỗi phát hiện

Không có lỗi mới.

## Đánh giá lỗi, ghi nhận của Soi Lỗi; R5

| Mục | Lá Chắn |
|---|---|
| **SL-T127-1** · Thấp · kiểm trùng bài đã đăng dùng danh sách cũ, không tải lại, không báo | Đồng ý Thấp. **Đã đóng** ở `8ce3383` đúng gợi ý (mục 6) |
| GN-1 ca trang của Thợ Máy không dựng được client WordPress | Đã được ca Soi Lỗi (tài khoản giả) và ca lượt 2 của Thợ Máy phủ; ca thử tạm của tôi xác nhận câu `MSG_NOT_CONNECTED` vào ghi chú khi chưa khai báo |
| GN-2 câu lệnh chỉ toàn chữ | Rủi ro LC-T120-24 đã chấp nhận, giữ Thấp (mục 1) |
| R5 (`tests/test_soi_loi_t127.py`) | Chỉ gỡ dấu `xfail`; `import pytest` giữ vì ca khác còn dùng. Đúng |
| Thợ Máy mục «Chỗ để ngỏ» 4 (chữ = tiếng Việt hoặc a–z, không phải mọi chữ Unicode) | **Đồng ý, đây là chỗ mạnh nhất của bộ lọc**: đóng mọi đường chữ giả dạng, vô hình, phải-sang-trái mà bản đầu `523b0ce` để lọt |

## Thử độc lập (Fable)

Script `probe_t127.py` (thư mục nháp của phiên; hàm thuần, không mạng, không Streamlit) và một ca AppTest tạm `probe_t127_page.py` (đã xóa khỏi `tests/` trước khi commit, bản lưu ở thư mục nháp).

| Phần | Ca | Kết quả |
|---|---|---|
| A NFC | 15 ca: ký tự đơn có phân rã chuẩn (Kelvin, varia, Greek `;`, Ohm, Angstrom), tổ hợp trên phụ âm, tổ hợp tiếng Việt, é/ö/ñ, ligature, gạch toàn khổ, gạch không ngắt, ı | Chỉ tổ hợp tiếng Việt, é và Kelvin→K được nhận; kết quả đều trong bảng trắng |
| B gạch nối, số, độ dài | `-cửa kéo`, `cửa kéo-`, `cửa--kéo`, `-1`, `-1a`, 80/81 ký tự (NFC, NFD), 80 + dấu cách quanh, 80 + `-` | Đúng luật: `-1` bỏ (không chữ), 81 bỏ, NFD 80 chữ được nhận |
| C số điện thoại, web | 21 chuỗi | Mọi dạng đầu `0`/`84` bị bỏ (kể cả từng chữ số một); hotline `1900`/`1800`, dãy 12 số, `wwwsuachuacuasat`, `ftp`, `mailto` được nhận (ghi nhận 1) |
| D `from_google_keywords` | 12 phần tử trộn (chữ xấu, số, None, tuple, trùng theo `fold_key`, 80 ký tự), `range(5)`, 10 lần cùng chữ | 4 đề xuất ADD, `source` «Search Console», `before=None`, trùng B-001 không tick sẵn; 3 câu báo đếm đúng; `range` → rỗng; 10 lần cùng chữ → 1 + «9 trùng» |
| E hiển thị `-` đầu | `PlanRow` giữ `-cửa kéo`; `safe_text` → `" -cửa kéo"` | CSV, Sheet không thành công thức |
| F quét bảng trắng | 15.000 mã điểm chen giữa hai chữ | 0 ký tự ngoài bảng trắng lọt ra kết quả |
| Trang (AppTest, tạm) | đặt thẳng 14 phần tử xấu vào `plan_google_keywords` rồi mở trang Kế hoạch (bản lưu kế hoạch mồi sẵn, chưa khai báo WordPress) | 3 đề xuất sạch, câu «4 từ khóa sau bị bỏ», «7 từ khóa không đưa vào», `MSG_NOT_CONNECTED`; `HYPERLINK`, `0909`, `[x](y)` không xuất hiện ở đâu trên trang; khóa phiên đã bị lấy ra; 0 lệnh mạng |

Ngoài ra: grep phần mới của hai trang theo danh sách mẫu cấm (`unsafe_allow_html`, `LinkColumn`, `st.cache_*`, `fragment`, `run_every`, `markdown_link`, `st.html`, `components`, `seo_app.ai`, `sheets`): không có.

## Danh sách kiểm tra (điều kiện của phiếu)

| Mã | Đạt | Bằng chứng |
|---|---|---|
| LC-T120-13 | ✔ | Mục 3, 4 |
| LC-T120-15 | ✔ | Mục 7 |
| LC-T120-24 | ✔ | Mục 1, 2, 3, 5: bộ lọc chặt hơn ô từ khóa thường (ô thường `PlanRow` nhận mọi chữ ≤ 120 ký tự, dấu câu), hiện nguyên văn, ≤ 10, không AI, nguồn «Search Console», qua `PlanRow` và `check_proposals` |
| Lá Chắn T-125 B.1 | ✔ | = LC-T120-24 |
| Yêu cầu 1–5 của phiếu | ✔ | 1: mục 3; 2: mục 1; 3: mục 2, 3, 5; 4: mục 4; 5: mục 7 |
| W1, W2 | ✔ | Không lệnh ghi tới WordPress, Sheet ở bước này; lời gọi website chỉ đọc (`list_published`) sau khi bấm |
| U1, U2 | ✔ | Chữ thuần mọi nơi (mục 5); không in `.env` |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pytest 13 file liên quan trên `6a4aeea` (`test_t127_dua_vao_ke_hoach`, `test_soi_loi_t127`, `test_plan_propose`, `test_plan_model`, `test_soi_loi_t098`, `test_t101_plan_page`, `test_t125_tracking_page`, `test_soi_loi_t125`, `test_app_pages`, `test_t103_plan_prompt`, `test_la_chan_t103`, `test_soi_loi_t103`, `test_t113_website_status`) | **923 qua, 0 bỏ qua, 0 xfail, 0 hỏng**, 3 phút 53 giây | ✔ |
| Probe A–F và ca trang tạm | đúng hướng cả (1 lần sửa kỳ vọng của chính probe: đếm 7 chứ không phải 5 từ khóa bị bỏ, vì «x» qua bộ lọc chữ nhưng bị `KEYWORD_MIN`) | ✔ |
| `ruff check .`; `ruff format --check` 5 file | sạch; đã đúng định dạng | ✔ |
| bandit `propose.py`, `plan.py`, `tracking.py` (`PYTHONUTF8=1`) | 1 Low B101 (`tracking.py:551`, `assert` thu hẹp kiểu của T-125, báo nhầm cũ) | ✔ |
| detect-secrets (`PYTHONUTF8=1`) 5 file của phiếu + 2 báo cáo | 0; biên bản này: 0 | ✔ |
| Ký tự ẩn (Cf, Cc, CR), NFC trong 5 file | 0; đều NFC | ✔ |
| D1 | `uv.lock`, `pyproject.toml`, `config/` không đổi | ✔ |
| Gộp thử | `git merge-tree --write-tree main HEAD` (`main` `7153f0a`) không xung đột; `main` không sửa file nào của phiếu | ✔ |

## Ghi nhận (không xếp lỗi)

1. `personal_info` không coi hotline `1900 xxxx`, `1800 xxxx` hay dãy số không đầu `0`/`84` là số điện thoại (đúng thiết kế `_PHONE_RE`, LC-T094-21): từ khóa như «sửa cửa 1900 1234» vào được kế hoạch. Người dùng vẫn tick từng dòng. Nếu muốn chặt hơn ở phiếu sau: bỏ từ khóa có dãy ≥ 7 chữ số liền hay cách.
2. Sau khi bấm nút, trang Kế hoạch có thể **gọi website** (`list_published`) khi danh sách bài trên máy cũ hơn 6 giờ (lượt 2, như T-098): là việc người dùng bấm; khóa phiên `pop` trước nên tải lại trang không gọi lại; lỗi thành câu cố định. Không phải «mở trang gọi mạng».
3. NFC đổi U+212A KELVIN thành `K` (chữ trong bảng trắng): vô hại vì kết quả chỉ gồm ký tự bảng trắng; ô chọn hiện nguyên văn (ký hiệu Kelvin), đề xuất ghi `K`.
4. Câu báo «không đưa vào kế hoạch» không nói «tối thiểu 2 ký tự» (`KEYWORD_MIN`); từ khóa 1 chữ rất hiếm. Chữ, không bảo mật.
5. Khi nhận từ khóa Google, `keep_proposals` **thay** bộ đề xuất đang chờ (từ file hay AI) chưa áp dụng, như `read_source` (T-098). Đúng cách cũ; nếu muốn, phiếu giao diện sau có thể hỏi lại.
6. Hằng `"plan_google_keywords"` khai báo ở cả hai trang (`GOOGLE_HANDOFF_KEY`); lệch nhau thì ca trang của Thợ Máy bắt được.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

**A. Gộp `main`: được ngay.** Chỉ Huy chạy toàn bộ test khi gộp.

**B. Cho việc sau** (không chặn T-127):

1. **Lượt thử thật với Google (kịch bản T-133):** thêm bước bấm «Đưa vào kế hoạch» với từ khóa thật: ô chọn chỉ có từ khóa sạch, câu đếm từ khóa bị bỏ, đề xuất hiện đúng ở trang Kế hoạch với nguồn «Search Console», cảnh báo trùng; **chỉ** sau «Áp dụng» mới có dòng mới trên Sheet (kiểm trực tiếp trên Sheet).
2. **Tài liệu (T-126 hay Thư Ký):** README mục «Theo dõi trên Google» ghi cách dùng nút và luật lọc (chỉ chữ tiếng Việt hoặc a–z, số, dấu cách, «-», ≤ 80 ký tự; không số điện thoại, email, web; ≤ 10 mỗi lần; luôn duyệt ở trang Kế hoạch).
3. **Sổ rủi ro (Thấp, không gấp):** mục 9 bảng T-120 («câu lệnh chỉ toàn chữ») ghi thêm hai lớp giảm nhẹ đã có ở T-127 (≤ 80 ký tự, không dấu câu; người dùng tick và «Áp dụng»).

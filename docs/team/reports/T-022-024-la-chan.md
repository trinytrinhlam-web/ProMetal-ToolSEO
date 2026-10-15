# Biên bản bảo mật T-022 + T-024 · Hồ sơ doanh nghiệp và bộ lọc hồ sơ theo khối

> **Lưu ý về model:** lần kiểm định này chạy **tạm bằng Opus 5.5** (`claude-opus-5-5`), vì Fable 5.1 bị giới hạn tới 01/11. Chủ dự án đã duyệt cách này. **Sau 01/11 phải kiểm lại bằng Fable** (Chỉ Huy giữ việc này trên bảng việc).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Opus 5.5 (tạm thay Fable 5.1, xem lưu ý trên) |
| Phiếu được kiểm | [T-022](../tickets/T-022-sua-ho-so-doanh-nghiep.md) · [T-024](../tickets/T-024-loc-ho-so-theo-khoi.md) |
| Phạm vi | `git diff origin/main...HEAD` trên nhánh `team/T-024`, HEAD `d1f5add` (đã gộp `team/T-022` và `main` mới nhất `14ab1ae`). File code/cấu hình đổi: `config/business_profile.md`, `seo_app/content/rules.py`, `seo_app/content/prompts.py`; test mới: `tests/test_business_profile.py`, `tests/test_profile_blocks.py`, `tests/test_soi_loi_t024.py`; 4 báo cáo |
| Ngày | 2026-10-15 |
| **Kết luận** | **T-022: ĐẠT** · **T-024: ĐẠT** (không có lỗi Nghiêm trọng/Cao/Trung bình; 4 lỗi Thấp ghi sổ, đề nghị một phiếu sửa nhỏ cho lỗi #1). Được gộp vào `main`. |

## Tóm tắt (cho chủ dự án)

Hồ sơ doanh nghiệp mà AI đọc khi viết bài giờ **đúng các quyết định của anh**: không năm thành lập, không tên người, không giá (kể cả so sánh rẻ/đắt), không hứa thời gian trả báo giá, khu vực gồm cả Bình Dương và Bà Rịa–Vũng Tàu cũ, địa chỉ chỉ 9 cái. Không có khóa, mật khẩu hay thông tin khách hàng nào trong đó. Bộ lọc mới giấu được các dòng "[CẦN XÁC NHẬN]" kể cả khi một ý viết nhiều dòng, gõ chữ hoa/thường, gõ trên Mac, hay dán từ web có ký tự vô hình.

Còn vài cách **gõ sai nhãn** mà bộ lọc chưa nhận (ví dụ quên dấu cách thành `[CẦNXÁC NHẬN]`, hoặc gõ không dấu `[CAN XAC NHAN]`): khi đó ý đó vẫn tới AI. Hồ sơ hiện tại không có lỗi gõ nào như vậy, và bài luôn là nháp anh duyệt trước, nên mức rủi ro thấp. Tôi đề nghị một phiếu nhỏ để bộ lọc nhận luôn các kiểu gõ sai này.

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| 1 | Thấp | Nhãn **gõ sai** không được nhận, ý chưa xác nhận lọt vào prompt: thiếu dấu cách (`[CẦNXÁC NHẬN]`, `[CẦN XÁCNHẬN]`, góp ý (d) của Soi Lỗi), **gõ không dấu** (`[CAN XAC NHAN]`, khi quên bật bộ gõ tiếng Việt), dùng ngoặc tròn `(CẦN XÁC NHẬN)` hoặc quên ngoặc | `seo_app/content/rules.py:19` (`\s+` và chỉ nhận `[` + chữ có dấu) | Đã chạy thử: `confirmed_profile("- BI MAT [CẦNXÁC NHẬN]")` → giữ nguyên dòng; tương tự với `[CẦN XÁCNHẬN]`, `[CAN XAC NHAN]`, `(CẦN XÁC NHẬN)`, `CẦN XÁC NHẬN`. Chủ dự án sửa file bằng Notepad, gõ sai nhãn → `system_prompt` (`seo_app/content/prompts.py:60`) đưa ý đó vào khung `<ho_so_doanh_nghiep>` với tiêu đề "thông tin đã được chủ doanh nghiệp xác nhận" → AI có thể dùng thông tin chưa chắc (ví dụ "khoảng 500 khách") trong bài **nháp**. Chặn được ở bước anh duyệt nháp. Hồ sơ hiện tại cả 3 nhãn đều gõ đúng (dòng 20, 26, 31), nên **hôm nay không lọt gì** | Phiếu nhỏ (Thợ Máy): đổi mẫu nhãn thành dạng "an toàn khi nghi ngờ": `\[\s*CẦN\s*XÁC\s*NHẬN` và thêm dạng bỏ dấu (so trên chữ đã bỏ dấu, ví dụ `CAN\s*XAC\s*NHAN` sau khi bỏ dấu và đổi `Đ`→`D`), chấp nhận cả `(` lẫn `[`. Các chuỗi này không bao giờ là nội dung thật của hồ sơ nên không lo lọc nhầm. Sửa kèm test `test_misspelled_tags_are_not_recognised`, `test_glued_tag_still_not_recognised_but_invisible_separator_is` (Soi Lỗi đã chỉ chỗ). Không chặn lần gộp này |
| 2 | Thấp | Nhãn đặt trên **tiêu đề** (`## 7. … [CẦN XÁC NHẬN]`) chỉ giấu dòng tiêu đề, các ý bên dưới vẫn tới AI | `seo_app/content/rules.py:96-106` (tiêu đề đứng riêng một khối, đúng yêu cầu 1 của phiếu T-024) | Đã chạy thử: `"## Muc [CẦN XÁC NHẬN]\n- BI MAT"` → AI thấy `- BI MAT`. Chủ dự án có thể nghĩ "gắn nhãn lên tiêu đề là giấu cả mục". Hướng dẫn đầu file (`config/business_profile.md:6-7`) nói nhãn áp cho "ý", không nói gì về tiêu đề | Thêm một dòng ghi chú `>` ở đầu hồ sơ (Ngòi Bút): "Nhãn đặt trên tiêu đề không giấu cả mục; muốn giấu cả mục thì gắn nhãn cho từng ý hoặc thêm `>` trước các dòng". Hoặc (Thợ Máy) cho nhãn ở tiêu đề giấu tới tiêu đề cùng cấp kế tiếp. Có thể gộp vào phiếu của lỗi #1 |
| 3 | Thấp | Đoạn văn **thụt đầu dòng kiểu Word** sau một đoạn có nhãn bị giấu theo (góp ý (a) của Soi Lỗi) | `seo_app/content/rules.py:97` (dòng thụt lề sau dòng trống luôn nối vào khối trước) | `"\tĐoạn 1 [CẦN XÁC NHẬN]\n\n\tĐoạn 2 đúng"` → mất cả Đoạn 2. Đây là **lọc thừa**, không phải lọt: không có thông tin chưa xác nhận nào tới AI, chỉ mất thông tin đúng. Hồ sơ hiện tại không có dòng thụt lề nào sau dòng trống (Soi Lỗi đã đo, kết quả không đổi) | **Không sửa trước khi gộp.** Về bảo mật, lọc thừa là hướng an toàn. Cách sửa Soi Lỗi đề xuất (chỉ nối dòng thụt lề vào khối gạch đầu dòng) lại mở đúng chiều ngược lại: đoạn văn thường + đoạn thụt lề có nhãn bên dưới sẽ để lọt đoạn đầu. Nếu sau này làm thì phải giữ được test SL-024-1 và thêm test cho trường hợp vừa nêu |
| 4 | Thấp | `prompts.py` nhập tên "riêng" `_IGNORABLE_NOT_CF` (có dấu `_`) từ `rules.py` | `seo_app/content/prompts.py:10`, `seo_app/content/rules.py:26-29` | Không phải đường tấn công. Rủi ro bảo trì: ai đó đổi tên/xóa hằng "riêng" trong `rules.py` mà không biết `prompts.py` dùng → `import` lỗi, test bắt ngay (an toàn khi hỏng). Bình luận `rules.py:25` đã ghi "Dùng chung với prompts.py" | Khi tiện, đổi thành tên công khai (`IGNORABLE_NOT_CF`) hoặc đưa vào `seo_app/text.py`. Không bắt buộc |

Không phát hiện lỗi Nghiêm trọng, Cao hay Trung bình.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Diff không có khóa/mật khẩu: `git log -p origin/main..HEAD \| grep -inE "api[_-]?key\|password\|secret\|token\|sk-ant\|AIza\|BEGIN PRIVATE"` → không dòng nào. `detect-secrets` không báo file nào trong 10 file đổi. Hồ sơ chỉ có thông tin công khai của doanh nghiệp (hotline `config/business_profile.md:19`, website `:18`) |
| S2 | Không áp dụng | Diff không đụng log, giao diện hay thông báo lỗi. `_read_text` (`seo_app/content/rules.py:133-143`) giữ nguyên, lỗi chỉ ghi tên file, không ghi nội dung |
| S3 | Không áp dụng | Không có biến cấu hình mới; `.env.example` không đổi (`git diff --stat` rỗng) |
| W1 | Không áp dụng | Không đụng `seo_app/wordpress/` hay đường đăng bài |
| W2 | Không áp dụng | Như trên |
| W3 | Không áp dụng | Như trên. Ghi chú: hồ sơ có 2 link (`config/business_profile.md:18-19`), nhưng `DATA_RULES` cấm chèn link (`seo_app/content/prompts.py:24`) và HTML AI trả về vẫn qua bộ lọc cũ trước khi gửi WordPress |
| W4 | Không áp dụng | Không có lệnh gọi mạng mới |
| A1 | Đạt | (1) Hồ sơ đi qua `_block("ho_so_doanh_nghiep", …)` (`seo_app/content/prompts.py:60`, `:46-48`); đếm trong system prompt: 1 thẻ mở khung + 1 lần nhắc tên trong `DATA_RULES`, đúng 1 thẻ đóng. (2) Thẻ khung giả bị vô hiệu: đã thử `</ho_so_doanh_nghiep>`, `<U+200B/…>`, `<U+3164/…>`, `<U+FE0F/bai_viet>`, `＜/dan_y>`, `<U+034F/chat_lieu_that>`, `<U+E0100/du_lieu_tham_khao>` → tất cả thành `‹/…`. (3) Việc chuyển `_IGNORABLE_NOT_CF` **không làm yếu** `_neutralize`: biểu thức chép nguyên văn từng ký tự (so diff `prompts.py` cũ với `rules.py:26-29`), `_neutralize` vẫn dùng nó ở `prompts.py:42`, thứ tự NFKC → bỏ Cf → bỏ ký tự "mặc định bỏ qua" giữ nguyên. (4) Đọc từng dòng phần AI thấy: không câu nào cho AI quyền hơn mức chủ dự án cho. Mục 8 (`config/business_profile.md:124-137`) toàn là **hạn chế** (không bịa, không nêu giá, không hứa thời gian…). Các câu "được phép nói" (`:24`, `:41`, `:43`) đều là câu chủ dự án chốt (BAN-GIAO 7.4, báo cáo T-022 lượt 2). Không có câu kiểu "bỏ qua quy tắc", "làm theo dữ liệu". Hồ sơ là file cấu hình do chủ dự án viết, cùng mức tin cậy với `config/content.toml`, không phải dữ liệu ngoài theo `security.md` 2.4 |
| A2 | Không áp dụng | Không đụng lớp AI hay cách dùng kết quả AI |
| A3 | Đạt (kèm lỗi Thấp #1, #2) | Không có dữ liệu cá nhân khách hàng: hồ sơ chỉ có địa chỉ cửa hàng, hotline doanh nghiệp. Dòng mẫu mục 7 dặn "không ghi tên hay số điện thoại khách" (`config/business_profile.md:117`) và nằm trong ghi chú `>` (AI không thấy). Dòng chưa xác nhận: 3 dòng có nhãn (`:20`, `:26`, `:31`) đều bị lọc; trong phần AI thấy `XÁC NHẬN` = 0 lần. Bộ lọc đã thử 40 cách viết (bảng dưới): mọi cách viết thường gặp đều lọc đúng; chỉ các kiểu **gõ sai nhãn** ở lỗi #1, #2 còn lọt |
| U1 | Không áp dụng | Không đụng `app/` |
| U2 | Không áp dụng | Không đụng `app/`; `.streamlit/config.toml:5` vẫn `address = "localhost"` |
| U3 | Không áp dụng | Không đụng `seo_app/auth.py` |
| F1 | Không áp dụng | Đường dẫn hồ sơ cố định trong code (`seo_app/content/rules.py:15`), không nhận đường dẫn từ người dùng |
| F2 | Không áp dụng | Không đụng ảnh |
| F3 | Đạt | Đọc hồ sơ bằng `encoding="utf-8-sig"` (`seo_app/content/rules.py:136`). Bộ lọc chỉ so khớp chuỗi bằng `re` và `unicodedata` (`:84-130`), không `eval`, `pickle`, `yaml.load`. Các biểu thức không có lồng lượng từ nên không có nguy cơ treo vì regex (ReDoS) |
| D1 | Đạt | `uv.lock`, `pyproject.toml` không đổi (`git diff --stat` rỗng). `pip-audit`: không có lỗ hổng |
| D2 | Đạt | `.gitignore` không đổi: vẫn chặn `.env` (dòng 2), `.env.*` (3), `*service-account*.json` (5), cache (11, 18, 19), `*.sqlite` (23-24) |
| D3 | Đạt | 3 file test mới chỉ nhập `re`, `random`, `unicodedata`, `pytest` và `seo_app.content.{rules,prompts}`; chỉ gọi hàm thuần và đọc file `config/` trong repo. Không có client mạng nào |

### Kiểm tra phần AI thấy với BAN-GIAO 7.4

Chạy `uv run python -c "from seo_app.content.rules import load_rules; print(load_rules().business_profile)"` (101 dòng, trùng với báo cáo Ngòi Bút lượt 2):

| Quyết định | Kết quả | Bằng chứng (dòng trong file `config/business_profile.md`) |
|---|---|---|
| Không năm thành lập | Đạt | Không có năm nào ("2026" = 0 lần). Cụm "năm thành lập" chỉ xuất hiện trong câu cấm (`:23`, `:128`) |
| Không tên người | Đạt | Không có tên người; câu cấm ở `:23`, `:128` |
| Không giá, kể cả so sánh rẻ/đắt | Đạt | Không có con số giá. "rẻ", "đắt", "VND" chỉ có trong câu cấm (`:87`, `:130-131`). Dòng "giá tham khảo theo vật liệu" cũ đã bỏ (ghi chú `:86`) |
| Không thời gian trả báo giá | Đạt | "15 phút", "30 phút" (báo giá) = 0 lần; câu cấm ở `:132-133`. "30–60 phút" ở `:32`, `:129` là thời gian **thợ có mặt**, không phải thời gian báo giá |
| Khu vực gồm Bình Dương, Bà Rịa–Vũng Tàu cũ | Đạt | `:39-41`. Chữ "chi nhánh" chỉ cho quận huyện TP.HCM cũ (`:42-43`), đúng mức chủ dự án xác nhận (báo cáo T-022 lượt 2) |
| Địa chỉ chỉ 9 cái | Đạt | Trụ sở `:46-47` + 8 địa chỉ trang Liên hệ `:48-51` = 9. Câu cấm tự đặt địa chỉ `:52`, `:134-135` |

Hai điểm **không phải lỗi bảo mật**, chỉ chuyển Chỉ Huy cân nhắc nếu muốn hỏi lại chủ dự án: (a) câu "Chỉ được nói 'nhiều năm kinh nghiệm'" (`:24`) là cách Ngòi Bút diễn đạt quyết định "không dùng năm thành lập"; (b) "miễn phí" (`:79`, `:82`, `:133`, `:137`) là cam kết dịch vụ, không phải con số giá. Cả hai đều có trên website và không trái chữ của BAN-GIAO 7.4.

### Thử bộ lọc (40 cách viết, `confirmed_profile`, chữ "BI MAT" là phần chưa xác nhận)

Lọc đúng (không lọt): nhãn ở dòng 1 / dòng 2 của ý; dòng tiếp quên thụt lề; đoạn văn nhiều dòng; dòng thụt lề sau dòng trống; NFD; chữ thường; ngoặc toàn chiều rộng `［ ］`; NBSP, tab, U+200B, U+200D, gạch nối mềm trong nhãn; `[ CẦN XÁC NHẬN ]`; CRLF; CR đơn; U+2028; form feed; `>` có dấu cách / tab / U+200B đứng trước; `＞`; gạch đầu dòng lồng 3 cấp; `1.` và `+`; ghi chú `>` chen giữa ý; dòng chỉ có khoảng trắng hoặc ký tự vô hình giữa ý; gạch đầu dòng tiếp theo gõ liền `-tiep`.

Còn lọt: `[CẦNXÁC NHẬN]`, `[CẦN XÁCNHẬN]`, `[CAN XAC NHAN]`, `(CẦN XÁC NHẬN)`, `CẦN XÁC NHẬN` không ngoặc, nhãn bị ngắt giữa hai dòng → lỗi #1; nhãn trên tiêu đề → lỗi #2. Ba kiểu không thực tế với Notepad (không tính là lỗi): chữ `С` Kirin trong nhãn; dòng tiếp không thụt lề mà bắt đầu bằng `#` hoặc `2. `.

## Quyết định cho hai góp ý Soi Lỗi để ngỏ (T-024 Soi Lỗi, lượt 2)

| Góp ý | Quyết định | Lý do |
|---|---|---|
| (a) Đoạn thụt đầu dòng kiểu Word bị giấu theo | **Ghi sổ rủi ro (lỗi #3), không sửa trước khi gộp.** Không cần phiếu riêng | Hướng hỏng là lọc thừa (an toàn). Hồ sơ thật không bị ảnh hưởng. Cách sửa đề xuất mở lại một đường lọt khác |
| (d) Nhãn gõ liền `[CẦNXÁC NHẬN]` | **Phiếu sau, mức Thấp (lỗi #1)**, không chặn lần gộp này | Hướng hỏng là lọt (không an toàn) nên nên sửa, nhưng cần chủ dự án gõ sai, hồ sơ hiện tại không có, và bài luôn là nháp được duyệt. Sửa rẻ (một biểu thức + test), nên gộp chung với nhãn không dấu và ngoặc tròn |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `No known vulnerabilities found` | Có |
| bandit (`-r seo_app app scripts`) | 1 cảnh báo Thấp: B101 `assert` ở `seo_app/storage/drafts.py:203` | Báo nhầm, file ngoài diff (xem dưới) |
| detect-secrets (`--all-files`) | Không file nào trong 10 file của diff bị báo. Các báo khác nằm trong `.venv/`, `CACHEDIR.TAG`, test và biên bản cũ | Có, giống các lần kiểm trước |
| Soát lịch sử git | `git log -p origin/main..HEAD` (24 commit) lọc `api_key/password/secret/token/sk-ant/AIza/BEGIN PRIVATE`: 0 dòng | Có |
| pytest / ruff | `2023 passed, 3 xfailed in 108.61s`; `ruff check .`: `All checks passed!` | Có |

## Báo nhầm đã loại

- bandit B101 `assert saved.saved_at is not None` (`seo_app/storage/drafts.py:203`): có từ trước, không thuộc diff, chỉ giúp kiểm tra kiểu; đã xếp báo nhầm ở biên bản T-016-020.
- detect-secrets ở `.venv/`, `tests/`, `docs/team/reports/` cũ: chuỗi mẫu/giả, đã xác minh ở các biên bản trước; không file nào của lần này.

## Điều kiện (nếu ĐẠT CÓ ĐIỀU KIỆN)

Không có điều kiện bắt buộc trước khi gộp. Đề nghị Chỉ Huy:

1. Mở một phiếu nhỏ mức Thấp (Thợ Máy, kèm Ngòi Bút cho một dòng hướng dẫn) cho lỗi #1 và #2, trước khi chủ dự án bắt đầu tự điền mục 7 của hồ sơ.
2. Ghi lỗi #3, #4 vào sổ rủi ro mức Thấp.
3. Sau 01/11, giao Lá Chắn chạy lại biên bản này bằng Fable 5.1.

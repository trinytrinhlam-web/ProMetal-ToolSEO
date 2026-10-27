# Tiến độ dự án SEO App (Pro-Metal, suachuacuasat.com)

_Cập nhật: 2026-10-16, 14:16 giờ Việt Nam. Người ghi: Chỉ Huy B (Claude). Chuyển máy hoặc project mới: đọc [`BAN-GIAO.md`](BAN-GIAO.md). Hai Chỉ Huy phối hợp qua [`docs/team/dong-bo.md`](docs/team/dong-bo.md)._

File này tóm tắt toàn bộ công việc: đã làm tới đâu, đang làm gì, còn lại gì. Chi tiết từng phiếu xem ở [`docs/team/board.md`](docs/team/board.md).

## 1. Tóm tắt nhanh

- Đã xong: bộ khung app, kết nối WordPress (chỉ tạo bản nháp), AI viết bài bằng Claude (bước 1–3 của trang Soạn bài), đội agent và quy trình kiểm tra bảo mật.
- Đã lên `main`: tự lưu bài đang soạn, ô nhập khóa API trong Cài đặt, hồ sơ doanh nghiệp (PR #3, bản đầu), ChatGPT và Gemini (T-018), nút Kiểm tra khóa cả 3 hãng (T-023).
- Đã lên `main` 2026-10-15: hồ sơ doanh nghiệp sửa theo trả lời của anh (T-022), bộ lọc hồ sơ chặt hơn (T-024).
- 2026-10-15: bộ test giờ chạy xanh cả trên Windows (T-027).
- Đã lên `main` 2026-10-15 chiều: lớp AI chịu được thư viện lệch phiên bản, chỉ gọi đúng máy chủ chính thức của 3 hãng (T-026).
- Đã lên `main` 2026-10-15 chiều: báo lỗi tiếng Việt khi máy chủ AI trả dữ liệu hỏng (T-028), bộ chặn mạng của test chặt hơn và chạy được trên mọi máy (T-029, T-030).
- Đã lên `main` 2026-10-15 tối: **thử mù mô hình** (T-019) ở Cài đặt → 🤖 Mô hình AI.
- Đã lên `main` 2026-10-16 sáng: bộ lọc hồ sơ nhận cả nhãn `[CẦN XÁC NHẬN]` gõ sai (T-032).
- Đã lên `main` 2026-10-15 tối: test đo tốc độ không còn đỏ oan (T-025).
- **Giai đoạn 2 xong** (2026-10-16): đủ 3 hãng AI, thử mù, bộ lọc hồ sơ chặt, chữ AI không còn thành link.
- Giai đoạn 4: thiết kế xong (T-033), đã chia phiếu; phần meta (T-036) Thợ Máy làm xong, chờ kiểm. Anh đã trả lời 4 câu (16/10); còn vài việc anh làm trên website (mục 4).
- Còn lại: ảnh, tối ưu SEO on-page, kế hoạch và lịch đăng, đăng lên WordPress thật.
- Bộ kiểm tra tự động trên `main`: 4.867 bài, đều qua trên Linux (lần chạy Windows gần nhất: 3.110 bài qua).

## 2. Lộ trình theo giai đoạn

| Giai đoạn | Nội dung | Trạng thái |
|---|---|---|
| 0 | Bộ khung: app Streamlit, đăng nhập bằng mật khẩu, `run.bat` / `run.command`, README | ✅ Xong |
| 1 | WordPress: kiểm tra kết nối, chuyên mục/thẻ, tạo bài nháp, tải ảnh, ảnh đại diện | ✅ Xong |
| 2 | AI viết bài | ✅ Xong (2026-10-16; xem mục 3) |
| 3 | Ảnh: chọn ảnh từ thư mục, nén WebP, đổi tên chuẩn SEO, **giữ nguyên GPS**, alt bằng AI, ảnh AI kèm prompt | ⚪ Chưa làm |
| 4 | Tối ưu on-page: meta title/description, schema, liên kết nội bộ (plugin SiteSEO) | 🟡 Đang làm: thiết kế xong (T-033); schema FAQPage (T-038) đã lên `main`; meta (T-036) và danh sách bài đã đăng (T-037) đang kiểm |
| 5 | Kế hoạch & lịch: nhận kế hoạch (file / dán / Google Sheets), AI đề xuất, hẹn giờ đăng, gửi bài lên WordPress | ⚪ Chưa làm |
| 6 | Theo dõi thứ hạng qua Search Console | ⚪ Chưa làm (anh chốt giữ, 2026-10-15) |

## 3. Giai đoạn 2 chi tiết

| Việc | Trạng thái |
|---|---|
| Lớp AI chung + Claude (Anthropic), mô hình từng việc trong `config/ai.toml` | ✅ Xong |
| Quy trình: ý định tìm kiếm → nghiên cứu đối thủ → dàn ý (anh duyệt) → viết → AI tự rà soát và sửa | ✅ Xong |
| Viết lại từng phần, quay lại bản trước | ✅ Xong |
| AI kiểm tra văn phong, tô câu có vấn đề, nút Áp dụng / Bỏ qua | ✅ Xong |
| Gia cố bảo mật: lọc HTML/link độc trong chữ AI, hiển thị an toàn (T-001 → T-015) | ✅ Xong, đã lên GitHub |
| Tự lưu bài đang soạn, mở lại / xóa bài dở (T-016, T-017, T-021) | ✅ Xong, đã lên GitHub |
| Ô nhập khóa API Claude / ChatGPT / Gemini trong Cài đặt → Kết nối (T-020, T-021) | ✅ Xong, đã lên GitHub |
| Thêm AI ChatGPT (OpenAI) và Gemini bằng thư viện chính hãng (T-018) | ✅ Xong, đã lên `main` |
| Nút Kiểm tra khóa ChatGPT/Gemini trong Cài đặt (T-023) | ✅ Xong, đã lên `main` |
| Hồ sơ doanh nghiệp theo trả lời của anh (T-022) | ✅ Xong, đã lên `main` |
| Bộ lọc hồ sơ: bỏ cả ý khi có nhãn `[CẦN XÁC NHẬN]` (T-024) | ✅ Xong, đã lên `main` |
| Ổn định test đo tốc độ chập chờn (T-025) | ✅ Xong, đã lên `main` |
| 4 lỗi Thấp lớp AI (T-026) | ✅ Xong, đã lên `main` |
| Bộ test chạy xanh trên Windows (T-027) | ✅ Xong, đã lên `main` |
| Chặn thêm UDP, tra tên trong bộ chặn mạng của test (T-029) + test chạy được trên Linux/Mac (T-030) | ✅ Xong, đã lên `main` |
| Nội dung hỏng từ máy chủ AI → báo lỗi tiếng Việt (T-028) | ✅ Xong, đã lên `main` |
| Thử mù mô hình trong Cài đặt (T-019) | ✅ Xong, đã lên `main` |
| Địa chỉ trần, email trong chữ AI không thành link (T-031) | ✅ Xong, đã lên `main` |
| Bộ lọc hồ sơ nhận cả nhãn `[CẦN XÁC NHẬN]` gõ sai và nhãn đặt trên tiêu đề (T-032) | ✅ Xong, đã lên `main` |
| 7 lỗi Thấp còn lại của lớp AI và thử mù (T-034) | ✅ Xong, đã lên `main` |
| README: hướng dẫn 3 hãng AI và thử mù (T-035) | ✅ Xong, đã lên `main` (README mục 7) |
| 3 lỗi Thấp còn lại của bộ lọc hồ sơ (T-043) | ✅ Xong, đã lên `main` (còn 3 lỗi Thấp hiếm gặp theo dõi ở T-045) |

Trên trang Soạn bài, bước 4 (SEO) và bước 5 (Xuất bản) vẫn là **bản demo**. Trang Tổng quan, Kế hoạch và 3 tab đầu của Cài đặt cũng vẫn là demo.

## 4. Việc đang chờ anh

### Việc anh xử lý sáng 28/10 (Chỉ Huy B ghi tối 27/10)

Anh dặn: vấn đề nào chưa giải quyết được thì ghi lại để sáng mai anh xử lý. Đều là việc trên website, phần mềm không tự làm:

1. **Tắt «Enable File-Based Execution» trong Code Snippets** (Snippets → Settings, mục Execution): hiện vẫn đang BẬT. Đây là đề xuất bảo mật từ 20/10 (Lá Chắn T-054). Tắt xong bấm Save, mở vài trang website xem còn bình thường.
2. **Gỡ các mật khẩu ứng dụng cũ trên tài khoản quản trị** (Tài khoản → Hồ sơ → Mật khẩu ứng dụng): Claude_QA_ProMetal, Claude_SEO, Auto_Post_SEO, claude_optimize, SEOManager. Cái nào không còn dùng thì gỡ: mỗi cái có toàn quyền quản trị. Phần mềm SEO chỉ dùng tài khoản Biên tập viên `phan-mem-seo`.
3. **Dọn snippet tạm trong Code Snippets**: «TEMP pm-claude-toolkit (Claude)» đang BẬT và còn khoảng 40 snippet tạm đã tắt (TEMP…, pm-lp-…, pm-purge…). Nhờ người làm web xem cái nào còn cần, còn lại xóa. Snippet tạm đang bật có thể mở đường gọi lạ trên website.
4. **(Không gấp) Trả `.htaccess` về y hệt bản cũ**: tối 27/10 trình sửa `.htaccess` của SiteSEO Pro xóa mất 4 dòng `<IfModule>` (khối WordPress, khối PHP của cPanel). Website vẫn chạy đúng; muốn y hệt thì vào cPanel → File Manager, thay `.htaccess` bằng nội dung file sao lưu `sao-luu-htaccess-2026-10-27.txt` (thư mục `D:\ProMetal-ToolSEO`). **Không dùng trình sửa `.htaccess` của SiteSEO nữa.**
5. **(Không gấp) Thùng rác bài viết**: còn 3 bài «[THỬ T-059]», WordPress tự xóa sau 30 ngày; muốn sạch ngay thì bấm «Dọn sạch thùng rác».
6. Việc cũ vẫn mở (ghi từ 16/10, chưa xác nhận): dọn khối doanh nghiệp rỗng tên của SiteSEO, đoạn «3 chi nhánh…» ở trang chủ, mức giá «$$»; nhờ người làm web xác nhận các đường `/prometal/v1/deploy-files`, `/prometal/v1/purge`, `/code-snippets/v1` bắt buộc đăng nhập quản trị.

7. **Giai đoạn 5 (kế hoạch, lịch, hẹn giờ, đăng bài): 6 câu thiết kế** (báo cáo `docs/team/reports/T-094-tho-may.md`). Theo lời anh dặn «có đề xuất thì làm theo đề xuất», Chỉ Huy **chọn khuyến nghị A cho cả 6 câu**; anh muốn đổi câu nào thì báo sáng mai:
   - 1A: khai báo `google-auth` là thư viện của app (đã có sẵn trong máy vì thư viện Gemini cần, không tải thêm).
   - 2A: file kế hoạch tải lên chỉ nhận CSV/TXT; Excel thì chép rồi dán (B là thêm thư viện `openpyxl`).
   - 3A: kế hoạch nằm ở tab «KeHoach» với các cột cố định (app tìm cột theo tên, anh vẫn sửa tay được).
   - 4A: app tự ghi 4 ô trạng thái trên Sheets sau khi gửi bài.
   - 5A: bài đã là nháp từ trước thì hẹn giờ trong trang quản trị WordPress.
   - 6A: «Cập nhật bài cũ» để giai đoạn sau.
   - Việc anh cần chuẩn bị cho Giai đoạn 5 (khi tới bước thử thật): tạo service account Google, chia sẻ file Google Sheets kế hoạch cho email của service account, lưu file khóa JSON ngoài thư mục dự án.

8. **Sổ rủi ro (Lá Chắn T-094 hỏi):** dòng ngày 15/10 (biến proxy và chứng chỉ của máy có thể chuyển hướng kết nối) hiện chỉ ghi cho thư viện AI. Đề nghị ghi rõ áp dụng cho cả kết nối WordPress và Google. Muốn khai thác phải chiếm được máy trước, mức Thấp. Anh đồng ý thì Chỉ Huy ghi sổ.

9. **Thử lại một bài nháp có một ảnh** sau khi gộp T-059 bước 7 (ảnh trong bài không còn bản thu nhỏ mất GPS): Chỉ Huy tạo bài thử bằng app khi anh có mặt, kiểm nguồn trang chỉ còn file đầy đủ và GPS còn; anh xóa bài và ảnh thử sau.

Đã xong tối 27/10: SiteSEO lên 1.4.2 và bật AI Abilities; tài khoản Biên tập viên `phan-mem-seo` + mật khẩu ứng dụng riêng, Kiểm tra kết nối «SiteSEO: ghi được»; thử thật T-059 (ghi SEO, ảnh còn GPS, từ chối bài đã chuyển trạng thái); xóa ảnh thử; chọn (a) cho ảnh đại diện của theme (không GPS trên điện thoại).

**Anh báo ngày 22/10: hiện chưa có máy Mac.** Bỏ việc nâng `uv` trên Mac. Máy Windows đã đủ: `certifi` mới, `uv` 0.13.4, nên bỏ lời dặn «không dùng app trên Wi-Fi công cộng» trên máy Windows. Khi có máy Mac: chạy `uv self update` rồi mở app bằng `run.command`.

**Anh đã trả lời ngày 21/10: gộp T-075 (`certifi`) và T-055; duyệt nâng công cụ `uv` (T-078). Máy Windows đã lên `uv` 0.13.4. Việc của anh: trên máy Mac mở Terminal chạy `uv self update` (ở mạng nhà hoặc công ty), rồi mở app bằng `run.command`; máy Windows mở lại app bằng `run.bat`. Lời dặn «không dùng app trên Wi-Fi công cộng» bỏ được khi cả 2 máy xong việc này.**

**Anh đã trả lời ngày 21/10: gộp phần chặn shortcode (T-061); duyệt nâng thư viện `certifi` lên 2026.10.19 (T-075, lỗi bảo mật mức Cao: app tin chứng chỉ có khóa bị lộ). Trong lúc chờ T-075 gộp: không dùng app trên Wi-Fi công cộng; sau khi gộp, mở app bằng `run.bat` / `run.command` ở cả 2 máy để tự cập nhật thư viện.**

**Anh đã trả lời ngày 20/10: rút gọn phần ảnh (ảnh Zalo mất GPS): làm màn hình chọn ảnh và phiếu bắt buộc, hoãn tạo ảnh AI và phiếu GPS, chuyển sớm sang SEO và đăng bài.**

**Anh đã trả lời ngày 20/10: agent phụ chạy mức Tối đa và chế độ nhanh (không ultracode); agent chỉ chạy test liên quan, Chỉ Huy chạy toàn bộ test khi gộp.**

**Anh đã trả lời ngày 20/10: chấp nhận rủi ro hard link trong thư mục ảnh (LC-T048-6), đã ghi sổ rủi ro `docs/team/security.md` mục 6.**

**Anh đã trả lời ngày 20/10: nâng lên Pillow 13 (T-058, lựa chọn A).**

**Anh đã trả lời ngày 19/10 năm câu Giai đoạn 3 (ảnh): 1A 2A 3A 4A 5A.** Chi tiết trong `CLAUDE.md`, mục "Quyết định đã chốt".

**Anh đã trả lời ngày 16/10: 1A 2A 3A 4A 5A.** Các việc anh cần làm trên website. Làm lúc nào cũng được, phần mềm vẫn chạy trong lúc chờ:

1. **Đã làm 27/10: cập nhật SiteSEO 1.1.6 → 1.4.2 và bật Abilities.** **Bật Abilities trong SiteSEO.** Vào trang quản trị WordPress → SiteSEO, tìm mục **Abilities** và bật lên. Phần mềm chỉ dùng tính năng này để ghi SEO cho bài **nháp do chính phần mềm tạo**.
2. **Tạo tài khoản Biên tập viên riêng cho phần mềm.**
   - Vào **Người dùng → Thêm mới**, đặt tên ví dụ `phan-mem-seo`, vai trò **Biên tập viên (Editor)**.
   - Đăng nhập bằng tài khoản này, vào **Hồ sơ → Application Passwords** để tạo mật khẩu ứng dụng.
   - Điền vào `.env` (`WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD`). Cách làm chi tiết ở README mục 6.
3. **Dọn 3 chỗ trên website** (anh hoặc người làm web):
   - tắt khối doanh nghiệp rỗng tên của SiteSEO (SiteSEO → Social → Knowledge Graph);
   - bỏ đoạn mô tả thừa ở trang chủ ghi "3 chi nhánh Gò Vấp, Hóc Môn, Thủ Đức";
   - cân nhắc bỏ mức giá "$$".
4. **Nhờ người làm web kiểm tra:** website có các đường `/prometal/v1/deploy-files`, `/prometal/v1/purge`, `/code-snippets/v1`. Nhờ họ xác nhận các đường này **bắt buộc đăng nhập quản trị**. Phần mềm không bao giờ gọi các đường này.
4b. **Cập nhật plugin Code Snippets (quan trọng, Lá Chắn T-054 nêu 20/10):** vào WordPress → Plugins, xem Code Snippets đã ở bản **3.9.2 trở lên** chưa, chưa thì cập nhật. Trong cài đặt Code Snippets, **tắt «Enable file-based execution»** nếu không dùng. Bản cũ có lỗ hổng (CVE-2025-13035) cho mọi tài khoản từ Cộng tác viên trở lên chạy mã trên máy chủ website, không riêng phần mềm. Làm trước khi phần mềm được bật nút Gửi nháp kèm ảnh. **Đã làm 26/10: chủ dự án báo đã cập nhật Code Snippets lên bản 4.0.0** (mục «tắt Enable file-based execution» chưa xác nhận).
5. Phần "câu chuyện khách hàng thật" trong hồ sơ doanh nghiệp: anh bổ sung khi rảnh (mục 7 của `config/business_profile.md` có hướng dẫn).
6. **Chạy kiểm tra trên Windows:** khi mở máy Windows với Chỉ Huy A, nhờ A chạy `uv run pytest` một lượt.

Đã trả lời 2026-10-16: 1A (ghi SEO qua Abilities của SiteSEO), 2A (tài khoản Biên tập viên riêng), 3A (đuôi "| Pro-Metal" khi còn chỗ), 4A (dọn chỗ trùng trên website), 5A (thêm thư viện Pillow cho Giai đoạn 3).

Đã trả lời 2026-10-15: không có hãng AI mặc định (đủ 3 hãng, anh tự đổi khi cần); giữ Giai đoạn 6; đưa thư mục kế hoạch lên repo (`docs/plan/`); lập phiếu điều phối chung cho 2 Chỉ Huy (`docs/team/dong-bo.md`).

Đã trả lời 2026-10-14: dùng thư viện chính hãng cho ChatGPT/Gemini; gộp PR #3 sau khi sửa; báo giá không nêu thời gian; không nói giá dưới dạng nào; khu vực gồm cả Bình Dương và Bà Rịa–Vũng Tàu cũ; mỗi agent một phiên con, mỗi phiếu một nhánh tạm.

## 5. Việc bắt buộc khi làm phần đăng bài lên WordPress (Giai đoạn 5)

Lá Chắn (agent bảo mật) yêu cầu, vì website **không có bản thử nghiệm**:

- Mặc định mọi bài là bản nháp; đăng ngay hoặc hẹn giờ chỉ khi anh bấm xác nhận.
- Màn hình xác nhận liệt kê **mọi link** trong bài, đánh dấu địa chỉ lạ.
- Lọc toàn bộ HTML cuối cùng trước khi gửi, kể cả phần anh tự gõ.

Danh sách đầy đủ ở cuối [`docs/team/board.md`](docs/team/board.md).

## 6. Quyết định anh đã chốt

- Push thẳng lên nhánh `main`, không tạo nhánh mới; giữ repo gọn.
- Không cần tiết kiệm chi phí mô hình AI.
- Giữ nguyên vị trí GPS trong ảnh (cố ý, cho SEO địa phương).
- Plugin SEO của website: SiteSEO. Không có site thử nghiệm.
- Không dùng năm thành lập, tên tác giả, bảng giá trong bài.
- Khóa API nhập trong app nhưng vẫn chỉ lưu trong file `.env` trên máy, không bao giờ lên GitHub.

## 7. Đội agent

Chỉ Huy (Claude) điều phối. Mọi việc đi qua phiếu → làm → Soi Lỗi kiểm thử → Lá Chắn kiểm bảo mật → mới đưa lên GitHub.

| Agent | Việc | Mô hình |
|---|---|---|
| Thợ Máy | Logic Python (`seo_app/`) | Opus 5.5 |
| Họa Sĩ | Giao diện (`app/`) | Opus 5.5 |
| Ngòi Bút | Prompt, quy tắc văn phong (`config/`) | Opus 5.5 |
| Soi Lỗi | Kiểm thử | Opus 5.5 |
| Lá Chắn | Bảo mật, có quyền chặn | Fable 5.1 (đang tạm chạy Opus 5.5 vì Fable bị giới hạn tới 01/11) |
| Thư Ký | Tài liệu | Sonnet 5.5 |

Hướng dẫn cho AI khác tiếp tục: đọc [`AGENTS.md`](AGENTS.md) trước.

## 8. Ghi chú để làm sau

- Kiểm lại các phiếu T-013 → T-021 bằng Fable 5.1 sau ngày 01/11.
- Thư Ký cập nhật README: nhập khóa API trong Cài đặt → Kết nối, bài đang soạn được tự lưu.
- Meta title/description chưa được lưu vào nháp (làm khi tới Giai đoạn 4).

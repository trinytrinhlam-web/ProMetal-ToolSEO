# Biên bản bảo mật T-095 · README: bước SEO trên trang Soạn bài, tài khoản WordPress cho app

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-095](../tickets/T-095-readme-buoc-seo-tai-khoan-wordpress.md) (Thư Ký) |
| Phạm vi | **Rút gọn, chỉ đọc README** (yêu cầu bảo mật riêng: D1, không lộ bí mật trong tài liệu). Diff `10c7933..88d9606`: `README.md` (+143/−25), báo cáo Thư Ký. Đối chiếu với code trên nhánh (đã có T-041, T-084): `app/views/write.py`, `app/views/wordpress.py`, `seo_app/wordpress/client.py`, `seo_app/storage/site_index.py`, `seo_app/images/folders.py`; `.env.example`, `.gitignore`; ghi chú 27/10 của `docs/team/tickets/T-059-thu-that-ghi-seo-mot-bai-nhap.md`; quyết định 2A (`CLAUDE.md`), `security.md` 2.1, 2.2 |
| Ngày | 2026-10-27 (22:37–23:07 +07, giờ máy; phiên bị ngắt 1 lần vì hết lượt dùng, làm tiếp từ 23:02) |
| **Kết luận** | **ĐẠT.** Không phát hiện lỗi. README hướng dẫn tài khoản đúng quyết định 2A, không hứa điều app chưa làm, không có bí mật, tên tài khoản thật hay đường dẫn máy. **Gộp `main` được ngay** (thử gộp không xung đột, `main` không đổi `README.md` từ gốc nhánh) |

## Tóm tắt (cho chủ dự án)

Phần README mới **an toàn và đúng với phần mềm**. Hướng dẫn tạo tài khoản đi đúng cách đã chốt: một tài khoản **Biên tập viên** riêng cho app (không dùng tài khoản quản trị), mật khẩu ứng dụng tạo **trên chính tài khoản đó**, dòng `WORDPRESS_USERNAME` là **tên đăng nhập** (đúng chỗ đã nhầm hôm 27/10), và có nhắc thu hồi mật khẩu ứng dụng không dùng, nhất là trên tài khoản quản trị. Phần bước SEO nói đúng những gì app làm và **chưa** làm: công tắc «Ghi SEO lên website» mặc định tắt, chỉ ghi vào bài nháp app vừa tạo trong lần gửi đó; đường dẫn, liên kết nội bộ, schema chưa gửi lên website. Tôi đối chiếu từng câu thông báo, tên nút README trích với code: đều khớp. README không có khóa, mật khẩu, tên tài khoản thật hay đường dẫn trên máy.

## Lỗi phát hiện

Không phát hiện lỗi.

## Kiểm từng việc được giao

| Việc | Kết quả | Bằng chứng |
|---|---|---|
| Tên nút, câu nhắc khớp code | **Đạt** | Script tách mọi câu trích «…» ở dòng README thêm mới (39 câu, kể cả câu lồng nhau), bỏ dấu «…», so từng mảnh với `app/`, `seo_app/`, `config/`: mọi câu của app đều có. 10 câu script báo «không thấy» đều có lý do: 4 câu là chữ ghép lúc chạy (`st.markdown(f"{'✅' if ok else '⚠️'} {text}")` với `"SEO: tiêu đề, mô tả, đường dẫn đã sẵn sàng"` và `"SEO: … chưa dùng được (xem bước SEO)"`, `write.py:3110`, `:2441-2442`; «Viết bài: ✅», «Tải ảnh lên: ✅», «Tài khoản: … — vai trò: editor» từ `wordpress.py:68-71`; «Bản 1/…» từ `write.py:2128`), 2 câu là tên mục của chính README («App nhớ việc đã gửi», «Cần biết khi gửi»), «Chờ duyệt» là trạng thái bài của WordPress, «dưới 2m» là lời khuyên cách viết. 20 tên nút/nhãn in đậm của app đều có (`grep -rF`): «Ghi SEO lên website», «✨ AI gợi ý tiêu đề và mô tả SEO», «🔄 Tải lại danh sách bài», «✨ AI gợi ý liên kết», «Dùng schema Hỏi đáp (FAQ) này cho bài», «Schema (dữ liệu có cấu trúc cho Google)», «Chép sang SiteSEO», «Xem trước trên Google», «Mở bài nháp trong WordPress», «Tạo thêm một bài nháp mới», «Kiểm tra kết nối», «Tải chuyên mục và thẻ», «Đường dẫn (slug)», «Gợi ý lại từ từ khóa», «🖼️ Ảnh»… Câu «SiteSEO: ghi được / chưa bật (…) / chưa dò được (…)» khớp `client.py:455-464`; «WordPress từ chối đăng nhập (mã 401)…» khớp `client.py:1546`; câu mục 8 «Chưa thấy thư mục ảnh số … trên máy này (USB chưa cắm hoặc Google Drive chưa chạy?)» khớp `folders.py:627-628` (T-084 đã có trên `main`); «dùng lại tới 6 giờ» khớp `DEFAULT_MAX_AGE_HOURS = 6.0` (`site_index.py:38`) |
| Tài khoản đúng tinh thần quyết định 2A | **Đạt** | `README.md:63-117` (mục 6): bước 1–2 tạo tài khoản riêng vai **Biên tập viên** bằng tài khoản quản trị, câu mở «Đừng dùng tài khoản quản trị cho app» kèm lý do đúng (Biên tập viên không cài plugin, không đổi cài đặt: lộ mật khẩu ứng dụng thì thiệt hại **nhỏ hơn**, không nói là không có); bước 3–6 tạo mật khẩu ứng dụng **trên tài khoản Biên tập viên** (đăng xuất rồi đăng nhập lại), tên mật khẩu chỉ để nhận ra; bước 7 `WORDPRESS_USERNAME` là tên đăng nhập, **không phải** tên đặt cho mật khẩu ứng dụng, cách tra tên đăng nhập; bước 10 Kiểm tra kết nối phải thấy «vai trò: editor», thấy `administrator` thì làm lại bước 3–7. «Lưu ý trên website» (`:119-122`): thu hồi mật khẩu ứng dụng không dùng, nhất là trên tài khoản quản trị (mật khẩu ứng dụng mang đủ quyền của tài khoản chứa nó). Bảng lỗi: dòng «không đủ quyền» (`:130`) bỏ «hoặc Quản trị viên» của bản cũ, chỉ còn Biên tập viên. Khớp `security.md` 2.2 («nên có vai trò Biên tập viên, không phải Quản trị viên (ghi trong README)») và ghi chú T-059 19:37 |
| Không hứa điều app chưa làm | **Đạt** | Mục 10, «Ghi SEO lên website» (`README.md:400-…`): công tắc **mặc định tắt** (`seo_toggle`, khóa `seo_write` không lưu vào nháp); bật thì ghi tiêu đề, mô tả, từ khóa chính vào **chính bài nháp app vừa tạo trong lần gửi đó** (`write_seo` chỉ dùng `result["post_id"]` của lần gửi này; client chỉ nhận mã trong `_created_post_ids`, kiểm còn nháp trước khi ghi, `client.py` `set_seo_meta`); «bài nháp tạo ở lần gửi trước, bài đã chuyển sang «Chờ duyệt» hay đã đăng đều không bị đụng tới» (khớp T-086 Ghi nhận 2 và lần thử thật T-059 (3): bài «Chờ duyệt» bị từ chối, không lệnh ghi); «Đường dẫn, liên kết nội bộ, schema không ghi»; ô bị Chặn thì không ghi riêng ô đó. «App chưa chèn các liên kết này vào bài nháp khi gửi», «app chưa gửi schema lên website», mục 11 «chuyên mục, đường dẫn (slug), liên kết nội bộ, schema chưa gửi» đúng với `create_draft_with_images(title, parts)` (không slug, không link chèn, không schema). README **không** nói app tự chặn tài khoản quản trị (app không làm việc đó): chỉ bảo người dùng tự xem dòng «vai trò» |
| Không lộ bí mật, đường dẫn máy (D1) | **Đạt** | Không dạng khóa nào (`sk-ant`, `AIza…`, `ghp_`, `xox`, `AKIA…`, `PRIVATE KEY`); không tên tài khoản thật của website (tên Biên tập viên thật ghi trong T-059 **không** có trong README, README dùng tên mẫu `bien-tap-seo`), không tên mật khẩu ứng dụng thật, không đường dẫn bản sao `.htaccess` trên máy (có trong ghi chú T-059, không đưa vào README), không đường dẫn kiểu `C:\Users…`, `D:/…`, `/Users/`, `/home/`. Dòng thêm mới không có tên miền thật (chỉ `ten-mien-cua-ban`). Mật khẩu ứng dụng ví dụ là dãy mẫu có từ trước (`abcd efgh ijkl mnop qrst uvwx`). File nhắc tới (`data/site_index.sqlite`) là đường dẫn tương đối trong dự án, nằm trong `data/` đã bị `.gitignore` chặn (`.gitignore:22`) |
| Lời khuyên về website không làm yếu bảo mật | **Đạt** | «Không dùng trình sửa `.htaccess` của SiteSEO Pro» (đúng sự cố 27/10), sửa `.htaccess` qua cPanel và sao lưu trước; không bảo tắt plugin bảo mật hay mở quyền; dòng 401 vẫn giữ hướng «nhờ người quản lý website kiểm tra» khi đã đúng tên và mật khẩu |

## Danh sách kiểm tra

Phiếu chỉ đổi tài liệu: các dòng về code là «Không áp dụng».

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` (đặt `PYTHONUTF8=1`) trên `README.md` và báo cáo Thư Ký, kèm file mồi tiếng Việt: mồi bắt 2/2, hai file thật 0. `git diff 10c7933..88d9606` không có dạng khóa |
| S2 | Đạt | README không in giá trị bí mật nào; hướng dẫn chỉ đặt mật khẩu ứng dụng vào `.env` |
| S3 | Không áp dụng | Không biến mới; `.env.example` không đổi (xem Quan sát 1) |
| W1 | Đạt | README không hướng dẫn đăng bài; «App chỉ tạo bài nháp» giữ nguyên |
| W2 | Đạt | README nói đúng: app không ghi SEO vào bài có sẵn, bài nháp lần trước, bài «Chờ duyệt» hay đã đăng |
| W3, W4 | Không áp dụng | Không đổi code gửi lên website, không lệnh mạng |
| A1–A3 | Không áp dụng | Không đổi lời dặn AI |
| U1–U3 | Không áp dụng | Không đổi giao diện, đăng nhập |
| F1–F3 | Không áp dụng | Không đọc/ghi file |
| D1 | Đạt | Không thư viện mới; mục «Không lộ bí mật» ở trên (yêu cầu D1 của phiếu) |
| D2 | Không áp dụng | `.gitignore` không đổi (vẫn chặn `data/`) |
| D3 | Không áp dụng | Không có test |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| detect-secrets 1.5.0 | **Đặt `PYTHONUTF8=1`**, `--all-files` trên bản sao `README.md`, `docs/team/reports/T-095-thu-ky.md` và file mồi có chữ tiếng Việt (khóa AWS mẫu, `password = …` giả): mồi bắt **2/2**, hai file thật **0** | Có. Đã xóa file mồi |
| Tìm chữ | `grep` README cho tên tài khoản, tên mật khẩu ứng dụng thật trong ghi chú T-059, đường dẫn máy, dạng khóa; dòng thêm mới tìm tên miền thật: 0 (chỉ dòng có từ trước nhắc tên kho `ProMetal-ToolSEO` khi tải dự án về) | Có |
| Đối chiếu câu trích | Script trong thư mục nháp (`quotes2.py`): 39 câu «…», 10 câu không thấy nguyên văn đều giải thích được (mục «Kiểm từng việc»); 20 nút/nhãn: có đủ | Có |
| pip-audit, bandit, pytest, ruff | Không chạy: phiếu chỉ đổi `README.md` và báo cáo, không đổi code, `uv.lock`, test | — |
| Thử gộp | `git merge-tree --write-tree origin/main origin/team/T-095` (`main` `bc29fdb`): không xung đột; `main` không đổi `README.md` từ gốc nhánh `10c7933`; gốc nhánh và T-084 (`ba12878`) đều đã nằm trên `main`, nên lưu ý «gộp sau T-084» trong báo cáo Thư Ký không còn cần | Có |

## Quan sát (không tính là lỗi)

1. **`.env.example` (đề xuất 2 của Thư Ký, tôi đồng ý):** dòng `WORDPRESS_USERNAME` hiện ghi «Tên đăng nhập WordPress của tài khoản sẽ đăng bài» (`.env.example:23-24`). Nên ghi rõ «tên đăng nhập của tài khoản Biên tập viên riêng cho app, không phải tên đặt cho Application Password»; dòng `WORDPRESS_APP_PASSWORD` thêm «tạo trên chính tài khoản đó». Đây đúng chỗ đã nhầm hôm 27/10, và `.env.example` là chỗ chủ dự án nhìn khi điền. Việc nhỏ cho phiếu dọn sau (Thư Ký hoặc Thợ Máy), không chặn gộp.
2. **Câu chú thích khung «Chép sang SiteSEO» trên app** (đề xuất 1 của Thư Ký) nói «dán vào hộp SiteSEO» cho cả ba khung, README nói đúng hơn (đường dẫn dán vào ô slug của bài). Chỉ là câu chữ, không liên quan bảo mật.
3. Vai **Biên tập viên** vẫn sửa, xóa được mọi bài trên website (không riêng bài app tạo). README nói đúng mức «thiệt hại nhỏ hơn nhiều» so với tài khoản quản trị, và đã dặn giữ mật khẩu ứng dụng trong `.env`, thu hồi khi không dùng. Không cần đổi gì.

## Báo nhầm đã loại

Không có (công cụ không báo mục nào ở file thật).

## Điều kiện

Không có. Kết luận **ĐẠT**; quan sát 1 nên làm ở một phiếu dọn nhỏ sau, không bắt buộc.

Không có rủi ro nào cần chủ dự án quyết định chấp nhận; không thêm dòng vào sổ rủi ro (`security.md` mục 6).

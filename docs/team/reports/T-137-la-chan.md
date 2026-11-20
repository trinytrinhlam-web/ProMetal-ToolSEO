# Biên bản bảo mật T-137 · Nhắc chống gửi trùng sau khi file nháp bị cất sang một bên (SL-T136-1, G4) · đầy đủ

> **Model:** **Fable 5.1** (dòng «You are powered by»: Fable 5.1, kiểm đầu lượt; hạn mức tuần Fable đã mở lại). Chỉ Huy B giao 18/11.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **Fable 5.1** · dưới Chỉ Huy B |
| Phiếu được kiểm | T-137 (phiếu trên `main`; lỗi gốc SL-T136-1, G4 của Soi Lỗi T-136; yêu cầu sửa của Lá Chắn T-136 lượt 2). Nhánh `team/T-137` từ `team/T-136` `6a005c1`: Họa Sĩ `2ee7152` (mã, test), `5daf638` (báo cáo); Soi Lỗi đầy đủ `619c229` (ĐẠT, 0 lỗi mới, G-1 → G-5). Đầu nhánh **`619c229`**, đã push |
| Phạm vi | **Đầy đủ**: diff `6a005c1..619c229` (`app/views/write.py` +53: nhánh cổng mới trong `publish_panel`, `moved_box`, `remember_moved`, câu `MSG_MOVED_*`; `app/views/home.py` +18: lời nhắc thường trực; `seo_app/storage/drafts.py` +49: `moved_aside_names`, `_MOVED_TAIL`, `_db_message(exc, path)`; `README.md` +1; 2 file test mới), đọc cùng phần không đổi mà cổng mới nối vào: `publish_panel` cả hàm, `send_lock_state`, `confirm_box`/`remember_confirm`, `COMPOSE_KEYS`, `KEEP_KEYS`, `_wp_reset_guards`, đường `clicked and allowed` → `send_draft`. Không sửa mã; không chạm website, Google; chỉ chạy test trong `wt-T-137` |
| Ngày | 2026-11-18 (giao ≈ 13:10, xong 13:48, +07, giờ máy) |
| Máy | Windows 11 Pro 10.0.26300, Python 3.12.15, SQLite 3.53.1, uv 0.13.4. Chỉ chạy test liên quan, không chạy toàn bộ; lô test chạy nền trong worktree |
| **Kết luận** | **ĐẠT**, **gộp `main` được ngay** (`main` `3202035` đã có T-136: `git merge-tree` không xung đột; từ `6a005c1` `main` không sửa file nào của phiếu): 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp mới. Cả 6 trọng tâm Chỉ Huy giao **đạt**; **SL-T136-1 và G4 đóng** đúng cả 6 yêu cầu Lá Chắn T-136 lượt 2 đặt ra. Cổng mới chỉ **thêm** (một `elif` sau hai nhánh khóa có sẵn, `allowed = allowed and …`), không nới T-089, T-092, T-130, W1. Về phía Lá Chắn, **SL-T136-1 không còn chặn việc bật công tắc Hẹn giờ/Đăng ngay cho bài thật**; còn lại là buổi thử thật (T-128, ca R bản cuối đã sửa theo G-2). Soi Lỗi G-1: Thấp, có từ T-092, không chặn; phiếu sau |

## Tóm tắt (cho chủ dự án)

Phiếu này vá lỗi nhỏ tôi và Soi Lỗi ghi ở T-136: sau khi file nháp bị chương trình khác làm hỏng và app cất nó sang một bên, app không còn nhắc gì và có thể để gửi trùng. **Đã vá đúng, gộp được.**

- **Chừng nào file cũ còn trong thư mục `data`:** trang Bài viết luôn nhắc (không còn ghi sai «Chưa có bài nào…»); ở bước Xuất bản, bài chưa có dấu «đã gửi» phải tick **«Tôi đã xem trên WordPress: bài này chưa có trên website»** ở mọi hình thức (Nháp, Hẹn giờ, Đăng ngay) thì nút gửi mới mở. Ô không tick sẵn; đổi bài, sửa bài, đổi hình thức hay sau mỗi lần bấm gửi thì phải tick lại.
- **Không nới khóa nào đang có:** bài đã có dấu «đã gửi» vẫn khóa đúng như cũ, không thêm ô thừa. Tôi đọc từng nhánh của nút gửi và đường bấm: cổng mới chỉ **thêm** một điều kiện.
- **App chỉ nhìn tên file đã cất**, không mở file đó; tên phải đúng khuôn app tự đặt, nên file lạ khác trong thư mục `data` không gây nhắc oan.
- **Câu báo sai nguyên nhân («chỉ đọc»)** khi đầu file bị sửa nay là «bị lỗi… thử tải lại trang», rồi lần sau app cất file; file chỉ đọc thật vẫn báo «chỉ đọc».
- **Việc của anh/chị (sau khi gộp):** nếu thư mục `data` của app đã có file tên dạng `drafts.hong-…sqlite` từ các lần thử trước, lời nhắc và ô tick sẽ hiện ngay cho mọi bài chưa gửi. Đối chiếu trên WordPress xong thì tự dời các file đó ra khỏi thư mục `data` (README mục «Gửi nháp»); app không tự xóa.

## Kết quả theo trọng tâm Chỉ Huy giao

### 1. Cổng mới chỉ THÊM, không nới T-089, T-092, T-130, W1 — **đạt**

**Chuỗi nhánh của `publish_panel`** (`write.py:4358`; đọc nguyên văn `:4446-4471`):

| Thứ tự | Điều kiện | Ô tick | Ghi chú |
|---|---|---|---|
| `allowed` ban đầu | client, không mục bị chặn, có gói dựng được, không dòng Chặn | | Không đổi |
| 1 | `_wp_maybe_draft`, hay lỗi đọc trạng thái gửi, hay `lock` đang gửi / gửi dở | «Tôi đã kiểm tra trang quản trị, vẫn muốn gửi» | Không đổi |
| 2 | tab đã gửi (`_wp_sent`) hay `lock.post_id` có | «Tạo thêm…» (`AGAIN_LABELS`) | Không đổi |
| **3 (mới)** | `moved := draft_storage.moved_aside_names()` khác rỗng | «Tôi đã xem trên WordPress: bài này chưa có trên website» | `allowed = allowed and moved_box(...)` |
| sau chuỗi | Hẹn giờ, Đăng ngay: `confirm_box` | «Tôi đã đọc lại toàn bài…» | Không đổi |

- `lock = send_lock_state(saved, saved_error)` (`:4196`, không đổi): trạng thái trong kho, hay điều tab biết khi kho đọc ra «chưa gửi» (T-092). Vì vậy tab biết «đã gửi 501» đi nhánh 2 (khóa cũ thắng), tab biết «gửi dở» đi nhánh 1; chỉ bài **không có** trạng thái nào (kho «chưa gửi», tab không biết) mới tới nhánh 3. Không có file đã cất thì `elif` rơi qua: hành vi **y hệt** trước T-137 (Soi Lỗi: 21 bước của tab đã biết y hệt; đột biến P7, M2 «cổng mới thay khóa cũ» bị bắt).
- **Chỉ thêm điều kiện:** `allowed` chỉ bị `and` thêm, không gán lại ở nhánh mới; `send_and_record`, so rồi đặt (T-089), `known_send_state`, `send_lock_state`, dòng mồ côi (T-130), màn hình xác nhận không đổi dòng nào (diff `write.py` chỉ có 5 khối: `COMPOSE_KEYS`, câu, `remember_moved`/`moved_box`, danh sách `_wp_reset_guards`, nhánh `elif`).
- **Nút bấm lọt:** `if clicked and allowed` (`:4480`) xét lại `allowed` trong **cùng lần chạy** với cú bấm (SL-T056-1), nên cú bấm lọt qua nút khóa (bấm đúp, trạng thái vẽ cũ) không gửi khi chưa tick; Họa Sĩ `test_click_through_gate_sends_nothing`, Soi Lỗi `test_duong_2…`, `test_tab_biet…` (vá `st.button` theo khóa `wp-send`, có đối chứng). `send_draft` nhận `post_id`, `seen` như cũ.
- **Mã băm ô tick:** `moved_box` (`:3368`) theo đúng mẫu `confirm_box` (`:3348`): `on_change=remember_moved` (`:3362`) chạy đầu lần chạy sau, lúc `_wp_shown` vẫn là mã băm của màn hình người dùng đã thấy; lần vẽ sau so `_wp_moved_digest` với `built.digest` (gồm chữ, ảnh, SEO, hình thức, giờ hẹn, công tắc SEO): khác thì bỏ tick, báo `MSG_MOVED_RESET`. Hai khóa `_wp_moved_ok`, `_wp_moved_digest` nằm trong `COMPOSE_KEYS` (`:191-193`, xóa khi đổi bài, `:522`), không nằm trong `KEEP_KEYS` (`:206-217`), và bị bỏ trong `_wp_reset_guards` (`:4364-4374`) ngay **trước** mỗi lần gửi (`:4484`): lần gửi hỏng giữa chừng cũng phải tick lại. Tick ở bài này không mang sang bài khác, không mang sang trang khác. Đột biến P3–P6, P6b, M3, M4 bị bắt.
- **W1:** không thêm đường gửi, không thêm lệnh tới website; «Đăng ngay», «Hẹn giờ» vẫn qua `confirm_box` và công tắc; cổng áp cả Nháp (nháp trùng cũng là một bài trên website).

### 2. `moved_aside_names`: chỉ tên, sau `dir_has_link`, khuôn chặt, không mở hay `stat` file đã cất — **đạt**

`drafts.py:1331-1361`: `dir_has_link(path.parent, PROJECT_ROOT)` **trước**, liên kết → `()`; rồi `[entry.name for entry in path.parent.iterdir()]` (chỉ tên từ danh sách thư mục, không `stat`, không mở); `OSError` → `()`. Khuôn `re.escape(stem) + _MOVED_TAIL + re.escape(suffix)` với `fullmatch`; `_MOVED_TAIL` (`:193`) = `.hong-[0-9]{8}-[0-9]{6}` + tùy chọn `-N` (N 2–9999, đúng cách `_move_aside` đánh số từ 2); `strptime` loại ngày giờ không có thật; chữ số chỉ ASCII (`\d` và `strptime` nhận chữ số toàn khối, Ả Rập: đột biến Q3, M12 bị bắt). Mới nhất trước. Probe (mục Thử độc lập): 12 tên, chỉ 3 tên đúng khuôn được nhận, đúng thứ tự; móc `sys.addaudithook`: **0** lần mở file `hong` khi dò (Soi Lỗi cũng kiểm bằng móc). Gọi ở mỗi lần vẽ hai trang: một `dir_has_link` và một lần liệt kê thư mục, rẻ.

### 3. G4: mã 8 + `newer_file_format` → file lạ; READONLY thật vẫn «chỉ đọc» — **đạt**

`_db_message(exc, path)` (`drafts.py:1943`): mã 8 **và** `sqlite_file.newer_file_format(path)` (bản T-136 lượt 2: chỉ đọc 20 byte của file thường, mở không chờ) → `_MSG_BROKEN`; mã 8 mà đầu file bình thường → `_MSG_READONLY`. `_connect` vốn đặt `_ready = False` với lỗi không phải «bận» nên thao tác kế kiểm lại file → `is_healthy` thấy byte 18 > 2 → cất sang một bên → ba trang báo `MSG_RECOVERED`, `moved_aside_names` thấy tên mới. Probe: kho đang dùng, byte 18 = 3 → lần lưu 1 `_MSG_BROKEN` (không còn «chỉ đọc»), lần 2 kho đã cất file (`drafts.hong-20261118-131513.sqlite`), dấu «đã gửi» nằm trong file cất đi; file chỉ đọc thật (`chmod`) → `_MSG_READONLY`, không cất. Đường đọc đầu file chỉ chạy trên nhánh lỗi mã 8, không thêm việc đọc nào ở thao tác thường.

### 4. Câu nhắc không in đường dẫn, có thoát Markdown — **đạt**

`MSG_SENT_MOVED` (`home.py:46`), `MSG_MOVED_GATE` (`write.py:350`), `MSG_MOVED_PLAN`, `MSG_MOVED_RESET`, `MOVED_CHECK_LABEL`: chữ cố định; chỗ chèn chỉ có tên file **mới nhất** (đã qua khuôn chặt, ký tự ASCII) qua `escape_markdown`, số file cũ hơn (`len(moved) - 1`), và Mã bài WordPress chỉ khi `_plan_ref.wp_post_id` là `int` (đã qua `DraftPlanRef`). Không đường dẫn, không `unsafe_allow_html`; `**Bài viết**` in đậm là chủ ý. Trang Bài viết: lời nhắc thay dòng «Chưa có bài nào…» nhưng danh sách bài (nếu có) vẫn hiện (`home.py:307-313`). README một đoạn đúng nhãn ô, tên cột, cách tắt (Họa Sĩ có ca đối chiếu README với chữ trên trang).

### 5. Năm ghi nhận của Soi Lỗi — **xét xong, không chặn**

| Ghi nhận | Lá Chắn |
|---|---|
| **G-1** · tab B (không biết) «Lưu lại thành nháp» → nháp có lại **không kèm** «đã gửi 501»; tab A biết nhưng không ghi lại; phiên mới thấy «chưa gửi». Với T-137, còn file đã cất thì phiên mới gặp cổng; người dùng dời file đi rồi thì nháp đó **không còn khóa** | **Thấp, có từ T-092** (Soi Lỗi T-092 G1, Lá Chắn T-092 «khoảng hở còn lại»; T-130 bịt phần xóa nháp, không bịt phần «tab không biết lưu lại»). Cần đủ bốn việc: file nháp bị cất, một tab mở bài **trước** lần gửi rồi lưu lại, người dùng dời file đã cất đi sau khi đã tick «đã xem trên WordPress» cho bài khác, rồi về sau mở đúng nháp đó mà gửi lại không xem website. README dặn đối chiếu **mọi** bài trước khi dời file. **Không chặn gộp, không chặn bật công tắc.** Phiếu sau (Thấp): tab biết «đã gửi» mà kho đọc ra «chưa gửi» **và nháp còn** thì ghi lại trạng thái đã biết kiểu so rồi đặt từ «chưa gửi» (như «Lưu lại thành nháp» của T-092; không ghi đè trạng thái mới hơn), kèm test hai tab; đụng khóa gửi trùng nên Lá Chắn **đầy đủ** |
| G-2 · ca R của kịch bản T-128 sau T-137 | Đúng. Tôi đã sửa bước 6 của **ca R bản cuối** (`T-136-la-chan-ca-R-ban-cuoi.md`, thư mục ghi chú chung): trang Soạn bài ở bước Chuẩn bị không có câu nhắc; lời nhắc và ô tick chỉ ở bước Xuất bản của bài chưa có dấu «đã gửi». Bước 4, 7, 8: trang Bài viết hiện cả lời nhắc lẫn danh sách bài; file đã cất còn tới dòng dọn 12 |
| G-3 · hai khung vàng cùng lúc ở lần vẽ cất file | Đồng ý; chỉ lặp, không sai |
| G-4 · README «dời file đó» khi có nhiều file | Đồng ý, câu chữ; phiếu chữ sau (nói «dời cả các file đó») |
| G-5 · test ghi `data/site_index.sqlite` vào thư mục chạy test | Ngoài phiếu; đã giao T-138. Tôi chỉ chạy test trong `wt-T-137` |

### 6. T-137 có đủ để đóng SL-T136-1 và bỏ điều kiện chặn công tắc — **có**

Đối chiếu 6 yêu cầu Lá Chắn T-136 lượt 2 (mục 2 của lượt đó):

| Yêu cầu T-136 lượt 2 | T-137 |
|---|---|
| 1. Dấu hiệu sống qua lần mở lại app, theo tên `drafts.hong-*.sqlite`, sau `dir_has_link`, khuôn chặt | ✔ `moved_aside_names` (mục 2); Soi Lỗi đường 2 (tắt mở lại app) |
| 2. Không mở, không đọc file đã cất; tên qua `escape_markdown`, không đường dẫn | ✔ mục 2, 4 |
| 3. Lời nhắc thường trực thay «Chưa có bài nào…»; cổng ở **mọi** hình thức cho bài chưa có dấu; không tick sẵn, không nhớ sang bài khác | ✔ mục 1, 4; Soi Lỗi 10 bước trang Bài viết, cổng ở Nháp, Hẹn giờ, Đăng ngay |
| 4. Chỉ thêm cổng; không nới T-089, T-092, T-130; lời nhắc hết khi dời file; câu nhắc nói chỉ dời sau khi đối chiếu | ✔ mục 1; `test_gate_gone_after_moved_file_removed`; README |
| 5. Nêu «Mã bài WordPress» của dòng kế hoạch | ✔ `MSG_MOVED_PLAN` (`test_gate_names_post_id_from_plan_row`) |
| 6. Test hai đường của Soi Lỗi, ca mở lại app, tên lạ không tính | ✔ Họa Sĩ 57 ca, Soi Lỗi 31 ca (52 bước G2 chạy lại: 2 lần gửi trùng không còn) |
| G4 | ✔ mục 3 |

**Kết luận:** SL-T136-1 và G4 **đóng**. Điều kiện B.4 của Lá Chắn T-136 lượt 2 («sửa SL-T136-1 trước khi bật công tắc cho bài thật») **đã xong**. Về phía Lá Chắn, trước khi bật công tắc Hẹn giờ/Đăng ngay cho bài thật chỉ còn **buổi thử thật** theo kịch bản T-128 (ca R bản cuối, có T-137) và quyết định của chủ dự án; G-1 là khuyến nghị phiếu sau, không chặn.

## Lỗi phát hiện

Không có lỗi mới.

## R5

`git diff --stat 6a005c1..619c229 -- tests/`: chỉ thêm `tests/test_t137_nhac_gui_trung.py`, `tests/test_soi_loi_t137.py`; không test cũ nào bị sửa, xóa, thêm `skip`/`xfail`. Mọi `parametrize` (10) đều có `ids=` ngắn.

## Thử độc lập (Fable)

Probe thuần Python trên file tạm (không mạng, không Streamlit; bản lưu trong thư mục nháp của phiên):

| Ca | Kết quả |
|---|---|
| G4: kho đang dùng, byte 18 = 3, lưu hai lần | Lần 1 `_MSG_BROKEN` (không «chỉ đọc»); lần 2 «Nháp này không còn trong kho» (file đã cất); `moved_aside_names` → đúng tên vừa cất |
| G4 đối chứng: file nháp thật đặt chỉ đọc | `_MSG_READONLY`; không cất |
| 12 tên trong `data/`: 3 đúng khuôn (hai cùng giây có `-2`), 9 gần giống (nhật ký, `-1`, giờ 24, chữ hoa, đuôi thêm, kho thẻ ảnh, chữ số toàn khối, `-10000`, 30/02) | Nhận đúng 3, mới nhất trước; 0 lần mở file `hong` (móc `sys.addaudithook`) |

Đọc mã: chuỗi nhánh `publish_panel`, `send_lock_state`, `confirm_box`/`remember_confirm` so với `moved_box`/`remember_moved`, `COMPOSE_KEYS`, `KEEP_KEYS`, `_wp_reset_guards`, đường `clicked and allowed` (mục 1). Ca trang (hai đường của Soi Lỗi, cú bấm lọt, đổi hình thức, mở lại app) tôi không viết lại: Họa Sĩ 57 ca và Soi Lỗi 31 ca đã phủ đúng các điểm tôi yêu cầu, chạy lại trong lô test dưới.

## Danh sách kiểm tra

| Mục | Đạt | Bằng chứng |
|---|---|---|
| Yêu cầu 1–6 của phiếu | ✔ | Mục 1–4; README |
| W1 (không mở đường gửi, khóa gửi trùng không nới) | ✔ | Mục 1 |
| W2 (không đụng website) | ✔ | Không lệnh mới tới website, Google; chỉ liệt kê tên file trong `data/` |
| U1 (chữ thuần, không HTML, thoát Markdown) | ✔ | Mục 4 |
| U2 (không in đường dẫn, `.env`) | ✔ | Chỉ tên file ngắn |
| F1, F3 (không đi theo liên kết, file lạ không đọc) | ✔ | `dir_has_link` trước; không mở file đã cất |
| R5 | ✔ | Mục R5 |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pytest 31 file liên quan trên `619c229`, chạy trong `wt-T-137` (T-137 ×2, T-136 ×3, T-131 ×3, kho nháp, trạng thái gửi T-086, T-089, T-092, T-130, T-100, trang Bài viết, bước Xuất bản T-102, T-112, T-115, `test_app_pages`, T-117) | **740 qua, 1 bỏ qua** (ca FIFO, Windows), 0 xfail, **0 hỏng**, 34 phút 30 giây; `data/site_index.sqlite` trong worktree là của lượt chạy 12/11 (Soi Lỗi G-5, T-138), lô này không tạo thêm | ✔ |
| Probe (mục Thử độc lập) | đúng hướng cả | ✔ |
| `ruff check .`; `ruff format --check` 5 file | sạch; đúng khuôn | ✔ |
| bandit `drafts.py`, `home.py` (`PYTHONUTF8=1`) | 2 báo nhầm có từ trước: B101 `drafts.py:984` (`assert` trong `save`), B608 `drafts.py:1906` (`_oversized_sql` ghép tên cột hằng, T-131) | ✔ |
| detect-secrets (`PYTHONUTF8=1`) 4 file mã, README, 2 test, 2 báo cáo; biên bản này | 2 báo nhầm có từ trước, cùng một chữ: ví dụ địa chỉ web kèm tên đăng nhập, mật khẩu giả trong docstring `write.py:2708` (có từ T-061/T-091) và báo cáo Họa Sĩ nhắc lại; biên bản này: 0 | ✔ |
| Ký tự ẩn (Cf, Cc, CR), NFC trong 6 file | 0; đều NFC | ✔ |
| D1 | `uv.lock`, `pyproject.toml`, `config/` không đổi | ✔ |
| Gộp thử | `git merge-tree --write-tree main HEAD` (`main` `3202035`, đã có T-136) không xung đột; từ `6a005c1` `main` không sửa file nào của phiếu | ✔ |

## Ghi nhận (không xếp lỗi)

1. **Cổng là lời xác nhận của người dùng**, không phải khóa cứng: app không thể biết bài đã có trên website hay chưa khi dấu nằm trong file đã cất (chủ ý B.2 của T-136: không đọc file lạ). Chốt chống gửi trùng **cứng** vẫn là dấu «đã gửi» trong kho hiện tại (T-086, T-089, T-130).
2. Máy chủ dự án có thể đã có file `drafts.hong-…` từ các lần thử trước (Họa Sĩ rủi ro 1): sau khi gộp, lời nhắc hiện ngay. Chỉ Huy báo trước chủ dự án; không ai tự dời file trong thư mục app.
3. `moved_box` vẫn vẽ ô tick khi gói chưa dựng được (`built is None`); `allowed` khi đó đã sai nên không ảnh hưởng.
4. Tick ô cổng lúc `_wp_shown` còn trống (lần vẽ trước lỗi dựng) rồi lần sau dựng được: ô bị bỏ tick kèm câu «Bài đã thay đổi…» hơi lệch nghĩa, nhưng đóng về phía an toàn.

## Điều kiện

**A. Gộp `main`: được ngay.** Chỉ Huy chạy toàn bộ test khi gộp (trong worktree, theo T-138).

**B. Cho việc sau** (không chặn):

1. **Phiếu sau (Thấp, Soi Lỗi G-1):** tab biết «đã gửi» thấy nháp có lại mà kho «chưa gửi» thì ghi lại kiểu so rồi đặt; Lá Chắn đầy đủ. Không cần trước khi bật công tắc.
2. **Kịch bản T-128:** dùng ca R bản cuối đã sửa bước 6 theo G-2 (file `T-136-la-chan-ca-R-ban-cuoi.md`, thư mục ghi chú chung); bước 7 ghi thêm «danh sách bài vẫn hiện cạnh lời nhắc».
3. **Phiếu chữ sau:** README «dời cả các file đó» khi có nhiều file (G-4); hai khung vàng cùng lúc (G-3) có thể gộp một.
4. **Lá Chắn T-136 lượt 2 B.4:** đã xong với T-137; Chỉ Huy cập nhật danh sách việc trước khi bật công tắc (còn buổi thử thật T-128 và quyết định chủ dự án).

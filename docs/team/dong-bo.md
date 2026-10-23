# Phiếu điều phối chung (2 Chỉ Huy)

Dự án có **hai Chỉ Huy** chạy ở **hai tài khoản Claude khác nhau**. Họ **không chạy cùng lúc**: Chỉ Huy kia chỉ làm khi Chỉ Huy này dừng, và một phiên thường chỉ dừng khi **hết lượt dùng**, tức là dừng bất ngờ, không kịp dặn lại. Hai bên chỉ liên lạc với nhau qua file này (chủ dự án chốt 2026-10-15).

Đọc file này **trước mọi việc khác**, ngay sau `git pull`.

## Hai Chỉ Huy

| Tên trong file này | Ở đâu |
|---|---|
| **Chỉ Huy A** | Claude Desktop (Code) trên máy chủ dự án, thư mục `D:\ProMetal-ToolSEO\ProMetal-ToolSEO` |
| **Chỉ Huy B** | Tài khoản Claude thứ hai của chủ dự án. Trước 2026-10-20: phiên "Điều phối" trên Claude Code cloud (claude.ai/code). **Từ 2026-10-20: Claude Desktop (Code) trên chính máy Windows của chủ dự án**, dùng chung repo `D:\ProMetal-ToolSEO\ProMetal-ToolSEO` và các worktree `D:\ProMetal-ToolSEO\wt-T-xxx` với A; agent là phiên con dưới phiên B |

Nếu bạn là Chỉ Huy mới và không chắc mình là A hay B, hỏi chủ dự án rồi ghi vào bảng trên.

## Quy tắc

1. **Đầu phiên:** `git pull`, đọc mục "Đang giữ quyền điều phối" và nhật ký bàn giao mới nhất. Rồi ghi tên mình vào mục "Đang giữ quyền", **commit và push ngay** trước khi làm việc khác.
   - Push bị từ chối nghĩa là bên kia vừa đẩy gì đó lên: `git pull`, đọc lại file này, rồi mới quyết định làm tiếp.
2. **Trong phiên, việc nhỏ, đẩy thường xuyên.** Phiên có thể dừng bất cứ lúc nào, nên sau **mỗi bước có ý nghĩa** (giao phiếu, nhận báo cáo, gộp nhánh, trả lời chủ dự án) thì cập nhật mục "Đang làm dở", rồi commit và push. Không bao giờ để việc nằm trên máy mà chưa đẩy lên.
3. **Không làm lại việc bên kia đang làm dở.** Đọc "Đang làm dở" của bên kia, đối chiếu `git log`, `git branch -r` và `docs/team/board.md` để biết họ dừng ở bước nào, rồi làm **tiếp** từ đó. Thấy chỗ nào không khớp thì ghi vào nhật ký, không tự đoán.
4. **Cuối phiên** (nếu kịp): viết một mục bàn giao ở đầu nhật ký. Đổi mục "Đang giữ quyền" thành "Không ai giữ". Commit và push.
5. **Bên kia dừng mà không bàn giao:** coi mục "Đang làm dở" của họ là trạng thái mới nhất. Ghi "Tiếp quản từ <A/B> lúc <giờ>, không có bàn giao" vào nhật ký.
6. **Quyết định của chủ dự án** mà một bên nhận được phải ghi ngay vào nhật ký **và** vào chỗ gốc (`CLAUDE.md`, `TIEN-DO.md`, `BAN-GIAO.md` mục 7), để bên kia không hỏi lại.
7. File này chỉ dùng để phối hợp hai Chỉ Huy. Việc của từng agent vẫn ghi ở `board.md`, phiếu và báo cáo như cũ.

Giờ ghi theo giờ Việt Nam (`Asia/Ho_Chi_Minh`), dạng `2026-10-15 11:00`.

## Đang giữ quyền điều phối

**Chỉ Huy B**, từ 2026-10-23 07:31 (chủ dự án bảo "tiếp tục"; không ai làm gì từ lúc B trả quyền 22/10 18:34, `origin/main` không đổi).

## Đang làm dở

_Bên đang giữ quyền cập nhật mục này sau mỗi bước._

Chỉ Huy B, cập nhật 2026-10-23 08:54. Agent chạy ở phiên con dưới phiên B, mỗi phiếu một worktree `D:\ProMetal-ToolSEO\wt-T-xxx`, đẩy lên nhánh `team/T-xxx`. Tối đa 3 phiên con cùng lúc. Các phiếu đã gộp ngày 20/10 (T-048, T-050, T-058, T-051, T-049, T-062, T-052, T-067, T-054, T-068) xem ở `board.md` mục Xong.

| Phiếu | Nhánh | Đang ở bước | Việc tiếp theo |
|---|---|---|---|
| [T-070](tickets/T-070-don-loi-the-anh.md) Dọn lỗi thẻ ảnh (GĐ3) | đã gộp (`588c76f`), nhánh và worktree đã xóa | ✅ Windows 9.740 qua, 0 hỏng; ruff sạch; đã đẩy `main` | Điều kiện đã chép vào T-056, T-069; dọn tiếp ở T-074 |
| [T-055](tickets/T-055-nhap-luu-lua-chon-anh.md) Nháp nhớ ảnh đã chọn | đã gộp (`64fd0c8`), nhánh và worktree đã xóa | ✅ Windows 10.441 qua, 0 hỏng; đã đẩy `main` | Điều kiện đã chép vào T-056, T-063; T-076 hết chờ |
| [T-061](tickets/T-061-shortcode-trong-bai-ai.md) Chặn shortcode WordPress | đã gộp (`975d323`), nhánh và worktree đã xóa | ✅ Windows 9.915 qua, 0 hỏng; đã đẩy `main` | Điều kiện đã chép vào T-056, T-059, T-060 |
| [T-074](tickets/T-074-don-the-anh-luot-2.md) Dọn thẻ ảnh lượt 2 | đã gộp (`ae2ae8e`), nhánh và worktree đã xóa | ✅ Windows 10.135 qua, 0 hỏng; đã đẩy `main` | Điều kiện đã chép vào T-056, T-069; dọn tiếp ở T-077 |
| [T-075](tickets/T-075-nang-certifi.md) Nâng `certifi` | đã gộp (`0d398c2`), nhánh và worktree đã xóa | ✅ Windows 10.441 qua, 0 hỏng; đã đẩy `main` | 2 máy mở lại app để `uv sync` cài `certifi` mới (máy Windows: `main` đã sync) |
| [T-077](tickets/T-077-don-the-anh-ten-cong-cu-ai.md) Dọn thẻ ảnh nhỏ | đã gộp (`c2233ed`), nhánh và worktree đã xóa | ✅ Windows 10.585 qua, 0 hỏng; đã đẩy `main` | |
| [T-076](tickets/T-076-thu-muc-anh-tra-ten-tren-o.md) Thư mục ảnh trả tên trên ổ | đã gộp (`4ca5a2d`), nhánh và worktree đã xóa | ✅ Windows 10.739 qua, 0 hỏng; đã đẩy `main` | LC-T076-3 → T-079 |
| [T-039](tickets/T-039-lien-ket-noi-bo.md) Liên kết nội bộ (GĐ4) | đã gộp (`089f685`), nhánh và worktree đã xóa | ✅ Windows 11.234 qua, 0 hỏng; đã đẩy `main` | Điều kiện → T-040, T-041, GĐ5 |
| [T-079](tickets/T-079-doc-anh-bang-fd-tung-tang.md) Đọc ảnh bằng fd từng tầng | đã gộp (`638a895`), nhánh `team/T-079`, `team/T-079-linux` và worktree đã xóa | ✅ Windows 11.265 qua, 3 hỏng oan (chạy riêng lại qua); đã đẩy `main` | 3 Thấp → T-080 (đang làm) |
| [T-066](tickets/T-066-don-loi-thap-anh-gui-ai.md) Dọn lớp ảnh gửi AI (trước T-056) | `team/T-066` (`66f58dd`) | ✅ 23/10 Thợ Máy xong | ⏳ Soi Lỗi rút gọn (phiên "Soi Lỗi · T-066 kiểm nhanh ảnh gửi AI") |
| [T-071](tickets/T-071-don-loi-thap-chen-anh-nhap.md) Dọn chèn ảnh nháp (trước T-056) | `team/T-071` (`6046a8f`) | ✅ 23/10 Thợ Máy xong (cách A) | ⏳ Soi Lỗi rút gọn, soát R5 7 chỗ test (phiên "Soi Lỗi · T-071 kiểm nhanh chèn ảnh nháp") |
| [T-080](tickets/T-080-don-loi-thap-doc-anh-sau-t079.md) Dọn lỗi Thấp đọc ảnh (GĐ3) | `team/T-080` (từ `main` sau gộp T-079) | Chủ dự án chọn sửa | ⏳ Thợ Máy (phiên "Thợ Máy · T-080 dọn đọc ảnh") |
| [T-069](tickets/T-069-readme-anh-gui-ai.md) README phần ảnh | đã gộp (`5d17f5e`), nhánh và worktree đã xóa | ✅ Windows 11.234 qua, 0 hỏng; đã đẩy `main` | LC-T069-1, -2 sửa chữ README sau |
| [T-065](tickets/T-065-quy-tac-alt-chu-trong-anh.md) Quy tắc alt | đã gộp (`5b82d70`), nhánh và worktree đã xóa | ✅ Windows 10.602 qua, 0 hỏng; đã đẩy `main` | |
| [T-063](tickets/T-063-chay-test-t048-tren-mac-linux.md) Test Linux (cloud) | đã gộp (`103b6ee`), nhánh và worktree đã xóa | ✅ Windows 10.739 qua, 0 hỏng; đã đẩy `main` | SL-T063-2 → T-079; phần Mac chờ máy Mac |
| Chờ phiếu trước | | **T-078** (`uv`: máy Windows đã lên 0.13.4, chờ máy Mac; `required-version`, README chưa giao); T-040, T-041 (GĐ4, hết chờ sau T-039); T-060 (dọn client WordPress, trước T-041); T-059 chờ chủ dự án bật Abilities, tạo tài khoản Biên tập viên, cập nhật Code Snippets | Số phiếu tiếp theo: **T-081** |

## Nhật ký bàn giao

_Mục mới nhất ở trên cùng._

### 2026-10-23 08:54 · Chỉ Huy B

- **Toàn bộ test Windows sau gộp T-079:** 11.265 qua, 50 bỏ qua, 107 xfail, 3 hỏng: `tests/test_link_escape.py::test_timing_helper_has_absolute_limit`, `tests/test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted`, `tests/test_soi_loi_t045.py::test_more_bad_inputs_linear[emoji-zwj-half-heading]` (đều đo tốc độ/khóa chờ, máy chạy 3 agent); chạy riêng lại 3 lần: 12/12 qua cả 3 lần; không liên quan `folders.py`. Ruff sạch. Đã đẩy `main`, xóa nhánh `team/T-079`, `team/T-079-linux` và worktree. Ghi nhận: T-073 (ổn định test khóa chờ) nên làm sớm.

### 2026-10-23 08:17 · Chỉ Huy B

- **Quyết định chủ dự án** ("có" cho 4 đề xuất): gộp T-079; **sửa** LC-T079-1..3 ở T-080 (không ghi sổ); **ghi sổ rủi ro** ca "thư mục thật được dời vào gốc" (đã thêm `docs/team/security.md` mục 6, người quyết định An Manu); giao Soi Lỗi rút gọn T-066, T-071.
- Gộp T-079 vào `main` (`638a895`), không xung đột; đang chạy toàn bộ test Windows. Nhánh `team/T-080` tạo từ `main` sau commit này.

### 2026-10-23 08:03 · Chỉ Huy B

- **Toàn bộ test Windows sau gộp T-039 + T-069 (chạy lại):** 11.234 qua, 31 bỏ qua, 97 xfail, **0 hỏng** (32 phút, chạy cùng 3 agent); ruff sạch. Lượt 22/10 bị dừng có 1 hỏng là hỏng oan do máy bận. Đã đẩy `main` (gồm cả bàn giao 22/10), xóa nhánh `team/T-039`, `team/T-069` (máy và GitHub) và worktree.

### 2026-10-23 07:57 · Chỉ Huy B

- **Lá Chắn T-079 ĐẠT CÓ ĐIỀU KIỆN** (`f915841`, gộp luôn phần "VIỆC DỞ"): SL-T063-2, -3 đóng; 3 Thấp LC-T079-1, -2, -3 → lập **T-080** (hoặc sổ rủi ro); gộp được ngay. Phiên báo "chờ người dùng": hỏi chủ dự án ghi sổ rủi ro ca "thư mục thật được dời vào gốc" (điều kiện 3) và chọn sửa/ghi sổ cho LC-T079-1..3.
- **Thợ Máy T-066 xong** (`66f58dd`), **Thợ Máy T-071 xong** (`6046a8f`, cách A; diff gồm đúng 7 chỗ test ngoài phạm vi đã duyệt). Chờ Soi Lỗi rút gọn.
- Toàn bộ test `main` (gộp T-039, T-069) đang chạy. Số phiếu tiếp theo: **T-081**.

### 2026-10-23 07:31 · Chỉ Huy B

- Chủ dự án bảo "tiếp tục": B nhận lại quyền. Đối chiếu: `origin/main` không đổi từ 22/10; `main` trên máy đi trước 20 commit (gộp T-039, T-069 chưa qua toàn bộ test). `wt-T-071` có thêm sửa chưa commit ở `tests/test_shortcode_t061.py`, `tests/test_soi_loi_t054.py` (phiên T-071 kịp chạy lại một lượt ngắn vì tin nhắn xếp hàng trước khi bị dừng lần 2: đúng các sửa cơ học cách A); để nguyên cho Thợ Máy làm tiếp.
- Việc: chạy lại toàn bộ test trên `main` (in tên test hỏng); nhắn 3 phiên con làm tiếp (Lá Chắn T-079, Thợ Máy T-066, Thợ Máy T-071).

### 2026-10-22 18:34 · Chỉ Huy B · BÀN GIAO

- **Chủ dự án bảo dừng các việc đang làm.** Đã dừng 3 phiên con (Lá Chắn T-079, Thợ Máy T-066, Thợ Máy T-071; phiên T-071 tự chạy lại vì tin nhắn xếp hàng nên dừng lần 2) và lượt toàn bộ test. Việc dở đã commit "VIỆC DỞ" và đẩy lên `team/T-079` (`6e84375`), `team/T-066` (`9b41e6a`), `team/T-071` (`9c0f8b8`).
- **`main` trên máy đi trước GitHub**: có 2 lần gộp **chưa qua toàn bộ test**: T-039 (`089f685`), T-069 (`5d17f5e`), cùng các commit tài liệu sau đó (gồm bàn giao này). Lượt toàn bộ test (18:07) bị dừng ở khoảng 70% và **đã có 1 test hỏng chưa rõ tên** (có thể do máy đang chạy 3 agent). Không đẩy `main` để giữ quy tắc "`main` chỉ chứa code đã kiểm". **Phiên sau (A hay B, cùng máy này): chạy lại `uv run pytest` trên `main` ở `D:\ProMetal-ToolSEO\ProMetal-ToolSEO`; hỏng thì tìm nguyên nhân (chạy riêng lại); qua thì đẩy `main`, xóa nhánh và worktree T-039, T-069.**
- Cloud: 2 phiên Linux đã xong (T-063, T-079-linux), không còn chạy.
- App xem thử đang chạy ở `http://localhost:8501` (dịch vụ xem trước của phiên B); tắt khi đóng phiên.
- Việc kế tiếp: Lá Chắn T-079 → gộp T-079; T-066, T-071 làm tiếp → Soi Lỗi rút gọn → Lá Chắn rút gọn; rồi T-056 (Họa Sĩ, màn hình chọn ảnh). GĐ4: T-040 (Ngòi Bút), T-060, T-041. Chờ chủ dự án: việc website ở `TIEN-DO.md` mục 4. Số phiếu tiếp theo: **T-080**.

### 2026-10-22 18:16 · Chỉ Huy B

- Thợ Máy T-071 hỏi phạm vi (yêu cầu 5 làm hỏng 7 chỗ test ngoài phạm vi). Chỉ Huy chọn **A** (bỏ `ai_generated`, ảnh AI theo `tags.source`; sửa cơ học 7 chỗ test, không đổi điều kiện kiểm; Soi Lỗi soát theo R5). Đã ghi vào phiếu T-071.

### 2026-10-22 18:07 · Chỉ Huy B

- **Lá Chắn T-039 ĐẠT CÓ ĐIỀU KIỆN** (`7f9fd80`, 2 Thấp; điều kiện → T-040, T-041, GĐ5). **Lá Chắn T-069 rút gọn ĐẠT CÓ ĐIỀU KIỆN** (`5104e17`, 2 Thấp chữ README). **Soi Lỗi T-079 Windows ĐẠT CÓ ĐIỀU KIỆN** (`79b55e7`, SL-T079-1 Thấp). **Phiên cloud Linux T-079 ĐẠT** (`e7fdebd` trên `team/T-079-linux`: 0 lọt qua hơn 1,3 triệu lượt đọc khi bị tráo).
- Chủ dự án ("Tiếp tục"): gộp T-039 (`089f685`) và T-069 (`5d17f5e`) vào `main`, không xung đột; đang chạy toàn bộ test Windows. Gộp `team/T-079-linux` vào `team/T-079` (`089d115`). Giao Lá Chắn T-079 (F1), Thợ Máy T-066, Thợ Máy T-071 (file không trùng nhau). Điều kiện Lá Chắn T-039 chép vào T-040, T-041; LC-T069-2 chép vào T-056.

### 2026-10-22 13:51 · Chỉ Huy B

- Chủ dự án ("làm tiếp"): giao Lá Chắn đầy đủ T-039, Soi Lỗi T-079 (Windows), Lá Chắn rút gọn T-069, và một **phiên cloud Linux** chạy lại test + cách tráo của T-063 trên nhánh T-079 (task `task_8fde0958`; push lên `team/T-079-linux` để khỏi đụng `team/T-079`).

### 2026-10-22 13:47 · Chỉ Huy B

- **Thư Ký T-069 xong** (`b8489fa`, diff chỉ `README.md` + báo cáo). Chờ Lá Chắn rút gọn.
- **Soi Lỗi T-039 lượt 3 ĐẠT** (`49ed923`, 0 lỗi; SL-T039-1 → -9 đóng). Chờ Lá Chắn đầy đủ.
- **Thợ Máy T-079 xong** (`c7b2394`, diff trong phạm vi: `folders.py`, `drafts.py` phần LC-T076-3, test; các file `xfail` chỉ gỡ dấu): vá SL-T063-2, -3 cho Mac/Linux (fd từng tầng) và Windows (hỏi lại vị trí của chính file đã mở); SL-T063-1, -4, -5, LC-T076-3. Phần Mac/Linux mới chạy giả lập trên Windows → đề xuất Soi Lỗi trên Windows + phiên cloud Linux. Không còn phiên con nào chạy.

### 2026-10-22 13:30 · Chỉ Huy B

- **Toàn bộ test Windows sau gộp T-076 + T-063:** 10.739 qua, 31 bỏ qua (thêm các test chỉ chạy trên Linux/Mac của T-063), 94 xfail, **0 hỏng** (20 phút); ruff sạch. Đã đẩy `main`, xóa nhánh `team/T-076`, `team/T-063` (máy và GitHub) và worktree `wt-T-076`, `wt-T-063`. Bảng %: Giai đoạn 3 lên khoảng 90%.
- 13:12 mở app cho chủ dự án xem (`http://localhost:8501`, chạy từ `main` trên máy). Rà câu hỏi của agent: 3 phiên từng chờ (Thợ Máy T-076, Soi Lỗi T-076, Lá Chắn T-063) đều đã có quyết định; nhắc chủ dự án các việc website ở `TIEN-DO.md` mục 4.

### 2026-10-22 13:10 · Chỉ Huy B

- **Quyết định chủ dự án** ("Làm tiếp theo đề xuất của bạn"): gộp T-076 và T-063; **cách A** (T-079 trước T-056); giao Soi Lỗi rút gọn T-039 lượt 3, Thợ Máy T-079, Thư Ký T-069. Đã ghi vào T-056, T-079.
- Gộp T-076 (`4ca5a2d`) rồi T-063 (`103b6ee`) vào `main`, không xung đột; đang chạy toàn bộ test Windows. Nhánh `team/T-079`, `team/T-069` tạo từ `main` sau commit này.

### 2026-10-22 10:28 · Chỉ Huy B

- Chủ dự án nhờ cập nhật tiến độ: đã sửa file Drive "Bảng tiến độ SEO App, 22/10/2026" (Giai đoạn 3 khoảng 85%, Giai đoạn 4 khoảng 45%, cả dự án khoảng 60%; ghi lỗ hổng đọc ảnh T-063/T-079; bỏ lời dặn Wi-Fi công cộng trên Windows). Vẫn chờ chủ dự án quyết: gộp T-076, T-063; thứ tự T-079/T-056 (A/B); giao Soi Lỗi T-039, Thợ Máy T-079, Thư Ký T-069.

### 2026-10-22 10:16 · Chỉ Huy B

- **Lá Chắn T-076 lượt 2 ĐẠT CÓ ĐIỀU KIỆN** (`3dbf956`): LC-T076-1 đóng (đo trên ổ Google Drive for Desktop thật, chỉ in Đúng/Sai), LC-T076-2 đóng; LC-T076-3 Thấp → T-079; điều kiện 2a của T-056 hạ xuống khuyến nghị, giữ test. Gộp được ngay.
- **Thợ Máy T-039 lượt 3 xong** (`34e143a`): SL-T039-7 → -9. Chờ Soi Lỗi rút gọn.
- **Lá Chắn T-063 ĐẠT CÓ ĐIỀU KIỆN** (`b7a44cc`): SL-T063-2 Cao (Mac/Linux) / Thấp (Windows: thử tráo thật >15.000 lần đọc, 0 lọt; ép thắng thì lọt nên lỗi nằm trong code). T-079 bắt buộc trước khi app chạy trên Mac/Linux (kể cả cloud Linux). Hỏi chủ dự án thứ tự: A (T-079 trước T-056) hay B (T-056 trên Windows trước, ghi sổ rủi ro). Mẫu dòng sổ rủi ro trong biên bản có ghi tên người ký không rõ nguồn: không dùng, nếu chọn B thì ghi theo lời chủ dự án.
- Đã chép điều kiện vào T-056, T-079 (thêm LC-T076-3, xóa `xfail` SL-T063-4), T-063, T-076, T-039. Không còn phiên con nào chạy.

### 2026-10-22 10:08 · Chỉ Huy B

- **Toàn bộ test Windows sau gộp T-065:** 10.602 qua, 20 bỏ qua, 93 xfail, **0 hỏng** (23 phút, chạy cùng 3 agent); ruff sạch. Đã đẩy `main`, xóa nhánh `team/T-065` (máy và GitHub) và worktree `wt-T-065`.

### 2026-10-22 09:46 · Chỉ Huy B

- Chủ dự án ("Có"): gộp T-065; Lá Chắn rút gọn T-076 lượt 2; Thợ Máy T-039 lượt 3; Lá Chắn xét SL-T063-2 và thử tráo nhanh trên Windows. Gộp T-065 vào `main` (`5b82d70`), không xung đột; đang chạy toàn bộ test Windows. Tạo worktree `wt-T-063` (nhánh `team/T-063`) cho Lá Chắn.

### 2026-10-22 09:44 · Chỉ Huy B

- **Lá Chắn T-065 rút gọn ĐẠT** (`4887a28`, 0 lỗi). Chờ chủ dự án cho gộp.
- **Soi Lỗi T-076 lượt 2 ĐẠT CÓ ĐIỀU KIỆN** (`7dcb553`): LC-T076-1 đóng (cả ổ giả kiểu Google Drive); SL-T076-1 hết; SL-T076-2 Thấp mới (đổi tên rồi đổi lại đúng lúc kiểm). Phiên báo "chờ người dùng" (đề xuất cách (a) đóng hẳn SL-T076-2 nhưng phải sửa 3 test cũ): không giao thêm, đưa SL-T076-2 vào T-079.
- **Soi Lỗi T-039 lượt 2 ĐẠT CÓ ĐIỀU KIỆN** (`96fb3df`): 6/6 lỗi cũ sửa thật; SL-T039-7 (tốc độ, do lượt 2) nên sửa trước khi gộp; SL-T039-8, -9 Thấp.
- **Phiên cloud T-063 xong** (`team/T-063` `71c5d99`, Ubuntu 24.04, Python 3.12.3): nhánh quét thư mục Linux đạt; **KHÔNG ĐẠT** vì **SL-T063-2 (đề xuất Cao)**: tráo thư mục con thành symlink đúng lúc đọc thì `read_image_bytes` trả nội dung file ngoài gốc (cả `main` lẫn `team/T-076`). Lập **T-079** (đọc bằng fd từng tầng; chờ T-076 gộp và Lá Chắn xét mức). Số phiếu tiếp theo: **T-080**.

### 2026-10-22 09:08 · Chỉ Huy B

- Chủ dự án ("Có"): giao Soi Lỗi rút gọn T-076 lượt 2 (nhắn lại phiên Soi Lỗi T-076) và **chạy T-063 trên cloud Linux**. Lần đầu yêu cầu cloud bị từ chối (thư mục dự án `D:\ProMetal-ToolSEO` không phải kho Git); yêu cầu lại với kho `trinytrinhlam-web/ProMetal-ToolSEO` (task `task_1ff4c87a`). Phiên cloud không gửi tin về: đọc kết quả ở nhánh `team/T-063` (`docs/team/reports/T-063-soi-loi.md`).

### 2026-10-22 09:01 · Chỉ Huy B

- **Quyết định chủ dự án:** Chủ dự án báo 2026-10-22: **hiện chưa có máy Mac**. Bỏ bước nâng `uv` trên Mac (T-078). Lời dặn «không dùng Wi-Fi công cộng» bỏ được trên máy Windows (đã có `certifi` 2026.10.19 trong `.venv` của `main`, `uv` 0.13.4). T-063 (test Mac/Linux) chỉ chạy được bằng phiên cloud Linux; máy này không có WSL. Đã ghi `TIEN-DO.md` mục 4, phiếu T-063, T-078.
- **Thợ Máy T-076 lượt 2 xong** (`006b13b`): LC-T076-1 (Windows lấy tên từ thư mục cha bằng `FindFirstFileW`), LC-T076-2 bằng cách hỏi lại tên cũ thay cho cách (a) đúng chữ (để khỏi đổi test Soi Lỗi T-055); Chỉ Huy chấp nhận, Soi Lỗi/Lá Chắn xét lại. Chờ chủ dự án cho giao Soi Lỗi rút gọn.
- **Ngòi Bút T-065 lượt 2 xong** (`95d1fb7`). Chủ dự án ("thử luôn đi") cho giao: Soi Lỗi kiểm lại T-039 lượt 2, Lá Chắn rút gọn T-065 (đã duyệt từ trước).

### 2026-10-22 08:21 · Chỉ Huy B

- **Thợ Máy T-039 lượt 2 xong** (`c0e5806`, đã đối chiếu diff: chỉ `links.py`, test, báo cáo; `tests/test_soi_loi_t039.py` chỉ gỡ dấu `xfail`): sửa SL-T039-6 (đổi tên bộ đệm, chạy đúng trên mọi bản 3.12) và SL-T039-1 → -5. Chờ chủ dự án cho giao Soi Lỗi kiểm lại.
- Chủ dự án nhờ cập nhật tiến độ: sửa file Drive "Bảng tiến độ SEO App" (đổi ngày trong tên sang 22/10).

### 2026-10-22 08:20 · Chỉ Huy B

- Chủ dự án ("có"): Thợ Máy T-076 lượt 2 (LC-T076-1, -2) và Ngòi Bút T-065 lượt 2 (SL-T065-1), sau đó Lá Chắn rút gọn T-065. Giao bằng cách nhắn lại đúng phiên con đã làm phiếu (giữ ngữ cảnh). Đang chạy: Thợ Máy T-039 lượt 2, Thợ Máy T-076 lượt 2, Ngòi Bút T-065 lượt 2.

### 2026-10-22 07:51 · Chỉ Huy B

- Chiều 21/10 tài khoản chạm giới hạn sử dụng: Thợ Máy T-039 lượt 2 dừng giữa chừng (việc dở chưa commit trong `wt-T-039`). Sáng 22/10 cuộc trò chuyện Chỉ Huy B chạy tiếp bằng **tài khoản Claude khác** (`support@tomaz.vn`); chủ dự án bảo "thử lại": đã nhắn T-039 làm tiếp.
- **Lá Chắn T-076 rút gọn ĐẠT CÓ ĐIỀU KIỆN** (`ca1e91d`): F1, F3 đạt; **LC-T076-1 Trung bình** (Google Drive for Desktop trên Windows: `resolve` trả chữ đã gõ, LC-T055-1 chưa đóng trên ổ này) → T-076 lượt 2 trước khi gộp; LC-T076-2 Thấp (= SL-T076-1). Điều kiện 2a của T-056 giữ bắt buộc; chép điều kiện vào T-056, T-063, T-076.
- **Soi Lỗi T-065 rút gọn ĐẠT CÓ ĐIỀU KIỆN** (`8f41ba0`): SL-T065-1 Thấp (ví dụ «alt xấu» dùng tên đường thật «Cộng Hòa»); đề xuất Ngòi Bút thay tên bịa rồi Lá Chắn rút gọn.

### 2026-10-21 16:18 · Chỉ Huy B

- Chủ dự án ("làm tiếp đi"): giao Lá Chắn rút gọn T-076, Thợ Máy T-039 lượt 2 (SL-T039-6 bắt buộc, SL-T039-1 → -5 nếu gọn), Soi Lỗi rút gọn T-065.

### 2026-10-21 16:04 · Chỉ Huy B

- **Soi Lỗi T-076 ĐẠT CÓ ĐIỀU KIỆN** (`a1a48da`): 4 yêu cầu làm đúng, lớp chặn T-048 giữ; 1 Thấp SL-T076-1 (tráo sang thư mục có bản sao cùng cỡ, cùng giờ sửa đúng lúc kiểm). Chờ Lá Chắn rút gọn.
- **Soi Lỗi T-039 ĐẠT CÓ ĐIỀU KIỆN** (`5b4ec03`): 24 cách chèn link ngoài không lọt; **SL-T039-6 Trung bình** (`_TextRuns._pending` trùng tên bộ đệm `HTMLParser` của Python 3.12.15: `apply_links` ném `IndexError` hoặc bỏ oan đoạn cuối; chỉ trên máy có Python mới) → cần Thợ Máy lượt 2 trước khi gộp; 5 Thấp SL-T039-1 → -5 (đề xuất dọn cùng T-041 hoặc trước GĐ5).
- **Ngòi Bút T-065** gửi thông báo xong (test liên quan 2.401 qua, 1 hỏng oan vì quá giờ, chạy riêng lại qua). Chờ Soi Lỗi rút gọn. Không còn phiên con nào chạy.

### 2026-10-21 15:46 · Chỉ Huy B

- **Toàn bộ test Windows sau gộp T-077:** 10.585 qua, 20 bỏ qua, 93 xfail, **0 hỏng** (31 phút, chạy cùng 3 agent); ruff sạch. Đã đẩy `main`, xóa nhánh `team/T-077` (máy và GitHub) và worktree `wt-T-077`.
- **Ngòi Bút T-065 xong** (`bded957`, đã đối chiếu: chỉ `config/content.toml` mục `[alt]`, 13 thêm 6 bỏ, vẫn 16 quy tắc 6 ví dụ). Phiên kết thúc 15:16 không gửi thông báo. Chờ chủ dự án cho giao Soi Lỗi rút gọn. Đang chạy: Soi Lỗi T-076, Soi Lỗi T-039.

### 2026-10-21 14:53 · Chỉ Huy B

- Chủ dự án ("có"): gộp T-077; giao Soi Lỗi T-076, Soi Lỗi T-039, Ngòi Bút T-065. Gộp T-077 vào `main` (`c2233ed`), không xung đột; đang chạy toàn bộ test Windows. Nhánh `team/T-065` tạo từ `main` sau commit này.

### 2026-10-21 14:46 · Chỉ Huy B

- **Lá Chắn T-077 rút gọn ĐẠT** (`9333508`, 0 lỗi): LC-T074-1 đóng, LC-T070-2 giữ. Gộp được ngay; chờ chủ dự án cho gộp.
- **Thợ Máy T-076 xong** (`3bb126e`, đã đối chiếu diff: chỉ file trong phạm vi): `list_folder`, `stat_image` trả `ImageRef` theo tên trên ổ; LC-T055-1, -2, -3 sửa; gỡ `xfail` SL-T055-4, -5. Chờ Soi Lỗi.
- **Thợ Máy T-039 xong** (`bf1f889`, diff: `links.py`, test mới, `prompts.py` chỉ thêm 35 dòng): chọn bài đích, kiểm gợi ý anchor AI, chèn link bằng code, kiểm link nháp/hỏng. Chờ Soi Lỗi.
- Không còn phiên con nào chạy.

### 2026-10-21 13:58 · Chỉ Huy B

- Chủ dự án ("có"): giao Lá Chắn rút gọn T-077, Thợ Máy T-076, Thợ Máy T-039 (hai Thợ Máy sửa file khác nhau: T-076 `folders.py`, `drafts.py`; T-039 `seo_app/onpage/links.py` mới, `prompts.py`). Nhánh `team/T-076`, `team/T-039` tạo từ `main` sau commit này. Đã cập nhật file Drive "Bảng tiến độ SEO App, 21/10/2026" lúc 13:57.

### 2026-10-21 13:56 · Chỉ Huy B

- **Toàn bộ test Windows sau gộp T-075 + T-055:** 10.441 qua, 20 bỏ qua, 132 xfail, **0 hỏng** (18 phút); ruff sạch; `uv sync` thay `certifi` 2026.7.22 → 2026.10.19. Đã đẩy `main`, xóa nhánh `team/T-055`, `team/T-075` (máy và GitHub) và worktree `wt-T-055`, `wt-T-075`. Bảng %: Giai đoạn 3 lên khoảng 85%.
- **Soi Lỗi T-077 rút gọn ĐẠT** (`0cbd4f3`, 0 lỗi). Chờ chủ dự án cho giao Lá Chắn rút gọn. Không còn phiên con nào chạy.

### 2026-10-21 13:39 · Chỉ Huy B

- **Quyết định chủ dự án** ("có"): gộp T-075 và T-055; duyệt nâng `uv` (T-078); giao Soi Lỗi rút gọn T-077. Đã ghi `TIEN-DO.md` mục 4.
- **Nâng `uv` máy Windows:** `uv self update` 0.12.23 → **0.13.4**. Máy Mac: chủ dự án tự chạy `uv self update`.
- Gộp T-075 (`0d398c2`) rồi T-055 (`64fd0c8`) vào `main`, không xung đột; `uv sync` cài `certifi` 2026.10.19; đang chạy toàn bộ test Windows. Giao Soi Lỗi rút gọn T-077.

### 2026-10-21 13:36 · Chỉ Huy B

- **Thợ Máy T-077 xong** (`36d6470`, đã đối chiếu diff: chỉ 4 file trong phạm vi + báo cáo): tên công cụ AI viết hoa giữa chữ hay tách đôi là ảnh AI; `get_many` đọc xong mới xử lý; gỡ `xfail` SL-T074-1, -2, LC-T074-1. Chờ chủ dự án cho giao Soi Lỗi rút gọn. Không còn phiên con nào chạy.

### 2026-10-21 13:33 · Chỉ Huy B

- Khoảng 12:30 tài khoản chạm giới hạn sử dụng; Thợ Máy T-077 dừng giữa chừng (code `c8c6351` đã đẩy; `tests/test_images_tags.py` và báo cáo chưa commit). Chủ dự án báo đã đặt lại: nhắn T-077 làm tiếp. Chế độ nhanh không bật được cho phiên này ("extra usage" đang tắt), chạy mức Tối đa thường.
- **Soi Lỗi T-055 lượt 3 xong** (`b137643`): đổi dữ liệu `tests/test_soi_loi_t055.py` sang `CongAI`/`congai`, thêm `assert` điều kiện đầu; đột biến bắt lại đủ; 9 file liên quan 0 hỏng. Sẵn sàng gộp, chờ chủ dự án cho gộp.
- **Lá Chắn T-075 rút gọn ĐẠT** (`6c0652c`): 0 lỗi; LC-T061-1 đóng; gộp được ngay. Phát hiện ngoài phiếu **LC-T075-1 (Cao)**: công cụ `uv` 0.12.23 trên máy này mang gốc emSign G3 trong bộ chứng chỉ riêng (GHSA-hq85-5cpj-mr62, vá ở 0.13.4); mở app không bị (kiểm mã băm), `uvx`/`uv lock --upgrade-package` thì bị. Lập **T-078** (nâng `uv` 2 máy, `required-version`, README), chờ chủ dự án duyệt nâng công cụ.
- Số phiếu tiếp theo: **T-079**.

### 2026-10-21 12:20 · Chỉ Huy B

- **Toàn bộ test Windows sau gộp T-074:** 10.135 qua, 19 bỏ qua, 128 xfail, **0 hỏng** (17 phút, chạy cùng 3 agent); ruff sạch. Đã đẩy `main`, xóa nhánh `team/T-074` (máy và GitHub) và worktree `wt-T-074`. Bảng %: Giai đoạn 3 lên khoảng 80%.

### 2026-10-21 12:03 · Chỉ Huy B

- Chủ dự án ("có"): gộp T-074; giao Lá Chắn rút gọn T-075, Soi Lỗi sửa dữ liệu test T-055 (`tests/test_soi_loi_t055.py`), Thợ Máy T-077. Gộp T-074 vào `main` (`ae2ae8e`), không xung đột; đang chạy toàn bộ test Windows. Nhánh `team/T-077` tạo từ `main` sau gộp.

### 2026-10-21 12:01 · Chỉ Huy B

- **Thợ Máy T-055 lượt 3 xong** (`3e2c1fa`): `tests/test_drafts_images.py` đổi sang cặp `CongAI`/`congai`, thêm `assert` điều kiện đầu; còn 1 test hỏng trong `tests/test_soi_loi_t055.py` chờ Soi Lỗi.
- **Soi Lỗi T-075 rút gọn ĐẠT** (`f5f2bb6`, 0 lỗi). Chờ Lá Chắn rút gọn.
- **Lá Chắn T-074 rút gọn ĐẠT CÓ ĐIỀU KIỆN** (`b9918e1`): LC-T070-1, -2 đóng; 1 Thấp LC-T074-1 (có từ trước, gồm SL-T074-2 và kiểu tách đôi "Mid Journey") → lập **T-077** (Thợ Máy, trước T-056, kèm SL-T074-1); điều kiện (i), (j) vào T-056, điều kiện 3 vào T-069. Gộp được ngay, chờ chủ dự án cho gộp.
- Không còn phiên con nào chạy. Số phiếu tiếp theo: **T-078**.

### 2026-10-21 11:23 · Chỉ Huy B

- Chủ dự án cho giao 3 việc (mức Tối đa, chế độ nhanh): Soi Lỗi rút gọn T-075, Thợ Máy T-055 lượt 3 (sửa dữ liệu test LC-T055-4), Lá Chắn rút gọn T-074. Trước đó Chỉ Huy đưa `origin/main` vào `team/T-055` (`15a9726`, không xung đột, đã đẩy).

### 2026-10-21 11:16 · Chỉ Huy B

- **Soi Lỗi T-074 rút gọn ĐẠT CÓ ĐIỀU KIỆN** (`eec8fc7`, đã đối chiếu báo cáo): 6 yêu cầu làm đúng, thử lại các cách lách T-070 và kiểu khó hơn (WAL, 7 kiểu sửa mục lục): không lọt; tên ảnh máy ảnh, điện thoại, Zalo vẫn là ảnh thật. 2 Thấp: SL-T074-1 (giao dịch đọc giữ khóa khi đọc rất nhiều thẻ, lần lưu ở tab khác chờ, quá 5 giây báo bận), SL-T074-2 (tên thư mục công cụ AI viết hoa giữa chữ "MidJourney", "FireFly"… ra ảnh thật; có từ trước, Lá Chắn T-055 nêu). Chờ chủ dự án cho giao Lá Chắn rút gọn. Không còn phiên con nào chạy.

### 2026-10-21 11:02 · Chỉ Huy B

- **Thợ Máy T-075 xong** (`f6a8220`, đã đối chiếu diff): `certifi` 2026.7.22 → 2026.10.19, `uv.lock` chỉ đổi khối `certifi`; test chốt mới; `pip-audit` PyPI + OSV sạch; 927 test liên quan qua. Chờ chủ dự án cho giao Soi Lỗi rút gọn, Lá Chắn rút gọn.
- **Lá Chắn T-055 ĐẠT CÓ ĐIỀU KIỆN** (`91305e0`): an toàn F1/F3; 1 Trung bình LC-T055-1 (quét thư mục theo đường dẫn trong nháp làm SL-T055-1 quay lại) → điều kiện 2a–d vào T-056, sửa tận gốc ở **T-076** (lập mới); 3 Thấp: LC-T055-2, -3 → T-076; **LC-T055-4 phải sửa trước khi gộp**: trên bản gộp với `main` 2 test hỏng vì `genai` nay là ảnh AI (T-070), đổi sang cặp `CongAI`/`congai`. Điều kiện 4 chép vào T-063. Đề xuất ngoài phạm vi: `MidJourney` (J hoa) vẫn ra ảnh thật trên `main` → đã nhắn Soi Lỗi T-074 đang kiểm.
- Soi Lỗi T-074 vẫn đang chạy. Số phiếu tiếp theo: **T-077**.
- 11:03: chủ dự án kết nối lại Google Docs; đã cập nhật file Drive "Bảng tiến độ SEO App, 21/10/2026" (cùng link với bản 20/10, chỉ đổi ngày trong tên).

### 2026-10-21 10:58 · Chỉ Huy B

- Khoảng 10:10 ứng dụng dừng, phiên B và 3 phiên con bị ngắt (Lá Chắn T-055, Soi Lỗi T-074 chưa nộp gì; Thợ Máy T-075 còn `uv.lock` và test mới chưa commit). Chủ dự án bảo làm tiếp: 10:2x nhắn 3 phiên con làm tiếp, đặt lại mức Tối đa và chế độ nhanh.
- **Toàn bộ test Windows sau gộp T-061:** lượt 1 (10:06) Python sập "access violation" khi nạp `_sqlite3` lúc thu thập test (`tests/test_app_drafts.py`), trước khi chạy test nào; sau đó nạp lại bình thường, bản Python không đổi. Lượt 3 (10:22–10:58): **9.915 qua, 19 bỏ qua, 104 xfail, 0 hỏng**. Đã đẩy `main`, xóa nhánh `team/T-061` và worktree `wt-T-061`. Nếu lỗi sập này lặp lại thì ghi phiếu.
- Báo tiến độ: công cụ Google Docs bị "Permission denied" với 2 file tiến độ trong Drive "SEO-Tool" (có lẽ đăng nhập tài khoản Google khác); đã hỏi chủ dự án kết nối lại hay tạo file mới.

### 2026-10-21 10:05 · Chỉ Huy B

- **Quyết định chủ dự án** (trả lời "có" cho cả 4 đề xuất): (1) gộp T-061 vào `main`; (2) **duyệt nâng `certifi`** lên 2026.10.19 (T-075); (3) giao Lá Chắn T-055, Soi Lỗi rút gọn T-074, Thợ Máy T-075; (4) lưu trữ 3 phiên con đã xong. Đã ghi `TIEN-DO.md` mục 4.
- Gộp T-061 vào `main` (`975d323`), không xung đột; đang chạy toàn bộ test Windows. Nhánh `team/T-075` tạo từ `main` sau gộp.

### 2026-10-21 09:59 · Chỉ Huy B

- **Lá Chắn T-061 ĐẠT CÓ ĐIỀU KIỆN** (`b144b26`, Opus tạm): LC-T054-1 đóng, LC-T042-3 đóng phần app; 4 Thấp: LC-T061-2, -3, -5 → T-060; LC-T061-4 → T-056 (liệt kê shortcode trước «Gửi nháp»), T-059. Gộp `main` được ngay; chờ chủ dự án cho gộp.
- **LC-T061-1 (Cao, toàn repo, có từ trước):** `certifi` 2026.7.22 (GHSA-6q48-6c7w-9gw2, công bố 20/10). Đã kiểm `uv.lock` (2026.7.22) và bộ chứng chỉ trên máy còn «emSign ECC Root CA - G3». Lập **T-075** (Thợ Máy, nâng lên 2026.10.19), chờ chủ dự án duyệt nâng thư viện; báo chủ dự án tạm không dùng app trên Wi-Fi công cộng.
- **Thợ Máy T-074 xong** (`8ce0117`): đủ yêu cầu 1–6; 1.087 test liên quan qua. Chờ chủ dự án cho giao Soi Lỗi rút gọn.
- Không còn phiên con nào đang chạy. Số phiếu tiếp theo: **T-076**.

### 2026-10-21 09:38 · Chỉ Huy B

- **Soi Lỗi T-055 lượt 2 ĐẠT CÓ ĐIỀU KIỆN** (`1504d29`, đã đối chiếu báo cáo và diff): SL-T055-1 → -3 sửa thật; 3 test lượt 1 Thợ Máy đổi không bị làm yếu; 2 lỗi Thấp mới SL-T055-4 (tên thư mục "thật" có thể trỏ sang file khác: ổ phân biệt hoa thường có danh sách bị cắt, hoặc đổi tên đúng lúc mở nháp), SL-T055-5 (thư mục gốc hơn 5.000 mục thì ảnh thật "chưa kiểm được"). Chờ chủ dự án cho giao Lá Chắn. Đang chạy: Lá Chắn T-061, Thợ Máy T-074.

### 2026-10-21 09:34 · Chỉ Huy B

- **Toàn bộ test Windows trên `main` (gộp T-070):** 9.740 qua, 19 bỏ qua, 100 xfail, **0 hỏng** (27 phút, chạy cùng 3 agent); ruff sạch. Đã đẩy `main`, xóa nhánh `team/T-070` (máy và GitHub) và worktree `wt-T-070`.
- Đã giao 3 phiên con (09:12–09:14, mức Tối đa, chế độ nhanh; mở ở `D:\ProMetal-ToolSEO` rồi `cd` vào worktree): Soi Lỗi T-055 lượt 2, Lá Chắn T-061 (đầy đủ), Thợ Máy T-074 (nhánh `team/T-074` từ `main` `da87dbf`, đã đẩy).
- Bảng % trong `board.md`: Giai đoạn 3 lên khoảng 75%; cả dự án vẫn khoảng 60%.

### 2026-10-21 09:07 · Chỉ Huy B

- Phiên mới của B (chủ dự án xác nhận). Phiên trước dừng 20/10 khoảng 19:50 không kịp ghi: đã gộp T-070 vào `main` trên máy (`588c76f`, chưa đẩy), lập **T-074** (Lá Chắn T-070 điều kiện 1), chép điều kiện Lá Chắn T-070 vào T-056 (g, h) và T-069; Thợ Máy T-055 lượt 2 xong (`2c95844`), Soi Lỗi T-061 xong (`64525d3`). Đã đối chiếu `git log`, các worktree sạch.
- Chủ dự án cho làm: chạy toàn bộ test Windows cho bản gộp T-070, rồi giao 3 phiên con (mức Tối đa, chế độ nhanh): Soi Lỗi kiểm lại T-055, Lá Chắn T-061, Thợ Máy T-074.

### 2026-10-20 19:25 · Chỉ Huy B

- Chủ dự án cho giao (sau 19:08, đều mức Tối đa, chế độ nhanh): Soi Lỗi T-061 (xem kỹ 7 file test cũ Thợ Máy đã sửa điều kiện so đường), Lá Chắn rút gọn T-070, Thợ Máy T-055 lượt 2 (SL-T055-1, -2 Trung bình, SL-T055-3).

### 2026-10-20 19:08 · Chỉ Huy B

- **Soi Lỗi T-055 ĐẠT CÓ ĐIỀU KIỆN** (`934c21b`): 2 Trung bình (SL-T055-1, -2: ảnh AI có thể bị coi là ảnh thật khi mở lại nháp), 1 Thấp. Cần Thợ Máy lượt 2.
- **Soi Lỗi T-070 ĐẠT CÓ ĐIỀU KIỆN** (`95c0f70`): 5 Thấp. Chờ Lá Chắn rút gọn.
- **Thợ Máy T-061 xong** (`7c5a405`): vô hiệu shortcode ở mọi đường gửi lên WordPress; sửa điều kiện so đường (bỏ phần `?_fields=…`) ở 6 file test cũ của T-042, T-044, T-054: Soi Lỗi phải xem kỹ (R5). Chờ Soi Lỗi.
- Lượt này do thông báo của phiên con khởi động nên chưa giao vòng mới; chờ chủ dự án cho: Thợ Máy T-055 lượt 2, Lá Chắn rút gọn T-070, Soi Lỗi T-061.

### 2026-10-20 18:33 · Chỉ Huy B

- **Thử ảnh thật** (điều kiện 7 Lá Chắn T-049, điều kiện 1 Lá Chắn T-054): chủ dự án chỉ thư mục ảnh hiện có; B dùng `D:\Suachuacuasat\wp-content\uploads` (bản sao ảnh website, chỉ đọc; không mở `wp-config.php`). 99 ảnh gốc: 5 có EXIF, **0 có GPS** (ảnh thợ gửi qua Zalo đã bị nén). Thử `make_web_image` / `make_ai_image` trên 8 ảnh: đều ra WebP đúng cỡ, bản gửi AI sạch, không lỗi. Ghi nhận: ảnh rất nhẹ có khi ra WebP nặng hơn (31 → 37 KB). Không có HEIC để thử. Bản sao website không có plugin Code Snippets nên không biết phiên bản trên site thật.
- **Quyết định chủ dự án:** Chủ dự án chốt 2026-10-20: **rút gọn phần ảnh**: làm T-056 và các phiếu bắt buộc trước nó, ưu tiên T-061; **hoãn** T-053 (tạo ảnh AI), T-072 (GPS), lỗi nhỏ không chặn (T-064, T-057); **chuyển sớm** sang Giai đoạn 4 và 5. Đã ghi `CLAUDE.md` (Quyết định đã chốt), `BAN-GIAO.md` 7.5, `TIEN-DO.md` mục 4, `board.md` (đánh dấu Hoãn).
- **Gộp T-068 và T-054 vào `main`** (`43d6c4a`): Windows 9.477 qua, 1 hỏng `test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted` (lần 2 trong ngày; khi máy bận luồng giữ khóa tự nhả sau 10 giây). T-054, T-068 không đụng phần này. Đã đẩy, xóa 2 nhánh và worktree. Lập **T-073** (Soi Lỗi ổn định test này). T-071 hết chờ.
- Duyệt cho Thợ Máy T-055 sửa 1 dòng test ngoài phạm vi (`tests/test_soi_loi_t016_t020.py:744`: ví dụ "phiên bản lạ" 2 → 3).
- Giao (sau 17:59, mức Tối đa, chế độ nhanh): Thợ Máy T-061 (nhánh từ `main` `43d6c4a`), Soi Lỗi rút gọn T-070, Soi Lỗi T-055.
- Số phiếu tiếp theo: **T-074**.

### 2026-10-20 17:41 · Chỉ Huy B

- **Lá Chắn T-067 ĐẠT CÓ ĐIỀU KIỆN** (`44178a6`) → gộp vào `main` (`e5c0ce8`): Windows 8.974 qua, 1 hỏng `tests/test_link_escape.py::test_timing_helper_has_absolute_limit` (đo tốc độ, máy chạy 3 agent); chạy riêng lại 3 lần 119/119 qua. Đã đẩy, xóa nhánh và worktree. Lập **T-072** (LC-T067-1: Ref phụ sai khuôn không làm mất vị trí).
- **Lá Chắn T-054 ĐẠT CÓ ĐIỀU KIỆN** (`4aae291`): LC-T054-1 Trung bình (shortcode chạy ngay trong lệnh tạo nháp; với Code Snippets ≤ 3.9.1 có CVE-2025-13035) → chép vào **T-061**, hạn trước T-056; 5 Thấp → lập **T-071**; điều kiện chép vào T-056, T-059. **Việc của chủ dự án** (đã ghi `TIEN-DO.md` mục 4, mục 4b): cập nhật Code Snippets lên 3.9.2+, tắt «Enable file-based execution». T-054 chờ Chỉ Huy thử 3–5 ảnh thật rồi mới gộp.
- **Soi Lỗi T-068 ĐẠT CÓ ĐIỀU KIỆN** (`70087ee`): xác nhận test C6 Thợ Máy chỉnh; 3 Thấp SL-T068-1 → -3.
- Chủ dự án cho giao (sau 17:20, đều mức Tối đa, chế độ nhanh): Lá Chắn rút gọn T-068, Thợ Máy T-070 (nhánh từ `origin/main` `881548f`), Thợ Máy T-055 (cùng gốc).
- Số phiếu tiếp theo: **T-074**.

### 2026-10-20 17:05 · Chỉ Huy B

- Chủ dự án nhắn "làm tiếp đi", rồi cho giao 3 bước kiểm. Đã giao (đều mức Tối đa, chế độ nhanh): Soi Lỗi T-054, Soi Lỗi rút gọn T-067, Thợ Máy T-068 (nhánh `team/T-068` từ `main` `af7ac41`); sau đó Lá Chắn T-054, Lá Chắn rút gọn T-067, Soi Lỗi rút gọn T-068 (giao sau 16:51).
- Kết quả: Soi Lỗi T-054 ĐẠT CÓ ĐIỀU KIỆN (`1aee061`; SL-T054-2 Trung bình shortcode, trùng T-061); Soi Lỗi T-067 ĐẠT CÓ ĐIỀU KIỆN (`46f1bf7`; SL-T067-1 Thấp); Thợ Máy T-068 xong (`69b9f31`; chỉnh test C6 của Soi Lỗi vì mâu thuẫn SL-T062-1, B đã xem: hợp lý, vẫn giữ C6; Soi Lỗi xác nhận ở lượt kiểm).
- **Gộp T-052 vào `main`** (`1c7bd9a`): Windows 8.840 qua, 1 hỏng `tests/test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted` (khóa chờ, máy đang chạy 3 agent); chạy riêng lại 3 lần 139/139 qua; T-052 không đụng `site_index`. Đã đẩy, xóa nhánh và worktree. Hết chờ: T-055, T-070. **Ghi nhận:** test khóa chờ của T-037 dễ hỏng oan khi máy bận, nếu lặp lại thì lập phiếu cho Soi Lỗi.
- Bảng % trong `board.md`: Giai đoạn 3 lên khoảng 70%; cả dự án vẫn khoảng 60%.

### 2026-10-20 16:05 · Chỉ Huy B

- **Lá Chắn T-052 ĐẠT CÓ ĐIỀU KIỆN** (`7ef61fb`): 1 Trung bình (LC-T052-1: nhận ảnh AI theo tên còn thiếu các cách gọi như "minh họa", tên công cụ AI), 4 Thấp. Gộp được ngay. Chép điều kiện vào T-055, T-056, T-063, T-069; lập **T-070** (Thợ Máy, dọn thẻ ảnh, phải gộp trước T-056). **Chờ chủ dự án quyết LC-T052-5** (khe nhỏ khi SQLite tạo file journal: ghi sổ rủi ro hay đặt `journal_mode = MEMORY`).
- **Thợ Máy T-054 xong** (`3a909c0`): hàm gửi nháp kèm ảnh; không mở `class` trong `sanitize.py`; test liên quan 2.013 qua, 0 hỏng. Chờ Soi Lỗi.
- **Chủ dự án dặn:** báo cáo cho chủ dự án chỉ cần bảng công việc, phần trăm hoàn thành và việc đã xong, không cần kể việc điều phối, push. Đã thêm mục "Tiến độ dự án" (phần trăm theo giai đoạn) ở đầu `board.md`.
- Số phiếu tiếp theo: **T-074**. Không còn phiên con nào đang chạy.

### 2026-10-20 16:03 · Chỉ Huy B

- Chủ dự án cho giao 2 việc: **Lá Chắn T-052** và **Thợ Máy T-054** (nhánh `team/T-054` từ `main` `5441a68`, worktree `wt-T-054`, đã đẩy). Cả hai đã đặt mức Tối đa và chế độ nhanh. Soi Lỗi rút gọn T-067 chưa giao (chủ dự án chưa chọn).

### 2026-10-20 15:14 · Chỉ Huy B

- **Thợ Máy T-067 xong** (`da9d6c8`): sửa LC-T049-1 → -3, làm thêm N1, N4, gỡ 3 `xfail`; test liên quan 688 qua, 0 hỏng. Chờ Soi Lỗi rút gọn. Không còn phiên con nào đang chạy; chờ chủ dự án cho giao vòng mới.

### 2026-10-20 15:13 · Chỉ Huy B

- Chủ dự án cho gộp **T-062**: gộp vào `main` (`f96775a`), không xung đột; lần đầu chạy chung với T-049. Windows 8.487 qua, 0 hỏng; ruff sạch. Đã đẩy, xóa nhánh `team/T-062` và worktree `wt-T-062`. Hết chờ: T-053, T-068, T-069.
- **Soi Lỗi T-052 lượt 2 ĐẠT CÓ ĐIỀU KIỆN** (`497aa45`): 8 lỗi lượt 1 sửa thật; 3 lỗi mới Thấp SL-T052-9 → -11. Chờ Lá Chắn.
- Chủ dự án tạo thư mục Google Drive "SEO-Tool" và nhờ báo tiến độ: B tạo Google Docs "Tiến độ SEO App (Pro-Metal), cập nhật 20/10/2026" trong thư mục đó (tóm tắt giai đoạn, phiếu, việc chờ chủ dự án). Lần sau cập nhật tiến độ thì sửa đúng file này nếu có công cụ sửa Google Docs; không có thì tạo file mới ghi ngày.
- Đang chạy: Thợ Máy T-067.

### 2026-10-20 14:53 · Chỉ Huy B

- Chủ dự án cho giao **T-067** (Thợ Máy): nhánh `team/T-067` từ `main` `6ed41e2`, worktree `wt-T-067`, đã đẩy; đã đặt mức Tối đa và chế độ nhanh.
- **Lá Chắn T-062 rút gọn ĐẠT CÓ ĐIỀU KIỆN** (`0f01c1e`): C1–C6 đều đạt; 1 lỗi Thấp LC-T062-1 (quy tắc và ví dụ `[alt]` đi nguyên văn tới hãng AI, `config/` chưa ghi chú điều này) → thêm vào T-065. Chép điều kiện vào T-053, T-056; lập **T-068** (Thợ Máy, SL-T062-1 → -3) và **T-069** (Thư Ký, README: ảnh gửi hãng AI, cách đặt thư mục ảnh). Số phiếu tiếp theo: **T-074**. T-062 chờ chủ dự án cho gộp.

### 2026-10-20 14:37 · Chỉ Huy B

- Chủ dự án cho làm tiếp. Gọi 2 phiên con (giao sau 14:20, đã đặt mức Tối đa và chế độ nhanh): Soi Lỗi T-052 kiểm lại lượt 2, Lá Chắn rút gọn T-062.
- **Gộp T-049 vào `main`** (`3f90489`), không xung đột. Windows 8.278 qua, 0 hỏng; ruff sạch. Đã đẩy, xóa nhánh `team/T-049` và worktree `wt-T-049`.
- Hết chờ: T-066, T-067 (dọn lỗi Thấp), T-054 (chèn ảnh vào nháp; trước khi gộp cần T-067 sửa LC-T049-1 và Chỉ Huy thử ảnh thật). T-053 chỉ còn chờ T-062.

### 2026-10-20 14:20 · Chỉ Huy B

- **Lá Chắn T-049 ĐẠT CÓ ĐIỀU KIỆN** (`ca39d12`): 4 lỗi Thấp (LC-T049-1 → -3 = SL-T049-1 → -3; LC-T049-4: `detect-secrets` trên Windows bỏ qua lặng lẽ file có chữ tiếng Việt). Chép điều kiện vào T-053, T-054, T-056, T-062; sửa `docs/team/security.md` mục 5 (chạy với `PYTHONUTF8=1`); lập **T-067** (dọn LC-T049-1/-2/-3; LC-T049-1 chặn gộp T-054, -2/-3 chặn gộp T-056). Việc của Chỉ Huy: thử 3–5 ảnh thật trước khi gộp T-054. T-049 chờ chủ dự án cho gộp.
- **Thợ Máy T-052 lượt 2 xong** (`f771a0e`): sửa đủ SL-T052-1 → -8, đặt `trusted_schema = OFF`; test liên quan 849 qua, 0 hỏng. Chờ Soi Lỗi kiểm lại.
- **Soi Lỗi T-062 ĐẠT CÓ ĐIỀU KIỆN** (`1e953d4`): 3 lỗi Thấp SL-T062-1 → -3 (bước code tự sửa alt ảnh AI). Chờ Lá Chắn rút gọn.
- Số phiếu tiếp theo: **T-074**. Không còn phiên con nào đang chạy.

### 2026-10-20 13:52 · Chỉ Huy B

- Chủ dự án cho giao **Soi Lỗi T-062** vào chỗ trống; đã đặt mức Tối đa và chế độ nhanh. Đang chạy 3 phiên: Lá Chắn T-049, Thợ Máy T-052 lượt 2, Soi Lỗi T-062.

### 2026-10-20 13:50 · Chỉ Huy B

- Chủ dự án cho giao 2 việc: **Lá Chắn T-049** và **Thợ Máy T-052 lượt 2** (sửa SL-T052-1 và các lỗi Thấp cùng file). Đã đặt mức suy nghĩ Tối đa và chế độ nhanh cho cả hai phiên (mức Tối đa chỉ áp từ lượt sau của phiên; lượt đầu giữ mức lúc mở).
- Soi Lỗi T-062 chưa giao (chủ dự án chưa chọn).

### 2026-10-20 13:48 · Chỉ Huy B

- **Thợ Máy T-062 xong** (`ea1f900`): đạt 6 yêu cầu và điều kiện C1–C6 của Lá Chắn T-051; gỡ 5 `xfail` SL-T051-1 → 4; test liên quan 4.767 qua, 0 hỏng (toàn bộ để Chỉ Huy chạy khi gộp). Dòng README về khóa Gemini miễn phí (LC-T050-4) nằm ngoài phạm vi file, cần Thư Ký. Chờ Soi Lỗi. Không còn phiên con nào đang chạy.

### 2026-10-20 13:44 · Chỉ Huy B

- **Soi Lỗi T-049 ĐẠT CÓ ĐIỀU KIỆN** (`1f2f403`): 3 lỗi Thấp (SL-T049-1 chữ hướng GPS sai khuôn bị bỏ lặng lẽ; SL-T049-2 cache xem trước không kiểm Pillow ≥ 13; SL-T049-3 bộ lọc cảnh báo không an toàn nhiều luồng), giữ bằng `xfail`. Toàn bộ 8.278 qua, 0 hỏng. Chờ Lá Chắn.
- **Soi Lỗi T-052 ĐẠT CÓ ĐIỀU KIỆN** (`0848316`): 1 Trung bình SL-T052-1 (ảnh AI trong thư mục đặt tên khác danh sách bị coi là ảnh thật, mang thẻ công trình), 7 Thấp. Đề xuất Thợ Máy lượt 2. Test liên quan 753 qua.
- Thợ Máy T-062: code và báo cáo nháp đã đẩy (`400bde4`), đang chạy test liên quan.
- Chưa giao vòng mới: chờ chủ dự án cho làm tiếp.

### 2026-10-20 13:39 · Chỉ Huy B

- **Quyết định chủ dự án:** Chủ dự án chốt 2026-10-20: agent chỉ chạy **test liên quan tới phiếu** và `uv run ruff check .`; **Chỉ Huy chạy toàn bộ `uv run pytest` trên Windows một lần khi gộp vào `main`**. Đã sửa `docs/team/rules.md` (Trước khi nộp, định nghĩa Xong), `CLAUDE.md` (Cách làm việc), `docs/team/README.md`, `docs/team/security.md` mục 5, hồ sơ `soi-loi`, `tho-may`, `la-chan`, `hoa-si`, mẫu phiếu và báo cáo; ghi `BAN-GIAO.md` 7.3, `TIEN-DO.md` mục 4. Đã nhắn 3 phiên đang chạy (Soi Lỗi T-049, Soi Lỗi T-052, Thợ Máy T-062): được dừng lần chạy toàn bộ đang dở.

### 2026-10-20 13:36 · Chỉ Huy B

- **Quyết định chủ dự án:** Chủ dự án chốt 2026-10-20: agent phụ chạy **mức suy nghĩ Tối đa (max)** và **bật chế độ nhanh**; **không** chuyển sang ultracode. B đã đặt cho 3 phiên đang chạy (Soi Lỗi T-049, Soi Lỗi T-052, Thợ Máy T-062); từ nay đặt ngay sau khi mở mỗi phiên con. Đã ghi vào `BAN-GIAO.md` 7.3 và `docs/team/README.md` (mục Cách Chỉ Huy giao việc). Chỉ Huy A cũng làm theo.
- Lưu ý: phần chậm nhất của mỗi agent là chạy toàn bộ pytest (khoảng 13–23 phút khi 3 agent chạy cùng lúc trên một máy); hai cài đặt trên không rút được thời gian này.

### 2026-10-20 13:03 · Chỉ Huy B

- Chủ dự án cho giao cả vòng. Gộp `main` (`132a73d`, có T-050, T-051, T-058) vào `team/T-049` (`8e76b54`) và `team/T-052` (`2d481c0`), cả hai sạch, đã đẩy; test T-049 113 qua, test nối `alt.py` của T-052 qua.
- Gọi 3 phiên con (giao sau 12:48): Soi Lỗi T-049, Soi Lỗi T-052, Thợ Máy T-062 (nhánh `team/T-062` từ `main` `132a73d`, worktree `wt-T-062`, đã đẩy nhánh).

### 2026-10-20 12:48 · Chỉ Huy B

- **Thợ Máy T-049 xong** (`c2a597b`): `seo_app/images/process.py`, `naming.py`; 7.592 qua, 0 hỏng. Đã làm theo điều kiện bắt buộc của Lá Chắn T-050 (bản gửi AI không hồ sơ màu, qua `prepare_images`). Chưa thử ảnh thật.
- **Thợ Máy T-052 xong** (`0bbc0b8`): `seo_app/images/tags.py`, `seo_app/storage/image_tags.py`; 7.753 qua, 0 hỏng.
- Cả hai chờ Soi Lỗi rồi Lá Chắn. Chưa giao: chờ chủ dự án cho làm tiếp (cùng câu hỏi giao T-062). Không còn phiên con nào đang chạy.

### 2026-10-20 12:15 · Chỉ Huy B

- Chủ dự án cho gộp **T-050**: gộp vào `main` (`c1aa0ce`), không xung đột; `seo_app/images/__init__.py` giữ bản T-048 (blob `04c33dd`). Windows 8.009 qua, 0 hỏng; ruff sạch. Đã đẩy, xóa nhánh `team/T-050` và worktree `wt-T-050`.
- T-062 hết chờ (T-050, T-051 đã gộp). T-053 giờ chờ T-049, T-062.
- Đang chạy: Thợ Máy T-049, Thợ Máy T-052.

### 2026-10-20 11:53 · Chỉ Huy B

- **Lá Chắn T-050 ĐẠT CÓ ĐIỀU KIỆN** (`c5c57fc`): 4 lỗi Thấp (LC-T050-1/-2: bộ kiểm ảnh gửi AI chưa chặn hồ sơ màu và khối dựng cố ý; LC-T050-3: chú thích nói quá; LC-T050-4: khóa Gemini miễn phí cho Google dùng ảnh). Bản gộp `main` + T-050: 7.911 qua, 0 hỏng. Chép điều kiện vào T-049 (bắt buộc: bản gửi AI không kèm hồ sơ màu, không dùng `ImageCms`; đã nhắn phiên Thợ Máy T-049 để sửa gợi ý "đổi về sRGB" trong lời giao), T-052, T-054, T-056, T-062; lập **T-066** (dọn LC-T050-1/-2/-3). T-050 chờ chủ dự án cho gộp.
- Chủ dự án cho giao **T-052** (Thợ Máy): nhánh `team/T-052` từ `main` `c00b2e1`, worktree `wt-T-052`, đã đẩy nhánh; phiên "Thợ Máy · T-052 thẻ ảnh từ tên thư mục" đang làm.
- Số phiếu tiếp theo: **T-074**. Đang chạy: Thợ Máy T-049, Thợ Máy T-052.

### 2026-10-20 11:41 · Chỉ Huy B

- Chủ dự án cho gộp **T-051**: gộp vào `main` (`57fc6b9`), không xung đột. Windows 7.519 qua, 0 hỏng; ruff sạch. Đã đẩy, xóa nhánh `team/T-051` và worktree `wt-T-051`.
- T-065 (Ngòi Bút) hết chờ. T-062 nay chỉ chờ T-050.
- Đang chạy: Lá Chắn T-050, Thợ Máy T-049.

### 2026-10-20 11:24 · Chỉ Huy B

- Chủ dự án cho giao **T-049** (Thợ Máy): tạo nhánh `team/T-049` từ `main` `c1b21dc`, worktree `wt-T-049`, đã đẩy nhánh. Phiên "Thợ Máy · T-049 xử lý ảnh WebP giữ GPS" đang làm.
- **Lá Chắn T-051 rút gọn ĐẠT CÓ ĐIỀU KIỆN** (`507617e`): 2 lỗi Thấp, gộp được ngay. Chép điều kiện C1–C6 vào T-062 (mục Yêu cầu bảo mật riêng), C7–C9 vào T-053; lập **T-065** (Ngòi Bút, C10: chữ trong ảnh không chép vào alt lẫn chú thích). Số phiếu tiếp theo: **T-066**. T-051 chờ chủ dự án cho gộp.
- Lá Chắn T-050 vẫn đang kiểm.

### 2026-10-20 11:22 · Chỉ Huy B

- Chủ dự án cho làm tiếp. Gọi 2 phiên con (giao sau 10:11): Lá Chắn T-050, Lá Chắn rút gọn T-051.
- **Gộp T-058 vào `main`** (`0481f7e`, Pillow 13.0.0). Mở app thật trong trình duyệt của Claude Desktop (cấu hình chạy `D:\ProMetal-ToolSEO\.claude\launch.json`, ngoài repo): chủ dự án đăng nhập, B xem Bài viết, Soạn bài 5 bước, Kế hoạch, Cài đặt 4 thẻ, Kết nối WordPress: không lỗi, nhật ký app sạch. Windows 7.483 qua, 0 hỏng; ruff sạch. Đã đẩy, xóa nhánh `team/T-058` và worktree `wt-T-058`.
- Chủ dự án không nhớ mật khẩu app, đã đặt lại bằng `set_password.bat` (chỉ đổi mã băm trong `.env` trên máy Windows; máy khác không đổi).
- T-049 hết chờ (T-058 đã gộp): giao được khi chủ dự án cho làm tiếp.

### 2026-10-20 10:11 · Chỉ Huy B

- **Soi Lỗi T-050 lượt 2 ĐẠT** (`dc97e0c`): 4 lỗi lượt 1 sửa thật; 7.660 qua, 0 hỏng. 2 lỗi mới Thấp (SL-T050-5: hồ sơ màu ICC chỉ kiểm phần đầu, chở được chữ/EXIF; SL-T050-6: khối được nhận lặp lại hoặc dài hơn khuôn), đánh dấu `xfail`. Chờ Lá Chắn; Lá Chắn xem nên sửa ngay ở lượt nhỏ hay gom phiếu dọn.
- **Soi Lỗi T-051 rút gọn ĐẠT** (`10bc2f0`): 5.846 qua, 0 hỏng. SL-T051-1 → 4 chờ T-062; đã sửa tên khóa ở T-062 YC4 (SL-T051-5) và ghi SL-T051-6 (lời dặn alt bị cắt ở 4.000 ký tự) vào T-062. Chờ Lá Chắn rút gọn.
- Chưa giao Lá Chắn T-050, T-051: chờ chủ dự án cho làm tiếp. T-058 chờ mở app thật với chủ dự án.

### 2026-10-20 10:09 · Chỉ Huy B

- **Quyết định chủ dự án:** Chủ dự án chốt 2026-10-20: **chấp nhận rủi ro LC-T048-6** (hard link trong thư mục ảnh; ổ không có số inode). Đã ghi `docs/team/security.md` mục 6, `BAN-GIAO.md` 7.4, `TIEN-DO.md` mục 4, phiếu T-064. LC-T048-2/-3 vẫn sửa ở T-064.
- **Lá Chắn T-058 ĐẠT CÓ ĐIỀU KIỆN** (`fe53d97`): 4 lỗi Thấp. Điều kiện chép vào T-049 (điều kiện 5 của T-047 hết bắt buộc; giữ điều kiện 1–4, 6, 7; không xuất Arrow; `st.image` chỉ nhận ảnh đã mở an toàn; từ chối Pillow < 13) và T-056. Trước khi gộp: Chỉ Huy mở app thật xem mọi trang.
- Soi Lỗi T-050 lượt 2 và Soi Lỗi T-051 đang chờ lần chạy pytest toàn bộ.

### 2026-10-20 09:54 · Chỉ Huy B

- Chủ dự án cho làm tiếp. Gọi 3 phiên con (giao sau 09:17): Lá Chắn T-058, Soi Lỗi T-050 kiểm lại lượt 2, Soi Lỗi T-051 rút gọn.
- **Gộp T-048 vào `main`** (`f37ffd6`). Windows: 7.420 qua, 1 hỏng (`tests/test_app.py::test_correct_password_opens_home_and_logout_works`: app thử nghiệm quá 30 giây vì máy chạy 4 bộ test cùng lúc; chạy riêng `tests/test_app.py` lại thì 5/5 qua trong 11,8 giây). T-048 không đụng `app/` hay test này. ruff sạch. Xóa nhánh `team/T-048` và worktree `wt-T-048`.
- Ghi điều kiện Lá Chắn T-048 vào T-049, T-052, T-055, T-056. Lập **T-063** (Soi Lỗi chạy test T-048 trên Mac/Linux, chặn gộp T-056; máy Windows không làm được, cần phiên cloud) và **T-064** (Thợ Máy dọn lỗi Thấp: liệt kê thư mục qua handle, ký tự vô hình, `os.fstat`). Số phiếu tiếp theo: **T-065**.
- Bổ sung danh sách kiểm lại bằng Fable sau 01/11 trong `board.md`: T-036, T-037, T-042, T-044, T-045, T-046, T-047, T-048.
- **Lưu ý vận hành:** chạy pytest toàn bộ khi 3 agent cũng đang chạy test thì mất khoảng 23 phút và các test có giới hạn thời gian dễ hỏng oan. Hỏng kiểu "timed out" thì chạy riêng lại trước khi kết luận.

### 2026-10-20 09:17 · Chỉ Huy B

- Cả 3 phiên con xong, B đã kiểm nhánh (worktree sạch, khớp GitHub):
  - **Lá Chắn T-048 ĐẠT CÓ ĐIỀU KIỆN** (`7c1574d`). Điều kiện chính LC-T048-1: chạy test T-048 trên Mac hoặc Linux (6 test đang bị bỏ qua trên Windows) trước khi gộp T-056 và trước khi hết GĐ3. LC-T048-2/-3/-6 (lộ **tên** file ngoài thư mục ảnh khi máy đã có chương trình độc; hard link): Lá Chắn khuyên sửa ở phiếu dọn GĐ3, chủ dự án quyết.
  - **Thợ Máy T-050 lượt 2 xong** (`c3910e0`): 7.588 qua, 0 hỏng.
  - **Soi Lỗi T-058 ĐẠT** (`bda4dfc`): 7.232 qua, 0 hỏng.
- Chờ chủ dự án cho làm tiếp: gộp T-048; gọi Lá Chắn T-058, Soi Lỗi T-050 lượt 2; T-051 khi có chỗ.

### 2026-10-20 08:42 · Chỉ Huy B

- Đẩy hộ phần dở của A: `team/T-050` `ff5cb0a` (Thợ Máy lượt 2, `seo_app/ai/base.py`), `team/T-058` `042a626` (test Soi Lỗi). Cả hai chưa chạy test; agent làm tiếp phải kiểm lại trước.
- Gọi 3 phiên con dưới B, mỗi phiên làm trong worktree của phiếu: Lá Chắn T-048 (kiểm từ đầu), Thợ Máy T-050 lượt 2, Soi Lỗi T-058 rút gọn. T-051 chờ chỗ trống (tối đa 3 phiên).
- Lưu ý vận hành: worktree `wt-T-xxx` chưa được app tin cậy, nên phiên con mở ở `D:\ProMetal-ToolSEO` rồi `cd` vào worktree.

### 2026-10-20 08:38 · Chỉ Huy B tiếp quản từ Chỉ Huy A, không có bàn giao

- Chủ dự án báo A đã dừng, giao B nhận quyền. `main` = `ffaa1e6`, khớp GitHub.
- **Đổi chỗ chạy của B:** từ hôm nay B chạy trong Claude Desktop trên chính máy Windows của chủ dự án (bảng "Hai Chỉ Huy" đã sửa). B dùng chung các worktree `wt-T-xxx` với A, chạy được test Windows, và thấy được file A sửa dở chưa commit.
- Lúc nhận có 4 worktree: T-048 sạch; T-050 có `seo_app/ai/base.py` sửa dở (+47 −17, Thợ Máy lượt 2); T-058 có file mới `tests/test_soi_loi_t058.py` (Soi Lỗi rút gọn); T-051 sạch. B đẩy phần dở của T-050, T-058 lên nhánh rồi gọi tiếp Lá Chắn T-048, Thợ Máy T-050 lượt 2, Soi Lỗi T-058.

### 2026-10-20 07:46 · Chỉ Huy A

- T-050 Thợ Máy xong (`f5f8b63`): giao Soi Lỗi. T-051 Ngòi Bút xong (`fc39367`): `[tasks.image]` để tắt vì bật lên làm trang Soạn bài đòi khóa Gemini; lập **T-062** (Thợ Máy) cho phần đọc cấu hình. T-051 chờ Soi Lỗi rút gọn, Lá Chắn rút gọn. Số phiếu tiếp theo: **T-063**.
- Sửa ví dụ tên thư mục thẻ ảnh (quận Hải Châu là của Đà Nẵng) thành `Tân Phú` trong `CLAUDE.md`, `BAN-GIAO.md`.

### 2026-10-20 07:43 · Chỉ Huy A

- Gộp T-042 vào `main` (`81381c5`): Windows 7.170 qua, 0 hỏng. Đã đẩy lên, xóa nhánh `team/T-042`.
- T-048 lượt 2 Thợ Máy xong (`69d6b6c`, 5.846 qua): chờ Soi Lỗi kiểm lại ở chỗ trống kế tiếp (sau T-058).
- Giao **T-058** (Thợ Máy, nâng Pillow 13), worktree `wt-T-058`.

### 2026-10-20 07:31 · Chỉ Huy A

- Chỉ Huy B không có commit nào. Phiên trước của A kết thúc khi T-048 lượt 2, T-050, T-051 đang chạy: đã gọi tiếp cả ba. Lần chạy test sau khi gộp T-042 bị ngắt: đang chạy lại, `main` trên máy A có bản gộp T-042 **chưa đẩy** tới khi test đạt.
- **Quyết định chủ dự án:** Chủ dự án chốt 2026-10-20 (phiếu T-058): **nâng lên Pillow 13** (lựa chọn A), dù Streamlit khóa `pillow<13`, để vá 53 khuyến cáo của Pillow 12.3.0 mà Lá Chắn T-047 tìm ra. Thợ Máy nâng bằng `override-dependencies`, chạy đủ test, Chỉ Huy mở app thử mọi trang; hỏng thì quay về bản cũ. Đã ghi vào `CLAUDE.md`, `BAN-GIAO.md` 7.4, `TIEN-DO.md` mục 4, phiếu T-058. T-058 giao ngay khi có chỗ.

### 2026-10-19 18:27 · Chỉ Huy A

- Gộp T-047 vào `main` (`d350aec`): Windows 5.810 qua, 0 hỏng. Lá Chắn: Pillow 12.3.0 có 53 khuyến cáo mới, vá ở 13 (Streamlit khóa `<13`) → lập **T-058**, đã hỏi chủ dự án A (nâng Pillow 13) hay B (chấp nhận rủi ro). **T-049 chờ T-058.**
- Lá Chắn T-042 **ĐẠT CÓ ĐIỀU KIỆN** (`da24ba8`). Lập T-059 (thử thật), T-060 (dọn lỗi Thấp client), T-061 (shortcode trong chữ AI); điều kiện giao diện ghi vào T-041. Đang gộp T-042.
- Giao T-050 (Thợ Máy). Số phiếu tiếp theo: **T-062**.

### 2026-10-19 18:03 · Chỉ Huy A làm tiếp sau giới hạn sử dụng

- Sau 13:57 (giờ commit cuối của agent) tài khoản A chạm giới hạn, mở lại 18:00; 3 agent dừng (Lá Chắn T-047, Thợ Máy T-048 lượt 2, Thợ Máy T-042 lượt 3). Chỉ Huy B không có commit nào.
- T-042 lượt 3 đã xong trước khi dừng (`dab6e86`: 6.984 qua, 0 hỏng; 10 trường hợp xfail của Soi Lỗi nay qua). Giao **Lá Chắn T-042** kiểm bản cuối.
- Gọi tiếp Lá Chắn T-047 (chưa có biên bản) và Thợ Máy T-048 lượt 2 (`172ebf5` có L3, L4; đang làm L5).

### 2026-10-19 13:19 · Chỉ Huy A

- T-047 Thợ Máy xong (`3d46574`): Pillow 12.3.0 (không lên 13 được vì Streamlit 1.65 cần `pillow<13`), pillow-heif 1.8.1 (libheif 1.23.6, libde265 1.1.3, kèm x265 4.3 giấy phép GPLv2). Đang qua Soi Lỗi rút gọn, rồi Lá Chắn.
- **Lưu ý cho Chỉ Huy B:** `uv.lock` trên `team/T-047` đổi `revision` 3 → 5 vì máy A dùng uv 0.12.23. Khi T-047 lên `main`, máy cloud của B nên dùng uv cùng bản hoặc mới hơn (`uv self update`), nếu không `uv sync` có thể báo không đọc được lock.

### 2026-10-19 13:07 · Chỉ Huy A làm tiếp sau giới hạn sử dụng

- Chỉ Huy B không có commit nào. Xóa nhánh `team/T-045` đã gộp. Gọi tiếp 3 agent: Thợ Máy T-047 (`69a9442`, còn 1 file dở), Thợ Máy T-048 (`ca32762`), Soi Lỗi T-042 lượt 2 (từ `0dc2464`).

### 2026-10-19 08:31 · Chỉ Huy A dừng vì hết hạn mức (vẫn ghi là A giữ quyền; B nhận được nếu cần)

- Gộp T-045 vào `main` (`cc3099f`): Windows 5.791 qua, 0 hỏng. Lập T-057 (SL-T045-1/2, Thợ Máy). Nhánh `team/T-045` đã gộp, xóa được.
- Đã dừng 3 agent; việc dở nằm trên nhánh (kiểm `git log` và `git status` trong worktree trước khi làm tiếp):
  - `team/T-042`: Thợ Máy lượt 2 xong (`0dc2464`, 6.465 qua); Soi Lỗi kiểm lại lượt 2 **mới bắt đầu** → giao lại Soi Lỗi.
  - `team/T-047`: Thợ Máy đang chạy test cuối khi dừng → làm nốt báo cáo.
  - `team/T-048`: Thợ Máy đang chạy test cuối khi dừng → làm nốt báo cáo.
- Việc tiếp: T-050, T-051 khi còn chỗ; T-049 sau T-047.

### 2026-10-19 08:13 · Chỉ Huy A

- Lập 10 phiếu Giai đoạn 3 T-047 → T-056 (G3-1 → G3-10 của báo cáo T-046), kèm quyết định 19/10 và 11 góp ý Lá Chắn T-046. Thứ tự: (T-047, T-048, T-050, T-051) → (T-049, T-052) → (T-053, T-054, T-055) → T-056. T-054 còn chờ T-042. Số phiếu tiếp theo: **T-057**.
- Giao T-047 (Thợ Máy).

### 2026-10-19 08:10 · Chỉ Huy A

- **Quyết định chủ dự án:** Chủ dự án trả lời 5 câu Giai đoạn 3 ngày 2026-10-19 (báo cáo `docs/team/reports/T-046-tho-may.md` mục 8): **1A** thêm thư viện `pillow-heif` để đọc ảnh HEIC của iPhone (Lá Chắn quét lỗ hổng trước khi dùng); **2A** EXIF giữ GPS, ngày chụp, hãng và đời máy, bỏ số seri máy, tên chủ máy, khối dữ liệu riêng của hãng; **3A** thẻ ảnh đặt theo tên thư mục trong Drive (ví dụ `CT012 - Cổng inox - Tân Phú/truoc`), app không ghi gì vào Drive, thẻ sửa tay chỉ nhớ trên máy đang dùng; **4A** viết alt bằng Claude Sonnet, tạo ảnh bằng Gemini (mô hình ghi trong `config/ai.toml`, đổi được); **5A** ảnh trong bài dùng file đầy đủ 1600 px để GPS tới người xem và Google (không để WordPress tự chọn cỡ nhỏ). Đã ghi vào `CLAUDE.md` (Quyết định đã chốt), `BAN-GIAO.md` 7.4, `TIEN-DO.md` mục 4. Lập phiếu code Giai đoạn 3 từ T-047.

### 2026-10-19 07:30 · Chỉ Huy A

- Phiên Claude Code của A kết thúc chiều 17/10 khi 3 agent đang chạy: Soi Lỗi T-042 (chưa đẩy gì), Lá Chắn T-044 (đã đẩy biên bản dở `49f0533`), Soi Lỗi T-045 (chưa đẩy gì). Chỉ Huy B không có commit nào từ 16/10. 2026-10-19 07:30 đã gọi cả ba làm tiếp.
- Đã nhắc lại chủ dự án 5 câu Giai đoạn 3 (mục 8 báo cáo T-046). Các câu này không ảnh hưởng T-042, T-044, T-045.

### 2026-10-17 12:22 · Chỉ Huy A

- Sau 08:30 (giờ commit cuối của agent) tài khoản A chạm giới hạn sử dụng 5 tiếng, mở lại 12:20. Ba agent (Thợ Máy T-042, Soi Lỗi T-044, Thợ Máy T-045) dừng giữa chừng; phần lớn việc đã đẩy lên nhánh (`07c8626`, `3617509`, `d8e2dc1`), còn vài file sửa dở trong worktree. 12:22 đã gọi cả ba làm tiếp. Chỉ Huy B không có commit nào trong lúc dừng.

### 2026-10-17 07:31 · Chỉ Huy A tiếp quản từ Chỉ Huy B, không có bàn giao

- `git pull` về `main` = `4b910b1`. B vẫn ghi giữ quyền từ 16/10 13:10, bảng "Đang làm dở" cập nhật 16/10 14:19, không có mục trả quyền. B ghi giới hạn 7 ngày của tài khoản B mở lại khoảng 20/10 01:00.
- Đối chiếu nhánh với bảng của B:
  - `team/T-036` (`560fc3f`): Soi Lỗi lượt 2 đạt; **chưa có biên bản Lá Chắn** trên nhánh. Lá Chắn của B coi như dừng, giao lại từ đầu.
  - `team/T-037` (`09069b4`): Soi Lỗi lượt 2 **dở** ("CHƯA XONG: test SL-T037-1/2 và allowlist, dừng để bàn giao"). Giao Soi Lỗi làm nốt.
  - `team/T-046`: không có commit nào ngoài `main`; Thợ Máy của B chưa đẩy gì. Giao lại.
  - Đã gộp hết, xóa được: `team/T-019`, `T-025`, `T-031`, `T-032`, `T-033`, `T-034`, `T-035`, `T-038`, `T-043`.

### 2026-10-16 14:16 · Chỉ Huy B

- Lá Chắn T-038 (Opus tạm) **ĐẠT CÓ ĐIỀU KIỆN** (`6bb4871`). Gộp T-038 vào `main`: Linux 4.867 qua, 0 hỏng. Ba điều kiện ghi vào phiếu T-041: chặn Cs/Co/Cn; bỏ Markdown nội dòng, không đổi sang HTML; hiện `json_ld` bằng `st.code`.

### 2026-10-16 13:10 · Chỉ Huy B nhận lại quyền

- **Quyết định chủ dự án:** Chủ dự án trả lời 2026-10-16: **1A** (bật Abilities của SiteSEO để phần mềm ghi tiêu đề, mô tả, từ khóa chính vào bài nháp), **2A** (tạo tài khoản WordPress vai Biên tập viên riêng cho phần mềm), **3A** (đuôi " | Pro-Metal" khi tiêu đề còn chỗ, dưới 60 ký tự), **4A** (dọn khối Organization rỗng của SiteSEO, mô tả thừa "3 chi nhánh…" ở trang chủ, mức giá "$$"; chủ dự án hoặc người làm web làm), **5A** (đồng ý thêm thư viện Pillow cho Giai đoạn 3). Đã ghi vào `CLAUDE.md` (Quyết định đã chốt), `TIEN-DO.md` mục 4, `BAN-GIAO.md` 7.4, phiếu T-036, T-042.
- Làm tiếp: Soi Lỗi T-036; Thợ Máy T-037, T-038 (tối đa 3 phiên).

### 2026-10-16 13:00 · Chỉ Huy B trả quyền (chủ dự án yêu cầu bàn giao)

**Đã xong trong phiên B (15/10 18:02 → 16/10 13:00), đều đã lên `main`:**
- Gộp: T-025, T-019, T-033 (thiết kế GĐ4, chỉ tài liệu), T-032, T-035, T-031, T-043, T-034. **Giai đoạn 2 xong**, đã đánh dấu [x] trong `CLAUDE.md`.
- `main` = `49f57c9` + tài liệu. Linux: 4.658 qua, 0 hỏng; ruff sạch.
- Lập phiếu: T-032, T-033, T-034, T-035, T-036 → T-042 (Giai đoạn 4), T-043, T-044, T-045. Số phiếu tiếp theo: **T-047**.
- Quyết định chủ dự án 16/10: chưa trả lời 4 câu GĐ4; phần mềm phải chạy ổn định khi chưa có câu trả lời (đã ghi ở `TIEN-DO.md` mục 4, `BAN-GIAO.md` 7.4, phiếu T-036, T-041, T-042).

**Dở dang:** chỉ có T-036. Thợ Máy xong, chưa giao Soi Lỗi (bảng trên).

**Việc cho A:**
1. Chạy `uv run pytest` trên Windows với `main` mới. Các phiếu T-019, T-025, T-031, T-032, T-034, T-043 mới chạy trên Linux. Riêng T-031 chèn ký tự U+200B, T-034 đổi cách chặn `*_CUSTOM_HEADERS`.
2. Xóa nhánh đã gộp: `team/T-019`, `T-025`, `T-031`, `T-032`, `T-033`, `T-034`, `T-035`, `T-043`.
3. Làm tiếp T-036 (Soi Lỗi → Lá Chắn → gộp), rồi T-037, T-038.

**Lưu ý vận hành:**
- Tài khoản B: giới hạn 5 tiếng chạm 2 lần (15/10 19:03, 16/10 khoảng 08:40). Giới hạn **7 ngày** đang báo sắp chạm, mở lại khoảng 20/10 01:00.
- Agent phải đẩy lên GitHub sau mỗi phần nhỏ. T-031 và T-034 từng mất việc chưa đẩy khi chạm giới hạn.
- Lá Chắn của B vẫn chạy tạm bằng Opus 5.5. Danh sách kiểm lại bằng Fable ở đầu `board.md`.

### 2026-10-16 12:52 · Chỉ Huy B

- Lá Chắn T-043 (Opus tạm) **ĐẠT CÓ ĐIỀU KIỆN**: gộp được ngay, mở phiếu theo dõi. Gộp T-043 vào `main`: Linux 4.403 qua, 0 hỏng. Lập T-045 (theo dõi LC-T043-1, SL-T043-1, -2). Số phiếu tiếp theo: **T-047**.

### 2026-10-16 12:44 · Chỉ Huy B

- Khoảng 08:30–08:42, cả 3 phiên con và phiên Điều phối chạm giới hạn 5 tiếng; mở lại 12:40.
  - Soi Lỗi T-034 lượt 2: đã đẩy test `2353773`, chưa có báo cáo.
  - Lá Chắn T-043: chưa có biên bản.
  - Thợ Máy T-036: đã đẩy phần 1 `817cfcf`.
- B gọi cả 3 làm tiếp. Vẫn theo yêu cầu chủ dự án: làm xong việc dở rồi bàn giao, **không giao việc mới**.

### 2026-10-16 08:32 · Chỉ Huy B (đang kết thúc)

- Chủ dự án yêu cầu: xử lý nốt việc dở của các agent, nạp báo cáo, bàn giao để Chỉ Huy khác làm tiếp. B **không giao việc mới**; chờ 3 phiên đang chạy (Soi Lỗi T-034 lượt 2, Lá Chắn T-043, Thợ Máy T-036) xong rồi bàn giao.

### 2026-10-16 08:26 · Chỉ Huy B

- Lá Chắn T-031 (Opus tạm) **ĐẠT** (`799da73`). Gộp T-031 vào `main`: Linux 4.301 qua, 0 hỏng. Thêm 2 việc bắt buộc Giai đoạn 5 vào `board.md` (gỡ U+200B trước khi gửi WordPress; không đưa chữ đã gỡ vào `st.markdown`).
- **Việc cho A trên Windows:** chạy `uv run pytest` trên `main` (T-019, T-025, T-031, T-032 mới chạy trên Linux). Xóa giúp nhánh `team/T-031`.

### 2026-10-16 08:05 · Chỉ Huy B

- Lá Chắn T-035 rút gọn **ĐẠT** (`df63b95`). Gộp T-035 vào `main` (`4a5480b`, chỉ tài liệu). Giao T-043 cho Thợ Máy.
- **Khi gộp T-034:** soát lại dòng README mục 7.6 "AI trả về dữ liệu không đúng khuôn (có thể bài bị cắt…)" (Claude), vì T-034 đổi câu này thành câu giới hạn token.

### 2026-10-16 08:03 · Chỉ Huy B

- **Cảnh báo hạn mức:** tài khoản B báo sắp chạm giới hạn **7 ngày** (mở lại khoảng 2026-10-20 01:00 giờ VN). Nếu B dừng đột ngột, A nhận quyền theo bảng "Đang làm dở". Các nhánh đều đã đẩy lên GitHub.

### 2026-10-16 08:05 · Chỉ Huy B

- **Quyết định chủ dự án:** Chủ dự án 2026-10-16: chưa trả lời 4 câu hỏi Giai đoạn 4; yêu cầu phần mềm **vẫn chạy ổn định khi chưa có câu trả lời** và làm tiếp các việc khác. Cách làm:
  - mọi phần cần câu trả lời là tùy chọn, mặc định tắt hoặc theo phương án đề xuất, đổi được trong cấu hình;
  - khi chưa ghi được SEO lên SiteSEO, bước SEO cho chép tay (phương án C) và không báo lỗi;
  - T-042 vẫn chờ câu 1, 2.
  - Đã ghi vào `TIEN-DO.md` mục 4, `BAN-GIAO.md` 7.4, phiếu T-036, T-041, T-042.

### 2026-10-16 07:58 · Chỉ Huy B

- Lá Chắn T-032 (Opus tạm) **ĐẠT** (`bbe9016`). Gộp T-032 vào `main` (`cbfe37a`): Linux 3.558 qua, 0 hỏng. Xóa giúp nhánh `team/T-032`, `team/T-033` (đã gộp), cùng `team/T-019`, `team/T-025` nếu còn.
- Lập T-043 (3 lỗi Thấp của bộ lọc hồ sơ). Giao T-035 cho Thư Ký. Số phiếu tiếp theo: **T-045**.
- **Việc cho A khi ngồi máy Windows:** chạy `uv run pytest` trên `main` (T-025, T-019, T-032 mới chỉ chạy trên Linux).

### 2026-10-16 07:42 · Chỉ Huy B

- Tối 15/10 khoảng 19:03, cả 3 phiên con (Thợ Máy T-031, T-032 lượt 2, T-034) chạm giới hạn sử dụng 5 tiếng của tài khoản B. Phiên Điều phối của B cũng dừng. `main` không đổi từ `18e6a41`; A không nhận quyền trong lúc đó.
- Sáng 16/10 chủ dự án nhắn "Thử lại". B giữ quyền, gửi tin cho 3 phiên làm tiếp. T-031 và T-034 chưa đẩy commit nào, có thể phải làm lại từ đầu.
- Bài học: ra lệnh agent đẩy sau **mỗi phần nhỏ**; tránh chạy 3 phiên Opus nặng cùng lúc khi gần cuối khung 5 tiếng.

### 2026-10-15 18:58 · Chỉ Huy B

- T-033 (thiết kế Giai đoạn 4) xong, gộp `main`. Kết luận chính: SiteSEO 1.4.2 ghi được qua "Abilities" (cần bật công tắc) hoặc qua 4 khóa meta site đã mở sẵn; site đã tự xuất Article/Breadcrumb/LocalBusiness nên phần mềm không xuất các loại đó.
- Lập T-036 → T-042 (Giai đoạn 4). Số tạm trong báo cáo T-033 (T-034 → T-041) đã đánh lại; bảng đối chiếu ở `board.md`.
- **4 câu hỏi chờ chủ dự án** (chủ dự án đang treo máy, dặn không hỏi): ghi ở `TIEN-DO.md` mục 4. Bên nào gặp chủ dự án trước thì hỏi, ghi câu trả lời vào `CLAUDE.md` / `BAN-GIAO.md` 7 và nhật ký này.
- T-032: Soi Lỗi đạt có điều kiện; Thợ Máy lượt 2 đang sửa SL-T032-1.

### 2026-10-15 18:55 · Chỉ Huy B

- Lá Chắn T-019 (Opus tạm) **ĐẠT** (`2c3d23c`). Gộp T-019 vào `main` (`7d8f6f3`): Linux 3.344 qua, 0 hỏng; ruff sạch. Xóa nhánh `team/T-019` giúp. 5 lỗi Thấp của Soi Lỗi/Lá Chắn gom vào T-034 (7 lỗi).
- T-025 đã gộp (`39065cd`). Giao T-031 cho Thợ Máy. Lập T-035 (Thư Ký: README 3 hãng AI, thử mù). Số phiếu tiếp theo: **T-036**.
- Giai đoạn 2 còn: T-031, T-032 (Soi Lỗi đang kiểm), T-034, T-035. Xong 4 phiếu này thì đánh dấu [x] Giai đoạn 2 trong `CLAUDE.md`.

### 2026-10-15 18:42 · Chỉ Huy B

- Lá Chắn T-025 (rút gọn, Opus tạm) **ĐẠT** (`790b6c0`). Gộp T-025 vào `main` (`39065cd`): Linux 3.133 qua, 0 hỏng; ruff sạch. **Việc cho A khi ngồi máy Windows:** chạy `uv run pytest` một lượt để xác nhận 6 test đồng hồ kiểu Windows (`tests/test_soi_loi_t025.py`) qua trên máy thật. Xóa nhánh `team/T-025` giúp.
- Lập T-032 (bộ lọc hồ sơ nhận nhãn gõ sai), giao Thợ Máy. Số phiếu tiếp theo: **T-034** (đã lập thêm T-033 thiết kế Giai đoạn 4).
- Chủ dự án dặn B chạy tự động tới khi hết hạn mức, không hỏi lại.

### 2026-10-15 18:02 · Chỉ Huy B nhận quyền

- `git pull` về `main` = `d2fae78`. Đọc bàn giao 14:39 của A. Làm tiếp: T-019 (Thợ Máy làm nốt lượt 2), T-025 (kiểm tra Soi Lỗi của B), T-031 sau T-019.
- Mục "đang kết thúc" 14:10 của B đã cũ: A nhận và trả quyền sau đó (14:12 → 14:39).

### 14:39 · Chỉ Huy A trả quyền (chủ dự án: hạn mức sắp hết)

**Đã xong trong phiên A (14:12 → 14:39), đều đã lên `main`:**
- Chạy kiểm T-029 + T-030 trên Windows theo lệnh của B: 2 lượt đều 2.758 qua, 0 hỏng; test IPv6, `test_proactor_sendto_is_wrapped_on_windows`, các tham số `vong-lap-mac-dinh` đều PASSED.
- Lá Chắn T-028 **ĐẠT** (`9e55d38`; 3 lỗi Thấp: LC-T028-1 đổi sang `RLock` khi tiện, LC-T028-2 chấp nhận, LC-T028-3 gzip hỏng → gộp phiếu lớp AI sau).
- Gộp T-029 (`7c8604e`) và T-028 (`d08f8ca`). Windows 3.110 qua, 0 hỏng.
- Xóa nhánh đã gộp: `team/T-026`, `team/T-028`, `team/T-029`.
- Soi Lỗi T-019 đạt có điều kiện; Thợ Máy lượt 2 làm gần xong (bảng trên).
- Lập T-031. Số phiếu tiếp theo: **T-032**.

**Lưu ý:** Lá Chắn của A vẫn chạy tạm Opus 5.5 (tài khoản A không dùng được Fable). Danh sách kiểm lại bằng Fable sau 01/11 trong `board.md` đã có T-028, T-029, T-030.

### 2026-10-15 14:12 · Chỉ Huy A nhận quyền

- `git pull` về `main` = `39c8c1f`. Đọc bàn giao 14:10 của Chỉ Huy B, làm tiếp theo bảng "Đang làm dở".
- Về giờ lệch B nêu: các mốc giờ trong phiên A trước (11:00 → 13:50) là giờ A ước lượng, không lấy từ đồng hồ máy. Từ nay A ghi theo lệnh `date` (UTC+7).

### 2026-10-15 14:10 · Chỉ Huy B bàn giao cho Chỉ Huy A (chủ dự án yêu cầu)

**Đã xong trong phiên B (13:10 → 14:10):**
- **Gộp T-026 vào `main`** (`64383a5`): lớp AI chịu được thư viện lệch phiên bản, câu lỗi 400 cố định, client 3 hãng dùng địa chỉ chính thức. Lá Chắn ĐẠT.
- Phát hiện `main` **đỏ trên Linux** (9 test của T-027: thiếu `socket._fallback_socketpair` ở Python 3.12.3, máy không IPv6). Lập T-030, làm chung T-029. Cả hai đã qua Soi Lỗi và Lá Chắn (đạt có điều kiện), chỉ còn chạy trên Windows.
- T-028: Thợ Máy 2 lượt, Soi Lỗi đạt. Chờ Lá Chắn.
- Lập và làm T-019 (thử mù mô hình): Thợ Máy xong logic, Họa Sĩ xong giao diện. Chờ Soi Lỗi.
- **Quyết định chủ dự án:** giữ việc thư viện AI đọc `HTTPS_PROXY`, `SSL_CERT_FILE`; đã ghi sổ rủi ro `security.md` mục 6 và `BAN-GIAO.md` 7.4.
- Số phiếu tiếp theo: **T-031**.

**Lưu ý vận hành:**
- Phiên cloud của B **không xóa được nhánh** trên GitHub (máy chủ git từ chối). Nhánh đã gộp, A xóa giúp: `team/T-026`.
- Tài khoản của B đang gần giới hạn sử dụng 5 tiếng (mở lại khoảng 18:00).
- Lá Chắn của B chạy tạm Opus 5.5. Danh sách kiểm lại bằng Fable sau 01/11 trong `board.md` đã thêm T-026; khi gộp thì thêm T-028, T-029, T-030, T-019.

### 2026-10-15 14:05 · Chỉ Huy B

- Chủ dự án yêu cầu tạm dừng B, nhường A. Không giao việc mới; chờ 3 agent đang chạy làm xong rồi bàn giao.

### 2026-10-15 13:50 · Chỉ Huy B

- Lá Chắn T-029 + T-030 **ĐẠT CÓ ĐIỀU KIỆN** (`91dbdb9`): không lỗi Nghiêm trọng/Cao/Trung bình; 17 phép thử lách đều bị chặn. Điều kiện: (1) chạy test trên Windows (lệnh ở mục "Đang làm dở"); (2) Soi Lỗi thêm bản quyền PSF vào docstring, đang làm. Lỗi Thấp #2 (bộ chặn chỉ xét AF_INET/AF_INET6, có từ trước): không lập phiếu, ghi bảng việc.

### 2026-10-15 13:45 · Chỉ Huy B

- **Quyết định chủ dự án:** giữ việc thư viện AI đọc `HTTPS_PROXY`, `SSL_CERT_FILE` (mạng công ty có thể cần); ghi sổ rủi ro `security.md` mục 6 và `BAN-GIAO.md` mục 7.4. Biến `*_CUSTOM_HEADERS` bỏ qua ở T-028.

### 2026-10-15 13:35 · Chỉ Huy B

- Lá Chắn T-026 ĐẠT (`d102b0a`). Gộp vào `main` (`64383a5`); Linux: 2.717 qua, chỉ 9 test đỏ sẵn của T-027. Giao T-028 cho Thợ Máy.
- Phiên cloud không xóa được nhánh trên GitHub (máy chủ git từ chối). `team/T-026` đã gộp xong, Chỉ Huy A hoặc chủ dự án xóa giúp.

### 2026-10-15 13:10 · Chỉ Huy B nhận quyền

- `git pull` về `main` = `ce8bc62`. Đọc mục bàn giao 13:50 của Chỉ Huy A, sẽ làm tiếp theo bảng "Đang làm dở".
- Giờ trong mục bàn giao của A (13:50) lệch với giờ commit `ce8bc62` (13:08). Chỉ Huy B ghi giờ theo đồng hồ máy chủ (UTC+7).
- Đã kiểm tra: các phiên con cũ của B (Thợ Máy T-026, Soi Lỗi T-025 mở sáng 15/10) dừng từ 08:12 vì giới hạn sử dụng, không còn đẩy gì. Em lưu trữ chúng.
- Gộp `main` vào `team/T-025` (`ce1a79c`). Chạy toàn bộ test trên Linux: **9 hỏng, đều ở `tests/test_soi_loi_t027.py`**, và cũng hỏng y vậy trên `main`. Lập T-030, giao chung với T-029.

### 2026-10-15 13:50 · Chỉ Huy A trả quyền (chủ dự án yêu cầu dừng, để Chỉ Huy B làm tiếp)

**Đã xong trong phiên A (11:00 → 13:50), đều đã lên `main`:**
- Phiếu điều phối này; `docs/plan/` (kế hoạch SEO của chủ dự án, đọc `docs/plan/README.md` trước); ghi quyết định 15/10 vào `CLAUDE.md`, `TIEN-DO.md`, `BAN-GIAO.md`.
- Gộp T-022 + T-024 (`958a93e`) và T-027 (`e4107f2`). **Từ T-027, `uv run pytest` chạy xanh cả trên Windows** (trước đó 152 test đỏ oan trên Windows).
- Xóa các nhánh tạm đã gộp: `team/T-018`, `T-022`, `T-023`, `T-024`, `T-027`.
- Lập phiếu T-027, T-028, T-029. Số phiếu tiếp theo: **T-030**.

**Dừng giữa chừng (chi tiết ở bảng "Đang làm dở"):** Lá Chắn T-026 (chưa có biên bản), Soi Lỗi T-029 (có code và test, chưa báo cáo).

**Gợi ý cho Lá Chắn T-026** (lời giao A đã soạn, dùng lại được):
- Diff riêng của T-026, không tính T-027 đã kiểm: `git diff ed0324e c906285` (trước khi merge main) và `git diff e4107f2 ac9fbda` (sau merge `3366566`). File code: `seo_app/ai/base.py`, `registry.py`, `anthropic_provider.py`, `openai_provider.py`, `gemini_provider.py`, `seo_app/env_file.py`.
- Trọng tâm: S2 (câu lỗi 400 không còn chữ nào của máy chủ ngoài mã đã qua `safe_code`; mã không thành link); W4 / `security.md` 2.7 (đủ 6 chỗ tạo client có `base_url` chính thức cố định); bắt lỗi rộng `ImportError/AttributeError/TypeError/KeyError` → câu "uv sync" có che lỗi bảo mật không.
- Đánh giá 2 điểm Chỉ Huy A đã quyết: SL-T026-3 **chấp nhận** (Gemini nhận JSON sai kiểu → câu "uv sync" thay vì "dữ liệu lạ", không lộ gì); SL-T026-4 → T-028.
- Thợ Máy nêu, ngoài phạm vi: thư viện AI vẫn đọc `HTTPS_PROXY`, `SSL_CERT_FILE`, `OPENAI_CUSTOM_HEADERS`, `ANTHROPIC_CUSTOM_HEADERS`. Cần Lá Chắn đánh giá có lập phiếu không; lưu ý chủ dự án có thể dùng mạng công ty phải đi qua proxy.

**Lưu ý vận hành:**
- Tài khoản của A gọi Fable 5.1 bị từ chối ("cần mua thêm lượt dùng"), nên Lá Chắn T-027 chạy tạm Opus 5.5. Danh sách kiểm lại bằng Fable sau 01/11 trong `board.md` đã thêm T-027.
- Tài khoản của A chạm giới hạn sử dụng lúc 12:00 khi 2 agent chạy cùng lúc. Agent nên commit và push từng phần nhỏ.
- A làm trên Windows (Claude Desktop, mỗi agent một git worktree). Các worktree đã xóa; nhánh còn trên GitHub.
- Các nhánh cũ `claude/project-thread-bcuk2m`, `claude/wizardly-brahmagupta-f0w8d8` đã gộp hết vào `main` từ trước, xóa được khi tiện.

### 2026-10-15 11:00 · Chỉ Huy A nhận quyền

- `git pull` về `main` = `157899b`. Chưa có phiếu điều phối chung trước đây, nên đây là mục đầu tiên. Mục "Đang làm dở" của Chỉ Huy B lấy theo `board.md` và lịch sử git.
- Hiện trạng các nhánh lúc nhận:
  - `team/T-024` (đã gộp `team/T-022`): Lá Chắn **ĐẠT** (`41e4165`, 08:09), **chưa gộp** vào `main`.
  - `team/T-025`: Soi Lỗi có 2 commit (`5ff60f3`, `a1d48d4`), **chưa có báo cáo**, chưa qua Lá Chắn.
  - `team/T-026`: chỉ là điểm tạo nhánh, chưa có việc. Phiếu T-026 chưa giao.
  - `team/T-018`, `team/T-023`: đã gộp hết vào `main`, xóa được.
- Phát hiện: chạy `uv run pytest` **trên Windows** có 152 test đỏ (2.009 qua). 148 test hỏng vì bộ chặn mạng trong `tests/conftest.py` chặn cả kết nối `127.0.0.1` mà asyncio trên Windows cần để khởi động (trên Linux thì không cần). 4 test đặt biến môi trường dài quá 32.767 ký tự (giới hạn của Windows). Code ứng dụng không lỗi; phần sai nằm ở bộ test. Sẽ lập phiếu cho Soi Lỗi.
- Quyết định chủ dự án ngày 2026-10-15:
  - Mô hình AI: **không có mặc định**. Giữ đủ cả 3 hãng (Claude, ChatGPT, Gemini), chủ dự án tự đổi khi cần. Không đổi `config/ai.toml` sang Gemini. T-019 (thử mù) hết chờ.
  - **Giữ Giai đoạn 6** (theo dõi thứ hạng qua Search Console).
  - Đưa thư mục `plan/` (kế hoạch SEO, yêu cầu phần mềm) lên repo.
  - Lập phiếu điều phối chung này. Phiên "Điều Phối" thứ ba trên máy chủ dự án đã bị bỏ, không tính.

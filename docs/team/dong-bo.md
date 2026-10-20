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

**Chỉ Huy B**, từ 2026-10-20 08:38 (chủ dự án báo A đã dừng, giao B nhận quyền). Tiếp quản **không có bàn giao**: commit cuối của A lúc 08:11, file sửa cuối trong worktree lúc 08:14.

## Đang làm dở

_Bên đang giữ quyền cập nhật mục này sau mỗi bước._

Chỉ Huy B, cập nhật 2026-10-20 09:54. Bảng cũ của A (cập nhật 17/10) đã cũ; bảng này B lập lại từ nhật ký, `git log` và các worktree. Agent chạy ở phiên con dưới phiên B, mỗi phiếu một worktree `D:\ProMetal-ToolSEO\wt-T-xxx`, đẩy lên nhánh `team/T-xxx`. Tối đa 3 phiên con cùng lúc.

| Phiếu | Nhánh | Đang ở bước | Việc tiếp theo |
|---|---|---|---|
| [T-048](tickets/T-048-doc-thu-muc-anh-an-toan.md) Đọc thư mục ảnh an toàn (GĐ3) | đã gộp (`f37ffd6`), nhánh đã xóa | ✅ Lá Chắn ĐẠT CÓ ĐIỀU KIỆN; 09:54 gộp vào `main` | Điều kiện đã ghi vào T-049, T-052, T-055, T-056; lập T-063 (test Mac/Linux, chặn gộp T-056), T-064 (dọn lỗi Thấp). LC-T048-6 chờ chủ dự án (sổ rủi ro) |
| [T-050](tickets/T-050-lop-ai-doc-anh-goi-y-alt.md) Lớp AI đọc ảnh, gợi ý alt (GĐ3) | `team/T-050` (`c3910e0`) | Thợ Máy lượt 2 xong (7.588 qua). ⏳ **Soi Lỗi kiểm lại lượt 2** (phiên "Soi Lỗi · T-050 lượt 2 kiểm lại", giao sau 09:17) | Lá Chắn (soát A3: `base.py:552–790`, `alt.py:96–143`) |
| [T-058](tickets/T-058-nang-pillow-13.md) Nâng Pillow 13 (GĐ3, chặn T-049) | `team/T-058` (`bda4dfc`) | Soi Lỗi rút gọn ĐẠT (7.232 qua). ⏳ **Lá Chắn đang kiểm** (phiên "Lá Chắn · T-058 kiểm Pillow 13", giao sau 09:17) | ĐẠT thì gộp, chạy test, Chỉ Huy mở app thử mọi trang; rồi giao T-049 |
| [T-051](tickets/T-051-prompt-alt-va-cau-hinh-anh.md) Prompt alt, cấu hình ảnh (GĐ3) | `team/T-051` (`fc39367`) | Ngòi Bút xong. ⏳ **Soi Lỗi rút gọn đang kiểm** (phiên "Soi Lỗi · T-051 kiểm cấu hình alt, ảnh", giao sau 09:17) | Lá Chắn rút gọn |
| Chờ phiếu trước | | T-052 (còn chỗ), T-063 (cần máy Linux/Mac), T-049 (sau T-058), T-062 (sau T-050, T-051), T-064, T-039 → T-041, T-057, T-060, T-061; T-059 chờ chủ dự án bật Abilities và tạo tài khoản Biên tập viên | Số phiếu tiếp theo: **T-065** |
| `main` | `f37ffd6` + tài liệu | Windows sau gộp T-048: 7.420 qua, 1 hỏng vì quá tải (`test_app.py` quá 30 giây khi 4 bộ test chạy cùng lúc; chạy riêng lại 5/5 qua). Lá Chắn chạy đúng bản gộp: 7.421 qua, 0 hỏng. ruff sạch | |

## Nhật ký bàn giao

_Mục mới nhất ở trên cùng._

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

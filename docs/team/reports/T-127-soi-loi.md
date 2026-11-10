# Báo cáo T-127 · Nút «Đưa vào kế hoạch» (từ khóa Google → đề xuất «Thêm» chờ duyệt) · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | T-127 (phiếu trên `main`: `docs/team/tickets/T-127-dua-tu-khoa-vao-ke-hoach.md`; LC-T120-13, -15, -24), nhánh `team/T-127`: mã Thợ Máy `523b0ce`, `0505f31`, báo cáo `0c1f286` (gốc `09fdad2`) |
| Ngày nộp | 2026-11-10 (11:53 +07:00) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (SL-T127-1). Sáu trọng tâm Chỉ Huy giao: bộ lọc chặt đúng (mọi ca thử bị bỏ: ký tự vô hình, chữ toàn khổ, chữ Nga, chữ Hy Lạp, `=HYPERLINK`, số điện thoại 5 dạng; 80 ký tự nhận, 81 bỏ); tối đa 10; chỉ ra đề xuất chờ duyệt, không ghi Sheet; không gọi AI; không lùi trang Kế hoạch, T-098, T-125 (gộp thử `main` `7153f0a`: 1.246 qua, 0 hỏng). Riêng **kiểm trùng bài đã đăng chưa như T-098** (SL-T127-1): dùng danh sách bài trên máy kể cả đã cũ, không tải lại, không báo. Sửa 2 dòng (bản sửa nháp: ca `xfail` thành XPASS, 93 ca khác qua). Điều kiện: sửa ở lượt 2 trước Lá Chắn đầy đủ, hay Chỉ Huy cho chuyển phiếu sau |

## Tóm tắt (cho chủ dự án)

- **Nút «Đưa vào kế hoạch» làm đúng và an toàn.**
  - Ô chọn chỉ có từ khóa «sạch». Tôi thử nhiều kiểu chữ lạ: ký tự vô hình, chữ giả dạng (chữ Nga trông như chữ Việt), chữ toàn khổ, công thức bảng tính, số điện thoại viết liền, cách, gạch. Tất cả đều bị loại.
  - Mỗi lần tối đa 10 từ khóa. Từ khóa chỉ thành đề xuất chờ anh/chị duyệt ở trang Kế hoạch; phần mềm không tự ghi vào Google Sheet, không gọi AI.
  - Trang Kế hoạch, trang Theo dõi và cách nạp kế hoạch cũ vẫn chạy như trước.
- **Lỗi nhỏ (SL-T127-1):** khi so từ khóa với bài đã đăng trên website, nút này dùng danh sách bài đang lưu trên máy, dù danh sách đó đã cũ (ví dụ lưu từ hôm qua). Bài mới đăng sau đó không được so, và phần mềm không báo gì.
  - Cách nạp kế hoạch cũ thì tải lại danh sách khi cũ hơn 6 giờ, và báo khi không tải được.
  - Hậu quả: có thể đề xuất viết bài mới trùng một bài vừa đăng mà không có cảnh báo. Anh/chị vẫn phải duyệt từng đề xuất nên không có gì tự ghi.
  - Sửa: đổi 2 dòng cho giống cách cũ.
- **Không có việc gì cần chủ dự án quyết.**

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t127.py` | Mới: **29 ca: 28 qua, 1 `xfail(strict=True)`** của SL-T127-1. Không gọi mạng; dùng lại fixture, dữ liệu mẫu, client giả đếm lệnh của `test_t125_tracking_page.py`, `test_t127_dua_vao_ke_hoach.py` |
| `docs/team/reports/T-127-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, test của Thợ Máy, phiếu hay file khác.

## 1. Sáu trọng tâm Chỉ Huy giao

| # | Trọng tâm | Kết quả |
|---|---|---|
| 1 | **Bộ lọc chặt (LC-T120-24)** | **Đúng.** `google_keyword` chỉ nhận 186 chữ (a–z, «đ», 12 nguyên âm tiếng Việt với đủ 5 dấu thanh, cả hoa), số 0–9, dấu cách thường, «-»; chuẩn NFC trước khi đếm; ≤ 80 ký tự; có ít nhất một chữ; `personal_info` không thấy gì; không có chữ «www», «http», «https». Tôi thử thêm 26 kiểu (`test_strict_filter_rejects`), đều bị bỏ: ZWSP, word joiner, BOM, «chữ» Hangul U+3164, soft hyphen, RLO; chữ, số toàn khổ; «с» Nga, «ο» Hy Lạp; `=HYPERLINK(...)`, `=1+1`, `+…`; NBSP, tab, xuống dòng; gạch dài; dấu tổ hợp lạ U+0336; số điện thoại liền, cách, gạch, đầu 84, số bàn; «www …», «http …»; 81 ký tự. Nhận: 80 ký tự, chữ tổ hợp tách rời (NFD → NFC), nhiều dấu cách (gộp). Ô chọn ở trang Theo dõi chỉ có từ khóa qua bộ lọc (ca của Thợ Máy); trang Kế hoạch lọc lại lần nữa |
| 2 | **Tối đa 10 từ khóa mỗi lần** | **Đúng.** `st.multiselect(max_selections=10)`, cắt 10 khi đặt vào phiên, và `from_google_keywords` cắt 10 lần nữa (danh sách trong phiên không được tin), câu báo chỉ đếm số (ca của Thợ Máy) |
| 3 | **Chỉ ra đề xuất chờ duyệt, không ghi thẳng Sheet** | **Đúng.** Trang Theo dõi chỉ đặt `plan_google_keywords` (tuple chữ) rồi chuyển trang; trang Kế hoạch dựng đề xuất trên kế hoạch vừa đọc và đưa vào ô duyệt có sẵn (`keep_proposals`); ghi Sheet vẫn chỉ qua «Áp dụng» (đọc lại Sheet trước khi ghi, T-100). Ca của Thợ Máy đếm lệnh: 0 lệnh Google, WordPress. Đề xuất có cảnh báo không được tick sẵn |
| 4 | **Không gọi AI** | **Đúng.** Đường đi: `plan_box` → `take_google_keywords` → `from_google_keywords` → `check_proposals`; không chạm `run_ai`, `plan_changes`, lớp AI. Ca AST của Thợ Máy qua |
| 5 | **Kiểm trùng như T-098** | Luật kiểm giống hệt (gọi đúng `check_proposals`): trùng dòng kế hoạch, trùng bài đã đăng, trang cửa ngõ (ca hàm của Thợ Máy). Tôi thêm ca **ở mức trang** (`test_published_post_duplicate_is_warned_when_the_list_is_fresh`): danh sách bài còn mới thì đề xuất «sửa cửa kéo bị kẹt» cảnh báo cả trùng dòng B-012 lẫn trùng bài 11, không gọi website. **Nhưng nguồn danh sách bài khác T-098: SL-T127-1** |
| 6 | **Không lùi trang Kế hoạch, T-098, T-125** | **Đúng.** Thợ Máy không đổi test cũ nào (R5: chỉ thêm `tests/test_t127_dua_vao_ke_hoach.py`). Mọi file test nơi gọi `propose.py` và hai trang, trên bản gộp thử với `main` `7153f0a`: 1.246 qua, 0 hỏng (mục 4) |

## 2. Lỗi mới

### SL-T127-1 · Thấp · Kiểm trùng bài đã đăng dùng danh sách trên máy kể cả đã cũ, không tải lại, không báo

- **Ở đâu:** `app/views/plan.py`, `take_google_keywords`: `index = cached_index()`.
  - `cached_index()` chỉ đọc bản lưu tạm, không xét tuổi: cũ bao lâu cũng dùng. Không có bản lưu tạm, hay chưa dựng được client WordPress, thì trả `None`: bỏ qua phép kiểm trùng bài đã đăng.
  - Hai đường đề xuất của T-098 (`read_source`, `read_sheet_link`) dùng `fresh_index()`: cũ hơn 6 giờ thì tải lại từ website; không tải được hay chưa kết nối thì đưa câu báo vào ghi chú đề xuất.
- **Tái hiện** (`test_sl_t127_1_stale_published_list_is_refreshed_or_told`):
  - Mở trang Theo dõi, chọn «sửa cửa kéo bị kẹt».
  - Danh sách bài trên máy lưu cách đây 7 giờ (lần lấy số liệu Google gần nhất từ hôm trước; trang Theo dõi vẫn vẽ bảng từ bản này).
  - Bấm «Đưa vào kế hoạch».
  - **Kết quả:** 0 lần gọi website, không câu báo nào về danh sách bài; đề xuất dựng trên danh sách 7 giờ trước. Với `fresh_index()` (đường T-098), cùng tình huống sẽ tải lại, hay báo «Chưa tải được danh sách bài đã đăng…».
- **Hậu quả:** bài đăng sau lần lưu danh sách không được so. Có thể ra đề xuất viết bài mới trùng một bài vừa đăng mà không có cảnh báo, và người dùng không biết phép kiểm thiếu.
- **Xếp Thấp:** người dùng vẫn duyệt từng đề xuất; không ghi gì tự động; danh sách cũ vẫn bắt được trùng với các bài đã có lúc lưu.
- **Gợi ý sửa** (2 dòng, như T-098):

  ```python
  index, notice = fresh_index()
  ...
  keep_proposals(found, base, index, [MSG_GOOGLE_FROM, *([notice] if notice else [])])
  ```

  Bước này chạy sau khi người dùng bấm nút, nên được gọi website như hai đường T-098. Danh sách còn mới (thường gặp) thì vẫn không gọi mạng.
- **Bản sửa nháp** (worktree tạm, đúng 2 dòng trên): ca `xfail` thành XPASS; `test_soi_loi_t127.py` và `test_t127_dua_vao_ke_hoach.py`: 93 ca khác qua (kể cả ca «0 lệnh mạng» của Thợ Máy, vì danh sách mẫu còn mới).

## 3. Ghi nhận (không chặn)

- **GN-1:** ca trang của Thợ Máy chạy khi chưa khai báo tài khoản WordPress, nên trang Kế hoạch không dựng được client; `cached_index()` trả `None`; phép kiểm trùng bài đã đăng chưa từng chạy ở mức trang. Ca đối chứng mới của tôi khai báo tài khoản giả để phủ chỗ này.
- **GN-2 (đúng thiết kế LC-T120-24):** câu lệnh viết bằng chữ thường, không dấu câu, dưới 80 ký tự vẫn qua bộ lọc, ví dụ một câu 47 ký tự bảo AI bỏ qua hướng dẫn. Đây là rủi ro Lá Chắn T-120 đã chấp nhận: phải có nhiều người gõ đúng câu đó trong 2–3 tháng; dòng kế hoạch vẫn qua mọi bộ kiểm, và khi viết bài từ khóa vào lời dặn AI trong khung dữ liệu như T-098. Lá Chắn đầy đủ nên xem lại.

## 4. Bằng chứng

```
# Windows 11, Python 3.12.15. Không chạy toàn bộ pytest.

# 1) Test Soi Lỗi trên nhánh (team/T-127 + file test mới)
$ uv run pytest -q tests/test_soi_loi_t127.py -rxX
28 passed, 1 xfailed                       ← xfail: SL-T127-1
$ uv run pytest -q tests/test_soi_loi_t127.py --runxfail -k sl_t127
E   assert (False or False)                ← không tải lại, không báo
1 failed

# 2) Bản sửa nháp SL-T127-1 (worktree tạm, 2 dòng)
$ pytest test_soi_loi_t127 test_t127_dua_vao_ke_hoach
1 XPASS(strict); 93 passed

# 3) Gộp thử team/T-127 + main 7153f0a (git merge-tree: không xung đột), worktree tạm tách rời,
#    seo_app nạp từ chính worktree tạm. Mọi file test nơi gọi propose.py, trang Kế hoạch, trang
#    Theo dõi, test quét gói liên quan
$ pytest test_t127_dua_vao_ke_hoach test_plan_propose test_plan_ai test_plan_sync \
         test_soi_loi_t098 test_soi_loi_t100 test_soi_loi_t103 test_soi_loi_t109 \
         test_la_chan_t100 test_la_chan_t103 test_t103_plan_prompt test_t113_website_status \
         test_t125_tho_may test_tracking_model
1150 passed, 1 skipped
$ pytest test_app_pages test_t101_plan_page test_t101_home_page test_t125_tracking_page \
         test_soi_loi_t125
96 passed
$ uv run ruff check .                       # cây gộp
All checks passed!
$ uv run ruff format --check tests/test_soi_loi_t127.py
1 file already formatted

# 4) Ký tự ẩn, CR: 0 trong file test mới và báo cáo này.
# 5) Quét bí mật: bản sao file test mới và báo cáo ở thư mục nháp, PYTHONUTF8=1,
#    detect-secrets --all-files (đứng trong thư mục quét): results {}.
#    Đối chứng: thêm file mồi có khóa giả (chữ tiếng Việt) → bắt được. Đã xóa mồi.
```

## 5. Đề xuất cho Chỉ Huy

- Giao Thợ Máy sửa SL-T127-1 ở lượt 2 (2 dòng), rồi gỡ dấu `xfail` (R5: chỉ gỡ dấu, không đổi kỳ vọng). Hay chuyển phiếu sau, tùy Chỉ Huy.
- Lá Chắn đầy đủ: xem GN-2.

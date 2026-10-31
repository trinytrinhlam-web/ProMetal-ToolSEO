# Báo cáo T-113 (phần Thợ Máy) · LC-T113-1: ngày website cuối năm 9999 không làm lõi tràn

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Việc | LC-T113-1 (Thấp), Lá Chắn T-113 tìm trong lõi T-109 (`docs/team/reports/T-113-la-chan.md`). Chỉ Huy B giao 31/10 14:20, cho phép sửa `seo_app/plan/` ngoài phạm vi T-113 |
| Nhánh | `team/T-113` (từ `d67fb32`) |
| Ngày nộp | 2026-10-31 14:19 (+07:00, theo lệnh `date`) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Đã sửa lỗi nhỏ Lá Chắn tìm ra. Nếu một bài trên website có ngày ở cuối năm 9999 (ngày vô lý, phải có người cố tình đặt), bấm «🌐 Cập nhật trạng thái từ website» trước đây hiện lỗi kỹ thuật. Nay phần mềm coi đó là «giờ không đọc được»: vẫn đề xuất đổi Trạng thái như bình thường, không ghi ô ngày, có cảnh báo.
- Sửa thêm một chỗ cùng kiểu. Giờ sát năm 9999 đọc từ file nháp trên máy (nếu file bị sửa tay) cũng không còn làm trang Kế hoạch hiện lỗi kỹ thuật.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/plan/website.py` | `_due_of`: xét năm theo **giờ UTC trước** khi đổi sang giờ Việt Nam (`YEAR_MIN - 1 ≤ năm UTC ≤ YEAR_MAX`). Ngoài khoảng thì `(None, True)` («giờ lạ»). Trong khoảng thì đổi múi giờ an toàn, rồi xét lại năm giờ Việt Nam như cũ, để ô «Ngày đăng thực tế» ghi ra luôn đọc lại được (`parse_plan_datetime` xét năm giờ Việt Nam). Kết quả: `OverflowError` không còn lọt ra; cảnh báo `ODD_DATE`, vẫn đề xuất đổi Trạng thái, không đổi ngày (đúng hợp đồng `test_odd_website_date_changes_status_but_not_date`) |
| `seo_app/plan/sync.py` | `_moment_text`: `astimezone` tràn thì thành `ValueError` («thời điểm ngoài khoảng»), không lọt `OverflowError`. Nơi gọi trên giao diện đã bắt `ValueError` (`retry_pending` ở trang Kế hoạch; `record_plan` ở Soạn bài bắt mọi lỗi) |
| `tests/test_la_chan_t113.py` (của Lá Chắn) | Gỡ dấu `xfail(strict=True)` của 4 ca LC-T113-1 (chỉ xóa dấu: bỏ hằng `LC_T113_1`, `DATES` thôi gắn dấu); thân test không đổi; 2 ca đối chứng `16:59:59` giữ nguyên (R5) |
| `tests/test_t109_website_status.py` (của Thợ Máy) | Thêm 9 ca (mục Kiểm thử) |

## Rà các chỗ đổi múi giờ khác (`website.py`, `sync.py`)

| Chỗ | Đầu vào | Kết luận |
|---|---|---|
| `website._due_of` | `date_gmt` của website (chưa tin cậy) | **Sửa** (LC-T113-1) |
| `website._time_text` | giờ website đã qua `_due_of`, hay `PlanRow` (năm 2020–2035) | An toàn |
| `website._same_moment`, `_close`, `now - due`, `now - checked_at` | như trên; giờ máy | An toàn (trừ, so sánh giữa hai giờ trong khoảng) |
| `sync._moment_text` | giờ máy; giờ hẹn người dùng chọn (`schedule`: ≤ 365 ngày); giờ website đã qua `_due_of`; `PlanStatusWrite.published_at` đọc lại từ `drafts.sqlite` (khuôn `AwareDatetime`, **không** kiểm năm) | **Sửa**: file nháp bị sửa tay có giờ sát năm 9999 thì trước đây `retry_pending` ở trang Kế hoạch ném `OverflowError` (giao diện chỉ bắt `ValueError`). Nay thành `ValueError`, nên hiện câu cố định. Việc ghi đó vẫn kẹt cho tới khi file được sửa; file nháp nằm trên máy, muốn sửa phải có quyền vào máy, nên không cần làm thêm |
| `sync._cached_at` | `fetched_at` của cache, đã đổi múi giờ sẵn trong `plan_cache._parse_time` | An toàn ở `sync` |

**Ngoài phạm vi, ghi lại để Chỉ Huy quyết:** `seo_app/storage/plan_cache.py:326` (`_parse_time`) gọi `parsed.astimezone(...)` mà chỉ bắt `ValueError`. File `data/plan_cache.sqlite` bị sửa tay với giờ kiểu `9999-12-31T23:59:59-05:00` sẽ ném `OverflowError` khi mở trang Kế hoạch. Cùng kiểu LC-T113-1 nhưng ở `seo_app/storage/` (ngoài phần anh cho phép), lại cần quyền vào máy. Đề xuất một dòng `except (ValueError, OverflowError)` ở phiếu dọn sau.

## Kiểm thử

- `tests/test_t109_website_status.py`, `tests/test_soi_loi_t109.py`, `tests/test_la_chan_t113.py`: **214 qua**. 4 ca LC-T113-1 (2 ở lõi, 2 qua trang Kế hoạch bằng AppTest) trước là `xfail` nay qua thật; 2 ca đối chứng vẫn qua.
- Test mới (9 ca):
  - `_due_of` theo biên năm: cuối năm 9999 (3 giờ), 23:59 ngày 31/12/2035 giờ Việt Nam (nhận), 00:00 ngày 01/01/2036 giờ Việt Nam (lạ), 00:00 ngày 01/01/2020 giờ Việt Nam (nhận), trước đó một phút (lạ), năm 1 (lạ);
  - `_moment_text` với giờ sát năm 9999: `ValueError`, giờ thường vẫn đúng chữ.
- Test liên quan: 22 file. Gồm T-113 (`test_t113_website_status`, `test_soi_loi_t113`, `test_la_chan_t113`), T-109 (2 file), T-100 (`test_plan_sync`, `test_plan_cache`, `test_t100_drafts_plan`, `test_t100_google_identity`, `test_soi_loi_t100`, `test_la_chan_t100`), T-101 (4 file + `test_la_chan_t101`), T-098/T-103 (`test_plan_model`, `test_plan_parse`, `test_plan_propose`, `test_plan_ai`, `test_t103_plan_prompt`), `test_google_sheets`. Kết quả: **1309 qua, 0 hỏng, 0 xfail, không XPASS** (5 phút 27 giây).
- `uv run ruff check .`: All checks passed. `ruff format --check` các file đã sửa: sạch.

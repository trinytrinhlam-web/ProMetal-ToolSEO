# Báo cáo T-112 · Chuẩn bị bật Hẹn giờ / Đăng ngay (phần Họa Sĩ)

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | T-112 (Chỉ Huy B giao 31/10 09:40) |
| Ngày nộp | 2026-10-31 |
| Nhánh | `team/T-112` (từ `d6df633`: `main` cục bộ `3cdd096` có T-102 + ghi chú `[plan]` của Ngòi Bút). Không gộp `main` |
| Kết quả | Xong yêu cầu 1, 2, 4, 5, 6 của phiếu; yêu cầu 3 (so `modified_gmt`) Chỉ Huy chuyển sang T-115 (Thợ Máy). Công tắc Hẹn giờ/Đăng ngay **vẫn mặc định tắt**, nay có nút ở Cài đặt (chỉ trong phiên, phương án A Chỉ Huy chọn). 16 ca test mới, gỡ 4 dấu `xfail` (SL-T102-1 ×3, LC-T102-1) |

## 1. Tóm tắt (cho chủ dự án)

- Công tắc Hẹn giờ / Đăng ngay **vẫn tắt** như trước. Phiếu này sửa những chỗ Lá Chắn và Soi Lỗi bắt buộc phải sửa trước khi bật:
  - **Đăng ngay** giờ chỉ đăng bài khi ảnh đại diện và SEO (nếu bạn bật «Ghi SEO lên website») đã lên website. Một trong hai bị lỗi lúc gửi thì bài **vẫn là nháp**, app nói rõ phần nào chưa lên; bạn sửa trong trang quản trị rồi tự bấm «Đăng» ở đó.
  - **Hẹn giờ** vẫn hẹn giờ khi thiếu một phần, nhưng báo rõ phần chưa lên để bạn sửa trước giờ đăng (hoặc chuyển bài về nháp).
  - Lệnh hẹn giờ/đăng không rõ kết quả (mất mạng đúng lúc): app không ghi gì vào dòng kế hoạch trên Google Sheet, để Sheet không nói sai «nháp».
  - Bài đã gửi mà bạn muốn gửi thêm một bài nữa: ô tick nói đúng việc sẽ làm («tạo thêm một bài mới và đăng công khai ngay» khi đang chọn Đăng ngay).
- Trang **Cài đặt** có tab mới «📅 Hẹn giờ, đăng» để bật Hẹn giờ / Đăng ngay: mặc định tắt, phải tick «Tôi hiểu…» trước; công tắc chỉ có hiệu lực trong lần mở app đó (tắt app, tải lại trang là tự tắt). Chỉ bật sau buổi thử thật trên website.
- Việc so «giờ sửa bài» trên website ngay trước khi đăng (ai đó vừa sửa nháp trong trang quản trị thì không đăng) cần sửa phần kết nối WordPress: Thợ Máy làm ở phiếu T-115.

## 2. Việc đã làm

Mọi thay đổi ở `app/views/write.py` và test. Không sửa `seo_app/**`, `config/**`.

### 2.1 Một luật chung cho SL-T102-1 và LC-T102-1 (yêu cầu 1)

| Phần | Chỗ làm |
|---|---|
| Ảnh đại diện | `send_and_record` (`:3538`): bài có ảnh mà `DraftWithImages.featured_media` trống (lệnh đặt ảnh đại diện hỏng) thì `result["featured_missing"]` (`:3628`) |
| SEO | `write_seo` (`:2780`): `result["seo_ok"]` chỉ đúng khi client báo đã ghi (`written`) và, với Abilities, hỏi lại bài còn là nháp được (`:2807`); lỗi 5xx, website từ chối, SiteSEO chưa cho ghi, lỗi lạ đều là chưa ghi |
| Luật | `release_missing` (`:3761`) gom phần đã xác nhận mà chưa lên (chữ cố định). `release_post` (`:3687`): **Đăng ngay** thiếu phần nào thì **không** gọi `release_draft`; bài vẫn là nháp; nháp ghi «đã gửi nháp, chưa đăng» (`released=False`, `release_unknown=False`: không khóa «có thể đã gửi»); câu `MSG_PUBLISH_HELD` (`:359`) nêu phần chưa lên và mã bài. **Hẹn giờ** thiếu phần nào thì vẫn hẹn giờ, câu cảnh báo `MSG_SCHEDULE_MISSING` (`:363`) hiện dưới câu «Đã hẹn giờ» (`release_result`, `:4036`) |
| Test cũ | 4 ca `xfail(strict=True)` (3 SL-T102-1 trong `tests/test_soi_loi_t102.py`, 1 LC-T102-1 trong `tests/test_la_chan_t102.py`) qua với `--runxfail` rồi **gỡ dấu** (chỉ xóa dòng dấu; `import pytest` của `test_la_chan_t102.py` thành thừa nên bỏ theo). Phiếu đã cho phép gỡ |

**Vì sao Hẹn giờ chỉ cảnh báo (người dùng quyết):**

1. Bài hẹn giờ chưa công khai lúc gửi, còn thời gian sửa ảnh đại diện, SEO trong trang quản trị trước giờ đăng (tối thiểu 10 phút, thường là ngày hôm sau).
2. Nếu chặn như Đăng ngay, bài thành nháp mà app **không** hẹn giờ được nháp có từ trước (câu hỏi 5 chọn A). Bạn vẫn phải tự hẹn giờ trong trang quản trị, tức là không an toàn hơn mà thêm việc.
3. Đúng thiết kế T-094 (Hẹn giờ khi SEO chưa ghi → Cảnh báo) và gợi ý của Lá Chắn T-102.

Câu cảnh báo nói rõ phần chưa lên và việc cần làm: sửa trước giờ đăng, hoặc chuyển bài về nháp.

### 2.2 Dòng kế hoạch khi lệnh chuyển không rõ kết quả (yêu cầu 4, G1 Lá Chắn T-102)

`record_plan` (`:3649`): kết quả lệnh chuyển `unsure` (mà không phải `went_public`) thì **không ghi gì** vào dòng (không cả «Đã gửi nháp»), không để việc còn nợ, câu `MSG_PLAN_RELEASE_UNSURE` (`:367`) dặn kiểm bài trong trang quản trị rồi sửa ô «Trạng thái». Đăng ngay bị giữ là nháp vẫn ghi đúng «Đã gửi nháp».

### 2.3 Ô «gửi lại» đúng nghĩa (yêu cầu 5, Ghi nhận 2 Lá Chắn T-102)

`AGAIN_LABELS`, `AGAIN_NOTES` (`:373`): bài đã gửi, ô tick và câu nhắc theo hình thức đang chọn: Nháp giữ chữ cũ «Tạo thêm một bài nháp mới»; Hẹn giờ «Tạo thêm một bài mới và hẹn giờ đăng bài mới đó»; Đăng ngay «Tạo thêm một bài mới và đăng công khai ngay bài mới đó». Đổi hình thức thì ô bị bỏ tick (nhãn khác là ô khác), phải tick lại.

### 2.4 Xét lại công tắc lúc bấm (G2 Lá Chắn T-102)

`send_draft` (`:3329`, dòng `:3359`): hình thức Hẹn giờ/Đăng ngay mà công tắc đã tắt đúng lúc bấm (tab khác, Cài đặt) thì không gửi gì, câu `MSG_RELEASE_OFF_SEND` (`:355`).

## 3. Nút công tắc trong Cài đặt (yêu cầu 2): Chỉ Huy chọn A (31/10 09:55)

Cách lưu đã đề xuất, Chỉ Huy chọn **A: chỉ trong phiên** (Lá Chắn đầy đủ T-112 xác nhận lại). Phương án B (lưu trong `data/` trên máy) không chọn; `.env`, `config/` không đề xuất.

| Điều kiện | Chỗ làm |
|---|---|
| Có nút trong Cài đặt, mặc định tắt (LC-T094-41) | `app/views/settings.py`: tab mới **«📅 Hẹn giờ, đăng»** đặt **cuối** (thứ tự tab cũ giữ nguyên, test cũ tìm tab theo vị trí), hàm `release_tab` |
| Bật phải biết mình đang làm gì | Ô «Tôi hiểu: bài sẽ được hẹn giờ/đăng công khai thật trên website» (`release_ack`); chưa tick thì công tắc (`release_toggle`) khóa; bỏ tick là tắt luôn (`_release_ack_changed`) |
| Chỉ trong phiên, không file nào | Công tắc chỉ là khóa `_release_enabled` trong `st.session_state` (cùng khóa `RELEASE_SWITCH` bước Xuất bản đọc); ô và nút của trang chỉ chép sang khóa đó qua `on_change`, mỗi lần vẽ dựng lại theo khóa thật (Streamlit dọn ô khi sang trang khác). Không ghi nháp, `.env`, `config/`, `data/` |
| Không tham số địa chỉ, file nháp, ô nhập khác bật được | Không đọc `st.query_params`; nháp không mang công tắc (khuôn nháp chặt); không ô nào khác ghi khóa này |
| Bật/tắt có câu giải thích, nói rõ tắt app là tự tắt | Bật: cảnh báo «đang **bật** trong lần mở app này… Tắt app hay tải lại trang là công tắc tự tắt». Tắt: «đang **tắt** (mặc định)… Chỉ bật sau buổi thử thật… mỗi lần mở app, tải lại trang là tắt». Bước Xuất bản (công tắc tắt) chỉ chỗ bật: «Cài đặt → 📅 Hẹn giờ, đăng (tắt app là tự tắt)» |
| Xét lại lúc bấm gửi (G2) | `send_draft` (mục 2.4) |

Test: `tests/test_t112_settings_switch.py` (7 ca):

- mặc định tắt, chưa tick thì nút khóa;
- bật xong sang Soạn bài thấy Hẹn giờ, quay lại Cài đặt vẫn bật;
- bỏ tick là tắt;
- bước Xuất bản chỉ chỗ bật;
- phiên mới là tắt và không có `.env`;
- tham số địa chỉ không bật được;
- nháp sửa tay thêm khóa công tắc không bật được.

## 4. So `modified_gmt` trước lệnh chuyển (yêu cầu 3, LC-T094-23): **chuyển sang T-115**

Phải sửa `seo_app/wordpress/**`, nên Chỉ Huy giao Thợ Máy ở phiếu riêng **T-115** (31/10 09:55), đúng đề xuất:

- Client nhớ `modified_gmt` từ các lệnh ghi của chính nó (tạo nháp, đặt ảnh đại diện, ghi meta).
- Ngay trước lệnh chuyển, lệnh `GET` kiểm nháp so lại; khác thì `ReleaseError` (không `unsure`), bài vẫn là nháp.
- Phía app không đổi. T-115 xong thì gộp nhánh T-115 vào T-112 và thêm test giao diện.
- Cần kiểm khi thử thật: ghi SEO qua Abilities có làm đổi `modified_gmt` không.

## 5. Test

- `tests/test_t112_release_rules.py` (mới, 9 ca):
  - Đăng ngay thiếu cả hai phần: câu nêu đủ phần chưa lên, nháp không khóa «có thể đã gửi».
  - Chỉ thiếu SEO.
  - Đối chứng: đủ thì vẫn đăng.
  - Hẹn giờ thiếu ảnh đại diện: vẫn hẹn giờ và có cảnh báo; đủ thì không cảnh báo.
  - Dòng kế hoạch: không rõ kết quả thì không ghi gì; Đăng ngay bị giữ thì ghi «Đã gửi nháp».
  - Ô «gửi lại» theo hình thức.
  - Công tắc tắt đúng lúc bấm thì 0 request.
- `tests/test_t112_settings_switch.py` (mới, 7 ca): mục 3.
- Chạy chọn lọc (máy đang chạy toàn bộ test trên `main`):
  - lượt A: T-112, T-102 (`test_t102_publish`, `test_la_chan_t102`, `test_soi_loi_t102`, `test_t102_formula_cells`), `test_wordpress_release`, `test_app_pages`, `test_t101_plan_page`, `test_t101_home_page`: **390 qua, 0 hỏng**;
  - lượt B, sau khi có nút ở Cài đặt: 15 file test trang Cài đặt, T-112, T-102, và luồng gửi (`test_app_images`, `test_content_edge_cases`, `test_t086_send_state`, `test_t089_send_draft`, `test_la_chan_t089`, T-041 ×3): **1.171 qua, 6 bỏ qua, 0 hỏng**.
- Trình duyệt thật: chưa xem được tab mới (khung trình duyệt bị ẩn lúc thử); tab đã có 7 ca AppTest.
- `uv run ruff check .`: sạch. `tests/test_soi_loi_t102.py` vốn chưa định dạng theo `ruff format` từ trước; tôi chỉ xóa dòng dấu, không định dạng lại file của Soi Lỗi.

## 6. Không lùi

- **T-099:** `release_draft` vẫn chỉ ở `release_post`, lệnh cuối trên client của lần bấm (AST test `tests/test_wordpress_release.py`).
- **T-102:** toàn bộ test T-102 qua.
- **T-110:** không sửa các câu `MSG_SEND_UNEXPECTED`, `MSG_SEND_INTERRUPTED`, `unsure_message`, `GPS_PUBLIC_WARNING`.
- **«Gửi nháp», khóa gửi trùng:** không đổi; nhãn ô của Nháp giữ nguyên chữ cũ.

## 7. Commit

- `1a7bcf7` yêu cầu 1, 4, 5 và G2; gỡ 4 dấu `xfail`; test T-112.
- `6ef1a4c` công tắc ở Cài đặt (phương án A); câu «đang tắt» chỉ chỗ bật; test.

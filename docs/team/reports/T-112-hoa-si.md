# Báo cáo T-112 · Chuẩn bị bật Hẹn giờ / Đăng ngay (phần Họa Sĩ)

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | T-112 (Chỉ Huy B giao 31/10 09:40) |
| Ngày nộp | 2026-10-31 (lượt 2: 02/11; lượt 3: 03/11) |
| Nhánh | `team/T-112` (từ `d6df633`: `main` cục bộ `3cdd096` có T-102 + ghi chú `[plan]` của Ngòi Bút). Không gộp `main` |
| Kết quả | Xong yêu cầu 1, 2, 4, 5, 6 của phiếu; yêu cầu 3 (so `modified_gmt`) Chỉ Huy chuyển sang T-115 (Thợ Máy). Công tắc Hẹn giờ/Đăng ngay **vẫn mặc định tắt**, nay có nút ở Cài đặt (chỉ trong phiên, phương án A Chỉ Huy chọn). 16 ca test mới, gỡ 4 dấu `xfail` (SL-T102-1 ×3, LC-T102-1). **Lượt 2 (02/11):** gộp `main` và `team/T-115`, thêm 3 ca test giao diện cho đường «bài bị sửa ngoài app» của T-115 (mục 8). **Lượt 3 (03/11):** gộp `main` `33dd87f`; sửa SL-T112-1 (dòng Chặn ở màn hình xác nhận + chốt thứ hai ở `release_missing`), 7 ca test mới, gỡ 2 `xfail` SL-T112-1 và đổi 9 ca cũ theo R5 Chỉ Huy duyệt (mục 9); khuyến nghị «ghi dấu SEO chưa lên» của Lá Chắn chưa làm, nêu lý do (mục 9.5) |

## 1. Tóm tắt (cho chủ dự án)

- Công tắc Hẹn giờ / Đăng ngay **vẫn tắt** như trước. Phiếu này sửa những chỗ Lá Chắn và Soi Lỗi bắt buộc phải sửa trước khi bật:
  - **Đăng ngay** giờ chỉ đăng bài khi ảnh đại diện và SEO (nếu bạn bật «Ghi SEO lên website») đã lên website. Một trong hai bị lỗi lúc gửi thì bài **vẫn là nháp**, app nói rõ phần nào chưa lên; bạn sửa trong trang quản trị rồi tự bấm «Đăng» ở đó.
  - **Hẹn giờ** vẫn hẹn giờ khi thiếu một phần, nhưng báo rõ phần chưa lên để bạn sửa trước giờ đăng (hoặc chuyển bài về nháp).
  - Lệnh hẹn giờ/đăng không rõ kết quả (mất mạng đúng lúc): app không ghi gì vào dòng kế hoạch trên Google Sheet, để Sheet không nói sai «nháp».
  - Bài đã gửi mà bạn muốn gửi thêm một bài nữa: ô tick nói đúng việc sẽ làm («tạo thêm một bài mới và đăng công khai ngay» khi đang chọn Đăng ngay).
- Trang **Cài đặt** có tab mới «📅 Hẹn giờ, đăng» để bật Hẹn giờ / Đăng ngay: mặc định tắt, phải tick «Tôi hiểu…» trước; công tắc chỉ có hiệu lực trong lần mở app đó (tắt app, tải lại trang là tự tắt). Chỉ bật sau buổi thử thật trên website.
- Việc so «giờ sửa bài» trên website ngay trước khi đăng (ai đó vừa sửa nháp trong trang quản trị thì không đăng) cần sửa phần kết nối WordPress: Thợ Máy làm ở phiếu T-115.
- **Lượt 3:** bật «Ghi SEO lên website» mà tiêu đề hay mô tả SEO đang trống hoặc bị «Chặn» ở bước SEO thì **Đăng ngay bị khóa nút** ngay ở màn hình xác nhận, kèm dòng nói rõ trường nào (trước đây bài vẫn lên công khai với tiêu đề, mô tả SEO mặc định). **Hẹn giờ** thì chỉ cảnh báo, vì còn sửa được trước giờ đăng.

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

- `tests/test_t112_release_rules.py` (mới, 9 ca ở lượt 1; lượt 2 thêm 4 ca, mục 8):
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
- `f598cef` báo cáo lượt 1.

## 8. Lượt 2 (Chỉ Huy B giao 02/11 17:50): gộp `main`, `team/T-115`; test giao diện cho T-115

### 8.1 Gộp

- Đầu nhánh lúc nhận việc: `245e199` (có thêm README bước Xuất bản của Thư Ký).
- `git merge origin/main`: lúc chạy `origin/main` đã là `7485b94`, mới hơn `935d381` anh ghi; phần thêm chỉ là tài liệu điều phối (`board.md`, `dong-bo.md`, phiếu). Có T-110 lượt 2–3, T-113, T-105. Commit gộp `5445028`, không xung đột.
- `git merge origin/team/T-115` (`a7572f7`): commit gộp `ff420d4`, không xung đột. Dấu `xfail` LC-T102-1 hai bên gỡ y hệt. `write.py` không đụng nhau: T-115 không sửa `app/**`.
- `uv sync` (`uv.lock` của `main` đổi).

### 8.2 Test giao diện cho đường `ReleaseError` của T-115

T-115 (client): lệnh kiểm nháp ngay trước lệnh chuyển so `modified_gmt` với giá trị website trả ở lần ghi cuối của chính client. Khác, thiếu hay «không biết» thì `ReleaseError(_RELEASE_CHANGED)`: không `unsure`, không gửi lệnh chuyển.

App không cần sửa: T-102 đã có sẵn đường hiện `ReleaseError` «bài vẫn là nháp». `tests/test_t112_release_rules.py`, mục «T-115», 3 ca, công tắc bật trong test:

| Ca | Kiểm |
|---|---|
| `test_post_edited_outside_after_last_write_is_not_released[Hẹn giờ]`, `[Đăng ngay]` | Lệnh kiểm nháp (`_fields=id,status,modified_gmt`) thấy giờ sửa mới hơn, như có người vừa «Lưu nháp» trong trang quản trị. Kết quả: không lệnh chuyển nào; câu cố định của client hiện bằng cảnh báo, không có lời máy chủ; bài vẫn là nháp; nháp ghi «đã gửi nháp, chưa hẹn giờ/đăng» (`released`, `release_unknown`, `pending` đều tắt), **không** khóa «có thể đã gửi»; mở lại vẫn vậy |
| `test_post_edited_outside_plan_row_gets_no_release_status` | Dòng kế hoạch **không** mang trạng thái chuyển («Đã hẹn giờ», «Đã đăng»). Bài thật sự vẫn là nháp nên dòng ghi đúng «Đã gửi nháp» kèm Mã bài WordPress |

**Dòng kế hoạch ở ca này: Chỉ Huy B giữ cách hiện có (02/11 19:00), Lá Chắn đầy đủ xét lại.**

- G1 (Lá Chắn T-102) chỉ áp cho lệnh chuyển **không rõ** kết quả: lúc đó bài có thể đã công khai mà Sheet lại nói «nháp», nên app không ghi gì.
- Ở đường T-115 thì kết quả **rõ**: website từ chối lệnh chuyển, bài **chắc chắn** vẫn là nháp đã có trên website (có mã bài).
- Vì vậy dòng ghi «Đã gửi nháp» kèm Mã bài WordPress, đúng sự thật, và không ghi trạng thái chuyển («Đã hẹn giờ», «Đã đăng»).
- Không ghi gì thì dòng còn «Đang viết» và mất mã bài, tức là sai hơn.

**T-115 làm luật Hẹn giờ chặt hơn ở một chỗ.** Lệnh đặt ảnh đại diện lỗi (500) thì client «không biết chắc» bài có bị sửa không (SL-T115-1), nên từ chối lệnh chuyển. Vì vậy với lỗi ảnh đại diện, Hẹn giờ cũng không còn «vẫn hẹn giờ, cảnh báo» như T-112 lượt 1 (mục 2.1): bài vẫn là nháp, câu cố định của client, không khóa «có thể đã gửi».

- Ca test `test_schedule_goes_on_but_warns_what_is_missing` của tôi (T-112, chưa lên `main`) đổi sang lỗi **SEO**: client không biết lỗi ghi SEO nên vẫn hẹn giờ, app cảnh báo phần SEO.
- Thêm ca `test_schedule_with_featured_failure_is_refused_by_client` cho lỗi ảnh đại diện.
- Lượt chạy chọn lọc đầu tiên sau khi gộp bị ngắt giữa chừng (phiên dừng) đã bắt đúng ca này hỏng; nay qua.

### 8.3 Test lượt 2

Chạy chọn lọc trên nhánh đã gộp, 20 file:

- T-112: `test_t112_release_rules` (13 ca), `test_t112_settings_switch`;
- T-102: `test_t102_publish`, `test_la_chan_t102`, `test_soi_loi_t102`, `test_t102_formula_cells`;
- T-110: `test_la_chan_t110`, `test_soi_loi_t110`, `test_t110_gan_anh_vao_bai_nhap`;
- T-115: `test_t115_modified_gmt`, `test_soi_loi_t115`;
- `test_wordpress_release`, `test_app_pages`;
- luồng gửi: `test_app_images`, `test_content_edge_cases`, `test_t086_send_state`, `test_t089_send_draft`, `test_la_chan_t089`, `test_t041_seo_ui`, `test_soi_loi_t041`.

Kết quả: **1.193 qua, 0 hỏng**. `ruff check .` sạch.

### 8.4 Commit lượt 2

- `5445028` gộp `main` `7485b94`; `ff420d4` gộp `team/T-115` `a7572f7`; `a1edee0` test giao diện T-115; `ac85c1b` test Hẹn giờ theo hành vi sau T-115; commit cuối: báo cáo mục 8.

## 9. Lượt 3 (Chỉ Huy B giao 03/11 12:50): SL-T112-1, khuyến nghị Lá Chắn

### 9.1 Gộp

- Đầu nhánh lúc nhận việc: `7e8af87` (báo cáo Soi Lỗi `b4f7900`, Lá Chắn đầy đủ `7e8af87`).
- `git merge origin/main` (`33dd87f`: T-115, T-117, T-119, biên bản T-116): commit gộp `df4ba4a`, không xung đột. `uv.lock` không đổi (`pyproject.toml` chỉ đổi chú thích `required-version`).

### 9.2 SL-T112-1: Đăng ngay khi tiêu đề hay mô tả SEO trống hoặc «Chặn»

Cơ chế lỗi (Soi Lỗi, Lá Chắn): bật «Ghi SEO» mà tiêu đề hay mô tả SEO đang «Chặn» ở bước SEO thì `seo_request` bỏ trường đó (chuỗi rỗng). Client ghi phần còn lại vẫn báo `written=True`, nên `release_missing` coi SEO đã lên và Đăng ngay vẫn đăng công khai với tiêu đề, mô tả SEO mặc định.

Sửa ở `app/views/write.py`, hai chốt. Không sửa bộ dựng `seo_app/publish/render.py` (Lá Chắn gợi ý đặt dòng Chặn ở đó, nhưng file này ngoài phạm vi của tôi; kết quả trên màn hình như nhau).

| Chốt | Chỗ làm |
|---|---|
| 1. Dòng **Chặn** ở màn hình xác nhận | `seo_left_out(seo)`: tiêu đề, mô tả SEO **trong gói sẽ gửi** (`built.seo`, cùng mã băm với ô tick) trống khi bật «Ghi SEO». `seo_notices(seo, mode)`: Đăng ngay là `Notice(BLOCK)` (`MSG_PUBLISH_SEO_LEFT_OUT`, nêu đúng trường), Hẹn giờ là `Notice(WARN)` (`MSG_SCHEDULE_SEO_LEFT_OUT`), Nháp thì không. `publish_panel` thêm vào `notices` ngay trước `review_panel`: dòng hiện cùng chỗ các dòng Chặn khác. `allowed` tắt nên nút khóa; cú bấm lọt qua nút khóa (bấm đúp) cũng bị `if clicked and allowed` chặn |
| 2. `release_missing` | SEO ghi được (`seo_ok`) mà lệnh ghi đã bỏ tiêu đề hay mô tả (`holder["seo"]["fields"]` trống) thì vẫn là «chưa lên», nêu đúng tên trường (`MISSING_SEO_FIELDS`: «tiêu đề SEO», «mô tả SEO»). Đăng ngay giữ nháp (`MSG_PUBLISH_HELD`), Hẹn giờ cảnh báo (`MSG_SCHEDULE_MISSING`) |

- Từ khóa chính bị bỏ (ký tự lạ, quá dài): **không** Chặn, không tính là thiếu. Lá Chắn: từ khóa chính không hiện công khai; bước SEO và chú thích dưới công tắc đã báo.
- Tắt «Ghi SEO»: giữ luật cũ của bộ dựng (Đăng ngay là Chặn, Hẹn giờ cảnh báo).
- Chốt 2 không tới được qua giao diện khi chốt 1 còn đứng: gói và lệnh ghi dùng cùng chữ SEO, mã băm khóa. Đây là chốt phòng hờ, có test qua đường Hẹn giờ (cùng hàm).

### 9.3 Đổi test cũ (R5): Chỉ Huy duyệt 03/11 12:45, (a)/(b)

Vì sao phải đổi:

1. 2 ca `xfail` SL-T112-1 không thể XPASS nguyên văn. `send_publish` của Soi Lỗi kiểm nút **mở** rồi mới bấm, mà sửa đúng thì nút **khóa** (chạy `--runxfail`: hỏng đúng ở `assert not send_button(at).disabled`).
2. Bài mẫu của test chưa có chữ SEO. Mọi ca cũ «Đăng ngay + bật Ghi SEO» nay bị khóa nút ở màn hình xác nhận. Lô chạy code mới với test cũ: 13 hỏng, đều thuộc loại này (7 ca cũ, 6 ca T-112 của tôi), 83 qua.

| Ca | Cũ | Mới | Duyệt |
|---|---|---|---|
| `test_soi_loi_t112::test_sl_t112_1_dang_ngay_khi_truong_seo_dang_chan_thi_khong_dang` `[tieu-de-chan]`, `[mo-ta-chan]` | `xfail` strict; `send_publish` kiểm nút mở, bấm; chờ lệnh ghi SEO có trường Chặn để trống, không lệnh đăng, nháp «chưa đăng» | Gỡ `xfail`, thêm docstring. Tick xác nhận → có dòng Chặn nêu đúng trường + nút khóa → cú bấm lọt vẫn không gửi gì: không lệnh ghi SEO (`calls == []`), không lệnh ghi nào (mọi yêu cầu là `GET`), `release_bodies == []`, nháp không có trạng thái gửi (`load_send_state` là `None`). Ý «trường Chặn không ghi, phần còn lại vẫn ghi» giữ ở ca Hẹn giờ mới của tôi (mục 9.4) | (b) |
| `test_t102_publish::test_publish_now_with_seo_written` | Bài mẫu chưa có chữ SEO | +4 dòng `session_state` (tiêu đề, mô tả SEO hợp lệ, như `send_publish` của Soi Lỗi) trước khi chọn Đăng ngay; mọi kiểm giữ nguyên | (a) |
| `test_la_chan_t102::_publish_now` (3 ca LC-T102-1) | như trên | như trên | (a) |
| `test_soi_loi_t102::test_sl_t102_1_dang_ngay_ma_seo_ghi_hong_thi_khong_dang` (3 ca) | như trên | như trên: lại đi tới lệnh ghi SEO, giữ đúng ý «ghi SEO lỗi thì không đăng» | (a) |
| `test_soi_loi_t102::test_sua_sau_khi_tick_thi_bo_tick` `[tieu-de]`, `[slug]` | như trên; sau sửa vẫn qua nhưng nút đã khóa sẵn vì dòng Chặn, nên kiểm «nút khóa» mất ý | như trên: nút khóa lại là do bỏ tick | (a), ca cùng loại tôi tìm ra khi đọc (không hỏng) |

- AppTest không cho bấm nút đang khóa (`AppTestError: Cannot update a disabled button widget`). Nên «cú bấm lọt» giả bằng `st.button` trả «đã bấm» cho nút `wp-send`, như ca G2 có sẵn (`test_switch_turned_off_at_click_sends_nothing`). Cách này đi đúng nhánh `if clicked and allowed` của trang.
- Ca của tôi (T-112, chưa lên `main`): `send(…, seo_write=True)` và `test_held_publish_writes_draft_sent_to_plan` nay đặt chữ SEO hợp lệ (`seo_texts`). Ý các ca giữ nguyên: SEO có chữ, lệnh ghi hỏng hay được.
- `ruff format --check` báo 3 file test cũ (`test_soi_loi_t102`, `test_soi_loi_t112`, `test_t102_publish`) có đoạn chưa đúng khuôn **từ trước**, không phải dòng tôi thêm: để nguyên.

### 9.4 Ca test mới (7, `tests/test_t112_release_rules.py`, mục «SL-T112-1»)

| Ca | Kiểm |
|---|---|
| `test_publish_blocked_when_seo_field_left_out` `[tieu-de-chan]`, `[mo-ta-chan]`, `[tieu-de-trong]`, `[mo-ta-trong]` | Đăng ngay: dòng Chặn nêu đúng trường, nút khóa dù đã tick; cú bấm lọt: không lệnh ghi nào, không lệnh ghi SEO, nháp không có trạng thái gửi |
| `test_publish_names_both_seo_fields_left_out` | Cả hai trường: một dòng Chặn nêu «tiêu đề SEO, mô tả SEO» |
| `test_schedule_with_seo_field_left_out_warns_and_goes_on` | Hẹn giờ: màn hình xác nhận chỉ cảnh báo (không Chặn); gửi thì ghi phần SEO còn lại (tiêu đề trống, mô tả đủ), vẫn hẹn giờ đúng giờ; kết quả cảnh báo «Bài đã hẹn giờ nhưng tiêu đề SEO chưa lên website lúc gửi» (chốt 2, client báo đã ghi một phần) |
| `test_publish_goes_when_only_focus_keyword_left_out` | Từ khóa chính có ký tự riêng (bước SEO báo «Chặn», lệnh ghi bỏ): Đăng ngay vẫn đăng, không chặn oan |

### 9.5 Khuyến nghị Lá Chắn (ghi dấu «SEO chưa lên» khi Hẹn giờ): chưa làm, không nhỏ trong phạm vi

- Ghi vào nháp: `SendState` (`seo_app/storage/drafts.py`) không có trường nào cho việc này, khuôn chặt. Thêm trường là việc của kho nháp (Thợ Máy); sau đó trang Bài viết mới nhắc được.
- Ghi vào dòng kế hoạch: chỉ có ô «Ghi chú của thợ», là chữ của người dùng. App chỉ được ghi 4 ô qua `record_status` (LC-T094-40); ghi ô ghi chú là đè chữ của thợ và phải đổi `seo_app/plan/`.
- Đề xuất phiếu sau: `SendState.seo_missing` (Thợ Máy), dòng nhắc ở bước Xuất bản và trang Bài viết (Họa Sĩ).
- Hiện tại cảnh báo hiện ở kết quả gửi, và từ lượt này hiện cả ở màn hình xác nhận trước khi bấm Hẹn giờ (dòng Cảnh báo, mục 9.2).

### 9.6 README (để Thư Ký làm cùng SL-T112-2, -3)

Tôi không sửa README. Mục 11 nên thêm một ý: bật «Ghi SEO» mà tiêu đề hay mô tả SEO trống hoặc «Chặn» thì Đăng ngay bị Chặn ở màn hình xác nhận (nút khóa), Hẹn giờ chỉ cảnh báo, từ khóa chính bị bỏ thì không chặn.

### 9.7 Test lượt 3

- Lô 1, 5 file bước Xuất bản (`test_t102_publish`, `test_la_chan_t102`, `test_soi_loi_t102`, `test_t112_release_rules`, `test_soi_loi_t112`): **105 qua, 2 xfail** (SL-T112-2, -3: README, của Thư Ký), 0 hỏng, 0 XPASS; 8 phút 48.
- Lô 2, 16 file (T-112 `test_t112_settings_switch`; T-102 `test_t102_formula_cells`; T-110 `test_la_chan_t110`, `test_soi_loi_t110`, `test_t110_gan_anh_vao_bai_nhap`; T-115 `test_t115_modified_gmt`, `test_soi_loi_t115`; `test_wordpress_release`, `test_app_pages`; luồng gửi `test_app_images`, `test_content_edge_cases`, `test_t086_send_state`, `test_t089_send_draft`, `test_la_chan_t089`, `test_t041_seo_ui`, `test_soi_loi_t041`): **1.111 qua, 0 hỏng**; 15 phút 05.
- Cộng hai lô: **1.216 qua, 2 xfail, 0 hỏng, 0 XPASS**.
- `ruff check` 6 file đổi: sạch.
- `detect-secrets` (`PYTHONUTF8=1`): file mồi tiếng Việt bắt được, đã xóa. Báo 1 chỗ có từ trước (`write.py`, docstring ví dụ `tên:mật-khẩu@` của T-041), không có gì mới.

### 9.8 Commit lượt 3

- `df4ba4a` gộp `main` `33dd87f`; `58d5326` sửa SL-T112-1 + test (gồm R5); commit cuối: báo cáo mục 9.

# Báo cáo T-112 (phần Thư Ký) · README: Nháp, Hẹn giờ, Đăng ngay ở bước Xuất bản

| Mục | Nội dung |
|---|---|
| Agent | Thư Ký (`thu-ky`) · model: Claude Opus 5.5 |
| Phiếu | T-112 «Chuẩn bị bật Hẹn giờ / Đăng ngay» (phần Thư Ký; Chỉ Huy B giao 31/10 11:00) |
| Nhánh | `team/T-112` (đầu `f598cef`, phần Họa Sĩ) |
| Ngày nộp | 2026-10-31 11:20 (+07:00, theo lệnh `date`) |
| Kết quả | Hoàn thành yêu cầu 1–5 của tin giao việc. Chỉ sửa `README.md` |

## Tóm tắt (cho chủ dự án)

- Mục 11 README đổi tên thành «Gửi bài lên WordPress: Nháp, Hẹn giờ, Đăng ngay». Mục này có:
  - bảng ba cách gửi;
  - khối «**Hẹn giờ và Đăng ngay hiện đang tắt**», cách bật ở **Cài đặt → 📅 Hẹn giờ, đăng**. Công tắc chỉ giữ trong lần mở app: tải lại trang hay tắt app là tự tắt;
  - phần gửi Nháp (thêm chọn chuyên mục, khung xem lại link);
  - phần Hẹn giờ, Đăng ngay khi đã bật: giờ điền sẵn, màn hình xác nhận, sửa bài thì phải tick lại;
  - luật «Đăng ngay chỉ đăng khi ảnh đại diện và SEO đã lên; Hẹn giờ thì vẫn hẹn nhưng cảnh báo»;
  - kết quả không rõ thì app khóa gửi lại, kèm 3 bước kiểm bài trên trang quản trị WordPress.
- README ghi rõ Hẹn giờ, Đăng ngay **chưa thử trên website thật**, sẽ thử cùng anh/chị trước khi dùng.
- Sửa thêm vài câu README đã cũ sau T-102 và T-110 (cùng chủ đề gửi bài):
  - bài nháp nay đã có link nội bộ, đường dẫn, chuyên mục, định dạng;
  - ảnh gắn vào bài nháp nên không hiện trong danh sách Media công khai trước khi bài đăng.

## Đã thay đổi

| Chỗ (`README.md`) | Thay đổi |
|---|---|
| `:7` (Trạng thái) | Thêm «Hẹn giờ, Đăng ngay đã làm nhưng đang tắt, chờ thử thật» |
| `:135` (mục 7) | «Hai cách Hẹn giờ, Đăng ngay vẫn là bản demo» → «đã làm nhưng đang tắt, chờ thử thật trên website (mục 11)» |
| `:201` (7.4 bước 6) | Thêm «Hẹn giờ, Đăng ngay hiện đang tắt (mục 11)» |
| `:381` (mục 10, Chép sang SiteSEO) | Bỏ «đường dẫn dán vào ô đường dẫn (slug) của bài»: app đã gửi đường dẫn kèm bài (T-102), khung để xem hay sửa tay |
| `:392` (mục 10, Liên kết nội bộ) | «App chưa chèn các liên kết này… (làm ở Giai đoạn 5)» → app chèn link các dòng còn tick «Dùng», tải lại danh sách bài ngay trước khi gửi |
| `:403`, `:406` (mục 10, Ghi SEO lên website) | Công tắc nằm phía trên nút gửi (mọi hình thức), Đăng ngay bắt buộc bật; «Đường dẫn, liên kết nội bộ, schema không ghi» → «Schema không ghi; đường dẫn, liên kết nội bộ đi cùng bài» |
| `:423` (mục 11, tiêu đề) | «Gửi bài nháp lên WordPress» → «Gửi bài lên WordPress: Nháp, Hẹn giờ, Đăng ngay» (số mục giữ 11) |
| `:425-439` (mới) | Bảng 3 hình thức và nút gửi; khối «Hẹn giờ và Đăng ngay hiện đang tắt», 3 bước bật ở Cài đặt (tick «Tôi hiểu…», bật công tắc; chỉ giữ trong lần mở app, không lưu file); công tắc tắt đúng lúc bấm thì không gửi gì |
| `:441-451` (Gửi dạng Nháp) | Thêm bước chuyên mục («🔄 Tải chuyên mục từ website») và khung «Xem lại link, địa chỉ trong bài»; đánh lại số bước 1–7 |
| `:453-462` (mới) | Hẹn giờ (ô Ngày đăng, Giờ đăng; giờ mặc định `[plan] default_time`, sai hay thiếu thì 08:00; dòng kế hoạch; 10 phút, một năm), Đăng ngay (bắt buộc ghi SEO), quyền đăng bài, múi giờ, màn hình xác nhận, tick lại khi sửa, thứ tự app làm |
| `:464-467` (mới) | Đăng ngay thiếu ảnh đại diện hay SEO thì giữ nháp (câu `MSG_PUBLISH_HELD`); Hẹn giờ vẫn hẹn, cảnh báo (câu `MSG_SCHEDULE_MISSING`) và lý do (theo báo cáo Họa Sĩ mục 2.1) |
| `:469-474` (mới) | Kết quả: xong, website từ chối, KHẨN (hẹn giờ mà đăng ngay), không rõ thì khóa gửi lại; dòng kế hoạch không ghi khi không rõ |
| `:476-480` (mới) | Kiểm bài trên trang quản trị: mở theo dòng «Sửa bài trong trang quản trị: …» hay Bài viết → Tất cả bài viết; xem trạng thái; đúng ý thì đừng gửi lại |
| `:484-488` (Cần biết khi gửi) | «Chỉ tạo bài nháp» → «Nháp không bao giờ tự đăng» + điều kiện Hẹn giờ/Đăng ngay. Ảnh: theo câu `GPS_PUBLIC_WARNING` hiện tại (T-110: gắn vào bài nháp, không hiện trong danh sách Media công khai trước khi bài đăng). Bài gửi đi gồm gì (định dạng, link nội bộ, slug, chuyên mục; thẻ, schema chưa gửi). Tải lại danh sách bài trước khi gửi |
| `:493` (Khi có lỗi) | Thêm ca «Bài vừa thay đổi sau khi bạn xem lại … Chưa gửi gì lên website» |
| `:500` (App nhớ việc đã gửi) | Câu «đã gửi» theo hình thức; ô gửi lại theo hình thức (3 nhãn `AGAIN_LABELS`); đổi hình thức thì bỏ tick |

Không đổi số mục (## 1 … ## 13). Không sửa code, `config/`, file phiếu.

## Đối chiếu với code (nhánh `team/T-112`, `f598cef`)

**Câu trích.** 49 câu trích, tên nút, nhãn ô trong phần mới đều có trong `app/`, `seo_app/`, `config/`. Kiểm bằng script Python đọc UTF-8, có nối chuỗi Python viết tách dòng: «thiếu: 0».

**Hành vi README mô tả.**

| README nói | Code |
|---|---|
| Ba hình thức, nhãn nút | `MODE_LABELS` `app/views/write.py:287-288`; `send_label` `:3086-3095` |
| Tắt thì chỉ có câu giải thích, không nút gửi | `publish_panel` `:4068-4071` (`MSG_RELEASE_OFF` `:296-301`) |
| Bật ở Cài đặt, phải tick «Tôi hiểu…», chỉ trong phiên, bỏ tick là tắt | `app/views/settings.py` `release_tab` (`MSG_RELEASE_ON` `:706-710`, `MSG_RELEASE_OFF_HERE` `:711-715`); tab «📅 Hẹn giờ, đăng» `:788`; báo cáo Họa Sĩ mục 3 |
| Công tắc tắt đúng lúc bấm: không gửi gì | `MSG_RELEASE_OFF_SEND` `write.py:356-359`; `send_draft` (báo cáo Họa Sĩ mục 2.4) |
| Chuyên mục | `category_picker` `write.py:2920-2945` |
| Ngày mai, giờ mặc định `[plan] default_time`, 08:00 khi sai | `schedule_picker` `:2883-2903`, `default_publish_time` `:2869-2880`, `DEFAULT_PUBLISH_TIME` `:294`; `config/content.toml:174-183` |
| Ngày, giờ từ dòng kế hoạch | `write.py:750-753` |
| Đã qua, < 10 phút, > 1 năm: Chặn | `seo_app/publish/schedule.py:48-53` (`MSG_PAST`, `MSG_TOO_SOON`, `MSG_TOO_FAR`) |
| Đăng ngay bắt buộc ghi SEO; Hẹn giờ nhắc chép SEO | `seo_app/publish/render.py:628-641` |
| Quyền đăng bài, múi giờ | `connection_info` `write.py:2906-2917`, `MSG_NO_PUBLISH_RIGHT` `:314-317`; `timezone_warning` `seo_app/wordpress/client.py:663-680` |
| Màn hình xác nhận, ô tick, bỏ tick khi đổi | `review_header` `write.py:3228-3258`, `confirm_box` `:3103-3115`, `MSG_CONFIRM_RESET` `:306-308` |
| Đăng ngay thiếu phần nào thì giữ nháp; Hẹn giờ vẫn hẹn và cảnh báo | `release_post` `:3688-3759`, `release_missing` `:3762-3771`, `MSG_PUBLISH_HELD` `:360-363`, `MSG_SCHEDULE_MISSING` `:364-367`, `release_result` `:4037-4055` |
| Không rõ kết quả: khóa, câu khi mở lại, ô «Tôi đã kiểm tra…» | `ReleaseError` (`_RELEASE_UNSURE` `client.py:591-595`), `MSG_RELEASE_UNSURE_LOCK` `write.py:389-393`, `unsure_message` `:3920-3938`, `publish_panel` (`locked` khi `release_unknown`) |
| KHẨN: hẹn giờ mà website đăng ngay | `_RELEASE_WENT_PUBLIC` `client.py:605-609` |
| Dòng kế hoạch không ghi khi không rõ | `record_plan` `write.py:3650-3662`, `MSG_PLAN_RELEASE_UNSURE` `:368-371` |
| Câu «đã gửi» theo hình thức, ô gửi lại 3 nhãn | `sent_message` `:3941-3959`, `AGAIN_LABELS`, `AGAIN_NOTES` `:374-388` |
| Bài gửi đi gồm định dạng, link nội bộ «Dùng», slug, chuyên mục; thẻ, schema chưa | `build_package` `:3020-3053` (`chosen_links` `:2958-2960`); `review_header` («Thẻ: không có»); `seo_use_faq` chỉ ở bước SEO và nháp |
| Tải lại danh sách bài trước khi gửi khi có link | `package_index` `:2968-2984`, `MSG_NO_LISTING` `:309-312` |
| Ảnh: công khai qua đường dẫn trực tiếp, không hiện trong danh sách Media trước khi đăng | `GPS_PUBLIC_WARNING` `:279-284` (T-110 lượt 1) |
| Bài đổi đúng lúc bấm | `MSG_CONFIRM_CHANGED` `:302-305` |

## Kiểm tra

```
# Dẫn chiếu «mục N» sau khi sửa: 6, 7, 7.1, 7.2, 7.5, 8, 9, 10, 11 — đều là mục có thật;
# số mục không đổi (## 1 … ## 13). README không có link neo `](#…)` (đếm: 0).

$ uv --version            # quy tắc T-078: kiểm trước khi chạy uvx
uv 0.13.4 (…)
$ PYTHONUTF8=1 uvx detect-secrets scan README.md docs/team/reports/T-112-thu-ky.md
  "results": {}
```

Không chạy pytest, ruff: chỉ đổi `README.md` và báo cáo.

## Rủi ro và điểm cần chú ý

- **Phần Hẹn giờ, Đăng ngay viết theo code và test, chưa xem trên website thật** (công tắc tắt; thử thật LC-T094-44 chưa làm). Sau buổi thử thật nên đọc lại mục 11, nhất là chữ trên màn hình xác nhận và câu kết quả.
- **T-115 (so `modified_gmt` trước lệnh chuyển) chưa gộp.** Khi gộp sẽ có thêm ca «bài trên website đổi sau lần xác nhận thì không chuyển». README chưa nhắc ca này. Câu «Website từ chối rõ ràng (…)» đã đủ chung để không sai.
- **Tên trạng thái bài trong trang quản trị** (bản nháp, lên lịch, xuất bản) viết theo nghĩa, kèm tên tiếng Anh. Tôi chưa đối chiếu chữ tiếng Việt chính xác trên trang quản trị thật.
- **Câu ảnh công khai** theo `GPS_PUBLIC_WARNING` sau T-110 lượt 1. T-110 lượt 2 (đang làm) có thể đổi chi tiết «gắn không được thì app báo». Khi gộp nên đối chiếu lại.
- Những câu tôi sửa ngoài phần Hẹn giờ/Đăng ngay (mục 10: link nội bộ, slug; mục 11: ảnh, nội dung bài gửi đi) là câu đã sai sau T-102, T-110 (đã gộp `main`). Chúng nằm trong mục gửi bài nên tôi sửa luôn. Lá Chắn nên đọc cùng.

## Câu hỏi cho chủ dự án

Không có.

## Lượt 2 (2026-11-03 13:18, +07:00)

Theo tin Chỉ Huy B 03/11, sau Soi Lỗi (`T-112-soi-loi.md`), Lá Chắn Fable (`T-112-la-chan.md`, `T-116-la-chan-nhom-2.md`), T-115 đã gộp và lượt 3 của Họa Sĩ (SL-T112-1). Nhánh từ `3f29c74`. Chỉ sửa `README.md`, cộng gỡ 3 dấu `xfail` ghim README (chỉ xóa dòng dấu, theo tin giao việc).

### Tóm tắt (cho chủ dự án)

- **Công tắc Hẹn giờ / Đăng ngay theo từng tab.** Mỗi tab trình duyệt có công tắc riêng: bật ở tab này không bật tab khác, tắt ở tab khác không tắt tab này. Xong việc thì tắt ở chính tab đã bật hoặc tải lại trang tab đó. Trước đây README nói ngược.
- **Hẹn giờ khi ảnh đại diện chưa lên:** app **không** hẹn giờ, bài vẫn là nháp. Chỉ khi thiếu SEO thì app vẫn hẹn giờ và cảnh báo.
- **Bài bị sửa trong trang quản trị** (hay do plugin, người khác) sau lần app ghi cuối: app không hẹn giờ, không đăng, bài vẫn là nháp. README dặn hai cách làm tiếp: tự hẹn giờ/đăng trong trang quản trị, hoặc gửi lại từ app rồi xóa bài nháp cũ.
- **Đăng ngay khi tiêu đề hay mô tả SEO trống hoặc «Chặn»:** nút gửi khóa ngay ở màn hình xác nhận, phải sửa ở bước SEO trước. Hẹn giờ thì chỉ cảnh báo.
- Dòng Trạng thái đầu README: trang Kết nối WordPress nay chỉ «tạo thử bài nháp chữ», không còn ảnh.

### Đã thay đổi

| Lỗi / việc | Chỗ (`README.md`) | Thay đổi |
|---|---|---|
| SL-T112-3 | `:457-460` | Bước 3: công tắc «chỉ giữ trong tab trình duyệt đó, trong lần mở app đó». Bước 4 mới: «**Mỗi tab trình duyệt có công tắc riêng**: bật ở tab này không bật tab khác (tab mới mở luôn tắt), và tắt ở tab khác **không** tắt tab này. Xong việc thì tắt ở chính tab đã bật, hoặc tải lại trang tab đó.» Câu «Công tắc bị tắt (ví dụ ở tab khác)…» → «Công tắc bị tắt (ở Cài đặt của cùng tab, hay tải lại trang) thì bước Xuất bản chỉ còn gửi Nháp; một lần bấm … lỡ lọt sau lúc tắt cũng không gửi gì…» |
| SL-T112-3 (cùng loại) | `:482` | Bỏ «(kể cả ở tab khác)» ở dòng «Sửa gì sau khi tick thì phải tick lại» (công tắc «Ghi SEO» cũng chỉ trong phiên) |
| SL-T112-1 (lượt 3 Họa Sĩ) | `:478`, `:479` | Hẹn giờ: bật «Ghi SEO» mà tiêu đề/mô tả SEO trống hay «Chặn» → cảnh báo «Hẹn giờ mà … sẽ không ghi lên website…», vẫn gửi được. Đăng ngay: cùng ca → dòng Chặn «Đăng ngay mà … sẽ không ghi lên website (đang trống hoặc báo «Chặn» ở bước SEO)…», nút khóa, sửa ở bước SEO trước; chỉ từ khóa chính có vấn đề thì không chặn |
| SL-T112-2 | `:488` | «**Hẹn giờ thì vẫn hẹn**» → «**Hẹn giờ thì vẫn hẹn khi chỉ thiếu SEO**» (giữ lý do); thêm: «Riêng **ảnh đại diện** chưa lên… app **không hẹn giờ**… bài vẫn là nháp, báo «… Chưa hẹn giờ, chưa đăng: bài vẫn là nháp…»» |
| Ca T-115 (G1 Soi Lỗi) | `:493-494` | Gạch mới «**Bài bị sửa ngoài app:**»: app hỏi lại giờ sửa bài ngay trước khi hẹn giờ/đăng; bị sửa sau lần app ghi cuối (hay không biết chắc, ví dụ ảnh đại diện vừa lỗi) thì không hẹn giờ/đăng, câu `_RELEASE_CHANGED` trích đủ; cách làm tiếp (a) tự làm trong trang quản trị, (b) gửi lại từ app (tạo thêm bài mới) rồi xóa nháp cũ. Câu «Website từ chối rõ ràng…» → «App hay website từ chối rõ ràng vì lý do khác…» |
| SL-T108-1 | `:7` | «tạo bài nháp có ảnh đại diện» → «tạo thử bài nháp chữ» (trang Kết nối sau T-108: mục «3. Tạo thử một bài nháp», chỉ chữ; README `:135`) |
| SL-T106-1 | — | **Không sửa:** câu khuyên «Quản trị viên (Administrator)» nằm ở `app/views/wordpress.py` (code), không phải README; 2 `xfail` của ca này giữ nguyên. Cần phiếu Họa Sĩ (bỏ «hoặc Quản trị viên (Administrator)») |

Không đổi số mục (## 1 … ## 14), không thêm mục.

### Gỡ dấu `xfail` (chỉ xóa dòng dấu)

| Ca | Trước khi gỡ | Diff |
|---|---|---|
| `tests/test_soi_loi_t112.py::test_sl_t112_2_readme_hen_gio_anh_dai_dien_hong_khong_hen` | `--runxfail`: qua | 6 dòng xóa |
| `tests/test_soi_loi_t112.py::test_sl_t112_3_readme_khong_noi_tat_o_tab_khac_la_tat_tab_nay` | `--runxfail`: qua | 5 dòng xóa |
| `tests/test_soi_loi_t106.py::test_sl_t108_1_readme_trang_thai_khop_trang_ket_noi` | `--runxfail`: qua | 4 dòng xóa |

`git diff --numstat -- tests/`: `0 4 tests/test_soi_loi_t106.py`, `0 11 tests/test_soi_loi_t112.py` (chỉ xóa, 0 dòng thêm).

### Đối chiếu với code

| README nói | Code |
|---|---|
| Công tắc chỉ trong phiên (mỗi tab một phiên) | `RELEASE_SWITCH` trong `st.session_state` (`app/views/write.py`, `app/views/settings.py` `release_tab`); ca Soi Lỗi `test_moi_phien_mot_cong_tac_tat_o_tab_khac_khong_tat_tab_nay` |
| Đăng ngay/Hẹn giờ khi tiêu đề, mô tả SEO bị bỏ | `MSG_PUBLISH_SEO_LEFT_OUT`, `MSG_SCHEDULE_SEO_LEFT_OUT` `write.py:376-383` (Họa Sĩ lượt 3, báo cáo mục 9.2) |
| Ảnh đại diện lỗi → Hẹn giờ bị client từ chối | `seo_app/wordpress/client.py:1545-1550` (`self._modified` không có mã bài → `_RELEASE_CHANGED`); ca `test_t112_release_rules.py::test_schedule_with_featured_failure_is_refused_by_client` |
| Bài bị sửa ngoài app → không hẹn giờ/đăng, câu báo | `_RELEASE_CHANGED` `client.py:618-622`, so `modified_gmt` `:1539-1550` (T-115) |
| Trang Kết nối chỉ tạo thử bài nháp chữ | `app/views/wordpress.py` mục «3. Tạo thử một bài nháp» (`:169`); README `:135` |

7 câu trích mới kiểm bằng Python (đọc UTF-8, nối chuỗi viết tách dòng): đều có trong code.

### Kiểm tra lượt 2

```
$ uv run pytest --runxfail <3 ca README ở trên>
3 passed
$ uv run pytest tests/test_soi_loi_t112.py tests/test_soi_loi_t106.py      (sau khi gỡ dấu)
42 passed, 2 xfailed          # 2 xfail còn lại = SL-T106-1 (code, ngoài phạm vi)
$ uv run ruff check .
All checks passed!
$ uv --version            # trước khi chạy uvx (T-078)
uv 0.13.4 (…)
$ PYTHONUTF8=1 uvx detect-secrets scan README.md docs/team/reports/T-112-thu-ky.md tests/test_soi_loi_t112.py tests/test_soi_loi_t106.py
  "results": {}
```

Dẫn chiếu «mục N»: 2, 3, 5 (`security.md`), 6, 7, 7.1, 7.2, 7.5, 8, 9, 10, 11, 13, 14. Đều có thật.

### Còn để ngỏ

- **SL-T106-1** (Thấp, code `app/views/wordpress.py`): cần phiếu cho Họa Sĩ.
- Hẹn giờ/Đăng ngay vẫn chưa thử trên website thật (LC-T094-44). Sau buổi thử nên đọc lại mục 11.

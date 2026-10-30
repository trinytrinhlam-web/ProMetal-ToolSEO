# Báo cáo T-099 · Client WordPress: hẹn giờ, đăng ngay, đọc trạng thái bài

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-099](../tickets/T-099-client-hen-gio-dang-ngay.md) (Giai đoạn 5, đợt 1) |
| Ngày nộp | 2026-10-29 00:06 (giờ máy, +07) |
| Kết quả | Hoàn thành phần code (chờ Soi Lỗi rút gọn, Lá Chắn đầy đủ, soát kỹ nhất) |

## Tóm tắt (cho chủ dự án)

- Phần mềm đã có **đúng một chỗ trong code** chuyển bài nháp sang **hẹn giờ** hay **đăng ngay**. Chưa có nút nào trên giao diện dùng tới: màn hình xác nhận và hai nút làm ở T-102, có công tắc mặc định tắt.
- Chỗ đó chỉ nhận bài nháp **phần mềm vừa tạo trong chính lần bấm đó**. Ngay trước khi chuyển, phần mềm hỏi lại website bài còn là nháp không. Bài đã có từ trước trên website thì không bao giờ bị chuyển (đúng câu 5A bạn chốt).
- **Giờ hẹn** tính theo giờ Việt Nam bạn chọn, đổi sang giờ quốc tế trước khi gửi. Phần mềm lấy giờ của chính website, rồi **chặn** khi:
  - giờ hẹn chưa tới 10 phút nữa, vì WordPress đăng ngay bài hẹn giờ quá gần;
  - giờ hẹn đã qua;
  - giờ hẹn xa hơn một năm;
  - đồng hồ máy tính lệch website hơn 2 phút;
  - không đọc được giờ của website.
- Gửi xong, phần mềm **kiểm câu trả lời**:
  - Website báo đúng thì xong.
  - Bạn chọn hẹn giờ mà website lại đăng ngay: hiện câu báo **KHẨN**, kèm cách chuyển bài về nháp.
  - Mất mạng, website lỗi, câu trả lời lạ: phần mềm báo «bài **có thể đã** hẹn giờ/đăng, mở trang quản trị kiểm tra» và **không tự gửi lại**.
- Có thêm lệnh **chỉ đọc** trạng thái bài (nháp, đã hẹn giờ, đã đăng…). Bước «Cập nhật trạng thái từ website» của trang Kế hoạch sẽ dùng lệnh này.
- Phần mềm đọc múi giờ của website. Múi giờ khác giờ Việt Nam thì nhắc: trang quản trị sẽ hiện giờ khác, nhưng bài vẫn lên đúng giờ Việt Nam.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/wordpress/client.py` | **Mới:** dấu riêng `_RELEASE` và khuôn `_is_release_request` (lệnh hẹn giờ/đăng duy nhất được phép); `release_draft` (+ `_release_check`, `_released_from`); `post_statuses` (+ `_state_from`); lớp `Released`, `ReleaseError`, `PostState`; `ConnectionInfo.timezone_string`, `gmt_offset`, `timezone_warning`; hàm phụ `_utc_now`, `_is_date_gmt`, `_is_id_list`, `_site_timezone`, `_site_offset`, `_format_offset`; câu báo `_RELEASE_*`, `_STATUS_BAD_IDS`. **Sửa chỗ dùng chung (nhỏ, có kiểm nơi gọi, mục «Hàm dùng chung đã sửa»):** `_is_plain_request` thêm tham số `release` và bảng kiểm giá trị `_PARAM_VALUES`; `_request` gỡ dấu `release` khỏi tùy chọn; `_FORBIDDEN_JSON_KEYS` thêm `date`, thêm `_RELEASE_ONLY_JSON_KEYS = {date_gmt}`; `ALLOWED_PARAMS` của `GET /wp/v2/posts` thêm `include`, `context`; `check_connection` đọc thêm 2 trường của `GET /wp-json/`; docstring đầu module |
| `seo_app/publish/schedule.py` (mới) | Logic giờ thuần: `local_to_utc`, `date_gmt_text`, `schedule_label`, `parse_server_date`, `release_time_problem` (lớp chặn cuối của client), `check_schedule` (cho màn hình chọn giờ, trả `Notice` như bộ dựng T-096) |
| `tests/test_wordpress_release.py` (mới) | 220 test: chạy đúng, LC-T094-22 → -27 (bảng dưới) |
| `tests/test_soi_loi_t037.py` | Đổi kỳ vọng 1 ca, Chỉ Huy duyệt 29/10 (mục «Test cũ đã đổi») |
| `tests/test_publish_schedule.py` (mới) | 81 test: đổi giờ, `date_gmt`, nhãn thứ, header `Date`, lớp chặn, màn hình chọn giờ |

Không sửa `app/**`, `config/**`, `seo_app/storage/**`, `seo_app/plan/**`, `seo_app/wordpress/__init__.py` (T-102 nhập thẳng từ `seo_app.wordpress.client`).

## Cách chạy của `release_draft` (thiết kế T-094 mục 3.3)

1. **Kiểm trước khi gửi gì** (sai: `ReleaseError`, 0 request): mã bài thuộc `_created_post_ids` của chính đối tượng client; `mode` đúng chữ `"future"`/`"publish"`; Đăng ngay không kèm giờ; Hẹn giờ thì `when_utc` là `datetime` có múi giờ (đổi ra chuỗi `date_gmt` bằng `schedule.date_gmt_text`, cùng hàm bộ dựng T-096 dùng cho mã băm xác nhận). Lệnh chuyển dựng sẵn được chạy qua `is_allowed_route` và `_is_plain_request(…, release=_RELEASE)` **trước** cả lệnh kiểm nháp: session có header lạ thì 0 request.
2. **Hỏi lại website** `GET /wp/v2/posts/<mã>?context=edit&_fields=id,status`: phải đúng mã, `status == "draft"` đúng chữ. Không còn nháp: bỏ mã khỏi `_created_post_ids`, từ chối. Giờ máy chủ đọc từ header `Date` của **chính câu trả lời này** (`parse_server_date`: chuỗi ASCII in được ≤ 64 ký tự, `email.utils.parsedate_to_datetime`, phải có múi giờ; `-0000` cũng bị coi là không rõ). `release_time_problem`: không có giờ máy chủ → Chặn; `|đồng hồ máy − giờ máy chủ| > 2 phút` → Chặn; Hẹn giờ: `giờ hẹn − giờ máy chủ` ≤ 0 → «đã qua», < 10 phút → «quá gần», > 365 ngày → «quá xa» (so bằng phép trừ, không tràn ở năm 9999; trên giờ đã bỏ phần lẻ của giây, đúng giờ sẽ gửi).
3. **Bỏ mã bài khỏi `_created_post_ids`** (từ đây không lệnh nào của client sửa tiếp bài, kể cả khi lỗi), rồi gửi **một** lệnh `POST /wp/v2/posts/<mã>?_fields=id,status,date_gmt,link` thân đúng `{"status": "future", "date_gmt": "YYYY-MM-DDTHH:MM:SS"}` hoặc `{"status": "publish"}`.
4. **Kiểm câu trả lời**: đúng mã bài; `status` đúng chế độ; Hẹn giờ thì `date_gmt` trả về đúng chuỗi đã gửi. `link` lạ (khác website) thì để rỗng.

| Kết cục | Trả về | `unsure` | `went_public` |
|---|---|---|---|
| Đúng hết | `Released(post_id, status, date_gmt, link, edit_link)` | | |
| Chặn ở bước 1–2 (chưa gửi lệnh chuyển) | `ReleaseError` «… bài vẫn là nháp» | tắt | tắt |
| Website từ chối 4xx ở lệnh chuyển (thiếu quyền `publish_posts`…) | `ReleaseError` câu cố định theo mã + «bài vẫn là nháp trên website» | tắt | tắt |
| Hết giờ, mất mạng, 3xx, 5xx, câu trả lời không phải JSON, lỗi lạ | `ReleaseError` «Không biết chắc… có thể đã… không tự gửi lại» | **bật** | tắt |
| Câu trả lời sai mã, sai trạng thái, Hẹn giờ mà giờ khác | `ReleaseError` «không đúng như mong đợi / giờ hẹn khác» | **bật** | tắt |
| Hẹn giờ mà website báo `publish` | `ReleaseError` «KHẨN… ĐĂNG CÔNG KHAI NGAY… chuyển về «Bản nháp»… báo chủ dự án» | tắt | **bật** |

Không nhánh nào gửi thêm lệnh vào bài sau lệnh chuyển. Mọi câu báo cố định: không chép lời máy chủ, không chép `WORDPRESS_URL`; chỉ chèn mã bài (số đã kiểm) và mã HTTP. `ReleaseError` mang `post_id`, `edit_link` để giao diện hiện link sửa bài (chữ thuần).

## Đối chiếu điều kiện Lá Chắn T-094

| Mã | Đáp ứng ở đâu | Test |
|---|---|---|
| LC-T094-1 (không gọi WordPress thật) | Test chỉ dùng `FakeWordPress` (`tests/fake_wordpress.py`, không sửa); bộ chặn mạng của `tests/conftest.py` vẫn bật. `schedule.py` không gọi mạng | Cả hai file test mới |
| LC-T094-2 (câu báo cố định) | `_RELEASE_*`, `_STATUS_BAD_IDS` (`client.py`), `MSG_*` (`schedule.py`): câu cố định; lỗi máy chủ đi qua `_error_from` sẵn có (không chép `message`); `raise … from None` ở lỗi WordPress | `test_tu_choi_4xx_thi_bai_van_la_nhap`, `test_loi_khong_ro_thi_co_the_da_chuyen_khong_tu_gui_lai`, `test_khong_kiem_duoc_nhap_thi_khong_gui_lenh_chuyen`, `test_loi_la_*`, `test_post_statuses_loi_may_chu_cau_co_dinh`: chuỗi mồi `BAIT` trong lời máy chủ, ngoại lệ không có trong câu báo; `WORDPRESS_URL` không có |
| LC-T094-3 (chữ hiện thuần) | Thuộc giao diện (T-101, T-102). Client chỉ trả chữ đã kiểm dạng: `link` qua `is_site_link`, `date_gmt` dạng ASCII cố định, `timezone_string` theo `_SITE_TIMEZONE`; `timezone_warning` không chèn chữ website (chỉ số độ lệch đã kiểm) | `test_mui_gio_khac_thi_canh_bao_chi_chen_so`, `test_post_statuses_bo_muc_la` |
| **LC-T094-22** (đúng một đường) | `_RELEASE = object()` (`client.py:184`); `_is_plain_request(…, release=…)` (`:215`): `release is _RELEASE` (so bằng `is`), thứ khác (kể cả `object()` khác, `True`) → từ chối; có dấu thì phải đúng `_is_release_request` (`:295`): `POST /wp/v2/posts/<mã>`, tùy chọn đúng `json` + `params`, `params` đúng `{"_fields": "id,status,date_gmt,link"}`, thân đúng `{"status": "future", "date_gmt": <ASCII YYYY-MM-DDTHH:MM:SS>}` hoặc `{"status": "publish"}` (`str` thật, đúng chữ). Không dấu: luật cũ (`status` chỉ `"draft"`), thêm `date` vào `_FORBIDDEN_JSON_KEYS` (không lệnh nào gửi, kể cả lệnh có dấu), `date_gmt` chỉ lệnh có dấu (`_RELEASE_ONLY_JSON_KEYS`). `_request` gỡ `release` khỏi tùy chọn trước khi tới `requests` (`:1940`). `create_draft` không đổi (chỉ `"draft"`) | `test_khong_dau_rieng_thi_khong_gui_duoc_trang_thai_hay_ngay` (12 ca, mọi đường ghi), `test_noi_danh_sach_khoa_van_khong_gui_duoc_date_gmt_hay_status_khac`, `test_co_dau_rieng_ma_sai_khuon_thi_chan` (26 ca), `test_dau_gia_bi_chan` (5 ca), `test_dau_rieng_dung_khuon_thi_qua_lop_kiem` (đối chứng), `test_dau_rieng_khong_toi_requests`, `test_tao_nhap_van_chi_draft`. **Đọc mã nguồn:** `test_dau_rieng_chi_o_dinh_nghia_release_draft_va_lop_kiem` (cây cú pháp: tên `_RELEASE` chỉ ở định nghĩa, `release_draft`, `_is_plain_request`; không file nào khác trong `seo_app/`, `app/` nhắc tới), `test_trong_client_chi_release_draft_gui_lenh_co_dau`, `test_release_draft_chi_duoc_goi_tu_mot_ham_buoc_xuat_ban` (hiện 0 nơi gọi; tối đa 1 hàm, phải ở `app/views/write.py`) |
| **LC-T094-23** (chỉ bài vừa tạo) | `release_draft` bước 1: `type(post_id) is int` và thuộc `_created_post_ids` (chỉ `create_draft` thêm vào, khi site xác nhận `draft`); bước 2 `_release_check` hỏi lại còn `draft`; không còn → bỏ mã. Bỏ mã **trước** lệnh chuyển. `post_statuses` không thêm mã nào. Câu 5A: không có đường hẹn giờ, đăng bài nháp có từ trước. **Phần «nên» so `modified_gmt`: chưa làm** (mục «Rủi ro» 1) | `test_bai_khong_do_client_tao_thi_tu_choi_khong_request` (6 ca, có `True`, `"42"`, `42.0`), `test_client_cua_luot_khac_khong_chuyen_duoc`, `test_ma_bai_tu_post_statuses_khong_thanh_bai_duoc_sua`, `test_site_bao_khong_con_la_nhap_thi_khong_gui_lenh_chuyen` (9 ca: `publish`, `future`, `pending`, `private`, `trash`, `Draft`, mã khác, mã chữ, danh sách), `test_sau_khi_chuyen_khong_lenh_nao_sua_tiep_bai`, `test_khong_kiem_duoc_nhap_*`, `test_mat_mang_luc_kiem_nhap_*`, `test_loi_la_luc_kiem_nhap_*` |
| **LC-T094-24** (giờ) | `date_gmt_text` (`schedule.py:98`): chỉ `datetime` có múi giờ (không lớp con), đổi UTC, bỏ phần lẻ của giây, 4 chữ số năm. `parse_server_date` (`:124`). `release_time_problem` (`:147`) với giờ máy chủ của **câu trả lời kiểm nháp ngay trước lệnh** (`_release_check` trả về), `_utc_now()` là đồng hồ máy. Đăng ngay không gửi ngày | `test_gio_hen_khong_mui_gio_hay_sai_kieu_thi_khong_request` (5 ca), `test_dang_ngay_kem_gio_thi_khong_request`, `test_hinh_thuc_la_thi_khong_request` (7 ca), `test_khong_doc_duoc_gio_may_chu_thi_chan` (6 dạng `Date` × 2 chế độ: thiếu, hỏng, ngày 99, `-0000`, quá dài, chữ ngoài ASCII), `test_dong_ho_may_lech_qua_2_phut_thi_chan` (lệch ±3 phút, 2 phút 1 giây, 400 ngày), `test_gio_hen_qua_gan_hay_qua_xa_theo_gio_may_chu_thi_chan` (đã qua, bằng bây giờ, 9 phút 59 giây, 365 ngày + 1 giây, 400 ngày), `test_bien_10_phut_va_365_ngay_duoc_gui`, `test_moc_10_phut_tinh_theo_gio_may_chu_khong_theo_dong_ho_may`, `test_gio_may_chu_lay_tu_chinh_cau_tra_loi_kiem_nhap`; cùng các ca trong `test_publish_schedule.py` |
| **LC-T094-25** (kiểm câu trả lời) | `_released_from` (`client.py:1474`) và nhánh lỗi của `release_draft` (bảng «Kết cục» ở trên) | `test_hen_gio_ma_site_dang_ngay_thi_bao_khan_va_dung` (chỉ 2 request, không gửi thêm), `test_cau_tra_loi_sai_thi_co_the_da_chuyen_khong_gui_lai` (14 ca), `test_tu_choi_4xx_thi_bai_van_la_nhap` (6 mã), `test_loi_khong_ro_thi_co_the_da_chuyen_khong_tu_gui_lai` (500, 502 HTML, 301, hết giờ, mất kết nối, đứt luồng × 2 chế độ; gọi lại: 0 request), `test_loi_la_khi_gui_thi_co_the_da_chuyen` |
| **LC-T094-26** (`post_statuses` chỉ đọc) | `post_statuses` (`client.py:1507`): chỉ `GET /wp/v2/posts`; mã đầu vào là số nguyên dương thật, ≤ 1.000; mỗi lệnh ≤ 100 mã (`include`), `status=draft,future,publish,pending,private`, `context=edit`, `per_page=100`, `_fields=id,status,date_gmt,modified_gmt,link` (hằng, không `content`, `excerpt`). `_PARAM_VALUES` (`:332`) kiểm **giá trị** trước khi gửi: `include` khớp `_ID_LIST` (1–100 mã ASCII, không số 0 đầu, không dấu cách, không `;`), `status` chỉ `publish` (cho `list_published`) hoặc đúng hằng trên, `context` chỉ `edit`. `include`, `context` chỉ thêm vào **đúng** `GET /wp/v2/posts`. Kết quả chỉ giữ mục đúng mã đã hỏi, trạng thái thuộc danh sách; không đổi `_created_post_ids` | `test_post_statuses_mot_lenh_chi_doc_tham_so_hang`, `test_post_statuses_bo_muc_la`, `test_post_statuses_chia_lenh_moi_lenh_toi_da_100_ma`, `test_post_statuses_ma_sai_thi_khong_hoi` (13 ca), `test_tham_so_doc_trang_thai_sai_gia_tri_thi_chan` (20 ca: chữ, số âm, `1,2;3`, 101 mã, `01`, `１`, số nguyên, `status=any`, `context=view`, `_fields` có `content`…), `test_include_chi_cho_get_posts`, `test_include_dung_100_ma_duoc_gui_va_list_published_van_chay` |
| **LC-T094-27** (múi giờ) | `ConnectionInfo.timezone_string` (`_site_timezone`: chữ dạng IANA `[A-Za-z][A-Za-z0-9_+/-]{0,63}`, còn lại rỗng), `gmt_offset` (`_site_offset`: số hay chữ số ASCII, −12 … +14, không `bool`, không NaN; còn lại `None`); `timezone_warning(timezone_name)` chỉ để Cảnh báo, câu cố định chỉ chèn độ lệch đã kiểm. `schedule.py` dùng `ZoneInfo(timezone_name)` (tên lấy từ `settings.timezone_name`, đã kiểm ở `load_settings`); nhãn tính từ giờ người dùng chọn: cả module không gọi đồng hồ máy | `test_mui_gio_*` (8 hàm), `test_connection_info_cu_van_tao_duoc_khong_can_mui_gio`; `test_nhan_*`, `test_module_khong_doc_dong_ho_may` |

## Hàm dùng chung đã sửa: nơi gọi và test cũ (yêu cầu 4)

| Chỗ sửa | Nơi gọi (grep cả nhập muộn) | Ảnh hưởng |
|---|---|---|
| `_is_plain_request` thêm `release` (chỉ từ khóa, mặc định `None`) | `_request`, `release_draft` (mới). Không test cũ nào gọi thẳng | Không dấu thì như cũ, cộng: khóa thân JSON `date`, `date_gmt` bị chặn (trước đây đã bị chặn vì không có trong `ALLOWED_JSON_KEYS`; nay chặn cả khi ai đó nới danh sách) |
| `_PARAM_VALUES`: giá trị `status` của `GET /wp/v2/posts` chỉ `publish` hay hằng mới | `list_published` (gửi `status=publish`) | Test cũ gửi `status=publish` vẫn qua (grep `"status": "publish"` trong `test_wordpress_t085.py`, `test_soi_loi_t085.py`, `test_wordpress_t060.py`) |
| `ALLOWED_PARAMS` `GET /wp/v2/posts` thêm `include`, `context` | `list_published`, `post_statuses` | `test_wordpress_t060.py::test_moi_duong_duoc_phep_deu_co_danh_sach_tham_so_va_nguoc_lai` vẫn đúng (không tên cấm) |
| `_FORBIDDEN_JSON_KEYS` thêm `date` | `_is_plain_request` | Không test cũ nào sửa hằng này |
| `_request` gỡ `release` | mọi hàm của client | Không ai truyền `release` ngoài `release_draft` (test đọc mã nguồn) |
| `ConnectionInfo` thêm 2 trường có mặc định ở **cuối** | `check_connection`; 8 chỗ tạo bằng vị trí trong test (`test_app_t044_safe_text.py`, `test_app_wordpress.py`, `test_soi_loi_t031.py`, `test_soi_loi_t091.py`, `test_t041_seo_ui.py`, `test_t091_don_client_wordpress.py`, `test_wordpress_seo_meta_t042.py`); `app/views/wordpress.py` chỉ đọc thuộc tính | Tạo bằng vị trí vẫn chạy; không test nào so bằng cả đối tượng |
| `check_connection` đọc `timezone_string`, `gmt_offset` | Trang Kết nối WordPress | Site không trả hai khóa: rỗng / `None` |

**Test cũ ghim bất biến cũ** (grep đọc mã nguồn `client.py`, chữ `publish`, `future`, `status`):

- `tests/test_soi_loi_t037.py::test_client_module_publish_names_are_read_only_helpers` và `test_r2_allowlist_still_blocks_other_names`: bắt mọi tên có chữ «publish» trong module client. Tên hằng câu báo đầu tiên của tôi (`_RELEASE_PUBLISH_WITH_TIME`) bị bắt; đã **đổi tên** thành `_RELEASE_NOW_WITH_TIME` (chỉ là câu báo). Hai test này qua, không sửa. Lưu ý: test tên **không** bắt được `release_draft` (tên không có chữ «publish»); đường mới được test cú pháp dưới đây và test LC-T094-22 bắt.
- `tests/test_soi_loi_t037.py::test_status_publish_or_future_only_in_list_published`: đọc cây cú pháp, khẳng định chỉ `list_published` có dict khóa `"status"` mang giá trị khác `"draft"`. T-099 **cố ý** thêm đúng hai chỗ như thế: `release_draft` (`"future"`, `"publish"`) và `post_statuses` (`POST_STATUS_FILTER`, chỉ đọc). Đã đổi kỳ vọng sau khi hỏi (bảng «Test cũ đã đổi»).
- `tests/test_safety.py::test_every_write_request_to_posts_never_publishes`, `test_create_draft_has_no_way_to_choose_status`: vẫn qua (tạo nháp, ảnh đại diện không đổi).

### Test cũ đã đổi

Chỉ Huy duyệt 29/10 (R5), đúng đề nghị: danh sách vẫn so **bằng** (`==`), không đổi thành «chứa».

| Ca | Dòng cũ | Dòng mới | Lý do |
|---|---|---|---|
| `tests/test_soi_loi_t037.py::test_status_publish_or_future_only_in_list_published` (kỳ vọng ở dòng 491 cũ, nay 496–501) | `assert offenders == [("list_published", "'publish'")]` | `assert offenders == [("list_published", "'publish'"), ("release_draft", "'future'"), ("release_draft", "'publish'"), ("post_statuses", "POST_STATUS_FILTER")]` | T-099 thêm đường duy nhất tới `future`/`publish` (`release_draft`) và lệnh chỉ đọc `post_statuses` theo thiết kế T-094 mục 3.3. Hàm nào khác thêm `status` lạ thì test vẫn đỏ |
| cùng ca, docstring | «Khóa ``status`` khác ``draft`` (publish, future…) chỉ được nằm trong hàm đọc.» | Nói rõ: chỉ `release_draft` được **gửi** trạng thái khác nháp (đường duy nhất theo thiết kế T-094 mục 3.3, LC-T094-22); `list_published`, `post_statuses` chỉ **đọc**; so bằng `==` | Khớp kỳ vọng mới |

Không đổi test cũ nào khác. Phần thân phép dò (đọc cây cú pháp) giữ nguyên.

## Bằng chứng

Máy Windows của chủ dự án, worktree `wt-T-099` (nhánh `team/T-099` = `main` `b241e79` + T-091 `9e0115e`).

```
$ uv sync
$ uv run pytest -q -p no:cacheprovider tests/test_wordpress_release.py tests/test_publish_schedule.py \
      tests/test_soi_loi_t037.py tests/test_safety.py
477 passed in 65.64s                       # 220 + 81 test mới; T-037 sau khi đổi kỳ vọng đã duyệt

$ uv run pytest -q -p no:cacheprovider <76 file test liên quan>      # 28/10 23:30 → 29/10 00:06
1 failed, 10643 passed, 1 skipped, 8 xfailed in 2186.84s (0:36:26)
FAILED tests/test_soi_loi_t037.py::test_status_publish_or_future_only_in_list_published
                                           # ca đã báo Chỉ Huy, đổi kỳ vọng sau khi duyệt, chạy lại: qua

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan <5 file của phiếu>
seo_app/wordpress/client.py: 1 «Basic Auth Credentials» ở dòng chú thích ví dụ
"htps://tên:mật-khẩu@site" có từ 23/10 (git blame 9f3b7e26), không phải khóa thật,
phiếu này không sửa dòng đó. 4 file còn lại: 0.
```

76 file liên quan: mọi file test nhắc tới client WordPress (`wordpress`, `fake_wp`, `FakeWordPress`, `ConnectionInfo`), `seo_app.publish`, gửi nháp, ghi SEO, gồm cả hai file mới.

**Thử «làm hỏng» code để chắc test bắt được** (sửa tạm trên bản chép, chạy `tests/test_wordpress_release.py`, rồi trả nguyên file; `cmp` xác nhận giống hệt):

| Làm hỏng | Số test đỏ |
|---|---|
| `_is_release_request` luôn đúng (bỏ kiểm khuôn) | 23 |
| Bỏ kiểm khoảng giờ hẹn | 8 |
| Không bỏ mã bài khỏi `_created_post_ids` trước lệnh chuyển | 28 |
| Nhận mọi dấu (`release is not None` thay cho `is _RELEASE`) | 6 |
| Bỏ kiểm lệch đồng hồ | 8 |
| Hẹn giờ mà website đăng ngay coi như thành công | 1 |
| Không kiểm giá trị `include` | 12 |

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: đúng dòng T-099 của thiết kế (mục 3.3, 3.4; `ConnectionInfo` thêm múi giờ site). Chỉ sửa `client.py` (phần mới, cộng các chỗ dùng chung ghi ở trên), `schedule.py` (mới), test.
- [x] Yêu cầu 2: LC-T094-22 → -27 và phần «Chung» (bảng trên). LC-T094-3 là việc giao diện. LC-T094-23 phần «nên» chưa làm (mục «Rủi ro» 1).
- [x] Yêu cầu 3: giữ nguyên `ALLOWED_ROUTES` (không thêm đường), `_created_post_ids`, `_positive_id`, `_json` (không sửa).
- [x] Yêu cầu 4: grep nơi gọi và test ghim bất biến cũ (mục trên).
- [x] Yêu cầu 5: 301 test mới; test cũ liên quan: 76 file, 10.643 qua; 1 đỏ là ca T-037 đã được duyệt đổi kỳ vọng, chạy lại qua; `uv run ruff check .` sạch.
- [x] Yêu cầu 6: báo cáo này.

## Rủi ro và điểm cần chú ý

1. **LC-T094-23, phần «nên» (so `modified_gmt`) chưa làm.** Muốn biết ai sửa nháp trong trang quản trị giữa lúc tạo và lúc chuyển, cần giá trị `modified_gmt` lấy **từ câu trả lời các lệnh ghi của chính app**, rồi so với lúc kiểm nháp. Hiện các lệnh ghi hỏi `_fields` cố định không có `modified_gmt` (`_POST_FIELDS`, `_POST_META_FIELDS`). Năm file test cũ ghim đúng chuỗi `_fields` đó (`test_shortcode_t061.py`, `test_soi_loi_t042.py`, `test_soi_loi_t054.py`, `test_wordpress_seo_meta_t042.py`, `test_wordpress_t060.py`), nên muốn thêm phải đổi kỳ vọng test cũ. So với header `Date` thì không dùng được: giờ trong cơ sở dữ liệu website và giờ của lớp đệm (CDN) có thể lệch vài giây, gây chặn oan mỗi lần. Khe hở thật chỉ vài giây, trong cùng một lần bấm. Nội dung app gửi đã được mã băm xác nhận của T-102 khóa. Nếu Lá Chắn muốn có, đề xuất lượt 2: thêm `modified_gmt` vào hai `_fields` trên (đổi 5 file test cũ, cần Chỉ Huy duyệt).
2. **Chưa thử với website thật** (LC-T094-44): website có trả header `Date` đúng không (không có thì app chặn hẹn giờ, đăng); tài khoản Biên tập viên đặt `future` bằng `date_gmt` qua REST được không; plugin bảo mật có chen câu trả lời không. Kiểm ở lượt thử thật trước khi bật công tắc (LC-T094-41).
3. Lệnh chuyển bị website từ chối 4xx: app báo «bài vẫn là nháp». Theo mã WordPress, lời từ chối 4xx là chưa lưu gì. Một plugin lạ lưu rồi mới trả 4xx thì câu này sai; Thấp, như cách client đang xử lý tải ảnh, tạo nháp.
4. Câu trả lời 3xx: như mọi lệnh của client, `requests` đọc thân câu trả lời chuyển hướng trước khi app kịp xét. App không đi theo, báo «có thể đã». Có từ trước, Thấp.
5. `timezone_warning` so độ lệch **hiện tại** của múi giờ phần mềm. Việt Nam không đổi giờ; múi giờ có giờ mùa hè thì câu cảnh báo có thể đổi theo mùa.

## Đề xuất

- **T-102 (Họa Sĩ), khi nối giao diện:**
  - Gọi `release_draft` từ **đúng một hàm** của `app/views/write.py`. Test `test_release_draft_chi_duoc_goi_tu_mot_ham_buoc_xuat_ban` sẽ đỏ nếu có hàm thứ hai hay gọi từ file khác.
  - Gọi trên **chính** client vừa tạo nháp trong lần bấm đó, sau ảnh đại diện và ghi SEO.
  - `when_utc` lấy từ `schedule.local_to_utc(ngày, giờ, settings.timezone_name)`, dùng **cùng giá trị** cho `build_article(date_gmt=schedule.date_gmt_text(when_utc))`.
  - Bắt `ReleaseError`: `unsure` hay `went_public` bật thì khóa gửi lại, hiện `str(err)` bằng widget chữ thường, `edit_link` không bấm được.
  - `check_schedule` cho màn hình chọn giờ, `schedule_label` cho nhãn, `ConnectionInfo.timezone_warning(settings.timezone_name)` cho cảnh báo múi giờ.
- **T-101:** «Cập nhật trạng thái từ website» dùng `post_statuses(mã bài từ Sheet)`; mã không có trong kết quả là bài đã xóa hay không xem được; «Lỡ lịch» so `PostState.date_gmt` với giờ hiện tại.
- **Soi Lỗi:** thử thêm các dạng header `Date` lạ của máy chủ thật. Dạng RFC 850 đọc được; dạng asctime (không ghi múi giờ) và `gmt_offset` dạng `"+7"` bị coi là không đọc được, tức là chặn hay cảnh báo: chiều an toàn.

## Câu hỏi cho chủ dự án

Không có.

---

## Lượt 2 (2026-10-30): LC-T099-1, SL-T099-1

Theo biên bản Lá Chắn `T-099-la-chan.md` (ĐẠT CÓ ĐIỀU KIỆN, `ce451fe`) và Soi Lỗi `T-099-soi-loi.md`. Hai lỗi Thấp, bắt buộc trước khi T-102 nối màn hình xác nhận.

### Tóm tắt (cho chủ dự án)

- Chỗ hẹn giờ, đăng bài nay **giành quyền chuyển bài ngay bước đầu**. Nếu sau này có hai việc cùng chuyển một bài, chỉ một việc được gửi lệnh, việc kia bị từ chối ngay. Bị chặn trước khi gửi lệnh (giờ sai, mất mạng lúc kiểm nháp…) thì bài vẫn là nháp của lần gửi đó như cũ.
- Lớp chặn lệnh WordPress nay chỉ nhận thân dạng byte ở đúng lệnh **tải ảnh**. Trước đây lệnh vào bài viết vẫn lọt qua lớp chặn nếu mang thân byte; website bỏ qua thân đó nên chưa thành lỗ, nhưng lời hứa «chỉ một chỗ được đăng bài» nay nằm hẳn ở lớp chặn của phần mềm.

### Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/wordpress/client.py` | **LC-T099-1:** `release_draft` giành mã bài bằng `self._created_post_ids.remove(post_id)` ngay đầu hàm (`KeyError` → từ chối «chỉ bài nháp vừa tạo», 0 request). Mọi bước trước lệnh chuyển (hình thức, giờ, lớp chặn, lệnh kiểm nháp, giờ máy chủ, lệch đồng hồ, khoảng hẹn giờ) nằm trong `try … finally`: bị chặn thì `finally` trả mã lại (`give_back`). Website báo không còn nháp: **không** trả mã. Ngay trước lệnh chuyển: `give_back = False`, mã không bao giờ trả lại. `_release_check` nay trả `(còn nháp, giờ máy chủ)`, không tự đụng `_created_post_ids`. Docstring bước 1–3 viết lại. Mọi chỗ dùng `_RELEASE` vẫn chỉ trong `release_draft`, `_is_plain_request`. **SL-T099-1:** `_is_image_upload` (mới) và một dòng trong `_is_plain_request`: có `data` thì phải đúng `POST /wp/v2/media`, không kèm `json`, có **đúng một** header `Content-Type` thuộc `IMAGE_TYPES`; còn lại từ chối trước khi gửi |
| `tests/test_la_chan_t099.py` | Gỡ 1 dấu `xfail` (LC-T099-1), chỉ xóa dòng dấu |
| `tests/test_soi_loi_t099.py` | Gỡ 1 dấu `xfail` phủ 5 ca (SL-T099-1), chỉ xóa dòng dấu |
| `tests/test_wordpress_release.py` | Thêm 27 ca của Thợ Máy (mục dưới) |

Trước khi gỡ dấu: chạy `-rX`, đủ 6 ca XPASS(strict) (1 LC-T099-1, 5 SL-T099-1), mọi ca khác qua. Không đổi điều kiện ca nào.

### Test mới (lượt 2)

| Test | Kiểm |
|---|---|
| `test_dang_kiem_nhap_thi_ma_bai_da_roi_khoi_tap` | Lúc lệnh kiểm nháp còn chờ, mã bài đã rời tập; lần gọi `release_draft` thứ hai và `set_featured_image` từ chính lúc đó bị từ chối, 0 request thêm (bản một luồng, xác định, của ca hai luồng của Lá Chắn) |
| `test_bi_chan_truoc_lenh_chuyen_thi_tra_ma_lai` (7 ca) | Hình thức lạ, Đăng ngay kèm giờ, giờ sai kiểu, header phiên lạ, lệnh kiểm nháp lỗi 500, thiếu `Date`, giờ quá gần: mã trở lại tập, không có lệnh chuyển |
| `test_khong_con_nhap_hay_da_gui_lenh_chuyen_thi_khong_tra_ma` | Không còn nháp, hay đã gửi lệnh chuyển (lỗi 503): mã không trở lại |
| `test_gianh_ma_bai_bang_mot_lenh_truoc_moi_lenh_mang` | Đọc mã nguồn: `remove` đứng trước `_release_check`, `_request`; không còn `in self._created_post_ids`, `discard` trong `release_draft` |
| `test_than_byte_chi_o_lenh_tai_anh` (12 ca) | Thân byte ở bài (`status=publish`, `future`, tạo bài, kèm loại ảnh), sửa ảnh có sẵn, ability, `GET`; ảnh thiếu `Content-Type`, chỉ có tên file, hai header loại, kèm `json`, dạng form: chặn, 0 request |
| `test_than_byte_tai_anh_dung_loai_van_gui_duoc` (5 loại ảnh) | Đối chứng: tải ảnh đúng loại vẫn gửi nguyên byte |

### Hàm dùng chung đã sửa: nơi gọi, test cũ

| Chỗ sửa | Nơi gọi (grep `seo_app/`, `app/`, `tests/`, cả nhập muộn) | Ảnh hưởng |
|---|---|---|
| `_is_plain_request`: luật `data` | `_request` (mọi hàm client), `release_draft` | Chỉ `_post_media` gửi `data` (đúng `POST /wp/v2/media`, `Content-Type` ảnh, `Content-Disposition`): không đổi. Test cũ gửi `data` qua `_request`: chỉ `test_soi_loi_t060.py::test_loai_than_khong_dung_loai_anh_bi_chan` (đã mong bị chặn, vẫn qua) |
| `_release_check` đổi kiểu trả về | Chỉ `release_draft` | Không test nào gọi thẳng |
| `release_draft` giành mã sớm | Chưa có nơi gọi ngoài test (T-102 sẽ gọi) | Câu báo giữ nguyên; ca cũ «bị chặn vì giờ thì bài vẫn của client» (`test_bi_chan_vi_gio_thi_bai_van_la_cua_client`, ca đối chứng của Lá Chắn, Soi Lỗi) vẫn qua |

### Bằng chứng (lượt 2)

```
$ uv run pytest -q -p no:cacheprovider -rX tests/test_la_chan_t099.py tests/test_soi_loi_t099.py \
      tests/test_wordpress_release.py tests/test_publish_schedule.py      # trước khi gỡ dấu
6 failed (XPASS(strict): 1 LC-T099-1, 5 SL-T099-1), 469 passed

$ uv run pytest -q -p no:cacheprovider tests/test_wordpress_release.py  # sau khi gỡ dấu, thêm ca
247 passed in 16.93s

$ uv run pytest -q -p no:cacheprovider <58 file test client WordPress>   # 30/10 10:34 → 11:22
8255 passed, 1 skipped in 2875.72s (0:47:55)                          # máy đang chạy toàn bộ test

$ uv run ruff check .
All checks passed!
```

58 file chọn lọc: mọi file test có `upload_media`, `_post_media`, `create_draft_with_images`, `/wp/v2/media`, `release_draft`, `_is_plain_request`, `_request(`, `send_draft`, `fake_wp`, `FakeWordPress` (client WordPress, tải ảnh, gửi nháp T-054/T-086/T-089, ghi SEO T-042/T-059, T-060, T-085, T-088, T-091, T-099 cùng hai file kiểm của Soi Lỗi, Lá Chắn). Trên nhánh `team/T-099` (chưa gộp `main` `3164a80`, theo dặn).

Thử «làm hỏng» code (sửa tạm, chạy `test_wordpress_release.py`, `test_la_chan_t099.py`, `test_soi_loi_t099.py`, trả nguyên file; script so lại: giống hệt):

| Làm hỏng | Số test đỏ |
|---|---|
| Không trả mã khi bị chặn trước lệnh chuyển | 30 |
| Trả mã cả khi website báo không còn nháp | 19 |
| Bỏ luật `data` | 16 |
| Nhận `data` ở mọi đường `POST` (bỏ điều kiện `/wp/v2/media`) | 2 |
| Nhận hai header `Content-Type` | 1 |

### Còn lại

- Ghi nhận G1 (so `modified_gmt`, LC-T094-23 «nên»), G2–G6 của Soi Lỗi: không thuộc lượt này, giữ như biên bản.
- Lời dặn T-102 của Lá Chắn (một lần `release_draft` mỗi lần bấm, trên chính client vừa tạo nháp, không giữ client chung) vẫn giữ: giành mã một bước chỉ là lớp phòng thêm.

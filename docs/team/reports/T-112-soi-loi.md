# Báo cáo T-112 · Chuẩn bị bật Hẹn giờ / Đăng ngay · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | T-112 `T-112-chuan-bi-bat-hen-gio-dang-ngay.md` (đọc ở checkout chính; nhánh này không chứa phiếu) |
| Nhánh | `team/T-112`, đầu nhánh `ef582ff` (Họa Sĩ lượt 2: đã gộp `main` `7485b94` và `team/T-115` `a7572f7`); thử gộp với `main` cục bộ `33dd87f` (có T-115, T-117, T-119, biên bản T-116) |
| Ngày nộp | 2026-11-02 |
| Kết quả | Hoàn thành (kiểm rút gọn). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn được. 0 Nghiêm trọng, 0 Cao, **1 Trung bình** (SL-T112-1), **2 Thấp** (SL-T112-2, SL-T112-3: README). **Không lỗi nào phải sửa trước Lá Chắn hay trước khi gộp** (công tắc vẫn mặc định tắt); cả ba sửa **trước khi bật công tắc**. Gộp `main` cục bộ `33dd87f` (và trước đó `b953e5e`): không xung đột; test chọn lọc 0 hỏng |

## Tóm tắt (cho chủ dự án)

- **Công tắc Hẹn giờ / Đăng ngay ở Cài đặt chạy đúng.** Mặc định tắt; phải tick «Tôi hiểu…» rồi mới bật được; bỏ tick là tắt; tải lại trang là tắt. Tôi thử bật bằng các đường khác (gõ thêm vào địa chỉ trang, gán thẳng giá trị lạ; file nháp sửa tay thì Họa Sĩ đã thử): không đường nào bật được.
- **Đăng ngay giữ bài là nháp khi ảnh đại diện hay SEO chưa lên** (cả khi website trả lời lạ lệnh đặt ảnh đại diện, hay lệnh ghi SEO lỗi bất ngờ); dòng kế hoạch ghi đúng; lệnh không rõ kết quả thì không ghi.
- **1 lỗi cần sửa trước khi bật Đăng ngay (Trung bình):** bật «Ghi SEO lên website» mà **tiêu đề hoặc mô tả SEO đang bị «Chặn»** ở bước SEO, app chỉ ghi phần còn lại rồi vẫn **đăng công khai** bài, với tiêu đề (hay mô tả) SEO mặc định. App có báo trước một dòng nhỏ, nhưng nút gửi vẫn bấm được. Thiết kế đã chốt: Đăng ngay khi SEO chưa ghi lên website là **Chặn**.
- **2 chỗ README chưa đúng (Thấp):**
  1. README nói Hẹn giờ «vẫn hẹn» khi ảnh đại diện chưa lên; thật ra (sau T-115) app **không** hẹn giờ trường hợp này, bài vẫn là nháp.
  2. README nói tắt công tắc «ở tab khác» thì tab đang mở không gửi được; thật ra **mỗi tab có công tắc riêng**: tắt ở tab này không tắt tab kia.
- **Việc của bạn:** không có. Khi bật công tắc: nhớ bật/tắt **từng tab** (mỗi tab trình duyệt một công tắc).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t112.py` | Mới: 18 ca (14 qua, 4 `xfail(strict=True)`: SL-T112-1 × 2, SL-T112-2, SL-T112-3). Mượn khung trang Soạn bài, Cài đặt và WordPress giả (`live`) của `test_app_images`, `test_app_pages`, `test_t102_publish` như file T-102 của tôi; có fixture tự động trỏ cache danh sách bài đã đăng sang thư mục tạm (không tạo `data/site_index.sqlite`) |
| `docs/team/reports/T-112-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác, không commit file phiếu, không gọi website thật.

## Kiểm theo yêu cầu

### 1. Công tắc không bật được bằng đường nào khác, tắt đúng khi tải lại

Họa Sĩ đã có ca: mặc định tắt, bật cần tick, bỏ tick là tắt, phiên mới là tắt và không ghi file, tham số địa chỉ ở trang Cài đặt, file nháp sửa tay. Tôi thêm:

| Thử | Kết quả |
|---|---|
| Tham số địa chỉ ở **chính trang Soạn bài** (`_release_enabled=true`, `release_enabled=1`, `release_ack`, `release_toggle`, `_wp_mode=Đăng ngay`/`Hẹn giờ`, `_wp_confirm=true`) | Không bật; chỉ có câu «Hẹn giờ và Đăng ngay đang **tắt**», không nút gửi (2 ca) |
| Giá trị «gần đúng» của công tắc trong phiên: `"true"`, `"True"`, `1`, `1.0`, `[True]`, `{"on": True}` | Không bật (bước Xuất bản xét `is True`) (6 ca) |
| Gán thẳng `release_ack=True`, `release_toggle=True` vào phiên (không qua bấm, không chạy hàm `on_change`) | Trang Cài đặt dựng lại hai ô theo công tắc thật: nút bật về tắt, công tắc vẫn tắt, Soạn bài không có nút gửi |
| Nút bật đang khóa (chưa tick «Tôi hiểu…») | AppTest không cho bấm (như trình duyệt). Đọc mã: hàm `_release_toggle_changed` (`settings.py:723`) còn đòi ô «Tôi hiểu…», nên dù trình duyệt bị sửa để gửi giá trị bật thì công tắc vẫn tắt (lớp chặn đôi) |
| Hai tab (hai phiên) | Mỗi phiên một công tắc: bật ở tab A không bật tab B; **tắt ở tab B không tắt tab A** (đúng thiết kế «chỉ trong phiên»; README nói ngược: SL-T112-3) |

### 2. Lối hỏng của Đăng ngay / Hẹn giờ

| Lối hỏng | Đăng ngay | Hẹn giờ | Ca |
|---|---|---|---|
| Ảnh đại diện lỗi (500) | Giữ nháp, câu `MSG_PUBLISH_HELD` nêu «ảnh đại diện» | T-115 từ chối (client «không biết» giờ sửa): bài vẫn là nháp, không khóa «có thể đã gửi» | Họa Sĩ |
| Ảnh đại diện **trả lời lạ** (200 nói về bài khác) | Giữ nháp, câu nêu «ảnh đại diện» | (như trên: T-115 lượt 2 coi là «không biết») | Soi Lỗi |
| SEO không ghi được (SiteSEO chưa cho, 5xx) | Giữ nháp, câu nêu SEO | Vẫn hẹn giờ, cảnh báo `MSG_SCHEDULE_MISSING` | Họa Sĩ |
| Ghi SEO **ném lỗi lạ** | Giữ nháp, câu nêu SEO, không lộ chữ lỗi | | Soi Lỗi |
| Ghi SEO qua Abilities xong mà hỏi lại bài còn là nháp không được | Giữ nháp, câu nêu SEO | | Soi Lỗi |
| **Tiêu đề / mô tả SEO đang «Chặn»** (bị bỏ khỏi lệnh ghi) | **Vẫn đăng** với tiêu đề/mô tả SEO mặc định | Vẫn hẹn giờ, có câu «Không ghi …» | **SL-T112-1** |
| Bài bị sửa ngoài app (`modified_gmt` khác) | T-115 từ chối, bài vẫn là nháp | như Đăng ngay | Họa Sĩ (3 ca), T-115 của tôi |
| Mạng, website trả lạ ở lệnh chuyển | Khóa «có thể đã gửi», không tự gửi lại | như Đăng ngay | T-102 |
| Công tắc tắt đúng lúc bấm | Không gửi gì (0 lệnh) | như Đăng ngay | Họa Sĩ |
| Đối chứng: đủ ảnh đại diện, SEO | Đăng | Hẹn giờ | Họa Sĩ, Soi Lỗi |

Khóa gửi trùng: Đăng ngay bị giữ thì nháp ghi «đã gửi nháp, chưa đăng» (`released=False`, không «không rõ»); ô gửi lại nói đúng hình thức (`AGAIN_LABELS`). Đúng (ca của Họa Sĩ, T-086, T-089 qua).

### 3. Dòng kế hoạch

`record_plan` (`write.py:3654`): lệnh chuyển không rõ kết quả (mà không phải «hẹn giờ thành đăng ngay») → không ghi gì, câu `MSG_PLAN_RELEASE_UNSURE`; Đăng ngay bị giữ, T-115 từ chối, website từ chối → «Đã gửi nháp» kèm mã bài; hẹn giờ xong → «Đã hẹn giờ» kèm giờ; đăng xong hay hẹn giờ mà website đăng ngay → «Đã đăng». Đúng (ca của Họa Sĩ trong `test_t112_release_rules.py` qua).

### 4. README mục 11

Đối chiếu với code trên nhánh đã gộp T-115:

- Đúng: công tắc ở Cài đặt, tick «Tôi hiểu…», chỉ giữ trong lần mở app, F5 là tắt; Đăng ngay phải bật «Ghi SEO lên website»; Đăng ngay thiếu phần nào thì giữ nháp (trừ SL-T112-1); kết quả không rõ thì khóa, không ghi dòng kế hoạch; ô gửi lại ba nhãn.
- **Sai (SL-T112-2):** `README.md:487` «**Hẹn giờ thì vẫn hẹn**» khi ảnh đại diện hay SEO chưa lên: sau T-115, ảnh đại diện hỏng thì client không hẹn giờ.
- **Sai (SL-T112-3):** `README.md:459` «Công tắc bị tắt trong lúc bạn đang ở bước Xuất bản (ví dụ ở tab khác) thì bấm gửi … không gửi gì»: mỗi tab một phiên, tắt ở tab khác không tắt tab đang mở.
- Còn thiếu (Thư Ký đã nêu, ghi nhận G1): ca «bài bị sửa trong trang quản trị sau khi app ghi thì không hẹn giờ/đăng» (T-115) chưa có trong README.

### 5. Không lùi; gộp thử

- **Cây nhánh `ef582ff`** + file test của tôi, 46 file chọn lọc (T-112, T-102, T-115, T-099, T-110, T-113/T-109, «Gửi nháp» T-086/T-089, trang Cài đặt và các trang, SEO T-041/T-059, các file ghim `_fields`), 2 phần: **2.581 passed, 13 xfailed, 0 failed** (1.413 + 1.168; 13 xfail: 4 của tôi, 9 LC-T113-2 có sẵn). Hai lượt này chạy file của tôi trước khi thêm ca Abilities; ca đó chạy riêng: qua.
- **Gộp thử `main` cục bộ `b953e5e`** (T-117: thư mục `data/` là liên kết, `seo_app/images/data_dir.py`, `process.py`, `image_tags.py`; biên bản T-116): **không xung đột** (cây `6a2d1fd`). 49 file (46 file trên cùng `test_t117_data_dir_links.py`, `test_soi_loi_t117.py`, `test_la_chan_t116_nhom1.py`), 2 phần: **2.606 passed, 16 xfailed, 0 failed** (1.413 + 1.193; thêm 3 xfail SL-T117-1 có sẵn).
- **`main` cục bộ nay là `33dd87f`** (thêm T-115 đã gộp chính thức, T-119 tài liệu, biên bản T-115 Lá Chắn): gộp **không xung đột** (cây `1c06933`). Cây này khác cây gộp với `b953e5e` chỉ ở tài liệu (`README.md` mục 14, `docs/team/security.md`, hai biên bản, ghi chú trong `pyproject.toml`), không đổi code hay test, nên kết quả trên vẫn đúng cho code. Chạy lại 5 file trên cây này (`test_soi_loi_t112.py` bản cuối, `test_t112_release_rules.py`, `test_t112_settings_switch.py`, `test_soi_loi_t110.py`, `test_soi_loi_t115.py`): **429 passed, 4 xfailed, 0 failed**. Ca T-110 của tôi (ghim `_fields`) Họa Sĩ đã thêm đúng `,modified_gmt` vào 2 chuỗi khi gộp T-115 (Chỉ Huy duyệt 02/11 13:00), đúng đề xuất của tôi ở T-115.
- Lần này mỗi lượt chạy qua script kiểm trước danh sách có thật, không rỗng, mọi file có trong bản sao (sai thì dừng, không chạy); dòng đầu mỗi kết quả ghi «Chạy N file chọn lọc» (21, 25, 21, 28).

### Đột biến

12 lượt cho 11 đột biến (script `mutate112.py`), mỗi lượt chạy `tests/test_soi_loi_t112.py`, `tests/test_t112_release_rules.py`, `tests/test_t112_settings_switch.py`, dừng ở ca hỏng đầu: **10/11 bị bắt**, 1 sống sót là lớp chặn đôi. (Máy tắt giữa lượt đầu, sau P5; bản sao đột biến còn để sót P6 nên tôi dựng lại bản sao sạch rồi chạy lại P5–P11.)

| Đột biến | Ca bắt đầu tiên |
|---|---|
| P1 bỏ luật giữ nháp của Đăng ngay | `test_soi_loi_t112.py::test_anh_dai_dien_tra_loi_la_thi_khong_dang` |
| P2 bỏ phần ảnh đại diện | như trên |
| P3 bỏ phần SEO | `test_soi_loi_t112.py::test_ghi_seo_nem_loi_la_thi_khong_dang` |
| P4 SEO luôn coi là đã lên | như trên |
| P5 hỏi lại bài sau Abilities lỗi vẫn coi SEO đã lên | `test_soi_loi_t112.py::test_abilities_hoi_lai_bai_loi_thi_khong_dang` (lượt đầu sống sót: chưa ca nào đi đường Abilities; tôi thêm ca này) |
| P6 bỏ kiểm công tắc lúc bấm (G2) | `test_t112_release_rules.py::test_switch_turned_off_at_click_sends_nothing` (Họa Sĩ) |
| P7 lệnh chuyển không rõ vẫn ghi dòng kế hoạch (G1) | `test_t112_release_rules.py::test_unsure_release_does_not_write_plan_status` (Họa Sĩ) |
| P8 công tắc nhận giá trị gần đúng (`bool` thay `is True`) | `test_soi_loi_t112.py::test_gia_tri_gan_dung_cua_cong_tac_khong_bat[chu-true]` |
| P9 nút bật không đòi «Tôi hiểu…» | sống sót: nút bật đã bị khóa khi chưa tick, AppTest (như trình duyệt) không cho bấm nút khóa; đây là lớp chặn thứ hai |
| P10 không dựng lại nút bật theo công tắc thật | `test_soi_loi_t112.py::test_gan_thang_o_tick_va_nut_khong_qua_bam_khong_bat` |
| P11 bỏ tick «Tôi hiểu…» không tắt | `test_t112_settings_switch.py::test_untick_ack_turns_off` (Họa Sĩ) |

## Lỗi tìm ra

### SL-T112-1 · Trung bình · Đăng ngay vẫn đăng khi tiêu đề hay mô tả SEO đang «Chặn»

- **Chỗ:** `app/views/write.py`: `seo_request` (`:2731`) bỏ trường đang «Chặn» khỏi lệnh ghi (`skipped`); `write_seo` (`:2812`) đặt `seo_ok = seo.written` (client ghi được **một phần** là `written=True`); `release_missing` (`:3766`) chỉ xét `seo_ok`. Bộ dựng (`seo_app/publish/render.py:628`) chỉ Chặn Đăng ngay khi **tắt** «Ghi SEO lên website»; danh sách «Kiểm tra trước khi gửi» (dòng SEO «chưa dùng được») chỉ hiển thị, không khóa nút.
- **Thử:** bật «Ghi SEO lên website», tiêu đề SEO dạng shortcode (`Sửa cổng [gallery] inox tại nhà`, bước SEO báo «Chặn»), Đăng ngay, tick xác nhận, gửi. App hiện chú thích «Sẽ không ghi Tiêu đề SEO…», nút gửi vẫn mở; lệnh ghi SEO chỉ mang mô tả, từ khóa; **lệnh đăng đi** (`{"status": "publish"}`), trang báo «Đã đăng bài công khai trên website». Mô tả «Chặn» cũng vậy.
- **Hậu quả:** bài lên công khai với tiêu đề (hay mô tả) SEO mặc định của SiteSEO: đúng điều LC-T094-39 và thiết kế T-094 mục 3 («Đăng ngay khi SEO chưa ghi lên website: Chặn, vì bài lên công khai với tiêu đề SEO mặc định mà không còn bước nào để sửa trước») và yêu cầu 1 của phiếu muốn chặn. Có báo trước (một dòng chú thích, dòng ⚠️ trong khung kiểm), nên không nặng hơn SL-T102-1; cùng mức **Trung bình**: không chặn gộp (công tắc tắt), **sửa trước khi bật công tắc**.
- **Test:** `test_sl_t112_1_dang_ngay_khi_truong_seo_dang_chan_thi_khong_dang` (2 xfail: tiêu đề, mô tả); đối chứng `test_doi_chung_seo_du_thi_dang` qua.
- **Gợi ý:** Đăng ngay có tiêu đề hay mô tả SEO bị «Chặn» thì Chặn ngay ở màn hình xác nhận (bộ dựng thêm dòng Chặn, nút gửi khóa), hoặc ít nhất `release_missing` coi `skipped` (tiêu đề, mô tả) là SEO chưa lên. Từ khóa chính bị bỏ thì không hiện công khai, chỉ cần cảnh báo.

### SL-T112-2 · Thấp · README nói Hẹn giờ vẫn hẹn khi ảnh đại diện chưa lên

- **Chỗ:** `README.md:487` («**Hẹn giờ thì vẫn hẹn**, kèm cảnh báo «Bài đã hẹn giờ nhưng … chưa lên website lúc gửi…»», dưới tiêu đề «Ảnh đại diện hay SEO chưa lên kịp»).
- **Thực tế** (nhánh đã gộp T-115): lệnh đặt ảnh đại diện lỗi thì client không biết chắc giờ sửa bài nên từ chối lệnh chuyển: bài vẫn là nháp, câu «… Chưa hẹn giờ, chưa đăng: bài vẫn là nháp…» (ca `test_schedule_with_featured_failure_is_refused_by_client` của Họa Sĩ). Chỉ SEO thiếu thì mới «vẫn hẹn, cảnh báo».
- **Test:** `test_sl_t112_2_readme_hen_gio_anh_dai_dien_hong_khong_hen` (xfail: gạch đầu dòng Hẹn giờ phải nói riêng ca ảnh đại diện).
- **Gợi ý:** sửa gạch đầu dòng: Hẹn giờ mà **SEO** chưa lên thì vẫn hẹn, cảnh báo; **ảnh đại diện** chưa lên thì không hẹn giờ, bài vẫn là nháp. Cùng lúc thêm ca T-115 (G1).

### SL-T112-3 · Thấp · README nói tắt công tắc ở tab khác thì tab đang mở không gửi được

- **Chỗ:** `README.md:459`.
- **Thực tế:** công tắc chỉ nằm trong phiên (`st.session_state`, Chỉ Huy chọn A), mỗi tab trình duyệt là một phiên: tắt ở tab B không đổi công tắc của tab A, tab A vẫn gửi Hẹn giờ/Đăng ngay được (ca `test_moi_phien_mot_cong_tac_tat_o_tab_khac_khong_tat_tab_nay`). Kiểm lúc bấm (G2) chỉ có tác dụng trong cùng phiên. Báo cáo Họa Sĩ mục 2.4 («tab khác, Cài đặt») cũng viết vậy.
- **Hậu quả:** chủ dự án có thể tưởng tắt một chỗ là tắt hết, để quên một tab còn bật. Vẫn phải chọn hình thức, xem lại, tick xác nhận rồi bấm gửi mới đi, nên **Thấp**.
- **Test:** `test_sl_t112_3_readme_khong_noi_tat_o_tab_khac_la_tat_tab_nay` (xfail).
- **Gợi ý:** README: «Mỗi tab trình duyệt có công tắc riêng: bật ở tab này không bật tab khác, tắt ở tab khác không tắt tab này. Xong việc thì tắt ở chính tab đó hoặc tải lại trang.»; bỏ «ví dụ ở tab khác».

## Ghi nhận (không tính lỗi)

- **G1 · README chưa có ca T-115** (Thư Ký đã nêu): bài bị sửa trong trang quản trị sau khi app ghi thì app không hẹn giờ/đăng, câu `_RELEASE_CHANGED`. Câu «Website từ chối rõ ràng…» chưa đúng hẳn (app từ chối, không phải website). Nên thêm khi sửa SL-T112-2.
- **G2 · `data/site_index.sqlite` sẵn có trong worktree `wt-T-112`** (tạo lúc 31/10 09:46, trước khi dọn `test_soi_loi_t102.py` ở T-115; bị `.gitignore` bỏ qua): để nguyên, không phải file tôi tạo; file test của tôi không tạo thêm.

## Lệnh đã chạy

- `pytest tests/test_soi_loi_t112.py`: 14 passed, 4 xfailed; `--runxfail`: SL-T112-1 hỏng ở «lệnh đăng đã đi» (`[{'status': 'publish'}] == []`), SL-T112-2 ở «gạch đầu dòng Hẹn giờ không nói ảnh đại diện», SL-T112-3 ở «câu còn "tab khác"».
- Thử tạm (không commit): Đăng ngay với tiêu đề SEO «Chặn»: «Đã đăng bài công khai trên website.»
- Cây nhánh, 46 file: 2.581 passed, 13 xfailed, 0 failed. Cây gộp `main` `b953e5e`, 49 file: 2.606 passed, 16 xfailed, 0 failed. Cây gộp `main` `33dd87f`, 5 file: 429 passed, 4 xfailed, 0 failed. Mọi lượt qua `run_list.sh` (kiểm danh sách trước khi chạy).
- Đột biến: 10/11 bị bắt, 1 lớp chặn đôi.
- `uv run ruff check .`: sạch. `detect-secrets` (`PYTHONUTF8=1`) trên file test, báo cáo: sạch (có file mồi tiếng Việt trong cùng lần quét: chỉ mồi bị báo).
- Script: thư mục ghi chú chung `T-112-soi-loi-scripts/` (`run_list.sh`, `mutate112.py`).

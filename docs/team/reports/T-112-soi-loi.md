# Báo cáo T-112 · Chuẩn bị bật Hẹn giờ / Đăng ngay · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | T-112 `T-112-chuan-bi-bat-hen-gio-dang-ngay.md` (đọc ở checkout chính; nhánh này không chứa phiếu) |
| Nhánh | `team/T-112`, đầu nhánh `ef582ff` (Họa Sĩ lượt 2: đã gộp `main` `7485b94` và `team/T-115` `a7572f7`); thử gộp với `main` cục bộ `33dd87f` (có T-115, T-117, T-119, biên bản T-116) |
| Ngày nộp | 2026-11-02 (lượt 3: 2026-11-03, mục «Lượt 3» cuối báo cáo) |
| Kết quả | Hoàn thành (kiểm rút gọn). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn được. 0 Nghiêm trọng, 0 Cao, **1 Trung bình** (SL-T112-1), **2 Thấp** (SL-T112-2, SL-T112-3: README). **Không lỗi nào phải sửa trước Lá Chắn hay trước khi gộp** (công tắc vẫn mặc định tắt); cả ba sửa **trước khi bật công tắc**. Gộp `main` cục bộ `33dd87f` (và trước đó `b953e5e`): không xung đột; test chọn lọc 0 hỏng. **Lượt 3 (03/11): ĐẠT CÓ ĐIỀU KIỆN**: SL-T112-1, -2, -3 đóng; 1 Thấp mới SL-T112-4 (README, sửa trước khi bật công tắc); gộp thử `main` `29499dd` không xung đột, 641 qua, 0 hỏng |

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

## Lượt 3 (2026-11-03)

| Mục | Nội dung |
|---|---|
| Nhánh | `team/T-112`, đầu nhánh `746ba9d`: Họa Sĩ lượt 3 (`58d5326` sửa SL-T112-1, `3f29c74` báo cáo mục 9), Thư Ký lượt 2 (`746ba9d` README, gỡ 3 `xfail` README); `main` `33dd87f` đã gộp ở `df4ba4a`. Thử gộp với `main` cục bộ `29499dd` (thêm T-118, T-073): **không xung đột**, cây `b76814c` |
| Kết quả | **ĐẠT CÓ ĐIỀU KIỆN**, chuyển Lá Chắn được. **SL-T112-1 (Trung bình) đóng**, **SL-T112-3 đóng**, **SL-T112-2 đóng** (đúng ca tôi nêu). Lỗi mới: **1 Thấp, SL-T112-4** (README: câu mới của SL-T112-2 làm đúng theo gợi ý lượt 1 của tôi, mà gợi ý đó chia luật Hẹn giờ chưa đúng). 0 lỗi code. Không chặn gộp (công tắc tắt); SL-T112-4 sửa **trước khi bật công tắc**. R5 đúng phạm vi duyệt |

### Tóm tắt (cho chủ dự án)

- **Lỗi Trung bình của lượt trước đã sửa đúng.** Bật «Ghi SEO lên website» mà tiêu đề hay mô tả SEO đang trống hoặc bị «Chặn» ở bước SEO thì nút **Đăng ngay khóa** ngay ở màn hình xem lại, kèm dòng nói rõ trường nào. Tôi thử 13 kiểu chữ lạ (ký tự điều khiển, ký tự vô hình, chỉ có dấu cách, thẻ HTML, «%%»…), sửa SEO sau khi đã tick, hai tab mở cùng một bài, bấm lọt qua nút đang khóa: **không lần nào bài bị đăng**. Hẹn giờ thì chỉ cảnh báo (còn sửa được trước giờ đăng). «Gửi nháp» như cũ.
- **README** đã sửa đúng 2 chỗ của lượt trước (công tắc theo từng tab; ca bài bị sửa ngoài app). Còn **1 chỗ nhỏ (Thấp)**, một phần do gợi ý của tôi lượt trước chưa chính xác: README nói «Hẹn giờ vẫn hẹn khi chỉ thiếu SEO; thiếu ảnh đại diện thì không hẹn». Thật ra app **không hẹn giờ khi một lệnh ghi bị lỗi giữa chừng** (ảnh đại diện, hay SEO lúc ghi qua đường dự phòng), và **vẫn hẹn, kèm cảnh báo, khi phần thiếu chưa hề được ghi**. Bài không bao giờ lên công khai sai; chỉ là câu báo bạn thấy có thể khác README. Sửa README trước khi bật công tắc.
- **Việc của bạn:** không có.

### Đã thay đổi (lượt 3)

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t112.py` | Thêm mục 4 «lượt 3»: **30 ca** (29 qua, 1 `xfail(strict=True)` SL-T112-4). Không đổi ca cũ (2 ca SL-T112-1, 2 ca README do Họa Sĩ, Thư Ký đổi theo R5 đã duyệt, xem mục 2). Cả file: 48 ca, 47 qua, 1 xfail |
| `docs/team/reports/T-112-soi-loi.md` | Mục «Lượt 3» này |

Không sửa code ứng dụng, không sửa test của agent khác, không commit file phiếu, không gọi website thật.

### 1. SL-T112-1 đóng thật

Đọc mã: `seo_left_out`/`seo_notices` (`app/views/write.py:3036-3056`) xét **đúng chữ SEO trong gói** (`built.seo`, cùng mã băm với ô tick, cùng chữ `seo_holder` đưa cho lệnh ghi); `publish_panel` thêm dòng vào `notices` trước `review_panel`, `allowed` tắt khi có dòng Chặn; cú bấm lọt bị `if clicked and allowed` chặn; chốt hai `release_missing` (`:3801`) xét trường bị bỏ khỏi lệnh ghi.

| Thử | Kết quả |
|---|---|
| **Đối chứng cú bấm lọt** (mới): cùng cách giả `st.button` như ca của Họa Sĩ và của tôi, nhưng nút **mở** (SEO hợp lệ) | Lần chạy sau **gửi thật** (lệnh ghi SEO, lệnh đăng): cách giả tới được nhánh gửi, nên «không gửi gì» ở các ca nút khóa là có nghĩa |
| 13 kiểu chữ «Chặn»: tiêu đề `%%`, `&#37;`, `<b>…</b>`, ký tự điều khiển, ký tự riêng (U+E000), ngoặc vuông toàn khổ, chỉ dấu cách, chỉ ký tự vô hình (U+200B U+2060), Hangul filler (U+3164); mô tả: thẻ HTML, ký tự điều khiển, ký tự riêng, chỉ ký tự vô hình | Bước SEO báo «Chặn» (`siteseo_copy` trả `None`, đúng câu «đang trống hoặc báo «Chặn» ở bước SEO»); Đăng ngay có dòng Chặn **nêu đúng trường**, nút khóa; cú bấm lọt: **0 lệnh ghi** (không cả tạo nháp), nháp không có trạng thái gửi |
| Dò thêm 29 kiểu chữ × 2 trường bằng hàm (`probe_seo_text.py`): có chữ nào bước SEO cho qua mà client **bỏ im lặng** (lệnh ghi bỏ trường, `release_missing` không thấy) không | **Không có.** Chữ bước SEO cho qua thì client ghi được, trừ tiêu đề trên 200 ký tự: client từ chối **cả** lệnh ghi (xem G3), không bỏ im lặng |
| Sửa SEO **sau khi tick**: xóa mô tả | Bỏ tick, báo «bỏ tick», có dòng Chặn «mô tả SEO»; tick lại vẫn khóa; bấm lọt không gửi |
| Sửa ngược: tiêu đề «Chặn» → hợp lệ | Hết dòng Chặn; tick → nút mở; gửi ghi **đúng chữ mới**, đăng |
| **Hai tab** mở cùng một bài: tab A tiêu đề «Chặn», tab B hợp lệ; cùng một cú bấm lọt cho cả hai | Tab A không gửi gì; tab B gửi đúng chữ của tab B (đối chứng ngay trong ca). Chữ SEO, ô tick, dòng Chặn là của từng phiên |
| Hẹn giờ: chỉ mô tả trống; cả hai «Chặn» | Màn hình xác nhận chỉ **Cảnh báo** nêu đúng trường, không Chặn; gửi thì vẫn hẹn đúng giờ; kết quả cảnh báo «Bài đã hẹn giờ nhưng mô tả SEO / tiêu đề SEO, mô tả SEO chưa lên…» (chốt hai) |
| Tắt «Ghi SEO», tiêu đề và mô tả trống: Hẹn giờ, Đăng ngay | Không thêm dòng mới; Đăng ngay vẫn là dòng Chặn cũ của bộ dựng «SEO chưa ghi lên website» |
| «Gửi nháp», bật «Ghi SEO», tiêu đề «Chặn» | Không dòng mới; gửi nháp được; lệnh ghi SEO bỏ tiêu đề, ghi mô tả; không lệnh chuyển trạng thái |
| Chốt hai (`release_missing`), gọi thẳng | Thiếu tiêu đề/mô tả/cả hai nêu đúng tên; từ khóa chính trống không tính; `seo_ok` sai thì chỉ «SEO (…)» (không lặp); ảnh đại diện + tiêu đề nêu cả hai; yêu cầu SEO thiếu khóa `fields` thì coi cả hai là thiếu (hướng an toàn) |
| `seo_notices` gọi thẳng | Tắt «Ghi SEO»: rỗng; Nháp: rỗng; đủ chữ: rỗng; Đăng ngay: một dòng **Chặn** nêu cả hai; Hẹn giờ: **Cảnh báo** |
| Họa Sĩ đã có: tiêu đề/mô tả «Chặn», trống (Đăng ngay, 4 ca); cả hai trường; Hẹn giờ tiêu đề «Chặn» (chốt hai, ghi phần còn lại); chỉ từ khóa chính hỏng thì vẫn đăng | Chạy lại: qua |

### 2. R5 đúng phạm vi duyệt (Chỉ Huy 03/11 12:45)

| Ca | Diff | Đối chiếu |
|---|---|---|
| (a) `test_t102_publish::test_publish_now_with_seo_written` | +1 dòng chú thích, +4 dòng `session_state` (tiêu đề, mô tả SEO hợp lệ) | Đúng (a); mọi kiểm giữ nguyên |
| (a) `test_la_chan_t102::_publish_now` (3 ca LC-T102-1) | như trên | Đúng (a) |
| (a) `test_soi_loi_t102::test_sl_t102_1_…` (3 ca của tôi) | như trên | Đúng (a); lại đi tới lệnh ghi SEO hỏng, giữ ý «ghi SEO lỗi thì không đăng» |
| (a) `test_soi_loi_t102::test_sua_sau_khi_tick_thi_bo_tick` `[tieu-de]`, `[slug]` (của tôi) | như trên | Ca Đăng ngay + Ghi SEO cũ nên thuộc (a). Không đổi thì ca vẫn qua nhưng nút **đã khóa sẵn** vì dòng Chặn, mất ý; thêm 4 dòng thì nút khóa lại là do bỏ tick (ca đối chứng của tôi xác nhận nút mở khi SEO hợp lệ). Giữ ý |
| (b) `test_soi_loi_t112::test_sl_t112_1_…` `[tieu-de-chan]`, `[mo-ta-chan]` (của tôi) | Gỡ `xfail`; thay «nút mở rồi bấm» bằng: dòng Chặn nêu đúng trường + nút khóa + cú bấm lọt: không lệnh ghi SEO, không lệnh ghi nào, `release_bodies == []`, nháp không có trạng thái gửi | Đúng (b), **mạnh hơn** bản cũ; ý «Đăng ngay khi trường SEO «Chặn» thì không đăng» giữ nguyên. Ý phụ «trường Chặn không ghi, phần còn lại vẫn ghi» nay nằm ở ca Hẹn giờ của Họa Sĩ và ca «Gửi nháp» của tôi |
| Gỡ 3 `xfail` README (Thư Ký): SL-T112-2, SL-T112-3, SL-T108-1 | Chỉ xóa dòng dấu (`0 thêm, 4 + 11 xóa`) | Đúng duyệt; 3 ca qua; dấu `xfail` của SL-T106-1 (code, không phải README) còn nguyên (đọc file; lượt này không chạy lại ca đó vì ngoài 4 phiếu được chạy, lần chạy của Thư Ký: 2 xfailed) |
| `test_t112_release_rules.py` (ca của chính phiếu, chưa lên `main`): `send(…, seo_write=True)` và `test_held_publish_writes_draft_sent_to_plan` thêm chữ SEO hợp lệ | Đọc từng ca dùng `seo_write=True`: 4 ca Đăng ngay, 1 ca Hẹn giờ, 1 ca T-115 (tham số, chỉ bật khi Đăng ngay), cộng ca dòng kế hoạch | Ý giữ nguyên (SEO có chữ; lệnh ghi hỏng hay được). Ca Hẹn giờ `test_schedule_goes_on_but_warns_what_is_missing` vẫn chỉ cảnh báo «SEO (…)» như trước |

Không ca nào bị tắt, bỏ qua hay nới kiểm.

### 3. README mục 11 (Thư Ký lượt 2)

| README nói | Đối chiếu | |
|---|---|---|
| Dòng 7: trang Kết nối «tạo thử bài nháp chữ» (SL-T108-1) | `app/views/wordpress.py` mục 3; ca `test_sl_t108_1_…` qua | Đúng |
| Công tắc «chỉ giữ trong tab trình duyệt đó, trong lần mở app đó»; «Mỗi tab trình duyệt có công tắc riêng… tắt ở tab khác **không** tắt tab này» (SL-T112-3) | Ca `test_moi_phien_mot_cong_tac_…` | Đúng; SL-T112-3 đóng |
| «Công tắc bị tắt (ở Cài đặt của cùng tab, hay tải lại trang) thì bước Xuất bản chỉ còn gửi Nháp; … bấm lọt … không gửi gì, báo «Chưa gửi gì lên website…»» | `publish_panel` (tắt: chỉ câu `MSG_RELEASE_OFF`, không nút gửi), G2 trong `send_draft`, câu có trong mã | Đúng |
| Bỏ «(kể cả ở tab khác)» ở dòng «Sửa gì sau khi tick» | `seo_write` chỉ trong phiên, không lưu vào nháp (`seo_app/storage/` không có) | Đúng |
| Hẹn giờ/Đăng ngay khi tiêu đề, mô tả SEO trống hoặc «Chặn»; «Chỉ từ khóa chính có vấn đề thì không chặn» | Mục 1 ở trên; hai câu trích có trong `MSG_*_SEO_LEFT_OUT` | Đúng |
| Ca T-115 «Bài bị sửa ngoài app»: câu trích | Ca mới `test_l3_readme_cau_bai_bi_sua_ngoai_app_khop_client`: câu trích **đúng từng chữ** `_RELEASE_CHANGED` (chỗ «(…)» là phần lược); cách (b) «tick ô gửi lại (sẽ tạo thêm một bài mới)» khớp nhãn `AGAIN_LABELS` | Đúng |
| «**Hẹn giờ thì vẫn hẹn khi chỉ thiếu SEO** … Riêng **ảnh đại diện** chưa lên (lệnh đặt ảnh đại diện lỗi) thì app **không hẹn giờ**» | Đúng với ca tôi nêu ở SL-T112-2 (lệnh đặt ảnh đại diện trả 500), **SL-T112-2 đóng**; nhưng luật thật không theo loại phần: **SL-T112-4** | Chưa đúng hẳn |
| SL-T106-1 | Thư Ký: câu khuyên «Quản trị viên» nằm trong code (`app/views/wordpress.py`), không phải README; để phiếu Họa Sĩ. Đồng ý | — |

### 4. Không lùi; gộp thử

- **Gộp thử** `main` cục bộ `29499dd` (T-118: `.streamlit/config.toml`, lớp AI, `env_file`, `site_index`, `plan_cache`; T-073: test khóa T-037) với `746ba9d`: `git merge-tree` **không xung đột**, cây `b76814c`. Hai bên không chung file code nào (nhánh lượt 3: `app/views/write.py`, `README.md`, test; `main`: `seo_app/ai/`, `seo_app/env_file.py`, `seo_app/storage/site_index.py`, `seo_app/storage/plan_cache.py`, `scripts/hash_password.py`, `.streamlit/config.toml`).
- **Chạy chọn lọc trên cây gộp** qua `run_list.sh` (kiểm danh sách, thiếu file thì dừng; dòng đầu mỗi lô đã xem: «Chạy 3/4/5 file chọn lọc»). Theo tin Chỉ Huy (RAM còn ít): chỉ file T-112, T-102, T-115, T-110, 3 lô nối tiếp, mỗi lúc một tiến trình:

| Lô | File | Kết quả |
|---|---|---|
| T-112 | `test_soi_loi_t112.py` (bản cuối), `test_t112_release_rules.py`, `test_t112_settings_switch.py` | 74 passed, 1 xfailed (SL-T112-4), 0 failed |
| T-102 («Gửi nháp» theo gói bộ dựng, Hẹn giờ, Đăng ngay, gửi trùng, hai tab, dòng kế hoạch) | `test_t102_publish.py`, `test_la_chan_t102.py`, `test_soi_loi_t102.py`, `test_t102_formula_cells.py` | 70 passed, 0 failed |
| T-115, T-110 (so `modified_gmt`; «Gửi nháp» gắn ảnh vào bài nháp) | `test_t115_modified_gmt.py`, `test_soi_loi_t115.py`, `test_t110_gan_anh_vao_bai_nhap.py`, `test_la_chan_t110.py`, `test_soi_loi_t110.py` | 496 passed, 0 failed |
| README SL-T108-1 (một ca, chỉ đọc chữ) | `test_soi_loi_t106.py::test_sl_t108_1_readme_trang_thai_khop_trang_ket_noi` | 1 passed |

Cộng: **641 passed, 1 xfailed, 0 failed, 0 XPASS**: không lùi ở «Gửi nháp», Hẹn giờ, Đăng ngay, T-115, T-110. Không chạy lại file ngoài 4 phiếu trên (T-099, T-086/T-089, các trang, ảnh): lượt 2 đã chạy chúng trên cây gộp `b953e5e` (49 file, 0 hỏng), lượt 3 chỉ đổi màn hình xác nhận và `release_missing` trong `app/views/write.py`. Các lô không chạy lại riêng trên cây nhánh: cây gộp chứa nguyên code nhánh, phần `main` thêm không chạm file nào của T-112 (ca mới của tôi đã chạy trên cây nhánh, xem «Lệnh đã chạy»).

### 5. Đột biến (code lượt 3)

9 đột biến trong bản sao `app/views/write.py` (script `mutate112r3.py`), mỗi lượt chạy các ca lượt 3 và 2 ca SL-T112-1 của `tests/test_soi_loi_t112.py` (`-k "l3 or sl_t112_1"`, 31 ca), dừng ở ca hỏng đầu: **9/9 bị bắt**. Sau mỗi lượt bản sao được trả nguyên (`cmp` với nhánh sau cùng: khớp).

| Đột biến | Ca bắt đầu tiên |
|---|---|
| Q1 bỏ hẳn dòng SEO ở màn hình xác nhận | `test_sl_t112_1_dang_ngay_khi_truong_seo_dang_chan_thi_khong_dang[tieu-de-chan]` |
| Q2 Đăng ngay chỉ Cảnh báo, không Chặn | như trên |
| Q3 Nháp cũng có dòng | `test_l3_gui_nhap_bat_ghi_seo_tieu_de_chan_van_nhu_cu` |
| Q4 tắt «Ghi SEO» vẫn xét trường bị bỏ | `test_l3_tat_ghi_seo_khong_them_dong_moi[Hẹn giờ]` |
| Q5 bỏ chốt hai ở `release_missing` | `test_l3_hen_gio_canh_bao_dung_truong_va_van_hen[mo-ta-trong]` |
| Q6 không thêm dòng SEO vào `notices` | `test_sl_t112_1_…[tieu-de-chan]` |
| Q7 cú bấm lọt không xét `allowed` (`if clicked:`) | `test_sl_t112_1_…[tieu-de-chan]`, phần bấm lọt (ca đối chứng cho thấy cách giả tới được nhánh gửi; lúc đó chốt hai vẫn giữ không đăng, nhưng bài nháp đã tạo, SEO đã ghi) |
| Q8 màn hình xác nhận chỉ xét tiêu đề | `test_sl_t112_1_…[mo-ta-chan]` |
| Q9 chốt hai chỉ xét mô tả | `test_l3_hen_gio_canh_bao_dung_truong_va_van_hen[ca-hai-chan]` |

### Lệnh đã chạy (lượt 3)

- Ca lượt 3 trên cây nhánh (`-k "l3 or sl_t112_4"`): 27 qua, 1 xfail, 1 hỏng do site giả (G6); sửa hai ca, chạy lại 3 ca: qua. Bản cuối cả file chạy trong lô T-112 trên cây gộp: 47 qua, 1 xfail.
- Dò chữ SEO (`probe_seo_text.py`, chỉ gọi hàm, không mạng): 29 kiểu chữ × 2 trường, 0 chữ bị client bỏ im lặng.
- Cây gộp `b76814c`, 4 lô chọn lọc: 641 passed, 1 xfailed, 0 failed (mục 4).
- Đột biến: 9/9 bị bắt.
- `uv run ruff check .`: sạch.
- `detect-secrets` (`PYTHONUTF8=1`) trên file test, báo cáo: sạch. Quét bản sao trong thư mục ngoài git cùng file mồi tiếng Việt: chỉ mồi bị báo (quét thẳng trong repo thì bộ quét bỏ qua file không do git theo dõi, kể cả mồi, nên không dùng kết quả đó).
- Script, ghi chú: thư mục ghi chú chung `T-112-soi-loi-scripts/` (`run_list.sh`, `mutate112r3.py`, `probe_seo_text.py`).

### Lỗi mới

#### SL-T112-4 · Thấp · README chia luật Hẹn giờ theo loại phần thiếu, luật thật theo lệnh ghi có lỗi giữa chừng không

- **Chỗ:** `README.md:488` (gạch «**Hẹn giờ thì vẫn hẹn khi chỉ thiếu SEO** … Riêng **ảnh đại diện** chưa lên (lệnh đặt ảnh đại diện lỗi) thì app **không hẹn giờ**…»).
- **Thực tế** (`seo_app/wordpress/client.py`, T-115): client chỉ không chuyển bài khi **không biết chắc giờ sửa bài**, tức là sau một lệnh ghi có thể đã ghi mà lỗi giữa chừng (`_taint_modified`: lệnh đặt ảnh đại diện lỗi, lệnh ghi SEO **đường meta** lỗi 5xx/mất mạng/trả lời lạ `:1423`, `:1428`). Phần thiếu mà **chưa hề ghi** thì không đánh dấu, Hẹn giờ vẫn đi:
  - Ghi SEO qua đường meta (SiteSEO không có Abilities, khóa meta mở trong REST) mà lệnh ghi trả 500: **chỉ thiếu SEO mà app không hẹn giờ**, bài vẫn là nháp, câu «… Chưa hẹn giờ, chưa đăng…» (ca `test_l3_hen_gio_ghi_seo_duong_meta[loi-giua-chung]`; đối chứng `[doi-chung-ghi-duoc]`: cùng đường meta mà ghi được thì hẹn giờ, không cảnh báo). Trái câu «vẫn hẹn khi chỉ thiếu SEO».
  - Lệnh đặt ảnh đại diện hỏng **ngay ở bước hỏi bài** (`_own_draft` lỗi, chưa ghi gì): ảnh đại diện chưa lên mà app **vẫn hẹn giờ**, kèm cảnh báo «Bài đã hẹn giờ nhưng ảnh đại diện chưa lên…» (ca `test_l3_hen_gio_chua_hoi_duoc_bai_de_dat_anh_dai_dien_thi_van_hen`). Trái câu «ảnh đại diện chưa lên (lệnh đặt ảnh đại diện lỗi) thì app không hẹn giờ».
  - Đường chính (Abilities, chủ dự án đã bật): ghi SEO lỗi không đánh dấu, nên «vẫn hẹn» đúng; vì vậy lệch chỉ ở đường dự phòng và ca hỏi bài lỗi, hiếm.
- **Nguồn:** câu này làm đúng theo **gợi ý của tôi ở SL-T112-2** («SEO chưa lên thì vẫn hẹn; ảnh đại diện chưa lên thì không hẹn»). Lượt 1 tôi chỉ thử lệnh đặt ảnh đại diện trả 500 và ghi SEO giả bằng `seo_answer` (không qua client thật), nên chia theo loại phần là sai của tôi.
- **Hậu quả:** chỉ là câu báo người dùng thấy khác README; cả hai hướng đều an toàn (không hẹn thì bài vẫn là nháp, có câu nói rõ; hẹn thì có cảnh báo rõ phần thiếu). **Thấp**, sửa trước khi bật công tắc (cùng đợt SL-T112-2).
- **Test:** `test_sl_t112_4_readme_hen_gio_ghi_seo_loi_giua_chung_khong_hen` (xfail: đoạn «Ảnh đại diện hay SEO chưa lên kịp» phải có câu nói «không hẹn giờ» gồm cả SEO); hai ca hành vi ở trên qua (ghim hành vi hiện tại).
- **Gợi ý câu README:** «Hẹn giờ vẫn hẹn, kèm cảnh báo, khi phần thiếu chưa được ghi lên website (ví dụ SiteSEO chưa cho ghi SEO). Còn lệnh ghi ảnh đại diện hay SEO **bị lỗi giữa chừng** thì app không biết chắc bài nháp trên website đã đổi chưa nên **không hẹn giờ**: bài vẫn là nháp, báo «… Chưa hẹn giờ, chưa đăng…» (xem «Bài bị sửa ngoài app»).»

### Ghi nhận lượt 3 (không tính lỗi)

- **G3 · Tiêu đề SEO trên 200 ký tự:** bước SEO chỉ «Cảnh báo» (dài), màn hình xác nhận không Chặn; client từ chối **cả** lệnh ghi SEO (`_seo_text`: quá 200 ký tự, chưa gửi gì). Đăng ngay vẫn giữ nháp (chốt `seo_ok` của lượt 1; ca `test_l3_tieu_de_tren_200_ky_tu_…` qua, trang hiện câu «quá dài» của client), Hẹn giờ vẫn hẹn và cảnh báo SEO chưa lên. An toàn; nếu muốn báo sớm thì bước SEO cho tiêu đề trên 200 ký tự mức «Chặn» (phiếu sau, không gấp).
- **G4 · Ký tự «trông như trống» mà không vô hình theo Unicode:** U+2800 (ô chữ nổi trống), dấu kết hợp đứng một mình (U+0301): `normalize_meta` không bỏ (không thuộc nhóm «mặc định bỏ qua»), bước SEO chỉ «Cảnh báo» (ngắn), nên mô tả SEO chỉ có U+2800 vẫn được ghi và Đăng ngay vẫn đi. Phải tự gõ/dán ký tự này; không phải lỗi của T-112 (bộ lọc T-041, T-090). Ghi lại cho phiếu dọn ký tự sau.
- **G5 · Hai lần ngắt giữa lượt:** máy ngủ/khởi động lại (03/11 ~15:00: lượt chạy ca mới và lô 22 file trên cây gộp chết, mã 4) và hết hạn mức (lô chạy lại bị dừng sau 45 ca, chưa ca nào hỏng). Mỗi lần tôi kiểm lại hai bản sao (`tar --compare` với `git archive`: chỉ khác file test của tôi), không còn tiến trình test nào của tôi, rồi chạy lại với thư mục tạm mới. Theo tin Chỉ Huy 03/11 (RAM còn ít): chỉ chạy file T-112, T-102, T-115, T-110, từng lô một tiến trình.
- **G6 · Fixture `site` (`tests/test_app_images.py`) dựng client bỏ qua `write_seo`:** client thật trong mọi ca giao diện luôn báo «chưa bật ghi SEO» mà không gửi gì. Các ca T-102/T-112 đều vá `set_seo_meta` nên không bị ảnh hưởng; nhưng ca nào muốn đi **đường ghi SEO thật** của client phải tự cho client nhận công tắc (`honor_seo_switch` trong file của tôi). Bản đầu ca tiêu đề trên 200 ký tự của tôi qua vì lý do này (không phải vì «quá dài»); tôi bắt được khi ca đường meta không gửi lệnh ghi nào, đã sửa cả hai và thêm kiểm câu của client. Ghi lại cho người viết test sau.

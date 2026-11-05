# Báo cáo T-124 · Lấy số liệu Search Console, lưu thuộc tính (Giai đoạn 6, đợt 2)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-124](../tickets/T-124-lay-so-lieu-luu-thuoc-tinh.md) |
| Nhánh | `team/T-124`, từ `main` cục bộ `8caab2f` (đã có T-121, T-122, T-123); commit mã và test `ac6a53a`, sửa ca test T-123 theo R5 `c8cbb5b`, báo cáo ở commit ngay sau |
| Ngày nộp | 2026-11-05 (giờ máy, +07) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Phần mềm đã có bước **lấy số liệu Google** cho trang «📈 Theo dõi». Phần này chưa có giao diện (T-125 làm nút bấm).
  - Lần đầu lấy 16 tháng, hết 18 lệnh tới Google (trần mỗi lần bấm là 20). Các lần sau chỉ lấy phần còn thiếu, thường 1 đến 3 lệnh.
  - Ngày Google chưa chốt số (thường 2–3 ngày gần nhất) được đánh dấu «tạm», không tính.
  - Bấm lại trong 10 phút mà chưa có gì mới thì không gửi lệnh. Hai tab cùng bấm thì tab sau được báo «đang lấy ở tab khác».
  - Lỗi giữa chừng: giữ phần đã lấy, lần bấm sau lấy tiếp.
- Nút **«Kiểm tra»** (Cài đặt): báo tài khoản dịch vụ có thấy thuộc tính không, quyền gì, số liệu có tới ngày nào, bao nhiêu phần trăm lượt hiển thị nằm ngoài website.
- **Lưu thuộc tính**: chỉ lưu được thuộc tính vừa tìm thấy bằng nút «Tìm thuộc tính», không gõ tay. Nếu máy có biến môi trường `GSC_SITE_URL` đè file `.env` thì phần mềm báo.
- Sửa 3 lỗi nhỏ Lá Chắn tìm ở đợt 1: file lưu tạm bị sửa tay thì nay tự bỏ và tạo lại; lỗi quyền khi xóa file lưu tạm ra câu tiếng Việt; bài có link viết hoa tên miền vẫn nhận số liệu.
- Ba chỗ đọc địa chỉ website (`WORDPRESS_URL`) nay dùng chung một hàm, một luật. Địa chỉ có thư mục con dạng tên file (có dấu chấm, ví dụ `/b.log`) bị từ chối ở cả phần WordPress lẫn Search Console. Website của anh ở gốc tên miền nên không ảnh hưởng.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/tracking/refresh.py` | Mới. `refresh` (nút «🔄 Lấy số liệu mới»), `check_connection` («Kiểm tra»), `find_properties` («Tìm thuộc tính»), `save_property` (lưu thuộc tính vào `.env`), `refresh_hint` (gợi ý «có thể đã có số liệu mới», không gọi mạng). Kết quả là dataclass có câu cố định: `RefreshReport` (`Outcome` DONE / PARTIAL / RECENT / BUSY / FAILED), `ConnectionCheck`, `HostShare`, `PropertyList`, `SaveResult`. Khóa cấp module `_FETCH_LOCK`. Không nhập Streamlit, AI, Google Sheets |
| `seo_app/env_file.py` | Thêm `validate_gsc_site_url` (bộ kiểm chặt riêng), `set_gsc_site_url(value, offered=…)` (chỉ ghi một mục trong danh sách vừa tìm thấy), `clear_gsc_site_url`, `gsc_site_url_overridden` (biến **có mặt** là đè, kể cả rỗng). Cùng bộ ghi nguyên tử `_write_value` với khóa AI, mã Sheet |
| `seo_app/wordpress/client.py` | Thêm hàm dùng chung `site_path_ok` (một luật đường con), `site_base` (chuẩn hóa `WORDPRESS_URL`), `site_link` (viết thường scheme, tên máy của link bài; LC-T123-1). Cửa vào `_is_plain_site_url` dùng `site_path_ok` (cùng mã cũ, chỉ tách hàm) |
| `seo_app/google/search_console.py` | `site_prefix` bỏ biểu thức `_PATH` riêng (nhận dấu «.»), dùng `site_path_ok` và `site_base` chung. Giữ phép kiểm chặt ở cửa vào (`from_settings`) |
| `seo_app/storage/search_cache.py` | Bỏ `site_base` riêng, nhập bản chung. LC-T122-1: `_prepare`, `_is_healthy` đọc `sqlite_master` bằng `_decode_text`; `_is_healthy` coi `_Corrupt` và mọi lỗi SQLite không phải bận, khóa, quyền, vào ra là file lạ (`_KEEP_FILE_CODES`). LC-T122-2: `clear()` đưa `dir_has_link` vào trong `try`. G1: `_parse_time` kiểm năm cả sau khi đổi múi giờ |
| `seo_app/tracking/match.py` | Bỏ `site_base` riêng, nhập bản chung. LC-T123-1: `build_tracking` viết thường scheme, tên máy của `item.link` (sau `is_site_link`) trước khi dựng khóa |
| `tests/test_tracking_refresh.py` | Mới, 100 ca: chia đoạn, số tạm, chặn bấm lại, đồng hồ lệch, trần lệnh, lỗi giữa chừng, khóa hai tab, một client mỗi lần bấm, từ khóa, ngày đăng, thử chung T-122 × T-123, gợi ý, «Kiểm tra», tìm và lưu thuộc tính, module không nhập AI/Sheets/giao diện |
| `tests/test_env_file_gsc.py` | Mới, 59 ca: bộ kiểm, ghi, xóa, chặn chèn biến, danh sách vừa tìm, biến môi trường đè `.env` |
| `tests/test_t124_chuan_hoa_va_cache.py` | Mới, 72 ca: bảng ca chung cho 3 nơi gọi cũ, một luật đường con (WordPress = Search Console), `site_link`, LC-T123-1, LC-T122-1, LC-T122-2, G1, 4 ca ghim G2 của T-122, ca ghim G2 của T-123 |
| `tests/test_google_search_console.py` | Đổi kỳ vọng 1 ca theo R5 (bảng ngay dưới), thêm 7 địa chỉ bị từ chối, 1 ca thoát «.» của bộ lọc |
| `tests/test_tracking_model.py` | Thu hẹp ca «gói là hàm thuần» của T-123 theo R5 (bảng ngay dưới): áp cho 7 file lõi, `refresh.py` là lớp nối |
| `docs/team/reports/T-124-tho-may.md` | Báo cáo này |

Không sửa `app/**`, README. Không thêm thư viện.

### Đổi kỳ vọng ca test cũ (R5)

| Ca | Cũ | Mới | Lý do |
|---|---|---|---|
| `test_tien_to_va_bieu_thuc_loc_dung_tu_wordpress_url[…b.log…]` (T-121) | `site_prefix("https://example.com/b.log/")` = `https://example.com/b.log/` | Chuyển sang `test_wordpress_url_khong_dung_duoc_bi_tu_choi`: ra `SearchConsoleError`. Ca nhận thay bằng `https://example.com/Blog_2/a-b~c` (đủ các ký tự được phép) | Phiếu yêu cầu 5 và Lá Chắn T-121 B.2: một luật đường con với client WordPress, luật này không nhận «.» (SL-T042-10, LC-T042-5). Phép thoát «.» của bộ lọc RE2 vẫn kiểm riêng: `test_bieu_thuc_loc_thoat_dau_cham_trong_tien_to` |

| `test_package_is_pure_functions` (T-123, `tests/test_tracking_model.py`) | Mọi file `*.py` trong `seo_app/tracking/` không được nhập mạng, file, `seo_app.google`, `seo_app.storage`, `seo_app.config`… | Phép kiểm nhập chỉ áp cho 7 file lõi (`__init__`, `model`, `periods`, `match`, `stats`, `flags`, `keywords`). `refresh.py` xếp riêng là lớp nối, vẫn kiểm không gọi `open`, `eval`, `exec`, `compile`, `__import__`. Thêm hai điều chặt hơn: gói không được có file nào chưa xếp loại; lõi không được nhập `seo_app.tracking.refresh` | Phiếu T-124 và thiết kế T-120 mục 6 đặt `refresh.py` trong gói này (docstring `__init__.py` của T-123 cũng ghi vậy); lớp nối phải nhập client, cache, `.env`. Phép kiểm riêng của `refresh.py`: `test_module_khong_nhap_giao_dien_ai_sheets`, `test_nap_module_khong_goi_ham_nao_ngoai_hang_so`. Thử 3 đột biến (lõi nhập `sqlite3`, lõi nhập `refresh`, thêm file lạ vào gói): cả 3 bị bắt |

Chỉ hai ca này đổi. Mọi test khác của T-121, T-122, T-123 và test `.env` giữ nguyên kỳ vọng.

### Cách dùng (cho T-125)

```python
store, index = SearchCacheStore(), SiteIndexStore()
wordpress = ...  # WordPressClient khi đã kết nối (như wordpress_client() ở app/views/plan.py), không thì None
report = refresh(settings, store, site_index=index, wordpress=wordpress)  # một lần bấm
st.write(escape_markdown(report.message)); [st.caption(escape_markdown(n)) for n in report.notes]
cache = store.load(CacheScope(settings.gsc_site_url, settings.wordpress_url))  # vẽ trang
hint = refresh_hint(cache)                                              # không gọi mạng
found = find_properties(settings)            # nút «Tìm thuộc tính»: giữ trong session_state
result = save_property(chosen_site_url, found)   # chỉ mục found.usable_site_urls
check = check_connection(settings)            # nút «Kiểm tra»: check.messages, check.hosts
```

## Chỗ thiết kế để ngỏ, tôi đã chọn

| # | Chỗ | Đã làm | Lý do |
|---|---|---|---|
| 1 | Chia đoạn ≤ 31 ngày | Đoạn cũ chia xuôi từ ngày đầu cần lấy; đoạn mới nhất luôn là 31 ngày cuối (khi khoảng đủ dài). Lần đầu: 15 đoạn cũ + 1 đoạn mới = 16 lệnh | Mọi ngày tạm (thường 2–3 ngày cuối) nằm trong đoạn mới nhất, đúng luật «ngày tạm chỉ ở cuối» của cache |
| 2 | Luật nối liền của cache (T-122) | Đoạn đầu tiên luôn tới hết phần đã lưu (`reach`): nếu cách chia thường dừng trước `covered_end` thì kéo dài (vẫn ≤ 31 ngày) | Cache chỉ nhận đoạn «mới nhất» bắt đầu từ ngày tạm và tới ít nhất `covered_end`. Không kéo thì cache từ chối (`MSG_BAD_RANGE`) và kẹt mãi |
| 3 | `first_incomplete_date` ở đoạn cũ | Có thì đánh dấu tạm từ ngày đó; đoạn sau bắt đầu lại từ ngày tạm (dài hết mức). Không tiến được (cả đoạn cũ là số tạm) thì dừng với `MSG_STUCK`, không lặp | Thiết kế 1.3 bước 4: «dòng có ngày ≥ `first_incomplete_date` là tạm» cho mọi đoạn. Google thật chỉ báo tạm 2–3 ngày cuối; ca lạ không được làm cache sai hay lặp tới hết 20 lệnh |
| 4 | Metadata sai dạng ở đoạn cũ | 3 ngày cuối đoạn là tạm (như đoạn mới nhất) | Thiết kế 2.4: «sai dạng … coi 3 ngày cuối là tạm (hướng an toàn)». Thiếu ở đoạn cũ là bình thường: đã chốt |
| 5 | Chặn bấm lại | Không gửi lệnh khi: lần ghi gần nhất < 10 phút, không ở tương lai quá 5 phút, ngày PT chưa sang ngày mới, đã có từ khóa hai kỳ | «E chưa đổi» chỉ biết được khi hỏi Google; ngày PT không đổi và đủ từ khóa là điều kiện biết được mà không gửi lệnh. 5 phút như `_CLOCK_SKEW` của `site_index` |
| 6 | Đồng hồ chỉnh lùi | `covered_end` sau hôm nay PT: `clear()`, lấy lại 16 tháng, ghi chú `MSG_CLOCK_BACK` | Lá Chắn T-122 mục 8.3 |
| 7 | Lỗi ở bước từ khóa, ngày đăng | Số liệu ngày đã đủ: `PARTIAL` với câu «Đã lấy số liệu tới hết ngày …», câu lỗi ở `notes`. Lần bấm sau không bị chặn (thiếu từ khóa) | Không làm mất phần ngày đã lưu; người dùng thấy đúng phần đã có |
| 8 | Ngày đăng | Chỉ hỏi bài (`type == "post"`) có 0 lượt hiển thị cả hai kỳ mặc định và chưa có trong cache, tối đa 1.000 mã; `keep` = mọi bài trong danh sách. WordPress lỗi chỉ ghi chú | Nhãn «mới đăng», «chưa có lượt hiển thị» chỉ cần ngày đăng của các bài này; `post_statuses` chỉ đọc |
| 9 | Danh sách bài | Đã kết nối WordPress: `SiteIndexStore.get` (tải lại khi cũ hơn 6 giờ); WordPress lỗi: dùng bản cũ, ghi chú giờ tải. Chưa kết nối: bản đã lưu | Như thiết kế 1.3 bước 6 |
| 10 | Ngày «hôm nay» | `periods.google_today(now)` (ngày PT, kiểm năm trước khi đổi múi giờ) thay cho `today_pacific()` | Cùng ngày PT với `today_pacific()` (Lá Chắn T-121 B.1), thêm phép kiểm năm của LC-T120-10. Client vẫn tự kiểm khoảng ngày bằng `today_pacific()` |
| 11 | «Kiểm tra» | Tối đa 3 lệnh (`sites`, 10 ngày theo ngày, 28 ngày theo trang nếu thuộc tính tên miền). Quyền «Chủ sở hữu», «Toàn quyền»: cảnh báo hạ quyền. Ngoài website ≥ 90%: cảnh báo `WORDPRESS_URL` có thể sai. Tên máy trùng website: ghi «địa chỉ http:// hoặc lạ» (GN-6) | Thiết kế 1.2 |
| 12 | Lưu thuộc tính | Hai lớp: `save_property` chỉ nhận mục `usable` của kết quả «Tìm thuộc tính», rồi `parse_property`; `set_gsc_site_url` kiểm chặt và đòi giá trị nằm trong `offered` | LC-T120-12: đường này không nhận chữ gõ tay |

## Bằng chứng

```
# Windows 11, Python 3.12.15, ruff 0.16.10. (1), (2) chạy trên cây làm việc trước khi commit;
# (3), (4) trên đúng commit ghi ở đầu mục, git status chỉ còn file báo cáo này chưa commit.

# 1) Mọi nơi gọi hàm dùng chung, trên mã đã gom (trước khi sửa test cũ):
#    T-121, T-122, T-123, client WordPress (cửa vào WORDPRESS_URL)
1 failed, 2499 passed, 1 skipped          ← đúng ca b.log (R5, bảng trên)

# 2) Mọi test .env (test_env_file, T-090, T-101, T-104, T-105, Lá Chắn/Soi Lỗi T-090, T-104, T-105,
#    config, khóa AI dùng env_file, Google Sheets), sau khi thêm 4 hàm GSC_SITE_URL
2516 passed, 11 skipped, 4 xfailed        ← 4 xfail có từ trước (SL-T026-3, SL-T028-1)

# 3) Trên ac6a53a: 3 file mới + mọi file của (1) và (2) + 13 file test_wordpress_*
$ uv run pytest -q tests/test_tracking_refresh.py tests/test_env_file_gsc.py \
    tests/test_t124_chuan_hoa_va_cache.py <T-121, T-122, T-123, WordPress, .env: 55 file>
1 failed, 6548 passed, 12 skipped, 4 xfailed in 848.56s
#    Ca hỏng: test_tracking_model.py::test_package_is_pure_functions (T-123) quét cả gói
#    seo_app/tracking/, gặp refresh.py → sửa theo R5 (bảng trên), commit c8cbb5b.

# 4) Trên c8cbb5b
$ uv run pytest -q tests/test_tracking_*.py tests/test_soi_loi_t123.py tests/test_t124_chuan_hoa_va_cache.py
489 passed in 37.03s
# Test đọc mã nguồn cả cây seo_app/ hay đọc client.py (grep rglob/glob/"seo_app" /):
$ uv run pytest -q tests/test_images_process.py tests/test_la_chan_t096.py \
    tests/test_t103_plan_prompt.py tests/test_soi_loi_t037.py tests/test_soi_loi_t110.py \
    tests/test_soi_loi_t115.py tests/test_t110_gan_anh_vao_bai_nhap.py tests/test_site_index.py \
    tests/test_google_service_account.py tests/test_soi_loi_t034.py
1163 passed, 4 skipped in 153.67s

$ uv run ruff check .                                  # toàn repo
All checks passed!
$ uv run ruff format --check <4 file mới>
4 files already formatted
# Không chạy ruff format trên file có sẵn: client.py ở main đã lệch định dạng từ trước (dòng
# không do T-124 viết); khối hàm mới đã đúng định dạng (ruff format --diff không đụng tới).

# Quét bí mật: bản sao 10 file đổi ở thư mục nháp, PYTHONUTF8=1, detect-secrets --all-files
2 phát hiện, cả 2 có sẵn ở 8caab2f (tên biến "APP_PASSWORD_HASH" ở env_file.py; chú thích ví dụ
"htps://tên:mật-khẩu@site" ở client.py). T-124 không thêm phát hiện nào.
# Đối chứng: thêm một khóa giả vào bản sao refresh.py → bắt được (Secret Keyword). Đã xóa.

# Ký tự ẩn, CR (script ở thư mục nháp): 0 trong 6 file mới hay sửa nhiều.
# Gộp thử: git merge-tree với main 8caab2f và origin/main: không xung đột.
```

**Thử đột biến** (script ở thư mục nháp: sửa cố ý một chỗ, chạy 3 file test mới, trả file về nguyên văn, kiểm SHA-256): 20 chỗ trên 5 file nguồn, **19 bị bắt**.

| Mã | Đột biến | Kết quả |
|---|---|---|
| M01 | Bỏ khóa (`acquire()` chờ) | Bị bắt. Lần đầu làm ca khóa **treo** (luồng tự chờ khóa nó giữ); đã sửa ca chạy ở luồng riêng có hạn chờ, nay hỏng gọn |
| M02–M07 | Mốc tương lai không coi là cũ; bỏ `reach`; không bỏ cache khi đồng hồ lùi; đoạn cũ bỏ metadata; bỏ chặn lặp; chặn bấm lại không xét từ khóa | Bị bắt cả 6 |
| M08–M10 | `save_property`, `set_gsc_site_url` bỏ kiểm danh sách vừa tìm; kiểm đè `.env` bằng `.strip()` | Bị bắt cả 3 |
| M11 | LC-T123-1: bỏ `site_link` | Bị bắt |
| M12 | LC-T122-1: bỏ `text_factory` ở `_is_healthy` | **Sống, đột biến tương đương**: không có `text_factory` thì lỗi giải mã ra `OperationalError` không có mã SQLite (đã chạy thử), vẫn rơi vào nhánh «file lạ, bỏ file». Giữ dòng này cho rõ ý, đúng đề xuất của Lá Chắn |
| M13–M15 | Ném lại mọi `DatabaseError`; `dir_has_link` ngoài `try`; bỏ kiểm năm sau khi đổi múi giờ | Bị bắt cả 3 |
| M16–M17 | Đường con nhận «.»; `site_base` không bỏ `:443` | Bị bắt cả 2 |
| M18–M20 | Ngày đăng hỏi mọi bài; không truyền `keep`; thiếu metadata ở đoạn mới nhất coi là chốt | Bị bắt cả 3 |

## Đối chiếu tiêu chí xong

- [x] **Yêu cầu 1** (`refresh`), các ca trong `tests/test_tracking_refresh.py`:
  - khoảng cần lấy, chia đoạn cũ tới mới, 18 lệnh lần đầu: `test_lan_dau_lay_16_thang_chia_doan_cu_toi_moi`; lần sau chỉ lấy từ ngày tạm: `test_lan_sau_chi_lay_tu_ngay_tam_dau_tien`; đoạn đầu tới hết phần đã lưu: `test_lay_tiep_sau_nhieu_ngay_doan_dau_toi_het_phan_da_luu`, `test_sau_khi_ket_lan_bam_sau_lay_tiep_duoc`; bảng `test_ngay_cuoi_cua_doan`;
  - tạm/chốt: `test_ngay_tam_dau_tien_cua_doan`, `test_doan_moi_nhat_thieu_hay_sai_metadata_3_ngay_cuoi_la_tam`, `test_doan_cu_metadata_sai_dang_lay_lai_tu_ngay_tam`, `test_doan_cu_bao_so_tam_hon_31_ngay_dung_khong_lap`, `test_chua_co_ngay_nao_da_chot`;
  - từ khóa 2 kỳ: ca lần đầu, `test_loi_tu_khoa_giu_so_lieu_ngay`, `test_tu_khoa_cham_tran_ghi_chu`;
  - làm mới `SiteIndex`, ngày đăng qua `post_statuses`: `test_ngay_dang_chi_hoi_bai_khong_co_luot_hien_thi`, `test_danh_sach_bai_cu_hon_6_gio_tai_lai`, `test_wordpress_loi_dung_danh_sach_cu`, `test_wordpress_loi_khong_co_danh_sach_cu`, `test_hoi_ngay_dang_loi_chi_ghi_chu`, `test_chua_ket_noi_wordpress_dung_danh_sach_da_luu`, `test_ngay_dang_cua_bai_da_go_bi_bo`, `test_ngay_dang_wordpress_sai_dang_bi_bo`;
  - ghi từng đoạn, dừng ở lỗi đầu: `test_loi_giua_chung_dung_o_loi_dau_tien`, `test_loi_ngay_lenh_dau_khong_luu_gi`;
  - chặn bấm lại: `test_bam_lai_trong_10_phut_khong_gui_lenh`, `test_bam_lai_sau_10_phut_chi_lay_doan_tam`, `test_moc_lay_lech_vai_phut_van_chan`, `test_sang_ngay_moi_khong_chan`;
  - gợi ý 3.3: `test_goi_y_co_the_da_co_so_lieu_moi` (10 ca), `test_goi_y_khong_goi_mang`.
- [x] **Yêu cầu 2** (`check_connection`): `test_kiem_tra_thuoc_tinh_ten_mien` (3 lệnh, khoảng ngày, không lọc ở lệnh đếm tên máy, GN-6), `test_kiem_tra_quyen_cao_canh_bao`, `test_kiem_tra_thuoc_tinh_khong_doc_duoc`, `test_kiem_tra_thuoc_tinh_tien_to_khong_dem_ten_may`, `test_kiem_tra_phan_ngoai_website`, `test_kiem_tra_chua_co_so_lieu_gan_day`, `test_kiem_tra_loi_google_cau_co_dinh`, `test_kiem_tra_file_khoa_hong`
- [x] **Yêu cầu 3** (`env_file`), `tests/test_env_file_gsc.py`: bộ kiểm (`test_bo_kiem_*`, 26 giá trị sai gồm xuống dòng, `=`, `#`, nháy, chữ hoa, `http://`, đường con, ký tự rộng 0); ghi, xóa giữ dòng khác (`test_ghi_*`, `test_thay_moi_dong_lap_va_giu_crlf`, `test_xoa_*`); **LC-T120-12**: `test_chi_ghi_thuoc_tinh_trong_danh_sach_vua_tim`, `test_gia_tri_sai_bi_chan_truoc_khi_xet_danh_sach`, và ở `refresh`: `test_luu_thuoc_tinh_vua_tim_thay`, `test_luu_thuoc_tinh_khong_duoc_chon_bi_tu_choi`, `test_luu_thuoc_tinh_phai_tu_ket_qua_tim`, `test_luu_thuoc_tinh_muc_gia_mao_qua_bo_kiem_chat`; **LC-T120-23**: `test_bao_bien_moi_truong_de_env` (rỗng, dấu cách đều là đè), `test_bien_moi_truong_rong_de_gia_tri_trong_env`, `test_luu_thuoc_tinh_bao_bien_moi_truong_de_env`, `test_luu_thuoc_tinh_mac_dinh_doc_os_environ`
- [x] **Yêu cầu 4**: một client mỗi lần bấm (`test_moi_lan_bam_mot_client_tu_from_settings`, `len(factory.created)` ở `test_bam_lai_trong_10_phut_khong_gui_lenh`); **LC-T120-22** khóa cấp module: `test_khoa_dang_giu_tab_khac_bao_ban`, `test_hai_tab_cung_bam_chi_mot_lan_lay` (hai luồng thật), `test_khoa_nha_ca_khi_loi_bat_ngo`; mốc chặn bấm lại nằm trong cache, không trong `session_state`; **LC-T120-8**: `test_tran_20_lenh_cua_client_that` (429 năm lần, lệnh thứ 21 bị chặn, giữ phần đã ghi), `test_het_tran_lenh_dung_giu_phan_da_luu_lan_sau_lay_tiep` (4 lần bấm mới đủ, mỗi lần lấy tiếp đúng chỗ)
- [x] **Yêu cầu 5**: một hàm `site_base`, một luật `site_path_ok`; bảng ca chung cho 3 nơi gọi cũ (`test_mot_ham_cho_ca_ba_noi_goi_cu`, 12 ca, gồm bảng của T-122 lượt 2 và T-123 lượt 2), WordPress = Search Console trên 24 đường con (`test_mot_luat_duong_con_cho_wordpress_va_search_console`), không còn bản riêng (`test_khong_con_ban_chuan_hoa_rieng`). Bảng ca cũ của T-122 (`SITE_BASE_CASES`), T-123 vẫn chạy và qua
- [x] **Yêu cầu 6**: `test_dataclass_that_cua_cache_qua_protocol_cua_loi_theo_doi`: `CachedDay`, `CachedQuery` đọc lại từ file SQLite (`final` là `bool`, `day` là `date`) qua `build_tracking`, `aggregate`, `page_queries`, `keyword_table`, `compare`, `page_flags` (bài mới đăng nhận nhãn «mới đăng» nhờ ngày đăng lấy từ `post_statuses`)
- [x] **Yêu cầu 7** (LC-T123-1): sửa phần T-124 (`test_link_bai_viet_hoa_ten_may_van_nhan_so_lieu`, `test_link_hoa_cua_may_khac_van_bi_bo`, `test_duong_dan_hoa_cua_link_giu_nguyen`). Phần T-125 còn lại: xem Đề xuất
- [x] **Yêu cầu 8**: chạy mọi test `.env` và mọi test của T-121, T-122, T-123, client WordPress (mục Bằng chứng). Grep theo hành vi bị ghim: `_is_plain_site_url`, `_SITE_PATH`, «chỉ được là địa chỉ website», `site_prefix`, `page_filter_expression`, `covers_site`, `site_base`, `MSG_OPEN`: mọi file tìm được đều nằm trong lượt chạy. Tôi **bỏ sót** một loại: test quét cả gói bằng `glob` (`test_package_is_pure_functions` của T-123 gặp file mới `refresh.py`). Lượt chạy cuối bắt được; đã sửa theo R5 (`c8cbb5b`) và chạy thêm mọi test đọc mã nguồn cả cây `seo_app/` hay đọc `client.py`: 1163 qua
- [x] **Lá Chắn T-122 mục 8**: LC-T122-1 (`test_file_sua_tay_bi_bo_va_ghi_lai_duoc`, `test_file_sua_tay_ghi_truoc_khi_doc` với UTF-8 hỏng trong `sqlite_master` và «schema format» 5; file bận vẫn giữ: `test_file_dang_ban_van_bao_ban_khong_xoa`), LC-T122-2 (`test_clear_loi_quyen_khi_kiem_lien_ket`, `test_clear_loi_xoa_file_cung_cau_co_dinh`), G1 (`test_moc_lay_doi_mui_gio_ra_ngoai_khoang_nam_bi_bo`), 4 ca ghim G2 (`test_ghim_*`), mốc ở tương lai coi như cũ (GN-2: `test_moc_lay_o_tuong_lai_coi_nhu_cu`), đồng hồ chỉnh lùi gọi `clear()` (`test_dong_ho_chinh_lui_bo_cache_lay_lai`). Ca ghim G2 của Lá Chắn T-123: `test_ghim_google_day_kiem_nam_truoc_khi_doi_mui_gio`
- [x] **Lá Chắn T-121 B.1, B.2**: một client mỗi lần bấm, khóa, lỗi «Đã gửi đủ 20 lệnh» giữ phần đã ghi, ngày PT, GN-6 (ở trên); giữ phép kiểm chặt ở `from_settings`, một luật đường con. Phần `escape_markdown` và lệnh xin mã chờ ~3 giây là của T-125 (Đề xuất)
- [x] **LC-T120-10**: ngày giờ máy lạ (`test_gio_may_khong_hop_le`), năm kiểm trước khi đổi múi giờ ở cache (G1, G2) và `google_day`; không lọt `OverflowError`, `ValueError`
- [x] **LC-T120-13, -21**: `test_module_khong_nhap_giao_dien_ai_sheets` (không nhập `streamlit`, `app`, `seo_app.ai`, `seo_app.google.sheets`, `seo_app.plan`, `anthropic`, `openai`, `google.genai`, `requests`), `test_nap_module_khong_goi_ham_nao_ngoai_hang_so` (nạp module chỉ gọi `timedelta`, `threading.Lock`). Phần AppTest mở trang không gọi mạng là của T-125
- [x] **LC-T120-15**: test chạy dưới bộ chặn mạng; Google giả, WordPress giả; ca biên 2.4 phần T-124: metadata thiếu, sai dạng, ngoài khoảng; chạm trần dòng (`test_doan_ngay_cham_tran_dong_ghi_chu_mot_lan`, từ khóa); dòng sai dạng bị bỏ và đếm (`test_dong_sai_dang_bi_bo_va_dem`)
- [x] Test liên quan và `uv run ruff check .` qua
- [x] Báo cáo này
- [ ] Toàn bộ `uv run pytest`: việc của Chỉ Huy khi gộp

## Rủi ro và điểm cần chú ý

- **`first_incomplete_date` ở đoạn cũ**: tôi theo đúng thiết kế (mọi đoạn), nhưng Google thật thường chỉ trả trường này khi khoảng có ngày tạm. Lượt thử thật (Lá Chắn T-121 B.4) nên ghi lại câu trả lời của một đoạn cũ để xác nhận.
- **Lần đầu cần 18 lệnh**: gặp 429 nhiều lần thì có thể phải bấm 2 lần mới đủ (đã có ca test). Không ảnh hưởng số liệu.
- **Nửa đêm giờ PT**: `refresh` tính «hôm nay» một lần lúc bấm; client tự kiểm khoảng ngày bằng `today_pacific()` lúc gửi. Bấm đúng lúc qua nửa đêm PT (14:00–15:00 giờ Việt Nam) thì hai bên lệch một ngày; khoảng vẫn hợp lệ (ngày cuối ≤ hôm nay của client), lần bấm sau lấy nốt ngày mới.
- **`refresh` chạy đồng bộ** khoảng một phút ở lần đầu (16 + 2 lệnh, mỗi lệnh có thể tới vài giây; lệnh xin mã có thể chờ thêm ~3 giây, GN-1 T-121). Giao diện nên hiện trạng thái chờ.
- **Khóa chỉ trong một tiến trình**: hai cửa sổ app chạy hai tiến trình riêng (hiếm) vẫn có thể lấy cùng lúc; khi đó cache tự chặn ghi xen nhau (giao dịch `BEGIN IMMEDIATE`, luật nối liền), nhiều nhất tốn gấp đôi lệnh.
- **Đổi luật đường con**: `WORDPRESS_URL` có thư mục con chứa «.» hay từ cấm nay bị client Search Console từ chối (trước đó client WordPress đã từ chối nên app chưa từng chạy được với địa chỉ như vậy).

## Đề xuất

- **T-125 (giao diện):**
  - hiện `report.message`, `report.notes`, `check.messages`, `PropertyList.message`, `SaveResult.message` qua `escape_markdown`; hiện `SiteEntry.site_url`, `HostShare.host` như chữ thuần (LC-T120-11, -19; Lá Chắn T-121 B.1, B.3);
  - giữ `find_properties(...)` trong `session_state` và chỉ cho chọn `found.usable_site_urls`, truyền đúng đối tượng đó vào `save_property` (LC-T120-12); `SaveResult.overridden` thì hiện cảnh báo LC-T120-23;
  - nút «Lấy số liệu mới» chỉ gọi `refresh` khi bấm, trong `st.status`/`st.spinner`; mở trang chỉ đọc cache (`store.load`) và `refresh_hint` (LC-T120-21); không đưa `SearchCache` qua `st.cache_data` (GN-1 Soi Lỗi T-122);
  - `MSG_OPEN`, `MSG_BROKEN` lặp lại: nút «Xóa bản lưu tạm» gọi `store.clear()` (Lá Chắn T-122 mục 8.2);
  - LC-T123-1 phần còn lại: khi `SiteTracking.skipped_items > 0` hiện câu cố định «N bài, trang không khớp địa chỉ website trong cài đặt».
- **T-126 (README):** lần đầu lấy khoảng một phút; bấm lại trong 10 phút không có gì mới; ý nghĩa «số tạm».
- **Ngoài phạm vi (Lá Chắn T-122 mục 8.4):** `plan_cache._is_healthy` có cùng mẫu LC-T122-1. Sửa giống ở đây (`text_factory`, `_KEEP_FILE_CODES`) khi có phiếu dọn.

## Câu hỏi cho chủ dự án

Không có.

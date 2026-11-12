# Báo cáo T-137 · Nhắc chống gửi trùng sau khi file nháp bị cất sang một bên (SL-T136-1, G4)

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | [T-137](../tickets/T-137-nhac-gui-trung-sau-khi-cat-file-nhap.md) (trên `main` `575cd46`) |
| Ngày nộp | 2026-11-12 |
| Nhánh | `team/T-137`, tạo từ đầu `team/T-136` (`6a005c1`, chưa gộp `main`) |
| Kết quả | Hoàn thành yêu cầu 1–6. Chỉ **thêm** cổng, không nới khóa nào; không đổi, không bỏ test cũ nào |

## Tóm tắt (cho chủ dự án)

Khi file nháp trên máy bị chương trình khác làm hỏng, phần mềm cất file cũ sang một bên (trong thư mục `data`, tên dạng `drafts.hong-…sqlite`) rồi bắt đầu file mới. Ghi chú «đã gửi» của các bài gửi trước đó nằm trong file cũ. Trước đây, sau lúc đó phần mềm có thể để bạn gửi lại một bài đã có trên website mà không nhắc gì, và trang Bài viết còn ghi «Chưa có bài nào phần mềm đã gửi lên WordPress.».

Nay, **chừng nào file cũ còn trong thư mục `data`**:

- Trang **Bài viết**, cột «Đã gửi WordPress», luôn có lời nhắc: danh sách có thể thiếu bài, trước khi gửi lại bài nào hãy xem trên WordPress bài đó đã có chưa.
- Ở bước **Xuất bản**, bài nào chưa có ghi chú «đã gửi» (cả Nháp, Hẹn giờ, Đăng ngay) phải tick ô **«Tôi đã xem trên WordPress: bài này chưa có trên website»** thì nút gửi mới mở. Ô không tick sẵn; đổi sang bài khác hay sửa bài thì phải tick lại. Bài mở từ dòng kế hoạch đã có «Mã bài WordPress» thì lời nhắc nêu luôn mã đó.

Đối chiếu xong, muốn tắt lời nhắc thì tự dời file cũ ra khỏi thư mục `data` (hay xóa nếu không cần giữ); phần mềm không tự xóa file. README mục «Gửi nháp» có thêm một đoạn nói việc này.

Thêm một sửa nhỏ về câu chữ: khi chương trình khác sửa đầu file nháp kiểu lạ, lần lưu đầu nay báo «File nháp bị lỗi… Thử tải lại trang» thay vì «đang ở chế độ chỉ đọc» (nói sai nguyên nhân). Tải lại trang thì phần mềm cất file cũ và báo như trên.

## Yêu cầu → cách làm → test

| # | Yêu cầu | Cách làm | Test (`tests/test_t137_nhac_gui_trung.py`) |
|---|---|---|---|
| 1 | Dấu hiệu «đã có file nháp bị cất» theo **tên** `drafts.hong-*.sqlite` trong `data/`: sống qua lần mở lại app, kiểm sau `dir_has_link`, khuôn tên chặt, không mở/đọc file đã cất | `moved_aside_names` (`seo_app/storage/drafts.py:1331`): `dir_has_link` trước (liên kết → rỗng), rồi chỉ liệt kê **tên** (`iterdir`, không `stat`, không mở). Khuôn `_MOVED_TAIL` (`:193`): `<tên>.hong-` + 8 và 6 chữ số **ASCII** + tùy chọn `-N` (N từ 2 tới 9999) + `<đuôi>`, khớp cả tên (`fullmatch`); ngày giờ phải có thật (`strptime`, `:192`). Tên và đuôi lấy từ chính đường dẫn kho (`drafts`, `.sqlite`). Mới nhất trước (giờ, rồi số thứ tự). Mặc định đọc `DEFAULT_DRAFTS_FILE` lúc gọi. Khuôn tên `_move_aside` không đổi từ T-016 (đã xem lịch sử), nên file do bản cũ cất cũng được nhận | `test_names_the_store_gives_are_found_newest_first` (tên do chính kho đặt, kèm file nhật ký không tính, thứ tự), `test_near_miss_names_do_not_count` (21 ca có đối chứng: ngày, giờ, giây không có thật, số thứ tự 0/1/02/10000, nhật ký, đuôi khác, chữ hoa, kho thẻ ảnh, chữ số toàn khối, chữ số Ả Rập…), `test_data_link_gives_nothing` (có đối chứng), `test_missing_or_odd_folder_gives_nothing`, `test_lists_names_only_never_opens_moved_files` (gài theo dõi `os.open`, `os.stat`, `os.lstat`, `open`, `sqlite3.connect`), `test_default_folder_read_at_call_time` |
| 2 | Lời nhắc thường trực ở cột «Đã gửi WordPress» thay «Chưa có bài nào…»; không in đường dẫn đầy đủ | `app/views/home.py:307-313`: có file đã cất thì `st.warning(MSG_SENT_MOVED)` (`:46`) thay dòng «Chưa có bài nào…»; vẫn hiện danh sách bài nếu có (danh sách có thể thiếu). Chỉ tên ngắn của file mới nhất (qua `escape_markdown`), kèm «và N file cũ hơn»; câu nói cách tắt (tự dời file, app không tự xóa) | `test_home_reminder_stays_until_moved_file_is_removed` (lần vẽ sau, phiên mới vẫn nhắc; không đường dẫn; dời file thì hết), `test_home_reminder_counts_older_files_and_keeps_sent_list`, `test_home_near_miss_names_change_nothing`, `test_home_data_link_no_reminder` |
| 3 | Cổng tick ở **mọi** hình thức cho bài **chưa có** dấu «đã gửi» trong kho hiện tại; không tick sẵn; đổi bài, đổi nội dung thì bỏ tick; chỉ thêm cổng; nêu Mã bài WordPress của dòng kế hoạch; bỏ file thì hết | `publish_panel` thêm **một nhánh `elif` thứ ba** sau hai nhánh khóa có sẵn (`app/views/write.py:4459-4461`): bài có trạng thái gửi (đã gửi, đang gửi, gửi dở, dòng hỏng, điều tab biết theo T-092) vẫn đi đúng nhánh cũ; chỉ bài «chưa gửi» mới gặp cổng mới. `moved_box` (`:3368`): lời nhắc `MSG_MOVED_GATE` (`:350`) + ô `MOVED_CHECK_LABEL` (`:357`), không tick sẵn; gắn mã băm của đúng màn hình lúc tick (`remember_moved`, `:3362`, như `confirm_box`): bài đổi (chữ, ảnh, SEO, giờ hẹn, hình thức) thì bỏ tick và nói vì sao (`MSG_MOVED_RESET`). Bỏ tick trước mỗi lần bấm gửi (`_wp_reset_guards`, `:4364-4373`); đổi bài thì `COMPOSE_KEYS` (`:192-193`) xóa; không nằm trong `KEEP_KEYS` nên sang trang khác cũng bỏ. Lúc bấm, `if clicked and allowed` xét lại cổng (cú bấm lọt). `_plan_ref.wp_post_id` là số nguyên (đã qua `DraftPlanRef`) thì thêm câu `MSG_MOVED_PLAN` | `test_gate_in_every_mode` (Nháp, Hẹn giờ, Đăng ngay: không tick sẵn, nút khóa dù đã tick «Tôi đã đọc lại…», tick thì gửi đúng một bài, sau đó khóa cũ T-086), `test_no_moved_file_nothing_changes` (không có file, tên gần giống: như cũ), `test_gate_unticked_when_article_changes`, `test_gate_unticked_when_switching_article`, `test_gate_unticked_after_failed_send`, `test_click_through_gate_sends_nothing` (vá `st.button` theo khóa `wp-send`, có đối chứng), `test_existing_locks_unchanged_with_moved_file`, `test_gate_names_post_id_from_plan_row`, `test_gate_gone_after_moved_file_removed` |
| 4 | G4: mã 8 mà `newer_file_format` đúng → coi là file lạ (cất, `MSG_RECOVERED`), không `_MSG_READONLY` | `_db_message(exc, path)` (`drafts.py:1943`): mã 8 mà đầu file ghi phiên bản lạ → `_MSG_BROKEN`; `_connect` (`:1267`), `_prepare` (`:1310`) truyền `self.path`. `_connect` vốn đặt `_ready = False` với lỗi không phải «bận», nên thao tác kế kiểm lại file, `is_healthy` thấy phiên bản lạ → cất sang một bên, các trang báo `MSG_RECOVERED`. File «chỉ đọc» thật (đầu file đúng) vẫn báo `_MSG_READONLY`, không bị cất. `_db_message` không truyền đường dẫn: như trước (test T-136 giữ nguyên) | `test_g4_newer_format_after_open_is_a_strange_file`, `test_g4_real_read_only_file_still_says_read_only` (đối chứng), `test_db_message_reads_header_only_for_read_only_code` (5 ca), `test_g4_on_compose_page_then_file_moved_and_lock_kept` (trên trang Soạn bài) |
| 5 | Test: hai đường của Soi Lỗi, không có file cất, tên gần giống, `data/` là liên kết, bỏ tick khi đổi bài; vá `st.button` kèm đối chứng; `ids=` ngắn | Như các cột trên, cộng hai ca theo đúng hai đường của Soi Lỗi | `test_route_1_tab_opened_before_send_elsewhere` (Nháp, Hẹn giờ: tab mở trước, tab khác gửi xong, trang khác cất file; khung T-092 «tab không biết»; «Lưu lại thành nháp» rồi vẫn khóa; Hẹn giờ tick «Tôi đã đọc lại…» vẫn khóa), `test_route_2_new_session_after_move` (F5/tab mới và mở lại app: «Bài đang soạn dở» rỗng, trang Bài viết nhắc, viết lại bài thì khóa, website vẫn một bài). Mọi tham số có `ids=` ngắn |
| 6 | README «Gửi nháp»: một đoạn ngắn lời thường | Thêm một gạch đầu dòng cuối danh sách «App nhớ việc đã gửi» (`README.md:527`) | `test_readme_paragraph_matches_page` (nhãn ô tick, tên cột, khuôn tên file, cách tắt, câu app báo đúng `MSG_RECOVERED`) |

## Thiết kế: vì sao thế này

1. **Theo tên file, không theo bộ nhớ.** Biến trong phiên mất khi F5 hay tắt app (đường 2 của Soi Lỗi); tên file còn tới khi người dùng dời đi. Không mở file đã cất (không SQLite, không chép dòng `send_states`): giữ hướng B.2 của T-136, và file đó là dữ liệu chưa tin cậy.
2. **Khuôn tên chặt.** Chỉ đúng tên `_move_aside` đặt; chữ số `[0-9]` (không `\d`: `\d` và cả `strptime` của Python nhận chữ số toàn khối, chữ số Ả Rập ở năm và chữ số thứ hai của ngày, giờ, phút, giây; đột biến Q3 chứng minh); ngày giờ có thật; số thứ tự từ 2 (app không đặt `-1`, `-0`, `-02`). Tên lạ khác trong `data/` không gây nhắc oan.
3. **Chỉ thêm cổng, đặt sau hai nhánh khóa có sẵn.** Bài đã có trạng thái gửi vẫn do khóa cũ giữ (ô «Tạo thêm…», «Tôi đã kiểm tra trang quản trị…»), không chồng thêm ô; các nhánh cũ không đổi một chữ. Bài «chưa gửi» trong kho hiện tại mới cần ô mới, kể cả Nháp (nháp trùng cũng là một bài trên website).
4. **Ô tick theo đúng cách ô xác nhận đang có** (`confirm_box`): gắn mã băm màn hình lúc tick, bỏ trước mỗi lần bấm gửi, đổi bài thì xóa. Mã băm gồm cả hình thức và giờ hẹn, nên đổi hình thức sau khi tick cũng phải tick lại (như ô «Tôi đã đọc lại…»).
5. **G4 chỉ đổi câu chữ.** Đường cất file sau lỗi đã có từ T-131 (`_ready = False`, thao tác kế kiểm lại); chỉ thêm việc đọc đầu file (đúng hàm `newer_file_format` của T-136, 20 byte, chỉ file thường) khi SQLite báo mã 8.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/storage/drafts.py` | `moved_aside_names` (mới, trong `__all__`), `_MOVED_STAMP`, `_MOVED_TAIL`; `_db_message(exc, path)` cho G4 và hai chỗ gọi trong `_connect`, `_prepare`. Không đụng phần giành, ghi trạng thái gửi |
| `app/views/write.py` | Nhánh cổng mới trong `publish_panel`, `moved_box`, `remember_moved`, các câu `MSG_MOVED_*`, `MOVED_CHECK_LABEL`; hai khóa mới trong `COMPOSE_KEYS` và trong danh sách bỏ tick trước khi gửi |
| `app/views/home.py` | Lời nhắc ở cột «Đã gửi WordPress» (`MSG_SENT_MOVED`, `MSG_SENT_MOVED_MORE`); docstring đầu file |
| `README.md` | Một đoạn ở mục «Gửi nháp» (danh sách «App nhớ việc đã gửi») |
| `tests/test_t137_nhac_gui_trung.py` | Mới: 57 ca (dò tên 26, G4 ở kho 7, trang Bài viết 4, bước Xuất bản 14, hai đường của Soi Lỗi 4, G4 trên trang Soạn bài 1, README 1) |

Không đổi test cũ nào (không R5); không `skip`, không `xfail`.

## Thử gỡ chỗ sửa (đột biến)

Script như T-130 (chép cây làm việc ra thư mục nháp, sửa đúng một chỗ, chạy các test được kỳ vọng bắt chỗ đó bằng venv của worktree; đã kiểm `seo_app` nạp từ bản sao; script ở thư mục nháp của phiên, không đưa vào repo). 23 đột biến: **22 bị bắt**, 1 tương đương.

| Đột biến | Kết quả |
|---|---|
| P1 bỏ cổng; P2 cổng chỉ ở Nháp; P3 ô tick sẵn; P4 ô hiện mà không khóa nút; P5 bài đổi không bỏ tick; P6 lần gửi không bỏ tick; P6b lần gửi không bỏ tick lẫn mã băm; P7 khóa «đã gửi» nhường chỗ cho cổng mới (nới khóa); P8 không nêu Mã bài WordPress | cả 9 bị bắt |
| Q1 dò tên chỉ cần chứa khuôn; Q2 không kiểm ngày giờ có thật; Q3 nhận chữ số không phải ASCII; Q4 số thứ tự bất kỳ; Q5 bỏ kiểm liên kết `data/`; Q6 cũ nhất trước; Q7 hỏi `stat` từng file | cả 7 bị bắt |
| R1 trang Bài viết không nhắc; R2 vẫn ghi «Chưa có bài nào…» cạnh lời nhắc; R3 không đếm file cũ hơn | cả 3 bị bắt |
| G1 G4 như cũ; G2 `_connect` không truyền đường dẫn; G3 mã 8 nào cũng báo hỏng (cả chỉ đọc thật) | cả 3 bị bắt |
| P9 bỏ hai khóa mới khỏi `COMPOSE_KEYS` | **không bắt được, tương đương**: đổi bài phải qua bước Chuẩn bị (hay trang khác), Streamlit đã xóa trạng thái ô không vẽ, và mã băm bài khác cũng bỏ tick. Giữ trong `COMPOSE_KEYS` làm lớp thứ ba, như `_wp_confirm` |

Lượt đầu có 2 đột biến sống sót, đã sửa test: **Q3** (hai ca chữ số lạ cũ bị `strptime` từ chối tình cờ; thử lại thấy `strptime` vẫn nhận chữ số toàn khối ở năm, chữ số Ả Rập ở chữ số thứ hai của giây, nên đổi hai ca cho trúng chỗ đó); **P6** (bỏ tick vẫn xảy ra nhờ lớp mã băm, nhưng kèm câu sai «Bài đã thay đổi…»: thêm khẳng định gửi hỏng thì bỏ tick lặng lẽ). Chạy lại: cả hai bị bắt.

## Bảo mật (W1, W2, U1; hướng B.2 của T-136)

- **W1** (không mở thêm đường gửi): chỉ thêm một điều kiện vào `allowed`; luồng gửi, so rồi đặt (T-089), khóa theo điều tab biết (T-092), dòng giữ lại khi xóa (T-130), màn hình xác nhận không đổi. Cú bấm lọt qua nút khóa không gửi gì (có đối chứng). Đột biến P4, P7 (cổng không khóa nút, nới khóa «đã gửi») đều bị bắt.
- **W2** (không đụng website): không thêm lệnh nào tới website, Google; chỉ đọc tên file trong `data/`.
- **U1**: câu nhắc là chữ cố định; tên file chỉ hiện khi khớp khuôn chặt (chữ ASCII cố định) và vẫn qua `escape_markdown`; mã bài là số nguyên đã qua `DraftPlanRef`; không `unsafe_allow_html`; không in đường dẫn đầy đủ (test kiểm đường dẫn thư mục không có trong câu).
- **File đã cất** (B.2 T-136, F3): không mở, không đọc, không `stat`; xét sau `dir_has_link` (liên kết thì bỏ qua, như mọi kho).
- Quét: `PYTHONUTF8=1 uvx detect-secrets scan` 5 file đổi: 1 phát hiện có sẵn (ví dụ `https://tên:mật-khẩu@…` trong docstring `app/views/write.py:2708`, không phải bí mật); `PYTHONUTF8=1 uvx bandit` 3 file nguồn: 2 phát hiện có sẵn ở bản gốc `6a005c1` (B101 `assert` trong `save`; B608 `_oversized_sql` ghép tên bảng, cột hằng), không phát hiện mới.

## Bằng chứng

Chọn file test liên quan (Chỉ Huy dặn không chạy toàn bộ pytest) theo bốn cách: (a) mọi file test nhắc tới trang Soạn bài, trang Bài viết hay `COMPOSE_KEYS`, `_wp_reset_guards`; (b) mọi file test dùng kho nháp, `_db_message`, `sqlite_file`, `dir_has_link` hay đọc README; (c) mọi file test quét mã cả gói (`rglob`); (d) theo phiếu: T-086, T-089, T-092, T-102, T-112, T-117, T-130, T-131, T-136, trang Cài đặt (`test_soi_loi_t084.py`, `test_t101_settings_google.py`), `test_app_pages.py`, `test_ui_escape.py`. Nơi gọi hàm đã sửa: `_db_message` của kho nháp chỉ được gọi trong `drafts.py` (`_connect`, `_prepare`) và `test_t136_kiem_file_chung.py`; bốn kho kia có hàm cùng tên riêng, không đổi; `moved_aside_names` là hàm mới, gọi ở `home.py`, `write.py`.

```
$ PYTHONUTF8=1 uv run --frozen pytest -q -p no:cacheprovider --no-header -rfE \
    tests/test_app_drafts.py tests/test_app_images.py tests/test_app_pages.py \
    tests/test_config_tolerance.py tests/test_content_edge_cases.py tests/test_drafts_images.py \
    tests/test_edit_unescape.py tests/test_images_process.py tests/test_images_tags.py \
    tests/test_la_chan_t056.py tests/test_la_chan_t086.py tests/test_la_chan_t089.py \
    tests/test_la_chan_t093.py tests/test_la_chan_t096.py tests/test_la_chan_t100.py \
    tests/test_la_chan_t102.py tests/test_la_chan_t116_nhom1.py tests/test_la_chan_t131.py \
    tests/test_la_chan_t136.py tests/test_phase2_fixes.py tests/test_plan_sync.py \
    tests/test_search_cache.py tests/test_site_index_t042.py tests/test_soi_loi_round3.py \
    tests/test_soi_loi_round4.py tests/test_soi_loi_round5.py tests/test_soi_loi_t003_t009.py \
    tests/test_soi_loi_t016_t020.py tests/test_soi_loi_t021_t017.py tests/test_soi_loi_t031.py \
    tests/test_soi_loi_t034.py tests/test_soi_loi_t041.py tests/test_soi_loi_t051.py \
    tests/test_soi_loi_t055.py tests/test_soi_loi_t056.py tests/test_soi_loi_t062.py \
    tests/test_soi_loi_t084.py tests/test_soi_loi_t086.py tests/test_soi_loi_t089.py \
    tests/test_soi_loi_t092.py tests/test_soi_loi_t100.py tests/test_soi_loi_t101.py \
    tests/test_soi_loi_t102.py tests/test_soi_loi_t106.py tests/test_soi_loi_t107.py \
    tests/test_soi_loi_t110.py tests/test_soi_loi_t112.py tests/test_soi_loi_t117.py \
    tests/test_soi_loi_t130.py tests/test_soi_loi_t131.py tests/test_soi_loi_t136.py \
    tests/test_storage_drafts.py tests/test_storage_send_state.py tests/test_t041_drafts_seo.py \
    tests/test_t041_links_ai.py tests/test_t041_seo_ui.py tests/test_t062_image_config.py \
    tests/test_t086_send_state.py tests/test_t089_send_draft.py tests/test_t092_nhap_bi_xoa.py \
    tests/test_t100_drafts_plan.py tests/test_t101_home_page.py tests/test_t101_plan_page.py \
    tests/test_t101_settings_google.py tests/test_t102_formula_cells.py tests/test_t102_publish.py \
    tests/test_t103_plan_prompt.py tests/test_t110_gan_anh_vao_bai_nhap.py \
    tests/test_t112_release_rules.py tests/test_t112_settings_switch.py \
    tests/test_t113_website_status.py tests/test_t117_data_dir_links.py \
    tests/test_t124_chuan_hoa_va_cache.py tests/test_t125_tho_may.py \
    tests/test_t130_giu_trang_thai_gui.py tests/test_t131_kho_du_lieu_phu.py \
    tests/test_t131_kho_nhap.py tests/test_t132_don_chu.py tests/test_t136_kiem_file_chung.py \
    tests/test_t137_nhac_gui_trung.py tests/test_ui_escape.py tests/test_wordpress_release.py
5719 passed, 13 skipped, 3 xfailed in 3466.55s (0:57:46)
# 82 file, 2026-11-12 16:49:03 → 17:46:53. Không ca nào hỏng, không XPASS. 3 xfail (strict) có
# sẵn, file không đổi: R4-3 (2 ca, test_soi_loi_round4.py), SL-T107-3 (1). 13 ca bỏ qua do hệ điều
# hành.

$ PYTHONUTF8=1 uv run --frozen pytest -q tests/test_t137_nhac_gui_trung.py   # lần chạy đầu, 56 ca
56 passed in 144.61s (0:02:24)        # ca thứ 57 (gửi hỏng) thêm sau: 1 passed; cả 57 qua ở lượt trên

# Bản test cuối (sau khi sửa 3 ca theo kết quả đột biến Q3, P6), 2026-11-12 17:57:39 → 18:09:08:
$ PYTHONUTF8=1 uv run --frozen pytest -q tests/test_t137_nhac_gui_trung.py
57 passed in 156.60s (0:02:36)
# rồi chạy lại trọn bộ 23 đột biến trên bản này: 22 bị bắt, 1 tương đương (P9)

$ uv run --frozen ruff check .
All checks passed!
$ uv run --frozen ruff format --check tests/test_t137_nhac_gui_trung.py app/views/home.py \
    app/views/write.py seo_app/storage/drafts.py
4 files already formatted
```

Thử nhanh hành vi thật trước khi viết test (script nháp, không đưa vào repo): byte 18 = 3 sau khi kho đã mở → đọc vẫn được, lần lưu báo `_MSG_BROKEN`, thao tác kế cất file, `moved_aside_names` trả đúng tên đó; `strptime` từ chối giây 60, 61, giờ 24, ngày 29/02/2025.

`main` cục bộ nay là `a493c53` (chưa có T-136): từ chỗ tách của T-136 (`71322c4`) `main` không đổi file nào trong `app/`, `seo_app/`, `tests/`, `README.md`.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: dò theo tên, khuôn chặt, sau `dir_has_link`, không mở/đọc file đã cất, còn sau khi mở lại app.
- [x] Yêu cầu 2: lời nhắc thường trực thay «Chưa có bài nào…», tên ngắn, không đường dẫn, nói cách tắt.
- [x] Yêu cầu 3: cổng tick mọi hình thức, không tick sẵn, bỏ tick khi đổi bài/nội dung/sau lần gửi; chỉ thêm cổng; nêu Mã bài WordPress; bỏ file thì hết.
- [x] Yêu cầu 4: G4 báo «bị lỗi», thao tác sau cất file, `MSG_RECOVERED`; «chỉ đọc» thật giữ câu cũ.
- [x] Yêu cầu 5: test hai đường của Soi Lỗi và các ca phiếu nêu; vá `st.button` kèm đối chứng; `ids=` ngắn.
- [x] Yêu cầu 6: README một đoạn lời thường.
- [x] Test liên quan + test mọi nơi gọi + test quét cả gói + `uv run ruff check .`.
- [x] Báo cáo `docs/team/reports/T-137-hoa-si.md`.
- [ ] Soi Lỗi (đầy đủ, chạy lại 52 bước G2), Lá Chắn đầy đủ (chưa tới lượt).

## Rủi ro và điểm cần chú ý

1. **Máy chủ dự án có thể đã có file `drafts.hong-…sqlite` từ trước** (file nháp từng bị cất ở các lần thử): gộp xong là lời nhắc và ô tick hiện ngay, cho mọi bài chưa gửi. Đúng thiết kế; Chỉ Huy nên báo trước cho chủ dự án: xem WordPress rồi dời các file đó ra khỏi `data`. Tôi không xem thư mục đó (đang dùng để thử thật).
2. **Nhắc cho mọi bài «chưa gửi»**, kể cả bài viết mới sau lúc cất (có thể trùng chủ đề bài cũ đã gửi): lặp lại tới khi người dùng dời file. Đây là cách duy nhất nhắc mà không đọc file đã cất.
3. **Đổi tên file đã cất ngay trong `data/`** (không khớp khuôn) cũng tắt nhắc: README chỉ nói «dời ra khỏi thư mục `data`». Số thứ tự trùng giây từ 10000 trở lên không được nhận (không thể xảy ra: mỗi lần cất cần một lần phát hiện file hỏng).
4. **Chỗ đặt file nháp là liên kết** bị cất cũng mang tên `drafts.hong-…` nên cũng nhắc: đúng (dấu «đã gửi» có thể ở file liên kết trỏ tới).
5. Câu bỏ tick «Bài đã thay đổi sau lần bạn tick…» cũng hiện khi chỉ đổi hình thức hay giờ hẹn (mã băm gồm cả hai), như ô «Tôi đã đọc lại…» hiện có.
6. Giao diện kiểm bằng AppTest, chưa mở trình duyệt thật.
7. Nhánh làm từ `team/T-136` (chưa gộp `main`): T-136 gộp xong thì gộp `main` vào `team/T-137` (Chỉ Huy báo).
8. **Ngoài phạm vi (việc tiếp theo đề xuất):** lượt chạy 82 file test tạo `data/site_index.sqlite` ngay trong thư mục chạy test (worktree, 16:57:44; git bỏ qua). `tests/conftest.py` chỉ trỏ kho nháp, kho thẻ ảnh sang thư mục tạm; test có WordPress giả mà không trỏ `site_index.DEFAULT_SITE_INDEX_FILE` (đọc mã: `test_app_images.py`, qua `cached_site_index`) ghi vào file thật. Chạy toàn bộ pytest trong thư mục app chủ dự án đang dùng thì có thể ghi đè cache danh sách bài (dữ liệu giả của `https://example.com`; cache, tải lại được). Nên thêm fixture tự động trong `conftest.py` cho `site_index`, `plan_cache`, `search_cache`.

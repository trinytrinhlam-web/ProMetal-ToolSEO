# Báo cáo T-137 · Nhắc chống gửi trùng sau khi file nháp bị cất sang một bên · Soi Lỗi (đầy đủ)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu | [T-137](../tickets/T-137-nhac-gui-trung-sau-khi-cat-file-nhap.md) (trên `main` `575cd46`) · lỗi gốc: Soi Lỗi T-136 SL-T136-1, G4 (Lá Chắn T-136 lượt 2) |
| Nhánh | `team/T-137` đầu `5daf638` (Họa Sĩ: mã, test `2ee7152`; `5daf638` chỉ thêm 5 dòng vào báo cáo Họa Sĩ; gốc `team/T-136` `6a005c1`). Mọi lần chạy dưới đây trên bản sao `2ee7152`, cùng mã với `5daf638`. Gộp thử `main` cục bộ `0c5d476` (đã có T-136): **không xung đột** (`git merge-tree`, cây `4c31744`); `app/`, `seo_app/`, `tests/`, `README.md`, `config/`, `pyproject.toml`, `uv.lock` của cây gộp **y hệt** nhánh, nên cũng là mã gộp |
| Ngày nộp | 2026-11-18 (giao 2026-11-12 18:02; máy tắt giữa chừng, chạy tiếp từ 2026-11-18 10:12; xong 2026-11-18 11:46, +07, giờ máy) |
| **Kết luận** | **ĐẠT**: 0 lỗi mới (0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp). SL-T136-1 và G4 **đóng**. Chạy lại đúng 52 bước G2 của T-136: 21 bước y hệt (mọi bước của tab đã biết bài đã gửi), 31 bước khác **đúng như phiếu**; 2 lần gửi trùng của bản cũ không còn. Không khóa nào bị nới. 108 file chọn lọc (mọi nơi gọi, ba test trang, quét cả gói): 9.173 qua, 0 hỏng; file test của Soi Lỗi: 31 qua. 5 ghi nhận, không chặn (G-5 ngoài phiếu: test ghi cache danh sách bài vào `data/` của thư mục chạy test; đã giao T-138) |

## Tóm tắt (cho chủ dự án)

- **Lỗi gửi trùng tôi tìm ra ở T-136 đã được vá đúng.** Tôi chạy lại đúng 52 bước thử cũ trên bản mới:
  - hai đường gửi trùng cũ nay đều bị chặn: bài chưa có dấu «đã gửi» phải tick ô **«Tôi đã xem trên WordPress: bài này chưa có trên website»** mới gửi được, ở cả Nháp, Hẹn giờ, Đăng ngay;
  - 2 lần gửi trùng lên website giả ở bản cũ nay không xảy ra;
  - trang **Bài viết** nhắc thường trực, không còn ghi sai «Chưa có bài nào phần mềm đã gửi lên WordPress.»;
  - bài đã có dấu «đã gửi» vẫn khóa như cũ, không thêm ô tick thừa.
- Câu báo sai nguyên nhân («chỉ đọc») khi file nháp bị sửa đầu file nay là «bị lỗi… thử tải lại trang»; file chỉ đọc thật vẫn báo «chỉ đọc».
- Phần mềm chỉ nhìn **tên** file đã cất, không mở file đó.
- **Việc của anh/chị** (sau khi gộp): nếu thư mục `data` của app có file tên dạng `drafts.hong-…sqlite`, ô tick trên sẽ hiện cho mọi bài chưa gửi. Đối chiếu trên WordPress xong thì tự dời file đó ra khỏi thư mục `data` (README mục «Gửi nháp»).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t137.py` | Mới: 31 ca, qua cả 31 (mục 3) |
| `docs/team/reports/T-137-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của Họa Sĩ, không commit file phiếu.

## 1. Chạy lại 52 bước G2 trên mã mới

Cùng ba script của T-136 (`test_g2_probe2.py`, `test_g2_probe3.py`, `test_g2_probe4.py`, thư mục ghi chú chung `T-136-soi-loi-G2-scripts/`), **không sửa một dòng**, chạy trong bản sao `git archive 2ee7152` (thư mục nháp của phiên; kiểm `seo_app` nạp từ bản sao). Nhóm G, H, R là ba đường gây cất file (lần ghi của Soạn bài, trang Bài viết của phiên khác, tắt mở lại app); nhóm CaR đi đúng các bước của ca R trong kịch bản T-128 (số bước là của bộ thử, không phải của kịch bản). So từng bước, từng trường với lần chạy ở T-136 (`2e43ebb`, `348f6f3`): bản mới có 50 bước (2 bước «tab B gửi giả» không còn vì nút khóa), **21 bước y hệt, 31 bước khác**; cả 31 đúng như phiếu:

| Nhóm | Bước | Bản cũ (T-136) | Bản mới (`2ee7152`) |
|---|---|---|---|
| G4 | Đường G 2a: tab đã gửi sửa bài sau khi đầu file bị sửa | «⚠️ Chưa lưu được nháp: File nháp đang ở chế độ chỉ đọc (file hay thư mục data bị đặt «chỉ đọc»…)» | «⚠️ Chưa lưu được nháp: File nháp bị lỗi nên không đọc/ghi được. Thử tải lại trang.» |
| Đường 1 (tab mở bài trước lần gửi ở tab khác) | G, H 7 → 12 (6 bước × 2): sau khi file bị cất, chạy lại, «Lưu lại thành nháp», Nháp, Hẹn giờ, tick «Tôi đã đọc lại…» | Nút gửi **mở**; không lời nhắc ngoài khung T-092 | Lời nhắc «… nên app không biết bài này đã có trên website chưa…», ô **Tôi đã xem trên WordPress…** không tick sẵn, nút **khóa** ở Nháp và Hẹn giờ (dù đã tick «Tôi đã đọc lại…») |
| | G, H 13 | Tab B gửi được: bài thứ 2, lệnh chuyển `future` | **Không còn bước này**: nút khóa, không gửi |
| Hệ quả của việc không gửi trùng | G, H 14, 16, 17 | Kho ghi trạng thái lần gửi trùng của tab B; phiên mới mở lại nháp thấy khóa «đã gửi và hẹn giờ…», website 2 bài | Không có lần gửi trùng: tab A vẫn khóa theo lần gửi của chính nó; phiên mới mở lại nháp (tab B đã lưu lại **không kèm** trạng thái gửi, đúng T-092) gặp **cổng mới**, website 1 bài (ghi nhận G-1) |
| Trang Bài viết | H 2a, 2b; R 2a, 2b; G, H 15; nhóm CaR 4a, 4b, 7a, 8b (10 bước) | Lần vẽ đầu sau khi cất có `MSG_RECOVERED`, sau đó «Chưa có bài nào phần mềm đã gửi lên WordPress.» | Lời nhắc thường trực «… nên danh sách này có thể thiếu bài…» ở mọi lần vẽ, mọi phiên; không còn «Chưa có bài nào…»; danh sách bài (nếu có) vẫn hiện |

21 bước y hệt: mọi bước của **tab đã biết bài đã gửi** (đường G 2b, 3 → 6; H 2c, 3 → 6; R 2c, 3; nhóm CaR 2, 5, 6a → 6c, 7b, 8a, 8c, 8d): `MSG_RECOVERED` khi trang Soạn bài cất file, khung T-092 «Tab này biết bài đã gửi…», khóa «Tạo thêm…», nút mờ, **không** có cổng mới; lưu lại rồi mở lại vẫn khóa.

## 2. Kiểm theo 7 điểm Chỉ Huy giao

| # | Điểm | Kết quả |
|---|---|---|
| 1 | Hai đường gửi trùng có lời nhắc và cổng tick ở mọi hình thức; cột «Đã gửi WordPress» không còn «Chưa có bài nào…» trơn | **Đạt.** Đường 1 Nháp, Hẹn giờ: mục 1 (đường G và H); Đăng ngay: `test_duong_1_dang_ngay…` (tab B mở trước, trang Bài viết của phiên khác cất file). Đường 2 (tắt mở lại app, viết lại bài): `test_duong_2_mo_lai_app_viet_lai_bai`. Trang Bài viết: mục 1 (10 bước), `test_duong_2…` (2 phiên × 2 lần vẽ) |
| 2 | Không nới khóa nào (T-089, T-092, T-130, W1); bài đã có dấu vẫn khóa; không có file cất thì không đổi | **Đạt.** Diff `write.py`: chỉ thêm nhánh `elif` **sau** hai nhánh khóa có sẵn, `allowed = allowed and moved_box(…)`, hai khóa mới trong `COMPOSE_KEYS` và danh sách bỏ tick; `send_and_record`, so rồi đặt, `send_lock_state`, `known_send_state` không đổi dòng nào. Mục 1: 21 bước của tab đã biết y hệt. `test_tab_biet_da_gui…` (khóa «Tạo thêm…» giữ, không cổng mới, cú bấm lọt không gửi). Đột biến M2 (cổng mới thay khóa «đã gửi») bị 3 ca bắt. Không có file cất: ca của Họa Sĩ `test_no_moved_file_nothing_changes` (không, gần giống), 18 tên gần giống của tôi. Lô chọn lọc có đủ test T-086, T-089, T-092, T-102, T-112, T-130 |
| 3 | Dò tên: khuôn chặt, sau `dir_has_link`, không mở/đọc file đã cất; `data/` là liên kết | **Đạt.** Tên do **chính kho** đặt khi cất ba lần cùng giây (`…-143622`, `-2`, `-3`) được nhận, mới nhất trước; chỗ đặt file nháp là junction bị cất cũng tính (chỉ xét tên); 18 tên gần giống (đuôi thêm, nhật ký, số thứ tự 1/02/10000, 7 chữ số, gạch dưới, giờ 24, 30/2, chữ hoa, khoảng trắng đầu, ký tự ẩn, chữ số Ả Rập ở cả ngày hay chỉ ở năm, chữ số toàn khối ở năm, đuôi khác, kho thẻ ảnh, tiền tố) không tính; móc kiểm `sys.addaudithook`: không sự kiện mở file nào trong `data/`, không mở SQLite. `dir_has_link` chạy trước khi liệt kê (đọc mã `drafts.py:1346`, liệt kê ở `:1348`); `data/` là junction thật: ca của Họa Sĩ `test_data_link_gives_nothing`, `test_home_data_link_no_reminder` (có đối chứng) |
| 4 | Ô tick không tick sẵn, bỏ tick khi đổi bài/nội dung/hình thức; không bấm lọt | **Đạt.** Không tick sẵn: mọi ca trang. Đổi hình thức Nháp → Hẹn giờ: bỏ tick, nói vì sao, tick «Tôi đã đọc lại…» chưa đủ (`test_doi_hinh_thuc…`); đổi nội dung, đổi bài, gửi hỏng: ca của Họa Sĩ. Cú bấm lọt (vá `st.button` theo khóa `wp-send`, bật/tắt từng lần chạy): chưa tick không gửi; **đối chứng** đã tick gửi đúng một bài; sau đó khóa «đã gửi», cú bấm lọt nữa không gửi (`test_duong_2…`); tab đã biết: cú bấm lọt không gửi (`test_tab_biet…`) |
| 5 | G4: byte 18 > 2 → cất file, `MSG_RECOVERED`, không còn `_MSG_READONLY` sai nguyên nhân; chỉ đọc thật vẫn «chỉ đọc» | **Đạt.** Kho đang dùng: đọc vẫn được (khóa «đã gửi 501» vẫn đọc ra), lần ghi báo `_MSG_BROKEN`, thao tác sau cất file, dấu «đã gửi» nằm nguyên trong file đã cất. Đối chứng file chỉ đọc thật: `_MSG_READONLY`, không cất. Trên trang: mục 1 (G 2a); bấm gửi đúng lúc file vừa hỏng: không gửi gì lên website (không ghi được «đang gửi»), câu «… chưa ghi được trạng thái gửi vào nháp (File nháp bị lỗi…)», cùng lần chạy đó kho cất file, cổng mới hiện, nút khóa (`test_g4_bam_gui…`) |
| 6 | Câu báo tiếng Việt cố định, không đường dẫn đầy đủ, có escape Markdown; README đúng hành vi | **Đạt.** `MSG_SENT_MOVED`, `MSG_MOVED_GATE`, `MSG_MOVED_PLAN`, `MSG_MOVED_RESET`: chữ cố định; chỉ tên file (đúng khuôn chặt, ký tự ASCII) qua `escape_markdown`; câu nêu Mã bài WordPress của dòng kế hoạch chỉ khi `_plan_ref.wp_post_id` là số nguyên (đọc mã `write.py:3382`; ca của Họa Sĩ `test_gate_names_post_id_from_plan_row`); quan sát mục 1: chỉ tên ngắn, không đường dẫn. README mục «Gửi nháp»: đúng nhãn ô tick, tên cột, khuôn tên, cách tắt (ghi nhận G-4: câu chữ khi có nhiều file) |
| 7 | Test liên quan + mọi nơi gọi + test trang + ruff | **Đạt.** 108 file chọn lọc (mọi nơi gọi, ba test trang, quét cả gói): 9.173 qua, 0 hỏng; file test của Soi Lỗi: 31 qua (mục 6); `ruff check .`, `ruff format --check`: sạch |

## 3. Test độc lập của Soi Lỗi (`tests/test_soi_loi_t137.py`, 31 ca)

| Ca | Kiểm |
|---|---|
| `test_ten_kho_dat_khi_cat_ba_lan_cung_giay_moi_nhat_truoc` | Đồng hồ đứng yên: kho cất ba lần cùng giây, tên do `_move_aside` đặt (`-2`, `-3`) đều nhận, mới nhất trước |
| `test_cho_dat_file_la_lien_ket_bi_cat_cung_tinh` | Junction thật ở chỗ đặt file nháp: kho cất chính liên kết, tên đó tính; nơi trỏ tới còn nguyên |
| `test_ten_gan_giong_khong_tinh` (18) · `test_ten_dung_khuon_duoc_tinh` (3, đối chứng) | Khuôn tên chặt; hai ca năm viết bằng chữ số Ả Rập, chữ số toàn khối (`strptime` vẫn đọc ra năm 2026, chỉ khuôn `[0-9]` chặn) |
| `test_do_ten_khong_mo_file_nao` | `sys.addaudithook`: không mở file trong `data/`, không mở SQLite; có liệt kê thư mục |
| `test_g4_kho_dang_dung_doc_duoc_ghi_bao_hong_roi_cat` · `test_g4_doi_chung_chi_doc_that_khong_cat` | G4 ở kho đã «sẵn sàng»; đối chứng chỉ đọc thật |
| `test_duong_1_dang_ngay_tab_mo_truoc_lan_gui_o_tab_khac` | Đường 1 ở **Đăng ngay** (ca Họa Sĩ có Nháp, Hẹn giờ): cổng, nút khóa dù đã tick «Tôi đã đọc lại…»; tick cổng thì gửi được đúng một bài, rồi khóa «đã gửi» thay cổng |
| `test_doi_hinh_thuc_sau_khi_tick_phai_tick_lai` | Tick ở Nháp, đổi Hẹn giờ: bỏ tick, câu `MSG_MOVED_RESET` |
| `test_duong_2_mo_lai_app_viet_lai_bai` | Tắt mở lại app: Bài viết nhắc ở 2 phiên × 2 lần vẽ, không «Chưa có bài nào…»; viết lại bài: cổng, cú bấm lọt không gửi, đối chứng tick rồi gửi một bài, sau đó khóa |
| `test_g4_bam_gui_luc_file_vua_hong_khong_gui_gi` | Bấm gửi đúng lúc file vừa hỏng (chưa có file đã cất): không lệnh ghi nào tới website, câu «bị lỗi», kho cất file, cổng hiện |
| `test_tab_biet_da_gui_khong_co_cong_moi_khoa_cu_giu` | Tab tự gửi: G4 khi sửa bài, `MSG_RECOVERED`, khung «Tab này biết…», không cổng mới, khóa «Tạo thêm…», cú bấm lọt không gửi |

## 4. Đột biến (test của Soi Lỗi có bắt được không)

Script `mutate137.py` (thư mục ghi chú chung `T-137-soi-loi-scripts/`): chép cây `2ee7152` ra thư mục nháp riêng, sửa đúng một chỗ, chạy **cả** file test của tôi bằng venv của worktree, trả file về bản gốc. Mỗi lượt có một lần chạy bản gốc trước (phải qua hết). Kết quả «error» (lỗi dựng) không tính là bắt.

| Mã | Đột biến | Kết quả | Ca bắt được |
|---|---|---|---|
| M1 | Bỏ cổng ở bước Xuất bản | Bắt | `test_duong_1_dang_ngay…`, `test_doi_hinh_thuc…`, `test_duong_2…` |
| M2 | Có file đã cất thì cổng mới **thay** khóa «đã gửi» (nới khóa) | Bắt | `test_duong_1_dang_ngay…`, `test_duong_2…`, `test_tab_biet_da_gui…` |
| M3 | Ô tick hiện mà không khóa nút | Bắt | `test_duong_1_dang_ngay…`, `test_doi_hinh_thuc…`, `test_duong_2…` |
| M4 | Bài, hình thức đổi mà không bỏ tick | Bắt | `test_doi_hinh_thuc…` |
| M5 | G4 như cũ (mã 8 luôn báo «chỉ đọc») | Bắt | `test_g4_kho_dang_dung…`, `test_g4_bam_gui…`, `test_tab_biet_da_gui…` |
| M6 | Dò tên chỉ cần **chứa** khuôn (`search` thay `fullmatch`) | Bắt | 4 tên gần giống (`duoi-them`, `nhat-ky-wal`, `cach-dau`, `tien-to`), `test_do_ten_khong_mo_file_nao` |
| M7 | Mở từng file đã cất trong lúc dò | Bắt | `test_do_ten_khong_mo_file_nao` (móc kiểm), `test_cho_dat_file_la_lien_ket…` |
| M8 | Cũ nhất trước | Bắt | `test_ten_kho_dat_khi_cat_ba_lan…` |
| M9 | Trang Bài viết vẫn ghi «Chưa có bài nào…» cạnh lời nhắc | Bắt | `test_duong_2…` |
| M10 | Trang Bài viết không nhắc | Bắt | `test_duong_1_dang_ngay…`, `test_duong_2…` |
| M11 | Không kiểm ngày giờ có thật | Bắt | tên gần giống `gio-24`, `30-thang-2` |
| M12 | Nhận chữ số không phải ASCII (`\d` thay `[0-9]`) | **Sống** ở bản 29 ca; thêm 2 ca, bản 31 ca: **Bắt** | `nam-a-rap`, `nam-toan-khoi` (năm viết bằng chữ số Ả Rập, chữ số toàn khối: `strptime` vẫn đọc ra 2026, chỉ khuôn `[0-9]` chặn) |
| M13 | Số thứ tự bất kỳ (`1`, `02`, `10000`) | Bắt | `so-thu-tu-1`, `so-thu-tu-02`, `so-thu-tu-10000` |

**13/13 bị bắt** trên bản test cuối.

Các lượt chạy:

- **Lượt 1** (2026-11-12, bản 28 ca; gốc 28 qua): M1 → M7.
- **Lượt 2** (2026-11-18, bản 29 ca; gốc 29 qua): M5 chạy lại có ca `test_g4_bam_gui…`, rồi M8 → M13.
- **Lượt 3** (bản 31 ca; gốc 31 qua): M12.

Hai sự cố trong lúc chạy:

- Lần thử đầu (12/11) cả 13 đột biến ra «1 error»: thư mục `--basetemp` chưa có. Không tính lần đó; đã sửa script (tạo thư mục, có lần chạy gốc, «error» không tính là bắt) rồi chạy lại.
- Máy tắt giữa lúc M8 đang chạy, nên `drafts.py` trong cây đột biến còn ở dạng đã sửa. Trước lượt 2, tôi trả file về bản gốc bằng `git archive` và kiểm `tar --compare` không còn khác nội dung.

Ca của Họa Sĩ cũng bắt được đột biến kiểu M12 (Q3 trong báo cáo Họa Sĩ).

## 5. R5

`git diff --stat 6a005c1 2ee7152 -- tests/`: chỉ thêm `tests/test_t137_nhac_gui_trung.py`; không test cũ nào bị sửa, xóa, thêm `skip`/`xfail`. Đúng.

## 6. Chạy chọn lọc

Bản sao `git archive 2ee7152` (cùng mã với `5daf638` và với cây gộp `main`), chạy qua `run_list.sh`: script kiểm danh sách trước, thiếu file thì dừng; dòng đầu mỗi lô đã xem («Chạy 27 file chọn lọc…»). Bốn lô nối tiếp, mỗi lúc một tiến trình pytest.

Danh sách 108 file là hợp của hai cách chọn:

- mọi file test nhắc tới trang Soạn bài hay trang Bài viết, kho nháp, `_db_message`, `_MSG_READONLY`, `_MSG_BROKEN`, `MSG_RECOVERED`, README, `COMPOSE_KEYS`, `_wp_reset_guards`, nút `wp-send`, `publish_panel`, hay quét cả gói (`rglob`, `glob`, `iterdir`);
- danh sách 82 file của Họa Sĩ.

Danh sách có đủ test T-086, T-089, T-092, T-102, T-112, T-130, T-136, ba test trang (`test_app_pages.py`, `test_soi_loi_t084.py`, `test_t101_settings_google.py`) và file test của Họa Sĩ. File test của tôi chạy riêng (mục 3).

| Lô | File | Kết quả | Thời gian |
|---|---|---|---|
| 00 | 27 | 2.975 passed, 13 skipped, 5 xfailed | 10 phút 7 giây (2026-11-12) |
| 01 | 27 | 2.305 passed, 2 skipped, 12 xfailed | 14 phút 46 giây (2026-11-18) |
| 02 | 27 | 2.268 passed, 12 skipped | 22 phút 20 giây (2026-11-18) |
| 03 | 27 | 1.625 passed, 6 skipped | 16 phút 58 giây (2026-11-18) |
| **Cộng** | **108** | **9.173 passed, 33 skipped, 17 xfailed, 0 failed, 0 XPASS** | |

Ca bị bỏ qua và ca xfail:

- **Bỏ qua:** đều do Windows (tạo symlink cần Developer Mode, quyền kiểu POSIX, FIFO, `os.environb`, ổ không phân biệt hoa thường).
- **Xfail:** đều có từ trước, không file nào của T-137 (SL-T067-1, SL-T107-3, `test_images_folders_soi_loi` r2, R4-3, SL-T070-4).

Hai lần máy tắt làm đứt lô chạy nền: tối 2026-11-12 (sau lô 00) và khoảng 11:24 ngày 2026-11-18 (giữa lô 03). Sau mỗi lần: kiểm bản sao không đổi nội dung (`tar --compare` với `git archive 2ee7152`), không còn tiến trình cũ, rồi chạy lại trọn lô dở. Lô 01 và lô 03 chạy lại từ đầu; phần đã chạy dở của chúng không tính.

## 7. Ghi nhận (không xếp lỗi)

1. **G-1 · Lưu lại không kèm trạng thái gửi (có từ T-092, nay có cổng che):** ở đường 1, tab B (không biết) bấm «Lưu lại thành nháp» trước tab A: nháp có lại trong kho mà **không** kèm «đã gửi 501». Tab A vẫn khóa theo điều nó biết nhưng không ghi lại vào kho (T-092 chỉ ghi khi chính tab đó bấm «Lưu lại»). Phiên mới mở lại nháp thấy «chưa gửi». Với T-137, khi file đã cất còn trong `data/`, phiên mới gặp cổng mới (mục 1, G, H 17). Người dùng dời file đi rồi thì nháp đó không còn khóa. README đã dặn đối chiếu **mọi** bài trên WordPress trước khi dời file. Đây là hành vi T-092 đã chấp nhận (Soi Lỗi T-092 G1, test `test_draft_saved_back_without_state_keeps_this_tab_locked`). Có thể làm sau: tab biết «đã gửi» thấy nháp có lại mà kho «chưa gửi» thì ghi lại kiểu so rồi đặt, như «Lưu lại thành nháp».
2. **G-2 · Kịch bản T-128 ca R sau khi gộp T-137:**
   - Bước 4: lời nhắc còn mãi (đúng ghi chú «Đã có phiếu sửa»).
   - Bước 6: ghi chú «cả hai trang phải có lời nhắc» chưa khớp. Trang **Soạn bài** chỉ nhắc ở bước **Xuất bản** của bài chưa có dấu «đã gửi» (ô tick). Ở bước Chuẩn bị của tab mới không có bài nào nên không có câu nhắc (mục 1, nhóm CaR bước `7b`).
   - Bước 7, 8: trang Bài viết hiện cả lời nhắc lẫn danh sách bài (mục 1, nhóm CaR bước `8b`). Sau bước 8 (trả file), file `drafts.hong-…` còn trong `data/` tới dòng dọn 12 của mục 6, nên lời nhắc và cổng còn tới lúc đó.
   - Nên sửa câu ở bước 6 khi gộp.
3. **G-3 · Hai khung vàng cùng lúc:** lần vẽ trang Bài viết mà chính trang đó cất file hiện cả `MSG_RECOVERED` lẫn lời nhắc mới (mục 1, H 2a; `test_duong_1…`). Hai câu nói cùng một việc; đúng, chỉ hơi lặp.
4. **G-4 · README khi có nhiều file:** README nói «tự dời file đó ra khỏi thư mục `data`». Có nhiều file `drafts.hong-…` thì phải dời **cả** (câu trên trang đã nói «và N file cũ hơn»). Sửa câu chữ khi tiện.
5. **G-5 · Việc ngoài phiếu, không chặn T-137 (đã có ở Họa Sĩ rủi ro 8, nay xác nhận):**
   - Lô đầu của lần chạy chọn lọc tạo `data/site_index.sqlite` ngay trong thư mục chạy test: bản sao trong thư mục nháp của phiên, 2026-11-12 18:12. Worktree `wt-T-137` cũng có file này từ lượt chạy của Họa Sĩ.
   - Kho này chỉ giữ cache của **một** website. Vì vậy chạy test trong thư mục app chủ dự án đang dùng có thể thay cache danh sách bài thật bằng dữ liệu của WordPress giả. App tải lại được, nhưng trong buổi thử thật thì bước SEO có thể thấy danh sách lạ.
   - Chỉ Huy B đã kiểm (2026-11-18): `data/` của app thật **không** bị ghi; lượt test chạy trong thư mục app sáng 18/11 là bộ test cấu hình AI, không chạm kho này. Từ nay chỉ chạy test ở worktree.
   - Fixture tự động trỏ `site_index`, `plan_cache`, `search_cache` sang thư mục tạm trong `tests/conftest.py` đã giao ở **T-138** (Thợ Máy).

## 8. Lệnh đã chạy

- Bộ G2 (52 bước): `test_g2_probe2.py`, `test_g2_probe3.py`, `test_g2_probe4.py` của T-136, không sửa, chạy trong bản sao `git archive 2ee7152` (`python -m pytest`, thư mục làm việc là bản sao; kiểm `seo_app` nạp từ bản sao): 5 passed. So bằng `diff_steps.py` với lần chạy ở T-136: 21 bước y hệt, 31 bước khác đúng phiếu (mục 1).
- `pytest tests/test_soi_loi_t137.py` (bản sao): **31 passed**.
- Đột biến: `mutate137.py`, 13/13 bị bắt (mục 4).
- Chạy chọn lọc: `run_list.sh` (kiểm danh sách, thiếu file thì dừng; đã xem dòng đầu mỗi lô), 108 file, 4 lô nối tiếp (mục 6).
- `git merge-tree --write-tree main 5daf638` (`main` cục bộ `0c5d476`): không xung đột; so mã cây gộp với nhánh: y hệt.
- `git diff --stat 6a005c1 2ee7152 -- tests/`: R5 (mục 5).
- `uv run --frozen ruff check .` (worktree, có file test mới): sạch («All checks passed!»); `ruff format --check tests/test_soi_loi_t137.py`: đúng khuôn.
- `detect-secrets` (`PYTHONUTF8=1`, quét bản sao 8 file trong thư mục ngoài git cùng file mồi tiếng Việt, `--all-files`): mồi bị bắt (quét chạy đúng); 2 phát hiện có sẵn, đều là ví dụ địa chỉ web kèm `tên:mật-khẩu@` trong docstring (`app/views/write.py:2708`, có từ trước T-137, Họa Sĩ đã ghi) và báo cáo Họa Sĩ nhắc lại ví dụ đó; file test mới và báo cáo này: 0.
- Script, danh sách file, quan sát G2: thư mục ghi chú chung `T-137-soi-loi-scripts/`.

# Báo cáo T-132 · Dọn chữ Giai đoạn 4: trang Kết nối khuyên đúng tài khoản Biên tập viên, vài lỗi Thấp meta

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-132](../tickets/T-132-don-chu-giai-doan-4.md) |
| Nhánh | `team/T-132` (từ `main` `f6a6e64`) |
| Ngày nộp | 2026-11-05 14:39 (+07:00, theo lệnh `date`); lượt 2: 2026-11-07 09:38 |
| Kết quả | Hoàn thành: mục bắt buộc và cả 4 mục tùy chọn; lượt 2: SL-T132-1, SL-T132-2 đã sửa |

## Tóm tắt (cho chủ dự án)

- **Trang Kết nối WordPress** (điều kiện đóng Giai đoạn 4): khi tài khoản thiếu quyền viết bài hay tải ảnh, trang chỉ khuyên dùng **một tài khoản riêng ở vai Biên tập viên**. Câu cũ còn khuyên «hoặc Quản trị viên», trái quyết định 2A; nay đã bỏ.
- **Bước SEO**: dưới ô «Dùng schema Hỏi đáp (FAQ) này cho bài» có thêm dòng «Ô này chỉ ghi nhớ lựa chọn trong nháp: app chưa gửi schema lên website.», để không ai tưởng schema đã lên website.
- **Gửi nháp có ghi SEO**: ghi xong, phần mềm hỏi lại website xem bài còn là nháp không. Nếu lần hỏi lại này lỗi mạng, câu báo cũ tự mâu thuẫn: vừa nói «Đã ghi SEO», vừa nói «trước khi ghi SEO… Chưa ghi gì». Nay câu báo nói đúng: SEO đã ghi, chỉ chưa hỏi lại được bài, nên mở bài trong trang quản trị để xem.
- **Lọc gợi ý meta của AI** bắt thêm:
  - vài cách nói giá: «chỉ 5 trăm», «triệu rưỡi», «giá tính bằng VNĐ»;
  - vài dạng tên miền lạ: «EVIL.SHOP», «evil[.]com», đuôi chữ Nga («evil.рф»), dấu chấm kiểu Trung Quốc.
- Các viết tắt địa danh như «TP.HCM», «TP.HN», «Q.GV», và số đếm như «hơn 5 trăm công trình» **không** bị bắt oan.
- Không thêm thư viện. Test không gọi website hay AI thật.

## Từng mục của phiếu: làm hay không

| Mục | Làm? | Cách làm |
|---|---|---|
| 1 · SL-T106-1 (bắt buộc) | **Làm** | <ul><li>`app/views/wordpress.py:131-136`: câu mới «Tài khoản thiếu quyền viết bài hoặc tải ảnh. Phần mềm cần một tài khoản riêng ở vai trò **Biên tập viên (Editor)**: nhờ người quản trị website kiểm tra vai trò của tài khoản này.»</li><li>Câu không có chữ «GPS», nên các ca đếm câu báo GPS của T-106 không đổi.</li><li>«Người quản trị website» là người, không phải vai: cùng cách nói với câu GPS ngay dưới (`wordpress.py:77`).</li><li>Gỡ `xfail` (R5, chỉ xóa dấu): xem mục «Gỡ dấu xfail».</li></ul> |
| 2a · LC-T036-2 | **Làm** | `seo_app/onpage/meta.py` (`has_link`), chi tiết ở dòng sau |
| 2b · SL-T036-11 | **Làm** | `seo_app/onpage/meta.py` (`_PRICE`), chi tiết ở dòng sau |
| 2c · Chú thích ô schema FAQ | **Làm** | <ul><li>`app/views/write.py:2823`: `st.caption(MSG_FAQ_NOT_SENT)` ngay dưới ô, chỉ hiện khi có ô.</li><li>Câu: `write.py:2435`, cùng ý README mục 10.</li></ul> |
| 2d · Hàm công khai thay `client._own_draft` | **Làm** | <ul><li>`WordPressClient.recheck_draft(post_id)` (`seo_app/wordpress/client.py:1343-1355`).</li><li>Chỉ nhận nháp chính client này tạo (như `set_seo_meta`), không thì `_RECHECK_NOT_OWN`, 0 lệnh.</li><li>Rồi gọi `_own_draft(post_id, failed=_RECHECK_FAILED)`: cùng một lệnh `GET` chỉ đọc, cùng xử lý bài đã đăng (`_SEO_NOT_DRAFT`, client thôi coi là của app) và bài bị sửa ngoài app (đánh dấu «không biết», T-115).</li><li>`write_seo` (`write.py:2960`) gọi hàm này; `app/` không còn chỗ nào đọc `client._…`.</li><li>**Phát hiện thêm, sửa kèm:** câu báo khi không hỏi lại được. Trước đây là `_SEO_CHECK_FAILED` («…trước khi ghi SEO. Chưa ghi gì…»), nối sau «Đã ghi SEO…». Nay là `_RECHECK_FAILED` (`client.py:469`).</li></ul> |

Chi tiết 2a (LC-T036-2), trên chữ đã NFKC như cũ:

| Dạng Lá Chắn T-036 nêu | Cách bắt |
|---|---|
| `evil。com` | `has_link` đổi dấu chấm Hán «。» thành «.» trước khi dò. NFKC đã đổi «｡» nửa khổ thành «。», «．» toàn khổ thành «.» |
| `evil[.]com` | `_LINK` thêm dấu chấm kiểu né liền chữ hai bên: `[.]`, `(.)`, `[dot]`, `(dot)` |
| `evil.xn--p1ai` | `_LINK` thêm nhãn punycode `xn--` (đầu nhãn) |
| `EVIL.SHOP` | `_BARE_DOMAIN` thêm dạng toàn chữ HOA khi nhãn cũng toàn HOA và dài từ 3 ký tự. Nhờ vậy «TP.HCM», «TP.HN», «Q.GV», «TP.BMT», «TX.TDM» không bị bắt; đuôi hoa chữ đầu («sat.Xem», đang ghim) vẫn không tính |
| `evil.рф` | `_ANY_TLD` + `_foreign_tld`: đuôi toàn chữ cái mà **không có chữ Latin nào** (theo tên Unicode). Chữ Việt có dấu là chữ Latin, nên «xong.tiếp», «XONG.TIẾP» không bị bắt |

Chi tiết 2b (SL-T036-11), thêm vào `_PRICE`:

- **«chữ số + trăm» nói trống** («5 trăm», «chỉ 5 trăm», «giá 5 trăm/m2»): là giá, trừ khi ngay sau là đơn vị đo, thời gian hay danh từ đếm (`_NOT_MONEY_AFTER_HUNDRED`). Ví dụ không tính: «hơn 5 trăm công trình», «cách 3 trăm mét», «4 trăm m2», «2 trăm khách hàng».
- **«trăm/nghìn/ngàn/triệu/tỷ/tỉ rưỡi»**: là giá.
- **Tên tiền đứng riêng** «VNĐ», «VND», «USD», «đô la»: là giá («vndirect», «usda» không tính).
- Ca SL-T036-10 «2 đô vật» vẫn bị coi là giá như cũ (`xfail` đó giữ nguyên, vẫn XFAIL).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `app/views/wordpress.py` | Câu cảnh báo thiếu quyền chỉ khuyên vai Biên tập viên (SL-T106-1) |
| `app/views/write.py` | <ul><li>Thêm hằng `MSG_FAQ_NOT_SENT` và dòng chú thích trong `faq_panel` (bước SEO).</li><li>`write_seo` gọi `client.recheck_draft(post_id)` thay `client._own_draft(post_id)`.</li><li>Không đụng bước Xuất bản, phần xóa nháp (T-130).</li></ul> |
| `seo_app/wordpress/client.py` | Thêm `recheck_draft` (công khai, chỉ đọc), câu `_RECHECK_NOT_OWN`, `_RECHECK_FAILED`. Hàm cũ không đổi |
| `seo_app/onpage/meta.py` | `_LINK`, `_BARE_DOMAIN`, `_ANY_TLD` + `_foreign_tld`, `has_link` (LC-T036-2); `_NOT_MONEY_AFTER_HUNDRED`, `_PRICE` (SL-T036-11) |
| `tests/test_soi_loi_t106.py` | Chỉ xóa dấu `xfail` SL-T106-1 |
| `tests/test_soi_loi_t036.py` | Chỉ xóa dấu `xfail` SL-T036-11 |
| `tests/test_t132_don_chu.py` (mới) | 15 hàm test, 70 ca: `recheck_draft`, `write_seo`, chú thích FAQ, dò giá, dò link |
| `tests/test_t132_trang_ket_noi.py` (mới) | 2 hàm test, 6 ca: câu thiếu quyền trên trang Kết nối |
| `docs/team/reports/T-132-tho-may.md` | Báo cáo này |

Không sửa `README.md` (mục 6 bước 10 và mục 10 đã nói đúng: dùng tài khoản Biên tập viên, app chưa gửi schema lên website), `config/**`, `pyproject.toml`, `uv.lock`.

## Gỡ dấu xfail (R5: chỉ xóa dấu, phiếu đã cho)

| File | Ca | Dấu đã xóa | Bằng chứng trước khi xóa |
|---|---|---|---|
| `tests/test_soi_loi_t106.py` (dòng 296-299 cũ) | `test_sl_t106_1_trang_khong_khuyen_nang_len_quan_tri` (2 ca: `contributor`, `khong-ro-quyen`) | `xfail(strict=True, reason="SL-T106-1: …")` | Chạy với dấu: `2 failed` vì `[XPASS(strict)]` cả 2 ca |
| `tests/test_soi_loi_t036.py` (dòng 664 cũ) | `test_r2_price_forms_still_missed` (4 ca: «5 trăm», «chỉ 5 trăm», «triệu rưỡi», «giá tính bằng VNĐ») | `xfail(strict=True, reason="SL-T036-11: …")` | Chạy với dấu: `4 failed` vì `[XPASS(strict)]` cả 4 ca; `test_r2_do_vat_not_price` vẫn `1 xfailed` |

Không đổi thân test, tham số hay docstring của hai ca.

## Bằng chứng

```
$ uv run pytest <66 file liên quan> -q -rfEX     # 13:47 → 14:37, không chạy toàn bộ pytest
7968 passed, 1 skipped, 1 xfailed in 3021.25s (0:50:21)
```

66 file gồm:

- **Trang Kết nối:** `test_soi_loi_t106`, `test_t106_trang_ket_noi`, `test_app_wordpress`, `test_soi_loi_t044`, `test_t132_trang_ket_noi`.
- **Meta, link** (mọi nơi gọi `mentions_price`, `has_link`): `test_soi_loi_t036`, `test_onpage_meta`, `test_t041_meta`, `test_la_chan_t040`, `test_soi_loi_t041`, `test_la_chan_t041`, `test_t040_prompts`, `test_onpage_links`, `test_soi_loi_t039`, `test_la_chan_t039`, `test_t041_links_ai`.
- **Bước SEO, Xuất bản:** `test_t041_seo_ui`, `test_t041_schema`, `test_t041_drafts_seo`, `test_soi_loi_t112`, `test_t112_release_rules`, `test_la_chan_t102`, `test_soi_loi_t102`, `test_t102_publish`, `test_app_images`.
- **Client WordPress** (mọi file test đụng `set_seo_meta`, `_own_draft`, `modified_gmt`, `release_draft`): `test_content_edge_cases`, `test_la_chan_t060`, `test_la_chan_t099`, `test_phase2_fixes`, `test_shortcode_t061`, `test_site_index`, `test_soi_loi_t037`, `test_soi_loi_t042`, `test_soi_loi_t042_round2`, `test_soi_loi_t054`, `test_soi_loi_t059`, `test_soi_loi_t060`, `test_soi_loi_t061`, `test_soi_loi_t085`, `test_soi_loi_t088`, `test_soi_loi_t091`, `test_soi_loi_t099`, `test_soi_loi_t110`, `test_soi_loi_t113`, `test_soi_loi_t115`, `test_t059_siet_ghi_seo_va_srcset`, `test_t091_don_client_wordpress`, `test_t101_home_page`, `test_t101_plan_page`, `test_t113_website_status`, `test_t115_modified_gmt`, `test_wordpress_images`, `test_wordpress_published`, `test_wordpress_release`, `test_wordpress_round2_t042`, `test_wordpress_seo_meta_t042`, `test_wordpress_t060`, `test_wordpress_t085`, `test_wordpress_routes_t042`, `test_t110_gan_anh_vao_bai_nhap`.
- **Test quét cả mã nguồn `app/`, `seo_app/`:** `test_la_chan_t096`, `test_soi_loi_t034`, `test_t103_plan_prompt`, `test_app_pages`, `test_images_process`.
- **Test mới:** `test_t132_don_chu`.

Ghi chú về kết quả:

- 1 `xfailed` là ca «đô vật» SL-T036-10, giữ nguyên.
- 1 `skipped` có sẵn, không phải ca mới: 76 ca mới đều qua, không bỏ qua ca nào.
- Sau khi định dạng lại `test_t132_trang_ket_noi.py` (chỉ đổi cách xuống dòng), chạy lại riêng: `102 passed` (2 file mới cùng `test_soi_loi_t106`).

```
$ uv run ruff check .
All checks passed!
```

- `ruff format --check`: lệch ở `app/views/wordpress.py` (5 dòng), `seo_app/wordpress/client.py` (8 dòng), `tests/test_soi_loi_t106.py` (123 dòng). Cả ba lệch **y hệt trên HEAD `f6a6e64`** và không nằm ở dòng mình sửa. Hai file test mới đã định dạng.
- **Đối chứng câu báo hỏi lại:** tạm cho `recheck_draft` gọi `_own_draft(post_id)` như chỗ gọi cũ (câu `_SEO_CHECK_FAILED`). Kết quả: `5 failed` (4 ca client «hỏi không được», 1 ca trang «câu không tự mâu thuẫn»). Trả lại code (`grep` xác nhận), chạy lại thì qua.
- **Ca giao diện:** `test_hoi_lai_sau_khi_ghi_seo_khong_duoc_thi_cau_khong_tu_mau_thuan`.
  - Bật «Ghi SEO», gửi nháp. Lần đọc bài thứ 2 (hỏi lại sau khi ghi) trả 500.
  - Câu kết quả bắt đầu bằng «Đã ghi SEO vào hộp SiteSEO của bài nháp.», có «Không hỏi lại được bài trên WordPress (mã 500)».
  - Không có «Chưa ghi gì», «trước khi ghi», không chép lời máy chủ.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1 (bắt buộc): trang chỉ khuyên Biên tập viên.
  - Bằng chứng: `test_sl_t106_1_trang_khong_khuyen_nang_len_quan_tri` qua, không còn dấu.
  - Ca mới: `test_thieu_quyen_chi_khuyen_bien_tap_vien` (4 ca: cộng tác viên, người đăng ký, tác giả không tải ảnh, website không cho biết quyền) và `test_du_quyen_thi_khong_co_cau_thieu_quyen`.
- [x] Yêu cầu 2: cả 4 mục tùy chọn đều làm (bảng trên).
- [x] Yêu cầu 3: không đụng bước Xuất bản, phần xóa nháp của `write.py`.
  - Diff `write.py` chỉ có: một hằng câu cạnh `MSG_SEO_RECHECK`, một dòng trong `faq_panel`, một dòng trong `write_seo` (chỗ gọi `_own_draft`, phiếu cho sửa).
- [x] Test liên quan và `uv run ruff check .` (mục Bằng chứng); báo cáo này.

## Rủi ro và điểm cần chú ý

1. **«Chữ số + trăm»:**
   - Danh sách đơn vị và danh từ đếm không đủ mọi danh từ. Danh từ ngoài danh sách («5 trăm gia đình»; lượt 1 ghi nhầm ví dụ «5 trăm thợ», mà «thợ» có trong danh sách, Soi Lỗi GN-2) bị coi là giá: gợi ý AI đó bị bỏ. Lệch về phía an toàn, như các đơn vị khác của `_PRICE`.
   - Số viết bằng chữ đứng trống («năm trăm» không kèm đơn vị) vẫn chưa bắt. Không thuộc 4 ca SL-T036-11; bắt sẽ đụng «năm» (năm tháng).
2. **`mentions_price` còn dùng cho ghi chú dòng kế hoạch** (`write.py:775`, `fill_from_plan` → `MSG_PLAN_PRICE`):
   - Ghi chú có «VNĐ», «5 trăm», «triệu rưỡi» nay cũng nhận câu nhắc «Ghi chú của dòng kế hoạch có nhắc giá». Chỉ là câu nhắc, không chặn gì.
   - Bộ dò giá riêng của trang Kế hoạch (`seo_app/plan/propose.py`) không đổi.
3. **Dò link** còn sót vài dạng (đổi lại để không bắt oan viết tắt địa danh):
   - «Evil.Shop» (hoa chữ đầu, cùng dạng «sat.Xem» đang ghim là không phải link);
   - «AB.SHOP» (nhãn HOA dưới 3 ký tự);
   - «evil [.] com» (có dấu cách).
   - Viết tắt toàn HOA từ 3 ký tự kiểu «KCN.VSIP» bị coi là link (lệch an toàn).
4. **`has_link` cũng kiểm cụm từ neo** liên kết nội bộ (`seo_app/onpage/links.py:433`):
   - Cụm từ neo mang các dạng mới trên bị từ chối «trông như địa chỉ web».
   - Cụm từ lấy từ chính bài tiếng Việt nên gần như không gặp. Cụm có `[`, `]` vốn đã bị từ chối trước đó.
5. **Câu `_SEO_NOT_DRAFT` khi hỏi lại thấy bài đã đăng:** giữ nguyên câu cũ («…Phần mềm không sửa bài đã đăng (không ghi SEO, không đổi ảnh đại diện)…»).
   - Câu đúng nghĩa (không ghi thêm gì nữa).
   - Test `test_post_published_during_seo_write_is_reported` ghim «không còn là bản nháp».
6. **`recheck_draft` giữ nguyên mọi hành vi của lần hỏi lại cũ**, kể cả khi `modified_gmt` của bài đổi sau lệnh ghi SEO qua Abilities.
   - Khi đó client đánh dấu «không biết giờ sửa», và «Hẹn giờ», «Đăng ngay» sẽ không chuyển bài (T-115).
   - Ghi SEO qua Abilities có đổi `modified_gmt` hay không là mục LC-T094-44 (b) của buổi thử thật T-128. Phiếu này không đổi chỗ đó.

## Đề xuất

- Khi có phiếu đưa schema FAQ lên website (cách d mục 3.3 của T-033), sửa lại câu `MSG_FAQ_NOT_SENT`.
- Soi Lỗi, Lá Chắn rút gọn (theo phiếu). Phần client chỉ thêm một hàm đọc, không đổi đường gọi (`_ALLOWED_ROUTES`), không có lệnh ghi mới.

## Câu hỏi cho chủ dự án

Không có.

## Lượt 2 (sửa 2 lỗi Thấp của Soi Lỗi)

Theo biên bản Soi Lỗi `docs/team/reports/T-132-soi-loi.md` (`ce6c4fd`, ĐẠT CÓ ĐIỀU KIỆN).

File đã sửa:

- `seo_app/onpage/meta.py`: chỉ phần dò link, dò giá.
- `tests/test_soi_loi_t132.py`: chỉ xóa 2 dấu `xfail`.
- `tests/test_t132_don_chu.py`: thêm test.
- Báo cáo này.

### Tóm tắt (cho chủ dự án)

- Bộ lọc gợi ý meta của AI nay bắt cả **tên miền giả dạng** dùng chữ Nga, chữ Hy Lạp trông y hệt chữ thường: «evil.cоm» (chữ «о» Nga) hiện trên Google giống hệt «evil.com», trước đây lọt, nay gợi ý đó bị bỏ.
- Bắt thêm cách viết giá **«đôla»** viết liền và «đô-la» («chỉ 20 đôla»).
- Câu thường có ký hiệu Hy Lạp hay chữ Nga hợp lệ không bị bắt oan: đơn vị «μm», «π», «Ω», «Ø60», chuẩn thép «ГОСТ».

### Đã sửa

| Mã | Cách sửa |
|---|---|
| **SL-T132-1** | <ul><li>`_foreign_tld` (chỉ bắt đuôi tên miền **không có** chữ Latin nào) thay bằng `_foreign_domain`.</li><li>«Chữ lạ» (`_foreign_letter`) là chữ cái không phải chữ ASCII, không phải chữ Việt. Chữ Việt là chữ ASCII hay «đ» thêm dấu thanh, dấu mũ của tiếng Việt, xét sau NFD (`_VIET_MARKS`).</li><li>Chuỗi dạng tên miền (`_DOTTED`: các nhãn nối bằng dấu chấm, nhãn cuối toàn chữ cái) bị coi là link khi: có chữ lạ, **và** đuôi có chữ lạ hay toàn chữ ASCII thường/HOA.</li><li>Bắt được 5 ca của Soi Lỗi: «evil.cоm», «evil.соm», «evil.cοm», «evil.shоp», «EVIL.SHОP».</li><li>Bắt thêm các dạng cùng loại:<ul><li>chữ lạ ở **nhãn** mà đuôi là chữ ASCII («еvil.shop», «ЕVIL.SHOP»);</li><li>chữ Latin ngoài tiếng Việt trông y hệt chữ thường (U+1D0F chữ O hoa nhỏ, U+0261 «g» viết tay);</li><li>tên miền nhiều tầng («ví-dụ.evil.cоm», «a.b.cоm»).</li></ul></li></ul> |
| **SL-T132-2** | <ul><li>`_MONEY_UNIT`: `đô(?:\s*-?\s*la)?` thay `đô(?:\s+la)?`, nên nhận «20 đôla», «hai đôla».</li><li>Luật tên tiền đứng riêng: `đô\s*-?\s*la` thay `đô\s+la`, nên nhận «tính bằng đôla», «tính bằng đô-la», «đô - la».</li></ul> |
| GN-3 (một phần) | `_LINK` nhận thêm ngoặc nhọn trong dấu chấm kiểu né («evil{.}com», «evil{dot}com»). Không có rủi ro bắt oan |

Không bắt oan (ca đang ghim và ca mới):

- 14 câu thường của Soi Lỗi (`test_cau_thuong_khong_bi_coi_la_link`) và các viết tắt địa danh của lượt 1.
- Câu có chữ Hy Lạp, chữ Nga hợp lệ (`test_cau_thuong_co_chu_hy_lap_kirin_khong_bi_coi_la_link`, 10 ca), kể cả khi thiếu dấu cách sau dấu chấm: «Sơn dày 60µm.Bền màu» (NFKC đổi «µ» thành «μ» Hy Lạp), «Lớp mạ 80μm. Bảo hành», «Thép đạt chuẩn ГОСТ.Bền chắc», «Thép chuẩn ГОСТ 8240», «Hệ số ma sát μ = 0.3», «Diện tích π.r²», «Ống Ø60.Mạ kẽm», «Điện trở 5Ω.Chống giật», «Thép α.β».
  - Lý do: đuôi là chữ Việt hay viết hoa chữ đầu, hoặc không có đuôi chữ cái dài từ 2 ký tự.
- Giá: «đô lá», «thủ đô Hà Nội», «khu đô thị» không bị coi là giá; ca «2 đô vật» (SL-T036-10) vẫn `xfail` như cũ.

### Gỡ dấu xfail (R5: chỉ xóa dấu, Chỉ Huy đã duyệt)

| File | Ca | Bằng chứng trước khi xóa |
|---|---|---|
| `tests/test_soi_loi_t132.py` (dòng 80-84 cũ) | `test_sl_t132_1_duoi_ten_mien_tron_chu_bi_bat` (5 ca) | `[XPASS(strict)]` cả 5 ca |
| `tests/test_soi_loi_t132.py` (dòng 129-132 cũ) | `test_sl_t132_2_dola_viet_lien_bi_bat` (3 ca) | `[XPASS(strict)]` cả 3 ca |

Không đổi thân test, tham số hay docstring.

### Test

- `tests/test_t132_don_chu.py` thêm 5 hàm test, 28 ca (mục «5. lượt 2»): tên miền trộn chữ ở nhãn hay đuôi (9), câu thường có chữ Hy Lạp, Kirin (10), dấu chấm ngoặc nhọn (2), «đôla» các cách viết (4), «đô» không phải tiền (3).
- **Đối chứng:** tạm đặt lại `meta.py` bản lượt 1 (HEAD `ce6c4fd`).
  - Kết quả: `18 failed` (8 ca của Soi Lỗi, 10 ca mới của mình). Hai ca mới vẫn qua trên bản cũ, vì vốn đã bị bắt bằng luật khác: «evil.bız» khớp «biz» khi không phân biệt hoa thường; «shop.evil.cоm» khớp «shop.evil».
  - Trả lại bản mới, mã băm file khớp trước và sau.
  - Hai ca ngoặc nhọn thêm sau lần đối chứng đó, kiểm riêng: nạp `meta.py` của HEAD từ `git show`, `has_link` trả `False` cho «evil{.}com», «EVIL{DOT}SHOP»; bản mới trả `True`.
- **Thời gian:** `has_link` trên 10 chuỗi 1.000 ký tự dựng xấu nhất mất tối đa 16,7 ms (lấy lần nhanh nhất trong 5 lần đo). Các chuỗi gồm «a.» ×500, «a-» ×500, «а.» Kirin ×500, nhãn dài 990 chữ… Soi Lỗi đo lượt 1: ≤ 20 ms.

```
$ uv run pytest <25 file, mọi nơi gọi has_link, mentions_price> -q -rfEX    # 09:15 → 09:27
2296 passed, 1 xfailed in 714.33s (0:11:54)
$ uv run pytest tests/test_images_process.py -k ma_nguon                    # ca quét mã nguồn seo_app/
1 passed, 138 deselected
$ uv run pytest <17 file có dùng bộ dò link, sau khi thêm ngoặc nhọn> -q -rfEX   # 09:28 → 09:37
1944 passed, 1 xfailed in 572.40s (0:09:32)
$ uv run ruff check .
All checks passed!
```

Các file test đã chạy:

- **Bộ lọc gợi ý meta và quy trình gợi ý** (`filter_ai_titles`, `filter_ai_descriptions` của `seo_app/content/workflow.py`): `test_onpage_meta`, `test_soi_loi_t036`, `test_t041_meta`, `test_la_chan_t040`, `test_soi_loi_t040`, `test_soi_loi_t041`, `test_la_chan_t041`, `test_t040_prompts`, `test_t090_meta_emoji_moi`, `test_content_workflow`.
- **Test của phiếu:** `test_soi_loi_t132`, `test_t132_don_chu`.
- **Cụm từ neo liên kết nội bộ** (`links.py:433`): `test_onpage_links`, `test_soi_loi_t039`, `test_la_chan_t039`, `test_t041_links_ai`.
- **Bước SEO:** `test_t041_seo_ui`.
- **Câu nhắc ghi chú kế hoạch** (`write.py:775`): `test_t101_home_page`, `test_t101_plan_page`, `test_la_chan_t100`, `test_la_chan_t103`.
- **Quét mã nguồn:** `test_la_chan_t096`, `test_soi_loi_t034`, `test_t103_plan_prompt`, `test_app_pages`.
- Đợt thứ ba chỉ gồm 17 file có dùng bộ dò link (bộ lọc meta, cụm từ neo, bước SEO, test của phiếu, quét ký tự đảo chiều).
- 1 `xfailed` ở cả hai đợt là ca «đô vật» SL-T036-10, giữ nguyên. Không chạy toàn bộ pytest.

### Còn lại (không sửa, lệch về phía an toàn hay ngoài phạm vi)

- **Bắt oan có thể có:** chữ lạ hợp lệ đứng sát dấu chấm, sau đó là một từ ASCII toàn chữ thường hay toàn HOA, không dấu cách («60μm.ben», «Ø60.ma», «ГОСТ.BEN»). Cùng loại với «60um.ben» mà luật cũ vốn đã bắt. Chữ Latin ngoài tiếng Việt cũng là chữ lạ, nên «Munich.Müller» bị bắt.
- **Soi Lỗi GN-3 chưa làm:**
  - «evil.SHOP» (nhãn thường, đuôi HOA): bắt dạng này sẽ bắt oan câu thiếu dấu cách kiểu «uy tin.HOTLINE», «giao nhanh.FREESHIP»;
  - «Evil.Shop», «AB.SHOP», «evil [.] com»: như lượt 1.
- **«thủ đô La Mã», «thủ đô La Paz»** bị coi là giá (có từ lượt 1, luật «đô la» đứng riêng).
- **Soi Lỗi GN-1, GN-2, GN-4, GN-5:** ngoài 2 lỗi được giao, không đổi.

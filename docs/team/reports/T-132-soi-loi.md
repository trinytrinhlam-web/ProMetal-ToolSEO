# Báo cáo T-132 · Dọn chữ Giai đoạn 4 · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | T-132 «Dọn chữ Giai đoạn 4» · mức kiểm **rút gọn**, Windows. Không gọi website, AI thật; không chạy cloud |
| Ngày nộp | 2026-11-07 |
| Máy kiểm | Windows 11 Pro 10.0.26300, Python 3.12.15. App khởi động lại khoảng 08:00: worktree gộp thử bị hỏng (HEAD rỗng), đã gỡ và dựng lại; mọi lượt chạy trong báo cáo là lượt sau đó |
| Mã nguồn | `team/T-132` tại `1c8bba7` (gốc `main` `f6a6e64`). Gộp thử với `main` cục bộ `06a1b0e` (đã có T-124, cũng sửa `client.py`) |
| Kết quả | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **2 Thấp mới** (SL-T132-1: đuôi tên miền trộn chữ Kirin «evil.cоm» lọt bộ dò link; SL-T132-2: «đôla» viết liền chưa bị coi là nói giá; không chặn Lá Chắn). Cả 5 trọng tâm đạt: trang Kết nối chỉ khuyên Biên tập viên; bộ lọc meta bắt đủ dạng Lá Chắn nêu, không bắt oan «TP.HCM», «Q.GV», câu thường; `recheck_draft` chỉ đọc, chỉ nháp client vừa tạo; câu `_RECHECK_FAILED` đúng sự thật; gỡ đúng 2 dấu `xfail`. Gộp thử `main` `06a1b0e` không xung đột: 64 file 8.645 qua, 1 `xfail` cũ, 0 hỏng. Test mới: 61 ca (53 qua, 8 `xfail`). Thử đột biến: 20, test Thợ Máy bắt 19, test Soi Lỗi bắt thêm 1, 0 sống |

## Tóm tắt (cho chủ dự án)

- **Trang Kết nối WordPress** giờ chỉ khuyên dùng một tài khoản riêng ở vai **Biên tập viên**. Không còn chỗ nào trong phần mềm khuyên dùng Quản trị viên.
- **Ghi SEO lên bài nháp:** phần hỏi lại website sau khi ghi chỉ đọc, chỉ làm với bài nháp phần mềm vừa tạo. Khi hỏi lại không được, câu báo nay nói đúng: SEO đã ghi, chỉ chưa biết bài còn là nháp không.
- **Lọc gợi ý tiêu đề, mô tả của AI** bắt thêm các dạng tên miền lạ và các cách nói giá («5 trăm», «triệu rưỡi», «VNĐ»…). Viết tắt địa danh như «TP.HCM», «Q.Gò Vấp», «P.12» và các câu thường không bị bắt nhầm.
- **Hai lỗi nhỏ mới (Thấp):**
  - tên miền viết lẫn một chữ cái tiếng Nga trông y hệt «.com» vẫn lọt qua bộ lọc;
  - «đôla» viết liền chưa bị coi là nói giá.
  - Cả hai chỉ làm một gợi ý AI xấu lọt tới bước người dùng duyệt; không chặn việc kiểm bảo mật.

## Việc 1 · SL-T106-1: trang Kết nối chỉ khuyên Biên tập viên — **đạt**

- Câu mới (`app/views/wordpress.py:131-136`): «Tài khoản thiếu quyền viết bài hoặc tải ảnh. Phần mềm cần một tài khoản riêng ở vai trò **Biên tập viên (Editor)**: nhờ người quản trị website kiểm tra vai trò của tài khoản này.» Không còn «hoặc Quản trị viên».
- Soát cả trang: hai chỗ khác có chữ «Quản trị viên» đều là lời can («Đừng nâng tài khoản lên Quản trị viên…», «Không cần, và không nên, nâng lên Quản trị viên»). Grep `app/`, `seo_app/`, `config/`, `README.md`: không chỗ nào khuyên vai Quản trị viên; README chỉ nhắc `administrator` là dùng nhầm tài khoản.
- Câu không chép tên đăng nhập, mật khẩu (test Thợ Máy `assert_no_account_details`).

## Việc 2 · Bộ lọc gợi ý meta (LC-T036-2, SL-T036-11) — **đạt, kèm SL-T132-1, SL-T132-2**

- Bộ lọc chỉ dùng cho **gợi ý AI** (bỏ gợi ý), cụm từ neo liên kết nội bộ (`links.py:433`) và câu nhắc ở ghi chú kế hoạch (`write.py:775`). Chữ người dùng tự gõ ở bước SEO không bị chặn vì hai hàm này.
- **Không bắt oan câu thường** (14 câu, `test_cau_thuong_khong_bi_coi_la_link`): «TP.HCM», «Q.Gò Vấp», «Q.7, TP. HCM», «P.12, Q.Tân Bình, TP.Thủ Đức», «Tp.HCM, Tp.Hà Nội, tp.hcm», «12 tháng.Liên hệ», «Xingfa.Hệ 55», «Austdoor.Bảo hành», «v.v.», «INOX.SUS304», «1.2mm», «Inox 304.Sơn», câu HOA có dấu («NHÀ.UY TÍN», «ĐÀI LOAN.GIÁ TỐT»). Cùng 12 ca của Thợ Máy («TP.HN», «Q.GV», «TP.BMT», «TX.TDM»…). Hai câu HOA không dấu bị bắt oan, xem GN-3.
- **Dạng Lá Chắn nêu và các biến thể đều bị bắt** (test Thợ Máy và đối chứng của tôi): «evil。com» (cả «｡», «︒»), «evil[.]com», «evil(dot)com», «evil.xn--p1ai», «EVIL.SHOP», «evil.рф», «evil․com», «evil﹒com», «evil．shop».
- **SL-T132-1 (Thấp):** đuôi tên miền **trộn** chữ Latin với chữ Kirin hay Hy Lạp lọt: «evil.cоm» (chữ «о» Kirin) hiện y hệt «evil.com», nhưng gợi ý AI mang nó vẫn được nhận. Mục Lỗi mới.
- **Dò giá:** «5 trăm», «chỉ 5 trăm», «giá 2 trăm 5», «triệu rưỡi», «VNĐ», «USD», «đô la», «50 đô-la» đều bị bắt. Đơn vị đo, thời gian, danh từ đếm trong danh sách không bị bắt: «5 trăm mẫu cửa», «5 trăm khách hàng», «đội 5 trăm thợ», «cách 3 trăm mét», «4 trăm m²», «hai tiếng rưỡi», «ba năm rưỡi», «đô thị», «USDA».
- **SL-T132-2 (Thấp):** «đôla» viết liền, «đô-la» đứng riêng chưa bị coi là nói giá («chỉ 20 đôla mỗi lần sửa» lọt). Mục Lỗi mới.
- Danh từ đếm ngoài danh sách bị coi là giá («hơn 5 trăm gia đình»…): xem GN-2.
- Thời gian dò chuỗi 1.000 ký tự dựng xấu nhất (`-a`×500, `1`×1000…): `has_link` ≤ 20 ms, `mentions_price` ≤ 50 ms. Không treo.

## Việc 3 · `WordPressClient.recheck_draft` — **đạt**

- Đọc code: `recheck_draft` kiểm chủ (`type(post_id) is int` và thuộc `_created_post_ids`), rồi gọi `_own_draft(post_id, failed=_RECHECK_FAILED)`. `_own_draft` chỉ có **một** lệnh `self._request("GET", "/wp/v2/posts/{id}", context=edit, _fields=id,status,meta,modified_gmt)`. Không đường gọi mới, không lệnh ghi. Test cây cú pháp mới khóa điều này.
- Ca mới (ngoài 13 ca của Thợ Máy):
  - nháp của **client khác** (lần bấm khác): từ chối, 0 lệnh;
  - client có nháp mã 1 thật mà gọi với `True`, `1.0`, `IntEnum` bằng 1, `"1"`: từ chối, 0 lệnh;
  - sau khi `release_draft` đã đăng bài: từ chối, 0 lệnh;
  - website trả gì khác «bài 42 đang là nháp» (danh sách, `{}`, bài 43, mã `"42"`, mã `true`, `future`, `pending`, `private`, `trash`, `Draft`): câu `_SEO_NOT_DRAFT`, client thôi coi bài là của app. Sau đó ghi SEO, đặt ảnh đại diện, hẹn giờ/đăng, hỏi lại đều bị từ chối, 0 lệnh;
  - không hỏi được (302 kèm `Location` lạ, 401, 403, 404, 500, hết giờ): câu `_RECHECK_FAILED` kèm mã, không chép lời máy chủ hay địa chỉ chuyển hướng, `__cause__` rỗng; không đi theo chuyển hướng; client **vẫn giữ** bài là nháp của app (chưa biết gì).
- `app/` không còn chỗ nào đọc `client._…` (test Thợ Máy).

## Việc 4 · Câu `_RECHECK_FAILED` — **đạt**

- Trên trang Soạn bài (test Thợ Máy, chạy lại qua): «Đã ghi SEO vào hộp SiteSEO của bài nháp. Kiểm lại ngay sau khi ghi SEO: Không hỏi lại được bài trên WordPress (mã 500) nên chưa biết bài còn là nháp không. Mở bài trong trang quản trị WordPress, xem trạng thái bài và hộp SiteSEO.» Không còn «trước khi ghi SEO… Chưa ghi gì».
- Câu chỉ có một chỗ `{code}`; không có mã bài, địa chỉ website, lời máy chủ.
- Hỏi lại hỏng thì `seo_ok = False`: «Đăng ngay» (T-112) coi SEO là chưa lên, hướng an toàn.
- Câu khi hỏi lại thấy bài **đã đăng** vẫn hơi tự mâu thuẫn: GN-1.

## Việc 5 · Gỡ `xfail` (R5) — **đạt**

- `tests/test_soi_loi_t106.py`: chỉ xóa 4 dòng dấu `xfail` SL-T106-1. `tests/test_soi_loi_t036.py`: chỉ xóa 1 dòng dấu `xfail` SL-T036-11. Không đổi thân, tham số, docstring.
- Dấu `xfail` SL-T036-10 («đô vật») còn nguyên, vẫn `xfailed`.
- Phiếu cho gỡ SL-T106-1; SL-T036-11 thuộc mục tùy chọn phiếu cho làm.

## Việc 6 · Không lùi, gộp thử — **đạt**

- Mọi nơi gọi hàm dùng chung (`has_link`, `mentions_price`, `accept_ai_*`, client WordPress, trang Kết nối, bước SEO, Xuất bản) và test quét mã nguồn `client.py`, `app/`: 64 file.
- Gộp thử với `main` `06a1b0e` (worktree tạm, không đẩy): `git merge-tree` không xung đột. `main` có T-124 sửa `client.py` (hàm chuẩn hóa `WORDPRESS_URL` gần `is_site_link`), không chạm `recheck_draft`, `_own_draft`.
- Kết quả trên bản gộp (64 file, 08:16 → 09:01): **8.645 qua, 1 `xfail`** (SL-T036-10 «đô vật», có từ trước), 0 hỏng, 0 `XPASS`. Đã kiểm `seo_app` nạp từ bản gộp. Thêm `test_soi_loi_t132.py` trên bản gộp: 53 qua, 8 `xfail`.
  - Worktree tạm đã gỡ.

## Thử đột biến (`sl132_mutate.py`)

- 20 đột biến trên 4 file sửa (`meta.py`, `client.py`, `wordpress.py`, `write.py`), một bản sao `git archive` của `1c8bba7`, trả file gốc giữa các đột biến, `PYTHONDONTWRITEBYTECODE=1`.
- Mỗi đột biến chạy 4 file trước (`-x`): `test_t132_don_chu`, `test_t132_trang_ket_noi`, `test_soi_loi_t036`, `test_soi_loi_t106`. Sống thì chạy `test_soi_loi_t132`.
- Đối chứng không đổi: 341 qua + 1 `xfail` (Thợ Máy và R5), 53 qua + 8 `xfail` (Soi Lỗi). `seo_app` nạp từ bản sao.

| Kết quả | Số | Đột biến |
|---|---|---|
| Test Thợ Máy bắt | 19 | K01 trang khuyên lại «hoặc Quản trị viên»; K02 `recheck_draft` bỏ kiểm chủ; K04 dùng câu `_SEO_CHECK_FAILED`; K05 không hỏi gì; K21 nuốt lỗi; K06 trang gọi lại `client._own_draft`; K07 bỏ chú thích FAQ; K08 bỏ dấu chấm kiểu né; K09 bỏ `xn--`; K10 bỏ dạng HOA; K11 dạng HOA nhận nhãn 2 ký tự (bắt oan «TP.HCM»); K12 bỏ đuôi chữ ngoại; K13 bỏ đổi «。»; K14 bỏ «chữ số + trăm»; K15 bỏ danh sách loại trừ; K19 bỏ «khách» khỏi danh sách; K16 bỏ «… rưỡi»; K17 bỏ tên tiền đứng riêng; K18 tên tiền bỏ ranh giới chữ (bắt oan «vndirect») |
| Chỉ test Soi Lỗi bắt | 1 | K03 `recheck_draft` kiểm `isinstance(post_id, int)` thay `type(...) is int`: client có nháp mã 1 thì `recheck_draft(True)` lọt bước kiểm chủ (`True == 1`). Test Thợ Máy chỉ thử `True` khi client chưa có nháp mã 1 |
| Sống cả hai | 0 | |

## Lỗi mới

| Mã | Mức | Mô tả | Test |
|---|---|---|---|
| **SL-T132-1** | Thấp | `_foreign_tld` chỉ bắt đuôi tên miền **không có chữ Latin nào**. Đuôi trộn chữ Latin với chữ Kirin hay Hy Lạp lọt cả `_LINK` (cần đúng «com», «vn»…), `_BARE_DOMAIN` (cần `[a-z]`), `_foreign_tld`: «evil.cоm» («о» Kirin), «evil.соm», «evil.cοm» («ο» Hy Lạp), «evil.shоp», «EVIL.SHОP». `has_odd_chars` không coi chữ Kirin là lạ, nên gợi ý AI «Cửa sắt bị xệ: xem evil.cоm để biết cách sửa» **được nhận**, trong khi bản «evil.com» bị bỏ. Trên trang kết quả Google, chữ này hiện y hệt «evil.com». Cần AI bị dụ (lời trong bài tham khảo) và người dùng chọn gợi ý đó | `tests/test_soi_loi_t132.py::test_sl_t132_1_duoi_ten_mien_tron_chu_bi_bat` (5 ca, `xfail(strict=True)`; `--runxfail`: hỏng đúng ở `has_link`). Đối chứng chữ thật: `test_doi_chung_ten_mien_that_bi_bat` (qua) |
| **SL-T132-2** | Thấp (một phần có từ trước) | Luật mới «tên tiền đứng riêng» chỉ nhận «đô la» viết rời. «đôla» viết liền và «đô-la» đứng riêng chưa bị coi là nói giá: «chỉ 20 đôla mỗi lần sửa», «giá tính bằng đôla», «tính bằng đô-la». Gợi ý mô tả AI mang chúng được nhận. «20 đôla» chưa bao giờ bị bắt (đơn vị `đô(?:\s+la)?` của `_MONEY_UNIT` có từ trước) | `tests/test_soi_loi_t132.py::test_sl_t132_2_dola_viet_lien_bi_bat` (3 ca, `xfail(strict=True)`; `--runxfail`: hỏng đúng ở `mentions_price`). Đối chứng «đô la»: `test_doi_chung_do_la_bi_bat` (qua) |

Gợi ý sửa:

- SL-T132-1: trong `_foreign_tld`, coi là tên miền lạ khi đuôi có **bất kỳ** chữ nào không phải Latin, không chỉ khi không có chữ Latin nào. Chữ Việt có dấu đều là chữ Latin, nên «xong.tiếp», «Cửa.Sắt» vẫn không bị bắt.
- SL-T132-2: thêm `đô\s*-?\s*la` (cả viết liền) vào luật tên tiền đứng riêng và vào `_MONEY_UNIT`.
- Không chặn Lá Chắn: cả hai chỉ làm một gợi ý AI xấu lọt tới tay người dùng duyệt.

## Ghi nhận

- **GN-1 · Câu khi hỏi lại thấy bài đã đăng.**
  - Trên trang Soạn bài (thử bằng AppTest, lần đọc thứ hai trả `publish`): «Đã ghi SEO vào hộp SiteSEO của bài nháp. Kiểm lại ngay sau khi ghi SEO: Bài này không còn là bản nháp trên website (có thể đã được đăng hoặc bị xóa). Phần mềm không sửa bài đã đăng (không ghi SEO, không đổi ảnh đại diện); nếu cần, sửa tay trong trang quản trị WordPress.»
  - «Đã ghi SEO» rồi «không ghi SEO» vẫn hơi tự mâu thuẫn, cùng loại với câu T-132 vừa sửa. Thợ Máy đã cân nhắc và giữ (mục Rủi ro 5).
  - Gợi ý khi có phiếu chữ sau: câu riêng cho lần hỏi lại, ví dụ «SEO đã ghi, nhưng ngay sau đó bài không còn là nháp (có thể vừa được đăng hay bị xóa). Mở bài trong trang quản trị, xem hộp SiteSEO.» Tình huống rất hiếm (bài bị đăng trong vài giây giữa lệnh ghi và lệnh hỏi lại).
- **GN-2 · «Chữ số + trăm» với danh từ đếm ngoài danh sách bị coi là giá:** «hơn 5 trăm gia đình», «5 trăm đánh giá», «3 trăm công ty», «2 trăm ngôi nhà», «4 trăm doanh nghiệp», «5 trăm hồ sơ», «5 trăm loại cửa»; tương tự «một nghìn rưỡi khách», «thủ đô La Paz».
  - Ảnh hưởng nhỏ: chỉ bỏ gợi ý AI (lời dặn AI vốn không cho số trong mô tả) và hiện câu nhắc ở ghi chú kế hoạch. Thợ Máy đã ghi là lệch an toàn.
  - Báo cáo Thợ Máy lấy «5 trăm thợ» làm ví dụ danh từ ngoài danh sách, nhưng «thợ» **có** trong danh sách (không bị bắt). Ví dụ đúng là «5 trăm gia đình».
- **GN-3 · Dò link còn vài dạng biên.**
  - Bị bắt oan (lệch an toàn, cùng loại «KCN.VSIP» Thợ Máy đã ghi): câu HOA không dấu thiếu dấu cách «… TPHCM.UY TÍN 24/7», «THS.KTS Nguyễn Văn A».
  - Còn lọt: Thợ Máy đã ghi «Evil.Shop», «AB.SHOP», «evil [.] com»; thêm «evil.SHOP» (nhãn thường, đuôi hoa) và «evil{.}com». Không cái nào là link bấm được.
- **GN-4 · Cách nói giá ngoài phạm vi SL-T036-11** (có từ trước): tiếng lóng «1 củ», «5 lít», «3 xị»; số viết bằng chữ «năm trăm thôi» (Thợ Máy đã ghi).
- **GN-5 · Trang Kết nối, tài khoản đã là Biên tập viên nhưng website không cho biết quyền** (có từ trước): vẫn hiện «Tài khoản thiếu quyền viết bài hoặc tải ảnh… cần một tài khoản riêng ở vai trò Biên tập viên», dù dòng trên ghi «vai trò: editor». Câu mới có thêm «nhờ người quản trị website kiểm tra vai trò», nên vẫn dùng được. Phiếu chữ sau có thể tách câu «website chưa cho biết quyền».

## Tệp và cách chạy lại

- Test: `tests/test_soi_loi_t132.py`, 12 hàm, 61 ca: 53 qua, 8 `xfail(strict=True)` (SL-T132-1 ×5, SL-T132-2 ×3). Tham số đều có `ids` ngắn.
  - Chạy: `uv run pytest tests/test_soi_loi_t132.py -rxX`.
  - Kiểm các ca `xfail`: thêm `--runxfail -k sl_t132`.
- Script (thư mục ghi chú chung, `T-132-soi-loi-scripts/`):
  - `sl132_probe.py`: thăm dò dò link, dò giá, thời gian chuỗi xấu nhất;
  - `sl132_mutate.py`: thử đột biến (một bản sao `git archive`, trả file gốc giữa các đột biến).
- detect-secrets (`PYTHONUTF8=1`, có file mồi trong thư mục tạm): file test và báo cáo **0** phát hiện; file mồi 2 phát hiện.

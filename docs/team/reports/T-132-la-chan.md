# Biên bản bảo mật T-132 · Dọn chữ Giai đoạn 4 · rút gọn

> **Model:** Claude Opus 5.5 (chủ dự án quyết 04/11: hết hạn mức Fable thì Lá Chắn chạy Opus).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-132](../tickets/T-132-don-chu-giai-doan-4.md) («phiếu B» của biên bản [T-129](T-129-la-chan.md)) · mức **rút gọn** |
| Phạm vi | <ul><li>**Nhánh:** `team/T-132` tại `4a3bc10`, diff `f6a6e64..4a3bc10`, 11 file.</li><li>**Mã đổi:** `app/views/wordpress.py`, `app/views/write.py` (6 dòng mỗi file), `seo_app/onpage/meta.py`, `seo_app/wordpress/client.py`.</li><li>**Các lượt:** Thợ Máy lượt 1 `1c8bba7`; Soi Lỗi `ce6c4fd` (SL-T132-1, -2); Thợ Máy lượt 2 `4a3bc10`.</li><li>Không gọi website thật, không sửa mã.</li></ul> |
| Ngày | 2026-11-07 09:40 (dừng vì hết hạn mức); 2026-11-09 07:34–07:50; 2026-11-10 (chạy lại test, điền số); giờ máy +07 |
| **Kết luận** | **ĐẠT.** <ul><li>0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp mới.</li><li>4 trọng tâm Chỉ Huy giao đều đạt.</li><li>**Điều kiện 1 của Lá Chắn T-129 (SL-T106-1) đã đóng.** Phần đóng Giai đoạn 4 còn điều kiện 2 (T-131, dọn kho dữ liệu phụ) và điều kiện 3 (tài liệu).</li><li>Gộp `main` được ngay.</li></ul> |

## Tóm tắt (cho chủ dự án)

- **Đã sửa câu khuyên sai trên trang «Kết nối WordPress».** Khi tài khoản thiếu quyền, trang nay chỉ khuyên dùng tài khoản riêng vai Biên tập viên, đúng việc anh đã chọn; không còn khuyên «Quản trị viên».
- **Bộ lọc gợi ý tiêu đề, mô tả SEO của AI chặt hơn.**
  - Nay bắt thêm tên miền viết kiểu né («evil[.]com», chữ Nga, chữ Trung) và các cách nói giá như «5 trăm», «triệu rưỡi», «đôla».
  - Tôi thử trên 2.450 câu tiếng Việt thật của dự án: không bỏ sót chỗ nào bản cũ bắt được, không bắt oan câu nào. Các chữ dễ nhầm như «TP.HCM», «5 trăm công trình», «Đô Lương» vẫn qua.
- **Bước kiểm «bài còn là nháp» sau khi ghi SEO** dùng một hàm chính thức của phần mềm. Hàm này chỉ đọc, chỉ hỏi bài nháp phần mềm vừa tạo, không mở thêm đường ghi nào lên website.
- **Không có lỗi mới. Không có gì anh phải quyết.**

## Lỗi phát hiện

Không phát hiện lỗi.

## Bốn trọng tâm Chỉ Huy giao

| # | Trọng tâm | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | `WordPressClient.recheck_draft`: chỉ đọc, chỉ nháp client vừa tạo, không mở đường ghi mới | **Đạt** | <ul><li>`client.py:1343-1355`: mã bài phải là `int` thật (loại `bool`) và có trong `_created_post_ids`, không thì câu `_RECHECK_NOT_OWN`, 0 lệnh ra mạng. Sau đó gọi `_own_draft`.</li><li>`_own_draft` chỉ gửi đúng một `GET /wp/v2/posts/{id}` (`context=edit`, `_fields` cố định) qua `_request`, tức qua danh sách đường gọi đã duyệt.</li><li>Tác dụng phụ chỉ ở trong máy: bài không còn là nháp thì bỏ khỏi danh sách «nháp của app»; bài bị sửa ngoài app thì đánh dấu «không biết», nên `release_draft` không chuyển bài.</li><li>Câu `_RECHECK_FAILED` cố định, chỉ chèn mã HTTP.</li><li>`write.py` (`write_seo`) gọi hàm này thay chỗ gọi hàm riêng; lỗi thì `written = False`, nên «Đăng ngay» vẫn khóa.</li><li>Test `test_t132_don_chu.py` ghim đủ: mã chưa tạo hay sai kiểu (`True`, `"42"`, `42.0`, `None`) bị từ chối với 0 lệnh; nháp của app thì đúng một `GET`; bài đã đăng thì báo và thôi coi là của app; bài bị sửa ngoài thì đánh dấu; không hỏi được thì câu riêng.</li></ul> |
| 2 | Bộ dò link, giá trong `meta.py` không nới lọc, không bắt oan câu thường | **Đạt** | <ul><li>**Đọc mã:** chỉ **thêm** nhánh:<ul><li>`_LINK`: dấu chấm kiểu né, `xn--`;</li><li>`_BARE_DOMAIN`: tên miền toàn chữ HOA, nhãn từ 3 ký tự để «TP.HCM», «Q.GV» không bị bắt;</li><li>`_foreign_domain`: chữ Kirin, Hy Lạp, Hán ở tên miền;</li><li>dấu chấm Hán «。» đổi thành «.» trước khi dò;</li><li>`_PRICE`: «5 trăm» trống, «… rưỡi», tên tiền đứng riêng.</li></ul>`đô(?:\s+la)?` đổi thành `đô(?:\s*-?\s*la)?`, bắt rộng hơn bản cũ.</li><li>**Thử:** so bản mới với bản `f6a6e64` trên 2.450 câu tiếng Việt thật (hồ sơ doanh nghiệp, `config/content.toml`, 11 file `docs/plan/`):<ul><li>bản cũ bắt mà bản mới bỏ: link 0, giá 0;</li><li>bản mới bắt thêm: link 0, giá 0.</li></ul></li><li>9 câu dễ nhầm đều không bị bắt: «TP.HCM», «Q.GV, TP.HN, TP.BMT», «Hơn 5 trăm công trình», «Cách 3 trăm mét», «Đô thị, đô vật, Đô Lương», «Inox 304.Sơn 60μm.Bền màu», «xong.tiếp theo», «1.2mm», «ISO.9001».</li><li>Bắt oan, nếu có, chỉ là bỏ một gợi ý AI (lệch về phía an toàn), người dùng vẫn tự gõ được.</li></ul> |
| 3 | SL-T106-1 đúng ý điều kiện 1 của T-129 | **Đạt** | <ul><li>`wordpress.py:131-136` nay chỉ khuyên tài khoản riêng vai **Biên tập viên (Editor)** và nhờ người quản trị kiểm vai trò, không còn «Quản trị viên (Administrator)».</li><li>Câu khớp câu dòng 78 («không nên nâng lên Quản trị viên») và README mục 6.</li><li>Ca `test_sl_t106_1_trang_khong_khuyen_nang_len_quan_tri` (2 tham số) nay qua.</li></ul> |
| 4 | R5: gỡ `xfail` đúng cách | **Đạt** | <ul><li>Lượt 1 chỉ xóa 2 khối dấu: SL-T036-11 (1 dòng), SL-T106-1 (4 dòng).</li><li>Lượt 2 chỉ xóa 2 khối dấu trong `test_soi_loi_t132.py`: SL-T132-1, -2 (9 dòng).</li><li>Không câu kiểm, tham số hay `ids=` nào đổi (`git diff … -- tests/`, chỉ các dòng `-` của dấu).</li><li>Ca «đô vật» (SL-T036-10, lệch an toàn) vẫn giữ.</li></ul> |

**Chú thích FAQ** (mục tùy chọn, góp ý của T-129): dưới ô «Dùng schema Hỏi đáp (FAQ) này cho bài» nay có câu cố định «Ô này chỉ ghi nhớ lựa chọn trong nháp: app chưa gửi schema lên website.» (`write.py`, `MSG_FAQ_NOT_SENT`), khớp README mục 10. Phần mềm vẫn không gửi schema.

## Danh sách kiểm tra

| Mã | Kết quả | Ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets: 0 bí mật thật (mục «Báo nhầm»), mồi bị bắt |
| S2 | Đạt | Câu mới (`_RECHECK_NOT_OWN`, `_RECHECK_FAILED`, `MSG_FAQ_NOT_SENT`, câu cảnh báo vai trò) đều cố định; chỉ chèn mã HTTP |
| S3 | Không áp dụng | Không biến cấu hình mới |
| W1 | Đạt | `recheck_draft` chỉ đọc; không đổi `status` |
| W2 | Đạt | Chỉ hỏi bài nháp client vừa tạo |
| W3 | Không áp dụng | Không gửi HTML mới |
| W4 | Đạt | Đi qua `_request` (https, timeout, danh sách đường gọi, không đi theo chuyển hướng) |
| A1 | Không áp dụng | Không đổi lời dặn AI |
| A2 | Đạt | Bộ kiểm kết quả AI (meta) chặt hơn, không nới |
| A3 | Không áp dụng | |
| U1 | Đạt | Không `unsafe_allow_html` mới; chữ mới là chữ hằng |
| U2 | Đạt | Trang Kết nối không khuyên nâng quyền (đóng SL-T106-1) |
| U3 | Không áp dụng | |
| F1 | Không áp dụng | Không đọc ghi file |
| F2 | Không áp dụng | |
| F3 | Đạt | Không `eval`, `pickle`; regex mới không lồng lượng từ kiểu dễ nổ (chạy 2.450 câu tức thì) |
| D1 | Đạt | Không thư viện mới |
| D2 | Không áp dụng | |
| D3 | Đạt | Móc kiểm: 0 kết nối ra ngoài máy |

## Kết quả công cụ quét, test

| Công cụ | Kết quả | Ghi chú |
|---|---|---|
| pytest | 20 file liên quan (T-132, bộ dò meta, ghi SEO, hỏi lại nháp, `modified_gmt`, bước SEO, trang Kết nối): **2.168 qua**, 1 `xfail` đã biết (SL-T036-10 «đô vật», lệch an toàn), **0 hỏng**; 9 phút 41 giây (chạy lại 10/11 vì lần 07/11 dừng giữa chừng) | <ul><li>Chỉ test liên quan, theo tin giao.</li><li>Móc kiểm `sys.addaudithook`: 0 kết nối ra ngoài máy (mọi `connect` tới `127.0.0.1` hay `::1`, cặp socket nội bộ của asyncio); 0 lần mở `.env` ngoài thư mục tạm của pytest.</li></ul> |
| ruff | `ruff check` 9 file đổi: sạch. `ruff format --check`: `meta.py` sạch; `client.py`, `wordpress.py` lệch định dạng **từ trước T-132** (đã so bản `f6a6e64`) | Dự án chỉ bắt buộc `ruff check` |
| detect-secrets (`PYTHONUTF8=1`) | 11 file đổi: 0 bí mật thật; 2 báo nhầm; mồi bị bắt | Chạy trên bản chép, đường dẫn tương đối, `--all-files` |
| Thử riêng | `probe_meta.py`: bộ dò mới so bản cũ trên 2.450 câu, cùng 9 câu dễ nhầm | Thư mục nháp của phiên |

## Báo nhầm đã loại

**detect-secrets «Basic Auth Credentials»** ở `app/views/write.py` và `seo_app/wordpress/client.py`:
- là chữ mẫu «tên:mật-khẩu@» trong chú thích;
- có từ trước T-132, phiếu không đổi các dòng đó;
- đã ghi ở biên bản T-129, mục 7.

## Điều kiện

Không có. Gộp `main` được ngay.

Giai đoạn 4 (theo T-129) còn hai điều kiện:
- **Điều kiện 2:** phiếu T-131, dọn kho dữ liệu phụ (LC-T129-1, SL-T117-1).
- **Điều kiện 3:** cập nhật Lộ trình, `TIEN-DO.md`.

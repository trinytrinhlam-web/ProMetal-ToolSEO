# Báo cáo T-115 · Client WordPress: so `modified_gmt` ngay trước lệnh chuyển (LC-T094-23)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | T-115 `T-115-client-so-modified-gmt.md` (Chỉ Huy B giao 31/10 09:55; nhánh này không chứa phiếu) |
| Nhánh | `team/T-115` (từ `d6df633` = `main` cục bộ có T-102, T-110 lượt 1, T-099 lượt 2) |
| Ngày nộp | 2026-10-31 12:34 (+07:00, theo lệnh `date`) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

- Khi bấm **Hẹn giờ** hay **Đăng ngay**, phần mềm kiểm thêm một điều ngay trước lệnh chuyển: bài nháp trên website có bị ai sửa sau lần phần mềm ghi cuối không. Người sửa có thể là chính anh/chị trong trang quản trị, một plugin, hay người khác.
- Có bị sửa, hoặc phần mềm không biết chắc, thì **không hẹn giờ, không đăng**. Bài vẫn là nháp, và phần mềm báo một câu cố định: mở trang quản trị WordPress xem lại bài rồi hẹn giờ hay đăng ở đó.
- Nhờ vậy bài không bao giờ bị đăng lên với nội dung khác bản anh/chị đã xem và xác nhận trong phần mềm.
- **Cần kiểm khi thử thật** (mục cuối): ghi SEO qua SiteSEO (Abilities) có làm đổi «giờ sửa cuối» của bài không. Nếu có thì nút Hẹn giờ/Đăng ngay sẽ luôn từ chối khi bật ghi SEO, theo hướng an toàn; khi đó phải thêm một bước đọc lại.

## Kế hoạch đã làm

1. Client nhớ `modified_gmt` website trả sau mỗi lệnh ghi của **chính nó** vào bài nháp: tạo nháp, ảnh đại diện, ghi meta SEO dự phòng.
2. Lệnh `GET` kiểm nháp ngay trước lệnh chuyển xin thêm `modified_gmt` và so với giá trị đã nhớ.
3. Mọi trường hợp không chắc (thiếu, sai dạng, lệnh ghi lỗi giữa chừng, bị sửa giữa hai lệnh ghi của app) đều coi là «không biết», và «không biết» thì không chuyển.
4. Chỉ sửa `seo_app/wordpress/client.py` (phần nhớ, so `modified_gmt` và 3 chuỗi `_fields`). **Không** đụng `_attach_media`, `_is_media_attach`, `upload_media`, các câu `_DRAFT_*` (T-110 lượt 3 đang sửa ở nhánh khác).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/wordpress/client.py` | `_POST_FIELDS`, `_POST_META_FIELDS`, `_RELEASE_CHECK_FIELDS` thêm `modified_gmt` (không trường nào WordPress dựng bằng `the_content`; `_asks_rendered_fields` vẫn sai). `self._modified: dict[int, str \| None]` riêng từng client: mỗi lần bấm một client mới, hai tab không dùng chung. Ba hàm phụ `_remember_modified`, `_taint_modified`, `_same_modified`. Câu `_RELEASE_CHANGED` cố định. `_release_check` trả thêm `modified_gmt` |
| `tests/test_t115_modified_gmt.py` (mới) | 23 ca |
| 11 file test cũ | Đổi theo R5, Chỉ Huy duyệt 31/10 10:55 (bảng dưới); gỡ dấu `xfail` LC-T102-1 (duyệt 13:20) |

### Cách nhớ và so (yêu cầu 1–3)

| Lúc | Việc |
|---|---|
| `create_draft` (bài site xác nhận `draft`) | Nhớ `modified_gmt` câu trả lời mang; thiếu, sai dạng thì «không biết» |
| `_own_draft` (đọc bài ngay trước lệnh ghi ảnh đại diện, SEO) | So `modified_gmt` với giá trị nhớ. Khác hay thiếu: đánh dấu «không biết». Lệnh ghi vẫn được làm (bài còn là nháp của app), nhưng giờ nó trả về **không** xóa được dấu vết bài bị sửa ngoài app |
| `set_featured_image` | Ghi xong: nhớ giờ mới. Lệnh ghi lỗi (5xx, mất mạng…): «không biết» |
| `_seo_via_meta` (ghi meta dự phòng) | Ghi xong: nhớ giờ mới. Lỗi giữa chừng: «không biết». 400/401/403 (site không cho ghi): giữ nguyên |
| `_seo_via_abilities` | Câu trả lời của ability **không có** `modified_gmt`: giữ giá trị nhớ (xem mục «Cần kiểm khi thử thật») |
| `_attach_media` (T-110: gắn ảnh vào bài) | Không đổi. Lệnh này sửa **ảnh** (`post_parent`), không sửa bài, nên không đổi `modified_gmt` của bài |
| `release_draft` | Sau khi kiểm còn nháp: `modified_gmt` của lệnh kiểm phải đúng dạng và bằng giá trị nhớ, không phải «không biết». Sai thì `ReleaseError(_RELEASE_CHANGED)`: không `unsure`, không gửi lệnh chuyển, **không trả mã bài** (cũng như «không còn là nháp»: bài cần người xem lại) |

Câu báo `_RELEASE_CHANGED`: «Bài nháp trên website đã bị sửa sau lần phần mềm ghi cuối (trong trang quản trị, plugin hay người khác), hoặc phần mềm không biết chắc bài có bị sửa không. Chưa hẹn giờ, chưa đăng: bài vẫn là nháp. Mở trang quản trị WordPress xem lại bài rồi hẹn giờ hay đăng ở đó.» App (T-102) đã có sẵn đường hiện `ReleaseError` «bài vẫn là nháp», nên không sửa `app/**`.

### Test cũ đổi (Chỉ Huy duyệt 31/10 10:55, R5)

**Kiểu (1): chỉ thêm `,modified_gmt` vào chuỗi `_fields` mong đợi.**

| File:dòng | Cũ → mới |
|---|---|
| `test_shortcode_t061.py:273` (`POST_FIELDS`) | `id,status,title,link,featured_media` → `…,modified_gmt` |
| `test_shortcode_t061.py:508`, `:529` | `id,status,meta` → `id,status,meta,modified_gmt` |
| `test_soi_loi_t061.py:315` | `?_fields=id%2Cstatus%2Ctitle%2Clink%2Cfeatured_media` → `…%2Cmodified_gmt` |
| `test_soi_loi_t061.py:323` | `?context=edit&_fields=id%2Cstatus%2Cmeta` → `…%2Cmodified_gmt` |
| `test_soi_loi_t061.py:285` (`SAFE_FIELDS`) | thêm `"modified_gmt"` vào danh sách tên trường được phép xin. Cùng kiểu, dạng danh sách thay cho chuỗi: `modified_gmt` là giờ, không phải trường WordPress dựng bằng `the_content`. **Chỉ Huy xác nhận 14:20** |
| `test_soi_loi_t054.py:621` | `id,status,meta` → `…,modified_gmt` |
| `test_soi_loi_t054.py:628` | `id,status,title,link,featured_media` → `…,modified_gmt` |
| `test_wordpress_seo_meta_t042.py:202` | `id,status,meta` → `…,modified_gmt` |
| `test_wordpress_release.py:148` | `id,status` → `id,status,modified_gmt` |
| `test_soi_loi_t099.py:186` | `id,status` → `id,status,modified_gmt` |

**Kiểu (2): chỉ thêm cùng một giá trị `modified_gmt` hợp lệ vào câu trả lời giả của website cho bài nháp.** Mỗi file một hằng `MODIFIED`; sửa ở hàm dựng site giả, ít chỗ nhất.

| File:dòng | Câu trả lời giả |
|---|---|
| `test_wordpress_release.py:59` | hằng `MODIFIED` |
| `test_wordpress_release.py:96` | `own_draft`: lệnh tạo nháp |
| `test_wordpress_release.py:124` | `site`: lệnh kiểm nháp mặc định. Khi test truyền `check=` riêng (ca cố ý thử «không còn là nháp», câu trả lời lạ) thì giữ nguyên |
| `test_wordpress_release.py:627` | lệnh tạo nháp riêng của ca «giờ máy chủ lấy từ chính lệnh kiểm» |
| `test_soi_loi_t099.py:54` | hằng `MODIFIED` |
| `test_soi_loi_t099.py:84`, `:92` | `_WpSite`: lệnh tạo nháp, lệnh kiểm bài |
| `test_soi_loi_t099.py:802` | `_hold_check`: lệnh kiểm nháp (mặc định) |
| `test_la_chan_t099.py:39` | hằng `MODIFIED` |
| `test_la_chan_t099.py:49`, `:67` | `_site`: lệnh tạo nháp; `DRAFT`: lệnh kiểm nháp |
| `test_la_chan_t099.py:116` | lệnh kiểm nháp thiếu header `Date` (giữ nguyên ý «thiếu `Date`») |
| `test_app_images.py:64` | hằng `MODIFIED` |
| `test_app_images.py:1003`, `:1006`, `:1027` | `Site` dùng chung của nhóm test app: lệnh kiểm bài, lệnh ghi vào bài, lệnh tạo nháp |
| `test_t102_publish.py:106`, `:114` | `live`: lệnh kiểm nháp, lệnh ghi vào bài |
| `test_soi_loi_t102.py:171` | lệnh kiểm nháp có header `Date` lệch (giữ nguyên ý «đồng hồ website lệch») |
| `test_la_chan_t102.py:50` | lệnh ghi vào bài (ảnh đại diện) |

**Ghi rõ:** ở nhóm test app và T-099, ngoài lệnh tạo nháp, kiểm nháp, tôi thêm `modified_gmt` cả vào câu trả lời giả của **lệnh ghi vào bài nháp** (ảnh đại diện, meta): `test_app_images.py:1006`, `test_t102_publish.py:114`, `test_la_chan_t102.py:50`. Website thật luôn trả trường này khi được xin trong `_fields`. Thiếu nó thì client coi là «không biết» (đúng yêu cầu 1) và không chuyển bài, nên các test Hẹn giờ/Đăng ngay có ảnh đại diện sẽ đỏ. Đây cũng chỉ là thêm trường vào câu trả lời giả, không đổi điều kiện, không nới kiểm, nhưng rộng hơn đúng chữ «tạo/kiểm nháp» trong lời duyệt nên tôi đã nêu ra: **Chỉ Huy xác nhận 14:20**.

Không ca cố ý thử «website trả lạ/thiếu» nào bị đổi ý: các ca truyền `check=` riêng, câu trả lời lệnh chuyển (`UNSURE_ANSWERS`…), lệnh lỗi, lệnh không còn nháp đều giữ nguyên và vẫn qua. Không đụng câu trả lời **tải ảnh** (T-110 lượt 3 đang thêm `"post": None` ở đó).

### LC-T102-1 nay bị chặn ở lớp client (Chỉ Huy duyệt gỡ dấu 31/10 13:20, R5)

- Đã gỡ dấu `xfail(strict=True)` của `test_la_chan_t102.py::test_lc_t102_1_dang_ngay_ma_anh_dai_dien_hong_thi_khong_dang`: chỉ xóa 4 dòng dấu, thân giữ nguyên. Bỏ luôn `import pytest` không còn dùng, để ruff sạch; nhánh T-112 (`f598cef`) cũng gỡ y hệt nên gộp không xung đột. 3 ca `xfail` SL-T102-1 giữ nguyên ở nhánh này.
- Lý do (giữ lại để tra):

#### Trước khi duyệt (ghi lại)

- `test_la_chan_t102.py::test_lc_t102_1_dang_ngay_ma_anh_dai_dien_hong_thi_khong_dang` là `xfail(strict=True)` của Lá Chắn: «LC-T102-1: Đăng ngay mà đặt ảnh đại diện hỏng lúc gửi vẫn gửi lệnh đăng công khai». Nay **XPASS** nên đỏ.
- Lý do: T-115 coi lệnh ghi ảnh đại diện lỗi (500) là «không biết giờ sửa cuối», nên `release_draft` từ chối, không gửi lệnh đăng. Tức T-115 chặn luôn lỗi LC-T102-1 ở lớp client; phía app (T-102) vẫn gọi `release_draft`, nhưng client không đăng.
- Hai ca đi kèm vẫn qua: ca tiền đề (lệnh ảnh có đi và hỏng, trang báo «chưa đặt được ảnh đại diện»), ca đối chứng (ảnh đặt được thì vẫn đăng).
- Đề nghị: theo R5, Lá Chắn hay anh gỡ dấu `xfail` (chỉ xóa dấu) và ghi LC-T102-1 đã đóng nhờ T-115; hoặc giữ dấu nếu muốn sửa thêm ở phía app (T-112).
- Ba ca `xfail` SL-T102-1 (Đăng ngay mà ghi SEO hỏng) vẫn `xfail` như cũ: các ca này thay `set_seo_meta` bằng hàm giả nên không đi qua client.

## Cần kiểm khi thử thật (yêu cầu 4)

Thử trên một bài nháp thử, công tắc Hẹn giờ/Đăng ngay còn tắt:

1. **Ghi SEO qua Abilities (SiteSEO 1.4.2) có làm đổi `modified_gmt` của bài không.** SiteSEO lưu SEO vào khóa meta (`update_post_meta`); WordPress lõi không đổi `post_modified` khi chỉ đổi meta, nên **dự kiến không đổi**. Cách kiểm: đọc `GET /wp/v2/posts/<mã>?context=edit&_fields=id,modified_gmt` trước và sau lệnh ghi SEO (cách nhau hơn 1 giây).
   - Không đổi: giữ như hiện nay.
   - Có đổi: câu trả lời ability không mang `modified_gmt`, nên client sẽ luôn từ chối chuyển khi bật ghi SEO. Đề xuất: sau lệnh ability, client đọc lại bằng `GET …&_fields=id,status,modified_gmt` rồi nhớ giờ đó. Khe giữa lệnh ghi SEO và lần đọc lại chỉ vài trăm mili giây; muốn bịt khe này thì so thêm `modified_gmt` của lần đọc với giờ trước khi ghi cộng tối đa vài giây.
2. **Ghi meta dự phòng, đặt ảnh đại diện** trả `modified_gmt` đúng giờ mới (dự kiến có: `wp_update_post` luôn đổi `post_modified`).
3. **Gắn ảnh vào bài (T-110)** không đổi `modified_gmt` của bài (dự kiến không: lệnh sửa bản ghi ảnh).
4. Một vòng đủ: Gửi nháp có ảnh đại diện, ghi SEO, Hẹn giờ. Phải hẹn giờ được. Rồi một vòng mở bài trong trang quản trị, bấm «Lưu nháp» sau khi app ghi xong, rồi mới Hẹn giờ: phải bị từ chối với câu `_RELEASE_CHANGED`, bài vẫn là nháp.

## Giới hạn

- `modified_gmt` của WordPress tính theo **giây**. Người khác sửa bài trong **cùng giây** với lệnh ghi cuối của app thì không phân biệt được. Khe rất hẹp, lại cần đúng lúc app đang ghi.
- Lệnh ghi của app bị lỗi giữa chừng thì coi là «không biết», nên lần đó không hẹn giờ/đăng được, phải làm trong trang quản trị. Hỏng theo hướng an toàn.

## Kiểm thử

- `tests/test_t115_modified_gmt.py`: **23 qua**. Gồm:
  - không bị sửa thì chuyển, lệnh kiểm xin `id,status,modified_gmt`;
  - ảnh đại diện, meta dự phòng cập nhật giá trị nhớ đúng thứ tự;
  - bị sửa sau lần ghi cuối thì từ chối, chỉ một lệnh `GET`, không lệnh chuyển, không trả mã;
  - lệnh kiểm trả `modified_gmt` lạ (9 dạng) hay lệnh tạo không trả (4 dạng) thì từ chối;
  - bị sửa giữa hai lệnh ghi của app thì không bị «rửa» bởi lệnh ghi sau;
  - lệnh ghi ảnh đại diện 503, lệnh ghi meta 502 thì «không biết»;
  - ghi qua Abilities giữ giá trị nhớ; nếu Abilities làm đổi giờ thì từ chối;
  - hai bài, hai client tách nhau;
  - `_fields` không xin trường dựng nội dung; câu báo cố định.
- Test liên quan: 80 file. Gồm mọi file test dùng `WordPressClient`, `fake_wordpress`, `release_draft` hay `seo_app.wordpress`: client WordPress T-042, T-054, T-060, T-061, T-085, T-088, T-091, T-099, T-102, T-110, trang ảnh, trang Kết nối WordPress, T-089. Kết quả: **10714 qua, 1 bỏ qua, 10 xfail có từ trước** (trong đó 3 ca SL-T102-1), 1 hỏng (1 giờ 17 phút).
  - Ca hỏng duy nhất là LC-T102-1 XPASS: lượt chạy này bắt đầu trước khi gỡ dấu. Sau khi gỡ dấu (Chỉ Huy duyệt 13:20), chạy lại `test_la_chan_t102.py`: **3 qua**.
  - Không ca XPASS nào khác.
- `uv run ruff check .`: All checks passed. `ruff format --check`: file mới sạch. `client.py` còn 2 chỗ bị đòi gộp dòng có từ trước (`_RELEASE_NOW_WITH_TIME`, một dòng `SeoWriteResult` trong `_seo_via_meta`; bản `HEAD` cũng vậy), không đụng tới.
- Quét ký tự vô hình trần và `detect-secrets` (`PYTHONUTF8=1`) trên `client.py`, file test mới, báo cáo. Chỉ có một kết quả «Basic Auth Credentials» ở `client.py:995`, và kết quả này đã có y hệt trên `HEAD` (`:986`, lệch 9 dòng do phần thêm mới), không do phiếu này.

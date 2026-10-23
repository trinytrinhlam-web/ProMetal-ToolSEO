# T-060 · Dọn lỗi Thấp của client WordPress sau T-042

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-19 |
| Giai đoạn | Giai đoạn 4 |
| Mức ưu tiên | Thấp (phải xong trước khi hết Giai đoạn 4; LC-T042-1 phải xong trước phiếu nào truyền tham số mới vào `_request`) |
| Phụ thuộc | T-042 đã gộp |
| Trạng thái | Thợ Máy xong, chờ Soi Lỗi |

## Mục tiêu

Client WordPress chặn cả tham số và header có thể đổi đường gọi, câu lỗi cũ không còn chép lời máy chủ hay địa chỉ.

## Bối cảnh

Lá Chắn T-042 (`docs/team/reports/T-042-la-chan.md`):

- **LC-T042-1:** `_request` chỉ kiểm đường, không kiểm tham số và header. `?rest_route=`, `?_method=`, `X-HTTP-Method-Override` có thể đổi đường hoặc phương thức (`seo_app/wordpress/client.py` khoảng dòng 810). Hôm nay không có đường tới vì mọi `params` do code viết sẵn.
- **LC-T042-4 (có từ trước):** `_error_from` cũ vẫn kèm "(WordPress: …)"; hàm khởi tạo chép lại `WORDPRESS_URL` khi sai phần đầu `https://` (khoảng dòng 876, 328).
- **LC-T042-5:** `WORDPRESS_URL` có `.pht`, `.cgi`, `.shtml` vẫn được nhận.

## Phạm vi

- **Được sửa:** `seo_app/wordpress/client.py`, test mới. Được sửa chuỗi mong đợi của test cũ về câu lỗi nếu cần, không nới kiểm tra.
- **Không được sửa:** `app/**`, `config/**`.

## Yêu cầu

1. `_request` từ chối tham số `rest_route`, `_method`, `_envelope`, `_jsonp` và header `X-HTTP-Method-Override` (danh sách cho phép tham số theo từng đường, hoặc danh sách cấm tối thiểu), có test.
2. Mọi câu lỗi là câu cố định kèm mã HTTP, không chép lời máy chủ, không chép `WORDPRESS_URL`.
3. Từ chối `WORDPRESS_URL` có đoạn đường là file thực thi (`.php` trừ `index.php` như T-042, `.pht`, `.phtml`, `.cgi`, `.shtml`, `.asp`, `.aspx`, `.jsp`).

## Yêu cầu bảo mật riêng

W3, W4, S2.

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (W3, S2).

## Ghi chú của Chỉ Huy
- 2026-10-21 (Chỉ Huy B): thêm từ Lá Chắn T-061 (`docs/team/reports/T-061-la-chan.md`, điều kiện 3–5): **LC-T061-2** (= SL-T061-1) trong `_seo_text` chặn mọi `<` mà ký tự ngay sau không phải khoảng trắng ASCII `[ \t\n\r\v\f]`, gỡ 4 `xfail` SL-T061-1 (hạn: trước khi bật ghi SEO cho người dùng ở T-041, hoặc đóng theo T-059 bước 4); **LC-T061-3** (= SL-T061-2) `upload_media` luôn ghi đè cả `alt_text`, `title`, `caption` (hoặc trang Kết nối WordPress đi qua `make_web_image`), gỡ 2 `xfail` SL-T061-2; **LC-T061-5** siết `tests/test_soi_loi_t042.py:423-424` (so phần đường **và** truy vấn). Phiếu này làm sau khi T-061 gộp.
- 2026-10-23 09:36 (Chỉ Huy B): Soi Lỗi T-071 nhắc: LC-T061-3 (`upload_media` luôn ghi đè cả ba ô) chưa ai làm, giữ trong T-060.
- 2026-10-23 11:10 (Chỉ Huy B): thêm **LC-T071-1** (Lá Chắn T-071, Thấp): `upload_media` (`seo_app/wordpress/client.py`, trang Kết nối WordPress) nhận mọi mã 2xx rồi ghi alt, tiêu đề, chú thích vào mã website trả → gọi `self._post_media(data, safe_name, content_type, new_only=True)`; gỡ 2 `xfail` trong `tests/test_la_chan_t071.py`, giữ ca đối chứng. Làm cạnh LC-T061-3. Theo mốc T-060 (trước khi hết GĐ4), không chặn T-056.
- 2026-10-23 17:22 (Chỉ Huy B): **chủ dự án duyệt giao Thợ Máy.** Nhánh `team/T-060` từ `main`, worktree `wt-T-060`. Chạy song song T-056 (Họa Sĩ): **không đổi hành vi `_has_shortcode`, `_SHORTCODE_OPEN`** (module mới `seo_app/wordpress/shortcodes.py` của T-056 dùng lại), không sửa `app/**`.
- 2026-10-23 18:01 (Chỉ Huy B): Thợ Máy xong phần 1 (`9f3b7e2`). Hỏi sửa 4 test cũ cho LC-T061-3 (`test_upload_media_with_alt`, `test_upload_media_without_metadata_is_one_request` → `…_still_overwrites_fields`, `test_upload_media_file`, `tests/test_soi_loi_t044.py::test_null_source_url_does_not_crash_page`): **Chỉ Huy đồng ý**, chỉ sửa đúng như mô tả, không nới kiểm tra, có bảng trước/sau cho Soi Lỗi soát R5.
- 2026-10-23 18:18 (Chỉ Huy B): **Thợ Máy xong** (`af6edfd`): 8/8 việc (LC-T042-1, -4, -5; LC-T061-2, -3, -5; LC-T071-1); gỡ `xfail` SL-T061-1, -2, LC-T071-1; sửa 4 test cũ theo LC-T061-3 (commit riêng `ee17bc9`, bảng trước/sau trong báo cáo); 2.350 test liên quan qua. Câu lỗi WordPress nay ngắn, không còn «(WordPress: …)». Chờ Soi Lỗi (phiếu ghi "Có", soát R5 4 test cũ).

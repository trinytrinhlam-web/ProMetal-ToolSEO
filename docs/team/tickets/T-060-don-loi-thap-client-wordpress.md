# T-060 · Dọn lỗi Thấp của client WordPress sau T-042

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-19 |
| Giai đoạn | Giai đoạn 4 |
| Mức ưu tiên | Thấp (phải xong trước khi hết Giai đoạn 4; LC-T042-1 phải xong trước phiếu nào truyền tham số mới vào `_request`) |
| Phụ thuộc | T-042 đã gộp |
| Trạng thái | Mới |

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

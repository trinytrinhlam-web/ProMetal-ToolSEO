# T-024 · Bộ lọc hồ sơ doanh nghiệp: lọc theo cả ý, không theo từng dòng

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Cao (thông tin chưa xác nhận có thể lọt vào bài) |
| Phụ thuộc | Không (làm song song T-018, T-022) |
| Trạng thái | Đã giao |

## Mục tiêu

Dòng nào trong `config/business_profile.md` chưa được chủ dự án xác nhận thì AI không bao giờ thấy, kể cả khi một ý viết dài nhiều dòng.

## Bối cảnh

- `seo_app/content/rules.py`, hàm `confirmed_profile`, lọc **từng dòng**. Nó bỏ dòng chứa `[CẦN XÁC NHẬN` và dòng bắt đầu bằng `>`.
- Ngòi Bút phát hiện ở T-022 (`docs/team/reports/T-022-ngoi-but.md`, nhánh `team/T-022`):
  1. Một gạch đầu dòng viết trên nhiều dòng (dòng sau thụt vào hai dấu cách) mà nhãn nằm ở **cuối dòng thứ hai**, đúng như hướng dẫn đầu file ("thêm `[CẦN XÁC NHẬN — lý do]` vào cuối dòng"). Khi đó dòng thứ nhất, chứa thông tin chưa xác nhận, **vẫn lọt vào prompt**. Ngược lại, nhãn ở dòng đầu thì các dòng tiếp theo lọt vào.
  2. Dòng ghi chú có dấu cách trước `>` (ví dụ `  > ghi chú`) không bị lọc.
- Chủ dự án sửa file này bằng Notepad, nên bộ lọc phải chịu được cách gõ thường gặp: dấu cách thừa, tab, Unicode dạng tổ hợp (NFD, gõ trên Mac).

## Phạm vi

- **Được sửa:** `seo_app/content/rules.py` (hàm `confirmed_profile` và hàm phụ nếu cần), test mới trong `tests/` cho phần mình làm.
- **Không được sửa:** `config/**` (Ngòi Bút), `seo_app/ai/**` (T-018 đang làm), `app/**`.
- **Ngoài phạm vi:** đổi cú pháp nhãn hay cách viết hồ sơ.

## Yêu cầu

1. Lọc theo **khối**: một gạch đầu dòng (`- …`, `* …`, `1. …`) cùng các dòng thụt vào ngay sau nó là một khối. Có nhãn ở bất kỳ dòng nào của khối thì bỏ cả khối. Đoạn văn thường (không phải gạch đầu dòng) thì khối là cả đoạn, ngăn bằng dòng trống. Tiêu đề (`#`) luôn đứng riêng một khối.
2. Dòng ghi chú: bỏ mọi dòng mà ký tự đầu tiên **không phải khoảng trắng** là `>`, kể cả dòng có dấu cách hoặc tab đứng trước.
3. Nhận nhãn không phân biệt hoa thường và dạng Unicode (chuẩn hóa NFC trước khi so), giữ cách khớp hiện tại `[CẦN XÁC NHẬN` (có hay không có phần lý do phía sau).
4. Không làm mất nội dung đúng: kết quả trên file thật ở nhánh `team/T-022` phải **giống hệt** kết quả của bộ lọc cũ, trừ chỗ bộ lọc cũ để lọt. Ghi phần so sánh vào báo cáo.
5. Test: ý nhiều dòng có nhãn ở dòng đầu, dòng giữa, dòng cuối; nhãn viết thường hoặc dạng NFD; `>` có dấu cách hoặc tab đứng trước; gạch đầu dòng lồng nhau; dòng trống giữa các khối; file rỗng; file chỉ có ghi chú.

## Yêu cầu bảo mật riêng

A1, A3 (thông tin chưa xác nhận không vào prompt), F3.

## Tiêu chí xong

- [ ] Không còn cách viết thường gặp nào làm dòng chưa xác nhận lọt vào prompt
- [ ] Kết quả trên file thật không mất dòng đúng nào
- [ ] `uv run pytest` và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-024-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có (thử các kiểu gõ lạ trong Notepad).
- Lá Chắn: Có (A1, A3).

## Ghi chú của Chỉ Huy

- Làm trong phiên con **"Thợ Máy · T-024 Bộ lọc hồ sơ"**, trên nhánh tạm `team/T-024`. Commit và đẩy lên `team/T-024`; không đẩy `main`. Chỉ Huy gộp vào `main` sau khi Lá Chắn ĐẠT.

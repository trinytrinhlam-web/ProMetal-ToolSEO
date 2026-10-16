# Biên bản bảo mật T-043 · Bộ lọc hồ sơ: 3 lỗi Thấp còn lại sau T-032

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (**Opus tạm**: Fable bị giới hạn tới 01/11, chủ dự án duyệt chạy tạm; kiểm lại bằng Fable sau 01/11) |
| Phiếu được kiểm | [T-043](../tickets/T-043-loc-ho-so-loi-thap-sau-t032.md) |
| Phạm vi | `git diff origin/main...team/T-043` (gốc `6cb6728`, đầu nhánh `7bf10a5`): `seo_app/content/rules.py`, `config/business_profile.md` (chỉ dòng `>`), 3 file test, 2 báo cáo |
| Ngày | 2026-10-16 |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** |

## Tóm tắt (cho chủ dự án)

Bản sửa an toàn và vẫn chạy nhanh với đầu vào xấu. Phần hồ sơ hiện tại mà AI thấy **giống hệt** bản đang chạy. Nhãn có in đậm, ngoặc kép, gạch nối hay ⚠ bên trong ngoặc giờ đã được nhận. Tôi tìm thêm một kiểu gõ rất hiếm mà bản cũ giấu còn bản mới để lọt: trong một ý đã có nhãn, có dòng thụt lề bắt đầu bằng `## …` và kết thúc bằng nửa nhãn kiểu `[CẦN`. Kiểu này gần như không gặp khi gõ hồ sơ trong Notepad. Tôi không chặn gộp. Điều kiện duy nhất là Chỉ Huy mở một phiếu theo dõi mức Thấp gộp lỗi này với 2 lỗi Soi Lỗi tìm ra. T-043 không cần làm thêm lượt.

## Lỗi phát hiện

Không có lỗi Nghiêm trọng, Cao hay Trung bình.

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| 1 | Thấp · không chặn | **LC-T043-1** (mới, **lùi so với `main`** trong một ca rất hẹp). Phần sửa SL-T032-5 (`rules.py:142`) tách một dòng thụt lề `## … [CẦN` ra khỏi ý phía trước, kể cả khi ý đó **đã có nhãn**. Nửa nhãn không ghép được với dòng kế, nên các dòng thụt lề sau đó (vốn thuộc ý có nhãn) thành một khối mới, không có nhãn. | `seo_app/content/rules.py:142-146` | `- giá [CẦN XÁC NHẬN]` / `  ## ghi chú [CẦN` / `  BIMAT` / `- ok` → trên `main` cả ý bị giấu; trên nhánh này `  ## ghi chú [CẦN` và `  BIMAT` tới AI. Muốn lọt cần ba điều cùng lúc: dòng nối thụt lề bắt đầu bằng `#` và dấu cách, nửa nhãn ở cuối dòng đó, nhãn không bao giờ được gõ hết. Fuzz 300.000 tài liệu ngẫu nhiên: mọi ca lùi đều cần dòng thụt lề `## … [nửa nhãn`; bỏ kiểu dòng này thì 0 ca lùi. | Ở `rules.py:142`, thêm điều kiện: khối đang mở đã có nhãn (`_is_unconfirmed(" ".join(block))`) thì để dòng nối vào khối như cũ. |
| 2 | Thấp · ghi nhận | Cùng nhánh code trên, ca **không có nhãn**: `- BIMAT` / `  ## 7 [CẦN XÁC` / `NHẬN]` → `- BIMAT` tới AI, trong khi `main` giấu nó (giấu nhờ may, vì nhãn thuộc tiêu đề). | `rules.py:142` | Ý `- BIMAT` không có nhãn của riêng nó. Hành vi này khớp với thiết kế đã duyệt ở SL-T032-2 (tiêu đề thụt lề có nhãn trọn cũng tách ý trước ra, `main` cũng vậy). | Không cần sửa. |
| 3 | Thấp · không chặn | **SL-T043-1** (Soi Lỗi): nhãn có từ 5 ký tự lạ trở lên thì lọt, ví dụ `[❗❗❗ **CẦN XÁC NHẬN**]`. Đã tái hiện. Cũng lọt trên `main`, nên không lùi. | `rules.py:27` | `- x [❗❗❗ **CẦN XÁC NHẬN**] BIMAT` → dòng tới AI. | Xem đánh giá ở dưới. |
| 4 | Thấp · không chặn | **SL-T043-2** (Soi Lỗi): `## 7 [CẦN XÁC` / `## NHẬN]` thì nội dung của mục lọt. Đã tái hiện. Cũng lọt trên `main`. | `rules.py:118-127` | `## 7 [CẦN XÁC` / `## NHẬN]` / `- BIMAT` / `## 8` → `- BIMAT` tới AI. Cần gõ nhầm `##` vào giữa nhãn. | Theo đề xuất của Soi Lỗi: dòng vừa ghép thành nhãn thì không được kết thúc mục giấu. |

## Đánh giá quyết định của Chỉ Huy về SL-T043-1, SL-T043-2

**Chọn (a): đồng ý ghi nhận, không sửa trong T-043.** Lý do:

- Cả hai ca đều lọt trên `main`, nên bản này không làm tệ hơn.
- Muốn lọt, chủ dự án phải gõ nhãn rất lạ: từ 5 ký tự lạ trở lên bên trong ngoặc, hoặc gõ `##` vào giữa nhãn. Hướng dẫn trong hồ sơ (`config/business_profile.md`, các dòng `>`) đã nêu mẫu chuẩn `[CẦN XÁC NHẬN — lý do]`.
- Nên **gộp vào phiếu theo dõi** cùng LC-T043-1, không đưa vào sổ rủi ro. Theo `security.md` (phần mức lỗi), chỉ chủ dự án được chấp nhận rủi ro thay vì sửa. Nếu chủ dự án không muốn sửa thì ghi cả 3 lỗi vào sổ rủi ro (mục 6).

**Nếu sau này sửa SL-T043-1 theo cách của Soi Lỗi** (`_GAP = r"(?:\s|[^\w\s\[\]()]|_)*+"`): **an toàn về ReDoS**, với 2 lưu ý.

- Lý do an toàn: ngoặc mở `[ (` không còn khớp được phần chen, nên mỗi điểm bắt đầu chỉ quét tới ngoặc kế tiếp. Hai nhánh `\s` và `[^\w\s\[\]()]|_` không chồng lên nhau, và lượng từ chiếm hữu `*+` không quay lui. Tôi đo trên mẫu đầy đủ, đầu vào 200 KB rồi 800 KB: `[[[`, `(((`, `[*`, `[ * `, `[CAN*`, `[CAN*[`, `(CAN XAC*(`, `[CAN * * *…`, `[CAN XAC****…[`. Tỉ lệ thời gian đều 3,9–4,1 (tuyến tính). Mẫu vẫn nhận các ca của SL-T043-1 và vẫn giữ `[*] cần xác nhận lịch`, `[ ] cần xác nhận`, `(xem) cần xác nhận`.
- Lưu ý 1: `_PARTIAL_TAG_REST` phải loại `[ (` tương tự. Cửa sổ `_PARTIAL_TAG_MAX = 64` cũng phải xem lại: không giới hạn số ký tự lạ thì nửa nhãn hợp lệ có thể dài hơn 64. Có thể giữ cửa sổ cố định và chấp nhận lọc thiếu khi nửa nhãn quá dài. Đừng bỏ cửa sổ, vì cửa sổ là thứ giữ cho mỗi dòng tốn thời gian cố định.
- Lưu ý 2: cần Python ≥ 3.11 cho `*+`. Dự án đã yêu cầu 3.12, nên không vướng.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | Soát diff `origin/main...HEAD` theo `api_key/password/secret/token`: không có dòng thêm nào. Không có file bí mật. |
| S2 | Không áp dụng | Không có log hay thông báo lỗi mới. |
| S3 | Không áp dụng | Không có biến cấu hình mới. |
| W1–W4 | Không áp dụng | Không đụng `seo_app/wordpress/`. |
| A1 | Đạt (kèm lỗi #1, Thấp) | Nhãn mới vẫn nằm trong `confirmed_profile`, chạy trước khi hồ sơ vào prompt. Mẫu nhãn mới chứa mẫu cũ (`{0,4}` cho phép 0 ký tự lạ), nên mọi nhãn trọn mà `main` nhận thì nhánh này vẫn nhận. `_PARTIAL_TAG_REST` cũng chứa `[A-Z\s]*` cũ, và nửa nhãn cũ dài nhất (22 ký tự sau khi gộp khoảng trắng) nằm gọn trong cửa sổ 64. Fuzz 300.000 tài liệu ghép từ 30 mảnh (nhãn trọn, nửa nhãn, tiêu đề thường, tiêu đề thụt lề, dòng `>`, dòng trống, ý có mã riêng): mọi ca lùi đều thuộc lỗi #1/#2; bỏ dòng thụt lề `## … [nửa nhãn` thì **0 ca lùi**. |
| A2 | Không áp dụng | Không đổi lớp AI. |
| A3 | Đạt | Nạp `rules.py` của `origin/main` và của nhánh cạnh nhau. Hồ sơ `main` qua bộ lọc `main` bằng hồ sơ nhánh qua bộ lọc nhánh: `equal: True`, 4826 ký tự. Hồ sơ nhánh qua bộ lọc `main` cũng ra y hệt. Diff `config/business_profile.md` chỉ có dòng bắt đầu bằng `>`: lọc diff, 0 dòng `+`/`-` khác. |
| U1–U3 | Không áp dụng | Không đụng `app/`. |
| F1 | Không áp dụng | Không có đường dẫn mới. |
| F2 | Không áp dụng | Không đụng ảnh. |
| F3 | Đạt | **ReDoS:** `_GAP` có giới hạn `{0,4}`, hai nhánh không chồng nhau. `_ends_with_partial_tag` chỉ xét 64 ký tự cuối, nên mỗi dòng tốn thời gian cố định. `_PARTIAL_TAG_REST` chạy `fullmatch` trên ≤ 64 ký tự. Đo `confirmed_profile` với đầu vào 200 KB rồi 800 KB: `[[[[`, `((((`, `[****`, `[ * `, `[_`, `[CAN*`, `[*CAN*XAC*`, dòng dài kết thúc bằng `[`, nhiều dòng `## [*`, nhiều dòng ` ## [CAN`, tiêu đề nửa nhãn rồi 800.000 dòng trống. Tỉ lệ thời gian 3,8–4,4 (tuyến tính). Ca chậm nhất là 1,8 s cho 800 KB toàn tiêu đề thụt lề, gấp nhiều lần hồ sơ thật (6 KB). |
| D1 | Đạt | `pyproject.toml`, `uv.lock` không đổi. |
| D2 | Đạt | `.gitignore` không đổi. |
| D3 | Đạt | 3 file test chỉ gọi `confirmed_profile` trên chuỗi. Không nhập `socket`, `requests` hay thư viện AI. Bộ chặn mạng chung trong `tests/conftest.py` vẫn bật. Diff `tests/test_soi_loi_t032.py` chỉ bỏ 2 dòng `xfail`, thân test giữ nguyên. |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| Soát diff theo từ khóa bí mật | 0 dòng | Có |
| Script dò so với `main` (fuzz 300.000 ca, A3, tốc độ) | Như trên | Có. Script trong scratchpad, không commit |
| pytest | 3660 passed, 4 skipped, 21 xfailed, 1 warning (cảnh báo pydantic của test lớp AI, có từ trước) | Có |
| ruff | All checks passed! | Có |

## Báo nhầm đã loại

- Lần so đầu bằng tập hợp dòng báo hàng nghìn "lùi". Nguyên nhân: các dòng nửa nhãn giống nhau lặp lại trong một tài liệu. Tôi đổi sang đánh mã riêng cho từng dòng nội dung và chỉ đếm mã bị lộ. Còn lại đúng lớp lỗi #1/#2.

## Điều kiện (nếu ĐẠT CÓ ĐIỀU KIỆN)

1. Chỉ Huy mở **một phiếu theo dõi mức Thấp** gộp LC-T043-1 (#1), SL-T043-1 (#3), SL-T043-2 (#4). Lỗi #1 sửa được bằng một điều kiện (xem bảng). Nếu sửa #3 theo cách của Soi Lỗi thì làm theo các lưu ý ReDoS ở trên. Phiếu này chỉ cần có trên bảng việc. T-043 được gộp ngay, không cần làm thêm lượt.
2. Nếu chủ dự án quyết định không sửa thì ghi 3 lỗi vào sổ rủi ro (`security.md` mục 6), do chủ dự án ký.

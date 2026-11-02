# T-118 · Dọn lỗi Thấp sau rà soát Fable: ẩn chi tiết lỗi trên trang, LC-T034-1..3, SL-T105-1, LC-T113-2

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-02 |
| Giai đoạn | Chung (bảo mật, dọn) |
| Mức ưu tiên | Thấp |
| Phụ thuộc | T-105, T-113 đã gộp `main` |
| Trạng thái | Đang làm |

## Mục tiêu

Gom các lỗi Thấp còn mở mà Lá Chắn (Fable, T-116 nhóm 3) và Soi Lỗi/Lá Chắn T-105, T-113 nêu vào một phiếu dọn nhỏ.

## Bối cảnh

- **Chủ dự án chọn 2026-11-02:** lỗi bất ngờ chỉ hiện **loại lỗi** trên trang (không đường dẫn); chi tiết vẫn ở cửa sổ dòng lệnh chạy app. Gốc: Lá Chắn T-001 #8, nhắc lại ở T-116 nhóm 3 (`docs/team/reports/T-116-la-chan-nhom-3.md`).
- **LC-T034-1:** tên mô hình dạng `https://…`/`www.` thành link trong `st.error`. **LC-T034-2:** `os.environb`/`getenvb` không bị che trong khung nhìn `os` đã lọc (`*_CUSTOM_HEADERS`). **LC-T034-3:** vòng trỏ `module.os` nằm trước `try`. (Biên bản T-034, T-116 nhóm 3.)
- **SL-T105-1:** chương trình khác **sửa** `.env` đúng lúc `set_password` vừa lưu → câu báo vẫn nói «dòng sai định dạng» (`docs/team/reports/T-105-soi-loi.md`).
- **LC-T113-2:** sửa tay ô `fetched_at` trong `data/plan_cache.sqlite` (`docs/team/reports/T-113-la-chan.md`).

## Phạm vi

- **Được sửa:** `.streamlit/config.toml` (chỉ `client.showErrorDetails`), `seo_app/ai/**` (đúng 3 chỗ LC-T034), `seo_app/env_file.py`, `scripts/hash_password.py` (câu báo SL-T105-1), `seo_app/plan/**` (cache LC-T113-2), test; gỡ `xfail` tương ứng khi XPASS (chỉ xóa dấu, R5).
- **Không được sửa:** `app/**` ngoài việc cần thiết cho câu báo; cách băm mật khẩu.

## Yêu cầu

1. `client.showErrorDetails = "type"` kèm chú thích tiếng Việt (chủ dự án chọn 02/11); kiểm lỗi bất ngờ trên trang không còn đường dẫn (test AppTest nếu được).
2. LC-T034-1: tên mô hình hiện thuần (không thành link) ở mọi câu báo; LC-T034-2: `environb`/`getenvb` cũng bị che; LC-T034-3: dời vòng trỏ vào trong `try`.
3. SL-T105-1: phân biệt «file vừa bị chương trình khác sửa» với «dòng sai định dạng» (hoặc câu chung đúng sự thật).
4. LC-T113-2: `fetched_at` hỏng/lạ trong cache → coi như cache cũ, đọc lại khi bấm; không lỗi trang.
5. Không lùi T-034, T-090, T-104, T-105, T-109, T-113.

## Yêu cầu bảo mật riêng

U2, U3, F3.

## Tiêu chí xong

- [ ] Yêu cầu 1–5
- [ ] Test liên quan + `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-118-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn.

## Ghi chú của Chỉ Huy

- Lập 2026-11-02 theo T-116 nhóm 3 (Fable) và quyết định của chủ dự án về hiện lỗi.
- 2026-11-02 17:23 (Chỉ Huy B): giao Thợ Máy (phiên T-075) 13:20, nhánh `team/T-118` từ `main` `935d381`.

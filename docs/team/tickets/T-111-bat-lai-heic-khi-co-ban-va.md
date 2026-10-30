# T-111 · Bật lại nhận ảnh HEIC khi có pillow-heif mang libheif ≥ 1.23.7

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-30 |
| Giai đoạn | Giai đoạn 3 (việc sau khi đóng giai đoạn) |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | Có bản pillow-heif mang libheif ≥ 1.23.7 trên PyPI (hiện mới có 1.8.1, mang libheif 1.23.6) |
| Trạng thái | Chờ (bản pillow-heif mới) |

## Mục tiêu

App nhận lại ảnh HEIC của iPhone (quyết định 1A ngày 2026-10-19) sau khi thư viện đã vá các lỗi libheif 1.23.6, giữ mọi lớp chặn của T-107.

## Bối cảnh

- T-107 (gộp `main` 30/10): lượt 1–2 giải mã HEIC một luồng, kiểm lưới ô trước khi giải mã (LC-T093-3); lượt 3 **tạm không nhận HEIC** bằng công tắc `HEIC_ENABLED = False` trong `seo_app/images/folders.py` (chủ dự án chọn 30/10 vì LC-T107-2: libheif 1.23.6 còn lỗi làm treo, vá ở 1.23.7), chặn HEIC có alpha trước giải mã (LC-T107-1).
- Chủ dự án đồng ý 30/10 (câu 4 rà soát Giai đoạn 3): nâng pillow-heif ngay khi có bản mang libheif ≥ 1.23.7, **sau khi Lá Chắn quét, không cần hỏi lại**.
- Lá Chắn T-107 lượt 3 (`docs/team/reports/T-107-la-chan.md`, mục «Lượt 3») ghi 8 điều kiện trước khi bật lại.

## Phạm vi

- **Được sửa:** `pyproject.toml`, `uv.lock` (chỉ pillow-heif), `seo_app/images/**`, `README.md` (câu về HEIC), test.
- **Không được sửa:** `app/**` (trừ khi câu báo cần, hỏi Chỉ Huy), `config/**`.

## Yêu cầu (8 điều kiện của Lá Chắn T-107 lượt 3)

1. Có pillow-heif mang libheif ≥ 1.23.7; Lá Chắn quét bản mới (khuyến cáo, giấy phép, thư viện C trong wheel) trước khi gộp.
2. Test chốt LC-T107-2 (`tests/test_la_chan_t107.py`, đọc thẳng công tắc và danh sách định dạng) phải qua mà **không sửa**.
3. Sửa **LC-T107-3 (Thấp)**: ảnh chính kiểu `iden` trỏ tới ảnh có alpha báo «RGB», lọt phép chặn alpha nhưng libheif vẫn giải mã alpha. Gợi ý: đọc khung HEIF bằng Python trước khi mở, chỉ nhận ảnh chính `hvc1` hoặc `grid` gồm các ô `hvc1`. Test `xfail(strict=True)` (4 ca) phải XPASS rồi gỡ dấu.
4. Giữ giải mã một luồng (`DECODE_THREADS = 0`), `_check_heif_grid` và chặn alpha.
5. Chạy lại các script dựng file tấn công của Soi Lỗi, Lá Chắn T-107 (thư mục ghi chú chung `T-107-soi-loi-scripts/`, `T-107-la-chan-scripts/`) trên libheif mới.
6. Thử ảnh HEIC chụp thật từ iPhone (giữ GPS, xoay đúng; ghi số đo tốc độ).
7. Sửa README: bỏ câu «tạm chưa nhận HEIC», giữ cách cho iPhone chụp JPEG như một lựa chọn.
8. Sửa **SL-T107-3 (Thấp)**: mở lại nháp cũ đã chọn ảnh `.heic` khi HEIC tắt thì ảnh bị bỏ với câu «bị hỏng» (sai lý do) và tự lưu xóa hẳn alt đã duyệt; nên giữ lựa chọn và báo đúng lý do «tạm chưa nhận HEIC». Có thể làm sớm ở một phiếu dọn nhỏ nếu máy rảnh.

## Yêu cầu bảo mật riêng

F1, F2, S1 (thư viện).

## Tiêu chí xong

- [ ] Yêu cầu 1–8
- [ ] Test liên quan + `uv run ruff check .`; toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-111-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Đầy đủ (thư viện mới).

## Ghi chú của Chỉ Huy

- Lập 2026-10-30 theo biên bản Lá Chắn T-107 lượt 3 và quyết định 4 của chủ dự án (30/10). Kiểm PyPI định kỳ: `uv pip index versions pillow-heif` hoặc trang PyPI; ghi libheif đi kèm từ ghi chú phát hành.

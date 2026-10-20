# T-066 · Dọn lỗi Thấp lớp ảnh gửi AI (sau T-050)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-20 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Thấp (gộp trước T-056 và trước khi hết Giai đoạn 3) |
| Phụ thuộc | T-050 đã gộp; nên sau T-049 (bản gửi AI không còn hồ sơ màu) |
| Trạng thái | Mới |

## Mục tiêu

Bộ kiểm ảnh gửi AI (`prepare_images` trong `seo_app/ai/base.py`) từ chối mọi hồ sơ màu và khối dựng cố ý, để không còn chỗ nhét chữ tự do hay GPS vào ảnh trước khi tới hãng AI.

## Bối cảnh

Biên bản Lá Chắn T-050 (`docs/team/reports/T-050-la-chan.md`), điều kiện 1: LC-T050-1 (= SL-T050-5, hồ sơ màu ICC chỉ được kiểm 132 byte đầu), LC-T050-2 (= SL-T050-6 mở rộng: khối lặp, dài hơn khuôn, DAC dài tùy ý, DQT lặp chở chữ), LC-T050-3 (chú thích nói quá khả năng lớp kiểm). Báo cáo Soi Lỗi T-050 lượt 2 có 15 test `xfail` cho các lỗi này.

## Phạm vi

- **Được sửa:** `seo_app/ai/base.py`, `tests/test_ai_images.py`, `tests/test_soi_loi_t050.py` (chỉ gỡ dấu `xfail` khi XPASS, đổi các ca ICC theo thiết kế mới).
- **Không được sửa:** `seo_app/images/**`, `app/**`, `config/**`.

## Yêu cầu

1. `prepare_images` từ chối **mọi** hồ sơ màu (JPEG APP2 `ICC_PROFILE`, PNG `iCCP`, WebP `ICCP`); bỏ `_icc_ok`, `_jpeg_icc_ok`, `_check_png_icc` và lần giải nén zlib.
2. Sửa theo SL-T050-6: APP0 và APP14 tối đa một lần; khối giải mã đúng độ dài theo số thành phần; bỏ DAC, chỉ nhận SOF0/1/2; PNG `PLTE` chỉ khi loại màu 3, `tRNS` đúng độ dài theo loại màu; bỏ `cHRM`, `sBIT`, `bKGD` nếu bản gửi AI của T-049 không cần.
3. Viết lại chú thích `base.py:552–556`, `:686–687` cho đúng khả năng thật của lớp kiểm (mẫu ở LC-T050-3).
4. Gỡ 15 dấu `xfail` SL-T050-5/-6 khi XPASS; ảnh sạch do T-049 tạo (bản gửi AI) vẫn qua.

## Yêu cầu bảo mật riêng

A3.

## Tiêu chí xong

- [ ] Đạt mọi yêu cầu trên, có test
- [ ] `uv run pytest` (0 hỏng, 0 lỗi trên Windows) và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-066-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Rút gọn. Lá Chắn: Rút gọn (A3).

## Ghi chú của Chỉ Huy

- Lập theo điều kiện 1 của Lá Chắn T-050. Việc này đổi thiết kế T-046 mục 3: bản gửi AI **không còn hồ sơ màu** (Chỉ Huy B duyệt, vì T-049 đã buộc bản gửi AI không kèm hồ sơ màu theo điều kiện 2 của Lá Chắn T-050).

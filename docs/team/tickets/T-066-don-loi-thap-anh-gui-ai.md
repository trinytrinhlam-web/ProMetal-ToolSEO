# T-066 · Dọn lỗi Thấp lớp ảnh gửi AI (sau T-050)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-20 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Thấp (gộp trước T-056 và trước khi hết Giai đoạn 3) |
| Phụ thuộc | T-050 đã gộp; nên sau T-049 (bản gửi AI không còn hồ sơ màu) |
| Trạng thái | Đang làm |

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
- 2026-10-22 18:07 (Chỉ Huy B): giao (chủ dự án "tiếp tục"). Nhánh `team/T-066` tạo từ `main` sau khi gộp T-039, T-069. Phiếu trước T-056.
- 2026-10-23 07:57 (Chỉ Huy B): Thợ Máy **xong** (`66f58dd`): mọi hồ sơ màu trong ảnh gửi AI bị từ chối, siết khối JPEG/PNG theo SL-T050-6, gỡ 15 `xfail`; ảnh sạch do `make_ai_image` tạo vẫn qua; 1.266 test liên quan qua. Chờ Soi Lỗi rút gọn.
- 2026-10-23 09:36 (Chỉ Huy B): **Soi Lỗi rút gọn ĐẠT** (`f8e6d21`): 0 lỗi mới; YC1–4 đạt; 892/892 bản gửi AI từ 446 ảnh thật qua (không chặn oan); 2 triệu tệp đột biến, trọng tài Pillow: 0 lọt; 27 test mới. Ghi nhận 1 (chú thích `base.py:553–554` hơi rộng; DRI/DNL lặp, SOS khai thừa thành phần) cùng loại LC-T050-2, để Lá Chắn quyết. Chờ Lá Chắn rút gọn.
- 2026-10-23 09:40 (Chỉ Huy B): chủ dự án duyệt: giao Lá Chắn rút gọn (A3).
- 2026-10-23 10:00 (Chỉ Huy B): **Lá Chắn rút gọn ĐẠT** (`3a76a3b`): 0 lỗi mới; LC-T050-1, -3, SL-T050-5, -6 đóng; LC-T050-2 đóng phần sửa được, phần còn lại (ảnh dựng cố ý giấu dữ liệu trong phần ảnh nén, DQT/DHT, DRI/DNL/SOS) đề nghị **ghi sổ rủi ro** (dòng mẫu trong biên bản, chờ chủ dự án duyệt; không chặn gộp). Sửa chữ chú thích `base.py:553–555` khi tiện. **Gộp được ngay**; Chỉ Huy gộp cùng T-071 khi Lá Chắn T-071 xong.
- 2026-10-23 10:54 (Chỉ Huy B): **chủ dự án đồng ý ghi sổ rủi ro** phần còn lại LC-T050-2 (ảnh dựng cố ý giấu dữ liệu trong phần ảnh nén, DQT/DHT, DRI/DNL/SOS); đã thêm vào `docs/team/security.md` mục 6.
- 2026-10-23 11:10 (Chỉ Huy B): **đã gộp vào `main` (Windows 23/10: 11.578 test qua, 0 hỏng)**; xóa nhánh `team/T-066`, worktree `wt-T-066`. Việc khi tiện: sửa chữ chú thích `base.py:553–555` theo biên bản Lá Chắn (làm cùng phiếu nào sau này chạm `base.py`).

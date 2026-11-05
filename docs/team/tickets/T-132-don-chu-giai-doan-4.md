# T-132 · Dọn chữ Giai đoạn 4: trang Kết nối khuyên đúng tài khoản Biên tập viên, vài lỗi Thấp meta

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`); Chỉ Huy duyệt cho Thợ Máy sửa câu trên `app/views/wordpress.py`, `app/views/write.py` (việc Họa Sĩ) để khỏi chia hai nhánh |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-05 |
| Giai đoạn | Giai đoạn 4 (điều kiện đóng, T-129) |
| Mức ưu tiên | Trung bình (trước bản 1.0) |
| Phụ thuộc | Không |
| Trạng thái | Đang làm |

## Mục tiêu

Đóng điều kiện 1 của Lá Chắn T-129 và dọn mấy lỗi chữ Thấp còn mở của Giai đoạn 4.

## Yêu cầu

1. **Bắt buộc · SL-T106-1:** `app/views/wordpress.py:131-134` chỉ khuyên tài khoản **Biên tập viên** (không khuyên «Quản trị viên»); gỡ `xfail` trong `tests/test_soi_loi_t106.py` (R5: chỉ xóa dấu).
2. Tùy chọn (làm nếu nhỏ, gọn): LC-T036-2, SL-T036-11 (`seo_app/onpage/meta.py`); một dòng chú thích dưới ô «Dùng schema FAQ»: «app chưa gửi schema lên website»; mở hàm công khai thay cho chỗ gọi `client._own_draft`.
3. Không đụng vùng bước Xuất bản và xóa nháp của `write.py` (T-130 đang sửa).

## Phạm vi

- **Được sửa:** `app/views/wordpress.py`, phần bước SEO của `app/views/write.py`, `seo_app/onpage/meta.py`, chỗ gọi `_own_draft`, test.

## Tiêu chí xong

- [ ] Yêu cầu 1 (bắt buộc), 2 (ghi rõ làm/không làm từng mục); test liên quan + `uv run ruff check .`; báo cáo `docs/team/reports/T-132-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: rút gọn. Lá Chắn: rút gọn.

## Ghi chú của Chỉ Huy

- Lập 2026-11-05 theo «Phiếu B» Lá Chắn T-129. Worktree `wt-T-132`, nhánh `team/T-132`.

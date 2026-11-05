# T-131 · Dọn kho dữ liệu phụ: kiểm file và chặn `data/` là liên kết cho mọi kho SQLite

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-05 |
| Giai đoạn | Giai đoạn 4 (điều kiện đóng, T-129) |
| Mức ưu tiên | Trung bình (trước bản 1.0) |
| Phụ thuộc | T-122 đã gộp (mẫu `search_cache`); phần `drafts.py` làm **sau khi T-130 gộp** |
| Trạng thái | Đang làm |

## Mục tiêu

Mọi kho SQLite trong máy kiểm file và từ chối `data/` là liên kết theo cùng một mẫu đã qua Lá Chắn ở `search_cache` (T-122), để đóng điều kiện 2 của Lá Chắn T-129.

## Bối cảnh

- Biên bản Lá Chắn T-129 (`docs/team/reports/T-129-la-chan.md`) mục 4, 5 «Phiếu A»: LC-T129-1 (Thấp), SL-T117-1 (Thấp), mẫu LC-T122-1.

## Yêu cầu

1. `seo_app/storage/site_index.py`: kiểm file như `search_cache` (LC-T129-1).
2. `site_index`, `plan_cache`, `drafts`: `data_dir.dir_has_link` ngay từ đầu (SL-T117-1).
3. `plan_cache._is_healthy`: lỗi giải mã, «unsupported file format» coi là file lạ (cùng mẫu LC-T122-1).
4. **`drafts.py` làm sau cùng, khi T-130 (Họa Sĩ, cùng file) đã gộp `main`**: gộp `main` vào nhánh rồi mới sửa; kho nháp giữ khóa chống gửi trùng nên không được làm mất trạng thái gửi.
5. Test ghim từng phần; sửa hàm dùng chung thì chạy test mọi nơi gọi và test quét cả gói.

## Phạm vi

- **Được sửa:** `seo_app/storage/site_index.py`, `plan_cache.py`, `drafts.py` (chỉ phần mở kho, kiểm file), test.
- **Không được sửa:** khối SEO và trạng thái gửi trong `drafts.py` ngoài việc mở kho.

## Tiêu chí xong

- [ ] Yêu cầu 1–5; test liên quan + `uv run ruff check .`; báo cáo `docs/team/reports/T-131-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: rút gọn. Lá Chắn: **đầy đủ** (đụng `drafts.py`).

## Ghi chú của Chỉ Huy

- Lập 2026-11-05 theo «Phiếu A» Lá Chắn T-129. Worktree `wt-T-131`, nhánh `team/T-131`.

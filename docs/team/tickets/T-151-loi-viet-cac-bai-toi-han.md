# T-151 · Lõi «Viết các bài tới hạn» (phiếu K)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-19 |
| Giai đoạn | Chế độ tự động (thiết kế T-141) |
| Mức ưu tiên | Cao |
| Phụ thuộc | **Đợt 4**: sau T-149 (lượt chạy, sổ việc, phần thuần của kế hoạch). Song song T-150, T-146 (khác file) |
| Trạng thái | Mới |

## Mục tiêu

Chọn các dòng kế hoạch tới hạn, ghi «Đang viết» lên Google Sheet, rồi viết **lần lượt** từng bài bằng lượt chạy T-149. Bài xong là «Chờ duyệt»; **không gửi gì lên website**. Giao diện ở T-152.

## Bối cảnh

- Thiết kế T-141: 4.1, 4.2 (chọn dòng, chạy lô), 2.5 (hai máy), 6.5 (ước lượt trước khi chạy), 7.2 dòng K; câu trả lời của chủ dự án 2A (dòng quá hạn), 3A (khóa khi đủ 5 bài chờ duyệt).
- Biên bản Lá Chắn T-141 (`03568dc`): mục 4 (5), mục 7, mục 8 dòng K; LC-T141-24: phiếu này nâng lên **Lá Chắn đầy đủ** (ghi Sheet, chọn dòng từ dữ liệu chưa tin cậy, tạo nháp hàng loạt). Yêu cầu sửa của Lá Chắn ở phiếu này: **trần 5 bài chờ duyệt** (LC-T141-14).
- Mã có sẵn: `seo_app/plan/sync.py` (`get_plan`, `open_row`, `plan_ref`, `status_write`, `write_status`, `record_status`), `seo_app/plan/model.py` (`PlanRow`, `parse_key`, `mask_personal_info`, các trạng thái), `DraftStore.find_plan_draft`, `MAX_DRAFTS = 30` (kho bỏ nháp cũ nhất khi đầy, kể cả bài chưa gửi).

## Yêu cầu

1. **Dòng được chọn** (`seo_app/auto/batch.py`, hàm thuần):
   - có Mã bài; dòng qua `PlanRow`, `parse_key`;
   - Trạng thái **«Chưa viết»** (dòng «Đang viết» bỏ qua);
   - Ngày dự kiến từ hôm nay tới 6 ngày sau, **hoặc đã quá ngày** (2A);
   - Loại trang không phải «Cập nhật bài cũ»;
   - máy này chưa có nháp của Mã bài đó (`find_plan_draft` theo mã băm Sheet đang dùng).
   - Thứ tự: ngày dự kiến (dòng quá hạn đứng trước), giờ đăng, Ưu tiên (Cao trước), Mã bài.
2. **Trần** (**LC-T141-14**): lấy tối đa `min(5, 5 − số bài chờ duyệt chưa gửi trên máy)` dòng, và không quá chỗ trống của kho nháp (lô không bao giờ làm kho bỏ nháp chưa gửi).
   - «Bài chờ duyệt chưa gửi» = nháp có `auto` đã chạy xong mà chưa có trạng thái gửi; định nghĩa đúng trong mã, ghi trong báo cáo.
   - Bằng 0 thì trả lý do để giao diện khóa nút kèm câu nhắc (T-152).
3. **Chạy lô** (LC-T141-15):
   - **Lúc bấm:** đọc lại Sheet (LC-T094-29).
   - **Trước từng dòng:**
     - `open_row`: dòng còn «Chưa viết» và còn hợp lệ thì làm tiếp;
     - tạo nháp gắn kế hoạch (`plan_ref`, phần thuần của `fill_from_plan` ở T-149);
     - ghi chú qua `mask_personal_info` **trước** khi vào chất liệu thật và lời dặn; bản chưa che không bao giờ lưu nháp;
     - ghi «Đang viết» qua `status_write` / `record_status` (như `start_from_plan`); kết quả không phải WRITTEN hay ALREADY thì bỏ dòng, ghi mã lý do;
     - giao bài cho lượt chạy T-149.
   - Các bài chạy lần lượt, không song song.
4. **Khi nào dừng lô:**
   - `quota_day`: dừng lô; dòng chưa tới lượt không bị đụng (vẫn «Chưa viết»);
   - 2 bài liền dừng vì `rate` hay `busy` (LC-T141-13): dừng lô;
   - `auth`, `model`, `bad_request`: dừng lô.
5. **Không gửi gì lên website** (LC-T094-35): lô không gọi WordPress, kể cả đọc (danh sách bài chỉ từ bản lưu trên máy); không bao giờ gửi, hẹn giờ, đăng hàng loạt.
6. **Sổ việc:** ghi Mã bài đang được lô xử lý (`parse_key`). Nút «Viết bài» ở trang Kế hoạch gặp Mã bài này thì mở bài đang chạy, không tạo nháp thứ hai (T-141 2.5).
7. **Ước lượt cho popover** (T-141 6.5): số lần gọi Gemini cần (khoảng 8 mỗi bài), số đã gọi hôm nay (kho đếm T-143), trần `[auto]` (T-148). Thiếu thì đề nghị số bài vừa đủ.
8. **Chữ Sheet** chỉ trả cho giao diện như dữ liệu (giao diện hiện chữ thuần, LC-T094-3, ở T-152); sổ việc không giữ chữ Sheet (LC-T141-9).
9. **Test** (LC-T141-21), Sheets giả, AI giả, Cloudflare giả dưới bộ chặn mạng:
   - **0 request WordPress, 0 kết nối ra ngoài**;
   - ba mức bài chờ duyệt (0, 2, 5) và giới hạn chỗ trống kho nháp; dòng quá hạn đứng trước;
   - dòng đổi trên Sheet giữa lúc bấm và lúc tới lượt → bỏ dòng; «Đang viết» do máy khác ghi → bỏ dòng;
   - `quota_day` dừng lô, dòng sau không bị đụng; hai bài liền `busy` dừng lô;
   - ghi chú có số điện thoại, email không bao giờ lưu nháp khi chưa che.

## Phạm vi

- **Được sửa:** `seo_app/auto/batch.py` (mới), `seo_app/auto/runner.py` (chỉ phần hàng đợi lô, nếu cần), test mới `tests/test_t151_*.py`.
- **Không được sửa:** `seo_app/plan/sync.py`, `seo_app/plan/model.py` (dùng hàm có sẵn), `seo_app/storage/drafts.py`, `app/**` (T-150, T-152).
- **Ngoài phạm vi:** nút, popover, danh sách «Chờ duyệt» (T-152); đọc lại dòng khi mở bài ở bước 5 (T-150).

## Yêu cầu bảo mật riêng (điều kiện Lá Chắn)

W1, W2 (lô không có lệnh WordPress nào), A1 (chữ Sheet vào lời dặn trong khung dữ liệu), A3 (che số điện thoại, email), D3. Ghi Google Sheet chỉ qua lớp ghi có kiểm xung đột (`write_status`).

- **LC-T141-14** (trần `min(5, 5 − bài chờ duyệt)`, chỗ trống kho nháp, bằng 0 thì khóa; test ba mức 0, 2, 5).
- **LC-T141-15** (mọi dòng qua `PlanRow`, `parse_key`; đọc lại Sheet lúc bấm và `open_row` trước từng dòng; «Đang viết» qua `status_write` / `record_status`, không WRITTEN/ALREADY thì bỏ dòng; che ghi chú trước khi vào chất liệu, bản chưa che không lưu; không gọi WordPress; chữ Sheet là chữ thuần ở giao diện).
- **LC-T141-21** (test bắt buộc: 0 WordPress, 0 kết nối ngoài).
- **LC-T094-29** (đọc lại Sheet trước khi ghi và trước khi mở bài từ một dòng), **LC-T094-35** (không gửi, hẹn, đăng hàng loạt), **LC-T094-21** (che tự động: bản chưa che không bao giờ rời máy).

## Tiêu chí xong

- [ ] Yêu cầu 1–9, có test.
- [ ] Test liên quan + test kế hoạch có sẵn gọi `open_row`, `record_status` (T-100, T-101, T-113) qua; `uv run ruff check .` sạch.
- [ ] Báo cáo `docs/team/reports/T-151-tho-may.md`.

## Kiểm thử và kiểm định

- Soi Lỗi: Có (trần, dòng đổi giữa chừng, hai máy, dừng lô).
- Lá Chắn: **đầy đủ** (LC-T141-24).

## Lưu ý chung

- Chỉ chạy test trong worktree của phiếu (`D:/ProMetal-ToolSEO/wt-T-151`), **không** chạy trong `D:/ProMetal-ToolSEO/ProMetal-ToolSEO`.
- Không chạy toàn bộ `uv run pytest`: chạy test liên quan, test của mọi nơi gọi hàm sửa, `uv run ruff check .`.
- Tham số test lớn kèm `ids=` ngắn.
- Test không gọi AI, Cloudflare, Google, WordPress thật. Lô thử trên Sheet bản sao chỉ ở buổi thử cùng chủ dự án (LC-T141-23).
- Không đọc `.env`, không in hay commit khóa; `detect-secrets` (`PYTHONUTF8=1`, có file mồi) sạch.
- Đổi kỳ vọng test cũ: theo R5.

## Ghi chú của Chỉ Huy

- Lập 2026-11-19 từ thiết kế T-140/T-141 (phiếu K, mục 7 của `docs/team/reports/T-141-tho-may.md`; biên bản Lá Chắn `fb9d2ef`, `03568dc`). Worktree `wt-T-151`, nhánh `team/T-151`.

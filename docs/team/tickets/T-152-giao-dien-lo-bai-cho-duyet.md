# T-152 · Giao diện «Viết các bài tới hạn», danh sách «Chờ duyệt» (phiếu L)

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-19 |
| Giai đoạn | Chế độ tự động (thiết kế T-141) |
| Mức ưu tiên | Cao |
| Phụ thuộc | **Đợt 5**: sau T-151 (lõi lô) và T-150 (mở bài ở bước 5, cờ bắt đầu tự động). Cùng lúc T-147 |
| Trạng thái | Mới |

## Mục tiêu

- **Trang Kế hoạch:** nút «🤖 Viết các bài tới hạn» (popover xác nhận, tiến độ lô dạng gọn).
- **Trang Bài viết:** thay khung demo «Đang viết» bằng danh sách thật «⏳ Đang chạy», «🟡 Chờ duyệt», «⚠️ Dừng giữa chừng»; popover «✍️ Viết bài mới» có thêm «🤖 Soạn tự động».

## Bối cảnh

- Thiết kế T-141: 4.1–4.3 (chọn dòng, chạy lô, danh sách «Chờ duyệt»), 2.2, 2.3 (tiến độ, nút), 7.2 dòng L; câu trả lời của chủ dự án 2A, 3A.
- Biên bản Lá Chắn T-141 (`03568dc`): mục 4 (5), mục 7, mục 8 dòng L. Hai yêu cầu sửa của Lá Chắn chạm phiếu này: **trần 5 bài chờ duyệt** (LC-T141-14, phần giao diện) và **đọc lại dòng Sheet khi mở bài «Chờ duyệt»** (LC-T141-16: phần kiểm ở bước 5 do T-150 làm; phiếu này chỉ mở bài qua đường đó).
- Mã có sẵn: `app/views/plan.py` (`plan_list`, `write_picker`, `start_writing`), `app/views/home.py` (khung «Đang viết» đọc `demo.ARTICLES_IN_PROGRESS`; nhãn `WEB_LABELS["pending"] = «Chờ duyệt»` của khung «Đã gửi WordPress»).

## Yêu cầu

1. **Nút ở trang Kế hoạch:**
   - nút ghi số dòng đủ điều kiện, tính từ bản kế hoạch lưu trên máy; mở trang không gọi Google;
   - bấm thì popover liệt kê «Mã bài · từ khóa · ngày giờ» bằng chữ thuần (`st.dataframe`, `st.text` hay `escape_markdown`: LC-T094-3);
   - popover có ước tính (lần gọi Gemini, ảnh AI, thời gian), số lần đã gọi hôm nay; nút «Bắt đầu» gọi lô T-151.
2. **Khóa nút** (LC-T141-14): T-151 trả trần bằng 0 (đã có 5 bài chờ duyệt chưa gửi, hay kho nháp hết chỗ) thì nút khóa, kèm câu nhắc «Duyệt bớt các bài chờ duyệt rồi viết tiếp».
3. **Tiến độ lô dạng gọn** ở Kế hoạch: chỉ đọc sổ việc trong bộ nhớ (LC-T141-20). Không mạng, không AI, không ghi đĩa; không `st.fragment(run_every)`.
4. **Trang Bài viết**, thay khung demo «Đang viết» bằng thẻ thật đọc từ kho nháp và sổ việc:
   - «⏳ Đang chạy»: bước, thời gian, nút Dừng;
   - «🟡 Chờ duyệt»: từ khóa, Mã bài, ngày giờ dự kiến, số chỗ vàng; nút «Mở để duyệt» mở Soạn bài ở bước 5 (`_open_draft`; kiểm dòng Sheet ở T-150, LC-T141-16);
   - «⚠️ Dừng giữa chừng»: lý do (từ mã lý do cố định), nút «Chạy tiếp».
   - Mọi chữ từ Sheet, AI là chữ thuần (LC-T094-3, LC-T141-15).
   - Xóa mẫu không còn dùng trong `seo_app/demo.py` (`ARTICLES_IN_PROGRESS`) nếu không trang nào khác dùng.
5. **Đổi nhãn:** huy hiệu trạng thái `pending` của WordPress ở khung «Đã gửi WordPress»: «Chờ duyệt» → **«Chờ duyệt trên website»**, để khỏi nhầm với danh sách mới.
6. **Popover «✍️ Viết bài mới»:** thêm nút «🤖 Soạn tự động». Nút đặt `_start_keyword` và cờ bắt đầu tự động (tên cờ thống nhất với T-150); nút «Bắt đầu» cũ (soạn từng bước) giữ nguyên.
7. **Mở trang không gọi mạng:** không gọi Google, WordPress khi chỉ mở trang (danh sách đọc từ kho nháp, bản lưu kế hoạch).
8. **Test** AppTest dưới bộ chặn mạng:
   - số dòng; popover hiện chữ thuần với chữ Sheet trông như Markdown, HTML; khóa ở 5 bài chờ duyệt (và 0, 2);
   - mở trang 0 request Google, WordPress; khung demo không còn; nhãn mới;
   - «Mở để duyệt» mở đúng nháp ở bước 5.

## Phạm vi

- **Được sửa:** `app/views/plan.py`, `app/views/home.py`, `seo_app/demo.py` (chỉ xóa mẫu không dùng), test mới `tests/test_t152_*.py`.
- **Không được sửa:** `app/views/write.py` (T-150), `seo_app/auto/**` (T-149, T-151), `seo_app/plan/**`, `seo_app/storage/**`.
- **Ngoài phạm vi:** lõi chọn dòng, ghi Sheet (T-151); kiểm dòng Sheet ở bước 5 (T-150).

## Yêu cầu bảo mật riêng (điều kiện Lá Chắn)

U1 (chữ Sheet, chữ AI hiện thuần), U2, D3.

- **LC-T141-14** (khóa nút khi trần bằng 0, kèm câu nhắc), **-15** (chữ Sheet ở popover, tiến độ, «Chờ duyệt» là chữ thuần), **-16** («Mở để duyệt» đi qua chốt đọc lại dòng ở bước 5 của T-150; danh sách không gọi Google), **-20** (tiến độ chỉ đọc sổ việc).
- **LC-T094-3** (chữ kế hoạch hiện bằng ô bảng, `st.text`, `escape_markdown`; không `unsafe_allow_html`, không `st.table`); đổi nhãn «Chờ duyệt trên website» (biên bản T-141 mục 8 dòng L).

## Tiêu chí xong

- [ ] Yêu cầu 1–8, có test.
- [ ] Test liên quan + test trang Kế hoạch, Bài viết có sẵn (T-101, T-113, T-127, T-137 phần trang Bài viết, `test_app_pages.py`) qua; `uv run ruff check .` sạch.
- [ ] Báo cáo `docs/team/reports/T-152-hoa-si.md`.

## Kiểm thử và kiểm định

- Soi Lỗi: Có (khóa nút, chữ Sheet, không gọi mạng khi mở trang).
- Lá Chắn: rút gọn.

## Lưu ý chung

- Chỉ chạy test trong worktree của phiếu (`D:/ProMetal-ToolSEO/wt-T-152`), **không** chạy trong `D:/ProMetal-ToolSEO/ProMetal-ToolSEO`.
- Không chạy toàn bộ `uv run pytest`: chạy test liên quan, test của mọi nơi gọi hàm sửa, `uv run ruff check .`.
- Tham số test lớn kèm `ids=` ngắn.
- Test không gọi AI, Cloudflare, Google, WordPress thật.
- Không đọc `.env`, không in hay commit khóa; `detect-secrets` (`PYTHONUTF8=1`, có file mồi) sạch.
- Đổi kỳ vọng test cũ: theo R5.

## Ghi chú của Chỉ Huy

- Lập 2026-11-19 từ thiết kế T-140/T-141 (phiếu L, mục 7 của `docs/team/reports/T-141-tho-may.md`; biên bản Lá Chắn `fb9d2ef`, `03568dc`). Worktree `wt-T-152`, nhánh `team/T-152`.

# T-149 · Lõi chạy tự động một bài (phiếu H)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-19 |
| Giai đoạn | Chế độ tự động (thiết kế T-141) |
| Mức ưu tiên | Cao |
| Phụ thuộc | **Đợt 3**: sau T-142, T-143, T-144, T-145, T-148 (T-153 qua T-145). Nếu Chỉ Huy chọn «lượt 1 không Cloudflare» (Lá Chắn chấp nhận, LC-T141-24): lượt 1 không cần T-142, chỗ ảnh AI để trống kèm prompt như hiện nay; lượt 2 cắm Cloudflare vào bước ảnh |
| Trạng thái | Mới |

## Mục tiêu

Gói `seo_app/auto/` chạy một bài từ từ khóa (hay từ dòng kế hoạch đã đọc lại) tới bước 5 · Xuất bản:

- trong **một luồng nền** của app;
- lưu nháp sau từng bước; dừng, chạy tiếp được; thử lại có trần;
- **không gửi, không đọc gì** từ website.

## Bối cảnh

- Thiết kế T-141: mục 1 (1.1–1.9: các bước, dàn ý tự duyệt, chỗ thiếu chất liệu thật, luật tự áp, SEO tự điền, ảnh, lưu sau từng bước, chỗ đặt mã), mục 2 (2.1–2.5: luồng nền, tiến độ, dừng, lỗi, hai tab, hai máy), 6.1, 7.2 dòng H; câu trả lời của chủ dự án 1A, 4A, 5A (mục 8).
- Thiết kế T-140: 1.7 (tự chọn khi nào chạy), 2.8 (đếm lượt).
- Biên bản Lá Chắn T-141 (`03568dc`): mục 4 (3), (4), mục 7, mục 8 dòng H. Hai yêu cầu sửa của Lá Chắn nằm ở phiếu này: **một lớp thử lại** (LC-T141-12) và **luồng daemon** (LC-T141-10).

## Yêu cầu

1. **Các bước** (`seo_app/auto/steps.py`): hàm thuần trên `DraftSnapshot`, không Streamlit, làm lại được, chạy tiếp từ bước chưa xong đầu tiên trên nội dung **hiện có** trong nháp.
   - **Nghiên cứu.**
   - **Dàn ý** + mã kiểm (T-141 1.3, LC-T141-6):
     - 3–8 mục, tiêu đề ≤ 120 ký tự, có ý, không trùng; ≤ 8 chỗ ảnh, mô tả ≤ 300 ký tự;
     - không link, email (`has_link`); số điện thoại, email (`personal_info`) thì che;
     - H1 không chứa «[cần bổ sung»;
     - không đạt: AI làm lại 1 lần.
   - **Viết:** lời dặn tự động của T-144, khuôn `AutoDraft`. `gaps` kiểm như 1.4: câu có thật trong phần, ≤ 10 mục, `clean_ai_text`, không vào bài (LC-T141-7).
   - **Rà soát, tự sửa** một lượt bằng `auto_fixable` (yêu cầu 3), rồi chấm lại.
   - **Quét bài sau bước viết** (LC-T141-8, bằng mã, không AI) → dấu vàng «câu cần xem lại», không khóa:
     - số điện thoại, email không có trong hồ sơ doanh nghiệp;
     - link, địa chỉ web trong thân (`has_link`);
     - giá khi chất liệu thật và ghi chú không có giá (`mentions_price`).
   - **SEO** (T-141 1.6):
     - meta: chọn bản đầu tiên không «Chặn», không trùng hệt bài đã đăng;
     - slug theo dòng kế hoạch hay `make_slug(từ khóa)`; từ khóa chính;
     - liên kết nội bộ **chỉ từ danh sách bài đã lưu trên máy** (không gọi website); thiếu link bắt buộc thì gọi lại 1 lần;
     - FAQ do mã dựng.
   - **Ảnh:** tự chọn (T-143) → chữ ảnh cả bài (`image_texts`, T-145) → Cloudflare (T-142), tối đa 8 ảnh mỗi bài, kiểm trần neuron trước từng ảnh, bọc qua `generated.py`. Mỗi chỗ tạo một lần mỗi lượt (`images_made`); chỗ đã có ảnh (tự chọn, đã tạo, bạn chọn, «Để trống chỗ này») không làm lại (LC-T141-20, LC-T140-14).
   - **Xong:** `step = 4`, `auto` ghi đã xong.
   - Bước ①–③ hỏng thì dừng bài; ④–⑥ hỏng thì bài vẫn tới bước cuối, phần thiếu thành dấu vàng (mã cố định trong `auto.notes`).
2. **Tiêu đề dự kiến (5A, LC-T141-6):** `title_hint` của dòng kế hoạch qua kiểm (`PlanRow`; ≤ 70 ký tự; có từ khóa chính so không dấu; `has_link` sai; `personal_info` = 0; qua `_neutralize`) thì làm H1 và vào lời dặn trong khung dữ liệu (T-144). Không qua thì không gửi, AI tự đặt, dấu vàng.
3. **`auto_fixable(flag, part)`** (`seo_app/content/workflow.py`), dùng cho **cả** đường soạn tay (`write_and_review` hiện áp mọi câu có thay thế mà không chốt nào) và đường tự động (LC-T141-5). 8 chốt:
   1. câu gốc có thật trong phần;
   2. câu thay ≤ 2 lần câu gốc;
   3. không thêm chữ số mới;
   4. không thêm link, email, số điện thoại;
   5. không cụm từ cấm;
   6. câu thay không chứa `[`, `]`, không thêm «[cần bổ sung»;
   7. một đoạn, không bắt đầu bằng `#`, `|`, `-`, `>`, không có `<`;
   8. `mentions_price(câu thay)` chỉ cấm khi câu gốc không có giá.

   Câu trượt chốt thành dấu vàng. Chạy test mọi nơi gọi `write_and_review`; đổi test cũ thì R5.
4. **Bộ dựng** (`seo_app/publish/render.py`, LC-T141-7): `find_missing` thấy «[cần bổ sung» trong tiêu đề, thân, alt, chú thích, tiêu đề SEO, mô tả SEO → dòng **Chặn** với Hẹn giờ, Đăng ngay; Nháp: Cảnh báo. Áp cho cả bài soạn tay.
5. **Luồng nền** (`seo_app/auto/runner.py`; LC-T141-9, **LC-T141-10**):
   - **Luồng:**
     - một luồng làm việc **daemon** (`threading.Thread(daemon=True)` + hàng đợi), **không** `ThreadPoolExecutor` (chờ worker lúc thoát, có thể treo app tới 15 phút);
     - client tạo trong luồng, bỏ khi xong; `seo_app/auto/` không import `streamlit`, không `add_script_run_ctx`.
   - **Sổ việc:**
     - một đối tượng có `threading.Lock`, giữ bằng `st.cache_resource` ở trang (T-150);
     - chỉ giữ mã nháp, Mã bài (đã `parse_key`), tên bước, giờ, số đếm, cờ dừng, mã lý do;
     - **không** giữ `AIRouter`, client, khóa, prompt, chữ AI, chữ Sheet.
   - **Dừng và mở lại:**
     - cờ dừng kiểm **trước mỗi lần gọi AI và mỗi lần ghi nháp**; mỗi lần ghi là một giao dịch SQLite;
     - mở lại app **không tự chạy**; nháp có `auto` chưa xong mà không có trong sổ việc là «Dừng giữa chừng (app đã tắt)».
6. **Một lớp thử lại** (**LC-T141-12**), cũng dùng LC-T141-13:
   - `registry.py`: `AIRouter(..., single_attempt=True)` tạo provider bằng tùy chọn không tự thử lại của T-148; lượt chạy chỉ dùng router này;
   - runner thử lại theo bảng T-141 2.4, trần 2 lần mỗi bước, 6 lần mỗi bài; `retry_after` ≤ 120 giây;
   - lô dừng khi 2 bài liền dừng vì `rate` hay `busy` (tín hiệu cho T-151);
   - kho đếm (T-143) ghi **mỗi request trước khi gửi**, kể cả lỗi: Gemini theo ngày Thái Bình Dương (T-148), neuron Cloudflare theo ngày UTC;
   - giãn nhịp theo `[auto]` (T-148).
7. **Lưu nháp** (LC-T141-11):
   - mỗi lần ghi của lượt chạy dùng `save(expected_saved_at=lần lưu trước)` (T-145); lệch thì dừng `conflict`, không ghi đè, không thử lại;
   - tự lưu của trang (`autosave` trong `write.py`) cũng truyền `expected_saved_at`; lệch thì báo «Nháp vừa được cập nhật ở nơi khác: mở lại».
8. **Không ghi duyệt** (LC-T141-4): lượt chạy không bao giờ ghi `alt_approved=True` hay `approved_sha256`. Sau lượt chạy, mọi ảnh có `alt_approved=False`.
9. **Dời phần thuần của kế hoạch** sang `seo_app/auto/plan_start.py`:
   - phần không dùng `st.session_state` của `start_from_plan`, `fill_from_plan` (che bằng `mask_personal_info`, mã nhắc giá), `plan_details`;
   - `write.py` gọi lại, giữ đúng hành vi (test T-101, T-102, T-103 không đổi).
10. **«Ghi SEO» mặc định của bài tự động** (LC-T141-17): lượt chạy tạo nháp với `auto.seo_write = True`. Bài soạn tay không có `auto` nên giữ mặc định tắt. Giao diện ở T-150.
11. **Test** (LC-T141-21):
    - cả lượt chạy với AI giả, Cloudflare giả, Sheets giả dưới bộ chặn mạng: **0 request WordPress, 0 kết nối ra ngoài**;
    - nháp của lượt chạy mở bằng AppTest ra đúng như soạn tay: dàn ý chưa escape, chữ bài đã escape, ảnh, SEO;
    - dừng giữa chừng, F5, hai tab (sổ việc dùng chung), tắt app (luồng là daemon); trần thử lại; `conflict`;
    - test quét mã: `seo_app/auto/` không import `streamlit`; chạy một bước trong `threading.Thread` thường không lỗi `NoSessionContext`;
    - không ảnh nào `alt_approved`; tiêu đề dự kiến qua và không qua kiểm.

## Phạm vi

- **Được sửa:**
  - `seo_app/auto/` (mới: `__init__.py`, `steps.py`, `runner.py`, `compose.py`, `plan_start.py`);
  - `seo_app/content/workflow.py` (`write(auto=True)`, `auto_fixable`, `write_and_review` dùng chốt);
  - `seo_app/publish/render.py` (dòng Chặn «[cần bổ sung»);
  - `seo_app/ai/registry.py` (tùy chọn `single_attempt`);
  - `app/views/write.py`: chỉ chỗ gọi hàm dời sang `plan_start.py` và `autosave` so giờ lưu;
  - test mới `tests/test_t149_*.py`.
- **Không được sửa:** giao diện mới của Soạn bài (T-150), `seo_app/storage/drafts.py` (T-145 đã làm), `seo_app/content/prompts.py` (Ngòi Bút), `config/**`, client WordPress, `seo_app/plan/sync.py` (chỉ gọi hàm có sẵn).
- **Ngoài phạm vi:** «Viết các bài tới hạn» (T-151), khung tiến độ, màn hình duyệt cuối (T-150).

## Yêu cầu bảo mật riêng (điều kiện Lá Chắn)

A1, A2, A3, W1, W2 (lượt chạy không có lệnh WordPress nào), F3, D3.

- **LC-T141-4** (lượt chạy không duyệt), **-5** (8 chốt, một hàm cho cả hai đường), **-6** (dàn ý mã kiểm, tiêu đề dự kiến), **-7** («[cần bổ sung» Chặn ở bộ dựng; `gaps` kiểm, không vào bài), **-8** (quét bài sau bước viết), **-9** (luồng nền không `st.*`, sổ việc có khóa, chỉ giữ dữ liệu cho phép), **-10** (luồng daemon, cờ dừng trước mỗi lần gọi và mỗi lần ghi, mở lại không tự chạy), **-11** (lưu có so giờ lưu, lệch thì dừng), **-12** (một lớp thử lại, đếm mỗi request trước khi gửi), **-20** (mỗi chỗ ảnh một lần tạo mỗi lượt, «Chạy tiếp» không tạo lại ảnh đã có, không đè ảnh tay và «Để trống chỗ này»), **-21** (test bắt buộc ở yêu cầu 11).
- **LC-T140-14** (C9 sửa: chỉ tạo ảnh trong lượt chạy người dùng đã bấm; không khi mở trang, mở nháp, chạy lại trang; ≤ 8 ảnh mỗi bài, kiểm trần trước từng ảnh; dừng ở lỗi đầu tiên 3036, 401, 403, 5xx).
- **LC-T094-35** (lượt chạy không gửi, không hẹn, không đăng; không gọi website).

## Tiêu chí xong

- [ ] Yêu cầu 1–11, có test.
- [ ] Test liên quan + test **mọi nơi gọi** `workflow.py` (`write_and_review`), `render.py` (bộ dựng, bước Xuất bản T-102, T-112), `registry.py`, các hàm dời khỏi `write.py` (T-101, T-102, T-103) và `tests/test_app_pages.py` qua; `uv run ruff check .` sạch.
- [ ] Báo cáo `docs/team/reports/T-149-tho-may.md`.

## Kiểm thử và kiểm định

- Soi Lỗi: **đầy đủ** (dừng, F5, hai tab, tắt app giữa chừng, thử lại, `conflict`).
- Lá Chắn: **đầy đủ**.

## Lưu ý chung

- Chỉ chạy test trong worktree của phiếu (`D:/ProMetal-ToolSEO/wt-T-149`), **không** chạy trong `D:/ProMetal-ToolSEO/ProMetal-ToolSEO`.
- Không chạy toàn bộ `uv run pytest`: chạy test liên quan, test của mọi nơi gọi hàm sửa, `uv run ruff check .`.
- Tham số test lớn kèm `ids=` ngắn.
- Test không gọi AI, Cloudflare, Google, WordPress thật. Lần gọi thử Cloudflare thật chỉ ở buổi thử cùng chủ dự án.
- Không đọc `.env`, không in hay commit khóa; `detect-secrets` (`PYTHONUTF8=1`, có file mồi) sạch.
- Đổi kỳ vọng test cũ: theo R5.

## Ghi chú của Chỉ Huy

- Lập 2026-11-19 từ thiết kế T-140/T-141 (phiếu H, mục 7 của `docs/team/reports/T-141-tho-may.md`; biên bản Lá Chắn `fb9d2ef`, `03568dc`). Worktree `wt-T-149`, nhánh `team/T-149`.

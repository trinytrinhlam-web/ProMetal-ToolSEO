# T-145 · Việc AI chữ ảnh cả bài, khuôn prompt ảnh, khuôn nháp 4 (phiếu D)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-19 |
| Giai đoạn | Chế độ tự động (thiết kế T-141) và ảnh AI (thiết kế T-140) |
| Mức ưu tiên | Cao |
| Phụ thuộc | **Đợt 2**: sau T-144 (lời dặn, `gaps`) và T-153 (chữ khuôn prompt ảnh). Làm từ `main` đã gộp đợt 1 |
| Trạng thái | Mới |

## Mục tiêu

- **Một lần gọi AI viết chữ ảnh cho mọi chỗ cần ảnh của bài:** khuôn prompt có cấu trúc, dòng tóm tắt tiếng Việt, alt, chú thích.
- **Mã ghép và kiểm prompt gửi FLUX** trong ngân sách độ dài của mô hình.
- **Khuôn nháp 4:** trường ảnh AI của T-140, trạng thái lượt chạy tự động của T-141, lưu nháp có so giờ lưu. Nâng khuôn một lần cho cả hai thiết kế.

## Bối cảnh

- Thiết kế T-141: 1.7 (chữ ảnh cả bài một lần gọi), 1.8 (khuôn nháp 4, `auto`), 1.10 (khuôn prompt chi tiết, ngân sách 900 ký tự), 7.1 dòng D.
- Thiết kế T-140: 2.7 (trường ảnh AI trong nháp), 3.1–3.5 (prompt ảnh).
- Biên bản Lá Chắn T-140 (`fb9d2ef`): LC-T140-9, -10, -13, -20. Biên bản Lá Chắn T-141 (`03568dc`): mục 6, mục 8 dòng D.
- Chữ của khuôn (kiểu ảnh, mệnh đề an toàn đầu, đuôi an toàn, chữ của các danh sách chọn, luật từng trường): báo cáo T-153 của Ngòi Bút.

## Yêu cầu

1. **Khuôn (`seo_app/content/models.py`):**
   - `Gap` (số phần, câu, cần bổ sung gì);
   - `AutoDraft`: như `Draft`, thêm `gaps` **bắt buộc**, không giá trị mặc định (khuôn strict của OpenAI đòi đủ mọi trường). `Draft` của đường soạn tay không đổi;
   - `ImagePromptSpec`: thành phần 5 (vị trí), 6 (người), 8 (góc máy, cỡ cảnh), 9 (ống kính), 10 (ánh sáng), 11 (bố cục) là `Literal` theo chữ của T-153. Trường tự do có trần: vật chính 80, chất liệu-màu 60, tình trạng 80, chi tiết phụ tối đa 3 mục × 40, bối cảnh 60, màu chủ đạo 30;
   - `ImageText(slot, prompt: ImagePromptSpec | None, summary_vi, alt_vi, caption_vi)`, `ImageTexts(items)`.
2. **`seo_app/images/prompt.py` (mới):**
   - hằng do T-153 viết: kiểu ảnh (thành phần 1), mệnh đề an toàn ngắn ≤ 60 ký tự ngay sau thành phần 1, đuôi an toàn ≤ 200 ký tự ở cuối;
   - ghép theo thứ tự cố định 1 → 12 rồi đuôi, ý chính lên đầu;
   - **kiểm từng trường tự do rồi kiểm chuỗi ghép cuối** (LC-T140-9):
     - một dòng; chỉ ký tự in được, không ký tự điều khiển, vô hình, đảo hướng;
     - không chữ số; không link, email, số điện thoại (`has_link`, `personal_info`);
     - không «Pro-Metal», tên miền website, tên quận huyện (`AREAS`, so không dấu);
     - không từ cấm `text, caption, watermark, logo, banner, label, lettering, typography, phone, website, address, brand` (so cả từ, không phân biệt hoa thường);
   - ngân sách (LC-T141-18): phần AI viết hay người dùng sửa ≤ 600 ký tự, đuôi ≤ 200, **cả prompt ≤ 900**;
   - không đạt thì không gửi, báo «Viết lại prompt», không sửa ngầm; prompt người dùng sửa tay: kiểm lại cả chuỗi;
   - `summary_vi` ≤ 140 ký tự, lọc như alt (không link, số điện thoại), không bao giờ gửi Cloudflare;
   - mục `[image_prompt]` của `config/content.toml` đọc chịu lỗi và **chỉ bổ sung**; phần bảo vệ nằm trong mã (như `ALT_SYSTEM`, C2 của T-051);
   - lời dặn hệ thống của việc chữ ảnh dựng ở module này từ chữ T-153.
3. **`ContentWriter.image_texts(slots)`** (`seo_app/content/workflow.py`), một lần gọi việc `image_prompt` cho cả bài (LC-T141-19):
   - **đầu vào** mỗi chỗ chỉ là mô tả ảnh, tiêu đề mục, mặt thẻ (giá trị danh sách cố định của `text_facets`); mỗi chỗ bọc `_block` riêng kèm số chỗ; không tên thư mục, tên file, chữ của khách (LC-T140-10);
   - **kết quả:**
     - số chỗ phải khớp; mục lạ hay trùng: bỏ;
     - chỗ ảnh AI: ghép và kiểm prompt (yêu cầu 2); chỗ ảnh thật: chỉ alt và chú thích viết từ chữ, **không gửi ảnh** (chủ dự án chọn 1A);
     - `alt_vi` qua `clean_alt_text(ai_generated=…)`; ảnh AI: alt «Minh họa…», chú thích «Ảnh minh họa (AI)…» do mã bảo đảm (LC-T140-13);
   - `TokenLimitError` hay sai khuôn: chỉ chỗ đó (hay các chỗ của lần gọi) trống kèm mã lý do; không dừng bài;
   - nhãn tiếng Việt của việc `image_prompt` trong `TASK_LABELS` (thử mù không gợi ý việc này).
4. **`DraftImage` khuôn 4** (LC-T140-20):
   - trường mới kiểm chặt: `generated_sha256` (64 hex), `generator` (hằng `cloudflare-flux-1-schnell`), `steps` 1–8 (loại `bool`), `history` ≤ 3 mục (băm + prompt ≤ 2048);
   - ảnh AI không bao giờ có mã công trình, khu vực, giai đoạn (LC-T140-13);
   - nháp cũ đọc như cũ; mất ảnh trên máy thì chỗ đó về trống và báo, không tự tạo lại.
5. **`DraftSnapshot.auto: AutoState | None`** (T-141 1.8):
   - `origin` (`keyword` | `plan`); `done` (tên bước cố định); `stop` (mã lý do cố định, không chữ tự do); `attempts` 0–20; `images_made` 0–8; `notes` (mã dấu vàng cố định); `gaps`;
   - `seo_write: bool`, mặc định `True` khi lượt chạy tạo nháp (LC-T141-17). Trường nằm trong `auto` để **không đụng khối SEO** của `drafts.py`;
   - `started_at`, `updated_at` có múi giờ;
   - không lưu chữ «đang chạy»: trạng thái chạy chỉ ở sổ việc trong bộ nhớ (T-149).
6. **`DraftStore.save(snapshot, *, must_exist=False, expected_saved_at=None)`** (LC-T141-11):
   - so giờ lưu trong **cùng giao dịch** `BEGIN IMMEDIATE` với `must_exist`;
   - lệch thì lỗi riêng (lớp con của `DraftError`), không ghi, không thử lại;
   - nâng `SCHEMA_VERSION` lên 4 (khuôn 3 vào `_OLD_SCHEMA_VERSIONS`). Ngoài ra không đụng gì khác ở `drafts.py`.
7. **Không ghi duyệt** (LC-T141-4): không hàm nào của phiếu ghi `alt_approved=True` hay `approved_sha256`.
8. **Test:**
   - khuôn 4: đọc ghi đủ trường; nháp khuôn 2, 3 mở được; trường sai (hex sai, `steps` 0, 9, `True`, `history` > 3, mã dừng lạ, giờ không múi giờ) bị từ chối; ảnh AI không mang mã công trình;
   - `save` so giờ lưu: khớp, lệch, nháp đã xóa, hai kết nối như hai tab;
   - ghép prompt: thứ tự, mệnh đề đầu, ngân sách, từng ca bị chặn (chữ số, từ cấm, tên quận có dấu và không dấu, link, email, số điện thoại, ký tự vô hình, đảo hướng), đường sửa tay;
   - `image_texts` với AI giả: số chỗ lệch, trùng, lạ, `TokenLimitError` → chỗ trống, không dừng; AI giả không bao giờ nhận ảnh.

## Phạm vi

- **Được sửa:** `seo_app/content/models.py`, `seo_app/content/workflow.py` (thêm `image_texts`, không đổi việc khác), `seo_app/images/prompt.py` (mới), `seo_app/storage/drafts.py` (chỉ: trường ảnh AI của `DraftImage`, `DraftSnapshot.auto`, `save(expected_saved_at)`, số khuôn), `seo_app/content/blind_test.py` (chỉ `TASK_LABELS`), test mới `tests/test_t145_*.py`.
- **Không được sửa:** phần mở kho, trạng thái gửi, `DraftSeo`, phần kế hoạch của `drafts.py` (T-130, T-136); `seo_app/content/prompts.py` (Ngòi Bút); `config/**`; `app/**`.
- **Ngoài phạm vi:** gọi `image_texts` trong lượt chạy, tạo ảnh (T-149); giao diện sửa prompt (T-150).

## Yêu cầu bảo mật riêng (điều kiện Lá Chắn)

A1, A2, F3. Nháp đọc từ file là dữ liệu chưa tin cậy: khuôn kiểm chặt.

- **LC-T140-9** (prompt cuối qua bộ kiểm trong mã trước khi gửi; không qua thì không gửi; đuôi an toàn trong mã, `config/` chỉ bổ sung), **LC-T140-10** (việc chữ ảnh: đầu vào chỉ mô tả, tiêu đề mục, mặt thẻ; dữ liệu bọc `_block`; khuôn kiểm chặt; alt qua `clean_alt_text(ai_generated=True)`; không gửi ảnh với ảnh AI), **LC-T140-13** (phần khuôn: ảnh AI không có mã công trình, khu vực, giai đoạn), **LC-T140-20** (khuôn nháp 4 kiểm chặt, nháp cũ đọc như cũ, không đụng phần mở kho, trạng thái gửi, khối SEO).
- **LC-T141-4** (không ghi duyệt), **LC-T141-11** (`save(expected_saved_at)` so trong cùng giao dịch, lệch thì dừng, không thử lại), **LC-T141-18** (khuôn `Literal` cho thành phần 5, 6, 8, 9, 10, 11; kiểm từng trường rồi chuỗi ghép; ≤ 900 / ≤ 600 / đuôi ≤ 200; mệnh đề an toàn ≤ 60 ký tự sau thành phần 1; `summary_vi` ≤ 140, không gửi Cloudflare; sửa tay kiểm lại cả chuỗi), **LC-T141-19** (một lần gọi cả bài: mỗi chỗ `_block` riêng kèm số chỗ, số chỗ phải khớp, mục lạ hay trùng bỏ, `TokenLimitError` hay sai khuôn chỉ làm trống chỗ ảnh, không gửi ảnh), **LC-T141-17** (phần khuôn: `seo_write` lưu trong nháp tự động).

## Tiêu chí xong

- [ ] Yêu cầu 1–8, có test.
- [ ] Test liên quan + test **mọi nơi gọi** `drafts.py` (kho nháp, gửi nháp, T-086, T-089, T-092, T-130, T-136, T-137, `test_app_pages.py`) và `workflow.py`, `models.py` qua; `uv run ruff check .` sạch.
- [ ] Báo cáo `docs/team/reports/T-145-tho-may.md`.

## Kiểm thử và kiểm định

- Soi Lỗi: Có (khuôn 4 với nháp cũ, so giờ lưu, bộ kiểm prompt).
- Lá Chắn: **đầy đủ** (đụng `save` của kho nháp).

## Lưu ý chung

- Chỉ chạy test trong worktree của phiếu (`D:/ProMetal-ToolSEO/wt-T-145`), **không** chạy trong `D:/ProMetal-ToolSEO/ProMetal-ToolSEO`.
- Không chạy toàn bộ `uv run pytest`: chạy test liên quan, test của mọi nơi gọi hàm sửa, `uv run ruff check .`.
- Tham số test lớn kèm `ids=` ngắn.
- Test không gọi AI, Cloudflare, Google, WordPress thật.
- Không đọc `.env`, không in hay commit khóa; `detect-secrets` (`PYTHONUTF8=1`, có file mồi) sạch.
- Đổi kỳ vọng test cũ: theo R5.

## Ghi chú của Chỉ Huy

- Lập 2026-11-19 từ thiết kế T-140/T-141 (phiếu D, mục 7 của `docs/team/reports/T-141-tho-may.md`; biên bản Lá Chắn `fb9d2ef`, `03568dc`). Worktree `wt-T-145`, nhánh `team/T-145`.

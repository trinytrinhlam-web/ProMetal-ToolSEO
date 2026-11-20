# T-138 · Tạm dùng Gemini Flash cho mọi việc AI: cấu hình, test ghim cấu hình, bước nghiên cứu không tìm web

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-18 |
| Giai đoạn | Chung (cấu hình AI) |
| Mức ưu tiên | Cao (chủ dự án cần dùng app ngay) |
| Phụ thuộc | `main` `0c5d476` (đã gộp T-136) |
| Trạng thái | Xong (gộp `main` 2026-11-20) |

## Bối cảnh

- Chủ dự án 2026-11-18: «chuyển sang dùng Gemini thời gian này», chọn **«Tạm dùng Flash miễn phí»**. Máy chưa có khóa Claude; khóa Gemini ở gói miễn phí.
- Chỉ Huy B đã thử thật bằng `GeminiProvider` của app (lời gọi rất ngắn, không in khóa):
  - `gemini-3-pro` (tên cũ trong ghi chú `config/ai.toml`): «Không có mô hình»; `gemini-2.5-pro` cũng vậy;
  - `gemini-3.1-pro-preview`, `gemini-pro-latest`: «hết tiền hoặc hết hạn mức»;
  - `gemini-3.8-flash`: trả lời được khi **không** tìm web (effort low, high); có tìm web thì «hết hạn mức»; có lúc 503 (quá tải).
- Cấu hình đã đổi tạm trên máy chủ dự án (chưa commit): 9 việc (research, outline, write, rewrite, review, meta, links, plan, alt) `provider = "gemini"`, `model = "gemini-3.8-flash"`; `[tasks.research]` `web_search = false`. Lấy nội dung này làm bản cấu hình của phiếu (Chỉ Huy chép sang nhánh).
- Với cấu hình mới, 14 test hỏng vì ghim cấu hình Claude đã commit (`test_settings_blind`, `test_soi_loi_t051` ×7, `test_soi_loi_t062` ×3, `test_t062_image_config` ×2, `test_app_pages::test_without_api_key_ai_buttons_are_locked`).

## Yêu cầu

1. Commit `config/ai.toml` như trên (giữ ghi chú cách quay lại Claude; sửa ví dụ tên mô hình Gemini trong phần chú thích đầu file cho đúng tên còn dùng được, ví dụ `gemini-3.8-flash`, `gemini-3.1-pro-preview`).
2. **Test ghim cấu hình:** sửa 14 test để kiểm **điều bảo vệ** (trang Soạn bài chỉ đòi khóa của hãng đang được cấu hình; việc ảnh bật thì chỉ đòi khóa Gemini khi gọi; hỏng `config/*.toml` thì trang vẫn chạy…) mà không phụ thuộc hãng cụ thể trong file cấu hình đã commit: đọc hãng từ cấu hình, hoặc dùng file cấu hình mẫu trong `tmp_path`. Ca nào ghim **quyết định của chủ dự án** (ví dụ alt dùng Claude Sonnet, 4A) thì đổi thành ghim cấu hình hiện tại kèm chú thích «chủ dự án 18/11 tạm Gemini». R5: ghi bảng «Đổi kỳ vọng ca test cũ» trong báo cáo, từng ca: cũ / mới / vì sao.
3. **Bước nghiên cứu khi tắt tìm web:** AI không đọc được trang nào nên không được có danh sách bài đối thủ bịa ra.
   - Lời dặn (`seo_app/content/prompts.research_prompt`) khi `web_search` tắt: nói rõ không tìm web, chỉ nêu ý định tìm kiếm, góc mới, câu hỏi từ hiểu biết chung; **để trống** danh sách bài đối thủ.
   - Code: `web_search` tắt thì bỏ mọi `competitors` AI trả về (không tin lời dặn).
   - Trang Soạn bài bước 1: một dòng nhắc «Đang tắt tìm Google: AI không đọc bài đối thủ» khi việc research tắt tìm web.
4. Test cho yêu cầu 3 (bật/tắt `web_search`, AI vẫn trả đối thủ khi tắt → bị bỏ). Test mọi nơi gọi `research_prompt`, `clean_research`; test trang (`test_app_pages`, `test_soi_loi_t084`, `test_t101_settings_google`). Tham số lớn kèm `ids=` ngắn.
5. README: một đoạn ngắn «Đang dùng Gemini Flash miễn phí» (giới hạn: có lúc báo bận 503, không tìm Google; cách quay lại Claude hay bật thanh toán Gemini để dùng Pro).

## Phạm vi

- **Được sửa:** `config/ai.toml`, `seo_app/content/prompts.py`, `seo_app/content/workflow.py` (chỉ phần research), trang Soạn bài bước 1 (một dòng nhắc), README, test.
- **Không được sửa:** lớp provider, khóa, `.env`.

## Kiểm thử và kiểm định

- Soi Lỗi: rút gọn. Lá Chắn: rút gọn (đổi kỳ vọng test ghim điều kiện bảo mật cũ: Lá Chắn phải xem bảng R5).

## Ghi chú của Chỉ Huy

- Lập 2026-11-18 theo quyết định của chủ dự án. Worktree `wt-T-138`, nhánh `team/T-138` từ `main`.
- 2026-11-20 16:15 (Chỉ Huy B): Thợ Máy lượt 1 (7bbe500, 6309116, 2bdee5f, d82ad6d), lượt 2 (8203c06, df517a3); Soi Lỗi rút gọn c1b6674 ĐẠT CÓ ĐIỀU KIỆN; Lá Chắn rút gọn (Fable) f2014f4 ĐẠT CÓ ĐIỀU KIỆN. Gộp cùng T-137; Windows 24.516 qua, 0 hỏng; `main` `f6ec79b`. B.2 (PREVIEW_CACHE_DIR) làm ở T-143; B.1, B.3 phiếu sau.

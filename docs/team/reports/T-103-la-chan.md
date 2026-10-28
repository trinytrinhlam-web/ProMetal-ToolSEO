# Biên bản bảo mật T-103 · Lời dặn AI đọc kế hoạch, `[tasks.plan]`, `[plan]`

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-103](../tickets/T-103-loi-dan-ai-doc-ke-hoach.md) (Ngòi Bút `f61012a`, Soi Lỗi `fdb47c2`, gốc `main` `24013b3`) · điều kiện [Lá Chắn T-094](T-094-la-chan.md): chung LC-T094-1, -2, -3; riêng LC-T094-42; liên quan LC-T094-19, -20, -21 |
| Phạm vi | **Rút gọn** (dữ liệu chưa tin cậy, lời dặn AI, cấu hình). Diff `24013b3..fdb47c2`: `seo_app/content/prompts.py` (+80/−20: chữ `DATA_RULES`, `plan_prompt`), `config/ai.toml` (+13/−2: `[tasks.plan]`), `config/content.toml` (+22: `[plan]`), `seo_app/content/blind_test.py` (+1: nhãn `plan`, ngoài danh sách file, Chỉ Huy đã nhận); test `tests/test_t103_plan_prompt.py` (19), `tests/test_soi_loi_t103.py` (13). Đọc thêm: `_plan_line`, `_block`, `_neutralize`, `system_prompt` (`prompts.py`); `plan_changes`, `_plan_task` (`workflow.py`); `load_ai_config`, `AIRouter` (`seo_app/ai/registry.py`); 3 provider (công cụ AI được gắn); `from_ai`, `preselected` (`seo_app/plan/propose.py`); `mentions_price` (`seo_app/onpage/meta.py`); bộ đọc `config/content.toml` (`rules.py`); thiết kế T-094 mục 1.6 (dòng kế hoạch → Soạn bài). Thử gộp với `main` trên máy `b241e79` |
| Ngày | 2026-10-28 (22:45–23:05 +07, giờ máy) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (LC-T103-1, nâng từ góp ý G2 của Soi Lỗi; lỗi nằm ở code T-098, không do T-103 tạo ra). Lời dặn, cấu hình mới của T-103 không có lỗi bảo mật. **Không lỗi nào bắt buộc sửa trước khi gộp T-103**; LC-T103-1 sửa trước khi T-101 nối đề xuất AI vào trang Kế hoạch (điều kiện 1). Gộp `main` được: không xung đột, 42 file test liên quan qua trên cây gộp |

## Tóm tắt (cho chủ dự án)

Lời dặn mới để AI đọc ghi chú kế hoạch **an toàn để gộp**. Tôi gài lệnh giả, thẻ giả, ký tự vô hình vào chữ dán và vào từ khóa kế hoạch: phần lời dặn của phần mềm không đổi một chữ, chữ độc luôn nằm trong khung «dữ liệu». Ghi chú của thợ, tiêu đề dự kiến, từ khóa phụ của kế hoạch đang có **không bao giờ** được gửi cho AI, nên lệnh giấu ở đó không tới được AI. Việc đọc kế hoạch không bao giờ tìm web, kể cả khi file cấu hình ghi bật, với cả 3 hãng AI. Cấu hình mới không có khóa, không làm đổi các việc AI khác (viết bài, meta, alt…).

Một lỗi nhỏ (Thấp) có từ phiếu trước: lời dặn cấm AI bịa giá, nhưng phần mềm chưa kiểm. Nếu AI vẫn ghi «giá 150.000đ» vào ghi chú hay tiêu đề dự kiến, đề xuất đó vẫn được tick sẵn, không cảnh báo. Ghi chú này về sau thành «Kinh nghiệm của xưởng» khi viết bài, nên cần một cảnh báo như cảnh báo số điện thoại đang có. Lỗi này không chặn việc gộp; cần sửa trước khi trang Kế hoạch dùng được đề xuất của AI.

## Lỗi phát hiện

### LC-T103-1 · Chữ AI đề xuất có giá vẫn được tick sẵn, không cảnh báo

| Mục | Nội dung |
|---|---|
| Mức | **Thấp** (cần người dùng duyệt đề xuất rồi duyệt bài mới thành hại; chưa khai thác được) |
| Nguồn | Góp ý G2 của Soi Lỗi, Lá Chắn nâng thành lỗi. Code của T-098 (`seo_app/plan/propose.py`, `from_ai`), không do T-103 tạo ra |
| Chỗ | `propose.from_ai` (`:296`): có cảnh báo `WARN_PERSONAL` (số điện thoại, email) cho chữ AI, **không** có kiểm giá. `Proposal.preselected` (`:130`): mục không cảnh báo thì tick sẵn |
| Tái hiện | AI giả trả «cap_nhat» B-001 với ghi chú «Giá thay bản lề 150.000đ, rẻ nhất quận», hay tiêu đề dự kiến «Bảng giá sửa bản lề…», hay «them» với từ khóa phụ «sửa cửa kéo 500k», ghi chú «Sửa trọn gói 2 triệu»: cả 5 ca qua bộ kiểm, `warnings == ()`, **tick sẵn**. `tests/test_la_chan_t103.py::test_lc_t103_1_price_in_ai_text_warns_and_is_not_preselected` (5 ca, `xfail(strict=True)`, hỏng đúng ở `assert proposal.warnings`) |
| Vì sao là rủi ro | security.md 2.4: kết quả AI là dữ liệu chưa tin cậy, kiểm rồi mới dùng. Chữ dán (nguồn ngoài, có thể chép từ tin nhắn, trang khác) dụ được AI, hay AI tự bịa. Theo thiết kế T-094 mục 1.6, «Ghi chú của thợ» điền vào «Kinh nghiệm của xưởng» (chất liệu thật) ở Soạn bài, nơi `DATA_RULES` nói số liệu lấy từ `<chat_lieu_that>` là thật: giá AI bịa thành «số liệu thật» của bài. Pro-Metal không công bố giá (hồ sơ doanh nghiệp, quy tắc meta T-040). Lời dặn T-103 đã cấm (`test_prompt_forbids_made_up_numbers_prices_and_personal_info`) nhưng chỉ lời dặn thì không đủ |
| Cách sửa gợi ý | Như `WARN_PERSONAL`: thêm câu cảnh báo cố định (vì có cảnh báo nên không tick sẵn) khi chữ **AI đổi** (từ khóa, từ khóa phụ, tiêu đề dự kiến, ghi chú) có giá, dò bằng `mentions_price` của `seo_app/onpage/meta.py` (đã gia cố ở T-036, T-040, T-041; không tính chỗ nằm trong từ khóa). Chỉ xét chữ AI đổi như SL-T098-15: giá có sẵn trong ghi chú cũ mà AI không đụng tới thì không cảnh báo (`test_old_price_in_notes_that_ai_did_not_change_gives_no_price_warning`, đang qua, phải giữ). Gỡ `xfail` khi XPASS (R5) |
| Ai sửa, hạn | Thợ Máy (Chỉ Huy đã định giao G2 ở phiếu sau). Trước khi T-101 nối đề xuất AI vào trang Kế hoạch; chậm nhất trước khi T-102 điền ghi chú vào «Kinh nghiệm của xưởng» |

## Đối chiếu điều kiện Lá Chắn T-094

| Mã | Đạt? | Bằng chứng |
|---|---|---|
| **LC-T094-1** Test không gọi Google, WordPress, AI thật | **Đạt** | Test mới dùng AI giả (`make_provider` giả) hoặc lớp provider thật với client giả; `test_soi_loi_t103.py` chỉ nhập `google.genai.types` để dựng câu trả lời giả. Không test nào nhập `requests`, `socket`, `urllib`, `http.client`; bộ chặn mạng `autouse` của `tests/conftest.py` vẫn bật. Test Lá Chắn chỉ dựng lời dặn và gọi `from_ai` |
| **LC-T094-2** Câu báo cố định | **Đạt** | Phiếu không thêm câu báo nào. Câu báo khi lời đáp của việc `plan` bị cắt (`TokenLimitError`, `_schema_error`) là câu có sẵn, cố định, chỉ có số token và tên việc |
| **LC-T094-3** Chữ thuần trên giao diện | **Đạt** (phần T-103) | Không đổi giao diện. Lời dặn cấm AI ghi địa chỉ web, link, HTML, Markdown vào mọi trường, và dặn viết lý do bằng lời của AI. Hiện chữ thuần vẫn là việc của T-101 (LC-T094-32) |
| **LC-T094-42** Giữ khung, `DATA_RULES` | **Đạt** | So cây cú pháp (Ngòi Bút, Soi Lỗi): `_block`, `DATA_TAGS`, `_neutralize`, `_plan_line` không đổi. `DATA_RULES` giữ mọi câu, nêu thêm `<de_bai>`, `<danh_sach_bai>`, `<ke_hoach_hien_tai>`, `<ke_hoach_moi>` (điều kiện 4 của biên bản T-098, góp ý G6); lời dặn hệ thống của `ContentWriter` có đủ 2 khung kế hoạch (script dưới) |
| LC-T094-42 Không xin URL, HTML, link Markdown | **Đạt** | Phần chỉ thị (ngoài 2 khung) 5.774 ký tự: 0 chỗ `http`, `www.`, `href`, `](`, `<a`, `src=`, `.vn`, `.com`, `url`, `slug`. Mọi dòng nhắc «link», «web», «địa chỉ» là câu cấm hay tả kế hoạch của website. Khuôn `PlanSuggestion` không có trường địa chỉ, slug, trang đích |
| LC-T094-42 `[tasks.plan]` không `web_search` | **Đạt** | Mục không có khóa `web_search`; chú thích nói phần mềm luôn tắt. Thử độc lập: bản sao cấu hình ghi `web_search = true` với `anthropic`, `openai`, `gemini`, và khi thiếu `[tasks.plan]` (dùng tạm `outline` bật tìm web): `_plan_task` luôn trả `web_search=False` (4/4). Công cụ duy nhất 3 provider gắn vào lệnh gửi là tìm web, chỉ khi `task.web_search` (`anthropic_provider.py:94`, `openai_provider.py:120`, `gemini_provider.py:218-221`) |
| LC-T094-42 `[plan]` chỉ bổ sung, code kiểm | **Đạt hôm nay; phần «code kiểm» chuyển T-102** | Hôm nay không bộ đọc nào đọc `[plan]` (`grep`): 4 bộ đọc `content.toml` (`load_rules`, `load_image_settings`, `load_alt_rules`, `load_meta_rules`) cho kết quả y hệt bản gốc. Nhãn chỉ nằm trong chú thích. Khi T-102 đọc `default_time`: điều kiện 2 |
| LC-T094-19 (liên quan) SL-7, khung, không tìm web | **Đạt** | Chạy lại script A1 của biên bản T-098 trên lời dặn mới: 81 mảnh độc × 6 lời dặn = 486, **0 vi phạm**; đối chứng tắt `_neutralize` 782, `_keyword` không đổi «» 405 (script vẫn bắt lỗi) |
| LC-T094-20 (liên quan) Kết quả AI chưa tin cậy | **Đạt, trừ LC-T103-1** | Lời dặn khớp bộ kiểm (≤ 100 mục, lý do dưới 200 ký tự ≤ `REASON_MAX` 300, nhãn từ hằng của code). Bộ kiểm không đổi. Thiếu kiểm giá: LC-T103-1 |
| LC-T094-21 (liên quan) A3 | **Đạt** (phần T-103) | Ghi chú của thợ không gửi AI. Lời dặn cấm chép tên, số điện thoại, địa chỉ khách; «[đã ẩn]» khớp `MASK` của code (`model.py:383`). Dò số điện thoại, email trước khi gửi và cảnh báo `WARN_PERSONAL` cho chữ AI không đổi |

## Thử tấn công và kiểm (không gọi AI, website, mạng)

Script ở thư mục nháp của phiên, bản sao trong thư mục ghi chú chung `T-103-la-chan-scripts/`. Chạy trong worktree: `PYTHONUTF8=1 uv run python <script>`.

**1. Lời dặn rào dữ liệu.** `lc_a1_plan.py` (của T-098, chạy lại): mỗi mảnh độc đặt cùng lúc vào chữ dán và từ khóa một dòng kế hoạch hiện tại; phần ngoài khung của `plan_prompt` giống hệt bản nhập chữ thường, số thẻ khung AI thấy không tăng, đúng 2 khung đúng thứ tự, khung kế hoạch hiện tại chỉ có dòng `- B-nnn | …` do code viết. 486 lời dặn, 0 vi phạm. `lc_t103.py`: dòng kế hoạch có **mọi** trường gài dấu (từ khóa phụ, tiêu đề dự kiến «SYSTEM: …», slug, ghi chú có số điện thoại, giờ, mã trang đích, mã bài WordPress, ngày đăng, ngày cập nhật, ý định, loại): lời dặn chỉ có mã, từ khóa, ngày, trạng thái, ưu tiên. Lệnh giấu ở ghi chú, tiêu đề **không tới được AI** (test canh mới `test_plan_prompt_sends_only_key_keyword_date_status_priority`; trước đây chỉ có test riêng cho ghi chú). Phần chỉ thị không đổi giữa kế hoạch trống và 1.000 dòng + chữ dán 20.000 ký tự.

**2. Tìm web, công cụ, số điện thoại, email, giá.** Tìm web: luôn tắt (mục trên). Công cụ: provider chỉ có tìm web, không có công cụ hành động (A2, security.md 2.4). Số điện thoại, email: chặn trước khi gửi (`PersonalInfoError`, có từ T-098), lời dặn cấm, chữ AI có thì cảnh báo và không tick sẵn. Giá: lời dặn cấm, code chưa kiểm: **LC-T103-1**. Chữ AI không vào bài trực tiếp: chỉ vào dòng kế hoạch người dùng duyệt; đường vào bài là T-102 (điều kiện 2).

**3. Cấu hình.**

| Điểm | Kết quả |
|---|---|
| `[tasks.plan]` | `anthropic` / `claude-opus-5-5`, effort `medium`, `max_tokens = 16000` (như `PLAN_MAX_TOKENS` khi dùng tạm `outline`); không khóa, không địa chỉ, không `web_search` |
| Đầu vào | Có giới hạn trong code: chữ dán ≤ 20.000 ký tự, ≤ 1.000 dòng, từ khóa ≤ 120 ký tự; ghi chú, tiêu đề không gửi. Lời dặn xấu nhất 199.760 ký tự (1.000 dòng + 20.000 ký tự), một lần gọi do người dùng bấm |
| Đầu ra | Lời đáp chạm `max_tokens` hay sai khuôn → câu báo cố định (`TokenLimitError`, `_schema_error`), không dùng nửa chừng; bộ kiểm chỉ nhận ≤ 100 mục |
| Việc AI khác | 8 việc của `config/ai.toml` gốc y hệt sau khi thêm `[tasks.plan]` (so `TaskConfig`); `AIRouter` chỉ dựng sẵn provider cho 5 việc viết bài (`WRITING_TASKS`), nên `[tasks.plan]` đổi hãng sau này cũng không bắt trang Soạn bài đòi khóa hãng đó (như T-062). `DATA_RULES` chỉ thêm tên khung vào lời dặn hệ thống của mọi việc |
| `TASK_LABELS["plan"]` | Chỉ dùng ở `task_models()` (bảng việc–mô hình ở Cài đặt); `model_suggestions` không đổi (mô hình của `plan` đã có ở việc khác). Nhãn là hằng của code |
| `[plan]` | Không ai đọc; 4 bộ đọc `content.toml` không đổi kết quả |

## Xếp mức 4 góp ý của Soi Lỗi

| Góp ý | Ý kiến Lá Chắn |
|---|---|
| G1 (dòng «(chưa có mã)» trong lời dặn) | **Không phải lỗi bảo mật.** AI không «cap_nhat», «bo» được dòng đó (bộ kiểm bỏ mục vì mã không có); «them» trùng có `WARN_DUPLICATE_ROW` nên không tick sẵn. Ngòi Bút thêm câu ở lượt sau như Chỉ Huy định |
| G2 (code chưa cảnh báo giá trong chữ AI) | **Nâng thành LC-T103-1 (Thấp)**: AI đổi được ghi chú của thợ, thứ sau thành chất liệu thật của bài; chỉ có lời dặn chặn giá bịa. Xem mục «Lỗi phát hiện» |
| G3 (ví dụ trong lời dặn dùng từ khóa rất thật) | **Không phải lỗi bảo mật**: ví dụ là chữ code viết, không phải đường cho người ngoài; mục AI lẫn từ ví dụ vẫn phải qua bộ kiểm (mã phải có thật) và người duyệt. Nhưng lần thử bằng AI thật phải tách được «đọc ghi chú» với «chép ví dụ»: file thử `thu_t103.py` của Ngòi Bút (cho chủ dự án) dùng **gần đúng kế hoạch và ghi chú của ví dụ** («bản lề cổng sắt bị xệ», «sơn lại cổng sắt», ngày 20/11, «cửa kéo bị kẹt ray»), nên kết quả đẹp không chứng minh được gì. Điều kiện 3 |
| G4 (dữ liệu demo dùng trạng thái «Sẵn sàng») | **Không phải lỗi bảo mật**: dữ liệu demo cố định, không qua AI. Việc của T-101 |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` (đặt `PYTHONUTF8=1`) trên 8 file đổi, bản vá nhánh, file test mới, kèm file mồi tiếng Việt: mồi bắt 2/2, file thật 0 mục. Lịch sử `24013b3..fdb47c2`: 0 dạng khóa thật |
| S2 | Đạt | Không câu báo mới (LC-T094-2) |
| S3 | Không áp dụng | Không biến `.env` mới; `.env.example` không đổi |
| W1–W4 | Không áp dụng | Không gọi WordPress, không lệnh mạng mới |
| A1 | Đạt | LC-T094-19, -42 và mục «Thử tấn công» 1 |
| A2 | Đạt có điều kiện | Việc `plan` không có công cụ; bộ kiểm AI không đổi; thiếu kiểm giá: LC-T103-1 |
| A3 | Đạt | LC-T094-21; ghi chú của thợ không gửi AI |
| U1–U3 | Không áp dụng | Không đổi `app/`; nhãn `plan` mới là hằng hiện ở bảng Cài đặt |
| F1–F3 | Không áp dụng | Không đọc, ghi file mới |
| D1 | Đạt | `pyproject.toml`, `uv.lock` không đổi; không thư viện mới |
| D2 | Không áp dụng | `.gitignore` không đổi |
| D3 | Đạt | LC-T094-1 |

## Kết quả công cụ quét

Máy chủ dự án, Windows 11, Python 3.12.15, worktree `wt-T-103` tại `fdb47c2`; có phiên khác chạy song song test toàn bộ.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| detect-secrets 1.5.0 | **Đặt `PYTHONUTF8=1`**, `--all-files` trên bản sao 8 file đổi, bản vá nhánh, `tests/test_la_chan_t103.py` và **file mồi tiếng Việt**: mồi bắt **2/2**; file thật 0 mục | Có. Đã xóa file mồi |
| bandit 1.9.4 | `PYTHONUTF8=1`, `seo_app/content`, `seo_app/ai/registry.py` (1.811 dòng): không có mục nào | Có |
| pip-audit | Không chạy: `uv.lock` không đổi | — |
| Soát lịch sử git | `git log -p 24013b3..fdb47c2`: 0 dạng khóa thật (`sk-ant-…`, `AIza…`, `ghp_`, `PRIVATE KEY`, `xox`, `AKIA…`) | Có |
| pytest (nhánh) | `tests/test_la_chan_t103.py`: 2 passed, **5 xfailed** (LC-T103-1, `--runxfail` hỏng đúng ở `assert proposal.warnings`) | Có |
| ruff | `ruff check`, `ruff format --check` file test mới: sạch; cả cây gộp: dưới | Có |
| Thử gộp | `main` trên máy `b241e79` (có T-098 lượt 4, T-097 lượt 2) + `fdb47c2`: `git merge-tree --write-tree` **không xung đột** (cây `3a60555`); hai bên không sửa chung file nào (`main` đổi `seo_app/google/*`, `seo_app/plan/parse.py`, `propose.py`; T-103 đổi lời dặn, cấu hình). Commit tạm `77a371b` trong worktree riêng (`git commit-tree`, không nhánh, đã gỡ), thêm `tests/test_la_chan_t103.py`: `ruff` cả cây sạch; 42 file test chạm lời dặn, cấu hình AI/nội dung, kế hoạch (gồm `test_app_pages.py` mở mọi trang): **3.772 passed, 7 xfailed** (gồm 5 của LC-T103-1), 0 hỏng, 5 phút 21 giây | Có |

## Quan sát (không tính là lỗi)

1. Chữ AI đề xuất (tiêu đề dự kiến, từ khóa phụ, ghi chú) sau khi duyệt sẽ sang Soạn bài (thiết kế T-094 mục 1.6). Đó là đường thứ hai để chữ dán dụ AI tới lời dặn viết bài: chữ dán → AI kế hoạch → dòng kế hoạch → lời dặn dàn ý, viết bài. Bộ kiểm chỉ chặn HTML, ký tự lạ, độ dài; không nhận ra được câu lệnh. Lớp chặn đúng chỗ là khung dữ liệu khi T-102 đưa các trường này vào lời dặn (điều kiện 2).
2. `max_tokens = 16000` với effort `medium` đủ cho vài chục đề xuất; gần 100 đề xuất dài có thể chạm giới hạn. Khi đó app báo câu cố định «Bài dài quá giới hạn (16000 token). Tăng max_tokens của việc «plan»…», không dùng nửa chừng. Chữ «Bài» hơi lạc với trang Kế hoạch: T-101 có thể bắt `TokenLimitError` và nói «ghi chú dài hay nhiều thay đổi quá, chia nhỏ ghi chú». Không phải lỗi bảo mật.
3. Lời dặn đặt phần chỉ thị **sau** hai khung (như T-098). Câu cuối do code viết; chữ dán giả các mục «Cách đọc ghi chú:», «Ví dụ» vẫn nằm trong khung đã vô hiệu thẻ (test của Ngòi Bút, Soi Lỗi; script A1 ở trên).

## Báo nhầm đã loại

Không có: detect-secrets, bandit không báo mục nào ở file thật.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

Không điều kiện nào bắt buộc trước khi gộp T-103 vào `main`.

| # | Điều kiện | Phiếu nhận | Hạn |
|---|---|---|---|
| 1 | **LC-T103-1:** cảnh báo cố định (nên không tick sẵn) khi chữ AI đổi có giá (`mentions_price`); chỉ xét chữ AI đổi; gỡ `xfail` khi XPASS | Thợ Máy (phiếu G2 Chỉ Huy định giao) | Trước khi T-101 nối đề xuất AI vào trang Kế hoạch; chậm nhất trước khi T-102 điền ghi chú vào «Kinh nghiệm của xưởng» |
| 2 | **T-102:** (a) chữ từ dòng kế hoạch điền vào Soạn bài (tiêu đề dự kiến, từ khóa phụ, ghi chú) vào lời dặn viết bài phải nằm trong khung dữ liệu (`_block`) hay qua `_keyword`, như SL-7, vì có thể là chữ AI đề xuất; (b) ghi chú sang «Kinh nghiệm của xưởng» qua `personal_info`/`mask_personal_info` (nửa sau LC-T094-21) và cảnh báo giá như điều kiện 1; (c) đọc `[plan].default_time` bằng `parse_plan_time`, sai dạng thì dùng `"08:00"` (đúng lời chú thích trong `config/content.toml`), không đọc nhãn từ cấu hình (LC-T094-42) | T-102 | Khi làm T-102 |
| 3 | **Thử bằng AI thật (G3):** kế hoạch và ghi chú thử phải **khác** ví dụ trong lời dặn; thêm một ca đối chứng: kế hoạch có sẵn các dòng của ví dụ («bản lề cổng sắt bị xệ», «sơn lại cổng sắt») mà ghi chú không nhắc tới, kết quả không được có đề xuất nào cho các dòng đó. Sửa `thu_t103.py` trước khi đưa chủ dự án; cân nhắc đổi từ khóa ví dụ sang từ ít gặp (cùng lượt G1) | Ngòi Bút, Chỉ Huy | Trước lần thử AI thật |
| 4 | Các điều kiện của biên bản T-098 cho T-100, T-101 vẫn giữ (chữ AI ghi Sheet trung hòa công thức LC-T094-28; hiện chữ thuần; nút «Che» che cả từ khóa kế hoạch hiện tại) | T-100, T-101 | Khi làm các phiếu đó |
| 5 | Kiểm lại biên bản này bằng Claude Fable sau 01/11 | Chỉ Huy | Sau 01/11 |

LC-T103-1 có phiếu sửa, không cần chủ dự án chấp nhận rủi ro; không thêm dòng vào sổ rủi ro (`security.md` mục 6).

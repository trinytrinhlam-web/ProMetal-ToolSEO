# Báo cáo T-083 · Dọn lỗi chữ nhỏ trong alt, chú thích ảnh AI (SL-T068-1, -2, -3, LC-T068-1, SL-T081-1)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-083](../tickets/T-083-don-loi-chu-mo-ta-anh.md) |
| Nhánh | `team/T-083` (worktree `D:\ProMetal-ToolSEO\wt-T-083`), gốc `main` `b60054f` |
| Ngày nộp | 2026-10-27 |
| Kết quả | Hoàn thành (yêu cầu 1–4). Không cần sửa phần đọc cấu hình ảnh: giới hạn dưới nằm ngay trong `alt.py` |

## Tóm tắt (cho chủ dự án)

- Khi AI tự viết chữ «Minh họa» theo kiểu lạ (không dấu «Minh hoa», «Tranh minh họa», trong dấu `` ` `` hay `_`, sau gạch đầu dòng «- », «1. », hay để «(AI)» tách riêng như «[Minh họa] (AI): …»), alt và chú thích nay chỉ còn **đúng một** tiền tố: «Minh họa cửa cuốn», «Ảnh minh họa (AI): ray dưới bị mòn». Trước đây bị lặp («Minh họa minh hoa cửa cuốn», «Ảnh minh họa (AI): (AI): …»).
- Alt AI chỉ viết mỗi chữ «Minh hoa», «- Minh họa» (không tả gì) nay bị từ chối với câu quen thuộc «AI không viết được alt…, bấm thử lại», như alt «???» từ trước. Alt ảnh AI mà chữ đầu dài hơn chỗ còn lại (chỉ gặp khi giới hạn alt rất nhỏ) cũng vậy, thay vì ra mẩu chữ cụt như «Minh họa [code_snipp».
- Chú thích ảnh AI không còn bị cụt giữa chữ («Ảnh minh họa (AI): r»): không đủ chỗ cho một chữ trọn thì chỉ ghi «Ảnh minh họa (AI)». Giới hạn quá nhỏ để chứa tiền tố thì phần mềm báo lỗi chứ không cắt cụt tiền tố (chỉ gặp khi code gọi sai; file cấu hình không cho đặt dưới 20).
- Bảo đảm cũ giữ nguyên: ảnh AI **luôn** có «Minh họa» / «Ảnh minh họa (AI)»; ảnh thật không đổi gì; chặn link, chặn shortcode như cũ. Kết quả nay «bất động»: lọc lại lần nữa không đổi chữ.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/images/alt.py` | Nhận thêm kiểu tiền tố AI tự viết (`_AI_PREFIX` `:362`, `_AI_TAG` `:372`, `_NUMBERED` `:376`, thêm `` ` `` `_` vào `_WRAPPERS` `:380`); `_strip_ai_prefix` (`:412`) bỏ cả dấu câu đầu phần thân, «(AI)» tách rời, số thứ tự trước tiền tố; `_cut`, `clean_alt_text` thêm tùy chọn `whole_words` (`:309`, `:335`); `_ai_body` mới (`:478`); `_check_ai_limits` mới (`:497`) và hằng `AI_ALT_MIN_CHARS`, `AI_CAPTION_MIN_CHARS` (`:404-405`); cắt thô `_RAW_FACTOR` (`:392`); `clean_suggestion` dùng các phần trên (`:536-557`); ảnh thật đi đúng hai dòng cũ (`:547-548`) |
| `tests/test_soi_loi_t068.py` | Gỡ 5 dòng `@pytest.mark.xfail(...)` (SL-T068-1, -2, -3; 23 ca). Thân test không đổi, 0 dòng thêm |
| `tests/test_soi_loi_t081.py` | Gỡ 5 dòng `@pytest.mark.xfail(...)` của `test_sl_t081_1_…` (5 ca). Thân test không đổi, 0 dòng thêm |
| `tests/test_t083_alt_tien_to.py` | Mới: 20 hàm test, 1.096 ca (mục «Test mới») |
| `docs/team/reports/T-083-tho-may.md` | Báo cáo này |

Không sửa `seo_app/images/html.py`, `seo_app/wordpress/**`, `app/**`, `config/**`, `seo_app/content/rules.py`.

## Cách sửa

| Lỗi | Sửa | Chỗ |
|---|---|---|
| **SL-T068-1** tiền tố không dấu, gạch nối, «AI» không ngoặc, gọi khác | `_AI_PREFIX` nhận «họa / hoạ / hoa» (có dấu đúng hoặc không dấu), «ảnh/anh», «hình/hinh», «bức/buc», thêm «tranh», «tranh vẽ», «hình vẽ»; hai chữ nối bằng khoảng trắng, «-», «‐», «‑», «_» hay dính liền («Minhhọa», gợi ý G3); «AI» không ngoặc, chỉ chữ hoa («Ảnh minh họa AI:») | `alt.py:354-368` |
| **SL-T068-2** dấu Markdown khác `*`, dấu đầu dòng | `_WRAPPERS` thêm `` ` `` và `_` (cả `` `` `` và `__`, tối đa 3 ký tự như cũ); «- », «• » bỏ nhờ bước bỏ dấu câu đầu chữ; số thứ tự «1. », «2) » (`_NUMBERED`) chỉ bỏ khi ngay sau là tiền tố | `alt.py:373-384`, `:432-437` |
| **SL-T081-1** «(AI)» tách khỏi tiền tố | Mỗi vòng của `_strip_ai_prefix`, chữ còn lại mở đầu bằng «(AI)» (hoa thường, có cách trong ngoặc) hay «AI» (chữ hoa, trọn chữ) thì bỏ, rồi bỏ dấu câu tiếp | `alt.py:369-372`, `:428-431` |
| **G1** (Soi Lỗi T-068) dấu câu đầu phần thân | Mỗi vòng bắt đầu bằng `lstrip(_AFTER_PREFIX)`: «- cửa cuốn», «: cửa cuốn» ra «Minh họa cửa cuốn» ngay lần đầu, không đợi chạy lại | `alt.py:385-388`, `:427` |
| **SL-T068-3** chú thích cụt giữa chữ ở 20–21 | Chú thích ảnh AI cắt bằng `whole_words=True`: cắt ở dấu cách cuối cùng còn vừa; không có chữ trọn nào vừa thì phần thân rỗng, chỉ còn «Ảnh minh họa (AI)». Alt giữ cách cắt cũ (alt không được rỗng). Ảnh thật giữ cách cắt cũ | `alt.py:309-324`, `:335-349`, `:467-475`, `:543-545`, `:554-556` |
| **LC-T068-1** giới hạn nhỏ hơn tiền tố | `clean_suggestion` ảnh AI: `caption_max_chars` < 17 (`AI_CAPTION_MIN_CHARS` = độ dài «Ảnh minh họa (AI)») hay `max_chars` < 10 (`AI_ALT_MIN_CHARS` = «Minh họa» + dấu cách + 1 ký tự) thì báo `ValueError` câu cố định, không cắt tiền tố. `_with_prefix` không còn nhánh `prefix[:limit]` | `alt.py:400-409`, `:497-506`, `:536-537` |
| Yêu cầu 3 (bất động) | `_ai_body`: bỏ tiền tố, cắt; nếu cắt giữa chữ làm lộ ra tiền tố mới («1. Minh_hoa10…» cắt còn «1. Minh_hoa») thì bỏ tiếp tới khi không đổi | `alt.py:478-494` |
| Chữ đầu không vừa (giữ ý `test_alt_cut_down_to_punctuation_only_is_refused`) | Ảnh AI: chữ đầu của phần thân (sau khi bỏ tiền tố, dấu câu) đã dài hơn chỗ còn lại thì phần thân rỗng: alt báo «AI không viết được alt», chú thích chỉ còn tiền tố. Xem đoạn dưới bảng | `alt.py:484-490` |
| **G4** (Soi Lỗi T-068) | Cắt thô chữ AI còn 4 × giới hạn trước khi bỏ tiền tố, theo khuyến nghị Lá Chắn T-068 | `alt.py:389-392`, `:542-545` |

**Vì sao thêm quy tắc «chữ đầu không vừa»:** lượt chạy đủ bộ test đầu tiên (17:58 → 18:26) hỏng 1 test cũ của Thợ Máy T-068, `tests/test_t062_alt_prompt.py::test_alt_cut_down_to_punctuation_only_is_refused` (ảnh AI, giới hạn 29, AI viết «?????????? cửacuốnnhàphốmởmộtnửa»: mong đợi «AI không viết được alt»). Bản `main` cắt còn «??????????» nên báo lỗi; sau G1 (bỏ dấu câu đầu thân, cần cho yêu cầu 3), bản mới cắt giữa chữ dài còn «Minh họa cửacuốnnhàphốmởmộtnử»: vẫn là alt vô nghĩa, đúng điều test muốn chặn. Tôi **không sửa test**; sửa code theo đúng ý test: chữ đầu đã không vừa thì kết quả chỉ là mẩu chữ cụt, coi như không có chữ. Lượt chạy lại sau khi sửa ở mục «Bằng chứng».

**Vì sao ngưỡng của LC-T068-1 là 17 / 10, không phải 20 như Lá Chắn T-068 gợi ý:** `tests/test_soi_loi_t081.py::test_cat_do_dai_sau_khi_bo_gach_cheo` (test của Soi Lỗi, tôi không được sửa) gọi ảnh AI với `max_chars=18`; ngưỡng 20 cho alt sẽ làm test đó hỏng. Ngưỡng theo đúng độ dài tiền tố vẫn đạt ý của Lá Chắn: **không bao giờ** cắt cụt tiền tố, và bảo đảm này nằm ngay trong `alt.py`, không dựa vào mức sàn 20 của `rules.py`. Với 17–19, chú thích là đúng «Ảnh minh họa (AI)»; với 10–19, alt là «Minh họa …» trọn tiền tố (hoặc báo «AI không viết được alt» khi chữ đầu không vừa). Chọn `ValueError` (lỗi lập trình) thay vì `AIError`: giới hạn đọc từ `config/` không bao giờ dưới 20, nên chỉ lời gọi sai trong code mới gặp, và câu «AI không viết được alt» sẽ nói sai nguyên nhân.

**Vì sao «Minh Hòa» không bị coi là tiền tố:** gợi ý của Soi Lỗi là so trên chữ đã bỏ hết dấu. Làm vậy thì «Minh Hòa», «Minh Hóa» (tên người, tên xã) cũng thành «minh hoa» và bị xóa khỏi alt. Tôi chỉ nhận đúng dấu («họa», «hoạ») hoặc không dấu hẳn («hoa»), đủ cho mọi ca Soi Lỗi nêu.

**Ví dụ (ảnh AI, giới hạn 125 / 200 trừ khi ghi khác; bản `main` → bản mới):**

| AI viết (alt / chú thích) | Bản `main` | Bản mới |
|---|---|---|
| «Minh hoa cửa cuốn» / «Anh minh hoa (AI): ray dưới bị mòn» | «Minh họa minh hoa cửa cuốn» / «Ảnh minh họa (AI): anh minh hoa (AI): ray dưới bị mòn» | «Minh họa cửa cuốn» / «Ảnh minh họa (AI): ray dưới bị mòn» |
| «Tranh minh họa cửa cuốn» / «Ảnh minh họa AI: ray dưới bị mòn» | «Minh họa tranh minh họa cửa cuốn» / «Ảnh minh họa (AI): AI: ray…» | «Minh họa cửa cuốn» / «Ảnh minh họa (AI): ray dưới bị mòn» |
| «`` `Minh họa` `` cửa cuốn» / «- Ảnh minh họa (AI): ray…» | «Minh họa `` `Minh họa` `` cửa cuốn» / «Ảnh minh họa (AI): - Ảnh minh họa (AI): ray…» | «Minh họa cửa cuốn» / «Ảnh minh họa (AI): ray dưới bị mòn» |
| «1. Minh họa: cửa cuốn» / «_Ảnh minh họa (AI)_: ray…» | «Minh họa 1. Minh họa: cửa cuốn» / «Ảnh minh họa (AI): _Ảnh minh họa (AI)_: ray…» | «Minh họa cửa cuốn» / «Ảnh minh họa (AI): ray dưới bị mòn» |
| «[Minh họa] (AI): Cổng inox 2 cánh» (cả hai) | «Minh họa (AI): Cổng inox 2 cánh» / «Ảnh minh họa (AI): (AI): Cổng inox 2 cánh» | «Minh họa cổng inox 2 cánh» / «Ảnh minh họa (AI): cổng inox 2 cánh» |
| «- cửa cuốn» / «: cửa cuốn» | «Minh họa - cửa cuốn» / «Ảnh minh họa (AI): : cửa cuốn» | «Minh họa cửa cuốn» / «Ảnh minh họa (AI): cửa cuốn» |
| «Minh hoa» (alt) | «Minh họa minh hoa» | báo «AI không viết được alt…» |
| chú thích «ray dưới bị mòn», giới hạn chú thích 20 | «Ảnh minh họa (AI): r» | «Ảnh minh họa (AI)» |
| chú thích «ray dưới bị mòn», giới hạn chú thích 10 | «Ảnh minh h» | `ValueError` «Giới hạn chú thích của ảnh AI là 10 ký tự, nhỏ hơn 17: không đủ chỗ cho tiền tố «Ảnh minh họa (AI)».» |
| «Minh Hòa cửa cuốn» | «Minh họa minh Hòa cửa cuốn» | như cũ (tên riêng, không phải tiền tố) |
| «[code_snippet id=1]» (alt), giới hạn alt 20 | «Minh họa [code_snipp» | báo «AI không viết được alt…» (chữ đầu 13 ký tự, chỗ còn 11) |

## Test mới (`tests/test_t083_alt_tien_to.py`)

- 31 kiểu tiền tố (không dấu, gạch nối, dính liền, «AI» không ngoặc, gọi khác, `` ` ``, `` `` ``, `_`, `__`, «- », «* », «• », «1. », «2) », «10. «…»», «(AI)» tách rời, «AI:» đứng trước) × 4 kiểu nối: alt, chú thích đúng từng chữ; alt chỉ có tiền tố bị từ chối, chú thích chỉ có tiền tố ra đúng tiền tố; ảnh thật giữ nguyên chữ.
- Chữ không phải tiền tố được giữ: «Minh Hòa», «Minh Hoàng», «Minh hoạt», «Anh minh», «AIR», «ai cũng thích», số thứ tự không đứng trước tiền tố.
- G1: 10 kiểu dấu câu đầu phần thân.
- Bất động: 144 chuỗi lạ × 5 cặp giới hạn (20/20 → 500/1000), cả ảnh AI lẫn ảnh thật (có 2 chuỗi «cắt giữa chữ lộ tiền tố», kèm test riêng).
- SL-T068-3: chú thích ảnh AI ở mọi giới hạn 17–89 cắt trọn chữ và lấy nhiều chữ nhất có thể; một chữ dài thì chỉ còn tiền tố; ảnh thật vẫn cắt như trước.
- LC-T068-1: mọi giới hạn 1–19 cho alt và chú thích: dưới ngưỡng báo `ValueError` (câu không chép chữ AI), từ ngưỡng trở lên tiền tố còn nguyên; ảnh thật giới hạn nhỏ không báo lỗi.
- Chữ đầu không vừa chỗ còn lại: 4 ca (giới hạn 10, 11, 29, 125): alt báo lỗi, chú thích chỉ còn tiền tố.
- G4: hàm bỏ tiền tố không bao giờ nhận chữ dài hơn 4 × giới hạn.
- W3 / mục 2.3: 6 kiểu tiền tố mới × 7 đuôi (shortcode `[code_snippet id=1]`, `[[…]]`, `[embed]…`, `[gallery …]` sau «(AI)», link Markdown, thẻ `<a>`, `<img onerror>`): chữ lưu không còn cú pháp link sống hay thẻ; `figure_html` không còn «[», «]», «\», `<a `, `onerror`, `javascript`; chạy lại không đổi.
- Mở lại nháp (`clean_loaded` → `_ai_prefixed`, đường thứ hai dùng `clean_suggestion`): alt «`` `Minh hoa` ``: …», chú thích «[Minh họa] (AI): …» ra đúng một tiền tố.

## Bằng chứng

Máy Windows 11 Pro (10.0.26300) của chủ dự án, Python 3.12.15 (uv), worktree `wt-T-083`. Máy chạy song song các agent khác.

Test của phiếu (9 file trong tiêu chí xong), test mới, và test của mọi nơi gọi hàm dùng chung đã sửa (`clean_suggestion`, `clean_alt_text`: `seo_app/storage/drafts.py` mở lại nháp, `app/views/write.py` qua `suggest_alt`; danh sách lấy bằng `grep` mọi file test nhập `seo_app.images.alt`, `seo_app.storage.drafts`, `suggest_alt`, `clean_loaded`):

```
$ uv run pytest -q -p no:cacheprovider -rfEX \
    tests/test_soi_loi_t068.py tests/test_soi_loi_t081.py tests/test_t081_alt_gach_cheo.py \
    tests/test_t062_alt_prompt.py tests/test_soi_loi_t062.py tests/test_soi_loi_t071.py \
    tests/test_shortcode_t061.py tests/test_soi_loi_t061.py tests/test_wordpress_images.py \
    tests/test_t083_alt_tien_to.py \
    tests/test_ai_images.py tests/test_app_drafts.py tests/test_app_images.py tests/test_drafts_images.py \
    tests/test_images_folders_t063.py tests/test_images_tags.py tests/test_la_chan_t056.py \
    tests/test_la_chan_t076.py tests/test_la_chan_t086.py tests/test_soi_loi_t016_t020.py \
    tests/test_soi_loi_t021_t017.py tests/test_soi_loi_t041.py tests/test_soi_loi_t050.py \
    tests/test_soi_loi_t052.py tests/test_soi_loi_t054.py tests/test_soi_loi_t055.py \
    tests/test_soi_loi_t056.py tests/test_soi_loi_t065.py tests/test_soi_loi_t076.py \
    tests/test_soi_loi_t086.py tests/test_soi_loi_t089.py tests/test_storage_drafts.py \
    tests/test_storage_send_state.py tests/test_t041_drafts_seo.py tests/test_t041_links_ai.py \
    tests/test_t041_meta.py tests/test_t041_seo_ui.py tests/test_t086_send_state.py \
    tests/test_t089_send_draft.py
(2026-10-27 18:30:00 → 19:36:40 +0700, bản cuối; máy chạy cùng lúc 2 lượt pytest của phiên khác nên chậm)
4681 passed, 20 skipped, 1 xfailed in 3989.71s (1:06:29)
```

- 0 hỏng, 0 XPASS. 1 `xfailed` là SL-T041-8 (`tests/test_soi_loi_t041.py:734`, emoji Unicode 16 ở phần SEO), có từ trước, không liên quan. 20 bỏ qua đều do máy: symlink, quyền POSIX chỉ thử trên Mac/Linux, ổ không phân biệt hoa thường, ổ tắt tên ngắn 8.3 (17 ca xem từng lý do bằng `-rs` trên 5 file; 3 ca còn lại thuộc các dấu bỏ qua theo hệ điều hành của `tests/test_drafts_images.py`, `tests/test_soi_loi_t055.py`).
- Lượt chạy đủ trước đó (17:58:06 → 18:26:04, trước khi thêm quy tắc «chữ đầu không vừa»): `1 failed, 4676 passed, 20 skipped, 1 xfailed`; ca hỏng là `test_alt_cut_down_to_punctuation_only_is_refused` (mục «Cách sửa»). Sau khi sửa: 7 file alt chạy lại thì 2 ca trong test mới của tôi hỏng (giới hạn alt 10–11 với chữ đầu «cửa» nay báo lỗi đúng quy tắc mới); đổi dữ liệu test đó sang chữ đầu một ký tự và thêm test riêng cho quy tắc; `tests/test_t083_alt_tien_to.py tests/test_t062_alt_prompt.py`: `1294 passed`; rồi lượt đủ ở trên.
- Sau lượt đủ chỉ thêm một dòng docstring trong `clean_suggestion` (không đổi code). Chạy lại 7 file alt trên đúng bản commit (19:43:18 → 19:47:27): `tests/test_t083_alt_tien_to.py tests/test_t062_alt_prompt.py tests/test_soi_loi_t062.py tests/test_soi_loi_t068.py tests/test_soi_loi_t081.py tests/test_t081_alt_gach_cheo.py tests/test_soi_loi_t071.py` → `1860 passed in 220.47s`.

```
$ uv run ruff check .
All checks passed!
$ uv run ruff format --check seo_app/images/alt.py tests/test_t083_alt_tien_to.py
2 files already formatted
```

- 28 ca `xfail` cũ (23 SL-T068, 5 SL-T081) qua với `--runxfail` trước khi gỡ dấu (`289 passed` trên 2 file); sau khi gỡ dấu vẫn qua (lượt chạy ở trên, 0 `xfailed`, 0 `XPASS` trong 2 file đó).
- `git diff origin/main -- tests/test_soi_loi_t068.py tests/test_soi_loi_t081.py`: chỉ có 10 dòng `-` (dòng dấu `xfail`), 0 dòng `+`.

**Thử ngẫu nhiên** trên bản cuối (script ngoài repo, ở thư mục ghi chú chung của các phiên, `T-083-tho-may-scripts/`: `fuzz_t083.py`, `fuzz_t083_classify.py`, kèm log hai lượt test; bản `main` của `alt.py` lấy bằng `git show b60054f:seo_app/images/alt.py`): 60.000 cặp alt/chú thích (hạt giống 83083) ghép 0–3 tiền tố từ 23 kiểu (có cả «Minh Hòa», «Minh hoạt», «Ảnh AI», «ai») × 24 kiểu mở đầu (ngoặc, `` ` ``, `_`, dấu đầu dòng, số thứ tự, `<b>`) × 18 kiểu nối (có `\:`, xuống dòng, NBSP, ký tự rộng 0) rồi 0–5 mảnh thân (shortcode, link, thẻ, email, `www.`, `\[`, chữ Hán, emoji, chữ rất dài), giới hạn alt 20–500, chú thích 20–1000:

| Đo | Bản `main` | Bản mới |
|---|---|---|
| Ảnh thật khác bản `main` | — | **0** |
| Ảnh AI thiếu tiền tố chuẩn (C6), quá giới hạn, nhiều dòng, sai NFC | 0 | **0** |
| Chạy lại `clean_suggestion` đổi chữ | 8.788 | **0** |
| Chữ lưu còn cú pháp link sống, thẻ, `href` | — | **0** |
| Chữ gửi WordPress (`plain_image_text`) có «\» mà đầu vào không có | — | **0** |
| Alt có «minh h…» lặp | 26.132 | 8.337 (chỉ còn khi tiền tố đứng sau chữ không phải tiền tố, ví dụ «~Anh minh hoa…», «Ảnh AI (AI): … Ảnh minh họa») |
| Báo «AI không viết được alt» mới | — | 5.129, `fuzz_t083_classify.py` xếp hết: 3.848 bỏ tiền tố xong không còn chữ cái, chữ số nào (bản `main` ra «Minh họa minh hoa», «Minh họa __Hình ảnh»…); 1.265 chữ đầu dài hơn chỗ còn lại (bản `main` ra mẩu chữ cụt «Minh họa [code_snipp», «Minh họa cửacuốnnhàp», «Minh họa C:\Users202»); 16 khác: cắt lộ tiền tố («Minh họa 1. Minh_hoa») hay thân «[nhãn]: chữ» mà `clean_ai_text` vốn xóa (Ghi nhận 1 của Soi Lỗi T-081) |
| Hết báo lỗi | — | 3 (dấu câu đầu thân được bỏ nên phần chữ thật vừa giới hạn, ví dụ «??? : cửacửa cuốn khe thoáng…» ra «Minh họa cửacửa cuốn») |
| Lỗi lạ khác | — | 0 |

Không gọi AI, WordPress hay mạng thật; test dùng dữ liệu giả và bộ chặn mạng của `tests/conftest.py`.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: SL-T068-1, -2, -3, LC-T068-1, SL-T081-1 sửa theo gợi ý (mục «Cách sửa»); 28 ca `xfail` cũ qua; làm kèm G1, G3, G4 theo khuyến nghị gom của Lá Chắn T-068
- [x] Yêu cầu 2: C6 giữ (test C6 cũ `tests/test_t062_alt_prompt.py`, `tests/test_soi_loi_t062.py::test_ai_image_alt_and_caption_always_start_with_prefix`, `tests/test_soi_loi_t068.py::test_c6_holds_for_prefix_styles_code_does_not_strip` qua; thử ngẫu nhiên 0 lần thiếu tiền tố); chặn link, shortcode giữ (`tests/test_shortcode_t061.py`, `tests/test_soi_loi_t061.py`, `tests/test_t081_alt_gach_cheo.py`, `tests/test_soi_loi_t081.py` qua; `test_shortcode_link_sau_tien_to_moi_van_bi_vo_hieu`)
- [x] Yêu cầu 3: bất động (`test_chay_lai_clean_suggestion_khong_doi_chu`, `test_cat_giua_chu_lo_ra_tien_to_thi_bo_tiep`; thử ngẫu nhiên 0/60.000)
- [x] Yêu cầu 4: gỡ `xfail` khi XPASS, chỉ xóa dấu
- [x] Test liên quan của phiếu qua, `uv run ruff check .` sạch (mục «Bằng chứng»); thêm test các nơi gọi hàm dùng chung (`clean_suggestion`, `clean_alt_text`: `seo_app/storage/drafts.py`, `app/views/write.py` qua `suggest_alt`)
- [x] Có test cho phần logic mới (`tests/test_t083_alt_tien_to.py`)
- [x] Báo cáo nộp tại `docs/team/reports/T-083-tho-may.md`

## Rủi ro và điểm cần chú ý

1. **Nhận rộng hơn ở đầu chữ ảnh AI.** Ở đầu alt / chú thích ảnh AI, code nay bỏ thêm: «(AI)», «AI» (chữ hoa, trọn chữ), dấu câu (G1), số thứ tự đứng trước tiền tố. Ví dụ «AI vẽ cổng sắt» ra «Minh họa vẽ cổng sắt». Chỉ đụng ảnh AI, nơi tiền tố chuẩn đã nói ảnh do AI làm; ảnh thật không đổi (0/60.000).
2. **«AI» không ngoặc ngay sau tiền tố bị bỏ** («Minh họa AI tạo cổng» ra «Minh họa tạo cổng»). Chấp nhận vì AI hay viết «Ảnh minh họa AI:»; chữ thường «ai» («Minh họa ai cũng thích») giữ nguyên.
3. **Cắt thô (G4) với chữ toàn tiền tố lặp dài hơn 4 × giới hạn** (hơn 500 ký tự với alt mặc định 125): phần thân có thể chỉ còn mẩu tiền tố dở, ví dụ «Minh họa minh» (test `test_bo_tien_to_chi_chay_tren_chu_da_cat_tho` ghi rõ). Tiền tố chuẩn vẫn còn, người dùng vẫn duyệt alt; AI thật (`max_tokens = 2000`) không viết như vậy.
4. **`ValueError` mới** khi gọi `clean_suggestion` cho ảnh AI với `max_chars` < 10 hay `caption_max_chars` < 17. Hiện không đường nào tới được: `suggest_alt` lấy giới hạn từ `load_alt_rules()` (sàn 20), `drafts._ai_prefixed` dùng 500 / 1000. Trước đây alt ≤ 9 báo `AIError`, chú thích < 17 cắt cụt tiền tố.
5. **Chữ đầu dài hơn chỗ còn lại thì alt ảnh AI báo lỗi.** Ở mức sàn 20 ký tự (còn 11 sau «Minh họa »), chữ đầu dài hơn 11 ký tự (địa chỉ web, tên ghép bằng gạch nối rất dài) làm alt báo «AI không viết được alt», người dùng bấm thử lại hoặc tự gõ. Ở mức mặc định 125 (còn 116) thì thực tế không gặp. Trước đây ra mẩu chữ cụt.
6. **Ngoặc lệch** («(Minh họa cửa cuốn (2 cánh))» ra «Minh họa cửa cuốn (2 cánh))», G2 Soi Lỗi T-068) chưa sửa: ngoài 5 lỗi của phiếu, chỉ là thẩm mỹ, kết quả vẫn bất động.

## Đề xuất

- **Soi Lỗi (rút gọn):** soát `_AI_PREFIX` có nhận nhầm chữ thật đầu alt ảnh AI không (tôi đã thử «Minh Hòa», «Minh Hoàng», «Minh hoạt», «Anh minh», «AIR»); soát ngưỡng 17 / 10 thay cho 20 và quy tắc «chữ đầu không vừa» (mục «Cách sửa»).
- **Lá Chắn (rút gọn, W3):** bước bỏ tiền tố chỉ đụng chữ ảnh AI đã qua `clean_ai_text`; phần thân vẫn lọc lại (`clean_alt_text`) trước và sau khi ghép tiền tố; lớp vô hiệu «[» «]» khi in ra (`html.py`, `client.py`) không đổi. A3: không đổi chữ gửi AI (`alt_system`, `alt_prompt`, `reference_lines` không có trong diff).
- G2 (ngoặc lệch) nếu muốn làm: phiếu dọn riêng, mức Thấp.

## Câu hỏi cho chủ dự án

Không có.

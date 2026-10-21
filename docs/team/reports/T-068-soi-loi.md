# Báo cáo T-068 · Soi Lỗi: dọn lỗi Thấp bước code tự sửa alt (sau T-062)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-068](../tickets/T-068-don-loi-thap-alt-anh-ai.md) · báo cáo Thợ Máy: [T-068-tho-may](T-068-tho-may.md) · lỗi gốc: [T-062-soi-loi](T-062-soi-loi.md) |
| Nhánh | `team/T-068` (worktree `D:\ProMetal-ToolSEO\wt-T-068`), kiểm trên HEAD `69b9f31` của Thợ Máy |
| Ngày nộp | 2026-10-20 |
| Máy chạy | Windows 11 Pro 10.0.26300, Python 3.12 (uv) |
| Mức kiểm | Rút gọn |
| Kết quả | Hoàn thành · **ĐẠT CÓ ĐIỀU KIỆN**: không lỗi chặn, chuyển sang Lá Chắn rút gọn được; điều kiện: 3 lỗi Thấp mới SL-T068-1 → 3 được ghi theo dõi (không chặn gộp T-068 hay T-056) |

## Tóm tắt (cho chủ dự án)

Thợ Máy đã sửa đúng 3 lỗi nhỏ ở bước phần mềm tự chỉnh alt: AI trả «???» nay bị từ chối; AI tự viết «Minh họa» trong ngoặc hay dính dấu câu thì phần mềm chỉ ghi **một** chữ «Minh họa»; giới hạn alt nhỏ không còn làm mất chữ. Tôi thử 60.000 cặp alt/chú thích viết đủ kiểu lạ: **ảnh AI lần nào cũng có chữ «Minh họa»** (hoặc phần mềm báo «AI không viết được alt» để anh/chị bấm thử lại), và **ảnh thật không bao giờ bị gắn chữ «Minh họa»**.

Tìm thêm **3 lỗi mức Thấp**, đều đã có từ trước phiếu này: nếu AI viết «Minh hoa» (không dấu), «Tranh minh họa», hay đặt chữ trong dấu định dạng lạ (`` `Minh họa` ``, «- Minh họa») thì alt thành «Minh họa minh hoa cửa cuốn» (lặp chữ); chú thích ảnh AI ở giới hạn thấp nhất (20 ký tự) bị cắt cụt thành «Ảnh minh họa (AI): r». Không lỗi nào làm mất chữ «Minh họa», và anh/chị vẫn duyệt từng alt ở màn hình chọn ảnh (T-056), nên không chặn.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t068.py` | Mới: 140 test qua, 23 test `xfail(strict=True)` cho 3 lỗi SL-T068-1 → 3 |
| `docs/team/reports/T-068-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, `config/`, test cũ.

## Kết quả kiểm

| # | Việc | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | 3 lỗi SL-T062-1 → 3 sửa thật; gỡ `xfail` mà thân test không đổi | **Đạt** | `git diff origin/main...HEAD -- tests/test_soi_loi_t062.py`: ở 3 test SL-T062 chỉ thay dòng `@pytest.mark.xfail(...)` bằng một dòng chú thích «Thợ Máy T-068 đã sửa: gỡ dấu xfail»; tham số và thân 3 test không đổi một dòng. 18/18 trường hợp qua (lần chạy `-k "sl_t062 or prefix"`: 38 qua). Code: `seo_app/images/alt.py:389-392` (`_meaningful`), `:363-386` (`_strip_ai_prefix`), `:433-446` (bỏ tiền tố → cắt → ghép) |
| 2 | Test C6 `test_ai_image_alt_and_caption_always_start_with_prefix` Thợ Máy đã chỉnh | **Xác nhận** | Xem mục «Ý kiến về test C6 đã chỉnh» bên dưới |
| 3 | C6: ảnh AI luôn có tiền tố, với mọi kiểu AI tự viết, giới hạn 20 → 1000 | **Đạt** | `test_c6_holds_for_prefix_styles_code_does_not_strip` (27 kiểu × giới hạn 20, 29, 125, 1000 = 108 trường hợp, gồm cả kiểu code chưa bỏ được); thử ngẫu nhiên 60.000 lần (mục Bằng chứng): **0** lần thiếu tiền tố, quá giới hạn, nhiều dòng, sai NFC, alt chấm cuối, alt thân không có chữ; **0** lỗi lạ (mọi lỗi đúng câu «AI không viết được alt…») |
| 4 | Alt chỉ có chữ số, chữ hệ khác | **Đạt** | `test_alt_with_only_digits_or_other_scripts_is_kept` («2024», «3», 门窗, Дверь, ประตู, باب; ảnh AI và ảnh thật): được nhận, đúng ý SL-T062-1 (chỉ bỏ alt không có chữ cái hay chữ số nào) |
| 5 | Ảnh thật không bao giờ bị thêm tiền tố | **Đạt** | `test_real_photo_never_gets_ai_prefix_whatever_the_limit` (9 kiểu × giới hạn 20, 125); thử ngẫu nhiên 20.000 lần ảnh thật: 0 lần có «minh» hay «(AI)» khi AI không viết |
| 6 | Tiền tố AI tự viết đủ kiểu | **Đạt phần phiếu đòi, có 2 lỗi Thấp ngoài danh sách** | Được bỏ đúng, ghi một tiền tố: ngoặc góc «», ngoặc kép “” "", ngoặc tròn, vuông, `**…**`, `***…***`, dính `!`, `?`, `…`, `...`, `:` (cả `:` dính chữ), `–`, `—`, `|`, `·`, lặp 2–3 lần (cả «Minh họa: «Minh họa» cửa»), viết hoa («MINH HOẠ»), NFD, dấu cách không ngắt, `\u2009`, `\u3000`, gạch mềm `\u00ad`, `\ufeff`, ngoặc bọc cả câu. Chưa được: không dấu, gạch nối, cách gọi khác (SL-T068-1); dấu Markdown khác `*`, dấu đầu dòng (SL-T068-2) |
| 7 | `max_chars` 20 và lớn; chú thích ảnh AI, ảnh thật | **Đạt, có 1 lỗi Thấp** | Alt ở 20: «Ảnh minh họa (AI): cửa kéo sắt» → «Minh họa cửa kéo sắt» (đủ 20); 500, 1000 không cắt. Chú thích ảnh AI ở 20–21 bị cắt giữa chữ (SL-T068-3, Thợ Máy đã nêu ở Rủi ro mục 3) |

### Ý kiến về test C6 đã chỉnh

**Tôi xác nhận cách chỉnh của Thợ Máy là đúng** (`tests/test_soi_loi_t062.py:482-488`), không cần sửa lại. Lý do:

1. Hai test của tôi ở T-062 mâu thuẫn thật: khi viết, test C6 ghi lại hành vi lúc đó (alt «???» vẫn ra «Minh họa ???»), còn `xfail` SL-T062-1 ghi hành vi mong muốn (báo lỗi). Sửa SL-T062-1 thì buộc phải đổi điều test C6 đòi với đúng hai đầu vào đó. Đây là lỗi thiết kế test của tôi, không phải Thợ Máy nới test.
2. C6 là «không bao giờ có alt ảnh AI thiếu tiền tố». Báo `AIError` nghĩa là không có alt nào được dùng (người dùng bấm thử lại hoặc tự gõ), nên C6 vẫn giữ. Test kiểm đúng câu lỗi (`match=EMPTY_ALT`), không chấp nhận lỗi bất kỳ.
3. Không yếu đi chỗ nào khác: nhánh mới chỉ chạy với đầu vào không có chữ cái hay chữ số (4/19 trường hợp: «???», «🔥🔥» ở giới hạn 20 và 125); 15 trường hợp còn lại giữ nguyên điều kiện. Chú thích «???», «🔥🔥» vẫn được kiểm đủ điều kiện cũ (tiền tố, giới hạn, NFC, một dòng), đi cùng một alt có chữ.
4. Nếu sau này code lại nhận «???», nhánh `pytest.raises` sẽ hỏng, nên test vẫn bắt được quay lui.

Ghi chú quy trình: chỉnh này nằm ngoài phần «gỡ xfail» phiếu cho phép, nhưng Thợ Máy đã nêu rõ ở Rủi ro mục 1 và tôi là người viết test này, nên tôi nhận. Phần kiểm chú thích vô nghĩa ra đúng tiền tố đã có test riêng của Thợ Máy (`test_caption_without_any_letter_is_left_empty`, `test_ai_caption_with_only_prefix_and_symbols_is_just_the_prefix`).

## Lỗi và ghi nhận

| Mã | Mức | Mô tả | Ai sửa |
|---|---|---|---|
| SL-T068-1 | Thấp | Tiền tố AI tự viết **không dấu**, **nối bằng gạch**, **thiếu ngoặc quanh «AI»** hay **gọi khác** không được nhận ra, code ghép thêm tiền tố chuẩn nên «minh họa» bị lặp: «Minh họa minh hoa cửa cuốn», «Minh họa MINH HOA: cửa cuốn», «Minh họa minh-họa cửa cuốn», «Minh họa tranh minh họa cửa cuốn», chú thích «Ảnh minh họa (AI): AI: ray…». Alt chỉ có tiền tố như vậy («Minh hoa», «Tranh minh họa») thành «Minh họa minh hoa», không mô tả gì mà vẫn được nhận (cùng loại SL-T062-1). Có từ trước T-068 (`main` cho kết quả y hệt) | Thợ Máy (`_AI_PREFIX`, `alt.py:347-350`) |
| SL-T068-2 | Thấp | Tiền tố trong **dấu Markdown khác `*`** (`` ` ``, `_`, `__`) hay sau **dấu đầu dòng** («- », «1. », «• ») không được nhận ra: «Minh họa `Minh họa` cửa cuốn», «Minh họa - Minh họa cửa cuốn», chú thích «Ảnh minh họa (AI): - Ảnh minh họa (AI): ray…». Alt chỉ có tiền tố như vậy («- Minh họa», «1. Minh họa») thành «Minh họa - Minh họa», «Minh họa 1. Minh họa»: không mô tả gì mà vẫn được nhận; chạy lại `clean_suggestion` trên chính kết quả đó thì báo lỗi. Có từ trước T-068 | Thợ Máy (`_WRAPPERS`, `alt.py:353-356`) |
| SL-T068-3 | Thấp | Chú thích ảnh AI với `caption_max_chars` 20–21 (bộ đọc cho phép từ 20): tiền tố «Ảnh minh họa (AI): » chiếm 19 ký tự, thân còn 1–2 ký tự nên bị cắt giữa chữ: «Ảnh minh họa (AI): r», «Ảnh minh họa (AI): cử». Thợ Máy đã nêu (Rủi ro mục 3); có từ trước T-068. Chỉ nâng mức thấp nhất trong `config/` thì chưa đủ (hàm vẫn nhận 20); nên sửa trong code | Thợ Máy (`_with_prefix`, `alt.py:404-410`) |

### Cách tái hiện

Cả 3 lỗi tái hiện bằng `clean_suggestion` với `AltSuggestion` giả (không gọi AI), có test `xfail(strict=True)` trong `tests/test_soi_loi_t068.py`.

- **SL-T068-1** (`test_sl_t068_1_unaccented_or_renamed_prefix_is_written_once`, 5 trường hợp; `test_sl_t068_1_alt_that_is_only_such_a_prefix_is_refused`, 3 trường hợp):
  `clean_suggestion(AltSuggestion(alt="Minh hoa cửa cuốn", caption="Anh minh hoa (AI): ray dưới bị mòn"), ai_generated=True)`.
  Mong đợi: alt «Minh họa cửa cuốn», chú thích «Ảnh minh họa (AI): ray dưới bị mòn». Thực tế: «Minh họa minh hoa cửa cuốn», «Ảnh minh họa (AI): anh minh hoa (AI): ray dưới bị mòn». Với `alt="Minh hoa"`: mong đợi `AIError` «AI không viết được alt»; thực tế alt «Minh họa minh hoa». Gợi ý sửa: so tiền tố trên bản đã bỏ dấu (như bộ lọc nhãn `[CẦN XÁC NHẬN]` của T-032), nhận «-», «_» giữa hai chữ, «AI» không ngoặc sau tiền tố, và thêm «tranh», «hình vẽ» vào nhóm chữ đứng trước «minh họa».
- **SL-T068-2** (`test_sl_t068_2_markdown_or_bulleted_prefix_is_written_once`, 6 trường hợp; `test_sl_t068_2_alt_that_is_only_such_a_prefix_is_refused`, 5 trường hợp):
  `clean_suggestion(AltSuggestion(alt="- Minh họa cửa cuốn", caption="- Ảnh minh họa (AI): ray dưới bị mòn"), ai_generated=True)`.
  Mong đợi: «Minh họa cửa cuốn», «Ảnh minh họa (AI): ray dưới bị mòn». Thực tế: «Minh họa - Minh họa cửa cuốn», «Ảnh minh họa (AI): - Ảnh minh họa (AI): ray dưới bị mòn». Với `alt="- Minh họa"`: mong đợi `AIError`; thực tế alt «Minh họa - Minh họa». Gợi ý sửa: thêm `` ` `` và `_` vào `_WRAPPERS`; bỏ dấu đầu dòng («- », «* », «• », «1. ») ở đầu chữ AI viết trước khi tìm tiền tố.
- **SL-T068-3** (`test_sl_t068_3_ai_caption_body_is_never_a_cut_word`, 4 trường hợp):
  `clean_suggestion(AltSuggestion(alt="Cửa cuốn", caption="ray dưới bị mòn"), ai_generated=True, caption_max_chars=20)`.
  Mong đợi: «Ảnh minh họa (AI)» (chú thích được phép chỉ có tiền tố; không đủ chỗ cho một chữ trọn thì bỏ phần thân). Thực tế: «Ảnh minh họa (AI): r»; ở 21: «Ảnh minh họa (AI): ra»; chú thích «cửa cuốn» ra «…: c», «…: cử». Gợi ý sửa: trong `_with_prefix`, nếu `_cut` phải cắt giữa chữ (phần thân không có dấu cách trong chỗ còn lại) thì với chú thích chỉ trả tiền tố. Alt không áp được cách này (alt không được rỗng), nên giữ như cũ.

Lý do hỏng thật của cả 23 trường hợp (chạy `--runxfail`) có ở mục Bằng chứng.

### Gợi ý (không phải lỗi, không có test xfail)

- **G1 · Dấu câu ở đầu phần thân không được bỏ khi AI không viết tiền tố.** «- cửa cuốn», «... cửa cuốn», «: cửa cuốn», «— cửa cuốn» ra «Minh họa - cửa cuốn», «Minh họa ... cửa cuốn»…; chạy lại `clean_suggestion` thì ra «Minh họa cửa cuốn» (kết quả không ổn định khi lọc lại). Dấu nối lạ sau tiền tố cũng còn: «Minh họa → cửa cuốn», «Minh họa ‐ cửa» (U+2010), «Minh họa ― cửa», «Minh họa ~ cửa». Ít gặp; nếu sửa SL-T068-2 thì Thợ Máy có thể bỏ luôn nhóm `_AFTER_PREFIX` ở đầu phần thân ảnh AI.
- **G2 · Ngoặc lệch còn sót.** ««Minh họa” cửa cuốn» ra «Minh họa ” cửa cuốn»; «(Minh họa cửa cuốn (2 cánh))» ra «Minh họa cửa cuốn (2 cánh))». Chỉ là thẩm mỹ.
- **G3 · Ký tự rộng 0 giữa tiền tố.** «Minh\u200bhọa cửa cuốn»: bộ lọc bỏ ký tự rộng 0 nên hai chữ dính thành «minhhọa», alt ra «Minh họa minhhọa cửa cuốn». AI gần như không viết vậy; ghi lại cho đủ.
- **G4 · Thời gian chạy tăng nhanh với chữ AI cực dài.** Vì nay bỏ tiền tố trên chữ chưa cắt, `_strip_ai_prefix` chạy trên toàn bộ chữ AI trả về: «Minh họa » lặp 1.000 lần (9.000 ký tự) mất 0,04 giây, 20.000 lần (180.000 ký tự) 0,69 giây, 60.000 lần (540.000 ký tự) 27 giây. Với `max_tokens = 2000` của `[tasks.alt]` (`config/ai.toml`), chữ AI trả về chỉ vài nghìn ký tự, nên không phải lỗi; nếu sau này tăng `max_tokens` rất lớn thì nên cắt thô (ví dụ 4 × `max_chars`) trước khi bỏ tiền tố.
- **G5 · Dấu «<» đứng riêng còn trong alt.** «cửa < 2m», «<cửa cuốn» giữ nguyên «<» (bộ lọc chỉ bỏ thẻ HTML trọn), cả ảnh thật lẫn ảnh AI. Có từ T-050, không thuộc T-068. Nhắc cho T-056 / Giai đoạn 5: khi ghi alt vào thuộc tính HTML phải thoát ký tự (`html.escape(..., quote=True)`), không trông vào bộ lọc này.

## Bằng chứng

```
$ git pull --ff-only            # đầu phiên, trong wt-T-068
Already up to date.             # HEAD 69b9f31

$ git diff origin/main...HEAD -- tests/test_soi_loi_t062.py
# 3 test SL-T062: chỉ đổi dòng @pytest.mark.xfail(...) thành chú thích «Thợ Máy T-068 đã sửa: gỡ dấu xfail»
# test C6: thêm 7 dòng (nhánh «không có chữ hay số» → pytest.raises(AIError, match=EMPTY_ALT))

$ uv run pytest tests/test_soi_loi_t062.py -q -p no:cacheprovider -k "sl_t062 or prefix" -rfEX
38 passed, 46 deselected in 4.63s                 # 18 SL-T062 + 19 C6 + 1 ảnh thật

$ uv run pytest tests/test_soi_loi_t068.py -q -p no:cacheprovider -k sl_t068 --runxfail   # lý do hỏng thật
E   + Minh họa minh hoa cửa cuốn          E   + Minh họa MINH HOA: cửa cuốn       # SL-T068-1
E   + Minh họa minh-họa cửa cuốn          E   + Minh họa tranh minh họa cửa cuốn
E   + Minh họa hình vẽ minh họa cửa cuốn  E   Failed: DID NOT RAISE AIError (3 lần)
E   + Minh họa `Minh họa` cửa cuốn        E   + Minh họa _Minh họa_ cửa cuốn      # SL-T068-2
E   + Minh họa __Minh họa__: cửa cuốn     E   + Minh họa - Minh họa cửa cuốn
E   + Minh họa 1. Minh họa: cửa cuốn      E   + Minh họa • Minh họa cửa cuốn
E   Failed: DID NOT RAISE AIError (5 lần)
E   assert ('r' == '' …   ('ra' …   ('c' …   ('cử' …                              # SL-T068-3
23 failed, 140 deselected in 2.13s

$ uv run python <script so sánh, ngoài repo: alt.py của origin/main nạp thay module>
# 17 kiểu của SL-T068-1, -2 và G1: main và T-068 cho kết quả y hệt → có từ trước, không phải T-068 làm hỏng

$ uv run python <script thử ngẫu nhiên C6, ngoài repo, seed 68>
ok 56336 err 3664
# 60.000 cặp alt/chú thích: 0–3 tiền tố lấy từ 21 kiểu (có dấu, không dấu, NFD, NBSP, ký tự rộng 0,
# gạch nối, «(AI)», «Tranh», «Ảnh AI»), 23 kiểu ngoặc mở (có cả `, _, „, 「, 【, {, <, ****),
# 22 kiểu dấu nối (có \n, \t, →, ‐, »); thân có HTML, link Markdown, </du_lieu_tham_khao>, \u202e,
# NUL, ESC, emoji, chữ số, chữ Hán, Kirin, chữ rất dài; max_chars 20–500, caption_max_chars 20–500.
# Lỗi C6 (thiếu tiền tố), quá giới hạn, nhiều dòng, sai NFC, alt chấm cuối, alt thân không chữ, lỗi lạ: 0
# Mọi lần báo lỗi: đúng câu «AI không viết được alt…».
# Còn lại (không phải C6): «minh họa» lặp 28864 lần ở alt, 15649 ở chú thích, chỉ với kiểu ngoài danh sách
# phiếu (SL-T068-1, -2); chạy lại cho kết quả khác 1710 lần (G1, SL-T068-2); «<» đứng riêng 2802 lần, đều
# do đầu vào có «<» không đóng (G5). Ảnh thật 20.000 lần: 0 lần thêm tiền tố.
```

Test liên quan theo phiếu và theo giao việc (không chạy toàn bộ; Chỉ Huy chạy toàn bộ trên Windows khi gộp):

```
$ uv run pytest tests/test_t062_alt_prompt.py tests/test_soi_loi_t062.py tests/test_soi_loi_t068.py \
    tests/test_ai_images.py tests/test_soi_loi_t050.py -q -p no:cacheprovider -rfEX
912 passed, 38 xfailed in 88.67s (0:01:28)        # 17:07:00 → 17:08:32 (+07:00), commit 59d7574
                                                  # 0 hỏng, 0 XPASS; 38 xfail = 23 SL-T068 mới + 15 dấu cũ
                                                  # của tests/test_soi_loi_t050.py

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check tests/test_soi_loi_t068.py
1 file already formatted
```

## Đối chiếu tiêu chí xong (mức rút gọn)

- [x] 3 lỗi SL-T062-1 → 3 sửa thật, `xfail` gỡ đúng, thân test không đổi (mục Kết quả kiểm, dòng 1)
- [x] Ý kiến về test C6 đã chỉnh: **xác nhận**, có lý do (mục riêng ở trên)
- [x] Thử lách tiền tố, alt chỉ số, chữ hệ khác, `max_chars` 20 và lớn, chú thích ảnh AI và ảnh thật (mục Kết quả kiểm, dòng 3–7)
- [x] Lỗi mới có test `xfail(strict=True)` mã SL-T068-1 → 3 trong `tests/test_soi_loi_t068.py`; không sửa code ứng dụng
- [x] Test liên quan qua, `uv run ruff check .` sạch (mục Bằng chứng)
- [x] Báo cáo nộp tại `docs/team/reports/T-068-soi-loi.md`

## Rủi ro và điểm cần chú ý

- Cả 3 lỗi mới đều làm **lặp chữ hoặc cụt chữ**, không làm mất tiền tố. Người dùng vẫn duyệt từng alt ở T-056 trước khi dùng. Khả năng gặp (suy luận, chưa thử với AI thật): SL-T068-2 cao hơn cả (AI hay trả chữ có định dạng Markdown, dấu đầu dòng); SL-T068-1 thấp (lời dặn đã đưa sẵn «Minh họa» có dấu); SL-T068-3 chỉ khi ai đó hạ `caption_max_chars` xuống 20–21 (mặc định 200).
- Script thử ngẫu nhiên và so sánh với `main` nằm ngoài repo, không thêm vào test (như Thợ Máy và Lá Chắn T-062 đã làm); test cố định nằm trong `tests/test_soi_loi_t068.py`.
- Không gọi AI thật, không gọi mạng, không dùng khóa thật.

## Đề xuất

- **Chỉ Huy:** chuyển T-068 sang Lá Chắn rút gọn (C6). Gom SL-T068-1 → 3 vào một phiếu dọn nhỏ cho Thợ Máy (`seo_app/images/alt.py` và gỡ `xfail` trong `tests/test_soi_loi_t068.py`), không cần chặn T-056; nên làm trước khi bật thật việc viết alt cho người dùng.
- **Thợ Máy (phiếu dọn sau):** nếu sửa SL-T068-2 thì xem luôn G1 (bỏ dấu câu đầu phần thân ảnh AI), để `clean_suggestion` chạy lại không đổi kết quả.
- **Họa Sĩ / Thợ Máy ở T-056, Giai đoạn 5:** G5 (thoát ký tự khi ghi alt vào HTML).
- **Ngòi Bút:** đồng ý đề xuất của Thợ Máy về `caption_max_chars` (nâng mức thấp nhất hoặc ghi chú 19 ký tự tiền tố), làm thêm cho SL-T068-3 chứ không thay sửa code.

## Câu hỏi cho chủ dự án

Không có.

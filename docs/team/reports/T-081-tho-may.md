# Báo cáo T-081 · Bỏ dấu «\» sót ở alt, chú thích ảnh AI (SL-T071-1)

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-081](../tickets/T-081-dau-gach-cheo-alt-anh-ai.md) |
| Ngày nộp | 2026-10-23 |
| Kết quả | Hoàn thành (yêu cầu 1–4). Chọn cách 1 của phiếu: bỏ dấu «\» ngay sau «]» của tiền tố vừa bỏ |

## Tóm tắt (cho chủ dự án)

- Khi AI viết mô tả ảnh minh họa kiểu «[Minh họa]: Cổng inox…», alt và chú thích lên website nay là «Minh họa cổng inox…» và «Ảnh minh họa (AI): cổng…», không còn dấu «\» thừa như trước (`Minh họa \: Cổng inox…`). Đủ 7 biến thể Soi Lỗi nêu, thêm dạng «[Minh họa](…)».
- Chặn shortcode, chặn link giữ nguyên: mọi dấu «[» «]» vẫn được đổi thành mã ký tự trước khi gửi WordPress. Ảnh thật không đổi gì. Dấu «\» do AI tự gõ ở chỗ khác vẫn giữ như cũ.
- Chỉ sửa 2 dòng code trong `seo_app/images/alt.py` (cộng chú thích). Thử trên 102.960 câu mẫu: chỉ đổi đúng những câu từng dính dấu «\» thừa.
- Một điểm nhỏ cần biết (không phải lỗi mới): câu kỳ quặc kiểu «[Minh họa]: [Mẹo]: cổng» (nhãn thứ hai rồi đúng **một** chữ) nay báo «AI không viết được alt, bấm thử lại», giống hệt cách phần mềm vẫn xử lý «Minh họa: [Mẹo]: cổng» từ trước. Chi tiết ở mục «Rủi ro».

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `seo_app/images/alt.py` | `_LINK_ESCAPES` (`:363`) và 2 dòng trong `_strip_ai_prefix` (`:391-392`): bỏ ngoặc đóng tận cùng bằng «]» của tiền tố mà ngay sau là `\:`, `\[`, `\(` thì bỏ luôn dấu «\»; thêm 2 câu vào docstring |
| `tests/test_t081_alt_gach_cheo.py` | Mới: 48 ca (biến thể của phiếu, tổ hợp 552 chuỗi, «\» ở chỗ khác, ảnh thật, gửi site giả, shortcode/link sau khi bỏ «\») |
| `tests/test_soi_loi_t071.py` | Gỡ `@pytest.mark.xfail(...)` của `test_sl_t071_1_…` (`:430`): xóa đúng 5 dòng dấu, thân test không đổi |
| `docs/team/reports/T-081-tho-may.md` | Báo cáo này |

Không sửa `seo_app/images/html.py`, `seo_app/wordpress/**`, `app/**`, `config/**`.

## Cách sửa và lý do chọn

**Nguyên nhân** (Soi Lỗi T-071): `clean_ai_text` → `escape_link_syntax` thêm «\» ngay sau «]» khi theo sau là «:» (nhãn đầu dòng), «[» hay «(» (`[Minh họa]\: Cổng`). `_strip_ai_prefix` bỏ tiền tố cùng ngoặc đóng «]» nhưng để lại dấu «\»; mất «]» rồi thì cả `unescape_link_syntax` lẫn bước gỡ `]\:` của T-071 (`html.py`) đều không nhận ra nó nữa.

**Sửa (cách 1 của phiếu):** trong `_strip_ai_prefix`, sau khi bỏ ngoặc đóng, nếu ngoặc đóng kết thúc bằng «]» và phần còn lại mở đầu bằng `\:`, `\[` hay `\(` thì bỏ dấu «\» đó, rồi mới bỏ dấu câu như cũ. Điều kiện này đúng bằng chỗ `plain_image_text` sẽ gỡ nếu «]» còn đó (`unescape_link_syntax` gỡ `]\[`, `]\(`; `_LABEL_COLON_ESCAPE` gỡ `]\:` ở mọi chỗ trong dòng), nên kết quả ảnh AI khớp cách phần mềm đã xử lý cùng chuỗi ở ảnh thật.

**Vì sao không chọn cách 2 (bỏ tiền tố trên chữ chưa escape):**
- Phải `unescape_link_syntax` **cả câu** trước khi bỏ tiền tố. Lúc lọc lại, `strip_markdown_links` thấy lại những link mà escape đã vô hiệu ở **giữa câu** (ví dụ `[x]\(y)` thành `[x](y)` rồi bị cắt còn «x»), tức là đổi nghĩa phần thân, trái yêu cầu 3 («dấu «\» ở chỗ khác giữ nguyên ý nghĩa»).
- Nếu bỏ tiền tố trên chữ thô (trước cả `clean_ai_text`) thì tiền tố nằm trong thẻ HTML (`<b>Minh họa</b> cửa cuốn`, ca của `tests/test_soi_loi_t062.py:469`) không còn được nhận, đổi hành vi đã kiểm ở T-062.
- Cách 1 chỉ đụng đúng một ký tự ở đúng một chỗ, dễ soát.

**Ví dụ (ảnh AI, chữ gửi WordPress sau `plain_image_text`):**

| AI viết | Trước | Sau |
|---|---|---|
| `[Minh họa]: Cổng inox 2 cánh` | `Minh họa \: Cổng inox 2 cánh` | `Minh họa cổng inox 2 cánh` |
| `[Ảnh minh họa (AI)]: cổng sau khi sơn` (chú thích) | `Ảnh minh họa (AI): \: cổng sau khi sơn` | `Ảnh minh họa (AI): cổng sau khi sơn` |
| `[Minh họa]:Cổng inox` | `Minh họa \:Cổng inox` | `Minh họa cổng inox` |
| `[Minh họa][cổng sắt] sơn đen` | `Minh họa \[cổng sắt] sơn đen` | `Minh họa [cổng sắt] sơn đen` |
| `[Minh họa](cổng sắt) sơn đen` | `Minh họa \(cổng sắt) sơn đen` | `Minh họa (cổng sắt) sơn đen` |
| `[Minh họa]: cổng \ rào` (AI gõ «\») | `Minh họa \: cổng \ rào` | `Minh họa cổng \ rào` |
| `[Minh họa]\\: cổng` (AI gõ «\\») | `Minh họa \\: cổng` | không đổi |

Dạng «[»: ngoặc vuông của phần thân («[cổng sắt]») giữ nguyên là chữ, như khi AI viết «[Minh họa] [cổng sắt] sơn đen» (có dấu cách); người đọc thấy «[cổng sắt]», WordPress nhận `&#91;cổng sắt&#93;`.

## Kiểm từng yêu cầu

| Yêu cầu | Kết quả | Bằng chứng |
|---|---|---|
| 1. Bỏ «\» khi bỏ ngoặc đóng của tiền tố | **Đạt** | `alt.py:391-392`. Thử đột biến (bên dưới): bỏ 2 dòng này → 42 ca hỏng |
| 2. Đủ biến thể, cả `clean_suggestion` lẫn `DraftImage(…, tags=ImageTags(source=SOURCE_AI))` gửi site giả | **Đạt** | `test_tien_to_ngoac_vuong_roi_hai_cham_khong_con_gach_cheo` (9 dạng tiền tố gồm 5 dạng của phiếu, «(AI)», ngoặc lồng `[*…*]`, `[«…»]`, `[(…)]` × «: » và «:» = 18 ca): alt đúng `Minh họa cổng inox 2 cánh sơn tĩnh điện`, chú thích đúng `Ảnh minh họa (AI): cổng sau khi sơn`, bằng kết quả của «Minh họa: …», chạy lại không đổi. `…_roi_ngoac_mo_…` (6 ca dạng «[», «(», tiền tố lặp). `…_bi_cat_do_dai_…` (cắt 30/40 ký tự). `test_moi_to_hop_…`: 12 kiểu ngoặc mở × 6 tiền tố × 8 chỗ nối (552 chuỗi): không «\», đúng một tiền tố. `test_gui_site_gia_…` (5 ca, đủ 7 dạng của phiếu): `alt` trong `<img>`, `<figcaption>` như trình duyệt đọc, `alt_text`, tiêu đề `[AI] …`, `caption` gửi REST đúng chữ |
| 3. Không nới T-061, T-062; «\» chỗ khác giữ nguyên; ảnh thật không đổi | **Đạt** | Mọi chuỗi JSON gửi site giả không có «\», «[», «]» trần (`test_gui_site_gia_…`, `test_bo_gach_cheo_khong_mo_lai_shortcode_hay_link` 8 ca: `[code_snippet id=1]`, `[/code_snippet]`, `[[code_snippet …]]`, `[embed]…[/embed]`, link Markdown, thẻ `<a>` ngay sau tiền tố: phần thân vẫn qua `clean_ai_text` lần nữa, rồi `escape_shortcodes`). `test_gach_cheo_o_cho_khac_giu_nguyen` (6 ca). `test_anh_that_khong_doi` (3 ca). So 102.960 chuỗi bản cũ/mới: ảnh thật khác nhau **0**, «[» «]» trần **0** |
| 4. Gỡ `xfail` 2 ca SL-T071-1 | **Đạt** | `git diff 1d1e53e -- tests/test_soi_loi_t071.py`: chỉ 5 dòng `@pytest.mark.xfail(…)` bị xóa. 2 ca qua (trong 145 ca của file) |

## So bản cũ, bản mới trên nhiều chuỗi

Script `diff_old_new.py` (ghi chú chung của các phiên, thư mục `T-081-tho-may-scripts/`) dựng 102.960 chuỗi: 13 kiểu ngoặc mở × 10 tiền tố × 4 dấu trước ngoặc đóng × 22 kiểu nối (có `\:`, `\\:`, `[x]`, `(x)`, `(AI):`, «[Mẹo]: », địa chỉ web…) × 9 phần thân (có «\» AI gõ, «[sắt]», shortcode, rỗng). Chạy `clean_suggestion` bản `1d1e53e` và bản mới, so chữ sau `plain_image_text` (lượt cuối, có bước kiểm «lỗi mới», xong trước 13:30; mỗi lượt khoảng 5 phút 30 giây):

```
tổng 102960 chuỗi; ảnh thật khác nhau: 0; «[» «]» trần sau lọc: 0
giống: 79320
gỡ «\»: 22760
lỗi mới: 880
hết lỗi: 0
khác: 0
```

- **gỡ «\»** (22.760): bản cũ có dấu «\» thừa, bản mới ít đúng một dấu «\» ở mỗi trường.
- **lỗi mới** (880): đều là chuỗi sau khi bỏ tiền tố còn «[nhãn]: một-chữ» (ví dụ «[Minh họa]: [Mẹo]: cổng»). Script kiểm từng ca: bản **cũ** với dạng không ngoặc vuông «Minh họa [Mẹo]: cổng» cũng báo lỗi y vậy (nếu không, ca đó bị xếp vào «khác», và «khác» = 0). Xem mục «Rủi ro».
- **khác**: 0.

## Thử đột biến (test có bắt được không)

`run_mutations.sh` (cùng thư mục): chép nhánh bằng `git archive HEAD` vào thư mục nháp, sửa dòng sửa của T-081, chạy `tests/test_t081_alt_gach_cheo.py` + `tests/test_soi_loi_t071.py`; kiểm `seo_app` được nạp từ bản sao ở cả 6 lượt (13:35–13:36).

| Đột biến | Kết quả |
|---|---|
| Không đổi gì | 193 passed |
| Bỏ hẳn bước gỡ «\» | 42 failed |
| Chỉ gỡ trước «:» | 11 failed |
| Không gỡ trước «(» | 2 failed |
| Gỡ cả khi ngoặc đóng không phải «]» | 1 failed (`«Minh họa»\: cổng` phải giữ «\») |
| Gỡ mọi «\» đứng sau «]» | 1 failed (`[Minh họa]\\: cổng` phải giữ) |

## Bằng chứng

Máy Windows 11 Pro (10.0.26300) của chủ dự án, Python 3.12, worktree `wt-T-081`, nhánh `team/T-081` (gốc `1d1e53e`). Máy đang chạy song song các agent khác.

```
$ uv run pytest -q -p no:cacheprovider -rxXfs tests/test_soi_loi_t071.py tests/test_t062_alt_prompt.py \
    tests/test_soi_loi_t062.py tests/test_soi_loi_t054.py tests/test_soi_loi_t068.py \
    tests/test_shortcode_t061.py tests/test_soi_loi_t061.py tests/test_wordpress_images.py \
    tests/test_ai_images.py tests/test_t081_alt_gach_cheo.py
(2026-10-23 13:36:56 → 13:37:59)
1358 passed, 29 xfailed in 57.29s

$ uv run ruff check .
All checks passed!
```

- 10 file: 9 file lời giao và file mới của phiếu. 0 hỏng, 0 XPASS. Lượt trước đó (13:33:01 → 13:35:20, máy bận hơn) cùng kết quả `1358 passed, 29 xfailed in 132.19s`.
- 29 `xfailed` đều là lỗi cũ, không liên quan: SL-T061-1 (4 ca), SL-T061-2 (2 ca) trong `tests/test_soi_loi_t061.py` (thuộc T-060); SL-T068-1 (8), SL-T068-2 (11), SL-T068-3 (4) trong `tests/test_soi_loi_t068.py` (gom phiếu dọn theo Lá Chắn T-068). Không ca nào thành XPASS.
- Riêng `tests/test_soi_loi_t071.py` + `tests/test_t081_alt_gach_cheo.py` (13:30–13:32): `193 passed` (145 + 48).
- `uv run ruff format --check` trên 3 file sửa: đã đúng định dạng.
- Sau lượt chạy trên, tôi chỉ sửa câu chú thích ở `alt.py:359-362` (không đổi code); chạy lại `tests/test_t081_alt_gach_cheo.py`, `test_soi_loi_t071.py`, `test_t062_alt_prompt.py`, `test_soi_loi_t062.py`, `test_soi_loi_t068.py`: `615 passed, 23 xfailed in 31.16s` (23 xfail là SL-T068-1 → -3), `ruff check .` sạch.
- Quét bí mật: chép `alt.py`, 2 file test, báo cáo này và `git diff 1d1e53e` của nhánh vào thư mục nháp, thêm một file mồi có chữ tiếng Việt (một khóa AWS giả, một dòng mật khẩu giả), chạy `PYTHONUTF8=1 uvx --offline detect-secrets scan --all-files .`: mồi **bắt đủ 2/2**, các file của phiếu: **0**. Đã xóa thư mục nháp.
- Script thử (không commit), thư mục ghi chú chung `T-081-tho-may-scripts/`: `probe.py` (in alt, chú thích 35 chuỗi; `probe_before.log`, `probe_after.log`), `diff_old_new.py` + `diff_old_new.log`, `check_new_errors.py`, `probe_invisible.py` + `.log`, `run_mutations.sh` + `mutations.log`. Chạy trong worktree bằng `PYTHONUTF8=1 uv run python <script>`; `diff_old_new.py` cần bản cũ: `git show 1d1e53e:seo_app/images/alt.py > <thư mục script>/old_alt.py`.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1–4 (mục «Kiểm từng yêu cầu»)
- [x] Test liên quan qua, `uv run ruff check .` sạch (mục «Bằng chứng»); toàn bộ test do Chỉ Huy chạy khi gộp
- [x] Có test cho phần logic mới: `tests/test_t081_alt_gach_cheo.py` (48 ca)
- [x] Báo cáo nộp tại `docs/team/reports/T-081-tho-may.md`

## Rủi ro và điểm cần chú ý

- **«[Minh họa]: [nhãn]: một-chữ» nay báo lỗi thay vì ra alt xấu.** Sau khi bỏ tiền tố, phần thân «[Mẹo]: cổng» được lọc lại (thiết kế T-062: lọc lại sau khi bỏ tiền tố); `clean_ai_text` coi «[nhãn]: một-chữ» ở đầu dòng là dòng khai báo link Markdown và xóa, nên alt rỗng → `AIError` «AI không viết được alt cho ảnh này. Bấm thử lại hoặc tự gõ alt.». Trước T-081 câu này ra `Minh họa \: [Mẹo]: cổng`. Đây là cách phần mềm **đã** xử lý «Minh họa: [Mẹo]: cổng», «[Minh họa] [Mẹo]: cổng» và cả ảnh thật «[Mẹo]: cổng» từ trước (kiểm bằng `check_new_errors.py` trên bản cũ). Hướng an toàn (không gửi gì lên website), người dùng bấm thử lại hay tự gõ. Phần thân nhiều chữ hơn («[Minh họa]: [Mẹo]: cổng inox 2 cánh») vẫn ra alt bình thường.
- Dấu «\» AI tự gõ ngay sau «]» của tiền tố, đứng trước «:», «[», «(» («[Minh họa]\: cổng») không phân biệt được với dấu do `escape_link_syntax` thêm (hai chuỗi giống hệt nhau sau khi lọc), nên cũng bị bỏ. Trong Markdown `\:` nghĩa là «:», và ảnh thật xử lý chuỗi này y như vậy (`plain_image_text` gỡ), nên không đổi ý nghĩa.
- Dạng xấu **khác**, không có «\», vẫn như trước (ngoài phạm vi phiếu): «[Minh họa cổng inox][x]» (ngoặc bọc cả câu rồi thêm «[x]») ra `Minh họa cổng inox][x]`. Không mở được link hay shortcode («[» «]» vẫn thành mã ký tự).

## Đề xuất

1. (Ghi nhận, không phải lỗi của T-081) `clean_ai_text` xóa cả dòng «[nhãn]: một-chữ» (coi là khai báo link Markdown), ảnh hưởng mọi alt, chú thích AI viết kiểu «[Ghi chú]: Cổng» (đúng một chữ), cả ảnh thật: ra lỗi «AI không viết được alt». Hướng an toàn; nếu Chỉ Huy thấy cần, gom vào phiếu dọn lỗi Thấp của phần alt (cùng SL-T068-1 → -3), không chặn T-056.
2. Soi Lỗi nên thử thêm theo cách của mình: tiền tố trong ngoặc vuông kèm ký tự vô hình, dấu cách quanh «]», chữ AI nhiều dòng. Tôi đã thử 49 chuỗi như vậy (`probe_invisible.py`: 8 ký tự vô hình × 5 vị trí, dấu cách, tab, xuống dòng `\n`, `\r\n`): 0 chuỗi còn «\», 0 lỗi; ký tự vô hình bị `normalize_meta` bỏ trước khi escape nên «\» luôn đứng sát sau «]».

## Câu hỏi cho chủ dự án

Không có.

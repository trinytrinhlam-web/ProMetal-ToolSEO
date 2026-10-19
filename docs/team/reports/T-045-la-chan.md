# Biên bản bảo mật T-045 · Bộ lọc hồ sơ: sửa 3 lỗi Thấp sau T-043

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (**Opus tạm**: tài khoản không dùng được Fable, chủ dự án đã duyệt chạy tạm). **Sau 01/11 phải kiểm lại bằng Fable.** |
| Phiếu được kiểm | [T-045](../tickets/T-045-loc-ho-so-theo-doi-sau-t043.md) |
| Phạm vi | `git diff origin/main...team/T-045` (gốc `b5ff3b3`, đầu nhánh lúc kiểm `f23a78b`): `seo_app/content/rules.py`, `tests/test_profile_tag_t032.py` (1 dòng xóa), `tests/test_soi_loi_t043.py` (bỏ 3 `xfail`), 2 file test mới, 2 báo cáo. `rules.py` trên `origin/main` (`f0f515f`) trùng gốc `b5ff3b3` |
| Ngày | 2026-10-19 |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** |

## Tóm tắt (cho chủ dự án)

Bản sửa an toàn. Phần hồ sơ thật mà AI thấy **giống hệt** bản đang chạy. Tôi tự thử 300.000 hồ sơ
ngẫu nhiên: không lần nào bản mới để lộ một dòng có nhãn `[CẦN XÁC NHẬN]`, hay chữ của một ý hoặc
một mục có nhãn, trong khi bản cũ giấu được. Bộ lọc vẫn chạy nhanh với đầu vào xấu cỡ 1 MB. Việc
Thợ Máy bỏ 1 ca test là đúng: ca đó ghim chính lỗi cần sửa, và nay đã được kiểm theo chiều ngược
lại. Còn 2 kiểu gõ nhãn rất hiếm vẫn lọt, nhưng **đã lọt từ trước** nên bản này không làm tệ hơn.
Điều kiện duy nhất: Chỉ Huy mở một phiếu theo dõi mức Thấp cho 2 lỗi đó. T-045 được gộp ngay, không
cần chờ phiếu đó.

## Lỗi phát hiện

Không có lỗi Nghiêm trọng, Cao hay Trung bình. Không có lỗi nào do T-045 gây ra.

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| 1 | Thấp · không chặn · có từ trước | **SL-T045-1** (Soi Lỗi; Lá Chắn tái hiện độc lập). Nhãn trên **tiêu đề** vắt qua **3 dòng**: tiêu đề chờ chỉ ghép với đúng 1 dòng kế. Lá Chắn tìm thêm **biến thể với tiêu đề lỡ thụt lề**, trong đó chữ nằm ngay trên dòng cuối của nhãn cũng lọt. | `seo_app/content/rules.py:146-170` (nhánh `pending`), `:208-212` | `## 7 [CẦN` / `XÁC` / `NHẬN]` / `- BIMAT` / `## 8` → cả 6 dòng tới AI (nhánh và `main` như nhau). Biến thể: `- a` / `  ## 7 [CẦN` / `  XÁC` / `  NHẬN] BIMAT` / `- ok` → `  NHẬN] BIMAT` tới AI (nhánh và `main` như nhau). Hậu quả: thông tin chưa xác nhận (ví dụ giá chưa chốt) có thể vào prompt, AI viết vào bản nháp. Bài vẫn là nháp, người dùng đọc trước khi đăng. Muốn lọt phải bấm Enter hai lần giữa nhãn của tiêu đề. | Theo gợi ý của Soi Lỗi: ghép mà chưa thành nhãn nhưng chuỗi ghép **vẫn kết thúc bằng nửa nhãn** thì tiếp tục chờ với chuỗi ghép, giới hạn số dòng (ví dụ 3) để giữ tuyến tính. Thêm test cho biến thể thụt lề. |
| 2 | Thấp · không chặn · có từ trước | **SL-T045-2** (Soi Lỗi; Lá Chắn tái hiện). Dòng nửa sau của nhãn tiêu đề lại kết thúc bằng nửa nhãn mới. Dòng đó bị bỏ qua (`continue`) nên không chờ tiếp; dòng `## NHẬN]` sau cùng thành tiêu đề cùng cấp và kết thúc mục đang giấu. | `rules.py:153-163` | `## 7 [CẦN XÁC` / `## NHẬN] [CẦN XÁC` / `## NHẬN]` / `- BIMAT` / `## 8` → `## NHẬN]` và `- BIMAT` tới AI (nhánh và `main` như nhau). Cùng kết quả khi dòng giữa không có `##`. Cần gõ nhầm `##` vào giữa nhãn hai lần liền. | Dòng nửa sau đã ghép thành nhãn mà chính nó kết thúc bằng nửa nhãn thì đặt lại tiêu đề chờ với dòng đó (cùng cấp `head_level`). |
| 3 | Thấp · ghi nhận, không cần sửa | Lớp Lá Chắn T-043 #2 gặp nhiều hơn vì nhãn có từ 5 ký tự lạ nay được nhận. Ý **không có nhãn** đứng ngay trước một tiêu đề lỡ thụt lề có nhãn được giữ lại; bản cũ giấu nó chỉ nhờ may. | `rules.py:183-202` | `- ok` / `  ## 7 [❗❗❗ **CẦN XÁC NHẬN**]` / `  BIMAT [CẦN XÁC NHẬN]` / `## 8` → `- ok` tới AI, tiêu đề, `BIMAT` và cả mục `## 7` bị giấu. `- ok` không có nhãn của riêng nó, nên đây **không** phải thông tin chưa xác nhận. Khớp thiết kế SL-T032-2 đã duyệt. | Không cần sửa. Muốn đổi thì đổi thiết kế SL-T032-2 (Chỉ Huy quyết). |

## Kiểm các trọng tâm Chỉ Huy giao

### A1/A3 · Fuzz độc lập so với `main`

Script riêng của Lá Chắn (scratchpad, không commit), không dùng lại script của Thợ Máy hay Soi Lỗi.
Nạp `rules.py` của `origin/main` (qua `git show`) cạnh `rules.py` của nhánh. Tài liệu ngẫu nhiên
3–12 dòng: 11 nhãn trọn (có `[❗❗❗ **CẦN XÁC NHẬN**]`, `[CẦN (XÁC NHẬN]`, `[[CẦN…`, emoji ghép, U+200B
trong nhãn, `[*****CẦN…`), 8 nửa nhãn, 6 nửa sau (có `NHẬN] [CẦN XÁC`), 8 câu thường dễ nhầm, 17 kiểu
đầu dòng (`- `, thụt lề, `## `, `  ## `, `  # `, `#x `, `##` dính chữ, `> `, `1. `, U+200B), dòng
trống. Mỗi dòng có mã riêng `Qnnn`.

Ba phép kiểm **độc lập với code bộ lọc** (mẫu nhãn tự viết theo đặc tả, bỏ dấu tự làm):

- (a) không dòng nào tới AI còn nhãn trọn (theo mẫu của Lá Chắn, của `main` và của nhánh);
- (b) ý gạch đầu dòng không thụt lề cùng các dòng nối của nó (bỏ dòng `>`, dừng ở dòng trống, tiêu
  đề, gạch đầu dòng mới, tiêu đề thụt lề) mà có nhãn thì không mã nào của ý đó tới AI;
- (c) tiêu đề thật không thụt lề có nhãn trọn thì mọi dòng tới tiêu đề thật cùng cấp hoặc cao hơn
  không tới AI.

| Lần chạy | Dòng lùi (cũ giấu, mới lộ) | Ngoài lớp #2 | Vi phạm (a) / (b) / (c) trên nhánh | Vi phạm (b) / (c) trên `main` | Dòng giấu thêm |
|---|---|---|---|---|---|
| 3 × 100.000 tài liệu (hạt giống 11, 12, 13) | 182 (145 tài liệu) | **0** | **0 / 0 / 0** | 23.077 / 15.998 | 179.121 |

- Phép kiểm (b), (c) **có tác dụng**: cùng tài liệu, bản `main` vi phạm hàng chục nghìn lần (chủ yếu
  do nhãn có từ 5 ký tự lạ, chính lỗi SL-T043-1 đã sửa). Nhánh: 0.
- 182 dòng lùi đều thuộc lớp #2 (lỗi #3 ở trên): dòng lộ không có nhãn, và trong 5 dòng sau nó có tiêu
  đề lỡ thụt lề mà nhãn hay nửa nhãn chỉ bản mới nhận. Tôi xem tay 10 tài liệu, kể cả 4 tài liệu mà
  bộ phân loại thô thứ hai (gom đoạn liền) báo "đoạn có nhãn". Cả 4 là báo nhầm của bộ phân loại: dòng
  có nhãn nằm ở **gạch đầu dòng khác** phía trên, mà gạch đầu dòng luôn mở khối mới.
- Kết luận: **không tìm thấy đường nào để chữ của một ý hay một mục có nhãn tới AI mà `main` giấu
  được.** Đường lọt còn lại (lỗi #1, #2) đã có trên `main`.

Thêm tay các ca quanh LC-T043-1 ngoài bảng mảnh fuzz, đều bị giấu trên nhánh (trên `main` đều lọt):
thụt lề bằng tab, có dòng trống giữa, có dòng `>` giữa, ý là đoạn văn thay vì gạch đầu dòng. Tiêu đề
`######` sâu nhất cũng đúng. Câu thường (`- khách cần xác nhận lịch`, `- [******] cần xác nhận`,
`- [1] cần xác nhận lịch`) vẫn giữ.

### A3 · Hồ sơ thật

```
profile file same as main: True 7800
new(wt) == main(main): True 4826 24cfa2b250174254f6adf8d8f1a047a4b3e828264b2b555c5ad85a49c1aa8439
load_rules == main: True
unconfirmed lines in output (new detector): 0
unconfirmed lines in output (old detector): 0
lines with '>' first: 0
tagged source lines present in output: []
```

Mã băm khớp số của Soi Lỗi (chuỗi UTF-8, xuống dòng `\n`). `config/business_profile.md` không đổi so
với `main` (`git diff origin/main -- config/business_profile.md`: 0 dòng).

### F3 · ReDoS

Đọc mẫu: `_LEAD_GAP = (?:[^\w\[\]()]|_)*+` (`rules.py:32`) không nhận ngoặc mở, nên mỗi điểm bắt đầu
chỉ quét tới ngoặc kế tiếp. `_GAP = (?:[^\w\])]|_)*+` (`:33`) cho ngoặc mở, nhưng nó chỉ chạy sau chữ
`CAN`/`CHUA`/`XAC`. Mỗi dải chen (không chứa chữ) đứng ngay sau đúng một chữ, nên chỉ bị quét bởi đúng
một điểm bắt đầu. Cả ba mẫu (`:32`, `:33`, `:43`) đều là **một** lớp ký tự với lượng từ chiếm hữu
`*+`/`++`, không lồng lượng từ, không quay lui. `_PARTIAL_TAG_REST` (`:45`) chạy `fullmatch` trên tối đa
64 ký tự. `_squeeze_gap` (`:262`) tuyến tính theo độ dài dải. `block_is_tagged` (`:127-134`) nhớ kết
quả. Khối chưa có nhãn chỉ dò một lần rồi bị đóng ngay (`join_block` sai, `:198`, `:201`). Vậy không
có đường nào dò lại cả khối ở mỗi dòng. Cần Python ≥ 3.11 cho `*+`; dự án yêu cầu `>=3.12`
(`pyproject.toml:6`).

Đo thời gian CPU (lần nhanh nhất trong 3 lần, mỗi lần lặp đủ 0,3 s, **xóa bộ nhớ đệm trước mỗi lời
gọi**; hàm phụ đo qua `__wrapped__`). Tỉ lệ khoảng 4 là tuyến tính, 16 là bậc hai.

| Đầu vào xấu (1 dòng) | `search` mẫu nhãn 256 KB → 1 MB | `_is_unconfirmed` | `_ends_with_partial_tag` | `_PARTIAL_GAP_RUN.sub` | `confirmed_profile` |
|---|---|---|---|---|---|
| `[[[[` | 0,011 → 0,035 s (3,2) | 3,6 | 4,0 | 4,8 | 0,13 → 0,50 s (3,8) |
| `[CAN[[[[` | 0,030 → 0,104 s (3,5) | 3,6 | 4,5 | 3,4 | 0,13 → 0,52 s (4,0) |
| `[CAN*[CAN*` | 0,016 → 0,063 s (4,0) | 3,6 | 3,9 | 4,1 | 0,13 → 0,50 s (4,0) |
| `[*(*` | 0,020 → 0,072 s (3,7) | 4,2 | 4,2 | 3,8 | 0,11 → 0,47 s (4,1) |
| `(` + `*` × n | 3,9 | 3,4 | 3,8 | 3,8 | 4,2 |
| `[CAN` + `(*` × n | 3,9 | 4,2 | 4,0 | 3,8 | 3,9 |
| `[CAN XAC` + `*` × n + `[` | 4,0 | 3,8 | 4,0 | 4,2 | 3,6 |
| `[CAN XAC [` lặp | 3,9 | 4,2 | 4,8 | 4,0 | 4,5 |
| `[CAN` + khoảng trắng × n + `XAC` | 3,7 | 4,2 | 3,8 | 4,1 | 4,0 |
| `[_` lặp | 4,8 | 3,4 | 5,0 | 4,8 | 3,4 |
| `[CAN [ [ [` | 3,6 | 4,0 | 4,2 | 4,0 | 3,8 |
| `[` + emoji ZWJ | 3,6 | 5,0 | 5,3 | 4,5 | 4,4 |
| `[CẦN XÁC` có dấu + `*` × n | 4,4 | 5,0 | 3,8 | 3,9 | 4,0 |

| `confirmed_profile`, nhiều dòng | 256 KB | 1 MB | Tỉ lệ |
|---|---|---|---|
| dòng `x N [[[[…` | 0,17 s | 0,69 s | 4,0 |
| dòng `x N [CAN*[CAN*…` | 0,18 s | 0,72 s | 4,0 |
| tiêu đề `## N [*(*…` | 0,64 s | 2,02 s | 3,1 |
| ý có nhãn + `  ## bN [CAN` (LC-T043-1) | 0,64 s | 2,52 s | 3,9 |
| `  ## bN [CAN` nối nhau, ý không nhãn | 0,67 s | 2,50 s | 3,7 |
| mục giấu + `  # xN [CAN` | 0,08 s | 0,33 s | 4,2 |
| `## N [CAN XAC` / `## NHAN]` (SL-T043-2) | 0,36 s | 1,38 s | 3,8 |
| tiêu đề nửa nhãn rồi 1 triệu dòng trống | 0,33 s | 1,47 s | 4,5 |

Mọi tỉ lệ nằm trong 3,1–5,3: **tuyến tính**. Ca chậm nhất là 2,5 s cho 1 MB, gấp khoảng 130 lần hồ sơ
thật (7,8 KB). Hồ sơ do chính chủ dự án gõ trên máy mình, không phải dữ liệu từ ngoài, nên không có
kẻ tấn công nào đưa được 1 MB vào.

### F3 · `functools.lru_cache` (`rules.py:269`, `:294`)

- **Có giới hạn:** `maxsize=8` cho mỗi hàm, có test ghim (`tests/test_soi_loi_t045.py:348-351`). Mỗi
  mục giữ một chuỗi (một dòng, hoặc cả khối đã nối). Tệ nhất 16 chuỗi cỡ một khối; với hồ sơ thật
  (7,8 KB) là dưới 130 KB, với đầu vào xấu 1 MB là khoảng 16 MB rồi bị thay dần. Không tăng mãi.
- **Giữ dữ liệu lâu hơn cần:** có, nhưng không đáng kể. Sau lần lọc cuối, tối đa 8 + 8 chuỗi của hồ sơ
  (có thể có ý chưa xác nhận) nằm trong bộ nhớ tiến trình Streamlit tới khi bị thay. Đây không phải
  tài sản cần bảo vệ ở `security.md` mục 1: không phải khóa, mật khẩu hay dữ liệu khách hàng. Nó vốn
  nằm sẵn ở dạng chữ thường trong `config/business_profile.md` trên cùng máy. Bộ nhớ đệm không đi vào
  prompt, log hay giao diện. Chỉ `rules.py` gọi hai hàm này (grep `seo_app app scripts`: không nơi nào
  khác).
- **Đúng đắn:** hai hàm là hàm thuần của một chuỗi, khóa so bằng giá trị, nên bộ nhớ đệm không đổi kết
  quả. Soi Lỗi đã có test chạy xuôi, ngược và xóa đệm (`test_lru_cache_does_not_change_results_between_calls`).
  `lru_cache` an toàn khi nhiều luồng Streamlit gọi cùng lúc: tệ nhất là tính lại, kết quả vẫn như nhau.

### R5 · Bỏ 1 ca trong `tests/test_profile_tag_t032.py`: **không vi phạm**

- Diff đúng 1 dòng xóa, 0 dòng thêm: ca `"- [*****CẦN XÁC NHẬN]"` trong `test_t043_plain_sentences_still_kept`,
  chú thích cũ "5 ký tự: quá giới hạn, coi là câu thường". Ca này khẳng định nhãn đó **được giữ lại
  cho AI**, tức ghim đúng lỗi SL-T043-1 mà phiếu yêu cầu sửa. Giữ ca này thì không sửa được lỗi.
- R5 cấm bỏ test để "qua" khi hành vi sai. Ở đây hành vi được ca đó ghim mới là hành vi sai, và việc
  bỏ làm bộ lọc **chặt hơn**. Chiều đúng đã được kiểm: `FIVE_PLUS_TAGS` (`tests/test_profile_tag_t045.py:119-136`)
  có `"[*****CẦN XÁC NHẬN]"` phải bị giấu. Soi Lỗi kiểm đúng dạng cũ với 5, 6, 7, 50 dấu `*`
  (`tests/test_soi_loi_t045.py:21`). Lá Chắn chạy lại: nhánh ra `'- ok'`, `main` ra `'- [*****CẦN XÁC NHẬN]\n- ok'`.
  Các ca câu thường còn lại của hàm vẫn qua.
- Thợ Máy ghi rõ việc bỏ và lý do trong báo cáo; Soi Lỗi đã chấp nhận. Lá Chắn đồng ý.
- `tests/test_soi_loi_t043.py`: chỉ bỏ 3 decorator `xfail(strict=True)` (9 dòng), thân test giữ nguyên;
  `strict=True` bảo đảm đây đúng là các ca đã sửa.

### Quyết định về SL-T045-1, SL-T045-2: **phiếu theo dõi mới, không ghi sổ rủi ro**

- Cả hai đã lọt trên `main`, nên T-045 không làm tệ hơn và không phải giữ T-045 lại.
- Mở **một phiếu theo dõi mức Thấp** (Thợ Máy), gộp lỗi #1 (cả biến thể thụt lề) và lỗi #2. Cách sửa
  nhỏ, đã có 5 test `xfail(strict=True)` sẵn (`tests/test_soi_loi_t045.py:266-296`), giữ tuyến tính bằng
  giới hạn số dòng chờ.
- Không ghi sổ rủi ro vì theo `security.md` mục 3, chỉ chủ dự án được chọn chấp nhận rủi ro thay vì
  sửa. Nếu chủ dự án thấy chuỗi phiếu bộ lọc đã đủ (đây là lượt thứ tư: T-032, T-043, T-045) và không
  muốn sửa tiếp thì ghi cả hai vào sổ rủi ro (mục 6) do chủ dự án ký. Lá Chắn chấp nhận được cả hai
  hướng, vì muốn lọt phải gõ nhãn tiêu đề rất lạ, và mọi bài AI viết vẫn là nháp, người dùng duyệt
  trước khi đăng.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `git diff origin/main...team/T-045` lọc dòng thêm theo `api_key/password/secret/token`: 0 dòng. `git log -p origin/main..team/T-045` cùng mẫu: 0 dòng. `detect-secrets` (cả repo): trong các file của diff 0 cảnh báo. Soát toàn lịch sử (`git log -p --all`) theo `sk-ant-`, `sk-proj-`, `AIza…`, `BEGIN … PRIVATE KEY`: chỉ có khóa giả có từ trước (`…KhoaGia…`), không thuộc phiếu này. Chưa từng commit `.env`, `.sqlite`, file service account (`git log --all --name-only`: 0 file). |
| S2 | Không áp dụng | Không có log, `st.error` hay thông báo lỗi mới. Diff `rules.py` không đụng `ContentRulesError`. |
| S3 | Không áp dụng | Không có biến cấu hình mới; `.env.example` không đổi. |
| W1 | Không áp dụng | Không đụng `seo_app/wordpress/`. |
| W2 | Không áp dụng | Như trên. |
| W3 | Không áp dụng | Như trên. |
| W4 | Không áp dụng | Như trên. |
| A1 | Đạt | Bộ lọc vẫn chạy trong `load_rules` trước khi hồ sơ vào prompt (`rules.py:353`, `prompts.py:56` không đổi). Fuzz độc lập 300.000 tài liệu: 0 vi phạm (a)/(b)/(c), 182 dòng lùi đều thuộc lớp #2 (không phải chữ của ý có nhãn). Mẫu nhãn mới nhận mọi nhãn mẫu cũ nhận (bỏ giới hạn `{0,4}`). Nửa nhãn: thu dải chen về một ký tự rồi mới cắt cửa sổ 64 (`:262-281`), nên cửa sổ chứa ít nhất phần chữ mà bản cũ xét. Đường lọt còn lại (lỗi #1, #2) có từ trước. |
| A2 | Không áp dụng | Không đổi lớp AI, không thêm công cụ cho AI. |
| A3 | Đạt | Hồ sơ thật: đầu ra nhánh bằng đầu ra `main`, 4.826 ký tự, sha256 `24cfa2b2…a8439`; 0 dòng còn nhãn, 0 dòng `>`; 5 dòng có nhãn trong nguồn đều không có trong đầu ra. `load_rules().business_profile` bằng đầu ra `main`. |
| U1 | Không áp dụng | Không đụng `app/`. |
| U2 | Không áp dụng | Như trên. |
| U3 | Không áp dụng | Như trên. |
| F1 | Không áp dụng | Không có đường dẫn mới; `BUSINESS_PROFILE_FILE` (`rules.py:16`) không đổi. |
| F2 | Không áp dụng | Không đụng ảnh. |
| F3 | Đạt | Không `eval`/`pickle`/`yaml.load`; đọc hồ sơ vẫn `encoding="utf-8-sig"` (`rules.py:305`, không đổi). ReDoS: 3 mẫu mới một lớp ký tự, chiếm hữu; đo 13 đầu vào xấu một dòng và 8 đầu vào nhiều dòng, 256 KB → 1 MB, tỉ lệ 3,1–5,3 (tuyến tính). `lru_cache(maxsize=8)` có giới hạn, chỉ giữ chữ hồ sơ (không phải bí mật), không đi ra ngoài tiến trình. |
| D1 | Đạt | `pyproject.toml`, `uv.lock` không đổi. `functools` là thư viện chuẩn. `pip-audit` (từ `uv export --frozen`): "No known vulnerabilities found". |
| D2 | Đạt | `.gitignore` không đổi, vẫn chặn `.env`, `.env.*`, `*service-account*.json`, `*.sqlite`, `.pytest_cache/`, `.ruff_cache/`, `__pycache__/` (`.gitignore:2-24`). |
| D3 | Đạt | 2 file test mới chỉ nhập `pytest`, `random`, `re`, `seo_app.content.rules`, `tests.timing`, và chỉ gọi hàm trên chuỗi. Không `socket`, `requests`, thư viện AI, không mở file. Bộ chặn mạng chung `tests/conftest.py:18` (autouse) vẫn bật. Fuzz trong test dùng hạt giống cố định. |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | No known vulnerabilities found (202 dòng yêu cầu từ `uv export --frozen`) | Có |
| bandit (`-r seo_app app scripts`) | 1 cảnh báo Low: B101 `assert` ở `seo_app/storage/drafts.py:203` | Có, báo nhầm, có từ trước (xem dưới). 0 cảnh báo trong `rules.py` |
| detect-secrets (`--all-files`) | Trong file đã commit: 1 cảnh báo (`tests/test_config.py:34`). Còn lại thuộc `.venv`, `.pytest_cache`, `.ruff_cache` (không commit) | Có, báo nhầm (xem dưới). 0 cảnh báo trong file của diff |
| Soát lịch sử git | Diff và commit của nhánh: 0 dòng. Toàn lịch sử: chỉ khóa giả có từ trước | Có |
| Fuzz so với `main` (script riêng) | 300.000 tài liệu, 0 vi phạm, 182 dòng lùi đều lớp #2 | Có, xem tay 10 tài liệu |
| Đo tốc độ (script riêng) | Tuyến tính, tỉ lệ 3,1–5,3 | Có |
| pytest | `5458 passed, 10 skipped, 28 xfailed, 1 warning in 546.56s` (Windows 11, `f23a78b` + biên bản). Cảnh báo pydantic của `tests/test_soi_loi_t028.py`, có từ trước | Có, khớp số của Soi Lỗi |
| ruff | `All checks passed!` | Có |

## Báo nhầm đã loại

- **bandit B101** `seo_app/storage/drafts.py:203` (`assert saved.saved_at is not None`): không thuộc diff
  (file có từ T-016), chỉ là kiểm tra kiểu, không phải kiểm tra an toàn.
- **detect-secrets** `tests/test_config.py:34` "Secret Keyword": mật khẩu giả `"abcd efgh"` của test cấu
  hình, có từ trước. Các cảnh báo trong `.venv` là mã của thư viện bên thứ ba, không commit.
- **Lần đo tốc độ đầu** cho tỉ lệ rất lớn (hàng chục nghìn) ở `_is_unconfirmed` và `_ends_with_partial_tag`,
  khoảng 8 ở `confirmed_profile` một dòng. Nguyên nhân: script đo gọi lặp cùng một chuỗi, nên ở cỡ 256 KB
  hầu hết lời gọi trúng bộ nhớ đệm, còn ở 1 MB chỉ gọi một lần. Sửa script để xóa bộ nhớ đệm trước mỗi
  lời gọi và đo hàm gốc qua `__wrapped__`: mọi tỉ lệ còn 3,1–5,3. Đây là lỗi của script đo, không phải
  của bộ lọc.
- **Bộ phân loại thô thứ hai** của fuzz báo 4 dòng lùi nằm trong "đoạn có nhãn". Xem tay: dòng có nhãn
  thuộc gạch đầu dòng khác phía trên. Cả 4 đều thuộc lớp #2.

## Điều kiện (nếu ĐẠT CÓ ĐIỀU KIỆN)

1. Chỉ Huy mở **một phiếu theo dõi mức Thấp** (Thợ Máy) cho SL-T045-1 (lỗi #1, kể cả biến thể tiêu đề
   thụt lề `- a` / `  ## 7 [CẦN` / `  XÁC` / `  NHẬN] BIMAT`) và SL-T045-2 (lỗi #2). Yêu cầu: bỏ đúng 5
   `xfail` ở `tests/test_soi_loi_t045.py:266-296`, thêm test cho biến thể thụt lề, giữ tuyến tính (giới
   hạn số dòng chờ), hồ sơ thật không đổi. Phiếu chỉ cần có trên bảng việc trước khi hết giai đoạn.
   **T-045 được gộp ngay**, không cần làm thêm lượt.
2. Nếu chủ dự án không muốn sửa tiếp thì ghi 2 lỗi vào sổ rủi ro (`security.md` mục 6), do chủ dự án ký.
3. Sau 01/11, kiểm lại T-045 bằng Fable (biên bản này chạy bằng Opus tạm).

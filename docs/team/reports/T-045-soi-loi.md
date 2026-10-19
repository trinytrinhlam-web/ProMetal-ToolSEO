# Báo cáo T-045 · Soi Lỗi kiểm thử: bộ lọc hồ sơ, 3 lỗi Thấp sau T-043

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-045](../tickets/T-045-loc-ho-so-theo-doi-sau-t043.md) |
| Ngày nộp | 2026-10-19 |
| Phạm vi | `git diff origin/main...team/T-045` (gốc `b5ff3b3`, đầu nhánh lúc nhận `0c63d50`): `seo_app/content/rules.py`, 3 file test, báo cáo Thợ Máy |
| Kết quả | Hoàn thành · Kết luận: **ĐẠT** |

## Tóm tắt (cho chủ dự án)

Cả 3 lỗi của phiếu đã sửa đúng. Tôi đã thử nhiều cách cố tình gõ nhãn `[CẦN XÁC NHẬN]` thật lạ
(hàng trăm emoji, ngoặc chen giữa, nhãn vắt qua dòng trống hay dòng ghi chú `>`, tiêu đề lỡ thụt
lề). Không cách nào làm một dòng có nhãn, hay chữ của một ý có nhãn, tới được AI mà bản đang chạy
trên `main` lại giấu được. Bộ lọc vẫn chạy nhanh với đầu vào xấu cỡ 1 MB. Phần hồ sơ thật AI thấy
**giống hệt** `main`. Tôi tìm thêm 2 kiểu gõ rất hiếm vẫn lọt. Cả hai **đã lọt từ trước** trên
`main`, nên bản này không làm tệ hơn: nhãn trên tiêu đề vắt qua **3 dòng**, và nhãn tiêu đề bị
tách hai lần liền nhau. Hai lỗi này không chặn gộp.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t045.py` | Mới: 73 test (68 qua, 5 `xfail(strict=True)` cho SL-T045-1, SL-T045-2). |
| `docs/team/reports/T-045-soi-loi.md` | Báo cáo này. |

Không sửa code ứng dụng, không sửa test cũ.

## Bằng chứng

```
$ uv run pytest tests/test_soi_loi_t045.py
68 passed, 5 xfailed in 9.37s

$ uv run pytest            (commit 4ab7efe, Windows 11)
5458 passed, 10 skipped, 28 xfailed, 1 warning in 596.60s (0:09:56)
(= 5.390 qua của Thợ Máy + 68 test mới; 23 xfailed cũ + 5 xfail mới; cảnh báo pydantic có từ trước)

$ uv run ruff check .
All checks passed!
```

### Điểm 1 · Thợ Máy bỏ 1 ca khỏi `test_t043_plain_sentences_still_kept`: **Soi Lỗi chấp nhận**

- Diff `tests/test_profile_tag_t032.py` đúng **1 dòng xóa, 0 dòng thêm**: ca `"- [*****CẦN XÁC NHẬN]"`
  (chú thích cũ "5 ký tự: quá giới hạn, coi là câu thường"). Ca này ghim chính lỗi SL-T043-1 mà
  phiếu yêu cầu sửa, nên giữ lại thì không thể sửa lỗi. Các ca còn lại của hàm đó giữ nguyên và
  vẫn qua.
- Không mất kiểm tra nào: chiều ngược lại đã được kiểm. `FIVE_PLUS_TAGS` trong
  `tests/test_profile_tag_t045.py` có `"[*****CẦN XÁC NHẬN]"` (phải bị giấu). Tôi thêm đúng dạng
  cũ, nhãn ngay sau gạch đầu dòng với 5, 6, 7, 50 dấu `*`
  (`test_removed_t032_case_now_hidden_exact_form`). Thêm cả câu thường nhiều ký tự lạ nhưng có
  ngoặc đóng, vẫn phải giữ (`- [******] cần xác nhận`, `- [***** CẦN] XÁC NHẬN`).
- Diff `tests/test_soi_loi_t043.py` chỉ bỏ 3 decorator `xfail` (9 dòng), thân test giữ nguyên.

### Điểm 2 · 91 dòng khác bản cũ (lớp Lá Chắn T-043 #2): **không có dòng có nhãn nào lọt**

Tôi viết fuzz riêng (script ở scratchpad, không commit), so `confirmed_profile` của nhánh với bản
`origin/main` (`rules.py` trên `main` trùng gốc `b5ff3b3`). Mỗi dòng nội dung có mã riêng. Mảnh
gồm 9 nhãn trọn, 10 nửa nhãn, 6 nửa sau, 14 kiểu đầu dòng, dòng trống, dòng `>`. Ngoài đếm dòng
lùi, tôi thêm **hai phép kiểm độc lập** với cách bộ lọc chia khối:

- (a) dòng tới AI không được chứa nhãn trọn (theo mẫu của cả bản cũ lẫn bản mới);
- (b) ý đơn giản có nhãn (gạch đầu dòng không thụt lề cùng các dòng thụt lề ngay sau, không bắt
  đầu bằng `#`) thì không mã nào của ý đó được tới AI.

| Lần chạy | Dòng lùi (cũ giấu, mới lộ) | Ngoài lớp #2 | Vi phạm (a)/(b) | Dòng giấu thêm |
|---|---|---|---|---|
| 300.000 tài liệu, đủ mảnh (3 hạt giống) | 216 (159 tài liệu) | **0** | **0** | 194.000 |
| 300.000 tài liệu, bỏ mảnh ≥ 5 ký tự lạ | **0** | 0 | **0** | 23.109 |

Phân loại tự động từng dòng lùi: dòng lộ **không có nhãn**, khối của nó **không có nhãn**, và khối
kết thúc ngay trước một tiêu đề thụt lề mà nhãn chỉ bản mới nhận (≥ 5 ký tự lạ), có thể cách một
dòng trống. Lần phân loại đầu báo 20 ca "ngoài lớp". Xem tay: đều là cùng lớp, chỉ có dòng trống
hoặc đoạn văn nằm giữa. Sửa bộ phân loại xong thì còn 0.

Ca Thợ Máy nêu: `- ok` / `  ## 7 [❗❗❗ **CẦN XÁC NHẬN**]` / `  BIMAT [CẦN XÁC NHẬN]` / `## 8` /
`- sau` → `- ok\n## 8\n- sau`. `- ok` không có nhãn của riêng nó. Tiêu đề, `BIMAT` và cả mục
`## 7` bị giấu. Đây đúng là thiết kế SL-T032-2 đã duyệt; bản cũ giấu `- ok` chỉ vì không nhận ra
nhãn trên tiêu đề nên ghép cả ba dòng thành một khối. **Không phải lỗi.** Có test ghim
(`test_class2_*`). Phép kiểm (a)/(b) chạy thành test cố định với 3 × 1.500 tài liệu
(`test_fuzz_no_tagged_line_or_tagged_item_reaches_ai`). Thử ngược: thay bộ lọc bằng bản `main`
hoặc bằng bộ lọc chỉ bỏ dòng có nhãn thì test này **hỏng** như mong đợi.

### Điểm 3 · Các ca Thợ Máy nhờ thử: đều giấu đúng

| Nhóm | Ca (rút gọn) | Kết quả | Test |
|---|---|---|---|
| Nhãn rất dài nhiều emoji vắt dòng trên tiêu đề | `## 7 [` + 40 × `👨‍👩‍👧‍👦⚠️🇻🇳❗**` + `CẦN` / `XÁC ❗×300 NHẬN]`; cùng ca với tiêu đề thụt lề; nửa nhãn chỉ có emoji rồi `CẦN XÁC NHẬN]` ở dòng sau | Giấu cả mục (`main` để lọt cả mục) | `test_long_emoji_half_tag_*` |
| Ngoặc mở chen giữa nhãn | `[CẦN (XÁC NHẬN]`, `[CẦN [** XÁC NHẬN]`, `[[CẦN…`, `[(CẦN…`, `([CẦN…`; trên tiêu đề vắt dòng `## 7 [CẦN (` / `XÁC NHẬN]`, `## 7 [CẦN ([` | Giấu | `test_open_bracket_inside_tag_hidden` |
| `  ## … [CẦN` nối nhau trong ý **có** nhãn | 3 dòng `  ## b [CẦN` liền nhau; xen dòng trống, `>`, U+200B, dòng quên thụt lề, `  ## NHẬN] c` | Giấu cả ý (`main` để lộ các dòng này) | `test_chained_indented_half_headings_in_tagged_item` (14 ca) |
| Như trên trong ý **không** nhãn | `- a` / `  ## b [CẦN` ×3 / `  BIMAT` | Giữ nguyên (không giấu thừa) | `test_chained_indented_half_headings_untagged_item_kept` |
| Tiêu đề cấp cao hơn có nhãn trong mục đang giấu | `## 7 [CẦN XÁC` / dòng trống / `## NHẬN]`; `  # 7 [CẦN XÁC NHẬN]`; `  # 7 [CẦN XÁC` / `NHẬN]`; `# 7 [❗❗❗❗❗ CẦN` / ` XÁC NHẬN]` | Giấu tới cấp của tiêu đề đó | `test_higher_tagged_heading_inside_hidden_section` |
| `## NHẬN]` sau tiêu đề chờ, xen dòng trống / `>` | 2 dòng trống; `> ghi chú`; `>` rồi dòng trống; `  >` thụt lề; trong ý có nhãn | Giấu cả mục | `test_heading_rest_after_blank_or_note_lines` |

Đã xem kỹ thêm các nhánh mới trong `rules.py`: `join_block` khi dòng trước còn nửa nhãn, khối chứa
tiêu đề chờ (`head_in_block`) ghép được hay không ghép được nhãn, `_tagged_heading_level` khi
dòng nửa sau là tiêu đề cấp cao hơn (`# XÁC NHẬN]`: giấu tới tiêu đề `##` kế tiếp, mục `## c` sau
đó được giữ đúng), `block_tagged` chỉ đặt lại trong `close_block`. Không tìm thấy đường lọt mới.

### Điểm 4 · Tốc độ và bộ nhớ đệm

Đo nhanh thời gian CPU (lấy lần nhanh nhất trong 3 lần; đo lúc bộ test đầy đủ đang chạy song song
nên số dao động; đồng hồ Windows có bước 15,6 ms):

| Đầu vào xấu | 250 KB | 1 MB |
|---|---|---|
| `[[[[` | 0,062 s | 0,156 s |
| `[CAN[[[[` | 0,031 s | 0,203 s |
| `[CAN*[CAN*` | 0,047 s | 0,203 s |
| `[*(*` | 0,047 s | 0,234 s |
| `[CAN*(*(` | 0,047 s | 0,203 s |
| ý có nhãn + `  ## b [CAN` × n | 0,156 s | 0,641 s |

Đều dưới 1 giây với 1 MB. Phép đo chuẩn của dự án (`tests/timing.py`, tỉ lệ thời gian khi đầu vào
gấp 4) qua với 10 đầu vào xấu mới (`test_more_bad_inputs_linear`): `[CAN` + `*(` lặp, `(` + dải `*`
dài lặp, `[CAN XAC` + `[[[[`, `[CAN [ [ [`, `[CAN XAC [` lặp, dòng nửa nhãn rồi tiêu đề nửa nhãn
lặp, dòng thường rồi tiêu đề nửa nhãn lặp, mục giấu với nhiều `  # x [CAN`, `## NHAN]` sau `>`
lặp, nửa nhãn tiêu đề toàn emoji ZWJ. Đọc mẫu: `_LEAD_GAP` không nhận ngoặc mở, mỗi lớp ký tự là
**một** lớp với `*+`/`++`, không lồng lượng từ. `block_is_tagged` dò khối chưa nhãn đúng một lần
rồi khối bị đóng ngay.

`lru_cache`: hai hàm được cache là hàm thuần của một chuỗi, nên cache không làm kết quả phụ thuộc
lần gọi trước. Test `test_lru_cache_does_not_change_results_between_calls`: 805 tài liệu chạy xuôi,
chạy ngược và chạy với cache bị xóa trước mỗi lần, ba kết quả như nhau. Ngoài
`rules.py`, không nơi nào gọi `_is_unconfirmed`/`_ends_with_partial_tag` (đã grep). `maxsize=8`
(có test ghim): tệ nhất giữ 8 chuỗi cỡ một khối hồ sơ trong bộ nhớ, không đáng kể.

### Điểm 5 · Hồ sơ thật

```
profile file same as main: True 7800
new filter(wt) == main filter(main): True 4826 24cfa2b250174254f6adf8d8f1a047a4b3e828264b2b555c5ad85a49c1aa8439
load_rules().business_profile == main filter: True
lines in / out: 143 101
```

So chuỗi kết quả (4.826 ký tự, sha256 của chuỗi UTF-8 xuống dòng `\n`). Thợ Máy đo sha256 của
file ghi bằng `write_text` trên Windows (xuống dòng CRLF), nên hai mã băm khác nhau là do cách đo,
không phải nội dung. Thêm test: không dòng nào trong hồ sơ AI thấy còn nhãn hay là dòng `>`.

## Lỗi phát hiện

Không có lỗi Nghiêm trọng, Cao, Trung bình. Không có ca lùi so với `main` ngoài lớp #2 (đúng
thiết kế). Hai lỗi Thấp dưới đây **đã có trên `main`**, không do T-045 gây ra.

| Mã | Mức | Lỗi | Tái hiện | Mong đợi | Thực tế (nhánh và `main` như nhau) |
|---|---|---|---|---|---|
| SL-T045-1 | Thấp · không chặn · có từ trước | Nhãn trên **tiêu đề** vắt qua **3 dòng**. Tiêu đề chờ chỉ ghép với đúng 1 dòng kế; ghép xong vẫn còn nửa nhãn thì bỏ chờ. (Ý thường không bị, vì cả khối được nối.) | `## 7 [CẦN` / `XÁC` / `NHẬN]` / `- BIMAT` / `## 8` / `- ok`. Cũng vậy với `## 7 [` / `CẦN` / `XÁC NHẬN]` và `## 7 [**` / `**CẦN` / `XÁC NHẬN]` | Giấu mục `## 7` (cả `- BIMAT`) | Cả 6 dòng tới AI |
| SL-T045-2 | Thấp · không chặn · có từ trước | Biến thể của SL-T043-2: dòng nửa sau của nhãn tiêu đề **lại kết thúc bằng nửa nhãn mới**, dòng kế dạng tiêu đề hoàn thành nó. Dòng nửa sau bị bỏ qua (`continue`) nên không chờ tiếp; dòng `## NHẬN]` cuối thành tiêu đề cùng cấp và kết thúc mục đang giấu. | `## 7 [CẦN XÁC` / `## NHẬN] [CẦN XÁC` / `## NHẬN]` / `- BIMAT` / `## 8` / `- ok`. Cũng vậy khi dòng giữa không có `##` | Giấu tới `## 8` | `## NHẬN]` và `- BIMAT` tới AI |

Gợi ý sửa (cho Thợ Máy, nếu Chỉ Huy mở phiếu): khi tiêu đề chờ ghép với dòng kế mà **chưa** thành
nhãn nhưng chuỗi ghép **vẫn kết thúc bằng nửa nhãn**, thì tiếp tục chờ với chuỗi ghép (giới hạn số
dòng, ví dụ 3, để giữ tuyến tính). Khi dòng nửa sau đã ghép thành nhãn mà chính nó kết thúc bằng
nửa nhãn, thì đặt lại tiêu đề chờ với dòng đó. Cả hai muốn lọt đều cần gõ nhãn rất lạ trên tiêu
đề. Hướng dẫn trong hồ sơ đã nêu mẫu chuẩn `[CẦN XÁC NHẬN — lý do]`.

Đã loại (không phải lỗi):

- `## 7 [CẦN )` / `XÁC NHẬN]`, `(CẦN [XÁC] NHẬN)`, `[CẦN] [XÁC NHẬN]`: có ngoặc đóng giữa nhãn,
  không phải nhãn theo thiết kế (T-043, test câu thường `- [CẦN] xác nhận`).
- `- a [CẦN XÁC NHẬN]` / `  ## b [CẦN` / dòng trống / `BIMAT2` (không thụt lề): `BIMAT2` là đoạn
  mới theo thiết kế (dòng không thụt lề sau dòng trống luôn mở khối mới). Bản mới còn giấu thêm
  dòng `## b [CẦN` mà `main` để lộ.
- `- giá` / `  ## ghi chú [CẦN` / `  BIMAT [CẦN XÁC NHẬN]`: `- giá` được giữ, giống `main`, cùng
  thiết kế SL-T032-2 (tiêu đề thụt lề tách ý trước khi ý đó chưa có nhãn).

## Đối chiếu tiêu chí xong

- [x] Xem việc sửa test ngoài danh sách `xfail` (điểm 1): đúng, không mất kiểm tra, **chấp nhận**
- [x] 91 dòng khác bản cũ (điểm 2): fuzz 300.000 ca của tôi ra 216 dòng, đều lớp #2, 0 dòng có
  nhãn hay chữ của ý có nhãn lọt
- [x] Các ca Thợ Máy nhờ thử (điểm 3): 6 nhóm, đều giấu đúng, có test
- [x] Tốc độ 1 MB và `lru_cache` (điểm 4): tuyến tính, cache không đổi kết quả
- [x] Hồ sơ thật giống hệt `main` (điểm 5)
- [x] Mỗi nhánh logic mới trong diff có test (của Thợ Máy và của tôi)
- [x] Test không gọi mạng, không cần `.env`, không phụ thuộc thứ tự chạy
- [x] `uv run pytest`, `uv run ruff check .`

## Rủi ro và điểm cần chú ý

- Lớp #2 nay gặp nhiều hơn (vì nhãn ≥ 5 ký tự lạ được nhận). Ý đứng ngay trước tiêu đề thụt lề có
  nhãn được giữ khi ý đó không có nhãn riêng. Đây là thiết kế đã duyệt. Muốn đổi thì phải đổi
  SL-T032-2 và sửa test đã duyệt; Chỉ Huy quyết.
- Bản mới giấu thừa nhiều hơn hẳn (fuzz: khoảng 194.000 dòng giấu thêm trên 300.000 tài liệu),
  đúng hướng an toàn. Với hồ sơ thật thì không đổi gì.

## Đề xuất

- Lá Chắn: kiểm A1/A3/F3 như Thợ Máy đề nghị. Có thể dùng lại phép kiểm (a)/(b) ở trên.
- Chỉ Huy: SL-T045-1, SL-T045-2 nên gộp vào một phiếu theo dõi mức Thấp, hoặc ghi vào sổ rủi ro
  (`security.md` mục 6) nếu chủ dự án không muốn sửa. Không cần làm trước khi gộp T-045.

## Câu hỏi cho chủ dự án

Không có.

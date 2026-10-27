# Báo cáo T-089 · Dọn lỗi Thấp gửi nháp sau T-086, lưu băm ảnh đã duyệt · Soi Lỗi (rút gọn)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-089](../tickets/T-089-gui-nhap-loi-thap-sau-t086.md) |
| Ngày nộp | 2026-10-26 (lượt 2: 2026-10-27) |
| Nhánh | `team/T-089` (kiểm code `87ad51c`, gốc `main` `3d7f4b7`; lượt 2: code `f2a72f5`, đầu nhánh `cf5a556`) |
| Kết quả | Hoàn thành (kiểm rút gọn, kèm thử trình duyệt thật với WordPress giả). **Kết luận: ĐẠT CÓ ĐIỀU KIỆN, chuyển Lá Chắn rút gọn được ngay.** LC-T086-1, SL-T086-1, SL-T086-2 **đã sửa thật** (cách tái hiện cũ và biến thể); băm ảnh đã duyệt lưu trong nháp đạt. Lỗi mới: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **1 Thấp** (SL-T089-1), không chặn gộp. Soát R5: **đạt**. Thử gộp với `main` và `team/T-041` mới nhất: **không xung đột**. **Lượt 2 (2026-10-27): SL-T089-1 đã sửa thật; 1 Thấp mới SL-T089-2 do chính bản sửa (lùi so với lượt 1 ở hai ca hiếm), không chặn gộp; vẫn ĐẠT CÓ ĐIỀU KIỆN** (mục «Lượt 2») |

## Lượt 2 (2026-10-27): kiểm lại nhanh bản sửa SL-T089-1

Theo tin giao việc của Chỉ Huy B (2026-10-27) và mục «Lượt 2» của báo cáo Họa Sĩ: `holder["claimed"]` (chỉ lần đã ghi được «đang gửi» mới ghi kết quả), `finish_send` chỉ thử ghi lại khi có dấu đó, `record_outcome` ghi kiểu so rồi đặt với `expected=(claimed, False)`, câu báo `MSG_STATE_CHANGED_ELSEWHERE`; gỡ 2 `xfail` SL-T089-1, thêm 4 test.

**Tóm tắt (cho chủ dự án):**

- Lỗi nhỏ SL-T089-1 **đã sửa thật**: hai tab cùng gửi một bài, tab bị từ chối dù bị bấm thêm đúng lúc (một hay hai lần liên tiếp), hay gặp lúc file nháp bận, đều không còn xóa ghi chú «đã gửi/đang gửi» của tab kia; mở lại bài vẫn khóa đúng, tick «Tạo thêm» là gửi được (không khóa oan). Người dùng cố ý gửi tiếp ở tab thứ hai trong lúc tab đầu đang gửi: bài nhớ đúng lần gửi sau, tab đầu vẫn hiện bài của nó và báo rõ.
- Gửi một tab bình thường vẫn ghi «đã gửi»; các ca cũ (bấm gì đó giữa lúc gửi, ngắt hai lần, gửi dở, mã bài lạ, nháp sửa tay) vẫn đúng.
- Còn **1 lỗi nhỏ mới (SL-T089-2)**, sinh ra từ chính bản sửa: nếu đúng lúc tab đầu đang gửi mà ở tab khác **bài bị xóa**, hoặc lần gửi cố ý ở tab khác **hỏng ngay** (chưa gửi gì), thì bài tab đầu vừa tạo không được ghi vào nháp; mở lại bài (nháp được lưu lại) không còn khóa, bấm là ra bài thứ hai. Bản lượt 1 không bị hai ca này. Rất khó gặp; sửa khoảng 2 dòng (đã thử trên bản sao: đóng được, các test khác vẫn qua).

| Việc kiểm | Kết quả | Bằng chứng |
|---|---|---|
| SL-T089-1, cách tái hiện cũ (tab thua so rồi đặt bị ngắt; tab kia đang gửi / đã gửi trọn bài 501) | **Đã sửa** | `SL: test_lost_tab_interrupted_keeps_other_tab_sending`, `…_keeps_other_tab_sent` (Họa Sĩ gỡ `xfail` sau khi XPASS) qua |
| Biến thể: thua so rồi đặt hay ghi «đang gửi» hỏng (file nháp bận) đúng lúc tab kia vừa gửi xong bài 501; ngắt ở lần ghi phiên thứ 1, thứ 2 sau đó; ngắt hai lần liên tiếp (ngay sau lần so rồi đặt và ở lần ghi đầu của lần chạy sau) | **Đạt** | `SL: test_lost_or_busy_tab_interrupted_keeps_other_tab_sent` × 6 (thua-ghi-1, thua-ghi-2, thua-hai-lan, ban, ban-hai-lan, ban-ghi-2): không request nào, nháp giữ «đã gửi 501» của tab kia, không còn `_wp_sending`, phiên mới khóa «đã gửi» và tick «Tạo thêm» thì mở (không khóa oan). Họa Sĩ `N: test_pending_not_written_then_interrupted_writes_nothing` (tab kia «đang gửi») qua |
| Ghi nhận 1 của Lá Chắn (tab kia cố ý tick «Tôi đã kiểm tra…» rồi gửi tiếp trong lúc tab này đang gửi) | **Đạt** (có Ghi nhận chữ L2-1) | Họa Sĩ `N: test_outcome_does_not_overwrite_other_tab_new_send`, `N: test_retry_in_finish_send_also_compares` qua. Thêm bằng **hai phiên thật** (`SL: test_confirmed_send_in_other_tab_keeps_its_record`): trong lúc website đang tạo bài 501 cho tab 1, tab 2 vẽ lại, thấy khóa «gửi dở», tick, gửi trọn bài 502: nháp giữ «đã gửi 502»; tab 1 hiện «Đã tạo bài nháp… (mã 501)» kèm câu «Chưa ghi được kết quả gửi vào nháp (một tab khác của app vừa ghi trạng thái gửi mới…)», khóa; phiên mới thấy «đã gửi» bài 502 |
| Không lùi các ca T-086/T-089 cũ | **Đạt** | Bộ test liên quan (mục «Bằng chứng lượt 2»): gửi một tab ghi «đã gửi 501» (`assert_one_post_locked_with_result`), ngắt ở từng lần ghi và ngắt hai lần (`test_soi_loi_t086.py`), gửi dở, mã bài lạ (2⁶³, 2⁶⁴, 10³⁰, âm, chữ…), nháp sửa tay, hai phiên luân phiên 3 vòng, «Tạo thêm» ba lần một tab |
| `xfail` gỡ đúng R5 | **Đạt** | `git diff d5d0e69..cf5a556 -- tests/`: `tests/test_soi_loi_t089.py` chỉ xóa 2 dấu `@pytest.mark.xfail(...)` (8 dòng), thân test không đổi; `tests/test_t089_send_draft.py` thêm 4 test, một dòng import thêm `DraftError`, không sửa test cũ. Không `skip`, không xóa test |
| Thử gộp | **Không xung đột** | `git merge-tree`: `cf5a556` + `origin/main` `e295f0e`; + `origin/team/T-041` `433c533` (T-041 thêm `write_seo` ngay sau `record_outcome` trong `send_and_record`, ghép đúng chỗ); gộp lần lượt cả ba |

**Lỗi mới lượt 2** (test `xfail(strict=True)` trong `tests/test_soi_loi_t089.py`; `--runxfail`: hỏng đúng câu kiểm «nháp phải còn dấu bài 501»):

| Mã | Mức | Lỗi | Tái hiện | Mong đợi | Thực tế | Gợi ý sửa |
|---|---|---|---|---|---|---|
| SL-T089-2 | Thấp (lùi so với lượt 1, hai ca hiếm) | Kết quả gửi bị bỏ khi nháp không còn dòng trạng thái gửi: `record_outcome` so với «đang gửi» của chính lần này, thấy «không có dòng» và coi là «tab khác vừa ghi trạng thái mới», nên không ghi dù bài đã tạo trên website | (1) `test_confirmed_send_in_other_tab_failing_first_keeps_this_post` (hai phiên thật): trong lúc website đang tạo bài 501 cho tab 1, tab 2 tick «Tôi đã kiểm tra…», gửi, lỗi trước khi có request nào (`WordPressError`, ví dụ kiểm sai trước khi gửi) nên ghi «chưa gửi» (xóa dòng, đúng «đang gửi» của nó). (2) `test_draft_deleted_elsewhere_while_sending_comes_back_locked`: trong lúc tab 1 đang gửi, tab 2 bấm «🗑️ Xóa» nháp (`DraftStore.delete` xóa cả dòng trạng thái gửi); tab 1 làm tiếp, lần tự lưu tạo lại nháp | Nháp ghi «đã gửi 501» (hay «đang gửi» khi chưa rõ); phiên mới mở nháp khóa, phải tick «Tạo thêm» | Nháp không có dòng trạng thái gửi; phiên mới mở nháp: nút «Gửi nháp» bật, không nhắc gì, bấm là ra bài thứ hai. Tab 1 báo «một tab khác của app vừa ghi trạng thái gửi mới» (ca 2 sai: nháp bị xóa). Đối chứng trên bản sao `git archive` `d5d0e69` (lượt 1, ghi không so): cả hai ca nháp giữ «đã gửi 501», phiên mới khóa | Trong `record_outcome`: so rồi đặt với `claimed` hỏng mà kết quả có bài hay chưa rõ (`state` khác `None`) thì thử thêm một lần so rồi đặt với «không có dòng» (`expected=(None, False)`): dòng của tab khác (đang gửi/đã gửi) vẫn không bị ghi đè, chỉ ghi khi nháp trống. Thử sửa giả đúng 2 dòng đó trên bản sao: 2 test `xfail` qua (`--runxfail`) cùng 16 test liên quan (4 test lượt 2 của Họa Sĩ, SL-T089-1 và các biến thể, hai phiên). Giữ chốt `claimed` (lớp chặn chính cho tab thua). Câu báo nên tách ca «nháp bị xóa» |

**Ghi nhận lượt 2 (không phải lỗi):**

- L2-1. Câu báo khi không ghi đè: «Chưa ghi được kết quả gửi vào nháp (một tab khác của app vừa ghi trạng thái gửi mới cho bài này, app không ghi đè): mở lại nháp này sau sẽ thấy nhắc «chưa có kết quả», hãy kiểm…». Vế «sẽ thấy nhắc chưa có kết quả» chỉ đúng khi tab kia còn đang gửi; tab kia gửi xong thì mở lại thấy «đã gửi bài 502» (thấy ở `test_confirmed_send_in_other_tab_keeps_its_record`). Nên đổi vế sau cho ca này (ví dụ «nháp giữ trạng thái của tab kia; kiểm trang quản trị: bài này (mã …) cũng đã lên»).
- L2-2. Đột biến R3 của Họa Sĩ (bỏ chốt `claimed`, giữ so rồi đặt) không bắt là đúng: hai lớp chặn độc lập. Khi sửa SL-T089-2 theo gợi ý (ghi khi nháp trống), chốt `claimed` thành lớp chặn chính cho tab thua, cần giữ.
- L2-3. Lượt 2 không thử lại trên trình duyệt thật (hai ca trình duyệt của lượt 1 không đổi đường đi: tab thắng ghi kết quả bằng so rồi đặt với «đang gửi» của chính nó).

**Bằng chứng lượt 2:**

File test của Soi Lỗi: `tests/test_soi_loi_t089.py` thêm 9 ca (6 biến thể SL-T089-1, 1 ca hai phiên cho Ghi nhận 1, 2 `xfail` SL-T089-2): nay 42 ca, 40 qua, 2 `xfail`. Không sửa code ứng dụng.

```
$ PYTHONUTF8=1 uv run pytest tests/test_app_images.py tests/test_soi_loi_t056.py \
    tests/test_la_chan_t056.py tests/test_soi_loi_t086.py tests/test_la_chan_t086.py \
    tests/test_storage_drafts.py tests/test_drafts_images.py tests/test_app_pages.py \
    tests/test_t086_send_state.py tests/test_storage_send_state.py \
    tests/test_t089_send_draft.py tests/test_soi_loi_t089.py -q -rxXf
480 passed, 1 skipped in 1396.65s (0:23:16)   # code f2a72f5 (đầu nhánh cf5a556), trước khi thêm
                                               # test lượt 2 của Soi Lỗi; không còn xfail nào

$ PYTHONUTF8=1 uv run pytest tests/test_soi_loi_t089.py -rxXf \
    -W error::pytest.PytestUnhandledThreadExceptionWarning
40 passed, 2 xfailed in 323.46s (0:05:23)      # 2 xfail = SL-T089-2

$ uv run pytest tests/test_soi_loi_t089.py --runxfail -k "failing_first or deleted_elsewhere"
2 failed   # hỏng đúng câu kiểm: assert state is not None (nháp không còn dấu bài 501)
# Cùng 2 test trên bản sao git archive d5d0e69 (mã lượt 1): 2 passed   -> lỗi lùi do lượt 2
# Bản sao HEAD + sửa giả 2 dòng trong record_outcome (gợi ý ở bảng trên), --runxfail:
18 passed  # 2 test SL-T089-2 + 16 test liên quan (4 test lượt 2 của Họa Sĩ, SL-T089-1 và biến thể,
           # hai phiên, «Tạo thêm» ba lần)

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan tests/test_soi_loi_t089.py docs/team/reports/T-089-soi-loi.md
"results": {}
```

**Kết luận lượt 2: ĐẠT CÓ ĐIỀU KIỆN, chuyển Lá Chắn rút gọn được.** SL-T089-1 đóng thật (cả ca tab thua bị ngắt, file nháp bận rồi ngắt, ngắt hai lần, tab kia cố ý gửi tiếp); không lùi các ca T-086/T-089 cũ; R5 đạt. Điều kiện: SL-T089-2 (Thấp, hai ca hiếm, lùi so với lượt 1, sửa khoảng 2 dòng trong `record_outcome`): Họa Sĩ sửa luôn trong phiếu này (khuyên, vì đúng chỗ vừa sửa) hoặc Chỉ Huy lập phiếu theo dõi. Không chặn gộp: so với `main` (hai tab bấm gần nhau là ra hai bài) bản này vẫn tốt hơn hẳn.

## Tóm tắt (cho chủ dự án)

- Lỗi «mở cùng một bài ở hai tab, bấm gửi cách nhau một giây ra hai bài nháp» **đã sửa thật**. Tôi làm lại đúng cách đã tìm ra lỗi lần trước, trên trình duyệt thật với một "WordPress giả" chạy trên máy và ảnh lớn 28 MB: hai tab bấm «Gửi nháp» cách nhau 1 giây chỉ ra **một** bài nháp; tab bấm sau báo rõ «Chưa gửi gì lên website: trạng thái gửi của bài này vừa thay đổi (thường do … một tab khác của app)» và khóa nút. Làm thêm một lượt «Tạo thêm một bài nháp mới» ở cả hai tab, bấm cách nhau chưa tới nửa giây: cũng chỉ một bài.
- File ảnh bị thay bằng ảnh khác cùng tên, cùng dung lượng, cùng giờ sửa, rồi mở lại bài ở cửa sổ mới và bấm gửi ngay (không xem lại ảnh): app **dừng, không gửi gì**, bỏ «Đã duyệt», bắt xem và duyệt lại; khung ảnh hiện đúng ảnh mới kèm dòng «📍 Ảnh có vị trí GPS». Website trả mã bài lạ (rất lớn, âm, chữ…): trang không lỗi, khóa nút, có câu báo cố định.
- Bài lưu từ bản cũ (chưa có «dấu vân tay» ảnh): mở ra phải tick «Đã duyệt» lại **một lần**, những lần mở sau không bị hỏi lại.
- Còn **1 lỗi nhỏ mới** (SL-T089-1): khi hai tab cùng gửi một bài, tab bị từ chối mà đúng lúc đó lại bị bấm thêm một cái (trong vài phần nghìn giây) thì app xóa mất ghi chú «đang gửi/đã gửi» của tab kia trong bài; mở lại bài sẽ không còn bị khóa, bấm là ra thêm bài thứ hai. Rất khó gặp; sửa nhỏ (đã thử một cách sửa trên bản sao: đóng được).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t089.py` | Mới: 33 ca (31 qua, 2 `xfail(strict=True)` SL-T089-1). Dùng lại ảnh giả, WordPress giả, AI giả của `tests/test_app_images.py` và hàm giúp của `tests/test_soi_loi_t056.py`, `tests/test_soi_loi_t086.py`, `tests/test_t086_send_state.py` |
| `docs/team/reports/T-089-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa test của agent khác.

## Kiểm từng lỗi cũ và yêu cầu

| Lỗi / yêu cầu | Kết quả | Bằng chứng |
|---|---|---|
| 1 · LC-T086-1 (mã bài từ 2⁶³ làm trang lỗi lặp lại) | **Đã sửa** | `LC: test_lc_t086_1_huge_post_id_from_site_does_not_break_page` (gỡ `xfail`) qua. Biến thể mới: mã 2⁶⁴ và 10³⁰ (`test_post_id_far_out_of_range_fixed_note`): câu cố định «website trả mã bài nháp lớn bất thường…», nháp giữ «đang gửi», nút khóa, hai lần chạy sau không lỗi, 1 bài. Ngắt lần chạy thật ở lần ghi phiên thứ 1, 2, 3 sau khi website trả mã 2⁶³ (`…_interrupted_at_each_write`): `finish_send` ghi lại kết quả cũng chỉ ra câu cố định, không lỗi trang, không còn dấu sót. Biên 2⁶³ − 1 (`test_largest_post_id_still_recorded`): ghi được «đã gửi», phiên mới phải tick «Tạo thêm». Mã âm, 0, chữ `"501"`, số thực, `null`, `true`, chữ `"9223372036854775808"` (`test_malformed_post_id_locks_unsure` × 7): client từ chối, khóa «gửi dở», nháp giữ «đang gửi», 1 bài, không lỗi trang |
| 2 · SL-T086-1 (hai tab cùng nháp ra hai bài) | **Đã sửa** (có lỗi mới SL-T089-1 ở nhánh bị ngắt) | Test tái hiện cũ `SL: test_other_tab_starts_sending_while_this_tab_prepares` (gỡ `xfail`) qua. Biến thể mới: hai phiên luân phiên 3 vòng «Tạo thêm» (`test_two_sessions_take_turns_one_post_per_round`): mỗi vòng đúng 1 bài, phiên bấm sau được nhắc rõ và khóa, vòng sau chính phiên đó tick lại và gửi được; phiên kia gửi **trọn** một lần thật (bài 501) trong lúc phiên này nén ảnh (`test_other_session_completes_send_while_this_one_prepares`): 1 bài, câu nhắc, khóa, nháp giữ «đã gửi 501». Trình duyệt thật: 2 lượt, mỗi lượt 1 bài (bảng dưới). Kho nháp nhiều luồng: Họa Sĩ `test_only_one_tab_wins` |
| 3 · SL-T086-2 (ảnh xem trước cũ trong cache, băm của file mới) | **Đã sửa** | Test tái hiện cũ `SL: test_preview_shown_matches_approved_content` (gỡ `xfail`) qua. Biến thể: file bị thay **sau khi** khung ảnh hiện, **trước khi** tick duyệt (`test_file_replaced_between_view_and_approval`): lần duyệt gắn với bản đã hiện (băm cũ lưu vào nháp); phiên mới mở lại: bỏ duyệt, nhắc «Ảnh này khác bản bạn đã duyệt…»; phiên cũ gửi: dừng, chưa gửi gì. Trình duyệt thật: sau khi thay file tại chỗ, khung ảnh của phiên mới hiện đúng ảnh mới và dòng GPS của nó |
| 4 · Băm ảnh đã duyệt trong `DraftImage`; mở lại mà ảnh khác băm thì bắt duyệt lại | **Đạt** | Băm sửa tay sai dạng, mở trong app (`test_hand_edited_hash_reopened_in_app` × 9: chữ hoa, 63 ký tự, không phải hex, số, `null`, list, dict, có xuống dòng, chuỗi 100.000 ký tự): trang không lỗi, ảnh giữ, bỏ duyệt, nhắc; duyệt lại thì nháp lưu băm đúng của file. Băm đúng dạng nhưng không phải của file: gửi thẳng ở bước Xuất bản thì dừng, không request nào (`test_valid_but_wrong_hash_stops_send_without_viewing`); mở ở bước Viết & kiểm tra thì nhắc «khác bản bạn đã duyệt» (`test_wrong_hash_seen_on_write_step`). Băm sửa tay nằm trên ảnh chưa duyệt: bị bỏ, không nhắc, duyệt thì gắn băm thật (`test_hash_on_unapproved_image_ignored`). Nháp cũ không có khóa băm: hỏi duyệt lại **một lần**, các lần mở sau giữ «Đã duyệt» (`test_old_draft_without_hash_asks_only_once`). Trình duyệt thật: ca 3 bảng dưới |
| 5 · Giữ mọi test T-086 | **Đạt** | `tests/test_soi_loi_t086.py` (ngắt ở từng lần ghi, ngắt hai lần, trạng thái sửa tay), `tests/test_la_chan_t086.py`, `tests/test_t086_send_state.py`, `tests/test_storage_send_state.py` đều qua (mục «Bằng chứng»); mã bài trong nháp vẫn không dùng để ghi lên website (`LC: test_saved_post_id_never_used_to_write_to_wordpress` qua) |
| Không chặn oan luồng gửi bình thường | **Đạt** | Một tab gửi, «Tạo thêm», gửi, «Tạo thêm», gửi: 3 bài, không lần nào bị nhắc «trạng thái gửi vừa thay đổi» (`test_one_session_create_more_three_times_not_refused`); khóa «gửi dở» → tick «Tôi đã kiểm tra…» → gửi được, nháp ghi «đã gửi» (`test_unsure_lock_confirmed_then_sent_not_refused`); trình duyệt thật lượt 2: tab thắng gửi bình thường |
| `xfail` gỡ chỉ xóa dấu | **Đạt** | Mục «Soát R5» |

## Thử trên trình duyệt thật với WordPress giả trên máy

- App worktree ở cổng 8513 (cấu hình tạm `soi-loi-t089`), ảnh giả Pillow trong thư mục tạm (có ảnh 6000×4000, 28 MB), mật khẩu thử tạo trong phiên, không có khóa AI (alt gõ tay).
- WordPress giả: script của Soi Lỗi T-056 (`fake_wp_https.py`), chỉ nghe `127.0.0.1:8743`, chậm 1 giây ở lệnh tải ảnh và lệnh tạo bài, ghi mọi request ra file. Chứng chỉ tự ký cho `localhost` (tạo hôm nay, chỉ cho lần thử); app vẫn kiểm chứng chỉ (`REQUESTS_CA_BUNDLE` trong file môi trường tạm, không tắt SSL).
- Không gửi gì tới website thật, không start `seo-app-main`.

| Ca | Kết quả (log WordPress giả) |
|---|---|
| 1. Cách tái hiện cũ của SL-T086-1: hai tab (hai phiên) cùng nháp ở bước Xuất bản, bấm «Gửi nháp» ở tab 1, 1 giây sau ở tab 2 | **1 bài (501), 1 lần tải ảnh.** Tab 1: «Đã tạo bài nháp trên WordPress (mã 501), kèm 1 ảnh», khóa «đã gửi». Tab 2: «Chưa gửi gì lên website: trạng thái gửi của bài này vừa thay đổi…», khóa «gửi dở» (lúc đó tab 1 còn đang gửi) |
| 2. Cả hai tab tick «Tạo thêm một bài nháp mới», bấm gửi cách nhau chưa tới nửa giây (tab 2 trước) | **1 bài (502), 1 lần tải ảnh.** Tab 1 thắng (nén xong trước), tab 2 nhận câu nhắc và khóa |
| 3. Thay `IMG_9000.jpg` tại chỗ bằng ảnh khác có GPS (cùng dung lượng, đặt lại giờ sửa); tab 3 (phiên mới) mở nháp, sang thẳng bước Xuất bản (vẫn «alt đã duyệt 1/1»), tick «Tạo thêm», bấm gửi | **Không request nào** (log vẫn 14 dòng). Trang: «Chưa gửi gì lên website. Ảnh ở mục «Bản lề cổng»: nội dung file khác bản bạn đã xem và duyệt…», «0/1» đã duyệt. Bước Viết & kiểm tra: khung ảnh hiện ảnh mới (đỏ), dòng «📍 Ảnh có vị trí GPS…», «Đã duyệt» bỏ tick |

Tổng: 2 bài cho 2 lượt hai tab bấm gần nhau (lần trước T-086: 2 bài cho 1 lượt). Xong thì dừng app và WordPress giả, xóa `data/` của worktree, cổng 8513, 8743 đã đóng. `D:\ProMetal-ToolSEO\.claude\launch.json`: đã trả đúng bản cũ (so SHA-256 `a5607e8c…f169`) ngay sau khi app chạy (18:37); lúc 18:40 một phiên khác (Họa Sĩ T-041, cấu hình `seo-app-t041-hoasi`, cổng 8502) thêm cấu hình tạm của họ vào file này: tôi **không** đụng vào, phiên đó tự trả.

## Lỗi tìm thấy

Lỗi có test `xfail(strict=True)` trong `tests/test_soi_loi_t089.py` (`--runxfail`: hỏng đúng câu kiểm «trạng thái của tab kia phải còn»; thử sửa giả trên bản sao thì cả hai qua).

| Mã | Mức | Lỗi | Tái hiện | Mong đợi | Thực tế | Gợi ý sửa |
|---|---|---|---|---|---|---|
| SL-T089-1 | Thấp | Tab thua «so rồi đặt» mà lần chạy bị ngắt ngay sau đó thì `finish_send` ghi trạng thái **của tab này** vào nháp, không so: xóa «đang gửi» hoặc «đã gửi» của tab kia | `test_lost_tab_interrupted_keeps_other_tab_sending`: tab 1 ghi «đang gửi» đúng lúc tab 2 so rồi đặt; ngay sau đó tab 2 nhận yêu cầu chạy lại thật (như bấm đúp, bấm nút khác). `test_lost_tab_interrupted_keeps_other_tab_sent`: tab 1 gửi **trọn** (bài 501, nháp «đã gửi») trong lúc tab 2 nén ảnh; tab 2 thua, bị ngắt | Tab chưa ghi được «đang gửi» thì không ghi gì vào nháp; nháp giữ trạng thái của tab 1; phiên mới mở nháp vẫn khóa | Tab 2 không gửi gì (đúng), nhưng ở lần chạy sau `finish_send` thấy `holder` có `result` mà chưa `saved` nên gọi `record_outcome` với `holder["state"] = (False, previous_post)` → `save_send_state(draft, None)`: **xóa** dòng trạng thái gửi (hay ghi đè `(False, previous_post)` khi bài đã có mã trước). Phiên mới mở nháp: nút «Gửi nháp» bật, không nhắc gì, bấm là ra bài thứ hai; ca tab 1 đã gửi thì mất luôn «đã gửi bài 501», không cần tick «Tạo thêm». Trái với Quyết định 5 của Họa Sĩ («`record_outcome` chỉ chạy sau khi chính lần này đã qua bước so rồi đặt»): đúng với `send_and_record`, sai với `finish_send` (`write.py:2315`). Cũng xảy ra khi ghi «đang gửi» hỏng (`DraftError`, file nháp bận) rồi bị ngắt. Khe ngắt: từ lúc đặt `_wp_sending` tới lúc `apply_send` bỏ dấu (thoát `st.spinner`, các lần ghi phiên trong `apply_send`); với tab thua chỉ vài mili giây (tới 5 giây khi file nháp bận), cần hai tab cùng bài nên **Thấp** | Đánh dấu `holder["claimed"] = True` ngay sau khi so rồi đặt thành công (trước khi gửi); `finish_send` chỉ gọi `record_outcome` khi `claimed`. Thử sửa giả đúng như vậy trên bản sao `git archive`: 2 test `xfail` qua (`--runxfail`). Nên thêm: `record_outcome` ghi kiểu so rồi đặt với `expected=(trạng thái «đang gửi» chính lần này đã ghi, False)`; đóng luôn Rủi ro 1 của Họa Sĩ (kết quả tab 1 ghi đè «đang gửi» của tab 2 đã xác nhận) |

## Thử gộp

| Gộp | Kết quả |
|---|---|
| `team/T-089` + `origin/main` (lúc giao `13e986f`, lúc nộp `0735c5d`) | Không xung đột (`git merge-tree`) |
| `team/T-089` + `origin/team/T-041` (lúc giao `13a554c`, lúc nộp `d2667f7`, cùng sửa `write.py`, `drafts.py`) | Không xung đột |
| Gộp lần lượt `team/T-089` → `main` → `team/T-041` (như Chỉ Huy sẽ làm) | Không xung đột. Chạy test trên cây đã gộp (bản xuất `git archive`, 8 file: test gửi nháp T-086, T-089, `test_soi_loi_t089.py`, và `test_t041_seo_ui.py`, `test_t041_drafts_seo.py` của T-041): **188 qua, 2 xfail** (SL-T089-1), không lỗi do gộp |

## Thử gỡ chỗ sửa (bản sao `git archive` `c0593be`, code như `87ad51c`; chỉ chạy test của Soi Lỗi)

| Đột biến | Kết quả |
|---|---|
| U1 ghi «đang gửi» không so (bỏ `expected`) | bắt được |
| U2 so với lần đọc lúc bấm thay vì lần vẽ trước (`_wp_seen`) | bắt được |
| U3 dựng `SendState` ngoài khối bắt lỗi (LC-T086-1 cũ) | bắt được |
| U4 nháp không có băm vẫn giữ «Đã duyệt» | bắt được |
| U5 khung ảnh không so băm của lần duyệt với ảnh đang hiện | bắt được |
| U6 không lưu băm vào nháp | bắt được |
| U7 nhận băm sai dạng | bắt được |
| U8 băm đi cùng ảnh chưa duyệt | test của Soi Lỗi không bắt: khung ảnh bỏ băm của ảnh chưa duyệt ngay lần vẽ, giao diện không khác. Test mô hình của Họa Sĩ `test_hash_only_valid_with_approval`, `test_hash_kept_with_approval` bắt (3 ca hỏng). Không cần thêm test |

## Soát R5

- `git diff 3d7f4b7..87ad51c -- tests/`: `tests/test_soi_loi_t086.py` chỉ xóa 2 dấu `@pytest.mark.xfail(...)` (SL-T086-1, -2), thân test không đổi; `tests/test_la_chan_t086.py` xóa 1 dấu `xfail` (LC-T086-1) và dòng `import pytest` không còn dùng.
- `tests/test_t086_send_state.py`: 2 hàm giả `save_send_state` thêm `**kwargs` và chuyển tiếp cho hàm thật (để nhận `expected=`); câu kiểm giữ nguyên. Không nới.
- `tests/test_app_images.py::test_open_draft_uses_checked_image_not_draft_fields`: nháp mẫu thêm băm đúng của file (không có băm thì nay phải duyệt lại, đúng yêu cầu 4); câu kiểm giữ nguyên. Không nới.
- Không `skip`, không xóa test.

## U1, W1, W2, F2 (soát nhanh)

- U1: phần mới không thêm `unsafe_allow_html`; câu mới (`MSG_SENT_ELSEWHERE`, `MSG_APPROVED_OTHER_VERSION`, `MSG_OLD_APPROVAL`, `MSG_POST_ID_OUT_OF_RANGE`) là câu cố định; `note` hiện qua `escape_markdown`; băm trong nháp không bao giờ hiện ra (sai dạng thì bỏ).
- W1, W2: vẫn chỉ `create_draft_with_images` (bài luôn nháp); so rồi đặt chỉ chặn thêm, không mở đường ghi mới.
- F2: ảnh xem trước dựng từ đúng byte `ImageLibrary.read_image_bytes` đã đọc để băm.
- Test không gọi mạng thật; WordPress giả của phần trình duyệt chỉ nghe `127.0.0.1`.

## Ghi nhận (không phải lỗi)

1. Tab mở từ **trước** khi file bị thay tại chỗ vẫn giữ kết quả kiểm ảnh trong phiên (khóa theo ảnh, cỡ, giờ sửa): khung ảnh vẫn hiện bản cũ là «Đã duyệt» (nhất quán với băm cũ); bấm gửi thì dừng nhờ so băm. Đã biết từ T-086, chấp nhận.
2. Bấm lại vào bước đang mở trên thanh bước không chạy lại trang (hành vi Streamlit), nên tab không thấy trạng thái gửi mới của tab kia tới thao tác kế tiếp (thấy trên trình duyệt thật). Khóa vẫn đúng lúc bấm gửi (so rồi đặt).
3. Mã bài sai dạng (âm, 0, chữ…): câu của client «WordPress trả về dữ liệu bài viết không đúng dạng. Thử lại sau…» đứng ngay dưới khóa «gửi dở» («bài nháp có thể đã có trên website… kiểm tra trước khi gửi lại»). Không gửi trùng được (phải tick xác nhận), nhưng chữ «Thử lại sau» có thể làm người dùng tick vội. Thuộc `seo_app/wordpress/client.py` (T-088), để Thợ Máy cân nhắc.
4. Quyết định 3 của Họa Sĩ (đọc trạng thái hỏng tạm thời lúc vẽ rồi bấm: báo «trạng thái gửi vừa thay đổi», lần vẽ sau đọc lại): một lần từ chối thừa, hướng an toàn, chấp nhận.

## Kết luận

**ĐẠT CÓ ĐIỀU KIỆN. Chuyển Lá Chắn rút gọn được ngay.** Ba lỗi của phiếu đóng thật bằng đúng cách tái hiện cũ (test cũ gỡ `xfail` qua, trình duyệt thật hai tab ra 1 bài) và các biến thể mới; băm ảnh đã duyệt trong nháp chặn đúng ảnh bị thay kể cả khi mở lại ở phiên mới và gửi thẳng; luồng một tab không bị chặn oan. Điều kiện:

1. SL-T089-1 (Thấp, một chỗ trong `finish_send`, sửa nhỏ): Họa Sĩ sửa luôn trong phiếu này (khuyên, vì đang ở đúng chỗ) hoặc Chỉ Huy lập phiếu theo dõi. Không chặn gộp: so với `main` hiện tại (hai tab bấm gần nhau là ra hai bài) bản này vẫn tốt hơn hẳn.
2. Giữ các test mới khi sửa.

## Bằng chứng

```
$ PYTHONUTF8=1 uv run pytest tests/test_app_images.py tests/test_soi_loi_t056.py \
    tests/test_la_chan_t056.py tests/test_soi_loi_t086.py tests/test_la_chan_t086.py \
    tests/test_storage_drafts.py tests/test_drafts_images.py tests/test_app_pages.py \
    tests/test_t086_send_state.py tests/test_storage_send_state.py \
    tests/test_t089_send_draft.py tests/test_soi_loi_t089.py
474 passed, 1 skipped, 2 xfailed in 1670.74s (0:27:50)   # code 87ad51c; 2 xfail = SL-T089-1

# Trước khi thêm file của Soi Lỗi (8 file của tiêu chí xong + 3 file test T-086, T-089):
443 passed, 1 skipped

# Cây gộp lần lượt team/T-089 (63c4820) → main 0735c5d → team/T-041 d2667f7 (git merge-tree,
# xuất bằng git archive, chạy bằng venv của wt-T-089; T-041 không đổi pyproject.toml, uv.lock):
$ pytest tests/test_t089_send_draft.py tests/test_soi_loi_t089.py tests/test_t086_send_state.py \
    tests/test_soi_loi_t086.py tests/test_la_chan_t086.py tests/test_storage_send_state.py \
    tests/test_t041_seo_ui.py tests/test_t041_drafts_seo.py
188 passed, 2 xfailed in 865.28s (0:14:25)

$ PYTHONUTF8=1 uv run pytest tests/test_soi_loi_t089.py -k keeps_other_tab --runxfail
2 failed   # hỏng đúng câu kiểm: assert state is not None (dòng trạng thái gửi đã bị xóa)
# Bản sao git archive + sửa giả (holder["claimed"], finish_send chỉ ghi lại khi claimed):
2 passed

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan tests/test_soi_loi_t089.py docs/team/reports/T-089-soi-loi.md
"results": {}
```

Máy Windows 11, có agent khác chạy song song. Không đọc `.env`; mật khẩu thử của app, mật khẩu ứng dụng WordPress thử chỉ nằm trong file môi trường tạm của phiên.

## Đối chiếu tiêu chí xong (phần Soi Lỗi)

- [x] 3 lỗi (LC-T086-1, SL-T086-1, SL-T086-2) đóng: cách tái hiện cũ và biến thể (hai tab, hai phiên nhiều vòng, mã bài 2⁶³ trở lên, âm, chữ; file bị thay trước khi chọn, lúc duyệt, giữa lúc gửi; mở lại nháp có băm khác; nháp cũ không có băm; băm sửa tay sai dạng).
- [x] Mọi test T-086 vẫn qua; không chặn oan luồng gửi bình thường; `xfail` gỡ chỉ xóa dấu.
- [x] Thử gộp với `main` và `team/T-041` mới nhất: không xung đột.
- [x] Lỗi mới có test `xfail(strict=True)` mã SL-T089-n; không sửa code ứng dụng.
- [x] Test liên quan và `ruff` (mục «Bằng chứng»). Toàn bộ `uv run pytest` do Chỉ Huy chạy khi gộp.

## Rủi ro và điểm cần chú ý

- `AppTest` không có `fastReruns`: ngắt dựng bằng yêu cầu chạy lại thật (`ScriptRequests.request_rerun`) tới đúng chỗ dừng kế tiếp; hai phiên «cùng lúc» dựng bằng phiên lồng nhau (phiên kia gửi trọn trong lúc phiên này nén ảnh). Phần chạy song song thật dựa vào lần thử trình duyệt ở trên.
- SL-T089-1 không tái hiện được bằng tay trên trình duyệt (khe vài mili giây); bằng chứng là test ngắt thật ở trên.

## Đề xuất

- **Họa Sĩ:** SL-T089-1 theo cột «Gợi ý sửa».
- **Thợ Máy (T-088):** Ghi nhận 3 (chữ «Thử lại sau» khi mã bài sai dạng mà bài có thể đã lên).

## Câu hỏi cho chủ dự án

Không có.

# Báo cáo T-089 · Dọn lỗi Thấp gửi nháp sau T-086, lưu băm ảnh đã duyệt trong nháp

| Mục | Nội dung |
|---|---|
| Agent | Họa Sĩ (`hoa-si`) · model: Claude Opus 5.5 |
| Phiếu | [T-089](../tickets/T-089-gui-nhap-loi-thap-sau-t086.md) |
| Ngày nộp | 2026-10-26 |
| Nhánh | `team/T-089` (từ `main` `3d7f4b7`) |
| Kết quả | Hoàn thành: yêu cầu 1–5; LC-T086-1, SL-T086-1, SL-T086-2 đã sửa, gỡ `xfail` 3 ca (chỉ xóa dấu); băm ảnh đã duyệt lưu trong `DraftImage` (điều kiện 3 của Lá Chắn T-086). Đã thử trên trình duyệt thật với WordPress giả. **Lượt 2 (2026-10-27):** SL-T089-1 đã sửa, ghi kết quả gửi kiểu so rồi đặt (đóng cả Ghi nhận 1 của Lá Chắn T-089), gỡ 2 `xfail` (mục «Lượt 2»). **Lượt 3 (2026-10-27):** SL-T089-2 (lỗi lùi của lượt 2) đã sửa, câu báo khi tab kia đã ghi trạng thái mới nói đúng, gỡ 2 `xfail` (mục «Lượt 3») |

## Lượt 3 (2026-10-27): SL-T089-2, câu báo L2-1

Theo mục «Lượt 2» của báo cáo Soi Lỗi T-089 (SL-T089-2, gợi ý sửa, Ghi nhận L2-1, L2-2) và tin giao việc của Chỉ Huy B.

**Tóm tắt (cho chủ dự án):** bản sửa lượt 2 sinh một lỗi nhỏ ở hai ca rất hiếm: đúng lúc tab đầu đang gửi mà ở tab khác bài bị xóa, hoặc lần gửi cố ý ở tab khác hỏng ngay, thì bài tab đầu vừa tạo không được ghi vào nháp (mở lại bài là hết khóa). Nay khi nháp không còn ghi chú gửi nào, app vẫn ghi lại bài vừa tạo nên mở lại bài vẫn khóa; ghi chú của tab khác (nếu có) vẫn không bị ghi đè. Câu báo khi tab kia đã ghi trạng thái mới nay nói đúng cả khi tab kia đã gửi xong: nháp giữ trạng thái của tab kia, bài của lần này (mã …) cũng đã lên website, hãy kiểm trang quản trị.

| # | Việc | Cách làm | Test |
|---|---|---|---|
| 1 | SL-T089-2: nháp không còn dòng trạng thái gửi lúc đang gửi | `record_outcome` (`app/views/write.py:2268-2269`): so với «đang gửi» của chính lần này hỏng mà kết quả có bài hay chưa rõ (`state` khác `None`) thì ghi thêm một lần với `expected=(None, False)`: chỉ ghi khi nháp **không còn dòng nào**; dòng của tab khác («đang gửi», «đã gửi») vẫn không bị ghi đè. Giữ chốt `claimed` (lớp chặn chính cho tab thua, Ghi nhận L2-2). Lần này chưa tạo gì (`state` là `None`) mà tab khác đã ghi trạng thái mới thì không còn gì để ghi: coi là xong, không báo (`:2277`) | `SL: test_confirmed_send_in_other_tab_failing_first_keeps_this_post`, `SL: test_draft_deleted_elsewhere_while_sending_comes_back_locked` (gỡ `xfail`), `N: test_outcome_recorded_when_send_state_row_gone`, `N: test_nothing_created_and_other_tab_wrote_no_note` |
| 2 | Câu báo khi tab kia đã ghi trạng thái mới (Ghi nhận L2-1) | `record_outcome` đặt `holder["kept_other"]` (`:2282`), `apply_send` chép sang kết quả trên trang (`:2307`); `send_result` hiện câu riêng `kept_other_message` (`:2399`, `:2447`): «Chưa ghi được kết quả gửi vào nháp: một tab khác của app vừa ghi trạng thái gửi mới cho bài này, app không ghi đè; nháp giữ trạng thái gửi của tab kia. Bài nháp của lần gửi này (mã 501) cũng đã có trên website [hay: có thể cũng đã có, khi chưa rõ]. Mở trang quản trị WordPress, kiểm tra Bài viết → Nháp trước khi gửi lại.» Bỏ vế «mở lại nháp sẽ thấy nhắc chưa có kết quả» cho ca này (sai khi tab kia đã gửi xong). Các ca «chưa ghi được» khác (file nháp bận, mã bài lạ) giữ câu cũ (đúng: nháp giữ «đang gửi» của chính lần này) | `N: test_kept_other_message_names_this_post` (tab kia đã gửi xong bài 777), `N: test_kept_other_message_when_result_unsure` (kết quả chưa rõ: không có mã, trang không lỗi); test lượt 2 của Họa Sĩ và Soi Lỗi tìm câu «một tab khác…» vẫn qua |
| 3 | Gỡ 2 `xfail` SL-T089-2 của `tests/test_soi_loi_t089.py` | Cả hai báo `[XPASS(strict)]` trước khi gỡ; chỉ xóa 2 dấu (8 dòng), thân test không đổi | Mục «Bằng chứng lượt 3» |
| 4 | Phạm vi | Chỉ `app/views/write.py` (luồng gửi nháp) và test; không đổi `seo_app/storage/drafts.py`, khối SEO, `seo_app/wordpress/**`, `config/**` | — |

**Thử gỡ chỗ sửa lượt 3** (bản sao `git archive` của `c636e9b` chép thêm `write.py` và hai file test của lượt 3, tức đúng nội dung `8a1ba02`; script `T-089-hoa-si-scripts/mutate_l3.py`):

| Đột biến | Kết quả |
|---|---|
| L3-a bỏ lần ghi thêm khi nháp trống (như lượt 2) | bắt được (3 hỏng: 2 test SL-T089-2 của Soi Lỗi, `N: test_outcome_recorded_when_send_state_row_gone`) |
| L3-b lần ghi thêm không so (`expected=None`, ghi đè cả dòng tab khác) | bắt được (4 hỏng: 2 test lượt 2 của Họa Sĩ, câu báo, `SL: test_confirmed_send_in_other_tab_keeps_its_record`) |
| L3-c câu báo cũ khi tab kia đã ghi (bỏ `kept_other`) | bắt được (2 hỏng) |
| L3-d lần này chưa tạo gì vẫn báo «chưa ghi được» | bắt được (1 hỏng) |
| Không đột biến (9 test trên) | 9 qua |

**Soát R5 lượt 3:** `tests/test_soi_loi_t089.py` chỉ xóa 2 dấu `@pytest.mark.xfail(...)` SL-T089-2; `tests/test_t089_send_draft.py` thêm 4 test, không sửa test cũ. Không `skip`, không xóa test.

**Bảo mật (W1, W2, U1, F2):** không đổi. Lần ghi thêm chỉ ghi trạng thái gửi trong nháp trên máy, chỉ khi nháp không còn dòng nào (không bao giờ ghi đè hay xóa trạng thái của tab khác, không mở khóa thêm); không thêm lệnh nào lên website. Câu báo mới ghép từ câu cố định và mã bài (số nguyên từ website, như các câu kết quả khác); không `unsafe_allow_html`. Dòng trạng thái ghi cho nháp vừa bị xóa ở tab khác chỉ là một dòng nhỏ trong `send_states` (nháp được lưu lại thì khóa đúng; không lưu lại thì dòng nằm yên, không ảnh hưởng gì).

**Bằng chứng lượt 3:**

```
# Trước khi gỡ dấu:
$ uv run pytest tests/test_soi_loi_t089.py -k "failing_first or deleted_elsewhere"
[XPASS(strict)] SL-T089-2: nháp không còn dòng trạng thái gửi thì kết quả gửi bị bỏ (bài đã tạo)
[XPASS(strict)] SL-T089-2: nháp bị xóa ở tab khác lúc đang gửi, tự lưu tạo lại thì không còn khóa

$ PYTHONUTF8=1 uv run pytest tests/test_app_images.py tests/test_soi_loi_t056.py \
    tests/test_la_chan_t056.py tests/test_soi_loi_t086.py tests/test_la_chan_t086.py \
    tests/test_storage_drafts.py tests/test_drafts_images.py tests/test_app_pages.py \
    tests/test_t086_send_state.py tests/test_storage_send_state.py \
    tests/test_t089_send_draft.py tests/test_soi_loi_t089.py -q -rxXf
493 passed, 1 skipped in 755.19s (0:12:35)
# Code 8a1ba02, chạy 09:04 → 09:17. Không còn xfail nào (lượt 2 của Soi Lỗi: 2 xfail SL-T089-2).

# Cây gộp lần lượt nhánh (8a1ba02) → main e8343fa (đã gộp T-088) → team/T-041 f21bc3a (git merge-tree,
# không xung đột; T-041 ghép write_seo ngay sau record_outcome trong send_and_record; xuất bằng
# git archive, chạy bằng venv của wt-T-089; T-041 không đổi pyproject.toml, uv.lock):
$ pytest tests/test_t089_send_draft.py tests/test_soi_loi_t089.py tests/test_t086_send_state.py \
    tests/test_soi_loi_t086.py tests/test_la_chan_t086.py tests/test_storage_send_state.py \
    tests/test_t041_seo_ui.py tests/test_t041_drafts_seo.py tests/test_soi_loi_t041.py \
    tests/test_wordpress_t088.py tests/test_soi_loi_t088.py -q -rxXf
1005 passed, 16 xfailed in 594.71s (0:09:54)
# 16 xfail đều có sẵn ở nhánh khác: 8 của tests/test_soi_loi_t041.py, 8 SL-T088-1; không cái nào của T-089.

$ uv run ruff check .
All checks passed!
```

**Đối chiếu việc lượt 3:**

- [x] SL-T089-2: ghi thêm một lần với `expected=(None, False)` khi so rồi đặt hỏng mà kết quả không phải «chưa gửi»; giữ chốt `claimed`; gỡ 2 `xfail` (chỉ xóa dấu).
- [x] Câu báo «mở lại nháp sẽ thấy nhắc chưa có kết quả» sửa cho ca tab kia đã ghi trạng thái mới (đúng cả khi tab kia đã gửi xong).
- [x] Phạm vi: `app/views/write.py` và test.
- [x] Test liên quan như lượt 2: 493 qua, 0 hỏng; `uv run ruff check .` sạch.
- [ ] Soi Lỗi, Lá Chắn rút gọn lượt 3 (chưa tới lượt).

## Lượt 2 (2026-10-27): SL-T089-1

Theo báo cáo Soi Lỗi T-089 (SL-T089-1, Thấp), biên bản Lá Chắn T-089 (mục «Mức SL-T089-1», Ghi nhận 1, Điều kiện 2) và tin giao việc của Chỉ Huy B.

**Tóm tắt (cho chủ dự án):** lỗi nhỏ cuối cùng của phần «gửi nháp» đã sửa. Trước đây, khi hai tab cùng gửi một bài, tab bị từ chối mà đúng lúc đó lại bị bấm thêm thì app có thể xóa mất ghi chú «đang gửi/đã gửi» của tab kia (mở lại bài là hết khóa). Nay chỉ tab đã thật sự bắt đầu gửi mới được ghi kết quả vào bài, và chỉ ghi khi ghi chú trong bài vẫn là của chính nó: tab bị từ chối không ghi gì; tab khác cố ý gửi thêm trong lúc tab này đang gửi thì kết quả của tab này không xóa ghi chú của tab kia (bài vẫn khóa, trang báo «chưa ghi được kết quả vào nháp»).

| # | Việc | Cách làm | Test |
|---|---|---|---|
| 1 | `holder["claimed"]`: chỉ lần gửi đã ghi được «đang gửi» mới ghi kết quả | `send_and_record` dựng trạng thái «đang gửi» một lần (`app/views/write.py:2196`), ghi kiểu so rồi đặt; ghi được thì đặt `holder["claimed"]` = đúng trạng thái đó (`:2214`), trước khi gửi. Thua tab khác hay ghi hỏng (file nháp bận): không có dấu. `finish_send` chỉ thử ghi lại kết quả khi có dấu (`:2335`); `record_outcome` không có dấu thì không ghi gì (`:2257-2259`) | `SL: test_lost_tab_interrupted_keeps_other_tab_sending`, `…_keeps_other_tab_sent` (gỡ `xfail`), `N: test_pending_not_written_then_interrupted_writes_nothing` (biến thể «file nháp bận» Soi Lỗi nêu) |
| 2 | Ghi kết quả kiểu so rồi đặt (Ghi nhận 1 của Lá Chắn T-089 = Rủi ro 1 lượt 1) | `record_outcome` ghi bằng `save_send_state(…, expected=(claimed, False))` (`:2263`): nháp còn đúng «đang gửi» của lần này thì ghi (kể cả xóa dòng khi chắc chắn chưa tạo gì); tab khác đã ghi «đang gửi» mới (người dùng cố ý tick «Tôi đã kiểm tra…» ở tab kia) thì **không ghi đè**, `note` = `MSG_STATE_CHANGED_ELSEWHERE` (`:187`, `:2275`), trang hiện kết quả của lần này kèm câu «Chưa ghi được kết quả gửi vào nháp (một tab khác của app vừa ghi trạng thái gửi mới cho bài này, app không ghi đè)…»; nháp giữ khóa của tab kia. Lần thử ghi lại ở `finish_send` cũng so như vậy | `N: test_outcome_does_not_overwrite_other_tab_new_send`, `N: test_retry_in_finish_send_also_compares`, `N: test_expected_delete_only_own_state` (kho nháp: xóa dòng kiểu so rồi đặt) |
| 3 | Gỡ 2 `xfail` của `tests/test_soi_loi_t089.py` khi XPASS | Cả hai báo `[XPASS(strict)]` trước khi gỡ; chỉ xóa 2 dấu (8 dòng), thân test không đổi | Mục «Bằng chứng lượt 2» |
| 4 | Phạm vi | Chỉ `app/views/write.py` (luồng gửi nháp) và test; không đổi `seo_app/storage/drafts.py` (`save_send_state` có `expected` từ lượt 1), không đụng khối SEO, `seo_app/wordpress/**`, `config/**` | — |

**Thử gỡ chỗ sửa lượt 2** (bản sao `git archive` của `d5d0e69` chép thêm `write.py` và hai file test của lượt 2, tức đúng nội dung `f2a72f5`; chạy 5 test của SL-T089-1 ở trên; script `T-089-hoa-si-scripts/mutate_l2.py`):

| Đột biến | Kết quả |
|---|---|
| Mã lượt 1 (`d5d0e69`) với test mới | bắt được: 5 hỏng đúng câu kiểm (nháp mất «đang gửi» của tab kia, bị ghi đè `(False, 501)`, lần ghi kết quả không so); `N: test_expected_delete_only_own_state` qua (kho nháp đã đúng từ lượt 1) |
| R2 ghi kết quả không so (giữ chốt `claimed`) | bắt được (2 hỏng) |
| R3 bỏ chốt `claimed` ở `finish_send` và `record_outcome` (giữ ghi kết quả so rồi đặt) | **không bắt**, đúng thiết kế: hai lớp chặn độc lập. Không có dấu thì `expected=(None, False)`, chỉ ghi khi nháp không có dòng nào, nên không xóa, không ghi đè trạng thái tab kia. Chốt giữ để rõ ý (không có «đang gửi» của mình thì không ghi gì) |
| R4 bỏ chốt `claimed` và ghi kết quả không so (như lượt 1) | bắt được (5 hỏng) |
| Không đột biến | 5 qua |

**Soát R5 lượt 2:** `tests/test_soi_loi_t089.py` chỉ xóa 2 dấu `@pytest.mark.xfail(...)`; `tests/test_t089_send_draft.py` thêm 4 test, không sửa test cũ. Không `skip`, không xóa test.

**Bảo mật (W1, W2, U1, F2):** không đổi. Không thêm đường gửi hay lệnh ghi nào lên website (chỉ đổi cách ghi trạng thái trong nháp trên máy). Câu mới `MSG_STATE_CHANGED_ELSEWHERE` cố định, hiện qua `escape_markdown`. Ghi kết quả so rồi đặt chỉ bớt lần ghi (không bao giờ mở khóa thêm).

**Thử gộp** (`git merge-tree`, không đụng thư mục làm việc): `main` cục bộ `11cb2c4` (đã có T-088, T-087), `origin/main` `e295f0e`, `origin/team/T-041` `cdc47d0`, `origin/team/T-088` `7e1fdae`: không xung đột.

**Bằng chứng lượt 2:**

```
# Trước khi gỡ dấu:
$ uv run pytest tests/test_soi_loi_t089.py -k keeps_other_tab
[XPASS(strict)] SL-T089-1: tab thua so rồi đặt bị ngắt thì finish_send ghi đè trạng thái của tab kia
[XPASS(strict)] SL-T089-1: tab thua so rồi đặt bị ngắt thì finish_send xóa «đã gửi» của tab kia

$ PYTHONUTF8=1 uv run pytest tests/test_app_images.py tests/test_soi_loi_t056.py \
    tests/test_la_chan_t056.py tests/test_soi_loi_t086.py tests/test_la_chan_t086.py \
    tests/test_storage_drafts.py tests/test_drafts_images.py tests/test_app_pages.py \
    tests/test_t086_send_state.py tests/test_storage_send_state.py \
    tests/test_t089_send_draft.py tests/test_soi_loi_t089.py -q -rxXf
480 passed, 1 skipped in 1333.04s (0:22:13)
# Code f2a72f5, chạy 07:41 → 08:03 (máy đang bận 93% vì một lượt pytest khác chạy song song).
# Không còn xfail nào trong 12 file (lượt 1: 2 xfail SL-T089-1).

# Cây gộp nhánh (f2a72f5) với main cục bộ 11cb2c4 (đã có T-088 sửa client.py; git merge-tree,
# xuất bằng git archive, chạy bằng venv của wt-T-089; pyproject.toml, uv.lock không đổi):
$ pytest tests/test_t089_send_draft.py tests/test_soi_loi_t089.py tests/test_t086_send_state.py \
    tests/test_soi_loi_t086.py tests/test_la_chan_t086.py tests/test_storage_send_state.py \
    tests/test_wordpress_t088.py tests/test_soi_loi_t088.py -q -rxXf
783 passed, 8 xfailed in 594.34s (0:09:54)
# 8 xfail đều là SL-T088-1 có sẵn trên main (test_soi_loi_t088.py), không phải của T-089.

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan app/views/write.py tests/test_t089_send_draft.py \
    tests/test_soi_loi_t089.py docs/team/reports/T-089-hoa-si.md
"results": {}
```

**Đối chiếu việc lượt 2:**

- [x] SL-T089-1: `holder["claimed"]`; `finish_send` chỉ ghi lại kết quả khi lần này đã ghi được «đang gửi»; ghi kết quả kiểu so rồi đặt (đóng cả Ghi nhận 1 của Lá Chắn T-089).
- [x] Gỡ 2 `xfail` của `tests/test_soi_loi_t089.py` khi XPASS (chỉ xóa dấu); thêm 4 test (có ca ghi kết quả so rồi đặt).
- [x] Phạm vi: `app/views/write.py` và test; không đụng khối SEO của `drafts.py`.
- [x] Test của tiêu chí xong + `tests/test_t086_send_state.py`, `tests/test_storage_send_state.py`, `tests/test_t089_send_draft.py`, `tests/test_soi_loi_t089.py`: 480 qua, 0 hỏng; `uv run ruff check .` sạch.
- [ ] Soi Lỗi, Lá Chắn rút gọn lượt 2 (chưa tới lượt).

Không mở lại app thật cho lượt 2: khe của SL-T089-1 chỉ vài mili giây, bấm tay không tái hiện được (Soi Lỗi cũng ghi vậy); bằng chứng là các test ngắt lần chạy thật ở trên. Luồng gửi bình thường (ghi kết quả so rồi đặt khi không có tab khác) được mọi test gửi nháp của T-056, T-086, T-089 kiểm (nháp ghi đúng «đã gửi, bài 501» sau khi gửi).

## Tóm tắt (cho chủ dự án)

- **Hai tab cùng một bài:** trước đây mở cùng một bài ở hai tab rồi bấm «Gửi nháp» ở cả hai cách nhau vài giây thì ra hai bài nháp. Nay app chỉ ghi «đang gửi» khi trạng thái trong nháp vẫn đúng như lúc bạn bấm (kiểm và ghi trong cùng một bước, hai tab không cùng qua được). Tab tới bước ghi sau không gửi gì, báo «Chưa gửi gì lên website: trạng thái gửi của bài này vừa thay đổi…» và khóa nút. Đã thử thật: hai tab bấm gần như cùng lúc, website giả nhận **đúng 1 bài, 1 ảnh**.
- **Mở lại nháp hôm khác:** app nay lưu «dấu vân tay» (băm) của ảnh lúc bạn duyệt alt ngay trong nháp. Ảnh trên máy bị thay bằng ảnh khác cùng tên (kể cả cùng dung lượng, cùng giờ sửa): mở lại nháp thì app bỏ «Đã duyệt», nhắc xem lại; bấm gửi thẳng ở bước Xuất bản thì app dừng, chưa gửi gì. Nháp cũ (lưu trước bản này) vẫn mở bình thường, chỉ phải tick «Đã duyệt» lại một lần.
- **Ảnh xem trước:** khung ảnh đã chọn nay luôn hiện đúng bản ảnh app đã đọc để kiểm GPS và để duyệt, không còn trường hợp hiện ảnh cũ trong khi app đang xét ảnh mới.
- **Mã bài lạ từ website:** website trả mã bài số cực lớn (chỉ khi website hỏng) thì trang không còn báo lỗi kỹ thuật lặp lại; app hiện kết quả, nhắc «chưa ghi được kết quả vào nháp», vẫn khóa nút.

## Yêu cầu → cách làm → test

`N:` là `tests/test_t089_send_draft.py` (mới, 19 hàm test, 29 ca), `SL:` `tests/test_soi_loi_t086.py`, `LC:` `tests/test_la_chan_t086.py`, `T:` `tests/test_t086_send_state.py`.

| # | Yêu cầu | Cách làm | Test |
|---|---|---|---|
| 1 | LC-T086-1: dựng `SendState` trong `try` của `record_outcome`; mã bài ngoài khoảng thì câu cố định, không lặp lỗi | `record_outcome` (`app/views/write.py:2239`) dựng `SendState` trong khối bắt lỗi; `DraftError` → câu của kho nháp, `ValueError` (pydantic `ValidationError`) → câu cố định `MSG_POST_ID_OUT_OF_RANGE` (`:176`), lỗi khác → «lỗi không mong đợi». Nháp giữ «đang gửi» (khóa «gửi dở»); `finish_send` thử ghi lại cũng chỉ ra câu đó | `LC: test_lc_t086_1_huge_post_id_from_site_does_not_break_page` (gỡ `xfail`), `N: test_huge_post_id_fixed_note_and_lock`, `N: test_huge_post_id_when_run_interrupted` (ngắt lần chạy thật: đường `finish_send`) |
| 2 | SL-T086-1: ghi «đang gửi» kiểu so rồi đặt trong một giao dịch; tab thứ hai bị khóa, có câu nhắc | `DraftStore.save_send_state(…, expected=(trạng thái, hỏng))` (`seo_app/storage/drafts.py:658`): `BEGIN IMMEDIATE` (giữ khóa ghi từ lúc đọc tới lúc ghi, `:677`), đọc bằng `_read_send_state` (`:747`, dùng chung với `load_send_state`), khác thì không ghi, trả `False`. `draft_panel` nhớ trạng thái ở lần vẽ người dùng đã thấy (`_wp_seen`, `write.py:2427`); `send_and_record` ghi «đang gửi» với `expected=seen`, không ghi được thì không gửi, `MSG_SENT_ELSEWHERE` (`:186`, `:2205`); lần vẽ sau khóa theo trạng thái trong nháp, ô xác nhận đã bỏ tick | `SL: test_other_tab_starts_sending_while_this_tab_prepares` (gỡ `xfail`), `N: test_expected_state_unchanged_is_written`, `…_changed_state_is_not_overwritten`, `…_broken_row_seen_as_broken`, `…_only_one_tab_wins` (4 luồng, đọc chậm lại: đúng 1 luồng ghi được, 3 luồng thấy trạng thái mới), `…_second_tab_locked_with_clear_message`, `…_ticked_confirmation_not_reused_for_new_send_elsewhere`, `…_two_sessions_create_more_only_once` (hai phiên AppTest); trình duyệt thật |
| 3 | SL-T086-2: ảnh xem trước dựng từ đúng byte đã băm | `web_info` (`write.py:871`) đọc file một lần: băm, `make_preview` (`:890`), rồi nén thử WebP để ra dòng GPS; giữ ảnh xem trước JPEG nhỏ trong phiên cùng kết quả (tối đa `MAX_WEB_INFO_KEPT` = 40 phiên bản). `slot_preview` (`:1063`) hiện ảnh xem trước của `web_info` thay vì `PreviewCache` (cache theo cỡ, giờ sửa). Lưới chọn ảnh vẫn dùng `PreviewCache` | `SL: test_preview_shown_matches_approved_content` (gỡ `xfail`), `N: test_chosen_preview_built_from_hashed_bytes` (ảnh hiện ra là `make_preview` của đúng byte có băm bằng băm của lần duyệt) |
| 4 | Lưu băm ảnh đã duyệt trong `DraftImage`; mở lại nháp mà ảnh khác băm thì bắt duyệt lại; nháp cũ vẫn mở | `DraftImage.approved_sha256` (`drafts.py:238`): chỉ nhận 64 chữ số hex thường, sai dạng thì bỏ băm (ảnh giữ); chưa duyệt hay ảnh AI chưa có file thì không có băm (`:292`); trống thì không ghi vào JSON (`exclude_if`, nháp giữ đúng khuôn cũ). Trang: `slot_texts` lưu `altsha-<id>` vào nháp (`write.py:756`); `set_pick` khôi phục băm từ nháp (`:731`, ghi sau cùng); `alt_editor` thấy ảnh đang hiện khác băm của lần duyệt thì bỏ «Đã duyệt» trước khi vẽ ô, báo `MSG_APPROVED_OTHER_VERSION` (`:1218`); lần gửi so byte sắp tải với băm (có sẵn từ T-086, nay có cả khi gửi thẳng sau khi mở lại nháp). Nháp không có băm: `restore_images` bỏ «Đã duyệt», báo một lần `MSG_OLD_APPROVAL` (`:487`) | `N: test_hash_kept_with_approval`, `…_hash_only_valid_with_approval` (11 ca), `…_hand_edited_hash_drops_hash_not_image`, `…_old_draft_without_hash_opens`, `…_approval_hash_saved_and_restored`, `…_reopened_draft_file_replaced_stops_send`, `…_reopened_draft_file_replaced_unapproved_on_view`, `…_reopened_draft_same_file_stays_approved`, `…_old_draft_without_hash_needs_new_approval`; trình duyệt thật |
| 5 | Giữ mọi test của T-086; gỡ `xfail` khi XPASS | Cả 3 ca báo `XPASS(strict)` trước khi gỡ; chỉ xóa dấu (và `import pytest` thừa ở `test_la_chan_t086.py`). Mọi test T-086 (ngắt ở từng lần ghi, ngắt hai lần, trạng thái sửa tay, mã bài trong nháp không dùng để ghi lên website) vẫn qua | Mục «Bằng chứng», «Soát R5» |

## Quyết định thiết kế cần Soi Lỗi, Lá Chắn xem

1. **So với trạng thái ở lần vẽ trước, không với lần đọc lúc bấm.** `seen` là trạng thái gửi app đọc ở lần vẽ người dùng đã thấy khi bấm (`_wp_seen`). Lý do: ô «Tôi đã kiểm tra…» hay «Tạo thêm một bài nháp mới» đã tick sẵn là xác nhận cho trạng thái người dùng thấy; tab khác bắt đầu một lần gửi mới (trạng thái khác) thì xác nhận cũ không được dùng cho lần gửi đó (`N: …_ticked_confirmation_not_reused…`, `…_two_sessions_create_more_only_once`). Không có `_wp_seen` (chưa vẽ lần nào) thì dùng lần đọc lúc bấm. `_wp_seen` nằm trong `COMPOSE_KEYS` (mở bài khác là bỏ).
2. **«Khác» là khác bất kỳ trường nào** (`pending`, `post_id`, `updated_at`): cùng «đang gửi» nhưng ghi lúc khác là lần gửi khác. Đồng hồ Windows nhảy 15,6 ms một lần; hai lần ghi chỉ có thể trùng giờ khi cách nhau dưới 15,6 ms, còn giữa lần vẽ người dùng thấy và cú bấm luôn có thao tác của người (lâu hơn nhiều).
3. **Dòng trạng thái hỏng:** người dùng thấy «không đọc được trạng thái gửi» và xác nhận thì ghi được khi dòng vẫn hỏng (`seen_broken`); dòng hỏng thành dòng đọc được (hay ngược lại) thì không ghi. Đọc hỏng tạm thời (file nháp bận) lúc vẽ rồi bấm: không gửi, báo «trạng thái gửi vừa thay đổi», lần vẽ sau đọc lại (hướng an toàn).
4. **Mở rộng `save_send_state` bằng `expected` thay vì thêm hàm mới:** ghi «đang gửi» vẫn đi qua đúng hàm cũ (test T-086 theo dõi hàm này vẫn đúng). Các lần ghi khác (kết quả gửi, test) không truyền `expected`, ghi luôn như trước. Hàm nay trả `True`/`False`.
5. **Ghi kết quả (`record_outcome`) không so** (lượt 1): chỉ chạy sau khi chính lần này đã qua bước so rồi đặt. Soi Lỗi tìm ra `finish_send` vẫn gọi lại cho lần gửi chưa qua bước đó (SL-T089-1). **Lượt 2:** chỉ lần có dấu `claimed` mới ghi, và ghi kiểu so rồi đặt (mục «Lượt 2»).
6. **Ảnh xem trước của ảnh đã chọn đi cùng `web_info`:** `make_preview` (được phép theo LC-T058-2) trên đúng byte đã băm; đọc cấu hình ảnh (`load_image_settings`) chuyển xuống sau khi có ảnh xem trước, nên `config/content.toml` sai vẫn thấy ảnh. `test_st_image_only_gets_preview_cache_bytes` vẫn qua không sửa: `make_preview` cho cùng byte với `PreviewCache.get` khi cùng file (mã hóa JPEG cố định).
7. **Băm trong nháp:** trường tùy chọn, không đổi `SCHEMA_VERSION` (nháp khuôn 2 có hay không có trường đều mở được; bản app cũ mở nháp có băm thì coi ảnh đó là ảnh hỏng, bỏ ảnh, giữ chữ). Sai dạng thì bỏ băm thay vì bỏ ảnh (người dùng chỉ phải duyệt lại). Dùng `Field(exclude_if=…)` của pydantic (có từ 2.11; `uv.lock` khóa 2.14.1), không thêm thư viện.
8. **Nháp cũ không có băm: bỏ «Đã duyệt» khi mở** (cách Lá Chắn T-086 Ghi nhận 1 đề xuất), thay vì gắn băm của file hiện tại lúc xem khung ảnh như T-086: không so được ảnh với lúc duyệt thì người dùng xem lại. Chỉ ảnh trong thư mục ảnh; ảnh AI chưa có file không bị ảnh hưởng.
9. Lần duyệt mà `web_info` không đọc được ảnh (ổ chậm) vẫn không có băm như T-086 (Soi Lỗi T-086 Ghi nhận 2); nháp lưu lần duyệt đó, mở lại thì phải duyệt lại (câu báo nói «ví dụ nháp lưu trước bản cập nhật này»).

## Yêu cầu bảo mật riêng (tự soát)

| Mã | Kết quả |
|---|---|
| W1 | Không đổi đường gửi: vẫn chỉ `create_draft_with_images` (bài luôn `draft`), không thêm `publish`/`future`. So rồi đặt chỉ chặn thêm (không ghi được «đang gửi» thì không gửi) |
| W2 | Không thêm lệnh sửa, xóa nào lên website. Mã bài trong nháp vẫn chỉ để hiện, dựng link và ghi lại vào «đang gửi» lần sau (`test_saved_post_id_never_used_to_write_to_wordpress` vẫn qua). Mã bài cực lớn chỉ hiện ra (số), không ghi vào nháp |
| U1 | Không thêm `unsafe_allow_html`. Chữ mới: câu cố định (`MSG_*`), số ảnh (`int`), câu lỗi qua `escape_markdown` (`send_result`); băm không hiện ra giao diện |
| F2 | Đọc ảnh vẫn qua `ImageLibrary.read_image_bytes` (giới hạn cỡ, điểm ảnh, chặn lối tắt như cũ); ảnh xem trước, băm, dòng GPS cùng một lần đọc; ảnh web vẫn giữ GPS (`make_web_image` không đổi). Băm trong nháp là dữ liệu chưa tin cậy: chỉ nhận đúng dạng hex, chỉ dùng để so, không bao giờ thay cho lần đọc file |

Thêm: S1 `detect-secrets` sạch (mục «Bằng chứng»); D1 không thêm thư viện, `uv.lock` không đổi.

## Soát R5 (test của agent khác, test cũ)

| File | Thay đổi |
|---|---|
| `tests/test_la_chan_t086.py` | Xóa dấu `xfail` LC-T086-1 và dòng `import pytest` không còn dùng (ruff F401); thân test không đổi |
| `tests/test_soi_loi_t086.py` | Xóa 2 dấu `xfail` (SL-T086-1, SL-T086-2); thân test không đổi |
| `tests/test_t086_send_state.py` | Hai hàm giả `flaky`, `busy` nhận thêm `**kwargs` (và `flaky` chuyển tiếp) vì `save_send_state` nay nhận `expected=`; logic, câu kiểm không đổi |
| `tests/test_app_images.py` | `test_open_draft_uses_checked_image_not_draft_fields`: nháp mẫu thêm `approved_sha256` đúng của file (nháp không có băm nay phải duyệt lại, yêu cầu 4; ca đó có test riêng `N: …_old_draft_without_hash_needs_new_approval`); câu kiểm không đổi; thêm `import hashlib` |

Không `skip`, không xóa test.

## Thử gỡ chỗ sửa

Bản sao `git archive` của `ccad396` trong thư mục tạm, `PYTHONPATH` trỏ bản sao, môi trường của worktree; mỗi đột biến chạy các test nên bắt nó (script `T-089-hoa-si-scripts/mutate_t089.py` trong ghi chú bàn giao). Đối chứng: bản sao không đột biến, đúng các test đó: 32 qua.

| Đột biến | Kết quả |
|---|---|
| M1 dựng `SendState` ngoài khối bắt lỗi (như trước LC-T086-1) | bắt được |
| M2 ghi «đang gửi» không so (bỏ `expected`) | bắt được |
| M3 so rồi đặt không giữ khóa ghi từ đầu (bỏ `BEGIN IMMEDIATE`) | bắt được (`N: test_only_one_tab_wins`) |
| M4 so với lần đọc lúc bấm thay vì lần vẽ trước | bắt được |
| M5 khung ảnh lấy ảnh xem trước từ cache theo cỡ, giờ sửa (như trước SL-T086-2) | bắt được |
| M6 không lưu băm vào nháp | bắt được |
| M7 mở lại nháp không khôi phục băm | bắt được |
| M8 khung ảnh không so với băm của lần duyệt trước | bắt được |
| M9 nháp cũ không có băm vẫn giữ «Đã duyệt» | bắt được |
| M10 băm trong nháp không kiểm dạng | bắt được |
| M11 băm không bỏ khi bỏ duyệt | bắt được |

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `app/views/write.py` | `record_outcome` bắt lỗi dựng `SendState`; `draft_panel` nhớ `_wp_seen`, `send_draft`/`send_and_record` ghi «đang gửi» với `expected`; `web_info` dựng ảnh xem trước từ byte đã băm, `slot_preview` dùng nó; `set_pick`, `slot_texts`, `restore_images`, `alt_editor` lưu, khôi phục, so băm của lần duyệt; câu báo mới |
| `seo_app/storage/drafts.py` | `save_send_state(expected=…)` so rồi đặt trong một giao dịch `BEGIN IMMEDIATE`; `_read_send_state` dùng chung; `DraftImage.approved_sha256` (khuôn chặt, không ghi khi trống) |
| `tests/test_t089_send_draft.py` (mới) | 29 ca: LC-T086-1, so rồi đặt (kho nháp, nhiều luồng, hai phiên), ảnh xem trước, băm trong nháp (khuôn, mở lại, file bị thay, nháp cũ) |
| `tests/test_la_chan_t086.py`, `tests/test_soi_loi_t086.py`, `tests/test_t086_send_state.py`, `tests/test_app_images.py` | Mục «Soát R5» |
| `docs/team/reports/T-089-hoa-si.md` | Báo cáo này |

Không sửa `seo_app/wordpress/**`, `seo_app/onpage/**`, `config/**`, khối SEO của `drafts.py`, bước 4 SEO của `write.py`.

## Bằng chứng

```
$ PYTHONUTF8=1 uv run pytest <39 file: 8 file của tiêu chí xong (test_app_images, test_soi_loi_t056,
    test_la_chan_t056, test_soi_loi_t086, test_la_chan_t086, test_storage_drafts, test_drafts_images,
    test_app_pages) + mọi file test đụng trang Soạn bài hay kho nháp (test_t086_send_state,
    test_storage_send_state, test_t089_send_draft, test_soi_loi_t055, test_la_chan_t076,
    test_soi_loi_t076, test_app_drafts, test_wordpress_images, …)> -q -rxXf
3908 passed, 18 skipped, 8 xfailed in 1020.63s (0:17:00)
# Code ccad396, chạy 14:47 → 15:04. 8 xfail đều có sẵn ở file cũ (test_soi_loi_round4 × 2,
# test_soi_loi_t003_t009 × 1, test_soi_loi_t081 × 5). tests/test_soi_loi_t086.py,
# tests/test_la_chan_t086.py không còn xfail.

# Trước khi gỡ dấu, mỗi ca báo XPASS(strict):
$ uv run pytest tests/test_la_chan_t086.py            # sau phần 1
[XPASS(strict)] LC-T086-1: mã bài website trả từ 2⁶³ làm record_outcome ném lỗi ngoài khối bắt
$ uv run pytest tests/test_soi_loi_t086.py …          # sau phần 2, phần 3
[XPASS(strict)] SL-T086-1: hai tab cùng một nháp, bấm gửi cách nhau vài giây vẫn ra hai bài
[XPASS(strict)] SL-T086-2: ảnh xem trước lấy từ cache theo cỡ, giờ sửa: duyệt gắn với ảnh chưa thấy

$ uv run ruff check .
All checks passed!
$ uv run ruff format --check <7 file .py đã đổi>
7 files already formatted

$ PYTHONUTF8=1 uvx detect-secrets scan <7 file đã đổi>
"results": {}

$ git merge-tree --write-tree HEAD <nhánh>   # thử gộp, không đụng thư mục làm việc
main (cục bộ, 3d7f4b7 = gốc nhánh): đã nằm trong nhánh
origin/team/T-041 (eac0431): không xung đột
origin/team/T-088 (1e87ce8): không xung đột
```

Máy Windows 11, có phiên khác chạy song song. Không đọc `.env`.

### Mở app thật (cổng 8505, WordPress giả)

Cấu hình tạm `wt-T-089-hoa-si` trong `D:\ProMetal-ToolSEO\.claude\launch.json` (không start `seo-app-main`), `uv run --env-file <file tạm>`; ảnh giả Pillow (có một ảnh 6000×4000), mật khẩu thử tạo trong phiên, bốn nháp mẫu dựng bằng script (ghi chú bàn giao `T-089-hoa-si-scripts/`). WordPress giả: bản sao script của Soi Lỗi T-056 (thêm tham số «mã bài đầu»), `https://localhost:8745`, chỉ nghe `127.0.0.1`, chứng chỉ tự ký mới cho `localhost` chỉ dùng cho lần thử, app vẫn kiểm chứng chỉ (`REQUESTS_CA_BUNDLE`). Không gửi gì tới website thật, không đọc `.env`.

| Ca | Kết quả |
|---|---|
| Nháp A ở hai tab (hai phiên), cả hai ở bước Xuất bản, nút «Gửi nháp» đều bật; bấm ở tab 1 rồi ngay sau đó ở tab 2 | WordPress giả: **1 bài (501), 1 ảnh** (`requests-lan1-hai-tab.jsonl`, 7 request). Lần này tab 2 ghi «đang gửi» trước (hai lần chạy gần như song song; tab nào qua trước không quan trọng, chỉ một tab qua): tab 2 «Đã tạo bài nháp trên WordPress (mã 501), kèm 1 ảnh», khóa «đã gửi»; tab 1 «Chưa gửi gì lên website: trạng thái gửi của bài này vừa thay đổi (thường do bài vừa được gửi, hoặc đang gửi, ở một tab khác của app)…», khóa «gửi dở», ô «Tôi đã kiểm tra…» bỏ tick, nút khóa. Nháp ghi `{"pending":false,"post_id":501,…}` |
| Nháp B (alt đã duyệt, có băm); file bị thay tại chỗ bằng ảnh đỏ có GPS, cùng cỡ, cùng giờ sửa; mở nháp | Khung ảnh hiện **ảnh đỏ mới**, dòng «📍 Ảnh có vị trí GPS» của file mới, ô «Đã duyệt» bỏ tick, câu «Ảnh này khác bản bạn đã duyệt trước đó (file đã bị thay bằng ảnh khác cùng tên) nên app đã bỏ «Đã duyệt»…» |
| Nháp C (alt đã duyệt, **không** có băm, như nháp cũ); mở nháp | Mở bình thường; câu «1 ảnh có alt đã duyệt nhưng nháp không có «dấu vân tay» của ảnh lúc duyệt… nên app đã bỏ «Đã duyệt»…», ô bỏ tick. Tick lại: nháp lưu băm đúng của file (`df8396e6c393…` = SHA-256 của `IMG_0001.jpg`) |
| Nháp D; WordPress giả trả mã bài 2⁶³ (`9223372036854775808`) | Trang không lỗi: «Đã tạo bài nháp trên WordPress (mã 9223372036854775808), kèm 1 ảnh», «Chưa ghi được kết quả gửi vào nháp (website trả mã bài nháp lớn bất thường, app không ghi được vào nháp)…», khóa «gửi dở»; bấm tiếp (tick ô xác nhận) trang vẫn không lỗi. Log app: không lỗi; console trình duyệt: không lỗi. Nháp giữ `{"pending":true,…}` |

Xong: dừng app, dừng WordPress giả, trả `launch.json` về đúng bản cũ (so từng byte, SHA-256 `a5607e8c…f169`), xóa `data/` của worktree; cổng 8505, 8745 đã đóng.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1–5, có test (bảng trên).
- [x] Test liên quan qua (8 file trong phiếu cùng mọi file test đụng trang Soạn bài, kho nháp), `uv run ruff check .` sạch (mục «Bằng chứng»). Toàn bộ `uv run pytest` do Chỉ Huy chạy khi gộp.
- [x] Báo cáo tại `docs/team/reports/T-089-hoa-si.md`.
- [ ] Soi Lỗi, Lá Chắn rút gọn (chưa tới lượt).

## Rủi ro và điểm cần chú ý

1. ~~**Ghi kết quả không so** (Quyết định 5): nếu trong lúc lần gửi của tab 1 đang chạy, người dùng ở tab 2 **cố ý** tick «Tôi đã kiểm tra…» (thấy «đang gửi» của tab 1) rồi gửi tiếp, thì kết quả của tab 1 ghi đè dấu «đang gửi» của tab 2.~~ **Đã đóng ở lượt 2:** kết quả ghi kiểu so rồi đặt với đúng «đang gửi» của lần đó (mục «Lượt 2»).
2. Bản app cũ (trước T-089) mở nháp có băm thì bỏ ảnh đó như ảnh hỏng (phần chữ giữ). Chỉ xảy ra khi quay về bản cũ.
3. Lần so rồi đặt đợi tối đa 5 giây khi tab khác đang giữ file nháp (`_SQLITE_TIMEOUT`); quá thì báo «File nháp đang bận», chưa gửi gì.
4. Ảnh xem trước của ảnh đã chọn không còn lấy từ cache trên ổ: mỗi phiên dựng lại một lần cho mỗi phiên bản file (ảnh 24 MP khoảng 0,35 giây, cùng lúc với lần nén thử WebP vốn đã có).
5. `AppTest` không có fastReruns; phần hai tab bấm gần như cùng lúc dựa vào test nhiều luồng của kho nháp và lần thử trình duyệt thật ở trên.

## Đề xuất

- **Thợ Máy (sau T-088):** giới hạn trên cho `_positive_id` của client (phòng nhiều lớp cho LC-T086-1, phần không bắt buộc của Lá Chắn T-086).
- **Thư Ký:** khi viết lại «Lời dặn tạm thời» của README (điều kiện 6 Lá Chắn T-086): nay mở cùng một bài ở hai tab không còn tạo hai bài nháp; nháp lưu trước bản này phải tick «Đã duyệt» lại một lần.

## Câu hỏi cho chủ dự án

Không có.

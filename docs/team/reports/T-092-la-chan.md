# Biên bản bảo mật T-092 · Nháp bị xóa ở tab khác: tự lưu không tạo lại, khóa gửi trùng theo điều tab biết · rút gọn (W1, W2, U1)

> **Model:** **Fable 5.1** (dòng «You are powered by»: Fable 5.1, kiểm đầu lượt). Chỉ Huy B giao 05/11 sau lượt 2 của Họa Sĩ. Soi Lỗi chưa kiểm lại lượt 2: biên bản này xác nhận thay việc SL-T092-1 đã đóng và hai dấu `xfail` đã gỡ đúng.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: **Fable 5.1** · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-092](../tickets/T-092-nhap-bi-xoa-o-tab-khac.md): Họa Sĩ lượt 1 (`acb54b1`, `7860e99`, `bc8a611`), Soi Lỗi rút gọn `c82c82e` (ĐẠT CÓ ĐIỀU KIỆN, **SL-T092-1** Thấp, ghi nhận G1), gộp `main` `bad6db7` (`16894d1`), Họa Sĩ lượt 2 **`bd03af9`** (đầu nhánh, đã push) |
| Phạm vi | **Rút gọn** (W1, W2, U1) theo trọng tâm Chỉ Huy giao: toàn bộ diff `bad6db7..bd03af9`, 9 file (`app/views/write.py`: tự lưu, khung báo, tạo lại, khóa bước Xuất bản, chú thích, câu từ khóa; `seo_app/storage/drafts.py`: `save(must_exist)`, `send_state_if_exists`, `DraftGoneError`; `.env.example`; `tests/test_t092_nhap_bi_xoa.py` mới 27 test; `tests/test_soi_loi_t092.py`; `tests/test_soi_loi_t089.py`, `tests/test_t041_seo_ui.py` đổi theo R5; 2 báo cáo). Đọc cùng code không đổi mà phiếu dựa vào: `publish_panel`, `send_draft`, `send_and_record`, `record_outcome`, `finish_send` (luồng gửi T-086/T-089), `DraftStore.delete`, `save_send_state`, `COMPOSE_KEYS`, `DRAFT_FLAGS`, `open_draft`. Không gọi website thật, không chạy cloud |
| Ngày | 2026-11-05 11:12 → 12:32 (+07, giờ máy đo bằng `date`) |
| Máy | Windows 11 Pro 10.0.26300, Python 3.12.15, uv 0.13.4. Chỉ chạy test liên quan (15 file), không chạy toàn bộ |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN**, **gộp `main` được ngay** (`main` `8caab2f`: `git merge-tree` không xung đột; từ gốc gộp `bad6db7` `main` không đụng file nào của phiếu): 0 Nghiêm trọng, 0 Cao, 0 Trung bình, **0 Thấp mới**. **SL-T092-1 đã đóng** ở lượt 2 (đọc mã, chạy test, thử riêng; xác nhận thay Soi Lỗi); **G1 đóng** cho tab đã biết bài. Hai dấu `xfail` gỡ đúng (chỉ xóa dấu và `import pytest` thừa, thân test không đổi). Điều kiện chỉ là khuyến nghị cho lúc bật công tắc Hẹn giờ / Đăng ngay và một việc duyệt R5 (mục «Điều kiện») |

## Tóm tắt (cho chủ dự án)

Bản sửa **an toàn để gộp**. Tôi đọc lại từ đầu và thử riêng, không dựa vào kết quả của Họa Sĩ, Soi Lỗi:

- **Xóa nháp ở tab này không còn làm tab kia lặng lẽ tạo lại nháp.** Tab kia hiện khung vàng, hỏi «Lưu lại thành nháp» hay «Bỏ bài này». Phép kiểm «nháp còn không» và phép ghi nằm trong **một** giao dịch giữ khóa, nên lần xóa ở tab khác không chen vào giữa được.
- **Lỗi nhỏ Soi Lỗi tìm ra đã sửa đúng:** tab đã thấy bài được gửi thì nút gửi (Nháp, Hẹn giờ, Đăng ngay) **vẫn khóa** sau khi nháp bị xóa ở tab khác, kể cả khi một tab thứ ba lưu lại nháp mà không biết bài đã gửi. Muốn gửi tiếp vẫn phải tự tick «Tạo thêm một bài mới…» như trước. Cú bấm lọt qua nút khóa cũng không gửi gì.
- **Không mở thêm đường nào lên website**, không xóa gì trên website hay trong kho nháp; chữ hiện ra là câu cố định.
- **Còn một khoảng hở nhỏ, đúng phạm vi phiếu:** tab chưa từng thấy bài được gửi (bài gửi rồi xóa ngay ở tab khác, trong lúc tab này không chạy lần nào) thì không có gì để khóa; khung báo nói rõ điều này. Bịt hẳn cần một thay đổi thiết kế nhỏ (giữ dấu «đã gửi» khi xóa nháp), tôi ghi ở mục «Điều kiện» để anh/chị và Chỉ Huy quyết trước khi bật Hẹn giờ / Đăng ngay.
- **Việc của anh/chị lúc này:** không có.

## Kết quả theo trọng tâm Chỉ Huy giao

### 1. Không còn đường nào ra bài thứ hai trên website (SL-T092-1, G1) — **đạt**

- **Khóa theo điều tab biết:** `send_lock_state` (`app/views/write.py:4109-4128`). Kho có trạng thái gửi, hay dòng hỏng: khóa theo kho như T-086. Kho đọc ra «chưa gửi»: lấy `known_send_state(own_send=False)` (`:898-924`, gộp lần đọc cuối khi nháp còn `_draft_send_known` và lần đọc ở bước Xuất bản `_wp_seen`, dòng muộn nhất thắng; lần đọc hỏng thì «gửi dở»). Bài **có mã** → khóa «đã gửi» luôn. «Gửi dở» **chưa có mã** → khóa chỉ khi nháp không còn trong kho (`send_state_if_exists`); không kiểm được (kho bận) → khóa (hướng an toàn, probe P4). Nháp còn mà kho «chưa gửi» = lần gửi đó đã xong mà chưa tạo gì (LC-T089-1): không khóa oan.
- **`publish_panel` (`:4349-4362`)** lấy `post_id`, `locked`, câu báo từ `lock`; `allowed` chỉ bị **thu hẹp thêm** (`allowed and checked`, `allowed and again`); cú bấm lọt vẫn qua `if clicked and allowed` xét trong cùng lần chạy. Ba hình thức chung một hàm, nên Hẹn giờ / Đăng ngay cũng khóa. Lần gửi vẫn so rồi đặt với **đúng** trạng thái trong kho (`seen`, `:4288-4289`): tick xác nhận rồi gửi thì gửi được một bài, kho ghi «đã gửi» bài đó (dòng chưa có nháp đi kèm, vô hại; «Lưu lại» giữ đúng dòng đó vì `recreate_draft` so rồi đặt với «chưa gửi»).
- **Ba tab (G1):** `kept_send_knowledge` (`:927-938`): lần đọc kho «chưa gửi» khi nháp còn không xóa bài có mã tab đã biết («chỉ lên, không xuống»). Đúng vì luồng gửi không bao giờ đưa nháp đã có bài về «chưa gửi» (lần gửi hỏng trả về đúng trạng thái trước nó, LC-T089-1; `delete` là lối duy nhất xóa dòng), nên «chưa gửi» ở đây chỉ là nháp bị xóa rồi lưu lại không kèm trạng thái.
- **Điều tab biết không đi theo bài khác:** `_draft_send_known` nằm trong `DRAFT_FLAGS` (`:215-224`), `_wp_seen` trong `COMPOSE_KEYS` (`:182`); `open_draft` (`:648`) và «Bỏ hẳn» (`discard_gone_draft`, `:887`) gọi `clear_compose` + `forget_draft` nên xóa cả hai (probe P2, P3: mở nháp khác hay bỏ hẳn thì không khóa oan).
- **Khoảng hở còn lại** (ngoài phạm vi «tab đó đang biết» của phiếu; Họa Sĩ Rủi ro 1, Soi Lỗi G1 với phiên mới): tab chưa từng thấy lần gửi thì không có gì để khóa; `MSG_GONE_UNKNOWN` nói rõ. Bịt hẳn: Đề xuất 1 của Họa Sĩ (điều kiện B1).

### 2. So rồi đặt trong giao dịch — **đạt**

- `DraftStore.save(..., must_exist=True)` (`seo_app/storage/drafts.py:876-911`): `BEGIN IMMEDIATE` giữ khóa ghi từ lúc kiểm `SELECT 1 FROM drafts` tới lúc `INSERT OR REPLACE`; không còn thì `DraftGoneError` (câu cố định `_MSG_DRAFT_GONE`), `with conn` cuộn lại. Lần xóa ở tab khác (`delete`, `:993-999`, xóa cả hai bảng trong một giao dịch) phải đợi.
- `send_state_if_exists` (`:1011-1025`): `BEGIN` một giao dịch đọc cho cả phép kiểm nháp lẫn phép đọc trạng thái, không lẫn «nháp còn, chưa gửi» với «vừa bị xóa»; dòng hỏng trả `(None, True)`.
- `autosave` (`:983-1020`): chỉ so rồi đặt khi nháp đã có trong kho (`_draft_saved_at`); nháp mới lần đầu vẫn tạo như cũ. `recreate_draft` (`:941-959`): ghi trạng thái gửi `expected=(None, False)` **trước**, nháp **sau**; dòng có sẵn mới hơn thì giữ nguyên.
- Test Họa Sĩ khóa đúng từng chỗ: `…_check_and_write_in_one_write_transaction`, `…_reads_in_one_transaction`, `…_deleted_between_check_and_save_is_not_recreated`, `…_writes_send_state_before_draft` (2 ca), `…_keeps_newer_row_written_after_delete`; đột biến M3, M4, M6, M7 bị bắt.

### 3. Nháp cũ vẫn mở được — **đạt**

`load`, `open_draft` không đổi; `must_exist` chỉ xét có dòng, không xét khuôn. Họa Sĩ `test_old_draft_still_opens_and_saves` (khuôn 1, trước T-055); `tests/test_app_drafts.py`, `tests/test_storage_drafts.py` trong lô test dưới; Soi Lỗi đã chạy `test_drafts_images`, `test_t100_drafts_plan` (khuôn 1, 2).

### 4. Không lùi T-086, T-089 — **đạt**

- Diff không chạm `send_draft`, `send_and_record`, `record_outcome`, `finish_send`, `apply_send`; chỉ **đọc** `_wp_seen`, `_wp_sent`, `_wp_maybe_draft`, `_wp_result`. Khóa đơn điệu, so rồi đặt «đang gửi», chỉ lần gửi giành được mới ghi kết quả, băm ảnh đã duyệt: nguyên.
- 6 file T-086/T-089 (`test_t086_send_state`, `test_soi_loi_t086`, `test_la_chan_t086`, `test_t089_send_draft`, `test_soi_loi_t089`, `test_la_chan_t089`) trong lô test dưới.
- R5 `tests/test_soi_loi_t089.py::test_draft_deleted_elsewhere_while_sending_comes_back_locked`: chỉ **thêm** 3 khẳng định (nháp không bị tạo lại, có khung báo, bấm «Lưu lại» mới tạo lại) và docstring; giữ nguyên hai khẳng định khóa. Đúng hệ quả của yêu cầu 1, không nới; Soi Lỗi (người viết ca) đã đồng ý; còn Chỉ Huy duyệt chính thức (điều kiện B2).
- Đối chứng của tôi (probe P5): tab chưa từng thấy trạng thái gửi, kho «chưa gửi»: bước Xuất bản mở như cũ. Họa Sĩ `test_unsure_knowledge_locks_only_when_draft_gone[nhap-con]`: không khóa oan.

### 5. Phần lượt 1 (yêu cầu 1–6 của phiếu) — **đạt**

| # | Kiểm |
|---|---|
| 1 | Tự lưu không lặng lẽ tạo lại: `autosave` thấy nháp không còn thì không `save`, hiện `gone_notice` (`:960-977`); «Lưu lại» giữ trạng thái gửi tab biết; «Bỏ hẳn» xóa trắng trang. Soi Lỗi thử thêm nháp được tab khác lưu lại, file nháp bị xóa khi app chạy |
| 2, 3 | Mục 4, 3 |
| 4 | `client.showErrorDetails = "type"` đã ở `main` từ T-118 (`.streamlit/config.toml:19`), phiếu không sửa; `tests/test_t118_don_thap.py`, `tests/test_app_pages.py` Họa Sĩ, Soi Lỗi đã chạy |
| 5 | Chú thích «Chép sang SiteSEO» (`:2700-2705`) đúng hành vi T-102 (đường dẫn gửi kèm bài) và README của T-112 nay đã ở `main`; `.env.example:23-28`: tài khoản Biên tập viên riêng, mật khẩu ứng dụng tạo trên chính tài khoản đó; không giá trị thật |
| 6 | `keyword_problem` (`:2646`) dùng `odd_char_messages`, `has_odd_chars` vẫn là điều kiện Chặn nên không lọt «ghi được»; R5 `tests/test_t041_seo_ui.py:710-728` Chỉ Huy đã duyệt, thêm ca `emoji-moi` |

## Bảo mật W1, W2, U1

| Mục | Kết quả | Bằng chứng |
|---|---|---|
| **W1** · mặc định nháp; `publish`/`future` chỉ khi người dùng xác nhận | Đạt | Lượt 1 và 2 chỉ **thêm khóa**, không thêm đường gửi, không đổi hình thức mặc định hay màn hình xác nhận; `release_draft` vẫn là lối duy nhất, chỉ sau ô tick xác nhận nội dung và ô «gửi lại»; công tắc Hẹn giờ / Đăng ngay vẫn mặc định tắt. Probe P1 (công tắc bật, Hẹn giờ, G1, cú bấm lọt sau khi tick xác nhận nội dung): 0 bài, 0 lệnh `future` |
| **W2** · không xóa, ghi đè dữ liệu trên website | Đạt | Không lệnh nào tới website trong diff. «Bỏ hẳn» chỉ xóa trạng thái phiên, không xóa gì trong kho (dòng trạng thái gửi mồ côi giữ nguyên). `recreate_draft` ghi trạng thái gửi kiểu so rồi đặt: không ghi đè dòng mới hơn; `save(must_exist)` không tạo lại nháp đã xóa |
| **U1** · `unsafe_allow_html` chỉ với chữ đã escape hay cố định | Đạt | Khung báo là ba câu cố định `MSG_DRAFT_GONE`, `MSG_GONE_SENT`, `MSG_GONE_UNKNOWN` (`:226-237`); câu lỗi kho nháp qua `escape_markdown` (`:965`); không `unsafe_allow_html`; câu khóa dùng lại `sent_message`, `unsure_message` với mã bài là số nguyên |

## Đánh giá lỗi, ghi nhận của Soi Lỗi

| Mục | Soi Lỗi | Lá Chắn |
|---|---|---|
| **SL-T092-1** · Thấp · tab biết bài đã gửi, nháp bị xóa ở tab khác: bước Xuất bản mở khóa | Thấp; sửa trước khi bật công tắc; gợi ý (a)/(b)/(c) | **Đồng ý mức Thấp. Đã đóng** ở `bd03af9` theo gợi ý (b) có bổ sung (khóa theo điều tab biết; «gửi dở» không mã chỉ khóa khi nháp không còn). Hai ca `test_sl_t092_1_*` gỡ `xfail` qua (lô test dưới), thân test không đổi; Họa Sĩ thêm 4 test (6 ca) kể cả cú bấm lọt và đối chứng đã tick; đột biến M17–M20 bị bắt |
| **G1** · ba tab, tab không biết «Lưu lại» ghi đè điều tab biết | Ghi nhận; đề nghị «chỉ lên không xuống» | **Đã đóng cho tab đã biết** (`kept_send_knowledge`); probe P1 thêm ca Hẹn giờ. Phiên mới mở nháp lưu lại không kèm trạng thái vẫn không khóa: thuộc khoảng hở còn lại (điều kiện B1) |
| G2 · yêu cầu 4 không đổi | Đúng | Đồng ý |

## Thử độc lập (Fable)

File tạm `tests/test_zz_la_chan_t092_tam.py` mượn khung `test_t092_nhap_bi_xoa`, `test_t102_publish` (WordPress giả, không mạng); **không commit, đã xóa** (bản lưu ở thư mục nháp của phiên). 5 ca, **5/5 qua**. Hai lần sửa kỳ vọng là lỗi của probe, không phải của app: ô «gửi lại» ở Hẹn giờ mang nhãn khác Nháp (`AGAIN_LABELS`), nên tìm theo khóa `_wp_again`; sau khi mở nháp khác, `_draft_send_known` giữ «chưa gửi» của nháp mới chứ không rỗng (đúng).

| Ca | Kiểm | Kết quả |
|---|---|---|
| P1 G1 + Hẹn giờ (công tắc bật) | Tab biết «đã gửi 777»; nháp bị xóa; tab thứ ba lưu lại không kèm trạng thái; tab này tick xác nhận nội dung (không tick «gửi lại»), cú bấm lọt qua nút khóa | Khóa qua 2 lần vẽ; 0 bài, 0 lệnh hẹn giờ; kho không có «đang gửi» |
| P2 mở nháp khác | Biết 777 của nháp X đã bị xóa; mở nháp Y chưa gửi | Y không ô khóa, không «mã 777»; điều tab biết của X không đi theo |
| P3 «Bỏ hẳn» | Sau khi biết 777 và nháp bị xóa | `_draft_send_known`, `draft_id` xóa; không ô khóa |
| P4 kho bận lúc kiểm | Tab biết «gửi dở» không mã; nháp bị xóa; `send_state_if_exists` ném `DraftError` | Vẫn khóa «gửi dở» (ô «Tôi đã kiểm tra…»); hết lỗi vẫn khóa |
| P5 đối chứng | Tab chưa thấy trạng thái gửi nào, kho «chưa gửi» | Mở như cũ, không ô khóa |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pytest 15 file trên `bd03af9`: `test_t092_nhap_bi_xoa`, `test_soi_loi_t092`, 6 file T-086/T-089, `test_storage_drafts`, `test_storage_send_state`, `test_app_drafts`, `test_t102_publish`, `test_t112_release_rules`, `test_soi_loi_t112`, `test_t041_seo_ui` | **410 qua, 0 xfail, 0 hỏng, 0 XPASS**, 29 phút 40 (11:13–11:43; chậm vì máy chạy cùng lúc probe và lô test của phiên khác). Hai ca `test_sl_t092_1_*` của Soi Lỗi (đã gỡ `xfail`) qua | ✔ |
| Probe 5 ca (mục trên) | 5/5 qua | ✔ |
| `ruff check` 5 file; `ruff format --check` 3 file | sạch; đã đúng định dạng | ✔ |
| bandit `write.py`, `drafts.py` (`PYTHONUTF8=1`) | `write.py` 0; `drafts.py` 1 Low B101 (`assert saved.saved_at is not None`, `:905`, có từ T-086) | ✔ |
| detect-secrets (`PYTHONUTF8=1`) 7 file của phiếu | 2 «Basic Auth Credentials» báo nhầm đã biết: `write.py:2645` (docstring ví dụ `tên:mật-khẩu@`), `T-092-hoa-si.md:67` (nhắc ví dụ đó); biên bản này: 0 phát hiện | ✔ |
| D1 | `uv.lock`, `pyproject.toml` không đổi; không thêm thư viện | ✔ |
| Gộp thử | `git merge-tree --write-tree main HEAD` (`main` `8caab2f`: thêm T-121, T-122, T-112 lượt 3, biên bản) không xung đột; `git diff bad6db7..main` không đụng file nào của phiếu | ✔ |

## Ghi nhận (không xếp lỗi)

1. **Khoảng hở còn lại** (Họa Sĩ Rủi ro 1): tab chưa từng thấy lần gửi thì không có gì để khóa; khung báo nói rõ. Xem điều kiện B1.
2. **Khóa «gửi dở» thừa** trong ca rất hiếm (Họa Sĩ Rủi ro 2): tab thấy «đang gửi» của tab khác, lần gửi đó hỏng mà chưa tạo gì, rồi nháp bị xóa → «Lưu lại» ra «gửi dở», phải tick «Tôi đã kiểm tra…». Hướng an toàn, chấp nhận.
3. **Dòng trạng thái gửi mồ côi** khi người dùng chủ động gửi tiếp lúc nháp không còn: vô hại (như SL-T089-2), «Lưu lại» gắn lại đúng dòng đó. Nếu làm B1 thì cần cách dọn dòng mồ côi cũ.
4. `send_lock_state` thêm một lần đọc SQLite mỗi lần vẽ, chỉ khi tab biết «gửi dở» không mã mà kho «chưa gửi»: không đáng kể.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

**A. Gộp `main`: được ngay.** Chỉ Huy chạy toàn bộ test khi gộp.

**B. Không chặn gộp:**

1. **Khuyến nghị trước khi bật công tắc Hẹn giờ / Đăng ngay** (Chỉ Huy, chủ dự án quyết; không bắt buộc với công tắc tắt): làm **Đề xuất 1 của Họa Sĩ** — giữ trạng thái gửi khi xóa nháp **đã gửi** (dòng mồ côi có chủ đích) kèm cách dọn dòng mồ côi cũ; đổi `DraftStore.delete` và test T-086 `test_send_state_removed_with_its_draft`. Khi đó nháp tạo lại ở **bất kỳ** tab hay phiên nào cũng khóa (`recreate_draft` so rồi đặt sẽ giữ dòng mồ côi), bịt nốt khoảng hở «tab không biết». Lá Chắn kiểm lại (hàm kho dùng chung: chạy test mọi nơi gọi).
2. **Chỉ Huy duyệt chính thức R5** `tests/test_soi_loi_t089.py` (Họa Sĩ xin khi gộp; Soi Lỗi và tôi đồng ý: chỉ thêm khẳng định).
3. (Nhỏ, Đề xuất 2 của Họa Sĩ) popover «🗑️ Xóa» của nháp đã gửi nhắc «xóa nháp không xóa bài trên website»: phiếu dọn giao diện sau.

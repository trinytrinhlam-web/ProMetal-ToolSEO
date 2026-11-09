# Biên bản bảo mật T-130 · Giữ trạng thái gửi khi xóa nháp đã gửi, nhắc khi xóa · rút gọn

> **Model:** Claude **Opus 5.5** (dòng «You are powered by»: Opus 5.5). Chỉ Huy B giao chạy Opus 5.5; chủ dự án 04/11: hết hạn mức Fable thì Lá Chắn chạy Opus 5.5, ghi rõ model.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-130](../tickets/T-130-giu-trang-thai-gui-khi-xoa-nhap.md) · rút gọn (W1, W2, U1) · điều kiện B1, B3 của [Lá Chắn T-092](T-092-la-chan.md) |
| Phạm vi | Chỉ đọc: `team/T-130` tại `9e3971b` (gốc `50a40a6`). Code: `seo_app/storage/drafts.py` (+45/−), `app/views/write.py` (+79/−). Test: `test_t130_giu_trang_thai_gui.py` (13 ca mới), `test_soi_loi_t130.py` (Soi Lỗi), R5 ở `test_storage_send_state.py`, `test_t092_nhap_bi_xoa.py`. Báo cáo đã đọc: [Họa Sĩ](T-130-hoa-si.md), [Soi Lỗi](T-130-soi-loi.md) (ĐẠT, 0 lỗi) |
| Máy | Windows 11 Pro, Python 3.12, uv 0.13.4. Chỉ chạy test liên quan, không chạy toàn bộ; không gọi website |
| Ngày | 2026-11-07 (09:06–09:41, giờ máy +07); nghỉ vì hết hạn mức, 2026-11-09 07:33–07:35 kiểm lại gộp với `main` mới rồi nộp |
| **Kết luận** | **ĐẠT** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp. W1, W2, U1 đạt. Điều kiện B1 (giữ trạng thái gửi, dọn dòng mồ côi) và B3 (nhắc khi xóa) của Lá Chắn T-092 **đóng**. R5 đúng cách. **Gộp `main` được ngay** |

## Tóm tắt (cho chủ dự án)

- **Khoảng hở cuối của việc «gửi trùng» đã bịt.** Trước đây, xóa nháp của một bài **đã gửi** thì phần mềm quên việc đã gửi. Một tab khác còn mở bài đó mà chưa từng thấy lần gửi, lưu lại rồi bấm gửi, là ra **bài thứ hai** trên website. Nay phần mềm giữ lại «dấu đã gửi» khi xóa nháp, nên nháp được lưu lại ở bất kỳ tab nào cũng bị khóa gửi trùng.
- **Không đụng website.** Xóa nháp chỉ xóa trên máy. Nút «🗑️ Xóa» của nháp đã gửi nay nhắc rõ: xóa nháp **không** xóa bài trên website, muốn bỏ bài thì xóa trong trang quản trị WordPress.
- **Dấu cũ được dọn an toàn:** phần mềm giữ tối đa 200 dấu của nháp đã xóa gần nhất, và không bao giờ đụng dấu của nháp còn trong máy.
- **Việc của anh/chị:** không có.

## 1. Còn đường nào ra bài thứ hai trên website không: **không** (W1)

Đọc mã `302ba7a`:

- **Xóa nháp giữ dòng trạng thái gửi.** `DraftStore.delete` (`drafts.py:991-1003`) chỉ xóa dòng nháp. Phần kho đầy bỏ bớt trong `save` (`:928-937`) cũng thôi xóa dòng trạng thái gửi của nháp bị bỏ. Phần mềm không bao giờ ghi dòng «chưa gửi» (chưa gửi là không có dòng), nên dòng nào còn cũng là một khóa: đã gửi, đang gửi, gửi dở, lệnh chuyển chưa rõ kết quả, dòng hỏng.
- **Tab chưa từng thấy lần gửi:**
  - lần tự lưu thấy nháp không còn (`send_state_if_exists` trả `None`, kể cả khi còn dòng mồ côi) thì đọc thêm dòng giữ lại (`kept_send_read`, `write.py:955-962`) gộp vào điều tab biết (`known_send_state(extra=…)`). Bước Xuất bản khóa ngay, trước cả khi lưu lại;
  - «Lưu lại thành nháp» dùng **đúng mã nháp cũ**, ghi trạng thái gửi kiểu so rồi đặt, giữ nguyên dòng có sẵn (ca `test_recreate_does_not_overwrite_row_written_in_between`). Phiên mới mở nháp đó đọc dòng trong kho, cũng khóa.
- **Nháp mới luôn có mã mới** (`uuid4().hex`, `drafts.py:171`), nên không bao giờ «nhặt» nhầm dòng mồ côi của nháp khác (không có khóa oan).
- **Lớp T-092 vẫn còn** cho trường hợp dòng giữ lại cũng mất (bị dọn, file nháp bị xóa): tab nào đã biết thì vẫn khóa theo điều tab biết. R5 thêm `lose_kept_state` vào 6 ca T-092 để ca vẫn kiểm đúng đường này (mục 4).
- **Luồng gửi không đổi:** màn hình xác nhận, mã băm, so rồi đặt «đang gửi», `release_draft` không đổi dòng nào. Phần mới chỉ **thêm** khóa, không mở khóa ở đâu.
- **Giới hạn còn lại** (đồng ý mức nhẹ như Họa Sĩ, Soi Lỗi):
  - quá 200 lần xóa nháp đã gửi sau đó thì dòng cũ nhất bị dọn;
  - xóa cả `data/drafts.sqlite` thì mất hết;
  - dòng đã bị xóa trước khi có T-130 thì không lấy lại được.

  Cả ba ca vẫn còn lớp «điều tab biết» của T-092 cho tab đã biết, và đều cần người dùng tự bấm gửi qua màn hình xác nhận.

## 2. Dọn dòng mồ côi không bao giờ xóa trạng thái của nháp còn tồn tại: **đúng**

`_trim_orphan_send_states` (`drafts.py:1213-1224`):

```sql
DELETE FROM send_states WHERE id NOT IN (SELECT id FROM drafts) AND rowid NOT IN
  (SELECT rowid FROM send_states WHERE id NOT IN (SELECT id FROM drafts) ORDER BY rowid DESC LIMIT ?)
```

- Điều kiện ngoài `id NOT IN (SELECT id FROM drafts)` loại hẳn mọi dòng của nháp còn trong kho. Dòng nháp có mã `NULL` (sửa tay) làm `NOT IN` không bao giờ đúng, nên không dọn gì (hướng an toàn; ca `test_trim_skips_when_drafts_table_has_null_id`).
- Chạy **trong cùng giao dịch** với lần xóa hay lần lưu (`:1002`, `:937`): kho thấy một trạng thái nhất quán, lần lưu ở tab khác không chen được vào giữa.
- Giữ 200 dòng ghi gần nhất theo `rowid`. `INSERT OR REPLACE` cho mỗi lần ghi một `rowid` mới lớn nhất, nên thứ tự theo `rowid` đúng là thứ tự lần ghi (ca `test_trim_order_follows_last_write`). `max(0, keep)` chặn số âm.
- Test: 7 ca kho của Họa Sĩ (dọn đúng số, đúng thứ tự, không đụng nháp còn, `keep = 0`, mã `NULL`, giới hạn mặc định). Soi Lỗi thêm ca kho đầy kèm nhiều dòng mồ côi và 3 đột biến (3/3 bị bắt).
- **Tự thử** (`probe_t130.py`, `DraftStore` thật trên thư mục tạm, không mạng):
  - nháp A còn trong kho, có trạng thái gửi ghi **sớm nhất**;
  - X đã gửi rồi bị xóa ngay sau A, tiếp theo là 199 rồi 200 lần xóa nháp đã gửi khác.

  Kết quả: sau 199 lần X còn; sau lần thứ 200 X bị dọn; luôn giữ đúng 200 dòng mồ côi. Trạng thái gửi của A còn nguyên qua mọi lần dọn và 5 lần tự lưu. **4/4 đúng**, khớp giới hạn Họa Sĩ ghi.

## 3. Không xóa gì trên website; câu nhắc là chữ cố định: **đạt** (W2, U1)

- **W2:** `delete_draft` (`write.py:881-892`) chỉ gọi `draft_store().delete` rồi xóa trắng trang khi đúng bài đang mở. Diff không thêm lệnh nào tới WordPress (không nhập client trong phần này). `seo_app/wordpress/**` không đổi.
- **U1:**
  - `MSG_DELETE_SENT` (`write.py:240-243`) là chữ cố định, chỉ chèn `post_id`. Đây là số nguyên đã kiểm khuôn trong `SendState`.
  - `MSG_DELETE_UNSURE` (`:244-247`) cố định hẳn.
  - Hiện bằng `st.warning`, không `unsafe_allow_html`.
  - `delete_warning` (`:965-977`) đọc lỗi (dòng hỏng, file bận) thì nhắc như lần gửi chưa rõ kết quả: hướng an toàn.
- Câu nhắc đúng sự thật: «bài mã …» chỉ khi đã có mã và không còn «đang gửi» hay «chưa rõ kết quả»; còn lại nói «có thể đã có trên website». Soi Lỗi kiểm cả bài đã hẹn giờ, đã đăng.

## 4. R5 đổi test T-086, T-092 đúng cách: **đạt**

- **T-086** `test_send_state_removed_with_its_draft` → `test_send_state_kept_as_orphan_when_its_draft_goes`: đổi đúng hành vi phiếu yêu cầu (yêu cầu 5, Chỉ Huy duyệt). Ca mới **chặt hơn**: kiểm cả hai đường (kho đầy bỏ bớt và xóa tay), so đúng giá trị trạng thái, và lưu lại thì có lại khóa (`send_state_if_exists`).
- **T-092** `test_must_exist_does_not_recreate_deleted_draft`: «`send_states` rỗng sau khi xóa» thành «dòng còn nguyên và lần ghi so rồi đặt hỏng không đổi nó». Đúng hành vi mới, không nới.
- **6 ca T-092 thêm `lose_kept_state`** (giả dòng giữ lại cũng mất, bằng `save_send_state(…, None)`): không bỏ hay đổi khẳng định nào. Không thêm bước này thì các ca vẫn qua nhưng **vì lý do sai** (dòng giữ lại làm hộ), mất phần kiểm lớp «điều tab biết». Thêm vào là giữ đúng ý ca. Đường mới (dòng giữ lại) có ca riêng ở `test_t130_*`, `test_soi_loi_t130.py`.
- Không `skip`, không `xfail`, không xóa test (đọc diff test `50a40a6..9e3971b`).

## 5. Ghi nhận (không tính lỗi)

- **Đồng ý G1 của Soi Lỗi (ngoài phạm vi):** bắt đầu viết lại từ một dòng kế hoạch mà nháp cũ đã bị xóa thì app tạo nháp **mã mới** (`write.py:755`). Đó là một bài mới, không mang khóa của bài cũ. Không phải đường gửi lặng lẽ, vì người dùng phải soạn rồi tự bấm gửi qua màn hình xác nhận. Dòng kế hoạch giữ «Đã gửi nháp» do luật chỉ đi tới. Nên có một phiếu nhỏ cho giao diện: nhắc «dòng này đã có bài trên website (mã …)» khi bắt đầu từ dòng kế hoạch đã có mã bài, giống câu nhắc ở nút Xóa. Chỉ Huy quyết.
- Mỗi lần vẽ khung «Bài đang soạn dở», popover đọc trạng thái gửi từng nháp (tối đa `MAX_DRAFTS` lần đọc nhỏ). Chỉ là chuyện tốc độ, không phải bảo mật.
- Dòng mồ côi chỉ chứa trạng thái gửi (mã bài, giờ, cờ), không chứa nội dung bài, giữ trong máy, tối đa 200 dòng × 4 KB.

## 6. Kết quả kiểm tra

| Việc | Kết quả | Đã xác minh |
|---|---|---|
| pytest 14 file liên quan trên nhánh `9e3971b` (kho nháp, trạng thái gửi, T-130 của Họa Sĩ và Soi Lỗi, T-092, T-086, T-089 cả ba bộ, T-100 nháp–kế hoạch, T-102 Xuất bản) | **344 qua, 0 hỏng**, 31 phút 48 (09:08–09:40, máy bận) | ✔ |
| `probe_t130.py` (ranh giới 200 dòng mồ côi, nháp còn không mất trạng thái) | 4/4 đúng | ✔ |
| Gộp thử `main` cục bộ `31d8cec` | `git merge-tree`: không xung đột (cây `6a99d85`), hai bên không chung file. Từ `06a1b0e` (cây gộp Soi Lỗi đã chạy test) tới `31d8cec`, `main` chỉ thêm tài liệu T-133, nên kết quả trên cây gộp của Soi Lỗi vẫn dùng được | ✔ |
| Kiểm lại gộp 09/11 với `main` cục bộ `223c5f2` (đã gộp T-125, lập phiếu T-127) | `git merge-tree`: không xung đột (cây `7980594`). Từ gốc chung `50a40a6`, phần `main` thêm (trang 📈 Theo dõi, Cài đặt → Search Console) **không chung file** với T-130. Không chạy lại test trên cây này; Chỉ Huy chạy toàn bộ test khi gộp | ✔ |
| Soi Lỗi (cây gộp `main` `06a1b0e`, 20 file) | 667 qua, 1 bỏ qua, 0 hỏng; đột biến 3/3 | dùng lại |
| ruff (2 file nguồn, 4 file test đổi) | sạch | ✔ |
| detect-secrets (`PYTHONUTF8=1`; chép 2 file nguồn, 2 file test mới, 3 báo cáo ra thư mục ngoài git cùng file mồi) | 2 «Basic Auth» báo nhầm đã biết: docstring `write.py:2691` (ví dụ địa chỉ có tên, mật khẩu, LC-T041-1) và dòng báo cáo Họa Sĩ `:88` trích lại ví dụ đó. Biên bản này: 0; file mồi: bị bắt | ✔ |
| bandit (Họa Sĩ) | 1 Low có sẵn (B101 `assert` trong `save`) | dùng lại |

## 7. Kết luận

**ĐẠT.** Gộp `main` được ngay. Điều kiện B1, B3 của Lá Chắn T-092 đóng. Khoảng hở «tab không biết» bịt xong, một việc cần trước khi bật công tắc Hẹn giờ / Đăng ngay.

# Báo cáo T-073 · Ổn định test khóa chờ của kho danh sách bài (T-037) · Soi Lỗi

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-073](../tickets/T-073-on-dinh-test-khoa-cho-t037.md) (Chỉ Huy B giao 02/11 19:40), nhánh `team/T-073` từ `origin/main` `7485b94` |
| Ngày nộp | 2026-11-03 (08:17 +07:00) |
| **Kết luận** | **XONG**: đã xác nhận nguyên nhân (đo được, giả lập được, tái hiện được dưới tải giả); sửa đúng một ca, chỉ đổi cách **giữ khóa** trong test, **mọi điều kiện kiểm giữ nguyên**. Cả file chạy 20 lần dưới tải giả: **20/20 lượt qua, 0 hỏng** (mỗi lượt 139 ca). Không sửa `seo_app/**` |

## Tóm tắt (cho chủ dự án)

- **Vì sao bài kiểm tra này hay đỏ oan:** bài kiểm tra cho một «chương trình khác» giữ file lưu tạm danh sách bài, rồi xem phần mềm có báo «đang bận» và không xóa file không. Chương trình giả đó chỉ giữ file **10 giây** rồi tự buông. Mà phần mềm phải chờ khóa 5 lần, mỗi lần khoảng 1,8 giây lúc máy bận vừa, tổng khoảng 9 giây. Máy bận nặng (nhiều phiên chạy test cùng lúc) thì quá 10 giây: file được buông giữa chừng, bài kiểm tra tưởng phần mềm sai.
- **Đã sửa:** chương trình giả giữ file **tới khi bài kiểm tra kiểm xong** mới buông (có giới hạn 2 phút để không bao giờ treo). Những gì bài kiểm tra đòi phần mềm làm đúng thì **giữ nguyên từng điều**.
- **Kết quả:** dưới tải giả nặng, bản cũ hỏng 4/4 lần, bản mới qua 4/4 lần; cả file chạy 20 lần dưới tải giả: 20/20 lần đều qua.
- Phần mềm không phải sửa gì. **Không có gì phải anh/chị quyết.**

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t037.py` | Ca `test_r2_long_lock_in_other_thread_is_busy_not_deleted`: luồng giữ khóa chỉ nhả khi phía chính kiểm xong; thêm hằng `_HOLD_LIMIT = 120` (chống treo), bắt lỗi trong luồng, kiểm khóa được giữ suốt lúc kiểm. Bảng cũ → mới ở mục 2 |
| `docs/team/reports/T-073-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, phiếu hay file khác.

## 1. Xác nhận nguyên nhân

**Đọc mã.** Ca test chỉ thu `_SQLITE_TIMEOUT` xuống 0,1 giây. Nhưng mỗi lần đọc hay ghi kho đều đi qua `_prepare` → `_is_healthy`, chờ khóa bằng `_HEALTH_TIMEOUT` = **1 giây** (test không thu nhỏ). Khóa `EXCLUSIVE` của luồng kia chặn cả đọc, nên `_is_healthy` chờ đủ hạn rồi báo bận. Phía chính gọi kho 5 lần lúc bị khóa: `load`, `is_stale`, `refresh`, `refresh` lần hai, `save`. Luồng giữ khóa thì `release.wait(10)`: quá 10 giây là tự `ROLLBACK`, nhả khóa.

**Đo giờ từng bước** (bản dò ghi giờ từng lần gọi, máy đang chạy bộ test của Chỉ Huy, tải 73%, chưa đốt CPU):

| Cách giữ khóa | Chờ khóa mỗi lần | Tổng 5 lần | Luồng tự nhả vì quá 10 giây | Kết quả |
|---|---|---|---|---|
| Cũ (tự nhả sau 10 giây) | 1,78–1,80 giây | 8,97 giây | Không | Qua, **dư chưa tới 1 giây** |
| Cũ, giả lập máy chậm (`_HEALTH_TIMEOUT` = 2,5) | 3,91 giây | 10,05 giây thì hỏng | **Có** | **Hỏng** ở bước thứ 3: `assert 'bận' in ''` (khóa vừa nhả nên ghi được) |
| Mới (nhả khi kiểm xong) | 1,79–1,80 giây | 8,98 giây | Không | Qua |
| Mới, giả lập máy chậm | 3,89–3,92 giây | 19,51 giây | Không | Qua |

Chạy đúng file trên `origin/main` (bản cũ) với cùng cách giả lập máy chậm: hỏng `assert 'bận' in ''`; bản mới qua (20,1 giây).

**Tải giả thật** (8 tiến trình đốt CPU trên máy 8 lõi, lúc máy đã tải 97% vì bộ test của Chỉ Huy; chạy xen kẽ bản cũ và bản mới, mỗi bản 4 lần):

| Bản | Hỏng | Ghi chú |
|---|---|---|
| Cũ (`origin/main`) | **4/4** | Lần nào cũng `Failed: DID NOT RAISE SiteIndexError`, đúng như ghi nhận 20/10, 30/10, 02/11 |
| Mới | **0/4** | Mỗi lần 16–19 giây: dưới tải nặng, mỗi lần chờ khóa «1 giây» kéo thành 3–4 giây |

Kết luận: đúng phỏng đoán của Chỉ Huy. Khung 10 giây của luồng giữ khóa chỉ dư khoảng 1 giây so với tổng thời gian chờ khóa của phía chính; máy bận là vượt.

## 2. Sửa (chỉ test; R5: Chỉ Huy duyệt đổi cách giữ khóa, không nới điều kiện kiểm)

| Chỗ | Cũ | Mới |
|---|---|---|
| Luồng giữ khóa đợi phía chính | `release.wait(10)`: quá 10 giây tự `ROLLBACK`, nhả khóa | `release.wait(_HOLD_LIMIT)`, `_HOLD_LIMIT = 120` giây chỉ để chống treo; ghi lại có phải tự nhả vì quá giờ không (`gave_up`) |
| Đợi luồng khóa xong | `assert locked.wait(10)` | `assert locked.wait(_HOLD_LIMIT)` (trả ngay khi luồng đã khóa) |
| Lỗi trong luồng giữ khóa | Không bắt: luồng chết lặng lẽ, phía chính hỏng ở câu khác, khó hiểu | Bắt vào `errors`, luôn đóng kết nối và `locked.set()`; kiểm `errors == []` ngay sau khi chờ khóa và lúc cuối |
| Đợi luồng kết thúc | `thread.join(10)` | `thread.join(_HOLD_LIMIT)`, thêm `assert not thread.is_alive()` |
| Khóa được giữ suốt lúc kiểm | Không kiểm | Thêm `assert gave_up == [False]`: nếu có ngày luồng lại tự nhả, test báo đúng lý do thay vì «DID NOT RAISE» |
| **Điều kiện kiểm** | `load` trả `None`; `is_stale` là `True`; `refresh` có `cache_error` chứa «bận»; `save` ném `SiteIndexError` khớp «bận»; `reset_count == 0`; nhả khóa thì đọc lại đúng bài 1 | **Giữ nguyên từng dòng**, cùng thứ tự |
| `_SQLITE_TIMEOUT` thu nhỏ | 0,1 | Giữ 0,1 |

Ca vẫn kiểm đúng điều nó kiểm: trong suốt lúc phía chính đọc, ghi, khóa **chắc chắn** còn bị giữ (trước đây không chắc), và `gave_up == [False]` chứng minh điều đó mỗi lần chạy.

## 3. Soát các test cùng kiểu

**Trong `tests/test_soi_loi_t037.py`** (được sửa theo phiếu):

| Ca | Cách giữ khóa / chờ | Đánh giá |
|---|---|---|
| `test_r2_long_lock_in_other_thread_is_busy_not_deleted` | Luồng tự nhả sau 10 giây | **Sửa** (mục 2) |
| `test_r2_short_lock_in_other_thread_is_waited_out` | Luồng giữ khóa, đồng hồ 0,3 giây nhả; phía chính phải chờ được trong `_HEALTH_TIMEOUT` | Khung rộng (nhả sau 0,3 giây, hạn chờ đo được ≥ 1,8 giây). Dưới tải giả, 20/20 lượt cả file đều qua: không cần sửa |
| `test_two_refreshes_at_once_both_succeed` | Hai luồng cùng ghi 15 lần, rào `Barrier`, không hạn chót trong test | Không có khung giờ của test; phụ thuộc hạn chờ ghi 1 giây của phần mềm. Dưới tải giả, 20/20 lượt qua: không cần sửa. Nếu máy bận tới mức một lần ghi 300 dòng quá hạn chờ ghi 1 giây, ca này sẽ báo «bận»; đó là hạn chờ của phần mềm, không phải khung giờ của test, nên phiếu chỉ sửa test không đổi |
| `test_locked_file_is_busy_not_corrupt`, `test_r2_locked_file_and_journal_are_not_deleted`, `test_r2_after_lock_released_refresh_writes_normally`, `test_r2_get_under_lock_raises_nothing`, `test_r2_lock_taken_between_health_check_and_read` | Khóa giữ ở luồng chính, nhả trong `finally` | Không phụ thuộc giờ: không cần sửa |
| `test_r2_lock_held_by_another_process_is_left_alone` | Tiến trình con giữ khóa tới khi nhận dòng từ phía chính (không hạn) | Không cần sửa |
| `test_r2_file_opened_by_other_program_share_delete_is_not_deleted` | Luồng chính giữ handle tới `finally` | Không cần sửa |

**Các file khác** (ngoài phạm vi sửa của phiếu, chỉ soát):

| File | Mẫu | Đánh giá |
|---|---|---|
| `test_ai_t034.py::test_lock_reports_held_by_other_thread` | Luồng giữ khóa `release.wait(10)` | Phía chính kiểm ngay một lệnh (không chờ khóa): dư gần 10 giây, rủi ro rất thấp |
| `test_app_images.py`, `test_soi_loi_t056.py` (`release.wait(90)`), `test_soi_loi_t027.py` (`wait(timeout=30)`), `test_la_chan_t089.py` (`WAIT = 30`, «chỉ để test không treo») | Giới hạn rộng | Cùng cách với bản sửa này |
| `test_soi_loi_t049.py`, `test_soi_loi_t099.py` (`….wait(10)` trên sự kiện) | Chờ luồng kia tới một điểm, trả ngay khi tới | Không tự nhả tài nguyên giữa chừng |
| `test_site_index_t042.py:211`, `test_t041_site_index.py:88` | Đo giờ: một lần chờ khóa (`_HEALTH_TIMEOUT` 1 giây) phải dưới `_SQLITE_TIMEOUT` (5 giây) | Một lần chờ khóa đo được 1,8 giây lúc máy bận vừa, 3–4 giây lúc tải nặng; hạn so 5 giây nên còn dư, nhưng không nhiều. Chạy 2 file 3 lần dưới cùng mức tải giả: 39/39 qua mỗi lần. Ghi nhận để theo dõi, chưa cần phiếu |

## 4. Chạy cả file 20 lần dưới tải giả

Tải giả: 8 tiến trình đốt CPU (máy 8 lõi), chỉ sống trong từng lô 5 lượt; máy đồng thời chạy bộ test của Chỉ Huy trên `main` (đo lúc 07:40, trước khi đốt: 97%). Mỗi lượt chạy cả `tests/test_soi_loi_t037.py` (139 ca).

| Lô (giờ bắt đầu) | Lượt | Kết quả mỗi lượt | Thời gian pytest mỗi lượt |
|---|---|---|---|
| 1 (07:49) | 5 | 139 qua | 71–76 giây |
| 2 (07:56) | 5 | 139 qua | 63–72 giây |
| 3 (08:03) | 5 | 139 qua | 57–67 giây |
| 4 (08:09) | 5 | 139 qua | 57–67 giây |

**Tổng: 20/20 lượt qua, 0 hỏng.** Ca đã sửa qua cả 20 lượt; ca khóa ngắn và ca hai luồng cùng ghi cũng qua cả 20 lượt.

## Lệnh đã chạy

```
uv run pytest <bản dò đo giờ từng bước, 2 cách giữ khóa × 2 mức chờ>      # cũ + chậm: hỏng; còn lại qua
uv run pytest <bản cũ origin/main / bản mới> -p slow_lock (giả lập máy chậm)   # cũ hỏng, mới qua
uv run python burn_compare.py 8 4 …  (8 tiến trình đốt CPU, xen kẽ cũ / mới)   # cũ 4/4 hỏng, mới 0/4
uv run python burn_and_run.py 8 5 … tests/test_soi_loi_t037.py  (× 4 lô)       # 20/20 lượt, mỗi lượt 139 qua
uv run ruff check .; uv run ruff format --check tests/test_soi_loi_t037.py
```

Quét ký tự ẩn: báo cáo sạch; `tests/test_soi_loi_t037.py` có một U+200B ở dòng 179, có sẵn trên `origin/main` (mẫu tấn công cố ý của `test_is_site_link_rejects_attacks`), phần sửa không thêm ký tự ẩn nào. Script dò, script tải giả: thư mục ghi chú chung, mục `T-073-soi-loi-scripts`. Không gọi website, Google thật; không chạy cloud.

# Biên bản bảo mật T-073 · Ổn định test khóa chờ của kho danh sách bài (T-037), chỉ sửa test

> **Model:** chạy bằng Claude Opus 5.5 (phiên này). Hồ sơ vai khuyên Claude Fable 5.1; phiếu này kiểm rút gọn, chỉ có sửa test.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (xem dòng trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-073](../tickets/T-073-on-dinh-test-khoa-cho-t037.md) · kiểm **rút gọn**, trọng tâm R5 (test không bị làm yếu) |
| Phạm vi | diff `7485b94..9824f8a` (nhánh `team/T-073`, 2 file): `tests/test_soi_loi_t037.py` (ca `test_r2_long_lock_in_other_thread_is_busy_not_deleted`, thêm hằng `_HOLD_LIMIT`), báo cáo Soi Lỗi. Kèm `seo_app/storage/site_index.py` (`_is_healthy`, `_is_busy`, `_HEALTH_TIMEOUT`) để thử đột biến |
| Báo cáo đã đọc | [Soi Lỗi](T-073-soi-loi.md) (XONG, 20/20 lượt dưới tải giả) |
| Ngày | 2026-11-03 (08:40–08:50, giờ máy +07) |
| **Kết luận** | **ĐẠT** · 0 lỗi. **R5 đạt: test không bị làm yếu.** Mọi điều kiện kiểm cũ giữ nguyên từng dòng, thêm 3 điều kiện chặt hơn; ca test vẫn bắt được lỗi gốc R2 (thử đột biến). **Gộp vào `main` được ngay** (không xung đột với `main` cục bộ `33dd87f`) |

## Tóm tắt (cho chủ dự án)

- **Bài kiểm tra này hết đỏ oan mà không bị nới.** Trước đây «chương trình giả» giữ file 10 giây rồi tự buông, máy bận thì buông sớm hơn lúc bài kiểm tra kiểm xong. Nay nó giữ tới khi bài kiểm tra kiểm xong mới buông. Mọi điều bài kiểm tra đòi phần mềm làm đúng (báo «đang bận», không xóa file lưu tạm…) vẫn giữ nguyên, còn thêm một điều kiểm: file chắc chắn bị giữ suốt lúc kiểm.
- **Tôi thử lại:**
  - Chạy 10 lần liền lúc máy đang bận chạy toàn bộ test: 10/10 qua.
  - Giả lập máy chậm: bản cũ hỏng, bản mới qua.
  - Cố ý làm hỏng phần mềm theo đúng kiểu lỗi cũ: bài kiểm tra báo đỏ ngay.
- Không sửa gì trong phần mềm. Không có gì cần anh/chị quyết.

## Lỗi phát hiện

Không phát hiện lỗi.

## R5 · So từng điều kiện kiểm (bản cũ `7485b94` → bản mới)

Tách mọi dòng `assert`, `pytest.raises`, `monkeypatch.setattr` của ca `test_r2_long_lock_in_other_thread_is_busy_not_deleted` ở hai bản rồi so:

| Điều kiện | Bản cũ | Bản mới |
|---|---|---|
| Thu nhỏ hạn chờ ghi | `monkeypatch.setattr(site_index, "_SQLITE_TIMEOUT", 0.1)` | Giữ nguyên |
| Chờ luồng kia khóa xong | `assert locked.wait(10)` | `assert locked.wait(_HOLD_LIMIT)`: chỉ là giới hạn chờ, trả ngay khi luồng đã khóa |
| `load` khi bị khóa | `assert store.load(BASE_URL) is None` | Giữ nguyên |
| `is_stale` khi bị khóa | `assert store.is_stale(BASE_URL) is True` | Giữ nguyên |
| `refresh` báo «bận» | `assert "bận" in store.refresh(...).cache_error` | Giữ nguyên |
| `save` ném lỗi «bận» | `with pytest.raises(site_index.SiteIndexError, match="bận")` | Giữ nguyên |
| Không xóa kho | `assert store.reset_count == 0` | Giữ nguyên |
| Nhả khóa thì đọc lại đúng dữ liệu cũ | `assert [i.id for i in store.load(BASE_URL).items] == [1]` | Giữ nguyên |
| **Mới:** luồng giữ khóa không lỗi | | `assert errors == []` (ngay sau khi khóa và lúc cuối) |
| **Mới:** luồng đã kết thúc | | `assert not thread.is_alive()` |
| **Mới:** khóa được giữ suốt lúc kiểm | | `assert gave_up == [False]` |

Dòng cũ duy nhất không còn nguyên văn là `locked.wait(10)` → `locked.wait(_HOLD_LIMIT)`. Đây là giới hạn chờ, không phải điều kiện kiểm phần mềm.

Ba điều kiện mới làm ca test **chặt hơn**:
- Trước đây, nếu luồng giữ khóa chết lặng lẽ hay tự buông giữa chừng, ca test vẫn có thể qua hoặc hỏng vì lý do khác.
- Nay ca test chứng minh mỗi lần chạy rằng khóa được giữ suốt lúc phía chính kiểm.
- `finally: locked.set()` trong luồng giữ khóa giúp phía chính không chờ mãi khi luồng lỗi trước lúc khóa; khi đó `errors == []` báo đúng lý do.

`seo_app/**` không đổi (`git diff --stat 7485b94..9824f8a -- seo_app/` trống).

## Thử lại độc lập

| Thử | Kết quả |
|---|---|
| **10 lần liền** ca đã sửa, lúc máy đang chạy toàn bộ test trên `main` (tải thật, không đốt CPU thêm), 08:42–08:45 | **10/10 qua**; thời gian trong pytest 11,4–17,2 giây. Lâu hơn khung 10 giây của bản cũ, khớp nguyên nhân Soi Lỗi đo |
| **Máy chậm cố định**: plugin nháp đặt `_HEALTH_TIMEOUT = 2.5` giây (5 lần chờ ≈ 12,5 giây) | **Bản mới: qua** (22,4 s). **Bản cũ `7485b94`:** hỏng `AssertionError: assert 'bận' in ''`, đúng kiểu hỏng oan đã ghi nhận (khóa tự nhả giữa chừng). Bản cũ chạy thường (không giả lập chậm): qua (13,8 s), tức bản sao chạy đúng |
| **Đột biến 1: «file bận coi như file hỏng»** (đúng loại lỗi R2 của T-037: xóa kho khi chương trình khác giữ khóa), qua `_is_corrupt` | Ca test **hỏng**: câu báo không còn chữ «bận» (phần mềm cố tạo lại file) |
| **Đột biến 2: «không nhận ra lỗi bận»**, qua `_is_busy` | Ca test **hỏng**: câu báo chung, không có chữ «bận» |
| Không đột biến, cùng plugin (đối chứng) | Qua (11,7 s) |

Plugin đột biến và giả lập chậm để ngoài repo, không commit.

## Thử gộp

- `main` cục bộ `33dd87f`: `git merge-tree --write-tree` không xung đột (cây `53b26ad`).
- `origin/main` `7485b94` là gốc nhánh: cây `2486181`, không xung đột.
- Từ `7485b94`, `main` không đổi `tests/test_soi_loi_t037.py`, `seo_app/storage/site_index.py`, `tests/conftest.py`. Ca test trên cây gộp vì vậy chạy y như trên nhánh.
- **Gộp được ngay.**

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` (đặt `PYTHONUTF8=1`) trên 2 file của diff: 1 mục ở `tests/test_soi_loi_t037.py`, **đã có ở `7485b94`** (cùng mã băm), báo cáo 0. Mồi khóa giả trong bản sao báo cáo (có chữ tiếng Việt): bắt được 1; không đặt `PYTHONUTF8`: 0; đã xóa mồi. Soát commit `9824f8a`: 0 khóa, mã băm |
| S2 | Không áp dụng | Không đổi code |
| S3 | Không áp dụng | Không có biến cấu hình mới |
| W1 | Không áp dụng | Không đụng WordPress |
| W2 | Không áp dụng | Như W1 |
| W3 | Không áp dụng | Như W1 |
| W4 | Không áp dụng | Như W1 |
| A1 | Không áp dụng | Không đụng AI |
| A2 | Không áp dụng | Như A1 |
| A3 | Không áp dụng | Như A1 |
| U1 | Không áp dụng | Không đụng giao diện |
| U2 | Không áp dụng | Như U1 |
| U3 | Không áp dụng | Như U1 |
| F1 | Đạt | Test dùng kho SQLite trong `tmp_path` (fixture `store`) |
| F2 | Không áp dụng | Không đụng ảnh |
| F3 | Không áp dụng | Không đổi cách đọc/ghi file |
| D1 | Đạt | `uv.lock`, `pyproject.toml` không đổi |
| D2 | Không áp dụng | `.gitignore` không đổi |
| D3 | Đạt | Ca test chỉ dùng SQLite cục bộ và luồng; không có mạng; bộ chặn mạng chung vẫn bật |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit, bandit | Không chạy | Không đổi thư viện, không đổi mã ứng dụng |
| detect-secrets (`PYTHONUTF8=1`) | 0 mục mới | Có (so mã băm với bản cũ, mồi) |
| Soát lịch sử git | Sạch | Có |
| pytest | Ca đã sửa 10/10 dưới tải thật; giả lập chậm: mới qua, cũ hỏng; 2 đột biến đều bị bắt | Có |
| ruff 0.16.10 | `All checks passed!` | Có |

## Ghi nhận (không thành lỗi)

- Soi Lỗi đã soát các ca cùng kiểu (mục 3 báo cáo Soi Lỗi). `tests/test_site_index_t042.py:211` và `tests/test_t041_site_index.py:88` so một lần chờ khóa với 5 giây, còn dư nhưng không nhiều khi máy rất bận. Đồng ý: theo dõi, chưa cần phiếu. Nếu sau này hỏng oan thì sửa theo đúng cách T-073 (không nới điều kiện kiểm phần mềm).

## Điều kiện

Không có.

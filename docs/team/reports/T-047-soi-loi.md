# Báo cáo T-047 · Kiểm thử rút gọn: khai báo Pillow và pillow-heif

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-047](../tickets/T-047-khai-bao-pillow-va-pillow-heif.md) |
| Ngày nộp | 2026-10-19 |
| Kết quả | Hoàn thành · **ĐẠT** |

## Tóm tắt (cho chủ dự án)

Hai thư viện ảnh được khai báo đúng, file khóa phiên bản (`uv.lock`) cài sạch được trên một môi trường hoàn toàn mới. Test của Thợ Máy không phụ thuộc thứ tự chạy và trả lại đúng trạng thái của Pillow. Tôi thêm 16 test cho ảnh HEIC hỏng, cắt cụt và file giả mạo đuôi `.heic`: tất cả báo lỗi bình thường, không treo, không sập chương trình. Không tìm thấy lỗi trong phiếu này; có 2 điều cần nhớ khi viết code mở ảnh thật (G3-3).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t047.py` | Mới, 16 test: HEIC cắt cụt/rỗng/hỏng giữa file, ảnh JPEG/PNG/WebP đổi đuôi `.heic`, file rác đổi đuôi `.heic`, chạy HEIC hỏng trong tiến trình con để chắc không sập/treo |
| `docs/team/reports/T-047-soi-loi.md` | Báo cáo này |

Không sửa `pyproject.toml`, `uv.lock`, code ứng dụng hay test của Thợ Máy.

## Kết quả kiểm

### 1. Khai báo thư viện và `uv.lock`

- `pyproject.toml`: có `"pillow>=12.3"` và `"pillow-heif>=1.8.1"`, kèm chú thích ngày duyệt. Đúng phiếu.
- `uv.lock`: thêm đúng một gói `pillow-heif 1.8.1` (phụ thuộc duy nhất `pillow`); khối `seo-app` có cả hai tên. Có wheel Windows cho cp312 (bản dự án dùng, `.python-version` = 3.12) đến cp315.
- `uv sync --locked` trên **môi trường mới và bộ nhớ đệm mới** (thư mục tạm, `UV_PROJECT_ENVIRONMENT` + `UV_CACHE_DIR` riêng): cài sạch, exit 0; trong môi trường đó `PIL 12.3.0`, `pillow_heif 1.8.1`, `libheif 1.23.6`.
- `uv lock --check`: `Resolved 70 packages`, exit 0 (lock khớp `pyproject.toml`).

### 2. `revision` của `uv.lock` đổi 3 → 5

```
$ uv --version
uv 0.12.23 (46b84fd0b 2026-10-03 x86_64-pc-windows-msvc)
```

Thử với uv cũ hơn (chạy qua `uvx --from uv==<bản>`, bộ nhớ đệm tạm):

| Bản uv | `uv lock --check` trên lock `revision = 5` | `uv lock` có ghi lại file không |
|---|---|---|
| 0.9.5 (2025-10-21) | Qua, exit 0 | Không đổi file (giữ `revision = 5`) |
| 0.11.0 (2026-03-23) | Qua, exit 0 | (không thử) |

Kết luận: máy dùng uv cũ (≥ 0.9.5) **vẫn đọc được** lock này. Dù vậy nên dặn máy kia nâng lên **uv 0.12.23** (`uv self update`) để hai máy ghi lock giống nhau, tránh diff `revision` qua lại.

### 3. Test của Thợ Máy `tests/test_pillow_heif_setup.py`

- Không gọi mạng: bộ chặn mạng tự động của `tests/conftest.py` áp cho mọi test; ảnh HEIC tạo trong `tmp_path`.
- Trả lại bảng định dạng: tôi gọi trực tiếp fixture `heif_registry_restored`, đăng ký HEIF ở giữa, rồi so sánh. Sau fixture: 6 bảng (`ID`, `OPEN`, `MIME`, `SAVE`, `SAVE_ALL`, `EXTENSION`) **giống hệt** trước, **cùng đối tượng** (không thay bằng bảng mới), `HEIF` không còn. Đối chiếu mã `register_heif_opener()` của pillow-heif 1.8.1: hàm chỉ ghi đúng 6 bảng này (và `options`, nhưng gọi không tham số thì `options` không đổi).
- Chạy riêng từng test: cả 3 qua. Đảo thứ tự (đăng ký trước, "chưa đăng ký" sau): 3 qua. Chạy file của tôi (đăng ký HEIF 15 lần) **trước** test "chưa đăng ký": 18 qua, **0 skip** (`-rs` không báo skip nào), tức bảng được trả lại thật chứ không phải test tự bỏ qua.

### 4. Ảnh HEIC hỏng và file giả mạo đuôi `.heic` (test mới)

| Trường hợp | Kết quả thật |
|---|---|
| File rỗng, 12 byte đầu, 100 byte đầu, đầu thật + thân toàn số 0 | `UnidentifiedImageError` ngay ở `Image.open` |
| Cắt còn một nửa, thiếu 10 byte cuối | `Image.open` **qua** (format HEIF, đúng kích thước); `load()` báo **`ValueError`** "Invalid input: Unexpected end of file…" |
| Đảo bit giữa dữ liệu ảnh, xóa 2.000 byte cuối thành số 0 | Giải mã **không báo lỗi**, ra ảnh đúng kích thước (điểm ảnh rác); không treo |
| JPEG, PNG, WebP đổi đuôi `.heic` | Pillow nhận đúng JPEG/PNG/WebP theo nội dung, không nhận nhầm là HEIF; với `formats=["HEIF"]` thì `UnidentifiedImageError` |
| Chữ tiếng Việt + `<script>`, byte ngẫu nhiên, PDF, khung `ftyp heic` giả + rác | `UnidentifiedImageError` (cả khi không giới hạn định dạng) |
| 6 mẫu hỏng mở trong tiến trình con (timeout 120 s) | Tiến trình con thoát mã 0, mọi lỗi là lỗi Python bắt được; mỗi lần dưới 2 s |

## Bằng chứng

```
$ uv run pytest tests/test_soi_loi_t047.py -v
16 passed in 25.60s        (lần đầu, máy lạnh; các lần sau ~5 s)

$ uv run pytest -q -rs --durations=3 tests/test_pillow_heif_setup.py tests/test_soi_loi_t047.py
1.60s call  tests/test_soi_loi_t047.py::test_heic_hong_khong_lam_sap_hay_treo_tien_trinh
19 passed in 6.37s

$ uv run pytest
5643 passed, 11 skipped, 35 xfailed, 1 warning in 891.64s (0:14:51)
(= 5.627 của Thợ Máy + 16 test mới; cảnh báo duy nhất là Pydantic ở tests/test_soi_loi_t028.py,
 không liên quan Pillow; chậm hơn lần Thợ Máy vì worktree khác chạy test cùng lúc)

$ uv run ruff check .
All checks passed!

$ uv run ruff format --check tests/test_soi_loi_t047.py tests/test_pillow_heif_setup.py
2 files already formatted
```

## Đối chiếu tiêu chí xong

- [x] `pyproject.toml` khai báo `pillow>=12.3`, `pillow-heif` (mục 1)
- [x] `uv.lock` khớp, `uv sync --locked` sạch trên môi trường mới (mục 1)
- [x] Test của Thợ Máy không phụ thuộc thứ tự, trả lại bảng định dạng, không gọi mạng (mục 3)
- [x] Thêm test HEIC hỏng/cắt cụt và file không phải HEIC đổi đuôi (mục 4, `tests/test_soi_loi_t047.py`)
- [x] Ghi bản uv và hành vi `revision = 5` (mục 2)
- [x] `uv run pytest` 0 hỏng, `uv run ruff check .` sạch (mục Bằng chứng)

## Lỗi tìm thấy

Không có lỗi trong phạm vi phiếu T-047.

## Rủi ro và điểm cần chú ý (cho G3-3, code mở ảnh thật)

1. **HEIC cắt cụt báo `ValueError`, không phải `OSError`, và chỉ nổ ở `load()`.** Tái hiện: tạo HEIC, cắt còn một nửa, `Image.open(p, formats=["HEIF"])` qua; `image.load()` ném `ValueError`. Ảnh JPEG cắt cụt của Pillow thì ném `OSError`. Code G3-3 phải gọi `load()` (hoặc thao tác giải mã) **trong** khối bắt lỗi và bắt cả `(OSError, ValueError)`, nếu không người dùng chọn ảnh iPhone chép dở từ USB/Drive sẽ làm trang Streamlit hiện lỗi đỏ. Test `test_heic_cat_cut_qua_duoc_open_chi_hong_o_load` ghi lại hành vi này.
2. **HEIC hỏng giữa dữ liệu vẫn giải mã được thành ảnh rác, không có lỗi.** Bộ giải mã HEVC không kiểm tổng; không phát hiện được bằng bắt lỗi. Chỉ ghi để biết (người dùng sẽ thấy ảnh xem trước bị nhòe/sai màu).
3. **Test "chưa đăng ký" của Thợ Máy có `pytest.skip` khi HEIF đã đăng ký sẵn.** Hiện không bao giờ skip (đã kiểm `-rs`). Nhưng khi G3-3 đăng ký HEIF lúc import module ảnh, test này sẽ lặng lẽ skip thay vì kiểm. Đề xuất: ở G3-3, fixture tự gỡ `HEIF` khỏi bảng trước test thay cho `skip`.
4. Bộ test toàn repo chạy lúc các worktree khác (`wt-T-042`, `wt-T-048`) cũng đang chạy test; test đo tốc độ có thể chậm hơn bình thường.

## Đề xuất

- Chỉ Huy dặn máy kia: `uv self update` lên 0.12.23 trước khi `uv sync`.
- G3-3 (Thợ Máy): bắt `(OSError, ValueError)` quanh cả `open` lẫn `load`, kèm giới hạn số điểm ảnh (góp ý Lá Chắn T-046 số 4); thay `skip` trong `test_chua_dang_ky_thi_pillow_khong_mo_duoc_heic` như mục 3.
- Lá Chắn: CVE của libheif 1.23.6, libde265 1.1.3, x265 4.3 (Soi Lỗi không kiểm).

## Câu hỏi cho chủ dự án

Không có.

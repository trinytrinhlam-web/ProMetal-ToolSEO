# Báo cáo T-058 · Nâng lên Pillow 13

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-058](../tickets/T-058-nang-pillow-13.md) |
| Ngày nộp | 2026-10-20 |
| Kết quả | Hoàn thành (chờ Chỉ Huy mở app thật kiểm mọi trang) |

## Tóm tắt (cho chủ dự án)

Thư viện ảnh Pillow đã lên **bản 13.0.0** (trước là 12.3.0), vá 40 khuyến cáo bảo mật của bản cũ. Streamlit ghi "chỉ chạy với Pillow dưới 13", nên phải ép bằng một dòng `override-dependencies` trong `pyproject.toml`; chỉ duy nhất gói Pillow đổi, mọi thư viện khác giữ nguyên. Toàn bộ test chạy qua trên Windows, kể cả test HEIC (pillow-heif 1.8.1 chạy tốt với Pillow 13) và một test mới cho Streamlit hiển thị ảnh Pillow. Người dùng không thấy gì khác trên giao diện. Nếu app hỏng thì quay về bản cũ bằng 3 bước ở mục "Cách quay về".

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `pyproject.toml` | `pillow>=12.3` → `pillow>=13.0.0`; thêm `[tool.uv] override-dependencies = ["pillow>=13.0.0,<14"]` kèm chú thích ngày chốt và cách quay về |
| `uv.lock` | `pillow` 12.3.0 → 13.0.0 (sdist + 68 wheel, mã băm mới); thêm mục `[manifest] overrides`; `requires-dist` của `seo-app` ghi `pillow>=13.0.0`. Không gói nào khác đổi (vẫn 70 gói) |
| `tests/test_pillow_version_t058.py` | Mới, 2 test: Pillow cài đúng bản 13.x (khớp metadata); `st.image` nhận một ảnh Pillow tạo trong bộ nhớ, không lỗi, ra đúng 1 phần tử ảnh có chú thích và địa chỉ media `.jpg`/`.png` |

Không có test cũ nào ghim số phiên bản 12.x (đã `grep` `12.3`, `pillow`, `PIL` trong `tests/`), nên không sửa test cũ. Không đụng `app/**`, `config/**`, `seo_app/**`, `tests/conftest.py`.

## Thông tin phiên bản

| Gói | Trước | Sau | Ghi chú |
|---|---|---|---|
| `pillow` | 12.3.0 | **13.0.0** (PyPI, sdist tải lên 2026-10-16 22:18 UTC) | Bản 13 mới nhất trong khoảng `<14` (`uv lock --upgrade-package pillow --dry-run`: "No lockfile changes detected") |
| `pillow-heif` | 1.8.1 | 1.8.1 | Chỉ đòi `pillow>=11.1.0`, không chặn trên → hợp lệ với 13. libheif 1.23.6, libde265 1.1.3 không đổi |
| `streamlit` | 1.65.0 | 1.65.0 | Khai báo `pillow<13,>=7.1.0` → bị override vượt qua |

## Bằng chứng

```
$ git merge origin/main        # bước 0, merge (không rebase), lấy T-042 + quyết định 20/10
$ uv sync && git push origin team/T-058
   bfd48bc..5e5c02b  team/T-058 -> team/T-058

$ uv lock
Resolved 70 packages in 1.17s
Updated pillow v12.3.0 -> v13.0.0
(uv 0.12.23 KHÔNG in cảnh báo nào về override)

$ uv sync
 - pillow==12.3.0
 + pillow==13.0.0
(cảnh báo duy nhất: không tạo được hardlink, uv chép file thay thế; không liên quan override)

$ uv lock --check
Resolved 70 packages in 3ms          # lock khớp pyproject

$ uv pip check
Found 1 incompatibility
The package `streamlit` requires `pillow>=7.1.0,<13`, but `13.0.0` is installed
(ĐÚNG như dự tính: đây là chỗ override cố ý vượt; uv lock/sync không báo, chỉ `uv pip check` báo)

$ uv tree --invert --package pillow
pillow v13.0.0
├── pillow-heif v1.8.1
├── seo-app v0.1.0
└── streamlit v1.65.0

$ uv run python -c "import PIL, pillow_heif, streamlit; print(PIL.__version__, pillow_heif.__version__, streamlit.__version__)"
13.0.0 1.8.1 1.65.0

$ uv export --format requirements-txt --no-hashes > req.txt     # 69 dòng ghim, có pillow==13.0.0
$ uvx pip-audit -r req.txt --disable-pip --no-deps              # pip-audit 2.10.1, nguồn PyPI
No known vulnerabilities found
$ uvx pip-audit -r req.txt --disable-pip --no-deps -s osv       # nguồn OSV
No known vulnerabilities found
(bỏ qua 1 dòng `-e .` là chính dự án)

$ uv run pytest tests/test_pillow_version_t058.py tests/test_pillow_heif_setup.py tests/test_soi_loi_t047.py -v
21 passed in 11.97s   (gồm 1 lần chạy đầu test mới hỏng do tôi dùng sai tên phần tử "imgs",
                       đã sửa thành at.get("image"); xem commit 47ff1c4)

$ uv run pytest
7172 passed, 11 skipped, 27 xfailed, 1 warning in 659.25s (0:10:59)
(0 hỏng, 0 lỗi; cảnh báo duy nhất: Pydantic trong tests/test_soi_loi_t028.py, có từ trước, không liên quan Pillow)

$ uv run pytest tests/test_app_pages.py tests/test_pillow_heif_setup.py tests/test_soi_loi_t047.py tests/test_pillow_version_t058.py -q -rs
39 passed in 30.41s   (không test nào bị bỏ qua: test mở mọi trang và test HEIC đều chạy thật)

$ uv run ruff check .
All checks passed!
```

**Kiểm thêm các hàm Pillow mà Streamlit 1.65 gọi** (`streamlit/elements/lib/image_utils.py`: `Image.open`, `Image.fromarray`, `resize(resample=Image.BILINEAR)`, `Image.Resampling`, `ImageFile.ImageFile`, `GifImagePlugin.GifImageFile`): chạy với `warnings.simplefilter("error")` trên Pillow 13, tạo ảnh từ numpy, thu nhỏ, lưu rồi mở lại PNG/JPEG/GIF/WEBP: không lỗi, không cảnh báo "sắp bỏ". App chỉ có một `st.image` (`app/main.py`, logo SVG, Streamlit đọc như chữ, không qua Pillow).

## Tra khuyến cáo của kho `python-pillow/Pillow` (2026-10-20 07:4x giờ VN)

`gh api repos/python-pillow/Pillow/security-advisories?per_page=100`: 61 khuyến cáo đã công bố, mới nhất 2026-10-19 09:47 UTC.

| Nhóm | Số lượng |
|---|---|
| Ảnh hưởng 12.3.0, vá ở **13.0.0** | **40** (2 nghiêm trọng, 13 cao, 22 trung bình, 3 thấp); gồm GHSA-8g5g-8vmr-9782 (JPEG `thumbnail()`/`draft()`), GHSA-g7cr-3p24-7wf7 (ghi JPEG), GHSA-g4qv-2jxx-769h (PNG eXIf), GHSA-p8hx-v2p6-rp84 (MPO `seek()`) |
| **Ảnh hưởng cả 13.0.0, chưa có bản vá** | **1**: GHSA-654x-cwwv-5j9c (trung bình, công bố 2026-10-19, khoảng `11.2.1 - 13.0.0`): xuất ảnh sang Arrow (`__arrow_c_array__`, `Image.fromarrow`) lộ vùng nhớ cũ **chỉ khi** đặt biến môi trường `PILLOW_ALIGNMENT` > 1 |
| Cũ hơn, đã vá trước 12.3.0 | 20 |

Về GHSA-654x-cwwv-5j9c: `grep` `PILLOW_ALIGNMENT`, `fromarrow`, `__arrow_c_` trong `app/`, `seo_app/`, `config/`, `tests/`, `.env.example` và trong thư viện Streamlit: không có kết quả. App không đặt biến đó và không xuất ảnh sang Arrow → không có đường đi. Pillow 12.3.0 cũng bị lỗi này, nên nâng không làm xấu đi.

**Lệch số với Lá Chắn T-047:** biên bản T-047 (tra 2026-10-19) ghi 53 khuyến cáo vá ở 13.0.0; hôm nay API trả 40 (tôi đếm theo trường `patched_versions` chứa `13.0.0`, và đối chiếu riêng khoảng ảnh hưởng: 41 mục chạm 12.3.0 = 40 + GHSA-654x). Có thể một số mục đã bị gộp hoặc rút sau ngày 19; tôi không có danh sách 53 mã của Lá Chắn để so từng mục. Kết luận không đổi: mọi mục còn công bố ảnh hưởng 12.3.0 đều đã vá ở 13.0.0, trừ GHSA-654x.

## Cách quay về Pillow 12.3.0 (nếu app hỏng)

1. Trong `pyproject.toml`: xóa khối `[tool.uv]` (3 dòng chú thích + `override-dependencies = [...]`), đổi `"pillow>=13.0.0"` về `"pillow>=12.3"`.
2. Chạy `uv lock` (mong đợi: `Updated pillow v13.0.0 -> v12.3.0`), rồi `uv sync`.
3. Xóa `tests/test_pillow_version_t058.py` (test này đòi bản 13), chạy `uv run pytest`.

Hoặc nhanh nhất: `git revert` hai commit `3e037c2` (pyproject + lock) và `47ff1c4` (test), rồi `uv sync`. Khi quay về thì phải theo lựa chọn B (chủ dự án ký chấp nhận rủi ro, T-049 tránh `thumbnail()`/`draft()`, `seek()`, ghi JPEG).

## Đối chiếu tiêu chí xong

- [x] `override-dependencies = ["pillow>=13.0.0,<14"]`, khai báo trực tiếp `pillow>=13.0.0`, `uv lock` (`pyproject.toml`, `uv.lock`; commit `3e037c2`)
- [x] Ghi phiên bản (13.0.0), thư viện đổi theo (không có), pillow-heif 1.8.1 chạy với Pillow 13 (`tests/test_pillow_heif_setup.py`, `tests/test_soi_loi_t047.py` qua hết)
- [x] `uv export` + `uvx pip-audit` (PyPI và OSV): 0 lỗ hổng; tra khuyến cáo kho Pillow: mục "Tra khuyến cáo"
- [x] `uv run pytest` 0 hỏng, 0 lỗi trên Windows; `uv run ruff check .` sạch
- [x] Test nhỏ xác nhận phiên bản (`tests/test_pillow_version_t058.py`)
- [x] Cách quay về: mục trên
- [ ] Mở app thật kiểm mọi trang: việc của Chỉ Huy (`uv run streamlit run app/main.py`)

## Rủi ro và điểm cần chú ý

- **Chạy trái khai báo của Streamlit.** Streamlit chưa được thử chính thức với Pillow 13. Các hàm Pillow mà Streamlit 1.65 dùng đều chạy (mục Bằng chứng), `tests/test_app_pages.py` mở mọi trang không lỗi, nhưng test không thay được việc mở app thật.
- **`uv pip check` sẽ luôn báo 1 xung đột** (streamlit đòi `pillow<13`) chừng nào còn override. Đó là cố ý; ai chạy lệnh này sau đừng "sửa" bằng cách hạ Pillow.
- **Nâng Streamlit sau này:** override vẫn giữ Pillow 13 dù Streamlit mới khai báo gì. Khi Streamlit cho phép Pillow 13 thì bỏ override (giữ `pillow>=13.0.0` trực tiếp).
- **GHSA-654x-cwwv-5j9c** chưa có bản vá; không có đường đi trong app (xem trên). T-049 không nên dùng `Image.fromarrow`/xuất Arrow và không đặt `PILLOW_ALIGNMENT`.
- pip-audit vẫn chưa có các khuyến cáo Pillow tháng 10 trong cơ sở dữ liệu (nó cũng không báo gì cho 12.3.0), nên "0 lỗ hổng" của pip-audit chưa phải bằng chứng đủ; bằng chứng chính là tra trực tiếp kho Pillow.

## Đề xuất

- Lá Chắn kiểm D1 cho phiếu này (ép phiên bản trái khai báo Streamlit; không thêm gói mới) và đối chiếu lại con số 53 → 40.
- Ghi GHSA-654x-cwwv-5j9c vào điều kiện T-049 (không xuất Arrow, không đặt `PILLOW_ALIGNMENT`); theo dõi Pillow 13.0.1.
- Lượt quét cuối Giai đoạn 3: chạy lại pip-audit và tra lại kho Pillow.

## Câu hỏi cho chủ dự án

Không có.

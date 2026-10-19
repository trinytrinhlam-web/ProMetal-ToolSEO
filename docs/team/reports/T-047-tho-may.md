# Báo cáo T-047 · Khai báo Pillow và pillow-heif

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-047](../tickets/T-047-khai-bao-pillow-va-pillow-heif.md) |
| Ngày nộp | 2026-10-19 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

Dự án đã khai báo hai thư viện ảnh: **Pillow 12.3.0** (đã có sẵn nhờ Streamlit, nay ghi tên trực tiếp) và **pillow-heif 1.8.1** (để đọc ảnh HEIC của iPhone). Quét lỗ hổng toàn bộ thư viện: không có lỗ hổng đã biết. Có một test nhỏ tạo ảnh HEIC giả rồi mở lại bằng Pillow, chạy được trên Windows. Người dùng chưa thấy gì khác trên giao diện (chưa có code dùng thư viện ở phiếu này).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `pyproject.toml` | Thêm `pillow>=12.3`, `pillow-heif>=1.8.1` kèm chú thích ngày duyệt |
| `uv.lock` | Thêm gói `pillow-heif 1.8.1`; `pillow` giữ 12.3.0, nay là phụ thuộc trực tiếp; `revision` 3 → 5 (do uv 0.12.23 ghi) |
| `tests/test_pillow_heif_setup.py` | 3 test: có bộ giải mã libde265; chưa đăng ký thì Pillow không mở được HEIC; đăng ký rồi mở ảnh HEIC giả đúng kích thước |

Commit: `b9e4b64` (thư viện), `69a9442` (test), `784f3d5` (nháp báo cáo), commit báo cáo hoàn chỉnh ngay sau.

## Thông tin thư viện

| Gói | Bản | Giấy phép (metadata) | Phụ thuộc kéo theo vào `uv.lock` |
|---|---|---|---|
| `pillow` | 12.3.0 (đã có trong lock, phát hành 2026-07-01) | MIT-CMU | Không có |
| `pillow-heif` | 1.8.1 (phát hành 2026-10-11, bản mới nhất) | BSD-3-Clause (mã nguồn) | Chỉ `pillow>=11.1.0` (đã có) → **không thêm gói phụ nào khác** |

**Vì sao Pillow không lên 13:** Streamlit 1.65 khai báo `pillow<13,>=7.1.0`. `uv lock --upgrade-package pillow --upgrade-package pillow-heif --dry-run` báo "No lockfile changes detected", tức 12.3.0 là bản cao nhất dùng được. pip-audit không báo lỗ hổng cho 12.3.0.

**Thư viện C đi kèm wheel pillow-heif 1.8.1** (cùng bản trên Windows và Mac):

| Nền tảng | libheif | libde265 (giải mã HEVC) | Khác | Nguồn bằng chứng |
|---|---|---|---|---|
| Windows `win_amd64` (đã cài, chạy thật) | 1.23.6 | 1.1.3 | x265 4.3 (bộ mã hóa), MinGW runtime (`libgcc_s_seh`, `libstdc++`, `libwinpthread`) | `pillow_heif.libheif_info()` + file DLL trong `RECORD` |
| Mac `macosx_11_0_arm64` | 1.23.6 | 1.1.3 | `libx265.217.dylib` | Tải wheel từ PyPI vào thư mục tạm, đọc tên file `.dylib`, chuỗi phiên bản trong file, `LICENSES_bundled.txt`; không chạy |
| Mac `macosx_10_15_x86_64` | 1.23.6 | 1.1.3 | `libx265.217.dylib` | Như trên |

SHA-256 hai wheel Mac đã tải trùng với mã băm ghi trong `uv.lock` (`1c60f323…` arm64, `a8e7edf5…` x86_64).

**Giấy phép bản cài sẵn (quan trọng):** `LICENSES_bundled.txt` trong wheel ghi *"License for pillow-heif binary wheels: GPLv2, due to base library licenses"*: libheif và libde265 là LGPLv3, x265 là GPLv2. Mã nguồn pillow-heif là BSD-3. App chỉ dùng nội bộ trên máy chủ dự án, không phân phối lại, nên GPL không đặt thêm nghĩa vụ. Nếu sau này đóng gói app để phát cho người khác thì phải xem lại.

## Bằng chứng

```
$ uv add "pillow>=12.3" pillow-heif
Resolved 70 packages in 2.52s
 + pillow-heif==1.8.1
 ~ seo-app==0.1.0

$ uv run python -c "import pillow_heif; print(pillow_heif.libheif_info())"
{'libheif': '1.23.6', 'HEIF': 'x265 HEVC encoder (4.3+1-e9b8812)', 'AVIF': '',
 'encoders': {'x265': 'x265 HEVC encoder (4.3+1-e9b8812)', 'mask': 'mask'},
 'decoders': {'libde265': 'libde265 HEVC decoder, version 1.1.3'}}

$ uv export --format requirements-txt --no-hashes -o <scratchpad>/t047-req.txt
(69 dòng ghim phiên bản, có pillow==12.3.0, pillow-heif==1.8.1)

$ uvx pip-audit -r <scratchpad>/t047-req.txt --no-deps      # pip-audit 2.10.1
WARNING:pip_audit._cli:--no-deps is supported, but users are encouraged to fully hash their pinned dependencies
WARNING:pip_audit._cli:Consider using a tool like `pip-compile`: https://pip-tools.readthedocs.io/en/latest/#using-hashes
No known vulnerabilities found
Name    Skip Reason
------- ----------------------------------------------------------------------
seo-app Dependency not found on PyPI and could not be audited: seo-app (0.1.0)

$ uv run pytest tests/test_pillow_heif_setup.py -v
test_libheif_kem_bo_giai_ma_hevc PASSED
test_chua_dang_ky_thi_pillow_khong_mo_duoc_heic PASSED
test_dang_ky_roi_mo_lai_heic_dung_kich_thuoc PASSED
3 passed in 9.45s
(chạy ngược thứ tự: đăng ký trước, "chưa đăng ký" sau → vẫn 2 passed, chứng tỏ bảng định dạng được trả lại)

$ uv run pytest
5627 passed, 11 skipped, 35 xfailed, 1 warning in 551.55s (0:09:11)
(cảnh báo duy nhất: Pydantic trong test lớp AI tests/test_soi_loi_t028.py, không liên quan Pillow)

$ uv run ruff check .
All checks passed!
```

## Đối chiếu tiêu chí xong

- [x] `uv add "pillow>=12.3" pillow-heif`, bản mới nhất ổn định (`pyproject.toml`, `uv.lock`)
- [x] Báo cáo phiên bản, giấy phép, thư viện phụ, bản libheif/libde265 Windows và Mac (mục "Thông tin thư viện")
- [x] `uv export` + `uvx pip-audit` trên toàn bộ `uv.lock`: không có lỗ hổng đã biết. Pillow không có bản vá mới hơn trong giới hạn Streamlit cho phép
- [x] Có test: `tests/test_pillow_heif_setup.py` (không gọi mạng, ảnh HEIC giả tạo trong `tmp_path`)
- [x] `uv run pytest` 0 hỏng, 0 lỗi trên Windows; `uv run ruff check .` sạch
- [x] Báo cáo nộp tại `docs/team/reports/T-047-tho-may.md`

## Rủi ro và điểm cần chú ý

- **pip-audit không quét thư viện C đi kèm wheel** (libheif, libde265, x265). Nó chỉ tra cơ sở dữ liệu lỗ hổng của gói PyPI. Lá Chắn cần đối chiếu libheif 1.23.6 và libde265 1.1.3 với danh sách CVE (góp ý T-046 số 4). Tôi không tra CVE thư viện C trong phiếu này.
- **pillow-heif 1.8.1 mới phát hành 8 ngày** (2026-10-11). Chưa thấy vấn đề, ghi lại để biết.
- **Giấy phép wheel là GPLv2** (do x265 đi kèm), xem trên. Dùng nội bộ thì không vướng.
- **Pillow bị Streamlit giữ ở 12.x.** Khi Streamlit cho phép Pillow 13 thì `uv lock --upgrade-package pillow` + pip-audit lại.
- `pillow_heif.register_heif_opener()` ghi vào bảng định dạng **toàn cục** của Pillow. Test đã tự trả lại bảng sau mỗi lần chạy. Code thật (G3-3) nên đăng ký một lần ở chỗ cố định và luôn mở ảnh với `formats=[...]` cụ thể.
- `uv.lock` đổi `revision = 3` → `5` vì uv 0.12.23 ghi định dạng mới. Máy dùng uv cũ hơn có thể báo lock mới hơn; nên giữ uv cùng bản trên 2 máy.

## Đề xuất

- G3-3 (mở ảnh): áp giới hạn số điểm ảnh, dung lượng file và bắt lỗi cho cả đường mở HEIC, có test riêng (góp ý Lá Chắn T-046 số 4). App chỉ cần đọc HEIC (đầu ra là WebP), nên code thật không cần ghi HEIC; `register_heif_opener()` đăng ký cả mở lẫn lưu HEIC, chỉ cần không gọi lưu HEIC.
- Lá Chắn: kiểm CVE của libheif 1.23.6, libde265 1.1.3, x265 4.3 trước khi ĐẠT.

## Câu hỏi cho chủ dự án

Không có.

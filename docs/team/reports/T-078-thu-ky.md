# Báo cáo T-078 (phần Thư Ký) · README: nâng công cụ `uv` lên 0.13.4, bỏ câu nhận ảnh AVIF

| Mục | Nội dung |
|---|---|
| Agent | Thư Ký (`thu-ky`) · model: Claude Opus 5.5 |
| Phiếu | T-078 `T-078-nang-uv.md` (phần Thư Ký; Chỉ Huy B giao 30/10 23:45) |
| Nhánh | `team/T-078` (đầu `1ebf679`, phần Thợ Máy) |
| Ngày nộp | 2026-10-30 23:43 (+07:00, theo lệnh `date`) |
| Kết quả | Hoàn thành yêu cầu 1–4. Chỉ sửa `README.md` |

## Tóm tắt (cho chủ dự án)

- Cuối mục 2 (Windows) và mục 3 (Mac) có thêm khối «**Công cụ `uv` phải từ bản 0.13.4 trở lên**»:
  - lý do: bản cũ còn tin một chứng chỉ đã bị lộ, kẻ xấu có thể giả kho thư viện để cài mã độc;
  - 4 bước: mở cửa sổ lệnh, gõ `uv --version`, cũ thì gõ `uv self update`, rồi mở app như thường;
  - hai ca phụ: máy không tìm thấy lệnh `uv`, và `uv` cài bằng `pip`.
- Mục 13 «Xử lý sự cố» có dòng mới. Cửa sổ báo `Required uv version …` rồi «Cài thư viện bị lỗi» thì nâng `uv` theo mục 2 / mục 3. Chỉ cần nhìn phần đầu câu, vì phần gợi ý ở cuối câu có thể khác nhau giữa các bản `uv`.
- Mục 12 «Cập nhật phiên bản mới» thêm một dòng: cập nhật phần mềm không tự nâng `uv`.
- Mục 9 bỏ chữ AVIF khỏi danh sách ảnh được nhận; ảnh `.avif` nay ghi là bị bỏ qua. Câu «Tạm chưa nhận ảnh HEIC» (T-107 lượt 3) giữ nguyên từng chữ.
- Máy Windows của anh/chị đã là `uv 0.13.4`, không phải làm gì.

## Đã thay đổi

| Chỗ (`README.md`) | Thay đổi |
|---|---|
| `:29-37` (cuối mục 2, mới) | Khối «Công cụ `uv` phải từ bản 0.13.4 trở lên»: lý do (GHSA-hq85-5cpj-mr62); `run.bat` chỉ cài khi máy chưa có, không tự nâng. 4 bước: mở **Command Prompt** từ phím Windows (không cần mở thư mục dự án) → `uv --version` (so từng số, ví dụ 0.13.5, 0.14.0 là đủ; 0.12.23, 0.13.3 là cũ) → `uv self update` → mở `run.bat`. Hai ca phụ: không tìm thấy lệnh `uv` thì gõ `%USERPROFILE%\.local\bin\uv.exe`; `uv` cài bằng `pip` thì `pip install --upgrade uv` hoặc cài lại theo trang chính thức |
| `:49-57` (cuối mục 3, mới) | Như trên cho Mac: `Command + Space` → Terminal; `~/.local/bin/uv`; `pip3 install --upgrade uv` |
| `:336` (mục 9) | «App nhận ảnh JPG, PNG, WebP, AVIF, …» → «App nhận ảnh JPG, PNG, WebP, … file khác (kể cả ảnh AVIF `.avif`) bị bỏ qua …» |
| `:489` (mục 12) | Dòng mới: công cụ `uv` không tự nâng; thấy `Required uv version …` thì nâng như cuối mục 2 / mục 3 |
| `:497` (mục 13, dòng mới) | `error: Required uv version … does not match the running version …` rồi «Cài thư viện bị lỗi»: nâng `uv`, mở lại. Đuôi câu có thể khác theo bản `uv`. `set_password` cũng báo câu này khi `uv` cũ |
| `:498` (mục 13) | Dòng «Cài thư viện bị lỗi» thêm «(không có dòng `Required uv version` phía trên)» để hai dòng không lẫn nhau |
| `:507` (Dành cho người phát triển) | «Cần có uv» → «từ bản 0.13.4 (`required-version` trong `pyproject.toml`; bản cũ hơn bị từ chối, nâng bằng `uv self update`)» |

Không đổi số mục, không thêm mục mới. Không sửa `pyproject.toml`, `uv.lock`, code, file phiếu.

## Đối chiếu

| README nói | Bằng chứng |
|---|---|
| Cần `uv` ≥ 0.13.4 | `pyproject.toml:43` `required-version = ">=0.13.4"` (Thợ Máy `1ebf679`) |
| Câu báo bắt đầu bằng `Required uv version`; `uv sync` dừng | Thử trên máy (`uv 0.13.4`) với dự án thử trong thư mục tạm, `required-version = ">=99.0"`, chạy `uv --offline sync`: «error: Required uv version `>=99.0` does not match the running version `0.13.4`. Update `uv` by running `uv self update`.», mã thoát 2. Khớp báo cáo Thợ Máy |
| Đuôi câu có thể khác giữa các bản | Báo cáo Thợ Máy: đuôi «Update `uv` by running…» là của bản 0.13.4, chưa đối chiếu được bản 0.12.x (không hạ cấp máy) |
| `uv --version` và `uv self update` vẫn chạy được khi `uv` cũ | Cùng dự án thử: `uv --version`, `uv self version` chạy bình thường (mã 0); `uv --offline self update --dry-run` đi qua bước kiểm bản, dừng ở «network connectivity is disabled» (không bị chặn bởi `required-version`). Không gọi mạng, không đổi `uv` trên máy. Bản 0.12.x chưa kiểm được, nên README vẫn bảo mở cửa sổ lệnh từ phím Windows / Spotlight (không trong thư mục dự án) cho chắc |
| `run.bat` / `run.command` chỉ cài `uv` khi chưa có, không tự nâng | `run.bat:9-13`, `run.command:13-16` (`where uv` / `command -v uv`, chỉ cài khi không thấy) |
| «Cài thư viện bị lỗi» hiện sau câu của `uv` | `run.bat:25-29`, `run.command:26-29` (`uv sync` lỗi → in câu này) |
| `set_password` cũng báo câu này | `set_password.bat` (dòng 16), `set_password.command` (dòng 9) chạy `uv run`; Thợ Máy thử: `uv run` dừng cùng câu |
| `uv` nằm ở `%USERPROFILE%\.local\bin\uv.exe` (Windows), `~/.local/bin/uv` (Mac) | `run.bat:7`, `run.command:11` đưa thư mục này vào PATH trước khi gọi `uv`. Máy Windows: `Test-Path` file này `True`, `Get-Command uv` trỏ vào đó |
| App không nhận `.avif`, file `.avif` đếm vào «file không phải ảnh» | `seo_app/images/folders.py:62` (`IMAGE_EXTENSIONS` = `.jpg .jpeg .png .webp`), `:572` (`other_files`), `app/views/write.py:1404` (nhãn «file không phải ảnh» trong dòng «Bỏ qua: …») |
| Câu HEIC giữ nguyên | `git diff` không có dòng nào ở `README.md:337` |

## Kiểm tra

```
$ grep -n -i "avif" README.md
336:   - App nhận ảnh JPG, PNG, WebP, mỗi ảnh tối đa 40 MB. Lối tắt, mục ẩn, file khác (kể cả ảnh AVIF `.avif`) bị bỏ qua ...
  → chỉ còn câu nói AVIF bị bỏ qua; không câu nào nói app nhận AVIF

# Link nội bộ: README không có link neo `](#…)` (đếm: 0). Dẫn chiếu «mục N»: 2, 3, 6, 7, 7.1, 7.2,
# 7.5, 8, 9, 10, 11, 13; đều là mục có thật, số mục không đổi (## 1 … ## 13 như trước).

$ PYTHONUTF8=1 uvx detect-secrets scan README.md docs/team/reports/T-078-thu-ky.md
  "results": {}
  (lần quét đầu báo nhầm «Secret Keyword» ở chữ «set_password.bat:16» trong báo cáo này:
   không phải bí mật, đã viết lại thành «set_password.bat (dòng 16)»)

# Thử mồi: bản sao README ngoài repo thêm một dòng khóa giả → bắt được
# «Secret Keyword», «Base64 High Entropy String»: bộ quét đọc được file tiếng Việt.
```

Không chạy pytest, ruff: chỉ đổi `README.md` và báo cáo.

## Rủi ro và điểm cần chú ý

- **Câu báo của `uv` 0.12.x** (máy cũ thật) chưa thấy tận mắt. README chỉ dựa vào phần đầu câu `Required uv version`, theo dặn của Thợ Máy.
- **`uv self update` trong thư mục dự án với `uv` 0.12.x** chưa kiểm được; với 0.13.4 thì không bị chặn. README tránh ca này bằng cách mở cửa sổ lệnh mới từ phím Windows / Spotlight.
- Hướng dẫn Mac viết theo cách cài của `run.command`, chưa thử trên máy Mac (chủ dự án hiện chưa có máy Mac).
- Câu `'uv' is not recognized…` là câu của Windows tiếng Anh. README ghi thêm «hay câu tương tự» cho máy cài tiếng Việt.

## Câu hỏi cho chủ dự án

Không có.

## Lượt 2 (2026-10-31 08:20, +07:00)

Sửa 2 lỗi Thấp của biên bản Lá Chắn T-078 (`09a5569`, `docs/team/reports/T-078-la-chan.md`), theo tin Chỉ Huy B 31/10. Chỉ sửa chữ, không sửa hook, `AGENTS.md`, `pyproject.toml`, code.

### Tóm tắt (cho chủ dự án)

- Bước nâng `uv` trong README (cả Windows và Mac) nay dặn: **làm ở mạng nhà hoặc công ty, không dùng Wi-Fi công cộng**. Bản `uv` cũ tải bản mới qua đúng kênh chứng chỉ bị lộ, nên trên Wi-Fi lạ có thể bị tráo bản giả. Cách nâng bằng `pip` cũng dặn như vậy.
- Thêm quy tắc cho các agent: trước khi chạy công cụ kiểm tra bằng `uvx`, phải xem `uv --version` từ 0.13.4 trở lên; cũ hơn thì dừng và báo Chỉ Huy. Lớp chặn `uv` cũ của dự án không phủ lệnh `uvx`.
- Máy Windows của anh/chị đã là `uv 0.13.4`: không phải làm gì.

### Đã thay đổi

| Lỗi | Chỗ | Thay đổi |
|---|---|---|
| LC-T078-1 | `docs/team/security.md` mục 5, ngay trên khối lệnh (`:129`) | Đoạn mới: «**Trước khi chạy `uvx` / `uv tool run`:** chạy `uv --version`, phải từ **0.13.4** trở lên (T-078, GHSA-hq85-5cpj-mr62 …). Thấp hơn thì **không chạy**, dừng và báo Chỉ Huy. `required-version` của dự án (`pyproject.toml`) chỉ chặn lệnh dự án (`uv sync`, `uv run`…), **không chặn `uvx`**.» |
| LC-T078-1 | `.claude/agents/la-chan.md` bước 3 (`:25`) | Thêm cuối bước 3 (Chỉ Huy cho phép sửa đúng câu này): «Trước khi chạy `uvx`: `uv --version` phải từ 0.13.4 (T-078, GHSA-hq85-5cpj-mr62); cũ hơn thì không chạy, báo Chỉ Huy (`required-version` của dự án không chặn `uvx`).» |
| LC-T078-1 | `README.md:507` (Dành cho người phát triển) | «bản cũ hơn bị từ chối» → «bản cũ hơn bị từ chối ở lệnh dự án như `uv sync`, `uv run`»; thêm «`required-version` không áp dụng cho `uvx`: kiểm `uv --version` trước khi dùng `uvx` (quy tắc ở `docs/team/security.md` mục 5).» |
| LC-T078-2 | `README.md:33`, `:53` (bước 3 của khối Windows, Mac) | Thêm «**Làm bước này ở mạng nhà hoặc công ty, không dùng Wi-Fi công cộng**: `uv` cũ tải bản mới qua đúng kênh chứng chỉ bị lộ.» |
| LC-T078-2 | `README.md:37`, `:57` (dòng `pip install` / `pip3 install`) | Thêm «Cũng làm ở mạng nhà hoặc công ty, không dùng Wi-Fi công cộng.» Không nêu bản `pip` (theo biên bản) |

### Ghi chú

- Các chỗ khác nhắc `uvx` (`grep -rln uvx`, bỏ `docs/team/reports`, `tickets`, `.venv`): chỉ còn `docs/team/dong-bo.md` (phiếu điều phối của Chỉ Huy, ngoài phạm vi). Hồ sơ agent khác trong `.claude/agents/` và `AGENTS.md`, `docs/team/rules.md` không có lệnh `uvx`.
- Chú thích `pyproject.toml:40-42` (phần Thợ Máy) vẫn ghi «uv cũ hơn thì từ chối chạy» mà không nói `uvx`. Biên bản nêu chỗ này trong vị trí của LC-T078-1, nhưng tin giao việc không gồm `pyproject.toml`, nên tôi không sửa. Nếu cần thì thêm «(không áp dụng cho `uvx`)» ở lượt Thợ Máy sau.

### Kiểm tra lượt 2

```
$ PYTHONUTF8=1 uvx detect-secrets scan README.md docs/team/security.md .claude/agents/la-chan.md docs/team/reports/T-078-thu-ky.md
  "results": {}
```

Số mục README không đổi (## 1 … ## 13); README không có link neo `](#…)`. Không chạy pytest, ruff (chỉ đổi tài liệu).

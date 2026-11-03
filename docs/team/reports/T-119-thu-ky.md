# Báo cáo T-119 · Tài liệu sau rà soát Fable: `pip-audit`, sổ rủi ro, README mục Google, chú thích `uvx`

| Mục | Nội dung |
|---|---|
| Agent | Thư Ký (`thu-ky`) · model: Claude Opus 5.5 |
| Phiếu | T-119 «Tài liệu sau rà soát Fable» (Chỉ Huy B giao 02/11 18:35) |
| Nhánh | `team/T-119` (từ `main` cục bộ `b953e5e`) |
| Ngày nộp | 2026-11-02 18:33 (+07:00, theo lệnh `date`) |
| Kết quả | Hoàn thành việc 1–4. Sửa `docs/team/security.md`, `README.md`, chú thích trong `pyproject.toml`; không sửa code, `uv.lock`, giá trị nào trong `pyproject.toml` |

## Tóm tắt (cho chủ dự án)

- README có **mục 14 mới «Kế hoạch và Google Sheets»**:
  - tạo tài khoản dịch vụ Google: project riêng, chỉ bật Sheets API, không gán vai trò;
  - cất file khóa đúng chỗ, khai báo trong `.env`;
  - chia sẻ đúng một Sheet cho email dịch vụ (quyền Người chỉnh sửa, không bật «Bất kỳ ai có đường liên kết»);
  - các nút ở **Cài đặt → 📗 Google** và trang **Kế hoạch**, kể cả nút **🌐 Cập nhật trạng thái từ website**;
  - phải làm gì khi lộ file khóa, bảng lỗi thường gặp.

  Trước đây README chưa có mục này, dù trong app đã có câu báo chỉ tới «README mục «Kế hoạch và Google Sheets»».
- Sổ rủi ro (`security.md` mục 6) thêm 2 dòng mức Thấp của lớp `.env` và lớp lọc hồ sơ, theo đề nghị Lá Chắn. Anh/chị đã đồng ý ngày 02/11 (Chỉ Huy B báo lúc 18:55).
- `security.md` mục 5 thêm cách chạy công cụ quét lỗ hổng thư viện (`pip-audit`) chạy được với dự án này. Đã chạy thử: 69 thư viện, không có lỗ hổng đã biết.
- Chú thích `required-version` trong `pyproject.toml` nói rõ dòng này không chặn `uvx`.

## Đã thay đổi

| Chỗ | Thay đổi |
|---|---|
| `pyproject.toml:40-44` (chỉ chú thích) | «uv cũ hơn thì từ chối chạy» → «từ chối chạy lệnh của dự án (`uv sync`, `uv run`, `uv lock`…)»; thêm «Dòng này KHÔNG áp cho `uvx` / `uv tool run` (LC-T078-1): trước khi dùng `uvx`, tự kiểm `uv --version` ≥ 0.13.4 (docs/team/security.md mục 5)». Giá trị `required-version = ">=0.13.4"`, `override-dependencies` không đổi (đọc lại bằng `tomllib`: `>=0.13.4`, `['pillow>=13.0.0,<14']`) |
| `docs/team/security.md` mục 5, khối lệnh | Dòng `uvx pip-audit  # (đọc môi trường uv)` (không chạy được) → `uvx pip-audit -r <tạm>/req.txt --no-deps --disable-pip` kèm «cách chạy: xem ngay dưới» |
| `docs/team/security.md:139-148` (mới) | Đoạn «**Chạy `pip-audit`**»: vì sao `-r` thường hỏng (pillow ép bản 13 ↔ Streamlit `pillow<13`, T-058); 3 bước: `uv --version` ≥ 0.13.4 → `uv export --format requirements-txt --no-hashes --no-emit-project -q -o <tạm>/req.txt` (file tạm ngoài repo) → `uvx pip-audit -r <tạm>/req.txt --no-deps --disable-pip --progress-spinner off`; hai dòng `WARNING` là bình thường; pip-audit không thấy lỗ hổng thư viện C trong wheel (libheif) → xem sổ rủi ro |
| `docs/team/security.md:176` (mới, mục 6) | T-016-020 #5: `env_file.py` dùng `dotenv.parser.parse_stream` (module con không ghi trong tài liệu chính thức; bản ghim 1.2.4). Lý do chấp nhận: rủi ro bảo trì, bản ghim; lỗi theo hướng an toàn nhờ bước so bằng `dotenv_values` (`_parse`, `env_file.py:258-273`); chạy lại `tests/test_env_file.py` mỗi lần nâng python-dotenv |
| `docs/team/security.md:177` (mới, mục 6) | T-022-024 #3: đoạn thụt lề sau dòng trống bị giấu theo đoạn trên có nhãn (lọc thừa, `rules.py:131-132`). Lý do chấp nhận: lọc thừa là hướng an toàn; sửa ngược lại thì để lọt; hồ sơ hiện tại không có đoạn thụt lề nào sau dòng trống (kiểm 02/11) |
| `README.md:503-553` (mục 14 mới, ngay trước «Dành cho người phát triển») | «Kế hoạch và Google Sheets»: tạo tài khoản dịch vụ (4 bước), cất file khóa, khai báo trong app (6 bước), trang Kế hoạch (danh sách, cung cấp kế hoạch, Viết bài, Cập nhật trạng thái từ website), giữ an toàn, bảng 7 câu lỗi |
| `README.md:65` (mục 4) | «**Kế hoạch** (đưa kế hoạch của bạn vào, mục 14)» |
| `README.md:78` (mục 5) | «File JSON service account của Google nên để ngoài thư mục dự án» → «File khóa JSON (service account) của Google phải để ngoài thư mục dự án và ngoài thư mục ảnh (mục 14)» (app từ chối file nằm trong hai chỗ này) |

**Vì sao mục 14 ở cuối:**

- Tên mục lấy đúng chữ mà câu báo của app đã dẫn chiếu (`MSG_NO_GOOGLE` `app/views/plan.py:84-87`).
- Đặt cuối phần người dùng (sau «13. Xử lý sự cố») thì không phải đánh số lại mục nào, không đổi «mục N» cũ.
- Cách này cũng không đụng các dòng mà nhánh `team/T-112` (README mục 11, chưa gộp) sửa.

## Đối chiếu

**README mục 14.** 51 câu trích, tên nút, nhãn ô đều có trong `app/`, `seo_app/`, `config/`, `.env.example`. Kiểm bằng script Python đọc UTF-8, có nối chuỗi viết tách dòng: «thiếu: 0».

| README nói | Code |
|---|---|
| Khung tài khoản dịch vụ, email, «chưa dùng được», ô file khóa chỉ sửa tay trong `.env` | `account_card` `app/views/settings.py:573-598`; `.env.example:38-47` |
| File khóa: trong thư mục phần mềm, thư mục ảnh thì từ chối; thư mục đồng bộ, Mac đọc được thì cảnh báo | `seo_app/google/service_account.py:83-90` (`_MSG_IN_PROJECT`, `_MSG_IN_IMAGES`), `:118-125` (`_WARN_SYNC`, `_WARN_MODE`), `:175-187` |
| Chỉ cần Sheets API | `SHEETS_SCOPE` `service_account.py:44`; `sheets.py:12` (chỉ `sheets.googleapis.com` và máy chủ mã) |
| Ô link Sheet, Lưu (chỉ lấy mã, ghi `GOOGLE_SHEET_ID`), Bỏ Sheet | `sheet_card` `settings.py:601-635`, `_save_sheet` `:533-549` |
| Kiểm tra kết nối, Chuẩn bị trang tính, Thêm cột còn thiếu | `check_card` `settings.py:638-681` |
| Danh sách, bản lưu 5 phút, Tải lại, lỗi thì hiện bản lưu | `plan_list` `app/views/plan.py:951-990`; `get_plan` `seo_app/plan/sync.py:321-345`; `DEFAULT_MAX_AGE_MINUTES = 5.0` `seo_app/storage/plan_cache.py:40` |
| Cung cấp kế hoạch, AI đọc, Đề xuất, Áp dụng | `plan.py:1039-1076`, `:392`, `:482`, `:517-523` |
| Viết bài, ghi trạng thái dòng, Thử ghi lại | `write_picker` `plan.py:893-917`, `pending_box` `:920-940`; `record_plan` `app/views/write.py` |
| Cập nhật trạng thái từ website: tick, Chọn tất cả, Ghi, chỉ 3 ô, 5 phút, «Lỡ lịch» 15 phút | `plan.py:967-968`, `web_check_box` `:740-800`, `MSG_WEB_NOTE` `:104-109`, `MSG_WEB_STALE` `:113-116`; `CHECK_MAX_AGE` `seo_app/plan/website.py:65` |
| Câu lỗi 403, 404, 429 | `_MSG_BY_STATUS` `seo_app/google/sheets.py:159-171` |
| Múi giờ WordPress «Hồ Chí Minh» | `timezone_warning` `seo_app/wordpress/client.py` («Nên đặt WordPress → Cài đặt → Tổng quan → Múi giờ là «Hồ Chí Minh»») |
| Điều kiện LC-T094-43 | `docs/team/reports/T-094-la-chan.md:137`; biên bản Fable `T-116-la-chan-nhom-4.md:128` |

Những ý của LC-T094-43 mà README mục 14 đã có:

- project Google riêng; chỉ bật Sheets API; tài khoản dịch vụ không có vai trò;
- khóa để ngoài thư mục dự án và thư mục đồng bộ; không gửi qua email, Zalo;
- chỉ chia sẻ đúng một Sheet, không bật «Bất kỳ ai có đường liên kết»;
- lộ khóa thì xóa khóa, tạo khóa mới, sửa `.env` cả hai máy;
- Mac `chmod 600`;
- WordPress đặt múi giờ «Hồ Chí Minh», lịch chạy (cron);
- tải Sheet về mở bằng Excel thì cẩn thận công thức.

Phần `.env.example` của điều kiện này đã có sẵn (`.env.example:38-52`), không phải sửa.

**Sổ rủi ro.**

- T-016-020 #5: nguồn là `docs/team/reports/T-016-020-la-chan.md:157`, `:213`.
- T-022-024 #3: nguồn là `docs/team/reports/T-022-024-la-chan.md:25`.
- Biên bản Fable `T-116-la-chan-nhom-3.md:36`, `:44`, `:71`, `:152` xác nhận cả hai còn đúng và chưa có dòng sổ.
- Vị trí code hiện tại: `seo_app/env_file.py:38` (nhập `parse_stream`), `:191`, `:148-150` (`_parse` = `dotenv_values`), `:258-273`; `seo_app/content/rules.py:131-132`.

## Kiểm tra

```
$ uv --version
uv 0.13.4 (7456b60bc 2026-10-20 x86_64-pc-windows-msvc)
$ uv export --format requirements-txt --no-hashes --no-emit-project -q -o <tạm>/req.txt   # 69 gói
$ PYTHONUTF8=1 uvx pip-audit -r <tạm>/req.txt --no-deps --disable-pip --progress-spinner off
WARNING:pip_audit._cli:--no-deps is supported, but users are encouraged to fully hash their pinned dependencies
WARNING:pip_audit._cli:Consider using a tool like `pip-compile`: …
No known vulnerabilities found
  (file tạm nằm ngoài repo; git status sau lệnh: chỉ pyproject.toml đang sửa)

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan README.md docs/team/security.md pyproject.toml docs/team/reports/T-119-thu-ky.md
  "results": {}
```

README: số mục 1–14, mọi «mục N» trỏ tới mục có thật; «mục 5» ở phần người phát triển là `security.md` mục 5. Không có link neo `](#…)`.

## Rủi ro và điểm cần chú ý

- **Hai dòng sổ rủi ro:** lúc đầu cột người quyết định ghi «chờ chủ dự án xác nhận», vì `rules.md` mục 4 xếp việc chấp nhận rủi ro vào việc phải hỏi chủ dự án. Chủ dự án đồng ý ngày 02/11 (tin Chỉ Huy B 18:55), nên cả hai dòng nay ghi «Chủ dự án đồng ý 2026-11-02».
- **Tên mục trên Google Cloud** (APIs & Services → Library, IAM & Admin → Service Accounts, Keys → Add key → Create new key → JSON) viết theo giao diện tiếng Anh thường gặp. Tôi chưa mở Google Cloud để đối chiếu.
- **Mục 14 nằm sau «Xử lý sự cố».** Cách này giữ số mục cũ, nhưng thứ tự đọc chưa thật tự nhiên. Khi nào README được sắp lại (ví dụ sau khi gộp T-112), có thể dời mục này lên gần mục 6 «Kết nối WordPress».
- LC-T094-44 (thử thật trên Sheet bản sao, cần chủ dự án) không thuộc phiếu này.
- Hai giới hạn `modified_gmt` của T-115: Chỉ Huy dặn ghi sổ sau khi Lá Chắn T-115 kết luận. Phiếu này chưa ghi.

## Câu hỏi cho chủ dự án

~~Có đồng ý ghi hai rủi ro Thấp ở `security.md` mục 6 (dòng 02/11: `parse_stream` của python-dotenv; lọc thừa đoạn thụt lề trong hồ sơ doanh nghiệp) vào sổ rủi ro đã chấp nhận không?~~ **Đã trả lời:** chủ dự án **đồng ý** ghi sổ cả hai dòng (2026-11-02, Chỉ Huy B báo lúc 18:55). Cột người quyết định đã đổi thành «Chủ dự án đồng ý 2026-11-02».

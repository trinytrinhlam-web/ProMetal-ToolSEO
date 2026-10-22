# Báo cáo T-069 · README: ảnh gửi hãng AI khi viết alt, cách đặt thư mục ảnh

| Mục | Nội dung |
|---|---|
| Agent | Thư Ký (`thu-ky`) · model: Claude Opus 5.5 |
| Phiếu | [T-069](../tickets/T-069-readme-anh-gui-ai.md) |
| Ngày nộp | 2026-10-22 |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

README có thêm hai phần. (1) Ở mục 7.2: việc viết alt gửi ảnh công trình (đã bỏ GPS, EXIF) cho hãng AI ghi ở `[tasks.alt]`; nên dùng Claude hoặc khóa **trả phí** của OpenAI/Gemini, vì khóa Gemini miễn phí cho Google dùng ảnh và cho người duyệt của Google xem. (2) Mục mới **8. Đặt thư mục ảnh**: cách khai báo `IMAGE_FOLDERS`, cách đặt tên thư mục công trình (`CT012 - Cổng inox - Tân Phú/truoc`), chỗ để ảnh AI, những chữ làm ảnh bị coi là ảnh AI, những điều cần tránh để ảnh thật không mất thẻ, và cách gỡ lỗi "Không mở được file lưu thẻ ảnh…". Mọi ví dụ trong mục 8 đã chạy thử trên code thật của `main` (`fa2cc39`). Hai mục cũ "Cập nhật phiên bản mới" và "Xử lý sự cố" đổi số thành 9 và 10 (không tài liệu nào trỏ tới số 8, 9 cũ).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `README.md` | Mục 7.2 thêm đoạn "Việc viết alt cho ảnh (`[tasks.alt]`)…" (dòng 139–142). Thêm mục 8 "Đặt thư mục ảnh" (dòng 198–263). Đổi số mục 8 → 9, 9 → 10 |
| `docs/team/reports/T-069-thu-ky.md` | Báo cáo này |

## Bằng chứng

```
$ uv run pytest tests/test_app_pages.py -q
18 passed in 48.05s

$ uv run ruff check .
All checks passed!

$ PYTHONUTF8=1 uvx detect-secrets scan README.md
results: {}   (0 mục)
# Mồi: bản sao README (có chữ tiếng Việt) thêm khóa giả AWS và ANTHROPIC_API_KEY giả
# → bắt đủ: AWS Access Key, Base64 High Entropy String, Secret Keyword. Đã xóa bản mồi
# (nằm ngoài repo, trong scratchpad).

$ git diff README.md | grep -E "^\+" | grep -inE "api[_-]?key|password|secret|token|Users/|ADMIN|ProMetal-ToolSEO|@|D:/"
(rỗng)
```

Không có test nào đọc README (`grep -rl README tests/` rỗng, không có `tests/test_readme*.py`).

Các ví dụ tên thư mục trong mục 8 được chạy qua `tags_for_image(ImageRef(0, …))` của code thật (script tạm trong scratchpad, không commit). Kết quả chính:

| Đường dẫn (bên dưới thư mục đã khai báo) | Kết quả |
|---|---|
| `CT012 - Cổng inox - Tân Phú/truoc/IMG_0001.jpg` | ảnh thật, CT012, Cổng inox, Tân Phú, trước |
| `CT012 - Cổng inox - Tân Phú/Hoàn thành/…`, `…/Sau/…`, `…/Hiện trạng/…`, `…/Trước khi làm/…` | sau / sau / trước / trước |
| `CT012 - Cổng inox - Tân Phú/IMG_0004.jpg` (ảnh để thẳng) | không có trước/sau |
| `Tân Phú - Cổng inox - CT012/truoc/…` (đổi thứ tự) | như ca đầu |
| `CT012 - Cổng inox - Nhà anh Tuấn - Tân Phú/…` | giữ CT012, Cổng inox, Tân Phú (phần tên khách bị bỏ) |
| `CT012 Cổng inox nhà anh Tuấn - Tân Phú/…` | **mất** CT012 và hạng mục, chỉ còn Tân Phú |
| `CT012 - Cổng inox - Quận 7 - Tân Phú/…` | khu vực để trống |
| `CT014 - Cua keo - q7/truoc/…` (không dấu) | CT014, Cửa kéo, Quận 7, trước |
| `CT012 - Cổng inox - Tân Phú/Ảnh AI/x.png`, `…/Hình AI/…`, `Ảnh AI/x.png`, `Ảnh minh họa/x.png` | ảnh AI (ca trong thư mục công trình giữ hạng mục) |
| `…/truoc/Gemini_Generated_Image_abc.png`, `…/Designer (3).png`, `…/AI01.png`, `…/IMG_AI_01.jpg` | ảnh AI |
| `Nhà chị Ái`, `Nhà anh Minh Hòa` (có dấu) | ảnh thật, giữ thẻ |
| `Nha chi Ai`, `Nha anh Minh Hoa` (không dấu) | ảnh AI, mất mã, khu vực, trước/sau |
| `Công ty Designer Home`, `Thuốc hàn Flux` | ảnh AI, mất thẻ |
| `Cua so ra ban cong` | ảnh thật (không thành "Sora") |
| `MidJourney`, `Mid Journey`, `Fire Fly`, `Co-Pilot`, `See Dream`, `Night Cafe`, `Comfy UI`, `HaiLuo` | ảnh AI |
| `Hai Luo`, `Leo nardo` | **ảnh thật** (không nhận ra) |
| `Ảnh tham khảo`, `Ảnh mạng` | ảnh thật |
| `Ảnh phối cảnh`, `Ảnh mô phỏng`, `Render`, `Ảnh trí tuệ nhân tạo`, `Hình do AI tạo`, `ai`, `Nhà ai`, `GenAI`, `AI images`, `do máy tạo`, `tạo tự động`, `Image Creator` | ảnh AI |

## Đối chiếu từng ý với code

**Yêu cầu 1 (mục 7.2, README dòng 139–142)**

- `[tasks.alt]` đang ghi `provider = "anthropic"`, `model = "claude-sonnet-5-5"`: `config/ai.toml` mục `[tasks.alt]`. README ghi "đang ghi Claude Sonnet".
- Ảnh gửi đi đã bỏ GPS, EXIF: bản gửi AI dựng lại từ điểm ảnh, JPEG không metadata (`seo_app/images/process.py:821` `make_ai_image`); `prepare_images` kiểm lại theo danh sách cho phép (`seo_app/images/alt.py:474`, docstring `alt.py:9-10`). Không gửi tên file, đường dẫn (`alt.py:9-11`).
- Chữ gửi kèm: thẻ (`tags`), từ khóa (`keyword`), quy tắc `[alt]` (`rules`) (`alt.py:449-488`). Thẻ gửi AI chỉ có hạng mục, khu vực, giai đoạn, không có mã công trình (`seo_app/images/tags.py:726-736` `reference`). README ghi đúng ba nhóm này.
- Gemini miễn phí / trả phí, người duyệt xem được: theo Lá Chắn T-050 LC-T050-4 (điều khoản Gemini API cập nhật 2026-04-28) và câu đề xuất ở báo cáo Thợ Máy T-062 mục Đề xuất. Không có code (code không biết khóa thuộc gói nào). Giữ ý "báo Chỉ Huy để ghi sổ rủi ro".
- Chưa có nút viết alt trên giao diện: `grep suggest_alt app/` rỗng. README nói rõ "Giao diện chưa có nút viết alt".

**Yêu cầu 2 (mục 8, README dòng 198–263)**

- Ví dụ `CT012 - Cổng inox - Tân Phú/truoc`: quy ước trong docstring `tags.py:3-6`; chạy thử ra đủ 4 thẻ (bảng trên).
- Tách phần bằng ` - ` và các dấu khác, phần không khớp bị bỏ cả phần: `tags.py:10-13`, `_split_parts` `:836-848`, `_parse_dir_name` `:863-895`.
- Danh sách mã, hạng mục, khu vực, trước/sau: `_CODE_PATTERN` `:79`, khu vực `:90-129`, trước/sau `:174-202`, hạng mục `:305-389`.
- Hai khu vực khác nhau thì để trống: `:18-20`, `_tags_from_dirs` `:910-939`.
- Tên thư mục gốc không được đọc (nên khai báo thư mục **chứa** công trình, và không khai báo riêng thư mục ảnh AI): `tags.py:32-35`, `:942-953`; `is_ai_name` (`:973-986`) có sẵn nhưng app chưa gọi (`grep is_ai_name app/` rỗng), đúng điều kiện 4 của Lá Chắn T-052 "cho tới khi T-056 làm".
- Ảnh AI để trong thư mục con có chữ AI, không mang mã, khu vực, trước/sau (giữ hạng mục): `tags.py:36-46`, `:933-937`.
- Danh sách chữ làm ảnh thành ảnh AI: `_AI_TOOLS` `:206-250`, `_AI_WORDS` `:251-263`, `_AI_PHRASES` `:269-280`, `_AI_JOINED` `:285-296`. README liệt kê đủ tên công cụ (trừ các dạng gõ tách `Mid Journey`… nêu riêng) và cụm tiếng Việt; bỏ `OIG…` (tên file Bing, người dùng không gõ) và `A.I.` (xem mục khác code).
- So không phân biệt hoa thường, phân biệt dấu (nên gõ có dấu): `tags.py:297-300`; mỗi dấu hiệu có thêm dạng không dấu `:473-488` (nên "Minh Hoa", "Ai" không dấu thành ảnh AI).
- Tên file ảnh cũng được xét: `tags_for_image` `:951-953`.
- App không ghi gì vào thư mục ảnh: `seo_app/images/folders.py:25` ("Chỉ đọc"), `seo_app/storage/image_tags.py:1-6`.
- Thẻ sửa tay chỉ nhớ trên máy đang dùng, trong `data/image_tags.sqlite`: `image_tags.py:1-6`, `:59`. Xóa file thì tạo lại, chỉ mất thẻ sửa tay: `image_tags.py:5-6`.
- Ảnh AI không sửa tay thành ảnh thật được: `_keep_ai` `image_tags.py:198-202`, câu báo `_MSG_AI_FOLDER` `:141-144`.
- Câu lỗi "Không mở được file lưu thẻ ảnh…": chép nguyên văn từ `_db_message` `image_tags.py:695-698`.
- Kiểm thư mục ở **Cài đặt → 🖼️ Ảnh** ("✅ tìm thấy" / "⚠️ không thấy trên máy này"): `app/views/settings.py:444`, `:473-479`.
- `IMAGE_FOLDERS` ngăn cách bằng `;`, ví dụ đường dẫn: `.env.example:48-51`, `seo_app/config.py:146-148`.

**Yêu cầu 3:** tiếng Việt, câu ngắn, có ví dụ; không có khóa, không có đường dẫn máy thật (ví dụ đường dẫn lấy từ `.env.example`; grep diff ở mục Bằng chứng rỗng).

**Điều kiện Lá Chắn chép trong phiếu:** T-052 điều kiện 4 (dòng 213, 239, 240, 249, 256), T-070 điều kiện 3 (dòng 241–244, 249–251), T-074 điều kiện 3 (dòng 245, 263), T-062 điều kiện 3 / LC-T050-4 (dòng 139–142).

## Chỗ phiếu khác code (đã theo code)

1. **Tên công cụ gõ tách (điều kiện T-074 số 3).** Phiếu dặn "gõ tên công cụ theo cách viết liền chuẩn (Midjourney, Firefly, Copilot, Seedream)". Từ T-077 (gộp sau khi lập điều kiện này), code đã nhận cả `Mid Journey`, `Fire Fly`, `Co Pilot`/`Co-Pilot`, `See Dream`, `MidJourney` (`tags.py:243-249`, `:865-867`). README vẫn giữ lời dặn (vì kiểu tách khác như `Hai Luo`, `Leo nardo` vẫn không nhận, đã chạy thử), nhưng nói rõ "app nhận được vài kiểu gõ tách … nhưng không phải mọi kiểu", không nói bốn tên trên gõ tách là hỏng.
2. **Thiếu một ý của Lá Chắn T-052 trong ghi chú của Chỉ Huy.** Điều kiện 4 của Lá Chắn T-052 (`docs/team/reports/T-052-la-chan.md:145`, LC-T052-4) còn có "không đặt thư mục app (chứa `data/`) trong Drive hay trong thư mục ảnh"; ghi chú trong phiếu bỏ sót. Đã thêm (README dòng 213).
3. **`A.I.` không dùng làm tên thư mục được.** `A.I.` có trong danh sách dấu hiệu (`tags.py:300`), nhưng tên thư mục kết thúc bằng dấu chấm bị lớp đọc thư mục từ chối (`folders.py:11`; chạy thử ra `ImageFolderError`). README không nêu `A.I.`.
4. **Thẻ sửa tay và nút viết alt chưa có trên giao diện** (chờ T-056). Phiếu viết như đã có; README nói "khi có màn hình chọn ảnh" / "Giao diện chưa có nút viết alt", để không hứa trước.

## Thêm ngoài phiếu (cùng chủ đề, đã kiểm code)

- **Đừng đổi thứ tự thư mục trong `IMAGE_FOLDERS`** (README dòng 212): khóa của thẻ sửa tay là (số thứ tự thư mục gốc, đường dẫn tương đối) (`image_tags.py:90-94`), số thứ tự là vị trí trong dòng `IMAGE_FOLDERS` (`folders.py:508`). Đổi thứ tự thì thẻ sửa tay không khớp đúng ảnh.
- **Tách phần bằng ` - ` để tên khách không kéo mất thẻ** (README dòng 232): đã chạy thử, `CT012 Cổng inox nhà anh Tuấn - Tân Phú` mất mã và hạng mục.

## Đối chiếu tiêu chí xong

- [x] Yêu cầu 1: đoạn `[tasks.alt]` ở mục 7.2 (README dòng 139–142)
- [x] Yêu cầu 2: mục 8 "Đặt thư mục ảnh" (README dòng 198–263), đủ các ý trong ghi chú của Chỉ Huy (T-052, T-070, T-074)
- [x] Yêu cầu 3: tiếng Việt, ngắn, không khóa, không đường dẫn máy thật
- [x] `uv run pytest tests/test_app_pages.py` 18 qua; không có `tests/test_readme*.py`; `uv run ruff check .` sạch
- [x] Báo cáo tại `docs/team/reports/T-069-thu-ky.md`

## Rủi ro và điểm cần chú ý

- Chữ `ai` tiếng Việt (nghĩa "ai, người nào") không có dấu nên cũng thành dấu hiệu ảnh AI (`Nhà ai` → ảnh AI, đã chạy thử). Hiếm gặp trong tên thư mục; README đã liệt kê `ai` trong danh sách.
- Phần Mac: chỉ có ví dụ đường dẫn USB lấy từ `.env.example`; chưa thử trên Mac (chủ dự án chưa có máy Mac). Không thêm hướng dẫn riêng cho Google Drive trên Mac.
- Danh sách tên công cụ trong README chép tay từ `tags.py`; khi phiếu sau thêm/bớt tên trong `_AI_TOOLS` thì phải sửa README theo.
- Khi T-056 gộp: soát lại các chỗ "chưa có" ở README dòng 139, 200, 256 và dòng 240 (nếu T-056 làm điều kiện 2(c) của Lá Chắn T-052: gốc có tên ảnh AI thì mọi ảnh trong đó là ảnh AI, thì bỏ lời dặn "đừng khai báo riêng thư mục ảnh AI").

## Đề xuất

- **T-056 (Họa Sĩ/Thợ Máy):** khi gộp, báo Thư Ký sửa các chỗ "chưa có" nêu trên; nếu giao diện hiện câu lỗi thẻ ảnh khác (ví dụ "File lưu thẻ ảnh đang bận…") thì thêm vào bảng lỗi mục 8.
- **Cài đặt → 🖼️ Ảnh (sau T-056):** có thể cảnh báo khi người dùng đổi thứ tự `IMAGE_FOLDERS` hay khai báo thư mục có tên ảnh AI làm gốc; hiện chỉ có lời dặn trong README.

## Câu hỏi cho chủ dự án

Không có.

# Báo cáo T-089 (phần README) · Viết lại «Lời dặn tạm thời» sau T-089

| Mục | Nội dung |
|---|---|
| Agent | Thư Ký (`thu-ky`) · model: Claude Opus 5.5 |
| Phiếu | [T-089](../tickets/T-089-gui-nhap-loi-thap-sau-t086.md), việc Thư Ký theo điều kiện của biên bản Lá Chắn T-089 (mục «Xem lại lượt 4», việc theo sau số 2) |
| Ngày nộp | 2026-10-27 |
| Nhánh | `team/T-089-readme` (từ `main` `641a837`) |
| Kết quả | Hoàn thành |

## Tóm tắt (cho chủ dự án)

README mục 10 «Gửi bài nháp lên WordPress» không còn khối «Lời dặn tạm thời». Lý do: mở cùng một bài ở hai tab rồi bấm gửi ở cả hai nay chỉ ra một bài nháp; tab bấm sau báo rõ và khóa nút. Mục 10 thêm hai ý vào phần «App nhớ việc đã gửi»: chuyện hai tab, và trường hợp đã tick xác nhận mà lần gửi hỏng trước khi tạo được bài thì bài vẫn khóa như cũ. «Lần gửi thật đầu tiên» thành một khối riêng, giữ nguyên: một bài, một ảnh, một tab, tải ảnh về kiểm GPS. Mục 9 «Chọn ảnh cho bài» thêm một đoạn về «dấu vân tay» ảnh lúc duyệt:
- mở lại bài mà ảnh đã bị thay thì app bỏ «Đã duyệt»;
- bài lưu bằng bản app cũ phải tick «Đã duyệt» lại một lần.

## Đã thay đổi

| Chỗ | Câu cũ | Câu mới |
|---|---|---|
| `README.md:287` (mục 9, đoạn mới) | (chưa có) | «Lúc bạn tick **Đã duyệt**, app nhớ «dấu vân tay» của đúng bản ảnh đang hiện (lưu trong nháp trên máy, không gửi đi đâu). Mở lại bài mà file ảnh đã bị thay bằng ảnh khác cùng tên thì ở khung ảnh app bỏ **Đã duyệt** («Ảnh này khác bản bạn đã duyệt trước đó…»), bắt xem lại ảnh, alt, chú thích rồi duyệt lại; bấm gửi thẳng ở bước Xuất bản thì app dừng, chưa gửi gì. Bài soạn dở lưu bằng bản app cũ (trước khi app có dấu vân tay này) thì các ảnh đã duyệt phải tick **Đã duyệt** lại một lần; app báo «… nháp không có «dấu vân tay» của ảnh lúc duyệt …».» |
| `README.md:312` | «(xem «App nhớ việc đã gửi» và lời dặn ở cuối mục này)» | «(xem «App nhớ việc đã gửi» bên dưới)» |
| `README.md:333` | «… Kiểm **Bài viết → Nháp** và **Media → Thư viện** trước khi tick.» | thêm «; đang gửi ở tab khác thì đợi tab đó xong rồi hãy xem.» |
| `README.md:335` (ý mới trong «App nhớ việc đã gửi») | (thay lời dặn «**Đừng mở cùng một bài ở hai tab (hay hai cửa sổ) rồi bấm 📤 Gửi nháp ở cả hai.** Bấm cách nhau vài giây thì vẫn có thể ra **hai bài nháp**… Mỗi lần gửi chỉ dùng một tab.») | «**Cùng một bài mở ở hai tab (hay hai cửa sổ), bấm 📤 Gửi nháp ở cả hai:** chỉ ra **một** bài nháp. Tab bấm sau không gửi gì, báo «Chưa gửi gì lên website: trạng thái gửi của bài này vừa thay đổi (thường do bài vừa được gửi, hoặc đang gửi, ở một tab khác của app)…», và nút gửi khóa theo lời nhắc phía trên nút.» |
| `README.md:336` (ý mới) | (chưa có) | «**Đã tick xác nhận rồi gửi, mà lần gửi đó hỏng trước khi tạo được bài** (ví dụ mất mạng lúc tải ảnh): bài giữ nguyên khóa như trước lúc gửi (vẫn «chưa có kết quả», hay vẫn «đã gửi» bài cũ). Muốn gửi tiếp thì kiểm trang quản trị rồi tick lại.» |
| `README.md:338-344` | Khối «**Lời dặn tạm thời** (tới khi app chặn được việc gửi cùng một bài từ hai tab)», ý «**Lần gửi thật đầu tiên**: thử **một bài, một ảnh, một tab**, …» | Khối riêng «**Lần gửi thật đầu tiên**»: cùng nội dung (một bài, một ảnh, một tab; ảnh có GPS chụp ở nơi đã công khai; 3 bước tải ảnh về, kiểm GPS, xóa bài thử). Không còn chữ «tạm thời» |

Ý 3 của tin giao việc (dấu vân tay ảnh) đặt ở mục 9, ngay sau câu «mở lại bài, app kiểm lại ảnh trên máy…», vì đó là chỗ README nói về «Đã duyệt». Phần «gửi thẳng thì app dừng» ở mục 10 đã có sẵn trong ý «Lỗi trước khi gửi (ảnh vừa đổi hay bị thay bằng ảnh khác cùng tên…)».

## Đối chiếu với code

`app/views/write.py` của `origin/team/T-089` (`d0a34d5`, có lượt 4). Mọi câu README trích đều có trong code: kiểm bằng `grep -F` và đọc giá trị hằng nhiều dòng bằng `ast`.

| Câu README | Code |
|---|---|
| Dấu vân tay gắn với bản ảnh đang hiện lúc duyệt, lưu trong nháp | `alt_editor` `:1221-1242` (`altsha-<id>` = băm của `web_info`), `slot_texts` `:760` (`approved_sha256` vào nháp) |
| Mở lại bài, ảnh bị thay: ở khung ảnh bỏ «Đã duyệt», câu «Ảnh này khác bản bạn đã duyệt trước đó…» | `:1221-1238`, `MSG_APPROVED_OTHER_VERSION` `:178-181` |
| Gửi thẳng ở Xuất bản: dừng, chưa gửi gì | `send_draft` so băm `:2112` (câu `MSG_FILE_REPLACED`, «Chưa gửi gì lên website.») |
| Nháp cũ không có băm: bỏ «Đã duyệt», câu «… nháp không có «dấu vân tay» của ảnh lúc duyệt …» | `restore_images` `:490-495`, `MSG_OLD_APPROVAL` `:182-186` |
| Hai tab: chỉ một bài; tab sau «Chưa gửi gì lên website: trạng thái gửi của bài này vừa thay đổi…», khóa theo lời nhắc | `send_and_record` ghi «đang gửi» so rồi đặt (`:2199`, `expected=seen`), không ghi được thì không gửi (`:2211-2214`, `MSG_SENT_ELSEWHERE` `:190-194`); `draft_panel` đọc trạng thái trong nháp mỗi lần vẽ (`:2488`) nên khóa «chưa có kết quả» hay «đã gửi» của tab kia |
| Tick xác nhận rồi gửi, hỏng trước khi tạo bài: giữ khóa như trước (vẫn «chưa có kết quả» hay «đã gửi» bài cũ), phải tick lại | `record_outcome`: `nothing_created` trả nháp về đúng trạng thái `replaced` (`:2273-2279`, LC-T089-1 lượt 4); ô xác nhận bị bỏ tick trước mỗi lần gửi (`:2544`) |
| «Lần gửi thật đầu tiên»: một bài, một ảnh, một tab | Tin giao việc của Chỉ Huy B (T-059), biên bản Lá Chắn T-089 «Xem lại lượt 4», việc theo sau số 2 |

## Kiểm tra

```
$ PYTHONUTF8=1 uvx detect-secrets scan README.md docs/team/reports/T-089-thu-ky.md
results: {}   (0 mục; thử mồi trên bản sao README ngoài repo vẫn bắt được khóa giả)

$ uv run ruff check .
All checks passed!
```

Không chạy pytest: chỉ đổi `README.md` và báo cáo, không có test đọc README.

## Rủi ro và điểm cần chú ý

- README viết theo code `origin/team/T-089` (có lượt 4: LC-T089-1). `main` `641a837` mới có lượt 1–3. Ý «hỏng trước khi tạo được bài thì bài giữ nguyên khóa» chỉ đúng khi lượt 4 đã gộp. Nên gộp nhánh này cùng lúc hoặc sau T-089 lượt 4.
- Câu «tab bấm sau» theo cách nói của biên bản Lá Chắn. Chính xác hơn là tab ghi «đang gửi» sau (kiểm lại, nén ảnh lâu hơn). Với người dùng, hai cách nói như nhau.

## Câu hỏi cho chủ dự án

Không có.

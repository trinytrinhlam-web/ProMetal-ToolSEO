# Biên bản bảo mật T-069 · README: ảnh gửi hãng AI khi viết alt, cách đặt thư mục ảnh

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem dòng trên) |
| Phiếu được kiểm | [T-069](../tickets/T-069-readme-anh-gui-ai.md) · kiểm **rút gọn** (phiếu tài liệu) |
| Phạm vi | diff `fa2cc39..b8489fa` (1 commit): `README.md` (mục 7.2 thêm đoạn `[tasks.alt]`, dòng 139–142; mục mới **8. Đặt thư mục ảnh**, dòng 198–263; mục cũ 8, 9 đổi số thành 9, 10), báo cáo Thư Ký. Không file code, cấu hình, test nào đổi. `main` lúc kiểm: `8fc7dd3` |
| Báo cáo đã đọc | [Thư Ký](T-069-thu-ky.md); điều kiện chép vào phiếu từ [Lá Chắn T-050](T-050-la-chan.md) (LC-T050-4), [T-052](T-052-la-chan.md) (điều kiện 4), [T-062](T-062-la-chan.md) (điều kiện 3), [T-070](T-070-la-chan.md) (điều kiện 3), [T-074](T-074-la-chan.md) (điều kiện 3); gợi ý cho T-069 ở [Lá Chắn T-077](T-077-la-chan.md) |
| Ngày | 2026-10-22 (13:50 → 14:23 +07, giờ máy) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 2 Thấp (LC-T069-1, LC-T069-2). Gộp vào `main` được ngay |

## Tóm tắt (cho chủ dự án)

Phần README mới **an toàn để gộp**. Mọi điều kiện bảo mật đã giao cho phiếu này đều có trong README, và README nói đúng điều phần mềm làm: tôi chạy lại các ví dụ tên thư mục trên code thật, kết quả khớp hết. README nói rõ việc viết alt gửi ảnh công trình cho hãng AI. Ảnh gửi đi đã bỏ GPS, không kèm tên file. Hãng AI vẫn thấy mọi thứ trong ảnh, vì vậy README khuyên dùng Claude hoặc khóa trả phí. Khóa Gemini miễn phí cho Google dùng ảnh, và người duyệt của Google có thể xem ảnh. Không có khóa, đường dẫn máy thật hay thông tin khách thật.

Có 2 chỗ nên viết rõ hơn, đều mức Thấp:

1. Lời dặn "đừng để thư mục phần mềm trong Google Drive" mới nêu lý do là thư mục `data/`. README chưa nói lý do quan trọng hơn: file `.env` chứa khóa AI và mật khẩu WordPress cũng nằm ở đó.
2. Ảnh mà bạn **đánh dấu tay** là ảnh AI sẽ lại thành "ảnh thật" khi xóa file thẻ, khi đổi thứ tự thư mục ảnh, hoặc khi mở trên máy kia. Nên dặn: muốn đánh dấu ảnh AI thì để ảnh trong thư mục có chữ "AI".

Màn hình chọn ảnh chưa có, nên cả hai chưa gây hại được. Thư Ký sửa 2 câu này trước khi gộp T-056.

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T069-1 | Thấp | Lời dặn không để thư mục phần mềm trong Google Drive chỉ nêu lý do `data/`, không nhắc `.env` (khóa AI, Application Password WordPress, mã băm mật khẩu app) cũng nằm trong thư mục đó | `README.md:213` | Chủ dự án dùng 2 máy, cả 2 có Google Drive for Desktop. Đọc dòng 213 thấy lý do chỉ là "file riêng trong `data/`", nghĩ đó là bộ nhớ đệm nên đặt cả thư mục phần mềm vào Drive cho tiện đồng bộ. Khi đó `.env` lên Google Drive: ai mở được thư mục Drive đó, hay chiếm được tài khoản Google, đều lấy được khóa và mật khẩu sửa bài trên site thật (`security.md` mục 2.1: bí mật chỉ nằm trong `.env` trên máy). Lời dặn hiện tại vẫn đúng ("Đừng để…"), chỉ thiếu lý do mạnh nhất, nên xếp Thấp | Thay dòng 213 bằng: «Đừng để thư mục phần mềm (thư mục có `run.bat`) nằm trong Google Drive, OneDrive (hay thư mục nào tự đồng bộ lên mạng) hoặc trong thư mục ảnh. Trong đó có file `.env` (khóa AI, mật khẩu WordPress) và thư mục `data/` (bài đang soạn, thẻ ảnh): để vậy thì các file này lên mạng hoặc lẫn vào thư mục ảnh.» Lý do nhắc OneDrive: Windows hay tự đồng bộ thư mục Documents lên OneDrive, và GitHub Desktop mặc định tải dự án vào Documents |
| LC-T069-2 | Thấp | README nói xóa `data/image_tags.sqlite` thì "chỉ mất các thẻ sửa tay", và thẻ sửa tay "máy kia không thấy". README không nói rằng trong thẻ sửa tay có cả **dấu "ảnh AI"** người dùng tự gắn (điều kiện 2(b) Lá Chắn T-052 cho T-056). Mất dấu này thì ảnh AI quay về "ảnh thật" | `README.md:212`, `:256`, `:263`; code `seo_app/storage/image_tags.py:1-6`, khóa theo số thứ tự gốc `:8-10` | Sau khi T-056 gộp: một ảnh AI nằm lẫn trong `CT012 - Cổng inox - Tân Phú/sau/`, chủ dự án bấm đổi sang ảnh AI (dấu chỉ lưu trong `data/image_tags.sqlite`). Sau đó: (a) app báo mãi lỗi, chủ dự án làm theo dòng 263 xóa file; hoặc (b) mở trên máy kia; hoặc (c) đổi thứ tự `IMAGE_FOLDERS`. Ảnh lại mang `CT012`, Tân Phú, "sau", source "thật". Đã thử đường (a), xem mục «Đã chạy thử». (b) và (c) cùng cơ chế: kho thẻ trên máy đó không có dòng cho ảnh này, vì khóa là số thứ tự gốc cộng đường dẫn. Viết alt thì `ai_generated=False`: alt không có «Minh họa», tả như công trình thật; nếu không để ý ô "Ảnh thật / Ảnh AI" thì ảnh AI lên site như công trình thật. Được che một phần: README dòng 239 đã dặn để ảnh AI trong thư mục có chữ AI, và T-056 phải hiện "Ảnh thật / Ảnh AI" trước khi viết alt. Hiện chưa có màn hình đánh dấu tay nên chưa khai thác được | Thêm vào dòng 256 (hoặc ngay sau dòng 257): «Ảnh AI thì đánh dấu bằng tên thư mục (để ảnh vào thư mục có chữ AI). Đánh dấu "ảnh AI" bằng tay chỉ nhớ trên máy này: xóa file `data/image_tags.sqlite`, đổi thứ tự `IMAGE_FOLDERS`, hay mở trên máy kia thì ảnh lại thành ảnh thật.» Ở dòng 263, đổi "chỉ mất các thẻ sửa tay" thành «chỉ mất các thẻ sửa tay (kể cả dấu "ảnh AI" gắn tay: kiểm lại các ảnh đó)» |

## Đối chiếu điều kiện bảo mật đã chép vào phiếu

| Điều kiện | Yêu cầu | Kết quả | Bằng chứng trong README / code |
|---|---|---|---|
| **LC-T050-4** (Lá Chắn T-050) / **điều kiện 3 Lá Chắn T-062** | Việc alt gửi ảnh công trình (đã bỏ GPS, EXIF) cho hãng AI ghi ở `[tasks.alt]`; nên dùng Claude hoặc khóa **trả phí** OpenAI / Gemini; khóa Gemini **miễn phí** cho Google dùng ảnh cải tiến sản phẩm, người duyệt xem được; muốn dùng khóa miễn phí thì báo Chỉ Huy ghi sổ rủi ro | **Đạt** | `README.md:139-142`, sát câu Thợ Máy đề xuất (`T-062-tho-may.md:109`). Đúng với điều khoản Gemini API Lá Chắn T-050 đã đọc (`T-050-la-chan.md:67-71`). Ghi thêm, đúng: hãng AI vẫn thấy mọi thứ **trong** ảnh (nhà khách, số nhà, người); giao diện chưa có nút viết alt (`grep suggest_alt app/`: 0). Code không biết khóa thuộc gói nào, nên README là lớp chặn duy nhất (như T-050 đã nêu) |
| **Điều kiện 4 Lá Chắn T-052** | (a) ảnh AI trong thư mục con có chữ AI **bên dưới** thư mục đã khai báo; (b) chưa khai báo thư mục ảnh AI làm một mục `IMAGE_FOLDERS` cho tới T-056; (c) thư mục ảnh thật không có chữ AI đứng riêng hay tên công cụ; (d) không đặt thư mục app (chứa `data/`) trong Drive hay thư mục ảnh (LC-T052-4); (e) thẻ sửa tay chỉ nhớ trên máy đang dùng | **Đạt** (d kèm LC-T069-1) | (a) `:239`, sơ đồ `:219-226`; (b) `:240`, đúng code: gốc không được đọc (`tags.py:32-35`, `tags_for_image` `:942-953`), `is_ai_name` chưa có nơi gọi trong `app/`; (c) `:249`; (d) `:213` (ghi chú phiếu bỏ sót ý này, Thư Ký tự thêm theo `T-052-la-chan.md:145`); (e) `:256` |
| **Điều kiện 3 Lá Chắn T-070** | Liệt kê các chữ làm ảnh thành ảnh AI; gõ tên thư mục ảnh thật **có dấu**; tránh tên công cụ đứng riêng (Sora, Flux, Designer, Canva, Bing…); không để ảnh từ mạng hay ảnh tham khảo trong thư mục ảnh | **Đạt** | `:241-244` (31 tên công cụ, đủ `_AI_TOOLS` `tags.py:206-250`, chỉ bỏ dạng viết khác `DALLE` và các dạng gõ tách, nêu riêng ở `:245`; đủ cụm `_AI_PHRASES` `:269-280` trừ cách đặt dấu kiểu cũ «minh hoạ»; `GenAI`, `AI images` từ `_AI_JOINED`. Các dấu hiệu không liệt kê, như `AIgen`, `OIG…`, chỉ làm thêm ảnh thành ảnh AI, là hướng an toàn); `:250` (có dấu); `:249` (tên công cụ đứng riêng, kèm ví dụ mất thẻ); `:251` (ảnh từ mạng, ảnh tham khảo, "app không phân biệt được") |
| **Điều kiện 3 Lá Chắn T-074** | Gõ tên công cụ liền chuẩn (Midjourney, Firefly, Copilot, Seedream); báo mãi "Không mở được file lưu thẻ ảnh…" thì đóng chương trình khác hoặc xóa `data/image_tags.sqlite` (chỉ mất thẻ sửa tay) | **Đạt** (kèm LC-T069-2) | `:245`, nói đúng phần T-077 đã sửa: app nhận `Mid Journey`, `Co-Pilot` nhưng không phải mọi kiểu (`Hai Luo`, `Leo nardo` chạy thử ra ảnh thật). `:263`: câu báo chép đúng nguyên văn `_db_message` (`image_tags.py:697-698`), cách xử lý đúng thứ tự (đóng chương trình khác trước, tắt app rồi mới xóa) |
| Gợi ý Lá Chắn T-077 (nên, không bắt buộc) | Để chữ "AI" trong tên thư mục ảnh AI ("Ảnh AI - Runway"); tên ảnh thật gần giống "ảnh AI" thì viết có dấu hay tách chữ ("An Hải", không "AnHai") | **Có** | `:239` (thư mục có chữ AI); `:250` (có dấu). Chạy thử: `AnHai` ra ảnh AI, mất mã; `An Hải`, `An Hai` giữ `CT012`, nên dặn "có dấu" là đủ |
| Ghi chú Chỉ Huy 2026-10-22 | Không hứa điều chưa kiểm trên Mac | **Đạt** | Phần Mac chỉ có một ví dụ dạng đường dẫn (`:208`), lấy từ `.env.example:50`; không nói gì về cách chạy trên Mac |

## README không hứa điều code không làm

| Câu README | Code | Kết quả |
|---|---|---|
| `:139` "đang ghi Claude Sonnet" | `config/ai.toml:71-77` (`anthropic`, `claude-sonnet-5-5`) | Đúng |
| `:139` ảnh gửi đi đã bỏ GPS, EXIF, không kèm tên file, đường dẫn | `suggest_alt` chỉ nhận `ImageInput` (bytes + MIME), luôn qua `prepare_images` (`alt.py:474`, kiểm theo danh sách cho phép ở `seo_app/ai/base.py:492`), bản gửi AI dựng lại từ điểm ảnh (`process.py:821`) | Đúng |
| `:139` chữ gửi kèm chỉ gồm quy tắc `[alt]`, từ khóa, hạng mục / khu vực / trước-sau | `alt_prompt` (`alt.py:269-303`), `ImageTags.reference` (`tags.py:726-736`, không gửi mã công trình, ảnh AI không gửi thẻ). Ngoài ra chỉ còn lời dặn cố định của code (`ALT_SYSTEM`), không phải dữ liệu của người dùng | Đúng |
| `:232` phần tên không khớp danh sách (tên khách, số điện thoại, địa chỉ, năm) bị bỏ và "không gửi đi đâu" | Module không trả lại chữ của tên thư mục (`tags.py:24-27`); chạy thử 4 tên có «Nhà anh Tuấn», số điện thoại, «12 Lê Lợi», năm: thẻ và prompt alt không có chữ nào trong số đó. Đường dẫn tương đối chỉ nằm trong file trên máy (`data/`), tên file ảnh gửi WordPress dựng từ thẻ và alt (`naming.py:57-73`) | Đúng |
| `:239`, `:257` ảnh AI không mang mã, khu vực, trước/sau; sửa tay không đổi thành ảnh thật | `ImageTags` từ chối (`tags.py:673-674`); `_keep_ai` (`image_tags.py:198-202`) | Đúng |
| `:255` app chỉ đọc, không ghi vào thư mục ảnh hay Drive | `folders.py:25`; `process.py` xử lý trong bộ nhớ (`io.BytesIO`), không lệnh ghi nào trong `folders.py`, `process.py`, `naming.py`, `tags.py`; kho thẻ chỉ ghi `data/image_tags.sqlite` (`image_tags.py:59`) | Đúng |
| `:209` Cài đặt → 🖼️ Ảnh hiện "✅ tìm thấy" / "⚠️ không thấy trên máy này" | `app/views/settings.py:474-479` | Đúng |
| `:263` xóa file thì "chỉ mất các thẻ sửa tay" | `image_tags.py:5-6`; chạy thử (mục dưới) | Đúng về dữ liệu; thiếu ý dấu "ảnh AI" (LC-T069-2) |

**Không hướng dẫn điều gì làm giảm an toàn:** không bảo tắt kiểm tra nào, không bảo để khóa ngoài `.env` hay gửi `.env` đi, không bảo chia sẻ hay đồng bộ `data/`. Để hai máy thấy cùng thẻ, README bảo đổi tên thư mục trên Drive (`:256`), không bảo chép `data/`. Ngược lại, `:213` dặn **không** để thư mục phần mềm trong Drive (LC-T069-1 chỉ đề nghị nêu thêm lý do).

## Đã chạy thử

Script tạm ngoài repo (`lc_t069_check.py`, `lc_t069_delete.py` trong scratchpad, không commit), chạy bằng `uv run --frozen python` trên nhánh, Windows:

- **Ví dụ README mục 8, 75 phép kiểm, 0 hỏng.** Ví dụ chính ra đủ `CT012`, Cổng inox, Tân Phú, trước. 23 tên thư mục và tên file ảnh AI ở `:239-245` (`Ảnh AI`, `Hình AI`, `ai`, `IMG_AI_01.jpg`, `Gemini_Generated_Image_….png`, `Designer (3).png`, `Ảnh AI - Runway`, `Mid Journey`, `Co-Pilot`, các cụm tiếng Việt…) đều là ảnh AI, không mã, khu vực, trước/sau; trong thư mục công trình thì giữ hạng mục. Đủ **31/31** tên công cụ README liệt kê đều nhận. `Nhà chị Ái`, `Nhà anh Minh Hòa` là ảnh thật; `Nha chi Ai`, `Nha anh Minh Hoa`, `Thuốc hàn Flux`, `Công ty Designer Home` là ảnh AI, mất mã. `Hai Luo`, `Leo nardo` ra ảnh thật, đúng như README cảnh báo. Gốc không được đọc: ảnh để thẳng trong gốc ra ảnh thật, `is_ai_name("G:/My Drive/Ảnh AI")` ra đúng, khớp `:240`. Hai khu vực thì để trống; `CT014 - Cua keo - q7/truoc` ra đủ thẻ.
- **Làm đúng lời dòng 263 khi còn sót file nhật ký.** Tạo kho thẻ có một dấu "ảnh AI" gắn tay, chép file kho cùng `-wal` (chế độ WAL) hoặc `-journal` (giao dịch đang mở) sang thư mục tạm, xóa **chỉ** `image_tags.sqlite` như README dặn, mở lại kho 3 lần. Cả hai trường hợp: mở được, không báo lỗi, không đổi tên file hỏng, bảng thẻ sửa tay rỗng, file nhật ký cũ không được "khôi phục" vào file mới. Ảnh lại mang thẻ thư mục (`CT012`, Tân Phú, sau, ảnh thật): đây là đường đi của LC-T069-2. Với `-wal`, file nhật ký cũ vẫn nằm lại cạnh file mới nhưng không gây hại qua 3 lần mở; không cần dặn thêm người dùng xóa nó.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` (có `PYTHONUTF8=1`) trên `README.md` và báo cáo Thư Ký: `"results": {}`. Soát commit `b8489fa`: không khóa, không mật khẩu. Ví dụ đường dẫn (`E:/anh-cong-trinh`, `G:/My Drive/Anh SEO`, `/Volumes/USB/anh-cong-trinh`, `G:/My Drive/Ảnh AI`) là dạng chung, lấy từ `.env.example`; không tên tài khoản máy, không `D:/ProMetal…`. Tên người, công ty trong ví dụ («anh Tuấn», «chị Ái», «Minh Hòa», «Designer Home») là tên bịa thông dụng, không có số nhà, số điện thoại, email |
| S2 | Không áp dụng | Không đụng code in lỗi; câu lỗi trong README chép nguyên văn từ code, không có đường dẫn |
| S3 | Không áp dụng | Không có biến cấu hình mới; `.env.example` không đổi. `IMAGE_FOLDERS` đã có (`.env.example:47-51`) |
| W1 | Không áp dụng | Tài liệu, không đường `publish` / `future` |
| W2 | Không áp dụng | Như W1 |
| W3 | Không áp dụng | Như W1 |
| W4 | Không áp dụng | Không client HTTP |
| A1 | Không áp dụng | Không đổi prompt. Mô tả của README về chữ gửi AI đúng với `alt_prompt` (bảng trên) |
| A2 | Không áp dụng | Không đổi code AI |
| A3 | Đạt | Mục đích chính của phiếu: README cho chủ dự án biết ảnh công trình tới hãng AI, hãng thấy gì, gói nào cho dùng lại ảnh (LC-T050-4); dặn tách phần tên khách bằng ` - ` để không mất thẻ, phần đó không đi đâu (`:232`, đã chạy thử) |
| U1 | Không áp dụng | Không đụng giao diện |
| U2 | Không áp dụng | Như U1 |
| U3 | Không áp dụng | Như U1 |
| F1 | Đạt | README không bảo đặt symlink, junction hay thư mục lạ; dặn khai báo thư mục **chứa** công trình (`:211`), không để thư mục phần mềm trong thư mục ảnh (`:213`) |
| F2 | Không áp dụng | Không đụng xử lý ảnh. Lưu ý: "bỏ GPS" ở `:139` nói về **bản gửi AI**, không mâu thuẫn quyết định giữ GPS cho ảnh đăng web (`security.md` mục 6), vì đoạn này chỉ nói về việc viết alt |
| F3 | Không áp dụng | Không đọc/ghi file mới |
| D1 | Đạt | `uv.lock`, `pyproject.toml` không đổi |
| D2 | Đạt | `.gitignore` không đổi; README dặn `data/` không lên Drive (`data/` đã có trong `.gitignore`) |
| D3 | Không áp dụng | Không test mới |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | **Không chạy (không áp dụng):** `uv.lock`, `pyproject.toml` không đổi | — |
| bandit | **Không chạy (không áp dụng):** không file Python nào đổi (`git diff --name-only fa2cc39..HEAD -- seo_app app scripts config tests uv.lock pyproject.toml .gitignore .env.example .streamlit .claude run.bat run.command`: 0 file) | — |
| detect-secrets | `PYTHONUTF8=1 uvx detect-secrets scan README.md docs/team/reports/T-069-thu-ky.md`: `"results": {}`. **Thử chuỗi mồi:** bản sao README (có chữ tiếng Việt) ngoài repo, thêm một dòng ghi chú tiếng Việt và một khóa AWS giả (khóa mẫu trong tài liệu của AWS): có `PYTHONUTF8=1` thì bắt được («AWS Access Key», dòng 312); đặt `PYTHONUTF8=0` thì `"results": {}`. Đã xóa bản mồi | Có |
| Soát lịch sử git | `git log -p fa2cc39..HEAD` lọc `api_key\|password\|secret\|token\|sk-…\|AIza\|AKIA\|PRIVATE KEY\|ghp_`: chỉ `max_tokens` (dòng ngữ cảnh của README) và các dòng lệnh quét trong báo cáo Thư Ký. Lọc dòng thêm theo `Users/`, `C:/`, `D:/`, `ADMIN`, `ProMetal-ToolSEO`, email, số điện thoại: chỉ dòng lệnh grep trong báo cáo Thư Ký | Có |
| pytest | Không có test đọc README (`tests/test_readme*.py` không có). Chạy 11 file test làm chứng cho các câu README (thẻ thư mục, kho thẻ sửa tay, ảnh gửi AI, xử lý ảnh): `test_images_tags`, `test_soi_loi_t052`, `test_soi_loi_t070`, `test_soi_loi_t074`, `test_soi_loi_t077`, `test_la_chan_t074`, `test_ai_images`, `test_images_process`, `test_soi_loi_t049`, `test_soi_loi_t050`, `test_t062_image_config`. `uv run --frozen pytest -q -p no:cacheprovider …` trên `b8489fa`, Windows, 14:00 → 14:21 (máy đang chạy song song agent khác): **1786 passed, 2 skipped, 22 xfailed**, 0 hỏng. Phiếu không đổi code hay test, nên kết quả này giống `main` | Có |
| ruff | `uv run ruff check .`: **All checks passed!** | Có |
| Thử gộp | `git merge-tree --write-tree origin/main HEAD` (`main` `8fc7dd3`): cây `923621f`, **không xung đột**. Từ gốc `fa2cc39`, `main` chỉ đổi `CLAUDE.md` (+1 dòng), `docs/team/board.md`, `docs/team/dong-bo.md`; không đụng `README.md` hay code | Có |
| Số mục README | Đổi số mục 8, 9 thành 9, 10. `git grep` tìm chỗ trỏ tới số mục README: không có; `run.bat:19`, `run.command:21` và các báo cáo trỏ theo **tên** mục «Xử lý sự cố», vẫn đúng | Có |

## Báo nhầm đã loại

- **`max_tokens`** (soát lịch sử): dòng ngữ cảnh `@@ … max_tokens = 32000` của README, là tên khóa cấu hình, không phải bí mật.
- **Dòng lệnh `detect-secrets`, `grep … api[_-]?key|password|secret|token|Users/|ADMIN…`** trong báo cáo Thư Ký: là lệnh quét, không chứa giá trị.

## Ghi nhận khác (không phải lỗi)

- **Gói miễn phí hay trả phí của Gemini:** README mục 7.1 (`:109`) đã nói Gemini "thường có bậc miễn phí…; muốn dùng nhiều thì bật thanh toán". Khi Thư Ký sửa LC-T069-1, -2 có thể thêm vào `:142` vài chữ cho dễ tự nhận ra: «(khóa của dự án Google chưa bật thanh toán)». Không bắt buộc.
- **Danh sách chữ nhận ảnh AI chép tay từ `tags.py`.** Thư Ký đã ghi rủi ro này. Phiếu sau thêm hay bớt tên trong `_AI_TOOLS`, `_AI_PHRASES` thì phải sửa `README.md:242-245` theo. Chỉ Huy nên chép một dòng nhắc vào phiếu nào đụng các danh sách đó.
- **Chữ "ai" tiếng Việt** (`Nhà ai`) cũng thành ảnh AI. Đây là hướng an toàn (ảnh chỉ mất thẻ). README đã liệt kê `ai` ở `:242`.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

Gộp T-069 vào `main` được ngay. Chỉ Huy chép điều kiện sau vào phiếu nhận:

1. **LC-T069-1 và LC-T069-2 (Thấp) → Thư Ký, sửa `README.md`. Hạn: gộp trước T-056, hoặc cùng lúc với T-056** (nút đánh dấu tay chỉ có từ T-056). Có thể làm chung lượt Thư Ký đã đề xuất để soát các chỗ "chưa có" ở `:139`, `:200`, `:240`, `:256`, miễn lượt đó không gộp sau T-056. Sửa sớm hơn trong một phiếu tài liệu nhỏ cũng được. Dùng câu đề xuất ở bảng lỗi. Lá Chắn kiểm rút gọn lại.
2. **T-056 (nhắc, không mới):** điều kiện 2(b) Lá Chắn T-052 (hiện "Ảnh thật / Ảnh AI" trước khi viết alt) và 3(j) Lá Chắn T-074 (lưu dấu AI lỗi thì trong phiên vẫn coi là ảnh AI) là lớp chặn chính cho đường đi của LC-T069-2; giữ nguyên.

Các điều kiện cũ đã giao cho T-069 (LC-T050-4 / điều kiện 3 T-062, điều kiện 4 T-052, điều kiện 3 T-070, điều kiện 3 T-074) **đóng** với phiếu này.

Chưa chạy: thử trên Mac (chủ dự án chưa có máy Mac; README không nói gì mới về Mac). Biên bản chạy tạm bằng Claude Opus 5.5; **kiểm lại bằng Claude Fable sau 01/11**.

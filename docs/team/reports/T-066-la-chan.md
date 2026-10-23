# Biên bản bảo mật T-066 · Dọn lỗi Thấp lớp ảnh gửi AI (sau T-050) · rút gọn

> **Model:** chạy tạm Claude Opus 5.5, cần kiểm lại bằng Claude Fable sau 01/11 (tài khoản chưa dùng được Fable; chủ dự án đã duyệt).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-066](../tickets/T-066-don-loi-thap-anh-gui-ai.md) |
| Phạm vi | Rút gọn (A3, theo phiếu). Diff `a9338f7..team/T-066` tại `f8e6d21`: code ứng dụng chỉ có `seo_app/ai/base.py` (+112/−114); test `tests/test_ai_images.py`, `tests/test_soi_loi_t050.py` (Thợ Máy), `tests/test_soi_loi_t066.py` (Soi Lỗi, mới); 2 báo cáo. Soát kỹ `base.py:443–790` (lớp kiểm JPEG/PNG/WebP) và đường gửi ảnh: `seo_app/images/alt.py:474`, 3 provider, `seo_app/images/process.py` (`make_ai_image`, `make_preview`, `jpeg_layout`). `origin/main` lúc kiểm `b38c590` (đã có T-079, T-039, T-069) |
| Ngày | 2026-10-23 (09:41–09:57 +07) |
| **Kết luận** | **ĐẠT**: 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp mới. **LC-T050-1, LC-T050-3 đóng; LC-T050-2 đóng phần sửa được** (phần còn lại là giới hạn vốn có, đề nghị ghi sổ rủi ro, không chặn); SL-T050-5, SL-T050-6 đóng. Gộp `main` được ngay |

## Tóm tắt (cho chủ dự án)

An toàn để gộp. Bộ kiểm cuối cùng trước khi ảnh rời máy tới hãng AI nay **từ chối mọi "hồ sơ màu"** (phần dữ liệu màu có thể mang tên, đời màn hình hay chữ tùy ý) và chặt hơn với các khối kỹ thuật bị lặp hay dài quá khuôn. Tôi tự thử lại: ảnh có hồ sơ màu ở cả 3 định dạng, kể cả hồ sơ giấu sau phần ảnh, đều bị chặn; 200.000 tệp bị sửa hỏng hay dựng cố ý không làm bộ kiểm lỏng hơn bản cũ ở tệp nào, không tệp nào lọt kèm thông tin mà thư viện ảnh đọc ra được, không lần nào gặp lỗi lạ. Bản ảnh mà chính phần mềm chuẩn bị để gửi AI (từ ảnh điện thoại có GPS, ghi chú, hồ sơ màu) vẫn qua đủ 320/320, không còn dấu vết nào của ảnh gốc.

Còn một giới hạn đã biết từ T-050: ảnh **cố tình dựng** vẫn giấu được dữ liệu trong chính phần ảnh. Không bộ kiểm nào chặn hết được việc này nếu không giải mã ảnh; bảo vệ thật là phần mềm luôn vẽ lại ảnh từ điểm ảnh trước khi gửi (T-049). Tôi đề nghị chủ dự án ghi giới hạn này vào sổ rủi ro (dòng mẫu ở dưới); việc này không chặn gộp. Hôm nay giao diện chưa thấy gì khác (màn hình chọn ảnh, viết alt là T-056).

## Lỗi phát hiện

Không phát hiện lỗi mới.

## Kiểm lại lỗi cũ và các mục phiếu giao

Số dòng theo `f8e6d21`.

| Mã / việc | Kết quả | Bằng chứng |
|---|---|---|
| Diff code chỉ ở `base.py` | **Đúng** | `git diff --stat a9338f7..team/T-066 -- seo_app/`: 1 file, `seo_app/ai/base.py`. `app/`, `config/`, `seo_app/images/**`, `uv.lock`, `pyproject.toml`, `.gitignore` không đổi |
| LC-T050-1 = SL-T050-5 · hồ sơ màu chở chữ | **Đóng** | Đúng cách (a) tôi chọn ở T-050: JPEG chỉ còn APP0, APP14 (`_JPEG_APP`, `base.py:580`), mọi APP2 rơi vào nhánh "ngoài danh sách" → metadata (`:636–637`); `iCCP` không còn trong `_PNG_ALLOWED` (`:681`); `ICCP` không còn trong `_WEBP_ALLOWED` (`:753`). Đã xóa `_icc_ok`, `_jpeg_icc_ok`, `_check_png_icc`, `import zlib` (`git grep` trên nhánh: 0 chỗ), nên lớp kiểm không còn giải nén gì. **Thử độc lập (A):** hồ sơ sRGB thật của LittleCMS trong JPEG, JPEG CMYK progressive, JPEG hồ sơ 150 KB chia 3 khối APP2, PNG RGB/RGBA, WebP có mất và không mất dữ liệu, APP2 đặt **sau** lượt quét, `iCCP` **sau** IDAT: bản `main` nhận 8/9, bản nhánh **9/9 "còn thông tin kèm theo"**. Soi Lỗi thử thêm 12 cách giấu hồ sơ màu ở khối khác loại: đều bị chặn |
| LC-T050-2 = SL-T050-6 · khối lặp, dài quá khuôn, DAC, SOF lạ | **Đóng phần sửa được** | APP0, APP14 tối đa một lần (`seen_app`, `:614`, `:633`); SOF0/1/2 đúng 6 + 3·N byte, SOS đúng 4 + 2·N, DRI/DNL đúng 2 byte (`_jpeg_decode_ok`, `:592–602`); bỏ DAC và SOF3, SOF5–15 (`_JPEG_DECODE`, `:570`); PNG: IHDR kiểm trường (`_png_ihdr_ok`, `:688–695`), `PLTE` chỉ ảnh bảng màu và ≤ 2^độ sâu màu (`:725–730`), `tRNS` đúng độ dài theo loại màu (`:731–736`), bỏ `cHRM`, `sBIT`, `bKGD`, `gAMA`/`sRGB`/`pHYs` đúng độ dài, không chunk nào sau IDAT (`:680`, `:716–719`). **Thử độc lập (C):** 17 kênh đã biết (APP0/APP14 lặp, DAC chở chữ, SOF3, SOF/SOS/DRI dài, PLTE ảnh RGB, tRNS dài, cHRM, bKGD, sBIT, gAMA sau IDAT, pHYs 8 byte, tRNS > số màu, WebP `ICCP`): bản `main` nhận 15, bản nhánh **chặn cả 17**. Phần còn lại (dữ liệu nén, DQT/DHT, CRC, trường cố định…) là giới hạn vốn có, xem mục "Quyết Ghi nhận 1" |
| LC-T050-3 · chú thích nói quá | **Đóng** | `base.py:551–560` theo đúng mẫu tôi đưa ở T-050: nói rõ "**Không** chống được ảnh dựng cố ý… lớp này chỉ là lưới cuối", bảo đảm thật là T-049. `:670–679` bỏ vế "không chứa chữ tự do"; câu "Pillow chỉ ghi các chunk này khi được yêu cầu (`dpi`, `pnginfo`)" đúng (Soi Lỗi đối chiếu mã Pillow 13). Docstring `prepare_images` (`:494–499`) "không giải nén gì": đúng. Chỉ còn câu chung `:553–554` hơi rộng (Ghi nhận 1, quyết ở dưới) |
| Gỡ 15 `xfail` SL-T050-5/-6, đổi ca hồ sơ màu | **Đúng** | `git diff a9338f7..team/T-066 -- tests/test_soi_loi_t050.py`: chỉ bỏ 2 hằng `SL5`, `SL6` và 2 dấu `@SL5`, `@SL6`; dữ liệu và `assert` của 15 ca không đổi. Các ca hồ sơ màu đổi theo thiết kế mới (Chỉ Huy B duyệt ở phiếu) vẫn khẳng định cả hai chiều: kèm hồ sơ màu → `IMAGE_METADATA_MESSAGE`; cùng ảnh không kèm → qua. Không test nào bị nới để cho qua |
| A3 · metadata ảnh gốc không tới hãng AI qua `prepare_images` | **Đạt** | Xem dòng A3 ở danh sách kiểm tra |
| Không chặn oan bản `make_ai_image` | **Đạt** | **Thử độc lập (D):** 160 ảnh gốc ngẫu nhiên (JPEG RGB/xám/CMYK, PNG RGB/RGBA/xám/LA/bảng màu/1 bit/16 bit, WebP, HEIC; 1–1500 px; 144 ảnh có hồ sơ màu sRGB, EXIF với GPS, hãng máy và tên khách, XMP, chú thích, chunk chữ; xoay 1–8; progressive, restart) → `make_ai_image` và `make_preview`: **320/320 bản qua**, không bản nào còn `ICC_PROFILE`, `acsp`, `Exif`, `xmpmeta`, `SAMSUNG`, `Le Loi`, `Tuan`. Mọi bản ra chỉ có đúng một kiểu khối trước lượt quét: `E0 DB C0 C4` (JFIF, DQT, SOF0, DHT), vì `make_ai_image` dựng ảnh mới từ điểm ảnh (`process.py:605`), lưu JPEG chỉ với `quality` (`:710`) rồi tự kiểm khuôn bằng `jpeg_layout` (`:714`, `:659–703`). Cộng với 892/892 của Soi Lỗi và 8 loại của Thợ Máy |
| Không ngoại lệ lạ, chỉ chặt hơn bản cũ | **Đạt** | **Thử độc lập (E):** 200.000 tệp đột biến (hạt giống `20261023`) từ 19 ảnh Pillow sạch: chèn 33 loại khối metadata/khối giải mã ở ranh giới khối, lặp, xóa, đổi chỗ khối, lật 1–4 byte, cắt cụt, nối đuôi. **Ngoại lệ ngoài `AIError`: 0**; **bản mới nhận mà bản cũ chặn: 0**; tệp bản mới nhận mà Pillow mở ra còn khóa `info` lạ (hồ sơ màu, EXIF, XMP, chú thích, chữ) hay EXIF: **0** (42.505 tệp được nhận). Đọc code cũng thấy mỗi danh sách cho phép mới là tập con của bản cũ, mỗi giới hạn độ dài chặt hơn hoặc bằng. Soi Lỗi: 2 triệu tệp, kết quả giống |
| Không chậm bất thường với tệp dựng cố ý | **Đạt** | Giới hạn kích thước giữ nguyên (`MAX_IMAGE_BYTES` 5 MB, tổng 10 MB, `:453–455`, kiểm trước khi đọc khối `:521–531`). **Thử độc lập (F)**, ảnh dựng 5 MB, lần nhanh nhất trong 3, máy đang chạy agent khác: 870 nghìn khối DRI 1,04 → 1,59 s (cũ → mới); 520 nghìn lượt quét 1,03 → 1,49 s; 1,3 triệu DQT rỗng 1,54 → 2,06 s; dữ liệu nén toàn `FF FF` 2,76 → 2,76 s; PNG 437 nghìn IDAT rỗng 0,58 → 0,69 s; JPEG thật 2400×1800: 0,003 s cả hai. Tăng tuyến tính theo dung lượng, chậm hơn tối đa ~1,5 lần ở tệp toàn khối nhỏ (kiểm thêm độ dài từng khối); ca xấu nhất cả lượt gửi (2 × 5 MB) dưới ~6 s. Đường thật của app không tới được ca này: byte gửi AI là JPEG vài trăm KB do `make_ai_image` tạo |
| Gộp với `origin/main` (`b38c590`) | **Được ngay** | Xem mục công cụ: không xung đột, test liên quan qua trên cây gộp. `main` đổi từ gốc (`folders.py`, `drafts.py`, test, tài liệu) không trùng file code nào của T-066 |

## Quyết Ghi nhận 1 của Soi Lỗi (câu chung chú thích, DRI/DNL lặp, SOS khai thừa)

**Quyết: chấp nhận, cùng loại phần còn lại của LC-T050-2. Không bắt sửa trong T-066, không siết thêm.**

Đã thử lại (B, cùng script): 294 khối DRI chở trọn một hồ sơ sRGB 588 byte; DNL trước lượt quét đầu; 200 khối DNL sau lượt quét; SOS khai 4 thành phần trong ảnh 1 thành phần; JPEG không có khung ảnh: **bản cũ và bản mới đều nhận**, đúng như Soi Lỗi mô tả (2 ca SOS thì Pillow không giải mã được ảnh).

Lý do:

- **Không mở thêm khả năng gì.** Mỗi khối DRI/DNL chở 2 byte, mỗi lượt quét chở tối đa 11 byte (đầu SOS là dữ liệu tùy ý ngay cả khi khai đúng số thành phần), trong khi một khối DQT hay DHT chở tới 65 KB, lặp không giới hạn, và dữ liệu ảnh nén không giới hạn (ca đối chứng B4, B5: cũng qua). Bịt DRI/DNL/SOS không giảm được lượng dữ liệu kẻ dựng file đưa đi.
- **Siết thêm có giá phải trả.** Chuẩn JPEG cho phép DRI xuất hiện trước mỗi lượt quét (đặt lại khoảng restart), nên cấm lặp DRI có thể chặn nhầm ảnh thật của phần mềm khác. DNL tối đa một lần, chỉ sau lượt quét đầu, và số thành phần của SOS không quá của khung ảnh thì làm được nhưng chỉ thêm code, không thêm an toàn.
- **Chú thích không còn gây hiểu sai như LC-T050-3.** Câu ngay sau (`:554–556`) nói rõ lớp này không chống được ảnh dựng cố ý, có nêu DQT, DHT; phần JPEG (`:566`) nói đúng "không kiểm độ dài" DQT, DHT. Người đọc không thể hiểu là lớp kiểm đã đủ. Lệch còn lại chỉ là câu chữ.

**Sửa chữ khi tiện** (không bắt buộc, làm cùng phiếu nào sau này chạm `base.py`), thay `:553–555`:

> …khối được nhận phải đúng độ dài theo khuôn (trừ bảng DQT, DHT); khung ảnh, APP0, APP14 và chunk PNG (trừ IDAT) không được lặp. **Không** chống được ảnh dựng cố ý: dữ liệu vẫn giấu được trong phần ảnh nén, bảng giải mã và các khối được lặp (DQT, DHT, DRI, DNL, SOS), các trường cố định (mật độ điểm ảnh, cờ…).

**Sổ rủi ro.** Phần còn lại của LC-T050-2 (gồm Ghi nhận 1) là rủi ro được chấp nhận thay vì sửa, nên theo `security.md` mục 3 và 6 phải do chủ dự án quyết và ghi sổ. Dòng mẫu để Chỉ Huy đưa chủ dự án duyệt (Lá Chắn không tự sửa `security.md`):

| Ngày | Rủi ro | Lý do chấp nhận | Người quyết định |
|---|---|---|---|
| 2026-10-23 | Lớp kiểm ảnh gửi AI (`prepare_images`, `seo_app/ai/base.py`; LC-T050-2 phần còn lại, Ghi nhận 1 của Soi Lỗi T-066): ảnh **dựng cố ý** vẫn chở được dữ liệu tùy ý tới hãng AI trong những phần phải nhận để giải mã (dữ liệu ảnh nén, bảng DQT/DHT, khối DRI/DNL/SOS lặp, CRC và dữ liệu sau dòng nén của PNG, đuôi VP8L/ALPH của WebP, các trường cố định như mật độ điểm ảnh). Metadata do phần mềm thật ghi (EXIF/GPS, XMP, chú thích, hồ sơ màu, khối riêng của hãng) đều bị chặn | Không đóng được nếu không giải mã ảnh. Bảo vệ thật là bản gửi AI luôn được dựng lại từ điểm ảnh (`make_ai_image`, T-049), nên byte dựng cố ý không đi theo đường của app (T-056 chỉ gửi bản đó). Muốn khai thác phải đặt được file dựng sẵn vào thư mục ảnh, và người nhận là hãng AI (kẻ dựng file không đọc lại được). Lá Chắn T-050, T-066 xếp Thấp | <chủ dự án> |

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | detect-secrets (`PYTHONUTF8=1`, `--all-files`, thư mục riêng có 6 file của diff lấy bằng `git show team/T-066:…`, patch `git log -p a9338f7..team/T-066`, 1 file mồi có chữ tiếng Việt): bắt **đủ 2/2 mồi**; 6 mục khác đều có từ trước (mục "Báo nhầm"); đã xóa thư mục quét. grep `security.md` mục 5 trên patch nhánh: chỉ tên dữ liệu thử (`SECRET_TEXT`, `ICC_SECRET`) và câu báo cáo tả cách quét. Không file nhị phân |
| S2 | Đạt | Câu báo vẫn cố định, không chép dữ liệu ảnh: chỉ thêm chữ "hồ sơ màu" vào `IMAGE_METADATA_MESSAGE` (`base.py:464–467`); không câu nào so nguyên văn câu này ngoài `base.py` và test (`git grep` trong `app/`, `seo_app/`) |
| S3 | Không áp dụng | Không biến cấu hình mới |
| W1 | Không áp dụng | Diff không có code WordPress |
| W2 | Không áp dụng | Như W1 |
| W3 | Không áp dụng | Không tạo HTML |
| W4 | Không áp dụng | Không gọi mạng; provider không đổi |
| A1 | Không áp dụng | Prompt không đổi |
| A2 | Không áp dụng | Không đổi cách gọi AI hay xử lý kết quả |
| A3 | Đạt | Đường duy nhất tới hãng AI: `ImageInput` chỉ có bytes + MIME (`base.py:470–484`); `suggest_alt` gọi `prepare_images` trước mọi lời gọi mạng (`alt.py:474`), mỗi provider gọi lại (`anthropic_provider.py:61`, `openai_provider.py:81`, `gemini_provider.py:137`); chưa có chỗ nào trong `app/` gọi `suggest_alt` (T-056). Mọi loại metadata do phần mềm thật ghi (EXIF/GPS, XMP, IPTC, chú thích, hồ sơ màu, khối riêng, chunk chữ) bị chặn theo danh sách cho phép, kèm bộ dò chuỗi EXIF/XMP ở mọi vị trí (`:533`, `:544`). Thử A, C, E: 0 lọt. Tên khách chỉ có thể nằm trong thẻ, đi qua lớp lọc của T-050, phiếu này không đụng. Bản `make_ai_image` không bị chặn oan (D: 320/320). Còn lại: ảnh dựng cố ý (LC-T050-2 phần còn lại, đề nghị ghi sổ) |
| U1 | Không áp dụng | Không có giao diện |
| U2 | Không áp dụng | Không có trang mới |
| U3 | Không áp dụng | Không đụng mật khẩu |
| F1 | Không áp dụng | Lớp kiểm chỉ đọc bytes trong bộ nhớ, không đường dẫn |
| F2 | Đạt | Giới hạn 4 ảnh / 5 MB mỗi ảnh / 10 MB tổng giữ nguyên và kiểm trước khi đọc khối (`base.py:453–455`, `:505–531`). Bỏ lần giải nén zlib duy nhất (hết chỗ phải chống bom giải nén: `iCCP` 64 MB nén bị từ chối ngay, test `test_png_iccp_decompression_bomb_is_rejected`). EXIF/GPS của **ảnh đăng web** không bị đụng (`process.py` không đổi), đúng quyết định mục 6 |
| F3 | Đạt | Chỉ so byte và đọc số nguyên; không `eval`, `pickle`, `exec`, không giải nén, không thư viện C nào đọc ảnh trong lớp kiểm |
| D1 | Đạt | `uv.lock`, `pyproject.toml` giống `main`; không import mới (bỏ bớt `zlib`). pip-audit 69 gói: không lỗ hổng |
| D2 | Đạt | `.gitignore` không đổi |
| D3 | Đạt | Bộ chặn mạng tự bật (`tests/conftest.py`); test mới chỉ dùng `io.BytesIO`, không `requests`, `urllib`, `socket`, không ghi file |

## Kết quả công cụ quét

Máy Windows 11 Pro (10.0.26300) của chủ dự án, Python 3.12, Pillow 13.0.0, worktree `wt-T-066`, nhánh `team/T-066` tại `f8e6d21`. Máy đang chạy song song các agent khác.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | `uv export --frozen --no-hashes --no-emit-project` (69 gói) → `uvx pip-audit -r … --no-deps --disable-pip`: **No known vulnerabilities found**. Khóa giống hệt `origin/main` | Có |
| bandit | `seo_app/ai/base.py`: **No issues identified** (576 dòng code). 3 file test của phiếu (bỏ B101): 3 mục B311 (`random` để sinh ảnh thử, hạt giống cố định) | Có. Báo nhầm (mục dưới) |
| detect-secrets 1.5.0 | **`PYTHONUTF8=1`**, `--all-files`: mồi **2/2** (`AWS Access Key`, `Secret Keyword`); 6 mục khác, đều có từ trước | Có. Mồi bị bắt nên file tiếng Việt thật sự được đọc (LC-T049-4) |
| Soát lịch sử git | `git log -p a9338f7..team/T-066 \| grep -inE "api[_-]?key\|password\|secret\|token"`: chỉ tên dữ liệu thử `SECRET_TEXT`, `ICC_SECRET` và 2 câu báo cáo tả cách quét mồi | Có, đọc từng dòng |
| ruff | `uv run ruff check .` (nhánh và cây gộp): **All checks passed!** | Có |
| pytest (nhánh) | `uv run pytest tests/test_ai_images.py tests/test_soi_loi_t050.py tests/test_soi_loi_t049.py tests/test_soi_loi_t066.py tests/test_images_process.py tests/test_app_pages.py tests/test_ai.py tests/test_ai_openai_gemini.py tests/test_ai_openai_gemini_soi_loi.py tests/test_ai_t026.py tests/test_ai_t028.py tests/test_ai_t034.py tests/test_soi_loi_t052.py tests/test_soi_loi_t062.py tests/test_soi_loi_t065.py tests/test_t062_alt_prompt.py -q -p no:cacheprovider -rfEsxX` (09:43–09:45): **1903 passed, 1 skipped, 0 hỏng, 0 xfail** | Có. Khớp số của Soi Lỗi. Bỏ qua 1: ca symlink T-052 (Windows chưa bật Developer Mode), có từ trước |
| Gộp với `main` | `git merge-tree --write-tree origin/main team/T-066` (`origin/main` = `b38c590`) → cây `2788699`, **không xung đột** (exit 0); cây gộp khác `main` đúng 6 file của T-066. Dựng cây gộp bằng `git archive` vào thư mục nháp, `uv sync --frozen`; 16 file test trên + `tests/test_drafts_images.py` (T-079 đổi đường đọc ảnh), 09:50–09:54: **2096 passed, 2 skipped, 0 hỏng**; ruff sạch | Có: `seo_app` nạp từ đúng thư mục cây gộp (in `__file__`; `base.py` không còn `zlib`), `certifi` 2026.10.19. 2 bỏ qua: ca symlink T-052 như trên, ca symlink chỉ Mac/Linux `tests/test_drafts_images.py:645` |
| Script thử (A–F) | `lc_t066_probe.py`, chạy `PYTHONUTF8=1 PYTHONPATH=. uv run python lc_t066_probe.py <old_base.py> [phần] [số tệp]` trong worktree; bản cũ lấy bằng `git show a9338f7:seo_app/ai/base.py`. Script và kết quả: thư mục ghi chú chung của nhóm phiên, `T-066-la-chan-scripts/`. Không commit | Có |

**Chưa chạy được (không ghi là đạt):** chưa chạy trên Mac/Linux (lớp kiểm chỉ đọc byte bằng Python thuần, không phụ thuộc hệ điều hành; chủ dự án chưa có máy Mac). Không chạy toàn bộ pytest (theo `rules.md`, Chỉ Huy chạy khi gộp). Không thử được bộ đọc ảnh của máy chủ hãng AI; "không lọt" ở trên lấy Pillow làm trọng tài, và lớp kiểm đọc chặt hơn Pillow ở mọi chỗ Soi Lỗi và tôi xem (đòi `FF` trước mỗi khối, đi hết mọi lượt quét tới EOI, không nhận dữ liệu sau EOI/IEND/RIFF): đây là suy luận.

## Báo nhầm đã loại

- detect-secrets "Basic Auth Credentials" ở `seo_app/ai/base.py:28` (chú thích ví dụ `https://admin:matkhau@site…` của bộ lọc lỗi, có từ trước; lệch 1 dòng do bỏ `import zlib`), ở `docs/team/reports/T-066-tho-may.md:103` và dòng tương ứng của patch (báo cáo trích lại đúng chú thích đó).
- detect-secrets "Base64 High Entropy String" ở `tests/test_ai_images.py:70–72`: 3 khóa giả `…T050KhoaGia…` của T-050, có từ trước.
- bandit B311 ở `tests/test_soi_loi_t050.py:993`, `tests/test_soi_loi_t066.py:62`, `:352`: `random` chỉ để sinh ảnh thử, không dùng cho mã hóa.

## Đề nghị (không chặn gộp)

1. **Chỉ Huy → chủ dự án:** duyệt dòng sổ rủi ro ở mục "Quyết Ghi nhận 1" (phần còn lại của LC-T050-2). Nếu chủ dự án không chấp nhận, cách thay thế là T-056 bắt buộc bằng code chỉ gửi bản `make_ai_image` (đề nghị 2), không phải siết thêm `base.py`.
2. **T-056** (điều kiện đã ghi trong phiếu ngày 23/10, từ Soi Lỗi T-066): chỉ gọi `suggest_alt` với `ImageInput(data=make_ai_image(ảnh).data, mime="image/jpeg")`; thêm: **có test** khẳng định byte provider giả nhận được đúng là bản `make_ai_image` của ảnh đã chọn (không phải byte gốc, không phải ảnh đăng web), kể cả khi ảnh gốc có GPS và hồ sơ màu. Lớp kiểm của T-066 nay chặn ảnh gốc điện thoại và ảnh WebP đăng web, nên lỡ truyền nhầm sẽ báo lỗi ngay chứ không lộ metadata.
3. **Phiếu nào sau này chạm `base.py`:** sửa câu chung `:553–555` theo mẫu ở trên.
4. **Sau 01/11:** kiểm lại biên bản này bằng Claude Fable.

## Kết luận

**ĐẠT.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp mới. Đủ 4 yêu cầu của phiếu; LC-T050-1, LC-T050-3, SL-T050-5, SL-T050-6 đóng; LC-T050-2 đóng phần sửa được, phần còn lại là giới hạn vốn có của cách kiểm cấu trúc (đề nghị ghi sổ rủi ro). Ghi nhận 1 của Soi Lỗi: chấp nhận, không bắt sửa. Gộp vào `main` được ngay.

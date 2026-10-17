# Báo cáo T-046 · Thiết kế Giai đoạn 3 (ảnh): tìm hiểu kỹ thuật, chia phiếu

| Mục | Nội dung |
|---|---|
| Agent | Thợ Máy (`tho-may`) · model: Claude Opus 5.5 |
| Phiếu | [T-046](../tickets/T-046-thiet-ke-giai-doan-3.md) |
| Ngày nộp | 2026-10-17 |
| Kết quả | Hoàn thành (phiếu thiết kế, không sửa code) |

## Tóm tắt (cho chủ dự án)

- Đã thử thật bằng Pillow: nén ảnh JPEG có vị trí GPS sang WebP **giữ được GPS**, với điều kiện code chép lại EXIF. Nén theo cách mặc định thì **mất hết GPS**, nên phải có test bắt buộc.
- Pillow **không đọc được ảnh HEIC** của iPhone. Cần chủ dự án chọn cách xử lý (câu hỏi 1).
- Pillow **đã có sẵn** trong `uv.lock` (bản 12.3.0, do Streamlit kéo theo). Phiếu đầu tiên chỉ cần khai báo nó trong `pyproject.toml`, không tải thêm gì.
- Đề xuất chia Giai đoạn 3 thành 10 phiếu, kèm 5 câu hỏi cho chủ dự án ở cuối.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `docs/team/reports/T-046-tho-may.md` | Báo cáo này (file duy nhất) |

Không sửa code, cấu hình, test. Thử nghiệm chạy trong thư mục tạm ngoài repo (`scratchpad\t046\`), không thêm Pillow vào dự án.

## Bằng chứng: kết quả thử Pillow (2026-10-17)

Máy Windows 11, Python 3.12.15. Chạy với **Pillow 12.3.0** (đúng bản trong `uv.lock`) và **Pillow 13.0.0** (bản mới nhất): hai bản cho kết quả giống hệt nhau. Ảnh và GPS đều giả, tạo bằng Pillow.

```
uv run --no-project --with pillow==12.3.0 python exif_gps_test.py
uv run --no-project --with pillow==12.3.0 python bomb_heic_test.py
uv run --no-project python f1_test.py
```

| # | Thử | Kết quả |
|---|---|---|
| 1 | JPEG giả 4000×3000, Orientation=6, GPS N 16.0544 / E 108.2022, hãng máy, đời máy, số seri giả | Đọc lại đủ |
| 2 | Nén WebP **không** truyền `exif=` | **Mất hết EXIF, mất GPS** |
| 3 | `ImageOps.exif_transpose` → đặt Orientation=1 → thu cạnh dài 1600 → WebP q80 kèm `exif=` | **GPS giữ nguyên** (N 16.0544, E 108.2022), Orientation=1, ngày chụp còn, ảnh 1200×1600 xoay đúng (điểm ảnh góc trái trên đúng màu) |
| 4 | Như 3, bỏ Make, Model, Software, BodySerialNumber | GPS và ngày chụp còn, thông tin máy hết |
| 5 | Bản gửi AI: cạnh dài 1024, JPEG, bỏ `exif` và `xmp` | File không còn chuỗi `Exif`, không có GPS |
| 6 | Ảnh chụp màn hình PNG không EXIF → WebP | Không lỗi, file không có EXIF |
| 7 | Bom giải nén (hạ ngưỡng để thử) | Quá 1 lần ngưỡng: chỉ cảnh báo. Quá 2 lần: `DecompressionBombError` ngay lúc mở, trước khi giải nén. Biến cảnh báo thành lỗi được (`warnings.simplefilter("error", Image.DecompressionBombWarning)`) |
| 8 | File BMP và file chữ `<?php …` đổi đuôi `.jpg`, mở với `formats=["JPEG","PNG","WEBP"]` | `UnidentifiedImageError`: Pillow nhận dạng theo nội dung file, không theo đuôi |
| 9 | File `.heic` (đầu file `ftypheic`) | Pillow **không đọc được** (`UnidentifiedImageError`). `.heic`, `.heif` không có trong danh sách đuôi Pillow nhận |
| 10 | AVIF | Pillow 12.3 và 13 đều đọc/ghi được |
| 11 | JPEG nhiều khung (MPO, iPhone hay tạo) | Mở được qua bộ mở JPEG, `im.format == "MPO"`. **Bẫy:** ghi `"MPO"` vào `formats=` gây `KeyError` |
| 12 | JPEG bị cụt | `load()` báo `OSError`, bắt được |
| 13 | Junction Windows trong thư mục ảnh trỏ ra ngoài | `Path.resolve()` + `is_relative_to(gốc)` **chặn được**. **Bẫy:** `os.scandir` báo junction là thư mục (`is_dir(follow_symlinks=False) = True`, `is_symlink() = False`); phải kiểm thêm `is_junction()` (Python 3.12+) |
| 14 | `..`, `C:/…`, `\\server\share\…`, `D:anh.jpg` | Chặn được bằng kiểm `PureWindowsPath`: có `drive`/`anchor`/`..` thì từ chối |

Lưu ý: dung lượng ở thử 3 (4 KB) là của ảnh phẳng hai màu, **không** đại diện cho ảnh thật. Chọn chất lượng WebP phải thử lại bằng ảnh thật (phiếu G3-3).

---

## 1. Đọc ảnh từ thư mục (F1)

**Nơi đặt code:** `seo_app/images/folders.py` (thư mục `seo_app/images/` đã ghi trong cấu trúc đề xuất của `CLAUDE.md`).

| Vấn đề | Thiết kế |
|---|---|
| Gốc thư mục | Mỗi thư mục trong `IMAGE_FOLDERS` được `resolve(strict=True)` lúc đọc cấu hình. Thư mục không tồn tại (USB chưa cắm, Drive chưa chạy) thì báo "chưa thấy thư mục", không lỗi app |
| Cách chỉ tới một ảnh | Giao diện chỉ giữ **(số thứ tự gốc, đường dẫn tương đối)**, không bao giờ nhận đường dẫn tuyệt đối từ người dùng hay từ nháp đã lưu |
| Chặn ra ngoài | Từ chối khi đường dẫn tương đối có `..`, ổ đĩa, `\\server`, gốc tuyệt đối (thử 14). Sau đó `resolve()` và bắt buộc `is_relative_to(gốc)`: chặn cả symlink lẫn junction trỏ ra ngoài (thử 13) |
| Không ghi vào thư mục ảnh | App chỉ **đọc** thư mục ảnh. File nén ra giữ trong bộ nhớ hoặc thư mục cache của app (đã chặn trong `.gitignore`). Ngoại lệ duy nhất có thể có: file thẻ ảnh, tùy câu hỏi 3 |
| Đuôi được nhận | `.jpg`, `.jpeg`, `.png`, `.webp`. Thêm `.heic`/`.heif` nếu chủ dự án chọn 1A. Không nhận `.gif` (ảnh động), `.bmp`, `.tif`, `.lnk` |
| Kiểm nội dung | Mở bằng `Image.open(f, formats=["JPEG","PNG","WEBP"])`, không tin đuôi file (thử 8). Ảnh MPO đi qua bộ mở JPEG (thử 11) |
| Giới hạn dung lượng | Đọc `stat().st_size` **trước khi mở**: tối đa 40 MB/file (ảnh 48 MP của iPhone khoảng 5–15 MB; con số chưa xác minh với ảnh thật) |
| Giới hạn điểm ảnh | `Image.MAX_IMAGE_PIXELS = 100_000_000` và biến cảnh báo thành lỗi (thử 7). Đủ cho máy 48–64 MP; máy 200 MP sẽ bị từ chối kèm câu báo rõ (chưa xác minh có ai trong đội dùng máy như vậy). Với JPEG, gọi `im.draft("RGB", (3200, 3200))` để giải nén ở 1/2–1/8 kích thước, giảm RAM |
| Ảnh cụt, hỏng | Bắt `UnidentifiedImageError`, `OSError`, `DecompressionBombError` → câu báo tiếng Việt, không chứa đường dẫn đầy đủ của máy |

**HEIC (ảnh iPhone):** Pillow không đọc được (thử 9). Có 3 cách, đưa thành **câu hỏi 1**:

| Cách | Hệ quả |
|---|---|
| Thêm thư viện `pillow-heif` (gắn vào Pillow, có bản cài sẵn cho Windows và Mac) | Đọc thẳng HEIC. Là thư viện mới, phải duyệt (D1) và Lá Chắn quét. Thư viện này đóng gói kèm libheif/libde265 (giấy phép LGPL, chưa xác minh chi tiết; dùng nội bộ thì thường không vướng) |
| Đổi cài đặt iPhone: Cài đặt → Camera → Định dạng → "Tương thích nhất" | Ảnh chụp mới là JPEG, không cần thư viện. Ảnh HEIC cũ vẫn không đọc được |
| App bỏ qua HEIC, liệt kê "N ảnh HEIC chưa đọc được" | Đơn giản nhất, nhưng phải tự chuyển đổi bằng công cụ khác |

**Quét thư mục lớn (hàng nghìn ảnh, Google Drive chậm):**
- Duyệt bằng `os.scandir` theo từng thư mục, **chỉ đọc tên và `stat`**, không mở ảnh khi quét. Không đi vào symlink/junction (`is_symlink()`, `is_junction()`).
- Có ngân sách: tối đa 5 000 file và 10 giây mỗi lần quét; vượt thì dừng và báo "thư mục quá lớn, chọn thư mục con". Số cụ thể sẽ chỉnh khi thử với Drive thật.
- Kết quả cache bằng `st.cache_data(ttl=300)` theo (gốc, thư mục con); có nút "Quét lại".
- Duyệt theo **từng thư mục con** (thường mỗi thư mục là một công trình) và phân trang 24–48 ảnh. Chỉ tạo ảnh xem trước cho trang đang mở. Ảnh xem trước nhỏ (320 px), lưu cache cục bộ, tên file là mã băm.
- Google Drive for Desktop có chế độ "chỉ trực tuyến": mở file sẽ khiến Drive tải file về. Vì vậy không mở file khi quét, và việc tạo ảnh xem trước chạy với giới hạn thời gian (chưa xác minh tốc độ thật).

## 2. Xử lý ảnh (YC-303, F2)

**Nơi đặt code:** `seo_app/images/process.py`. Các bước dưới đây đều đã thử (thử 3–6).

| Bước | Cách làm |
|---|---|
| 1. Mở an toàn | Như mục 1 (định dạng, dung lượng, số điểm ảnh) |
| 2. Lấy EXIF | `exif = im.getexif()` trước khi xoay |
| 3. Xoay đúng chiều | `ImageOps.exif_transpose(im)`, rồi đặt `exif[Orientation] = 1` |
| 4. Đổi chế độ màu | CMYK → RGB; PNG bảng màu → RGBA; giữ `icc_profile` để màu không lệch |
| 5. Thu nhỏ | `thumbnail((1600, 1600), LANCZOS)`: chỉ thu nhỏ, không phóng to |
| 6. Nén WebP | `save(..., "WEBP", quality=80, method=6, exif=exif.tobytes(), icc_profile=...)`. Chất lượng 80 là điểm khởi đầu, đặt trong `config/content.toml` để chỉnh. Thử với ảnh thật ở G3-3, nhắm khoảng 150–400 KB/ảnh |
| 7. **Kiểm sau khi nén** | Mở lại file WebP; nếu ảnh gốc có GPS mà bản WebP không có thì **dừng và báo lỗi**, không tải lên. Có test bắt buộc chứng minh (thử 2 cho thấy chỉ cần quên tham số `exif=` là mất GPS) |
| 8. Bản gửi AI | Tách riêng: cạnh dài 1024, JPEG q85, **không EXIF, không XMP** (thử 5) |

**Thông tin máy trong EXIF** (chủ dự án mới chốt "giữ GPS", chưa nói về phần còn lại). Đưa thành **câu hỏi 2**:

| Nhóm trường | Ví dụ | Đề xuất |
|---|---|---|
| Vị trí | GPS | **Giữ** (đã chốt) |
| Chiều, ngày chụp | Orientation (đặt =1), DateTimeOriginal | Giữ |
| Máy | Make, Model, LensModel, Software | Giữ (vô hại) |
| Định danh người/máy | BodySerialNumber, LensSerialNumber, CameraOwnerName, Artist | Bỏ: không giúp SEO, lộ máy của nhân viên |
| Dữ liệu riêng của hãng | MakerNote (khối nhị phân, có thể vài KB) | Bỏ: nặng, không đọc được, có thể chứa số seri (chưa xác minh với ảnh iPhone thật) |
| Ảnh nhỏ nhúng trong EXIF | IFD1 thumbnail | Bỏ nếu còn: ảnh này chưa xoay và chưa thu nhỏ. Chưa xác minh `Exif.tobytes()` của Pillow có chép nó hay không; G3-3 phải kiểm |
| XMP | dữ liệu Adobe/Apple | Không chép (chỉ chép EXIF); chưa xác minh XMP của iPhone có chứa GPS hay không |

**Ảnh chụp màn hình, ảnh không có EXIF:** vẫn xử lý bình thường, file ra không có EXIF (thử 6). Giao diện ghi "Ảnh không có vị trí GPS". App **không tự thêm** GPS.

**Đặt tên file:**
- Tên = `slugify(hạng mục + khu vực + mã công trình)`; nếu thiếu thẻ thì dùng alt đã duyệt; cuối cùng là `anh`. Dùng `slugify` sẵn có (`seo_app/text.py`), cắt còn 60 ký tự, đuôi `.webp`.
- Tránh trùng trong cùng một bài: thêm `-2`, `-3`. Trên WordPress: WordPress tự thêm hậu tố khi trùng và không ghi đè file cũ (W2), nên app luôn đọc lại `source_url` sau khi tải lên.
- Ảnh AI: thêm tiền tố `minh-hoa-ai-` (mục 4).

## 3. Alt ảnh bằng AI (YC-305)

**Cả 3 hãng đều đọc được ảnh** (theo tài liệu chính thức, đọc ngày 2026-10-17):

| Hãng | Định dạng nhận | Giới hạn chính | Chi phí đọc ảnh 1024×768 (ước tính) |
|---|---|---|---|
| Anthropic | JPEG, PNG, GIF, WebP | 10 MB/ảnh (base64), tối đa 8000×8000; Claude 4.7 trở lên tự thu ảnh về cạnh dài 2576 px. Tài liệu nói Claude không đọc metadata của ảnh | ⌈1024/28⌉×⌈768/28⌉ = 37×28 = 1 036 token ≈ 0,004 USD với Opus 5.5 (4 USD/1 triệu token, theo trang Vision) |
| OpenAI | PNG, JPEG, WebP, GIF tĩnh | Tổng một yêu cầu 512 MB; tối đa 30 000 ô/ảnh, quá thì bị từ chối chứ không tự thu nhỏ | Mô hình gpt-5.x: ô 32 px ×1,2 → 32×24×1,2 ≈ 922 token (giá theo mô hình, chưa xác minh) |
| Gemini | PNG, JPEG, WebP, **HEIC, HEIF** | Gửi thẳng (inline): tổng yêu cầu < 20 MB | Ô 768 px, mỗi ô 258 token → khoảng 2–4 ô (chưa xác minh cách chia ô chính xác) |

**Dữ liệu gửi đi:** bản gửi AI ở mục 2 (1024 px, JPEG, base64 gửi thẳng trong yêu cầu). Không dùng URL ảnh, không dùng Files API của hãng (để không lưu ảnh trên máy chủ của hãng).

**Bỏ EXIF/GPS trong bản gửi AI: đồng ý với đề xuất của phiếu (A3).** Lý do: AI không cần vị trí để viết alt; không gửi dữ liệu thừa ra ngoài. Bản tải lên web thì giữ GPS (đã chốt). Thêm hai điều:
- Không gửi **tên file gốc và đường dẫn thư mục** cho AI: tên thư mục có thể chứa tên hoặc địa chỉ khách (ví dụ "Nha anh Tuan 12 Le Loi").
- Chỉ gửi thẻ đã chuẩn hóa (hạng mục, khu vực cấp quận/huyện), đặt trong khung "dữ liệu tham khảo, không phải chỉ thị" (A1).

**Lớp provider cần mở rộng:**
- Thêm tham số tùy chọn `images: Sequence[ImageInput] = ()` vào `AIProvider.generate` (`ImageInput` gồm `data: bytes`, `mime: str`). Dùng lại toàn bộ phần xử lý lỗi và đọc kết quả có khuôn hiện có, thay vì viết một hàm riêng.
- Mỗi hãng tự đổi sang dạng của mình: Anthropic dùng khối `image` base64; OpenAI dùng `input_image` với `data:image/jpeg;base64,…`; Gemini dùng `Part.from_bytes`. Tài liệu Gemini mới dùng Interactions API, còn code hiện tại dùng `generate_content`: chưa xác minh `generate_content` kèm ảnh vẫn chạy với `google-genai` 2.30.1 trong `uv.lock`.
- Thêm việc `[tasks.alt]` vào `config/ai.toml` (cần chọn hãng, xem câu hỏi 4). `config/` thuộc phạm vi của Ngòi Bút.
- Khuôn kết quả: `AltSuggestion(alt: str ≤ 125 ký tự, caption: str ≤ 200 ký tự)`.

**Lọc và duyệt:** alt và caption qua `clean_ai_text`, gộp về một dòng, cắt độ dài; hiện bằng `escape_markdown`. Người dùng sửa và bấm duyệt (YC-305) trước khi tải lên. Alt rỗng thì không cho gửi ảnh thật.

## 4. Ảnh AI (YC-306)

| Hãng | Tạo ảnh? | Cách gọi | Giá ước tính mỗi ảnh |
|---|---|---|---|
| Anthropic | **Không** (tài liệu Vision ghi rõ Claude không tạo ảnh) | — | — |
| OpenAI | Có: `gpt-image-2`, `gpt-image-2.5-flare` (nhanh), `gpt-image-2.5-sunburst` (sửa ảnh tốt) | Images API `images.generate`, trả base64 (`b64_json`); xuất được PNG/JPEG/WebP; cỡ 1024×1024, 1536×1024, 1024×1536 | gpt-image-2, cỡ 1024×1024: thấp 0,006 / vừa 0,053 / cao 0,211 USD. Bản 2.5: giá 30 USD/1 triệu token đầu ra, số token mỗi ảnh lấy từ máy tính giá trên web: **chưa xác minh** |
| Gemini | Có: `gemini-nano-banana-2.1` (đề xuất), `gemini-3.1-flash-lite-image`, `gemini-3.1-flash-image`, `gemini-3-pro-image` | Tài liệu dùng `client.interactions.create(..., response_format={"type":"image", ...})`, trả base64. Chưa xác minh SDK 2.30.1 có hàm này | nano-banana-2.1: 0,0336 (1K) / 0,0504 (2K) USD; flash-lite: 0,0336; 3.1-flash: 0,067 / 0,101; 3-pro: 0,134. Không có gói miễn phí cho ảnh |

Ảnh Gemini luôn có dấu chìm SynthID (nằm trong điểm ảnh, nén lại vẫn còn theo mô tả của Google, chưa xác minh). OpenAI có gắn dữ liệu C2PA hay không: tài liệu đã đọc không nói, chưa xác minh. Nếu có thì sẽ mất khi app nén lại sang WebP.

**Thiết kế:**
- Việc mới `[tasks.image]` trong `config/ai.toml`. Nếu khai báo `provider = "anthropic"` thì app báo "Claude không tạo được ảnh, chọn openai hoặc gemini".
- **Prompt:** lấy từ mô tả "chỗ cần ảnh" của dàn ý; lưu cùng nháp; hiện trong ô sửa được và `st.code` (có nút sao chép). Mỗi lần tạo ảnh lưu đúng prompt đã dùng.
- **Chi phí:** hiện giá ước tính trước khi bấm tạo; mỗi lần tạo 1 ảnh (`n=1`).
- **Kiểm ảnh trả về:** giải base64 có giới hạn (≤ 20 MB) → mở bằng Pillow với `formats=["PNG","JPEG","WEBP"]` → kiểm số điểm ảnh và kích thước đúng cỡ đã xin → đi qua đúng quy trình nén WebP ở mục 2 (không có EXIF gốc, không có GPS).
- **Đánh dấu ảnh AI:** tên file `minh-hoa-ai-<slug>.webp`; EXIF `ImageDescription = "Ảnh minh họa tạo bằng AI"` và `Software = "<hãng>/<mô hình>"`; caption mặc định "Ảnh minh họa (AI)"; tiêu đề media bắt đầu bằng `[AI]`. Alt vẫn mô tả nội dung ảnh như bình thường.
- **Không bao giờ gắn thẻ công trình thật:** khuôn thẻ có trường `nguon: "that" | "ai"`. Khi `nguon = "ai"`, code từ chối `ma_cong_trinh` và `truoc/sau`; có test chứng minh.

## 5. Gắn thẻ ảnh (YC-302)

Thẻ gồm: hạng mục, khu vực, trước/sau, mã công trình. Yêu cầu: **2 máy cùng thấy**.

| Cách | Ưu | Nhược |
|---|---|---|
| A. Tên thư mục làm thẻ: `<mã> - <hạng mục> - <khu vực>/truoc/`, `/sau/` | Không cần lưu gì, 2 máy thấy ngay qua Drive, người đọc hiểu, app không phải ghi file | Phải đặt tên thư mục đúng quy ước; thẻ theo cả thư mục, không theo từng ảnh |
| B. File thẻ đi kèm trong thư mục Drive (1 file `_seo_tags.json` mỗi thư mục) | Thẻ từng ảnh, đồng bộ qua Drive, đi cùng ảnh | App phải **ghi** vào thư mục ảnh (hiện chỉ đọc). Hai máy sửa cùng lúc thì Drive tạo bản "(1)"; USB không đồng bộ; đổi tên ảnh thì mất thẻ |
| C. SQLite cục bộ (giống kho nháp) | Nhanh, có sẵn, không thêm thư viện | **Mỗi máy một bản, 2 máy không thấy nhau.** Đặt file SQLite trong thư mục Drive dễ hỏng file, không nên |
| D. Trên WordPress media | Thấy ở mọi nơi | Chỉ có sau khi đã tải ảnh lên (công khai); thẻ riêng cần plugin đăng ký meta; sửa media cũ đụng W2 |

**Đề xuất:** A làm gốc (đọc thẻ từ tên thư mục), cộng C để làm cache và nhớ thẻ sửa tay trên từng máy. Nếu chủ dự án cần thẻ từng ảnh đồng bộ giữa 2 máy thì chọn thêm B, chỉ ghi đúng một tên file, ghi an toàn (ghi file tạm rồi đổi tên). Đưa thành **câu hỏi 3**.

## 6. Tải lên WordPress

Dùng hàm sẵn có `upload_media`, `create_draft(featured_media=…)`, `set_featured_image`.

| Bước | Thiết kế |
|---|---|
| Khi nào tải | **Chỉ khi người dùng bấm "Gửi nháp"**, không tải lúc chọn ảnh. Lý do: ảnh trên WordPress là **công khai ngay** qua đường dẫn, kể cả khi bài vẫn là nháp, và ảnh có GPS |
| Thứ tự | Tải từng ảnh (`upload_media`, kèm alt, caption, title) → dựng HTML `<figure><img src alt width height></figure>` bằng code (giá trị đã escape) → `create_draft(content, featured_media=<ảnh đầu hoặc ảnh người dùng chọn>)` |
| Lỗi giữa chừng | Ảnh đã tải mà tạo bài lỗi: ảnh còn lại trong thư viện media. App liệt kê đường dẫn sửa từng ảnh; **không xóa** (app không có hàm xóa, W2) |
| Bộ lọc HTML | `sanitize_html` đã cho phép `img`, `figure`, `figcaption`, `src`, `alt`, `width`, `height`, `srcset`. **Chưa cho `class`**, nên thiếu `class="wp-image-<id>"`. Thiếu lớp này thì WordPress không tự thêm `srcset` (ảnh nhiều cỡ cho điện thoại; theo hiểu biết về `wp_filter_content_tags`, chưa xác minh trên site). Nếu cần thì mở `class` chỉ cho mẫu `wp-image-\d+` và `wp-block-image` (Lá Chắn phải soát) |
| W1–W4 | Bài luôn `draft`; ảnh đại diện chỉ đặt cho bài app vừa tạo (đã có trong `set_featured_image`); không ghi đè media cũ; https, timeout, SSL như hiện tại |
| Bytes ảnh | `upload_media` gửi nguyên bytes, không sửa gì, nên GPS lên tới máy chủ. Có test với `fake_wordpress` kiểm bytes gửi đi còn GPS |

**GPS sau khi lên WordPress (cần kiểm trên site thật):**
- WordPress chỉ tạo bản "-scaled" khi ảnh lớn hơn 2560 px. App thu về 1600 px nên file gốc được giữ nguyên (chưa xác minh với WebP).
- Các cỡ nhỏ do WordPress tự tạo (thumbnail, medium, large) **bị bỏ metadata**: GD luôn bỏ; Imagick bỏ theo mặc định (`image_strip_meta = true`). Nếu bài hiện cỡ nhỏ qua `srcset`, trình duyệt có thể tải bản **không có GPS**. Muốn chắc có GPS thì `src` trỏ vào file đầy đủ.
- Plugin nén ảnh hoặc CDN (Smush, ShortPixel, LiteSpeed, Cloudflare Polish…) có thể xóa EXIF của cả file gốc. Chưa biết site đang dùng gì: chủ dự án cần kiểm (xem phần Rủi ro).
- Site phải nhận WebP (WordPress 5.8 trở lên, máy chủ có thư viện ảnh hỗ trợ WebP). Chưa xác minh trên suachuacuasat.com.

## 7. Chia phiếu Giai đoạn 3

Đặt tên tạm G3-1…G3-10; Chỉ Huy đánh số T-xxx. Phiếu logic thuần, test bằng ảnh giả tạo trong test, đặt trước. Phiếu nào sửa code cũng qua Soi Lỗi và Lá Chắn.

| Phiếu | Mục tiêu | Agent | File được sửa | Phụ thuộc | Bảo mật |
|---|---|---|---|---|---|
| **G3-1** | Khai báo `pillow>=12.3` trong `pyproject.toml` (đã duyệt; `uv.lock` đã có 12.3.0, chỉ cập nhật thành phụ thuộc trực tiếp) | Thợ Máy | `pyproject.toml`, `uv.lock` | — | D1, `pip-audit` |
| G3-2 | Đọc thư mục ảnh an toàn: gốc, đường dẫn tương đối, chặn `..`/symlink/junction, đuôi file, giới hạn dung lượng, quét có ngân sách, phân trang | Thợ Máy | `seo_app/images/__init__.py`, `seo_app/images/folders.py`, `tests/test_images_folders.py` | — (không cần Pillow) | F1, F3; test junction chạy trên Windows, symlink trên Mac |
| G3-3 | Xử lý ảnh: mở an toàn, xoay, thu nhỏ, WebP, chép EXIF (theo câu 2), **kiểm GPS sau nén**, bản gửi AI không EXIF, ảnh xem trước, đặt tên file | Thợ Máy | `seo_app/images/process.py`, `seo_app/images/naming.py`, `tests/test_images_process.py` | G3-1; câu hỏi 1, 2 | F2 (test bắt buộc: còn GPS sau nén; bản AI không còn EXIF), chống bom giải nén |
| G3-4 | Đọc ảnh cho AI: tham số `images` trong lớp provider của 3 hãng, khuôn `AltSuggestion`, hàm gợi ý alt | Thợ Máy | `seo_app/ai/base.py`, `seo_app/ai/*_provider.py`, `seo_app/ai/registry.py`, `seo_app/images/alt.py`, `tests/fake_ai.py`, `tests/test_ai_images.py` | — (nhận bytes; chạy song song với G3-2, G3-3) | A1, A2, A3 (không gửi EXIF, tên file, đường dẫn), lọc `clean_ai_text` |
| G3-5 | Prompt và quy tắc viết alt; thêm `[tasks.alt]`, `[tasks.image]` vào `config/ai.toml`; chất lượng WebP vào `config/content.toml` | Ngòi Bút | `config/ai.toml`, `config/content.toml`, file prompt alt trong `config/` | Câu hỏi 4; chạy song song | A1 |
| G3-6 | Thẻ ảnh: khuôn thẻ (`nguon` thật/AI), đọc thẻ từ tên thư mục, cache SQLite (và file thẻ nếu chọn B) | Thợ Máy | `seo_app/images/tags.py`, `seo_app/storage/image_tags.py`, `tests/test_images_tags.py` | G3-2; câu hỏi 3 | F1 (nếu ghi file thẻ: chỉ đúng một tên, ghi an toàn), F3, YC-306 |
| G3-7 | Tạo ảnh AI: hàm tạo ảnh cho OpenAI và Gemini, kiểm ảnh trả về, đánh dấu AI, ước tính giá | Thợ Máy | `seo_app/ai/images.py` (mới), `seo_app/ai/openai_provider.py`, `seo_app/ai/gemini_provider.py`, `tests/test_ai_image_gen.py` | G3-3, **G3-4** (cùng file provider, phải chạy sau) | A2, kiểm định dạng/kích thước, không GPS, không thẻ công trình |
| G3-8 | WordPress: dựng HTML `<figure>`, (nếu cần) mở `class="wp-image-N"` trong bộ lọc, test bytes gửi lên còn GPS | Thợ Máy | `seo_app/wordpress/client.py`, `seo_app/sanitize.py`, `seo_app/images/html.py`, `tests/test_wordpress_images.py` | G3-3 | W1–W4, 2.3 (Lá Chắn soát kỹ thay đổi ở `sanitize.py`) |
| G3-9 | Nháp lưu lựa chọn ảnh: gốc + đường dẫn tương đối, nguồn thật/AI, alt đã duyệt, prompt AI; đọc được nháp cũ | Thợ Máy | `seo_app/storage/drafts.py`, `tests/test_drafts_images.py` | G3-6 | F1 (không lưu đường dẫn tuyệt đối), nháp cũ vẫn mở được |
| G3-10 | Giao diện: thay demo "chỗ cần ảnh" bằng chức năng thật (bố cục đã duyệt): chọn thư mục/ảnh, xem trước, duyệt alt, tạo ảnh AI kèm prompt, gửi nháp kèm ảnh | Họa Sĩ | `app/views/write.py`, `seo_app/demo.py`, `app/assets/style.css` | G3-2 → G3-9 | U1, U2; không hiện đường dẫn tuyệt đối |

Sau G3-10: Thư Ký cập nhật README (cách khai báo `IMAGE_FOLDERS`, HEIC, GPS). Lá Chắn chạy một lượt toàn Giai đoạn 3.

**Nhóm chạy song song:** (G3-2, G3-4, G3-5) → (G3-3, G3-6) → (G3-7, G3-8, G3-9) → G3-10. Không có hai phiếu cùng lúc sửa một file. Riêng `seo_app/images/__init__.py` chỉ G3-2 tạo; phiếu sau không sửa file này, import thẳng module con.

## 8. Câu hỏi cho chủ dự án

Xếp theo mức cần thiết. Mỗi câu trả lời bằng một chữ cái.

**Câu 1. Ảnh HEIC của iPhone** (định dạng ảnh mặc định của iPhone; thư viện ảnh Pillow không đọc được).
- **A. Thêm thư viện `pillow-heif` (đề xuất).** Đọc thẳng ảnh iPhone cũ và mới. Là thư viện mới: Lá Chắn quét lỗ hổng trước khi dùng.
- B. Không thêm thư viện; anh chỉnh iPhone sang "Tương thích nhất" (Cài đặt → Camera → Định dạng). Ảnh mới là JPEG; ảnh HEIC cũ app báo "chưa đọc được".
- C. App chỉ liệt kê ảnh HEIC là "bỏ qua".

**Câu 2. Ngoài GPS, giữ phần nào của thông tin ảnh (EXIF)?**
- **A. Giữ GPS, ngày chụp, hãng và đời máy; bỏ số seri máy, tên chủ máy và khối dữ liệu riêng của hãng (đề xuất).** Không lộ máy của nhân viên, file nhẹ hơn.
- B. Giữ toàn bộ như ảnh gốc. Đơn giản nhất, nhưng số seri máy công khai trên web.
- C. Chỉ giữ GPS.

**Câu 3. Thẻ ảnh (hạng mục, khu vực, trước/sau, mã công trình) lưu ở đâu để 2 máy cùng thấy?**
- **A. Đặt theo tên thư mục trong Drive, ví dụ `CT012 - Cổng inox - Hải Châu/truoc` (đề xuất).** App không phải ghi gì vào Drive. Thẻ sửa tay chỉ nhớ trên máy đang dùng.
- B. Như A, cộng thêm một file thẻ nhỏ trong mỗi thư mục Drive, app được phép ghi. Thẻ từng ảnh đồng bộ 2 máy; hai máy sửa cùng lúc thì Drive có thể tạo bản trùng.
- C. Chỉ lưu trên máy (mỗi máy tự gắn thẻ riêng).

**Câu 4. Hãng AI cho hai việc mới (ghi trong `config/ai.toml`, đổi được bất cứ lúc nào):**
- **A. Viết alt: Claude Sonnet; tạo ảnh: Gemini `gemini-nano-banana-2.1` (khoảng 0,034 USD/ảnh) (đề xuất).** Claude không tạo được ảnh.
- B. Tạo ảnh bằng OpenAI `gpt-image-2` (chất lượng vừa khoảng 0,053 USD/ảnh, cao khoảng 0,21 USD/ảnh).
- C. Anh tự thử rồi chọn (app sẽ cho thử tạo ảnh như thử mù viết bài; thêm việc cho G3-10).

**Câu 5. Ảnh trong bài dùng file nào?**
- **A. Dùng file đầy đủ 1600 px làm ảnh chính, để chắc chắn GPS tới người xem và Google (đề xuất).** Điện thoại tải ảnh nặng hơn một chút (khoảng 150–400 KB/ảnh).
- B. Để WordPress tự chọn cỡ nhỏ cho điện thoại (`srcset`). Trang nhẹ hơn, nhưng các cỡ nhỏ WordPress tạo ra **không còn GPS**.

## Đối chiếu tiêu chí xong

- [x] Báo cáo đủ 8 mục, có thử nghiệm EXIF/GPS sau khi nén WebP (phần Bằng chứng, thử 2–5)
- [x] Không thay đổi code, cấu hình, test (`git diff --stat origin/main` chỉ có file này)
- [x] Đẩy báo cáo lên `team/T-046`

## Rủi ro và điểm cần chú ý

- **Mất GPS âm thầm:** thiếu một tham số `exif=` là mất GPS (thử 2). Đã đưa vào thiết kế: kiểm sau nén và test bắt buộc ở G3-3.
- **Ảnh công khai trước bài:** media WordPress xem được ngay qua đường dẫn, kể cả khi bài là nháp. Ảnh có GPS của nhà khách sẽ công khai từ lúc tải lên. Đã chốt giữ GPS (sổ rủi ro mục 6); thiết kế chỉ tải lên khi bấm "Gửi nháp".
- **Site có thể xóa EXIF:** plugin nén ảnh hoặc CDN. Việc chủ dự án làm: sau lần gửi thật đầu tiên, tải file ảnh từ web về và kiểm GPS (Thợ Máy có thể viết script kiểm, chỉ đọc).
- **Tài liệu hãng AI thay đổi nhanh:** tên mô hình tạo ảnh, giá, cách gọi (Gemini chuyển sang Interactions API). Các số ở mục 3, 4 đọc ngày 2026-10-17; phải xác minh lại khi làm G3-4, G3-7.
- **Chưa thử với ảnh thật:** ảnh iPhone thật (MakerNote, XMP, MPO, ảnh nhỏ nhúng trong EXIF), Drive "chỉ trực tuyến", dung lượng WebP thật. G3-3 cần vài ảnh mẫu do chủ dự án chọn, ảnh mẫu **không commit** vào repo (2.9).
- Google có dùng GPS trong EXIF để xếp hạng hay không: chưa xác minh. Không ảnh hưởng thiết kế, vì việc giữ GPS đã được chốt.

## Đề xuất

- `config/ai.toml` thuộc phạm vi của Ngòi Bút, nên tách G3-5 riêng. Nếu muốn ít phiếu hơn, Chỉ Huy có thể cho Thợ Máy sửa file này trong G3-4.
- Khi mở `class` trong `sanitize.py` (G3-8), Lá Chắn nên soát riêng thay đổi đó.

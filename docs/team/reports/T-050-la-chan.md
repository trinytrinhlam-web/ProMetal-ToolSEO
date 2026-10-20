# Biên bản bảo mật T-050 · Lớp AI đọc ảnh, gợi ý alt (G3-4)

> **Model:** chạy tạm Claude Opus 5.5 vì tài khoản không dùng được Fable (chủ dự án đã duyệt). **Sau 01/11 phải kiểm lại bằng Fable.**

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-050](../tickets/T-050-lop-ai-doc-anh-goi-y-alt.md) |
| Phạm vi | Diff `origin/main...team/T-050` tại `dc97e0c` (merge-base `ffaa1e6`, 19 commit): `seo_app/ai/base.py`, `anthropic_provider.py`, `openai_provider.py`, `gemini_provider.py`, `registry.py`, `seo_app/images/alt.py`, `seo_app/images/__init__.py` (rỗng), `tests/fake_ai.py`, `tests/test_ai_images.py`, `tests/test_soi_loi_t050.py`, 2 báo cáo. Đọc thêm code xung quanh: `seo_app/sanitize.py` (`clean_ai_text`), `seo_app/content/prompts.py` (`_block`), `seo_app/onpage/meta.py` (`normalize_meta`), `tests/conftest.py` |
| Ngày | 2026-10-20 |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** (0 Nghiêm trọng/Cao/Trung bình; 4 Thấp LC-T050-1 → -4; không chặn gộp) |

## Tóm tắt (cho chủ dự án)

Gộp được. Lớp gửi ảnh cho AI làm đúng điều quan trọng nhất: ảnh chỉ đi thẳng tới máy chủ chính thức của hãng, không kèm tên file hay đường dẫn trên máy; ảnh còn GPS, EXIF hay ghi chú do điện thoại, máy ảnh, phần mềm ghi vào đều bị từ chối; thẻ ảnh trông như đường dẫn máy bị bỏ; chữ AI trả về được lọc và cắt ngắn. Còn 4 điểm nhỏ (mức Thấp): hồ sơ màu trong ảnh có thể mang tên, đời màn hình tới AI; ảnh **cố tình** dựng vẫn giấu được dữ liệu; 2 chú thích trong code hứa nhiều hơn khả năng thật; và nếu sau này đổi việc viết alt sang Gemini bằng khóa miễn phí thì Google được dùng ảnh. Cách xử lý: phiếu xử lý ảnh T-049 bỏ hồ sơ màu khỏi bản gửi AI, một phiếu dọn nhỏ sửa lớp kiểm trước khi làm giao diện ảnh (T-056), và README ghi rõ nên dùng khóa trả phí nếu đổi hãng cho việc alt.

## Lỗi phát hiện

Không có lỗi Nghiêm trọng, Cao hay Trung bình. 4 lỗi **Thấp**; LC-T050-1 và LC-T050-2 là SL-T050-5 và SL-T050-6 của Soi Lỗi, Lá Chắn xác nhận lại và bổ sung đường đi.

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T050-1 (= SL-T050-5) | Thấp | Hồ sơ màu ICC (JPEG APP2, PNG `iCCP`, WebP `ICCP`) chỉ được kiểm 132 byte đầu; phần còn lại, kể cả các thẻ chữ của một hồ sơ **đúng khuôn hoàn toàn**, đi nguyên tới hãng AI | `seo_app/ai/base.py:563–569` (`_icc_ok`), `:609–618`, `:700–714` | Ảnh gốc có hồ sơ màu mang chữ (hồ sơ màn hình đã cân màu, ảnh chụp màn hình; thẻ `desc`/`dmnd`/`dmdd`/`cprt`/`meta`) → T-049 lưu bản gửi AI dạng **PNG** mà không xóa `info`: Pillow 12.3 **và** 13.0 tự chép hồ sơ màu (thử P10) → `prepare_images` nhận → tên, đời, có thể cả số seri màn hình hoặc tên người đặt hồ sơ tới máy chủ hãng AI. Ảnh dựng cố ý thì chở được cả GPS (P1) | Cách **(a)**: bản gửi AI **không** kèm hồ sơ màu; `prepare_images` từ chối mọi APP2 ICC / `iCCP` / `ICCP`. Không chuyển màu bằng `ImageCms` (sẽ đưa hồ sơ chưa tin cậy vào thư viện C LittleCMS) |
| LC-T050-2 (= SL-T050-6, mở rộng) | Thấp | Đọc cấu trúc không chặn được ảnh **dựng cố ý**: ngoài các khối lặp/dài hơn khuôn Soi Lỗi nêu, còn khối DAC dài tùy ý, DQT lặp chở chữ, chữ thô trong dữ liệu quét JPEG, CRC của `IDAT` rỗng, dữ liệu sau dòng nén `IDAT`, đuôi chunk `VP8L` | `base.py:572–578`, `:621–661`, `:690–693`, `:758–790` | Chỉ có khi ai đó **cố ý** dựng file rồi đặt vào thư mục ảnh của chủ dự án; người nhận là hãng AI, kẻ dựng file không đọc được; T-049 dựng lại từ điểm ảnh thì mất hết. Không phần mềm thật nào tự sinh các dạng này | Gom vào phiếu dọn: làm theo gợi ý SL-T050-6, bỏ thêm DAC và khung ảnh ngoài SOF0/1/2 (Pillow không ghi). Không cần (và không thể) chặn hết: chấp nhận giới hạn, ghi đúng trong chú thích (LC-T050-3) |
| LC-T050-3 | Thấp | Chú thích nói quá khả năng lớp kiểm: "khối được nhận phải đúng khuôn… (không còn chỗ nhét chữ tự do)"; "độ dài cố định và nhỏ, không chứa chữ tự do" | `base.py:552–556`, `:686–687` | Người làm T-049 (hoặc người kiểm sau) đọc chú thích, tin lớp kiểm đã đủ, nên để Pillow tự chép hồ sơ màu hay bỏ bước dựng lại từ điểm ảnh → LC-T050-1 thành đường thật | Viết lại 2 chú thích theo mẫu ở mục LC-T050-3 bên dưới |
| LC-T050-4 | Thấp | `[tasks.alt]` đổi được sang Gemini (không có hãng mặc định). Khóa Gemini **gói miễn phí**: Google được dùng nội dung gửi lên để cải tiến sản phẩm và người duyệt có thể đọc | `seo_app/images/alt.py:262` (`ai.get(ALT_TASK)`), `config/ai.toml` | Chủ dự án đổi `[tasks.alt]` sang `gemini` với khóa miễn phí → ảnh công trình (nhà khách, số nhà, người trong ảnh) tới Google kèm quyền dùng lại | Ghi rõ trong README / Cài đặt: việc alt dùng Claude (mặc định 4A) hoặc khóa trả phí; chủ dự án muốn dùng Gemini miễn phí thì ghi sổ rủi ro |

### LC-T050-1 · Hồ sơ màu ICC chở chữ (xác nhận SL-T050-5, bổ sung đường đi thật)

**Thử lại (script tạm trong scratchpad, không commit; chạy với Pillow 12.3.0 của nhánh và Pillow 13.0.0 của bản gộp với `team/T-058`, kết quả giống hệt):**

| Ca | Cách dựng | `prepare_images` |
|---|---|---|
| P1 | Hồ sơ 132 byte đầu hợp lệ + đuôi TIFF thô `MM\0*` chứa `GPS 16.0544N 108.2022E; D:/Anh/Nha anh Tuan 12 Le Loi/IMG_0001.jpg`, đặt vào JPEG / PNG / WebP | QUA cả 3 |
| P2 | Hồ sơ ICC v4 **đúng khuôn hoàn toàn**: bảng 4 thẻ, mọi byte thuộc một thẻ, không đuôi; chữ nằm trong thẻ `desc` ("Nha anh Tuan 12 Le Loi - GPS…"), `dmdd` ("DELL U2720Q serial CN0ABC1234"), `cprt` | QUA cả 3 |
| P10 | Ảnh gốc JPEG có hồ sơ P2 → `Image.open` → `resize` → `save` **không** truyền `icc_profile` | JPEG, WebP: Pillow không chép hồ sơ. **PNG: Pillow tự chép hồ sơ** (có `iCCP`) → QUA |
| P11 | Như P10 nhưng dựng ảnh mới rồi `paste` điểm ảnh (cách T-049 nên làm) | QUA, không còn hồ sơ màu ở cả 3 định dạng |

**Đánh giá mức:** Thấp, đồng ý với Soi Lỗi. Hồ sơ của máy ảnh, điện thoại (sRGB, Display P3) là hồ sơ chuẩn, không có GPS hay dữ liệu khách. Thứ lọt được qua đường thật (P10) là thông tin **thiết bị** (tên, đời, có thể số seri màn hình, tên người đặt cho hồ sơ), không phải vị trí công trình. Đây là suy luận theo cấu trúc ICC, chưa thử với hồ sơ màn hình thật. GPS chỉ lọt khi có người cố ý dựng file (P1).

**Chọn (a) hay (b): chọn (a)**, biến thể "bỏ hồ sơ, không chuyển màu":

- (b) không đủ: P2 là hồ sơ đúng khuôn tuyệt đối mà vẫn chở chữ trong `desc`/`dmdd`. Muốn chặn phải đọc nội dung từng thẻ, tức viết thêm một bộ đọc ICC trong code an toàn: thêm mã, thêm chỗ sai.
- (a) bỏ hẳn một đường đi và **xóa bớt code**: `_icc_ok`, `_jpeg_icc_ok`, `_check_png_icc` và lần giải nén zlib duy nhất của lớp kiểm (chỗ phải chống bom giải nén) không còn cần.
- AI viết alt không cần màu chính xác tuyệt đối: ảnh Display P3 đọc như sRGB chỉ nhạt màu đi một chút, vẫn nhận ra "cổng xanh", "cửa cuốn màu bạc".
- **Không** dùng `ImageCms.profileToProfile` để đổi sang sRGB: làm vậy đưa hồ sơ màu chưa tin cậy từ ảnh gốc vào LittleCMS (thư viện C). Bỏ hồ sơ thì không phải đọc nó.
- Thay đổi này đổi thiết kế T-046 mục 3 / ghi chú `base.py:582–584` ("ảnh iPhone Display P3 mất hồ sơ thì màu sai"), cần Chỉ Huy duyệt; không đụng quyết định nào của chủ dự án (2A nói về EXIF của **bản đăng web**, không nói về bản gửi AI). Bản đăng web (WebP 1600 px) vẫn giữ hồ sơ màu như cũ.

### LC-T050-2 · Ảnh dựng cố ý (xác nhận SL-T050-6, mở rộng)

**Thử thêm ngoài 15 ca `xfail` của Soi Lỗi** (cùng script, Pillow 12.3.0 và 13.0.0): JPEG 9 khối APP0 lặp (P3), khối DAC chở chữ (P4), DQT bảng số 3 không dùng chở chữ (P5), chữ thô trong dữ liệu quét (P6); PNG 17 khối `IDAT` rỗng mà CRC chở chữ (P7), `IDAT` có TIFF thô sau dòng nén (P8); WebP `VP8L` có chữ sau dòng bit (P9). **Tất cả QUA.**

**Đánh giá mức:** Thấp, đồng ý với Soi Lỗi. Mọi chỗ trên đều nằm trong phần **phải** nhận để giải mã ảnh (dữ liệu quét, bảng lượng tử, dữ liệu nén), nên đọc cấu trúc không bao giờ chặn hết được; sửa SL-T050-6 chỉ bịt các chỗ "có khuôn", không đóng được cả lớp này (P5–P9 vẫn qua sau khi sửa). Muốn khai thác phải ghi được file vào thư mục ảnh của chủ dự án, và cái lợi duy nhất là đưa dữ liệu tới hãng AI (kẻ dựng file không đọc lại được). Bảo vệ thật là T-049 dựng bản gửi AI lại từ điểm ảnh (P11).

**Sửa (gom vào phiếu dọn, rẻ):** theo gợi ý SL-T050-6 (APP0, APP14 tối đa một lần; SOF đúng 6 + 3·số thành phần, SOS đúng 4 + 2·số thành phần, DRI, DNL đúng 2 byte; PNG `PLTE` chỉ với loại màu 3, `tRNS` đúng độ dài theo loại màu, bỏ `cHRM`, `sBIT`, `bKGD`), cộng thêm: bỏ DAC (`0xCC`) và chỉ nhận khung ảnh SOF0/SOF1/SOF2 (Pillow chỉ ghi các loại này; SOF3, SOF5–7, SOF9–15 là ảnh không tổn hao, phân cấp, mã số học). Không cần giới hạn số khối DQT/DHT (dữ liệu quét đã là kênh không giới hạn).

### LC-T050-3 · Chú thích nói quá khả năng lớp kiểm

Soi Lỗi nói đúng. `base.py:552–553` hứa "khối được nhận phải đúng khuôn của nó (không còn chỗ nhét chữ tự do)"; `:686–687` nói các chunk PNG phụ "độ dài cố định và nhỏ, không chứa chữ tự do" (`cHRM` 32 byte, `pHYs` 8 byte tự do đủ chứa một cặp tọa độ GPS). Báo cáo Thợ Máy lượt 2 cũng viết "không còn chỗ nhét GPS hay đường dẫn". Câu `:555–556` ("Không kiểm được dữ liệu giấu bên trong phần ảnh nén hay bên trong nội dung hồ sơ màu") thì đúng nhưng đặt sau lời hứa nên dễ bị đọc lướt.

Mẫu thay cho `base.py:552–556` (Thợ Máy chỉnh câu chữ tùy ý, giữ ý):

> Kiểm theo DANH SÁCH CHO PHÉP: chặn metadata do phần mềm thật ghi (EXIF, XMP, IPTC, chú thích, khối riêng của hãng máy ảnh…) và mọi loại khối chưa biết. **Không** chống được ảnh dựng cố ý: dữ liệu vẫn giấu được trong phần ảnh nén, bảng giải mã và các trường cố định (mật độ điểm ảnh…). Bảo đảm thật là bản gửi AI được dựng lại từ điểm ảnh, không kèm hồ sơ màu (T-049); lớp này chỉ là lưới cuối.

Và `:686–687`: bỏ vế "không chứa chữ tự do", thay bằng "Pillow chỉ ghi các chunk này khi được yêu cầu; giữ để không từ chối nhầm".

### LC-T050-4 · Điều khoản dữ liệu khi đổi việc alt sang hãng khác (A3)

- Anthropic (mặc định 4A): trang Vision, mục FAQ, ghi Anthropic không dùng ảnh tải lên để huấn luyện mô hình và ảnh không được lưu quá thời gian xử lý yêu cầu (đọc 2026-10-20).
- Gemini API (điều khoản cập nhật 2026-04-28): gói **miễn phí** cho Google dùng nội dung gửi lên để cải tiến sản phẩm, và "human reviewers may read, annotate, and process your API input and output"; gói **trả phí** thì không dùng để cải tiến sản phẩm, chỉ lưu tạm để chống lạm dụng.
- Code không biết khóa thuộc gói nào, nên không chặn bằng code được. Cách xử lý là tài liệu + quyết định của chủ dự án (xem mục Điều kiện).

### Khuyến nghị: sửa ngay ở lượt nhỏ của T-050 hay gom phiếu dọn?

**Gom vào một phiếu dọn riêng, không chặn gộp T-050**, với hai ràng buộc:

1. **Nửa quan trọng của LC-T050-1 làm ngay ở T-049** (phiếu chưa bắt đầu, chỉ cần chép điều kiện): bản gửi AI dựng lại từ điểm ảnh, **không** kèm hồ sơ màu, xóa `info`; test khẳng định bản gửi AI qua `prepare_images` và không có APP2 ICC / `iCCP` / `ICCP`, kể cả khi ảnh gốc có hồ sơ màu mang chữ (như P10). Như vậy ngay cả khi T-050 còn nhận hồ sơ màu, đường thật đã đóng ở nguồn.
2. **Phiếu dọn phải gộp trước T-056** (phiếu đầu tiên gửi ảnh thật của chủ dự án tới AI), và trong mọi trường hợp trước khi hết Giai đoạn 3. Phiếu dọn gồm: LC-T050-1 phần `prepare_images` (cách a), LC-T050-2 (SL-T050-6 + DAC/SOF), LC-T050-3 (chú thích). 15 test `xfail(strict=True)` của Soi Lỗi bảo đảm phiếu không bị quên: sửa xong chúng báo XPASS và phải gỡ dấu; 6 ca ICC của Soi Lỗi sẽ qua theo cách (a) vì mọi hồ sơ màu đều bị từ chối. Các ca có hồ sơ màu trong những test đang đòi ảnh có ICC phải qua (`test_allowed_blocks_in_right_shape_pass`, `test_pillow_images_of_every_kind_pass`, `test_clean_pillow_images_with_icc_pass`…) đổi thành "bị từ chối"; Chỉ Huy duyệt việc đổi test này.

Lý do không sửa ngay ở T-050: hiện **chưa có đường gọi nào** đưa ảnh thật tới `suggest_alt` (giao diện là T-056, bản gửi AI là T-049, cả hai chưa làm), nên cửa sổ rủi ro chưa mở; một lượt nữa của T-050 kéo theo một vòng Soi Lỗi + Lá Chắn và giữ chân chuỗi T-051 → T-062 → T-053 đang chờ T-050 gộp; phần sửa ở phiếu dọn đụng `base.py` + test, không đụng file của T-049, nên làm song song được. Nếu Chỉ Huy muốn làm ngay thì cũng ổn: khoảng 30 dòng code, Lá Chắn chỉ cần kiểm lại rút gọn.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` trên 12 file của diff: 0 phát hiện; trên toàn bộ patch `git log -p origin/main..team/T-050` (19 commit, 248 KB): 0 phát hiện (đã thử chuỗi mồi AWS + `password=` trong cùng lần quét: bắt đủ 2, tức công cụ có đọc file). Soát tay lịch sử: chuỗi giống khóa duy nhất là khóa giả `sk-ant-api03-T050KhoaGia_…`, `sk-proj-T050KhoaGia_…`, `AIzaSyT050KhoaGia_…` (`tests/test_ai_images.py:64–66`, dùng để kiểm câu lỗi không chép khóa, cùng kiểu các phiếu trước). Dữ liệu "Nha anh Tuan 12 Le Loi", GPS 16.0544N 108.2022E trong test là dữ liệu giả (Lá Chắn T-046 đã xác nhận: trung tâm thành phố, không phải một nhà). Không ảnh thật nào được commit (ảnh trong test đều tạo bằng Pillow lúc chạy) |
| S2 | Đạt | Câu báo ảnh cố định, không chép dữ liệu ảnh, MIME hay đường dẫn: `base.py:458–468`; câu "quá lớn" chỉ có con số (`:522–531`). `ImageInput.__repr__` không in bytes (`:483–485`, test `tests/test_ai_images.py:175`). Lỗi máy chủ khi có ảnh vẫn đi đường câu cố định cũ (`bad_request_error`, `base.py:406–429`): `test_400_with_images_is_fixed_message` (`tests/test_ai_images.py:804`) và Soi Lỗi thử 400/413/422/500 × 3 hãng với câu máy chủ chứa khóa giả và base64 ảnh: không chép. Không có `logging`/`print` trong `seo_app/ai`, `seo_app/images` (grep rỗng). Địa chỉ máy chủ cố định giữ nguyên: `anthropic_provider.py:48`, `openai_provider.py:67`, `gemini_provider.py:122`; fixture `network` (`tests/test_ai_images.py:646`) đặt `*_BASE_URL=https://evil.example/` + `*_CUSTOM_HEADERS` mà `assert_official` (`:706`) vẫn thấy đúng máy chủ chính thức, `https`, không header lạ. Ảnh gửi thẳng trong yêu cầu, không Files API, không URL: `anthropic_provider.py:159–179` (khối `base64`), `openai_provider.py:165–184` (`data:` URL), `gemini_provider.py:258–274` (`Part.from_bytes`) |
| S3 | Không áp dụng | Không có biến môi trường mới: diff không có `os.environ`/`getenv`; `.env.example` không đổi (`git diff --stat` rỗng) |
| W1 | Không áp dụng | Phiếu không đụng `seo_app/wordpress/`, `app/` (`git diff --stat origin/main...team/T-050 -- seo_app/wordpress app` rỗng). Alt chỉ là gợi ý trả về cho code gọi |
| W2 | Không áp dụng | Như W1: không có lời gọi WordPress nào |
| W3 | Không áp dụng (điều kiện cho T-054) | Phiếu này không gửi HTML. Alt/chú thích AI đã qua `clean_ai_text` (`alt.py:217–230`), nhưng còn ký tự rộng 0 và escape Markdown: T-054 phải gỡ rồi `html.escape(…, quote=True)` trước khi ghi vào `<img alt>`/`<figcaption>` (mục Điều kiện) |
| W4 | Đạt (phần AI) | 3 hãng: địa chỉ `https://` chính thức cố định (S2); `timeout` OpenAI `openai_provider.py:67`, Gemini `gemini_provider.py:122`; Anthropic dùng thời hạn mặc định của thư viện như trước (không đổi ở phiếu này). Không có `verify=False`. Kích thước yêu cầu: tối đa 4 ảnh × 5 MB, tổng 10 MB (`base.py:454–456`) → base64 tối đa 6,7 MB/ảnh, 13,3 MB/yêu cầu: dưới giới hạn Anthropic 10 MB/ảnh (tính sau base64) và 32 MB/yêu cầu (trang Vision, đọc 2026-10-20), dưới 20 MB gửi thẳng của Gemini. Băn khoăn số 2 của Soi Lỗi ("5 MB tính trên base64?") đã có lời đáp: không vấn đề |
| A1 | Đạt | Thẻ và từ khóa nằm trong khung `<du_lieu_tham_khao>` (`alt.py:191–199`, dùng `_block` có vô hiệu thẻ khung); lời dặn hệ thống nói chữ trong ảnh và trong khung là dữ liệu (`alt.py:82–84`). Chữ kiểm = chữ gửi: `_short_text` chạy NFKC + bỏ ký tự điều khiển, vô hình **trước** khi kiểm (`alt.py:130–143`), đúng phép `_neutralize` của khung làm; danh sách cho phép ký tự (`:106`, `:120–123`) và quy tắc đường dẫn (`:111–117`, `:126–127`). SL-T050-1 đã sửa thật: `test_tag_cannot_close_data_frame` (`tests/test_ai_images.py:1034`), `test_random_tags_reach_ai_exactly_as_checked` (`tests/test_soi_loi_t050.py:976`), `test_real_paths_and_file_names_are_dropped` (`:970`, Drive Windows/Mac, OneDrive, NAS, USB, toàn chiều rộng). `guidance` (quy tắc của chủ dự án trong `config/`) đặt ngoài khung (`alt.py:163–169`): đúng, vì là cấu hình tin cậy, không phải dữ liệu ngoài. Còn lại ngoài phạm vi phiếu: thẻ một dấu `/` như `Users/Lam` được gửi (thiết kế SL-T050-4); T-052 chỉ được đưa phần thư mục **dưới** thư mục ảnh đã khai báo (mục Điều kiện) |
| A2 | Đạt | Việc alt luôn tắt tìm web (`alt.py:263–265`), nên không hãng nào nhận công cụ: `anthropic_provider.py:94`, `openai_provider.py:120–121`, `gemini_provider.py:220–221` chỉ thêm công cụ khi bật. Kết quả AI: kiểm khuôn (`alt.py:273–274`), lọc HTML/link, gộp một dòng, cắt ≤ 125/200 ký tự, alt rỗng sau lọc là lỗi (`:217–238`). Đầu-cuối 3 hãng bằng thư viện thật + mạng giả: `tests/test_soi_loi_t050.py:598`. Chữ trong ảnh vẫn có thể khiến AI chép số điện thoại, tên người vào alt: lời dặn cấm (`alt.py:85–86`), người dùng duyệt ở T-056 (mục Điều kiện) |
| A3 | Đạt, kèm LC-T050-1 → -4 (Thấp) | `ImageInput` chỉ có bytes + MIME (`base.py:474–487`); `prepare_images` từ chối chuỗi, `Path`, bytes trần, dict (`:502–515`, test `tests/test_ai_images.py:204`); ảnh kiểm trước mọi lời gọi mạng (`anthropic_provider.py:61`, `openai_provider.py:81`, `gemini_provider.py:137`, `alt.py:261`). Danh sách cho phép khối ảnh (`base.py:552–790`): EXIF, XMP, IPTC, chú thích, khối riêng của hãng, mọi khối lạ đều bị từ chối (39 test SL-T050-2 qua; 0/965 ảnh Pillow sạch bị chặn nhầm theo Soi Lỗi). Ảnh AI bỏ hết thẻ (`alt.py:180`). Còn lại: hồ sơ màu chở chữ (LC-T050-1), ảnh dựng cố ý (LC-T050-2), chú thích nói quá (LC-T050-3), gói Gemini miễn phí (LC-T050-4). Nội dung điểm ảnh tới hãng AI là chủ đích (quyết định 4A); chỉ ảnh người dùng chọn đăng mới nên được gửi (điều kiện T-056) |
| U1 | Không áp dụng (điều kiện cho T-056) | Phiếu không có giao diện; diff không có `unsafe_allow_html`. T-056 hiện alt bằng ô nhập chữ hoặc `escape_markdown`, không HTML |
| U2 | Không áp dụng | Không thêm trang. `.streamlit/config.toml:5` vẫn `address = "localhost"` |
| U3 | Không áp dụng | Không đụng đăng nhập, mật khẩu |
| F1 | Đạt | Phiếu không mở file nào: `ImageInput` nhận bytes, từ chối đường dẫn (`base.py:502–515`); `Path(`/`open(` trong diff chỉ có ở test (dữ liệu thử "đường dẫn khách" và ảnh HEIC tạo trong bộ nhớ). Đọc file ảnh thật là việc của `ImageLibrary.read_image_bytes` (T-048, đã gộp) |
| F2 | Đạt | Giới hạn số ảnh, dung lượng từng ảnh và tổng (`base.py:454–456`, `:506–531`); giải nén hồ sơ màu PNG có trần 5 MB (`:707`, Soi Lỗi thử bom 1 GB: từ chối sau 0,03 giây). GPS: bản gửi AI **không** được mang GPS (A3) và lớp kiểm bảo đảm điều đó với ảnh do phần mềm thật tạo; giữ GPS ở bản đăng web là việc T-049, không đổi ở đây |
| F3 | Đạt | Không `eval`, `exec`, `pickle`, `yaml.load`, `subprocess` trong diff (grep rỗng); `zlib.decompressobj().decompress(…, max_length)` có giới hạn; không ghi file. Chữ tiếng Việt chỉ nằm trong mã nguồn UTF-8 |
| D1 | Đạt | `uv.lock`, `pyproject.toml` không đổi (`git diff --stat` rỗng); không nâng `google-genai` (2.30.1 vẫn chạy `generate_content` kèm ảnh, YC3). `pip-audit` trên 69 gói ghim: 0 (PyPI và OSV). Pillow 12.3.0 của nhánh còn các khuyến cáo tháng 10 mà cơ sở dữ liệu của pip-audit chưa có (LC-T058-4); đã có T-058 nâng Pillow 13, và test ảnh của phiếu này qua trên Pillow 13 (mục Thử gộp) |
| D2 | Đạt | `.gitignore` không đổi; vẫn chặn `.env`, `.env.*` (trừ `.env.example`), `*service-account*.json`, `secrets/`, `.venv/`, `data/`, `*.sqlite` |
| D3 | Đạt | Test 3 hãng dùng thư viện thật với `httpx.MockTransport` / `httpx2.MockTransport` (`tests/test_ai_images.py:646–680`); bộ chặn mạng chung vẫn chạy (`tests/conftest.py:19`) và cả bộ test qua dưới nó. Không có lời gọi AI, WordPress, Google thật |

## Kết quả công cụ quét

Máy Windows 11 của chủ dự án, worktree `wt-T-050` tại `dc97e0c` (trước khi thêm biên bản), 2026-10-20.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit 2.10.1 | `uv export --frozen --no-hashes --no-emit-project` → 69 gói ghim (`anthropic==1.13.0`, `openai==3.31.0`, `google-genai==2.30.1`, `pillow==12.3.0`, `pillow-heif==1.8.1`). Nguồn PyPI: `No known vulnerabilities found`. Nguồn OSV (`-s osv`): `No known vulnerabilities found` | Có. `uv.lock` không đổi so với `main`, nên kết quả giống `main`. Lưu ý LC-T058-4: cơ sở dữ liệu chưa có các khuyến cáo Pillow tháng 10; việc đó đã được T-058 xử lý (Pillow 13) |
| bandit 1.9.4 | `-r seo_app app scripts`: 8.139 dòng, 1 mục Thấp (B101 `assert`, `seo_app/storage/drafts.py:203`) | Có. Có từ trước, không thuộc phiếu này. 0 mục trong file của T-050 |
| detect-secrets 1.5.0 | 12 file của diff: 0. Patch toàn nhánh: 0 (chuỗi mồi trong cùng lần quét bị bắt đủ). `--all-files`: 411 mục, tất cả trong `.venv/`, `.pytest_cache/`, `.ruff_cache/` (không theo dõi bởi git), trừ `tests/test_config.py:34` | Có. `tests/test_config.py:34` là mật khẩu giả `"abcd efgh"` của test cấu hình cũ, T-050 không đổi file này |
| Soát lịch sử git | `git log -p origin/main..team/T-050` grep `api[_-]?key\|password\|secret\|token`, `sk-`, `AIza`: chỉ thấy khóa giả `…KhoaGia…` (`tests/test_ai_images.py:64–66`) và biến test `SECRET` chứa địa chỉ, GPS giả | Có |
| pytest 9.1.1 (worktree) | `1 failed, 7659 passed, 11 skipped, 42 xfailed, 1 warning in 892.14s (0:14:52)`. Hỏng: `tests/test_soi_loi_t037.py::test_r2_long_lock_in_other_thread_is_busy_not_deleted` (`DID NOT RAISE SiteIndexError`) | Có. Test khóa SQLite với thời hạn 0,1 giây của T-037, không thuộc phiếu này; máy đang chạy song song bộ test khác. Chạy riêng lại 3 lần: `1 passed` cả 3; cả file `139 passed`. 42 xfail = 27 của phiếu khác + 15 `xfail(strict=True)` SL-T050-5/-6. Cảnh báo là của test cũ `test_soi_loi_t028.py` (pydantic), như các lượt trước |
| pytest (bản gộp `main` + T-050, Pillow 12.3.0) | Cây `1980948` (`git archive` ra thư mục tạm, `uv sync --frozen --offline`): `7911 passed, 17 skipped, 45 xfailed, 1 warning in 888.69s (0:14:48)`, **0 hỏng**. Riêng `tests/test_ai_images.py` + `tests/test_soi_loi_t050.py` với `-rs`: `490 passed, 15 xfailed`, không test nào bị bỏ qua | Có. Đây là đúng bản sẽ lên `main`. Số bỏ qua, xfail nhiều hơn worktree là test của các phiếu đã gộp vào `main` sau khi nhánh tách (T-048…), không thuộc T-050 |
| pytest (bản gộp `team/T-058` + T-050, Pillow 13.0.0) | `tests/test_ai_images.py` + `tests/test_soi_loi_t050.py`: `490 passed, 15 xfailed in 58.81s` | Có. Danh sách cho phép không chặn nhầm ảnh Pillow 13; 15 ca lỗi Thấp vẫn đúng là lỗi (không XPASS) |
| ruff 0.16.10 | `All checks passed!` | Có |

## Báo nhầm đã loại

- bandit B101 (`assert` ở `seo_app/storage/drafts.py:203`): code cũ, ngoài phạm vi; không phải chỗ kiểm an toàn.
- detect-secrets: 410 mục trong thư mục thư viện và bộ nhớ đệm không thuộc repo; `tests/test_config.py:34` là dữ liệu giả của test.
- Khóa `sk-…KhoaGia…`, `AIza…KhoaGia…` trong test: khóa giả để kiểm câu lỗi không chép khóa.
- Test T-037 hỏng một lần khi máy quá tải: chạy riêng qua 3/3. Ghi nhận cho Soi Lỗi: test này phụ thuộc thời gian (thời hạn 0,1 giây), có thể đỏ oan khi chạy song song nhiều bộ test (giống ghi chú T-025).

## Thử gộp

`git merge-tree --write-tree` (không đụng thư mục làm việc, không tạo ref):

| Gộp | Kết quả |
|---|---|
| `origin/main` (`97ec6b5`) + `team/T-050` | Sạch, cây `1980948`. `seo_app/images/__init__.py` lấy bản của `main` (T-048, blob `04c33dd`, có docstring); file rỗng của T-050 tự biến mất vì bản rỗng không thêm dòng nào. Khớp ghi chú của Lá Chắn T-048 |
| `origin/team/T-058` + `team/T-050` | Sạch, cây `1961d9d` (Pillow 13.0.0); test ảnh qua (bảng trên) |
| `origin/team/T-051` + `team/T-050` | Sạch, cây `5af3f81` |

Thứ tự gộp nào cũng được. Gộp T-058 trước hay sau, chạy lại `tests/test_ai_images.py tests/test_soi_loi_t050.py` trên bản gộp (đã làm ở đây: qua).

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

Không điều kiện nào chặn gộp T-050. Chỉ Huy chép vào phiếu tương ứng:

1. **Phiếu dọn mới (Thợ Máy), gộp trước T-056 và trước khi hết Giai đoạn 3:** "Dọn lỗi Thấp lớp ảnh gửi AI (LC-T050-1/-2/-3, SL-T050-5/-6)". Phạm vi `seo_app/ai/base.py`, `tests/test_ai_images.py`, `tests/test_soi_loi_t050.py` (gỡ 15 dấu `xfail` khi XPASS). (a) `prepare_images` từ chối mọi hồ sơ màu (JPEG APP2 `ICC_PROFILE`, PNG `iCCP`, WebP `ICCP`), bỏ `_icc_ok`, `_jpeg_icc_ok`, `_check_png_icc` và lần giải nén zlib; (b) sửa theo SL-T050-6, bỏ DAC, chỉ nhận SOF0/1/2; (c) viết lại chú thích `base.py:552–556`, `:686–687` (mẫu ở LC-T050-3). Chỉ Huy duyệt việc đổi thiết kế T-046 mục 3 (bản gửi AI không còn hồ sơ màu) và đổi các ca ICC trong test. Soi Lỗi + Lá Chắn kiểm rút gọn.
2. **T-049 (xử lý ảnh), bắt buộc:** bản gửi AI dựng lại từ điểm ảnh (ảnh mới + dán điểm ảnh, hoặc xóa sạch `info`), **không kèm hồ sơ màu** và không truyền `icc_profile`, `exif`, `comment`, `pnginfo`; **không** dùng `ImageCms` để đổi hồ sơ màu của ảnh gốc. Lưu ý Pillow 12.3 và 13.0 **tự chép** hồ sơ màu khi lưu PNG. Test: ảnh gốc có EXIF + GPS + XMP + COM **và** hồ sơ màu có chữ trong thẻ `desc` → bản gửi AI qua `prepare_images`, không có `ICC_PROFILE`/`iCCP`/`ICCP`/`acsp`, không có chuỗi GPS. Bản đăng web (WebP 1600 px) giữ hồ sơ màu và GPS như thiết kế.
3. **T-056 (giao diện chỗ cần ảnh):** (a) chỉ gọi `suggest_alt` khi người dùng bấm, cho ảnh đã chọn vào bài; **không** gợi ý alt hàng loạt cho cả thư mục (ảnh chưa chọn đăng không được rời máy, A3); (b) alt và chú thích hiện trong ô nhập chữ để người dùng sửa và duyệt trước khi dùng, hoặc qua `escape_markdown`; không `unsafe_allow_html` (U1); (c) lỗi hiện đúng câu `AIError`, không `st.exception`; (d) nên cảnh báo khi alt có dãy số giống số điện thoại (Soi Lỗi rủi ro 5).
4. **T-054 (chèn ảnh vào nháp):** trước khi ghi alt/chú thích vào HTML: `unbreak_autolinks`, gỡ escape Markdown mà `clean_ai_text` thêm (`]\(`…), rồi `html.escape(…, quote=True)`; `<figure>` dựng bằng code và qua `sanitize_html` lần cuối (góp ý Lá Chắn T-046 số 7). `alt_text` gửi qua REST cũng dùng chữ đã gỡ ký tự rộng 0.
5. **T-052 (thẻ ảnh):** chỉ đưa vào thẻ phần tên thư mục **bên dưới** thư mục ảnh đã khai báo (không `Users/…`, `My Drive/…`); thẻ khu vực đối chiếu danh sách quận/huyện cố định (góp ý T-046 số 3). Lớp lọc của T-050 cho qua thẻ một dấu `/` theo thiết kế SL-T050-4, nên không thay được việc này.
6. **README / Cài đặt (Thư Ký hoặc T-062):** ghi một dòng: việc viết alt gửi ảnh công trình cho hãng AI; dùng Claude (mặc định 4A) hoặc khóa **trả phí** của OpenAI/Gemini; khóa Gemini miễn phí cho Google dùng ảnh để cải tiến sản phẩm và người duyệt có thể đọc. Nếu chủ dự án vẫn muốn dùng khóa Gemini miễn phí cho alt: ghi sổ rủi ro (`security.md` mục 6), chủ dự án quyết (LC-T050-4).
7. **Sau 01/11:** kiểm lại phiếu này bằng Fable.

Không cần sửa thêm trong T-050 trước khi gộp.

## Kết luận

**ĐẠT CÓ ĐIỀU KIỆN.** 0 Nghiêm trọng, 0 Cao, 0 Trung bình; 4 Thấp (LC-T050-1 → -4, trong đó LC-T050-1/-2 là SL-T050-5/-6). Hai lỗi Trung bình lượt 1 (SL-T050-1, -2) đã sửa thật: thẻ ảnh kiểm trên đúng chữ gửi AI, ảnh kiểm theo danh sách cho phép. Gộp vào `main` được ngay; điều kiện ở mục trên đi vào T-049, T-052, T-054, T-056, phiếu dọn mới và README.

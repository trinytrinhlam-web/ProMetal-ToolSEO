# Biên bản bảo mật T-050 · Lớp AI đọc ảnh, gợi ý alt (G3-4)

> **Model:** chạy tạm Claude Opus 5.5 vì tài khoản không dùng được Fable (chủ dự án đã duyệt). **Sau 01/11 phải kiểm lại bằng Fable.**

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm) · dưới Chỉ Huy B |
| Phiếu được kiểm | [T-050](../tickets/T-050-lop-ai-doc-anh-goi-y-alt.md) |
| Phạm vi | Diff `origin/main...team/T-050` tại `dc97e0c` (merge-base `ffaa1e6`, 19 commit): `seo_app/ai/base.py`, `anthropic_provider.py`, `openai_provider.py`, `gemini_provider.py`, `registry.py`, `seo_app/images/alt.py`, `seo_app/images/__init__.py` (rỗng), `tests/fake_ai.py`, `tests/test_ai_images.py`, `tests/test_soi_loi_t050.py`, 2 báo cáo. Đọc thêm code xung quanh: `seo_app/sanitize.py` (`clean_ai_text`), `seo_app/content/prompts.py` (`_block`), `seo_app/onpage/meta.py` (`normalize_meta`), `tests/conftest.py` |
| Ngày | 2026-10-20 |
| **Kết luận** | **(đang viết, xem mục Kết luận ở cuối)** |

## Tóm tắt (cho chủ dự án)

_(viết sau cùng)_

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
2. **Phiếu dọn phải gộp trước T-056** (phiếu đầu tiên gửi ảnh thật của chủ dự án tới AI), và trong mọi trường hợp trước khi hết Giai đoạn 3. Phiếu dọn gồm: LC-T050-1 phần `prepare_images` (cách a), LC-T050-2 (SL-T050-6 + DAC/SOF), LC-T050-3 (chú thích). 15 test `xfail(strict=True)` của Soi Lỗi bảo đảm phiếu không bị quên: sửa xong chúng báo XPASS và phải gỡ dấu; 6 ca ICC của Soi Lỗi sẽ qua theo cách (a) vì mọi hồ sơ màu đều bị từ chối. Các test đang đòi ảnh có ICC phải qua (`test_allowed_blocks_in_right_shape_pass`, `test_pillow_images_of_every_kind_pass`, `test_clean_pillow_images_with_icc_pass`…) đổi thành "bị từ chối".

Lý do không sửa ngay ở T-050: hiện **chưa có đường gọi nào** đưa ảnh thật tới `suggest_alt` (giao diện là T-056, bản gửi AI là T-049, cả hai chưa làm), nên cửa sổ rủi ro chưa mở; một lượt nữa của T-050 kéo theo một vòng Soi Lỗi + Lá Chắn và giữ chân chuỗi T-051 → T-062 → T-053 đang chờ T-050 gộp; phần sửa ở phiếu dọn đụng `base.py` + test, không đụng file của T-049, nên làm song song được. Nếu Chỉ Huy muốn làm ngay thì cũng ổn: khoảng 30 dòng code, Lá Chắn chỉ cần kiểm lại rút gọn.

_(Phần 2: danh sách kiểm tra 19 dòng; phần 3: công cụ, thử gộp, điều kiện, kết luận. Đang viết.)_

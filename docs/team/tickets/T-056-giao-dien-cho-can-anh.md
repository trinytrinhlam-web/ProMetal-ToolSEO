# T-056 · Giao diện chỗ cần ảnh (G3-10)

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`) |
| Người giao | Chỉ Huy A |
| Ngày giao | 2026-10-19 |
| Giai đoạn | Giai đoạn 3 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-048 → T-055 đã gộp |
| Trạng thái | Mới |

## Mục tiêu

Thay phần demo "chỗ cần ảnh" trên trang Soạn bài bằng chức năng thật, giữ bố cục chủ dự án đã duyệt.

## Bối cảnh

- Thiết kế: `docs/team/reports/T-046-tho-may.md` (mục 1–7); góp ý Lá Chắn: `docs/team/reports/T-046-la-chan.md`.
- Quyết định chủ dự án 2026-10-19 (`CLAUDE.md`, Quyết định đã chốt): 1A thêm `pillow-heif`; 2A EXIF giữ GPS, ngày chụp, hãng, đời máy, bỏ số seri, tên chủ máy, MakerNote; 3A thẻ ảnh theo tên thư mục Drive, app **không ghi** gì vào Drive; 4A alt bằng Claude Sonnet, tạo ảnh bằng Gemini; 5A ảnh trong bài dùng file đầy đủ 1600 px.
- **Giữ nguyên GPS** trong ảnh tải lên web (sổ rủi ro `security.md` mục 6). Test không gọi mạng thật, dùng ảnh giả tạo trong test (không commit ảnh thật).

## Phạm vi

- **Được sửa:** `app/views/write.py`, `seo_app/demo.py`, `app/assets/style.css`, test giao diện.
- **Không được sửa:** `seo_app/**` (trừ `demo.py`), `config/**`.

## Yêu cầu

1. Chọn thư mục/ảnh, xem trước, duyệt alt (nút viết lại), tạo ảnh AI kèm prompt xem/sửa/sao chép, gửi nháp kèm ảnh.
2. Trước nút Gửi nháp, nói rõ ảnh (có GPS) sẽ xem được công khai qua đường dẫn kể cả khi bài là nháp (góp ý Lá Chắn số 8).
3. Không hiện đường dẫn tuyệt đối; mọi chữ từ AI/WordPress hiện an toàn (U1); `tests/test_app_pages.py` vẫn qua.
4. Xong phiếu này: Thư Ký cập nhật README (khai báo `IMAGE_FOLDERS`, HEIC, GPS); Lá Chắn chạy một lượt toàn Giai đoạn 3.

## Yêu cầu bảo mật riêng

U1, U2; góp ý Lá Chắn T-046 số 8.

## Tiêu chí xong

- [ ] Đạt mọi yêu cầu trên, có test
- [ ] `uv run pytest` (0 hỏng, 0 lỗi trên Windows) và `uv run ruff check .` sạch
- [ ] Báo cáo nộp tại `docs/team/reports/T-056-<mã-agent>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (U1, U2).

## Ghi chú của Chỉ Huy

- Lập từ báo cáo T-046 (G3 tương ứng ở tiêu đề) và quyết định chủ dự án 2026-10-19. Làm trên nhánh tạm `team/T-056`, tạo từ `main`.
- 2026-10-19 (Chỉ Huy A): **Điều kiện từ Soi Lỗi T-048** (`docs/team/reports/T-048-soi-loi.md`): tên file/thư mục lấy từ máy là dữ liệu chưa tin cậy. Hiện tên bằng chữ đã escape và **cô lập hướng chữ** (ký tự RLO U+202E, ký tự rộng 0 có thể làm tên trông khác thật). Giữ kết quả quét trong phiên (hiện mỗi lần chuyển trang quét lại từ đầu). Chạy quét trong luồng riêng để thư mục Drive chậm không làm treo giao diện (báo cáo Thợ Máy T-048 điểm 7).
- 2026-10-20 (Chỉ Huy A): theo Soi Lỗi T-050: chữ trong ảnh (biển hiệu, giấy dán) có thể khiến AI chép số điện thoại hay tên người vào alt. Giao diện **luôn hiện alt để người dùng duyệt** trước khi dùng, không tự áp alt AI.
- 2026-10-20 (Chỉ Huy B): **Điều kiện Lá Chắn T-048** (`docs/team/reports/T-048-la-chan.md`):
  - **Chặn gộp:** trước khi gộp phiếu này (phiếu giao diện đầu tiên gọi `ImageLibrary`), T-063 phải xong: test T-048 đã chạy thật trên Mac hoặc Linux (LC-T048-1, Trung bình).
  - Hiện tên bằng chữ đã escape, cô lập hướng chữ (LC-T048-4 mục b).
  - Không dùng `ImageLibrary._folders`; không hiện đường dẫn tuyệt đối (dùng `roots()`).
  - Chỉ quét khi người dùng mở thư mục hoặc bấm quét lại.
  - Báo cho người dùng khi thư mục gốc đi qua lối tắt (mục "Ghi nhận" của biên bản).
- 2026-10-20 (Chỉ Huy B): **Điều kiện Lá Chắn T-058** (LC-T058-2): xem trước ảnh bằng `st.image` chỉ với ảnh Pillow đã mở qua hàm mở an toàn của module ảnh (T-049) hoặc byte WebP/JPEG do app tạo; không đưa đường dẫn hay byte gốc của file trong thư mục ảnh (Streamlit tự mở bằng Pillow không giới hạn định dạng).
- 2026-10-20 (Chỉ Huy B): **Điều kiện Lá Chắn T-050** (điều kiện 3): (a) chỉ gọi `suggest_alt` khi người dùng bấm, cho ảnh đã chọn vào bài; **không** gợi ý alt hàng loạt cho cả thư mục (ảnh chưa chọn không được rời máy, A3); (b) alt và chú thích hiện trong ô nhập chữ để người dùng sửa, duyệt trước khi dùng, hoặc qua `escape_markdown`; không `unsafe_allow_html` (U1); (c) lỗi hiện đúng câu `AIError`, không `st.exception`; (d) nên cảnh báo khi alt có dãy số giống số điện thoại.
- 2026-10-20 (Chỉ Huy B): **Điều kiện Lá Chắn T-049** (`docs/team/reports/T-049-la-chan.md`, điều kiện 3): `st.image` chỉ nhận byte từ `PreviewCache.get(library, ref)` hoặc `make_preview(...)`; không bao giờ nhận kết quả `open_image`, byte gốc hay đường dẫn. Bắt cả `ImageFolderError` lẫn `ImageProcessError` để hiện câu tiếng Việt; lỗi khác khi xử lý ảnh hiện một câu cố định, không để Streamlit in dấu vết lỗi. Hiện `WebImage.notice` khi có, và "Ảnh không có vị trí GPS" khi `WebImage.gps is None`. Không cho đặt thư mục cache (nếu buộc phải cho thì chặn thư mục nằm trong `IMAGE_FOLDERS` và vẫn qua `_cache_dir_is_ignored`). Phụ thuộc T-067 (LC-T049-2, -3 phải xong trước khi gộp phiếu này).
- 2026-10-20 (Chỉ Huy B): **Điều kiện Lá Chắn T-062** (điều kiện 4): gọi `suggest_alt(..., ai_generated=<theo trường nguồn của ảnh, không theo AI>, rules=load_alt_rules())`; bắt `AIError` (gồm `ContentRulesError`) và hiện bằng `st.error(str(exc))`, không `st.exception`; dựng router với `prepare=("alt",)` hoặc `()`; có test: ảnh AI qua giao diện vẫn ra alt «Minh họa…». Truyền `load_image_settings()` vào `make_web_image` (điều kiện 6 Lá Chắn T-049). Trước khi gộp phiếu này: T-065 (LC-T062-1, C10), T-068 (SL-T062-1 → -3), T-069 (README LC-T050-4) phải xong.
- 2026-10-20 (Chỉ Huy B): **Điều kiện Lá Chắn T-052** (`docs/team/reports/T-052-la-chan.md`, điều kiện 2): (a) lấy thẻ bằng `resolve`/`resolve_many`, không bằng `get`/`get_many`; (b) hiện rõ "Ảnh thật / Ảnh AI" từng ảnh **trước** khi viết alt, một bấm để đổi sang ảnh AI (`ImageTagStore.set(source="ai")`); `ai_generated` của `suggest_alt` và `image_file_name` lấy từ thẻ sau bước này, có test; (c) thư mục gốc có tên cuối mang dấu hiệu AI (`is_ai_name`) thì mọi ảnh trong gốc là ảnh AI, hoặc Cài đặt cảnh báo rõ; (d) `ImageTagStore.recovered_from` chỉ hiện `.name`; (e) `FolderTags.unmatched` chỉ hiện dạng số, chữ tên thư mục hiện đã escape, cô lập hướng chữ; (f) fixture trong `tests/conftest.py` trỏ `DEFAULT_IMAGE_TAGS_FILE` sang thư mục tạm. Trước khi gộp phiếu này: T-070 phải gộp.
- 2026-10-20 (Chỉ Huy B): **Điều kiện Lá Chắn T-054** (điều kiện 4): (a) chỉ truyền thẻ từ `ImageTags` vào `DraftImage`, có test (LC-T054-4); (b) chỉ gọi `create_draft_with_images` khi người dùng bấm «Gửi nháp», nhắc ngay trước nút: ảnh (có GPS) xem được công khai ngay khi tải lên, kể cả khi bài là nháp; (c) hiện `exc.uploaded`, `exc.maybe_uploaded` bằng chữ thường/`escape_markdown`. Trước khi gộp phiếu này: T-061 (LC-T054-1) và T-071 phải gộp. **Điều kiện Lá Chắn T-067** (điều kiện 2): hiện `WebImage.notice` khi có.
- 2026-10-20 (Chỉ Huy B): **Điều kiện Lá Chắn T-070** (điều kiện 2): giữ (a)–(f) của Lá Chắn T-052, thêm (g) gọi `is_ai_name` với `RootInfo.label` (tên lấy từ `Path`, không tự cắt chuỗi đường dẫn) **và** với tên thư mục gốc sau `resolve()`; một trong hai đúng thì mọi ảnh trong gốc là ảnh AI; (h) hiện lý do một ảnh bị coi là ảnh AI ("tên thư mục hoặc tên file có chữ AI / tên công cụ tạo ảnh"), vì người dùng không đổi lại được trong app. Trước khi gộp phiếu này: T-074 phải gộp.
- 2026-10-21 (Chỉ Huy B): **Điều kiện Lá Chắn T-061** (`docs/team/reports/T-061-la-chan.md`, điều kiện 2, LC-T061-4): trước nút «Gửi nháp», tìm và **liệt kê rõ** mọi đoạn dạng shortcode trong tiêu đề, nội dung, đoạn trích, alt, chú thích (cùng quy tắc `_has_shortcode`, xét trên chữ đã gỡ ký tự vô hình), nhắc «WordPress sẽ chạy đoạn này nếu bạn sửa và lưu bài trong trang quản trị; nên xóa»; có test. Hàm tìm công khai đặt ở `seo_app/` (Thợ Máy, T-071 hoặc phần logic riêng). Chỉ Huy xác nhận `TIEN-DO.md` mục 4b (Code Snippets ≥ 3.9.2) trước khi bật nút. Trước khi gộp phiếu này: T-075 (`certifi`) phải gộp.
- 2026-10-21 (Chỉ Huy B): **Điều kiện Lá Chắn T-055** (`docs/team/reports/T-055-la-chan.md`, điều kiện 2): (a) **LC-T055-1** không bao giờ gọi `ImageLibrary.list_folder` với thư mục lấy từ nháp (`chosen_image.rel_path`, `checked.image.rel_path`, `checked.ref`) hay chữ người dùng gõ; chỉ đi từ gốc xuống qua `SubFolder.rel_path` của chính các lần quét; `scanned` truyền vào `check_draft_images` chỉ lấy từ các danh sách đó; "mở thư mục chứa ảnh" cũng đi từ gốc (bỏ được ràng buộc này khi T-076 gộp). Có test: nháp ghi `…/congai/cong.png`, trên ổ là `CongAI`, qua luồng mở nháp, mở thư mục, chọn lại ảnh vẫn là ảnh AI, alt có «Minh họa». (b) Hiện, duyệt, chèn ảnh bằng `checked.image`, `checked.tags`, `checked.ref`, không bằng trường trong nháp vừa mở; ảnh không dùng được thì hiện `checked.message`; hiện `snapshot.dropped_images` khi lớn hơn 0. (c) **LC-T055-2** xem trước và tải lên dùng cùng `checked.ref`; gọi lại `check_chosen_image` ngay trước khi tải ảnh của nháp lên WordPress. (d) Truyền `ai_roots` vào `check_draft_images`. Đề xuất: kiểm ảnh của nháp một lần khi mở nháp, giữ kết quả trong phiên; lưu lại theo `DraftImage.from_library(checked.ref, checked.tags, …)`. Trước khi gộp phiếu này: T-055 và nên cả T-076 phải gộp.
- 2026-10-21 (Chỉ Huy B): **Điều kiện Lá Chắn T-074** (`docs/team/reports/T-074-la-chan.md`, điều kiện 2): (i) gọi `resolve_many` theo từng trang (tối đa 200 ảnh), không gọi cho cả lần quét (SL-T074-1); (j) nút đổi sang ảnh AI: nếu `ImageTagStore.set(…)` báo lỗi (đang bận, file hỏng) thì trong phiên vẫn coi ảnh đó là ảnh AI (hướng an toàn) và hiện câu lỗi; không viết alt hay gửi nháp như ảnh thật vì lần lưu hỏng; có test. Trước khi gộp phiếu này: T-077 phải gộp.

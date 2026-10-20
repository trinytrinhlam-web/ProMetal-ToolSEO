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

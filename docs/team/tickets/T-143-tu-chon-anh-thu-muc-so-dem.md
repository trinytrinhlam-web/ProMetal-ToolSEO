# T-143 · Tự chọn ảnh thư mục, sổ ảnh đã gửi, kho đếm lượt (phiếu B)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-19 |
| Giai đoạn | Chế độ tự động (thiết kế T-141) và ảnh AI (thiết kế T-140) |
| Mức ưu tiên | Cao |
| Phụ thuộc | Không. **Đợt 1**, song song T-142, T-148 và T-144 → T-153 (khác file). Làm từ `main` mới nhất |
| Trạng thái | Mới |

## Mục tiêu

- Hàm thuần gán ảnh trong thư mục cho các chỗ cần ảnh của **cả bài**, chỉ dựa vào tên thư mục, tên file: không mở ảnh, không gọi AI, không mạng.
- Sổ ảnh đã gửi, để tránh dùng lại ảnh ở bài khác.
- Kho đếm lượt dùng chung: neuron Cloudflare theo ngày UTC, lần gọi Gemini theo ngày giờ Thái Bình Dương.

## Bối cảnh

- Thiết kế T-140: mục 1.1–1.7 (đầu vào, mặt thẻ, ứng viên, chấm điểm, ảnh đã dùng, không gửi ảnh cho AI, khi nào chạy), 2.8 (đếm lượt), mục 6 phiếu B.
- Thiết kế T-141: 1.7 (ảnh trong luồng tự động), 2.4 (sổ đếm, giãn nhịp), 6, 7.1 dòng B.
- Biên bản Lá Chắn T-140 (`fb9d2ef`): LC-T140-7, -11, -12 (bản sửa ở biên bản T-141 mục 2). Biên bản Lá Chắn T-141 (`03568dc`): mục 8 dòng B.
- Chủ dự án chọn câu 4A của T-140: không giới hạn số ảnh thật mỗi bài, chỉ lấy khi khớp rõ.

## Yêu cầu

1. **`tags.text_facets(text) -> TextFacets`** (T-140 1.2): quét chữ tự do bằng **đúng danh sách cố định** (`_CATEGORY_OBJECTS`, `_CATEGORY_MATERIALS`, `_CATEGORY_ACTIONS`, `AREAS` kèm `_AREA_ALIASES`, `_AREA_PREFIXES`, `_PHASE_WORDS`); khớp cụm dài nhất trước, không dấu, không phân biệt hoa thường, cùng bước làm sạch `clean_folder_name`. Kết quả chỉ gồm giá trị của danh sách. Vài chữ giai đoạn mới cho mô tả («hư hỏng», «bị gỉ», «xệ», «kẹt» → `truoc`): ghi trong báo cáo để Ngòi Bút duyệt chữ.
2. **`seo_app/images/autopick.py` (mới), chấm điểm** (T-140 1.4): vật trùng đúng +6; vật cùng họ +3; chất liệu trùng +2, khác hẳn −2; việc trùng +1; khu vực trùng +2; giai đoạn trùng +2, ngược −2.
   - Ngưỡng «đủ hợp»: có vật trùng đúng, hoặc tổng ≥ 5 **và** có vật cùng họ. Không có vật nào trùng thì không bao giờ tự chọn.
   - Hòa điểm: ảnh chưa dùng ở bài khác → giai đoạn hợp → ảnh sửa gần nhất → thứ tự `ImageRef`.
   - Khuyến nghị của Lá Chắn: mô tả không nói tình trạng hư thì ưu tiên ảnh giai đoạn `sau`. Thợ Máy quyết, ghi trong báo cáo.
3. **Ứng viên** (T-140 1.3):
   - đi từ `ImageLibrary.roots()`: `list_folder(root, "", recursive=False)`, chấm điểm thẻ thư mục, lấy tối đa 5 thư mục, rồi `list_folder(…, recursive=True, page_size=200)`, tối đa 1.000 ảnh;
   - thẻ bằng `ImageTagStore.resolve_many` theo trang ≤ 200;
   - ảnh có dấu hiệu AI vẫn là ảnh AI (`source="ai"`).
4. **Hàm cho cả bài:**
   - đầu vào: các chỗ (mã chỗ, mô tả, tiêu đề mục), từ khóa, khu vực của bài;
   - gán tham lam theo thứ tự chỗ; một ảnh không dùng hai lần trong bài; bản sao (cùng tên, cỡ, giờ sửa) tính là một;
   - **không đè** chỗ đã có quyết định (bạn chọn tay, «Để trống chỗ này»);
   - đầu ra mỗi chỗ: ảnh được chọn, hay mã lý do cố định (không khớp, hết ngân sách quét…);
   - **không bao giờ** ghi `alt_approved`, `approved_sha256` (LC-T141-4).
5. **Chỉ đọc tên** (LC-T140-11):
   - chỉ `list_folder` (tên, `stat`), trang ≤ 200, tối đa 5 thư mục, 1.000 ảnh;
   - **không** `read_image_bytes` trong lúc tìm (test đếm = 0);
   - không bao giờ `list_folder` từ đường dẫn lấy trong nháp (LC-T055-1: luôn đi từ thư mục gốc);
   - dấu vân tay = tên file chữ thường, cỡ byte, giờ sửa làm tròn giây.
6. **Kho `seo_app/storage/image_usage.py` (mới), file `data/image_usage.sqlite`**, qua `sqlite_file.guard` (T-136: so cấu trúc, `trusted_schema = OFF`, `dir_has_link`). Ba phần, không bí mật:
   - **Đếm neuron Cloudflare** theo ngày UTC (LC-T140-7):
     - ước tính 4 ô × 4,80 + `steps` × 9,60 trước khi gọi, cập nhật theo cỡ ảnh thật; trần 9.000;
     - ghi **trước** khi gửi lệnh (kể cả lỗi mạng, hết giờ); 3036 → ghi đầy cả ngày đó.
   - **Đếm request Gemini** theo khóa ngày do nơi gọi đưa (ngày giờ Thái Bình Dương, hàm của T-148); ghi **mỗi request trước khi gửi** (LC-T141-12).
   - **Sổ ảnh đã gửi** (T-140 1.5):
     - chỉ dấu vân tay và `ImageRef`, tối đa 10.000 dòng; không dùng để mở file;
     - hàm ghi do đường gửi gọi sau khi website xác nhận nháp đã tạo (nối ở T-150);
     - lỗi kho không làm hỏng việc khác.
7. **`tests/conftest.py`:** fixture tự chạy trỏ `DEFAULT_…_FILE` của kho mới sang thư mục tạm (như yêu cầu 6 của T-138). `tests/test_t138_khong_ghi_data_that.py` vẫn qua (mọi kho của `seo_app/storage` trỏ ra ngoài dự án).
8. **Test:**
   - bảng ca chấm điểm cố định (tiếng Việt có dấu, không dấu, dính chữ; chữ tự do không lọt thành thẻ);
   - đếm `read_image_bytes` = 0 khi tìm; ngân sách quét; không trùng ảnh trong bài; không đè lựa chọn tay, «Để trống chỗ này»; ảnh AI giữ là ảnh AI;
   - kho đếm: sang ngày UTC và ngày Thái Bình Dương (cả hai mốc đổi giờ mùa hè của Mỹ), ghi trước khi gửi, ghi đầy, file hỏng, `data/` là liên kết;
   - sổ ảnh: trần 10.000 dòng.

## Phạm vi

- **Được sửa:** `seo_app/images/tags.py` (thêm `text_facets`, chữ giai đoạn), `seo_app/images/autopick.py` (mới), `seo_app/storage/image_usage.py` (mới), `tests/conftest.py` (chỉ fixture trỏ kho mới), test mới `tests/test_t143_*.py`.
- **Không được sửa:** `seo_app/images/folders.py` (đọc thư mục an toàn T-048 → T-080), `seo_app/storage/image_tags.py` (chỉ gọi `resolve_many`), `seo_app/storage/drafts.py`, `seo_app/ai/**`, `app/**`, `config/**`.
- **Ngoài phạm vi:** gọi hàm gán ảnh trong lượt chạy (T-149), ghi sổ ảnh sau khi gửi (T-150), hiện số đếm ở Cài đặt (T-146).

## Yêu cầu bảo mật riêng (điều kiện Lá Chắn)

F1, F3, A3 (không gửi ảnh cho AI để so).

- **LC-T140-7** (đếm lượt: kho qua `sqlite_file.guard`, ngày UTC, ước tính trước khi gọi, ghi trước khi gửi, 3036 ghi đầy, trần 9.000), **LC-T140-11** (chỉ đọc tên, không `read_image_bytes` khi tìm, không `list_folder` từ đường dẫn của nháp, `text_facets` chỉ trả giá trị danh sách, sổ ảnh ≤ 10.000 dòng, ghi sau khi website xác nhận), **LC-T140-12 (bản sửa theo T-141)**: ảnh tự chọn **không bao giờ tự duyệt**; «Để trống chỗ này» và lựa chọn tay không bao giờ bị đè.
- **LC-T141-12** (kho đếm dùng chung ghi **mỗi request** trước khi gửi), **LC-T141-4** (hàm gán ảnh không ghi duyệt).

## Tiêu chí xong

- [ ] Yêu cầu 1–8, có test.
- [ ] Test liên quan + test mọi nơi gọi `tags.py` (`test_images_tags*.py`, `test_app_images.py`, test thẻ ảnh của Soi Lỗi T-052, T-070, T-074, T-077) + `tests/test_t138_khong_ghi_data_that.py` qua; `uv run ruff check .` sạch.
- [ ] Báo cáo `docs/team/reports/T-143-tho-may.md`.

## Kiểm thử và kiểm định

- Soi Lỗi: Có (chấm điểm, không mở file khi tìm, kho đếm qua mốc ngày).
- Lá Chắn: rút gọn (F1, F3).

## Lưu ý chung

- Chỉ chạy test trong worktree của phiếu (`D:/ProMetal-ToolSEO/wt-T-143`), **không** chạy trong `D:/ProMetal-ToolSEO/ProMetal-ToolSEO`.
- Không chạy toàn bộ `uv run pytest`: chạy test liên quan, test của mọi nơi gọi hàm sửa, `uv run ruff check .`.
- Tham số test lớn kèm `ids=` ngắn.
- Test không gọi AI, Cloudflare, Google, WordPress thật; ảnh, thư mục giả tạo trong test.
- Không đọc `.env`, không in hay commit khóa; `detect-secrets` (`PYTHONUTF8=1`, có file mồi) sạch.
- Đổi kỳ vọng test cũ: theo R5.

## Ghi chú của Chỉ Huy

- Lập 2026-11-19 từ thiết kế T-140/T-141 (phiếu B, mục 7 của `docs/team/reports/T-141-tho-may.md`; biên bản Lá Chắn `fb9d2ef`, `03568dc`). Worktree `wt-T-143`, nhánh `team/T-143`.

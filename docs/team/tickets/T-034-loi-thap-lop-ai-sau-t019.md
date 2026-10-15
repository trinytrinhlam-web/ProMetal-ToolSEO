# T-034 · Lỗi Thấp còn lại của lớp AI và thử mù (sau T-019)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Thấp (phải xong trước khi đóng Giai đoạn 2) |
| Phụ thuộc | T-019 đã gộp vào `main`, vì phiếu sửa `seo_app/content/blind_test.py` và `seo_app/ai/**` mà T-019 vừa đổi. Không làm cùng lúc với T-031 nếu T-031 sửa `blind_test.py` |
| Trạng thái | Chờ T-019 |

## Mục tiêu

Gom các lỗi mức Thấp mà Soi Lỗi và Lá Chắn đã ghi sổ về lớp AI và trang thử mù. Sửa một lượt để đóng Giai đoạn 2 sạch.

## Bối cảnh và danh sách lỗi

| Mã | Nguồn | Lỗi | Hướng sửa gợi ý |
|---|---|---|---|
| SL-T019-3 | `docs/team/reports/T-019-soi-loi.md` (lượt 2) | Che tên mô hình trong bài thử mù còn để lộ **số phiên bản** đứng sau tên: "Tôi là Claude Opus 5.5" thành "«đã ẩn tên mô hình» «đã ẩn tên mô hình» 5.5"; tương tự "GPT 6.1", "Gemini 3 Pro". Người quen số phiên bản đoán được hãng. Test `xfail(strict)` sẵn: `test_version_number_after_vendor_word_is_masked` | Sau một chữ đã che, che luôn phần số/biến thể đi liền sau (`5.5`, `6.1`, `3 Pro`, `Flash`…). **Không** che số đứng riêng trong bài: test đối chứng `test_version_like_numbers_in_article_are_kept` ("dày 5.5 mm") phải vẫn qua |
| SL-T019-4 | như trên | Riêng Claude, khi bài thử bị cắt vì quá dài, thư viện `anthropic` ném `ValidationError` trước khi biết lý do dừng. Câu lỗi vì thế bảo "tăng max_tokens của việc «blind_test» trong config/ai.toml", mục người dùng không làm theo được. OpenAI và Gemini đã đúng. Test `xfail(strict)` sẵn: `test_blind_token_limit_anthropic_real_library_points_to_effort` | Ở nhánh `ValidationError` của `anthropic_provider.py`, nếu nhận ra bị cắt (`stop_reason == "max_tokens"` lấy được an toàn) thì ném `TokenLimitError`. Câu chữ đúng như T-019 lượt 2, **không** chép chữ máy chủ |
| SL-T019-5 | như trên ("Ghi nhận thêm") | `ignoring_custom_headers` (`seo_app/ai/base.py`) **gỡ** biến `*_CUSTOM_HEADERS` khỏi `os.environ` trong lúc tạo client. Luồng khác đang duyệt `os.environ` đúng lúc đó (httpx tìm proxy, `dict(os.environ)`) bị `KeyError`. Test T-028 `test_other_threads_reading_environment_never_fail` có lúc hỏng: Soi Lỗi gặp 25/25 lần khi chạy riêng file trên `main`; Chỉ Huy B chạy 5 lần đều qua, tức là lỗi phụ thuộc máy. Thử mù là chỗ đầu tiên tạo client song song ở nhiều luồng | Tìm cách không gỡ biến khỏi `os.environ`, ví dụ chặn đúng chỗ thư viện đọc biến (nếu thư viện có điểm đọc ổn định), hoặc cách khác có lý do rõ. Phải giữ đủ: header lạ **không bao giờ** tới client (test T-028 vẫn qua). Không làm thì báo cáo lý do và đề xuất sửa test. **Không** được nới lỏng test để qua |
| LC-T028-1 | `docs/team/reports/T-028-la-chan.md` | Khóa `_ENV_LOCK` là `threading.Lock`: gọi lồng trong cùng luồng sẽ treo (hiện chưa có chỗ gọi lồng) | Đổi sang `RLock`, có test gọi lồng. Nếu SL-T019-5 bỏ hẳn việc gỡ biến thì xét lại có cần khóa không |
| LC-T028-3 | như trên (= SL-T028-3) | Nội dung nén `gzip`/`br` hỏng ở Anthropic/OpenAI ra câu "Không kết nối được tới …" thay vì câu "dữ liệu lạ" | Nhánh `APIConnectionError`: nếu `__cause__` (hoặc chuỗi nguyên nhân) là lỗi giải nén của httpx (`DecodingError`) thì ra `bad_response_error`. Áp dụng cả ở `seo_app/env_file.py` (nút Kiểm tra khóa). Bỏ `xfail` của test tương ứng |

## Phạm vi

- **Được sửa:** `seo_app/ai/**`, `seo_app/content/blind_test.py`, `seo_app/env_file.py`, test.
  - Chỉ bỏ dấu `xfail` của đúng các test đã nêu khi đã sửa xong.
  - Ghi tên các test đó vào báo cáo.
- **Không được sửa:** `app/**`, `config/**`, `seo_app/sanitize.py` (T-031 sửa).
- **Ngoài phạm vi:** đổi mô hình mặc định, thêm thư viện.

## Yêu cầu

1. Sửa 5 lỗi trên. Lỗi nào không sửa được hoặc thấy không nên sửa thì nêu lý do trong báo cáo để Chỉ Huy quyết.
2. Mọi câu lỗi vẫn là câu cố định tiếng Việt, không chép chữ máy chủ, không lộ khóa (S2, T-026, T-028).
3. Test cho mọi nhánh mới, không gọi mạng thật. Riêng SL-T019-5: test chạy song song nhiều luồng phải qua ổn định. Chạy riêng file `tests/test_soi_loi_t028.py` ít nhất 30 lần, 0 hỏng, ghi số vào báo cáo.
4. `uv run pytest` và `uv run ruff check .` sạch.

## Yêu cầu bảo mật riêng

S2, W4 / mục 2.7 (chỉ gọi máy chủ chính thức, header lạ không lọt), A2, D1, D3.

## Tiêu chí xong

- [ ] 5 lỗi đã sửa hoặc có lý do rõ
- [ ] Test `xfail` tương ứng đã bỏ dấu và qua
- [ ] `tests/test_soi_loi_t028.py` chạy riêng 30 lần, 0 hỏng
- [ ] Báo cáo `docs/team/reports/T-034-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có.
- Lá Chắn: Có (S2, W4).

## Ghi chú của Chỉ Huy

- Làm trong phiên con **"Thợ Máy · T-034 Lỗi Thấp lớp AI sau T-019"**, trên nhánh tạm `team/T-034` (tạo từ `main` **sau khi** T-019 đã gộp).

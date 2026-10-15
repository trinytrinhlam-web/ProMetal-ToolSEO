# Báo cáo T-028 · Kiểm thử: máy chủ AI trả mã 200 nhưng nội dung hỏng

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-028](../tickets/T-028-noi-dung-hong-tu-may-chu-ai.md) |
| Ngày nộp | 2026-10-15 |
| Kết quả | Hoàn thành · **ĐẠT** (3 lỗi mức Thấp, không chặn) |

## Tóm tắt (cho chủ dự án)

Tôi thử hơn 100 cách máy chủ AI (hoặc proxy, Wi-Fi công cộng) có thể trả về thứ hỏng: trang HTML, JSON
hỏng hay bị cắt, luồng chữ hỏng ở nhiều chỗ, dữ liệu nén hỏng, mạng đứt giữa chừng. Ở cả 3 hãng, cả lúc
viết bài lẫn nút Kiểm tra khóa, người dùng luôn thấy một câu tiếng Việt cố định, không bao giờ thấy khối
lỗi tiếng Anh, chữ của máy chủ hay khóa API. Khóa đúng vẫn được báo "dùng được". Có 3 chỗ câu gợi ý hơi
sai hướng (ví dụ báo "kiểm tra mạng" thay vì "dữ liệu lạ"); không lộ gì, không sập trang, đề xuất để sau.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_soi_loi_t028.py` | Mới: 122 trường hợp (117 qua, 5 `xfail(strict=True)` cho SL-T028-1/2/3). Không sửa test cũ, không sửa code ứng dụng. |
| `docs/team/reports/T-028-soi-loi.md` | Báo cáo này. |

## Bằng chứng

```
$ uv run pytest -q tests/test_soi_loi_t028.py tests/test_ai_t028.py tests/test_soi_loi_t026.py
605 passed, 7 xfailed, 1 warning in 17.16s

$ uv run pytest -q          (toàn repo, Linux)
9 failed, 3064 passed, 2 skipped, 10 xfailed, 1 warning in 168.18s   (9 hỏng = T-027/T-030, biết trước)

$ uv run ruff check .
All checks passed!
```

9 test hỏng đều là lỗi biết trước trong `tests/test_soi_loi_t027.py` (T-030 đang sửa; Linux thiếu
`socket._fallback_socketpair`, máy không có IPv6), có sẵn trên `main`, không do T-028. Trước khi thêm test
của tôi, nhánh của Thợ Máy cho đúng kết quả Thợ Máy báo: `9 failed, 2947 passed, 2 skipped, 5 xfailed`.
Test nhiều luồng chạy lặp 3 lần đều qua. Chưa chạy được trên Windows (máy cloud là Linux).

## Kiểm thử theo từng điểm Chỉ Huy giao

### (a) Phân biệt "dữ liệu lạ" với "uv sync" bằng traceback

| Thử | Kết quả |
|---|---|
| 13 dạng luồng SSE hỏng mới (`delta.text` là số, `index` lệch, `message_delta` thiếu/`null` `usage`, `data` không phải JSON, `content_block_stop` trước `start`, `content_block` thiếu, `message` null / thiếu `content` / `content` là số, chỉ có `ping`, sự kiện `error` rác hoặc quá tải), UTF-8 hỏng trong luồng | Câu cố định, phần lớn đúng "dữ liệu lạ" (`test_anthropic_other_broken_streams_give_fixed_message`, `test_anthropic_broken_stream_is_exactly_strange_data`) |
| gzip hỏng, gzip bị cắt, br hỏng; 3 hãng × viết bài + Kiểm tra | Câu cố định; Anthropic/OpenAI gzip hỏng ra "Không kết nối được" → **SL-T028-3** |
| Trả lời bị cắt giữa chừng (máy chủ đóng kết nối giữa thân JSON), 3 hãng × 2 chỗ | Câu cố định "Không kết nối được tới …" |
| JSON bị cắt (proxy cắt bớt, kết nối đóng đúng) | "dữ liệu lạ", 3 hãng |
| **Chiều ngược**: 13 dạng JSON sai kiểu (chuỗi, số, `true`, danh sách, `output`/`content`/`status` sai kiểu…) × Anthropic/OpenAI × viết bài + Kiểm tra; Gemini Kiểm tra | Không lần nào ra câu "uv sync" (`test_strange_json_never_reported_as_library_problem`) |
| `stop_reason` lạ (số, chuỗi mới, `null`, danh sách) | Không sập; có lúc vẫn trả bài (chấp nhận được) |
| **Lệch phiên bản nảy ra sâu** trong hàm đọc trả lời (vá `construct_type`, `APIResponse._parse` ném `TypeError`) | Ra "dữ liệu lạ" thay vì "uv sync" → **SL-T028-1** (Thợ Máy đã nêu ở rủi ro 2) |
| Lệch phiên bản ở pydantic (`model_construct` ném `TypeError`) | Đúng câu "uv sync" (lỗi nảy ra lúc dựng khuôn, trước khi gọi) |

### (b) Nút Kiểm tra khóa

- Danh sách đúng dạng như máy chủ thật trả (Anthropic rỗng / có `has_more`, OpenAI rỗng / 1 mô hình,
  Gemini có `nextPageToken`, có `supportedGenerationMethods`): đều "dùng được"
  (`test_check_realistic_valid_listings_are_ok`). **Không thấy khóa đúng bị báo nhầm.**
- `{}`, Gemini `models` rỗng / `null` / chuỗi: "dữ liệu lạ" (`test_check_empty_or_missing_listing_is_strange_data`).
- Ghi nhận: Anthropic `{"data": [5, "x"]}`, OpenAI `{"data": [null]}`, Gemini `{"models": [{}]}` vẫn ra
  "dùng được" (chỉ xét `data` là danh sách, không xét từng mục). Proxy khó trả đúng dạng này; không phải lỗi.
- Rủi ro 4 của Thợ Máy (Gemini trả trang đầu rỗng với khóa đúng) không tái hiện được bằng mạng giả; với
  `page_size=1` Google luôn trả ít nhất 1 mô hình cho khóa dùng được. Chấp nhận.

### (c) `ignoring_custom_headers` và nhiều luồng

| Thử | Kết quả |
|---|---|
| 16 luồng cùng lúc tạo client Anthropic/OpenAI thật (rào `Barrier`), biến có giá trị Unicode + `Authorization` lạ | Không client nào nhận header lạ, không lỗi, biến trả lại đúng từng ký tự, khóa được nhả (`test_many_threads_creating_clients_at_once`) |
| 3 luồng gỡ/trả liên tục + 3 luồng duyệt `os.environ` (`urllib.request.getproxies()` như httpx, `dict(os.environ)`) trong 0,5 giây | Không lỗi "dictionary changed size" (`os.environ` sao chép danh sách khóa trước khi duyệt). Thử tay 5 giây: luồng khác thấy biến "biến mất" ~7.000 lần, đúng như Thợ Máy nêu ở rủi ro 5; app không đọc 2 biến này ở chỗ nào khác |
| Ngoại lệ trong lúc gỡ: `KeyboardInterrupt`, `SystemExit`, `GeneratorExit`, `MemoryError`; tạo client hỏng (`TypeError`) | Biến trả lại, khóa được nhả; nút Kiểm tra ra câu "uv sync" |
| Chỉ 1 trong 2 biến có; giá trị rỗng `""` | Không tự thêm biến vốn không có; giá trị rỗng trả lại đúng |

**Biến có bị mất hẳn khỏi môi trường không?** Với ngoại lệ bình thường thì không (khối `finally`). Chỉ còn
2 khe lý thuyết, không có đường thật trong app:

1. Ngoại lệ bất đồng bộ (Ctrl+C rơi đúng giữa 2 lệnh `os.environ.pop`, trước `try`): biến đã gỡ chưa kịp
   ghi vào `saved`. Ctrl+C vốn tắt luôn app, Streamlit không chèn ngoại lệ vào luồng chạy trang.
2. Luồng khác **ghi** biến này đúng trong khoảnh khắc đang gỡ: lúc trả lại, giá trị cũ đè lên giá trị mới
   (hoặc biến vừa bị xóa lại hiện về). App không ghi 2 biến này ở đâu.

Thêm: `threading.Lock` không vào lại được; gọi lồng `ignoring_custom_headers` trong cùng luồng sẽ treo.
Hiện không có chỗ nào lồng. Ghi lại để ai sửa sau biết.

### (d) Câu báo cố định

- Mọi câu ở mọi test trên: không chứa `SERVER_TEXT`, khóa giả 3 hãng, `<`, `{`, "Error", "Traceback".
- Lỗi mạng giữa luồng có chèn chữ máy chủ **và** khóa giả vào thông điệp (`ReadError`, `ReadTimeout`,
  `DecodingError`): câu báo không chứa cả hai (`test_network_errors_mid_stream_never_echo_server_or_key`).
- Câu mới chỉ ghép tên hãng viết sẵn và `task.max_tokens` / `task.name` từ `config/ai.toml`.

## Lỗi tìm thấy

| Mã | Mức | Chỗ | Cách tái hiện | Mong đợi | Thực tế |
|---|---|---|---|---|---|
| **SL-T028-1** | Thấp (rủi ro đã nêu) | `seo_app/ai/base.py` `is_bad_response` | Vá `openai._models.construct_type` hoặc `anthropic._models.construct_type` ném `TypeError` (giả lập thư viện tự lệch phiên bản bên trong), gọi viết bài với trả lời hợp lệ. Test: `test_deep_library_mismatch_is_reported_as_library` (xfail strict). Nút Kiểm tra cũng vậy. | Câu "uv sync" | "Máy chủ … trả về dữ liệu lạ". Không lộ gì, không sập (`test_deep_library_mismatch_never_crashes`). Thợ Máy đã nêu (rủi ro 2). Đề xuất: **chấp nhận**, vì sửa thì phải đoán nguồn lỗi, dễ làm hỏng chiều ngược (dữ liệu hỏng ra "uv sync") vốn quan trọng hơn. |
| **SL-T028-2** | Thấp | `seo_app/ai/base.py` `IGNORED_ENV`, `openai/_client.py:281-286` | Đặt `OPENAI_ORG_ID=org-…` và/hoặc `OPENAI_PROJECT_ID=proj_…` trong môi trường máy (biến sót từ công cụ OpenAI khác), bấm Kiểm tra khóa. Test: `test_openai_org_and_project_env_ignored` (xfail strict). | Không gửi header `OpenAI-Organization` / `OpenAI-Project` (app không dùng tổ chức/dự án) | Thư viện gắn 2 header này vào mọi lời gọi. Với máy chủ thật, khóa không thuộc tổ chức đó bị từ chối (401) → app báo "Khóa không đúng" dù khóa đúng. Không lộ khóa. Đây là "biến tương tự" theo mục 3 của phiếu. Sửa nhỏ: thêm 2 biến vào `IGNORED_ENV`. Anthropic: đã xem `anthropic/_client.py`, `ANTHROPIC_AUTH_TOKEN` không được đọc khi app truyền `api_key`, nên không có lỗi tương tự. |
| **SL-T028-3** | Thấp (có sẵn trước T-028) | `seo_app/ai/anthropic_provider.py`, `openai_provider.py`, `env_file.py` | Máy chủ trả mã 200, `content-encoding: gzip`, thân không phải gzip. Test: `test_gzip_garbage_is_strange_data` (xfail strict). | "Máy chủ … trả về dữ liệu lạ" | "Không kết nối được tới Anthropic/OpenAI. Kiểm tra mạng Internet." (thư viện bọc `httpx2.DecodingError` thành `APIConnectionError` trước khi app thấy; nhánh `"decode"` của `network_error_kind` chỉ có tác dụng khi lỗi nảy ra giữa luồng). Câu cố định, vẫn hướng người dùng xem mạng. Gemini đã ra đúng "dữ liệu lạ". |

## Đối chiếu tiêu chí xong

- [x] SL-T026-4 bỏ `xfail` và qua: `tests/test_soi_loi_t026.py::test_garbage_200_gives_vietnamese_error`
  (4 trường hợp); có test cho cả 3 hãng (`tests/test_ai_t028.py`, `tests/test_soi_loi_t028.py`).
- [x] Mỗi nhánh logic mới có test: `is_bad_response`, `network_error_kind`, `unreadable_error`,
  nhánh `ValidationError` (bài bị cắt), `_as_list`, `_other_result`, `_listing_ok` (cả `allow_empty`),
  `ignoring_custom_headers`, `no_debug_config`.
- [x] Không bắt nhầm dữ liệu hỏng thành "uv sync" (đã thử 13 dạng × 2 hãng × 2 chỗ).
- [x] Câu báo cố định, không chép máy chủ, không chứa khóa (S2).
- [x] Test không gọi mạng thật (`MockTransport`, bộ chặn mạng của `conftest.py` vẫn bật).
- [x] `uv run ruff check .` sạch; `uv run pytest` không hỏng gì ngoài 9 test biết trước của T-030.
- [ ] Chạy trên Windows: chưa (máy cloud là Linux).

## Rủi ro và điểm cần chú ý

- Nhận diện dựa vào tên hàm trong thư viện (rủi ro 1 của Thợ Máy): nâng thư viện mà đổi tên hàm thì
  `test_check_garbage_*`, `test_generate_garbage_*` đỏ ngay. Đã kiểm, đúng.
- Nhánh `ValidationError` của Anthropic ghi "có thể bài bị cắt vì quá giới hạn … token" cả khi lý do khác
  (ví dụ máy chủ gửi kiểu `delta` mới mà thư viện chưa biết → bài rỗng). Câu có chữ "có thể", chấp nhận.
- Sự kiện `error` giữa luồng (quá tải) vẫn ra "Anthropic báo lỗi 200" (Thợ Máy đã ghi nhận, có sẵn trên `main`).
- Test `test_other_threads_reading_environment_never_fail` dựa vào thời gian (0,5 giây) nhưng chỉ khẳng
  định "không có lỗi", nên không thể hỏng ngẫu nhiên khi code đúng.

## Đề xuất

- **Chỉ Huy:** cho qua cổng Lá Chắn. SL-T028-2 nên sửa (1 dòng: thêm `OPENAI_ORG_ID`, `OPENAI_PROJECT_ID`
  vào `IGNORED_ENV`), có thể làm ngay trong T-028 hoặc phiếu sau. SL-T028-1 đề xuất chấp nhận. SL-T028-3
  có sẵn trước T-028, để phiếu sau nếu muốn (bắt `APIConnectionError` có `__cause__` là `DecodingError`).
- **Lá Chắn:** xem 2 khe lý thuyết ở mục (c) (biến bị đè / mất khi có ngoại lệ bất đồng bộ) có cần
  chuyển sang "xóa hẳn khỏi tiến trình lúc khởi động" không.

## Câu hỏi cho chủ dự án

Không có.

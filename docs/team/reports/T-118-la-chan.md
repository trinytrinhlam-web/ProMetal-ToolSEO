# Biên bản bảo mật T-118 · Dọn lỗi Thấp sau rà soát Fable: ẩn chi tiết lỗi trên trang, LC-T034-1..3, SL-T105-1, LC-T113-2, SL-T118-1

> **Model:** chạy bằng Claude Opus 5.5 (phiên này). Hồ sơ vai khuyên Claude Fable 5.1; phiếu này kiểm rút gọn, không thuộc lượt kiểm lại bằng Fable (T-116).

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (xem dòng trên) · dưới Chỉ Huy B |
| Phiếu được kiểm | T-118 `T-118-don-thap-sau-fable.md` (bản trong thư mục nháp của Chỉ Huy, chưa lên `main`) · kiểm **rút gọn** (U2, U3, F3) |
| Phạm vi | diff `935d381..73d4205` (nhánh `team/T-118`, 17 file). Code: `.streamlit/config.toml`, `seo_app/ai/base.py`, `anthropic_provider.py`, `openai_provider.py`, `gemini_provider.py`, `seo_app/env_file.py`, `scripts/hash_password.py`, `seo_app/storage/plan_cache.py`, `site_index.py`. Test: `tests/test_t118_don_thap.py` (mới), `tests/test_soi_loi_t118.py` (mới), 4 file test cũ (R5). 3 báo cáo. Kèm mã đóng gói lỗi của Streamlit 1.65 (`streamlit/elements/exception.py`), `seo_app/sanitize.py` (`escape_link_syntax`, `clean_ai_text`) |
| Báo cáo đã đọc | [Thợ Máy](T-118-tho-may.md) (2 lượt), [Soi Lỗi](T-118-soi-loi.md) (ĐẠT CÓ ĐIỀU KIỆN, SL-T118-1 nay đã sửa ở lượt 2) |
| Ngày | 2026-11-03 (08:25–08:45, giờ máy +07) |
| **Kết luận** | **ĐẠT** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 0 Thấp mới. **Đóng:** LC-T034-1, LC-T034-2, LC-T034-3, SL-T105-1, LC-T113-2, SL-T118-1, và Lá Chắn T-001 #8 (chi tiết lỗi trên trang). **Gộp vào `main` được ngay**: gộp thử với `main` cục bộ `33dd87f` không xung đột, test chọn lọc trên cây gộp 0 hỏng |

## Tóm tắt (cho chủ dự án)

- **Lỗi bất ngờ trên trang nay chỉ hiện loại lỗi**, đúng như anh/chị chọn ngày 02/11. Tôi kiểm tận chỗ Streamlit đóng gói lỗi: câu lỗi gốc, đường dẫn thư mục và các dòng mã bị xóa **ngay trong máy, trước khi gửi lên trình duyệt**, chứ không chỉ bị giấu trên màn hình. Chi tiết vẫn in ở cửa sổ đen chạy app để người hỗ trợ xem.
- **Các lỗi nhỏ còn lại đã sửa đúng:**
  - Tên mô hình AI viết như một địa chỉ web không còn thành link bấm được trong câu báo.
  - Biến môi trường chứa header lạ bị chặn thêm ở một lối đọc ít dùng (chỉ có trên Mac).
  - Công cụ đặt mật khẩu báo đúng khi file `.env` vừa bị chương trình khác sửa đúng lúc lưu.
  - Ngày giờ sửa tay hỏng trong file lưu tạm không làm trang hiện lỗi.
- **Không lộ gì, không nới lớp bảo vệ nào.** Test cũ chỉ đổi đúng câu mong đợi đã được duyệt. Chạy test không đụng file `.env` thật.

## Lỗi phát hiện

Không phát hiện lỗi mới.

## Từng lỗi được đóng

| Lỗi | Kết quả | Bằng chứng |
|---|---|---|
| **T-001 #8 / chủ dự án 02/11** · chi tiết lỗi trên trang (U2) | **Đóng** | `.streamlit/config.toml:19` `showErrorDetails = "type"`; `uv run streamlit config show` trong worktree đọc ra đúng `"type"`. Mã Streamlit 1.65 (`elements/exception.py`, hàm `_error_detail_visibility` và `marshall`): với `"type"`, `show_message` và `show_trace` là `False`. Câu lỗi bị thay bằng câu chung, `stack_trace` bị xóa trước khi dựng, **ở phía máy chủ trước khi gửi**. **Thử độc lập:** gọi `marshall(..., apply_show_error_details=True)` như `AppSession` làm với 3 lỗi chưa bắt, có đường dẫn và khóa giả trong câu lỗi, kể cả câu của lỗi gốc lồng bên trong: `FileNotFoundError`, `RuntimeError` có `__cause__`, `SyntaxError` có tên file. Byte protobuf gửi đi chỉ còn tên loại lỗi và câu «This app has encountered an error…», **0 dòng stack**, không còn đường dẫn, tên file, thư mục dự án, khóa, chữ `Traceback` hay `File "`. Đối chứng `"full"` (mặc định trước T-118): lộ tên file và dòng `File "`. App không gọi `st.exception` ở đâu (lệnh này không theo cấu hình) |
| **LC-T034-1** · tên mô hình thành link trong `st.error` | **Đóng** | `model_label` (`seo_app/ai/base.py:469-480`) = `escape_link_syntax` (link Markdown, địa chỉ trần, `www.`, email: bộ chặn T-031) rồi đổi «<» thành «&lt;» (link tự động `<scheme:…>`). Dùng ở 7 câu báo: 2 câu × 3 hãng, cộng câu lỗi 400 |
| **SL-T118-1** · tên mô hình dạng `<https:…>` vẫn là link tự động | **Đóng** (với tên mô hình) | Thử lại: `<https:evil.example/x>`, `<https://…>`, `<mailto:…>` qua `model_label`: không còn mẫu link tự động CommonMark. 6 ca của Soi Lỗi nay qua (bỏ dấu `xfail`) |
| **LC-T034-2** · `os.environb` / `getenvb` không bị che | **Đóng** | `_EnvironbWithoutIgnored` và `_OsWithoutIgnored.__getattr__` (`base.py:296-340`) che 4 tên `IGNORED_ENV` ở bản byte. Trên Windows (không có `environb`) vẫn báo `AttributeError` như `os` thật. Test giả lập qua trên Windows; ca thật chỉ chạy được trên Mac/Linux (bỏ qua ở đây, có ghi lý do) |
| **LC-T034-3** · vòng trỏ `module.os` nằm trước `try` | **Đóng** | `ignoring_custom_headers` (`base.py:347-400`): cả vòng trỏ lẫn bước gỡ biến nằm trong `try`; `finally` luôn trả biến và trả `os` thật cho mọi module đã trỏ. Test: module thứ hai nạp lỗi thì module đầu vẫn được trả lại |
| **SL-T105-1** · `.env` bị sửa đúng lúc lưu mà báo «dòng sai định dạng» (U3) | **Đóng** | `EnvFileChangedError` (`env_file.py:89-94`), câu `_CHANGED_RESTORED` / `MSG_ENV_CHANGED`: «đọc lại ngay sau khi lưu đã khác bản vừa ghi… đã được trả về bản trước khi lưu». Câu này chỉ đến sau khi bỏ bản vừa ghi **thành công**: nhánh không trả được đi trước, có câu riêng. Chạy lại script thử 5 ca của Lá Chắn T-105 trên mã mới: ca d nay ra đúng câu mới; mọi ca 0 lộ giá trị biến, mã băm, đường dẫn, traceback; `.env` đúng trạng thái câu báo nói; không sót file tạm |
| **LC-T113-2** · giờ tải sửa tay làm `load()` ném `OverflowError` | **Đóng** | `_parse_time` của `plan_cache.py:326-331` và `site_index.py:391-396` bắt `OverflowError`, `ValueError` khi đổi múi giờ, coi như file hỏng. `load()` trả `None` (coi như chưa có cache), lần lưu sau vẫn được; trang Bài viết và Kế hoạch mở không lỗi. 9 ca `xfail` cũ nay qua (bỏ dấu) |

**Bước «trả bản cũ» của SL-T105-1.** Ở T-105 tôi đề xuất (mức «nên») không trả bản cũ khi chữ đọc lại khác chữ vừa ghi, để khỏi xóa thay đổi của chương trình kia. Thợ Máy giữ bước trả bản cũ và nêu lý do: bộ ghi không phân biệt được «chương trình khác vừa ghi» với «ổ đĩa ghi không trọn», và với ca sau thì trả về bản cũ đã kiểm là cách giữ `.env` dùng được.

**Đồng ý với lý do này.** Giữ `.env` ở một trạng thái chắc chắn đọc được thì quan trọng hơn. Câu báo mới đã nói rõ file được trả về bản trước khi lưu. Việc thay đổi đồng thời của chương trình kia bị mất vẫn là Quan sát 2 của Lá Chắn T-104 (hai bộ ghi không khóa lẫn nhau), có từ trước, rất hiếm, không lộ gì.

## Ghi nhận: bộ chặn link dùng chung và Đề xuất 4 của Thợ Máy

- `escape_link_syntax` dùng chung (T-031) vẫn để nguyên link tự động `<https:…>`, `<mailto:…>` (thử lại: còn).
- Nhưng **đường chữ AI** (`clean_ai_text`) bỏ cả cụm `<…>` như một thẻ HTML trước bước chặn link. Thử 3 mẫu: kết quả là chữ rỗng hay mất cụm đó, không còn link.
- Chỗ còn lại gọi thẳng `escape_link_syntax` chỉ hiện chữ do người dùng tự gõ (sửa tay đoạn bài, tiêu đề dàn ý sau khi sửa), không phải dữ liệu từ ngoài.
- Vì vậy Đề xuất 4 của Thợ Máy (chặn `<scheme:…>` ngay trong `escape_link_syntax`, giữ phép đảo `unescape_link_syntax`) là **gia cố thêm**, không phải lỗi mở. Làm khi tiện, không cần phiếu gấp.

## R5 · Test cũ đổi

| File | Đổi | Ý kiến |
|---|---|---|
| `tests/test_env_file.py::test_mismatch_after_write_restores_old_file` | `pytest.raises(EnvFileError, match="định dạng lạ")` thành `pytest.raises(EnvFileChangedError, match="khác bản vừa ghi")` | **Không yếu đi, chặt hơn:** loại lỗi hẹp hơn (lớp con), vẫn kiểm file trả bản cũ từng byte và đúng 2 lần ghi. Chỉ Huy duyệt 02/11 17:55 |
| `tests/test_t105_set_password.py::test_readback_mismatch_still_reported_as_format` → `…_reported_as_changed` | Câu mong đợi `MSG_ENV_FORMAT` thành `MSG_ENV_CHANGED` (so bằng nguyên câu) | Không yếu: vẫn mã thoát 1, `.env` trả bản cũ từng byte. Chỉ Huy duyệt |
| `tests/test_soi_loi_t105.py` | Gỡ 2 dấu `xfail(strict=True)` SL-T105-1 | Đúng R5: chỉ xóa dấu, thân test giữ nguyên, nay qua |
| `tests/test_la_chan_t113.py` | Gỡ dấu `xfail` LC-T113-2 (định nghĩa dấu và 2 chỗ dùng) | Đúng R5: các giá trị thử giữ nguyên, nay qua |

## Thử gộp với `main`

- `main` cục bộ `33dd87f` (có T-115, T-117, T-119, biên bản T-116): `git merge-tree --write-tree` → **không xung đột** (cây `1141598`). Hai bên không chung file nào.
- Chạy thật: worktree tạm trong thư mục nháp (commit treo `6bfdf08`, không đẩy, đã gỡ), `uv sync --frozen`. Đặt một `.env` canh (giả) ở gốc dự án.
  - Chạy 8 file: `tests/test_t118_don_thap.py`, `tests/test_soi_loi_t118.py`, `tests/test_la_chan_t113.py`, `tests/test_soi_loi_t105.py`, `tests/test_t105_set_password.py`, `tests/test_env_file.py`, `tests/test_ai_t034.py`, `tests/test_ai_t028.py`.
  - Kết quả: **556 passed, 5 skipped, 0 hỏng** (261 s, 08:30–08:35). 5 ca bỏ qua có ghi lý do: `os.environb` không có trên Windows (1), quyền 600 kiểu Mac/Linux (1), tạo symlink cần quyền đặc biệt (3).
  - `.env` canh **không đổi** (SHA-256 `bc75dc92…`, giờ sửa giữ nguyên). `ruff`: sạch.
- Audit hook (plugin pytest nháp, không commit) trên cùng lượt: 65 sự kiện, **cả 65 là `127.0.0.1`** (cặp socket nội bộ của AppTest); 0 lần tra tên, 0 lần nối ra ngoài.
- **Gộp được ngay.**

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` (đặt `PYTHONUTF8=1`) trên 14 file của diff: các mục báo ở `seo_app/ai/base.py:30` (chú thích nêu ví dụ địa chỉ có kèm tên đăng nhập và mật khẩu giả), `seo_app/env_file.py:58` (tên hằng), `tests/test_env_file.py` (9 khóa giả trong test cũ) đều **đã có ở `935d381`**: so theo mã băm chuỗi bị báo, 0 mục mới. Mồi khóa giả trong bản sao file test (có chữ tiếng Việt): bắt được 1; không đặt `PYTHONUTF8`: 0; đã xóa mồi. Soát 5 commit `935d381..73d4205` (dòng thêm vào): 0 mã băm thật, khóa `sk-ant-`/`sk-proj-`/`AIza`, khóa riêng PEM |
| S2 | Đạt | Mục «Từng lỗi được đóng»: câu báo mới đều là hằng, chỉ chèn tên mô hình đã làm sạch hay tên loại lỗi |
| S3 | Không áp dụng | Không có biến cấu hình mới |
| W1 | Không áp dụng | Không đụng `seo_app/wordpress/` |
| W2 | Không áp dụng | Như W1 |
| W3 | Không áp dụng | Như W1 |
| W4 | Không áp dụng | Không có lời gọi mạng mới |
| A1 | Không áp dụng | Không đổi prompt |
| A2 | Đạt | Kết quả AI vẫn qua `clean_ai_text`; tên mô hình trong câu báo qua `model_label` |
| A3 | Đạt | `*_CUSTOM_HEADERS`, `OPENAI_ORG_ID`, `OPENAI_PROJECT_ID` không tới client ở cả lối byte (LC-T034-2) |
| U1 | Đạt | Câu báo dùng `st.error` (Markdown, không `unsafe_allow_html`); «&lt;» chỉ là chữ |
| U2 | Đạt | `server.address = "localhost"` không đổi (`config.toml:5`); lỗi bất ngờ không lộ đường dẫn (mục trên); `app/` không đổi |
| U3 | Đạt | `seo_app/auth.py`, `seo_app/config.py` không đổi; `set_password` báo đúng trạng thái `.env`, không in mã băm hay giá trị biến |
| F1 | Đạt | Bộ ghi `.env` vẫn từ chối liên kết tắt; chỉ ghi file chỉ định |
| F2 | Không áp dụng | Không đụng ảnh |
| F3 | Đạt | `.env` vẫn đọc/ghi `encoding="utf-8"`, ghi nguyên tử; cache SQLite đọc qua tham số, không `eval`/`pickle`; ngày giờ hỏng không lọt lỗi ra trang |
| D1 | Đạt | `uv.lock`, `pyproject.toml` không đổi |
| D2 | Không áp dụng | `.gitignore` không đổi |
| D3 | Đạt | Audit hook: 0 nối ra ngoài; test chỉ dùng thư mục tạm, `.env` canh không đổi |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | Không chạy | `uv.lock` không đổi (đã sạch ở T-114) |
| bandit | Không chạy | Kiểm rút gọn; thay đổi nhỏ, đọc tay hết |
| detect-secrets (`PYTHONUTF8=1`) | 0 mục mới (các mục báo đều có từ trước) | Có (so mã băm với bản cũ, mồi) |
| Soát lịch sử git | Sạch | Có |
| pytest | Cây gộp 556 qua, 0 hỏng; `.env` canh không đổi. Máy đang chạy toàn bộ test nên chỉ chạy chọn lọc | Có |
| ruff 0.16.10 | `All checks passed!` (cây gộp) | Có |

## Báo nhầm đã loại

- `detect-secrets` «Basic Auth Credentials» ở `seo_app/ai/base.py:30`: chú thích liệt kê kiểu chữ bị lọc (một địa chỉ mẫu kèm tên đăng nhập và mật khẩu giả), không phải thông tin đăng nhập thật; có từ trước.
- `detect-secrets` ở `tests/test_env_file.py`: khóa giả của test cũ, có từ trước.

## Điều kiện

Không có.

## Đề xuất

- Đề xuất 4 của Thợ Máy (chặn `<scheme:…>` ngay trong `escape_link_syntax` dùng chung): gia cố, không gấp (mục «Ghi nhận»).

Script thử (đóng gói lỗi của Streamlit, link tự động, tình huống `.env`) và plugin audit hook để ngoài repo, không commit; bản sao ở thư mục ghi chú chung `T-118-la-chan-scripts/`.

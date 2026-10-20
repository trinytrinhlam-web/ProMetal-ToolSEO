# Biên bản bảo mật T-052 · Thẻ ảnh đọc từ tên thư mục Drive (G3-6)

> **Model:** chạy tạm **Claude Opus 5.5** vì tài khoản này không dùng được Fable (chủ dự án đã duyệt). Cần **kiểm lại bằng Claude Fable sau 01/11**.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem trên) |
| Phiếu được kiểm | [T-052](../tickets/T-052-the-anh-theo-ten-thu-muc.md) |
| Phạm vi | diff `origin/main...team/T-052` (gốc chung `132a73d`, HEAD `497aa45`; `main` lúc kiểm `5441a68`): `seo_app/images/tags.py` (mới, 906 dòng), `seo_app/storage/image_tags.py` (mới, 540 dòng), `tests/test_images_tags.py`, `tests/test_soi_loi_t052.py`, 2 báo cáo. Code ứng dụng tại `f771a0e` (lượt 2 của Thợ Máy, không đổi tới `497aa45`). Code xung quanh: `seo_app/images/folders.py` (`ImageRef`, T-048), `seo_app/images/alt.py` (T-050), `seo_app/storage/drafts.py`, `app/views/write.py` |
| Ngày | 2026-10-20 (bắt đầu 15:00, phần 1 lúc 15:31 +07) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** (chi tiết ở mục Kết luận, viết ở phần 3) |

## Tóm tắt (cho chủ dự án)

Phần quan trọng nhất **an toàn**: chữ riêng trong tên thư mục (tên khách, số điện thoại, địa chỉ, câu "ra lệnh", ký tự vô hình) **không bao giờ** đi ra khỏi module thẻ. Tôi tự thử 40.000 đường dẫn ngẫu nhiên ghép từ chữ riêng, chữ trong danh sách và ký tự lạ: mọi thẻ ra đều là chữ do code viết sẵn, không lọt một mảnh chữ riêng nào. App không ghi gì vào thư mục ảnh (tôi chụp tên, cỡ, giờ sửa, mã băm mọi file trước và sau: không đổi). Kho thẻ sửa tay chỉ ghi `data/image_tags.sqlite`; hard link và junction đặt vào chỗ file đều bị gỡ, file bên ngoài không bị đụng.

Chỗ còn yếu là **nhận ra ảnh AI chỉ dựa vào tên**: thư mục tên "Ảnh minh họa", "trí tuệ nhân tạo", hay ảnh tạo bằng Copilot, Designer, Leonardo… vẫn bị coi là **ảnh thật**, nên khi có giao diện (T-056) ảnh AI có thể được tả như công trình thật của Pro-Metal. Cần sửa ở một phiếu dọn và trong giao diện **trước khi gộp T-056** (người dùng phải thấy và đổi được "Ảnh thật / Ảnh AI"). Ngoài ra có vài lỗi nhỏ: file thẻ bị làm độc có thể làm treo phần thẻ ảnh (cần chương trình lạ chạy trên máy).

Kết luận: **ĐẠT CÓ ĐIỀU KIỆN**, gộp vào `main` được ngay; điều kiện đi vào phiếu dọn mới, T-055, T-056, T-063, T-069 và sổ rủi ro.

## Kết quả công cụ quét

Máy Windows 11 Pro (10.0.26300), Python 3.12, worktree `wt-T-052`, nhánh `team/T-052` tại `497aa45`.

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit 2.10.1 | `uv export --frozen --no-hashes --no-emit-project` → 69 gói ghim (`pillow==13.0.0`, `pillow-heif==1.8.1`, `streamlit==1.65.0`). Nguồn PyPI: **No known vulnerabilities found**. Nguồn OSV (`-s osv`): **No known vulnerabilities found**. Môi trường đã cài (`--path .venv/Lib/site-packages`): **No known vulnerabilities found** (bỏ qua `seo-app` vì là chính dự án) | Có. `git diff --quiet origin/main team/T-052 -- uv.lock pyproject.toml`: không đổi, nên kết quả giống `main`. Lưu ý LC-T058-4 còn đó: cơ sở dữ liệu của pip-audit có thể chậm hơn khuyến cáo mới nhất |
| bandit 1.9.4 | `tags.py` + `image_tags.py`: **No issues identified** (1.220 dòng). Toàn bộ `seo_app app scripts`: 10.061 dòng, 1 mục Thấp B101 (`assert`, `seo_app/storage/drafts.py:203`, có từ trước). File test của phiếu (bỏ B101): B311 `tests/test_images_tags.py:902`, `:924`; B608 `tests/test_soi_loi_t052.py:580` | Có. B101 ngoài phạm vi. Mục ở file test là báo nhầm (mục "Báo nhầm đã loại") |
| detect-secrets 1.5.0 | **Chạy với `PYTHONUTF8=1`** (`security.md` mục 5) và luôn có chuỗi mồi trong file có chữ tiếng Việt. (1) 6 file của diff chép ra thư mục riêng + 1 file mồi: **0 mục ở 6 file**, mồi bị bắt. (2) Toàn bộ patch của nhánh (`git log -p origin/main..team/T-052`, 290 KB) + 2 mồi (khóa AWS, `password = …`): bắt **đủ 2 mồi, 0 mục khác**. (3) Toàn lịch sử mọi nhánh (`git log -p --all`, 7,8 MB) + 1 mồi: 84 mục, **tất cả là khóa/mật khẩu giả của test cũ** hoặc câu trong biên bản cũ (`KhoaGia`, `SoiLoi…`, `T026…`, `BIMAT_KHONG_DUOC_IN`, `abcd efgh…`, `mat-khau-thu-123`), không mục nào thuộc file của T-052 | Có. Đối chứng: chạy **không** có `PYTHONUTF8=1` thì file patch có tiếng Việt bị bỏ qua lặng lẽ (chỉ quét được file JSON kết quả), đúng LC-T049-4. Lần đầu tôi quét file ngoài repo bằng tên file thì công cụ ra "0" mà **không bắt mồi**, nên đã bỏ kết quả đó, quét lại trong thư mục riêng với `--all-files` |
| Soát lịch sử git | Lệnh ở `security.md` mục 5 (`grep -inE "api[_-]?key\|password\|secret\|token"`) trên `git log -p origin/main..team/T-052`: 21 dòng, đều là tên hàm `_tokens` (`tags.py:366`), biến `secret`/`secrets` trong test (danh sách chữ riêng **giả** để kiểm không lọt: `tests/test_images_tags.py:428`, `tests/test_soi_loi_t052.py:115`) và một dòng báo cáo Thợ Máy có chữ `_tokens`. `git diff --numstat`: **không có file nhị phân**, không ảnh nào được commit (ảnh trong test tạo bằng Pillow lúc chạy) | Có, đọc từng dòng |
| ruff | `uv run ruff check .`: **All checks passed!** | Có |
| pytest (test liên quan, `rules.md`) | `uv run pytest tests/test_images_tags.py tests/test_soi_loi_t052.py tests/test_images_folders*.py tests/test_ai_images.py -q -p no:cacheprovider -rsx` tại `497aa45` (15:24–15:26): **849 passed, 8 skipped, 8 xfailed, 0 hỏng** | Có. 8 bỏ qua: 2 ca symlink của phiếu (`tests/test_images_tags.py:1346`, `tests/test_soi_loi_t052.py:538`, Windows chưa bật Developer Mode) + 6 ca T-048 (`tests/test_images_folders.py:62` ×4, `:368`, `:381`). 8 xfail: 5 ca SL-T052-9/-10/-11 + 3 ca T-048 (R2-1 ×2, R2-2) |
| Gộp với `main` | `git merge-tree --write-tree origin/main team/T-052` → cây `316b9d6`, **không xung đột** (exit 0). Dựng cây gộp bằng `git archive` vào thư mục tạm, chạy `tests/test_images_tags.py tests/test_soi_loi_t052.py tests/test_images_folders.py tests/test_images_folders_soi_loi.py tests/test_ai_images.py tests/test_soi_loi_t050.py` (15:29–15:30): **1095 passed, 8 skipped, 23 xfailed, 0 hỏng** | Có: `seo_app` được nạp từ đúng thư mục cây gộp (in `seo_app.__file__`); cây gộp có `alt.py` mới của T-062 và `naming.py`, `process.py` của T-049. 23 xfail = 8 ở trên + 15 ca đã ghi của T-050 (SL-T050-5/-6, dọn ở T-066) |

**Chưa chạy được (không ghi là đạt):**
- **Ca symlink**: Windows này chưa bật Developer Mode, `os.symlink` báo lỗi 1314 (tôi thử lại: đúng 1314). Hai test symlink của phiếu bị bỏ qua; kết luận "symlink cũng bị gỡ" chỉ là **suy luận từ code** (`image_tags.py:443` kiểm `is_symlink()` ở mỗi lần mở, cùng đường với junction và hard link đã chạy thật).
- **Tên NFD thật từ ổ Mac** (APFS, Google Drive for Desktop trên Mac): chỉ thử được tên NFD ghi lên NTFS (Soi Lỗi `test_invisible_nfd_and_fullwidth_names_on_disk_give_clean_tags`, và thử ngẫu nhiên của tôi có 20% phần NFD). Chưa chạy trên Mac.
- Không chạy toàn bộ pytest (theo `rules.md`, Chỉ Huy chạy khi gộp).

## Thử độc lập của Lá Chắn

Script nằm ngoài repo (thư mục tạm của phiên), không sửa code hay test. Chạy bằng `.venv` của worktree.

| # | Thử gì | Kết quả |
|---|---|---|
| T1 | **A3, thử ngẫu nhiên 40.000 đường dẫn** (hạt giống 52052): ghép 1–7 mảnh từ 17 chữ riêng (tên khách, số điện thoại, địa chỉ, `IGNORE ALL RULES`, `<script>`, email, `C:\Users\Lam`, `My Drive`…) và 19 chữ trong danh sách; chèn 14 ký tự vô hình/hướng chữ/ngắt dòng (U+200B, U+200F, U+2028, U+2029, U+061C, U+FEFF, U+FFF9, U+E0041, U+202E, U+2066, U+00AD, U+034F, U+FE0F, U+3164) ở vị trí ngẫu nhiên; 20% mảnh NFD, 10% mảnh toàn chiều rộng; 11 kiểu dấu tách | **0 thẻ ngoài danh sách, 0 lần lọt chữ riêng** (so cả `project_code`, `category`, `area`, `phase` và `reference()`) |
| T2 | `reference()` | Chỉ 3 nhãn cố định `Hạng mục`, `Khu vực`, `Giai đoạn`; **không** có mã công trình (`tags.py:636-646`) |
| T3 | **YC4, 29 cách đặt tên thư mục ảnh AI** nằm trong `CT012 - Cổng inox - Quận 7/truoc/<tên>/x.png` | Nhận đúng là ảnh AI: `Ảnh do AI tạo`, `ẢnhAI`, `ANHAI`, `anhai`, `AI images`, `GenAI`, `Ảnh Gemini`, `Midjourney`. **Bị coi là ảnh thật, giữ CT012 · Quận 7 · trước:** `Ảnh trí tuệ nhân tạo` (= SL-T052-11), **`Ảnh minh họa`, `Hình minh họa`, `minh hoa`**, `genai` (viết thường), `Ảnh Copilot`, `Bing Image Creator`, `Microsoft Designer`, `Canva`, `Leonardo`, `Ideogram`, `Flux`, `Grok`, `Kling`, `Dreamina`, `ComfyUI`, `Runway`, `Krea`, `Seedream`, `Ảnh do máy tạo`, `Ảnh tạo tự động`, `Ảnh dựng`, `Phối cảnh 3D`, `Render`, `Ảnh АІ` (chữ Kirin). Xem LC-T052-1 |
| T4 | Tên file ảnh AI hay gặp lẫn trong thư mục công trình | Nhận: `Gemini_Generated_Image_….png`, `ChatGPT Image …png`, `DALL·E …webp`, `…midjourney_v6.png`, `Firefly ….jpg`. **Không nhận:** `Designer (3).png` (tên mặc định của Microsoft Designer/Bing), `Copilot_….jpg`, `Leonardo_Kino_XL.jpg`, `ideogram (1).jpeg`. `IMG_0001.jpg`, `image.png` là ảnh thật (đúng) |
| T5 | Nhận nhầm ảnh thật thành ảnh AI (hướng an toàn) | `Nha chi Ai`, `Công ty AI Việt`, `Gemini Tower`, `Lô A, I`, `GPT Plaza` → ảnh AI, mất CT/khu vực. `Nhà anh Hải`, `Mái tôn`, `Nhà chị Ái`, `Thái Sơn` → ảnh thật (đúng). Đánh đổi có chủ ý, không lộ chữ |
| T6 | Dựng `ImageTags(source="ai", …)` có mã CT / khu vực / trước-sau | Cả 3 bị `TagError` (`tags.py:583-586`); chỉ hạng mục được giữ |
| T7 | **App không ghi vào thư mục ảnh**: gốc đặt dưới `Users/Nguyễn Thị Hoa/My Drive/Kho CT999 Quận 1`, 3 thư mục (có tên khách, số điện thoại, thư mục `Ảnh AI`), quét bằng `ImageLibrary.list_folder`, `resolve_many`, `set`, `clear`, `list_manual`; chụp tên, cỡ, `st_mtime_ns`, SHA-256 mọi file/thư mục trước và sau | **Không file nào đổi, không file mới** trong thư mục ảnh. Thẻ ra: `{Hạng mục: Cổng inox, Khu vực: Tân Phú, Giai đoạn: Trước khi làm}`, `{Khu vực: Quận 3, Giai đoạn: Sau khi làm}`, ảnh AI `{}`; không lấy `CT999`, `Quận 1` từ tên gốc |
| T8 | Thời gian đọc thẻ xấu nhất: đường dẫn 1.009 ký tự, 4 tầng, mỗi tầng 250 ký tự đầy dấu tách và chữ trong danh sách | 9,3 ms/ảnh (`tags_for_image`), 10,3 ms (`tags_for_folder`). Không có đường nổ thời gian |
| T9 | **F1, hard link** (Windows tạo không cần quyền quản trị): `data/image_tags.sqlite` là hard link tới một SQLite ngoài `data/` (lúc đầu; sau lần dùng đầu; và hard link ở chỗ `-journal`), rồi `set` | Cả 3 ca: **file ngoài không đổi** (SHA-256), `st_nlink` của file ngoài từ 2 về 1, file trong `data/` là file riêng mới, `-journal` lạ bị gỡ |
| T10 | **F1, junction** đặt vào chỗ file sau lần dùng đầu, trỏ tới thư mục có `giu.txt` | `resolve` không báo lỗi, junction bị gỡ, file mới được tạo, `giu.txt` còn nguyên |
| T11 | **F3, file thẻ độc trong `data/`** (bảng/khung nhìn/trigger dựng sẵn), mỗi ca giới hạn 20 giây | (a) `info` là khung nhìn (VIEW) đệ quy vô hạn: **`_is_healthy` treo**, bị giết sau 20 giây. (b) Bảng `manual_tags` đúng cột kèm trigger `AFTER INSERT` chạy truy vấn đệ quy vô hạn: `_is_healthy` cho qua, **`set` treo**, bị giết sau 20 giây. (c) `manual_tags` là bảng `WITHOUT ROWID`: `_is_healthy` cho qua; `set` và `list_manual` báo "Không mở được file…" ở **mọi lần, kể cả tạo kho mới** (khởi động lại app cũng không khỏi), file không bị đổi tên. (d) `manual_tags` là khung nhìn trỏ bảng không có: như (c). (e) `manual_tags` là khung nhìn đệ quy có cột `ref_key` cố định: `resolve` chạy xong ngay (SQLite tự bỏ điều kiện luôn sai), còn `list_manual` thì treo theo SL-T052-9. Xem LC-T052-2 |
| T12 | **YC4 qua `get`**: lưu thẻ sửa tay "ảnh thật" (CT012, Quận 7) cho `…/genai/x.png`, rồi hỏi bằng `…/GenAI/x.png` (cùng khóa vì không phân biệt hoa thường; thẻ tự đọc của tên mới là ảnh AI) | `resolve` đúng: ảnh AI, chỉ giữ hạng mục. **`get` trả `source='that'`, `CT012`, `Quận 7`.** Xem LC-T052-3 |
| T13 | Câu báo lỗi của kho (`_db_message` với lỗi khóa, hỏng, không mở được; file rác bị đổi tên) | Không câu nào chứa đường dẫn. `recovered_from` là **đường dẫn tuyệt đối** (`image_tags.py:156`, `:381`): hiện tại không hiện ra đâu; điều kiện cho T-056 |
| T14 | Symlink | Không tạo được (lỗi 1314). Chưa chạy |

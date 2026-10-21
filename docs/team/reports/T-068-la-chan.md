# Biên bản bảo mật T-068 · Dọn lỗi Thấp bước code tự sửa alt (sau T-062)

> **Model:** chạy tạm **Claude Opus 5.5** vì tài khoản này không dùng được Claude Fable (chủ dự án đã duyệt). Kiểm lại bằng Fable sau 01/11.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (tạm, xem dòng trên) |
| Phiếu được kiểm | [T-068](../tickets/T-068-don-loi-thap-alt-anh-ai.md) · kiểm **rút gọn** (A1 / C6: ảnh AI luôn có tiền tố do code bảo đảm) |
| Phạm vi | diff `origin/main...team/T-068` (gốc `af7ac41`, HEAD `70087ee`): `seo_app/images/alt.py`, `tests/test_t062_alt_prompt.py`, `tests/test_soi_loi_t062.py`, `tests/test_soi_loi_t068.py`, 2 báo cáo. `main` lúc kiểm: `881548f` (đã có T-052) |
| Báo cáo đã đọc | [Thợ Máy](T-068-tho-may.md), [Soi Lỗi](T-068-soi-loi.md) (ĐẠT CÓ ĐIỀU KIỆN, SL-T068-1 → -3), [Lá Chắn T-062](T-062-la-chan.md) (bảng C1–C6) |
| Ngày | 2026-10-20 (17:31 +07) |
| **Kết luận** | **ĐẠT CÓ ĐIỀU KIỆN** · 0 Nghiêm trọng, 0 Cao, 0 Trung bình, 1 Thấp (LC-T068-1, có từ trước T-068). Gộp vào `main` được ngay |

## Tóm tắt (cho chủ dự án)

Phiếu này **an toàn để gộp**. Bảo đảm quan trọng nhất vẫn giữ: **ảnh do AI vẽ luôn được phần mềm ghi «Minh họa» / «Ảnh minh họa (AI)»**, AI viết gì cũng vậy, nên không bao giờ có chuyện ảnh AI được giới thiệu như công trình thật. Tôi tự thử thêm 60.000 câu trả lời AI viết đủ kiểu lạ (dấu câu trơn, «Minh họa» trong ngoặc, viết hoa, không dấu, gạch đầu dòng, mã HTML, link, giới hạn ký tự rất nhỏ): **không lần nào mất chữ «Minh họa»**; khi AI chỉ trả dấu câu thì phần mềm báo «AI không viết được alt» để anh/chị bấm thử lại. Ảnh thật thì không bao giờ bị gắn chữ «Minh họa». Mã HTML và link trong chữ AI vẫn bị lọc **trước** khi ghép tiền tố, và lọc lại sau khi ghép.

Có **1 điểm nhỏ (mức Thấp)**, đã có từ trước phiếu này: nếu một phiếu sau gọi thẳng hàm làm sạch với giới hạn chú thích dưới 17 ký tự (bỏ qua file cấu hình) thì chú thích ảnh AI chỉ còn mẩu «Ảnh minh h». Hiện **không xảy ra được**, vì file cấu hình không cho đặt dưới 20 ký tự. Nên sửa cùng phiếu dọn 3 lỗi Thấp Soi Lỗi vừa tìm (chữ «Minh họa» bị lặp, chú thích cụt chữ); cả 4 lỗi đều không làm mất tiền tố, không chặn gộp phiếu này hay màn hình chọn ảnh (T-056).

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| LC-T068-1 | Thấp | Với ảnh AI, `caption_max_chars` nhỏ hơn 17 (độ dài «Ảnh minh họa (AI)») thì chú thích là tiền tố bị cắt cụt (`prefix[:limit]`, ví dụ «Ảnh minh h»), không còn đủ «(AI)». Bảo đảm C6 cho chú thích vì vậy dựa vào mức sàn 20 ở **file khác** (`rules.py`), không nằm trong `alt.py`. Có từ trước T-068 (`_with_prefix` không đổi; `main` cho kết quả y hệt). Alt thì T-068 đã chặn: `max_chars` ≤ 9 nay báo `AIError`, trước đây trả «Minh» | `seo_app/images/alt.py:404-409` (`_with_prefix`, nhánh `room <= 0`), `:438`, `:445`; mức sàn `seo_app/content/rules.py:89`, `:485-490` | **Hiện không khai thác được:** `clean_suggestion` chỉ được gọi từ `suggest_alt` (`alt.py:494-499`) với giới hạn lấy từ `load_alt_rules()` (sàn 20) hoặc mặc định 125 / 200; ngoài `alt.py` chưa có code nào gọi (`git grep` trên `main` và nhánh). Chỉ xảy ra nếu phiếu sau (T-056, Giai đoạn 5) gọi `clean_suggestion(..., ai_generated=True, caption_max_chars=<17)` trực tiếp → chú thích «Ảnh minh h» (Lá Chắn thử mọi giới hạn 1–40: cụt ở 1–16) | Trong `clean_suggestion`: ảnh AI mà `max_chars` hay `caption_max_chars` nhỏ hơn `ALT_MIN_CHARS` (20) thì báo lỗi (ví dụ `ValueError` cho lỗi lập trình, hoặc `AIError` câu cố định), không cắt tiền tố; test giới hạn 1–19. Làm cùng phiếu dọn SL-T068-3 (cùng hàm `_with_prefix`) |

Không có lỗi Nghiêm trọng, Cao hay Trung bình.

## Trọng tâm C6 (A1): ảnh AI luôn có tiền tố do code bảo đảm

| Yêu cầu kiểm | Kết quả | Bằng chứng |
|---|---|---|
| Không đường nào trả alt ảnh AI thiếu tiền tố | **Đạt** | `clean_suggestion` (`alt.py:433-446`) chỉ có hai lối ra: `raise AIError(EMPTY_ALT_MESSAGE)` (`:441-442`) hoặc `return` sau khối `if ai_generated:` ghép tiền tố (`:443-445`). Khi tới `:444`, thân alt đã khác rỗng và có chữ (`_meaningful`, `:439`), nên `_with_prefix` đi nhánh ghép `prefix + sep + thân` (`:410`), không đi nhánh `prefix[:limit]`. Thân đã cắt sẵn còn `max_chars − 9` (`:437`, `:439`), nên `_cut` trong `_with_prefix` không cắt nữa; nếu lọc lại làm dài ra (ví dụ `_lower_first` đổi «İ» thành 2 ký tự) thì `clean_alt_text` cắt **từ cuối**, tiền tố ở đầu còn nguyên (với `max_chars` ≥ 10 chỗ cắt luôn sau «Minh họa »). `.rstrip(_ALT_END)` (`:444`) không ăn vào tiền tố vì tiền tố kết thúc bằng chữ «a» |
| Alt chỉ có dấu câu, biểu tượng | **Đạt** (chặt hơn trước) | `_meaningful` (`alt.py:389-392`) chạy **sau** khi bỏ tiền tố AI tự viết và **sau** khi cắt (`:439`), nên «???», «Minh họa ???», «**Minh họa**», «(Minh họa)», «“Ảnh minh họa (AI)”: …», `<script>…</script>` đều báo `AIError` với đúng câu `EMPTY_ALT_MESSAGE` (Lá Chắn thử 22 kiểu × giới hạn 20, 125: 0 lần ra alt). Chú thích như vậy thì còn đúng tiền tố «Ảnh minh họa (AI)» (`:440`, `:409`) |
| Tiền tố AI tự viết đủ kiểu | **Đạt về C6** | `_strip_ai_prefix` (`alt.py:363-386`) chỉ **bỏ bớt** chữ ở đầu (và một ngoặc đóng ở cuối); tiền tố chuẩn luôn do code ghép lại sau đó. Vòng lặp luôn dừng: mỗi vòng bỏ ít nhất 8 ký tự («minh họa»). Regex `_AI_PREFIX` (`:347-350`) dùng `.match` (neo đầu chuỗi), không có lượng từ lồng nhau, chạy trên chữ đã gộp một dòng: không có nguy cơ ReDoS. Kiểu chưa nhận ra (không dấu, gạch đầu dòng, `` ` ``…) chỉ làm **lặp** chữ «minh họa» sau tiền tố chuẩn (SL-T068-1, -2), không làm mất tiền tố |
| Cắt theo giới hạn nhỏ | **Đạt cho alt; chú thích xem LC-T068-1** | Lá Chắn thử mọi cặp `max_chars` × `caption_max_chars` từ 1 tới 40: alt báo `AIError` khi `max_chars` ≤ 9, từ 10 trở lên luôn bắt đầu «Minh họa» và không quá giới hạn; chú thích từ 17 trở lên luôn bắt đầu «Ảnh minh họa (AI)», dưới 17 bị cụt (LC-T068-1, không tới được qua cấu hình). Ở 20–21 phần thân chú thích cụt giữa chữ (SL-T068-3), tiền tố vẫn đủ |
| Ảnh thật không bao giờ bị thêm tiền tố | **Đạt** | Bỏ tiền tố và ghép tiền tố đều nằm trong `if ai_generated:` (`alt.py:435-438`, `:443-445`); `ai_generated` là tham số do code truyền theo nguồn ảnh, AI không quyết. Lá Chắn thử 60.000 cặp ảnh thật: 0 lần đầu ra có «minh» hay «(AI)» mà đầu vào không có |
| Lọc HTML / link chạy **trước** khi ghép tiền tố | **Đạt** | Thứ tự: `_one_line` (`alt.py:321-326`: bỏ ký tự điều khiển, `normalize_meta`, `clean_ai_text`) chạy đầu tiên trên chữ AI (`:433`); bỏ tiền tố trên chữ **đã lọc** (`:436`); `clean_alt_text` lọc lại phần thân (`:439`, qua `_one_line` ở `:333`); `_with_prefix` lọc lại cả chuỗi đã ghép (`:410`). Bỏ tiền tố chỉ bỏ ký tự ở đầu / một ký tự ở cuối, rồi phần thân còn qua bộ lọc hai lần nữa, nên không dựng lại được thẻ hay link. Lá Chắn thử «[Minh họa](javascript:alert(1))», ««<b>Minh họa</b>» <script>…», `<iframe>`, `<a href>`, `</du_lieu_tham_khao>`, `‮`: 0 kết quả còn thẻ HTML trọn hay link Markdown, lọc lại không đổi |
| Test C6 Soi Lỗi bị chỉnh không làm yếu bảo đảm (R5) | **Đạt** | `tests/test_soi_loi_t062.py:482-488`: chỉ với 2 đầu vào không có chữ, số («???», «🔥🔥», 4/19 trường hợp) test đòi `AIError` đúng câu (`match=EMPTY_ALT`, `:62`) thay vì alt có tiền tố; báo lỗi nghĩa là không có alt nào được dùng, nên C6 không yếu đi. Chú thích kỳ lạ vẫn được kiểm đủ điều kiện cũ (`:489-493`). Nếu code lại nhận «???», `pytest.raises` hỏng: test vẫn bắt quay lui. 15 trường hợp còn lại không đổi. Ở 3 test SL-T062 chỉ dòng `@pytest.mark.xfail` được thay bằng chú thích, thân test không đổi. `tests/test_t062_alt_prompt.py` chỉ thêm (172 dòng thêm, 0 dòng xóa): nhóm test C6 cũ giữ nguyên. Đồng ý với Soi Lỗi (người viết test) |

**Thử độc lập** (script tạm ngoài repo, không thêm vào test, không gọi mạng, seed 6868): 60.000 cặp alt / chú thích ảnh AI ghép từ 0–3 tiền tố (20 kiểu: có dấu, không dấu, NFD, viết hoa, NBSP, ký tự rộng 0, gạch mềm, BOM, «(AI)», «Tranh», «Ảnh AI»), 25 kiểu ngoặc / dấu đầu dòng mở đầu (`«`, `“`, `**`, `` ` ``, `_`, `- `, `1. `, `• `, `> `, `{`, `【`…), 18 kiểu dấu nối (có `\n`, `\t`, `→`), 28 kiểu thân (dấu câu trơn, emoji, HTML, `<script>`, link Markdown, `</du_lieu_tham_khao>`, `‮`, NUL, ESC, địa chỉ web, chữ Hán, chữ rất dài, «İstanbul»); `max_chars` 10–500, `caption_max_chars` 17–500. Kết quả:

- 49.085 lần ra kết quả, **tất cả**: alt bắt đầu «Minh họa », chú thích là «Ảnh minh họa (AI)» hoặc bắt đầu «Ảnh minh họa (AI): », không quá giới hạn, một dòng, NFC, không thẻ HTML trọn, không link Markdown, thân alt có chữ, lọc lại không đổi, chạy lại vẫn có tiền tố hoặc báo lỗi.
- 10.915 lần báo lỗi, **tất cả** đúng câu «AI không viết được alt…».
- 578 lần chạy lại `clean_suggestion` trên chính kết quả thì báo lỗi (ví dụ «Minh họa - Minh họa» → bỏ hết tiền tố → rỗng): đúng SL-T068-2 / G1 của Soi Lỗi, không mất tiền tố.
- Ảnh thật 60.000 cặp: 56.793 kết quả, 3.207 báo lỗi; **0** lần thêm «Minh họa» hay «(AI)», 0 lần quá giới hạn.

## Đánh giá 3 lỗi Thấp của Soi Lỗi (SL-T068-1 → -3)

| Mã | Mức Soi Lỗi | Lá Chắn | Lý do | Sửa ngay hay gom |
|---|---|---|---|---|
| SL-T068-1 (tiền tố không dấu, gạch nối, gọi khác bị lặp; alt chỉ «Minh hoa» vẫn nhận) | Thấp | **Đồng ý Thấp**, không phải lỗi bảo mật | Tiền tố chuẩn vẫn đứng đầu; chỉ lặp chữ hoặc alt nghèo nghĩa («Minh họa minh hoa»), vẫn nói đúng là ảnh minh họa. Khả năng gặp thấp: lời dặn `AI_PREFIX_NOTE` (`alt.py:138-140`) đưa sẵn «Minh họa» có dấu. Người dùng duyệt từng alt ở T-056 | **Gom phiếu dọn** |
| SL-T068-2 (tiền tố trong `` ` ``, `_`, sau «- », «1. », «• » bị lặp; chạy lại thì báo lỗi) | Thấp | **Đồng ý Thấp**, không phải lỗi bảo mật | Như trên, không mất tiền tố. Dễ gặp nhất trong 3 lỗi (AI hay trả Markdown). Lưu ý cho T-056: **không** chạy lại `clean_suggestion` trên alt đã làm sạch (kết quả có thể thành `AIError` oan) cho tới khi sửa SL-T068-2 và G1 | **Gom phiếu dọn** |
| SL-T068-3 (chú thích ảnh AI ở 20–21 cụt giữa chữ) | Thấp | **Đồng ý Thấp**, không phải lỗi bảo mật | Tiền tố «Ảnh minh họa (AI)» vẫn đủ; chỉ phần thân cụt 1–2 ký tự, và chỉ khi ai đó hạ `caption_max_chars` xuống 20–21 (mặc định 200). Cùng hàm với LC-T068-1 | **Gom phiếu dọn**, cùng LC-T068-1 |

**Khuyến nghị:** không cần lượt sửa trong T-068; **T-068 gộp được ngay** (điều kiện 2 của Lá Chắn T-062 đã xong: SL-T062-1 → -3 sửa thật, C6 giữ). Gom **SL-T068-1, -2, -3 và LC-T068-1** vào **một phiếu dọn nhỏ** cho Thợ Máy (chỉ `seo_app/images/alt.py`, gỡ `xfail` trong `tests/test_soi_loi_t068.py` khi XPASS, thêm test giới hạn 1–19 cho LC-T068-1); nên làm kèm G1 (bỏ dấu câu đầu thân ảnh AI) và G4 (cắt thô chữ AI, ví dụ 4 × `max_chars`, trước khi bỏ tiền tố). Phiếu dọn **không chặn T-056**, nhưng nên xong **trước khi đóng Giai đoạn 3** (trước khi chủ dự án dùng việc viết alt hằng ngày). Người sửa giữ nguyên C6: mọi test C6 hiện có (`tests/test_t062_alt_prompt.py`, `tests/test_soi_loi_t062.py::test_ai_image_alt_and_caption_always_start_with_prefix`, `tests/test_soi_loi_t068.py::test_c6_holds_for_prefix_styles_code_does_not_strip`) phải qua; Lá Chắn kiểm rút gọn C6.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` (đặt `PYTHONUTF8=1`) trên 6 file của diff: 0 phát hiện; chuỗi mồi bắt được (mục Công cụ). Soát 5 commit `origin/main..team/T-068` (`git log -p`, lọc `api_key\|password\|secret\|token\|sk-…\|AIza\|AKIA\|ghp_\|PRIVATE KEY`): 1 dòng khớp, là chữ `max_tokens` trong báo cáo Soi Lỗi, không phải bí mật |
| S2 | Đạt | Lỗi mới duy nhất là câu cố định `EMPTY_ALT_MESSAGE` (`alt.py:65`, `:442`), không chép chữ AI, không có đường dẫn hay khóa. Diff không thêm `print`, log, `st.*` |
| S3 | Không áp dụng | Không có biến môi trường mới; `.env.example` không đổi |
| W1 | Không áp dụng | Không đụng `seo_app/wordpress/`, không có đường `publish` / `future` |
| W2 | Không áp dụng | Như W1 |
| W3 | Không áp dụng | Không gửi HTML lên WordPress. Alt / chú thích vẫn qua `clean_ai_text` trước và sau khi ghép tiền tố (mục C6). Nhắc lại cho T-054 / T-056: gỡ ký tự rộng 0 rồi `html.escape(..., quote=True)` khi ghi alt vào thuộc tính HTML (`alt.py:24-26`; «<» đứng riêng vẫn còn, G5 Soi Lỗi) |
| W4 | Không áp dụng | Không có client HTTP mới |
| A1 | Đạt | C6 (mục trên). Lời dặn gửi AI không đổi: `alt_system`, `alt_prompt`, `reference_lines` không có trong diff, nên tách dữ liệu / chỉ thị giữ như T-062 (`alt.py:283`, `:298`) |
| A2 | Đạt | Kết quả AI vẫn là dữ liệu chưa tin: kiểm khuôn `AltSuggestion` (`alt.py:492-493`), qua `clean_suggestion` trước khi dùng; T-068 còn chặt hơn (alt không có chữ bị từ chối, `:439-442`). Việc alt vẫn tắt tìm web, AI không có công cụ (`:476-478`, không đổi) |
| A3 | Không áp dụng | Diff không đổi chữ gửi AI (chỉ đổi bước làm sạch chữ AI trả về) |
| U1 | Không áp dụng | Không đụng `app/`, không có `unsafe_allow_html` |
| U2 | Không áp dụng | Không đụng đăng nhập, `.streamlit/config.toml` |
| U3 | Không áp dụng | Như U2 |
| F1 | Không áp dụng | Diff không đọc / ghi file |
| F2 | Không áp dụng | Không đụng xử lý ảnh, EXIF / GPS |
| F3 | Đạt | Không `eval`, `pickle`, `yaml.load`; không đọc file. bandit 0 |
| D1 | Đạt | `uv.lock`, `pyproject.toml` không đổi (`git diff --name-only origin/main...team/T-068 -- uv.lock pyproject.toml .gitignore .env.example app config seo_app/ai seo_app/content`: 0 file); không thư viện mới |
| D2 | Không áp dụng | `.gitignore` không đổi |
| D3 | Đạt | Test dùng `AltSuggestion` / provider giả; bộ chặn mạng chung `tests/conftest.py` vẫn bật; 912 test liên quan qua không gọi mạng |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | **Không chạy (không áp dụng):** `uv.lock`, `pyproject.toml` không đổi so với `main` | — |
| bandit | `uvx bandit seo_app/images/alt.py`: **No issues identified** (391 dòng, 0 `#nosec`). 3 file test (`-s B101`, bỏ cảnh báo `assert`): **No issues identified** (989 dòng) | Có |
| detect-secrets | `PYTHONUTF8=1 uvx detect-secrets scan <6 file của diff>`: **0 phát hiện**. **Thử chuỗi mồi** (security.md mục 5): chép `alt.py` (có chữ tiếng Việt) ra thư mục tạm ngoài repo, thêm một khóa AWS giả: có `PYTHONUTF8=1` thì bắt được («AWS Access Key», dòng 502); không đặt thì 0. Đã xóa file mồi | Có |
| Soát lịch sử git | `git log -p origin/main..team/T-068` (5 commit), lọc mẫu khóa và từ khóa: chỉ 1 dòng chữ `max_tokens` trong báo cáo | Có |
| pytest (test liên quan) | `uv run pytest tests/test_t062_alt_prompt.py tests/test_soi_loi_t062.py tests/test_soi_loi_t068.py tests/test_ai_images.py tests/test_soi_loi_t050.py -q -p no:cacheprovider -rfEX` trên `70087ee`, Windows, 17:24:25 → 17:25:30: **912 passed, 38 xfailed in 57.56s**, 0 hỏng, 0 XPASS (38 xfail = 23 SL-T068 mới + 15 dấu cũ của `test_soi_loi_t050.py`). Toàn bộ pytest: Chỉ Huy chạy khi gộp (quy tắc 2026-10-20) | Có |
| ruff | `uv run ruff check .`: **All checks passed!**; `ruff format --check` 4 file `.py` của diff: đã đúng định dạng | Có |
| Thử gộp | `git merge-tree --write-tree origin/main team/T-068` (`main` `881548f`): cây `6dcc767`, mã thoát 0, **không xung đột** | Có |
| Test trên cây đã gộp | `main` đã có T-052, có test gọi `alt.py` (`tests/test_soi_loi_t052.py`: `suggest_alt`, `alt_prompt`; `tests/test_images_tags.py`: `reference_lines`; cả hai dùng hàm T-068 không đổi hoặc alt giả có chữ). Xuất cây `6dcc767` bằng `git archive` ra thư mục tạm ngoài repo, chạy bằng môi trường của worktree: `pytest tests/test_soi_loi_t052.py tests/test_images_tags.py tests/test_soi_loi_t068.py tests/test_soi_loi_t062.py tests/test_t062_alt_prompt.py` 17:30:54 → 17:32:03: **776 passed, 2 skipped, 28 xfailed**, 0 hỏng, 0 XPASS. 2 skipped = test symlink của T-052 (Windows chưa bật Developer Mode, có từ trước); 28 xfail = 23 SL-T068 + 5 SL-T052-9 → -11 | Có |

## Báo nhầm đã loại

Không có: `detect-secrets` và bandit không báo gì trên diff. Dòng khớp duy nhất khi soát lịch sử git là chữ `max_tokens` trong `docs/team/reports/T-068-soi-loi.md` (gợi ý G4), không phải bí mật.

## Ghi nhận khác (không phải lỗi bảo mật)

- **G4 của Soi Lỗi (chạy chậm với chữ AI cực dài):** `_strip_ai_prefix` nay chạy trên chữ AI chưa cắt, mỗi vòng sao chép phần còn lại nên thời gian tăng theo bình phương số tiền tố lặp. Chữ AI bị chặn bởi `max_tokens = 2000` của `[tasks.alt]` (`config/ai.toml:77`), cỡ vài nghìn ký tự, chạy vài phần trăm giây; ảnh có chữ «hãy lặp Minh họa 100.000 lần» cũng không vượt được `max_tokens`. Không phải lỗi; đề xuất cắt thô trong phiếu dọn để bước làm sạch không phụ thuộc cấu hình.
- **Đổi hành vi ảnh thật** (Thợ Máy, Rủi ro mục 2): alt ảnh thật chỉ có dấu câu nay báo lỗi, chú thích như vậy để trống; dấu chấm cuối bỏ trước khi cắt. Chặt hơn, không phải lỗi bảo mật.
- **Chú thích lỗi thời trong test:** `tests/test_soi_loi_t062.py:472` vẫn ghi `LONG_PREFIX` «hiện báo «không viết được alt» (SL-T062-3…)» dù T-068 đã sửa; chỉ là chữ, phiếu dọn có thể sửa luôn.
- **LC-T062-1 (từ T-062) vẫn theo dõi** ở phiếu Ngòi Bút (chú thích trong `config/content.toml` rằng quy tắc và ví dụ `[alt]` được gửi cho hãng AI), không thuộc phạm vi T-068.

## Điều kiện (ĐẠT CÓ ĐIỀU KIỆN)

T-068 **gộp được ngay**; nó hoàn tất điều kiện 2 của Lá Chắn T-062 (SL-T062-1 → -3, giữ C6). Các việc sau không chặn gộp T-068 hay T-056:

1. **Phiếu dọn mới → Thợ Máy**, phạm vi `seo_app/images/alt.py` và `tests/test_soi_loi_t068.py` (gỡ `xfail` khi XPASS), **trước khi đóng Giai đoạn 3**: sửa SL-T068-1, -2, -3 và **LC-T068-1** (ảnh AI với giới hạn dưới 20 thì báo lỗi, không cắt tiền tố; test giới hạn 1–19); nên kèm G1 và cắt thô (G4). Giữ nguyên mọi test C6; Lá Chắn kiểm rút gọn C6.
2. **Chuyển cho T-056** (giao diện duyệt alt), thêm vào điều kiện 4 của Lá Chắn T-062: gọi `suggest_alt` với `rules=load_alt_rules()` (không tự truyền giới hạn nhỏ cho `clean_suggestion`); không chạy lại `clean_suggestion` trên alt đã làm sạch hay alt người dùng sửa tay cho tới khi phiếu dọn ở mục 1 gộp; khi ghi alt vào HTML thì gỡ ký tự rộng 0 rồi `html.escape(..., quote=True)`.

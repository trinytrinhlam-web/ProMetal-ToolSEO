# Biên bản bảo mật T-032 · Bộ lọc hồ sơ nhận nhãn gõ sai và nhãn trên tiêu đề

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: Claude Opus 5.5 (**Opus tạm**: Fable bị giới hạn tới 01/11, chủ dự án duyệt chạy tạm; kiểm lại bằng Fable sau 01/11) |
| Phiếu được kiểm | [T-032](../tickets/T-032-loc-ho-so-nhan-go-sai.md) |
| Phạm vi | `git diff origin/main...team/T-032` (gốc `53c5d0d`, đầu nhánh `da33f5b`): `seo_app/content/rules.py`, `seo_app/content/prompts.py`, `config/business_profile.md`, 4 file test, 2 báo cáo |
| Ngày | 2026-10-16 |
| **Kết luận** | **ĐẠT** |

## Tóm tắt (cho chủ dự án)

Bộ lọc mới an toàn hơn bản đang chạy: gõ nhãn hơi sai (dính chữ, không dấu, ngoặc tròn, "chưa xác nhận", bị xuống dòng) hay gắn nhãn lên tiêu đề thì phần đó vẫn không tới AI. Phần hồ sơ hiện tại AI thấy **giống hệt** trước (đã so từng ký tự). Còn vài cách gõ hiếm vẫn lọt (ví dụ nhãn in đậm bên trong ngoặc `[**CẦN XÁC NHẬN**]`, hay gạch nối `[CẦN-XÁC-NHẬN]`); các cách này bản cũ cũng lọt, nên không phải lỗi mới. Anh cứ gõ nhãn đúng mẫu `[CẦN XÁC NHẬN — lý do]` là chắc chắn nhất.

## Lỗi phát hiện

Không có lỗi Nghiêm trọng, Cao hay Trung bình. Không có chỗ nào **lùi** so với `main`: mọi trường hợp lọt dưới đây cũng lọt trên `main` (trên `main`, các dòng dưới tiêu đề có nhãn vốn không bị giấu).

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| 1 | Thấp · **không chặn** | **SL-T032-4** (Soi Lỗi): tiêu đề có nửa nhãn, rồi dòng trống, rồi nửa sau. Đã tái hiện. | `seo_app/content/rules.py:107-113` | `## 7 [CẦN XÁC` / dòng trống / `NHẬN]` / `- BIMAT` / `## 8` → dòng trống làm tiêu đề thôi chờ, AI thấy `## 7 [CẦN XÁC`, `NHẬN]`, `- BIMAT`. Cần **hai** lỗi gõ cùng lúc (nhãn bị xuống dòng và chèn dòng trống giữa nhãn), nhìn trong Notepad đã thấy nhãn vỡ. | Khi `pending`, coi dòng trống như dòng `>` (chờ tiếp, giữ dòng trống lại để trả về nếu không ghép được). Hoặc an toàn hơn: hết chờ mà không ghép được thì vẫn giấu cả mục (nửa nhãn trên tiêu đề = có ý muốn giấu). |
| 2 | Thấp · **không chặn** | **SL-T032-5** (Soi Lỗi): tiêu đề thụt lề có nửa nhãn. Đã tái hiện. | `rules.py:124` (chỉ xét nhãn trọn), `rules.py:137` (chỉ tiêu đề không thụt lề mới chờ) | `- t` / ` ## 7 [CẦN XÁC` / `NHẬN]` / `- BIMAT` / `## 8` → khối `- t …` bị giấu (thừa), nhưng `- BIMAT` tới AI. Cũng cần hai lỗi gõ cùng lúc (thụt lề tiêu đề và nhãn bị xuống dòng). | Ở dòng 124, xét thêm `_ends_with_partial_tag(line)` cho tiêu đề thụt lề và cho vào nhánh chờ như tiêu đề thường. |
| 3 | Thấp · không chặn | **LC-T032-1** (mới): ký tự khác khoảng trắng nằm giữa ngoặc mở và chữ, hoặc giữa các chữ của nhãn, thì nhãn không được nhận: `[**CẦN XÁC NHẬN**]` (in đậm Markdown bên trong ngoặc), `["CẦN XÁC NHẬN"]`, `[⚠ CẦN XÁC NHẬN]`, `[: CẦN XÁC NHẬN]`, `[CẦN-XÁC-NHẬN]`, `[CẦN_XÁC_NHẬN]`. | `rules.py:22` | `- x [**CẦN XÁC NHẬN**] BIMAT` → cả dòng tới AI. Kiểu in đậm có thể gặp vì file là Markdown; tuy vậy `**[CẦN XÁC NHẬN]**` (in đậm bên ngoài) vẫn được nhận. Trên `main` cũng lọt. | Cho phép một số **có giới hạn** ký tự không phải chữ: `[\[(][\W_]{0,4}(?:CAN\|CHUA)[\W_]{0,4}XAC[\W_]{0,4}NHAN`. **Phải giữ giới hạn `{0,4}`**: dùng `[\W_]*` thì `[` cũng khớp `\W`, chuỗi `[[[[…` thành bậc hai (ReDoS). Thêm test tốc độ cho chuỗi toàn `[`. Gộp vào phiếu sửa SL-T032-4/5. |
| 4 | Thấp · ghi nhận | Dòng chỉ có `#` (tiêu đề rỗng) kết thúc mục đang giấu. | `rules.py:27`, `rules.py:114-117` | `## 7 [CẦN XÁC NHẬN]` / `- a` / `#` / `- BIMAT` → `- BIMAT` tới AI. Theo đúng thiết kế (Markdown coi `#` là tiêu đề cấp 1 rỗng; Thợ Máy có test ghim `##` rỗng). Rất hiếm người gõ một dấu `#` trơn giữa mục. | Không cần sửa. Nếu sửa: tiêu đề rỗng không kết thúc mục giấu (lọc thừa). |

Đã ghi nhận lại, ngoài phạm vi phiếu (Soi Lỗi đã nêu, biên bản T-022-024 đã nêu): ngoặc khác `{…}`, `<…>`, `【…】`; chữ Kirin/Hy Lạp giống chữ Latinh trong nhãn; tiêu đề kiểu gạch dưới `=====`; nhãn vắt qua hai ý khác nhau. Không lùi so với `main`.

**Đề xuất:** Chỉ Huy mở một phiếu nhỏ (Thấp) gộp #1, #2, #3, làm khi tiện, trước khi chủ dự án điền nhiều chữ vào mục 7 hồ sơ.

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt | `detect-secrets` trên 9 file đổi: `{}`. Soát `git log -p origin/main..HEAD` theo `api_key/password/secret/token`: không có dòng nào. |
| S2 | Không áp dụng | Diff không có log, `st.error`, thông báo lỗi mới. |
| S3 | Không áp dụng | Không có biến cấu hình mới. |
| W1 | Không áp dụng | Không đụng `seo_app/wordpress/`. |
| W2 | Không áp dụng | Như trên. |
| W3 | Không áp dụng | Như trên. |
| W4 | Không áp dụng | Như trên. |
| A1 | Đạt | Hồ sơ là chỉ thị của chủ dự án, không phải dữ liệu ngoài. Ý chưa xác nhận bị bỏ trước khi vào prompt: `rules.py:93` (cả khối, nhãn tìm trên các dòng nối nhau), `rules.py:114-117` (mục dưới tiêu đề có nhãn), `rules.py:107-113`, `137` (tiêu đề có nửa nhãn), `rules.py:124` (tiêu đề thụt lề). Đã thử 26 cách viết nhãn/tiêu đề xấu (`probe.py` trong scratchpad): các kiểu trong phiếu, NFKC (`⁽ ⁾`, `﹙ ﹚`), dấu tổ hợp chen giữa chữ, ngắt dòng bằng U+2028, U+2029, `\f`, tiêu đề có tab, `(chua xac nhan)` đều bị lọc. Chỗ lọt chỉ là lỗi #1–#4 ở trên, đều Thấp và đều đã lọt trên `main`. `prompts.py:42` vẫn chạy `_neutralize` (bỏ ký tự vô hình, vô hiệu thẻ giả) như cũ, chỉ đổi tên nhập. |
| A2 | Không áp dụng | Không đổi lớp AI. |
| A3 | Đạt | Phần AI thấy của hồ sơ thật **giống hệt** `main`: nạp `rules.py` của `origin/main` (qua `git archive`) và của nhánh cạnh nhau, chạy trên hồ sơ của mỗi bên: `equal: True 4826` ký tự. Diff `config/business_profile.md` chỉ có dòng bắt đầu bằng `>` (đã lọc diff: không dòng `+`/`-` nào khác). Bộ lọc chỉ thêm chiều giấu: lọc thừa với `(cần xác nhận …)`, `[CẠN XÁC NHẬN]` là chủ ý của phiếu và chấp nhận được. |
| U1 | Không áp dụng | Không đụng `app/`. |
| U2 | Không áp dụng | Như trên. |
| U3 | Không áp dụng | Như trên. |
| F1 | Không áp dụng | Không có đường dẫn mới; vẫn đọc `config/business_profile.md` cố định (`rules.py:15`). |
| F2 | Không áp dụng | Không đụng ảnh. |
| F3 | Đạt | Đọc hồ sơ vẫn `encoding="utf-8-sig"`; không `eval`/`pickle`. **ReDoS:** 3 mẫu mới/đổi đều tuyến tính. `rules.py:22`: mỗi điểm bắt đầu là `[`/`(`, `\s*` không khớp được ngoặc nên dừng ở ngoặc kế. `rules.py:29`: `[A-Z\s]*$` cũng dừng ở ngoặc kế. `rules.py:27`: neo đầu dòng, độ dài cố định. Đo thử đầu vào xấu (nhiều tiêu đề nửa nhãn + nhiều `[` + chuỗi khoảng trắng dài): 20.000 → 0,44 giây, 40.000 → 0,87 giây (gấp đôi đầu vào, gấp đôi thời gian). Vòng lặp vẫn một lượt qua các dòng, mỗi khối tìm nhãn một lần. |
| D1 | Đạt | `pyproject.toml`, `uv.lock` không đổi. `uvx pip-audit`: No known vulnerabilities found. |
| D2 | Đạt | `.gitignore` không đổi. |
| D3 | Đạt | 4 file test chỉ gọi `confirmed_profile`/`load_rules` trên chuỗi và file tạm; không nhập `socket`, `requests`, thư viện AI. Bộ chặn mạng chung trong `tests/conftest.py` vẫn bật. |

## Đánh giá 2 lỗi Thấp của Soi Lỗi

- **SL-T032-4 (#1): Thấp, không chặn gộp.** Tái hiện đúng như Soi Lỗi ghi. Không lùi: trên `main` cả mục dưới tiêu đề có nhãn **trọn** cũng tới AI. Muốn lọt phải gõ sai hai chỗ cùng lúc, và nửa nhãn hiện rõ trong Notepad.
- **SL-T032-5 (#2): Thấp, không chặn gộp.** Tái hiện đúng. Cùng lý do: cần hai lỗi gõ cùng lúc, không lùi so với `main`.

Hai lỗi này cùng lỗi #3 nên làm chung một phiếu nhỏ. Không cần đưa vào sổ rủi ro đã chấp nhận (mục 6 của `security.md`) nếu có phiếu sửa; nếu chủ dự án không muốn sửa thì ghi vào sổ.

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | No known vulnerabilities found | Thư viện không đổi trong phiếu |
| bandit (`seo_app/content`) | No issues identified | Có |
| detect-secrets (9 file đổi) | 0 kết quả | Có |
| Soát lịch sử git (`origin/main..HEAD`) | Không có dòng chứa `api_key`, `password`, `secret`, `token` | Có |
| pytest | 3323 passed, 4 skipped, 12 xfailed, **1 failed**: `tests/test_soi_loi_t028.py::test_other_threads_reading_environment_never_fail` | Test chạy đua nhiều luồng của T-028 (`seo_app/ai`), phiếu này không đụng. Chạy riêng 3 lần: cả 3 lần qua. Thợ Máy và Soi Lỗi đã gặp cùng test chập chờn này (Soi Lỗi ghi là T-034). Không liên quan T-032. |
| ruff | All checks passed! | Có |

## Báo nhầm đã loại

- Test T-028 hỏng một lần trong lượt chạy toàn bộ: chập chờn do chạy đua luồng, ngoài phạm vi diff (xem trên).

## Điều kiện (nếu ĐẠT CÓ ĐIỀU KIỆN)

Không có. Kết luận ĐẠT; lỗi #1–#4 đều Thấp. Đề xuất phiếu sửa #1–#3 ở trên là khuyến nghị, không phải điều kiện gộp.

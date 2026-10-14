# Báo cáo T-022 · Kiểm thử hồ sơ doanh nghiệp (Soi Lỗi)

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus |
| Phiếu | [T-022](../tickets/T-022-sua-ho-so-doanh-nghiep.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành. **Kết luận: ĐẠT** (phần của T-022). Lỗi bộ lọc còn lại thuộc T-024, đã có test `xfail` chờ sửa. |

## Tóm tắt (cho chủ dự án)

Đã kiểm hồ sơ doanh nghiệp bằng test chạy trên chính file thật. Phần AI đọc được đúng như Ngòi Bút báo cáo: quy tắc mục 8 còn đủ, không lọt dòng chưa xác nhận hay dòng ghi chú, không có năm thành lập hay giá tiền, có hotline/Zalo và đúng 9 địa chỉ. Bộ lọc vẫn còn vài kẽ hở khi gõ lạ (đang được sửa ở phiếu T-024); file hiện tại không dính kẽ hở nào.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/test_business_profile.py` | 24 test mới: 18 test trên file thật + test bộ lọc, 6 test `xfail(strict=True)` cho lỗi bộ lọc |
| `docs/team/reports/T-022-soi-loi.md` | Báo cáo này |

Không sửa code ứng dụng, không sửa hay nới lỏng test có sẵn.

## Bằng chứng

Trước khi thêm test (nhánh `team/T-022`, commit `73ba839`):

```
$ uv run pytest -q
1871 passed, 3 xfailed in 158.96s
$ uv run ruff check .
All checks passed!
```

Sau khi thêm test:

```
$ uv run pytest -q tests/test_business_profile.py
18 passed, 6 xfailed in 0.39s
$ uv run pytest -q
1889 passed, 9 xfailed in 140.75s (0:02:20)
$ uv run ruff check .
All checks passed!
```

**Kiểm tra đối chứng** (cố tình làm hỏng `config/business_profile.md` tạm thời, rồi khôi phục bằng `git checkout`), để chắc test bắt được lỗi thật:

| Làm hỏng | Test báo đỏ |
|---|---|
| Đưa lại dòng quy tắc cũ có nhãn `[CẦN XÁC NHẬN]` vào mục 8 | `test_every_rule_line_of_section_8_survives_filter`, `test_section_8_has_no_tagged_line`, `test_section_8_is_complete_in_visible_profile` |
| Nhãn ở dòng thứ hai của một ý nhiều dòng (mục 3) | `test_multiline_items_are_kept_or_dropped_whole` |
| Thêm "Thành lập năm 2012", "từ 450.000đ/m2", bỏ một địa chỉ | `test_no_founding_year_…`, `test_no_vnd_price_…`, `test_section_3_lists_exactly_nine_addresses` |
| Ghi chú `  > …` có dấu cách đứng trước; gạch đầu dòng mẫu trống "- Câu hỏi…:" | `test_no_note_line_reaches_ai`, `test_no_empty_template_bullet_reaches_ai` |

## Các test mới (viết theo cấu trúc, không chép câu chữ)

- Mục 8: lấy mọi dòng dưới tiêu đề `## 8.` từ file → từng dòng phải còn sau `confirmed_profile`, mục 8 không có dòng nào mang nhãn, mục 8 ở phần AI thấy giống hệt mục 8 gốc (bỏ ghi chú).
- Nhãn: không còn `[CẦN XÁC NHẬN` (so sau NFC + `casefold`, kể cả viết thường hay cách khoảng); mọi dòng có nhãn trong file gốc đều vắng.
- Ghi chú: không dòng nào ở phần AI thấy bắt đầu bằng `>` (kể cả có khoảng trắng phía trước); mọi dòng ghi chú gốc đều vắng.
- Ý nhiều dòng: mỗi gạch đầu dòng cùng dòng thụt sau nó được giữ cả hoặc bỏ cả (chặn câu cụt và thông tin chưa xác nhận lọt nửa ý).
- Mục 7: không có gạch đầu dòng mẫu bỏ trống (kết thúc bằng `:`).
- Khung: `load_rules().business_profile` đúng bằng kết quả lọc; system prompt có đúng một thẻ mở `<ho_so_doanh_nghiep>` và một thẻ đóng (đứng riêng dòng); nội dung trong khung là hồ sơ, đủ số dòng; số hotline không xuất hiện ở phần chỉ thị ngoài khung.
- `BAN-GIAO.md` mục 7.4: không có năm `19xx/20xx` đứng riêng (ngày quyết định dạng `2026-10-14` không tính), không "thành lập năm…", không "N năm kinh nghiệm"; không có số tiền (đ, đồng, VND, k, nghìn, triệu…); có "Hotline", "Zalo" và số điện thoại; cả hồ sơ chỉ có **một** số điện thoại; mục 3 có đúng 9 số nhà khác nhau; địa chỉ trụ sở ở mục 1 nằm trong danh sách mục 3.
- File: đủ mục 1–8 theo thứ tự.

## Lỗi tìm thấy

### Lỗi bộ lọc (thuộc T-024, không chặn T-022 vì file hiện tại không dính)

Tái hiện bằng `confirmed_profile` của `seo_app/content/rules.py` hiện tại. Mỗi lỗi có test `xfail(strict=True, reason="chờ T-024…")` trong `tests/test_business_profile.py`; khi T-024 sửa xong, test sẽ chuyển sang "XPASS" và báo đỏ để bỏ dấu `xfail`.

| # | Cách tái hiện (đầu vào) | Mong đợi | Thực tế |
|---|---|---|---|
| SL-022-1 | `"- Khách đã phục vụ: khoảng 500\n  khách [CẦN XÁC NHẬN]"` (nhãn ở dòng cuối của ý) | Bỏ cả ý | Còn `"- Khách đã phục vụ: khoảng 500"`: con số chưa xác nhận lọt vào AI |
| SL-022-2 | `"- Khách…: khoảng 500 [CẦN XÁC NHẬN]\n  khách trong năm"` (nhãn ở dòng đầu) | Bỏ cả ý | Còn câu cụt `"khách trong năm"` |
| SL-022-3 | `"  > ghi chú"` (dấu cách trước `>`) | Bỏ dòng | Còn `"> ghi chú"` (dấu cách đầu bị `strip()` ăn mất nên trông như ghi chú nhưng vẫn vào AI) |
| SL-022-4 | `"\t> ghi chú"` (tab trước `>`) | Bỏ dòng | Còn `"> ghi chú"` |
| SL-022-5 | Dòng có nhãn ở dạng NFD (`unicodedata.normalize("NFD", "[CẦN XÁC NHẬN]")`, kiểu gõ/dán trên Mac) | Bỏ dòng | Dòng còn nguyên, nhãn lọt vào AI |
| SL-022-6 | `"[CẦN XÁC NHẬN]"` (dấu cách không ngắt giữa chữ, hay gặp khi dán từ web/Word) | Bỏ dòng | Dòng còn nguyên. **Không nằm trong yêu cầu T-024** (đề xuất bên dưới) |

Đã thử thêm và **đạt**: nhãn viết thường `[cần xác nhận]` bị bỏ đúng (`test_lowercase_tag_is_dropped`).

### Ghi nhận nhỏ (không phải lỗi, không chặn)

- `_neutralize` trong `seo_app/content/prompts.py` chuẩn hóa NFKC cả hồ sơ, nên trong prompt dấu "…" thành "...". Nội dung không đổi nghĩa; chỉ lưu ý nếu sau này hồ sơ có ký tự như "m²" (sẽ thành "m2"). Test khung đã so với kết quả qua `_neutralize`.
- Phần AI thấy còn ngày quyết định dạng `2026-10-14` (mục 1, mục 3). Không phải năm thành lập, nhưng là chi tiết nội bộ AI không cần; Ngòi Bút có thể cân nhắc chuyển sang dòng ghi chú `>`.

## Đối chiếu tiêu chí xong

- [x] Quy tắc dòng 112 cũ còn sau `confirmed_profile` (`test_every_rule_line_of_section_8_survives_filter`, `test_section_8_is_complete_in_visible_profile`)
- [x] Không còn dòng nào chứa `[CẦN XÁC NHẬN` trong phần AI thấy (`test_no_unconfirmed_tag_reaches_ai_any_case_or_normal_form`, `test_raw_file_really_has_tagged_lines_and_none_survive`)
- [x] Không dòng ghi chú `>` nào lọt (`test_no_note_line_reaches_ai`)
- [x] Hồ sơ nằm đúng trong khung `<ho_so_doanh_nghiep>` (`test_profile_sits_exactly_inside_its_frame_in_system_prompt`)
- [x] Quyết định 7.4: không năm thành lập, không giá VND, có hotline/Zalo, 9 địa chỉ mục 3 (các test `test_no_founding_year_…`, `test_no_vnd_price_…`, `test_hotline_and_zalo_visible`, `test_section_3_lists_exactly_nine_addresses`)
- [x] `uv run pytest` và `uv run ruff check .` sạch

## Rủi ro và điểm cần chú ý

- Test đếm địa chỉ dựa vào số nhà đứng trước tên đường viết hoa. Nếu chủ dự án bổ sung chi nhánh (BAN-GIAO 7.4: "cho tới khi anh bổ sung"), test sẽ báo đỏ và phải sửa con số 9 cùng lúc với quyết định mới. Đó là chủ ý: số địa chỉ là quyết định của chủ dự án.
- Test "chỉ một số điện thoại" sẽ báo đỏ nếu sau này thêm số thứ hai; khi đó cập nhật test theo quyết định mới.
- Khi T-024 gộp vào `main`, 5 test `xfail` "chờ T-024" sẽ XPASS và báo đỏ (strict): bỏ dấu `xfail` của chúng trong cùng lần gộp.

## Đề xuất

- (Thợ Máy, T-024 hoặc phiếu sau) Chuẩn hóa khoảng trắng trong nhãn: coi NBSP, nhiều dấu cách, tab giữa các chữ `CẦN XÁC NHẬN` như một dấu cách (SL-022-6).
- (Ngòi Bút) Cân nhắc chuyển các ngày quyết định `(chủ dự án … 2026-10-14)` sang dòng ghi chú `>`.

## Câu hỏi cho chủ dự án

Không có.

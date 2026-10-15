# Báo cáo T-025 · Ổn định các test đo tốc độ chập chờn

| Mục | Nội dung |
|---|---|
| Agent | Soi Lỗi (`soi-loi`) · model: Claude Opus 5.5 |
| Phiếu | [T-025](../tickets/T-025-on-dinh-test-do-toc-do.md) |
| Ngày nộp | 2026-10-15 |
| Kết quả | Hoàn thành (phần Windows mới kiểm bằng đồng hồ giả, chưa chạy trên máy Windows thật) |

## Tóm tắt (cho chủ dự án)

Hai test kiểm "công cụ đo tốc độ có bắt được code chậm không" thỉnh thoảng đỏ oan. Nguyên nhân: công cụ đo đầu vào nhỏ 2 lần liền nhau ngay đầu, nên nếu đúng lúc đó máy bị chậm một nhịp thì cả 2 lần đều bị đo chậm. Nay công cụ đo xen kẽ nhỏ / lớn và lấy lần nhanh nhất. Đo lại 1.000 lần: trước khi sửa hỏng 25 lần, sau khi sửa 0 lần. Ngưỡng 9 giữ nguyên, code chậm vẫn luôn bị bắt, bộ test không chậm thêm đáng kể (khoảng 1,6 giây).

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `tests/timing.py` | (commit `5ff60f3`) Thứ tự đo: nhỏ, rồi từng vòng lớn → nhỏ (tối đa 3 vòng). Tỉ lệ = lớn nhanh nhất / nhỏ nhanh nhất. Vòng 1 chỉ dừng sớm khi tỉ lệ ≤ 6 (`CLEAR_RATIO`); từ vòng 2 dừng khi ≤ 9. `MAX_RATIO = 9`, `MIN_MEASURE = 0,1 s`, `MAX_SECONDS = 5 s` giữ nguyên. |
| `tests/test_soi_loi_t025.py` | (commit `a1d48d4`) Test hồi quy bằng đồng hồ giả: "đợt máy bận" làm việc chậm gấp 2–2,5 lần đặt ở nhiều vị trí. Hàm bình phương luôn bị bắt; hàm tuyến tính luôn qua; tỉ lệ 7 qua, tỉ lệ 9,2 bị bắt; khóa cứng `MAX_RATIO == 9`. (commit `ee41ccb`, phiên này) Thêm 6 test đồng hồ kiểu Windows (bậc 15,625 ms). |

Không sửa code ứng dụng. Không sửa test nào dùng helper (round3/5/6/7, `test_link_escape.py`, `test_sanitize_hardening.py`, `test_soi_loi_t003_t009.py`): chúng hưởng lợi qua `tests/timing.py`.

## Đánh giá 2 commit của lượt trước

- **Đúng hướng.** Thời gian CPU chỉ có thể bị đo *dài ra* khi máy bận, không bao giờ ngắn đi. Nên lấy lần nhanh nhất của mỗi cỡ chỉ đưa tỉ lệ về gần giá trị thật. Đo thêm cỡ nhỏ thì tỉ lệ chỉ tăng, tức là bắt hàm chậm *chặt hơn*. Đo thêm cỡ lớn thì code cũ đã làm sẵn (3 lần).
- **Không nới lỏng.** Ngưỡng, số lần đo cỡ lớn và mốc tuyệt đối đều giữ nguyên. Không skip, không có "hỏng thì chạy lại": helper chỉ đo thêm *trong cùng một lần kiểm*, và vẫn báo lỗi nếu tỉ lệ tốt nhất quá 9. Vòng 1 còn chặt hơn trước (dừng sớm ở 6 thay vì 9).
- **Giới hạn còn lại (suy luận):** hàm bình phương chỉ lọt khi *cả 3* lần đo cỡ nhỏ đều bị đội lên, hoặc cả 3 lần đo cỡ lớn đều may mắn. Trong 1.000 lần đo dưới đây, tỉ lệ thấp nhất của bản bình phương là 11,7 (ngưỡng 9).

## Nguyên nhân, có số đo

Script đo (để ngoài repo) chép đúng thuật toán cũ (`23d493e`) và mới, trả về tỉ lệ cuối cùng. Mỗi lần đo là **một tiến trình Python mới** (vì lỗi cũ hay rơi vào lượt đầu), xen kẽ cũ / mới. Đo 5 trường hợp đúng như trong test: bản bình phương của round6, 3 bản quét lỗi của round7, và hàm tuyến tính `clean_ai_text` của round6. Máy Linux 4 nhân. "Máy bận" = 3 bản `pytest` toàn bộ chạy song song liên tục.

Tỉ lệ đo được (hỏng = bản bình phương ≤ 9, hoặc bản tuyến tính > 9):

| Lúc | Helper | Trường hợp | n | thấp nhất | 5% thấp nhất | trung vị | hỏng |
|---|---|---|---|---|---|---|---|
| Rảnh | cũ | round6 bình phương | 100 | 11,2 | 12,8 | 15,8 | 0 |
| Rảnh | cũ | round7 `_far_title` | 100 | 8,0 | 10,2 | 15,5 | **4** |
| Rảnh | cũ | round7 `_lt_unclosed` | 100 | 7,2 | 9,8 | 14,6 | **3** |
| Rảnh | cũ | round7 `_lt_interrupted` | 100 | 8,2 | 10,9 | 15,0 | **3** |
| Rảnh | cũ | round6 tuyến tính | 100 | 2,6 | 3,2 | 4,2 (cao nhất 7,6) | 0 |
| Bận | cũ | round6 bình phương | 100 | 10,9 | 12,8 | 15,8 | 0 |
| Bận | cũ | round7 `_far_title` | 100 | 8,5 | 9,3 | 15,4 | **4** |
| Bận | cũ | round7 `_lt_unclosed` | 100 | 6,4 | 8,5 | 14,3 | **8** |
| Bận | cũ | round7 `_lt_interrupted` | 100 | 5,5 | 9,7 | 15,2 | **3** |
| Bận | cũ | round6 tuyến tính | 100 | 2,7 | 3,3 | 4,5 (cao nhất 6,9) | 0 |
| Rảnh | **mới** | round6 bình phương | 100 | 13,3 | 14,6 | 16,8 | 0 |
| Rảnh | **mới** | round7 `_far_title` | 100 | 12,2 | 13,9 | 16,0 | 0 |
| Rảnh | **mới** | round7 `_lt_unclosed` | 100 | 11,7 | 13,1 | 15,7 | 0 |
| Rảnh | **mới** | round7 `_lt_interrupted` | 100 | 11,9 | 13,2 | 16,2 | 0 |
| Rảnh | **mới** | round6 tuyến tính | 100 | 3,4 | 3,9 | 4,4 (cao nhất 6,7) | 0 |
| Bận | **mới** | round6 bình phương | 100 | 14,2 | 14,7 | 16,8 | 0 |
| Bận | **mới** | round7 `_far_title` | 100 | 12,5 | 13,4 | 15,8 | 0 |
| Bận | **mới** | round7 `_lt_unclosed` | 100 | 14,1 | 14,7 | 15,9 | 0 |
| Bận | **mới** | round7 `_lt_interrupted` | 100 | 11,9 | 13,6 | 15,8 | 0 |
| Bận | **mới** | round6 tuyến tính | 100 | 3,2 | 3,6 | 4,4 (cao nhất 6,0) | 0 |

**Tổng:** helper cũ hỏng **25 / 1.000** lần đo (10 lúc rảnh, 15 lúc bận), đều ở bản quét lỗi round7 (khớp với 4/80 ở T-024). Helper mới hỏng **0 / 1.000**.

Đọc số: trung vị của bản cũ và mới gần bằng nhau (~15–16, đúng tỉ lệ lý thuyết 16 của hàm bình phương). Khác biệt nằm ở **đuôi thấp**: bản cũ có những lần tỉ lệ rơi xuống 5–8, nghĩa là cỡ nhỏ bị đo chậm gấp 2–3 lần. Hai lần đo cỡ nhỏ của bản cũ đứng liền nhau ở đầu, nên cùng dính một nhịp máy chậm (bộ nhớ đệm nguội, CPU chưa tăng xung, hoặc tiến trình khác chen vào). Bản mới đo cỡ nhỏ thêm sau mỗi lần đo cỡ lớn, nên có ít nhất một lần đo sạch. Bản round6 chỉ hỏng ở máy Ngòi Bút (1/3) mà không hỏng ở đây vì tỉ lệ của nó cao hơn round7 một chút (thấp nhất 10,9 so với 5,5).

## Chạy thật bằng pytest

Chạy 4 test tốc độ bị ảnh hưởng (`test_helper_catches_quadratic_function`, `test_helper_accepts_linear_function`, 3 trường hợp `test_many_lookup_inputs_catch_naive_scan`) cùng cả file `test_soi_loi_t025.py` (lúc đó 17 test), mỗi lần một tiến trình mới:

| Lúc | Số lần | Kết quả | Thời gian mỗi lần |
|---|---|---|---|
| Rảnh | 50 | 50/50 "22 passed" | trung bình 6,1 s, lâu nhất 6,6 s |
| Bận (3 pytest song song) | 100 | 100/100 "22 passed" | trung bình 6,2 s, lâu nhất 8,0 s |

Cộng với 200 lần đo ở bảng trên, mỗi test tốc độ đã chạy **350 lần (150 lần qua pytest + 200 lần qua script), 0 lần hỏng**.

## Thời gian chạy

8 file dùng helper (548 test), chạy xen kẽ cũ / mới, 3 lần mỗi bản:

| Helper | Lần 1 | Lần 2 | Lần 3 | Trung bình |
|---|---|---|---|---|
| Cũ | 48,8 s | 48,6 s | 46,8 s | 48,1 s |
| Mới | 48,8 s | 49,6 s | 50,7 s | 49,7 s |

Tăng khoảng **1,6 s** (hàm bình phương nay luôn đo thêm 2 lần cỡ nhỏ, mỗi lần ≥ 0,1 s). Test mới của T-025 dùng đồng hồ giả, cả file chạy dưới 0,25 s. Toàn bộ bộ test: helper cũ 141 s, helper mới 142 s (lần chạy cuối dưới đây). Một lần chạy khác của bản mới ra 159 s: dao động đến từ test giao diện (`test_app.py` một lần 8,8 s), không phải từ helper. Dưới mốc 20 s.

## Bằng chứng

```
$ uv run pytest
3133 passed, 4 skipped, 9 xfailed, 1 warning in 142.23s (0:02:22)

$ uv run ruff check .
All checks passed!
```

Các test đỏ trên Linux của T-027 đã hết sau khi gộp `main` (T-029, T-030): `uv run pytest` xanh hoàn toàn. 9 xfail và 4 skip có sẵn từ trước, không thuộc phiếu này.

## Đối chiếu tiêu chí xong

- [x] 0 lần hỏng trong ít nhất 100 lần chạy mỗi test đã sửa, có số liệu (bảng "Nguyên nhân" và "Chạy thật bằng pytest")
- [x] Bản bình phương vẫn bị bắt (tỉ lệ thấp nhất 11,7 trên 800 lần đo), bản tuyến tính vẫn qua (cao nhất 6,7 trên 200 lần đo); `test_ratio_just_above_max_is_caught`, `test_limits_are_not_loosened`
- [x] `uv run pytest` và `uv run ruff check .` sạch
- [x] Báo cáo nộp tại `docs/team/reports/T-025-soi-loi.md`

## Rủi ro và điểm cần chú ý

- **Windows chưa chạy thật.** Phần đồng hồ thô (15,625 ms) mới kiểm bằng đồng hồ giả `_CoarseClock` (6 test): hàm tuyến tính qua, hàm bình phương bị bắt. Lưu ý: 6 test này kiểm helper *với* `MIN_MEASURE = 0,1 s` hiện có; tôi thử hạ `MIN_MEASURE` xuống 0,001 thì chúng vẫn qua, nên chúng **không** canh được việc ai đó hạ `MIN_MEASURE`. Việc đó do `test_limits_are_not_loosened` canh (`MIN_MEASURE >= 0.1`). Nên chạy 100 lần trên máy Windows của chủ dự án khi tiện: `for /L %i in (1,1,100) do uv run pytest -q tests/test_soi_loi_round6.py::test_helper_catches_quadratic_function tests/test_soi_loi_round7.py::test_many_lookup_inputs_catch_naive_scan`.
- **Mac chưa chạy.** Theo lý thuyết không có gì riêng (đồng hồ CPU chính xác như Linux).
- Số đo trên là máy cloud 4 nhân. Máy yếu hơn và bận hơn có thể làm đuôi thấp dài thêm. Khoảng cách từ 11,7 tới ngưỡng 9 là khoảng 30%.

## Đề xuất

- (Chỉ Huy) Phiếu này chỉ sửa `tests/`, Lá Chắn kiểm rút gọn (soát bí mật). Diff không có khóa, `.env`, hay gọi mạng (đồng hồ giả, không socket).
- (Soi Lỗi, khi có máy Windows) Chạy lệnh 100 lần ở mục Rủi ro và ghi kết quả vào đây.

## Câu hỏi cho chủ dự án

Không có.

# Báo cáo T-xxx · <Tên việc>

> Sao chép file này thành `docs/team/reports/T-xxx-<mã-agent>.md`. Viết tiếng Việt, ngắn, có bằng chứng.

| Mục | Nội dung |
|---|---|
| Agent | <Tên> (`<mã>`) · model: <model đã dùng> |
| Phiếu | [T-xxx](../tickets/T-xxx-ten-ngan.md) |
| Ngày nộp | YYYY-MM-DD |
| Kết quả | Hoàn thành / Hoàn thành một phần / Bị chặn |

## Tóm tắt (cho chủ dự án)

<2–4 câu: đã làm gì, người dùng thấy gì khác. Không dùng thuật ngữ khi không cần.>

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `đường/dẫn.py` | <một dòng> |

## Bằng chứng

```
$ uv run pytest
<dán dòng kết quả cuối, ví dụ "42 passed in 3.1s">

$ uv run ruff check .
<dán kết quả>
```

<Ảnh chụp hoặc mô tả cách tự kiểm tra trên giao diện, nếu có.>

## Đối chiếu tiêu chí xong

- [x] <tiêu chí 1> (bằng chứng: `file:dòng` hoặc tên test)
- [ ] <tiêu chí chưa đạt> (lý do)

## Rủi ro và điểm cần chú ý

<Chỗ dễ hỏng, giả định đã đưa ra, việc chưa chắc chắn. Ghi "Không có" nếu không có.>

## Đề xuất

<Việc nên làm tiếp, việc thuộc agent khác phát hiện được trong lúc làm. Chỉ Huy sẽ lập phiếu nếu cần.>

## Câu hỏi cho chủ dự án

<Chỉ khi thật sự cần. Mỗi câu trả lời được bằng một từ, kèm đề xuất.>

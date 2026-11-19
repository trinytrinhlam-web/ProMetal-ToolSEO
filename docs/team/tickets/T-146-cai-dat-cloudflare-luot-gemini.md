# T-146 · Cài đặt: mục Cloudflare Workers AI, số lần gọi AI trong ngày (phiếu E)

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-19 |
| Giai đoạn | Chế độ tự động (thiết kế T-141) và ảnh AI (thiết kế T-140) |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | Sau T-142 (client, kiểm token), T-143 (kho đếm), T-148 (đọc `[auto]`, ngày Thái Bình Dương). Thiết kế xếp **đợt 4** (song song T-150, T-151); chỉ sửa `app/views/settings.py` nên chạy sớm hơn được khi ba phiếu trên đã gộp |
| Trạng thái | Mới |

## Mục tiêu

Cài đặt → 🔌 Kết nối có mục «Cloudflare Workers AI (tạo ảnh minh họa)»:

- trạng thái mã tài khoản, token («đã nhập / chưa nhập»);
- nút «Kiểm tra kết nối» (chỉ khi bấm);
- số neuron đã dùng hôm nay và số lần gọi Gemini hôm nay trên máy này;
- một dòng về dữ liệu gửi đi.

## Bối cảnh

- Thiết kế T-140: mục 4 (phần Cài đặt), 2.5 (biến `.env`, token tối thiểu), 2.8 (đếm lượt), mục 6 phiếu E.
- Thiết kế T-141: 2.4 (sổ đếm Gemini, giãn nhịp), 6.3 (đặt lại lúc nửa đêm giờ Thái Bình Dương, khoảng 15:00 giờ Việt Nam mùa đông), 7.1 dòng E (phần Soạn bài của E chuyển sang T-150).
- Biên bản Lá Chắn T-140 (`fb9d2ef`): LC-T140-2, -7, -8. Biên bản Lá Chắn T-141 (`03568dc`): mục 8 dòng E.

## Yêu cầu

1. **Trạng thái khóa:** mã tài khoản, token chỉ hiện «đã nhập / chưa nhập». Không bao giờ hiện giá trị, kể cả 4 ký tự cuối.
2. **Nút «Kiểm tra kết nối»:**
   - chỉ chạy khi bấm, gọi hàm kiểm token của T-142 (không tốn neuron);
   - câu báo cố định qua `escape_markdown`, nói rõ chưa chứng minh quyền Workers AI;
   - lỗi hiện câu tiếng Việt của client, không `st.exception`.
3. **Số đếm trên máy này**, đọc từ kho `data/image_usage.sqlite` (T-143), không bí mật:
   - «Hôm nay máy này đã dùng khoảng X neuron (trần 9.000 của app, đặt lại 7:00)»;
   - «Hôm nay máy này đã gọi Gemini Y lần (ngày của Google, đặt lại khoảng 15:00)». Có trần ở `[auto]` (T-148) thì hiện cả trần.
   - Ghi rõ là số **ước tính, của riêng máy này**: hai máy chia chung hạn mức.
4. **Dòng dữ liệu gửi đi:** app chỉ gửi Cloudflare một câu prompt tiếng Anh; Cloudflare không dùng để huấn luyện (nguồn ở README, T-147).
5. **Mở trang không gọi mạng:** không `st.cache_data`, `st.cache_resource` quanh lệnh mạng; không hiện mã tài khoản, token, số neuron thô của Cloudflare (chỉ số app ước tính).
6. **Test AppTest** với client giả, kho đếm trong thư mục tạm, dưới bộ chặn mạng: không lộ giá trị `.env`; nút chỉ gọi khi bấm (đếm lệnh = 0 khi mở trang); số đếm đúng; câu lỗi đúng. Chạy lại các test cũ chặn in giá trị `.env` và đếm huy hiệu của trang Cài đặt (`test_soi_loi_t084.py`, `test_t101_settings_google.py`).

## Phạm vi

- **Được sửa:** `app/views/settings.py`, test mới `tests/test_t146_*.py`.
- **Không được sửa:** `app/views/write.py` (T-150), `seo_app/**` (chỉ dùng API của T-142, T-143, T-148), `README.md` (T-147), `config/**`.
- **Ngoài phạm vi:** giao diện bước ảnh, màn hình duyệt cuối (T-150).

## Yêu cầu bảo mật riêng (điều kiện Lá Chắn)

U1 (chữ hiện thuần), U2 (không đường dẫn đầy đủ), S2 (không in bí mật).

- **LC-T140-2** (phần giao diện): Cài đặt chỉ hiện «đã nhập / chưa nhập», không 4 ký tự cuối.
- **LC-T140-7** (phần hiện): số neuron là số app ước tính, của máy này.
- **LC-T140-8** (phần giao diện): kiểm token chỉ chạy khi bấm, câu báo nói rõ chưa chứng minh quyền Workers AI.
- Biên bản T-141 mục 8 dòng E: dòng «đã gọi Gemini X lần» đọc từ sổ đếm, không bí mật.

## Tiêu chí xong

- [ ] Yêu cầu 1–6, có test.
- [ ] Test liên quan + test trang Cài đặt có sẵn qua; `uv run ruff check .` sạch.
- [ ] Báo cáo `docs/team/reports/T-146-hoa-si.md`.

## Kiểm thử và kiểm định

- Soi Lỗi: Có (không lộ giá trị, nút chỉ khi bấm).
- Lá Chắn: rút gọn (U1, S2, LC-T140-2).

## Lưu ý chung

- Chỉ chạy test trong worktree của phiếu (`D:/ProMetal-ToolSEO/wt-T-146`), **không** chạy trong `D:/ProMetal-ToolSEO/ProMetal-ToolSEO`.
- Không chạy toàn bộ `uv run pytest`: chạy test liên quan, test của mọi nơi gọi hàm sửa, `uv run ruff check .`.
- Tham số test lớn kèm `ids=` ngắn.
- Test không gọi AI, Cloudflare, Google, WordPress thật. Lần gọi thử Cloudflare thật chỉ ở buổi thử cùng chủ dự án.
- Không đọc `.env`, không in hay commit khóa; `detect-secrets` (`PYTHONUTF8=1`, có file mồi) sạch.
- Đổi kỳ vọng test cũ: theo R5.

## Ghi chú của Chỉ Huy

- Lập 2026-11-19 từ thiết kế T-140/T-141 (phiếu E, mục 7 của `docs/team/reports/T-141-tho-may.md`; biên bản Lá Chắn `fb9d2ef`, `03568dc`). Worktree `wt-T-146`, nhánh `team/T-146`.

# Tiến độ dự án SEO App (Pro-Metal, suachuacuasat.com)

_Cập nhật: 2026-10-14, 21:20 giờ Việt Nam. Người ghi: Chỉ Huy (Claude)._

File này tóm tắt toàn bộ công việc: đã làm tới đâu, đang làm gì, còn lại gì. Chi tiết từng phiếu xem ở [`docs/team/board.md`](docs/team/board.md).

## 1. Tóm tắt nhanh

- Đã xong: bộ khung app, kết nối WordPress (chỉ tạo bản nháp), AI viết bài bằng Claude (bước 1–3 của trang Soạn bài), đội agent và quy trình kiểm tra bảo mật.
- Gần xong, chờ đưa lên GitHub: tự lưu bài đang soạn (F5 không mất bài) và ô nhập khóa API trong Cài đặt.
- Còn lại: thêm AI ChatGPT/Gemini, thử mù mô hình, ảnh, tối ưu SEO on-page, kế hoạch và lịch đăng, đăng lên WordPress thật.
- Bộ kiểm tra tự động: khoảng 1.870 bài kiểm tra, đều qua.

## 2. Lộ trình theo giai đoạn

| Giai đoạn | Nội dung | Trạng thái |
|---|---|---|
| 0 | Bộ khung: app Streamlit, đăng nhập bằng mật khẩu, `run.bat` / `run.command`, README | ✅ Xong |
| 1 | WordPress: kiểm tra kết nối, chuyên mục/thẻ, tạo bài nháp, tải ảnh, ảnh đại diện | ✅ Xong |
| 2 | AI viết bài | 🟡 Đang làm (xem mục 3) |
| 3 | Ảnh: chọn ảnh từ thư mục, nén WebP, đổi tên chuẩn SEO, **giữ nguyên GPS**, alt bằng AI, ảnh AI kèm prompt | ⚪ Chưa làm |
| 4 | Tối ưu on-page: meta title/description, schema, liên kết nội bộ (plugin SiteSEO) | ⚪ Chưa làm |
| 5 | Kế hoạch & lịch: nhận kế hoạch (file / dán / Google Sheets), AI đề xuất, hẹn giờ đăng, gửi bài lên WordPress | ⚪ Chưa làm |
| 6 | Theo dõi thứ hạng qua Search Console | ⏸ Chờ anh quyết có giữ không |

## 3. Giai đoạn 2 chi tiết

| Việc | Trạng thái |
|---|---|
| Lớp AI chung + Claude (Anthropic), mô hình từng việc trong `config/ai.toml` | ✅ Xong |
| Quy trình: ý định tìm kiếm → nghiên cứu đối thủ → dàn ý (anh duyệt) → viết → AI tự rà soát và sửa | ✅ Xong |
| Viết lại từng phần, quay lại bản trước | ✅ Xong |
| AI kiểm tra văn phong, tô câu có vấn đề, nút Áp dụng / Bỏ qua | ✅ Xong |
| Gia cố bảo mật: lọc HTML/link độc trong chữ AI, hiển thị an toàn (T-001 → T-015) | ✅ Xong, đã lên GitHub |
| Tự lưu bài đang soạn, mở lại / xóa bài dở (T-016, T-017, T-021) | 🟡 Làm xong, đã qua kiểm tra; đang sửa 1 lỗi nhỏ cuối rồi đưa lên GitHub |
| Ô nhập khóa API Claude / ChatGPT / Gemini trong Cài đặt → Kết nối (T-020, T-021) | 🟡 Làm xong, đã qua kiểm tra; đưa lên GitHub cùng lượt trên |
| Thêm AI ChatGPT (OpenAI) và Gemini (T-018) | ⏳ **Chờ anh chọn** cách kết nối (thẻ hỏi trong chat) |
| Thử mù mô hình trong Cài đặt (T-019) | ⏳ Làm sau T-018 |

Trên trang Soạn bài, bước 4 (SEO) và bước 5 (Xuất bản) vẫn là **bản demo**. Trang Tổng quan, Kế hoạch và 3 tab đầu của Cài đặt cũng vẫn là demo.

## 4. Việc đang chờ anh

1. **Chọn cách thêm ChatGPT và Gemini** (thẻ trong chat): dùng thư viện chính hãng (em đề xuất) hay tự viết.
2. **PR #3 Hồ sơ doanh nghiệp** (`config/business_profile.md`) đang chờ gộp. Khi chưa gộp, AI viết bài chưa có thông tin riêng của Pro-Metal. Còn một chỗ nhỏ cần chỉnh ở dòng 112 trước khi gộp.
3. **Giai đoạn 6** (theo dõi thứ hạng): có giữ không.
4. Phần "câu chuyện khách hàng thật" trong hồ sơ doanh nghiệp: anh bổ sung sau.

## 5. Việc bắt buộc khi làm phần đăng bài lên WordPress (Giai đoạn 5)

Lá Chắn (agent bảo mật) yêu cầu, vì website **không có bản thử nghiệm**:

- Mặc định mọi bài là bản nháp; đăng ngay hoặc hẹn giờ chỉ khi anh bấm xác nhận.
- Màn hình xác nhận liệt kê **mọi link** trong bài, đánh dấu địa chỉ lạ.
- Lọc toàn bộ HTML cuối cùng trước khi gửi, kể cả phần anh tự gõ.

Danh sách đầy đủ ở cuối [`docs/team/board.md`](docs/team/board.md).

## 6. Quyết định anh đã chốt

- Push thẳng lên nhánh `main`, không tạo nhánh mới; giữ repo gọn.
- Không cần tiết kiệm chi phí mô hình AI.
- Giữ nguyên vị trí GPS trong ảnh (cố ý, cho SEO địa phương).
- Plugin SEO của website: SiteSEO. Không có site thử nghiệm.
- Không dùng năm thành lập, tên tác giả, bảng giá trong bài.
- Khóa API nhập trong app nhưng vẫn chỉ lưu trong file `.env` trên máy, không bao giờ lên GitHub.

## 7. Đội agent

Chỉ Huy (Claude) điều phối. Mọi việc đi qua phiếu → làm → Soi Lỗi kiểm thử → Lá Chắn kiểm bảo mật → mới đưa lên GitHub.

| Agent | Việc | Mô hình |
|---|---|---|
| Thợ Máy | Logic Python (`seo_app/`) | Opus 5.5 |
| Họa Sĩ | Giao diện (`app/`) | Opus 5.5 |
| Ngòi Bút | Prompt, quy tắc văn phong (`config/`) | Opus 5.5 |
| Soi Lỗi | Kiểm thử | Opus 5.5 |
| Lá Chắn | Bảo mật, có quyền chặn | Fable 5.1 (đang tạm chạy Opus 5.5 vì Fable bị giới hạn tới 01/11) |
| Thư Ký | Tài liệu | Sonnet 5.5 |

Hướng dẫn cho AI khác tiếp tục: đọc [`AGENTS.md`](AGENTS.md) trước.

## 8. Ghi chú để làm sau

- Kiểm lại các phiếu T-013 → T-021 bằng Fable 5.1 sau ngày 01/11.
- Thư Ký cập nhật README: nhập khóa API trong Cài đặt → Kết nối, bài đang soạn được tự lưu.
- Meta title/description chưa được lưu vào nháp (làm khi tới Giai đoạn 4).

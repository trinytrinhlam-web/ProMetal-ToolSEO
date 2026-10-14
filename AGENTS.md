# AGENTS.md — Điểm bắt đầu cho mọi AI

Bạn là một AI (Claude, ChatGPT, Gemini, Copilot…) vừa được giao thư mục dự án này. Đọc theo đúng thứ tự dưới đây trước khi làm bất cứ việc gì.

1. `CLAUDE.md`: dự án là gì, các quyết định đã chốt, quy trình nội dung, lộ trình, trạng thái. **Đây là luật gốc của dự án**, áp dụng cho mọi AI chứ không riêng Claude.
2. `docs/team/README.md`: cách đội agent làm việc (ai điều phối, phiếu giao việc, báo cáo).
3. `docs/team/rules.md`: quy tắc bắt buộc cho mọi agent.
4. `docs/team/security.md`: chính sách bảo mật. Mọi thay đổi phải qua cổng bảo mật này.
5. `docs/team/board.md`: bảng việc, cho biết đang làm gì và việc tiếp theo là gì.
6. Hồ sơ vai trò của bạn trong `.claude/agents/<tên>.md`, nếu bạn được giao một vai.

## Bạn là ai trong đội?

- Nếu người dùng giao cho bạn **một phiếu** (`docs/team/tickets/T-xxx-*.md`), bạn là agent ghi trong phiếu. Đọc hồ sơ vai trò tương ứng, chỉ làm trong phạm vi phiếu, xong thì nộp báo cáo theo `docs/team/templates/report.md`.
- Nếu người dùng nhờ bạn **điều phối** hoặc tiếp tục dự án nói chung, bạn đóng vai **Chỉ Huy** (`.claude/agents/chi-huy.md`).

## Ba điều tuyệt đối không làm

- Không đưa khóa API, mật khẩu, file `.env`, file JSON service account vào git, log hay giao diện.
- Không đăng bài công khai lên WordPress (website **không có bản thử nghiệm**, mọi thay đổi là thật). Mặc định chỉ tạo bản nháp.
- Không gọi WordPress, AI hay Google thật trong test.

## Lệnh chuẩn

```bash
uv sync                            # cài thư viện
uv run pytest                      # kiểm thử
uv run ruff check .                # kiểm tra code
uv run streamlit run app/main.py   # chạy app
```

Ngôn ngữ làm việc: **tiếng Việt** (tài liệu, báo cáo, giao diện, trao đổi với người dùng). Tên biến và hàm trong code viết bằng tiếng Anh.

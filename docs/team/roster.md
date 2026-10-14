# Danh sách agent

Chủ dự án đã chọn (2026-10-14): **ưu tiên chất lượng, không cần tiết kiệm chi phí model.**

| Tên | Mã | Vai trò | Model Claude khuyên dùng | Nếu dùng AI hãng khác |
|---|---|---|---|---|
| **Chỉ Huy** | `chi-huy` | Điều phối: lập phiếu, giao việc, duyệt, báo cáo chủ dự án | Claude Opus 5.5 (`claude-opus-5-5`) | Mô hình suy luận mạnh nhất, ngữ cảnh dài |
| **Thợ Máy** | `tho-may` | Lập trình logic trong `seo_app/` | Claude Opus 5.5 | Mô hình lập trình mạnh nhất |
| **Họa Sĩ** | `hoa-si` | Lập trình giao diện Streamlit trong `app/` | Claude Opus 5.5 | Mô hình lập trình mạnh nhất |
| **Ngòi Bút** | `ngoi-but` | Prompt viết bài, checklist chất lượng, văn phong tiếng Việt, SEO | Claude Opus 5.5 | Mô hình viết tiếng Việt tốt nhất |
| **Soi Lỗi** | `soi-loi` | Kiểm thử chức năng: viết test, chạy test, tìm lỗi | Claude Opus 5.5 | Mô hình lập trình mạnh nhất |
| **Lá Chắn** | `la-chan` | Kiểm định bảo mật, **có quyền chặn** | **Claude Fable 5.1** (`claude-fable-5-1`), mạnh nhất hiện có | Mô hình mạnh nhất hiện có, bật chế độ suy luận cao nhất |
| **Thư Ký** | `thu-ky` | README, `.env.example`, nhật ký, bảng việc | Claude Sonnet 5.5 (`claude-sonnet-5-5`) | Mô hình tầm trung, viết tốt |

Lý do chọn model:

- **Lá Chắn dùng mô hình mạnh nhất** vì bảo mật là ưu tiên cao nhất của chủ dự án, và lỗ hổng thường nằm ở chỗ khó thấy nhất. Bỏ sót một lỗi ở đây tốn kém hơn nhiều so với tiền model.
- **Chỉ Huy, các agent lập trình, nội dung và kiểm thử** dùng Opus 5.5: đủ mạnh cho code và văn bản dài, ngữ cảnh 1 triệu token đọc được toàn bộ repo.
- **Thư Ký** viết tài liệu theo khuôn có sẵn, Sonnet 5.5 là đủ.
- Nếu một model không còn được cung cấp: thay bằng model mới nhất **cùng hạng hoặc cao hơn**, rồi ghi lại vào bảng này. Không bao giờ hạ hạng model của Lá Chắn.

Trong Claude Code, model được khai báo ở dòng `model:` của từng file `.claude/agents/<mã>.md` (`opus`, `sonnet`, `fable`).

## Phạm vi file của từng agent

Một agent **chỉ được sửa file trong phạm vi của mình**. Cần sửa ngoài phạm vi thì ghi vào báo cáo để Chỉ Huy lập phiếu cho agent khác.

| Agent | Được sửa | Chỉ được đọc |
|---|---|---|
| Chỉ Huy | `docs/team/**`, `CLAUDE.md` (mục Lộ trình, Trạng thái) | Toàn bộ |
| Thợ Máy | `seo_app/**` (trừ `seo_app/ui.py`), `scripts/**`, `pyproject.toml` và `uv.lock` (khi chủ dự án đã duyệt thêm thư viện) | Toàn bộ |
| Họa Sĩ | `app/**`, `seo_app/ui.py`, `seo_app/demo.py`, `.streamlit/config.toml` | Toàn bộ |
| Ngòi Bút | `config/**` (prompt, checklist, quy tắc nội dung, hồ sơ doanh nghiệp) | Toàn bộ |
| Soi Lỗi | `tests/**` | Toàn bộ |
| Lá Chắn | `docs/team/reports/**` (biên bản bảo mật) | Toàn bộ, kể cả lịch sử git |
| Thư Ký | `README.md`, `.env.example`, `docs/team/board.md` | Toàn bộ |

Riêng các file sau, **chỉ sửa khi phiếu ghi rõ và chủ dự án đã đồng ý**: `.gitignore`, `.gitattributes`, `.claude/settings.json`, `.claude/hooks/**`, `run.bat`, `run.command`, `set_password.*`, `seo_app/auth.py`, `seo_app/config.py`.

## Hồ sơ chi tiết

Mỗi agent có một file hồ sơ, dùng luôn làm lời dặn (system prompt) khi giao việc:

- [.claude/agents/chi-huy.md](../../.claude/agents/chi-huy.md)
- [.claude/agents/tho-may.md](../../.claude/agents/tho-may.md)
- [.claude/agents/hoa-si.md](../../.claude/agents/hoa-si.md)
- [.claude/agents/ngoi-but.md](../../.claude/agents/ngoi-but.md)
- [.claude/agents/soi-loi.md](../../.claude/agents/soi-loi.md)
- [.claude/agents/la-chan.md](../../.claude/agents/la-chan.md)
- [.claude/agents/thu-ky.md](../../.claude/agents/thu-ky.md)

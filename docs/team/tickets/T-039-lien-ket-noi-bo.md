# T-039 · Liên kết nội bộ: chọn ứng viên, AI gợi ý anchor, chèn link an toàn

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-15 |
| Giai đoạn | Giai đoạn 4 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-037 đã gộp (dùng kiểu dữ liệu danh sách bài). T-036 đã gộp (cùng sửa `seo_app/content/prompts.py`) |
| Trạng thái | Chờ T-036, T-037 |

## Mục tiêu

Làm 3 việc, trong đó link chỉ được chèn bằng code:
- gợi ý 2–5 liên kết tới bài/trang **đã đăng** trên site, đúng quy tắc của chủ dự án;
- AI chỉ chọn cụm từ (anchor) có sẵn trong bài;
- code chèn link sau khi người dùng tick duyệt.

## Bối cảnh

Thiết kế: `docs/team/reports/T-033-tho-may.md`:
- mục 4.2 → 4.5;
- mục 6: phiếu "T-036" trong báo cáo, nay là **T-039**.

Yêu cầu gốc: YC-601 → YC-604.

## Phạm vi

- **Được sửa:**
  - mới: `seo_app/onpage/links.py`, `tests/test_onpage_links.py`;
  - `seo_app/content/prompts.py`: chỉ **thêm** tên khung mới vào `DATA_TAGS` và hàm lời dặn.
- **Không được sửa:** `seo_app/sanitize.py`, `clean_ai_text`, mọi bộ lọc đã có; `app/**`; `seo_app/wordpress/**`.

## Yêu cầu (tóm tắt, chi tiết theo thiết kế)

1. **Code chọn ứng viên** theo YC-601, YC-602:
   - link bắt buộc theo phiếu giao bài luôn có mặt;
   - bài hướng dẫn → trang dịch vụ đích + 2–3 bài cùng nhóm (trùng từ không dấu giữa tiêu đề);
   - chỉ lấy từ danh sách **đã đăng**.
2. **AI** nhận danh sách ứng viên (chỉ ID + tiêu đề, **không URL**) và bài viết, mỗi thứ trong một khung dữ liệu. AI trả khuôn pydantic `[{post_id, section, anchor}]`.
3. **Code kiểm từng gợi ý; sai thì bỏ**, không sửa giùm:
   - `post_id` nằm trong ứng viên;
   - anchor có nguyên văn trong thân phần đó, không nằm trong tiêu đề;
   - anchor dài 2–8 từ, không trùng anchor khác;
   - mỗi đích tối đa 1 link, tổng tối đa 5;
   - không 2 link trong cùng một đoạn.
4. **Link lưu riêng** dạng dữ liệu `InternalLink(section, anchor, post_id)`, không nhét vào chữ Markdown.
5. **`apply_links(html, links, index)`:**
   - duyệt **nút chữ** bằng `html.parser`, không dùng regex trên HTML;
   - bọc lần xuất hiện đầu tiên của anchor ở đúng phần;
   - `href` lấy từ danh sách bài, **không bao giờ** từ AI; escape bằng `html.escape(quote=True)`;
   - không chèn bên trong `<a>`, `<h2>`, `<h3>`, `<code>`.

   Kết quả vẫn phải qua `sanitize_html` sau đó (Giai đoạn 5 làm): có test chứng minh `sanitize_html(apply_links(...))` giữ đúng link.
6. **Kiểm link nháp/hỏng** trên HTML cuối (YC-603, YC-604):
   - link cùng tên miền mà không có trong danh sách đã đăng → Chặn;
   - dạng `?p=`, `?page_id=`, `preview=true` → Chặn;
   - link ra ngoài → chỉ liệt kê, không tự gọi tới.
7. **Test:**
   - AI đưa URL lạ, `post_id` lạ, anchor không có trong bài;
   - anchor nằm trong tiêu đề;
   - HTML có sẵn `<a>`;
   - anchor có ký tự đặc biệt;
   - link tới bài `future`/`draft`.

   Có test tốc độ tuyến tính.

## Yêu cầu bảo mật riêng

A1, A2, W3 (không nới bộ lọc nào), U1, D3. Test chứng minh AI không chèn được link ngoài.

## Tiêu chí xong

- [ ] Chọn ứng viên, kiểm gợi ý AI, chèn link an toàn: có test
- [ ] `uv run pytest`, `uv run ruff check .` sạch
- [ ] Báo cáo `docs/team/reports/T-039-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có. Lá Chắn: Có (A1, A2, W3).

## Ghi chú của Chỉ Huy

- Phiên **"Thợ Máy · T-039 Liên kết nội bộ"**, nhánh `team/T-039` (từ `main` sau khi T-036, T-037 gộp).

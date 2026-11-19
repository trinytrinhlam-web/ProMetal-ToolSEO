# T-150 · Giao diện Soạn bài: soạn tự động, khung tiến độ, màn hình duyệt cuối, bước ảnh (phiếu J)

| Mục | Nội dung |
|---|---|
| Giao cho | Họa Sĩ (`hoa-si`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-11-19 |
| Giai đoạn | Chế độ tự động (thiết kế T-141) và ảnh AI (thiết kế T-140) |
| Mức ưu tiên | Cao |
| Phụ thuộc | **Đợt 4**: sau T-149 (và T-142, T-143, T-145 qua T-149). Song song T-151, T-146 (khác file). Nếu T-149 làm «lượt 1 không Cloudflare» thì phiếu này cũng chia hai lượt theo |
| Trạng thái | Mới |

## Mục tiêu

Trên trang Soạn bài:

- nút «🤖 Soạn tự động»; khung tiến độ; chế độ chỉ xem khi bài đang chạy; Dừng, Chạy tiếp, Chạy lại;
- **màn hình duyệt cuối ở bước 5**: nút «Sửa» quay về đúng bước, dấu vàng, **một ô duyệt chung** thay tick từng ảnh;
- bước ảnh theo T-140 mục 4;
- mở bài «Chờ duyệt» gắn kế hoạch thì đọc lại dòng Sheet.

## Bối cảnh

- Thiết kế T-141: 2.2, 2.3, 2.5 (tiến độ, nút, hai tab); mục 3 (3.1–3.6: bố cục, «Sửa», dấu vàng, chặn và cảnh báo, ô duyệt chung, giữ nguyên); 4.4 (ngày giờ hẹn, dòng quá hạn: ngày mai, giờ của dòng); 1.7, 1.10 (`summary_vi`, prompt); 7.2 dòng J; câu trả lời của chủ dự án 1A, 2A, 4A.
- Thiết kế T-140: mục 4 (bước ảnh, màn hình xác nhận). Phần Soạn bài của phiếu E (T-140) chuyển sang phiếu này.
- Biên bản Lá Chắn T-141 (`03568dc`): mục 2 (câu chính thức thay **LC-T140-12**), mục 5 («Ghi SEO» bật sẵn), mục 7, mục 8 dòng J. Yêu cầu sửa của Lá Chắn ở phiếu này: **đọc lại dòng Sheet khi mở bài «Chờ duyệt»** (LC-T141-16) và **«Ghi SEO» bật sẵn chỉ cho bài tự động** (LC-T141-17).
- Mẹo AppTest: nút bị khóa không bấm được; giả cú bấm bằng cách vá `st.button` theo key, kèm ca đối chứng.

## Yêu cầu

1. **Bắt đầu:** bước 1 có nút chính «🤖 Soạn tự động» (từ khóa, ô chất liệu thật không bắt buộc) gọi lượt chạy T-149. Nút cũ «🔎 Phân tích từ khóa» giữ nguyên. Nhận cờ bắt đầu tự động do trang Bài viết đặt (T-152) trong `init_state`.
2. **Khung tiến độ** (LC-T141-20):
   - vòng chờ trong lần chạy trang chỉ **đọc** sổ việc (không mạng, không AI, không ghi đĩa); không `st.fragment(run_every)`; không `st.cache_data`, `st.cache_resource` quanh lệnh mạng;
   - bài đang chạy thì trang **chỉ xem** (không ô sửa, không tự lưu);
   - xong thì `st.rerun()`, mở nháp ở bước 5.
3. **Nút điều khiển:**
   - ⏸ Dừng; ▶ Chạy tiếp; ✖ Bỏ khỏi hàng;
   - 🔁 Chạy lại từ bước này: hỏi xác nhận; không đè ảnh bạn chọn tay, «Để trống chỗ này»;
   - «Chạy tiếp» không tạo lại ảnh đã có.
4. **Màn hình duyệt cuối** (T-141 3.1–3.4):
   - dòng trạng thái (số chỗ vàng, chỗ chặn);
   - bài viết: tô vàng `gaps` và câu cần xem lại, tô đỏ «[cần bổ sung»;
   - thẻ ảnh;
   - SEO: tiêu đề, mô tả, slug, từ khóa chính, xem trước Google, link nội bộ, FAQ;
   - dàn ý thu gọn;
   - khung gửi (Nháp, Hẹn giờ, Đăng ngay như hiện nay).
   - Mỗi phần có «✏️ Sửa»: ghi `_from_review` và chỗ cần mở, rồi chuyển bước. Các bước 1–4 có thanh «Đang sửa bài tự động · ↩ Về bước duyệt».
   - Mọi chữ AI, Sheet, website hiện thuần (`escape_markdown`, ô bảng, `ui.highlight` đã escape); không `unsafe_allow_html` với chữ chưa tin cậy.
5. **Ô duyệt chung** (LC-T141-1, -2, -3; LC-T140-12 bản sửa):
   - **Lúc vẽ màn hình cuối:** lưu vào phiên `{pid: băm byte file đang hiện}` lấy từ `web_info` (cùng byte dựng dòng GPS, ảnh xem trước), cùng lúc với `_wp_shown`.
   - **Lúc tick:** callback chỉ **chép** các giá trị đã lưu sang `altok-`, `altsha-` và `_wp_confirmed`; không đọc lại file, không tính lại băm. Ảnh không có trong bản lưu lần vẽ thì không được duyệt.
   - **Nhãn và khi khóa:**
     - nhãn ghi số ảnh và số ảnh có GPS, ví dụ «…xem cả 4 ảnh ở trên (2 ảnh có GPS)»;
     - ô khóa khi gói chưa dựng được, khi lượt chạy chưa xong, khi còn dòng Chặn;
     - **bắt buộc ở mọi hình thức gửi, cả Nháp**, với nháp có `auto`.
   - **Thẻ ảnh:** dựng từ đúng byte đã băm (`make_preview`), đủ lớn; nhãn nguồn 📁 Tự chọn / ✨ Ảnh AI / 🖐 Bạn chọn; huy hiệu GPS; dấu vàng ảnh tự chọn «xem kỹ nhà khách»; `GPS_PUBLIC_WARNING` trước nút gửi.
   - **Với bài tự động:**
     - chỗ ảnh «sẵn sàng» khi ảnh dùng được và có alt;
     - **lúc gửi**, mọi ảnh sẵn sàng phải có `altsha`; thiếu thì không gửi, báo «chưa duyệt» (hiện `send_draft` chỉ so khi có);
     - giữ so băm byte đọc để tải với `altsha`, dựng lại gói rồi so `_wp_confirmed` ngay trước lệnh mạng đầu tiên (LC-T094-38), **cả Nháp**.
   - **Bài soạn tay:** giữ tick từng ảnh, không đổi gì.
6. **Bỏ duyệt khi sửa** (LC-T141-4): «Sửa» làm đổi ảnh, alt, chú thích, hay «Chạy lại» phần ảnh → `unapprove` ảnh đó; mã băm màn hình đổi nên ô chung bỏ tick (`confirm_box`). Mở nháp vẫn bỏ duyệt khi thiếu băm (như hiện nay).
7. **Mở bài «Chờ duyệt» gắn kế hoạch ở bước 5** (**LC-T141-16**):
   - có Google: đọc lại dòng (`open_row`). Trạng thái đã qua «Đang viết», hay ô Mã bài WordPress có giá trị (máy kia đã gửi) → cảnh báo **đỏ** «dòng này đã có bài trên website từ máy khác»; nút gửi khóa tới khi tick «vẫn gửi» (như khóa gửi trùng T-086);
   - không có Google: cảnh báo vàng;
   - nháp không gắn kế hoạch: không đổi gì.
8. **«Ghi SEO lên website»** (**LC-T141-17**):
   - **bật sẵn chỉ cho nháp có `auto`**: đọc `auto.seo_write` từ nháp, không từ `.env` hay cấu hình; trạng thái nằm trong mã băm như nay; tắt được, tắt rồi tải lại vẫn giữ;
   - bài soạn tay giữ mặc định tắt (Lá Chắn T-042);
   - đường ghi không đổi (`write_seo` chỉ sau `create_draft_with_images` trong cùng cú bấm, chỉ vào mã bài vừa tạo); `MSG_SEO_WILL_SKIP` giữ.
9. **Bước ảnh** (T-140 mục 4):
   - nhãn nguồn; ảnh AI xem trước dựng từ WebP đã lưu (`make_preview`);
   - nút Tạo lại, Ảnh trước, Sửa prompt (hiện `summary_vi` và prompt tiếng Anh bằng `st.code`/`text_area`; sửa xong T-145 kiểm lại cả chuỗi), «Để trống chỗ này»;
   - «✨ AI xem ảnh, viết lại alt» từng ảnh thật, chỉ khi bấm (1A, Lá Chắn T-050 3a);
   - câu báo cố định qua `escape_markdown`; không hiện mã tài khoản, token, số neuron thô.
10. **Sổ ảnh đã gửi:** sau khi website xác nhận đã tạo nháp, ghi các ảnh thư mục đã tải vào sổ ảnh đã gửi (T-143), trong `send_and_record`, không `st.*`. Lỗi sổ không đổi kết quả gửi.
11. **Dòng kế hoạch quá hạn** (2A): ô Ngày điền sẵn ngày mai, ô Giờ giữ giờ của dòng (không có giờ thì `[plan].default_time`).
12. **Test** (LC-T141-21, LC-T140-18), AppTest với lượt chạy giả, AI giả, Cloudflare giả, dưới bộ chặn mạng:
    - **Lượt chạy, trang:** bắt đầu; chỉ xem khi đang chạy; dừng, chạy tiếp; hai tab; F5; mở trang, mở nháp không gọi Cloudflare (đếm = 0).
    - **Ô duyệt chung:** tick chép đúng băm của lần vẽ; file bị thay sau khi vẽ → gửi dừng; thiếu `altsha` → không gửi; Nháp của bài tự động đòi tick, bài tay không đổi; sửa alt → bỏ tick.
    - **Sửa, «Ghi SEO», kế hoạch:** «Sửa» → thanh quay lại → về bước 5; «Ghi SEO» bật sẵn chỉ với nháp tự động, giữ sau tải lại; dòng Sheet đã gửi ở máy khác → đỏ, khóa, tick «vẫn gửi» mới mở; không Google → vàng.

## Phạm vi

- **Được sửa:** `app/views/write.py`, `app/assets/style.css`, `seo_app/ui.py` (chỉ lớp tô vàng cho `gaps` nếu cần), test mới `tests/test_t150_*.py`.
- **Không được sửa:** `seo_app/auto/**` (T-149, T-151), `seo_app/storage/**`, client WordPress, bộ dựng `seo_app/publish/**`, `app/views/home.py`, `app/views/plan.py` (T-152), `app/views/settings.py` (T-146).
- **Ngoài phạm vi:** danh sách «Chờ duyệt», nút lô (T-152); Cài đặt Cloudflare (T-146).

## Yêu cầu bảo mật riêng (điều kiện Lá Chắn)

U1, U2, W1 (đường gửi), W3, A3, D3.

- **LC-T141-1** (băm từ lần vẽ), **-2** (lúc gửi bài tự động mọi ảnh phải có `altsha`, so cả Nháp), **-3** (ô duyệt chung: nhãn đếm ảnh, khi khóa, thẻ ảnh dựng từ byte đã băm, `GPS_PUBLIC_WARNING`), **-4** (sửa, chạy lại thì bỏ duyệt), **-16** (đọc lại dòng Sheet khi mở bài «Chờ duyệt»), **-17** («Ghi SEO» bật sẵn chỉ cho nháp có `auto`), **-20** (khung tiến độ, nút), **-21** (test).
- **LC-T140-12 (bản sửa, biên bản T-141 mục 2):** ảnh tự chọn không bao giờ tự duyệt; bài tự động chỉ gửi được khi ô duyệt chung đã tick; tick ghi duyệt cho đúng ảnh đang hiện, gắn băm từ lần vẽ (LC-T141-1) và mã băm màn hình (LC-T094-38); đòi tick cả ở Nháp; lúc gửi ảnh thiếu băm thì không gửi (LC-T141-2); thẻ ảnh đủ lớn, đúng byte đã băm, nhãn «📁 Tự chọn», GPS, dấu vàng; đổi, bỏ ảnh qua «Sửa»; không đè lựa chọn tay, «Để trống chỗ này»; bài soạn tay giữ tick từng ảnh.
- **LC-T140-13** (phần hiện: ảnh AI ghi nhãn «Minh họa», «Ảnh minh họa (AI)»), **LC-T140-14** (không tạo ảnh khi mở trang, mở nháp, chạy lại trang), **LC-T140-15** (ảnh xem trước từ byte WebP đã lưu, đủ lớn; prompt hiện chữ thuần; không mã tài khoản, token, số neuron thô), **LC-T140-18** (AppTest với Cloudflare giả).
- **LC-T094-38, -41** (mã băm xác nhận; công tắc Hẹn giờ, Đăng ngay mặc định tắt): giữ. T-086, T-089, T-092, T-130, T-137: giữ.

## Tiêu chí xong

- [ ] Yêu cầu 1–12, có test.
- [ ] Test liên quan + test trang Soạn bài và đường gửi có sẵn (`test_app_pages.py`, `test_app_images.py`, T-056, T-086, T-089, T-092, T-102, T-112, T-130, T-137) qua; `uv run ruff check .` sạch.
- [ ] Báo cáo `docs/team/reports/T-150-hoa-si.md`.

## Kiểm thử và kiểm định

- Soi Lỗi: **đầy đủ** (ô duyệt chung, tráo file sau khi vẽ, hai tab, F5, dòng Sheet đã gửi ở máy khác).
- Lá Chắn: **đầy đủ** (đường gửi).

## Lưu ý chung

- Chỉ chạy test trong worktree của phiếu (`D:/ProMetal-ToolSEO/wt-T-150`), **không** chạy trong `D:/ProMetal-ToolSEO/ProMetal-ToolSEO`.
- Không chạy toàn bộ `uv run pytest`: chạy test liên quan, test của mọi nơi gọi hàm sửa, `uv run ruff check .`.
- Tham số test lớn kèm `ids=` ngắn.
- Test không gọi AI, Cloudflare, Google, WordPress thật. Lần gọi thử Cloudflare thật chỉ ở buổi thử cùng chủ dự án.
- Không đọc `.env`, không in hay commit khóa; `detect-secrets` (`PYTHONUTF8=1`, có file mồi) sạch.
- Đổi kỳ vọng test cũ: theo R5.

## Ghi chú của Chỉ Huy

- Lập 2026-11-19 từ thiết kế T-140/T-141 (phiếu J, mục 7 của `docs/team/reports/T-141-tho-may.md`; biên bản Lá Chắn `fb9d2ef`, `03568dc`). Worktree `wt-T-150`, nhánh `team/T-150`.

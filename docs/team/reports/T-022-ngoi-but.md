# Báo cáo T-022 · Soát và sửa hồ sơ doanh nghiệp trước khi AI dùng

| Mục | Nội dung |
|---|---|
| Agent | Ngòi Bút (`ngoi-but`) · model: Claude Opus |
| Phiếu | [T-022](../tickets/T-022-sua-ho-so-doanh-nghiep.md) |
| Ngày nộp | 2026-10-14 |
| Kết quả | Hoàn thành (lượt 2 đã áp dụng trả lời của chủ dự án) |

## Tóm tắt (cho chủ dự án)

Hồ sơ doanh nghiệp đã được soát lại để phần AI đọc được là đúng và đủ. Quy tắc "chỉ nêu địa chỉ ở mục 3" trước đây bị lọc mất, nay đã còn. Chỗ báo giá "15 phút hay 30 phút" chưa thống nhất nên tạm ẩn khỏi AI cho tới khi anh chọn. Mục 7 (chất liệu thật) giờ AI chỉ thấy một dòng "chưa có, không được tự đặt ra"; các dòng mẫu chuyển thành ghi chú có hướng dẫn điền ngay trong file.

## Đã thay đổi

| File | Thay đổi |
|---|---|
| `config/business_profile.md` | Sửa quy tắc bị lọc nhầm, ẩn số liệu mâu thuẫn, đổi mục 7 sang ghi chú, khớp với quyết định ở `BAN-GIAO.md` mục 7.4 |
| `docs/team/reports/T-022-ngoi-but.md` | Báo cáo này |

Chi tiết (trước → sau), số dòng theo file mới:

1. **Quy tắc dòng 112 cũ (yêu cầu 1).** Trước: `- Chỉ nêu địa chỉ đã ghi ở mục 3; không dùng dòng nào mang nhãn [CẦN XÁC NHẬN]` (cả dòng bị lọc vì chứa nhãn). Sau (dòng 127–128): `- Chỉ nêu địa chỉ đã ghi ở mục 3. Thông tin nào không có trong hồ sơ này (email, mạng xã hội, số khách đã phục vụ, thời gian trả báo giá…) thì không nêu và không đoán`. Viết theo hướng AI hiểu được: AI không bao giờ thấy dòng có nhãn, nên quy tắc nói về thông tin *vắng mặt* thay vì nhắc tới nhãn.
2. **Đầu file (yêu cầu 3).** Trước: "File này được đưa nguyên văn vào prompt" (không đúng, vì có lọc). Sau (dòng 3–13): hướng dẫn cho chủ dự án hai loại dòng bị lọc (`>` ở đầu dòng, không có dấu cách phía trước; dòng có `[CẦN XÁC NHẬN`), cách thêm/xóa nhãn, nhắc lưu UTF-8 bằng Notepad.
3. **Báo giá 15 phút / 30 phút (yêu cầu 4, không tự quyết).** Trước: AI thấy `nhận khoảng giá trong khoảng 15 phút (trang Bảng giá ghi 30 phút)`, tức thấy cả hai con số mâu thuẫn. Sau: dòng 75 giữ phần chắc chắn (`gửi 2–3 ảnh hoặc clip ngắn qua Zalo để nhận khoảng giá, miễn phí`); con số tách sang dòng 76 có nhãn `[CẦN XÁC NHẬN …]` nên AI không thấy, chờ anh chọn.
4. **Ghi chú "trang chủ có chỗ ghi 30 phút" ở mục 2.** Trước: AI thấy, dễ khiến AI viết "30 phút". Sau: dòng 32 thành ghi chú `>`. Con số AI dùng vẫn là "30–60 phút" (dòng 31).
5. **Mục 3, khớp `BAN-GIAO.md` 7.4.** Thêm câu `Bài viết nói "có thợ ở mọi khu vực TP.HCM"` (dòng 39–40) đúng như quyết định. Dòng "Website sẽ được bổ sung đủ địa chỉ… thêm vào đây" là việc của chủ dự án, chuyển thành ghi chú `>` (dòng 49). Danh sách địa chỉ giữ nguyên: đếm được đúng 9 địa chỉ (trụ sở + 8 địa chỉ trang Liên hệ), khớp "9 địa chỉ".
6. **Tên tác giả, bảng giá (khớp 7.4).** Dòng 23 và dòng 124–125 thêm "hay tác giả", "bảng giá"; dòng 84 thêm "hay bảng giá".
7. **Mục 7 (yêu cầu 3).** Quyết định: AI **không** nên thấy các gạch đầu dòng trống. Lý do: dòng kiểu "3–5 ca sửa thật đáng nhớ (khu vực, tình trạng…):" để trống trong khung hồ sơ dễ bị AI hiểu là chỗ cần điền, dẫn tới bịa ca sửa. Sau: AI chỉ thấy một dòng (dòng 101–103) "Mục này chưa có nội dung. Không tự đặt ra ca sửa, câu hỏi của khách… chỉ dùng chất liệu thật người dùng nhập cho từng bài." Các dòng mẫu và hướng dẫn điền 3 bước chuyển thành ghi chú `>` (dòng 105–119), đọc rõ bằng Notepad. Đổi tiêu đề thành "Chất liệu thật của xưởng" (bỏ chữ "chủ dự án điền" vì đó là việc cho người, không phải cho AI). Dòng mẫu "ca sửa thật" nhắc thêm "không ghi tên hay số điện thoại khách" (A3). Dòng "Thư mục ảnh công trình thật" bỏ khỏi mẫu: đó là đường dẫn trong máy, đã có chỗ khai báo riêng là `IMAGE_FOLDERS` trong `.env` (`.env.example:51`), AI không cần.

Không đổi: mục 4, 6 và các dòng còn lại của mục 1, 2, 5, 8.

## AI sẽ thấy gì

Kết quả nguyên văn của `uv run python -c "from seo_app.content.rules import load_rules; print(load_rules().business_profile)"` trên file sau khi sửa:

```markdown
# Hồ sơ doanh nghiệp — Cơ khí Pro-Metal (suachuacuasat.com)


## 1. Thông tin chung

- Tên thương hiệu: Cơ khí Pro-Metal (viết trong bài: "Pro-Metal")
- Website: https://suachuacuasat.com
- Hotline / Zalo: 03.4444.07.17 (https://zalo.me/0344440717)
- Trụ sở chính / xưởng: 728/1 Lê Trọng Tấn, Sơn Kỳ, Bình Tân, TP.HCM
- Giờ phục vụ: 6h–21h mỗi ngày; buổi tối và Chủ nhật cần hẹn trước
- Năm thành lập, số năm kinh nghiệm, tên người phụ trách hay tác giả: không dùng trong bài
  (chủ dự án quyết định 2026-10-14). Chỉ được nói "nhiều năm kinh nghiệm".

## 2. Năng lực

- Đội thợ: gần 30 thợ lành nghề
- Thời gian có mặt: 30–60 phút trong nội thành, giờ cao điểm có thể lâu hơn
- Thợ mang sẵn vật tư thông dụng nên phần lớn ca sửa xong trong cùng buổi
- Giá trị cốt lõi: Tận tâm – Trách nhiệm – Chuyên nghiệp

## 3. Khu vực phục vụ

- Phục vụ toàn bộ các quận, huyện, thành phố trực thuộc TP.HCM; có chi nhánh
  ở tất cả các khu vực (chủ dự án xác nhận 2026-10-14). Bài viết nói "có thợ ở
  mọi khu vực TP.HCM"; bài viết theo khu vực được phép nói "có thợ/chi nhánh gần
  khu vực này".
- Địa chỉ cụ thể dùng được (trong bài và schema): trụ sở 728/1 Lê Trọng Tấn,
  Sơn Kỳ, Bình Tân, cùng các địa chỉ ở trang Liên hệ:
  1686 Tỉnh Lộ 10, P. Bình Tân; Lầu 4, 249 Cộng Hòa, P.13, Tân Bình;
  64 Vườn Chuối, Quận 3; 216 Lý Chính Thắng, P.9, Quận 3;
  44 Đinh Công Tráng, Tân Định, Quận 1; 412 Nguyễn Thị Minh Khai, P.5, Quận 3;
  202 Lê Lai, P. Phạm Ngũ Lão, Quận 1; 11A Hồng Hà, P.2, Tân Bình.
  Không tự đặt ra địa chỉ cho khu vực chưa có trong danh sách này.

## 4. Dịch vụ

### Sửa chữa tại nhà
- Sửa cửa sắt: cửa xệ cạ nền, kẹt, bản lề rơ/gãy/rớt, khóa hỏng/kẹt chìa/mất chìa,
  khung mục rỉ cần hàn gia cố, rỉ sét bong sơn, cót két, đóng dội ngược;
  thay chốt, tay nắm, thanh chặn, bánh xe
- Sửa cửa kéo / cửa xếp: kẹt hoặc trật ray, bánh xe mòn, lá cong/gãy,
  khóa sập/khóa chùm hỏng, nhíp/lò xo trợ lực yếu, dàn cửa xệ
- Cửa cuốn: kẹt, lệch nan, trật ray, khóa cơ, va cạ. Lỗi mô-tơ / bộ điều khiển
  báo phương án riêng trước khi làm
- Thợ hàn sắt tại nhà; sửa cổng sắt, cổng sắt mỹ thuật

### Thi công mới
- Cửa sắt, cổng sắt, cửa kéo
- Mái hiên, mái che (có khung inox)
- Cầu thang, lan can sắt và inox
- Cửa, cổng inox
- Cửa nhôm kính (Xingfa), lan can nhôm, vách ngăn nhôm kính văn phòng
- Vách ngăn panel
- Nhà xưởng, văn phòng, công ty: thiết kế, thi công, sửa chữa

## 5. Giá và cam kết

- Không niêm yết một giá chung; giá theo hạng mục, mức hư hỏng, vật tư
- Báo giá nhanh: gửi 2–3 ảnh hoặc clip ngắn qua Zalo để nhận khoảng giá, miễn phí
- Giá qua điện thoại chỉ để tham khảo; giá chốt sau khi đo đạc tại chỗ
- Khảo sát, đo đạc miễn phí trong nội thành, kể cả khi khách không làm
- Báo giá trước khi làm, thu tiền sau khi xong, không phát sinh mập mờ
- Bảo hành 2 năm công thợ và mối hàn, có phiếu ghi hạng mục và ngày làm;
  vật tư thay mới bảo hành theo nhà sản xuất
- Giá tham khảo theo vật liệu (tương đối, chưa có số): sơn dầu thấp,
  sơn tĩnh điện trung bình, mạ kẽm trung bình–cao, giả gỗ và sắt đặc/hoa văn cao
- Không đưa giá cụ thể (VND) hay bảng giá vào bài; hướng khách gửi ảnh/clip qua Zalo để báo giá

## 6. Kiến thức nghề đã có trên website (dùng được trong bài)

- Cửa kéo đẩy nặng thường do nhiều nguyên nhân cùng lúc: ray bẩn, bánh xe mòn,
  khớp lá khô dầu, lò xo trợ lực yếu, dàn cửa xệ
- Ca nhẹ (vệ sinh ray, thay bánh xe, chỉnh khe) khoảng 1 tiếng; ca nặng (nắn ray
  cong, thay lá, căn lại cả dàn) có thể mất cả buổi
- Ca cót két thường xử lý dưới 1 tiếng
- Sơn lại: làm buổi sáng, chiều khô mặt, hôm sau dùng bình thường
- Bảo dưỡng cửa kéo nhà mặt tiền / dùng nhiều: vệ sinh ray, tra mỡ 6 tháng–1 năm/lần
- Bánh xe phải đúng tải trọng; khớp lá tra mỡ chuyên dụng
- Vật liệu thường dùng: sắt hộp, sắt tấm, sắt đặc, hoa văn đúc, sắt mạ kẽm,
  sắt giả gỗ, inox; sơn dầu, sơn tĩnh điện, sơn chống rỉ

## 7. Chất liệu thật của xưởng

- Mục này chưa có nội dung. Không tự đặt ra ca sửa, câu hỏi của khách, sai lầm
  hay gặp, độ dày hoặc thương hiệu vật tư; chỉ dùng chất liệu thật người dùng
  nhập cho từng bài.


## 8. Quy tắc khi AI viết về doanh nghiệp

- Xưng "Pro-Metal" hoặc "chúng tôi"; giọng thợ có nghề, nói thẳng, có ví dụ
- Không bịa số năm kinh nghiệm, số công trình, giá, tên khách hàng, đánh giá;
  không nêu năm thành lập, tên người phụ trách hay tác giả, bảng giá, giá cụ thể
- Không hứa thời gian có mặt nhanh hơn "30–60 phút"
- Chỉ nêu địa chỉ đã ghi ở mục 3. Thông tin nào không có trong hồ sơ này (email,
  mạng xã hội, số khách đã phục vụ, thời gian trả báo giá…) thì không nêu và không đoán
- Lời kêu gọi liên hệ: gửi ảnh/clip qua Zalo 03.4444.07.17 để được báo khoảng giá miễn phí
```

## Các dòng bị lọc

Dòng có nhãn `[CẦN XÁC NHẬN` (4 dòng, đều là thông tin chưa chắc, đúng ý định):

```
 20 | - Email: [CẦN XÁC NHẬN — website chưa có]
 25 | - Mạng xã hội, Google Business Profile: [CẦN XÁC NHẬN — website chưa có liên kết]
 30 | - Khách đã phục vụ: khoảng 500 [CẦN XÁC NHẬN con số và cách đếm]
 76 | - Thời gian trả báo giá qua Zalo: [CẦN XÁC NHẬN — hồ sơ cũ ghi "khoảng 15 phút", trang Bảng giá ghi "30 phút"]
```

Dòng bắt đầu bằng `>` (28 dòng, đều là ghi chú cho chủ dự án): 3–13 (hướng dẫn đầu file), 32 (ghi chú "30 phút"), 49 (ghi chú bổ sung địa chỉ), 105–119 (hướng dẫn và dòng mẫu mục 7).

Kiểm tra chéo: không còn dòng quy tắc hay thông tin dùng được nào bị lọc; trong phần AI thấy không còn chữ `XÁC NHẬN` (`grep -c` = 0).

## Bằng chứng

```
$ uv run pytest -q
1871 passed, 3 xfailed in 105.55s (0:01:45)

$ uv run ruff check .
All checks passed!
```

## Đối chiếu tiêu chí xong

- [x] Quy tắc ở dòng 112 còn nguyên sau `confirmed_profile` (gạch đầu dòng thứ 4 của mục 8 trong phần "AI sẽ thấy gì", nội dung viết lại không chứa nhãn)
- [x] Không còn dòng nào chứa `[CẦN XÁC NHẬN` trong phần AI thấy (xem trên; `grep -c "XÁC NHẬN"` trên kết quả = 0)
- [x] `uv run pytest` và `uv run ruff check .` sạch
- [x] Báo cáo nộp tại `docs/team/reports/T-022-ngoi-but.md`

Yêu cầu bảo mật: A1, không có câu nào kiểu "bỏ qua quy tắc"; các dòng thêm vào đều là giới hạn chặt hơn ("không nêu", "không đoán", "không tự đặt ra"). A3, không có dữ liệu khách hàng; chỉ hotline và địa chỉ cửa hàng công khai. S1, không có khóa hay mật khẩu.

Ví dụ kiểm tra (đầu vào mẫu → đầu ra mong muốn, suy luận, chưa gọi AI thật):
- Bài "sửa cửa kéo Quận 7" → AI viết "có thợ ở mọi khu vực TP.HCM / có thợ gần khu vực này", **không** đưa ra địa chỉ Quận 7.
- Phần kêu gọi liên hệ → "gửi ảnh/clip qua Zalo 03.4444.07.17 để được báo khoảng giá miễn phí", **không** hứa "báo giá trong 15 phút" hay "30 phút".
- Mở bài giới thiệu → không có email, số khách đã phục vụ, năm thành lập.

## Rủi ro và điểm cần chú ý

- Bộ lọc làm theo **từng dòng**: nếu sau này ai thêm nhãn `[CẦN XÁC NHẬN` vào dòng đầu của một gạch đầu dòng nhiều dòng, các dòng tiếp theo vẫn lọt vào AI (thành mẩu câu cụt). Hiện cả 4 dòng có nhãn đều là một dòng, nên chưa xảy ra.
- Dấu `>` có dấu cách đứng trước (ví dụ `  > ghi chú`) **không** bị lọc. Đã ghi rõ trong hướng dẫn đầu file.
- Ghi chú `>` nằm giữa danh sách làm Markdown hiển thị hơi lệch nếu xem trên GitHub; không ảnh hưởng AI hay Notepad.

## Đề xuất

- (Thợ Máy) Cân nhắc cho `confirmed_profile` lọc cả khối gạch đầu dòng (dòng có nhãn + các dòng thụt lề ngay sau nó), và chấp nhận `>` có dấu cách đứng trước. Ngoài phạm vi phiếu này nên chưa làm.
- (Soi Lỗi) Test trên file thật như phiếu ghi; có thể thêm: phần AI thấy chứa "Chỉ nêu địa chỉ đã ghi ở mục 3", không chứa "15 phút", mục 7 không chứa dòng mẫu nào ("Câu hỏi khách hay hỏi nhất").

## Câu hỏi cho chủ dự án

1. **Báo giá qua Zalo trả trong bao lâu?** Hồ sơ cũ ghi "khoảng 15 phút", trang Bảng giá trên website ghi "30 phút". Trả lời: `15` / `30` / `bỏ`. Đề xuất: **30** (khớp website, hứa chậm mà giữ được tốt hơn). Đến khi anh trả lời, AI không nêu con số này.
2. **"Giá tham khảo theo vật liệu" (sơn dầu thấp, sơn tĩnh điện trung bình, mạ kẽm trung bình–cao…), không có số tiền: có được nói trong bài không?** Anh đã chốt không dùng bảng giá; mục này chỉ so sánh rẻ/đắt, không phải bảng giá. Trả lời: `Có` / `Không`. Đề xuất: **Có** (giúp khách chọn vật liệu, không có con số). Hiện đang để AI thấy.
3. **"Mọi khu vực TP.HCM" có gồm vùng Bình Dương và Bà Rịa – Vũng Tàu cũ không?** Từ 1/7/2025 hai tỉnh này đã sáp nhập vào TP.HCM, nên AI có thể hiểu "mọi khu vực TP.HCM" là gồm cả Thủ Dầu Một, Vũng Tàu. Trả lời: `Có` / `Không`. Đề xuất: **Không**, khi đó Ngòi Bút sẽ sửa mục 3 thành "các quận, huyện của TP.HCM cũ (trước sáp nhập)".

## Lượt 2: theo trả lời của chủ dự án

Chỉ Huy chuyển trả lời của chủ dự án (2026-10-14) cho 3 câu hỏi ở trên. Thay đổi trong `config/business_profile.md` (trước → sau):

1. **Thời gian trả báo giá qua Zalo: không nêu.**
   - Bỏ dòng `- Thời gian trả báo giá qua Zalo: [CẦN XÁC NHẬN …15 phút… 30 phút]`. Thay bằng ghi chú `>` (dòng 78): "Chủ dự án chốt 2026-10-14: không nêu thời gian trả báo giá…".
   - Dòng báo giá nhanh (dòng 77) sửa thành "…qua Zalo để được báo khoảng giá miễn phí", khớp đúng câu chủ dự án cho phép.
   - Mục 8 thêm quy tắc: "Không nêu hay hứa báo giá xong trong bao lâu; chỉ viết "gửi ảnh/clip qua Zalo để được báo khoảng giá miễn phí"". Bỏ "thời gian trả báo giá" khỏi danh sách "thông tin không có" vì đã có quy tắc riêng.
2. **Giá tương đối theo vật liệu: không dùng.**
   - Bỏ 2 dòng "Giá tham khảo theo vật liệu (tương đối, chưa có số): sơn dầu thấp…". Thay bằng ghi chú `>` (dòng 84).
   - Mục 8 thêm quy tắc: "Không so sánh rẻ, đắt hay trung bình giữa các vật liệu hoặc cách làm; không nêu bất kỳ con số giá nào".
   - Giữ nguyên các cam kết không phải giá: báo giá miễn phí, khảo sát miễn phí, báo giá trước khi làm, thu tiền sau, bảo hành 2 năm.
3. **Khu vực: có gồm Bình Dương và Bà Rịa – Vũng Tàu cũ.**
   - Mục 3, gạch đầu dòng 1: "Có thợ ở mọi khu vực TP.HCM, kể cả khu vực Bình Dương và Bà Rịa – Vũng Tàu cũ (nay đã sáp nhập vào TP.HCM…)". Không ghi ngày sáp nhập: cụm "từ 1/7/2025" làm test của Soi Lỗi (`test_no_vnd_price_in_visible_profile`, `test_no_founding_year_in_visible_profile`) báo nhầm là giá và năm thành lập; sửa câu chữ thay vì sửa test. Bài theo khu vực được nói "có thợ gần khu vực này".
   - Tách riêng gạch đầu dòng 2 về chi nhánh: "Có chi nhánh ở tất cả các quận, huyện của TP.HCM trước sáp nhập". Lý do: trả lời của chủ dự án nói **có thợ** ở hai khu vực mới, còn xác nhận **có chi nhánh** trước đó là cho các quận huyện TP.HCM cũ. Ngòi Bút không mở rộng chữ "chi nhánh" sang Bình Dương, Vũng Tàu khi chưa có xác nhận. Nếu chủ dự án muốn AI nói "có chi nhánh" ở cả hai khu vực này, chỉ cần sửa dòng này.
   - Địa chỉ cụ thể giữ đúng 9 địa chỉ. Mục 8 thêm: "không đặt ra địa chỉ ở Bình Dương, Vũng Tàu hay khu vực nào khác".

Kiểm tra: trong phần AI thấy không còn chữ `XÁC NHẬN`, `15 phút`, `sơn dầu thấp` (`grep -c` = 0). Các dòng bị lọc lượt 2: 3 dòng có nhãn `[CẦN XÁC NHẬN` (dòng 20, 25, 30: email, mạng xã hội, số khách) và các dòng ghi chú `>` 3–13, 32, 51, 78, 84, 106–120.

### AI sẽ thấy gì (lượt 2)

Kết quả nguyên văn của `uv run python -c "from seo_app.content.rules import load_rules; print(load_rules().business_profile)"`:

```markdown
# Hồ sơ doanh nghiệp — Cơ khí Pro-Metal (suachuacuasat.com)


## 1. Thông tin chung

- Tên thương hiệu: Cơ khí Pro-Metal (viết trong bài: "Pro-Metal")
- Website: https://suachuacuasat.com
- Hotline / Zalo: 03.4444.07.17 (https://zalo.me/0344440717)
- Trụ sở chính / xưởng: 728/1 Lê Trọng Tấn, Sơn Kỳ, Bình Tân, TP.HCM
- Giờ phục vụ: 6h–21h mỗi ngày; buổi tối và Chủ nhật cần hẹn trước
- Năm thành lập, số năm kinh nghiệm, tên người phụ trách hay tác giả: không dùng
  trong bài. Chỉ được nói "nhiều năm kinh nghiệm".

## 2. Năng lực

- Đội thợ: gần 30 thợ lành nghề
- Thời gian có mặt: 30–60 phút trong nội thành, giờ cao điểm có thể lâu hơn
- Thợ mang sẵn vật tư thông dụng nên phần lớn ca sửa xong trong cùng buổi
- Giá trị cốt lõi: Tận tâm – Trách nhiệm – Chuyên nghiệp

## 3. Khu vực phục vụ

- Có thợ ở mọi khu vực TP.HCM, kể cả khu vực Bình Dương và Bà Rịa – Vũng Tàu cũ
  (nay đã sáp nhập vào TP.HCM). Bài viết nói "có thợ ở mọi khu vực TP.HCM"; bài
  viết theo khu vực được phép nói "có thợ gần khu vực này".
- Có chi nhánh ở tất cả các quận, huyện của TP.HCM trước sáp nhập; bài viết về
  các khu vực này được nói "có chi nhánh gần khu vực này".
- Địa chỉ cụ thể dùng được (trong bài và schema): trụ sở 728/1 Lê Trọng Tấn,
  Sơn Kỳ, Bình Tân, cùng các địa chỉ ở trang Liên hệ:
  1686 Tỉnh Lộ 10, P. Bình Tân; Lầu 4, 249 Cộng Hòa, P.13, Tân Bình;
  64 Vườn Chuối, Quận 3; 216 Lý Chính Thắng, P.9, Quận 3;
  44 Đinh Công Tráng, Tân Định, Quận 1; 412 Nguyễn Thị Minh Khai, P.5, Quận 3;
  202 Lê Lai, P. Phạm Ngũ Lão, Quận 1; 11A Hồng Hà, P.2, Tân Bình.
  Không tự đặt ra địa chỉ cho khu vực chưa có trong danh sách này.

## 4. Dịch vụ

### Sửa chữa tại nhà
- Sửa cửa sắt: cửa xệ cạ nền, kẹt, bản lề rơ/gãy/rớt, khóa hỏng/kẹt chìa/mất chìa,
  khung mục rỉ cần hàn gia cố, rỉ sét bong sơn, cót két, đóng dội ngược;
  thay chốt, tay nắm, thanh chặn, bánh xe
- Sửa cửa kéo / cửa xếp: kẹt hoặc trật ray, bánh xe mòn, lá cong/gãy,
  khóa sập/khóa chùm hỏng, nhíp/lò xo trợ lực yếu, dàn cửa xệ
- Cửa cuốn: kẹt, lệch nan, trật ray, khóa cơ, va cạ. Lỗi mô-tơ / bộ điều khiển
  báo phương án riêng trước khi làm
- Thợ hàn sắt tại nhà; sửa cổng sắt, cổng sắt mỹ thuật

### Thi công mới
- Cửa sắt, cổng sắt, cửa kéo
- Mái hiên, mái che (có khung inox)
- Cầu thang, lan can sắt và inox
- Cửa, cổng inox
- Cửa nhôm kính (Xingfa), lan can nhôm, vách ngăn nhôm kính văn phòng
- Vách ngăn panel
- Nhà xưởng, văn phòng, công ty: thiết kế, thi công, sửa chữa

## 5. Giá và cam kết

- Không niêm yết một giá chung; giá theo hạng mục, mức hư hỏng, vật tư
- Báo giá nhanh: gửi 2–3 ảnh hoặc clip ngắn qua Zalo để được báo khoảng giá miễn phí
- Giá qua điện thoại chỉ để tham khảo; giá chốt sau khi đo đạc tại chỗ
- Khảo sát, đo đạc miễn phí trong nội thành, kể cả khi khách không làm
- Báo giá trước khi làm, thu tiền sau khi xong, không phát sinh mập mờ
- Bảo hành 2 năm công thợ và mối hàn, có phiếu ghi hạng mục và ngày làm;
  vật tư thay mới bảo hành theo nhà sản xuất
- Không đưa giá cụ thể (VND) hay bảng giá vào bài; hướng khách gửi ảnh/clip qua Zalo để báo giá

## 6. Kiến thức nghề đã có trên website (dùng được trong bài)

- Cửa kéo đẩy nặng thường do nhiều nguyên nhân cùng lúc: ray bẩn, bánh xe mòn,
  khớp lá khô dầu, lò xo trợ lực yếu, dàn cửa xệ
- Ca nhẹ (vệ sinh ray, thay bánh xe, chỉnh khe) khoảng 1 tiếng; ca nặng (nắn ray
  cong, thay lá, căn lại cả dàn) có thể mất cả buổi
- Ca cót két thường xử lý dưới 1 tiếng
- Sơn lại: làm buổi sáng, chiều khô mặt, hôm sau dùng bình thường
- Bảo dưỡng cửa kéo nhà mặt tiền / dùng nhiều: vệ sinh ray, tra mỡ 6 tháng–1 năm/lần
- Bánh xe phải đúng tải trọng; khớp lá tra mỡ chuyên dụng
- Vật liệu thường dùng: sắt hộp, sắt tấm, sắt đặc, hoa văn đúc, sắt mạ kẽm,
  sắt giả gỗ, inox; sơn dầu, sơn tĩnh điện, sơn chống rỉ

## 7. Chất liệu thật của xưởng

- Mục này chưa có nội dung. Không tự đặt ra ca sửa, câu hỏi của khách, sai lầm
  hay gặp, độ dày hoặc thương hiệu vật tư; chỉ dùng chất liệu thật người dùng
  nhập cho từng bài.


## 8. Quy tắc khi AI viết về doanh nghiệp

- Xưng "Pro-Metal" hoặc "chúng tôi"; giọng thợ có nghề, nói thẳng, có ví dụ
- Không bịa số năm kinh nghiệm, số công trình, giá, tên khách hàng, đánh giá;
  không nêu năm thành lập, tên người phụ trách hay tác giả, bảng giá, giá cụ thể
- Không hứa thời gian có mặt nhanh hơn "30–60 phút"
- Không so sánh rẻ, đắt hay trung bình giữa các vật liệu hoặc cách làm; không nêu
  bất kỳ con số giá nào
- Không nêu hay hứa báo giá xong trong bao lâu; chỉ viết "gửi ảnh/clip qua Zalo để
  được báo khoảng giá miễn phí"
- Chỉ nêu địa chỉ đã ghi ở mục 3; không đặt ra địa chỉ ở Bình Dương, Vũng Tàu hay
  khu vực nào khác. Thông tin nào không có trong hồ sơ này (email, mạng xã hội,
  số khách đã phục vụ…) thì không nêu và không đoán
- Lời kêu gọi liên hệ: gửi ảnh/clip qua Zalo 03.4444.07.17 để được báo khoảng giá miễn phí
```

### Bằng chứng (lượt 2)

```
$ uv run pytest -q
1889 passed, 9 xfailed in 108.86s (0:01:48)   # sau khi gộp test của Soi Lỗi (tests/test_business_profile.py)

$ uv run ruff check .
All checks passed!
```

### Lượt 2, phần bổ sung (theo góp ý Soi Lỗi và bộ lọc mới T-024)

- **Bỏ ngày quyết định khỏi phần AI thấy** (góp ý của Soi Lỗi): các cụm "(chủ dự án quyết định/xác nhận 2026-10-14)" ở mục 1 và mục 3 chuyển thành dòng ghi chú `>` đặt ngay sau ý. Ngày không giúp gì cho bài viết. Nội dung ý giữ nguyên.
- **Hướng dẫn đầu file khớp bộ lọc mới của T-024** (Thợ Máy, nhánh `team/T-024`): dòng ghi chú là dòng bắt đầu bằng `>` (bỏ câu "không có dấu cách phía trước", vì bộ lọc mới bỏ cả dòng `>` thụt lề). Nhãn `[CẦN XÁC NHẬN — lý do]` đặt ở dòng nào của một ý, kể cả dòng xuống hàng, thì AI bỏ cả ý; viết hoa hay thường đều được.
- **Đối chiếu hai bộ lọc:** chạy `confirmed_profile` của `main` hiện tại và của `origin/team/T-024` trên file mới: kết quả **giống hệt nhau**, không còn "2026" hay "XÁC NHẬN" trong phần AI thấy. Phần "AI sẽ thấy gì (lượt 2)" ở trên đã cập nhật theo file mới.

```
$ uv run pytest -q
1889 passed, 9 xfailed in 119.94s (0:01:59)

$ uv run ruff check .
All checks passed!
```

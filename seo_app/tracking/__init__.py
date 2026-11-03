"""Giai đoạn 6 (thiết kế ``docs/team/reports/T-120-tho-may.md``): theo dõi bài qua Google Search
Console.

Lõi tính toán (T-123) gồm hàm thuần, không gọi mạng, không đọc ghi file:

- ``model``: khuôn dòng số liệu đọc từ cache (``Protocol``) và các kiểu kết quả;
- ``periods``: ngày theo giờ Google (PT), kỳ 7/28/91 ngày hay tự chọn, kỳ so sánh, tuần;
- ``match``: khớp địa chỉ trang với bài, trang WordPress và dòng kế hoạch; «Trang khác»;
- ``stats``: cộng dồn, vị trí trung bình theo lượt hiển thị, so hai kỳ, số viết kiểu Việt Nam;
- ``flags``: nhãn đánh dấu bài, ngưỡng là hằng có tên;
- ``keywords``: từ khóa của một bài, gộp cách gõ có dấu, không dấu.

Client Search Console (T-121) nằm ở ``seo_app/google/``, cache số liệu (T-122) ở
``seo_app/storage/``; bước lấy số liệu (T-124) thêm ``refresh.py`` vào gói này.
"""

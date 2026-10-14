"""Đo tốc độ bằng TỈ LỆ thay vì mốc giây cố định (T-015).

Mốc "dưới 1 giây" dễ hỏng trên máy Windows chậm hoặc đang bận. Ở đây chạy cùng một hàm trên
đầu vào cỡ 1/4 và cỡ đầy đủ (gấp 4): hàm chạy tuyến tính thì thời gian tăng khoảng 4 lần, hàm
bình phương tăng khoảng 16 lần. Ngưỡng 9 lần bắt được hàm bình phương.

Đo cho ổn định (T-015 lần 2, Soi Lỗi R6-3):
- Dùng THỜI GIAN CPU của tiến trình (``time.process_time``), không dùng đồng hồ thường: máy
  bận (chương trình khác chiếm CPU) không làm tăng thời gian CPU của test.
- Trên Windows thời gian CPU chỉ chính xác tới khoảng 15,6 ms, nên mỗi lần đo chạy lặp hàm
  tới khi đủ ``MIN_MEASURE`` giây rồi chia cho số lần chạy.

Thêm một mốc tuyệt đối rộng cho cỡ đầy đủ (``MAX_SECONDS``, Lá Chắn T-015 #2): bắt hàm tuyến
tính nhưng chậm bất thường (làm treo app), mà máy chậm vẫn không đỏ oan.
"""

from __future__ import annotations

import gc
import time
from collections.abc import Callable

FACTOR = 4  # đầu vào lớn dài gấp mấy lần đầu vào nhỏ
MAX_RATIO = 9.0  # thời gian lớn / thời gian nhỏ tối đa
MAX_SECONDS = 5.0  # thời gian CPU tối đa cho một lần chạy cỡ đầy đủ (hiện khoảng 0,2 giây)
MIN_MEASURE = 0.1  # mỗi lần đo kéo dài ít nhất chừng này giây CPU (vượt độ phân giải Windows)


def _time_per_call(fn: Callable[[str], object], text: str) -> float:
    """Thời gian CPU trung bình mỗi lần gọi ``fn(text)``, đo trong ít nhất ``MIN_MEASURE`` giây."""
    calls = 0
    start = time.process_time()
    while True:
        fn(text)
        calls += 1
        elapsed = time.process_time() - start
        if elapsed >= MIN_MEASURE or elapsed > MAX_SECONDS:
            return elapsed / calls


def assert_scales_linearly(
    fn: Callable[[str], object], make: Callable[[int], str], *, label: object = ""
) -> None:
    """``make(k)`` tạo đầu vào cỡ ``k``/4 so với cỡ đầy đủ; ``make(4)`` là cỡ đầy đủ.

    Cỡ nhỏ lấy kết quả nhanh nhất của 2 lần đo; cỡ lớn đo tối đa 3 lần, dừng sớm khi đã đạt.
    """
    small, large = make(1), make(FACTOR)
    assert len(large) > len(small), "đầu vào lớn phải dài hơn đầu vào nhỏ"
    enabled = gc.isenabled()
    gc.disable()
    try:
        fn(small)  # chạy nháp: nạp và biên dịch biểu thức chính quy
        t_small = max(min(_time_per_call(fn, small) for _ in range(2)), 1e-9)
        t_large = float("inf")
        for _ in range(3):
            t_large = min(t_large, _time_per_call(fn, large))
            if t_large <= MAX_RATIO * t_small:
                break
    finally:
        if enabled:
            gc.enable()
    ratio = t_large / t_small
    assert ratio <= MAX_RATIO, (label, f"gấp {FACTOR} độ dài thì chậm gấp {ratio:.1f} lần")
    assert t_large <= MAX_SECONDS, (label, f"cỡ đầy đủ mất {t_large:.1f} giây CPU")

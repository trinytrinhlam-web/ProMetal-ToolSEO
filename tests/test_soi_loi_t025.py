"""Soi Lỗi T-025: helper đo tốc độ không đỏ oan khi máy bận, vẫn bắt hàm bình phương.

Báo cáo: docs/team/reports/T-025-soi-loi.md. Dùng đồng hồ giả nên kết quả cố định, không phụ
thuộc máy. Không gọi mạng, không cần .env.
"""

from __future__ import annotations

import pytest
import timing
from timing import assert_scales_linearly


class _BurstClock:
    """Đồng hồ CPU giả có một "đợt bận": việc bắt đầu trong ``[start, end)`` giây CPU tốn gấp
    ``factor`` lần (máy khác tranh bộ nhớ đệm, CPU hạ xung nhịp). Số đo thật ở T-025: đợt bận
    kéo dài cỡ 0,1–0,3 giây và làm thời gian đội lên tới khoảng 2 lần.
    """

    def __init__(self, start: float, end: float, factor: float) -> None:
        self.cpu = 0.0
        self.start, self.end, self.factor = start, end, factor

    def run(self, work: float) -> None:
        busy = self.start <= self.cpu < self.end
        self.cpu += work * (self.factor if busy else 1.0)

    def process_time(self) -> float:
        return self.cpu


def _install(monkeypatch, clock: _BurstClock) -> None:
    monkeypatch.setattr(timing, "time", clock)


def _power(clock: _BurstClock, base: float, exponent: float):
    """Hàm giả: cỡ nhỏ (20 000 ký tự) tốn ``base`` giây, cỡ gấp k tốn ``base * k**exponent``."""
    return lambda text: clock.run(base * (len(text) / 20_000) ** exponent)


def _make(k: int) -> str:
    return "a" * (20_000 * k)


# Đợt bận phủ trọn phần đầu: lần chạy nháp và cả 2 lần đo cỡ nhỏ theo thứ tự cũ (nhỏ, nhỏ, lớn).
# Thứ tự cũ đo ra tỉ lệ 400 / 50 = 8 < 9 nên hàm bình phương lọt: đúng lỗi chập chờn của T-025.
@pytest.mark.parametrize("end", [0.1, 0.2, 0.3])
def test_burst_over_small_measurements_does_not_hide_quadratic(monkeypatch, end):
    clock = _BurstClock(0.0, end, 2.0)
    _install(monkeypatch, clock)
    with pytest.raises(AssertionError, match="chậm gấp"):
        assert_scales_linearly(_power(clock, 0.025, 2), _make)


@pytest.mark.parametrize("start", [0.0, 0.05, 0.15, 0.3, 0.6, 1.0])
def test_burst_anywhere_does_not_hide_quadratic(monkeypatch, start):
    clock = _BurstClock(start, start + 0.3, 2.0)
    _install(monkeypatch, clock)
    with pytest.raises(AssertionError, match="chậm gấp"):
        assert_scales_linearly(_power(clock, 0.025, 2), _make)


# Đợt bận rơi vào lần đo cỡ lớn: hàm tuyến tính vẫn được nhận nhờ đo thêm vòng sau.
@pytest.mark.parametrize("start", [0.0, 0.1, 0.15, 0.25, 0.5])
def test_burst_does_not_fail_linear_function(monkeypatch, start):
    clock = _BurstClock(start, start + 0.3, 2.5)
    _install(monkeypatch, clock)
    assert_scales_linearly(_power(clock, 0.025, 1), _make)


def test_ratio_between_clear_and_max_still_passes(monkeypatch):
    # 4**1.4 ≈ 7: trên CLEAR_RATIO nên phải đo thêm vòng, nhưng vẫn dưới MAX_RATIO.
    clock = _BurstClock(0.0, 0.0, 1.0)
    _install(monkeypatch, clock)
    assert_scales_linearly(_power(clock, 0.025, 1.4), _make)


def test_ratio_just_above_max_is_caught(monkeypatch):
    # 4**1.6 ≈ 9,2: hơi quá ngưỡng, máy rảnh, vẫn phải bị bắt (không nới MAX_RATIO).
    clock = _BurstClock(0.0, 0.0, 1.0)
    _install(monkeypatch, clock)
    with pytest.raises(AssertionError, match="chậm gấp 9.2"):
        assert_scales_linearly(_power(clock, 0.025, 1.6), _make)


def test_limits_are_not_loosened():
    assert timing.MAX_RATIO == 9.0
    assert timing.CLEAR_RATIO < timing.MAX_RATIO
    assert timing.MIN_MEASURE >= 0.1  # đồng hồ CPU trên Windows chỉ chính xác ~15,6 ms

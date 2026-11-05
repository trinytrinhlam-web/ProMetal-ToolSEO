"""T-123 (Thợ Máy): kiểu dữ liệu của gói theo dõi bài (``seo_app.tracking.model``) và dữ liệu giả
dùng chung cho các file ``test_tracking_*``.

``Day``, ``Query`` là dataclass ``frozen`` giống hệt khuôn ``CachedDay``, ``CachedQuery`` của cache
T-122 (thiết kế T-120 mục 3.1): gói tính toán chỉ dựa vào tên trường (``Protocol``), nên chạy được
với dataclass của T-122 mà không phải chờ phiếu đó. Không gọi mạng, không đọc ghi file.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from seo_app.plan.model import PlanRow
from seo_app.tracking import match, stats
from seo_app.tracking.model import Comparison, PageKey, PageStats
from seo_app.tracking.periods import Period
from seo_app.wordpress.client import PublishedItem

SITE = "https://suachuacuasat.com"  # WORDPRESS_URL như config.py đọc (đã bỏ «/» cuối)
E = date(2026, 10, 31)  # ngày chốt cuối của cache trong các ví dụ


@dataclass(frozen=True)
class Day:
    """Một ngày × một trang, đúng tên trường ``CachedDay`` (T-122)."""

    day: date
    page: str
    clicks: int
    impressions: int
    position_sum: float
    final: bool = True


@dataclass(frozen=True)
class Query:
    """Một trang × một từ khóa trong một khoảng, đúng tên trường ``CachedQuery`` (T-122)."""

    start: date
    end: date
    page: str
    query: str
    clicks: int
    impressions: int
    position_sum: float


def day_row(
    day: date,
    path: str,
    clicks: int,
    impressions: int,
    position: float = 1.0,
    *,
    final: bool = True,
) -> Day:
    """Dòng ngày cho trang ``SITE + path``; ``position`` là vị trí trung bình của dòng."""
    return Day(day, SITE + path, clicks, impressions, position * impressions, final)


def query_row(
    period: Period,
    path: str,
    query: str,
    clicks: int,
    impressions: int,
    position: float = 1.0,
) -> Query:
    return Query(
        period.start, period.end, SITE + path, query, clicks, impressions, position * impressions
    )


def item(
    post_id: int, path: str, *, kind: str = "post", title: str = "", slug: str = ""
) -> PublishedItem:
    """Bài (``kind="post"``) hay trang đã đăng; ``slug`` mặc định lấy từ đường dẫn."""
    return PublishedItem(
        id=post_id,
        type=kind,
        slug=slug or path.strip("/").rsplit("/", 1)[-1],
        link=SITE + path,
        title=title or f"Bài {post_id}",
    )


def plan_row(keyword: str = "sửa cửa sắt", **fields: object) -> PlanRow:
    return PlanRow(keyword=keyword, **fields)


# ------------------------------------------------------------------------------- kiểu dữ liệu


def test_page_stats_ctr_position_weighted_and_empty():
    stats_ = PageStats(clicks=3, impressions=40, position_sum=200.0)
    assert stats_.ctr == 3 / 40
    assert stats_.position == 5.0
    empty = PageStats()
    assert empty.ctr is None and empty.position is None  # không chia cho 0, không NaN
    total = stats_ + PageStats(1, 10, 20.0)
    assert (total.clicks, total.impressions, total.position_sum) == (4, 50, 220.0)


def test_comparison_deltas_and_signs():
    now, before = PageStats(52, 1000, 4200.0), PageStats(40, 800, 5040.0)
    cmp = Comparison(now, before)
    assert cmp.clicks_delta == 12 and cmp.impressions_delta == 200
    assert cmp.rank_gain is not None and round(cmp.rank_gain, 6) == 2.1  # 6,3 → 4,2: lên 2,1 bậc
    assert cmp.ctr_delta is not None and round(cmp.ctr_delta, 6) == 0.002
    low = Comparison(now, before, low_data=True)
    assert low.rank_gain is None and low.ctr_delta is None  # ít dữ liệu: không so CTR, vị trí
    alone = Comparison(now, None)
    assert alone.clicks_delta is None and alone.rank_gain is None


def test_page_key_text():
    assert str(PageKey("/")) == "/"
    assert str(PageKey("/", "s=cửa")) == "/?s=cửa"
    assert str(PageKey("/a", "")) == "/a?"


def test_frozen_dataclasses_like_t122_fit_the_protocols():
    """Dataclass ``frozen`` cùng tên trường như T-122 dùng thẳng được ở mọi hàm (``Protocol``)."""
    period = Period(date(2026, 10, 1), E)
    rows = [day_row(date(2026, 10, 5), "/sua-cua-sat/", 2, 10, 3.0)]
    tracking = match.build_tracking(SITE, [item(10, "/sua-cua-sat/")], rows)
    assert stats.aggregate(tracking.pages[0].days, period) == PageStats(2, 10, 30.0)
    assert stats.aggregate(rows, period) == PageStats(2, 10, 30.0)


# ------------------------------------------------------------------------- hàm thuần (phiếu)

_PACKAGE = Path(__file__).resolve().parents[1] / "seo_app" / "tracking"
# Gói tính toán không gọi mạng, không đọc ghi file, không phụ thuộc T-121 (google), T-122 (storage).
_FORBIDDEN_IMPORTS = (
    "socket",
    "requests",
    "urllib.request",
    "http",
    "sqlite3",
    "pathlib",
    "os",
    "io",
    "shutil",
    "subprocess",
    "tempfile",
    "pickle",
    "streamlit",
    "seo_app.google",
    "seo_app.storage",
    "seo_app.ai",
    "seo_app.config",
)
_FORBIDDEN_CALLS = {"open", "eval", "exec", "compile", "__import__"}


def _imports(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
            names.update(f"{node.module}.{alias.name}" for alias in node.names)
    return names


_CORE = ("__init__.py", "model.py", "periods.py", "match.py", "stats.py", "flags.py", "keywords.py")
# T-124 (R5): ``refresh.py`` là lớp nối của gói (thiết kế T-120 mục 6: client T-121, cache T-122,
# ``.env``), không phải hàm thuần. Phép kiểm riêng của nó ở ``tests/test_tracking_refresh.py``
# (không nhập Streamlit, AI, Google Sheets; nạp module không gọi gì ngoài hằng). File mới trong gói
# phải được xếp vào lõi hay lớp nối ở đây, không lọt qua phép kiểm.
_IO_MODULES = ("refresh.py",)


def test_package_is_pure_functions():
    files = sorted(_PACKAGE.glob("*.py"))
    assert set(_CORE) <= {path.name for path in files} <= set(_CORE) | set(_IO_MODULES)
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        forbidden = (
            () if path.name in _IO_MODULES else (*_FORBIDDEN_IMPORTS, "seo_app.tracking.refresh")
        )
        for name in _imports(tree):
            assert not any(name == bad or name.startswith(bad + ".") for bad in forbidden), (
                path.name,
                name,
            )
        calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        assert not calls & _FORBIDDEN_CALLS, (path.name, calls & _FORBIDDEN_CALLS)

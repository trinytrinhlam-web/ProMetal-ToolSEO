"""Bộ dựng bài cuối gửi WordPress (T-096; thiết kế ``docs/team/reports/T-094-tho-may.md`` mục
3.2, 3.5, 4, 6; điều kiện Lá Chắn LC-T094-4 → -10).

``build_article`` nhận bài như trong nháp (chữ thô: còn ký tự ngắt rộng 0 của T-031, escape link
Markdown của ``clean_ai_text``) và trả ``BuiltArticle``: **đúng** các chuỗi sẽ gửi, dữ liệu cho
màn hình xác nhận (``ArticleReview``) và mã băm xác nhận. Mọi hình thức gửi (Nháp, Hẹn giờ, Đăng
ngay) phải gửi đúng gói này (LC-T094-36); không chỗ nào khác ghép HTML bài.

Thứ tự (LC-T094-5, LC-T039 đk 3a), trên cùng một chuỗi:

1. Mỗi phần: ``<h2>`` tiêu đề phần (từ phần thứ hai, như ``article_parts`` cũ) + thân Markdown.
   ``unbreak_autolinks`` chạy ở đây, trên chữ thô, **trước** khi escape (LC-T094-9); chữ đã gỡ
   vẫn coi là chưa an toàn: bộ chuyển (``markdown_to_html``) escape mọi thứ, không tạo link.
2. ``sanitize_html`` → ``place_links`` (link nội bộ, địa chỉ chỉ từ danh sách bài đã đăng) →
   ``sanitize_html`` → ``check_links(…, required_ids)``. Không bước nào sửa HTML sau
   ``check_links``. ``index`` phải vừa tải lại từ site ngay trước khi gọi (việc của giao diện).
3. Cắt HTML cuối thành từng phần ở các ``<h2>`` (chỉ tiêu đề phần là ``<h2>``: bộ chuyển hạ mọi
   tiêu đề trong thân xuống ``<h3>``); ``"\\n".join(sections)`` đúng bằng HTML đã kiểm. Ảnh do
   client chèn sau phần của nó (``content_parts``), bằng ``figure_html``.
4. Mã băm SHA-256 trên bản chuẩn hóa xác định (JSON khóa sắp xếp, UTF-8, ``(",", ":")``) của mọi
   thứ sẽ gửi (LC-T094-8). Giao diện tính lúc hiện màn hình xác nhận và so lại ngay trước lệnh
   mạng đầu tiên (LC-T094-38).

Chữ trong ``ArticleReview`` là chữ thô: giao diện phải escape khi hiện (``needs_escape``).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import TypeVar

from seo_app.images.html import plain_image_text
from seo_app.onpage.links import (
    InternalLink,
    LinkKind,
    LinkReport,
    Notice,
    check_links,
    place_links,
)
from seo_app.onpage.meta import Level, worst
from seo_app.publish.markdown import _DROPPED, escape_text, markdown_to_html
from seo_app.publish.review import (
    BareAddress,
    LinkRow,
    bare_addresses,
    block_texts,
    embedded_urls,
    link_rows,
)
from seo_app.sanitize import sanitize_html, strip_tags, unbreak_autolinks, unescape_link_syntax
from seo_app.storage.site_index import SiteIndex
from seo_app.wordpress.shortcodes import find_shortcodes

T = TypeVar("T")

DIGEST_VERSION = "t096-1"  # đổi khi đổi cách chuẩn hóa: mã băm cũ không còn khớp
MODES = ("draft", "future", "publish")
MAX_PARTS = 100
MAX_SLUG_CHARS = 200
_DATE_GMT = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_H2 = re.compile("<h2>")

_MSG_BAD_INPUT = "Dữ liệu bài gửi vào bộ dựng sai dạng ({what}). Chưa gửi gì lên website."
_MSG_SPLIT = "Không dựng được bài theo từng phần. Chưa gửi gì lên website."


class BuildError(ValueError):
    """Đầu vào bộ dựng sai dạng (lỗi lập trình, không phải lỗi nội dung). Câu cố định."""


@dataclass(frozen=True)
class ArticlePart:
    """Một phần của bài như trong nháp. ``heading`` chỉ dùng từ phần thứ hai (phần đầu là mở
    bài, không có ``<h2>``); ``body``: Markdown."""

    heading: str
    body: str


@dataclass(frozen=True)
class ArticleImage:
    """Ảnh sẽ chèn sau thân phần ``section``. ``sha256``: băm byte sẽ tải (như ``altsha-``);
    ``alt``, ``caption``: chữ đã duyệt (bộ dựng tự đổi về chữ thường như ``figure_html``)."""

    section: int
    sha256: str
    alt: str
    caption: str = ""
    featured: bool = False
    has_gps: bool = False


@dataclass(frozen=True)
class SeoFields:
    """Chữ SEO sẽ ghi lên SiteSEO (``write``: công tắc «Ghi SEO lên website»)."""

    title: str = ""
    description: str = ""
    focus_keyword: str = ""
    write: bool = False


@dataclass(frozen=True)
class ImageRow:
    section: int
    section_name: str
    alt: str
    caption: str
    featured: bool
    has_gps: bool


@dataclass(frozen=True)
class ArticleReview:
    """Dữ liệu màn hình xác nhận (thiết kế T-094 mục 3.5; LC-T094-7). Mọi chữ là chữ thô."""

    links: tuple[LinkRow, ...]
    bare: tuple[BareAddress, ...]
    embeds: tuple[str, ...]
    shortcodes: tuple[tuple[str, str], ...]  # (chỗ, đoạn)
    images: tuple[ImageRow, ...]
    skipped_links: tuple[str, ...]
    problems: tuple[Notice, ...]
    needs_escape: bool = field(default=True, init=False)  # chữ thô: escape khi hiện (U1)

    @property
    def level(self) -> Level:
        return worst(p.level for p in self.problems)

    @property
    def blocked(self) -> bool:
        return self.level is Level.BLOCK


@dataclass(frozen=True)
class BuiltArticle:
    """Gói sẽ gửi. ``sections``: HTML cuối từng phần (đã lọc, đã chèn link, đã kiểm);
    ``title``, ``excerpt``, ``slug``: đúng chữ đưa vào ``create_draft``."""

    title: str
    sections: tuple[str, ...]
    excerpt: str
    slug: str
    categories: tuple[int, ...]
    tags: tuple[int, ...]
    images: tuple[ArticleImage, ...]
    seo: SeoFields
    mode: str
    date_gmt: str
    review: ArticleReview
    digest: str

    @property
    def html(self) -> str:
        """HTML cuối đã kiểm (chưa có ảnh): ``"\\n".join(sections)``."""
        return "\n".join(self.sections)

    def matches(self, digest: object) -> bool:
        """Mã băm người dùng đã xác nhận có đúng gói này không."""
        return isinstance(digest, str) and hmac.compare_digest(digest, self.digest)

    def content_parts(self, images: Mapping[int, T]) -> list[str | T]:
        """Nội dung theo thứ tự cho ``create_draft_with_images``: HTML phần 0, ảnh phần 0, HTML
        phần 1… ``images``: đối tượng ảnh của client theo số phần, **đúng** các phần đã khai
        trong ``build_article`` (ảnh đã băm, đã liệt kê ở màn hình xác nhận)."""
        if set(images) != {image.section for image in self.images}:
            raise BuildError(_MSG_BAD_INPUT.format(what="ảnh không khớp bài đã dựng"))
        parts: list[str | T] = []
        for number, section in enumerate(self.sections):
            parts.append(section)
            if number in images:
                parts.append(images[number])
        return parts


def plain_line(text: object) -> str:
    """Chữ một dòng (tiêu đề bài, tiêu đề phần, đoạn trích): gỡ ký tự ngắt rộng 0 và escape link
    Markdown (``unescape_link_syntax`` gỡ cả hai), bỏ ký tự điều khiển, gộp khoảng trắng.
    **Chưa** escape HTML."""
    if not isinstance(text, str):
        return ""
    return " ".join(_DROPPED.sub("", unescape_link_syntax(text)).split())


def _section_html(number: int, part: ArticlePart) -> str:
    pieces = []
    if number > 0:
        pieces.append(f"<h2>{escape_text(plain_line(part.heading))}</h2>")
    body = markdown_to_html(unbreak_autolinks(part.body))
    if body:
        pieces.append(body)
    return "\n".join(pieces)


def _split(final: str, count: int) -> tuple[str, ...]:
    """Cắt HTML cuối thành ``count`` phần ở các ``<h2>``; ``"\\n".join`` ra đúng ``final``."""
    starts = [match.start() for match in _H2.finditer(final)]
    if len(starts) != count - 1:
        raise BuildError(_MSG_SPLIT)
    bounds = [0, *starts, len(final)]
    pieces = []
    for start, end in zip(bounds, bounds[1:], strict=False):
        piece = final[start:end]
        if end != len(final):
            if not piece.endswith("\n"):
                raise BuildError(_MSG_SPLIT)
            piece = piece[:-1]
        pieces.append(piece)
    if "\n".join(pieces) != final:
        raise BuildError(_MSG_SPLIT)
    return tuple(pieces)


def _ids(values: object, what: str) -> tuple[int, ...]:
    if isinstance(values, str | bytes) or not isinstance(values, Iterable):
        raise BuildError(_MSG_BAD_INPUT.format(what=what))
    out = tuple(values)
    if not all(type(v) is int and 0 < v < 2**63 for v in out):
        raise BuildError(_MSG_BAD_INPUT.format(what=what))
    return out


def _check_inputs(
    parts: object, images: object, seo: object, mode: object, date_gmt: object
) -> tuple[tuple[ArticlePart, ...], tuple[ArticleImage, ...]]:
    if isinstance(parts, str | bytes) or not isinstance(parts, Sequence):
        raise BuildError(_MSG_BAD_INPUT.format(what="các phần"))
    items = tuple(parts)
    if len(items) > MAX_PARTS or not all(
        isinstance(p, ArticlePart) and isinstance(p.heading, str) and isinstance(p.body, str)
        for p in items
    ):
        raise BuildError(_MSG_BAD_INPUT.format(what="các phần"))
    if isinstance(images, str | bytes) or not isinstance(images, Sequence):
        raise BuildError(_MSG_BAD_INPUT.format(what="ảnh"))
    pictures = tuple(images)
    sections: set[int] = set()
    for image in pictures:
        if (
            not isinstance(image, ArticleImage)
            or type(image.section) is not int
            or not 0 <= image.section < len(items)
            or image.section in sections
            or not isinstance(image.sha256, str)
            or not _SHA256.fullmatch(image.sha256)
            or not isinstance(image.alt, str)
            or not isinstance(image.caption, str)
            or type(image.featured) is not bool
            or type(image.has_gps) is not bool
        ):
            raise BuildError(_MSG_BAD_INPUT.format(what="ảnh"))
        sections.add(image.section)
    if sum(image.featured for image in pictures) > 1:
        raise BuildError(_MSG_BAD_INPUT.format(what="nhiều ảnh đại diện"))
    if (
        not isinstance(seo, SeoFields)
        or not all(isinstance(v, str) for v in (seo.title, seo.description, seo.focus_keyword))
        or type(seo.write) is not bool
    ):
        raise BuildError(_MSG_BAD_INPUT.format(what="SEO"))
    if mode not in MODES:
        raise BuildError(_MSG_BAD_INPUT.format(what="hình thức gửi"))
    if not isinstance(date_gmt, str) or (
        _DATE_GMT.fullmatch(date_gmt) is None if mode == "future" else date_gmt != ""
    ):
        raise BuildError(_MSG_BAD_INPUT.format(what="giờ hẹn"))
    return items, pictures


def digest_of(payload: Mapping[str, object]) -> str:
    """SHA-256 (hex) của bản chuẩn hóa xác định: JSON khóa sắp xếp, ``(",", ":")``, UTF-8 (nửa
    cặp UTF-16 lẻ giữ nguyên dạng ``surrogatepass`` để không lỗi)."""
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8", "surrogatepass")).hexdigest()


def build_article(
    *,
    title: str,
    parts: Sequence[ArticlePart],
    index: SiteIndex,
    links: Iterable[InternalLink] = (),
    required_ids: Iterable[int] = (),
    images: Sequence[ArticleImage] = (),
    excerpt: str = "",
    slug: str = "",
    categories: Iterable[int] = (),
    tags: Iterable[int] = (),
    seo: SeoFields | None = None,
    mode: str = "draft",
    date_gmt: str = "",
) -> BuiltArticle:
    """Dựng gói sẽ gửi WordPress và dữ liệu xác nhận. Không gọi mạng.

    ``mode``: "draft", "future" (``date_gmt`` dạng ``YYYY-MM-DDTHH:MM:SS``, đúng chuỗi sẽ gửi),
    "publish" (``date_gmt`` rỗng). Đầu vào sai dạng: ``BuildError``. Vấn đề nội dung (link hỏng,
    chỗ bị nhúng, thiếu tiêu đề…) nằm trong ``review.problems``; ``review.blocked`` thì giao diện
    khóa nút gửi.
    """
    seo = SeoFields() if seo is None else seo
    items, pictures = _check_inputs(parts, images, seo, mode, date_gmt)
    if not isinstance(title, str) or not isinstance(excerpt, str) or not isinstance(slug, str):
        raise BuildError(_MSG_BAD_INPUT.format(what="tiêu đề, đoạn trích, slug"))
    if not isinstance(index, SiteIndex):
        raise BuildError(_MSG_BAD_INPUT.format(what="danh sách bài"))
    cats, tag_ids = _ids(categories, "chuyên mục"), _ids(tags, "thẻ")
    required = _ids(required_ids, "link bắt buộc")

    raw = "\n".join(_section_html(number, part) for number, part in enumerate(items))
    placed = place_links(sanitize_html(raw), links, index)
    final = sanitize_html(placed.html)
    report = check_links(final, index, required)
    sections = _split(final, len(items)) if items else ()

    final_title = strip_tags(plain_line(title)).strip()  # như ``create_draft``
    final_excerpt = escape_text(plain_line(excerpt))
    final_images = tuple(
        ArticleImage(
            section=image.section,
            sha256=image.sha256,
            alt=plain_image_text(image.alt),
            caption=plain_image_text(image.caption),
            featured=image.featured,
            has_gps=image.has_gps,
        )
        for image in sorted(pictures, key=lambda image: image.section)
    )
    names = [plain_line(part.heading) for part in items]
    review = _review(
        final=final,
        sections=sections,
        names=names,
        report=report,
        skipped=placed.skipped,
        title=final_title,
        images=final_images,
        index=index,
        slug=slug,
        seo=seo,
        mode=mode,
        bodies=[part.body for part in items],
    )
    payload = {
        "v": DIGEST_VERSION,
        "mode": mode,
        "date_gmt": date_gmt,
        "title": final_title,
        "excerpt": final_excerpt,
        "slug": slug,
        "categories": list(cats),
        "tags": list(tag_ids),
        "sections": list(sections),
        "images": [
            {
                "section": image.section,
                "sha256": image.sha256,
                "alt": image.alt,
                "caption": image.caption,
                "featured": image.featured,
                "has_gps": image.has_gps,
            }
            for image in final_images
        ],
        "seo": {
            "title": seo.title,
            "description": seo.description,
            "focus_keyword": seo.focus_keyword,
            "write": seo.write,
        },
    }
    return BuiltArticle(
        title=final_title,
        sections=sections,
        excerpt=final_excerpt,
        slug=slug,
        categories=cats,
        tags=tag_ids,
        images=final_images,
        seo=seo,
        mode=mode,
        date_gmt=date_gmt,
        review=review,
        digest=digest_of(payload),
    )


def _section_label(number: int, name: str) -> str:
    if number == 0:
        return f"Mở bài «{name}»" if name else "Mở bài"
    return f"Mục «{name}»" if name else f"Mục {number + 1}"


def _review(
    *,
    final: str,
    sections: tuple[str, ...],
    names: list[str],
    report: LinkReport,
    skipped: tuple[str, ...],
    title: str,
    images: tuple[ArticleImage, ...],
    index: SiteIndex,
    slug: str,
    seo: SeoFields,
    mode: str,
    bodies: list[str],
) -> ArticleReview:
    problems: list[Notice] = []
    block, warn = Level.BLOCK, Level.WARN

    if not title:
        problems.append(Notice(block, "Bài chưa có tiêu đề."))
    if not any(text.strip() for text in block_texts(final)) or not any(b.strip() for b in bodies):
        problems.append(Notice(block, "Bài chưa có nội dung."))
    for number, name in enumerate(names):
        if number > 0 and not name:
            problems.append(Notice(block, f"Mục thứ {number + 1} chưa có tiêu đề."))
    if slug and (len(slug) > MAX_SLUG_CHARS or not _SLUG.fullmatch(slug)):
        problems.append(
            Notice(block, "Slug chỉ được có chữ thường không dấu, số và dấu «-» (ví dụ sua-cua).")
        )

    rows = link_rows(final, report, index.site)
    for row in rows:
        if row.level is Level.BLOCK:
            problems.append(Notice(block, f"Link «{row.href}»: {row.message}"))
    problems.extend(report.missing)
    external = sum(1 for row in rows if row.kind is LinkKind.EXTERNAL)
    if external:
        problems.append(
            Notice(warn, f"Có {external} link ra ngoài website: xem lại từng link trong bảng.")
        )
    flagged = sum(1 for row in rows if row.flags and row.level is not Level.BLOCK)
    if flagged:
        problems.append(Notice(warn, f"Có {flagged} link có dấu hiệu lạ: xem cột cờ trong bảng."))
    problems.extend(Notice(warn, f"Link nội bộ không chèn được: {s}") for s in skipped)

    embeds = embedded_urls(final)
    if embeds:
        problems.append(
            Notice(
                block,
                f"Có {len(embeds)} đoạn chỉ có một địa chỉ web: WordPress sẽ nhúng cả trang đó "
                "vào bài. Viết thêm chữ quanh địa chỉ hoặc bỏ địa chỉ.",
            )
        )
    bare = bare_addresses(final, index.site)
    if bare:
        problems.append(
            Notice(
                warn,
                f"Có {len(bare)} địa chỉ web, email hiện dạng chữ trong bài (không bấm được): "
                "xem danh sách.",
            )
        )

    shortcodes = _shortcodes(title, sections, names, images)
    if shortcodes:
        problems.append(
            Notice(
                warn,
                f"Có {len(shortcodes)} đoạn dạng shortcode («[» liền chữ, có «]» phía sau): "
                "WordPress sẽ chạy nếu bạn sửa và lưu bài trong trang quản trị; nên xóa.",
            )
        )

    image_rows = tuple(
        ImageRow(
            section=image.section,
            section_name=_section_label(image.section, names[image.section]),
            alt=image.alt,
            caption=image.caption,
            featured=image.featured,
            has_gps=image.has_gps,
        )
        for image in images
    )
    for row in image_rows:
        if not row.alt:
            problems.append(Notice(block, f"Ảnh ở {row.section_name} chưa có alt (mô tả ảnh)."))
    with_gps = sum(1 for row in image_rows if row.has_gps)
    if with_gps:
        problems.append(
            Notice(
                warn,
                f"{with_gps} ảnh còn vị trí GPS: ai xem ảnh trên website cũng đọc được vị trí.",
            )
        )

    if not seo.write and mode == "publish":
        problems.append(
            Notice(
                block,
                "Đăng ngay mà SEO chưa ghi lên website: bài lên công khai với tiêu đề SEO mặc "
                "định. Bật «Ghi SEO lên website» hoặc gửi dạng Nháp / Hẹn giờ.",
            )
        )
    elif not seo.write and mode == "future":
        problems.append(
            Notice(
                warn,
                "SEO chưa ghi lên website: chép tiêu đề, mô tả vào SiteSEO trước giờ đăng.",
            )
        )

    return ArticleReview(
        links=rows,
        bare=bare,
        embeds=embeds,
        shortcodes=shortcodes,
        images=image_rows,
        skipped_links=skipped,
        problems=tuple(problems),
    )


def _shortcodes(
    title: str, sections: tuple[str, ...], names: list[str], images: tuple[ArticleImage, ...]
) -> tuple[tuple[str, str], ...]:
    """(chỗ, đoạn) dạng shortcode trong mọi chữ sẽ gửi, như ``shortcode_findings`` của trang Soạn
    bài: tiêu đề bài, từng phần (chữ đã giải mã của HTML cuối), alt và chú thích ảnh; thêm các
    đoạn chỉ thấy khi ghép mọi chữ theo đúng thứ tự gửi («[» ở mục này, «]» ở mục sau)."""
    found: list[tuple[str, str]] = [("Tiêu đề bài", s) for s in find_shortcodes(title)]
    by_section = {image.section: image for image in images}
    content: list[str] = []
    for number, section in enumerate(sections):
        label = _section_label(number, names[number])
        text = "\n".join(block_texts(section))
        found.extend((label, s) for s in find_shortcodes(text))
        content.append(text)
        image = by_section.get(number)
        if image is not None:
            found.extend((f"Alt ảnh ở {label}", s) for s in find_shortcodes(image.alt))
            found.extend((f"Chú thích ảnh ở {label}", s) for s in find_shortcodes(image.caption))
            content += [image.alt, image.caption]
    seen = {segment for _where, segment in found}
    for segment in find_shortcodes("\n".join(content)):
        if segment not in seen:
            found.append(("Nội dung, vắt qua nhiều mục", segment))
            seen.add(segment)
    return tuple(found)


__all__ = [
    "DIGEST_VERSION",
    "MODES",
    "ArticleImage",
    "ArticlePart",
    "ArticleReview",
    "BuildError",
    "BuiltArticle",
    "ImageRow",
    "SeoFields",
    "build_article",
    "digest_of",
    "plain_line",
]

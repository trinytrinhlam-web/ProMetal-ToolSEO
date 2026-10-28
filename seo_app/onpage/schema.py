"""Schema JSON-LD loại FAQPage: dựng từ cặp hỏi-đáp và kiểm hợp lệ, không cần mạng.

Thiết kế: ``docs/team/reports/T-033-tho-may.md`` mục 3.

- Site đã tự xuất Article, BreadcrumbList, LocalBusiness (và Organization của SiteSEO), nên
  phần mềm **từ chối dựng** các loại đó (``SITE_OWNED_TYPES``). ``HowTo`` luôn bị chặn.
- **AI không viết JSON.** Code dựng JSON-LD từ danh sách cặp (câu hỏi, trả lời) đã có trong bài.
- Câu hỏi và trả lời phải có **nguyên văn** trong bài (sau chuẩn hóa NFC và khoảng trắng):
  Google yêu cầu nội dung schema hiện trên trang. So trên chữ người đọc thấy (``plain_text``): bỏ
  dấu Markdown ở **cả** bài lẫn câu hỏi, trả lời; link chỉ giữ chữ, không giữ địa chỉ; không bao
  giờ đổi sang HTML. JSON-LD chỉ mang chữ đã bỏ dấu Markdown (SL-T038-2, Lá Chắn T-038).
- Chuỗi JSON xuất ra đổi ``<``, ``>``, ``&`` thành ``\\u003c``, ``\\u003e``, ``\\u0026`` nên không
  bao giờ đóng được thẻ ``</script>``.
- Giai đoạn 4 **chưa** đưa schema lên site (cách "d" mục 3.3); kết quả chỉ để xem trước và kiểm.
  Giao diện hiện ``json_ld`` bằng ``st.code(..., language="json")``, không ``unsafe_allow_html``.
- ``build_article_faq``: tìm mục Hỏi đáp trong bài (``find_faq``) rồi dựng như ``build_faq_page``.

Mọi hàm ở đây là hàm thuần: không đọc ``.env``, không gọi mạng. Địa chỉ site (``WORDPRESS_URL``)
truyền vào dạng tham số.
"""

from __future__ import annotations

import html
import json
import re
import unicodedata
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from seo_app.content.models import Section
from seo_app.content.rules import IGNORABLE_NOT_CF, MISSING_PATTERN
from seo_app.onpage.meta import odd_char_kinds
from seo_app.sanitize import strip_markdown_links, strip_tags, unescape_link_syntax
from seo_app.text import remove_accents

SCHEMA_CONTEXT = "https://schema.org"

# Loại phần mềm được dựng (cả loại lồng bên trong).
ALLOWED_TYPES = frozenset({"FAQPage", "Question", "Answer"})
# Loại site đã tự xuất (code riêng của site hoặc SiteSEO): phần mềm không dựng, tránh trùng nguồn.
SITE_OWNED_TYPES = frozenset(
    {
        "Article",
        "BlogPosting",
        "NewsArticle",
        "BreadcrumbList",
        "LocalBusiness",
        "HomeAndConstructionBusiness",
        "Organization",
    }
)
# Loại không bao giờ dùng (thiết kế mục 3.2).
FORBIDDEN_TYPES = frozenset({"HowTo"})

# Giới hạn độ dài (ký tự NFC, sau chuẩn hóa).
MAX_QUESTIONS = 20
MAX_QUESTION_LENGTH = 300
MAX_ANSWER_LENGTH = 2000
MAX_URL_LENGTH = 2000
# Bài dài hơn mức này không đem so (chặn dữ liệu bất thường làm chậm app).
MAX_ARTICLE_LENGTH = 500_000
MSG_ARTICLE_TOO_LONG = "Bài quá dài, không đối chiếu được hỏi đáp."


class Level(StrEnum):
    """Mức kết quả kiểm: Cảnh báo (vẫn dùng được) hoặc Chặn (không được dùng)."""

    WARN = "canh_bao"
    BLOCK = "chan"


@dataclass(frozen=True)
class Issue:
    """Một vấn đề tìm thấy. ``message`` là câu tiếng Việt, **không** chép lại dữ liệu đầu vào
    (an toàn khi hiện trên giao diện)."""

    level: Level
    message: str


# ------------------------------------------------------------------ khuôn pydantic


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True, strict=True)


class Answer(_Strict):
    type: Literal["Answer"] = Field(default="Answer", alias="@type")
    text: str


class Question(_Strict):
    type: Literal["Question"] = Field(default="Question", alias="@type")
    name: str
    accepted_answer: Answer = Field(alias="acceptedAnswer")


class FAQPage(_Strict):
    context: Literal["https://schema.org"] = Field(default=SCHEMA_CONTEXT, alias="@context")
    type: Literal["FAQPage"] = Field(default="FAQPage", alias="@type")
    url: str | None = None
    main_entity: list[Question] = Field(alias="mainEntity", min_length=1)

    def to_data(self) -> dict[str, Any]:
        """Dạng dict JSON-LD (khóa ``@context``, ``@type``, ``mainEntity``…)."""
        return self.model_dump(by_alias=True, exclude_none=True)


@dataclass(frozen=True)
class SchemaResult:
    """Kết quả dựng: ``page`` và ``json_ld`` là ``None`` khi có vấn đề mức Chặn."""

    page: FAQPage | None
    json_ld: str | None
    issues: tuple[Issue, ...]

    @property
    def blocked(self) -> bool:
        return any(issue.level is Level.BLOCK for issue in self.issues)


# ------------------------------------------------------------------ chuẩn hóa

_SPACES = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """NFC, bỏ ký tự vô hình (loại Cf và ``IGNORABLE_NOT_CF``), gộp mọi khoảng trắng (kể cả
    xuống dòng) thành một dấu cách, bỏ khoảng trắng đầu cuối. NFC chạy cả trước và sau để
    ghép lại chữ với dấu bị ký tự vô hình chen giữa."""
    text = unicodedata.normalize("NFC", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Cf")
    text = IGNORABLE_NOT_CF.sub("", text)
    text = _SPACES.sub(" ", text).strip()
    return unicodedata.normalize("NFC", text)


# ------------------------------------------------------------------ bỏ dấu Markdown

_HEADING_MARK = re.compile(r"^[ \t]{0,3}#{1,6}(?:[ \t]+|$)")
_HEADING_TAIL = re.compile(r"[ \t]+#+[ \t]*$")
_QUOTE_MARK = re.compile(r"^[ \t]*(?:>[ \t]?)+")
_LIST_MARK = re.compile(r"^[ \t]*(?:[-*+]|\d{1,9}[.)])[ \t]+")
_ESCAPABLE = frozenset("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")


def _strip_inline(block: str) -> str:
    """Bỏ dấu nhấn trong một đoạn: cặp ``**``, ``__``, ``*``, ``_``, ``~~`` (giữ chữ bên trong),
    mọi dấu huyền ngược (đoạn ``mã``); ``\\X`` (ký tự đã escape) thành ``X``.

    Gần như Markdown: dãy dấu mở được khi chữ ngay sau không phải khoảng trắng, đóng được khi
    chữ ngay trước không phải khoảng trắng (``_`` không mở/đóng giữa hai chữ cái, chữ số:
    «ten_file»); chỉ bỏ dãy đóng có dãy mở cùng loại đứng trước. Dãy lẻ («2*3m», «5 * 3») là chữ,
    giữ nguyên. Một lượt, tuyến tính (mỗi loại dấu một ngăn xếp)."""
    chars: list[str] = []
    marks: list[bool] = []  # ký tự có thể là dấu nhấn (*, _, ~ không escape)
    i, n = 0, len(block)
    while i < n:
        ch = block[i]
        if ch == "\\" and i + 1 < n and block[i + 1] in _ESCAPABLE:
            chars.append(block[i + 1])
            marks.append(False)
            i += 2
            continue
        if ch != "`":
            chars.append(ch)
            marks.append(ch in "*_~")
        i += 1
    drop = [False] * len(chars)
    openers: dict[str, list[tuple[int, int]]] = {"*": [], "_": [], "~": []}
    j = 0
    while j < len(chars):
        if not marks[j]:
            j += 1
            continue
        ch, end = chars[j], j
        while end < len(chars) and marks[end] and chars[end] == ch:
            end += 1
        before = chars[j - 1] if j else " "
        after = chars[end] if end < len(chars) else " "
        can_open = not after.isspace() and (ch != "_" or not before.isalnum())
        can_close = not before.isspace() and (ch != "_" or not after.isalnum())
        if ch == "~" and end - j < 2:
            can_open = can_close = False
        if can_close and openers[ch]:
            start, stop = openers[ch].pop()
            for k in (*range(start, stop), *range(j, end)):
                drop[k] = True
        elif can_open:
            openers[ch].append((j, end))
        j = end
    return "".join(ch for ch, dropped in zip(chars, drop, strict=True) if not dropped)


def plain_text(markdown: str) -> str:
    """Chữ người đọc thấy trên trang từ Markdown của bài (SL-T038-2, Lá Chắn T-038 điều kiện 2).

    1. Bỏ dấu ``\\`` do app thêm để vô hiệu link và ký tự ngắt địa chỉ (``unescape_link_syntax``).
    2. Link ``[chữ](địa chỉ)`` chỉ giữ chữ, ảnh ``![alt](địa chỉ)`` chỉ giữ alt, dòng khai báo link
       bị bỏ (``strip_markdown_links``): địa chỉ (kể cả ``javascript:``) không bao giờ vào JSON-LD.
    3. Từng dòng: bỏ dấu tiêu đề ``#``, trích dẫn ``>``, gạch đầu dòng.
    4. Từng đoạn (các dòng liền nhau): bỏ dấu nhấn (``_strip_inline``).
    5. Bỏ link lần nữa: link nằm trong đoạn ``mã`` (bước 2 cố ý bỏ qua đoạn mã) hay viết bằng dấu
       ngoặc đã escape giờ là chữ thường, cũng chỉ giữ chữ (SL-T041-6).
    6. ``normalize_text``.

    Không bao giờ đổi sang HTML: chữ ra vẫn phải qua ``_has_html`` và ``to_json_ld``. Chạy tuyến
    tính theo độ dài chữ.
    """
    text = strip_markdown_links(unescape_link_syntax(markdown))
    blocks: list[list[str]] = [[]]
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = _QUOTE_MARK.sub("", line)
        if _HEADING_MARK.match(line):
            blocks.append([_HEADING_TAIL.sub("", _HEADING_MARK.sub("", line))])
            blocks.append([])  # tiêu đề là một đoạn riêng
            continue
        if line.strip():
            blocks[-1].append(_LIST_MARK.sub("", line))
        elif blocks[-1]:
            blocks.append([])
    text = "\n\n".join(_strip_inline("\n".join(b)) for b in blocks if b)
    return normalize_text(strip_markdown_links(text))


def _has_html(text: str) -> bool:
    """Có thẻ HTML, kể cả viết dạng thực thể (``&lt;script&gt;``)."""
    return any(strip_tags(variant) != variant for variant in (text, html.unescape(text)))


# ------------------------------------------------------------------ kiểm loại

def check_schema_type(schema_type: object) -> Issue | None:
    """Kiểm một giá trị ``@type``. ``None`` nếu được phép dựng."""
    if not isinstance(schema_type, str) or not schema_type.strip():
        return Issue(Level.BLOCK, "Thiếu loại schema (@type) hoặc loại không phải một chữ.")
    name = schema_type.strip()
    if name in FORBIDDEN_TYPES:
        return Issue(Level.BLOCK, f"Không dùng schema {name}.")
    if name in SITE_OWNED_TYPES:
        return Issue(
            Level.BLOCK,
            f"Site đã tự xuất schema {name}; phần mềm không dựng loại này để tránh trùng.",
        )
    if name not in ALLOWED_TYPES:
        return Issue(Level.BLOCK, "Loại schema này không nằm trong danh sách phần mềm được dựng.")
    return None


def _expect_type(node: dict[str, Any], expected: str, where: str) -> Issue | None:
    raw = node.get("@type")
    if isinstance(raw, list):
        for item in raw:
            refused = check_schema_type(item)
            if refused is not None:
                return refused
        return Issue(Level.BLOCK, f"{where}: chỉ được một loại schema (@type).")
    refused = check_schema_type(raw)
    if refused is not None:
        return refused
    if raw.strip() != expected:
        return Issue(Level.BLOCK, f"{where}: loại phải là {expected}.")
    return None


# ------------------------------------------------------------------ kiểm URL


def _host(url: str) -> str | None:
    try:
        parts = urlsplit(url)
        host = parts.hostname
    except ValueError:
        return None
    if not host:
        return None
    return host.rstrip(".").lower()


def check_url(url: object, site_url: str | None) -> list[Issue]:
    """URL phải là ``https://``, không có tài khoản/mật khẩu, cùng tên máy với ``site_url``."""
    if not isinstance(url, str) or not url.strip():
        return [Issue(Level.BLOCK, "Địa chỉ trang (url) phải là một chữ không rỗng.")]
    if len(url) > MAX_URL_LENGTH:
        return [Issue(Level.BLOCK, f"Địa chỉ trang dài quá {MAX_URL_LENGTH} ký tự.")]
    if any(ch.isspace() or unicodedata.category(ch) in ("Cc", "Cf") for ch in url):
        return [Issue(Level.BLOCK, "Địa chỉ trang có khoảng trắng hoặc ký tự lạ.")]
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError:
        return [Issue(Level.BLOCK, "Địa chỉ trang không đúng dạng.")]
    if parts.scheme.lower() != "https":
        return [Issue(Level.BLOCK, "Địa chỉ trang phải bắt đầu bằng https://.")]
    if "@" in parts.netloc or parts.username is not None or parts.password is not None:
        return [Issue(Level.BLOCK, "Địa chỉ trang không được chứa tài khoản hoặc dấu @.")]
    host = _host(url)
    if host is None:
        return [Issue(Level.BLOCK, "Địa chỉ trang thiếu tên miền.")]
    site_host = _host(site_url) if isinstance(site_url, str) and site_url.strip() else None
    if site_host is None:
        return [Issue(Level.BLOCK, "Chưa khai báo địa chỉ website (WORDPRESS_URL) để đối chiếu.")]
    if host != site_host:
        return [Issue(Level.BLOCK, "Địa chỉ trang không cùng tên miền với website.")]
    if port not in (None, 443):
        return [Issue(Level.BLOCK, "Địa chỉ trang không được ghi cổng riêng.")]
    return []


# ------------------------------------------------------------------ kiểm chữ


def _check_text(
    value: object, *, label: str, max_length: int, article: str | None
) -> tuple[list[Issue], str | None]:
    """Kiểm một câu hỏi hoặc câu trả lời. Trả (vấn đề, chữ đã chuẩn hóa hoặc ``None``)."""
    if not isinstance(value, str):
        return [Issue(Level.BLOCK, f"{label}: phải là chữ.")], None
    text = normalize_text(value)
    issues: list[Issue] = []
    if not text:
        return [Issue(Level.BLOCK, f"{label}: đang để trống.")], None
    # Ký tự không được có trong câu hỏi, trả lời (Lá Chắn T-038 điều kiện 1, SL-T038-1): điều khiển
    # (Cc: NUL, ESC, DEL, C1…), surrogate lẻ (Cs: JSON-LD không mã hóa được UTF-8), ký tự riêng
    # (Co), ký tự chưa gán (Cn). Câu báo tách hai loại như ô meta (SL-T041-8, T-090): ký tự chưa
    # gán có thể là emoji rất mới, nhìn thấy được, nên không nói «không nhìn thấy».
    odd, unknown = odd_char_kinds(text)
    if odd:
        issues.append(
            Issue(
                Level.BLOCK,
                f"{label}: có ký tự điều khiển hoặc ký tự lạ (không nhìn thấy, thường do dán từ "
                "nơi khác). Sửa trong bài: gõ lại câu đó bằng chữ thường.",
            )
        )
    if unknown:
        issues.append(
            Issue(
                Level.BLOCK,
                f"{label}: có ký tự phần mềm chưa nhận ra (có thể là biểu tượng cảm xúc rất mới). "
                "Sửa trong bài: xóa ký tự đó hoặc thay bằng biểu tượng quen thuộc.",
            )
        )
    if _has_html(text):
        issues.append(Issue(Level.BLOCK, f"{label}: có thẻ HTML."))
    if len(text) > max_length:
        issues.append(Issue(Level.BLOCK, f"{label}: dài quá {max_length} ký tự."))
    if not issues and article is not None and text not in article:
        issues.append(Issue(Level.BLOCK, f"{label}: không có nguyên văn trong bài."))
    if not issues and MISSING_PATTERN.search(text):  # góp ý G3 Soi Lỗi T-041
        return [Issue(Level.WARN, f"{label}: còn chỗ «[cần bổ sung: …]» chưa điền.")], text
    return issues, (None if issues else text)


def _prepare_article(article_text: object) -> tuple[str | None, list[Issue]]:
    """Bài để đối chiếu: chữ người đọc thấy (``plain_text``, đã bỏ dấu Markdown)."""
    if not isinstance(article_text, str) or not article_text.strip():
        return None, [Issue(Level.BLOCK, "Chưa có nội dung bài để đối chiếu hỏi đáp.")]
    if len(article_text) > MAX_ARTICLE_LENGTH:
        return None, [Issue(Level.BLOCK, MSG_ARTICLE_TOO_LONG)]
    return plain_text(article_text), []


# ------------------------------------------------------------------ kiểm JSON-LD


def validate_faq_page(
    data: object, *, article_text: str, site_url: str | None = None
) -> list[Issue]:
    """Kiểm một FAQPage dạng dict (ví dụ đọc lại từ JSON). Danh sách rỗng = hợp lệ.

    Kiểm: ``@context``, ``@type`` (chặn HowTo và loại site đã xuất), khóa lạ, ``mainEntity``
    ≥ 1 câu, mỗi câu có ``name`` và ``acceptedAnswer.text`` không rỗng, không thẻ HTML, không
    ký tự điều khiển hay ký tự lạ, độ dài, URL cùng tên miền, nội dung có nguyên văn trong bài.
    ``article_text`` là Markdown của bài: so với chữ người đọc thấy (``plain_text``), nên chữ trong
    ``data`` còn dấu Markdown (``**``, link) thì không khớp và bị Chặn.
    """
    if not isinstance(data, dict):
        return [Issue(Level.BLOCK, "Schema phải là một đối tượng JSON.")]
    issues: list[Issue] = []
    if data.get("@context") != SCHEMA_CONTEXT:
        issues.append(Issue(Level.BLOCK, f"@context phải đúng {SCHEMA_CONTEXT}."))
    type_issue = _expect_type(data, "FAQPage", "Schema")
    if type_issue is not None:
        # Sai loại thì không kiểm tiếp phần trong: dữ liệu không phải FAQPage.
        return [*issues, type_issue]

    article, article_issues = _prepare_article(article_text)
    issues.extend(article_issues)

    if "url" in data:
        issues.extend(check_url(data["url"], site_url))

    entities = data.get("mainEntity")
    if not isinstance(entities, list) or not entities:
        issues.append(Issue(Level.BLOCK, "Cần ít nhất 1 câu hỏi (mainEntity)."))
        entities = []
    elif len(entities) > MAX_QUESTIONS:
        issues.append(Issue(Level.BLOCK, f"Tối đa {MAX_QUESTIONS} câu hỏi."))
        entities = []

    seen: set[str] = set()
    for index, node in enumerate(entities, start=1):
        where = f"Câu hỏi {index}"
        if not isinstance(node, dict):
            issues.append(Issue(Level.BLOCK, f"{where}: phải là một đối tượng."))
            continue
        type_issue = _expect_type(node, "Question", where)
        if type_issue is not None:
            issues.append(type_issue)
            continue
        found, question = _check_text(
            node.get("name"), label=where, max_length=MAX_QUESTION_LENGTH, article=article
        )
        issues.extend(found)
        if question is not None:
            key = question.casefold()
            if key in seen:
                issues.append(Issue(Level.WARN, f"{where}: trùng với một câu hỏi trước."))
            seen.add(key)
            if not question.endswith(("?", "？")):
                issues.append(Issue(Level.WARN, f"{where}: nên kết thúc bằng dấu hỏi."))
        answer = node.get("acceptedAnswer")
        if not isinstance(answer, dict):
            issues.append(Issue(Level.BLOCK, f"{where}: thiếu câu trả lời (acceptedAnswer)."))
            continue
        type_issue = _expect_type(answer, "Answer", f"Trả lời {index}")
        if type_issue is not None:
            issues.append(type_issue)
            continue
        found, _ = _check_text(
            answer.get("text"),
            label=f"Trả lời {index}",
            max_length=MAX_ANSWER_LENGTH,
            article=article,
        )
        issues.extend(found)

    # Khóa lạ, kiểu sai…: để khuôn pydantic (extra="forbid", strict) bắt.
    if not any(issue.level is Level.BLOCK for issue in issues):
        try:
            FAQPage.model_validate(data)
        except ValidationError:
            issues.append(
                Issue(Level.BLOCK, "Schema có trường lạ hoặc sai kiểu so với khuôn FAQPage.")
            )
    return issues


# ------------------------------------------------------------------ dựng


def build_faq_page(
    pairs: Iterable[tuple[str, str]],
    *,
    article_text: str,
    site_url: str | None = None,
    page_url: str | None = None,
) -> SchemaResult:
    """Dựng FAQPage từ các cặp (câu hỏi, trả lời) đã có trong bài.

    Câu hỏi, trả lời (Markdown như trong bài) được đổi thành chữ người đọc thấy (``plain_text``:
    bỏ dấu Markdown, link chỉ giữ chữ, chuẩn hóa NFC và khoảng trắng) trước khi dựng và đối chiếu
    với ``article_text``. Có vấn đề mức Chặn thì không dựng (``page`` và ``json_ld`` là ``None``);
    chỉ có Cảnh báo thì vẫn dựng.
    """
    entities: list[dict[str, Any]] = []
    for pair in pairs:
        try:
            question, answer = pair
        except (TypeError, ValueError):
            return SchemaResult(
                None, None, (Issue(Level.BLOCK, "Mỗi mục hỏi đáp phải gồm câu hỏi và trả lời."),)
            )
        entities.append(
            {
                "@type": "Question",
                "name": plain_text(question) if isinstance(question, str) else question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": plain_text(answer) if isinstance(answer, str) else answer,
                },
            }
        )
        if len(entities) > MAX_QUESTIONS:
            break
    data: dict[str, Any] = {"@context": SCHEMA_CONTEXT, "@type": "FAQPage"}
    if page_url is not None:
        data["url"] = page_url
    data["mainEntity"] = entities

    issues = validate_faq_page(data, article_text=article_text, site_url=site_url)
    if any(issue.level is Level.BLOCK for issue in issues):
        return SchemaResult(None, None, tuple(issues))
    page = FAQPage.model_validate(data)
    return SchemaResult(page, to_json_ld(page), tuple(issues))


# ------------------------------------------------------------------ mục Hỏi đáp trong bài (T-041)

# Tiêu đề mục Hỏi đáp, so trên chữ không dấu, chữ thường, dấu câu thành dấu cách: «Hỏi đáp»,
# «Hỏi - đáp», «Hỏi và đáp», «Câu hỏi thường gặp», «Thắc mắc thường gặp», «FAQ».
_FAQ_HEADING = re.compile(r"\b(?:hoi (?:va )?dap|cau hoi|thac mac|faq)\b")
_NOT_WORD = re.compile(r"[\W_]+")
# Câu hỏi là cả dòng in đậm kết thúc bằng dấu hỏi (có thể có gạch đầu dòng trước, chữ trả lời sau).
_BOLD_QUESTION = re.compile(r"(?:[-*+]|\d{1,9}[.)])?[ \t]*(\*\*|__)(.+?[?？])\1[ \t]*(.*)")
MSG_NO_FAQ = "Bài chưa có mục Hỏi đáp (tiêu đề mục có «Hỏi đáp» hay «Câu hỏi thường gặp»)."
# Có mục Hỏi đáp nhưng chưa nhận ra cặp hỏi-đáp nào (góp ý 4 của Họa Sĩ T-041).
MSG_NO_FAQ_QUESTION = (
    "Mục Hỏi đáp chưa có câu hỏi đúng dạng: mỗi câu hỏi là tiêu đề con (###) hay dòng in đậm, kết "
    "thúc bằng dấu hỏi, câu trả lời nằm ngay bên dưới."
)


def _is_faq_heading(heading: str) -> bool:
    words = _NOT_WORD.sub(" ", remove_accents(normalize_text(heading)).lower())
    return _FAQ_HEADING.search(" ".join(words.split())) is not None


def _is_question(markdown: str) -> bool:
    return plain_text(markdown).endswith(("?", "？"))


def _question_of(block: list[str]) -> tuple[str, str] | None:
    """(câu hỏi, chữ trả lời cùng dòng) nếu đoạn ``block`` mở đầu bằng một câu hỏi."""
    first = block[0].strip()
    if _HEADING_MARK.match(first):
        heading = _HEADING_TAIL.sub("", _HEADING_MARK.sub("", first))
        # Tiêu đề con chỉ là câu hỏi khi kết thúc bằng dấu hỏi (SL-T041-5).
        return (heading, "\n".join(block[1:])) if _is_question(heading) else None
    bold = _BOLD_QUESTION.fullmatch(first)
    if bold is not None:
        return bold.group(2), "\n".join([bold.group(3), *block[1:]])
    # Đoạn một dòng là câu hỏi; gạch đầu dòng thì không (danh sách câu nên hỏi thợ trong trả lời).
    if len(block) == 1 and not _LIST_MARK.match(first) and _is_question(first):
        return first, ""
    return None


def find_faq(parts: Sequence[Section]) -> list[tuple[str, str]]:
    """Các cặp (câu hỏi, trả lời) trong mục Hỏi đáp của bài, ở dạng Markdown như trong bài.

    Mục Hỏi đáp: phần không phải mở bài (phần 0) có tiêu đề như ``_FAQ_HEADING``. Trong thân mục,
    câu hỏi là dòng tiêu đề con kết thúc bằng «?» (``### …?``), dòng in đậm cả câu kết thúc bằng
    «?» (``**…?**``, trả lời có thể nằm tiếp ngay sau trên cùng dòng), hoặc đoạn chỉ một dòng kết
    thúc bằng «?». Trả lời là các dòng sau đó tới câu hỏi kế tiếp; tiêu đề con không phải câu hỏi
    («### Lưu ý») kết thúc câu trả lời đang có (SL-T041-5). Câu hỏi không có trả lời bị bỏ. Lấy tối
    đa ``MAX_QUESTIONS + 1`` cặp: dựng thì ``build_faq_page`` báo quá nhiều.
    """
    pairs: list[tuple[str, str]] = []
    for part in list(parts)[1:]:
        if not _is_faq_heading(part.heading):
            continue
        question: str | None = None
        answer: list[str] = []
        # Đoạn: các dòng liền nhau; dòng trống ngăn đoạn, dòng tiêu đề con luôn mở đoạn mới.
        blocks: list[list[str]] = [[]]
        for line in part.body.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
            if _HEADING_MARK.match(line) and blocks[-1]:
                blocks.append([])
            if line.strip():
                blocks[-1].append(line)
            elif blocks[-1]:
                blocks.append([])
        for block in (b for b in blocks if b):
            found = _question_of(block)
            if found is None and not _HEADING_MARK.match(block[0].strip()):
                if question is not None:
                    answer.append("\n".join(block))
                continue
            if question is not None and plain_text("\n\n".join(answer)):
                pairs.append((question, "\n\n".join(answer)))
            question, answer = None, []
            if found is not None:
                question, rest = found
                answer = [rest] if rest.strip() else []
            if len(pairs) > MAX_QUESTIONS:
                return pairs
        if question is not None and plain_text("\n\n".join(answer)):
            pairs.append((question, "\n\n".join(answer)))
    return pairs[: MAX_QUESTIONS + 1]


def article_markdown(parts: Sequence[Section]) -> str:
    """Cả bài (tiêu đề từng phần và thân phần) dạng Markdown, để đối chiếu hỏi đáp."""
    return "\n\n".join(f"{part.heading}\n\n{part.body}" for part in parts)


def build_article_faq(
    parts: Sequence[Section], *, site_url: str | None = None, page_url: str | None = None
) -> SchemaResult:
    """FAQPage của bài: tìm mục Hỏi đáp (``find_faq``) rồi dựng và kiểm (``build_faq_page``).

    Bài chưa có mục Hỏi đáp: kết quả Chặn với câu ``MSG_NO_FAQ``. Bài dài quá
    ``MAX_ARTICLE_LENGTH`` thì Chặn ngay, trước khi tìm mục Hỏi đáp (góp ý G2 Soi Lỗi T-041: bài dán
    nhầm vài triệu ký tự không làm trang chậm). Giao diện hiện ``json_ld`` bằng
    ``st.code(..., language="json")`` và ``issues`` bằng chữ thuần (câu báo không chép chữ của bài).
    """
    article = article_markdown(parts)
    if len(article) > MAX_ARTICLE_LENGTH:
        return SchemaResult(None, None, (Issue(Level.BLOCK, MSG_ARTICLE_TOO_LONG),))
    pairs = find_faq(parts)
    if not pairs:
        has_section = any(_is_faq_heading(part.heading) for part in list(parts)[1:])
        message = MSG_NO_FAQ_QUESTION if has_section else MSG_NO_FAQ
        return SchemaResult(None, None, (Issue(Level.BLOCK, message),))
    return build_faq_page(pairs, article_text=article, site_url=site_url, page_url=page_url)


# ------------------------------------------------------------------ xuất JSON an toàn

_SCRIPT_SAFE = str.maketrans(
    {
        "<": "\\u003c",
        ">": "\\u003e",
        "&": "\\u0026",
        " ": "\\u2028",
        " ": "\\u2029",
    }
)


def to_json_ld(page: FAQPage) -> str:
    """Chuỗi JSON-LD an toàn để đặt trong ``<script type="application/ld+json">``.

    ``<``, ``>``, ``&`` (và U+2028, U+2029) chỉ có thể nằm trong chuỗi JSON, nên đổi thành dạng
    ``\\uXXXX`` vẫn là JSON hợp lệ, đọc lại (``json.loads``) ra đúng nội dung, nhưng không bao
    giờ tạo được ``</script>`` hay ``<!--``.
    """
    text = json.dumps(page.to_data(), ensure_ascii=False, indent=2)
    return text.translate(_SCRIPT_SAFE)

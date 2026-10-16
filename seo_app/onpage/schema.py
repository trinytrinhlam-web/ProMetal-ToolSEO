"""Schema JSON-LD loại FAQPage: dựng từ cặp hỏi-đáp và kiểm hợp lệ, không cần mạng.

Thiết kế: ``docs/team/reports/T-033-tho-may.md`` mục 3.

- Site đã tự xuất Article, BreadcrumbList, LocalBusiness (và Organization của SiteSEO), nên
  phần mềm **từ chối dựng** các loại đó (``SITE_OWNED_TYPES``). ``HowTo`` luôn bị chặn.
- **AI không viết JSON.** Code dựng JSON-LD từ danh sách cặp (câu hỏi, trả lời) đã có trong bài.
- Câu hỏi và trả lời phải có **nguyên văn** trong bài (sau chuẩn hóa NFC và khoảng trắng):
  Google yêu cầu nội dung schema hiện trên trang.
- Chuỗi JSON xuất ra đổi ``<``, ``>``, ``&`` thành ``\\u003c``, ``\\u003e``, ``\\u0026`` nên không
  bao giờ đóng được thẻ ``</script>``.
- Giai đoạn 4 **chưa** đưa schema lên site (cách "d" mục 3.3); kết quả chỉ để xem trước và kiểm.

Mọi hàm ở đây là hàm thuần: không đọc ``.env``, không gọi mạng. Địa chỉ site (``WORDPRESS_URL``)
truyền vào dạng tham số.
"""

from __future__ import annotations

import html
import json
import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from seo_app.content.rules import IGNORABLE_NOT_CF
from seo_app.sanitize import strip_tags

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


def _has_control(text: str) -> bool:
    """Còn ký tự điều khiển (loại Cc) sau chuẩn hóa: NUL, ESC, DEL, C1…"""
    return any(unicodedata.category(ch) == "Cc" for ch in text)


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
    if _has_control(text):
        issues.append(Issue(Level.BLOCK, f"{label}: có ký tự điều khiển."))
    if _has_html(text):
        issues.append(Issue(Level.BLOCK, f"{label}: có thẻ HTML."))
    if len(text) > max_length:
        issues.append(Issue(Level.BLOCK, f"{label}: dài quá {max_length} ký tự."))
    if not issues and article is not None and text not in article:
        issues.append(Issue(Level.BLOCK, f"{label}: không có nguyên văn trong bài."))
    return issues, (None if issues else text)


def _prepare_article(article_text: object) -> tuple[str | None, list[Issue]]:
    if not isinstance(article_text, str) or not article_text.strip():
        return None, [Issue(Level.BLOCK, "Chưa có nội dung bài để đối chiếu hỏi đáp.")]
    if len(article_text) > MAX_ARTICLE_LENGTH:
        return None, [Issue(Level.BLOCK, "Bài quá dài, không đối chiếu được hỏi đáp.")]
    return normalize_text(article_text), []


# ------------------------------------------------------------------ kiểm JSON-LD


def validate_faq_page(
    data: object, *, article_text: str, site_url: str | None = None
) -> list[Issue]:
    """Kiểm một FAQPage dạng dict (ví dụ đọc lại từ JSON). Danh sách rỗng = hợp lệ.

    Kiểm: ``@context``, ``@type`` (chặn HowTo và loại site đã xuất), khóa lạ, ``mainEntity``
    ≥ 1 câu, mỗi câu có ``name`` và ``acceptedAnswer.text`` không rỗng, không thẻ HTML, không
    ký tự điều khiển, độ dài, URL cùng tên miền, nội dung có nguyên văn trong bài.
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

    Chữ được chuẩn hóa (NFC, khoảng trắng) trước khi dựng. Có vấn đề mức Chặn thì không dựng
    (``page`` và ``json_ld`` là ``None``); chỉ có Cảnh báo thì vẫn dựng.
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
                "name": normalize_text(question) if isinstance(question, str) else question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": normalize_text(answer) if isinstance(answer, str) else answer,
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

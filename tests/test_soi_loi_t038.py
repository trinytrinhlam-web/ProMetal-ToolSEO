"""Soi Lỗi · T-038: thử phá schema FAQPage (dựng, kiểm, xuất JSON-LD).

Lỗi chưa sửa đánh ``xfail(strict=True)`` kèm mã ``SL-T038-n`` (xem
``docs/team/reports/T-038-soi-loi.md``). Không gọi mạng.
"""

from __future__ import annotations

import itertools
import json
import unicodedata

import pytest

from seo_app.onpage.schema import (
    MAX_QUESTIONS,
    SITE_OWNED_TYPES,
    FAQPage,
    Level,
    build_faq_page,
    check_schema_type,
    check_url,
    normalize_text,
    to_json_ld,
    validate_faq_page,
)
from tests.timing import assert_scales_linearly

SITE = "https://suachuacuasat.com"
Q = "Cửa sắt sơn tĩnh điện dùng được bao lâu?"
A = "Thường 8–10 năm nếu lau bụi mỗi tháng và sơn dặm chỗ trầy."


def _article(q: str = Q, a: str = A) -> str:
    return f"# Bài\n\nMở bài.\n\n## Hỏi đáp\n\n### {q}\n\n{a}\n"


def _build(q: str = Q, a: str = A, article: str | None = None, **kwargs):
    kwargs.setdefault("site_url", SITE)
    text = _article(q, a) if article is None else article
    return build_faq_page([(q, a)], article_text=text, **kwargs)


def _data(q: str = Q, a: str = A, **extra) -> dict:
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        ],
    }
    data.update(extra)
    return data


def _assert_script_safe(json_ld: str) -> None:
    for bad in ("<", ">", "&", " ", " "):
        assert bad not in json_ld
    assert "</script" not in json_ld.lower()


# ------------------------------------------------------------------ 1. tiêu chí phiếu


def test_happy_path_output_shape():
    result = _build(page_url="https://suachuacuasat.com/cua-sat/")
    assert not result.blocked
    data = json.loads(result.json_ld)
    assert data["@context"] == "https://schema.org"
    assert data["@type"] == "FAQPage"
    assert data["url"] == "https://suachuacuasat.com/cua-sat/"
    entity = data["mainEntity"][0]
    assert entity == {
        "@type": "Question",
        "name": Q,
        "acceptedAnswer": {"@type": "Answer", "text": A},
    }


@pytest.mark.parametrize("name", ["HowTo", " HowTo ", "howto", "HowToStep", "https://schema.org/HowTo"])
def test_howto_variants_never_allowed(name):
    issue = check_schema_type(name)
    assert issue is not None and issue.level is Level.BLOCK


@pytest.mark.parametrize("name", sorted(SITE_OWNED_TYPES))
def test_site_owned_types_refused_at_top_and_nested(name):
    assert _blocked(validate_faq_page({**_data(), "@type": name}, article_text=_article()))
    nested = _data()
    nested["mainEntity"][0]["@type"] = name
    assert _blocked(validate_faq_page(nested, article_text=_article()))
    nested = _data()
    nested["mainEntity"][0]["acceptedAnswer"]["@type"] = name
    assert _blocked(validate_faq_page(nested, article_text=_article()))


@pytest.mark.parametrize(
    "type_value", [["FAQPage"], ["FAQPage", "HowTo"], {"x": 1}, None, "", "FAQPage ", 5]
)
def test_odd_top_type_values_blocked(type_value):
    assert _blocked(validate_faq_page({**_data(), "@type": type_value}, article_text=_article()))


@pytest.mark.parametrize(
    "context",
    ["http://schema.org", "https://schema.org/", ["https://schema.org"], None, "https://evil.tld"],
)
def test_bad_context_blocked(context):
    assert _blocked(validate_faq_page({**_data(), "@context": context}, article_text=_article()))


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.update({"@id": "https://suachuacuasat.com/#faq"}),
        lambda d: d["mainEntity"][0].update({"url": "https://suachuacuasat.com/"}),
        lambda d: d["mainEntity"][0]["acceptedAnswer"].update({"author": "x"}),
        lambda d: d.update({"name": "FAQ"}),
    ],
)
def test_extra_keys_forbidden_anywhere(mutate):
    data = _data()
    mutate(data)
    assert _blocked(validate_faq_page(data, article_text=_article()))


def test_question_count_bounds():
    assert _blocked(validate_faq_page(_data() | {"mainEntity": []}, article_text=_article()))
    pairs = [(f"Câu {i}?", f"Đáp {i}.") for i in range(MAX_QUESTIONS + 1)]
    article = "\n".join(f"{q} {a}" for q, a in pairs)
    assert not build_faq_page(pairs[:MAX_QUESTIONS], article_text=article, site_url=SITE).blocked
    assert build_faq_page(pairs, article_text=article, site_url=SITE).blocked


def test_infinite_pairs_generator_terminates():
    pairs = ((f"q{i}?", "a") for i in itertools.count())
    assert build_faq_page(pairs, article_text="q1? a", site_url=SITE).blocked


@pytest.mark.parametrize("bad", ["a\x00b", "a\x07b", "a\x1bb", "a\x7fb", "a\x9bb"])
def test_control_chars_blocked(bad):
    assert _build(a=bad).blocked
    assert _build(q=bad + "?").blocked


@pytest.mark.parametrize("ws", ["a\x1fb", "a\x0bb", "a\x85b", "a b", "a b"])
def test_whitespace_like_controls_become_plain_space(ws):
    """Python coi các ký tự này là khoảng trắng: được gộp thành dấu cách, không lọt ra JSON."""
    result = _build(a=ws)
    assert not result.blocked
    assert json.loads(result.json_ld)["mainEntity"][0]["acceptedAnswer"]["text"] == "a b"


@pytest.mark.parametrize(
    "html_text",
    [
        "</script><script>alert(1)</script>",
        "</SCRIPT >",
        "<img src=x onerror=alert(1)>",
        "<!-- x",
        "&lt;script&gt;",
        "&#60;script&#62;",
        "&#x3c;img onerror=1&#x3e;",
        "<​script>",
        "<scr<script>ipt>",
    ],
)
def test_html_blocked_in_question_and_answer(html_text):
    assert _build(a=html_text).blocked
    assert _build(q=html_text + "?").blocked


@pytest.mark.parametrize("ok", ["a < b & c > d", "<3 và 2>1", "x <= 3", "Tom & Jerry", "＜b＞"])
def test_plain_math_and_fullwidth_not_html(ok):
    result = _build(a=ok)
    assert not result.blocked
    _assert_script_safe(result.json_ld)
    assert json.loads(result.json_ld)["mainEntity"][0]["acceptedAnswer"]["text"] == ok


def test_length_limits():
    assert _build(q="x" * 300 + "?").blocked
    assert not _build(q="x" * 299 + "?").blocked
    assert _build(a="y" * 2001).blocked
    assert not _build(a="y" * 2000).blocked
    assert build_faq_page([(Q, A)], article_text="x" * 500_001, site_url=SITE).blocked


# ------------------------------------------------------------------ 2. phá JSON xuất ra

PAYLOADS = [
    "Đóng thẻ </script> giữa câu",
    "Mở chú thích <!-- và đóng -->",
    "CDATA ]]> và <![CDATA[",
    "Dòng mới nữa",
    "Dấu < viết sẵn và > và &",
    "Thực thể &amp; hợp lệ",
    "Chữ toàn khổ ＜／script＞",
    'Ngoặc "kép" và \\ gạch ngược',
]


@pytest.mark.parametrize("payload", PAYLOADS)
def test_payload_never_escapes_script_and_roundtrips(payload):
    """Dựng thẳng khuôn (bỏ qua bộ kiểm) để chắc ``to_json_ld`` tự an toàn."""
    page = FAQPage.model_validate(_data(q=payload, a=payload, url="https://x/</script>"))
    out = to_json_ld(page)
    _assert_script_safe(out)
    back = json.loads(out)
    assert back["mainEntity"][0]["name"] == payload
    assert back["mainEntity"][0]["acceptedAnswer"]["text"] == payload
    assert back["url"] == "https://x/</script>"


@pytest.mark.parametrize(
    "payload",
    ["Ký tự ]]> lạ", "Dấu < viết sẵn và > và &", "Thực thể &amp; hợp lệ", "Toàn khổ ＜／script＞"],
)
def test_payload_through_build(payload):
    result = _build(a=payload)
    assert not result.blocked
    _assert_script_safe(result.json_ld)
    assert json.loads(result.json_ld)["mainEntity"][0]["acceptedAnswer"]["text"] == payload


@pytest.mark.xfail(strict=True, reason="SL-T038-1: ký tự thay thế lẻ (surrogate) lọt qua bộ kiểm")
def test_lone_surrogate_blocked():
    result = _build(a="Trả lời \ud800 lỗi.")
    assert result.blocked


def test_lone_surrogate_output_is_at_least_valid_json():
    """Trạng thái hiện tại của SL-T038-1: JSON đọc lại được nhưng không mã hóa được UTF-8."""
    result = _build(a="Trả lời \ud800 lỗi.")
    if result.json_ld is not None:
        json.loads(result.json_ld)
        with pytest.raises(UnicodeEncodeError):
            result.json_ld.encode("utf-8")


def test_output_always_utf8_encodable_for_normal_vietnamese():
    result = _build()
    result.json_ld.encode("utf-8")


# ------------------------------------------------------------------ 3. khớp nguyên văn


def test_nfd_question_and_nfc_article_match_both_ways():
    nfd_q, nfd_a = unicodedata.normalize("NFD", Q), unicodedata.normalize("NFD", A)
    assert not build_faq_page([(nfd_q, nfd_a)], article_text=_article(), site_url=SITE).blocked
    nfd_article = unicodedata.normalize("NFD", _article())
    result = build_faq_page([(Q, A)], article_text=nfd_article, site_url=SITE)
    assert not result.blocked
    text = json.loads(result.json_ld)["mainEntity"][0]["name"]
    assert text == unicodedata.normalize("NFC", text)


@pytest.mark.parametrize("space", [" ", " ", "　", "\t", "\n", "  "])
def test_odd_spaces_match(space):
    article = _article(Q.replace(" ", space), A.replace(" ", space))
    assert not build_faq_page([(Q, A)], article_text=article, site_url=SITE).blocked
    assert not build_faq_page(
        [(Q.replace(" ", space), A)], article_text=_article(), site_url=SITE
    ).blocked


@pytest.mark.parametrize("invisible", ["​", "﻿", "⁠", "­", "‍"])
def test_invisible_chars_ignored_and_removed_from_output(invisible):
    q = Q.replace("sắt", "s" + invisible + "ắt")
    result = build_faq_page([(q, A)], article_text=_article(), site_url=SITE)
    assert not result.blocked
    assert invisible not in result.json_ld


def test_question_in_paragraph_not_heading():
    article = f"Khách hay hỏi: {Q} Xưởng trả lời: {A}"
    assert not build_faq_page([(Q, A)], article_text=article, site_url=SITE).blocked


def test_question_in_bold_paragraph():
    article = f"## Hỏi đáp\n\n**{Q}**\n\n{A}\n"
    assert not build_faq_page([(Q, A)], article_text=article, site_url=SITE).blocked


def test_answer_spanning_two_paragraphs_matches_after_space_collapse():
    a = "Câu một. Câu hai."
    article = f"### {Q}\n\nCâu một.\n\nCâu hai.\n"
    assert not build_faq_page([(Q, a)], article_text=article, site_url=SITE).blocked


def test_paraphrase_and_case_change_blocked():
    assert build_faq_page([(Q.lower(), A)], article_text=_article(), site_url=SITE).blocked
    assert build_faq_page(
        [(Q, A.replace("Thường", "Thông thường"))], article_text=_article(), site_url=SITE
    ).blocked


BOLD_ANSWER_MD = "Thường **8–10 năm** nếu lau bụi mỗi tháng và sơn dặm chỗ trầy."


def test_bold_answer_raw_markdown_passes_and_leaks_asterisks():
    """Hiện tại: truyền đúng chữ thô thì qua, nhưng JSON-LD mang theo dấu ``**``."""
    result = build_faq_page(
        [(Q, BOLD_ANSWER_MD)], article_text=_article(a=BOLD_ANSWER_MD), site_url=SITE
    )
    assert not result.blocked
    assert "**" in json.loads(result.json_ld)["mainEntity"][0]["acceptedAnswer"]["text"]


@pytest.mark.xfail(
    strict=True,
    reason="SL-T038-2: câu trả lời chữ thường không khớp bài có **đậm**/link Markdown",
)
@pytest.mark.parametrize(
    "md_answer",
    [
        BOLD_ANSWER_MD,
        "Thường *8–10 năm* nếu lau bụi mỗi tháng và sơn dặm chỗ trầy.",
        "Thường 8–10 năm nếu lau bụi mỗi tháng và [sơn dặm](https://suachuacuasat.com/x) chỗ trầy.",
        "Thường `8–10 năm` nếu lau bụi mỗi tháng và sơn dặm chỗ trầy.",
    ],
)
def test_plain_answer_matches_markdown_formatted_article(md_answer):
    result = build_faq_page([(Q, A)], article_text=_article(a=md_answer), site_url=SITE)
    assert not result.blocked


# ------------------------------------------------------------------ 4. URL


@pytest.mark.parametrize(
    "url",
    [
        "https://suachuacuasat.com/",
        "https://suachuacuasat.com/cua-sat/?p=1#faq",
        "HTTPS://SUACHUACUASAT.COM/a",
        "https://suachuacuasat.com./a",
        "https://suachuacuasat.com:443/a",
    ],
)
def test_url_ok(url):
    assert check_url(url, SITE) == []


@pytest.mark.parametrize(
    "url",
    [
        "http://suachuacuasat.com/",
        "https://www.suachuacuasat.com/",
        "https://suachuacuasat.com.evil.tld/",
        "https://evilsuachuacuasat.com/",
        "https://suachuacuasat.com@evil.tld/",
        "https://evil.tld@suachuacuasat.com/",
        "https://user:pass@suachuacuasat.com/",
        "https://xn--suachuacusat-x.com/",
        "https://suachuacuasát.com/",
        "https://suachuacuasat。com/",
        "https://suachuacuasat.com%2eevil.tld/",
        "https://suachuacuasat.com\\@evil.tld/",
        "https://suachuacuasat.com\\evil.tld/",
        "https:suachuacuasat.com/",
        "https:///suachuacuasat.com/",
        "//suachuacuasat.com/",
        "javascript:alert(1)//suachuacuasat.com",
        "https://suachuacuasat.com:8443/",
        "https://suachuacuasat.com:99999/",
        "https://[::1]/",
        "https://suachuacuasat.com/ a",
        "https://suachuacuasat.com/‮x",
        "",
        None,
        "https://suachuacuasat.com/" + "a" * 2000,
    ],
)
def test_url_bad(url):
    issues = check_url(url, SITE)
    assert issues and all(issue.level is Level.BLOCK for issue in issues)


def test_www_site_accepts_only_www():
    www = "https://www.suachuacuasat.com"
    assert check_url("https://www.suachuacuasat.com/a", www) == []
    assert check_url("https://suachuacuasat.com/a", www)


@pytest.mark.parametrize("site", [None, "", "   ", "khong-phai-url"])
def test_url_without_site_blocked(site):
    assert check_url("https://suachuacuasat.com/", site)


def test_bad_page_url_blocks_build():
    assert _build(page_url="https://suachuacuasat.com.evil.tld/").blocked
    assert _build(page_url="http://suachuacuasat.com/").blocked


def test_messages_do_not_echo_url_or_text():
    secret = "MA-BI-MAT-123"
    result = _build(
        q=f"<b>{secret}</b>?", a=secret, page_url=f"https://{secret}.evil.tld/"
    )
    assert result.blocked
    assert all(secret not in issue.message for issue in result.issues)


# ------------------------------------------------------------------ 5. tốc độ


def _long_article(scale: int) -> tuple[list[tuple[str, str]], str]:
    pairs = [
        (f"Câu {i} hỏi về cửa sắt?", "Trả lời " + "cửa sắt " * 200 + str(i))
        for i in range(MAX_QUESTIONS)
    ]
    body = "Đoạn văn về cửa sắt sơn tĩnh điện. " * (2500 * scale)
    return pairs, body + "\n".join(f"### {q}\n\n{a}" for q, a in pairs)


def test_build_scales_linearly_with_article_length():
    cache: dict[str, list[tuple[str, str]]] = {}

    def make(k: int) -> str:
        pairs, article = _long_article(k)
        cache[article] = pairs
        return article

    def run(article: str) -> None:
        result = build_faq_page(cache[article], article_text=article, site_url=SITE)
        assert not result.blocked

    assert_scales_linearly(run, make, label="bài dài")


def test_worst_case_substring_search_is_fast_enough():
    import time

    article = "a" * 499_000
    pairs = [("a" * 298 + "b?", "a" * 1999 + "b")] * MAX_QUESTIONS
    start = time.process_time()
    assert build_faq_page(pairs, article_text=article, site_url=SITE).blocked
    assert time.process_time() - start < 5.0


def test_normalize_text_idempotent():
    for text in [Q, A, "a​ b ́c", unicodedata.normalize("NFD", Q)]:
        once = normalize_text(text)
        assert normalize_text(once) == once


def _blocked(issues) -> bool:
    return any(issue.level is Level.BLOCK for issue in issues)

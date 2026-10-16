"""T-038: dựng và kiểm schema FAQPage không cần mạng."""

from __future__ import annotations

import json

import pytest

from seo_app.onpage.schema import (
    FORBIDDEN_TYPES,
    MAX_ANSWER_LENGTH,
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

SITE = "https://suachuacuasat.com"
Q1 = "Cửa sắt sơn tĩnh điện dùng được bao lâu?"
A1 = "Thường 8–10 năm nếu lau bụi mỗi tháng và sơn dặm chỗ trầy."
Q2 = "Có cần sơn lót chống gỉ không?"
A2 = "Có. Xưởng luôn sơn lót epoxy trước khi sơn phủ."
ARTICLE = f"""# Cửa sắt sơn tĩnh điện

Đoạn mở bài.

## Hỏi đáp

### {Q1}

{A1}

### {Q2}

{A2}
"""


def _messages(issues) -> str:
    return " | ".join(issue.message for issue in issues)


def _blocked(issues) -> bool:
    return any(issue.level is Level.BLOCK for issue in issues)


def _build(pairs, article=ARTICLE, **kwargs):
    kwargs.setdefault("site_url", SITE)
    return build_faq_page(pairs, article_text=article, **kwargs)


# ------------------------------------------------------------------ dựng


def test_build_ok_and_json_roundtrip():
    result = _build([(Q1, A1), (Q2, A2)], page_url=SITE + "/cua-sat-son-tinh-dien/")
    assert not result.blocked, _messages(result.issues)
    assert result.issues == ()
    data = json.loads(result.json_ld)
    assert data["@context"] == "https://schema.org"
    assert data["@type"] == "FAQPage"
    assert data["url"] == SITE + "/cua-sat-son-tinh-dien/"
    assert [q["name"] for q in data["mainEntity"]] == [Q1, Q2]
    assert [q["acceptedAnswer"]["text"] for q in data["mainEntity"]] == [A1, A2]
    assert all(q["@type"] == "Question" for q in data["mainEntity"])
    assert all(q["acceptedAnswer"]["@type"] == "Answer" for q in data["mainEntity"])
    # Đọc lại vẫn qua bộ kiểm.
    assert validate_faq_page(data, article_text=ARTICLE, site_url=SITE) == []


def test_build_without_url_has_no_url_key():
    result = _build([(Q1, A1)])
    assert "url" not in json.loads(result.json_ld)


def test_json_keeps_vietnamese_unescaped():
    result = _build([(Q1, A1)])
    assert "Cửa sắt" in result.json_ld


def test_whitespace_and_nfd_are_normalized_for_matching():
    import unicodedata

    question = unicodedata.normalize("NFD", "Cửa sắt   sơn tĩnh điện\ndùng được bao lâu?")
    answer = "  Thường 8–10 năm nếu lau bụi​ mỗi tháng và sơn dặm chỗ trầy.\n"
    result = _build([(question, answer)])
    assert not result.blocked, _messages(result.issues)
    data = json.loads(result.json_ld)
    assert data["mainEntity"][0]["name"] == Q1
    assert data["mainEntity"][0]["acceptedAnswer"]["text"] == A1


def test_article_in_nfd_still_matches():
    import unicodedata

    result = _build([(Q1, A1)], article=unicodedata.normalize("NFD", ARTICLE))
    assert not result.blocked, _messages(result.issues)


def test_pydantic_models_forbid_extra():
    with pytest.raises(ValueError):
        FAQPage.model_validate(
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": "a?", "acceptedAnswer": {"text": "b"}}
                ],
                "author": "x",
            }
        )


# ------------------------------------------------------------------ khớp nội dung


def test_question_not_in_article_is_blocked():
    result = _build([("Cửa cuốn có ồn không?", A1)])
    assert result.blocked
    assert result.page is None and result.json_ld is None
    assert "không có nguyên văn trong bài" in _messages(result.issues)


def test_answer_paraphrased_is_blocked():
    result = _build([(Q1, "Khoảng 8 đến 10 năm.")])
    assert result.blocked
    assert "Trả lời 1: không có nguyên văn" in _messages(result.issues)


def test_empty_article_is_blocked():
    result = _build([(Q1, A1)], article="   ")
    assert result.blocked
    assert "Chưa có nội dung bài" in _messages(result.issues)


# ------------------------------------------------------------------ dữ liệu độc


@pytest.mark.parametrize(
    "payload",
    [
        "</script><script>alert(1)</script>",
        '<img src=x onerror="alert(1)">',
        "&lt;script&gt;alert(1)&lt;/script&gt;",
        "<!-- x -->",
        "<svg/onload=alert(1)>",
    ],
)
def test_html_in_question_or_answer_is_blocked(payload):
    question = f"Hỏi {payload}?"
    answer = f"Đáp {payload}."
    article = ARTICLE + f"\n{question}\n{answer}\n"
    result = _build([(question, A1)], article=article)
    assert result.blocked and result.json_ld is None
    assert "có thẻ HTML" in _messages(result.issues)
    result = _build([(Q1, answer)], article=article)
    assert result.blocked and result.json_ld is None


@pytest.mark.parametrize("char", ["\x00", "\x1b", "\x7f", "\x85\x00", "\x9b"])
def test_control_characters_are_blocked(char):
    answer = f"Có{char} chứ."
    result = _build([(Q1, answer)], article=ARTICLE + answer)
    assert result.blocked
    assert "ký tự điều khiển" in _messages(result.issues)


def test_messages_never_echo_input():
    payload = "<img src=x onerror=alert(1)>"
    result = _build([(payload + "?", payload)], article=ARTICLE + payload)
    assert payload not in _messages(result.issues)
    assert "onerror" not in _messages(result.issues)


def test_json_output_cannot_close_script_tag():
    # Dữ liệu hợp lệ (không phải thẻ) nhưng có <, >, &: vẫn không được thành "</script" hay "<!--".
    question = "Giá cửa < 5 triệu & cửa > 2 m thì sao?"
    answer = "So sánh a < b, b > c & d; x <= 3 && y >= 1 -->."
    article = ARTICLE + f"\n{question}\n{answer}\n"
    result = _build([(question, answer)], article=article)
    assert not result.blocked, _messages(result.issues)
    text = result.json_ld
    for bad in ("<", ">", "&", " ", " "):
        assert bad not in text
    assert "\\u003c" in text and "\\u003e" in text and "\\u0026" in text
    data = json.loads(text)
    assert data["mainEntity"][0]["name"] == question
    assert data["mainEntity"][0]["acceptedAnswer"]["text"] == answer


@pytest.mark.parametrize("payload", ["</ script>", "<!- x", "</"])
def test_half_tags_are_blocked_conservatively(payload):
    answer = f"Đáp {payload}."
    assert _build([(Q1, answer)], article=ARTICLE + answer).blocked


def test_to_json_ld_escapes_even_if_model_built_directly():
    # Khuôn dựng tay (bỏ qua bộ kiểm) vẫn không thể đóng thẻ script khi xuất.
    page = FAQPage.model_validate(
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": "</script><script>alert(1)</script>",
                    "acceptedAnswer": {"@type": "Answer", "text": "x y<!--"},
                }
            ],
        }
    )
    text = to_json_ld(page)
    assert "</" not in text and "<" not in text and " " not in text
    data = json.loads(text)
    assert data["mainEntity"][0]["name"] == "</script><script>alert(1)</script>"
    assert data["mainEntity"][0]["acceptedAnswer"]["text"] == "x y<!--"


# ------------------------------------------------------------------ loại schema


@pytest.mark.parametrize("schema_type", sorted(SITE_OWNED_TYPES))
def test_site_owned_types_refused(schema_type):
    issue = check_schema_type(schema_type)
    assert issue is not None and issue.level is Level.BLOCK
    assert "Site đã tự xuất" in issue.message


@pytest.mark.parametrize("schema_type", sorted(FORBIDDEN_TYPES))
def test_howto_refused(schema_type):
    issue = check_schema_type(schema_type)
    assert issue is not None and issue.level is Level.BLOCK


@pytest.mark.parametrize("schema_type", ["Recipe", "", None, 5, "Product"])
def test_unknown_types_refused(schema_type):
    assert check_schema_type(schema_type) is not None


def test_faqpage_allowed():
    assert check_schema_type("FAQPage") is None


def _data(**overrides):
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": Q1, "acceptedAnswer": {"@type": "Answer", "text": A1}}
        ],
    }
    data.update(overrides)
    return data


@pytest.mark.parametrize(
    "schema_type", ["HowTo", "Article", "LocalBusiness", ["FAQPage", "HowTo"], ["FAQPage"]]
)
def test_validate_rejects_bad_top_type(schema_type):
    issues = validate_faq_page(_data(**{"@type": schema_type}), article_text=ARTICLE)
    assert _blocked(issues)


def test_validate_rejects_howto_nested():
    data = _data()
    data["mainEntity"][0]["@type"] = "HowTo"
    assert _blocked(validate_faq_page(data, article_text=ARTICLE))
    data = _data()
    data["mainEntity"][0]["acceptedAnswer"]["@type"] = "Question"
    assert _blocked(validate_faq_page(data, article_text=ARTICLE))


@pytest.mark.parametrize(
    "context", ["http://schema.org", "https://schema.org/", "https://evil.example", None, ""]
)
def test_validate_rejects_bad_context(context):
    issues = validate_faq_page(_data(**{"@context": context}), article_text=ARTICLE)
    assert "@context phải đúng" in _messages(issues)


def test_validate_rejects_extra_keys():
    issues = validate_faq_page(_data(author="x"), article_text=ARTICLE)
    assert _blocked(issues)
    data = _data()
    data["mainEntity"][0]["acceptedAnswer"]["url"] = "https://evil.example"
    assert _blocked(validate_faq_page(data, article_text=ARTICLE))


@pytest.mark.parametrize("entities", [[], None, "abc", [1], [{"@type": "Question"}]])
def test_validate_rejects_bad_main_entity(entities):
    assert _blocked(validate_faq_page(_data(mainEntity=entities), article_text=ARTICLE))


def test_validate_rejects_non_dict():
    for data in (None, [], "x", 1):
        assert _blocked(validate_faq_page(data, article_text=ARTICLE))


def test_empty_question_or_answer_blocked():
    assert _build([("   ", A1)]).blocked
    assert _build([(Q1, "​")]).blocked
    assert _build([]).blocked
    assert _build([(Q1,)]).blocked
    assert _build([(Q1, None)]).blocked


# ------------------------------------------------------------------ giới hạn


def test_too_many_questions_blocked():
    pairs = [(f"Câu {i}?", f"Đáp {i}.") for i in range(MAX_QUESTIONS + 1)]
    article = "\n".join(f"{q}\n{a}" for q, a in pairs)
    result = _build(pairs, article=article)
    assert result.blocked
    assert f"Tối đa {MAX_QUESTIONS}" in _messages(result.issues)
    ok = _build(pairs[:MAX_QUESTIONS], article=article)
    assert not ok.blocked, _messages(ok.issues)


def test_too_long_answer_blocked():
    answer = "a" * (MAX_ANSWER_LENGTH + 1)
    result = _build([(Q1, answer)], article=ARTICLE + answer)
    assert result.blocked
    assert "dài quá" in _messages(result.issues)


def test_warnings_do_not_block():
    article = ARTICLE + "\nCửa sắt bền bao lâu\nKhá bền.\n"
    result = _build([("Cửa sắt bền bao lâu", "Khá bền."), (Q1, A1), (Q1, A1)], article=article)
    assert not result.blocked
    levels = {issue.level for issue in result.issues}
    assert levels == {Level.WARN}
    assert "dấu hỏi" in _messages(result.issues)
    assert "trùng" in _messages(result.issues)
    assert result.json_ld is not None


# ------------------------------------------------------------------ URL


@pytest.mark.parametrize(
    "url",
    [
        SITE + "/bai/",
        "https://SuaChuaCuaSat.com/bai",
        "https://suachuacuasat.com./bai",
        "https://suachuacuasat.com:443/bai",
    ],
)
def test_url_same_domain_ok(url):
    assert check_url(url, SITE) == []


@pytest.mark.parametrize(
    "url",
    [
        "http://suachuacuasat.com/bai",
        "https://evil.example/bai",
        "https://suachuacuasat.com.evil.example/bai",
        "https://www.suachuacuasat.com/bai",
        "https://suachuacuasat.com@evil.example/bai",
        "https://user:pw@suachuacuasat.com/bai",
        "https://suachuacuasat.com:8080/bai",
        "javascript:alert(1)",
        "//suachuacuasat.com/bai",
        "https://suachuacuasat.com/b ai",
        "https://suachuacuasat.com/\x00",
        "",
        None,
        "https://suachuacuasat.com/" + "a" * 3000,
    ],
)
def test_url_bad_blocked(url):
    issues = check_url(url, SITE)
    assert _blocked(issues)


def test_url_without_site_url_blocked():
    assert "WORDPRESS_URL" in _messages(check_url(SITE + "/bai", None))
    assert _blocked(check_url(SITE + "/bai", ""))


def test_build_with_foreign_url_blocked():
    result = _build([(Q1, A1)], page_url="https://evil.example/bai")
    assert result.blocked
    assert "không cùng tên miền" in _messages(result.issues)


# ------------------------------------------------------------------ chuẩn hóa


def test_normalize_text():
    assert normalize_text("  a\n\tb c​ d  ") == "a b c d"
    assert normalize_text("é") == "é"

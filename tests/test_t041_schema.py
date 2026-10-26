"""T-041 (Thợ Máy): schema FAQPage trước khi bước SEO hiện ``json_ld``.

- Lá Chắn T-038 điều kiện 1 (SL-T038-1): ký tự Cs, Co, Cn bị Chặn như ký tự điều khiển.
- Lá Chắn T-038 điều kiện 2 (SL-T038-2 và lỗi 3): bỏ Markdown nội dòng ở cả bài lẫn câu trả lời;
  link chỉ giữ chữ (``javascript:`` không vào JSON-LD), ảnh chỉ giữ alt; không đổi sang HTML; chữ
  sau khi bỏ dấu vẫn qua bộ chặn thẻ và ``to_json_ld``.
- ``find_faq``/``build_article_faq``: tìm mục Hỏi đáp trong bài (dạng chữ như trên trang Soạn bài).

Không gọi mạng.
"""

from __future__ import annotations

import json

import pytest
from timing import assert_scales_linearly

from seo_app.content.models import Section
from seo_app.onpage.schema import (
    MAX_QUESTIONS,
    MSG_NO_FAQ,
    Level,
    article_markdown,
    build_article_faq,
    build_faq_page,
    find_faq,
    plain_text,
    validate_faq_page,
)
from seo_app.sanitize import clean_ai_text, escape_link_syntax

SITE = "https://suachuacuasat.com"
Q = "Cửa sắt sơn tĩnh điện dùng được bao lâu?"
A = "Thường 8–10 năm nếu lau bụi mỗi tháng và sơn dặm chỗ trầy."


def _article(q: str = Q, a: str = A) -> str:
    return f"# Bài\n\nMở bài.\n\n## Hỏi đáp\n\n### {q}\n\n{a}\n"


def _texts(result) -> list[str]:
    data = json.loads(result.json_ld)
    return [t for e in data["mainEntity"] for t in (e["name"], e["acceptedAnswer"]["text"])]


def _assert_script_safe(json_ld: str) -> None:
    for bad in ("<", ">", "&", " ", " "):
        assert bad not in json_ld
    assert "</script" not in json_ld.lower()


# ============================================================ điều kiện 1: Cs, Co, Cn


@pytest.mark.parametrize("odd", ["\ud800", "\udfff", "", "\U000f0000", "͸", "\x00"])
@pytest.mark.parametrize("where", ["q", "a"])
def test_odd_chars_blocked(odd, where):
    q = Q.replace("bao lâu", f"bao{odd} lâu") if where == "q" else Q
    a = A.replace("8–10", f"8{odd}–10") if where == "a" else A
    result = build_faq_page([(q, a)], article_text=_article(q, a), site_url=SITE)
    assert result.blocked and result.json_ld is None
    messages = " ".join(issue.message for issue in result.issues)
    assert "ký tự lạ" in messages and odd not in messages


def test_validate_blocks_odd_chars_in_data():
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": Q, "acceptedAnswer": {"@type": "Answer", "text": A}}
        ],
    }
    assert validate_faq_page(data, article_text=_article()) == []
    data["mainEntity"][0]["acceptedAnswer"]["text"] = A + ""
    issues = validate_faq_page(data, article_text=_article(a=A + ""))
    assert issues and all(issue.level is Level.BLOCK for issue in issues)


# ============================================================ điều kiện 2: bỏ Markdown


@pytest.mark.parametrize(
    ("markdown", "plain"),
    [
        ("Thường **8–10 năm** nếu lau bụi", "Thường 8–10 năm nếu lau bụi"),
        ("Thường __8–10 năm__ nếu", "Thường 8–10 năm nếu"),
        ("Thường *8–10 năm* nếu _lau_ bụi", "Thường 8–10 năm nếu lau bụi"),
        ("Thường `8–10 năm` nếu", "Thường 8–10 năm nếu"),
        ("Thường ~~5~~ 8–10 năm", "Thường 5 8–10 năm"),
        ("Xem [bảng giá](javascript:alert(1)) nhé", "Xem bảng giá nhé"),
        ("Xem [bảng giá](https://e.vil/x 'tiêu đề') nhé", "Xem bảng giá nhé"),
        ("Ảnh ![cửa gỉ](https://tên-miền-lạ.vn/a.png) đây", "Ảnh cửa gỉ đây"),
        ("### Câu hỏi? ###", "Câu hỏi?"),
        ("- **Có.** Được\n1. Bước một\n> Trích", "Có. Được Bước một Trích"),
        ("5 * 3 = 15, ten_file, a ~ b", "5 * 3 = 15, ten_file, a ~ b"),
        ("Cửa 2*3m, khung 1_5", "Cửa 2*3m, khung 1_5"),  # dấu lẻ, không có cặp: là chữ
        ("**Đậm vắt\nqua dòng**", "Đậm vắt qua dòng"),
        ("**Mở ở đoạn này\n\nđóng ở đoạn kia**", "**Mở ở đoạn này đóng ở đoạn kia**"),
        ("Dấu \\*sao\\* thật", "Dấu *sao* thật"),
        ("[cần bổ sung: giá]", "[cần bổ sung: giá]"),
        ("Đoạn một.\n\nĐoạn   hai.", "Đoạn một. Đoạn hai."),
    ],
)
def test_plain_text(markdown, plain):
    assert plain_text(markdown) == plain


def test_plain_text_of_app_text_drops_escapes_and_addresses():
    """Chữ trong trang Soạn bài đã qua ``clean_ai_text``/``escape_link_syntax`` (``]\\(``, ký tự
    ngắt địa chỉ): bỏ dấu ``\\`` app thêm, link sửa tay vẫn chỉ giữ chữ."""
    typed = escape_link_syntax("Xem [bảng giá](javascript:alert(1)) và www.vi-du.vn nhé.")
    assert "]\\(" in typed and "​" in typed
    assert plain_text(typed) == "Xem bảng giá và www.vi-du.vn nhé."


@pytest.mark.parametrize(
    "markdown",
    [
        "Thường **8–10 năm** nếu lau bụi mỗi tháng và sơn dặm chỗ trầy.",
        "Thường *8–10 năm* nếu lau bụi mỗi tháng và sơn dặm chỗ trầy.",
        "Thường `8–10 năm` nếu lau bụi mỗi tháng và sơn dặm chỗ trầy.",
        "Thường 8–10 năm nếu lau bụi mỗi tháng và [sơn dặm](javascript:alert(1)) chỗ trầy.",
        "Thường 8–10 năm nếu lau bụi mỗi tháng và [sơn dặm](https://e.vil/x) chỗ trầy.",
        "Thường 8–10 năm nếu lau bụi ![](https://tên-miền-lạ.vn/a.png)mỗi tháng và sơn dặm "
        "chỗ trầy.",
    ],
)
@pytest.mark.parametrize("answer_side", ["plain", "markdown"])
def test_markdown_both_sides_matches_and_json_is_plain(markdown, answer_side):
    answer = A if answer_side == "plain" else markdown
    result = build_faq_page([(Q, answer)], article_text=_article(a=markdown), site_url=SITE)
    assert not result.blocked, result.issues
    text = json.loads(result.json_ld)["mainEntity"][0]["acceptedAnswer"]["text"]
    assert text == A
    for mark in ("*", "`", "](", "https://"):
        assert mark not in text
    for address in ("javascript", "e.vil", "tên-miền-lạ"):
        assert address not in result.json_ld


@pytest.mark.parametrize(
    "answer",
    [
        "<**script**>alert(1)</**script**>",
        "<`script`>alert(1)<`/script`>",
        "Trả lời </**script**><**script**>x",
        "[<script>](https://e.vil) chữ",
        "![<img src=x onerror=alert(1)>](https://e.vil/a.png)",
        "**<b>đậm</b>**",
    ],
)
def test_html_hidden_between_markdown_marks_is_blocked(answer):
    result = build_faq_page([(Q, answer)], article_text=_article(a=answer), site_url=SITE)
    assert result.blocked and result.json_ld is None
    assert any("thẻ HTML" in issue.message for issue in result.issues)


def test_markdown_never_becomes_html():
    result = build_faq_page(
        [(Q, "Có. Xem [mục này](https://suachuacuasat.com/x) và **lưu ý**.")],
        article_text=_article(a="Có. Xem [mục này](https://suachuacuasat.com/x) và **lưu ý**."),
        site_url=SITE,
    )
    assert not result.blocked
    _assert_script_safe(result.json_ld)
    assert _texts(result)[1] == "Có. Xem mục này và lưu ý."
    assert "href" not in result.json_ld and "<a" not in result.json_ld


@pytest.mark.parametrize("answer", ["` `", "`` ` ``", "[](https://e.vil)"])
def test_only_marks_answer_is_empty(answer):
    result = build_faq_page([(Q, answer)], article_text=_article(a=answer), site_url=SITE)
    assert result.blocked
    assert any("để trống" in issue.message for issue in result.issues)


def test_spaced_stars_are_text_not_marks():
    """«** **» (dấu sao có khoảng trắng hai bên) Markdown hiện nguyên chữ: giữ như trên trang."""
    assert plain_text("Điểm ** ** lạ") == "Điểm ** ** lạ"


def test_data_with_markdown_marks_does_not_validate():
    """``validate_faq_page`` nhận dict có sẵn: chữ còn dấu Markdown không khớp chữ người đọc thấy,
    nên JSON-LD mang dấu Markdown không qua được bộ kiểm."""
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": Q,
                "acceptedAnswer": {"@type": "Answer", "text": "Thường **8–10 năm** nếu"},
            }
        ],
    }
    issues = validate_faq_page(data, article_text=_article(a="Thường **8–10 năm** nếu lau"))
    assert any("nguyên văn" in issue.message for issue in issues)


def test_plain_text_is_linear():
    assert_scales_linearly(
        plain_text, lambda k: "**a** `b` [c](d) _e_ \\* ~~f~~\n" * (k * 1500), label="plain_text"
    )


def test_messages_never_echo_article():
    secret = "MA-BI-MAT-T041"
    result = build_faq_page([(Q, f"<**b**>{secret}")], article_text=_article(), site_url=SITE)
    assert result.blocked
    assert all(secret not in issue.message for issue in result.issues)


# ============================================================ mục Hỏi đáp trong bài


def _parts(faq_body: str, heading: str = "Câu hỏi thường gặp") -> list[Section]:
    return [
        Section(heading="Mở bài", body="Cửa sắt bị xệ thường do **bản lề** mòn."),
        Section(heading="Nguyên nhân", body="Bản lề mòn, trụ lún.\n\n### Có cần thay cả cửa?\n"),
        Section(heading=heading, body=faq_body),
    ]


FAQ_BODY = """### Cửa sắt sơn tĩnh điện dùng được bao lâu?

Thường **8–10 năm** nếu lau bụi mỗi tháng.

**Có cần tháo cánh khi sơn lại không?** Không, thợ sơn tại chỗ.
Mất khoảng một ngày.

Có bảo hành không?

Có, bảo hành 12 tháng.

- Có giấy tờ không?

### Câu hỏi không có trả lời?
"""


def test_find_faq_formats():
    assert find_faq(_parts(FAQ_BODY)) == [
        ("Cửa sắt sơn tĩnh điện dùng được bao lâu?", "Thường **8–10 năm** nếu lau bụi mỗi tháng."),
        ("Có cần tháo cánh khi sơn lại không?", "Không, thợ sơn tại chỗ.\nMất khoảng một ngày."),
        ("Có bảo hành không?", "Có, bảo hành 12 tháng.\n\n- Có giấy tờ không?"),
    ]


@pytest.mark.parametrize(
    "heading",
    ["Hỏi đáp", "Hỏi - đáp", "HỎI VÀ ĐÁP", "Câu hỏi thường gặp", "Thắc mắc hay gặp", "FAQ",
     "Hoi dap nhanh"],
)  # fmt: skip
def test_faq_heading_variants(heading):
    assert len(find_faq(_parts(FAQ_BODY, heading))) == 3


@pytest.mark.parametrize("heading", ["Cách xử lý", "Hỏi thợ trước khi đáp ứng", "Lưu ý"])
def test_other_headings_are_not_faq(heading):
    assert find_faq(_parts(FAQ_BODY, heading)) == []


def test_intro_is_never_faq():
    parts = [Section(heading="Hỏi đáp", body=FAQ_BODY)]
    assert find_faq(parts) == []


def test_headings_without_blank_lines_still_split():
    body = "### Câu một?\nTrả lời một.\n### Câu hai?\nTrả lời hai."
    assert find_faq(_parts(body)) == [("Câu một?", "Trả lời một."), ("Câu hai?", "Trả lời hai.")]


def test_build_article_faq_from_app_text():
    """Chữ trong trang Soạn bài đã qua ``clean_ai_text`` (link bị bỏ, địa chỉ trần có ký tự ngắt):
    vẫn dựng được, JSON-LD là chữ thuần, an toàn trong thẻ script."""
    parts = [
        Section(heading=p.heading, body=clean_ai_text(p.body))
        for p in _parts(FAQ_BODY + "\n### Xem ở đâu?\n\nTại [trang này](https://e.vil) hoặc "
                        "www.suachuacuasat.com nhé.\n")
    ]  # fmt: skip
    result = build_article_faq(parts, site_url=SITE)
    assert not result.blocked, result.issues
    _assert_script_safe(result.json_ld)
    texts = _texts(result)
    assert texts[0] == "Cửa sắt sơn tĩnh điện dùng được bao lâu?"
    assert texts[1] == "Thường 8–10 năm nếu lau bụi mỗi tháng."
    assert texts[-1] == "Tại trang này hoặc www.suachuacuasat.com nhé."
    assert "e.vil" not in result.json_ld and "​" not in result.json_ld


def test_build_article_faq_without_faq_section():
    result = build_article_faq(_parts(FAQ_BODY, "Cách xử lý"))
    assert result.blocked and result.json_ld is None
    assert [issue.message for issue in result.issues] == [MSG_NO_FAQ]


def test_build_article_faq_too_many_questions():
    body = "\n\n".join(f"### Câu {i}?\n\nTrả lời {i}." for i in range(MAX_QUESTIONS + 5))
    assert len(find_faq(_parts(body))) == MAX_QUESTIONS + 1
    result = build_article_faq(_parts(body))
    assert result.blocked
    assert any(f"Tối đa {MAX_QUESTIONS}" in issue.message for issue in result.issues)


def test_subheading_without_question_mark_ends_the_answer():
    """SL-T041-5: tiêu đề con không phải câu hỏi không thành câu hỏi, và kết thúc câu trả lời
    trước đó (chữ của mục khác không lẫn vào trả lời)."""
    body = (
        "### Cửa cuốn kêu to có sao không?\n\nThường do ray khô dầu.\n\n"
        "### Lưu ý khi tự tra dầu\n\nNgắt điện trước khi làm.\n\n"
        "**Bao lâu tra dầu một lần?** Ba tháng một lần."
    )
    assert find_faq(_parts(body)) == [
        ("Cửa cuốn kêu to có sao không?", "Thường do ray khô dầu."),
        ("Bao lâu tra dầu một lần?", "Ba tháng một lần."),
    ]


@pytest.mark.parametrize(
    "answer",
    [
        "Gõ `[x](javascript:alert(1))` vào ô.",
        "Gõ \\[x\\](javascript:alert(1)) vào ô.",  # ngoặc đã escape: Markdown hiện thành chữ
        "Gõ `![ảnh](https://e.vil/a.png)` vào ô.",
    ],
)
def test_link_inside_code_or_escaped_keeps_only_text(answer):
    """SL-T041-6: link nằm trong đoạn mã hay viết bằng ngoặc đã escape cũng chỉ giữ chữ."""
    parts = [
        Section(heading="Mở bài", body="x"),
        Section(heading="Hỏi đáp", body=f"### {Q}\n\n{answer}"),
    ]
    result = build_article_faq(parts, site_url=SITE)
    assert not result.blocked, result.issues
    for address in ("javascript", "e.vil", "](", "https://"):
        assert address not in _texts(result)[1]


def test_too_long_article_is_blocked_before_searching(monkeypatch):
    """Góp ý G2: bài dài quá ``MAX_ARTICLE_LENGTH`` bị Chặn trước khi tìm mục Hỏi đáp."""
    import seo_app.onpage.schema as schema

    def no_search(parts):
        raise AssertionError("không được tìm mục Hỏi đáp trong bài quá dài")

    monkeypatch.setattr(schema, "find_faq", no_search)
    parts = _parts("### Câu?\n\nTrả lời." + " chữ" * schema.MAX_ARTICLE_LENGTH)
    result = build_article_faq(parts)
    assert result.blocked and [i.message for i in result.issues] == [schema.MSG_ARTICLE_TOO_LONG]


def test_missing_material_in_answer_is_a_warning():
    """Góp ý G3: trả lời còn «[cần bổ sung: …]» vẫn dựng (xem trước) nhưng có Cảnh báo."""
    body = "### Giá thay ray bao nhiêu?\n\nTùy loại ray, [cần bổ sung: giá thay ray]."
    result = build_article_faq(_parts(body), site_url=SITE)
    assert not result.blocked and result.json_ld is not None
    assert [(i.level, i.message) for i in result.issues] == [
        (Level.WARN, "Trả lời 1: còn chỗ «[cần bổ sung: …]» chưa điền.")
    ]


def test_article_markdown_has_every_part():
    text = article_markdown(_parts(FAQ_BODY))
    assert "Mở bài" in text and "Câu hỏi thường gặp" in text and "Có bảo hành không?" in text

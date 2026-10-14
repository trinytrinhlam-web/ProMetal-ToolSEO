"""Soi Lỗi kiểm thử lượt 4: T-008 lần 3 (escape cú pháp link) và T-012 (ô sửa bỏ/thêm escape).

Báo cáo: docs/team/reports/T-008r3-012-soi-loi.md. Test ``xfail(strict=True)`` = lỗi THẬT còn
lách được, đánh số khớp với báo cáo (R4-…). Khi sửa xong, test báo XPASS và phải gỡ ``xfail``.

Thước đo "không còn tạo được link": ``escape_link_syntax(out) == out``. Hàm này thêm "\\" vào
MỌI chỗ "](", "][" và "]:" đầu dòng còn hiệu lực, nên nếu nó không đổi gì thì không còn chỗ nào.
Kết quả này đã được đối chiếu bằng bộ hiển thị Markdown thật (markdown-it-py và micromark + GFM,
chạy tạm ngoài dự án, xem báo cáo). Không gọi mạng, không cần .env.
"""

from __future__ import annotations

import random
import re

import pytest
from fake_ai import DRAFT, FakeProvider
from fake_ai import SCORES as DRAFT_SCORES
from streamlit.testing.v1 import AppTest

from seo_app.ai import registry as ai_registry
from seo_app.auth import hash_password
from seo_app.content.models import Draft, Flag, Review, Section
from seo_app.content.workflow import apply_flag, clean_ai_line, clean_flags, clean_review
from seo_app.sanitize import clean_ai_text, escape_link_syntax, unescape_link_syntax

E = "https://evil.example"
# "](" hoặc "][" mà "]" không bị escape (đứng sau một số chẵn dấu "\\").
LIVE_BRACKET = re.compile(r"(?<!\\)(?:\\\\)*\][(\[]")


def no_link_left(text: str) -> bool:
    return escape_link_syntax(text) == text and not LIVE_BRACKET.search(text)


# Mỗi dòng: một cách viết link (đã có link thật khi hiển thị nếu không lọc).
ATTACKS = [
    # nội dòng, ảnh, tiêu đề link, ngoặc nhọn
    f"[a]({E})",
    f"![a]({E})",
    f'[a]({E} "t")',
    f"[a](<{E}>)",
    f"# [a]({E})",
    # tham chiếu: đầy đủ, rút gọn, trơn
    f"[a][r]\n\n[r]: {E}",
    f"[a][]\n\n[a]: {E}",
    f"[a]\n\n[a]: {E}",
    f"[a]:{E}\n\n[a]",
    f"[a]: <{E}>\n\n[a]",
    # xuống dòng kiểu Windows / Mac cũ
    f"[a]\r\n\r\n[a]: {E}",
    f"[a]\r\r[a]: {E}",
    f"x\r\r[a]: {E}\r\r[a]",
    # khai báo nằm trong khối: thụt lề, trích dẫn, danh sách, lồng nhiều tầng
    f"   [a]: {E}\n\n[a]",
    f"\t[a]: {E}\n\n[a]",
    f"> [a]: {E}\n\n[a]",
    f"- [a]: {E}\n\n[a]",
    f"+ [a]: {E}\n\n[a]",
    f"* [a]: {E}\n\n[a]",
    f"1. [a]: {E}\n\n[a]",
    f"10) [a]: {E}\n\n[a]",
    f"> > - 1. [a]: {E}\n\n[a]",
    f"\u3000[a]: {E}\n\n[a]",
    # nhãn nhiều dòng, nhãn có "]" escape, chú thích cuối trang
    f"[a\nb]: {E}\n\n[a b]",
    f"[a\\]b]: {E}\n\n[a\\]b]",
    f"[^1]: {E}\n\nx[^1]",
    # "\\" đã escape sẵn, ngoặc lồng, nhiều "]"
    f"[a\\\\]({E})",
    f"\\\\[a\\\\]({E})",
    f"[a]\\\\({E})",
    f"[a]]({E})",
    f"[[a]]({E})",
    f"[a][b][c]({E})",
    f"[a]\\[r]\n\n[r]: {E}",
    # chữ "\\(" AI viết sẵn: hiện như "](" trong ô sửa, lưu lại phải escape
    f"[a]\\({E})",
    # code span không làm mất escape
    f"`x`[a]({E})",
    f"[`]`]({E})",
    f"[a`]`({E})",
    # ký tự lạ ngay sau "]"
    f"[a]\u00a0({E})",
    f"[a]\u200b({E})",
    f"[a]\ufeff({E})",
    f"[a]\x0b({E})",
    f"[a]\u0085({E})",
    f"x\u2028[a]: {E}\n\n[a]",
    # ký tự "giống" ngoặc (Unicode) và thực thể HTML: Markdown không coi là ngoặc
    f"[a］({E})",
    f"[a]（{E}）",
    f"&#91;a&#93;({E})",
    f"[a]&#40;{E})",
    # chuỗi rất dài
    "[a]" * 3000 + f"({E})",
    "[" * 5000 + f"a]({E})",
    "](" * 5000,
]


@pytest.mark.parametrize("text", ATTACKS)
def test_clean_ai_text_leaves_no_link(text):
    assert no_link_left(clean_ai_text(text)), repr(clean_ai_text(text))[:300]


@pytest.mark.parametrize("text", ATTACKS)
def test_clean_ai_line_leaves_no_link(text):
    out = clean_ai_line(text)
    assert "\n" not in out and "\r" not in out
    assert no_link_left(out), repr(out)[:300]


@pytest.mark.parametrize("text", ATTACKS)
@pytest.mark.parametrize("template", ["> {}", "- {}", "## {}", "**Gợi ý:** {}", ":gray[{}]"])
def test_cleaned_text_inside_display_templates_leaves_no_link(text, template):
    # Cách write.py ghép chữ AI vào Markdown: chữ đã lọc không ghép với khung ra link.
    shown = template.format(clean_ai_text(text))
    assert not LIVE_BRACKET.search(shown), repr(shown)[:300]


@pytest.mark.parametrize("text", ATTACKS)
def test_escape_is_idempotent_and_clean_is_stable(text):
    once = clean_ai_text(text)
    assert escape_link_syntax(once) == once
    assert clean_ai_text(once) == once


# ------------------------------------------------------------ apply_flag: ghép câu không ra link


@pytest.mark.parametrize(
    ("body", "sentence", "replacement"),
    [
        (f"[Gọi thợ] Câu thừa.({E})", "Câu thừa.", ""),
        (f"[Gọi thợ] Câu thừa. [r]\n\n[r]: {E}", "Câu thừa. ", ""),
        (f"Đoạn A.\nCâu thừa.[r]: {E}\n\n[r]", "Đoạn A.\nCâu thừa.", ""),
        (f"[Gọi thợ]X({E})", "X", ""),
        (f"[Gọi thợ]X({E})", "X", "]["),
        (f"[Gọi thợ]X({E})", "X", "\\"),
        # bỏ dấu "\\" (câu = "\\"): mọi escape bị bỏ, kết quả phải escape lại
        (clean_ai_text(f"[a]({E}) và [b][c]\n\n[c]: {E}"), "\\", ""),
        (f"[cần bổ sung: giá]({E})", "\\", "x"),
        (f"[cần bổ sung: giá]({E})", "]\\", "]"),
        (f"Mục [a][b]\n\n[b]: {E}", "]\\", "]"),
    ],
)
def test_apply_flag_cannot_join_a_link(body, sentence, replacement):
    body = clean_ai_text(body)
    assert sentence in body, repr(body)
    assert no_link_left(apply_flag(body, sentence, replacement))


# ------------------------------------------------------------ T-012: ô sửa → lưu


@pytest.mark.parametrize("text", ATTACKS)
def test_edit_box_round_trip_keeps_text_and_stays_safe(text):
    stored = clean_ai_text(text)
    shown = unescape_link_syntax(stored)  # chữ trong ô «Sửa trực tiếp»
    assert escape_link_syntax(shown) == stored  # bấm Lưu không sửa gì: y như cũ
    assert no_link_left(escape_link_syntax(shown))


@pytest.mark.parametrize("typed", [*ATTACKS, "[a](b)\r\n[c]: d", "Gõ tay [x](y) và [z]: w"])
def test_whatever_user_types_is_saved_without_link(typed):
    # save_manual / current_outline: escape_link_syntax(chữ trong ô).
    saved = escape_link_syntax(typed.replace("\r\n", "\n"))
    assert no_link_left(saved)


def test_unescape_then_escape_is_identity_on_random_attack_text():
    rng = random.Random(4)
    tokens = ["[", "]", "(", ")", "\\", ":", "\n", " ", "!", "`", "a", "-", "1.", ">", "\t", E]
    for _ in range(4000):
        raw = "".join(rng.choice(tokens) for _ in range(rng.randint(1, 20)))
        stored = clean_ai_text(raw)
        assert no_link_left(stored), repr(raw)
        assert escape_link_syntax(unescape_link_syntax(stored)) == stored, repr(raw)
        joined = apply_flag(stored, rng.choice(tokens), rng.choice(["", "x", "[", "]", "\\"]))
        assert no_link_left(joined), repr(raw)


# ------------------------------------------------------------ chữ thường không hỏng


@pytest.mark.parametrize(
    "text",
    [
        "Cửa cuốn khe thoáng (loại tấm liền) giá khoảng [cần bổ sung: giá] mỗi m².",
        "[Lưu ý]: lò xo xoắn rất căng.\n- [Mẹo]: tra dầu ray 3 tháng/lần.\n> [Chú ý]: tắt CB.",
        "Bảng [1][2] và mục [3]: xem bên dưới (đơn vị: triệu đồng).",
        "- [ ] Kiểm tra lò xo\n- [x] Tra dầu ray",
        "Ngoặc tròn (chú thích) và ngoặc vuông [chú thích] riêng rẽ.",
        "Đường dẫn Windows C:\\Anh\\cong-inox.jpg vẫn giữ.",
    ],
)
def test_normal_text_only_gains_invisible_backslashes(text):
    out = clean_ai_text(text)
    assert unescape_link_syntax(out) == text
    added = len(out) - len(text)
    assert added >= 0 and out.replace("]\\", "]") == text.replace("]\\", "]")
    assert no_link_left(out)


# ================================== R4-1 · Trung bình · câu AI chỉ ra hiện bằng "> {câu}"

PASSWORD = "mat-khau-thu-123"
# Trong bài: "[thợ]:" nằm giữa dòng nên không phải khai báo link, không bị escape (đúng).
EVIL_BODY = f"Gọi ngay [thợ]: {E}\n[thợ] nhé."
# Câu AI "chỉ ra" là một đoạn con của bài, bắt đầu bằng "[thợ]:". write.py hiện câu này bằng
# st.markdown(f"> {câu}"): "[thợ]:" thành đầu dòng → khai báo link, "[thợ]" thành link thật.
EVIL_SENTENCE = f"[thợ]: {E}\n[thợ] nhé."


def test_r4_1_flag_sentence_is_a_substring_of_safe_body():
    body = clean_ai_text(EVIL_BODY)
    assert no_link_left(body)  # bài thì an toàn
    review = clean_review(
        Review(
            scores=DRAFT_SCORES,
            flags=[Flag(section=0, sentence=EVIL_SENTENCE, reason="r", replacement="")],
            summary="",
        )
    )
    flags = clean_flags([Section(heading="h", body=body)], review.flags)
    assert flags and flags[0].sentence == EVIL_SENTENCE  # câu được nhận vì có trong bài


class _EvilProvider(FakeProvider):
    def generate(self, task, *, system, prompt, schema):
        if schema is Draft:
            self.calls.append((task.name, system, prompt))
            return Draft(
                title=DRAFT.title,
                intro=EVIL_BODY,
                sections=DRAFT.sections,
            )
        if schema is Review:
            self.calls.append((task.name, system, prompt))
            flag = Flag(section=0, sentence=EVIL_SENTENCE, reason="Nghe máy móc", replacement="")
            return Review(scores=DRAFT_SCORES, flags=[flag], summary="Khá ổn.")
        return super().generate(task, system=system, prompt=prompt, schema=schema)


@pytest.mark.xfail(
    strict=True,
    reason="R4-1 (Trung bình): câu AI chỉ ra (flag.sentence) chỉ cần là một đoạn con của bài. "
    "write.py:506 hiện nó bằng st.markdown(f'> {sentence}') mà không escape lại, nên '[nhãn]:' "
    "giữa dòng trong bài thành đầu dòng → khai báo link + '[nhãn]' thành link bấm được.",
)
def test_r4_1_flag_sentence_shown_in_review_has_no_link(project_root, monkeypatch):
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    monkeypatch.setenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    provider = _EvilProvider()
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: provider)
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/write.py").run()
    at.text_input(key="keyword").input("sửa cửa cuốn").run()
    for label in ("🔎 Phân tích từ khóa", "Tiếp: tạo dàn ý →", "✅ Duyệt dàn ý, viết toàn bài →"):
        next(b for b in at.button if b.label == label).click().run()
        assert not at.exception, at.exception
    quoted = [m.value for m in at.markdown if m.value.startswith("> ")]
    assert quoted, "không thấy câu AI chỉ ra trên trang"
    for value in quoted:
        assert no_link_left(value), value


# ============================ R4-4 · Thấp · "[chữ](có dấu cách)" không phải link vẫn bị cắt


@pytest.mark.xfail(
    strict=True,
    reason="R4-4 (Thấp): '](…có dấu cách…)' không phải link theo CommonMark nhưng "
    "strip_markdown_links vẫn bỏ phần '(…)' (R3-4 chỉ sửa cho '[cần bổ sung: …]'). Nay "
    "escape_link_syntax đã chặn link, bước bỏ này chỉ làm mất chữ của người đọc.",
)
@pytest.mark.parametrize(
    "text",
    ["Khách hỏi: «Cửa kêu [rè rè](sau mưa) là sao?»", "Xem [Bảng 1](đơn vị triệu đồng) dưới."],
)
def test_r4_4_bracket_then_parenthesis_with_spaces_keeps_text(text):
    assert unescape_link_syntax(clean_ai_text(text)) == text


# ================================== R4-2 · Thấp · escape_link_syntax không tự hiểu "\r"


@pytest.mark.xfail(
    strict=True,
    reason="R4-2 (Thấp): escape_link_syntax chỉ coi '\\n' là xuống dòng; '\\r' đứng riêng "
    "(Markdown coi là xuống dòng) thì '[a]:' đầu dòng không bị escape. clean_ai_text đã đổi "
    "'\\r' trước, nhưng save_manual và apply_flag gọi escape_link_syntax trực tiếp "
    "(sanitize.py:210-257, write.py:208, workflow.py:157-159).",
)
@pytest.mark.parametrize("text", [f"a\r\r[a]: {E}\r\r[a]", f"Đoạn.\r\r> [a]: {E}\r\r[a]"])
def test_r4_2_escape_handles_lone_carriage_return(text):
    assert "]\\:" in escape_link_syntax(text)
    assert "]\\:" in apply_flag(text, "không-có", "x")


# ================================== R4-3 · Thấp · dấu "\" hiện ra trong đoạn code


@pytest.mark.xfail(
    strict=True,
    reason="R4-3 (Thấp): trong `code` Markdown không hiểu escape, nên '\\' thêm sau ']' hiện ra "
    "thành chữ: `a](b` → `a]\\(b`. Trong code cũng không thể có link nên không cần escape.",
)
@pytest.mark.parametrize("text", ["Dùng `arr]](x)` trong code.", "Mã `x][y` giữ nguyên."])
def test_r4_3_code_span_is_not_escaped(text):
    assert clean_ai_text(text) == text

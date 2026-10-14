"""Trường hợp xấu của Giai đoạn 2 phần 1: AI trả rỗng / sai khuôn / lỗi mạng, tiếng Việt,
HTML trong kết quả AI, viết lại một phần không đụng phần khác, file cấu hình viết sai.

Test ``xfail(strict=True)`` là lỗi thật, số lỗi khớp với ``docs/team/reports/T-002-soi-loi.md``.
"""

import unicodedata
from types import SimpleNamespace

import pytest
from fake_ai import DRAFT, OUTLINE, RESEARCH, FakeProvider
from streamlit.testing.v1 import AppTest

from seo_app.ai import AIError, AIRouter, TaskConfig, load_ai_config
from seo_app.ai import registry as ai_registry
from seo_app.ai.anthropic_provider import MAX_CONTINUATIONS, AnthropicProvider
from seo_app.auth import hash_password
from seo_app.config import Settings
from seo_app.content import ContentWriter, Section
from seo_app.content import prompts as content_prompts
from seo_app.content.models import (
    Competitor,
    Draft,
    Flag,
    Outline,
    Research,
    Review,
    Scores,
    SectionText,
)
from seo_app.content.rules import ContentRules, find_banned, find_missing, load_rules
from seo_app.content.workflow import apply_flag, clean_flags, draft_to_parts

TASKS = {
    name: TaskConfig(name=name, provider="anthropic", model="claude-opus-5-5")
    for name in ("research", "outline", "write", "rewrite", "review")
}
RULES = ContentRules(
    business_profile="- Tên thương hiệu: Pro-Metal",
    address="Xưng «chúng tôi»",
    tone="Thân thiện",
    banned=("Trong thời đại", "Có thể thấy rằng"),
    checklist=("Không bịa số liệu",),
)
XSS = '<img src="x" onerror="alert(1)">'
PASSWORD = "mat-khau-thu-123"


class ScriptedProvider(FakeProvider):
    """FakeProvider nhưng cho phép thay kết quả (hoặc lỗi) theo từng khuôn dữ liệu."""

    def __init__(self, **overrides):
        super().__init__()
        self.overrides = overrides  # tên khuôn -> giá trị hoặc Exception

    def generate(self, task, *, system, prompt, schema):
        value = self.overrides.get(schema.__name__)
        if value is None:
            return super().generate(task, system=system, prompt=prompt, schema=schema)
        self.calls.append((task.name, system, prompt))
        if isinstance(value, Exception):
            raise value
        return value


def make_writer(monkeypatch, provider) -> ContentWriter:
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: provider)
    return ContentWriter(AIRouter(TASKS, Settings()), RULES)


# ------------------------------------------------------------- AI lỗi mạng / sai khuôn


NETWORK = AIError("Không kết nối được tới Anthropic. Kiểm tra mạng Internet.")


@pytest.mark.parametrize(
    ("schema", "call"),
    [
        ("Research", lambda w: w.research("cửa sắt")),
        ("Outline", lambda w: w.outline("cửa sắt", RESEARCH, {})),
        ("Draft", lambda w: w.write_and_review("cửa sắt", RESEARCH, {}, OUTLINE)),
        ("Review", lambda w: w.review("cửa sắt", "T", draft_to_parts(DRAFT))),
        ("SectionText", lambda w: w.rewrite_section("cửa sắt", "T", draft_to_parts(DRAFT), 1)),
    ],
)
def test_network_error_at_every_step_is_an_ai_error(monkeypatch, schema, call):
    writer = make_writer(monkeypatch, ScriptedProvider(**{schema: NETWORK}))
    with pytest.raises(AIError, match="mạng"):
        call(writer)


class _Stream:
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return self.message


def test_web_search_that_never_finishes_stops_with_error():
    calls = []

    def stream(**kwargs):
        calls.append(kwargs)
        return _Stream(SimpleNamespace(stop_reason="pause_turn", parsed_output=None, content=[]))

    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(stream=stream)))
    task = TaskConfig(name="research", provider="anthropic", model="m", web_search=True)
    with pytest.raises(AIError, match="tìm kiếm quá lâu"):
        AnthropicProvider("k", client=client).generate(task, system="", prompt="", schema=Research)
    assert len(calls) == MAX_CONTINUATIONS + 1  # có giới hạn, không lặp mãi


def test_bad_flags_from_ai_are_dropped():
    parts = draft_to_parts(DRAFT)
    flags = [
        Flag(section=-1, sentence="304 nhiều niken hơn.", reason="", replacement=""),
        Flag(section=1, sentence="   ", reason="", replacement="x"),
        Flag(section=1, sentence="", reason="", replacement="x"),
        Flag(section=1, sentence="  304 nhiều niken hơn.  ", reason="", replacement="y"),
    ]
    assert [(f.section, f.sentence) for f in clean_flags(parts, flags)] == [
        (1, "304 nhiều niken hơn.")
    ]


def test_out_of_range_scores_are_clamped(monkeypatch):
    weird = Review(
        scores=Scores(friendly=-20, natural=250, readable=0, specific=100, seo=55),
        flags=[],
        summary="",
    )
    writer = make_writer(monkeypatch, ScriptedProvider(Review=weird))
    scores = writer.review("kw", "T", draft_to_parts(DRAFT)).scores
    assert scores.model_dump() == {
        "friendly": 0,
        "natural": 100,
        "readable": 0,
        "specific": 100,
        "seo": 55,
    }


def test_empty_draft_title_falls_back_to_outline_title(monkeypatch):
    draft = DRAFT.model_copy(update={"title": ""})
    writer = make_writer(monkeypatch, ScriptedProvider(Draft=draft))
    title, _ = writer.write("kw", RESEARCH, {}, OUTLINE)
    assert title == OUTLINE.title


# ------------------------------------------------------------------- AI trả rỗng


@pytest.mark.xfail(
    strict=True,
    reason="Lỗi #6: AI trả bài rỗng (không mở bài, không mục) vẫn được nhận như bài bình thường "
    "(workflow.py:108-114), không báo người dùng.",
)
def test_empty_draft_is_reported(monkeypatch):
    writer = make_writer(
        monkeypatch, ScriptedProvider(Draft=Draft(title="", intro="", sections=[]))
    )
    with pytest.raises(AIError):
        writer.write("kw", RESEARCH, {}, OUTLINE)


@pytest.mark.xfail(
    strict=True,
    reason="Lỗi #6: AI viết lại trả chuỗi rỗng thì rewrite_section trả '' (workflow.py:150), "
    "giao diện im lặng không làm gì (write.py:428).",
)
def test_empty_rewrite_is_reported(monkeypatch):
    writer = make_writer(monkeypatch, ScriptedProvider(SectionText=SectionText(body="  \n ")))
    with pytest.raises(AIError):
        writer.rewrite_section("kw", "T", draft_to_parts(DRAFT), 1)


def test_empty_outline_and_research_do_not_crash_prompts():
    empty_research = Research(
        intent=[], article_type="", competitors=[], new_angles=[], questions=[]
    )
    text = content_prompts.write_prompt("kw", empty_research, {}, Outline(title="", items=[]))
    assert "(người dùng chưa nhập)" in text


# ---------------------------------------------------------------------- tiếng Việt


def test_vietnamese_and_special_characters_survive_prompts():
    keyword = 'cửa sắt "2 cánh" <đẹp> & rẻ — giá?'
    material = {"Kinh nghiệm": "Ổ khóa Việt-Tiệp ≥ 3 năm; 50% khách hỏi «có gỉ không?»"}
    text = content_prompts.outline_prompt(keyword, RESEARCH, material)
    assert keyword in text
    assert material["Kinh nghiệm"] in text


def test_find_banned_is_case_insensitive_with_vietnamese_capitals():
    text = "TRONG THỜI ĐẠI công nghệ, cửa cuốn rất phổ biến. Cổng 304 bền."
    assert find_banned(text, list(RULES.banned)) == [
        ("TRONG THỜI ĐẠI công nghệ, cửa cuốn rất phổ biến.", "Trong thời đại")
    ]


@pytest.mark.xfail(
    strict=True,
    reason="Lỗi #7: so khớp cụm từ cấm không chuẩn hóa Unicode (rules.py:64-72); chữ tiếng "
    "Việt dạng tổ hợp (NFD, hay gặp khi dán từ máy Mac) lọt qua.",
)
def test_find_banned_handles_decomposed_vietnamese():
    text = unicodedata.normalize("NFD", "Trong thời đại số, cổng inox rất phổ biến.")
    assert find_banned(text, list(RULES.banned))


def test_find_missing_with_vietnamese_and_brackets():
    text = "Giá [cần bổ sung: giá cổng 4 m (2 cánh)] và [CẦN BỔ SUNG: ảnh] nhé."
    assert find_missing(text) == ["[cần bổ sung: giá cổng 4 m (2 cánh)]", "[CẦN BỔ SUNG: ảnh]"]


def test_apply_flag_removes_sentence_cleanly():
    body = "Câu một. Câu hai sáo rỗng. Câu ba."
    assert apply_flag(body, "Câu hai sáo rỗng.", "") == "Câu một. Câu ba."
    assert apply_flag(body, "Câu hai sáo rỗng.", "Câu hai cụ thể.") == (
        "Câu một. Câu hai cụ thể. Câu ba."
    )


def test_business_profile_with_unconfirmed_lowercase_tag_is_dropped(tmp_path):
    profile = tmp_path / "p.md"
    profile.write_text("- Hotline: 0909\n- Email: [cần xác nhận]\n", encoding="utf-8")
    rules = load_rules(profile_path=profile)
    assert "0909" in rules.business_profile
    assert "Email" not in rules.business_profile


# ----------------------------------------------- viết lại một phần không đụng phần khác


def test_rewrite_section_does_not_change_input_parts(monkeypatch):
    writer = make_writer(monkeypatch, FakeProvider())
    parts = draft_to_parts(DRAFT)
    before = [p.model_copy() for p in parts]
    body = writer.rewrite_section("kw", "T", parts, 2, ["Ngắn hơn"], "")
    assert body == "Bản viết lại số 1."
    assert parts == before


def test_rewrite_prompt_targets_only_the_chosen_part():
    parts = draft_to_parts(DRAFT)
    text = content_prompts.rewrite_prompt("kw", "T", parts, 3, [], "")
    assert "viết lại riêng phần [Phần 3] «Chi phí»" in text
    assert "[cần bổ sung" in text  # dặn giữ chỗ thiếu số liệu


# --------------------------------------------------------------- file cấu hình viết sai


def _write_toml(tmp_path, body: str):
    path = tmp_path / "ai.toml"
    path.write_text(body, encoding="utf-8")
    return path


@pytest.mark.xfail(
    strict=True,
    reason="Lỗi #4: max_tokens không phải số hoặc mục [tasks] viết sai dạng làm load_ai_config "
    "ném ValueError/AttributeError thay vì AIError (registry.py:32-48); trang Soạn bài "
    "chỉ bắt AIError nên sập.",
)
@pytest.mark.parametrize(
    "body",
    [
        '[tasks.write]\nprovider = "anthropic"\nmodel = "m"\nmax_tokens = "nhiều"',
        "[tasks]\nwrite = 1",
    ],
)
def test_bad_value_types_in_ai_config_give_ai_error(tmp_path, body):
    with pytest.raises(AIError):
        load_ai_config(_write_toml(tmp_path, body))


@pytest.mark.xfail(
    strict=True,
    reason='Lỗi #5: web_search = "false" (chuỗi) bị hiểu là True vì bool("false") '
    '(registry.py:47).',
)
def test_web_search_string_false_is_not_true(tmp_path):
    body = '[tasks.write]\nprovider = "anthropic"\nmodel = "m"\nweb_search = "false"'
    try:
        tasks = load_ai_config(_write_toml(tmp_path, body))
    except AIError:
        return  # báo lỗi rõ ràng cũng chấp nhận được
    assert tasks["write"].web_search is False


# ------------------------------------------------------------------ giao diện Soạn bài


@pytest.fixture
def app_env(monkeypatch):
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    monkeypatch.setenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


def open_write(project_root, monkeypatch, provider) -> AppTest:
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: provider)
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/write.py").run()
    assert not at.exception, at.exception
    return at


def button(at: AppTest, label: str, key: str | None = None):
    for b in at.button:
        if b.label == label and (key is None or b.key == key):
            return b
    raise AssertionError(f"Không thấy nút {label!r}")


def to_article(at: AppTest) -> AppTest:
    at.text_input(key="keyword").input("so sánh inox 201 và 304").run()
    button(at, "🔎 Phân tích từ khóa").click().run()
    button(at, "Tiếp: tạo dàn ý →").click().run()
    button(at, "✅ Duyệt dàn ý, viết toàn bài →").click().run()
    assert not at.exception, at.exception
    return at


def test_ai_error_on_research_is_shown_not_crash(project_root, monkeypatch, app_env):
    at = open_write(project_root, monkeypatch, ScriptedProvider(Research=NETWORK))
    at.text_input(key="keyword").input("cửa sắt").run()
    button(at, "🔎 Phân tích từ khóa").click().run()
    assert not at.exception, at.exception
    assert any("mạng" in e.value for e in at.error)
    assert at.session_state["research"] is None


def test_ai_error_on_write_keeps_user_on_outline(project_root, monkeypatch, app_env):
    at = open_write(project_root, monkeypatch, ScriptedProvider(Draft=NETWORK))
    at.text_input(key="keyword").input("cửa sắt").run()
    button(at, "🔎 Phân tích từ khóa").click().run()
    button(at, "Tiếp: tạo dàn ý →").click().run()
    button(at, "✅ Duyệt dàn ý, viết toàn bài →").click().run()
    assert not at.exception, at.exception
    assert at.session_state["step"] == 1
    assert at.session_state["part_ids"] == []
    assert any("mạng" in e.value for e in at.error)


def test_rewriting_one_part_leaves_other_parts_untouched(project_root, monkeypatch, app_env):
    at = to_article(open_write(project_root, monkeypatch, FakeProvider()))
    ids = at.session_state["part_ids"]
    before = {pid: list(at.session_state[f"texts-{pid}"]) for pid in ids}
    target = ids[2]
    button(at, "Viết lại phần này", key=f"do-rw-{target}").click().run()
    assert not at.exception, at.exception
    for pid in ids:
        if pid == target:
            assert at.session_state[f"texts-{pid}"] == [*before[pid], "Bản viết lại số 1."]
            assert at.session_state[f"ver-{pid}"] == 1
        else:
            assert at.session_state[f"texts-{pid}"] == before[pid]
            assert at.session_state[f"ver-{pid}"] == 0


def test_rewrite_error_keeps_old_version(project_root, monkeypatch, app_env):
    provider = ScriptedProvider(SectionText=NETWORK)
    at = to_article(open_write(project_root, monkeypatch, provider))
    pid = at.session_state["part_ids"][1]
    before = list(at.session_state[f"texts-{pid}"])
    button(at, "Viết lại phần này", key=f"do-rw-{pid}").click().run()
    assert not at.exception, at.exception
    assert at.session_state[f"texts-{pid}"] == before
    assert any("mạng" in e.value for e in at.error)


def test_competitor_javascript_link_is_not_rendered(project_root, monkeypatch, app_env):
    research = RESEARCH.model_copy(
        update={
            "competitors": [
                Competitor(title="Bài lạ", url="javascript:alert(1)", covers="a", missing="b")
            ]
        }
    )
    at = open_write(project_root, monkeypatch, ScriptedProvider(Research=research))
    at.text_input(key="keyword").input("cửa sắt").run()
    button(at, "🔎 Phân tích từ khóa").click().run()
    assert not any("javascript:" in m.value for m in at.markdown)


def test_html_in_ai_article_is_not_rendered_as_html(project_root, monkeypatch, app_env):
    draft = Draft(
        title="Bài có mã độc",
        intro=f"Mở bài bình thường. {XSS}",
        sections=[
            Section(heading=i.heading, body="<script>alert(2)</script>") for i in OUTLINE.items
        ],
    )
    at = to_article(open_write(project_root, monkeypatch, ScriptedProvider(Draft=draft)))
    html_blocks = [m for m in at.markdown if getattr(m.proto, "allow_html", False)]
    assert html_blocks
    for m in html_blocks:
        assert "onerror" not in m.value and "<script" not in m.value


def test_publish_now_requires_confirmation(project_root, monkeypatch, app_env):
    at = open_write(project_root, monkeypatch, FakeProvider())
    at.session_state["step"] = 4
    at.run()
    send = "📤 Gửi sang WordPress"
    assert not button(at, send).disabled  # Nháp: được gửi
    at.segmented_control[-1].set_value("Đăng ngay").run()
    assert button(at, send).disabled
    at.checkbox[0].check().run()
    assert not button(at, send).disabled


def test_page_opens_with_minimal_ai_config(project_root, monkeypatch, app_env, tmp_path):
    """Đối chứng cho test xfail bên dưới: cách thay file cấu hình hoạt động đúng."""
    path = _write_toml(tmp_path, '[tasks.write]\nprovider = "anthropic"\nmodel = "m"')
    monkeypatch.setattr(load_ai_config, "__defaults__", (path,))
    at = open_write(project_root, monkeypatch, FakeProvider())
    assert not at.exception


@pytest.mark.xfail(strict=True, reason="Lỗi #4: trang Soạn bài sập khi max_tokens không phải số.")
def test_non_numeric_max_tokens_shows_warning(project_root, monkeypatch, app_env, tmp_path):
    path = _write_toml(
        tmp_path, '[tasks.write]\nprovider = "anthropic"\nmodel = "m"\nmax_tokens = "nhiều"'
    )
    monkeypatch.setattr(load_ai_config, "__defaults__", (path,))
    at = open_write(project_root, monkeypatch, FakeProvider())
    assert not at.exception

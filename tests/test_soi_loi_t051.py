"""Soi Lỗi T-051 (rút gọn): cấu hình việc ảnh (``config/ai.toml``) và quy tắc alt
(``config/content.toml``). Báo cáo: ``docs/team/reports/T-051-soi-loi.md``.

Kiểm:

- hai file đọc được bằng chính bộ đọc của app, mục mới không đổi kết quả của việc cũ; file hỏng
  hay thiếu mục vẫn báo lỗi tiếng Việt như T-010, trang Soạn bài không sập;
- khối ``[tasks.image]`` đang tắt không làm trang Soạn bài đòi khóa Gemini; bật thử khối này
  trong bản tạm (``tmp_path``, không đụng file thật) đúng cách chú thích trong file hướng dẫn;
- 6 ví dụ alt không vi phạm chính quy tắc ``[alt]``, còn mỗi bản xấu vi phạm ít nhất một quy tắc.

Test ``xfail(strict=True)`` = việc còn chờ T-062, đánh số SL-T051-… khớp báo cáo. Khi T-062 làm
xong, test báo XPASS và phải gỡ dấu ``xfail``. Không gọi mạng, khóa API là chuỗi giả, không
cần .env.
"""

import re
import tomllib
import unicodedata
from collections import Counter

import pytest
from streamlit.testing.v1 import AppTest

import seo_app.content.rules as rules_module
from seo_app.ai import AIError
from seo_app.ai import registry as ai_registry
from seo_app.ai.registry import AIRouter, load_ai_config
from seo_app.config import Settings
from seo_app.content import blind_test
from seo_app.content.rules import ContentRulesError, find_banned, load_rules

AI_TOML = ai_registry.AI_CONFIG_FILE
CONTENT_TOML = rules_module.CONTENT_CONFIG_FILE
NO_PROFILE = "khong-co-ho-so.md"
FAKE_KEY = "sk-ant-khoa-gia-t051-khong-duoc-hien"
KEY_FIELDS = {
    "anthropic": "anthropic_api_key",
    "openai": "openai_api_key",
    "gemini": "gemini_api_key",
}
WRITING_TASKS = ("research", "outline", "write", "rewrite", "review")
# 4 dòng mà chú thích trong ai.toml bảo xóa dấu # khi bật việc tạo ảnh, theo đúng thứ tự.
IMAGE_LINES = ("[tasks.image]", "provider", "model", "max_tokens")

T062 = "chờ T-062 (Thợ Máy)"


def _ai_text() -> str:
    return AI_TOML.read_text(encoding="utf-8")


def _content_text() -> str:
    return CONTENT_TOML.read_text(encoding="utf-8")


def _alt() -> dict:
    return tomllib.loads(_content_text())["alt"]


def enable_image_block(text: str, lines: int = len(IMAGE_LINES), keep_space: bool = False) -> str:
    """Làm như chú thích trong ai.toml: xóa dấu # ở đầu ``lines`` dòng đầu của khối
    ``[tasks.image]``. ``keep_space``: chỉ xóa «#», để lại dấu cách đầu dòng (người dùng hay xóa
    như vậy trong Notepad)."""
    rows = text.split("\n")
    starts = [i for i, row in enumerate(rows) if row.startswith("# [tasks.image]")]
    assert len(starts) == 1, "ai.toml phải có đúng một dòng «# [tasks.image]»"
    for offset, prefix in enumerate(IMAGE_LINES[:lines]):
        row = rows[starts[0] + offset]
        assert row.startswith(f"# {prefix}"), f"dòng thứ {offset + 1} của khối ảnh: {row!r}"
        rows[starts[0] + offset] = row[1:] if keep_space else row[2:]
    return "\n".join(rows)


def _write(tmp_path, name: str, text: str):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _enabled_ai_toml(tmp_path):
    return _write(tmp_path, "ai.toml", enable_image_block(_ai_text()))


# ------------------------------------------------------------------ config/ai.toml


def test_alt_task_is_claude_sonnet_with_small_budget():
    # Quyết định 4A: alt viết bằng Claude Sonnet; việc ngắn nên effort thấp, không tìm web.
    alt = load_ai_config()["alt"]
    assert (alt.provider, alt.model, alt.effort, alt.max_tokens, alt.web_search) == (
        "anthropic",
        "claude-sonnet-5-5",
        "low",
        2000,
        False,
    )


def test_old_tasks_still_load_next_to_alt():
    tasks = load_ai_config()
    assert {*WRITING_TASKS, "meta", "alt"} <= set(tasks)
    assert tasks["research"].web_search is True
    assert [n for n, t in tasks.items() if t.web_search] == ["research"]


def test_ai_toml_header_names_three_providers_and_no_default():
    header = _ai_text().split("\n[tasks.")[0]  # chú thích trước mục [tasks.…] thật đầu tiên
    for word in ('"anthropic"', '"openai"', '"gemini"', "Không có hãng mặc định"):
        assert word in header
    assert "Claude KHÔNG tạo được ảnh" in header


def test_image_task_never_forces_an_extra_key_for_writing():
    """Chỉ có khóa của các hãng mà các việc khác dùng: trang Soạn bài (``AIRouter``) vẫn tạo được.

    Đang qua vì ``[tasks.image]`` tắt. Ai bật khối này trước khi T-062 làm ``AIRouter`` tạo
    provider khi cần thì test này hỏng (đúng lý do khối đang tắt)."""
    tasks = load_ai_config()
    keys = {KEY_FIELDS[t.provider]: "khoa-gia" for name, t in tasks.items() if name != "image"}
    router = AIRouter(tasks, Settings(**keys))
    for name in WRITING_TASKS:
        router.get(name)


def test_image_block_is_written_exactly_as_the_comment_says():
    text = _ai_text()
    assert "\n[tasks.image]" not in text  # đang tắt
    enable_image_block(text)  # đủ 4 dòng, đúng thứ tự, mỗi dòng bắt đầu bằng «# »


@pytest.mark.parametrize(
    "keep_space", [False, True], ids=["xoa-dau-thang-va-cach", "chi-xoa-dau-thang"]
)
def test_enabled_image_block_reads_as_gemini_and_keeps_other_tasks(tmp_path, keep_space):
    path = _write(tmp_path, "ai.toml", enable_image_block(_ai_text(), keep_space=keep_space))
    tasks = load_ai_config(path)
    image = tasks["image"]
    assert (image.provider, image.model, image.max_tokens, image.web_search) == (
        "gemini",
        "gemini-nano-banana-2.1",
        2000,
        False,
    )
    assert {n: t for n, t in tasks.items() if n != "image"} == load_ai_config()


def test_half_enabled_image_block_gives_vietnamese_error(tmp_path):
    # Người dùng chỉ xóa # ở 2 dòng đầu (quên dòng model): báo rõ, không đoán tên mô hình.
    path = _write(tmp_path, "ai.toml", enable_image_block(_ai_text(), lines=2))
    with pytest.raises(AIError, match="«image».*model"):
        load_ai_config(path)


@pytest.mark.xfail(
    strict=True,
    raises=AIError,
    reason=f"SL-T051-1, {T062}: AIRouter tạo provider cho mọi việc ngay lúc tạo",
)
def test_sl_t051_1_enabled_image_needs_gemini_key_only_when_called(tmp_path):
    tasks = load_ai_config(_enabled_ai_toml(tmp_path))
    try:
        router = AIRouter(tasks, Settings(anthropic_api_key=FAKE_KEY))
    except AIError as exc:
        # Đúng lý do Ngòi Bút ghi trong báo cáo T-051 (không phải lỗi khác).
        assert "GEMINI_API_KEY" in str(exc) and FAKE_KEY not in str(exc)
        raise
    router.get("write")
    with pytest.raises(AIError, match="GEMINI_API_KEY"):
        router.get("image")


@pytest.mark.xfail(
    strict=True,
    raises=pytest.fail.Exception,  # «DID NOT RAISE»: hiện file vẫn đọc được
    reason=f"SL-T051-2, {T062}: chưa từ chối Claude cho việc tạo ảnh",
)
def test_sl_t051_2_image_task_on_anthropic_is_refused(tmp_path):
    gemini = 'provider = "gemini"\nmodel = "gemini-nano-banana-2.1"'
    text = enable_image_block(_ai_text())
    assert text.count(gemini) == 1
    text = text.replace(gemini, gemini.replace('"gemini"', '"anthropic"', 1))
    with pytest.raises(AIError, match="Claude không tạo được ảnh"):
        load_ai_config(_write(tmp_path, "ai.toml", text))


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=f"SL-T051-3, {T062}: TASK_LABELS thiếu nhãn alt, meta",
)
def test_sl_t051_3_every_task_has_a_vietnamese_label():
    # Cài đặt → 🤖 Mô hình AI hiện bảng việc–mô hình: việc thiếu nhãn hiện tên thô «alt», «meta».
    raw = [row.task for row in blind_test.task_models() if row.task_label == row.task]
    assert raw == []


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=f"SL-T051-4, {T062}: thử mù gợi ý cả mô hình tạo ảnh",
)
def test_sl_t051_4_blind_test_does_not_suggest_image_model(tmp_path):
    rows = blind_test.task_models(_enabled_ai_toml(tmp_path))
    assert "gemini-nano-banana-2.1" not in blind_test.model_suggestions(rows)["gemini"]


@pytest.mark.parametrize(
    "broken",
    ["bom", "ansi", "cut"],
)
def test_real_ai_toml_broken_on_disk_is_handled_like_t010(tmp_path, broken):
    text = _ai_text()
    if broken == "bom":
        path = tmp_path / "ai.toml"
        path.write_bytes(b"\xef\xbb\xbf" + AI_TOML.read_bytes())
        assert load_ai_config(path) == load_ai_config()
        return
    if broken == "ansi":
        path = tmp_path / "ai.toml"
        path.write_bytes(text.encode("cp1258", errors="replace"))
        match = "UTF-8"
    else:  # file lưu dở giữa mục [tasks.alt]
        path = _write(tmp_path, "ai.toml", text[: text.index('model = "claude-sonnet-5-5"') + 12])
        match = "cú pháp"
    with pytest.raises(AIError, match=match):
        load_ai_config(path)


# ------------------------------------------------------------- config/content.toml


def test_project_content_toml_loads_with_new_sections():
    rules = load_rules()
    assert rules.address and rules.tone and rules.banned and rules.checklist
    images = tomllib.loads(_content_text())["images"]
    assert set(images) == {"webp_quality", "max_edge_px"}
    assert type(images["webp_quality"]) is int and 1 <= images["webp_quality"] <= 100
    assert type(images["max_edge_px"]) is int and images["max_edge_px"] == 1600  # quyết định 5A


def test_new_sections_do_not_change_old_rules(tmp_path):
    text = _content_text()
    old = _write(tmp_path, "content.toml", text[: text.index("\n[images]")] + "\n")
    profile = tmp_path / NO_PROFILE
    assert load_rules(old, profile) == load_rules(CONTENT_TOML, profile)


def test_alt_section_shape():
    alt = _alt()
    assert type(alt["max_chars"]) is int and 0 < alt["max_chars"] <= 125
    assert type(alt["caption_max_chars"]) is int and alt["caption_max_chars"] > alt["max_chars"]
    for key in ("rules", "bad_starts"):
        assert alt[key] and all(isinstance(v, str) and v.strip() for v in alt[key]), key
    examples = alt["examples"]
    assert len(examples) >= 6
    for example in examples:
        assert set(example) == {"anh", "the", "tot", "xau", "vi_sao"}
        assert all(isinstance(v, str) and v.strip() for v in example.values())
    sources = Counter(e["anh"].split(":")[0] for e in examples)
    assert sources["Ảnh thật"] >= 2 and sources["Ảnh AI"] >= 2


def test_limits_named_in_rules_exist_in_alt_section():
    # Quy tắc ghi «không quá max_chars ký tự»: tên đó phải có thật trong [alt], đổi tên là lộ.
    alt = _alt()
    names = set(re.findall(r"\b[a-z]+(?:_[a-z]+)+\b", " ".join(alt["rules"])))
    assert names == {"max_chars", "caption_max_chars"}
    assert names <= set(alt)


@pytest.mark.parametrize(
    ("yeu_cau", "words"),
    [
        ("ngắn, có giới hạn ký tự", ["không quá max_chars ký tự"]),
        ("không nhồi từ khóa", ["Từ khóa của bài", "tối đa một lần", "không liệt kê từ khóa"]),
        (
            "không bịa địa điểm hay tên khách",
            ["Không bịa địa điểm, tên khách", "Không bao giờ ghi tên khách"],
        ),
        (
            "ảnh AI không tả như công trình thật",
            ["không bao giờ được tả như công trình thật", "«Minh họa»", "«Ảnh minh họa (AI)»"],
        ),
        ("chữ trong ảnh không chép", ["Chữ đọc được trong ảnh"]),
    ],
)
def test_alt_rules_cover_ticket_requirements(yeu_cau, words):
    text = "\n".join(_alt()["rules"])
    for word in words:
        assert word in text, f"{yeu_cau}: thiếu «{word}»"


# ------------------------------------------------- ví dụ alt theo đúng quy tắc của nó

# Tên quận/huyện TP.HCM (và tên lạ có trong ví dụ) để dò khu vực bịa thêm. So trên chữ thường.
_AREA = re.compile(
    r"\bquận\s+\d+\b|\b(?:bình tân|tân bình|gò vấp|hải châu|bình thạnh|phú nhuận|tân phú|thủ đức"
    r"|bình chánh|hóc môn|củ chi|nhà bè|cần giờ)\b"
)
# Cụm cấm riêng cho alt ảnh AI (quy tắc «Ảnh tạo bằng AI không bao giờ…»), đã tách «anh/chị».
_AI_FORBIDDEN = (
    "công trình",
    "thi công",
    "nhà anh",
    "nhà chị",
    "tại quận",
    "trước khi sửa",
    "sau khi sửa",
    "pro-metal",
)
_NUMBER_WITH_UNIT = re.compile(r"\d+\s*(?:phút|giờ|ngày|tháng|năm|m|cm|mm|kg|k|đồng|nghìn|triệu)\b")
_PERSON = re.compile(r"\b(?:anh|chị|cô|chú|ông|bà)\s+(\w)")
_STREET = re.compile(r"\bđường\s+(\w)")


def _ad_words(rules: list[str]) -> list[str]:
    rule = next(r for r in rules if "quảng cáo" in r)
    words = [w.casefold() for w in re.findall(r"«([^»]+)»", rule)]
    assert words, rule
    return words


def _tags(example: dict) -> dict[str, str]:
    out = {}
    for part in example["the"].split(";"):
        key, sep, value = part.partition(":")
        if sep:
            out[key.strip().casefold()] = value.strip().casefold()
    return out


def violations(text: str, example: dict, alt: dict, banned: tuple[str, ...]) -> list[str]:
    """Các quy tắc [alt] mà ``text`` (alt cho ảnh ``example``) vi phạm, dò được bằng máy."""
    text = unicodedata.normalize("NFC", text)
    low = text.casefold()
    tags = _tags(example)
    is_ai = example["anh"].startswith("Ảnh AI")
    found = []
    if len(text) > alt["max_chars"]:
        found.append(f"dài {len(text)} > {alt['max_chars']} ký tự")
    if "\n" in text or text != text.strip():
        found.append("xuống dòng hoặc thừa khoảng trắng")
    if text[-1:] in tuple(".!?…;:,"):
        found.append("chấm câu ở cuối")
    if any(low.startswith(s.casefold()) for s in alt["bad_starts"]):
        found.append("mở đầu bằng «Hình ảnh/Ảnh…»")
    if find_banned(text, banned):
        found.append("cụm từ cấm của [voice].banned")
    found += [f"quảng cáo «{w}»" for w in _ad_words(alt["rules"]) if w in low]
    if "pro-metal" in low and "pro-metal" not in example["anh"].casefold():
        found.append("thêm tên Pro-Metal không có trong ảnh")
    if re.search(r"\b0\d{2,}", low):
        found.append("số điện thoại")
    if _NUMBER_WITH_UNIT.search(low):
        found.append("số liệu ảnh không cho thấy")
    if any(m.group(1).isupper() for m in _PERSON.finditer(text)):
        found.append("tên người")
    if any(m.group(1).isupper() for m in _STREET.finditer(text)):
        found.append("tên đường")
    repeated = [w for w, n in Counter(re.findall(r"\w{3,}", low)).items() if n >= 3]
    if repeated:
        found.append(f"lặp từ (nhồi): {repeated}")
    for area in _AREA.findall(low):
        if is_ai or area != tags.get("khu vực"):
            found.append(f"khu vực «{area}» không có trong thẻ")
    for phrase, tag in (("trước khi sửa", "trước"), ("sau khi sửa", "sau")):
        if phrase in low and (is_ai or tags.get("trước/sau") != tag):
            found.append(f"«{phrase}» không theo thẻ")
    if is_ai:
        if not text.startswith("Minh họa"):
            found.append("ảnh AI không mở đầu bằng «Minh họa»")
        found += [f"ảnh AI tả như thật: «{w}»" for w in _AI_FORBIDDEN if w in low]
    return found


def test_good_examples_follow_their_own_rules():
    alt = _alt()
    banned = load_rules().banned
    problems = {e["tot"]: violations(e["tot"], e, alt, banned) for e in alt["examples"]}
    assert {tot: p for tot, p in problems.items() if p} == {}


def test_bad_examples_really_break_a_rule():
    # Bản «xau» phải sai thật, không thì AI học nhầm điều cần tránh.
    alt = _alt()
    banned = load_rules().banned
    clean = [e["xau"] for e in alt["examples"] if not violations(e["xau"], e, alt, banned)]
    assert clean == []


def test_good_examples_are_all_different_and_real_ones_do_not_pose_as_ai():
    examples = _alt()["examples"]
    goods = [e["tot"] for e in examples]
    assert len(set(goods)) == len(goods)
    for e in examples:
        if e["anh"].startswith("Ảnh thật"):
            assert not e["tot"].startswith("Minh họa"), e["tot"]


def test_violation_checker_catches_each_rule():
    # Máy dò ở trên phải bắt được từng lỗi, không thì test «ví dụ tốt» qua mà không nói lên gì.
    alt = _alt()
    banned = load_rules().banned
    real = {
        "anh": "Ảnh thật: cửa cuốn",
        "the": "hạng mục: sửa cửa cuốn; khu vực: Tân Bình; trước/sau: trước",
    }
    ai = {"anh": "Ảnh AI: cửa cuốn", "the": "nguồn: AI"}
    cases = [
        (real, "Cửa cuốn " + "kẹt " * 40, "dài"),
        (real, "Cửa cuốn kẹt lưng chừng.", "chấm câu"),
        (real, "Ảnh cửa cuốn kẹt lưng chừng", "mở đầu"),
        (real, "Trong thời đại nay cửa cuốn kẹt", "cụm từ cấm"),
        (real, "Cửa cuốn uy tín kẹt lưng chừng", "quảng cáo"),
        (real, "Cửa cuốn Pro-Metal kẹt lưng chừng", "Pro-Metal"),
        (real, "Cửa cuốn kẹt, gọi 0909123456", "số điện thoại"),
        (real, "Cửa cuốn kẹt, sửa xong trong 30 phút", "số liệu"),
        (real, "Cửa cuốn nhà anh Tuấn bị kẹt", "tên người"),
        (real, "Cửa cuốn kẹt ở đường Cộng Hòa", "tên đường"),
        (real, "Cửa cuốn kẹt ở Gò Vấp", "khu vực"),
        (real, "Cửa cuốn kẹt, sau khi sửa", "sau khi sửa"),
        (real, "sửa cửa cuốn, sửa cửa cuốn kẹt, sửa cửa", "lặp từ"),
        (ai, "Cửa cuốn nhà phố mở một nửa", "Minh họa"),
        (ai, "Minh họa công trình cửa cuốn", "tả như thật"),
        (ai, "Minh họa cửa cuốn ở Tân Bình", "khu vực"),
    ]
    missed = [
        (text, rule)
        for example, text, rule in cases
        if not any(rule in v for v in violations(text, example, alt, banned))
    ]
    assert missed == []


# ----------------------------------------------- content.toml hỏng hay thiếu mục (T-010)


@pytest.mark.parametrize("broken", ["bom", "ansi", "cut", "alt-sai-dang", "thieu-muc-moi"])
def test_real_content_toml_broken_on_disk_is_handled_like_t010(tmp_path, broken):
    text = _content_text()
    profile = tmp_path / NO_PROFILE
    path = tmp_path / "content.toml"
    if broken == "bom":
        path.write_bytes(b"\xef\xbb\xbf" + CONTENT_TOML.read_bytes())
    elif broken == "ansi":
        path.write_bytes(text.encode("cp1258", errors="replace"))
    elif broken == "cut":  # lưu dở giữa ví dụ alt đầu tiên
        path.write_text(text[: text.index('anh = "Ảnh thật') + 12], encoding="utf-8")
    elif broken == "alt-sai-dang":
        path.write_text(text.replace("max_chars = 125", 'max_chars = "125"'), encoding="utf-8")
    else:
        path.write_text(text[: text.index("\n[images]")] + "\n", encoding="utf-8")

    if broken == "ansi":
        with pytest.raises(ContentRulesError, match="UTF-8"):
            load_rules(path, profile)
    elif broken == "cut":
        with pytest.raises(ContentRulesError, match="cú pháp"):
            load_rules(path, profile)
    else:
        # Bộ đọc hiện nay chưa đọc [images]/[alt] (T-062 làm): thiếu hay sai dạng thì việc cũ
        # vẫn chạy; khi T-062 đọc các mục này, sai dạng được phép báo ContentRulesError.
        try:
            assert load_rules(path, profile) == load_rules(CONTENT_TOML, profile)
        except ContentRulesError as exc:
            assert broken == "alt-sai-dang" and "max_chars" in str(exc)


# ------------------------------------------------------------------ trang Soạn bài


def _open_write_page(project_root) -> AppTest:
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.session_state["authenticated"] = True
    at.switch_page("views/write.py").run()
    if at.exception:
        # Không dùng assert: test xfail dưới đây chỉ chấp nhận AssertionError về khóa Gemini.
        pytest.fail(f"Trang Soạn bài sập: {at.exception}")
    return at


def _shown_text(at: AppTest) -> list[str]:
    return [
        e.value for kind in (at.warning, at.error, at.info, at.markdown, at.caption) for e in kind
    ]


def _analyze_button(at: AppTest):
    return next(b for b in at.button if b.label == "🔎 Phân tích từ khóa")


def test_write_page_with_committed_config_needs_only_claude_key(project_root, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    at = _open_write_page(project_root)
    assert not [w.value for w in at.warning if "API_KEY" in w.value]
    at.text_input(key="keyword").input("sửa cửa cuốn bị kẹt").run()
    assert not _analyze_button(at).disabled
    assert not any(FAKE_KEY in t for t in _shown_text(at))


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=f"SL-T051-1, {T062}: bật [tasks.image] thì trang Soạn bài đòi khóa Gemini",
)
def test_sl_t051_1_write_page_with_image_enabled_does_not_ask_for_gemini_key(
    project_root, tmp_path, monkeypatch
):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(ai_registry.load_ai_config, "__defaults__", (_enabled_ai_toml(tmp_path),))
    at = _open_write_page(project_root)
    warnings = [w.value for w in at.warning]
    assert not any("GEMINI_API_KEY" in w for w in warnings), warnings


@pytest.mark.parametrize("variant", ["bat-du", "bat-nua"])
def test_write_page_with_image_block_touched_never_crashes_or_shows_key(
    project_root, tmp_path, monkeypatch, variant
):
    # Bật đủ (chưa có T-062) hay bật nửa chừng: trang báo tiếng Việt, khóa nút AI, không lộ khóa.
    lines = len(IMAGE_LINES) if variant == "bat-du" else 2
    path = _write(tmp_path, "ai.toml", enable_image_block(_ai_text(), lines=lines))
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(ai_registry.load_ai_config, "__defaults__", (path,))
    at = _open_write_page(project_root)
    shown = _shown_text(at)
    assert not any(FAKE_KEY in t for t in shown)
    if variant == "bat-nua":
        assert any("«image»" in w.value and "model" in w.value for w in at.warning)
        at.text_input(key="keyword").input("sửa cửa cuốn bị kẹt").run()
        assert _analyze_button(at).disabled


@pytest.mark.parametrize("broken", ["ansi", "cut", "alt-sai-dang"])
def test_write_page_survives_broken_real_content_toml(project_root, tmp_path, monkeypatch, broken):
    text = _content_text()
    path = tmp_path / "content.toml"
    if broken == "ansi":
        path.write_bytes(text.encode("cp1258", errors="replace"))
    elif broken == "cut":
        path.write_text(text[: text.index('anh = "Ảnh thật') + 12], encoding="utf-8")
    else:
        path.write_text(text.replace("max_chars = 125", 'max_chars = "125"'), encoding="utf-8")
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(rules_module.load_rules, "__defaults__", (path, tmp_path / NO_PROFILE))
    at = _open_write_page(project_root)
    if broken != "alt-sai-dang":
        assert any("UTF-8" in w.value or "cú pháp" in w.value for w in at.warning)

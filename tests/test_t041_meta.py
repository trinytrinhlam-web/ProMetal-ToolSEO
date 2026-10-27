"""T-041 (Thợ Máy): bộ kiểm meta trước khi bước SEO dùng gợi ý AI, và mục [meta] của content.toml.

- LC-T036-1: ký tự điều khiển (Cc), surrogate lẻ (Cs), ký tự riêng (Co), chưa gán (Cn) bị bỏ ở
  chữ người dùng gõ, gợi ý AI (JSON ``\\u0000``, ``\\u001b``) và hậu tố thương hiệu.
- SL-T036-12: ``has_link``, ``mentions_price`` gọi thẳng với chữ dài không treo, coi như có.
- LC-T040-1: chỗ nói giá vắt qua mép từ khóa vẫn bị bắt; cụm nên tránh (``[meta].avoid``) dò
  cùng cách.
- SL-T040-1: title 49 ký tự (không gắn được « | Pro-Metal») là «dài vừa».
- ``load_meta_rules`` và ``ContentWriter.meta`` dùng mục ``[meta]``.
- Hàm cho giao diện: ``site_posts``, ``siteseo_copy``.

Không gọi AI, không gọi mạng: AI là provider giả.
"""

from __future__ import annotations

import json

import pytest
from timing import assert_scales_linearly

from seo_app.ai import AIRouter, TaskConfig
from seo_app.ai import registry as ai_registry
from seo_app.ai.registry import missing_task_message
from seo_app.config import Settings
from seo_app.content import ContentWriter, Section, prompts
from seo_app.content.prompts import MetaSuggestions
from seo_app.content.rules import (
    CONTENT_CONFIG_FILE,
    ContentRules,
    ContentRulesError,
    MetaRules,
    load_meta_rules,
    load_rules,
)
from seo_app.onpage.meta import (
    BRAND_SUFFIX,
    MAX_SCAN_CHARS,
    Level,
    accept_ai_description,
    accept_ai_title,
    check_description,
    check_title,
    check_title_duplicates,
    filter_ai_titles,
    find_avoided,
    has_link,
    has_odd_chars,
    mentions_price,
    normalize_meta,
    resolve_brand_suffix,
    seo_write_problem,
    site_posts,
    siteseo_copy,
    with_brand,
)
from seo_app.storage.site_index import SiteIndex
from seo_app.wordpress.client import PublishedItem

KEYWORD = "cửa sắt bị xệ"
TITLE = "Cửa sắt bị xệ: dấu hiệu sớm và cách xử lý gọn"  # 45 ký tự: gắn được đuôi
DESC = (
    "Cửa sắt bị xệ, cạ nền khi đóng mở? Xem 5 dấu hiệu sớm, nguyên nhân hay gặp và việc bạn tự "
    "làm được trước khi gọi thợ đến tận nhà."
)
ODD = ["\x00", "\x1b", "\x7f", "\x9b", "\ud800", "\udfff", "", "\U000f0000", "͸"]


# ============================================================ LC-T036-1: ký tự lạ


@pytest.mark.parametrize("odd", ODD)
def test_user_text_with_odd_chars_is_blocked(odd):
    """Lượt 3: chữ người dùng có ký tự điều khiển / ký tự lạ bị Chặn kèm câu báo (không lặng lẽ
    bỏ ký tự rồi chép, ghi); ``value`` vẫn là chữ đã chuẩn hóa, không còn ký tự đó."""
    raw = TITLE.replace("bị", f"b{odd}ị")
    assert normalize_meta(raw) == TITLE and has_odd_chars(raw)
    for check in (check_title(raw), check_title(raw, ""), check_description(DESC + odd)):
        assert check.level is Level.BLOCK
        assert "ký tự điều khiển hoặc ký tự lạ" in " ".join(check.messages)
        assert odd not in check.value and check.value.encode("utf-8")
        assert odd not in " ".join(check.messages)
    copy = siteseo_copy(raw, DESC + odd, "cua-sat-bi-xe")
    assert copy.title is None and copy.description is None and copy.slug == "cua-sat-bi-xe"


@pytest.mark.parametrize("odd", ["\x00", "\x1b"])
def test_ai_json_with_control_chars_is_rejected(odd):
    """Đường AI thật: JSON có ``\\u0000``/``\\u001b`` qua được khuôn ``MetaSuggestions``; gợi ý đó
    bị bỏ (lượt 3), bản không có ký tự lạ thì được nhận."""
    escaped = json.dumps(odd)[1:-1]
    raw = MetaSuggestions.model_validate_json(
        f'{{"titles": ["Cửa sắt bị xệ:{escaped} dấu hiệu sớm và cách xử lý gọn"],'
        f' "descriptions": ["{DESC[:20]}{escaped}{DESC[20:]}"]}}'
    )
    assert odd in raw.titles[0]
    assert accept_ai_title(raw.titles[0], KEYWORD) is None
    assert accept_ai_description(raw.descriptions[0], KEYWORD) is None
    assert accept_ai_title(TITLE, KEYWORD) == TITLE + BRAND_SUFFIX
    assert accept_ai_description(DESC, KEYWORD) == DESC


@pytest.mark.parametrize("odd", ODD)
def test_brand_suffix_with_odd_chars_falls_back_to_default(odd):
    """Đuôi trong cấu hình có ký tự lạ là cấu hình sai: dùng đuôi mặc định, như khi có thẻ HTML."""
    assert resolve_brand_suffix(f" | Pro{odd}-Metal") == BRAND_SUFFIX
    assert resolve_brand_suffix(f" | Cơ khí{odd} PM") == BRAND_SUFFIX
    assert with_brand(TITLE, f" | Cơ khí{odd} PM") == TITLE + BRAND_SUFFIX


def test_whitespace_control_chars_still_become_spaces():
    text = "Cửa\tsắt\nbị\x0bxệ\x1c\x85gọn"
    assert normalize_meta(text) == "Cửa sắt bị xệ gọn"
    assert not has_odd_chars(text)  # tab, xuống dòng… là khoảng trắng, không phải ký tự lạ
    assert check_title(text + " dấu hiệu sớm và cách xử lý tại nhà").level is Level.GOOD
    assert normalize_meta("a\x00b") == "ab" and has_odd_chars("a\x00b")


# ============================================================ SL-T036-12: chữ dài


@pytest.mark.parametrize(
    "make",
    [lambda k: "a-" * (k * 2000), lambda k: "a." * (k * 2000), lambda k: "1" * (k * 4000)],
    ids=["gach", "cham", "so"],
)
@pytest.mark.parametrize("fn", [has_link, mentions_price], ids=["link", "gia"])
def test_detectors_linear_on_long_text(fn, make):
    assert_scales_linearly(fn, make, label="dò link/giá")


def test_long_text_counts_as_found():
    """Dài quá mức dò: coi như có link, có giá (hướng an toàn), không dò bậc hai."""
    long_plain = "chữ thường " * (MAX_SCAN_CHARS // 5)
    assert has_link(long_plain) and mentions_price(long_plain)
    assert find_avoided(long_plain, ["uy tín"]) == ["uy tín"]
    # NFKC làm chữ dài ra (U+FDFA thành 18 ký tự): đo cả sau NFKC.
    assert has_link("ﷺ" * (MAX_SCAN_CHARS // 10))
    short = "Cửa sắt bị xệ: dấu hiệu sớm"
    assert not has_link(short) and not mentions_price(short)


# ============================================================ LC-T040-1 và cụm nên tránh


@pytest.mark.parametrize(
    ("keyword", "text"),
    [
        ("giá sửa cửa sắt", "Giá sửa cửa sắt giá rẻ: những gì quyết định"),
        ("báo giá", "Cửa kéo báo giá tốt cho nhà phố"),
        ("cửa sắt giá", "Cửa sắt giá 500k: những gì cần biết"),
        ("sửa cua quận 1", "Sửa cua quận 1 triệu: thợ đến tận nơi"),
        ("sửa cua quận 1", "Sửa cua quận 1.000đ: thợ đến tận nơi"),
    ],
)
def test_price_touching_keyword_is_found(keyword, text):
    assert mentions_price(text, keyword)


@pytest.mark.parametrize(
    ("keyword", "text"),
    [
        ("giá sửa cửa sắt", "Giá sửa cửa sắt phụ thuộc vào những gì?"),
        ("cửa sắt giá bao nhiêu", "Cửa sắt giá bao nhiêu? Những điều quyết định"),
        ("chi phí sửa cửa cuốn", "Chi phí sửa cửa cuốn: phụ thuộc vào đâu"),
        ("giá rẻ", "Cửa sắt giá rẻ có bền không? giá rẻ thì nên xem gì"),  # 2 lần trong câu
        ("ＧＩÁ RẺ", "Cửa sắt giá rẻ có bền không?"),  # từ khóa toàn khổ: NFKC như câu
    ],
)
def test_price_words_inside_keyword_only_are_kept(keyword, text):
    assert not mentions_price(text, keyword)


def test_keyword_not_a_string_is_ignored():
    assert mentions_price("Cửa sắt giá rẻ", None)  # type: ignore[arg-type]
    assert find_avoided("Thợ uy tín", ["uy tín"], None) == ["uy tín"]  # type: ignore[arg-type]


AVOID = ("uy tín", "chuyên nghiệp", "100%", "24/7", "xem ngay", "giá cả")


@pytest.mark.parametrize(
    ("text", "keyword", "found"),
    [
        ("Thợ uy tín đến tận nhà", "", ["uy tín"]),
        ("THỢ UY TÍN đến tận nhà", "", ["uy tín"]),
        ("Thợ uy  tín đến tận nhà", "", ["uy tín"]),  # khoảng trắng đôi
        ("Thợ ｕｙ tín đến tận nhà", "", ["uy tín"]),  # toàn khổ
        ("Bảo hành 100% và 24/7", "", ["100%", "24/7"]),
        ("Thợ uy tíntốt", "", []),  # không đứng trọn từ
        ("Sửa cửa uy tín HCM: chọn thợ thế nào", "sửa cửa uy tín hcm", []),
        ("Sửa cửa uy tín HCM: thợ uy tín", "sửa cửa uy tín hcm", ["uy tín"]),  # lần thứ hai
        ("Sửa cửa uy tín HCM: xem ngay", "sửa cửa uy tín hcm", ["xem ngay"]),
        ("Sửa cửa chuyên nghiệp: giá cả ra sao", "sửa cửa chuyên", ["chuyên nghiệp", "giá cả"]),
    ],
)
def test_find_avoided(text, keyword, found):
    """Chỗ khớp vắt qua mép từ khóa («sửa cửa chuyên» + «chuyên nghiệp») vẫn tính."""
    assert find_avoided(text, AVOID, keyword) == found


@pytest.mark.parametrize(
    ("keyword", "text"),
    [
        ("sua cua uy tin hcm", "Sửa cửa uy tín HCM: chọn thợ thế nào cho đúng"),
        ("cua cuon gia re", "Cửa cuốn giá rẻ: nên chọn loại nào"),
        ("CUA CUON GIA RE", "cửa cuốn giá rẻ: nên chọn loại nào"),
        ("cửa cuốn giá rẻ", "Cua cuon gia re: nen chon loai nao"),  # câu không dấu, từ khóa có dấu
    ],
)
def test_keyword_without_accents_still_covers_its_words(keyword, text):
    """SL-T041-3: chỗ nằm trong từ khóa được so không dấu, như ``has_keyword``."""
    assert find_avoided(text, AVOID, keyword) == []
    assert not mentions_price(text, keyword)


def test_keyword_without_accents_does_not_hide_other_words():
    assert find_avoided("Sửa cửa uy tín HCM: thợ uy tín", AVOID, "sua cua uy tin hcm") == ["uy tín"]
    assert mentions_price("Cửa cuốn giá rẻ, giá tốt cho nhà phố", "cua cuon gia re")
    assert mentions_price("Cửa cuốn giá rẻ hơn", "cua cuon")  # «giá rẻ» ngoài từ khóa


def test_avoid_phrases_ignore_blank_and_odd_items():
    assert find_avoided("Thợ uy tín", ["", "   ", "uy tín"]) == ["uy tín"]


def test_accept_ai_uses_avoid_with_keyword_exception():
    title = "Sửa cửa uy tín HCM: chọn thợ thế nào cho đúng?"
    assert accept_ai_title(title, "sửa cửa uy tín hcm", avoid=AVOID) is not None
    assert accept_ai_title(title, "sửa cửa", avoid=AVOID) is None
    assert accept_ai_title(title, "sửa cửa") is not None  # không truyền avoid: như cũ
    desc = DESC.replace("Xem 5", "Thợ uy tín, xem 5")
    assert accept_ai_description(desc, KEYWORD, avoid=AVOID) is None
    assert accept_ai_description(desc, KEYWORD) == desc


# ============================================================ SL-T040-1


def _title(length: int) -> str:
    base = "Cửa sắt bị xệ: nguyên nhân hay gặp và cách xử lý từng bước tại nhà"
    title = base[:length].rstrip()
    while len(title) < length:
        title += "a"
    return title


@pytest.mark.parametrize("length", [49])
def test_title_too_long_for_suffix_is_not_short(length):
    check = check_title(_title(length))
    assert check.level is Level.GOOD
    assert "hơi ngắn" not in check.messages[0] and "dài vừa" in check.messages[0]


@pytest.mark.parametrize(
    ("length", "suffix", "final", "short"),
    [
        (48, None, 60, False),  # ô sửa: gắn được đuôi (48 + 12 = 60), chấm title gửi đi
        (38, None, 50, False),
        (37, None, 49, True),  # 37 + 12 = 49: có đuôi mà vẫn ngắn
        (49, "", 49, True),  # không dùng đuôi: ngưỡng thường
        (49, " | Pro", 55, False),  # đuôi ngắn gắn được
        (45, " | Cơ khí Pro-Metal HCM", 45, False),  # đuôi 23 ký tự không gắn được
        (37, " | Cơ khí Pro-Metal HCM", 60, False),  # 37 + 23 = 60: gắn được
    ],
)
def test_title_suffix_band_depends_on_suffix(length, suffix, final, short):
    check = check_title(_title(length), suffix)
    assert check.level is Level.GOOD
    assert check.length == final and len(check.value) == final
    assert ("hơi ngắn" in check.messages[0]) is short


def test_title_with_suffix_or_too_short_keeps_old_rules():
    with_suffix = _title(37) + BRAND_SUFFIX  # 49 ký tự đã có đuôi: ngưỡng thường
    assert check_title(with_suffix).length == 49
    assert check_title(with_suffix).messages == ("Meta title hơi ngắn: 49 ký tự, nên 50–60 ký tự.",)
    assert check_title(_title(17)).level is Level.WARN  # 17 + 12 = 29: dưới 30 vẫn Cảnh báo
    assert check_title(_title(20), "").level is Level.WARN
    assert check_title("").level is Level.BLOCK


def test_edit_box_title_is_judged_as_sent():
    """SL-T041-2: ô sửa hiện title chưa có đuôi; ``check_title`` chấm title gửi đi
    (``with_brand``): ``value``, ``length`` là của title đó, câu báo nói đã tính cả đuôi."""
    check = check_title(TITLE)  # 45 ký tự, chưa có đuôi
    assert check.value == with_brand(TITLE) == TITLE + BRAND_SUFFIX
    assert check.length == 57 and check.level is Level.GOOD
    assert check.messages == ("Meta title dài vừa: 57 ký tự (tính cả đuôi thương hiệu).",)
    # Đã có đuôi (gợi ý AI, title cuối): như cũ, không thêm ghi chú.
    assert check_title(TITLE + BRAND_SUFFIX).messages == ("Meta title dài vừa: 57 ký tự.",)
    # Đuôi dạng cũ: chấm dạng thống nhất sẽ gửi.
    assert check_title(TITLE + " | Pro Metal").value == TITLE + BRAND_SUFFIX
    # Chặn xét trên chữ đưa vào, không gắn đuôi.
    blocked = check_title("Cửa sắt <b>bị xệ</b> nên làm gì")
    assert blocked.level is Level.BLOCK and BRAND_SUFFIX not in blocked.value


def test_ai_title_of_49_chars_is_accepted_without_suffix():
    title = _title(49)
    assert accept_ai_title(title, KEYWORD) == title
    assert "hơi ngắn" not in check_title(title).messages[0]


# ============================================================ [meta] trong content.toml


def _config(tmp_path, meta: str | None):
    text = CONTENT_CONFIG_FILE.read_text(encoding="utf-8")
    base = text[: text.index("\n# LƯU Ý (T-040")] + "\n"
    path = tmp_path / "content.toml"
    path.write_text(base + ("" if meta is None else "\n[meta]\n" + meta + "\n"), encoding="utf-8")
    return path


def test_load_meta_rules_from_real_config():
    rules = load_meta_rules()
    assert rules.brand_suffix == " | Pro-Metal"
    assert "uy tín" in rules.avoid and "xem ngay" in rules.avoid
    assert resolve_brand_suffix(rules.brand_suffix) == BRAND_SUFFIX


def test_load_meta_rules_missing_section_uses_defaults(tmp_path):
    assert load_meta_rules(_config(tmp_path, None)) == MetaRules()
    assert resolve_brand_suffix(MetaRules().brand_suffix) == BRAND_SUFFIX


@pytest.mark.parametrize(
    ("meta", "suffix", "avoid"),
    [
        ('brand_suffix = ""\navoid = []', "", ()),
        ("brand_suffix = 123", None, ()),
        ("brand_suffix = []", None, ()),
        ('avoid = "uy tín"', None, ("uy tín",)),  # chuỗi đơn: một dòng
        ('avoid = ["  xem   ngay ", "", "24/7"]', None, ("xem ngay", "24/7")),
    ],
)
def test_load_meta_rules_shapes(tmp_path, meta, suffix, avoid):
    assert load_meta_rules(_config(tmp_path, meta)) == MetaRules(suffix, avoid)


@pytest.mark.parametrize("meta", ["avoid = [1, 2]", "avoid = [[]]", "avoid = 5"])
def test_load_meta_rules_bad_avoid_is_an_error(tmp_path, meta):
    with pytest.raises(ContentRulesError, match=r"content\.toml, mục \[meta\]"):
        load_meta_rules(_config(tmp_path, meta))


def test_load_meta_rules_bad_section(tmp_path):
    path = tmp_path / "content.toml"
    path.write_text("meta = 5\n", encoding="utf-8")  # khóa ở gốc, không phải mục [meta]
    with pytest.raises(ContentRulesError, match="meta"):
        load_meta_rules(path)


def test_bad_meta_section_does_not_lock_load_rules(tmp_path):
    path = _config(tmp_path, "avoid = [1, 2]")
    profile = tmp_path / "khong-co-ho-so.md"
    assert load_rules(path, profile) == load_rules(CONTENT_CONFIG_FILE, profile)


# ============================================================ ContentWriter.meta đọc [meta]

RULES = ContentRules(
    business_profile="- Tên thương hiệu: Pro-Metal",
    address="Xưng «chúng tôi»",
    tone="Thân thiện",
    banned=("Hãy cùng tìm hiểu",),
    checklist=(),
)
TASKS = {
    name: TaskConfig(name=name, provider="anthropic", model="claude-opus-5-5")
    for name in ("research", "outline", "write", "rewrite", "review", "meta")
}
ARTICLE = [Section(heading="Mở bài", body="Cửa sắt bị xệ thường do bản lề mòn.")]


class _FakeMeta:
    def __init__(self, titles, descriptions):
        self.result = MetaSuggestions(titles=list(titles), descriptions=list(descriptions))

    def generate(self, task, *, system, prompt, schema):
        return self.result


def _writer(monkeypatch, titles, descriptions, meta_rules=None):
    provider = _FakeMeta(titles, descriptions)
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: provider)
    return ContentWriter(AIRouter(TASKS, Settings()), RULES, meta_rules)


def test_writer_meta_drops_avoid_phrases_from_config(monkeypatch):
    bad = "Cửa sắt bị xệ: xem ngay cách tự chỉnh bản lề"
    writer = _writer(monkeypatch, [bad, TITLE], [DESC.replace("Xem 5", "Thợ uy tín. Xem 5"), DESC])
    result = writer.meta(KEYWORD, "Bài", ARTICLE)
    assert result.titles == [TITLE + BRAND_SUFFIX]
    assert result.descriptions == [DESC]


def test_writer_meta_uses_given_meta_rules(monkeypatch):
    bad = "Cửa sắt bị xệ: bảo hành tận tình cho từng nhà"
    rules = MetaRules(brand_suffix=" | Cơ khí PM", avoid=("tận tình",))
    writer = _writer(monkeypatch, [bad, TITLE], [DESC], rules)
    result = writer.meta(KEYWORD, "Bài", ARTICLE)
    assert result.titles == [TITLE + " | Cơ khí PM"]
    # brand_suffix truyền thẳng vẫn thắng cấu hình (như trước T-041).
    assert writer.meta(KEYWORD, "Bài", ARTICLE, brand_suffix="").titles == [TITLE]


def test_writer_meta_reports_bad_meta_section(monkeypatch, tmp_path):
    import seo_app.content.workflow as workflow

    path = _config(tmp_path, "avoid = [1, 2]")
    monkeypatch.setattr(workflow, "load_meta_rules", lambda: load_meta_rules(path))
    writer = _writer(monkeypatch, [TITLE], [DESC])
    with pytest.raises(ContentRulesError, match=r"mục \[meta\]"):
        writer.meta(KEYWORD, "Bài", ARTICLE)


@pytest.mark.parametrize(
    ("suffix", "ranges", "short_example"),
    [
        (None, "40-48 hoặc 50-60", True),  # mặc định « | Pro-Metal» (12 ký tự): như T-040
        (" | Pro-Metal", "40-48 hoặc 50-60", True),
        ("", "50-60", False),  # không gắn đuôi
        (" | Cơ khí Pro-Metal HCM", "29-37 hoặc 50-60", False),  # 23 ký tự
        (" | PM", "50-60", True),  # đuôi ngắn: title 50-60 nào cũng gắn được
    ],
)
def test_meta_prompt_follows_brand_suffix(suffix, ranges, short_example):
    """SL-T041-7: lời dặn nói đúng đuôi đang dùng; G1: bỏ câu «49 ký tự … hơi ngắn» đã cũ."""
    text = prompts.meta_prompt(KEYWORD, "Bài", ARTICLE, brand_suffix=suffix)
    block = " ".join(text[text.index("- titles:") : text.index("- descriptions:")].split())
    assert f"mỗi cái {ranges} ký tự" in block
    assert "49 ký tự" not in block
    assert "KHÔNG tự viết tên thương hiệu" in block
    assert ("(ngắn, còn chỗ cho đuôi thương hiệu)" in block) is short_example
    resolved = resolve_brand_suffix(suffix)
    if resolved:
        assert f"«{resolved}» ({len(resolved)} ký tự)" in block
    else:
        assert "tự gắn đuôi" not in block


def test_writer_meta_prompt_uses_config_suffix(monkeypatch):
    seen = []

    class Recorder(_FakeMeta):
        def generate(self, task, *, system, prompt, schema):
            seen.append(prompt)
            return self.result

    provider = Recorder([TITLE], [DESC])
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: provider)
    rules = MetaRules(brand_suffix=" | Cơ khí Pro-Metal HCM")
    writer = ContentWriter(AIRouter(TASKS, Settings()), RULES, rules)
    writer.meta(KEYWORD, "Bài", ARTICLE)
    assert "mỗi cái 29-37 hoặc 50-60 ký tự" in " ".join(seen[-1].split())


def test_missing_meta_and_links_tasks_have_examples():
    """Góp ý G5: thiếu [tasks.meta], [tasks.links] thì câu báo có mẫu để chép (như việc alt)."""
    for name in ("meta", "links"):
        message = missing_task_message(name)
        assert f"[tasks.{name}]" in message and 'provider = "anthropic"' in message
        assert "web_search" not in message


# ============================================================ hàm cho giao diện


def _index(*items) -> SiteIndex:
    from datetime import datetime
    from zoneinfo import ZoneInfo

    return SiteIndex(
        site="https://suachuacuasat.com",
        fetched_at=datetime(2026, 10, 26, 9, 0, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")),
        items=tuple(items),
    )


def test_site_posts_from_index_feeds_duplicate_checks():
    item = PublishedItem(
        id=7,
        type="post",
        slug="cua-sat-bi-xe",
        link="https://suachuacuasat.com/cua-sat-bi-xe/",
        title="Cửa sắt bị xệ: dấu hiệu sớm và cách xử lý gọn",
        meta_title="",
        meta_desc=DESC,
    )
    posts = site_posts(_index(item))
    assert [(p.id, p.slug, p.meta_description) for p in posts] == [(7, "cua-sat-bi-xe", DESC)]
    assert check_title_duplicates(TITLE + BRAND_SUFFIX, posts).level is Level.BLOCK
    assert site_posts(None) == []
    assert check_title_duplicates(TITLE, site_posts(None)).level is Level.GOOD


def test_siteseo_copy_gives_final_values():
    copy = siteseo_copy(f"  {TITLE} ", DESC + "​", "cua-sat-bi-xe")
    assert copy.title == TITLE + BRAND_SUFFIX
    assert copy.description == DESC
    assert copy.slug == "cua-sat-bi-xe"
    assert [c.field for c in copy.checks] == ["title", "description", "slug"]
    assert siteseo_copy(TITLE, DESC, "x", suffix="").title == TITLE


@pytest.mark.parametrize(
    ("title", "description", "slug", "blocked"),
    [
        ("Cửa sắt <b>bị xệ</b> tại nhà nhanh gọn", DESC, "cua-sat", "title"),
        (TITLE, "Mô tả %%sitetitle%% " + DESC, "cua-sat", "description"),
        (TITLE, DESC, "../etc/passwd", "slug"),
        (TITLE, DESC, "Cửa-Sắt", "slug"),
        ("", DESC, "cua-sat", "title"),
    ],
)
def test_siteseo_copy_refuses_blocked_fields(title, description, slug, blocked):
    copy = siteseo_copy(title, description, slug)
    assert getattr(copy, blocked) is None
    others = {"title", "description", "slug"} - {blocked}
    assert all(getattr(copy, name) is not None for name in others)
    check = next(c for c in copy.checks if c.field == blocked)
    assert check.level is Level.BLOCK and check.messages


def test_control_chars_blocked_on_every_path_but_whitespace_is_not():
    """Lượt 3 (lỗi lùi do ``normalize_meta`` bỏ ký tự điều khiển): ô sửa → các bản trong nháp →
    bộ kiểm → chép SiteSEO → client WordPress đều Chặn chữ có ký tự điều khiển, kèm câu báo; tab,
    xuống dòng thì vẫn chỉ được gộp thành dấu cách."""
    from seo_app.storage.drafts import DraftMetaVersions

    raw = "Cửa sắt bị xệ\x1b: dấu hiệu sớm và cách xử lý"
    kept = DraftMetaVersions(versions=[raw]).text  # như giao diện lưu bản người dùng sửa
    assert "\x1b" in kept
    assert check_title(kept).level is Level.BLOCK
    assert siteseo_copy(kept, DESC, "cua-sat-bi-xe").title is None
    assert "điều khiển" in seo_write_problem("Tiêu đề SEO", raw)
    spaced = "Cửa sắt bị xệ:\tdấu hiệu sớm\nvà cách xử lý"
    assert seo_write_problem("Tiêu đề SEO", spaced) == ""
    assert check_title(DraftMetaVersions(versions=[spaced]).text).level is Level.GOOD


def test_seo_write_problem_uses_client_rules():
    """SL-T041-1: cùng bộ kiểm với client WordPress (``set_seo_meta``); câu lý do không chép chữ."""
    assert seo_write_problem("Meta title", TITLE) == ""
    for bad in ("Cửa [gallery] xệ", "Cửa <1> xệ", "Giảm &#37 hôm nay", "Cửa [<>x id=1] xệ"):
        problem = seo_write_problem("Meta title", bad)
        assert problem.startswith("Meta title ") and "gallery" not in problem


def test_siteseo_copy_and_ai_description_refuse_shortcode():
    desc = DESC.replace("Xem 5", "Xem [gallery] 5")
    copy = siteseo_copy(TITLE, desc, "cua-sat-bi-xe")
    assert copy.description is None and copy.title == TITLE + BRAND_SUFFIX
    check = copy.checks[1]
    assert check.level is Level.BLOCK and "shortcode" in check.messages[0]
    assert accept_ai_description(desc, KEYWORD) is None
    assert accept_ai_description(DESC, KEYWORD) == DESC


def test_filter_titles_passes_avoid_through():
    titles = ["Cửa sắt bị xệ: thợ chuyên nghiệp chỉnh bản lề", TITLE]
    assert filter_ai_titles(titles, KEYWORD, avoid=AVOID) == [TITLE + BRAND_SUFFIX]

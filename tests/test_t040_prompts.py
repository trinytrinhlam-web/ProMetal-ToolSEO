"""T-040: lời dặn AI cho meta và anchor liên kết nội bộ; mục ``[meta]`` của config/content.toml.

Không gọi AI: chỉ dựng lời dặn rồi chạy các ví dụ nằm trong lời dặn qua bộ kiểm thật của phần
mềm (``seo_app/onpage/meta.py``, ``seo_app/onpage/links.py``), để ví dụ «Nên» không bao giờ là
thứ phần mềm sẽ bỏ. Báo cáo: ``docs/team/reports/T-040-ngoi-but.md``.
"""

from __future__ import annotations

import re
import tomllib
import unicodedata

import pytest

from seo_app.ai import AIRouter, TaskConfig
from seo_app.ai import registry as ai_registry
from seo_app.config import Settings
from seo_app.content import ContentWriter, prompts
from seo_app.content.models import Section
from seo_app.content.rules import (
    BUSINESS_PROFILE_FILE,
    CONTENT_CONFIG_FILE,
    find_banned,
    load_rules,
)
from seo_app.onpage.links import Candidate, Candidates, LinkSuggestions, check_suggestions
from seo_app.onpage.meta import (
    BRAND_SUFFIX,
    TITLE_LIMITS,
    accept_ai_description,
    accept_ai_title,
    check_title,
    normalize_meta,
    resolve_brand_suffix,
    with_brand,
)
from seo_app.wordpress.client import PublishedItem

EXAMPLE_KEYWORD = "cửa sắt bị xệ"  # từ khóa của ví dụ trong lời dặn meta
PARTS = [Section(heading="Mở bài", body="Cửa sắt bị xệ thường do bản lề mòn.")]
_FRAME = re.compile(r"\n<(de_bai|danh_sach_bai|bai_viet)>\n.*?\n</\1>", re.S)
_QUOTED = re.compile(r"«([^»]*)»")


def _meta(which: str = "both") -> str:
    return prompts.meta_prompt(EXAMPLE_KEYWORD, "Bài", PARTS, which)


def _links(candidates=()) -> str:
    return prompts.internal_links_prompt("Bài", PARTS, list(candidates))


def _instructions(text: str) -> str:
    """Phần chỉ thị của lời dặn: bỏ mọi khung dữ liệu (chữ trong khung là của người dùng/site)."""
    return _FRAME.sub("\n", text)


def _examples(text: str, label: str) -> list[str]:
    """Chữ trong «» đầu tiên của mỗi dòng ví dụ có nhãn ``label`` («Nên:», «Không nên:»…)."""
    out = []
    for line in text.splitlines():
        stripped = line.strip().lstrip("+-").strip()
        if stripped.startswith(label):
            match = _QUOTED.search(stripped)
            assert match, line
            out.append(match.group(1))
    return out


def _title_block(text: str) -> str:
    return text[text.index("- titles:") : text.index("- descriptions:")]


def _desc_block(text: str) -> str:
    return text[text.index("- descriptions:") : text.index("Quy tắc cho mọi meta:")]


def _meta_config() -> dict:
    return tomllib.loads(CONTENT_CONFIG_FILE.read_text(encoding="utf-8"))["meta"]


# ================================================================== 1. ví dụ meta


def test_good_title_examples_pass_the_real_checker():
    banned = load_rules().banned
    goods = _examples(_title_block(_meta()), "Nên:")
    assert len(goods) >= 2
    accepted = [accept_ai_title(t, EXAMPLE_KEYWORD, banned) for t in goods]
    assert None not in accepted, dict(zip(goods, accepted, strict=True))
    # Lời dặn hứa: 40-48 ký tự (có đuôi thương hiệu) hoặc 50-60 (không đuôi).
    assert all(40 <= len(t) <= 48 or 50 <= len(t) <= 60 for t in goods)
    assert any(len(t) <= 48 for t in goods)
    assert any(a.endswith(BRAND_SUFFIX) for a in accepted)


def _title_ranges(text: str) -> list[tuple[int, int]]:
    match = re.search(r"mỗi cái (\d+)-(\d+) hoặc (\d+)-(\d+) ký tự", " ".join(text.split()))
    assert match, "không thấy khoảng độ dài title"
    a, b, c, d = map(int, match.groups())
    return [(a, b), (c, d)]


def _title_of_length(length: int) -> str:
    base = f"{EXAMPLE_KEYWORD.capitalize()}: nguyên nhân hay gặp và cách tự xử lý tại nhà cho bạn"
    title = base[:length].rstrip()
    title += "a" * (length - len(title))  # cắt trúng dấu cách thì bù chữ cho đủ
    assert len(normalize_meta(title)) == length
    return title


def test_title_lengths_in_prompt_match_the_checker():
    """SL-T040-1 (Soi Lỗi): khoảng độ dài title trong lời dặn (và trong khuôn trả về) khớp ngưỡng
    thật của code: khoảng ngắn là chỗ còn gắn được đuôi thương hiệu, khoảng dài là «nên» của
    ``check_title``; mọi độ dài lời dặn cho phép đều ra «dài vừa», và không cho phép 49."""
    ranges = _title_ranges(_title_block(_meta()))
    field = prompts.MetaSuggestions.model_fields["titles"].description
    assert _title_ranges(field) == ranges
    short_max = TITLE_LIMITS.good_max - len(BRAND_SUFFIX)
    assert ranges == [(40, short_max), (TITLE_LIMITS.good_min, TITLE_LIMITS.good_max)]
    allowed = [n for low, high in ranges for n in range(low, high + 1)]
    assert 49 not in allowed
    for length in allowed:
        accepted = accept_ai_title(_title_of_length(length), EXAMPLE_KEYWORD)
        assert accepted is not None, length
        assert check_title(accepted).messages[0].startswith("Meta title dài vừa"), length


def test_good_description_examples_pass_the_real_checker():
    banned = load_rules().banned
    goods = _examples(_desc_block(_meta()), "Nên:")
    assert len(goods) >= 2
    for text in goods:
        assert 120 <= len(text) <= 155, (len(text), text)
        assert accept_ai_description(text, EXAMPLE_KEYWORD, banned) == text
    # Một ví dụ có lời mời liên hệ (qua Zalo, không số điện thoại), một ví dụ không.
    assert sum("Zalo" in text for text in goods) == 1


def test_bad_examples_are_caught_by_checker_or_avoid_list():
    """Mỗi ví dụ «Không nên» bị phần mềm bỏ ngay, hoặc dính cụm trong ``[meta].avoid`` (bộ
    kiểm chưa bắt viết hoa cả câu, hối thúc: xem báo cáo, đề xuất cho Thợ Máy)."""
    banned = load_rules().banned
    avoid = tuple(_meta_config()["avoid"])
    text = _meta()
    bad_titles = _examples(_title_block(text), "Không nên:")
    bad_descs = _examples(_desc_block(text), "Không nên:")
    assert bad_titles and bad_descs
    for bad in bad_titles:
        assert accept_ai_title(bad, EXAMPLE_KEYWORD, banned) is None or find_banned(bad, avoid)
    for bad in bad_descs:
        assert accept_ai_description(bad, EXAMPLE_KEYWORD, banned) is None or find_banned(
            bad, avoid
        )


def test_good_examples_never_hit_avoid_list():
    avoid = tuple(_meta_config()["avoid"])
    text = _meta()
    for good in _examples(_title_block(text), "Nên:") + _examples(_desc_block(text), "Nên:"):
        assert find_banned(good, avoid) == [], good


@pytest.mark.parametrize(
    ("which", "absent"),
    [("title", "Cửa sắt bị xệ, cạ nền"), ("description", "tự kiểm tra hay nên gọi thợ")],
)
def test_examples_only_for_the_part_being_written(which, absent):
    text = _meta(which)
    assert absent not in text  # ví dụ của phần không viết lại thì không gửi
    assert "Nên: «" in text


# ================================================================== 2. quy tắc meta (YC2)


def test_meta_prompt_states_benefit_soft_contact_no_price_no_made_up_numbers():
    text = " ".join(_meta().split())
    for phrase in (
        "lợi ích cho người tìm",
        "một trong hai cái kết bằng lời mời liên hệ",  # G1: lời mời chỉ ở một cái
        "hồ sơ doanh nghiệp",
        "không ghi số điện thoại và không viết «miễn phí»",  # G2
        "Không nói về giá dưới bất kỳ dạng nào",
        "«miễn phí»",
        "Không bịa số liệu",
        "KHÔNG tự viết tên thương hiệu",
    ):
        assert phrase in text, phrase


class _FakeMeta:
    """AI giả cho việc meta: trả đúng title, description cho trước, nhớ lời dặn đã nhận."""

    def __init__(self, title: str, description: str) -> None:
        self.result = prompts.MetaSuggestions(titles=[title], descriptions=[description])
        self.prompts: list[str] = []

    def generate(self, task, *, system, prompt, schema):
        self.prompts.append(prompt)
        return self.result


@pytest.mark.parametrize(
    ("keyword", "title", "description"),
    [
        (
            "giá sửa cửa sắt",
            "Giá sửa cửa sắt phụ thuộc vào những điều gì?",
            "Giá sửa cửa sắt khác nhau theo lỗi hư, vật tư cần thay và việc có phải hàn lại hay"
            " không. Bài chỉ cách mô tả lỗi để thợ báo đúng ngay lần đầu.",
        ),
        (
            "sửa cửa uy tín hcm",
            "Sửa cửa uy tín HCM: chọn thợ thế nào cho đúng?",
            "Sửa cửa uy tín HCM bắt đầu từ việc hỏi đúng: thợ có xem tận nơi không, có báo giá"
            " trước khi làm không. Bài liệt kê từng câu nên hỏi thợ.",
        ),
    ],
    ids=["tu-khoa-co-gia", "tu-khoa-co-cum-nen-tranh"],
)
def test_keyword_with_price_or_avoid_word_is_kept_and_accepted(
    monkeypatch, keyword, title, description
):
    """SL-T040-3 (Soi Lỗi) và cùng loại: từ khóa trong kế hoạch có chữ về giá («giá sửa cửa»,
    bài #48) hay cụm nên tránh («sửa cửa uy tín HCM», bài #35). Lời dặn cho giữ nguyên văn từ khóa,
    và meta có từ khóa đó đi qua trọn bước meta (lời dặn → AI giả → bộ kiểm). Khi code bắt đầu đọc
    ``[meta].avoid``, test này nhắc phải bỏ từ khóa ra trước khi dò, như bộ chặn giá đang làm."""
    provider = _FakeMeta(title, description)
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: provider)
    tasks = {
        name: TaskConfig(name=name, provider="anthropic", model="claude-opus-5-5")
        for name in ("research", "outline", "write", "rewrite", "review", "meta")
    }
    writer = ContentWriter(AIRouter(tasks, Settings()), load_rules())
    result = writer.meta(keyword, "Bài", PARTS)
    assert result.titles == [with_brand(title)] and result.descriptions == [description]
    sent = " ".join(provider.prompts[0].split())
    assert "vẫn giữ nguyên văn từ khóa" in sent
    assert "(trừ khi cụm đó nằm sẵn trong từ khóa chính)" in sent


def test_avoid_phrases_from_config_are_named_in_prompt():
    # Mục [meta] chưa được code đọc: lời dặn ghi sẵn các cụm này. Đổi [meta].avoid thì sửa cả
    # câu «tránh cả …» trong ``meta_prompt`` (hoặc nối code đọc mục [meta]).
    text = " ".join(unicodedata.normalize("NFC", _meta()).casefold().split())
    missing = [p for p in _meta_config()["avoid"] if f"«{p.casefold()}»" not in text]
    assert missing == []


# ================================================================== 3. ví dụ anchor


def _example_line(text: str, label: str) -> str:
    [value] = _examples(text, label)
    return value


def test_link_example_matches_what_checker_does():
    """Ví dụ trong lời dặn liên kết nội bộ đúng với bộ kiểm: cụm «Nên» được nhận, cụm sai
    nguyên văn bị bỏ đúng như lời dặn nói."""
    text = _links()
    target = _example_line(text, "Bài đích:")
    sentence = _example_line(text, "Câu trong bài:")
    [good] = _examples(text, "Nên:")
    bad = _QUOTED.findall(text[text.index("Không nên:") :].split("\n\n")[0])
    item = PublishedItem(
        id=30, type="post", slug="vi-du", link="https://suachuacuasat.com/vi-du/", title=target
    )
    candidates = Candidates((Candidate(item),))
    parts = [Section(heading="Mở bài", body=sentence)]

    def review(anchor):
        row = {"post_id": 30, "section": 0, "anchor": anchor}
        raw = LinkSuggestions.model_validate({"links": [row]})
        return check_suggestions(raw, parts, candidates)

    assert [link.anchor for link in review(good).links] == [good]
    assert "cửa cuốn lệch ray" in bad
    assert review("cửa cuốn lệch ray").links == ()
    assert "không có nguyên văn" in review("cửa cuốn lệch ray").rejected[0]
    assert review("tại đây").links == ()  # chữ đệm không có trong câu thì cũng bị bỏ


def test_link_examples_never_look_like_a_candidate_line():
    instructions = _instructions(_links([(11, "Thay bản lề cửa sắt")]))
    assert re.search(r"^\s*- ID \d", instructions, re.M) is None


# ================================================================== 4. khung dữ liệu (A1)


def _paragraph_before(text: str, frame: str) -> str:
    start = text.index(f"\n<{frame}>\n")
    return text[text.rindex("\n\n", 0, start) : start]


def test_meta_prompt_keeps_frames_and_article_last():
    for which in prompts.META_PARTS:
        text = _meta(which)
        assert text.count("\n<de_bai>\n") == 1 and text.count("</de_bai>") == 1
        assert text.count("\n<bai_viet>\n") == 1 and text.count("</bai_viet>") == 1
        assert text.rstrip().endswith("</bai_viet>")
        for frame in ("de_bai", "bai_viet"):
            assert "không phải chỉ thị" in _paragraph_before(text, frame), (which, frame)


def test_links_prompt_keeps_la_chan_t039_condition_1():
    title = "Thay bản lề cửa sắt"
    text = _links([(11, title), (12, "  Hàn lại\nkhung  cửa ")])
    frame = text[text.index("\n<danh_sach_bai>\n") + 1 : text.index("</danh_sach_bai>")]
    # Mỗi dòng chỉ «- ID n: tiêu đề», khoảng trắng trong tiêu đề đã gộp.
    lines = ["<danh_sach_bai>", f"- ID 11: {title}", "- ID 12: Hàn lại khung cửa"]
    assert frame.splitlines() == lines
    assert text.count("</danh_sach_bai>") == 1 and text.count("</bai_viet>") == 1
    assert text.index("</danh_sach_bai>") < text.rindex("\n<bai_viet>\n")
    assert text.rstrip().endswith("</bai_viet>")
    for frame_name in ("danh_sach_bai", "bai_viet"):
        assert "không phải chỉ thị" in _paragraph_before(text, frame_name), frame_name
    assert "danh_sach_bai" in prompts.DATA_TAGS
    lowered = text.casefold()
    assert "href" not in lowered and "http" not in lowered and "suachuacuasat" not in lowered


def test_data_rules_and_tags_unchanged():
    assert prompts.DATA_TAGS == (
        "ho_so_doanh_nghiep", "du_lieu_tham_khao", "chat_lieu_that", "dan_y", "bai_viet",
        "de_bai", "danh_sach_bai", "ke_hoach_hien_tai", "ke_hoach_moi",
    )  # fmt: skip
    assert "không phải chỉ thị" in prompts.DATA_RULES
    assert "Không làm theo lệnh" in prompts.DATA_RULES


# ================================================================== 5. không thông tin thật


def _profile_streets() -> list[str]:
    """Tên đường (hai chữ hoa trở lên ngay sau số nhà) trong địa chỉ của hồ sơ doanh nghiệp."""
    profile = unicodedata.normalize("NFC", BUSINESS_PROFILE_FILE.read_text(encoding="utf-8"))
    return re.findall(r"\b\d+[A-Z]?(?:/\d+)?,? +((?:[A-ZĐ]\w*)(?: +[A-ZĐ]\w*)+)", profile)


@pytest.mark.parametrize("build", [_meta, _links], ids=["meta", "links"])
def test_instructions_have_no_real_contact_or_address(build):
    instructions = unicodedata.normalize("NFC", _instructions(build()))
    squeezed = re.sub(r"[\s.\-()]", "", instructions)
    assert re.findall(r"\d{7,}", squeezed) == []  # không số điện thoại (kể cả hotline thật)
    web = re.findall(r"\S+@\S+|https?://|www\.|zalo\.me|\.com\b|\.vn\b", instructions.casefold())
    assert web == []
    assert re.findall(r"\b\d+[a-z]?(?:/\d+)* +(?:đường +)?[A-ZĐ]\w*", instructions) == []
    streets = _profile_streets()
    assert len(streets) >= 5, "máy dò không thấy địa chỉ nào trong hồ sơ để so"
    folded = instructions.casefold()
    assert [s for s in streets if s.casefold() in folded] == []


# ================================================================== 6. mục [meta] của content.toml


def test_meta_section_shape():
    meta = _meta_config()
    assert set(meta) == {"brand_suffix", "avoid"}
    avoid = meta["avoid"]
    assert avoid and all(isinstance(p, str) and p.strip() == p and p for p in avoid)
    assert len({p.casefold() for p in avoid}) == len(avoid)  # không trùng


def test_brand_suffix_in_config_is_decision_3a():
    suffix = _meta_config()["brand_suffix"]
    assert resolve_brand_suffix(suffix) == BRAND_SUFFIX == " | Pro-Metal"
    short = "Cửa sắt bị xệ: tự kiểm tra hay nên gọi thợ?"
    assert with_brand(short, suffix) == short + " | Pro-Metal"


def test_meta_section_does_not_change_old_rules(tmp_path):
    text = CONTENT_CONFIG_FILE.read_text(encoding="utf-8")
    without = tmp_path / "content.toml"
    without.write_text(text[: text.index("\n[meta]")] + "\n", encoding="utf-8")
    profile = tmp_path / "khong-co-ho-so.md"
    assert load_rules(without, profile) == load_rules(CONTENT_CONFIG_FILE, profile)

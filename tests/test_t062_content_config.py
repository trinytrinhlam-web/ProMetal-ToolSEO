"""T-062: đọc ``[images]`` và ``[alt]`` của ``config/content.toml`` chịu lỗi như T-010.

Thiếu mục, thiếu khóa thì dùng mặc định 80 / 1600 / 125 / 200. Sai dạng thì báo
``ContentRulesError`` tiếng Việt, nêu ``config/content.toml`` và tên mục, không có đường dẫn đầy
đủ trên máy; không nhận ``true`` / ``false`` làm số (Lá Chắn T-051 C5). Không gọi mạng.
"""

import pytest

import seo_app.content.rules as rules_module
from seo_app.content.rules import (
    ALT_MIN_CHARS,
    IMAGE_EDGE_MAX,
    IMAGE_EDGE_MIN,
    AltExample,
    AltRules,
    ContentRulesError,
    ImageSettings,
    load_alt_rules,
    load_image_settings,
    load_rules,
)

NO_PROFILE = "khong-co-ho-so.md"
OLD = '[voice]\ntone = "thân thiện"\n[review]\nchecklist = ["Cụ thể"]\n'


def _content(tmp_path, body: str | bytes):
    path = tmp_path / "content.toml"
    if isinstance(body, str):
        path.write_text(body, encoding="utf-8")
    else:
        path.write_bytes(body)
    return path


def _message(exc: pytest.ExceptionInfo, tmp_path) -> str:
    message = str(exc.value)
    assert "config/content.toml" in message
    assert str(tmp_path) not in message and "\\" not in message  # không lộ đường dẫn máy
    return message


# ------------------------------------------------------------------ file thật của dự án


def test_project_content_toml_images_and_alt():
    assert load_image_settings() == ImageSettings(webp_quality=80, max_edge_px=1600)
    alt = load_alt_rules()
    assert (alt.max_chars, alt.caption_max_chars) == (125, 200)
    assert len(alt.rules) == 16 and alt.rules[-1].startswith("Chú thích (caption)")
    assert "Hình ảnh" in alt.bad_starts
    assert len(alt.examples) == 6
    assert all(e.image and e.good and e.bad and e.why for e in alt.examples)
    assert alt.examples[4].good.startswith("Minh họa")


def test_reading_new_sections_does_not_change_old_rules(tmp_path):
    real = rules_module.CONTENT_CONFIG_FILE.read_text(encoding="utf-8")
    without = _content(tmp_path, real[: real.index("\n[images]")] + "\n")
    profile = tmp_path / NO_PROFILE
    assert load_rules(without, profile) == load_rules(rules_module.CONTENT_CONFIG_FILE, profile)


# ------------------------------------------------------------------ thiếu thì dùng mặc định


@pytest.mark.parametrize(
    "body",
    [OLD, OLD + "[images]\n", OLD + "[alt]\n", OLD + "[images]\nkhac = 1\n[alt]\nkhac = 2\n"],
    ids=["thieu-ca-hai", "images-rong", "alt-rong", "khoa-la"],
)
def test_missing_sections_or_keys_use_defaults(tmp_path, body):
    path = _content(tmp_path, body)
    assert load_image_settings(path) == ImageSettings(80, 1600)
    assert load_alt_rules(path) == AltRules(125, 200, (), (), ())


def test_partial_sections_keep_other_defaults(tmp_path):
    path = _content(tmp_path, "[images]\nwebp_quality = 75\n[alt]\ncaption_max_chars = 150\n")
    assert load_image_settings(path) == ImageSettings(webp_quality=75, max_edge_px=1600)
    assert load_alt_rules(path) == AltRules(max_chars=125, caption_max_chars=150)


def test_bom_file_loads(tmp_path):
    path = _content(tmp_path, b"\xef\xbb\xbf[images]\nmax_edge_px = 1200\n")
    assert load_image_settings(path).max_edge_px == 1200


# ------------------------------------------------------------------ [images] sai dạng


@pytest.mark.parametrize(
    "value",
    ["true", "false", '"80"', "80.0", "0", "101", "-5", "[80]", "{a = 1}"],
)
def test_bad_webp_quality(tmp_path, value):
    with pytest.raises(ContentRulesError) as info:
        load_image_settings(_content(tmp_path, f"[images]\nwebp_quality = {value}\n"))
    message = _message(info, tmp_path)
    assert "[images]" in message and "webp_quality" in message and "1 đến 100" in message


@pytest.mark.parametrize(
    "value", ["true", "false", '"1600"', "1600.5", "0", "-1", str(IMAGE_EDGE_MIN - 1),
              str(IMAGE_EDGE_MAX + 1)],
)  # fmt: skip
def test_bad_max_edge_px(tmp_path, value):
    with pytest.raises(ContentRulesError) as info:
        load_image_settings(_content(tmp_path, f"[images]\nmax_edge_px = {value}\n"))
    message = _message(info, tmp_path)
    assert "[images]" in message and "max_edge_px" in message


@pytest.mark.parametrize("value", [1, 100])
def test_webp_quality_edges_are_accepted(tmp_path, value):
    path = _content(tmp_path, f"[images]\nwebp_quality = {value}\n")
    assert load_image_settings(path).webp_quality == value


@pytest.mark.parametrize("value", [IMAGE_EDGE_MIN, IMAGE_EDGE_MAX])
def test_max_edge_px_edges_are_accepted(tmp_path, value):
    path = _content(tmp_path, f"[images]\nmax_edge_px = {value}\n")
    assert load_image_settings(path).max_edge_px == value


@pytest.mark.parametrize("body", ['images = "80"\n', "images = 80\n", "[[images]]\na = 1\n"])
def test_images_not_a_section(tmp_path, body):
    with pytest.raises(ContentRulesError) as info:
        load_image_settings(_content(tmp_path, body))
    assert "[images]" in _message(info, tmp_path)


# ------------------------------------------------------------------ [alt] sai dạng


@pytest.mark.parametrize("key", ["max_chars", "caption_max_chars"])
@pytest.mark.parametrize(
    "value", ["true", "false", '"125"', "125.0", "0", "-3", str(ALT_MIN_CHARS - 1), "[125]"]
)
def test_bad_alt_limits(tmp_path, key, value):
    with pytest.raises(ContentRulesError) as info:
        load_alt_rules(_content(tmp_path, f"[alt]\n{key} = {value}\n"))
    message = _message(info, tmp_path)
    assert "[alt]" in message and key in message


def test_alt_limit_message_names_the_right_key(tmp_path):
    # «max_chars» nằm trong «caption_max_chars»: câu báo phải nêu đúng khóa sai.
    with pytest.raises(ContentRulesError) as info:
        load_alt_rules(_content(tmp_path, "[alt]\nmax_chars = 125\ncaption_max_chars = true\n"))
    assert "caption_max_chars phải là số nguyên" in str(info.value)
    with pytest.raises(ContentRulesError) as info:
        load_alt_rules(_content(tmp_path, '[alt]\nmax_chars = "125"\n'))
    assert ": max_chars phải là số nguyên" in str(info.value)


def test_alt_min_and_large_limits_are_accepted(tmp_path):
    path = _content(tmp_path, f"[alt]\nmax_chars = {ALT_MIN_CHARS}\ncaption_max_chars = 5000\n")
    assert (load_alt_rules(path).max_chars, load_alt_rules(path).caption_max_chars) == (
        ALT_MIN_CHARS,
        5000,
    )


@pytest.mark.parametrize(
    ("body", "word"),
    [
        ("[alt]\nrules = [1, 2]\n", "rules"),
        ('[alt]\nrules = {a = "b"}\n', "rules"),
        ("[alt]\nbad_starts = [true]\n", "bad_starts"),
        ('alt = "ngắn thôi"\n', "[alt]"),
        ('[alt]\nexamples = "một ví dụ"\n', "[[alt.examples]]"),
        ("[alt]\nexamples = [1, 2]\n", "[[alt.examples]]"),
        ('[[alt.examples]]\nanh = "Ảnh thật"\ntot = 5\n', "«tot»"),
        ('[[alt.examples]]\nanh = "Ảnh thật"\n', "«tot»"),
        ('[[alt.examples]]\ntot = "Cửa cuốn kẹt"\n', "«anh»"),
        ('[[alt.examples]]\nanh = "Ảnh"\ntot = "Cửa"\nxau = "Ảnh cửa"\n', "«vi_sao»"),
        ('[[alt.examples]]\nanh = "Ảnh"\ntot = "Cửa"\nxau = "Ảnh cửa"\nvi_sao = "  "\n', "vi_sao"),
    ],
)
def test_bad_alt_shape(tmp_path, body, word):
    with pytest.raises(ContentRulesError) as info:
        load_alt_rules(_content(tmp_path, body))
    message = _message(info, tmp_path)
    assert word in message and ("[alt" in message)


def test_alt_example_numbers_the_broken_example(tmp_path):
    body = (
        '[[alt.examples]]\nanh = "Ảnh 1"\ntot = "Cửa 1"\n'
        '[[alt.examples]]\nanh = "Ảnh 2"\ntot = "Cửa 2"\nxau = "Ảnh cửa"\n'
    )
    with pytest.raises(ContentRulesError, match="thứ 2"):
        load_alt_rules(_content(tmp_path, body))


def test_alt_text_is_single_line_and_rule_string_becomes_list(tmp_path):
    body = (
        '[alt]\nrules = "Một  quy tắc\\nhai dòng"\nbad_starts = ["Ảnh", "  "]\n'
        '[[alt.examples]]\nanh = "Ảnh\\nthật"\nthe = ""\ntot = "Cửa   cuốn"\n'
    )
    alt = load_alt_rules(_content(tmp_path, body))
    assert alt.rules == ("Một quy tắc hai dòng",)
    assert alt.bad_starts == ("Ảnh",)
    assert alt.examples == (AltExample(image="Ảnh thật", tags="", good="Cửa cuốn"),)


# ------------------------------------------------------------------ file hỏng (như T-010)


@pytest.mark.parametrize("loader", [load_image_settings, load_alt_rules])
def test_broken_file_gives_vietnamese_error(tmp_path, loader):
    ansi = _content(tmp_path, ("# ghi chú\n[alt]\nmax_chars = 125\n").encode("cp1258"))
    with pytest.raises(ContentRulesError, match="UTF-8"):
        loader(ansi)
    with pytest.raises(ContentRulesError, match="cú pháp"):
        loader(_content(tmp_path, "[alt\n"))
    with pytest.raises(ContentRulesError) as info:
        loader(tmp_path / "khong-co" / "content.toml")
    assert "config/content.toml" in str(info.value) and str(tmp_path) not in str(info.value)


def test_bad_alt_section_does_not_block_writing_rules(tmp_path):
    # [alt] sai chỉ khóa việc viết alt; quy tắc viết bài (trang Soạn bài) vẫn đọc được.
    path = _content(tmp_path, OLD + '[alt]\nmax_chars = "125"\n[images]\nwebp_quality = 0\n')
    assert load_rules(path, tmp_path / NO_PROFILE).checklist == ("Cụ thể",)
    with pytest.raises(ContentRulesError):
        load_alt_rules(path)
    with pytest.raises(ContentRulesError):
        load_image_settings(path)

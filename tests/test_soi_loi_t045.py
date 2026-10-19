"""Soi Lỗi kiểm thử T-045 (bộ lọc hồ sơ: LC-T043-1, SL-T043-1, SL-T043-2).

Chỉ gọi ``confirmed_profile`` (và hàm phụ của nó) trên chuỗi, không gọi mạng, không đọc ``.env``.
Nguyên tắc: khi nghi ngờ thì lọc thừa. Mọi ca ở đây kiểm rằng không có dòng có nhãn hay chữ của
ý có nhãn tới AI.
"""

import random
import re

import pytest

from seo_app.content import rules
from seo_app.content.rules import confirmed_profile
from tests.timing import assert_scales_linearly

# --- Điểm 1: ca «- [*****CẦN XÁC NHẬN]» bị bỏ khỏi test câu thường, nay phải bị giấu ----------


@pytest.mark.parametrize("stars", [5, 6, 7, 50])
def test_removed_t032_case_now_hidden_exact_form(stars):
    # Đúng dạng ca cũ (nhãn ngay sau gạch đầu dòng, không có chữ khác), nay theo chiều ngược lại.
    tag = "- [" + "*" * stars + "CẦN XÁC NHẬN]"
    assert confirmed_profile(f"- trước\n{tag}\n- sau") == "- trước\n- sau"


@pytest.mark.parametrize(
    "line",
    [
        "- [******] cần xác nhận",  # ngoặc đóng trước chữ: không phải nhãn
        "- [***** CẦN] XÁC NHẬN",  # ngoặc đóng giữa nhãn: không phải nhãn (như T-043)
    ],
)
def test_many_symbols_but_closed_bracket_still_plain(line):
    # Bỏ giới hạn 4 ký tự không được biến câu có ngoặc đóng thành nhãn.
    assert confirmed_profile(line) == line


# --- Điểm 2: lớp Lá Chắn T-043 #2 (dòng giữ lại không có nhãn riêng) --------------------------


def test_class2_item_before_indented_tagged_heading_has_no_tag_of_its_own():
    # Ca Thợ Máy nêu: «- ok» được giữ (không có nhãn), nhưng tiêu đề có nhãn và ý có nhãn
    # bên dưới không lọt chữ nào.
    text = "- ok\n  ## 7 [❗❗❗ **CẦN XÁC NHẬN**]\n  BIMAT [CẦN XÁC NHẬN]\n## 8\n- sau"
    out = confirmed_profile(text)
    assert out == "- ok\n## 8\n- sau"
    assert "BIMAT" not in out and "❗" not in out


def test_class2_tagged_heading_section_hidden_to_end():
    text = "- ok\n  ## 7 [❗❗❗ **CẦN XÁC NHẬN**]\n  BIMAT\n- BIMAT 2\n## 8\n- B"
    assert confirmed_profile(text) == "- ok\n## 8\n- B"


# Fuzz nhỏ, cố định hạt giống: mỗi dòng nội dung có mã riêng «Z<n>Q». Hai phép kiểm độc lập với
# cách bộ lọc chia khối:
#   (a) không dòng nào còn nhãn trọn tới AI;
#   (b) ý đơn giản (gạch đầu dòng không thụt lề + các dòng thụt lề không bắt đầu bằng «#» ngay
#       sau nó) có nhãn thì không mã nào của ý đó tới AI.
_FULL = [
    "[CẦN XÁC NHẬN]",
    "(chưa xác nhận)",
    "[**CẦN XÁC NHẬN**]",
    "[❗❗❗ **CẦN XÁC NHẬN**]",
    "[⚠️👨‍👩‍👧‍👦 CẦN XÁC NHẬN]",
    "[CẦN (XÁC NHẬN]",
    "[CẦN [** XÁC NHẬN]",
    "[" + "*" * 70 + "CẦN XÁC NHẬN]",
]
_HALF = ["[CẦN", "[CẦN XÁC", "(chưa", "[", "[❗❗❗ **CẦN", "[CẦN (", "[" + "⚠️" * 40 + "CẦN XÁC"]
_REST = ["NHẬN]", "XÁC NHẬN]", "CẦN XÁC NHẬN]", "NHẬN**]", "xác nhận)"]
_PLAIN = ["giá cổng", "cần xác nhận lịch", "[1] ghi chú", "(xem bảng)"]
_PREFIX = ["- ", "* ", "1. ", "  ", "\t", "", "## ", "### ", "# "]
_PREFIX += ["  ## ", "  ### ", "##x ", "  - "]
_ID = re.compile(r"Z\d+Q")
_BULLET = re.compile(r"(?:[-*+]|\d+[.)])\s")


def _fuzz_doc(rnd: random.Random) -> str:
    lines = []
    for n in range(rnd.randint(2, 9)):
        r = rnd.random()
        if r < 0.08:
            lines.append("")
            continue
        if r < 0.12:
            lines.append(rnd.choice(["> ghi chú", "  > x"]))
            continue
        p, zid, k = rnd.choice(_PREFIX), f"Z{n}Q", rnd.random()
        if k < 0.25:
            lines.append(f"{p}{zid} {rnd.choice(_PLAIN)}")
        elif k < 0.45:
            lines.append(f"{p}{zid} {rnd.choice(_PLAIN)} {rnd.choice(_FULL)}")
        elif k < 0.70:
            lines.append(f"{p}{zid} {rnd.choice(_PLAIN)} {rnd.choice(_HALF)}")
        else:
            lines.append(f"{p}{rnd.choice(_REST)} {zid}")
    return "\n".join(lines)


def _simple_items(lines: list[str]) -> list[list[str]]:
    items: list[list[str]] = []
    cur: list[str] | None = None
    for ln in lines:
        st = ln.strip()
        if st.startswith(">"):
            continue
        if st and not ln[0].isspace() and _BULLET.match(st):
            cur = [ln]
            items.append(cur)
        elif cur is not None and st and ln[0].isspace() and not st.startswith("#"):
            cur.append(ln)
        else:
            cur = None
    return items


@pytest.mark.parametrize("seed", [4501, 4502, 4503])
def test_fuzz_no_tagged_line_or_tagged_item_reaches_ai(seed):
    rnd = random.Random(seed)
    for _ in range(1500):
        doc = _fuzz_doc(rnd)
        out = confirmed_profile(doc)
        kept_ids = set(_ID.findall(out))
        for ln in out.splitlines():
            assert not rules._is_unconfirmed(ln), (doc, ln)
        for item in _simple_items(doc.splitlines()):
            if rules._is_unconfirmed(" ".join(item)):
                assert not (set(_ID.findall(" ".join(item))) & kept_ids), (doc, out)


# --- Điểm 3: các ca Thợ Máy nhờ thử -------------------------------------------------------------

_EMOJI = "👨‍👩‍👧‍👦⚠️🇻🇳❗**"


@pytest.mark.parametrize(
    "text",
    [
        # nhãn rất dài nhiều emoji vắt dòng trên tiêu đề
        f"## 6\n- A\n## 7 [{_EMOJI * 40}CẦN\nXÁC {'❗' * 300} NHẬN]\n- BIMAT\n## 8\n- ok",
        f"## 6\n- A\n## 7 [{_EMOJI * 40}\nCẦN XÁC NHẬN]\n- BIMAT\n## 8\n- ok",
        # như trên, tiêu đề thụt lề
        f"## 6\n- A\n  ## 7 [{_EMOJI * 40}CẦN XÁC\nNHẬN]\n- BIMAT\n## 8\n- ok",
        f"## 6\n- A\n  ## 7 [{_EMOJI * 40}\n  CẦN XÁC NHẬN]\n  BIMAT\n## 8\n- ok",
    ],
)
def test_long_emoji_half_tag_on_heading_hidden(text):
    out = confirmed_profile(text)
    assert "BIMAT" not in out
    assert out.endswith("## 8\n- ok")


def test_long_emoji_half_tag_on_indented_heading_in_tagged_item():
    text = f"- A [CẦN XÁC NHẬN]\n  ## 7 [{_EMOJI * 50}CẦN XÁC\n  BIMAT\n- ok"
    assert confirmed_profile(text) == "- ok"


@pytest.mark.parametrize(
    "text",
    [
        "- x [CẦN (XÁC NHẬN] BIMAT\n- ok",
        "- x [CẦN [** XÁC NHẬN] BIMAT\n- ok",
        "- x [CẦN (XÁC\n  NHẬN] BIMAT\n- ok",
        "- x [[CẦN XÁC NHẬN BIMAT\n- ok",
        "- x [(CẦN XÁC NHẬN BIMAT\n- ok",
        "- x ([CẦN XÁC NHẬN BIMAT\n- ok",
        "## 7 [CẦN (XÁC\nNHẬN]\n- BIMAT\n## 8\n- ok",
        "## 7 [CẦN [** XÁC\nNHẬN]\n- BIMAT\n## 8\n- ok",
        "## 7 [CẦN (\nXÁC NHẬN]\n- BIMAT\n## 8\n- ok",
        "## 7 [CẦN ([\nXÁC NHẬN]\n- BIMAT\n## 8\n- ok",
    ],
)
def test_open_bracket_inside_tag_hidden(text):
    out = confirmed_profile(text)
    assert "BIMAT" not in out
    assert out.endswith("- ok")


@pytest.mark.parametrize(
    "text",
    [
        "- a [CẦN XÁC NHẬN]\n  ## b [CẦN\n  ## c [CẦN\n  ## d [CẦN\n  BIMAT\n- ok",
        "- a [CẦN XÁC NHẬN]\n  ## b [CẦN\n  ## c (\n  ## d [\n  BIMAT\n\n  BIMAT2\n- ok",
        "- a [CẦN XÁC NHẬN]\n  ## b [CẦN\n\n  BIMAT2\n- ok",
        "- a [CẦN XÁC NHẬN]\n  ## b [CẦN\n\n\n  BIMAT2\n  BIMAT3\n- ok",
        "- a [CẦN XÁC NHẬN]\n  ## b [CẦN\n> note\n  BIMAT2\n- ok",
        "- a [CẦN XÁC NHẬN]\n  ## b [CẦN\n  > ghi chú\n  BIMAT\n- ok",
        "- a [CẦN XÁC NHẬN]\n  ## b [CẦN\n​\n  BIMAT\n- ok",
        "- a [CẦN XÁC NHẬN]\n​  ## b [CẦN\n  BIMAT\n- ok",
        "- a [CẦN XÁC NHẬN]\n  ​## b [CẦN\n  BIMAT\n- ok",
        "- a [CẦN XÁC NHẬN]\n  ## b [CẦN\n  ## NHẬN] c\n  BIMAT\n- ok",
        "- a [CẦN XÁC NHẬN]\n\n  ## b [CẦN\n  BIMAT\n- ok",
        "- a [CẦN XÁC NHẬN]\n\n  ## b [CẦN\n\n  BIMAT\n- ok",
        "- a [CẦN XÁC NHẬN]\n  ## b [CẦN\nBIMAT dòng quên thụt lề\n- ok",
        "Đoạn [CẦN XÁC NHẬN]\n  ## b [CẦN\nBIMAT dòng quên thụt lề\n\n- ok",
    ],
)
def test_chained_indented_half_headings_in_tagged_item(text):
    # Mọi dòng của ý có nhãn (kể cả dòng «  ## … [CẦN» nối nhau, dòng trống, dòng «>», ký tự
    # vô hình) đều bị giấu.
    assert confirmed_profile(text) == "- ok"


@pytest.mark.parametrize(
    "text",
    [
        "- a\n  ## b [CẦN\n  ## c [CẦN\n  ## d [CẦN\n  BIMAT\n- ok",
        "- a\n  ## b [CẦN\n  ## c XÁC NHẬN]\n  BIMAT\n- ok",  # chữ «c» chen giữa: không phải nhãn
    ],
)
def test_chained_indented_half_headings_untagged_item_kept(text):
    # Không có nhãn nào: không giấu thừa.
    assert confirmed_profile(text) == text


@pytest.mark.parametrize(
    "text",
    [
        "### 6.1 [CẦN XÁC NHẬN]\n- bí mật\n## 7 [CẦN XÁC\n\n## NHẬN]\n- BIMAT\n### 7.1\n- BIMAT\n"
        "## 8\n- ok",
        "### 6.1 [CẦN XÁC NHẬN]\n- bí mật\n  # 7 [CẦN XÁC NHẬN]\n- BIMAT\n## 8\n- BIMAT\n# 9\n- ok",
        "### 6.1 [CẦN XÁC NHẬN]\n- bí mật\n  # 7 [CẦN XÁC\nNHẬN]\n- BIMAT\n## 8\n- BIMAT\n"
        "# 9\n- ok",
        "### 6.1 [CẦN XÁC NHẬN]\n- bí mật\n# 7 [❗❗❗❗❗ CẦN\n XÁC NHẬN]\n- BIMAT\n"
        "## 8\n- BIMAT\n# 9\n- ok",
    ],
)
def test_higher_tagged_heading_inside_hidden_section(text):
    out = confirmed_profile(text)
    assert "BIMAT" not in out and "bí mật" not in out
    assert out.endswith("- ok")


@pytest.mark.parametrize(
    "text",
    [
        "## 7 [CẦN XÁC\n\n\n## NHẬN]\n- BIMAT\n## 8\n- ok",
        "## 7 [CẦN XÁC\n> ghi chú\n## NHẬN]\n- BIMAT\n## 8\n- ok",
        "## 7 [CẦN XÁC\n> ghi chú\n\n## NHẬN]\n- BIMAT\n## 8\n- ok",
        "## 7 [CẦN XÁC\n  > ghi chú\n  ## NHẬN]\n- BIMAT\n## 8\n- ok",
        "- a [CẦN XÁC NHẬN]\n  ## 7 [CẦN XÁC\n\n## NHẬN]\n- BIMAT\n## 8\n- ok",
        "- a [CẦN XÁC NHẬN]\n  ## 7 [CẦN XÁC\n> x\n## NHẬN]\n- BIMAT\n## 8\n- ok",
        "## 7 [CẦN XÁC\nNHẬN]\n## 7 [CẦN XÁC\n## NHẬN]\n- BIMAT\n## 8\n- ok",
    ],
)
def test_heading_rest_after_blank_or_note_lines(text):
    assert confirmed_profile(text) == "## 8\n- ok"


def test_heading_rest_after_blank_lines_keeps_item_before_indented_heading():
    text = "- a\n  ## 7 [CẦN XÁC\n\n\n## NHẬN]\n- BIMAT\n## 8\n- ok"
    assert confirmed_profile(text) == "- a\n## 8\n- ok"


def test_lower_level_rest_line_hides_to_tagged_heading_level():
    # «# XÁC NHẬN]» là nửa sau của nhãn trên tiêu đề «## b»: giấu tới tiêu đề «##» kế tiếp.
    text = "- a [CẦN XÁC NHẬN]\n  ## b [CẦN\n# XÁC NHẬN]\n- BIMAT\n## c\n- giữ\n# d\n- ok"
    assert confirmed_profile(text) == "## c\n- giữ\n# d\n- ok"


# --- Lỗi tìm thêm (có từ trước trên ``main``, không lùi; mức Thấp) ----------------------------


@pytest.mark.xfail(
    strict=True,
    reason="SL-T045-1: nhãn trên tiêu đề vắt qua 3 dòng: tiêu đề chờ chỉ ghép với đúng 1 dòng kế",
)
@pytest.mark.parametrize(
    "text",
    [
        "## 7 [CẦN\nXÁC\nNHẬN]\n- BIMAT\n## 8\n- ok",
        "## 7 [\nCẦN\nXÁC NHẬN]\n- BIMAT\n## 8\n- ok",
        "## 7 [**\n**CẦN\nXÁC NHẬN]\n- BIMAT\n## 8\n- ok",
    ],
)
def test_sl_t045_1_heading_tag_over_three_lines(text):
    assert "BIMAT" not in confirmed_profile(text)


@pytest.mark.xfail(
    strict=True,
    reason="SL-T045-2: nửa sau của nhãn tiêu đề lại mở nửa nhãn mới, dòng kế dạng tiêu đề hoàn "
    "thành nó: dòng đó kết thúc mục đang giấu, mục lọt",
)
@pytest.mark.parametrize(
    "text",
    [
        "## 7 [CẦN XÁC\n## NHẬN] [CẦN XÁC\n## NHẬN]\n- BIMAT\n## 8\n- ok",
        "## 7 [CẦN XÁC\nNHẬN] [CẦN XÁC\n## NHẬN]\n- BIMAT\n## 8\n- ok",
    ],
)
def test_sl_t045_2_rest_line_opens_new_half_tag(text):
    assert "BIMAT" not in confirmed_profile(text)


# --- Điểm 4: tốc độ và bộ nhớ đệm ----------------------------------------------------------------


@pytest.mark.parametrize(
    "make",
    [
        lambda k: "- " + "[CAN" + "*(" * 25000 * k,
        lambda k: "- " + "(" + "*" * 1000 + ("(" + "*" * 1000) * 25 * k,
        lambda k: "- [CAN XAC" + "[" * 50000 * k,
        lambda k: "- [CAN" + " [" * 25000 * k,
        lambda k: "- " + "[CAN XAC [" * 6000 * k,
        lambda k: "- x\n" + "  y [CAN\n  ## b [CAN\n" * 2500 * k,
        lambda k: "- x\n" + "  y\n  ## b [CAN\n" * 2500 * k,
        lambda k: "### a [CAN XAC NHAN]\n" + "  # x [CAN\n  ## y\n" * 2500 * k,
        lambda k: ("## 7 [CAN XAC\n\n> x\n## NHAN]\n- y\n") * 1000 * k,
        lambda k: "## 7 [" + "👨‍👩‍👧‍👦" * 10000 * k + "\nCAN XAC NHAN]\n- x",
    ],
    ids=[
        "can-star-paren",
        "paren-long-star-runs",
        "xac-then-brackets",
        "can-space-bracket",
        "repeated-can-xac-bracket",
        "half-line-then-half-heading",
        "plain-line-then-half-heading",
        "hidden-many-indented-higher",
        "rest-after-note",
        "emoji-zwj-half-heading",
    ],
)
def test_more_bad_inputs_linear(make):
    assert_scales_linearly(confirmed_profile, make, label="Soi Lỗi T-045")


def test_lru_cache_does_not_change_results_between_calls():
    # Cùng tập tài liệu, chạy xuôi, chạy ngược và chạy sau khi xóa bộ nhớ đệm mỗi lần: kết quả
    # phải như nhau (kết quả không phụ thuộc lần gọi trước).
    rnd = random.Random(4599)
    docs = [_fuzz_doc(rnd) for _ in range(800)]
    docs += ["- a [CẦN XÁC NHẬN]", "- a [CẦN XÁC NHẬN]", "- a", "## 7 [CẦN XÁC", "NHẬN]"]
    forward = [confirmed_profile(d) for d in docs]
    backward = [confirmed_profile(d) for d in reversed(docs)][::-1]
    fresh = []
    for d in docs:
        rules._is_unconfirmed.cache_clear()
        rules._ends_with_partial_tag.cache_clear()
        fresh.append(confirmed_profile(d))
    assert forward == backward == fresh


def test_lru_cache_is_small():
    # Bộ nhớ đệm giữ tối đa 8 chuỗi: không giữ cả hồ sơ lớn qua nhiều lần gọi.
    assert rules._is_unconfirmed.cache_info().maxsize == 8
    assert rules._ends_with_partial_tag.cache_info().maxsize == 8


# --- Điểm 5: hồ sơ thật ----------------------------------------------------------------------


def test_real_profile_has_no_tag_reaching_ai():
    out = rules.load_rules().business_profile
    assert out
    for ln in out.splitlines():
        assert not rules._is_unconfirmed(ln)
        assert not ln.lstrip().startswith(">")

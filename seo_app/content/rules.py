"""Quy tắc nội dung (``config/content.toml``), hồ sơ doanh nghiệp và các kiểm tra không cần AI."""

from __future__ import annotations

import functools
import re
import tomllib
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from seo_app.ai.base import AIError
from seo_app.config import PROJECT_ROOT

CONTENT_CONFIG_FILE = PROJECT_ROOT / "config" / "content.toml"
BUSINESS_PROFILE_FILE = PROJECT_ROOT / "config" / "business_profile.md"
# Ý mang nhãn «[CẦN XÁC NHẬN» (có hay không có lý do phía sau) trong hồ sơ doanh nghiệp chưa
# được chủ dự án xác nhận: AI không được thấy. So trên chữ đã bỏ ký tự vô hình, chuẩn hóa NFKC,
# viết hoa và bỏ dấu (``_tag_text``), nên nhận cả các kiểu gõ sai trong Notepad: dính chữ
# («[CẦNXÁC NHẬN]»), không dấu («[CAN XAC NHAN]»), ngoặc tròn, «CHƯA XÁC NHẬN». An toàn khi nghi
# ngờ: thà giấu thừa còn hơn để lọt. Vẫn bắt buộc có ngoặc mở để câu thường như «khách cần xác
# nhận lịch» không bị giấu.
# Giữa ngoặc mở và chữ, giữa các chữ: bao nhiêu khoảng trắng và ký tự không phải chữ/số cũng
# được («[**CẦN XÁC NHẬN**]», «["CẦN"]», «[❗❗❗ **CẦN»,  «[CẦN-XÁC_NHẬN]», emoji ghép nhiều điểm
# mã; LC-T032-1, SL-T043-1), trừ dấu đóng ngoặc.
# Chống chạy bậc hai (ReDoS) khi không giới hạn số ký tự: ngay sau ngoặc mở (``_LEAD_GAP``)
# không cho thêm ngoặc mở nào, nên với «[[[[…» mỗi điểm bắt đầu chỉ quét tới ngoặc kế tiếp
# (nhãn «[[CẦN…» vẫn khớp, tính từ ngoặc cuối). Giữa các chữ (``_GAP``) thì cho ngoặc mở
# («[CẦN (XÁC NHẬN]»): trước mỗi chữ «CAN»/«CHUA» chỉ có đúng một điểm bắt đầu khớp được (ngoặc
# mở gần nhất), và các dải chen không chứa chữ, nên mỗi dải chỉ bị quét một lần. Mỗi nhóm là
# MỘT lớp ký tự (không lồng lượng từ) và dùng lượng từ chiếm hữu ``*+``: không quay lui.
_LEAD_GAP = r"(?:[^\w\[\]()]|_)*+"
_GAP = r"(?:[^\w\])]|_)*+"
_UNCONFIRMED_PATTERN = re.compile(rf"[\[(]{_LEAD_GAP}(?:CAN|CHUA){_GAP}XAC{_GAP}NHAN")
# Gạch đầu dòng: «- », «* », «+ », «1. », «1) ».
_BULLET = re.compile(r"(?:[-*+]|\d+[.)])(?:\s|$)")
# Tiêu đề "thật" như Markdown: 1–6 dấu «#» rồi khoảng trắng hoặc hết dòng. Chỉ tiêu đề thật mới
# kết thúc mục đang giấu; «#suachuacuasat» hay «#1 khu vực» thì không (Soi Lỗi SL-T032-1).
_REAL_HEADING = re.compile(r"#{1,6}(?:\s|$)")
# Dải ký tự chen trong nhãn (như ``_GAP``: khoảng trắng, «_», ký tự không phải chữ/số trừ dấu
# đóng ngoặc). ``_ends_with_partial_tag`` thu mỗi dải về một ký tự: «[» nếu dải có ngoặc mở,
# không thì dấu cách.
_PARTIAL_GAP_RUN = re.compile(r"(?:[^\w\])]|_)++")
# Phần sau ngoặc mở của nửa nhãn, trên chữ đã thu dải: chỉ chữ cái (đã bỏ dấu), dấu cách và «[».
_PARTIAL_TAG_REST = re.compile(r"[A-Z \[]*")
# Cửa sổ cuối dòng được xét. Sau khi thu dải, nửa nhãn dài nhất là ngoặc rồi 11 chữ, mỗi chữ
# cách nhau tối đa một ký tự: 23 ký tự, nên bao nhiêu ký tự lạ cũng không đẩy nửa nhãn ra ngoài.
_PARTIAL_TAG_MAX = 64
_TAG_WORDS = ("CANXACNHAN", "CHUAXACNHAN")

# Ký tự "mặc định bỏ qua" (Unicode Default_Ignorable_Code_Point) KHÔNG thuộc loại Cf: không
# hiện ra nhưng nằm giữa "<" và "/" vẫn làm thẻ giả trông như thật với AI (Soi Lỗi R3-7), hay
# chen trong nhãn [CẦN XÁC NHẬN] làm nhãn không được nhận (SL-024-2). Dùng chung với prompts.py.
IGNORABLE_NOT_CF = re.compile(
    "[\u034f\u115f\u1160\u17b4\u17b5\u180b-\u180d\u180f\u2065\u3164"
    "\ufe00-\ufe0f\uffa0\ufff0-\ufff8\U000e0100-\U000e01ef]"
)

# Chỗ AI để trống vì thiếu dữ liệu thật, ví dụ: [cần bổ sung: giá cổng 4 m của xưởng]
MISSING_PATTERN = re.compile(r"\[cần bổ sung:[^\]]*\]", re.IGNORECASE)
_SENTENCE_END = re.compile(r"(?<=[.!?…])\s+|\n+")


class ContentRulesError(AIError):
    """``config/content.toml`` hoặc hồ sơ doanh nghiệp đọc không được / viết sai dạng.

    Là một loại ``AIError`` để trang Soạn bài báo lỗi tiếng Việt và khóa các bước AI, thay vì
    hiện lỗi Python.
    """


@dataclass(frozen=True)
class ContentRules:
    business_profile: str
    address: str
    tone: str
    banned: tuple[str, ...]
    checklist: tuple[str, ...]


def confirmed_profile(text: str) -> str:
    """Hồ sơ doanh nghiệp đã bỏ các ý còn nhãn [CẦN XÁC NHẬN] và mọi dòng ghi chú ``>``.

    Lọc theo **khối**, không theo từng dòng, để một ý viết trên nhiều dòng không lọt nửa nào:

    - Gạch đầu dòng (``- …``, ``* …``, ``1. …``) không thụt lề mở một khối; các dòng sau nó
      cho tới dòng trống, tiêu đề hoặc gạch đầu dòng không thụt lề kế tiếp đều thuộc khối đó
      (dòng thụt vào, gạch đầu dòng lồng nhau, cả dòng quên thụt lề khi gõ Notepad).
    - Đoạn văn thường: khối là cả đoạn, ngăn bằng dòng trống.
    - Dòng **thụt lề** ngay sau dòng trống vẫn thuộc khối trước (một ý nhiều đoạn, như Markdown;
      Soi Lỗi SL-024-1). Dòng không thụt lề sau dòng trống luôn mở khối mới.
    - Tiêu đề ``#`` (không thụt lề) luôn đứng riêng một khối.

    Khối có nhãn thì bỏ cả khối. Nhãn được tìm trên cả khối (các dòng nối nhau bằng dấu cách),
    nên nhãn bị xuống dòng giữa chừng («[CẦN XÁC» cuối dòng này, «NHẬN]» đầu dòng sau) vẫn được
    nhận. Tiêu đề có nhãn thì bỏ cả **mục**: tiêu đề đó và mọi dòng bên dưới, tới tiêu đề kế tiếp
    cùng cấp hoặc cao hơn (số dấu ``#`` bằng hoặc ít hơn; ``## 7. …`` giấu qua ``### 7.1`` tới
    ``## 8.``). Chỉ tiêu đề thật (``#`` rồi khoảng trắng) mới kết thúc mục đang giấu. Tiêu đề lỡ
    thụt lề mà có nhãn cũng giấu cả mục. Tiêu đề kết thúc bằng nửa nhãn (``## 7. … [CẦN XÁC``)
    được xét nối với dòng kế (bỏ qua dòng trống ở giữa, SL-T032-4); dòng kế đó là nửa sau của
    nhãn nên bị giấu theo, kể cả khi trông như tiêu đề (``## NHẬN]``, SL-T043-2). Đang giấu mà
    gặp tiêu đề cấp cao hơn có nhãn của riêng nó thì giấu tới cấp của tiêu đề đó. Tiêu đề lỡ
    thụt lề có nửa nhãn nằm trong ý đã có nhãn thì không tách ý ra (LC-T043-1), nhưng vẫn chờ
    dòng kế như tiêu đề. Dòng ghi chú (ký tự nhìn thấy đầu tiên là ``>``) luôn bị bỏ và không
    cắt khối.
    Ký tự vô hình (U+200B, BOM…) bị bỏ qua khi xét cấu trúc và nhãn (SL-024-2). Các dòng giữ lại
    y nguyên như trong file.
    """
    kept: list[str] = []
    block: list[str] = []
    blanks: list[str] = []  # dòng trống chưa biết thuộc khối trước hay nằm giữa hai khối
    hidden_level = 0  # > 0: đang giấu mục của tiêu đề có nhãn với số «#» này
    # Tiêu đề có nửa nhãn ở cuối, chờ dòng kế: (dòng, số «#», đã nằm trong khối đang mở chưa).
    pending: tuple[str, int, bool] | None = None
    pending_blanks: list[str] = []  # dòng trống giữa tiêu đề chờ và dòng kế (SL-T032-4)
    block_tagged = False  # khối đang mở đã biết là có nhãn (thêm dòng vẫn còn nhãn)

    def close_block() -> None:
        nonlocal block_tagged
        if block and not (block_tagged or _is_unconfirmed(" ".join(block))):
            kept.extend(block)
        block.clear()
        block_tagged = False
        kept.extend(blanks)
        blanks.clear()

    def block_is_tagged() -> bool:
        # Nhớ kết quả «có nhãn»: khối có nhãn chỉ dài thêm cho tới khi đóng, nên không phải dò
        # lại cả khối ở mỗi dòng (giữ bộ lọc tuyến tính). Khối chưa có nhãn chỉ dò một lần rồi
        # bị đóng ngay (dòng đang xét tách ra thành tiêu đề).
        nonlocal block_tagged
        if block and not block_tagged:
            block_tagged = _is_unconfirmed(" ".join(block))
        return block_tagged

    for line in text.splitlines():
        visible = _visible(line)
        stripped = visible.strip()
        if stripped.startswith(">"):
            continue
        indented = bool(stripped) and visible[0].isspace()
        heading = bool(stripped) and not indented and stripped.startswith("#")
        level = len(stripped) - len(stripped.lstrip("#"))
        # Dòng có thể mở mục: tiêu đề không thụt lề, hoặc tiêu đề thật lỡ thụt lề (SL-T032-2).
        heading_like = heading or (indented and _REAL_HEADING.match(stripped) is not None)
        if pending is not None:
            if not stripped:
                pending_blanks.append(line)  # nửa sau của nhãn có thể nằm sau dòng trống
                continue
            head, head_level, head_in_block = pending
            pending = None
            joined = _is_unconfirmed(f"{head} {line}")
            if joined:
                if head_in_block:
                    # Khối chứa tiêu đề chờ, và tiêu đề đó cùng dòng này thành nhãn: bỏ cả khối.
                    block_tagged = True
                    close_block()
                pending_blanks.clear()
                # Dòng này (nửa sau của nhãn) bị giấu cùng mục. Bỏ qua luôn, kể cả khi nó trông
                # như tiêu đề cùng cấp («## 7 [CẦN XÁC» rồi «## NHẬN]»): nó là một phần của nhãn,
                # không được kết thúc mục đang giấu (SL-T043-2).
                hidden_level = _tagged_heading_level(line, heading_like, level, head_level)
                continue
            if head_in_block:
                # Tiêu đề chờ đã nằm trong khối: dòng trống sau nó xử lý như sau dòng thường.
                blanks.extend(pending_blanks)
            else:
                kept.append(head)
                kept.extend(pending_blanks)
            pending_blanks.clear()
        if hidden_level:
            if not heading or level > hidden_level or not _REAL_HEADING.match(stripped):
                hidden_level = _tagged_heading_level(line, heading_like, level, hidden_level)
                continue
            hidden_level = 0
        if not stripped:
            if block:
                blanks.append(line)
            else:
                kept.append(line)
            continue
        join_block = False  # tiêu đề thụt lề vẫn nằm trong khối trước (không tách khối)
        if indented and _REAL_HEADING.match(stripped):
            prev_half = bool(block) and _ends_with_partial_tag(block[-1])
            if _is_unconfirmed(line):
                # Tiêu đề lỡ thụt lề mà có nhãn: vẫn giấu cả mục (SL-T032-2). Dòng trước còn
                # nửa nhãn thì dòng này có thể là nửa sau của nhãn đó: giấu luôn khối trước.
                heading = True
                join_block = prev_half
            elif _ends_with_partial_tag(line):
                # Tiêu đề lỡ thụt lề có nửa nhãn ở cuối: chờ dòng kế như tiêu đề thường
                # (SL-T032-5). Nhưng không tách khối khi dòng trước còn nửa nhãn (dòng này có
                # thể là nửa sau của nhãn đó, tách ra thì khối trước lọt) hay khối trước đã có
                # nhãn (tách ra thì các dòng thụt lề phía sau, vẫn thuộc ý có nhãn, thành khối
                # mới không nhãn và tới AI: LC-T043-1). Khi đó dòng này vừa nằm trong khối, vừa
                # chờ dòng kế.
                heading = True
                join_block = prev_half or block_is_tagged()
        if blanks and not indented:
            close_block()
        if (heading and not join_block) or (not indented and _BULLET.match(stripped)):
            close_block()
        block.extend(blanks)
        blanks.clear()
        if heading:
            if _is_unconfirmed(line):
                hidden_level = level
            elif _ends_with_partial_tag(line):
                if join_block:
                    block.append(line)
                pending = (line, level, join_block)  # SL-T032-3
                continue
            block.append(line)
            close_block()
            continue
        block.append(line)
    # Hết file mà tiêu đề còn nửa nhãn: an toàn khi nghi ngờ, bỏ tiêu đề đó.
    close_block()
    return "\n".join(kept).strip()


def _tagged_heading_level(line: str, heading_like: bool, level: int, hidden_level: int) -> int:
    """Mức giấu mới khi gặp ``line`` lúc đang giấu mục cấp ``hidden_level``.

    Dòng có thể mở mục (tiêu đề không thụt lề, hoặc tiêu đề thật lỡ thụt lề) mà ít «#» hơn
    (cấp cao hơn) và chính nó có nhãn hay nửa nhãn ở cuối thì phần giấu mở rộng tới cấp của
    nó, như khi gặp nó lúc không giấu. Không vậy thì nhãn của nó bị nuốt cùng mục đang giấu và
    mục của nó lọt (ví dụ «#x [CẦN XÁC NHẬN]» hay «  ## [CẦN XÁC NHẬN]» không kết thúc mục đang
    giấu). Nửa nhãn cũng tính, vì không thể chờ dòng kế cho một dòng đã bị giấu: an toàn khi
    nghi ngờ.
    """
    if (
        heading_like
        and level < hidden_level
        and (_is_unconfirmed(line) or _ends_with_partial_tag(line))
    ):
        return level
    return hidden_level


def _visible(line: str) -> str:
    """Dòng để so khớp: bỏ ký tự vô hình (Unicode loại Cf như U+200B, BOM, gạch nối mềm, và các
    ký tự "mặc định bỏ qua" khác), chuẩn hóa NFKC và viết hoa.

    NFKC chạy trước vì nó có thể biến ký tự thường thành ký tự vô hình (U+FFA0 thành U+1160);
    chạy lại NFC sau cùng để ghép chữ với dấu bị ký tự vô hình tách ra.
    """
    text = unicodedata.normalize("NFKC", line)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Cf")
    text = IGNORABLE_NOT_CF.sub("", text)
    return unicodedata.normalize("NFC", text).upper()


def _tag_text(text: str) -> str:
    """Chữ để tìm nhãn: như ``_visible`` rồi bỏ hết dấu tiếng Việt (tách NFD, bỏ dấu kết hợp,
    đổi «Đ» thành «D»), để «[CẦN XÁC NHẬN]», «[CAN XAC NHAN]» và «[CẦN XAC NHẬN]» như nhau."""
    decomposed = unicodedata.normalize("NFD", _visible(text))
    bare = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return bare.replace("Đ", "D")


def _squeeze_gap(match: re.Match[str]) -> str:
    run = match.group()
    return "[" if "[" in run or "(" in run else " "


# Bộ nhớ đệm nhỏ: cùng một dòng thường được xét vài lần liên tiếp (dòng đang xét, rồi là
# «dòng trước» của dòng kế). Chuỗi Python nhớ sẵn mã băm nên tra lại gần như không tốn gì.
@functools.lru_cache(maxsize=8)
def _ends_with_partial_tag(text: str) -> bool:
    """Cuối dòng là nửa đầu của nhãn, ví dụ «[CẦN XÁC», «(chưa», «[**CẦN», «[» (nhãn bị xuống
    dòng).

    Mỗi dải ký tự chen (khoảng trắng, «*», emoji…) được thu về một ký tự trước (``[`` nếu dải
    có ngoặc mở, không thì dấu cách): mọi ngoặc mở trong cùng một dải cho cùng một kết quả, nên
    thu lại không đổi kết quả mà nửa nhãn luôn ngắn. Sau đó chỉ xét đoạn cuối dài
    ``_PARTIAL_TAG_MAX`` ký tự, nên phần so khớp tốn thời gian cố định dù dòng có hàng nghìn
    ngoặc. Thử từng ngoặc mở trong đoạn đó.
    """
    squeezed = _PARTIAL_GAP_RUN.sub(_squeeze_gap, _tag_text(text))
    tail = squeezed[-_PARTIAL_TAG_MAX:]
    for start, ch in enumerate(tail):
        if ch != "[":
            continue
        rest = tail[start + 1 :]
        if not _PARTIAL_TAG_REST.fullmatch(rest):
            continue
        letters = re.sub(r"[^A-Z]", "", rest)
        if any(words.startswith(letters) for words in _TAG_WORDS):
            return True
    return False


@functools.lru_cache(maxsize=8)
def _is_unconfirmed(text: str) -> bool:
    """Đoạn chữ có nhãn [CẦN XÁC NHẬN], kể cả khi gõ sai (xem ``_UNCONFIRMED_PATTERN``) hay có
    ký tự vô hình chen vào nhãn. Ký tự vô hình bị bỏ hẳn: mẫu nhãn cho phép giữa các chữ có hay
    không có dấu cách, nên «C<U+200D>ẦN» và «CẦN<U+200B>XÁC» đều khớp."""
    return _UNCONFIRMED_PATTERN.search(_tag_text(text)) is not None


def _read_text(path: Path) -> str:
    try:
        # "utf-8-sig": nhận cả file UTF-8 có BOM (Notepad đời cũ lưu kiểu này).
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ContentRulesError(
            f"File config/{path.name} không lưu ở dạng UTF-8. Mở lại bằng Notepad, chọn "
            "Lưu thành (Save As) → Mã hóa (Encoding): UTF-8, rồi lưu."
        ) from exc
    except OSError as exc:
        raise ContentRulesError(f"Không đọc được file config/{path.name}.") from exc


def _table(data: dict, key: str, path: Path) -> dict:
    value = data.get(key, {})
    if not isinstance(value, dict):
        raise ContentRulesError(
            f"File config/{path.name}: «{key}» phải là một mục [{key}], không phải một giá trị."
        )
    return value


def _text(table: dict, key: str, path: Path) -> str:
    value = table.get(key, "")
    if not isinstance(value, str):
        raise ContentRulesError(f"File config/{path.name}: «{key}» phải là chữ trong ngoặc kép.")
    return value


def _text_list(table: dict, key: str, path: Path) -> tuple[str, ...]:
    value = table.get(key, [])
    if isinstance(value, str):
        # Viết nhầm một chuỗi thay vì danh sách: coi là danh sách một dòng, không tách từng chữ.
        value = [value]
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ContentRulesError(
            f'File config/{path.name}: «{key}» phải là danh sách chữ, ví dụ ["dòng 1", "dòng 2"].'
        )
    return tuple(v for v in value if v.strip())


def load_rules(
    path: Path = CONTENT_CONFIG_FILE, profile_path: Path = BUSINESS_PROFILE_FILE
) -> ContentRules:
    """Đọc quy tắc nội dung. File sai bảng mã hoặc sai dạng thì báo ``ContentRulesError``."""
    try:
        data = tomllib.loads(_read_text(path))
    except tomllib.TOMLDecodeError as exc:
        raise ContentRulesError(f"File config/{path.name} viết sai cú pháp: {exc}") from exc
    voice = _table(data, "voice", path)
    review = _table(data, "review", path)
    profile = confirmed_profile(_read_text(profile_path)) if profile_path.is_file() else ""
    return ContentRules(
        business_profile=profile,
        address=_text(voice, "address", path),
        tone=_text(voice, "tone", path),
        banned=_text_list(voice, "banned", path),
        checklist=_text_list(review, "checklist", path),
    )


def sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_END.split(text) if s.strip()]


def find_banned(text: str, banned: tuple[str, ...] | list[str]) -> list[tuple[str, str]]:
    """Các câu chứa cụm từ cấm: [(câu, cụm từ)]. Không phân biệt hoa thường.

    So khớp sau khi chuẩn hóa Unicode (NFC; chữ Việt dán từ máy Mac hay ở dạng tổ hợp NFD) và
    gộp mọi khoảng trắng (dấu cách không ngắt, nhiều dấu cách) thành một dấu cách. Cụm từ phải
    đứng trọn từ: «Tóm lại» không khớp «Tóm lạii». Câu trả về giữ nguyên như trong bài.
    """
    patterns = [(phrase, _phrase_pattern(phrase)) for phrase in banned if phrase.strip()]
    found = []
    for sentence in sentences(text):
        normalized = _normalize(sentence)
        for phrase, pattern in patterns:
            if pattern.search(normalized):
                found.append((sentence, phrase))
                break
    return found


def _normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).lower().split())


def _phrase_pattern(phrase: str) -> re.Pattern[str]:
    """Cụm từ đứng trọn từ: không dính chữ cái/chữ số ngay trước hoặc ngay sau.

    Chỉ đòi ranh giới ở đầu (cuối) cụm khi cụm bắt đầu (kết thúc) bằng chữ cái/chữ số: cụm
    «Nhìn chung,» vẫn khớp «Nhìn chung,cửa…» (thiếu dấu cách sau dấu phẩy, Soi Lỗi R3-5).
    """
    normalized = _normalize(phrase)
    before = r"(?<!\w)" if re.match(r"\w", normalized) else ""
    after = r"(?!\w)" if re.search(r"\w$", normalized) else ""
    return re.compile(before + re.escape(normalized) + after)


def find_missing(text: str) -> list[str]:
    """Các chỗ «[cần bổ sung: …]» còn trong bài."""
    return MISSING_PATTERN.findall(text)

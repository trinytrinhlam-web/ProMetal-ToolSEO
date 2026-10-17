"""Quy tắc nội dung (``config/content.toml``), hồ sơ doanh nghiệp và các kiểm tra không cần AI."""

from __future__ import annotations

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
# Giữa ngoặc mở và chữ, giữa các chữ: khoảng trắng tùy ý và tối đa 4 ký tự không phải chữ/số
# («[**CẦN XÁC NHẬN**]», «["CẦN"]», «[⚠ CẦN»,  «[CẦN-XÁC_NHẬN]», Lá Chắn LC-T032-1), trừ dấu
# đóng ngoặc. Giới hạn {0,4} là bắt buộc: «[» cũng là ký tự không phải chữ, dùng «*» thì chuỗi
# «[[[[…» chạy bậc hai. Hai nhánh trong nhóm không trùng nhau với «\s», nên không quay lui bùng nổ.
_GAP = r"\s*(?:(?:[^\w\s\])]|_)\s*){0,4}"
_UNCONFIRMED_PATTERN = re.compile(rf"[\[(]{_GAP}(?:CAN|CHUA){_GAP}XAC{_GAP}NHAN")
# Gạch đầu dòng: «- », «* », «+ », «1. », «1) ».
_BULLET = re.compile(r"(?:[-*+]|\d+[.)])(?:\s|$)")
# Tiêu đề "thật" như Markdown: 1–6 dấu «#» rồi khoảng trắng hoặc hết dòng. Chỉ tiêu đề thật mới
# kết thúc mục đang giấu; «#suachuacuasat» hay «#1 khu vực» thì không (Soi Lỗi SL-T032-1).
_REAL_HEADING = re.compile(r"#{1,6}(?:\s|$)")
# Phần sau ngoặc mở của nửa nhãn: chỉ chữ cái (đã bỏ dấu), khoảng trắng, «_» và ký tự không
# phải chữ/số trừ dấu đóng ngoặc (như ``_GAP``).
_PARTIAL_TAG_REST = re.compile(r"(?:[A-Z\s_]|[^\w\s\])])*")
# Nửa nhãn dài nhất sau khi gộp khoảng trắng: ngoặc, 11 chữ, 4 khoảng × (4 ký tự + dấu cách).
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
    được xét nối với dòng kế (bỏ qua dòng trống ở giữa, SL-T032-4). Dòng ghi chú (ký tự nhìn
    thấy đầu tiên là ``>``) luôn bị bỏ và không cắt khối.
    Ký tự vô hình (U+200B, BOM…) bị bỏ qua khi xét cấu trúc và nhãn (SL-024-2). Các dòng giữ lại
    y nguyên như trong file.
    """
    kept: list[str] = []
    block: list[str] = []
    blanks: list[str] = []  # dòng trống chưa biết thuộc khối trước hay nằm giữa hai khối
    hidden_level = 0  # > 0: đang giấu mục của tiêu đề có nhãn với số «#» này
    pending: tuple[str, int] | None = None  # tiêu đề có nửa nhãn ở cuối, chờ dòng kế
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
        if pending is not None:
            if not stripped:
                pending_blanks.append(line)  # nửa sau của nhãn có thể nằm sau dòng trống
                continue
            head, head_level = pending
            pending = None
            if _is_unconfirmed(f"{head} {line}"):
                hidden_level = head_level  # dòng này (nửa sau của nhãn) bị giấu cùng mục
            else:
                kept.append(head)
                kept.extend(pending_blanks)
            pending_blanks.clear()
        if hidden_level:
            if not heading or level > hidden_level or not _REAL_HEADING.match(stripped):
                continue
            hidden_level = 0
        if not stripped:
            if block:
                blanks.append(line)
            else:
                kept.append(line)
            continue
        if indented and _REAL_HEADING.match(stripped):
            if _is_unconfirmed(line):
                # Tiêu đề lỡ thụt lề mà có nhãn: vẫn giấu cả mục (SL-T032-2).
                heading = True
            elif _ends_with_partial_tag(line) and not (
                block and (_ends_with_partial_tag(block[-1]) or block_is_tagged())
            ):
                # Tiêu đề lỡ thụt lề có nửa nhãn ở cuối: chờ dòng kế như tiêu đề thường
                # (SL-T032-5). Dòng trước còn nửa nhãn thì dòng này có thể là nửa sau của nhãn
                # đó: để nó nối vào khối trước như cũ, không tách ra làm khối trước lọt. Khối
                # trước đã có nhãn thì cũng không tách: tách ra thì các dòng thụt lề phía sau
                # (vẫn thuộc ý có nhãn) thành khối mới không nhãn và tới AI (LC-T043-1).
                heading = True
        if blanks and not indented:
            close_block()
        if heading or (not indented and _BULLET.match(stripped)):
            close_block()
        block.extend(blanks)
        blanks.clear()
        if heading:
            if _is_unconfirmed(line):
                hidden_level = level
            elif _ends_with_partial_tag(line):
                pending = (line, level)  # SL-T032-3
                continue
            block.append(line)
            close_block()
            continue
        block.append(line)
    # Hết file mà tiêu đề còn nửa nhãn: an toàn khi nghi ngờ, bỏ tiêu đề đó.
    close_block()
    return "\n".join(kept).strip()


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


def _ends_with_partial_tag(text: str) -> bool:
    """Cuối dòng là nửa đầu của nhãn, ví dụ «[CẦN XÁC», «(chưa», «[**CẦN», «[» (nhãn bị xuống
    dòng).

    Chỉ xét đoạn cuối dài ``_PARTIAL_TAG_MAX`` ký tự (sau khi gộp khoảng trắng), nên mỗi dòng
    tốn thời gian cố định dù có hàng nghìn ngoặc. Thử từng ngoặc mở trong đoạn đó.
    """
    tail = " ".join(_tag_text(text).split())[-_PARTIAL_TAG_MAX:]
    for start, ch in enumerate(tail):
        if ch not in "[(":
            continue
        rest = tail[start + 1 :]
        if not _PARTIAL_TAG_REST.fullmatch(rest):
            continue
        letters = re.sub(r"[^A-Z]", "", rest)
        if any(words.startswith(letters) for words in _TAG_WORDS):
            return True
    return False


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

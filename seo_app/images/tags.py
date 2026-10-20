"""Thẻ ảnh đọc từ tên thư mục (phiếu T-052, quyết định 3A, thiết kế T-046 mục 4–5).

Quy ước (chủ dự án chốt 3A): mỗi công trình một thư mục trong Google Drive, ví dụ
``CT012 - Cổng inox - Tân Phú/truoc/IMG_0001.jpg``. App đọc thẻ (mã công trình, hạng mục, khu
vực, trước/sau, nguồn thật/AI) từ **tên thư mục** và không ghi gì vào thư mục ảnh hay Drive. Thẻ
sửa tay chỉ nhớ trên máy đang dùng (``seo_app.storage.image_tags``).

Cách đọc một tên thư mục:

- Tách thành từng phần theo `` - `` (gạch ngang có khoảng trắng) và các dấu ``– — , ; | + & ( )
  [ ]``. Mỗi phần phải khớp **trọn vẹn** với danh sách cố định, hoặc là ghép của các mục trong
  danh sách (``CT012 Cổng inox Tân Phú``). Phần không khớp bị bỏ cả phần. Phần không khớp mà có
  gạch nối liền chữ hay gạch dưới (``CT012-Cổng inox-Nhà anh Tuấn``) thì thử lại từng mảnh.
- So không phân biệt hoa thường, có dấu hay không dấu, chữ dính liền (``TanPhu``, ``Q7``).
- Thư mục sâu hơn (gần ảnh hơn) quyết định thẻ của nó. Một thư mục ghi hai giá trị khác nhau cho
  cùng một thẻ (``Quận 7 - Tân Phú``) thì thẻ đó để trống, không đoán.

An toàn (góp ý Lá Chắn T-046 số 3; điều kiện Lá Chắn T-048 LC-T048-4a và T-050 số 5; A3):

- Tên thư mục là dữ liệu chưa tin cậy, có thể chứa tên, số điện thoại, địa chỉ khách. Module
  **không bao giờ trả lại chữ của tên thư mục**: mọi giá trị thẻ là chữ do code viết sẵn
  (danh sách quận/huyện, hạng mục, trước/sau) hoặc mã đúng mẫu ``CT`` + số. Phần không khớp chỉ
  được đếm (``FolderTags.unmatched``), nên không thể đi vào prompt AI, tên file, tiêu đề, chú
  thích. ``ImageTags`` tự kiểm lại điều này mỗi lần được tạo (kể cả từ cache, từ ô nhập).
- Trước khi so: bỏ ký tự vô hình/định dạng (Unicode Cf: U+200B, U+200F, U+061C, U+FEFF,
  U+FFF9–FFFB, khối thẻ U+E0000–E007F…), ngắt dòng/đoạn (Zl, Zp: U+2028, U+2029), ký tự điều
  khiển (Cc), surrogate lẻ (Cs), vùng riêng (Co), ký tự chưa gán (Cn); rồi chuẩn hóa NFKC.
- Chỉ đọc phần đường dẫn **bên dưới** thư mục ảnh đã khai báo: đầu vào là ``ImageRef`` của T-048
  (số thứ tự gốc + đường dẫn tương đối) hoặc đường dẫn tương đối đã qua đúng lớp kiểm của T-048.
  Không nhận đường dẫn tuyệt đối, nên tên ổ đĩa, ``Users/…``, ``My Drive/…`` và tên chính thư
  mục gốc không bao giờ được đọc. Tên file ảnh cũng không dùng.
- Ảnh AI luôn có ``source = "ai"`` và không mang mã công trình, khu vực, trước/sau (chỉ được giữ
  hạng mục). Thư mục có tên kiểu ``Ảnh AI`` thì mọi ảnh bên trong là ảnh AI.
- Module chỉ xử lý chữ: không đọc ổ đĩa, không mở hay ghi file.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from seo_app.images.folders import ImageRef, SubFolder
from seo_app.text import remove_accents

SOURCE_REAL = "that"  # ảnh thật (chụp công trình)
SOURCE_AI = "ai"  # ảnh do AI tạo
SOURCES = (SOURCE_REAL, SOURCE_AI)
PHASE_BEFORE = "truoc"
PHASE_AFTER = "sau"
PHASE_LABELS = {PHASE_BEFORE: "Trước khi làm", PHASE_AFTER: "Sau khi làm"}
SOURCE_LABELS = {SOURCE_REAL: "Ảnh thật", SOURCE_AI: "Ảnh AI"}
FIELD_LABELS = {
    "source": "Nguồn ảnh",
    "project_code": "Mã công trình",
    "category": "Hạng mục",
    "area": "Khu vực",
    "phase": "Trước/sau",
}
# Nhãn khi gửi kèm ảnh cho AI viết alt (``reference``). Không gửi mã công trình: AI không cần.
REFERENCE_LABELS = {"category": "Hạng mục", "area": "Khu vực", "phase": "Giai đoạn"}

MAX_CODE_DIGITS = 6  # CT + tối đa 6 chữ số (khớp ``seo_app/images/naming.py`` của T-049)
_CODE_PATTERN = re.compile(rf"CT[0-9]{{1,{MAX_CODE_DIGITS}}}")
_MAX_VALUE_CHARS = 300  # chữ dài hơn thì không phải một thẻ
_MAX_WORDS_PER_PART = 16
_MAX_CATEGORY_ITEMS = 6  # "Thay bánh xe cửa kéo inox" là 4 mục

# ----- danh sách cố định ---------------------------------------------------------------------
#
# Khu vực phục vụ (config/business_profile.md mục 3): mọi quận, huyện TP.HCM trước sáp nhập, cả
# Bình Dương và Bà Rịa – Vũng Tàu cũ. Quận 2, Quận 9 đã nhập vào Thủ Đức (2021) nhưng người ta
# vẫn gọi tên cũ. Long Điền và Đất Đỏ nhập thành Long Đất (2025): giữ cả ba tên.

HCM_AREAS = (
    "TP.HCM",
    *(f"Quận {number}" for number in range(1, 13)),
    "Bình Thạnh",
    "Gò Vấp",
    "Phú Nhuận",
    "Tân Bình",
    "Tân Phú",
    "Bình Tân",
    "Thủ Đức",
    "Bình Chánh",
    "Hóc Môn",
    "Củ Chi",
    "Nhà Bè",
    "Cần Giờ",
)
BINH_DUONG_AREAS = (
    "Bình Dương",
    "Thủ Dầu Một",
    "Dĩ An",
    "Thuận An",
    "Tân Uyên",
    "Bắc Tân Uyên",
    "Bến Cát",
    "Bàu Bàng",
    "Dầu Tiếng",
    "Phú Giáo",
)
BA_RIA_VUNG_TAU_AREAS = (
    "Bà Rịa – Vũng Tàu",
    "Vũng Tàu",
    "Bà Rịa",
    "Phú Mỹ",
    "Châu Đức",
    "Xuyên Mộc",
    "Long Điền",
    "Đất Đỏ",
    "Long Đất",
    "Côn Đảo",
)
# Cho giao diện chọn khu vực theo nhóm.
AREA_GROUPS = (
    ("TP.HCM", HCM_AREAS),
    ("Bình Dương (cũ)", BINH_DUONG_AREAS),
    ("Bà Rịa – Vũng Tàu (cũ)", BA_RIA_VUNG_TAU_AREAS),
)
AREAS = (*HCM_AREAS, *BINH_DUONG_AREAS, *BA_RIA_VUNG_TAU_AREAS)
_AREA_SET = frozenset(AREAS)

# Cách viết khác của tên tỉnh/thành (tên quận/huyện thì tự nhận có dấu hay không dấu).
_AREA_ALIASES = {
    "TP.HCM": (
        "HCM",
        "TPHCM",
        "Hồ Chí Minh",
        "TP Hồ Chí Minh",
        "Thành phố Hồ Chí Minh",
        "Sài Gòn",
        "Saigon",
    ),
    "Bình Dương": ("Tỉnh Bình Dương",),
    "Bà Rịa – Vũng Tàu": ("BRVT", "Tỉnh Bà Rịa – Vũng Tàu"),
}
# Chữ đứng trước tên quận/huyện: "Q.7", "Quận Tân Phú", "H. Củ Chi", "TP Thủ Đức", "TX Phú Mỹ".
_AREA_PREFIXES = (
    "Quận",
    "Q",
    "Huyện",
    "H",
    "Thành phố",
    "TP",
    "Thị xã",
    "TX",
    "District",
    "Dist",
)
_NUMBERED_PREFIXES = ("Quận", "Q", "District", "Dist")  # quận số bắt buộc có chữ đứng trước

_PHASE_WORDS = {
    PHASE_BEFORE: (
        "trước",
        "trước khi làm",
        "trước khi sửa",
        "trước khi thi công",
        "trước thi công",
        "hiện trạng",
        "before",
    ),
    PHASE_AFTER: (
        "sau",
        "sau khi làm",
        "sau khi sửa",
        "sau khi thi công",
        "sau thi công",
        "làm xong",
        "sửa xong",
        "hoàn thành",
        "hoàn thiện",
        "after",
    ),
}
_AI_WORDS = (
    "AI",
    "ảnh AI",
    "hình AI",
    "AI tạo",
    "ảnh AI tạo",
    "tạo bằng AI",
    "ảnh tạo bằng AI",
    "minh họa AI",
    "ảnh minh họa AI",
    "AI generated",
)

# Hạng mục = [việc] + vật + [vật liệu], ghép từ các từ dưới đây (theo dịch vụ ở
# config/business_profile.md mục 4). Giá trị thẻ là đúng các từ này nối lại, ví dụ "Cổng inox",
# "Sửa cửa kéo", "Thay bánh xe cửa kéo". Thêm từ mới: thêm vào danh sách và chạy lại test.
_CATEGORY_ACTIONS = (
    "sửa",
    "sửa chữa",
    "làm",
    "làm mới",
    "thi công",
    "lắp",
    "lắp đặt",
    "thay",
    "thay mới",
    "sơn",
    "sơn lại",
    "hàn",
    "bảo dưỡng",
    "bảo trì",
    "gia công",
    "cải tạo",
)
_CATEGORY_OBJECTS = (
    "cửa",
    "cổng",
    "cửa kéo",
    "cửa xếp",
    "cửa cuốn",
    "cửa sổ",
    "cửa đi",
    "cửa chính",
    "cửa lùa",
    "cửa trượt",
    "cổng xếp",
    "cổng trượt",
    "cổng lùa",
    "lan can",
    "cầu thang",
    "tay vịn",
    "mái hiên",
    "mái che",
    "mái tôn",
    "mái kính",
    "mái vòm",
    "hàng rào",
    "khung",
    "khung bảo vệ",
    "chuồng cọp",
    "song cửa",
    "bông gió",
    "vách ngăn",
    "nhà xưởng",
    "nhà tiền chế",
    "bản lề",
    "khóa",
    "ray",
    "bánh xe",
    "chốt",
    "tay nắm",
    "lá cửa",
    "mô tơ",
    "kệ",
    "giàn phơi",
)
_CATEGORY_MATERIALS = (
    "sắt",
    "inox",
    "nhôm",
    "kính",
    "nhôm kính",
    "kính cường lực",
    "Xingfa",
    "sắt mỹ thuật",
    "mỹ thuật",
    "sắt hộp",
    "mạ kẽm",
    "sắt mạ kẽm",
    "giả gỗ",
    "sắt giả gỗ",
    "gỗ",
    "thép",
    "tôn",
    "panel",
    "CNC",
    "tĩnh điện",
    "sơn tĩnh điện",
    "hoa văn",
)
_CATEGORY_ALIASES = {"Xingfa": ("Xing Fa",), "mô tơ": ("motor", "mô-tơ")}

# ----- làm sạch và tách chữ ------------------------------------------------------------------

# Bỏ hẳn (điều kiện Lá Chắn T-048 LC-T048-4a): điều khiển (Cc), định dạng/vô hình (Cf),
# surrogate lẻ (Cs), vùng riêng (Co), chưa gán (Cn), ngắt dòng (Zl), ngắt đoạn (Zp). Bỏ chứ không
# thay bằng dấu cách, nên chèn ký tự vô hình vào giữa chữ không đổi được kết quả. Các kiểu dấu
# cách khác (Zs: dấu cách không ngắt, dấu cách toàn chiều rộng…) thành dấu cách thường.
_DROP_CATEGORIES = frozenset({"Cc", "Cf", "Cs", "Co", "Cn", "Zl", "Zp"})
# Nối trong một phần (không tách phần): gạch nối liền chữ, gạch dưới, dấu chấm, nháy.
_JOINERS = frozenset("-_.'’")
# Các kiểu gạch nối ngắn (NFKC không đổi hết về "-"): coi như "-". Gạch dài – — tách phần.
_HYPHENS = str.maketrans(dict.fromkeys("\u2010\u2011\u2012\u2043\u2212\ufe63\uff0d", "-"))
_SPACED_HYPHEN = re.compile(r"\s+-+\s*|\s*-+\s+")
_PIECE_SPLIT = re.compile(r"[-_.]+")
_REAL_WORDS = frozenset({("that",), ("anh", "that"), ("hinh", "that")})  # ảnh thật


def clean_folder_name(value: object) -> str:
    """Tên thư mục đã bỏ ký tự vô hình/điều khiển/ngắt dòng và chuẩn hóa NFKC, gộp khoảng trắng.

    Chỉ dùng để so với danh sách cố định; chữ này vẫn là dữ liệu chưa tin cậy (giao diện muốn
    hiện thì phải escape như mọi tên thư mục khác).
    """
    if not isinstance(value, str):
        return ""
    text = _strip_hidden(value)
    text = _strip_hidden(unicodedata.normalize("NFKC", text))
    return " ".join(text.split())


def _strip_hidden(text: str) -> str:
    out = []
    for ch in text:
        if unicodedata.category(ch) not in _DROP_CATEGORIES:
            out.append(" " if ch.isspace() else ch)
    return "".join(out)


def _is_word_char(ch: str) -> bool:
    return ch.isalnum() or unicodedata.category(ch).startswith("M")


def _starts_new_word(prev: str, ch: str) -> bool:
    """Chữ dính liền: "TanPhu" → "Tan Phu", "Q7" → "Q 7", "CT012" → "CT 012"."""
    if prev.isdigit() != ch.isdigit() and prev.isalnum() and ch.isalnum():
        return True
    return prev.islower() and ch.isupper()


def _words(text: str) -> list[str]:
    """Các từ của ``text`` (đã làm sạch) ở dạng so: không dấu, chữ thường."""
    words: list[str] = []
    buffer: list[str] = []
    prev = ""
    for ch in text:
        if _is_word_char(ch):
            if buffer and _starts_new_word(prev, ch):
                words.append("".join(buffer))
                buffer = []
            buffer.append(ch)
        elif buffer:
            words.append("".join(buffer))
            buffer = []
        prev = ch
    if buffer:
        words.append("".join(buffer))
    return [remove_accents(word).casefold() for word in words]


# ----- từ điển -------------------------------------------------------------------------------

_AREA = "area"
_PHASE = "phase"
_CODE = "project_code"
_AI = "ai"
_ACTION = "action"
_OBJECT = "object"
_MATERIAL = "material"
_CATEGORY_KINDS = frozenset({_ACTION, _OBJECT, _MATERIAL})


@dataclass(frozen=True)
class _Item:
    kind: str
    value: str  # chữ do code viết sẵn (không bao giờ là chữ của tên thư mục)


def _build_vocabulary() -> dict[tuple[str, ...], _Item]:
    vocabulary: dict[tuple[str, ...], _Item] = {}

    def add(text: str, item: _Item, *, compact: bool = True) -> None:
        key = tuple(_words(clean_folder_name(text)))
        keys = [key]
        if compact and len(key) > 1:
            keys.append(("".join(key),))  # "tanphu", "conginox"…
        for one in keys:
            existing = vocabulary.setdefault(one, item)
            if existing != item:  # lỗi lập trình: hai mục cùng một cách viết
                raise RuntimeError(f"Trùng cách viết trong danh sách thẻ ảnh: {' '.join(one)}")

    for number in range(1, 13):
        item = _Item(_AREA, f"Quận {number}")
        for prefix in _NUMBERED_PREFIXES:
            add(f"{prefix} {number}", item, compact=False)
            add(f"{prefix} {number:02d}", item, compact=False)
    for area in AREAS:
        if area.startswith("Quận "):
            continue
        item = _Item(_AREA, area)
        names = (area, *_AREA_ALIASES.get(area, ()))
        for name in names:
            add(name, item)
            if area not in _AREA_ALIASES:  # chỉ quận/huyện mới có "Quận", "H.", "TP"…
                for prefix in _AREA_PREFIXES:
                    add(f"{prefix} {name}", item, compact=False)
    for phase, texts in _PHASE_WORDS.items():
        for text in texts:
            add(text, _Item(_PHASE, phase))
    for text in _AI_WORDS:
        add(text, _Item(_AI, SOURCE_AI))
    for kind, texts in (
        (_ACTION, _CATEGORY_ACTIONS),
        (_OBJECT, _CATEGORY_OBJECTS),
        (_MATERIAL, _CATEGORY_MATERIALS),
    ):
        for text in texts:
            item = _Item(kind, text)
            for name in (text, *_CATEGORY_ALIASES.get(text, ())):
                add(name, item)
    return vocabulary


_VOCABULARY = _build_vocabulary()
_MAX_KEY_WORDS = max(len(key) for key in _VOCABULARY)


def _code_at(words: Sequence[str], index: int) -> _Item | None:
    """Mã công trình ở vị trí ``index``: "ct" rồi 1–6 chữ số ASCII ("CT012", "ct 12", "CT-012")."""
    if words[index] != "ct" or index + 1 >= len(words):
        return None
    digits = words[index + 1]
    if not (digits.isascii() and digits.isdigit() and 1 <= len(digits) <= MAX_CODE_DIGITS):
        return None
    return _Item(_CODE, f"CT{digits}")


def _segment(words: Sequence[str]) -> list[_Item] | None:
    """Chia ``words`` thành các mục trong từ điển, phủ **trọn** mọi từ; ít mục nhất (cụm dài
    nhất trước). Không chia được thì ``None``."""
    count = len(words)
    if not 0 < count <= _MAX_WORDS_PER_PART:
        return None
    best: list[list[_Item] | None] = [None] * (count + 1)
    best[count] = []
    for start in range(count - 1, -1, -1):
        options: list[tuple[int, _Item]] = []
        for length in range(min(_MAX_KEY_WORDS, count - start), 0, -1):
            item = _VOCABULARY.get(tuple(words[start : start + length]))
            if item is not None:
                options.append((length, item))
        code = _code_at(words, start)
        if code is not None:
            options.append((2, code))
        for length, item in options:
            rest = best[start + length]
            if rest is None:
                continue
            current = best[start]
            if current is None or len(rest) + 1 < len(current):
                best[start] = [item, *rest]
    return best[0]


def _category_text(run: Sequence[_Item]) -> str:
    text = " ".join(item.value for item in run)
    return text[:1].upper() + text[1:]


# ----- thẻ -----------------------------------------------------------------------------------


class TagError(ValueError):
    """Thẻ không hợp lệ. Câu tiếng Việt hiện thẳng được; không chép lại chữ đã nhập."""


@dataclass(frozen=True)
class ImageTags:
    """Thẻ của một ảnh. Mọi giá trị đều thuộc danh sách cố định (kiểm lúc tạo).

    - ``source``: ``"that"`` (ảnh thật) hoặc ``"ai"`` (ảnh AI).
    - ``project_code``: ``"CT012"`` (``CT`` + 1–6 chữ số) hoặc rỗng.
    - ``category``: hạng mục ghép từ danh sách, ví dụ ``"Cổng inox"``, hoặc rỗng.
    - ``area``: một tên trong ``AREAS``, ví dụ ``"Tân Phú"``, ``"Quận 7"``, hoặc rỗng.
    - ``phase``: ``"truoc"``, ``"sau"`` hoặc rỗng.

    Ảnh AI không được mang mã công trình, khu vực, trước/sau (thiết kế T-046 mục 4).
    """

    source: str = SOURCE_REAL
    project_code: str = ""
    category: str = ""
    area: str = ""
    phase: str = ""

    def __post_init__(self) -> None:
        for name in FIELD_LABELS:
            if type(getattr(self, name)) is not str:
                raise TagError(f"Thẻ «{FIELD_LABELS[name]}» không hợp lệ.")
        if self.source not in SOURCES:
            raise TagError("Nguồn ảnh phải là ảnh thật hoặc ảnh AI.")
        if self.project_code and not _CODE_PATTERN.fullmatch(self.project_code):
            raise TagError("Mã công trình phải có dạng CT và số, ví dụ CT012.")
        if self.area and self.area not in _AREA_SET:
            raise TagError("Khu vực phải là một quận/huyện trong danh sách.")
        if self.phase and self.phase not in PHASE_LABELS:
            raise TagError("Thẻ trước/sau chỉ nhận «trước» hoặc «sau».")
        if self.category and match_category(self.category) != self.category:
            raise TagError("Hạng mục phải ghép từ danh sách hạng mục có sẵn.")
        if self.source == SOURCE_AI and (self.project_code or self.area or self.phase):
            raise TagError(
                "Ảnh AI không được gắn mã công trình, khu vực hay trước/sau của công trình thật."
            )

    @classmethod
    def from_input(
        cls,
        *,
        source: str = SOURCE_REAL,
        project_code: str = "",
        category: str = "",
        area: str = "",
        phase: str = "",
    ) -> ImageTags:
        """Thẻ từ ô nhập của người dùng (thẻ sửa tay): chuẩn hóa từng ô theo danh sách cố định
        ("ct 12" → "CT12", "q7" → "Quận 7", "cổng INOX" → "Cổng inox", "truoc" → "truoc").

        Ô nào có chữ mà không khớp danh sách thì báo ``TagError`` nêu tên ô (không chép lại chữ).
        """
        fields = (
            ("source", source, match_source),
            ("project_code", project_code, match_project_code),
            ("category", category, match_category),
            ("area", area, match_area),
            ("phase", phase, match_phase),
        )
        normalized: dict[str, str] = {}
        bad: list[str] = []
        for name, value, matcher in fields:
            matched = matcher(value) if clean_folder_name(value) else ""
            if not matched and (not isinstance(value, str) or clean_folder_name(value)):
                bad.append(FIELD_LABELS[name])
            normalized[name] = matched
        if bad:
            raise TagError(f"Không có trong danh sách: {', '.join(bad)}. Hãy chọn hoặc sửa lại.")
        normalized["source"] = normalized["source"] or SOURCE_REAL
        return cls(**normalized)

    @classmethod
    def for_ai_image(cls, category: str = "") -> ImageTags:
        """Thẻ của ảnh AI: chỉ có hạng mục (nếu khớp danh sách)."""
        return cls.from_input(source=SOURCE_AI, category=category)

    @property
    def is_ai(self) -> bool:
        return self.source == SOURCE_AI

    @property
    def is_empty(self) -> bool:
        """Không có thẻ nội dung nào (chỉ có nguồn ảnh)."""
        return not (self.project_code or self.category or self.area or self.phase)

    def reference(self) -> dict[str, str]:
        """Thẻ gửi kèm ảnh cho AI viết alt (``suggest_alt(tags=…)``): hạng mục, khu vực,
        trước/sau. Không gửi mã công trình. Ảnh AI không gửi thẻ nào."""
        if self.is_ai:
            return {}
        values = {
            "category": self.category,
            "area": self.area,
            "phase": PHASE_LABELS.get(self.phase, ""),
        }
        return {REFERENCE_LABELS[name]: value for name, value in values.items() if value}


@dataclass(frozen=True)
class FolderTags:
    """Thẻ đọc từ tên thư mục của một ảnh (hoặc một thư mục).

    ``unmatched``: số phần tên thư mục không khớp danh sách, đã bỏ (chỉ đếm, không giữ chữ).
    ``conflicts``: tên các thẻ để trống vì một thư mục ghi hai giá trị khác nhau.
    """

    tags: ImageTags = field(default_factory=ImageTags)
    unmatched: int = 0
    conflicts: tuple[str, ...] = ()


# ----- so một giá trị với danh sách --------------------------------------------------------


def _value_items(value: object) -> list[_Item] | None:
    text = clean_folder_name(value)
    if not text or len(text) > _MAX_VALUE_CHARS:
        return None
    return _segment(_words(text))


def _one(value: object, kind: str) -> str:
    items = _value_items(value)
    if not items or len(items) != 1 or items[0].kind != kind:
        return ""
    return items[0].value


def match_area(value: object) -> str:
    """Tên chuẩn của khu vực ("q.7" → "Quận 7", "tan phu" → "Tân Phú"); không khớp: rỗng."""
    return _one(value, _AREA)


def match_phase(value: object) -> str:
    """``"truoc"`` / ``"sau"`` ("Trước khi sửa" → "truoc", "hoàn thành" → "sau"); không khớp:
    rỗng."""
    return _one(value, _PHASE)


def match_project_code(value: object) -> str:
    """Mã công trình chuẩn ("ct 012" → "CT012"); sai mẫu ``CT`` + 1–6 chữ số: rỗng."""
    return _one(value, _CODE)


def match_source(value: object) -> str:
    """``"that"`` hoặc ``"ai"`` (nhận cả "ảnh AI", "Ảnh thật"); không khớp: rỗng."""
    words = tuple(_words(clean_folder_name(value)))
    if words in _REAL_WORDS:
        return SOURCE_REAL
    return _one(value, _AI)


def match_category(value: object) -> str:
    """Hạng mục chuẩn ghép từ danh sách ("cong INOX" → "Cổng inox"); không khớp: rỗng.

    Phải có ít nhất một vật hoặc vật liệu ("Sửa" một mình không phải hạng mục)."""
    items = _value_items(value)
    if (
        not items
        or len(items) > _MAX_CATEGORY_ITEMS
        or any(item.kind not in _CATEGORY_KINDS for item in items)
        or all(item.kind == _ACTION for item in items)
    ):
        return ""
    return _category_text(items)


# ----- đọc thẻ từ tên thư mục ----------------------------------------------------------------


@dataclass
class _DirTags:
    values: dict[str, list[str]] = field(
        default_factory=lambda: {"project_code": [], "category": [], "area": [], "phase": []}
    )
    ai: bool = False
    unmatched: int = 0

    def add(self, items: Sequence[_Item]) -> None:
        run: list[_Item] = []
        for item in (*items, None):
            if item is not None and item.kind in _CATEGORY_KINDS:
                run.append(item)
                continue
            if run and len(run) <= _MAX_CATEGORY_ITEMS and any(i.kind != _ACTION for i in run):
                self.values["category"].append(_category_text(run))
            run = []
            if item is None:
                break
            if item.kind == _AI:
                self.ai = True
            else:
                self.values[item.kind].append(item.value)


def _split_parts(text: str) -> list[str]:
    """Tách tên đã làm sạch thành các phần (xem docstring module)."""
    text = _SPACED_HYPHEN.sub("|", text.translate(_HYPHENS))
    parts: list[str] = []
    buffer: list[str] = []
    for ch in text:
        if _is_word_char(ch) or ch == " " or ch in _JOINERS:
            buffer.append(ch)
        else:
            parts.append("".join(buffer))
            buffer = []
    parts.append("".join(buffer))
    return [part for part in parts if _words(part)]


def _parse_dir_name(name: str) -> _DirTags:
    result = _DirTags()
    for part in _split_parts(clean_folder_name(name)):
        items = _segment(_words(part))
        if items is not None:
            result.add(items)
            continue
        pieces = [piece for piece in _PIECE_SPLIT.split(part) if _words(piece)]
        if len(pieces) < 2:
            result.unmatched += 1
            continue
        for piece in pieces:
            piece_items = _segment(_words(piece))
            if piece_items is None:
                result.unmatched += 1
            else:
                result.add(piece_items)
    return result


def _tags_from_dirs(dir_names: Iterable[str]) -> FolderTags:
    """Ghép thẻ của các thư mục từ gốc xuống: thư mục sâu hơn quyết định; một thư mục ghi hai giá
    trị khác nhau thì thẻ đó để trống; có thư mục ảnh AI thì cả nhánh là ảnh AI."""
    chosen = {"project_code": "", "category": "", "area": "", "phase": ""}
    decided: set[str] = set()
    conflicts: list[str] = []
    unmatched = 0
    ai = False
    for name in reversed(tuple(dir_names)):
        parsed = _parse_dir_name(name)
        unmatched += parsed.unmatched
        ai = ai or parsed.ai
        for key, values in parsed.values.items():
            if key in decided or not values:
                continue
            decided.add(key)
            distinct = list(dict.fromkeys(values))
            if len(distinct) == 1:
                chosen[key] = distinct[0]
            else:
                conflicts.append(key)
    if ai:
        # Ảnh AI không mang thẻ công trình thật (thiết kế T-046 mục 4).
        for key in ("project_code", "area", "phase"):
            chosen[key] = ""
        conflicts = [key for key in conflicts if key == "category"]
    tags = ImageTags(source=SOURCE_AI if ai else SOURCE_REAL, **chosen)
    return FolderTags(tags=tags, unmatched=unmatched, conflicts=tuple(sorted(conflicts)))


def tags_for_image(ref: ImageRef) -> FolderTags:
    """Thẻ của một ảnh, đọc từ các thư mục **bên dưới** thư mục gốc chứa ảnh.

    Nhận ``ImageRef`` của T-048 (đường dẫn tương đối, đã kiểm), không nhận đường dẫn tuyệt đối:
    tên thư mục gốc, tên ổ đĩa, ``Users/…``, ``My Drive/…`` không bao giờ được đọc. Không dùng
    tên file ảnh. Không đọc ổ đĩa.
    """
    if not isinstance(ref, ImageRef):
        raise TypeError("tags_for_image chỉ nhận ImageRef (đường dẫn tương đối trong thư mục ảnh).")
    return _tags_from_dirs(ref.parts[:-1])


def tags_for_folder(folder: str | SubFolder) -> FolderTags:
    """Thẻ của một thư mục con (``SubFolder`` hoặc ``SubFolder.rel_path`` /
    ``FolderListing.rel_dir``: đường dẫn tương đối so với thư mục gốc, dạng ``a/b``).

    Đường dẫn được kiểm bằng đúng lớp kiểm của ``ImageRef`` (T-048): ``..``, ổ đĩa, đường dẫn
    tuyệt đối, ký tự lạ bị từ chối bằng ``ImageFolderError``.
    """
    rel_dir = folder.rel_path if isinstance(folder, SubFolder) else folder
    if not isinstance(rel_dir, str):
        raise TypeError("tags_for_folder chỉ nhận đường dẫn tương đối dạng chữ.")
    if rel_dir == "":
        return FolderTags()
    # Mượn ImageRef để kiểm đường dẫn: thêm một tên file giả hợp lệ ở cuối rồi bỏ đi.
    ref = ImageRef(0, f"{rel_dir}/_.jpg")
    return _tags_from_dirs(ref.parts[:-1])


__all__ = [
    "AREAS",
    "AREA_GROUPS",
    "BA_RIA_VUNG_TAU_AREAS",
    "BINH_DUONG_AREAS",
    "FIELD_LABELS",
    "HCM_AREAS",
    "PHASE_AFTER",
    "PHASE_BEFORE",
    "PHASE_LABELS",
    "REFERENCE_LABELS",
    "SOURCES",
    "SOURCE_AI",
    "SOURCE_LABELS",
    "SOURCE_REAL",
    "FolderTags",
    "ImageTags",
    "TagError",
    "clean_folder_name",
    "match_area",
    "match_category",
    "match_phase",
    "match_project_code",
    "match_source",
    "tags_for_folder",
    "tags_for_image",
]

"""Kho nháp cục bộ cho bài đang soạn (SQLite có sẵn của Python, không thêm thư viện).

Mỗi nháp là một ``DraftSnapshot`` lưu dạng JSON trong một dòng của bảng ``drafts``. Dữ liệu
đọc từ file được coi là chưa tin cậy: giới hạn kích thước, kiểm khuôn bằng pydantic; nháp hỏng
thì bỏ qua và báo lỗi tiếng Việt, không làm sập app. File hỏng hẳn (không phải SQLite) được
đổi tên sang một bên để giữ lại, rồi tạo file mới.

Không dùng ``pickle``; mọi câu SQL dùng tham số ``?``. Khuôn không có chỗ nào cho khóa API
hay mật khẩu, và ``extra="forbid"`` chặn mọi trường lạ.

Ảnh đã chọn cho chỗ cần ảnh (T-055, khuôn 2; thiết kế T-046 mục 7 G3-9):

- Mỗi phần của bài nhớ một ``DraftImage``: ảnh trong thư mục ảnh hoặc ảnh tạo bằng AI, nguồn
  ảnh (thật/AI), hạng mục, alt và cờ đã duyệt, chú thích, prompt ảnh AI.
- Ảnh trong thư mục ảnh chỉ lưu ``ImageRef`` của T-048 (số thứ tự thư mục gốc, đường dẫn tương
  đối), không bao giờ lưu đường dẫn tuyệt đối (F1): ``ImageRef(...)`` kiểm lại mỗi lần tạo, kể cả
  khi đọc nháp. Khi mở nháp, ``check_draft_images`` dựng lại ``ImageRef`` rồi hỏi
  ``ImageLibrary.stat_image`` (thư mục gốc còn khai báo không, file còn không, có đi qua liên kết
  không), không tin số thứ tự gốc ghi trong nháp. Từ đó dùng ``ImageRef`` theo tên trên ổ mà
  ``stat_image`` trả (T-076), không theo chữ hoa thường trong nháp, để thẻ đọc từ tên thư mục thật
  (SL-T055-1, LC-T055-1).
- Nháp là dữ liệu chưa tin cậy (góp ý Lá Chắn T-046 số 11, điều kiện Lá Chắn T-048 và T-052): thẻ
  dựng lại qua ``ImageTags(...)``; nguồn ảnh nghiêng về ảnh AI (nháp ghi AI **hoặc** thẻ hiện tại
  nói AI thì là ảnh AI; nháp không bao giờ kéo ảnh AI về ảnh thật); alt, chú thích, prompt là chữ
  thường có giới hạn độ dài, chỉ được lọc và hiện, không chạy gì.
- Nháp khuôn 1 (chưa có ảnh) vẫn mở được. Dữ liệu ảnh hỏng (sửa tay, sai khuôn) chỉ làm mất ảnh
  đó (``DraftSnapshot.dropped_images`` đếm), phần chữ của bài giữ nguyên.

Trạng thái «Gửi nháp» (T-086, SL-T056-8, -11): ``SendState`` lưu ở bảng riêng ``send_states``
(không nằm trong JSON của nháp), nên lần tự lưu nháp không ghi đè, giờ lưu nháp không đổi, và nháp
cũ (không có dòng nào) vẫn mở như trước. Giao diện ghi «đang gửi» **trước** khi gửi, ghi kết quả
ngay khi có, đọc lại khi vẽ nút gửi (kể cả sau khi mở lại nháp, tải lại trang).
"""

from __future__ import annotations

import re
import sqlite3
import unicodedata
import uuid
from collections.abc import Collection, Iterable, Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    ValidationError,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    field_validator,
    model_validator,
)
from pydantic_core import PydanticSerializationError  # đi kèm pydantic, không phải thư viện mới

from seo_app.ai.base import AIError
from seo_app.config import DEFAULT_TIMEZONE, PROJECT_ROOT
from seo_app.content.models import OutlineItem, Research, Review
from seo_app.content.workflow import clean_ai_line, clean_research, clean_review
from seo_app.images.alt import (
    AI_ALT_PREFIX,
    AI_CAPTION_PREFIX,
    AltSuggestion,
    clean_alt_text,
    clean_suggestion,
)
from seo_app.images.folders import (
    MAX_REL_PATH_CHARS,
    ImageEntry,
    ImageFolderError,
    ImageLibrary,
    ImageRef,
    SubFolder,
)
from seo_app.images.tags import SOURCE_AI, SOURCE_REAL, ImageTags, TagError, tags_for_image
from seo_app.sanitize import clean_ai_text, escape_link_syntax, strip_tags, unescape_link_syntax

if TYPE_CHECKING:
    from seo_app.storage.image_tags import ImageTagStore

DEFAULT_DRAFTS_FILE = PROJECT_ROOT / "data" / "drafts.sqlite"
MAX_DRAFTS = 30
MAX_DRAFT_BYTES = 5 * 1024 * 1024  # một nháp (JSON, UTF-8) không quá 5 MB
STEP_COUNT = 5  # Chuẩn bị · Dàn ý · Viết & kiểm tra · SEO · Xuất bản
# 1: chữ của bài (T-016). 2: thêm ảnh đã chọn cho chỗ cần ảnh (T-055).
SCHEMA_VERSION = 2
_OLD_SCHEMA_VERSIONS = frozenset({1})  # vẫn mở được, nâng lên SCHEMA_VERSION khi mở
_ID_PATTERN = re.compile(r"[0-9a-f]{32}")
_SQLITE_TIMEOUT = 5  # giây chờ khi file đang bị một lần lưu khác giữ

# Ảnh đã chọn (T-055). Số thứ tự thư mục gốc lớn hơn mức này không thể do app ghi: bỏ ảnh đó.
# Số trong khoảng mà thư mục chưa khai báo thì giữ, ``check_draft_images`` báo "không có".
MAX_ROOT_INDEX = 999
# Giới hạn lưu trữ (ký tự, sau khi lọc). Rộng hơn giới hạn viết alt trong config/content.toml
# (mặc định 125 và 200) để đổi cấu hình không cắt mất alt đã duyệt; giao diện kiểm lại theo cấu
# hình trước khi dùng.
MAX_ALT_CHARS = 500
MAX_CAPTION_CHARS = 1000
MAX_PROMPT_CHARS = 4000
_RAW_TEXT_FACTOR = 4  # chữ thô dài hơn giới hạn × số này thì cắt bớt trước khi lọc (đỡ tốn công)
_MAX_CATEGORY_CHARS = 300  # như ``seo_app.images.tags``: dài hơn thì không phải một thẻ
# Khóa ``context`` khi đọc nháp từ file: ảnh hỏng thì bỏ ảnh và ghi vào danh sách này.
_DROPPED_IMAGES = "dropped_images"
# Danh sách thư mục không xác nhận được tên thư mục chứa ảnh, hay cho tên khác mà ảnh ở tên đó
# không phải ảnh vừa kiểm (SL-T055-1, LC-T055-2). Không có đường dẫn máy. Cách làm lại là đi từ
# thư mục ảnh gốc xuống, không mở thư mục theo đường dẫn ghi trong nháp (LC-T055-1).
_MSG_FOLDER_NAME = (
    "Chưa kiểm được tên thư mục chứa ảnh này (thư mục vừa đổi tên hoặc ảnh vừa thay đổi trong lúc "
    "kiểm). Hãy mở lại từ thư mục ảnh gốc rồi chọn lại ảnh."
)
# Trạng thái gửi (T-086): một dòng JSON vài chục byte; lớn hơn mức này là bị sửa tay, hỏng.
MAX_SEND_STATE_BYTES = 4096
_MSG_SEND_STATE_BROKEN = "Trạng thái gửi ghi trong nháp bị hỏng nên không đọc được."
# Prompt: bỏ ký tự điều khiển (trừ xuống dòng, tab), ký tự vô hình/định dạng (kể cả ký tự đảo
# hướng chữ), surrogate lẻ (không ghi được ra UTF-8).
_PROMPT_DROP = frozenset({"Cc", "Cf", "Cs"})
_category = unicodedata.category


class DraftError(Exception):
    """Lỗi kho nháp; thông báo tiếng Việt, hiện thẳng được cho người dùng."""


def new_draft_id() -> str:
    """Mã nháp mới: 32 ký tự hex ngẫu nhiên."""
    return uuid.uuid4().hex


def _check_id(draft_id: str) -> str:
    if not isinstance(draft_id, str) or not _ID_PATTERN.fullmatch(draft_id):
        raise DraftError("Mã nháp không hợp lệ.")
    return draft_id


# ---------------------------------------------------------------------- khuôn


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


def _drop_surrogates(text: str) -> str:
    """Bỏ surrogate lẻ: không ghi được ra UTF-8 (lưu nháp báo "ký tự lạ"), giao diện lỗi khi
    hiện."""
    return "".join(ch for ch in text if _category(ch) != "Cs")


def _one_line(value: object, limit: int) -> object:
    """Alt, chú thích: lọc như chữ AI (``clean_alt_text``: bỏ thẻ HTML, link, ký tự vô hình; một
    dòng), tối đa ``limit`` ký tự. Không phải chữ thì trả nguyên để pydantic báo sai khuôn."""
    if not isinstance(value, str):
        return value
    return clean_alt_text(_drop_surrogates(value[: limit * _RAW_TEXT_FACTOR]), limit)


def _clean_prompt(value: object) -> object:
    """Prompt ảnh AI: giữ nhiều dòng, bỏ ký tự điều khiển/vô hình, tối đa ``MAX_PROMPT_CHARS``.

    Chỉ là chữ để hiện (ô sửa, ``st.code``) và gửi cho AI tạo ảnh khi người dùng bấm; không bỏ thẻ
    HTML hay escape (chữ trong ô sửa không phải Markdown, bản sao chép phải đúng chữ).
    """
    if not isinstance(value, str):
        return value
    text = value[: MAX_PROMPT_CHARS * _RAW_TEXT_FACTOR]
    text = unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))
    kept = "".join(ch for ch in text if ch in "\n\t" or _category(ch) not in _PROMPT_DROP)
    return kept.strip()[:MAX_PROMPT_CHARS].rstrip()


def _ai_tags(category: str) -> ImageTags:
    """Thẻ ảnh AI (chỉ có hạng mục), dựng qua ``ImageTags(...)``; hạng mục sai thì bỏ trống."""
    try:
        return ImageTags(source=SOURCE_AI, category=category)
    except TagError:
        return ImageTags(source=SOURCE_AI)


def _ai_prefixed(text: str, *, caption: bool = False) -> str:
    """Alt (hay chú thích) của ảnh AI bắt đầu bằng đúng một tiền tố «Minh họa» (hay «Ảnh minh họa
    (AI)»), ghép bằng chính hàm của luồng gợi ý alt (``clean_suggestion``, quy tắc C6 Lá Chắn
    T-051): bỏ tiền tố tự viết, cắt phần thân theo ranh giới từ, ghi lại tiền tố chuẩn. Bỏ tiền tố
    rồi không còn chữ nào (alt chỉ là «minh họa», «???») thì trả chuỗi rỗng."""
    try:
        fixed = clean_suggestion(
            AltSuggestion(alt=text, caption=text),
            ai_generated=True,
            max_chars=MAX_ALT_CHARS,
            caption_max_chars=MAX_CAPTION_CHARS,
        )
    except AIError:
        return ""
    return fixed.caption if caption else fixed.alt


class DraftImage(_Strict):
    """Ảnh đã chọn cho một chỗ cần ảnh (T-055).

    Hai loại:

    - **Ảnh trong thư mục ảnh** (ảnh thật, hoặc ảnh AI người dùng để trong thư mục): ``root_index``
      và ``rel_path`` là ``ImageRef`` của T-048, kiểm bằng chính ``ImageRef(...)`` mỗi lần tạo
      (chặn ``..``, ổ đĩa, đường dẫn tuyệt đối, UNC…). Không bao giờ lưu đường dẫn tuyệt đối (F1).
      Tạo bằng ``DraftImage.from_library`` từ kết quả quét.
    - **Ảnh tạo bằng AI** (``root_index`` là ``None``): chỉ lưu prompt, không lưu ảnh hay đường dẫn.
      Luôn là ảnh AI.

    Nguồn ảnh nghiêng về ảnh AI: chỉ đúng chữ ``"that"`` mới là ảnh thật, mọi giá trị khác đọc
    thành ``"ai"``. Hạng mục chỉ nhận giá trị ``ImageTags`` chấp nhận (sai thì bỏ trống, không giữ
    chữ lạ). Alt, chú thích: một dòng, đã lọc, tối đa ``MAX_ALT_CHARS``/``MAX_CAPTION_CHARS``; alt
    rỗng thì không thể "đã duyệt". Prompt: nhiều dòng, tối đa ``MAX_PROMPT_CHARS``.
    """

    source: str = SOURCE_AI
    root_index: int | None = Field(default=None, strict=True, ge=0, le=MAX_ROOT_INDEX)
    rel_path: str = Field(default="", max_length=MAX_REL_PATH_CHARS)
    category: str = ""
    alt: str = ""
    alt_approved: bool = Field(default=False, strict=True)
    caption: str = ""
    prompt: str = ""

    @field_validator("source", mode="before")
    @classmethod
    def _source_or_ai(cls, value: object) -> str:
        return SOURCE_REAL if isinstance(value, str) and value == SOURCE_REAL else SOURCE_AI

    @field_validator("category", mode="before")
    @classmethod
    def _known_category(cls, value: object) -> str:
        # Dựng lại qua ImageTags (tự kiểm theo danh sách hạng mục cố định, điều kiện Lá Chắn T-052).
        if not isinstance(value, str) or not value or len(value) > _MAX_CATEGORY_CHARS:
            return ""
        try:
            return ImageTags(category=value).category
        except TagError:
            return ""

    @field_validator("alt", mode="before")
    @classmethod
    def _clean_alt(cls, value: object) -> object:
        return _one_line(value, MAX_ALT_CHARS)

    @field_validator("caption", mode="before")
    @classmethod
    def _clean_caption(cls, value: object) -> object:
        return _one_line(value, MAX_CAPTION_CHARS)

    @field_validator("prompt", mode="before")
    @classmethod
    def _clean_prompt_text(cls, value: object) -> object:
        return _clean_prompt(value)

    @model_validator(mode="after")
    def _check_place(self) -> DraftImage:
        if self.root_index is None:
            if self.rel_path:
                raise ValueError("đường dẫn ảnh thiếu số thứ tự thư mục gốc")
            self.source = SOURCE_AI  # ảnh tạo bằng AI không bao giờ là ảnh thật
        else:
            try:
                ImageRef(self.root_index, self.rel_path)
            except ImageFolderError:
                raise ValueError("đường dẫn ảnh không hợp lệ") from None
        if not self.alt:
            self.alt_approved = False
        return self

    @classmethod
    def from_library(
        cls,
        image: ImageRef | ImageEntry,
        tags: ImageTags,
        *,
        alt: str = "",
        alt_approved: bool = False,
        caption: str = "",
        prompt: str = "",
    ) -> DraftImage:
        """Ảnh chọn từ thư mục ảnh. ``image``: ``ImageEntry``/``ImageRef`` **của kết quả quét**
        (khóa lựa chọn, điều kiện Lá Chắn T-048); ``tags``: thẻ đang dùng cho ảnh (``resolve``)."""
        ref = image.ref if isinstance(image, ImageEntry) else image
        if not isinstance(ref, ImageRef) or not isinstance(tags, ImageTags):
            raise TypeError("from_library cần ImageRef (hoặc ImageEntry) và ImageTags.")
        return cls(
            source=tags.source,
            root_index=ref.root_index,
            rel_path=ref.rel_path,
            category=tags.category,
            alt=alt,
            alt_approved=alt_approved,
            caption=caption,
            prompt=prompt,
        )

    @property
    def is_generated(self) -> bool:
        """Ảnh tạo bằng AI (không nằm trong thư mục ảnh)."""
        return self.root_index is None

    @property
    def ref(self) -> ImageRef | None:
        """``ImageRef`` dựng lại (đã kiểm dạng chữ); ảnh tạo bằng AI: ``None``. Muốn biết ảnh còn
        dùng được trên máy này không thì dùng ``check_draft_images``."""
        if self.root_index is None:
            return None
        return ImageRef(self.root_index, self.rel_path)


def _ai_wording(image: DraftImage) -> DraftImage:
    """Chữ đi kèm ảnh AI: alt bắt đầu «Minh họa», chú thích bắt đầu «Ảnh minh họa (AI)» (quy tắc C6
    Lá Chắn T-051, SL-T055-2). Code bảo đảm, không trông vào người hay AI.

    Alt duyệt khi ảnh còn là ảnh thật (hay nháp sửa tay) tả ảnh như công trình thật: thêm tiền tố
    **và** bỏ "đã duyệt", vì chữ đã đổi không còn là chữ người dùng đã duyệt, người dùng đọc lại
    rồi duyệt (hay bấm gợi ý lại với ``ai_generated=True``). Alt, chú thích đã có tiền tố thì giữ
    nguyên, kể cả "đã duyệt"; alt, chú thích trống thì để trống.
    """
    update: dict[str, object] = {}
    if image.alt and not image.alt.startswith(AI_ALT_PREFIX):
        update.update(alt=_ai_prefixed(image.alt), alt_approved=False)
    if image.caption and not image.caption.startswith(AI_CAPTION_PREFIX):
        update["caption"] = _ai_prefixed(image.caption, caption=True)
    if not update:
        return image
    return DraftImage.model_validate({**image.model_dump(), **update})


class DraftPart(_Strict):
    """Một phần của bài: tiêu đề, mọi phiên bản (để quay lại bản trước) và bản đang chọn."""

    heading: str
    versions: list[str] = Field(min_length=1)
    current: int = Field(default=0, ge=0)
    image: str = ""  # mô tả chỗ cần ảnh; trống nếu phần này không cần ảnh
    chosen_image: DraftImage | None = None  # ảnh đã chọn cho chỗ cần ảnh (T-055)

    @field_validator("versions")
    @classmethod
    def _escape_versions(cls, versions: list[str]) -> list[str]:
        # Thân bài trong session luôn ở dạng đã escape link. Chạy lại (idempotent, bản đúng
        # không đổi) để file bị sửa tay cũng không chèn được link Markdown vào bài.
        return [escape_link_syntax(text) for text in versions]

    @field_validator("chosen_image", mode="wrap")
    @classmethod
    def _drop_broken_image(
        cls, value: object, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
    ) -> DraftImage | None:
        """Đọc nháp từ file (``DraftStore.load``): ảnh sai khuôn thì bỏ riêng ảnh đó và đếm, phần
        chữ của bài giữ nguyên. Tạo trong code (giao diện, ``save``): sai khuôn là lỗi, báo ngay."""
        try:
            return handler(value)
        except ValidationError:
            dropped = (info.context or {}).get(_DROPPED_IMAGES)
            if not isinstance(dropped, list):
                raise
            dropped.append(info.field_name)
            return None

    @model_validator(mode="after")
    def _current_in_range(self) -> DraftPart:
        if self.current >= len(self.versions):
            raise ValueError("phiên bản đang chọn nằm ngoài danh sách phiên bản")
        return self

    @property
    def text(self) -> str:
        return self.versions[self.current]


class DraftSnapshot(_Strict):
    """Đủ để dựng lại trang Soạn bài. Chữ giữ đúng như trong session (xem «Cách giao diện dùng»
    trong ``docs/team/reports/T-016-tho-may.md``)."""

    schema_version: int = SCHEMA_VERSION
    id: str = Field(default_factory=new_draft_id)
    saved_at: AwareDatetime | None = None  # do ``DraftStore.save`` đặt, kèm múi giờ
    step: int = Field(default=0, ge=0, lt=STEP_COUNT)
    keyword: str = ""
    material: dict[str, str] = Field(default_factory=dict, max_length=20)
    research: Research | None = None
    research_keyword: str = ""
    outline_title: str = ""  # như ô sửa: chưa escape (current_outline escape lại)
    outline: list[OutlineItem] = Field(default_factory=list)  # heading chưa escape, như ô sửa
    article_title: str = ""
    parts: list[DraftPart] = Field(default_factory=list)
    review: Review | None = None
    auto_fixed: int = Field(default=0, ge=0)
    ignored_flags: list[str] = Field(default_factory=list)
    _dropped_images: int = PrivateAttr(default=0)

    @model_validator(mode="before")
    @classmethod
    def _no_images_before_v2(cls, data: object, info: ValidationInfo) -> object:
        """Khuôn cũ chưa có ảnh đã chọn: dữ liệu ảnh nằm trong nháp khuôn cũ là sửa tay, bỏ đi
        (đọc từ file thì đếm vào ``dropped_images``; ``null`` là "chưa chọn ảnh", không mất ảnh
        nào nên không đếm, SL-T055-3). Phần chữ giữ nguyên."""
        if not isinstance(data, dict):
            return data
        parts = data.get("parts")
        if data.get("schema_version", SCHEMA_VERSION) == SCHEMA_VERSION or not isinstance(
            parts, list
        ):
            return data
        dropped = (info.context or {}).get(_DROPPED_IMAGES)
        kept = []
        for part in parts:
            if isinstance(part, dict) and "chosen_image" in part:
                if part["chosen_image"] is not None and isinstance(dropped, list):
                    dropped.append("chosen_image")
                part = {key: value for key, value in part.items() if key != "chosen_image"}
            kept.append(part)
        return {**data, "parts": kept}

    @field_validator("schema_version")
    @classmethod
    def _known_version(cls, value: int) -> int:
        if value != SCHEMA_VERSION and value not in _OLD_SCHEMA_VERSIONS:
            raise ValueError(f"phiên bản khuôn {value} không được hỗ trợ")
        return SCHEMA_VERSION  # nháp khuôn cũ được nâng lên khuôn hiện tại khi mở

    @property
    def dropped_images(self) -> int:
        """Số ảnh đã chọn bị bỏ khi mở nháp vì dữ liệu ảnh hỏng (phần chữ của bài vẫn giữ)."""
        return self._dropped_images

    @field_validator("id")
    @classmethod
    def _valid_id(cls, value: str) -> str:
        if not _ID_PATTERN.fullmatch(value):
            raise ValueError("mã nháp phải là 32 ký tự hex")
        return value

    @field_validator("ignored_flags", mode="before")
    @classmethod
    def _flags_from_set(cls, value: object) -> object:
        # session giữ ``ignored_flags`` dạng set; lưu thành danh sách có thứ tự cố định.
        if isinstance(value, set | frozenset):
            return sorted(value)
        return value

    @property
    def title(self) -> str:
        """Tên hiển thị trong danh sách: tiêu đề bài, rồi tiêu đề dàn ý, rồi từ khóa."""
        for candidate in (self.article_title, self.outline_title, self.keyword):
            if candidate.strip():
                return candidate.strip()
        return "Bài chưa đặt tên"


class DraftSummary(_Strict):
    """Một dòng trong danh sách nháp."""

    id: str
    title: str
    keyword: str
    saved_at: AwareDatetime


@dataclass(frozen=True)
class DraftList:
    drafts: list[DraftSummary]
    skipped: int = 0  # số dòng hỏng đã bỏ qua


class SendState(_Strict):
    """Trạng thái «Gửi nháp» của một nháp (T-086). Ghi trước khi gửi và ngay khi có kết quả.

    - ``pending``: đang gửi, hoặc lần gửi gần nhất không rõ kết quả (bị ngắt giữa chừng, lỗi đúng
      lúc tạo nháp): bài nháp, ảnh có thể đã có trên website.
    - ``post_id``: mã bài nháp gần nhất app đã tạo trên website cho nháp này.

    Đọc từ file là dữ liệu chưa tin cậy: khuôn chặt (đúng kiểu, không đổi ``"1"``/``true`` thành
    số), giờ phải có múi giờ, không có trường chữ nào để hiện ra giao diện.
    """

    pending: bool = Field(default=False, strict=True)
    post_id: int | None = Field(default=None, ge=1, lt=2**63, strict=True)
    updated_at: AwareDatetime

    @classmethod
    def now(
        cls, *, pending: bool, post_id: int | None, timezone: str = DEFAULT_TIMEZONE
    ) -> SendState:
        return cls(pending=pending, post_id=post_id, updated_at=datetime.now(ZoneInfo(timezone)))


@dataclass
class DraftStore:
    """Kho nháp trong một file SQLite. Mỗi thao tác mở và đóng kết nối riêng (an toàn khi
    Streamlit chạy nhiều luồng)."""

    # Tra lúc tạo kho (không lúc import), để test trỏ được ``DEFAULT_DRAFTS_FILE`` sang thư mục
    # tạm và ``DraftStore()`` không bao giờ đụng ``data/`` thật trong test (Soi Lỗi R8-4).
    path: Path = field(default_factory=lambda: DEFAULT_DRAFTS_FILE)
    timezone: str = DEFAULT_TIMEZONE
    max_drafts: int = MAX_DRAFTS
    max_bytes: int = MAX_DRAFT_BYTES
    recovered_from: Path | None = field(default=None, init=False)
    """Nếu file cũ hỏng và đã được đổi tên sang một bên: đường dẫn bản hỏng (để báo người dùng)."""
    _ready: bool = field(default=False, init=False, repr=False)

    # ------------------------------------------------------------ thao tác

    def save(self, snapshot: DraftSnapshot) -> DraftSnapshot:
        """Tạo mới hoặc ghi đè nháp cùng mã. Trả về bản đã đặt ``saved_at``."""
        saved = snapshot.model_copy(update={"saved_at": datetime.now(ZoneInfo(self.timezone))})
        # Kiểm khuôn lại toàn bộ: model_copy không kiểm, và giao diện có thể đã sửa trường.
        try:
            saved = DraftSnapshot.model_validate(saved.model_dump())
        except ValidationError as exc:
            raise DraftError(f"Không lưu được nháp: dữ liệu sai khuôn ({_short(exc)}).") from None
        try:
            data = saved.model_dump_json()
            size = len(data.encode("utf-8"))
        except (PydanticSerializationError, UnicodeError):
            # Ví dụ ký tự surrogate lẻ: không ghi được ra UTF-8 (Soi Lỗi R8-5).
            raise DraftError(
                "Không lưu được nháp: trong bài có ký tự lạ không lưu được. "
                "Thử xóa ký tự vừa dán vào."
            ) from None
        if size > self.max_bytes:
            limit_mb = self.max_bytes // (1024 * 1024)
            raise DraftError(
                f"Không lưu được nháp: bài quá lớn (giới hạn {limit_mb} MB). "
                "Thử xóa bớt các phiên bản cũ."
            )
        assert saved.saved_at is not None
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO drafts (id, title, keyword, saved_at, saved_ts, data) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    saved.id,
                    saved.title,
                    saved.keyword,
                    saved.saved_at.isoformat(),
                    saved.saved_at.timestamp(),
                    data,
                ),
            )
            # Giữ nháp vừa lưu cộng (max - 1) nháp mới nhất khác. Không dựa vào giờ máy để giữ
            # nháp vừa lưu: đồng hồ bị chỉnh lùi thì nó lại là nháp "cũ nhất" (Soi Lỗi R8-6).
            # Trạng thái gửi của đúng các nháp bị bỏ đi cũng bỏ theo (T-086).
            conn.execute(
                "DELETE FROM send_states WHERE id IN "
                "(SELECT id FROM drafts WHERE id != ? AND id NOT IN "
                "(SELECT id FROM drafts WHERE id != ? "
                "ORDER BY saved_ts DESC, rowid DESC LIMIT ?))",
                (saved.id, saved.id, max(0, self.max_drafts - 1)),
            )
            conn.execute(
                "DELETE FROM drafts WHERE id != ? AND id NOT IN "
                "(SELECT id FROM drafts WHERE id != ? "
                "ORDER BY saved_ts DESC, rowid DESC LIMIT ?)",
                (saved.id, saved.id, max(0, self.max_drafts - 1)),
            )
        return saved

    def load(self, draft_id: str) -> DraftSnapshot:
        """Đọc một nháp. Nháp không có, quá lớn hoặc sai khuôn: ``DraftError`` dễ hiểu.

        Riêng ảnh đã chọn sai khuôn thì chỉ bỏ ảnh đó (``dropped_images`` đếm), vẫn mở được bài.
        Ảnh trong nháp chưa được kiểm trên ổ đĩa: gọi ``check_draft_images`` trước khi dùng.
        """
        _check_id(draft_id)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT length(CAST(data AS BLOB)) FROM drafts WHERE id = ?", (draft_id,)
            ).fetchone()
            if row is None:
                raise DraftError("Không tìm thấy nháp này (có thể đã bị xóa).")
            if row[0] is None or row[0] > self.max_bytes:
                raise DraftError("Nháp này quá lớn hoặc bị hỏng nên không mở được.")
            (data,) = conn.execute("SELECT data FROM drafts WHERE id = ?", (draft_id,)).fetchone()
        dropped: list[str] = []
        try:
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            if not isinstance(data, str):
                raise TypeError("dữ liệu không phải chữ")
            snapshot = DraftSnapshot.model_validate_json(data, context={_DROPPED_IMAGES: dropped})
        except (ValidationError, UnicodeDecodeError, TypeError) as exc:
            raise DraftError(f"Nháp này bị hỏng nên không mở được ({_short(exc)}).") from None
        if snapshot.id != draft_id:
            raise DraftError("Nháp này bị hỏng nên không mở được (mã nháp không khớp).")
        loaded = clean_loaded(snapshot)
        loaded._dropped_images = len(dropped)
        return loaded

    def list_drafts(self, limit: int = MAX_DRAFTS) -> DraftList:
        """Các nháp mới nhất trước. Dòng hỏng bị bỏ qua và đếm vào ``skipped``."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, title, keyword, saved_at FROM drafts "
                "ORDER BY saved_ts DESC, rowid DESC LIMIT ?",
                (max(0, int(limit)),),
            ).fetchall()
        drafts: list[DraftSummary] = []
        skipped = 0
        for draft_id, title, kw, saved_at in rows:
            try:
                summary = DraftSummary(id=draft_id, title=title, keyword=kw, saved_at=saved_at)
                _check_id(summary.id)
            except (ValidationError, DraftError):
                skipped += 1
                continue
            drafts.append(summary)
        return DraftList(drafts=drafts, skipped=skipped)

    def delete(self, draft_id: str) -> bool:
        """Xóa một nháp (kèm trạng thái gửi của nó). Trả về ``False`` nếu không có nháp đó."""
        _check_id(draft_id)
        with self._connect() as conn:
            conn.execute("DELETE FROM send_states WHERE id = ?", (draft_id,))
            cursor = conn.execute("DELETE FROM drafts WHERE id = ?", (draft_id,))
            return cursor.rowcount > 0

    def load_send_state(self, draft_id: str) -> SendState | None:
        """Trạng thái gửi của nháp (T-086); ``None``: chưa gửi lần nào, kể cả nháp cũ.

        Dòng quá lớn, sai khuôn (sửa tay, hỏng): ``DraftError``. Giao diện coi như chưa rõ kết quả
        lần gửi trước (khóa nút gửi, nhắc kiểm trang quản trị), không đoán.
        """
        _check_id(draft_id)
        with self._connect() as conn:
            return _read_send_state(conn, draft_id)

    def save_send_state(
        self,
        draft_id: str,
        state: SendState | None,
        *,
        expected: tuple[SendState | None, bool] | None = None,
    ) -> bool:
        """Ghi trạng thái gửi của nháp; ``None`` thì xóa (T-086). Không đụng nội dung, giờ lưu của
        nháp; lần tự lưu nháp (``save``) cũng không đụng trạng thái này. Trả ``True`` khi đã ghi.

        ``expected`` (so rồi đặt, T-089, SL-T086-1): ``(trạng thái, hỏng)`` người dùng thấy lúc bấm
        gửi, như ``load_send_state`` trả (``hỏng``: dòng không đọc được). Đọc và ghi trong **một**
        giao dịch giữ khóa ghi từ đầu (``BEGIN IMMEDIATE``): trạng thái trong nháp đã khác (tab khác
        vừa ghi «đang gửi», «đã gửi») thì không ghi gì, trả ``False``. Mọi tab trên một máy đi qua
        cùng file nên hai tab không cùng qua được bước này."""
        _check_id(draft_id)
        data = None if state is None else state.model_dump_json()
        with self._connect() as conn:
            if expected is not None:
                conn.execute("BEGIN IMMEDIATE")  # lần ghi khác phải đợi tới khi giao dịch này xong
                try:
                    current, broken = _read_send_state(conn, draft_id), False
                except DraftError:
                    current, broken = None, True
                seen, seen_broken = expected
                if broken != seen_broken or (not broken and current != seen):
                    return False
            if data is None:
                conn.execute("DELETE FROM send_states WHERE id = ?", (draft_id,))
            else:
                conn.execute(
                    "INSERT OR REPLACE INTO send_states (id, data) VALUES (?, ?)",
                    (draft_id, data),
                )
        return True

    # ------------------------------------------------------------ nội bộ

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        if self._ready and not self.path.exists():
            # File hoặc cả thư mục data/ bị xóa khi app đang chạy: tạo lại (Soi Lỗi R8-1).
            self._ready = False
        self._prepare()
        try:
            # ``with conn``: một giao dịch, xong thì commit, lỗi thì rollback
            with closing(sqlite3.connect(self.path, timeout=_SQLITE_TIMEOUT)) as conn, conn:
                yield conn
        except sqlite3.DatabaseError as exc:
            raise DraftError(_db_message(exc)) from None
        except OSError as exc:
            raise DraftError(f"Không đọc/ghi được file nháp ({exc.strerror or exc}).") from None

    def _prepare(self) -> None:
        """Lần đầu: tạo thư mục, kiểm file, tạo bảng. File hỏng thì đổi tên sang một bên."""
        if self._ready:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if self.path.exists() and not _is_healthy(self.path):
                self.recovered_from = self._move_aside()
            with closing(sqlite3.connect(self.path, timeout=_SQLITE_TIMEOUT)) as conn, conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS drafts ("
                    "id TEXT PRIMARY KEY, title TEXT NOT NULL, keyword TEXT NOT NULL, "
                    "saved_at TEXT NOT NULL, saved_ts REAL NOT NULL, data TEXT NOT NULL)"
                )
                # File nháp tạo trước T-086 chưa có bảng này: tạo thêm, nháp cũ giữ nguyên.
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS send_states ("
                    "id TEXT PRIMARY KEY, data TEXT NOT NULL)"
                )
        except sqlite3.DatabaseError as exc:
            raise DraftError(_db_message(exc)) from None
        except OSError as exc:
            raise DraftError(f"Không tạo được file nháp ({exc.strerror or exc}).") from None
        self._ready = True

    def _move_aside(self) -> Path:
        stamp = datetime.now(ZoneInfo(self.timezone)).strftime("%Y%m%d-%H%M%S")
        target = self.path.with_name(f"{self.path.stem}.hong-{stamp}{self.path.suffix}")
        n = 1
        while target.exists():
            n += 1
            target = self.path.with_name(f"{self.path.stem}.hong-{stamp}-{n}{self.path.suffix}")
        self.path.replace(target)
        return target


def _read_send_state(conn: sqlite3.Connection, draft_id: str) -> SendState | None:
    """Trạng thái gửi của nháp, đọc trên kết nối đang mở (``load_send_state``, và lần so rồi đặt
    của ``save_send_state``). Dòng quá lớn, sai khuôn: ``DraftError`` câu cố định."""
    row = conn.execute(
        "SELECT length(CAST(data AS BLOB)) FROM send_states WHERE id = ?", (draft_id,)
    ).fetchone()
    if row is None:
        return None
    if row[0] is None or row[0] > MAX_SEND_STATE_BYTES:
        raise DraftError(_MSG_SEND_STATE_BROKEN)
    (data,) = conn.execute("SELECT data FROM send_states WHERE id = ?", (draft_id,)).fetchone()
    try:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        if not isinstance(data, str):
            raise TypeError("dữ liệu không phải chữ")
        return SendState.model_validate_json(data)
    except (ValidationError, UnicodeDecodeError, TypeError):
        raise DraftError(_MSG_SEND_STATE_BROKEN) from None


def clean_loaded(snapshot: DraftSnapshot) -> DraftSnapshot:
    """Lọc lại mọi chữ do AI tạo trong nháp đọc từ file, bằng đúng các hàm ``clean_*`` mà luồng
    AI dùng lúc nhận kết quả (Lá Chắn T-016-020 #1, Soi Lỗi R8-2).

    File nháp là dữ liệu chưa tin cậy; kiểm khuôn không chặn được link Markdown hay thẻ HTML.
    Các hàm lọc chạy lại không đổi gì trên chữ đã sạch, nên bản đúng giữ nguyên sau nhiều lần
    lưu/mở. Chất liệu thật là chữ người dùng gõ (không phải chữ AI) nên giữ nguyên; từ khóa chỉ
    được gộp về một dòng.

    Dạng lưu của từng trường (xem ``app/views/write.py``):
    - dàn ý ở dạng ô sửa (chưa escape): lọc như AI rồi bỏ escape, giống ``set_outline``;
    - thân bài ở dạng đã escape, có thể có chữ người dùng sửa tay: bỏ thẻ rồi escape, giống
      ``apply_flag``;
    - ảnh đã chọn: dựng lại ``DraftImage`` (chạy lại mọi kiểm tra và bộ lọc của nó); nháp ghi ảnh
      AI thì alt, chú thích có tiền tố ảnh AI (``_ai_wording``). Ảnh mà chỉ thẻ trên máy nói là
      ảnh AI thì ``check_draft_images`` mới biết, và cũng thêm tiền tố ở đó.
    """

    def outline_line(text: str) -> str:
        return unescape_link_syntax(clean_ai_line(text))

    def chosen(image: DraftImage) -> DraftImage:
        image = DraftImage.model_validate(image.model_dump())
        return _ai_wording(image) if image.source == SOURCE_AI else image

    return snapshot.model_copy(
        update={
            "research": None if snapshot.research is None else clean_research(snapshot.research),
            "review": None if snapshot.review is None else clean_review(snapshot.review),
            # Hiện trong st.warning (Markdown) ở bước Chuẩn bị: lọc như chữ một dòng (Lá Chắn #4).
            "research_keyword": clean_ai_line(snapshot.research_keyword),
            # Ô từ khóa chỉ nhận một dòng; dòng trống làm phụ đề «Từ khóa: …» (khối HTML trong
            # ui.py) thoát ra thành Markdown có link sống (Soi Lỗi R9-1). Gộp mọi khoảng trắng.
            "keyword": " ".join(snapshot.keyword.split()),
            "outline_title": outline_line(snapshot.outline_title),
            "outline": [
                OutlineItem(
                    heading=outline_line(item.heading),
                    points=[clean_ai_text(point) for point in item.points],
                    image=clean_ai_text(item.image),
                )
                for item in snapshot.outline
            ],
            "article_title": clean_ai_line(snapshot.article_title),
            "parts": [
                DraftPart(
                    heading=clean_ai_line(part.heading),
                    versions=[escape_link_syntax(strip_tags(text)) for text in part.versions],
                    current=part.current,
                    image=clean_ai_text(part.image),
                    chosen_image=None if part.chosen_image is None else chosen(part.chosen_image),
                )
                for part in snapshot.parts
            ],
        }
    )


# ---------------------------------------------------------------------- ảnh đã chọn


@dataclass(frozen=True)
class CheckedImage:
    """Ảnh đã chọn trong nháp sau khi kiểm lại trên máy này (``check_draft_images``).

    - ``image``: ảnh đã chọn dựng lại từ nháp. Ảnh AI (theo ``tags``) thì alt, chú thích luôn có
      tiền tố ảnh AI; alt phải thêm tiền tố thì không còn "đã duyệt" (SL-T055-2). Giao diện dùng
      ``image`` này (không dùng ảnh trong nháp vừa mở) để hiện, duyệt và lưu lại.
    - ``ref``: ảnh trong thư mục ảnh: ``ImageRef`` theo tên trên ổ (là ``entry.ref``); ảnh không
      dùng được thì ``ImageRef`` dựng lại từ nháp (hay tên trên ổ, nếu ``stat_image`` đã trả);
      ảnh tạo bằng AI: ``None``.
    - ``entry``: kết quả ``ImageLibrary.stat_image`` khi ảnh còn dùng được; ``None`` nếu không.
    - ``tags``: thẻ dùng cho ảnh, nguồn ảnh theo hướng an toàn (xem ``check_draft_images``).
    - ``message``: vì sao ảnh không dùng được (câu tiếng Việt của T-048, không chứa đường dẫn).
    - ``tag_error``: không đọc được thẻ sửa tay (đang dùng thẻ đọc từ tên thư mục).
    """

    image: DraftImage
    ref: ImageRef | None
    entry: ImageEntry | None
    tags: ImageTags
    message: str = ""
    tag_error: str = ""

    @property
    def is_generated(self) -> bool:
        """Ảnh tạo bằng AI: không có file trong thư mục ảnh, chỉ có prompt."""
        return self.ref is None

    @property
    def available(self) -> bool:
        """Ảnh trong thư mục ảnh còn dùng được trên máy này (ảnh tạo bằng AI: ``False``)."""
        return self.entry is not None

    @property
    def is_ai(self) -> bool:
        return self.tags.is_ai


def _name_key(name: str) -> str:
    """Khóa so một tên: không phân biệt hoa thường, cùng dạng Unicode (như ``ImageLibrary`` so tên
    đã gõ với tên trên ổ)."""
    return unicodedata.normalize("NFC", name).casefold()


class _FolderNames:
    """Đối chiếu tên các thư mục trên đường tới một ảnh với danh sách thư mục (SL-T055-1).

    Thẻ đọc từ tên thư mục phân biệt hoa thường ("CongAI" là thư mục ảnh AI nhờ tách chữ hoa,
    "congai" thì không), còn ổ Windows, Mac thì không: nháp ghi ``…/congai/…`` (sửa tay, hay thư mục
    được đổi hoa thường sau khi chọn ảnh) vẫn trỏ tới thư mục ``CongAI``. Từ T-076,
    ``ImageLibrary.stat_image`` đã trả ``ImageRef`` theo tên trên ổ, lấy từ chính thư mục cha (không
    từ ``resolve``, LC-T076-1); đây là lớp phòng thứ hai: danh sách cho tên khác nghĩa là thư mục
    vừa đổi tên giữa hai lần xem (xem ``_check_images``). Xem tên bằng ``library.list_folder`` từng
    tầng, từ thư mục gốc xuống: không đệ quy, chỉ đọc tên và ``stat``, không mở file ảnh (Drive "chỉ
    trực tuyến" không bị tải về); mỗi thư mục xem một lần cho cả nháp. Tên file không cần: tên file
    chỉ dùng để nhận ảnh AI và không tách chữ hoa (``tags_for_image``).
    """

    def __init__(self, library: ImageLibrary) -> None:
        self._library = library
        self._listings: dict[tuple[int, str], tuple[tuple[SubFolder, ...], bool] | str] = {}

    def real_ref(self, ref: ImageRef) -> ImageRef:
        """``ref`` (tên do ``stat_image`` trả) với tên thư mục theo danh sách thư mục. Danh sách nói
        ngược lại (thư mục vừa đổi tên, bị xóa, bị tráo): ``ImageFolderError``."""
        real_dir = ""
        for name in ref.parts[:-1]:
            real_dir = self._child(ref.root_index, real_dir, name)
        return ImageRef(ref.root_index, f"{real_dir}/{ref.name}") if real_dir else ref

    def _child(self, root_index: int, rel_dir: str, name: str) -> str:
        """Đường dẫn thật của thư mục con ``name`` trong ``rel_dir`` (đã là tên thật)."""
        key = (root_index, rel_dir)
        if key not in self._listings:
            try:
                listing = self._library.list_folder(root_index, rel_dir, page_size=1)
            except ImageFolderError as exc:
                self._listings[key] = str(exc)
            else:
                self._listings[key] = (listing.subfolders, listing.truncated)
        listed = self._listings[key]
        if isinstance(listed, str):
            raise ImageFolderError(listed)
        subfolders, truncated = listed
        # Trùng hẳn trước (ổ phân biệt hoa thường có thể có cả "CongAI" lẫn "congai": "congai" là
        # một thư mục khác).
        for sub in subfolders:
            if sub.name == name:
                return sub.rel_path
        if truncated:
            # Danh sách bị cắt (thư mục quá nhiều mục, quét quá giờ): không nhận tên chỉ trùng không
            # phân biệt hoa thường, có thể là thư mục khác (LC-T055-2); giữ tên ``stat_image`` đã
            # trả, là tên trên ổ, không báo "chưa kiểm được" chỉ vì thư mục cha lớn (LC-T055-3).
            return f"{rel_dir}/{name}" if rel_dir else name
        # Xem hết mà không có tên trùng hẳn: phải có đúng một tên trùng không phân biệt hoa thường.
        same = [sub for sub in subfolders if _name_key(sub.name) == _name_key(name)]
        if len(same) != 1:  # thư mục vừa đổi tên, bị xóa, bị tráo
            raise ImageFolderError(_MSG_FOLDER_NAME)
        return same[0].rel_path


def _safe_tags(image: DraftImage, current: ImageTags, *, ai_root: bool) -> ImageTags:
    """Thẻ dùng cho ảnh trong thư mục ảnh (điều kiện Lá Chắn T-052 số 3).

    Thẻ hiện tại (``resolve`` hay tên thư mục) là gốc; nháp chỉ được kéo về phía ảnh AI: nháp ghi
    AI, thẻ hiện tại nói AI hoặc cả thư mục gốc là thư mục ảnh AI thì là ảnh AI, không mang mã công
    trình, khu vực, trước/sau. Nháp không bao giờ làm ảnh AI thành ảnh thật, cũng không thêm thẻ nào
    cho ảnh thật.
    """
    try:
        current = ImageTags(
            source=current.source,
            project_code=current.project_code,
            category=current.category,
            area=current.area,
            phase=current.phase,
        )
    except TagError:
        return _ai_tags(image.category)
    if image.source == SOURCE_AI or current.is_ai or ai_root:
        return _ai_tags(current.category or image.category)
    return current


def check_draft_images(
    snapshot: DraftSnapshot,
    library: ImageLibrary,
    *,
    tag_store: ImageTagStore | None = None,
    scanned: Iterable[ImageRef | ImageEntry] = (),
    ai_roots: Collection[int] = (),
) -> dict[int, CheckedImage]:
    """Kiểm lại các ảnh đã chọn trong nháp trên máy này. Trả ``{số thứ tự phần: CheckedImage}``
    cho các phần có ảnh đã chọn.

    Nháp là dữ liệu chưa tin cậy (góp ý Lá Chắn T-046 số 11, điều kiện Lá Chắn T-048, T-052):

    - Mỗi ảnh được dựng lại (``DraftImage`` rồi ``ImageRef(...)``), rồi hỏi
      ``library.stat_image``: số thứ tự gốc không còn khai báo, file mất, đi qua liên kết, quá lớn…
      thì ``entry`` là ``None`` kèm ``message``. Không mở file ảnh (Drive "chỉ trực tuyến" không bị
      tải về). Đọc ảnh sau này cũng phải qua ``library.read_image_bytes(ref)``.
    - ``ref`` là ``ImageRef`` theo tên trên ổ do ``stat_image`` trả (T-076, LC-T055-1; tên lấy từ
      thư mục cha, kể cả trên ổ Google Drive for Desktop, LC-T076-1), không theo chữ hoa thường
      trong nháp, nên thẻ đọc từ tên thư mục thật (SL-T055-1).
    - Ảnh nháp ghi là ảnh thật còn được đối chiếu tên thư mục với danh sách thư mục (lớp phòng thứ
      hai, ``list_folder`` không đệ quy, mỗi thư mục một lần cho cả nháp). Danh sách xem hết mà cho
      tên khác tên ``stat_image`` vừa trả thì thư mục vừa đổi tên: ảnh không dùng được, kèm
      ``message``, kể cả khi ảnh ở tên mới cùng cỡ, cùng giờ sửa (bản sao; LC-T055-2, LC-T076-2).
      Các lần hỏi lại so cả định danh file (``ImageEntry.file_id``, LC-T076-3).
      Danh sách bị cắt (thư mục cha hơn 5.000 mục, quét quá giờ) mà chưa thấy tên trùng hẳn thì
      giữ tên ``stat_image`` trả (LC-T055-3).
    - ``scanned`` (**điều kiện**): ``ImageEntry``/``ImageRef`` lấy từ ``ImageLibrary.list_folder``,
      tức theo tên trên ổ. Chỉ dùng để bỏ bước đối chiếu ở trên, cho ảnh mà ``ImageRef`` do
      ``stat_image`` trả **trùng hẳn** (cùng gốc, cùng từng chữ) một ``ImageRef`` trong
      ``scanned``. ``scanned`` không bao giờ đổi ảnh được kiểm hay thẻ của ảnh. ``ImageRef`` dựng
      từ chữ trong nháp, chữ gõ tay hay kết quả quét cũ (trước khi đổi tên thư mục) không làm sai
      kết quả: khác tên trên ổ thì không trùng, ảnh vẫn được đối chiếu như khi không có
      ``scanned``.
    - Thẻ: ``tag_store.resolve_many`` (thẻ sửa tay hoặc tên thư mục), không có ``tag_store`` thì
      thẻ đọc từ tên thư mục. Nguồn ảnh theo hướng an toàn (``_safe_tags``); ``ai_roots``: số thứ
      tự các thư mục gốc mà mọi ảnh trong đó là ảnh AI (giao diện quyết, ví dụ theo tên gốc).
    - Ảnh AI: alt, chú thích trong ``CheckedImage.image`` luôn có tiền tố ảnh AI (SL-T055-2).
    - Ảnh tạo bằng AI: ``ref`` và ``entry`` là ``None``, thẻ ảnh AI với hạng mục ghi trong nháp.
    """
    if not isinstance(snapshot, DraftSnapshot):
        raise TypeError("check_draft_images cần DraftSnapshot.")
    chosen = {
        index: part.chosen_image
        for index, part in enumerate(snapshot.parts)
        if part.chosen_image is not None
    }
    checked = _check_images(
        list(chosen.values()), library, tag_store=tag_store, scanned=scanned, ai_roots=ai_roots
    )
    return dict(zip(chosen, checked, strict=True))


def check_chosen_image(
    image: DraftImage,
    library: ImageLibrary,
    *,
    tag_store: ImageTagStore | None = None,
    scanned: Iterable[ImageRef | ImageEntry] = (),
    ai_roots: Collection[int] = (),
) -> CheckedImage:
    """Như ``check_draft_images`` cho một ảnh."""
    (checked,) = _check_images(
        [image], library, tag_store=tag_store, scanned=scanned, ai_roots=ai_roots
    )
    return checked


def _check_images(
    images: list[DraftImage],
    library: ImageLibrary,
    *,
    tag_store: ImageTagStore | None,
    scanned: Iterable[ImageRef | ImageEntry],
    ai_roots: Collection[int],
) -> list[CheckedImage]:
    if not isinstance(library, ImageLibrary):
        raise TypeError("Cần ImageLibrary để kiểm ảnh trong nháp.")
    scanned_refs: set[ImageRef] = set()  # chỉ so trùng hẳn (xem docstring ``check_draft_images``)
    for item in scanned:
        found = item.ref if isinstance(item, ImageEntry) else item
        if isinstance(found, ImageRef):
            scanned_refs.add(found)
    ai_root_set = frozenset(index for index in ai_roots if type(index) is int)

    rebuilt: list[DraftImage] = []
    for image in images:
        if not isinstance(image, DraftImage):
            raise TypeError("Ảnh đã chọn phải là DraftImage.")
        # Dựng lại để chạy lại mọi kiểm tra (đối tượng có thể đã bị sửa sau khi tạo).
        rebuilt.append(DraftImage.model_validate(image.model_dump()))

    folder_names = _FolderNames(library)
    located: list[tuple[DraftImage, ImageRef | None, ImageEntry | None, str]] = []
    for image in rebuilt:
        ref = image.ref
        if ref is None:
            located.append((image, None, None, ""))
            continue
        try:
            # ``entry.ref`` theo tên trên ổ (T-076): từ đây không dùng chữ hoa thường trong nháp.
            entry = library.stat_image(ref)
            ref, message = entry.ref, ""
            # Lớp phòng thứ hai (SL-T055-1). Chỉ cần khi ảnh có thể ra ảnh thật (nháp ghi AI hay gốc
            # AI thì đã là ảnh AI) và chưa có trong kết quả quét.
            if (
                image.source == SOURCE_REAL
                and ref.root_index not in ai_root_set
                and ref not in scanned_refs
            ):
                real = folder_names.real_ref(ref)
                if real != ref:
                    # Danh sách thư mục cho tên khác tên ``stat_image`` vừa trả. ``ImageLibrary``
                    # lấy tên từ chính thư mục cha (LC-T076-1) nên đây là thư mục vừa đổi tên giữa
                    # hai lần xem: hỏi lại tên cũ thì ổ trả tên khác, ảnh không dùng được, không
                    # nhận ảnh ở tên mới dù cùng cỡ, cùng giờ sửa (bản sao, LC-T076-2 = SL-T076-1).
                    # Chỉ dùng tên của danh sách khi hỏi lại tên cũ vẫn ra đúng kết quả cũ (thư
                    # viện không cho biết tên trên ổ) và ảnh ở tên mới là **cùng một file**: cùng
                    # cỡ, cùng giờ sửa, cùng định danh trên ổ (``file_id``) với lần hỏi đầu; dùng
                    # số liệu mới (LC-T055-2). So định danh giữa các lần hỏi: thư mục đổi tên đi
                    # rồi đổi lại, hay danh sách nhớ từ ảnh trước của nháp, không làm bản sao ở
                    # tên khác thành ảnh đã chọn (LC-T076-3 = SL-T076-2). Ổ không cho biết định
                    # danh (``file_id`` là ``None`` cả hai lần) thì chỉ so được cỡ, giờ sửa.
                    first = library.stat_image(ref)
                    if first != entry or first.file_id != entry.file_id:
                        raise ImageFolderError(_MSG_FOLDER_NAME)
                    again = library.stat_image(real)
                    same = (again.size, again.modified, again.file_id) == (
                        entry.size,
                        entry.modified,
                        entry.file_id,
                    )
                    if again.ref != real or not same:
                        raise ImageFolderError(_MSG_FOLDER_NAME)
                    ref, entry = again.ref, again
        except ImageFolderError as exc:
            entry, message = None, str(exc)
        located.append((image, ref, entry, message))

    refs = [ref for _image, ref, _entry, _message in located if ref is not None]
    current: dict[ImageRef, tuple[ImageTags, str]] = {}
    if tag_store is not None and refs:
        for ref, resolved in tag_store.resolve_many(refs).items():
            current[ref] = (resolved.tags, resolved.error)
    for ref in refs:
        if ref not in current:
            current[ref] = (tags_for_image(ref).tags, "")

    results: list[CheckedImage] = []
    for image, ref, entry, message in located:
        if ref is None:
            results.append(
                CheckedImage(
                    image=_ai_wording(image), ref=None, entry=None, tags=_ai_tags(image.category)
                )
            )
            continue
        tags, tag_error = current[ref]
        tags = _safe_tags(image, tags, ai_root=ref.root_index in ai_root_set)
        results.append(
            CheckedImage(
                image=_ai_wording(image) if tags.is_ai else image,
                ref=ref,
                entry=entry,
                tags=tags,
                message=message,
                tag_error=tag_error,
            )
        )
    return results


def _is_healthy(path: Path) -> bool:
    """File là SQLite đọc được, và bảng ``drafts``, ``send_states`` (nếu có) có đủ cột cần dùng."""
    try:
        with closing(sqlite3.connect(path, timeout=_SQLITE_TIMEOUT)) as conn:
            if conn.execute("PRAGMA quick_check").fetchone() != ("ok",):
                return False
            columns = {row[1] for row in conn.execute("PRAGMA table_info(drafts)")}
            send_columns = {row[1] for row in conn.execute("PRAGMA table_info(send_states)")}
    except sqlite3.DatabaseError:
        return False
    needed = {"id", "title", "keyword", "saved_at", "saved_ts", "data"}
    return (not columns or needed <= columns) and (
        not send_columns or {"id", "data"} <= send_columns
    )


def _db_message(exc: sqlite3.DatabaseError) -> str:
    if isinstance(exc, sqlite3.OperationalError) and "locked" in str(exc).lower():
        return "File nháp đang bận (có thể app mở ở tab khác đang lưu). Thử lại sau giây lát."
    return "File nháp bị lỗi nên không đọc/ghi được. Thử tải lại trang."


def _short(exc: Exception) -> str:
    """Tóm tắt lỗi kiểm khuôn: chỉ nêu tên trường cấp một **do code định nghĩa**.

    Không chép gì từ file ra (kể cả tên trường hay khóa của ``material``, vốn là chữ trong
    file và được hiện bằng ``st.error``, tức Markdown — Soi Lỗi R8-3).
    """
    if isinstance(exc, ValidationError):
        names: list[str] = []
        for error in exc.errors(include_input=False, include_url=False):
            loc = error["loc"]
            first = loc[0] if loc else None
            name = first if first in DraftSnapshot.model_fields else "trường lạ"
            if not loc:
                name = "toàn bộ"
            if name not in names:
                names.append(name)
        where = ", ".join(names[:3])
        more = f" và {len(names) - 3} chỗ khác" if len(names) > 3 else ""
        return f"sai ở: {where}{more}"
    if isinstance(exc, UnicodeDecodeError):
        return "chữ không đúng mã UTF-8"
    return "dữ liệu không đọc được"


__all__ = [
    "DEFAULT_DRAFTS_FILE",
    "MAX_ALT_CHARS",
    "MAX_CAPTION_CHARS",
    "MAX_DRAFTS",
    "MAX_DRAFT_BYTES",
    "MAX_PROMPT_CHARS",
    "MAX_ROOT_INDEX",
    "MAX_SEND_STATE_BYTES",
    "SCHEMA_VERSION",
    "CheckedImage",
    "DraftError",
    "DraftImage",
    "DraftList",
    "DraftPart",
    "DraftSnapshot",
    "DraftStore",
    "DraftSummary",
    "SendState",
    "check_chosen_image",
    "check_draft_images",
    "clean_loaded",
    "new_draft_id",
]

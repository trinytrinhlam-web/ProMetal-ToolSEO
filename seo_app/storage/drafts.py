"""Kho nháp cục bộ cho bài đang soạn (SQLite có sẵn của Python, không thêm thư viện).

Mỗi nháp là một ``DraftSnapshot`` lưu dạng JSON trong một dòng của bảng ``drafts``. Dữ liệu
đọc từ file được coi là chưa tin cậy: giới hạn kích thước, kiểm khuôn bằng pydantic; nháp hỏng
thì bỏ qua và báo lỗi tiếng Việt, không làm sập app. File hỏng hẳn (không phải SQLite) được
đổi tên sang một bên để giữ lại, rồi tạo file mới.

Không dùng ``pickle``; mọi câu SQL dùng tham số ``?``. Khuôn không có chỗ nào cho khóa API
hay mật khẩu, và ``extra="forbid"`` chặn mọi trường lạ.
"""

from __future__ import annotations

import re
import sqlite3
import uuid
from collections.abc import Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)
from pydantic_core import PydanticSerializationError  # đi kèm pydantic, không phải thư viện mới

from seo_app.config import DEFAULT_TIMEZONE, PROJECT_ROOT
from seo_app.content.models import OutlineItem, Research, Review
from seo_app.content.workflow import clean_ai_line, clean_research, clean_review
from seo_app.sanitize import clean_ai_text, escape_link_syntax, strip_tags, unescape_link_syntax

DEFAULT_DRAFTS_FILE = PROJECT_ROOT / "data" / "drafts.sqlite"
MAX_DRAFTS = 30
MAX_DRAFT_BYTES = 5 * 1024 * 1024  # một nháp (JSON, UTF-8) không quá 5 MB
STEP_COUNT = 5  # Chuẩn bị · Dàn ý · Viết & kiểm tra · SEO · Xuất bản
SCHEMA_VERSION = 1
_ID_PATTERN = re.compile(r"[0-9a-f]{32}")
_SQLITE_TIMEOUT = 5  # giây chờ khi file đang bị một lần lưu khác giữ


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


class DraftPart(_Strict):
    """Một phần của bài: tiêu đề, mọi phiên bản (để quay lại bản trước) và bản đang chọn."""

    heading: str
    versions: list[str] = Field(min_length=1)
    current: int = Field(default=0, ge=0)
    image: str = ""  # mô tả chỗ cần ảnh; trống nếu phần này không cần ảnh

    @field_validator("versions")
    @classmethod
    def _escape_versions(cls, versions: list[str]) -> list[str]:
        # Thân bài trong session luôn ở dạng đã escape link. Chạy lại (idempotent, bản đúng
        # không đổi) để file bị sửa tay cũng không chèn được link Markdown vào bài.
        return [escape_link_syntax(text) for text in versions]

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

    @field_validator("schema_version")
    @classmethod
    def _known_version(cls, value: int) -> int:
        if value != SCHEMA_VERSION:
            raise ValueError(f"phiên bản khuôn {value} không được hỗ trợ")
        return value

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
            conn.execute(
                "DELETE FROM drafts WHERE id != ? AND id NOT IN "
                "(SELECT id FROM drafts WHERE id != ? "
                "ORDER BY saved_ts DESC, rowid DESC LIMIT ?)",
                (saved.id, saved.id, max(0, self.max_drafts - 1)),
            )
        return saved

    def load(self, draft_id: str) -> DraftSnapshot:
        """Đọc một nháp. Nháp không có, quá lớn hoặc sai khuôn: ``DraftError`` dễ hiểu."""
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
        try:
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            if not isinstance(data, str):
                raise TypeError("dữ liệu không phải chữ")
            snapshot = DraftSnapshot.model_validate_json(data)
        except (ValidationError, UnicodeDecodeError, TypeError) as exc:
            raise DraftError(f"Nháp này bị hỏng nên không mở được ({_short(exc)}).") from None
        if snapshot.id != draft_id:
            raise DraftError("Nháp này bị hỏng nên không mở được (mã nháp không khớp).")
        return clean_loaded(snapshot)

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
        """Xóa một nháp. Trả về ``False`` nếu không có nháp đó."""
        _check_id(draft_id)
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM drafts WHERE id = ?", (draft_id,))
            return cursor.rowcount > 0

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
      ``apply_flag``.
    """

    def outline_line(text: str) -> str:
        return unescape_link_syntax(clean_ai_line(text))

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
                )
                for part in snapshot.parts
            ],
        }
    )


def _is_healthy(path: Path) -> bool:
    """File là SQLite đọc được, và nếu có bảng ``drafts`` thì bảng có đủ cột cần dùng."""
    try:
        with closing(sqlite3.connect(path, timeout=_SQLITE_TIMEOUT)) as conn:
            if conn.execute("PRAGMA quick_check").fetchone() != ("ok",):
                return False
            columns = {row[1] for row in conn.execute("PRAGMA table_info(drafts)")}
    except sqlite3.DatabaseError:
        return False
    needed = {"id", "title", "keyword", "saved_at", "saved_ts", "data"}
    return not columns or needed <= columns


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
    "MAX_DRAFTS",
    "MAX_DRAFT_BYTES",
    "DraftError",
    "DraftList",
    "DraftPart",
    "DraftSnapshot",
    "DraftStore",
    "DraftSummary",
    "clean_loaded",
    "new_draft_id",
]

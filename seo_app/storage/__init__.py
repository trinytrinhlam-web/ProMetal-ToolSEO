"""Lưu trữ cục bộ trên máy (cache, nháp). Xóa đi vẫn chạy được, chỉ mất nháp chưa gửi."""

from seo_app.storage.drafts import (
    DEFAULT_DRAFTS_FILE,
    MAX_DRAFT_BYTES,
    MAX_DRAFTS,
    DraftError,
    DraftList,
    DraftPart,
    DraftSnapshot,
    DraftStore,
    DraftSummary,
    new_draft_id,
)

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
    "new_draft_id",
]

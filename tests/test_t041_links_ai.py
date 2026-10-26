"""T-041 (Thợ Máy): AI gợi ý liên kết nội bộ (điều kiện Lá Chắn T-039 số 2a, 2b).

- ``[tasks.links]`` trong ``config/ai.toml`` không có ``web_search``; bật thì phần mềm từ chối.
- ``ContentWriter.internal_links`` chỉ gọi
  ``_run("links", internal_links_prompt(...), LinkSuggestions)`` rồi ``check_suggestions``: không
  gửi địa chỉ cho AI, không dùng trường nào khác của câu trả lời.
- Gợi ý đạt lưu vào nháp (``DraftLink``) rồi đọc lại, chèn link chỉ qua ``apply_links``.

AI là provider giả, không gọi mạng.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from seo_app.ai import AIError, AIRouter, TaskConfig, load_ai_config
from seo_app.ai import registry as ai_registry
from seo_app.config import Settings
from seo_app.content import ContentWriter, Section
from seo_app.content.blind_test import TASK_LABELS
from seo_app.content.rules import ContentRules
from seo_app.onpage.links import (
    Candidate,
    Candidates,
    InternalLink,
    LinkReview,
    LinkSuggestions,
    apply_links,
)
from seo_app.sanitize import sanitize_html
from seo_app.storage import DraftSnapshot, DraftStore
from seo_app.storage.drafts import DraftLink, DraftSeo
from seo_app.storage.site_index import SiteIndex
from seo_app.wordpress import PublishedItem

SITE = "https://suachuacuasat.com"
SERVICE = PublishedItem(
    id=10, type="page", slug="sua-cua-keo-tphcm", link=f"{SITE}/sua-cua-keo-tphcm/",
    title="Sửa cửa kéo tại TP.HCM",
)  # fmt: skip
STUCK = PublishedItem(
    id=11, type="post", slug="cua-keo-bi-ket", link=f"{SITE}/cua-keo-bi-ket/",
    title="Cửa kéo bị kẹt: nguyên nhân và cách xử lý",
)  # fmt: skip
INDEX = SiteIndex(
    site=SITE,
    fetched_at=datetime(2026, 10, 26, 9, 0, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")),
    items=(SERVICE, STUCK),
)
CANDIDATES = Candidates((Candidate(SERVICE, required=True), Candidate(STUCK)))
PARTS = [
    Section(heading="Mở bài", body="Cửa kéo bị kẹt ray là lỗi hay gặp ở nhà phố."),
    Section(heading="Khi nào gọi thợ", body="Không tự chỉnh được thì gọi dịch vụ sửa cửa kéo."),
]
RULES = ContentRules(
    business_profile="- Tên thương hiệu: Pro-Metal", address="", tone="", banned=(), checklist=()
)
GOOD = {"post_id": 10, "section": 1, "anchor": "dịch vụ sửa cửa kéo"}


class FakeLinks:
    def __init__(self, payload: dict):
        self.payload = payload
        self.calls: list[tuple[TaskConfig, str, str, type]] = []

    def generate(self, task, *, system, prompt, schema):
        self.calls.append((task, system, prompt, schema))
        return schema.model_validate(self.payload)


def make_writer(monkeypatch, payload, **task_changes):
    provider = FakeLinks(payload)
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: provider)
    tasks = {
        name: TaskConfig(name=name, provider="anthropic", model="claude-opus-5-5")
        for name in ("research", "outline", "write", "rewrite", "review", "meta")
    }
    tasks["links"] = TaskConfig(
        name="links", provider="anthropic", model="claude-opus-5-5", **task_changes
    )
    return ContentWriter(AIRouter(tasks, Settings()), RULES), provider


# ------------------------------------------------------------------ cấu hình


def test_links_task_in_config_has_no_web_search():
    tasks = load_ai_config()
    links, meta = tasks["links"], tasks["meta"]
    assert links.web_search is False
    assert (links.provider, links.model, links.effort) == (meta.provider, meta.model, "low")
    assert links.max_tokens <= 4000
    assert TASK_LABELS["links"] == "Gợi ý liên kết nội bộ"


# ------------------------------------------------------------------ gọi AI


def test_internal_links_sends_ids_and_titles_only(monkeypatch):
    writer, provider = make_writer(monkeypatch, {"links": [GOOD]})
    review = writer.internal_links("Cửa kéo bị kẹt", PARTS, CANDIDATES)
    assert review.links == (InternalLink(section=1, anchor="dịch vụ sửa cửa kéo", post_id=10),)
    assert review.missing_required == ()
    [(task, system, prompt, schema)] = provider.calls
    assert task.name == "links" and schema is LinkSuggestions
    assert "<danh_sach_bai>" in prompt and "ID 10: Sửa cửa kéo tại TP.HCM" in prompt
    for address in ("http", "suachuacuasat", "sua-cua-keo-tphcm", "cua-keo-bi-ket"):
        assert address not in prompt
    assert "<ho_so_doanh_nghiep>" in system


def test_internal_links_checks_every_suggestion(monkeypatch):
    payload = {
        "links": [
            {**GOOD, "url": "https://evil.example/", "href": "javascript:alert(1)"},
            {"post_id": 99, "section": 0, "anchor": "cửa kéo bị kẹt"},  # không phải bài đích
            {"post_id": 11, "section": 0, "anchor": "không có trong bài"},
        ]
    }
    writer, _ = make_writer(monkeypatch, payload)
    review = writer.internal_links("Bài", PARTS, CANDIDATES)
    assert review.links == (InternalLink(section=1, anchor="dịch vụ sửa cửa kéo", post_id=10),)
    assert len(review.rejected) == 2
    assert all("evil" not in m and "javascript" not in m for m in review.rejected)


def test_internal_links_refuses_web_search(monkeypatch):
    writer, provider = make_writer(monkeypatch, {"links": [GOOD]}, web_search=True)
    with pytest.raises(AIError, match=r"web_search.*\[tasks\.links\]"):
        writer.internal_links("Bài", PARTS, CANDIDATES)
    assert provider.calls == []


def test_internal_links_without_candidates_does_not_call_ai(monkeypatch):
    def no_provider(name, settings):
        raise AssertionError("không có bài đích thì không được gọi AI")

    writer, _ = make_writer(monkeypatch, {"links": []})
    monkeypatch.setattr(ai_registry, "make_provider", no_provider)
    writer.ai._providers.clear()
    assert writer.internal_links("Bài", PARTS, Candidates(())) == LinkReview((), (), ())


def test_internal_links_missing_task_is_a_clear_error(monkeypatch):
    writer, _ = make_writer(monkeypatch, {"links": [GOOD]})
    del writer.ai.tasks["links"]
    with pytest.raises(AIError):
        writer.internal_links("Bài", PARTS, CANDIDATES)


# ------------------------------------------------------------------ AI → nháp → chèn link


def test_suggestion_saved_in_draft_then_applied(monkeypatch, tmp_path):
    writer, _ = make_writer(monkeypatch, {"links": [GOOD]})
    review = writer.internal_links("Bài", PARTS, CANDIDATES)
    store = DraftStore(path=tmp_path / "data" / "drafts.sqlite")
    seo = DraftSeo(links=[DraftLink.from_link(link) for link in review.links])
    saved = store.save(DraftSnapshot(keyword="cửa kéo", seo=seo))
    used = [d.to_link() for d in store.load(saved.id).seo.links if d.use]
    html = (  # mở bài không có <h2> (phần 0), mỗi phần sau đúng một <h2>
        "<p>Cửa kéo bị kẹt ray là lỗi hay gặp ở nhà phố.</p>"
        "<h2>Khi nào gọi thợ</h2><p>Không tự chỉnh được thì gọi dịch vụ sửa cửa kéo.</p>"
    )
    out = sanitize_html(apply_links(sanitize_html(html), used, INDEX))
    assert f'<a href="{SITE}/sua-cua-keo-tphcm/">dịch vụ sửa cửa kéo</a>' in out

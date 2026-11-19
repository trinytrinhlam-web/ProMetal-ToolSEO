"""Soi Lỗi T-138 (rút gọn): tạm Gemini Flash, bước nghiên cứu không tìm web, test ghim cấu hình.

Không gọi AI thật, Google thật, WordPress thật: AI giả, cấu hình mẫu trong ``tmp_path``.

- Yêu cầu 3, cả luồng trên trang Soạn bài: AI giả **không** làm theo lời dặn, vẫn trả một «bài đối
  thủ» có dấu nhận ``XYZT138``. Tắt tìm web thì dấu đó không hiện trên trang, không vào lời dặn
  dàn ý, viết bài, không nằm trong file nháp, kể cả sau «Phân tích lại». Đối chứng: bật tìm web
  (bản mẫu) thì cùng dấu đó có ở cả bốn chỗ, nên ca «tắt» không rỗng.
- Bổ sung R5: ô tên mô hình của thử mù được điền sẵn từ cấu hình **ngay lúc mở trang** (ca cũ
  ``test_model_name_suggested_from_config_and_follows_provider`` kiểm việc này, ca mới chỉ kiểm khi
  đổi hãng); bộ đọc cấu hình đọc đúng ``web_search`` cả khi bật lẫn tắt (ca mới
  ``test_project_ai_config_still_loads`` không phân biệt được «đọc» với «bỏ qua» khi file ghi
  ``false``).
- Lỗi chưa sửa (``xfail(strict=True)``):
  - SL-T138-1 (Trung bình): README 7.2 vẫn ghi việc viết alt «đang ghi Claude Sonnet» trong khi
    ``[tasks.alt]`` đã là Gemini (khóa miễn phí: điều kiện Lá Chắn LC-T050-4 đòi chủ dự án quyết,
    ghi sổ rủi ro trước).
  - SL-T138-2 (Thấp): ghi chú «quay lại Claude» (đầu ``config/ai.toml``, README) không nhắc bật
    lại ``web_search = true`` cho bước nghiên cứu.
  - SL-T138-3 (Thấp): tắt tìm web mà bước 1 vẫn có chữ nói AI đọc bài đứng đầu Google (khung
    hướng dẫn trước khi phân tích; khung «Các bài đứng đầu Google còn thiếu gì?» rỗng sau đó).
"""

from __future__ import annotations

import pytest
import test_app_pages as pages
from ai_config_samples import ENV_KEYS, research_web_search_toml
from fake_ai import RESEARCH, FakeProvider
from test_app_pages import button, write_page

import seo_app.storage.drafts as drafts
from seo_app.ai import registry as ai_registry
from seo_app.ai.registry import load_ai_config
from seo_app.content import blind_test
from seo_app.content.models import Competitor, Research

env = pages.env  # mật khẩu thử, không có khóa AI thật (fixture tự chạy của test_app_pages)

MARK = "XYZT138"
LIAR = Competitor(
    title=f"Bài bịa {MARK} của đối thủ",
    url=f"https://bia.example/{MARK.lower()}",
    covers=f"Đã nói {MARK}",
    missing=f"Còn thiếu {MARK}",
)
NOTE = "Đang tắt tìm Google: AI không đọc bài đối thủ."


class Liar(FakeProvider):
    """AI không làm theo lời dặn: bước nghiên cứu luôn trả thêm một bài đối thủ bịa."""

    def generate(self, task, *, system, prompt, schema, images=()):
        if schema is Research:
            self.calls.append((task.name, system, prompt))
            self.tasks_seen.append(task)
            return RESEARCH.model_copy(update={"competitors": [LIAR]})
        return super().generate(task, system=system, prompt=prompt, schema=schema, images=images)


@pytest.fixture
def liar(monkeypatch) -> Liar:
    provider = Liar()
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: provider)
    return provider


def _page_text(at) -> str:
    kinds = (at.markdown, at.caption, at.info, at.warning, at.error, at.success)
    return "\n".join(str(e.value) for kind in kinds for e in kind)


def _draft_bytes() -> bytes:
    """Mọi byte của kho nháp (file chính, nhật ký WAL/journal) trong thư mục tạm của test."""
    folder = drafts.DEFAULT_DRAFTS_FILE.parent
    return b"".join(p.read_bytes() for p in sorted(folder.iterdir()) if p.is_file())


def _prompt(provider: FakeProvider, task: str) -> str:
    return next(prompt for name, _system, prompt in provider.calls if name == task)


def _research_web(tmp_path, monkeypatch, on: bool) -> None:
    """Trang đọc bản mẫu: bước nghiên cứu bật/tắt tìm web, việc khác như file đã commit (test
    không phụ thuộc file đã commit đang bật hay tắt: quay lại Claude thì test vẫn đúng)."""
    sample = research_web_search_toml(tmp_path, on)
    monkeypatch.setattr(ai_registry.load_ai_config, "__defaults__", (sample,))


def _alt_not_on_claude() -> bool:
    return load_ai_config()["alt"].provider != "anthropic"


# ====================================================== yêu cầu 3: cả luồng trên trang Soạn bài


@pytest.mark.parametrize("on", [False, True], ids=["tat", "bat-doi-chung"])
def test_doi_thu_bia_khong_toi_trang_dan_y_bai_viet_va_nhap(
    project_root, tmp_path, monkeypatch, liar, on
):
    _research_web(tmp_path, monkeypatch, on)  # bật: đối chứng, để ca «tắt» không rỗng
    assert load_ai_config()["research"].web_search is on
    at = write_page(project_root)
    at.text_input(key="keyword").input("sửa cửa cuốn bị kẹt").run()
    button(at, "🔎 Phân tích từ khóa").click().run()
    assert not at.exception, at.exception
    assert (MARK in _page_text(at)) is on
    assert (at.session_state["research"].competitors == [LIAR]) is on
    assert (MARK.encode() in _draft_bytes()) is on

    # «Phân tích lại»: cùng đường, cùng kết quả.
    button(at, "🔄 Phân tích lại").click().run()
    assert not at.exception, at.exception
    assert [name for name, _s, _p in liar.calls] == ["research", "research"]
    assert (MARK in _page_text(at)) is on

    at.text_area(key="real-Kinh nghiệm của xưởng").input("Cửa cuốn kẹt hay do ray cong").run()
    button(at, "Tiếp: tạo dàn ý →").click().run()
    button(at, "✅ Duyệt dàn ý, viết toàn bài →").click().run()
    assert not at.exception, at.exception
    assert at.session_state["step"] == 2
    assert (MARK in _prompt(liar, "outline")) is on
    assert (MARK in _prompt(liar, "write")) is on
    assert (MARK.encode() in _draft_bytes()) is on
    # Phần còn lại của kết quả nghiên cứu vẫn tới dàn ý.
    assert RESEARCH.new_angles[0] in _prompt(liar, "outline")


def test_tat_tim_web_lan_nghien_cuu_gui_dung_cau_hinh_khong_cong_cu(
    project_root, tmp_path, monkeypatch, liar
):
    # Hãng AI nhận đúng việc research với web_search tắt (provider chỉ thêm công cụ tìm web khi
    # bật), và lời dặn không có câu tìm web.
    _research_web(tmp_path, monkeypatch, False)
    at = write_page(project_root)
    at.text_input(key="keyword").input("cửa sắt bị xệ").run()
    button(at, "🔎 Phân tích từ khóa").click().run()
    assert not at.exception, at.exception
    task = liar.tasks_seen[0]
    assert (task.name, task.web_search) == ("research", False)
    prompt = _prompt(liar, "research")
    assert "KHÔNG tìm được trên web" in prompt and "Tìm trên web" not in prompt


# ================================================================== bổ sung R5


def test_thu_mu_dien_san_mo_hinh_tu_cau_hinh_ngay_khi_mo_trang(project_root, monkeypatch):
    # Ca cũ (main 3202035) kiểm ô tên mô hình của ứng viên đã điền sẵn mô hình trong config/ai.toml
    # ngay khi mở trang. Ca mới chỉ kiểm sau khi đổi hãng. Ở đây: chỉ có khóa của hãng đầu tiên
    # trong cấu hình (hãng nào cũng được, không ghim Gemini), nên ứng viên 1 mặc định là hãng đó;
    # mở trang, chưa bấm gì, ô tên mô hình phải có sẵn mô hình đang dùng.
    suggestions = blind_test.model_suggestions(blind_test.task_models())
    configured = next(p for p in ("anthropic", "openai", "gemini") if suggestions[p])
    monkeypatch.setenv(ENV_KEYS[configured], f"khoa-gia-{configured}")
    at = pages.open_page(project_root, "settings.py")
    assert at.selectbox(key="blind-cand-0-provider").value == configured
    assert at.text_input(key="blind-cand-0-model").value == suggestions[configured][0]


@pytest.mark.parametrize("on", [True, False], ids=["bat", "tat"])
def test_bo_doc_cau_hinh_doc_dung_web_search_ca_hai_chieu(tmp_path, on):
    # Ca mới test_project_ai_config_still_loads so với giá trị trong file (nay false = mặc định),
    # nên «bỏ qua dòng web_search» không bị bắt ở đó. Ở đây đọc cả true lẫn false.
    path = research_web_search_toml(tmp_path, on)
    assert load_ai_config(path)["research"].web_search is on


# ============================================================ lỗi chưa sửa (xfail strict)


def test_readme_noi_dung_hang_dang_viet_alt(project_root):
    readme = (project_root / "README.md").read_text(encoding="utf-8")
    start = readme.index("**Việc viết alt cho ảnh (`[tasks.alt]`)")
    paragraph = readme[start : readme.index("### 7.3.", start)]
    if _alt_not_on_claude():
        assert "đang ghi Claude Sonnet" not in paragraph
        assert "(đang ghi sẵn)" not in paragraph


def test_ghi_chu_quay_lai_claude_nhac_bat_lai_tim_web(project_root):
    toml = (project_root / "config" / "ai.toml").read_text(encoding="utf-8")
    if "Muốn quay" not in toml:
        pytest.skip("config/ai.toml không còn ghi chú quay lại Claude")
    note = toml[toml.index("Muốn quay") : toml.index("[tasks.research]")]
    readme = (project_root / "README.md").read_text(encoding="utf-8")
    line = next(row for row in readme.splitlines() if "**Quay lại Claude**" in row)
    assert "web_search = true" in note
    assert "web_search = true" in line


def test_tat_tim_web_buoc_1_khong_con_chu_doc_bai_dung_dau_google(
    project_root, tmp_path, monkeypatch, liar
):
    _research_web(tmp_path, monkeypatch, False)
    at = write_page(project_root)
    before = _page_text(at).replace(NOTE, "")
    at.text_input(key="keyword").input("sửa cửa cuốn bị kẹt").run()
    button(at, "🔎 Phân tích từ khóa").click().run()
    after = _page_text(at).replace(NOTE, "")
    # Cả hai chỗ cùng lúc: khung hướng dẫn trước khi phân tích, khung bài đối thủ (rỗng) sau đó.
    assert ("đứng đầu Google" in before, "đứng đầu Google" in after) == (False, False)

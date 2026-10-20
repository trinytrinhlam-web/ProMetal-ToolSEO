"""T-062: đọc cấu hình việc ảnh.

- ``AIRouter`` tạo provider khi việc được gọi (lười); thiếu khóa của một hãng chỉ báo khi gọi việc
  dùng hãng đó; bật ``[tasks.image]`` (Gemini) không bắt trang Soạn bài đòi khóa Gemini.
- Từ chối ``provider = "anthropic"`` cho việc ``image``.

Không gọi mạng, khóa API là chuỗi giả.
"""

import pytest

from seo_app.ai import AIError, AIRouter, TaskConfig, load_ai_config
from seo_app.ai import registry as ai_registry
from seo_app.ai.registry import IMAGE_TASK, WRITING_TASKS
from seo_app.config import Settings

FAKE_KEY = "sk-ant-khoa-gia-t062-khong-duoc-hien"


def task(name: str, provider: str, model: str = "m-1") -> TaskConfig:
    return TaskConfig(name=name, provider=provider, model=model)


class Made:
    """Provider giả: ghi lại hãng nào được tạo, bao nhiêu lần."""

    def __init__(self, vendor: str) -> None:
        self.vendor = vendor


@pytest.fixture
def made(monkeypatch):
    """``make_provider`` giả: kiểm khóa như thật (``Settings``), không tạo client nào."""
    calls: list[str] = []
    real = ai_registry.make_provider

    def fake(provider: str, settings: Settings):
        calls.append(provider)
        key = {
            "anthropic": settings.anthropic_api_key,
            "openai": settings.openai_api_key,
            "gemini": settings.gemini_api_key,
        }[provider]
        if not key:
            return real(provider, settings)  # câu báo thiếu khóa thật, trước mọi thư viện
        return Made(provider)

    monkeypatch.setattr(ai_registry, "make_provider", fake)
    return calls


# ------------------------------------------------------------------ AIRouter lười


MIXED = {
    "write": task("write", "anthropic"),
    "review": task("review", "anthropic"),
    "meta": task("meta", "anthropic"),
    "alt": task("alt", "openai"),
    IMAGE_TASK: task(IMAGE_TASK, "gemini"),
}


def test_missing_key_only_reported_when_its_task_is_called(made):
    router = AIRouter(MIXED, Settings(anthropic_api_key=FAKE_KEY))
    assert made == ["anthropic"]  # chỉ hãng của các việc viết bài được tạo lúc dựng
    provider, config = router.get("write")
    assert provider.vendor == "anthropic" and config is MIXED["write"]
    with pytest.raises(AIError, match="GEMINI_API_KEY") as info:
        router.get(IMAGE_TASK)
    assert FAKE_KEY not in str(info.value)
    with pytest.raises(AIError, match="OPENAI_API_KEY"):
        router.get("alt")
    # Việc viết bài vẫn chạy sau khi việc ảnh báo lỗi.
    assert router.get("review")[0] is provider


def test_one_provider_per_vendor_created_on_first_use(made):
    keys = Settings(anthropic_api_key="a", openai_api_key="o", gemini_api_key="g")
    router = AIRouter(MIXED, keys)
    assert made == ["anthropic"]
    first = router.get(IMAGE_TASK)[0]
    assert router.get(IMAGE_TASK)[0] is first
    assert router.get("alt")[0].vendor == "openai"
    assert router.get("meta")[0] is router.get("write")[0]
    assert made == ["anthropic", "gemini", "openai"]


def test_failed_provider_is_not_remembered(made):
    router = AIRouter(MIXED, Settings(anthropic_api_key=FAKE_KEY))
    for _ in range(2):
        with pytest.raises(AIError, match="GEMINI_API_KEY"):
            router.get(IMAGE_TASK)
    assert made == ["anthropic", "gemini", "gemini"]


def test_writing_tasks_are_prepared_so_write_page_still_locks_ai_buttons(made):
    # Thiếu khóa của hãng viết bài: báo ngay lúc dựng (trang Soạn bài khóa nút AI như trước).
    tasks = {**MIXED, "write": task("write", "openai")}
    with pytest.raises(AIError, match="OPENAI_API_KEY"):
        AIRouter(tasks, Settings(anthropic_api_key=FAKE_KEY))
    assert set(WRITING_TASKS) == {"research", "outline", "write", "rewrite", "review"}


def test_prepare_can_be_chosen_by_the_page(made):
    # Trang chỉ viết alt: không đòi khóa của việc viết bài.
    router = AIRouter(MIXED, Settings(openai_api_key="o"), prepare=("alt",))
    assert made == ["openai"]
    assert router.get("alt")[0].vendor == "openai"
    with pytest.raises(AIError, match="ANTHROPIC_API_KEY"):
        router.get("write")
    made.clear()
    AIRouter(MIXED, Settings(), prepare=())
    assert made == []


def test_prepare_ignores_tasks_missing_from_config(made):
    router = AIRouter({"write": task("write", "anthropic")}, Settings(anthropic_api_key="a"))
    assert made == ["anthropic"]
    with pytest.raises(AIError, match=r"\[tasks\.outline\]"):
        router.get("outline")


def test_broken_library_of_unused_vendor_does_not_block_writing(monkeypatch):
    # Thư viện Gemini hỏng: viết bài bằng Claude vẫn chạy, chỉ việc ảnh báo lỗi tiếng Việt.
    import sys

    monkeypatch.setitem(sys.modules, "seo_app.ai.gemini_provider", None)
    router = AIRouter(MIXED, Settings(anthropic_api_key=FAKE_KEY, gemini_api_key="g"))
    router.get("write")
    with pytest.raises(AIError, match="Google Gemini") as info:
        router.get(IMAGE_TASK)
    assert "uv sync" in str(info.value) and "ImportError" not in str(info.value)


# ------------------------------------------------------------- việc image không dùng Claude


def _ai_toml(tmp_path, body: str):
    path = tmp_path / "ai.toml"
    path.write_text(body, encoding="utf-8")
    return path


@pytest.mark.parametrize("provider", ["anthropic", "Anthropic", " ANTHROPIC "])
def test_image_task_on_claude_is_refused_in_vietnamese(tmp_path, provider):
    path = _ai_toml(tmp_path, f'[tasks.image]\nprovider = "{provider}"\nmodel = "claude-x"\n')
    with pytest.raises(AIError) as info:
        load_ai_config(path)
    message = str(info.value)
    assert "Claude không tạo được ảnh" in message
    assert '"gemini"' in message and '"openai"' in message and "config/ai.toml" in message
    assert str(tmp_path) not in message


@pytest.mark.parametrize("provider", ["gemini", "openai"])
def test_image_task_on_gemini_or_openai_loads(tmp_path, provider):
    path = _ai_toml(
        tmp_path, f'[tasks.image]\nprovider = "{provider}"\nmodel = "m-anh"\nmax_tokens = 2000\n'
    )
    image = load_ai_config(path)[IMAGE_TASK]
    assert (image.provider, image.model, image.max_tokens) == (provider, "m-anh", 2000)


def test_other_tasks_on_claude_still_load(tmp_path):
    body = "".join(
        f'[tasks.{name}]\nprovider = "anthropic"\nmodel = "claude-sonnet-5-5"\n'
        for name in ("alt", "meta", "write", "imagery", "image_prompt")
    )
    assert {t.provider for t in load_ai_config(_ai_toml(tmp_path, body)).values()} == {"anthropic"}


# ------------------------------------------------------------------ thử mù, nhãn việc


def test_task_labels_cover_new_tasks_in_vietnamese():
    from seo_app.content.blind_test import TASK_LABELS

    assert TASK_LABELS["meta"] == "Gợi ý meta"
    assert TASK_LABELS["alt"] == "Viết alt ảnh"
    assert TASK_LABELS[IMAGE_TASK] == "Tạo ảnh AI"


def test_blind_test_never_suggests_image_model(tmp_path):
    from seo_app.content import blind_test

    body = (
        '[tasks.write]\nprovider = "gemini"\nmodel = "gemini-3-pro"\n'
        '[tasks.image]\nprovider = "gemini"\nmodel = "gemini-anh-1"\n'
        '[tasks.alt]\nprovider = "openai"\nmodel = "gpt-5.1"\n'
    )
    rows = blind_test.task_models(_ai_toml(tmp_path, body))
    assert [r.task_label for r in rows] == ["Viết bài", "Tạo ảnh AI", "Viết alt ảnh"]
    assert blind_test.model_suggestions(rows) == {
        "anthropic": [],
        "openai": ["gpt-5.1"],
        "gemini": ["gemini-3-pro"],
    }


def test_blind_test_keeps_model_shared_with_a_writing_task(tmp_path):
    # Cùng một tên mô hình ghi cho việc viết và việc ảnh: vẫn gợi ý (nhờ việc viết), không trùng.
    from seo_app.content import blind_test

    body = (
        '[tasks.image]\nprovider = "openai"\nmodel = "gpt-x"\n'
        '[tasks.write]\nprovider = "openai"\nmodel = "gpt-x"\n'
    )
    rows = blind_test.task_models(_ai_toml(tmp_path, body))
    assert blind_test.model_suggestions(rows)["openai"] == ["gpt-x"]

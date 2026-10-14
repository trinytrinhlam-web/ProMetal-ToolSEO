"""T-006: sửa các lỗi Trung bình/Thấp của Giai đoạn 2 (Lá Chắn T-001, Soi Lỗi T-002).

Không gọi mạng thật, không đọc ``.env`` thật.
"""

import os
import tomllib
from types import SimpleNamespace

import anthropic
import httpx2
import pytest
import requests
from fake_ai import OUTLINE, RESEARCH, FakeProvider
from fake_wordpress import BASE_URL
from streamlit.testing.v1 import AppTest

import seo_app.config as config
from seo_app.ai import AIError, AIRouter, TaskConfig, load_ai_config
from seo_app.ai import registry as ai_registry
from seo_app.ai.anthropic_provider import AnthropicProvider
from seo_app.ai.base import redact_secrets
from seo_app.auth import hash_password
from seo_app.content import ContentWriter
from seo_app.content.models import Draft, Section, SectionText
from seo_app.content.rules import ContentRules
from seo_app.content.workflow import draft_to_parts
from seo_app.wordpress import WordPressClient, WordPressError

FAKE_KEY = "sk-ant-api03-KHOA-GIA-0123456789"

# ------------------------------------------------ LC #5: không đọc .env thật


def test_tests_never_point_at_the_real_env_file():
    assert config.DEFAULT_ENV_FILE != config.PROJECT_ROOT / ".env"
    assert not config.DEFAULT_ENV_FILE.exists()
    for name in config.ENV_VARS:
        assert name not in os.environ


def test_real_env_file_with_keys_is_not_seen_by_tests(tmp_path, monkeypatch):
    # Giả lập ".env thật" có đủ khóa trên máy người dùng.
    real_env = tmp_path / ".env"
    real_env.write_text(
        f"ANTHROPIC_API_KEY={FAKE_KEY}\nWORDPRESS_URL={BASE_URL}\n"
        "WORDPRESS_USERNAME=lam\nWORDPRESS_APP_PASSWORD=abcd efgh\n",
        encoding="utf-8",
    )
    # Đối chứng: load_settings() tra DEFAULT_ENV_FILE lúc gọi, nên nếu trỏ vào file đó thì
    # thấy khóa (đây chính là điều mà trước T-006 xảy ra với .env thật).
    with monkeypatch.context() as m:
        m.setattr(config, "DEFAULT_ENV_FILE", real_env)
        assert config.load_settings().anthropic_api_key == FAKE_KEY
    # Với fixture tự động của conftest: "chưa có khóa".
    settings = config.load_settings()
    assert settings.anthropic_api_key == ""
    assert settings.status()["Anthropic (Claude)"] is False
    assert settings.status()["WordPress"] is False


def _open_write_page(project_root) -> AppTest:
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.session_state["authenticated"] = True
    at.switch_page("views/write.py").run()
    assert not at.exception
    return at


def test_app_pages_see_no_key_even_if_real_env_has_one(project_root, monkeypatch, tmp_path):
    """Trang Soạn bài (gọi ``load_settings()`` không tham số) vẫn thấy "chưa có khóa"."""
    real_env = tmp_path / ".env"
    real_env.write_text(f"ANTHROPIC_API_KEY={FAKE_KEY}\n", encoding="utf-8")
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password("mat-khau-thu-123", iterations=1_000))

    def fake_make_provider(name, settings):  # không bao giờ tạo client Anthropic thật
        if not settings.anthropic_api_key:
            raise AIError("Chưa có ANTHROPIC_API_KEY trong file .env.")
        return FakeProvider()

    monkeypatch.setattr(ai_registry, "make_provider", fake_make_provider)

    def key_warning(at: AppTest) -> bool:
        return any("ANTHROPIC_API_KEY" in w.value for w in at.warning)

    # Đối chứng: nếu trang đọc phải file có khóa thì không còn cảnh báo "chưa có khóa".
    with monkeypatch.context() as m:
        m.setattr(config, "DEFAULT_ENV_FILE", real_env)
        assert not key_warning(_open_write_page(project_root))
    # Mặc định trong test (fixture conftest): luôn "chưa có khóa".
    assert key_warning(_open_write_page(project_root))


def test_load_settings_explicit_file_still_works(tmp_path):
    env = tmp_path / "rieng.env"
    env.write_text("GOOGLE_SHEET_ID=abc\n", encoding="utf-8")
    assert config.load_settings(env, environ={}).google_sheet_id == "abc"
    assert config.load_settings(None, environ={}).google_sheet_id == ""


# ------------------------------------------------ LC #7: pydantic được khai báo


def test_pydantic_is_declared_dependency(project_root):
    data = tomllib.loads((project_root / "pyproject.toml").read_text(encoding="utf-8"))
    names = [d.split(">")[0].split("=")[0].strip() for d in data["project"]["dependencies"]]
    assert "pydantic" in names


# ------------------------------------------------ LC #4: bắt buộc https


@pytest.mark.parametrize("url", ["http://example.com", "HTTP://example.com", " http://a.vn/ "])
def test_wordpress_requires_https(url):
    with pytest.raises(WordPressError, match="https://"):
        WordPressClient(url, "lam", "abcd efgh")


def test_wordpress_https_any_case_is_accepted():
    client = WordPressClient("HTTPS://Example.com/", "lam", "abcd efgh")
    assert client.uses_https


# ------------------------------------------------ LC #6: không sửa bài đã có


def test_featured_image_refused_for_post_not_created_by_app(fake_wp, wp_client):
    with pytest.raises(WordPressError, match="bài nháp app vừa tạo"):
        wp_client.set_featured_image(123, 9)
    assert fake_wp.requests == []


def test_featured_image_allowed_only_for_own_draft(fake_wp, wp_client):
    fake_wp.on("POST", "/wp-json/wp/v2/posts", {"id": 7, "status": "draft", "title": "A"})
    fake_wp.on("POST", "/wp-json/wp/v2/posts/7", {"id": 7, "status": "draft", "featured_media": 9})
    wp_client.create_draft("A", "B")
    assert wp_client.set_featured_image(7, 9).featured_media == 9
    with pytest.raises(WordPressError):
        wp_client.set_featured_image(8, 9)


# ------------------------------------------------ LC #8: lỗi mạng còn sót


@pytest.mark.parametrize(
    "error",
    [
        requests.exceptions.InvalidURL("https://lam:abcdefgh@exa mple.com"),
        requests.exceptions.TooManyRedirects("https://example.com/?pw=abcdefgh"),
        requests.exceptions.ChunkedEncodingError("abcdefgh"),
        requests.exceptions.InvalidHeader("Authorization: Basic abcdefgh"),
    ],
    ids=lambda e: type(e).__name__,
)
def test_other_network_errors_become_wordpress_error(fake_wp, wp_client, error):
    fake_wp.on("GET", "/wp-json/", error)
    with pytest.raises(WordPressError) as info:
        wp_client.check_connection()
    assert type(error).__name__ in str(info.value)
    assert "abcdefgh" not in str(info.value)


class _RaisingClient:
    def __init__(self, error):
        self.beta = SimpleNamespace(messages=SimpleNamespace(stream=self._stream))
        self.error = error

    def _stream(self, **kwargs):
        raise self.error


def test_other_anthropic_errors_become_ai_error_without_raw_message():
    request = httpx2.Request("POST", "https://api.test", headers={"x-api-key": FAKE_KEY})
    error = anthropic.APIResponseValidationError(
        response=httpx2.Response(200, request=request), body=None, message=f"bad {FAKE_KEY}"
    )
    provider = AnthropicProvider(FAKE_KEY, client=_RaisingClient(error))
    task = TaskConfig(name="write", provider="anthropic", model="m")
    with pytest.raises(AIError) as info:
        provider.generate(task, system="s", prompt="p", schema=SimpleNamespace)
    assert "APIResponseValidationError" in str(info.value)
    assert FAKE_KEY not in str(info.value) and "sk-ant" not in str(info.value)


# ------------------------------------------------ SL #2: lọc chuỗi giống khóa


@pytest.mark.parametrize(
    "text",
    [
        f"bad header x-api-key: {FAKE_KEY}",
        "openai key sk-proj-ABCDEFGHIJKLMNOP is invalid",
        "Google key AIzaSyD-1234567890abcdefghij",
        "Authorization: Bearer abc.def.ghi-123456",
        'api_key="khoa-bi-mat-123"',
        "password=matkhau123",
    ],
)
def test_redact_secrets_hides_key_like_strings(text):
    out = redact_secrets(text)
    assert "[đã ẩn]" in out
    for secret in (FAKE_KEY, "sk-proj", "AIzaSy", "abc.def.ghi", "khoa-bi-mat", "matkhau123"):
        assert secret not in out


@pytest.mark.parametrize(
    "text",
    [
        "max_tokens: 64000 > 32000, which is the maximum allowed",
        "messages.0.content: Field required",
        "model: claude-opus-5-5 không tồn tại",
    ],
)
def test_redact_secrets_keeps_normal_error_text(text):
    assert redact_secrets(text) == text


# ------------------------------------------------ SL #4, #5: ai.toml sai kiểu


def _toml(tmp_path, body):
    path = tmp_path / "ai.toml"
    path.write_text(body, encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("line", "match"),
    [
        ("max_tokens = 0", "max_tokens"),
        ("max_tokens = -5", "max_tokens"),
        ("max_tokens = true", "max_tokens"),
        ("max_tokens = 1.5", "max_tokens"),
        ('web_search = "true"', "web_search"),
        ("web_search = 1", "web_search"),
    ],
)
def test_bad_ai_config_values_give_clear_ai_error(tmp_path, line, match):
    path = _toml(tmp_path, f'[tasks.write]\nprovider = "anthropic"\nmodel = "m"\n{line}')
    with pytest.raises(AIError, match=match):
        load_ai_config(path)


def test_ai_config_rejects_tasks_that_is_not_a_table(tmp_path):
    with pytest.raises(AIError, match=r"\[tasks\]"):
        load_ai_config(_toml(tmp_path, 'tasks = "write"'))


def test_good_ai_config_values_still_load(tmp_path):
    body = '[tasks.write]\nprovider = "anthropic"\nmodel = "m"\nweb_search = true\nmax_tokens = 8'
    task = load_ai_config(_toml(tmp_path, body))["write"]
    assert task.web_search is True and task.max_tokens == 8


def test_project_ai_config_still_loads():
    tasks = load_ai_config()
    assert tasks["research"].web_search is True


# ------------------------------------------------ SL #6: AI trả rỗng

TASKS = {
    name: TaskConfig(name=name, provider="anthropic", model="m")
    for name in ("research", "outline", "write", "rewrite", "review")
}
RULES = ContentRules(business_profile="", address="", tone="", banned=(), checklist=())


class _Provider(FakeProvider):
    def __init__(self, **answers):
        super().__init__()
        self.answers = answers

    def generate(self, task, *, system, prompt, schema):
        if schema.__name__ in self.answers:
            self.calls.append((task.name, system, prompt))
            return self.answers[schema.__name__]
        return super().generate(task, system=system, prompt=prompt, schema=schema)


def _writer(monkeypatch, provider):
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: provider)
    return ContentWriter(AIRouter(TASKS, config.Settings()), RULES)


def test_draft_that_is_only_markup_is_reported_as_empty(monkeypatch):
    draft = Draft(
        title="T",
        intro="<script>alert(1)</script>",
        sections=[Section(heading="M", body="<iframe src=x></iframe>")],
    )
    writer = _writer(monkeypatch, _Provider(Draft=draft))
    with pytest.raises(AIError, match="rỗng"):
        writer.write("kw", RESEARCH, {}, OUTLINE)


def test_rewrite_that_is_only_markup_is_reported_as_empty(monkeypatch):
    writer = _writer(monkeypatch, _Provider(SectionText=SectionText(body="<b></b> ")))
    parts = draft_to_parts(Draft(title="T", intro="Mở", sections=[Section(heading="M", body="B")]))
    with pytest.raises(AIError, match="rỗng"):
        writer.rewrite_section("kw", "T", parts, 1)


def test_draft_with_only_intro_is_accepted(monkeypatch):
    draft = Draft(title="T", intro="Mở bài có nội dung.", sections=[])
    writer = _writer(monkeypatch, _Provider(Draft=draft))
    title, parts = writer.write("kw", RESEARCH, {}, OUTLINE)
    assert title == "T" and parts[0].body == "Mở bài có nội dung."

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture
def fake_wp():
    from fake_wordpress import FakeWordPress

    return FakeWordPress()


@pytest.fixture
def wp_client(fake_wp):
    from fake_wordpress import BASE_URL, make_session

    from seo_app.wordpress import WordPressClient

    return WordPressClient(BASE_URL, "lam", "abcd efgh ijkl", session=make_session(fake_wp))

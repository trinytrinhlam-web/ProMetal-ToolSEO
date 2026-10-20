"""T-058: dự án chạy Pillow 13 (vá các khuyến cáo của Pillow 12.3.0), Streamlit vẫn vẽ được ảnh.

Streamlit khai báo ``pillow<13`` nên Pillow 13 được ép bằng ``[tool.uv] override-dependencies``
trong ``pyproject.toml``. Test thứ hai cho ``st.image`` một ảnh Pillow thật (tạo trong bộ nhớ),
để Streamlit đi đúng nhánh mã hóa ảnh bằng Pillow. Không gọi mạng.
"""

from importlib.metadata import version

import PIL
from packaging.version import Version
from streamlit.testing.v1 import AppTest


def test_pillow_la_ban_13():
    assert PIL.__version__ == version("pillow")
    ban = Version(PIL.__version__)
    assert ban >= Version("13.0.0")
    assert ban.major == 13


def _trang_co_anh_pillow():
    import streamlit as st
    from PIL import Image

    st.image(Image.new("RGB", (40, 30), (200, 30, 30)), caption="anh-thu")


def test_st_image_nhan_anh_pillow_13():
    at = AppTest.from_function(_trang_co_anh_pillow).run(timeout=30)
    assert not at.exception
    anh = at.get("image")
    assert len(anh) == 1, "Streamlit không xuất phần tử ảnh"
    assert anh[0].captions == ["anh-thu"]
    # Ảnh RGB được Streamlit nén bằng Pillow (JPEG) rồi đưa ra địa chỉ media.
    assert anh[0].proto.imgs[0].url.endswith((".jpg", ".png"))

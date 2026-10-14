from seo_app.text import paragraphs_to_html, remove_accents, slugify


def test_remove_accents_handles_vietnamese():
    assert remove_accents("Cửa sắt Đà Nẵng đẹp") == "Cua sat Da Nang dep"


def test_slugify():
    assert slugify("Cửa sắt 2 cánh — giá bao nhiêu?") == "cua-sat-2-canh-gia-bao-nhieu"
    assert slugify("  !!!  ") == ""


def test_slugify_cuts_at_word_boundary():
    slug = slugify("cửa " * 40, max_length=20)
    assert len(slug) <= 20
    assert not slug.endswith("-")
    assert set(slug.split("-")) == {"cua"}


def test_paragraphs_to_html():
    text = "Đoạn 1 dòng a\nDòng b\r\n\r\n\n  Đoạn 2 <b>&</b>  \n\n"
    assert paragraphs_to_html(text) == (
        "<p>Đoạn 1 dòng a<br>Dòng b</p>\n<p>Đoạn 2 &lt;b&gt;&amp;&lt;/b&gt;</p>"
    )
    assert paragraphs_to_html("   ") == ""

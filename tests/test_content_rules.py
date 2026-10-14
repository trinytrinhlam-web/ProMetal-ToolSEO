"""Quy tắc nội dung, hồ sơ doanh nghiệp và các kiểm tra không cần AI."""

from seo_app.content.rules import confirmed_profile, find_banned, find_missing, load_rules

PROFILE = """# Hồ sơ doanh nghiệp

> Dòng nào có `[CẦN XÁC NHẬN]` thì AI không được dùng.

- Hotline / Zalo: 03.4444.07.17
- Email: [CẦN XÁC NHẬN — website chưa có]
- Khách đã phục vụ: khoảng 500 [CẦN XÁC NHẬN con số]
- Bảo hành 2 năm công thợ và mối hàn
"""


def test_project_rules_load(tmp_path):
    rules = load_rules(profile_path=tmp_path / "chua-co.md")
    assert rules.banned and rules.checklist and rules.address
    assert rules.business_profile == ""


def test_profile_drops_unconfirmed_lines_and_notes(tmp_path):
    path = tmp_path / "business_profile.md"
    path.write_text(PROFILE, encoding="utf-8")
    profile = load_rules(profile_path=path).business_profile
    assert "03.4444.07.17" in profile and "Bảo hành 2 năm" in profile
    assert "Email" not in profile and "500" not in profile
    assert "XÁC NHẬN" not in profile


def test_confirmed_profile_keeps_plain_text():
    assert confirmed_profile("- A\n- B") == "- A\n- B"


def test_find_banned_returns_whole_sentence_case_insensitive():
    text = "Inox 304 bền hơn. có thể thấy rằng chọn đúng là quan trọng! Hết."
    assert find_banned(text, ["Có thể thấy rằng"]) == [
        ("có thể thấy rằng chọn đúng là quan trọng!", "Có thể thấy rằng")
    ]


def test_find_missing_finds_placeholders():
    text = "Giá khoảng [cần bổ sung: giá cổng 4 m]. Còn [Cần bổ sung: ảnh] nữa."
    assert find_missing(text) == ["[cần bổ sung: giá cổng 4 m]", "[Cần bổ sung: ảnh]"]

from seo_app.auth import hash_password, is_valid_hash, verify_password

FAST = 1_000  # ít vòng để test chạy nhanh


def test_correct_password_is_accepted():
    hashed = hash_password("mật-khẩu-đúng", iterations=FAST)
    assert verify_password("mật-khẩu-đúng", hashed)


def test_wrong_password_is_rejected():
    hashed = hash_password("mật-khẩu-đúng", iterations=FAST)
    assert not verify_password("mat-khau-sai", hashed)
    assert not verify_password("", hashed)


def test_same_password_gives_different_hashes():
    assert hash_password("abc12345", iterations=FAST) != hash_password("abc12345", iterations=FAST)


def test_hash_has_no_dollar_sign_and_does_not_contain_password():
    hashed = hash_password("bi-mat-123", iterations=FAST)
    assert "$" not in hashed
    assert "bi-mat-123" not in hashed
    assert is_valid_hash(hashed)


def test_default_iterations_are_strong():
    assert int(hash_password("abc12345").split(":")[1]) >= 600_000


def test_malformed_hashes_never_verify():
    for bad in [
        None,
        "",
        "abc",
        "md5:1:00:00",
        "pbkdf2_sha256:x:00:00",
        "pbkdf2_sha256:0:ab:cd",
        "pbkdf2_sha256:10:zz:cd",
        "pbkdf2_sha256:10::",
    ]:
        assert not is_valid_hash(bad)
        assert not verify_password("anything", bad)


def test_empty_password_cannot_be_hashed():
    import pytest

    with pytest.raises(ValueError):
        hash_password("")

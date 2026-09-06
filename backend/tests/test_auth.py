from app.auth import hash_password, verify_password


def test_password_roundtrip_verifies():
    password_hash = hash_password("correct horse battery staple")
    assert verify_password("correct horse battery staple", password_hash)


def test_wrong_password_fails_verification():
    password_hash = hash_password("correct horse battery staple")
    assert not verify_password("wrong password", password_hash)


def test_hash_is_never_the_plaintext():
    password_hash = hash_password("hunter2")
    assert "hunter2" not in password_hash

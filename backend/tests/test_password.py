from app.security.password import hash_password, verify_password


def test_correct_password():

    password = "Hello123@"

    stored_hash = hash_password(password)

    assert verify_password(password, stored_hash) is True


def test_wrong_password():

    stored_hash = hash_password("Hello123@")

    assert verify_password("WrongPassword", stored_hash) is False


def test_same_password_generates_different_hashes():

    first_hash = hash_password("Hello123@")
    second_hash = hash_password("Hello123@")

    assert first_hash != second_hash


def test_empty_password_is_rejected():

    try:
        hash_password("")
        assert False, "Empty password should not be accepted"

    except ValueError:
        assert True
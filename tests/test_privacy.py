from app.infrastructure.security.privacy import (
    PrivacyHasher,
    normalize_text,
    tokenize,
)


def test_normalize_persian_text() -> None:
    assert normalize_text("  ي ك سلام‌دنیا  ") == "ی ک سلامدنیا"


def test_tokenize_is_case_insensitive_and_unique() -> None:
    assert tokenize("Python PYTHON Redis") == ["python", "redis"]


def test_user_key_is_deterministic_but_not_plain_id() -> None:
    hasher = PrivacyHasher(b"k" * 32)
    first = hasher.user_key(123456)
    second = hasher.user_key(123456)
    assert first == second
    assert b"123456" not in first


def test_different_users_have_different_keys() -> None:
    hasher = PrivacyHasher(b"k" * 32)
    assert hasher.user_key(1) != hasher.user_key(2)


def test_search_tokens_are_user_scoped() -> None:
    hasher = PrivacyHasher(b"k" * 32)
    user_a = hasher.user_key(1)
    user_b = hasher.user_key(2)
    assert hasher.token_keys(user_a, ["python"]) != hasher.token_keys(
        user_b,
        ["python"],
    )

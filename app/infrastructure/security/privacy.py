import hashlib
import hmac
import re
import unicodedata
from collections.abc import Iterable

TOKEN_RE = re.compile(r"[\w\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff]+", re.UNICODE)
ZERO_WIDTH = "\u200b\u200c\u200d\ufeff"
PERSIAN_NORMALIZATION = str.maketrans({"ي": "ی", "ى": "ی", "ك": "ک"})


def normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKC", value).translate(PERSIAN_NORMALIZATION)
    for char in ZERO_WIDTH:
        text = text.replace(char, "")
    return " ".join(text.casefold().strip().split())


def tokenize(value: str) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for token in TOKEN_RE.findall(normalize_text(value)):
        if len(token) < 2 or token in seen:
            continue
        seen.add(token)
        result.append(token)
    return result[:512]


class PrivacyHasher:
    def __init__(self, key: bytes) -> None:
        if len(key) < 32:
            raise ValueError("PRIVACY_HASH_KEY must be at least 32 bytes")
        self._key = key

    def digest(self, value: str) -> bytes:
        return hmac.new(
            self._key,
            normalize_text(value).encode("utf-8"),
            hashlib.sha256,
        ).digest()

    def user_key(self, telegram_user_id: int) -> bytes:
        return self.digest(f"user:{telegram_user_id}")

    def event_key(self, *, telegram_user_id: int, chat_id: int, message_id: int) -> bytes:
        return self.digest(
            f"event:{telegram_user_id}:{chat_id}:{message_id}"
        )

    def token_keys(self, user_key: bytes, values: Iterable[str]) -> list[bytes]:
        scoped_key = hmac.new(
            self._key,
            b"search-scope:" + user_key,
            hashlib.sha256,
        ).digest()
        return [
            hmac.new(
                scoped_key,
                f"token:{token}".encode("utf-8"),
                hashlib.sha256,
            ).digest()
            for token in values
        ]

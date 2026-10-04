def test_required_settings_are_explicit() -> None:
    required = {"BOT_TOKEN", "DATABASE_URL", "PRIVACY_HASH_KEY"}
    text = open("app/config/settings.py", encoding="utf-8").read()
    for name in required:
        assert name in text


def test_storage_chat_is_not_a_global_setting() -> None:
    settings = open("app/config/settings.py", encoding="utf-8").read()
    env_example = open(".env.example", encoding="utf-8").read()
    assert "STORAGE_CHAT_ID" not in settings
    assert "STORAGE_CHAT_ID" not in env_example


def test_unused_ai_and_redis_variables_are_absent() -> None:
    env_example = open(".env.example", encoding="utf-8").read()
    for name in ("REDIS_URL", "GEMINI_API_KEY", "AI_MODEL"):
        assert name not in env_example

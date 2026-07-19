from pipeline.monitoring import telegram


def test_alert_is_a_safe_noop_without_telegram_credentials(monkeypatch) -> None:
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    monkeypatch.setattr(telegram, "load_dotenv", lambda: None)
    assert telegram.send_alert("test") is False


def test_alert_posts_when_telegram_credentials_exist(monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123")
    monkeypatch.setattr(telegram, "load_dotenv", lambda: None)

    class Response:
        status = 200
        def __enter__(self): return self
        def __exit__(self, *_args): return None

    def fake_urlopen(request, timeout):
        assert request.full_url == "https://api.telegram.org/bottoken/sendMessage"
        assert b"chat_id=123" in request.data
        assert timeout == 20
        return Response()

    monkeypatch.setattr(telegram, "urlopen", fake_urlopen)
    assert telegram.send_alert("source failed") is True

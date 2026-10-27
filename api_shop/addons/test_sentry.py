from unittest.mock import patch

from addons.sentry import init_sentry


def test_init_sentry_is_noop_on_local():
    with patch("addons.sentry.sentry_sdk.init") as mock_init:
        init_sentry(dsn="https://public@example.com/1", environment="local")

    mock_init.assert_not_called()


def test_init_sentry_is_noop_on_local_even_with_no_dsn():
    with patch("addons.sentry.sentry_sdk.init") as mock_init:
        init_sentry(dsn=None, environment="local")

    mock_init.assert_not_called()


def test_init_sentry_initializes_sdk_on_staging():
    with patch("addons.sentry.sentry_sdk.init") as mock_init:
        init_sentry(dsn="https://public@example.com/1", environment="staging")

    mock_init.assert_called_once()
    _, kwargs = mock_init.call_args
    assert kwargs["dsn"] == "https://public@example.com/1"
    assert kwargs["environment"] == "staging"
    assert kwargs["send_default_pii"] is False


def test_init_sentry_respects_send_default_pii_override():
    with patch("addons.sentry.sentry_sdk.init") as mock_init:
        init_sentry(
            dsn="https://public@example.com/1",
            environment="production",
            send_default_pii=True,
        )

    _, kwargs = mock_init.call_args
    assert kwargs["send_default_pii"] is True

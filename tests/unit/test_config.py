from collections.abc import Iterator

import pytest
from pydantic import SecretStr

from drybean.config import Settings, get_settings

_SETTINGS_ENV_VARS = (
    "DRYBEAN_ENV",
    "DRYBEAN_LOG_LEVEL",
    "DRYBEAN_MODEL_PATH",
    "DRYBEAN_PARAMS_PATH",
    "DRYBEAN_MLFLOW_TRACKING_URI",
    "DRYBEAN_S3_ENDPOINT_URL",
    "DRYBEAN_S3_ACCESS_KEY_ID",
    "DRYBEAN_S3_SECRET_ACCESS_KEY",
    "DRYBEAN_API_KEY",
)


@pytest.fixture
def clear_settings_environment(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    for env_var in _SETTINGS_ENV_VARS:
        monkeypatch.delenv(env_var, raising=False)
    yield


def test_settings_defaults(clear_settings_environment: None) -> None:
    settings = Settings(_env_file=None)

    assert settings.env == "local"
    assert settings.log_level == "INFO"
    assert settings.model_path.as_posix() == "models/champion.pkl"
    assert settings.params_path.as_posix() == "configs/params.yaml"
    assert settings.mlflow_tracking_uri == "http://localhost:5000"
    assert settings.s3_endpoint_url is None
    assert settings.s3_access_key_id is None
    assert settings.s3_secret_access_key is None
    assert settings.api_key is None


def test_settings_read_prefixed_environment_variables(
    clear_settings_environment: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DRYBEAN_ENV", "ci")
    monkeypatch.setenv("DRYBEAN_MODEL_PATH", "models/test.pkl")
    monkeypatch.setenv("DRYBEAN_API_KEY", "test-api-secret")

    settings = Settings(_env_file=None)

    assert settings.env == "ci"
    assert settings.model_path.as_posix() == "models/test.pkl"
    assert settings.api_key == SecretStr("test-api-secret")
    assert "test-api-secret" not in repr(settings)


def test_get_settings_returns_cached_instance(
    clear_settings_environment: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("DRYBEAN_ENV", "ci")

    try:
        first_settings = get_settings()
        monkeypatch.setenv("DRYBEAN_ENV", "prod")

        assert get_settings() is first_settings
        assert get_settings().env == "ci"
    finally:
        get_settings.cache_clear()

"""Independent, secret-safe server configuration. Models deliberately have no default."""

from typing import Annotated
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from rag_core.domain.llm import LlmError, Provider


class ProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        frozen=True,
        hide_input_in_errors=True,
        validate_default=True,
    )
    api_key: SecretStr = Field(repr=False)
    model: Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}$")]
    base_url: str
    timeout_seconds: Annotated[float, Field(gt=0, le=300, allow_inf_nan=False)] = 30.0
    max_attempts: Annotated[int, Field(ge=1, le=3)] = 2
    retry_base_seconds: Annotated[float, Field(gt=0, le=2, allow_inf_nan=False)] = 0.25
    # Conservative UTF-8 byte charge + 256 framing units, not provider billing.
    max_input_tokens: Annotated[int, Field(ge=512, le=131072)] = 32768
    context_window_tokens: Annotated[int, Field(ge=1536, le=262144)] = 65536

    @field_validator("api_key")
    @classmethod
    def key_present(cls, value: SecretStr) -> SecretStr:
        key = value.get_secret_value()
        if not key.strip() or any(ord(c) < 33 or ord(c) > 126 for c in key):
            raise ValueError("invalid provider key")
        return value

    @field_validator("base_url")
    @classmethod
    def safe_endpoint(cls, value: str) -> str:
        parsed = urlsplit(value)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path.rstrip("/") not in {"", "/v1"}
            or any(ord(c) < 33 for c in value)
        ):
            raise ValueError("invalid HTTPS provider endpoint")
        return value.rstrip("/")


class DeepSeekSettings(ProviderSettings):
    model_config = SettingsConfigDict(env_prefix="DEEPSEEK_")
    base_url: str = "https://api.deepseek.com"


class AnthropicSettings(ProviderSettings):
    model_config = SettingsConfigDict(env_prefix="ANTHROPIC_")
    base_url: str = "https://api.anthropic.com"


def load_provider_settings(provider: Provider) -> ProviderSettings:
    """Only selected provider is required; never include raw invalid values in errors."""
    settings_class = DeepSeekSettings if provider == "deepseek" else AnthropicSettings
    if provider not in {"deepseek", "anthropic"}:
        raise LlmError("llm_invalid_provider")
    try:
        return settings_class()
    except ValidationError as exc:
        fields = sorted({str(error["loc"][0]) for error in exc.errors(include_input=False)})
        raise LlmError(f"llm_invalid_config:{provider}:{','.join(fields)}") from None

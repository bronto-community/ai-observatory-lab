"""Which LLM the agent talks to.

LLM_PROVIDER picks the vendor; MODEL_ID (or BEDROCK_MODEL_ID for Bedrock)
picks the model. Bedrock is the default and uses your AWS credentials; the
others need their own API key in the environment:

  LLM_PROVIDER  key needed          default model
  bedrock       AWS credentials     global.amazon.nova-2-lite-v1:0   (no access form)
  openai        OPENAI_API_KEY      gpt-5.4-mini
  anthropic     ANTHROPIC_API_KEY   claude-haiku-4-5-20251001
  gemini        GEMINI_API_KEY      gemini-3.8-flash

Whichever you pick, Strands emits the same GenAI spans, so the traces and
the dashboard work unchanged.
"""

import os

PROVIDER = os.environ.get("LLM_PROVIDER", "bedrock").strip().lower()
REGION = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-west-2"

DEFAULTS = {
    "bedrock": "global.amazon.nova-2-lite-v1:0",
    "openai": "gpt-5.4-mini",
    "anthropic": "claude-haiku-4-5-20251001",
    "gemini": "gemini-3.8-flash",
}
KEYS = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "gemini": "GEMINI_API_KEY"}

# OpenTelemetry gen_ai.provider.name values for the per-question log event.
PROVIDER_NAMES = {"bedrock": "aws.bedrock", "openai": "openai", "anthropic": "anthropic", "gemini": "gcp.gemini"}

if PROVIDER not in DEFAULTS:
    raise SystemExit(f"LLM_PROVIDER={PROVIDER!r}: use one of {', '.join(DEFAULTS)}")

MODEL_ID = (
    os.environ.get("MODEL_ID")
    or (os.environ.get("BEDROCK_MODEL_ID") if PROVIDER == "bedrock" else None)
    or DEFAULTS[PROVIDER]
)

# USD per million tokens (input, output), on-demand list prices. Only used for
# the "estimated cost" field: the GenAI conventions count tokens, not dollars.
PRICES = {
    "nova-2-lite": (0.33, 2.75),
    "nova-lite": (0.06, 0.24),
    "nova-pro": (0.80, 3.20),
    "nova-micro": (0.035, 0.14),
    "gpt-oss-120b": (0.15, 0.60),
    "gpt-oss-20b": (0.07, 0.30),
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-sonnet-4-5": (3.00, 15.00),
    "gemini-2.5-flash": (0.30, 2.50),
}


def api_key() -> str | None:
    """The vendor API key for the current provider (None for Bedrock)."""
    if PROVIDER == "bedrock":
        return None
    key = os.environ.get(KEYS[PROVIDER], "").strip()
    if not key:
        raise SystemExit(f"LLM_PROVIDER={PROVIDER} needs {KEYS[PROVIDER]} in .env")
    return key


def model(model_id: str | None = None, max_tokens: int = 1024):
    """A Strands model for the configured provider."""
    model_id = model_id or MODEL_ID
    if PROVIDER == "bedrock":
        from strands.models import BedrockModel
        return BedrockModel(model_id=model_id, region_name=REGION, max_tokens=max_tokens)
    if PROVIDER == "openai":
        from strands.models.openai import OpenAIModel
        return OpenAIModel(client_args={"api_key": api_key()}, model_id=model_id,
                           params={"max_completion_tokens": max_tokens})
    if PROVIDER == "anthropic":
        from strands.models.anthropic import AnthropicModel
        return AnthropicModel(client_args={"api_key": api_key()}, model_id=model_id, max_tokens=max_tokens)
    from strands.models.gemini import GeminiModel
    # Gemini counts its thinking against the output limit: leave room for both.
    return GeminiModel(client_args={"api_key": api_key()}, model_id=model_id,
                       params={"max_output_tokens": max_tokens * 4})


def estimated_cost(model_id: str, tokens_in: int, tokens_out: int) -> float | None:
    for key, (p_in, p_out) in PRICES.items():
        if key in model_id:
            return round((tokens_in * p_in + tokens_out * p_out) / 1_000_000, 6)
    return None  # no list price on file for this model

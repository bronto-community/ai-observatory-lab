"""Lets Severin's AI SRE agents run on OpenAI, Anthropic or Gemini, not only Bedrock.

Python imports this module at start-up. Each step's agent.py builds its model
with `BedrockModel(model_id=..., region_name=...)`. When LLM_PROVIDER names
another provider, that name returns the same provider's model as Track A
(see llm.py), so his agent code runs unchanged.
"""

import os

if os.environ.get("LLM_PROVIDER", "bedrock").strip().lower() != "bedrock":
    import strands.models

    def _model_for_provider(**_bedrock_args):
        from llm import model
        return model(max_tokens=4096)  # investigations write longer answers than Track A

    strands.models.BedrockModel = _model_for_provider

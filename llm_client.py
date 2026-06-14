"""
Foundry IQ LLM Client
=======================
Calls Azure AI Foundry / GitHub Models for live LLM reasoning.

Used by Agent 3 (Transparency) to synthesize the executive verdict
using a real model rather than templated strings.

Falls back gracefully to a templated response if no credentials
are available — demo mode remains fully functional offline.

Endpoint: GitHub Models (Azure AI Inference)
  - URL: https://models.inference.ai.azure.com
  - Model: gpt-4o-mini (free tier via GitHub PAT)
  - Auth: GITHUB_TOKEN environment variable (free at github.com/settings/tokens)
"""

import os
import json
from typing import Optional

# Try to load .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GITHUB_MODELS_ENDPOINT = "https://models.inference.ai.azure.com/chat/completions"
DEFAULT_MODEL = "gpt-4o-mini"


def is_llm_available() -> bool:
    """Check if a GitHub token is configured."""
    return bool(os.environ.get("GITHUB_TOKEN"))


def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 600,
    temperature: float = 0.4,
) -> Optional[str]:
    """
    Call GitHub Models / Azure AI Inference for a single completion.

    Returns the model's text response, or None if the call fails
    (in which case the caller should fall back to templated output).
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return None

    try:
        import urllib.request
        import urllib.error

        body = json.dumps({
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }).encode("utf-8")

        req = urllib.request.Request(
            GITHUB_MODELS_ENDPOINT,
            data=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "FoundrySentinel/1.0",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        # Silently fail to templated mode — demo never breaks
        print(f"[LLM] call failed, falling back to template: {type(e).__name__}: {e}")
        return None


def synthesize_executive_verdict(
    risk_level: str,
    risk_score: int,
    violations: list,
    principles_touched: list,
    counterfactuals: list,
) -> tuple[str, str]:
    """
    Synthesize the executive verdict using a real LLM (when available).

    Returns:
        (verdict_text, source) where source is 'foundry_iq_llm' or 'templated'
    """
    if not is_llm_available():
        return None, "templated"  # signals caller to use template

    # Build the prompt
    violation_summary = "\n".join([
        f"- {v['rule_id']} ({v['severity']}): {', '.join(p['name'] for p in v['principles_violated'])}"
        for v in violations[:5]
    ])

    principles_str = ", ".join(principles_touched) if principles_touched else "none"

    system_prompt = (
        "You are the Transparency Agent for Foundry Sentinel — a Responsible AI "
        "assurance system that audits enterprise AI agents for bias and ethical "
        "violations. Your role is to synthesise a clear, authoritative executive "
        "verdict for HR, L&D, and Compliance stakeholders. "
        "\n\n"
        "Be direct, plain-language, and decisive. No hedging. No jargon. "
        "Lead with the verdict, follow with the evidence count, end with the "
        "required action. Maximum 4 sentences. "
        "Match the tone to the risk level: CRITICAL = urgent and clear; "
        "HIGH = firm and remedial; MODERATE = cautionary; LOW = approving."
    )

    user_prompt = f"""Synthesise an executive verdict for this audit:

Risk Level: {risk_level}
Risk Score: {risk_score}/100
Violations detected: {len(violations)}
Ethical principles touched: {principles_str}

Top violations:
{violation_summary}

Counterfactual scenarios available: {len(counterfactuals)}

Write the executive verdict now. Start with an emoji that matches severity (🛑 for CRITICAL, ⚠️ for HIGH, 📋 for MODERATE, ✅ for LOW). Maximum 4 sentences."""

    response = call_llm(system_prompt, user_prompt, max_tokens=300)

    if response:
        return response, "foundry_iq_llm"
    return None, "templated"


if __name__ == "__main__":
    print(f"LLM available: {is_llm_available()}")
    if is_llm_available():
        # Smoke test
        result = call_llm(
            "You are helpful.",
            "Say 'Foundry IQ LLM client working' in exactly those words.",
            max_tokens=20,
        )
        print(f"Response: {result}")
    else:
        print("Set GITHUB_TOKEN environment variable to enable live LLM calls.")
        print("Get a free token at: https://github.com/settings/tokens")

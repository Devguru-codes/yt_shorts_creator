"""Local LLM backend — OpenAI or Gemini, selected by LLM_PROVIDER."""
import time
from ..config import (
    GEMINI_MODEL,
    LLM_PROVIDER,
    OPENAI_MODEL,
    require_gemini_key,
    require_openai_key,
    BACKUP_GEMINI_API_KEY,
)
import os


def call_openai_llm(prompt: str) -> str:
    """OpenAI Chat Completions backend used by --mode local."""
    try:
        from openai import OpenAI  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "openai is required for --mode local. Install it with:\n"
            "    pip install -r requirements-local.txt"
        ) from e

    client = OpenAI(api_key=require_openai_key())
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.7,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content or ""


def call_gemini_llm(prompt: str) -> str:
    """Gemini backend used by --mode local when LLM_PROVIDER=gemini."""
    try:
        from google import genai  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "google-genai is required for LLM_PROVIDER=gemini. Install it with:\n"
            "    pip install -r requirements-local.txt"
        ) from e

    current_key = require_gemini_key()
    client = genai.Client(api_key=current_key)
    for attempt in range(4):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config={
                    "temperature": 0.2,
                    "response_mime_type": "application/json",
                    "max_output_tokens": 8192,
                },
            )
            return response.text or ""
        except Exception as e:
            if "429" in str(e) or "503" in str(e):
                print(f"API busy ({'Rate Limit' if '429' in str(e) else 'High Demand'}). Sleeping 25s... (Attempt {attempt+1}/4)", flush=True)
                time.sleep(25)
                if BACKUP_GEMINI_API_KEY and current_key == require_gemini_key():
                    print("Switching to backup key for retry...", flush=True)
                    current_key = BACKUP_GEMINI_API_KEY
                else:
                    current_key = require_gemini_key()
                client = genai.Client(api_key=current_key)
            else:
                break
    
    print("Gemini exhausted/failed, failing over to Groq...", flush=True)
    return call_groq_llm(prompt)

def call_groq_llm(prompt: str) -> str:
    """Groq failover backend."""
    try:
        from groq import Groq
    except ImportError as e:
        raise RuntimeError("groq is required for failover. pip install groq") from e

    groq_keys = [
        os.getenv("GROQ_API_KEY"),
        os.getenv("GROQ_API_KEY_1"),
        os.getenv("GROQ_API_KEY_2"),
    ]
    groq_keys = [k for k in groq_keys if k]
    if not groq_keys:
        raise RuntimeError("GROQ_API_KEY environment variable is required for Groq failover")

    models_to_try = [
        os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-20b",
    ]

    for key in groq_keys:
        client = Groq(api_key=key)
        for model in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model,
                    temperature=0.2,
                    messages=[{"role": "user", "content": prompt}],
                )
                print(f"[highlights] Groq failover succeeded with model: {model}", flush=True)
                return response.choices[0].message.content or ""
            except Exception as e:
                print(f"[highlights] Groq attempt with {model} failed: {e}", flush=True)

    raise RuntimeError("All Groq failover attempts failed.")


def call_local_llm(prompt: str) -> str:
    """Dispatch to the configured local LLM provider."""
    provider = (LLM_PROVIDER or "openai").strip().lower()
    if provider == "openai":
        return call_openai_llm(prompt)
    if provider == "gemini":
        return call_gemini_llm(prompt)
    raise RuntimeError(
        f"Unknown LLM_PROVIDER={provider!r}. Use 'openai' or 'gemini'."
    )

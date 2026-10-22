

"""Free AI tips using Gemini (Google AI Studio free key).

Tries a list of Gemini models; if all fail, asks Google which models your key can
use and tries those. Shows the exact error for every model that failed."""
import os
import requests

BASE = "https://generativelanguage.googleapis.com/v1beta"
PREFERRED = ["gemini-flash-latest", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-lite-latest"]
SKIP = ("tts", "image", "live", "audio", "embedding", "robotics", "computer-use", "veo", "imagen")


def _headers(key):
    return {"x-goog-api-key": key, "Content-Type": "application/json"}


def available_models(key, timeout=30):
    """Models your key can use for text generation."""
    r = requests.get(f"{BASE}/models", headers=_headers(key), params={"pageSize": 200}, timeout=timeout)
    r.raise_for_status()
    names = []
    for m in r.json().get("models", []):
        if "generateContent" in m.get("supportedGenerationMethods", []):
            names.append(m["name"].split("/", 1)[1])
    return names


def _call(model, prompt, key, timeout):
    r = requests.post(
        f"{BASE}/models/{model}:generateContent",
        headers=_headers(key),
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=timeout,
    )
    if r.status_code != 200:
        raise RuntimeError(f"{model}: HTTP {r.status_code} {r.text[:200]}")
    return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


def ask_gemini(prompt, models=None, timeout=60):
    """Returns (model_name, text)."""
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY not set")
    errors, tried = [], []

    def attempt(model):
        tried.append(model)
        try:
            return model, _call(model, prompt, key, timeout)
        except Exception as e:
            errors.append(str(e))
            return None

    for m in models or PREFERRED:
        res = attempt(m)
        if res:
            return res
        if "API_KEY_INVALID" in errors[-1] or "HTTP 401" in errors[-1] or "HTTP 403" in errors[-1]:
            raise RuntimeError("Gemini key problem -> " + errors[-1])

    # Fallback: let Google tell us which models this key can use.
    try:
        avail = [m for m in available_models(key) if m not in tried and not any(s in m for s in SKIP)]
        flash = [m for m in avail if "flash" in m]
        gemma = [m for m in avail if "gemma" in m]
        for m in (flash + gemma)[:4]:
            res = attempt(m)
            if res:
                return res
    except Exception as e:
        errors.append(f"list models: {e}")
    raise RuntimeError("All Gemini models failed -> " + " | ".join(errors))


def ask(prompt):
    return ask_gemini(prompt)

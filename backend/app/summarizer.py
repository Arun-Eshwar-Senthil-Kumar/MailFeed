import os, re
import httpx

def _fallback(body: str) -> str:
    sents = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", body).strip())
    return " ".join(sents[:2])[:220]

def summarize(subject: str, body: str) -> str:
    key, base, model = (os.getenv(k) for k in ("LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL"))
    if not (key and base and model):
        return _fallback(body)
    try:
        r = httpx.post(
            base.rstrip("/") + "/chat/completions", timeout=20,
            headers={"Authorization": f"Bearer {key}"},
            json={"model": model, "max_tokens": 100, "messages": [
                {"role": "system", "content": "Summarize the email in at most 2 short sentences "
                 "(under 35 words). Lead with what the reader must do or know, include any deadline. No preamble."},
                {"role": "user", "content": f"Subject: {subject}\n\n{body[:3000]}"}]})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("LLM summary failed, using fallback:", e)
        return _fallback(body)

import os
import requests

def generate_product_assistance(message, product_context=""):
    """OpenAI-compatible chat completion adapter; returns a clear fallback if unconfigured."""
    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("LLM_MODEL", "").strip()
    if not api_key or not model:
        return {"enabled": False, "answer": "AI assistant is not configured yet. Add LLM_API_KEY and LLM_MODEL to your environment."}
    system = (
        "You are a shopping decision assistant. Use only the supplied product context for factual "
        "claims about availability, prices, and product specifications. If information is missing, say so. "
        "Compare trade-offs clearly; never claim an order was placed."
    )
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [
                {"role": "system", "content": system + "\nProduct context:\n" + (product_context[:12000] or "No product context supplied.")},
                {"role": "user", "content": message[:4000]},
            ], "temperature": 0.3},
            timeout=25,
        )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]
        return {"enabled": True, "answer": answer}
    except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
        return {"enabled": True, "answer": f"AI assistant temporarily unavailable ({exc.__class__.__name__})."}

import os
import requests

def search_external_products(query, limit=8):
    api_key = os.getenv("SERPAPI_API_KEY", "").strip()
    if not api_key or not query.strip():
        return {"enabled": bool(api_key), "results": [], "message": "SERP search is not configured or query is empty."}
    try:
        response = requests.get(
            "https://serpapi.com/search.json",
            params={"engine": "google_shopping", "q": query, "api_key": api_key, "num": min(max(limit, 1), 20)},
            timeout=12,
        )
        response.raise_for_status()
        data = response.json()
        results = []
        for item in data.get("shopping_results", [])[:limit]:
            results.append({
                "title": item.get("title", ""),
                "price": item.get("price", ""),
                "source": item.get("source", ""),
                "link": item.get("link", ""),
                "thumbnail": item.get("thumbnail", ""),
                "external": True,
            })
        return {"enabled": True, "results": results, "message": ""}
    except (requests.RequestException, ValueError) as exc:
        return {"enabled": True, "results": [], "message": f"External search temporarily unavailable: {exc.__class__.__name__}."}

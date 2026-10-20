"""Adapter for the project's existing trained recommendation model.

Set RECOMMENDER_MODEL_PATH to a trusted joblib artifact and adapt predict/ranking
logic to the exact model interface after the source notebook is reviewed.
"""
import os
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=1)
def load_model():
    model_path = os.getenv("RECOMMENDER_MODEL_PATH", "").strip()
    if not model_path:
        return None
    path = Path(model_path)
    if not path.is_file():
        return None
    import joblib
    return joblib.load(path)

def recommend_products(products, query="", limit=8):
    """Safe baseline until the original model and feature schema are connected."""
    model = load_model()
    items = list(products)
    if not items:
        return []
    # Do not guess model inputs. Use explainable text matching as a fallback.
    terms = [term.lower() for term in query.split() if len(term) > 1]
    def score(product):
        text = f"{product.name} {product.description} {product.category}".lower()
        return sum(term in text for term in terms)
    return sorted(items, key=lambda p: (score(p), p.stock > 0, p.created_at), reverse=True)[:limit]

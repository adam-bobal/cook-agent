"""Recipe search and ingredient extraction utilities."""
from __future__ import annotations

import re
from typing import List, Dict, Optional

SAMPLE_RECIPES = [
    {
        "title": "Simple Pancakes",
        "ingredients": ["flour", "milk", "egg", "baking powder", "salt", "butter"],
        "instructions": "Mix dry ingredients, add milk and egg, cook on skillet."
    },
    {
        "title": "Tomato Pasta",
        "ingredients": ["pasta", "tomato", "garlic", "olive oil", "basil", "salt"],
        "instructions": "Cook pasta, prepare sauce with tomato and garlic, toss together."
    },
    {
        "title": "Avocado Toast",
        "ingredients": ["bread", "avocado", "salt", "pepper", "lemon"],
        "instructions": "Toast bread, smash avocado, season, and serve."
    }
]


def search_recipes(query: str, top_n: int = 5) -> List[Dict]:
    """Return recipes from the sample dataset matching query by simple scoring."""
    q = query.lower()
    scored = []
    for r in SAMPLE_RECIPES:
        score = 0
        if q in r["title"].lower():
            score += 3
        if q in r["instructions"].lower():
            score += 2
        for ing in r["ingredients"]:
            if q in ing.lower():
                score += 1
        if score > 0:
            scored.append((score, r))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _s, r in scored][:top_n]


def extract_ingredients_from_text(text: str) -> List[str]:
    """Simple heuristic extractor for ingredient-like tokens in free-form text."""
    lines = re.split(r"\n|;|,", text)
    candidates = []
    for line in lines:
        line = line.strip()
        # common pattern: "- 2 eggs" or "2 cups flour"
        m = re.search(r"(?:\d+\s*[\w/.-]*)?\s*([A-Za-z][A-Za-z \-]+)$", line)
        if m:
            cand = m.group(1).strip()
            if len(cand) > 1 and len(cand.split()) <= 4:
                candidates.append(cand.lower())

    # fallback: look for known ingredients in the text
    known = set()
    for r in SAMPLE_RECIPES:
        for ing in r["ingredients"]:
            if re.search(rf"\b{re.escape(ing)}\b", text, re.I):
                known.add(ing)

    return sorted(set(candidates) | known)


def extract_ingredients(text: str, model_client=None) -> List[str]:
    """Attempt to use model client to extract ingredients; fall back to heuristic.

    If `model_client` is provided and configured, the function will send a prompt
    asking the model to return a JSON array of ingredients. Otherwise it uses
    `extract_ingredients_from_text`.
    """
    if model_client and getattr(model_client, "configured", lambda: False)():
        prompt = (
            "Extract the list of ingredients from the following text. "
            "Return a JSON array of ingredient names only.\n\nText:\n" + text
        )
        try:
            out = model_client.generate(prompt)
            # Try to pull brackets-delimited list
            m = re.search(r"\[.*\]", out, re.S)
            if m:
                import json

                try:
                    arr = json.loads(m.group(0))
                    if isinstance(arr, list):
                        return [str(x).lower() for x in arr]
                except Exception:
                    pass
            # otherwise, fallback to heuristics
        except Exception:
            pass

    return extract_ingredients_from_text(text)

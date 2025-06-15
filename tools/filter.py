import json
from pathlib import Path
from langchain.tools import tool
from tools.semantic_search import semantic_search

# Path to your local model metadata
MODEL_METADATA_PATH = Path(__file__).parent.parent / "data/model_metadata.json"

def load_models():
    with open(MODEL_METADATA_PATH, encoding="utf-8") as f:
        return json.load(f)

def fuzzy_in(needle, haystack_list):
    """Return True if needle (lowercased) appears as substring in any haystack item."""
    needle = needle.lower()
    return any(needle in str(item).lower() for item in haystack_list)


@tool
def filter_models(
    tag: str = "", 
    min_likes: int = 0, 
    task: str = "", 
    min_score: float = 0.0, 
    license: str = "", 
    provider: str = "", 
    merged_only: bool = False
) -> str:
    """
    Flexible filter for leaderboard models.
    Can filter by tag, min_likes, task/type, min average score, license, provider, and merged status.
    """
    models = load_models()
    matches = []
    for m in models:
        tags = m.get("tags", [])
        if tag and not fuzzy_in(tag, tags + [m.get("Type", "")]):
            continue
        if m.get("Hub ❤️", 0) < min_likes:
            continue
        if task and task.lower() not in str(m.get("Type", "")).lower():
            continue
        if min_score and (m.get("Average ⬆️") is None or float(m.get("Average ⬆️", 0)) < min_score):
            continue
        if license and license.lower() not in str(m.get("Hub License", "")).lower():
            continue
        if provider and provider.lower() not in str(m.get("Official Providers", "")).lower():
            continue
        if merged_only and not m.get("Merged", False):
            continue
        matches.append(m)
    
    if not matches:
        # Fallback: try semantic search using tag or task or free-form query
        query = tag or task or provider or license
        if not query:
            return "No models found with those filters."
        docs, metadatas = semantic_search(query, top_k=10)
        if metadatas:
            result = "Semantic Fallback Results:\n"
            for m in metadatas[:10]:
                result += (
                    f"- {m.get('model_id', m.get('fullname', ''))}: {m.get('model_card', '')[:80]}... "
                    f"(Score: {m.get('Average ⬆️','?')}, Likes: {m.get('Hub ❤️','?')})\n"
                )
            if len(metadatas) > 10:
                result += f"...and {len(metadatas) - 10} more."
            return result
        return "No models found with those filters, even with semantic search."

    # Limit output for readability
    result = "Filtered Models:\n"
    for m in matches[:10]:
        result += (
            f"- {m['model_id']}: {m.get('model_card', '')[:80]}... (Score: {m.get('Average ⬆️','?')}, Likes: {m.get('Hub ❤️', 0)})\n"
        )
    if len(matches) > 10:
        result += f"...and {len(matches) - 10} more."
    return result
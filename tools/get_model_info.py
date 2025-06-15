import requests
import json
from pathlib import Path
from langchain.tools import tool
from tools.semantic_search import semantic_search

MODEL_METADATA_PATH = Path(__file__).parent.parent / "data/model_metadata.json"


def load_models():
    with open(MODEL_METADATA_PATH, encoding="utf-8") as f:
        return json.load(f)

@tool
def get_model_info(model_id: str) -> str:
    """
    Return detailed info (from local leaderboard data) for a given model_id (fullname).
    Fallback to semantic search if no direct/substring match.
    """
    models = load_models()
    # Try exact match first
    info = next(
        (
            m
            for m in models
            if m.get("model_id") == model_id or m.get("fullname") == model_id
        ),
        None,
    )
    # Fallback: case-insensitive substring match
    if not info:
        model_id_lc = model_id.lower()
        info = next(
            (
                m
                for m in models
                if model_id_lc in str(m.get("model_id", "")).lower()
                or model_id_lc in str(m.get("fullname", "")).lower()
            ),
            None,
        )
    # Fallback: semantic search for a relevant model
    used_semantic = False
    if not info:
        docs, metadatas = semantic_search(model_id, top_k=3)
        info = None
        for meta in metadatas:
            # Only accept semantic match if user query appears in model_id or fullname (case-insensitive)
            if (
                model_id.lower() in str(meta.get("model_id", "")).lower()
                or model_id.lower() in str(meta.get("fullname", "")).lower()
            ):
                info = meta
                used_semantic = True
                break
    if not info:
        return f"No model found with id {model_id}."
    providers = info.get("Official Providers")
    if isinstance(providers, list):
        providers_str = ", ".join(providers)
    elif isinstance(providers, str):
        providers_str = providers
    else:
        providers_str = ""
    fields = [
        ("Model", info.get("model_id", "")),
        ("Description", info.get("description", "")),
        ("Summary", info.get("summary", "")),
        ("Provider(s)", providers_str if info.get("Official Providers") else "N/A"),
        ("Average Score", info.get("Average ⬆️", "N/A")),
        (
            "Benchmarks",
            f"BBH: {info.get('BBH')}, IFEval: {info.get('IFEval')}, MATH Lvl 5: {info.get('MATH Lvl 5')}, GPQA: {info.get('GPQA')}, MMLU-PRO: {info.get('MMLU-PRO')}",
        ),
        ("License", info.get("Hub License", "N/A")),
        ("Likes", info.get("Hub ❤️", "N/A")),
        ("#Params (B)", info.get("#Params (B)", "N/A")),
        ("Architecture", info.get("Architecture", "N/A")),
        ("Type", info.get("Type", "N/A")),
        ("Base Model", info.get("Base Model", "N/A")),
        ("Merged", info.get("Merged", "N/A")),
        ("Upload Date", info.get("Upload To Hub Date", "N/A")),
        ("Submission Date", info.get("Submission Date", "N/A")),
        ("Tags", ", ".join(info.get("tags", [])) if info.get("tags") else "N/A"),
    ]
    summary = "\n".join([f"{k}: {v}" for k, v in fields if v and v != "N/A"])
    if used_semantic:
        summary = f"(No exact match found. Showing closest model by semantic search.)\n{summary}"
    return summary

import json
import os
import hashlib
from pathlib import Path
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
from langchain.tools import tool

# Path configs
MODEL_METADATA_PATH = Path(__file__).parent.parent / "data/model_metadata.json"
CHROMA_DIR = Path(__file__).parent.parent / "data/chroma_db"
HASH_PATH = CHROMA_DIR / "model_metadata_hash.txt"

# Ensure the chroma directory exists
os.makedirs(CHROMA_DIR, exist_ok=True)


# Load all model metadata
def load_models():
    with open(MODEL_METADATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def model_to_index_text(m):
    providers = m.get("Official Providers")
    if isinstance(providers, list):
        providers_str = ", ".join(providers)
    elif isinstance(providers, str):
        providers_str = providers
    else:
        providers_str = ""
    return (
        f"{m.get('fullname', '')}. {m.get('Model', '')}. "
        f"{m.get('description', '') or ''} "
        f"{m.get('summary', '') or ''}"
        f"Tags: {', '.join(m.get('tags', []))}. "
        f"Providers: {providers_str}. "
        f"Benchmarks: BBH {m.get('BBH')}, IFEval {m.get('IFEval')}, "
        f"Math {m.get('MATH Lvl 5')}, GPQA {m.get('GPQA')}, MMLU-PRO {m.get('MMLU-PRO')}, "
        f"Average Score {m.get('Average ⬆️')}. "
        f"License: {m.get('Hub License', '')}. Likes: {m.get('Hub ❤️', '')}. "
        f"Params: {m.get('#Params (B)', '')}. Type: {m.get('Type', '')}. "
        f"Architecture: {m.get('Architecture', '')}. Base Model: {m.get('Base Model', '')}"
    )


# Utility: Get hash of the metadata file for cache busting
def get_file_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# Persistent Chroma client
chroma_client = PersistentClient(path=str(CHROMA_DIR))
collection = chroma_client.get_or_create_collection("hf_models")

# Load model metadata
with open(MODEL_METADATA_PATH, encoding="utf-8") as f:
    model_docs = json.load(f)

# Compute hash to check if embeddings need update
current_hash = get_file_hash(MODEL_METADATA_PATH)
stored_hash = ""
if HASH_PATH.exists():
    with open(HASH_PATH) as f:
        stored_hash = f.read().strip()

if current_hash != stored_hash:
    print(
        "🔄 Model metadata changed or no cache found. Rebuilding ChromaDB collection..."
    )
    # Clear and repopulate collection
    all_ids = collection.get()["ids"]
    if all_ids:
        print(f"Deleting {len(all_ids)} previous documents from ChromaDB...")
        collection.delete(ids=all_ids)  # Delete all previous docs
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    models = load_models()
    texts = [model_to_index_text(m) for m in models]

    for idx, (doc, text) in enumerate(zip(models, texts)):
        embedding = embedder.encode(text)
        fixed_doc = {}
        for k, v in doc.items():
            if isinstance(v, list):
                # Convert list to comma-separated string
                fixed_doc[k] = ", ".join(str(i) for i in v)
            elif isinstance(v, dict):
                # Convert dict to JSON string
                import json

                fixed_doc[k] = json.dumps(v)
            else:
                fixed_doc[k] = v

        collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[fixed_doc],
            ids=[str(idx)],
        )
    with open(HASH_PATH, "w") as f:
        f.write(current_hash)
    print("✅ ChromaDB collection rebuilt successfully.")
else:
    print("✅ Using cached ChromaDB collection. No need to rebuild.")


def semantic_search(query, top_k=3):
    embedder = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )  # Safe to re-instantiate for query
    q_emb = embedder.encode(query)
    results = collection.query(
        query_embeddings=[q_emb],
        n_results=top_k,
    )
    return results["documents"][0], results["metadatas"][0]


@tool
def semantic_model_search(query: str, top_k: int = 3) -> str:
    """
    Finds leaderboard models relevant to a free-text query using semantic search.
    Returns summaries of top results.
    """
    docs, metadatas = semantic_search(query, top_k)
    if not metadatas:
        return "No relevant models found."
    result = "Top Semantic Matches:\n"
    for meta in metadatas:
        desc = meta.get("description", "") or meta.get("summary", "")
        score = meta.get("Average ⬆️", "?")
        provider = meta.get("Official Providers", "N/A")
        if isinstance(provider, list):
            provider = ", ".join(provider)
        result += (
            f"Model: {meta.get('model_id', meta.get('fullname', ''))}\n"
            f"Provider(s): {provider}\n"
            f"Type: {meta.get('Type', '')}, Params: {meta.get('#Params (B)', '')}B\n"
            f"Average Score: {score}\n"
            f"License: {meta.get('Hub License', '')}\n"
            f"Description: {desc[:200]}...\n"
            "-----\n"
        )
    return result

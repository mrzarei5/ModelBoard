import os
import json
import time

from datasets import load_dataset
from huggingface_hub import HfApi
from tqdm import tqdm
import requests
from pathlib import Path
from dotenv import dotenv_values


def fetch_readme(model_id, max_retries=10, api_key=None):
    url = f"https://huggingface.co/{model_id}/raw/main/README.md"
    retries = 0
    backoff = 2
    while retries < max_retries:
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else None
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return r.text
        elif r.status_code == 429:
            wait = backoff**retries
            print(f"Rate limited fetching {model_id}. Sleeping for {wait} seconds.")
            time.sleep(wait)
            retries += 1
        else:
            break
    return ""


config = dotenv_values(Path(__file__).parent.parent / ".env")

api_key = config.get("HF_API_KEY", None)

print("Loading leaderboard data...")
leaderboard = load_dataset("open-llm-leaderboard/contents", split="train")
models = [entry for entry in leaderboard if entry.get("Available on the hub") is True]

print(f"Total models on leaderboard and available on hub: {len(models)}")

# --- Add extra fields of interest here ---
fields_to_save = [
    "fullname",
    "Model",
    "Average ⬆️",
    "Hub License",
    "Hub ❤️",
    "#Params (B)",
    "Architecture",
    "Type",
    "BBH",
    "IFEval",
    "MATH Lvl 5",
    "GPQA",
    "MMLU-PRO",
    "Merged",
    "Official Providers",
    "Upload To Hub Date",
    "Submission Date",
    "Generation",
    "Base Model",
]

api = HfApi()
db = []
for entry in tqdm(models, desc="Fetching model info"):
    model_id = entry["fullname"]
    record = {k: entry.get(k, None) for k in fields_to_save}
    record["model_id"] = model_id
    record["readme"] = fetch_readme(model_id, api_key=api_key)
    try:
        info = api.model_info(model_id)
        record["description"] = (
            info.cardData.get("description", "") if info.cardData else ""
        )
        record["summary"] = info.cardData.get("summary", "") if info.cardData else ""
        record["tags"] = info.tags
        record["pipeline_tag"] = info.pipeline_tag if info.pipeline_tag else ""
    except Exception as e:
        record["description"] = ""
        record["summary"] = ""
        record["tags"] = []
        record["pipeline_tag"] = ""
    db.append(record)

with open(Path(__file__).parent / "model_metadata.json", "w") as f:
    json.dump(db, f, indent=2)

print(f"\nSaved {len(db)} leaderboard models to leaderboard_models.json")

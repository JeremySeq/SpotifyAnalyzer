import os
import json
import uuid

ANALYSIS_DIR = "./data/analyses"
os.makedirs(ANALYSIS_DIR, exist_ok=True)


def _generate_analysis_id() -> str:
    return uuid.uuid4().hex[:8]


def _get_analysis_path(analysis_id: str) -> str:
    return os.path.join(ANALYSIS_DIR, f"{analysis_id}.json")


def save_analysis_result(result: dict) -> str:
    analysis_id = _generate_analysis_id()
    path = _get_analysis_path(analysis_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f)
    return analysis_id

def load_analysis_result(analysis_id: str) -> dict | None:
    path = _get_analysis_path(analysis_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

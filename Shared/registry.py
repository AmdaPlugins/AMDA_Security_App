import json
from pathlib import Path
import streamlit as st

def load_registry(path: Path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_registry(path: Path, registry: list):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

def get_site_by_prefix(registry: list, prefix: str):
    return next((s for s in registry if s["prefix"] == prefix), None)

def get_prefixes(registry: list):
    return [s["prefix"] for s in registry]

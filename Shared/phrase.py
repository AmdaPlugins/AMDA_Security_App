import json
from pathlib import Path
import streamlit as st

def filter_phrases_by_site(phrases: list, site_info: dict):
    return [
        p for p in phrases
        if p.get("site") == site_info["site"]
        and p.get("name") == site_info["name"]
        and p.get("address") == site_info["address"]
    ]

def get_categories(phrases: list):
    return sorted(set(p["cat"] for p in phrases if p.get("cat")))

def get_hotwords(phrases: list):
    hot = set()
    for p in phrases:
        for word in p.get("hotwords", []):
            if len(word) > 2:
                hot.add(word.lower())
    return sorted(hot)

def save_phrase(path: Path, phrases: list, new_phrase: dict):
    phrases.append(new_phrase)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(phrases, f, indent=2, ensure_ascii=False)

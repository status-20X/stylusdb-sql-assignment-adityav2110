from __future__ import annotations

import re
from html import unescape
from typing import Iterable, List, Sequence

SKILL_DICTIONARY = {
    "python",
    "java",
    "javascript",
    "typescript",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "react",
    "node",
    "django",
    "flask",
    "fastapi",
    "machine learning",
    "nlp",
    "deep learning",
    "git",
    "linux",
    "spark",
    "hadoop",
    "llm",
    "ollama",
}


def clean_text(text: str) -> str:
    text = unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^a-zA-Z0-9+.#\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def extract_skills(text: str, skill_dictionary: Iterable[str] = SKILL_DICTIONARY) -> List[str]:
    normalized = clean_text(text)
    found = []
    for skill in sorted(skill_dictionary):
        escaped = re.escape(skill)
        if re.search(rf"\b{escaped}\b", normalized):
            found.append(skill)
    return found


def unique_preserve_order(values: Sequence[str]) -> List[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result

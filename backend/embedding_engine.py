from __future__ import annotations

from hashlib import sha256
from typing import List


class EmbeddingEngine:
    """Generates embeddings with sentence-transformers, falling back to deterministic vectors."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is not None:
            return self._model
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        except Exception:
            self._model = False
        return self._model

    def _fallback_embedding(self, text: str, dimensions: int = 128) -> List[float]:
        digest = sha256((text or "").encode("utf-8")).digest()
        repeated = (digest * ((dimensions // len(digest)) + 1))[:dimensions]
        return [byte / 255 for byte in repeated]

    def generate_resume_embedding(self, text: str) -> List[float]:
        return self._generate_embedding(text)

    def generate_job_embedding(self, text: str) -> List[float]:
        return self._generate_embedding(text)

    def _generate_embedding(self, text: str) -> List[float]:
        model = self._load_model()
        if model and model is not False:
            vector = model.encode(text or "", normalize_embeddings=True)
            return vector.tolist()
        return self._fallback_embedding(text)

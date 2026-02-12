from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from .embedding_engine import EmbeddingEngine
from .models import ResumeObject
from .utils import clean_text, extract_skills


class ResumeParser:
    def __init__(self, embedding_engine: Optional[EmbeddingEngine] = None):
        self.embedding_engine = embedding_engine or EmbeddingEngine()

    def parse_resume(self, file_path: str) -> ResumeObject:
        raw_text = self._extract_raw_text(file_path)
        normalized_text = clean_text(raw_text)
        skills = extract_skills(normalized_text)
        experience_years = self.extract_experience_years(normalized_text)
        embeddings = self.embedding_engine.generate_resume_embedding(normalized_text)
        return ResumeObject(
            raw_text=raw_text,
            skills=skills,
            experience_years=experience_years,
            embeddings=embeddings,
        )

    def _extract_raw_text(self, file_path: str) -> str:
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            return self._extract_pdf_text(path)
        if suffix == ".docx":
            return self._extract_docx_text(path)
        return path.read_text(encoding="utf-8", errors="ignore")

    def _extract_pdf_text(self, path: Path) -> str:
        try:
            import PyPDF2

            text = []
            with path.open("rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text.append(page.extract_text() or "")
            return "\n".join(text)
        except Exception:
            return ""

    def _extract_docx_text(self, path: Path) -> str:
        try:
            import docx

            document = docx.Document(str(path))
            return "\n".join(p.text for p in document.paragraphs)
        except Exception:
            return ""

    def extract_experience_years(self, text: str) -> float:
        patterns = [
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
            r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        ]

        values = []
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                try:
                    values.append(float(match.group(1)))
                except ValueError:
                    continue

        return max(values) if values else 0.0

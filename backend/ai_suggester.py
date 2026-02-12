from __future__ import annotations

from typing import Any, Dict

import requests


class AISuggester:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3") -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def suggest(self, resume_text: str, job_description: str) -> str:
        prompt = self._build_prompt(resume_text, job_description)
        try:
            payload: Dict[str, Any] = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            }
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=45,
            )
            response.raise_for_status()
            body = response.json()
            return body.get("response", "No suggestions returned.")
        except Exception as exc:
            return f"AI suggestion unavailable: {exc}"

    def _build_prompt(self, resume_text: str, job_description: str) -> str:
        return f"""You are a resume optimization expert.

Here is the resume:
{resume_text}

Here is the job description:
{job_description}

Tasks:
1. Identify missing skills.
2. Suggest resume bullet improvements.
3. Suggest quantification improvements.
4. Suggest keywords to include.

Keep it structured and concise.
"""

from __future__ import annotations

import re
from typing import List, Tuple

from .models import JobObject, RawJobObject
from .utils import clean_text, extract_skills


class JobNormalizer:
    def normalize_jobs(self, raw_jobs: List[RawJobObject]) -> List[JobObject]:
        jobs: List[JobObject] = []
        for raw in raw_jobs:
            if not raw.job_description:
                continue
            description = clean_text(raw.job_description)
            experience_years = self.parse_experience_range(raw.experience_required_text)
            jobs.append(
                JobObject(
                    company=raw.company,
                    role=raw.role,
                    job_description=description,
                    experience_required_text=raw.experience_required_text,
                    experience_required_years=experience_years,
                    apply_link=raw.apply_link,
                    skills=extract_skills(description),
                )
            )
        return jobs

    def parse_experience_range(self, experience_text: str) -> Tuple[float, float]:
        text = (experience_text or "").lower()
        range_match = re.search(r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)", text)
        if range_match:
            return (float(range_match.group(1)), float(range_match.group(2)))

        min_match = re.search(r"(?:minimum|min|at least)\s*(\d+(?:\.\d+)?)", text)
        if min_match:
            return (float(min_match.group(1)), 100.0)

        single_year_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)", text)
        if single_year_match:
            value = float(single_year_match.group(1))
            return (value, value)

        return (0.0, 100.0)

from __future__ import annotations

import math
from typing import List

from .models import JobObject, ResumeObject
from .scoring_engine import ScoringEngine
from .utils import unique_preserve_order


class MatcherEngine:
    def __init__(self, scoring_engine: ScoringEngine | None = None) -> None:
        self.scoring_engine = scoring_engine or ScoringEngine()

    def match_jobs(self, resume: ResumeObject, jobs: List[JobObject]) -> List[JobObject]:
        for job in jobs:
            semantic_score = self.cosine_similarity(resume.embeddings or [], job.embeddings or [])
            skill_overlap = self.skill_overlap_score(resume.skills, job.skills)
            experience = self.scoring_engine.experience_score(
                resume.experience_years,
                job.experience_required_years,
            )
            job.match_score = self.scoring_engine.final_score(semantic_score, skill_overlap, experience)
        return sorted(jobs, key=lambda x: x.match_score, reverse=True)

    def cosine_similarity(self, first: List[float], second: List[float]) -> float:
        if not first or not second:
            return 0.0

        max_len = max(len(first), len(second))
        padded_a = (first + [0.0] * max_len)[:max_len]
        padded_b = (second + [0.0] * max_len)[:max_len]

        dot_product = sum(a * b for a, b in zip(padded_a, padded_b))
        norm_a = math.sqrt(sum(a * a for a in padded_a))
        norm_b = math.sqrt(sum(b * b for b in padded_b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        similarity = dot_product / (norm_a * norm_b)
        return max(0.0, min(1.0, similarity))

    def skill_overlap_score(self, resume_skills: List[str], job_skills: List[str]) -> float:
        dedup_resume = set(unique_preserve_order(resume_skills))
        dedup_job = set(unique_preserve_order(job_skills))
        if not dedup_job:
            return 0.0
        overlap = dedup_resume.intersection(dedup_job)
        return len(overlap) / len(dedup_job)

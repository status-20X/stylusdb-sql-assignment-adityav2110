from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ScoreConfig:
    semantic_weight: float = 0.6
    skill_weight: float = 0.25
    experience_weight: float = 0.15


class ScoringEngine:
    def __init__(self, config: ScoreConfig | None = None) -> None:
        self.config = config or ScoreConfig()

    def experience_score(self, candidate_experience: float, required_range: tuple[float, float]) -> float:
        min_years, max_years = required_range
        return 1.0 if min_years <= candidate_experience <= max_years else 0.0

    def final_score(self, semantic_score: float, skill_overlap_score: float, experience_score: float) -> float:
        score = (
            (self.config.semantic_weight * semantic_score)
            + (self.config.skill_weight * skill_overlap_score)
            + (self.config.experience_weight * experience_score)
        )
        return self.normalize_score(score)

    def normalize_score(self, score: float) -> float:
        score = max(0.0, min(1.0, score))
        return round(score * 100, 2)

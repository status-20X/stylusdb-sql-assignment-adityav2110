from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ResumeObject:
    raw_text: str
    skills: List[str]
    experience_years: float
    education: List[str] = field(default_factory=list)
    projects: List[str] = field(default_factory=list)
    embeddings: Optional[List[float]] = None


@dataclass
class RawJobObject:
    company: str
    role: str
    job_description: str
    experience_required_text: str
    apply_link: str
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class JobObject:
    company: str
    role: str
    job_description: str
    experience_required_text: str
    experience_required_years: Tuple[float, float]
    apply_link: str
    skills: List[str] = field(default_factory=list)
    embeddings: Optional[List[float]] = None
    match_score: float = 0.0

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from .ai_suggester import AISuggester
from .crawler_engine import CrawlerEngine
from .embedding_engine import EmbeddingEngine
from .job_normalizer import JobNormalizer
from .matcher_engine import MatcherEngine
from .models import JobObject, ResumeObject
from .resume_parser import ResumeParser


class MainController:
    def __init__(self) -> None:
        self.embedding_engine = EmbeddingEngine()
        self.resume_parser = ResumeParser(embedding_engine=self.embedding_engine)
        self.crawler_engine = CrawlerEngine()
        self.job_normalizer = JobNormalizer()
        self.matcher_engine = MatcherEngine()
        self.ai_suggester = AISuggester()

    def parse_resume(self, resume_file_path: str) -> ResumeObject:
        return self.resume_parser.parse_resume(resume_file_path)

    def load_excel(self, excel_file_path: str) -> List[Dict[str, str]]:
        df = pd.read_excel(excel_file_path)
        expected = {"Company", "Career URL"}
        if not expected.issubset(df.columns):
            raise ValueError("Excel must include 'Company' and 'Career URL' columns")
        return [
            {"company": row["Company"], "url": row["Career URL"]}
            for _, row in df.iterrows()
            if row["Company"] and row["Career URL"]
        ]

    def filter_selected_companies(
        self,
        companies: List[Dict[str, str]],
        selected_company_names: List[str],
    ) -> List[Dict[str, str]]:
        selected = set(selected_company_names)
        return [company for company in companies if company["company"] in selected]

    def run_matching_pipeline(
        self,
        resume_file_path: str,
        excel_file_path: str,
        selected_company_names: List[str],
        top_n: int = 10,
    ) -> List[JobObject]:
        resume = self.parse_resume(resume_file_path)
        all_companies = self.load_excel(excel_file_path)
        selected_companies = self.filter_selected_companies(all_companies, selected_company_names)
        raw_jobs = self.crawler_engine.crawl_selected_sites(selected_companies)

        normalized_jobs = self.job_normalizer.normalize_jobs(raw_jobs)
        for job in normalized_jobs:
            job.embeddings = self.embedding_engine.generate_job_embedding(job.job_description)

        ranked_jobs = self.matcher_engine.match_jobs(resume, normalized_jobs)
        return ranked_jobs[:top_n]

    def discuss_with_ai(self, resume_text: str, selected_job_description: str) -> str:
        return self.ai_suggester.suggest(resume_text, selected_job_description)

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from .models import RawJobObject


class CrawlerEngine:
    def __init__(self, timeout_seconds: int = 12, max_workers: int = 8) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_workers = max_workers

    def crawl_selected_sites(self, selected_companies: List[Dict[str, str]]) -> List[RawJobObject]:
        jobs: List[RawJobObject] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_map = {
                executor.submit(self._crawl_single_company, company): company
                for company in selected_companies
            }
            for future in as_completed(future_map):
                try:
                    jobs.extend(future.result())
                except Exception:
                    continue
        return jobs

    def _crawl_single_company(self, company: Dict[str, str]) -> List[RawJobObject]:
        company_name = company.get("company", "Unknown")
        url = company.get("url", "")
        if not url:
            return []

        html = self._fetch_html(url)
        if not html:
            html = self._fetch_with_playwright(url)
        if not html:
            return []

        return self._extract_jobs_from_html(company_name, html, url)

    def _fetch_html(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=self.timeout_seconds)
            if response.ok:
                return response.text
        except Exception:
            return ""
        return ""

    def _fetch_with_playwright(self, url: str) -> str:
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=self.timeout_seconds * 1000)
                page.wait_for_timeout(1200)
                content = page.content()
                browser.close()
                return content
        except Exception:
            return ""

    def _extract_jobs_from_html(self, company: str, html: str, source_url: str) -> List[RawJobObject]:
        soup = BeautifulSoup(html, "html.parser")

        job_containers = soup.select("article, .job, .job-card, li, .posting")
        if not job_containers:
            job_containers = [soup]

        jobs: List[RawJobObject] = []
        for container in job_containers:
            role = self._find_role(container)
            description = self._find_description(container)
            experience_text = self._find_experience_text(container)
            apply_link = self._find_apply_link(container, source_url)

            if not role or not description:
                continue

            jobs.append(
                RawJobObject(
                    company=company,
                    role=role,
                    job_description=description,
                    experience_required_text=experience_text,
                    apply_link=apply_link,
                )
            )

        return jobs

    def _find_role(self, container) -> str:
        heading = container.find(["h1", "h2", "h3", "h4"])
        return heading.get_text(" ", strip=True) if heading else ""

    def _find_description(self, container) -> str:
        paragraphs = container.find_all(["p", "div", "span"])
        text = " ".join(node.get_text(" ", strip=True) for node in paragraphs)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _find_experience_text(self, container) -> str:
        raw_text = container.get_text(" ", strip=True)
        match = re.search(r"(\d+\s*[-–]\s*\d+\s*(?:years?|yrs?))", raw_text, re.IGNORECASE)
        if match:
            return match.group(1)
        match = re.search(r"(minimum\s*\d+\s*(?:years?|yrs?))", raw_text, re.IGNORECASE)
        return match.group(1) if match else ""

    def _find_apply_link(self, container, fallback: str) -> str:
        anchor = container.find("a", href=True)
        return anchor["href"] if anchor else fallback

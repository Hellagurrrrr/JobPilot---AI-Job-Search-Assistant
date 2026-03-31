# loaders/job_page_loader.py

from __future__ import annotations

from loaders.safe_fetcher import SafeFetcher
from loaders.playwright_fetcher import PlaywrightFetcher


class JobPageLoader:
    def __init__(self) -> None:
        self.safe_fetcher = SafeFetcher(timeout=12, max_retries=2, min_text_length=300)
        self.playwright_fetcher = PlaywrightFetcher(
            timeout_ms=15000,
            wait_after_load_ms=2500,
            min_text_length=300,
            headless=True,
        )

    def load(self, url: str) -> str:
        # 先试静态抓取
        safe_result = self.safe_fetcher.fetch(url)
        print("\n[SafeFetcher]")
        print(safe_result.short_debug())

        if safe_result.text:
            print("\n[SafeFetcher 文本预览]")
            print(safe_result.text[:500])

        if safe_result.success:
            return safe_result.text

        # 再试 Playwright
        pw_result = self.playwright_fetcher.fetch(url)
        print("\n[PlaywrightFetcher]")
        print(pw_result.short_debug())

        if pw_result.text:
            print("\n[PlaywrightFetcher 文本预览]")
            print(pw_result.text[:500])

        if pw_result.success:
            return pw_result.text

        raise ValueError(
            "网页抓取失败：静态抓取和 Playwright 抓取都未拿到可靠的 JD 正文。"
        )
# loaders/safe_fetcher.py

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass, field
from typing import Optional

import requests
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": (
        os.getenv(
            "USER_AGENT",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        )
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


BLOCK_PATTERNS = [
    r"请完成验证",
    r"安全验证",
    r"异常访问",
    r"访问受限",
    r"请先登录",
    r"登录后查看",
    r"滑动验证",
    r"验证码",
    r"robot",
    r"access denied",
    r"forbidden",
]

JD_HINT_PATTERNS = [
    r"岗位职责",
    r"职位描述",
    r"任职要求",
    r"岗位要求",
    r"职位要求",
    r"加分项",
    r"我们希望你",
    r"responsibilities",
    r"requirements",
    r"qualifications",
]


@dataclass
class FetchResult:
    url: str
    success: bool
    status_code: Optional[int] = None
    final_url: Optional[str] = None
    method: str = "requests"
    raw_html: str = ""
    text: str = ""
    error: Optional[str] = None
    warnings: list[str] = field(default_factory=list)
    blocked: bool = False
    looks_like_jd: bool = False

    def short_debug(self) -> str:
        return (
            f"FetchResult(success={self.success}, status_code={self.status_code}, "
            f"blocked={self.blocked}, looks_like_jd={self.looks_like_jd}, "
            f"warnings={self.warnings}, error={self.error})"
        )


class SafeFetcher:
    def __init__(
        self,
        timeout: int = 12,
        max_retries: int = 2,
        min_text_length: int = 300,
        sleep_seconds: float = 1.0,
    ) -> None:
        self.timeout = timeout
        self.max_retries = max_retries
        self.min_text_length = min_text_length
        self.sleep_seconds = sleep_seconds

    def fetch(self, url: str) -> FetchResult:
        """
        安全抓取入口。
        只做基础 requests + HTML 提取，不做绕过风控的行为。
        """
        result = FetchResult(url=url, success=False)

        if not self._is_valid_url(url):
            result.error = "无效 URL"
            return result

        last_error: Optional[str] = None

        for attempt in range(1, self.max_retries + 2):
            try:
                response = requests.get(
                    url,
                    headers=DEFAULT_HEADERS,
                    timeout=self.timeout,
                    allow_redirects=True,
                )

                result.status_code = response.status_code
                result.final_url = str(response.url)
                result.raw_html = response.text

                if response.status_code >= 400:
                    result.error = f"HTTP {response.status_code}"
                    if attempt <= self.max_retries:
                        time.sleep(self.sleep_seconds)
                        continue
                    return self._finalize_result(result)

                result.text = self._extract_text(response.text)
                return self._finalize_result(result)

            except requests.RequestException as e:
                last_error = str(e)
                result.error = f"请求失败: {e}"
                if attempt <= self.max_retries:
                    time.sleep(self.sleep_seconds)
                    continue

        if last_error:
            result.error = last_error
        return self._finalize_result(result)

    def _finalize_result(self, result: FetchResult) -> FetchResult:
        text = result.text or ""

        if not text.strip():
            result.warnings.append("提取到的文本为空")

        if len(text.strip()) < self.min_text_length:
            result.warnings.append(
                f"文本较短（{len(text.strip())} chars），可能不是有效正文"
            )

        if self._contains_block_signal(text):
            result.blocked = True
            result.warnings.append("疑似登录/验证/风控页面")

        result.looks_like_jd = self._looks_like_jd(text)
        if not result.looks_like_jd:
            result.warnings.append("页面内容看起来不像标准 JD")

        result.success = (
            result.error is None
            and not result.blocked
            and len(text.strip()) >= self.min_text_length
        )

        return result

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        return url.startswith("http://") or url.startswith("https://")

    @staticmethod
    def _extract_text(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")

        # 去掉明显噪声
        for tag in soup(["script", "style", "noscript", "svg", "footer", "nav"]):
            tag.decompose()

        # 优先尝试正文区域
        candidates = []

        for selector in [
            "main",
            "article",
            '[role="main"]',
            ".job-detail",
            ".job-sec",
            ".job-box",
            ".job-primary",
            ".position-content",
            ".content",
        ]:
            found = soup.select(selector)
            for node in found:
                txt = node.get_text(separator="\n", strip=True)
                if txt:
                    candidates.append(txt)

        if candidates:
            best = max(candidates, key=len)
            return SafeFetcher._clean_text(best)

        # 回退到整页文本
        full_text = soup.get_text(separator="\n", strip=True)
        return SafeFetcher._clean_text(full_text)

    @staticmethod
    def _clean_text(text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        return text.strip()

    @staticmethod
    def _contains_block_signal(text: str) -> bool:
        low = text.lower()
        for pattern in BLOCK_PATTERNS:
            if re.search(pattern, low, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def _looks_like_jd(text: str) -> bool:
        hits = 0
        for pattern in JD_HINT_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                hits += 1
        return hits >= 1
# loaders/playwright_fetcher.py

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


DEFAULT_USER_AGENT = os.getenv(
    "USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/136.0.0.0 Safari/537.36",
)

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
class PlaywrightFetchResult:
    url: str
    success: bool
    final_url: Optional[str] = None
    method: str = "playwright"
    title: str = ""
    text: str = ""
    raw_html: str = ""
    screenshot_path: Optional[str] = None
    error: Optional[str] = None
    warnings: list[str] = field(default_factory=list)
    blocked: bool = False
    looks_like_jd: bool = False

    def short_debug(self) -> str:
        return (
            f"PlaywrightFetchResult(success={self.success}, "
            f"blocked={self.blocked}, looks_like_jd={self.looks_like_jd}, "
            f"title={self.title!r}, screenshot_path={self.screenshot_path!r}, "
            f"warnings={self.warnings}, error={self.error})"
        )


class PlaywrightFetcher:
    def __init__(
        self,
        timeout_ms: int = 15000,
        wait_after_load_ms: int = 2500,
        min_text_length: int = 300,
        headless: bool = True,
        screenshot_dir: str = "artifacts/screenshots",
    ) -> None:
        self.timeout_ms = timeout_ms
        self.wait_after_load_ms = wait_after_load_ms
        self.min_text_length = min_text_length
        self.headless = headless
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def fetch(self, url: str) -> PlaywrightFetchResult:
        result = PlaywrightFetchResult(url=url, success=False)

        if not self._is_valid_url(url):
            result.error = "无效 URL"
            return result

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(
                    user_agent=DEFAULT_USER_AGENT,
                    locale="zh-CN",
                    viewport={"width": 1440, "height": 1600},
                )
                page = context.new_page()

                try:
                    # page.goto 默认会等待 load 事件
                    page.goto(url, timeout=self.timeout_ms, wait_until="load")
                except PlaywrightTimeoutError:
                    result.warnings.append("page.goto 超时，继续尝试提取当前页面内容")
                except Exception as e:
                    result.error = f"页面访问失败: {e}"
                    browser.close()
                    return result

                # 再给动态页面一点渲染时间
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=5000)
                except Exception:
                    pass

                page.wait_for_timeout(self.wait_after_load_ms)

                result.final_url = page.url
                result.title = page.title()

                # 保存截图，便于调试
                screenshot_path = self.screenshot_dir / self._build_screenshot_name(result.final_url or url)
                try:
                    page.screenshot(path=str(screenshot_path), full_page=True)
                    result.screenshot_path = str(screenshot_path)
                except Exception as e:
                    result.warnings.append(f"截图失败: {e}")

                # 先取 html，再取文本
                try:
                    result.raw_html = page.content()
                except Exception as e:
                    result.warnings.append(f"获取 HTML 失败: {e}")

                result.text = self._extract_text_from_page(page)

                browser.close()

        except Exception as e:
            result.error = f"Playwright 启动或执行失败: {e}"
            return self._finalize_result(result)

        return self._finalize_result(result)

    def _finalize_result(self, result: PlaywrightFetchResult) -> PlaywrightFetchResult:
        text = (result.text or "").strip()

        if not text:
            result.warnings.append("提取到的文本为空")

        if len(text) < self.min_text_length:
            result.warnings.append(f"文本较短（{len(text)} chars），可能不是有效正文")

        if self._contains_block_signal(text) or self._contains_block_signal(result.title):
            result.blocked = True
            result.warnings.append("疑似登录/验证/风控页面")

        result.looks_like_jd = self._looks_like_jd(text)
        if not result.looks_like_jd:
            result.warnings.append("页面内容看起来不像标准 JD")

        result.success = (
            result.error is None
            and not result.blocked
            and len(text) >= self.min_text_length
        )
        return result

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        return url.startswith("http://") or url.startswith("https://")

    @staticmethod
    def _build_screenshot_name(url: str) -> str:
        safe = re.sub(r"[^a-zA-Z0-9]+", "_", url)[:80].strip("_")
        return f"{safe or 'page'}.png"

    @staticmethod
    def _clean_text(text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        return text.strip()

    def _extract_text_from_page(self, page) -> str:
        # 优先常见正文区域
        selectors = [
            "main",
            "article",
            '[role="main"]',
            ".job-detail",
            ".job-sec",
            ".job-box",
            ".job-primary",
            ".position-content",
            ".job-card-body",
            ".content",
        ]

        candidates: list[str] = []

        for selector in selectors:
            try:
                locator = page.locator(selector)
                count = locator.count()
                for i in range(min(count, 5)):
                    txt = locator.nth(i).inner_text(timeout=2000).strip()
                    if txt:
                        candidates.append(txt)
            except Exception:
                continue

        if candidates:
            best = max(candidates, key=len)
            return self._clean_text(best)

        # 回退：直接取 body 可见文本
        try:
            body_text = page.locator("body").inner_text(timeout=3000)
            return self._clean_text(body_text)
        except Exception:
            return ""

    @staticmethod
    def _contains_block_signal(text: str) -> bool:
        low = (text or "").lower()
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
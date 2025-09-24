"""Core search utilities for the Doniyor privacy-focused search engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, List, Optional
import html
import re

from duckduckgo_search import DDGS


_SAFE_SEARCH_MAP = {
    True: "moderate",
    False: "off",
}


@dataclass(slots=True)
class SearchResult:
    """A single search result item."""

    title: str
    url: str
    snippet: str

    @classmethod
    def from_ddg(cls, item: dict) -> "SearchResult":
        """Create a :class:`SearchResult` from a duckduckgo-search result."""

        title = html.unescape(item.get("title") or "")
        href = item.get("href") or ""
        body = html.unescape(item.get("body") or "")
        return cls(title=title.strip(), url=href.strip(), snippet=_clean_snippet(body))


@dataclass(slots=True)
class SearchQuery:
    """Normalized representation of a user search query."""

    text: str
    region: str
    max_results: int
    safe_search: bool


def _clean_snippet(snippet: str) -> str:
    snippet = re.sub(r"\s+", " ", snippet).strip()
    return snippet


class DoniyorSearchEngine:
    """A privacy-first wrapper around DuckDuckGo search."""

    def __init__(
        self,
        *,
        default_region: str = "us-en",
        default_max_results: int = 10,
        safe_search: bool = True,
    ) -> None:
        self._default_region = default_region
        self._default_max_results = max(1, default_max_results)
        self._default_safe_search = safe_search

    def build_query(
        self,
        text: str,
        *,
        region: Optional[str] = None,
        max_results: Optional[int] = None,
        safe_search: Optional[bool] = None,
    ) -> SearchQuery:
        if not text or not text.strip():
            raise ValueError("Query text must be non-empty")

        normalized = " ".join(text.split())
        return SearchQuery(
            text=normalized,
            region=region or self._default_region,
            max_results=max(1, max_results or self._default_max_results),
            safe_search=self._default_safe_search if safe_search is None else safe_search,
        )

    def search(
        self,
        text: str,
        *,
        region: Optional[str] = None,
        max_results: Optional[int] = None,
        safe_search: Optional[bool] = None,
    ) -> List[SearchResult]:
        query = self.build_query(text, region=region, max_results=max_results, safe_search=safe_search)
        return list(self._execute(query))

    def _execute(self, query: SearchQuery) -> Iterator[SearchResult]:
        ddg_safe_mode = _SAFE_SEARCH_MAP[bool(query.safe_search)]
        with DDGS() as ddgs:
            generator = ddgs.text(
                query=query.text,
                region=query.region,
                safesearch=ddg_safe_mode,
                max_results=query.max_results,
            )
            seen_urls: set[str] = set()
            for item in generator:
                if not isinstance(item, dict):
                    continue
                result = SearchResult.from_ddg(item)
                if not result.url or result.url in seen_urls:
                    continue
                seen_urls.add(result.url)
                yield result

    def search_iter(
        self,
        text: str,
        *,
        region: Optional[str] = None,
        max_results: Optional[int] = None,
        safe_search: Optional[bool] = None,
    ) -> Iterable[SearchResult]:
        query = self.build_query(text, region=region, max_results=max_results, safe_search=safe_search)
        return self._execute(query)

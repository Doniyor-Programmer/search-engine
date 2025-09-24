from __future__ import annotations

from typing import Iterable
from types import SimpleNamespace

import pytest

from doniyor.search import DoniyorSearchEngine, SearchResult


def fake_ddg_results(items: Iterable[dict]):
    class _FakeDDGS:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def text(self, *_, **__):
            return iter(items)

    return _FakeDDGS()


def test_build_query_normalizes_whitespace():
    engine = DoniyorSearchEngine()
    query = engine.build_query("  privacy   search  ")
    assert query.text == "privacy search"


def test_search_filters_duplicates(monkeypatch):
    results = [
        {"title": "Result 1", "href": "https://example.com/a", "body": " A summary "},
        {"title": "Result 2", "href": "https://example.com/a", "body": "Duplicate URL"},
        {"title": "Result 3", "href": "https://example.com/b", "body": "More info"},
    ]

    engine = DoniyorSearchEngine()

    monkeypatch.setattr("doniyor.search.DDGS", lambda: fake_ddg_results(results))

    search_results = engine.search("privacy")
    assert len(search_results) == 2
    assert all(isinstance(item, SearchResult) for item in search_results)

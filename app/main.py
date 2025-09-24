"""FastAPI application exposing the Doniyor search engine."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from doniyor import DoniyorSearchEngine

app = FastAPI(
    title="Doniyor",
    description=(
        "Doniyor is a privacy-first metasearch experience built on top of DuckDuckGo. "
        "No personal data is stored or logged."
    ),
    version="1.0.0",
)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

engine = DoniyorSearchEngine()


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request, q: str | None = Query(default=None, alias="q")):
    error: str | None = None
    results = []
    query_text = (q or "").strip()

    if query_text:
        try:
            results = engine.search(query_text)
        except ValueError as exc:
            error = str(exc)
        except Exception:
            error = "We could not retrieve private results at this time. Please try again later."

    context = {
        "request": request,
        "query": query_text,
        "results": results,
        "error": error,
        "title": "Doniyor — Private Search",
    }
    return templates.TemplateResponse("index.html", context)


@app.get("/api/search")
async def api_search(
    query: str = Query(..., min_length=1, description="Search phrase"),
    region: str | None = Query(None, description="Region code such as 'us-en'"),
    max_results: int | None = Query(None, ge=1, le=50, description="Maximum results to fetch"),
    safe_search: bool | None = Query(
        None,
        description="Enable strict filtering of adult content (defaults to true)",
    ),
):
    try:
        results = engine.search(query, region=region, max_results=max_results, safe_search=safe_search)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - fallback error handling
        raise HTTPException(status_code=502, detail="Failed to fetch privacy-preserving results") from exc

    return {
        "query": query,
        "count": len(results),
        "results": [result.__dict__ for result in results],
    }

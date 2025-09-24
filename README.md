# Doniyor — Privacy Focused Search Engine

Doniyor is a custom, privacy-first metasearch engine that proxies your query through our
backend before retrieving results from DuckDuckGo. The application never stores logs or
tracking data and exposes both a clean web interface and a JSON API.

## Features

- 🔒 **Privacy-first** – incoming requests are normalized in-memory without persisting logs.
- 🌐 **Region aware** – choose DuckDuckGo region codes like `us-en`, `uk-en`, etc.
- 🛡️ **Safe search control** – opt-in or out of adult content filtering.
- ⚙️ **Developer friendly API** – query results as JSON from `/api/search`.
- 🎨 **Modern UI** – responsive interface with zero external trackers or fonts.

## Getting Started

Install the dependencies and run the FastAPI server using Uvicorn:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 in your browser to use Doniyor.

### Environment Variables

No secrets are required. Doniyor uses DuckDuckGo's public search endpoint and keeps all
requests anonymous.

### API Usage

```
GET /api/search?query=privacy%20tools&max_results=5&region=uk-en
```

Example response:

```json
{
  "query": "privacy tools",
  "count": 5,
  "results": [
    {"title": "...", "url": "https://example.com", "snippet": "..."}
  ]
}
```

### Testing

Run the unit test suite with:

```bash
pytest
```

## License

MIT

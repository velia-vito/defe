# Python frontend

A standalone, TMDB-free local search page that streams results from the project's Python scraper integrations. It lives in its own folder and does not need Node.js.

## Run

From the project root, install the existing API requirements if needed and start the frontend:

```powershell
.venv\Scripts\pip install -r api\requirements.txt
.venv\Scripts\python py-front\app.py
```

Then open <http://127.0.0.1:8080>.

If you do not already have a virtual environment, create one first:

```powershell
python -m venv .venv
.venv\Scripts\pip install -r api\requirements.txt
```

Search results stream while scraper sources are checked. Language, audio, resolution, source, codec, HDR, and recognized size labels are parsed heuristically from each release title, URL, and scraper tags. Use the filters and sort selector to refine results. No TMDB credentials, Node.js, or separate API process are required.

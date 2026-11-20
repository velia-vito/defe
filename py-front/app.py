"""Python-based frontend server (no TMDB or Node.js required)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from api.main import Body, SCRAPERS, stream_events
from parser import enrich_link

app = FastAPI(title="DEFE Python Frontend")


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    return HTMLResponse((HERE / "index.html").read_text(encoding="utf-8"))


@app.get("/api/health")
async def health() -> dict:
    return {"ok": True, "scrapers": len(SCRAPERS)}


async def _enriched_stream(body: Body, request: Request) -> AsyncIterator[bytes]:
    buf = ""
    async for chunk in stream_events(body, request):
        buf += chunk.decode("utf-8", errors="replace")
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("t") == "hit" and isinstance(ev.get("links"), list):
                ev["links"] = [enrich_link(item) for item in ev["links"]]
            yield (json.dumps(ev) + "\n").encode("utf-8")
    if buf.strip():
        try:
            ev = json.loads(buf.strip())
            if ev.get("t") == "hit" and isinstance(ev.get("links"), list):
                ev["links"] = [enrich_link(item) for item in ev["links"]]
            yield (json.dumps(ev) + "\n").encode("utf-8")
        except json.JSONDecodeError:
            pass


@app.post("/api/search")
async def search(request: Request, body: Body) -> StreamingResponse:
    return StreamingResponse(
        _enriched_stream(body, request),
        media_type="application/x-ndjson; charset=utf-8",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)

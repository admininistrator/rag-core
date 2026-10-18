"""Local metadata UI shell. Only the cookie-protected API supplies operational data."""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates

ROOT = Path(__file__).parent
TEMPLATES = Jinja2Templates(directory=ROOT / "templates")
PAGES = {
    "overview": ("Overview", "Local operations at a glance"),
    "documents": ("Documents", "Registered versions and readiness"),
    "jobs": ("Jobs", "Ingestion progress and recovery"),
    "sessions": ("Sessions", "Active links and retained session metadata"),
    "index": ("Index / models", "Published generations and configured revisions"),
    "evaluations": ("Evaluations", "Quality reports and run provenance"),
}
HEADERS = {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; "
    "connect-src 'self'; img-src 'self'; base-uri 'none'; form-action 'self'; "
    "frame-ancestors 'none'",
}


def build_admin_views() -> APIRouter:
    router = APIRouter(include_in_schema=False)

    @router.get("/admin/assets/{name}")
    async def asset(name: str) -> Response:
        # Fixed allowlist, no filesystem path from the client.
        types = {"admin.css": "text/css", "admin.js": "text/javascript"}
        if name not in types:
            return Response(status_code=404, headers=HEADERS)
        return Response(
            (ROOT / "static" / name).read_bytes(), media_type=types[name], headers=HEADERS
        )

    @router.get("/admin", response_class=HTMLResponse)
    @router.get("/admin/{page}", response_class=HTMLResponse)
    async def view(request: Request, page: str = "overview") -> Response:
        if page not in PAGES:
            return Response(status_code=404, headers=HEADERS)
        title, subtitle = PAGES[page]
        return TEMPLATES.TemplateResponse(
            request=request,
            name="admin.html",
            context={"page": page, "title": title, "subtitle": subtitle, "pages": PAGES},
            headers=HEADERS,
        )

    return router

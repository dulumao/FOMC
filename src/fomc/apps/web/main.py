from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fomc.config import load_env
from .backend import (
    PortalError,
    export_cpi_pdf,
    export_macro_pdf,
    export_labor_pdf,
    list_macro_months,
    refresh_macro_month,
    get_macro_month,
    fetch_indicator_data,
    generate_cpi_report,
    generate_labor_report,
    list_indicator_tree,
)

load_env()

APP_DIR = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(APP_DIR / "templates"))

app = FastAPI(title="FOMC Portal", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")


def _default_month() -> str:
    return datetime.utcnow().strftime("%Y-%m")


@app.get("/", response_class=HTMLResponse)
def landing(request: Request) -> HTMLResponse:
    return TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "default_month": _default_month(),
        },
    )


@app.get("/toolbox", response_class=HTMLResponse)
def toolbox_page(request: Request) -> HTMLResponse:
    return TEMPLATES.TemplateResponse(
        "toolbox.html",
        {"request": request, "default_month": _default_month()},
    )


@app.get("/reports")
def redirect_reports():
    return RedirectResponse(url="/toolbox", status_code=307)


@app.get("/macro-events")
def redirect_macro_events():
    return RedirectResponse(url="/toolbox", status_code=307)


@app.get("/api/reports/labor")
def api_labor_report(month: str = Query(..., regex=r"^\d{4}-\d{2}$")):
    try:
        return generate_labor_report(month)
    except PortalError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/reports/cpi")
def api_cpi_report(month: str = Query(..., regex=r"^\d{4}-\d{2}$")):
    try:
        return generate_cpi_report(month)
    except PortalError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/macro-events")
def api_macro_events(
    month: str = Query(..., regex=r"^\d{4}-\d{2}$"),
    refresh: bool = False,
):
    try:
        return get_macro_month(month, refresh=refresh)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/macro-events/months")
def api_macro_months(order: str = Query("desc")):
    try:
        return list_macro_months(order=order)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/macro-events/refresh")
def api_macro_refresh(month: str = Query(..., regex=r"^\d{4}-\d{2}$")):
    try:
        return refresh_macro_month(month)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/macro-events/pdf")
def api_macro_pdf(
    month: str = Query(..., regex=r"^\d{4}-\d{2}$"),
    refresh: bool = False,
):
    try:
        pdf_bytes, headers = export_macro_pdf(month, refresh=refresh)
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": headers.get("Content-Disposition", f'attachment; filename="macro_{month}.pdf"')},
        )
    except PortalError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/reports/labor.pdf")
def api_labor_pdf(month: str = Query(..., regex=r"^\d{4}-\d{2}$")):
    try:
        pdf_bytes, headers = export_labor_pdf(month)
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": headers.get("Content-Disposition", f'attachment; filename="labor_{month}.pdf"')
            },
        )
    except PortalError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/reports/cpi.pdf")
def api_cpi_pdf(month: str = Query(..., regex=r"^\d{4}-\d{2}$")):
    try:
        pdf_bytes, headers = export_cpi_pdf(month)
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": headers.get("Content-Disposition", f'attachment; filename="cpi_{month}.pdf"')
            },
        )
    except PortalError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/indicators")
def api_indicators():
    try:
        return list_indicator_tree()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/indicator-data")
def api_indicator_data(
    indicator_id: int = Query(..., ge=1),
    date_range: str = Query("3Y"),
):
    try:
        return fetch_indicator_data(indicator_id, date_range=date_range)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("fomc.apps.web.main:app", host="0.0.0.0", port=9000, reload=True)

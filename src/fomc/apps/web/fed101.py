from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import difflib
import html
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import markdown2

from fomc.config.paths import REPO_ROOT
from fomc.data.database.connection import SessionLocal
from fomc.data.database.models import EconomicDataPoint, EconomicIndicator
from fomc.data.meetings.calendar_service import ensure_fomc_calendar
from fomc.apps.web.backend import (
    DEFAULT_HISTORY_CUTOFF,
    DEFAULT_MEETING_RANGE_END,
    DEFAULT_MEETING_RANGE_START,
    PortalError,
    get_meeting_context,
    get_meeting_decision_cached,
    generate_cpi_report,
    generate_labor_report,
)
from fomc.data.modeling.taylor_service import build_taylor_series_from_db
from fomc.rules.taylor_rule import ModelType


CONTENT_DIR = REPO_ROOT / "content" / "fed101"


@dataclass(frozen=True)
class Fed101ChapterMeta:
    slug: str
    title: str
    order: int = 1000
    summary: str | None = None
    flow_step: str | None = None
    try_meeting: str | None = None
    hidden: bool = False
    filename: str | None = None
    depth: int = 0

    def as_dict(self) -> dict:
        return {
            "slug": self.slug,
            "title": self.title,
            "order": self.order,
            "summary": self.summary,
            "flow_step": self.flow_step,
            "try_meeting": self.try_meeting,
            "hidden": self.hidden,
            "filename": self.filename,
            "depth": self.depth,
        }


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    stripped = text.lstrip("\ufeff")
    if not stripped.startswith("---\n"):
        return {}, text

    end = stripped.find("\n---\n", 4)
    if end < 0:
        return {}, text

    header = stripped[4:end].strip("\n")
    body = stripped[end + 5 :]

    meta: dict[str, Any] = {}
    for raw in header.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        if not val:
            meta[key] = ""
            continue
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            if not inner:
                meta[key] = []
            else:
                meta[key] = [x.strip().strip("'\"") for x in inner.split(",")]
            continue
        meta[key] = val.strip("'\"")

    return meta, body


_CELL_BLOCK_RE = re.compile(r"```fomc-cell\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE)


def _extract_cells(md_body: str) -> tuple[str, list[dict[str, Any]]]:
    cells: list[dict[str, Any]] = []

    def _replace(match: re.Match[str]) -> str:
        raw = (match.group(1) or "").strip()
        try:
            cell = json.loads(raw)
        except Exception as exc:
            cell = {"type": "error", "params": {"message": f"Invalid cell JSON: {exc}", "raw": raw}}

        if not isinstance(cell, dict):
            cell = {"type": "error", "params": {"message": "Cell JSON must be an object", "raw": raw}}

        if "id" not in cell:
            cell["id"] = f"cell-{len(cells) + 1}"

        if "type" not in cell:
            cell["type"] = "error"
            cell["params"] = {"message": "Missing cell.type"}

        cells.append(cell)
        payload = html.escape(json.dumps(cell, ensure_ascii=False), quote=True)
        return f"<div class=\"f101-cell\" data-cell=\"{payload}\"></div>"

    rendered = _CELL_BLOCK_RE.sub(_replace, md_body)
    return rendered, cells


def _strip_leading_h1(md_body: str) -> str:
    """
    Fed101 pages already render an explicit page title in the template.
    To avoid duplicate huge titles, strip the first H1 if it's the first non-empty line.
    """
    lines = (md_body or "").replace("\r", "").split("\n")
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and re.match(r"^\s*#\s+\S+", lines[i] or ""):
        i += 1
        if i < len(lines) and not lines[i].strip():
            i += 1
        return "\n".join(lines[i:]).lstrip("\n")
    return md_body


def _discover_chapter_files() -> list[Path]:
    if not CONTENT_DIR.exists():
        return []
    # Support nested chapters, e.g. content/fed101/data/nfp.md
    return sorted([p for p in CONTENT_DIR.rglob("*.md") if p.is_file()])


def _parse_bool(val: object | None) -> bool:
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    s = str(val).strip().lower()
    return s in {"1", "true", "yes", "y", "on"}


def list_fed101_chapters(*, include_hidden: bool = False) -> list[Fed101ChapterMeta]:
    chapters: list[Fed101ChapterMeta] = []
    for path in _discover_chapter_files():
        text = path.read_text(encoding="utf-8")
        meta, _body = _parse_frontmatter(text)
        default_slug = str(path.relative_to(CONTENT_DIR)).replace("\\", "/")
        default_slug = default_slug[:-3] if default_slug.lower().endswith(".md") else default_slug
        slug = str(meta.get("slug") or default_slug).strip()
        title = str(meta.get("title") or slug).strip()
        order = int(meta.get("order") or 1000)
        hidden = _parse_bool(meta.get("hidden"))
        chapters.append(
            Fed101ChapterMeta(
                slug=slug,
                title=title,
                order=order,
                summary=(str(meta.get("summary")).strip() if meta.get("summary") is not None else None),
                flow_step=(str(meta.get("flow_step")).strip() if meta.get("flow_step") is not None else None),
                try_meeting=(str(meta.get("try_meeting")).strip() if meta.get("try_meeting") is not None else None),
                hidden=hidden,
                filename=str(path.relative_to(REPO_ROOT)),
                depth=slug.count("/"),
            )
        )
    if not include_hidden:
        chapters = [c for c in chapters if not c.hidden]
    return sorted(chapters, key=lambda c: (c.order, c.slug))


def get_fed101_chapter(slug: str) -> tuple[Fed101ChapterMeta, str, list[dict[str, Any]]]:
    slug = (slug or "").strip()
    if not slug:
        raise PortalError("Missing chapter slug")

    target = None
    for path in _discover_chapter_files():
        text = path.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(text)
        default_slug = str(path.relative_to(CONTENT_DIR)).replace("\\", "/")
        default_slug = default_slug[:-3] if default_slug.lower().endswith(".md") else default_slug
        file_slug = str(meta.get("slug") or default_slug).strip()
        if file_slug == slug:
            target = (path, meta, body)
            break

    if not target:
        raise PortalError(f"Chapter not found: {slug}")

    path, meta, body = target
    title = str(meta.get("title") or slug).strip()
    order = int(meta.get("order") or 1000)
    chapter_meta = Fed101ChapterMeta(
        slug=slug,
        title=title,
        order=order,
        summary=(str(meta.get("summary")).strip() if meta.get("summary") is not None else None),
        flow_step=(str(meta.get("flow_step")).strip() if meta.get("flow_step") is not None else None),
        try_meeting=(str(meta.get("try_meeting")).strip() if meta.get("try_meeting") is not None else None),
        hidden=_parse_bool(meta.get("hidden")),
        filename=str(path.relative_to(REPO_ROOT)),
        depth=slug.count("/"),
    )

    body_with_cells, cells = _extract_cells(body)
    body_with_cells = _strip_leading_h1(body_with_cells)
    html_body = markdown2.markdown(
        body_with_cells,
        extras=["autolink", "break-on-newline", "fenced-code-blocks", "cuddled-lists", "code-friendly"],
    )
    return chapter_meta, html_body, cells


def _compute_time_window(date_range: str, *, end_date: datetime | None = None) -> tuple[datetime | None, datetime | None]:
    if not date_range or date_range == "all":
        return None, end_date
    end = end_date or datetime.utcnow()
    dr = date_range.strip().upper()
    if dr == "1Y":
        start = end - timedelta(days=365)
    elif dr == "3Y":
        start = end - timedelta(days=365 * 3)
    elif dr == "5Y":
        start = end - timedelta(days=365 * 5)
    elif dr == "10Y":
        start = end - timedelta(days=365 * 10)
    else:
        start = end - timedelta(days=365 * 3)
    return start, end


def _resolve_meeting_month(meeting_id: str | None) -> str | None:
    if not meeting_id:
        return None
    try:
        ctx = get_meeting_context(meeting_id, history_cutoff=DEFAULT_HISTORY_CUTOFF)
    except Exception:
        return None
    months = ctx.get("report_months") or []
    if not months:
        return None
    return str(months[-1])


def _slice_series_by_years(points: list[dict[str, Any]], years: int) -> list[dict[str, Any]]:
    if not points:
        return points
    try:
        end = datetime.fromisoformat(str(points[-1].get("date") or "")[:10])
    except Exception:
        return points
    start = end - timedelta(days=365 * years)
    out: list[dict[str, Any]] = []
    for p in points:
        try:
            d = datetime.fromisoformat(str(p.get("date") or "")[:10])
        except Exception:
            continue
        if d >= start:
            out.append(p)
    return out


def _fetch_indicator_series_by_code(
    *,
    code: str,
    date_range: str = "5Y",
    end_date_iso: str | None = None,
) -> dict:
    code = (code or "").strip()
    if not code:
        raise PortalError("Missing indicator code")

    end_dt = None
    if end_date_iso:
        try:
            end_dt = datetime.fromisoformat(end_date_iso[:10])
        except Exception:
            end_dt = None

    start_dt, end_dt = _compute_time_window(date_range, end_date=end_dt)

    session = SessionLocal()
    try:
        indicator = (
            session.query(EconomicIndicator)
            .filter(EconomicIndicator.code == code)
            .limit(1)
            .one_or_none()
        )
        if not indicator:
            raise PortalError(f"Indicator not found in DB: {code} (run init/sync first)")

        query = (
            session.query(EconomicDataPoint.date, EconomicDataPoint.value)
            .filter(EconomicDataPoint.indicator_id == indicator.id)
            .order_by(EconomicDataPoint.date.asc())
        )
        if start_dt:
            query = query.filter(EconomicDataPoint.date >= start_dt)
        if end_dt:
            query = query.filter(EconomicDataPoint.date <= end_dt)

        rows = query.all()
        dates: list[str] = []
        values: list[float | None] = []
        for dt, val in rows:
            try:
                dates.append(dt.strftime("%Y-%m-%d"))
            except Exception:
                dates.append(str(dt)[:10])
            values.append(val)

        return {
            "code": indicator.code,
            "name": indicator.name,
            "units": indicator.units,
            "dates": dates,
            "values": values,
        }
    finally:
        session.close()


def _unified_diff(a: str | None, b: str | None, *, a_label: str, b_label: str) -> str:
    a_lines = (a or "").splitlines(keepends=False)
    b_lines = (b or "").splitlines(keepends=False)
    diff = difflib.unified_diff(a_lines, b_lines, fromfile=a_label, tofile=b_label, lineterm="")
    return "\n".join(diff)


def _extract_md_headings(md: str | None) -> list[str]:
    if not md:
        return []
    out: list[str] = []
    for line in (md or "").splitlines():
        m = re.match(r"^\s*#{1,6}\s+(.*)$", line.strip())
        if m:
            out.append(m.group(1).strip())
    return out


def _keyword_score(text: str | None, keywords: dict[str, list[str]]) -> dict[str, int]:
    s = (text or "").lower()
    counts: dict[str, int] = {}
    for k, words in keywords.items():
        counts[k] = sum(s.count(w.lower()) for w in words)
    return counts


def _top_terms(md: str | None, *, k: int = 10) -> list[dict[str, Any]]:
    if not md:
        return []
    text = re.sub(r"[`*_>#\\[\\]().,:;\"'!?/\\\\]", " ", md)
    tokens = [t.strip().lower() for t in text.split() if len(t.strip()) >= 4]
    stop = {
        "this",
        "that",
        "with",
        "from",
        "will",
        "have",
        "been",
        "were",
        "their",
        "they",
        "into",
        "over",
        "more",
        "than",
        "also",
        "which",
        "should",
        "would",
        "about",
        "after",
        "before",
        "while",
        "where",
        "when",
        "policy",
        "meeting",
    }
    tokens = [t for t in tokens if t not in stop]
    c = Counter(tokens)
    return [{"term": term, "count": int(cnt)} for term, cnt in c.most_common(k)]


def _resolve_meeting_end_date(meeting_id: str) -> str | None:
    meeting_id = (meeting_id or "").strip()
    if not meeting_id:
        return None
    meetings = ensure_fomc_calendar(start=DEFAULT_MEETING_RANGE_START, end=DEFAULT_MEETING_RANGE_END, force_refresh=False)
    for m in meetings:
        if m.meeting_id == meeting_id:
            return m.end_date.isoformat()
    return None


def run_fed101_cell(cell_type: str, params: dict | None, context: dict | None) -> dict:
    cell_type = (cell_type or "").strip().lower()
    params = params or {}
    context = context or {}

    meeting_id = str(context.get("meeting_id") or "").strip() or None
    meeting_end = _resolve_meeting_end_date(meeting_id) if meeting_id else None
    meeting_month = _resolve_meeting_month(meeting_id) if meeting_id else None

    if cell_type == "indicator_chart":
        codes = params.get("codes") or []
        if isinstance(codes, str):
            codes = [codes]
        date_range = str(params.get("date_range") or "5Y")
        use_meeting_end = bool(params.get("use_meeting_end")) and bool(meeting_end)
        end_date_iso = meeting_end if use_meeting_end else None
        series = [_fetch_indicator_series_by_code(code=str(c), date_range=date_range, end_date_iso=end_date_iso) for c in codes]
        return {
            "kind": "indicator_series",
            "series": series,
            "context": {"meeting_id": meeting_id, "meeting_end": meeting_end, "date_range": date_range},
        }

    if cell_type == "taylor_model":
        model = params.get("model") or "taylor"
        try:
            model_enum = ModelType(model)
        except Exception:
            model_enum = ModelType.TAYLOR

        payload = dict(params)
        payload.pop("model", None)
        start_date = payload.get("start_date")
        end_date = payload.get("end_date")
        if params.get("use_meeting_end") and meeting_end:
            end_date = meeting_end
        if params.get("use_meeting_end") and meeting_end and not start_date:
            try:
                d = datetime.fromisoformat(meeting_end[:10])
                start_date = (d - timedelta(days=365)).date().isoformat()
            except Exception:
                start_date = None

        session = SessionLocal()
        try:
            return build_taylor_series_from_db(
                session=session,
                model=model_enum,
                start_date=start_date,
                end_date=end_date,
                real_rate=payload.get("real_rate"),
                target_inflation=payload.get("target_inflation"),
                alpha=payload.get("alpha"),
                beta=payload.get("beta"),
                okun=payload.get("okun"),
                intercept=payload.get("intercept"),
                rho=payload.get("rho"),
                inflation_code=payload.get("inflation_code") or "PCEPILFE",
                unemployment_code=payload.get("unemployment_code") or "UNRATE",
                nairu_code=payload.get("nairu_code") or "NROU",
                fed_effective_code=payload.get("fed_effective_code") or "EFFR",
            )
        finally:
            session.close()

    if cell_type == "labor_figure":
        figure = str(params.get("figure") or "fig1").strip().lower()
        month = str(params.get("month") or "").strip() or None
        use_meeting_month = bool(params.get("use_meeting_month"))
        if not month and use_meeting_month:
            month = meeting_month
        if not month:
            return {"kind": "note", "message": "缺少 month：请在 cell 参数中指定 month=YYYY-MM，或先选择示例会议并开启 use_meeting_month。"}

        payload = generate_labor_report(month)

        return {
            "kind": "labor_figure",
            "figure": figure,
            "month": month,
            "headline_summary": payload.get("headline_summary"),
            "chart_commentary": payload.get("chart_commentary"),
            "data": {
                "payems_series": list(payload.get("payems_series") or []),
                "unemployment_series": list(payload.get("unemployment_series") or []),
                "unemployment_types_series": payload.get("unemployment_types_series"),
                "employment_participation_series": list(payload.get("employment_participation_series") or []),
                "industry_contribution": payload.get("industry_contribution"),
            },
        }

    if cell_type == "cpi_figure":
        figure = str(params.get("figure") or "yoy").strip().lower()
        month = str(params.get("month") or "").strip() or None
        use_meeting_month = bool(params.get("use_meeting_month"))
        if not month and use_meeting_month:
            month = meeting_month
        if not month:
            return {"kind": "note", "message": "缺少 month：请在 cell 参数中指定 month=YYYY-MM，或先选择示例会议并开启 use_meeting_month。"}

        payload = generate_cpi_report(month)

        return {
            "kind": "cpi_figure",
            "figure": figure,
            "month": month,
            "headline_summary": payload.get("headline_summary"),
            "chart_commentary": payload.get("chart_window"),
            "weight_year": payload.get("weight_year"),
            "data": {
                "yoy_series": list(payload.get("yoy_series") or []),
                "mom_series": list(payload.get("mom_series") or []),
                "contributions_yoy": payload.get("contributions_yoy"),
                "contributions_mom": payload.get("contributions_mom"),
            },
        }

    if cell_type == "meeting_statement_diff":
        if not meeting_id:
            return {"kind": "note", "message": "此 Cell 需要在页面顶部选择一个示例会议（meeting_id）。"}
        ctx = get_meeting_context(meeting_id, history_cutoff=DEFAULT_HISTORY_CUTOFF)
        prev = (ctx.get("previous_meeting") or {}).get("meeting_id")

        cur_dec = get_meeting_decision_cached(meeting_id)
        prev_dec = get_meeting_decision_cached(prev) if prev else None

        statement_diff = None
        minutes_diff = None
        if prev_dec:
            statement_diff = _unified_diff(
                prev_dec.get("statement"),
                cur_dec.get("statement"),
                a_label=f"{prev}:statement",
                b_label=f"{meeting_id}:statement",
            )
            minutes_diff = _unified_diff(
                prev_dec.get("minutes_summary"),
                cur_dec.get("minutes_summary"),
                a_label=f"{prev}:minutes",
                b_label=f"{meeting_id}:minutes",
            )

        return {
            "kind": "meeting_statement_diff",
            "meeting_id": meeting_id,
            "previous_meeting_id": prev,
            "current": {
                "statement": cur_dec.get("statement"),
                "minutes_summary": cur_dec.get("minutes_summary"),
            },
            "previous": {
                "statement": (prev_dec or {}).get("statement") if prev_dec else None,
                "minutes_summary": (prev_dec or {}).get("minutes_summary") if prev_dec else None,
            },
            "diff": {"statement": statement_diff, "minutes_summary": minutes_diff},
            "cta": {
                "generate_url": f"/history/{meeting_id}/decision",
                "hint": "若为空，请先在“历史会议模拟→决议/纪要”生成并缓存。",
            },
        }

    if cell_type == "meeting_decision_brief":
        if not meeting_id:
            return {"kind": "note", "message": "此 Cell 需要在页面顶部选择一个示例会议（meeting_id）。"}

        dec = get_meeting_decision_cached(meeting_id)
        statement = dec.get("statement")
        minutes = dec.get("minutes_summary")

        if not statement and not minutes:
            return {
                "kind": "meeting_decision_brief",
                "meeting_id": meeting_id,
                "available": False,
                "message": "未找到已缓存的 Statement/Minutes 生成稿；请先在历史会议模拟中生成“决议与纪要”。",
                "cta": {"generate_url": f"/history/{meeting_id}/decision"},
            }

        joined = (statement or "") + "\n" + (minutes or "")
        return {
            "kind": "meeting_decision_brief",
            "meeting_id": meeting_id,
            "available": True,
            "statement_md": statement,
            "minutes_md": minutes,
            "analysis": {
                "statement_headings": _extract_md_headings(statement),
                "minutes_headings": _extract_md_headings(minutes),
                "top_terms": _top_terms(joined, k=12),
            },
            "cta": {"generate_url": f"/history/{meeting_id}/decision"},
        }

    return {"kind": "note", "message": f"Unknown cell type: {cell_type}"}

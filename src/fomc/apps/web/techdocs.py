from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path
from typing import Any

import markdown2

from fomc.config.paths import REPO_ROOT
from fomc.apps.web.backend import PortalError


CONTENT_DIR = REPO_ROOT / "content" / "techdocs"


@dataclass(frozen=True)
class TechDocsChapterMeta:
    slug: str
    title: str
    order: int = 1000
    summary: str | None = None
    hidden: bool = False
    filename: str | None = None
    depth: int = 0

    def as_dict(self) -> dict:
        return {
            "slug": self.slug,
            "title": self.title,
            "order": self.order,
            "summary": self.summary,
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


def _parse_bool(val: object | None) -> bool:
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    s = str(val).strip().lower()
    return s in {"1", "true", "yes", "y", "on"}


def _strip_leading_h1(md_body: str) -> str:
    """
    TechDocs pages already render an explicit page title in the template.
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
    return sorted([p for p in CONTENT_DIR.rglob("*.md") if p.is_file()])


def list_techdocs_chapters(*, include_hidden: bool = False) -> list[TechDocsChapterMeta]:
    chapters: list[TechDocsChapterMeta] = []
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
            TechDocsChapterMeta(
                slug=slug,
                title=title,
                order=order,
                summary=(str(meta.get("summary")).strip() if meta.get("summary") is not None else None),
                hidden=hidden,
                filename=str(path.relative_to(REPO_ROOT)),
                depth=slug.count("/"),
            )
        )
    if not include_hidden:
        chapters = [c for c in chapters if not c.hidden]
    return sorted(chapters, key=lambda c: (c.order, c.slug))


def get_techdocs_chapter(slug: str) -> tuple[TechDocsChapterMeta, str]:
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
    chapter_meta = TechDocsChapterMeta(
        slug=slug,
        title=title,
        order=order,
        summary=(str(meta.get("summary")).strip() if meta.get("summary") is not None else None),
        hidden=_parse_bool(meta.get("hidden")),
        filename=str(path.relative_to(REPO_ROOT)),
        depth=slug.count("/"),
    )

    body = _strip_leading_h1(body)
    html_body = markdown2.markdown(body, extras=["autolink", "break-on-newline", "fenced-code-blocks"])
    return chapter_meta, html_body


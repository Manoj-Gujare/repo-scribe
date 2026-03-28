"""Frontmatter parsing for blog preview and metadata fallbacks."""
import json
import re
from typing import Any


def split_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    """
    Split YAML-like frontmatter (first --- ... --- block) from body.
    Returns ({}, bom-stripped text) if no valid block found.
    """
    text = markdown.lstrip("\ufeff")
    if not text.startswith("---"):
        return {}, text

    after_open = text[3:].lstrip("\r\n")
    m = re.search(r"(?m)^---\s*$", after_open)
    if not m:
        return {}, text

    fm_block = after_open[: m.start()]
    body = after_open[m.end():].lstrip("\r\n")
    return _parse_simple_frontmatter(fm_block), body


def _parse_simple_frontmatter(block: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        val = rest.strip()
        if key == "word_count" and re.fullmatch(r"\d+", val):
            out[key] = int(val)
        elif key == "read_time":
            rm = re.match(r"^(\d+)", val)
            if rm:
                out[key] = int(rm.group(1))
        elif key == "tags" and val.startswith("["):
            try:
                out[key] = json.loads(val)
            except json.JSONDecodeError:
                pass
        elif key in ("style", "tone", "title", "subtitle", "repo", "generated_at"):
            out[key] = val.strip("\"'")
    return out


def merge_display_metadata(final_blog: str, metadata: dict | None) -> dict:
    """Prefer pipeline metadata; fill gaps from frontmatter; fix read_time."""
    parsed, _ = split_frontmatter(final_blog)
    base = parsed.copy()
    if metadata:
        base.update(metadata)

    rt = base.get("read_time", 0)
    if isinstance(rt, str):
        m = re.match(r"^(\d+)", rt.strip())
        base["read_time"] = int(m.group(1)) if m else 0

    wc = base.get("word_count") or 0
    if not base.get("read_time") and wc:
        base["read_time"] = max(1, round(int(wc) / 200))
    return base


def strip_frontmatter_for_display(markdown: str) -> str:
    """Return body only (frontmatter stripped); BOM is always removed."""
    _, body = split_frontmatter(markdown)
    return body

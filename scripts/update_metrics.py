#!/usr/bin/env python3
"""Fetch citation counts for SHAIPE publications and update static metrics.

Queries open scholarly APIs (OpenAlex, Semantic Scholar, Crossref, Europe PMC)
across both journal DOIs and related preprint/version IDs, plus Google Scholar
author profiles when `SERPAPI_KEY` is configured. Takes the highest verified
count for each paper (respecting any manual `min_citations` baseline) and
updates `assets/data/metrics.json` and `publications.html`.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = ROOT / "assets" / "data" / "metrics.json"
PUBLICATIONS_HTML = ROOT / "publications.html"

USER_AGENT = (
    "SHAIPE-Website-Metrics/1.0 "
    "(https://github.com/josh-strong/SHAIPE_website; "
    "mailto:joshua.strong@eng.ox.ac.uk)"
)
TIMEOUT_SECONDS = 8
_SCHOLAR_AUTHOR_CACHE: dict[str, list[dict]] = {}


def fetch_json(url: str) -> dict | list | None:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        safe_url = re.sub(r"api_key=[^&]+", "api_key=***", url)
        print(f"  [skip] {safe_url} ({exc})", file=sys.stderr)
        return None


def normalise_title(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def all_dois_for(pub: dict) -> list[str]:
    dois: list[str] = []
    primary = pub.get("doi")
    if isinstance(primary, str) and primary.strip():
        dois.append(primary.strip())
    for extra in pub.get("related_dois", []) or []:
        if isinstance(extra, str) and extra.strip() and extra.strip() not in dois:
            dois.append(extra.strip())
    return dois


def query_openalex(pub: dict) -> int | None:
    dois = all_dois_for(pub)
    work_ids: list[str] = [
        wid.split("/")[-1]
        for wid in (pub.get("openalex_ids") or [])
        if isinstance(wid, str) and wid.strip()
    ]
    individual_counts: list[int] = []

    if dois:
        doi_filter = "|".join(f"https://doi.org/{d}" for d in dois)
        encoded = urllib.parse.quote(doi_filter, safe=":|/")
        data = fetch_json(f"https://api.openalex.org/works?filter=doi:{encoded}&per-page=25")
        if isinstance(data, dict):
            for item in data.get("results", []) or []:
                if not isinstance(item, dict):
                    continue
                if isinstance(item.get("cited_by_count"), int):
                    individual_counts.append(item["cited_by_count"])
                wid = str(item.get("id", "")).split("/")[-1]
                if wid.startswith("W") and wid not in work_ids:
                    work_ids.append(wid)

    dedup_count: int | None = None
    if len(work_ids) > 1:
        cites_filter = "|".join(work_ids)
        cites_data = fetch_json(f"https://api.openalex.org/works?filter=cites:{cites_filter}&per-page=1")
        if isinstance(cites_data, dict):
            meta_count = (cites_data.get("meta") or {}).get("count")
            if isinstance(meta_count, int):
                dedup_count = meta_count
    elif len(work_ids) == 1 and not individual_counts:
        work_data = fetch_json(f"https://api.openalex.org/works/{work_ids[0]}")
        if isinstance(work_data, dict) and isinstance(work_data.get("cited_by_count"), int):
            individual_counts.append(work_data["cited_by_count"])

    candidates = [c for c in individual_counts if c is not None]
    if dedup_count is not None:
        candidates.append(dedup_count)
    return max(candidates) if candidates else None


def query_semantic_scholar(pub: dict) -> int | None:
    dois = all_dois_for(pub)
    if not dois:
        return None
    if len(dois) == 1:
        encoded = urllib.parse.quote(dois[0], safe="")
        url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{encoded}?fields=citationCount"
        data = fetch_json(url)
        if isinstance(data, dict) and isinstance(data.get("citationCount"), int):
            return data["citationCount"]
        return None

    citing_ids: set[str] = set()
    counts: list[int] = []
    for doi in dois:
        encoded = urllib.parse.quote(doi, safe="")
        url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{encoded}?fields=citationCount,citations.paperId"
        data = fetch_json(url)
        if isinstance(data, dict):
            if isinstance(data.get("citationCount"), int):
                counts.append(data["citationCount"])
            for cit in data.get("citations", []) or []:
                if isinstance(cit, dict) and cit.get("paperId"):
                    citing_ids.add(str(cit["paperId"]))
    if citing_ids:
        counts.append(len(citing_ids))
    return max(counts) if counts else None


def query_crossref(pub: dict) -> int | None:
    counts: list[int] = []
    for doi in all_dois_for(pub):
        encoded = urllib.parse.quote(doi, safe="")
        data = fetch_json(f"https://api.crossref.org/works/{encoded}")
        if isinstance(data, dict):
            msg = data.get("message", {})
            if isinstance(msg, dict) and isinstance(msg.get("is-referenced-by-count"), int):
                counts.append(msg["is-referenced-by-count"])
    return max(counts) if counts else None


def query_google_scholar_serpapi(pub: dict) -> int | None:
    api_key = os.environ.get("SERPAPI_KEY", "").strip()
    author_id = str(pub.get("scholar_author_id", "")).strip()
    title = str(pub.get("title", "")).strip()
    if not api_key or not author_id or not title:
        return None

    if author_id not in _SCHOLAR_AUTHOR_CACHE:
        params = urllib.parse.urlencode(
            {
                "engine": "google_scholar_author",
                "author_id": author_id,
                "hl": "en",
                "num": "100",
                "api_key": api_key,
            }
        )
        data = fetch_json(f"https://serpapi.com/search.json?{params}")
        articles = data.get("articles", []) if isinstance(data, dict) else []
        _SCHOLAR_AUTHOR_CACHE[author_id] = articles if isinstance(articles, list) else []

    target_titles = [normalise_title(title)] + [
        normalise_title(t) for t in (pub.get("scholar_titles") or []) if isinstance(t, str)
    ]
    matched_total = 0
    matched_any = False
    for art in _SCHOLAR_AUTHOR_CACHE[author_id]:
        if not isinstance(art, dict):
            continue
        art_title = normalise_title(str(art.get("title", "")))
        if any(art_title == t or art_title.startswith(t) for t in target_titles if t):
            cited_val = (art.get("cited_by") or {}).get("value")
            matched_any = True
            if isinstance(cited_val, int):
                matched_total += cited_val

    return matched_total if matched_any else None


SOURCES = [
    ("google_scholar", query_google_scholar_serpapi),
    ("openalex", query_openalex),
    ("semantic_scholar", query_semantic_scholar),
    ("crossref", query_crossref),
]


def format_citations(count: int) -> str:
    return "1 citation" if count == 1 else f"{count} citations"


def sync_publications_from_html(metrics: dict, html_text: str) -> None:
    """Ensure any `data-citation-doi` present in publications.html is tracked."""
    known = {p["doi"].lower(): p for p in metrics.get("publications", []) if "doi" in p}
    for match in re.finditer(r'data-citation-doi="([^"]+)"', html_text):
        doi = match.group(1).strip()
        if doi and doi.lower() not in known:
            entry = {
                "id": re.sub(r"[^a-z0-9]+", "-", doi.lower()).strip("-"),
                "doi": doi,
                "open_access": True,
                "citations": 0,
                "source": "initial",
            }
            metrics.setdefault("publications", []).append(entry)
            known[doi.lower()] = entry


def update_html_fallbacks(html_text: str, metrics: dict) -> str:
    totals = metrics["totals"]
    pub_count = totals["publications"]
    cit_count = totals["citations"]
    oa_count = totals.get("open_access", pub_count)
    oa_pct = f"{round((oa_count / pub_count) * 100)}%" if pub_count else "100%"

    replacements = {
        "total-publications": str(pub_count),
        "total-citations": str(cit_count),
        "open-access": oa_pct,
    }
    for key, value in replacements.items():
        pattern = re.compile(rf'(<[^>]*\bdata-metric="{re.escape(key)}"[^>]*>)(.*?)(</[^>]+>)', re.DOTALL)
        html_text = pattern.sub(rf"\g<1>{value}\g<3>", html_text)

    by_doi = {p["doi"].lower(): int(p.get("citations", 0)) for p in metrics.get("publications", []) if "doi" in p}

    def replace_doi(match: re.Match[str]) -> str:
        open_tag, doi, inner, close_tag = match.group(1), match.group(2), match.group(3), match.group(4)
        count = by_doi.get(doi.lower())
        if count is None:
            return match.group(0)
        clean_open = re.sub(r"\s+hidden(?==\"[^\"]*\"|\b)", "", open_tag)
        if count > 0:
            return f"{clean_open}{format_citations(count)}{close_tag}"
        hidden_open = clean_open[:-1] + " hidden>"
        return f"{hidden_open}{close_tag}"

    doi_pattern = re.compile(
        r'(<[^>]*\bdata-citation-doi="([^"]+)"[^>]*>)(.*?)(</[^>]+>)',
        re.DOTALL,
    )
    return doi_pattern.sub(replace_doi, html_text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="Skip network queries and only sync HTML from metrics.json")
    parser.add_argument("--force-timestamp", action="store_true", help="Update updated_at even if counts are unchanged")
    args = parser.parse_args()

    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    original_snapshot = json.dumps(metrics, sort_keys=True)

    html_text = PUBLICATIONS_HTML.read_text(encoding="utf-8") if PUBLICATIONS_HTML.exists() else ""
    if html_text:
        sync_publications_from_html(metrics, html_text)

    if not args.offline:
        for pub in metrics.get("publications", []):
            doi = pub.get("doi")
            if not doi:
                continue
            print(f"Checking {doi}...")
            results: list[tuple[int, str]] = []
            for source_name, fn in SOURCES:
                count = fn(pub)
                if count is not None:
                    print(f"  {source_name}: {count}")
                    results.append((count, source_name))

            min_floor = pub.get("min_citations")
            if isinstance(min_floor, int):
                results.append((min_floor, "google_scholar"))

            if results:
                best_count, best_source = max(results, key=lambda item: item[0])
                pub["citations"] = best_count
                pub["source"] = best_source
            else:
                print(f"  [warn] No API responded for {doi}; keeping {pub.get('citations', 0)}", file=sys.stderr)

    pubs = metrics.get("publications", [])
    metrics["totals"] = {
        "publications": len(pubs),
        "citations": sum(int(p.get("citations", 0)) for p in pubs),
        "open_access": sum(1 for p in pubs if p.get("open_access", True)),
    }

    comparable_before = json.loads(original_snapshot)
    comparable_after = json.loads(json.dumps(metrics))
    comparable_before.pop("updated_at", None)
    comparable_after.pop("updated_at", None)

    if comparable_before != comparable_after or args.force_timestamp:
        metrics["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    METRICS_PATH.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    if html_text:
        updated_html = update_html_fallbacks(html_text, metrics)
        if updated_html != html_text:
            PUBLICATIONS_HTML.write_text(updated_html, encoding="utf-8")

    print(
        f"Summary: {metrics['totals']['publications']} publications, "
        f"{metrics['totals']['citations']} total citations."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Streamlit dashboard for inspecting crawl outputs."""

import json
import sqlite3
from collections import Counter
from statistics import mean
from typing import Any, Dict, List
from urllib.parse import urlparse

import streamlit as st


def _read_pages_from_sqlite(db_path: str) -> List[Dict[str, Any]]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT payload FROM pages ORDER BY crawled_at DESC").fetchall()
    return [json.loads(row[0]) for row in rows]


def _read_pages_from_json(json_path: str) -> List[Dict[str, Any]]:
    with open(json_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload.get("pages", [])


@st.cache_data(show_spinner=False)
def load_pages(source_type: str, source_path: str) -> List[Dict[str, Any]]:
    if source_type == "sqlite":
        return _read_pages_from_sqlite(source_path)
    return _read_pages_from_json(source_path)


def with_derived_fields(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for page in pages:
        url = page.get("url", "")
        host = urlparse(url).netloc or "unknown"
        status = "error" if page.get("error") else "ok"
        row = dict(page)
        row["host"] = host
        row["status"] = status
        rows.append(row)
    return rows


def filter_pages(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    providers = sorted({p.get("provider", "unknown") for p in pages})
    hosts = sorted({p.get("host", "unknown") for p in pages})

    st.sidebar.subheader("Filters")
    selected_providers = st.sidebar.multiselect("Provider", providers, default=providers)
    selected_hosts = st.sidebar.multiselect("Host", hosts, default=hosts)
    status_filter = st.sidebar.multiselect("Status", ["ok", "error"], default=["ok", "error"])
    min_content_length = st.sidebar.slider("Min content length", 0, 15000, 0, 100)
    title_query = st.sidebar.text_input("Title contains", "").strip().lower()

    filtered: List[Dict[str, Any]] = []
    for page in pages:
        if page.get("provider", "unknown") not in selected_providers:
            continue
        if page.get("host", "unknown") not in selected_hosts:
            continue
        if page.get("status", "ok") not in status_filter:
            continue
        if int(page.get("content_length", 0)) < min_content_length:
            continue
        if title_query and title_query not in str(page.get("title", "")).lower():
            continue
        filtered.append(page)

    return filtered


def render_metrics(pages: List[Dict[str, Any]]) -> None:
    total = len(pages)
    ok_count = sum(1 for page in pages if page.get("status") == "ok")
    error_count = total - ok_count
    avg_length = int(mean([int(page.get("content_length", 0)) for page in pages])) if pages else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pages", total)
    col2.metric("OK", ok_count)
    col3.metric("Errors", error_count)
    col4.metric("Avg Content Length", avg_length)


def render_charts(pages: List[Dict[str, Any]]) -> None:
    provider_counts = Counter(page.get("provider", "unknown") for page in pages)
    host_counts = Counter(page.get("host", "unknown") for page in pages)
    status_counts = Counter(page.get("status", "ok") for page in pages)

    col1, col2, col3 = st.columns(3)
    col1.subheader("By Provider")
    col1.bar_chart(provider_counts)
    col2.subheader("By Host")
    col2.bar_chart(host_counts)
    col3.subheader("By Status")
    col3.bar_chart(status_counts)


def render_table_and_detail(pages: List[Dict[str, Any]]) -> None:
    if not pages:
        st.warning("No pages match current filters.")
        return

    table_rows = [
        {
            "timestamp": page.get("timestamp"),
            "provider": page.get("provider"),
            "status": page.get("status"),
            "host": page.get("host"),
            "content_length": page.get("content_length", 0),
            "links_found": page.get("links_found", 0),
            "title": page.get("title", ""),
            "url": page.get("url", ""),
        }
        for page in pages
    ]
    st.subheader("Pages")
    st.dataframe(table_rows, use_container_width=True)

    url_options = [page.get("url", "") for page in pages if page.get("url")]
    selected_url = st.selectbox("Inspect page", options=url_options)
    selected = next(page for page in pages if page.get("url") == selected_url)

    tab1, tab2, tab3 = st.tabs(["Metadata", "Markdown", "Text"])
    with tab1:
        st.json(selected)
    with tab2:
        st.markdown(selected.get("content_markdown", ""))
    with tab3:
        st.text_area("Extracted text", selected.get("content", ""), height=280)

    st.download_button(
        "Download filtered JSON",
        data=json.dumps(pages, ensure_ascii=False, indent=2),
        file_name="filtered_pages.json",
        mime="application/json",
    )


def main() -> None:
    st.set_page_config(page_title="Gathering Dashboard", layout="wide")
    st.title("Gathering Dashboard")
    st.caption("Visualize crawl outputs from SQLite or JSON")

    st.sidebar.header("Data Source")
    source_type = st.sidebar.radio("Source type", ["sqlite", "json"], horizontal=True)
    source_path = st.sidebar.text_input(
        "Source path",
        value="crawl_data.db" if source_type == "sqlite" else "scraped_data.json",
    )

    if not source_path:
        st.info("Provide a source path to load crawl data.")
        return

    try:
        pages = load_pages(source_type, source_path)
    except Exception as exc:
        st.error(f"Failed to load source: {exc}")
        return

    pages = with_derived_fields(pages)
    filtered_pages = filter_pages(pages)

    render_metrics(filtered_pages)
    render_charts(filtered_pages)
    render_table_and_detail(filtered_pages)


if __name__ == "__main__":
    main()
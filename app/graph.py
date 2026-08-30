# placeholder for graph construction
from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from .state import NewsState

from .sources import (
    fetch_gdelt,
    fetch_rss,
    fetch_newsapi,
    fetch_youtube,
)

from .processing import (
    aggregate_sources,
    deduplicate,
    rank_items,
)

from .llm import summarize

from .email import send_email


# ============================================================
# GRAPH
# ============================================================

builder = StateGraph(
    NewsState
)


# ============================================================
# SOURCE NODES
# ============================================================

builder.add_node(
    "fetch_gdelt",
    fetch_gdelt
)

builder.add_node(
    "fetch_rss",
    fetch_rss
)

builder.add_node(
    "fetch_newsapi",
    fetch_newsapi
)

builder.add_node(
    "fetch_youtube",
    fetch_youtube
)


# ============================================================
# PROCESSING NODES
# ============================================================

builder.add_node(
    "aggregate",
    aggregate_sources
)

builder.add_node(
    "deduplicate",
    deduplicate
)

builder.add_node(
    "rank",
    rank_items
)

builder.add_node(
    "summarize",
    summarize
)

builder.add_node(
    "send_email",
    send_email
)


# ============================================================
# PARALLEL SOURCE EXECUTION
# ============================================================

builder.add_edge(
    START,
    "fetch_gdelt"
)

builder.add_edge(
    START,
    "fetch_rss"
)

builder.add_edge(
    START,
    "fetch_newsapi"
)

builder.add_edge(
    START,
    "fetch_youtube"
)


# ============================================================
# AFTER SOURCES
# ============================================================

builder.add_edge(
    "fetch_gdelt",
    "aggregate"
)

builder.add_edge(
    "fetch_rss",
    "aggregate"
)

builder.add_edge(
    "fetch_newsapi",
    "aggregate"
)

builder.add_edge(
    "fetch_youtube",
    "aggregate"
)


# ============================================================
# PIPELINE
# ============================================================

builder.add_edge(
    "aggregate",
    "deduplicate"
)

builder.add_edge(
    "deduplicate",
    "rank"
)

builder.add_edge(
    "rank",
    "summarize"
)

builder.add_edge(
    "summarize",
    "send_email"
)

builder.add_edge(
    "send_email",
    END
)


# ============================================================
# COMPILE
# ============================================================

graph = builder.compile()
# placeholder for processing pipelines
from rapidfuzz import fuzz

from .state import NewsState, NewsItem


# ============================================================
# AGGREGATE
# ============================================================

def aggregate_sources(state: NewsState) -> dict:

    print("Aggregating sources...")

    items: list[NewsItem] = []

    items.extend(
        state.get("gdelt_items", [])
    )

    items.extend(
        state.get("rss_items", [])
    )

    items.extend(
        state.get("newsapi_items", [])
    )

    items.extend(
        state.get("youtube_items", [])
    )

    print(
        f"Total collected: {len(items)}"
    )

    return {
        "all_items": items
    }


# ============================================================
# DEDUPLICATION
# ============================================================

def deduplicate(state: NewsState) -> dict:

    print("Deduplicating...")

    items = state.get(
        "all_items",
        []
    )

    unique: list[NewsItem] = []

    for item in items:

        title = (
            item["title"]
            .strip()
            .lower()
        )

        if not title:
            continue

        duplicate = False

        for existing in unique:

            existing_title = (
                existing["title"]
                .strip()
                .lower()
            )

            similarity = fuzz.ratio(
                title,
                existing_title,
            )

            if similarity >= 85:

                duplicate = True
                break

        if not duplicate:

            unique.append(item)

    print(
        f"After deduplication: "
        f"{len(unique)}"
    )

    return {
        "deduplicated_items": unique
    }


# ============================================================
# RANKING
# ============================================================

def rank_items(state: NewsState) -> dict:

    print("Ranking news...")

    items = state.get(
        "deduplicated_items",
        []
    )

    source_scores = {

        "TechCrunch": 5,

        "MIT Technology Review": 5,

        "Google AI": 5,

        "Hugging Face": 5,

        "GDELT": 3,

        "NewsAPI": 3,

        "YouTube": 2,
    }

    scored_items = []

    for item in items:

        score = source_scores.get(
            item["source"],
            2
        )

        item_copy = dict(item)

        item_copy["_score"] = score

        scored_items.append(
            item_copy
        )

    scored_items.sort(
        key=lambda x: x["_score"],
        reverse=True,
    )

    top_items = scored_items[:15]

    print(
        f"Selected {len(top_items)} items"
    )

    return {
        "ranked_items": top_items
    }
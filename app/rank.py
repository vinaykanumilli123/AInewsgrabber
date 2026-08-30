from datetime import datetime, timezone


IMPORTANT_KEYWORDS = {

    "gpt": 3,
    "gemini": 3,
    "claude": 3,
    "openai": 3,
    "anthropic": 3,
    "deepmind": 3,
    "model": 3,
    "agent": 3,

    "launch": 2,
    "release": 2,
    "announced": 2,
    "research": 2,
    "breakthrough": 2,
    "open source": 2,
    "open-weight": 2,

    "funding": 2,
    "acquisition": 2,
    "regulation": 2,
    "lawsuit": 2,
}


SOURCE_SCORES = {

    "TechCrunch": 5,
    "MIT Technology Review": 5,
    "Hugging Face": 5,
    "Google AI": 5,

    "GDELT": 3,
    "NewsAPI": 3,

    "YouTube": 2,
}


def calculate_score(item):

    title = item.get(
        "title",
        ""
    ).lower()

    content = item.get(
        "content",
        ""
    ).lower()

    text = title + " " + content

    score = 0

    # --------------------------------------------------------
    # Source quality
    # --------------------------------------------------------

    score += SOURCE_SCORES.get(
        item.get("source"),
        2
    )

    # --------------------------------------------------------
    # Keyword importance
    # --------------------------------------------------------

    for keyword, points in IMPORTANT_KEYWORDS.items():

        if keyword in text:

            score += points

    # --------------------------------------------------------
    # Title bonus
    # --------------------------------------------------------

    for keyword in IMPORTANT_KEYWORDS:

        if keyword in title:

            score += 1

    # --------------------------------------------------------
    # Content quality
    # --------------------------------------------------------

    if len(content) > 200:

        score += 2

    elif len(content) > 100:

        score += 1

    return score


def rank_items(
    items,
    limit=15
):

    print("Ranking news...")

    for item in items:

        item["_score"] = (
            calculate_score(item)
        )

    items.sort(
        key=lambda x: x["_score"],
        reverse=True
    )

    ranked = items[:limit]

    print(
        f"Selected {len(ranked)} items"
    )

    for index, item in enumerate(
        ranked,
        start=1
    ):

        print(
            f"{index}. "
            f"{item['title'][:80]} "
            f"(score={item['_score']})"
        )

    return ranked
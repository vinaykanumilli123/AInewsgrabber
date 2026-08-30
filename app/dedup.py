import re

from rapidfuzz.fuzz import ratio


SIMILARITY_THRESHOLD = 85


def normalize_title(title):

    title = title.lower()

    title = re.sub(
        r"[^a-z0-9\s]",
        "",
        title
    )

    title = re.sub(
        r"\s+",
        " ",
        title
    )

    return title.strip()


def deduplicate(items):

    print("Deduplicating...")

    unique_items = []

    seen_urls = set()
    seen_titles = []

    for item in items:

        url = item.get(
            "url",
            ""
        ).strip()

        title = item.get(
            "title",
            ""
        ).strip()

        if not title:
            continue

        # ----------------------------------------------------
        # Exact URL duplicate
        # ----------------------------------------------------

        if url and url in seen_urls:

            continue

        normalized = normalize_title(
            title
        )

        # ----------------------------------------------------
        # Fuzzy title duplicate
        # ----------------------------------------------------

        duplicate = False

        for existing_title in seen_titles:

            similarity = ratio(
                normalized,
                existing_title
            )

            if similarity >= SIMILARITY_THRESHOLD:

                duplicate = True
                break

        if duplicate:

            continue

        # ----------------------------------------------------
        # Keep article
        # ----------------------------------------------------

        unique_items.append(
            item
        )

        if url:

            seen_urls.add(
                url
            )

        seen_titles.append(
            normalized
        )

    print(
        f"After deduplication: "
        f"{len(unique_items)}"
    )

    return unique_items
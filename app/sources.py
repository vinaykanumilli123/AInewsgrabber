import os
import time
import re

import requests
import feedparser

from dotenv import load_dotenv

from .state import NewsState, NewsItem


load_dotenv()


# ============================================================
# CONFIG
# ============================================================

REQUEST_TIMEOUT = 10
GDELT_RETRIES = 2


# ============================================================
# HELPERS
# ============================================================

def clean_text(text: str) -> str:
    """
    Remove basic HTML and unnecessary whitespace.
    """

    if not text:
        return ""

    # Remove HTML tags
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def get_category(
    title: str,
    content: str
) -> str:
    """
    Basic rule-based categorization.

    We can make this smarter later if needed.
    """

    text = (
        f"{title} {content}"
    ).lower()

    if any(
        word in text
        for word in [
            "model",
            "gpt",
            "gemini",
            "claude",
            "llama",
        ]
    ):
        return "AI Models"

    if any(
        word in text
        for word in [
            "agent",
            "agents",
            "agentic",
        ]
    ):
        return "AI Agents"

    if any(
        word in text
        for word in [
            "research",
            "study",
            "paper",
            "researcher",
        ]
    ):
        return "AI Research"

    if any(
        word in text
        for word in [
            "funding",
            "investment",
            "acquisition",
            "acquire",
        ]
    ):
        return "AI Business"

    if any(
        word in text
        for word in [
            "law",
            "lawsuit",
            "regulation",
            "regulator",
            "government",
        ]
    ):
        return "AI Regulation"

    return "General AI"


def make_item(
    title: str,
    url: str,
    source: str,
    published_at: str,
    content: str,
) -> NewsItem:

    title = clean_text(title)
    content = clean_text(content)

    return {
        "title": title,
        "url": url,
        "source": source,
        "published_at": published_at,
        "content": content,
        "category": get_category(
            title,
            content
        ),
    }


# ============================================================
# GDELT
# ============================================================

def fetch_gdelt(
    state: NewsState
) -> dict:

    print("Fetching GDELT...")

    url = (
        "https://api.gdeltproject.org/"
        "api/v2/doc/doc"
    )

    params = {
        "query": (
            '"artificial intelligence" OR '
            '"generative AI" OR '
            '"AI agents"'
        ),
        "mode": "artlist",
        "maxrecords": 20,
        "format": "json",
        "sort": "datedesc",
    }

    for attempt in range(
        1,
        GDELT_RETRIES + 2
    ):

        try:

            response = requests.get(
                url,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            data = response.json()

            articles = []

            for article in data.get(
                "articles",
                []
            ):

                title = article.get(
                    "title",
                    ""
                )

                article_url = article.get(
                    "url",
                    ""
                )

                published_at = article.get(
                    "seendate",
                    ""
                )

                if not title or not article_url:
                    continue

                articles.append(
                    make_item(
                        title=title,
                        url=article_url,
                        source="GDELT",
                        published_at=published_at,
                        content="",
                    )
                )

            print(
                f"GDELT: "
                f"{len(articles)} items"
            )

            return {
                "gdelt_items": articles
            }

        except Exception as e:

            print(
                f"GDELT attempt "
                f"{attempt} failed: {e}"
            )

            if attempt <= GDELT_RETRIES:

                time.sleep(2)

    print(
        "GDELT unavailable. "
        "Continuing with other sources..."
    )

    return {
        "gdelt_items": []
    }


# ============================================================
# NEWS API
# ============================================================

def fetch_newsapi(
    state: NewsState
) -> dict:

    print("Fetching NewsAPI...")

    api_key = os.getenv(
        "NEWS_API_KEY"
    )

    if not api_key:

        print(
            "NEWS_API_KEY not configured."
        )

        return {
            "newsapi_items": []
        }

    url = (
        "https://newsapi.org/v2/everything"
    )

    params = {
        "q": (
            '"artificial intelligence" OR '
            '"generative AI" OR '
            '"AI agents"'
        ),
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,
        "apiKey": api_key,
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        articles = []

        for article in data.get(
            "articles",
            []
        ):

            title = article.get(
                "title",
                ""
            )

            article_url = article.get(
                "url",
                ""
            )

            if not title or not article_url:
                continue

            articles.append(
                make_item(
                    title=title,
                    url=article_url,
                    source="NewsAPI",
                    published_at=article.get(
                        "publishedAt",
                        ""
                    ),
                    content=(
                        article.get(
                            "description",
                            ""
                        )
                        or ""
                    ),
                )
            )

        print(
            f"NewsAPI: "
            f"{len(articles)} items"
        )

        return {
            "newsapi_items": articles
        }

    except Exception as e:

        print(
            f"NewsAPI failed: {e}"
        )

        return {
            "newsapi_items": []
        }


# ============================================================
# RSS
# ============================================================

RSS_FEEDS = {

    "TechCrunch":
        "https://techcrunch.com/feed/",

    "MIT Technology Review":
        "https://www.technologyreview.com/feed/",

    "Hugging Face":
        "https://huggingface.co/blog/feed.xml",

    "Google AI":
        "https://blog.google/technology/ai/rss/",
}


def fetch_rss(
    state: NewsState
) -> dict:

    print("Fetching RSS feeds...")

    articles = []

    for source, url in RSS_FEEDS.items():

        try:

            feed = feedparser.parse(
                url
            )

            for entry in feed.entries[:10]:

                title = entry.get(
                    "title",
                    ""
                )

                article_url = entry.get(
                    "link",
                    ""
                )

                if not title or not article_url:
                    continue

                published_at = (
                    entry.get(
                        "published",
                        ""
                    )
                    or entry.get(
                        "updated",
                        ""
                    )
                    or ""
                )

                content = (
                    entry.get(
                        "summary",
                        ""
                    )
                    or entry.get(
                        "description",
                        ""
                    )
                    or ""
                )

                articles.append(
                    make_item(
                        title=title,
                        url=article_url,
                        source=source,
                        published_at=published_at,
                        content=content,
                    )
                )

        except Exception as e:

            print(
                f"{source} RSS failed: "
                f"{e}"
            )

    print(
        f"RSS: "
        f"{len(articles)} items"
    )

    return {
        "rss_items": articles
    }


# ============================================================
# YOUTUBE
# ============================================================

def fetch_youtube(
    state: NewsState
) -> dict:

    print("Fetching YouTube...")

    api_key = os.getenv(
        "YOUTUBE_API_KEY"
    )

    if not api_key:

        print(
            "YOUTUBE_API_KEY not configured."
        )

        return {
            "youtube_items": []
        }

    url = (
        "https://www.googleapis.com/"
        "youtube/v3/search"
    )

    params = {
        "part": "snippet",
        "q": (
            "artificial intelligence AI"
        ),
        "type": "video",
        "order": "date",
        "maxResults": 10,
        "key": api_key,
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        articles = []

        for item in data.get(
            "items",
            []
        ):

            video_id = (
                item.get(
                    "id",
                    {}
                )
                .get(
                    "videoId"
                )
            )

            if not video_id:
                continue

            snippet = item.get(
                "snippet",
                {}
            )

            title = snippet.get(
                "title",
                ""
            )

            article_url = (
                "https://www.youtube.com/"
                f"watch?v={video_id}"
            )

            content = snippet.get(
                "description",
                ""
            )

            published_at = snippet.get(
                "publishedAt",
                ""
            )

            articles.append(
                make_item(
                    title=title,
                    url=article_url,
                    source="YouTube",
                    published_at=published_at,
                    content=content,
                )
            )

        print(
            f"YouTube: "
            f"{len(articles)} items"
        )

        return {
            "youtube_items": articles
        }

    except Exception as e:

        print(
            f"YouTube failed: {e}"
        )

        return {
            "youtube_items": []
        }
# placeholder for application state management
from typing import TypedDict


class NewsItem(TypedDict):
    title: str
    url: str
    source: str
    published_at: str
    content: str
    category: str


class NewsState(TypedDict, total=False):

    # Source results
    gdelt_items: list[NewsItem]
    rss_items: list[NewsItem]
    newsapi_items: list[NewsItem]
    youtube_items: list[NewsItem]

    # Processing
    all_items: list[NewsItem]
    deduplicated_items: list[NewsItem]
    ranked_items: list[NewsItem]

    # Final output
    final_digest: str
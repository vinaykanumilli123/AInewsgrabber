import os

from dotenv import load_dotenv

from langchain_google_genai import (
    ChatGoogleGenerativeAI
)

from langchain_groq import ChatGroq


load_dotenv()


# ============================================================
# GEMINI
# ============================================================

def get_gemini():

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv(
            "GEMINI_API_KEY"
        ),
        temperature=0.2,
    )


# ============================================================
# GROQ
# ============================================================

def get_groq():

    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv(
            "GROQ_API_KEY"
        ),
        temperature=0.2,
    )


# ============================================================
# PREPARE ARTICLES
# ============================================================

def prepare_articles(items):

    articles = []

    for index, item in enumerate(
        items,
        start=1
    ):

        articles.append(
            f"""
ARTICLE {index}

Title:
{item.get("title", "")}

Source:
{item.get("source", "")}

Category:
{item.get("category", "")}

Published:
{item.get("published_at", "")}

URL:
{item.get("url", "")}

Description:
{item.get("content", "")[:700]}

--------------------------------
"""
        )

    return "\n".join(
        articles
    )


# ============================================================
# SUMMARIZE
# ============================================================

def summarize(state):

    print("Summarizing news...")

    items = state.get(
        "ranked_items",
        []
    )

    if not items:

        return {
            "final_digest":
                "No important AI news was found today."
        }

    articles_text = prepare_articles(
        items
    )

    prompt = f"""
You are writing a daily AI newsletter for
a normal person who is interested in AI
but does NOT have a technical background.

Your job is to explain important AI news
as if you are explaining it to an intelligent
12-year-old.

Do NOT use complicated technical language
unless absolutely necessary.

If you use a technical word, explain it
immediately in simple language.

From the articles below, select the
10 most important and useful stories.

For every story use EXACTLY this format:

STORY_START

TITLE:
A short, interesting headline.

WHAT_HAPPENED:
Explain what happened in 2-3 very simple
sentences.

WHY_IT_MATTERS:
Explain why a normal person should care
in 1-2 simple sentences.

IN_SIMPLE_WORDS:
Explain the story again in ONE very simple
sentence using an everyday analogy when useful.

CATEGORY:
Choose one:
AI Models
AI Agents
AI Research
AI Business
AI Regulation
AI Products
AI Infrastructure
Other

SOURCE:
The original source name.

URL:
The original article URL.

STORY_END

IMPORTANT RULES:

1. Explain like a child can understand it.
2. Do not assume the reader knows AI terminology.
3. Avoid hype and exaggerated language.
4. Do not invent facts.
5. Only use information contained in the articles.
6. Remove duplicate stories.
7. If several articles discuss the same event,
   combine them into one story.
8. Prefer important developments over minor news.
9. Prefer recent developments.
10. Prefer model releases, AI agents, research,
    major company announcements, regulation,
    lawsuits, funding, acquisitions and
    important open-source developments.
11. Ignore promotional or low-value articles.
12. Keep each story short.
13. Maximum 10 stories.
14. Do NOT write an introduction or conclusion.
15. Follow the format exactly.

Here are today's articles:

{articles_text}
"""

    # ========================================================
    # GEMINI
    # ========================================================

    try:

        print("Trying Gemini...")

        llm = get_gemini()

        response = llm.invoke(
            prompt
        )

        print(
            "Gemini succeeded."
        )

        return {
            "final_digest":
                response.content
        }

    except Exception as e:

        print(
            f"Gemini failed: {e}"
        )

    # ========================================================
    # GROQ FALLBACK
    # ========================================================

    try:

        print(
            "Falling back to Groq..."
        )

        llm = get_groq()

        response = llm.invoke(
            prompt
        )

        print(
            "Groq succeeded."
        )

        return {
            "final_digest":
                response.content
        }

    except Exception as e:

        print(
            f"Groq failed: {e}"
        )

        return {
            "final_digest":
                "Today's AI digest could not be generated."
        }
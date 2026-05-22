import feedparser
import requests
import random

from bs4 import BeautifulSoup
from newspaper import Article
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# RSS FEEDS
# ─────────────────────────────────────────────

RSS_FEEDS = {

    "India": {

        "All": [

            "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
            "https://feeds.feedburner.com/ndtvnews-top-stories",
            "https://indianexpress.com/section/india/feed/",
            "https://www.thehindu.com/news/national/feeder/default.rss"
        ],

        "Politics": [

            "https://www.thehindu.com/news/national/feeder/default.rss",
            "https://indianexpress.com/section/political-pulse/feed/"
        ],

        "Technology": [

            "https://feeds.feedburner.com/gadgets360-latest",
            "https://tech.hindustantimes.com/rss/topnews/rssfeed.xml"
        ],

        "Finance": [

            "https://www.moneycontrol.com/rss/business.xml",
            "https://www.livemint.com/rss/markets"
        ],

        "Sports": [

            "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
            "https://sports.ndtv.com/rss/all"
        ],

        "Entertainment": [

            "https://www.bollywoodhungama.com/rss/news.xml",
            "https://www.ndtv.com/entertainment/feed"
        ]
    },

    "World": {

        "All": [

            "http://rss.cnn.com/rss/edition.rss",
            "http://feeds.bbci.co.uk/news/rss.xml",
            "https://feeds.reuters.com/reuters/topNews",
            "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
        ],

        "Politics": [

            "http://rss.cnn.com/rss/cnn_allpolitics.rss",
            "https://feeds.bbci.co.uk/news/politics/rss.xml"
        ],

        "Technology": [

            "https://techcrunch.com/feed/",
            "https://www.theverge.com/rss/index.xml"
        ],

        "Finance": [

            "https://feeds.reuters.com/news/usbusiness",
            "https://www.cnbc.com/id/10001147/device/rss/rss.html"
        ],

        "Sports": [

            "https://www.espn.com/espn/rss/news",
            "https://sports.yahoo.com/top/rss.xml"
        ],

        "Entertainment": [

            "https://www.hollywoodreporter.com/feed/",
            "https://variety.com/feed/"
        ]
    }
}

# ─────────────────────────────────────────────
# FETCH NEWS
# ─────────────────────────────────────────────

def fetch_news(region="India", category="All"):

    articles = []

    feeds = RSS_FEEDS.get(region, {}).get(category, [])

    time_threshold = datetime.utcnow() - timedelta(hours=24)

    for url in feeds:

        try:

            feed = feedparser.parse(url)

            # GET LARGER ARTICLE POOL

            entries = feed.entries[:20]

            # RANDOMIZE ARTICLES

            random.shuffle(entries)

            for entry in entries:

                try:

                    published = None

                    if hasattr(entry, "published_parsed"):

                        published = datetime(*entry.published_parsed[:6])

                    # SKIP OLD ARTICLES

                    if (
                        published
                        and
                        published < time_threshold
                    ):

                        continue

                    title = entry.get("title", "No Title")

                    link = entry.get("link", "")

                    summary = entry.get("summary", "")

                    raw_source = (
                        feed.feed.title
                        if hasattr(feed, "feed") and hasattr(feed.feed, "title")
                        else "Unknown"
                    )

                    # Clean long RSS feed titles
                    if "|" in raw_source:
                        source = raw_source.split("|")[-1].strip()
                    elif " - " in raw_source:
                        source = raw_source.split(" - ")[-1].strip()
                    elif len(raw_source) > 30:
                        source = raw_source[:28].strip() + "…"
                    else:
                        source = raw_source

                    # CLEAN HTML SUMMARY

                    summary = BeautifulSoup(
                        summary,
                        "html.parser"
                    ).get_text()

                    # ARTICLE OBJECT

                    article_data = {

                        "title": title,

                        "link": link,

                        "summary": summary,

                        "source": source,

                        "published": published
                    }

                    articles.append(article_data)

                except Exception:
                    continue

        except Exception:
            continue

    # REMOVE DUPLICATES

    unique_articles = []

    seen_links = set()

    for article in articles:

        if article["link"] not in seen_links:

            unique_articles.append(article)

            seen_links.add(article["link"])

    # SORT BY LATEST

    unique_articles.sort(
        key=lambda x:
        x["published"]
        if x["published"]
        else datetime.min,
        reverse=True
    )

    # RANDOMIZE SLIGHTLY AMONG LATEST

    latest_pool = unique_articles[:30]

    random.shuffle(latest_pool)

    return latest_pool

# ─────────────────────────────────────────────
# EXTRACT FULL ARTICLE
# ─────────────────────────────────────────────

def extract_full_article(url):

    try:

        article = Article(url)

        article.download()

        article.parse()

        text = article.text

        if text and len(text) > 200:

            return text

    except Exception:
        pass

    # FALLBACK METHOD

    try:

        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        paragraphs = soup.find_all("p")

        text = " ".join(
            [
                p.get_text()
                for p in paragraphs
            ]
        )

        return text

    except Exception:

        return ""
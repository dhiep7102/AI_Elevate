# collector.py
import feedparser
from gnews import GNews

def collect_rss(feeds, limit=5):
    articles = []
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries[:limit]:
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "summary": entry.summary if hasattr(entry, "summary") else ""
            })
    return articles

# def collect_google_news(topic, limit=5):
#     google_news = GNews(language='en', country='US', period='1d', max_results=limit)
#     results = google_news.get_news(topic)
#     articles = [{"title": r["title"], "link": r["url"], "summary": r["description"]} for r in results]
#     return articles

def collect_all(topic="global news"):
    rss_feeds = [
        "https://vnexpress.net/rss/tin-moi-nhat.rss",  # VNExpress – latest news
        "https://tuoitre.vn/rss/tin-moi-nhat.rss",  # Tuoi Tre – latest news
        "https://vietnamnews.vn/rss/general.rss",  # Vietnam News English site
        "https://thanhnien.vn/rss/home.rss",  # Thanh Nien – general news
        "https://nhandan.vn/rss/home.rss"  # Nhan Dan – official newspaper
    ]
    articles = collect_rss(rss_feeds) #+ collect_google_news(topic)
    print(f"[Collector] Collected {len(articles)} articles")
    return articles
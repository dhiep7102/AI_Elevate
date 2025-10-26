# tools.py
import re
from typing import List, Dict, Any
from collector import collect_all, collect_rss

def tool_get_latest_articles(topic: str = "global news", limit: int = 30) -> Dict[str, Any]:
    """Gọi collector gốc của bạn để lấy bài (có thể nhiều nguồn)."""
    articles = collect_all(topic)  # dùng source hiện tại của bạn
    if limit and isinstance(limit, int):
        articles = articles[:limit]
    return {"articles": articles, "count": len(articles)}

def tool_search_articles_by_keyword(articles: List[Dict[str, Any]], keyword: str) -> Dict[str, Any]:
    kw = keyword.lower()
    filtered = [a for a in articles if kw in (a.get("title","")+a.get("summary","")).lower()]
    return {"filtered": filtered, "count": len(filtered)}

def tool_extract_entities(text: str) -> Dict[str, Any]:
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    money  = re.findall(r"\$?\b\d+(?:\.\d{1,2})?\b", text)
    dates  = re.findall(r"\b20\d{2}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/20\d{2}\b", text)
    return {"emails": emails, "money_values": money, "dates": dates}

def tool_sentiment_overview(texts: List[str]) -> Dict[str, Any]:
    pos_words = {"tăng", "tốt", "tích cực", "kỷ lục", "ổn định", "phê duyệt"}
    neg_words = {"giảm", "xấu", "tiêu cực", "đình trệ", "trì hoãn", "bị phạt"}
    pos = sum(sum(1 for w in pos_words if w in t.lower()) for t in texts)
    neg = sum(sum(1 for w in neg_words if w in t.lower()) for t in texts)
    overall = "positive" if pos >= neg else "negative"
    return {"positive_hits": pos, "negative_hits": neg, "overall": overall}

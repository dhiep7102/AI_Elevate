# analyzer.py
import json, time
from typing import List, Dict, Any
from openai import AzureOpenAI
from config import (
    AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT,
    TEMPERATURE, TOP_P, LOG_PATH
)
from memory import ConversationManager
from tools import (
    tool_get_latest_articles, tool_search_articles_by_keyword,
    tool_extract_entities, tool_sentiment_overview
)

# ==== OpenAI client ====
client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION
)

SYSTEM_PROMPT = """Bạn là trợ lý tóm tắt tin tức Việt Nam. Trả lời súc tích, có mục, liệt kê sự kiện chính, nguyên nhân, tác động.
Khi cần dữ kiện, hãy đề xuất gọi function thích hợp thay vì đoán. Khi không đủ thông tin, hãy hỏi lại rõ.
Hãy suy nghĩ từng bước để chọn tool đúng, nhưng CHỈ trả kết luận gọn gàng (không lộ chuỗi suy luận)."""

FEW_SHOT = [
    {"role":"user","content":"Tóm tắt nhanh các tin kinh tế trong ngày."},
    {"role":"assistant","content":"Dưới đây là bản tóm tắt theo nhóm chủ đề: • Tăng trưởng/Chính sách • Doanh nghiệp • Thị trường (nguồn kèm link)."},
]

# Function schemas cho LLM
FUNCTIONS = [
    {
        "name": "tool_get_latest_articles",
        "description": "Lấy danh sách bài viết mới nhất theo chủ đề từ nhiều nguồn RSS.",
        "parameters": {"type":"object","properties":{"topic":{"type":"string"},"limit":{"type":"integer"}}, "required": ["topic"]}
    },
    {
        "name": "tool_search_articles_by_keyword",
        "description": "Lọc danh sách bài viết theo từ khóa.",
        "parameters": {"type":"object","properties":{"articles":{"type":"array","items":{"type":"object"}},"keyword":{"type":"string"}}, "required": ["articles","keyword"]}
    },
    {
        "name": "tool_extract_entities",
        "description": "Trích xuất thực thể (email, số tiền, ngày tháng) từ văn bản.",
        "parameters": {"type":"object","properties":{"text":{"type":"string"}}, "required": ["text"]}
    },
    {
        "name": "tool_sentiment_overview",
        "description": "Tổng hợp sentiment đơn giản (positive/negative) từ danh sách văn bản.",
        "parameters": {"type":"object","properties":{"texts":{"type":"array","items":{"type":"string"}}}, "required": ["texts"]}
    }
]

def _tool_router(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if name == "tool_get_latest_articles":
        return tool_get_latest_articles(args.get("topic", "global news"), args.get("limit", 30))
    if name == "tool_search_articles_by_keyword":
        return tool_search_articles_by_keyword(args.get("articles", []), args.get("keyword", ""))
    if name == "tool_extract_entities":
        return tool_extract_entities(args.get("text",""))
    if name == "tool_sentiment_overview":
        return tool_sentiment_overview(args.get("texts", []))
    return {"error": f"Unknown tool: {name}"}

# ====== API GIỮ NGUYÊN CHO GUI ======
def summarize_articles(articles: List[Dict[str, Any]], topic: str) -> str:
    """
    Giữ nguyên chữ ký cũ để GUI không phải đổi.
    Bên trong: tạo cuộc hội thoại, để LLM tự gọi function khi cần,
    rồi trả về bản tóm tắt có dẫn nguồn.
    """
    cm = ConversationManager(client, SYSTEM_PROMPT, FEW_SHOT)

    # Ghép input (vẫn giống cách cũ: list bài + topic)
    user_prompt = {
        "role": "user",
        "content": (
            "Bạn là biên tập viên. Hãy tóm tắt theo chủ đề:\n"
            f"Chủ đề: {topic}\n"
            "Dữ liệu đầu vào (JSON articles) dưới đây. Nếu cần lọc/nhóm/sentiment, hãy gọi function phù hợp rồi tóm tắt có mục, có nguồn:\n"
            + json.dumps(articles, ensure_ascii=False)[:12000]  # hạn chế độ dài
        )
    }
    cm.add(**user_prompt)

    t0 = time.time()
    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        messages=cm.history,
        functions=FUNCTIONS,
        function_call="auto",
    )
    msg = response.choices[0].message

    # Nếu model yêu cầu gọi tool, ta chạy và feed lại
    if getattr(msg, "function_call", None):
        fn = msg.function_call.name
        args = json.loads(msg.function_call.arguments or "{}")
        result = _tool_router(fn, args)
        cm.add(role="function", name=fn, content=json.dumps(result, ensure_ascii=False))


        follow = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            messages=cm.history
        )
        msg = follow.choices[0].message

    text = (msg.content or "").strip()
    # log đơn giản cho rubric
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": time.time(),
            "type": "summary",
            "topic": topic,
            "articles_count": len(articles),
            "output_preview": text[:400]
        }, ensure_ascii=False) + "\n")
    return text

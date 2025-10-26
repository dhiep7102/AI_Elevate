# InsightFlow AI — Vietnam News Summarizer (Azure OpenAI)

A multi-turn chatbot that collects Vietnam news from multiple RSS sources, lets the model **call tools** to filter/inspect content, and **summarizes** by topic with concise, structured output.  
This project is aligned with the Workshop brief: **Azure OpenAI SDK**, **function calling**, **(reasonable) batching**, **message management**, **few-shot + CoT prompting**, and **conversation logs**.

---

## 1) How this source meets the Workshop requirements

### ✅ OpenAI SDK (Azure) & Chat Completions
- Azure client is initialized and used for `chat.completions`.  
  See initialization and usage in `analyzer.py`.

### ✅ Function Calling (tool-usage)
- Tool schemas are declared and routed to local functions that operate on articles.  
  Functions: `tool_get_latest_articles`, `tool_search_articles_by_keyword`, `tool_extract_entities`, `tool_sentiment_overview`.  
  See function schemas + router in `analyzer.py`, and tool implementations in `tools.py`.

### ✅ Prompting (system + few-shot + “hidden” CoT instruction)
- **System prompt** defines role, constraints, formatting.  
- **Few-shot** gives exemplar behavior.  
- **CoT (hidden)**: model is told to think to choose tools but only output conclusions.  
  See `SYSTEM_PROMPT` & `FEW_SHOT` in `analyzer.py`.

### ✅ Message management (conversation memory)
- Conversation history is maintained and can be summarized (evolution summary) to keep context short and relevant in long sessions.  
  See `ConversationManager` in `memory.py`. (Used by `analyzer.summarize_articles`.)

### ✅ Batching / multi-source collection
- Multiple RSS feeds are fetched in one pass to form the working corpus for each summary (reasonable batching for this scope).  
  See `collector.collect_all` / `collect_rss`.

### ✅ Multi-turn dialogue with context
- **GUI** supports repeated topic runs in the same session; the analyzer tracks and summarizes context internally.  
  See `GUI.py` and the `summarize_articles` API contract kept intact.

### ✅ Conversation logs
- Each summary request writes an entry to `logs/conversations.jsonl` (timestamp, topic, preview).  
  Implemented in `analyzer.py`.

---

## 2) Repository structure

```
.
├─ analyzer.py      # Core: prompting, function calling, logging
├─ collector.py     # News collection from multiple VN RSS feeds
├─ config.py        # Azure OpenAI settings (hard-coded; no ENV)
├─ GUI.py           # Tkinter app (kept as-is, calls summarize_articles)
├─ main.py          # Optional CLI runner
├─ memory.py        # ConversationManager: history + auto-summarize
├─ tools.py         # Tool functions invoked via function-calling
└─ logs/
   └─ conversations.jsonl  # conversation summaries/logs (generated)
```

---

## 3) Quick start

### Requirements
- Python **3.10+**
- Packages:
  ```
  openai==1.*
  feedparser>=6.0.11
  ```
  Install:
  ```bash
  pip install "openai==1.*" "feedparser>=6.0.11"
  ```
- **Tkinter** (for GUI):
  - Windows/macOS (python.org): usually preinstalled.
  - Ubuntu/Debian: `sudo apt-get install -y python3-tk`

### Configure Azure OpenAI (NO ENV)
Open `config.py` and set these values (hard-coded):
```python
AZURE_OPENAI_ENDPOINT    = "https://<your-resource>.openai.azure.com/"
AZURE_OPENAI_KEY         = "<YOUR_AZURE_OPENAI_KEY>"
AZURE_OPENAI_API_VERSION = "2024-07-01-preview"
AZURE_OPENAI_DEPLOYMENT  = "<your-deployment-name>"  # e.g., gpt-4o-mini
```
> Tip: **Deployment name** is the name you gave when deploying the model in Azure, not the base model name string.

### Run (GUI)
```bash
python GUI.py
```
- Enter a topic (e.g., “kinh tế”, “giáo dục”, “công nghệ”) → click **Tóm tắt**.  
- The app will collect news from multiple VN sources and generate a structured summary with source links.

### Run (CLI) — optional
```bash
python main.py
```

---

## 4) How it works (flow)

1) **Collect**: `collector.collect_all()` reads multiple RSS feeds (VNExpress, Tuổi Trẻ, etc.) and returns `[{title, link, summary}, …]`.  
2) **Ask**: GUI/CLI passes `(articles, topic)` to `analyzer.summarize_articles(...)` (API unchanged).  
3) **Prompt**: The analyzer seeds the conversation with `SYSTEM_PROMPT` and `FEW_SHOT`, then provides the articles JSON + topic to the model.  
4) **Function-calling**: If the model decides it needs filtering, entity extraction, or sentiment overview, it calls a declared tool; results are fed back into the model to compose the final answer.  
   - Tool schemas & router in `analyzer.py`; implementations in `tools.py`.  
5) **Summarize**: The model returns a **structured, concise** Vietnamese summary with **2–5 source links**.  
6) **Log**: A brief log entry is appended to `logs/conversations.jsonl` for the session.

---

## 5) Feature details (for evaluators)

### Prompting strategy
- **System**: Editor persona, output style (“Sự kiện chính • Bối cảnh/Nguyên nhân • Tác động • Triển vọng”), sources requirement, tool-first stance, hidden CoT.  
- **Few-shot**: Sets concise, sectioned summaries aligned with Vietnamese newsroom style.

### Tools (function calling)
- `tool_get_latest_articles(topic, limit)`: optionally refresh corpus from RSS if needed.  
- `tool_search_articles_by_keyword(articles, keyword)`: server-side filtering by query.  
- `tool_extract_entities(text)`: quick regex-based entity hints (emails, money, dates).  
- `tool_sentiment_overview(texts[])`: coarse sentiment signal for a set of texts.

### Conversation management
- `ConversationManager` maintains a message window and can **summarize** recent turns to keep context lean over longer sessions.  
  (Useful for extended GUI runs.)

### Batching / performance
- **Multi-source** RSS ingestion in a single sweep (`collector.collect_all`). This is a practical batching step for workshop scope; can be extended to `aiohttp` later without changing GUI API.

### Logging
- Appends JSON lines with timestamp, topic, article count, and output preview; useful for demos and grading.

---

## 6) Usage examples

**GUI flow**
1. Launch `GUI.py`.
2. Enter: `kinh tế`.
3. Click **Tóm tắt** → the output window shows:
   - Fetch status and article count,
   - A structured Vietnamese summary (key events, why they matter, near-term outlook),
   - 2–5 source links from the collected feeds.

**CLI flow**
```
$ python main.py
== Vietnam News Summarizer (CLI) ==
Nhập chủ đề (Enter để thoát): công nghệ
Thu được 30 bài. Đang tóm tắt...
=== BẢN TÓM TẮT ===
<structured summary here>
```

---

## 7) Troubleshooting

- **401/403 / Invalid credentials**  
  Check `config.py`: verify endpoint format `https://<resource>.openai.azure.com/`, the **deployment name** (not just the base model name), and API version allowed on your Azure resource.

- **`tkinter` not found (Linux)**  
  Install: `sudo apt-get install -y python3-tk`.

- **Empty summary or too few articles**  
  RSS feeds occasionally throttle or change fields. Add/replace sources in `collector.py` as needed.

---

## 8) Limits & guardrails

- **Live accuracy** depends on RSS availability; no paywalled sites are fetched.  
- **Entity & sentiment tools** are lightweight (regex/keyword)—they’re **hints**, not full NLP pipelines.  
- **Chain-of-thought** is prompted for tool selection only; the assistant outputs final conclusions, not raw reasoning.

---

## 9) Suggested extensions (future work)

- **Async fetching** (`aiohttp`) for faster, parallel RSS retrieval.  
- **Clustering**: group similar articles before summarization.  
- **Source scoring**: prioritize diverse/authoritative outlets.  
- **Exporters**: save summaries to HTML/Markdown/PDF and auto-email/Telegram.

---

## 10) Deliverables checklist (for the Workshop)

- **Problem & mock data schema**: news summarization with RSS corpus.  
- **Prompt templates (few-shot + hidden CoT)**: defined in analyzer.  
- **Complete SDK-based chatbot** with chat completions, function calling, message management.  
- **(Reasonable) batching**: multi-source RSS sweep.  
- **Tested conversation logs**: `logs/conversations.jsonl`.  
- **Team presentation ready**: use this README’s sections (Architecture, Prompting, Tools, Demo, Learnings) to build your slides.

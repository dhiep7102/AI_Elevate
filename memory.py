# memory.py
import json, uuid
from typing import List, Dict
from openai import AzureOpenAI
from config import (
    AZURE_OPENAI_DEPLOYMENT, HISTORY_WINDOW, SUMMARY_KEEP_LAST, SUMMARY_TRIGGER_TURNS
)

class ConversationManager:
    """Giữ history ngắn + tự tóm tắt khi dài, để GUI vẫn multi-turn."""
    def __init__(self, client: AzureOpenAI, system_prompt: str, few_shot: List[Dict]):
        self.client = client
        self.history: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}, *few_shot]
        self.turns = 0
        self.session_id = str(uuid.uuid4())

    def add(self, role: str, content: str, name: str = None):
        msg = {"role": role, "content": content}
        if name:
            msg["name"] = name
        self.history.append(msg)

    def _summarize(self):
        snippet = self.history[-SUMMARY_KEEP_LAST:]
        prompt = [{"role":"system","content":"Tóm tắt hội thoại ngắn gọn để giữ ngữ cảnh cho các lượt sau (tiếng Việt)."}, *snippet]
        resp = self.client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            temperature=0.2,
            messages=prompt
        )
        summary = resp.choices[0].message.content.strip()
        self.history = [
            self.history[0],  # system gốc
            {"role":"system","content":f"[Conversation summary]\n{summary}"},
            *snippet
        ]

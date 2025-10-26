# config.py
# AZURE_OPENAI_ENDPOINT = "https://aiportalapi.stu-platform.live/jpe"
# AZURE_OPENAI_KEY = "sk-7mB_8TPvxyB1hbWfklo_iQ"
# AZURE_OPENAI_DEPLOYMENT = "GPT-4o-mini"  # name of your deployed model

# # Email (nếu dùng Gmail notifier)
# EMAIL_ADDRESS = "you@gmail.com"
# EMAIL_PASSWORD = "YOUR_APP_PASSWORD"
# EMAIL_RECEIVER = "recipient@gmail.com"

# # Telegram (nếu dùng Telegram notifier)
# TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
# TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

#--------------------------------------------------------------------------
# config.py
import os
from pathlib import Path

# ==== Azure OpenAI (ENV) ====
AZURE_OPENAI_ENDPOINT    = os.getenv("AZURE_OPENAI_ENDPOINT", "https://aiportalapi.stu-platform.live/jpe")
AZURE_OPENAI_KEY         = os.getenv("AZURE_OPENAI_KEY", "sk-7mB_8TPvxyB1hbWfklo_iQ")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-07-01-preview")
AZURE_OPENAI_DEPLOYMENT  = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")  # deployment name của bạn

# ==== Model params ====
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
TOP_P       = float(os.getenv("TOP_P", "1.0"))

# ==== Conversation mgmt ====
HISTORY_WINDOW        = int(os.getenv("HISTORY_WINDOW", "12"))
SUMMARY_KEEP_LAST     = int(os.getenv("SUMMARY_KEEP_LAST", "6"))
SUMMARY_TRIGGER_TURNS = int(os.getenv("SUMMARY_TRIGGER_TURNS", str(HISTORY_WINDOW)))

# ==== Logging ====
LOG_DIR  = Path(os.getenv("LOG_DIR", "logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "conversations.jsonl"

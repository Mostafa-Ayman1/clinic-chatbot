import os
from dotenv import load_dotenv


load_dotenv(override=True)

# ---------------------------------------------------------
# 1. OpenAI Configuration
# ---------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
N8N_WEBHOOK = os.getenv("N8N_WEBHOOK")




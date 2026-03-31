'''
config/settings.py: environment manager
'''
import os
from dotenv import load_dotenv

load_dotenv()

ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")
if not ZHIPUAI_API_KEY:
    raise ValueError("未检测到 ZHIPUAI_API_KEY，请检查 .env 文件是否正确加载")

MODEL_NAME = os.getenv("MODEL_NAME", "glm-4")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0")

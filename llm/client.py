'''
llm/client.py: initiate chat models and agents
'''
from langchain_community.chat_models import ChatZhipuAI

from config.settings import MODEL_NAME, TEMPERATURE
from models.schemas import CVInfo, JDInfo, MatchResult

chat_model = ChatZhipuAI(
    model=MODEL_NAME,
    temperature=TEMPERATURE,
)

structured_jd_model = chat_model.with_structured_output(JDInfo)
structured_cv_model = chat_model.with_structured_output(CVInfo)
structured_match_model = chat_model.with_structured_output(MatchResult)



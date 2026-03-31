'''
llm/client.py: initiate chat models and agents
'''
from langchain_community.chat_models import ChatZhipuAI

from config.settings import MODEL_NAME, TEMPERATURE
from models.schemas import CVInfo, JDInfo, MatchResult

model = ChatZhipuAI(
    model=MODEL_NAME,
    temperature=TEMPERATURE,
)

structured_jd_model = model.with_structured_output(JDInfo)
structured_cv_model = model.with_structured_output(CVInfo)
structured_match_model = model.with_structured_output(MatchResult)



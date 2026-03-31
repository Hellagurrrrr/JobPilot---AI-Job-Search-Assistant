'''
services/match_service.py: matching between cv and jd
'''
from langchain.messages import AIMessage, HumanMessage, SystemMessage

from models.schemas import CVInfo, JDInfo, MatchResult
from llm.prompts import MATCH_ANALYSIS_SYSTEM_PROMPT
from llm.client import structured_match_model

def match_cv_to_jd(cv: CVInfo, jd: JDInfo) -> MatchResult:
    messages = [
        SystemMessage(
            content=(MATCH_ANALYSIS_SYSTEM_PROMPT)
        ),
        HumanMessage(
            content=f"""
CV:
{cv.model_dump_json(indent=2, ensure_ascii=False)}

JD:
{jd.model_dump_json(indent=2, ensure_ascii=False)}
"""
        )
    ]
    return structured_match_model.invoke(messages)
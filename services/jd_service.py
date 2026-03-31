'''
services/jd_service.py: jd loading and extracting
'''
from langchain.messages import AIMessage, HumanMessage, SystemMessage

from loaders.job_page_loader import JobPageLoader
from models.schemas import JDInfo
from llm.prompts import JD_ANALYSIS_SYSTEM_PROMPT
from llm.client import structured_jd_model

job_page_loader = JobPageLoader()

def extract_jd_from_text(job_text: str) -> JDInfo:
    messages = [
        SystemMessage(
            content=(JD_ANALYSIS_SYSTEM_PROMPT)
        ),
        HumanMessage(content=job_text),
    ]
    return structured_jd_model.invoke(messages)

def extract_jd_from_url(url: str) -> JDInfo:
    page_text = job_page_loader.load(url)
    return extract_jd_from_text(page_text)
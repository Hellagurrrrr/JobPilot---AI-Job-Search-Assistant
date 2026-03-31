'''
services/cv_service/py: cv loading and extracting
'''
from langchain.messages import AIMessage, HumanMessage, SystemMessage

from loaders.cv_doc_loader import CVDocLoader
from models.schemas import CVInfo
from llm.prompts import CV_ANALYSIS_SYSTEM_PROMPT
from llm.client import structured_cv_model

cv_doc_loader = CVDocLoader()

def extract_cv_from_text(cv_text: str) -> CVInfo:
    messages = [
        SystemMessage(
            content=(CV_ANALYSIS_SYSTEM_PROMPT)
        ),
        HumanMessage(content=cv_text),
    ]
    return structured_cv_model.invoke(messages)

def extract_cv_from_pdf(fp: str) -> CVInfo:
    doc_text = cv_doc_loader.load(fp)
    return extract_cv_from_text(doc_text)

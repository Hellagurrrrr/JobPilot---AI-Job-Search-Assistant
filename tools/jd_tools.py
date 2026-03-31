'''
tools/jd_tools.py
'''
import json
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from services.jd_service import extract_jd_from_text, extract_jd_from_url

class JDUrlPathInput(BaseModel):
    jd_url: str = Field(description="岗位要求网页链接路径")


class JDTextInput(BaseModel):
    jd_text: str = Field(description="岗位要求原始文本内容")

@tool(args_schema=JDTextInput)
def extract_jd_from_text_tool(jd_text: str) -> str:
    """从岗位要求文本中提取结构化信息。"""
    result = extract_jd_from_text(jd_text)
    return json.dumps(result.model_dump(), ensure_ascii=False, indent=2)

@tool(args_schema=JDUrlPathInput)
def extract_jd_from_url_tool(jd_url: str) -> str:
    """从岗位要求的网页链接直接提取结构化信息。"""
    result = extract_jd_from_url(jd_url)
    return json.dumps(result.model_dump(), ensure_ascii=False, indent=2)

jd_tools = [
    extract_jd_from_text_tool,
    extract_jd_from_url_tool
]


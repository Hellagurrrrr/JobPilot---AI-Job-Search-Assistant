'''
tools/cv_tools.py: tools for cv handling
'''
import json
from langchain.tools import tool
from pydantic import BaseModel, Field

from services.cv_service import (
    load_cv_text_from_pdf,
    extract_cv_from_text,
    extract_cv_from_pdf,
)

class CVPdfPathInput(BaseModel):
    file_path: str = Field(description="简历PDF文件路径")


class CVTextInput(BaseModel):
    cv_text: str = Field(description="简历原始文本内容")


@tool(args_schema=CVPdfPathInput)
def load_cv_text_from_pdf_tool(file_path: str) -> str:
    """读取 PDF 简历并返回原始文本。"""
    return load_cv_text_from_pdf(file_path)


@tool(args_schema=CVTextInput)
def extract_cv_from_text_tool(cv_text: str) -> str:
    """读取 PDF 简历，并返回结构化简历 JSON。"""
    result = extract_cv_from_text(cv_text)
    return json.dumps(result.model_dump(), ensure_ascii=False, indent=2)


@tool(args_schema=CVPdfPathInput)
def extract_cv_from_pdf_tool(file_path: str) -> str:
    """解析简历文本，并返回结构化简历 JSON。"""
    result = extract_cv_from_pdf(file_path)
    return json.dumps(result.model_dump(), ensure_ascii=False, indent=2)


cv_tools = [
    load_cv_text_from_pdf_tool,
    extract_cv_from_text_tool,
    extract_cv_from_pdf_tool,
]
import os
from dotenv import load_dotenv

from langchain_community.chat_models import ChatZhipuAI
from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain_community.document_loaders import WebBaseLoader

from pydantic import BaseModel, Field

from loaders.job_page_loader import JobPageLoader
from loaders.cv_doc_loader import CVDocLoader

load_dotenv()
if not os.getenv("ZHIPUAI_API_KEY"):
    raise ValueError("未检测到 ZHIPUAI_API_KEY，请检查 .env 文件是否正确加载")

class JDInfo(BaseModel):
    """Structured information extracted from a job description."""
    title: str = Field(description="The title of the job")
    required_skills: list[str] = Field(description="List of all required skills for this job")
    preferred_skills: list[str] = Field(description="List of all preferred or nice-to-have skills")
    responsibilities: list[str] = Field(description="List of main responsibilities for this job")
    Education_requirments: str = Field(description="The requirment of education background")

class CVInfo(BaseModel):
    """Structured information extracted from a CV."""
    skills: list[str] = Field(description="List of all skills this candidate have")
    projects: list[str] = Field(description="List of all projects done by this candidate")
    experience: list[str] = Field(description="List of all experience this condidate have except their projects")
    education: list[str] = Field(description="List of all education experience of this candidate")

class MatchResult(BaseModel):
    """Structured information of matching result for uploaded cv and jd."""
    match_score: float = Field(description="A score of the matching result")
    missing_skills: list[str] = Field(description="List of all skills mising from the provided job description")
    strengths: list[str] = Field(description="List of all strengths the candidate have for applying provided job")
    suggestion: str = Field(description="A short suggestion for this candidate")

model = ChatZhipuAI(
    model="glm-4",
    temperature=0.1,
)

structured_jd_model = model.with_structured_output(JDInfo)
structured_cv_model = model.with_structured_output(CVInfo)
structured_match_model = model.with_structured_output(MatchResult)

job_page_loader = JobPageLoader()
cv_doc_loader = CVDocLoader()

def analyze_jd_from_text(job_text: str) -> JDInfo:
    messages = [
        SystemMessage(
            content=(
                "你是一个招聘分析专家。"
                "请从岗位描述中提取结构化信息。"
                "要求："
                "1. 不要臆造信息；"
                "2. required_skills 只放明确的岗位要求；"
                "3. preferred_skills 只放优先项/加分项；"
                "4. responsibilities 提取主要职责；"
                "5. 缺失信息返回空列表或 Unknown。"
            )
        ),
        HumanMessage(content=job_text),
    ]
    return structured_jd_model.invoke(messages)

def analyze_cv_from_text(cv_text: str) -> str:
    messages = [
        SystemMessage(
            content=(
                "你是一个简历分析助手。"
                "请从简历中提取结构化信息。"
                "要求："
                "1. 不要臆造信息；"
                "2. 缺失信息返回空列表或 Unknown。"
            )
        ),
        HumanMessage(content=cv_text),
    ]
    return structured_cv_model.invoke(messages)

def match_cv_jd(text: str) -> str:
    messages = [
        SystemMessage(
            content=(
                "你是一个岗位匹配分析助手。"
                "请根据提供的简历和岗位描述分析用户的匹配度。"
                "要求："
                "1. 不要臆造信息；"
                "2. 缺失信息返回空列表或 Unknown。"
            )
        ),
        HumanMessage(content=text),
    ]
    return structured_match_model.invoke(messages)

def analyze_jd_from_url(url: str) -> JDInfo:
    page_text = job_page_loader.load(url)
    return analyze_jd_from_text(page_text)

def analyze_cv_from_doc(fp: str) -> CVInfo:
    doc_text = cv_doc_loader.load(fp)
    return analyze_cv_from_text(doc_text)

def analyze_match_from_text(cv: CVInfo, jd: JDInfo) -> MatchResult:
    messages = [
        SystemMessage(
            content=(
                "你是一个岗位匹配分析助手。"
                "请基于结构化CV和JD进行分析。"
                "不要臆造信息。"
            )
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

def main():
    # 简历读取
    file_path = input("请输入简历文件路径: ").strip()
    try:
        cv = analyze_cv_from_doc(file_path)
        print("\n===== CV 分析结果 =====")
        print(cv.model_dump_json(indent=2, ensure_ascii=False))
    except Exception as e:
        print("\n===== 分析失败 =====")
        print(e)
        print("请直接粘贴 CV 文件地址继续分析。")    

    # JD读取
    url = input("请输入岗位链接: ").strip()
    try:
        jd = analyze_jd_from_url(url)
        print("\n===== JD 分析结果 =====")
        print(jd.model_dump_json(indent=2, ensure_ascii=False))
    except Exception as e:
        print("\n===== 抓取或分析失败 =====")
        print(e)
        print("请直接粘贴 JD 文本继续分析。")

    if cv != None and jd != None:
        match_result = analyze_match_from_text(cv, jd)
        print("\n===== 岗位匹配分析结果 =====")
        print(match_result.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
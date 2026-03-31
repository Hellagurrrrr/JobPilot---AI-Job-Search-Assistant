from typing import TypedDict, Optional, Any
from langchain_core.messages import BaseMessage

class JobPilotState(TypedDict, total=False):
    messages: list[BaseMessage]

    user_input: str
    task_type: str   # parse_cv / parse_jd / match / chat

    cv_path: str
    cv_text: str
    cv_info: dict[str, Any]

    jd_url: str
    jd_text: str
    jd_info: dict[str, Any]

    match_result: dict[str, Any]

    final_response: str
    error: str
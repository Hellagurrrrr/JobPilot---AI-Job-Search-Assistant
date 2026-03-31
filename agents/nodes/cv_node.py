from memory.state_schema import JobPilotState
from services.cv_service import extract_cv_from_pdf, extract_cv_from_text

def cv_node(state: JobPilotState) -> dict:
    try:
        if state.get("cv_path"):
            cv_info = extract_cv_from_pdf(state["cv_path"])
            return {
                "cv_info": cv_info.model_dump(),
                "error": ""
            }

        if state.get("cv_text"):
            cv_info = extract_cv_from_text(state["cv_text"])
            return {
                "cv_info": cv_info.model_dump(),
                "error": ""
            }

        return {"error": "未提供简历路径或简历文本。"}
    except Exception as e:
        return {"error": f"CV 解析失败：{str(e)}"}
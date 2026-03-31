from memory.state_schema import JobPilotState
from models.schemas import CVInfo, JDInfo
from services.match_service import match_cv_to_jd

def match_node(state: JobPilotState) -> dict:
    try:
        if not state.get("cv_info"):
            return {"error": "缺少 CV 信息，无法进行岗位匹配。"}
        if not state.get("jd_info"):
            return {"error": "缺少 JD 信息，无法进行岗位匹配。"}

        cv = CVInfo(**state["cv_info"])
        jd = JDInfo(**state["jd_info"])
        match_result = match_cv_to_jd(cv, jd)

        return {
            "match_result": match_result.model_dump(),
            "error": ""
        }
    except Exception as e:
        return {"error": f"匹配失败：{str(e)}"}
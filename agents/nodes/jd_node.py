from memory.state_schema import JobPilotState
from services.jd_service import extract_jd_from_text, extract_jd_from_url

def jd_node(state: JobPilotState) -> dict:
    try:
        if state.get("jd_url"):
            jd_info = extract_jd_from_url(state["jd_url"])
            return{
                "jd_info": jd_info.model_dump(),
                "error": ""
            }
        
        if state.get("jd_text"):
            jd_info = extract_jd_from_text(state["jd_text"])
            return{
                "jd_info": jd_info.model_dump(),
                "error": ""
            }
        
        return {"error": "未提供岗位描述链接或文本。"}
    except Exception as e:
        return {"error": f"JD 解析失败：{str(e)}"}
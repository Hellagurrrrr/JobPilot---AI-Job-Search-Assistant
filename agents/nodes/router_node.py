from memory.state_schema import JobPilotState

def router_node(state: JobPilotState) -> dict:
    text = state.get("user_input", "").lower()

    if "匹配" in text or "match" in text:
        return {"task_type": "match"}

    if "岗位" in text or "jd" in text or "job description" in text:
        return {"task_type": "parse_jd"}

    if "简历" in text or "cv" in text or "resume" in text:
        return {"task_type": "parse_cv"}

    return {"task_type": "chat"}
from memory.state_schema import JobPilotState

def response_node(state: JobPilotState) -> dict:
    if state.get("error"):
        return {"final_response": state["error"]}

    task_type = state.get("task_type")

    if task_type == "parse_cv":
        cv = state.get("cv_info", {})
        return {
            "final_response": (
                f"候选人：{cv.get('name', 'Unknown')}\n"
                f"技能：{', '.join(cv.get('skills', []))}\n"
                f"亮点：{', '.join(cv.get('highlights', []))}"
            )
        }

    if task_type == "parse_jd":
        jd = state.get("jd_info", {})
        return {
            "final_response": (
                f"岗位：{jd.get('title', 'Unknown')}\n"
                f"必备技能：{', '.join(jd.get('required_skills', []))}\n"
                f"职责：{', '.join(jd.get('responsibilities', []))}"
            )
        }

    if task_type == "match":
        result = state.get("match_result", {})
        return {
            "final_response": (
                f"匹配度：{result.get('match_score', 'Unknown')}\n"
                f"候选人优势：{', '.join(result.get('strengths', []))}\n"
                f"缺失技能：{', '.join(result.get('missing_skills', []))}\n"
                f"建议：{result.get('suggestion', '')}"
            )
        }

    return {"final_response": "暂未识别到明确任务。"}
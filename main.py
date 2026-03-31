from agents.jobpilot_agent import jobpilot_app

result = jobpilot_app.invoke(
    {
        "user_input": "请帮我解析这个简历文件：D:/实习材料/尹禹婷中文简历.pdf，并总结候选人的技能优势",
        "cv_path": "D:/实习材料/尹禹婷中文简历.pdf",
    },
    config={"configurable": {"thread_id": "demo-session-1"}}
)

print(result["final_response"])

result = jobpilot_app.invoke(
    {
        "user_input": "这是目标岗位JD：https://join.qq.com/post_detail.html?postid=1200791473415778304，请帮我分析",
        "jd_url": "https://join.qq.com/post_detail.html?postid=1200791473415778304"
    },
    config={"configurable": {"thread_id": "demo-session-1"}}
)

print(result["final_response"])

result = jobpilot_app.invoke(
    {
        "user_input": "请帮我匹配目标岗位"
    },
    config={"configurable": {"thread_id": "demo-session-1"}}
)

print(result["final_response"])
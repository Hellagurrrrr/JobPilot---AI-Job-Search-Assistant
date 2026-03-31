# main.py
from agents.jobpilot_agent import jobpilot_agent

result = jobpilot_agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "请帮我解析这个简历文件：D:/实习材料/尹禹婷中文简历.pdf，并总结候选人的技能优势"
        }
    ]
})

print(print(result["messages"][-1].content))
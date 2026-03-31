# agents/jobpilot_agent.py
from langchain.agents import create_agent

from llm.client import chat_model
from tools.cv_tools import cv_tools

from llm.prompts import SYSTEM_PROMPT

jobpilot_agent = create_agent(
    model=chat_model,
    tools=cv_tools,
    system_prompt=SYSTEM_PROMPT,
)
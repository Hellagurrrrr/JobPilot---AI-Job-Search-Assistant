from agents.graphs.jobpilot_graph import build_jobpilot_graph
from memory.checkpointer import checkpointer

jobpilot_app = build_jobpilot_graph(checkpointer=checkpointer)
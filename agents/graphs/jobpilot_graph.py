from langgraph.graph import StateGraph, START, END

from memory.state_schema import JobPilotState
from agents.nodes.router_node import router_node
from agents.nodes.cv_node import cv_node
from agents.nodes.jd_node import jd_node
from agents.nodes.match_node import match_node
from agents.nodes.response_node import response_node

def route_by_task(state: JobPilotState) -> str:
    task = state.get("task_type", "chat")
    if task == "parse_cv":
        return "cv_node"
    if task == "parse_jd":
        return "jd_node"
    if task == "match":
        return "match_node"
    return "response_node"

def build_jobpilot_graph(checkpointer=None):
    graph = StateGraph(JobPilotState)

    graph.add_node("router_node", router_node)
    graph.add_node("cv_node", cv_node)
    graph.add_node("jd_node", jd_node)
    graph.add_node("match_node", match_node)
    graph.add_node("response_node", response_node)

    graph.add_edge(START, "router_node")

    graph.add_conditional_edges(
        "router_node",
        route_by_task,
        {
            "cv_node": "cv_node",
            "jd_node": "jd_node",
            "match_node": "match_node",
            "response_node": "response_node",
        }
    )

    graph.add_edge("cv_node", "response_node")
    graph.add_edge("jd_node", "response_node")
    graph.add_edge("match_node", "response_node")
    graph.add_edge("response_node", END)

    return graph.compile(checkpointer=checkpointer)
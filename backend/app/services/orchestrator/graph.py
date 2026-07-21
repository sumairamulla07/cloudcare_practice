"""
LangGraph orchestration — lifted directly from blueprint section 9.1.

PLACEHOLDER STATUS: the graph wiring below is real and will run, but the
node functions (monitor, analyze, decide, supervise, execute, verify) in
./nodes.py are stubs that return mock data. Fill each one in as you connect
real AWS data, a real LLM, and MongoDB. Nothing else in this file needs to
change as you do that — this is the stable "shape" of the pipeline.

To actually run this:
    from app.services.orchestrator.graph import build_graph
    graph = build_graph()
    result = graph.invoke(initial_state)
"""

from langgraph.graph import END, StateGraph

from app.models.schemas import CloudCareState
from app.services.orchestrator.nodes import analyze, decide, execute, monitor, supervise, verify


def route_after_supervisor(state: dict) -> str:
    decision = state.get("supervisor_decision")
    if decision == "execute":
        return "execute"
    if decision == "reanalyze" and state.get("reanalysis_count", 0) < 3:
        return "analyze"
    if decision == "human_review":
        return END
    return END


def build_graph():
    g = StateGraph(dict)
    for name, fn in [
        ("monitor", monitor),
        ("analyze", analyze),
        ("decide", decide),
        ("supervise", supervise),
        ("execute", execute),
        ("verify", verify),
    ]:
        g.add_node(name, fn)
    g.set_entry_point("monitor")
    g.add_edge("monitor", "analyze")
    g.add_edge("analyze", "decide")
    g.add_edge("decide", "supervise")
    g.add_conditional_edges("supervise", route_after_supervisor)
    g.add_edge("execute", "verify")
    g.add_edge("verify", END)
    return g.compile()

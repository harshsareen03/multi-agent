from __future__ import annotations

from typing import Any, Literal, TypedDict

from agents.autogen_agents import AutoGenCoordinator
from agents.coding_agent import CodingAgent
from agents.crew import CrewOrchestrator
from agents.research_agent import ResearchAgent
from database.chroma_db import ChromaDatabase
from rag.retriever import RAGRetriever


class AgentMessage(TypedDict):
    agent: str
    message: str


class WorkflowDashboard(TypedDict):
    active_agents: list[str]
    workflow_steps: list[str]
    agent_messages: list[AgentMessage]


class WorkflowPlan(TypedDict):
    agent: str
    role: str
    goal: str
    tasks: list[str]
    needs_code: bool


class WorkflowResearch(TypedDict):
    agent: str
    role: str
    goal: str
    summary: str
    notes: list[str]
    sources: list[dict[str, Any]]
    context: list[dict[str, Any]]


class WorkflowCode(TypedDict):
    agent: str
    role: str
    goal: str
    code: str
    execution: dict[str, object]


class WorkflowWriter(TypedDict):
    agent: str
    role: str
    goal: str
    final_answer: str
    workflow: list[str]


class WorkflowState(TypedDict, total=False):
    query: str
    plan: WorkflowPlan
    research: WorkflowResearch
    code: WorkflowCode
    writer: WorkflowWriter
    dashboard: WorkflowDashboard


class PlannerAgent:
    role = "Supervisor Agent"
    goal = "Assign tasks to other agents"

    def run(self, query: str) -> WorkflowPlan:
        needs_code = any(token in query.lower() for token in ["code", "python", "build", "implement"])
        return {
            "agent": "Supervisor Agent",
            "role": self.role,
            "goal": self.goal,
            "tasks": [
                "Retrieve relevant context from vector memory",
                "Research the topic with web search",
                "Generate code if needed",
                "Write the final response",
            ],
            "needs_code": needs_code,
        }


class WriterAgent:
    role = "Content writer"
    goal = "Summarize research"

    def run(
        self,
        query: str,
        plan: WorkflowPlan,
        research: WorkflowResearch,
        code: WorkflowCode | None,
        messages: list[dict[str, str]],
    ) -> WorkflowWriter:
        response_lines = [
            f"Answer for: {query}",
            research["summary"],
        ]
        if code:
            response_lines.append("A starter Python implementation was generated.")
            response_lines.append(code["execution"]["stdout"].strip() or "Code executed without stdout.")
        response_lines.append("Agent collaboration summary:")
        response_lines.extend(f"{item['speaker']}: {item['message']}" for item in messages)
        return {
            "agent": "Writer Agent",
            "role": self.role,
            "goal": self.goal,
            "final_answer": "\n".join(response_lines),
            "workflow": plan["tasks"],
        }


class AgentWorkflowService:
    def __init__(self) -> None:
        self.database = ChromaDatabase()
        self.retriever = RAGRetriever(self.database)
        self.planner = PlannerAgent()
        self.research_agent = ResearchAgent()
        self.coding_agent = CodingAgent()
        self.writer_agent = WriterAgent()
        self.crew = CrewOrchestrator()
        self.autogen = AutoGenCoordinator()
        self.graph = self._build_graph()

    def _build_graph(self):
        from langgraph.graph import END, START, StateGraph

        graph = StateGraph(WorkflowState)
        graph.add_node("planner", self._planner_node)
        graph.add_node("research", self._research_node)
        graph.add_node("coding", self._coding_node)
        graph.add_node("writer", self._writer_node)
        graph.add_edge(START, "planner")
        graph.add_edge("planner", "research")
        graph.add_conditional_edges(
            "research",
            self._route_after_research,
            {"coding": "coding", "writer": "writer"},
        )
        graph.add_edge("coding", "writer")
        graph.add_edge("writer", END)
        return graph.compile()

    def _new_dashboard(self, needs_code: bool) -> WorkflowDashboard:
        active_agents = ["Supervisor Agent", "Research Agent", "Writer Agent"]
        if needs_code:
            active_agents.insert(2, "Coding Agent")
        return {
            "active_agents": active_agents,
            "workflow_steps": ["planner"],
            "agent_messages": [{"agent": "Supervisor Agent", "message": "Plan created."}],
        }

    def _append_dashboard(
        self,
        dashboard: WorkflowDashboard,
        step: str,
        messages: list[AgentMessage],
    ) -> WorkflowDashboard:
        return {
            "active_agents": list(dashboard["active_agents"]),
            "workflow_steps": [*dashboard["workflow_steps"], step],
            "agent_messages": [*dashboard["agent_messages"], *messages],
        }

    def _planner_node(self, state: WorkflowState) -> WorkflowState:
        plan = self.planner.run(state["query"])
        return {
            "plan": plan,
            "dashboard": self._new_dashboard(plan["needs_code"]),
        }

    def _research_node(self, state: WorkflowState) -> WorkflowState:
        retrieved = self.retriever.retrieve(state["query"])
        research = self.research_agent.run(state["query"], retrieved)
        self.database.add_documents(
            [
                {
                    "id": f"query-{abs(hash(state['query']))}",
                    "text": research["summary"],
                    "metadata": {"source": "research_agent"},
                }
            ]
        )
        return {
            "research": research,
            "dashboard": self._append_dashboard(
                state["dashboard"],
                "research",
                [{"agent": "Research Agent", "message": research["summary"]}],
            ),
        }

    def _coding_node(self, state: WorkflowState) -> WorkflowState:
        code = self.coding_agent.run(state["query"], state["research"]["summary"])
        return {
            "code": code,
            "dashboard": self._append_dashboard(
                state["dashboard"],
                "coding",
                [
                    {
                        "agent": "Coding Agent",
                        "message": "Starter Python code generated and executed.",
                    }
                ],
            ),
        }

    def _writer_node(self, state: WorkflowState) -> WorkflowState:
        code_output = None
        if "code" in state:
            code_output = state["code"]["execution"].get("stdout")
        messages = self.autogen.run_dialogue(
            state["query"],
            state["research"]["summary"],
            code_output if isinstance(code_output, str) else None,
        )
        writer = self.writer_agent.run(
            query=state["query"],
            plan=state["plan"],
            research=state["research"],
            code=state.get("code"),
            messages=messages,
        )
        return {
            "writer": writer,
            "dashboard": self._append_dashboard(
                state["dashboard"],
                "writer",
                [{"agent": item["speaker"], "message": item["message"]} for item in messages],
            ),
        }

    def _route_after_research(self, state: WorkflowState) -> Literal["coding", "writer"]:
        return "coding" if state["plan"]["needs_code"] else "writer"

    def run(self, query: str) -> dict[str, Any]:
        state = self.graph.invoke({"query": query})
        code_output = None
        if state.get("code"):
            stdout = state["code"]["execution"].get("stdout")
            if isinstance(stdout, str):
                code_output = stdout
        crew_result = self.crew.run(
            query=query,
            research_summary=state["research"]["summary"],
            code_output=code_output,
        )
        final_response = crew_result["final_answer"] or state["writer"]["final_answer"]
        return {
            "query": query,
            "crew": crew_result,
            "plan": state["plan"],
            "research": state["research"],
            "code": state.get("code"),
            "final_response": final_response,
            "dashboard": state["dashboard"],
            "rag_context": state["research"]["context"],
        }

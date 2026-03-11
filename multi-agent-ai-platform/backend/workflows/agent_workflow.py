from __future__ import annotations

from typing import Any, TypedDict

from agents.autogen_agents import AutoGenCoordinator
from agents.coding_agent import CodingAgent
from agents.crew import CrewOrchestrator
from agents.research_agent import ResearchAgent
from database.chroma_db import ChromaDatabase
from rag.retriever import RAGRetriever


class WorkflowState(TypedDict, total=False):
    query: str
    plan: dict[str, Any]
    research: dict[str, Any]
    code: dict[str, Any]
    writer: dict[str, Any]
    dashboard: dict[str, Any]


class PlannerAgent:
    role = "Supervisor Agent"
    goal = "Assign tasks to other agents"

    def run(self, query: str) -> dict[str, Any]:
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
        plan: dict[str, Any],
        research: dict[str, Any],
        code: dict[str, Any] | None,
        messages: list[dict[str, str]],
    ) -> dict[str, Any]:
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

    def _build_graph(self):
        from langgraph.graph import END, START, StateGraph

        graph = StateGraph(WorkflowState)

        def planner_node(state: WorkflowState) -> WorkflowState:
            plan = self.planner.run(state["query"])
            dashboard = {
                "active_agents": ["Supervisor Agent", "Research Agent", "Writer Agent"],
                "workflow_steps": ["planner"],
                "agent_messages": [{"agent": "Supervisor Agent", "message": "Plan created."}],
            }
            if plan["needs_code"]:
                dashboard["active_agents"].insert(2, "Coding Agent")
            return {"plan": plan, "dashboard": dashboard}

        def research_node(state: WorkflowState) -> WorkflowState:
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
            dashboard = state["dashboard"]
            dashboard["workflow_steps"].append("research")
            dashboard["agent_messages"].append(
                {"agent": "Research Agent", "message": research["summary"]}
            )
            return {"research": research, "dashboard": dashboard}

        def coding_node(state: WorkflowState) -> WorkflowState:
            code = self.coding_agent.run(state["query"], state["research"]["summary"])
            dashboard = state["dashboard"]
            dashboard["workflow_steps"].append("coding")
            dashboard["agent_messages"].append(
                {"agent": "Coding Agent", "message": "Starter Python code generated and executed."}
            )
            return {"code": code, "dashboard": dashboard}

        def writer_node(state: WorkflowState) -> WorkflowState:
            messages = self.autogen.run_dialogue(
                state["query"],
                state["research"]["summary"],
                state.get("code", {}).get("execution", {}).get("stdout") if state.get("code") else None,
            )
            writer = self.writer_agent.run(
                query=state["query"],
                plan=state["plan"],
                research=state["research"],
                code=state.get("code"),
                messages=messages,
            )
            dashboard = state["dashboard"]
            dashboard["workflow_steps"].append("writer")
            dashboard["agent_messages"].extend(
                {"agent": item["speaker"], "message": item["message"]} for item in messages
            )
            return {"writer": writer, "dashboard": dashboard}

        def route_from_plan(state: WorkflowState) -> str:
            return "coding" if state["plan"]["needs_code"] else "writer"

        graph.add_node("planner", planner_node)
        graph.add_node("research", research_node)
        graph.add_node("coding", coding_node)
        graph.add_node("writer", writer_node)
        graph.add_edge(START, "planner")
        graph.add_edge("planner", "research")
        graph.add_conditional_edges("research", route_from_plan, {"coding": "coding", "writer": "writer"})
        graph.add_edge("coding", "writer")
        graph.add_edge("writer", END)
        return graph.compile()

    def run(self, query: str) -> dict[str, Any]:
        graph = self._build_graph()
        state = graph.invoke({"query": query})
        return {
            "query": query,
            "crew": self.crew.describe(),
            "plan": state["plan"],
            "research": state["research"],
            "code": state.get("code"),
            "final_response": state["writer"]["final_answer"],
            "dashboard": state["dashboard"],
            "rag_context": state["research"]["context"],
        }


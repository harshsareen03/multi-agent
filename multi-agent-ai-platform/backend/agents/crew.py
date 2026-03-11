from __future__ import annotations

import os
from typing import Any


class CrewOrchestrator:
    def describe(self) -> dict[str, Any]:
        if not os.getenv("OPENAI_API_KEY"):
            return {
                "framework": "CrewAI",
                "enabled": False,
                "error": "OPENAI_API_KEY is not set for the backend process.",
                "agents": [],
                "tasks": [],
            }
        try:
            from crewai import Agent, Crew, Process, Task
            supervisor = Agent(
                role="Supervisor Agent",
                goal="Assign tasks to the research, coding, and writer agents.",
                backstory="Coordinates a multi-agent execution pipeline.",
                verbose=False,
            )
            researcher = Agent(
                role="Research Agent",
                goal="Find information about a topic.",
                backstory="Specializes in search-backed evidence gathering.",
                verbose=False,
            )
            coder = Agent(
                role="Coding Agent",
                goal="Generate code solutions.",
                backstory="Implements Python solutions for research-driven tasks.",
                verbose=False,
            )
            writer = Agent(
                role="Writer Agent",
                goal="Summarize research and execution results.",
                backstory="Produces concise summaries for end users.",
                verbose=False,
            )
            tasks = [
                Task(description="Plan work for the user query.", agent=supervisor),
                Task(description="Research the user query.", agent=researcher),
                Task(description="Generate code if the query needs code.", agent=coder),
                Task(description="Write the final response.", agent=writer),
            ]
            crew = Crew(
                agents=[supervisor, researcher, coder, writer],
                tasks=tasks,
                process=Process.sequential,
            )
            return {
                "framework": "CrewAI",
                "enabled": True,
                "agents": [agent.role for agent in crew.agents],
                "tasks": [task.description for task in crew.tasks],
            }
        except Exception as exc:
            return {
                "framework": "CrewAI",
                "enabled": False,
                "error": str(exc),
                "agents": [],
                "tasks": [],
            }

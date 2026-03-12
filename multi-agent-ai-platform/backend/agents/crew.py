from __future__ import annotations

import os
from typing import Any


class CrewOrchestrator:
    def _preflight(self) -> tuple[bool, str | None]:
        if not os.getenv("OPENAI_API_KEY"):
            return False, "OPENAI_API_KEY is not set for the backend process."
        try:
            import crewai  # noqa: F401
        except Exception as exc:
            return False, f"CrewAI import failed: {exc}"
        return True, None

    def describe(self) -> dict[str, Any]:
        enabled, error = self._preflight()
        if not enabled:
            return {
                "framework": "CrewAI",
                "enabled": False,
                "error": error,
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

    def run(
        self,
        query: str,
        research_summary: str,
        code_output: str | None,
    ) -> dict[str, Any]:
        enabled, error = self._preflight()
        if not enabled:
            return {
                "framework": "CrewAI",
                "enabled": False,
                "error": error,
                "final_answer": None,
            }

        try:
            from crewai import Agent, Crew, Process, Task

            supervisor = Agent(
                role="Supervisor Agent",
                goal="Coordinate a concise and accurate final answer.",
                backstory="Coordinates the research, coding, and writing stages.",
                verbose=False,
            )
            writer = Agent(
                role="Writer Agent",
                goal="Produce the final answer for the user.",
                backstory="Turns workflow outputs into a concise response.",
                verbose=False,
            )

            task_description = (
                f"User query: {query}\n\n"
                f"Research summary:\n{research_summary}\n\n"
                f"Code output:\n{code_output or 'No code output was produced.'}\n\n"
                "Write a short final answer that uses the research summary and code output when relevant."
            )
            tasks = [
                Task(
                    description="Review the workflow context and define the response objective.",
                    expected_output="A short handoff summarizing how the final answer should be written.",
                    agent=supervisor,
                ),
                Task(
                    description=task_description,
                    expected_output="A concise user-facing answer.",
                    agent=writer,
                ),
            ]
            crew = Crew(
                agents=[supervisor, writer],
                tasks=tasks,
                process=Process.sequential,
                verbose=False,
            )
            result = crew.kickoff()
            final_answer = getattr(result, "raw", None) or getattr(result, "output", None) or str(result)
            return {
                "framework": "CrewAI",
                "enabled": True,
                "error": None,
                "final_answer": final_answer,
            }
        except Exception as exc:
            return {
                "framework": "CrewAI",
                "enabled": False,
                "error": str(exc),
                "final_answer": None,
            }

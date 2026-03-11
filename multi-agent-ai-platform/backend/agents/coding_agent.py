from __future__ import annotations

from dataclasses import dataclass

from tools.python_executor import PythonExecutorTool


@dataclass
class CodingAgent:
    role: str = "Software engineer"
    goal: str = "Generate code solutions"

    def __post_init__(self) -> None:
        self.tool = PythonExecutorTool()

    def run(self, query: str, research_summary: str) -> dict[str, object]:
        code = (
            "import json\n\n"
            "response = {\n"
            f"    'query': {query!r},\n"
            f"    'research_summary': {research_summary!r},\n"
            "    'status': 'starter implementation generated'\n"
            "}\n"
            "print(json.dumps(response, indent=2))\n"
        )
        execution = self.tool.run(code=code)
        return {
            "agent": "Coding Agent",
            "role": self.role,
            "goal": self.goal,
            "code": code,
            "execution": execution,
        }


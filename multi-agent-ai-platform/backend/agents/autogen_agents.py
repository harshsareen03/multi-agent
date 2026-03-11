from __future__ import annotations


class AutoGenCoordinator:
    def run_dialogue(self, query: str, research_summary: str, code_output: str | None) -> list[dict[str, str]]:
        try:
            import autogen
        except Exception as exc:
            return [
                {
                    "speaker": "AutoGen",
                    "message": f"AutoGen unavailable, using fallback conversation. Reason: {exc}",
                },
                {
                    "speaker": "Supervisor Agent",
                    "message": f"Research summary reviewed for query: {query}",
                },
            ]

        supervisor = autogen.AssistantAgent(
            name="supervisor_agent",
            llm_config=False,
            system_message="You coordinate agent handoffs and summarize the state.",
        )
        writer = autogen.AssistantAgent(
            name="writer_agent",
            llm_config=False,
            system_message="You summarize research and code output into a concise answer.",
        )
        supervisor_message = (
            f"Query: {query}\n"
            f"Research: {research_summary}\n"
            f"Code output: {code_output or 'No code step executed.'}"
        )
        supervisor_reply = supervisor.generate_reply(messages=[{"role": "user", "content": supervisor_message}])
        writer_reply = writer.generate_reply(messages=[{"role": "user", "content": supervisor_reply}])
        return [
            {"speaker": "Supervisor Agent", "message": supervisor_reply},
            {"speaker": "Writer Agent", "message": writer_reply},
        ]


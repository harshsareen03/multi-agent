import { useState } from "react";
import ChatUI from "./components/ChatUI";
import AgentDashboard from "./components/AgentDashboard";
import { askAgents } from "./api/api";

function buildAssistantMessage(result) {
  return {
    id: crypto.randomUUID(),
    role: "assistant",
    content: result.final_response,
  };
}

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    const nextPrompt = prompt.trim();
    if (!nextPrompt) {
      return;
    }

    const userMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: nextPrompt,
    };

    setMessages((current) => [...current, userMessage]);
    setPrompt("");
    setLoading(true);
    setError("");

    try {
      const response = await askAgents(nextPrompt);
      setResult(response.result);
      setDashboard(response.result.dashboard);
      setMessages((current) => [...current, buildAssistantMessage(response.result)]);
    } catch (requestError) {
      setError(requestError?.response?.data?.detail || "Backend request failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen px-4 py-8 md:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-8">
          <div className="inline-flex rounded-full border border-cyan-400/30 bg-cyan-400/10 px-4 py-2 text-xs uppercase tracking-[0.3em] text-cyan-200">
            Multi-Agent AI Platform
          </div>
          <h1 className="mt-4 max-w-3xl text-4xl font-semibold tracking-tight text-white md:text-6xl">
            Chat with collaborating AI agents for research, coding, and synthesis.
          </h1>
          <p className="mt-4 max-w-2xl text-base text-slate-300 md:text-lg">
            LangGraph coordinates the workflow, CrewAI defines team roles, AutoGen simulates
            inter-agent discussion, and ChromaDB stores retrievable context.
          </p>
        </header>

        {error ? (
          <div className="mb-6 rounded-2xl border border-red-400/20 bg-red-500/10 px-4 py-3 text-sm text-red-100">
            {error}
          </div>
        ) : null}

        <div className="grid gap-6 xl:grid-cols-[1.4fr_0.9fr]">
          <ChatUI
            messages={messages}
            prompt={prompt}
            loading={loading}
            onPromptChange={setPrompt}
            onSubmit={handleSubmit}
          />
          <AgentDashboard dashboard={dashboard} result={result} />
        </div>
      </div>
    </main>
  );
}


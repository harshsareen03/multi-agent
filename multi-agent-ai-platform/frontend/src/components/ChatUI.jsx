export default function ChatUI({
  messages,
  prompt,
  loading,
  onPromptChange,
  onSubmit,
}) {
  return (
    <section className="flex h-[80vh] flex-col rounded-3xl border border-white/10 bg-white/5 shadow-panel backdrop-blur">
      <div className="border-b border-white/10 px-6 py-5">
        <h2 className="text-xl font-semibold text-white">Chat Interface</h2>
        <p className="text-sm text-slate-300">Ask the agent team to research, code, and explain.</p>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto px-6 py-5">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`max-w-3xl rounded-2xl px-4 py-3 text-sm leading-6 ${
              message.role === "user"
                ? "ml-auto bg-signal text-slate-950"
                : "bg-slate-900/80 text-slate-100"
            }`}
          >
            <div className="mb-1 text-xs uppercase tracking-[0.2em] text-slate-300">
              {message.role === "user" ? "You" : "Platform"}
            </div>
            <div className="whitespace-pre-wrap">{message.content}</div>
          </div>
        ))}
        {messages.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-white/10 p-6 text-sm text-slate-300">
            Try: "Research LangGraph vs CrewAI and generate a starter Python example."
          </div>
        ) : null}
      </div>

      <form onSubmit={onSubmit} className="border-t border-white/10 p-4">
        <div className="flex flex-col gap-3 md:flex-row">
          <textarea
            value={prompt}
            onChange={(event) => onPromptChange(event.target.value)}
            placeholder="Describe the task for the multi-agent system..."
            className="min-h-28 flex-1 rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-white outline-none transition focus:border-cyanflare"
          />
          <button
            type="submit"
            disabled={loading || !prompt.trim()}
            className="rounded-2xl bg-cyanflare px-6 py-4 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-300"
          >
            {loading ? "Running..." : "Send"}
          </button>
        </div>
      </form>
    </section>
  );
}


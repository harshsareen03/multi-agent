export default function AgentDashboard({ dashboard, result }) {
  return (
    <section className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-panel backdrop-blur">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-white">Agent Dashboard</h2>
        <p className="text-sm text-slate-300">Active agents, workflow steps, and inter-agent messages.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Active Agents</h3>
          <ul className="space-y-2 text-sm text-slate-200">
            {(dashboard?.active_agents || []).map((agent) => (
              <li key={agent}>{agent}</li>
            ))}
          </ul>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Workflow Steps</h3>
          <ul className="space-y-2 text-sm text-slate-200">
            {(dashboard?.workflow_steps || []).map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ul>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">CrewAI Team</h3>
          <ul className="space-y-2 text-sm text-slate-200">
            {(result?.crew?.agents || []).map((agent) => (
              <li key={agent}>{agent}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-4">
        <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Agent Messages</h3>
        <div className="space-y-3">
          {(dashboard?.agent_messages || []).map((item, index) => (
            <div key={`${item.agent}-${index}`} className="rounded-xl bg-slate-950/70 p-3 text-sm">
              <div className="mb-1 text-xs uppercase tracking-[0.2em] text-cyan-300">{item.agent}</div>
              <div className="whitespace-pre-wrap text-slate-200">{item.message}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}


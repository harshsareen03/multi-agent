# multi-agent-ai-platform

Full-stack multi-agent AI platform with a FastAPI backend and a React frontend. Users submit a prompt in a chat UI and receive a response produced by a coordinated agent workflow for research, code generation, and answer writing.

## Architecture

### Backend

- `FastAPI` exposes `GET /` for health and `POST /ask` for workflow execution.
- `LangGraph` orchestrates the state machine: planner -> research -> coding optional -> writer -> final response.
- `CrewAI` defines the role-based team metadata for Supervisor, Research, Coding, and Writer agents.
- `AutoGen` simulates agent-to-agent conversational review and summary exchange.
- `LangChain` tools wrap `web_search` and `python_executor`.
- `ChromaDB` stores vectorized memory for a lightweight RAG pipeline.

### Frontend

- `React + Vite` provides a chat-style UI.
- `TailwindCSS` styles the chat layout and agent dashboard.
- `Axios` calls the backend `/ask` endpoint.

## Project Structure

```text
multi-agent-ai-platform
├── backend
│   ├── app.py
│   ├── requirements.txt
│   ├── agents
│   │   ├── research_agent.py
│   │   ├── coding_agent.py
│   │   ├── crew.py
│   │   └── autogen_agents.py
│   ├── workflows
│   │   └── agent_workflow.py
│   ├── tools
│   │   ├── web_search.py
│   │   └── python_executor.py
│   ├── rag
│   │   ├── vector_store.py
│   │   └── retriever.py
│   └── database
│       └── chroma_db.py
├── frontend
│   ├── index.html
│   ├── package.json
│   └── src
│       ├── App.jsx
│       ├── components
│       │   ├── ChatUI.jsx
│       │   └── AgentDashboard.jsx
│       └── api
│           └── api.js
└── README.md
```

## Backend Workflow

1. User sends a query to `POST /ask`.
2. `PlannerAgent` decides whether code generation is needed.
3. `RAGRetriever` pulls context from ChromaDB.
4. `ResearchAgent` gathers search results and contextual notes.
5. `CodingAgent` generates and executes Python code if needed.
6. `AutoGenCoordinator` produces inter-agent conversation messages.
7. `WriterAgent` produces the final response and dashboard updates.

## RAG Flow

1. Seed documents are stored in ChromaDB.
2. Text is embedded with a deterministic local embedding function.
3. Similar documents are retrieved for each user query.
4. Retrieved context is passed into research and writing steps.

## Run The Project

### Backend

```bash
cd multi-agent-ai-platform/backend
pip install -r requirements.txt
uvicorn app:app --reload
```

Optional environment variables:

```bash
export OPENAI_API_KEY=your_key
export TAVILY_API_KEY=your_search_key
```

### Frontend

```bash
cd multi-agent-ai-platform/frontend
npm install
npm run dev
```

The frontend expects the backend at `http://127.0.0.1:8000`.

## Example Request

```json
{
  "query": "Research LangGraph and CrewAI, then generate a Python starter example for a multi-agent workflow."
}
```

## Example Response Shape

```json
{
  "status": "success",
  "result": {
    "query": "Research LangGraph and CrewAI, then generate a Python starter example for a multi-agent workflow.",
    "crew": {
      "framework": "CrewAI",
      "enabled": true,
      "agents": ["Supervisor Agent", "Research Agent", "Coding Agent", "Writer Agent"],
      "tasks": ["Plan work for the user query.", "Research the user query.", "Generate code if the query needs code.", "Write the final response."]
    },
    "plan": {
      "needs_code": true
    },
    "research": {
      "summary": "Research findings for the query."
    },
    "code": {
      "execution": {
        "returncode": 0
      }
    },
    "final_response": "Answer for: ...",
    "dashboard": {
      "active_agents": ["Supervisor Agent", "Research Agent", "Coding Agent", "Writer Agent"],
      "workflow_steps": ["planner", "research", "coding", "writer"],
      "agent_messages": []
    }
  }
}
```

## Production Notes

- Replace the deterministic local embedding function with OpenAI embeddings or another managed embedding service if you need higher-quality retrieval.
- Replace the placeholder search fallback with a real web search provider.
- Add authentication, persistence, and monitoring before deploying publicly.

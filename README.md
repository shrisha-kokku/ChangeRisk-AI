# ChangeRisk AI

Multi-agent LangGraph system that analyzes proposed code changes against a codebase, its tests, and security policies, then lets a tool-calling agent act on the result in GitHub. Every write action pauses for human approval, and the reviewer can edit it first.

## Overview

A developer describes a change, for example: *"I want to add UPI refund functionality to my payment system."*

ChangeRisk AI works in two phases:

1. **Analysis.** Relevant context is retrieved from the indexed codebase, tests, and security policies. An LLM judge-supervisor routes the request to specialist agents, and the findings are combined into a risk report covering security concerns, required tests, and the files and APIs likely to change.
2. **Action.** The developer chats with an action agent, for example *"File this as an issue."* The agent decides which GitHub tools to call. It searches for existing issues first, then creates a new issue or comments on an existing one. Any write action pauses for approval, with editable content, before it runs.

## Features

- **Judge-supervisor routing.** An LLM decides which specialist agent runs next, based on what is already known about the change. A loop guard forces the final report once all specialists have run.
- **Specialist agents.** Security review, test impact analysis, and affected files/APIs.
- **Retrieval-augmented analysis.** Codebase, tests, and policies are indexed in ChromaDB using local embeddings.
- **Guardrail.** The final report is checked against the retrieved evidence before it is shown.
- **Tool-calling action agent.** The LLM chooses between `search_issues`, `create_issue`, and `add_comment`, and checks for duplicates before creating an issue.
- **Human-in-the-loop.** Write tools pause with LangGraph `interrupt()`. The reviewer can edit the arguments (title, body, labels, comment text) before approving, and only the approved version runs.
- **MCP integration.** The backend is an MCP client for GitHub's official hosted MCP server.
- **Live execution trace.** Every agent step, tool call, and tool result is streamed to the UI as it happens.
- **Observability.** Every run is traced in LangSmith.

## Architecture

### Analysis phase

```mermaid
flowchart TD
    A[Developer request] --> B[Extractor]
    B --> C[RAG Retriever]
    C --> D{Supervisor - Judge}
    D -->|security| E[Security Agent]
    D -->|test_impact| F[Test Impact Agent]
    D -->|code_search| G[Code Search Agent]
    E --> D
    F --> D
    G --> D
    D -->|report| H[Guardrail + Report Builder]
    H --> I[Risk report]
```

The supervisor runs after every specialist and decides the next step. A safety check forces the report once all three specialists have run, so a bad LLM decision can never cause an endless loop.

### Action phase

```mermaid
flowchart TD
    A[User instruction] --> B[Action Agent - LLM]
    B -->|read tool| C[search_issues]
    B -->|write tool| D[Human approval - editable]
    D -->|approved| E[create_issue / add_comment]
    D -->|rejected| B
    C --> B
    E --> B
    B -->|no more tools| F[Final response]
```

Read tools run automatically. Write tools call GitHub's MCP server only after approval. The agent runs one tool per turn, so a resumed approval can never repeat an earlier action.

## Tech stack

| Area              | Tool                                                                  |
| ----------------- | --------------------------------------------------------------------- |
| Orchestration     | LangGraph, LangChain                                                  |
| LLM               | Groq via`langchain-groq` (`openai/gpt-oss-120b`)                  |
| Retrieval         | ChromaDB,`sentence-transformers` (local embeddings)                 |
| Human-in-the-loop | LangGraph`interrupt()` with a checkpointer                          |
| Guardrail         | Grounding check on the final report                                   |
| Tool integration  | MCP client (`langchain-mcp-adapters`) to GitHub's remote MCP server |
| Observability     | LangSmith                                                             |
| Backend           | FastAPI                                                               |
| UI                | Streamlit                                                             |
| Packaging         | Docker                                                                |

## Project structure

```
ChangeRisk AI/
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── api/
│   │   ├── routes_analysis.py   # /analyze-change/stream
│   │   └── routes_action.py     # /chat and /decision
│   ├── core/config.py           # environment configuration
│   ├── graph/
│   │   ├── state.py             # shared state passed between nodes
│   │   ├── nodes.py             # extractor, retrieval, and report nodes
│   │   └── build_graph.py       # analysis graph wiring and routing
│   ├── agents/
│   │   ├── supervisor.py        # judge that selects the next specialist
│   │   ├── security_agent.py
│   │   ├── test_impact_agent.py
│   │   ├── code_search_agent.py
│   │   ├── action_agent.py      # tool-calling agent with the approval gate
│   │   └── tools.py             # search_issues, create_issue, add_comment
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── vectorstore.py
│   │   ├── ingest.py            # builds the vector index
│   │   └── retriever.py
│   ├── mcp/
│   │   └── github_client.py     # MCP client for GitHub's MCP server
│   ├── guardrails/validators.py
│   ├── llm/groq_client.py
│   ├── models/schemas.py        # request models
│   └── services/
│       ├── change_service.py    # streams the analysis
│       └── action_service.py    # runs the action agent
├── data/                        # source documents to index (sample payment system)
├── chroma_db/                   # persisted vector index (generated)
├── scripts/run_ingest.py        # index builder
├── ui/
│   ├── streamlit_app.py
│   └── static/robot.svg
├── .streamlit/config.toml       # UI theme
├── Dockerfile
├── .dockerignore
└── requirements.txt
```

## Getting started

### Prerequisites

- Python 3.11 or later
- A Groq API key (console.groq.com)
- A LangSmith API key (smith.langchain.com)
- A GitHub personal access token with the `repo` scope
- A GitHub repository to receive the issues

All services above offer a free tier.

### Installation

```bash
git clone <repository-url>
cd "ChangeRisk AI"
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
python -m pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_key
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=changerisk-ai
GITHUB_TOKEN=your_github_token
GITHUB_REPO=your-username/your-issues-repo
```

| Variable                 | Description                                                  |
| ------------------------ | ------------------------------------------------------------ |
| `GROQ_API_KEY`         | Groq API key used for all LLM calls                          |
| `LANGCHAIN_API_KEY`    | LangSmith API key                                            |
| `LANGCHAIN_TRACING_V2` | Set to`true` to enable LangSmith tracing                   |
| `LANGCHAIN_PROJECT`    | LangSmith project name                                       |
| `GITHUB_TOKEN`         | GitHub token used to authenticate with the GitHub MCP server |
| `GITHUB_REPO`          | Repository that receives issues, in`owner/repo` format     |
| `API_URL`              | UI only. Backend URL, defaults to`http://localhost:8000`   |

### Build the index

Place the codebase files, tests, and security policies to analyze in `data/`, then run:

```bash
python scripts/run_ingest.py
```

The index is written to `chroma_db/`. To re-index after changing `data/`, delete `chroma_db/` first to avoid duplicate entries.

### Run

Start the backend:

```bash
uvicorn app.main:app --reload
```

In a second terminal, start the UI:

```bash
streamlit run ui/streamlit_app.py
```

| Service           | URL                        |
| ----------------- | -------------------------- |
| API documentation | http://localhost:8000/docs |
| UI                | http://localhost:8501      |

## API reference

All streaming endpoints return newline-delimited JSON events.

| Method | Endpoint                   | Description                                                                                                                                                                                                                 |
| ------ | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GET    | `/health`                | Health check                                                                                                                                                                                                                |
| POST   | `/analyze-change/stream` | Runs the analysis. Events:`step` (finished steps and the next agent) and `done` (risk report and full execution log).                                                                                                   |
| POST   | `/chat`                  | Sends a message to the action agent. Body:`message`, `report`, and optional `thread_id`. Events: `start`, `message`, `tool_call`, `tool_result`, and `approval` (a write action is waiting for a decision). |
| POST   | `/decision`              | Resumes a paused action with the reviewer's decision. Body:`thread_id`, `approved`, and `args` (the possibly edited arguments). Same events as `/chat`.                                                             |

Example analysis request:

```json
{"change_request": "I want to add UPI refund functionality to my payment system"}
```

Example decision request:

```json
{"thread_id": "<thread_id from the start event>", "approved": true, "args": {"title": "...", "body": "...", "labels": ["security"]}}
```

## Deployment

### Backend (Docker)

```bash
docker build -t changerisk-ai .
docker run -p 8000:8000 --env-file .env changerisk-ai
```

The image contains the backend only. Provide the environment variables through the hosting platform rather than baking them into the image.

### UI

The Streamlit UI can be hosted separately. Set the `API_URL` environment variable (or Streamlit secret) to the deployed backend URL.

## Limitations

- Both graphs use an in-memory checkpointer, so a paused approval or an ongoing chat is lost if the backend restarts. For production, use a persistent checkpointer such as Postgres.
- The sample data in `data/` is a small mock payment system that demonstrates retrieval.
- The grounding check is a lightweight heuristic and does not replace human review.
- GitHub's search index can lag briefly, so an issue created moments ago may not appear in the duplicate check.

# ChangeRisk AI

Multi-agent LangGraph system that analyzes proposed code changes against a codebase, its tests, and security policies. An LLM judge-supervisor routes each request to specialist agents, and a GitHub issue is filed only after human approval.

## Overview

A developer describes a change, for example: *"I want to add UPI refund functionality to my payment system."*

ChangeRisk AI retrieves the relevant context from the indexed codebase, tests, and security policies, runs the specialist agents the request needs, and produces a risk report covering security concerns, required tests, and the files and APIs likely to change. The graph then pauses for human approval. On approval, the issue is filed through GitHub's official MCP server.

## Features

- **Judge-supervisor routing.** An LLM decides which specialist agent runs next, based on what is already known about the change. A loop guard forces the final report once all specialists have run.
- **Specialist agents.** Security review, test impact analysis, and affected files/APIs.
- **Retrieval-augmented analysis.** Codebase, tests, and policies are indexed in ChromaDB using local embeddings.
- **Guardrail.** The final report is checked against the retrieved evidence before a human sees it.
- **Human-in-the-loop.** The graph pauses with LangGraph `interrupt()` and resumes with the reviewer's decision.
- **MCP integration.** The backend acts as an MCP client and calls the `issue_write` tool on GitHub's hosted MCP server.
- **Live execution trace.** Each agent step is streamed to the UI as it happens.
- **Observability.** Every run is traced in LangSmith.

## Architecture

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
    H --> I[Human Approval]
    I -->|approved| J[GitHub issue via MCP]
    I -->|rejected| K[No action taken]
```

The request runs in two phases:

1. **Analysis.** `POST /analyze-change/stream` runs the graph and streams each finished step until the graph pauses at the approval node.
2. **Decision.** `POST /approve` resumes the paused graph, identified by `thread_id`, with the reviewer's decision.

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
│   │   ├── routes_analysis.py   # /analyze-change and /analyze-change/stream
│   │   └── routes_approval.py   # /approve
│   ├── core/config.py           # environment configuration
│   ├── graph/
│   │   ├── state.py             # shared state passed between nodes
│   │   ├── nodes.py             # extractor, retrieval, report, and approval nodes
│   │   └── build_graph.py       # graph wiring and routing
│   ├── agents/
│   │   ├── supervisor.py        # judge that selects the next specialist
│   │   ├── security_agent.py
│   │   ├── test_impact_agent.py
│   │   └── code_search_agent.py
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── vectorstore.py
│   │   ├── ingest.py            # builds the vector index
│   │   └── retriever.py
│   ├── mcp/
│   │   └── github_client.py     # MCP client for GitHub's MCP server
│   ├── guardrails/validators.py
│   ├── llm/groq_client.py
│   ├── models/schemas.py        # request and response models
│   └── services/change_service.py
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

| Method | Endpoint                   | Description                                                                                                                                                                      |
| ------ | -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GET    | `/health`                | Health check                                                                                                                                                                     |
| POST   | `/analyze-change`        | Runs the graph until it pauses for approval. Returns`thread_id`, `risk_report`, `question`, and `execution_log`.                                                         |
| POST   | `/analyze-change/stream` | Same analysis, streamed as newline-delimited JSON events:`start` (thread ID), `step` (finished steps and the next agent), and `done` (risk report and full execution log). |
| POST   | `/approve`               | Resumes the paused graph with the reviewer's decision. Returns`status` and `execution_log`.                                                                                  |

Example analysis request:

```json
{"change_request": "I want to add UPI refund functionality to my payment system"}
```

Example approval request:

```json
{"thread_id": "<thread_id from the analysis response>", "approved": true}
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

- The graph checkpointer is in-memory, so a paused analysis is lost if the backend restarts. For production, use a persistent checkpointer such as Postgres.
- The sample data in `data/` is a small mock payment system that demonstrates retrieval.
- The grounding check is a lightweight heuristic and does not replace human review.

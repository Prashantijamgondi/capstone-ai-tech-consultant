# AI Tech Consultant — Monorepo

Autonomous multi-service AI consulting platform built for software & SaaS businesses to handle product inquiries, customer support inboxes, and discovery meeting scopes of work.

## Architecture
- **Task 1: The Knowledge Brain (	ask1-knowledge-brain/)**: Python (FastAPI, SQLite FTS5, Multimodal Vision, polite sitemap crawler, daily delta sync, and human escalation loop).
- **Task 2: The Inbox Agent (	ask2-inbox-agent/)**: TypeScript strict mode (Express, 50-email test bank, Task 1 API client, human review workflow, 20-consecutive-approval autonomy rule).
- **Task 3: Meeting to Scope of Work (	ask3-meeting-to-scope/)**: Python (Multi-agent team: Analyst, Product Feasibility, Estimator, and Scope Differ with 3 roleplay transcripts).
- **Unified Control Dashboard (ui/)**: Clean web portal testing all 3 tasks live.

## Quickstart (Single-Command Run)

### 1. Prerequisites
- Python 3.10+
- Node.js v18+
- (Optional) ANTHROPIC_API_KEY for live Claude 3.5 Sonnet / Haiku inference. Fallbacks to deterministic grounded heuristics if omitted.

### 2. Launch All Services
`cmd
run_all.bat
`
This starts:
- Task 1 Knowledge Brain on http://127.0.0.1:8001 (Docs at /docs)
- Task 2 Inbox Agent on http://127.0.0.1:8002
- Task 3 Meeting to Scope on http://127.0.0.1:8003
- Unified Web UI on http://127.0.0.1:3000

### 3. Run Evaluation Suites (20+ Tests Per Task)
`cmd
python task1-knowledge-brain/evaluation/eval_suite.py
cd task2-inbox-agent && npm run eval
python task3-meeting-to-scope/evaluation/run_evals.py
`

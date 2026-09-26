# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Overview
**RepoDoc** — GitHub repo auditing tool. FastAPI backend + React/Vite frontend with Clean Architecture (Domain / Use Cases / Infrastructure / UI).

## Commands

### Backend (run from `backend/`)
```bash
# Activate venv first
.\.venv\Scripts\activate          # Windows
source .venv/bin/activate         # Mac/Linux

uvicorn app.main:app --reload --port 8000   # Dev server
```
> **No test suite exists yet.** `backend/tests/` is an empty directory.

### Frontend (run from `frontend/`)
```bash
npm run dev      # Dev server on http://localhost:5173
npm run lint     # ESLint
npm run build    # Production build
```

## Critical Architecture Notes

- **WatsonX LLM is mocked** — `WatsonXClient._generate()` in [`backend/app/infrastructure/llm/watsonx_client.py`](backend/app/infrastructure/llm/watsonx_client.py) always returns hardcoded JSON instead of calling the real API. Replace the `# --- MOCK START ---` block with the real `httpx` POST when credentials are available.
- **`analyze_repo.py` passes `"mock_key"/"mock_id"`** to `WatsonXClient` — these are intentional placeholders; the mock never hits the network.
- **`GithubClient.fetch_repo_summary()`** returns a `tree` key at the top level but the use-case reads `repo_data.get('tree', [])` — this works because the actual key returned by `_fetch_file_tree` is stored under `file_tree`, **not** `tree`. The use-case currently reads `file_tree` items by filtering from the top-level `tree` key only if `type == 'blob'`, so only file blobs are sent to LLM (directories are excluded).
- **CORS** is hardcoded to `http://localhost:5173` only — update `main.py` for any other origin.
- **Backend API base URL** is hardcoded in [`frontend/src/infrastructure/api/auditApi.js`](frontend/src/infrastructure/api/auditApi.js) as `http://localhost:8000`. No env var support.

## Backend Code Style (Python)

- Python 3.12, Pydantic v2, FastAPI, `httpx` for async HTTP.
- All infrastructure clients are **async context managers** (`async with Client() as c`); always use `async with`, never instantiate and call directly.
- Custom exceptions per client: `GithubClientError`, `WatsonXClientError`, `WatsonXTimeoutError` — catch these specifically, not bare `Exception`.
- Module-level constants use `_SCREAMING_SNAKE` with a leading underscore (private).
- Pydantic request models live in `main.py` (no separate `schemas/` files used yet despite the directory existing).
- `app/core/domain/` and `app/schemas/` directories exist but are empty — scaffold models there when expanding.
- Imports: stdlib → third-party → internal (`app.*`), separated by blank lines.

## Frontend Code Style (JavaScript/React)

- React 19, Vite 8, `.jsx` extensions (no TypeScript).
- **Zero external UI library** — all styling is inline `style={{}}` objects. Do not add CSS-in-JS or component libraries.
- Severity color constants are centralised in `SEVERITY_STYLES` map in `AuditPage.jsx` — reference that map for any new severity-aware UI.
- API layer lives exclusively in `frontend/src/infrastructure/api/` — keep fetch calls out of components.
- Clean Architecture mirrored in frontend: `core/domain/`, `core/useCases/`, `infrastructure/api/`, `ui/features/`, `ui/components/`, `ui/layouts/`.
